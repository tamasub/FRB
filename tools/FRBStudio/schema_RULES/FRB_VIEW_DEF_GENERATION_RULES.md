# FRB Studio View Definition Generation Rules

対象: `FRBStudio_App` / No-Code JSON Studio v0.4.1 系

この文書は、AI が新しいデータ JSON から `view_def.json` を生成するための作成ルールである。

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

