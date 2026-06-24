# v0.13.2 Markdown TableCell Editor Notes

## 目的

Markdown表を、本文文字列としてではなく TableBlock / TableCell として扱い、Preview上からセル単位で編集できる入口を追加する。

会社でCopilotが出した表形式の計画案に対して、Markdown上でセル単位コメント・編集がしづらく、Excelへ逃げるしかなかった体験を踏まえた改善。

## 対応内容

- `table` Blockに対して、DOM上の `th` / `td` へ TableCellメタデータを付与
  - `data-md-table-id`
  - `data-md-table-block-id`
  - `data-md-cell-id`
  - `data-md-cell-row-index`
  - `data-md-cell-column-index`
  - `data-md-cell-line`
- Editorモードで表セルをクリックすると、小ダイアログを表示
- 小ダイアログ内でセル値を編集し、反映するとMarkdown表行を再生成
- `|` は `\|` へ変換
- 改行は `<br>` へ変換
- 直前操作は既存の SentenceBlock undo と同じバックアップ構造を利用
- 右クリックメニューにも `TableCell編集` を追加

## 対象範囲

MVPでは GitHub Flavored Markdown 風の単純表を対象にする。

```markdown
| 項目 | 内容 |
|---|---|
| A | B |
```

## 対象外

- 結合セル
- HTML table
- Excel完全互換
- 列幅の維持
- セル内MarkdownのWYSIWYG編集
- 表全体の行追加・列追加・列削除

## 判断

セル編集は、Markdown原文に直接spliceするのではなく、Block Modelで得たTableBlockの行番号・列番号を使って、対象行だけをMarkdown表行として再生成する。

## 注意

Markdown表の区切り行はDOMには描画されないため、DOM上のtbody行はMarkdown上のrow index +2として扱う。

```text
Markdown row 0: header
Markdown row 1: separator
Markdown row 2+: body
```
