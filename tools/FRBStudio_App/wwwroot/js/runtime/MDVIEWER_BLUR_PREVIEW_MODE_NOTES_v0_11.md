# MD Viewer Blur Preview Mode Notes v0.11

## 目的

Markdown Viewer / Editor に、本文エディターからフォーカスが外れたときに Viewer 表示へ自動復帰する動作を追加した。

Studio側の Markdown 編集欄と同じく、以下の往復を実現する。

```text
書く
↓
カーソルを外す
↓
記事として読む
```

## 動作

- Editorモードで本文textareaを編集する
- textareaからフォーカスが外れる
- editor内の補助ボタンや slash menu への移動でなければ Viewerモードへ戻る
- Markdownは再レンダリングされる
- 編集位置に近い見出し、またはスクロール比率を使って、Viewer側のスクロール位置を復元する

## スクロール復元方針

優先順位は以下。

1. カーソル位置より前の直近Markdown見出しを探す
2. Preview内の同じ見出しへスクロールする
3. 見出しが見つからない場合は editor の scrollTop 比率を preview 側へ反映する

## 保存方針

保存値はMarkdown原文のまま保持する。
Viewer表示はHTML化されたプレビューであり、HTMLをMarkdown原文へ混入させない。

## 注意

Markdown原文とPreview HTMLでは高さが一致しないため、スクロール復元は完全一致ではなく「近い位置へ戻す」方針とする。
