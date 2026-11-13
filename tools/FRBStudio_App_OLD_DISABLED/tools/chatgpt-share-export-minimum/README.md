# ChatGPT Share Export Minimum v0.1

ChatGPTの共有URLを1件受け取り、会話ログをMarkdownファイルへ保存する最小CLIです。

## 今回の範囲

```text
共有URL 1件
  ↓
Playwrightで共有ページを開く
  ↓
User / Assistant の表示テキストを取得
  ↓
Markdown 1ファイルを保存
  ↓
処理結果を標準出力へJSON 1行で返す
```

StudioくんのGrid、一括実行、状態更新はまだ含めていません。

## 前提

- Windows
- Node.js 20以上（Node.js 22推奨）
- 一般公開されている `https://chatgpt.com/share/...` URL

Business / Enterpriseなど、閲覧にログインやワークスペース権限が必要なURLは、この最小版では対象外です。

## 1. 初回セットアップ

フォルダ内の次を実行します。

```bat
setup.cmd
```

NodeパッケージとPlaywright用Chromiumがインストールされます。

## 2. 実行

```bat
export.cmd "https://chatgpt.com/share/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

保存先を指定する場合:

```bat
export.cmd "https://chatgpt.com/share/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" "F:\chat_logs"
```

Node.jsから直接呼ぶ場合:

```bat
node export_chatgpt_share.mjs "https://chatgpt.com/share/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" output
```

画面を表示して動作確認する場合:

```bat
node export_chatgpt_share.mjs "https://chatgpt.com/share/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" output --headed
```

## 出力ファイル

例:

```text
output/
└─ 20260720_193000_会話タイトル.md
```

Markdownの構造:

```markdown
---
title: "会話タイトル"
source_url: "https://chatgpt.com/share/..."
exported_at: "2026-07-20T10:30:00.000Z"
message_count: 12
---

# 会話タイトル

## 001 User

相談内容...

## 002 Assistant

回答内容...
```

## 標準出力

成功時:

```json
{"status":"SUCCESS","source_url":"https://chatgpt.com/share/...","title":"会話タイトル","message_count":12,"output_file":"F:\\...\\output\\....md","exported_at":"..."}
```

失敗時:

```json
{"status":"FAILED","source_url":"https://chatgpt.com/share/...","error":"エラー内容"}
```

- 成功終了コード: `0`
- 処理失敗: `1`
- 引数・URL不正: `2`

この契約なら、将来Studioくんからプロセス実行し、標準出力JSONをGridのステータスへ反映できます。

## 現時点の制約

- ChatGPT画面のDOMを参照するため、画面構造変更時はセレクタ修正が必要です。
- 最小版は表示テキストを保存します。画像・添付ファイル本体・生成物は保存しません。
- Markdownの見出しやコードブロックは、画面上の表示テキストとして取得されます。完全な元Markdown復元ではありません。
- 共有リンクの範囲までしか取得できません。元チャットへ後から追加した未共有メッセージは対象外です。

## 次段階の想定

```text
Grid登録JSON
- id
- shared_url
- status
- output_file
- message_count
- last_error
- downloaded_at

一括Runner
  ↓
このCLIをURLごとに呼び出す
  ↓
標準出力JSONをGridへ反映
```
