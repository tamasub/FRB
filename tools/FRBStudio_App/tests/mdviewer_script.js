
const mdUrlEl=document.getElementById("mdUrl"),previewEl=document.getElementById("preview"),tocEl=document.getElementById("toc"),charCountEl=document.getElementById("charCount"),readTimeEl=document.getElementById("readTime"),localFileBtn=document.getElementById("localFileBtn"),localFileInput=document.getElementById("localFileInput"),tocDepthBtns=[...document.querySelectorAll(".toc-depth-btn")],themeSelect=document.getElementById("themeSelect"),editorEl=document.getElementById("editor"),btnViewerMode=document.getElementById("btnViewerMode"),btnEditorMode=document.getElementById("btnEditorMode"),articleCard=document.getElementById("articleCard"),metaFileName=document.getElementById("metaFileName"),editorFileName=document.getElementById("editorFileName"),slashMenu=document.getElementById("slashMenu"),managedMdSelect=document.getElementById("managedMdSelect"),btnRefreshManagedMd=document.getElementById("btnRefreshManagedMd"),btnOverwriteManagedMd=document.getElementById("btnOverwriteManagedMd");

const fmPanel=document.getElementById("fmPanel"),fmHeader=document.getElementById("fmHeader"),fmBody=document.getElementById("fmBody"),fmToggleIcon=document.getElementById("fmToggleIcon"),fmSuggestArea=document.getElementById("fmSuggestArea");
const fmTitle=document.getElementById("fmTitle"),fmSlug=document.getElementById("fmSlug"),fmEmoji=document.getElementById("fmEmoji"),fmType=document.getElementById("fmType"),fmTopics=document.getElementById("fmTopics"),fmPublished=document.getElementById("fmPublished");

let tocDepth="all";
let currentManagedMarkdownName = "";
let isManagedMarkdownDirty = false;
let launchMarkdownRuntime = { fromUrl: false, readonly: false, fileParam: "" };

// 最新のmarked.js仕様に合わせてグローバル設定を適用
marked.use({ gfm: true, breaks: true });

function preprocessQiita(md){return md.replace(/:::note\s*(info|warn)?\s*\n([\s\S]*?)\n:::/g,(_,type,body)=>`<div class="qiita-note ${type||"info"}">\n\n${body.trim()}\n\n</div>`)}
function slugify(text,index){return"sec-"+index+"-"+encodeURIComponent(text.trim().toLowerCase()).replace(/%/g,"")}

// YAMLフロントマターの高度パース
function parseFrontMatter(md) {
  const match = md.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  if (!match) return { data: null, content: md };
  
  const yamlText = match[1];
  const content = md.substring(match[0].length);
  const data = {};
  
  yamlText.split('\n').forEach(line => {
    const idx = line.indexOf(':');
    if (idx !== -1) {
      const key = line.substring(0, idx).trim();
      let val = line.substring(idx + 1).trim();
      if (val.startsWith('"') && val.endsWith('"')) val = val.slice(1, -1);
      if (val.startsWith("'") && val.endsWith("'")) val = val.slice(1, -1);
      if (val.startsWith('[') && val.endsWith(']')) {
        try { val = JSON.parse(val.replace(/'/g, '"')); } catch(e) { val = val.slice(1, -1).split(',').map(s=>s.trim().replace(/['"]/g,'')); }
      }
      data[key] = val;
    }
  });
  return { data, content };
}

// 保存ファイル名の入力欄同期
function syncFileNameUI(name) {
  metaFileName.value = name;
  editorFileName.value = name;
}
[metaFileName, editorFileName].forEach(input => {
  input.addEventListener("input", (e) => syncFileNameUI(e.target.value));
});

// モード切り替え
btnViewerMode.addEventListener("click", () => {
  document.body.setAttribute("data-mode", "viewer");
  btnViewerMode.classList.add("mode-active");
  btnEditorMode.classList.remove("mode-active");
  buildToc();
});
btnEditorMode.addEventListener("click", () => {
  document.body.setAttribute("data-mode", "editor");
  btnEditorMode.classList.add("mode-active");
  btnViewerMode.classList.remove("mode-active");
});

// テーマ切り替え
themeSelect.addEventListener("change", (e) => {
  document.documentElement.setAttribute("data-theme", e.target.value);
});

// フロントマターパネルのトグル
fmHeader.addEventListener("click", () => {
  const isCollapsed = fmBody.classList.toggle("collapsed");
  fmToggleIcon.textContent = isCollapsed ? "▼" : "▲";
});

// フロントマターの自動挿入
window.insertSuggestedFrontMatter = function() {
  const rawText = editorEl.value;
  let detectedTitle = "frb_expanded_thought";
  const h1Match = rawText.match(/^(?:#\s+|\s*#+\s*)(.*)$/m);
  if (h1Match && h1Match[1]) {
    detectedTitle = h1Match[1].trim().replace(/['"]/g, '');
  }
  const generatedFM = `---\ntitle: "${detectedTitle}"\nemoji: "📖"\ntype: "idea"\ntopics: ["ai", "development", "thought"]\npublished: false\n---\n\n`;
  editorEl.value = generatedFM + rawText;
  renderMarkdown(editorEl.value, "#", "Front Matter Generated");
};



// Qiita風 / コマンド入力（Code / Table）
const slashCommands = [
  {
    key: "code",
    aliases: ["code", "コード", "```"],
    icon: "</>",
    title: "Code block",
    desc: "``` で囲んだコードブロックを挿入",
    make: () => "```\n\n```"
  },
  {
    key: "table",
    aliases: ["table", "テーブル", "表"],
    icon: "▦",
    title: "Table",
    desc: "Markdownテーブルを挿入",
    make: () => "| 項目 | 内容 |\n|---|---|\n|  |  |"
  }
];
let slashState = { open: false, start: -1, query: "", active: 0 };

function getCurrentLineInfo() {
  const pos = editorEl.selectionStart;
  const value = editorEl.value;
  const lineStart = value.lastIndexOf("\n", pos - 1) + 1;
  const lineEndIdx = value.indexOf("\n", pos);
  const lineEnd = lineEndIdx === -1 ? value.length : lineEndIdx;
  return { pos, lineStart, lineEnd, line: value.slice(lineStart, lineEnd), beforeCaret: value.slice(lineStart, pos) };
}

function getSlashMatches(query) {
  const q = query.trim().toLowerCase();
  if (!q) return slashCommands;
  return slashCommands.filter(cmd => cmd.aliases.some(a => a.toLowerCase().startsWith(q)) || cmd.title.toLowerCase().includes(q));
}

function positionSlashMenu() {
  const rect = editorEl.getBoundingClientRect();
  slashMenu.style.left = Math.min(rect.left + 22, window.innerWidth - 300) + "px";
  slashMenu.style.top = Math.min(rect.top + 58, window.innerHeight - 180) + "px";
}

function showSlashMenu(query = "") {
  const matches = getSlashMatches(query);
  if (!matches.length) { hideSlashMenu(); return; }
  slashState.open = true;
  slashState.query = query;
  slashState.active = Math.min(slashState.active, matches.length - 1);
  slashMenu.innerHTML = `<div class="slash-hint">/ でMarkdown部品を挿入　↑↓ Enter / Esc</div>` + matches.map((cmd, i) => `
    <button type="button" class="slash-item ${i === slashState.active ? "active" : ""}" data-key="${cmd.key}" role="option" aria-selected="${i === slashState.active}">
      <span class="slash-icon">${cmd.icon}</span>
      <span><div class="slash-title">${cmd.title}</div><div class="slash-desc">${cmd.desc}</div></span>
    </button>
  `).join("");
  slashMenu.querySelectorAll(".slash-item").forEach(btn => {
    btn.addEventListener("mousedown", e => {
      e.preventDefault();
      applySlashCommand(btn.dataset.key);
    });
  });
  positionSlashMenu();
  slashMenu.classList.add("show");
}

function hideSlashMenu() {
  slashState.open = false;
  slashMenu.classList.remove("show");
}

function replaceRange(start, end, text, selectStartOffset = null, selectEndOffset = null) {
  const value = editorEl.value;
  editorEl.value = value.slice(0, start) + text + value.slice(end);
  const nextPos = start + text.length;
  if (selectStartOffset !== null && selectEndOffset !== null) {
    editorEl.setSelectionRange(start + selectStartOffset, start + selectEndOffset);
  } else {
    editorEl.setSelectionRange(nextPos, nextPos);
  }
  editorEl.focus();
  renderMarkdown(editorEl.value, "#", "Live Editing");
}

function insertAtCursor(text, selectStartOffset = null, selectEndOffset = null) {
  replaceRange(editorEl.selectionStart, editorEl.selectionEnd, text, selectStartOffset, selectEndOffset);
}

// Markdownショートカット（Ctrl+B / Cmd+B：選択文字を太字化）
function wrapSelection(prefix, suffix = prefix, placeholder = "text") {
  const start = editorEl.selectionStart;
  const end = editorEl.selectionEnd;
  const value = editorEl.value;
  const selected = value.slice(start, end);

  // 選択範囲が既に prefix/suffix で囲まれている場合は解除する
  const before = value.slice(Math.max(0, start - prefix.length), start);
  const after = value.slice(end, end + suffix.length);
  if (selected && before === prefix && after === suffix) {
    const newValue = value.slice(0, start - prefix.length) + selected + value.slice(end + suffix.length);
    editorEl.value = newValue;
    editorEl.setSelectionRange(start - prefix.length, end - prefix.length);
    editorEl.focus();
    renderMarkdown(editorEl.value, "#", "Live Editing");
    return;
  }

  const body = selected || placeholder;
  const wrapped = prefix + body + suffix;
  editorEl.value = value.slice(0, start) + wrapped + value.slice(end);

  if (selected) {
    editorEl.setSelectionRange(start + prefix.length, start + prefix.length + selected.length);
  } else {
    editorEl.setSelectionRange(start + prefix.length, start + prefix.length + placeholder.length);
  }

  editorEl.focus();
  renderMarkdown(editorEl.value, "#", "Live Editing");
}

function toggleBoldSelection() {
  wrapSelection("**", "**", "太字");
}


function applySlashCommand(key) {
  const cmd = slashCommands.find(c => c.key === key);
  if (!cmd) return;
  const { lineStart, lineEnd } = getCurrentLineInfo();
  const insertion = cmd.make();
  const suffix = editorEl.value.slice(lineEnd, lineEnd + 1) === "\n" ? "" : "\n";
  const prefix = lineStart > 0 && editorEl.value.slice(lineStart - 1, lineStart) !== "\n" ? "\n" : "";
  hideSlashMenu();
  replaceRange(lineStart, lineEnd, prefix + insertion + suffix);
}

function updateSlashFromInput() {
  const info = getCurrentLineInfo();
  const m = info.beforeCaret.match(/^\s*\/([\w\u3040-\u30ff\u3400-\u9fff`-]*)$/);
  if (!m) { hideSlashMenu(); return; }
  slashState.start = info.lineStart + info.beforeCaret.indexOf("/");
  showSlashMenu(m[1] || "");
}

editorEl.addEventListener("keyup", (e) => {
  if (["ArrowUp", "ArrowDown", "Enter", "Escape"].includes(e.key)) return;
  updateSlashFromInput();
});
editorEl.addEventListener("click", updateSlashFromInput);
editorEl.addEventListener("scroll", () => { if (slashState.open) positionSlashMenu(); });
window.addEventListener("resize", () => { if (slashState.open) positionSlashMenu(); });

document.addEventListener("click", (e) => {
  if (!slashMenu.contains(e.target) && e.target !== editorEl) hideSlashMenu();
});

editorEl.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "b") {
    e.preventDefault();
    hideSlashMenu();
    toggleBoldSelection();
    return;
  }
  if (!slashState.open) return;
  const matches = getSlashMatches(slashState.query);
  if (e.key === "ArrowDown") {
    e.preventDefault();
    slashState.active = (slashState.active + 1) % matches.length;
    showSlashMenu(slashState.query);
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    slashState.active = (slashState.active - 1 + matches.length) % matches.length;
    showSlashMenu(slashState.query);
  } else if (e.key === "Enter" || e.key === "Tab") {
    e.preventDefault();
    applySlashCommand(matches[slashState.active].key);
  } else if (e.key === "Escape") {
    e.preventDefault();
    hideSlashMenu();
  }
});

document.getElementById("btnInsertCode").addEventListener("click", () => insertAtCursor("```js\n// code here\n```\n", 6, 18));
document.getElementById("btnInsertTable").addEventListener("click", () => insertAtCursor("| 項目 | 内容 |\n|---|---|\n|  |  |\n"));

// エディター入力連動
editorEl.addEventListener("input", () => {
  isManagedMarkdownDirty = true;
  renderMarkdown(editorEl.value, "#", "Live Editing");
  updateSlashFromInput();
});

function setupSmoothScrollLinks() {
  tocEl.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const targetId = link.getAttribute("href").substring(1);
      const targetEl = document.getElementById(targetId);
      if(targetEl) {
        targetEl.scrollIntoView({ behavior: "smooth", block: "center" });
        targetEl.classList.remove("flash-target");
        void targetEl.offsetWidth; 
        targetEl.classList.add("flash-target");
      }
    });
  });
}


function isConstraintReportMarkdown(content) {
  const text = String(content || "");
  return (
    text.includes("## 制約グループ詳細") ||
    (text.includes("# AI制約設計書") && text.includes("#### 含まれる個別制約"))
  );
}

function normalizePseudoJapaneseLists(md) {
  const lines = String(md || "").split(/\r?\n/);
  let inFence = false;
  let inPseudoList = false;

  const normalized = lines.map(line => {
    const trimmed = line.trim();

    if (/^```/.test(trimmed) || /^~~~/.test(trimmed)) {
      inFence = !inFence;
      inPseudoList = false;
      return line;
    }
    if (inFence) return line;

    // 日本語記事でよく使う「・」「･」をMarkdownリストとして扱う。
    if (/^[ \t　]*[・･]\s*/.test(line)) {
      inPseudoList = true;
      return line.replace(/^[ \t　]*[・･]\s*/, "- ");
    }

    // 「・項目」の直後に全角スペース等で字下げされた行は、子リストとして扱う。
    if (inPseudoList && /^[ \t　]+\S/.test(line)) {
      const body = line.replace(/^[ \t　]+/, "");
      if (!/^([-*+]|\d+\.|#{1,6}\s|>|\||```|~~~)/.test(body)) {
        return "  - " + body;
      }
    }

    if (!trimmed) {
      inPseudoList = false;
      return line;
    }

    if (!/^[ \t　]/.test(line)) inPseudoList = false;
    return line;
  });

  return normalized.join("\n");
}

function applyMarkdownIndentClasses(enabled = false) {
  const indentClasses = ["md-indent-h4-content", "md-indent-h5-content", "md-indent-h6-content"];
  previewEl.classList.toggle("constraint-report", Boolean(enabled));
  previewEl.classList.toggle("normal-article", !Boolean(enabled));

  let currentHeadingLevel = 0;
  [...previewEl.children].forEach(el => {
    el.classList.remove(...indentClasses);
    const match = el.tagName.match(/^H([1-6])$/);
    if (match) {
      currentHeadingLevel = Number(match[1]);
      return;
    }

    // 通常記事ではインデント補正しない。
    // AI制約設計書レポートだけ、h4/h5/h6配下の本文・表・リストを軽く右へ寄せる。
    if (!enabled) return;

    if (currentHeadingLevel >= 6) {
      el.classList.add("md-indent-h6-content");
    } else if (currentHeadingLevel >= 5) {
      el.classList.add("md-indent-h5-content");
    } else if (currentHeadingLevel >= 4) {
      el.classList.add("md-indent-h4-content");
    }
  });
}

function buildToc(){
  const allHeadings=[...previewEl.querySelectorAll("h1,h2,h3")];
  allHeadings.forEach((h,i)=>{if(!h.id)h.id=slugify(h.textContent,i)});
  const headings=allHeadings.filter(h => {
    const lvl=Number(h.tagName.substring(1));
    return tocDepth==="all"||lvl<=Number(tocDepth);
  });
  tocEl.innerHTML="";
  if(!headings.length){tocEl.innerHTML='<span style="color:var(--muted);font-size:13px;">見出しがありません</span>';return}
  headings.forEach((h)=>{
    const a=document.createElement("a");
    a.href="#"+h.id;
    a.textContent=h.textContent;
    a.className="level-"+h.tagName.substring(1);
    tocEl.appendChild(a);
  });
  setupSmoothScrollLinks();
}

function updateMeta(rawMd, parsedContent){
  const chars = parsedContent.replace(/\s/g,"").length;
  charCountEl.textContent = chars.toLocaleString("ja-JP")+" 文字";
  readTimeEl.textContent = "約 "+Math.max(1,Math.ceil(chars/800))+" 分";
}

function renderMarkdown(rawMd, sourceUrl, sourceLabel){
  articleCard.style.opacity = 0.85;
  
  setTimeout(() => {
    const { data, content } = parseFrontMatter(rawMd);
    
    if (data) {
      fmSuggestArea.style.display = "none";
      fmPanel.style.display = "block";
      
      fmTitle.textContent = data.title || "-";
      const baseName = data.title ? data.title.toLowerCase().replace(/[^a-z0-9ー-龠ぁ-んァ-ヶ]/g, "_").substring(0, 30) : "article";
      fmSlug.textContent = baseName + ".md";
      
      if (!metaFileName.value || ["Front Matter Generated", "Clipboard Paste", "Local file"].includes(sourceLabel)) {
        syncFileNameUI(baseName + ".md");
      }
      
      fmEmoji.textContent = data.emoji || "💡";
      fmType.textContent = data.type || "tech";
      fmPublished.textContent = data.published !== undefined ? String(data.published) : "false";
      
      fmTopics.innerHTML = "";
      if (Array.isArray(data.topics)) {
        data.topics.forEach(t => {
          const span = document.createElement("span");
          span.className = "fm-tag";
          span.textContent = t;
          fmTopics.appendChild(span);
        });
      } else { fmTopics.textContent = "-"; }
      
    } else {
      fmPanel.style.display = "none";
      fmSuggestArea.style.display = "block";
      fmSuggestArea.innerHTML = `
        <div class="fm-suggest-card">
          <span class="fm-suggest-text">⚡ Zenn/Qiita用のフロントマターが設定されていません。</span>
          <button type="button" style="font-size:12px; padding:6px 12px; background:linear-gradient(135deg, #f59e0b, #d97706);" onclick="insertSuggestedFrontMatter()">設定ヘッダーを自動生成</button>
        </div>
      `;
      
      const h1Match = content.match(/^(?:#\s+|\s*#+\s*)(.*)$/m);
      const fallbackName = h1Match ? h1Match[1].trim().replace(/[^a-z0-9ー-龠ぁ-んァ-ヶ]/g, "_").substring(0, 20) : "frb_thought";
      if (!metaFileName.value) syncFileNameUI(fallbackName + ".md");
    }
    
    const constraintReport = isConstraintReportMarkdown(content);
    const renderContent = constraintReport ? content : normalizePseudoJapaneseLists(content);
    const html = marked.parse(preprocessQiita(renderContent));
    previewEl.innerHTML = DOMPurify.sanitize(html, { ADD_ATTR: ["target"] });
    previewEl.querySelectorAll('a[href^="http"]').forEach(a => { a.target = "_blank"; a.rel = "noreferrer"; });
    applyMarkdownIndentClasses(constraintReport);
    
    buildToc();
    updateMeta(rawMd, content);
    articleCard.style.opacity = 1;
  }, 40);
}


function isReadonlyLaunchModeValue(mode) {
  return String(mode ?? '').trim().toLowerCase() === 'readonly';
}

function normalizeLaunchMarkdownName(raw) {
  const value = String(raw ?? '').trim();
  if (!value) return null;
  const decoded = value.replace(/\\/g, '/');
  if (decoded.includes('://') || decoded.startsWith('//')) throw new Error(`file に外部URLは指定できません: ${value}`);
  if (decoded.startsWith('/')) throw new Error(`file に絶対パスは指定できません: ${value}`);
  if (/^[a-zA-Z]:/.test(decoded)) throw new Error(`file にローカルドライブパスは指定できません: ${value}`);
  if (/[?#]/.test(decoded)) throw new Error(`file にクエリ文字列やハッシュは指定できません: ${value}`);
  if (!/\.(md|markdown|txt)$/i.test(decoded)) throw new Error(`file は .md / .markdown / .txt を指定してください: ${value}`);
  const parts = decoded.split('/');
  if (parts.some(part => !part || part === '.' || part === '..')) throw new Error(`file のパスが不正です: ${value}`);

  let rel = parts.join('/');
  if (rel.startsWith('data/markdown/')) rel = rel.slice('data/markdown/'.length);
  if (rel.startsWith('markdown/')) rel = rel.slice('markdown/'.length);
  return rel;
}

function applyMarkdownReadonlyLaunchControls() {
  if (!launchMarkdownRuntime.readonly) return;
  editorEl.readOnly = true;
  editorEl.setAttribute('aria-readonly', 'true');
  [btnOverwriteManagedMd, document.getElementById('btnSaveFile'), localFileBtn, document.getElementById('btnPasteClip')]
    .forEach(btn => { if (btn) btn.disabled = true; });
  if (previewEl && !document.getElementById('readonlyLaunchNote')) {
    const note = document.createElement('div');
    note.id = 'readonlyLaunchNote';
    note.className = 'qiita-note info';
    note.textContent = 'URL Launch ReadOnly: このMarkdownは閲覧モードで開いています。';
    previewEl.parentElement?.insertBefore(note, previewEl);
  }
}

function normalizeMarkdownFileName(name) {
  let n = (name || "").trim();
  if (!n) n = "frb_thought.md";
  n = n.replace(/[\\/:*?"<>|]/g, "_");
  if (!/\.(md|markdown)$/i.test(n)) n += ".md";
  return n;
}

async function refreshManagedMarkdownList(selectName = "") {
  try {
    const res = await fetch("/api/markdown", { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const files = await res.json();
    managedMdSelect.innerHTML = "";
    if (!files.length) {
      const opt = document.createElement("option");
      opt.value = "";
      opt.textContent = "管理Markdownなし";
      managedMdSelect.appendChild(opt);
      return [];
    }
    files.forEach(name => {
      const opt = document.createElement("option");
      opt.value = name;
      opt.textContent = name;
      managedMdSelect.appendChild(opt);
    });
    const target = selectName || currentManagedMarkdownName || files[0];
    if (files.includes(target)) managedMdSelect.value = target;
    return files;
  } catch (err) {
    console.warn("管理Markdown一覧の取得に失敗", err);
    managedMdSelect.innerHTML = `<option value="">一覧取得失敗</option>`;
    return [];
  }
}

async function loadManagedMarkdown(name) {
  if (!name) return;
  if (isManagedMarkdownDirty && currentManagedMarkdownName && currentManagedMarkdownName !== name) {
    const ok = confirm("未保存の編集があります。保存せずに別のMarkdownを読み込みますか？");
    if (!ok) {
      managedMdSelect.value = currentManagedMarkdownName;
      return;
    }
  }

  previewEl.innerHTML = '<div class="status-shimmer">data/markdown から容赦なくMarkdown読み込み中...</div>';
  try {
    const res = await fetch(`/api/markdown/${encodeURIComponent(name)}`, { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const md = await res.text();
    currentManagedMarkdownName = name;
    isManagedMarkdownDirty = false;
    editorEl.value = md;
    syncFileNameUI(name);
    renderMarkdown(md, "#", "Managed Markdown");
    applyMarkdownReadonlyLaunchControls();
  } catch (err) {
    previewEl.innerHTML = `<div class="qiita-note warn">管理Markdown読み込みエラー: ${err.message}</div>`;
  }
}

async function saveManagedMarkdown(name, content, quiet = false) {
  const fileName = normalizeMarkdownFileName(name);
  const res = await fetch(`/api/markdown/${encodeURIComponent(fileName)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: fileName, content })
  });
  if (!res.ok) throw new Error(await res.text());
  currentManagedMarkdownName = fileName;
  isManagedMarkdownDirty = false;
  syncFileNameUI(fileName);
  await refreshManagedMarkdownList(fileName);
  if (!quiet) alert(`保存しました: data/markdown/${fileName}`);
  return fileName;
}

async function askRegisterAsManagedMarkdown(fileName, content) {
  const safeName = normalizeMarkdownFileName(fileName || metaFileName.value || editorFileName.value);
  syncFileNameUI(safeName);
  const ok = confirm(`${safeName} を data/markdown の管理対象にしますか？\n\nOK: data/markdown に保存して管理対象にする\nキャンセル: 画面上で開くだけ`);
  if (!ok) {
    currentManagedMarkdownName = "";
    isManagedMarkdownDirty = true;
    return;
  }
  try {
    await saveManagedMarkdown(safeName, content, true);
    alert(`管理対象にしました: data/markdown/${safeName}`);
  } catch (err) {
    alert("管理対象への保存に失敗しました。\n" + err.message);
  }
}

async function loadMarkdown(rawUrl){
  if(!rawUrl.startsWith("http")) return;
  previewEl.innerHTML='<div class="status-shimmer">思考空間を同期中（Markdown読み込み中）...</div>';
  try{
    const res=await fetch(rawUrl,{cache:"no-store"});
    if(!res.ok)throw new Error(`HTTP ${res.status}`);
    const md=await res.text();
    editorEl.value = md;
    renderMarkdown(md, rawUrl, "GitHub Raw");
  }catch(err){
    previewEl.innerHTML=`<div class="qiita-note alert">読み込みエラー: ${err.message}</div>`;
  }
}

function loadLocalFile(file){
  if(!file)return;
  previewEl.innerHTML='<div class="status-shimmer">ローカルの思考コアを展開中...</div>';
  const reader=new FileReader();
  reader.onload=async ()=>{
    const md=String(reader.result||"");
    currentManagedMarkdownName = "";
    isManagedMarkdownDirty = true;
    editorEl.value = md;
    syncFileNameUI(normalizeMarkdownFileName(file.name));
    renderMarkdown(md, "#", "Local file");
    await askRegisterAsManagedMarkdown(file.name, md);
  };
  reader.readAsText(file,"UTF-8");
}

// ファイルダイアログ連動保存
document.getElementById("btnSaveFile").addEventListener("click", () => {
  const blob = new Blob([editorEl.value], { type: "text/markdown;charset=utf-8;" });
  const a = document.createElement("a");
  const saveName = metaFileName.value || "frb_expanded_thought.md";
  a.href = URL.createObjectURL(blob);
  a.download = saveName;
  a.click();
});

// 超速クリップボード流し込み
document.getElementById("btnPasteClip").addEventListener("click", async () => {
  try {
    const text = await navigator.clipboard.readText();
    editorEl.value = text;
    renderMarkdown(text, "#", "Clipboard Paste");
    const originalText = document.getElementById("btnPasteClip").textContent;
    document.getElementById("btnPasteClip").textContent = "⚡ 思考同期完了！";
    setTimeout(() => document.getElementById("btnPasteClip").textContent = originalText, 1500);
  } catch (err) {
    alert("クリップボードの読み込み権限を許可してください。");
  }
});

btnRefreshManagedMd.addEventListener("click", async () => {
  const files = await refreshManagedMarkdownList(currentManagedMarkdownName);
  if (files.length && !currentManagedMarkdownName) await loadManagedMarkdown(managedMdSelect.value);
});

managedMdSelect.addEventListener("change", () => loadManagedMarkdown(managedMdSelect.value));

btnOverwriteManagedMd.addEventListener("click", async () => {
  try {
    const saveName = normalizeMarkdownFileName(currentManagedMarkdownName || metaFileName.value || editorFileName.value);
    if (!currentManagedMarkdownName) {
      const ok = confirm(`${saveName} を data/markdown の管理対象として保存しますか？`);
      if (!ok) return;
    }
    await saveManagedMarkdown(saveName, editorEl.value);
  } catch (err) {
    alert("上書き保存に失敗しました。\n" + err.message);
  }
});

document.getElementById("loadBtn").addEventListener("click",()=>loadMarkdown(mdUrlEl.value));
localFileBtn.addEventListener("click",()=>localFileInput.click());
localFileInput.addEventListener("change",e=>loadLocalFile(e.target.files&&e.target.files[0]));

// 強固な全画面ドラッグ＆ドロップ検知
window.addEventListener("dragover", (e) => {
  e.preventDefault();
  document.body.classList.add("drag-over");
});
window.addEventListener("dragleave", (e) => {
  e.preventDefault();
  if (e.clientX === 0 && e.clientY === 0) {
    document.body.classList.remove("drag-over");
  }
});
window.addEventListener("drop", (e) => {
  e.preventDefault();
  document.body.classList.remove("drag-over");
  if (e.dataTransfer && e.dataTransfer.files.length > 0) {
    loadLocalFile(e.dataTransfer.files[0]);
  }
});

tocDepthBtns.forEach(btn=>btn.addEventListener("click",()=>{
  tocDepth=btn.dataset.depth;
  tocDepthBtns.forEach(b=>b.classList.toggle("active",b.dataset.depth===tocDepth));
  buildToc();
}));

// 初期ロード: ?file=xxx.md があればそれを優先。無ければ data/markdown の先頭を読む。
(async () => {
  const params = new URLSearchParams(location.search);
  const requestedFileRaw = params.get('file') || params.get('md');
  const mode = params.get('mode') || '';
  launchMarkdownRuntime = {
    fromUrl: Boolean(requestedFileRaw),
    readonly: isReadonlyLaunchModeValue(mode),
    fileParam: requestedFileRaw || ''
  };

  try {
    const requestedFile = requestedFileRaw ? normalizeLaunchMarkdownName(requestedFileRaw) : '';
    const files = await refreshManagedMarkdownList(requestedFile || '');
    if (requestedFile) {
      await loadManagedMarkdown(requestedFile);
    } else if (files.length) {
      await loadManagedMarkdown(managedMdSelect.value || files[0]);
    } else {
      loadMarkdown(mdUrlEl.value);
      applyMarkdownReadonlyLaunchControls();
    }
  } catch (err) {
    console.error(err);
    previewEl.innerHTML = `<div class="qiita-note warn">URL Launch 読み込みエラー: ${String(err.message || err)}</div>`;
    applyMarkdownReadonlyLaunchControls();
  }
})();
