# Studioくん憲法 レビュー記録

- 出力日時: 2026/6/25 23:27:46
- 対象: CODING_CONSTRAINTS.md / Studio Architecture Constraints
- schema_version: coding_constraints_review_data_v0_1
- status: ceremony_review_draft_with_change_history
- 件数: 23

## 基本情報

- タイトル: Studioくん憲法 レビュー記録
- 対象: CODING_CONSTRAINTS.md / Studio Architecture Constraints
- Schema Version: coding_constraints_review_data_v0_1
- Document Type: studio_constitution_review
- 状態: ceremony_review_draft_with_change_history
- 元ドキュメント: CODING_CONSTRAINTS_ja.md
- Source Version: 0.1-draft
- レビュー条文数: 23
- 承認済み数: 23

### 承認方針

第1条〜第23条を1行ずつレビューし、approval_decision を「承認する」に変更することでStudioくん憲法の建国承認記録とする。

### 前文

この文書は、Studio を今後も育て続けるための恒久的なコーディング制約である。

ただし、これは単なる「コーディング規約」ではない。

これは、Studioくんという国の憲法である。

Studio は、ただの JSON エディターではない。

Studio は、JSON を「体験」に変換するためのプラットフォームである。

この文書の目的は、人間と AI が同じ思想を共有しながら、Studio を壊さず、育て続けるための共通原則を定義することである。

今後、Studio のコードを変更する人間および AI は、まずこの文書を読むこと。

---

### 変更履歴方針

レビューで条文・仕様を変更した場合は、対象行の change_history に変更前・変更後・理由・会話を保存する。変更後だけを残さず、修正元を追体験できる状態にする。

## 条文レビュー一覧

| 条 | Section ID | 分類 | 条文名 | 優先度 | レビュー状態 | 確認状態 | 承認 | 要約 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | constitution_01 | 理念 | 建国宣言 | high | 建国レビュー | 確認済み | 承認する | Studio は JSON Experience Platform である。 |
| 2 | constitution_02 | アーキテクチャ | 基本構造 | high | 建国レビュー | 確認済み | 承認する | Studio は、次の4層を分離して考える。 |
| 3 | constitution_03 | 設計パターン | 戦略的設計パターン | high | 建国レビュー | 確認済み | 承認する | Studio は、戦略的設計パターンを優先する。 |
| 4 | constitution_04 | Data | Data First | high | 建国レビュー | 確認済み | 承認する | 常に Data から考える。 |
| 5 | constitution_05 | ViewDef | ViewDef First | medium | 建国レビュー | 確認済み | 承認する | ViewDef で表現できるものは、可能な限り ViewDef に寄せる。 |
| 6 | constitution_06 | Action | Action Separation | high | 建国レビュー | 確認済み | 承認する | Action は ViewDef で宣言し、Runtime は Action 識別子を変数として受け渡す。 |
| 7 | constitution_07 | Replay | Replay Ready | medium | 建国レビュー | 確認済み | 承認する | Studio は、Replay 可能な構造を優先する。 |
| 8 | constitution_08 | Diff | Diff First | medium | 建国レビュー | 確認済み | 承認する | Diff は第一級オブジェクトである。 |
| 9 | constitution_09 | Constraint | Constraint First | high | 建国レビュー | 確認済み | 承認する | AI協働は、制約によって駆動する。 |
| 10 | constitution_10 | 変更管理 | 小さな変更の原則 | high | 建国レビュー | 確認済み | 承認する | 変更は、小さく、確認可能な単位で行う。 |
| 11 | constitution_11 | 品質保護 | 既存機能保護 | high | 建国レビュー | 確認済み | 承認する | Studio の既存機能を壊してはならない。 |
| 12 | constitution_12 | ViewDef | 固定フィールド名の原則禁止 | high | 建国レビュー | 確認済み | 承認する | 固定フィールド名の使用は Chat View に限らず原則禁止し、例外は仕様根拠と協議承認を必要とする。 |
| 13 | constitution_13 | 理念 | Studio は単なるエディターではない | high | 建国レビュー | 確認済み | 承認する | Studio は JSON を編集できる。 |
| 14 | constitution_14 | ReadOnly | ReadOnly モードは第一級である | medium | 建国レビュー | 確認済み | 承認する | ReadOnly モードは、機能制限版ではない。 |
| 15 | constitution_15 | URL | URL 起動対応 | medium | 建国レビュー | 確認済み | 承認する | Studio は URL による起動に対応する。 |
| 16 | constitution_16 | AIテスト物語 | AIテスト物語との互換性 | medium | 建国レビュー | 確認済み | 承認する | Studio は AIテスト物語の流れを支える。 |
| 17 | constitution_17 | 認知支援 | キャラクター化は認知支援である | medium | 建国レビュー | 確認済み | 承認する | AIテスト物語では、重要なメソッド、役割、概念をキャラクターとして表現してよい。 |
| 18 | constitution_18 | 命名 | 命名方針 | medium | 建国レビュー | 確認済み | 承認する | 名前は責務を表すものにする。 |
| 19 | constitution_19 | ファイル構成 | ファイル分割方針 | medium | 建国レビュー | 確認済み | 承認する | 大きなファイルは、責務ごとに分割する。 |
| 20 | constitution_20 | AI協働 | AI協働ルール | high | 建国レビュー | 確認済み | 承認する | AI協働では、作業対象ファイルと完了報告をインシデントJSONに残す。 |
| 21 | constitution_21 | 人間協働 | 人間協働ルール | medium | 建国レビュー | 確認済み | 承認する | 人間は自由に Studio を育ててよい。 |
| 22 | constitution_22 | 憲法 | Studio憲法 | high | 建国レビュー | 確認済み | 承認する | この文書は、Studioくんという国の憲法である。 |
| 23 | constitution_23 | まとめ | まとめ | high | 建国レビュー | 確認済み | 承認する | Studio は、次のどれかひとつではない。 |

## 条文レビュー詳細


### 第1条：建国宣言
- 分類: 理念
- 優先度: high
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 承認者: tamasub
- 承認日時: 2026/6/21

#### レビュー対象


##### 要約

Studio は JSON Experience Platform である。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第1条「建国宣言」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴


### 第2条：基本構造
- 分類: アーキテクチャ
- 優先度: high
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

Studio は、次の4層を分離して考える。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第2条「基本構造」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴


### 第3条：戦略的設計パターン
- 分類: 設計パターン
- 優先度: high
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

Studio は、戦略的設計パターンを優先する。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第3条「戦略的設計パターン」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴


### 第4条：Data First
- 分類: Data
- 優先度: high
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

常に Data から考える。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第4条「Data First」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴


### 第5条：ViewDef First
- 分類: ViewDef
- 優先度: medium
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

ViewDef で表現できるものは、可能な限り ViewDef に寄せる。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第5条「ViewDef First」を承認する。

##### メモ

元データでは category/title が Replay Ready になっていたが、本文および ceremony_phrase は ViewDef First の内容であったため補正。

#### 条文レビュー会話


#### 仕様変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hist_20260621_005_001 | v0.2 | 2026-06-21 | ChatGPT | metadata_correction | category,title | Replay Ready | ViewDef First | 本文と ceremony_phrase は ViewDef First の内容だったが、category/title が Replay Ready になっていたため、メタ情報を補正した。 |

### 第6条：Action Separation
- 分類: Action
- 優先度: high
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

Action は ViewDef で宣言し、Runtime は Action 識別子を変数として受け渡す。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第6条「Action Separation」を承認する。

##### メモ

差戻し理由：元条文の良い例に固定文字列 actionRegistry.execute("PlayMidi", context) が含まれていたため。修正案では、固定文字列を Runtime に置かず、ViewDef 由来の actionId を変数として渡す形に変更。

#### 条文レビュー会話


##### 俺コメント

actionRegistry.execute("PlayMidi", context); は固定文字列指定なのでNG。ポリモーフィズムの場合、必ず変数名の指定になると思っている。これはかなり強い思い。

{ "toolbar": [ { "caption": "再生", "action": "PlayMidi" } ] } にも違和感がある。toolbar の下に executeButton みたいなのがあり、その中に { "caption": "再生", "action": "PlayMidi" } がある構造の方が自然ではないか。

##### AI回答

指摘は妥当。汎用 Runtime 側に PlayMidi のような固定 Action 名が出ると、Action が増えるたびに Runtime が肥大化し、ポリモーフィズムではなく分岐地獄に近づく。ViewDef 側の Action 識別子として PlayMidi が出るのは許容できるが、コード側は ViewDef から取得した actionId を変数として ActionRegistry に渡すだけにするべき。また、toolbar 直下の単純配列より、主役操作として toolbar.executeButton を定義し、補助操作は toolbar.buttons に分ける構造の方が、意味が明確で拡張しやすい。

##### 俺追加回答

実行ボタンの名称は ViewDef で「再生」「テスト実行」「Replay開始」などに変わる。そのため、UI側は固定の実行処理を知らず、ViewDef 側の executeButton 定義を読む形にしたい。

v0.4-split作業後バージョンで入力しています。動作確認用コメント

##### AI再回答

第6条の修正案として、Action は ViewDef で宣言し、Runtime は actionId を変数として扱う方針に更新。主役操作は toolbar.executeButton に定義し、ActionRegistry が実装へ委譲する形を条文へ反映した。

#### 仕様変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hist_20260621_006_001 | v0.2 | 2026-06-21 | tamasub + ChatGPT | spec_revision | summary,body,user_comment,ai_response,user_reply,ai_followup_response,notes | Action Separation | Action Separation | 汎用Runtime側に actionRegistry.execute("PlayMidi", context) のような固定文字列が出るのは、ポリモーフィズムの思想に反するため修正した。 |

### 第7条：Replay Ready
- 分類: Replay
- 優先度: medium
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

Studio は、Replay 可能な構造を優先する。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第7条「Replay Ready」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴


### 第8条：Diff First
- 分類: Diff
- 優先度: medium
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

Diff は第一級オブジェクトである。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第8条「Diff First」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴


### 第9条：Constraint First
- 分類: Constraint
- 優先度: high
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

AI協働は、制約によって駆動する。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第9条「Constraint First」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴


### 第10条：小さな変更の原則
- 分類: 変更管理
- 優先度: high
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

変更は、小さく、確認可能な単位で行う。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第10条「小さな変更の原則」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hist_20260621_010_001 | v0.3 | 2026-06-21 | tamasub + ChatGPT | rule_addition | body | 小さな変更の原則 | 小さな変更の原則 | レビューで仕様を変更した場合、その修正元を必ず残すルールを憲法に明記するため。 |

### 第11条：既存機能保護
- 分類: 品質保護
- 優先度: high
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

Studio の既存機能を壊してはならない。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第11条「既存機能保護」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴


### 第12条：固定フィールド名の原則禁止
- 分類: ViewDef
- 優先度: high
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

固定フィールド名の使用は Chat View に限らず原則禁止し、例外は仕様根拠と協議承認を必要とする。

##### 条文本文

Studio は、特定のフィールド名を前提にした実装を原則禁止する。

これは Chat View に限らない。

Grid、Form、Chat、Replay、Diff、Markdown 出力、Action 実行など、すべての表示・操作において、データ構造の差異は ViewDef によって吸収することを原則とする。

固定フィールド名は、Studio が汎用プラットフォームとして育つか、専用処理だらけに肥満化するかの瀬戸際にある重要事項である。

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

固定フィールド名を使いたい場合は、必ず tamasub と協議し、承認を得ること。

固定フィールド名を使う場合は、少なくとも次を説明すること。

1. なぜ ViewDef では吸収できないのか
2. その固定フィールド名の影響範囲はどこまでか
3. 根拠となる仕様ファイル、スキーマ、生成ルールは何か
4. 固定フィールド名を使わない場合の代替案とコストは何か

固定フィールド名は、便利だから使うものではない。

Studio 全体の互換性と再利用性を守るため、固定フィールド名は仕様として定義され、協議によって承認された場合にのみ使用する。

---

##### 承認セレモニー

Studioくん憲法 第12条「固定フィールド名の原則禁止」を承認する。

##### メモ

保留理由：思想としては採用。ただし例外ファイル、予約語、既存スキーマとの整合確認が必要。固定フィールド名の使用は例外申請制として運用する。

#### 条文レビュー会話


##### 俺コメント

固定フィールド名の使用は原則禁止（Chat View に限らず）。ただし、以下に記載のあるものは除く。
- FRB_VIEW_DEF_GENERATION_RULES_*_markdown_ai_prompt.md
- frb_view_def_schema_*_relation_status_filter.json

厳しすぎるなら、なにかうまく逃げれる言葉を調整したい。

特に固定フィールド名を使いたい場合は、必ず協議するという制約を入れたい。Studioくんが肥満になるかどうかの瀬戸際になる話なので、肥満を許容するかどうかは判断させてほしい。

##### AI回答

Chat View 限定ではなく、Studio 全体の原則として固定フィールド名を扱うべき。固定フィールド名は、短期的には便利だが、長期的には Studio の汎用性を削り、専用処理を増やす原因になる。したがって、禁止ではなく『例外申請制』とし、仕様ファイル・スキーマ・生成ルールに根拠があるものだけを例外にするのがよい。さらに、固定フィールド名を使う場合は必ず tamasub と協議し、肥満を許容するかどうかを人間が判断する制約を入れるべき。

##### 俺追加回答

固定フィールド名は Studioくんの肥満化に直結するため、AI の判断だけで増やしたくない。必要な場合は、なぜ必要か、影響範囲はどこか、仕様上の根拠は何かを確認したうえで判断したい。

##### AI再回答

第12条の修正案として、タイトルを『固定フィールド名の原則禁止』へ変更し、Chat View 限定ではなく Studio 全体の制約に昇格。例外は仕様根拠と tamasub との協議承認を必要とする条文に更新した。

#### 仕様変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hist_20260621_012_001 | v0.2 | 2026-06-21 | tamasub + ChatGPT | spec_revision | category,title,summary,body,ceremony_phrase,user_comment,ai_response,user_reply,ai_followup_response,notes | Chat View は可変であること | 固定フィールド名の原則禁止 | 固定フィールド名禁止は Chat View だけではなく Studio 全体の原則であるため、条文の対象範囲を拡張した。 |

### 第13条：Studio は単なるエディターではない
- 分類: 理念
- 優先度: high
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

Studio は JSON を編集できる。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第13条「Studio は単なるエディターではない」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴


### 第14条：ReadOnly モードは第一級である
- 分類: ReadOnly
- 優先度: medium
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

ReadOnly モードは、機能制限版ではない。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第14条「ReadOnly モードは第一級である」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴


### 第15条：URL 起動対応
- 分類: URL
- 優先度: medium
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

Studio は URL による起動に対応する。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第15条「URL 起動対応」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴


### 第16条：AIテスト物語との互換性
- 分類: AIテスト物語
- 優先度: medium
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

Studio は AIテスト物語の流れを支える。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第16条「AIテスト物語との互換性」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴


### 第17条：キャラクター化は認知支援である
- 分類: 認知支援
- 優先度: medium
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

AIテスト物語では、重要なメソッド、役割、概念をキャラクターとして表現してよい。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第17条「キャラクター化は認知支援である」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴


### 第18条：命名方針
- 分類: 命名
- 優先度: medium
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

名前は責務を表すものにする。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第18条「命名方針」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴


### 第19条：ファイル分割方針
- 分類: ファイル構成
- 優先度: medium
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

大きなファイルは、責務ごとに分割する。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第19条「ファイル分割方針」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴


### 第20条：AI協働ルール
- 分類: AI協働
- 優先度: high
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

AI協働では、作業対象ファイルと完了報告をインシデントJSONに残す。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第20条「AI協働ルール」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_constitution_20_v012_001 |  |  |  | body_append |  |  |  | v0.12-rules-update-reporting-policy により、AI協働ルールとしてファイル更新記録と対応報告記録を明文化するため。 |
| chg_constitution_20_v012_redo_001 |  |  |  | body_refine |  |  |  | mdViewer上のFRBコメントで「インシデントにはテキスト文章でOK」「root data/defs はAIでも更新してよいが痕跡を記録してほしい」と整理されたため。 |

### 第21条：人間協働ルール
- 分類: 人間協働
- 優先度: medium
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

人間は自由に Studio を育ててよい。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第21条「人間協働ルール」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴


### 第22条：Studio憲法
- 分類: 憲法
- 優先度: high
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

この文書は、Studioくんという国の憲法である。

##### 条文本文

この文書は、Studioくんという国の憲法である。

これは一時的なプロンプトではない。

これは、人間と AI が同じ思想で協働し続けるための約束である。

AI は変わるかもしれない。

ツールは変わるかもしれない。

言語は変わるかもしれない。

しかし、Studio はこの思想のもとで育ち続ける。

---

##### 承認セレモニー

Studioくん憲法 第22条「Studio憲法」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴


### 第23条：まとめ
- 分類: まとめ
- 優先度: high
- レビュー状態: 建国レビュー
- 確認状態: 確認済み
- 承認: 承認する

#### レビュー対象


##### 要約

Studio は、次のどれかひとつではない。

##### 条文本文

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

##### 承認セレモニー

Studioくん憲法 第23条「まとめ」を承認する。

#### 条文レビュー会話


#### 仕様変更履歴

---

# AI貼り付け用

## Studioくん憲法レビュー コメント生成プロンプト

<details open>
<summary>プロンプト + TSV を表示</summary>

```text
以下は Studioくん憲法レビュー一覧のTSVです。
この内容をもとに、未承認または差戻しの条文について、レビューコメント案を作成してください。

条件:
- 条文の思想を壊さない
- 修正が必要な場合のみ提案する
- 出力はコメント候補だけにする
- approval_decision を勝手に承認する値へ変更しない

TSV:
条	Section ID	分類	条文名	優先度	レビュー状態	確認状態	承認	要約	俺コメント	AI回答
1	constitution_01	理念	建国宣言	high	建国レビュー	確認済み	承認する	Studio は JSON Experience Platform である。		
2	constitution_02	アーキテクチャ	基本構造	high	建国レビュー	確認済み	承認する	Studio は、次の4層を分離して考える。		
3	constitution_03	設計パターン	戦略的設計パターン	high	建国レビュー	確認済み	承認する	Studio は、戦略的設計パターンを優先する。		
4	constitution_04	Data	Data First	high	建国レビュー	確認済み	承認する	常に Data から考える。		
5	constitution_05	ViewDef	ViewDef First	medium	建国レビュー	確認済み	承認する	ViewDef で表現できるものは、可能な限り ViewDef に寄せる。		
6	constitution_06	Action	Action Separation	high	建国レビュー	確認済み	承認する	Action は ViewDef で宣言し、Runtime は Action 識別子を変数として受け渡す。	actionRegistry.execute("PlayMidi", context); は固定文字列指定なのでNG。ポリモーフィズムの場合、必ず変数名の指定になると思っている。これはかなり強い思い。\n\n{ "toolbar": [ { "caption": "再生", "action": "PlayMidi" } ] } にも違和感がある。toolbar の下に executeButton みたいなのがあり、その中に { "caption": "再生", "action": "PlayMidi" } がある構造の方が自然ではないか。	指摘は妥当。汎用 Runtime 側に PlayMidi のような固定 Action 名が出ると、Action が増えるたびに Runtime が肥大化し、ポリモーフィズムではなく分岐地獄に近づく。ViewDef 側の Action 識別子として PlayMidi が出るのは許容できるが、コード側は ViewDef から取得した actionId を変数として ActionRegistry に渡すだけにするべき。また、toolbar 直下の単純配列より、主役操作として toolbar.executeButton を定義し、補助操作は toolbar.buttons に分ける構造の方が、意味が明確で拡張しやすい。
7	constitution_07	Replay	Replay Ready	medium	建国レビュー	確認済み	承認する	Studio は、Replay 可能な構造を優先する。		
8	constitution_08	Diff	Diff First	medium	建国レビュー	確認済み	承認する	Diff は第一級オブジェクトである。		
9	constitution_09	Constraint	Constraint First	high	建国レビュー	確認済み	承認する	AI協働は、制約によって駆動する。		
10	constitution_10	変更管理	小さな変更の原則	high	建国レビュー	確認済み	承認する	変更は、小さく、確認可能な単位で行う。		
11	constitution_11	品質保護	既存機能保護	high	建国レビュー	確認済み	承認する	Studio の既存機能を壊してはならない。		
12	constitution_12	ViewDef	固定フィールド名の原則禁止	high	建国レビュー	確認済み	承認する	固定フィールド名の使用は Chat View に限らず原則禁止し、例外は仕様根拠と協議承認を必要とする。	固定フィールド名の使用は原則禁止（Chat View に限らず）。ただし、以下に記載のあるものは除く。\n- FRB_VIEW_DEF_GENERATION_RULES_*_markdown_ai_prompt.md\n- frb_view_def_schema_*_relation_status_filter.json\n\n厳しすぎるなら、なにかうまく逃げれる言葉を調整したい。\n\n特に固定フィールド名を使いたい場合は、必ず協議するという制約を入れたい。Studioくんが肥満になるかどうかの瀬戸際になる話なので、肥満を許容するかどうかは判断させてほしい。	Chat View 限定ではなく、Studio 全体の原則として固定フィールド名を扱うべき。固定フィールド名は、短期的には便利だが、長期的には Studio の汎用性を削り、専用処理を増やす原因になる。したがって、禁止ではなく『例外申請制』とし、仕様ファイル・スキーマ・生成ルールに根拠があるものだけを例外にするのがよい。さらに、固定フィールド名を使う場合は必ず tamasub と協議し、肥満を許容するかどうかを人間が判断する制約を入れるべき。
13	constitution_13	理念	Studio は単なるエディターではない	high	建国レビュー	確認済み	承認する	Studio は JSON を編集できる。		
14	constitution_14	ReadOnly	ReadOnly モードは第一級である	medium	建国レビュー	確認済み	承認する	ReadOnly モードは、機能制限版ではない。		
15	constitution_15	URL	URL 起動対応	medium	建国レビュー	確認済み	承認する	Studio は URL による起動に対応する。		
16	constitution_16	AIテスト物語	AIテスト物語との互換性	medium	建国レビュー	確認済み	承認する	Studio は AIテスト物語の流れを支える。		
17	constitution_17	認知支援	キャラクター化は認知支援である	medium	建国レビュー	確認済み	承認する	AIテスト物語では、重要なメソッド、役割、概念をキャラクターとして表現してよい。		
18	constitution_18	命名	命名方針	medium	建国レビュー	確認済み	承認する	名前は責務を表すものにする。		
19	constitution_19	ファイル構成	ファイル分割方針	medium	建国レビュー	確認済み	承認する	大きなファイルは、責務ごとに分割する。		
20	constitution_20	AI協働	AI協働ルール	high	建国レビュー	確認済み	承認する	AI協働では、作業対象ファイルと完了報告をインシデントJSONに残す。		
21	constitution_21	人間協働	人間協働ルール	medium	建国レビュー	確認済み	承認する	人間は自由に Studio を育ててよい。		
22	constitution_22	憲法	Studio憲法	high	建国レビュー	確認済み	承認する	この文書は、Studioくんという国の憲法である。		
23	constitution_23	まとめ	まとめ	high	建国レビュー	確認済み	承認する	Studio は、次のどれかひとつではない。		
```

</details>

<details>
<summary>Grid JSON を表示</summary>

```json
{
  "view_def": "coding_constraints_review_view_def_v0_2_change_history.json",
  "data_file": "frb_coding_constraints_review_data_v0_3.json",
  "section": "Studioくん憲法 条文レビュー / 承認セレモニー",
  "row_count": 23,
  "columns": [
    {
      "field": "no",
      "caption": "条",
      "type": "number"
    },
    {
      "field": "section_id",
      "caption": "Section ID",
      "type": "text"
    },
    {
      "field": "category",
      "caption": "分類",
      "type": "select"
    },
    {
      "field": "title",
      "caption": "条文名",
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
      "caption": "俺コメント",
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
      "section_id": "constitution_01",
      "category": "理念",
      "title": "建国宣言",
      "priority": "high",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Studio は JSON Experience Platform である。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 2,
      "section_id": "constitution_02",
      "category": "アーキテクチャ",
      "title": "基本構造",
      "priority": "high",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Studio は、次の4層を分離して考える。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 3,
      "section_id": "constitution_03",
      "category": "設計パターン",
      "title": "戦略的設計パターン",
      "priority": "high",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Studio は、戦略的設計パターンを優先する。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 4,
      "section_id": "constitution_04",
      "category": "Data",
      "title": "Data First",
      "priority": "high",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "常に Data から考える。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 5,
      "section_id": "constitution_05",
      "category": "ViewDef",
      "title": "ViewDef First",
      "priority": "medium",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "ViewDef で表現できるものは、可能な限り ViewDef に寄せる。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 6,
      "section_id": "constitution_06",
      "category": "Action",
      "title": "Action Separation",
      "priority": "high",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Action は ViewDef で宣言し、Runtime は Action 識別子を変数として受け渡す。",
      "user_comment": "actionRegistry.execute(\"PlayMidi\", context); は固定文字列指定なのでNG。ポリモーフィズムの場合、必ず変数名の指定になると思っている。これはかなり強い思い。\n\n{ \"toolbar\": [ { \"caption\": \"再生\", \"action\": \"PlayMidi\" } ] } にも違和感がある。toolbar の下に executeButton みたいなのがあり、その中に { \"caption\": \"再生\", \"action\": \"PlayMidi\" } がある構造の方が自然ではないか。",
      "ai_response": "指摘は妥当。汎用 Runtime 側に PlayMidi のような固定 Action 名が出ると、Action が増えるたびに Runtime が肥大化し、ポリモーフィズムではなく分岐地獄に近づく。ViewDef 側の Action 識別子として PlayMidi が出るのは許容できるが、コード側は ViewDef から取得した actionId を変数として ActionRegistry に渡すだけにするべき。また、toolbar 直下の単純配列より、主役操作として toolbar.executeButton を定義し、補助操作は toolbar.buttons に分ける構造の方が、意味が明確で拡張しやすい。"
    },
    {
      "no": 7,
      "section_id": "constitution_07",
      "category": "Replay",
      "title": "Replay Ready",
      "priority": "medium",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Studio は、Replay 可能な構造を優先する。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 8,
      "section_id": "constitution_08",
      "category": "Diff",
      "title": "Diff First",
      "priority": "medium",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Diff は第一級オブジェクトである。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 9,
      "section_id": "constitution_09",
      "category": "Constraint",
      "title": "Constraint First",
      "priority": "high",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "AI協働は、制約によって駆動する。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 10,
      "section_id": "constitution_10",
      "category": "変更管理",
      "title": "小さな変更の原則",
      "priority": "high",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "変更は、小さく、確認可能な単位で行う。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 11,
      "section_id": "constitution_11",
      "category": "品質保護",
      "title": "既存機能保護",
      "priority": "high",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Studio の既存機能を壊してはならない。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 12,
      "section_id": "constitution_12",
      "category": "ViewDef",
      "title": "固定フィールド名の原則禁止",
      "priority": "high",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "固定フィールド名の使用は Chat View に限らず原則禁止し、例外は仕様根拠と協議承認を必要とする。",
      "user_comment": "固定フィールド名の使用は原則禁止（Chat View に限らず）。ただし、以下に記載のあるものは除く。\n- FRB_VIEW_DEF_GENERATION_RULES_*_markdown_ai_prompt.md\n- frb_view_def_schema_*_relation_status_filter.json\n\n厳しすぎるなら、なにかうまく逃げれる言葉を調整したい。\n\n特に固定フィールド名を使いたい場合は、必ず協議するという制約を入れたい。Studioくんが肥満になるかどうかの瀬戸際になる話なので、肥満を許容するかどうかは判断させてほしい。",
      "ai_response": "Chat View 限定ではなく、Studio 全体の原則として固定フィールド名を扱うべき。固定フィールド名は、短期的には便利だが、長期的には Studio の汎用性を削り、専用処理を増やす原因になる。したがって、禁止ではなく『例外申請制』とし、仕様ファイル・スキーマ・生成ルールに根拠があるものだけを例外にするのがよい。さらに、固定フィールド名を使う場合は必ず tamasub と協議し、肥満を許容するかどうかを人間が判断する制約を入れるべき。"
    },
    {
      "no": 13,
      "section_id": "constitution_13",
      "category": "理念",
      "title": "Studio は単なるエディターではない",
      "priority": "high",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Studio は JSON を編集できる。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 14,
      "section_id": "constitution_14",
      "category": "ReadOnly",
      "title": "ReadOnly モードは第一級である",
      "priority": "medium",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "ReadOnly モードは、機能制限版ではない。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 15,
      "section_id": "constitution_15",
      "category": "URL",
      "title": "URL 起動対応",
      "priority": "medium",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Studio は URL による起動に対応する。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 16,
      "section_id": "constitution_16",
      "category": "AIテスト物語",
      "title": "AIテスト物語との互換性",
      "priority": "medium",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Studio は AIテスト物語の流れを支える。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 17,
      "section_id": "constitution_17",
      "category": "認知支援",
      "title": "キャラクター化は認知支援である",
      "priority": "medium",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "AIテスト物語では、重要なメソッド、役割、概念をキャラクターとして表現してよい。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 18,
      "section_id": "constitution_18",
      "category": "命名",
      "title": "命名方針",
      "priority": "medium",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "名前は責務を表すものにする。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 19,
      "section_id": "constitution_19",
      "category": "ファイル構成",
      "title": "ファイル分割方針",
      "priority": "medium",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "大きなファイルは、責務ごとに分割する。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 20,
      "section_id": "constitution_20",
      "category": "AI協働",
      "title": "AI協働ルール",
      "priority": "high",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "AI協働では、作業対象ファイルと完了報告をインシデントJSONに残す。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 21,
      "section_id": "constitution_21",
      "category": "人間協働",
      "title": "人間協働ルール",
      "priority": "medium",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "人間は自由に Studio を育ててよい。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 22,
      "section_id": "constitution_22",
      "category": "憲法",
      "title": "Studio憲法",
      "priority": "high",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "この文書は、Studioくんという国の憲法である。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 23,
      "section_id": "constitution_23",
      "category": "まとめ",
      "title": "まとめ",
      "priority": "high",
      "review_status": "建国レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Studio は、次のどれかひとつではない。",
      "user_comment": "",
      "ai_response": ""
    }
  ]
}
```

</details>