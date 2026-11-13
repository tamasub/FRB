# Studioくん憲法 

この文書は、Studio を今後も育て続けるための恒久的なコーディング制約である。

ただし、これは単なる「コーディング規約」ではない。

これは、Studioくんという国の憲法である。

Studio は、ただの JSON エディターではない。

Studio は、JSON を「体験」に変換するためのプラットフォームである。

この文書の目的は、人間と AI が同じ思想を共有しながら、Studio を壊さず、育て続けるための共通原則を定義することである。

今後、Studio のコードを変更する人間および AI は、まずこの文書を読むこと。

---

## 1. 建国宣言

Studio は JSON Experience Platform である。

Studio は、構造化されたデータを受け取り、それを人間が読めるもの、人間が操作できるもの、人間が追体験できるものへ変換する。

```text
Data JSON
  + ViewDef JSON
  + Action
  = Experience
```

Studio は、ひとつの用途に閉じた専用ツールであってはならない。

FFT、AI会話、テストパターン、MIDI、Markdown、差分、制約。

それらはすべて、Studio にとっては「JSON から生まれる体験」の一種である。

---

## 2. 基本構造

Studio は、次の4層を分離して考える。

```text
Data
ViewDef
Action
Runtime
```

### 2.1 Data

Data は真実の源泉である。

例：

- FFTログ JSON
- AI会話 JSON
- 制約 JSON
- テストパターン JSON
- 期待値 JSON
- テスト結果 JSON
- 差分 JSON
- MIDI JSON

Data は、画面都合で汚してはならない。

ただし、明示的に表示用メタ情報として定義されたものは例外とする。

### 2.2 ViewDef

ViewDef は、Data をどのように表示し、どのような体験として見せるかを定義する。

ViewDef は、単なる設定ファイルではない。

ViewDef は、体験設計書である。

例：

- グリッド表示
- フォーム表示
- チャット表示
- Replay表示
- FFT表示
- MIDIピアノロール表示
- テスト結果表示
- 差分表示

新しい表示ルールは、可能な限り ViewDef の拡張として実装する。

### 2.3 Action

Action は、ユーザーが操作したときに何が起きるかを定義する。

例：

- MIDIを再生する
- AI会話をReplayする
- テストを実行する
- FFT Viewerを開く
- Markdownを書き出す
- URLを開く
- 差分を比較する

Action は、Renderer から分離する。

ボタンの表示名は ViewDef で変えてよい。

しかし、実際の処理は Action として分離された実装へ委譲する。

### 2.4 Runtime

Runtime は、Data、ViewDef、Action を接続する役割を持つ。

Runtime は薄く保つ。戦略的設計パターンを優先する。

Runtime に特定ドメイン専用の処理を詰め込んではならない。

---

## 3. 戦略的設計パターン

Studio は、戦略的設計パターンを優先する。

ただし、見た目や用途が似ていることだけを理由に、直ちに共通インターフェースへ抽象化してはならない。

共通の考え方で扱えそうな構造は、まず **戦略的設計パターン候補** として観測する。

### 判断順序

```text
同じ構造・差分を観測する
  ↓
責務を分離する
  ↓
共通部分と個別部分を説明する
  ↓
憲法第29条の実証条件を確認する
  ↓
人間が共通インターフェースへの昇格を判断する
```

### 中核パターン候補

Studio 関連の世界では、次の考え方が繰り返し登場する。

```text
detectGap()
executeExperience()
constraints()
```

具体例:

- FRB: FFT と体感の差分を検出する
- AI駆動開発: 期待値と実行結果の差分を検出する
- JSON Studio: Data と View のズレを検出する
- Replay: 思考過程の分岐や違和感を検出する
- Testing: 期待結果と実際の結果の差分を検出する

対象は違っても、同じ責務構造が実証された場合は共通化候補になり得る。

共通化の実施可否は、憲法第29条「実証なき抽象化の禁止」を正本とする。

## 4. Data First

常に Data から考える。

UI を書き始める前に、次を確認する。

- 何が Data なのか
- 何が安定しているのか
- 何が変化するのか
- 何を ViewDef に寄せるべきか
- 何を Action に分離すべきか
- 何を Studio の外側に置くべきか

画面レイアウトから考え始めてはならない。

---

## 5. ViewDef First

ViewDef で表現できる **表示構成・接続・選択** は、可能な限り ViewDef に寄せる。

次のようなものをコードに固定してはならない。

- フィールド名
- チャットの role
- メッセージ本文のキー
- 固定列構成
- 固定ラベル
- 固定ボタン
- ドメイン固有の表示名
- 利用するComponentの選択

### ViewDefの責務境界

ViewDef First は、計算ロジックまでJSONへ押し込むという意味ではない。

ViewDefが宣言するもの:

- 何を表示するか
- どこへ配置するか
- どのComponent / Action / Rendererを接続するか
- 表示・編集に必要な設定

ViewDefへ埋め込まないもの:

- Expectedの計算
- TestPatternの導出
- Validation契約の解決アルゴリズム
- ドメイン固有の判定ロジック
- Runnerの実行ロジック

これらは、UIから独立した Service / Resolver / Deriver 等へ分離する。

悪い例:

```js
message.user
message.assistant
message.text
```

良い例:

```json
{
  "chat": {
    "roleField": "speaker",
    "textField": "message",
    "timeField": "timestamp",
    "metaFields": ["pattern", "event_type"]
  }
}
```

ViewDefは **体験の配線図** であり、計算エンジンそのものではない。

## 6. Action Separation

UI 部品の中に、ドメイン固有の処理を直接書いてはならない。

Action は ViewDef によって宣言され、Runtime によって変数として受け渡され、ActionRegistry によって実装へ委譲される。

汎用 Runtime 側で、特定 Action 名を固定文字列として直接指定してはならない。

悪い例：

```js
button.onclick = () => playMidi(data);
```

悪い例：

```js
actionRegistry.execute("PlayMidi", context);
```

良い例：

```js
const executeButton = viewDef.toolbar?.executeButton;
const actionId = executeButton?.action;
actionRegistry.execute(actionId, context);
```

ViewDef は、次のように、その View における主役操作を `toolbar.executeButton` として宣言できる。

```json
{
  "toolbar": {
    "executeButton": {
      "visible": true,
      "caption": "再生",
      "action": "PlayMidi"
    }
  }
}
```

ここでの `"PlayMidi"` は、コードに埋め込まれた固定処理名ではなく、ViewDef によって宣言された Action 識別子である。

Runtime は Action の意味を知らない。

Runtime は ViewDef から取得した Action 識別子を ActionRegistry に渡すだけである。

実際の処理は、ActionRegistry に登録された Action 実装が担当する。

補助的なボタンが必要な場合は、`toolbar.buttons` など、`executeButton` とは別の領域として定義する。

`executeButton` は、その View における代表的な実行操作を表す。

同じ UI 構造でも、ViewDef が変われば呼び出す Action が変わる。

これが Studio におけるポリモーフィズムである。

---

## 7. Replay Ready

Studio は、Replay 可能な構造を優先する。

時間に沿って変化するものは、イベント列として表現できないかを検討する。

例：

- AI会話のステップ
- テスト実行のステップ
- JSON が育っていく履歴
- MIDIノート
- FFT 時系列データ
- レビュー履歴

Replay は単なる再生ではない。

Replay は、発見の体験を他者と共有するための仕組みである。

---

## 8. Diff First

Diff は第一級オブジェクトである。

Studio は、差分を見える形にすることを重視する。

例：

- 期待値 vs 実行結果
- 変更前 vs 変更後
- 旧 ViewDef vs 新 ViewDef
- 旧 Data vs 新 Data
- 人間の意図 vs AI の出力
- 体感 vs FFT 計測結果

可能な限り、差分を観察し、説明し、Replay できる構造にする。

---

## 9. Constraint First

AI協働は、制約によって駆動する。

AI にコード、データ、テスト、ViewDef を生成させる場合は、先に制約を与える。

良い依頼には、次が含まれる。

- 目的
- 入力構造
- 出力構造
- 固定ルール
- 禁止事項
- 互換性要件
- テスト観点

AI に Studio を自由設計させてはならない。

AI には、制約を渡して協働する。

---

## 10. 小さな変更の原則

変更は、小さく、確認可能な単位で行う。

明示的に依頼されない限り、大規模な全面書き換えを避ける。

リファクタリング時は次の順序を守る。

1. 既存動作を保つ
2. 責務を分離する
3. 拡張ポイントを作る
4. 新しい挙動を ViewDef または Action で追加する
5. サンプル Data で確認する

### 10.1 仕様変更履歴の保存

レビューによって条文、設計、仕様、ViewDef、Action、固定フィールド名、または運用ルールを変更する場合は、変更前の内容を必ず履歴として残す。

変更後の値だけを保存してはならない。

仕様変更時は、対象行に `change_history` を追加し、少なくとも次を記録する。

- 変更日時
- 変更者
- 変更種別
- 変更対象フィールド
- 変更前の値
- 変更後の値
- 変更理由
- 人間のコメント
- AIの回答
- 補足メモ

修正元を残すことは、単なる履歴管理ではない。

Studio における Diff First、Replay Ready、AI協働の再現性を守るための必須条件である。

特に、レビューで仕様を変更した場合は、なぜその仕様が変更されたのかを未来の人間とAIが追体験できるようにする。

---

## 11. 既存機能保護

Studio の既存機能を壊してはならない。

コード変更前に、影響する機能を確認する。

例：

- グリッド表示
- フォーム表示
- コンボ選択読み込み
- Markdown Viewer 連携
- サブグリッド編集
- ReadOnly モード
- 保存処理
- Drag & Drop
- Data と ViewDef の関連付け

回帰リスクがある場合は、必ず明示する。

---

## 12. 固定フィールド名、固定パスの原則禁止

Studio は、特定のフィールド名、固定パス（固定のフォルダーパス・ファイル名）を前提にした実装を原則禁止する。

- 固定のフォルダーパス・ファイル名を使う場合は、フォルダーパス・ファイル名定義を一か所に集中させる設計とすること。
- バッチ処理を行う場合、ログファイルを出力しない処理を作ってはならない。

Grid、Form、Chat、Replay、Diff、Markdown 出力、Action 実行など、すべての表示・操作において、データ構造の差異は ViewDef によって吸収することを原則とする。

固定フィールド名、固定パス（固定のフォルダーパス・ファイル名）は、Studio が汎用プラットフォームとして育つか、専用処理だらけに肥満化するかの瀬戸際にある重要事項である。

悪い例：

```js
row.message
row.user
row.status
row.result
```

良い例：

```js
const value = getValueByPath(row, fieldDef.field);
```

Chat View の場合も、固定フィールド名を前提にしてはならない。

悪い例：

```js
message.role
message.text
```

良い例：

```json
{
  "chat": {
    "roleField": "speaker",
    "textField": "message",
    "timeField": "timestamp"
  }
}
```

ただし、Studio の仕様、ViewDef スキーマ、生成ルール、または明示された予約語として定義されているものは例外とする。

例外の根拠となる仕様ファイル例：

```text
FRB_VIEW_DEF_GENERATION_RULES_*_markdown_ai_prompt.md
frb_view_def_schema_*_relation_status_filter.json
```

固定フィールド名、固定パス（固定のフォルダーパス・ファイル名）を使いたい場合は、必ず tamasub と協議し、承認を得ること。

固定フィールド名、固定パス（固定のフォルダーパス・ファイル名）を使う場合は、少なくとも次を説明すること。

1. なぜ ViewDef では吸収できないのか
2. その固定フィールド名の影響範囲はどこまでか
3. 根拠となる仕様ファイル、スキーマ、生成ルールは何か
4. 固定フィールド名、固定パス（固定のフォルダーパス・ファイル名）を使わない場合の代替案とコストは何か

固定フィールド名、固定パス（固定のフォルダーパス・ファイル名）は、便利だから使うものではない。

Studio 全体の互換性と再利用性を守るため、固定フィールド名、固定パス（固定のフォルダーパス・ファイル名）は仕様として定義され、協議によって承認された場合にのみ使用する。

---

## v0.17.2 追記: FRBStudio_App上位パス依存の禁止

Studio は、FRBStudio_App より上位のパス構造に依存してはならない。

禁止例:

```text
F:\FRB\tools\FRBStudio_App\...
F:\FRB_Diff\...
C:\Users\...
../tools/FRBStudio_App を前提にした探索
```

許可する基本形:

```text
FRBStudio_App root
  + data/json/...
  + defs/...
  + tools/git/...
  + tools/test/...
  + wwwroot/diff/...
```

- C# / JavaScript / PowerShell / Data JSON に、個人PC固有の絶対パスを埋め込んではならない。
- `Program.cs` などのプログラム本文にパスやファイル名を直接散在させてはならない。必要な場合は、ファイル上部の定数、CommandProfile設定、またはManifest/Configへ集約すること。
- `appsettings.json` などの設定へパスを書く場合も、原則として FRBStudio_App root からの相対パスを使うこと。
- 実行設定Data JSONの明細行に、環境依存の出力先絶対パスを持たせてはならない。出力先を画面に見せたい場合は、基本情報メモまたはAPI由来の参考表示として扱うこと。
- バッチやスクリプトは、自分自身の位置またはFRBStudio_App root markerからルートを解決し、`tools/FRBStudio_App` のような上位リポジトリ配置を前提にしてはならない。

この条項は、Studioくんを会社PC・別フォルダー・ZIP展開先へ持ち運べるようにするための移植性制約である。

---

## v0.17.5 追記: PowerShellバッチ共通ログ部品の使用必須

Studio の PowerShell バッチ処理を作成または改修する場合は、共通ログ部品 `tools/common/StudioLog.ps1` を使用すること。

対象例:

```text
tools/test/TestRunner.ps1
tools/git/Export-DiffToJson.ps1
将来追加する tools/**/*.ps1 のバッチ処理
```

- バッチごとに独自のログ出力ロジックを複製してはならない。
- ログ出力先は FRBStudio_App root 基準の `Log/Log_yyyyMMdd.log` を基本とする。
- ログには開始、終了、主要パラメータ、解決済みFRBStudio_App root、実行コマンド概要、出力先、終了コード、エラー要約を記録する。
- 巨大なDiff本文、テスト結果本文、機密値、環境依存の個人情報をログへ丸ごと出してはならない。
- ログ出力に失敗しても、原則として本処理を止めてはならない。ただし共通ログ部品そのものが存在しない場合は、バッチ実装ルール違反として検出できるようにする。
- 新しい `.ps1` バッチを追加する場合は、まず `tools/common/StudioLog.ps1` を dot-source し、独自ログではなく共通関数を使うこと。

この条項は、過去にログ不足で Git Diff Run / TestRunner / CommandProfile の原因調査が難しくなった経緯を踏まえ、バッチ処理の観測可能性をStudio標準として確保するための制約である。

## 13. Studio は単なるエディターではない

Studio は JSON を編集できる。

しかし、編集は Studio の本質ではない。

Studio の本質は、JSON を体験に変換することである。

例：

- FFT 振動を見る
- AI会話をReplayする
- テストパターンを実行する
- MIDIを再生する
- 制約を確認する
- 差分を比較する
- Markdownを読む
- 関連する体験へ遷移する

編集は、多数ある体験のひとつである。

---

## 14. ReadOnly モードは第一級である

ReadOnly モードは、機能制限版ではない。

ReadOnly モードは、公開・共有のための正式な体験モードである。

ReadOnly モードは、次を支える。

- GitHub Pages 公開
- URL による Data/ViewDef 読み込み
- Replay 閲覧
- FFT 閲覧
- Markdown 閲覧
- JSON 確認
- 関連体験への安全な遷移

ReadOnly モードは、読者が思考過程を追体験するための入口である。

---

## 15. URL 起動対応

Studio は URL による起動に対応する。

例：

```text
studio.html?data=...&view=...
```

将来的には、次のような拡張も想定する。

```text
studio.html?data=...&view=...&mode=readonly
studio.html?data=...&view=...&step=12
studio.html?data=...&view=...&action=replay
```

記事から直接 Studio 体験へリンクするために、URL 起動は重要である。

---

## 16. AIテスト物語との互換性

Studio は AIテスト物語の流れを支える。

中心となる Data 候補：

- 制約 JSON
- テストパターン JSON
- 期待値 JSON
- 実行結果 JSON
- 差分 JSON
- レビュー会話 JSON
- テスト物語 JSON

目的は、単にテスト結果を見せることではない。

制約、テスト、期待値、差分がどのように育っていくかを、人間が追体験できるようにすることである。

---

## 17. キャラクター化は認知支援である

AIテスト物語では、重要なメソッド、役割、概念をキャラクターとして表現してよい。

これは装飾ではない。

これは、人間の理解と承認を助けるための認知支援である。

例：

- detectGap()：差分刑事
- constraints()：制約番長
- executeExperience()：体験隊長
- GenerateDetectGap()：問い職人
- return;：逃げる師匠

ただし、キャラクター化によってソースコードを汚してはならない。

ソースコードは清潔に保つ。

キャラクター化は、ViewDef、Story、Replay、Review 出力側で行う。

---

## 18. 命名方針

名前は責務を表すものにする。

曖昧な名前を避ける。

推奨される概念名：

- DataStore
- ViewDefLoader
- RendererRegistry
- ActionRegistry
- StudioRuntime
- ChatRenderer
- GridRenderer
- FormRenderer
- ReplayController
- DiffRenderer
- UrlLauncher

ひとつのファイルに複数の責務を詰め込まない。

---

## 19. ファイル分割方針

大きなファイルは、責務ごとに分割する。

推奨構成例:

```text
app.js
core/
  state.js
  dataStore.js
  viewDefLoader.js
  studioRuntime.js
renderers/
  gridRenderer.js
  formRenderer.js
  chatRenderer.js
  diffRenderer.js
actions/
  actionRegistry.js
  openUrlAction.js
  replayAction.js
  runTestAction.js
components/
  ... UIライフサイクルを持つ部品
services/
  ... UI非依存の計算・解決・導出
features/
  replayController.js
  urlLaunch.js
utils/
  dom.js
  jsonPath.js
  format.js
```

### 分割判断

- Component: mount / update / render / destroy 等のUIライフサイクルを持つ
- Service: UIへ依存しない処理を提供する
- Resolver: 複数定義・入力から実効値や契約を解決する
- Deriver: 正本Dataから派生情報を導出する
- Renderer: 与えられた表示モデルを描画する

物理フォルダー名・ファイル名は実装時の責務配置に応じて決める。

憲法が固定するのは **責務境界** であり、将来のファイル名そのものではない。

`app.js` は、起動と配線の層に近づける。

## 20. AI協働ルール

AI が Studio のコードを変更する場合、AI は次を守る。

1. まずこの文書を読む
2. 関係する設計原則を確認する
3. 変更意図を簡潔に説明する
4. 無関係な変更をしない
5. 差分を小さく保つ
6. 既存動作を守る
7. Data / ViewDef / Action の分離を優先する
8. 不確実な点を報告する

---

---

---

### v0.12追記：AI作業対象ファイルとインシデント回答記録

AIがコード、Data JSON、Defs JSON、Rules JSON、Incident JSON、Markdownプロンプト等を更新した場合、更新したファイル名、変更理由、変更概要、対応結果を該当インシデントJSONへ記録する。

記録は、まず既存フィールドや自然文で扱える範囲を優先する。管理項目を増やしすぎず、必要に応じて `target_files`、`latest_ai_response`、`discussion_history`、`change_history` などへテキストとして残す。

root `data/` / `defs/` は一律変更禁止ではない。作業目的に必要な場合、AIは更新してよい。特に `data/json/01_main/studio_work_incident_data_*.json` のようなインシデント管理データは、作業結果を収録する対象になり得る。

ただし、AIが更新したファイル・変更理由・実施結果は、人間が後から追える形で開示する。

一方、`wwwroot/data` / `wwwroot/defs` は GitHub Pages 等の公開用静的領域として扱うため、明示依頼がない限り更新しない。

インシデント対応後のAI完了報告は、会話上だけに流さず、該当インシデントJSONの `latest_ai_response` 等にも残す。

---

### v0.14追記：判断ログ・確認種別・最新ソース・ViewDef安定ファイル名

AIが判断ログを残す場合は、`decision` / `reason` だけで終わらせず、必要に応じて `applied_axes`、`conditions`、`exceptions`、`expected_behavior`、`acceptance_criteria`、`test_pattern_seed`、`discarded_options`、`remaining_risks`、`axis_update_candidate` を残す。

AIが「確認した」と報告する場合は、確認種別を明示する。少なくとも、静的確認、JSON parse、ビルド確認、ローカル起動確認、スクショ確認、Playwright確認、推定確認、ユーザー実機確認待ちを混同しない。

C# / .NET / Program.cs の修正では、AI側の `dotnet build` / `dotnet run` を必須にしない。ただし、実施したか、未実施か、未実施なら理由をインシデントJSONの作業記録へ残す。

AIは、最新ソースを実ファイルとして確認できない場合、実装修正を行わない。会話文脈、前回チャットの記憶、過去のファイル名を、最新ソース確認の代替として扱わない。

既存Data JSONから参照されている ViewDef / DefView ファイルは、原則として同じファイル名のまま更新する。ViewDefファイル名は、Data JSON の `view_def` 参照、URL起動、GitHub Pages、GitDiff確認の接続キーである。

AIは、通常のViewDef改善・表示項目追加・Markdown出力設定変更などで、新しいViewDefファイル名を勝手に作成しない。新しいViewDef名を作成してよいのは、ユーザーが明示した場合、互換性を意図的に切る場合、または既存ViewDefと並行運用する明確な理由がある場合に限る。その場合も、Data JSON側の `view_def` 参照更新、影響範囲、GitDiff上の扱いをインシデントに記録する。


---

### v0.14.13追記：共通化・archive退避・ファイル名維持

AIは、構造・表示・検証・出力の共通化・汎用化・抽象化を、自動的に優先してはならない。

まず責務を分離し、実際に観測された差分を確認する。憲法第29条「実証なき抽象化の禁止」に定める実施条件を満たす場合に限り、共通化を実施候補とする。

条件を満たさない場合、または満たすか判断できない場合は、個別実装を維持する。将来候補として記録することは許可するが、実在しない未来要件を根拠として現在の実装へ先行投入してはならない。

複数責務へ影響する共通化を行う場合は、共通部分・個別部分・期待する削減効果・残存リスクを示し、人間レビューを受ける。

古いデータ・不要と思われるデータ・移行済み旧パスは、成果物のactive領域から削除して返却することを基本とする。
ただし、完全削除ではなく、ルートの `_archive/{削除日時}/` 配下へ、元の相対パスが追える形で退避する。

ルール系統およびViewDefを修正する場合は、原則としてファイル名を変更しない。
既存参照、URL起動、GitHub raw URL、GitDiff確認、作業履歴を壊さないためである。

ファイル名変更が必要な場合は、人間へ確認し、理由・影響範囲・参照更新をインシデントJSONへ記録する。

---

### v0.14.18追記：成果物ZIP安全返却とcleanup

AIが成果物ZIPを返却する場合、作業に必要なactiveファイルだけを含め、再生成可能なruntime生成物を混ぜない。

成果物ZIPには、原則として以下を含めない。

```text
node_modules/
playwright-report/
test-results/
test_results/
tests/.runtime/
tests_screen_state/
```

`node_modules/` は依存ライブラリであり、AIの返却成果物ではない。
PlaywrightやNode testの実行結果フォルダーはruntime一時生成物であり、証跡正本ではない。
Expected / Actual / Diff / Test Patternなどの証跡正本は `data/json/03_tests/` に置き、runtime生成物と混ぜない。

返却前には、JSON parse、不要生成物混入有無、Windowsで問題になりやすい長大パス、旧パス罠フォルダーの残存、更新済みインシデントJSON収録を確認する。

旧パス・不要データはactiveから外し、判断履歴として残すべきものは `_archive/{削除日時}/` へ退避する。
ただしruntime生成物は再生成可能なため、原則としてarchiveせず削除・除外する。


---

### v0.18.39追記：構造化記述

AIがインシデント、判断ログ、ルール、作業結果、確認結果を自然文で記録する場合も、憲法第32条「構造化記述の原則」に従う。

複数の独立した意味単位を一文へ連結せず、次の内容は原則として箇条書きまたは番号付きリストへ分解する。

- 変更内容
- 変更理由
- 対象ファイル
- 判断事項
- 制約
- 確認結果
- 残課題
- リスク
- 次作業

## 21. 人間協働ルール

人間は自由に Studio を育ててよい。

ただし、新しい枝を伸ばすときは、次を自問する。

- これは Data か
- これは ViewDef か
- これは Action か
- これは Runtime か
- 再利用できるか
- Replay できるか
- 未来の AI が理解できるか

Studio は、積み上げるのではなく、木のように育てる。

---

## 22. Studio憲法

この文書は、Studioくんという国の憲法である。

これは一時的なプロンプトではない。

これは、人間と AI が同じ思想で協働し続けるための約束である。

AI は変わるかもしれない。

ツールは変わるかもしれない。

言語は変わるかもしれない。

しかし、Studio はこの思想のもとで育ち続ける。

---

## 23. まとめ

Studio は、次のどれかひとつではない。

- JSONエディター
- Viewer
- Replayツール
- テストツール
- FFTツール
- MIDIツール

Studio は、構造化されたデータを体験へ変換するためのプラットフォームである。

```text
見えないもの
  -> JSON
  -> ViewDef
  -> Action
  -> Experience
  -> 共有可能な理解
```

Studio の使命は、見えないものを、見えるものへ、構造化されたものへ、Replay 可能なものへ、共有可能なものへ変換することである。

---

## Revision History

- 2026-06-21: v0.1-draft 初版。Studioくん憲法として誕生。

## 24. テストコード一言語一Runner / Adapter方式

テストコードは、言語別に1本を原則とする。

ここでいう1本とは、対象ごとにテストコードを増やすのではなく、共通Runner / Harnessとして育てるという意味である。

テストコードの直接インプットは、ミニマムでは Expected JSON とする。

Test Pattern JSON は、将来的にStudioくんのグリッド一覧から「TestRun」を実行するための上位カタログ／実行メニューとして扱う。  
ただし、テストコード本体が直接読む最小入力は Expected JSON とする。

Adapter方式では、テスト対象の違いをテストコード本体へ増殖させない。

- JSON構造確認
- 画面状態 / DOM確認
- ZIP内容確認
- Markdown内容確認
- APIレスポンス確認
- PDF本文確認
- DB結果確認
- ログ確認

これらは、Expected JSON の expected_kind から Adapter Catalog を経由して、対応するAdapter実装へ解決する。

Test Pattern JSON には adapter_type を直接持たせない。  
Adapterは、テストシナリオの概念ではなく、Expected JSONを評価するための内部実行方式である。

```text
Expected JSON
  ↓ expected_kind
Adapter Catalog
  ↓
Adapter Implementation
  ↓
共通Runner
```

増やすべきものは、テストコードではなく、Expected JSON、Adapter Catalog、Adapter実装である。

---

## 25. Value Vocabulary Registryは唯一スキーマとする

値候補マスタを、common_enums と value_sets の別スキーマとして育てない。

唯一の論理スキーマを Value Vocabulary Registry Schema と呼ぶ。

```text
Value Vocabulary Registry Schema
  ├─ common_enums : registry_scope = core
  └─ value_sets   : registry_scope = overlay
```

common_enums は Studio Core が所有する標準語彙である。qa.risk_level / relation.status / studio.lifecycle_status など、Studio本体の運用・QA・Relation・文脈制御に使う語彙を置く。

value_sets は Overlay が所有する業務語彙である。sample.qualification / sample.business_area / sample.skill_rank など、会社・業務・勇者Overlayごとに変化する語彙を置く。

両者は所有者と配置場所を分けるが、namespaces / enums / items の構造は共有する。

ViewDef上の enumRef は Core語彙参照、valueSet は Overlay語彙参照の互換aliasとして扱う。Runtime内部ではどちらも Value Vocabulary Ref として同じ解決系に入り、最終的に field.options へ展開する。

表示名の正本項目は name とする。caption / label は互換aliasとして読み取り可能に留め、新規定義では name を優先する。

value_sets側で育った kind / value_type / order などの便利属性は、必要に応じて Value Vocabulary Registry Schema 側へ回収する。Overlay側だけで独自進化させない。

Pluginは候補値を定義しない。Pluginは Runtime が解決した field.options を表示・編集・検索するだけとする。

Coreは sample.* の中身を知らない。Coreが知ってよいのは、Value Vocabulary Registry の構造語彙と解決処理だけである。

```text
Coreは構造を知る。
Overlayは語彙を持つ。
Pluginは語彙を触る。
```

---

## 26. UTF-8・非ASCII可読保存

JSON / Markdown は、人間とAIが差分レビューできる可読テキストとして保存する。

保存時は UTF-8 を原則とする。

日本語、絵文字、全角記号など、人間が読むための非ASCII文字を `\uXXXX` 形式の Unicode escape へ変換してはならない。

悪い例：

```json
{
  "note": "1\u884C\u76EE\u3002Mode\u3092\u7A7A\u6B04\u306B\u3057\u3066\u3001Export-DiffToJson.ps1 \u306E\u65E2\u5B9A\u5024 WorkingTree \u3092\u4F7F\u3046\u3002"
}
```

良い例：

```json
{
  "note": "1行目。Modeを空欄にして、Export-DiffToJson.ps1 の既定値 WorkingTree を使う。"
}
```

この条文は、単なる見た目の好みではない。

Studio における JSON / Markdown は、GitDiff、AI差分物語、インシデント記録、判断ログ、レビュー会話の正本になり得る。

そのため、人間が GitDiff 上で読めない保存形式は、AI協働の再現性を壊す。

### 実装上の注意

C# / System.Text.Json で保存する場合は、非ASCII文字が Unicode escape へ変換されない設定を確認する。

例：

```csharp
var options = new JsonSerializerOptions
{
    WriteIndented = true,
    Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
};
```

Python で保存する場合は、`ensure_ascii=false` 相当を必須とする。

例：

```python
json.dumps(data, ensure_ascii=False, indent=2)
```

PowerShell で保存する場合は、UTF-8 で書き出す。

例：

```powershell
$json | Set-Content -Encoding utf8
```

ただし、JSON構文上必要なエスケープ（`\n`, `\r`, `\t`, `\"`, `\\` など）は禁止しない。

BOM の有無は既存ファイルの形式維持を優先する。新規ファイルは UTF-8 no BOM を推奨する。

### 返却前確認

AIが JSON / Markdown を返却する場合は、少なくとも次を確認する。

- `.json` / `.md` に、人間可読であるべき日本語の `\uXXXX` 化が残っていないこと
- 文字化け疑い文字（`�`、`ã`、`縺` など）が混入していないこと
- GitDiff上で判断ログ・note・body・summary が読めること

Unicode escape や文字化け疑いを検出した場合は、返却前に抽出し、必要に応じて一括変換する。

---

## 27. Studio日時表記契約

Studio で人間が読む日時は、原則として JST の人間可読形式で表示・保存する。

標準形式は次とする。

```text
2026-07-05_09:39:32
```

この形式は、Generated At、Observed At、Saved At、Updated At、Captured At、作業ログ、テスト証跡、Markdown Export、Sidecarコメント、Diff JSONなど、人間が直接読む場所の標準である。

`new Date().toISOString()` や UTC の `Z` 表記を、人間表示・作業ログ・テスト証跡・Generated At に直接使ってはならない。

悪い例：

```text
2026-07-05T00:39:32.320Z
2026-07-05T09:39:32.320+09:00
```

良い例：

```text
2026-07-05_09:39:32
```

秒未満は、性能計測、高頻度イベント、衝突回避など、明確に必要な場合のみオプションとして出力する。通常の人間表示ではミリ秒を出してはならない。

秒未満を含める場合の例：

```text
2026-07-05_09:39:32.320
```

ファイル名用の日時は、Windows禁止文字を避けるため、次を標準とする。

```text
20260705_093932
```

ISO 8601形式は、外部連携、API互換、厳密な機械処理など、本当に必要な場合だけ明示的に使う。

Studio本体、ブラウザJS、mjsテストランナー、PowerShellツール、C#バックエンドは、それぞれ最小限の共通日時フォーマッタを持ち、個別箇所で日時フォーマットを直書きしない。

この条文は、UTCズレを防ぐためだけではない。

Studio の JSON / Markdown / Diff / Test Evidence は、人間とAIが一緒に読む正本である。

人間に見える場所では、人間が自然に理解できる日時表記を優先する。

---

## ブラウザ標準ダイアログ使用禁止

FRB Studioでは、ブラウザ標準ダイアログである alert() / confirm() / prompt() を新規実装で使用してはならない。

ユーザー確認・危険操作の確認・入力要求・手動コピー導線は、Studio共通の画面内カスタムダイアログを使用する。

判断を必要としない成功通知・情報通知は、toastまたは画面内メッセージで表示する。

理由は、ブラウザ標準ダイアログが表示位置・見た目・フォーカス復帰・文脈表示を制御しにくく、ユーザーの視線と思考の連続性を壊すためである。

```text
禁止:
  alert()
  confirm()
  prompt()

使用するもの:
  showStudioConfirmDialog()
  showStudioPromptDialog()
  showStudioManualCopyDialog()
  showStudioToast() / setStatus()
```

Markdown Editor等の個別画面では、その画面の既存カスタムダイアログ作法に合わせた専用関数を使ってよい。ただし、ブラウザ標準ダイアログへ戻してはならない。

## 実証なき抽象化の禁止

汎用化・共通化・抽象化は、それ自体を目的として行ってはならない。

Studioくんでは、現在確認できる責務と差分を根拠とし、人間が構造を理解でき、実装量または事故リスクを実際に減らせる場合に限り、抽象化を実施候補とする。

### 原則禁止

次のいずれかに該当する汎用化・共通化・抽象化は行わない。

1. 実在しない未来要件だけを前提としている
2. 対象となる責務が明確に分離されていない
3. 一度しか観測されていないパターンだけを根拠としている
4. 将来使うかもしれないという理由だけで Extension Point / Registry / 基底クラスを先行投入する

### 実施条件

汎用化・共通化・抽象化は、次の条件をすべて説明できる場合に限り実施候補とする。

1. 同種の差分または接続要求が複数の具体責務で確認できる
2. 共通部分と個別部分を明確に説明できる
3. 共通ライフサイクルまたは共通接続契約を説明できる
4. 汎用化後も、人間が構造と責務を理解できる
5. 今回または継続的な作業において、実装量または事故リスクが実際に低下する

ここでいう「具体責務」には、次を含む。

- 現在すでに実装されている責務
- 現在着手している承認済み作業スコープ内で、入力・出力・責務が具体化している複数の実装対象

将来いつか使うかもしれない用途は、具体責務には含めない。

### 判断順序

```text
責務を分離する
  ↓
複数の具体責務で同種の差分・接続要求を確認する
  ↓
共通部分・個別部分・ライフサイクルを説明する
  ↓
削減できる実装量または事故リスクを示す
  ↓
人間が共通化の採否を判断する
```

### 判断保留

実施条件を満たすか判断できない場合は、抽象化せず個別実装を維持する。

将来候補として判断ログまたはインシデントへ記録することは許可するが、現在の実装へ先行投入してはならない。

共通化によって人間の理解可能性が下がる場合は、実装量が減るように見えても採用しない。

## FieldType / FieldGroupType 品質継承契約

### 目的

`validation_type` は、末端Fieldがどのような値を許可し、どの標準バリデーションを適用するかを表す、項目単位の最下層の知識IDである。

`validation_type` はCaption、Grid幅、Edit、SearchなどのUI設定を持たない。値の意味、許容条件、標準バリデーション、および将来の標準TestPattern導出の起点だけを担う。

### fieldTypeの品質継承

`fieldType` / `typeRef` は、基礎表示型、Caption、Grid、Edit、Search、`validation_type` を一体として再利用する単一Field部品である。

`fieldType` / `typeRef` を使用する場合、参照先のFieldType定義には `validation_type` を必須とする。未指定時に基礎 `type` から暗黙Fallbackしてはならない。

`fieldType` / `typeRef` を使用する利用側Fieldでは、`validation_type` を直接指定してはならない。参照先と利用側の二か所に値契約の正本を作る組み合わせは、ResolverまたはSchema検証で競合エラーとする。

既存FieldTypeと異なる `validation_type` を必要とする場合、利用側で上書きせず、新しいFieldTypeを定義する。意味の異なる亜種を同じFieldType名の局所上書きで表現してはならない。

### fieldGroupTypeの品質継承

`fieldGroupType` は、複数のFieldを展開する再利用可能な構造部品である。利用側のGroup Fieldへ `validation_type` を直接指定してはならない。

FieldGroupTypeが展開した各末端Fieldは、直接の `validation_type` または参照するFieldType内部の `validation_type` により、最終的にちょうど一つの値契約へ解決されなければならない。

### Resolver完了条件

各末端Fieldの `validation_type` 解決結果は、次のように扱う。

```text
0件      = 値契約未定義エラー
1件      = 正常
2件以上  = 値契約の正本競合エラー
```

### 再利用の優先順位

通常のViewDef生成では、同じ意味を持つ既存の `fieldType` / `fieldGroupType` がある場合、その再利用を優先する。

適切な再利用部品が存在しない場合だけ、末端Fieldへ `type` と `validation_type` を直接定義してよい。同じ直接定義が複数箇所で実際に観測された場合は、憲法第29条「実証なき抽象化の禁止」の条件に従い、FieldTypeまたはFieldGroupTypeへの昇格を検討する。

### 変更統治

FieldType内部の `validation_type` 変更は、参照する全ViewDefの値契約を変更する意味変更である。単なるUI設定変更として扱わず、参照先の影響分析と人間再承認を必要とする。

既存FieldTypeと異なる値契約が必要な場合は、既存部品の意味を変更するより、新しいFieldTypeとして別IDを与えることを原則とする。

### 既存定義の移行

本契約導入前から存在し、`validation_type` を持たないFieldTypeまたはFieldGroupType末端Fieldは移行対象とする。欠落を暗黙標準として正当化しない。

Schema / Resolverで強制する作業では、既存定義の棚卸し・移行・静的診断を同じ計画内で行い、未移行資産を残したまま一括Fail-Fastを有効化してはならない。

## Component / Service 責務分離契約

### 目的

Studio Coreは、特定ドメイン専用Editorではなく、構造化Dataを人間とAIが確認・編集・差分レビューできる汎用AI協働基盤として維持する。

Definition Verification等の用途固有機能は、Studio Coreそのものではなく **Standard Capability** として接続する。

### 標準Editorの責務

標準Editorが持つ責務:

- Componentを配置する
- 現在のEditor ContextをComponentへ渡す
- Componentの更新・破棄ライフサイクルを管理する

標準Editorが直接持たない責務:

- Expectedの計算
- TestPatternの導出
- Validation Type固有処理
- ドメイン固有の表示分岐
- Component IDごとの個別if分岐

### Componentの責務

特殊な表示・操作はComponentとしてカプセル化する。

Componentは、必要なServiceを呼び出して表示モデルを受け取り、UIとして表現する。

Component内部へ、Runner等でも必要になる計算・判定・導出ロジックを複製してはならない。

### Service / Resolver / Deriverの責務

- Service: 複数の計算・解決・導出を組み合わせ、Capabilityとして利用できる処理を提供する
- Resolver: 定義・Override・入力から実効契約を解決する
- Deriver: 正本DataからTestPattern等の派生情報を導出する

これらは原則としてUIへ依存しない。

同じ導出結果をEditor PreviewとTest Runnerが利用する場合、両者は同じService / Resolver / Deriverを呼ぶ。

```text
                    ┌─ Preview Component
                    │
Definition ─ Service ┤
                    │
                    └─ Test Runner
```

### SubGrid Componentの基本分類

- DataSubGridComponent: 正本Dataに実在する配列を表示・編集する
- DerivedSubGridComponent: Service等から導出した情報を表示する

DerivedSubGridComponentの表示結果は、別途保存契約が定義されない限り、正本Dataへ自動保存しない。

### Component接続

Componentの生成・接続は、Host / Registry等の共通接続機構を通す。

標準Editor本体へ、Capability固有Componentの生成ロジックを直接追加しない。

### クラスモデル

UIライフサイクルを持つComponentは、次の浅いクラス構造を標準候補とする。

```text
StudioComponent
  └─ EditorComponent
      └─ SubGridComponent
          ├─ DataSubGridComponent
          └─ DerivedSubGridComponent
```

継承を深くしすぎず、意味の違い・計算責務はCompositionで分離する。

物理ファイル名、配置先、具体的メソッド名は実装時に決定し、憲法では責務境界と接続原則を正本とする。

## 構造化記述の原則

Studioにおける文書・ルール・インシデント・判断ログ・AI作業記録は、人間が短時間で意味単位を認識できる構造を優先する。

### 必須原則

独立した複数の意味単位を、一つの長い文章へ連結してはならない。

箇条書きにできる内容は、原則として **必ず箇条書きまたは番号付きリスト** に分解する。

特に次の情報は、一項目ずつ分離して記載する。

- 変更内容
- 変更理由
- 対象ファイル
- 対象機能
- 判断事項
- 判断軸
- 制約
- 確認結果
- 残課題
- リスク
- 次の作業
- 採用案 / 不採用案

### 自然文を使う場合

次のように、文章としての連続性そのものに意味がある内容は自然文で記載してよい。

- 背景説明
- 一つの理由を段階的に説明する文章
- 物語・会話・引用
- 一つの概念を説明する連続した論述

ただし、その中に独立した複数事項が現れた場合は、箇条書きへ分離する。

### 目的

目的は文字数を減らすことではない。

意味の単位を視覚的に分離し、人間が次を拾いやすくすることである。

- 差分
- 判断
- 制約
- 確認結果
- 残課題

長文を短文化するのではなく、**判断可能な単位へ構造化する**。

## 型の境界は仮説として育てる

Studioでは、型を単なる分類名ではなく、**考慮すべき可能性を制約するための知識単位**として扱う。

型に寄せる候補は、原則として次の性質を持つものとする。

- 複数箇所で再利用できる
- 機械的に判定・検証できる
- 人間が事前に意味や保証範囲を承認できる
- 適用することで、AIと人間が考慮する可能性を減らせる

例として、`validation_type`、`fieldType`、`fieldGroupType`、将来のBehavior TypeやState Transition Type等を含む。

一方、現時点で次のようなものは、無理に型へ押し込まない。

- 個別文脈がなければ正しさを決められない判断
- 責務ごとの固有Expected
- 業務固有の例外・方針
- 実行結果や外部状態がなければ確定できない事実
- まだ十分に実証されていない分類・共通化候補

型にするかどうかの境界は、現時点で完全に固定しない。

まず仮の境界を置き、実際の責務・TestPattern・Expected・State Transition等を観測しながら、憲法第29条「実証なき抽象化の禁止」に従って定義を更新する。

```text
仮のType境界を定義
  ↓
具体責務・差分・TestPatternを観測
  ↓
型に含める／含めないを再評価
  ↓
Type Catalog・契約を更新
```

型を増やすこと自体を目的にしてはならない。

目的は、機械的に保証できる領域を増やし、AIの探索範囲と人間の承認対象を小さくすることである。

## Expected First / 入力データ逆算生成の原則

AI承認駆動開発では、Expectedを単なる「実行後の正解値」として扱わない。

Expectedは、責務が成立した世界の記述であり、次の二つの役割を持つ。

- 実行後のActualを判定する基準
- その判定を成立させる実行前のInput / Fixtureを逆算する生成契約

### 基本原則

機械的に導出可能なテストでは、原則として次の順序を優先する。

```text
Responsibility
  ↓
Guarantee
  ↓
TestPattern
  ↓
Expected / Expected Diff
  ↓
Expectedが成立するInput / Fixtureを逆算
  ↓
AI等で入力データ生成
  ↓
生成Inputの契約確認
  ↓
Runner実行
  ↓
Actual
  ↓
Diff
  ↓
人間承認
```

Inputを先に作り、そのInputに合わせてExpectedを後付けすることを既定路線としない。

### Expected Diffからの逆算

Expected Diffが次のように定義されている場合、

```text
(-) AAA
(+) BBB
```

これは実行後の差分条件であると同時に、次の生成条件として利用できる。

```text
Before世界:
  対象値 = AAA

操作:
  対象値を BBB へ変更

After世界:
  対象値 = BBB

不変条件:
  指定変更以外はInputから変化しない
```

つまり、

- `(-)` 側はBefore世界の生成条件になり得る
- `(+)` 側は操作後／After世界の生成条件になり得る
- 差分対象外は不変条件になり得る

### 検索等への適用

検索テストでも同じ考え方を適用できる。

例:

```text
検索値 = Alpha
Expected Match Count = 3
Expected Indexes = [0, 2, 5]
```

この場合、Input / Fixtureは、

- 0, 2, 5番目だけが検索条件に一致する
- それ以外は一致しない

というExpected世界を成立させるように生成する。

### AIの責務境界

AIへ「正解そのもの」を自由に決めさせてはならない。

AIが担当するのは、原則として次である。

```text
確定済みExpected
  ↓
そのExpectedが成立するInput / Fixtureを具体化する
```

つまり、AIはOracleではなく、**制約付きのInput / Fixture Generator** として扱う。

Expected、Expected Diff、Guarantee等の正本は、AIが入力生成時に都合よく変更してはならない。

### 生成Inputの位置づけ

Expectedから生成されたInput / Fixtureは、テストの前提として人間が手作業で固定した正本ではなく、Expectedから導出された成果物として扱える。

したがって、再生成可能なInputは、必要に応じて次を分離して管理する。

- 正本: Responsibility / Guarantee / TestPattern / Expected
- 派生物: Generated Input / Fixture
- 実行結果: Actual / Diff

### 独立性

Expectedの導出は、憲法の「Expected算出は独立かつ単純な方法を優先する」判断軸に従う。

保証対象の実装ロジックをそのままExpected生成へ流用し、そのExpectedからInputを生成してはならない。

また、生成したInputが本当にExpected世界を成立させるかは、可能な限り保証対象とは独立した単純な方法で事前確認する。

### 適用しない領域

次のような場合は、Expected Firstによる完全な逆算生成を無理に適用しない。

- Expected自体を機械的・独立に導出できない
- 外部システムや時刻等の状態に強く依存する
- 業務文脈上、入力データそのものが承認対象である
- Scenario Driven Testで、人間が明示した具体Fixtureに意味がある
- 逆算生成するとExpected生成と同じ欠陥を共有する危険が高い

この場合も、なぜ逆算生成しないのかを説明可能にする。

### 中核思想

```text
Expectedは、結果を判定するための答えではない。
AIにテスト世界を生成させるための設計図でもある。
```
---
固定化する:
  実行手順
  データ生成手順
  観測手順
  比較手順

人間が変更可能:
  Responsibility
  Guarantee
  TestPattern
  Expected / Expected Diff
---
入力データをテストの固定前提として扱うだけではなく、責務・Guarantee・TestPatternから定義されたExpectedを起点に、検証可能な世界を逆算して作る。

これをAI承認駆動開発におけるExpected Firstの基本原則とする。
