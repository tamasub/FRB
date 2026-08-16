# FRB Studio App Settings — 設計概要 v0.2 Draft

更新日: 2026-08-16  
対象資材: `FRBStudio_App20260816_190410`  
位置づけ: `app_settings.json` 登録・更新機能、および標準Editorの `sectionGroups` 拡張に関する設計概要  
ステータス: Draft / 意識合わせ反映版

---

## 1. 目的

FRB Studio に `⚙ 設定` を追加し、`app_settings.json` に保持するアプリ動作設定を、Studio上から登録・更新できるようにする。

ただし、Settings専用Editorを新規実装することを目的とはしない。

今回の中心は、

> **標準Editorに「Viewを明示的なグループ単位で切り替える能力」を追加し、Settingsをその最初の利用例とする。**

ことである。

---

## 2. 今回の中核判断軸

### 外からつまめ原則

既存構造や既存責務をなるべく壊したくないときは、内部へ専用実装を追加する前に、**既存の要素を外部定義から選択・組み合わせることで実現できないかを先に考える。**

つまり、

> **壊す前に、まず外からつまめないか考える。**

内部変更と外部構成のどちらでも実現できる場合は、既存構造を維持できる「外からつまむ」方法を優先する。

今回の `sectionGroups` は、この原則の代表的な適用例とする。

---

## 3. 現行ViewDefの構造

現行ViewDefは、1つの `view` の中に複数の `sections` を持つ。

概念的には以下の構造である。

```json
{
  "views": [
    {
      "id": "sample_view",
      "caption": "Sample",
      "layout": "...",
      "sections": [
        {
          "id": "header",
          "type": "form"
        },
        {
          "id": "main",
          "type": "grid"
        }
      ]
    }
  ]
}
```

現在は、ViewDefに定義された `sections` を1つの画面構成として扱っている。

今回、この既存構造を壊さず、その外側から表示対象Sectionを束ねる概念を追加する。

---

# 4. 新規固定キーワード `sectionGroups`

ViewDefの `view` に、任意項目として次の固定キーワードを追加する。

```text
sectionGroups
```

`sectionGroups` は、既存の `sections` を利用目的ごとの表示単位として束ねるための定義である。

基本形:

```json
{
  "sectionGroups": [
    {
      "id": "launch",
      "caption": "ショートカット",
      "sectionIds": [
        "launch_shortcuts"
      ]
    },
    {
      "id": "markdown",
      "caption": "Markdown Studio",
      "sectionIds": [
        "markdown_settings"
      ]
    }
  ]
}
```

---

## 4.1 用語

```text
sections
= 既存の画面構成要素

sectionGroup
= 複数のSectionをまとめた1つの表示単位

sectionGroups
= View内に存在するSection Groupの一覧

sectionIds
= そのGroupで表示する既存SectionのID一覧
```

重要なのは、`sectionGroups` 自身は新しいRendererや新しいSection Typeではないことである。

---

# 5. `sectionGroups` の基本思想

今回追加するのは、

```text
新しい画面部品
```

ではなく、

```text
既存画面部品の見せ方
```

である。

構造としては、

```text
ViewDef
  │
  ├─ sections
  │    ├─ Section A
  │    ├─ Section B
  │    ├─ Section C
  │    └─ Section D
  │
  └─ sectionGroups
       ├─ Group 1 → A + B
       └─ Group 2 → C + D
```

となる。

実行時は、

```text
sectionGroupを選択
        ↓
sectionIdsを解決
        ↓
対象sectionsを抽出
        ↓
既存Editor / Rendererへ渡す
```

という流れとする。

つまり、

> **既存Editorを起動するトリガーを、ViewDefの外側に追加する。**

という位置づけである。

---

# 6. 標準Editorへの追加能力

`sectionGroups` が存在する場合、標準EditorはSection Groupを切り替えるナビゲーションを表示する。

イメージ:

```text
┌─────────────────────────────────────┐
│ ⚙ Studio設定                        │
├──────────────┬──────────────────────┤
│ ショートカット │                      │
│ Markdown      │   既存Editor表示領域  │
│ Review        │                      │
│ ...           │                      │
└──────────────┴──────────────────────┘
```

ただし、

```text
サイドバー
タブ
上部メニュー
```

のどれで表現するかは、`sectionGroups` のデータ契約とは分離する。

今回固定するのは、

> **Groupを選択すると、そのGroupの `sectionIds` に属する既存Sectionが標準Editorで表示される。**

という動作契約である。

---

# 7. `sectionGroups` はForm専用ではない

ここは今回の重要点。

`sectionGroups` は、

```text
Formをカテゴリ分けする仕組み
```

ではない。

既存Sectionであれば、そのTypeに関係なく束ねられる。

例えばSettingsでは、

```text
ショートカット
→ Grid Section

Markdown Studio
→ Form Section
```

という構成が可能。

例:

```json
{
  "sectionGroups": [
    {
      "id": "launch",
      "caption": "ショートカット",
      "sectionIds": [
        "launch_shortcuts"
      ]
    },
    {
      "id": "markdown",
      "caption": "Markdown Studio",
      "sectionIds": [
        "markdown_settings"
      ]
    }
  ],

  "sections": [
    {
      "id": "launch_shortcuts",
      "caption": "起動ショートカット",
      "type": "grid",
      "dataPath": "$.launch_shortcuts",
      "fields": []
    },
    {
      "id": "markdown_settings",
      "caption": "Markdown Studio",
      "type": "form",
      "dataPath": "$.markdown",
      "fields": []
    }
  ]
}
```

この場合でも、

```text
Grid Renderer
Form Renderer
```

は既存実装をそのまま利用する。

---

# 8. 後方互換

`sectionGroups` は任意項目とする。

```text
sectionGroups なし
→ 現行ViewDefと同じ動作

sectionGroups あり
→ Group選択ナビゲーションを有効化
→ 選択GroupのSectionのみ既存Editorへ渡す
```

既存ViewDefを今回の機能追加のために書き換える必要はない。

---

# 9. `sectionGroups` の初期ルール

v0.1では、複雑な機能を持たせず以下を基本ルールとする。

### Group順

`sectionGroups` の配列順を、ナビゲーション表示順とする。

### Section順

`sectionIds` の配列順を、Group内のSection表示順とする。

### Section参照

`sectionIds` に指定するIDは、同一Viewの `sections[].id` に存在しなければならない。

### Section再利用

同じSection IDを複数のSection Groupから参照してよい。

Section定義そのものをコピーしない。

### 未所属Section

`sectionGroups` が存在する場合、原則として全Sectionを1つ以上のGroupから参照する。

未所属Sectionがある場合は、ViewDef検証で警告またはエラー候補とする。

### Renderer

Groupごとの専用Rendererは作らない。

---

# 10. `layout` との関係

`sectionGroups` は既存の `layout` を置き換えない。

初期設計では、

```text
sectionGroups
    ↓
Active Sectionを決定
    ↓
既存layout / Section Renderer
```

という順序で扱う。

つまり、

> `sectionGroups` はRendererの内側へ入り込む機能ではなく、既存Editorへ渡すSectionを外側で選択する機能

とする。

これが「外からつまむ」の具体的な実装境界となる。

---

# 11. App Settingsへの適用

現在の `app_settings.json` には、

```text
hosting
ui
default_launch
markdown
```

が存在する。

今回、`default_launch` は使用せず、

```text
launch_shortcuts
```

へ置き換える。

理由:

```text
自動起動
```

ではなく、

```text
利用者が明示的にクリックして既存Editorを起動するショートカット
```

として扱うため。

---

# 12. `launch_shortcuts`

最小構造案:

```json
{
  "launch_shortcuts": [
    {
      "id": "incident",
      "caption": "インシデント管理",
      "data": "01_main/_studio_work_incident_data_v2.json",
      "view_def": "rules/studio_work_incident_view_def_v0_5.json"
    }
  ]
}
```

役割は、

```text
よく使うData
+
そのDataを表示するViewDef
```

の組を登録すること。

`view_def` の省略・空文字時に既存の自動解決を利用するかは、実装時に既存Resolver契約へ合わせる。

---

## 12.1 登録と実行は別責務

ここは明確に分離する。

```text
⚙ Settings
    ↓
launch_shortcutsを登録・更新する

別途 Shortcut Menu
    ↓
launch_shortcutsを一覧表示する
    ↓
クリック
    ↓
既存JSON Object Studioを起動する
```

Settings画面自身はショートカットを自動実行しない。

また、FRB Studio起動時に `launch_shortcuts` の先頭を自動表示することもしない。

---

# 13. Settings ViewDefの初期イメージ

Settings自体も `sectionGroups` の最初の利用者として構築する。

```json
{
  "id": "app_settings_v0_1",
  "caption": "Studio設定",
  "layout": "standard",

  "sectionGroups": [
    {
      "id": "launch",
      "caption": "ショートカット",
      "sectionIds": [
        "launch_shortcuts"
      ]
    },
    {
      "id": "markdown",
      "caption": "Markdown Studio",
      "sectionIds": [
        "markdown_settings"
      ]
    }
  ],

  "sections": [
    {
      "id": "launch_shortcuts",
      "caption": "起動ショートカット",
      "type": "grid",
      "dataPath": "$.launch_shortcuts",
      "fields": []
    },
    {
      "id": "markdown_settings",
      "caption": "Markdown Studio",
      "type": "form",
      "dataPath": "$.markdown",
      "fields": []
    }
  ]
}
```

この例では、

```text
ショートカットを選択
→ 既存Grid Editor

Markdown Studioを選択
→ 既存Form Editor
```

となる。

Settings専用画面実装は不要。

---

# 14. `app_settings.json` のCanonical

現時点では、

```text
System側 app_settings.json
```

をCanonicalとする。

将来的には、

```text
System app_settings.json
+
User app_settings.json
+
Override Resolution
```

という構造を持つ可能性はある。

ただし、

> **利用者別 `app_settings.json` によるOverride構造は現時点では考えない。**

これを今回の明示的な制約とする。

---

# 15. System Definitionの配置

Settings用ViewDef / Field Definitionは、ユーザーが管理する、

```text
defs
fielddefs
```

へ置かない。

これらはユーザーエリアとして扱う。

Settingsを成立させるDefinitionはStudio本体が所有するため、

```text
wwwroot/config
```

付近のSystem領域へ収録する。

配置イメージ:

```text
wwwroot/
  config/
    app_settings.json

    app_settings/
      app_settings_view_def_v0_1.json
      app_settings_field_definitions_v0_1.json
```

具体的なサブフォルダ名は実装時に確定してよい。

重要なのは、

```text
defs / fielddefs
= ユーザー定義

wwwroot/config付近
= Studio自身を成立させるSystem定義
```

という所有境界を維持すること。

---

# 16. 保存責務

現行Native Shellでは `wwwroot/config` は通常の `writable_roots` に含まれていない。

一方、今回更新したい対象はSystem設定である、

```text
wwwroot/config/app_settings.json
```

のみ。

そのため初期設計では、

> **`wwwroot/config` 全体を一般的なユーザー書込領域へ昇格させるのではなく、`app_settings.json` を対象とした固定保存契約を設ける。**

方向を優先する。

概念:

```text
Settings Editor
      ↓
App Settings Save Contract
      ↓
固定対象:
wwwroot/config/app_settings.json
```

具体的なNative Shellコマンド名 / API形式は実装設計時に決定する。

---

# 17. Field Definition

Settingsで使用する入力制約は、Settings専用JavaScriptへ直接記述せず、System側Field Definitionとして定義する。

例:

```text
launch_shortcuts[].id
launch_shortcuts[].caption
launch_shortcuts[].data
launch_shortcuts[].view_def

markdown.large_file_warning_enabled
markdown.large_file_warning_bytes
```

Validationは既存のDefinition Driven Validation機構を再利用する。

Settings専用Validatorは原則作らない。

---

# 18. Settingsの初期表示対象

初期段階では、利用者が変更する必要があるものだけをViewへ露出する。

例:

```text
ショートカット
  launch_shortcuts

Markdown Studio
  large_file_warning_enabled
  large_file_warning_bytes
```

現在存在する、

```text
hosting
ui
```

はDataとして保持しても、Settings Viewへ表示する必要はない。

原則:

> **Dataに存在することと、設定画面から変更可能であることは別。**

---

# 19. Round Trip

Settings Viewへ表示していない `app_settings.json` の項目は、保存時に削除しない。

```text
Read Canonical JSON
        ↓
表示・編集対象Fieldのみ更新
        ↓
未表示Fieldを保持
        ↓
Canonical JSONへ保存
```

とする。

---

# 20. `sectionGroups` のSettings以外への利用

`sectionGroups` はSettings専用機能ではない。

例えば将来、

```text
Field Definition Editor

基本情報
Constraint
Generated Test
Runtime Validation
```

や、

```text
Incident Editor

概要
判断
後続対応
テスト
Evidence
```

のように、同じDataを複数の表示単位へ分ける場合にも利用できる。

つまり、

```text
1 Data
+
1 ViewDef
+
複数Section
+
sectionGroups
```

から、

```text
利用目的別の複数View Projection
```

を作ることができる。

---

# 21. やらないこと

今回のスコープでは、以下を行わない。

```text
Settings専用Editorを作る
Settings専用Rendererを作る
設定カテゴリごとのHTMLを作る
設定カテゴリごとのJavaScript分岐を増やす
default_launchによる自動起動
launch_shortcutsをSettings画面から自動実行する
User app_settings.json Overrideを作る
defs / fielddefsへSystem Settings Definitionを配置する
sectionGroupsのために既存sections構造を置き換える
sectionGroupsのために既存Rendererを複製する
```

---

# 22. 実装フェーズ案

## Phase 1 — ViewDef拡張

```text
ViewDef SchemaへsectionGroups追加
sectionGroups / sectionIds検証
既存ViewDef後方互換確認
```

## Phase 2 — 標準Editor Group Navigation

```text
sectionGroups認識
Group選択UI
Active sectionIds解決
既存Editor / Rendererへの接続
```

この段階でSettingsとは無関係なサンプルViewDefでも動作確認する。

## Phase 3 — App Settings Definition

```text
default_launch → launch_shortcutsへ変更
System側Settings ViewDef
System側Settings Field Definition
SettingsをsectionGroupsで表示
```

## Phase 4 — App Settings Save

```text
app_settings.json固定保存契約
Validation
Round Trip
updated_at更新
```

## Phase 5 — Shortcut Launcher

```text
launch_shortcuts読込
Shortcut Menu表示
クリックで既存Editor起動
```

Shortcut LauncherはSettings Editorとは別責務として実装する。

---

# 23. 受入観点

最低限、以下を満たすこと。

### ViewDef

- `sectionGroups` がない既存ViewDefは従来通り表示される
- `sectionGroups` があるViewDefではGroup Navigationが表示される
- Group選択時に指定 `sectionIds` のSectionだけが表示される
- Form SectionとGrid Sectionの両方をGroup化できる
- 同じSectionを複数Groupから参照できる
- 存在しない `sectionIds` はViewDef検証で検出される

### Settings

- `app_settings.json` がCanonicalである
- `launch_shortcuts` を登録・更新できる
- Markdown設定を登録・更新できる
- 非表示設定値が保存時に失われない
- Settings専用Rendererを使用しない

### Shortcut

- `launch_shortcuts` は自動起動しない
- 別のShortcut Menuから利用者が明示的に起動する
- Shortcut選択後は既存Editorの起動経路を利用する

---

# 24. 設計の一言要約

> **Settings専用画面を作るのではなく、ViewDefへ `sectionGroups` を追加し、既存Sectionを外からつまんで表示単位を作る。Settingsはその最初の利用例とする。**

---

# 25. 今回生まれた設計パターン

## Pinch from the Outside — 外からつまむ

```text
既存構造
  ├─ A
  ├─ B
  ├─ C
  └─ D

      ↑ 外からつまむ

外部定義
  ├─ 用途1 → A + B
  └─ 用途2 → C + D
```

レビュー時の問い:

> **それ、外からつまめんのかい？**

既存構造をなるべく壊したくない状況では、

> **外からつまむことを優先する。**

これをFRB Studioの設計判断軸として扱う。
