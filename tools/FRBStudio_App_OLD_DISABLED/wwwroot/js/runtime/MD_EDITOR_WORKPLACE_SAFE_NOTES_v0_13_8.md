# v0.13.8-md-editor-workplace-safe notes

## 目的

会社Edge環境で Markdown Viewer / Editor の編集ダイアログやセル編集が不安定になる問題に対して、貼り付け安全化・編集UI安定化・デバッグ表示非表示・Editor初期表示・`/code` 挿入をまとめて扱う。

## 対応方針

- 編集ダイアログ内の `paste` / `beforeinput` / `input` / `keydown` / pointer系イベントを外側の閉じ処理へ伝播させない。
- Ctrl+Enter / Escape / 明示ボタン以外で閉じる設計に寄せる。
- フローティングメニューはヘッダー下端より上に出ないように補正する。
- URLで `mode` が指定されていない場合は Editor 初期表示へ寄せる。
- 通常利用ではカレントBlock/Cellのデバッグ行番号表示を隠す。
- 空Markdown時も開始できるようプレースホルダーを表示する。
- Editor textareaで `/code` 行を Enter した場合、 fenced code block を挿入する。

## 制約

- テーブル挿入は今回対応しない。
- GitHub raw の `mdViewer.html` がHTMLとしてツール側でダウンロード制限されたため、このZIPには直接書き換え済み `mdViewer.html` ではなく、ローカルの `wwwroot/mdViewer.html` へ注入する patch applicator を収録する。
- `wwwroot/data` / `wwwroot/defs` は更新しない。

## 適用方法

`tools/FRBStudio_App` 直下で以下を実行する。

```bash
python wwwroot/patches/apply_v0_13_8_md_editor_workplace_safe.py
```

実行すると `wwwroot/mdViewer.html.bak_v0_13_8` を作成したうえで、`</body>` 直前に workplace-safe guard を注入する。

## 確認ポイント

- 会社Edgeでセル編集ダイアログに貼り付けてもダイアログが閉じないこと。
- 起動直後に Editor が選択されること。
- フローティングメニューがヘッダーより上に食い込まないこと。
- `mdblk_... / Lxx-yy` のようなデバッグ表示が通常表示されないこと。
- 空Markdownでも入力開始できること。
- Editor textareaで `/code` と入力して Enter すると ` ```text ... ``` ` が挿入されること。
