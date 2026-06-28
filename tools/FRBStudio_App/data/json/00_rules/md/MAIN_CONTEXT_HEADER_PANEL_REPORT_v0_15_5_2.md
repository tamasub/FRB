# v0.15.5.2 Main Context Header Panel Report

## 目的

主文脈を通常Gridの主役にせず、画面全体の入口として概要ヘッダー上に要約表示し、必要時だけ展開して明細確認・編集できるようにする。

## 方針

- ViewDefは文脈実データを持たない。
- 主文脈の実データはData root `main_context_refs[]` に置く。
- ViewDefは `context.main_context.data_path` 等で、主文脈データの場所と表示方法だけを宣言する。
- Runtimeは主文脈をヘッダー要約 + 展開パネルとして表示する。
- 通常Gridは対象一覧・インシデント一覧・テストパターン一覧など本来の作業対象を扱う。

## 更新内容

### Runtime

- `currentViewDefContextModel` を追加。
- `context.main_context.data_path` を正規化する `extractViewDefContextModel()` を追加。
- Data root の主文脈refsをヘッダー上に表示する `renderMainContextHeaderPanel()` を追加。
- 主文脈パネルで編集した値をData側へ戻す `applyMainContextHeaderPanelEdits()` を追加。
- `applyHeaderEdits()` 実行時に主文脈パネル編集も回収する。

### Sample ViewDef

- `mainContextGrid` を撤去。
- `targetsGrid` を唯一の主Gridに戻した。
- 主文脈は `context.main_context.data_path = "$.main_context_refs"` で宣言し、Runtimeヘッダーパネルが表示する。

### Rules / Schema

- 主文脈ヘッダーパネル契約をViewDef生成ルールへ追加。
- `mainContextContract` に `header_panel` / `display_mode` の表示ヒントを追加。

## 次フェーズ

`v0.15.5.3-target-context-detail-panel` で、対象文脈 `context_refs[]` をDetail上部に表示する。
