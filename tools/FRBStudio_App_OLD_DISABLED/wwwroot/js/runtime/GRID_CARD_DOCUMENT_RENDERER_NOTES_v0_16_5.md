# v0.16.5 Grid Card(Document) Renderer

## 目的

短文・一覧編集向けの従来 Table/Compact Grid を維持したまま、長文・レビュー向けの Card(Document) Grid を ViewDef で選択できるようにした。

## ViewDef指定

Grid section に以下のような指定を追加する。

```json
{
  "type": "grid",
  "dataPath": "work_items",
  "grid": {
    "renderer": "document",
    "displayStyle": "card",
    "document": {
      "titleField": "title",
      "metaFields": ["phase", "status", "verification_status"],
      "fields": [
        "phase",
        "title",
        { "field": "objective", "markdown": { "enabled": true, "allowLinks": true, "allowImages": true } }
      ]
    }
  }
}
```

未指定時は従来どおり Table/Compact Grid として描画する。

## 実装方針

- `renderGrid()` は ViewDef の `grid.renderer` / `grid.displayStyle` を見て、`gridTable` または `gridDocument` へ委譲する。
- Table/Compact Grid は既存の一覧表示・ソート・ダブルクリック詳細を維持する。
- Card(Document) Grid はカード内フィールドをクリックして原文編集できる。
- Markdown対象フィールドは表示時にMarkdownとして読むが、編集時は原文を扱い、保存値にHTMLを混ぜない。
- 行操作は、末尾追加・上挿入・下挿入・削除・複製・上下移動をカード上で扱う。

## Preview背面問題の修正

Detailサブグリッドのプレビューは、従来 `div` overlay だったため、`detailDialog.showModal()` の背面に隠れることがあった。

v0.16.5では、プレビュー自体を `dialog.showModal()` で開くようにし、後から開いたPreviewをブラウザのtop-layerへ載せる。

## 確認観点

- `grid.renderer` 未指定のViewDefでは従来Table Gridが維持されること。
- `grid.renderer: "document"` 指定時にCard(Document) Gridへ切り替わること。
- カード内テキスト/textarea/selectを編集し、blur/F12/Ctrl+Enterで反映できること。
- Markdown表示はプレビュー、編集値はMarkdown原文として保持されること。
- 末尾追加・上挿入・下挿入・削除・複製・上下移動で配列順序が壊れないこと。
- DetailからサブグリッドPreviewを開いても背面に隠れないこと。
