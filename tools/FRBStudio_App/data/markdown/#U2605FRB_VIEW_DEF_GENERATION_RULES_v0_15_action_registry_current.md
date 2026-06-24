# FRB Studio ViewDef Generation Rules v0.15 — Current Runtime / Action Registry Edition

対象: `FRBStudio_App` / No-Code JSON Studio v0.6+ 系  
対応Schema: `frb_view_def_schema_v0_8_action_registry_toolbar.json`

この文書は、AIに **Data JSON から ViewDef JSON を作成させる** ときの作成ルールである。

Studioくんにおける ViewDef は、単なる画面定義ではない。

```text
Data JSON + ViewDef JSON + Runtime + Action = Experience
```

ViewDef は、データの見え方・編集の仕方・Markdown化・AIへの渡し方・仮想データの作り方・主役Actionを宣言する **体験設計書** である。

---

## 0. AIへ渡す資料の優先順位

ViewDef生成を依頼するとき、AIは次の優先順位で判断する。

1. 最新の対象 Data JSON
2. 最新の ViewDef Schema
3. この Rules MD
4. 既存の近い ViewDef サンプル
5. 最新ソースの実装挙動
6. 過去ルール・過去ViewDef

古いルールや古いViewDefは、参考にはしてよいが、最新Schema / 最新Runtime / このRulesに反する場合は採用しない。

---

## 1. 生成時の絶対原則

### 1.1 Data First

Data JSONに存在する構造を最優先する。

- 存在しないフィールドを勝手に増やさない。
- 意味が不明なフィールドは、まず readonly 表示に寄せる。
- 配列はMain Grid候補または `objectArray` / `stringArray` 候補として扱う。
- ルート直下のメタ情報は Header Form 候補にする。

### 1.2 ViewDef First

Runtimeやソースを個別データ専用に変えない。表示・編集・Markdown・Actionの違いは ViewDef に宣言する。

### 1.3 固定Dataフィールド名の原則禁止

Runtime内に `row.message`、`row.status`、`row.result` のようなData固定名を増やす前提でViewDefを作ってはいけない。

ViewDefでは、対象Dataに実在するフィールドを `field` に指定する。

```json
{ "field": "latest_user_comment", "caption": "最新ユーザーコメント", "type": "textarea" }
```

Runtime側の固定名ではなく、ViewDefの `field` によって意味を与える。

### 1.4 camelCaseを基本にする

Runtimeは一部 snake_case alias も読むが、新規ViewDefでは camelCase を基本にする。

推奨:

```json
"dataSources", "virtualData", "targetPath", "writeBack", "executeButton"
```

互換目的以外では snake_case を混在させない。

---

## 2. 基本構造

現行Studioは、基本的に **1画面1メイングリッド** で設計する。

```json
{
  "app": {
    "name": "No-Code JSON Studio",
    "version": "example-v0.1"
  },
  "views": [
    {
      "id": "example_view",
      "caption": "Example View",
      "layout": "header-search-grid-detail",
      "sections": []
    }
  ]
}
```

`views[0]` が主画面として使われる。

---

## 3. layout

通常は文字列で指定する。

```json
"layout": "header-search-grid-detail"
```

詳細ダイアログを広くしたい場合は object 形式を使える。

```json
"layout": {
  "detailDialog": "wide"
}
```

ただし、意味なく wide にしない。`chat`、`objectArray`、長文textarea、Relationカードなど横幅が必要な画面で使う。

---

## 4. Section設計

### 4.1 Header Form

ルート直下のメタ情報を表示する。

```json
{
  "id": "header",
  "caption": "基本情報",
  "type": "form",
  "dataPath": "$",
  "fields": []
}
```

最初に見つかった `type: "form"` かつ `role !== "detailOnly"` の section がHeaderになる。

### 4.2 Main Grid

対象配列を表示・編集する。

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

最初に見つかった `type: "grid"` がMain Gridになる。

### 4.3 dataPath

使用可能な形式は簡易dot path。

```text
$
$.items
$.work_items
views.0.caption
```

避ける形式:

```text
items[0].name
$.items[0].name
キー名に . を含むJSON
```

---

## 5. Field設計

基本形:

```json
{
  "field": "title",
  "caption": "タイトル",
  "type": "text",
  "grid": { "visible": true, "width": 220 },
  "edit": { "visible": true },
  "search": { "visible": true, "operator": "contains" }
}
```

### 5.1 caption必須運用

すべての field に `caption` を付ける。  
AIが意味を推定できる場合は、日本語captionにする。

### 5.2 grid / edit / search は分離する

- `grid.visible`: 一覧に出すか
- `edit.visible`: Detailに出すか
- `edit.readonly`: Detailで編集不可にするか
- `search.visible`: 検索欄に出すか

一覧に出さないが詳細では見たい項目は、次のようにする。

```json
"grid": { "visible": false },
"edit": { "visible": true }
```

### 5.3 readonly

計算結果、ID、履歴、AI回答、仕様説明は原則 readonly。

```json
"readonly": true,
"edit": { "visible": true, "readonly": true }
```

---

## 6. Field type一覧

現行Runtimeで扱う基本type:

| type | 用途 | 備考 |
|---|---|---|
| `text` | 短い文字列 | 迷ったらこれ |
| `textarea` | 長文\|xxx | `edit.height` 推奨 |
| `number` | 数値\|xxx\| | grid format可 |
| `boolean` | true/false | select表示 |
| `select` | 状態・分類 | `options` 必須級 |
| `datetime` | 日付・時刻文字列 | 現状はtext入力 |
| `objectArray` | オブジェクト配列 | サブグリッド表示向け |
| `stringArray` | 文字列配列aa | サブグリッド表示向け |
| `chat` | 複数フィールドの会話表示 | `edit.messages` 推奨 |

### 6.1 select options

単純な候補:

```json
"options": ["未着手", "作業中", "完了"]
```

オブジェクト候補も使用可能。既定では `cd` が値、`name` が表示名。

```json
"options": [
  { "cd": "draft", "name": "下書き" },
  { "cd": "active", "name": "運用中" }
]
```

独自フィールド名を使う場合:

```json
"valueField": "id",
"labelField": "label"
```

禁止:

```json
"options": ""
```

---

## 7. 入力UI制御

### 7.1 radio

承認・状態選択など、少数候補を明示したい場合に使う。

```json
{
  "field": "status",
  "caption": "状態",
  "type": "select",
  "control": "radio",
  "options": ["未着手", "作業中", "完了"]
}
```

または:

```json
"edit": { "control": "radio" }
```

### 7.2 listbox

候補を一覧で見せたい場合に使う。

```json
"edit": { "control": "listbox" }
```

---

## 8. objectArray / stringArray

配列をDetail内でサブグリッド表示したい場合に使う。

```json
{
  "field": "discussion_history",
  "caption": "会話履歴",
  "type": "objectArray",
  "grid": { "visible": false },
  "edit": { "visible": true }
}
```

原則:

- Gridには出さずDetailで見る。
- 履歴・ログ・変更履歴は readonly寄りで扱う。
- ただしStudioはサブグリッド編集に対応しているため、必要なら編集対象にできる。
- 配列の中身をMain Gridにしたい場合は、section.dataPathでその配列を指定する。

---

## 9. chat type

`chat` は、複数フィールドを会話タイムラインとして見せるための仮想表示fieldである。

```json
{
  "field": "__work_chat",
  "caption": "作業会話サマリ",
  "type": "chat",
  "grid": { "visible": false },
  "edit": {
    "visible": true,
    "messages": [
      { "role": "user", "field": "user_request", "label": "依頼" },
      { "role": "ai", "field": "ai_response", "label": "AI回答", "readonly": true },
      { "role": "user", "field": "latest_user_comment", "label": "追加コメント" },
      { "role": "ai", "field": "latest_ai_response", "label": "AI再回答", "readonly": true }
    ],
    "input": {
      "enabled": true,
      "userField": "latest_user_comment",
      "aiField": "latest_ai_response",
      "placeholder": "この作業へのコメントを追加...",
      "sendLabel": "送信"
    }
  }
}
```

### 9.1 chatの原則

- `field` は `__xxx_chat` のような仮想名でよい。
- 実際に表示する内容は `edit.messages[].field` で指定する。
- AI回答系は readonly 推奨。
- 人間が追記する欄は `edit.input.userField` に指定する。
- chatに固定フィールド名を期待しない。必ず `messages` で明示する。

### 9.2 embeddedFields

吹き出し内にradio等を埋め込める。

```json
{
  "role": "user",
  "field": "user_comment",
  "label": "俺コメント",
  "embeddedFields": [
    {
      "field": "approval_decision",
      "label": "判断",
      "type": "select",
      "control": "radio",
      "options": ["承認", "保留", "差戻し"]
    }
  ]
}
```

---

## 10. Detail Footer配置

子配列サブグリッドの後に表示したいfieldは `detailFooter` を使う。

```json
{
  "field": "__review_chat",
  "caption": "レビュー会話",
  "type": "chat",
  "layout": { "placement": "detailFooter" },
  "grid": { "visible": false },
  "edit": { "visible": true }
}
```

または:

```json
"edit": { "layout": { "placement": "detailFooter" } }
```

用途:

- chat
- 補足メモ
- 長文レビュー欄
- 子グリッドの後に読みたい説明

---

## 11. Markdown出力

### 11.1 view.markdown

Data JSONをMarkdown出力する設定。

```json
"markdown": {
  "enabled": true,
  "type": "generic_sections",
  "title": "作業レポート",
  "defaultFileName": "work_report.md",
  "sections": []
}
```

現在の登録済み `markdown.type`:

- `auto`
- `generic_sections`
- `screen_state_expected`
- `screen_state_diff`
- `screen_state_test_patterns`

### 11.2 ViewDef Markdownとは別物

`view.markdown` は Data JSON のMarkdown出力用。  
ViewDef定義そのものを読むための「ViewDef Markdown→Viewer」とは別系統。

### 11.3 markdown.sections

```json
{
  "title": "概要",
  "source": "header",
  "format": "paragraph",
  "fields": [
    { "field": "title", "caption": "タイトル" },
    { "field": "purpose", "caption": "目的", "format": "paragraph" }
  ]
}
```

主な `source`:

- `root` / `sourceData`
- `currentRow`
- `allRows`
- `header`
- `grid`
- `rows` / `currentRows`

主な `format`:

- `auto`
- `text`
- `paragraph`
- `textarea`
- `blockquote`
- `code`
- `json`
- `note`
- `table`
- `list`
- `cards`
- `chat`
- `heading`
- `constraintList`
- `detailList`
- `detail`

---

## 12. Markdown AI Prompt

AI貼り付け用ブロックは、対象 grid section の `markdown.aiPrompt` に持たせる。

```json
{
  "id": "work_items",
  "caption": "作業項目",
  "type": "grid",
  "dataPath": "$.work_items",
  "markdown": {
    "aiPrompt": {
      "enabled": true,
      "title": "次アクション生成プロンプト",
      "targetFile": "studio_work_incident_data_v0_4.json",
      "rowSource": "filtered",
      "visibleOnly": true,
      "includeGridJson": true,
      "template": [
        "以下は現在表示中の作業項目です。",
        "この内容をもとに、次にAIへ依頼する作業文を作成してください。",
        "",
        "条件:",
        "- 作業範囲を混ぜない",
        "- 既存機能を壊さない",
        "- 出力は作業依頼文だけにする",
        "",
        "TSV:"
      ]
    }
  },
  "fields": []
}
```

`rowSource`:

| 値 | 意味 |
|---|---|
| `filtered` | 現在表示中の行。検索・絞り込み後。既定値 |
| `all` / `current` | currentRows全体 |
| `selected` | 選択中の1行 |

`includeGridJson: true` を推奨する。TSVだけでなく field/caption/rows を持つため、AIが列意味を取り違えにくい。

---

## 13. dataSources

複数JSONを参照する場合に使う。

```json
"dataSources": {
  "relations": "constraint_trace_relations_v0_1.json",
  "diff": "screen_state_smoke_001.diff.json"
}
```

- keyはViewDef内で参照する別名。
- 値は管理対象JSONファイル名。
- サブフォルダがある場合はフルパスを使う。

---

## 14. virtualData

`virtualData` は、元DataやdataSourcesから画面表示用の仮想配列を生成する。

```json
"virtualData": {
  "builder": "relation_axis_cards",
  "targetPath": "$.relation_axis_cards",
  "relations": {
    "source": "relations",
    "path": "$.relations"
  },
  "axis": {
    "path": "$.constraints",
    "nodeType": "constraint",
    "idField": "constraint_id",
    "titleField": "title"
  }
}
```

現在の登録済み `virtualData.builder`:

- `relation_axis_cards`
- `relation_diff_cards`
- `relation_diff_check_cards`
- `constraint_trace_cards`
- `test_pattern_trace_cards`
- `expected_check_cross_counts`
- `expected_check_shortage_findings`

### 14.1 virtualDataの原則

- 通常のViewDef生成では無理に使わない。
- relation / diff / shortage / trace など、元DataをそのままGrid表示しても読みにくい場合に使う。
- `targetPath` は生成結果の格納先。Main Gridの `dataPath` はこの `targetPath` を指す。
- builder固有の固定フィールド名はAdapter/Builder仕様として扱う。Runtime全体へ漏らさない。

### 14.2 statusFilter

Relation線の採用条件はViewDefで明示する。

```json
"relation": {
  "statusFilter": ["approved"],
  "structureStatusFilter": ["derived", "approved"],
  "excludeStatus": ["rejected"]
}
```

意味:

- `statusFilter`: 証跡線として採用するstatus
- `structureStatusFilter`: 構造線として採用するstatus
- `excludeStatus`: 常に除外するstatus

---

## 15. writePolicy / writeBack

仮想データを使う場合、どのJSONへ書き戻してよいか曖昧にしない。

トップレベル:

```json
"writePolicy": {
  "mode": "singleSource",
  "primarySource": "relations",
  "virtualDataReadonly": false
}
```

virtualData内:

```json
"writeBack": {
  "enabled": true,
  "source": "relations",
  "path": "$.relations",
  "keyField": "relation_id",
  "fields": [
    { "from": "review_status", "to": "status" }
  ]
}
```

不安な場合は readonly に寄せる。

---

## 16. toolbar.executeButton / Action

View固有の主役操作を1つ置きたい場合は、`toolbar.executeButton` を使う。

```json
"toolbar": {
  "executeButton": {
    "visible": true,
    "caption": "Markdown出力",
    "action": "ExportMarkdown"
  }
}
```

現在の登録済みAction:

- `LoadData`
- `SaveData`
- `ExportMarkdown`
- `ExportViewDefMarkdown`
- `RefreshServerLists`
- `ShowActionContext`
- `Noop`

### 16.1 Actionの原則

- `toolbar` 直下を配列にしない。
- 主役操作は `toolbar.executeButton` に置く。
- `caption` はボタン表示名。
- `action` はActionRegistryの識別子。
- Runtimeに固定Action名を書かせる設計にしない。

良い:

```json
"action": "ExportMarkdown"
```

悪い設計思想:

```js
executeStudioAction("PlayMidi", context)
```

ViewDef上のAction名は宣言。Runtime内のAction固定文字列は脂肪。

### 16.2 toolbar.buttons

`toolbar.buttons` は将来の補助ボタン用予約領域。  
現行v0.6では `executeButton` だけを前提にする。

---

## 17. extends / 継承

既存ViewDefの一部だけ変えたい場合は `extends` を使う。

```json
{
  "extends": "screen_state_diff_view_def_base_v0_2_checks.json",
  "views": [
    {
      "id": "screen_state_diff_child",
      "caption": "【CHILD】Failure Focus",
      "layout": "header-search-grid-detail",
      "sections": []
    }
  ]
}
```

配列は `id` / `field` / `name` をキーにマージされる。  
削除したい場合は `remove: true` / `$remove: true` / `_remove: true` を使える。

```json
{ "field": "debug_info", "remove": true }
```

継承を使う時は caption に **【BASE】/【CHILD】** を入れると、人間が理解しやすい。

---

## 18. common field types

共通語彙は `common_types_v0_1.json` が既定で読み込まれる。  
明示したい場合:

```json
"fieldTypeSources": ["common_types_v0_1.json"]
```

fieldでは `fieldType` / `typeRef` または `type` に名前空間付き参照を書ける。

```json
{
  "field": "status",
  "caption": "状態",
  "fieldType": "core.review_status"
}
```

または:

```json
{
  "field": "status",
  "caption": "状態",
  "type": "core.review_status"
}
```

ただしAIが新規ViewDefを作るときは、まず基本typeで明示する方が安全。共通fieldTypeは既存定義が確実に使える場合だけ使う。

---

## 19. 命名ルール

### 19.1 ファイル名

```text
<対象>_view_def_v0_1.json
<対象>_view_def_v0_2_<目的>.json
```

例:

```text
studio_work_incident_view_def_v0_2_execute_button_sample.json
screen_state_diff_view_def_child_v0_3_failure_focus.json
```

### 19.2 id

- View ID: `snake_case`
- section ID: `header`, `mainGrid`, `work_items` など
- 仮想field: `__work_chat` のように `__` を付けると実Dataと区別しやすい

---

## 20. AI生成時の出力ルール

AIがViewDef JSONを生成するときは、以下を守る。

1. 出力JSONは構文エラーなし。
2. JSONにコメントを書かない。
3. `views[0].sections` を必ず持たせる。
4. Main Gridの `dataPath` は実在する配列を指す。
5. Header Formはルート `$` を指す。
6. fieldには `field` / `caption` / `type` を必ず入れる。
7. 長文は `textarea` + `edit.height`。
8. 状態・分類は `select` + `options`。
9. 履歴配列は `objectArray`。
10. 会話表示は `chat` + `edit.messages`。
11. AI Promptが必要な場合は grid section の `markdown.aiPrompt` に書く。
12. 主役Actionが必要な場合は `toolbar.executeButton` に書く。
13. 迷ったら readonly に寄せる。
14. 固定Dataフィールド名をRuntimeに求める設計にしない。

---

## 21. 禁止・注意パターン

### 21.1 toolbar配列は禁止

悪い:

```json
"toolbar": [
  { "caption": "再生", "action": "PlayMidi" }
]
```

良い:

```json
"toolbar": {
  "executeButton": {
    "caption": "再生",
    "action": "PlayMidi"
  }
}
```

ただし `PlayMidi` はActionRegistryに登録されている場合のみ使う。

### 21.2 options空文字は禁止

悪い:

```json
"options": ""
```

良い:

```json
"options": []
```

または `options` 自体を省略する。

### 21.3 fieldにbracket pathを書かない

悪い:

```json
"field": "items[0].name"
```

良い:

```json
"field": "name"
```

section側で:

```json
"dataPath": "$.items"
```

### 21.4 目的の違うものを混ぜない

- ViewDef生成
- Schema変更
- Runtime変更
- Data変換

これらは混ぜない。  
ViewDefで吸収できることはViewDefで吸収する。

---

## 22. Schema見直しが必要な条件

次の場合だけ、Schema更新を検討する。

- Runtimeが正式対応したViewDefキーがSchemaにない。
- 既存Runtimeが読んでいるaliasをSchemaが拒否している。
- AI生成で毎回同じ誤りが出る。
- ViewDefで宣言すべき概念が、Schema上で表現できない。
- 固定フィールド名を標準メタフィールドとして昇格させる必要がある。

Schema更新は、Runtime変更とは別作業として扱う。  
Schemaだけを肥満化させず、「Runtimeが読む公用語」を明記する。

---

## 23. AI依頼テンプレート

```text
添付のData JSONから、FRB Studio / No-Code JSON Studio用のViewDef JSONを作成してください。

条件:
- FRB_VIEW_DEF_GENERATION_RULES_v0_15 に従う
- schema は frb_view_def_schema_v0_8_action_registry_toolbar.json を前提にする
- Runtime内のData固定名を前提にしない
- field / caption / type を必ず入れる
- ルートのメタ情報は header form
- 主配列は main grid
- 配列履歴は objectArray
- 会話表示が必要な場合は chat + edit.messages
- Markdown AI貼り付け用が必要な場合は section.markdown.aiPrompt
- 主役Actionが必要な場合は toolbar.executeButton
- 出力は JSON ファイルとしてそのまま保存できる完全なJSONのみ
```

---

## 24. まとめ

ViewDefは、画面定義ではなく体験設計書である。

```text
Dataを変えずに、見方を変える。
Runtimeを太らせずに、ViewDefへ宣言する。
AIが迷わないように、構造・履歴・ActionをJSONに残す。
```

これがStudioくんのViewDef生成ルールである。
