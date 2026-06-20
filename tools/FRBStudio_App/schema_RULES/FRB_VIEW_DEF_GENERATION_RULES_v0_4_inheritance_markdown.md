# FRB Studio View Definition Generation Rules

対象: `FRBStudio_App` / No-Code JSON Studio v0.4.1+ 系

この文書は、AI が新しいデータ JSON から `view_def.json` を生成するための作成ルールである。

## 0. v0.4追加方針（継承・Markdown・レポート）

この版では、ViewDefを単なる画面定義ではなく、以下の3つを扱う定義として拡張する。

```text
画面でどう見るか
Markdownでどう読むか
継承差分をどう理解するか
```

追加された主な考え方は以下である。

- `extends` による ViewDef 継承。
- `markdown.type` は **データJSONのMarkdown出力用** として扱う。
- `ViewDef Markdown→Viewer` は ViewDef定義そのものを読むための固定レポートであり、`markdown.type` とは別系統とする。
- 画面用の `grid.visible` / `edit.visible` と、Markdown出力用の `markdown.sections` は分離する。
- 継承表示ラベルは、人間が見る caption では **【BASE】/【CHILD】** を使う。

---

---

## 1. 現行アプリの前提

現行アプリは **1画面1グリッド** を前提とする。

画面構成は固定で、以下の構造を持つ。

```text
Header Form
↓
Search Form
↓
Grid
↓
Detail Dialog
```

そのため、`view_def.json` では基本的に以下を定義する。

- 画面情報
- Header 用 form section
- Main Grid 用 grid section
- 各 field の表示・編集・検索ルール

---

## 2. トップレベル構造

```json
{
  "app": {
    "name": "No-Code JSON Studio",
    "version": "0.2-draft"
  },
  "views": [
    {
      "id": "example_main",
      "caption": "Example Viewer / Light Editor",
      "layout": "header-search-grid-detail",
      "sections": []
    }
  ]
}
```

### app

| key | 必須 | 説明 |
|---|---:|---|
| name | 任意 | アプリ名。現行では表示には強く依存しない |
| version | 任意 | 定義バージョン |

### views

現行アプリでは `views[0]` のみ使用する。

| key | 必須 | 説明 |
|---|---:|---|
| id | 推奨 | View ID |
| caption | 推奨 | 画面名 |
| layout | 推奨 | 現行では `header-search-grid-detail` 固定 |
| sections | 必須 | section 配列 |

---

## 3. Section 定義

section には `form` と `grid` がある。

### 3.1 form section

Header Form として使われる。

```json
{
  "id": "header",
  "caption": "基本情報",
  "type": "form",
  "dataPath": "$",
  "fields": []
}
```

現行アプリでは、最初に見つかった `type: "form"` かつ `role !== "detailOnly"` の section が Header Form になる。

| key | 必須 | 説明 |
|---|---:|---|
| id | 推奨 | section ID |
| caption | 推奨 | Header 表示名 |
| type | 必須 | `form` |
| dataPath | 必須 | データ JSON 上の参照位置。ルートは `$` |
| fields | 必須 | field 配列 |

### 3.2 grid section

Main Grid として使われる。

```json
{
  "id": "items",
  "caption": "一覧",
  "type": "grid",
  "dataPath": "$.items",
  "keyField": "id",
  "fields": []
}
```

現行アプリでは、最初に見つかった `type: "grid"` の section が Main Grid になる。

| key | 必須 | 説明 |
|---|---:|---|
| id | 推奨 | section ID |
| caption | 推奨 | Grid 表示名 |
| type | 必須 | `grid` |
| dataPath | 必須 | 配列への JSON パス。必ず Array を指すこと |
| keyField | 任意 | 行識別用。現行アプリでは主に設計メモ用途 |
| fields | 必須 | field 配列 |

---

## 4. dataPath / field パスのルール

現行アプリのパスは簡易 dot path である。

使用可能:

```text
$
$.items
$.experiment.memo
views.0.caption
```

注意:

- `$.` で始まるパスはルートから参照する。
- `field` は section の `dataPath` からの相対パスとして扱われる。
- 配列添字は `views.0.caption` のように dot で書く。
- `items[0].name` のような bracket 記法は使わない。
- キー名に `.` を含む JSON は避ける。

例:

```json
{
  "type": "form",
  "dataPath": "$",
  "fields": [
    { "field": "experiment.memo", "caption": "実験メモ", "type": "textarea" }
  ]
}
```

これは `sourceData.experiment.memo` を編集する。

---

## 5. Field 定義

```json
{
  "field": "name",
  "caption": "名前",
  "type": "text",
  "readonly": false,
  "grid": {
    "visible": true,
    "width": 160
  },
  "edit": {
    "visible": true,
    "readonly": false
  },
  "search": {
    "visible": true,
    "operator": "contains"
  },
  "defaultValue": ""
}
```

| key | 必須 | 説明 |
|---|---:|---|
| field | 必須 | データ項目パス |
| caption | 推奨 | 表示名 |
| type | 必須 | field type |
| readonly | 任意 | Header/Detail 編集不可 |
| grid | 任意 | Grid 表示設定 |
| edit | 任意 | Header/Detail 表示・編集設定 |
| search | 任意 | Search Form 表示設定 |
| options | `select`時推奨 | 選択肢 |
| format | 任意 | number 表示フォーマット |
| defaultValue | 任意 | 新規行追加時の初期値 |
| create | 任意 | 新規行作成時の制御 |

---

## 6. Field type 一覧

現行アプリで扱える type は以下。

| type | 入力UI | 保存時の型 | 主な用途 |
|---|---|---|---|
| text | input text | string | 通常文字列 |
| number | input number | number / null | 数値 |
| boolean | select true/false | boolean | 真偽値 |
| select | select | string | 固定候補 |
| datetime | input text | string | 日時文字列 |
| textarea | textarea | string | 長文 |
| objectArray | input text + child table表示 | stringに変換される可能性あり | 配列の閲覧向け。編集は原則 readonly 推奨 |
| stringArray | input text + child table表示 | stringに変換される可能性あり | 配列の閲覧向け。編集は原則 readonly 推奨 |

### 重要注意

`objectArray` / `stringArray` は詳細画面下部に子テーブルとして表示される。
ただし現行アプリでは、通常入力欄にも `N items` と表示されるため、編集可能にすると配列が文字列化される危険がある。

そのため、配列項目は以下を推奨する。

```json
{
  "field": "children",
  "caption": "子要素",
  "type": "objectArray",
  "grid": { "visible": false },
  "edit": { "visible": true, "readonly": true },
  "readonly": true,
  "defaultValue": []
}
```

---

## 7. grid 設定

```json
"grid": {
  "visible": true,
  "width": 120,
  "format": "#.000"
}
```

| key | 説明 |
|---|---|
| visible | `false` のとき Grid に表示しない。未指定なら表示される |
| width | 列幅 px |
| format | number 表示フォーマット |

### AI生成ルール

- 一覧で見たい主要項目は `grid.visible: true`
- 長文・配列・内部管理項目は `grid.visible: false`
- 文字列は 120〜220 px
- 数値は 80〜120 px
- 日時は 160〜190 px

---

## 8. edit 設定

```json
"edit": {
  "visible": true,
  "readonly": false,
  "height": 90,
  "step": "0.001",
  "min": 0,
  "max": 100
}
```

| key | 説明 |
|---|---|
| visible | `false` のとき Detail/Header に表示しない。未指定なら表示される |
| readonly | true のとき編集不可 |
| height | textarea の最小高さ px |
| step | number input の step |
| min | number input の min |
| max | number input の max |

---

## 9. search 設定

```json
"search": {
  "visible": true,
  "operator": "contains"
}
```

| operator | 対象 | 説明 |
|---|---|---|
| contains | text / textarea / datetime | 部分一致 |
| equals | text / select / boolean / number | 完全一致 |
| gte | number | 以上 |
| lte | number | 以下 |

### 既定動作

- number は未指定時 `gte`
- number 以外は未指定時 `contains`

### AI生成ルール

- ID・名前・メモ → `contains`
- select / boolean → `equals`
- 数値 → `gte`
- 全項目を検索に出さない。主要項目だけにする。

---

## 10. defaultValue / create

新規行追加時、grid section の `fields` から行オブジェクトが生成される。

### defaultValue がある場合

`defaultValue` がそのまま初期値になる。

### defaultValue がない場合

| type | 既定値 |
|---|---|
| number | 0 |
| boolean | false |
| objectArray | [] |
| stringArray | [] |
| select | options[0] または空文字 |
| その他 | 空文字 |

### create.include

```json
"create": { "include": false }
```

この指定がある field は、新規行作成時に生成対象から外れる。

---

## 11. validation

既存 view_def には `validation.required` が登場するが、現行アプリ側では未実装に近い。

```json
"validation": {
  "required": true
}
```

現時点では将来用メタ情報として扱う。
AIは重要項目に付けてもよいが、アプリで入力チェックされる前提にはしないこと。

---

## 12. AIによる view_def 生成ルール

新しいデータ JSON から view_def を作るときは、以下の手順に従う。

### Step 1. ルート直下を確認する

- ルート直下のスカラー値や小さな object は Header Form 候補
- ルート直下の配列は Main Grid 候補
- `view_def` は管理項目なので Header に出す場合は readonly 推奨

### Step 2. Main Grid 配列を1つ選ぶ

現行アプリは 1画面1グリッドのため、編集したい主配列を1つ選ぶ。

候補例:

- `items`
- `rows`
- `metrics`
- `scores`
- `notes`
- `tsBuf`
- `views.0.sections.1.fields`

### Step 3. Header section を作る

配列以外のメタ情報を Header に置く。

例:

```json
{
  "id": "header",
  "caption": "基本情報",
  "type": "form",
  "dataPath": "$",
  "fields": []
}
```

### Step 4. Grid section を作る

主配列を `dataPath` に指定する。

例:

```json
{
  "id": "items",
  "caption": "items",
  "type": "grid",
  "dataPath": "$.items",
  "keyField": "id",
  "fields": []
}
```

### Step 5. field type を推定する

| データ値 | 推奨 type |
|---|---|
| string | text |
| 長い string | textarea |
| ISO日時風 string | datetime |
| number | number |
| boolean | boolean |
| 少数の固定候補らしい string | select |
| string[] | stringArray |
| object[] | objectArray |
| object | 原則 flatten して `a.b` として field 化 |

### Step 6. select の options を作る

同じ field に現れる値の種類が少ない場合、`select` にして `options` を列挙する。

目安:

- ユニーク値が 2〜10 個
- 状態・区分・種別・type・operator などの項目名

### Step 7. 編集危険項目を readonly にする

以下は readonly 推奨。

- 自動生成 ID
- 保存日時
- 計測ログの時刻
- 配列項目 objectArray / stringArray
- 仕様上壊すと危険な構造項目

---

## 13. 最小テンプレート

```json
{
  "app": {
    "name": "No-Code JSON Studio",
    "version": "0.2-draft"
  },
  "views": [
    {
      "id": "example_main",
      "caption": "Example Editor",
      "layout": "header-search-grid-detail",
      "sections": [
        {
          "id": "header",
          "caption": "基本情報",
          "type": "form",
          "dataPath": "$",
          "fields": []
        },
        {
          "id": "items",
          "caption": "一覧",
          "type": "grid",
          "dataPath": "$.items",
          "keyField": "id",
          "fields": []
        }
      ]
    }
  ]
}
```

---

## 14. 現行制約まとめ

- 現行は 1画面1グリッド。
- `views[0]` のみ使用。
- `form` は Header 用。
- `grid` は Main Grid 用。
- `dataPath` は dot path。
- `objectArray` / `stringArray` は閲覧向け。編集可にしない方が安全。
- `validation` は将来用メタ情報。
- 画面定義 JSON 自体も、このルールに従ってメンテ対象にできる。



---

## 15. Field type: chat（v0.4-draft）

`chat` は、JSON上の複数フィールドを会話タイムラインとして表示するための特殊な Field Type である。

No-Code JSON Studio 本体は汎用ツールのまま、AIレビュー・設計レビュー・実験ログなどを「会話として読める」表示にするために使う。

### 15.1 目的

通常の Form 表示では、以下のようなレビュー履歴が単なる入力欄の羅列になる。

```text
制約本文
俺コメント
AI回答
俺追加回答
AI再回答
```

`chat` を使うと、これを左右の吹き出しレイアウトとして表示できる。

```text
制約本文
↓
User: 俺コメント
AI:   AI回答
User: 俺追加回答
AI:   AI再回答
```

### 15.2 データ構造

現行実装では、会話そのものを `discussion[]` に移行しなくてもよい。
既存の複数フィールドを `edit.messages` で束ねて表示する。

```json
{
  "field": "__review_chat",
  "caption": "制約レビュー会話",
  "type": "chat",
  "grid": { "visible": false },
  "edit": {
    "visible": true,
    "messages": [
      { "role": "constraint", "field": "statement", "label": "制約本文", "readonly": true },
      { "role": "user", "field": "user_comment", "label": "俺コメント" },
      { "role": "ai", "field": "ai_response", "label": "AI回答", "readonly": true },
      { "role": "user", "field": "user_reply", "label": "俺追加回答" },
      { "role": "ai", "field": "ai_followup_response", "label": "AI再回答", "readonly": true }
    ]
  },
  "create": { "include": false }
}
```

### 15.3 表示ルール

- `role: user` は左側に表示する。
- `role: ai` は右側に表示する。
- `role: constraint` は会話の起点として中央・全幅寄りに表示する。
- `readonly: true` のメッセージは編集不可とする。
- 入力された内容は、`messages[].field` で指定した元フィールドへ保存する。

### 15.4 AI生成ルール

AIレビューや制約レビュー用の view_def を作る場合、以下のような項目があれば `chat` 表示を推奨する。

- `statement`
- `user_comment`
- `ai_response`
- `user_reply`
- `ai_followup_response`

ただし、Grid検索や一覧確認のため、元フィールド自体は消さず、必要に応じて `edit.visible: false` にして chat に集約する。


---

## 16. Detail Dialog 配置制御: `layout.placement`（v0.5-draft）

Detail Dialog内で、通常フォーム・子配列表示・会話欄の順番を制御したい場合、fieldに `layout.placement` を指定できる。

### 16.1 目的

レビュー画面では、まずレビュー対象を読み、その後に個別明細を確認し、最後にコメントする流れが自然である。

```text
通常フォーム / レビュー対象
↓
objectArray / stringArray の子テーブル
↓
会話・コメント欄
```

このため、会話欄などを子テーブルより後ろに表示したい場合は `detailFooter` を使う。

### 16.2 指定例

```json
{
  "field": "__group_chat",
  "caption": "制約グループ会話",
  "type": "chat",
  "layout": {
    "placement": "detailFooter",
    "order": 900
  },
  "grid": { "visible": false },
  "edit": {
    "visible": true,
    "messages": []
  },
  "create": { "include": false }
}
```

### 16.3 AI生成ルール

- レビュー対象カードは通常位置に置く。
- objectArray / stringArray は子テーブルとして表示する。
- コメント欄・会話欄・レビュー後に入力する項目は `layout.placement: "detailFooter"` を指定する。
- caption名で表示順を判定しない。役割を `layout.placement` に明示する。


---

## 17. ViewDef継承: `extends`（v0.4-draft）

ViewDefは、他のViewDefを継承できる。
目的は、同じデータJSONに対して、差分だけで別の観察モードを作ることである。

```text
同じデータJSON
↓
親BASE ViewDef
↓ extends
子CHILD ViewDef
↓
Summary View / Failure Focus View / Peak Focus View など
```

### 17.1 基本形

```json
{
  "extends": "screen_state_diff_view_def_base_v0_2_checks.json",
  "views": [
    {
      "id": "screen_state_diff_main",
      "caption": "【CHILD】Screen State Diff Failure Focus View",
      "sections": []
    }
  ]
}
```

### 17.2 マージルール

継承解決では、親BASEを読み込んだ後、子CHILDの定義で上書きする。

| 対象 | マージキー | ルール |
|---|---|---|
| `views[]` | `id` | 同じ `id` の view をマージする |
| `sections[]` | `id` | 同じ `id` の section をマージする |
| `fields[]` | `field` | 同じ `field` の field をマージする |
| その他の配列 | キーなし | 原則として子CHILDで置換する |
| object | key | 再帰的にマージする |
| scalar | - | 子CHILDの値で上書きする |

### 17.3 内部IDと表示名のルール

親BASEを上書きしたい場合、内部IDは親子で同じにする。

```text
views[].id      → 親子で同じ
sections[].id   → 親子で同じ
fields[].field  → 親子で同じ
```

ただし、人間が見る名前は脳バグ防止のため、必ず区別する。

```text
ファイル名: base / child を入れる
caption:   【BASE】/【CHILD】 を入れる
```

例:

```json
{ "caption": "【BASE】Screen State Diff Viewer / Full Checks" }
```

```json
{ "caption": "【CHILD】Screen State Diff Failure Focus View" }
```

### 17.4 AI生成ルール

- 共通の基本ViewDefは `base` と命名する。
- 差分だけを持つViewDefは `child` と命名する。
- captionには `【BASE】` または `【CHILD】` を入れる。
- 内部IDはマージキーとして使うため、親子で同じものを維持する。
- 継承は差分を小さくするために使う。抽象化しすぎない。

---

## 18. Markdown出力ルール（データJSON用）（v0.4-draft）

`Markdown出力→Viewer` は、対象JSONの内容をMarkdown化するための出口である。
この制御は ViewDef の `markdown` 設定で行う。

```json
{
  "markdown": {
    "enabled": true,
    "type": "screen_state_diff",
    "title": "画面状態JSON 差分結果",
    "defaultFileName": "screen_state_diff_export.md"
  }
}
```

### 18.1 重要な分離

`markdown.type` は **データJSONのMarkdown出力タイプ** である。
`ViewDef Markdown→Viewer` の出力形式を制御するものではない。

```text
Markdown出力→Viewer
  対象: データJSON
  設定: viewDef.markdown

ViewDef Markdown→Viewer
  対象: ViewDef JSON
  設定: 原則アプリ側の固定レポート
```

将来、ViewDefレポート側の制御が必要になった場合は、`markdown` ではなく `viewDefReport` などの別名を使う。

### 18.2 既存 type

| type | 用途 |
|---|---|
| `screen_state_expected` | 画面状態JSONの期待値定義 |
| `screen_state_diff` | 画面状態JSONの差分結果 |
| `screen_state_test_patterns` | 画面状態JSONのテストパターン台帳 |
| `auto` / 未指定 | 汎用テーブル出力 |

### 18.3 AI生成ルール

- 専用Markdownが必要なデータは `markdown.type` を明示する。
- 専用Markdownが不要なデータは未指定でもよい。汎用出力へフォールバックする。
- ファイル名を固定したい場合は `defaultFileName` を指定する。
- Markdown出力の見出しは `markdown.title` を優先する。

---

## 19. 汎用Markdownセクション出力: `markdown.type = generic_sections`（v0.4-draft）

画面で見たい構造と、Markdownで読ませたい構造は一致しないことがある。
そのため、Markdown出力では `grid.visible` に依存せず、`markdown.sections` で出力構造を定義できる。

```text
grid.visible / edit.visible
  → 画面表示の制御

markdown.sections
  → Markdown出力の制御
```

### 19.1 基本形

```json
{
  "markdown": {
    "enabled": true,
    "type": "generic_sections",
    "title": "AI制約設計書",
    "defaultFileName": "ai_constraint_spec_export.md",
    "sections": [
      {
        "title": "レビュー対象",
        "source": "currentRow",
        "fields": [
          { "field": "summary", "caption": "要約", "format": "blockquote" },
          { "field": "scope", "caption": "対象範囲", "format": "paragraph" }
        ]
      },
      {
        "title": "含まれる個別制約",
        "source": "currentRow",
        "arrayField": "constraints",
        "format": "table",
        "fields": [
          { "field": "id", "caption": "ID" },
          { "field": "title", "caption": "タイトル" },
          { "field": "statement", "caption": "制約本文" }
        ]
      }
    ]
  }
}
```

### 19.2 markdown section

| key | 説明 |
|---|---|
| `title` | Markdown見出し |
| `source` | 出力元。`sourceData` / `currentRow` / `allRows` など |
| `dataPath` | 任意のデータパス |
| `arrayField` | 配列項目を表・カードとして出す場合の field |
| `format` | `table` / `list` / `cards` / `paragraph` / `blockquote` / `json` / `chat` |
| `fields` | 出力する項目の配列 |

### 19.3 markdown field

| key | 説明 |
|---|---|
| `field` | データ項目パス |
| `caption` | Markdown上の表示名 |
| `format` | `text` / `paragraph` / `blockquote` / `code` / `json` / `note` |
| `visible` | `false` の場合Markdownに出さない |
| `empty` | 空値時の表示文字 |

### 19.4 AI生成ルール

- 詳細ダイアログで読む重要情報は、必要に応じて `markdown.sections` にも明示する。
- `objectArray` / `stringArray` の中身をMarkdownに出したい場合は、`arrayField` を使う。
- レビュー対象文章、含まれる個別制約、会話ログなどは `generic_sections` の主対象である。
- 画面で非表示の項目でも、Markdownで必要なら `markdown.sections` に含める。

---

## 20. ViewDef Markdownレポート（ViewDef定義用）（v0.4-draft）

`ViewDef Markdown→Viewer` は、ViewDef定義そのものをMarkdown化する出口である。
これはデータJSONのMarkdown出力とは別系統である。

### 20.1 出力内容

標準レポートでは以下を出力する。

```text
基本情報
View / Section 概要
継承差分サマリ
生ViewDef概要
解決済みViewDef概要
元ViewDef JSON
解決済みViewDef JSON
```

### 20.2 継承差分サマリ

`extends` がある場合、親BASEの解決済みViewDefと、子CHILDの解決済みViewDefを比較し、以下の差分を出力する。

- View差分
- Section差分
- Field差分

`extends` がない場合は、継承差分なしとして出力する。

### 20.3 viewDefReport（将来用）

将来、ViewDefレポートの出力内容をViewDef側から制御したい場合は、`markdown` ではなく `viewDefReport` を使う。

```json
{
  "viewDefReport": {
    "enabled": true,
    "includeInheritanceDiff": true,
    "includeResolvedJson": true
  }
}
```

---

## 21. chat field 拡張: `edit.input` / `embeddedFields` / radio（v0.4-draft）

`chat` field は、会話表示だけでなく、コメント追加入力や埋め込みフィールドも扱える。

### 21.1 コメント追加入力: `edit.input`

```json
{
  "field": "__group_chat",
  "caption": "制約グループ会話",
  "type": "chat",
  "edit": {
    "visible": true,
    "messages": [],
    "input": {
      "enabled": true,
      "userField": "user_reply",
      "aiField": "ai_followup_response",
      "placeholder": "この制約グループへのコメントを追加...",
      "sendLabel": "送信"
    }
  }
}
```

| key | 説明 |
|---|---|
| `enabled` | 入力バーを表示するか |
| `userField` | 送信内容を書き込むフィールド |
| `aiField` | AI回答待ち欄として用意するフィールド |
| `placeholder` | 入力欄のプレースホルダー |
| `sendLabel` | 送信ボタン表示 |

### 21.2 メッセージ内埋め込み: `embeddedFields`

チャット吹き出しの中に、承認ラジオなどの入力部品を埋め込める。

```json
{
  "role": "constraint",
  "field": "statement",
  "label": "制約本文",
  "readonly": true,
  "embeddedFields": [
    {
      "field": "review_check",
      "label": "確認",
      "control": "radio",
      "options": ["未確認", "確認済み", "対象外"]
    }
  ]
}
```

### 21.3 radio control

通常Fieldまたは埋め込みFieldで、`control: "radio"` または `edit.control: "radio"` を指定できる。

```json
{
  "field": "review_check",
  "caption": "確認状態",
  "type": "select",
  "options": ["未確認", "確認済み", "対象外"],
  "edit": {
    "visible": true,
    "control": "radio"
  }
}
```

### 21.4 AI生成ルール

- レビュー状態・承認状態など、候補が少なく頻繁に触る項目は radio を推奨する。
- 会話末尾にコメントを追記したい場合は `edit.input` を使う。
- 会話の中で同時に確認状態を変更したい場合は `embeddedFields` を使う。

---

## 22. 追加制約まとめ（v0.4）

- `extends` は ViewDef継承用。
- 継承マージでは `views.id` / `sections.id` / `fields.field` をキーにする。
- 人間が見る caption は `【BASE】/【CHILD】` で親子を区別する。
- `markdown.type` はデータJSONのMarkdown出力用。
- `ViewDef Markdown→Viewer` はViewDef定義レポート用であり、`markdown.type` とは別系統。
- `generic_sections` では、画面表示とは別にMarkdown出力順を定義できる。
- `grid.visible` は画面用、`markdown.sections` はMarkdown用。
- chat field は `edit.messages` / `edit.input` / `embeddedFields` を使ってレビュー会話を構成できる。
