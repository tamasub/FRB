# Studioくん 改修インシデント管理

- 出力日時: 2026/6/28 17:13:51
- 対象: FRB Studio / JSON Object Studio / FRBStudio App 改修計画
- schema_version: studio_work_incident_data_v0_1
- status: active
- 件数: 80

## 基本情報

- タイトル: FRB Studio / JSON Object Studio 改修インシデント管理
- 対象: FRB Studio / JSON Object Studio / FRBStudio App 改修計画
- Schema Version: studio_work_incident_data_v0_1
- 状態: active

### 目的

Studioくん本体改修に関する重要な修正依頼・方針・会話履歴を作業項目ごとに残す。承認ワークフローではなく、インシデント管理・作業項目管理・会話履歴管理を目的とする。

### 運用方針

重要な修正依頼は作業項目として登録する。仕様変更・方針変更・実装方針の会話は discussion_history / decision_log / change_history に残す。作業項目ごとの会話履歴を残し、未来の人間とAIが経緯を追体験できるようにする。

### 標準メタフィールド方針

Runtime内のData固定名は原則NG。ただし、Studio標準メタフィールドとして憲法・仕様に明記されたものは使用可能。例: created_at, updated_at, deleted, is_deleted, created_by, updated_by などは、標準メタフィールドとして定義すれば使用可。

## 作業項目一覧

| 作業ID | Phase | タイトル | 種別 | 分類 | 優先度 | 状態 | 確認状態 | 目的 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| studio_work_0001 | v0.4-split | app.js ソース分割 | refactoring | source_split | high | 完了 | 確認済み | 既存機能を維持したまま、巨大化した app.js を責務ごとに分割する。 |
| studio_work_0002 | v0.5-registry | Renderer / VirtualData / Action のRegistry化 | architecture | registry | high | 完了 | 確認済み | 分岐や固定実装をRegistryへ寄せ、戦略的設計パターンとして差し替え可能な構造へ移行する。 |
| studio_work_0003 | v0.6-action-execute-button | toolbar.executeButton / Action 実行対応 | feature | action | high | 完了 | 確認済み | ViewDefで定義された toolbar.executeButton を読み取り、caption と action に応じた主役操作を実行できるようにする。 |
| studio_work_0004 | v0.7-viewdef-rules-review | ★FRB_VIEW_DEF_GENERATION_RULES / Schema レビュー | rules_review | rules_schema | high | 完了 | 確認済み | 現時点の最新Runtime、Registry、toolbar.executeButton、Markdown出力、chat/objectArray仕様に合わせて、ViewDef生成ルールMDをv0.16へ更新する。 |
| studio_work_0005 | v0.7-objectarray-save-integrity | objectArray / 履歴配列の保存健全性確認 | bugfix | save_integrity |  | 完了 | 確認済み | discussion_history / decision_log / change_history などの配列データが、保存後も配列として保持されることを保証し、detailFooter/chat欄の編集・削除が反映・上書き保存されるようにする。 |
| studio_work_0006 | v0.7-chat-input-mapping | ☆彡chat送信欄の保存先・末尾表示・Markdownリンク/画像対応 | feature_fix | chat | high | 完了 | 確認済み | chat型で追加コメント入力欄を使う場合に、保存先userField/aiFieldをViewDefで明示し、送信したユーザーコメントをmessages定義位置ではなく会話末尾へ表示する。あわせて、ViewDefで許可されたchat本文に限りMarkdownリンク/画像記法を表示できるようにする。 |
| studio_work_0007 | v0.7-markdown-export-contract | Markdown出力契約 / JSON展開情報 / AI貼り付け用 | specification | markdown_export | high | 未着手 | 未確認 | Markdown出力ボタンで何を出力できるべきかを、ViewDef生成ルール・Schema・Runtime仕様として整理する。 |
| studio_work_0008 | v0.7-filename-encoding-sanitize | Markdown出力ファイル名の文字化け対策 | bugfix | file_io | high | 未着手 | 未確認 | Markdown出力やViewer連携で、Unicodeエスケープ/URLエンコード/HTMLエンティティ風の文字化けファイル名が大量発生する問題を解消する。 |
| studio_work_0009 | v0.7-viewdef-sample-fixtures | ViewDef代表サンプル / 健康診断セット整理 | maintenance | fixtures | medium | 未着手 | 未確認 | 今後の改修時に最低限確認する代表Data/ViewDefセットを整理し、回帰確認の基準を作る。 |
| studio_work_0010 | v0.7-fixed-name-audit | Runtime内固定フィールド名監査 | architecture_audit | fixed_name | medium | 未着手 | 未確認 | Runtime内に残っている固定フィールド名・固定Action名・固定builder名を棚卸しし、骨格か脂肪かを分類する。 |
| studio_work_0011 | v0.7-standard-meta-fields | Studio標準メタフィールド定義 | rules_review | standard_fields | medium | 未着手 | 未確認 | Runtime内Data固定名禁止の例外として認めるStudio標準メタフィールド候補を整理し、採用ルールを定義する。 |
| studio_work_0012 | v0.7-json-select-folder-hierarchy | JSON / ViewDef 選択一覧のサブフォルダー階層対応 | feature |  | high | 完了 | 確認済み | JSON / ViewDef 選択一覧を、フラットなdatalistではなくフォルダー階層で選べるツリー型ファイルピッカーへ変更する。data/json配下およびdefs配下のサブフォルダーJSONを手動ツリーJSONなしで自動表示し、文字列検索にも対応する。 |
| studio_work_0013 | v0.8-url-param-launch-load | 起動URLパラメータによるData/ViewDef自動読込 | feature |  | high | 完了 | 確認済み | 記事やREADMEからURLをクリックするだけで、指定されたData JSON / ViewDef JSON / Markdownを自動読込し、読者がStudioくん上で同じ画面・同じデータを体験できるようにする。 |
| studio_work_0014 | v0.9-json-object-studio-branding | FRB Studio / JSON Object Studio 正式表示名・app_info導入 |  |  | high | 完了 | 確認済み | 画面上の正式表示名を FRB Studio / JSON Object Studio へ整理し、現在のブランド・プロダクト名・version・revision・taglineを app_info.json で管理できるようにする。 |
| studio_work_0015 | v0.9-versioned-incident-management | Version / Revision / Phase 分離とVersion Detail連携 | data_model | incident_versioning | high | 未着手 | 未確認 | Version / Revision / Phase の役割を分離し、IncidentがどのVersionで見つかり、どのVersionで対応され、どのVersion Detailに含まれたかを追跡できるようにする。 |
| studio_work_0016 | v0.9-rules-json-source-of-truth | ルール系Data JSON原本化 / Foundation Rules追加 | data_design | rules_data | high | 未着手 | 未確認 | Markdownをルール原本にせず、ルール・制約・レビュー対象はドメイン別Data JSONを原本として管理し、共通ViewDefでレビューできるようにする。 |
| studio_work_0017 | v0.9-rule-review-common-viewdef-polish | 共通Rule Review ViewDefの汎用化仕上げ | improvement | viewdef_polish | low | 未着手 | 未確認 | rule_review_common_view_def_v0_1.json を特定データ専用の匂いから切り離し、複数ドメインのルールレビューで安全に使える共通ViewDefへ整える。 |
| studio_work_0018 | v0.9-json-utf8-human-readable-save | Data JSONの日本語可読保存 | bugfix_improvement | encoding | high | 未着手 | 未確認 | Data JSONを人間が直接読めるUTF-8日本語で保存し、\uXXXX だらけの人間拒否モードを避ける。 |
| studio_work_0019 | v0.10-markdown-preview-display-mode | 表示モードのMarkdownプレビュー対応 | feature | markdown | medium | 完了 | 確認済み | textarea / chat / detailBodyカードなど、Markdown記法を許可した文言欄について、表示モードではMarkdownプレビューとして表示し、編集時はMarkdown原文を編集できるようにする。 |
| studio_work_0020 | v0.11-mdviewer-blur-preview-mode | Markdown Viewer / Editor のblur時プレビュー自動復帰 | feature | markdown | high | 完了 | 確認済み | Markdown Viewer / Editor で本文textareaを編集した後、前へ/次へや手動Viewer切替を行わなくても、カーソルが本文エディターから外れた時点で自動的にViewer表示へ戻るようにする。 |
| studio_work_0021 | v0.11.1-mdviewer-single-pane-blur-preview | ★Markdown Viewer / Editor の単一欄blurプレビュー再チャレンジ |  |  | high | 完了 | 確認済み | Editorモードで入力欄とプレビュー欄を2つ並べず、1つの欄で、テキストボックスにフォーカスがある時だけMarkdown原文入力モード、フォーカスが外れたらMarkdownプレビューモードへ戻る操作感にする。 |
| studio_work_0022 | v0.12-rules-update-reporting-policy | AI作業対象ファイル記録 / インシデント回答記録ルール整備 | rules_review |  | high | 完了 | 確認済み | AI作業時のファイル更新ルールを整理し、root data/defs を過剰に保護しすぎないこと、AIが更新したファイルをインシデントJSONへ記録すること、インシデント対応後の報告内容をAI回答欄へ残すことをルール化する。 |
| studio_work_0023 | v0.11.7-mdviewer-dirty-block-comment | Markdown汚し方式の吹き出しFRBコメント |  |  | high | 完了 | 確認済み | Markdownプレビュー上の意味ブロックに対して、右クリックからFRBコメントを追加できるようにする。コメントはsidecar JSONではなく、Markdown本文をあえて汚す形式で挿入し、レビュー会話へそのまま貼り付けられる体験を確認する。 |
| studio_work_0024 | v0.13-md-block-model-foundation | Markdown Block Model基盤 / SentenceBlock化 |  |  | high | 完了 | 確認済み | Markdown本文を直接文字列編集するのではなく、見出し・段落・リスト・表・コードブロック等のBlock構造へ分解し、UI上で選択可能なSentenceBlock/Blockとして扱う基盤を作る。 |
| studio_work_0025 | v0.13.1-md-sentence-insert-delete | SentenceBlockの＋挿入 / 削除 / Markdown再生成 | feature |  | high | 完了 | 確認済み | カレントSentenceBlockの点線枠付近に「＋」を表示し、前後へのセンテンス挿入と既存センテンス削除を行い、Markdownへ綺麗に再生成できるようにする。 |
| studio_work_0026 | v0.13.2-md-table-cell-editor | Markdown表セル単位編集 | feature |  | high | 完了 | 確認済み | Markdown表をTableBlockとして認識し、セル単位でクリック選択・編集ダイアログ表示・値更新・Markdown表再生成を行えるようにする。 |
| studio_work_0027 | v0.13.3-md-comment-sidecar-json | SentenceBlock / TableCell コメント sidecar JSON | feature |  | high | 完了 | 確認済み | Markdown本文を汚さずに、SentenceBlockやTableCellへコメントを付けられるsidecar JSON方式を導入する。 |
| studio_work_0028 | v0.13.4-md-comment-review-ui | Markdownコメント表示 / 解決 / コメント一覧UI | feature |  | medium | 完了 | 確認待ち | SentenceBlock/TableCellに付与されたコメントを、本文上のバッジ・サイド一覧・解決状態として確認できるレビューUIを整える。 |
| studio_work_0029 | v0.13.5-md-roundtrip-save-safety | Markdown Block編集の保存安全性 / RoundTrip / Diff確認 |  |  | high | 完了 | 確認済み | Block編集・表セル編集・コメント操作後も、Markdown本文とsidecar JSONが安全に保存され、意図しない本文破壊が起きないことを確認する保存安全性レイヤーを作る。 |
| studio_work_0030 | v0.13.6-md-copilot-table-review-fixture | Copilot表形式計画案レビュー用fixture | maintenance |  | medium | 完了 | 確認済み | Copilotが出力しがちな表形式の計画案Markdownを代表サンプルとして用意し、表セル編集・セルコメント・SentenceBlockコメントの確認に使えるfixtureを整備する。 |
| studio_work_0031 | v0.13.3.1-md-comment-sidecar-api-save-fix | MarkdownコメントSidecar JSONのAPI実ファイル保存対応 | bugfix |  | high | 完了 | 確認済み | mdViewerで作成したMarkdownコメントSidecar JSONを、localStorageだけでなく data/markdown 配下の実ファイルとして保存・読込できるようにする。 |
| studio_work_0032 | v0.13.4.1-md-comment-review-sidebar-compact-layout | Markdownコメントレビュー左サイドバーのコンパクトレイアウト調整 |  |  | high | 完了 | 確認済み | v0.13.4で追加したコメントレビューUIにより、100%表示時に左バーが縦方向へ収まりにくくなったため、右バー化する前に左バー内の目次・ドキュメントメタ・コメントレビューをコンパクト化し、各領域内スクロールで操作できるようにする。 |
| studio_work_0033 | v0.13.5-md-roundtrip-save-safety | Markdown Block編集の保存安全性 / RoundTrip / Diff確認 |  |  | high | 完了 | 確認済み | Block編集・表セル編集・Sidecarコメント操作後も、Markdown本文とSidecar JSONが安全に保存され、意図しない本文破壊や表構造崩れが起きないことを保存前後で確認する。 |
| studio_work_0034 | v0.13.7-md-raw-block-dialog-editor | Markdown通常BlockのRaw Markdownダイアログ編集 | feature |  | high | 完了 | 確認済み | Markdown Viewer / Editor上で、表セルだけでなく通常の本文Blockも、左クリックまたは右クリックメニューから小ダイアログで軽く編集できるようにする。ダイアログには見た目のテキストではなく、# / - / > / ``` などを含むRaw Markdown断片をそのまま表示し、編集者がMarkdown構造を理解した状態で更新できるようにする。 |
| studio_work_0035 | v0.13.8-md-editor-workplace-safe | Markdown Editorの職場Edge安全化 / 実戦UX安定化 | feature_fix |  | high | 完了 | 確認済み | Markdown Editorを職場環境でも実戦投入できる編集器へ寄せる。会社Edge環境での貼り付け時に編集ダイアログが閉じる問題を防ぎ、sentence挿入・空Markdown・/code挿入・初期Editor表示など、mdViewer.htmlの編集体験を安定化する。 |
| studio_work_0036 | v0.13.9-md-editor-nonblocking-ux | Markdown Editorの非ブロッキング通知 / 初期表示安全化 / Sidecarコメントダイアログ統一 | feature_fix |  | high | 完了 | 確認済み | Markdown Editorの操作感をもう一段上げる。OKを押すだけの情報ダイアログを非ブロッキングなタイマー式メッセージラベルへ置き換え、初期表示では勝手にファイルを読まず、Sidecarコメント入力も既存の新しいダイアログUIへ統一する。 |
| studio_work_0037 | v0.13.10-main-json-select-reset-toast-ux | Main画面のJSON選択時ViewDef再解決 / 非ブロッキング通知化 | feature_fix |  | high | 完了 | 確認済み | JSON Object Studio本体画面で、対象JSONを選択した時に古いViewDef選択状態を引きずらず、選択されたData JSON内のview_def定義からViewDefを再解決して読み直す。あわせて、Main画面のOKだけ情報メッセージを、Markdown Editor側と同じ非ブロッキングなタイマー式メッセージへ寄せる。 |
| studio_work_0038 | v0.13.10-index-studio-tool-dock-layout | index.html Studioツールドック導線 / Viewer・Outputメニュー整列 |  |  | medium | 完了 | 確認済み | JSON Object Studio本体画面のヘッダーに、Markdown Viewer / DiffJson Viewer / MetaDiff Hypothesis Viewer への導線をStudioツール群として追加し、既存のMarkdown出力ボタン群も含めて、横幅に応じて自然に整列・折り返しできるメニュー配置へ調整する。 |
| studio_work_0039 | v0.14.0-decision-log-confirmation-governance | 判断ログ系項目見直し / AI確認種別明示 / 最新ソース確認ルール追加 | rules_review | decision_log_governance | high | 完了 | 確認済み | AI駆動開発における判断ログを、単なる作業説明ではなく、期待値・例外条件・受入条件・テストパターン生成の種として扱えるようにする。あわせて、AIが作業報告で『確認した』と言う場合の確認種別を明示し、最新ソース未確認による古いソース前提の修正事故を防ぐ。 |
| studio_work_0040 | v0.14.1-data-viewdef-candidates | Data JSON内ViewDef候補リスト / ViewDef生死確認導線 | feature_design | viewdef_management | high | 完了 | 確認済み | Data JSON側で、そのDataに対して利用可能なViewDef候補を複数指定できるようにし、Studio上ではData JSONに明示された候補だけを手動切替対象として扱う。これにより、DataとViewDefの紐づきを明確化し、未参照ViewDefを棚卸し・掃除しやすい状態を作る。 |
| studio_work_0041 | v0.14.2-incident-prompt-copy-action | インシデント依頼プロンプト自動生成コピーAction | feature |  | high | 完了 | 確認済み | インシデント管理画面のグリッド上部に、選択中作業項目からAI依頼プロンプトを自動生成してクリップボードへコピーするActionボタンを追加する。毎回incident_fileとphaseを手作業でコピーして依頼ひな形へ貼り付ける負荷とミスを減らし、AI作業依頼の入口品質を安定させる。 |
| studio_work_0042 | v0.14.3-v0.14.12-test-evidence-folder-and-diff-contract | テスト証跡フォルダー整理 / Actual-Diff責務分離 / Diff共通フォーマット整理 | architecture_data_contract | test_evidence | high | 完了 | 確認済み | screen_state_smoke_001 と incident_prompt_copy_action のテスト証跡を data/json/03_tests 配下へ集約し、Expected / Actual / Diff / TestPattern / Relation の責務と配置を整理する。あわせて、Actual JSON と Diff JSON の責務を分離し、Diff Result を共通ViewDefで扱える方向へ寄せる。 |
| studio_work_0043 | v0.14.13-foundation-commonization-archive-filename-policy | Foundation / Coding Constraints 共通化・archive退避・ファイル名維持原則 | rules_review | foundation_policy | high | 完了 | 確認済み | Studioくん全体の作業原則として、共通化優先、人間相談、削除データの_archive退避、ルール/ViewDefファイル名維持を憲法・Foundation・AI作業プロンプトへ整理する。 |
| studio_work_0044 | v0.14.14-test-evidence-rules-contract | Test Evidence Rules / Expected-Actual-Diff責務分離 | rules_review | test_evidence | high | 完了 | 確認済み | Expected JSON / Actual JSON / Diff JSON / Test Code の責務をルールとして固定し、テスト失敗時にもDiff証跡が必ず残る文化を定義する。 |
| studio_work_0045 | v0.14.15-test-folder-archive-runtime-policy | Folder / Archive Rules 03_tests正本・旧パス削除・Runtime生成物隔離 | rules_review | folder_policy | high | 完了 | 確認済み | テスト証跡の正本フォルダー、旧パス削除、_archive退避、Playwright runtime生成物隔離、root直下に生成物を生やさない方針を整理する。 |
| studio_work_0046 | v0.14.16-diff-result-common-format-rules | Diff Result Common Format / diff_result_v0_1共通サマリ定義 | rules_review | diff_result_format | high | 完了 | 確認済み | QA Diff と Screen State Diff を同じViewDefで見られる方向へ寄せるため、diff_result_v0_1 の共通サマリ・checks[]共通フィールドをルール化する。 |
| studio_work_0047 | v0.14.17-viewdef-generation-common-viewdef-policy | ViewDef Generation Rules 共通ViewDef優先・既存ファイル名維持・pass標準化 | rules_review | viewdef_generation_rules | high | 完了 | 確認済み | ViewDef生成時に、共通化できるViewDefは共通化を検討し、既存ViewDef修正時は原則ファイル名を変えず、Diff系明細判定はchecks[].passへ寄せるルールを整理する。 |
| studio_work_0048 | v0.14.18-delivery-cleanup-zip-safety-policy | Delivery / Cleanup Rules 成果物ZIP安全化・不要生成物除外 | rules_review | delivery_cleanup | medium | 完了 | 確認済み | AIが成果物を返却する際に、node_modulesやPlaywright生成物、長大パスのテスト結果を混ぜず、Windowsで安全に解凍できるZIPを返すルールを整理する。 |
| studio_work_0049 | v0.14.19-rule-review-status-responsibility-issue | Rule Review承認/確認状態の単一正本化と責務整理 | open_issue | rule_review_workflow | high | 未着手 | 未確認 | Rule Review系データにおける review_status / verification_status / approval_decision の意味、単一正本、UI上の表示・操作責務、人間とAIの権限範囲を整理する。特に、AIがルール本文・章・要約・分類などを修正した場合に、その章またはルール行が未承認・未確認・未レビューへ戻るべきかを運用ルールとして定義する。 |
| studio_work_0050 | v0.14.20-rules-filename-reference-migration | 00_rulesファイル名変更に伴う参照更新インシデント | rules_reference_migration | rules_filename_migration | high | 完了 | 確認済み | 00_rules配下のルール系JSONファイル名整理に伴い、旧ファイル名を参照しているツール・ViewDef・インベントリ・作業依頼テンプレート・ルール本文・インシデントJSONを洗い出し、次工程で新ファイル名へ更新するための作業単位を作成する。 |
| studio_work_0051 | v0.14.21-human-ai-responsibility-rules | 新ルール候補：Human / AI Responsibility Rules 人間・AI責務境界ルール | rules_review |  | high | 未着手 | 未確認 | 人間が最終判断する項目、AIが更新してよい項目、AI更新後に未承認へ戻すべき状態項目を整理し、承認・確認・レビュー状態の責務境界を明確にする。 |
| studio_work_0052 | v0.14.22-definition-of-done-rules | 新ルール候補：Definition of Done Rules 作業完了条件ルール | rules_review |  | high | 未着手 | 未確認 | AI作業における『完了』の条件を定義し、成果物・証跡・インシデント更新・返却安全性をそろえる。 |
| studio_work_0053 | v0.14.23-change-impact-risk-classification-rules | 新ルール候補：Change Impact / Risk Classification Rules 変更影響・リスク分類ルール | rules_review |  | medium | 未着手 | 未確認 | 変更内容を低・中・高・超高リスクに分類し、AI作業時の確認粒度・報告粒度・人間相談要否を切り替えられるようにする。 |
| studio_work_0054 | v0.14.24-traceability-rules | 新ルール候補：Traceability Rules ルール・インシデント・証跡トレースルール | rules_review |  | high | 未着手 | 未確認 | Rule / Incident / Expected / Actual / Diff / ViewDef / Release のつながりを辿れるようにするためのトレーサビリティ方針を整理する。 |
| studio_work_0055 | v0.14.25-test-runner-execution-rules | 新ルール候補：Test Runner / Execution Rules 共通テストランナー実行ルール | rules_review |  | high | 未着手 | 未確認 | テストコードをケースごとに増やすのではなく、実行言語ごとの共通ランナーへ寄せ、Test Pattern / Expected JSONを増やす運用を整理する。 |
| studio_work_0056 | v0.14.26-migration-backward-compatibility-rules | 新ルール候補：Migration / Backward Compatibility Rules 移行・互換・廃止ルール | rules_review |  | high | 未着手 | 未確認 | ファイル名変更・フォルダー移行・互換フィールド追加時に、旧名・旧パス・互換項目をどう扱うかを定義する。 |
| studio_work_0057 | v0.14.27-ai-work-context-package-rules | 新ルール候補：AI Work Context Package Rules AI作業文脈パッケージルール | rules_review |  | medium | 未着手 | 未確認 | AIに作業依頼するときの最小文脈セット、優先順位、添付ZIPとraw URLの扱いをルール化する。 |
| studio_work_0058 | v0.14.28-git-release-branch-rules | 新ルール候補：Git / Release / Branch Rules Git・リリース・ブランチ運用ルール | rules_review |  | medium | 未着手 | 未確認 | AI返却ZIP、GitHub main、release tag、GitHub Pages公開物、_archiveの関係を整理し、正本と成果物の位置づけを明確にする。 |
| studio_work_0059 | v0.14.29-security-public-data-rules | 新ルール候補：Security / Public Data Rules 公開データ・安全管理ルール | rules_review |  | high | 未着手 | 未確認 | GitHub Pagesや記事連携で公開してよいData/Defsと、ローカル限定・非公開にすべき情報の境界を整理する。 |
| studio_work_0060 | v0.14.30-error-incident-escalation-rules | 新ルール候補：Error / Incident Escalation Rules エラー・違和感・再発防止ルール | rules_review |  | medium | 未着手 | 未確認 | AI作業中に発生したエラー、ユーザー環境のみの不具合、仕様未確定の違和感をどうインシデント化・エスカレーションするかを整理する。 |
| studio_work_0061 | v0.14.32-viewdef-header-search-layout-rules | ViewDef作成ルール：ヘッダー基本情報と検索項目のコンパクト表示方針 | rules_review | viewdef_generation_layout | medium | 完了 | 確認済み | ViewDef作成時に、ヘッダー部・基本情報・画面検索項目をコンパクトに見せるための表示方針をルール化する。ヘッダー基本情報は1行に収まる項目だけを表示し、長文・複数行項目を原則非表示にすることで、詳細本文やグリッドへ視線を早く移せる画面にする。 |
| studio_work_0062 | v0.14.37-git-diff-export-command-profile | Studioくん Git Diff Run / Export-DiffToJson.ps1 CommandProfile連携 | feature | git_diff_command_profile | high | 完了 | 確認済み | Studioくんのグリッド一覧上部に Git Diff Run 系の実行ボタンを追加し、選択行のGit差分出力設定から Program.cs の許可済みCommandProfileを経由して Export-DiffToJson.ps1 を実行できるようにする。Git Diff結果をJSON化し、Studioくんでレビュー・AI差分物語へ接続する入口を作る。 |
| studio_work_0063 | v0.14.38-test-runner-command-profile | Studioくん Test Run / TestRunner.ps1 CommandProfile連携 | feature | test_runner_command_profile | high | 完了 | 確認済み | Studioくんから許可済みのテスト実行プリセットを選択し、Grid上部の Test Run ボタンで TestRunner.ps1 を起動できるようにする。コマンド入力が苦手な人間でも、意味の分かるCaption付きData JSON行を選ぶだけで、Playwright UI起動やNode標準テスト実行を再現可能にする。 |
| studio_work_0064 | v0.14.39-test-runner-result-classification | Studioくん Test Runner 結果分類 / テスト失敗通知改善 | improvement | test_runner_result_ui | high | 完了 | 確認済み | TestRunner wait mode の exit_code=1 をAction起動エラーとして扱わず、ランチャー起動失敗・テスト成功・テスト失敗を result_kind で分類して返し、Studioくん画面上でもテスト失敗を専用通知として表示できるようにする。 |
| studio_work_0065 | v0.15.1-common-enums-definition | common_enums_v0_1.json 追加 / Enumを値の正本として定義 | data_design | enum | high | 完了 | 確認済み | EnumをStudioくんの値語彙の最小管理単位として追加し、cd/name/description/sort_order/deprecatedなどを持てる共通定義ファイルを作る。 |
| studio_work_0066 | v0.15.2-fieldtype-enumref-resolve | common_types FieldType の enumRef / options解決対応 | feature |  | high | 完了 | 確認済み | FieldTypeからEnumを参照できるようにし、baseType=select かつ enumRefありの場合に common_enums のitemsをoptionsとして解決できるようにする。 |
| studio_work_0067 | v0.15.3-context-enums-added | context系Enum / context_read_timing FieldType追加 | feature | context_enum | high | 完了 | 確認済み | AI文脈制御で利用する context_read_timing などのEnumを追加し、ViewDefやData行のcontext_refsで使える共通語彙を整える。 |
| studio_work_0068 | v0.15.4-common-types-options-to-enumref | 既存 common_types options のEnum参照化整理 | refactoring | common_types_cleanup | medium | 完了 | 確認済み | 既存common_types_v0_1.jsonでFieldType内にだらだら直書きされているselect optionsを棚卸しし、共通Enumへ移せるものは enumRef 参照へ寄せる。 |
| studio_work_0069 | v0.15.5-viewdef-context-read-contract | ViewDef文脈制御 read_contract 初期実装 / 主文脈・対象文脈モデル見直しへ移行 | architecture |  | high | 完了（後続あり） | 見直し反映済み | ViewDefにAI作業前に読むべき追加文脈を定義できるようにする初期入口を作った上で、画面全体の主文脈と個別明細の対象文脈を分ける正式モデルへ移行する。 |
| studio_work_0070 | v0.15.6-grid-column-resize-viewdef-save | グリッド列幅変更 / ViewDef明示保存 | feature | grid_viewdef | medium | 未着手 | 未確認 | グリッド表示中に列幅をドラッグ変更できるようにし、必要な場合のみ明示操作で現在のViewDefの fields[].grid.width へ反映できるようにする。 |
| studio_work_0071 | v0.15.7-objectarray-section-search | objectArray / 履歴セクションのまとまり検索対応 | feature |  | high | 未着手 | 未確認 | discussion_history / change_history / decision_log などの objectArray 形式の深い階層を、項目単位ではなく『会話履歴』『変更履歴』『判断ログ』『履歴全体』のようなセクション単位で検索できるようにする。 |
| studio_work_0072 | v0.15.8-gitdiff-result-viewer-launch | GitDiffRun結果JSONのDiffJsonViewer自動表示 | feature | gitdiff_viewer | high | 未着手 | 未確認 | StudioくんからGitDiffRunを起動した後、生成された差分JSONをwwwroot配下の一時公開フォルダーへ出力し、DiffJsonViewer.html?src=... で自動表示できるようにする。 |
| studio_work_0073 | v0.15.9-gitdiff-large-result-handling | GitDiffRun巨大差分JSONのViewer表示上限 / エラー表示 | feature | gitdiff_large_data | medium | 未着手 | 未確認 | wwwroot配下に生成された差分JSONがDiffJsonViewer.htmlで扱えないほど大きい場合に、無理に表示せず、安全にサイズ上限エラーとして扱えるようにする。 |
| studio_work_0074 | v0.16.0-proposal-driven-jobflow | AI提案駆動JobFlow / JobControl JSON構想 | architecture |  | high | 未着手 | 未確認 | AI作業の開始点を、人間の明示依頼だけでなくAI改善提案JSONからも始められるようにする。Improvement Proposal JSON → 人間承認 → JobControl JSON → Job実行 → TestResult / GitDiff / AIテスト物語 / AI差分物語 / Incident更新 までを、AI協働可能なJobFlowとして定義する。 |
| studio_work_0075 | v0.15.5.1-context-model-cleanup | 主文脈 / 対象文脈モデル整理 | architecture_cleanup | context_model | high | 完了 | 確認済み | v0.15.5初期実装で見えたズレを踏まえ、主文脈と対象文脈の用語・JSON配置・明細構造・表示方針を確定する。 |
| studio_work_0076 | v0.15.5.2-main-context-header-panel | 主文脈ヘッダー表示 / 展開編集パネル | feature | context_ui | high | 完了 | 確認済み | ViewDef全体にかかる主文脈を、画面ヘッダー/概要部分に要約表示し、ボタン押下で明細を確認・必要に応じて編集できるようにする。 |
| studio_work_0077 | v0.15.5.3-target-context-detail-panel | 対象文脈Detail上部表示 / context_refs編集 | feature | context_ui | high | 完了 | 確認済み | Data明細オブジェクト内の context_refs[] を対象文脈として、Detail画面の上部に要約・確認・編集できる形で表示する。 |
| studio_work_0078 | v0.16.1-studio-context-engineer-wannabe-mission-draft | Studio Context Engineer Wannabe / Mission定義ドラフト | data_design | mission_context_design | high | 完了 | 確認済み | Studio Context Engineer Wannabe — 文脈設計者になりたいStudioくん構想の初期ドラフトとして、AIへ複数StepのMissionを依頼するためのMission定義JSONと、AIから作業完了時に受け取るMission実行結果サマリーJSONを作成する。 |
| studio_work_0079 | v0.16.2-detail-subgrid-table-edit-core-mvp | Studio Table Edit Core / Detailサブグリッド編集MVP | feature | table_edit_core | high | 完了 | 確認済み | Detail画面内の objectArray / stringArray サブグリッドを汎用的に編集できるStudio標準テーブル編集MVPを作る。Mission定義JSONの steps.outputs / success_conditions / inputs / depends_on などを、Studio上で直接育てられる状態にする。 |
| studio_work_0080 | v0.16.3-incident-contextdef-open-work-draft | Incident ContextDef / 未完了作業の文脈素案投入 |  |  | high | 完了 | 確認済み | インシデント管理DataにContextDef項目を追加し、未完了の作業項目だけを対象に、AIが作業前に読むべき文脈素案を入れられる状態にする。 |

## 作業項目詳細


### v0.4-split: app.js ソース分割
- 作業ID: studio_work_0001
- 種別: refactoring
- 分類: source_split
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
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
- 確認状態: 確認済み
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
- 確認状態: 確認済み
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
- 確認状態: 確認済み
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
- 状態: 完了
- 確認状態: 確認済み
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

### v0.7-chat-input-mapping: ☆彡chat送信欄の保存先・末尾表示・Markdownリンク/画像対応
- 作業ID: studio_work_0006
- 種別: feature_fix
- 分類: chat
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/js/renderers/field_controls.js, wwwroot/js/runtime/detail_save.js, wwwroot/js/runtime/CHAT_INPUT_MAPPING_NOTES_v0_7.md, wwwroot/js/runtime/CHAT_MARKDOWN_PREVIEW_FIX_NOTES_v0_8_1.md, styles.css, studio_work_incident_data_v0_9.json

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

送信欄入力がedit.input.userFieldへ保存されること。送信後の追加コメントが最後のAI回答の後ろに表示されること。input.userFieldと同じfieldがmessagesにあっても二重表示されないこと。Markdownリンク [text](./path) と画像 ![alt](./path) がViewDef許可時のみ表示されること。保存済み追加コメントでMarkdown原文とMarkdown previewが二重表示されないこと。保存値はMarkdown原文のまま残り、HTMLがJSONへ混入しないこと。

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


# バグ報告　
- MarkDownプレビューにコメント原文が表示されて、コメント原文が２重表示されている。

# バグ報告後AI回答
1. 送信欄の下に出る preview は入力欄専用にする
2. 保存済み latest_user_comment の末尾表示では preview 枠を出さない
3. 保存済みコメントは Markdown変換済みHTMLだけを1回表示する
4. 編集モードに入った時だけ、原文 + preview を出すか検討


![alt text](./images/chat/tamasub.png)

##### AI追加回答

v0.7-chat-input-mapping バグ対応完了。appendPosition=afterMessages で末尾表示する保存済み追加コメントを、編集可能メッセージではなく表示専用Markdownメッセージとして描画するように修正した。これにより、Markdown画像/リンクを含むコメントで「原文 + Markdown preview」が二重表示される問題を解消。保存値はMarkdown原文のまま保持し、表示時のみMarkdown変換する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0006_001 | 2026-06-21 | user | 作業候補整理 | studio_work_incident_data_v0_4.json に次の作業データを追加したい。FRB_VIEW_DEF_GENERATION_RULESレビュー、objectArray/chat保存健全性、chat input mapping、Markdown出力契約、ViewDef代表サンプル整理、固定フィールド名監査、Studio標準メタフィールド定義、文字化けファイル名大量発生対応を整理したい。 |
| disc_0006_002 | 2026-06-21 | assistant | 作業候補整理 | chat入力欄は固定名に逃げず、edit.input.userField / aiField を明示するルールにする。 |
| disc_0006_extra_20260621 | 2026-06-21 | user | Rulesレビューからの追加論点 | チャット欄でMarkdown書式のリンク/画像を扱いたい。追加コメント欄の保存先も固定名ではなくedit.input.userField/aiFieldで明示したい。 |
| disc_0006_003 | 2026-06-21 | user | v0.7-chat-input-mapping作業依頼 | studio_work_incident_data_v0_7.json の v0.7-chat-input-mapping 対応を依頼。チャット欄でMarkdown書式のリンク/画像を扱いたい。追加コメント欄の保存先も固定名ではなくedit.input.userField/aiFieldで明示したい。 |
| disc_0006_004 | 2026-06-21 | user | 送信コメント表示位置の違和感 | 現状ではメッセージ送信すると最後のAI回答の直前の欄に追加されて意味不明な時系列になる。送信したコメントは最後のAI回答の次に表示したい。 |
| disc_0006_005 | 2026-06-21 | assistant | v0.7-chat-input-mapping作業結果 | chatInputConfigでedit.input.userField/aiField/appendPosition/markdownを扱うようにし、appendPosition=afterMessagesの場合はinput.userFieldを通常messages表示から除外して末尾表示するようにした。Markdownリンク/画像は許可されたchatだけ表示変換し、編集可能欄では原文を保持しつつプレビュー表示する。 |
| disc_0006_006 | 2026-06-21 | user | Markdownプレビュー二重表示バグ報告 | AI回答が最終ではない状態でMarkdown画像リンクを送信すると、追加コメント欄に原文が追加され、その下にMarkdown previewも出るため、コメント原文が二重表示される。v0.7-chat-input-mappingのバグ対応として修正したい。 |
| disc_0006_007 | 2026-06-21 | assistant | Markdownプレビュー二重表示バグ対応結果 | 保存済みの末尾追加コメントは入力欄/編集中UIではなく会話タイムライン上の保存済みメッセージとして扱う。renderMarkdownOnly表示モードを追加し、Markdown変換済み表示を1回だけ行い、preview枠は出さないようにした。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0006_001 | 2026-06-21 | chat送信欄の保存先はRuntime固定名ではなく、ViewDefのedit.input.userField / aiFieldを優先する。 | データごとにコメント欄のフィールド名は異なるため、Runtimeがuser_reply等の固定Data名へ依存するとStudioくんが特定データ構造に太るため。 |
| dec_0006_002 | 2026-06-21 | 送信欄由来のユーザーコメントはappendPosition=afterMessagesを既定とし、会話末尾へ表示する。 | messages定義順の途中にあるuserFieldへ追記すると、最後のAI回答の直前に新コメントが割り込んで時系列が崩れるため。 |
| dec_0006_003 | 2026-06-21 | chat内Markdownリンク/画像はViewDefで許可された場合のみ表示変換し、保存値はMarkdown原文のまま保持する。 | 全フィールド自動Markdown化は危険だが、作業会話にスクリーンショットリンクや画像を残す用途は重要なため。 |
| dec_0006_004 | 2026-06-21 | 保存済みの末尾追加コメントではMarkdown preview枠を表示しない。 | 送信済みコメントは入力中UIではなく保存済み会話メッセージであり、原文とpreviewを同時に出すと同一コメントが二重表示されて時系列レビューが読みにくくなるため。 |
| dec_0006_005 | 2026-06-21 | appendPosition=afterMessages の userField 表示は renderMarkdownOnly の表示専用モードで描画する。 | Markdown画像/リンクを表示しつつ、contenteditableによるHTML保存値混入やpreview二重表示を避けるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0006_001 | 2026-06-21 | chat_input_mapping | chat送信欄はuserFieldの定義位置に従って表示され、latest_user_commentがlatest_ai_responseの前にある場合、新規送信コメントも最後のAI回答の前へ割り込んでいた。Markdownリンク/画像もchat本文では表示変換されなかった。 | edit.input.userFieldを保存先として扱いながら、appendPosition=afterMessagesの場合はuserFieldを会話末尾へ表示するように変更。Markdownリンク/画像は許可されたchat本文で表示変換するようにした。 | チャットの時系列を自然に保ち、作業会話にスクリーンショットや関連資料リンクを残せるようにするため。 |
| chg_0006_002 | 2026-06-21 | chat_markdown_preview_fix | 末尾表示された保存済み追加コメントが編集可能メッセージとして描画され、Markdown記法を含む場合に本文原文とMarkdown previewが同時に表示されていた。 | 末尾表示された保存済み追加コメントは表示専用Markdownメッセージとして描画され、Markdown変換済み表示だけを1回表示する。preview枠は入力中/編集中UI専用に限定した。 | チャットタイムライン上の保存済みコメントを読み物として自然に表示し、二重表示とHTML保存値混入を防ぐため。 |

### v0.7-markdown-export-contract: Markdown出力契約 / JSON展開情報 / AI貼り付け用
- 作業ID: studio_work_0007
- 種別: specification
- 分類: markdown_export
- 優先度: high
- 状態: 未着手
- 確認状態: 未確認
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
- 確認状態: 未確認
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
- 確認状態: 未確認
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
- 確認状態: 未確認
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
- 確認状態: 未確認
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


### v0.7-json-select-folder-hierarchy: JSON / ViewDef 選択一覧のサブフォルダー階層対応
- 作業ID: studio_work_0012
- 種別: feature
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: Program.cs, wwwroot/index.html, wwwroot/app.js, wwwroot/js/core/viewdef_resolver.js, wwwroot/js/ui/file_tree_picker.js, wwwroot/styles.css

#### 目的

JSON / ViewDef 選択一覧を、フラットなdatalistではなくフォルダー階層で選べるツリー型ファイルピッカーへ変更する。data/json配下およびdefs配下のサブフォルダーJSONを手動ツリーJSONなしで自動表示し、文字列検索にも対応する。

#### 背景

現在のJSON選択一覧は data 配下のJSONがフラットに並ぶため、test_patterns や tests_screen_state などのサブフォルダー内ファイルが混ざって表示され、目的のJSONを探しにくい。今後Studioくん自身の管理データ、制約、テストパターン、画面状態、実験ログが増えるほど、フォルダー階層で整理できることが必須になる。

#### 対象範囲

Program.csでdata/defs配下のJSONを再帰列挙し、相対パスをAPI一覧として返す。load/save/dropは相対パスを安全に扱う。フロント側はAPIが返す相対パス一覧から自動でツリーを生成し、フォルダー開閉・ファイル選択・文字列検索を行う。日本語displayName/manifest管理は後続検討とする。

#### 対象外

日本語ファイル名の全面採用、日本語表示名レジストリ、既存ファイルの一括リネーム、過去の文字化けファイル名の一括修復はこの作業では必須にしない。まずはサブフォルダー階層対応を優先し、日本語名/日本語説明表示は後続候補として整理する。

#### 固定名方針

Runtimeが特定のDataフィールド名に依存しない方針は維持する。ファイル一覧については data / defs というStudioの管理ルートは骨格として扱うが、配下のフォルダー名やファイル名は固定しない。読込対象はAPIが返す相対パスで扱う。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、ファイル一覧APIとUI選択処理を安全に拡張する。

#### リスク

basenameだけで読込・保存している箇所が残ると、同名ファイル衝突や別フォルダーへの誤保存が起きる。Windowsの区切り文字、URLエンコード、日本語ファイル名、文字化けファイル名、既存API互換性、Drop時の管理対象コピー先との整合に注意する必要がある。

#### 確認観点

data/json/test_patterns/foo.json のようなサブフォルダーJSONがツリー表示されること。defs/studio/foo.json のようなViewDefもツリー表示されること。検索語で相対パス検索できること。選択後に相対パスが入力欄へ入り、読み込み・上書き保存できること。同名ファイルが別フォルダーにあっても区別できること。

#### 作業会話サマリ


##### 依頼 / 方針

JSON選択一覧をフォルダー階層に対応してほしい。JSONフォルダー配下のサブフォルダーに対応してほしい。ViewDefも同様。日本語ファイル名または日本語説明表示も将来的に検討したいが、まずサブフォルダー対応は必須。

##### AI整理

サブフォルダー対応は先に作業項目化する価値が高い。data/defs の再帰一覧と相対パス読込を先に入れ、英語ファイル名がつらい問題は日本語表示名レジストリやファイル説明メタデータとして後続検討に分離するのが安全。

##### 追加コメント

studio_work_incident_data_v0_10_folder_hierarchy.json の v0.7-json-select-folder-hierarchy 対応を依頼。Program.csも添付。手動でツリー用JSONを作る方式は避けたい。data/json配下とdefs配下のサブフォルダーを自動でツリー表示したい。文字列検索にも対応したい。フォルダー一覧の最新化はリアルタイムでなく、システム全体リロードタイミングでよい。
AI完了報告
1. file-tree-row を flex から grid に変更
2. アイコン列・ファイル名列を明示的に確保
3. file-tree-label を追加して、文字色・表示状態を強制
4. folder名 / file名 用の専用classを追加
5. 万一名前が空になった場合の fallback も追加

##### AI追加回答

対応完了。Program.csで data/defs のJSON一覧を再帰取得し、相対パスで返すように変更。data/defsのload/save/dropでサブフォルダー相対パスを安全に扱えるようにした。フロント側では datalist ではなく独自のツリー型ファイルピッカーを追加し、API一覧の相対パスから自動でフォルダー階層を生成する。検索は相対パス全体に対するトークン検索として実装。日本語displayName/manifestは未実装で後続検討。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0012_001 | 2026-06-21 | user | JSON選択一覧の階層対応依頼 | JSON選択一覧をフォルダー階層に対応して欲しい。JSONフォルダー配下のサブフォルダーに対応して欲しい。ViewDefも同様。英語のファイル名がつらいので、日本語ファイル名か日本語説明表示も考えたいが、後でもよい。 |
| disc_0012_002 | 2026-06-21 | assistant | 作業項目化方針 | まず必須要件として data / defs 配下の再帰ファイル一覧と相対パス読込・保存を作業項目化する。日本語表示名は、ファイル名そのものを日本語化するより、displayName/descriptionを持つmanifest方式を後続候補に分けるのが安全。 |
| disc_0012_003 | 2026-06-21 | user | v0.7-json-select-folder-hierarchy作業依頼 | Program.csも添付して、JSON/ViewDef選択一覧のサブフォルダー階層対応を依頼。手動でツリー用JSONを作る方式は避け、Program.csの再帰一覧とJS側の自動ツリー生成で対応したい。文字列検索も必要。 |
| disc_0012_004 | 2026-06-21 | assistant | v0.7-json-select-folder-hierarchy作業結果 | Program.csでListJsonFilesを再帰列挙に変更し、SafeJsonPath/SafeDataPath/ToApiNameをサブフォルダー相対パス対応にした。wwwroot側にfile_tree_picker.jsを追加し、入力欄からフォルダー開閉・検索・選択できる独自ツリーUIを導入した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0012_001 | 2026-06-21 | JSON選択一覧はbasenameではなくrelativePathを内部値として扱う。 | サブフォルダー対応後は同名ファイルが複数存在し得るため、basenameだけでは読込・保存先を一意に決められない。 |
| dec_0012_002 | 2026-06-21 | data と defs の両方でサブフォルダー階層対応を行う。 | 対象JSONだけでなくViewDefも増え続けるため、片方だけ階層対応すると運用上の迷子が残るため。 |
| dec_0012_003 | 2026-06-21 | 日本語ファイル名/日本語説明表示は、サブフォルダー対応後の後続検討に分離する。 | ファイル名エンコーディング問題と混ぜると原因切り分けが難しくなる。まずASCII寄りファイル名＋日本語displayName/description候補を安全策として検討する。 |
| dec_0012_001 | 2026-06-21 | ツリー構造は手動JSONではなく、APIが返す相対パス一覧からJS側で自動生成する。 | フォルダー追加やファイル移動のたびに管理用JSONを手で更新する運用は、Studioくんのやる気回復UIとして逆効果であり、保守負荷も高いため。 |
| dec_0012_002 | 2026-06-21 | 日本語ファイル名/displayName/manifest管理は今回のスコープ外とし、まずサブフォルダー階層と検索を優先する。 | フォルダー階層対応、文字化けファイル名、表示名管理を同時に進めると原因切り分けが難しくなるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0012_001 | 2026-06-21 | folder_hierarchy_picker | JSON/ViewDef選択一覧はフラットな入力欄+datalist中心で、サブフォルダー階層が見えず、長い英語ファイル名が大量に並んで探しづらかった。 | Program.csが再帰的にJSON一覧を相対パスで返し、フロント側が相対パスからフォルダー階層ツリーを自動生成する。検索語入力時は相対パス全体で絞り込み、該当ファイルを選択できる。 | ファイル選択を「長い一覧」から「整理された棚」に変え、Studioくんを使う心理的負荷を下げるため。 |

### v0.8-url-param-launch-load: 起動URLパラメータによるData/ViewDef自動読込
- 作業ID: studio_work_0013
- 種別: feature
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/index.html, wwwroot/app.js, wwwroot/js/runtime/load_runtime.js, wwwroot/js/core/file_api.js, wwwroot/js/core/viewdef_resolver.js, mdViewer.html, Program.cs if API routing/relative path handling is needed

#### 目的

記事やREADMEからURLをクリックするだけで、指定されたData JSON / ViewDef JSON / Markdownを自動読込し、読者がStudioくん上で同じ画面・同じデータを体験できるようにする。

#### 背景

AI駆動開発研究日誌やZenn/Qiita記事でStudioくんの体験を読者に共有するには、説明だけでは足りない。記事内に「この画面をStudioで開く」リンクを置き、起動URLにJSONファイルパスを付けて参照できるようにしないと、読者がData/View分離・ViewDef・差分文化を実際に触って追体験できない。以前この話を確認したはずだが、作業項目から抜け落ちていたため、ここで明示的に登録する。

#### 対象範囲

index.html起動時にURLSearchParamsを読み取り、data/view/view_def/md/file等のパラメータを解釈する。例: index.html?data=data/json/sample.json&view=defs/studio/sample_view_def.json。指定がある場合は通常のコンボ選択を待たずに、自動でData JSONとViewDef JSONを読み込む。mdViewer.html側も必要に応じて file=... でMarkdownを自動表示できるようにする。相対パスはdata/defs/docs等の許可ルート内に正規化し、URLエンコード/日本語/空白/サブフォルダーに対応する。

v0.8.1追加スコープ: GitHub Pagesなどの静的ホスティング環境では /api/defs / /api/data が存在しないため、URL起動およびData内 view_def 自動解決時に静的ファイルとして defs/... / data/... を探索する。

#### 対象外

任意の外部URLからのJSON読込、CORS回避、ユーザーPC上の任意ローカルファイル直接参照、認証付きファイル参照、公開用GitHub Pages完全対応はこの作業の必須範囲外。まずはStudio管理配下の相対パス指定とローカルFRBStudio上での体験共有導線を優先する。

#### 固定名方針

URLパラメータ名 data/view/view_def/md/file はStudio標準起動契約として扱うため使用可。ただしData内部のフィールド名をRuntimeが固定参照してはいけない。パラメータ値はファイル相対パスであり、Data構造ではなくStudioの外部入力契約として扱う。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、起動時のURLパラメータ読込と既存load処理への橋渡しを安全に追加する。

#### リスク

URLエンコード/デコード、日本語ファイル名、#を含むパス、空白、Windows区切り文字、サブフォルダー相対パス、GitHub Pages上の相対パス、既存コンボ読込との競合、自動読込失敗時のエラー表示で回帰するリスクがある。特に # はURLフラグメントとして扱われるため、ファイル名や記事リンクではエンコードまたは回避ルールが必要。

#### 確認観点

index.html?data=data/json/foo.json でData JSONだけ自動読込できること。index.html?data=data/json/foo.json&view=defs/studio/foo_view_def.json でData/ViewDefを同時に自動読込できること。サブフォルダー指定が動くこと。URLエンコードされた日本語/空白パスが扱えること。存在しないファイル指定時に画面が壊れず分かりやすいエラーになること。通常の手動コンボ読込・Drop読込に影響しないこと。mdViewer.html?file=... でMarkdownが自動表示されること。記事中の「この画面をStudioで開く」リンク例が成立すること。

v0.8.1確認: GitHub Pages上の index.html?data=data/json/01_main/studio_work_incident_data_v0_12_url_param_launch_load.json で、Data内 view_def から defs/studio_work_incident_view_def_v0_2_readable_cards.json を静的読込できること。/api/defs へアクセスして404にならないこと。localhostでは従来どおりAPI優先で動くこと。

#### 作業会話サマリ


##### 依頼 / 方針

読者に体験してもらう為に、起動URLにJSONのファイルパスをつけて参照できるようにせんとあかん。以前どこかで確認したはずだが、データが作業項目から抜け落ちているので、まず添付JSONに作業項目として追加したい。

##### AI整理

URL起動によるData/ViewDef自動読込は、Studioくんを単なるローカル編集ツールから、記事読者が体験できる共有ビューアへ拡張する重要項目。v0.8-url-param-launch-loadとして新規インシデント登録し、実装は既存の相対パス読込・ファイルツリー対応を土台に進めるのが自然。

##### 追加コメント

GitHub Pages上では /api/defs/... が存在せず、Data内 view_def 自動解決時に 404 になる。v0.8.1-github-pages-static-launch として、静的ホスティング時だけ /api/defs 依存を外してほしい。

##### AI追加回答

v0.8.1-github-pages-static-launch として、GitHub Pages / file:// / 非localhost静的ホスティングでは /api を使わず、defs/... / data/... の静的ファイル探索を優先するように修正。Data内 view_def がファイル名のみの場合も defs/<name> 等から読めるようにした。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0013_001 | 2026-06-21 | user | URL参照作業項目の欠落確認 | 読者に体験してもらう為に、起動URLにJSONのファイルパスをつけて、参照できるようにせんとあかんなって話がでてこない。 |
| disc_0013_002 | 2026-06-21 | assistant | 作業項目化方針 | URLにData/ViewDef/Markdownの相対パスを付けて起動し、読者が記事から同じ画面を開ける導線として作業項目化する。 |
| disc_0013_003 | 2026-06-21 | user | 作業項目追加依頼 | どこかの時点でデータがなくなっている。まず添付JSONに作業項目として追加してほしい。 |
| disc_0013_003 | 2026-06-21 | user | v0.8-url-param-launch-load作業依頼 | studio_work_incident_data_v0_12_url_param_launch_load.json v0.8-url-param-launch-load の対応を依頼。 |
| disc_0013_004 | 2026-06-21 | assistant | v0.8-url-param-launch-load作業結果 | index.html のURL Launch Loadを強化し、data/view/def/mode=readonlyに対応。dataのみ指定時はData内 view_def からViewDefを解決。mdViewer.html は file/md による管理Markdown自動読込に対応。不正パス拒否とReadOnly制御を追加。 |
| disc_0013_008 | 2026-06-21 | user | GitHub Pages上のURL起動エラー | GitHub Pages上では /api/defs/studio_work_incident_view_def_v0_2_readable_cards.json の読み込みに失敗し404になった。v0.8.1-github-pages-static-launch として、静的ホスティング時だけ /api/defs 依存を外す対応を依頼。 |
| disc_0013_009 | 2026-06-21 | assistant | v0.8.1 GitHub Pages静的読込対応 | GitHub Pages / file:// / 非localhost静的ホスティングでは /api を使わず、Data/ViewDefを wwwroot配下の静的ファイルとして探索する方針で対応。Data内 view_def がファイル名のみの場合も defs/<name> などから解決する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0013_001 | 2026-06-21 | URL起動によるData/ViewDef自動読込をv0.8の高優先度作業項目として登録する。 | 読者が記事からStudioくんを直接体験できないと、AI駆動開発研究日誌の『体験共有』が説明止まりになり、Studioくんの価値が伝わりにくいため。 |
| dec_0013_002 | 2026-06-21 | URLパラメータ名 data/view/view_def/md/file はStudio標準起動契約として扱う。 | これはData内部フィールド名ではなく、Studio外部起動インターフェースの契約であり、記事・README・GitHub連携から再利用するための公用語になるため。 |
| dec_0013_003 | 2026-06-21 | v0.8ではURLからのAction実行やReplay実行は行わず、data/view/fileの起動読込とreadonly入口に限定する。 | URLクリックだけでActionを実行できると事故リスクが上がるため、まず追体験リンクとして安全な読込機能に絞る。 |
| dec_0013_004 | 2026-06-21 | URLパラメータのパスは同一アプリ配下の相対パスまたはAPI管理名に限定し、外部URL・絶対パス・親ディレクトリ参照を拒否する。 | 記事やREADMEから安全に起動できるようにしつつ、任意ファイル読込の事故を防ぐため。 |
| dec_0013_006 | 2026-06-21 | GitHub Pagesなどの静的ホスティングでは /api/defs / /api/data に依存せず、静的ファイル探索を優先する。 | GitHub PagesにはFRBStudio.exeのMinimal APIが存在しないため、Dataは読めてもData内 view_def の解決で /api/defs 404 が発生する。記事からStudio体験へリンクするには静的ホスティングで完結する必要があるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0013_001 | 2026-06-21 | incident_added | URL起動でData/ViewDefを参照する作業項目がインシデント管理JSONに存在しなかった。 | studio_work_0013 v0.8-url-param-launch-load として、起動URLパラメータによるData/ViewDef/Markdown自動読込を追加。 | 読者体験リンクを実現するための前提作業として、忘れないように作業管理へ登録するため。 |
| chg_0013_001 | 2026-06-21 | url_param_launch_load | autoLoadFromQuery は view と data の両方がある場合の単純fetchに近く、dataのみ指定・readonly・パス検証・mdViewer file起動は不足していた。 | URLパラメータから data/view(def)/mode=readonly を解釈し、dataだけ指定時はData内 view_def でViewDefを解決する。mdViewer.html は file/md パラメータから管理Markdownを自動読込する。パス検証とreadonly制御を追加した。 | 記事・README・Markdownから読者が同じData/ViewDef/Markdown体験へ直接入れるようにするため。 |
| chg_0013_004 | 2026-06-21 | github_pages_static_launch_fix | Data内 view_def の自動解決は fetchApiJsonWithUrl('defs', name) から /api/defs/... へ向かい、GitHub Pages上で404になっていた。 | 静的ホスティング判定を追加し、GitHub Pages等では /api を使わず defs/<name> / defs/studio/<name> / defs/json/<name> を静的ファイルとして探索するようにした。Data側も data/<name> / data/json/<name> を探索候補にした。 | GitHub Pages上の記事リンクからData/ViewDefを自動読込し、読者が同じStudio画面を追体験できるようにするため。 |

### v0.9-json-object-studio-branding: FRB Studio / JSON Object Studio 正式表示名・app_info導入
- 作業ID: studio_work_0014
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/config/app_info.json, wwwroot/config/app_settings.json, wwwroot/index.html, wwwroot/styles.css, wwwroot/js/ui/page_setup.js, wwwroot/js/core/state.js, wwwroot/app.js, wwwroot/mdViewer.html, wwwroot/js/markdown/data_markdown.js, wwwroot/defs/*.json

#### 目的

画面上の正式表示名を FRB Studio / JSON Object Studio へ整理し、現在のブランド・プロダクト名・version・revision・taglineを app_info.json で管理できるようにする。

#### 背景

No-Code JSON Studio という旧称から、JSON Object Studio へ名称を寄せる方針が固まった。Studioくんは単なるJSONエディターではなく、思考・制約・差分・レビュー・インシデント・物語をJSON Objectとして扱うStudioになり始めているため、表示名と思想を画面上に明示する必要がある。

#### 対象範囲

app_info.jsonを導入し、brand/product/version/revision/display_version/tagline/statusを保持する。画面ヘッダーは FRB Studio / JSON Object Studio v0.4-r001 / JSONで思考を構造化し、AIとの文脈を育てる。を基本表示にする。version/revisionは主役ではなく、小さく控えめに表示する。app_settings.jsonは将来の動作設定分離先として方針だけ定義する。

#### 対象外

この作業ではリリース履歴、インシデント詳細、全設定値、全画面ViewDefを app_info.json へ混在させない。app_settings.json の詳細項目設計や設定UIまでは必須にしない。

#### 固定名方針

app_info.json の brand/product/version/revision/display_version/tagline はStudio標準の名札情報として扱う。個別Data JSONのフィールド名をRuntimeが決め打ちするものではない。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、起動時にapp_info.jsonを読める範囲で実装する。

#### リスク

旧称がViewDefやData内に残り、正式名称と過去名が混在するリスクがある。app_info.json に設定や履歴を詰め込みすぎると、名札ファイルとしての役割が崩れる。

#### 確認観点

ヘッダーにFRB Studio / JSON Object Studio / v0.4-r001 / taglineが表示されること。version表記が主張しすぎないこと。app_info.jsonが存在しない場合も画面が壊れないこと。旧称が必要以上に表面へ出ないこと。

#### 作業会話サマリ


##### 依頼 / 方針

v0.4-r001の命名・Foundation・ルール管理まわりで見えている追加インシデントを、まとめられるものはまとめて studio_work_incident_data_v0_12_url_param_launch_load.json に追加したい。共通ViewDefのAI Prompt targetFile固定の件も、優先低でよいので漏れないように追加してほしい。

##### AI整理

命名・表示名・app_info導入は1つのFoundation系インシデントとしてまとめる。app_infoはアプリの名札、app_settingsは将来の動作設定として分離し、表示名と思想を画面に出す。

##### 追加コメント

studio_work_incident_data_v0_13_foundation_incidents_added.json の v0.9-json-object-studio-branding 対応として、正式名称への切り替えを依頼。

##### AI追加回答

正式表示名を FRB Studio / JSON Object Studio へ切り替え、config/app_info.json を名札情報として作成。ヘッダーは app_info.json から brand/product/display_version/tagline を読み込むようにし、旧称No-Code JSON Studioの画面表面表示を整理。app_settings.json は将来設定分離用の雛形として追加。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0014_001 | 2026-06-22 | user | 正式名称と表示方針 | FRB Studio / JSON Object Studio として表示し、JSONで思考を構造化し、AIとの文脈を育てるというタグラインを使いたい。 |
| disc_0014_002 | 2026-06-22 | assistant | app_info分離 | app_info.jsonはアプリの名札として、現在の名称・version・revision・taglineだけを持つ。動作設定や履歴は混ぜない。 |
| disc_0014_003 | 2026-06-22 | user | v0.9-json-object-studio-branding作業依頼 | v0.9-json-object-studio-branding として正式名称への切り替えを依頼。 |
| disc_0014_004 | 2026-06-22 | assistant | v0.9-json-object-studio-branding作業結果 | app_info.jsonを作成し、ヘッダー表示・document.title・Markdown Viewer導線・Markdown出力既定名・ViewDef app.nameの表面表示をFRB Studio / JSON Object Studioへ更新。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0014_001 | 2026-06-22 | 正式表示名は FRB Studio / JSON Object Studio とする。 | No-Codeではなく、JSON Objectとして思考・文脈・差分を扱うStudioであることを明確にするため。 |
| dec_0014_002 | 2026-06-22 | app_info.jsonは名札情報に限定する。 | 設定・履歴・インシデントを混ぜると役割が曖昧になり、将来の管理が破綻しやすいため。 |
| dec_0014_003 | 2026-06-22 | app_info.json は wwwroot/config/app_info.json に配置する。 | アプリ名札としてRuntime起動時に静的ファイルとして読み込みやすく、dataやdefsのドメインデータと混ざらないため。 |
| dec_0014_004 | 2026-06-22 | 画面表面上の旧称 No-Code JSON Studio は JSON Object Studio へ切り替える。 | 正式名称をJSON Object Studioに統一し、No-Codeは過去名として扱うため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0014_001 | 2026-06-22 | incident_added | 正式名称・app_info・taglineの導入作業がインシデント管理に存在しなかった。 | studio_work_0014 として、JSON Object Studio正式表示名とapp_info導入を登録。 | Studioくん自身の名前と名札をDataとして管理するため。 |
| chg_0014_002 | 2026-06-22 | branding_runtime_update | ヘッダー・title・一部導線に No-Code JSON Studio / FRB Studio Lab / v0.3-draft が残っていた。 | ヘッダー・title・Markdown Viewer導線を FRB Studio / JSON Object Studio / v0.4-r001 / タグライン表示へ更新。表示値は config/app_info.json から読み込む。 | Studioくん自身の正式名称と思想を画面上の名札として明示するため。 |

### v0.9-versioned-incident-management: Version / Revision / Phase 分離とVersion Detail連携
- 作業ID: studio_work_0015
- 種別: data_model
- 分類: incident_versioning
- 優先度: high
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: studio_work_incident_data_*.json, studio_work_incident_view_def_*.json, release_data.json, release_view_def_*.json, version_detail_data.json if created

#### 目的

Version / Revision / Phase の役割を分離し、IncidentがどのVersionで見つかり、どのVersionで対応され、どのVersion Detailに含まれたかを追跡できるようにする。

#### 背景

phaseに v0.8-url-param-launch-load のような値が入り、Versionと作業テーマが混在している。今後、Studioくんの変更履歴を追うには、製品リリース単位と作業テーマ、インシデント発見・対応状況を分ける必要がある。

#### 対象範囲

Incidentに found_in_version / target_version / fixed_in_version を追加する方針を定義する。Version Detailまたはrelease_data側に、どのwork_item_idを含むかを保持する。phaseは作業テーマとして残し、version/revisionとは混ぜない。

#### 対象外

この作業では既存全インシデントの完全な履歴補正までは必須にしない。まずData構造とViewDef表示方針を決め、以降のインシデントから運用できるようにする。

#### 固定名方針

found_in_version / target_version / fixed_in_version はStudioインシデント管理Dataの標準候補として扱う。ただし他Dataへ無条件に要求するRuntime固定名にはしない。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、ViewDefとData構造の追加で表現する。

#### リスク

既存phase値を一気に修正すると履歴追跡が難しくなる。Version DetailとIncidentの責務を混ぜると、なぜやるのか/何を入れたのかが再び曖昧になる。

#### 確認観点

work_itemにfound_in_version/target_version/fixed_in_versionを追加しても既存画面が壊れないこと。phaseは作業テーマとして残ること。release_data側からwork_item_idを辿れること。

#### 作業会話サマリ


##### 依頼 / 方針

v0.4-r001の命名・Foundation・ルール管理まわりで見えている追加インシデントを、まとめられるものはまとめて studio_work_incident_data_v0_12_url_param_launch_load.json に追加したい。共通ViewDefのAI Prompt targetFile固定の件も、優先低でよいので漏れないように追加してほしい。

##### AI整理

Version/Revision/Phase分離とIncident-Version Detail連携は1つのデータモデル整理としてまとめる。Incidentは理由、Version Detailは含めた変更内容を記録する。

##### 追加コメント

v0.4-r001の命名・Foundation・ルール管理まわりで見えている追加インシデントを、まとめられるものはまとめて studio_work_incident_data_v0_12_url_param_launch_load.json に追加したい。共通ViewDefのAI Prompt targetFile固定の件も、優先低でよいので漏れないように追加してほしい。

##### AI追加回答

Version/Revision/Phase分離、found/target/fixed version、IncidentとVersion DetailのID連携を1件にまとめて追加する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0015_001 | 2026-06-22 | user | VersionとPhaseの違和感 | phaseにv0.8-url-param-launch-loadのような値が入ると、Versionなのか作業テーマなのか分かりにくい。 |
| disc_0015_002 | 2026-06-22 | assistant | データモデル整理 | Version/Revisionは製品リリース、Phaseは作業テーマ、Incidentはなぜやるのか、Version Detailは何を入れたのかとして分離するのがよい。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0015_001 | 2026-06-22 | Phaseは作業テーマとして扱い、Version/Revisionとは分離する。 | 作業テーマとリリース単位を混ぜると、履歴と責任範囲を追いにくくなるため。 |
| dec_0015_002 | 2026-06-22 | Incidentには found_in_version / target_version / fixed_in_version を持たせる。 | 不具合や違和感がどのVersionで見つかり、どのVersionで直ったかを追跡するため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0015_001 | 2026-06-22 | incident_added | Version/Revision/Phase分離とVersion Detail連携が作業項目化されていなかった。 | studio_work_0015 として、Versioned Incident Managementを登録。 | Studioくんの変更履歴とインシデント管理を長期運用できるようにするため。 |

### v0.9-rules-json-source-of-truth: ルール系Data JSON原本化 / Foundation Rules追加
- 作業ID: studio_work_0016
- 種別: data_design
- 分類: rules_data
- 優先度: high
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: wwwroot/data/rules/frb_foundation_rules_data_v0_1.json, wwwroot/data/rules/frb_viewdef_generation_rules_data_v0_1.json, wwwroot/defs/rules/rule_review_common_view_def_v0_1.json, wwwroot/exports/rules/*.md

#### 目的

Markdownをルール原本にせず、ルール・制約・レビュー対象はドメイン別Data JSONを原本として管理し、共通ViewDefでレビューできるようにする。

#### 背景

frb_coding_constraints_data_v0_3.json が実は憲法レビューの原本であり、Markdown Exportは原本ではなく表示用Viewだったことを確認した。今後はFRB Studio FoundationやViewDef生成ルールも、MarkdownではなくData JSONを原本として扱う必要がある。

#### 対象範囲

frb_foundation_rules_data_v0_1.json を追加し、Studio運用原則をrules配列として管理する。frb_viewdef_generation_rules_data_v0_1.json と同じ rule_review_data_v0_1 構造に寄せる。data/rules・defs/rules・exports/rules の配置方針を使う。MarkdownはData JSONからのExport Viewとして扱う。

#### 対象外

この作業ではすべての既存Markdownを即Data JSONへ変換しない。まずFoundation RulesとViewDef生成Rulesを代表例として整える。

#### 固定名方針

rules配列はルールレビュー共通構造の契約として扱う。個別ドメインの意味はdomainとrule_idで分け、Runtimeが特定ドメイン名に依存しないようにする。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、Data/ViewDef/Markdown Exportの役割分離を徹底する。

#### リスク

Markdownを原本として編集し続けると、承認状態・変更履歴・レビュー会話が分散する。逆にData JSON化しすぎると人間の初期確認が重くなるため、Markdown下書き→Data JSON原本化の流れを明確にする必要がある。

#### 確認観点

frb_foundation_rules_data_v0_1.json が rule_review_common_view_def_v0_1.json で読み込めること。rules配列17件が表示されること。Markdown Exportは原本ではなく表示用であることが分かること。data/rules配下でURL起動できること。

#### 作業会話サマリ


##### 依頼 / 方針

v0.4-r001の命名・Foundation・ルール管理まわりで見えている追加インシデントを、まとめられるものはまとめて studio_work_incident_data_v0_12_url_param_launch_load.json に追加したい。共通ViewDefのAI Prompt targetFile固定の件も、優先低でよいので漏れないように追加してほしい。

##### AI整理

Markdown原本化を避ける方針、Foundation Rules JSON追加、rulesフォルダー配置、ドメイン別Data JSON＋共通ViewDefを1つの作業項目にまとめる。

##### 追加コメント

v0.4-r001の命名・Foundation・ルール管理まわりで見えている追加インシデントを、まとめられるものはまとめて studio_work_incident_data_v0_12_url_param_launch_load.json に追加したい。共通ViewDefのAI Prompt targetFile固定の件も、優先低でよいので漏れないように追加してほしい。

##### AI追加回答

Foundation RulesをData JSON原本として追加し、MarkdownはExport Viewとして扱うインシデントを登録する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0016_001 | 2026-06-22 | user | Markdown原本化への違和感 | Markdownを原本にするとまた分からなくなりそう。frb_coding_constraints_data_v0_3.json が原本で、MarkdownはExportだった。 |
| disc_0016_002 | 2026-06-22 | assistant | Data JSON原本方針 | Data JSONはドメインで分ける。ViewDefは構造で共有する。MarkdownはJSONから生成されるViewとする。 |
| disc_0016_003 | 2026-06-22 | assistant | Foundation Rules生成 | frb_foundation_rules_data_v0_1.json を、rule_review_common_view_def_v0_1.json 前提で生成する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0016_001 | 2026-06-22 | 構造化できるルールはData JSONを原本とする。 | 承認状態・レビュー会話・変更履歴・差分管理を保持するにはMarkdownよりData JSONが適しているため。 |
| dec_0016_002 | 2026-06-22 | ルール系Dataはドメイン別に分け、ViewDefはrules構造で共通化する。 | ドメインごとの責任範囲を分けながら、レビュー体験を共通化するため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0016_001 | 2026-06-22 | incident_added | Foundation Rules JSON化とMarkdown非原本化が作業項目化されていなかった。 | studio_work_0016 として、ルール系Data JSON原本化 / Foundation Rules追加を登録。 | Studioくん自身の原則をData JSON原本として管理するため。 |

### v0.9-rule-review-common-viewdef-polish: 共通Rule Review ViewDefの汎用化仕上げ
- 作業ID: studio_work_0017
- 種別: improvement
- 分類: viewdef_polish
- 優先度: low
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: wwwroot/defs/rules/rule_review_common_view_def_v0_1.json, related rule review data json, markdown export templates

#### 目的

rule_review_common_view_def_v0_1.json を特定データ専用の匂いから切り離し、複数ドメインのルールレビューで安全に使える共通ViewDefへ整える。

#### 背景

共通ViewDefとして使い始めたが、AI Prompt targetFile が frb_viewdef_generation_rules_data_v0_1.json 固定になっている。また、承認印など憲法レビュー由来のトーン、Foundation系カテゴリ未対応、Markdown Exportでsummary/body等が重複しやすい問題が見えている。

#### 対象範囲

markdown.aiPrompt.targetFile固定をなくす、または現在Data名から動的に扱う方針を検討する。カテゴリ選択肢にFoundation系を含めるか、select固定ではなくtext/柔軟候補にする。approval_stampなど共通ViewDefに不要な専用項目を非表示または削除する。Markdown Exportでsource_heading/summary/bodyを出しすぎる問題を整理し、レビュー記録用と元Rules風出力の分離を検討する。

#### 対象外

この作業は優先低。現時点でStudio読込やレビューができる場合、v0.9高優先タスクを止めてまで実施しない。大規模なMarkdown Exportエンジン刷新は別作業に分ける。

#### 固定名方針

共通ViewDef内に特定Data JSONファイル名を固定しない。targetFile等が必要な場合も、現在読込中Data名・ViewDef設定・ActionContextから取得できる設計に寄せる。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、ViewDef定義とMarkdown出力設定の調整で対応する。

#### リスク

共通ViewDefに特定ドメインの匂いが残ると、Foundation Rulesや他ドメインRulesで誤ったファイル名・カテゴリ・表示トーンが混入する。逆に柔軟にしすぎると入力補助が弱くなる。

#### 確認観点

frb_viewdef_generation_rules_data と frb_foundation_rules_data の両方で同じViewDefを使えること。AI PromptのtargetFileが誤った固定名にならないこと。Markdown Exportで同じ説明が過剰に重複しないこと。承認印など不要項目が共通画面で目立たないこと。

#### 作業会話サマリ


##### 依頼 / 方針

v0.4-r001の命名・Foundation・ルール管理まわりで見えている追加インシデントを、まとめられるものはまとめて studio_work_incident_data_v0_12_url_param_launch_load.json に追加したい。共通ViewDefのAI Prompt targetFile固定の件も、優先低でよいので漏れないように追加してほしい。

##### AI整理

共通ViewDefのAI Prompt targetFile固定は優先低だが、共通ViewDefとしては危険なので漏れないように専用インシデントとして登録する。関連する汎用化仕上げも同じ低優先タスクにまとめる。

##### 追加コメント

v0.4-r001の命名・Foundation・ルール管理まわりで見えている追加インシデントを、まとめられるものはまとめて studio_work_incident_data_v0_12_url_param_launch_load.json に追加したい。共通ViewDefのAI Prompt targetFile固定の件も、優先低でよいので漏れないように追加してほしい。

##### AI追加回答

targetFile固定、カテゴリ候補、承認印、Markdown Export重複などを低優先の共通ViewDef汎用化仕上げとして追加する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0017_001 | 2026-06-22 | assistant | targetFile固定の発見 | 共通ViewDefのAI Prompt targetFile が frb_viewdef_generation_rules_data_v0_1.json 固定っぽい。共通の顔をして、心に元カノの名前を刻んでいる状態。 |
| disc_0017_002 | 2026-06-22 | user | 優先度指定 | 共通ViewDefのAI Prompt targetFileの件も、優先低でいいのでもれないように追加してほしい。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0017_001 | 2026-06-22 | AI Prompt targetFile固定の件は優先低で作業項目化する。 | 今すぐ致命的ではないが、共通ViewDefとして複数Dataに使う場合に誤ったファイル名をAI Promptへ出すリスクがあるため。 |
| dec_0017_002 | 2026-06-22 | 共通ViewDefは憲法専用トーンを落とし、汎用ルールレビューとして整える。 | Foundation Rules、ViewDef Rules、Coding Constraintsなど複数ドメインで共有するため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0017_001 | 2026-06-22 | incident_added | 共通ViewDefのtargetFile固定や汎用化仕上げが作業項目として登録されていなかった。 | studio_work_0017 として、低優先の共通Rule Review ViewDef汎用化仕上げを登録。 | 優先は低いが、共通ViewDefの将来事故を防ぐため。 |

### v0.9-json-utf8-human-readable-save: Data JSONの日本語可読保存
- 作業ID: studio_work_0018
- 種別: bugfix_improvement
- 分類: encoding
- 優先度: high
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: JSON generation scripts, Program.cs save API, wwwroot/js/core/file_api.js, any export/save utilities

#### 目的

Data JSONを人間が直接読めるUTF-8日本語で保存し、\uXXXX だらけの人間拒否モードを避ける。

#### 背景

frb_viewdef_generation_rules_data_v0_1.json の日本語が Unicode escape で表示され、人間が直接読むにはつらい状態になった。JSONとしては正しいが、Studioくんの原本思想ではData JSONも人間が読める必要がある。

#### 対象範囲

Python生成時はensure_ascii=false相当で保存する。.NETのSystem.Text.Json保存時は日本語を過剰にescapeしない設定を検討する。Studioくんの保存APIやExport処理でも、UTF-8で日本語がそのまま読めることを基本にする。

#### 対象外

この作業では既存の全JSONを一括変換しない。必要な代表Dataから順次UTF-8可読版へ置き換える。ファイル名文字化け問題はstudio_work_0008側の範囲とし、ここではJSON本文の可読性を扱う。

#### 固定名方針

エンコーディング設定はData構造ではなく保存処理の契約として扱う。特定Dataフィールド名をRuntimeが参照する作業ではない。

#### module化方針

type="module" 化は今回の主目的ではない。保存処理・生成スクリプト・API設定を中心に確認する。

#### リスク

JSONとしては正常でも、人間が読めない状態が再発すると、Data JSON原本化の思想と矛盾する。過剰なUnsafeRelaxed設定はHTML/URL系エスケープとの境界に注意が必要。

#### 確認観点

日本語title/summary/bodyが\uXXXXではなく日本語のまま保存されること。Studioで読み込んでも値が壊れないこと。保存→再読込→Git diffで可読性が保たれること。既存の文字化けファイル名対策と混同しないこと。

#### 作業会話サマリ


##### 依頼 / 方針

v0.4-r001の命名・Foundation・ルール管理まわりで見えている追加インシデントを、まとめられるものはまとめて studio_work_incident_data_v0_12_url_param_launch_load.json に追加したい。共通ViewDefのAI Prompt targetFile固定の件も、優先低でよいので漏れないように追加してほしい。

##### AI整理

日本語JSONの可読保存は、Data JSONを原本にするなら重要度が高い。ファイル名文字化けとは別に、JSON本文のUTF-8可読性インシデントとして追加する。

##### 追加コメント

v0.4-r001の命名・Foundation・ルール管理まわりで見えている追加インシデントを、まとめられるものはまとめて studio_work_incident_data_v0_12_url_param_launch_load.json に追加したい。共通ViewDefのAI Prompt targetFile固定の件も、優先低でよいので漏れないように追加してほしい。

##### AI追加回答

日本語JSONを\uXXXXではなくUTF-8可読形式で保存する作業を追加する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0018_001 | 2026-06-22 | user | Unicode escape表示の違和感 | この人間は日本語よめません状態ってどうにかなるよね？？？笑 |
| disc_0018_002 | 2026-06-22 | assistant | 原因整理 | 文字化けではなくUnicodeエスケープ保存。JSONとしては正しいが人間可読性が死んでいる。Pythonならensure_ascii=False、.NETなら日本語を過剰escapeしない設定で直せる。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0018_001 | 2026-06-22 | Data JSON本文はUTF-8で日本語が読める形式を基本とする。 | Data JSONは原本であり、人間も直接読む対象であるため。 |
| dec_0018_002 | 2026-06-22 | JSON本文のUnicode escape問題は、Markdown出力ファイル名の文字化け問題とは別インシデントで扱う。 | 本文保存の可読性とファイル名sanitizeは原因も対策箇所も異なるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0018_001 | 2026-06-22 | incident_added | JSON本文の日本語可読保存が作業項目として登録されていなかった。 | studio_work_0018 として、Data JSONの日本語可読保存を登録。 | Data JSON原本化の思想を守るため。 |

### v0.10-markdown-preview-display-mode: 表示モードのMarkdownプレビュー対応
- 作業ID: studio_work_0019
- 種別: feature
- 分類: markdown
- 優先度: medium
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/js/renderers/field_controls.js, wwwroot/styles.css, wwwroot/defs/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json, representative ViewDefs such as rule_review_common_view_def_v0_2_editable_review_target.json

#### 目的

textarea / chat / detailBodyカードなど、Markdown記法を許可した文言欄について、表示モードではMarkdownプレビューとして表示し、編集時はMarkdown原文を編集できるようにする。

#### 背景

rule_review_common_view_def でレビュー対象の本文を編集可能にし、Markdownリンク/画像記法を入れられるようになった。一方、表示モードではMarkdown原文がそのまま見えるため、仕様書本文・ルール本文・チャット欄・作業メモなどの読み物としての体験が弱い。チャット欄ではMarkdown表示の仕組みが一部入っているため、同じ考え方を共通の文言欄へ広げたい。

#### 対象範囲

ViewDefで markdown.enabled / inline / allowLinks / allowImages が指定された textarea/chat/message/detailBodyカードを対象に、表示モードではMarkdownをHTMLへ変換してプレビュー表示する。編集モードではMarkdown原文を保持し、必要に応じて入力中プレビューを表示する。保存値は必ずMarkdown原文のままとし、HTMLをData JSONへ混入させない。既存のchat送信欄、末尾表示、Markdown preview二重表示対策との整合を取る。

#### 対象外

この作業では外部Markdownエディタ化、WYSIWYG本格編集、全フィールド自動Markdown化、任意HTML許可、外部URL画像の高度なセキュリティ制御までは行わない。まずViewDefで許可された文言欄の表示モードMarkdownプレビューに限定する。

#### 固定名方針

Runtimeが body / summary / user_comment など特定Dataフィールド名を決め打ちしてMarkdown化しない。Markdown表示可否はViewDefのfield/message定義上の markdown 設定に従う。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、Markdown描画処理を共通関数化して既存renderingへ安全に差し込む。

#### リスク

Markdown変換とcontenteditable保存が混ざると、HTMLがJSONへ保存されるリスクがある。既存chatのpreview二重表示問題が再発するリスクがある。全フィールドを自動Markdown化すると意図しないリンク化・画像表示が起きるため、ViewDef明示設定に限定する必要がある。

#### 確認観点

rule_review_common_view_def の body に Markdownリンクと画像を入れ、表示モードではプレビュー表示、編集時は原文編集、保存後もMarkdown原文がData JSONに残ること。chat欄の保存済みコメントで二重表示が再発しないこと。allowImages=false の欄では画像表示されないこと。通常textareaで markdown 未指定の欄は従来表示のまま壊れないこと。F12反映→上書き保存→再読込でHTML混入がないこと。

#### 作業会話サマリ


##### 依頼 / 方針

今の仕様書の文言欄とかチャット欄とか共通なんやけど、表示モードの時は、Markdownプレビューモードに対応してもらうことはできそう？できそうなら、添付インシデントに追加をお願いしたい。

##### AI整理

対応可能。すでにchat欄でMarkdownリンク/画像表示とpreview二重表示対策の考え方があるため、ViewDefのmarkdown設定を契約として、表示モードではMarkdownプレビュー、編集時は原文編集に分けるインシデントとして追加する。

##### 追加コメント

Markdown原文を編集した後、前へ/次へで別データへ移動しないとプレビューへ戻らない。カーソルがカレントテキストボックスを外れた時にプレビュー表示へ戻してほしい。

##### AI追加回答

v0.10.2として、Markdown原文編集モードのcontenteditableがblurしたタイミングで、Markdown原文を行データへ反映し、その場でMarkdownプレビュー表示へ戻す処理を追加した。保存値はMarkdown原文のままとし、HTMLはData JSONへ混入させない。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0019_001 | 2026-06-22 | user | 表示モードMarkdownプレビュー相談 | 今の仕様書の文言欄とかチャット欄とか共通なんやけど、表示モードの時は、Markdownプレビューモードに対応してもらうことはできそう？できそうなら、添付インシデントに追加をお願いしたい。 |
| disc_0019_002 | 2026-06-22 | assistant | 作業項目化方針 | 対応可能。ViewDefでMarkdownを許可したtextarea/chat/detailBodyカードについて、表示モードはMarkdownプレビュー、編集時はMarkdown原文編集に分ける作業として登録する。 |
| disc_0019_003 | 2026-06-22 | user | v0.10-markdown-preview-display-mode作業依頼 | studio_work_incident_data_v0_16_markdown_preview_display_mode_added.json v0.10-markdown-preview-display-mode の対応を依頼。仕様書欄やチャット欄の表示モードMarkdownプレビューはモチベーションが上がるため優先したい。 |
| disc_0019_004 | 2026-06-22 | assistant | v0.10-markdown-preview-display-mode作業結果 | field_controls.jsにMarkdown表示モードを追加。Markdown許可済みchat messageとtextareaは、表示時にMarkdown変換済みHTMLを1回だけ表示し、クリック後にMarkdown原文編集へ切り替える。styles.cssに表示/編集中の見た目を追加し、index.htmlのcache busterを更新した。 |
| disc_0019_003 | 2026-06-22 | user | v0.10確認結果 | 01_main/studio_work_incident_data_v0_17_markdown_preview_display_mode_done.json で確認しているけど、Markdownプレビュー表示が変わらない。 |
| disc_0019_004 | 2026-06-22 | assistant | v0.10.1修正方針 | v0.10はリンク/画像のインラインMarkdown変換中心で、#見出しや箇条書きを処理していなかった。Markdownブロックレンダリングを追加し、ViewDef側にもmarkdown設定を追加する。 |
| disc_0019_005 | 2026-06-22 | user | Markdown編集後プレビュー復帰相談 | Markdownを編集した後、プレビュー状態にするには前へ/次へで別データを表示させて戻る必要がある。理想はカーソルがカレントテキストボックスを外れた時にプレビュー表示になってほしい。 |
| disc_0019_006 | 2026-06-22 | assistant | v0.10.2 Markdown blur preview fix | Markdown原文編集欄のblur時に、raw値を行データへ同期し、同じ欄をMarkdownプレビューへ戻す処理を追加。F12や上書き保存時もMarkdown原文が保存される。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0019_001 | 2026-06-22 | Markdownプレビューは表示モードに限定し、保存値はMarkdown原文のまま保持する。 | HTMLをData JSONへ混入させると、原本としてのJSONが壊れ、Git diffやAI貼り付け時の再利用性も下がるため。 |
| dec_0019_002 | 2026-06-22 | Markdown化する対象はViewDefのmarkdown設定で明示された欄に限定する。 | 全textareaを自動Markdown化すると、意図しないリンク化・画像表示・表示崩れが起きるため。 |
| dec_0019_003 | 2026-06-22 | chat欄の既存Markdown表示/preview二重表示対策と同じ思想で、文言欄の表示モードにも展開する。 | 仕様書本文、ルール本文、レビューコメント、作業メモを共通の読み物体験として扱うため。 |
| dec_0019_004 | 2026-06-22 | 通常表示ではMarkdownプレビュー、クリック後にMarkdown原文編集へ切り替える方式を採用する。 | 常時textarea原文表示だと読み物としての気持ちよさが弱く、常時HTML編集だとData JSONへHTMLが混入するリスクがあるため。 |
| dec_0019_004 | 2026-06-22 | Markdownプレビューはリンク/画像だけでなく、見出し・箇条書き・コードブロックも表示対象とする。 | 仕様書本文やルール本文を読み物として扱うには、#見出しや箇条書きがそのまま見えるだけではモチベーションが上がる表示体験にならないため。 |
| dec_0019_004 | 2026-06-22 | Markdown原文編集欄はblur時にプレビューへ戻す。 | 前へ/次へで再描画しないとプレビューへ戻れない操作は、読み物として育てるStudio体験に合わないため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0019_001 | 2026-06-22 | incident_added | 表示モードでtextarea/chat/detailBodyカードをMarkdownプレビュー表示する作業項目が存在しなかった。 | studio_work_0019 として、表示モードのMarkdownプレビュー対応を登録。 | JSON原本の本文をMarkdown記法で育てつつ、表示時は読み物として自然に確認できるようにするため。 |
| chg_0019_002 | 2026-06-22 | markdown_preview_display_mode_runtime_update | Markdown許可されたchat/detailBody/textareaでも、編集可能欄はMarkdown原文がそのまま表示されることが多く、仕様書本文やルール本文を読み物として確認しづらかった。 | Markdown許可されたchat messageとdetail textareaは、通常表示でMarkdownプレビューを表示し、クリック後にMarkdown原文編集へ切り替わる。保存値はMarkdown原文のまま保持する。 | JSON原本をMarkdown記法で育てつつ、表示時は読み物として自然に確認できるようにするため。 |
| chg_0019_002 | 2026-06-22 | markdown_block_preview_fix | Markdown表示は主にリンク/画像のインライン変換で、#見出し・箇条書き・引用・コードブロックはプレーンテキストのまま表示されていた。 | renderMarkdownContentを追加し、表示モードで見出し・箇条書き・引用・コードブロックをHTMLプレビュー表示する。編集時はMarkdown原文へ戻す。 | 表示モードMarkdownプレビューを、仕様書・ルール本文として読める体験にするため。 |
| chg_0019_003 | 2026-06-22 | markdown_blur_preview_fix | Markdown原文編集後、同じ欄をプレビュー表示へ戻すには詳細再描画が必要だった。 | contenteditableのblur時にMarkdown原文を行データへ同期し、その場でMarkdownプレビュー表示へ戻す。 | Markdown本文を編集しながら、すぐ読み物表示で確認できるようにするため。 |

### v0.11-mdviewer-blur-preview-mode: Markdown Viewer / Editor のblur時プレビュー自動復帰
- 作業ID: studio_work_0020
- 種別: feature
- 分類: markdown
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/mdViewer.html, wwwroot/js/runtime/MDVIEWER_BLUR_PREVIEW_MODE_NOTES_v0_11.md

#### 目的

Markdown Viewer / Editor で本文textareaを編集した後、前へ/次へや手動Viewer切替を行わなくても、カーソルが本文エディターから外れた時点で自動的にViewer表示へ戻るようにする。

#### 背景

JSON Object Studio側のMarkdown編集カードでは、編集後にフォーカスが外れるとプレビュー表示へ戻る操作感が非常に気持ちよかった。同じ体験をMarkdown Viewer / Editorへ適用できれば、Markdown記事編集も「書く → 離す → 記事として読む」の往復になり、モチベーションが大きく上がる。

#### 対象範囲

Editorモードの本文textareaにblurハンドリングを追加する。フォーカスがeditor内の補助ボタンやslash menuへ移った場合は自動Viewer復帰しない。本文エリア外へ出た場合はMarkdownを再描画し、Viewerモードへ戻す。Preview側のスクロール位置は、カーソル位置直前の見出しを優先し、見出しが取れない場合はeditor.scrollTop比率で復元する。

#### 対象外

完全な行単位アンカー同期、分割ビューのライブカーソル追従、編集中部分だけの差分プレビュー、Markdown ASTによる厳密な位置対応は今回の対象外。まずは体験価値を優先し、近い位置へ戻る実用的な復元に留める。

#### 固定名方針

特定Markdownファイル名やDataフィールド名には依存しない。mdViewer.html内のEditor/Preview DOMに対するUI動作として実装し、Markdown原文とHTMLプレビューの責務を分離する。

#### module化方針

既存のmdViewer.html単体script構成を維持する。type="module"化や大規模分割は行わない。

#### リスク

textareaのblurは、保存ボタン・挿入ボタン・slash menu操作でも発生するため、補助UIクリック時に意図せずViewerへ戻るリスクがある。またMarkdown原文とPreview HTMLは高さが一致しないため、スクロール位置の完全一致は保証しない。

#### 確認観点

Editorモードで本文を編集し、本文エリア外をクリックするとViewerモードへ戻ること。編集内容がPreviewへ反映されること。editor内のCode/Table/保存/ファイル名など補助UIへ移動した場合は勝手にViewerへ戻らないこと。カーソル近くの見出し、またはスクロール比率によりViewer側が近い位置へ戻ること。保存値はMarkdown原文のままでHTMLが混入しないこと。

#### 作業会話サマリ


##### 依頼 / 方針

Markdown Viewer / Editorにも、Studio側のMarkdown編集欄と同じ入力方式を適用したい。Editorで編集したあと、フォーカスが外れた時にPreview表示へ戻るようにしたい。Preview表示時のスクロール位置が重要なので、チャレンジ対応してほしい。

##### AI整理

対応方針として、Editor本文textareaのblur時にViewerモードへ自動復帰する処理を追加する。復帰時はMarkdownを再レンダリングし、カーソル位置直前の見出しへスクロールする。見出しが取れない場合はeditor.scrollTop比率をPreview側へ反映する。

##### 追加コメント

これはやばいことになってきましたよぉ～。インシデントに追加した上で、チャレンジ対応をお願いします。最新資材投入します。よろしく！！やばいよやばいよぉ～笑

##### AI追加回答

Markdown Viewer / Editor の本文textarea blur時Viewer自動復帰に対応。editor内補助UIへの移動は除外し、本文外へフォーカスが出た時だけViewerへ戻す。スクロール復元はカーソル直前見出し優先、なければスクロール比率方式で実装した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0020_001 | 2026-06-22 | user | Markdown Viewerへの操作感適用相談 | Studio側のMarkdown編集欄と同じように、Markdown Viewer / Editorでもフォーカスが外れた時にプレビュー表示へ戻せるか相談。スクロール位置がポイントになると指摘。 |
| disc_0020_002 | 2026-06-22 | assistant | 対応方針 | まずはscroll ratio方式で可能。さらに気持ちよくするならカーソル位置直前の見出しアンカーへ戻す方式が良いと整理。 |
| disc_0020_003 | 2026-06-22 | user | チャレンジ対応依頼 | インシデントに追加した上で、最新資材を投入してチャレンジ対応を依頼。 |
| disc_0020_004 | 2026-06-22 | assistant | 作業結果 | mdViewer.htmlへEditor blur preview modeを追加。本文textareaからフォーカスが外れたらViewerへ戻し、見出しまたはスクロール比率でPreview位置を復元する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0020_001 | 2026-06-22 | Editor補助UIへのフォーカス移動では自動Viewer復帰しない。 | Code/Table/保存/ファイル名入力/slash menuなどの操作中にEditorが消えると作業が壊れるため。 |
| dec_0020_002 | 2026-06-22 | スクロール復元は見出しアンカー優先、比率復元をフォールバックとする。 | Markdown原文とHTMLプレビューでは高さが一致しないため、単純なscrollTop比率だけではズレる。カーソル直前の見出しが取れれば体感位置が自然になるため。 |
| dec_0020_003 | 2026-06-22 | 保存値はMarkdown原文のまま保持し、Viewer表示はHTMLプレビューに限定する。 | Markdown Viewer / Editorでも、JSON Object Studio側と同じく原文と表示を分離し、HTMLを保存値へ混入させないため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0020_001 | 2026-06-22 | mdviewer_blur_preview_mode | EditorでMarkdown本文を編集した後、Viewer表示へ戻るにはViewerボタンを押すか、別操作で再描画・再表示する必要があった。 | 本文textareaからフォーカスが外れた時、自動でMarkdownを再レンダリングしViewerモードへ戻る。スクロール位置は見出しアンカーまたはeditor scroll比率で復元する。 | 書く→離す→記事として読む、の操作感をMarkdown Viewer / Editorにも適用し、記事編集のモチベーションを上げるため。 |

### v0.11.1-mdviewer-single-pane-blur-preview: ★Markdown Viewer / Editor の単一欄blurプレビュー再チャレンジ
- 作業ID: studio_work_0021
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/mdViewer.html

#### 目的

Editorモードで入力欄とプレビュー欄を2つ並べず、1つの欄で、テキストボックスにフォーカスがある時だけMarkdown原文入力モード、フォーカスが外れたらMarkdownプレビューモードへ戻る操作感にする。

#### 背景

v0.11-mdviewer-blur-preview-mode の1回目対応では、Editorモード中に入力欄とプレビュー欄の2ペイン構成が残り、JSON Object Studio側で得られた『書く→離す→読める』操作感と一致しなかった。Markdown Viewer / Editorでも、1つの欄が入力面とプレビュー面を切り替える体験へ寄せる必要がある。

#### 対象範囲

mdViewer.htmlのEditorモードを単一ペイン構成へ変更する。Editorモードではarticle previewとの2カラムをやめ、編集カード内の1つの領域でtextareaとMarkdownプレビューを切り替える。textarea blur時にMarkdownプレビューへ戻し、プレビューをクリックしたら同じ欄で入力モードへ戻る。スクロール位置は見出しまたはスクロール比率で可能な範囲で復元する。

#### 対象外

wwwroot/data配下、wwwroot/defs配下のファイル追加・更新は行わない。GitHub専用公開エリアのためAI更新禁止とする。Markdown本文の保存仕様、API仕様、管理Markdown一覧仕様の大規模変更は行わない。

#### 固定名方針

特定Markdownファイル名や特定データ名へ依存しない。EditorモードのDOM制御はmdViewer.html内の汎用UI要素に限定する。

#### module化方針

type="module" 化は行わず、既存の単一HTML内script方式を維持する。

#### リスク

textareaとプレビューを同一欄で切り替えるため、blurタイミング、Code/Tableボタン、slash menu、保存ボタン、ファイル名入力欄とのフォーカス競合が起きる可能性がある。スクロール復元はMarkdown原文とHTMLプレビューで高さが異なるため完全一致しない可能性がある。

#### 確認観点

Editorボタン押下で入力モードになること。本文textareaからフォーカスが外れると同じ欄がMarkdownプレビューになること。プレビューをクリックすると同じ欄が入力モードへ戻ること。Code/Tableボタンで意図せずプレビューモードへ落ちないこと。Viewerボタンで通常Viewer表示へ戻ること。保存値にHTMLが混入しないこと。wwwroot/dataおよびwwwroot/defs配下が更新されていないこと。

#### 作業会話サマリ


##### 依頼 / 方針

対応1回目後コメントとして、Editorモードの時は入力欄とプレビュー欄を2つ持つのではなく、1つの欄でテキストボックスのフォーカスがある時は入力モード、フォーカスが外れたらプレビューモードにするチャレンジを依頼。補足として、wwwroot\data と wwwroot\defs はGitHub専用公開エリアのためAIによるファイル追加更新を禁止、不要だったwwwroot\wwwrootフォルダーは削除済みとの共有あり。

##### AI整理

Editorモードを単一欄方式へ変更。Editorモードではarticle-card側を非表示にし、編集カード内の同じ領域でtextareaとMarkdownプレビューを切り替える。blur時はMarkdownプレビューへ戻し、プレビュークリックでtextarea入力へ戻る。スクロール復元は見出し優先、取れない場合はスクロール比率で復元する。wwwroot/dataおよびwwwroot/defs配下は変更しない。

##### 追加コメント

Editorモードの時は、入力欄とプレビュー欄を２つもつのではなく、１つの欄でテキストボックスのフォーカスがある時は入力モード。フォーカスが外れたらプレビューモードにするチャレンジをお願いします。wwwroot/data・wwwroot/defs はGitHub専用公開エリアのためAI更新禁止。

# ２回目チャレンジ後コメント

おおおーーーかなりいけている笑　まずは相談。

エディターモードの時に、左端の目次とメタは出したままにしておいてほしい。

エディターモードの時の欄の横幅は、プレビューモードの時の文章欄と同じ幅・位置になるように調整お願いしたい。

エディターモードの時のプレビューでクリックした行を記憶しておいて、エディターモードに切り替わった時に、その行にカーソルがいけば完璧！！できるだろうか？

プレビューモードの時は、現状でOKで、テキスト欄（文章欄）をクリックしてもエディターモードに切り替わらなければOK

##### AI追加回答

単一欄blurプレビュー方式で再実装。mdViewer.htmlのみを変更し、wwwroot/data・wwwroot/defsは未変更。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0021_001 | 2026-06-22 | user | 対応1回目後コメント | Editorモードの時は、入力欄とプレビュー欄を２つもつのではなく、１つの欄でテキストボックスのフォーカスがある時は入力モード。フォーカスが外れたらプレビューモードにするチャレンジをお願いします。 |
| disc_0021_002 | 2026-06-22 | user | 公開エリア更新禁止 | wwwroot\data と wwwroot\def はGitHub専用公開エリアの為、AIによるファイル追加更新を禁止。wwwroot\wwwroot は不要なフォルダーとして削除済み。 |
| disc_0021_003 | 2026-06-22 | assistant | 再チャレンジ対応結果 | mdViewer.htmlを単一欄方式へ変更。EditorモードではtextareaとMarkdownプレビューを同じ欄で切り替える。blurでプレビュー、プレビュークリックで入力に戻る。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0021_001 | 2026-06-22 | Editorモードでは入力欄とプレビュー欄を2カラムで並べない。 | 書く場所と読む場所が分かれると、JSON Object Studio側で得られた『書く→離す→読める』操作感にならないため。 |
| dec_0021_002 | 2026-06-22 | wwwroot/dataおよびwwwroot/defs配下はAI更新禁止エリアとして扱う。 | GitHub専用公開エリアであり、AIによる不用意なファイル追加・更新を避けるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0021_001 | 2026-06-22 | mdviewer_single_pane_blur_preview | Editorモードで入力欄とプレビュー欄が2つの領域として存在し、blur後の体験が分離していた。 | Editorモードで1つの欄が、focus時はtextarea、blur時はMarkdownプレビューとして切り替わる。 | Markdown Viewer / Editorでも『書く→離す→記事として読む』体験を成立させるため。 |

### v0.12-rules-update-reporting-policy: AI作業対象ファイル記録 / インシデント回答記録ルール整備
- 作業ID: studio_work_0022
- 種別: rules_review
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: 優先度A: data/json/00_rules/frb_coding_constraints_review_data_v0_3.json, data/json/00_rules/frb_studio_foundation_review_data_v0_1.json, data/json/00_rules/_json_creation_prompt.md。前回誤反映の取り下げ: data/json/00_rules/frb_viewdef_generation_rules_review_data_v0_1.json, data/json/00_rules/frb_view_def_schema_review_data_v0_1.json。作業結果収録: data/json/01_main/studio_work_incident_data_v0_25_rules_update_reporting_policy_redone.json。

#### 目的

AI作業時のファイル更新ルールを整理し、root data/defs を過剰に保護しすぎないこと、AIが更新したファイルをインシデントJSONへ記録すること、インシデント対応後の報告内容をAI回答欄へ残すことをルール化する。

#### 背景

ルール系ブラッシュアップ候補メモで「ZIP内に root data/ / defs/ が存在する場合も、同様に原則変更しない」と整理したが、この表現は強すぎる。root data/defs はAI作業で更新が必要になることがあるため、禁止ではなく、更新対象と更新結果をインシデントJSONに記録する運用へ寄せる必要がある。

#### 対象範囲

root data/defs は、作業目的に必要な場合はAIが更新してよい。ただし、更新したファイル名、変更理由、変更概要を該当インシデントの change_history / latest_ai_response / discussion_history へ記録する。インシデント対応後のAI完了報告は、会話上だけでなく、インシデントJSONの ai_response または latest_ai_response にも反映する。今後予定するルール変更では、どのルールファイルに対する変更かを target_files または target_rule_files として明記する。

#### 対象外

このインシデント追加時点では、ルール本文そのものの細部修正までは行わない。まずは作業項目として登録し、細かい文言や対象ルールファイルはユーザーコメントで確認しながら詰める。wwwroot/data と wwwroot/defs に関する既存の公開用領域ルールそのものを今回ここで再定義しない。

#### 固定名方針

変更ファイル記録やAI回答記録のために、必要な管理フィールドはインシデント管理JSONの標準運用として扱う。ただし、Runtime側が特定データ専用の固定フィールド名に依存する実装は行わない。

#### module化方針

type="module" 化は今回の目的ではない。ルール文書とインシデント運用の整理を対象とする。

#### リスク

root data/defs の更新を許容すると、AIが不要なデータ更新まで行うリスクがある。そのため、許可ではなく「必要時のみ更新可」「更新ファイルを必ず記録」「理由と結果をインシデントに残す」という制約で管理する。

#### 確認観点

インシデントJSONに今回の論点が作業項目として追加されていること。target_files / target_rule_files に予定変更対象のルールファイルが明記されていること。root data/defs の一律変更禁止が入っていないこと。更新ファイル一覧とAI完了報告をインシデントJSONに残す方針が入っていること。

#### 作業会話サマリ


##### 依頼 / 方針

ルール系ブラッシュアップ候補をインシデントとして追加したい。特に、root data/defs まで原則変更しないという表現は強すぎるため削除したい。def/dataフォルダーはAI側でも更新してよく、どのファイルを更新したかをインシデントJSONへ記録してほしい。インシデント対応後のAI報告内容も、インシデントJSONのAI回答欄へ記録するルールにしたい。今回予定する変更内容がどのルールファイルに対する変更かも明記したい。

##### AI整理

v0.12-rules-update-reporting-policy 対応完了。root data/defs は一律変更禁止ではなく、必要時更新可＋インシデントJSONへの更新ファイル記録をルール化。AI完了報告は ai_response / latest_ai_response / discussion_history に残す方針を追加。各ルールJSONに v0.12 の変更履歴コメントまたはレビューNoteを追加し、_JSON作成プロンプトにも同方針を追記。

##### 追加コメント

studio_work_incident_data_v0_22_rules_update_reporting_policy_added.json の v0.12-rules-update-reporting-policy 対応を依頼。各ルールJSONにも変更履歴コメントを追加する。

----
# AIチャットコメントに対する俺コメント追加

---
うぃーー、これはたぶん前回こっちが **「全部のルールJSONに同じ思想を横流ししすぎた」** 感あるね💦
整理すると、今回の v0.12 は **全ルールに同じ文章を入れる話ではなく、各ファイルの責務に応じて置き場所を分ける話** やと思う。

# v0.12-rules-update-reporting-policy ルール反映方針メモ

## まず全体方針

<!-- FRB_COMMENT_START id="frbcmt_20260622_194023_62pl" status="OK" -->
> ✅ **FRBコメント：OK**
>
> 了解。この方針でOK。
<!-- FRB_COMMENT_END -->

今回追加したい本質はこれ。

```text
AIが何を触ったか
なぜ触ったか
結果どうなったか
それをインシデントJSONに残す
```

ただし、これは **ViewDef生成ルールそのもの** ではなく、もう少し上位の **AI作業運用ルール**。

なので、配置としてはこう分けるのが自然。

```text
憲法 / Coding Constraints:
  AI作業時の守るべき原則

Foundation Rules:
  data / defs / wwwroot/data / wwwroot/defs の位置づけ

ViewDef Generation Rules:
  その情報を画面に出す場合のViewDef設計ルール

Schema Review:
  Schema変更が必要かどうかの判断メモ

JSON作成プロンプト:
  AIに作業させるときの短い実務指示
```

---

# 1. `frb_coding_constraints_review_data_v0_3.json`

## 役割

Studioくん憲法・AI作業時の安全柵。

ここが今回の **主戦場その1**。

## 追加・変更したらよい内容

### 追加候補

`constitution_20: AI協働ルール` あたりに追加するのが自然。

```text
AIがファイルを更新した場合、更新したファイル名、変更理由、変更概要、対応結果をインシデントJSONへ記録する。
```

記録先の考え方もここに置く。

```text
target_files:
  予定していた対象ファイル

target_rule_files:
  ルール更新作業で予定していたルールファイル

actual_updated_files:
  実際にAIが更新したファイル

latest_ai_response:
  AIの完了報告

discussion_history:
  作業依頼・判断・結果の会話履歴

change_history:
  変更前後と理由
```

<!-- FRB_COMMENT_START id="frbcmt_20260622_194322_1ixp" status="COMMENT" -->
> 💬 **FRBコメント：コメント**
>
> インシデントに情報追加する場合は、ご提案のテキスト文章の追加でOK。よろしく
<!-- FRB_COMMENT_END -->

### 修正候補

`root data/defs は原則変更しない` みたいな強い書き方がある場合は弱める。

<!-- FRB_COMMENT_START id="frbcmt_20260622_194545_b7se" status="COMMENT" -->
> 💬 **FRBコメント：コメント**
>
> root\data\json\01_main\studio_work_incident_data_*.json の更新済みファイルを収録して欲しいというのと、defやJsonDataはAIでも更新して欲しいという意図。でも、更新したら、その痕跡をどこかに記録して開示して欲しいという意図。
<!-- FRB_COMMENT_END -->

```text
root data/ / defs/:
  作業目的に必要ならAI更新可。
  ただし、更新ファイルと理由をインシデントJSONへ記録する。

wwwroot/data / wwwroot/defs:
  GitHub Pages等の公開用静的領域。
  明示依頼がない限りAI更新しない。
```

### 削る・弱める候補

```text
wwwroot/data 差分なし
wwwroot/defs 差分なし
```

これは毎回の必須報告ルールにはしない。
必要な作業のときだけ確認・報告でよい。

## 変更履歴コメントの入れ方

対象は `constitution_20`、必要なら `constitution_10` / `constitution_11` くらい。

全条文に入れない。

---

# 2. `frb_studio_foundation_review_data_v0_1.json`

## 役割

Studio全体の基礎方針・フォルダー思想・運用思想。

ここが今回の **主戦場その2**。

## 追加・変更したらよい内容

### 追加候補

`foundation_rule_007: Incident と Version Detail の関係` に寄せる。

```text
Incident JSON は、作業依頼・対象ファイル・実更新ファイル・AI完了報告・判断履歴を残す作業台帳である。
```

<!-- FRB_COMMENT_START id="frbcmt_20260622_194626_htxx" status="OK" -->
> ✅ **FRBコメント：OK**
>
> 了解。この方針でOK。
<!-- FRB_COMMENT_END -->

`foundation_rule_011: rules フォルダーの役割` に寄せる。

```text
root data/defs と wwwroot/data/defs は役割が違う。
```

整理するとこう。

```text
root data/:
  作業用・管理用Data JSONを置く場所。
  AIが更新することがある。

root defs/:
  作業用・管理用ViewDef JSONを置く場所。
  AIが更新することがある。

wwwroot/data/:
  公開・静的ホスティング用Data JSON。
  明示依頼がない限り更新しない。

wwwroot/defs/:
  公開・静的ホスティング用ViewDef JSON。
  明示依頼がない限り更新しない。
```

<!-- FRB_COMMENT_START id="frbcmt_20260622_194651_62dk" status="OK" -->
> ✅ **FRBコメント：OK**
>
> 了解。この方針でOK。
<!-- FRB_COMMENT_END -->

### 追加したい基本原則

```text
AIがroot data/defsを更新すること自体は禁止しない。
ただし、更新した事実をインシデントJSONに残す。
```

<!-- FRB_COMMENT_START id="frbcmt_20260622_194712_b5up" status="OK" -->
> ✅ **FRBコメント：OK**
>
> 了解。この方針でOK。
<!-- FRB_COMMENT_END -->

## 変更履歴コメントの入れ方

対象は以下あたりだけでよさそう。

```text
foundation_rule_007
foundation_rule_011
foundation_rule_018
```

<!-- FRB_COMMENT_START id="frbcmt_20260622_194719_fiz9" status="OK" -->
> ✅ **FRBコメント：OK**
>
> 了解。この方針でOK。
<!-- FRB_COMMENT_END -->

もし `foundation_rule_018` がすでにあるなら、そこを本命にして整える。

---

# 3. `frb_viewdef_generation_rules_review_data_v0_1.json`

## 役割

ViewDefをどう作るかのルール。

ここに **AI作業運用ルールを濃く入れすぎるとズレる**。

## 追加・変更したらよい内容

ここでは、運用ルールそのものではなく、

```text
インシデントJSONに記録された情報を、ViewDefでどう見せるか
```

に寄せるのがよい。

### 追加候補

`AI生成時の出力ルール` か `Detail Body readable cards` あたりに追加。

```text
インシデント管理ViewDefを生成する場合、以下のフィールドは見える位置に配置する。
```

候補フィールド。

```text
target_files
target_rule_files
actual_updated_files
ai_response
latest_ai_response
discussion_history
change_history
```

<!-- FRB_COMMENT_START id="frbcmt_20260622_194832_j8xl" status="ASK" -->
> ❓ **FRBコメント：要確認**
>
> ここまではまずはしなくてよいと思う。管理項目数はまずは押さえて運用したい。
<!-- FRB_COMMENT_END -->

### 表示方針

```text
target_files:
  予定対象としてカード表示

target_rule_files:
  ルール変更対象としてカード表示

actual_updated_files:
  実更新ファイル一覧としてカード表示

latest_ai_response:
  AI完了報告としてMarkdown表示

discussion_history:
  chat / objectArray として履歴表示

change_history:
  objectArray として変更前後を表示
```

<!-- FRB_COMMENT_START id="frbcmt_20260622_194907_k2xh" status="COMMENT" -->
> 💬 **FRBコメント：コメント**
>
> 項目ではなく、テキスト文章でのコメントを希望する。
<!-- FRB_COMMENT_END -->

### 注意点

ここでは、以下のような運用ルールを主語にしすぎない方がよい。

```text
AIはroot data/defsを更新してよい
AIはwwwroot/dataを更新してはいけない
```

<!-- FRB_COMMENT_START id="frbcmt_20260622_194919_716p" status="OK" -->
> ✅ **FRBコメント：OK**
>
> 了解。この方針でOK。
<!-- FRB_COMMENT_END -->

これは ViewDef生成ルールではなく、Foundation / Coding Constraints 側の責務。

ViewDef側ではこう言う程度でよい。

```text
Dataに作業対象・更新対象・AI回答欄が存在する場合、それらを人間が確認できるViewDefにする。
```

<!-- FRB_COMMENT_START id="frbcmt_20260622_194950_ovpm" status="OK" -->
> ✅ **FRBコメント：OK**
>
> 了解。この方針でOK。
<!-- FRB_COMMENT_END -->

## 変更履歴コメントの入れ方

対象は以下だけで十分。

```text
viewdef_rule_10_01 Detail Body readable cards
viewdef_rule_20 AI生成時の出力ルール
必要なら viewdef_rule_09 chat type
```

<!-- FRB_COMMENT_START id="frbcmt_20260622_195005_3tz3" status="OK" -->
> ✅ **FRBコメント：OK**
>
> 了解。この方針でOK。
<!-- FRB_COMMENT_END -->

今ある `viewdef_rule_20_01〜20_04` は、少し運用ルールに寄りすぎているなら、本文を薄くして **表示・生成時の扱い** に寄せるのが良さそう。

---

# 4. `frb_view_def_schema_review_data_v0_1.json`

## 役割

ViewDef Schema のレビュー記録。

ここは **今回ほぼ変更不要寄り**。

## 追加・変更したらよい内容

今回の `target_rule_files` / `actual_updated_files` は、基本的には **Data JSON側のフィールド名**。

ViewDef Schemaそのものの新しい構文ではない。

なので、ここに入れるならルール追加ではなく、レビューコメントでよい。

<!-- FRB_COMMENT_START id="frbcmt_20260622_195047_96cm" status="OK" -->
> ✅ **FRBコメント：OK**
>
> 了解。この方針でOK。
<!-- FRB_COMMENT_END -->

```text
v0.12の target_rule_files / actual_updated_files は、ViewDef Schemaの新規プロパティではなく、インシデント管理Data上のフィールドとして扱う。
現行Schemaでは fields[] に任意field名を定義できるため、Schema変更は必須ではない。
```

### 将来検討として残すなら

```text
もし将来、incident系DataをStudio標準管理データとして扱うなら、
target_rule_files / actual_updated_files / completion_report などを
標準メタフィールド候補として検討する。
```

<!-- FRB_COMMENT_START id="frbcmt_20260622_195119_spte" status="NG" -->
> 🚫 **FRBコメント：NG**
>
> まずは無しの方向で。
<!-- FRB_COMMENT_END -->

## 変更履歴コメントの入れ方

トップレベルの `review_notes` に1件でよい。
360件ある schema_items に無理に追加しない。

---

# 5. `_frb_view_def_schema_v0_9_chat_input_mapping.json`

## 役割

実際の ViewDef JSON Schema。

ここは **今回変更しない方がよい**。

<!-- FRB_COMMENT_START id="frbcmt_20260622_195127_91c8" status="OK" -->
> ✅ **FRBコメント：OK**
>
> 了解。この方針でOK。
<!-- FRB_COMMENT_END -->

## 理由

今回の話は、

```text
Data JSONの運用ルール
Incident JSONの記録ルール
AI作業完了報告の残し方
```

であって、

```text
ViewDef Schemaに新しい構文を追加する話
```

ではない。

`target_rule_files` や `actual_updated_files` は、ViewDef Schemaのプロパティではなく、Data側の任意フィールド。

だから、現時点では schema 本体に入れない。

## 将来変更するなら

以下のような新機能を入れるとき。

```text
markdown.blockActions
contextMenu
temporaryHighlight
commentBadge
blockToAiAction
```

つまり、Markdownプレビューのブロック操作をViewDef化するとき。

今回の v0.12 では不要。

---

# 6. `_json_creation_prompt.md`

## 役割

AIにViewDef JSONを作らせるときの実務プロンプト。

ここは **短く実務指示だけ入れる** のがよい。

## 追加・変更したらよい内容

今後のAI作業向けに、こういう短いチェックを入れる。

```text
ルール更新作業の場合:
- インシデントJSONの target_files / target_rule_files を確認する
- 予定外のファイルを更新しない
- 更新したファイルは actual_updated_files に記録する
- 完了報告は latest_ai_response に残す
- ルール本文を変更した場合は、その rule.change_history に変更前後と理由を残す
```

### 注意点

ここに長い思想文を入れすぎない。

このファイルはAIへの実務プロンプトなので、

```text
詳しい思想は frb_coding_constraints_review_data / foundation / viewdef_generation_rules を参照
```

<!-- FRB_COMMENT_START id="frbcmt_20260622_195241_689v" status="OK" -->
> ✅ **FRBコメント：OK**
>
> 了解。この方針でOK。
<!-- FRB_COMMENT_END -->

ぐらいがよい。

## 変更履歴コメントの入れ方

Markdownコメントで末尾に1行で十分。

```markdown
<!-- change_history: 2026-06-22 v0.12 / AI作業対象ファイル記録とインシデント回答記録の実務指示を追加 -->
```

<!-- FRB_COMMENT_START id="frbcmt_20260622_195249_90cm" status="OK" -->
> ✅ **FRBコメント：OK**
>
> 了解。この方針でOK。
<!-- FRB_COMMENT_END -->

---

# 7. インシデントJSON側に必要な考え方

これは `00_rules.zip` のルールファイルではないけど、今回の本命。

## 追加・整理したいフィールド

```text
target_files:
  作業依頼時点での予定対象

target_rule_files:
  ルール更新の場合の予定対象ルールファイル

actual_updated_files:
  AIが実際に更新したファイル

ai_response:
  その作業項目のAI回答・方針

latest_ai_response:
  今回対応後のAI完了報告

discussion_history:
  会話履歴

change_history:
  変更前後・理由
```

## 重要な整理

```text
target_files = 予定
actual_updated_files = 実績
latest_ai_response = 完了報告
change_history = 変更内容の履歴
discussion_history = 会話の履歴
```

<!-- FRB_COMMENT_START id="frbcmt_20260622_195419_xrcv" status="COMMENT" -->
> 💬 **FRBコメント：コメント**
>
> actual_updated_files = 実績　は、テキスト文字列でまずはスタート
<!-- FRB_COMMENT_END -->

この分離が大事。

---

# 今回の修正優先順位

## 優先度A

<!-- FRB_COMMENT_START id="frbcmt_20260622_195519_f4h7" status="COMMENT" -->
> 💬 **FRBコメント：コメント**
>
> 優先度Aだけの対応としましょう。
<!-- FRB_COMMENT_END -->

```text
frb_coding_constraints_review_data_v0_3.json
frb_studio_foundation_review_data_v0_1.json
_json_creation_prompt.md
```

ここに今回の運用ルールを入れる。

## 優先度B

```text
frb_viewdef_generation_rules_review_data_v0_1.json
```

ここは「インシデント管理ViewDefでどう見せるか」に限定して入れる。

## 優先度C

```text
frb_view_def_schema_review_data_v0_1.json
```

Schema変更不要の判断メモを残す程度。

## 原則変更なし

```text
_frb_view_def_schema_v0_9_chat_input_mapping.json
```

今回の v0.12 では触らない。

---

# まとめ

今回のズレはたぶんここ。

```text
前回の方向:
  各ルールJSONに同じ運用ルールを広く追加しすぎた

今回の正しい方向:
  ルールの責務ごとに置き場所を分ける
```

最終形はこれがよさそう。

```text
Coding Constraints:
  AI作業の義務として記録する

Foundation:
  data/defs と wwwroot/data/defs の役割を分ける

ViewDef Generation Rules:
  記録された情報を見えるViewDefにする

Schema Review:
  Schema変更は不要と判断記録する

Schema本体:
  触らない

JSON作成プロンプト:
  AIへの短い実務チェックだけ置く
```

<!-- FRB_COMMENT_START id="frbcmt_20260622_195549_cbuo" status="COMMENT" -->
> 💬 **FRBコメント：コメント**
>
> これは憲法に追加しましょう
<!-- FRB_COMMENT_END -->

これなら、ルールが太りすぎず、責務もかなり綺麗に分かれると思う。

---
# 2026-06-22 再対応依頼

v0.12-rules-update-reporting-policy に基づいて、ルールデータの修正を依頼。mdViewerで入れたFRBコメントを反映し、優先度Aを中心に対応する。

##### AI追加回答

v0.12-rules-update-reporting-policy 再対応完了。mdViewerで付与されたFRBコメントを反映し、優先度Aとして Coding Constraints / Foundation Rules / _json_creation_prompt.md を修正。root data/defs はAI更新可、wwwroot/data/defs は明示依頼がない限り更新しない方針を整理。更新ファイル・理由・対応結果は、まずテキスト文章でインシデントJSONへ残す運用に修正。前回過剰反映していた ViewDef Generation Rules のv0.12運用ルール群と Schema Review の将来検討メモは取り下げた。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0022_001 | 2026-06-22 | user | ルール系ブラッシュアップのインシデント追加 | ルール系ブラッシュアップ候補をインシデントとして管理したい。root data/defs まで原則変更しないという表現は強すぎるため削除したい。def/dataフォルダーはAI側でも更新してよく、どのファイルを更新したかをインシデントJSONへ記録してほしい。インシデント対応結果の報告内容もAI回答欄へ記録するルールにしたい。今回予定する変更内容がどのルールファイルに対する変更かも明記したい。 |
| disc_0022_002 | 2026-06-22 | assistant | インシデント追加結果 | studio_work_0022 を追加。root data/defs は一律保護ではなく、必要時更新可＋更新ファイル記録へ方針変更する作業項目として登録。AI対応報告を ai_response / latest_ai_response / discussion_history へ残す運用も対象に含めた。 |
| disc_0022_003 | 2026-06-22 | user | v0.12対応依頼 | studio_work_incident_data_v0_22_rules_update_reporting_policy_added.json v0.12-rules-update-reporting-policy の対応を依頼。各ルールJSONにも変更履歴コメントを追加してほしい。 |
| disc_0022_004 | 2026-06-22 | assistant | v0.12対応結果 | v0.12-rules-update-reporting-policy 対応完了。root data/defs は一律変更禁止ではなく、必要時更新可＋インシデントJSONへの更新ファイル記録をルール化。AI完了報告は ai_response / latest_ai_response / discussion_history に残す方針を追加。各ルールJSONに v0.12 の変更履歴コメントまたはレビューNoteを追加し、_JSON作成プロンプトにも同方針を追記。 |
| disc_0022_redo_20260622_user | 2026-06-22 | user | v0.12-rules-update-reporting-policy 再対応依頼 | mdViewerで入れたFRBコメントに基づき、優先度A中心でルールデータの修正を依頼。実更新ファイルはまずテキスト文字列で記録する方針。 |
| disc_0022_redo_20260622_assistant | 2026-06-22 | assistant | v0.12-rules-update-reporting-policy 再対応結果 | v0.12-rules-update-reporting-policy 再対応完了。mdViewerで付与されたFRBコメントを反映し、優先度Aとして Coding Constraints / Foundation Rules / _json_creation_prompt.md を修正。root data/defs はAI更新可、wwwroot/data/defs は明示依頼がない限り更新しない方針を整理。更新ファイル・理由・対応結果は、まずテキスト文章でインシデントJSONへ残す運用に修正。前回過剰反映していた ViewDef Generation Rules のv0.12運用ルール群と Schema Review の将来検討メモは取り下げた。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0022_001 | 2026-06-22 | root data/defs は一律変更禁止とはしない。 | root data/defs はAI作業で更新が必要になる場合があり、公開用領域である wwwroot/data・wwwroot/defs と同じ強さで保護すると運用が硬くなりすぎるため。 |
| dec_0022_002 | 2026-06-22 | AIが更新したファイルはインシデントJSONへ記録する。 | どのファイルを更新したかがインシデント単位で追えると、未来の人間とAIが作業経緯・影響範囲・判断理由を追体験しやすくなるため。 |
| dec_0022_003 | 2026-06-22 | インシデント対応後のAI報告内容を ai_response / latest_ai_response / discussion_history に残す。 | 会話上の完了報告だけでは後から流れやすいため、作業結果をインシデントJSONに残して管理画面上で確認できるようにするため。 |
| dec_0022_004 | 2026-06-22 | ルール変更インシデントでは、予定変更対象のルールファイルを明記する。 | ルール系ファイルが複数存在するため、どのルールに対する変更かを明示しないと、AIが正本や対象範囲を誤認するリスクがあるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0022_001 | 2026-06-22 | incident_added | studio_work_incident_data_v0_21_mdviewer_single_pane_blur_preview_done.json / items_count=21 | studio_work_incident_data_v0_22_rules_update_reporting_policy_added.json / items_count=22 | ルール系ブラッシュアップを細かい実装前にインシデントとして管理し、ユーザーコメントで文言調整できる状態にするため。 |
| chg_0022_002 | 2026-06-22 | rules_update_reporting_policy_applied | root data/defs の扱い、AI更新ファイル記録、AI完了報告のインシデント記録がルールJSON群へ十分に反映されていない状態 | 各ルールJSONにv0.12変更履歴コメントを追加し、AI更新ファイル記録とAI完了報告のインシデント記録を明文化。完了版は studio_work_incident_data_v0_23_rules_update_reporting_policy_done.json として保存。 | AI作業の更新対象と結果を、会話だけではなくインシデント管理データから追体験できるようにするため。 |
| chg_0022_redo_20260622_001 | 2026-06-22 | rules_scope_correction | 前回v0.12対応では ViewDef Generation Rules / Schema Review にも運用ルールを広く追加し、target_rule_files / actual_updated_files を構造フィールドとして扱う方向が強かった。 | 優先度A中心に修正。Coding Constraints / Foundation / JSON作成プロンプトに運用ルールを置き、実更新ファイルはまずテキスト文章でインシデントJSONへ残す。ViewDef Generation Rules / Schema Review の過剰反映は取り下げ。 | mdViewer上のFRBコメントで、管理項目数を抑え、コメント/報告はテキスト文章中心で始める方針が確認されたため。 |

### v0.11.7-mdviewer-dirty-block-comment: Markdown汚し方式の吹き出しFRBコメント
- 作業ID: studio_work_0023
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/mdViewer.html, wwwroot/js/runtime/MDVIEWER_DIRTY_BLOCK_COMMENT_NOTES_v0_11_7.md, studio_work_incident_data_v0_24_mdviewer_dirty_block_comment_done.json

#### 目的

Markdownプレビュー上の意味ブロックに対して、右クリックからFRBコメントを追加できるようにする。コメントはsidecar JSONではなく、Markdown本文をあえて汚す形式で挿入し、レビュー会話へそのまま貼り付けられる体験を確認する。

#### 背景

ブロックハイライト機能により、プレビュー上の意味ブロックを操作対象にできる感覚が得られた。次の段階として、AI案やルール案に対して「了解」「NG」「要修正」「要確認」などの人間コメントをUI上で明確に残し、コメントする文化を育てたい。

#### 対象範囲

mdViewer.htmlのプレビューブロック右クリックメニューにコメント系アクションを追加する。対象ブロック直後に FRB_COMMENT_START / FRB_COMMENT_END で囲んだMarkdownコメントブロックを挿入し、Previewでは吹き出し風コメントとして表示する。

#### 対象外

sidecar JSONによるコメント永続化、コメント一覧管理、レビューJSONへの自動流し込み、AI自動分類、複数コメントの高度な編集UIは今回対象外。まずはMarkdown汚し方式で体験確認を行う。

#### 固定名方針

FRB_COMMENT_START / FRB_COMMENT_END はMarkdown内コメントブロックを機械抽出するための明示マーカーとして扱う。RuntimeのData固定名ではなく、Markdownレビュー記法としての固定マーカーである。

#### module化方針

type="module" 化は行わない。既存のmdViewer.html内script方式を維持し、最新資材に対して最小差分で追加する。

#### リスク

Markdown本文を汚すため、公開用Markdownにそのまま残るリスクがある。コードブロックやテーブル内部へ挿入するとMarkdown構造を壊す可能性があるため、対象ブロック直後へ挿入する方針とする。

#### 確認観点

mdViewer.html inline scriptがnode --check OKであること。wwwroot/js/*.jsがnode --check OKであること。右クリックメニューから各コメント種別を挿入できること。FRB_COMMENTがPreviewで吹き出し風に表示されること。コメント付きMarkdownコピーが使えること。

#### 作業会話サマリ


##### 依頼 / 方針

Markdown汚し方式の吹き出しコメントをインシデントに追加した上で、最新資材に対して対応してほしい。コメントをする文化を大切に育てたい。

##### AI整理

対応方針: sidecar JSON保存設計には進まず、まずはMarkdown本文をあえて汚すFRB_COMMENT方式で、ブロック単位のコメント体験を実装する。コメントは対象ブロック直後に挿入し、Previewでは吹き出し風に表示する。

##### 追加コメント

Markdown汚し方式の吹き出しコメントをインシデントに追加した上で、最新資材に対して対応をお願いします。コメントをする文化を大切に育てよう！！

##### AI追加回答

v0.11.7-mdviewer-dirty-block-comment 対応完了。mdViewer.html に右クリックコメントメニューを追加し、対象ブロック直後へ FRB_COMMENT_START / FRB_COMMENT_END 付きMarkdownコメントを挿入できるようにした。PreviewではFRBコメントを吹き出し風に表示し、コメント付きMarkdown全体をコピーできる導線も追加した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0023_001 | 2026-06-22 | user | 機能相談 | mdViewer.htmlに、Markdownを汚していいから意味ブロックごとにコメントを入れたい。コメントしたものをレビュー会話に貼り付けたい。UI的にコメントだと分かる吹き出しコメントにしたい。 |
| disc_0023_002 | 2026-06-22 | assistant | 方針整理 | Markdown内に FRB_COMMENT_START / FRB_COMMENT_END マーカー付きコメントを挿入し、Previewでは吹き出し風に表示する方式を提案。sidecar JSONより軽く、レビュー会話へそのまま貼り付けられる。 |
| disc_0023_003 | 2026-06-22 | user | 作業依頼 | Markdown汚し方式の吹き出しコメントをインシデントに追加した上で、最新資材に対して対応してほしい。コメントする文化を大切に育てたい。 |
| disc_0023_004 | 2026-06-22 | assistant | 作業結果 | mdViewer.htmlへ右クリックコメントメニュー、FRB_COMMENT挿入、吹き出しPreview表示、コメント付きMarkdownコピーを追加。ノートファイル MDVIEWER_DIRTY_BLOCK_COMMENT_NOTES_v0_11_7.md を追加。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0023_001 | 2026-06-22 | コメントはsidecar JSONではなくMarkdown本文へ挿入する。 | まずはコメント文化とレビュー会話へ貼り付ける体験を優先し、保存設計を重くしないため。 |
| dec_0023_002 | 2026-06-22 | コメントは対象ブロックの直後へ挿入する。 | コードブロックやテーブル内部を壊さず、意味ブロックに対する人間コメントとして読みやすくするため。 |
| dec_0023_003 | 2026-06-22 | FRB_COMMENT_START / FRB_COMMENT_END を固定マーカーとして採用する。 | Markdownを汚しつつ、後からAIやRuntimeがコメント範囲を機械抽出できるようにするため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0023_001 | 2026-06-22 | mdviewer_dirty_comment | mdViewerのプレビュー右クリックでは一時ハイライトのみ可能で、意味ブロックに人間コメントを残す導線はなかった。 | 右クリックからコメント追加/OK/NG/要修正/要確認コメントを選び、FRB_COMMENT付きMarkdownブロックを対象ブロック直後に挿入できるようにした。 | AI案やルール案に対する人間判断を、テキストだけでなくUI上で明確なコメントとして残し、レビュー会話へ貼り付けられるようにするため。 |
| chg_0023_002 | 2026-06-22 | preview_rendering | FRB_COMMENT記法は存在せず、コメントをUI的に吹き出し表示する仕組みはなかった。 | FRB_COMMENT_START / END で囲まれたコメントをPreviewで吹き出し風に表示する preprocessFrbComments を追加。 | Markdown本文は汚すが、Preview上では人間がコメントだと一目で分かる表示にするため。 |

### v0.13-md-block-model-foundation: Markdown Block Model基盤 / SentenceBlock化
- 作業ID: studio_work_0024
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/mdViewer.html, wwwroot/js/markdown/*, wwwroot/js/runtime/*

#### 目的

Markdown本文を直接文字列編集するのではなく、見出し・段落・リスト・表・コードブロック等のBlock構造へ分解し、UI上で選択可能なSentenceBlock/Blockとして扱う基盤を作る。

#### 背景

MarkdownをAI協働の文書Dataとして普及させるには、文章全体をtextareaで編集するだけでは弱い。Copilotが出した表形式計画案のように、部分単位で指摘・修正・差し込みできる編集粒度が必要になった。

#### 対象範囲

mdViewerのプレビュー表示時にMarkdownをBlock配列へ分解し、各Blockへblock_id/type/source_range等の内部情報を付与する。まずは表示・選択・点線枠表示までを対象とし、編集保存は後続インシデントで扱う。

#### 対象外

完全なMarkdown AST互換、全Markdown方言対応、表セル編集、コメント永続化、AI自動レビュー連携は対象外。まずブロック選択できる基盤を作る。

#### 固定名方針

block_id / table_id はMarkdown編集Runtimeの内部識別子として扱う。Data JSONの固定フィールド名ではなく、Markdown編集セッション内の構造識別子である。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、mdViewer/Runtime側へ最小差分で追加する。必要なら将来の分割・Registry化は別インシデントで扱う。

#### リスク

Markdownパーサを作り込みすぎると実装が肥大化する。コードブロック内の記号や表内の | を誤認識して構造を壊すリスクがあるため、MVPでは対応Markdown範囲を明示する。

#### 確認観点

見出し、段落、箇条書き、表、コードブロック、引用を含むMarkdownを読み込み、想定どおりBlock化されること。コードブロック内部は編集対象Blockとして分解しすぎないこと。カレントBlockが点線枠で分かること。

#### 作業会話サマリ


##### 依頼 / 方針

Markdownの表のセル単位編集とセル単位コメントをしたい。背景として、会社でCopilotが出してきた表形式の計画案に対してコメント・編集したかったが、Markdown上ではうまくできず、やむなくExcelに頼った。Json+Markdownを普及させるには、MarkdownをSentenceBlock/CellBlock単位で編集・コメントできる機能が必要だと感じた。

##### AI整理

Markdownを直接文字列編集するのではなく、MarkdownをBlock構造へ分解し、SentenceBlock / TableCellBlock として編集したうえでMarkdownへ再生成する方針が現実的。巨大案件にせず、基盤・段落編集・表セル編集・コメント永続化・レビューUI・保存安全性・代表fixtureに分割して登録する。

##### 追加コメント

じゃーー覚悟して、進みますかぁーーーJson＋MarkDownの未来に向かって！！ v0.13-md-block-model-foundation の対応をお願いしまっす！！ファーストステップゴー！！

##### AI追加回答

v0.13-md-block-model-foundation 対応完了。mdViewerにMarkdown Block Model Runtimeを追加し、Markdown原文をfront_matter / heading / paragraph / list_item / table / code_block / blockquote / horizontal_ruleへ分解する基盤を実装。Preview DOMへ data-md-block-id / data-md-block-type / data-md-table-id を付与し、Editorモードで点線枠・current block管理・Block Modelメタ表示・右クリックBlock情報確認を可能にした。表はTable Blockとしてrows/cellsメタデータまで持たせたが、セル編集・コメント永続化は後続v0.13.2/v0.13.3へ分離。保存値はMarkdown原文のまま保持し、HTMLやBlock JSONは混入しない。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0024_001 | 2026-06-24 | user | Markdownセル編集/コメント機能の背景共有 | Markdownの表のセル単位編集とセル単位コメントをしたい。背景として、会社でCopilotが出してきた表形式の計画案に対してコメント・編集したかったが、Markdown上ではうまくできず、やむなくExcelに頼った。Json+Markdownを普及させるには、MarkdownをSentenceBlock/CellBlock単位で編集・コメントできる機能が必要だと感じた。 |
| disc_0024_002 | 2026-06-24 | assistant | インシデント分割方針 | Markdownを直接文字列編集するのではなく、MarkdownをBlock構造へ分解し、SentenceBlock / TableCellBlock として編集したうえでMarkdownへ再生成する方針が現実的。巨大案件にせず、基盤・段落編集・表セル編集・コメント永続化・レビューUI・保存安全性・代表fixtureに分割して登録する。 |
| disc_0024_003 | 2026-06-24 | user | v0.13-md-block-model-foundation 作業依頼 | じゃーー覚悟して、進みますかぁーーーJson＋MarkDownの未来に向かって！！ v0.13-md-block-model-foundation の対応をお願いしまっす！！ファーストステップゴー！！ |
| disc_0024_004 | 2026-06-24 | assistant | v0.13-md-block-model-foundation 作業結果 | v0.13-md-block-model-foundation 対応完了。mdViewerにMarkdown Block Model Runtimeを追加し、Markdown原文をfront_matter / heading / paragraph / list_item / table / code_block / blockquote / horizontal_ruleへ分解する基盤を実装。Preview DOMへ data-md-block-id / data-md-block-type / data-md-table-id を付与し、Editorモードで点線枠・current block管理・Block Modelメタ表示・右クリックBlock情報確認を可能にした。表はTable Blockとしてrows/cellsメタデータまで持たせたが、セル編集・コメント永続化は後続v0.13.2/v0.13.3へ分離。保存値はMarkdown原文のまま保持し、HTMLやBlock JSONは混入しない。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0024_001 | 2026-06-24 | Markdown本文を直接編集対象にせず、Block構造へ変換してから編集対象にする。 | 直接文字列編集では挿入・削除・コメント位置管理が破綻しやすく、削除後の空行整理や表セル位置追跡が難しいため。 |
| dec_0024_002 | 2026-06-24 | v0.13では完全Markdown ASTではなく、mdViewer内MVP Block Modelとして実装する。 | 表セル編集・コメント永続化まで一気に作ると肥大化するため、まずPreview DOMとMarkdown原文の対応付けを安定させる。 |
| dec_0024_003 | 2026-06-24 | Table Blockはrows/cellsメタデータまで保持するが、セル編集UIは後続インシデントに分離する。 | 会社でCopilot表を編集できずExcelに逃げた課題に向けた足場は必要だが、初回はBlock基盤を壊さず小さく成立させるため。 |
| dec_0024_004 | 2026-06-24 | Block ModelはMarkdown本文へ保存せず、Runtime内部状態とPreview DOM属性として扱う。 | Markdown原文を原本として守り、HTMLや一時的なBlock JSONを保存値へ混入させないため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0024_001 | 2026-06-24 | incident_registration | Markdown表セル編集・セルコメント・SentenceBlock編集に関する作業項目が未登録。 | v0.13-md-block-model-foundation として作業項目を登録。 | 会社でCopilot表形式計画案をMarkdown上でレビューできずExcelへ逃げた実体験を、JSON+Markdown普及に必要な機能改善として回収するため。 |
| chg_0024_002 | 2026-06-24 | md_block_model_foundation_runtime_added | mdViewerはdata-md-line中心でPreview要素とMarkdown行を対応付けていたが、Block ID/type/source_range/table cellsを持つ正式なBlock Model Runtimeはなかった。 | markdownBlockModelRuntimeとparseMarkdownBlocksを追加し、Preview要素へdata-md-block-id/type/table-idを付与。サイドバーでBlock Model状態を表示し、右クリックメニューからBlock情報を確認できるようにした。 | MarkdownをSentenceBlock / TableCellBlock単位で編集・コメントする後続機能の土台を作るため。 |

### v0.13.1-md-sentence-insert-delete: SentenceBlockの＋挿入 / 削除 / Markdown再生成
- 作業ID: studio_work_0025
- 種別: feature
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/mdViewer.html, wwwroot/js/markdown/*, wwwroot/js/runtime/*, styles.css

#### 目的

カレントSentenceBlockの点線枠付近に「＋」を表示し、前後へのセンテンス挿入と既存センテンス削除を行い、Markdownへ綺麗に再生成できるようにする。

#### 背景

Markdownで文章を育てるには、既存文を修正するだけでなく、途中へ一文足す・不要文を消す操作が必要。textarea全体編集では、レビュー対象の文脈と操作対象がズレやすい。

#### 対象範囲

paragraph/list item相当のSentenceBlockを対象に、insert before/after、delete、empty block cleanup、空行正規化、Undo用の直前バックアップを実装する。

#### 対象外

表セル編集、複数ブロック一括移動、ドラッグ&ドロップ並べ替え、AI自動挿入提案は対象外。

#### 固定名方針

insert/delete操作名はMarkdown Editor内部Actionとして扱う。Runtimeが特定Dataフィールド名に依存しないよう、対象はcurrentBlockIdで渡す。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、mdViewer/Runtime側へ最小差分で追加する。必要なら将来の分割・Registry化は別インシデントで扱う。

#### リスク

削除時に見出し直下の空行やリスト構造を壊すリスクがある。文章ブロックとMarkdown構文ブロックの境界を誤ると公開用Markdownが崩れる。

#### 確認観点

段落の前後挿入、段落削除、リスト項目削除、見出し直後への挿入、末尾挿入を確認する。削除後に余計な空行が増えないこと。保存前後でMarkdown構造が破綻しないこと。

#### 作業会話サマリ


##### 依頼 / 方針

Markdownの表のセル単位編集とセル単位コメントをしたい。背景として、会社でCopilotが出してきた表形式の計画案に対してコメント・編集したかったが、Markdown上ではうまくできず、やむなくExcelに頼った。Json+Markdownを普及させるには、MarkdownをSentenceBlock/CellBlock単位で編集・コメントできる機能が必要だと感じた。

##### AI整理

Markdownを直接文字列編集するのではなく、MarkdownをBlock構造へ分解し、SentenceBlock / TableCellBlock として編集したうえでMarkdownへ再生成する方針が現実的。巨大案件にせず、基盤・段落編集・表セル編集・コメント永続化・レビューUI・保存安全性・代表fixtureに分割して登録する。

##### 追加コメント

v0.13.1.2-md-sentence-toolbar-row-anchor-fix 確認完了。カレント枠1本＋対象行右端の操作バーで軽快な操作感になった。

##### AI追加回答

v0.13.1.2-md-sentence-toolbar-row-anchor-fix 対応完了。v0.13.1.1の安全領域/corridor方式を撤回し、SentenceBlock操作バーを対象Blockの右端・中央付近に固定表示するrow-anchor方式へ変更した。カレント表示は青系の1本に統一し、hoverは薄い背景のみへ弱めた。操作バー表示中はBlock IDバッジを非表示にし、ボタン下に隠れたラベルが見える問題も抑止した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0025_001 | 2026-06-24 | user | Markdownセル編集/コメント機能の背景共有 | Markdownの表のセル単位編集とセル単位コメントをしたい。背景として、会社でCopilotが出してきた表形式の計画案に対してコメント・編集したかったが、Markdown上ではうまくできず、やむなくExcelに頼った。Json+Markdownを普及させるには、MarkdownをSentenceBlock/CellBlock単位で編集・コメントできる機能が必要だと感じた。 |
| disc_0025_002 | 2026-06-24 | assistant | インシデント分割方針 | Markdownを直接文字列編集するのではなく、MarkdownをBlock構造へ分解し、SentenceBlock / TableCellBlock として編集したうえでMarkdownへ再生成する方針が現実的。巨大案件にせず、基盤・段落編集・表セル編集・コメント永続化・レビューUI・保存安全性・代表fixtureに分割して登録する。 |
| disc_0025_003 | 2026-06-24 | user | v0.13.1作業依頼 | v0.13.1-md-sentence-insert-delete の対応を依頼。セカンドステップとして、SentenceBlockの＋挿入 / 削除 / Markdown再生成に進む。 |
| disc_0025_004 | 2026-06-24 | assistant | v0.13.1作業結果 | EditorモードのPreview上でBlockへマウスを乗せると、＋上/＋下/削除/↩の操作バーを表示するようにした。右クリックメニューにも同等のSentenceBlock操作を追加。操作時はMarkdown原文を行単位で更新し、Previewを再描画する。直前操作バックアップも追加した。 |
| disc_0025_003 | 2026-06-24 | user | v0.13.1操作バー逃げる問題 | SentenceBlock操作バーへマウスを移動させようとするとメニューが逃げることがある。追加は1回でき、追加行の削除はできた。メニューの下に何か表示されているが隠れて見えない。 |
| disc_0025_004 | 2026-06-24 | assistant | v0.13.1.1操作バーsticky fix対応結果 | インライン操作バーにsticky制御を追加。操作バーとカレントBlockの間の安全領域ではhover対象を切り替えないようにし、操作バーへマウス移動しても逃げにくくした。操作バー表示中はBlock IDバッジを非表示にして重なり表示を解消。 |
| disc_0025_007 | 2026-06-24 | user | v0.13.1.2 row-anchor修正依頼 | カレント行を緑色と青色の2つ作っているように見えて意味が分からない。単純にメニューをその行の右端に出せば解決しないか、という相談。v0.13.1.2-md-sentence-toolbar-row-anchor-fix の対応を依頼。 |
| disc_0025_008 | 2026-06-24 | assistant | v0.13.1.2 row-anchor修正結果 | 安全領域方式を撤回し、操作バーを対象Blockの右端に固定するrow-anchor方式へ変更。カレント枠は1本に統一し、hover表示は薄い背景のみへ弱めた。Block IDバッジは操作バー表示中に非表示化した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0025_001 | 2026-06-24 | SentenceBlockの挿入・削除はBlock配列操作後にMarkdown再生成する。 | Markdown文字列に対して直接spliceすると、空行・リスト・表・コードブロックの整合性を保ちにくいため。 |
| dec_0025_002 | 2026-06-24 | SentenceBlock操作はDOM直接編集ではなくMarkdown原文更新後の再描画方式とする。 | Preview DOMだけを編集すると保存値と表示が乖離しやすい。Markdown原文を更新して再描画すれば、保存値を原文のまま保ち、Block ID/行範囲も再計算できるため。 |
| dec_0025_003 | 2026-06-24 | ＋挿入UIはEditorモードのPreview上に小さな操作バーとして表示する。 | textarea全体編集へ戻らず、対象Blockの文脈上で「足す/消す」を実行できる体験を優先するため。 |
| dec_0025_004 | 2026-06-24 | v0.13.1ではSentenceBlock=Markdown Blockとして扱い、表セル編集はv0.13.2へ分離する。 | 表セル編集まで同時に入れると、Block挿入削除の保存安全性確認とセル編集の複雑性が混ざるため。 |
| dec_0025_004 | 2026-06-24 | SentenceBlock操作バーはhover追従だけでなく、操作バーへ移動するための安全領域を持つsticky UIにする。 | Block上に表示された操作バーへ向かう途中でhover対象が別Blockに切り替わると、バーが再配置されて逃げるため。 |
| dec_0025_005 | 2026-06-24 | 操作バー表示中はBlock IDバッジを非表示にする。 | 操作バーとBlock IDバッジが同じBlock付近に表示されると重なり、何か出ているが読めない状態になるため。Block情報は右クリックメニューやメタ表示で確認できる。 |
| dec_0025_007 | 2026-06-24 | v0.13.1.1の安全領域方式は撤回し、row-anchor方式へ変更する。 | 安全領域方式ではカレント行とhover/safe-zone由来の枠が二重に見え、操作対象が分かりにくくなるため。操作バーを対象行の右端に所属させる方が、視線移動とマウス移動が自然になる。 |
| dec_0025_008 | 2026-06-24 | カレント表示は1本に統一し、hover表示は弱める。 | Markdown編集時に「いま操作しているBlock」が一目で分からないと、挿入・削除操作の信頼感が下がるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0025_001 | 2026-06-24 | incident_registration | Markdown表セル編集・セルコメント・SentenceBlock編集に関する作業項目が未登録。 | v0.13.1-md-sentence-insert-delete として作業項目を登録。 | 会社でCopilot表形式計画案をMarkdown上でレビューできずExcelへ逃げた実体験を、JSON+Markdown普及に必要な機能改善として回収するため。 |
| chg_0025_002 | 2026-06-24 | md_sentence_insert_delete_runtime | v0.13ではMarkdown Block ModelによりPreview上のBlock特定はできたが、Block単位で文を追加・削除する操作は存在しなかった。 | EditorモードのPreview上でBlock付近に＋上/＋下/削除/↩操作バーを表示し、右クリックメニューからも同操作を実行できるようにした。挿入・削除はMarkdown原文へ反映し、renderMarkdownで再描画する。 | Markdownを単なる表示対象ではなく、SentenceBlock単位で育てられる編集対象に進化させるため。 |
| chg_0025_002 | 2026-06-24 | md_sentence_toolbar_sticky_fix | カレントBlockからインライン操作バーへマウス移動する途中で別Blockへhover判定が切り替わり、操作バーが逃げることがあった。Block IDバッジも操作バーの下に重なって見えにくかった。 | 操作バーのmouseenter/mouseleaveと安全領域判定を追加し、バーへ移動中はカレントBlockを維持するようにした。操作バー表示中はBlock IDバッジを非表示にした。 | ＋挿入 / 削除 / Undo を安定して押せるようにするため。 |
| chg_0025_004 | 2026-06-24 | md_sentence_toolbar_row_anchor_fix | v0.13.1.1では、操作バーを逃がさないために安全領域/corridor判定を追加したが、結果としてカレント枠とhover/safe-zone系の枠が二重に見え、操作対象が分かりにくくなっていた。 | 安全領域/corridor判定を撤回し、操作バーを対象Blockの右端・中央付近へ固定表示するrow-anchor方式に変更。カレント枠は1本に統一し、hoverは薄い背景のみへ弱めた。 | SentenceBlock操作は、対象行と操作ボタンの関係が直感的に分かる必要があるため。 |

### v0.13.2-md-table-cell-editor: Markdown表セル単位編集
- 作業ID: studio_work_0026
- 種別: feature
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/mdViewer.html, wwwroot/js/markdown/*, wwwroot/js/runtime/*, styles.css

#### 目的

Markdown表をTableBlockとして認識し、セル単位でクリック選択・編集ダイアログ表示・値更新・Markdown表再生成を行えるようにする。

#### 背景

会社でCopilotが提示した表形式の計画案に対して、セル単位でコメント・修正したかったがMarkdown上では難しく、Excelへ逃げるしかなかった。この悔しさが本件の直接の起点である。

#### 対象範囲

GitHub Flavored Markdown相当の単純な表を対象に、header/align/body rowsを解析し、table_id/row_index/column_keyでセルを識別する。セル編集はインラインではなく小ダイアログから行い、| はエスケープ、改行は <br> へ変換する。

#### 対象外

結合セル、複雑なHTML表、セル内の複数段落Markdown、表全体の高度な整形、Excel完全互換は対象外。まずCopilotの計画表を編集できる最小機能に限定する。

#### 固定名方針

row_index / column_key / table_id はMarkdown Table Editor内部の識別子。Data固定名ではなく、Markdown表構造の一時識別子として扱う。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、mdViewer/Runtime側へ最小差分で追加する。必要なら将来の分割・Registry化は別インシデントで扱う。

#### リスク

Markdown表は |、改行、桁揃え、エスケープの扱いで壊れやすい。セル内Markdownを許可しすぎると再生成が不安定になるため、MVPでは1行セルを基本にする。

#### 確認観点

Copilot風の計画表を読み込み、任意セルを編集して保存できること。| が \| として保存されること。セル内改行が <br> へ変換されること。表の列数が崩れないこと。

#### 作業会話サマリ


##### 依頼 / 方針

Markdownの表のセル単位編集とセル単位コメントをしたい。背景として、会社でCopilotが出してきた表形式の計画案に対してコメント・編集したかったが、Markdown上ではうまくできず、やむなくExcelに頼った。Json+Markdownを普及させるには、MarkdownをSentenceBlock/CellBlock単位で編集・コメントできる機能が必要だと感じた。

##### AI整理

Markdown表セル単位編集MVPとして、GFM風の単純表に限定し、セルクリック→小ダイアログ編集→Markdown表行再生成の方式で実装した。表セル編集はインライン編集ではなく小ダイアログ方式とし、Markdown原文へHTMLを混入させない。

##### 追加コメント

よぉーーーー　じゃぁーー　v0.13.2-md-table-cell-editor　お願い！！　サードステップGo！！

##### AI追加回答

v0.13.2-md-table-cell-editor は実機確認済み。表セルクリック→小ダイアログ編集→反映でMarkdown表セルが更新されることを確認。キャッシュクリア後に正常動作した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0026_001 | 2026-06-24 | user | Markdownセル編集/コメント機能の背景共有 | Markdownの表のセル単位編集とセル単位コメントをしたい。背景として、会社でCopilotが出してきた表形式の計画案に対してコメント・編集したかったが、Markdown上ではうまくできず、やむなくExcelに頼った。Json+Markdownを普及させるには、MarkdownをSentenceBlock/CellBlock単位で編集・コメントできる機能が必要だと感じた。 |
| disc_0026_002 | 2026-06-24 | assistant | インシデント分割方針 | Markdownを直接文字列編集するのではなく、MarkdownをBlock構造へ分解し、SentenceBlock / TableCellBlock として編集したうえでMarkdownへ再生成する方針が現実的。巨大案件にせず、基盤・段落編集・表セル編集・コメント永続化・レビューUI・保存安全性・代表fixtureに分割して登録する。 |
| disc_0026_002 | 2026-06-24 | user | v0.13.2-md-table-cell-editor作業依頼 | v0.13.2-md-table-cell-editor の対応を依頼。Markdown表セル単位編集へ進み、Excelに逃げたくなる領域へ踏み込みたい。 |
| disc_0026_003 | 2026-06-24 | assistant | v0.13.2-md-table-cell-editor作業結果 | mdViewer.htmlにTableCell編集MVPを追加。TableBlockのDOM tableへセルメタデータを付与し、Editorモードのセルクリックで小ダイアログを表示。反映時は対象Markdown表行を再生成し、Previewを再描画する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0026_001 | 2026-06-24 | 表セル編集はMVPでは小ダイアログ方式にする。 | インライン編集はカーソル制御・列幅・Markdown再生成の難易度が高く、最初の実装では事故りやすいため。 |
| dec_0026_002 | 2026-06-24 | 表セル編集はMVPでは小ダイアログ方式で実装する。 | インライン編集はカーソル制御・列幅・Markdown再生成の難易度が高く、まず安全にセル単位編集の体験を確認するため。 |
| dec_0026_003 | 2026-06-24 | DOM上のtbody行はMarkdown表のseparator行を飛ばしてrowIndex+2として扱う。 | GFM表はMarkdown上ではheader/separator/bodyだが、HTML DOMにはseparator行が描画されないため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0026_001 | 2026-06-24 | incident_registration | Markdown表セル編集・セルコメント・SentenceBlock編集に関する作業項目が未登録。 | v0.13.2-md-table-cell-editor として作業項目を登録。 | 会社でCopilot表形式計画案をMarkdown上でレビューできずExcelへ逃げた実体験を、JSON+Markdown普及に必要な機能改善として回収するため。 |
| chg_0026_002 | 2026-06-24 | md_table_cell_editor_mvp | Markdown表はTableBlockとして認識されていたが、Preview上のth/tdセル単位で選択・編集するUIはなかった。表を直すにはMarkdown原文かExcelへ逃げる必要があった。 | Preview上の表セルへTableCellメタデータを付与し、Editorモードでセルクリックまたは右クリックメニューから小ダイアログ編集できるようにした。反映時は対象行のみMarkdown表として再生成する。 | JSON+MarkdownをAI協働の編集基盤にするには、Copilot等が出す表形式計画案をExcelに逃がさず、その場でセル単位編集できる体験が必要なため。 |

### v0.13.3-md-comment-sidecar-json: SentenceBlock / TableCell コメント sidecar JSON
- 作業ID: studio_work_0027
- 種別: feature
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/mdViewer.html, wwwroot/js/markdown/*, wwwroot/js/runtime/*, comments sidecar data files

#### 目的

Markdown本文を汚さずに、SentenceBlockやTableCellへコメントを付けられるsidecar JSON方式を導入する。

#### 背景

Markdown汚し方式のFRBコメントは体験確認として有効だったが、表セル単位コメントをMarkdown本文へ直接埋め込むと表が壊れやすい。レビューコメントは本文と分離し、必要に応じて表示・解決・AI共有できる形が望ましい。

#### 対象範囲

article.md に対して article.md.comments.json のようなsidecar JSONを持ち、block_id/table_id/row_index/column_key/comment/status/author/created_at を保存する。Markdown本体は原文を維持する。

#### 対象外

複数ユーザー同時編集、クラウド同期、コメントのGitHub PR連携、AI自動コメント生成は対象外。

#### 固定名方針

comments.jsonの標準キーはMarkdownコメントレイヤー仕様として扱う。Studio一般Dataの固定名ではなく、sidecar comment schemaとして明示的に定義する。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、mdViewer/Runtime側へ最小差分で追加する。必要なら将来の分割・Registry化は別インシデントで扱う。

#### リスク

block_idがMarkdown編集により変化するとコメントの紐づけが外れるリスクがある。表の行追加・削除時にrow_indexだけでは位置がズレる可能性があるため、将来的にanchor textやhash補助が必要。

#### 確認観点

SentenceBlockコメント、TableCellコメントを追加して保存・再読込できること。Markdown本文にはコメント本文が混入しないこと。表セル編集後も可能な範囲でコメント紐づけが維持されること。

#### 作業会話サマリ


##### 依頼 / 方針

Markdownの表のセル単位編集とセル単位コメントをしたい。背景として、会社でCopilotが出してきた表形式の計画案に対してコメント・編集したかったが、Markdown上ではうまくできず、やむなくExcelに頼った。Json+Markdownを普及させるには、MarkdownをSentenceBlock/CellBlock単位で編集・コメントできる機能が必要だと感じた。

##### AI整理

Markdownを直接文字列編集するのではなく、MarkdownをBlock構造へ分解し、SentenceBlock / TableCellBlock として編集したうえでMarkdownへ再生成する方針が現実的。巨大案件にせず、基盤・段落編集・表セル編集・コメント永続化・レビューUI・保存安全性・代表fixtureに分割して登録する。

##### 追加コメント

フォースステップ v0.13.3-md-comment-sidecar-json の対応依頼。Markdown本文を汚さず、SentenceBlock / TableCell コメントをsidecar JSONとして保存できるようにしたい。

# v0.13.3.1 追補
Sidecar JSON がファイルとして見当たらない。Program.cs関連ソース一式を渡すので、MarkdownコメントSidecar JSONを実ファイルへ保存できるように対応してほしい。

##### AI追加回答

v0.13.3-md-comment-sidecar-json は実機確認済み。本文上のコメントバッジ表示、操作バーとの配置調整、本文を汚さないSidecarコメントの基本動作を確認。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0027_001 | 2026-06-24 | user | Markdownセル編集/コメント機能の背景共有 | Markdownの表のセル単位編集とセル単位コメントをしたい。背景として、会社でCopilotが出してきた表形式の計画案に対してコメント・編集したかったが、Markdown上ではうまくできず、やむなくExcelに頼った。Json+Markdownを普及させるには、MarkdownをSentenceBlock/CellBlock単位で編集・コメントできる機能が必要だと感じた。 |
| disc_0027_002 | 2026-06-24 | assistant | インシデント分割方針 | Markdownを直接文字列編集するのではなく、MarkdownをBlock構造へ分解し、SentenceBlock / TableCellBlock として編集したうえでMarkdownへ再生成する方針が現実的。巨大案件にせず、基盤・段落編集・表セル編集・コメント永続化・レビューUI・保存安全性・代表fixtureに分割して登録する。 |
| disc_0027_001 | 2026-06-24 | user | v0.13.3-md-comment-sidecar-json作業依頼 | 現実味がでてきたので、フォースステップ v0.13.3-md-comment-sidecar-json の対応を依頼。Markdown本文を汚さず、コメントをsidecar JSONへ分離したい。 |
| disc_0027_002 | 2026-06-24 | assistant | v0.13.3-md-comment-sidecar-json作業結果 | mdViewer.htmlにSidecar JSONコメントRuntimeを追加。右クリックメニューのコメント追加をSidecar JSON方式に切り替え、SentenceBlock/TableCellのターゲット情報をコメントJSONへ保存できるようにした。Preview上にはコメントバッジを表示し、Sidecar JSONの保存・コピーも可能にした。 |
| disc_0027_0133_1_user | 2026-06-24 | user | Sidecar JSON実ファイル保存相談 | Sidecar JSON がどのパスに保存されているか見当たらない。Program.cs関連ソース一式を送るので対応してほしい。 |
| disc_0027_0133_1_assistant | 2026-06-24 | assistant | v0.13.3.1 Sidecar API保存対応 | Program.cs の SafeMarkdownPath を拡張し、data/markdown 配下で .md / .markdown に加えて .md.comments.json / .markdown.comments.json を許可。GET時はSidecar JSONを application/json として返す。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0027_001 | 2026-06-24 | 表セルコメントはMarkdown本文へ直接埋め込まず、sidecar JSONを第一候補とする。 | Markdown表内部へコメントを埋め込むと表構造が壊れやすく、公開用Markdownにもレビューコメントが漏れるリスクがあるため。 |
| dec_0027_001 | 2026-06-24 | コメントはMarkdown本文へ直接挿入せず、sidecar JSONを第一候補とする。 | Markdown本文にレビューコメントを混ぜると、公開用本文・表構造・Diffが汚れるため。 |
| dec_0027_002 | 2026-06-24 | sidecar名は article.md に対して article.md.comments.json とする。 | 対象Markdownとの対応関係が人間にもAIにも分かりやすく、ファイル単位で持ち運びやすいため。 |
| dec_0027_003 | 2026-06-24 | v0.13.3ではコメント解決・一覧UI・編集UIは本格実装しない。 | それらは v0.13.4-md-comment-review-ui の範囲とし、今回は永続化とターゲット紐づけの基盤に集中するため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0027_001 | 2026-06-24 | incident_registration | Markdown表セル編集・セルコメント・SentenceBlock編集に関する作業項目が未登録。 | v0.13.3-md-comment-sidecar-json として作業項目を登録。 | 会社でCopilot表形式計画案をMarkdown上でレビューできずExcelへ逃げた実体験を、JSON+Markdown普及に必要な機能改善として回収するため。 |
| chg_0027_001 | 2026-06-24 | md_comment_sidecar_json_runtime | 右クリックコメントはMarkdown本文へFRBコメントブロックを挿入する汚し方式が中心だった。TableCellコメントの保存先も本文側に寄りやすかった。 | 右クリックコメントはSidecar JSONへ保存する方式に変更。SentenceBlockはblock、TableCellはtable_cellとしてtarget情報を保持し、Preview上にバッジを表示する。 | Markdown本文を公開用本文として綺麗に保ちつつ、レビューコメントを構造化データとしてAIと共有できるようにするため。 |
| chg_0027_0133_1 | 2026-06-24 | backend_api_save_fix | /api/markdown/{name} は .md / .markdown のみ許可していたため、mdViewer側が送る <md名>.comments.json はBadRequestになり、localStorageフォールバックだけに残っていた。 | /api/markdown/{name} で <md名>.comments.json / <markdown名>.comments.json を data/markdown 配下に保存・読込できるようにした。 | Sidecar JSONをブラウザ内だけでなく実ファイルとして残し、Git diffやAI共有に使えるようにするため。 |

### v0.13.4-md-comment-review-ui: Markdownコメント表示 / 解決 / コメント一覧UI
- 作業ID: studio_work_0028
- 種別: feature
- 優先度: medium
- 状態: 完了
- 確認状態: 確認待ち
- 対象ファイル: wwwroot/mdViewer.html, wwwroot/js/runtime/MARKDOWN_COMMENT_REVIEW_UI_NOTES_v0_13_4.md

#### 目的

SentenceBlock/TableCellに付与されたコメントを、本文上のバッジ・サイド一覧・解決状態として確認できるレビューUIを整える。

#### 背景

コメントを保存できても、本文上でどこにコメントが付いているか分からなければレビュー文化として使いにくい。Excelのセルコメントのように、対象箇所とコメントの関係が一目で見える必要がある。

#### 対象範囲

左サイドバーにコメントレビュー一覧を追加する。Sidecar JSON内のコメントを、未解決/全件/解決済で絞り込み、クリックで対象Block/TableCellへスクロールする。コメントの解決/再開、本文編集、削除を行い、既存Sidecar保存処理で .comments.json へ保存する。

#### 対象外

コメントスレッドの多段返信、通知、権限管理、外部レビューサービス連携は対象外。

#### 固定名方針

status/open/resolved 等はcomment sidecar schema内の状態値として扱う。Runtimeが任意Dataフィールドへ固定依存しないよう、comment layer専用に閉じる。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、mdViewer/Runtime側へ最小差分で追加する。必要なら将来の分割・Registry化は別インシデントで扱う。

#### リスク

UIが重くなるとMarkdown Viewerの読みやすさが落ちる。コメントが多い場合に本文が騒がしくなるため、表示ON/OFFや一覧への逃がしが必要。

#### 確認観点

Sidecarコメント追加後に左のコメントレビュー一覧へ表示されること。一覧クリックで対象Block/TableCellへジャンプすること。解決で本文上のバッジから消え、解決済フィルターに移ること。再開で未解決に戻ること。編集/削除後に .comments.json が更新されること。Markdown本文にコメント情報が混入しないこと。

#### 作業会話サマリ


##### 依頼 / 方針

Markdownの表のセル単位編集とセル単位コメントをしたい。背景として、会社でCopilotが出してきた表形式の計画案に対してコメント・編集したかったが、Markdown上ではうまくできず、やむなくExcelに頼った。Json+Markdownを普及させるには、MarkdownをSentenceBlock/CellBlock単位で編集・コメントできる機能が必要だと感じた。

##### AI整理

v0.13.4-md-comment-review-ui は、v0.13.3で保存できるようになったSidecarコメントを、レビュー可能なUIとして扱う段階。本文上の小さなバッジだけではコメント全体を追いにくいため、コメント一覧・ジャンプ・解決状態管理をMVPとして実装する。

##### 追加コメント

v0.13.4-md-comment-review-ui の概要確認後、実装を依頼。Sidecarコメントを一覧で見て、対象へジャンプし、解決/未解決を管理できるようにしたい。

##### AI追加回答

v0.13.4-md-comment-review-ui 対応完了。左サイドバーにコメントレビュー一覧を追加し、未解決/全件/解決済フィルター、コメントクリックで対象Block/TableCellへジャンプ、解決/再開、編集、削除を実装。変更は既存Sidecar保存処理で .comments.json へ保存し、Markdown本文は汚さない。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0028_001 | 2026-06-24 | user | Markdownセル編集/コメント機能の背景共有 | Markdownの表のセル単位編集とセル単位コメントをしたい。背景として、会社でCopilotが出してきた表形式の計画案に対してコメント・編集したかったが、Markdown上ではうまくできず、やむなくExcelに頼った。Json+Markdownを普及させるには、MarkdownをSentenceBlock/CellBlock単位で編集・コメントできる機能が必要だと感じた。 |
| disc_0028_002 | 2026-06-24 | assistant | インシデント分割方針 | Markdownを直接文字列編集するのではなく、MarkdownをBlock構造へ分解し、SentenceBlock / TableCellBlock として編集したうえでMarkdownへ再生成する方針が現実的。巨大案件にせず、基盤・段落編集・表セル編集・コメント永続化・レビューUI・保存安全性・代表fixtureに分割して登録する。 |
| disc_0028_20260624_user | 2026-06-24 | user | v0.13.4-md-comment-review-ui 作業依頼 | 概要確認後、v0.13.4-md-comment-review-ui の対応を依頼。コメント一覧、解決/未解決、対象へのジャンプを実用化したい。 |
| disc_0028_20260624_assistant | 2026-06-24 | assistant | v0.13.4-md-comment-review-ui 作業結果 | mdViewer.htmlへコメントレビューUIを追加。Sidecarコメントを左サイドバーに一覧表示し、フィルター、対象ジャンプ、一時ハイライト、解決/再開、編集、削除に対応した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0028_001 | 2026-06-24 | コメントは本文常時展開ではなく、バッジ＋一覧で扱う。 | 常時本文へ吹き出し表示すると、Markdown本文の読解体験が崩れ、レビュー対象そのものが読みにくくなるため。 |
| dec_0028_20260624_001 | 2026-06-24 | v0.13.4のMVPは、コメント一覧・対象ジャンプ・解決/再開を中心にする。 | コメント追加機能だけでは、コメントが増えた時に未対応箇所を追跡できないため。まず付箋を一覧管理できるレビューUIを優先する。 |
| dec_0028_20260624_002 | 2026-06-24 | コメント本文の編集/削除もMVPに含めるが、Markdown本文には混入させない。 | コメントはSidecar JSONの責務であり、Markdown本文を公開用本文として綺麗に保つため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0028_001 | 2026-06-24 | incident_registration | Markdown表セル編集・セルコメント・SentenceBlock編集に関する作業項目が未登録。 | v0.13.4-md-comment-review-ui として作業項目を登録。 | 会社でCopilot表形式計画案をMarkdown上でレビューできずExcelへ逃げた実体験を、JSON+Markdown普及に必要な機能改善として回収するため。 |
| chg_0028_20260624_001 | 2026-06-24 | md_comment_review_ui | Sidecarコメントは本文上の小さなバッジとJSONコピー/保存で扱えたが、全コメントの一覧、未解決件数、対象ジャンプ、解決状態管理がなかった。 | 左サイドバーにコメントレビュー一覧を追加し、未解決/全件/解決済フィルター、クリックジャンプ、一時ハイライト、解決/再開、編集、削除を実装した。 | Markdown + Sidecar JSONを、コメントを付けるだけでなくレビュー運用できる道具へ進めるため。 |

### v0.13.5-md-roundtrip-save-safety: Markdown Block編集の保存安全性 / RoundTrip / Diff確認
- 作業ID: studio_work_0029
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/mdViewer.html, wwwroot/js/markdown/*, wwwroot/js/runtime/*, Program.cs if save API changes are needed

#### 目的

Block編集・表セル編集・コメント操作後も、Markdown本文とsidecar JSONが安全に保存され、意図しない本文破壊が起きないことを確認する保存安全性レイヤーを作る。

#### 背景

Markdownを構造編集する以上、保存時に本文が壊れると信頼を失う。JSON+Markdown普及のためには、Excelに逃げなくても安全に戻れるという安心感が必須である。

#### 対象範囲

保存前バックアップ、差分プレビュー、RoundTrip検査、コードブロック保護、表列数検査、sidecar JSONの整合性検査を行う。まずは手動確認できるログ/警告を優先する。

#### 対象外

完全な自動テストスイート、Git操作自動化、外部バックアップサービス連携は対象外。まず保存前後で壊れていないか見えるようにする。

#### 固定名方針

RoundTrip検査用の内部メタ情報はMarkdown Editor Runtime内に閉じる。Markdown本文へ不可視メタを大量埋め込みしない。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、mdViewer/Runtime側へ最小差分で追加する。必要なら将来の分割・Registry化は別インシデントで扱う。

#### リスク

安全性チェックを厳しくしすぎると保存できないケースが増える。逆に緩すぎると本文破壊を見逃すため、警告と強行保存のバランスが必要。

#### 確認観点

編集なし保存で本文が変化しないこと。段落追加/削除後の差分が最小であること。表セル編集後に列数が崩れないこと。sidecar comments JSONが壊れている場合に警告できること。

#### 作業会話サマリ


##### 依頼 / 方針

Markdownの表のセル単位編集とセル単位コメントをしたい。背景として、会社でCopilotが出してきた表形式の計画案に対してコメント・編集したかったが、Markdown上ではうまくできず、やむなくExcelに頼った。Json+Markdownを普及させるには、MarkdownをSentenceBlock/CellBlock単位で編集・コメントできる機能が必要だと感じた。

##### AI整理

Markdownを直接文字列編集するのではなく、MarkdownをBlock構造へ分解し、SentenceBlock / TableCellBlock として編集したうえでMarkdownへ再生成する方針が現実的。巨大案件にせず、基盤・段落編集・表セル編集・コメント永続化・レビューUI・保存安全性・代表fixtureに分割して登録する。

##### 追加コメント

Markdownの表のセル単位編集とセル単位コメントをしたい。背景として、会社でCopilotが出してきた表形式の計画案に対してコメント・編集したかったが、Markdown上ではうまくできず、やむなくExcelに頼った。Json+Markdownを普及させるには、MarkdownをSentenceBlock/CellBlock単位で編集・コメントできる機能が必要だと感じた。

##### AI追加回答

v0.13.5-md-roundtrip-save-safety を新規インシデントとして登録。MarkdownをAI協働用の編集基盤へ進化させるため、まず現実的な改善単位に分割して管理する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0029_001 | 2026-06-24 | user | Markdownセル編集/コメント機能の背景共有 | Markdownの表のセル単位編集とセル単位コメントをしたい。背景として、会社でCopilotが出してきた表形式の計画案に対してコメント・編集したかったが、Markdown上ではうまくできず、やむなくExcelに頼った。Json+Markdownを普及させるには、MarkdownをSentenceBlock/CellBlock単位で編集・コメントできる機能が必要だと感じた。 |
| disc_0029_002 | 2026-06-24 | assistant | インシデント分割方針 | Markdownを直接文字列編集するのではなく、MarkdownをBlock構造へ分解し、SentenceBlock / TableCellBlock として編集したうえでMarkdownへ再生成する方針が現実的。巨大案件にせず、基盤・段落編集・表セル編集・コメント永続化・レビューUI・保存安全性・代表fixtureに分割して登録する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0029_001 | 2026-06-24 | Markdown構造編集には保存前差分確認とRoundTrip検査をセットで導入する。 | Markdownを再生成する方式では、意図しない整形差分や構造破壊が起きる可能性があるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0029_001 | 2026-06-24 | incident_registration | Markdown表セル編集・セルコメント・SentenceBlock編集に関する作業項目が未登録。 | v0.13.5-md-roundtrip-save-safety として作業項目を登録。 | 会社でCopilot表形式計画案をMarkdown上でレビューできずExcelへ逃げた実体験を、JSON+Markdown普及に必要な機能改善として回収するため。 |

### v0.13.6-md-copilot-table-review-fixture: Copilot表形式計画案レビュー用fixture
- 作業ID: studio_work_0030
- 種別: maintenance
- 優先度: medium
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/data/markdown/copilot_table_review_fixture_v0_13_6.md, wwwroot/data/markdown/copilot_table_review_fixture_v0_13_6.md.comments.json, wwwroot/js/runtime/MARKDOWN_COPILOT_TABLE_REVIEW_FIXTURE_NOTES_v0_13_6.md

#### 目的

Copilotが出力しがちな表形式の計画案Markdownを代表サンプルとして用意し、表セル編集・セルコメント・SentenceBlockコメントの確認に使えるfixtureを整備する。

#### 背景

今回の直接の痛みは、会社でCopilotが出した表形式計画案をMarkdown上でレビューできず、Excelに頼ったこと。実体験に近いfixtureがないと、実装しても本当に欲しかった体験に近づいたか判断しにくい。

#### 対象範囲

計画案テーブル、担当/期限/状態/懸念/コメント欄を含むサンプルMarkdownと、コメントsidecar JSON例、確認手順を用意する。

#### 対象外

実際の会社情報や機密計画の投入は対象外。架空データで、構造と不満だけを再現する。

#### 固定名方針

fixture内の列名はサンプルDataでありRuntime固定名ではない。Runtimeは列名に依存せず、table headerからcolumn_keyを生成する。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、mdViewer/Runtime側へ最小差分で追加する。必要なら将来の分割・Registry化は別インシデントで扱う。

#### リスク

実データに近づけすぎると機密情報混入リスクがある。fixtureは架空の計画案として作成し、構造だけ再現する。

#### 確認観点

fixtureを読み込み、表セル編集、セルコメント追加、SentenceBlockコメント追加、保存、再読込が一通り確認できること。

#### 作業会話サマリ


##### 依頼 / 方針

Markdownの表のセル単位編集とセル単位コメントをしたい。背景として、会社でCopilotが出してきた表形式の計画案に対してコメント・編集したかったが、Markdown上ではうまくできず、やむなくExcelに頼った。Json+Markdownを普及させるには、MarkdownをSentenceBlock/CellBlock単位で編集・コメントできる機能が必要だと感じた。

##### AI整理

Markdownを直接文字列編集するのではなく、MarkdownをBlock構造へ分解し、SentenceBlock / TableCellBlock として編集したうえでMarkdownへ再生成する方針が現実的。巨大案件にせず、基盤・段落編集・表セル編集・コメント永続化・レビューUI・保存安全性・代表fixtureに分割して登録する。

##### 追加コメント

とりあえずの最終ステップとして、v0.13.6-md-copilot-table-review-fixture の対応を依頼。Copilot風の表形式計画案fixtureを追加し、表セル編集・TableCellコメント・コメントレビューUI・Save Safetyの実戦確認に使えるようにする。

##### AI追加回答

v0.13.6-md-copilot-table-review-fixture 対応完了。実会社情報を含まない架空のCopilot風計画案Markdownを追加し、初期SidecarコメントJSONも同時に用意。Markdown表セル編集、TableCellコメント、コメントレビュー一覧ジャンプ、Save Safetyを1ファイルで確認できるfixtureとして整備した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0030_001 | 2026-06-24 | user | Markdownセル編集/コメント機能の背景共有 | Markdownの表のセル単位編集とセル単位コメントをしたい。背景として、会社でCopilotが出してきた表形式の計画案に対してコメント・編集したかったが、Markdown上ではうまくできず、やむなくExcelに頼った。Json+Markdownを普及させるには、MarkdownをSentenceBlock/CellBlock単位で編集・コメントできる機能が必要だと感じた。 |
| disc_0030_002 | 2026-06-24 | assistant | インシデント分割方針 | Markdownを直接文字列編集するのではなく、MarkdownをBlock構造へ分解し、SentenceBlock / TableCellBlock として編集したうえでMarkdownへ再生成する方針が現実的。巨大案件にせず、基盤・段落編集・表セル編集・コメント永続化・レビューUI・保存安全性・代表fixtureに分割して登録する。 |
| disc_0030_20260624_user_001 | 2026-06-24 | user | v0.13.6 fixture作成依頼 | とりあえずの最終ステップ v0.13.6-md-copilot-table-review-fixture の対応を依頼。 |
| disc_0030_20260624_assistant_001 | 2026-06-24 | assistant | v0.13.6 fixture作成結果 | Copilot風の架空計画案MarkdownとSidecarコメントJSONを追加。表セル編集・TableCellコメント・コメントレビューUI・Save Safetyをまとめて確認できるfixtureとして整備。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0030_001 | 2026-06-24 | 実会社情報は使わず、Copilot風の架空計画案fixtureで検証する。 | 会社情報・業務計画の機密混入を避けつつ、Excelへ逃げたくなった編集体験だけを安全に再現するため。 |
| dec_0030_20260624_001 | 2026-06-24 | v0.13.6ではRuntime機能追加ではなく、実戦確認用fixtureを追加する。 | v0.13.1〜v0.13.5で主要機能は通っているため、最後にCopilot風の表形式計画案を使って実運用に近い確認を行うため。 |
| dec_0030_20260624_002 | 2026-06-24 | fixtureは実会社情報を含まない架空データにする。 | 会社情報・業務計画の機密混入を避けつつ、Excelへ逃げたくなった編集体験だけを安全に再現するため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0030_001 | 2026-06-24 | incident_registration | Markdown表セル編集・セルコメント・SentenceBlock編集に関する作業項目が未登録。 | v0.13.6-md-copilot-table-review-fixture として作業項目を登録。 | 会社でCopilot表形式計画案をMarkdown上でレビューできずExcelへ逃げた実体験を、JSON+Markdown普及に必要な機能改善として回収するため。 |
| chg_0030_20260624_001 | 2026-06-24 | fixture_added | Copilot表形式計画案レビューをまとめて試せるMarkdown fixtureが存在しなかった。 | copilot_table_review_fixture_v0_13_6.md と .comments.json を追加し、表セル編集・コメント・レビュー一覧・Save Safetyを一括確認できるようにした。 | v0.13系で作ったMarkdown構造編集機能を、実戦に近い表形式計画案で確認するため。 |

### v0.13.3.1-md-comment-sidecar-api-save-fix: MarkdownコメントSidecar JSONのAPI実ファイル保存対応
- 作業ID: studio_work_0031
- 種別: bugfix
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: Program.cs

#### 目的

mdViewerで作成したMarkdownコメントSidecar JSONを、localStorageだけでなく data/markdown 配下の実ファイルとして保存・読込できるようにする。

#### 背景

v0.13.3でSidecar JSON方式を導入したが、既存Program.csの /api/markdown/{name} は .md / .markdown のみ許可していた。そのため article.md.comments.json の保存APIがBadRequestになり、ブラウザlocalStorageフォールバックにだけ残っていた。

#### 対象範囲

Program.csのSafeMarkdownPathを拡張し、Markdown本文ファイルに紐づく .md.comments.json / .markdown.comments.json のみ許可する。GET時はSidecar JSONを application/json; charset=utf-8 として返す。保存先は既存の data/markdown 配下とし、mdViewer側の既存 /api/markdown/{sidecarName} 呼び出しをそのまま活かす。

#### 対象外

任意JSON保存API化、Markdownサブフォルダー対応、Sidecarコメント一覧UI、コメント編集・削除、解決状態管理、RoundTrip安全検査は今回対象外。

#### 固定名方針

許可するファイル名は Markdown本文に紐づく .comments.json のみ。RuntimeやAPIが任意Dataフィールド名に依存する変更ではない。

#### module化方針

type="module" 化は行わない。既存Program.csのMinimal API構成を維持する。

#### リスク

/api/markdownを任意JSON保存口にしてしまうと事故るため、.md.comments.json / .markdown.comments.json のみに限定する。content-type変更による既存Markdown読込への影響に注意する。

#### 確認観点

mdViewerでSidecarコメントを追加し、data/markdown/<md名>.comments.json が作成されること。再読込後にSidecarコメントが復元されること。.jsonだけの任意ファイル名はBadRequestになること。既存.md/.markdown本文の読込・保存が従来どおり動くこと。

#### 作業会話サマリ


##### 依頼 / 方針

Program.cs関連のソース一式送付するので、Sidecar JSONを実ファイルに保存できるように対応してほしい。

##### AI整理

Program.cs側でMarkdown管理APIの許可拡張を行う。Markdown本文は .md/.markdown、Sidecarは .md.comments.json/.markdown.comments.json のみ許可し、保存先は data/markdown に統一する。

##### 追加コメント

Program.cs関連のソース一式を送付。これで対応してほしい。

##### AI追加回答

v0.13.3.1-md-comment-sidecar-api-save-fix は実機確認済み。data/markdown 配下に <mdファイル名>.comments.json が物理ファイルとして生成されることを確認。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0031_001 | 2026-06-24 | user | Sidecar JSON保存先確認 | sidecar JSON がどのパスに保存されているか見当たらない。 |
| disc_0031_002 | 2026-06-24 | assistant | 原因説明 | 現状はlocalStorageフォールバックに残っている可能性が高い。Program.csの /api/markdown が .comments.json を許可していないため、実ファイル保存に失敗している。 |
| disc_0031_003 | 2026-06-24 | user | Program.csソース提供 | Program.cs関連のソース一式を送るので対応してほしい。 |
| disc_0031_004 | 2026-06-24 | assistant | 対応結果 | Program.csのSafeMarkdownPathを拡張し、Markdown本文に紐づくSidecar JSONだけをdata/markdown配下に保存できるようにした。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0031_001 | 2026-06-24 | Sidecar JSONの保存先は data/markdown/<md名>.comments.json とする。 | Markdown本文と同じ管理領域に置くことで、記事本文とレビューコメントの対応関係が分かりやすくなるため。 |
| dec_0031_002 | 2026-06-24 | /api/markdown は任意JSONではなく、Markdown本文に紐づく .comments.json のみ許可する。 | APIを広げすぎると任意JSON保存口になり、安全性と責務が崩れるため。 |
| dec_0031_003 | 2026-06-24 | mdViewer側の既存 /api/markdown/{sidecarName} 呼び出しは変更しない。 | フロント側は既にSidecar保存を試行しているため、今回はバックエンドの許可条件だけを直すのが最小安全修正になるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0031_001 | 2026-06-24 | program_cs_safe_markdown_path_fix | SafeMarkdownPath は .md / .markdown のみ許可。<md名>.comments.json は invalid file name となりAPI保存できなかった。 | SafeMarkdownPath が .md.comments.json / .markdown.comments.json も許可。GET時はSidecar JSONを application/json として返す。 | SidecarコメントをlocalStorageだけではなく実ファイルとして保存するため。 |

### v0.13.4.1-md-comment-review-sidebar-compact-layout: Markdownコメントレビュー左サイドバーのコンパクトレイアウト調整
- 作業ID: studio_work_0032
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/mdViewer.html, wwwroot/js/runtime/MARKDOWN_COMMENT_REVIEW_SIDEBAR_COMPACT_LAYOUT_NOTES_v0_13_4_1.md

#### 目的

v0.13.4で追加したコメントレビューUIにより、100%表示時に左バーが縦方向へ収まりにくくなったため、右バー化する前に左バー内の目次・ドキュメントメタ・コメントレビューをコンパクト化し、各領域内スクロールで操作できるようにする。

#### 背景

コメントレビュー一覧が入ったことで、左の目次・ドキュメントメタ・コメント一覧が縦に長くなり、ブラウザを縮小しないと操作しづらい状態になった。現在の『左=ナビ/メタ/レビュー、中央=本文』の構成は自然なので、まずは右バーへ逃がさず左バーの3段レイアウト化で解決する。

#### 対象範囲

mdViewer.htmlの左サイドバーを画面高に収めるグリッドレイアウトへ変更する。目次パネルとコメントレビュー一覧は内部スクロールにし、ドキュメントメタはコンパクト表示にする。コメントカードは本文表示を2行程度に抑え、100%表示でも左バー全体が扱いやすくなるようにする。

#### 対象外

右バー化、Sidecar JSON形式変更、コメントレビューの解決/編集/削除ロジック変更、wwwroot/data配下およびwwwroot/defs配下の更新は行わない。

#### 固定名方針

特定Markdownファイル名やコメント内容には依存しない。mdViewer.htmlのUIレイアウト調整として扱う。

#### module化方針

type="module"化は行わず、既存mdViewer.html単体script構成を維持する。今回の主変更はCSSとHTML class追加に限定する。

#### リスク

左バーを画面高に固定するため、極端に低い画面高では各パネルが窮屈になる可能性がある。狭幅画面では縦積みへ戻すレスポンシブ設定で回避する。

#### 確認観点

ブラウザ100%表示で左バー全体が画面内に収まること。目次が内部スクロールできること。コメントレビュー一覧が内部スクロールできること。ドキュメントメタが過度に高さを取らないこと。コメント一覧クリック・解決・編集・削除が従来どおり動くこと。

#### 作業会話サマリ


##### 依頼 / 方針

v0.13.4-md-comment-review-ui は良いが、縮小しないと操作できない。左の目次の高さを少し低くして、コメント一覧の高さも抑えめにしてスクロールで対応し、100%の状態で左バーの内容が画面に収まるようにしたい。窮屈なら右バー案も検討したい。

##### AI整理

右バー化は保留し、まず左バーを3段レイアウト化して、目次・メタ・コメントレビューをコンパクト化する方針で対応。現在の左バー構成はレビュー道具として自然なので、内部スクロールとカード圧縮で100%表示時の操作性を改善する。

##### 追加コメント

では、調整お願いします！！ v0.13.4.1-md-comment-review-sidebar-compact-layout

##### AI追加回答

v0.13.4.1対応完了。mdViewer.htmlの左サイドバーを画面高に収めるグリッド構成へ変更し、目次とコメントレビュー一覧を内部スクロール化。ドキュメントメタとコメントカードをコンパクト化し、100%表示時でも左バーを扱いやすくした。wwwroot/dataおよびwwwroot/defs配下は変更なし。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0032_001 | 2026-06-24 | user | v0.13.4 UI確認 | コメントレビューUIは良いが、画面をかなり縮小しないと操作しづらい。左の目次とコメント一覧の高さを抑えて、100%表示で左バー内に収めたい。右バー化も検討対象。 |
| disc_0032_002 | 2026-06-24 | assistant | 対応方針 | 右バー化は本文幅を削るため保留。まずは左バー内を、目次・ドキュメントメタ・コメントレビューの3段レイアウトにして、各領域内スクロールで対応する。 |
| disc_0032_003 | 2026-06-24 | user | 作業依頼 | v0.13.4.1-md-comment-review-sidebar-compact-layout の調整を依頼。 |
| disc_0032_004 | 2026-06-24 | assistant | 作業結果 | mdViewer.htmlのみを実質変更し、左サイドバーの高さ固定・内部スクロール・メタ表示圧縮・コメントカード圧縮を実施。実装メモを追加した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0032_001 | 2026-06-24 | コメントレビューUIは右バーへ移動せず、まず左バー内のコンパクト化で対応する。 | 右バー化すると本文幅が削られ、Markdown本文を読む体験が落ちるため。現在の左=ナビ/メタ/レビュー、中央=本文の構成が自然なため、まず左バーを整える。 |
| dec_0032_002 | 2026-06-24 | 目次とコメントレビュー一覧はパネル内スクロールにする。 | 左バー全体をページスクロールに任せると、100%表示時に下部のコメント操作へ届きにくくなるため。 |
| dec_0032_003 | 2026-06-24 | wwwroot/data および wwwroot/defs 配下は変更しない。 | 今回の目的はmdViewerのレイアウト調整であり、公開用Data/ViewDef領域を更新する必要がないため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0032_001 | 2026-06-24 | mdviewer_sidebar_compact_layout | 左サイドバーに目次・ドキュメントメタ・コメントレビューが縦に並び、コメントレビュー追加後は100%表示で全体が収まりにくかった。 | 左サイドバーを画面高に収める3段グリッドに変更。目次とコメントレビュー一覧は内部スクロール化し、ドキュメントメタとコメントカードをコンパクト化した。 | ブラウザ100%表示でも左バー内のナビ・メタ・コメントレビューを操作できるようにするため。 |

### v0.13.5-md-roundtrip-save-safety: Markdown Block編集の保存安全性 / RoundTrip / Diff確認
- 作業ID: studio_work_0033
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/mdViewer.html, wwwroot/js/runtime/MARKDOWN_ROUNDTRIP_SAVE_SAFETY_NOTES_v0_13_5.md

#### 目的

Block編集・表セル編集・Sidecarコメント操作後も、Markdown本文とSidecar JSONが安全に保存され、意図しない本文破壊や表構造崩れが起きないことを保存前後で確認する。

#### 背景

v0.13系でMarkdown本文をBlock化し、SentenceBlock挿入/削除、TableCell編集、Sidecarコメント、コメントレビューUIまで進んだ。編集力が増えたぶん、保存時に本文・表・コメント参照を壊さない安全性レイヤーが必要になった。

#### 対象範囲

上書き保存前にSave Safety検査を実行する。コードフェンス閉じ忘れ、表列数不一致、Sidecarコメント対象Block/TableCellの参照、Markdownレンダリング例外、読込時点との差分行数サマリを確認する。保存前にlocalStorageへ直前バックアップを保存し、保存後にAPIから再取得してRoundTrip一致を確認する。手動の保存検査ボタンも追加する。

#### 対象外

Git diff相当の詳細差分ビュー、バックアップ一覧UI、復元ボタン、Markdown ASTによる厳密な再生成比較、Program.csのAPI追加は今回の対象外。まずmdViewer.html単体のMVP保存安全性に限定する。

#### 固定名方針

Save SafetyはMarkdown ViewerのUI操作契約として実装し、特定Markdownファイル名や特定Dataフィールド名には依存しない。localStorageキーのprefixはmdViewer保存バックアップ用の内部契約として扱う。

#### module化方針

mdViewer.html単体script構成を維持する。type=module化やJS分割は行わない。

#### リスク

保存前検査が厳しすぎると通常保存の邪魔になる。逆に緩すぎると壊れた表や迷子コメントを見逃す。localStorageバックアップは容量制限により失敗する可能性があるため、失敗時は警告に留める。

#### 確認観点

保存検査ボタンで検査結果が表示されること。正常MarkdownではOK表示になること。未閉じコードブロックではエラーになり保存が中止されること。列数不一致のMarkdown表ではエラーになること。Sidecarコメント対象が見つからない場合は警告になること。上書き保存後にAPI再取得で本文一致を確認すること。localStorageにfrb-md-save-backup:<filename>:latestが保存されること。

#### 作業会話サマリ


##### 依頼 / 方針

v0.13.5-md-roundtrip-save-safety の対応依頼。MarkdownレビューStudioとして実用化が進んできたため、次に保存安全性を入れたい。

##### AI整理

v0.13.5-md-roundtrip-save-safety 対応完了。mdViewer.htmlに保存検査ボタン、保存前Save Safety検査、localStorage直前バックアップ、保存後RoundTrip確認を追加。本文・表構造・Sidecarコメント参照を保存前に検査し、エラー時は保存中止、警告時は確認ダイアログを出す。

##### 追加コメント

よし、次！！v0.13.5-md-roundtrip-save-safety よろしくぅ！！

##### AI追加回答

Save Safetyレイヤーを追加。上書き保存時に自動検査し、手動の保存検査ボタンでも確認できるようにした。検査前にはlocalStorageへMarkdown本文とSidecar JSONの直前バックアップを保存し、保存後はAPIから再取得してRoundTrip一致を確認する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0033_001 | 2026-06-24 | user | v0.13.5作業依頼 | v0.13.5-md-roundtrip-save-safety の対応を依頼。 |
| disc_0033_002 | 2026-06-24 | assistant | v0.13.5作業結果 | 保存検査ボタン、保存前検査、localStorageバックアップ、保存後RoundTrip確認を追加。エラー時は保存中止、警告時は確認付き保存にした。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0033_001 | 2026-06-24 | 保存安全性はまずmdViewer.html単体のMVPとして実装する。 | Program.csやdiff専用UIまで広げると作業範囲が肥大化するため、保存前検査・バックアップ・保存後確認に絞る。 |
| dec_0033_002 | 2026-06-24 | 保存前にlocalStorageへ直前バックアップを残す。 | 保存検査やAPI保存の前に復旧材料を残しておくことで、本文破壊時の心理的安全性を上げるため。 |
| dec_0033_003 | 2026-06-24 | エラーは保存中止、警告は確認付き保存とする。 | 未閉じコードブロックや表列数不一致は本文破壊の可能性が高い。一方、Sidecarコメント迷子は本文保存自体は可能なため、警告扱いにする。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0033_001 | 2026-06-24 | markdown_save_safety_runtime_update | 上書き保存時にMarkdown本文・表構造・Sidecarコメント参照の保存前検査や保存後RoundTrip確認がなかった。 | 上書き保存前にSave Safety検査とlocalStorageバックアップを実行し、保存後にAPIから再取得して本文一致を確認する。手動の保存検査ボタンも追加。 | Markdown編集機能が増えたことで、保存時に壊さないための安全性レイヤーが必要になったため。 |

### v0.13.7-md-raw-block-dialog-editor: Markdown通常BlockのRaw Markdownダイアログ編集
- 作業ID: studio_work_0034
- 種別: feature
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/mdViewer.html, wwwroot/js/runtime/MARKDOWN_RAW_BLOCK_DIALOG_EDITOR_NOTES_v0_13_7.md

#### 目的

Markdown Viewer / Editor上で、表セルだけでなく通常の本文Blockも、左クリックまたは右クリックメニューから小ダイアログで軽く編集できるようにする。ダイアログには見た目のテキストではなく、# / - / > / ``` などを含むRaw Markdown断片をそのまま表示し、編集者がMarkdown構造を理解した状態で更新できるようにする。

#### 背景

v0.13.2でMarkdown表セルをクリック編集できるようになり、v0.13.3〜v0.13.6でコメント・レビュー・保存安全性・fixtureまで整った。一方、通常の段落・見出し・リスト・コードブロックは、まだセル編集と同じ軽さで修正できない。Markdown本文行もセルと同じ操作感で編集できれば、ExcelにもWordにも逃げず、Markdownを構造編集できる文書として扱える。ユーザーは、見出し記号や箇条書き記号を隠す高機能エディタではなく、# や - が見えているRaw Markdown編集のほうが分かりやすいと判断した。

#### 対象範囲

Editorモード中のみ、通常Blockの左クリックでRaw Markdown編集ダイアログを開く。右クリックメニューに『行テキスト編集』または『Raw Markdown編集』を追加し、同じ小ダイアログ編集を開けるようにする。右クリックメニューには従来どおり、大きな本文テキストボックス編集へ遷移する『テキストボックス編集』相当の操作も残す。対象Blockのline_start/line_endに基づき、該当Markdown断片をそのままtextareaへ表示し、反映時は同じ範囲を置換してMarkdownを再生成・再描画する。paragraph / heading / list_item / blockquote / horizontal_rule / code_block などを段階的に対象とする。code_block は中身だけではなく、開始・終了フェンスを含むコードブロック全体を編集対象とする。

#### 対象外

WYSIWYG編集、#や-を隠すスマート編集、見出し本文だけ編集してMarkdown記号を自動維持する高機能エディタ、複数Blockをまたぐ任意範囲選択編集、表全体編集、HTMLブロックの高度な解析、Markdown ASTによる厳密な再構築は対象外。表セル編集は既存のv0.13.2を継続し、この作業では通常BlockのRaw Markdown断片編集に絞る。

#### 固定名方針

特定Markdownファイル名や特定本文内容には依存しない。Block Model上の type / line_start / line_end / block_id など、Markdown Viewer内部の構造情報を使う。Data JSON固有の固定フィールド名をRuntimeに追加しない。

#### module化方針

type="module" 化は行わず、既存のmdViewer.html単体script構成を維持する。必要な実装メモのみ wwwroot/js/runtime 配下へ追加する。

#### リスク

見た目上は1行でもMarkdown原文では複数行のBlockがある。特にcode_block、blockquote、連続list、空行境界を誤るとMarkdown構造を壊す。左クリック編集がTableCell編集やコメントバッジクリック、操作バークリックと競合する可能性がある。Viewerモードで左クリック編集を有効にすると閲覧体験と編集体験が混ざるため、Editorモード限定にする必要がある。

#### 確認観点

Editorモード中、通常段落を左クリックするとRaw Markdown断片がダイアログに表示され、反映で該当行だけ更新されること。見出しBlockでは # / ## を含む原文が表示されること。リストBlockでは - または番号を含む原文が表示されること。blockquoteでは > を含む原文が表示されること。code_blockでは ``` から ``` までの全体が表示・編集できること。表セルクリックは従来どおりTableCell編集になること。右クリックからRaw Markdown編集と従来テキストボックス編集を選び分けられること。反映後にSave Safetyでエラー検査できること。Viewerモード中は本文クリックで編集に入らないこと。

#### 作業会話サマリ


##### 依頼 / 方針

普通の行もセル編集と同じように編集できるようにしたい。左クリックではセル編集と同じ感じでダイアログ編集。右クリックメニューにはテキストボックス編集のようなメニューを作り、現状通り大きなテキストボックス編集へ遷移できるようにしたい。さらに、ダイアログに編集文字が表示された時は # や - などのMarkdown記号も見えている状態で編集したい。記号を隠す高機能編集ではなく、Raw Markdownが見えている方が分かりやすい。コードブロックはコードブロック全体を編集できるようにしないとややこしい。まずはインシデントへ追加してほしい。

##### AI整理

方針OK。スマートに # や - を隠して本文だけ編集するより、Raw Markdown断片をそのままダイアログに出す方が、Markdown構造を誤解せず安全に編集できる。特にcode_blockは中身だけではなくフェンスを含むBlock全体を編集対象にするのが自然。v0.13.7-md-raw-block-dialog-editorとして、通常Blockの左クリックRaw Markdown編集、右クリックRaw Markdown編集、従来テキストボックス編集導線の共存をインシデント登録する。

##### 追加コメント

v0.13.7-md-raw-block-dialog-editor の実装依頼。今日の最終仕上げとして、通常Blockもセル編集と同じようにRaw Markdown小ダイアログで編集できるようにしたい。# / - / > / ``` は隠さず、コードブロックはフェンス込みで全体編集する方針。


■AIコメント
今日の到達点、かなり名前つけたくなるね。

Markdown Review Studio
または
Markdown + JSON Review Layer

これは記事ネタとしても強い笑

##### AI追加回答

v0.13.7-md-raw-block-dialog-editor 対応完了。Editorモード中、表セルは従来どおりTableCell編集、通常Blockは左クリックでRaw Markdown編集ダイアログを開くように変更。右クリックメニューに Raw Markdown編集 と テキストボックス編集 を併設。Raw編集では # / - / > / ``` を隠さず、code_blockはフェンス込みのBlock全体を編集対象にした。反映時は対象Blockのline rangeだけを置換し、既存のUndoバックアップ/再描画/Save Safetyに乗せる。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0034_001 | 2026-06-24 | user | 通常Block編集方式の相談 | 既にある普通の行もセルの編集と同じように編集できるようにしたい。左クリックではセル編集と同じ感じでダイアログ編集。右クリックのメニューにテキストボックス編集みたいなメニューを作って、現状通りテキストボックス編集に遷移できるようにしたら完璧ではないか。 |
| disc_0034_002 | 2026-06-24 | assistant | 通常Block編集方式の初期方針 | Editorモード限定で、左クリックは小ダイアログ編集、右クリックは小ダイアログ編集と従来テキストボックス編集を選び分ける二段構えがよいと整理。 |
| disc_0034_003 | 2026-06-24 | user | Raw Markdown編集方針 | ダイアログでは # や - も見えている状態で編集したい。これがないとややこしい。コードブロックはコードブロック全体が編集できる感じにしないとややこしい。OKならインシデントにまず追加してほしい。 |
| disc_0034_004 | 2026-06-24 | assistant | インシデント追加結果 | v0.13.7-md-raw-block-dialog-editorとして、通常BlockのRaw Markdownダイアログ編集をインシデント追加。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0034_001 | 2026-06-24 | 通常Blockの小ダイアログ編集では、見た目テキストではなくRaw Markdown断片を表示・編集する。 | # / - / > などを隠すと、Markdown構造が分からなくなり、ユーザーにとって逆にややこしくなるため。 |
| dec_0034_002 | 2026-06-24 | code_block は中身だけではなく、開始・終了フェンスを含むコードブロック全体を編集対象にする。 | 中身だけを編集すると、フェンスや言語指定との関係が見えず、Markdown構造の破壊や誤解が起きやすいため。 |
| dec_0034_003 | 2026-06-24 | 左クリック編集はEditorモード限定にする。 | Viewerモードで本文クリック編集を有効にすると、読む操作と編集操作が混ざり、閲覧体験が不安定になるため。 |
| dec_0034_004 | 2026-06-24 | 右クリックメニューには、小ダイアログ編集と従来テキストボックス編集導線を併存させる。 | 軽い修正は小ダイアログ、大きな編集は従来テキストボックス編集という使い分けが自然なため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0034_001 | 2026-06-24 | incident_added | v0.13.6までで表セル編集・Sidecarコメント・コメントレビュー・保存安全性・fixtureは整ったが、通常本文Blockをセルと同じ軽さで編集する作業項目は未登録だった。 | studio_work_0034 v0.13.7-md-raw-block-dialog-editor として、通常BlockのRaw Markdownダイアログ編集を登録。 | Markdown表だけでなく、通常本文・見出し・リスト・コードブロックも構造を見ながら軽く編集できるようにするため。 |
| chg_0034_002 | 2026-06-24 | md_raw_block_dialog_editor_runtime_update | 通常Blockを左クリックすると従来の本文テキストボックス編集へ遷移していた。表セルのみ小ダイアログ編集に対応していた。 | Editorモード中の通常Block左クリックでRaw Markdown小ダイアログを表示。右クリックメニューにRaw Markdown編集とテキストボックス編集を併設。反映時は対象Blockの行範囲のみ置換して再描画する。 | Markdown表セルと同じ軽さで通常本文も編集でき、かつMarkdown記号を隠さず構造を理解したまま編集できるようにするため。 |

### v0.13.8-md-editor-workplace-safe: Markdown Editorの職場Edge安全化 / 実戦UX安定化
- 作業ID: studio_work_0035
- 種別: feature_fix
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/mdViewer.html

#### 目的

Markdown Editorを職場環境でも実戦投入できる編集器へ寄せる。会社Edge環境での貼り付け時に編集ダイアログが閉じる問題を防ぎ、sentence挿入・空Markdown・/code挿入・初期Editor表示など、mdViewer.htmlの編集体験を安定化する。

#### 背景

Copilot作成の計画書Markdownを仕事でメンテしようとしたところ、会社Edge環境でセル編集ダイアログへ文字列を貼り付けると画面が閉じる現象が発生した。自宅Chrome/Edgeでは再現しないため、会社PCのEdge・セキュリティ・クリップボード制御・拡張機能によるイベント順序差分が疑われる。昨日のv0.13.7でMarkdown Editorとして大きく進化したが、実戦利用には貼り付け安全性・挿入UI・空ファイル対応・デバッグ表示抑制が必要になった。

#### 対象範囲

会社Edge環境でのpaste/beforeinput/input/keydown/pointer/click系イベントをダイアログ内で安全に扱い、貼り付けでは編集ダイアログを閉じない。sentence挿入はwindow.prompt等のブラウザ標準ダイアログを廃止し、既存のRaw Markdown編集ダイアログ風UIへ統一する。フローティングメニューはヘッダーより上に行かないようtop座標下限を設ける。mdViewer.html起動直後はEditorモードを初期値にする。カレントセル/ブロックの行数やID表示は通常非表示とし、デバッグフラグ時のみ表示する。空mdファイルでも最初の行/ブロックを挿入できるようにする。Editor画面では /code から fenced code block を挿入できるようにする。

#### 対象外

テーブル挿入は今回対応しない。Markdownの本格WYSIWYG化、外部Markdownエディタ化、ASTベースの高度編集、既存コメントSidecar仕様の大改修、GitHub Pages公開用 wwwroot/data / wwwroot/defs の更新はこの作業では行わない。

#### 固定名方針

特定Markdownファイル名や特定Dataフィールド名へ依存しない。mdViewer.html内のMarkdownブロック編集UI・ダイアログ・フローティングメニュー・slash commandに関する汎用UI動作として実装する。/code はEditorコマンド契約として扱うが、任意Data構造への固定名依存は行わない。

#### module化方針

type="module" 化は行わず、既存のmdViewer.html単体script構成を維持する。必要な場合でも最小限の関数追加・既存関数差し替えに留め、v0.13.7のRaw Markdownダイアログ編集の成果を壊さない。

#### リスク

会社Edge環境固有の貼り付けイベント順序はローカル環境で完全再現できない可能性がある。blur/focusoutで閉じる設計が残ると再発しやすい。イベント伝播を止めすぎるとCtrl+Enter反映、Escapeキャンセル、保存ボタン、フローティングメニュー操作に副作用が出る。Editor初期表示化により、Viewer用途で開きたい時のURL mode指定や既存localStorage復元との優先順位にも注意が必要。

#### 確認観点

会社EdgeまたはEdge相当環境で、セル編集/Raw Markdown編集ダイアログにCtrl+V貼り付けしても閉じないこと。Ctrl+Enterで反映、Escapeまたはキャンセルで閉じること。sentence挿入がブラウザ標準promptではなくRaw Markdown編集風ダイアログで行えること。フローティングメニューがヘッダーより上へ重ならないこと。mdViewer.html起動直後がEditorモードになること。通常利用時にカレントセル/ブロックID/行数デバッグ表示が出ないこと。空mdファイルでも最初のブロックを挿入できること。Editor画面で /code から ```text のコードブロックを挿入できること。テーブル挿入は出ない、または未対応として扱われること。

#### 作業会話サマリ


##### 依頼 / 方針

添付インシデントファイルに以下のマークダウン改善インシデント方針のデータを追加。今回の改修名: v0.13.8-md-editor-workplace-safe。依頼内容: 会社Edge環境での貼り付け時に編集ダイアログが閉じないようにする。sentence挿入をブラウザ標準promptではなく既存のRaw Markdown編集ダイアログ風UIへ寄せる。フローティングメニューがヘッダーより上に行かないようにする。mdViewer.html起動直後はEditorモードを初期値にする。カレントセル/ブロックの行数デバッグ表示は通常非表示にする。空mdファイルでも行挿入できるようにする。Editor画面で /code からコードブロックを挿入できるようにする。テーブル挿入は今回対応しない。

##### AI整理

v0.13.8-md-editor-workplace-safe を新規インシデントとして追加する。今回の本質は、Markdown Editorを仕事で使える実戦編集器へ寄せることであり、会社Edgeの貼り付けイベント揺れを防御しつつ、挿入UI・空ファイル・/code・初期Editor表示などの操作感を整えること。

##### 追加コメント

v0.13.8.3-mdviewer-dialog-slash-fix を実機確認。空Markdown対応、Cancel、ESC、Raw Markdown編集ダイアログ内の / によるコードブロック挿入までOK。バグ対応などの作業履歴をインシデントファイルへ記録し、更新後JSON単体で返却してほしい。

##### AI追加回答

v0.13.8-md-editor-workplace-safe 完了。初回のpatch applicator方式では不足があり、ユーザー提供のmdViewer.htmlバックアップを基準に直接修正へ切り替えた。v0.13.8.1で起動時Editorモード、空Markdownプレースホルダー、prompt廃止、Sentence挿入ダイアログ化、Raw Markdown/TableCell/Sentence系ダイアログのCancel/Esc強化、デバッグ表示抑制、テーブル挿入非表示、フローティングメニュー軽補正を実施。v0.13.8.2で空Markdownプレースホルダーをsynthetic blockとして扱い、空ファイルでも右クリック/＋上/＋下/Raw Markdown編集が動くように修正し、/code選択系イベントを補強。v0.13.8.3でRaw Markdown編集ダイアログおよびSentence挿入ダイアログ内textareaにも / → fenced code block挿入を適用し、TableCell編集には適用しない方針で完了。ユーザー実機確認で、空md、Cancel、ESC、ダイアログエディター内 / 挿入がOKとなった。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0035_001 | 2026-06-25 | user | v0.13.8インシデント追加依頼 | 会社Edgeで貼り付け時に編集ダイアログが閉じる問題を含むMarkdown Editor改善方針を、添付インシデント管理JSONへ追加してほしい。 |
| disc_0035_002 | 2026-06-25 | assistant | v0.13.8インシデント追加結果 | v0.13.8-md-editor-workplace-safe を studio_work_0035 として追加。貼り付け安全化、prompt廃止、メニュー位置制御、Editor初期表示、デバッグ表示非表示、空Markdown対応、/code挿入、テーブル挿入対象外を作業範囲として整理した。 |
| disc_0035_20260625_workplace_safe_patch_ready | 2026-06-25 | assistant | v0.13.8-md-editor-workplace-safe 作業結果 | GitHub基準ソース運用で作業開始。mdViewer.html直接取得はツール制限により未達のため、ローカルmdViewer.htmlへ注入するpatch applicatorを作成。貼り付け安全化、ダイアログ内イベント遮断、メニュー位置補正、Editor初期表示、デバッグ表示非表示、空Markdown補助、/code挿入をまとめた。 |
| disc_0035_20260625_user_patch_result_ng | 2026-06-25 | user | v0.13.8初回patch結果の不具合報告 | 初回patch適用後、起動時はEditorモードになったが、空mdで行挿入できない、行挿入ダイアログが古いpromptのまま、行編集ダイアログのキャンセル/Escで閉じない、行挿入メニューバーがヘッダーより上に行く等の不具合を確認。対策がmdViewer.htmlで完結するなら添付バックアップファイルで対応してほしい。 |
| disc_0035_20260625_assistant_direct_fix_013801 | 2026-06-25 | assistant | v0.13.8.1 mdViewer直接修正 | patch applicator方式を取り下げ、ユーザー提供の mdViewer.html.bak_v0_13_8 を直接修正。起動時Editor維持、空mdプレースホルダー、prompt廃止、Sentence挿入ダイアログ化、Raw Markdown/TableCell/Sentence系のCancel/Esc強化、デバッグ表示非表示、/メニューCode block限定、Table挿入非表示、メニュー位置軽補正を実施。 |
| disc_0035_20260625_user_empty_slash_bug | 2026-06-25 | user | 空Markdownとslash menuの追加不具合報告 | v0.13.8.1確認でだいぶ進んだが、空ファイル読込時に行挿入用メニューが表示されない、/でCode blockのマークが選択できない問題を確認。 |
| disc_0035_20260625_assistant_empty_slash_fix_013802 | 2026-06-25 | assistant | v0.13.8.2 empty/slash fix | 空MarkdownプレースホルダーをMarkdown Block扱いのsynthetic blockに修正し、data-md-line/data-md-block-idを付与。空Markdownでも右クリックメニュー、＋上/＋下、Raw Markdown編集を可能にした。/メニューのCode blockはpointerdown/mousedown/clickと / + Enter/Tab の保険を追加。Cancel/Escも再補強。 |
| disc_0035_20260625_user_dialog_slash_bug | 2026-06-25 | user | Raw Markdown編集ダイアログ内slash不具合報告 | v0.13.8.2確認で空mdはOK、Cancel OK、Esc OK。ただしRaw Markdown編集ダイアログ内で / を入力してもコードブロックが挿入されず、/ だけが残る問題を確認。 |
| disc_0035_20260625_assistant_dialog_slash_fix_013803 | 2026-06-25 | assistant | v0.13.8.3 dialog slash fix | 原因は / → Code block挿入処理がメインの #editor 専用で、Raw Markdown編集ダイアログ内textareaには効いていなかったこと。Raw Markdown編集ダイアログとSentence挿入ダイアログ内でも、行頭の / 入力で fenced code block を即挿入するよう修正。/ + Enter/Tab の保険も追加。TableCell編集ダイアログには適用しない。 |
| disc_0035_20260625_user_done_confirm | 2026-06-25 | user | v0.13.8.3確認完了 | OK。確認できた。バグ対応などもろもろインシデントファイルに作業履歴として記録して、更新後JSON単体で返却してほしい。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0035_001 | 2026-06-25 | 貼り付け操作では編集ダイアログを閉じない設計にする。 | 会社Edge環境ではpaste時にblur/focusout/click系のイベント順序が通常環境と変わる可能性があり、貼り付けが編集完了や外側クリック扱いになると仕事利用に耐えないため。 |
| dec_0035_002 | 2026-06-25 | sentence挿入のwindow.promptを廃止し、Raw Markdown編集ダイアログ風UIへ統一する。 | ブラウザ標準ダイアログは操作感が悪く、Edgeやセキュリティ環境との相性も読みにくいため。挿入と編集のUIを統一すると操作学習コストも下がるため。 |
| dec_0035_003 | 2026-06-25 | テーブル挿入は今回対応しない。 | 今回の目的は職場利用でのMarkdown編集安定化であり、テーブル挿入まで含めるとスコープが広がりすぎるため。/codeの最小追加でまずEditorコマンドの土台を作る。 |
| dec_0035_004 | 2026-06-25 | mdViewer.html起動直後はEditorモードを初期値とする。 | Markdown Editor機能が主役になりつつあり、編集目的で開く頻度が高いため。URLパラメータ等で明示指定がある場合はそれを優先する余地を残す。 |
| dec_0035_tool_limit_001 | 2026-06-25 | mdViewer.htmlの直接置換ではなくpatch applicator方式で返却する。 | GitHub raw の mdViewer.html はHTMLとしてツール側ダウンロード制限にかかり、完全な最新HTMLを安全に取得して上書き版を生成できなかったため。ローカル既存ファイルへ注入する方式なら、ユーザー側の最新ソースに対して最小差分で適用できる。 |
| dec_0035_006 | 2026-06-25 | 初回patch applicator方式ではなく、ユーザー提供バックアップを基準に mdViewer.html 直接修正へ切り替える。 | GitHub raw HTMLの完全取得・置換に制限があり、patch方式では実機の既存構造へ十分に噛み合わなかったため。 |
| dec_0035_007 | 2026-06-25 | 空Markdownは単なるメッセージではなく、synthetic blockとして扱う。 | 空ファイル状態でも既存のブロック選択・右クリック・＋上/＋下・Raw Markdown編集の流れに乗せるため。 |
| dec_0035_008 | 2026-06-25 | Raw Markdown編集ダイアログおよびSentence挿入ダイアログ内の / 入力でも Code block を挿入する。 | ユーザーが実際に操作している編集面はメイン #editor だけではなく、Raw Markdown編集ダイアログ内textareaであり、そこで / が効かないと期待した編集体験にならないため。 |
| dec_0035_009 | 2026-06-25 | TableCell編集ダイアログには / → Code block 挿入を適用しない。 | TableCellは表セル内容の編集が目的であり、今回スコープではテーブル挿入・表構造編集を扱わないため。 |
| dec_0035_010 | 2026-06-25 | フローティングメニューのヘッダー重なりは軽補正に留め、実運用に支障がなければ深追いしない。 | 一瞬の見た目問題であり、別行をカレントにすれば回避できるため、ダイアログ・空Markdown・slash挿入など実操作の安定化を優先するため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0035_001 | 2026-06-25 | incident_added | studio_work_incident_data_v0_39_md_raw_block_dialog_editor_done.json / items_count=34 | studio_work_incident_data_v0_40_md_editor_workplace_safe_added.json / items_count=35 | 会社Edge貼り付け問題とMarkdown Editor実戦UX改善を、実装前に明示的な作業項目として管理するため。 |
| chg_0035_001 | 2026-06-25 | md_editor_workplace_safe_patch_ready | 会社Edge環境でMarkdownセル/Block編集ダイアログに貼り付けると、外側のblur/click/keydown系処理に巻き込まれ、編集ダイアログが閉じる可能性があった。sentence挿入はブラウザ標準promptに依存し、操作感がRaw Markdown編集ダイアログと揃っていなかった。 | 貼り付け・入力・クリックイベントをダイアログ内で止めるworkplace-safe guard、フローティングメニュー位置補正、Editor初期表示、デバッグ表示非表示、空Markdownプレースホルダー、/code挿入を行うpatch applicatorを追加。 | 会社Edgeなど職場環境での実戦投入時に、貼り付け操作やセキュリティ拡張によるフォーカス揺れで編集作業が壊れないようにするため。 |
| chg_0035_002 | 2026-06-25 | mdviewer_direct_fix_v0_13_8_1 | patch applicator方式では、空md挿入、prompt廃止、Cancel/Esc、メニュー位置などが実機上で十分に解決していなかった。 | ユーザー提供の mdViewer.html.bak_v0_13_8 を直接修正し、起動時Editor、空mdプレースホルダー、Sentence挿入ダイアログ化、Raw Markdown/TableCell/Sentence系ダイアログのCancel/Esc強化、デバッグ表示非表示、/メニューCode block限定、Table挿入非表示、メニュー位置軽補正を実装した。 | 職場EdgeでもMarkdown Editorを実戦投入できるよう、実際のmdViewer.html構造に直接合わせて修正する必要があったため。 |
| chg_0035_003 | 2026-06-25 | mdviewer_empty_slash_fix_v0_13_8_2 | 空Markdown表示が通常のMarkdown Block扱いになっておらず、右クリックや＋上/＋下の対象にならなかった。/メニューのCode block選択もマウス操作で拾いにくかった。 | 空Markdownプレースホルダーをsynthetic blockとして扱い、data-md-line/data-md-block-idを付与。空Markdownでも右クリックメニュー、＋上/＋下、Raw Markdown編集を可能にした。/メニューのCode block選択はpointerdown/mousedown/clickおよび / + Enter/Tab で補強した。 | 空ファイルから最初の行を作れることはMarkdown Editorとして必須であり、既存のブロック操作と同じ導線へ載せるため。 |
| chg_0035_004 | 2026-06-25 | mdviewer_dialog_slash_fix_v0_13_8_3 | Raw Markdown編集ダイアログ内のtextareaでは / 入力がメイン #editor 用のslash処理に届かず、/ だけが入力されてコードブロックへ展開されなかった。 | Raw Markdown編集ダイアログおよびSentence挿入ダイアログ内textareaでも、行頭の / 入力または / + Enter/Tab により fenced code block を挿入するようにした。TableCell編集ダイアログには適用しない。 | 実際の編集操作はRaw Markdown編集ダイアログ上で行われるため、ダイアログ内でも / → Code block の期待動作を成立させる必要があったため。 |
| chg_0035_005 | 2026-06-25 | incident_completion_update | studio_work_0035 は一部完了・要実機確認の状態で、patch_readyとして初回対応までの履歴のみ記録されていた。 | v0.13.8.1 / v0.13.8.2 / v0.13.8.3 の追加バグ対応、ユーザー確認結果、最終更新ファイル、判断ログ、変更履歴を追記し、status=完了 / verification_status=確認済みに更新した。 | バグ対応の流れをインシデントJSON上で追体験できるようにし、今回の完了状態を明確に残すため。 |

### v0.13.9-md-editor-nonblocking-ux: Markdown Editorの非ブロッキング通知 / 初期表示安全化 / Sidecarコメントダイアログ統一
- 作業ID: studio_work_0036
- 種別: feature_fix
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/mdViewer.html

#### 目的

Markdown Editorの操作感をもう一段上げる。OKを押すだけの情報ダイアログを非ブロッキングなタイマー式メッセージラベルへ置き換え、初期表示では勝手にファイルを読まず、Sidecarコメント入力も既存の新しいダイアログUIへ統一する。

#### 背景

v0.13.8でMarkdown Editorは実戦投入できる段階まで進んだが、まだブラウザ標準のalert/prompt系UIが残っている。特に『管理対象にしました』のようなOK確認だけの情報ダイアログは、編集の流れを止めて操作感を落とす。また、起動直後にファイルコンボの先頭ファイルが自動ロードされると、他者に画面を見せた時に意図しないMarkdown本文が表示されて驚かせる可能性がある。さらに、行挿入時のSidecarコメント入力が古いブラウザ標準ダイアログのまま残っているため、v0.13.8で整えたRaw Markdown編集風ダイアログ体験とズレている。

#### 対象範囲

mdViewer.html内のOKを押すだけの情報表示は、原則としてタイマー式のメッセージラベルまたはtoast表示へ変更する。成功/情報/警告/エラーの種別を持ち、一定時間後に自動で消える。保存完了、管理対象コピー完了、URL読込完了など、ユーザーの判断を必要としない通知を対象とする。ユーザー判断が必要なconfirm系、危険操作、入力が必要なケースは対象外とし、必要に応じて専用ダイアログ化する。Markdown Editor初期表示では、ファイルコンボの先頭ファイルを自動プレロードしない。URLパラメータ file/md 等で明示指定された場合、またはユーザーがファイルを選択してURL読込/読込ボタンを押した場合のみ読み込む。Sidecarコメント入力はwindow.prompt等の古いブラウザ標準ダイアログを廃止し、既存のRaw Markdown編集/挿入ダイアログ風UIへ統一する。キャンセル、ESC、貼り付け、Enter/Ctrl+Enterの扱いも既存ダイアログの作法に合わせる。

#### 対象外

Markdown本文編集の本格WYSIWYG化、Sidecarコメント構造そのものの大改修、コメント一覧管理UIの新設、URLパラメータによる明示ロードの廃止、危険操作confirmの全面廃止、GitHub Pages公開用 wwwroot/data / wwwroot/defs の更新は今回対象外とする。

#### 固定名方針

特定Markdownファイル名や特定Dataフィールド名へ依存しない。通知表示、初期ロード制御、Sidecarコメント入力はmdViewer.html内の汎用UI動作として扱う。通知文言は固定メッセージを最小限にし、処理側からmessage/type/durationを渡せる形に寄せる。

#### module化方針

type="module" 化は行わず、既存のmdViewer.html単体script構成を維持する。v0.13.8で修正したRaw Markdown編集ダイアログ、空Markdown対応、/code挿入、Cancel/ESC挙動を壊さないように最小差分で対応する。

#### リスク

alert/promptを一括置換すると、ユーザー判断が必要なconfirmや入力必須の処理まで非ブロッキング化してしまうリスクがある。通知が短すぎると重要な情報を見落とす可能性があり、長すぎると画面を邪魔する。初期プレロード停止により、従来の『起動したら先頭ファイルが見える』操作に慣れていた場合は一手増える。Sidecarコメントの新ダイアログ化では、既存コメント挿入位置、空文字キャンセル、ESC、貼り付け、フォーカス復帰に注意が必要。

#### 確認観点

管理対象コピー完了や保存完了などのOKだけ情報表示が、ブラウザ標準alertではなく画面上のメッセージラベル/toastとして表示され、一定時間後に消えること。危険操作やユーザー判断が必要なconfirmは不用意に消えていないこと。mdViewer.html初期表示時に、ファイルコンボの先頭ファイルが自動ロードされず、本文欄は空/案内表示になること。URLパラメータ file/md 指定時は従来どおり明示ロードされること。ユーザーがファイル選択後にURL読込または読込操作をした場合は正常に表示されること。行挿入時のSidecarコメント入力がブラウザ標準promptではなく、新しいStudio風ダイアログで表示されること。Sidecarコメントダイアログでキャンセル/ESC/貼り付けが安定して動くこと。v0.13.8で確認済みの空Markdown、Cancel、ESC、Raw Markdown編集ダイアログ内 / code block 挿入が回帰しないこと。

#### 作業会話サマリ


##### 依頼 / 方針

Markdown Editorで『管理対象にしました』のようなOKを押すだけのインフォメーションダイアログは操作性と操作感を落とすため、タイマー仕掛けのメッセージラベルに変更したい。初期表示時にファイルコンボの先頭ファイルがプレロードされる仕様は、他の人が見たら驚く可能性があるので、何も表示しないように変更したい。行挿入時のSidecarコメントのダイアログが古いブラウザ標準ダイアログのままなので、新しいダイアログへ変更したい。できそうならインシデントに追加し、更新後JSON単体で返却してほしい。

##### AI整理

対応可能。今回の本質は『作業を止めるUIを減らす』こと。OKだけの情報表示はtoast/メッセージラベルへ移し、判断が必要なconfirmや入力が必要な処理は専用ダイアログへ寄せる。初期表示は安全側に倒して、明示URLまたはユーザー操作がない限りMarkdownを読み込まない。Sidecarコメント入力はv0.13.8で整えたダイアログ作法へ統一する。

##### 追加コメント

incident_file=data/json/01_main/studio_work_incident_data_v0_43_md_editor_nonblocking_ux_added.json / phase=v0.13.9-md-editor-nonblocking-ux として、最新 mdViewer.html を添付し、Markdown Editorの非ブロッキング通知化・初期プレロード停止・Sidecarコメント入力ダイアログ統一の実装を依頼。

##### AI追加回答

v0.13.9-md-editor-nonblocking-ux を実装。OKだけの情報ダイアログをtoast/タイマー式メッセージへ寄せ、管理Markdown一覧取得後に先頭ファイルを自動プレロードしないよう変更。URLパラメータ file/md 指定時だけ明示ロードする。Sidecarコメント追加・編集はブラウザ標準promptではなくStudio風ダイアログへ統一し、キャンセル/ESC/貼り付けが既存ダイアログ作法で動くようにした。危険操作confirmとコピー失敗時の手動コピーpromptは安全上残した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0036_001 | 2026-06-25 | user | Markdown Editor UX追加改善相談 | OKを押すだけの情報ダイアログは操作性と操作感を落とすため、タイマー式メッセージラベルへ変更したい。初期表示時の先頭ファイル自動プレロードを止めたい。Sidecarコメント入力ダイアログが古いままなので新しいダイアログへ変更したい。 |
| disc_0036_002 | 2026-06-25 | assistant | インシデント追加方針 | 対応可能。非ブロッキング通知、初期表示安全化、Sidecarコメント入力ダイアログ統一を1件のMarkdown Editor UX仕上げインシデントとして登録する。 |
| disc_0036_005 | 2026-06-25 | user | v0.13.9-md-editor-nonblocking-ux作業依頼 | incident_file と phase を指定し、最新 mdViewer.html を添付して、非ブロッキング通知化・初期プレロード停止・Sidecarコメント入力ダイアログ統一の実装を依頼。 |
| disc_0036_006 | 2026-06-25 | assistant | v0.13.9-md-editor-nonblocking-ux実装結果 | mdViewer.html単体で対応。toast通知基盤を追加し、OKだけの情報alertをsuccess/info/warn/error toastへ置換。refreshManagedMarkdownListと初期ロード処理を変更し、起動直後は先頭ファイルを自動ロードしないようにした。Sidecarコメント追加・編集用のStudio風ダイアログを追加し、add/editのpromptを廃止。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0036_001 | 2026-06-25 | OKだけの情報ダイアログは、非ブロッキングなtoast/メッセージラベルへ置き換える。 | ユーザー判断を必要としない通知で操作を止めると、Markdown編集のリズムと操作感が悪化するため。 |
| dec_0036_002 | 2026-06-25 | 起動直後はファイルコンボの先頭ファイルを自動ロードしない。 | 他者に画面を見せた時に意図しないMarkdown本文が表示されると驚かせる可能性があり、初期状態は安全で空のワークスペースにする方がよいため。 |
| dec_0036_003 | 2026-06-25 | Sidecarコメント入力はブラウザ標準promptではなく、Studio風の専用ダイアログへ統一する。 | v0.13.8でRaw Markdown編集・Sentence挿入を専用ダイアログへ寄せたため、Sidecarコメントだけ古いpromptが残ると操作感が分断されるため。 |
| dec_0036_004 | 2026-06-25 | ユーザー判断が必要なconfirm系は、今回のtoast化対象に含めない。 | 非ブロッキング化してはいけない確認まで消すと、破壊的操作や意図しない更新の安全柵が弱くなるため。 |
| dec_0036_005 | 2026-06-25 | Sidecarコメント追加・編集は、ブラウザ標準promptではなくStudio風ダイアログへ統一する。 | v0.13.8で整えたRaw Markdown編集/挿入ダイアログの操作感と合わせ、キャンセル・ESC・貼り付けの挙動を安定させるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0036_001 | 2026-06-25 | incident_added | studio_work_incident_data_v0_42_md_editor_workplace_safe_done.json / items_count=35 | studio_work_incident_data_v0_43_md_editor_nonblocking_ux_added.json / items_count=36 | v0.13.8完了後に見えたMarkdown Editorの次段階UX改善として、非ブロッキング通知、初期表示安全化、Sidecarコメントダイアログ統一を作業項目化するため。 |
| chg_0036_002 | 2026-06-25 | nonblocking_toast_runtime | 保存完了、管理対象コピー完了、Sidecar JSON保存完了、コピー完了など、一部のOKだけ情報表示がalertで表示され、ユーザーがOKを押すまで操作が止まっていた。 | showMarkdownToast / showMarkdownSuccess / showMarkdownWarn / showMarkdownError を追加し、OKだけの情報表示を一定時間で消えるtoastへ置換。 | Markdown Editorの操作テンポを止めず、情報は見せるが作業をブロックしない操作感にするため。 |
| chg_0036_003 | 2026-06-25 | initial_preload_disabled | mdViewer.html初期ロード時に、data/markdown一覧の先頭ファイルが自動ロードされる仕様だった。 | refreshManagedMarkdownListは空選択を先頭に置き、初期ロードではURLパラメータ file/md がある場合だけloadManagedMarkdownを実行する。明示指定がなければ案内表示/空Markdown状態で開始する。 | 他者が初めて開いた時に意図しないMarkdown本文が表示されることを防ぐため。 |
| chg_0036_004 | 2026-06-25 | sidecar_comment_dialog_unified | Sidecarコメント追加・編集でwindow.promptが残っていた。 | mdSidecarCommentEditorを追加し、Sidecarコメント追加・編集をStudio風ダイアログに統一。wireMarkdownDialogPanelに乗せ、キャンセル/ESC/Ctrl+Enter/貼り付け停止を既存ダイアログ作法へ揃えた。 | Markdown Editor内の編集体験を統一し、ブラウザ標準ダイアログによる操作感の断絶をなくすため。 |

### v0.13.10-main-json-select-reset-toast-ux: Main画面のJSON選択時ViewDef再解決 / 非ブロッキング通知化
- 作業ID: studio_work_0037
- 種別: feature_fix
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/index.html, wwwroot/app.js, wwwroot/styles.css, wwwroot/js/core/file_api.js, wwwroot/js/core/viewdef_resolver.js, wwwroot/js/runtime/load_runtime.js, wwwroot/js/ui/file_tree_picker.js, wwwroot/js/ui/page_setup.js

#### 目的

JSON Object Studio本体画面で、対象JSONを選択した時に古いViewDef選択状態を引きずらず、選択されたData JSON内のview_def定義からViewDefを再解決して読み直す。あわせて、Main画面のOKだけ情報メッセージを、Markdown Editor側と同じ非ブロッキングなタイマー式メッセージへ寄せる。

#### 背景

現状では、ユーザーが毎回ブックマークバーからStudioくんを開き直し、初期化再表示してから対象JSONを選び直している。これは、前回選択していたViewDef JSON欄が残ったまま別Data JSONを読み込むと、DataとViewDefのアンマッチが起きてエラーになるためである。JSONデータを選択する行為は『新しいDataを読み込みたい』という明確な意思表示なので、既存ViewDef選択を保持するより、Data側のview_defを正として再解決する方が自然。またMain画面にも、画面上部などに古いメッセージが表示されたまま残り、『いつのメッセージ？』となる操作感の悪さがあるため、v0.13.9のMarkdown Editorと同様に非ブロッキング通知へ寄せたい。

#### 対象範囲

対象JSON選択時または読込時に、ViewDef JSON欄を一度クリアし、選択されたData JSONを読み込んだ後、そのData内のview_def値からViewDefを再解決してViewDef欄へ再表示し、読み込み直す。URLパラメータや明示的にViewDef指定がある場合は、既存の明示指定を優先する。ただし通常のコンボ操作では、前回ViewDef選択を暗黙に引きずらない。Data内にview_defが存在しない場合は、ViewDef欄を空にし、分かりやすい非ブロッキング通知で知らせる。Main画面の成功/情報/軽微な警告メッセージは、Markdown Editor側と同じ方針でtoastまたはタイマー式メッセージラベルへ変更する。一定時間後に自動で消え、次の操作を妨げないようにする。

#### 対象外

Data JSON内のview_def命名規約そのものの変更、ViewDef探索パスの大規模再設計、既存ViewDefファイル名の一括修正、危険操作や未保存破棄のconfirm全面廃止、Markdown Editor側の追加改修、GitHub Pages公開用 wwwroot/data / wwwroot/defs の更新は今回対象外とする。

#### 固定名方針

view_def はData JSONからViewDefを辿るStudio標準メタ情報として扱う。ただしRuntimeが個別Dataの業務フィールド名へ依存してはいけない。通知基盤のDOM IDやtoast関数名はUI骨格として許容するが、特定Data名やViewDef名を固定しない。

#### module化方針

type="module" 化は行わない。既存の従来script方式と現在の分割JS構成を前提に、対象JSON選択・読込処理・ViewDef再解決処理・通知表示処理を安全に拡張する。

#### リスク

既存のURL起動、Drop読込、手動ViewDef指定、GitHub Pages静的読込、サブフォルダー相対パス、Data内view_defがファイル名のみの場合の解決、未保存データの扱いと競合するリスクがある。ViewDef欄を無条件クリアしすぎると、明示ViewDef指定で開きたいケースを壊す可能性があるため、ユーザー操作の種別と優先順位を丁寧に分ける必要がある。

#### 確認観点

対象JSONコンボで別Data JSONを選択した時、前回のViewDef選択が残らず、一度ViewDef欄がクリアされること。Data JSON内のview_def値からViewDefが再解決され、ViewDef欄に再表示されること。前回Dataと前回ViewDefのアンマッチによるエラーが発生しないこと。URLパラメータでData/ViewDefを明示指定した場合は従来どおり指定ViewDefが優先されること。Data内にview_defがない場合は画面が壊れず、非ブロッキング通知で理由が分かること。Main画面の保存完了/読込完了/軽微な情報通知がOKダイアログや常駐メッセージではなく、一定時間後に消えるtoast/メッセージラベルになること。危険操作や未保存破棄のconfirmが不用意に消えていないこと。

#### 作業会話サマリ


##### 依頼 / 方針

JSONデータを選択するとき、毎回ブックマークバーでStudioくんを選択して初期化再表示してからデータを選択している。そうしないと定義とのアンマッチでエラーになる。JSONデータを選択するということは新しいデータを読み込みたい意思表示なので、ViewDefJSON欄は一度クリアしてから、データJSONに定義されているViewDefファイル名を再表示して読み込み直してほしい。それと、Studioくんのメイン画面もMarkdown Editor側と同様にタイマー仕掛けのメッセージに変更し、画面トップに『いつのメッセージ？』のようなメッセージが残ることを防ぎたい。

##### AI整理

対応可能。これは小さく見えるが利用頻度が非常に高いMain画面の操作感改善であり、Data選択を『新しいData読込の明示意思』として扱うのが自然。対象JSON選択時には古いViewDef選択を引きずらず、Data内view_defを正として再解決する。Main画面通知もMarkdown Editorで導入した非ブロッキングtoast方針へ統一する。

##### 追加コメント

対象JSON選択時にData内view_defが特定され存在する場合、ViewDef欄のツリー選択ダイアログが表示されると「さらに選べということか」と感じる。自動特定済みの場合はViewDef選択ダイアログを表示しないようにしてほしい。

##### AI追加回答

v0.13.10.1-main-json-select-autofill-silent 対応完了。対象JSON選択後にData内view_defをViewDef欄へ自動反映する際、defNameInputへinputイベントを発火しない静かな値設定へ変更した。これにより、ViewDefが特定済みの場合にファイルツリーピッカーが開いて「選択待ち」のように見える問題を抑止する。あわせて、既存ViewDefクリア時もinputイベントを発火しないようにし、表示中のfile-tree-pickerを即時/遅延で閉じる補助処理を追加。index.html の app.js cache buster を更新。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0037_001 | 2026-06-25 | user | Main画面のData/ViewDefアンマッチ解消依頼 | JSONデータを選択するとき、毎回Studioくんを初期化再表示してからデータを選んでいる。そうしないと定義とのアンマッチでエラーになる。JSONデータ選択時はViewDefJSON欄を一度クリアし、Data JSON内のview_defを再表示して読み込み直してほしい。 |
| disc_0037_002 | 2026-06-25 | user | Main画面通知の非ブロッキング化依頼 | Studioくんのメイン画面もMarkdown Editor側と同様に、タイマー仕掛けのメッセージに変更してほしい。画面トップにいつのメッセージか分からない表示が残ることを防ぎたい。 |
| disc_0037_003 | 2026-06-25 | assistant | インシデント登録方針 | 対象JSON選択は新しいData読込の意思表示として扱い、前回ViewDefを暗黙に保持しない方針で登録する。Main画面通知はv0.13.9 Markdown Editorの非ブロッキングtoast方針を本体画面にも展開する。 |
| disc_0037_003 | 2026-06-25 | user | ViewDef自動反映時の選択ツリー表示違和感 | 対象JSONを選択し、Data内view_defからViewDefが特定されている場合に、ViewDef選択ダイアログが表示されると、ユーザーには「さらに選べ」という意味に見えてしまう。特定済みの場合はViewDef選択ダイアログを表示しないようにしたい。 |
| disc_0037_004 | 2026-06-25 | assistant | v0.13.10.1対応結果 | Data内view_defをViewDef欄へ自動反映する処理で、defNameInputへinputイベントを発火しないように変更。file_tree_picker.jsはinputイベントでツリーを表示するため、自動反映時は静かに値だけ入れ、表示中のツリーを閉じる補助処理を追加した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0037_001 | 2026-06-25 | 通常の対象JSON選択では、既存ViewDef選択を一度クリアし、Data内view_defからViewDefを再解決する。 | 対象JSONを選ぶ行為は新しいDataを開く意思表示であり、前回ViewDefを暗黙に引きずるとData/ViewDefアンマッチが発生して作業開始前の心理的負荷が高くなるため。 |
| dec_0037_002 | 2026-06-25 | URLパラメータや明示ViewDef指定がある場合は、その明示指定を優先する。 | 記事リンクや検証リンクではDataとViewDefを明示的に組み合わせたいケースがあるため、通常コンボ操作と明示起動契約を分ける必要がある。 |
| dec_0037_003 | 2026-06-25 | Main画面の成功/情報通知はタイマー式toastへ移行し、危険操作confirmは残す。 | OKを押すだけの通知や常駐メッセージは作業の流れを止めるが、削除・未保存破棄など人間判断が必要な操作まで非ブロッキング化すると事故につながるため。 |
| dec_0037_004 | 2026-06-25 | 危険操作や管理対象コピー確認など、人間判断が必要なconfirmは今回toast化しない。 | 削除・未保存破棄・管理対象コピーなどは自動で消える通知にすると事故につながるため。 |
| dec_0037_004 | 2026-06-25 | Data内view_defからViewDefが自動特定できた場合、ViewDef選択ツリーは表示しない。 | 自動特定済みの状態で選択UIが開くと、ユーザーには追加選択を求められているように見え、操作の確信を下げるため。 |
| dec_0037_005 | 2026-06-25 | プログラムによるViewDef欄更新ではinputイベントを発火しない。 | file_tree_picker.jsはinputイベントで候補ツリーを表示するため、自動補完時にinputイベントを発火すると不要な選択UIが出てしまう。人間の手入力・クリック選択とはイベント発火を分ける。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0037_001 | 2026-06-25 | incident_added | Main画面では、対象JSONを切り替えても前回ViewDef選択が残り、Data/ViewDefアンマッチ時にエラーが発生する運用上の違和感が作業項目化されていなかった。またMain画面通知の非ブロッキング化も未登録だった。 | studio_work_0037 / v0.13.10-main-json-select-reset-toast-ux として、対象JSON選択時のViewDef再解決とMain画面toast通知化を登録。 | 毎回ブックマークから初期化再表示してからDataを選ぶ運用を不要にし、利用頻度の高いMain画面の操作感を改善するため。 |
| chg_0037_002 | 2026-06-25 | data_selection_viewdef_reset | 対象JSONを変更してもViewDef欄に前回の選択が残り、読込時に明示ViewDefとして優先されてData/ViewDefアンマッチエラーになることがあった。 | 対象JSON input/change時にViewDef欄とDrop済みViewDefを即時クリアし、選択Data JSONを事前取得してData内 view_def をViewDef欄へ再表示するフックを追加した。Data内 view_def がない場合は、読込時に互換ViewDefを自動探索する旨をtoastで通知する。 | 対象JSON選択を新しいData読込の意思表示として扱い、ブックマーク再起動で初期化する運用を不要にするため。 |
| chg_0037_003 | 2026-06-25 | incident_completion_update | studio_work_0037 は未着手で、actual_updated_files と作業結果履歴が未記録だった。 | statusを完了、verification_statusを要実機確認へ更新し、actual_updated_files / latest_ai_response / discussion_history / decision_log / change_history に実装内容を記録した。index.html の app.js cache buster 更新も実績ファイルに含めた。 | Foundation Rule 19 および v0.12 のAI更新ファイル記録ルールに従い、作業結果をインシデントJSONへ残すため。 |
| chg_0037_004 | 2026-06-25 | app_js_cache_buster_update | index.html の app.js script URL は app.js?v=json-object-studio-009 のままで、ブラウザキャッシュにより更新後app.jsが読み込まれない可能性があった。 | index.html の app.js script URL を app.js?v=main-json-select-reset-toast-01310 へ更新した。 | ローカル上書き後にブラウザが旧app.jsを使い続ける事故を避けるため。 |
| chg_0037_003 | 2026-06-25 | viewdef_autofill_picker_suppression | 対象JSON選択後にData内view_defをdefNameInputへ反映する際、inputイベントをdispatchしていたため、ViewDefファイルツリーピッカーが開き、自動特定済みなのに選択を促しているように見えていた。 | defNameInputへ値を入れる処理を静かな設定に変更し、inputイベントを発火しないようにした。あわせて、表示中のfile-tree-pickerを閉じる補助処理を追加した。 | Data選択時のViewDef再解決を、人間に余計な選択を求めない自然な自動補完として成立させるため。 |
| chg_0037_004 | 2026-06-25 | cache_buster_update | index.html は app.js?v=main-json-select-reset-toast-01310 を読み込んでいた。 | index.html は app.js?v=main-json-select-reset-toast-01310-1 を読み込む。 | ブラウザキャッシュにより修正前 app.js が残ることを避けるため。 |

### v0.13.10-index-studio-tool-dock-layout: index.html Studioツールドック導線 / Viewer・Outputメニュー整列
- 作業ID: studio_work_0038
- 優先度: medium
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/index.html, wwwroot/styles.css

#### 目的

JSON Object Studio本体画面のヘッダーに、Markdown Viewer / DiffJson Viewer / MetaDiff Hypothesis Viewer への導線をStudioツール群として追加し、既存のMarkdown出力ボタン群も含めて、横幅に応じて自然に整列・折り返しできるメニュー配置へ調整する。

#### 背景

Studioくん第4話『差分を語り始める』の文脈で、Studio本体からDiffJsonViewer.htmlとMetaDiff_HypothesisViewer.htmlへ移動できる導線が必要になった。実体としては別HTMLだが、同じwwwroot配下のStudioファミリーとしてヘッダーから呼び出せるようにすることで、JSON編集・Markdown閲覧・差分確認・AI差分仮説確認が一つの作業場に並ぶ。初期案ではツールドックが右端で隠れたり、Outputブロックだけ下段に残って空白感が出たりしたため、通常幅・広幅の両方で見た目が破綻しない配置へ段階的に調整した。

#### 対象範囲

index.htmlのStudio関連ツール導線を整理する。Viewerグループには mdViewer.html / DiffJsonViewer.html / MetaDiff_HypothesisViewer.html へのリンクを配置する。Outputグループには既存の exportMarkdownBtn / exportViewDefMarkdownBtn を残し、JS連動用IDを維持したまま二段表示の短いボタンへ変更する。styles.css側ではヘッダーのレスポンシブ配置、広幅時の横流れ、通常幅時の折り返し、ツールドックの縦位置中央揃えを調整する。

#### 対象外

DiffJsonViewer.html / MetaDiff_HypothesisViewer.html 本体の機能改修、Markdown出力処理の内部仕様変更、app.jsの出力処理変更、正式なアプリRevision引き上げ、Viewer群の完全統合、URLパラメータ連携強化は今回対象外とする。

#### 固定名方針

exportMarkdownBtn / exportViewDefMarkdownBtn は既存JSとの接続点としてDOM骨格固定名のため維持する。mdViewer.html / DiffJsonViewer.html / MetaDiff_HypothesisViewer.html は同一wwwroot配下のStudio標準ツールファイル名としてリンク対象にする。Runtimeが個別Dataフィールド名へ依存する変更は行わない。

#### module化方針

type="module" 化は行わない。既存の従来script方式と現在の分割JS構成を維持し、HTML/CSS中心のメニュー導線・レイアウト調整に限定する。

#### リスク

ヘッダー内要素が増えたことで通常Window幅で右端が隠れる、Outputブロックだけ下段に残って空白感が出る、既存Markdown出力ボタンのID変更によりapp.js側のイベントが切れる、ブックマークバー表示時の実用幅で折り返しが不自然になるリスクがある。

#### 確認観点

通常利用しているブラウザWindow幅でメニュー右端が隠れないこと。広いWindow幅ではViewerとOutputが右側へ横並びで流れ、縦位置中央揃えになること。通常幅ではOutputブロックが下段に逃げても不自然な空白が出ないこと。Markdown Viewer / DiffJsonViewer / MetaDiff Hypothesis Viewer のリンクが開けること。exportMarkdownBtn / exportViewDefMarkdownBtn のIDが維持され、既存のMarkdown出力処理が壊れていないこと。

#### 作業会話サマリ


##### 依頼 / 方針

index.htmlのメニュー調整作業履歴としてインシデントに残しておきたい。StudioくんからMetaDiff_HypothesisViewer.htmlとDiffJsonViewer.htmlへリンク追加し、既存のMarkdown出力→Viewer / ViewDef Markdown→Viewerボタンも横長でデザイン的に気になるため、Viewer / Output のボタン配置をいい感じに調整したい。

##### AI整理

Studioくん本体にDiff機能を直接統合するのではなく、同じwwwroot配下のDiffJsonViewer.htmlとMetaDiff_HypothesisViewer.htmlをStudioツールとして呼び出せるようにする方針で対応。既存のMarkdown出力ボタンIDは維持しながら短い二段ボタンへ変更し、Viewer群とOutput群をツールドック化した。通常幅・広幅のスクリーンショット確認に基づき、Viewerは上段右側、Outputは幅に応じて右側へ流れる/下段へ逃げるレスポンシブ配置へ調整した。

##### 追加コメント

完全たるStudioという感じで、ラインナップ勢ぞろい。今日は満足。いい一日の終わりになった。なお、このメニュー調整はリビジョンを上げてもよいぐらいだが、今日は作業履歴としてインシデントに残す。

##### AI追加回答

この日、StudioくんはただのJSON編集画面ではなくなった。JSON、Markdown、Diff、AI仮説の道具が一つの作業場に並び、ようやくStudioという名前に追いついた。作業履歴として、index.html / styles.css のヘッダーツールドック調整をインシデントへ追加する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0038_001 | 2026-06-25 | user | Studioくん差分Viewer導線追加相談 | Studioくんの中に差分を見る機能はまだないが、MetaDiff_HypothesisViewer.html を wwwroot の中に入れて、Studioくんからリンク追加すればStudioくんの中にあることにできるのではないか。 |
| disc_0038_002 | 2026-06-25 | assistant | Studioツール化方針 | 本体へDiff機能を直接実装したとは言わず、Studioくんが差分を読むためのViewerを呼び出せるようになった、と扱う方針を提案。wwwroot配下に置いてリンクすればStudioくんファミリーとして自然に扱える。 |
| disc_0038_003 | 2026-06-25 | user | DiffJsonViewer導線追加 | DiffJsonViewer.html もある。DiffJsonViewerは差分の事実を見るViewer、MetaDiff Hypothesis Viewerは差分の意味を見るViewerとして扱える。 |
| disc_0038_004 | 2026-06-25 | assistant | 差分Viewer二層構造整理 | DiffJsonViewer.html は差分の事実、MetaDiff_HypothesisViewer.html は差分の意味を見る二段構えとして整理。Studioくんはその二つをつなぐ作業場になったと説明できる。 |
| disc_0038_005 | 2026-06-25 | user | index.htmlメニュー調整依頼 | index.htmlにリンクを追加し、Markdown出力→ViewerとViewDef Markdown→Viewerの横長ボタンも含めてデザイン修正してほしい。 |
| disc_0038_006 | 2026-06-25 | assistant | 初回ツールドック対応結果 | DiffJsonViewer.html / MetaDiff_HypothesisViewer.html へのリンクを追加し、既存Markdown出力ボタンを短い二段ボタン化。Output / Viewer のツール群に分けた。 |
| disc_0038_007 | 2026-06-25 | user | 通常Window幅で右端が隠れる | 普段使うWindow幅では右側のメニューが隠れるため、左へ寄せてうまく調整してほしい。 |
| disc_0038_008 | 2026-06-25 | assistant | レスポンシブ調整結果 | ヘッダー左のブランド領域を少しコンパクト化し、読込系ブロックを左寄せ＋折り返し可能に変更。狭い時はOutput/Viewerブロックを次行へ逃がし、右端のはみ出しを回避した。 |
| disc_0038_009 | 2026-06-25 | user | Viewer右側配置案 | Viewer群を入力行の右側へ上げて、Output群だけ下段左に逃がす案に寄せたい。右側の空き感もなんとかしたい。 |
| disc_0038_010 | 2026-06-25 | assistant | Viewer上段・Output下段配置結果 | Markdown / DiffJSON / MetaDiff のViewer群を上段右側へ配置し、MD出力 / ViewDef出力 のOutput群は下段左へ逃がす形に調整。右側の大きな空白感を軽減した。 |
| disc_0038_011 | 2026-06-25 | user | 広幅時の横流れ要望 | 横に広い時はOutputブロックも右に流れてほしい。その時は縦位置中央揃えでメニュー達が並んでほしい。 |
| disc_0038_012 | 2026-06-25 | assistant | 広幅横流れ対応結果 | 横幅が広い時はViewerの右にOutputが並び、通常幅ではOutputが下段へ逃げるレスポンシブ配置へ調整。メニュー群は縦位置中央揃えにした。 |
| disc_0038_013 | 2026-06-25 | user | 完成確認 | 完璧。かっこいい。完全たるStudioという感じで、ラインナップ勢ぞろい。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0038_001 | 2026-06-25 | DiffJsonViewer.html と MetaDiff_HypothesisViewer.html はStudio本体へ直接統合せず、同じwwwroot配下のViewerツールとしてindex.htmlからリンクする。 | 本体機能として無理に統合するより、既存ViewerをStudio作業場の道具として並べる方が現時点の実装量が少なく、Studioくん第4話の『差分を見る道具と語る道具を手に入れた』という物語にも合うため。 |
| dec_0038_002 | 2026-06-25 | ヘッダーツールは Viewer と Output の2グループに分ける。 | Markdown Viewer / DiffJSON / MetaDiff は見る道具、Markdown出力 / ViewDef出力 は出す道具であり、役割を分けた方がStudio作業場として理解しやすいため。 |
| dec_0038_003 | 2026-06-25 | exportMarkdownBtn / exportViewDefMarkdownBtn のIDは変更しない。 | app.js側の既存イベント接続を壊さず、UI表現だけを二段短縮ボタンへ変更するため。 |
| dec_0038_004 | 2026-06-25 | 通常Window幅では右端が隠れないことを優先し、Output群は必要に応じて下段へ逃がす。 | 実運用ではブックマークバー等で横幅が狭くなるため、広幅の見た目より、普段使う幅で全メニューが見えることを優先する必要があるため。 |
| dec_0038_005 | 2026-06-25 | 横幅が広い場合はOutput群もViewer群の右側へ流し、メニュー群は縦位置中央揃えにする。 | 広幅時に下段左だけにOutputが残ると空白感が出るため、利用可能な横幅がある場合はツールドック全体を上段へ横流しした方がStudio感が出るため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0038_001 | 2026-06-25 | header_tool_links | index.htmlヘッダーにはMarkdown出力→Viewer、ViewDef Markdown→Viewer、Markdown Viewerへの導線のみがあり、DiffJsonViewer.html / MetaDiff_HypothesisViewer.html へのリンクは存在しなかった。 | Viewerグループに Markdown Viewer / DiffJSON / MetaDiff のリンクを追加し、Studioくんから差分の事実とAI差分仮説のViewerへ移動できるようにした。 | Studioくん第4話『差分を語り始める』の文脈で、差分を見る道具と差分の意味を見る道具をStudio本体から呼べる導線が必要になったため。 |
| chg_0038_002 | 2026-06-25 | button_design | Markdown出力→Viewer / ViewDef Markdown→Viewer のボタンが横長で、ヘッダー内でデザイン的に重く見えていた。 | MD / ViewDef を主ラベル、出力→Viewer をサブラベルとする短い二段ボタンへ変更し、Outputグループへ整理した。 | ヘッダー内の横幅消費を抑え、Viewer導線と並べてもStudioツール群として見やすくするため。 |
| chg_0038_003 | 2026-06-25 | responsive_layout | ツールドック追加直後は、通常Window幅で右端が隠れたり、Outputブロックが下段左に残って右側が大きく空く状態があった。 | 通常幅では右端が隠れないように折り返し、広幅ではViewerの右にOutputが流れて横並びになるレスポンシブ配置へ調整した。メニュー群は縦位置中央揃えにした。 | 普段使うブラウザ幅と広幅スクリーンの両方で、Studioツール群が自然に見えるようにするため。 |

### v0.14.0-decision-log-confirmation-governance: 判断ログ系項目見直し / AI確認種別明示 / 最新ソース確認ルール追加
- 作業ID: studio_work_0039
- 種別: rules_review
- 分類: decision_log_governance
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み

#### 対象ファイル

data/json/00_rules/frb_coding_constraints_review_data_v0_3.json
data/json/00_rules/frb_viewdef_generation_rules_review_data_v0_1.json
data/json/00_rules/frb_studio_foundation_review_data_v0_1_github_fetch_urls_added.json
data/json/00_rules/_json_creation_prompt.md
defs/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json
data/json/01_main/studio_work_incident_data_v0_49_decision_log_confirmation_governance_added.json

#### 目的

AI駆動開発における判断ログを、単なる作業説明ではなく、期待値・例外条件・受入条件・テストパターン生成の種として扱えるようにする。あわせて、AIが作業報告で『確認した』と言う場合の確認種別を明示し、最新ソース未確認による古いソース前提の修正事故を防ぐ。

#### 背景

このチャットで、思考ログ・判断ログ・文脈・判断軸の役割分担を整理した結果、インシデント管理に残す判断ログの粒度が不足していることが明確になった。特に、判断内容と理由だけでは、後続AIが例外条件・期待値・受入条件・テスト生成観点を再現しにくい。また、AI側の確認には静的確認・JSON parse・ビルド確認・ローカル起動確認・スクショ確認・Playwright確認・推定確認など複数種類があり、これらを混同すると『確認しました』の意味が曖昧になる。さらに、直前の別チャットで扱った最新ソースは、現在チャットの実ファイルとして自動的に存在するわけではなく、文脈記憶と実ソースを混同すると古いソースへ修正する事故が起きる。

#### 対象範囲

最低対象として、frb_coding_constraints_review_data_v0_3.json、frb_viewdef_generation_rules_review_data_v0_1.json、frb_studio_foundation_review_data_v0_1_github_fetch_urls_added.json の判断ログ系項目を見直す。判断ログには、decision/reason に加えて、applied_axes、conditions、exceptions、expected_behavior、acceptance_criteria、test_pattern_seed、discarded_options、remaining_risks、axis_update_candidate、source_reference、confirmation_level 等の追加を検討する。あわせて、インシデント管理ViewDefおよび憲法レビュー系ViewDefで、これらの項目を入力・表示・Markdown出力できるか確認する。AI作業報告では、静的確認、自動テスト、ビルド確認、ローカル起動確認、スクショ確認、Playwright確認、推定確認、ユーザー実機確認待ちを区別する方針をルール化する。

#### 対象外

この作業では、Studio本体のC# / .NET 実行確認を必須化しない。C#修正は過去に大きな問題が少なく、修正頻度も低いため、AI側でdotnet build/runを必須要求しない。ただし、C#実行確認を実施したか、未実施か、未実施なら理由はインシデントの作業記録へ明示する。Playwright E2EテストやテストパターンJSONの本格運用は、この作業では設計・種作りまでとし、実装自動化は別インシデントで扱う。

#### 固定名方針

判断ログ系フィールドはStudio標準メタ/運用メタとして扱う。ただし、個別Dataの業務フィールド名をRuntimeへ固定実装しない。decision_log / change_history / discussion_history など既存の履歴配列名はインシデント管理データ上の運用語彙として扱うが、他データへ適用する場合はViewDefで宣言された配列・フィールドを正とする。

#### module化方針

type="module" 化は行わない。この作業はルールデータ・ViewDef・判断ログ項目の見直しが主目的であり、既存の従来script方式および現在のStudio構成を前提にする。

#### リスク

判断ログ項目を増やしすぎると、記録が重くなり人間が書かなくなるリスクがある。逆に項目が薄すぎると、AIが後から判断を再現できず、テストパターン生成や差分レビューに使えない。確認種別の明示を曖昧にすると、静的確認や推定確認を実行確認と誤認するリスクがある。最新ソース確認ルールが弱いと、会話文脈だけで古いソースへ修正する事故が再発する。

#### 確認観点

対象3ルールデータに判断ログ系項目見直しが作業対象として明記されていること。判断ログ標準項目に、判断内容・理由・適用判断軸・条件・例外・期待値・受入条件・テストパターン種・残リスク・判断軸更新候補が含まれていること。AI確認種別として、静的確認/JSON parse/ビルド確認/ローカル起動確認/スクショ確認/Playwright確認/推定確認/ユーザー実機確認待ちが区別されていること。C#実行確認は必須化せず、実施有無を記録すればよい方針になっていること。最新ソース未確認時は実装修正を行わず、base_source確認を求める方針になっていること。

#### 作業会話サマリ


##### 依頼 / 方針

インシデントにデータ追加をお願いします。ルール関係の判断ログ系の項目見直しは、最低次の3ファイルが対象。frb_coding_constraints_review_data_v0_3.json、frb_viewdef_generation_rules_review_data_v0_1.json、frb_studio_foundation_review_data_v0_1_github_fetch_urls_added.json。他にも追加すべきものがあれば提案ください。C#の修正時のAI側で実行確認する必要はなし。過去特に問題が発生しておらず、修正頻度も少ないので、それは要求しない。但し、実施有無が明確にインシデントに作業記録として残れば問題なし。

##### AI整理

判断ログ系項目見直しを v0.14.0-decision-log-confirmation-governance として新規インシデント化する。最低対象3ファイルに加えて、インシデント管理ViewDef、憲法レビューViewDef、関連するViewDef/Schema/Rules文書も見直し候補へ含める。C#実行確認は必須化せず、実施/未実施/未実施理由を確認ログとして残す方針を明記する。

##### 追加コメント

最新data/defs ZIPを基準に、v0.14.0-decision-log-confirmation-governanceを再対応。DefView / ViewDef のファイル名は原則変更しないルールを追加したい。C#実行確認は要求しないが、実施有無は作業記録へ明記する。

##### AI追加回答

v0.14.0-decision-log-confirmation-governance 再対応完了。最新data/defs ZIPを基準ソースとして、最低対象3ルールデータに判断ログ拡張・AI確認種別明示・最新ソース未確認時の実装修正禁止・C#実行確認非必須だが記録必須の方針を反映。追加で、ViewDef / DefView のファイル名は原則変更せず、同名更新を基本とするルールを追加した。ViewDefファイル名はData JSONのview_def参照、URL起動、GitHub Pages、GitDiffの接続キーとして扱う。前回のような新規ViewDef名作成は行わず、既存 studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json を同名更新した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0039_001 | 2026-06-26 | user | AI側の確認実態確認 | インシデントで作業依頼した時、AIは何かTESTをしているのか。テストコードを使っているなら見せてほしい。 |
| disc_0039_002 | 2026-06-26 | assistant | 確認種別の整理 | AI側の確認には、JSON構文確認、静的構造確認、JS構文確認、ローカル表示確認、スクショ確認、Playwright確認、推定確認などがあり、正式なテストコードとして外部化されていない確認が混ざっていた。 |
| disc_0039_003 | 2026-06-26 | user | Playwright確認可能性 | Playwrightなども使ってテストできる可能性があるのか確認した。 |
| disc_0039_004 | 2026-06-26 | assistant | Playwright確認方針 | 条件がそろえば、Studioくんをローカル起動または静的配信し、Playwrightで画面表示、DOM確認、スクショ取得を行える可能性がある。ただし毎回実施していたわけではなく、実施有無を明示すべきと整理した。 |
| disc_0039_005 | 2026-06-26 | user | C#実行確認の扱い | C#実行環境がないと言われたことがあるが、C#修正時のAI側実行確認は必須にしなくてよい。過去特に問題が発生しておらず、修正頻度も少ないため要求しない。ただし実施有無は明確に記録したい。 |
| disc_0039_006 | 2026-06-26 | user | 最新ソース未確認事故 | ソースを添付せずに修正依頼したとき、最新ソースではないものに対して修正されたことがあった。直前の別チャットでやりとりしている最新ソースをAIが実ファイルとして認識できないことが原因ではないかと確認した。 |
| disc_0039_007 | 2026-06-26 | assistant | 最新ソース確認ルール | 会話文脈と実ファイルとしての最新ソースは別物。最新ソースが添付またはGitHub commit等で確認できない場合、実装修正を行わず、base_source確認を求めるべきと整理した。 |
| disc_0039_008 | 2026-06-26 | user | インシデント追加依頼 | 判断ログ系項目見直し、AI確認種別明示、最新ソース確認ルール、C#実行確認の扱いをインシデントへ追加したい。最低対象は3つのルールレビュー系データファイル。 |
| disc_0039_009 | 2026-06-26 | user | v0.14.0再対応依頼 | 最新data・defsのZIPを添付し、v0.14.0-decision-log-confirmation-governance の再対応を依頼。DefView / ViewDef のファイル名は原則変更しないルール追加を希望。 |
| disc_0039_010 | 2026-06-26 | assistant | v0.14.0再対応結果 | 最新ZIPを基準に、最低対象3ルールデータ、_json_creation_prompt.md、既存インシデントViewDef同名ファイル、更新済みインシデントJSONを修正。ViewDef新規名は作成せず、GitDiffとData側view_def参照を守る方針を反映。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0039_001 | 2026-06-26 | 判断ログは decision / reason だけでなく、条件・例外・期待値・受入条件・テストパターン種まで残せる構造へ拡張する。 | 判断ログを後続AIが再利用し、テストパターン生成やAI差分レビューへ接続するには、なぜ決めたかだけでなく、どの条件で有効か、何を満たせばOKか、何を例外とするかが必要なため。 |
| dec_0039_002 | 2026-06-26 | AIの確認結果は、確認種別を明示して記録する。 | 静的確認、JSON parse、ビルド確認、ローカル起動確認、スクショ確認、Playwright確認、推定確認、ユーザー実機確認待ちが混在すると、『確認済み』の意味が不透明になるため。 |
| dec_0039_003 | 2026-06-26 | C#修正時のAI側実行確認は必須にしない。ただし実施有無と未実施理由は記録する。 | FRBStudioのC#側修正は過去に大きな問題が少なく、修正頻度も低い。AI側コンテナ環境ではdotnet SDKやWindows固有挙動の制約もあるため、実行確認を必須化すると運用負荷が過剰になるため。 |
| dec_0039_004 | 2026-06-26 | 最新ソースを実ファイルとして確認できない場合、AIは実装修正を行わない。 | 直前の別チャットで扱った最新ソースは、現在チャットの作業ファイルとして自動的に存在するわけではない。会話文脈だけで修正すると、古いソース前提のパッチを作る事故が起きるため。 |
| dec_0039_005 | 2026-06-26 | 既存Data JSONから参照されているViewDef / DefViewファイルは、原則として同じファイル名のまま更新する。 | ViewDefファイル名はData JSONのview_def参照、URL起動、GitHub Pages静的読込、GitDiffの差分観測点として機能しており、安易に新名化すると参照更新漏れや差分確認不能が起きるため。 |
| dec_0039_006 | 2026-06-26 | 今回の作業ではC#実行確認、Playwright、スクショ確認を実施しない。 | ユーザー方針としてC#実行確認は要求されておらず、今回の作業対象はData/Rules/ViewDef更新であるため。未実施であることを確認ログへ明示すれば十分と判断した。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0039_001 | 2026-06-26 | incident_added | studio_work_incident_data_v0_48_index_studio_tool_dock_layout_added.json / items_count=38 | studio_work_incident_data_v0_49_decision_log_confirmation_governance_added.json / items_count=39 | AI確認種別、判断ログ標準化、最新ソース確認、C#実行確認の扱いを、今後のAI駆動開発運用ルールとして作業項目化するため。 |
| chg_0039_002 | 2026-06-26 | rules_and_viewdef_update | v0.14.0はインシデントとして未着手で、判断ログ・確認種別・最新ソース確認・ViewDef安定ファイル名のルールが最低対象3ファイルへ反映されていなかった。前回対応では新しいViewDefファイル名を作成してしまい、Data側view_def参照とGitDiff運用に合わなかった。 | 最低対象3ルールデータへv0.14ルールを反映し、_json_creation_prompt.mdへ短い実務チェックを追加。既存インシデントViewDefはファイル名を変更せず同名更新し、実更新ファイルと確認ログを表示候補へ追加。更新済みインシデントJSONをv0_50として作成。 | 判断ログ駆動テスト生成・AI確認透明化・最新ソース確認・ViewDef安定ファイル名を、StudioくんのAI作業事故防止ルールとして定着させるため。 |

### v0.14.1-data-viewdef-candidates: Data JSON内ViewDef候補リスト / ViewDef生死確認導線
- 作業ID: studio_work_0040
- 種別: feature_design
- 分類: viewdef_management
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/js/core/viewdef_resolver.js, wwwroot/js/runtime/load_runtime.js, wwwroot/app.js, wwwroot/index.html, wwwroot/styles.css, data/json/**/*.json, defs/**/*.json, data/json/00_rules/frb_studio_foundation_review_data_v0_1_github_fetch_urls_added.json, data/json/00_rules/frb_viewdef_generation_rules_review_data_v0_1.json, data/json/00_rules/frb_coding_constraints_review_data_v0_3.json, data/json/00_rules/_json_creation_prompt.md

#### 目的

Data JSON側で、そのDataに対して利用可能なViewDef候補を複数指定できるようにし、Studio上ではData JSONに明示された候補だけを手動切替対象として扱う。これにより、DataとViewDefの紐づきを明確化し、未参照ViewDefを棚卸し・掃除しやすい状態を作る。

#### 背景

ViewDefを短期間に多数作成した結果、どのViewDefが現役で、どれが不要・旧版・実験用なのか分かりにくくなっている。現在は1つのData JSONに対して1つのview_defを指定する運用が中心だが、実際にはリレーション系・レビュー系・診断系など複数のViewで同じDataを確認したい場合がある。一方で、全defsから自由に切替できると、DataとViewDefの関係が曖昧になり、死んでいるViewDefを特定しづらくなる。

#### 対象範囲

既存の top-level view_def は互換性維持のため既定ViewDefとして残す。追加で view_def_candidates または同等の候補配列をData JSONに持てるようにする。StudioのViewDef切替UIは、Data JSONに定義された候補だけを表示する。候補未定義の既存Dataでは、従来どおり単一view_defのみを利用する。候補リストにはlabel/role/status/noteなどを持たせ、現役・旧版・診断用・削除候補を人間が判断できるようにする。

#### 対象外

この作業ではViewDefファイルの自動削除、全Data JSONの一括正規化、dead ViewDef自動削除、ViewDef内容の妥当性判定、Git上の削除コミット生成までは行わない。まずはData JSONからViewDef候補を明示し、紐づき可視化と手動切替の土台を作る。

#### 固定名方針

view_def はStudio標準の既定ViewDef指定キーとして維持する。view_def_candidates はDataとViewDefの関連を表す標準候補キーとして検討するが、Runtimeが特定ドメインのData構造へ依存してはいけない。ViewDefファイル名はDataとの接続キーであり、通常改修では勝手に変更しない。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、ViewDef解決・手動切替UI・候補表示を最小変更で追加する。

#### リスク

Data JSONに候補が増えることで、候補リストの更新漏れが発生する可能性がある。候補に含めるだけで現役扱いにすると古いViewDefが延命するリスクもある。逆に全defsから自由に切替できる設計にすると、DataとViewDefの接続関係が曖昧になり、死んでいるViewDefを特定できなくなる。

#### 確認観点

view_defのみの既存Dataが従来どおり読み込めること。view_def_candidatesを持つDataでは候補リストだけが切替UIに出ること。候補を選ぶと同じDataに対してViewDefだけ切り替わること。存在しない候補ViewDefは警告表示されること。保存時に意図せず既定view_defを書き換えないこと。GitHub Pages静的読込でも候補ViewDefが相対パス解決できること。

#### 作業会話サマリ


##### 依頼 / 方針

ViewDefを大量に作成した結果、どれが生きていてどれが死んでいるのか分からなくなっている。死んでいるViewDefを特定するため、Data JSON側にViewDefを複数指定できるようにしたい。手動で切り替えられるViewDefは、あらかじめData JSONに指定されているものだけにする。これによりDataとViewDefの紐づきを明確化し、ときどき掃除できる状態を作りたい。

##### AI整理

方針OK。DataとViewDefの関係をData側で明示する設計は、ViewDef棚卸しにかなり有効。既存のview_defは既定ViewDefとして維持し、追加でview_def_candidatesのような候補配列を持たせるのが安全。UIでは候補に登録されたViewDefだけを切替可能にし、未参照ViewDefを死活確認しやすくする。

##### 追加コメント

最新ソースZIPを添付し、v0.14.1-data-viewdef-candidates の実装を依頼。最新ソースが取得できない時は中止する方針だったが、今回は添付ZIPを基準ソースとして作業。

##### AI追加回答

v0.14.1-data-viewdef-candidates 実装完了。Data JSONの top-level view_def を既定ViewDef、view_def_candidates を切替可能ViewDef候補として扱うRuntimeを追加。対象Dataに view_def / view_def_candidates がある場合、ViewDef手動切替UIはその候補だけを表示・選択可能にする。候補外ViewDefを明示選択した場合はエラーにし、手動切替しても保存時に既定 view_def を勝手に書き換えないようにした。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0040_001 | 2026-06-26 | user | ViewDef棚卸し相談 | ViewDefを多数作成した結果、どれが生きていてどれが死んでいるか分からない。死んでいるViewDefを特定するために、Data JSON側に複数ViewDefを指定し、手動切替できる候補をData側で限定したい。 |
| disc_0040_002 | 2026-06-26 | assistant | インシデント追加方針 | 既存view_defは既定ViewDefとして残し、追加の候補配列をData JSONに持たせる方針が安全。ViewDef切替UIはDataに定義された候補のみを表示し、未参照ViewDefの棚卸しにつなげる。 |
| disc_0040_003 | 2026-06-26 | user | v0.14.1実装依頼 | 最新ソースZIPを添付し、Data JSON内ViewDef候補リスト対応の実装を依頼。 |
| disc_0040_004 | 2026-06-26 | assistant | v0.14.1実装結果 | view_def / view_def_candidates をData側のViewDef接続契約として読み取り、ViewDefピッカーと明示選択を候補内へ制限するRuntimeを追加。既定view_defの勝手な上書きも抑止。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0040_001 | 2026-06-26 | 既存の top-level view_def は既定ViewDefとして維持する。 | 既存Data JSONとの互換性を守り、Data読込時の標準ViewDefを引き続き一意に決められるようにするため。 |
| dec_0040_002 | 2026-06-26 | 複数ViewDef候補はData JSON側に明示する。 | DataとViewDefの関係をData側の契約として残すことで、全defsからの自由切替よりも死活確認・GitDiff・掃除がしやすくなるため。 |
| dec_0040_003 | 2026-06-26 | 手動ViewDef切替UIは、Data JSONに指定された候補だけを表示する。 | あらかじめ紐づけられたViewDefだけを切替対象にすることで、実験ViewDef・旧ViewDef・未参照ViewDefの境界を明確にするため。 |
| dec_0040_004 | 2026-06-26 | 未参照ViewDefの削除はこのインシデントでは行わない。 | まず参照関係を明示する土台を作り、その後に棚卸しレポートや削除候補抽出を行う方が安全なため。 |
| dec_0040_005 | 2026-06-26 | view_def のみを持つ既存Dataでは、view_defを単一候補として扱う。 | Dataから明示されたViewDefだけを手動切替対象にする方針を徹底し、全defs自由選択による生死不明ViewDefの増殖を防ぐため。 |
| dec_0040_006 | 2026-06-26 | 手動切替しても既定view_defは保存時に自動上書きしない。 | view_defはDataの既定ViewDef契約であり、一時的な候補切替で既定表示が勝手に変わるとGitDiffと運用意図が壊れるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0040_001 | 2026-06-26 | incident_added | Data JSONとViewDefの関係は基本的に単一view_def指定で、複数候補や棚卸し導線がインシデント管理に存在しなかった。 | studio_work_0040 として、Data JSON内ViewDef候補リストとViewDef生死確認導線を登録。 | 大量に作成されたViewDefの現役・旧版・削除候補を判断し、DataとViewDefの接続関係を明確にするため。 |
| chg_0040_002 | 2026-06-26 | runtime_update | ViewDef選択UIは基本的にserverDefNames全体から選択でき、Data JSON側の複数ViewDef候補契約は存在しなかった。 | Data JSONの view_def / view_def_candidates から候補リストを生成し、ViewDef選択UIと明示選択を候補内へ制限するようにした。 | DataとViewDefの接続関係を明確化し、未参照ViewDefの棚卸しをしやすくするため。 |
| chg_0040_003 | 2026-06-26 | data_contract_rule_update | Foundation RulesにData JSON内ViewDef候補契約が明文化されていなかった。 | foundation_rule_019 と _json_creation_prompt.md に、view_def / view_def_candidates の扱いを追記。 | AI作業時にもViewDef候補をData側の接続契約として扱えるようにするため。 |

### v0.14.2-incident-prompt-copy-action: インシデント依頼プロンプト自動生成コピーAction
- 作業ID: studio_work_0041
- 種別: feature
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/js/actions/action_registry.js, wwwroot/js/actions/action_toolbar.js, wwwroot/js/runtime/load_runtime.js, wwwroot/js/core/state.js, wwwroot/app.js, wwwroot/index.html, wwwroot/styles.css, defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json, data/json/01_main/studio_work_incident_data_v0_52_incident_prompt_copy_action_added.json

#### 目的

インシデント管理画面のグリッド上部に、選択中作業項目からAI依頼プロンプトを自動生成してクリップボードへコピーするActionボタンを追加する。毎回incident_fileとphaseを手作業でコピーして依頼ひな形へ貼り付ける負荷とミスを減らし、AI作業依頼の入口品質を安定させる。

#### 背景

インシデント管理JSONからChatGPTへ作業依頼する際、毎回データJSONファイル名とphaseをコピーし、定型プロンプトへ貼り付ける小さな手作業が発生している。作業としては地味だが、頻度が高く、phaseやincident_fileの貼り間違いが起きるとAI作業の前提がズレる。Studioくんには既にtoolbar.executeButtonとActionRegistryの戦略的設計パターンがあるため、ViewDefにプロンプトひな形を宣言し、JS側は汎用的にテンプレート展開してクリップボードへコピーするActionとして実装するのが自然。

#### 対象範囲

インシデント管理ViewDefのグリッド上部または既存のexecuteButton領域に『AI依頼プロンプトコピー』ボタンを追加する。ボタン定義はViewDef側にcaption/action/promptTemplateを持たせる。Runtime/Action側では選択中行、現在読込中Data JSON相対パス、必要に応じてViewDef情報をActionContextへ渡す。CopyPromptFromTemplate Actionは、ViewDefに定義されたpromptTemplate内の {{data.filePath}} / {{data.fileName}} / {{row.phase}} / {{row.work_item_id}} / {{row.title}} などを展開し、navigator.clipboard.writeTextでコピーする。コピー成功時はtoast表示し、clipboard API失敗時は手動コピー用textareaまたはdialogへfallbackする。

#### 対象外

この作業ではChatGPT API連携、外部LLMへの自動送信、Action実行によるGitHub取得、インシデント自動作成、選択行の自動ステータス変更、複数行一括依頼生成は行わない。まずは選択中1行の依頼プロンプトを生成してクリップボードへコピーするところまでを対象とする。

#### 固定名方針

JS側にインシデント専用の依頼文を固定実装しない。プロンプト本文はViewDefのpromptTemplateへ置く。Action名 CopyPromptFromTemplate は汎用Action識別子として扱い、Data固有の文言やFoundation Rule URLなどはViewDef設定値として渡す。ViewDefファイル名はDataとの接続キーであるため、既存ViewDefファイル名を変更せず同名更新を基本とする。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式とActionRegistry構造を維持し、必要なActionとActionContext拡張だけを最小変更で追加する。

#### リスク

ActionContextに現在Dataファイル名や選択行が渡らない場合、誤ったincident_fileやphaseで依頼文が生成されるリスクがある。clipboard APIはブラウザ権限や非HTTPS環境で失敗する場合がある。JS側へ依頼文を固定実装するとRuntimeがインシデント管理専用に太る。複数行選択や未選択時の扱いを曖昧にすると誤依頼につながる。

#### 確認観点

インシデント管理JSONを読み込み、任意の作業行を選択した状態で『AI依頼プロンプトコピー』ボタンを押すと、クリップボードにincident_fileとphaseが埋め込まれた依頼文が入ること。選択行を変えるとphaseが変わること。現在読込中Data JSONの相対パスがincident_fileへ入ること。未選択時はコピーせず警告すること。promptTemplate未定義時は分かりやすいエラーになること。clipboard API失敗時に手動コピーできること。既存executeButton/ActionRegistry動作に回帰がないこと。

#### 作業会話サマリ


##### 依頼 / 方針

毎回インシデントからChatGPTへお願いするときに、jsonファイル名とphase名を手作業でコピーして依頼ひな形へ貼り付けるのが地味に嫌。グリッド一覧の上部にアクションボタンを配置し、クリックしたらViewDefに仕込んだプロンプトひな形へデータJSONファイル名とphase名を埋め込み、クリップボードへコピーしてほしい。戦略的設計パターン対応で、ViewDefにボタン名を指定し、Action用FunctionをJS側に追加すれば機能するはず。まず会話で認識合わせし、OKならインシデントを追加したい。

##### AI整理

方針OK。これは単なる便利機能ではなく、Studioくん自身を依頼発行装置にする改善。JS側は汎用Action CopyPromptFromTemplate として、ViewDefのpromptTemplateを読み、選択行と現在Dataファイル情報で変数展開してクリップボードへコピーする。依頼文そのものはJSへ固定せずViewDef側へ置くのが正しい。

##### 追加コメント

v0.14.2-incident-prompt-copy-action の対応依頼。作業ルールとして Foundation Rules raw / main ZIP / raw base URL を指定し、FRB Studio Foundation Rules の foundation_rule_019「GitHub基準ソースとZIP返却契約」を参照すること。最新ソース一式として wwwroot20260627_0007.zip と studio_work_incident_data_v0_53_data_viewdef_candidates_implemented.json を添付。

##### AI追加回答

v0.14.2-incident-prompt-copy-action 対応完了。CopyPromptFromTemplate Actionを追加し、ViewDefの toolbar.executeButton.promptTemplate からAI依頼プロンプトを生成するようにした。選択中行の phase / work_item_id / title と現在読込中Data JSONの data/json/... パスをテンプレート変数へ展開し、クリップボードへコピーする。clipboard APIが失敗した場合は手動コピー用ダイアログを表示する。プロンプト本文はJSに固定せず、インシデント管理ViewDef側に保持する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0041_001 | 2026-06-26 | user | AI依頼プロンプトコピー相談 | 毎回インシデントから依頼するときに、jsonファイル名とphase名をコピーしてひな形に貼り付ける作業が地味に嫌。グリッド一覧上部のアクションボタンで、ViewDefに仕込んだプロンプトひな形へ自動埋め込みし、クリップボードへコピーしたい。 |
| disc_0041_002 | 2026-06-26 | assistant | 設計方針確認 | 既存のtoolbar.executeButton / ActionRegistry方針に乗せられる。JS側には汎用Action CopyPromptFromTemplate を追加し、依頼文はViewDefのpromptTemplateへ置くのが安全。 |
| disc_0041_003 | 2026-06-26 | user | インシデント追加依頼 | できる認識でOK。インシデントを追加して返却してほしい。 |
| disc_0041_004 | 2026-06-26 | assistant | インシデント追加結果 | studio_work_0041 / v0.14.2-incident-prompt-copy-action として、インシデント依頼プロンプト自動生成コピーActionを追加。 |
| disc_0041_005 | 2026-06-27 | user | v0.14.2-incident-prompt-copy-action作業依頼 | v0.14.2-incident-prompt-copy-action の対応依頼。作業ルールとして Foundation Rules raw / main ZIP / raw base URL を指定し、FRB Studio Foundation Rules の foundation_rule_019「GitHub基準ソースとZIP返却契約」を参照すること。最新ソース一式として wwwroot20260627_0007.zip と studio_work_incident_data_v0_53_data_viewdef_candidates_implemented.json を添付。 |
| disc_0041_006 | 2026-06-27 | assistant | v0.14.2-incident-prompt-copy-action作業結果 | v0.14.2-incident-prompt-copy-action 対応完了。CopyPromptFromTemplate Actionを追加し、ViewDefの toolbar.executeButton.promptTemplate からAI依頼プロンプトを生成するようにした。選択中行の phase / work_item_id / title と現在読込中Data JSONの data/json/... パスをテンプレート変数へ展開し、クリップボードへコピーする。clipboard APIが失敗した場合は手動コピー用ダイアログを表示する。プロンプト本文はJSに固定せず、インシデント管理ViewDef側に保持する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0041_001 | 2026-06-26 | プロンプト本文はJSではなくViewDefのpromptTemplateへ置く。 | 依頼文をJSへ固定するとRuntimeがインシデント管理専用に太るため。ViewDefが文章・ボタン名・Action指定を持ち、Runtimeは汎用的にテンプレート展開する方がStudioくんの設計思想に合う。 |
| dec_0041_002 | 2026-06-26 | Action名は CopyPromptFromTemplate のような汎用Actionにする。 | 将来、インシデント依頼以外にもレビュー依頼、Markdown記事依頼、差分レビュー依頼などのテンプレートコピーへ使い回せるため。 |
| dec_0041_003 | 2026-06-26 | テンプレート変数として現在Dataファイル情報と選択中行をActionContextへ渡す。 | incident_fileとphaseを自動埋め込みするには、現在読込中のData JSON相対パスと選択行のphaseが必要になるため。 |
| dec_0041_004 | 2026-06-26 | ViewDefファイル名は変更せず、既存のインシデント管理ViewDefを同名更新する。 | ViewDefファイル名はData JSONとの接続キーであり、GitDiffの観測点でもあるため。通常改修で新しいViewDef名を勝手に作ると参照更新や差分確認が面倒になる。 |
| dec_0041_005 | 2026-06-27 | クリップボード失敗時は手動コピー用ダイアログを表示する。 | ブラウザ権限や非HTTPS環境で navigator.clipboard.writeText が失敗しても、生成済みプロンプトを失わず人間がコピーできるようにするため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0041_001 | 2026-06-26 | incident_added | インシデント管理画面からChatGPT依頼文を作る際、incident_fileとphaseを人間が手作業でコピーしていた。 | studio_work_0041 として、ViewDefのpromptTemplateとActionRegistryを使ったAI依頼プロンプト自動生成コピーActionを登録。 | 小さな定型作業をAction化し、AI依頼の入口品質を安定させるため。 |
| chg_0041_002 | 2026-06-27 | incident_prompt_copy_action_implemented | toolbar.executeButton からActionは実行できたが、インシデント依頼プロンプトをViewDefテンプレートから生成してコピーする汎用Actionは未実装だった。 | CopyPromptFromTemplate Actionを追加し、ViewDefのpromptTemplateを選択行と現在Dataファイル情報で展開してクリップボードへコピーできるようにした。 | incident_file と phase の手作業コピーをなくし、AI作業依頼の入口品質を安定させるため。 |

### v0.14.3-v0.14.12-test-evidence-folder-and-diff-contract: テスト証跡フォルダー整理 / Actual-Diff責務分離 / Diff共通フォーマット整理
- 作業ID: studio_work_0042
- 種別: architecture_data_contract
- 分類: test_evidence
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: data/json/03_tests/**, tests/screen_state/ncjs-screen-state-compare.checks.spec.ts, tests/qa/static/incident_prompt_copy_action_viewdef_static.test.mjs, playwright.config.ts, .gitignore, tests/tools/cleanup_runtime_artifacts.ps1

#### 目的

screen_state_smoke_001 と incident_prompt_copy_action のテスト証跡を data/json/03_tests 配下へ集約し、Expected / Actual / Diff / TestPattern / Relation の責務と配置を整理する。あわせて、Actual JSON と Diff JSON の責務を分離し、Diff Result を共通ViewDefで扱える方向へ寄せる。

#### 背景

v0.14.2-incident-prompt-copy-action 実装後、Actual Result JSONの明細強調表示やサマリ表示を確認する中で、passed/pass のフィールド名不一致、ActualとDiffの責務混在、旧フォルダー残存、Playwright実行時生成物のroot直下発生などが連続して発覚した。これらはJS拡張ではなく、データ契約・フォルダー構造・証跡文化の問題として整理する必要があった。

#### 対象範囲

Step 1としてscreen_state_smoke_001のテストデータを data/json/03_tests/screen_state/screen_state_smoke_001/ 配下へ集約。Step 2としてscreen_state actual/diff出力先を新階層へ変更。Step 3としてincident_prompt_copy_actionを data/json/03_tests/qa/v0_14_2_incident_prompt_copy_action/ 配下へ移動。Step 4-AとしてQAのactual.jsonを観測値のみ、diff.jsonを比較結果に責務分離。Step 4-BとしてQA DiffとScreen State Diffの上部サマリ項目とchecks[].passを共通化。さらにPlaywright/runtime生成フォルダーのroot直下発生抑止、旧パス罠フォルダー削除、diff出力パス確認を実施した。

#### 対象外

Diff Result共通ViewDefの本格作成・既存screen_state/qa全データの完全移行・全テストスイートの自動実行統合・ViewDef共有化は次Stepへ残す。actual.jsonの共通ViewDef化もこの段階では対象外。

#### 固定名方針

強調表示のためにRuntime JSをpass/passed両対応へ太らせるのではなく、データ契約を既存文化の checks[].pass に揃える。Actual Result JSONの判定フィールドに checks[].passed を標準化しない。Diff JSONの明細判定フィールドは checks[].pass を正とする。

#### module化方針

type="module" 化は行わない。既存のNode test / Playwright構成を維持し、出力先とデータ契約のみ整理する。

#### リスク

旧パスが残ると、diffが出ているのに空フォルダーを見てしまう罠が残る。Expected差分でnode --testがfailする場合でも、diff.jsonが先に保存される必要がある。Windowsではtest-results配下の長いPlaywright添付ファイル名がZIP解凍エラーを起こすため、成果物ZIPにruntime生成物を混ぜない必要がある。

#### 確認観点

screen_state_smoke_001のexpected/actual/diff/test_patternsが03_tests/screen_state配下にあること。QAのexpected/actual/diff/test_patterns/relationsが03_tests/qa配下にあること。QA actual.jsonにexpected/pass/resultLabel/summaryが入らないこと。QA diff.jsonにexpected/actual/pass/resultLabel/summary/failedCount/failedCheckIds/firstFailureが入ること。Expectedを意図的にズラした場合でもdiff.jsonが出力された後にtestがfailすること。root直下にplaywright-report/test-results/test_results/tests_screen_stateが生えないこと。旧 data/json/03_tests/v0_14_2_incident_prompt_copy_action/ が残っていないこと。

#### 作業会話サマリ


##### 依頼 / 方針

Step 1〜Step 4-Bとして、screen_state_smoke_001 のデータ整理、actual/diff出力先変更、incident_prompt_copy_action の 03_tests/qa 配下移動、Actual/Diff責務分離、QA Diff と Screen State Diff の共通サマリフォーマット整理を依頼。途中で、空の tests_screen_state が生える問題、Playwright生成フォルダー問題、diff.jsonが出ていないように見える問題もあわせて解消したい。

##### AI整理

テスト証跡を data/json/03_tests 配下へ整理し、Expected / Actual / Diff の責務を分離。Actualは観測値、Diffは比較結果と定義し直し、Diff Resultの上部サマリを共通化した。Playwright生成物は tests/.runtime へ隔離し、root直下の罠フォルダーと旧パスを削除する方針にした。

##### 追加コメント

OK!!解決！！次の１手は？？まず　インシデントにこのチャットでやったことを作業履歴として追加しようか？？更新後Json返却お願い

##### AI追加回答

このチャットで整理したテスト証跡フォルダー構造、Actual/Diff責務分離、Diff共通フォーマット、runtime生成物抑止、旧パス罠フォルダー削除までを studio_work_0042 として作業履歴に追加する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0042_001 | 2026-06-27 | user | Actual Result強調表示の違和感 | 明細のfail強調は効いたが、左上の判定や差分サマリの強調にも対応したい。次のステップで共有フォーマットにしないといけない。 |
| disc_0042_002 | 2026-06-27 | assistant | データ契約への方針修正 | JSをpass/passed両対応に太らせるのではなく、Actual Result JSON側を既存文化の pass に合わせるべきと整理。checks[].passed は使わず checks[].pass を正とする方針へ修正した。 |
| disc_0042_003 | 2026-06-27 | user | フォルダー階層整理相談 | 既にあるスモークテスト関係のデータのフォルダー階層を綺麗にする必要がある。テストパターンJSONなどは FRBStudio_App/data/json/03_tests 配下に置くほうが綺麗ではないかという違和感。 |
| disc_0042_004 | 2026-06-27 | assistant | Step 1 方針 | data/json/03_tests/{domain}/{suite_id}/ 配下に test_patterns / expected / actual / diff / relations / summary / notes を集約する案を提示。Step 1として screen_state_smoke_001 のデータだけを 03_tests/screen_state 配下へ整理した。 |
| disc_0042_005 | 2026-06-27 | user | tests_screen_state の存在確認 | tests_screen_state フォルダーに .github/.gitignore/setup.md があるが、これは必要なのか、想定は何かと確認。 |
| disc_0042_006 | 2026-06-27 | assistant | tests_screen_state の扱い | tests_screen_state は旧構成の名残であり、正本フォルダーではないと整理。テストデータは data/json/03_tests、実行コードは tests、ViewDefは defs に分ける方針を確認した。 |
| disc_0042_007 | 2026-06-27 | user | Step 2依頼 | screen_state の actual / diff 出力先を新階層へ変更するStep 2を依頼。 |
| disc_0042_008 | 2026-06-27 | assistant | Step 2対応 | screen_stateのテストコードがテストパターンJSON内の expectedFile / outputActualFile / outputDiffFile を読んで、新しい data/json/03_tests/screen_state/screen_state_smoke_001 配下へ出力するように整理した。 |
| disc_0042_009 | 2026-06-27 | user | Step 3依頼 | incident_prompt_copy_action を 03_tests/qa 配下へ寄せるStep 3を依頼。 |
| disc_0042_010 | 2026-06-27 | assistant | Step 3対応 | incident_prompt_copy_action 系を data/json/03_tests/qa/v0_14_2_incident_prompt_copy_action/ 配下へ移動。patterns は test_patterns に揃え、Expected JSONのexecution_contractやテストコード参照も新パスへ更新した。 |
| disc_0042_011 | 2026-06-27 | user | actual.json と diff.json の責務相談 | .actual.json と diff.json の違いがよく分からなくなった。diff.json は actual.json があれば不要ではないかと相談。 |
| disc_0042_012 | 2026-06-27 | assistant | 責務分離方針 | 今のactual.jsonはactualではなくdiff/resultになっていると整理。本来は expected.json=期待値、actual.json=観測値、diff.json=比較結果 と分けるべきと提案した。 |
| disc_0042_013 | 2026-06-27 | user | Step 4-A依頼 | TP-IPC-001 の actual.json / diff.json の責務分離を依頼。actual.jsonは観測値のみ、diff.jsonはexpected/actual/pass/summaryを持ち、node --testの成否はdiff.failedCountをもとに判定する方針。あわせてスモークテストで空の tests_screen_state が生えるのも止めてほしい。 |
| disc_0042_014 | 2026-06-27 | assistant | Step 4-A対応 | QA actual.jsonを観測値のみへ分離し、diff.jsonを比較結果の正本に変更。テストコードはExpectedを読み、Actual Observation生成、Diff Result生成、diff.failedCountでfail/pass判定する流れに整理した。空のtests_screen_state対策も追加した。 |
| disc_0042_015 | 2026-06-27 | user | Windows ZIP解凍エラー | ZIP解凍時にファイル名が長すぎるエラーが大量に発生した。 |
| disc_0042_016 | 2026-06-27 | assistant | runtime生成物除去 | 原因はPlaywrightのtest-results/attachments等の長い生成物をZIPに混ぜたこと。test-results / playwright-report / test_results / tests_screen_state を成果物ZIPから除去し、Windows解凍安全版を作成した。 |
| disc_0042_017 | 2026-06-27 | user | runtimeフォルダー再発 | playwright-report / test_results / test-results / tests_screen_state などのフォルダーがまたroot直下に生えたと報告。 |
| disc_0042_018 | 2026-06-27 | assistant | Playwright runtime出力ポリシー | playwright.config.ts を追加し、root直下へplaywright-report/test-resultsを作らないようにして、一時出力を tests/.runtime/playwright-output/ へ隔離。.gitignoreと cleanup_runtime_artifacts.ps1 も追加した。 |
| disc_0042_019 | 2026-06-27 | user | Step 4-B依頼 | QA Diff と Screen State Diff の共通サマリフォーマット整理を依頼。diff.jsonの上部サマリ項目、checks[].pass、failedCount/failedCheckIds/firstFailureを共通化し、同じViewDefで見られる方向に寄せたい。actual.jsonは対象外。 |
| disc_0042_020 | 2026-06-27 | assistant | Step 4-B対応 | QA Diff と Screen State Diff の schema_version/document_type/domain/diff_kind/status/resultLabel/summary/total/passCount/failCount/failedCount/failedCheckIds/firstFailure/checks[].pass を共通化するように生成側と既存diffを整理した。 |
| disc_0042_021 | 2026-06-27 | user | diff.json未出力エラー | Expected比較はわざとエラーにしているが、TP-IPC-001.diff.json が出力されていないと報告。 |
| disc_0042_022 | 2026-06-27 | assistant | diff出力順序修正 | diff.jsonを保存し、存在確認した後に failedCount を見てtestをfailさせる順序へ修正した。Expected差分でfailしてもdiff.jsonは残る方針を明確化した。 |
| disc_0042_023 | 2026-06-27 | user | 旧パス罠フォルダー発見 | diffフォルダーが空に見えると再報告。実際には data/json/03_tests/v0_14_2_incident_prompt_copy_action/diff という旧パスを見ていた。 |
| disc_0042_024 | 2026-06-27 | assistant | 旧パス削除 | 正本は data/json/03_tests/qa/v0_14_2_incident_prompt_copy_action/diff/TP-IPC-001.diff.json であり、旧フォルダー data/json/03_tests/v0_14_2_incident_prompt_copy_action/ が罠になっていたためZIPから削除し、cleanupにも旧パス削除を追加した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0042_001 | 2026-06-27 | テスト証跡データは data/json/03_tests/{domain}/{suite_id}/ 配下へ集約する。 | Expected / Actual / Diff / TestPattern / Relation が散在すると、Studioくんでの確認・AIへの引継ぎ・Git差分確認で迷子になるため。 |
| dec_0042_002 | 2026-06-27 | テストコードは data/json に置かず tests/ 配下に置く。 | data/json はStudioくんで見るテスト証跡・期待値・差分の置き場であり、実行する仕掛けは tests/ に分けるため。 |
| dec_0042_003 | 2026-06-27 | ViewDefは data/json に置かず defs/ 配下に置く。 | DataとViewを分離し、Data JSONの参照キーとしてViewDefを安定運用するため。 |
| dec_0042_004 | 2026-06-27 | Diff明細の判定フィールドは checks[].pass を正とする。 | 既存のscreen_state diff表示・強調表示がpassを前提としており、passedを追加標準化すると契約が分裂するため。 |
| dec_0042_005 | 2026-06-27 | actual.json は観測値のみを持つ。 | actual.jsonにexpected/pass/summaryを入れるとdiff.jsonとの責務が崩れ、Diffという名前の意味が失われるため。 |
| dec_0042_006 | 2026-06-27 | diff.json は expected と actual の比較結果を持つ。 | Expected=期待値、Actual=観測値、Diff=比較結果という三層構造を明確にすることで、AI駆動開発の証跡文化として再利用しやすくなるため。 |
| dec_0042_007 | 2026-06-27 | Expected差分でテストがfailしても、diff.jsonは必ず保存してからfailさせる。 | テストfail時こそ差分証跡が必要であり、Diff Result JSONをStudioくんで確認できないとAI差分物語・承認判断に使えないため。 |
| dec_0042_008 | 2026-06-27 | Playwrightのruntime生成物はroot直下に出さず tests/.runtime/ へ隔離する。 | root直下にplaywright-report/test-results/test_results/tests_screen_stateが生えると、ソース正本と実行時生成物が混ざり、ZIP配布やGit管理で混乱するため。 |
| dec_0042_009 | 2026-06-27 | 旧パス data/json/03_tests/v0_14_2_incident_prompt_copy_action/ は残さない。 | 正本を data/json/03_tests/qa/v0_14_2_incident_prompt_copy_action/ に移した後、旧フォルダーが残るとdiff未出力と誤認する罠フォルダーになるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0042_001 | 2026-06-27 | folder_structure | screen_state_smoke_001 関連データが data/json/03_screen_state, test_patterns, tests_screen_state/test_results 等に散在。 | data/json/03_tests/screen_state/screen_state_smoke_001/test_patterns, expected, actual, diff, relations, summary, notes に集約。 | スモークテスト証跡をテスト単位で追跡しやすくするため。 |
| chg_0042_002 | 2026-06-27 | screen_state_output_path | screen_state actual/diff の出力先が旧構成やテストコード側の固定パスに依存。 | テストパターンJSONの expectedFile / outputActualFile / outputDiffFile を読み、新しい03_tests配下へ出力。 | 出力先をテストコード固定ではなく、テストパターンデータ契約へ寄せるため。 |
| chg_0042_003 | 2026-06-27 | qa_folder_structure | data/json/03_tests/v0_14_2_incident_prompt_copy_action/ 配下にQAテスト証跡が配置され、domainが階層に含まれていなかった。 | data/json/03_tests/qa/v0_14_2_incident_prompt_copy_action/ 配下に test_patterns, expected, actual, diff, relations, summary, notes を配置。 | 今後qa以外のdomainが増えても整理できるようにするため。 |
| chg_0042_004 | 2026-06-27 | actual_diff_responsibility_split | TP-IPC-001.actual.json に expected / actual / pass / summary が混在し、実質diff/resultになっていた。 | TP-IPC-001.actual.json は観測値のみ、TP-IPC-001.diff.json は expected / actual / pass / summary / failedCount / firstFailure を持つ比較結果に分離。 | ActualとDiffの責務を明確化し、Diffという名前に意味を戻すため。 |
| chg_0042_005 | 2026-06-27 | diff_common_format | QA Diff と Screen State Diff の上部サマリ項目や明細項目が揺れていた。 | schema_version=document_type=diff_result_v0_1系、status/resultLabel/summary/total/passCount/failCount/failedCount/failedCheckIds/firstFailure/checks[].pass を共通化。 | 将来的に同じDiff Result ViewDefで表示できる方向に寄せるため。 |
| chg_0042_006 | 2026-06-27 | runtime_artifact_policy | Playwright実行時にroot直下へplaywright-report, test-results, test_results, tests_screen_stateが生え、ZIPへ混入するとWindows長パスエラーも発生した。 | playwright.config.ts と .gitignore と cleanup_runtime_artifacts.ps1 を追加し、runtime生成物を tests/.runtime/ へ隔離。成果物ZIPからruntime生成物を除外。 | ソース正本・証跡JSON・一時生成物を混ぜないため。 |
| chg_0042_007 | 2026-06-27 | legacy_path_cleanup | data/json/03_tests/v0_14_2_incident_prompt_copy_action/ 旧フォルダーが残り、ユーザーが空のdiffフォルダーを見て未出力と誤認した。 | 旧フォルダーをZIPから削除し、cleanupスクリプトにも旧パス削除を追加。正本は data/json/03_tests/qa/v0_14_2_incident_prompt_copy_action/ に一本化。 | 旧パスを罠フォルダーとして残さないため。 |

### v0.14.13-foundation-commonization-archive-filename-policy: Foundation / Coding Constraints 共通化・archive退避・ファイル名維持原則
- 作業ID: studio_work_0043
- 種別: rules_review
- 分類: foundation_policy
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: data/json/00_rules/frb_coding_constraints_review_data_v0_3.json, data/json/00_rules/frb_studio_foundation_review_data_v0_1_github_fetch_urls_added.json, data/json/00_rules/_json_creation_prompt.md, data/json/01_main/studio_work_incident_data_v0_56_rules_revision_work_items_added.json, data/json/05_inventory/defs_data_link_inventory_v0_1.json, data/json/05_inventory/defs_data_link_inventory_v0_2_repaired.json, _archive/{削除日時}/...

#### 目的

Studioくん全体の作業原則として、共通化優先、人間相談、削除データの_archive退避、ルール/ViewDefファイル名維持を憲法・Foundation・AI作業プロンプトへ整理する。

#### 背景

Step 4-A/4-Bの作業で、JSを増やすよりデータ契約を揃えること、旧パスを残すと罠フォルダーになること、ViewDef名を変えると参照元修正が連鎖することが明確になった。

#### 対象範囲

共通化できるものは原則共通化する。ただし過剰共通化で将来苦しくなる場合はAIが独断せず人間に相談する。古いデータ・不要データは成果物から削除し、ルート_archive/{削除日時}/へ退避する。ルール系統およびViewDefは原則ファイル名を変更しない。

#### 対象外

Expected/Actual/Diffの詳細フォーマットや個別ViewDef実装はこの作業では扱わない。まず最上位の作業原則として記録する。

#### 固定名方針

ルール系ファイルおよびViewDefは、既存参照を壊さないため原則として同じファイル名のまま更新する。新しい正本世代を作る必要がある場合は、人間に確認してからファイル名変更する。

#### module化方針

type="module" 化は今回の主目的ではない。ルールData / ルールMD / ViewDef / インシデント管理JSONの作業単位整理を対象とする。

#### リスク

共通化原則を強く書きすぎると、ドメイン差分まで無理に潰す危険がある。archive退避を曖昧にすると削除したはずの旧パスが成果物に残り、再び罠フォルダーになる。

#### 確認観点

共通化原則、人間相談条件、_archive/{削除日時}/退避、ルール/ViewDefファイル名維持が各対象ファイルの責務に応じて入っていること。

#### 作業会話サマリ


##### 依頼 / 方針

このチャットで見えてきた憲法・ルール系の改正概要を、作業単位ごとにインシデントへ追加する。追加原則として、共通化できるものは原則共通化し、やりすぎて将来苦しくなる場合は人間に相談する。古いデータ・不要データは削除して返却するが、削除データはルートの _archive/{削除日時}/ に退避する。ルール系統およびViewDefを修正する場合は、参照元修正を避けるため原則ファイル名を変更しない。

##### AI整理

Foundation / Coding Constraints 共通化・archive退避・ファイル名維持原則 を作業単位として追加する。実装・ルール本文修正は次工程で行い、今回のインシデント追加では対象ファイル・目的・範囲・判断ログを整理する。

実作業結果: Foundation/Coding Constraints/_json_creation_promptへv0.14.13原則を反映。旧パス・不要データはactiveから外し、_archiveへ退避する運用を今回の成果物でも適用。

##### 追加コメント

最新資材として添付ZIPを使用し、incident_file=data/json/01_main/studio_work_incident_data_v0_56_rules_revision_work_items_added.json、phase=v0.14.13-foundation-commonization-archive-filename-policy を対象に作業。Foundation Rules の foundation_rule_019「GitHub基準ソースとZIP返却契約」を参照。

##### AI追加回答

v0.14.13 対応完了。Foundation Rulesに共通化・archive退避・ファイル名維持原則を追加し、foundation_rule_019へZIP返却契約として追記、foundation_rule_020を新規追加。Coding Constraints の constitution_20へ同原則を追記し、_json_creation_prompt.mdへ短い実務チェックを追加。添付ZIP内でFoundation Rulesが派生名になっていたため、GitHub raw契約上の安定名 frb_studio_foundation_review_data_v0_1_github_fetch_urls_added.json へactiveファイル名を復元し、旧派生名ファイルとFoundation内のテスト行 row_copy_1 は _archive/{削除日時}/へ退避。成果物ZIPから tests/.runtime 等のruntime生成物は除外。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0043_001 | 2026-06-27 | user | 憲法・ルール改正候補の作業単位化依頼 | このチャットで見えてきた憲法・ルール系の改正概要を、作業単位ごとにインシデントへ追加する。追加原則として、共通化できるものは原則共通化し、やりすぎて将来苦しくなる場合は人間に相談する。古いデータ・不要データは削除して返却するが、削除データはルートの _archive/{削除日時}/ に退避する。ルール系統およびViewDefを修正する場合は、参照元修正を避けるため原則ファイル名を変更しない。 |
| disc_0043_002 | 2026-06-27 | assistant | 作業単位化方針 | Foundation / Coding Constraints 共通化・archive退避・ファイル名維持原則 として、対象ルールファイル・目的・範囲・リスク・確認観点を整理してインシデントへ追加する。 |
| disc_0043_003 | 2026-06-27 | user | v0.14.13作業依頼 | 最新資材は添付ZIPを使用。incident_file=data/json/01_main/studio_work_incident_data_v0_56_rules_revision_work_items_added.json、phase=v0.14.13-foundation-commonization-archive-filename-policy。Foundation Rules raw URLとfoundation_rule_019「GitHub基準ソースとZIP返却契約」を参照。 |
| disc_0043_004 | 2026-06-27 | assistant | v0.14.13作業結果 | Foundation Rules / Coding Constraints / _json_creation_prompt.mdへ共通化優先・人間相談・_archive退避・ファイル名維持原則を反映。Foundation RulesはGitHub raw契約の安定名へ復元し、旧派生名とテスト行を_archiveへ退避。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0043_001 | 2026-06-27 | 共通化できるものは原則共通化する。 | 今回のDiff/Actual/ViewDef整理で、構造が揃っているものは共有フォーマットへ寄せた方がStudioくんの表示・比較・AIレビューが安定するため。 |
| dec_0043_002 | 2026-06-27 | 共通化が将来の拡張性・可読性・保守性を苦しくすると判断した場合、AIは人間に相談する。 | 過剰共通化は別ドメインの意味を薄め、あとで逃げ場がなくなるため。 |
| dec_0043_003 | 2026-06-27 | 古いデータ・不要データは成果物から削除し、_archive/{削除日時}/へ退避する。 | 旧パスを残すと、存在するだけで正本と誤認される罠フォルダーになるため。 |
| dec_0043_004 | 2026-06-27 | ルール系統およびViewDefは原則ファイル名を変更しない。 | Data JSONのview_def参照、URL起動、GitHub Pages、AIプロンプトがファイル名に依存しており、変更時の連鎖修正を避けるため。 |
| dec_0043_005 | 2026-06-27 | 添付ZIP内のFoundation Rules派生名ファイルはactiveに残さず、安定名へ復元して旧名を_archiveへ退避する。 | 作業プロンプトとfoundation_rule_019のraw URLが安定名を参照しており、派生名をactiveに残すと次回以降の取得・参照がズレるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0043_001 | 2026-06-27 | incident_added | 共通化・archive退避・ファイル名維持が作業項目として分離されていなかった。 | studio_work_0043 として最上位ルール改正作業を追加。 | 今回のチャットで憲法級の作業原則が複数見えたため。 |
| chg_0043_002 | 2026-06-27 | rules_update_applied | 共通化・archive退避・ファイル名維持はインシデント作業項目として登録済みだったが、ルール本文には未反映だった。 | Foundation Rules、Coding Constraints、_json_creation_prompt.mdへv0.14.13原則を反映。 | 今回の作業依頼 phase=v0.14.13-foundation-commonization-archive-filename-policy に対応するため。 |
| chg_0043_003 | 2026-06-27 | archive_and_filename_restore | 添付ZIP内のFoundation Rules activeファイル名が frb_studio_foundation_review_data_v0_1_github_fetch_urls_added_viewdef_candidates_rule_added.json になっていた。またFoundation rules[]にMarkdown入力テスト用の row_copy_1 が残っていた。 | active側をGitHub raw契約の安定名 frb_studio_foundation_review_data_v0_1_github_fetch_urls_added.json へ復元。旧派生名ファイルと row_copy_1 は _archive/{削除日時}/へ退避。 | foundation_rule_019のraw URL契約と、v0.14.13のルール/ViewDefファイル名維持・不要データarchive退避原則に合わせるため。 |

### v0.14.14-test-evidence-rules-contract: Test Evidence Rules / Expected-Actual-Diff責務分離
- 作業ID: studio_work_0044
- 種別: rules_review
- 分類: test_evidence
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: 新規候補: data/json/00_rules/frb_test_evidence_rules_review_data_v0_1.json, 既存反映候補: data/json/00_rules/frb_studio_foundation_review_data_v0_1_github_fetch_urls_added.json, tests/**/*.mjs, tests/**/*.spec.ts

#### 目的

Expected JSON / Actual JSON / Diff JSON / Test Code の責務をルールとして固定し、テスト失敗時にもDiff証跡が必ず残る文化を定義する。

#### 背景

TP-IPC-001でactual.jsonにexpected/pass/summaryが混在し、diff.jsonの存在意義が曖昧になった。責務分離により、Diffという名前へ意味を戻す必要がある。

#### 対象範囲

Expected JSONは期待値の正本、Actual JSONは観測値のみ、Diff JSONはExpectedとActualの比較結果、Test Codeは実行する仕掛けと定義する。actual.jsonにはexpected/pass/resultLabel/summary/failedCountを持たせない。Diff出力後にassertする。

#### 対象外

個別テストコードの全面修正や既存全テストデータの移行はこの作業では必須にしない。まずルールとして正本化する。

#### 固定名方針

ルール系ファイルおよびViewDefは、既存参照を壊さないため原則として同じファイル名のまま更新する。新しい正本世代を作る必要がある場合は、人間に確認してからファイル名変更する。

#### module化方針

type="module" 化は今回の主目的ではない。ルールData / ルールMD / ViewDef / インシデント管理JSONの作業単位整理を対象とする。

#### リスク

actual.jsonに比較結果を混ぜると、diff.jsonが不要に見え、証跡の名前と責務が崩れる。assert前にdiffを書かないと、失敗したのに確認材料が残らない。

#### 確認観点

actual.jsonにexpected/pass/summaryがないこと、diff.jsonにexpected/actual/pass/summaryがあること、テストfail時もdiff.jsonが出ること、期待値がExpected JSON側にあること。

#### 作業会話サマリ


##### 依頼 / 方針

このチャットで見えてきた憲法・ルール系の改正概要を、作業単位ごとにインシデントへ追加する。追加原則として、共通化できるものは原則共通化し、やりすぎて将来苦しくなる場合は人間に相談する。古いデータ・不要データは削除して返却するが、削除データはルートの _archive/{削除日時}/ に退避する。ルール系統およびViewDefを修正する場合は、参照元修正を避けるため原則ファイル名を変更しない。

##### AI整理

Test Evidence Rules / Expected-Actual-Diff責務分離 を作業単位として追加する。実装・ルール本文修正は次工程で行い、今回のインシデント追加では対象ファイル・目的・範囲・判断ログを整理する。

##### 追加コメント

今回の作業依頼: incident_file=data/json/01_main/studio_work_incident_data_v0_56_rules_revision_work_items_added.json / phase=v0.14.14-test-evidence-rules-contract。FRB Studio Foundation Rules の foundation_rule_019「GitHub基準ソースとZIP返却契約」を参照し、最新添付資材を使って対応する。

##### AI追加回答

v0.14.14 対応完了。Test Evidence Rules正本として data/json/00_rules/frb_test_evidence_rules_review_data_v0_1.json を新規追加し、Expected JSONは期待値の正本、Actual JSONは観測値のみ、Diff JSONは比較結果、Test Codeは実行する仕掛けとして責務分離を定義。Foundation Rulesへ foundation_rule_021 を追加し、Diff出力後assert、checks[].pass標準、テストコード期待値直書き禁止を明文化した。成果物ZIPから node_modules / tests/.runtime 等のruntime生成物は除外。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0044_001 | 2026-06-27 | user | 憲法・ルール改正候補の作業単位化依頼 | このチャットで見えてきた憲法・ルール系の改正概要を、作業単位ごとにインシデントへ追加する。追加原則として、共通化できるものは原則共通化し、やりすぎて将来苦しくなる場合は人間に相談する。古いデータ・不要データは削除して返却するが、削除データはルートの _archive/{削除日時}/ に退避する。ルール系統およびViewDefを修正する場合は、参照元修正を避けるため原則ファイル名を変更しない。 |
| disc_0044_002 | 2026-06-27 | assistant | 作業単位化方針 | Test Evidence Rules / Expected-Actual-Diff責務分離 として、対象ルールファイル・目的・範囲・リスク・確認観点を整理してインシデントへ追加する。 |
| disc_0044_003 | 2026-06-27 | user | v0.14.14-test-evidence-rules-contract 作業依頼 | 最新添付資材を使い、incident_file と phase に基づいて Test Evidence Rules / Expected-Actual-Diff責務分離をルール本文へ反映する依頼。Foundation Rule 019を参照。 |
| disc_0044_004 | 2026-06-27 | assistant | v0.14.14-test-evidence-rules-contract 作業結果 | Test Evidence Rules正本Data JSONを追加し、Foundation RulesへTest Evidence契約を追加。Expected/Actual/Diff/Test Code責務分離、actual.json禁止項目、diff.json責務、Diff出力後assert、checks[].pass標準を定義した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0044_001 | 2026-06-27 | Expected JSONは期待値の正本とする。 | テストコードへ期待値を直書きすると、Expected JSONを育てる文化が死ぬため。 |
| dec_0044_002 | 2026-06-27 | Actual JSONは観測値のみを持つ。 | 実行時に観測した事実と比較結果を混ぜないため。 |
| dec_0044_003 | 2026-06-27 | Diff JSONは比較結果を持つ。 | Studioくんで判定・差分・失敗サマリを見る正本を明確にするため。 |
| dec_0044_004 | 2026-06-27 | テストはfailしてよいが、Diffは必ず残す。 | AI駆動開発では失敗そのものより、失敗を追体験できる証跡が重要なため。 |
| dec_0044_005 | 2026-06-27 | Test Evidence Rulesは専用Data JSONとして新規追加し、Foundation Rulesには契約への入口を追加する。 | テスト証跡の詳細ルールをFoundation Rulesへ全部詰め込むと肥大化するため、詳細はドメイン別Rules Dataへ分離し、Foundationは上位契約を保持する。 |
| dec_0044_006 | 2026-06-27 | 今回の作業では個別テストコードの全面修正は行わない。 | v0.14.14の目的はルール契約の正本化であり、既存テスト実装の全面移行は別インシデントで扱うため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0044_001 | 2026-06-27 | incident_added | Expected/Actual/Diff責務分離が実装メモにはあるが、ルール改正作業として独立していなかった。 | studio_work_0044 としてTest Evidence Rules作業を追加。 | 今回のチャットでテスト証跡文化の中核ルールが確定したため。 |
| chg_0044_002 | 2026-06-27 | rules_data_added | Expected / Actual / Diff / Test Code責務分離の詳細ルールDataが存在しなかった。 | data/json/00_rules/frb_test_evidence_rules_review_data_v0_1.json を追加。 | Expected/Actual/Diff責務分離を、MarkdownメモではなくData JSON原本としてレビュー・運用できるようにするため。 |
| chg_0044_003 | 2026-06-27 | foundation_rules_update | Foundation Rules上にTest Evidence契約の入口がなかった。 | foundation_rule_021としてTest Evidence / Expected-Actual-Diff責務分離契約を追加。 | Foundation Rulesからテスト証跡の基本契約へ辿れるようにするため。 |

### v0.14.15-test-folder-archive-runtime-policy: Folder / Archive Rules 03_tests正本・旧パス削除・Runtime生成物隔離
- 作業ID: studio_work_0045
- 種別: rules_review
- 分類: folder_policy
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: data/json/00_rules/frb_studio_foundation_review_data_v0_1_github_fetch_urls_added.json, data/json/00_rules/frb_test_evidence_rules_review_data_v0_1.json, data/json/00_rules/_json_creation_prompt.md, tests/tools/cleanup_runtime_artifacts.ps1, .gitignore, playwright.config.ts, data/json/03_tests/notes/TEST_FOLDER_ARCHIVE_RUNTIME_POLICY_NOTES_v0_1.md

#### 目的

テスト証跡の正本フォルダー、旧パス削除、_archive退避、Playwright runtime生成物隔離、root直下に生成物を生やさない方針を整理する。

#### 背景

screen_state_smoke_001 と incident_prompt_copy_action の整理で、data/json/03_tests 配下へ証跡を集約する方針が固まった。同時に tests_screen_state / test-results / playwright-report / 旧QAパスが混乱源になった。

#### 対象範囲

Studioくんで見るテスト証跡は data/json/03_tests/{domain}/{suite_id}/ に集約する。test_patterns/expected/actual/diff/relations/summary/notes をテスト単位で持つ。テストコードは tests/ 配下、runtime一時生成物は tests/.runtime/ 配下へ隔離する。旧パスは成果物から削除し、必要なら_archiveへ退避する。

追加方針として、テストコードはコード実行言語ごとに1つの共通ランナーへ寄せることを基本とする。新しいテストケースは、まずTest Pattern JSON / Expected JSONの追加で対応し、ケースごとにテストコードファイルを増やさない。過剰共通化により将来苦しくなる場合は人間へ相談する。

#### 対象外

Diff Resultの詳細スキーマや共通ViewDef設計は別作業とする。ここでは置き場所と削除/隔離のルールに集中する。

#### 固定名方針

ルール系ファイルおよびViewDefは、既存参照を壊さないため原則として同じファイル名のまま更新する。新しい正本世代を作る必要がある場合は、人間に確認してからファイル名変更する。

#### module化方針

type="module" 化は今回の主目的ではない。ルールData / ルールMD / ViewDef / インシデント管理JSONの作業単位整理を対象とする。

#### リスク

旧パスを残すと、ファイルが出ていないのではなく別の旧フォルダーを見ていたという誤認が起きる。runtime生成物をZIPに混ぜるとWindowsパス長エラーやノイズが発生する。

#### 確認観点

data/json/03_tests配下に証跡が集約されること。tests_screen_stateや旧QAパスが正本扱いされないこと。Playwright生成物がroot直下や成果物ZIPに入らないこと。

#### 作業会話サマリ


##### 依頼 / 方針

このチャットで見えてきた憲法・ルール系の改正概要を、作業単位ごとにインシデントへ追加する。追加原則として、共通化できるものは原則共通化し、やりすぎて将来苦しくなる場合は人間に相談する。古いデータ・不要データは削除して返却するが、削除データはルートの _archive/{削除日時}/ に退避する。ルール系統およびViewDefを修正する場合は、参照元修正を避けるため原則ファイル名を変更しない。

##### AI整理

Folder / Archive Rules 03_tests正本・旧パス削除・Runtime生成物隔離 を作業単位として追加する。実装・ルール本文修正は次工程で行い、今回のインシデント追加では対象ファイル・目的・範囲・判断ログを整理する。

##### 追加コメント

今回の作業依頼: v0.14.15-test-folder-archive-runtime-policy。Foundation Rules の foundation_rule_019「GitHub基準ソースとZIP返却契約」を参照し、最新添付資材を使用する。今後方針として「テストコードは、コード実行言語毎（Ex.JSとplaywright）に1ファイルでテスト実行できるよう共通化に努めていくことを基本とする。」というルールも合わせて追加する。

##### AI追加回答

v0.14.15-test-folder-archive-runtime-policy 対応完了。Foundation Rulesに foundation_rule_022「Test Folder / Archive / Runtime生成物隔離契約」を追加し、foundation_rule_019にもZIP返却契約として03_tests正本・runtime生成物除外・実行言語ごとのテストコード共通化を追記。Test Evidence Rulesには test_evidence_rule_010「テスト証跡フォルダーは03_tests配下に集約する」と test_evidence_rule_011「テストコードは実行言語ごとの共通ランナーへ寄せる」を追加。_json_creation_prompt.md に実務チェックを追加し、cleanup_runtime_artifacts.ps1 / .gitignore / playwright.config.ts / 03_tests notes を整備。成果物ZIPから tests/.runtime などruntime生成物は除外した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0045_001 | 2026-06-27 | user | 憲法・ルール改正候補の作業単位化依頼 | このチャットで見えてきた憲法・ルール系の改正概要を、作業単位ごとにインシデントへ追加する。追加原則として、共通化できるものは原則共通化し、やりすぎて将来苦しくなる場合は人間に相談する。古いデータ・不要データは削除して返却するが、削除データはルートの _archive/{削除日時}/ に退避する。ルール系統およびViewDefを修正する場合は、参照元修正を避けるため原則ファイル名を変更しない。 |
| disc_0045_002 | 2026-06-27 | assistant | 作業単位化方針 | Folder / Archive Rules 03_tests正本・旧パス削除・Runtime生成物隔離 として、対象ルールファイル・目的・範囲・リスク・確認観点を整理してインシデントへ追加する。 |
| disc_0045_003 | 2026-06-27 | user | v0.14.15作業依頼 | 今回の作業依頼: v0.14.15-test-folder-archive-runtime-policy。Foundation Rules の foundation_rule_019「GitHub基準ソースとZIP返却契約」を参照し、最新添付資材を使用する。今後方針として「テストコードは、コード実行言語毎（Ex.JSとplaywright）に1ファイルでテスト実行できるよう共通化に努めていくことを基本とする。」というルールも合わせて追加する。 |
| disc_0045_004 | 2026-06-27 | assistant | v0.14.15作業結果 | v0.14.15-test-folder-archive-runtime-policy 対応完了。Foundation Rulesに foundation_rule_022「Test Folder / Archive / Runtime生成物隔離契約」を追加し、foundation_rule_019にもZIP返却契約として03_tests正本・runtime生成物除外・実行言語ごとのテストコード共通化を追記。Test Evidence Rulesには test_evidence_rule_010「テスト証跡フォルダーは03_tests配下に集約する」と test_evidence_rule_011「テストコードは実行言語ごとの共通ランナーへ寄せる」を追加。_json_creation_prompt.md に実務チェックを追加し、cleanup_runtime_artifacts.ps1 / .gitignore / playwright.config.ts / 03_tests notes を整備。成果物ZIPから tests/.runtime などruntime生成物は除外した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0045_001 | 2026-06-27 | テスト証跡の正本は data/json/03_tests/{domain}/{suite_id}/ とする。 | Expected/Actual/Diff/TestPattern/Relationsをテスト単位で追いやすくするため。 |
| dec_0045_002 | 2026-06-27 | テストコードは tests/ 配下へ置く。 | 実行する仕掛けとStudioくんで見るData JSONを分離するため。 |
| dec_0045_003 | 2026-06-27 | runtime生成物は tests/.runtime/ へ隔離し、成果物ZIPに含めない。 | Playwright出力や添付ファイルがWindows解凍エラー・ノイズ・誤認の原因になるため。 |
| dec_0045_004 | 2026-06-27 | 旧パスフォルダーは成果物から削除し、必要なら_archiveへ退避する。 | 旧パスが存在すると空フォルダーでも正本に見えるため。 |
| dec_0045_005 | 2026-06-27 | テストコードは、コード実行言語ごとに1つの共通ランナーへ寄せることを基本とする。 | テストケースごとにコードファイルを増やすと、Expected JSONを正本として育てる文化が弱まり、テストコード側へ期待値や分岐が肥大化するため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0045_001 | 2026-06-27 | incident_added | 03_tests正本化、旧パス削除、runtime隔離が個別対応の履歴に留まっていた。 | studio_work_0045 としてFolder/Archive Rules作業を追加。 | 今後のテスト追加時に同じ混乱を繰り返さないため。 |
| chg_0045_002 | 2026-06-27 | rules_update | 03_tests正本、runtime生成物隔離、実行言語ごとのテストコード共通化がルール本文へ未反映だった。 | Foundation Rules / Test Evidence Rules / _json_creation_prompt.md にv0.14.15ルールを追加し、cleanupスクリプト・.gitignore・playwright.config.ts・03_tests notes を整備。 | 旧パス罠フォルダー、root直下runtime生成物、テストコード増殖を防ぐため。 |

### v0.14.16-diff-result-common-format-rules: Diff Result Common Format / diff_result_v0_1共通サマリ定義
- 作業ID: studio_work_0046
- 種別: rules_review
- 分類: diff_result_format
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: data/json/00_rules/frb_diff_result_format_rules_data_v0_1.json, data/json/00_rules/frb_foundation_rules_data_v0_1.json, data/json/00_rules/frb_test_evidence_rules_data_v0_1.json, data/json/00_rules/_json_creation_prompt.md, data/json/01_main/studio_work_incident_data_v0_59_future_incident_filename_aligned.json

#### 目的

QA Diff と Screen State Diff を同じViewDefで見られる方向へ寄せるため、diff_result_v0_1 の共通サマリ・checks[]共通フィールドをルール化する。

#### 背景

Step 4-BでQA DiffとScreen State Diffのサマリ項目を揃えた。次のStep 5で共通ViewDef化する前に、Diff Resultの共通フォーマットをルールとして定義しておく必要がある。

#### 対象範囲

diff.jsonの上部サマリ項目として schema_version/document_type/domain/diff_kind/test_id/status/resultLabel/summary/total/passCount/failCount/failedCount/failedCheckIds/firstFailure を標準化する。checks[]は check_id/name/target/type/expected/actual/missing/pass/message を基本とする。

#### 対象外

Actual JSONやExpected JSONの詳細ルールは別作業。ここではdiff.jsonの比較結果フォーマットに限定する。

#### 固定名方針

ルール系ファイルおよびViewDefは、既存参照を壊さないため原則として同じファイル名のまま更新する。新しい正本世代を作る必要がある場合は、人間に確認してからファイル名変更する。

#### module化方針

type="module" 化は今回の主目的ではない。ルールData / ルールMD / ViewDef / インシデント管理JSONの作業単位整理を対象とする。

#### リスク

フォーマットを固定しすぎるとドメイン固有の差分情報を持ちにくくなる。一方で緩すぎると共通ViewDef化できないため、共通項目＋ドメイン拡張領域のバランスが必要。

#### 確認観点

QA DiffとScreen State Diffの両方が共通サマリで読めること。checks[].passが判定フィールドとして使えること。firstFailureから初回失敗が読めること。

#### 作業会話サマリ


##### 依頼 / 方針

このチャットで見えてきた憲法・ルール系の改正概要を、作業単位ごとにインシデントへ追加する。追加原則として、共通化できるものは原則共通化し、やりすぎて将来苦しくなる場合は人間に相談する。古いデータ・不要データは削除して返却するが、削除データはルートの _archive/{削除日時}/ に退避する。ルール系統およびViewDefを修正する場合は、参照元修正を避けるため原則ファイル名を変更しない。

##### AI整理

Diff Result Common Format / diff_result_v0_1共通サマリ定義 を作業単位として追加する。実装・ルール本文修正は次工程で行い、今回のインシデント追加では対象ファイル・目的・範囲・判断ログを整理する。

##### 追加コメント

最新資材を添付。v0.14.16-diff-result-common-format-rules として、Diff Result共通フォーマットをルール化する作業を依頼。Foundation Rules raw URLは frb_foundation_rules_data_v0_1.json を参照する。

##### AI追加回答

v0.14.16-diff-result-common-format-rules 対応完了。frb_diff_result_format_rules_data_v0_1.json を新規追加し、diff_result_v0_1の上部サマリ、checks[]標準項目、checks[].pass判定、互換項目とドメイン拡張の扱いを定義。Foundation Rulesへfoundation_rule_023、Test Evidence Rulesへtest_evidence_rule_012を追加し、_json_creation_prompt.mdにもDiff生成時チェックを追記した。actual.jsonは対象外のため修正なし。既存diff.json本体も今回はルール化のみで変更なし。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0046_001 | 2026-06-27 | user | 憲法・ルール改正候補の作業単位化依頼 | このチャットで見えてきた憲法・ルール系の改正概要を、作業単位ごとにインシデントへ追加する。追加原則として、共通化できるものは原則共通化し、やりすぎて将来苦しくなる場合は人間に相談する。古いデータ・不要データは削除して返却するが、削除データはルートの _archive/{削除日時}/ に退避する。ルール系統およびViewDefを修正する場合は、参照元修正を避けるため原則ファイル名を変更しない。 |
| disc_0046_002 | 2026-06-27 | assistant | 作業単位化方針 | Diff Result Common Format / diff_result_v0_1共通サマリ定義 として、対象ルールファイル・目的・範囲・リスク・確認観点を整理してインシデントへ追加する。 |
| disc_0046_003 | 2026-06-27 | user | v0.14.16作業依頼 | 最新資材を添付し、v0.14.16-diff-result-common-format-rules の対応を依頼。Diff Result Common Format / diff_result_v0_1共通サマリ定義をルール化する。 |
| disc_0046_004 | 2026-06-27 | assistant | v0.14.16作業結果 | frb_diff_result_format_rules_data_v0_1.jsonを新規追加し、Foundation Rules / Test Evidence Rules / _json_creation_prompt.md / インシデントJSONを更新。Diff Resultの正本項目、checks[].pass、failedCount/failedCheckIds/firstFailureをルール化した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0046_001 | 2026-06-27 | Diff Resultのdocument_typeは diff_result を標準とする。 | QA/Screen Stateなどドメインを超えて同じ比較結果ViewDefで扱いやすくするため。 |
| dec_0046_002 | 2026-06-27 | Diff明細の判定フィールドは checks[].pass とする。 | passed/ok/resultなどの別名を増やすと強調表示・比較・ViewDefが分岐するため。 |
| dec_0046_003 | 2026-06-27 | failedCount / failedCheckIds / firstFailure を共通サマリとして持つ。 | 失敗の有無と初回失敗を上部フォームで即確認できるようにするため。 |
| dec_0046_004 | 2026-06-27 | ドメイン固有情報は共通項目を壊さず拡張項目として持つ。 | 共通化と将来拡張性を両立するため。 |
| dec_0046_005 | 2026-06-27 | Diff Result Format Rulesは新規Data JSONとして frb_diff_result_format_rules_data_v0_1.json に分離する。 | Test Evidence Rulesに埋め込みすぎると、Diff Resultのフォーマット規約が太り、Step 5の共通ViewDef化時に参照しづらくなるため。 |
| dec_0046_006 | 2026-06-27 | 既存diff.json本体は今回修正せず、ルール化と入口追加に限定する。 | Step 4-Bで既にQA DiffとScreen State Diffの共通化は実施済みであり、今回はルール正本化が目的のため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0046_001 | 2026-06-27 | incident_added | diff_result_v0_1の共通フォーマットが実装成果物として存在するが、ルール作業として独立していなかった。 | studio_work_0046 としてDiff Result Common Format Rules作業を追加。 | Step 5の共通ViewDef化へ進む前に、Data契約を明文化するため。 |
| chg_0046_002 | 2026-06-27 | rules_data_added | Diff Result共通フォーマットのルール正本が存在しなかった。 | data/json/00_rules/frb_diff_result_format_rules_data_v0_1.json を新規追加。diff_result_v0_1サマリ、checks[]標準項目、pass判定、互換項目、拡張方針を定義。 | QA DiffとScreen State Diffを同じViewDefで見るためのData契約を明文化するため。 |
| chg_0046_003 | 2026-06-27 | rules_link_added | Foundation Rules / Test Evidence RulesからDiff Result Format Rulesへの入口がなかった。 | foundation_rule_023 と test_evidence_rule_012 を追加し、frb_diff_result_format_rules_data_v0_1.json を参照するようにした。 | 上位憲法とテスト証跡ルールから、Diff Result共通フォーマット正本へ辿れるようにするため。 |

### v0.14.17-viewdef-generation-common-viewdef-policy: ViewDef Generation Rules 共通ViewDef優先・既存ファイル名維持・pass標準化
- 作業ID: studio_work_0047
- 種別: rules_review
- 分類: viewdef_generation_rules
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json, FRB_VIEW_DEF_GENERATION_RULES_ALL_v0_16.md, defs/**/*.json

#### 目的

ViewDef生成時に、共通化できるViewDefは共通化を検討し、既存ViewDef修正時は原則ファイル名を変えず、Diff系明細判定はchecks[].passへ寄せるルールを整理する。

#### 背景

Actual Resultの強調表示不一致で、JSを広げるのではなくData/ViewDef契約を揃えるべきという判断があった。また、ViewDefファイル名を変更するとData側view_def参照修正が連鎖することが明確になった。

#### 対象範囲

既存ViewDefを修正する場合はファイル名を変えない。Diff Result / Actual Observation / Expected Checksなど複数ドメインで同じ構造を持てるものは、個別ViewDefを増やす前に共通ViewDef化を検討する。やりすぎる場合は人間へ相談する。

#### 対象外

実際の共通Diff Result ViewDef作成はStep 5で扱う。この作業は生成ルール・設計方針の整備に限定する。

#### 固定名方針

ルール系ファイルおよびViewDefは、既存参照を壊さないため原則として同じファイル名のまま更新する。新しい正本世代を作る必要がある場合は、人間に確認してからファイル名変更する。

#### module化方針

type="module" 化は今回の主目的ではない。ルールData / ルールMD / ViewDef / インシデント管理JSONの作業単位整理を対象とする。

#### リスク

共通ViewDefを増やしすぎるとドメイン別の読みやすさが落ちる。逆に個別ViewDefを増やしすぎると同じ構造なのに保守箇所が分散する。

#### 確認観点

既存Dataのview_def参照が壊れないこと。新規Diff系ViewDefでpassedではなくpassを使うこと。共通化判断で人間相談条件が明記されていること。

#### 作業会話サマリ


##### 依頼 / 方針

このチャットで見えてきた憲法・ルール系の改正概要を、作業単位ごとにインシデントへ追加する。追加原則として、共通化できるものは原則共通化し、やりすぎて将来苦しくなる場合は人間に相談する。古いデータ・不要データは削除して返却するが、削除データはルートの _archive/{削除日時}/ に退避する。ルール系統およびViewDefを修正する場合は、参照元修正を避けるため原則ファイル名を変更しない。

##### AI整理

ViewDef Generation Rules 共通ViewDef優先・既存ファイル名維持・pass標準化 を作業単位として追加する。実装・ルール本文修正は次工程で行い、今回のインシデント追加では対象ファイル・目的・範囲・判断ログを整理する。

##### 追加コメント

最新資材に対して v0.14.17-viewdef-generation-common-viewdef-policy の対応を依頼。Foundation Rules raw URLは frb_foundation_rules_data_v0_1.json を参照し、foundation_rule_019 のZIP返却契約に従う。

##### AI追加回答

v0.14.17対応完了。frb_viewdef_generation_rules_data_v0_1.json に viewdef_rule_25 系として共通ViewDef優先・既存ViewDefファイル名維持・Diff系checks[].pass標準化を追加。_json_creation_prompt.md にAI実務チェックを追記。実際の共通Diff Result ViewDef作成はStep 5の対象として残した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0047_001 | 2026-06-27 | user | 憲法・ルール改正候補の作業単位化依頼 | このチャットで見えてきた憲法・ルール系の改正概要を、作業単位ごとにインシデントへ追加する。追加原則として、共通化できるものは原則共通化し、やりすぎて将来苦しくなる場合は人間に相談する。古いデータ・不要データは削除して返却するが、削除データはルートの _archive/{削除日時}/ に退避する。ルール系統およびViewDefを修正する場合は、参照元修正を避けるため原則ファイル名を変更しない。 |
| disc_0047_002 | 2026-06-27 | assistant | 作業単位化方針 | ViewDef Generation Rules 共通ViewDef優先・既存ファイル名維持・pass標準化 として、対象ルールファイル・目的・範囲・リスク・確認観点を整理してインシデントへ追加する。 |
| disc_0047_003 | 2026-06-27 | user | v0.14.17作業依頼 | 最新資材を添付し、v0.14.17-viewdef-generation-common-viewdef-policy の対応を依頼。共通ViewDef優先・既存ファイル名維持・pass標準化をViewDef Generation Rulesへ反映する。 |
| disc_0047_004 | 2026-06-27 | assistant | v0.14.17対応結果 | ViewDef Generation Rulesにviewdef_rule_25系を追加し、共通ViewDef優先・過剰共通化時の人間相談・既存ViewDefファイル名維持・Diff系checks[].pass標準化を明文化。_json_creation_prompt.mdにも短い実務チェックを追記した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0047_001 | 2026-06-27 | 既存ViewDef修正時は原則ファイル名を変更しない。 | Data JSON側view_def参照、URL起動、AIプロンプトの接続キーを壊さないため。 |
| dec_0047_002 | 2026-06-27 | 共通化できるViewDefは共通化を検討する。 | 同じ構造の表示をドメイン別に増やすと、修正・強調表示・AIレビューの保守が分散するため。 |
| dec_0047_003 | 2026-06-27 | 共通化で将来苦しくなる場合は人間に相談する。 | 表示項目の意味が薄まる共通化は、短期的には楽でも長期的に保守しづらくなるため。 |
| dec_0047_004 | 2026-06-27 | Diff系ViewDefではchecks[].passを判定フィールドとして扱う。 | 既存の強調表示・差分表示との互換性を優先するため。 |
| dec_0047_005 | 2026-06-27 | ViewDef生成時は、個別ViewDefを増やす前に共通ViewDef化を検討する。 | Diff Result / Actual Observation / Expected Checksなど、同じ構造を複数ドメインで読む可能性があるため。 |
| dec_0047_006 | 2026-06-27 | 既存ViewDefの修正では、原則として同じファイル名を維持する。 | Data JSONのview_def参照、URL起動、インベントリ、過去インシデントの参照切れを防ぐため。 |
| dec_0047_007 | 2026-06-27 | Diff系ViewDefの判定フィールドはchecks[].passを正本とする。 | 既存強調表示とDiff Result共通フォーマットを揃え、passed/ok/resultの乱立を防ぐため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0047_001 | 2026-06-27 | incident_added | ViewDef共通化・ファイル名維持・pass標準化が個別会話で見えていたが、ViewDef生成ルール作業として独立していなかった。 | studio_work_0047 としてViewDef Generation Rules改正作業を追加。 | Step 5の共通Diff Result ViewDef化を安全に進めるため。 |
| chg_0047_002 | 2026-06-27 | rules_update | frb_viewdef_generation_rules_data_v0_1.json では、共通ViewDef優先・既存ViewDefファイル名維持・Diff系checks[].pass標準化が独立した生成ルールとして明文化されていなかった。 | viewdef_rule_25 / 25_01 / 25_02 / 25_03 / 25_04 を追加し、共通ViewDef判断基準・人間相談条件・同名更新原則・pass標準化を明文化した。 | Step 5のDiff Result共通ViewDef化を、安全に進めるための生成ルールを先に整備するため。 |
| chg_0047_003 | 2026-06-27 | prompt_update | _json_creation_prompt.md に、ViewDef生成時の共通ViewDef優先・同名更新・checks[].pass標準化の短い実務指示がなかった。 | v0.14.17追加ルールとして、共通ViewDef化検討、過剰共通化時の人間相談、既存ViewDefファイル名維持、Diff系checks[].pass標準化を追記した。 | AIへViewDef生成を依頼する際に、長いルール本文を読まなくても最低限の実務チェックを実行できるようにするため。 |

### v0.14.18-delivery-cleanup-zip-safety-policy: Delivery / Cleanup Rules 成果物ZIP安全化・不要生成物除外
- 作業ID: studio_work_0048
- 種別: rules_review
- 分類: delivery_cleanup
- 優先度: medium
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: data/json/00_rules/frb_coding_constraints_data_v0_3.json, data/json/00_rules/_json_creation_prompt.md, .gitignore, tests/tools/cleanup_runtime_artifacts.ps1

#### 目的

AIが成果物を返却する際に、node_modulesやPlaywright生成物、長大パスのテスト結果を混ぜず、Windowsで安全に解凍できるZIPを返すルールを整理する。

#### 背景

v0.14.8でPlaywrightのtest-resultsをZIPへ混ぜてしまい、Windows解凍時にパス長エラーが発生した。成果物とruntime生成物の分離を返却ルールとして固定する必要がある。

#### 対象範囲

成果物ZIPには node_modules / playwright-report / test-results / test_results / tests/.runtime / tests_screen_state を含めない。古いフォルダーや不要データは削除し、必要なら_archiveへ退避する。ZIP作成前に最長パスと不要生成物を確認する。

#### 対象外

アプリ実装やテスト仕様そのものは対象外。返却物の清掃・除外・安全性チェックに限定する。

#### 固定名方針

ルール系ファイルおよびViewDefは、既存参照を壊さないため原則として同じファイル名のまま更新する。新しい正本世代を作る必要がある場合は、人間に確認してからファイル名変更する。

#### module化方針

type="module" 化は今回の主目的ではない。ルールData / ルールMD / ViewDef / インシデント管理JSONの作業単位整理を対象とする。

#### リスク

除外しすぎると必要な正本Dataまで落とす危険がある。逆に除外が甘いと解凍エラー、巨大ZIP、旧パス混入、node_modules混入が再発する。

#### 確認観点

ZIP内にnode_modulesやtest-resultsが含まれていないこと。旧パス罠フォルダーが含まれていないこと。Windows解凍でパス長エラーが出ないこと。正本Data/ViewDefは残っていること。

#### 作業会話サマリ


##### 依頼 / 方針

このチャットで見えてきた憲法・ルール系の改正概要を、作業単位ごとにインシデントへ追加する。追加原則として、共通化できるものは原則共通化し、やりすぎて将来苦しくなる場合は人間に相談する。古いデータ・不要データは削除して返却するが、削除データはルートの _archive/{削除日時}/ に退避する。ルール系統およびViewDefを修正する場合は、参照元修正を避けるため原則ファイル名を変更しない。

##### AI整理

Delivery / Cleanup Rules 成果物ZIP安全化・不要生成物除外 を作業単位として追加する。実装・ルール本文修正は次工程で行い、今回のインシデント追加では対象ファイル・目的・範囲・判断ログを整理する。

##### 追加コメント

v0.14.18-delivery-cleanup-zip-safety-policy 対応依頼。既に一部ルール改正されている可能性を踏まえつつ、Foundation Rules foundation_rule_019 のZIP返却契約を参照し、成果物ZIP安全化・不要生成物除外ルールを反映する。

##### AI追加回答

v0.14.18対応完了。既存のv0.14.15 Test Folder / Runtime生成物隔離ルールを踏まえ、foundation_rule_019 と constitution_20、_json_creation_prompt.md にDelivery/Cleanup/ZIP安全返却チェックを補強。root .gitignoreを追加し、node_modules/Playwright生成物/tests/.runtime/tests_screen_stateを成果物ZIPへ含めない方針を明示。cleanup_runtime_artifacts.ps1もv0.14.18方針に合わせて更新し、証跡正本 data/json/03_tests は削除対象にしないことを明記した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0048_001 | 2026-06-27 | user | 憲法・ルール改正候補の作業単位化依頼 | このチャットで見えてきた憲法・ルール系の改正概要を、作業単位ごとにインシデントへ追加する。追加原則として、共通化できるものは原則共通化し、やりすぎて将来苦しくなる場合は人間に相談する。古いデータ・不要データは削除して返却するが、削除データはルートの _archive/{削除日時}/ に退避する。ルール系統およびViewDefを修正する場合は、参照元修正を避けるため原則ファイル名を変更しない。 |
| disc_0048_002 | 2026-06-27 | assistant | 作業単位化方針 | Delivery / Cleanup Rules 成果物ZIP安全化・不要生成物除外 として、対象ルールファイル・目的・範囲・リスク・確認観点を整理してインシデントへ追加する。 |
| disc_0048_002 | 2026-06-27 | user | v0.14.18 Delivery/Cleanup作業依頼 | 最新資材を添付し、v0.14.18-delivery-cleanup-zip-safety-policy の対応を依頼。既に一部ルール改正されている気もするが、Foundation Rules foundation_rule_019を参照して進める。 |
| disc_0048_003 | 2026-06-27 | assistant | v0.14.18 Delivery/Cleanup対応結果 | 既存のv0.14.15 runtime生成物隔離方針を重複させすぎないようにしつつ、返却前チェック・ZIP除外リスト・Windows長大パス安全性・cleanupスクリプト運用を明文化。Foundation Rules / Coding Constraints / _json_creation_prompt.md / .gitignore / cleanup script / report MD / incident JSONを更新した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0048_001 | 2026-06-27 | 成果物ZIPにruntime生成物を含めない。 | 一時ファイルは再生成可能であり、成果物に混ぜるとノイズと解凍エラーの原因になるため。 |
| dec_0048_002 | 2026-06-27 | ZIP返却前に不要生成物と旧パスを確認する。 | 旧パスや空フォルダーが残ると、正本誤認・未出力誤認が起きるため。 |
| dec_0048_003 | 2026-06-27 | Windows解凍安全性を意識して長大パスを含めない。 | ユーザー環境で解凍できない成果物は実用できないため。 |
| dec_0048_004 | 2026-06-27 | 削除対象は必要に応じて_archiveへ退避する。 | 完全削除ではなく追跡可能な削除にするため。 |
| dec_0048_004 | 2026-06-27 | v0.14.18では新しい証跡構造を増やさず、成果物ZIP返却安全性とcleanup運用を補強する。 | v0.14.15で03_tests正本・tests/.runtime隔離は既に定義済みのため、今回は重複した構造定義ではなく返却前チェックとZIP除外契約を明確化するのが安全なため。 |
| dec_0048_005 | 2026-06-27 | runtime生成物はarchive退避ではなく、原則として削除・ZIP除外する。 | node_modules、Playwright report/test-results、tests/.runtimeは再生成可能な一時生成物であり、archiveへ収録するとZIP肥大化・長大パス・誤参照の原因になるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0048_001 | 2026-06-27 | incident_added | ZIP返却安全性とcleanup方針が個別事故対応に留まっていた。 | studio_work_0048 としてDelivery/Cleanup Rules作業を追加。 | 同じWindows解凍エラーや生成物混入を再発させないため。 |
| chg_0048_002 | 2026-06-27 | rules_update | 成果物ZIP返却時の不要生成物除外はv0.14.15で一部定義済みだったが、返却前チェック・Windows長大パス確認・cleanupスクリプト運用が作業依頼用プロンプトと憲法に十分まとまっていなかった。 | foundation_rule_019、constitution_20、_json_creation_prompt.mdへv0.14.18のDelivery/Cleanup/ZIP安全返却チェックを追加。 | 成果物ZIPにruntime生成物や長大パスが混入する事故を再発させないため。 |
| chg_0048_003 | 2026-06-27 | delivery_tooling_update | root .gitignore がなく、cleanup_runtime_artifacts.ps1 は基本的な削除対象のみ定義していた。 | root .gitignoreを追加し、runtime生成物除外対象を明示。cleanup_runtime_artifacts.ps1にv0.14.18方針コメント、削除後確認、証跡正本を触らない注意を追加。 | AIや人間が成果物ZIP作成時に不要生成物を混入させないため。 |

### v0.14.19-rule-review-status-responsibility-issue: Rule Review承認/確認状態の単一正本化と責務整理
- 作業ID: studio_work_0049
- 種別: open_issue
- 分類: rule_review_workflow
- 優先度: high
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: data/json/00_rules/frb_*_data_v*.json（frb_view_def_schema_review_data_v0_1.json は必要時のみ別扱い）, data/json/00_rules/frb_test_evidence_rules_data_v0_1.json, data/json/00_rules/frb_coding_constraints_data_v0_3.json, data/json/00_rules/frb_foundation_rules_data_v0_1.json, defs/rules/rule_review_common_view_def_*.json, rules/studio_work_incident_view_def_*.json

#### 目的

Rule Review系データにおける review_status / verification_status / approval_decision の意味、単一正本、UI上の表示・操作責務、人間とAIの権限範囲を整理する。特に、AIがルール本文・章・要約・分類などを修正した場合に、その章またはルール行が未承認・未確認・未レビューへ戻るべきかを運用ルールとして定義する。

#### 背景

Test Evidence Rulesレビュー画面で、上部詳細欄・グリッド・確認メッセージカードに承認/確認状態が複数表示され、どれが正本か分かりにくい状態が見えた。現状は同じフィールドを複数UIで表示している可能性が高いが、運用として『AIが修正したものをAIが承認済みにしてよいのか』『確認状態と承認は二つ必要か』『人間が判断する欄とAIが更新する欄の境界はどこか』が未整理である。

#### 対象範囲

承認状態・確認状態・レビュー状態の意味を整理する。グリッド/上部詳細/確認メッセージカードが同じ正本フィールドを表示しているか確認する。AIがルール本文や章を修正した場合のステータスリセットルールを定義する。人間が最終承認する項目と、AIが作業都合で更新してよい項目を分離する。verification_status と approval_decision の両方が必要か、統合できるかを検討する。

#### 対象外

この作業項目追加時点では、ViewDefやRuntimeの即時修正は行わない。既存データのステータス一括変更もしない。まず懸案として残し、次工程でルール本文・ViewDef・必要ならRuntime動作へ落とし込む。

#### 固定名方針

review_status / verification_status / approval_decision は現時点ではRule Review系Dataの管理フィールド候補として扱う。ただし、同じ意味の状態を複数フィールドへ重複保持しない。グリッド・上部詳細・確認カードは、同じ正本フィールドを表示/編集するUIであり、別々の状態を保持してはいけない。

#### module化方針

type="module" 化は今回の主目的ではない。データ契約・運用ルール・ViewDef表示方針の整理を対象とする。

#### リスク

AIが修正したルールを承認済みのまま残すと、人間未確認の内容が正本化されるリスクがある。逆に状態項目を増やしすぎると、未レビュー/未確認/未承認の違いが分からなくなり、レビュー運用が重くなる。UI上で同じ状態を複数箇所から編集できる場合、正しくても二重管理に見えて人間が不安になる。

#### 確認観点

AIがルール本文を修正した場合に承認/確認/レビュー状態がどう扱われるべきかを確認する。グリッド・上部詳細・確認メッセージカードが同じ正本フィールドを見ていることを確認する。人間だけが最終承認できる状態になっているか確認する。verification_statusとapproval_decisionが二つ必要か、一つに寄せられるかを確認する。

#### 作業会話サマリ


##### 依頼 / 方針

承認欄・確認状態欄の使い分けは一旦懸案としてインシデントに追加したい。特に、ある章をAIが修正したら、その章は未承認状態にならないといけない。また、確認状態欄と承認欄などについて、人間orAIの責務を明確に運用定義する必要がある。二ついるかどうかも含めて、ひとまず懸案として残したい。

##### AI整理

Rule Review承認/確認状態の単一正本化と責務整理を懸案インシデントとして追加する。即時修正ではなく、AI修正時の未承認リセット、人間/AI責務、verification_statusとapproval_decisionの要否を次工程で整理する対象として管理する。

##### 追加コメント

承認欄・確認状態欄の使い分けは一旦懸案としてインシデントに追加したい。AIが章を修正した場合の未承認化、人間/AIの責務、確認状態欄と承認欄が二つ必要かを後で整理したい。

##### AI追加回答

懸案として studio_work_0049 を追加。現時点ではViewDef/Runtime修正は行わず、Rule Reviewステータス運用の設計課題として残す。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0049_001 | 2026-06-27 | user | 承認/確認状態UIの混乱 | Rule Review画面で、上部詳細欄・グリッド・確認メッセージカードに承認/確認状態が見えており、どれをどう使い分けるのか気になった。 |
| disc_0049_002 | 2026-06-27 | assistant | 暫定整理 | グリッド・上部詳細・確認メッセージカードは同じ正本フィールドを見ている想定。ただしUI上は二重管理に見えるため、正本フィールドと操作UIの関係をルール化した方がよいと整理した。 |
| disc_0049_003 | 2026-06-27 | user | 懸案追加依頼 | 一旦懸案としてインシデントに追加したい。AIが章を修正したら、その章は未承認状態にならないといけない。確認状態欄と承認欄などについて、人間orAIの責務を明確に運用定義する必要がある。二ついるかどうかも後で整理したい。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0049_001 | 2026-06-27 | 承認/確認状態の使い分けは、即時修正せず懸案として管理する。 | 単なるUI表示調整ではなく、AI修正時の未承認化と人間/AI責務分担に関わる運用設計課題であるため。 |
| dec_0049_002 | 2026-06-27 | AIがルール本文・章・要約・分類などを修正した場合、対象ルールは少なくとも人間確認待ちへ戻す方向で検討する。 | AIが更新した内容を、人間未確認のまま承認済みとして残すと正本管理の信頼性が落ちるため。 |
| dec_0049_003 | 2026-06-27 | 人間が最終承認する項目と、AIが作業上更新してよい状態項目を分離して定義する。 | AIが作業完了や要レビューを記録することは有用だが、最終承認までAIが担うと承認ワークフローの意味が薄れるため。 |
| dec_0049_004 | 2026-06-27 | verification_status と approval_decision が二つ必要かを検討課題として残す。 | 状態項目が多すぎると運用が重くなり、違いが分からなくなるため。必要性が薄い場合は統合・非表示・readonly化を検討する。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0049_001 | 2026-06-27 | incident_added | Rule Reviewの承認/確認状態の責務とAI修正時の未承認化が作業項目として管理されていなかった。 | studio_work_0049 として、Rule Review承認/確認状態の単一正本化と責務整理を懸案追加。 | ルール系DataをAIが更新する運用が始まったため、承認状態の信頼性と人間/AIの責務境界を明確にする必要がある。 |

### v0.14.20-rules-filename-reference-migration: 00_rulesファイル名変更に伴う参照更新インシデント
- 作業ID: studio_work_0050
- 種別: rules_reference_migration
- 分類: rules_filename_migration
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: data/json/00_rules/_json_creation_prompt.md; data/json/00_rules/frb_foundation_rules_data_v0_1.json; data/json/00_rules/filename_updatelist.md; data/json/01_main/00_do_incident_prompt_temple.md; data/json/01_main/studio_work_incident_data_v0_57_rule_review_status_responsibility_issue_added.json; data/json/05_inventory/defs_data_link_inventory_v0_1.json; data/json/05_inventory/defs_data_link_inventory_v0_2_repaired.json; defs/rules/studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json; defs/rules/tmp/rule_review_common_view_def_v0_1.json; defs/rules/tmp/rule_review_common_view_def_v0_2_editable_review_target.json; defs/relation/relation_axis_constraint_view_def_v0_1.json; defs/relation/relation_axis_test_pattern_view_def_v0_1.json; data/markdown/*.md の生成済みExport/メモ類; data/json/03_tests/qa/v0_14_2_incident_prompt_copy_action/actual/TP-IPC-001.actual.json; data/json/03_tests/qa/v0_14_2_incident_prompt_copy_action/diff/TP-IPC-001.diff.json

#### 目的

00_rules配下のルール系JSONファイル名整理に伴い、旧ファイル名を参照しているツール・ViewDef・インベントリ・作業依頼テンプレート・ルール本文・インシデントJSONを洗い出し、次工程で新ファイル名へ更新するための作業単位を作成する。

#### 背景

filename_updatelist.mdで、frb_studio_foundation_review_data_v0_1_github_fetch_urls_added.json → frb_foundation_rules_data_v0_1.json など、00_rulesの正本ファイル名が短く整理された。これにより、foundation_rule_019のraw URL契約、AI作業依頼テンプレート、_json_creation_prompt.md、ViewDefのAI Prompt targetFile、データ/定義インベントリ、relation系ViewDef、過去インシデント内の参照に旧ファイル名が残る可能性が出た。旧名が残ると、AIやスクリプトが存在しないファイルを取得し、またStudioくん上のリンク・プロンプト・インベントリが古い正本を指すリスクがある。

#### 対象範囲

対象は、現行運用で参照される旧ファイル名を新ファイル名へ更新すること。特に、Foundation Rules raw URL、data/json/01_main/00_do_incident_prompt_temple.md、data/json/00_rules/_json_creation_prompt.md、data/json/00_rules/frb_foundation_rules_data_v0_1.json内の参照、defs/rules系ViewDefのtargetFile/AI Prompt、defs/relation系ViewDefのtargetFileまたは参照Data、data/json/05_inventoryのData/ViewDefリンク一覧を更新対象とする。filename_updatelist.mdは変更履歴として旧名を残してよい。過去の実行証跡・actual/diff・古いインシデントJSONは、履歴として旧名を残すか、新正本参照へ更新するかを次工程で判断する。

変更対比:
- `_frb_view_def_schema_v0_9.json` → `frb_view_def_schema_v0_9.json`
- `ai_constraint_spec_aggregated_v0_6_footer_chat.json` → `frb_constraint_spec_v0_6.json`
- `frb_coding_constraints_review_data_v0_3.json` → `frb_coding_constraints_data_v0_3.json`
- `frb_studio_foundation_review_data_v0_1_github_fetch_urls_added.json` → `frb_foundation_rules_data_v0_1.json`
- `frb_test_evidence_rules_review_data_v0_1.json` → `frb_test_evidence_rules_data_v0_1.json`
- `frb_viewdef_generation_rules_review_data_v0_1.json` → `frb_viewdef_generation_rules_data_v0_1.json`

検出結果:
- `_frb_view_def_schema_v0_9.json` → `frb_view_def_schema_v0_9.json`: 2件 / data/json/00_rules/filename_updatelist.md, data/markdown/filename_updatelist.md
- `ai_constraint_spec_aggregated_v0_6_footer_chat.json` → `frb_constraint_spec_v0_6.json`: 7件 / data/json/00_rules/filename_updatelist.md, data/json/05_inventory/defs_data_link_inventory_v0_1.json, data/json/05_inventory/defs_data_link_inventory_v0_2_repaired.json, data/markdown/constraint_trace_cards_virtual_view_def_v0_1_viewdef.md, data/markdown/filename_updatelist.md, defs/relation/relation_axis_constraint_view_def_v0_1.json, defs/relation/relation_axis_test_pattern_view_def_v0_1.json
- `frb_coding_constraints_review_data_v0_3.json` → `frb_coding_constraints_data_v0_3.json`: 11件 / data/json/00_rules/filename_updatelist.md, data/json/00_rules/_json_creation_prompt.md, data/json/01_main/studio_work_incident_data_v0_55_test_evidence_diff_contract_added.json, data/json/01_main/studio_work_incident_data_v0_56_rules_revision_work_items_added.json, data/json/01_main/studio_work_incident_data_v0_57_rule_review_status_responsibility_issue_added.json, data/json/05_inventory/defs_data_link_inventory_v0_1.json, data/json/05_inventory/defs_data_link_inventory_v0_2_repaired.json, data/markdown/coding_constraints_review_export.md, ...（計11件）
- `frb_studio_foundation_review_data_v0_1_github_fetch_urls_added.json` → `frb_foundation_rules_data_v0_1.json`: 13件 / data/json/00_rules/filename_updatelist.md, data/json/00_rules/frb_foundation_rules_data_v0_1.json, data/json/01_main/00_do_incident_prompt_temple.md, data/json/01_main/studio_work_incident_data_v0_55_test_evidence_diff_contract_added.json, data/json/01_main/studio_work_incident_data_v0_56_rules_revision_work_items_added.json, data/json/01_main/studio_work_incident_data_v0_57_rule_review_status_responsibility_issue_added.json, data/json/03_tests/qa/v0_14_2_incident_prompt_copy_action/actual/TP-IPC-001.actual.json, data/json/03_tests/qa/v0_14_2_incident_prompt_copy_action/diff/TP-IPC-001.diff.json, ...（計13件）
- `frb_test_evidence_rules_review_data_v0_1.json` → `frb_test_evidence_rules_data_v0_1.json`: 6件 / data/json/00_rules/filename_updatelist.md, data/json/00_rules/frb_foundation_rules_data_v0_1.json, data/json/01_main/studio_work_incident_data_v0_56_rules_revision_work_items_added.json, data/json/01_main/studio_work_incident_data_v0_57_rule_review_status_responsibility_issue_added.json, data/markdown/filename_updatelist.md, data/markdown/rule_review_decision_log_export.md
- `frb_viewdef_generation_rules_review_data_v0_1.json` → `frb_viewdef_generation_rules_data_v0_1.json`: 14件 / data/json/00_rules/filename_updatelist.md, data/json/00_rules/frb_foundation_rules_data_v0_1.json, data/json/00_rules/_json_creation_prompt.md, data/json/01_main/studio_work_incident_data_v0_55_test_evidence_diff_contract_added.json, data/json/01_main/studio_work_incident_data_v0_56_rules_revision_work_items_added.json, data/json/01_main/studio_work_incident_data_v0_57_rule_review_status_responsibility_issue_added.json, data/json/05_inventory/defs_data_link_inventory_v0_1.json, data/json/05_inventory/defs_data_link_inventory_v0_2_repaired.json, ...（計14件）

#### 対象外

この作業項目追加時点では、実ファイル参照の置換・コード修正・URL修正は行わない。過去の履歴として意味がある change_history / discussion_history / filename_updatelist.md の旧ファイル名は一律置換しない。test evidence の actual/diff に含まれる旧プロンプト文字列も、証跡として残すべきか判断してから扱う。

#### 固定名方針

ルール系ファイル名は原則として安定名を使う。今後は作業履歴や派生内容をファイル名に残さず、正本名は短く保つ。ファイル名変更が必要な場合は、参照元洗い出し・更新インシデント・旧名archive/互換方針をセットで扱う。

#### module化方針

type="module" 化は今回の対象外。ファイル参照・Data/ViewDefリンク・テンプレート・ルール本文の参照整合を対象とする。

#### リスク

Foundation Rules raw URLや作業依頼テンプレートに旧名が残ると、AIやスクリプトが存在しないファイルを取得する。ViewDefのtargetFileに旧名が残ると、AI依頼プロンプトやMarkdown出力が誤ったファイルを参照する。逆に履歴文字列まで機械的に置換すると、過去の作業経緯や証跡が改ざんされたように見えるリスクがある。

#### 確認観点

grep等で旧ファイル名参照を確認し、filename_updatelist.mdおよび履歴として意図的に残す箇所以外に旧名が残っていないこと。Foundation Rules raw URLが新ファイル名 frb_foundation_rules_data_v0_1.json を指すこと。Studio上で新ファイル名のRules JSONを読み込めること。ViewDefのAI Prompt/targetFileが新正本名を指すこと。Inventoryに旧名と新名のズレがないこと。

#### 作業会話サマリ


##### 依頼 / 方針

ファイル名を変えたことで影響するツール・JSONを洗い出して、それを対応する為のインシデントを作成し、更新後インシデントJSONを返却してほしい。

##### AI整理

00_rulesファイル名変更に伴う旧ファイル名参照をZIP内から検索し、影響範囲を分類した。Foundation Rules raw URL、作業依頼テンプレート、_json_creation_prompt.md、Foundation Rules本文、インベントリ、ViewDef targetFile、relation系ViewDef、過去インシデント/証跡/Markdown Exportに旧名参照が見つかったため、studio_work_0050として参照更新インシデントを追加する。

##### 追加コメント

最新資材を添付。phase v0.14.20-rules-filename-reference-migration として、00_rulesファイル名変更に伴う現行参照の更新を依頼。

##### AI追加回答

v0.14.20-rules-filename-reference-migration 対応完了。Foundation Rules raw URL契約、作業依頼テンプレート、_json_creation_prompt.md、Foundation Rules本文、Inventory、rules/relation系ViewDefの旧ファイル名参照を新ファイル名へ更新。追加で schema 旧派生名 frb_view_def_schema_v0_9_chat_input_mapping.json も現行ファイル frb_view_def_schema_v0_9.json へ補正。filename_updatelist.md、過去インシデント、生成済みExport、test evidence actual/diffは履歴・証跡として旧名を保持。更新レポート FILENAME_REFERENCE_MIGRATION_REPORT_v0_14_20.md を追加。

フォローアップとして、未着手インシデント内に残っていた旧ルールJSON名を新ファイル名へ補正。履歴・完了済みインシデントの旧名は証跡として残した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0050_001 | 2026-06-27 | user | 00_rulesファイル名変更後の影響洗い出し依頼 | 最新資材を添付。ファイル名を変えたことで影響するツール・JSONを洗い出して、それを対応する為のインシデントを作成し、更新後インシデントJSONを返却してほしい。 |
| disc_0050_002 | 2026-06-27 | assistant | 影響洗い出し結果 | filename_updatelist.mdの変更対比に基づき、ZIP内の旧ファイル名参照を検索。Foundation raw URL、作業依頼テンプレート、_json_creation_prompt.md、Foundation Rules本文、インベントリ、ViewDef targetFile、relation系ViewDef、過去インシデント・証跡・Markdown Exportに旧名参照を検出した。履歴として残す箇所と、現行正本参照として更新すべき箇所を分けて対応する必要がある。 |
| disc_0050_002 | 2026-06-27 | user | v0.14.20作業依頼 | 最新資材を添付。00_rulesファイル名変更に伴う参照更新を実施してほしい。 |
| disc_0050_003 | 2026-06-27 | assistant | v0.14.20作業結果 | 現行参照を新ファイル名へ更新。履歴・証跡・filename_updatelist.mdは旧名を残し、更新対象ファイルと判断をレポートへ記録した。 |
| disc_0050_004 | 2026-06-27 | user | 未着手インシデント内の旧名補正依頼 | これからやるインシデントデータの中に古い名前が残っているため、間違い防止として新ファイル名へ補正してほしい。 |
| disc_0050_005 | 2026-06-27 | assistant | 未着手インシデント内の旧名補正結果 | 未着手インシデントのみを対象に、00_rules旧ファイル名を新ファイル名へ補正。完了済みインシデント内の旧名は履歴として保持した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0050_001 | 2026-06-27 | 00_rulesファイル名変更は、参照更新インシデントとして独立管理する。 | ファイル名変更はルール本文だけでなく、raw URL、作業依頼テンプレート、ViewDef targetFile、inventory、テスト証跡、Markdown Exportへ広く影響するため。 |
| dec_0050_002 | 2026-06-27 | 履歴として意味のある旧ファイル名は一律置換しない。 | change_history、discussion_history、filename_updatelist、actual/diff証跡に含まれる旧名は、当時の経緯や証跡として価値があるため、現行参照と履歴参照を分ける必要がある。 |
| dec_0050_003 | 2026-06-27 | 現行のAI/スクリプト取得契約では新ファイル名を正本とする。 | Foundation Rulesの安定名を frb_foundation_rules_data_v0_1.json へ整理したため、今後のraw URL契約と依頼テンプレートは新名へ寄せる必要がある。 |
| dec_0050_004 | 2026-06-27 | filename_updatelist.md と過去証跡は旧名を保持する。 | 変更対比・過去会話・actual/diffは当時の経緯を示す証跡であり、現行参照と区別する必要があるため。 |
| dec_0050_005 | 2026-06-27 | 現行テンプレート・ViewDef・Inventory・Foundation Rules契約は新ファイル名へ移行する。 | AIやスクリプトが参照する入口に旧名が残ると、存在しない正本を読みにいくリスクがあるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0050_001 | 2026-06-27 | incident_added | items_count=49 / 00_rulesファイル名変更に伴う参照更新インシデントなし | items_count=50 / studio_work_0050 v0.14.20-rules-filename-reference-migration を追加 | ファイル名変更に伴う参照元更新を、次工程で漏れなく実施するため。 |
| chg_0050_002 | 2026-06-27 | filename_reference_migration_applied | 現行テンプレート・ViewDef・Inventory・Foundation Rules本文に、00_rules旧ファイル名参照が残っていた。 | 現行運用で使う参照を新ファイル名へ更新し、更新レポートを追加。履歴として意味のある旧名は保持。 | ファイル名整理後もAI/スクリプト/Studio ViewDefが新しい正本を参照できるようにするため。 |
| chg_0050_003 | 2026-06-27 | schema_reference_alias_migration | frb_view_def_schema_v0_9_chat_input_mapping.json / _frb_view_def_schema_v0_9_chat_input_mapping.json など、旧派生名の参照が一部activeファイルに残っていた。 | 現行参照を frb_view_def_schema_v0_9.json へ補正。 | 00_rulesファイル名整理後の現行schemaファイル名と参照名を一致させるため。 |
| chg_0050_003 | 2026-06-27 | future_incident_filename_alignment | 未着手インシデントのtarget_files / target_rule_files等に旧00_rulesファイル名が残っていた。 | 未着手インシデント内の現行参照を新00_rulesファイル名へ補正。完了済みインシデントの旧名は履歴として保持。 | 次工程でAIや人間が旧ファイル名を参照して作業対象を誤らないようにするため。 |

### v0.14.21-human-ai-responsibility-rules: 新ルール候補：Human / AI Responsibility Rules 人間・AI責務境界ルール
- 作業ID: studio_work_0051
- 種別: rules_review
- 優先度: high
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: data/json/01_main/studio_work_incident_data_*.json, defs/rules/*review*.json, data/json/00_rules/*.json

#### 目的

人間が最終判断する項目、AIが更新してよい項目、AI更新後に未承認へ戻すべき状態項目を整理し、承認・確認・レビュー状態の責務境界を明確にする。

#### 背景

Rule Review承認/確認状態の単一正本化懸案が出ており、AIがルール本文や章を修正した場合に approval_decision / verification_status / review_status をどう扱うかが未定義である。

#### 対象範囲

人間のみが最終承認できる項目、AIが作業上更新してよい確認状態、AI修正時に未承認・未確認へ戻す条件、既存 studio_work_0049 との関係を整理する。

#### 対象外

このインシデント追加時点では、承認UIやViewDefの実装修正、既存全データの状態変更は行わない。

#### 固定名方針

approval_decision / verification_status / review_status はインシデント・ルールレビューDataの標準候補として扱うが、Runtime固定名として無条件に一般Dataへ要求しない。

#### module化方針

type="module" 化は今回の主目的ではない。まずルール系Data JSON・インシデント管理Data・必要なViewDef方針として整理する。

#### リスク

AIが状態を勝手に承認済みにしてしまうと人間承認の意味が壊れる。逆に全変更で未承認へ戻しすぎると運用負荷が高くなる。

#### 確認観点

AIが本文を変更した場合、要約だけ変更した場合、ViewDefだけ変更した場合の状態更新ルールが整理されていること。

#### 作業会話サマリ


##### 依頼 / 方針

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI整理

Human / AI Responsibility Rules 人間・AI責務境界ルール を将来対応インシデントとして追加。現時点では実装・ルール本文改正は行わず、必要を感じたタイミングで個別フェーズとして着手できるよう、目的・範囲・リスク・確認観点を整理した。

##### 追加コメント

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI追加回答

将来ルール候補をインシデント化。必要になった時点で個別にルール本文・ViewDef・テスト証跡へ反映する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0051_001 | 2026-06-27 | user | 将来ルール候補のインシデント追加 | 普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。 |
| disc_0051_002 | 2026-06-27 | assistant | 将来ルール候補の整理 | Human / AI Responsibility Rules 人間・AI責務境界ルール はAI駆動開発を継続運用する上で必要になり得るため、未着手インシデントとして登録し、後で必要性が高まった時に実作業化する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0051_001 | 2026-06-27 | 現時点ではルール本文へ即反映せず、将来対応インシデントとして残す。 | 今すぐ全ルールを増やすとStudioくんのルール体系が太りすぎるため。必要性を感じた段階で、対象ルールファイルごとに個別対応する。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0051_001 | 2026-06-27 | incident_added | AI駆動開発で今後必要になり得る追加ルール系統がインシデント管理上で未登録だった。 | studio_work_0051 v0.14.21-human-ai-responsibility-rules として、Human / AI Responsibility Rules 人間・AI責務境界ルール を未着手インシデントに追加。 | 必要を感じたタイミングで漏れなくルール化・実装化へ進めるようにするため。 |

### v0.14.22-definition-of-done-rules: 新ルール候補：Definition of Done Rules 作業完了条件ルール
- 作業ID: studio_work_0052
- 種別: rules_review
- 優先度: high
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: data/json/00_rules/*.json, data/json/01_main/studio_work_incident_data_*.json, tests/tools/*

#### 目的

AI作業における『完了』の条件を定義し、成果物・証跡・インシデント更新・返却安全性をそろえる。

#### 背景

毎回、JSON parse、runtime生成物除外、ZIP長大パス確認、インシデント更新済み確認を行っているが、完了条件としての独立ルールはまだ薄い。

#### 対象範囲

作業完了条件、failしていても完了扱いできる条件、返却前チェック、インシデント更新、証跡保存、未確認項目の明示を整理する。

#### 対象外

この時点ではCI/CDや自動ゲート実装までは行わない。まず人間とAIが合意できるDone定義を作る。

#### 固定名方針

Done判定用の項目をDataに追加する場合も、Runtimeが特定Data専用フィールドへ依存しないようViewDef側で表示する。

#### module化方針

type="module" 化は今回の主目的ではない。まずルール系Data JSON・インシデント管理Data・必要なViewDef方針として整理する。

#### リスク

Doneの定義が曖昧だと、AIが『できた』と言っても証跡やインシデント更新が不足する。逆にDone条件を重くしすぎると小作業が進まなくなる。

#### 確認観点

小さな文言修正、ルール追加、テスト失敗を期待する作業、UI実装修正の各ケースでDone条件が説明できること。

#### 作業会話サマリ


##### 依頼 / 方針

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI整理

Definition of Done Rules 作業完了条件ルール を将来対応インシデントとして追加。現時点では実装・ルール本文改正は行わず、必要を感じたタイミングで個別フェーズとして着手できるよう、目的・範囲・リスク・確認観点を整理した。

##### 追加コメント

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI追加回答

将来ルール候補をインシデント化。必要になった時点で個別にルール本文・ViewDef・テスト証跡へ反映する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0052_001 | 2026-06-27 | user | 将来ルール候補のインシデント追加 | 普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。 |
| disc_0052_002 | 2026-06-27 | assistant | 将来ルール候補の整理 | Definition of Done Rules 作業完了条件ルール はAI駆動開発を継続運用する上で必要になり得るため、未着手インシデントとして登録し、後で必要性が高まった時に実作業化する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0052_001 | 2026-06-27 | 現時点ではルール本文へ即反映せず、将来対応インシデントとして残す。 | 今すぐ全ルールを増やすとStudioくんのルール体系が太りすぎるため。必要性を感じた段階で、対象ルールファイルごとに個別対応する。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0052_001 | 2026-06-27 | incident_added | AI駆動開発で今後必要になり得る追加ルール系統がインシデント管理上で未登録だった。 | studio_work_0052 v0.14.22-definition-of-done-rules として、Definition of Done Rules 作業完了条件ルール を未着手インシデントに追加。 | 必要を感じたタイミングで漏れなくルール化・実装化へ進めるようにするため。 |

### v0.14.23-change-impact-risk-classification-rules: 新ルール候補：Change Impact / Risk Classification Rules 変更影響・リスク分類ルール
- 作業ID: studio_work_0053
- 種別: rules_review
- 優先度: medium
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: data/json/00_rules/*.json, data/json/01_main/studio_work_incident_data_*.json

#### 目的

変更内容を低・中・高・超高リスクに分類し、AI作業時の確認粒度・報告粒度・人間相談要否を切り替えられるようにする。

#### 背景

ファイル名変更、テスト証跡構造変更、Diff責務分離、ZIP返却などで、変更の危険度によって必要な確認が大きく変わることが見えてきた。

#### 対象範囲

変更種別ごとのリスク分類、必須確認、archive要否、人間相談条件、インシデント記録粒度を整理する。

#### 対象外

この作業では実際の自動リスク判定エンジンやUIバッジ表示は行わない。

#### 固定名方針

risk / priority 等はインシデント管理Dataでは使用しているが、一般DataのRuntime固定名として扱わない。

#### module化方針

type="module" 化は今回の主目的ではない。まずルール系Data JSON・インシデント管理Data・必要なViewDef方針として整理する。

#### リスク

低リスク扱いした変更が実は参照切れを起こす可能性がある。高リスク扱いを乱用すると作業速度が落ちる。

#### 確認観点

文言修正、ViewDef表示調整、Data構造変更、Runtime保存処理変更、ファイル名変更、承認状態自動更新のリスク分類が整理されていること。

#### 作業会話サマリ


##### 依頼 / 方針

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI整理

Change Impact / Risk Classification Rules 変更影響・リスク分類ルール を将来対応インシデントとして追加。現時点では実装・ルール本文改正は行わず、必要を感じたタイミングで個別フェーズとして着手できるよう、目的・範囲・リスク・確認観点を整理した。

##### 追加コメント

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI追加回答

将来ルール候補をインシデント化。必要になった時点で個別にルール本文・ViewDef・テスト証跡へ反映する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0053_001 | 2026-06-27 | user | 将来ルール候補のインシデント追加 | 普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。 |
| disc_0053_002 | 2026-06-27 | assistant | 将来ルール候補の整理 | Change Impact / Risk Classification Rules 変更影響・リスク分類ルール はAI駆動開発を継続運用する上で必要になり得るため、未着手インシデントとして登録し、後で必要性が高まった時に実作業化する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0053_001 | 2026-06-27 | 現時点ではルール本文へ即反映せず、将来対応インシデントとして残す。 | 今すぐ全ルールを増やすとStudioくんのルール体系が太りすぎるため。必要性を感じた段階で、対象ルールファイルごとに個別対応する。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0053_001 | 2026-06-27 | incident_added | AI駆動開発で今後必要になり得る追加ルール系統がインシデント管理上で未登録だった。 | studio_work_0053 v0.14.23-change-impact-risk-classification-rules として、Change Impact / Risk Classification Rules 変更影響・リスク分類ルール を未着手インシデントに追加。 | 必要を感じたタイミングで漏れなくルール化・実装化へ進めるようにするため。 |

### v0.14.24-traceability-rules: 新ルール候補：Traceability Rules ルール・インシデント・証跡トレースルール
- 作業ID: studio_work_0054
- 種別: rules_review
- 優先度: high
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: data/json/03_tests/**, data/json/00_rules/*.json, data/json/01_main/studio_work_incident_data_*.json, defs/relation/*.json

#### 目的

Rule / Incident / Expected / Actual / Diff / ViewDef / Release のつながりを辿れるようにするためのトレーサビリティ方針を整理する。

#### 背景

Expected / Actual / Diff責務分離やDiff共通フォーマットにより証跡文化が育ってきたが、どのルールを根拠にどのテストやExpectedがあるかの接続ルールはまだ薄い。

#### 対象範囲

rule_id、work_item_id、test_pattern_id、check_id、view_def、release/versionの関連をどう残すかを整理する。relation系Dataやtrace_relationsの正本位置も検討する。

#### 対象外

この段階では全既存証跡へのID逆引き付与やGraph表示実装は行わない。

#### 固定名方針

relation_refs / rule_id / check_id 等は証跡・ルールDataの契約として扱い、Runtimeが一般Dataへ無条件要求しない。

#### module化方針

type="module" 化は今回の主目的ではない。まずルール系Data JSON・インシデント管理Data・必要なViewDef方針として整理する。

#### リスク

IDを増やしすぎると入力負荷が上がる。逆にIDがないと、なぜこのExpectedが存在するのか後で追えなくなる。

#### 確認観点

任意のDiff checkから、関連Expected、TestPattern、Incident、根拠Ruleを辿る方針が説明できること。

#### 作業会話サマリ


##### 依頼 / 方針

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI整理

Traceability Rules ルール・インシデント・証跡トレースルール を将来対応インシデントとして追加。現時点では実装・ルール本文改正は行わず、必要を感じたタイミングで個別フェーズとして着手できるよう、目的・範囲・リスク・確認観点を整理した。

##### 追加コメント

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI追加回答

将来ルール候補をインシデント化。必要になった時点で個別にルール本文・ViewDef・テスト証跡へ反映する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0054_001 | 2026-06-27 | user | 将来ルール候補のインシデント追加 | 普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。 |
| disc_0054_002 | 2026-06-27 | assistant | 将来ルール候補の整理 | Traceability Rules ルール・インシデント・証跡トレースルール はAI駆動開発を継続運用する上で必要になり得るため、未着手インシデントとして登録し、後で必要性が高まった時に実作業化する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0054_001 | 2026-06-27 | 現時点ではルール本文へ即反映せず、将来対応インシデントとして残す。 | 今すぐ全ルールを増やすとStudioくんのルール体系が太りすぎるため。必要性を感じた段階で、対象ルールファイルごとに個別対応する。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0054_001 | 2026-06-27 | incident_added | AI駆動開発で今後必要になり得る追加ルール系統がインシデント管理上で未登録だった。 | studio_work_0054 v0.14.24-traceability-rules として、Traceability Rules ルール・インシデント・証跡トレースルール を未着手インシデントに追加。 | 必要を感じたタイミングで漏れなくルール化・実装化へ進めるようにするため。 |

### v0.14.25-test-runner-execution-rules: 新ルール候補：Test Runner / Execution Rules 共通テストランナー実行ルール
- 作業ID: studio_work_0055
- 種別: rules_review
- 優先度: high
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: tests/**/*.mjs, tests/**/*.spec.ts, data/json/03_tests/**, tests/tools/*

#### 目的

テストコードをケースごとに増やすのではなく、実行言語ごとの共通ランナーへ寄せ、Test Pattern / Expected JSONを増やす運用を整理する。

#### 背景

すでに『テストコードは実行言語ごとに1ファイルへ共通化に努める』方針が出ているが、Node.js系・Playwright系・将来Python系の実行規約として独立整理する余地がある。

#### 対象範囲

Node.js系共通 .mjs、Playwright系共通 .spec.ts、将来Python系ランナー、Expected直書き禁止、失敗時証跡出力、ランナー引数/対象TestPattern指定方式を整理する。

#### 対象外

この作業では既存テストコードの全面統合や新しいテストランナー実装は行わない。

#### 固定名方針

test_id / check_id / expected_file 等はTest Evidence契約の一部として扱い、一般Runtime固定名ではない。

#### module化方針

type="module" 化は今回の主目的ではない。まずルール系Data JSON・インシデント管理Data・必要なViewDef方針として整理する。

#### リスク

共通ランナーに寄せすぎると汎用化が過剰になり読みにくくなる。ケースごとのテストコードを増やしすぎると保守不能になる。

#### 確認観点

新しいテストケースを追加する場合に、まずTest Pattern JSONを増やすべきか、新ランナーが必要か判断できること。

#### 作業会話サマリ


##### 依頼 / 方針

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI整理

Test Runner / Execution Rules 共通テストランナー実行ルール を将来対応インシデントとして追加。現時点では実装・ルール本文改正は行わず、必要を感じたタイミングで個別フェーズとして着手できるよう、目的・範囲・リスク・確認観点を整理した。

##### 追加コメント

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI追加回答

将来ルール候補をインシデント化。必要になった時点で個別にルール本文・ViewDef・テスト証跡へ反映する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0055_001 | 2026-06-27 | user | 将来ルール候補のインシデント追加 | 普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。 |
| disc_0055_002 | 2026-06-27 | assistant | 将来ルール候補の整理 | Test Runner / Execution Rules 共通テストランナー実行ルール はAI駆動開発を継続運用する上で必要になり得るため、未着手インシデントとして登録し、後で必要性が高まった時に実作業化する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0055_001 | 2026-06-27 | 現時点ではルール本文へ即反映せず、将来対応インシデントとして残す。 | 今すぐ全ルールを増やすとStudioくんのルール体系が太りすぎるため。必要性を感じた段階で、対象ルールファイルごとに個別対応する。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0055_001 | 2026-06-27 | incident_added | AI駆動開発で今後必要になり得る追加ルール系統がインシデント管理上で未登録だった。 | studio_work_0055 v0.14.25-test-runner-execution-rules として、Test Runner / Execution Rules 共通テストランナー実行ルール を未着手インシデントに追加。 | 必要を感じたタイミングで漏れなくルール化・実装化へ進めるようにするため。 |

### v0.14.26-migration-backward-compatibility-rules: 新ルール候補：Migration / Backward Compatibility Rules 移行・互換・廃止ルール
- 作業ID: studio_work_0056
- 種別: rules_review
- 優先度: high
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: data/json/**/*.json, defs/**/*.json, _archive/**, filename_updatelist.md

#### 目的

ファイル名変更・フォルダー移行・互換フィールド追加時に、旧名・旧パス・互換項目をどう扱うかを定義する。

#### 背景

00_rulesファイル名変更や旧パス罠フォルダー、testId/test_id互換などで、移行と互換を明確に扱う必要が見えてきた。

#### 対象範囲

旧パスarchive、旧名参照更新、互換項目の残し方、deprecated_since、remove_after_phase、履歴として旧名を残す範囲、現行参照として置換する範囲を整理する。

#### 対象外

この作業では既存全データへのdeprecated項目追加や旧互換項目削除は行わない。

#### 固定名方針

deprecated_since / remove_after_phase 等を導入する場合も、特定Data専用ではなく移行管理用メタ情報として扱う。

#### module化方針

type="module" 化は今回の主目的ではない。まずルール系Data JSON・インシデント管理Data・必要なViewDef方針として整理する。

#### リスク

互換項目を残しすぎると正本が増える。旧項目を急に消すと既存ViewDefや証跡が壊れる。

#### 確認観点

ファイル名変更、フォルダー移動、フィールド名変更、互換alias追加のケースで、何を更新し何を履歴として残すか説明できること。

#### 作業会話サマリ


##### 依頼 / 方針

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI整理

Migration / Backward Compatibility Rules 移行・互換・廃止ルール を将来対応インシデントとして追加。現時点では実装・ルール本文改正は行わず、必要を感じたタイミングで個別フェーズとして着手できるよう、目的・範囲・リスク・確認観点を整理した。

##### 追加コメント

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI追加回答

将来ルール候補をインシデント化。必要になった時点で個別にルール本文・ViewDef・テスト証跡へ反映する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0056_001 | 2026-06-27 | user | 将来ルール候補のインシデント追加 | 普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。 |
| disc_0056_002 | 2026-06-27 | assistant | 将来ルール候補の整理 | Migration / Backward Compatibility Rules 移行・互換・廃止ルール はAI駆動開発を継続運用する上で必要になり得るため、未着手インシデントとして登録し、後で必要性が高まった時に実作業化する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0056_001 | 2026-06-27 | 現時点ではルール本文へ即反映せず、将来対応インシデントとして残す。 | 今すぐ全ルールを増やすとStudioくんのルール体系が太りすぎるため。必要性を感じた段階で、対象ルールファイルごとに個別対応する。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0056_001 | 2026-06-27 | incident_added | AI駆動開発で今後必要になり得る追加ルール系統がインシデント管理上で未登録だった。 | studio_work_0056 v0.14.26-migration-backward-compatibility-rules として、Migration / Backward Compatibility Rules 移行・互換・廃止ルール を未着手インシデントに追加。 | 必要を感じたタイミングで漏れなくルール化・実装化へ進めるようにするため。 |

### v0.14.27-ai-work-context-package-rules: 新ルール候補：AI Work Context Package Rules AI作業文脈パッケージルール
- 作業ID: studio_work_0057
- 種別: rules_review
- 優先度: medium
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: data/json/01_main/00_do_incident_prompt_temple.md, data/json/00_rules/_json_creation_prompt.md, data/json/01_main/studio_work_incident_data_*.json

#### 目的

AIに作業依頼するときの最小文脈セット、優先順位、添付ZIPとraw URLの扱いをルール化する。

#### 背景

現在の作業依頼では incident_file / phase / Foundation raw URL / main ZIP / raw base / 最新添付ZIP を明示しており、かなり安定してきたが、独立した文脈パッケージルールはまだない。

#### 対象範囲

AI作業依頼テンプレート、必須入力、任意入力、最新資材優先順位、raw URL参照、添付ZIP優先、ファイル名変更時の注意、コンテキスト不足時の確認方針を整理する。

#### 対象外

この作業では自動テンプレート生成UIや外部LLM連携は行わない。

#### 固定名方針

incident_file / phase / raw_url 等はAI作業依頼の外部契約であり、一般DataのRuntime固定名として扱わない。

#### module化方針

type="module" 化は今回の主目的ではない。まずルール系Data JSON・インシデント管理Data・必要なViewDef方針として整理する。

#### リスク

依頼文が重くなりすぎると毎回の作業が面倒になる。軽すぎるとAIが旧ファイル名や旧パスを参照する。

#### 確認観点

最新ZIPがある場合、raw URLとどちらを優先するか。incident_fileとphaseが食い違った場合にどう確認するかが整理されていること。

#### 作業会話サマリ


##### 依頼 / 方針

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI整理

AI Work Context Package Rules AI作業文脈パッケージルール を将来対応インシデントとして追加。現時点では実装・ルール本文改正は行わず、必要を感じたタイミングで個別フェーズとして着手できるよう、目的・範囲・リスク・確認観点を整理した。

##### 追加コメント

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI追加回答

将来ルール候補をインシデント化。必要になった時点で個別にルール本文・ViewDef・テスト証跡へ反映する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0057_001 | 2026-06-27 | user | 将来ルール候補のインシデント追加 | 普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。 |
| disc_0057_002 | 2026-06-27 | assistant | 将来ルール候補の整理 | AI Work Context Package Rules AI作業文脈パッケージルール はAI駆動開発を継続運用する上で必要になり得るため、未着手インシデントとして登録し、後で必要性が高まった時に実作業化する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0057_001 | 2026-06-27 | 現時点ではルール本文へ即反映せず、将来対応インシデントとして残す。 | 今すぐ全ルールを増やすとStudioくんのルール体系が太りすぎるため。必要性を感じた段階で、対象ルールファイルごとに個別対応する。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0057_001 | 2026-06-27 | incident_added | AI駆動開発で今後必要になり得る追加ルール系統がインシデント管理上で未登録だった。 | studio_work_0057 v0.14.27-ai-work-context-package-rules として、AI Work Context Package Rules AI作業文脈パッケージルール を未着手インシデントに追加。 | 必要を感じたタイミングで漏れなくルール化・実装化へ進めるようにするため。 |

### v0.14.28-git-release-branch-rules: 新ルール候補：Git / Release / Branch Rules Git・リリース・ブランチ運用ルール
- 作業ID: studio_work_0058
- 種別: rules_review
- 優先度: medium
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: README, release_data.json if created, data/json/01_main/studio_work_incident_data_*.json, GitHub運用メモ

#### 目的

AI返却ZIP、GitHub main、release tag、GitHub Pages公開物、_archiveの関係を整理し、正本と成果物の位置づけを明確にする。

#### 背景

現在はZIP返却中心だが、GitHub raw URLやGitHub Pages公開、main ZIP参照が作業ルールに入っており、将来的にリリース管理が必要になる。

#### 対象範囲

AI返却ZIPの位置づけ、GitHub mainの正本性、release tag、公開用wwwroot、_archive、作業ブランチ/ローカル作業の扱いを整理する。

#### 対象外

この時点ではGit操作の自動化、ブランチ作成、タグ作成、CIリリースは行わない。

#### 固定名方針

version / revision / phase はStudioインシデント・リリース管理の候補語であり、全Dataに強制しない。

#### module化方針

type="module" 化は今回の主目的ではない。まずルール系Data JSON・インシデント管理Data・必要なViewDef方針として整理する。

#### リスク

ZIPを正本扱いするとGitHubとのズレが出る。GitHub mainを正本にする場合、AI返却物の取り込み手順が必要になる。

#### 確認観点

AI返却ZIP、GitHub main、GitHub Pages、release tag、_archiveの関係を説明できること。

#### 作業会話サマリ


##### 依頼 / 方針

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI整理

Git / Release / Branch Rules Git・リリース・ブランチ運用ルール を将来対応インシデントとして追加。現時点では実装・ルール本文改正は行わず、必要を感じたタイミングで個別フェーズとして着手できるよう、目的・範囲・リスク・確認観点を整理した。

##### 追加コメント

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI追加回答

将来ルール候補をインシデント化。必要になった時点で個別にルール本文・ViewDef・テスト証跡へ反映する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0058_001 | 2026-06-27 | user | 将来ルール候補のインシデント追加 | 普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。 |
| disc_0058_002 | 2026-06-27 | assistant | 将来ルール候補の整理 | Git / Release / Branch Rules Git・リリース・ブランチ運用ルール はAI駆動開発を継続運用する上で必要になり得るため、未着手インシデントとして登録し、後で必要性が高まった時に実作業化する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0058_001 | 2026-06-27 | 現時点ではルール本文へ即反映せず、将来対応インシデントとして残す。 | 今すぐ全ルールを増やすとStudioくんのルール体系が太りすぎるため。必要性を感じた段階で、対象ルールファイルごとに個別対応する。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0058_001 | 2026-06-27 | incident_added | AI駆動開発で今後必要になり得る追加ルール系統がインシデント管理上で未登録だった。 | studio_work_0058 v0.14.28-git-release-branch-rules として、Git / Release / Branch Rules Git・リリース・ブランチ運用ルール を未着手インシデントに追加。 | 必要を感じたタイミングで漏れなくルール化・実装化へ進めるようにするため。 |

### v0.14.29-security-public-data-rules: 新ルール候補：Security / Public Data Rules 公開データ・安全管理ルール
- 作業ID: studio_work_0059
- 種別: rules_review
- 優先度: high
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: wwwroot/data/**, wwwroot/defs/**, data/json/**, docs/articles, README

#### 目的

GitHub Pagesや記事連携で公開してよいData/Defsと、ローカル限定・非公開にすべき情報の境界を整理する。

#### 背景

wwwroot/data・wwwroot/defsは公開用静的領域として扱う話があり、今後AI協働・社内情報・個人情報・実験メモが混ざるリスクがある。

#### 対象範囲

公開可否分類、ローカル限定領域、GitHub Pages公開領域、個人情報・社内情報・秘密情報の扱い、AIが公開領域へ出してはいけない情報を整理する。

#### 対象外

この作業ではセキュリティスキャン実装や秘密情報検出ツール作成までは行わない。

#### 固定名方針

public/private 等の状態項目を導入する場合も、公開管理用契約として扱い、一般Runtime固定名にしない。

#### module化方針

type="module" 化は今回の主目的ではない。まずルール系Data JSON・インシデント管理Data・必要なViewDef方針として整理する。

#### リスク

公開してはいけない情報がGitHub Pagesに混入すると重大。厳しすぎると公開用サンプルや記事連携が進まない。

#### 確認観点

公開用サンプル、個人メモ、社内情報、実験ログ、ルールData、ViewDefの公開可否判断が整理されていること。

#### 作業会話サマリ


##### 依頼 / 方針

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI整理

Security / Public Data Rules 公開データ・安全管理ルール を将来対応インシデントとして追加。現時点では実装・ルール本文改正は行わず、必要を感じたタイミングで個別フェーズとして着手できるよう、目的・範囲・リスク・確認観点を整理した。

##### 追加コメント

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI追加回答

将来ルール候補をインシデント化。必要になった時点で個別にルール本文・ViewDef・テスト証跡へ反映する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0059_001 | 2026-06-27 | user | 将来ルール候補のインシデント追加 | 普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。 |
| disc_0059_002 | 2026-06-27 | assistant | 将来ルール候補の整理 | Security / Public Data Rules 公開データ・安全管理ルール はAI駆動開発を継続運用する上で必要になり得るため、未着手インシデントとして登録し、後で必要性が高まった時に実作業化する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0059_001 | 2026-06-27 | 現時点ではルール本文へ即反映せず、将来対応インシデントとして残す。 | 今すぐ全ルールを増やすとStudioくんのルール体系が太りすぎるため。必要性を感じた段階で、対象ルールファイルごとに個別対応する。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0059_001 | 2026-06-27 | incident_added | AI駆動開発で今後必要になり得る追加ルール系統がインシデント管理上で未登録だった。 | studio_work_0059 v0.14.29-security-public-data-rules として、Security / Public Data Rules 公開データ・安全管理ルール を未着手インシデントに追加。 | 必要を感じたタイミングで漏れなくルール化・実装化へ進めるようにするため。 |

### v0.14.30-error-incident-escalation-rules: 新ルール候補：Error / Incident Escalation Rules エラー・違和感・再発防止ルール
- 作業ID: studio_work_0060
- 種別: rules_review
- 優先度: medium
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: data/json/01_main/studio_work_incident_data_*.json, tests/**/*.spec.ts, tests/**/*.mjs, reports/*.md if created

#### 目的

AI作業中に発生したエラー、ユーザー環境のみの不具合、仕様未確定の違和感をどうインシデント化・エスカレーションするかを整理する。

#### 背景

diffが出ない、旧パスを見ていた、runtimeフォルダーが生える、ZIP長大パスなど、作業中のエラーや違和感が改善ルールへつながった。

#### 対象範囲

再現可/再現不可、ユーザー環境依存、AI作業ミス、仕様未確定、再発防止メモ、暫定対応/恒久対応の切り分けを整理する。

#### 対象外

この作業ではエラー自動収集やログビューア実装は行わない。

#### 固定名方針

error_type / recurrence / workaround 等を導入する場合も、インシデント管理Dataの候補として扱い、一般Runtime固定名にしない。

#### module化方針

type="module" 化は今回の主目的ではない。まずルール系Data JSON・インシデント管理Data・必要なViewDef方針として整理する。

#### リスク

何でもインシデント化すると管理が膨らむ。逆に違和感を流すと同じ事故が繰り返される。

#### 確認観点

再現できるエラー、ユーザー環境だけのエラー、AIの作業ミス、仕様相談、運用懸案をどう分類するか説明できること。

#### 作業会話サマリ


##### 依頼 / 方針

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI整理

Error / Incident Escalation Rules エラー・違和感・再発防止ルール を将来対応インシデントとして追加。現時点では実装・ルール本文改正は行わず、必要を感じたタイミングで個別フェーズとして着手できるよう、目的・範囲・リスク・確認観点を整理した。

##### 追加コメント

普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。

##### AI追加回答

将来ルール候補をインシデント化。必要になった時点で個別にルール本文・ViewDef・テスト証跡へ反映する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0060_001 | 2026-06-27 | user | 将来ルール候補のインシデント追加 | 普通にAI駆動開発をガシガシ回す人が作るルール系統で、まだStudioくんに無いルール系を、今後必要を感じたら徐々に対応できるよう、漏れないようにインシデントに分けて追加したい。 |
| disc_0060_002 | 2026-06-27 | assistant | 将来ルール候補の整理 | Error / Incident Escalation Rules エラー・違和感・再発防止ルール はAI駆動開発を継続運用する上で必要になり得るため、未着手インシデントとして登録し、後で必要性が高まった時に実作業化する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0060_001 | 2026-06-27 | 現時点ではルール本文へ即反映せず、将来対応インシデントとして残す。 | 今すぐ全ルールを増やすとStudioくんのルール体系が太りすぎるため。必要性を感じた段階で、対象ルールファイルごとに個別対応する。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0060_001 | 2026-06-27 | incident_added | AI駆動開発で今後必要になり得る追加ルール系統がインシデント管理上で未登録だった。 | studio_work_0060 v0.14.30-error-incident-escalation-rules として、Error / Incident Escalation Rules エラー・違和感・再発防止ルール を未着手インシデントに追加。 | 必要を感じたタイミングで漏れなくルール化・実装化へ進めるようにするため。 |

### v0.14.32-viewdef-header-search-layout-rules: ViewDef作成ルール：ヘッダー基本情報と検索項目のコンパクト表示方針
- 作業ID: studio_work_0061
- 種別: rules_review
- 分類: viewdef_generation_layout
- 優先度: medium
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json, data/json/00_rules/_json_creation_prompt.md, defs/**/*.json, data/json/01_main/studio_work_incident_data_*.json

#### 目的

ViewDef作成時に、ヘッダー部・基本情報・画面検索項目をコンパクトに見せるための表示方針をルール化する。ヘッダー基本情報は1行に収まる項目だけを表示し、長文・複数行項目を原則非表示にすることで、詳細本文やグリッドへ視線を早く移せる画面にする。

#### 背景

StudioくんのViewDefが増えるにつれて、ヘッダー部・基本情報に多くの項目やマルチテキストボックスを出すと、画面上部が縦に太り、一覧・詳細・検索の初期視認性が落ちる。特にOwnerなど確認優先度の低い項目や長文欄は、基本情報の主役ではなく、必要な場合に詳細側で確認できればよい。

#### 対象範囲

ViewDef生成ルールに、ヘッダー部・基本情報の表示項目選定方針を追加する。マルチテキストボックスはヘッダー基本情報では画面表示オフを基本とする。ヘッダー基本情報は1行に収まる範囲で表示オン項目を調整する。Ownerはヘッダー基本情報では表示オフを基本とする。画面検索項目部分は各項目の縦マージンを調整し、縦長になりすぎないコンパクト表示を基本とする。

#### 対象外

このインシデント追加時点では既存ViewDefの一括修正やRuntime CSS修正は行わない。まずViewDef作成・生成時のルールとして登録し、必要を感じたタイミングで個別ViewDefまたはRuntime側の実装調整へ進む。

#### 固定名方針

Ownerなどのフィールド名をRuntime固定名として特別扱いしない。ヘッダー基本情報に表示するかどうかはViewDefの表示設定で制御する。Ownerは運用上の基本方針としてヘッダー非表示を推奨するが、Data構造やRuntime仕様の固定名にはしない。

#### module化方針

type="module" 化は今回の主目的ではない。ViewDef生成ルールとAI作業プロンプトのブラッシュアップを中心に扱う。

#### リスク

ヘッダー部を絞りすぎると、一覧から最低限の文脈を掴みにくくなる。逆に表示項目を増やしすぎると、画面上部が縦に太り、Studioくんの一覧性と作業テンポが落ちる。検索項目の余白を詰めすぎると視認性が落ちる可能性があるため、コンパクトさと読みやすさのバランスが必要。

#### 確認観点

新規ViewDef生成時に、ヘッダー基本情報の表示オン項目が1行に収まること。マルチテキストボックスがヘッダー基本情報に表示されていないこと。Ownerがヘッダー基本情報で表示オフになっていること。検索項目部分の縦マージンが過剰でなく、画面上部がコンパクトに見えること。

#### 作業会話サマリ


##### 依頼 / 方針

ViewDef作成時のルールブラッシュアップとして、ヘッダー部・基本情報のマルチテキストボックスは画面表示オフを基本とする。ヘッダー部・基本情報は1行に収まる範囲に画面表示オン項目を調整する。ヘッダー部・基本情報 Ownerは表示オフ。画面検索項目部分は、各項目の縦マージンを調整し、縦長がコンパクトになるように調整する。

##### AI整理

ViewDef作成ルールの将来ブラッシュアップ対象としてインシデント化する。現時点ではルール本文や既存ViewDefの改正は行わず、ヘッダー基本情報・Owner表示・検索項目マージンの方針を漏れないよう未着手項目として追加する。

##### 追加コメント

最新資材を基準に、v0.14.32-viewdef-header-search-layout-rules として、ヘッダー基本情報・検索項目のコンパクト表示方針をルール本文へ反映する作業を依頼。

##### AI追加回答

v0.14.32 対応完了。frb_viewdef_generation_rules_data_v0_1.json に viewdef_rule_26 系を追加し、ヘッダー基本情報は1行に収まる範囲、マルチテキストボックス/長文欄は表示オフ基本、Ownerは表示オフ基本、検索項目は縦マージン調整でコンパクト表示する方針を明文化した。_json_creation_prompt.md にも短い実務チェックを追加。既存ViewDefの一括修正とRuntime CSS修正は対象外。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0061_001 | 2026-06-27 | user | ViewDef作成ルールブラッシュアップ依頼 | ヘッダー部・基本情報のマルチテキストボックスは画面表示オフにすることを基本とする。ヘッダー部・基本情報は1行に収まる範囲に画面表示オン項目を調整することを基本とする。ヘッダー部・基本情報 Ownerは表示オフ。画面検索項目部分は、各項目の縦マージンは調整し、縦長がコンパクトになるように調整する。 |
| disc_0061_002 | 2026-06-27 | assistant | インシデント追加方針 | ViewDef生成時のUI設計ルールとして、ヘッダー基本情報は短く、長文欄は出さず、Ownerは基本非表示、検索項目は縦に太らせない方針を未着手インシデントとして登録する。 |
| disc_0061_003 | 2026-06-27 | user | v0.14.32ルール更新依頼 | 最新資材を添付し、incident_file=data/json/01_main/studio_work_incident_data_v0_61_viewdef_header_search_layout_rules_added.json、phase=v0.14.32-viewdef-header-search-layout-rules としてルール更新を依頼。Foundation Rules foundation_rule_019 のZIP返却契約を参照する。 |
| disc_0061_004 | 2026-06-27 | assistant | v0.14.32ルール更新結果 | ViewDef Generation Rulesへ viewdef_rule_26 系を追加し、ヘッダー基本情報1行化、長文/マルチテキスト非表示、Owner非表示、検索項目コンパクト表示の方針を反映。_json_creation_prompt.mdにも実務指示を追加し、更新済みインシデントJSONへ結果を記録した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0061_001 | 2026-06-27 | ヘッダー部・基本情報は、1行に収まる範囲の表示オン項目に絞ることを基本方針とする。 | 画面上部が縦に太ると、Grid一覧・詳細本文・検索結果へ到達する前に視線が詰まり、Studioくんの一覧性と作業テンポが落ちるため。 |
| dec_0061_002 | 2026-06-27 | ヘッダー部・基本情報のマルチテキストボックスとOwnerは、原則として表示オフにする。 | 長文欄や所有者情報はヘッダーの初期視認性に対して情報量が重く、必要な場合は詳細側で確認すればよいため。 |
| dec_0061_003 | 2026-06-27 | 画面検索項目部分は、縦マージンを調整してコンパクト表示を基本とする。 | 検索項目は頻繁に使うが、縦に膨らみすぎると一覧の表示領域を圧迫するため。 |
| dec_0061_004 | 2026-06-27 | 今回のv0.14.32では、ルール本文とAI作業プロンプトの更新に限定し、既存ViewDefの一括修正やRuntime CSS修正は行わない。 | まずViewDef生成時の設計方針として明文化し、既存画面への適用は必要性が出たタイミングで個別に扱う方が回帰リスクを抑えられるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0061_001 | 2026-06-27 | incident_added | ViewDef生成時のヘッダー基本情報・検索項目のコンパクト表示方針が作業項目として登録されていなかった。 | studio_work_0061 として、ViewDef作成ルール：ヘッダー基本情報と検索項目のコンパクト表示方針を追加。 | 今後ViewDefを生成・修正するときに、画面上部を太らせすぎないためのUI設計方針を漏らさず扱えるようにするため。 |
| chg_0061_002 | 2026-06-27 | rules_update | ViewDef生成ルール上で、ヘッダー基本情報・Owner・長文欄・検索項目マージンのコンパクト表示方針が明文化されていなかった。 | frb_viewdef_generation_rules_data_v0_1.json に viewdef_rule_26 系を追加し、_json_creation_prompt.md に v0.14.32 実務チェックを追加した。 | 新規ViewDef生成時に画面上部が縦に太りすぎることを防ぎ、Grid一覧・詳細本文・検索結果へ入りやすいStudio体験を維持するため。 |

### v0.14.37-git-diff-export-command-profile: Studioくん Git Diff Run / Export-DiffToJson.ps1 CommandProfile連携
- 作業ID: studio_work_0062
- 種別: feature
- 分類: git_diff_command_profile
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: Program.cs, Export-DiffToJson.ps1, data/json/04_tools/git_diff_export_run_config_data_v0_1.json, defs/tools/git_diff_export_run_config_view_def_v0_1.json, wwwroot/js/actions/action_registry.js, wwwroot/js/actions/action_toolbar.js, wwwroot/js/runtime/load_runtime.js, wwwroot/styles.css

#### 目的

Studioくんのグリッド一覧上部に Git Diff Run 系の実行ボタンを追加し、選択行のGit差分出力設定から Program.cs の許可済みCommandProfileを経由して Export-DiffToJson.ps1 を実行できるようにする。Git Diff結果をJSON化し、Studioくんでレビュー・AI差分物語へ接続する入口を作る。

#### 背景

Git DiffをStudioくんで扱えるようにすると、コード差分を単なるテキストではなく、JSON Objectとしてレビュー・要約・AI差分物語へ渡せる。ユーザーは Export-DiffToJson.ps1 をすでに用意しており、Studioくんから実行パラメータを選んで起動したい。一方で、DiffToJson.jsonをGit管理配下へ出力すると、差分出力ファイル自身がGit差分になり、差分が差分を生む再帰事故が起きるため、出力先はGit管理外に置く必要がある。

#### 対象範囲

Git Diff実行設定Data JSONとViewDefを追加する。Data JSONは1行目=WorkingTree相当の既定行、2行目=Mode Staged、3行目=Mode Head、4行目=Range指定として From / To を持つ行を想定する。グリッド一覧上部に「Git Diff Run」または「Git Diff JSON出力」ボタンを表示し、選択行の command_profile_id / mode / from_ref / to_ref / unified / max_patch_chars / no_patch / output_path_display をProgram.csへ渡す。Program.csは任意コマンドではなく許可済みCommandProfileだけを実行し、Export-DiffToJson.ps1の実体パス、固定または許可済みOutputPath、許可オプション、タイムアウト、引数検証を管理する。OutputPathは画面に常時表示したいためData JSONにも表示用として保持するが、実行時の正本はProgram.cs側のCommandProfile設定とする。

#### 対象外

任意コマンドライン実行、Data JSONからの自由なscriptPath指定、外部URL実行、GitHub Pagesなど静的ホスティング上での実行、PowerShell以外の一般コマンドランナー本格化、Git差分JSONの詳細ViewDef/AI差分物語生成は初回スコープ外とする。まずはExport-DiffToJson.ps1を安全に起動するCommandProfile Runnerの最小実装に絞る。

#### 固定名方針

Data JSONに任意のcommandLineやscriptPathを持たせない。command_profile_id はStudio標準Action/CommandProfile識別子として扱い、Program.cs側で許可済みprofileだけ解決する。output_path は画面表示と人間確認のためData JSONにも持たせるが、実行時はProgram.cs側の許可済みCommandProfile/Option定義と照合し、不一致時は拒否またはProgram.cs正本値を優先する。

#### module化方針

type="module" 化は行わない。既存のActionRegistry / toolbar.executeButton / Program.cs Minimal API構成を前提に、必要最小限のAction追加とAPI追加で実装する。

#### リスク

任意コマンド実行化すると危険。OutputPathをData JSONから自由入力させると任意ファイル書き込みリスクがある。DiffToJson.jsonをGit管理配下へ出力すると差分が差分を生む地獄になる。Git diffが巨大な場合に処理が長時間化する。PowerShell引数の文字列連結を誤るとコマンドインジェクションリスクがある。GitHub Pagesでは実行不可なので、静的モードでボタンを有効にすると混乱する。

#### 確認観点

WorkingTree/Staged/Head/Range各行からGit Diff Runできること。Range行では From / To から安全に from..to が組み立てられること。OutputPathが画面に表示されること。実行時はProgram.cs側の許可済みOutputPathと照合され、Git管理配下への勝手な出力を避けること。Data JSONに任意commandLineを書いても実行されないこと。Modeは許可値以外拒否されること。From/Toは安全なGit ref文字だけ許可されること。ProcessStartInfo.ArgumentListで引数を渡し、タイムアウトとstdout/stderr/exit_codeが返ること。静的ホスティング時はGit Diff Runがdisabledまたは実行不可になること。

#### 作業会話サマリ


##### 依頼 / 方針

StudioくんにGitDiffデビューさせたい。Git DiffのExport-DiffToJson.ps1をキックするJSONデータを作り、1行目はデータなし、2行目は-Mode Staged、3行目は-Mode Head、4行目はFrom/Toの2項目のようなパラメータ入力行にしたい。グリッド一覧上部の「Git Diff Run」ボタンをクリックするとExport-DiffToJson.ps1が実行されるシナリオにしたい。Program.csも修正が必要。Export-DiffToJson.ps1の名称はうまく汎用的に管理し、Program.cs側が汎用的にコマンドラインを実行できるようにしたいが、簡易なセキュリティーリスク対策案もほしい。さらに、DiffToJson.jsonがGit配下に入ると差分が差分を生む地獄になるため、F:\FRB_Diff\DiffToJson.json のようなGit管理外パスはProgram.cs側の許可済みコマンドオプションとして管理したい。ただし出力パスは画面に常時表示したいため、Data JSON側にも表示用として持つ二重管理を許容する。

##### AI整理

方針合意。Data JSONは実行リクエストと画面表示用の出力パスを持つが、任意commandLineやscriptPathは持たせない。Program.cs側にCommandProfile Registryを置き、git_diff_export profileだけがExport-DiffToJson.ps1と許可済みOutputPathを解決する。OutputPathはData JSONにも表示用として持つが、実行時はProgram.cs側の正本設定と照合する。DiffToJson.jsonはGit管理外のF:\FRB_Diff\DiffToJson.json等へ出力し、Git配下に差分生成物を置かない。Git Diff RunはローカルFRBStudio実行時のみ有効にする。

##### 追加コメント

今回の作業依頼: incident_file=data/json/01_main/studio_work_incident_data_v0_62_git_diff_command_profile_added.json / phase=v0.14.37-git-diff-export-command-profile。Foundation Rules foundation_rule_019 を参照し、Git Diff Run / CommandProfile連携の実装を依頼。

##### AI追加回答

v0.14.37-git-diff-export-command-profile 対応完了。Git Diff実行設定Data JSON / ViewDefを追加し、Grid上部の Git Diff Run ボタンから選択行を Program.cs の許可済み CommandProfile API へ渡す RunCommandProfile Actionを追加。Program.csには /api/actions/command/run と /api/actions/command/profiles を追加し、git_diff_export profileだけが tools/git/Export-DiffToJson.ps1 を実行できるようにした。OutputPathはProgram.cs側の正本設定 F:\FRB_Diff\DiffToJson.json とData JSON側 output_path_display を照合し、不一致時は拒否する。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0062_001 | 2026-06-27 | user | Git Diffデビュー相談 | StudioくんにGitDiffデビューさせたい。Export-DiffToJson.ps1をキックするJSONデータを作り、グリッド一覧上部のGit Diff RunボタンからProgram.cs経由で実行したい。 |
| disc_0062_002 | 2026-06-27 | assistant | CommandProfile方針 | Data JSONに任意commandLineを書かせず、Program.cs側の許可済みCommandProfileだけを実行する構成を提案。Mode/From/ToなどはData JSON、scriptPath/OutputPath/許可オプションはProgram.cs側で管理する方針を整理。 |
| disc_0062_003 | 2026-06-27 | user | Git管理外OutputPathの必要性 | DiffToJson.jsonがGit配下に入ると、差分が勝手に差分を生む構図になり収集がつかなくなる。F:\FRB_Diff\DiffToJson.json のパス自体はProgram.cs側で管理し、許可するコマンドのオプション情報として扱いたい。 |
| disc_0062_004 | 2026-06-27 | assistant | OutputPath責務修正 | Git Diff用途ではアプリ配下出力は危険と整理。DiffToJson.jsonはGit管理外へ出力し、OutputPathはProgram.cs側CommandProfileの固定または許可済みオプションとして管理する方針に修正。 |
| disc_0062_005 | 2026-06-27 | user | OutputPath二重管理合意 | 出力パスは画面にずっと表示しておきたいので、二重管理やむなし。Data JSON側にも持つ方針でインシデント登録を依頼。 |
| disc_0062_006 | 2026-06-27 | assistant | インシデント登録 | studio_work_0062 として、Git Diff Run / CommandProfile連携を登録。Data JSON側は表示用output_pathを持つが、実行正本はProgram.cs側とする方針を明記。 |
| disc_0062_007 | 2026-06-27 | user | v0.14.37作業依頼 | incident_file と phase を指定し、Foundation Rules のGitHub基準ソースとZIP返却契約に基づいて Git Diff Run / CommandProfile連携の実装を依頼。 |
| disc_0062_008 | 2026-06-27 | assistant | v0.14.37作業結果 | Git Diff実行設定Data/ViewDef、RunCommandProfile Action、Program.cs CommandProfile API、Export-DiffToJson.ps1配置、OutputPath照合、簡易セキュリティ制約を実装。任意commandLine/scriptPathはData JSONに持たせず、git_diff_export profileだけを許可した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0062_001 | 2026-06-27 | Git Diff実行は任意コマンド実行ではなく、Program.cs側の許可済みCommandProfileとして実装する。 | Data JSONに自由なcommandLineやscriptPathを持たせると、任意コマンド実行リスクが高いため。 |
| dec_0062_002 | 2026-06-27 | DiffToJson.jsonはGit管理配下ではなく、F:\FRB_Diff\DiffToJson.json などGit管理外へ出力する。 | Git配下へ差分出力JSONを置くと、そのファイル自身がGit差分になり、差分が差分を生む再帰事故が起きるため。 |
| dec_0062_003 | 2026-06-27 | OutputPathはData JSONにも表示用として持つが、実行時の正本はProgram.cs側のCommandProfile設定とする。 | ユーザーは画面上で出力先を常時確認したい。一方で実行時の安全性はProgram.cs側の許可済みパス管理で担保する必要があるため。 |
| dec_0062_004 | 2026-06-27 | 初回の行構成はWorkingTree/Staged/Head/Rangeの代表4行とする。 | Git Diff Runの操作感を確認するには、よく使う差分範囲を最小の設定行として持つのが分かりやすいため。 |
| dec_0062_005 | 2026-06-27 | GitHub Pagesなどの静的ホスティングではGit Diff Runを実行しない。 | サーバー側のProgram.csとローカルGitリポジトリがない環境ではPowerShell実行ができず、実行可能に見えると混乱とリスクがあるため。 |
| dec_0062_006 | 2026-06-27 | CommandProfile APIは /api/actions/command/run とし、Data JSONは実行パラメータだけを渡す。 | 既存のActionRegistry / toolbar.executeButton構成と整合させつつ、任意コマンド実行を避けるため。 |
| dec_0062_007 | 2026-06-27 | Export-DiffToJson.ps1 は tools/git/Export-DiffToJson.ps1 として同梱し、FRBStudio.csprojで出力ディレクトリへコピーする。 | Program.csが許可済みScriptPathを管理し、実行時にscriptPath不存在で失敗しないようにするため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0062_001 | 2026-06-27 | incident_added | StudioくんからExport-DiffToJson.ps1を安全に実行する作業項目がインシデント管理JSONに存在しなかった。 | studio_work_0062 v0.14.37-git-diff-export-command-profile として、Git Diff Run / CommandProfile連携を未着手インシデント登録した。 | Git DiffをJSON化し、Studioくんでレビュー・AI差分物語へ接続する入口を作るため。 |
| chg_0062_002 | 2026-06-27 | git_diff_command_profile_runtime_added | StudioくんからExport-DiffToJson.ps1を実行するData/ViewDef/API/Actionが存在しなかった。 | git_diff_export CommandProfile、Git Diff実行設定Data/ViewDef、RunCommandProfile Action、Program.cs APIを追加し、選択行からGit Diff JSON出力を実行できる入口を作った。 | Git DiffをJSON化し、Studioくんでレビュー・AI差分物語へ接続するため。 |
| chg_0062_003 | 2026-06-27 | command_profile_security_guard_added | Data JSONから任意コマンドや任意OutputPathを指定できる設計にすると、コマンドインジェクションや任意ファイル書き込みのリスクがあった。 | Data JSONには任意commandLine/scriptPathを持たせず、Mode/From/To等だけをProgram.csへ渡す。Program.csは許可済みprofile、Mode/Range/ref文字、OutputPath照合、timeout、ProcessStartInfo.ArgumentListで安全側に寄せた。 | 簡易なセキュリティーリスク対策を初回実装に組み込むため。 |

### v0.14.38-test-runner-command-profile: Studioくん Test Run / TestRunner.ps1 CommandProfile連携
- 作業ID: studio_work_0063
- 種別: feature
- 分類: test_runner_command_profile
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: Program.cs / FRBStudio.csproj / appsettings.json / tools/test/TestRunner.ps1 / data/json/04_tools/test_runner_run_config_data_v0_1.json / defs/tools/test_runner_run_config_view_def_v0_1.json / wwwroot/js/actions/action_registry.js / wwwroot/index.html / runtime notes

#### 目的

Studioくんから許可済みのテスト実行プリセットを選択し、Grid上部の Test Run ボタンで TestRunner.ps1 を起動できるようにする。コマンド入力が苦手な人間でも、意味の分かるCaption付きData JSON行を選ぶだけで、Playwright UI起動やNode標準テスト実行を再現可能にする。

#### 背景

v0.14.37 Git Diff Run / CommandProfile連携により、CLIコマンドの引数やパスをData JSONプリセットとして画面化し、Program.cs側の許可済みCommandProfileだけを安全に実行する道筋が見えた。次の枝として、AI駆動開発の作業台に必要なTest RunnerをStudioくんから起動できるようにする。

#### 対象範囲

TestRunner.ps1 を追加し、Data JSON側の test_runner_id / caption / run_mode / command_preview などから、許可済みテストだけを起動する。初期Data JSONは最低2行とし、playwright_ui は `npx playwright test --ui` を起動する launch 型、incident_prompt_copy_action_static は `node --test tests/qa/static/incident_prompt_copy_action_viewdef_static.test.mjs` を実行して終了を待つ wait 型とする。Program.cs側は test_runner CommandProfileまたは既存CommandProfile APIの拡張で TestRunner.ps1 のみを許可し、Data JSONから任意commandLine/scriptPath/test_fileを受け付けない。ViewDefにはGrid上部の `Test Run` executeButton を用意する。

#### 対象外

任意コマンドランナー化、Data JSONに自由なcommandLine/args/scriptPath/test_fileを持たせること、全テストファイルの自由選択、テスト結果の詳細JSON化、Playwright UIプロセス管理画面、テスト履歴管理、Expected/Actual/Diffの自動生成まではこの初回スコープに含めない。

#### 固定名方針

command_profile_id / test_runner_id / run_mode はCommandProfile/TestRunner実行契約上の識別子として扱う。Runtimeが特定テストファイル名や任意Dataフィールド名を固定参照するのではなく、ViewDefとData JSONで宣言された実行プリセットをActionContextとしてProgram.csへ渡す。

#### module化方針

type="module" 化は行わず、既存のActionRegistry / toolbar.executeButton / Program.cs Minimal API 構成を維持する。v0.14.37のCommandProfile Runner方針を踏襲し、必要最小限の追加で進める。

#### リスク

Playwright UIは起動後に終了しない可能性が高く、wait型で扱うとAPIが返らずtimeoutになる。任意コマンド化するとコマンドインジェクションや任意ファイル実行のリスクがある。node --testはexit_codeで成否を返せるが、作業ディレクトリやnode/npxのPATH依存で実行失敗する可能性がある。静的ホスティングではサーバー側実行ができないため、ボタン実行不可または分かりやすいエラーが必要。

#### 確認観点

Data JSONに最低2行のテスト実行プリセットが存在すること。Playwright UI行は run_mode=launch としてAPIが起動後に返ること。Node static test行は run_mode=wait として終了まで待ち、exit_code/stdout/stderr/duration_msを返すこと。Data JSONに自由commandLineを書いても実行されないこと。test_runner_idが許可値以外の場合は拒否されること。静的ホスティングではTest Runが実行不可になること。Grid上部のTest Runボタンから選択行の設定で実行できること。

#### 作業会話サマリ


##### 依頼 / 方針

Git Diff Run の成功で、Studioくんがコマンド引数をData JSONプリセットとして画面化できる可能性が見えた。次はTest Runnerまで行きたい。TestRunnerというスクリプトを作り、パラメータでどちらのコマンドを実行するかを選ぶイメージ。JSONデータとしては最低2行で、`npx playwright test --ui` と `node --test tests/qa/static/incident_prompt_copy_action_viewdef_static.test.mjs` を扱いたい。まずは会話し、その後AI駆動開発の作業台を作り始めるため、インシデント追加を依頼。

##### AI整理

方針合意。Test RunnerはGit Diff Runの次の自然な枝として、CommandProfile Runnerに test_runner profile を追加するのがよい。Playwright UIは起動しっぱなしになるため run_mode=launch、node --test は終了を待つ run_mode=wait として扱う。Data JSONには test_runner_id と表示用 command_preview を持たせるが、任意commandLineや自由test_fileは持たせない。TestRunner.ps1内部で許可済みIDだけを分岐実行する。

##### 追加コメント

最新資材添付。v0.14.38-test-runner-command-profile として、.cs関連は Program.cs フォルダー内で更新し、他と混ぜない方針で TestRunner.ps1 / Test Run CommandProfile連携の実装を依頼。

# 2026-06-27 起動確認結果
Playwright UI行で Test Run を押すと「Actionエラー: TestRunnerの起動に失敗しました」と表示された。

##### AI追加回答

v0.14.38.1 launch mode 起動失敗修正完了。run_mode=launch では stdout/stderr をリダイレクトしないため、StandardOutputEncoding / StandardErrorEncoding を設定しないよう Program.cs を修正。run_mode=wait の時だけ出力をリダイレクトし、UTF-8 encoding を設定する。更新は .cs関連フォルダー内の Program.cs/Program.cs に限定。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0063_001 | 2026-06-27 | user | Test Runner構想 | TestRunnerというスクリプトを作り、パラメータで `npx playwright test --ui` と `node --test tests/qa/static/incident_prompt_copy_action_viewdef_static.test.mjs` のどちらを実行するか選ぶイメージを相談。Data JSONは最低2行を想定。 |
| disc_0063_002 | 2026-06-27 | assistant | Test Runner方針整理 | Playwright UIは起動後に待ち続ける可能性があるため run_mode=launch、node --test は終了を待つ run_mode=wait として扱う方針を提案。Data JSONには任意commandLineではなく test_runner_id と表示用command_previewを持たせ、Program.cs/TestRunner.ps1側で許可済みIDだけを実行する設計にする。 |
| disc_0063_003 | 2026-06-27 | user | インシデント追加依頼 | AI駆動開発の作業台を作りはじめる流れとして、Test Runner / CommandProfile連携のインシデント追加を依頼。 |
| disc_0063_004 | 2026-06-27 | assistant | インシデント登録 | studio_work_0063 v0.14.38-test-runner-command-profile として、Studioくん Test Run / TestRunner.ps1 CommandProfile連携を未着手インシデント登録。 |
| disc_0063_005 | 2026-06-27 | user | v0.14.38作業依頼 | incident_file と phase を指定し、Foundation Rules foundation_rule_019 に基づいて TestRunner.ps1 / Test Run CommandProfile連携の実装を依頼。.cs関連はProgram.csフォルダー内で更新し、他と混ぜないよう指定。 |
| disc_0063_006 | 2026-06-27 | assistant | v0.14.38作業結果 | test_runner CommandProfile、TestRunner.ps1、Test Runner実行設定Data/ViewDef、RunCommandProfile Action拡張、Program.cs launch/wait制御を実装。Playwright UIはlaunchで起動後すぐ返し、Node静的テストはwaitで終了まで待つ構成にした。 |
| disc_0063_005 | 2026-06-27 | user | v0.14.38 TestRunner launch mode 起動失敗報告 | Playwright UI行でTest Runを押すと、通知後に「Actionエラー: TestRunnerの起動に失敗しました」と表示された。TestRunner.ps1は tools/test 配下に存在する。 |
| disc_0063_006 | 2026-06-27 | assistant | v0.14.38.1 起動失敗修正結果 | launch modeではstdout/stderrをリダイレクトしないのにStandardOutputEncoding/StandardErrorEncodingを設定していたため、Process.Start失敗の原因になっていた可能性が高い。wait mode時だけencodingを設定するようProgram.csを修正。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0063_001 | 2026-06-27 | Test Runnerは任意コマンドランナーではなく、許可済みtest_runner_idだけを実行するCommandProfile連携として設計する。 | 画面から自由commandLineを実行できる設計にすると、コマンドインジェクションや任意ファイル実行のリスクが高くなるため。 |
| dec_0063_002 | 2026-06-27 | Playwright UIはrun_mode=launch、node --testはrun_mode=waitとして扱う。 | `npx playwright test --ui` はUI起動後に終了しない可能性が高く、通常のwait実行ではtimeoutや失敗扱いになりやすいため。 |
| dec_0063_003 | 2026-06-27 | Data JSONのcommand_previewは表示専用とし、実行正本にはしない。 | 人間には実行されるコマンドのイメージを見せたいが、その文字列を実行すると任意コマンド実行に近づくため。 |
| dec_0063_004 | 2026-06-27 | 初期Data JSONは最低2行で開始する。 | まずPlaywright UI起動とNode静的テスト実行の2パターンを通し、AI駆動開発の作業台としての勝ちパターンを小さく確認するため。 |
| dec_0063_005 | 2026-06-27 | .cs関連ファイルはProgram.csフォルダー配下で更新する。 | ユーザー指定により、Program.cs / csproj / appsettings / TestRunner.ps1 を他のルートファイルと混ぜず、Program.csフォルダー内で管理するため。 |
| dec_0063_006 | 2026-06-27 | 既存の /api/actions/command/run と RunCommandProfile を拡張し、test_runner profileを追加する。 | Git Diff Runで作ったCommandProfile Runnerの導線を再利用し、テスト実行専用の任意コマンドランナーを別途増やさずに済ませるため。 |
| dec_0063_007 | 2026-06-27 | TestRunner.ps1 は test_runner_id の許可値だけを分岐実行し、Data JSONのcommand_previewは表示専用とする。 | コマンド入力を楽にしつつ、画面から任意commandLineや任意test_fileを実行できる状態にしないため。 |
| dec_0063_006 | 2026-06-27 | run_mode=launch では StandardOutputEncoding / StandardErrorEncoding を設定しない。 | stdout/stderrをリダイレクトしないProcessStartInfoにencodingを指定するとProcess.Start時に失敗する可能性があるため。launch系は起動して返すことを優先し、出力取得はwait系に限定する。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0063_001 | 2026-06-27 | incident_added | Studioくんからテスト実行コマンドをData JSONプリセットとして起動する作業項目がインシデント管理JSONに存在しなかった。 | studio_work_0063 v0.14.38-test-runner-command-profile として、Test Run / TestRunner.ps1 CommandProfile連携を未着手インシデント登録した。 | Git Diff Runで見えたCommandProfile Runnerの可能性を、AI駆動開発の作業台としてTest Runnerへ展開するため。 |
| chg_0063_002 | 2026-06-27 | test_runner_command_profile_runtime_added | Studioくんからテスト実行プリセットを選択して安全に起動するCommandProfile / Data JSON / ViewDef / Actionが存在しなかった。 | test_runner CommandProfile、TestRunner.ps1、test_runner_run_config Data/ViewDef、RunCommandProfile拡張を追加し、選択行からTest Runを実行できる入口を作った。 | AI駆動開発の作業台として、コマンドが苦手でもCaption付きプリセット行を選んでテストを起動・実行できるようにするため。 |
| chg_0063_003 | 2026-06-27 | test_runner_launch_wait_policy_added | Playwright UIのような起動しっぱなし系と、node --testのような終了待ち系を同じwait実行として扱うと、timeoutや失敗扱いになる可能性があった。 | playwright_ui は run_mode=launch として起動後すぐAPIを返し、incident_prompt_copy_action_static は run_mode=wait として exit_code/stdout/stderr/duration_ms を返す。 | テスト種別ごとの実行特性に合わせて、APIの応答体験と安全性を両立するため。 |
| chg_0063_004 | 2026-06-27 | test_runner_launch_encoding_fix | run_mode=launch でも ProcessStartInfo.StandardOutputEncoding / StandardErrorEncoding を設定していた。 | redirectOutput=true、つまり run_mode=wait の時だけ stdout/stderr encoding を設定する。run_mode=launch ではencodingを設定しない。 | Playwright UI起動時の TestRunnerの起動に失敗しました エラーを解消するため。 |

### v0.14.39-test-runner-result-classification: Studioくん Test Runner 結果分類 / テスト失敗通知改善
- 作業ID: studio_work_0064
- 種別: improvement
- 分類: test_runner_result_ui
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: Program.cs/Program.cs / wwwroot/js/actions/action_registry.js / data/json/04_tools/test_runner_run_config_data_v0_1.json / defs/tools/test_runner_run_config_view_def_v0_1.json / Program.cs/tools/test/TestRunner.ps1 if needed / data/json/01_main/studio_work_incident_data_v0_64_test_runner_result_classification_added.json

#### 目的

TestRunner wait mode の exit_code=1 をAction起動エラーとして扱わず、ランチャー起動失敗・テスト成功・テスト失敗を result_kind で分類して返し、Studioくん画面上でもテスト失敗を専用通知として表示できるようにする。

#### 背景

v0.14.38 Test Runner CommandProfile連携により、Studioくんから Playwright UI / node --test を起動できるようになった。一方、node --test が正常に起動してテスト本体がfailした場合でも、現状は「Actionエラー: TestRunner が失敗しました: exit_code=1」と表示され、TestRunnerの起動失敗とテスト失敗が混同される。AI駆動開発の作業台としては、コマンド起動失敗ではなくテスト結果としてfailを確認できる表示へ分離する必要がある。

#### 対象範囲

Program.cs の /api/actions/command/run 応答に result_kind を追加する。result_kind は launcher_error / test_passed / test_failed を基本とする。wait mode でプロセス起動に成功し exit_code=0 の場合は test_passed、exit_code!=0 の場合は test_failed とし、Process.Start失敗・Profile不正・Script不在・timeoutなど実行基盤側の失敗は launcher_error として扱う。ActionRegistry側では result_kind に応じて通知文言とトースト種別を分け、test_failed はエラートーストではなく「テスト失敗」通知として表示する。stdout / stderr / output artifact path をユーザーが確認できる形で返す・表示する。

#### 対象外

この作業ではテスト本体の期待値修正、Playwright specの合否改善、差分JSONの中身の判定ロジック変更、テストレポートViewerの本格実装、複数テストの一括実行管理、Playwright UI内の実行制御までは行わない。まず起動失敗とテスト失敗の表示分類を整える。

#### 固定名方針

result_kind / exit_code / stdout / stderr / output_artifacts はCommandProfile実行結果の標準レスポンス候補として扱う。ただしRuntimeが特定テストファイル名や特定diffファイル名を決め打ちしない。artifact path はData JSONまたはTestRunner.ps1の許可済みtest_runner_idに紐づく表示・返却情報として扱う。

#### module化方針

type="module" 化は行わず、既存のActionRegistry / toolbar.executeButton / Program.cs Minimal API 構成を維持する。

#### リスク

exit_code=1 を常にテスト失敗と扱うと、Script内部の前提不足や環境不備までテスト失敗に見えるリスクがある。そのため Process.Start失敗、profile/script/arg検証失敗、timeout、PowerShell起動失敗などは launcher_error として分ける必要がある。stdout/stderrを長く表示しすぎると画面通知が読みにくくなるため、詳細表示と短い通知を分ける必要がある。

#### 確認観点

node --test が pass した場合に result_kind=test_passed となり成功通知になること。node --test が fail した場合に result_kind=test_failed となり、Action起動エラーではなくテスト失敗通知になること。存在しないscript/profile不正/timeout等では result_kind=launcher_error となり、従来どおり起動・実行基盤のエラーとして表示されること。stdout/stderrとoutput artifact pathがAPIレスポンスまたは画面表示で確認できること。Playwright UI launch行の起動成功表示に悪影響がないこと。

#### 作業会話サマリ


##### 依頼 / 方針

wait mode の exit_code=1 を「Action起動エラー」と呼ばない。result_kind として launcher_error / test_passed / test_failed を返す。テスト失敗時はエラートーストではなく「テスト失敗」通知にする。stdout / stderr / output artifact path を表示できるようにする。

##### AI整理

TestRunner結果分類の改善インシデントとして登録する。v0.14.38でTestRunnerの起動とテスト実行は成立したため、次は起動基盤の失敗とテスト本体の失敗を分離し、AI駆動開発の作業台として人間が判断しやすい通知・証跡表示へ進める。

##### 追加コメント

v0.14.39-test-runner-result-classification として、綺麗状態を目指し、wait modeのテスト失敗とAction起動エラーを分離する実装を依頼。

##### AI追加回答

v0.14.39-test-runner-result-classification 対応完了。Program.cs は TestRunner APIレスポンスへ result_kind を追加し、wait modeでexit_code=0なら test_passed、exit_code!=0なら test_failed、起動・環境・timeout系は launcher_error として返すようにした。test_failed はHTTP 200で返すため、ActionToolbarのcatchへ落ちず、Action起動エラー扱いにならない。ActionRegistry は test_failed 時に「テスト失敗」通知を出し、stdout / stderr / output_artifacts を確認できる結果ダイアログを表示する。TestRunner Run Config Data/ViewDefには output_artifact_path を表示項目として追加した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0064_001 | 2026-06-27 | user | TestRunner結果表示の違和感 | node --test 実行は動いたが、テスト本体がfailした場合に Actionエラー: TestRunner が失敗しました: exit_code=1 と表示される。 |
| disc_0064_002 | 2026-06-27 | assistant | 改善方針 | Runner起動失敗ではなくテスト失敗を拾えている状態なので、wait mode の exit_code=1 をAction起動エラーと呼ばず、result_kindで launcher_error / test_passed / test_failed を分けるのがよい。 |
| disc_0064_003 | 2026-06-27 | user | インシデント追加依頼 | wait mode の exit_code=1 をAction起動エラーと呼ばない。result_kindを返す。テスト失敗時はテスト失敗通知にする。stdout/stderr/output artifact pathを表示できるようにする、という内容をインシデントに追加してほしい。 |
| disc_0064_004 | 2026-06-27 | user | v0.14.39作業依頼 | 綺麗状態を目指し、v0.14.39-test-runner-result-classification の実装を依頼。Foundation Rules foundation_rule_019 のZIP返却契約を参照。 |
| disc_0064_005 | 2026-06-27 | assistant | v0.14.39作業結果 | Program.csでresult_kindを返すようにし、test_failedはHTTP 200で返却。ActionRegistry/ActionToolbarでtest_failed通知をwarn扱いにし、stdout/stderr/output_artifactsを結果ダイアログで確認可能にした。TestRunner Run Config Data/ViewDefへoutput_artifact_pathを追加。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0064_001 | 2026-06-27 | wait modeでプロセス起動に成功した後のexit_code!=0は、原則としてtest_failedとして扱う。 | TestRunnerやActionの起動失敗と、テスト本体の失敗を混同すると、人間が見るべき対象が分かりにくくなるため。 |
| dec_0064_002 | 2026-06-27 | Process.Start失敗、Profile不正、Script不在、timeoutなど実行基盤側の失敗はlauncher_errorとして扱う。 | テスト本体のfailとは異なり、Studioくん・CommandProfile・環境設定側を確認すべきエラーだから。 |
| dec_0064_003 | 2026-06-27 | test_failedはエラートーストではなく、テスト失敗通知として表示する。 | テスト失敗はAI駆動開発の作業台では正常に観測された結果であり、ランチャー故障のように見せないため。 |
| dec_0064_004 | 2026-06-27 | stdout / stderr / output artifact path をレスポンスまたは画面から確認できるようにする。 | テスト失敗時に、diff JSONやログへすぐ辿れないと、次の判断・MetaDiff・差分物語へ進みにくいため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0064_001 | 2026-06-27 | incident_added | TestRunner wait mode の exit_code=1 が Action起動エラーとして表示され、テスト失敗とランチャー失敗の境界が曖昧だった。 | studio_work_0064 として、result_kindによるTestRunner結果分類と、テスト失敗通知・stdout/stderr/artifact path表示改善を登録。 | AI駆動開発の作業台として、テスト結果を人間が判断しやすい形で観測できるようにするため。 |
| chg_0064_002 | 2026-06-27 | test_runner_result_classification_backend | TestRunner wait modeでexit_code!=0の場合、success=falseかつHTTP 500相当で返り、フロント側ではAction起動エラーと同じ経路で扱われていた。 | TestRunner wait modeでプロセス起動後にexit_code!=0となった場合は result_kind=test_failed としてHTTP 200で返す。exit_code=0はtest_passed、起動・設定・timeout系はlauncher_errorとして返す。 | テスト本体のfailとランチャー・環境側の失敗を分離し、人間が見るべき対象を明確にするため。 |
| chg_0064_003 | 2026-06-27 | test_runner_result_classification_frontend | ActionToolbarはexecuteStudioActionの例外をすべて「Actionエラー」としてsetStatusしていた。ActionRegistryも非2xx応答を常にthrowしていた。 | ActionRegistryはresult_kind=test_failedを通常結果として扱い、テスト失敗通知と詳細ダイアログを返す。ActionToolbarはAction結果のstatusOptionsをsetStatusへ渡し、テスト失敗をerrorではなくwarn通知で表示する。 | テスト失敗を「壊れた」ではなく、AI駆動開発の作業台で観測されたテスト結果として扱うため。 |
| chg_0064_004 | 2026-06-27 | test_runner_artifact_path_display | TestRunner Run Config上では、テストがどのdiff JSONを更新するかが画面から辿りにくかった。 | Data JSON/ViewDefにoutput_artifact_pathを追加し、APIレスポンスにもoutput_artifactsを含めることで、stdout/stderrとあわせて差分JSONへ辿れるようにした。 | テスト失敗後にdiff JSON・MetaDiff・差分物語へ進みやすくするため。 |

### v0.15.1-common-enums-definition: common_enums_v0_1.json 追加 / Enumを値の正本として定義
- 作業ID: studio_work_0065
- 種別: data_design
- 分類: enum
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: data/json/00_rules/common_enums_v0_1.json, defs/common/common_enums_view_def_v0_1.json, data/json/00_rules/COMMON_ENUMS_DEFINITION_REPORT_v0_15_1.md, data/json/01_main/studio_work_incident_data_v0_74_proposal_driven_jobflow_added.json

#### 目的

EnumをStudioくんの値語彙の最小管理単位として追加し、cd/name/description/sort_order/deprecatedなどを持てる共通定義ファイルを作る。

#### 背景

common_types_v0_1.json は意味つきFieldTypeカタログとして成立しているが、select options がFieldType内に直書きされており、値候補そのものの正本管理がまだ分離されていない。context_read_timing、status、risk、severity、trustなどは複数FieldType・ViewDef・Data・AI文脈制御で共有されるため、Enumとして管理する必要がある。

#### 対象範囲

common_enums_v0_1.json を追加し、namespaces / enums / items の基本構造を定義する。items は cd / name / description / sort_order / deprecated を基本候補とする。まずは器と契約を作り、既存optionsの全面移行は後続インシデントで扱う。

#### 対象外

この作業では既存 common_types_v0_1.json 内のoptionsを一括移行しない。Studio Runtime側の enumRef 解決実装も次インシデントに分ける。まず値の正本ファイルの構造を定める。

#### 固定名方針

Runtimeが特定Dataフィールド名を決め打ちしない方針を維持する。Enum / FieldType / ViewDef / Data の責務を分け、値の正本はEnum、画面項目としての使い方はFieldType、配置はViewDef、実値はDataとして扱う。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式と既存common_types運用を前提に、まずData/定義/解決ルールを段階的に追加する。

#### リスク

Enumを何でも入れる共通ごった煮にすると管理不能になる。namespaceを切り、値の意味単位を守る必要がある。risk.high / priority.high / confidence.high はcdが似ていても意味が違う可能性があるため、安易に統合しない。

#### 確認観点

common_enums_v0_1.json がUTF-8日本語可読で保存されること。namespace.enums.items で複数Enumを表現できること。既存common_typesを壊さず、まだenumRef未対応でも既存画面が動くこと。

#### 作業会話サマリ


##### 依頼 / 方針

Enumは管理の最小単位として必要。common_typesはFieldTypeの共通管理として使い、Enumは値の正本として分離したい。

##### AI整理

common_enums_v0_1.json を追加し、Enumを値語彙の正本として扱うための namespaces / enums / items 構造と enumRef形式を定義した。既存common_types optionsの移行とRuntime enumRef解決は後続インシデントへ分離した。

##### 追加コメント

Enumの仕掛けを作った後、既存のOptionでだらだら書いているものを整理したい。まずインシデントとして追加したい。

##### AI追加回答

v0.15.1-common-enums-definition として、data/json/00_rules/common_enums_v0_1.json を追加。Enum参照形式を {namespace_id}.{enum_id} とし、item標準項目を cd/name/description/sort_order/deprecated として定義。代表Enumとして studio.lifecycle_status、qa.risk_level、qa.severity_level、relation.status、relation.confidence、relation.priority を収録した。既存 common_types_v0_1.json は壊さず未変更とし、enumRef解決・既存options移行・context.read_timing本追加は後続インシデントへ残した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0065_001 | 2026-06-27 | user | Enum / FieldType / Context制御の設計相談 | common_types_v0_1.json の現状を確認し、FieldTypeとしてできていること、Enumとして未分離なことを整理した。context_read_timing などはEnumが管理の最小単位になると判断した。 |
| disc_0065_002 | 2026-06-27 | assistant | 作業分割提案 | Enum定義追加、FieldType enumRef解決、context系Enum追加、既存optionsのEnum参照化、ViewDef文脈制御 read_contract対応の5件に分けてインシデント登録する方針を提案した。 |
| disc_0065_003 | 2026-06-27 | user | インシデント追加依頼 | Enumの仕掛けを作った後に、既存のOptionでだらだら書いているものを整理したい。インシデント追加と更新後JSON返却を依頼。 |
| disc_0065_004 | 2026-06-28 | user | 作業依頼 | v0.15.1-common-enums-definition として、憲法を参照し、戦略的設計パターンを目指して common_enums_v0_1.json 追加作業を依頼。 |
| disc_0065_005 | 2026-06-28 | assistant | 作業結果 | Foundation Rule 19を参照し、phaseを studio_work_0065 として特定。common_enums_v0_1.json と common_enums_view_def_v0_1.json、設計レポートを追加し、既存common_types options移行とRuntime enumRef解決はスコープ外として温存した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0065_001 | 2026-06-27 | Enumを値の正本として定義する。 | FieldType内optionsだけでは、複数画面・複数Dataで共有される値語彙の重複や表記揺れを防げないため。 |
| dec_0065_002 | 2026-06-27 | common_enums_v0_1.json を common_types とは別ファイルにする。 | FieldTypeの見た目・編集・検索設定と、値候補そのものの管理責務を分離するため。 |
| dec_0065_003 | 2026-06-27 | 既存optionsの一括移行はこのインシデントでは行わない。 | 仕掛け追加と既存整理を混ぜると差分が大きくなり、回帰リスクが上がるため。 |
| dec_0065_004 | 2026-06-28 | Enum参照形式は {namespace_id}.{enum_id} とする。 | FieldTypeやViewDefから参照する際に、意味領域とEnum本体を明確に分け、同名Enumの衝突を避けるため。 |
| dec_0065_005 | 2026-06-28 | v0.15.1ではcommon_types_v0_1.jsonを変更しない。 | 既存select optionsを壊さず、値正本の器追加と既存移行を分離して回帰リスクを抑えるため。 |
| dec_0065_006 | 2026-06-28 | 代表Enumはサンプル兼移行候補として収録し、既存FieldTypeの正本切替は行わない。 | common_enumsの構造確認に必要な実例を持たせつつ、enumRef解決前に画面表示を壊さないため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0065_001 | 2026-06-27 | incident_added | Enumを値の正本として管理する作業項目が存在しなかった。 | studio_work_0065 として common_enums_v0_1.json 追加を登録。 | FieldType / Enum / ViewDef / Data の責務分離を進めるため。 |
| chg_0065_002 | 2026-06-28 | viewdef_added | common_enums専用の表示・編集ViewDefなし。 | defs/common/common_enums_view_def_v0_1.json を追加し、Namespace一覧、Notes、Change HistoryをStudio上で確認できるようにした。 | Enum正本をData JSONとして扱い、人間がStudioくんで確認・編集できる入口を用意するため。 |
| chg_0065_003 | 2026-06-28 | scope_guard | common_types内optionsの移行やRuntime enumRef解決も同時に行う可能性があった。 | v0.15.1ではcommon_typesを変更せず、既存options移行・Runtime解決・context系Enum本追加を後続インシデントへ分離。 | 仕掛け追加と既存整理を混ぜると差分が大きくなり、回帰リスクが上がるため。 |

### v0.15.2-fieldtype-enumref-resolve: common_types FieldType の enumRef / options解決対応
- 作業ID: studio_work_0066
- 種別: feature
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/js/core/state.js, wwwroot/js/core/field_types.js, wwwroot/index.html, defs/common/common_types_v0_1.json, data/json/00_rules/common_enums_v0_1.json, data/json/00_rules/FIELDTYPE_ENUMREF_RESOLVE_REPORT_v0_15_2.md, data/json/01_main/studio_work_incident_data_v0_74_proposal_driven_jobflow_added.json

#### 目的

FieldTypeからEnumを参照できるようにし、baseType=select かつ enumRefありの場合に common_enums のitemsをoptionsとして解決できるようにする。

#### 背景

既存のcommon_types_v0_1.jsonはFieldType内にoptionsを直持ちしている。今後は enumRef を追加し、Enumを値の正本、FieldTypeを画面項目としての使い方として分ける必要がある。既存方式との互換を保ちながら、段階的にenumRefへ寄せる。

#### 対象範囲

common_types の fieldTypes に enumRef を持てるようにする。baseType=select かつ enumRef がある場合、common_enums の該当Enumを解決して選択肢として扱う。optionsのみの場合は従来どおりローカル選択肢として扱う。enumRef と options が両方ある場合は、enumRef側を正本とし、optionsは互換用・キャッシュ・展開結果として扱う方針を定義する。

#### 対象外

この作業では既存FieldTypeのoptionsを大量にenumRef化しない。まず enumRef の解決ルールと互換方針を作る。既存options整理は v0.15.4 側で扱う。

#### 固定名方針

Runtimeが特定Dataフィールド名を決め打ちしない方針を維持する。Enum / FieldType / ViewDef / Data の責務を分け、値の正本はEnum、画面項目としての使い方はFieldType、配置はViewDef、実値はDataとして扱う。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式と既存common_types運用を前提に、まずData/定義/解決ルールを段階的に追加する。

#### リスク

enumRefとoptionsの両方が存在する場合の優先順位を曖昧にすると、画面表示とData validationがズレる。最初は警告扱い、将来的にはエラー扱いにできる余地を残す。

#### 確認観点

既存options直書きFieldTypeが従来どおり表示・編集できること。enumRefのみのselect FieldTypeがEnumから選択肢を取得できること。enumRef+optionsの併用時にenumRef側を正として扱うこと。Enum未存在時に分かりやすくエラーまたは警告になること。

#### 作業会話サマリ


##### 依頼 / 方針

Enumを定義した上で、FieldType側に enumRef を持たせ、options は enum 由来の展開結果として扱うイメージにしたい。

##### AI整理

common_types のFieldTypeに enumRef を追加し、既存options直書き方式と互換を保ちながらEnum参照へ移行できる仕掛けとして登録する。

##### 追加コメント

v0.15.2-fieldtype-enumref-resolve の作業依頼。常に憲法(frb_coding_constraints)をまず参照し、constitution_03 戦略的設計パターンを目指して作業する。FieldTypeからEnumを参照できるようにし、baseType=select かつ enumRefありの場合に common_enums のitemsをoptionsとして解決できるようにする。

##### AI追加回答

v0.15.2-fieldtype-enumref-resolve 対応完了。FieldType Resolverへ共通Enum解決を追加し、common_enums_v0_1.json を値語彙正本として読み込めるようにした。select/radio系FieldTypeが enumRef を持つ場合、Enum items を options として展開する。enumRef と options が併存する場合は enumRef 側を正本として優先し、既存optionsは互換用・キャッシュ・展開結果として扱う。Enum未存在時は console.warn で警告し、既存optionsがあれば互換表示を継続する。既存optionsの全面移行は行わず、qa.risk に enumRef=qa.risk_level を追加し、enumRefのみ確認用の qa.risk_enumref_only_sample を追加した。JSON parse、wwwroot配下JS node --check、enumRef機能確認を実施済み。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0066_001 | 2026-06-27 | user | Enum / FieldType / Context制御の設計相談 | common_types_v0_1.json の現状を確認し、FieldTypeとしてできていること、Enumとして未分離なことを整理した。context_read_timing などはEnumが管理の最小単位になると判断した。 |
| disc_0066_002 | 2026-06-27 | assistant | 作業分割提案 | Enum定義追加、FieldType enumRef解決、context系Enum追加、既存optionsのEnum参照化、ViewDef文脈制御 read_contract対応の5件に分けてインシデント登録する方針を提案した。 |
| disc_0066_003 | 2026-06-27 | user | インシデント追加依頼 | Enumの仕掛けを作った後に、既存のOptionでだらだら書いているものを整理したい。インシデント追加と更新後JSON返却を依頼。 |
| disc_0066_20260628_user_v0152 | 2026-06-28 | user | v0.15.2-fieldtype-enumref-resolve作業依頼 | 常に憲法(frb_coding_constraints)をまず参照し、constitution_03 戦略的設計パターンを目指して作業する。phase v0.15.2-fieldtype-enumref-resolve として、FieldType enumRef 解決対応を依頼。困ることがあれば推測で進めず中止して相談する。 |
| disc_0066_20260628_ai_v0152 | 2026-06-28 | assistant | v0.15.2-fieldtype-enumref-resolve作業結果 | constitution_03の戦略的設計パターンに従い、個別Dataフィールド名分岐ではなくFieldType ResolverへEnum解決を統合。common_enumsを値正本、FieldTypeを画面項目の使い方として分離し、enumRefをselect/radio系optionsへ解決するRuntimeを追加した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0066_001 | 2026-06-27 | FieldType側に enumRef を追加できるようにする。 | Enumを値の正本、FieldTypeを画面項目としての使い方に分けるため。 |
| dec_0066_002 | 2026-06-27 | optionsのみの場合は従来互換のローカル選択肢として扱う。 | 既存common_types_v0_1.jsonのselect項目を一気に壊さないため。 |
| dec_0066_003 | 2026-06-27 | enumRefとoptionsが両方ある場合はenumRef側を正本とする。 | 値候補の正本を一つにしないと、差分管理とAI文脈制御で意味ズレが起きるため。 |
| dec_0066_20260628_enumref_priority | 2026-06-28 | enumRef と options が併存する場合は enumRef 側を正本として優先する。 | Enumを値候補の正本、optionsを互換用・キャッシュ・展開結果として扱い、画面表示と値語彙の正本を分離するため。 |
| dec_0066_20260628_compat_warn | 2026-06-28 | Enum未存在時は警告扱いとし、既存optionsがあれば互換表示を継続する。 | v0.15.2は移行途中の段階であり、既存ViewDef/FieldTypeを壊さず後続v0.15.4の整理へ接続するため。 |
| dec_0066_20260628_no_mass_migration | 2026-06-28 | 既存FieldType optionsの全面enumRef化は行わず、代表例とサンプルのみ追加する。 | 今回のスコープは解決ルールと互換方針の実装であり、既存options整理はv0.15.4側で扱うため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0066_001 | 2026-06-27 | incident_added | FieldTypeからEnumを参照する作業項目が存在しなかった。 | studio_work_0066 として common_types FieldType の enumRef / options解決対応を登録。 | 既存common_types運用を維持しながらEnumレイヤーへ移行するため。 |
| chg_0066_20260628_runtime_enumref | 2026-06-28 | runtime_enumref_resolve | FieldType Resolverはcommon_types options直書き解決のみで、common_enumsを値正本として参照しなかった。 | common_enums_v0_1.jsonを読み込み、select/radio系FieldTypeのenumRefをEnum itemsからoptionsへ展開するRuntimeを追加。 | Enum / FieldType / ViewDef / Data の責務分離をRuntimeへ接続するため。 |
| chg_0066_20260628_common_types_sample | 2026-06-28 | common_types_sample_update | common_types_v0_1.jsonにenumRef確認用FieldTypeがなく、既存options直書きだけだった。 | qa.riskへenumRef=qa.risk_levelを追加し、互換用optionsを保持。qa.risk_enumref_only_sampleを追加。 | enumRef+options併用とenumRefのみの両方を確認可能にするため。 |
| chg_0066_20260628_common_enums_policy | 2026-06-28 | common_enums_runtime_policy_update | common_enums_v0_1.json の runtime_policy は「自動解決しない」だった。 | v0.15.2でRuntimeがenumRef解決する方針へ更新。 | v0.15.1で作ったEnum正本をFieldType Resolverへ接続したため。 |

### v0.15.3-context-enums-added: context系Enum / context_read_timing FieldType追加
- 作業ID: studio_work_0067
- 種別: feature
- 分類: context_enum
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: data/json/00_rules/common_enums_v0_1.json, data/json/00_rules/common_types_v0_1.json, related context ViewDef samples

#### 目的

AI文脈制御で利用する context_read_timing などのEnumを追加し、ViewDefやData行のcontext_refsで使える共通語彙を整える。

#### 背景

ViewDefに文脈制御を持たせる場合、追加文脈は何を読むかだけでなく、いつ読むかが重要になる。before_load / on_row_select / before_review / before_code_update / before_zip_return などは複数ViewDef・複数Data・複数ルールで共通利用されるため、FieldType内のローカルoptionsではなくEnumとして管理する必要がある。

#### 対象範囲

context.read_timing Enumを追加する。候補値は before_load / after_load / on_row_select / before_edit / before_save / before_review / before_diff_story / before_code_update / before_zip_return とする。必要に応じて context.purpose / context.failure_policy / context.trust も候補として整理する。common_types側には context.context_read_timing FieldTypeを追加し、enumRef=context.read_timing を参照する。

#### 対象外

この作業ではViewDefの read_contract 本体実装やData行context_refsの実行制御までは行わない。まずAI文脈制御で使う語彙とFieldTypeを定義する。

#### 固定名方針

Runtimeが特定Dataフィールド名を決め打ちしない方針を維持する。Enum / FieldType / ViewDef / Data の責務を分け、値の正本はEnum、画面項目としての使い方はFieldType、配置はViewDef、実値はDataとして扱う。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式と既存common_types運用を前提に、まずData/定義/解決ルールを段階的に追加する。

#### リスク

timing値をViewDefごとにベタ書きすると before_ai_review / before_review のような表記揺れが起きる。Enum正本を使って語彙を固定する必要がある。

#### 確認観点

context.read_timing の全候補がEnumに定義されていること。context_read_timing FieldTypeがenumRefで参照できること。ViewDefでselect項目として使えること。descriptionに読みタイミングの意味が残っていること。

#### 作業会話サマリ


##### 依頼 / 方針

before_load / after_load / on_row_select / before_edit / before_save / before_review / before_diff_story / before_code_update / before_zip_return のようなtimingを共通管理したい。

##### AI整理

context_read_timing はEnum初回ユースケースとしてちょうどよい。AI文脈制御の共通語彙として追加するインシデントを登録する。

##### 追加コメント

v0.15.3確認中、context_refs_sample の読みタイミングselectで共通Enum定義JSON json/00_rules/common_enums_v0_1.json の404が発生。/api/data の起点に合わせたパス補正を依頼。

##### AI追加回答

v0.15.3.1補修として、DEFAULT_COMMON_ENUMS_FILE を 00_rules/common_enums_v0_1.json に修正し、commonEnumSources の data/json・json prefix をAPI相対パスへ正規化。context.read_timing と context.context_read_timing も再収録し、context_refs_sample_view_def に正しい commonEnumSources を明示した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0067_001 | 2026-06-27 | user | Enum / FieldType / Context制御の設計相談 | common_types_v0_1.json の現状を確認し、FieldTypeとしてできていること、Enumとして未分離なことを整理した。context_read_timing などはEnumが管理の最小単位になると判断した。 |
| disc_0067_002 | 2026-06-27 | assistant | 作業分割提案 | Enum定義追加、FieldType enumRef解決、context系Enum追加、既存optionsのEnum参照化、ViewDef文脈制御 read_contract対応の5件に分けてインシデント登録する方針を提案した。 |
| disc_0067_003 | 2026-06-27 | user | インシデント追加依頼 | Enumの仕掛けを作った後に、既存のOptionでだらだら書いているものを整理したい。インシデント追加と更新後JSON返却を依頼。 |
| disc_0067_20260628_001_context_enum_api_path_404 | 2026-06-28 | user | context.read_timing select 404報告 | context_refs_sample の読みタイミングselect確認時に、共通Enum定義JSON[json/00_rules/common_enums_v0_1.json] の /api/data/json/00_rules/common_enums_v0_1.json 読込が404になった。 |
| disc_0067_20260628_002_context_enum_api_path_fix | 2026-06-28 | assistant | context.read_timing select 404補修結果 | /api/data は data/json 起点であるため、Runtime既定Enumパスを 00_rules/common_enums_v0_1.json へ補正。data/json/ または json/ prefix が混入してもAPI相対パスへ正規化する処理を追加した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0067_001 | 2026-06-27 | context.read_timing を共通Enumとして追加する。 | AI文脈制御の読みタイミングは複数箇所で共有される制御語彙であり、FieldType内ローカルoptionsでは表記揺れを防ぎにくいため。 |
| dec_0067_002 | 2026-06-27 | context_read_timing FieldTypeは common_types 側に追加する。 | Enumを画面上のselect項目として使うためには、caption/grid/edit/searchを持つFieldTypeが必要なため。 |
| dec_0067_003 | 2026-06-27 | ViewDef read_contractの本体実装は別インシデントに分ける。 | 語彙定義と文脈制御実行を混ぜると作業範囲が肥大化するため。 |
| dec_0067_20260628_001_common_enum_api_relative_path | 2026-06-28 | commonEnumSources / DEFAULT_COMMON_ENUMS_FILE は /api/data の起点(data/json)からの相対パスで統一する。 | json/00_rules を渡すと /api/data/json/00_rules となり、実ファイル data/json/00_rules/common_enums_v0_1.json と対応しないため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0067_001 | 2026-06-27 | incident_added | context_read_timing などのAI文脈制御語彙が共通Enumとして登録されていなかった。 | studio_work_0067 として context系Enum / context_read_timing FieldType追加を登録。 | ViewDef文脈制御の前提となる共通語彙を整えるため。 |
| chg_0067_20260628_001_common_enum_api_path_fix | 2026-06-28 | bugfix | DEFAULT_COMMON_ENUMS_FILE が json/00_rules/common_enums_v0_1.json で、API呼び出しが /api/data/json/00_rules/common_enums_v0_1.json となり404。 | DEFAULT_COMMON_ENUMS_FILE を 00_rules/common_enums_v0_1.json に補正し、normalizeDataJsonApiPath で data/json/・json/ prefix を除去。 | context.read_timing の選択肢をDetail selectへ表示できるようにするため。 |

### v0.15.4-common-types-options-to-enumref: 既存 common_types options のEnum参照化整理
- 作業ID: studio_work_0068
- 種別: refactoring
- 分類: common_types_cleanup
- 優先度: medium
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: defs/common/common_types_v0_1.json, data/json/00_rules/common_enums_v0_1.json, data/json/00_rules/COMMON_TYPES_OPTIONS_TO_ENUMREF_REPORT_v0_15_4.md

#### 目的

既存common_types_v0_1.jsonでFieldType内にだらだら直書きされているselect optionsを棚卸しし、共通Enumへ移せるものは enumRef 参照へ寄せる。

#### 背景

common_types_v0_1.json には qa.risk / relation.status / relation.confidence / relation.priority / severity など、似た選択肢を持つFieldTypeが複数ある。現状は実用的だが、値の正本がFieldTypeごとに分散しているため、表記揺れ・意味ズレ・重複更新が起きやすい。

#### 対象範囲

既存FieldTypeのoptionsを棚卸しし、Enum化候補を分類する。risk / severity / confidence / priority の high/medium/low 系は、同じEnumに統合できるか、意味別Enumに分けるかを判断する。relation.status、relation.coverage、node_type、relation_type、qa.feature_area、test_axis、quality_axis、check_axis、scenario_type、finding_type などを対象候補として確認する。移行する場合はFieldType側へ enumRef を追加し、optionsは削除またはキャッシュ扱いにする。

#### 対象外

この作業では一気に全optionsを統合しない。意味が違う high/medium/low を雑に共通化しない。まず棚卸し、分類、段階的移行を行う。

#### 固定名方針

Runtimeが特定Dataフィールド名を決め打ちしない方針を維持する。Enum / FieldType / ViewDef / Data の責務を分け、値の正本はEnum、画面項目としての使い方はFieldType、配置はViewDef、実値はDataとして扱う。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式と既存common_types運用を前提に、まずData/定義/解決ルールを段階的に追加する。

#### リスク

意味が似ているだけで同じEnumへ統合すると、risk.high と confidence.high のように意味の違う値が混ざる。逆に分けすぎるとEnumの再利用価値が下がる。判断ログを残す必要がある。

#### 確認観点

既存FieldTypeのselect項目が移行後も表示・編集・検索できること。Enum化した選択肢がData既存値と一致すること。意味が違う値を無理に統合していないこと。options削除/残置の方針が記録されていること。

#### 作業会話サマリ


##### 依頼 / 方針

enumの仕掛けを作った後に、既存のOptionでだらだら書いているやつを整理したい。

##### AI整理

common_types既存select optionsを棚卸しし、qa/relation系の代表FieldTypeへenumRefを追加。common_enumsへ対応Enumを追加し、既存optionsは互換用スナップショットとして残置した。risk/confidence/priority/severityなど意味の違うhigh/medium/low系は統合せず、意味別Enumとして分離。

##### 追加コメント

common_typesの中にある既存Option群を、Enum正本に寄せていきたい。ただし意味の違いは丁寧に見る必要がある。

##### AI追加回答

common_types既存select optionsを棚卸しし、qa/relation系の代表FieldTypeへenumRefを追加。common_enumsへ対応Enumを追加し、既存optionsは互換用スナップショットとして残置した。risk/confidence/priority/severityなど意味の違うhigh/medium/low系は統合せず、意味別Enumとして分離。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0068_001 | 2026-06-27 | user | Enum / FieldType / Context制御の設計相談 | common_types_v0_1.json の現状を確認し、FieldTypeとしてできていること、Enumとして未分離なことを整理した。context_read_timing などはEnumが管理の最小単位になると判断した。 |
| disc_0068_002 | 2026-06-27 | assistant | 作業分割提案 | Enum定義追加、FieldType enumRef解決、context系Enum追加、既存optionsのEnum参照化、ViewDef文脈制御 read_contract対応の5件に分けてインシデント登録する方針を提案した。 |
| disc_0068_003 | 2026-06-27 | user | インシデント追加依頼 | Enumの仕掛けを作った後に、既存のOptionでだらだら書いているものを整理したい。インシデント追加と更新後JSON返却を依頼。 |
| disc_0068_001 | 2026-06-28 | user | 作業依頼 | v0.15.4-common-types-options-to-enumref として、common_typesの既存Option群をEnum正本に寄せる作業を依頼。00_rules/common_enums_v0_1.json は参照が多いため移動せず戻した。 |
| disc_0068_002 | 2026-06-28 | assistant | 作業結果 | common_typesのselect FieldTypeを棚卸しし、qa/relation系の代表FieldTypeにenumRefを追加。common_enumsへ対応Enumを追加し、既存optionsは互換用スナップショットとして残した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0068_001 | 2026-06-27 | 既存options整理は enumRef解決対応後に行う。 | 仕掛けがない状態でoptionsを消すと既存ViewDef/画面が壊れるため。 |
| dec_0068_002 | 2026-06-27 | high/medium/low系は安易に一つのEnumへ統合しない。 | risk、severity、confidence、priorityでは同じcdでも意味と判断軸が違う可能性があるため。 |
| dec_0068_003 | 2026-06-27 | 移行は棚卸し・分類・段階的enumRef化の順で進める。 | 共通化対象とローカル選択肢として残す対象を判断しやすくするため。 |
| dec_0068_001 | 2026-06-28 | common_enums_v0_1.json の配置は data/json/00_rules/common_enums_v0_1.json のまま維持する。 | 既存参照が多く、配置変更は影響範囲が広いため。v0.15.4の主目的はoptionsのenumRef化であり、パス移動は別作業に分離する。 |
| dec_0068_002 | 2026-06-28 | 既存optionsは削除せず互換用スナップショットとして残す。 | RuntimeのenumRef解決は導入済みだが、既存ViewDefや静的確認、enum読み込み失敗時の互換性を守るため。 |
| dec_0068_003 | 2026-06-28 | risk / severity / confidence / priority は同じ high/medium/low でも統合しない。 | リスク・重要度・確信度・優先度は判断軸が異なり、同一Enumにすると意味の混線が起きるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0068_001 | 2026-06-27 | incident_added | 既存common_types内optionsをEnum参照へ整理する作業項目が存在しなかった。 | studio_work_0068 として既存 common_types options のEnum参照化整理を登録。 | 値候補の重複・表記揺れ・意味ズレを減らし、Enum正本運用へ移行するため。 |
| chg_0068_001 | 2026-06-28 | common_enums_expansion | common_enumsには一部のqa/relation Enumのみが登録されていた。 | qa.feature_area/test_axis/quality_axis/check_axis/scenario_type/finding_type、relation.coverage/node_type/relation_typeなどを追加。 | common_types内のselect options直書きを値語彙正本へ寄せるため。 |
| chg_0068_002 | 2026-06-28 | common_types_enumref_added | 複数のselect FieldTypeがoptions直書きのみだった。 | 対象FieldTypeにenumRefを追加し、optionsは互換用スナップショットとして残置。 | FieldTypeは使い方、Enumは値語彙正本という責務分離を進めるため。 |
| chg_0068_003 | 2026-06-28 | report_added | v0.15.4の棚卸し結果レポートがなかった。 | COMMON_TYPES_OPTIONS_TO_ENUMREF_REPORT_v0_15_4.md を追加。 | 移行対象、保留方針、意味別Enum分離判断を後続AI/人間が追えるようにするため。 |

### v0.15.5-viewdef-context-read-contract: ViewDef文脈制御 read_contract 初期実装 / 主文脈・対象文脈モデル見直しへ移行
- 作業ID: studio_work_0069
- 種別: architecture
- 優先度: high
- 状態: 完了（後続あり）
- 確認状態: 見直し反映済み
- 対象ファイル: ViewDef schema/rules, data/json/00_rules/common_enums_v0_1.json, data/json/00_rules/common_types_v0_1.json, relevant ViewDefs, runtime context resolver if needed

#### 目的

ViewDefにAI作業前に読むべき追加文脈を定義できるようにする初期入口を作った上で、画面全体の主文脈と個別明細の対象文脈を分ける正式モデルへ移行する。

#### 背景

v0.15.5初期実装では context.read_contract と context_refs の入口を作ったが、画面体験としてはcontext_refsサンプルが主役に見え、ViewDef全体にかかる文脈契約がヘッダー/概要に見えない違和感が出た。会話により、全体は『主文脈』、個別明細は『対象文脈』として整理し直す方針になった。

#### 対象範囲

この作業項目は初期実装と違和感検出までを記録する。正式なモデル整理は v0.15.5.1-context-model-cleanup、主文脈のヘッダー表示は v0.15.5.2-main-context-header-panel、対象文脈のDetail上部表示は v0.15.5.3-target-context-detail-panel に分離する。

#### 対象外

この作業項目では、主文脈/対象文脈の最終UI実装を完了扱いにしない。既存の context.read_contract は互換入口として扱い、正式な context.main_context.refs[] への整理は後続で行う。

#### 固定名方針

Runtimeが特定Dataフィールド名を決め打ちしない方針を維持する。Enum / FieldType / ViewDef / Data の責務を分け、値の正本はEnum、画面項目としての使い方はFieldType、配置はViewDef、実値はDataとして扱う。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式と既存common_types運用を前提に、まずData/定義/解決ルールを段階的に追加する。

#### リスク

context_refsを通常Gridデータとして見せると、ViewDef全体にかかる文脈契約と個別明細にかかる対象文脈が混同される。JS実装へ先に進むと、動作はしても思想と画面体験がズレるリスクが高い。

#### 確認観点

v0.15.5を完了品として固定せず、後続インシデントへ分割されていること。主文脈はViewDef側、対象文脈はData明細側という整理がdecision_logとchange_historyに残っていること。

#### 作業会話サマリ


##### 依頼 / 方針

ViewDefに文脈制御プロパティを持たせたい。ViewDef全体にかかるものとData行単位に指定するものを分け、追加文脈を読ませるタイミングを制御したい。ViewDef全体にかかる文脈と、data行単位にかかる文脈を分けて考える必要がある。追加文脈は何を読むかだけでなく、いつ読むかが重要。

##### AI整理

ViewDef文脈制御はEnum追加とは別インシデントにする。read_contract / row context_refs / timing / failure_policy を扱うAI協働オーケストレーター化の入口として登録する。

##### 追加コメント

v0.15.5はこのままJS実装へ進む前に、主文脈/対象文脈の概念とインシデント構造を先に綺麗に整理したい。必要なら現行インシデントを没にして新規複数インシデントを起こしてよい。

## 返却ファイル

* [更新後Incident JSON](sandbox:/mnt/data/studio_work_incident_data_v0_74_context_model_cleanup_incidents_added.json)

## 今回の整理

`studio_work_0069 / v0.15.5-viewdef-context-read-contract` は、完了品として固定せず、

```text
完了（後続あり）
```

に変更しました。

理由は、初期実装としては意味があるけど、
**主文脈 / 対象文脈の画面体験がまだズレている**ためです。

## 新規追加したインシデント

```text
studio_work_0075
v0.15.5.1-context-model-cleanup
主文脈 / 対象文脈モデル整理
```

```text
studio_work_0076
v0.15.5.2-main-context-header-panel
主文脈ヘッダー表示 / 展開編集パネル
```

```text
studio_work_0077
v0.15.5.3-target-context-detail-panel
対象文脈Detail上部表示 / context_refs編集
```

## 反映した思想

* 全体文脈 = **主文脈**
* 個別明細文脈 = **対象文脈**
* 主文脈は ViewDef 側

  * `context.main_context.refs[]`
* 対象文脈は Data明細側

  * `context_refs[]`
* `context_refs[]` は明細オブジェクト内の先頭寄りに配置

  * `work_item_id / phase / title` の直後
* 旧 `context.read_contract` は互換扱い
* JS実装はまだ触らず、まずインシデント・Rules・Schema・サンプル整理を先にする

## 確認結果

* JSON parse：OK
* `items_count`: 74 → 77
* `work_item_id` 重複なし
* `0069 / 0075 / 0076 / 0077` に `context_refs` を先頭寄りで追加済み

##### AI追加回答

# AI回答

## 結論

v0.15.5 は初期入口としては有効だが、画面体験としては未完成扱いにする。  
`context_refs` のサンプルが通常Gridデータとして前面に出てしまい、ViewDef全体にかかる文脈契約が「画面の入口」として見えていなかった。

## 方針変更

- 全体文脈は **主文脈**
- 個別明細の文脈は **対象文脈**
- 主文脈は ViewDef JSON 側で管理する
- 対象文脈は Data JSON の明細オブジェクト側で管理する
- `context.read_contract` は旧互換として扱い、正式モデルは `context.main_context.refs[]` へ寄せる
- `context_refs[]` は対象文脈として、明細本文より前に置く

## 後続インシデント

- `v0.15.5.1-context-model-cleanup`
- `v0.15.5.2-main-context-header-panel`
- `v0.15.5.3-target-context-detail-panel`

## 確認結果

- v0.15.5を完了品として固定しない方針に変更
- 主文脈/対象文脈の用語を確定
- JS実装前にインシデント・Rules・Schema・サンプルを整える進め方に変更


#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0069_001 | 2026-06-27 | user | Enum / FieldType / Context制御の設計相談 | common_types_v0_1.json の現状を確認し、FieldTypeとしてできていること、Enumとして未分離なことを整理した。context_read_timing などはEnumが管理の最小単位になると判断した。 |
| disc_0069_002 | 2026-06-27 | assistant | 作業分割提案 | Enum定義追加、FieldType enumRef解決、context系Enum追加、既存optionsのEnum参照化、ViewDef文脈制御 read_contract対応の5件に分けてインシデント登録する方針を提案した。 |
| disc_0069_003 | 2026-06-27 | user | インシデント追加依頼 | Enumの仕掛けを作った後に、既存のOptionでだらだら書いているものを整理したい。インシデント追加と更新後JSON返却を依頼。 |
| disc_0069_v0155_001_user_request | 2026-06-28 | user | v0.15.5-viewdef-context-read-contract 作業依頼 | ViewDefに文脈制御プロパティを持たせ、ViewDef全体にかかる文脈とData行単位の文脈を分け、追加文脈を読むタイミングを制御したい。 |
| disc_0069_v0155_002_assistant_completion_report | 2026-06-28 | assistant | v0.15.5-viewdef-context-read-contract 作業結果 | # AI回答<br><br>## 今回の更新<br><br>- `wwwroot/js/core/viewdef_context_contract.js`<br>- `wwwroot/js/core/state.js`<br>- `wwwroot/js/runtime/load_runtime.js`<br>- `wwwroot/index.html`<br>- `data/json/00_rules/frb_view_def_schema_v0_9.json`<br>- `data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json`<br>- `data/json/00_rules/common_enums_v0_1.json`<br>- `defs/common/common_types_v0_1.json`<br>- `data/json/00_rules/context_refs_sample_data_v0_1.json`<br>- `defs/rules/context_refs_sample_view_def_v0_1.json`<br>- `data/json/00_rules/VIEWDEF_CONTEXT_READ_CONTRACT_REPORT_v0_15_5.md`<br>- `data/json/01_main/studio_work_incident_data_v0_74_proposal_driven_jobflow_added.json`<br><br>## やったこと<br><br>ViewDef全体にかかる文脈契約として `context.read_contract` を追加し、Data行単位の文脈参照 `context_refs` と分離して扱えるようにした。<br><br>- ViewDef schema に `context` / `read_contract` / `contextRef` / `rowContextContract` を追加<br>- ViewDef生成ルールに `viewdef_rule_27` を追加<br>- `context.failure_policy` / `context.trust_category` をEnum正本へ追加<br>- `context.failure_policy` / `context.trust_category` FieldTypeを追加<br>- `context_refs_sample_view_def_v0_1.json` に read_contract サンプルを追加<br>- Runtimeに `viewdef_context_contract.js` を追加し、ViewDef読込時に契約を正規化して `currentViewDefReadContract` へ保持<br><br>## 方針<br><br>v0.15.5では、外部ファイル自動読込やLLM投入までは行わない。  <br>今回は「ViewDefが、AIに読ませる文脈を宣言できる」契約と、Runtimeがその契約を認識できる入口までに限定した。<br><br>必須文脈が読めない場合は、`failure_policy=stop_and_report` を基本方針とする。  <br>ただし実際の停止・報告ワークフロー実装は後続フェーズで扱う。<br><br>## 確認結果<br><br>- JSON parse：OK<br>- `wwwroot` 配下 JS `node --check`：OK<br>- `context.read_timing`：OK<br>- `context.failure_policy`：OK<br>- `context.trust_category`：OK<br>- `context.failure_policy -> enumRef=context.failure_policy`：OK<br>- `context.trust_category -> enumRef=context.trust_category`：OK<br>- `context_refs_sample_view_def_v0_1.json` の `context.read_contract`：OK<br>- runtime生成物除外：OK<br> |
| disc_0069_v0155_003_assistant_completion_report_display_fix | 2026-06-28 | assistant | v0.15.5 AI完了報告表示補修 | # AI回答<br><br>## 今回の更新<br><br>- `wwwroot/js/core/viewdef_context_contract.js`<br>- `wwwroot/js/core/state.js`<br>- `wwwroot/js/runtime/load_runtime.js`<br>- `wwwroot/index.html`<br>- `data/json/00_rules/frb_view_def_schema_v0_9.json`<br>- `data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json`<br>- `data/json/00_rules/common_enums_v0_1.json`<br>- `defs/common/common_types_v0_1.json`<br>- `data/json/00_rules/context_refs_sample_data_v0_1.json`<br>- `defs/rules/context_refs_sample_view_def_v0_1.json`<br>- `data/json/00_rules/VIEWDEF_CONTEXT_READ_CONTRACT_REPORT_v0_15_5.md`<br>- `data/json/01_main/studio_work_incident_data_v0_74_proposal_driven_jobflow_added.json`<br><br>## やったこと<br><br>ViewDef全体にかかる文脈契約として `context.read_contract` を追加し、Data行単位の文脈参照 `context_refs` と分離して扱えるようにした。<br><br>- ViewDef schema に `context` / `read_contract` / `contextRef` / `rowContextContract` を追加<br>- ViewDef生成ルールに `viewdef_rule_27` を追加<br>- `context.failure_policy` / `context.trust_category` をEnum正本へ追加<br>- `context.failure_policy` / `context.trust_category` FieldTypeを追加<br>- `context_refs_sample_view_def_v0_1.json` に read_contract サンプルを追加<br>- Runtimeに `viewdef_context_contract.js` を追加し、ViewDef読込時に契約を正規化して `currentViewDefReadContract` へ保持<br><br>## 方針<br><br>v0.15.5では、外部ファイル自動読込やLLM投入までは行わない。  <br>今回は「ViewDefが、AIに読ませる文脈を宣言できる」契約と、Runtimeがその契約を認識できる入口までに限定した。<br><br>必須文脈が読めない場合は、`failure_policy=stop_and_report` を基本方針とする。  <br>ただし実際の停止・報告ワークフロー実装は後続フェーズで扱う。<br><br>## 確認結果<br><br>- JSON parse：OK<br>- `wwwroot` 配下 JS `node --check`：OK<br>- `context.read_timing`：OK<br>- `context.failure_policy`：OK<br>- `context.trust_category`：OK<br>- `context.failure_policy -> enumRef=context.failure_policy`：OK<br>- `context.trust_category -> enumRef=context.trust_category`：OK<br>- `context_refs_sample_view_def_v0_1.json` の `context.read_contract`：OK<br>- runtime生成物除外：OK<br><br><br>---<br><br>補足: 画面の「AI追加回答」で読み返せるよう、同じ完了報告Markdownを `latest_ai_response` にも反映した。 |
| disc_0069_v0155_review_001_user | 2026-06-28 | user | 主文脈 / 対象文脈の設計見直し | context_refsにはメインと行単位の話があり、全体は画面ヘッダーに表示する主文脈、個別明細は対象文脈として扱うイメージ。JSへ進む前にインシデント側を綺麗にしたい。 |
| disc_0069_v0155_review_002_assistant | 2026-06-28 | assistant | v0.15.5系分割方針 | v0.15.5は初期入口として残し、主文脈/対象文脈モデル整理、主文脈ヘッダー表示、対象文脈Detail表示の3段階へ分割する方針に整理。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0069_001 | 2026-06-27 | ViewDef全体の文脈とData行単位の文脈を分離する。 | 全体ルールと特定行だけに必要な追加文脈を混ぜると、AIへ渡す情報が過剰になり文脈が濁るため。 |
| dec_0069_002 | 2026-06-27 | timing は context.read_timing Enumを使う。 | before_review / before_code_update などの制御語彙を共通化し、表記揺れを防ぐため。 |
| dec_0069_003 | 2026-06-27 | requiredな文脈が読めない場合は stop_and_report を基本方針にする。 | ルール未読のまま雰囲気で作業する事故を防ぐため。 |
| dec_0069_v0155_004 | 2026-06-28 | ViewDef全体文脈は context.read_contract、Data行単位文脈は context_refs として分離する。 | 全体ルールと行固有文脈を混ぜると、AIに渡す情報が過剰になり、必要な文脈の粒度が濁るため。 |
| dec_0069_v0155_005 | 2026-06-28 | v0.15.5では自動読込実行ではなく、ViewDef契約定義とRuntime認識入口までに限定する。 | 外部LLM投入や作業停止制御まで同時に実装すると責務が膨らむため、まず契約をData/ViewDef/Rules/Runtimeで共有できる状態にする。 |
| dec_0069_v0155_review_006 | 2026-06-28 | 全体文脈の表示名を『主文脈』、個別明細側の文脈表示名を『対象文脈』とする。 | 行文脈ではインシデント番号単位・テストパターン単位・ルール単位などに広がる概念を表しきれないため。 |
| dec_0069_v0155_review_007 | 2026-06-28 | 主文脈は ViewDef 側の context.main_context.refs[]、対象文脈は Data明細側の context_refs[] として整理する。 | ViewDef全体にかかる前提文脈と、個別対象を扱う時だけ必要な追加文脈を混同しないため。 |
| dec_0069_v0155_review_008 | 2026-06-28 | 対象文脈 context_refs[] は明細オブジェクト内の先頭寄り、id/phase/title の直後に置くことを推奨する。 | 対象文脈は本文に混ざる補足ではなく、その明細を扱う前に読む入口だから。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0069_001 | 2026-06-27 | incident_added | ViewDefがAI作業前に読むべき文脈を制御する作業項目が存在しなかった。 | studio_work_0069 として ViewDef文脈制御 read_contract / row context_refs 対応を登録。 | Studioくんを画面定義ツールからAI作業の文脈ルーティング定義へ進化させるため。 |
| chg_0069_v0155_001 | 2026-06-28 | viewdef_context_contract_schema_rules | ViewDef schema/rulesには、AI作業前に読むべき文脈を宣言する read_contract 契約がなかった。 | frb_view_def_schema_v0_9.json に context/read_contract 関連定義を追加し、frb_viewdef_generation_rules_data_v0_1.json に viewdef_rule_27 を追加。 | AIへ渡す文脈をViewDefで宣言し、画面定義と同じJSON文化で管理するため。 |
| chg_0069_v0155_002 | 2026-06-28 | context_enum_fieldtypes_added | context.read_timing は存在したが、failure_policy / trust は文字列として扱われていた。 | context.failure_policy / context.trust_category Enum と FieldType を追加。 | 失敗時方針と信頼区分の表記揺れを避け、select候補として表示できるようにするため。 |
| chg_0069_v0155_003 | 2026-06-28 | runtime_contract_recognition | RuntimeはViewDef上のread_contractを特に認識していなかった。 | viewdef_context_contract.js を追加し、ViewDef読込時にread_contractを正規化して currentViewDefReadContract に保持する。 | v0.15.5では自動読込はしないが、Runtimeが契約を認識できる入口を用意するため。 |
| chg_0069_v0155_004_completion_report_display_fix | 2026-06-28 | incident_report_visibility_fix | AI完了報告Markdownは discussion_history には存在したが、画面上の「AI追加回答」に表示される latest_ai_response は短い要約のままだった。 | latest_ai_response にも # AI回答 / 今回の更新 / やったこと / 方針 / 確認結果 のMarkdown完了報告を反映し、Studio画面の会話カードで読み返せるようにした。 | ユーザーが作業詳細報告をStudio画面上の会話履歴として読み返せるようにするため。 |
| chg_0069_v0155_review_005 | 2026-06-28 | incident_reclassification | v0.15.5 を ViewDef context.read_contract / row context_refs 対応の完了項目として扱っていた。 | v0.15.5 は初期入口と違和感検出の記録に変更し、正式モデル整理とUI実装は v0.15.5.1〜v0.15.5.3 へ分割。 | context_refsサンプルが主役に見える表示では、主文脈と対象文脈の思想が画面体験に反映されないため。 |

### v0.15.6-grid-column-resize-viewdef-save: グリッド列幅変更 / ViewDef明示保存
- 作業ID: studio_work_0070
- 種別: feature
- 分類: grid_viewdef
- 優先度: medium
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: wwwroot/js/renderers/grid_renderer.js, wwwroot/js/renderers/grid_detail.js, wwwroot/js/runtime/load_runtime.js, wwwroot/js/core/viewdef_resolver.js, wwwroot/js/core/file_api.js, wwwroot/styles.css, related ViewDef schema/rules if needed

#### 目的

グリッド表示中に列幅をドラッグ変更できるようにし、必要な場合のみ明示操作で現在のViewDefの fields[].grid.width へ反映できるようにする。

#### 背景

実データをStudioくんで確認していると、列幅をその場で調整したくなる。列幅は人間が『この項目をちゃんと見たい』と判断した痕跡でもあり、ViewDefを人間が育てる体験に直結する。一方で、列幅変更を常時ViewDefへ自動保存すると、ちょっと触っただけでViewDefが汚れ、Git差分が width 変更だらけになるリスクがある。

#### 対象範囲

グリッド列幅のドラッグ変更を可能にする。変更直後はRuntime上の一時変更として扱い、ViewDefへは自動保存しない。ユーザーが明示的に『列幅をViewDefへ保存』を実行した場合のみ、現在読込中のViewDef source の fields[].grid.width へ反映する。必要に応じて未保存列幅変更ありの表示、minWidth/maxWidth、readOnly時の無効化、保存成功/失敗トーストを追加する。

#### 対象外

列幅変更の常時自動ViewDef保存は行わない。localStorageによる個人列幅保存、列順変更、列表示/非表示の保存、複数ユーザー向けの個人プロファイル管理、共通FieldType/common_types側の幅更新はこの作業では必須にしない。

#### 固定名方針

Runtimeは特定Dataフィールド名に依存しない。列幅保存対象はViewDefの fields[] 内で宣言された field と grid.width に限定する。common_types や resolved ViewDef 由来の幅を直接正本として更新せず、必要な場合は現在のViewDef source へ grid.width の明示overrideとして保存する。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、グリッド描画・列幅ドラッグ・ViewDef保存処理へ安全に追加する。

#### リスク

列幅変更を自動保存すると、閲覧中の偶発操作でViewDefが汚れる。個人の見やすさが共有ViewDefへ混入する。Git差分が width 数値変更だらけになり、本来の機能差分が見えにくくなる。resolved ViewDefやcommon_types由来の設定を誤って正本更新すると、共通型全体へ予期せぬ影響が出る。

#### 確認観点

グリッド列ヘッダー境界をドラッグして列幅が変わること。列幅変更だけではViewDefファイルが保存されないこと。明示保存実行時のみ対象ViewDefの fields[].grid.width が更新されること。保存後に再読込して列幅が維持されること。readOnly/静的ホスティング時にはViewDef保存操作が無効または非表示になること。hidden列・サブグリッド・横スクロール・既存ソート/選択操作が壊れないこと。

#### 作業会話サマリ


##### 依頼 / 方針

データをグリッドで表示している状態で、グリッドの列の幅を変えたくて、しかも、その変えた幅をViewDefに保存する機能がほしい。列幅変更を常に許可していると面倒な話になるのか、まず会話したい。

##### AI整理

列幅変更は実用上かなり重要。ただし、ドラッグした瞬間にViewDefへ自動保存すると、偶発操作でViewDefが汚れ、Git差分が列幅変更だらけになる。まずはRuntime上の一時変更として扱い、ユーザーが明示的に『列幅をViewDefへ保存』した場合のみ fields[].grid.width へ反映する方針が安全。

##### 追加コメント

うぃーーー。ではインシデント追加して更新後JSON返却お願いします。

##### AI追加回答

studio_work_0070 として、グリッド列幅変更 / ViewDef明示保存インシデントを追加。列幅変更はまずRuntime一時変更とし、ViewDef保存は明示操作必須、常時自動保存は禁止方針として登録した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0070_001 | 2026-06-27 | user | グリッド列幅変更相談 | データをグリッドで表示している状態で、グリッドの列の幅を変えたくて、しかも、その変えた幅をViewDefに保存する機能がほしい。列幅変更を常に許可していると面倒な話になるのか、まず会話したい。 |
| disc_0070_002 | 2026-06-27 | assistant | 列幅保存方針整理 | 列幅変更は『画面上の一時的な見やすさ調整』であり、ViewDef保存は『画面定義そのものの変更』。ドラッグ直後にViewDefへ自動保存せず、Runtime一時変更、必要なら個人設定保存、明示操作でViewDef反映、という段階分けが安全と整理した。 |
| disc_0070_003 | 2026-06-27 | user | インシデント追加依頼 | インシデント追加して更新後JSON返却を依頼。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0070_001 | 2026-06-27 | 列幅ドラッグ変更はまずRuntime上の一時変更として扱う。 | 単に見やすくするための操作を、即座にViewDef設計変更として扱うと、偶発操作で定義が汚れるため。 |
| dec_0070_002 | 2026-06-27 | ViewDefへの列幅保存は明示操作必須とする。 | ViewDefは共有される画面定義であり、個人の一時的な列幅調整を自動で正本化しないため。 |
| dec_0070_003 | 2026-06-27 | 保存先は fields[].grid.width を基本とする。 | 既存ViewDefの列幅定義と自然に接続でき、列幅変更をViewDefの明示的な設計差分として管理できるため。 |
| dec_0070_004 | 2026-06-27 | localStorageによる個人列幅保存は将来検討とする。 | 個人の見やすさと共有ViewDefの設計変更を分離する選択肢として有効だが、初回実装に含めるとスコープが膨らむため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0070_001 | 2026-06-27 | incident_added | studio_work_incident_data_v0_69_enum_context_incidents_added.json / items_count=69 | studio_work_incident_data_v0_70_grid_column_resize_viewdef_save_added.json / items_count=70 | グリッド列幅変更とViewDefへの明示保存機能を、将来実装前に作業項目として忘れず管理するため。 |

### v0.15.7-objectarray-section-search: objectArray / 履歴セクションのまとまり検索対応
- 作業ID: studio_work_0071
- 種別: feature
- 優先度: high
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: wwwroot/js/runtime/search_runtime.js, wwwroot/js/renderers/grid_renderer.js, wwwroot/js/renderers/grid_detail.js, wwwroot/js/core/viewdef_resolver.js, wwwroot/app.js, wwwroot/styles.css, relevant ViewDefs such as studio_work_incident_view_def_*.json, frb_view_def_schema_*.json / rules if needed

#### 目的

discussion_history / change_history / decision_log などの objectArray 形式の深い階層を、項目単位ではなく『会話履歴』『変更履歴』『判断ログ』『履歴全体』のようなセクション単位で検索できるようにする。

#### 背景

ルール改定後に最新JSONを開いても、変更があった箇所や過去会話をStudio画面上から探しにくく、JSON生データを直接検索する運用になっていた。ルールJSONの名前固定化やGitDiffRunによりファイル名指定の差分比較土台はできたが、『どのインシデントの会話・判断・変更履歴にその話があったか』を掘り当てる導線が不足している。Studioくんのインシデント管理JSONが育つほど、深い階層の履歴検索が必要になる。

#### 対象範囲

ViewDefの objectArray / childArea / detailBody などのまとまり単位に search.visible を持たせ、そのセクション全体を検索対象にできるようにする。discussion_history は会話履歴、change_history は変更履歴、decision_log は判断ログとして検索対象化する。search.group="history" のようなグループ指定により、会話履歴・変更履歴・判断ログを束ねた『履歴全体』串刺し検索もできるようにする。必要に応じて、従来のJSON生データ検索に相当する『JSON全体』検索もRuntime上の一時文字列化で提供する。

#### 対象外

初期対応では、全JSON階層の完全全文検索、全文字列フィールドの自動検索、ヒット箇所のカード単位ハイライト、検索結果からGitDiffRunを直接起動する連携、厳密な検索インデックス永続化、外部全文検索エンジン導入は行わない。まずは履歴セクション単位の集約検索と、必要最低限のJSON全体検索に限定する。

#### 固定名方針

Runtimeが discussion_history / change_history / decision_log という特定Data名を無条件に固定検索するのではなく、ViewDef上で search.visible=true とされたセクションを検索対象とする。インシデント管理ViewDefでは結果として discussion_history / change_history / decision_log を対象化する。検索用テキストはData JSONへ保存せず、Runtime上の一時インデックスとして扱う。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、検索処理・ViewDef解釈・検索UIへ段階的に追加する。

#### リスク

検索スコープをViewDefとは別に手書き定義すると、表示定義と検索定義がズレて同じような定義が増える。逆に最初から全フィールド自動検索にすると、id・日付・status等のノイズが多くなり、検索結果が読みにくくなる。深い階層の値を検索用にData JSONへ保存するとJSONが太り、原本が検索キャッシュで汚れる。

#### 確認観点

会話履歴検索で discussion_history[].topic / message / speaker 等が検索対象になること。変更履歴検索で change_history[].change_type / before / after / reason / updated_files 等が検索対象になること。判断ログ検索で decision_log[].decision / reason が検索対象になること。履歴全体検索で上記3セクションが串刺し検索されること。検索ヒット時は親のwork_item行が絞り込まれること。検索用テキストがData JSONへ保存されないこと。既存の浅い項目検索やGrid表示に回帰がないこと。

#### 作業会話サマリ


##### 依頼 / 方針

会話履歴や変更履歴や判断ログのようなJSONの一つ深い階層の明細についても検索できるようにしたい。項目を指定した検索ではなく、会話履歴全体、変更履歴全体、判断ログ全体のような検索がよい。最初は会話履歴・変更履歴・判断ログごとに検索できればよく、将来的には文字列フィールドなら何でも検索、さらに会話履歴・変更履歴・判断ログの串刺し検索やJSON全体検索も欲しい。

##### AI整理

検索スコープを別定義で大量に持つより、ViewDef上のobjectArrayやchildAreaなどの表示セクションに search.visible を持たせ、その表示定義から検索対象を自動生成する方針が自然。最初は会話履歴・変更履歴・判断ログのセクション単位検索、次にsearch.groupによる履歴全体の串刺し検索、必要に応じてJSON全体検索を用意する。検索用文字列はData JSONへ保存せずRuntime上で一時生成する。

##### AI追加回答

studio_work_0071 として、objectArray / 履歴セクションのまとまり検索対応インシデントを追加。ViewDefの表示セクションに search.visible を持たせ、会話履歴・変更履歴・判断ログ・履歴全体・JSON全体検索を段階的に実現する方針として登録した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0071_001 | 2026-06-27 | user | 深い階層検索の相談 | ルール改定後に最新JSONを読んでも、変更があったところをどう検索するのか分からない。会話履歴や変更履歴や判断ログのような、JSONの一つ深い階層の明細についても検索できるようにしたい。 |
| disc_0071_002 | 2026-06-27 | assistant | 検索スコープ初期案 | 当初はViewDef全体に search.scopes を持たせる案を提示したが、表示定義と検索定義が二重になり、同じような定義が増えるリスクがある。 |
| disc_0071_003 | 2026-06-27 | user | セクションsearch案 | searchScopesのような別定義ではなく、レビュー会話などのセクション自体に search.visible を持たせればよいのではないかと指摘。 |
| disc_0071_004 | 2026-06-27 | assistant | セクション検索方針 | objectArray / childArea / detailBody などのまとまり単位に search.visible を持たせ、表示セクションから検索対象を自動生成する方針へ整理。子fields[]は親セクションの検索対象として集約し、除外したい子項目だけ search.visible=false とする。 |
| disc_0071_005 | 2026-06-27 | user | 段階的検索の夢 | 最初は会話履歴・変更履歴・判断ログごとの検索でよい。将来的には文字列フィールドなら何でも検索できるようにしたい。その前に会話履歴・変更履歴・判断ログの串刺し検索もあるとよい。 |
| disc_0071_006 | 2026-06-27 | assistant | 段階的実装方針 | Step1は会話履歴・変更履歴・判断ログの個別検索、Step2はsearch.group=historyによる履歴全体検索、Step3はsearch.visible=trueのまとまり全部、Step4は文字列系フィールド自動検索という進化順で整理。 |
| disc_0071_007 | 2026-06-27 | user | JSON生データ検索からの昇格 | 今は検索機能がないためJSON生データで検索している。ルールJSONの名前固定化でGitDiffは見やすくなり、GitDiffRunでファイル名指定比較の土台もできたが、Studio画面上で履歴を探したい。 |
| disc_0071_008 | 2026-06-27 | assistant | 記憶から差分への導線 | 今回の検索機能はJSON生データ検索をStudio画面操作へ昇格させるもの。将来的には検索で会話履歴を探し、判断を読み、変更履歴を確認し、対象ファイルのGitDiffRunへ降りる導線につながる。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0071_001 | 2026-06-27 | 検索対象は別途 searchScopes を大量に手書きせず、ViewDef上の表示セクションに search.visible を持たせる。 | 表示定義と検索定義を二重に持つとズレや重複が発生するため。表示のまとまりを検索のまとまりとしても使う方がStudioくんのViewDef思想に合う。 |
| dec_0071_002 | 2026-06-27 | 初期対応は会話履歴・変更履歴・判断ログのセクション単位検索に限定する。 | 最初から全JSON階層の全文検索にするとノイズが増えやすいが、現状のJSON生データ検索よりはセクション単位検索だけでも大幅に使いやすくなるため。 |
| dec_0071_003 | 2026-06-27 | search.group により、会話履歴・変更履歴・判断ログを束ねた履歴全体検索を扱う。 | 個別セクション検索だけでなく、過去会話・判断・変更のどこかに書いた情報を一括で掘り当てたい場面が多いため。 |
| dec_0071_004 | 2026-06-27 | 検索用テキストはData JSONへ保存しない。 | 検索キャッシュを原本Dataへ混ぜるとJSONが太り、Git差分や原本性が汚れるため。検索用の集約文字列はRuntime上で一時生成する。 |
| dec_0071_005 | 2026-06-27 | 将来的にJSON全体検索と文字列系フィールド自動検索を検討する。 | 現状はJSON生データ検索で探しているため、最低限の『全部探す』逃げ道も有用。段階的にStudio画面上の検索体験へ置き換えるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0071_001 | 2026-06-27 | incident_added | studio_work_incident_data_v0_70_grid_column_resize_viewdef_save_added.json / items_count=70 | studio_work_incident_data_v0_71_objectarray_section_search_added.json / items_count=71 | 会話履歴・変更履歴・判断ログなどの深い階層をStudio画面上で検索できるようにし、JSON生データ検索に頼っていた履歴探索をStudioくんの機能として扱うため。 |

### v0.15.8-gitdiff-result-viewer-launch: GitDiffRun結果JSONのDiffJsonViewer自動表示
- 作業ID: studio_work_0072
- 種別: feature
- 分類: gitdiff_viewer
- 優先度: high
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: Program.cs, wwwroot/js/actions/action_registry.js, wwwroot/js/actions/action_toolbar.js, wwwroot/js/core/file_api.js, wwwroot/DiffJsonViewer.html, wwwroot/js/renderers/diff_json_viewer*.js, wwwroot/styles.css, related GitDiffRun action/runtime files

#### 目的

StudioくんからGitDiffRunを起動した後、生成された差分JSONをwwwroot配下の一時公開フォルダーへ出力し、DiffJsonViewer.html?src=... で自動表示できるようにする。

#### 背景

StudioくんからGitDiffRunを起動できる土台ができたことで、『差分を作る』だけでなく『差分をその場で見る』まで一気通貫したい。当初はF:\FRB_Diffなど管理外フォルダーの差分JSONをProgram.cs側で読み込んでAPIレスポンスにdiff_json本文を含める案だったが、差分JSONをwwwroot配下の生成用フォルダーへ出力し、そのフォルダーを.gitignoreでGit管理対象外にすれば、DiffJsonViewer.htmlが通常の静的ファイルとして読み込める。この場合、APIレスポンスの主役はJSON本文ではなく、viewer_url / diff_json_path / file_size_bytes / summary などの案内情報になる。

#### 対象範囲

GitDiffRun実行時の差分JSON出力先を、例: wwwroot/diff_runs/DiffToJson_*.json のようなViewerから参照可能な生成用フォルダーへ寄せる。この生成用フォルダーまたはDiffToJson_*.jsonだけを.gitignoreで除外し、リポジトリに一時成果物が混入しないようにする。GitDiffRun実行APIは、差分JSON本文ではなく ok / exit_code / viewer_url / diff_json_path / file_size_bytes / summary / warnings を返す。Studioくんはviewer_urlを受け取り、DiffJsonViewer.html?src=./diff_runs/DiffToJson_*.json のようなURLで自動表示する。DiffJsonViewer.htmlはsrcパラメータを同一アプリ配下の許可パスとして検証し、fetchして表示する。

#### 対象外

差分JSON本文をAPIレスポンスに丸ごと含める方式は初期方針から外す。大量差分JSONのページング、ストリーミング、diff_id方式、部分読み込み、圧縮転送、差分検索インデックス化、AI差分物語の自動生成、Viewerの高度な差分分類UIは本インシデントでは扱わない。大量データの扱いは v0.15.9-gitdiff-large-result-handling として分離する。

#### 固定名方針

ブラウザ側が F:\FRB_Diff などのローカル絶対パスを直接読む設計にはしない。Runtimeが任意パスを指定して読み込める構造も避ける。GitDiffRunが生成した出力ファイル、かつProgram.cs側で許可された出力フォルダー配下の差分JSONだけを読み取り対象にする。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、GitDiffRun Action/APIレスポンスとDiffJsonViewer表示導線を段階的に追加する。

#### リスク

wwwroot配下に生成差分JSONを置くため、.gitignore設定を誤ると一時成果物がGit管理対象に混入するリスクがある。srcパラメータを無制限に許すと任意パス参照や意図しないファイル公開のリスクがある。古いDiffToJson_*.jsonが溜まり続けるとローカル容量が増えるため、将来的には掃除方針が必要になる。巨大JSONはDiffJsonViewer側の表示限界に達する可能性があるが、それはv0.15.9で安全にエラー扱いする。

#### 確認観点

GitDiffRun成功時に wwwroot/diff_runs/DiffToJson_*.json が生成されること。.gitignoreで対象フォルダー配下のDiffToJson_*.jsonだけがGit管理対象外になること。APIレスポンスにdiff_json本文ではなくviewer_url/diff_json_path/file_size_bytes/summaryが含まれること。DiffJsonViewer.html?src=./diff_runs/DiffToJson_*.json で差分JSONが表示されること。存在しないsrcや許可外srcでは分かりやすいエラーになること。既存のGitDiffRun起動のみの動作を壊さないこと。

#### 作業会話サマリ


##### 依頼 / 方針

StudioくんからGitDiffが起動できるようになったので、差分JSONの出力が終わったらDiffJsonViewer.htmlで表示するところまで将来候補としてやりたい。当初は差分JSONの中身をそのままレスポンスで受け取る感覚があったが、改めて考えると、差分データをwwwroot配下に入れ、.gitignoreでGit管理対象外にすれば、DiffJsonViewer.htmlがsrc指定で直接読めるため、APIレスポンスで巨大JSON本文を運ぶ必要は基本ない。

##### AI整理

方針を修正。GitDiffRun結果JSONは、APIレスポンス本文で運ぶのではなく、wwwroot配下の生成用フォルダーへ出力し、.gitignoreでGit管理対象外にする。APIはviewer_url / diff_json_path / file_size_bytes / summary等を返し、StudioくんはDiffJsonViewer.html?src=... を開く。差分JSON本文の運搬役をAPIに背負わせず、Viewerが静的ファイルとして読む構成にする。

##### 追加コメント

差分データをwwwrootの中に入れられるなら、APIレスポンスでJSON本文を返す話ではなく、DiffJsonViewer.htmlがsrcで読めばよい。大容量の場合も、単にDiffJsonViewer.htmlで扱えない容量としてエラーにすればよいのではないか、という方針修正。

##### AI追加回答

v0.15.8の方針を修正。差分JSONはwwwroot配下のgitignore対象フォルダーへ出力し、APIレスポンスではJSON本文ではなくviewer_url/path/size/summaryを返す。DiffJsonViewer.htmlはsrcパラメータで差分JSONを静的取得して表示する方針へ更新した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0072_001 | 2026-06-27 | user | GitDiffRun後のViewer表示相談 | StudioくんからGitDiffが起動できるようになったので、差分JSONの出力が終わったらDiffJsonViewer.htmlで表示するところまでいけるのではないか。差分JSONの中身をそのままレスポンスで受け取ってもよいのではないか。 |
| disc_0072_002 | 2026-06-27 | assistant | 実装方針整理 | 差分JSONが F:\FRB_Diff など管理外フォルダーに出る場合、ブラウザから直接読むのではなく、Program.cs側が許可された出力先から差分JSONを読み込み、APIレスポンスとして返すのが自然。Studioくんはdiff_jsonを受け取り、DiffJsonViewer.htmlまたは画面内Viewerへ渡して表示する。 |
| disc_0072_003 | 2026-06-27 | user | 体験価値 | これが一気通貫できたら他の人もびびる体験になる。GitDiffRun → 差分JSON → Viewer表示までつながると、KPI至上主義者にも刺さるのではないか。 |
| disc_0072_004 | 2026-06-27 | assistant | 体験価値整理 | GitDiffRun起動、差分JSON生成、DiffJsonViewer自動表示、差分分類・強調、AI差分物語、人間承認までの導線は、承認準備時間短縮・確認漏れ低減・AI作業結果の追跡性向上に直結する体験になる。 |
| disc_0072_005 | 2026-06-27 | user | インシデント追加依頼 | まずはインシデント追加。大量データの取り扱いは2件のインシデントに最初から分けておきたい。 |
| disc_0072_006 | 2026-06-27 | user | wwwroot配下出力への方針転換 | DiffToJson_*.jsonを全部Git管理対象外にするのではなく、差分データをwwwroot配下の生成フォルダーへ出力し、そのフォルダーだけ.gitignoreで除外すればよいと整理。 |
| disc_0072_007 | 2026-06-27 | assistant | APIレスポンス方針の修正 | APIレスポンスでdiff_json本文を返す方針から、viewer_url / diff_json_path / file_size_bytes / summary を返し、DiffJsonViewer.htmlがsrcで静的取得する方針へ修正。 |
| disc_0072_008 | 2026-06-27 | user | 大容量問題の再整理 | wwwroot配下に置けるならAPIレスポンス容量の問題ではなく、DiffJsonViewer.htmlで扱えるサイズかどうかの問題として整理できる。扱えないサイズならエラーでよい。 |
| disc_0072_009 | 2026-06-27 | assistant | 方針更新完了 | v0.15.8を、差分JSON本文レスポンス方式ではなく、wwwroot生成フォルダー + .gitignore + DiffJsonViewer src読込方式へ更新する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0072_001 | 2026-06-27 | 差分JSON本文は基本的にAPIレスポンスへ含めず、wwwroot配下の生成用フォルダーへ出力する。 | wwwroot配下であればDiffJsonViewer.htmlが通常の静的ファイルとして読み込めるため、APIレスポンスを巨大JSON運搬経路にする必要がない。 |
| dec_0072_002 | 2026-06-27 | 生成されたDiffToJson_*.jsonは、フォルダー指定の.gitignoreでGit管理対象外にする。 | DiffToJson_*.json全体を無視すると保存したい差分JSONまで対象外になるため、例: /tools/FRBStudio_App/wwwroot/diff_runs/DiffToJson_*.json のように生成用フォルダー配下だけ除外する。 |
| dec_0072_003 | 2026-06-27 | GitDiffRun実行APIはviewer_url / diff_json_path / file_size_bytes / summary / warningsを返す。 | APIの役割は差分JSON本文の運搬ではなく、Viewerへ渡す場所・サイズ・概要・警告を案内することに寄せる。 |
| dec_0072_004 | 2026-06-27 | DiffJsonViewer.htmlはsrcパラメータで同一アプリ配下の許可された差分JSONだけを読み込む。 | src指定による表示体験を実現しつつ、任意パス参照や意図しないファイル読込を避けるため。 |
| dec_0072_005 | 2026-06-27 | 大量差分JSONの扱いはv0.15.9に分離し、v0.15.8では通常サイズの一気通貫表示を優先する。 | GitDiffRunからViewer表示までの体験を先に作り、巨大JSONの表示限界・エラー表示・将来の分割表示は別スコープで扱う方が安全なため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0072_001 | 2026-06-27 | incident_added | items_count=71 / latest=studio_work_0071 | items_count=73 / added studio_work_0072 and studio_work_0073 | GitDiffRun結果JSONのDiffJsonViewer自動表示と、大量差分JSONの取り扱いを別インシデントとして管理するため。 |
| chg_0072_002 | 2026-06-27 | incident_policy_update | GitDiffRun実行後、Program.cs側で差分JSON本文を読み込み、APIレスポンスにdiff_jsonとして含めてViewerへ渡す方針。 | GitDiffRun実行後、差分JSONをwwwroot配下のgitignore対象生成フォルダーへ出力し、APIはviewer_url/path/size/summaryを返す。DiffJsonViewer.htmlはsrcで差分JSONを静的取得する。 | 差分JSONをwwwroot配下に置けばブラウザが通常の静的ファイルとして読めるため、APIレスポンスを巨大JSON本文の運搬経路にする必要がない。 |

### v0.15.9-gitdiff-large-result-handling: GitDiffRun巨大差分JSONのViewer表示上限 / エラー表示
- 作業ID: studio_work_0073
- 種別: feature
- 分類: gitdiff_large_data
- 優先度: medium
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: Program.cs, wwwroot/js/actions/action_registry.js, wwwroot/js/core/file_api.js, wwwroot/DiffJsonViewer.html, wwwroot/js/renderers/diff_json_viewer*.js, wwwroot/styles.css, related GitDiffRun API/runtime files

#### 目的

wwwroot配下に生成された差分JSONがDiffJsonViewer.htmlで扱えないほど大きい場合に、無理に表示せず、安全にサイズ上限エラーとして扱えるようにする。

#### 背景

v0.15.8の方針を、APIレスポンスでdiff_json本文を返す方式から、wwwroot配下の生成用フォルダーへ差分JSONを出力し、DiffJsonViewer.htmlがsrcで読む方式へ修正した。これによりGit管理の大容量問題は.gitignoreで解消し、APIレスポンス肥大化も基本的には回避できる。残る大容量問題は、DiffJsonViewer.htmlがその差分JSONをfetch/parse/renderできるかどうかである。初期段階では、Viewer表示限界を超えるファイルは安全にエラー表示すればよい。

#### 対象範囲

DiffJsonViewer.htmlまたはGitDiffRun実行API側で差分JSONのfile_size_bytesを確認し、設定した表示上限を超える場合はViewer表示を止める。上限超過時は、too_large=true / file_size_bytes / max_viewer_size_bytes / diff_json_path / summary / warnings などを表示し、『差分JSONが大きすぎるためViewerでは表示できない』ことを明示する。通常サイズの場合はv0.15.8のsrc読込方式でそのまま表示する。

#### 対象外

初期段階では、diff_id方式、部分読み込み、ページング、ストリーミング、WebSocket配信、巨大diffのsummary-first高度表示、外部DB化、全文検索エンジン化は行わない。まずはViewerで扱えない巨大JSONを安全に止める・分かりやすくエラー表示することに限定する。

#### 固定名方針

diff_idは内部一時IDであり、任意のローカルパスをブラウザに読ませるための抜け道にしない。output_pathを表示する場合も、読み取りAPIは許可フォルダー配下かつGitDiffRunが生成した差分JSONに限定する。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を前提に、API応答・Viewer表示・大容量時の分岐を段階的に追加する。

#### リスク

巨大JSONを無理にfetch/parse/renderするとブラウザが固まる。サイズ上限を厳しすぎる値にすると一気通貫体験が途切れやすくなる。逆にゆるすぎる値にするとメモリ使用量が増え、Viewerが操作不能になる。Git管理やAPIレスポンス容量の問題と、Viewer表示限界の問題を混同しないようにする必要がある。

#### 確認観点

設定した上限以下のDiffToJson_*.jsonはDiffJsonViewer.html?src=...で表示できること。上限を超えるファイルはfetch/parse/renderへ進まず、too_largeまたは明確なエラーメッセージを表示すること。エラー表示にfile_size_bytes / max_viewer_size_bytes / diff_json_path / summaryが表示されること。Git管理対象外設定により、巨大なDiffToJson_*.jsonがGit差分に出ないこと。APIレスポンスに巨大JSON本文を含めないこと。

#### 作業会話サマリ


##### 依頼 / 方針

大量データなら、その時はエラーで返してもよい。ただし、wwwroot配下の生成フォルダーに差分JSONを置き、.gitignoreで除外するなら、大容量問題はAPIレスポンスではなくDiffJsonViewer.htmlで扱える容量かどうかの問題になる。扱えない容量ならエラーでよい、という整理へ修正したい。

##### AI整理

v0.15.9の位置づけを修正。大量差分JSON対策は、APIレスポンスやdiff_id方式を前提にした段階化ではなく、まずDiffJsonViewer.htmlの表示上限・安全なエラー表示として扱う。Git管理の肥大化は.gitignoreで回避し、APIレスポンスには巨大JSON本文を含めない。残る問題はViewerで表示できるサイズかどうかであり、初期段階では上限超過時にエラーでよい。

##### 追加コメント

wwwroot配下に差分JSONを置けるなら、APIレスポンスで巨大JSONを返す話ではない。大容量の場合はDiffJsonViewer.htmlが扱えない容量としてエラーにすればよい、という整理にしたい。

##### AI追加回答

v0.15.9を、diff_id/部分読み込み中心の大容量対策から、DiffJsonViewerの表示上限・too_largeエラー表示中心のインシデントへ更新した。diff_idや部分読み込みは初期スコープ外の将来候補とし、まずは安全に止める方針へ整理した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0073_001 | 2026-06-27 | user | 大量データ時の扱い | 大量データなら、その時はエラーで返してもよい。エラーにしない方向にはがんばりたいが、ステップは分けてよい。 |
| disc_0073_002 | 2026-06-27 | assistant | インシデント分離方針 | GitDiffRun結果JSONのDiffJsonViewer自動表示はv0.15.8として一気通貫体験を優先し、大量差分JSONのレスポンス肥大化・描画停止・diff_id方式・部分読み込みはv0.15.9として分離するのが安全。 |
| disc_0073_003 | 2026-06-27 | user | インシデント追加依頼 | 大量データの取り扱いは2件のインシデントに最初から分けておこう。更新後JSON返却を依頼。 |
| disc_0073_004 | 2026-06-27 | user | Git管理対象外による大容量問題の再整理 | DiffToJson_*.jsonをwwwroot配下の生成フォルダーへ置き、そのフォルダーだけ.gitignoreで除外すれば、Git管理上の大容量問題は解消できると整理。 |
| disc_0073_005 | 2026-06-27 | user | Viewer表示限界への整理 | 大容量の場合は、APIレスポンスで返せない問題ではなく、DiffJsonViewer.htmlで扱えない容量であるという整理でよい。扱えないならエラーでよい。 |
| disc_0073_006 | 2026-06-27 | assistant | v0.15.9方針修正 | v0.15.9を、diff_id方式中心ではなく、DiffJsonViewerの表示上限・too_largeエラー表示中心に修正する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0073_001 | 2026-06-27 | 大量差分JSON問題は、まずDiffJsonViewer.htmlの表示限界問題として扱う。 | 差分JSONはwwwroot配下のgitignore対象フォルダーから静的取得するため、APIレスポンス肥大化ではなく、Viewerがfetch/parse/renderできるかが主問題になるため。 |
| dec_0073_002 | 2026-06-27 | Viewer表示上限を超えた場合は、初期段階ではエラーでよい。 | 巨大JSONを無理に表示してブラウザを固めるより、サイズ・パス・概要を示して安全に止める方が実用的であるため。 |
| dec_0073_003 | 2026-06-27 | diff_id方式・部分読み込み・ストリーミングは初期スコープ外の将来候補とする。 | まずはGitDiffRunからViewer表示までの通常サイズ体験を安定させ、大容量時は安全なエラー表示で十分に運用できるため。 |
| dec_0073_004 | 2026-06-27 | Git管理の大容量問題は、生成用フォルダーの.gitignore除外で解消する。 | 一時成果物のDiffToJson_*.jsonをGitに入れなければ、リポジトリ肥大化やGit差分ノイズは避けられるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0073_001 | 2026-06-27 | incident_added | GitDiffRun結果JSONのDiffJsonViewer自動表示のみを1件で扱う案 | v0.15.8で通常サイズの直接返却・Viewer表示、v0.15.9で大量データの段階的取り扱いを分離 | 通常ケースの体験実装と、大量データの堅牢化・安全停止・部分読み込みを分けることで、実装スコープとリスクを管理しやすくするため。 |
| chg_0073_002 | 2026-06-27 | incident_policy_update | v0.15.9は、APIレスポンス肥大化対策としてsummary-only / diff_id / 部分読み込みを段階的に扱うインシデントだった。 | v0.15.9は、wwwroot配下のgitignore対象差分JSONをDiffJsonViewer.htmlが扱えるかどうかの表示上限・エラー表示インシデントへ整理した。diff_idや部分読み込みは将来候補へ後退。 | 差分JSON本文をAPIレスポンスで運ばない方針になったため、大容量問題の主戦場がAPIではなくViewer表示限界へ変わった。 |

### v0.16.0-proposal-driven-jobflow: AI提案駆動JobFlow / JobControl JSON構想
- 作業ID: studio_work_0074
- 種別: architecture
- 優先度: high
- 状態: 未着手
- 確認状態: 未確認
- 対象ファイル: data/json/01_main/studio_work_incident_data_*.json, future: data/json/02_job/job_control_data_v0_1.json, data/json/02_job/improvement_proposal_data_v0_1.json, data/json/02_job/job_approval_data_v0_1.json, data/json/02_job/job_run_result_data_v0_1.json, defs/job/job_control_view_def_v0_1.json, defs/job/improvement_proposal_view_def_v0_1.json

#### 目的

AI作業の開始点を、人間の明示依頼だけでなくAI改善提案JSONからも始められるようにする。Improvement Proposal JSON → 人間承認 → JobControl JSON → Job実行 → TestResult / GitDiff / AIテスト物語 / AI差分物語 / Incident更新 までを、AI協働可能なJobFlowとして定義する。

#### 背景

Studioくんでは、Incident JSON、GitDiffRun、DiffJsonViewer、AI差分物語、AIテスト物語、AI協働可能なノーコードテスト、JobControl JSON構想がつながり始めている。特に肝は、作業のスタートを『人間が毎回チャットで依頼する』だけにせず、AIが前回作業や現在Contextから出した改善提案を、次のJob候補として扱えるかどうかである。これが成立すると、AIが作業し、改善提案を出し、人間が承認し、次Jobが生成されるという、観察可能で承認可能な自律型AI協働フローへ進める。

#### 対象範囲

AI提案駆動JobFlowの最小データ構造と流れを整理する。対象は Proposal Context Pack、Improvement Proposal JSON、Proposal Evaluation / Approval JSON、JobControl JSON、JobRun Result JSON、Artifact Manifest、AIテスト物語、AI差分物語、Incident更新の関係定義とする。JobControl JSONには source_proposal_id / source_incident_id / inputs / required_rules / steps / stop_conditions / outputs / human_approval / artifact_manifest を持たせる方針を検討する。初期段階では完全自動実行ではなく、AI提案からJobControl JSONを生成し、Studioくんで人間が承認・確認できることを主目的とする。Jobの中では、TestPattern JSON / Expected JSON生成、汎用Test Runner実行、Result JSON生成、GitDiffRun、DiffJsonViewer用viewer_url生成、AIテスト物語生成、AI差分物語生成、Incident更新を標準ステップ候補として扱う。

#### 対象外

完全自律実行、外部AIエージェント常駐、バックグラウンド監視、無承認のコード変更、無承認の次Job連鎖、AIが提案を即実行する挙動は対象外とする。初期段階では、自動実行基盤そのものよりも、AI提案をJob候補に変換し、人間が承認してから次Jobとして扱えるデータ構造を育てることを優先する。汎用Test Runner本体、DiffJsonViewer高度化、AI差分物語/AIテスト物語の詳細生成エンジンは、必要に応じて別インシデントで扱う。

#### 固定名方針

JobFlow系の job_id / proposal_id / source_proposal_id / source_incident_id / approval_status / stop_conditions / outputs などは、JobFlowデータの標準フィールド候補として扱う。ただしRuntimeが任意Dataの特定フィールド名に依存する実装は避ける。JobFlow用Data/ViewDef/Actionの契約として定義された範囲で使用する。

#### module化方針

type="module" 化は今回の主目的ではない。まずはData JSON / ViewDef / Action / Prompt生成の構造設計として扱い、既存の従来script方式・既存Studio運用と矛盾しない形で育てる。

#### リスク

AI提案をそのまま作業命令として扱うと、不要・危険・重複・低優先の作業が連鎖するリスクがある。提案は必ず候補であり、人間承認または評価Jobを通して approved / rejected / deferred / converted を明示する必要がある。ループが長くなると目的逸脱や同じ提案の再発が起きるため、max_iterations、stop_if_no_approved_proposals、stop_if_same_proposal_repeated、stop_if_tests_fail、stop_if_unexpected_files_changed などの停止条件が重要になる。

#### 確認観点

Improvement Proposal JSONからJobControl JSON候補を生成できること。提案がcandidateのまま実行されず、human_approvalでapprovedになってから次Jobへ変換されること。JobControl JSONにsource_proposal_idとsource_incident_idを保持できること。Jobの標準出力としてAIテスト物語・AI差分物語・Artifact Manifest・Incident更新を表現できること。stop_conditionsにより、ルール未読、対象ファイル欠落、テスト失敗、想定外差分、未承認提案が安全に止まること。

#### 作業会話サマリ


##### 依頼 / 方針

自律型AIエージェント構想というかJOBフローの話もインシデントに追加して育てたい。JOBフローが実現できたら、AI差分物語やAIテスト物語の生成まで1つのJOBの中でできるはず。特に、このインシデントの肝は、スタートがAI提案から始められるか否かである。まずはインシデントに追加してほしい。

##### AI整理

AI提案駆動JobFlowとしてインシデント化する。中心は、AIの改善提案を単なるメモで終わらせず、Improvement Proposal JSONとして構造化し、人間承認を経てJobControl JSONへ変換できるようにすること。JobControl JSONが実行手順・停止条件・成果物・承認対象を持てば、1つのJobの中でTestPattern生成、汎用Test Runner実行、GitDiffRun、AIテスト物語、AI差分物語、Incident更新まで標準出力として扱える。

##### 追加コメント

初期JobFlowでは、完全なパラレル実行は対象外とする。
AI提案生成や影響範囲分析などのread-only jobは将来並列化候補とするが、
source / incident / ViewDef / Expected などを書き換えるwrite jobは直列実行を基本とする。

理由:
AI作業では、並列実装よりも、入力・差分・成果物・承認状態を確実に追跡できることを優先する。
まずは1 Jobを安全に最後まで実行し、AI差分物語 / AIテスト物語 / Artifact Manifest / Incident更新まで一気通貫させる。

##### AI追加回答

studio_work_0074 として AI提案駆動JobFlow / JobControl JSON構想を追加。AI改善提案JSONを次Jobの候補として扱い、人間承認後にJobControl JSONへ変換する流れを中心に整理した。Jobの標準出力としてTestResult、GitDiff、AIテスト物語、AI差分物語、Artifact Manifest、Incident更新を扱う方針を記録した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0074_001 | 2026-06-28 | user | JobFlow構想の整理相談 | 自律型AIエージェント構想というか、JOBフローの話もインシデントに追加して育てたい。JOBフローが実現できたら、AI差分物語やAIテスト物語の生成まで1つのJOBの中でできるのではないかと相談。 |
| disc_0074_002 | 2026-06-28 | assistant | JobFlow構想整理 | JobControl JSONは、入力、参照ルール、実行手順、停止条件、成果物、承認対象を持つAI作業定義として整理できる。1つのJob内でTestPattern生成、汎用Test Runner実行、GitDiffRun、AIテスト物語、AI差分物語、Incident更新まで標準ステップ化できると整理。 |
| disc_0074_003 | 2026-06-28 | user | 肝の明確化 | このインシデントの肝は、スタートがAI提案から始められるか否かである。まずはインシデントに追加してほしい。 |
| disc_0074_004 | 2026-06-28 | assistant | インシデント追加 | AI提案駆動JobFlowとして、Improvement Proposal JSONから人間承認を経てJobControl JSONへ変換し、Job実行結果としてAIテスト物語・AI差分物語・Artifact Manifest・Incident更新へつなげるインシデントを追加した。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0074_001 | 2026-06-28 | JobFlowの開始点は、人間の明示依頼だけでなくAI改善提案JSONも許容する。 | AIの出力を次のAI入力にできる形で残すことが、観察可能な自律型AI協働フローの入口になるため。 |
| dec_0074_002 | 2026-06-28 | AI提案は命令ではなくcandidateとして扱い、人間承認または評価Jobを通してからJobControl JSONへ変換する。 | AI提案を即実行すると、不要・危険・重複・低優先の作業が連鎖するリスクがあるため。 |
| dec_0074_003 | 2026-06-28 | Jobの標準出力候補にAIテスト物語とAI差分物語を含める。 | 人間が承認するためには、TestResultやGitDiffそのものだけでなく、なぜ承認できるかを説明する物語化された判断材料が必要なため。 |
| dec_0074_004 | 2026-06-28 | テストはテストコード増殖ではなく、TestPattern JSON / Expected JSON / Result JSON をJobFlowの成果物として扱う。 | AI協働可能なノーコードテストでは、テストコードは汎用Runnerとして奥に下げ、テスト内容をJSON定義として育てるため。 |
| dec_0074_005 | 2026-06-28 | 初期段階では完全自動実行ではなく、JobControl JSONの生成・表示・承認・AI依頼プロンプト化を優先する。 | いきなり外部エージェント化すると危険と実装範囲が大きいため、まずはStudioくん上で見えるJobFlowとして育てるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0074_001 | 2026-06-28 | incident_added | studio_work_incident_data_v0_73_gitdiff_viewer_wwwroot_src_policy_updated.json / items_count=73 | studio_work_incident_data_v0_74_proposal_driven_jobflow_added.json / items_count=74 | AI提案を起点にJobControl JSONへつなげ、AI差分物語・AIテスト物語・Artifact Manifest・Incident更新までを1つのJobFlowとして育てるため。 |

### v0.15.5.1-context-model-cleanup: 主文脈 / 対象文脈モデル整理
- 作業ID: studio_work_0075
- 種別: architecture_cleanup
- 分類: context_model
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: data/json/00_rules/frb_view_def_schema_v0_9.json, data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json, data/json/00_rules/context_refs_sample_data_v0_1.json, defs/rules/context_refs_sample_view_def_v0_1.json, data/json/00_rules/VIEWDEF_CONTEXT_MODEL_CLEANUP_REPORT_v0_15_5_1.md, data/json/01_main/studio_work_incident_data_v0_74_context_model_cleanup_incidents_added.json

#### 目的

v0.15.5初期実装で見えたズレを踏まえ、主文脈と対象文脈の用語・JSON配置・明細構造・表示方針を確定する。

#### 背景

context_refsにはViewDef全体にかかる文脈と、個別明細にかかる文脈が混在し得る。全体は主文脈として画面の入口に、個別明細は対象文脈としてDetail上部に置く整理が必要になった。

#### 対象範囲

主文脈はData root main_context_refs[]、対象文脈はData明細context_refs[]として整理する。ViewDefは文脈実データを持たず、context.main_context.data_path / context.target_context.field / data_path で場所と表示・編集方法だけを宣言する。旧context.read_contractは互換宣言として残すが、具体的なrequired_refs[]は埋め込まない。

#### 対象外

この作業ではJSのヘッダー表示・Detail表示・自動読込実行までは行わない。まずインシデント、Rules、Schema、サンプルData/ViewDefの地ならしに限定する。

#### 固定名方針

Runtimeが特定Data名に依存しないよう、主文脈はViewDef側の契約、対象文脈はViewDefで宣言された明細フィールドとして扱う。context_refsは標準メタ候補として扱うが、使用ルールを明記する。

#### module化方針

type="module" 化は行わない。v0.15.5.1ではJS実装を主目的にしない。

#### リスク

概念整理前にUI実装へ進むと、context_refsが普通のGridデータに見え、文脈契約という思想が画面体験に反映されない。

#### 確認観点

主文脈がViewDef側 context.main_context.refs[]、対象文脈がData明細側 context_refs[] としてSchema/Rules/Sample/Incidentに明記されていること。Context Ref明細項目が共通化されていること。旧read_contract互換方針があること。JS実装に踏み込んでいないこと。JSON parseが通ること。

#### 作業会話サマリ


##### 依頼 / 方針

v0.15.5の主文脈/対象文脈設計を、JS実装へ進む前にインシデント側で綺麗に整理したい。必要なら複数インシデントへ分割してよい。

##### AI整理

v0.15.5をそのまま進めず、主文脈/対象文脈モデルを先にインシデント側へ焼き込む。これにより後続JS実装のズレを防ぐ。

##### 追加コメント

最新資材 wwwroot281038.zip と更新済みIncident JSONを添付し、phase v0.15.5.1-context-model-cleanup の作業を依頼。Foundation Rule 19のZIP返却契約に従う。

##### AI追加回答

# AI回答

## 今回の補修

- `defs/rules/context_refs_sample_view_def_v0_1.json`
- `data/json/00_rules/context_refs_sample_data_v0_1.json`
- `data/json/00_rules/frb_view_def_schema_v0_9.json`
- `data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json`
- `data/json/00_rules/VIEWDEF_CONTEXT_MODEL_CLEANUP_REPORT_v0_15_5_1.md`
- `data/json/01_main/studio_work_incident_data_v0_74_context_model_cleanup_incidents_added.json`

## 直したこと

v0.15.5.1初回整理で、主文脈の実データをViewDef側 `context.main_context.refs[]` に置いてしまっていた点を修正した。

## 確定モデル

- ViewDefは画面定義だけを持つ。
- 主文脈の実データはData root `main_context_refs[]` に置く。
- ViewDefは `context.main_context.data_path` で主文脈のDataパスを宣言する。
- 対象文脈の実データはData明細オブジェクト内 `context_refs[]` に置く。
- ViewDefは `context.target_context.field` / `data_path` で対象文脈の場所を宣言する。
- 旧 `context.read_contract` は互換宣言として残すが、具体的な `required_refs[]` は埋め込まない。

## 確認結果

- JSON parse：OK
- `items_count`: 77 維持
- `work_item_id` 重複なし
- JSファイルは未変更
- 更新済みIncident JSONはZIP内 `data/json/01_main/` に収録
- runtime生成物除外：OK


#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0075_001_user | 2026-06-28 | user | インシデント側の地ならし依頼 | v0.15.5の主文脈/対象文脈設計を、JS実装へ進む前にインシデント側で綺麗に整理したい。必要なら複数インシデントへ分割してよい。 |
| disc_0075_002_assistant | 2026-06-28 | assistant | v0.15.5.1追加方針 | JS実装前に、主文脈/対象文脈の用語、JSON配置、共通明細構造、旧read_contract互換方針を整理するインシデントとして追加。 |
| disc_0075_003_user_request_v01551 | 2026-06-28 | user | v0.15.5.1-context-model-cleanup 作業依頼 | 最新資材を添付し、v0.15.5.1-context-model-cleanup として主文脈/対象文脈モデル整理を依頼。 |
| disc_0075_004_assistant_completion_report | 2026-06-28 | assistant | v0.15.5.1-context-model-cleanup 作業結果 | # AI回答<br><br>## 今回の更新<br><br>- `data/json/00_rules/frb_view_def_schema_v0_9.json`<br>- `data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json`<br>- `data/json/00_rules/context_refs_sample_data_v0_1.json`<br>- `defs/rules/context_refs_sample_view_def_v0_1.json`<br>- `data/json/00_rules/VIEWDEF_CONTEXT_MODEL_CLEANUP_REPORT_v0_15_5_1.md`<br>- `data/json/01_main/studio_work_incident_data_v0_74_context_model_cleanup_incidents_added.json`<br><br>## やったこと<br><br>v0.15.5 初期実装の `context.read_contract` / `context_refs` を、JS実装へ進む前にモデル整理した。<br><br>## 確定したモデル<br><br>- 主文脈<br>  - ViewDef / 画面全体にかかる文脈<br>  - 正本: `context.main_context.refs[]`<br>  - 表示方針: ヘッダー要約 + ボタン展開<br><br>- 対象文脈<br>  - インシデント1件、テストパターン1件、ルール1件など個別対象にかかる文脈<br>  - 正本: Data明細オブジェクト内の `context_refs[]`<br>  - 表示方針: Detail上部の入口セクション<br><br>## Context Ref共通明細<br><br>主文脈でも対象文脈でも、明細1件の構造は共通とする。<br><br>- `context_ref_id`<br>- `title`<br>- `read_timing`<br>- `target_path`<br>- `purpose`<br>- `failure_policy`<br>- `trust_category`<br>- `required`<br>- `enabled`<br>- `sort_order`<br>- `note`<br><br>## 互換方針<br><br>旧 `context.read_contract` は削除せず、互換入口として残す。新規ViewDefでは `context.main_context.refs[]` を優先する。<br><br>## 確認結果<br><br>- JSON parse：OK<br>- `items_count`: 77 維持<br>- `work_item_id` 重複なし<br>- v0.15.5.1 は完了扱いへ更新<br>- JSファイルは未変更<br>- 更新済みIncident JSONはZIP内 `data/json/01_main/` に収録<br>- runtime生成物除外：OK<br> |
| disc_0075_v0155_1_fix_user_001 | 2026-06-28 | user | 主文脈データ配置の指摘 | たぶん、ズレている気がする。なんで、ViewDef側に文脈の内容となるデータがいる？？ ViewDefは画面定義だけ。最新資材添付します。再度お願いします。 |
| disc_0075_v0155_1_fix_assistant_001 | 2026-06-28 | assistant | v0.15.5.1補修結果 | # AI回答<br><br>## 今回の補修<br><br>- `defs/rules/context_refs_sample_view_def_v0_1.json`<br>- `data/json/00_rules/context_refs_sample_data_v0_1.json`<br>- `data/json/00_rules/frb_view_def_schema_v0_9.json`<br>- `data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json`<br>- `data/json/00_rules/VIEWDEF_CONTEXT_MODEL_CLEANUP_REPORT_v0_15_5_1.md`<br>- `data/json/01_main/studio_work_incident_data_v0_74_context_model_cleanup_incidents_added.json`<br><br>## 直したこと<br><br>v0.15.5.1初回整理で、主文脈の実データをViewDef側 `context.main_context.refs[]` に置いてしまっていた点を修正した。<br><br>## 確定モデル<br><br>- ViewDefは画面定義だけを持つ。<br>- 主文脈の実データはData root `main_context_refs[]` に置く。<br>- ViewDefは `context.main_context.data_path` で主文脈のDataパスを宣言する。<br>- 対象文脈の実データはData明細オブジェクト内 `context_refs[]` に置く。<br>- ViewDefは `context.target_context.field` / `data_path` で対象文脈の場所を宣言する。<br>- 旧 `context.read_contract` は互換宣言として残すが、具体的な `required_refs[]` は埋め込まない。<br><br>## 確認結果<br><br>- JSON parse：OK<br>- `items_count`: 77 維持<br>- `work_item_id` 重複なし<br>- JSファイルは未変更<br>- 更新済みIncident JSONはZIP内 `data/json/01_main/` に収録<br>- runtime生成物除外：OK<br> |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0075_001 | 2026-06-28 | 全体文脈は『主文脈』、個別明細文脈は『対象文脈』と呼ぶ。 | 行文脈よりも、インシデント・テストパターン・ルールなどの対象単位に自然に適用できるため。 |
| dec_0075_002 | 2026-06-28 | 主文脈は context.main_context.refs[]、対象文脈は context_refs[] を基本配置とする。 | ViewDef全体の前提と、明細単位の追加前提を分離するため。 |
| dec_0075_003 | 2026-06-28 | 旧 context.read_contract は互換扱いとし、削除ではなく main_context.refs への移行候補とする。 | 既存v0.15.5実装とサンプルを壊さず、段階的に整理するため。 |
| dec_0075_004 | 2026-06-28 | 主文脈は context.main_context.refs[] を正本とする。 | ViewDef全体にかかる文脈をData行と混ぜず、画面の入口として扱うため。 |
| dec_0075_005 | 2026-06-28 | 対象文脈はData明細オブジェクト内の context_refs[] を正本とする。 | インシデント1件、テストパターン1件、ルール1件など個別対象にかかる追加文脈を、対象本文の前提として管理するため。 |
| dec_0075_006 | 2026-06-28 | 主文脈と対象文脈のContext Ref明細構造は共通化する。 | 同じ『読むべき文脈』であり、スコープだけが違うため。 |
| dec_0075_007 | 2026-06-28 | 旧 context.read_contract は互換入口として残す。 | v0.15.5初期実装や既存サンプルを壊さず、段階的にmain_contextへ移行するため。 |
| dec_0075_008 | 2026-06-28 | v0.15.5.1ではJS実装に踏み込まない。 | 画面ヘッダー表示とDetail上部表示は後続フェーズへ分け、設計整理と実装を混ぜないため。 |
| dec_0075_v0155_1_fix_001 | 2026-06-28 | ViewDefには主文脈/対象文脈の実データを置かない。ViewDefはDataパスと表示・編集定義だけを持つ。 | ViewDefは画面定義であり、文脈の内容データを持つとData/ViewDef分離が崩れるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0075_001 | 2026-06-28 | incident_added | v0.15.5に主文脈/対象文脈整理とUI実装の意図が混在していた。 | v0.15.5.1として、用語・JSON配置・Rules/Schema/Data整理を独立インシデント化。 | JS実装前に設計モデルを固定し、後続UI実装のズレを防ぐため。 |
| chg_0075_002 | 2026-06-28 | viewdef_generation_rule_update | viewdef_rule_27 は read_contract / row context_refs 分離の説明が中心。 | viewdef_rule_27 を主文脈/対象文脈モデルへ更新し、viewdef_rule_27_01を追加。 | 画面全体文脈と個別対象文脈の表示体験をJS実装前に明文化するため。 |
| chg_0075_003 | 2026-06-28 | sample_restructure | context_refs_sample_data は context_refs 自体が主Gridデータに見える構成。 | sample_targets[] の各明細内に context_refs[] を置く構成へ変更。 | 対象文脈はData明細にぶら下がる入口であり、context_refs自体を通常業務データとして見せないため。 |
| chg_0075_004 | 2026-06-28 | sample_viewdef_context_model | context_refs_sample_view_def は context.read_contract のみを主契約としていた。 | context.main_context / context.target_context を追加し、read_contract は互換入口として残した。 | 新規ViewDefではmain_contextを正本とし、旧実装互換も保つため。 |
| chg_0075_005 | 2026-06-28 | report_added | v0.15.5.1の設計整理レポートがなかった。 | VIEWDEF_CONTEXT_MODEL_CLEANUP_REPORT_v0_15_5_1.md を追加。 | 後続v0.15.5.2/.3の前提を人間とAIが読み返せるようにするため。 |
| chg_0075_v0155_1_fix_001 | 2026-06-28 | context_model_correction | 主文脈の実データをViewDef側 context.main_context.refs[] / read_contract.required_refs[] に置いていた。 | 主文脈の実データをData root main_context_refs[] に移し、ViewDef側は context.main_context.data_path などの宣言だけにした。 | ViewDefは画面定義だけであり、文脈内容データを保持すべきではないため。 |

### v0.15.5.2-main-context-header-panel: 主文脈ヘッダー表示 / 展開編集パネル
- 作業ID: studio_work_0076
- 種別: feature
- 分類: context_ui
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/js/core/state.js, wwwroot/js/core/viewdef_context_contract.js, wwwroot/js/runtime/load_runtime.js, wwwroot/js/renderers/*, wwwroot/styles.css, wwwroot/index.html, relevant ViewDefs

#### 目的

ViewDef全体にかかる主文脈を、画面ヘッダー/概要部分に要約表示し、ボタン押下で明細を確認・必要に応じて編集できるようにする。

#### 背景

v0.15.5初期表示ではcontext_refsサンプルが通常Gridとして見え、主文脈が画面の入口として見えなかった。主文脈はData行ではなく、画面全体の前提としてヘッダーに出すべきである。

#### 対象範囲

ViewDefの context.main_context.data_path からData rootの主文脈refs配列を取得し、ヘッダーに件数・必須件数・停止系失敗方針・読みタイミングを要約表示する。ボタンで主文脈明細を展開し、Data側へ編集反映できるようにする。主文脈を通常Gridの主役にしない。旧read_contractは互換宣言として限定的に扱う。

#### 対象外

対象文脈context_refs[]のDetail上部表示はv0.15.5.3で扱う。外部文脈ファイルの自動読込やLLM投入はこの段階では行わない。

#### 固定名方針

Runtimeは特定ViewDef名や特定Data名ではなく、ViewDefに宣言された context.main_context.data_path を読み、Data root上の主文脈refsを扱う。ViewDef内に具体的な文脈refs実データを置かない。

#### module化方針

type="module" 化は行わない。既存script方式を維持する。

#### リスク

ヘッダーへ出しすぎると画面が重くなる。常時表示は要約に留め、明細はボタンで確認する。

#### 確認観点

主文脈0件/1件/複数件で表示が壊れないこと。必須件数や停止系失敗方針が要約に出ること。ViewDefにcontext未定義でも壊れないこと。主文脈が通常Gridの主役にならず、対象一覧が主Gridとして表示されること。更新済みIncident JSONがZIP内data/json/01_main/に収録されること。

#### 作業会話サマリ


##### 依頼 / 方針

v0.15.5の主文脈/対象文脈設計を、JS実装へ進む前にインシデント側で綺麗に整理したい。必要なら複数インシデントへ分割してよい。

##### AI整理

主文脈は普通のGridデータではなく画面全体の入口なので、ヘッダー要約と展開明細として扱う。

##### 追加コメント

今回の作業依頼: incident_file=data/json/01_main/studio_work_incident_data_v0_74_context_model_cleanup_incidents_added.json / phase=v0.15.5.2-main-context-header-panel。Foundation Rule 19「GitHub基準ソースとZIP返却契約」を参照して対応。

##### AI追加回答

# AI回答

## 今回の更新
- `wwwroot/js/core/state.js`
- `wwwroot/js/core/viewdef_context_contract.js`
- `wwwroot/js/renderers/field_controls.js`
- `wwwroot/js/runtime/load_runtime.js`
- `wwwroot/js/runtime/detail_save.js`
- `wwwroot/index.html`
- `wwwroot/styles.css`
- `defs/rules/context_refs_sample_view_def_v0_1.json`
- `data/json/00_rules/context_refs_sample_data_v0_1.json`
- `data/json/00_rules/frb_view_def_schema_v0_9.json`
- `data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json`
- `data/json/00_rules/MAIN_CONTEXT_HEADER_PANEL_REPORT_v0_15_5_2.md`
- `data/json/01_main/studio_work_incident_data_v0_74_context_model_cleanup_incidents_added.json`

## やったこと
- 主文脈を通常Gridの主役にせず、概要ヘッダー上の要約 + 「主文脈を確認」ボタンで扱うRuntimeを追加。
- ViewDefは `context.main_context.data_path` などの表示・参照宣言だけを持ち、主文脈の実データはData root `main_context_refs[]` から読むように整理。
- 展開パネル内で主文脈明細を確認・編集し、「主文脈を反映」でData側へ反映できるようにした。
- `context_refs_sample_view_def_v0_1.json` から主文脈Gridを外し、主Gridを `sample_targets[]` に戻した。
- Schema/Rulesへ「主文脈は通常Gridではなくヘッダー要約+展開パネルで扱う」契約を追加。

## 方針
- 主文脈 = 画面全体の入口。Data root `main_context_refs[]`。
- 対象文脈 = 個別対象の入口。Data明細 `context_refs[]`。
- ViewDefは文脈データを持たず、Data上の場所と表示方法だけを宣言する。
- 対象文脈Detail上部表示は `v0.15.5.3-target-context-detail-panel` に残す。

## 確認結果
- JSON parse：OK
- JS `node --check`：OK
- 主文脈Grid撤去：OK
- 主Grid = `sample_targets[]`：OK
- ViewDef内に主文脈実データなし：OK
- 更新済みIncident JSONのZIP内収録：OK
- runtime生成物除外：OK

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0076_001_assistant | 2026-06-28 | assistant | v0.15.5.2追加方針 | 主文脈はViewDef全体にかかるため、ヘッダー/概要エリアへ要約表示し、ボタンで明細を開くUI実装インシデントとして追加。 |
| disc_0076_002_user_actual_request | 2026-06-28 | user | v0.15.5.2作業依頼 | あぁーーjs側が対応できてない事実があるってことやね？？ まぁ、意識が一致しているか、じゃっかん不安あるけどしかたないね。次にまず進もう。v0.15.5.2-main-context-header-panel の作業を依頼。 |
| disc_0076_003_assistant_completion_report | 2026-06-28 | assistant | v0.15.5.2完了報告 | # AI回答<br><br>## 今回の更新<br>- `wwwroot/js/core/state.js`<br>- `wwwroot/js/core/viewdef_context_contract.js`<br>- `wwwroot/js/renderers/field_controls.js`<br>- `wwwroot/js/runtime/load_runtime.js`<br>- `wwwroot/js/runtime/detail_save.js`<br>- `wwwroot/index.html`<br>- `wwwroot/styles.css`<br>- `defs/rules/context_refs_sample_view_def_v0_1.json`<br>- `data/json/00_rules/context_refs_sample_data_v0_1.json`<br>- `data/json/00_rules/frb_view_def_schema_v0_9.json`<br>- `data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json`<br>- `data/json/00_rules/MAIN_CONTEXT_HEADER_PANEL_REPORT_v0_15_5_2.md`<br>- `data/json/01_main/studio_work_incident_data_v0_74_context_model_cleanup_incidents_added.json`<br><br>## やったこと<br>- 主文脈を通常Gridの主役にせず、概要ヘッダー上の要約 + 「主文脈を確認」ボタンで扱うRuntimeを追加。<br>- ViewDefは `context.main_context.data_path` などの表示・参照宣言だけを持ち、主文脈の実データはData root `main_context_refs[]` から読むように整理。<br>- 展開パネル内で主文脈明細を確認・編集し、「主文脈を反映」でData側へ反映できるようにした。<br>- `context_refs_sample_view_def_v0_1.json` から主文脈Gridを外し、主Gridを `sample_targets[]` に戻した。<br>- Schema/Rulesへ「主文脈は通常Gridではなくヘッダー要約+展開パネルで扱う」契約を追加。<br><br>## 方針<br>- 主文脈 = 画面全体の入口。Data root `main_context_refs[]`。<br>- 対象文脈 = 個別対象の入口。Data明細 `context_refs[]`。<br>- ViewDefは文脈データを持たず、Data上の場所と表示方法だけを宣言する。<br>- 対象文脈Detail上部表示は `v0.15.5.3-target-context-detail-panel` に残す。<br><br>## 確認結果<br>- JSON parse：OK<br>- JS `node --check`：OK<br>- 主文脈Grid撤去：OK<br>- 主Grid = `sample_targets[]`：OK<br>- ViewDef内に主文脈実データなし：OK<br>- 更新済みIncident JSONのZIP内収録：OK<br>- runtime生成物除外：OK |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0076_001 | 2026-06-28 | 主文脈は常時明細表示せず、ヘッダー要約 + 確認ボタンで扱う。 | 画面の前提として重要だが、常時明細表示すると通常作業の邪魔になるため。 |
| dec_0076_002 | 2026-06-28 | 主文脈はViewDef内refsではなくData root main_context_refs[]を読む。 | ViewDefは画面定義であり、文脈の実データを持つとData/ViewDef分離が崩れるため。 |
| dec_0076_003 | 2026-06-28 | 主文脈GridをサンプルViewDefから外し、対象一覧を主Gridに戻す。 | 主文脈を通常Gridの主役にすると、対象一覧と対象文脈の確認導線が消えるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0076_001 | 2026-06-28 | incident_added | 主文脈が通常Gridデータまたはサンプルとして見える状態だった。 | 主文脈をヘッダー要約と展開明細として表示する後続インシデントを追加。 | 主文脈を画面全体の入口として扱うUI体験へ寄せるため。 |
| chg_0076_002 | 2026-06-28 | runtime_header_panel | 主文脈を通常Gridとして表示するしかなく、対象一覧が主Gridとして見えにくかった。 | Data root main_context_refs[] を概要ヘッダー上の要約+展開パネルとして表示し、通常Gridは対象一覧へ戻した。 | 主文脈は画面全体の入口であり、Gridの主役ではないため。 |
| chg_0076_003 | 2026-06-28 | viewdef_sample_cleanup | context_refs_sample_view_def_v0_1.json に mainContextGrid と targetsGrid が並び、Runtimeの最初のGrid選択で主文脈Gridが主役になった。 | mainContextGrid を撤去し、targetsGrid を唯一の主Gridにした。主文脈は context.main_context.data_path をもとにRuntimeヘッダーパネルで表示する。 | 現行Runtimeの主Grid処理に合わせ、対象一覧と対象文脈の導線を維持するため。 |

### v0.15.5.3-target-context-detail-panel: 対象文脈Detail上部表示 / context_refs編集
- 作業ID: studio_work_0077
- 種別: feature
- 分類: context_ui
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み

#### 対象ファイル

wwwroot/js/core/state.js
wwwroot/js/core/viewdef_context_contract.js
wwwroot/js/renderers/field_controls.js
wwwroot/js/renderers/grid_detail.js
wwwroot/js/runtime/load_runtime.js
wwwroot/js/runtime/detail_save.js
wwwroot/index.html
wwwroot/styles.css
defs/rules/context_refs_sample_view_def_v0_1.json
data/json/00_rules/context_refs_sample_data_v0_1.json
data/json/00_rules/frb_view_def_schema_v0_9.json
data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json
data/json/00_rules/TARGET_CONTEXT_DETAIL_PANEL_REPORT_v0_15_5_3.md
data/json/01_main/studio_work_incident_data_v0_74_context_model_cleanup_incidents_added.json

#### 目的

Data明細オブジェクト内の context_refs[] を対象文脈として、Detail画面の上部に要約・確認・編集できる形で表示する。

#### 背景

対象文脈はインシデント1件、テストパターン1件、ルール1件などの個別対象を扱う前に読む追加文脈である。本文や変更履歴に埋もれるのではなく、明細詳細の入口に置く必要がある。

#### 対象範囲

ViewDefで対象文脈フィールドを宣言し、既定ではcontext_refs[]を対象文脈として扱う。Detail上部に『対象文脈 n件』の要約を表示し、展開時にContext Ref明細をobjectArrayとして確認・編集できるようにする。Grid列には中身を出しすぎず件数要約を基本にする。

#### 対象外

主文脈ヘッダー表示はv0.15.5.2で扱う。対象文脈に基づく外部文脈ファイル自動読込・LLM投入・実行停止制御は後続とする。

#### 固定名方針

context_refsは標準候補として扱うが、ViewDef側で対象文脈フィールドを宣言できる余地を残す。Runtimeが特定業務フィールド名へ依存しないようにする。

#### module化方針

type="module" 化は行わない。既存script方式を維持する。

#### リスク

context_refs[]を通常Detail Formの入力欄として扱うと、配列が件数字符列で壊れるリスクがある。既存objectArray保存健全性ルールを守る必要がある。

#### 確認観点

context_refs[]が明細オブジェクト内にあるサンプルでDetail上部に表示されること。対象文脈を編集・追加・削除・反映できること。編集後もcontext_refs[]が配列として残ること。context_refs未定義行でも壊れないこと。Gridでは生JSONではなく件数要約になること。

#### 作業会話サマリ


##### 依頼 / 方針

v0.15.5の主文脈/対象文脈設計を、JS実装へ進む前にインシデント側で綺麗に整理したい。必要なら複数インシデントへ分割してよい。

##### AI整理

対象文脈は明細本文に混ざる普通の補足ではなく、その対象を扱う前に読む入口としてDetail上部へ出す。

##### 追加コメント

v0.15.5.3-target-context-detail-panel の追加UX補修依頼。対象文脈がある場合はDetail上部で横幅いっぱいを使う。主文脈と同様に対象文脈も普段は隠し、ボタンクリックで開く形にする。主文脈・対象文脈ともに余白を減らし、縦方向をコンパクトに調整する。

##### AI追加回答

# AI回答

## 今回の更新
- `wwwroot/js/core/state.js`
- `wwwroot/js/core/viewdef_context_contract.js`
- `wwwroot/js/runtime/load_runtime.js`
- `wwwroot/index.html`
- `wwwroot/styles.css`
- `data/json/00_rules/TARGET_CONTEXT_DETAIL_PANEL_COMPACT_REPORT_v0_15_5_3_1.md`
- `data/json/01_main/studio_work_incident_data_v0_74_context_model_cleanup_incidents_added.json`

## やったこと
- 対象文脈DetailパネルをDetail Form内で横幅いっぱい表示に変更。
- `targetContextDetailPanelExpanded` の初期値を `false` にし、対象文脈も主文脈と同じく通常は要約表示に変更。
- 「対象文脈を追加」ボタンは展開時のみ表示し、閉じている時の要約行をコンパクト化。
- 主文脈・対象文脈のパネル、バッジ、テーブル、入力欄、フッターの余白を縮小し、縦方向をコンパクト化。
- index.html のキャッシュバスターを更新。

## 方針
- 主文脈は画面全体の入口、対象文脈は明細の入口。
- どちらも本文より前に置くが、明細は常時展開せず、必要な時だけ開く。
- 対象文脈はDetail上部で横幅いっぱいを使い、横スクロール前提のContext Ref表を読みやすくする。

## 確認結果
- JSON parse：OK
- JS `node --check`：OK
- 対象文脈初期折りたたみ：OK
- 対象文脈横幅いっぱい表示CSS：OK
- 主文脈/対象文脈コンパクトCSS：OK
- 更新済みIncident JSONのZIP内収録：OK
- runtime生成物除外：OK


#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0077_001_assistant | 2026-06-28 | assistant | v0.15.5.3追加方針 | 対象文脈はData明細オブジェクト内のcontext_refs[]として扱い、Detail上部の入口セクションで要約・展開・編集できるUI実装インシデントとして追加。 |
| disc_0077_001_user_request_v01553 | 2026-06-28 | user | v0.15.5.3作業依頼 | 今回の作業依頼:<br>- incident_file: data/json/01_main/studio_work_incident_data_v0_74_context_model_cleanup_incidents_added.json<br>- phase: v0.15.5.3-target-context-detail-panel<br><br>作業ルール:<br>Foundation Rules raw を参照し、FRB Studio Foundation Rules の foundation_rule_019「GitHub基準ソースとZIP返却契約」に従って対応。 |
| disc_0077_002_ai_report_v01553 | 2026-06-28 | assistant | v0.15.5.3作業結果 | # AI回答<br><br>## 今回の更新<br>- `wwwroot/js/core/state.js`<br>- `wwwroot/js/core/viewdef_context_contract.js`<br>- `wwwroot/js/renderers/field_controls.js`<br>- `wwwroot/js/renderers/grid_detail.js`<br>- `wwwroot/js/runtime/load_runtime.js`<br>- `wwwroot/js/runtime/detail_save.js`<br>- `wwwroot/index.html`<br>- `wwwroot/styles.css`<br>- `defs/rules/context_refs_sample_view_def_v0_1.json`<br>- `data/json/00_rules/context_refs_sample_data_v0_1.json`<br>- `data/json/00_rules/frb_view_def_schema_v0_9.json`<br>- `data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json`<br>- `data/json/00_rules/TARGET_CONTEXT_DETAIL_PANEL_REPORT_v0_15_5_3.md`<br>- `data/json/01_main/studio_work_incident_data_v0_74_context_model_cleanup_incidents_added.json`<br><br>## やったこと<br>- Data明細側 `context_refs[]` を対象文脈としてDetail上部へ表示する専用パネルを追加。<br>- 「対象文脈 n件 / 必須n / 停止n」の要約をDetail上部に表示。<br>- 対象文脈を展開して、Context Ref明細を編集・追加・削除・反映できるようにした。<br>- Gridでは `context_refs[]` の生JSONではなく件数要約を表示するようにした。<br>- 対象文脈は通常childArea末尾のobjectArray表示から除外し、Detail上部パネルを正本表示にした。<br>- Schema / Rules / Sample ViewDef / Sample Data に v0.15.5.3 の契約を反映。<br><br>## 方針<br>- 主文脈 = 画面全体の入口。Data root `main_context_refs[]`。<br>- 対象文脈 = 個別対象の入口。Data明細 `context_refs[]`。<br>- ViewDefは文脈の中身を持たず、Data上の場所と表示・編集方法だけを宣言する。<br>- 対象文脈は本文や変更履歴に埋もれさせず、Detail画面の先頭寄りに置く。<br><br>## 確認結果<br>- JSON parse：OK<br>- JS `node --check`：OK<br>- 対象文脈Detail上部パネル：OK<br>- Grid件数要約：OK<br>- 通常childArea末尾表示から対象文脈を除外：OK<br>- ViewDef内に文脈実データなし：OK<br>- 更新済みIncident JSONのZIP内収録：OK<br>- runtime生成物除外：OK<br> |
| disc_0077_003_user_compact_ux_request | 2026-06-28 | user | v0.15.5.3対象文脈UX補修依頼 | 対象文脈がある場合は横幅いっぱいを使う。主文脈と同様に普段は隠れていてボタンクリックで開く形にする。主文脈・対象文脈ともに余白を減らし、縦方向をコンパクトに調整する。 |
| disc_0077_004_ai_report_v015531_compact | 2026-06-28 | assistant | v0.15.5.3対象文脈UX補修結果 | # AI回答<br><br>## 今回の更新<br>- `wwwroot/js/core/state.js`<br>- `wwwroot/js/core/viewdef_context_contract.js`<br>- `wwwroot/js/runtime/load_runtime.js`<br>- `wwwroot/index.html`<br>- `wwwroot/styles.css`<br>- `data/json/00_rules/TARGET_CONTEXT_DETAIL_PANEL_COMPACT_REPORT_v0_15_5_3_1.md`<br>- `data/json/01_main/studio_work_incident_data_v0_74_context_model_cleanup_incidents_added.json`<br><br>## やったこと<br>- 対象文脈DetailパネルをDetail Form内で横幅いっぱい表示に変更。<br>- `targetContextDetailPanelExpanded` の初期値を `false` にし、対象文脈も主文脈と同じく通常は要約表示に変更。<br>- 「対象文脈を追加」ボタンは展開時のみ表示し、閉じている時の要約行をコンパクト化。<br>- 主文脈・対象文脈のパネル、バッジ、テーブル、入力欄、フッターの余白を縮小し、縦方向をコンパクト化。<br>- index.html のキャッシュバスターを更新。<br><br>## 方針<br>- 主文脈は画面全体の入口、対象文脈は明細の入口。<br>- どちらも本文より前に置くが、明細は常時展開せず、必要な時だけ開く。<br>- 対象文脈はDetail上部で横幅いっぱいを使い、横スクロール前提のContext Ref表を読みやすくする。<br><br>## 確認結果<br>- JSON parse：OK<br>- JS `node --check`：OK<br>- 対象文脈初期折りたたみ：OK<br>- 対象文脈横幅いっぱい表示CSS：OK<br>- 主文脈/対象文脈コンパクトCSS：OK<br>- 更新済みIncident JSONのZIP内収録：OK<br>- runtime生成物除外：OK<br> |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0077_001 | 2026-06-28 | 対象文脈はDetail上部に表示し、変更履歴や会話履歴より前に置く。 | 対象文脈はその明細を扱う前提であり、作業本文に入る前に確認する入口だから。 |
| dec_0077_002 | 2026-06-28 | Gridでは対象文脈の中身を出しすぎず、件数要約を基本にする。 | 文脈明細を一覧に展開するとGridの主目的が濁るため。 |
| dec_0077_v01553_001 | 2026-06-28 | 対象文脈はDetail上部パネルを正本表示とし、通常childArea末尾のobjectArray表示から除外する。 | 対象文脈は対象を扱う前の入口であり、本文や変更履歴の後ろに埋もれると意味が弱くなるため。 |
| dec_0077_v01553_002 | 2026-06-28 | Gridではcontext_refs[]の生JSONではなく件数要約を表示する。 | 一覧では対象文脈の有無と件数が分かればよく、JSON全文を表示すると読みにくくなるため。 |
| dec_0077_v015531_001 | 2026-06-28 | 対象文脈Detailパネルは通常折りたたみ、必要時にボタンで展開する。 | 対象文脈は明細の入口だが、常時展開するとDetail本文の視認性を下げるため。 |
| dec_0077_v015531_002 | 2026-06-28 | 対象文脈パネルはDetail Form内で横幅いっぱいを使う。 | Context Ref表は対象パス・目的など横に長い情報を持つため、左カラムに閉じ込めると読みにくいため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0077_001 | 2026-06-28 | incident_added | context_refs[]が通常データ行一覧として見える可能性があった。 | 対象文脈としてDetail上部に表示・編集する後続インシデントを追加。 | 対象文脈を個別対象の入口として扱い、本文や履歴に埋もれさせないため。 |
| chg_0077_v01553_001 | 2026-06-28 | target_context_detail_panel | context_refs[]は通常objectArrayとしてchildAreaに表示され、GridではJSON文字列として見えやすかった。 | context_refs[]を対象文脈としてDetail上部パネルに表示し、Gridでは件数要約を表示する。 | 対象文脈を個別対象の入口として扱うため。 |
| chg_0077_v015531_001 | 2026-06-28 | target_context_compact_layout | 対象文脈Detailパネルは初期展開され、Detail Formの左カラム相当の幅で表示されていた。 | 対象文脈Detailパネルを初期折りたたみにし、展開時はDetail Formの横幅いっぱいで表示する。 | 対象文脈を明細の入口として見せつつ、通常時のDetail画面をコンパクトに保つため。 |
| chg_0077_v015531_002 | 2026-06-28 | context_panel_compact_spacing | 主文脈・対象文脈パネルのpadding/marginが大きく、縦方向の占有が大きかった。 | 主文脈・対象文脈パネル、バッジ、テーブル、入力欄、フッターの余白を縮小した。 | 文脈入口として常時見える要約部分を軽くし、画面密度を上げるため。 |

### v0.16.1-studio-context-engineer-wannabe-mission-draft: Studio Context Engineer Wannabe / Mission定義ドラフト
- 作業ID: studio_work_0078
- 種別: data_design
- 分類: mission_context_design
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み

#### 対象ファイル

data/json/00_rules/studio_context_engineer_wannabe_foundation_rules_data_v0_1_draft.json
data/json/02_mission/studio_context_engineer_wannabe_mission_def_data_v0_1_draft.json
data/json/02_mission/studio_context_engineer_wannabe_mission_result_summary_data_v0_1_draft.json
data/json/01_main/studio_work_incident_data_v0_76_studio_context_engineer_wannabe_mission_draft_done.json
future: defs/mission/studio_context_engineer_wannabe_mission_view_def_v0_1_draft.json
future: defs/mission/studio_context_engineer_wannabe_mission_result_summary_view_def_v0_1_draft.json

#### 目的

Studio Context Engineer Wannabe — 文脈設計者になりたいStudioくん構想の初期ドラフトとして、AIへ複数StepのMissionを依頼するためのMission定義JSONと、AIから作業完了時に受け取るMission実行結果サマリーJSONを作成する。

#### 背景

当初はJOB制御JSONとして相談を始めたが、JOB Controlという名前はJP1的・業務システム的でStudioくんの物語性に合わない。会話の中で Studio Agent Wannabe — AIエージェントになりたいStudioくん が生まれ、さらに上位概念として Studio Context Engineer Wannabe — 文脈設計者になりたいStudioくん が採用された。Wannabeは『まだできてない』を弱点にせず、物語の入口に変える命名であり、高目標設置型を名前に埋め込む技法でもある。今回やることは大きな看板に対する小さな初手として、Mission定義JSONとMission実行結果サマリーJSONのドラフト作成に限定する。

#### 対象範囲

Mission定義JSONのMVPスキーマを作成する。候補項目は mission_id / title / incident_ref / context_refs / mode / jobs / steps / depends_on / inputs / outputs / success_conditions / on_success / on_failure とする。Mission実行結果サマリーJSONのMVPスキーマを作成する。候補項目は mission_result_summary_id / mission_id / status / result_summary / step_results / output_refs / review_points / next_action とする。初期は直列方式とし、前Step成功時に次Stepへ進む単純な構造を基本にする。ただし将来の並列化・DAG化を見据え、depends_onは配列として設計する。ユーザー向けの表札はMission / Mission実行結果サマリーとし、内部構造ではjob / stepなどの実務キー名を許容する。

#### 対象外

完全なAIエージェント、自動実行エンジン、バックグラウンド監視、途中状態のリアルタイム制御、スケジューラ、外部AI常駐、無承認のコード変更、並列write job実行、UI組み込み、Mission ViewDefの本格実装は対象外とする。今回は、AIに渡すMission定義と、AIから最後に受け取るMission実行結果サマリーのデータ構造ドラフトを作る段階とする。

#### 固定名方針

mission_id / mission_result_summary_id / step_id / depends_on / inputs / outputs / success_conditions などはMission系Dataの標準フィールド候補として扱う。ただしRuntimeが任意Dataの特定フィールド名に依存する実装は避ける。job / step などの実務的な内部キーは、Studio Context Engineer Wannabeという外側の概念名の配下で、Mission構造を表現するために使用可能とする。

#### module化方針

type="module" 化は今回の主目的ではない。まずはData JSONドラフト・サンプル・インシデント記録として扱い、既存の従来script方式や既存Studio運用と矛盾しない形で育てる。

#### リスク

名前が強くなりすぎることで、実行エンジン・自動監視・本物のAIエージェント化まで一気に作りたくなるスコープ肥大リスクがある。Wannabeは未完成・試作・成長途中を明示する安全装置として扱う。Mission実行結果サマリーに詳細履歴を詰め込みすぎると、個々の成果物に残す履歴との責務が混ざるため、結果の大筋と成果物参照に留める。

#### 確認観点

Mission定義JSONが、複数Stepの直列依頼、入力、出力、成功条件、depends_on、on_success/on_failureを表現できること。Mission実行結果サマリーJSONが、Mission全体の結果、各Stepの要約、成果物参照、レビュー観点、次アクションを表現できること。Mission実行結果サマリーが途中監視ではなく完了時の結果報告として読めること。内部にjob/stepが出ても、ユーザー向け概念がStudio Context Engineer Wannabe / Missionとして成立すること。

#### 作業会話サマリ


##### 依頼 / 方針

簡単にJOB制御JSONを作りたい。最初は前のJOBSTEPが正常終了した時に次へ進む単純な直列方式でよい。ただし並列化は視野に入れたい。ステップ毎にインプットとアウトプットを定義し、依頼内容はインシデントに紐づけたい。その後、JOB Controlという名称はJP1風で面白くないため、FRB版のミニチュアAIエージェント感が伝わる名前を練りたい。最終的に Studio Context Engineer Wannabe — 文脈設計者になりたいStudioくん を大きな看板として採用し、インシデント登録したい。

##### AI整理

1インシデントとして登録する方針が妥当。今回は実行エンジンではなく、Studio Context Engineer Wannabe構想の初期ドラフトとして、Mission定義JSONとMission実行結果サマリーJSONの2本を作る作業に絞る。JobFlow本体より上位の文脈設計者Wannabeとして、入力・出力・成功条件・結果サマリー・成果物参照を設計する。

##### 追加コメント

今回の作業依頼: incident_file=data/json/01_main/studio_work_incident_data_v0_75_studio_context_engineer_wannabe_mission_draft_added.json、phase=v0.16.1-studio-context-engineer-wannabe-mission-draft。mdはStudioくんから作るため不要。Foundation Rules rawを参照し、foundation_rule_019『GitHub基準ソースとZIP返却契約』を前提に、Studio Context Engineer Wannabe憲法的なData JSON、Mission定義フォーマット、Mission実行結果サマリーフォーマットを作成する。

##### AI追加回答

v0.16.1-studio-context-engineer-wannabe-mission-draft 対応完了。Markdownは作成せず、Data JSON原本として 1) Studio Context Engineer Wannabe Foundation Rules v0.1 draft、2) Mission Definition Format v0.1 draft、3) Mission Result Summary Format v0.1 draft を作成。あわせて本インシデントを完了扱いに更新し、実更新ファイルをactual_updated_filesへテキスト記録した。JSON parse確認済み。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0078_001 | 2026-06-28 | user | Mission構想の入口相談 | 簡単にJOB制御JSONを作りたい。最初は前のJOBSTEPが正常終了した時に次へ進む単純な直列方式でよい。ただし並列化は視野に入れたい。ステップ毎にインプットとアウトプットを定義し、依頼内容はインシデントに紐づけたい。 |
| disc_0078_002 | 2026-06-28 | assistant | JobDef / JobRun整理 | JobDefは作業手順書、JobRunは作業実績ログとして整理。ただしユーザーが結果という言葉がないと分かりにくいと指摘し、JobRunはJOB実行結果サマリーという理解へ修正。 |
| disc_0078_003 | 2026-06-28 | user | 結果サマリーの位置づけ | JOB実行結果サマリーは、個々の作業詳細ログではなく、JOB依頼したものが大筋でどういう結果だったかをぱっと分かるようにするものと整理。現状では途中で見られないため、最後に結果として受け取るもの。 |
| disc_0078_004 | 2026-06-28 | user | 名称違和感 | JOBコントロール的なキーワードはJP1みたいで面白くない。FRB版のミニチュアAIエージェント感が伝わるワードがよい。 |
| disc_0078_005 | 2026-06-28 | assistant | Studio Agent Wannabe発見 | AIエージェントもどきの英語候補として Wannabe AI Agent を提案。そこから Studio Agent Wannabe — AIエージェントになりたいStudioくん が生まれた。 |
| disc_0078_006 | 2026-06-28 | user | Studio Context Engineer Wannabe採用 | Studio Context Engineer Wannabe — 文脈設計者になりたいStudioくん が刺さった。Studio Agent Wannabeを食う上位概念として、文脈設計者になりたいStudioくんを採用する流れになった。 |
| disc_0078_007 | 2026-06-28 | assistant | Wannabe命名の意味 | Wannabeは『まだできてない』を弱点にせず、物語の入口に変える。高すぎる目標を未完成なまま今日の一歩に接続する命名技法として整理。 |
| disc_0078_008 | 2026-06-28 | user | 高目標設置型との接続 | 思考拡張の設計理論にあるパターン6：高目標設置型と接続。高い目標を置くことで、人間とAIの探索行動を起動する。Wannabeはそのネーミング版として見えてきた。 |
| disc_0078_009 | 2026-06-28 | user | インシデント登録依頼 | 小さい看板を大きく掲げる。Studio Context Engineer Wannabe — 文脈設計者になりたいStudioくんのインシデント登録を依頼。更新後JSON返却を希望。 |
| disc_0078_010 | 2026-06-28 | user | v0.16.1作業依頼 | 本日のメインイベントとして、Studio Context Engineer Wannabe憲法的なData JSON、Mission定義JSONフォーマット、Mission実行結果サマリーJSONフォーマットの作成を依頼。MarkdownはStudioくんから作るため不要。 |
| disc_0078_011 | 2026-06-28 | assistant | v0.16.1作業結果 | Data JSON原本として、Studio Context Engineer Wannabe Foundation Rules、Mission Definition Format、Mission Result Summary Formatを作成。更新済みインシデントJSONとZIPを返却する。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0078_001 | 2026-06-28 | 概念名は Studio Context Engineer Wannabe — 文脈設計者になりたいStudioくん とする。 | 単なるJOB制御ではなく、Studioくんが文脈設計者へ向かう成長物語として扱うため。 |
| dec_0078_002 | 2026-06-28 | ユーザー向けの表札は Mission / Mission実行結果サマリー とする。 | JobControlやJobRunだけでは業務システム臭が強く、結果サマリーの意味も初見では伝わりにくいため。 |
| dec_0078_003 | 2026-06-28 | 内部構造では job / step / depends_on などの実務キー名を許容する。 | 外側の概念名がStudioくんの物語性を担保するため、内部は実務的で分かりやすいキー名を使ってよい。表札は物語、内部は実務と分離する。 |
| dec_0078_004 | 2026-06-28 | Mission実行結果サマリーは途中監視用ではなく、作業完了時にAIから受け取る結果報告とする。 | 現状のチャット依頼ではAIの内部途中状態は外から見られないため、まずは結果受領時の説明書・索引として定義するのが現実的なため。 |
| dec_0078_005 | 2026-06-28 | 初期MVPは直列方式とし、depends_on配列だけ将来の並列化を見据えて採用する。 | 最初から並列制御や排他制御に踏み込むと重くなるが、depends_on配列なら直列にも将来のDAGにも自然に拡張できるため。 |
| dec_0078_006 | 2026-06-28 | Wannabeは未完成を明示するスコープ制御ワードとして扱う。 | 『文脈設計者になりたい』という高目標を掲げつつ、今回はMission定義JSONと結果サマリーJSONの小さな初手に留めるため。 |
| dec_0078_007 | 2026-06-28 | Mission定義とMission実行結果サマリーは別ファイルに分ける。 | AIに渡すものとAIから受け取るものを混ぜると、依頼構造と結果報告の責務が曖昧になるため。 |
| dec_0078_008 | 2026-06-28 | Markdownは作成せず、Data JSON原本だけを作成する。 | MarkdownはStudioくんからExportする表示用Viewであり、今回の作業依頼で明示的に不要と指定されたため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0078_001 | 2026-06-28 | incident_added | studio_work_incident_data_v0_74_context_model_cleanup_incidents_added.json / items_count=77 | studio_work_incident_data_v0_75_studio_context_engineer_wannabe_mission_draft_added.json / items_count=78 | Studio Context Engineer Wannabe — 文脈設計者になりたいStudioくん構想の初期ドラフトとして、Mission定義JSONとMission実行結果サマリーJSON作成をインシデント管理へ登録するため。 |
| chg_0078_002 | 2026-06-28 | studio_context_engineer_wannabe_foundation_added | Studio Context Engineer Wannabe構想はインシデントとして登録済みだが、憲法的なData JSON原本は未作成だった。 | studio_context_engineer_wannabe_foundation_rules_data_v0_1_draft.json を作成し、Wannabe、Mission、Step、success_conditions、Result Summary、Data JSON原本などの基本原則を15ルールとして定義した。 | Mission定義フォーマットの前提となる判断軸を構造化するため。 |
| chg_0078_003 | 2026-06-28 | mission_format_added | Mission定義JSONとMission実行結果サマリーJSONのフォーマットは会話上の案に留まっていた。 | Mission定義フォーマットとMission実行結果サマリーフォーマットをそれぞれData JSONとして作成した。 | AIに渡す文脈パッケージと、AIから受け取る完了時結果サマリーを分離して扱うため。 |
| chg_0078_004 | 2026-06-28 | incident_done_update | studio_work_0078 は未着手で、actual_updated_filesは初期登録JSONのみだった。 | studio_work_0078 を完了・確認済みに更新し、今回の実更新ファイル4件をactual_updated_filesへテキスト記録した。 | Foundation RulesのAI作業ファイル記録方針に従い、未来の人間とAIが成果物を追えるようにするため。 |

### v0.16.2-detail-subgrid-table-edit-core-mvp: Studio Table Edit Core / Detailサブグリッド編集MVP
- 作業ID: studio_work_0079
- 種別: feature
- 分類: table_edit_core
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: wwwroot/js/runtime/detail_save.js, wwwroot/js/renderers/field_controls.js, wwwroot/js/renderers/grid_detail.js, wwwroot/styles.css, future candidate: wwwroot/js/runtime/detail_subgrid_edit.js, future candidate: wwwroot/js/core/table_edit_core.js, mdViewer.html refactoring candidate

#### 目的

Detail画面内の objectArray / stringArray サブグリッドを汎用的に編集できるStudio標準テーブル編集MVPを作る。Mission定義JSONの steps.outputs / success_conditions / inputs / depends_on などを、Studio上で直接育てられる状態にする。

#### 背景

Studio Context Engineer Wannabe のMission定義JSONを眺めた結果、Mission Steps配下の outputs / success_conditions / inputs / depends_on をグリッド表示するだけでは足りず、セル編集・行追加・行削除が必要になった。既存の対象文脈パネルは context_refs 専用編集として先行実装されているが、今回必要なのは field.type === objectArray / stringArray に基づく汎用サブグリッド編集である。また、Markdown Editorではテーブル編集体験が育ち始めているため、将来的には操作体系を共通化し、Studio Table Edit Coreとして抽出する。

#### 対象範囲

MVPでは、Detail内の objectArray / stringArray サブグリッドを対象に、セル編集、行追加、行削除、変更中フラグ、反映(F12)時の親JSON同期を行う。stringArrayは value 列として扱い、objectArrayは先頭行またはViewDef定義から列を生成する。Runtimeは outputs / success_conditions などの固定フィールド名ではなく、ViewDefの field.type と field定義に基づいて汎用制御する。Markdown Editor由来の +上 / +下 / 削除 / 反映 の操作感に寄せるが、初期実装はDetailサブグリッド側に閉じてもよい。文字列セルは将来的なMarkdown表示・Markdown編集に対応できる前提で設計し、保存値はMarkdown原文を保持する。

#### 対象外

外部DataGridライブラリ導入、Excel風の完全セル操作、コピー&ペースト大量編集、ドラッグ並び替え、多段ネスト編集、objectArray読み物表示モード、子行専用ダイアログ、Markdownセルの本格プレビュー、Markdown Editor側の即時リファクタリングは今回のMVP対象外とする。ただし、将来のStudio Table Edit Core抽出とMarkdown Editorへの逆輸入を前提に、重複実装を負債ではなく試作として扱う。

#### 固定名方針

Runtimeが context_refs / outputs / success_conditions / inputs / depends_on などの特定フィールド名を決め打ちしない。編集対象はViewDefの field.type === objectArray / stringArray と、必要に応じて edit.subGrid / itemFields / columns の宣言から判断する。フィールド名ごとの専用UIが必要な場合は、汎用編集コアの上にAdapterとして分離する。

#### module化方針

type="module" 化は今回の主目的ではない。既存の従来script方式を維持し、必要であれば detail_subgrid_edit.js などのscript追加で段階的に実装する。将来的な TableEditCore 抽出時に責務分離を検討する。

#### リスク

配列編集の反映処理を誤ると親JSONのobjectArray/stringArrayを破壊する。contenteditableやtextarea編集でHTMLがJSONへ混入するリスクがある。既存の対象文脈専用パネルやMarkdown Editorのテーブル編集と似た機能が一時的に重複する。最初から共通化しすぎると実装が肥大化し、逆に専用実装に寄せすぎると将来のTable Edit Core抽出が難しくなる。

#### 確認観点

Mission定義JSONの steps[].depends_on / inputs / outputs / success_conditions をDetailサブグリッド上で編集できること。stringArrayのvalue編集・行追加・削除が親JSONへ反映されること。objectArrayの各列編集・行追加・削除が親JSONへ反映されること。F12反映→上書き保存→再読込で配列構造が壊れないこと。HTMLがJSONへ混入しないこと。既存context_refs専用編集、Markdownプレビュー、通常Detail編集が壊れないこと。

#### 作業会話サマリ


##### 依頼 / 方針

Mission定義JSONを眺める中で、本格的にグリッドを編集したいタイミングになってきた。外部グリッドライブラリではなく、Markdown Editorで育ったテーブル編集体験を参考にしつつ、Detail内の判断ログ・会話履歴・Mission Steps配下のサブグリッドを育てたい。最初は重複してもよいが、将来的にはStudio Table Edit Coreとして抽出し、Markdown Editor側へ戻すリファクタリングができるとよい。各セル編集を基本とし、文字列セルは将来的にMarkdown書式へ対応できる前提で計画に入れてほしい。ステップが多くならないように配慮しながらインシデント登録を依頼。

##### AI整理

外部グリッドライブラリに寄せず、Studio標準の汎用テーブル編集コアを育てる方針とする。初手はDetail内 objectArray / stringArray サブグリッド編集MVPに絞り、セル編集・行追加・行削除・F12反映同期を実装候補とする。Markdown Editorで育った +上 / +下 / 削除 / 反映 の操作感は参考にしつつ、最初から共通化しすぎず、後続で Studio Table Edit Core へ抽出する。文字列セルはMarkdown原文を保存値として保持し、将来的なMarkdown表示・編集に対応できる設計原則を残す。

##### 追加コメント

チャレンジインシデント対応として、v0.16.2-detail-subgrid-table-edit-core-mvp の実装を依頼。Foundation Rule 19に従い、更新済みインシデントJSONをZIP内 data/json/01_main/ に収録する。

##### AI追加回答

v0.16.2-detail-subgrid-table-edit-core-mvp 対応完了。外部DataGridライブラリは導入せず、Detail内 objectArray / stringArray を編集する自前の detail_subgrid_edit.js を追加。既存 renderChildArea は createDetailSubGridCard へ委譲し、F12/反映時に applyDetailSubGridEdits で親JSONへ同期する。stringArrayは value 列、objectArrayは既存keyまたはViewDefの subGrid columns / itemFields から列生成する。行追加・行削除・セル編集・未反映バッジに対応。文字列セルはMarkdown原文保持前提の設計メモを残した。JS構文確認とJSON parse確認はOK。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0079_001 | 2026-06-28 | user | Detailサブグリッド編集相談 | Mission定義JSONのDetail内サブグリッドを見て、本格的にグリッドを編集したいタイミングになってきたと相談。 |
| disc_0079_002 | 2026-06-28 | assistant | 実装方針整理 | 外部Grid標準機能ではなく、HTML table + input/select/textarea によるStudio標準グリッド編集MVPとして育てる方針を提案。 |
| disc_0079_003 | 2026-06-28 | user | Markdown Editorとの関係整理 | Markdown Editorで育ったテーブル編集体験を、JSON側の判断ログ・会話履歴・objectArray編集へ活かし、最終的には共通コアとしてMarkdown側へ戻すリファクタリングができるとよいと整理。 |
| disc_0079_004 | 2026-06-28 | user | Markdown文字列セル方針 | 各セル編集を基本とし、文字列セルはMarkdown書式に対応することを計画に入れてほしい。最初から実装しなくてよいが、設計原則として扱いたい。 |
| disc_0079_005 | 2026-06-28 | assistant | インシデント登録方針 | Detailサブグリッド編集MVPを小さな初手として登録し、Markdown文字列セル対応とStudio Table Edit Core抽出は将来拡張ポイントとして同じインシデント内に残す方針で整理。 |
| disc_0079_006 | 2026-06-28 | user | v0.16.2作業依頼 | チャレンジインシデント対応として、v0.16.2-detail-subgrid-table-edit-core-mvp の実装を依頼。うまく育てれるかなぁ～？よろしく！！ |
| disc_0079_007 | 2026-06-28 | assistant | v0.16.2対応結果 | AI回答<br><br>## 今回の更新<br><br>- `wwwroot/js/runtime/detail_subgrid_edit.js`<br>- `wwwroot/js/runtime/detail_save.js`<br>- `wwwroot/js/renderers/grid_detail.js`<br>- `wwwroot/index.html`<br>- `wwwroot/styles.css`<br>- `wwwroot/js/runtime/DETAIL_SUBGRID_TABLE_EDIT_CORE_NOTES_v0_16_2.md`<br>- `data/json/01_main/studio_work_incident_data_v0_77_detail_subgrid_table_edit_core_mvp_added.json`<br><br>## やったこと<br><br>Detail内の `objectArray` / `stringArray` サブグリッドを、セル編集・行追加・行削除できるMVPへ変更しました。`stringArray` は `value` 列として扱い、`objectArray` は既存行のkeyまたはViewDefの `edit.subGrid.columns` / `itemFields` から列を生成します。<br><br>## 方針<br><br>外部DataGridは導入せず、Studio標準の自前HTML table編集として育てる方針です。`outputs` / `success_conditions` / `inputs` / `depends_on` のような固定フィールド名には依存せず、ViewDefの `field.type` を基準にしています。文字列セルは将来Markdownを宿せる前提で、保存値は原文を保持する方針を実装メモへ残しました。<br><br>## 確認結果<br><br>- JSON parse：OK<br>- JS構文確認：OK<br>- runtime生成物除外：OK<br>- 更新済みIncident JSONのZIP内収録：OK |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0079_001 | 2026-06-28 | 外部DataGridライブラリは導入せず、Studio標準テーブル編集MVPとして育てる。 | 現状のメイングリッド・サブグリッドは自前HTML table描画であり、外部ライブラリ標準機能に乗るより、Data JSON / ViewDef / F12反映契約に合わせて育てる方が安全なため。 |
| dec_0079_002 | 2026-06-28 | 初手はDetail内 objectArray / stringArray サブグリッド編集に限定する。 | Mission定義JSONで実際に困っている編集対象が steps 配下の配列であり、ここを編集できれば実用価値が大きい一方、メイングリッド全体編集やMarkdown Editor共通化まで同時に行うと肥大化するため。 |
| dec_0079_003 | 2026-06-28 | Runtimeは特定フィールド名ではなくViewDefのtype宣言で編集対象を判断する。 | outputs / success_conditions / context_refs などの名前ごとに専用実装するとStudioくんが特定Data構造に太るため。 |
| dec_0079_004 | 2026-06-28 | 文字列セルは将来的にMarkdownを宿せる前提で扱う。 | 判断ログ・会話履歴・依頼方針・メモなどの文字列セルは、単なる値ではなく文脈の入口であり、保存値はMarkdown原文、表示はView側でMarkdownレンダリングという分離が必要になるため。 |
| dec_0079_005 | 2026-06-28 | Markdown Editorとの重複実装は初期段階では許容し、後続でStudio Table Edit Coreへ抽出する。 | 最初から完全共通化を狙うと実装が重くなるため、まずJSON側で実用MVPを育て、共通操作が見えた段階でTable Edit Coreとして抽出する方が安全なため。 |
| dec_0079_006 | 2026-06-28 | Detailサブグリッド編集MVPは detail_subgrid_edit.js として分離する。 | 既存 detail_save.js に編集ロジックを肥大化させず、将来 Studio Table Edit Core へ抽出しやすくするため。 |
| dec_0079_007 | 2026-06-28 | 配列編集は画面上ドラフトをF12/反映時に親JSONへ同期する。 | Studio既存の反映契約を維持し、編集途中の値が即座に正本JSONへ入り続ける不安を避けるため。 |
| dec_0079_008 | 2026-06-28 | MVPではMarkdownセルの本格プレビューは実装せず、Markdown原文保持前提を設計メモに残す。 | 初手のスコープをセル編集・行追加・行削除に絞りつつ、将来の読み物表示・Markdown Editor共通化へ接続するため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0079_001 | 2026-06-28 | incident_added | studio_work_incident_data_v0_76_studio_context_engineer_wannabe_mission_draft_done.json / items_count=78 | studio_work_incident_data_v0_77_detail_subgrid_table_edit_core_mvp_added.json / items_count=79 | Mission定義JSONをStudio上で育てるため、Detail内サブグリッド編集MVPと将来のStudio Table Edit Core抽出方針を作業項目として登録するため。 |
| chg_0079_002 | 2026-06-28 | detail_subgrid_edit_core_added | Detail内 objectArray / stringArray は表示専用のtableで、セル編集・行追加・行削除はできなかった。 | detail_subgrid_edit.js を追加し、objectArray / stringArray を編集可能なサブグリッドとして描画する。 | Mission定義JSONの steps 配下の depends_on / inputs / outputs / success_conditions をStudio上で育てられるようにするため。 |
| chg_0079_003 | 2026-06-28 | detail_apply_sync | applyDetailInputsToRow は objectArray / stringArray を保存破壊防止のため通常入力欄から除外していた。 | 通常入力欄除外は維持しつつ、applyDetailSubGridEdits により専用サブグリッドDOMから配列値を回収して親JSONへ反映する。 | 件数文字列で配列を壊さず、編集用サブグリッドだけを正本配列の更新入口にするため。 |
| chg_0079_004 | 2026-06-28 | ui_css_update | child-table は表示専用で、長文セルや編集状態の視認性が弱かった。 | サブグリッド用のセル入力、行操作ボタン、未反映バッジ、長文textarea、横スクロール時の操作列固定に対応するCSSを追加。 | Mission Steps配下の長文・配列セルを、壊さず編集できる体験に寄せるため。 |

### v0.16.3-incident-contextdef-open-work-draft: Incident ContextDef / 未完了作業の文脈素案投入
- 作業ID: studio_work_0080
- 優先度: high
- 状態: 完了
- 確認状態: 確認済み
- 対象ファイル: data/json/01_main/studio_work_incident_data_*.json, defs/rules/studio_work_incident_view_def_*.json, 必要に応じて frb_view_def_schema_v0_9.json / context_refs関連サンプル

#### 目的

インシデント管理DataにContextDef項目を追加し、未完了の作業項目だけを対象に、AIが作業前に読むべき文脈素案を入れられる状態にする。

#### 背景

Studioくんでは主文脈・対象文脈・context_refsの入口が育ってきたが、インシデント管理Dataそのものには、未完了作業ごとに『AIが作業前に何を読むべきか』をまとめるContextDefがまだない。未完了作業が増えるほど、AIは対象インシデントだけでなく、関連Rules・Foundation・過去判断・注意点を見落としやすくなる。まず未完了作業に限定して文脈素案を入れることで、作業依頼時の文脈パッケージ化へ近づける。

#### 対象範囲

work_itemsの各明細に context_def または context_def_draft 相当の項目を追加する。初期対象は status が未着手など未完了の作業項目のみとし、完了済み作業への一括追記は行わない。文脈素案には、作業前に読む目的、参照すべき関連インシデント、関連Rules、関連成果物、注意すべき制約、想定される読みタイミングを含める。まずはAIが作った素案として扱い、人間が後で編集・承認できる粒度に留める。

#### 対象外

完了済み作業へのContextDef一括投入、外部ファイルの自動読込、LLMへの自動投入、MissionDefとの完全統合、ContextDefスキーマの完全確定、全ViewDefへの本格UI実装、多段ネストContextの実行制御は対象外とする。まずはインシデント管理Data上の文脈素案フィールド追加と未完了作業への初期投入に限定する。

#### 固定名方針

context_def / context_def_draft はインシデント管理Data内の文脈素案フィールドとして扱う。ただしRuntimeが特定Data専用の固定名として直接処理するのではなく、ViewDefで表示・編集対象として宣言する。将来、Studio標準ContextDefへ昇格する場合はFoundation RulesまたはContext Engineer Wannabe憲法で明記する。

#### module化方針

type="module" 化は行わない。今回の主対象はData JSONとViewDefの項目追加であり、必要なJS修正がある場合も既存script方式を維持する。

#### リスク

未完了作業すべてへ過剰な文脈を入れるとDataが重くなり、作業前に読むべき文脈が逆に読みにくくなる。ContextDefが増えると、主文脈・対象文脈・context_refsとの責務境界が曖昧になるリスクがある。まず素案として最小項目に留め、完了済み作業には retroactive に入れない。

#### 確認観点

未完了作業だけにContextDef素案が入ること。完了済み作業へ不要な追記をしないこと。Studioで読み込んだときに既存Grid/Detailが壊れないこと。ContextDefが通常の長文欄に埋もれず、対象作業の入口として見えること。F12反映・上書き保存後もcontext_def_draftが保持されること。

#### 作業会話サマリ


##### 依頼 / 方針

インシデントデータにContextDefの項目を追加して、未完了の作業についてだけでよいので、文脈素案を入れるインシデントにしてほしい。

##### AI整理

インシデント化方針として、まず v0.16.3-incident-contextdef-open-work-draft を登録する。作業の初手は、インシデント管理Dataにcontext_def/context_def_draft項目を追加し、status=未着手など未完了作業だけにAI作業前の文脈素案を入れること。完了済み作業への一括投入や自動読込実行は対象外とする。

##### 追加コメント

急ぎ対応として、インシデントデータにContextDef項目を追加し、未完了の作業だけに文脈素案を入れる作業をインシデント登録したい。

studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json　は、更新して、
studio_work_incident_view_def_v0_5.json　としてください。

##### AI追加回答

v0.16.3対応完了。インシデント管理Dataの未完了作業25件へ context_def_status / context_def_updated_at / context_def_draft / context_refs を投入し、作業前に読む文脈素案を持てる状態にした。完了済み作業へのcontext_def_draft一括投入は行っていない。ViewDefは studio_work_incident_view_def_v0_5.json として更新し、ContextDef素案と対象文脈を表示・編集対象に追加した。

#### 会話履歴

| History ID | 日時 | 発言者 | 話題 | 内容 |
| --- | --- | --- | --- | --- |
| disc_0080_001 | 2026-06-28 | user | ContextDef項目追加相談 | インシデントデータにContextDefの項目を追加して、未完了の作業についてだけでいいので、文脈素案を入れるインシデントにしてほしい。 |
| disc_0080_002 | 2026-06-28 | assistant | インシデント登録方針 | 完了済み作業へ一括投入せず、未完了作業だけを対象にContextDef素案を入れる作業として登録する。初期は文脈素案であり、ContextDefスキーマ確定や自動読込実行は後続に分ける。 |
| disc_0080_003 | 2026-06-28 | user | v0.16.3作業依頼 | studio_work_incident_data_v0_78_incident_contextdef_open_work_draft_added.json を対象に、未完了作業へContextDef文脈素案を投入し、ViewDefを v0_5 へ更新する作業を依頼。 |
| disc_0080_004 | 2026-06-28 | assistant | v0.16.3作業結果 | baseline未着手25件にcontext_def_draftとcontext_refsを投入。ViewDef v0.5を作成し、Data rootのview_defを rules/studio_work_incident_view_def_v0_5.json へ更新。 |

#### 判断ログ

| Decision ID | 日時 | 判断 | 理由 |
| --- | --- | --- | --- |
| dec_0080_001 | 2026-06-28 | ContextDef投入対象は未完了作業に限定する。 | 完了済み作業へ retroactive に文脈を入れると作業履歴が重くなり、初期対応範囲も大きくなりすぎるため。 |
| dec_0080_002 | 2026-06-28 | 初期ContextDefは確定仕様ではなく文脈素案として扱う。 | ContextDefの最終スキーマを先に固めすぎると、主文脈・対象文脈・MissionDefとの関係整理が重くなるため。 |
| dec_0080_003 | 2026-06-28 | 自動読込・LLM投入・Mission連携は今回の対象外にする。 | まずはインシデント管理Data上で文脈素案を持てる状態を作ることを優先し、実行制御と混ぜないため。 |
| dec_0080_001 | 2026-06-28 | ContextDef初期投入は未完了作業25件に限定する。 | 完了済み作業へretroactiveに文脈素案を入れると、当時の作業文脈と後付け文脈が混ざるため。まず今後作業する入口だけを整える。 |
| dec_0080_002 | 2026-06-28 | context_def_draftはMarkdown文字列、context_refsは構造化配列として併用する。 | 人間が読みやすい文脈素案と、Studio上で編集しやすい対象文脈配列の両方を小さく始めるため。 |

#### 変更履歴

| History ID | 日時 | 変更種別 | 変更前 | 変更後 | 理由 |
| --- | --- | --- | --- | --- | --- |
| chg_0080_001 | 2026-06-28 | incident_added | インシデント管理Dataには、未完了作業ごとにAIが作業前に読むべき文脈素案を保持するContextDef項目がなかった。 | studio_work_0080 として、ContextDef項目追加と未完了作業への文脈素案投入インシデントを登録した。 | 未完了作業をAIに渡す前の文脈パッケージ化を進めるため。 |
| chg_0080_001 | 2026-06-28 | incident_contextdef_draft_added | 未完了作業には、作業前に読むべき文脈をまとめるContextDef項目がなかった。 | baseline未着手25件にcontext_def_status / context_def_updated_at / context_def_draft / context_refsを追加し、文脈素案と対象文脈の入口を持たせた。 | 未来のAIと人間が、作業に入る前の文脈を追体験できるようにするため。 |
| chg_0080_002 | 2026-06-28 | viewdef_v0_5_contextdef_fields | studio_work_incident_view_def_v0_4_readable_cards_confirm_status_markdown_preview.json が現行ViewDefだった。 | studio_work_incident_view_def_v0_5.json を追加し、ContextDef素案・文脈状態・対象文脈context_refsを表示対象にした。 | ContextDef項目をDataに追加するだけでなく、Studio上で眺めて育てられるようにするため。 |

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
作業ID	Phase	タイトル	種別	分類	優先度	状態	確認状態	文脈状態	対象ファイル	目的
studio_work_0007	v0.7-markdown-export-contract	Markdown出力契約 / JSON展開情報 / AI貼り付け用	specification	markdown_export	high	未着手	未確認	draft	wwwroot/js/markdown/*.js, mdViewer.html, FRB_VIEW_DEF_GENERATION_RULES_*.md, frb_view_def_schema_*.json	Markdown出力ボタンで何を出力できるべきかを、ViewDef生成ルール・Schema・Runtime仕様として整理する。
studio_work_0008	v0.7-filename-encoding-sanitize	Markdown出力ファイル名の文字化け対策	bugfix	file_io	high	未着手	未確認	draft	wwwroot/js/core/file_api.js, wwwroot/js/core/fileNameUtils.js or equivalent, wwwroot/js/markdown/*.js, mdViewer.html, backend save/load API if needed	Markdown出力やViewer連携で、Unicodeエスケープ/URLエンコード/HTMLエンティティ風の文字化けファイル名が大量発生する問題を解消する。
studio_work_0009	v0.7-viewdef-sample-fixtures	ViewDef代表サンプル / 健康診断セット整理	maintenance	fixtures	medium	未着手	未確認	draft	defs/studio/*, data/studio/*, sample fixtures README	今後の改修時に最低限確認する代表Data/ViewDefセットを整理し、回帰確認の基準を作る。
studio_work_0010	v0.7-fixed-name-audit	Runtime内固定フィールド名監査	architecture_audit	fixed_name	medium	未着手	未確認	draft	wwwroot/js/**/*.js, index.html, ViewDef schema/rules	Runtime内に残っている固定フィールド名・固定Action名・固定builder名を棚卸しし、骨格か脂肪かを分類する。
studio_work_0011	v0.7-standard-meta-fields	Studio標準メタフィールド定義	rules_review	standard_fields	medium	未着手	未確認	draft	CODING_CONSTRAINTS.md, FRB_VIEW_DEF_GENERATION_RULES_*.md, frb_view_def_schema_*.json	Runtime内Data固定名禁止の例外として認めるStudio標準メタフィールド候補を整理し、採用ルールを定義する。
studio_work_0015	v0.9-versioned-incident-management	Version / Revision / Phase 分離とVersion Detail連携	data_model	incident_versioning	high	未着手	未確認	draft	studio_work_incident_data_*.json, studio_work_incident_view_def_*.json, release_data.json, release_view_def_*.json, version_detail_data.json if created	Version / Revision / Phase の役割を分離し、IncidentがどのVersionで見つかり、どのVersionで対応され、どのVersion Detailに含まれたかを追跡できるようにする。
studio_work_0016	v0.9-rules-json-source-of-truth	ルール系Data JSON原本化 / Foundation Rules追加	data_design	rules_data	high	未着手	未確認	draft	wwwroot/data/rules/frb_foundation_rules_data_v0_1.json, wwwroot/data/rules/frb_viewdef_generation_rules_data_v0_1.json, wwwroot/defs/rules/rule_review_common_view_def_v0_1.json, wwwroot/exports/rules/*.md	Markdownをルール原本にせず、ルール・制約・レビュー対象はドメイン別Data JSONを原本として管理し、共通ViewDefでレビューできるようにする。
studio_work_0017	v0.9-rule-review-common-viewdef-polish	共通Rule Review ViewDefの汎用化仕上げ	improvement	viewdef_polish	low	未着手	未確認	draft	wwwroot/defs/rules/rule_review_common_view_def_v0_1.json, related rule review data json, markdown export templates	rule_review_common_view_def_v0_1.json を特定データ専用の匂いから切り離し、複数ドメインのルールレビューで安全に使える共通ViewDefへ整える。
studio_work_0018	v0.9-json-utf8-human-readable-save	Data JSONの日本語可読保存	bugfix_improvement	encoding	high	未着手	未確認	draft	JSON generation scripts, Program.cs save API, wwwroot/js/core/file_api.js, any export/save utilities	Data JSONを人間が直接読めるUTF-8日本語で保存し、\uXXXX だらけの人間拒否モードを避ける。
studio_work_0049	v0.14.19-rule-review-status-responsibility-issue	Rule Review承認/確認状態の単一正本化と責務整理	open_issue	rule_review_workflow	high	未着手	未確認	draft	data/json/00_rules/frb_*_data_v*.json（frb_view_def_schema_review_data_v0_1.json は必要時のみ別扱い）, data/json/00_rules/frb_test_evidence_rules_data_v0_1.json, data/json/00_rules/frb_coding_constraints_data_v0_3.json, data/json/00_rules/frb_foundation_rules_data_v0_1.json, defs/rules/rule_review_common_view_def_*.json, rules/studio_work_incident_view_def_*.json	Rule Review系データにおける review_status / verification_status / approval_decision の意味、単一正本、UI上の表示・操作責務、人間とAIの権限範囲を整理する。特に、AIがルール本文・章・要約・分類などを修正した場合に、その章またはルール行が未承認・未確認・未レビューへ戻るべきかを運用ルールとして定義する。
studio_work_0051	v0.14.21-human-ai-responsibility-rules	新ルール候補：Human / AI Responsibility Rules 人間・AI責務境界ルール	rules_review		high	未着手	未確認	draft	data/json/01_main/studio_work_incident_data_*.json, defs/rules/*review*.json, data/json/00_rules/*.json	人間が最終判断する項目、AIが更新してよい項目、AI更新後に未承認へ戻すべき状態項目を整理し、承認・確認・レビュー状態の責務境界を明確にする。
studio_work_0052	v0.14.22-definition-of-done-rules	新ルール候補：Definition of Done Rules 作業完了条件ルール	rules_review		high	未着手	未確認	draft	data/json/00_rules/*.json, data/json/01_main/studio_work_incident_data_*.json, tests/tools/*	AI作業における『完了』の条件を定義し、成果物・証跡・インシデント更新・返却安全性をそろえる。
studio_work_0053	v0.14.23-change-impact-risk-classification-rules	新ルール候補：Change Impact / Risk Classification Rules 変更影響・リスク分類ルール	rules_review		medium	未着手	未確認	draft	data/json/00_rules/*.json, data/json/01_main/studio_work_incident_data_*.json	変更内容を低・中・高・超高リスクに分類し、AI作業時の確認粒度・報告粒度・人間相談要否を切り替えられるようにする。
studio_work_0054	v0.14.24-traceability-rules	新ルール候補：Traceability Rules ルール・インシデント・証跡トレースルール	rules_review		high	未着手	未確認	draft	data/json/03_tests/**, data/json/00_rules/*.json, data/json/01_main/studio_work_incident_data_*.json, defs/relation/*.json	Rule / Incident / Expected / Actual / Diff / ViewDef / Release のつながりを辿れるようにするためのトレーサビリティ方針を整理する。
studio_work_0055	v0.14.25-test-runner-execution-rules	新ルール候補：Test Runner / Execution Rules 共通テストランナー実行ルール	rules_review		high	未着手	未確認	draft	tests/**/*.mjs, tests/**/*.spec.ts, data/json/03_tests/**, tests/tools/*	テストコードをケースごとに増やすのではなく、実行言語ごとの共通ランナーへ寄せ、Test Pattern / Expected JSONを増やす運用を整理する。
studio_work_0056	v0.14.26-migration-backward-compatibility-rules	新ルール候補：Migration / Backward Compatibility Rules 移行・互換・廃止ルール	rules_review		high	未着手	未確認	draft	data/json/**/*.json, defs/**/*.json, _archive/**, filename_updatelist.md	ファイル名変更・フォルダー移行・互換フィールド追加時に、旧名・旧パス・互換項目をどう扱うかを定義する。
studio_work_0057	v0.14.27-ai-work-context-package-rules	新ルール候補：AI Work Context Package Rules AI作業文脈パッケージルール	rules_review		medium	未着手	未確認	draft	data/json/01_main/00_do_incident_prompt_temple.md, data/json/00_rules/_json_creation_prompt.md, data/json/01_main/studio_work_incident_data_*.json	AIに作業依頼するときの最小文脈セット、優先順位、添付ZIPとraw URLの扱いをルール化する。
studio_work_0058	v0.14.28-git-release-branch-rules	新ルール候補：Git / Release / Branch Rules Git・リリース・ブランチ運用ルール	rules_review		medium	未着手	未確認	draft	README, release_data.json if created, data/json/01_main/studio_work_incident_data_*.json, GitHub運用メモ	AI返却ZIP、GitHub main、release tag、GitHub Pages公開物、_archiveの関係を整理し、正本と成果物の位置づけを明確にする。
studio_work_0059	v0.14.29-security-public-data-rules	新ルール候補：Security / Public Data Rules 公開データ・安全管理ルール	rules_review		high	未着手	未確認	draft	wwwroot/data/**, wwwroot/defs/**, data/json/**, docs/articles, README	GitHub Pagesや記事連携で公開してよいData/Defsと、ローカル限定・非公開にすべき情報の境界を整理する。
studio_work_0060	v0.14.30-error-incident-escalation-rules	新ルール候補：Error / Incident Escalation Rules エラー・違和感・再発防止ルール	rules_review		medium	未着手	未確認	draft	data/json/01_main/studio_work_incident_data_*.json, tests/**/*.spec.ts, tests/**/*.mjs, reports/*.md if created	AI作業中に発生したエラー、ユーザー環境のみの不具合、仕様未確定の違和感をどうインシデント化・エスカレーションするかを整理する。
studio_work_0070	v0.15.6-grid-column-resize-viewdef-save	グリッド列幅変更 / ViewDef明示保存	feature	grid_viewdef	medium	未着手	未確認	draft	wwwroot/js/renderers/grid_renderer.js, wwwroot/js/renderers/grid_detail.js, wwwroot/js/runtime/load_runtime.js, wwwroot/js/core/viewdef_resolver.js, wwwroot/js/core/file_api.js, wwwroot/styles.css, related ViewDef schema/rules if needed	グリッド表示中に列幅をドラッグ変更できるようにし、必要な場合のみ明示操作で現在のViewDefの fields[].grid.width へ反映できるようにする。
studio_work_0071	v0.15.7-objectarray-section-search	objectArray / 履歴セクションのまとまり検索対応	feature		high	未着手	未確認	draft	wwwroot/js/runtime/search_runtime.js, wwwroot/js/renderers/grid_renderer.js, wwwroot/js/renderers/grid_detail.js, wwwroot/js/core/viewdef_resolver.js, wwwroot/app.js, wwwroot/styles.css, relevant ViewDefs such as studio_work_incident_view_def_*.json, frb_view_def_schema_*.json / rules if needed	discussion_history / change_history / decision_log などの objectArray 形式の深い階層を、項目単位ではなく『会話履歴』『変更履歴』『判断ログ』『履歴全体』のようなセクション単位で検索できるようにする。
studio_work_0072	v0.15.8-gitdiff-result-viewer-launch	GitDiffRun結果JSONのDiffJsonViewer自動表示	feature	gitdiff_viewer	high	未着手	未確認	draft	Program.cs, wwwroot/js/actions/action_registry.js, wwwroot/js/actions/action_toolbar.js, wwwroot/js/core/file_api.js, wwwroot/DiffJsonViewer.html, wwwroot/js/renderers/diff_json_viewer*.js, wwwroot/styles.css, related GitDiffRun action/runtime files	StudioくんからGitDiffRunを起動した後、生成された差分JSONをwwwroot配下の一時公開フォルダーへ出力し、DiffJsonViewer.html?src=... で自動表示できるようにする。
studio_work_0073	v0.15.9-gitdiff-large-result-handling	GitDiffRun巨大差分JSONのViewer表示上限 / エラー表示	feature	gitdiff_large_data	medium	未着手	未確認	draft	Program.cs, wwwroot/js/actions/action_registry.js, wwwroot/js/core/file_api.js, wwwroot/DiffJsonViewer.html, wwwroot/js/renderers/diff_json_viewer*.js, wwwroot/styles.css, related GitDiffRun API/runtime files	wwwroot配下に生成された差分JSONがDiffJsonViewer.htmlで扱えないほど大きい場合に、無理に表示せず、安全にサイズ上限エラーとして扱えるようにする。
studio_work_0074	v0.16.0-proposal-driven-jobflow	AI提案駆動JobFlow / JobControl JSON構想	architecture		high	未着手	未確認	draft	data/json/01_main/studio_work_incident_data_*.json, future: data/json/02_job/job_control_data_v0_1.json, data/json/02_job/improvement_proposal_data_v0_1.json, data/json/02_job/job_approval_data_v0_1.json, data/json/02_job/job_run_result_data_v0_1.json, defs/job/job_control_view_def_v0_1.json, defs/job/improvement_proposal_view_def_v0_1.json	AI作業の開始点を、人間の明示依頼だけでなくAI改善提案JSONからも始められるようにする。Improvement Proposal JSON → 人間承認 → JobControl JSON → Job実行 → TestResult / GitDiff / AIテスト物語 / AI差分物語 / Incident更新 までを、AI協働可能なJobFlowとして定義する。
```

</details>

<details>
<summary>Grid JSON を表示</summary>

```json
{
  "view_def": "rules/studio_work_incident_view_def_v0_5.json",
  "data_file": "studio_work_incident_data_v0_79_incident_contextdef_open_work_draft_done.json",
  "section": "改修インシデント / 作業項目",
  "row_count": 25,
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
      "field": "verification_status",
      "caption": "確認状態",
      "type": "select"
    },
    {
      "field": "context_def_status",
      "caption": "文脈状態",
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
      "work_item_id": "studio_work_0007",
      "phase": "v0.7-markdown-export-contract",
      "title": "Markdown出力契約 / JSON展開情報 / AI貼り付け用",
      "incident_type": "specification",
      "category": "markdown_export",
      "priority": "high",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
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
      "verification_status": "未確認",
      "context_def_status": "draft",
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
      "verification_status": "未確認",
      "context_def_status": "draft",
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
      "verification_status": "未確認",
      "context_def_status": "draft",
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
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "CODING_CONSTRAINTS.md, FRB_VIEW_DEF_GENERATION_RULES_*.md, frb_view_def_schema_*.json",
      "objective": "Runtime内Data固定名禁止の例外として認めるStudio標準メタフィールド候補を整理し、採用ルールを定義する。"
    },
    {
      "work_item_id": "studio_work_0015",
      "phase": "v0.9-versioned-incident-management",
      "title": "Version / Revision / Phase 分離とVersion Detail連携",
      "incident_type": "data_model",
      "category": "incident_versioning",
      "priority": "high",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "studio_work_incident_data_*.json, studio_work_incident_view_def_*.json, release_data.json, release_view_def_*.json, version_detail_data.json if created",
      "objective": "Version / Revision / Phase の役割を分離し、IncidentがどのVersionで見つかり、どのVersionで対応され、どのVersion Detailに含まれたかを追跡できるようにする。"
    },
    {
      "work_item_id": "studio_work_0016",
      "phase": "v0.9-rules-json-source-of-truth",
      "title": "ルール系Data JSON原本化 / Foundation Rules追加",
      "incident_type": "data_design",
      "category": "rules_data",
      "priority": "high",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "wwwroot/data/rules/frb_foundation_rules_data_v0_1.json, wwwroot/data/rules/frb_viewdef_generation_rules_data_v0_1.json, wwwroot/defs/rules/rule_review_common_view_def_v0_1.json, wwwroot/exports/rules/*.md",
      "objective": "Markdownをルール原本にせず、ルール・制約・レビュー対象はドメイン別Data JSONを原本として管理し、共通ViewDefでレビューできるようにする。"
    },
    {
      "work_item_id": "studio_work_0017",
      "phase": "v0.9-rule-review-common-viewdef-polish",
      "title": "共通Rule Review ViewDefの汎用化仕上げ",
      "incident_type": "improvement",
      "category": "viewdef_polish",
      "priority": "low",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "wwwroot/defs/rules/rule_review_common_view_def_v0_1.json, related rule review data json, markdown export templates",
      "objective": "rule_review_common_view_def_v0_1.json を特定データ専用の匂いから切り離し、複数ドメインのルールレビューで安全に使える共通ViewDefへ整える。"
    },
    {
      "work_item_id": "studio_work_0018",
      "phase": "v0.9-json-utf8-human-readable-save",
      "title": "Data JSONの日本語可読保存",
      "incident_type": "bugfix_improvement",
      "category": "encoding",
      "priority": "high",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "JSON generation scripts, Program.cs save API, wwwroot/js/core/file_api.js, any export/save utilities",
      "objective": "Data JSONを人間が直接読めるUTF-8日本語で保存し、\\uXXXX だらけの人間拒否モードを避ける。"
    },
    {
      "work_item_id": "studio_work_0049",
      "phase": "v0.14.19-rule-review-status-responsibility-issue",
      "title": "Rule Review承認/確認状態の単一正本化と責務整理",
      "incident_type": "open_issue",
      "category": "rule_review_workflow",
      "priority": "high",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "data/json/00_rules/frb_*_data_v*.json（frb_view_def_schema_review_data_v0_1.json は必要時のみ別扱い）, data/json/00_rules/frb_test_evidence_rules_data_v0_1.json, data/json/00_rules/frb_coding_constraints_data_v0_3.json, data/json/00_rules/frb_foundation_rules_data_v0_1.json, defs/rules/rule_review_common_view_def_*.json, rules/studio_work_incident_view_def_*.json",
      "objective": "Rule Review系データにおける review_status / verification_status / approval_decision の意味、単一正本、UI上の表示・操作責務、人間とAIの権限範囲を整理する。特に、AIがルール本文・章・要約・分類などを修正した場合に、その章またはルール行が未承認・未確認・未レビューへ戻るべきかを運用ルールとして定義する。"
    },
    {
      "work_item_id": "studio_work_0051",
      "phase": "v0.14.21-human-ai-responsibility-rules",
      "title": "新ルール候補：Human / AI Responsibility Rules 人間・AI責務境界ルール",
      "incident_type": "rules_review",
      "category": "",
      "priority": "high",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "data/json/01_main/studio_work_incident_data_*.json, defs/rules/*review*.json, data/json/00_rules/*.json",
      "objective": "人間が最終判断する項目、AIが更新してよい項目、AI更新後に未承認へ戻すべき状態項目を整理し、承認・確認・レビュー状態の責務境界を明確にする。"
    },
    {
      "work_item_id": "studio_work_0052",
      "phase": "v0.14.22-definition-of-done-rules",
      "title": "新ルール候補：Definition of Done Rules 作業完了条件ルール",
      "incident_type": "rules_review",
      "category": "",
      "priority": "high",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "data/json/00_rules/*.json, data/json/01_main/studio_work_incident_data_*.json, tests/tools/*",
      "objective": "AI作業における『完了』の条件を定義し、成果物・証跡・インシデント更新・返却安全性をそろえる。"
    },
    {
      "work_item_id": "studio_work_0053",
      "phase": "v0.14.23-change-impact-risk-classification-rules",
      "title": "新ルール候補：Change Impact / Risk Classification Rules 変更影響・リスク分類ルール",
      "incident_type": "rules_review",
      "category": "",
      "priority": "medium",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "data/json/00_rules/*.json, data/json/01_main/studio_work_incident_data_*.json",
      "objective": "変更内容を低・中・高・超高リスクに分類し、AI作業時の確認粒度・報告粒度・人間相談要否を切り替えられるようにする。"
    },
    {
      "work_item_id": "studio_work_0054",
      "phase": "v0.14.24-traceability-rules",
      "title": "新ルール候補：Traceability Rules ルール・インシデント・証跡トレースルール",
      "incident_type": "rules_review",
      "category": "",
      "priority": "high",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "data/json/03_tests/**, data/json/00_rules/*.json, data/json/01_main/studio_work_incident_data_*.json, defs/relation/*.json",
      "objective": "Rule / Incident / Expected / Actual / Diff / ViewDef / Release のつながりを辿れるようにするためのトレーサビリティ方針を整理する。"
    },
    {
      "work_item_id": "studio_work_0055",
      "phase": "v0.14.25-test-runner-execution-rules",
      "title": "新ルール候補：Test Runner / Execution Rules 共通テストランナー実行ルール",
      "incident_type": "rules_review",
      "category": "",
      "priority": "high",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "tests/**/*.mjs, tests/**/*.spec.ts, data/json/03_tests/**, tests/tools/*",
      "objective": "テストコードをケースごとに増やすのではなく、実行言語ごとの共通ランナーへ寄せ、Test Pattern / Expected JSONを増やす運用を整理する。"
    },
    {
      "work_item_id": "studio_work_0056",
      "phase": "v0.14.26-migration-backward-compatibility-rules",
      "title": "新ルール候補：Migration / Backward Compatibility Rules 移行・互換・廃止ルール",
      "incident_type": "rules_review",
      "category": "",
      "priority": "high",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "data/json/**/*.json, defs/**/*.json, _archive/**, filename_updatelist.md",
      "objective": "ファイル名変更・フォルダー移行・互換フィールド追加時に、旧名・旧パス・互換項目をどう扱うかを定義する。"
    },
    {
      "work_item_id": "studio_work_0057",
      "phase": "v0.14.27-ai-work-context-package-rules",
      "title": "新ルール候補：AI Work Context Package Rules AI作業文脈パッケージルール",
      "incident_type": "rules_review",
      "category": "",
      "priority": "medium",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "data/json/01_main/00_do_incident_prompt_temple.md, data/json/00_rules/_json_creation_prompt.md, data/json/01_main/studio_work_incident_data_*.json",
      "objective": "AIに作業依頼するときの最小文脈セット、優先順位、添付ZIPとraw URLの扱いをルール化する。"
    },
    {
      "work_item_id": "studio_work_0058",
      "phase": "v0.14.28-git-release-branch-rules",
      "title": "新ルール候補：Git / Release / Branch Rules Git・リリース・ブランチ運用ルール",
      "incident_type": "rules_review",
      "category": "",
      "priority": "medium",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "README, release_data.json if created, data/json/01_main/studio_work_incident_data_*.json, GitHub運用メモ",
      "objective": "AI返却ZIP、GitHub main、release tag、GitHub Pages公開物、_archiveの関係を整理し、正本と成果物の位置づけを明確にする。"
    },
    {
      "work_item_id": "studio_work_0059",
      "phase": "v0.14.29-security-public-data-rules",
      "title": "新ルール候補：Security / Public Data Rules 公開データ・安全管理ルール",
      "incident_type": "rules_review",
      "category": "",
      "priority": "high",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "wwwroot/data/**, wwwroot/defs/**, data/json/**, docs/articles, README",
      "objective": "GitHub Pagesや記事連携で公開してよいData/Defsと、ローカル限定・非公開にすべき情報の境界を整理する。"
    },
    {
      "work_item_id": "studio_work_0060",
      "phase": "v0.14.30-error-incident-escalation-rules",
      "title": "新ルール候補：Error / Incident Escalation Rules エラー・違和感・再発防止ルール",
      "incident_type": "rules_review",
      "category": "",
      "priority": "medium",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "data/json/01_main/studio_work_incident_data_*.json, tests/**/*.spec.ts, tests/**/*.mjs, reports/*.md if created",
      "objective": "AI作業中に発生したエラー、ユーザー環境のみの不具合、仕様未確定の違和感をどうインシデント化・エスカレーションするかを整理する。"
    },
    {
      "work_item_id": "studio_work_0070",
      "phase": "v0.15.6-grid-column-resize-viewdef-save",
      "title": "グリッド列幅変更 / ViewDef明示保存",
      "incident_type": "feature",
      "category": "grid_viewdef",
      "priority": "medium",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "wwwroot/js/renderers/grid_renderer.js, wwwroot/js/renderers/grid_detail.js, wwwroot/js/runtime/load_runtime.js, wwwroot/js/core/viewdef_resolver.js, wwwroot/js/core/file_api.js, wwwroot/styles.css, related ViewDef schema/rules if needed",
      "objective": "グリッド表示中に列幅をドラッグ変更できるようにし、必要な場合のみ明示操作で現在のViewDefの fields[].grid.width へ反映できるようにする。"
    },
    {
      "work_item_id": "studio_work_0071",
      "phase": "v0.15.7-objectarray-section-search",
      "title": "objectArray / 履歴セクションのまとまり検索対応",
      "incident_type": "feature",
      "category": "",
      "priority": "high",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "wwwroot/js/runtime/search_runtime.js, wwwroot/js/renderers/grid_renderer.js, wwwroot/js/renderers/grid_detail.js, wwwroot/js/core/viewdef_resolver.js, wwwroot/app.js, wwwroot/styles.css, relevant ViewDefs such as studio_work_incident_view_def_*.json, frb_view_def_schema_*.json / rules if needed",
      "objective": "discussion_history / change_history / decision_log などの objectArray 形式の深い階層を、項目単位ではなく『会話履歴』『変更履歴』『判断ログ』『履歴全体』のようなセクション単位で検索できるようにする。"
    },
    {
      "work_item_id": "studio_work_0072",
      "phase": "v0.15.8-gitdiff-result-viewer-launch",
      "title": "GitDiffRun結果JSONのDiffJsonViewer自動表示",
      "incident_type": "feature",
      "category": "gitdiff_viewer",
      "priority": "high",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "Program.cs, wwwroot/js/actions/action_registry.js, wwwroot/js/actions/action_toolbar.js, wwwroot/js/core/file_api.js, wwwroot/DiffJsonViewer.html, wwwroot/js/renderers/diff_json_viewer*.js, wwwroot/styles.css, related GitDiffRun action/runtime files",
      "objective": "StudioくんからGitDiffRunを起動した後、生成された差分JSONをwwwroot配下の一時公開フォルダーへ出力し、DiffJsonViewer.html?src=... で自動表示できるようにする。"
    },
    {
      "work_item_id": "studio_work_0073",
      "phase": "v0.15.9-gitdiff-large-result-handling",
      "title": "GitDiffRun巨大差分JSONのViewer表示上限 / エラー表示",
      "incident_type": "feature",
      "category": "gitdiff_large_data",
      "priority": "medium",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "Program.cs, wwwroot/js/actions/action_registry.js, wwwroot/js/core/file_api.js, wwwroot/DiffJsonViewer.html, wwwroot/js/renderers/diff_json_viewer*.js, wwwroot/styles.css, related GitDiffRun API/runtime files",
      "objective": "wwwroot配下に生成された差分JSONがDiffJsonViewer.htmlで扱えないほど大きい場合に、無理に表示せず、安全にサイズ上限エラーとして扱えるようにする。"
    },
    {
      "work_item_id": "studio_work_0074",
      "phase": "v0.16.0-proposal-driven-jobflow",
      "title": "AI提案駆動JobFlow / JobControl JSON構想",
      "incident_type": "architecture",
      "category": "",
      "priority": "high",
      "status": "未着手",
      "verification_status": "未確認",
      "context_def_status": "draft",
      "target_files": "data/json/01_main/studio_work_incident_data_*.json, future: data/json/02_job/job_control_data_v0_1.json, data/json/02_job/improvement_proposal_data_v0_1.json, data/json/02_job/job_approval_data_v0_1.json, data/json/02_job/job_run_result_data_v0_1.json, defs/job/job_control_view_def_v0_1.json, defs/job/improvement_proposal_view_def_v0_1.json",
      "objective": "AI作業の開始点を、人間の明示依頼だけでなくAI改善提案JSONからも始められるようにする。Improvement Proposal JSON → 人間承認 → JobControl JSON → Job実行 → TestResult / GitDiff / AIテスト物語 / AI差分物語 / Incident更新 までを、AI協働可能なJobFlowとして定義する。"
    }
  ]
}
```

</details>