# v0.16.2 Detail SubGrid Table Edit Core MVP

## 目的

Detail画面内の `objectArray` / `stringArray` サブグリッドを、特定フィールド名に依存せず編集できるようにする。

## 実装方針

- 外部DataGridライブラリは導入しない。
- `field.type === "objectArray"` / `field.type === "stringArray"` を汎用編集対象とする。
- `context_refs` などの専用フィールド名には依存しない。
- 保存値はJSON値を正本とし、F12 / 反映ボタンで親JSONへ同期する。
- 文字列セルはMarkdown原文を保持できる前提で扱う。MVPではMarkdownプレビューまでは行わない。

## MVP範囲

- セル編集
- 行追加
- 行削除
- 変更中バッジ
- F12 / 反映ボタンで親JSONへ同期
- `stringArray` は `value` 列として編集
- `objectArray` は既存行のkey、またはViewDefの `edit.subGrid.columns` / `itemFields` から列を生成

## 将来候補

- Studio Table Edit Core への抽出
- Markdown Editor の表編集との共通化
- 文字列セルのMarkdown表示・Markdownプレビュー
- objectArray読み物表示モード
- 子行専用ダイアログ
