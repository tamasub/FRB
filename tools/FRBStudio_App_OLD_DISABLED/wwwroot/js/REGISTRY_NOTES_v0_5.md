# v0.5-registry Notes

## 目的

v0.4-splitで責務分割したStudioくんに、Registryの骨格を追加した。

この段階の目的は、ステップ数を減らすことではなく、次の追加・変更時に触る場所を明確にすること。

## 追加したRegistry

- `js/core/registry.js`
  - 小さな汎用Registryプリミティブ
- `js/renderers/renderer_registry.js`
  - 高レベルRenderer登録
- `js/renderers/field_control_registry.js`
  - Field type/controlごとの入力部品Renderer登録
- `js/virtualData/virtual_data_registry.js`
  - virtualData builder登録
- `js/markdown/markdown_registry.js`
  - markdown.typeごとのMarkdown出力builder登録
- `js/actions/action_registry.js`
  - v0.6-action-execute-buttonで使うActionRegistryの受け皿

## 実施したこと

- `virtualData` の builder 分岐を `VirtualDataBuilderRegistry` へ移動
- `markdown.type` の分岐を `MarkdownExportRegistry` へ移動
- `createInput` の field type 分岐を `FieldControlRegistry` へ移動
- `loadFromObjects` の初期描画呼び出しを `RendererRegistry` 経由へ変更
- 既存ヘッダーボタンの動作は変更しない
- `toolbar.executeButton` 本格対応は v0.6 に残す
- `type="module"` 化は行わない

## 固定名方針

- ViewDefで宣言される builder名 / markdown.type / field.type は、Registryのキーとして扱う
- Runtime側にData固定フィールド名を増やさない
- 既存のAdapter / Builder 内の仕様フィールドは、今回のv0.5では撤去せず分類対象として維持する

## 確認

- 全JSに対して `node --check` 済み
- ブラウザ実機確認は利用者環境で実施する
