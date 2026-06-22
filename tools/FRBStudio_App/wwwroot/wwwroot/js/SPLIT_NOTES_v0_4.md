# v0.4-split Notes

目的: 既存機能を維持したまま、巨大な `app.js` を責務ごとに分割する。

## 方針

- `type="module"` 化は行わない。
- 従来 script 方式で読み込み順を明示する。
- 既存のグローバル状態・関数呼び出しは維持する。
- 固定フィールド名の全面撤去は行わない。
- 固定名を見つけた場合は、即削除ではなく分類する。

## 固定名の分類

| 分類 | 方針 |
| --- | --- |
| Studio仕様の固定名 | OK |
| DOMシェル固定名 | OK |
| ViewDef宣言値 | 条件付きOK |
| Adapter / Builder 内の仕様固定名 | 条件付きOK |
| Runtime内のData固定名 | 原則NG |

Runtime内のData固定名であっても、Studio標準メタフィールドとして憲法・仕様に明記されたものは例外とする。

## 分割ファイル

- `js/core/state.js`
- `js/core/file_api.js`
- `js/core/field_types.js`
- `js/core/viewdef_resolver.js`
- `js/core/loaders.js`
- `js/ui/page_setup.js`
- `js/core/data_utils.js`
- `js/virtualData/relation_builders.js`
- `js/virtualData/expected_builders.js`
- `js/renderers/field_controls.js`
- `js/renderers/grid_detail.js`
- `js/markdown/data_markdown.js`
- `js/markdown/viewdef_markdown.js`
- `js/runtime/detail_save.js`
- `js/runtime/load_runtime.js`
- `app.js`

## 注意

この段階は v0.4-split であり、Registry化や `toolbar.executeButton` の本格対応は行わない。
