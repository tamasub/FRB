# Studioくん 改修インシデント管理

- 出力日時: 2026/6/21 19:49:11
- 対象: No-Code JSON Studio / FRBStudio App 改修計画
- schema_version: studio_work_incident_data_v0_1
- status: active
- 件数: 11

## 基本情報

- タイトル: Studioくん 改修インシデント管理
- 対象: No-Code JSON Studio / FRBStudio App 改修計画
- Schema Version: studio_work_incident_data_v0_1
- 状態: active

### 目的

Studioくん本体改修に関する重要な修正依頼・方針・会話履歴を作業項目ごとに残す。承認ワークフローではなく、インシデント管理・作業項目管理・会話履歴管理を目的とする。

### 運用方針

重要な修正依頼は作業項目として登録する。仕様変更・方針変更・実装方針の会話は discussion_history / decision_log / change_history に残す。作業項目ごとの会話履歴を残し、未来の人間とAIが経緯を追体験できるようにする。

### 標準メタフィールド方針

Runtime内のData固定名は原則NG。ただし、Studio標準メタフィールドとして憲法・仕様に明記されたものは使用可能。例: created_at, updated_at, deleted, is_deleted, created_by, updated_by などは、標準メタフィールドとして定義すれば使用可。

## 作業項目一覧

| 作業ID | Phase | タイトル | 種別 | 分類 | 優先度 | 状態 | 目的 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| studio_work_0001 | v0.4-split | app.js ソース分割 | refactoring | source_split | high | 完了 | 既存機能を維持したまま、巨大化した app.js を責務ごとに分割する。 |
| studio_work_0002 | v0.5-registry | Renderer / VirtualData / Action のRegistry化 | architecture | registry | high | 完了 | 分岐や固定実装をRegistryへ寄せ、戦略的設計パターンとして差し替え可能な構造へ移行する。 |
| studio_work_0003 | v0.6-action-execute-button | toolbar.executeButton / Action 実行対応 | feature | action | high | 完了 | ViewDefで定義された toolbar.executeButton を読み取り、caption と action に応じた主役操作を実行できるようにする。 |
| studio_work_0004 | v0.7-viewdef-rules-review | ★FRB_VIEW_DEF_GENERATION_RULES / Schema レビュー | rules_review | rules_schema | high | 完了 | 現時点の最新Runtime、Registry、toolbar.executeButton、Markdown出力、chat/objectArray仕様に合わせて、ViewDef生成ルールMDをv0.16へ更新する。 |
| studio_work_0005 | v0.7-objectarray-save-integrity | objectArray / 履歴配列の保存健全性確認 | bugfix | save_integrity | critical | 完了 | discussion_history / decision_log / change_history などの配列データが、保存後も配列として保持されることを保証し、detailFooter/chat欄の編集・削除が反映・上書き保存されるようにする。 |
| studio_work_0006 | v0.7-chat-input-mapping | chat送信欄の保存先・末尾表示・Markdownリンク/画像対応 | feature_fix | chat | high | 完了 | chat型で追加コメント入力欄を使う場合に、保存先userField/aiFieldをViewDefで明示し、送信したユーザーコメントをmessages定義位置ではなく会話末尾へ表示する。あわせて、ViewDefで許可されたchat本文に限りMarkdownリンク/画像記法を表示できるようにする。 |
| studio_work_0007 | v0.7-markdown-export-contract | Markdown出力契約 / JSON展開情報 / AI貼り付け用 | specification | markdown_export | high | 未着手 | Markdown出力ボタンで何を出力できるべきかを、ViewDef生成ルール・Schema・Runtime仕様として整理する。 |
| studio_work_0008 | v0.7-filename-encoding-sanitize | Markdown出力ファイル名の文字化け対策 | bugfix | file_io | high | 未着手 | Markdown出力やViewer連携で、Unicodeエスケープ/URLエンコード/HTMLエンティティ風の文字化けファイル名が大量発生する問題を解消する。 |
| studio_work_0009 | v0.7-viewdef-sample-fixtures | ViewDef代表サンプル / 健康診断セット整理 | maintenance | fixtures | medium | 未着手 | 今後の改修時に最低限確認する代表Data/ViewDefセットを整理し、回帰確認の基準を作る。 |
| studio_work_0010 | v0.7-fixed-name-audit | Runtime内固定フィールド名監査 | architecture_audit | fixed_name | medium | 未着手 | Runtime内に残っている固定フィールド名・固定Action名・固定builder名を棚卸しし、骨格か脂肪かを分類する。 |
| studio_work_0011 | v0.7-standard-meta-fields | Studio標準メタフィールド定義 | rules_review | standard_fields | medium | 未着手 | Runtime内Data固定名禁止の例外として認めるStudio標準メタフィールド候補を整理し、採用ルールを定義する。 |

## 作業項目詳細


### v0.4-split: app.js ソース分割
- 作業ID: studio_work_0001
- 種別: refactoring
- 分類: source_split
- 優先度: high
- 状態: 完了
- 対象ファイル: app.js, index.html

#### 目的

既存機能を維持したまま、巨大化した app.js を責務ごとに分割する。

#### 背景

Studioくん憲法に基づき、Data / ViewDef / Action / Runtime の責務分離を進める。まずは機能追加ではなく、肥満化した app.js の内臓整理を行う。

#### 対象範囲

従来script方式のまま、core / renderers / virtualData / markdown などの責務単位へ分割する。index.html は分割後の script 読み込みへ変更する。

#### 対象外

type="module" 化は行わない。ActionRegistry完全実装、toolbar.executeButton本格対応、Chat View完全可変化、固定フィールド名の全面撤去はこの段階では行わない。

#### 固定名方針

固定名を見つけたら即削除ではなく分類する。Studio仕様の固定名・DOMシェル固定名は骨格として残す。Runtime内のData固定名は原則NG。ただしStudio標準メタフィールドとして憲法・仕様に明記されたものは例外。

#### module化方針

type="module" は将来検討。v0.4-split では従来script方式 + window名前空間または既存グローバル互換で安全に進める。

#### リスク

グローバル変数依存、関数定義順、イベント初期化順、保存処理、サブグリッド編集、chat型表示、Markdown出力への回帰リスク。

#### 確認観点

JSON読込、保存、Grid表示、Detail編集、サブグリッド、chat型、Markdown出力、ViewDef Markdown出力、Drop、コンボ読込を確認する。

#### 作業会話サマリ


##### 依頼 / 方針

v0.4-split としてすすめよう。Runtime内のData固定名は原則NGで、Studioとして汎用的によく使うフィールドと認定するものは、憲法に記載しておけばOK。type="module" は将来的にのスタンスでよい。

##### AI整理

意識合わせ完了。v0.4-split は機能追加ではなく既存機能維持の責務分割。固定フィールド名は、骨格・脂肪を分類し、標準メタフィールド制度として憲法・仕様で定義されたものは許容する。

##### 追加コメント

v0.4-split の作業を依頼。data.zip と studio_work_incident_data_v0_1.json を添付。

##### AI追加回答

既存機能維持を優先し、type="module" 化せず従来script方式で app.js を責務分割。Registry化と toolbar.executeButton 本格対応はスコープ外として維持。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0001_001 | 2026-06-21 | user | 方針合意 | v0.4-split としてすすめよう。Runtime内のData固定名は原則NGだが、汎用フィールドは憲法に記載しておけばOK。 |
| disc_0001_002 | 2026-06-21 | assistant | 方針整理 | v0.4-split は機能維持のままソース分割。type="module" 化は見送り、固定名は分類して扱う。 |
| disc_0001_003 | 2026-06-21 | user | 作業依頼 | studio_work_incident_data_v0_1.json の v0.4-split の作業をお願いします。 |
| disc_0001_004 | 2026-06-21 | assistant | 作業結果 | app.js を core / ui / virtualData / renderers / markdown / runtime に分割し、index.html の script 読み込みを更新。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0001_001 | 2026-06-21 | v0.4-split は従来script方式で進める。 | type="module" 化はスコープや読み込み順変更のリスクがあるため、初回分割では安全を優先する。 |
| dec_0001_002 | 2026-06-21 | 固定名は即削除ではなく分類する。 | Studio仕様・DOM骨格・ViewDef宣言値・Adapter仕様・Runtime脂肪を区別する必要があるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0001_001 | 2026-06-21 | source_split | wwwroot/app.js 1ファイル構成 | wwwroot/js 配下に責務分割し、wwwroot/app.js は起動・イベント配線中心へ縮小 | v0.4-split の目的である既存機能維持のままの責務分割を実施するため。 |

### v0.5-registry: Renderer / VirtualData / Action のRegistry化
- 作業ID: studio_work_0002
- 種別: architecture
- 分類: registry
- 優先度: high
- 状態: 完了
- 対象ファイル: wwwroot/js/core/registry.js, wwwroot/js/renderers/*registry.js, wwwroot/js/virtualData/virtual_data_registry.js, wwwroot/js/markdown/markdown_registry.js, wwwroot/js/actions/action_registry.js, index.html

#### 目的

分岐や固定実装をRegistryへ寄せ、戦略的設計パターンとして差し替え可能な構造へ移行する。

#### 背景

v0.4-split で責務分割した後、Renderer / VirtualDataBuilder / Action をRegistry管理にすることで、Studioくんを専用処理の塊ではなく拡張可能なRuntimeへ近づける。

#### 対象範囲

RendererRegistry、VirtualDataBuilderRegistry、ActionRegistry の導入方針を整理する。既存 builder 名や renderer 分岐を、段階的にRegistryへ寄せる。

#### 対象外

ActionRegistryの完全な実行ボタン連動は v0.6-action-execute-button 側で扱う。v0.5ではRegistryの骨格と既存処理の移設を主目的とする。

#### 固定名方針

builder名やrenderer種別など、ViewDefで宣言される識別子は条件付きOK。Runtimeが特定Dataフィールド名を直接参照する場合は原則NG。

#### module化方針

type="module" 化はまだ行わない。v0.4と同じscript方式を維持する。

#### リスク

Registry読み込み順、登録漏れ、field control factory移設、virtualData builder alias不足、markdown.type未登録時の回帰リスク。

#### 確認観点

全JSのnode --check確認済み。実機ではJSON読込、Grid/Form/Chat/ObjectArray表示、relation系VirtualData、Markdown AI Prompt出力、保存処理を確認する。

#### 作業会話サマリ


##### 依頼 / 方針

v0.5-registry を重要作業項目として管理したい。

##### AI整理

v0.5-registry は、v0.4で分割した責務を戦略的設計パターンへ寄せる段階。Registry化によって、Renderer・VirtualDataBuilder・Actionの差し替え可能性を高める。

##### 追加コメント

v0.5-registry確認完了。続いて v0.6-action-execute-button の対応を依頼。

##### AI追加回答

追加の事前確認なしで、v0.5-registry の範囲に限定して実施。Renderer / FieldControl / VirtualData / Markdown / Action のRegistry骨格を追加し、既存ヘッダーボタン動作や toolbar.executeButton 本格対応は v0.6 に残した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0002_001 | 2026-06-21 | assistant | 作業構想 | v0.5-registry では RendererRegistry / VirtualDataBuilderRegistry / ActionRegistry を入れるのが自然。 |
| disc_0002_002 | 2026-06-21 | user | v0.5-registry作業依頼 | studio_work_incident_data_v0_2.json の v0.5-registry 作業を添付に基づいて依頼。事前に意識合わせすべき項目があれば確認。 |
| disc_0002_003 | 2026-06-21 | assistant | v0.5-registry作業結果 | v0.5-registry は機能追加ではなく健康体化。Registry骨格を追加し、分岐を登録制に寄せた。v0.6-action-execute-button の実装はスコープ外として保持。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0002_001 | 2026-06-21 | Registry化は v0.4-split の後に行う。 | 先に責務分割しないと、Registry化と既存コード整理が混ざって回帰リスクが上がるため。 |
| dec_0002_002 | 2026-06-21 | v0.5ではActionRegistryを追加するが、既存UIボタンとの接続は行わない。 | toolbar.executeButton本格対応は v0.6 の作業範囲であり、v0.5ではRegistryの受け皿整備に留めるため。 |
| dec_0002_003 | 2026-06-21 | virtualData builder / markdown.type / field control をRegistryへ寄せる。 | ViewDefで宣言される識別子をRuntime分岐ではなく登録済み実装へ委譲し、追加時の触る場所を明確にするため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| hist_0002_001 | 2026-06-21 | architecture_registry | v0.4-splitでは責務別ファイルに分割したが、builder/typeごとの一部固定分岐は残っていた。 | Registry骨格を追加し、VirtualData / Markdown / FieldControl / Renderer / Action を登録制へ寄せた。 | ステップ数削減より、追加・変更時に触る場所を明確にし、AIが迷子にならない健康体へ近づけるため。 |

### v0.6-action-execute-button: toolbar.executeButton / Action 実行対応
- 作業ID: studio_work_0003
- 種別: feature
- 分類: action
- 優先度: high
- 状態: 完了
- 対象ファイル: wwwroot/js/actions/action_registry.js, wwwroot/js/actions/action_toolbar.js, wwwroot/js/runtime/load_runtime.js, wwwroot/index.html, wwwroot/styles.css, defs/studio/*execute_button_sample.json

#### 目的

ViewDefで定義された toolbar.executeButton を読み取り、caption と action に応じた主役操作を実行できるようにする。

#### 背景

Action Separation の会話で、toolbar直下配列ではなく toolbar.executeButton を主役操作として定義する方針になった。RuntimeはActionの意味を知らず、ViewDef由来の actionId を ActionRegistry に渡すだけにする。

#### 対象範囲

ViewDefの toolbar.executeButton 定義を読み取り、ボタン表示名を caption から出す。クリック時は actionId を変数として ActionRegistry.execute(actionId, context) に渡す。

#### 対象外

MIDI再生やテスト実行など、各Actionの中身の作り込みは必要最小限。まずはAction実行の骨格とサンプルActionを優先する。

#### 固定名方針

Runtimeに actionRegistry.execute("PlayMidi", context) のような固定Action名を書かない。"PlayMidi" は ViewDef上のAction識別子としてのみ許容する。

#### module化方針

type="module" 化はまだ行わない。v0.4/v0.5のscript方式を継続する。

#### リスク

ActionRegistry読込順、executeButton未定義時の既存画面影響、未登録Actionクリック時のエラーハンドリング、既存ヘッダーボタン群との役割混同、ActionContext肥満化。

#### 確認観点

全JSのnode --check確認済み。実機ではexecuteButton未定義ViewDefで既存動作に影響しないこと、executeButton定義ViewDefでcaption表示とAction実行が動くこと、ExportMarkdown/Noop/ShowActionContextなどの登録済みActionが実行できることを確認する。

#### 作業会話サマリ


##### 依頼 / 方針

v0.6-action-execute-button を重要作業項目として管理したい。

##### AI整理

v0.6-action-execute-button は、Studioくんの実行ボタンポリモーフィズムの中核。Runtimeに固定Action名を置かず、ViewDefのexecuteButton定義を変数として扱う。

##### 追加コメント

v0.5-registry確認完了。続いて、studio_work_incident_data_v0_3.json の v0.6-action-execute-button 対応を依頼。事前に意識合わせすべき項目があれば確認してほしい。

##### AI追加回答

追加の事前確認なしで、v0.6-action-execute-button の範囲に限定して実施。ViewDefの toolbar.executeButton から actionId を取得し、固定Action名をRuntimeに置かず ActionRegistry へ変数として渡す実行ボタンを追加した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0003_001 | 2026-06-21 | user | ViewDef構造 | { "toolbar": [ { "caption": "再生", "action": "PlayMidi" } ] } ではなく、toolbar の下に executeButton がある構造ではないか。 |
| disc_0003_002 | 2026-06-21 | assistant | ViewDef構造整理 | 主役操作は toolbar.executeButton、補助操作は toolbar.buttons に分けるのが自然。 |
| disc_0003_003 | 2026-06-21 | user | 作業依頼 | v0.5-registry確認完了。続いて v0.6-action-execute-button の対応を依頼。 |
| disc_0003_004 | 2026-06-21 | assistant | 作業結果 | toolbar.executeButton を読み取り、captionを表示し、actionIdをActionRegistryへ渡す view execute button runtime を追加。未定義時はボタンを出さず既存画面に影響しないようにした。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0003_001 | 2026-06-21 | 主役操作は toolbar.executeButton とする。 | 単なるボタン一覧ではなく、そのViewにおける代表的な実行操作として意味づけるため。 |
| dec_0003_002 | 2026-06-21 | RuntimeはAction名を固定文字列で指定しない。 | Action名はViewDefから取得したactionIdとして変数で受け渡す必要があるため。 |
| dec_0003_003 | 2026-06-21 | executeButton はGrid右上の操作エリアに表示する。 | ViewDefに紐づく主役操作であり、既存ヘッダーボタン群と混同せず、Gridの作業文脈に近い位置へ置くため。 |
| dec_0003_004 | 2026-06-21 | RuntimeはAction名を固定せず、executeButton.actionをactionId変数として渡す。 | Action Separationとポリモーフィズムの原則を守るため。 |
| dec_0003_005 | 2026-06-21 | v0.6では補助ボタン toolbar.buttons の実装は行わない。 | 今回のスコープは主役操作 toolbar.executeButton の接続であり、補助ボタン群は将来拡張として分離するため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0003_001 | 2026-06-21 | action_execute_button | ActionRegistryはv0.5で受け皿のみ存在し、ViewDefのtoolbar.executeButtonからは実行されていなかった。 | toolbar.executeButtonを読み取り、Grid右上に主役実行ボタンを表示し、executeButton.actionをActionRegistryへ変数として渡して実行する。 | Viewごとに「再生」「テスト実行」「Replay開始」などの主役操作をViewDefで宣言し、Runtimeを固定Action名から切り離すため。 |

### v0.7-viewdef-rules-review: ★FRB_VIEW_DEF_GENERATION_RULES / Schema レビュー
- 作業ID: studio_work_0004
- 種別: rules_review
- 分類: rules_schema
- 優先度: high
- 状態: 完了
- 対象ファイル: FRB_VIEW_DEF_GENERATION_RULES_ALL_v0_15.md, FRB_VIEW_DEF_GENERATION_RULES_ALL_v0_16.md, frb_view_def_schema_v0_8_action_registry_toolbar.json, wwwroot.zip

#### 目的

現時点の最新Runtime、Registry、toolbar.executeButton、Markdown出力、chat/objectArray仕様に合わせて、ViewDef生成ルールMDをv0.16へ更新する。

#### 背景

既存のルール文書が紛失・不完全になったため、最新ソースと過去の設計判断をもとに、AIへViewDef生成を依頼する際の公用ルールを再構築する必要がある。

#### 対象範囲

FRB_VIEW_DEF_GENERATION_RULES_ALL正本を更新し、detailBodyカード化、objectArray/chat保存契約、Markdown出力契約、Markdownリンク/画像記法、ファイル名sanitize、Rules正本命名ルールを追加する。

#### 対象外

この作業ではテストパターンや制約レビューの細部仕様には踏み込まない。まずViewDef生成ルールとSchemaの地ならしを行う。

#### 固定名方針

Runtime内Data固定名を前提とする記述は原則NG。Data側の固定名ではなく、ViewDefでfield/path/type/markdown/actionを宣言する方針を明記する。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、必要なルール・Runtime仕様・保存仕様を整理する。

#### リスク

Rulesに実装未対応の概念を書きすぎるとRuntimeと乖離する。今回、実装修正が必要なものは既存v0.7インシデントへ明示的に残す。

#### 確認観点

v0.16にdetailBody readable card、objectArray保存契約、chat input mapping、chat Markdownリンク/画像、Markdown出力契約、展開前/展開後JSON、文字化けファイル名対策、Rules正本命名ルールが入っているか確認する。

#### 作業会話サマリ


##### 依頼 / 方針

studio_work_incident_data_v0_4.json に次の作業データを追加したい。FRB_VIEW_DEF_GENERATION_RULESレビュー、objectArray/chat保存健全性、chat input mapping、Markdown出力契約、ViewDef代表サンプル整理、固定フィールド名監査、Studio標準メタフィールド定義、文字化けファイル名大量発生対応を整理したい。

##### AI整理

FRB_VIEW_DEF_GENERATION_RULESレビューは確定で追加。最新RuntimeとSchema/Rulesのズレを見直し、AIへViewDef生成を依頼するための公用語を整える。

##### 追加コメント

#依頼結論20260621_1746
01:FRB_VIEW_DEF_GENERATION_RULESに長文説明フィールドは必要に応じてdetailBodyカード化するルールを追加お願いします。
02:objectArray/chat保存健全性、chat input mapping、Markdown出力契約、ViewDef代表サンプル整理、固定フィールド名監査、Studio標準メタフィールド定義、文字化けファイル名大量発生対応をお願いします。
03:チャット欄において、画像リンク(MarkDown書式のリンク文字）に対応し、画像表示を可能として欲しい。
04:追加コメント欄に入力し、「反映(F12)」した文字が上書き保存しても保存されない。尚、チャット送信欄に内容を追加したら、追加されて保存された。しかし、同じ追加コメント欄の別の文書を削除して保存しても、ゾンビの様に復活してくる笑。
05:FRB_VIEW_DEF_GENERATION_RULES_ALL_v0_15.mdを更新お願いします。尚、ファイル名のバージョン番号の後ろに目的を示す言葉を付加するのは禁止します。GENERATION_RULESのみ適用ルール。本ルールも追記ください。更新したらバージョン数字のみ変更ください。FRB_VIEW_DEF_GENERATION_RULESを使って差分情報を記載する文書も禁止。ファイル名にALLという文言追加し、明示しています。（本ファイルの紛失防止対策）

##### AI追加回答

FRB_VIEW_DEF_GENERATION_RULES_ALL_v0_16.mdを作成。長文説明フィールドのdetailBody readable card化、objectArray保存契約、chat input mapping、chat本文Markdownリンク/画像記法、Markdown出力契約、展開前/展開後JSON、ファイル名sanitize、Rules正本命名ルールを追記。実装修正が必要な保存バグ等は既存v0.7インシデントへ継続課題として残す。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0004_001 | 2026-06-21 | user | 作業候補整理 | studio_work_incident_data_v0_4.json に次の作業データを追加したい。FRB_VIEW_DEF_GENERATION_RULESレビュー、objectArray/chat保存健全性、chat input mapping、Markdown出力契約、ViewDef代表サンプル整理、固定フィールド名監査、Studio標準メタフィールド定義、文字化けファイル名大量発生対応を整理したい。 |
| disc_0004_002 | 2026-06-21 | assistant | 作業候補整理 | FRB_VIEW_DEF_GENERATION_RULESレビューは確定で追加。最新RuntimeとSchema/Rulesのズレを見直し、AIへViewDef生成を依頼するための公用語を整える。 |
| disc_0004_003 | 2026-06-21 | user | Rules v0.16更新依頼 | #依頼結論20260621_1746<br>01:FRB_VIEW_DEF_GENERATION_RULESに長文説明フィールドは必要に応じてdetailBodyカード化するルールを追加お願いします。<br>02:objectArray/chat保存健全性、chat input mapping、Markdown出力契約、ViewDef代表サンプル整理、固定フィールド名監査、Studio標準メタフィールド定義、文字化けファイル名大量発生対応をお願いします。<br>03:チャット欄において、画像リンク(MarkDown書式のリンク文字）に対応し、画像表示を可能として欲しい。<br>04:追加コメント欄に入力し、「反映(F12)」した文字が上書き保存しても保存されない。尚、チャット送信欄に内容を追加したら、追加されて保存された。しかし、同じ追加コメント欄の別の文書を削除して保存しても、ゾンビの様に復活してくる笑。<br>05:FRB_VIEW_DEF_GENERATION_RULES_ALL_v0_15.mdを更新お願いします。尚、ファイル名のバージョン番号の後ろに目的を示す言葉を付加するのは禁止します。GENERATION_RULESのみ適用ルール。本ルールも追記ください。更新したらバージョン数字のみ変更ください。FRB_VIEW_DEF_GENERATION_RULESを使って差分情報を記載する文書も禁止。ファイル名にALLという文言追加し、明示しています。（本ファイルの紛失防止対策） |
| disc_0004_004 | 2026-06-21 | assistant | Rules v0.16更新結果 | FRB_VIEW_DEF_GENERATION_RULES_ALL_v0_16.mdを作成。長文説明フィールドのdetailBody readable card化、objectArray保存契約、chat input mapping、chat本文Markdownリンク/画像記法、Markdown出力契約、展開前/展開後JSON、ファイル名sanitize、Rules正本命名ルールを追記。実装修正が必要な保存バグ等は既存v0.7インシデントへ継続課題として残す。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0004_001 | 2026-06-21 | FRB_VIEW_DEF_GENERATION_RULES正本はALL付き・バージョン数字のみ更新する。 | 派生名や差分名が増えると、AIが正本を誤認し、ルール文書紛失や旧版参照が起きるため。 |
| dec_0004_002 | 2026-06-21 | 長文説明フィールドは必要に応じてdetailBody readable cardへ寄せる。 | 目的・背景・対象範囲・リスク等をtextareaの羅列にすると読みにくく、レビュー画面としての体験が悪化するため。 |
| dec_0004_003 | 2026-06-21 | chat/textarea内のMarkdownリンク・画像記法は、ViewDefで許可された場所だけ表示対象とする。 | 全フィールド自動Markdown化は危険だが、会話履歴にスクリーンショットリンクを残す用途は重要なため。 |
| dec_0004_004 | 2026-06-21 | 追加コメント欄の保存バグとゾンビ復活は、Rulesに保存契約を明記しつつ、実装修正は別インシデントで扱う。 | Rules更新とRuntime修正を混ぜると作業範囲が肥大化するため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0004_001 | 2026-06-21 | rules_update | FRB_VIEW_DEF_GENERATION_RULES_ALL_v0_15.md | FRB_VIEW_DEF_GENERATION_RULES_ALL_v0_16.md | 最新Runtime/ActionRegistry/Markdown/chat/objectArray運用と、ユーザーコメントで明確化されたRules正本命名ルールを反映するため。 |

### v0.7-objectarray-save-integrity: objectArray / 履歴配列の保存健全性確認
- 作業ID: studio_work_0005
- 種別: bugfix
- 分類: save_integrity
- 優先度: critical
- 状態: 完了
- 対象ファイル: wwwroot/js/renderers/field_controls.js, wwwroot/js/renderers/grid_detail.js, wwwroot/js/runtime/detail_save.js, representative objectArray/chat data/view_def

#### 目的

discussion_history / decision_log / change_history などの配列データが、保存後も配列として保持されることを保証し、detailFooter/chat欄の編集・削除が反映・上書き保存されるようにする。

#### 背景

インシデント管理JSON自体がStudioくんの作業記憶であるため、履歴配列が '3 items' のような表示文字列へ置き換わると、未来の人間とAIが経緯を追体験できなくなる。

#### 対象範囲

objectArray/stringArrayをDetail Formの通常入力欄から除外し、childAreaサブグリッド表示へ限定する。detailFooter/chatなどdetailForm外に描画されたcontenteditableも反映対象に含める。

#### 対象外

この作業ではobjectArrayの高度な並べ替え・差分比較・個別承認までは行わない。

#### 固定名方針

discussion_history などのフィールド名をRuntimeが特別扱いしない。objectArrayとしてViewDefで定義されたフィールドを汎用的に扱う。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、必要なルール・Runtime仕様・保存仕様を整理する。

#### リスク

保存処理の修正により、通常文字列フィールドやchat型、detail保存に回帰が起きるリスクがある。

#### 確認観点

discussion_history / decision_log / change_history が保存後もArrayで残ること。chat/detailFooterのlatest_user_comment編集・削除がF12反映と上書き保存で残ること。objectArrayの「2 items」表示文字列が保存値へ混入しないこと。

#### 作業会話サマリ


##### 依頼 / 方針

studio_work_incident_data_v0_4.json に次の作業データを追加したい。FRB_VIEW_DEF_GENERATION_RULESレビュー、objectArray/chat保存健全性、chat input mapping、Markdown出力契約、ViewDef代表サンプル整理、固定フィールド名監査、Studio標準メタフィールド定義、文字化けファイル名大量発生対応を整理したい。

##### AI整理

objectArray保存健全性は最優先候補。作業履歴の母艦が壊れないよう、表示文字列と保存実体を分離する。

##### 追加コメント

studio_work_incident_data_v0_6.json の v0.7-objectarray-save-integrity 対応を依頼。追加コメント欄が保存されない・削除してもゾンビ復活するため、objectArray/chat保存健全性を先に直したい。

##### AI追加回答

Detail Formだけでなく detailDialog 全体の data-field コントロールを反映対象にし、detailFooter/chat欄の編集・削除を保存対象にした。objectArray/stringArrayはDetail Formの通常入力欄から除外し、配列を「2 items」文字列で上書きしないようにした。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0005_001 | 2026-06-21 | user | 作業候補整理 | studio_work_incident_data_v0_4.json に次の作業データを追加したい。FRB_VIEW_DEF_GENERATION_RULESレビュー、objectArray/chat保存健全性、chat input mapping、Markdown出力契約、ViewDef代表サンプル整理、固定フィールド名監査、Studio標準メタフィールド定義、文字化けファイル名大量発生対応を整理したい。 |
| disc_0005_002 | 2026-06-21 | assistant | 作業候補整理 | objectArray保存健全性は最優先候補。作業履歴の母艦が壊れないよう、表示文字列と保存実体を分離する。 |
| disc_0005_extra_20260621 | 2026-06-21 | user | Rulesレビューからの追加論点 | 追加コメント欄に入力して反映(F12)しても上書き保存されない。削除して保存した文言がゾンビのように復活する。objectArray/chat保存健全性の観点で実装修正が必要。 |
| disc_0005_003 | 2026-06-21 | user | v0.7-objectarray-save-integrity作業依頼 | studio_work_incident_data_v0_6.json v0.7-objectarray-save-integrity の対応を依頼。事前意識合わせが必要なら確認してほしい。 |
| disc_0005_004 | 2026-06-21 | assistant | v0.7-objectarray-save-integrity作業結果 | detailEditableControlsをdetailDialog全体へ拡張し、detailFooter/chatのcontenteditable編集を反映対象にした。objectArray/stringArrayを通常Detail Formから除外し、配列保存の破壊を防止した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0005_001 | 2026-06-21 | objectArray/stringArrayは通常Detail Formに入力欄として表示しない。 | 「2 items」のような表示専用文字列が、反映・保存時に配列本体を上書きするリスクをなくすため。 |
| dec_0005_002 | 2026-06-21 | 反映対象の取得範囲をdetailFormからdetailDialog全体へ広げる。 | chat/detailFooterはchildArea側に描画されるため、detailFormだけでは追加コメント欄の編集・削除を保存できないため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0005_001 | 2026-06-21 | save_integrity_fix | detailEditableControlsはdetailForm内だけを対象にしており、detailFooter/chat欄の編集がF12反映・上書き保存に回収されなかった。またobjectArray/stringArrayが通常入力欄に出ると件数文字列で配列を壊す可能性があった。 | detailDialog全体のdata-field付きコントロールを回収し、chat/detailFooterのcontenteditableを保存対象にした。objectArray/stringArrayは通常入力欄から除外し、childArea表示専用にした。 | 作業履歴配列とチャットコメントをStudioくんの記憶として安全に保持するため。 |

### v0.7-chat-input-mapping: chat送信欄の保存先・末尾表示・Markdownリンク/画像対応
- 作業ID: studio_work_0006
- 種別: feature_fix
- 分類: chat
- 優先度: high
- 状態: 完了
- 対象ファイル: wwwroot/js/renderers/field_controls.js, wwwroot/js/runtime/detail_save.js, frb_view_def_schema_*.json, FRB_VIEW_DEF_GENERATION_RULES_*.md

#### 目的

chat型で追加コメント入力欄を使う場合に、保存先userField/aiFieldをViewDefで明示し、送信したユーザーコメントをmessages定義位置ではなく会話末尾へ表示する。あわせて、ViewDefで許可されたchat本文に限りMarkdownリンク/画像記法を表示できるようにする。

#### 背景

chat edit.messages は任意フィールドを吹き出し表示できるが、追加入力欄が既定の user_reply / ai_followup_response に依存すると、固定フィールド名肥満につながる。

#### 対象範囲

chat型の edit.input.enabled / userField / aiField / appendPosition / placeholder / sendLabel / markdown をRuntimeで扱う。input.userField と同じfieldがmessagesに定義されていても、appendPosition=afterMessagesの場合は通常messages表示から除外し、最後のAI回答の後ろへ末尾表示する。Markdownは保存値を原文のまま保持し、表示時だけリンク/画像へ変換する。

#### 対象外

チャット履歴のAI自動生成や外部LLM連携は行わない。まず入力欄の保存先明示と既存表示の安定化に限定する。

#### 固定名方針

user_request / latest_user_comment などのフィールド名をRuntimeで決め打ちしない。ViewDefの edit.input.userField / aiField を優先する。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、必要なルール・Runtime仕様・保存仕様を整理する。

#### リスク

既存chat表示やreadonly吹き出し、contenteditable保存との競合リスクがある。

#### 確認観点

送信欄入力がedit.input.userFieldへ保存されること。送信後の追加コメントが最後のAI回答の後ろに表示されること。input.userFieldと同じfieldがmessagesにあっても二重表示されないこと。Markdownリンク [text](./path) と画像 ![alt](./path) がViewDef許可時のみ表示されること。保存値はMarkdown原文のまま残ること。

#### 作業会話サマリ


##### 依頼 / 方針

studio_work_incident_data_v0_4.json に次の作業データを追加したい。FRB_VIEW_DEF_GENERATION_RULESレビュー、objectArray/chat保存健全性、chat input mapping、Markdown出力契約、ViewDef代表サンプル整理、固定フィールド名監査、Studio標準メタフィールド定義、文字化けファイル名大量発生対応を整理したい。

##### AI整理

chat入力欄は固定名に逃げず、edit.input.userField / aiField を明示するルールにする。

##### 追加コメント

studio_work_incident_data_v0_7.json の v0.7-chat-input-mapping 対応を依頼。チャット送信欄の保存先を固定名ではなく edit.input.userField / aiField で明示したい。送信したコメントは最後のAI回答の直前ではなく、最後のAI回答の次に表示したい。あわせて、チャット欄でMarkdown書式のリンク/画像を扱いたい。


# AI作業完了報告
1. edit.input.userField / aiField をRuntimeで読む
2. 送信欄の内容を userField に保存する
3. appendPosition=afterMessages の場合、追加コメントを会話末尾に表示する
4. userField が messages 側にもある場合は二重表示しない
5. chat欄で Markdownリンク / 画像記法を表示できるようにする
6. studio_work_incident_view_def_v0_2_readable_cards.json を更新
7. studio_work_incident_data_v0_8.json で該当インシデントを完了扱いに更新


##### AI追加回答

v0.7-chat-input-mapping対応完了。chat.edit.input.userField / aiField / appendPosition / markdown をRuntimeで扱い、送信欄由来のユーザーコメントをmessages定義位置に割り込ませず、会話末尾へ表示するようにした。Markdownリンク/画像はViewDefで許可されたchat本文のみ表示変換し、保存値はMarkdown原文のまま保持する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0006_001 | 2026-06-21 | user | 作業候補整理 | studio_work_incident_data_v0_4.json に次の作業データを追加したい。FRB_VIEW_DEF_GENERATION_RULESレビュー、objectArray/chat保存健全性、chat input mapping、Markdown出力契約、ViewDef代表サンプル整理、固定フィールド名監査、Studio標準メタフィールド定義、文字化けファイル名大量発生対応を整理したい。 |
| disc_0006_002 | 2026-06-21 | assistant | 作業候補整理 | chat入力欄は固定名に逃げず、edit.input.userField / aiField を明示するルールにする。 |
| disc_0006_extra_20260621 | 2026-06-21 | user | Rulesレビューからの追加論点 | チャット欄でMarkdown書式のリンク/画像を扱いたい。追加コメント欄の保存先も固定名ではなくedit.input.userField/aiFieldで明示したい。 |
| disc_0006_003 | 2026-06-21 | user | v0.7-chat-input-mapping作業依頼 | studio_work_incident_data_v0_7.json の v0.7-chat-input-mapping 対応を依頼。チャット欄でMarkdown書式のリンク/画像を扱いたい。追加コメント欄の保存先も固定名ではなくedit.input.userField/aiFieldで明示したい。 |
| disc_0006_004 | 2026-06-21 | user | 送信コメント表示位置の違和感 | 現状ではメッセージ送信すると最後のAI回答の直前の欄に追加されて意味不明な時系列になる。送信したコメントは最後のAI回答の次に表示したい。 |
| disc_0006_005 | 2026-06-21 | assistant | v0.7-chat-input-mapping作業結果 | chatInputConfigでedit.input.userField/aiField/appendPosition/markdownを扱うようにし、appendPosition=afterMessagesの場合はinput.userFieldを通常messages表示から除外して末尾表示するようにした。Markdownリンク/画像は許可されたchatだけ表示変換し、編集可能欄では原文を保持しつつプレビュー表示する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0006_001 | 2026-06-21 | chat送信欄の保存先はRuntime固定名ではなく、ViewDefのedit.input.userField / aiFieldを優先する。 | データごとにコメント欄のフィールド名は異なるため、Runtimeがuser_reply等の固定Data名へ依存するとStudioくんが特定データ構造に太るため。 |
| dec_0006_002 | 2026-06-21 | 送信欄由来のユーザーコメントはappendPosition=afterMessagesを既定とし、会話末尾へ表示する。 | messages定義順の途中にあるuserFieldへ追記すると、最後のAI回答の直前に新コメントが割り込んで時系列が崩れるため。 |
| dec_0006_003 | 2026-06-21 | chat内Markdownリンク/画像はViewDefで許可された場合のみ表示変換し、保存値はMarkdown原文のまま保持する。 | 全フィールド自動Markdown化は危険だが、作業会話にスクリーンショットリンクや画像を残す用途は重要なため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0006_001 | 2026-06-21 | chat_input_mapping | chat送信欄はuserFieldの定義位置に従って表示され、latest_user_commentがlatest_ai_responseの前にある場合、新規送信コメントも最後のAI回答の前へ割り込んでいた。Markdownリンク/画像もchat本文では表示変換されなかった。 | edit.input.userFieldを保存先として扱いながら、appendPosition=afterMessagesの場合はuserFieldを会話末尾へ表示するように変更。Markdownリンク/画像は許可されたchat本文で表示変換するようにした。 | チャットの時系列を自然に保ち、作業会話にスクリーンショットや関連資料リンクを残せるようにするため。 |

### v0.7-markdown-export-contract: Markdown出力契約 / JSON展開情報 / AI貼り付け用
- 作業ID: studio_work_0007
- 種別: specification
- 分類: markdown_export
- 優先度: high
- 状態: 未着手
- 対象ファイル: wwwroot/js/markdown/*.js, mdViewer.html, FRB_VIEW_DEF_GENERATION_RULES_*.md, frb_view_def_schema_*.json

#### 目的

Markdown出力ボタンで何を出力できるべきかを、ViewDef生成ルール・Schema・Runtime仕様として整理する。

#### 背景

Markdown出力は単なる表示ではなく、Studioの現在状態・Data・ViewDef・AI貼り付け用TSVを人間とAIへ渡す外交文書フォーマットになっている。

#### 対象範囲

AI貼り付け用、TSV、Grid JSON、展開前ViewDef JSON、展開後ViewDef JSON、必要に応じたData JSON、Markdown内リンク/画像記法の扱いを定義する。

#### 対象外

この作業ではMarkdown ViewerのUI大改修やPDF印刷最適化は主目的にしない。

#### 固定名方針

画像やリンクはData固定名ではなく、chat/textarea/markdown対象フィールドのMarkdown記法として扱う。画像URL専用固定フィールド名は原則作らない。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、必要なルール・Runtime仕様・保存仕様を整理する。

#### リスク

出力内容を増やしすぎるとMarkdownが巨大化し、AI貼り付け用途で扱いづらくなるリスクがある。

#### 確認観点

markdown.aiPrompt、includeGridJson、rowSource、visibleOnly、source/resolved JSON出力、chat/textarea内Markdownリンク/画像記法が期待どおり出るか確認する。

#### 作業会話サマリ


##### 依頼 / 方針

studio_work_incident_data_v0_4.json に次の作業データを追加したい。FRB_VIEW_DEF_GENERATION_RULESレビュー、objectArray/chat保存健全性、chat input mapping、Markdown出力契約、ViewDef代表サンプル整理、固定フィールド名監査、Studio標準メタフィールド定義、文字化けファイル名大量発生対応を整理したい。

##### AI整理

Markdown出力契約はテストパターン以前に整える。AI貼り付け用、展開前/展開後JSON、Markdown記法の扱いを正式化する。

##### 追加コメント

Markdown出力契約として、AI貼り付け用、展開前/展開後JSON、チャット欄Markdownリンク/画像記法の扱いを整理したい。

##### AI追加回答

v0.16 Rulesに契約として追記済み。Runtime実装とSchema必要性はこのインシデントで継続確認する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0007_001 | 2026-06-21 | user | 作業候補整理 | studio_work_incident_data_v0_4.json に次の作業データを追加したい。FRB_VIEW_DEF_GENERATION_RULESレビュー、objectArray/chat保存健全性、chat input mapping、Markdown出力契約、ViewDef代表サンプル整理、固定フィールド名監査、Studio標準メタフィールド定義、文字化けファイル名大量発生対応を整理したい。 |
| disc_0007_002 | 2026-06-21 | assistant | 作業候補整理 | Markdown出力契約はテストパターン以前に整える。AI貼り付け用、展開前/展開後JSON、Markdown記法の扱いを正式化する。 |
| disc_0007_extra_20260621 | 2026-06-21 | user | Rulesレビューからの追加論点 | Markdown出力契約として、AI貼り付け用、展開前/展開後JSON、チャット欄Markdownリンク/画像記法の扱いを整理したい。 |

#### 判断ログ


#### 変更履歴


### v0.7-filename-encoding-sanitize: Markdown出力ファイル名の文字化け対策
- 作業ID: studio_work_0008
- 種別: bugfix
- 分類: file_io
- 優先度: high
- 状態: 未着手
- 対象ファイル: wwwroot/js/core/file_api.js, wwwroot/js/core/fileNameUtils.js or equivalent, wwwroot/js/markdown/*.js, mdViewer.html, backend save/load API if needed

#### 目的

Markdown出力やViewer連携で、Unicodeエスケープ/URLエンコード/HTMLエンティティ風の文字化けファイル名が大量発生する問題を解消する。

#### 背景

画面上のファイル一覧に #U521d#U671f... のような文字化けファイル名が大量表示されており、Markdown出力ファイルの再利用・検索・削除・GitHub連携に悪影響がある。

#### 対象範囲

ファイル名生成、URLエンコード/デコード、Markdown出力名、Viewer遷移URL、保存APIへの渡し方を確認し、ファイルシステム上で安全かつ人間が読める名前に正規化する。

#### 対象外

過去に生成済みの文字化けファイルの一括リネームや削除ツールは、必要なら別作業とする。まず新規発生を止める。

#### 固定名方針

Dataフィールド名に依存したファイル名決め打ちは避ける。ViewDef名・Data名・titleなどを使う場合も、共通sanitize関数を通す。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、必要なルール・Runtime仕様・保存仕様を整理する。

#### リスク

日本語ファイル名、記号、空白、Windows禁止文字、URL相対パス、GitHub Pages上のパス解決で回帰するリスクがある。

#### 確認観点

日本語タイトル、英数字タイトル、空白入り、記号入り、既存mdファイル、Viewer URL遷移、保存後のファイル一覧表示を確認する。

#### 作業会話サマリ


##### 依頼 / 方針

Markdown出力時に文字化けファイル名が大量発生している。さっき提案した作業候補も含めて、studio_work_incident_data_v0_4.json に作業データを追加して整理したい。

##### AI整理

文字化けファイル名対応は新規インシデントとして追加する。まず新規発生を止め、ファイル名生成・URL・保存APIの境界を確認する。

##### 追加コメント

Rules正本ファイル名はALL付き・バージョン数字のみ変更。Markdown出力やViewerで文字化けファイル名を新規生成しないルールも必要。

##### AI追加回答

v0.16 Rulesに正本命名ルールとMarkdown出力ファイル名sanitizeを追記済み。実装修正はこのインシデントで扱う。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0008_001 | 2026-06-21 | user | 不具合報告 | Markdown出力/Viewer付近で、#U521d#U671f... のような文字化けファイル名が大量発生している。 |
| disc_0008_002 | 2026-06-21 | assistant | 作業候補化 | ファイル名生成・URLエンコード/デコード・保存API境界を確認し、Markdown出力ファイル名のsanitize/decodeルールを整備するインシデントとして扱う。 |
| disc_0008_extra_20260621 | 2026-06-21 | user | Rulesレビューからの追加論点 | Rules正本ファイル名はALL付き・バージョン数字のみ変更。Markdown出力やViewerで文字化けファイル名を新規生成しないルールも必要。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0008_001 | 2026-06-21 | 文字化けファイル名問題は、テストパターンや制約詳細に進む前の基盤不具合として扱う。 | Markdown出力やAI貼り付け用ファイルが再利用できなくなると、Studioくんの外部記憶・外交文書機能が壊れるため。 |

#### 変更履歴


### v0.7-viewdef-sample-fixtures: ViewDef代表サンプル / 健康診断セット整理
- 作業ID: studio_work_0009
- 種別: maintenance
- 分類: fixtures
- 優先度: medium
- 状態: 未着手
- 対象ファイル: defs/studio/*, data/studio/*, sample fixtures README

#### 目的

今後の改修時に最低限確認する代表Data/ViewDefセットを整理し、回帰確認の基準を作る。

#### 背景

v0.4〜v0.6で機能が増えたため、通常Grid/Formだけでなく、chat、objectArray、markdown.aiPrompt、toolbar.executeButton、relation系virtualDataを代表サンプルとして持つ必要がある。

#### 対象範囲

代表サンプルの一覧、用途、確認観点、保存場所、最新版の見分け方を整理する。

#### 対象外

自動テストパターンJSONやテストコード化は今回の対象外。まず人間とAIが確認できるfixturesを整理する。

#### 固定名方針

サンプルDataのフィールド名をRuntimeが標準として解釈しない。あくまでサンプルであり、ViewDefで構造を説明する。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、必要なルール・Runtime仕様・保存仕様を整理する。

#### リスク

サンプルが増えすぎると管理不能になるリスクがある。代表性と最小構成を重視する。

#### 確認観点

通常Grid/Form、chat、objectArray、markdown.aiPrompt、toolbar.executeButton、relation系virtualData、憲法レビュー、インシデント管理を確認する。

#### 作業会話サマリ


##### 依頼 / 方針

studio_work_incident_data_v0_4.json に次の作業データを追加したい。FRB_VIEW_DEF_GENERATION_RULESレビュー、objectArray/chat保存健全性、chat input mapping、Markdown出力契約、ViewDef代表サンプル整理、固定フィールド名監査、Studio標準メタフィールド定義、文字化けファイル名大量発生対応を整理したい。

##### AI整理

テストコードに入る前に、Studioくん健康診断用の代表サンプルセットを整理する。

##### 追加コメント

テスト送信

![alt text](./images/chat/tamasub.png)

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0009_001 | 2026-06-21 | user | 作業候補整理 | studio_work_incident_data_v0_4.json に次の作業データを追加したい。FRB_VIEW_DEF_GENERATION_RULESレビュー、objectArray/chat保存健全性、chat input mapping、Markdown出力契約、ViewDef代表サンプル整理、固定フィールド名監査、Studio標準メタフィールド定義、文字化けファイル名大量発生対応を整理したい。 |
| disc_0009_002 | 2026-06-21 | assistant | 作業候補整理 | テストコードに入る前に、Studioくん健康診断用の代表サンプルセットを整理する。 |

#### 判断ログ


#### 変更履歴


### v0.7-fixed-name-audit: Runtime内固定フィールド名監査
- 作業ID: studio_work_0010
- 種別: architecture_audit
- 分類: fixed_name
- 優先度: medium
- 状態: 未着手
- 対象ファイル: wwwroot/js/**/*.js, index.html, ViewDef schema/rules

#### 目的

Runtime内に残っている固定フィールド名・固定Action名・固定builder名を棚卸しし、骨格か脂肪かを分類する。

#### 背景

Studioくん憲法ではRuntime内Data固定名は原則NG。ただしStudio仕様・DOM骨格・ViewDef宣言値・Adapter仕様・標準メタフィールド候補は例外になり得るため、まず分類が必要。

#### 対象範囲

JS全体を対象に、固定文字列参照を抽出し、分類メモを作る。すぐ削除せず、v0.8以降の改善候補へつなげる。

#### 対象外

この作業では大規模な置換やリファクタリングは行わない。分類と判断ログ作成を主目的とする。

#### 固定名方針

固定名を見つけても即削除しない。Studio仕様の骨格、DOMシェル、ViewDef宣言値、Adapter仕様、Runtime脂肪、標準メタフィールド候補に分類する。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、必要なルール・Runtime仕様・保存仕様を整理する。

#### リスク

過剰に固定名を悪者扱いすると、DOM骨格やViewDef公用語まで壊すリスクがある。

#### 確認観点

row.xxx / message.xxx / action名直書き / builder名分岐 / DOM ID / ViewDefキーの分類ができていることを確認する。

#### 作業会話サマリ


##### 依頼 / 方針

studio_work_incident_data_v0_4.json に次の作業データを追加したい。FRB_VIEW_DEF_GENERATION_RULESレビュー、objectArray/chat保存健全性、chat input mapping、Markdown出力契約、ViewDef代表サンプル整理、固定フィールド名監査、Studio標準メタフィールド定義、文字化けファイル名大量発生対応を整理したい。

##### AI整理

固定名監査は削除ではなく分類。Studioくんの骨格と脂肪を見分ける作業として登録する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0010_001 | 2026-06-21 | user | 作業候補整理 | studio_work_incident_data_v0_4.json に次の作業データを追加したい。FRB_VIEW_DEF_GENERATION_RULESレビュー、objectArray/chat保存健全性、chat input mapping、Markdown出力契約、ViewDef代表サンプル整理、固定フィールド名監査、Studio標準メタフィールド定義、文字化けファイル名大量発生対応を整理したい。 |
| disc_0010_002 | 2026-06-21 | assistant | 作業候補整理 | 固定名監査は削除ではなく分類。Studioくんの骨格と脂肪を見分ける作業として登録する。 |

#### 判断ログ


#### 変更履歴


### v0.7-standard-meta-fields: Studio標準メタフィールド定義
- 作業ID: studio_work_0011
- 種別: rules_review
- 分類: standard_fields
- 優先度: medium
- 状態: 未着手
- 対象ファイル: CODING_CONSTRAINTS.md, FRB_VIEW_DEF_GENERATION_RULES_*.md, frb_view_def_schema_*.json

#### 目的

Runtime内Data固定名禁止の例外として認めるStudio標準メタフィールド候補を整理し、採用ルールを定義する。

#### 背景

created_at / updated_at / deleted / is_deleted などは汎用性が高い一方、安易に標準化すると固定名肥満につながるため、例外申請制として整理する必要がある。

#### 対象範囲

標準メタフィールド候補、用途、型、表示方針、保存方針、Runtimeが参照してよい範囲を整理する。

#### 対象外

この作業では全Dataへ標準メタフィールドを強制追加しない。採用基準と予約候補を決めるだけに留める。

#### 固定名方針

標準メタフィールドは憲法・Rules・Schemaに明記されたものだけ例外扱い。追加時はtamasub協議を必須とする。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、必要なルール・Runtime仕様・保存仕様を整理する。

#### リスク

便利だからという理由で標準フィールドを増やしすぎると、Studioくんが特定データ構造に太るリスクがある。

#### 確認観点

created_at / updated_at / created_by / updated_by / deleted / is_deleted / sort_order / status などの採用可否と扱いが整理されていることを確認する。

#### 作業会話サマリ


##### 依頼 / 方針

studio_work_incident_data_v0_4.json に次の作業データを追加したい。FRB_VIEW_DEF_GENERATION_RULESレビュー、objectArray/chat保存健全性、chat input mapping、Markdown出力契約、ViewDef代表サンプル整理、固定フィールド名監査、Studio標準メタフィールド定義、文字化けファイル名大量発生対応を整理したい。

##### AI整理

標準メタフィールドは便利だが肥満リスクも高い。候補と採用ルールを先に定義する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0011_001 | 2026-06-21 | user | 作業候補整理 | studio_work_incident_data_v0_4.json に次の作業データを追加したい。FRB_VIEW_DEF_GENERATION_RULESレビュー、objectArray/chat保存健全性、chat input mapping、Markdown出力契約、ViewDef代表サンプル整理、固定フィールド名監査、Studio標準メタフィールド定義、文字化けファイル名大量発生対応を整理したい。 |
| disc_0011_002 | 2026-06-21 | assistant | 作業候補整理 | 標準メタフィールドは便利だが肥満リスクも高い。候補と採用ルールを先に定義する。 |

#### 判断ログ


#### 変更履歴

---

# AI貼り付け用

## Studio改修インシデント レビュー / 次アクション生成プロンプト

<details open>
<summary>プロンプト + TSV を表示</summary>

```text
以下は Studio改修インシデント管理のTSVです。
この内容をもとに、未着手・対応中・保留の作業項目について、次にAIへ依頼すべき作業指示案を作成してください。

条件:
- 既存機能を壊さない
- Studioくん憲法の Data / ViewDef / Action / Runtime 分離を守る
- Runtime内のData固定名は原則NG
- ただし、憲法・仕様に明記されたStudio標準メタフィールドは例外
- v0.4 / v0.5 / v0.6 の作業範囲を混ぜない
- 出力は作業項目ごとの依頼文候補だけにする
- 長文フィールドはtextareaの羅列ではなく、必要に応じてdetailBodyのカード表示を提案する

TSV:
作業ID	Phase	タイトル	種別	分類	優先度	状態	対象ファイル	目的
studio_work_0001	v0.4-split	app.js ソース分割	refactoring	source_split	high	完了	app.js, index.html	既存機能を維持したまま、巨大化した app.js を責務ごとに分割する。
studio_work_0002	v0.5-registry	Renderer / VirtualData / Action のRegistry化	architecture	registry	high	完了	wwwroot/js/core/registry.js, wwwroot/js/renderers/*registry.js, wwwroot/js/virtualData/virtual_data_registry.js, wwwroot/js/markdown/markdown_registry.js, wwwroot/js/actions/action_registry.js, index.html	分岐や固定実装をRegistryへ寄せ、戦略的設計パターンとして差し替え可能な構造へ移行する。
studio_work_0003	v0.6-action-execute-button	toolbar.executeButton / Action 実行対応	feature	action	high	完了	wwwroot/js/actions/action_registry.js, wwwroot/js/actions/action_toolbar.js, wwwroot/js/runtime/load_runtime.js, wwwroot/index.html, wwwroot/styles.css, defs/studio/*execute_button_sample.json	ViewDefで定義された toolbar.executeButton を読み取り、caption と action に応じた主役操作を実行できるようにする。
studio_work_0004	v0.7-viewdef-rules-review	★FRB_VIEW_DEF_GENERATION_RULES / Schema レビュー	rules_review	rules_schema	high	完了	FRB_VIEW_DEF_GENERATION_RULES_ALL_v0_15.md, FRB_VIEW_DEF_GENERATION_RULES_ALL_v0_16.md, frb_view_def_schema_v0_8_action_registry_toolbar.json, wwwroot.zip	現時点の最新Runtime、Registry、toolbar.executeButton、Markdown出力、chat/objectArray仕様に合わせて、ViewDef生成ルールMDをv0.16へ更新する。
studio_work_0005	v0.7-objectarray-save-integrity	objectArray / 履歴配列の保存健全性確認	bugfix	save_integrity	critical	完了	wwwroot/js/renderers/field_controls.js, wwwroot/js/renderers/grid_detail.js, wwwroot/js/runtime/detail_save.js, representative objectArray/chat data/view_def	discussion_history / decision_log / change_history などの配列データが、保存後も配列として保持されることを保証し、detailFooter/chat欄の編集・削除が反映・上書き保存されるようにする。
studio_work_0006	v0.7-chat-input-mapping	chat送信欄の保存先・末尾表示・Markdownリンク/画像対応	feature_fix	chat	high	完了	wwwroot/js/renderers/field_controls.js, wwwroot/js/runtime/detail_save.js, frb_view_def_schema_*.json, FRB_VIEW_DEF_GENERATION_RULES_*.md	chat型で追加コメント入力欄を使う場合に、保存先userField/aiFieldをViewDefで明示し、送信したユーザーコメントをmessages定義位置ではなく会話末尾へ表示する。あわせて、ViewDefで許可されたchat本文に限りMarkdownリンク/画像記法を表示できるようにする。
studio_work_0007	v0.7-markdown-export-contract	Markdown出力契約 / JSON展開情報 / AI貼り付け用	specification	markdown_export	high	未着手	wwwroot/js/markdown/*.js, mdViewer.html, FRB_VIEW_DEF_GENERATION_RULES_*.md, frb_view_def_schema_*.json	Markdown出力ボタンで何を出力できるべきかを、ViewDef生成ルール・Schema・Runtime仕様として整理する。
studio_work_0008	v0.7-filename-encoding-sanitize	Markdown出力ファイル名の文字化け対策	bugfix	file_io	high	未着手	wwwroot/js/core/file_api.js, wwwroot/js/core/fileNameUtils.js or equivalent, wwwroot/js/markdown/*.js, mdViewer.html, backend save/load API if needed	Markdown出力やViewer連携で、Unicodeエスケープ/URLエンコード/HTMLエンティティ風の文字化けファイル名が大量発生する問題を解消する。
studio_work_0009	v0.7-viewdef-sample-fixtures	ViewDef代表サンプル / 健康診断セット整理	maintenance	fixtures	medium	未着手	defs/studio/*, data/studio/*, sample fixtures README	今後の改修時に最低限確認する代表Data/ViewDefセットを整理し、回帰確認の基準を作る。
studio_work_0010	v0.7-fixed-name-audit	Runtime内固定フィールド名監査	architecture_audit	fixed_name	medium	未着手	wwwroot/js/**/*.js, index.html, ViewDef schema/rules	Runtime内に残っている固定フィールド名・固定Action名・固定builder名を棚卸しし、骨格か脂肪かを分類する。
studio_work_0011	v0.7-standard-meta-fields	Studio標準メタフィールド定義	rules_review	standard_fields	medium	未着手	CODING_CONSTRAINTS.md, FRB_VIEW_DEF_GENERATION_RULES_*.md, frb_view_def_schema_*.json	Runtime内Data固定名禁止の例外として認めるStudio標準メタフィールド候補を整理し、採用ルールを定義する。
```

</details>

<details>
<summary>Grid JSON を表示</summary>

```json
{
  "view_def": "studio_work_incident_view_def_v0_2_readable_cards.json",
  "data_file": "studio_work_incident_data_v0_8.json",
  "section": "改修インシデント / 作業項目",
  "row_count": 11,
  "columns": [
    {
      "field": "work_item_id",
      "caption": "作業ID",
      "type": "text"
    },
    {
      "field": "phase",
      "caption": "Phase",
      "type": "text"
    },
    {
      "field": "title",
      "caption": "タイトル",
      "type": "text"
    },
    {
      "field": "incident_type",
      "caption": "種別",
      "type": "select"
    },
    {
      "field": "category",
      "caption": "分類",
      "type": "select"
    },
    {
      "field": "priority",
      "caption": "優先度",
      "type": "select"
    },
    {
      "field": "status",
      "caption": "状態",
      "type": "select"
    },
    {
      "field": "target_files",
      "caption": "対象ファイル",
      "type": "textarea"
    },
    {
      "field": "objective",
      "caption": "目的",
      "type": "textarea"
    }
  ],
  "rows": [
    {
      "work_item_id": "studio_work_0001",
      "phase": "v0.4-split",
      "title": "app.js ソース分割",
      "incident_type": "refactoring",
      "category": "source_split",
      "priority": "high",
      "status": "完了",
      "target_files": "app.js, index.html",
      "objective": "既存機能を維持したまま、巨大化した app.js を責務ごとに分割する。"
    },
    {
      "work_item_id": "studio_work_0002",
      "phase": "v0.5-registry",
      "title": "Renderer / VirtualData / Action のRegistry化",
      "incident_type": "architecture",
      "category": "registry",
      "priority": "high",
      "status": "完了",
      "target_files": "wwwroot/js/core/registry.js, wwwroot/js/renderers/*registry.js, wwwroot/js/virtualData/virtual_data_registry.js, wwwroot/js/markdown/markdown_registry.js, wwwroot/js/actions/action_registry.js, index.html",
      "objective": "分岐や固定実装をRegistryへ寄せ、戦略的設計パターンとして差し替え可能な構造へ移行する。"
    },
    {
      "work_item_id": "studio_work_0003",
      "phase": "v0.6-action-execute-button",
      "title": "toolbar.executeButton / Action 実行対応",
      "incident_type": "feature",
      "category": "action",
      "priority": "high",
      "status": "完了",
      "target_files": "wwwroot/js/actions/action_registry.js, wwwroot/js/actions/action_toolbar.js, wwwroot/js/runtime/load_runtime.js, wwwroot/index.html, wwwroot/styles.css, defs/studio/*execute_button_sample.json",
      "objective": "ViewDefで定義された toolbar.executeButton を読み取り、caption と action に応じた主役操作を実行できるようにする。"
    },
    {
      "work_item_id": "studio_work_0004",
      "phase": "v0.7-viewdef-rules-review",
      "title": "★FRB_VIEW_DEF_GENERATION_RULES / Schema レビュー",
      "incident_type": "rules_review",
      "category": "rules_schema",
      "priority": "high",
      "status": "完了",
      "target_files": "FRB_VIEW_DEF_GENERATION_RULES_ALL_v0_15.md, FRB_VIEW_DEF_GENERATION_RULES_ALL_v0_16.md, frb_view_def_schema_v0_8_action_registry_toolbar.json, wwwroot.zip",
      "objective": "現時点の最新Runtime、Registry、toolbar.executeButton、Markdown出力、chat/objectArray仕様に合わせて、ViewDef生成ルールMDをv0.16へ更新する。"
    },
    {
      "work_item_id": "studio_work_0005",
      "phase": "v0.7-objectarray-save-integrity",
      "title": "objectArray / 履歴配列の保存健全性確認",
      "incident_type": "bugfix",
      "category": "save_integrity",
      "priority": "critical",
      "status": "完了",
      "target_files": "wwwroot/js/renderers/field_controls.js, wwwroot/js/renderers/grid_detail.js, wwwroot/js/runtime/detail_save.js, representative objectArray/chat data/view_def",
      "objective": "discussion_history / decision_log / change_history などの配列データが、保存後も配列として保持されることを保証し、detailFooter/chat欄の編集・削除が反映・上書き保存されるようにする。"
    },
    {
      "work_item_id": "studio_work_0006",
      "phase": "v0.7-chat-input-mapping",
      "title": "chat送信欄の保存先・末尾表示・Markdownリンク/画像対応",
      "incident_type": "feature_fix",
      "category": "chat",
      "priority": "high",
      "status": "完了",
      "target_files": "wwwroot/js/renderers/field_controls.js, wwwroot/js/runtime/detail_save.js, frb_view_def_schema_*.json, FRB_VIEW_DEF_GENERATION_RULES_*.md",
      "objective": "chat型で追加コメント入力欄を使う場合に、保存先userField/aiFieldをViewDefで明示し、送信したユーザーコメントをmessages定義位置ではなく会話末尾へ表示する。あわせて、ViewDefで許可されたchat本文に限りMarkdownリンク/画像記法を表示できるようにする。"
    },
    {
      "work_item_id": "studio_work_0007",
      "phase": "v0.7-markdown-export-contract",
      "title": "Markdown出力契約 / JSON展開情報 / AI貼り付け用",
      "incident_type": "specification",
      "category": "markdown_export",
      "priority": "high",
      "status": "未着手",
      "target_files": "wwwroot/js/markdown/*.js, mdViewer.html, FRB_VIEW_DEF_GENERATION_RULES_*.md, frb_view_def_schema_*.json",
      "objective": "Markdown出力ボタンで何を出力できるべきかを、ViewDef生成ルール・Schema・Runtime仕様として整理する。"
    },
    {
      "work_item_id": "studio_work_0008",
      "phase": "v0.7-filename-encoding-sanitize",
      "title": "Markdown出力ファイル名の文字化け対策",
      "incident_type": "bugfix",
      "category": "file_io",
      "priority": "high",
      "status": "未着手",
      "target_files": "wwwroot/js/core/file_api.js, wwwroot/js/core/fileNameUtils.js or equivalent, wwwroot/js/markdown/*.js, mdViewer.html, backend save/load API if needed",
      "objective": "Markdown出力やViewer連携で、Unicodeエスケープ/URLエンコード/HTMLエンティティ風の文字化けファイル名が大量発生する問題を解消する。"
    },
    {
      "work_item_id": "studio_work_0009",
      "phase": "v0.7-viewdef-sample-fixtures",
      "title": "ViewDef代表サンプル / 健康診断セット整理",
      "incident_type": "maintenance",
      "category": "fixtures",
      "priority": "medium",
      "status": "未着手",
      "target_files": "defs/studio/*, data/studio/*, sample fixtures README",
      "objective": "今後の改修時に最低限確認する代表Data/ViewDefセットを整理し、回帰確認の基準を作る。"
    },
    {
      "work_item_id": "studio_work_0010",
      "phase": "v0.7-fixed-name-audit",
      "title": "Runtime内固定フィールド名監査",
      "incident_type": "architecture_audit",
      "category": "fixed_name",
      "priority": "medium",
      "status": "未着手",
      "target_files": "wwwroot/js/**/*.js, index.html, ViewDef schema/rules",
      "objective": "Runtime内に残っている固定フィールド名・固定Action名・固定builder名を棚卸しし、骨格か脂肪かを分類する。"
    },
    {
      "work_item_id": "studio_work_0011",
      "phase": "v0.7-standard-meta-fields",
      "title": "Studio標準メタフィールド定義",
      "incident_type": "rules_review",
      "category": "standard_fields",
      "priority": "medium",
      "status": "未着手",
      "target_files": "CODING_CONSTRAINTS.md, FRB_VIEW_DEF_GENERATION_RULES_*.md, frb_view_def_schema_*.json",
      "objective": "Runtime内Data固定名禁止の例外として認めるStudio標準メタフィールド候補を整理し、採用ルールを定義する。"
    }
  ]
}
```

</details>