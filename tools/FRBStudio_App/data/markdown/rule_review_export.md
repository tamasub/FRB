# ルールレビュー記録

- 出力日時: 2026/6/25 21:30:31
- 対象: FRB Studio / JSON Object Studio
- schema_version: rule_review_data_v0_1
- status: converted_draft
- 件数: 20

## 基本情報

- タイトル: FRB Studio Foundation Review Data
- 対象: FRB Studio / JSON Object Studio
- ドメイン: frb_studio_foundation
- Schema Version: rule_review_data_v0_1
- Document Type: rule_review_data
- 状態: converted_draft
- 元ドキュメント: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- Source Version: v0.1
- Introduced In: v0.4-r001
- 生成日時: 2026-06-22T12:24:16+09:00
- ルール数: 19
- 承認済み数: 0

### 承認方針

各ルールは人間が内容確認し、verification_status を確認済みにしたうえで approval_decision を承認する。AIはレビューコメント案を出せるが、承認判断は人間が行う。

### 変換メモ

FRB Studio / JSON Object Studio の命名・設定・バージョン・インシデント・ルール管理・Markdown Export に関する基本原則を、共通ルールレビューViewDefで扱えるように rules 配列へ構造化したData JSON。Markdownは原本ではなく、このJSONの出力Viewとして扱う想定。

### 前文

このData JSONは、FRB Studio / JSON Object Studio の土台となる運用原則を管理するためのレビュー対象データである。

Markdownを原本にせず、構造化できるルール・制約・判断理由はData JSONを原本として管理する。

Data JSONをViewDefで表示・編集し、Markdownは必要に応じてExport Viewとして生成する。

### 変更履歴方針

ルール本文、要約、カテゴリ、優先度、承認判断を変更した場合は、各 rule.change_history に変更前後・理由・会話を残す。

## ルールレビュー一覧

| No. | 章番号 | Rule ID | 親Rule ID | 分類 | ルール名 | 優先度 | レビュー状態 | 確認状態 | 承認 | 要約 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | foundation_rule_001 |  | 運用 | FRB Studio の位置づけ | high | 未レビュー | 確認済み | 承認する | FRB Studio は、JSON Object Studio を含む Studio 系ツール群の共通ブランド名として扱う。 |
| 2 | 2 | foundation_rule_002 |  | 運用 | JSON Object Studio の正式名称 | high | 未レビュー | 確認済み | 承認する | 現在のプロダクト名は JSON Object Studio とする。 |
| 3 | 3 | foundation_rule_003 |  | 運用 | 画面表示名 | high | 未レビュー | 確認済み | 承認する | 画面上では FRB Studio / JSON Object Studio / 表示バージョン / タグラインを表示する。 |
| 4 | 4 | foundation_rule_004 |  | 運用 | app_info.json の役割 | high | 未レビュー | 確認済み | 承認する | app_info.json はアプリの名札として、現在の名称・表示バージョン・タグラインのみを持つ。 |
| 5 | 5 | foundation_rule_005 |  | 運用 | app_settings.json の役割 | medium | 未レビュー | 確認済み | 承認する | システム全体の動作パラメータは app_settings.json に分離する。 |
| 6 | 6 | foundation_rule_006 |  | 運用 | Version / Revision / Phase の分離 | high | 未レビュー | 確認済み | 承認する | Version、Revision、Phase は混ぜず、それぞれ別の意味として扱う。 |
| 7 | 7 | foundation_rule_007 |  | 運用 | Incident と Version Detail の関係 | high | 未レビュー | 確認済み | 承認する | Incident は「なぜやるのか」、Version Detail は「何を入れたのか」を記録する。 |
| 8 | 8 | foundation_rule_008 |  | 原則 | Markdownを原本にしない | high | 未レビュー | 確認済み | 承認する | 構造化できるルール・制約・レビュー・判断理由は、Markdownではなく Data JSON を原本とする。 |
| 9 | 9 | foundation_rule_009 |  | 原則 | ルール系データはドメイン別Data JSONで管理する | high | 未レビュー | 確認済み | 承認する | 憲法、制約、ViewDef生成ルール、Studio運用原則などのルール系データは、ドメインごとに Data JSON を分ける。 |
| 10 | 10 | foundation_rule_010 |  | 基本構造 | ViewDefは構造が同じなら共通化する | high | 未レビュー | 確認済み | 承認する | ルール系Data JSONはドメインごとに分けるが、レビュー対象としての基本構造が同じ場合、ViewDefは共通化してよい。 |
| 11 | 11 | foundation_rule_011 |  | 運用 | rules フォルダーの役割 | medium | 未レビュー | 確認済み | 承認する | ルール・制約・憲法レビュー系の ViewDef / Data JSON / Export は、rules フォルダー配下で管理する。 |
| 12 | 12 | foundation_rule_012 |  | 運用 | 日本語JSONの可読性 | high | 未レビュー | 確認済み | 承認する | Data JSONは人間が直接読む可能性があるため、日本語をUnicodeエスケープした状態で保存しない。 |
| 13 | 13 | foundation_rule_013 |  | Markdown | Markdown Export の位置づけ | high | 未レビュー | 確認済み | 承認する | Markdown Export は、Data JSON の表示用Viewである。 |
| 14 | 14 | foundation_rule_014 |  | 原則 | FRB Studio の基本思想 | high | 未レビュー | 確認済み | 承認する | FRB Studio / JSON Object Studio は、JSONで思考を構造化し、AIとの文脈を育てるためのStudioである。 |
| 15 | 15 | foundation_rule_015 |  | 基本構造 | Data / View / Export の原則 | high | 未レビュー | 確認済み | 承認する | Data JSON、ViewDef JSON、Markdown Export、Git Diff、AI、Human の役割を分ける。 |
| 16 | 16 | foundation_rule_016 |  | 原則 | 承認判断は人間が行う | high | 未レビュー | 確認済み | 承認する | AIはレビューを支援するが、採用可否・承認・保留・差戻しの最終判断は人間が行う。 |
| 17 | 17 | foundation_rule_017 |  | 運用 | v0.4-r001 の意味 | high | 未レビュー | 確認済み | 承認する | v0.4-r001 は、JSON Object Studio としての正式命名、およびバージョン・リビジョン・インシデント・ルール管理の整理を開始したリビジョンとして扱う。 |
| 18 | 18 | foundation_rule_018 |  | 運用 | AI作業ファイル記録とインシデント回答記録 | high | 未レビュー | 確認済み | 承認する | AIが作業で更新したファイル・変更理由・対応結果を、インシデントJSONへ自然文中心で残す。root data/defs は必要時更新可、wwwroot/data/defs は公開用として保護する。 |
| 19 |  | row_copy_1 |  | 運用 | ★マークダウン　入力テストデータ | high | 未レビュー | 未確認 | 未承認 | # 見出し<br>## 見出し<br>- 箇条書き<br>1. 番号付きリスト |
| 20 | 19 | foundation_rule_019 |  | 運用 | GitHub基準ソースとZIP返却契約 | high | 未レビュー | 確認済み | 承認する | AI作業では、GitHub main を基準ソースとし、依頼は incident_file と phase を中心に行う。返却物は data / defs / wwwroot 階層のZIPとし、更新済みインシデントJSONを data/json/01_main に含める。取得時は tree/blob URL と raw/archive URL を用途で使い分ける。 |

## ルールレビュー詳細


### 1 FRB Studio の位置づけ
- Rule ID: foundation_rule_001
- 分類: 運用
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- 元行: 0

#### レビュー対象


##### 元見出し

1. FRB Studio の位置づけ

##### 要約

FRB Studio は、JSON Object Studio を含む Studio 系ツール群の共通ブランド名として扱う。

##### ルール本文

FRB Studio は、JSON Object Studio を含む Studio 系ツール群の共通ブランド名として扱う。

JSON Object Studio は、FRB Studio の中にある現在の主要プロダクトである。

将来的に Markdown Studio、Diff Studio、FFT Studio などの派生ツールが増えても、共通ブランドは FRB Studio とする。

理由:
FRB Studio は単一ツール名ではなく、FRB研究から生まれた知識管理・差分管理・AI協働支援ツール群の総称として育てるため。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 変更履歴

（なし）

### 2 JSON Object Studio の正式名称
- Rule ID: foundation_rule_002
- 分類: 運用
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- 元行: 0

#### レビュー対象


##### 元見出し

2. JSON Object Studio の正式名称

##### 要約

現在のプロダクト名は JSON Object Studio とする。

##### ルール本文

現在のプロダクト名は JSON Object Studio とする。

この名前は、単なる JSON エディターではなく、思考・制約・差分・レビュー・テスト・インシデント・物語などを JSON オブジェクトとして扱う Studio であることを表す。

旧称の No-Code JSON Studio は、必要に応じて過去名として扱うが、今後の正式表示では使用しない。

理由:
「No-Code」は便利な説明ではあるが、現在のStudioくんの本質はノーコードではなく、JSONオブジェクトとして思考や文脈を構造化することにあるため。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 変更履歴

（なし）

### 3 画面表示名
- Rule ID: foundation_rule_003
- 分類: 運用
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- 元行: 0

#### レビュー対象


##### 元見出し

3. 画面表示名

##### 要約

画面上では FRB Studio / JSON Object Studio / 表示バージョン / タグラインを表示する。

##### ルール本文

画面上では、以下の構成で表示する。

FRB Studio  
JSON Object Studio v0.4-r001

JSONで思考を構造化し、AIとの文脈を育てる。

ただし、バージョン表記は主役ではない。画面上ではフォントを小さくし、薄めに表示する。

主役は JSON Object Studio であり、バージョンは成長履歴の名札として扱う。

理由:
ユーザーが最初に認識すべきものはプロダクト名と思想であり、バージョン番号ではないため。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 変更履歴

（なし）

### 4 app_info.json の役割
- Rule ID: foundation_rule_004
- 分類: 運用
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- 元行: 0

#### レビュー対象


##### 元見出し

4. app_info.json の役割

##### 要約

app_info.json はアプリの名札として、現在の名称・表示バージョン・タグラインのみを持つ。

##### ルール本文

`app_info.json` はアプリの名札として扱う。

保持する情報は、現在のブランド名、プロダクト名、version、revision、display_version、tagline、status 程度に限定する。

`app_info.json` に、動作設定、履歴、インシデント、リリース詳細、画面定義ルールを混在させない。

`app_info.json` は「今このアプリは何者か」を示すためのファイルである。

理由:
名札ファイルに設定や履歴を混ぜると、役割が曖昧になり、将来的に管理が破綻するため。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 変更履歴

（なし）

### 5 app_settings.json の役割
- Rule ID: foundation_rule_005
- 分類: 運用
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- 元行: 0

#### レビュー対象


##### 元見出し

5. app_settings.json の役割

##### 要約

システム全体の動作パラメータは app_settings.json に分離する。

##### ルール本文

システム全体の動作パラメータが必要になった場合は、`app_info.json` ではなく `app_settings.json` に分離する。

`app_settings.json` には、API優先か静的JSON優先か、デフォルトData/ViewDef、機能ON/OFF、UI設定、パス設定などを持たせる。

`app_info` は「何者か」、`app_settings` は「どう動くか」を表す。

理由:
表示上の名札と動作設定を分けることで、アプリ構成を読みやすくし、将来的な拡張に耐えられるようにするため。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 変更履歴

（なし）

### 6 Version / Revision / Phase の分離
- Rule ID: foundation_rule_006
- 分類: 運用
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- 元行: 0

#### レビュー対象


##### 元見出し

6. Version / Revision / Phase の分離

##### 要約

Version、Revision、Phase は混ぜず、それぞれ別の意味として扱う。

##### ルール本文

Version、Revision、Phase は混ぜない。

Version はプロダクトとしての節目を表す。

Revision は同一Version内の細かい更新単位を表す。

Phase は作業テーマや開発フェーズを表す。

例:

- Version: v0.4
- Revision: r001
- Display Version: v0.4-r001
- Phase: json-object-studio-branding
- Phase: versioned-incident-management

理由:
Phase に `v0.8-url-param-launch-load` のような値を入れると、バージョンと作業テーマが混在し、後から履歴を追いにくくなるため。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 変更履歴

（なし）

### 7 Incident と Version Detail の関係
- Rule ID: foundation_rule_007
- 分類: 運用
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- 元行: 0

#### レビュー対象


##### 元見出し

7. Incident と Version Detail の関係

##### 要約

Incident は「なぜやるのか」、Version Detail は「何を入れたのか」を記録する。

##### ルール本文

Incident は「なぜやるのか」を記録する。

Version Detail は「そのVersion/Revisionに何を入れたのか」を記録する。

Incident と Version Detail は ID で紐づける。

Incident には、発見バージョン、対応予定バージョン、対応完了バージョンを持たせる。

例:

- found_in_version
- target_version
- fixed_in_version

理由:
不具合、違和感、改善要望、作業課題と、実際にリリースへ含まれた変更内容は別物であるため。

### v0.12追記：Incident JSONはAI作業台帳でもある

Incident JSON は、作業依頼・対象ファイル・実更新ファイル・変更理由・対応結果・AI完了報告を残す作業台帳でもある。

ただし、最初から管理項目を増やしすぎない。まずは `target_files`、`latest_ai_response`、`discussion_history`、`change_history` など既存の記録場所へ、テキスト文章として残す運用を優先する。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_foundation_rule_007_v012_redo_001 |  |  |  | body_append |  |  |  | v0.12 FRBコメントで、更新した痕跡をインシデントJSONに残したいという意図が確認されたため。 |

### 8 Markdownを原本にしない
- Rule ID: foundation_rule_008
- 分類: 原則
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- 元行: 0

#### レビュー対象


##### 元見出し

8. Markdownを原本にしない

##### 要約

構造化できるルール・制約・レビュー・判断理由は、Markdownではなく Data JSON を原本とする。

##### ルール本文

構造化できるルール・制約・レビュー・判断理由は、Markdownを原本にしない。

原本は Data JSON とする。

Markdown は Data JSON から生成される表示用 Export View として扱う。

理由:
Markdownを原本にすると、構造化されたレビュー、承認状態、変更履歴、差分管理が難しくなるため。

また、過去に Markdown Export を原本と誤認しそうになったため、明確に役割を分離する。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 変更履歴

（なし）

### 9 ルール系データはドメイン別Data JSONで管理する
- Rule ID: foundation_rule_009
- 分類: 原則
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- 元行: 0

#### レビュー対象


##### 元見出し

9. ルール系データはドメイン別Data JSONで管理する

##### 要約

憲法、制約、ViewDef生成ルール、Studio運用原則などのルール系データは、ドメインごとに Data JSON を分ける。

##### ルール本文

憲法、制約、ViewDef生成ルール、Studio運用原則などのルール系データは、ドメインごとに Data JSON を分ける。

例:

- `coding_constraints_review_data_v0_3.json`
- `frb_studio_foundation_review_data_v0_1.json`
- `frb_viewdef_generation_rules_review_data_v0_1.json`

理由:
ドメインが違うルールを1つのData JSONに混ぜると、目的、責任範囲、更新履歴が曖昧になるため。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 変更履歴

（なし）

### 10 ViewDefは構造が同じなら共通化する
- Rule ID: foundation_rule_010
- 分類: 基本構造
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- 元行: 0

#### レビュー対象


##### 元見出し

10. ViewDefは構造が同じなら共通化する

##### 要約

ルール系Data JSONはドメインごとに分けるが、レビュー対象としての基本構造が同じ場合、ViewDefは共通化してよい。

##### ルール本文

ルール系Data JSONはドメインごとに分ける。

ただし、レビュー対象としての基本構造が同じ場合、ViewDefは共通化してよい。

共通ルールレビューViewDefとして、`rule_review_common_view_def_v0_1.json` を使用する。

Data JSON 側は、レビュー対象配列を `rules` に揃える。

理由:
データはドメインで分け、ViewDefは構造で共有することで、重複した画面定義を減らし、レビュー体験を統一できるため。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 変更履歴

（なし）

### 11 rules フォルダーの役割
- Rule ID: foundation_rule_011
- 分類: 運用
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- 元行: 0

#### レビュー対象


##### 元見出し

11. rules フォルダーの役割

##### 要約

ルール・制約・憲法レビュー系の ViewDef / Data JSON / Export は、rules フォルダー配下で管理する。

##### ルール本文

ルール・制約・憲法レビュー系の ViewDef / Data JSON / Export は、rules フォルダー配下で管理する。

推奨構成:

- `wwwroot/defs/rules/`
- `wwwroot/data/rules/`
- `wwwroot/exports/rules/`

フォルダー名はURLやGitHub Pagesでの扱いやすさを考慮し、小文字 `rules` を基本とする。

理由:
ルール系ファイルを通常の業務データや画面定義と混在させると、原本と出力、専用ViewDefと共通ViewDefの区別がつきにくくなるため。

### v0.12追記：root data/defs と wwwroot/data/defs の役割分離

root `data/` / `defs/` は、作業用・管理用の Data JSON / ViewDef JSON を置く場所であり、作業目的に必要な場合はAIが更新してよい。

`wwwroot/data` / `wwwroot/defs` は、GitHub Pages等の公開用静的ホスティング領域として扱う。明示依頼がない限り、AIは更新しない。

AIが root `data/` / `defs/` を更新した場合は、どのファイルを更新したか、なぜ更新したか、結果どうなったかをインシデントJSONへ残す。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_foundation_rule_011_v012_redo_001 |  |  |  | body_append |  |  |  | root data/defs まで一律更新禁止にするのは強すぎるというユーザーコメントを反映するため。 |

### 12 日本語JSONの可読性
- Rule ID: foundation_rule_012
- 分類: 運用
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- 元行: 0

#### レビュー対象


##### 元見出し

12. 日本語JSONの可読性

##### 要約

Data JSONは人間が直接読む可能性があるため、日本語をUnicodeエスケープした状態で保存しない。

##### ルール本文

Data JSONは人間が直接読む可能性があるため、日本語をUnicodeエスケープした状態で保存しない。

JSON保存時は UTF-8 で、日本語がそのまま読める形式を基本とする。

Pythonで生成する場合は `ensure_ascii=false` 相当の指定を使う。

.NETで生成する場合は、日本語を過剰に `\uXXXX` へ変換しない保存設定を使用する。

理由:
JSONは原本であり、人間も読む対象である。

日本語が `\u306E\u547D...` のように保存されると、JSONとしては正しくても、人間にとっての可読性が大きく下がるため。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 変更履歴

（なし）

### 13 Markdown Export の位置づけ
- Rule ID: foundation_rule_013
- 分類: Markdown
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- 元行: 0

#### レビュー対象


##### 元見出し

13. Markdown Export の位置づけ

##### 要約

Markdown Export は、Data JSON の表示用Viewである。

##### ルール本文

Markdown Export は、Data JSON の表示用Viewである。

Markdown Export は、人間が読みやすく確認するため、またAIへ文脈として渡すために生成する。

ただし、Markdown Export を直接編集して原本として扱ってはいけない。

Markdown側には、原本Data JSONのファイル名を明記する。

理由:
Markdownは読みやすいが、構造化レビュー、承認状態、変更履歴、差分管理にはData JSONの方が適しているため。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 変更履歴

（なし）

### 14 FRB Studio の基本思想
- Rule ID: foundation_rule_014
- 分類: 原則
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- 元行: 0

#### レビュー対象


##### 元見出し

14. FRB Studio の基本思想

##### 要約

FRB Studio / JSON Object Studio は、JSONで思考を構造化し、AIとの文脈を育てるためのStudioである。

##### ルール本文

FRB Studio / JSON Object Studio は、JSONで思考を構造化し、AIとの文脈を育てるためのStudioである。

扱う対象は、データだけではない。

制約、差分、レビュー、テスト、インシデント、ルール、物語、知識、判断理由も JSON Object として扱う。

理由:
Studioくんの本質は、JSON編集そのものではなく、人間とAIが共有できる文脈を構造化し、継続的に育てることにあるため。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 変更履歴

（なし）

### 15 Data / View / Export の原則
- Rule ID: foundation_rule_015
- 分類: 基本構造
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- 元行: 0

#### レビュー対象


##### 元見出し

15. Data / View / Export の原則

##### 要約

Data JSON、ViewDef JSON、Markdown Export、Git Diff、AI、Human の役割を分ける。

##### ルール本文

FRB Studioでは、以下の役割分担を基本とする。

Data JSON は原本である。

ViewDef JSON は表示・編集・レビュー体験を定義する。

Markdown Export は表示用・共有用の出力である。

Git Diff は差分観測のために使う。

AI はData JSONやMarkdown Exportをもとに、仮説生成、レビュー、要約、差分解釈を行う。

Human は違和感を回収し、最終判断を行う。

理由:
この役割分担により、JSON原本、画面表示、Markdown共有、AI協働、人間レビューの責任範囲が明確になるため。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 変更履歴

（なし）

### 16 承認判断は人間が行う
- Rule ID: foundation_rule_016
- 分類: 原則
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- 元行: 0

#### レビュー対象


##### 元見出し

16. 承認判断は人間が行う

##### 要約

AIはレビューを支援するが、採用可否・承認・保留・差戻しの最終判断は人間が行う。

##### ルール本文

AIはレビューコメント案、改善案、矛盾指摘、要約、分類案を出せる。

ただし、ルールの採用可否、承認、保留、差戻しの最終判断は人間が行う。

AIの出力は判断材料であり、判断そのものではない。

理由:
FRB StudioはAI協働を前提とするが、制約とルールの責任は人間が持つ必要があるため。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 変更履歴

（なし）

### 17 v0.4-r001 の意味
- Rule ID: foundation_rule_017
- 分類: 運用
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md
- 元行: 0

#### レビュー対象


##### 元見出し

17. v0.4-r001 の意味

##### 要約

v0.4-r001 は、JSON Object Studio としての正式命名、およびバージョン・リビジョン・インシデント・ルール管理の整理を開始したリビジョンとして扱う。

##### ルール本文

v0.4-r001 は、JSON Object Studio としての正式命名、およびバージョン・リビジョン・インシデント・ルール管理の整理を開始したリビジョンとして扱う。

このリビジョンでは、少なくとも以下を含む。

- FRB Studio / JSON Object Studio の表示名整理
- app_info.json の導入
- app_settings.json の将来分離方針
- Version / Revision / Phase の分離
- Incident / Version Detail の関係整理
- Markdownを原本にしない原則
- ルール系Data JSONと共通ViewDefの方針
- 日本語JSONの可読性方針

理由:
v0.4-r001 は、Studioくんが単なるJSON編集ツールから、自分自身の名前・ルール・履歴を管理し始める節目であるため。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 変更履歴

（なし）

### 18 AI作業ファイル記録とインシデント回答記録
- Rule ID: foundation_rule_018
- 分類: 運用
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB Studio Foundation Rules
- 元行: 0

#### レビュー対象


##### 元見出し

18. AI作業ファイル記録とインシデント回答記録

##### 要約

AIが作業で更新したファイル・変更理由・対応結果を、インシデントJSONへ自然文中心で残す。root data/defs は必要時更新可、wwwroot/data/defs は公開用として保護する。

##### ルール本文

AIがData JSON、Defs JSON、Rules JSON、Incident JSON、Markdownプロンプト等を更新した場合、更新したファイル、変更理由、変更概要、対応結果を該当インシデントJSONへ記録する。

記録はまずテキスト文章でよい。専用フィールドを増やしすぎず、`target_files`、`latest_ai_response`、`discussion_history`、`change_history` など、既存の記録場所へ人間とAIが後から読める形で残す。

root `data/` / `defs/` は一律変更禁止ではなく、作業目的に必要な場合は更新可能とする。特に `data/json/01_main/studio_work_incident_data_*.json` は、作業結果を収録するためにAIが更新する対象になり得る。

`wwwroot/data` / `wwwroot/defs` はGitHub Pages等の公開用静的領域として扱うため、明示依頼がない限り更新しない。

インシデント対応後のAI完了報告は、会話上だけでなく `latest_ai_response` 等に残す。

##### 確認メッセージ

Foundation Rule 18「AI作業ファイル記録とインシデント回答記録」をレビューする。

#### レビュー会話


#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_foundation_rule_018_v012_001 |  |  |  | rule_added |  |  |  | v0.12-rules-update-reporting-policy をStudio運用の基礎ルールとして定着させるため。 |
| chg_foundation_rule_018_v012_redo_001 |  |  |  | body_refine |  |  |  | v0.12 FRBコメントで、管理項目を抑えつつ更新痕跡を残す方針に修正されたため。 |

### ★マークダウン 入力テストデータ
- Rule ID: row_copy_1
- 分類: 運用
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認
- 元行: 0

#### レビュー対象


##### 元見出し

# 見出し
## 見出し
- 箇条書き
1. 番号付きリスト

##### 要約

# 見出し
## 見出し
- 箇条書き
1. 番号付きリスト

##### ルール本文

# 見出し
## 見出し
- 箇条書き
1. 番号付きリスト
> 引用
`inline code`
**太字**


```
やばいっす


```


![alt text](./images/chat/tamasub.png)

#### レビュー会話


#### 変更履歴

（なし）

### 19 GitHub基準ソースとZIP返却契約
- Rule ID: foundation_rule_019
- 分類: 運用
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB Studio Foundation Rules
- 元行: 0

#### レビュー対象


##### 元見出し

19. GitHub基準ソースとZIP返却契約

##### 要約

AI作業では、GitHub main を基準ソースとし、依頼は incident_file と phase を中心に行う。返却物は data / defs / wwwroot 階層のZIPとし、更新済みインシデントJSONを data/json/01_main に含める。取得時は tree/blob URL と raw/archive URL を用途で使い分ける。

##### ルール本文

FRB Studio / JSON Object Studio のAI作業では、原則として GitHub main の最新ソースを基準ソースとして扱う。

ユーザーは毎回ソースZIPを添付するのではなく、incident_file と phase を指定して作業を依頼できるようにする。

AIは、指定された incident_file を読み、work_items[] から phase が一致する作業項目を探し、その objective / scope / user_request / latest_user_comment / decision_log / test_points を正として作業内容を判断する。

phase が見つからない場合、または作業内容が特定できない場合は、推測で実装せず確認する。

返却は原則ZIPとし、ZIP直下の基本階層は以下とする。

- data/
- defs/
- wwwroot/

修正したファイルは、FRBStudio_App配下と同じ相対パスで格納する。

更新済みインシデント管理JSONは、必ず data/json/01_main/ に格納する。

インシデントJSONには、AIが更新したファイル、変更理由、変更概要、確認ポイントを latest_ai_response / discussion_history / change_history へ残す。

wwwroot/data と wwwroot/defs は公開用静的領域として扱い、明示依頼がない限り更新しない。

Program.cs など FRBStudio 本体側の更新が必要な場合は、返却前に配置方針と更新対象を明示する。

理由:
毎回ソースZIPを添付する運用では、依頼準備が重く、AIとの協働が作業単位ではなくファイル受け渡し単位になってしまう。
GitHub main を基準ソースとし、インシデントJSONを作業台帳として使うことで、作業依頼、実装、返却、履歴記録を一つの運用契約として安定させるため。

### GitHub取得URLの標準

AIがGitHub上の基準ソースを取得する場合は、用途に応じて以下のURLを使い分ける。

人間がブラウザで確認するためのtree/blob URL:

- FRBStudio 本体: https://github.com/tamasub/FRB/tree/main/tools/FRBStudio
- FRBStudio_App: https://github.com/tamasub/FRB/tree/main/tools/FRBStudio_App
- Foundation Rules: https://github.com/tamasub/FRB/blob/main/tools/FRBStudio_App/data/json/00_rules/frb_studio_foundation_review_data_v0_1.json

AIやスクリプトが直接取得するためのraw/archive URL:

- リポジトリ main ZIP: https://github.com/tamasub/FRB/archive/refs/heads/main.zip
- FRBStudio_App raw base: https://raw.githubusercontent.com/tamasub/FRB/main/tools/FRBStudio_App/
- FRBStudio 本体 raw base: https://raw.githubusercontent.com/tamasub/FRB/main/tools/FRBStudio/
- Foundation Rules raw: https://raw.githubusercontent.com/tamasub/FRB/main/tools/FRBStudio_App/data/json/00_rules/frb_studio_foundation_review_data_v0_1.json

incident_file は FRBStudio_App からの相対パスとして扱う。
たとえば `incident_file: data/json/01_main/studio_work_incident_data_xxx.json` が指定された場合、raw URL は以下の形式で解決する。

`https://raw.githubusercontent.com/tamasub/FRB/main/tools/FRBStudio_App/{incident_file}`

個別ファイルを直接取得できない場合、またはHTMLなど大きなファイルの完全取得が不安定な場合は、リポジトリ main ZIP を取得し、展開後の `FRB-main/tools/FRBStudio_App/` または `FRB-main/tools/FRBStudio/` を基準として作業する。

GitHubのtree/blob URLは閲覧用であり、機械取得や完全ファイル取得にはraw URLまたはmain ZIPを優先する。

##### 確認メッセージ

Foundation Rule 19「GitHub基準ソースとZIP返却契約」をレビューする。

##### メモ

GitHub上の閲覧用URLだけでは大きなHTML等の完全取得が不安定な場合があるため、raw URLとmain ZIP URLを標準取得URLとして追記。

#### レビュー会話


#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_foundation_rule_019_v0138_001 |  |  |  | rule_added |  |  |  | ソースZIP添付運用から卒業し、インシデントJSONを中心にAI作業を依頼・記録・返却できるようにするため。 |
| chg_foundation_rule_019_v0138_002 |  |  |  | body_append |  |  |  | GitHub基準運用で、大きなHTMLファイル等をAIが完全取得できない場合に備え、作業依頼プロンプトから安定してソース取得へ辿れるようにするため。 |

---

# AI貼り付け用

## ルールレビュー コメント生成プロンプト

<details open>
<summary>プロンプト + TSV を表示</summary>

```text
以下はルールレビュー一覧のTSVです。
この内容をもとに、未承認・差戻し・未確認のルールについて、レビューコメント案を作成してください。

条件:
- ルールの思想を壊さない
- 修正が必要な場合のみ提案する
- Data JSONを原本、MarkdownをExport Viewとして扱う前提を守る
- approval_decision を勝手に承認へ変更しない
- 出力はコメント候補だけにする

TSV:
No.	Rule ID	章番号	分類	ルール名	優先度	レビュー状態	確認状態	承認	要約	人間コメント	AI回答
1	foundation_rule_001	1	運用	FRB Studio の位置づけ	high	未レビュー	確認済み	承認する	FRB Studio は、JSON Object Studio を含む Studio 系ツール群の共通ブランド名として扱う。		
2	foundation_rule_002	2	運用	JSON Object Studio の正式名称	high	未レビュー	確認済み	承認する	現在のプロダクト名は JSON Object Studio とする。		
3	foundation_rule_003	3	運用	画面表示名	high	未レビュー	確認済み	承認する	画面上では FRB Studio / JSON Object Studio / 表示バージョン / タグラインを表示する。		
4	foundation_rule_004	4	運用	app_info.json の役割	high	未レビュー	確認済み	承認する	app_info.json はアプリの名札として、現在の名称・表示バージョン・タグラインのみを持つ。		
5	foundation_rule_005	5	運用	app_settings.json の役割	medium	未レビュー	確認済み	承認する	システム全体の動作パラメータは app_settings.json に分離する。		
6	foundation_rule_006	6	運用	Version / Revision / Phase の分離	high	未レビュー	確認済み	承認する	Version、Revision、Phase は混ぜず、それぞれ別の意味として扱う。		
7	foundation_rule_007	7	運用	Incident と Version Detail の関係	high	未レビュー	確認済み	承認する	Incident は「なぜやるのか」、Version Detail は「何を入れたのか」を記録する。		
8	foundation_rule_008	8	原則	Markdownを原本にしない	high	未レビュー	確認済み	承認する	構造化できるルール・制約・レビュー・判断理由は、Markdownではなく Data JSON を原本とする。		
9	foundation_rule_009	9	原則	ルール系データはドメイン別Data JSONで管理する	high	未レビュー	確認済み	承認する	憲法、制約、ViewDef生成ルール、Studio運用原則などのルール系データは、ドメインごとに Data JSON を分ける。		
10	foundation_rule_010	10	基本構造	ViewDefは構造が同じなら共通化する	high	未レビュー	確認済み	承認する	ルール系Data JSONはドメインごとに分けるが、レビュー対象としての基本構造が同じ場合、ViewDefは共通化してよい。		
11	foundation_rule_011	11	運用	rules フォルダーの役割	medium	未レビュー	確認済み	承認する	ルール・制約・憲法レビュー系の ViewDef / Data JSON / Export は、rules フォルダー配下で管理する。		
12	foundation_rule_012	12	運用	日本語JSONの可読性	high	未レビュー	確認済み	承認する	Data JSONは人間が直接読む可能性があるため、日本語をUnicodeエスケープした状態で保存しない。		
13	foundation_rule_013	13	Markdown	Markdown Export の位置づけ	high	未レビュー	確認済み	承認する	Markdown Export は、Data JSON の表示用Viewである。		
14	foundation_rule_014	14	原則	FRB Studio の基本思想	high	未レビュー	確認済み	承認する	FRB Studio / JSON Object Studio は、JSONで思考を構造化し、AIとの文脈を育てるためのStudioである。		
15	foundation_rule_015	15	基本構造	Data / View / Export の原則	high	未レビュー	確認済み	承認する	Data JSON、ViewDef JSON、Markdown Export、Git Diff、AI、Human の役割を分ける。		
16	foundation_rule_016	16	原則	承認判断は人間が行う	high	未レビュー	確認済み	承認する	AIはレビューを支援するが、採用可否・承認・保留・差戻しの最終判断は人間が行う。		
17	foundation_rule_017	17	運用	v0.4-r001 の意味	high	未レビュー	確認済み	承認する	v0.4-r001 は、JSON Object Studio としての正式命名、およびバージョン・リビジョン・インシデント・ルール管理の整理を開始したリビジョンとして扱う。		
18	foundation_rule_018	18	運用	AI作業ファイル記録とインシデント回答記録	high	未レビュー	確認済み	承認する	AIが作業で更新したファイル・変更理由・対応結果を、インシデントJSONへ自然文中心で残す。root data/defs は必要時更新可、wwwroot/data/defs は公開用として保護する。		
19	row_copy_1		運用	★マークダウン　入力テストデータ	high	未レビュー	未確認	未承認	# 見出し\n## 見出し\n- 箇条書き\n1. 番号付きリスト		
20	foundation_rule_019	19	運用	GitHub基準ソースとZIP返却契約	high	未レビュー	確認済み	承認する	AI作業では、GitHub main を基準ソースとし、依頼は incident_file と phase を中心に行う。返却物は data / defs / wwwroot 階層のZIPとし、更新済みインシデントJSONを data/json/01_main に含める。取得時は tree/blob URL と raw/archive URL を用途で使い分ける。		
```

</details>

<details>
<summary>Grid JSON を表示</summary>

```json
{
  "view_def": "rules/rule_review_common_view_def_v0_2_editable_review_target.json",
  "data_file": "frb_studio_foundation_review_data_v0_1_github_fetch_urls_added.json",
  "section": "レビュー項目一覧",
  "row_count": 20,
  "columns": [
    {
      "field": "no",
      "caption": "No.",
      "type": "number"
    },
    {
      "field": "rule_id",
      "caption": "Rule ID",
      "type": "text"
    },
    {
      "field": "section_no",
      "caption": "章番号",
      "type": "text"
    },
    {
      "field": "category",
      "caption": "分類",
      "type": "select"
    },
    {
      "field": "title",
      "caption": "ルール名",
      "type": "text"
    },
    {
      "field": "priority",
      "caption": "優先度",
      "type": "select"
    },
    {
      "field": "review_status",
      "caption": "レビュー状態",
      "type": "select"
    },
    {
      "field": "verification_status",
      "caption": "確認状態",
      "type": "select"
    },
    {
      "field": "approval_decision",
      "caption": "承認",
      "type": "select"
    },
    {
      "field": "summary",
      "caption": "要約",
      "type": "textarea"
    },
    {
      "field": "user_comment",
      "caption": "人間コメント",
      "type": "textarea"
    },
    {
      "field": "ai_response",
      "caption": "AI回答",
      "type": "textarea"
    }
  ],
  "rows": [
    {
      "no": 1,
      "rule_id": "foundation_rule_001",
      "section_no": "1",
      "category": "運用",
      "title": "FRB Studio の位置づけ",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "FRB Studio は、JSON Object Studio を含む Studio 系ツール群の共通ブランド名として扱う。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 2,
      "rule_id": "foundation_rule_002",
      "section_no": "2",
      "category": "運用",
      "title": "JSON Object Studio の正式名称",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "現在のプロダクト名は JSON Object Studio とする。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 3,
      "rule_id": "foundation_rule_003",
      "section_no": "3",
      "category": "運用",
      "title": "画面表示名",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "画面上では FRB Studio / JSON Object Studio / 表示バージョン / タグラインを表示する。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 4,
      "rule_id": "foundation_rule_004",
      "section_no": "4",
      "category": "運用",
      "title": "app_info.json の役割",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "app_info.json はアプリの名札として、現在の名称・表示バージョン・タグラインのみを持つ。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 5,
      "rule_id": "foundation_rule_005",
      "section_no": "5",
      "category": "運用",
      "title": "app_settings.json の役割",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "システム全体の動作パラメータは app_settings.json に分離する。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 6,
      "rule_id": "foundation_rule_006",
      "section_no": "6",
      "category": "運用",
      "title": "Version / Revision / Phase の分離",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Version、Revision、Phase は混ぜず、それぞれ別の意味として扱う。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 7,
      "rule_id": "foundation_rule_007",
      "section_no": "7",
      "category": "運用",
      "title": "Incident と Version Detail の関係",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Incident は「なぜやるのか」、Version Detail は「何を入れたのか」を記録する。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 8,
      "rule_id": "foundation_rule_008",
      "section_no": "8",
      "category": "原則",
      "title": "Markdownを原本にしない",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "構造化できるルール・制約・レビュー・判断理由は、Markdownではなく Data JSON を原本とする。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 9,
      "rule_id": "foundation_rule_009",
      "section_no": "9",
      "category": "原則",
      "title": "ルール系データはドメイン別Data JSONで管理する",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "憲法、制約、ViewDef生成ルール、Studio運用原則などのルール系データは、ドメインごとに Data JSON を分ける。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 10,
      "rule_id": "foundation_rule_010",
      "section_no": "10",
      "category": "基本構造",
      "title": "ViewDefは構造が同じなら共通化する",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "ルール系Data JSONはドメインごとに分けるが、レビュー対象としての基本構造が同じ場合、ViewDefは共通化してよい。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 11,
      "rule_id": "foundation_rule_011",
      "section_no": "11",
      "category": "運用",
      "title": "rules フォルダーの役割",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "ルール・制約・憲法レビュー系の ViewDef / Data JSON / Export は、rules フォルダー配下で管理する。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 12,
      "rule_id": "foundation_rule_012",
      "section_no": "12",
      "category": "運用",
      "title": "日本語JSONの可読性",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Data JSONは人間が直接読む可能性があるため、日本語をUnicodeエスケープした状態で保存しない。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 13,
      "rule_id": "foundation_rule_013",
      "section_no": "13",
      "category": "Markdown",
      "title": "Markdown Export の位置づけ",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Markdown Export は、Data JSON の表示用Viewである。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 14,
      "rule_id": "foundation_rule_014",
      "section_no": "14",
      "category": "原則",
      "title": "FRB Studio の基本思想",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "FRB Studio / JSON Object Studio は、JSONで思考を構造化し、AIとの文脈を育てるためのStudioである。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 15,
      "rule_id": "foundation_rule_015",
      "section_no": "15",
      "category": "基本構造",
      "title": "Data / View / Export の原則",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Data JSON、ViewDef JSON、Markdown Export、Git Diff、AI、Human の役割を分ける。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 16,
      "rule_id": "foundation_rule_016",
      "section_no": "16",
      "category": "原則",
      "title": "承認判断は人間が行う",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "AIはレビューを支援するが、採用可否・承認・保留・差戻しの最終判断は人間が行う。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 17,
      "rule_id": "foundation_rule_017",
      "section_no": "17",
      "category": "運用",
      "title": "v0.4-r001 の意味",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "v0.4-r001 は、JSON Object Studio としての正式命名、およびバージョン・リビジョン・インシデント・ルール管理の整理を開始したリビジョンとして扱う。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 18,
      "rule_id": "foundation_rule_018",
      "section_no": "18",
      "category": "運用",
      "title": "AI作業ファイル記録とインシデント回答記録",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "AIが作業で更新したファイル・変更理由・対応結果を、インシデントJSONへ自然文中心で残す。root data/defs は必要時更新可、wwwroot/data/defs は公開用として保護する。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 19,
      "rule_id": "row_copy_1",
      "section_no": "",
      "category": "運用",
      "title": "★マークダウン　入力テストデータ",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "summary": "# 見出し\n## 見出し\n- 箇条書き\n1. 番号付きリスト",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 20,
      "rule_id": "foundation_rule_019",
      "section_no": "19",
      "category": "運用",
      "title": "GitHub基準ソースとZIP返却契約",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "AI作業では、GitHub main を基準ソースとし、依頼は incident_file と phase を中心に行う。返却物は data / defs / wwwroot 階層のZIPとし、更新済みインシデントJSONを data/json/01_main に含める。取得時は tree/blob URL と raw/archive URL を用途で使い分ける。",
      "user_comment": "",
      "ai_response": ""
    }
  ]
}
```

</details>