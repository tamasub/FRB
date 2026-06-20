# FRB Studio — Markdown AI Prompt / AI Copy Block 028

## 目的

Markdown出力の最後尾に、AIへそのまま貼り付けられるブロックを出力する。

不足検出 VirtualData の結果を使って、Expected / Check 追加候補をAIに作らせるループを作る。

```text
不足検出 VirtualData
  ↓
Markdown出力
  ↓
AI貼り付け用プロンプト + TSV + Grid JSON
  ↓
AIが追加候補JSONを生成
  ↓
人間レビュー
  ↓
qa_expected_checks_classified_v0_1.json に追記
  ↓
再度、不足検出 VirtualData
```

## 追加・変更ファイル

```text
wwwroot/app.js
  - Markdown出力末尾に AI貼り付け用ブロックを追加
  - section.markdown.aiPrompt を解釈
  - filtered / all / selected の rowSource に対応
  - TSV と Grid JSON を出力

defs/qa_shortage_expected_findings_view_def_v0_1.json
  - mainGrid.markdown.aiPrompt を追加

schema_RULES/FRB_VIEW_DEF_GENERATION_RULES_v0_14_markdown_ai_prompt.md
schema_RULES/README_viewdef_rules_v0_14.md
  - ルール文書を追加
```

## 使い方

```text
データJSON:
  qa_expected_checks_classified_v0_1.json

画面定義JSON:
  qa_shortage_expected_findings_view_def_v0_1.json

操作:
  Markdown出力→Viewer
```

Markdownの最後尾に次が出る。

```text
# AI貼り付け用

## Expected / Check 追加候補生成プロンプト

- プロンプト
- 現在表示中の不足検出TSV
- Grid JSON
```

## rowSource

今回の不足検出ViewDefは `rowSource: "filtered"`。

そのため、検索で絞り込んでからMarkdown出力すれば、表示中の不足だけをAIに渡せる。

## 方針

- ブラウザコピーでは落ちるヘッダキャプションを、Markdown出力で確実に保持する。
- TSVはAIへ貼り付けやすい入力形式。
- Grid JSONは field / caption / rows を保持する正確性優先の入力形式。
