# MARKDOWN_RAW_BLOCK_DIALOG_EDITOR_NOTES_v0_13_7

## 概要

Markdown Viewer / Editor の Editor モードで、通常のMarkdown BlockをRaw Markdown断片として小ダイアログ編集できるようにした。

## 方針

- 左クリック: 表セルは従来どおり TableCell編集、通常Blockは Raw Markdown編集。
- 右クリック: `✏ Raw Markdown編集` と `📝 テキストボックス編集` を併存。
- Raw Markdown編集では、`#` / `-` / `>` / fenced code block の ``` を隠さない。
- code_block は中身だけではなく、開始・終了フェンスを含むBlock全体を編集する。
- 反映時は対象Blockの start_line / end_line の範囲だけを置換し、Markdownを再描画する。
- 既存のUndoバックアップ、Save Safety、Sidecarコメント運用に乗せる。

## 未対応

- WYSIWYG編集。
- Markdown ASTによる厳密な構造修復。
- 複数Block横断編集。

## 確認観点

1. Editorモードで通常本文行を左クリックし、Raw Markdown編集ダイアログが出ること。
2. heading / list_item / blockquote で `#` や `-` や `>` が表示されたまま編集できること。
3. code_block でフェンス込みの全体が編集できること。
4. 右クリックメニューから Raw Markdown編集とテキストボックス編集の両方を選べること。
5. 反映後にSave Safetyが通ること。
