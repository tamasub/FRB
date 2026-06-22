# FRB Studio ViewDef Generation Rules ALL v0.16

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

### 0.1 FRB_VIEW_DEF_GENERATION_RULES_ALL の命名ルール

このRules文書は、AIへViewDef生成を依頼するための **正本** として扱う。

ファイル名は必ず次の形式にする。

```text
FRB_VIEW_DEF_GENERATION_RULES_ALL_v0_16.md
```

ルール:

- `FRB_VIEW_DEF_GENERATION_RULES_ALL` を必ず含める。
- バージョン更新時は、`v0_15` → `v0_16` のように **バージョン数字だけ** を変更する。
- バージョン番号の後ろに目的語・差分名・説明語を付けない。
- `FRB_VIEW_DEF_GENERATION_RULES_v0_16_action_registry_current.md` のような派生名は禁止する。
- 差分情報・生成レポート・検討メモを `FRB_VIEW_DEF_GENERATION_RULES...` 名で作らない。
- 差分やレポートは `viewdef_rules_update_report_v0_16.json` など、別名にする。

このルールは **FRB_VIEW_DEF_GENERATION_RULES_ALL** にのみ適用する。  
通常のViewDefファイル名やData JSONファイル名には適用しない。

目的は、Rules正本の紛失防止と、AIが古い派生Rulesを正本と誤認する事故を防ぐことである。

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

### 1.3.1 固定名の分類

固定名を見つけても即削除しない。次のどれかに分類する。

| 分類 | 扱い |
|---|---|
| Studio仕様の骨格 | `views`, `sections`, `fields`, `field`, `caption`, `type`, `grid`, `edit`, `markdown`, `toolbar` など。公用語として使用可。 |
| DOMシェルの骨格 | `loadBtn`, `saveBtn` などStudio本体UIのID。Data固定名ではないため使用可。 |
| ViewDef宣言値 | `virtualData.builder`, `markdown.type`, `toolbar.executeButton.action` など。ViewDefで宣言する識別子として使用可。 |
| Adapter / Builder仕様 | relation系builder内部など、特定Adapterの仕様として閉じている固定名。Runtime全体へ漏らさない。 |
| Runtime脂肪 | `row.message`, `row.status`, `row.result` のようにData構造をRuntimeが決め打ちするもの。原則NG。 |
| Studio標準メタフィールド候補 | 汎用性が高いが例外扱いが必要なもの。採用前に明記・協議する。 |

### 1.3.2 Studio標準メタフィールド候補

次のようなフィールドは、将来的にStudio標準メタフィールドとして扱える可能性がある。

```text
created_at
updated_at
created_by
updated_by
deleted
is_deleted
sort_order
status
```

ただし、便利だからという理由だけで標準化してはいけない。  
標準メタフィールドとして扱う場合は、憲法・Rules・Schemaのいずれかに用途・型・Runtimeが参照してよい範囲を明記する。

標準化されていないDataフィールド名を、Runtimeが直接参照することは禁止する。

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
| `textarea` | 長文 | `edit.height` 推奨 |
| `number` | 数値 | grid format可 |
| `boolean` | true/false | select表示 |
| `select` | 状態・分類 | `options` 必須級 |
| `datetime` | 日付・時刻文字列 | 現状はtext入力 |
| `objectArray` | オブジェクト配列 | サブグリッド表示向け |
| `stringArray` | 文字列配列 | サブグリッド表示向け |
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


### 8.1 objectArray / stringArray 保存契約

`objectArray` / `stringArray` は、表示用の件数文字列と保存実体を必ず分離する。

悪い保存結果:

```json
"discussion_history": "3 items"
```

良い保存結果:

```json
"discussion_history": [
  { "history_id": "disc_001", "message": "..." }
]
```

ルール:

- `2 items`, `3 items` などの表示文字列をData JSONへ保存してはいけない。
- Detail画面で件数表示する場合も、保存時は元の配列を保持する。
- `discussion_history`, `decision_log`, `change_history`, `review_notes` などをRuntimeが固定名で特別扱いしない。
- ViewDefで `type: "objectArray"` と宣言されたフィールドを汎用的に配列として扱う。
- 保存処理で編集対象外のobjectArrayを上書きしない。

これは、Studioくんの会話履歴・判断ログ・改修履歴を守るための必須条件である。

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


### 9.1.1 chat入力保存契約

`chat` は仮想表示fieldであり、`field: "__work_chat"` 自体を保存先にしてはいけない。

追加コメント入力欄を使う場合は、必ず保存先を明示する。

```json
"input": {
  "enabled": true,
  "userField": "latest_user_comment",
  "aiField": "latest_ai_response",
  "placeholder": "この作業へのコメントを追加...",
  "sendLabel": "送信"
}
```

ルール:

- `edit.input.userField` を優先して人間入力を保存する。
- `edit.input.aiField` はAI再回答欄や初期化先として使う。
- `user_reply` / `ai_followup_response` などの既定固定名に依存しない。
- `messages[].field` で表示しているフィールドを編集した場合、保存時にそのフィールドへ反映される必要がある。
- 反映(F12)後に上書き保存しても値が保存されない、または削除した文字が復活する状態はNG。
- chat表示用DOMの値とData JSONの値を同期し、ゾンビ復活を起こさない。

### 9.1.2 chat本文のMarkdownリンク / 画像記法

chat本文やコメント欄では、必要に応じてMarkdownリンク・画像記法を許可できる。

例:

```markdown
[参考資料](./docs/spec.md)
![画面イメージ](./png/screen_001.png)
```

ViewDefでは、Markdown解釈を許可するfieldを明示する。

```json
{
  "role": "user",
  "field": "latest_user_comment",
  "label": "追加コメント",
  "markdown": {
    "inline": true,
    "allowLinks": true,
    "allowImages": true
  }
}
```

簡易指定として、Runtimeが対応している場合は次も許容する。

```json
{ "role": "user", "field": "latest_user_comment", "label": "追加コメント", "markdown": true }
```

ルール:

- すべてのtextareaでMarkdownを自動解釈しない。
- `chat`、memo系textarea、Markdown出力対象フィールドなど、ViewDefで明示された場所だけ許可する。
- 相対パスは、出力されたMarkdownファイルまたはViewer表示基準の相対パスとして扱う。どちらを採用するかはRuntime仕様に明記する。
- Data側に `image_url` のような固定フィールド名を作る前に、本文中Markdown記法で表現できないか検討する。

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

### 10.1 Detail Body readable cards

説明・背景・方針・リスク・確認観点などの長文フィールドが多数ある場合、textareaを横並びに大量配置しない。

読み物として確認したい長文は、`detailBody` の横広カードとして表示することを優先する。

代表例:

```json
{
  "field": "__work_summary_cards",
  "caption": "作業内容 / 方針",
  "type": "chat",
  "grid": { "visible": false },
  "edit": {
    "visible": true,
    "messages": [
      { "role": "constraint", "field": "objective", "label": "目的", "height": 120 },
      { "role": "constraint", "field": "background", "label": "背景", "height": 120 },
      { "role": "constraint", "field": "scope", "label": "対象範囲", "height": 120 },
      { "role": "constraint", "field": "risk", "label": "リスク", "height": 120 },
      { "role": "constraint", "field": "test_points", "label": "確認観点", "height": 120 }
    ],
    "input": { "enabled": false }
  },
  "layout": {
    "placement": "detailBody",
    "order": 120
  }
}
```

この場合、元フィールドは検索対象として残しつつ、Detailの通常textarea表示を非表示にできる。

```json
{
  "field": "objective",
  "caption": "目的",
  "type": "textarea",
  "grid": { "visible": true },
  "edit": { "visible": false },
  "search": { "visible": true, "operator": "contains" }
}
```

ルール:

- 入力中心の項目はtextarea、レビュー・確認中心の項目はreadable cardに寄せる。
- `objective`, `background`, `scope`, `out_of_scope`, `fixed_name_policy`, `module_policy`, `expected_outputs`, `risk`, `test_points` などはカード化候補。
- `layout.placement: "detailBody"` を使い、子グリッドより上に置く。
- 子グリッドの後に置きたい会話欄は `detailFooter` を使う。
- 表示専用カードでは `edit.input.enabled: false` を指定する。
- 保存できる必要があるカード項目は、chat保存契約に従い、表示DOMとData JSONを同期させる。

これは、長文textareaの農場を避け、レビュー対象を読み物として扱うためのルールである。

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


### 11.4 Markdown出力契約

Markdown出力は単なる表示ではない。  
Studioの現在状態・Data・ViewDef・AI貼り付け用情報を、人間とAIへ渡すための外部記憶フォーマットである。

Markdown出力で扱う対象:

- Data JSONの内容
- 現在表示中のGrid行
- Header / Detail / objectArray / chat
- AI貼り付け用prompt / TSV / Grid JSON
- 必要に応じた展開前ViewDef JSON
- 必要に応じた展開後ViewDef JSON
- Markdownリンク / 画像記法

ViewDefで出力範囲を明示し、出しすぎによる巨大化を避ける。

### 11.5 展開前JSON / 展開後JSON

ViewDef Markdown出力では、必要に応じて展開前JSONと展開後JSONを出力できるようにする。

| 種類 | 意味 |
|---|---|
| 展開前JSON | 人間が書いたViewDef。設計意図確認用。 |
| 展開後JSON | extends / common field types / alias解決後、Runtimeが解釈する最終形。実行状態確認用。 |

想定指定:

```json
"markdown": {
  "export": {
    "includeSourceViewDefJson": true,
    "includeResolvedViewDefJson": true,
    "includeSourceDataJson": false,
    "includeResolvedDataJson": false
  }
}
```

ルール:

- デフォルトで巨大JSONをすべて出さない。
- バグ調査・AI依頼・Schema/Rulesレビューでは展開前/展開後の両方が有効。
- 展開後JSONはRuntimeが実際に見ている構造として扱う。
- 差分情報をRules本文に混ぜない。差分レポートは別ファイルにする。

### 11.6 Markdownリンク / 画像記法

Markdown出力対象の本文では、必要に応じてリンク・画像記法を保持する。

```markdown
[リンク名](./docs/sample.md)
![画像説明](./png/sample.png)
```

ルール:

- Markdown記法はDataの文字列として保持する。
- 画像URL専用の固定Dataフィールド名を前提にしない。
- chat/textarea/markdown対象フィールドで、ViewDefがMarkdown解釈を許可した場合に表示対象とする。
- 画像表示を許可する場合は、セキュリティと相対パス解決のルールをRuntime側に持つ。

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

### 19.1.1 Markdown出力ファイル名のsanitize

Markdown出力やViewer連携で生成するファイル名は、人間が読める名前にする。

禁止:

```text
#U521d#U671f#U8868#U793a#U306e#U753b#U9762.md
```

ルール:

- Unicode文字を `#Uxxxx` 形式へ変換したファイル名を新規生成しない。
- URLエンコード/デコード、HTMLエンティティ、独自Unicodeエスケープを混在させない。
- 日本語ファイル名を許容する場合はUTF-8文字列として扱う。
- Windows禁止文字 `< > : " / \\ | ? *` などは共通sanitize関数で置換する。
- 空白や記号を含む場合も、保存API・Viewer URL・GitHub連携で破綻しないことを確認する。
- ViewDef名・Data名・titleからファイル名を作る場合も、必ず同じsanitize関数を通す。
- 過去に生成済みの文字化けファイルの一括リネームは別作業として扱ってよい。まず新規発生を止める。

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
15. 長文説明フィールドがある場合は、必要に応じて `detailBody` のreadable cardへ寄せ見やすさに配慮する。
16. chat入力欄を使う場合は、`edit.input.userField` / `edit.input.aiField` を明示する。
17. objectArray/stringArrayは表示用件数文字列を保存しない。
18. Markdownリンク/画像記法を許可する場合は、許可するfieldをViewDefで明示する。
19. Markdown出力ファイル名はsanitizeし、`#Uxxxx` 形式の文字化け名を新規生成しない。

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
- FRB_VIEW_DEF_GENERATION_RULES_ALL_v0_16 に従う
- schema は frb_view_def_schema_v0_8_action_registry_toolbar.json を前提にする
- Runtime内のData固定名を前提にしない
- field / caption / type を必ず入れる
- ルートのメタ情報は header form
- 主配列は main grid
- 配列履歴は objectArray
- 会話表示が必要な場合は chat + edit.messages
- Markdown AI貼り付け用が必要な場合は section.markdown.aiPrompt
- 主役Actionが必要な場合は toolbar.executeButton
- 長文説明項目が多い場合は detailBody readable card を検討する
- chat入力欄を使う場合は edit.input.userField / aiField を明示する
- Markdownリンク/画像記法を使う場合は許可fieldを明示する
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
