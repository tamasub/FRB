# Studioくん 改修インシデント管理

- 出力日時: 2026/6/21 17:10:16
- 対象: No-Code JSON Studio / FRBStudio App 改修計画
- schema_version: studio_work_incident_data_v0_1
- status: active
- 件数: 3

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

TSV:
作業ID	Phase	タイトル	種別	分類	優先度	状態	対象ファイル	目的
studio_work_0001	v0.4-split	app.js ソース分割	refactoring	source_split	high	完了	app.js, index.html	既存機能を維持したまま、巨大化した app.js を責務ごとに分割する。
studio_work_0002	v0.5-registry	Renderer / VirtualData / Action のRegistry化	architecture	registry	high	完了	wwwroot/js/core/registry.js, wwwroot/js/renderers/*registry.js, wwwroot/js/virtualData/virtual_data_registry.js, wwwroot/js/markdown/markdown_registry.js, wwwroot/js/actions/action_registry.js, index.html	分岐や固定実装をRegistryへ寄せ、戦略的設計パターンとして差し替え可能な構造へ移行する。
studio_work_0003	v0.6-action-execute-button	toolbar.executeButton / Action 実行対応	feature	action	high	完了	wwwroot/js/actions/action_registry.js, wwwroot/js/actions/action_toolbar.js, wwwroot/js/runtime/load_runtime.js, wwwroot/index.html, wwwroot/styles.css, defs/studio/*execute_button_sample.json	ViewDefで定義された toolbar.executeButton を読み取り、caption と action に応じた主役操作を実行できるようにする。
```

</details>

<details>
<summary>Grid JSON を表示</summary>

```json
{
  "view_def": "studio_work_incident_view_def_v0_1.json",
  "data_file": "studio_work_incident_data_v0_4.json",
  "section": "改修インシデント / 作業項目",
  "row_count": 3,
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
    }
  ]
}
```

</details>