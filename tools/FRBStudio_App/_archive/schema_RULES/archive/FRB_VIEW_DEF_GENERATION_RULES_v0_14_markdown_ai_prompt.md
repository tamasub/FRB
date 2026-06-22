# FRB ViewDef Generation Rules v0.14 — Markdown AI Prompt / AI Copy Block

## 目的

Markdown出力時に、画面で表示中のグリッド行を AI にそのまま渡せる形で出力する。

これにより、次のループを自然に回せる。

```text
VirtualDataで不足検出
  ↓
Markdown出力
  ↓
AI貼り付け用プロンプト + TSV + Grid JSON
  ↓
AIが追加候補JSONを生成
  ↓
人間レビュー
  ↓
元JSONに追記
  ↓
再度VirtualDataで不足検出
```

## section.markdown.aiPrompt

AI貼り付け用プロンプトは、対象グリッド section に持たせる。

```json
{
  "id": "mainGrid",
  "type": "grid",
  "caption": "不足検出一覧",
  "dataPath": "$.expected_shortage_findings",
  "markdown": {
    "aiPrompt": {
      "enabled": true,
      "title": "Expected / Check 追加候補生成プロンプト",
      "targetFile": "qa_expected_checks_classified_v0_1.json",
      "rowSource": "filtered",
      "visibleOnly": true,
      "includeGridJson": true,
      "template": [
        "以下は不足検出一覧のTSVです。",
        "この内容をもとに、{{targetFile}} に追加する Expected / Check 候補を作成してください。",
        "",
        "条件:",
        "- テストパターンIDは増やさない",
        "- expected_checks の追加候補だけ作る",
        "- 既存check_idと重複しない",
        "- 出力は追加候補だけのJSON配列にしてください",
        "",
        "TSV:"
      ]
    }
  }
}
```

## 出力内容

Markdown出力の末尾に、次を追加する。

```text
# AI貼り付け用

## Expected / Check 追加候補生成プロンプト

プロンプト + TSV

Grid JSON
```

## rowSource

| 値 | 意味 |
| --- | --- |
| filtered | 現在表示中の行。検索・絞り込み後の行を使う。既定値。 |
| all / current | currentRows 全体を使う。 |
| selected | 選択中の1行だけを使う。 |

## 変数

`template` では `{{変数名}}` を使える。

| 変数 | 意味 |
| --- | --- |
| targetFile | 追加候補の投入先ファイル名 |
| sourceFile / dataFile | 現在の対象JSONファイル名 |
| viewDef | 現在のViewDefファイル名 |
| sectionCaption | 対象sectionのcaption |
| rowCount | 出力対象行数 |
| totalRowCount | currentRows全体件数 |
| filteredRowCount | 表示中件数 |

## 方針

- Markdown本文は人間確認用。
- AI貼り付け用ブロックは、AIへの依頼文と入力データをまとめる。
- TSVは人間にもAIにも読みやすい形式。
- Grid JSONは field/caption/rows を保持し、列意味の取り違えを防ぐ。
- この出力は保存データには書き戻さない。
