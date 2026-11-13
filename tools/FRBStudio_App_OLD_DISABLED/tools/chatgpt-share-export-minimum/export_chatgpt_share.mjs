#!/usr/bin/env node

import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { chromium } from 'playwright';

const EXIT_FAILURE = 1;
const EXIT_USAGE = 2;

function printUsage() {
  console.error(`Usage:
  node export_chatgpt_share.mjs <shared-url> [output-dir] [--headed]

Example:
  node export_chatgpt_share.mjs "https://chatgpt.com/share/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  node export_chatgpt_share.mjs "https://chatgpt.com/share/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" output --headed
`);
}

function parseArgs(argv) {
  const args = argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) {
    return { help: true };
  }

  const positional = args.filter((arg) => !arg.startsWith('--'));
  return {
    help: false,
    url: positional[0],
    outputDir: positional[1] ?? 'output',
    headed: args.includes('--headed'),
  };
}

function validateSharedUrl(rawUrl) {
  let url;
  try {
    url = new URL(rawUrl);
  } catch {
    throw new Error('共有URLの形式が正しくありません。');
  }

  const allowedHosts = new Set(['chatgpt.com', 'www.chatgpt.com', 'chat.openai.com']);
  if (url.protocol !== 'https:' || !allowedHosts.has(url.hostname)) {
    throw new Error('https://chatgpt.com/share/... 形式のURLを指定してください。');
  }

  if (!url.pathname.startsWith('/share/')) {
    throw new Error('ChatGPTの共有URLではありません。/share/ を含むURLを指定してください。');
  }

  return url;
}

function sanitizeFileName(value) {
  const sanitized = value
    .normalize('NFKC')
    .replace(/[<>:"/\\|?*\u0000-\u001F]/g, '_')
    .replace(/\s+/g, ' ')
    .replace(/[. ]+$/g, '')
    .trim()
    .slice(0, 80);

  return sanitized || 'chatgpt_shared_chat';
}

function formatLocalTimestamp(date = new Date()) {
  const pad = (value) => String(value).padStart(2, '0');
  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
    '_',
    pad(date.getHours()),
    pad(date.getMinutes()),
    pad(date.getSeconds()),
  ].join('');
}

function yamlString(value) {
  return JSON.stringify(String(value));
}

function normalizeText(value) {
  return String(value ?? '')
    .replace(/\r\n/g, '\n')
    .replace(/\u00a0/g, ' ')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function buildMarkdown({ title, titleSource, sourceUrl, exportedAt, messages }) {
  const lines = [
    '---',
    `title: ${yamlString(title)}`,
    `title_source: ${yamlString(titleSource)}`,
    `source_url: ${yamlString(sourceUrl)}`,
    `exported_at: ${yamlString(exportedAt)}`,
    `message_count: ${messages.length}`,
    '---',
    '',
    `# ${title}`,
    '',
  ];

  messages.forEach((message, index) => {
    const roleLabel = message.role === 'user'
      ? 'User'
      : message.role === 'assistant'
        ? 'Assistant'
        : message.role;

    lines.push(`## ${String(index + 1).padStart(3, '0')} ${roleLabel}`);
    lines.push('');
    lines.push(message.text || '(空のメッセージ)');
    lines.push('');
  });

  return `${lines.join('\n').trimEnd()}\n`;
}

async function launchBrowser(headed) {
  const launchOptions = { headless: !headed };

  try {
    return await chromium.launch(launchOptions);
  } catch (firstError) {
    for (const channel of ['chrome', 'msedge']) {
      try {
        console.error(`[INFO] Playwright Chromiumが見つからないため、${channel} を試します。`);
        return await chromium.launch({ ...launchOptions, channel });
      } catch {
        // 次の候補へ進む。
      }
    }

    throw new Error(
      `ブラウザを起動できません。setup.cmd を実行してください。\n${firstError.message}`,
    );
  }
}

async function scrollEntirePage(page) {
  await page.evaluate(async () => {
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    let previousHeight = 0;
    let stableCount = 0;

    for (let i = 0; i < 120; i += 1) {
      window.scrollTo(0, document.body.scrollHeight);
      await sleep(150);

      const currentHeight = document.body.scrollHeight;
      if (currentHeight === previousHeight) {
        stableCount += 1;
        if (stableCount >= 4) break;
      } else {
        stableCount = 0;
        previousHeight = currentHeight;
      }
    }

    window.scrollTo(0, 0);
  });
}

async function extractConversation(page) {
  return page.evaluate(() => {
    const cleanText = (value) => String(value ?? '')
      .replace(/\r\n/g, '\n')
      .replace(/\u00a0/g, ' ')
      .replace(/[ \t]+\n/g, '\n')
      .replace(/\n{3,}/g, '\n\n')
      .trim();

    const findContentElement = (root, role) => {
      const selectors = role === 'assistant'
        ? [
            '[data-message-content]',
            '.markdown.prose',
            '.markdown',
          ]
        : [
            '[data-message-content]',
            '[class*="whitespace-pre-wrap"]',
          ];

      for (const selector of selectors) {
        const found = root.matches?.(selector) ? root : root.querySelector(selector);
        if (found) return found;
      }
      return root;
    };

    let nodes = Array.from(document.querySelectorAll('[data-message-author-role]'));

    if (nodes.length === 0) {
      nodes = Array.from(document.querySelectorAll('article[data-testid^="conversation-turn-"]'));
    }

    const messages = [];
    for (const node of nodes) {
      const roleNode = node.hasAttribute?.('data-message-author-role')
        ? node
        : node.querySelector('[data-message-author-role]');

      let role = roleNode?.getAttribute('data-message-author-role') ?? '';
      if (!role) {
        const label = cleanText(node.querySelector('h5, [aria-label]')?.textContent).toLowerCase();
        role = label.includes('user') || label.includes('you') ? 'user' : 'assistant';
      }

      if (!['user', 'assistant', 'system', 'tool'].includes(role)) continue;

      const contentRoot = findContentElement(roleNode ?? node, role);
      const text = cleanText(contentRoot?.innerText ?? contentRoot?.textContent);
      if (!text) continue;

      const previous = messages.at(-1);
      if (previous && previous.role === role && previous.text === text) continue;

      messages.push({ role, text });
    }

    const genericTitles = new Set([
      '',
      'ChatGPT',
      'ChatGPT Shared Chat',
      'Shared conversation',
      'View this chat',
      'このチャットを見てみる',
    ]);

    const normalizeTitle = (value) => cleanText(value)
      .replace(/^ChatGPT\s*[-–—:]\s*/i, '')
      .replace(/\s*[-–—:]\s*ChatGPT$/i, '')
      .trim();

    // 共有ページでは og:title が「このチャットを見てみる」のような
    // 汎用文言になることがある。一方、document.title には実タイトルが入るため、
    // document.title を最優先にして汎用タイトルを除外する。
    const titleCandidates = [
      {
        source: 'document.title',
        value: normalizeTitle(document.title),
      },
      {
        source: 'meta[property="og:title"]',
        value: normalizeTitle(
          document.querySelector('meta[property="og:title"]')?.getAttribute('content'),
        ),
      },
      {
        source: 'meta[name="twitter:title"]',
        value: normalizeTitle(
          document.querySelector('meta[name="twitter:title"]')?.getAttribute('content'),
        ),
      },
      {
        source: 'h1',
        value: normalizeTitle(document.querySelector('main h1, article h1, h1')?.textContent),
      },
    ];

    let selectedTitle = titleCandidates.find(
      (candidate) => candidate.value && !genericTitles.has(candidate.value),
    );

    if (!selectedTitle) {
      const firstUserMessage = messages.find((message) => message.role === 'user')?.text ?? '';
      const firstLine = cleanText(firstUserMessage).split('\n')[0].slice(0, 80);
      if (firstLine) {
        selectedTitle = {
          source: 'first_user_message',
          value: firstLine,
        };
      }
    }

    const title = selectedTitle?.value || 'ChatGPT Shared Chat';
    const titleSource = selectedTitle?.source || 'fallback';
    const pageText = cleanText(document.body?.innerText).slice(0, 1500);

    return { title, titleSource, messages, pageText };
  });
}

async function main() {
  const options = parseArgs(process.argv);
  if (options.help) {
    printUsage();
    return;
  }

  if (!options.url) {
    printUsage();
    process.exitCode = EXIT_USAGE;
    return;
  }

  let sharedUrl;
  try {
    sharedUrl = validateSharedUrl(options.url);
  } catch (error) {
    console.error(`[ERROR] ${error.message}`);
    process.exitCode = EXIT_USAGE;
    return;
  }

  let browser;
  try {
    console.error(`[INFO] 共有チャットを開きます: ${sharedUrl.href}`);
    browser = await launchBrowser(options.headed);

    const context = await browser.newContext({
      locale: 'ja-JP',
      viewport: { width: 1440, height: 1000 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36',
    });
    const page = await context.newPage();

    const response = await page.goto(sharedUrl.href, {
      waitUntil: 'domcontentloaded',
      timeout: 60_000,
    });

    if (response && response.status() >= 400) {
      throw new Error(`共有URLの取得に失敗しました。HTTP ${response.status()}`);
    }

    await page.waitForLoadState('networkidle', { timeout: 15_000 }).catch(() => {});
    await page.waitForFunction(
      () => document.querySelectorAll('[data-message-author-role], article[data-testid^="conversation-turn-"]').length > 0,
      { timeout: 30_000 },
    ).catch(() => {});

    await scrollEntirePage(page);
    const extracted = await extractConversation(page);

    if (extracted.messages.length === 0) {
      throw new Error(
        `会話本文を検出できませんでした。共有リンクが無効・権限制限付き・未公開、またはChatGPTの画面構造が変更された可能性があります。\n` +
        `画面先頭: ${extracted.pageText || '(本文なし)'}`,
      );
    }

    const exportedAt = new Date().toISOString();
    const shareId = sharedUrl.pathname.split('/').filter(Boolean).at(-1) ?? 'shared_chat';
    const effectiveTitle = extracted.title || shareId;
    const effectiveTitleSource = extracted.title ? extracted.titleSource : 'share_id';
    const fileName = `${formatLocalTimestamp()}_${sanitizeFileName(effectiveTitle)}.md`;
    const outputDir = path.resolve(options.outputDir);
    const outputFile = path.join(outputDir, fileName);

    await fs.mkdir(outputDir, { recursive: true });
    await fs.writeFile(
      outputFile,
      buildMarkdown({
        title: effectiveTitle,
        titleSource: effectiveTitleSource,
        sourceUrl: sharedUrl.href,
        exportedAt,
        messages: extracted.messages.map((message) => ({
          ...message,
          text: normalizeText(message.text),
        })),
      }),
      'utf8',
    );

    const result = {
      status: 'SUCCESS',
      source_url: sharedUrl.href,
      title: effectiveTitle,
      title_source: effectiveTitleSource,
      message_count: extracted.messages.length,
      output_file: outputFile,
      exported_at: exportedAt,
    };

    // Studio連携時に機械処理しやすいよう、標準出力はJSON 1行だけにする。
    process.stdout.write(`${JSON.stringify(result)}\n`);
  } catch (error) {
    const result = {
      status: 'FAILED',
      source_url: options.url,
      error: error instanceof Error ? error.message : String(error),
    };
    process.stdout.write(`${JSON.stringify(result)}\n`);
    process.exitCode = EXIT_FAILURE;
  } finally {
    await browser?.close().catch(() => {});
  }
}

await main();
