# ルールレビュー記録（判断ログ・変更履歴対応）

- 出力日時: 2026/6/28 1:40:33
- 対象: FRB Studio / JSON Object Studio
- schema_version: rule_review_data_v0_1
- status: converted_draft
- 件数: 23

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
- 生成日時: 2026-06-26T00:00:00+09:00
- ルール数: 23
- 承認済み数: 23

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
| 19 | 19 | foundation_rule_019 |  | 運用 | GitHub基準ソースとZIP返却契約 | high | 未レビュー | 確認済み | 承認する | AI作業ではGitHub mainまたはユーザー添付ZIPを基準ソースとし、incident_file/phaseを中心に作業する。返却ZIPには更新済みインシデントJSONを含め、node_modulesやruntime生成物、長大パスのテスト結果を混ぜず、Windowsで安全に展開できる成果物として返却する。 |
| 20 | 20 | foundation_rule_020 |  | 運用 | 共通化・archive退避・ファイル名維持原則 | high | 未レビュー | 確認済み | 承認する | 共通化できるものは原則共通化し、やりすぎで将来苦しくなる場合は人間へ相談する。古いデータ・不要データはactiveから削除して_archiveへ退避し、ルール系ファイルおよびViewDefは原則同じファイル名で更新する。 |
| 21 | 21 | foundation_rule_021 |  | テスト証跡 | Test Evidence / Expected-Actual-Diff 責務分離契約 | high | 未レビュー | 確認済み | 承認する | テスト証跡では、Expected JSONを期待値の正本、Actual JSONを観測値のみ、Diff JSONを比較結果、Test Codeを実行する仕掛けとして責務分離する。 |
| 22 | 22 | foundation_rule_022 |  | folder_policy | Test Folder / Archive / Runtime生成物隔離契約 | high | 未レビュー | 確認済み | 承認する | テスト証跡は data/json/03_tests/{domain}/{suite_id}/ を正本とし、テストコードは tests/、runtime一時生成物は tests/.runtime/ に分離する。旧パスはactiveから除去し、必要に応じて_archiveへ退避する。テストコードは実行言語ごとの共通ランナーへ寄せる。 |
| 23 | 23 | foundation_rule_023 |  | test_evidence | Diff Result Common Format / diff_result_v0_1契約 | high | 未レビュー | 確認済み | 承認する | Diff Result JSONはdocument_type=diff_result、schema_version=diff_result_v0_1を標準とし、上部サマリとchecks[].passを共通化する。 |

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


#### 判断ログ

（なし）

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


#### 判断ログ

（なし）

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


#### 判断ログ

（なし）

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


#### 判断ログ

（なし）

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


#### 判断ログ

（なし）

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


#### 判断ログ

（なし）

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


#### 判断ログ

（なし）

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


#### 判断ログ

（なし）

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

- `frb_coding_constraints_data_v0_3.json`
- `frb_foundation_rules_data_v0_1.json`
- `frb_viewdef_generation_rules_data_v0_1.json`

理由:
ドメインが違うルールを1つのData JSONに混ぜると、目的、責任範囲、更新履歴が曖昧になるため。

##### 確認メッセージ

このルールをレビューし、採用可否を判断する。

#### レビュー会話


#### 判断ログ

（なし）

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


#### 判断ログ

（なし）

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


#### 判断ログ

（なし）

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


#### 判断ログ

（なし）

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


#### 判断ログ

（なし）

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


#### 判断ログ

（なし）

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


#### 判断ログ

（なし）

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


#### 判断ログ

（なし）

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


#### 判断ログ

（なし）

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


#### 判断ログ

（なし）

#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_foundation_rule_018_v012_001 |  |  |  | rule_added |  |  |  | v0.12-rules-update-reporting-policy をStudio運用の基礎ルールとして定着させるため。 |
| chg_foundation_rule_018_v012_redo_001 |  |  |  | body_refine |  |  |  | v0.12 FRBコメントで、管理項目を抑えつつ更新痕跡を残す方針に修正されたため。 |

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

AI作業ではGitHub mainまたはユーザー添付ZIPを基準ソースとし、incident_file/phaseを中心に作業する。返却ZIPには更新済みインシデントJSONを含め、node_modulesやruntime生成物、長大パスのテスト結果を混ぜず、Windowsで安全に展開できる成果物として返却する。

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
- Foundation Rules: https://github.com/tamasub/FRB/blob/main/tools/FRBStudio_App/data/json/00_rules/frb_foundation_rules_data_v0_1.json

AIやスクリプトが直接取得するためのraw/archive URL:

- リポジトリ main ZIP: https://github.com/tamasub/FRB/archive/refs/heads/main.zip
- FRBStudio_App raw base: https://raw.githubusercontent.com/tamasub/FRB/main/tools/FRBStudio_App/
- FRBStudio 本体 raw base: https://raw.githubusercontent.com/tamasub/FRB/main/tools/FRBStudio/
- Foundation Rules raw: https://raw.githubusercontent.com/tamasub/FRB/main/tools/FRBStudio_App/data/json/00_rules/frb_foundation_rules_data_v0_1.json

incident_file は FRBStudio_App からの相対パスとして扱う。
たとえば `incident_file: data/json/01_main/studio_work_incident_data_xxx.json` が指定された場合、raw URL は以下の形式で解決する。

`https://raw.githubusercontent.com/tamasub/FRB/main/tools/FRBStudio_App/{incident_file}`

個別ファイルを直接取得できない場合、またはHTMLなど大きなファイルの完全取得が不安定な場合は、リポジトリ main ZIP を取得し、展開後の `FRB-main/tools/FRBStudio_App/` または `FRB-main/tools/FRBStudio/` を基準として作業する。

GitHubのtree/blob URLは閲覧用であり、機械取得や完全ファイル取得にはraw URLまたはmain ZIPを優先する。

---

### ViewDef安定ファイル名契約

既存Data JSONから参照されている ViewDef / DefView ファイルは、原則として同じファイル名のまま更新する。

ViewDefファイル名は単なる成果物名ではなく、以下をつなぐ接続キーである。

- Data JSON の `view_def` 参照
- URL起動リンク
- GitHub Pages上の静的読込
- GitDiffによる変更前後比較
- 既存の作業履歴・記事リンク・説明文

そのため、AIは通常のViewDef改善で `*_v0_5_*.json` のような新規ファイル名を勝手に作成しない。既存ViewDefを改修する場合は、同じ相対パス・同じファイル名で返却する。

新しいViewDefファイル名を作成できるのは、ユーザーが明示的に新名を指定した場合、既存ViewDefとの互換性を意図的に切る場合、または旧ViewDefと新ViewDefを並行運用する明確な理由がある場合に限る。

ViewDefファイル名を変更する場合は、Data JSON側の `view_def` 参照更新、URL起動やGitHub Pagesへの影響、GitDiffで新規追加扱いになる理由を、該当インシデントの `decision_log` / `change_history` / `latest_ai_response` に記録する。

---

### Data JSON内ViewDef候補契約

Data JSON は、既定ViewDefとして top-level `view_def` を持つことができる。

同じData JSONを複数のViewDefで確認したい場合は、追加で top-level `view_def_candidates` を持つ。

推奨形は以下とする。

```json
{
  "view_def": "rules/main_view_def.json",
  "view_def_candidates": [
    {
      "view_def": "rules/main_view_def.json",
      "label": "標準表示",
      "role": "default",
      "status": "active",
      "note": "通常利用するViewDef"
    },
    {
      "view_def": "rules/relation_view_def.json",
      "label": "リレーション確認",
      "role": "relation",
      "status": "active",
      "note": "関連データ確認用"
    }
  ]
}
```

Studio の手動ViewDef切替UIは、Data JSONに `view_def` / `view_def_candidates` として明示されたViewDefだけを切替候補として扱う。

これにより、Data JSONから参照されていないViewDefを棚卸し対象として発見しやすくし、ViewDefの現役・旧版・診断用・削除候補の判断をData側の接続情報から追えるようにする。

候補リストはViewDefファイル名変更の代替ではない。既存ViewDefの通常改修ではファイル名を変更せず、同名更新を原則とする。

---

### Data JSON内ViewDef候補の記述ルール

`view_def_candidates` は ViewDef JSON 側の定義ではなく、Data JSON 側のメタ情報として扱う。

`view_def_candidates[].view_def` は、`defs/` 配下からの相対パスで記述する。  
そのため、値には `defs/` を付けない。

例:

```json
{
  "view_def": "qa/qa_expected_checks_classified_view_def_v0_1.json",
  "view_def_candidates": [
    {
      "view_def": "qa/qa_expected_checks_classified_view_def_v0_1.json",
      "label": "標準表示",
      "role": "default",
      "status": "active",
      "note": "通常利用するViewDef"
    },
    {
      "view_def": "qa/qa_expected_checks_sample_view_def_v0_1.json",
      "label": "リレーション確認用",
      "role": "relation",
      "status": "active",
      "note": "関連データ確認用"
    }
  ]
}
```

`view_def` は既定ViewDefであり、通常読込時に最初に使用するViewDefを示す。

`view_def_candidates` は、そのData JSONで手動切替を許可するViewDef候補を示す。

`role` は候補ViewDefの用途を表す。まずは以下を標準候補とする。

- `default`: 通常利用する標準表示
- `relation`: 関連データ・リレーション確認用
- `review`: レビュー用
- `compare`: 比較用
- `debug`: 診断・確認用

`status` は候補ViewDefの利用状態を表す。まずは以下を標準候補とする。

- `active`: 現役候補
- `deprecated`: 旧版だが一時的に残す候補
- `inactive`: 通常の手動切替候補には出さない候補

Studio の手動ViewDef切替UIは、原則として `status: "active"` の候補を表示対象とする。

top-level `view_def` は、`view_def_candidates` 内の `role: "default"` または先頭候補と一致させることを推奨する。

AIは、実体が存在しないViewDef、利用意図が不明な試作ViewDef、削除候補のViewDefを、ユーザー確認なしに `view_def_candidates` へ追加しない。

`view_def_candidates` は、ViewDef棚卸しのための接続情報であり、Runtimeが全defsから自由に候補を探すための仕組みではない。


---

### v0.14.13 追記: 共通化・archive退避・安定ファイル名の返却契約

AIは、構造・表示・検証・出力が共通化できるものについて、原則として共通化を優先する。
ただし、共通化により将来の拡張性、可読性、保守性、ドメイン固有の意味が苦しくなると判断される場合、AIは独断で進めず、人間へ相談する。

古いデータ、旧パス、不要と思われるデータは、成果物ZIPのactive領域から削除して返却することを基本とする。
ただし、完全削除ではなく、ZIPルート直下の `_archive/{削除日時}/` 配下へ、元の相対パスが追える形で退避する。

例:

```text
_archive/20260627_153000/data/json/03_tests/old_suite/...
```

旧パスをactive領域に残すと、存在するだけで正本と誤認される罠フォルダーになる。
そのため、移行済み・不要・重複と判断したものは、activeから消し、archiveへ退避する。

ルール系ファイルおよびViewDefファイルは、参照元が多いため、原則として既存ファイル名を変更しない。
ルール本文やViewDef定義を修正する場合は、同じ相対パス・同じファイル名で更新する。
新しい正本世代を作る、互換性を意図的に切る、旧版と並行運用するなど、ファイル名変更が必要な場合は、人間へ確認し、理由・影響範囲・参照更新をインシデントJSONへ記録する。

---

### v0.14.15 追記: Test Folder / Runtime生成物返却契約

テスト証跡の正本は、原則として以下に集約する。

```text
data/json/03_tests/{domain}/{suite_id}/
├─ test_patterns/
├─ expected/
├─ actual/
├─ diff/
├─ relations/
├─ summary/
└─ notes/
```

`tests/` はテストを実行するコードの置き場であり、Expected / Actual / Diff などの証跡正本を置く場所ではない。

Playwright や Node test が実行時に生成する一時成果物は、root直下に生やさない。必要な場合は `tests/.runtime/` 配下へ隔離し、成果物ZIPには含めない。

成果物ZIPには、原則として以下を含めない。

```text
node_modules/
playwright-report/
test-results/
test_results/
tests/.runtime/
tests_screen_state/
```

旧パスや移行済みフォルダーはactive領域に残さず、必要に応じて `_archive/{削除日時}/` に退避する。runtime生成物は再生成可能な一時成果物であるため、原則としてarchive退避対象ではなく成果物から除外する。

テストコードは、コード実行言語ごとに共通ランナーへ寄せることを基本とする。たとえば Node.js系は1つの共通 `.mjs`、Playwright系は1つの共通 `.spec.ts` で複数テストパターンを実行できる形を目指す。新しいテストケース追加時は、まずTest Pattern / Expected JSON の追加で対応し、テストコードファイルをケースごとに増やさない。過剰共通化により将来苦しくなる場合は、人間へ相談する。

---

### v0.14.18 追記: Delivery / Cleanup / ZIP安全返却チェック

成果物ZIPを返却する前に、AIはactive領域へ再生成可能なruntime生成物を混入させない。
特に以下は成果物ZIPへ含めない。

```text
node_modules/
playwright-report/
test-results/
test_results/
tests/.runtime/
tests_screen_state/
```

`node_modules/` は依存ライブラリであり、成果物ではない。Playwrightの `playwright-report/`、`test-results/`、Node/Playwright実行時の `tests/.runtime/` は再生成可能な一時生成物であり、原則として `_archive` 退避対象ではなく、返却ZIPから除外する。

返却前チェックでは、少なくとも次を確認する。

1. JSON parse が通ること。
2. 生成物除外リストがZIPに含まれていないこと。
3. Windows展開で問題になりやすい長大パスを含めないこと。
4. 旧パス・不要データをactiveに残していないこと。
5. 更新済みインシデントJSONを `data/json/01_main/` に含め、AIの完了報告・実更新ファイル・確認内容を記録すること。

旧パス・不要データのうち、判断履歴として残すべきものは `_archive/{削除日時}/` へ退避する。
runtime生成物は再生成可能なため、原則としてarchiveせず削除・除外する。


##### 確認メッセージ

Foundation Rule 19「GitHub基準ソースとZIP返却契約」をレビューする。

##### メモ

GitHub上の閲覧用URLだけでは大きなHTML等の完全取得が不安定な場合があるため、raw URLとmain ZIP URLを標準取得URLとして追記。

#### レビュー会話


#### 判断ログ

| Decision ID | 日時 | 判断種別 | 判断内容 | 理由 | 条件 | 例外 | 補足 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dec_foundation_rule_019_v0141_001 | 2026-06-26 |  | view_def_candidates はData JSON側のメタ情報とし、候補ViewDefのパスは defs/ 配下からの相対パスで記述する。 | Data JSONとViewDefの接続関係をData側で明示しつつ、defs/付きパスとdefs/なしパスが混在して手動切替UIに重複表示される事故を避けるため。 |  |  |  |
| dec_foundation_rule_019_v01413_001 | 2026-06-27 |  | 旧パス・不要データはactiveに残さず、_archive/{削除日時}/へ退避する。 | active領域に残る旧パスは、Studioのファイルツリーや人間確認で正本と誤認される罠フォルダーになるため。 |  |  |  |
| dec_foundation_rule_019_v01415_001 | 2026-06-27 |  | テスト証跡はdata/json/03_tests配下、テストコードはtests配下、runtime生成物はtests/.runtime配下へ分離する。 | 証跡正本・実行コード・一時生成物を混ぜると、旧パス誤認やZIP混入事故が再発するため。 |  |  |  |
| dec_foundation_rule_019_v01418_001 | 2026-06-27 |  | runtime生成物は原則archiveではなく返却ZIPから除外する。 | node_modulesやPlaywright report/test-resultsは再生成可能な一時成果物であり、証跡正本ではない。archiveへ積むとZIP肥大化・長大パス・誤参照の原因になるため。 |  |  |  |

#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_foundation_rule_019_v0138_001 |  |  |  | rule_added |  |  |  | ソースZIP添付運用から卒業し、インシデントJSONを中心にAI作業を依頼・記録・返却できるようにするため。 |
| chg_foundation_rule_019_v0138_002 |  |  |  | body_append |  |  |  | GitHub基準運用で、大きなHTMLファイル等をAIが完全取得できない場合に備え、作業依頼プロンプトから安定してソース取得へ辿れるようにするため。 |
| chg_foundation_rule_019_v014_001 |  |  |  | body_append |  |  |  | ViewDefファイル名がData JSONのview_def参照・URL起動・GitDiffの差分観測点として機能しているため。 |
| chg_foundation_rule_019_v0141_001 |  |  |  | body_append |  |  |  | DataとViewDefの接続関係を明確化し、未参照ViewDefの棚卸し・削除候補判断をしやすくするため。 |
| chg_foundation_rule_019_v0141_002 |  |  |  | body_append |  |  |  | v0.14.1-data-viewdef-candidates の実運用確認で、候補パスや表示対象の判断ルールをFoundation Rulesに残す必要が見えたため。 |
| chg_foundation_rule_019_v01413_001 |  |  |  | body_append |  |  |  | Step 4-A/4-Bで旧パス罠フォルダー、Actual/Diff契約、ViewDefファイル名変更の副作用が明確になったため。 |
| chg_foundation_rule_019_v01415_001 |  |  |  | body_append |  |  |  | 旧パス罠フォルダー、Playwright生成物の混入、テストケースごとのコード増殖を防ぎ、Expected/Actual/Diff証跡を安定してStudioくんで確認できるようにするため。 |
| chg_foundation_rule_019_v01418_001 |  |  |  | body_append |  |  |  | 成果物ZIPにPlaywright生成物や長大パスが混入し、Windows解凍エラーや旧パス罠フォルダーが発生した経験を返却契約へ反映するため。 |

### 20 共通化・archive退避・ファイル名維持原則
- Rule ID: foundation_rule_020
- 分類: 運用
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md

#### レビュー対象


##### 元見出し

## 20. 共通化・archive退避・ファイル名維持原則

##### 要約

共通化できるものは原則共通化し、やりすぎで将来苦しくなる場合は人間へ相談する。古いデータ・不要データはactiveから削除して_archiveへ退避し、ルール系ファイルおよびViewDefは原則同じファイル名で更新する。

##### ルール本文

共通化できるものは、原則として共通化する。

ただし、共通化によって将来の拡張性・可読性・保守性・ドメイン固有の意味が苦しくなると判断される場合、AIは独断で共通化を進めず、人間へ相談する。

古いデータ・不要と思われるデータは、成果物のactive領域から削除して返却することを基本とする。
ただし、完全削除ではなく、ルートの `_archive` フォルダー配下に削除日時フォルダーを作成し、元の相対パスが追える形で退避する。

例:

```text
_archive/20260627_153000/data/json/03_tests/old_path/...
```

旧パスや不要データをactive領域に残すと、存在するだけで正本と誤認される可能性がある。
そのため、削除対象はactiveから外し、archiveへ退避したうえで、何を退避したかをインシデントJSONの `change_history` / `latest_ai_response` に残す。

ルール系統およびViewDefを修正する場合は、原則としてファイル名を変更しない。
これは、Data JSONの `view_def` 参照、URL起動、GitHub raw URL、GitDiff確認、作業履歴、記事リンクなど、参照元が多いためである。

新しい正本世代を作る、互換性を切る、旧版と並行運用するなどの理由でファイル名変更が必要な場合は、人間に確認し、理由・影響範囲・参照更新をインシデントJSONへ記録する。

##### 確認メッセージ

旧パスを残すな。だが、歴史は捨てるな。archiveへ送れ。

##### メモ

今回、添付ZIP内のFoundation Rulesファイル名がGitHub raw契約上の安定名と異なっていたため、active側は安定名へ復元し、旧ファイル名は_archiveへ退避した。

#### レビュー会話


##### AI回答

v0.14.13-foundation-commonization-archive-filename-policy により追加。共通化優先、過剰共通化時の人間相談、不要データの_archive退避、ルール/ViewDefファイル名維持をFoundation Rulesの運用原則として定義。

#### 判断ログ

| Decision ID | 日時 | 判断種別 | 判断内容 | 理由 | 条件 | 例外 | 補足 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dec_foundation_rule_020_v01413_001 | 2026-06-27 |  | 共通化できるものは共通化するが、やりすぎる前に人間へ相談する。 | 共通化は強力だが、ドメイン差分を消しすぎると将来の拡張性・可読性を損なうため。 |  |  |  |
| dec_foundation_rule_020_v01413_002 | 2026-06-27 |  | 不要データはactiveから削除し、_archive/{削除日時}/へ退避する。 | 削除履歴を残しつつ、active領域に罠フォルダーや旧正本候補を残さないため。 |  |  |  |

#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_foundation_rule_020_v01413_001 |  |  |  | rule_added |  |  |  | 今回のテスト証跡整理で、共通フォーマット化、旧パス罠フォルダー、ファイル名変更による参照元修正のリスクが明確になったため。 |

### 21 Test Evidence / Expected-Actual-Diff 責務分離契約
- Rule ID: foundation_rule_021
- 分類: テスト証跡
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB_STUDIO_FOUNDATION_RULES_v0_1_draft.md

#### レビュー対象


##### 元見出し

21. Test Evidence / Expected-Actual-Diff 責務分離契約

##### 要約

テスト証跡では、Expected JSONを期待値の正本、Actual JSONを観測値のみ、Diff JSONを比較結果、Test Codeを実行する仕掛けとして責務分離する。

##### ルール本文

FRB Studio / JSON Object Studio のテスト証跡では、Expected / Actual / Diff / Test Code の責務を明確に分離する。

```text
Expected JSON = 期待値の正本
Actual JSON   = 実行時に観測した値のみ
Diff JSON     = Expected と Actual の比較結果
Test Code     = 実行する仕掛け
```

Expected JSONは、期待値の正本である。Test Codeは期待値を直書きせず、Expected JSONを読み込んで比較する。

Actual JSONは、実行時に観測した値のみを保持する。actual.jsonには、原則として expected / pass / resultLabel / summary / failedCount / failedCheckIds / firstFailure を持たせない。

Diff JSONは、ExpectedとActualの比較結果を保持する。diff.jsonは、expected / actual / pass / resultLabel / summary / failedCount / failedCheckIds / firstFailure / checks[] を持ち、Studioくんで失敗内容を確認する正本になる。

テストがfailする場合でも、assertより前に actual.json と diff.json を保存する。

```text
テストはfailしてよい。
でもDiffは残れ。
```

詳細なテスト証跡ルールの正本は、以下のData JSONで管理する。

```text
data/json/00_rules/frb_test_evidence_rules_data_v0_1.json
```

この契約は、QA / Screen State / ViewDef静的検証など、Expected / Actual / Diff 構造を持つテスト証跡に適用する。
過剰適用により将来苦しくなると判断される場合は、AIが独断で拡張せず、人間へ相談する。

##### 確認メッセージ

Foundation Rule 21「Test Evidence / Expected-Actual-Diff 責務分離契約」をレビューする。

##### メモ

詳細ルールは frb_test_evidence_rules_data_v0_1.json を正本として管理する。

#### レビュー会話


##### AI回答

v0.14.14-test-evidence-rules-contract により追加。Expected / Actual / Diff / Test Code の責務分離と、Diff出力後assertの原則をFoundation Rulesへ反映。

#### 判断ログ

| Decision ID | 日時 | 判断種別 | 判断内容 | 理由 | 条件 | 例外 | 補足 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dec_foundation_rule_021_v01414_001 | 2026-06-27 |  | Expected / Actual / Diff / Test Code の責務をFoundation Rulesで固定する。 | テスト証跡の名前と役割を揃え、AIと人間が失敗理由を追体験できる状態を作るため。 |  |  |  |
| dec_foundation_rule_021_v01414_002 | 2026-06-27 |  | assertはactual/diff保存後に行う。 | テストがfailした時にdiff.jsonが出力されないと、Studioくんで失敗理由を確認できないため。 |  |  |  |

#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_foundation_rule_021_v01414_001 |  |  |  | rule_added |  |  |  | TP-IPC-001でactual.jsonにexpected/pass/summaryが混在し、diff.jsonの責務が曖昧になったため。 |

### 22 Test Folder / Archive / Runtime生成物隔離契約
- Rule ID: foundation_rule_022
- 分類: folder_policy
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 承認者: tamasub
- 承認日時: 2026-06-27
- 元行: 0

#### レビュー対象


##### 元見出し

Test Folder / Archive / Runtime生成物隔離契約

##### 要約

テスト証跡は data/json/03_tests/{domain}/{suite_id}/ を正本とし、テストコードは tests/、runtime一時生成物は tests/.runtime/ に分離する。旧パスはactiveから除去し、必要に応じて_archiveへ退避する。テストコードは実行言語ごとの共通ランナーへ寄せる。

##### ルール本文

Test Folder / Archive / Runtime生成物の扱いは、以下を基本契約とする。

```text
data/json/03_tests/ = Studioくんで見るテスト証跡の正本
tests/              = テストを実行するコード
tests/.runtime/     = Playwright / Node test などの一時生成物
_archive/           = activeから外した旧データ・不要データの退避先
```

## 1. テスト証跡の正本

Expected / Actual / Diff / Test Pattern / Relations / Summary / Notes は、原則として以下の構造へ集約する。

```text
data/json/03_tests/{domain}/{suite_id}/
├─ test_patterns/
├─ expected/
├─ actual/
├─ diff/
├─ relations/
├─ summary/
└─ notes/
```

例:

```text
data/json/03_tests/qa/v0_14_2_incident_prompt_copy_action/
data/json/03_tests/screen_state/screen_state_smoke_001/
```

## 2. テストコードの置き場

テストコードは `tests/` 配下へ置く。
`tests/` は実行する仕掛けの置き場であり、Expected / Actual / Diff の正本置き場ではない。

テストコードは、コード実行言語ごとに1つの共通ランナーへ寄せることを基本とする。

例:

```text
tests/qa/static/incident_prompt_copy_action_viewdef_static.test.mjs
tests/screen_state/ncjs-screen-state-compare.checks.spec.ts
```

新しいテストケースを追加する場合、まず Test Pattern / Expected JSON の追加で対応し、ケースごとにテストコードファイルを増やさない。
ただし、ドメイン差分や実行方式の違いを吸収しすぎて将来苦しくなる場合は、人間へ相談する。

## 3. runtime一時生成物の隔離

Playwright や Node test が実行時に生成する一時ファイルは、root直下に出さない。
必要な場合は `tests/.runtime/` 配下へ隔離する。

成果物ZIPには、原則として以下を含めない。

```text
node_modules/
playwright-report/
test-results/
test_results/
tests/.runtime/
tests_screen_state/
```

runtime生成物は再生成可能な一時成果物であり、原則として `_archive` 退避対象ではない。

## 4. 旧パスの扱い

移行済み旧パスや不要データは、active領域に残さない。
ただし、削除対象が人間またはAIの判断履歴として残すべきデータである場合は、完全削除せず `_archive/{削除日時}/` 配下へ元の相対パスが追える形で退避する。

旧パスをactiveに残すと、ファイルが出ていないのではなく、別の旧フォルダーを見ていたという誤認が起きる。

```text
旧パスを残すな。
旧パスは罠フォルダーになる。
```

## 5. cleanupスクリプト

runtime生成物や旧runtimeフォルダーは、必要に応じて `tests/tools/cleanup_runtime_artifacts.ps1` で掃除する。
このスクリプトは再生成可能な一時生成物を削除するためのものであり、Expected / Actual / Diff などの証跡正本を削除してはいけない。

##### 確認メッセージ

旧パスを残すな。旧パスは罠フォルダーになる。

##### メモ

runtime生成物は再生成可能なため、成果物ZIPから除外し、原則としてarchive退避対象にはしない。

#### レビュー会話


##### AI回答

v0.14.15で、03_tests正本、tests実行コード、tests/.runtime一時生成物、_archive退避の責務分離を追加。あわせて、テストコードは実行言語ごとに共通ランナーへ寄せる方針を追加。

#### 判断ログ

| Decision ID | 日時 | 判断種別 | 判断内容 | 理由 | 条件 | 例外 | 補足 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dec_foundation_rule_022_v01415_001 | 2026-06-27 |  | テストコードは実行言語ごとの共通ランナーへ寄せることを基本とする。 | テストケースごとにコードファイルを増やすと、Expected JSONを正本として育てる文化が弱まり、テストコード側へ期待値や分岐が肥大化するため。 |  |  |  |
| dec_foundation_rule_022_v01415_002 | 2026-06-27 |  | runtime生成物は成果物ZIPに含めず、必要ならtests/.runtimeへ隔離する。 | Playwrightレポートや添付ファイルは長いパス名・ノイズ・誤認の原因になるため。 |  |  |  |

#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_foundation_rule_022_v01415_001 |  |  |  | rule_added |  |  |  | テスト証跡と実行コードと一時生成物を分離し、旧パス罠フォルダーとZIP混入事故を防ぐため。 |

### 23 Diff Result Common Format / diff_result_v0_1契約
- Rule ID: foundation_rule_023
- 分類: test_evidence
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 承認者: tamasub
- 承認日時: 2026-06-27
- 元行: 0

#### レビュー対象


##### 元見出し

Diff Result Common Format / diff_result_v0_1契約

##### 要約

Diff Result JSONはdocument_type=diff_result、schema_version=diff_result_v0_1を標準とし、上部サマリとchecks[].passを共通化する。

##### ルール本文

Diff Result JSONは、Expected JSON と Actual JSON の比較結果を保持する正本である。

Diff Result共通フォーマットでは、以下を標準とする。

```text
schema_version = diff_result_v0_1
document_type  = diff_result
domain         = qa / screen_state / viewdef など
diff_kind      = 差分種別
test_id        = テストまたは証跡ID
status         = pass / fail などの機械判定
resultLabel    = 画面表示用の短い判定
summary        = 人間向け要約
total / passCount / failCount / failedCount
failedCheckIds / failedChecks / firstFailure
checks[]
```

Diff明細の判定フィールドは、`checks[].pass` を正本とする。
`passed` / `ok` / `result` などの別名を新規標準化しない。

ドメイン固有情報は追加項目として保持してよいが、共通項目の意味を壊してはいけない。
共通化しすぎて将来苦しくなる場合は、AIが独断せず人間へ相談する。

詳細なDiff Result Format Rulesの正本は、以下のData JSONで管理する。

```text
data/json/00_rules/frb_diff_result_format_rules_data_v0_1.json
```

##### 確認メッセージ

Diff Resultは共通サマリとpassで読む。

##### メモ

詳細ルールは frb_diff_result_format_rules_data_v0_1.json を正本として管理する。

#### レビュー会話


##### AI回答

v0.14.16で、diff_result_v0_1共通サマリとchecks[].pass標準化をFoundation Rulesへ追加。

#### 判断ログ

| Decision ID | 日時 | 判断種別 | 判断内容 | 理由 | 条件 | 例外 | 補足 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dec_foundation_rule_023_v01416_001 | 2026-06-27 |  | Diff Resultのdocument_typeはdiff_result、schema_versionはdiff_result_v0_1を標準とする。 | QA / Screen Stateなどドメインを超えて同じ比較結果ViewDefで扱いやすくするため。 |  |  |  |
| dec_foundation_rule_023_v01416_002 | 2026-06-27 |  | Diff明細の判定フィールドはchecks[].passへ統一する。 | passed / ok / result などの別名を増やすと、強調表示・比較・ViewDefが分岐するため。 |  |  |  |

#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_foundation_rule_023_v01416_001 |  |  |  | rule_added |  |  |  | Step 5 Diff Result共通ViewDef化へ進む前に、Data契約を明文化するため。 |

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
19	foundation_rule_019	19	運用	GitHub基準ソースとZIP返却契約	high	未レビュー	確認済み	承認する	AI作業ではGitHub mainまたはユーザー添付ZIPを基準ソースとし、incident_file/phaseを中心に作業する。返却ZIPには更新済みインシデントJSONを含め、node_modulesやruntime生成物、長大パスのテスト結果を混ぜず、Windowsで安全に展開できる成果物として返却する。		
20	foundation_rule_020	20	運用	共通化・archive退避・ファイル名維持原則	high	未レビュー	確認済み	承認する	共通化できるものは原則共通化し、やりすぎで将来苦しくなる場合は人間へ相談する。古いデータ・不要データはactiveから削除して_archiveへ退避し、ルール系ファイルおよびViewDefは原則同じファイル名で更新する。		v0.14.13-foundation-commonization-archive-filename-policy により追加。共通化優先、過剰共通化時の人間相談、不要データの_archive退避、ルール/ViewDefファイル名維持をFoundation Rulesの運用原則として定義。
21	foundation_rule_021	21	テスト証跡	Test Evidence / Expected-Actual-Diff 責務分離契約	high	未レビュー	確認済み	承認する	テスト証跡では、Expected JSONを期待値の正本、Actual JSONを観測値のみ、Diff JSONを比較結果、Test Codeを実行する仕掛けとして責務分離する。		v0.14.14-test-evidence-rules-contract により追加。Expected / Actual / Diff / Test Code の責務分離と、Diff出力後assertの原則をFoundation Rulesへ反映。
22	foundation_rule_022	22	folder_policy	Test Folder / Archive / Runtime生成物隔離契約	high	未レビュー	確認済み	承認する	テスト証跡は data/json/03_tests/{domain}/{suite_id}/ を正本とし、テストコードは tests/、runtime一時生成物は tests/.runtime/ に分離する。旧パスはactiveから除去し、必要に応じて_archiveへ退避する。テストコードは実行言語ごとの共通ランナーへ寄せる。		v0.14.15で、03_tests正本、tests実行コード、tests/.runtime一時生成物、_archive退避の責務分離を追加。あわせて、テストコードは実行言語ごとに共通ランナーへ寄せる方針を追加。
23	foundation_rule_023	23	test_evidence	Diff Result Common Format / diff_result_v0_1契約	high	未レビュー	確認済み	承認する	Diff Result JSONはdocument_type=diff_result、schema_version=diff_result_v0_1を標準とし、上部サマリとchecks[].passを共通化する。		v0.14.16で、diff_result_v0_1共通サマリとchecks[].pass標準化をFoundation Rulesへ追加。
```

</details>

<details>
<summary>Grid JSON を表示</summary>

```json
{
  "view_def": "rules/rule_review_common_view_def_v0_3.json",
  "data_file": "frb_foundation_rules_data_v0_1.json",
  "section": "レビュー項目一覧",
  "row_count": 23,
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
      "rule_id": "foundation_rule_019",
      "section_no": "19",
      "category": "運用",
      "title": "GitHub基準ソースとZIP返却契約",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "AI作業ではGitHub mainまたはユーザー添付ZIPを基準ソースとし、incident_file/phaseを中心に作業する。返却ZIPには更新済みインシデントJSONを含め、node_modulesやruntime生成物、長大パスのテスト結果を混ぜず、Windowsで安全に展開できる成果物として返却する。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 20,
      "rule_id": "foundation_rule_020",
      "section_no": "20",
      "category": "運用",
      "title": "共通化・archive退避・ファイル名維持原則",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "共通化できるものは原則共通化し、やりすぎで将来苦しくなる場合は人間へ相談する。古いデータ・不要データはactiveから削除して_archiveへ退避し、ルール系ファイルおよびViewDefは原則同じファイル名で更新する。",
      "user_comment": "",
      "ai_response": "v0.14.13-foundation-commonization-archive-filename-policy により追加。共通化優先、過剰共通化時の人間相談、不要データの_archive退避、ルール/ViewDefファイル名維持をFoundation Rulesの運用原則として定義。"
    },
    {
      "no": 21,
      "rule_id": "foundation_rule_021",
      "section_no": "21",
      "category": "テスト証跡",
      "title": "Test Evidence / Expected-Actual-Diff 責務分離契約",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "テスト証跡では、Expected JSONを期待値の正本、Actual JSONを観測値のみ、Diff JSONを比較結果、Test Codeを実行する仕掛けとして責務分離する。",
      "user_comment": "",
      "ai_response": "v0.14.14-test-evidence-rules-contract により追加。Expected / Actual / Diff / Test Code の責務分離と、Diff出力後assertの原則をFoundation Rulesへ反映。"
    },
    {
      "no": 22,
      "rule_id": "foundation_rule_022",
      "section_no": "22",
      "category": "folder_policy",
      "title": "Test Folder / Archive / Runtime生成物隔離契約",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "テスト証跡は data/json/03_tests/{domain}/{suite_id}/ を正本とし、テストコードは tests/、runtime一時生成物は tests/.runtime/ に分離する。旧パスはactiveから除去し、必要に応じて_archiveへ退避する。テストコードは実行言語ごとの共通ランナーへ寄せる。",
      "user_comment": "",
      "ai_response": "v0.14.15で、03_tests正本、tests実行コード、tests/.runtime一時生成物、_archive退避の責務分離を追加。あわせて、テストコードは実行言語ごとに共通ランナーへ寄せる方針を追加。"
    },
    {
      "no": 23,
      "rule_id": "foundation_rule_023",
      "section_no": "23",
      "category": "test_evidence",
      "title": "Diff Result Common Format / diff_result_v0_1契約",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Diff Result JSONはdocument_type=diff_result、schema_version=diff_result_v0_1を標準とし、上部サマリとchecks[].passを共通化する。",
      "user_comment": "",
      "ai_response": "v0.14.16で、diff_result_v0_1共通サマリとchecks[].pass標準化をFoundation Rulesへ追加。"
    }
  ]
}
```

</details>