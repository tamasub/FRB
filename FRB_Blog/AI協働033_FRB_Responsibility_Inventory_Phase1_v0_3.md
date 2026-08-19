# 責務棚卸し Phase 1 — 既存責務を「今の粒度のまま」並べる

作成日: 2026-08-19  
ステータス: Draft / Phase 1  
対象: FRB Studio / AI承認駆動開発  
目的: 責務の粒度標準化・Behavior Pattern化・TestPattern / Expected自動生成を検討する前段として、既存責務を現在の粒度のまま棚卸しする。

---

## 0. 今回の研究目的

最終的に目指すのは、次の状態である。

```text
人間が少数の意味あるキーワードを承認
        ↓
標準Behavior / Optionを解決
        ↓
TestPatternをプログラム生成
        ↓
Expectedをプログラム生成
        ↓
Actual
        ↓
Diff
        ↓
人間承認
```

今回のPhase 1では、まだこの共通化を行わない。

まず、

> **現在、Studioくんの中で「責務」として何を、どの粒度で切っているか**

をそのまま見える状態にする。

---

## 1. Phase 1でやること

既存責務について、以下を可能な限りそのまま収集する。

- `responsibility_cd`
- `name`
- `test_level`
- `summary`
- `purpose`
- `source_file`
- `interface_name`
- `in_scope`
- `out_of_scope`
- `constraint_ids`
- `guarantees`
- 既存テスト
- 備考

### このPhaseではやらないこと

以下はPhase 2以降で行う。

- 責務名の統合
- 責務粒度の変更
- SAVE / LOAD / RESET 等への標準Pattern化
- GuaranteeのBehavior Pattern化
- TestPatternの自動生成
- Expectedの自動生成
- JSON Schemaの確定
- Runtime実装
- Test Runner実装

**Phase 1では「今あるものを、そのまま並べる」。**

---

## 2. 棚卸し時の重要ルール

### Rule 1 — 先に抽象化しない

たとえば既存責務が、

```text
grid_column_build
```

なら、そのまま記録する。

この段階で、

```text
FILTER
BUILD
PROJECTION
```

などへ置き換えない。

---

### Rule 2 — 粒度が変でも直さない

Phase 1の目的は、責務粒度の現状把握である。

```text
責務Aは細かすぎる
責務Bは大きすぎる
責務CとDはほぼ同じ
```

と思っても、まずそのまま記録する。

違和感は `phase1_notes` に残す。

---

### Rule 3 — Guaranteeも原文を優先する

Guaranteeについても、先に共通Behaviorへ変換しない。

```text
visible=falseを除外する
入力順を維持する
空入力でも例外停止しない
入力を変更しない
```

など、現在定義されている意味をそのまま保持する。

---

### Rule 4 — 「機械生成できそう」はまだ判定しない

Phase 1では、

```text
このGuaranteeはNO_MUTATIONにできそう
この責務はRESET Patternになりそう
```

といった判断は確定しない。

気づいた場合はメモだけ残す。

---

## 3. 責務一覧

Phase 1完了時には、まずこの一覧を埋める。

> 抽出方針:
> - **JSON Object Studio** は、既存の Responsibility Master / ResponsibilityDef Draft を優先して採用する。
> - **Markdown Studio / Diff JSON / MetaDiff** は、現時点で責務JSONとして明示定義されていないものが多いため、実装上の関数境界から「責務候補」として拾う。
> - Phase 1では責務粒度の統合・分割・Behavior Pattern化は行わない。
> - `Guarantee数=未定義` は「保証が存在しない」ではなく、現時点で責務定義JSONとしてGuarantee配列が定義されていないことを示す。

| No | responsibility_cd | 責務名 | Test Level | Source / Interface | Guarantee数 | 既存Test | Phase1 Notes |
|---:|---|---|---|---|---:|---|---|
| 1 | `grid_column_build` | Grid列生成責務 | UT | `wwwroot/js/responsibilities/grid_column_builder.js` / `GridColumnBuilder.build` | 5 | あり | **[JSON] 既存責務定義**。Responsibility Master登録済み。 |
| 2 | `search_filter` | 検索条件評価責務 | UT | `wwwroot/js/responsibilities/search_filter.js` / `SearchFilter.apply` | 8 | あり | **[JSON] 既存責務定義**。Expected Test 4件＋Smoke/検索Operator系Testあり。 |
| 3 | `csv_export` | CSV出力責務 | UT | `wwwroot/js/responsibilities/csv_exporter.js` / `CsvExporter.resolveFields / CsvExporter.export` | 6 | あり | **[JSON] 既存責務定義**。Expected Test 2件＋Smokeあり。 |
| 4 | `grid_aggregate` | Grid数値集計責務 | UT | `wwwroot/js/responsibilities/grid_aggregator.js` / `GridAggregator.build` | 6 | あり | **[JSON] 既存責務定義**。Responsibility Smokeで集計・非数値除外等を確認。 |
| 5 | `viewdef_parse` | ViewDef解釈責務 | UT | ResponsibilityDef Draft / `ViewDefParser.parse` | 未定義 | 専用Test未確認 | **[JSON] 既存Draft責務**。Active ViewDefを後続責務向けに解釈する契約として定義済み。 |
| 6 | `editor_field_build` | Editor項目生成責務 | UT | ResponsibilityDef Draft / `EditorFieldBuilder.build` | 未定義 | 専用Test未確認 | **[JSON] 既存Draft責務**。ViewDef fieldsからEditor項目定義を生成する契約。 |
| 7 | `search_state` | 検索状態管理責務 | UT/CT | `wwwroot/js/runtime/search_state.js` / Draft `SearchStateManager.update` | 未定義 | 関連Testあり | **[JSON] 既存Draft責務**。検索条件・結果・現在行・UI stateの管理境界。 |
| 8 | `renderer_display` | Renderer表示責務 | UT/CT | ResponsibilityDef Draft / `Renderer.render` | 未定義 | 専用Test未確認 | **[JSON] 既存Draft責務**。判断済みViewModel/StateをDOMへ反映する責務として定義済み。 |
| 9 | `markdown_document_load` | Markdown文書読込責務 | 未定義 | `wwwroot/mdViewer.html` / `loadWorkspaceMarkdown / loadManagedMarkdown / loadLocalFile / loadMarkdown` | 未定義 | 関連静的Testあり | **[Markdown] 実装から抽出候補**。Workspace / managed / externalの読込経路が存在。仮CD。 |
| 10 | `markdown_document_save` | Markdown文書保存責務 | 未定義 | `wwwroot/mdViewer.html` / `saveWorkspaceMarkdown / saveManagedMarkdown / saveMarkdownWithNativeDialog` | 未定義 | 関連静的Testあり | **[Markdown] 実装から抽出候補**。Front Matter materialize・Save Safetyを経由して保存。仮CD。 |
| 11 | `markdown_mode_transition` | Markdownモード遷移責務 | 未定義 | `wwwroot/mdViewer.html` / `setMarkdownMode` | 未定義 | 関連静的Testあり | **[Markdown] 実装から抽出候補**。Viewer / Editor / Review切替とReadOnly・表示状態を管理。仮CD。 |
| 12 | `markdown_review_session` | Markdown Review開始・再開責務 | 未定義 | `wwwroot/mdViewer.html` / `openExistingMarkdownReviewMode / startNewMarkdownReview` | 未定義 | 関連静的Testあり | **[Markdown] 実装から抽出候補**。既存Review再開とNEW Review開始が独立関数として存在。仮CD。 |
| 13 | `markdown_review_sidecar` | Markdown Review JSON永続化責務 | 未定義 | `wwwroot/mdViewer.html` / `saveMarkdownCommentSidecar / persistMarkdownCommentReviewMutation` | 未定義 | 関連静的Testあり | **[Markdown] 実装から抽出候補**。コメント・判定・ハイライトをReview JSONへ保持。仮CD。 |
| 14 | `diff_json_load` | Diff JSON読込責務 | 未定義 | `wwwroot/DiffJsonViewer.html` / `loadJsonFile / loadJsonUrl / applyDiffJson` | 未定義 | 関連静的Testあり | **[Diff JSON] 実装から抽出候補**。File/URL読込後に正規化・初期選択・各View更新を実施。仮CD。 |
| 15 | `diff_file_filter` | Diff対象ファイル抽出責務 | 未定義 | `wwwroot/DiffJsonViewer.html` / `fileMatches / renderFileList` | 未定義 | UI静的確認あり | **[Diff JSON] 実装から抽出候補**。左側検索語＋Statusで対象ファイルを抽出。仮CD。 |
| 16 | `diff_detail_filter` | 選択ファイル内差分抽出責務 | 未定義 | `wwwroot/DiffJsonViewer.html` / `hunkMatches / lineTypeMatches / renderDetail` | 未定義 | UI静的確認あり | **[Diff JSON] 実装から抽出候補**。選択範囲・検索語・行種別でDifference detailsを抽出。仮CD。 |
| 17 | `diff_json_save_as` | Diff JSON別名保存責務 | 未定義 | `wwwroot/DiffJsonViewer.html` / `saveDiffJsonAs` | 未定義 | あり | **[Diff JSON] 実装から抽出候補**。Native Save Asを優先し、利用不可時はbrowser downloadへfallback。仮CD。 |
| 18 | `metadiff_markdown_load` | MetaDiff Markdown読込責務 | 未定義 | `wwwroot/MetaDiff_HypothesisViewer.html` / `loadMarkdownFile` | 未定義 | 専用Test未確認 | **[MetaDiff] 実装から抽出候補**。Markdown Preview生成と埋込JSON抽出の起点。仮CD。 |
| 19 | `metadiff_evidence_extract` | MetaDiff根拠JSON抽出・正規化責務 | 未定義 | `wwwroot/MetaDiff_HypothesisViewer.html` / `extractJsonBlocks / normalizeEvidence` | 未定義 | 専用Test未確認 | **[MetaDiff] 実装から抽出候補**。`json` / `diff_hypothesis.json` blockを抽出しEvidence行へ正規化。仮CD。 |
| 20 | `metadiff_evidence_filter` | MetaDiff根拠差分絞り込み責務 | 未定義 | `wwwroot/MetaDiff_HypothesisViewer.html` / `rowMatches / renderEvidence` | 未定義 | 専用Test未確認 | **[MetaDiff] 実装から抽出候補**。検索語・ファイル・カテゴリ・Evidence ID focusをAND評価。仮CD。 |

### Phase 1 一覧時点のメモ

```text
JSON Object Studio
  既にResponsibility Master / ResponsibilityDef Draftが存在する。
  → 既存定義を起点にできる。

Markdown Studio
  責務JSONとしての明示定義は未確認。
  ただし Load / Save / Mode / Review / Review JSON persistence は
  関数境界と静的テストから比較的はっきり拾える。

Diff JSON
  Load / 左ファイル抽出 / 選択ファイル内差分抽出 / Save As が
  独立した操作・関数境界として拾える。

MetaDiff
  Markdown Load / Embedded JSON Extraction+Normalization /
  Evidence Filter が実装上のまとまりとして拾える。
```

**この段階では、上記20件を同じ粒度だとはみなさない。**

Phase 2で初めて、

```text
大きすぎる責務
小さすぎる責務
他画面と同じ構造を持つ責務
複数Guaranteeへ分解できる責務
```

を横断比較する。

---

# 4. 責務詳細

## 4.1 `grid_column_build` — Grid列生成責務

### 基本情報

```yaml
responsibility_cd: grid_column_build
name: Grid列生成責務
test_level: UT
approval_status: draft
enabled: true
source_file: wwwroot/js/responsibilities/grid_column_builder.js
interface_name: GridColumnBuilder.build
```

### Summary

`grid.visible=false` を除外し、ViewDef上の列順を維持したGrid列配列を返す。

### Purpose

ViewDefのfields定義から、Grid表示に利用する列配列を確定する。

### In Scope

- `grid.visible` の解釈
- 表示列の抽出
- 列順の維持
- 呼出側 `includeField` 方針の適用

### Out of Scope

- DOM描画
- 列幅計算
- Gridイベント処理
- CSV出力

### Constraints

- `constitution_11`
- `constitution_12`

### Guarantees

#### `grid_column_build_g001`

概要：非表示指定された項目をGrid列へ含めないことを保証する。

- guarantee_type: `rule`
- condition: fieldsに`grid.visible=false`の項目が含まれる場合
- guarantee: 当該項目をGrid列へ含めない。
- observable_result: 返却列のfield一覧に非表示項目が存在しない。
- expected_def_type: `RuleExpectedDef`
- test_pattern_seed: `visible=false除外パターン`
- priority: high

#### `grid_column_build_g002`

概要：表示対象フィールドの列順がViewDefの定義順を維持することを保証する。

- guarantee_type: `state`
- condition: 表示対象フィールドが複数ある場合
- guarantee: 返却列の順序はViewDef fieldsの順序を維持する。
- observable_result: 返却field一覧が入力順と一致する。
- expected_def_type: `StateExpectedDef`
- test_pattern_seed: `表示列の順序維持パターン`
- priority: medium

#### `grid_column_build_g003`

概要：fieldsが未指定または空でも安全に空配列を返すことを保証する。

- guarantee_type: `rule`
- condition: fieldsが未指定または空配列の場合
- guarantee: 例外で停止せず空配列を返す。
- observable_result: 返却値が空配列である。
- expected_def_type: `RuleExpectedDef`
- test_pattern_seed: `fields未指定安全パターン`
- priority: medium

#### `grid_column_build_g004`

概要：呼出側から指定されたincludeField方針に従って列を採用することを保証する。

- guarantee_type: `interface`
- condition: includeField方針が呼出側から指定された場合
- guarantee: 指定された方針による列採用結果を返す。
- observable_result: includeFieldの判定結果と返却列が一致する。
- expected_def_type: `InterfaceExpectedDef`
- test_pattern_seed: `カスタムincludeField適用パターン`
- priority: medium

#### `grid_column_build_g005`

概要：Grid列生成によって入力されたfields定義を変更しないことを保証する。

- guarantee_type: `no_side_effect`
- condition: Grid列を生成した場合
- guarantee: 入力されたfields定義を変更しない。
- observable_result: 処理前後のfieldsが同一である。
- expected_def_type: `StateExpectedDef`
- test_pattern_seed: `ViewDef fields非破壊パターン`
- priority: medium

### 既存テスト

- `grid_column_build_visible_fields_basic`
- `grid_column_build_empty_fields_safe`

### Phase 1 Notes

現時点では責務・Guaranteeともに変更しない。

Phase 2では、このGuarantee群について、

```text
他責務にも同じGuarantee構造が存在するか？
同じ意味を持つGuaranteeを共通Behaviorとして扱えるか？
```

を横断比較する予定。

---

# 5. 追加責務記入テンプレート

以下を責務ごとにコピーして使用する。

## X.X `<responsibility_cd>` — `<責務名>`

### 基本情報

```yaml
responsibility_cd:
name:
test_level:
approval_status:
enabled:
source_file:
interface_name:
```

### Summary

-

### Purpose

-

### In Scope

- 

### Out of Scope

- 

### Constraints

- 

### Guarantees

#### `<guarantee_id>`

- guarantee_type:
- condition:
- guarantee:
- observable_result:
- expected_def_type:
- test_pattern_seed:
- priority:
- enabled:

### 既存テスト

- 

### Phase 1 Notes

- 粒度に関する違和感:
- 他責務との類似:
- 保証の重複候補:
- その他:

---

# 6. Phase 1 完了条件

次を満たしたらPhase 1完了とする。

- 主要な既存責務が一覧化されている
- 各責務の現在の粒度が保持されている
- 各責務のGuaranteeが可能な範囲で収集されている
- Source / Interfaceが追跡可能になっている
- 既存Testとの対応が確認できる
- 共通化・Pattern化はまだ実施していない
- 粒度や重複への違和感だけがNotesとして残っている

---

# 7. Phase 2への引継ぎ

Phase 2では、Phase 1で集めたGuaranteeを横断して比較する。

想定する流れ:

```text
既存Responsibility
        ↓
Guaranteeを横断比較
        ↓
同じ意味を持つGuaranteeを発見
        ↓
Behavior Pattern候補
        ↓
TestPattern生成可能性を評価
        ↓
Expected生成可能性を評価
```

Phase 2の主要な問いは次の一つとする。

> **このBehaviorキーワードを人間が1つ承認すると、何個のTestPattern + Expectedを安全にプログラム生成できるか？**

---

## 現時点の研究上の仮説

```text
Responsibility
  = 1つのExpectedではない

Responsibility
  ↓
複数Guarantee
  ↓
複数TestPattern
  ↓
TestPatternごとのExpected
```

さらに将来的には、

```text
具体Responsibility
        ↓
複数Behavior Pattern
        ↓
各Behavior Patternから
TestPattern + Expectedをプログラム生成
```

という構造へ昇格できる可能性がある。

ただし、この仮説を先に既存責務へ押し付けない。

**まずPhase 1では、現物を見る。**
