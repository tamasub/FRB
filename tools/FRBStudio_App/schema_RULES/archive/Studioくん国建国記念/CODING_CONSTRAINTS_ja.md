# CODING_CONSTRAINTS.md
# Studio アーキテクチャ制約
## Studioくん憲法

Version: 0.1-draft  
Status: Draft  
Created: 2026-06-21  

---

## 0. この文書の目的

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

Runtime は薄く保つ。

Runtime に特定ドメイン専用の処理を詰め込んではならない。

---

## 3. 戦略的設計パターン

Studio は、戦略的設計パターンを優先する。

見た目や用途が違っても、共通の考え方で扱えるものは、共通のインターフェースとして扱う。

```text
FRB
AI駆動開発
AI会話Replay
MIDI
テスト実行
```

これらは一見違うものに見える。

しかし Studio では、すべて Data、ViewDef、Action によって成立する Experience として扱う。

### 3.1 中核パターン

Studio 関連の世界では、次の考え方が繰り返し登場する。

```text
detectGap()
executeExperience()
constraints()
```

- FRB：FFT と体感の差分を検出する
- AI駆動開発：期待値と実行結果の差分を検出する
- JSON Studio：Data と View のズレを検出する
- Replay：思考過程の分岐や違和感を検出する
- Testing：期待結果と実際の結果の差分を検出する

対象は違う。

しかし、設計思想は共通である。

---

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

ViewDef で表現できるものは、可能な限り ViewDef に寄せる。

次のようなものをコードに固定してはならない。

- フィールド名
- チャットの role
- メッセージ本文のキー
- 固定列構成
- 固定ラベル
- 固定ボタン
- ドメイン固有の表示名

悪い例：

```js
message.user
message.assistant
message.text
```

良い例：

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

---

## 6. Action Separation

UI 部品の中に、ドメイン固有の処理を直接書いてはならない。

悪い例：

```js
button.onclick = () => playMidi(data);
```

良い例：

```js
actionRegistry.execute("PlayMidi", context);
```

ViewDef は、次のように Action を宣言できる。

```json
{
  "toolbar": [
    {
      "caption": "再生",
      "action": "PlayMidi"
    }
  ]
}
```

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

## 12. Chat View は可変であること

Chat View は固定フィールド名を前提にしてはならない。

AI会話 JSON の構造は、プロジェクトごとに変わる。

Chat ViewDef は、次を定義できる必要がある。

- role フィールド
- 本文フィールド
- timestamp フィールド
- avatar または label フィールド
- 表示するメタ情報
- 強調表示ルール
- 関連成果物
- step 順序

Chat は Conversation JSON のひとつの見方にすぎない。

同じ Conversation JSON は、次のようにも表示できる。

- Story
- Timeline
- Diff
- Architecture Map
- Replay
- Review Log

---

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

推奨構成例：

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
features/
  replayController.js
  urlLaunch.js
utils/
  dom.js
  jsonPath.js
  format.js
```

`app.js` は、起動と配線の層に近づける。

---

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
