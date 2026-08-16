# FRB Studio 標準検索機能 設計概要 v0.1

- 対象: JSON Object Studio / ViewDef Driven UI
- 種別: Design Overview / Search Capability
- 作成日: 2026-08-16
- 状態: 構想・設計整理
- 主題: **Field Definition / ViewDef から標準検索能力を導出し、業務利用にも耐えうる検索の最低ラインを整備する**

---

## 0. この設計の位置づけ

FRB Studio の検索機能を、単純な「文字を含む行を絞り込む機能」から、

**Field の型・Validation Type に応じた標準検索能力を持つ仕組み**

へ育てる。

今回の目的は、検索機能を際限なく高機能化することではない。

今後、

- Definition Driven Testing
- TestPattern の機械導出
- Expected の検証
- 業務データへの応用

へ進むために、Studio が持つべき標準的な検索契約を先に整えることである。

特に、数値・日付に対する範囲検索や、文字列の除外検索、空白／空白以外検索は、業務検索における最低限の実用機能として扱う。

---

# 1. 現状認識

現行 Studio には、すでに検索責務の基礎が存在する。

主な既存構造:

```text
ViewDef / Field
    ↓
renderSearch()
    ↓
Search UI
    ↓
SearchFilter
    ↓
Grid表示対象
```

現行コードでは `renderSearch()` が `gridDef().fields` のうち、

```text
search.visible = true
```

の Field を検索欄へ投影している。

つまり実装思想としてはすでに、

> Search は独立した Field 定義ではなく、Grid / Canonical Field からの Projection

という方向へ寄っている。

一方、一部の ViewDef には現在も `search` Section が存在し、同一 `dataPath`・同一 Field が `search` Section と `grid` Section の双方へ重複定義されている。

これは今後の検索機能拡張において、設定値の不整合・二重管理を生みやすい。

---

# 2. 中核原則

## 2.1 Field 定義は一か所を正本とする

同一 `dataPath` の同一 Field を、検索用・Grid用・Detail用として別々に再定義しない。

```text
Canonical Field Definition
        │
        ├─ grid
        ├─ edit
        └─ search
```

各表示領域は、同一 Field に対する Projection として扱う。

### 原則

> **検索条件は独立した Field 定義ではない。  
> Canonical Field Definition から導出される検索 Projection である。**

---

## 2.2 検索演算子は型から標準導出する

ViewDef に検索演算子を毎回すべて書かせない。

基本は、

```text
Field type
Validation Type
        ↓
Search Capability Resolver
        ↓
標準検索演算子
```

として導出する。

### 原則

> **検索演算子は Field の型・Validation Type から標準導出し、必要な場合だけ ViewDef で Override する。**

---

## 2.3 現在の Studio の構造を壊さない

今回の検索拡張を理由に、

```text
BaseEditor
 ├─ TextEditor
 ├─ NumberEditor
 ├─ DateEditor
 ...
```

のような新しい UI Class 体系へ全面移行しない。

将来的には Field Control 単位の Class 化を検討できるが、現段階では既存の、

```text
Resolver
Renderer
Responsibility
Registry
```

を中心とした Studio の構造を利用する。

---

# 3. 今回「やること」

## 3.1 Search Capability Resolver を追加する

Field Definition から、その Field が標準的に利用できる検索演算子を導出する薄い責務を追加する。

仮称:

```text
SearchCapabilityResolver
```

責務:

```text
入力:
  Field Definition
  Resolved Validation Type

出力:
  利用可能な標準検索演算子
  推奨デフォルト検索モード
```

例:

```text
type = text
    ↓
text_standard

type = number / integer / decimal
    ↓
numeric_standard

type = date / datetime
    ↓
date_standard

type = boolean
    ↓
boolean_standard

type = select
    ↓
select_standard
```

---

# 4. 標準検索演算子

## 4.1 Text

初期標準:

| Operator | 意味 |
|---|---|
| `contains` | 入力文字列を含む |
| `not_contains` | 入力文字列を含まない |
| `equals` | 完全一致 |
| `not_equals` | 完全一致以外 |
| `blank` | 空白 / 未設定 |
| `not_blank` | 空白以外 / 設定済み |

### UIイメージ

```text
Caption

[ 含む ▼ ] [ ABC                           ]
```

```text
Caption

[ 含まない ▼ ] [ ABC                      ]
```

```text
Caption

[ 空白以外 ▼ ]
```

`blank / not_blank` 選択時は値入力欄を不要とする。

---

## 4.2 Number / Integer / Decimal

初期標準:

| Operator | 意味 |
|---|---|
| `equals` | 等しい |
| `not_equals` | 等しくない |
| `gte` | 以上 |
| `lte` | 以下 |
| `between` | 範囲 |
| `blank` | 空白 / 未設定 |
| `not_blank` | 空白以外 / 設定済み |

### 範囲検索

```text
金額

[ 範囲 ▼ ] [ From ] ～ [ To ]
```

基本契約:

```text
Fromのみ入力
  → From以上

Toのみ入力
  → To以下

From / To両方
  → From以上 AND To以下
```

これにより、

- 以上
- 以下
- From ～ To

を同じ範囲UIで自然に扱える。

---

## 4.3 Date / DateTime

初期標準:

| Operator | 意味 |
|---|---|
| `equals` | 同一日 / 同一日時 |
| `not_equals` | 同一値以外 |
| `gte` | 指定値以降 |
| `lte` | 指定値以前 |
| `between` | 期間範囲 |
| `blank` | 未設定 |
| `not_blank` | 設定済み |

### UIイメージ

```text
更新日

[ 範囲 ▼ ] [ 2026-08-01 ] ～ [ 2026-08-31 ]
```

数値と同様、

```text
Fromだけ
  → 以降

Toだけ
  → 以前
```

を許可する。

---

## 4.4 Boolean

初期標準:

```text
equals
```

UI例:

```text
Enabled

[ 指定なし ▼ ]
[ true ]
[ false ]
```

必要に応じて `blank / not_blank` を将来追加可能とする。

---

## 4.5 Select / Enum

初期標準:

```text
equals
not_equals
```

既存の複数選択検索が安全に利用できる場合は、現行互換として維持する。

ただし今回の初期計画では、複雑な集合演算の追加までは行わない。

---

# 5. Validation Type との接続

検索能力の判定は、可能な限り `type` の文字列だけに依存しない。

優先順位の考え方:

```text
Resolved Validation Type
        ↓
Field type
        ↓
安全なfallback
```

例:

```text
view type = text
validation_type = integer
```

の場合、

検索能力としては `numeric_standard` を採用する方向を基本とする。

理由:

> UIの見た目ではなく、値として何者かを基準に検索演算子を決めるため。

これにより、Validation / Runtime Validation / TestPattern / Search が同じ Field 契約から派生できる。

---

# 6. ViewDef の標準形

## 6.1 基本形

通常は以下だけで検索可能とする。

```json
{
  "field": "updated_at",
  "type": "datetime",
  "validation_type": "datetime",
  "grid": {
    "visible": true
  },
  "edit": {
    "visible": true
  },
  "search": {
    "visible": true
  }
}
```

この場合、検索演算子は自動導出する。

```text
datetime
    ↓
equals
not_equals
gte
lte
between
blank
not_blank
```

---

## 6.2 Override

特殊な Field だけ Override を許可する。

例:

```json
{
  "search": {
    "visible": true,
    "operator_set": "date_range"
  }
}
```

または将来的に、

```json
{
  "search": {
    "visible": true,
    "operators": [
      "between",
      "blank",
      "not_blank"
    ]
  }
}
```

を検討可能とする。

ただし初期実装では、自由な Operator 配列をむやみに増やさず、標準 Operator Set を優先する。

---

# 7. Search Section の扱い

## 7.1 新規設計では Field を重複定義しない

以下のような構造は新規ViewDefでは原則作らない。

```text
search Section
 ├─ run_config_id
 ├─ caption
 └─ mode

grid Section
 ├─ run_config_id
 ├─ caption
 └─ mode
```

同じFieldの設定値が2か所に存在すると、

```text
search側
  search.visible = false

grid側
  search.visible = true
```

のような不整合が発生する。

---

## 7.2 Search Section を残す場合の責務

Search Sectionを残す場合でも、Field Definitionの所有者にはしない。

将来的な形:

```json
{
  "id": "search",
  "type": "search",
  "caption": "検索",
  "sourceSection": "grid"
}
```

または、

```json
{
  "id": "search",
  "type": "search",
  "fieldRefs": [
    "run_config_id",
    "caption",
    "updated_at"
  ]
}
```

つまり、

> Search Section は「検索UIをどこへ置くか」を定義する。  
> Fieldそのものの意味は定義しない。

---

## 7.3 既存ViewDef互換

既存ViewDefを一気に全移行しない。

初期対応では、

- 現行ViewDefを壊さない
- `gridDef().fields[].search` をCanonical Search Projectionとして優先
- Legacy Search Sectionは即削除しない
- 新規ViewDef生成ルールから二重Field定義を減らす

という段階移行を採る。

---

# 8. Search UI Renderer

現時点では新しいField Control Class体系を導入しない。

既存 `renderSearch()` / `createInput()` 系の構造を利用しつつ、検索UI生成責務だけを整理する。

イメージ:

```text
renderSearch()
    ↓
SearchCapabilityResolver
    ↓
SearchControlRenderer
    ↓
既存 input / select / date control
```

`SearchControlRenderer` は仮称であり、実装時に既存責務との統合を検討する。

重要なのは、

> Field型ごとの検索UI判断を `renderSearch()` に巨大な if 文として蓄積しないこと。

---

# 9. SearchFilter の拡張

現行 `SearchFilter` はすでに薄い責務として分離されている。

現在存在する主な挙動:

```text
text contains
text equals
number gte
number lte
number equals
boolean equals
multiple value match
full text search
```

これを今回の標準 Operator 語彙へ拡張する。

追加対象:

```text
not_contains
not_equals
between
blank
not_blank
date/datetime comparison
```

---

# 10. 条件の結合

初期段階では、複数Fieldの検索条件は現在と同様、

```text
AND
```

で結合する。

例:

```text
Status = active
AND
UpdatedAt >= 2026-08-01
AND
Caption not_contains "test"
```

---

# 11. 全文検索との関係

既存の全文検索は別責務として維持する。

```text
Field Search
  = Fieldごとの構造化検索

Full Text Search
  = JSON全体からの横断文字検索
```

両者は現在と同じくANDで適用する。

```text
Field Criteria
AND
Full Text Query
```

今回、全文検索のアルゴリズム自体は変更しない。

---

# 12. 今回「やらないこと」

今回の検索標準化では、以下を対象外とする。

## 12.1 UI Class体系の全面リファクタ

やらない:

```text
BaseEditor
TextEditor
NumberEditor
DateEditor
...
```

への全面移行。

理由:

- 現行Studioへの影響が大きい
- 検索機能追加の目的を超える
- 将来、Studioを広く外部展開する段階で再検討する

---

## 12.2 SQL / DB検索エンジン

対象外:

- SQL生成
- DB側WHERE生成
- Server Side Search
- Query Planner
- Index設計

現時点ではStudio内の読み込み済みJSONデータに対する検索を対象とする。

---

## 12.3 複雑な論理式

対象外:

```text
(A OR B) AND (C OR D)
```

などの任意AND/ORグループ。

初期標準:

```text
Field条件 AND Field条件 AND ...
```

---

## 12.4 高度な文字列検索

初期対象外:

- Regex
- fuzzy search
- 類似度検索
- 発音検索
- typo補正
- ranking / relevance score

---

## 12.5 大規模データ検索性能の最適化

初期対象外:

- 数十万～数百万件向けIndex
- Web Worker化
- 仮想検索Index
- 永続検索Index

まず検索契約の正しさを優先する。

性能問題が実利用で発生した場合に別責務として扱う。

---

## 12.6 Search Preset / 保存条件の高度化

検索条件のお気に入り保存、共有、履歴、高度なPreset管理は今回の中心にしない。

既存の検索状態保存・復元契約を壊さないことを優先する。

---

## 12.7 既存ViewDefの一括変換

既存のSearch Section重複定義を今回一括削除しない。

まず、

1. 新しい標準を定義
2. Runtimeを対応
3. 新規ViewDef生成を新標準へ
4. 代表ViewDefで移行検証
5. 既存ViewDefを段階移行

とする。

---

# 13. 検索責務の境界

今回の責務分割イメージ:

```text
Field Definition
      ↓
SearchCapabilityResolver
      │
      ├─ operator set
      └─ default mode
      ↓
Search UI Renderer
      ↓
Search Criteria
      ↓
SearchFilter
      ↓
Filtered Rows
      ↓
Grid Renderer
```

### 責務

#### SearchCapabilityResolver

```text
何が検索可能かを判断する
```

#### Search UI Renderer

```text
検索能力をどう入力UIへ表現するか
```

#### SearchFilter

```text
CriteriaとDataを比較して一致行を返す
```

この3責務を混ぜない。

---

# 14. 将来のField Control Class化に備える境界

今回Class体系へ移行しないが、将来の移行を阻害する実装もしない。

避けるべきこと:

```text
画面コードA
 if type=date...

画面コードB
 if type=date...

画面コードC
 if type=date...
```

Field型固有判断を複数画面へ散らさない。

理想:

```text
SearchCapabilityResolver
Search UI生成境界
```

へ集約しておく。

将来、

```text
Search UI Renderer
        ↓
DateFieldControl
NumberFieldControl
TextFieldControl
```

へ置き換えられる構造を維持する。

---

# 15. TestPatternへの接続

検索標準化が完了すると、Definition Driven Test の対象として非常に扱いやすくなる。

例:

```text
Field Definition
  type = integer
  search.visible = true
```

から、

```text
SearchCapability
  equals
  not_equals
  gte
  lte
  between
  blank
  not_blank
```

を導出できる。

その結果、

```text
TestPattern
  equals
  gte
  lte
  between_from_only
  between_to_only
  between_both
  blank
  not_blank
```

を機械導出できる。

---

## 15.1 Text代表パターン

```text
contains_hit
contains_miss
not_contains_hit
not_contains_excluded
equals
not_equals
blank
not_blank
case_insensitive_contains
```

---

## 15.2 Number代表パターン

```text
equals
not_equals

gte_boundary
gte_below

lte_boundary
lte_above

between_inside
between_min
between_max
between_outside

from_only
to_only

blank
not_blank
```

---

## 15.3 Date代表パターン

```text
equals
not_equals

gte_boundary
lte_boundary

between_inside
between_from
between_to
between_outside

from_only
to_only

blank
not_blank

invalid_date_input
```

---

# 16. 実装フェーズ案

## Phase 1: Search契約定義

- 標準Operator語彙を確定
- Field type / Validation Type → Operator Set対応表を確定
- ViewDef Override契約を確定
- Legacy Search Sectionとの互換方針を確定

---

## Phase 2: SearchCapabilityResolver

- Resolver追加
- 型から標準Operatorを導出
- Validation Type優先順位を実装
- Resolver単体テスト

---

## Phase 3: SearchFilter Operator拡張

追加:

```text
not_contains
not_equals
between
blank
not_blank
date/datetime comparison
```

SearchFilterをDOM非依存の責務として維持する。

---

## Phase 4: Search UI拡張

- Operator選択UI
- `between` のFrom / To
- blank系では値欄非表示
- Number / Date / Textの標準UI
- 現行Search stateとの接続

---

## Phase 5: ViewDef標準化

- 新規ViewDef生成ルール更新
- Search Section二重Field定義を新規生成しない
- 代表ViewDefを新標準へ移行
- Legacy ViewDef互換確認

---

## Phase 6: Definition Driven Test接続

- SearchCapabilityからTestPattern候補を導出
- Expected / Actual / Diffへ接続
- Search Capabilityがテスト証跡として説明可能になることを確認

---

# 17. 初期Acceptance Criteria

最低限、以下が成立した時点で「標準検索 v1」とみなす。

## Text

- 含む
- 含まない
- 完全一致
- 一致以外
- 空白
- 空白以外

## Number

- 等しい
- 等しくない
- 以上
- 以下
- From ～ To
- 空白
- 空白以外

## Date / DateTime

- 等しい
- 等しくない
- 以降
- 以前
- From ～ To
- 空白
- 空白以外

## 共通

- 複数Field条件はAND
- Full Text SearchとのANDが維持される
- ViewDefのField定義を検索用に二重作成しなくてよい
- 型から標準検索能力が導出される
- ViewDef Overrideが可能
- SearchFilterはDOMから独立した責務としてテスト可能
- 現行StudioのGrid / Detail / Validation体系を壊さない

---

# 18. 設計上の「やる / やらない」まとめ

| 項目 | 今回 |
|---|---|
| Text contains | やる |
| Text not_contains | やる |
| Text equals / not_equals | やる |
| blank / not_blank | やる |
| Number >= / <= | やる |
| Number From-To | やる |
| Date >= / <= | やる |
| Date From-To | やる |
| Validation TypeからOperator導出 | やる |
| ViewDef Override | やる |
| Search Sectionの二重Field定義を新規標準から外す | やる |
| 現行SearchFilter責務の拡張 | やる |
| Definition Driven Testへの接続準備 | やる |
| UI Editor Class体系の全面変更 | やらない |
| SQL / DB検索 | やらない |
| 任意AND/OR式 | やらない |
| Regex / fuzzy / AI検索 | やらない |
| 大量データ向けIndex | やらない |
| 既存ViewDef全件一括移行 | やらない |

---

# 19. この設計で目指す状態

```text
Field Definition
      │
      ├─ Validation
      ├─ Runtime Editor
      ├─ Grid
      ├─ Detail
      ├─ Search Capability
      └─ TestPattern
```

検索だけが特別な別世界ではなく、

**同じField Definitionから派生する能力の一つ**

として扱う。

最終的に目指す構造:

```text
Field Definition
        ↓
Capability Resolution
        ↓
┌───────────────┬────────────────┬────────────────┐
│ Validation    │ Search         │ TestPattern    │
│ Capability    │ Capability     │ Capability     │
└───────────────┴────────────────┴────────────────┘
        ↓
Renderer / Validator / Runner
```

---

# 20. 今回の設計判断

今回の検索強化は、単なるUI便利機能追加ではない。

Studio が将来、

```text
JSON編集ツール
    ↓
Definition Driven Studio
    ↓
業務データも扱える汎用Studio
```

へ広がれるための基礎能力として位置づける。

一方で、現在のStudioに対して過剰なClass再設計や巨大リファクタは行わない。

> **今の構造に沿って小さく検索能力を追加し、  
> 将来の大規模リファクタを邪魔しない境界を作る。**

これを今回の実装判断軸とする。
