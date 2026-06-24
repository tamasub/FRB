# v0.13.5-md-roundtrip-save-safety

## 目的

Markdown Block / TableCell / Sidecarコメント編集が増えてきたため、保存時に本文破壊・表構造崩れ・Sidecarコメント迷子を検知するための保存安全性レイヤーを追加する。

## 実装方針

- Markdown保存前に Save Safety 検査を実行する。
- 検査前に localStorage へ直前バックアップを保存する。
- エラーがある場合は保存を中止する。
- 警告がある場合は確認ダイアログを出す。
- 保存後に `/api/markdown/{name}` で再取得し、保存前本文と一致するか確認する。
- `.comments.json` は従来の Sidecar 保存処理を使い、本文にはコメントを混入しない。

## 検査項目

- Markdown Block Model の解析安定性
- コードブロックのフェンス閉じ忘れ
- Markdown表の列数不一致
- Markdown表の区切り行認識
- Sidecarコメントの対象Block / TableCell参照
- Markdownレンダリング例外
- 読込時点との差分行数サマリ

## UI

上部の管理Markdown操作エリアに `保存検査` ボタンを追加する。
保存検査ボタンは直近の検査結果に応じて `OK / nW / nE` 表示へ変わる。

## バックアップ

保存前バックアップは以下のlocalStorageキーに保存する。

```text
frb-md-save-backup:<filename>:latest
```

保存内容にはMarkdown本文、SidecarコメントJSON、検査結果を含める。

## 未対応

- Git diff相当の詳細差分ビュー
- バックアップ一覧UI
- 復元ボタン
- Markdown ASTによる厳密な再生成比較

まずは、保存直前に壊しそうな兆候を止めるMVPとする。
