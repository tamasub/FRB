# FRB Studio Core 文脈サマリー

更新日: 2026-07-16  
対象: `F:\FRB\tools\FRBStudio_App\wwwroot`  
目的: StudioくんのCore改修を始める際に、全体解析を毎回やり直さず、人間とAIが同じ設計文脈から作業を開始するための入口。

---

## 1. 最初に押さえる結論

`wwwroot` は、Studioくんの汎用JSON研究・編集基盤である。

中心思想は次の分離にある。

```text
Data
  = 内容・事実・研究対象の正本

ViewDef
  = 表示、編集、検索、文脈参照、Action、Markdown化の宣言

Core
  = DataとViewDefを解釈して画面を組み立てる汎用ランタイム

Overlay / Plugin
  = Coreへ混ぜないドメイン専用機能
```

Coreへ個別業務やFX固有の条件を直接追加しない。汎用性がない処理は、原則としてOverlay側へ置く。

---

## 2. アプリ全体における位置づけ

Studioくんは大きく次の層で構成される。

```text
Program.cs/Program.cs
  Windowsトレイアプリ + ASP.NET Coreホスト + ファイル/API境界
      ↓
wwwroot/
  汎用JSON UI、ViewDefランタイム、PluginHost、各種Viewer
      ↓
defs/ + data/json/
  Core側ViewDefと管理Data
      ↓
studio_overlays/{overlayId}/
  manifestで宣言されたドメイン別追加物
```

バックエンドは通常 `http://localhost:5055` で静的ファイルとAPIを提供する。

---

## 3. 主要エントリーポイント

### `index.html`

Studioくん本体画面のDOMとスクリプト読込順を定義する。

画面の主な領域:

- Data / ViewDef選択、Drop、再読込
- ヘッダー・Main Context
- 検索欄
- グリッドまたはDocument Card
- Actionツールバー
- 詳細編集ダイアログ
- 行コンテキストメニュー

### `app.js`

初期化とイベント配線を担当する薄い統合層。

主な責務:

- Data / ViewDef選択イベント
- Dropイベント
- Overlay Plugin読込開始
- URLパラメータによる自動読込
- Viewer起動
- Screen Stateテスト用フック
- Status / Toast連携

個別の描画・保存ロジックは、できるだけ各責務ファイルへ置く。

### `styles.css`

Studio本体の画面スタイル。約2,700行あるため、変更時は対象DOMと状態クラスを先に特定する。

---

## 4. スクリプト構成と読込モデル

フロントエンドはES Modulesではなく、`index.html`から順番に読み込むグローバルスクリプト方式である。

したがって、次の点に注意する。

- 読込順が依存関係そのものになっている。
- 関数・変数の改名は他ファイルからのグローバル参照を確認する。
- 新規ファイル追加時は`index.html`へのscript追加位置が重要。
- `window`公開APIと通常のトップレベル関数が混在している。

大まかな読込順:

```text
日時・状態・Registry・File API
  ↓
Overlay Manager / FieldType / ViewDef Resolver
  ↓
UI補助・Loader・Data Utility
  ↓
Renderer / Field Control / Responsibility
  ↓
VirtualData / Grid / Markdown / Detail
  ↓
Context Contract / Runtime Loader / Action
  ↓
PluginHost / Search State / Toolbar
  ↓
app.js
```

---

## 5. Coreの主要責務

### 5.1 状態管理

`js/core/state.js`

主な状態:

- `viewDef`
- `sourceData`
- `currentRows`
- `filteredRows`
- `selectedIndex`
- 読込中Data / ViewDef名とAPI URL
- 各種キャッシュと既定設定名

単一のグローバル状態を複数モジュールが共有する構成である。状態追加時は、Data再読込・ViewDef切替・検索・詳細保存時のリセット範囲を確認する。

### 5.2 Data / ViewDef読込

主要ファイル:

- `js/core/file_api.js`
- `js/core/loaders.js`
- `js/core/viewdef_resolver.js`

重要な挙動:

- 管理Dataは `/api/data/...` から取得・保存する。
- 管理ViewDefは `/api/defs/...` から取得する。
- Overlayファイルは `overlay/{overlayId}/{relativePath}` というAPI名で扱う。
- DropしたJSONは、管理対象へ登録するか「見るだけ」にするかを画面内ダイアログで選ぶ。
- Overlay Data / ViewDefは原則読み取り専用。
- Data内の`view_def`と`view_def_candidates`がViewDef選択候補を制限する。
- 明示ViewDefは優先されるが、Dataと互換性がない場合はそのまま適用しない。
- ViewDef未指定時はData名やルート配列を使って候補を推定する。

### 5.3 ViewDef継承

`js/core/viewdef_resolver.js`

- `extends`による継承を解決する。
- 配列要素は識別キーを基準にマージする。
- 循環参照を検出する。
- 継承元と継承先のどちらが正本かを意識し、子ViewDefだけを見て判断しない。

### 5.4 FieldType / Value Vocabulary / FieldGroupType

`js/core/field_types.js`

三つのRegistryを解決する。

```text
FieldType Registry
  型、表示、編集の共通定義

Value Vocabulary Registry
  enumRef / valueSet / valueVocabularyRef の選択肢

FieldGroupType Registry
  複数Fieldのグループ定義と動的切替
```

重要事項:

- Core共通語彙は `data/json/config/common_enums_v0_1.json`。
- 古い `00_rules/common_enums...` は互換エイリアスとして扱う。
- Overlayの`value_set_files`も同じ語彙解決系へ統合する。
- Pluginへは可能な限り解決済みの`field.options`を渡す。
- FieldGroupはsource fieldの値によりVariantを切り替え、`visibleWhen`を統合する。

### 5.5 Overlay Manager

`js/core/overlay_manager.js`

- `/api/overlays`でOverlay一覧を取得する。
- `status: active`のmanifestを読み込む。
- manifestに明記されたData、ViewDef、ValueSet、SearchPattern、Plugin Indexだけを登録する。
- Overlayディレクトリを暗黙に全走査しない。

manifestがCoreとOverlay間の契約である。Overlayへファイルを追加するだけではStudioから見えず、対応するmanifest配列への登録が必要。

### 5.6 PluginHost

`js/core/plugin_host.js`

現在の主要拡張点:

- FieldEditor
- SearchFilter
- Action

Pluginは`plugin_index.json`からmanifest、entry scriptの順で読み込まれ、`activate(studio)`で登録する。

Pluginへ渡すStudio APIには、主に次が含まれる。

- sourceData / rows / filteredRows / selectedRow取得
- dot pathの値取得・設定
- 再描画
- Action、FieldEditor、SearchFilter登録
- Toast / Status表示
- 日時・option label/value補助

CoreからPlugin内部のドメインロジックへ依存しない。

---

## 6. 描画と編集

### 6.1 Grid / Document Card

`js/renderers/grid_detail.js`

二つの主表示を持つ。

- 通常グリッド
- Card(Document)表示

主な機能:

- ソート
- 行選択
- 詳細ダイアログ
- Document Cardインライン編集
- 行追加、複製、移動、削除
- CSV出力
- 行コンテキストメニュー

便利機能として、`no`や`message_id / id / key / code / name`を推測する箇所がある。完全宣言型ではないため、汎用化改修時の確認ポイントになる。

### 6.2 Field Control

`js/renderers/field_controls.js`

担当範囲:

- Field値の表示・フォーマット
- 通常入力Control
- Select / Vocabulary options
- 配列表示
- Chat / Message表示
- Inline Markdown
- Header / Search Control
- Plugin FieldEditor連携
- `visibleWhen`
- 失敗行・失敗セルの強調

`objectArray`と`stringArray`は、表示文字列をそのまま保存して壊さないよう、通常Detail Formから除外され、Subgrid側で編集する。

### 6.3 Detail / Subgrid保存

主要ファイル:

- `js/runtime/detail_save.js`
- `js/runtime/detail_subgrid_edit.js`

保存経路は二種類ある。

```text
通常Data
  現在の管理Dataを上書き保存

VirtualData + writeBack
  仮想行のキーから元Data行を探し、指定Fieldを元Dataへ書き戻す
```

Overlay Dataは原則読み取り専用なので、直接上書きではなくSidecarや別の管理Dataを使う設計が基本。

### 6.4 Context Contract

`js/core/viewdef_context_contract.js`

Dataは参照IDを持ち、ViewDefが参照先Data、path、表示Fieldを宣言する。

- Main Context: 画面ヘッダー側の参照文脈
- Target Context: Detail側の対象行文脈

旧`readContract`表現を現在のmain/target contextへ正規化する互換処理もある。

---

## 7. VirtualData

主要ファイル:

- `js/virtualData/virtual_data_registry.js`
- `js/virtualData/relation_builders.js`
- `js/virtualData/expected_builders.js`

ViewDefの`dataSources`を追加読込し、`virtualData`宣言に従って表示用配列を生成する。

主なBuilder:

- `relation_axis_cards`
- `relation_diff_cards`
- `relation_diff_check_cards`
- `expected_check_cross_counts`
- `expected_check_shortage_findings`
- 互換用`constraint_trace_cards`
- `test_pattern_trace_cards`

生成物はsourceDataのトップレベルへ非列挙プロパティとして付与される。JSON保存時にVirtualDataを誤って正本へ混入させないための仕組みである。

---

## 8. 検索とAction

### 8.1 検索

主要ファイル:

- `js/responsibilities/search_filter.js`
- `js/runtime/search_state.js`

Core検索は`contains / equals / gte / lte`を担当し、その後にPlugin SearchFilterを適用する。

検索状態はCoreとPluginをまとめた`ui_state`として保存・復元できる。LocalStorageとOverlay SearchPatternの両方を扱えるが、標準の検索条件保存UIは現在意図的に非表示で、APIブリッジだけ残されている。

### 8.2 Action

主要ファイル:

- `js/actions/action_registry.js`
- `js/actions/action_toolbar.js`

標準Action:

- Load
- Save
- ExportMarkdown
- ExportViewDefMarkdown
- Refresh
- CopyPrompt
- RunCommandProfile
- Noop

`toolbar.executeButton.actionId`により実行Actionを切り替える。Overlay Plugin Actionも同じRegistryへ登録される。

コマンド実行はブラウザから任意コマンドを投げる仕組みではない。Program.cs側のホワイトリスト済みCommand Profileだけを呼び出す。

---

## 9. Markdown

### 9.1 Data / ViewDefからのMarkdown生成

主要ファイル:

- `js/markdown/data_markdown.js`
- `js/markdown/viewdef_markdown.js`
- `js/markdown/markdown_registry.js`

Data Markdownの主なモード:

- `review_report`
- `full_dump`
- `document_rebuild` / `document_sections`

違い:

- review_reportは`markdown.export: false`を尊重する。
- full_dumpは原則すべて出力する。
- document_rebuildは構造化Dataから文書を再構築する。

### 9.2 `mdViewer.html`

約5,900行の独立したMarkdown Viewer / Editor。

主な機能:

- Markdown表示・編集・目次
- Mermaid表示とfallback
- Front Matter編集
- PreviewとRaw間の位置同期
- Table cell / Raw block / 文節単位編集
- コメントSidecar
- 管理Markdown読込・上書き保存
- OS Open/Save Asダイアログ連携
- 保存前Safety検査とLocalStorageバックアップ
- 読み取り専用URL起動

Studio本体とは別の大きなサブシステムとして扱う。Markdown改修時は、本体のMarkdown生成とViewer内編集を混同しない。

---

## 10. その他のViewer

### `DiffJsonViewer.html`

Git Diff等の構造化Diff JSONを読み、Summary、ファイル、Hunk、行単位で表示する。

### `MetaDiff_HypothesisViewer.html`

AI仮説Markdownと根拠差分JSONを同時表示し、根拠カードを検索・絞り込みする。

### `Not_index.html`

公開範囲見直し中の案内画面。Studio本体の`index.html`とは役割が違う。

---

## 11. バックエンドAPIとの境界

Coreが主に利用するAPI:

```text
GET/POST /api/data/...
GET      /api/defs/...
GET/POST /api/markdown/...
GET      /api/overlays
GET      /api/overlays/{overlayId}/...
POST     /api/overlays/{overlayId}/sidecars/...
POST     /api/actions/command/...
```

ファイル名・相対path・拡張子はProgram.cs側でも検証される。フロント側だけを直して保存可能範囲を拡張したつもりにならない。

---

## 12. テストと確認先

Core変更時の主な検証:

```powershell
npx playwright test tests/screen_state/ncjs-screen-state-compare.checks.spec.ts
node --test tests/qa/static/incident_prompt_copy_action_viewdef_static.test.mjs
node --test tests/qa/static/field_group_type_resolver_static.test.mjs
node tests/responsibilities/responsibility_expected_tests.mjs
node tests/responsibilities/responsibility_refactor_first_step_smoke.mjs
```

注意:

- PlaywrightはStudioくんが`localhost:5055`で起動済みである必要がある。
- Screen Stateテストは`data/json/03_tests`配下のActual/Diffを更新する。
- `tests/.runtime`以外へPlaywrightの一時成果物を出さない。
- テスト実行前に、成果物更新を伴うか確認する。

---

## 13. 改修先の判断表

| 改修内容 | 第一候補 |
|---|---|
| 汎用Data/ViewDef読込 | `js/core/loaders.js`, `file_api.js`, `viewdef_resolver.js` |
| 型・語彙・FieldGroup解決 | `js/core/field_types.js` |
| グリッド・カード | `js/renderers/grid_detail.js` |
| Field表示・入力 | `js/renderers/field_controls.js` |
| Detail / Subgrid保存 | `js/runtime/detail_save.js`, `detail_subgrid_edit.js` |
| Context表示 | `js/core/viewdef_context_contract.js` |
| Relation / Expected仮想表示 | `js/virtualData/*` |
| Action | `js/actions/*`またはOverlay Plugin |
| Overlay登録・読込 | `js/core/overlay_manager.js`, `plugin_host.js` |
| Markdown生成 | `js/markdown/*` |
| Markdown Viewer内編集 | `mdViewer.html` |
| ファイル保存/API/OSダイアログ | `Program.cs/Program.cs` |
| FX固有 | `studio_overlays/gpt_fx_lab`。Coreへ入れない |

---

## 14. 現在認識している注意点

1. `.cs`と`.js`は現在Git追跡対象である。古い「git管理外」という文書より、`git ls-files`と現在のGit状態を正とする。
2. グローバルスクリプト方式なので、局所的な関数名変更でも横断影響がある。
3. CoreとOverlayの境界を崩さない。
4. Overlayはmanifest宣言が正本であり、単なるファイル配置では有効にならない。
5. ViewDef変更時はDataの`view_def` / `view_def_candidates`、継承元、FieldType/ValueSet参照も確認する。
6. VirtualDataは表示用派生物であり、Data正本へ無条件に保存しない。
7. Markdown生成ロジックと`mdViewer.html`の編集ロジックは別責務。
8. ブラウザ標準`alert / confirm / prompt`ではなく、Studio画面内ダイアログを使う方針。
9. 保存処理ではUTF-8、人間可読JSON、Sidecar整合性を守る。
10. 実装前に`data/json/00_rules`の該当ルールと変更対象周辺の既存テストを確認する。

---

## 15. 次回作業開始時の最短ルート

1. この文書を読む。
2. `data/json/00_rules`から改修テーマに該当するルールを読む。
3. 変更対象がCoreかOverlayかを決める。
4. 対象Data・ViewDef・Plugin manifest・Program.csの契約を確認する。
5. 関連テストと、テストが更新するEvidenceを確認する。
6. `git status`と対象ファイルの追跡状態を確認してから編集する。

この文書は詳細仕様の正本ではなく、迷子にならないための地図である。実際の挙動については現行ソース、ViewDef、manifest、ルールJSON、テストを優先する。

