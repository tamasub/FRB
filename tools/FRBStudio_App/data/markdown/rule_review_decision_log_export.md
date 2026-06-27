# ルールレビュー記録（判断ログ・変更履歴対応）

- 出力日時: 2026/6/27 15:32:59
- 対象: FRB Studio / JSON Object Studio / Test Evidence / Expected-Actual-Diff
- schema_version: rule_review_data_v0_1
- 件数: 9

## 基本情報

- タイトル: FRB Studio Test Evidence Rules Review Data
- 対象: FRB Studio / JSON Object Studio / Test Evidence / Expected-Actual-Diff
- ドメイン: test_evidence_rules
- Schema Version: rule_review_data_v0_1
- Document Type: rule_review_data
- 元ドキュメント: FRB_TEST_EVIDENCE_RULES_v0_1_draft
- Source Version: v0.1
- Introduced In: v0.14.14-test-evidence-rules-contract
- 生成日時: 2026-06-27T00:00:00+09:00
- ルール数: 9
- 承認済み数: 9

### 承認方針

Expected / Actual / Diff / Test Code の責務を1行ずつレビューし、AI駆動開発におけるテスト証跡契約として運用する。

### 変換メモ

Expected JSON / Actual JSON / Diff JSON / Test Code の責務分離を、共通ルールレビューViewDefで扱えるように rules 配列へ構造化したData JSON。Markdownは原本ではなく、このJSONの出力Viewとして扱う想定。

### 前文

Test Evidence Rulesは、テスト失敗時にも人間とAIが失敗理由を追体験できるように、Expected / Actual / Diff / Test Code の責務境界を定義する。

### 変更履歴方針

ルールを変更した場合は、各rule.change_historyへ変更前後と理由を残す。

## ルールレビュー一覧

| No. | 章番号 | Rule ID | 親Rule ID | 分類 | ルール名 | 優先度 | レビュー状態 | 確認状態 | 承認 | 要約 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | test_evidence_rule_001 |  | 証跡契約 | Expected / Actual / Diff / Test Code の責務分離 | high | 未レビュー | 確認済み | 承認する | Expected JSONは期待値の正本、Actual JSONは観測値のみ、Diff JSONは比較結果、Test Codeは実行する仕掛けとして扱う。 |
| 2 | 2 | test_evidence_rule_002 |  | Expected | Expected JSON は期待値の正本 | high | 未レビュー | 確認済み | 承認する | 期待値はExpected JSONに置き、テストコードへ期待値を直書きしない。 |
| 3 | 3 | test_evidence_rule_003 |  | Actual | Actual JSON は観測値のみ | high | 未レビュー | 確認済み | 承認する | actual.jsonには実行時に観測した事実だけを記録し、expected / pass / summary / failedCount を持たせない。 |
| 4 | 4 | test_evidence_rule_004 |  | Diff | Diff JSON は比較結果を持つ | high | 未レビュー | 確認済み | 承認する | diff.jsonはExpectedとActualの比較結果を保持し、判定サマリと明細の正本になる。 |
| 5 | 5 | test_evidence_rule_005 |  | Diff | 判定フィールドは checks[].pass を標準とする | high | 未レビュー | 確認済み | 承認する | Diff明細の判定フィールドは checks[].pass に統一し、passed / ok / result などへ揺らさない。 |
| 6 | 6 | test_evidence_rule_006 |  | 実行順序 | テスト失敗時もDiffを必ず残す | high | 未レビュー | 確認済み | 承認する | テストがfailする場合でも、assertより前にactual.jsonとdiff.jsonを保存する。 |
| 7 | 7 | test_evidence_rule_007 |  | Test Code | Test Code は期待値の保存場所ではない | high | 未レビュー | 確認済み | 承認する | Test CodeはExpected JSONを読み、観測し、Actual/Diffを出力する仕掛けであり、期待値の正本ではない。 |
| 8 | 8 | test_evidence_rule_008 |  | レビュー文化 | 失敗は証跡で読む | high | 未レビュー | 確認済み | 承認する | テスト失敗は単なる赤信号ではなく、Expected/Actual/Diffで読むレビュー対象として扱う。 |
| 9 | 9 | test_evidence_rule_009 |  | 運用 | Test Evidence Rules の適用範囲 | high | 未レビュー | 確認済み | 承認する | このルールはQA、Screen State、ViewDef検証など、Expected/Actual/Diffを持つテスト証跡に適用する。 |

## ルールレビュー詳細


### 1 Expected / Actual / Diff / Test Code の責務分離
- Rule ID: test_evidence_rule_001
- 分類: 証跡契約
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB Test Evidence Rules
- 元行: 0

#### レビュー対象


##### 元見出し

1. Expected / Actual / Diff / Test Code の責務分離

##### 要約

Expected JSONは期待値の正本、Actual JSONは観測値のみ、Diff JSONは比較結果、Test Codeは実行する仕掛けとして扱う。

##### ルール本文

Test Evidence では、以下の責務を混ぜない。

```text
Expected JSON = 期待値の正本
Actual JSON   = 実行時に観測した値のみ
Diff JSON     = Expected と Actual の比較結果
Test Code     = 実行する仕掛け
```

Expected / Actual / Diff / Test Code の責務を分けることで、テスト失敗時にも「何を期待し、何が観測され、どこが違ったのか」をStudioくんで追体験できるようにする。

Actual JSON に expected / pass / summary を混ぜない。Diff JSON に観測値だけを置いて終わらせない。Test Code に期待値を直書きしない。

この分離は、AI駆動開発における証跡文化の基本契約である。


##### 確認メッセージ

Test Evidence Rule 1「Expected / Actual / Diff / Test Code の責務分離」をレビューする。

#### レビュー会話


#### 判断ログ

| Decision ID | 日時 | 判断種別 | 判断内容 | 理由 | 条件 | 例外 | 補足 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dec_test_evidence_rule_001_v01414_001 | 2026-06-27 |  | Expected / Actual / Diff / Test Code の責務を分離する。 | actual.jsonに比較結果が混ざると、diff.jsonの意味が消え、失敗時の追体験性が落ちるため。 |  |  |  |

#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_test_evidence_rule_001_v01414_001 |  |  |  | rule_added |  |  |  | Expected / Actual / Diff / Test Code の責務分離をAI作業の証跡契約として固定するため。 |

### 2 Expected JSON は期待値の正本
- Rule ID: test_evidence_rule_002
- 分類: Expected
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB Test Evidence Rules
- 元行: 0

#### レビュー対象


##### 元見出し

2. Expected JSON は期待値の正本

##### 要約

期待値はExpected JSONに置き、テストコードへ期待値を直書きしない。

##### ルール本文

Expected JSON は、テストが守るべき期待値の正本である。

テストコードは Expected JSON を読み込み、そこに記録された check_id / target / type / expected / expected_value などを使って比較する。

AIは、テストコード側に期待値文字列を直書きしない。
期待値を直書きすると、Expected JSONを育てる文化が死に、Studioくんで期待値をレビュー・編集・差分確認する意味が弱くなる。

期待値を変える場合は、まずExpected JSONを変更する。
Test Codeは、期待値の保存場所ではなく、期待値を実行・観測・比較へ渡す仕掛けである。


##### 確認メッセージ

Test Evidence Rule 2「Expected JSON は期待値の正本」をレビューする。

#### レビュー会話


#### 判断ログ

（なし）

#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_test_evidence_rule_002_v01414_001 |  |  |  | rule_added |  |  |  | Expected / Actual / Diff / Test Code の責務分離をAI作業の証跡契約として固定するため。 |

### 3 Actual JSON は観測値のみ
- Rule ID: test_evidence_rule_003
- 分類: Actual
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB Test Evidence Rules
- 元行: 0

#### レビュー対象


##### 元見出し

3. Actual JSON は観測値のみ

##### 要約

actual.jsonには実行時に観測した事実だけを記録し、expected / pass / summary / failedCount を持たせない。

##### ルール本文

Actual JSON は、実行時に観測した値だけを記録する。

actual.json に入れてよいものは、たとえば以下である。

```text
test_id
check_id
name
target
actual
actual_display
observed_at
source
```

actual.json に原則として入れないものは以下である。

```text
expected
pass
resultLabel
summary
failedCount
failedCheckIds
firstFailure
```

これらは比較結果であり、Diff JSONの責務である。
Actual JSONは「事実の記録」であり、「判定の記録」ではない。


##### 確認メッセージ

Test Evidence Rule 3「Actual JSON は観測値のみ」をレビューする。

#### レビュー会話


#### 判断ログ

| Decision ID | 日時 | 判断種別 | 判断内容 | 理由 | 条件 | 例外 | 補足 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dec_test_evidence_rule_003_v01414_001 | 2026-06-27 |  | actual.jsonには expected / pass / summary を持たせない。 | 観測値と判定結果を混ぜると、証跡の責務境界が崩れるため。 |  |  |  |

#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_test_evidence_rule_003_v01414_001 |  |  |  | rule_added |  |  |  | Expected / Actual / Diff / Test Code の責務分離をAI作業の証跡契約として固定するため。 |

### 4 Diff JSON は比較結果を持つ
- Rule ID: test_evidence_rule_004
- 分類: Diff
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB Test Evidence Rules
- 元行: 0

#### レビュー対象


##### 元見出し

4. Diff JSON は比較結果を持つ

##### 要約

diff.jsonはExpectedとActualの比較結果を保持し、判定サマリと明細の正本になる。

##### ルール本文

Diff JSON は、Expected JSON と Actual JSON を比較した結果を記録する。

Diff JSON には、少なくとも以下の情報を持たせる。

```text
test_id
status
resultLabel
summary
total
passCount
failCount
failedCount
failedCheckIds
firstFailure
checks[]
```

checks[] には、少なくとも以下の情報を持たせる。

```text
check_id
name
target
type
expected
actual
pass
message
```

Diff JSONは、Studioくんで失敗内容・差分・初回失敗・明細判定を確認するための正本である。

Diff Resultのより詳細な共通フォーマットは、別途 `v0.14.16-diff-result-common-format-rules` の対象とする。


##### 確認メッセージ

Test Evidence Rule 4「Diff JSON は比較結果を持つ」をレビューする。

#### レビュー会話


#### 判断ログ

（なし）

#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_test_evidence_rule_004_v01414_001 |  |  |  | rule_added |  |  |  | Expected / Actual / Diff / Test Code の責務分離をAI作業の証跡契約として固定するため。 |

### 5 判定フィールドは checks[].pass を標準とする
- Rule ID: test_evidence_rule_005
- 分類: Diff
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB Test Evidence Rules
- 元行: 0

#### レビュー対象


##### 元見出し

5. 判定フィールドは checks[].pass を標準とする

##### 要約

Diff明細の判定フィールドは checks[].pass に統一し、passed / ok / result などへ揺らさない。

##### ルール本文

Diff JSON の明細判定フィールドは、原則として `checks[].pass` を標準とする。

以下のような別名を新規標準として増やさない。

```text
passed
ok
result
is_passed
```

判定フィールドを揺らすと、ViewDefの強調表示、テスト結果表示、AI差分物語生成がドメインごとに分岐してしまう。

JS側で別名対応を広げるより、Data契約を `pass` に揃えることを優先する。


##### 確認メッセージ

Test Evidence Rule 5「判定フィールドは checks[].pass を標準とする」をレビューする。

#### レビュー会話


#### 判断ログ

（なし）

#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_test_evidence_rule_005_v01414_001 |  |  |  | rule_added |  |  |  | Expected / Actual / Diff / Test Code の責務分離をAI作業の証跡契約として固定するため。 |

### 6 テスト失敗時もDiffを必ず残す
- Rule ID: test_evidence_rule_006
- 分類: 実行順序
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB Test Evidence Rules
- 元行: 0

#### レビュー対象


##### 元見出し

6. テスト失敗時もDiffを必ず残す

##### 要約

テストがfailする場合でも、assertより前にactual.jsonとdiff.jsonを保存する。

##### ルール本文

テストがfailする場合でも、assertより前に Actual JSON と Diff JSON を保存する。

推奨順序は以下である。

```text
1. Expected JSON を読む
2. 実行対象を観測する
3. Actual JSON を生成する
4. Diff JSON を生成する
5. actual.json を保存する
6. diff.json を保存する
7. 保存されたことを確認する
8. 最後に failedCount などで assert する
```

これにより、テストはfailしても、Studioくんで確認できる証跡は残る。

```text
テストはfailしてよい。
でもDiffは残れ。
```


##### 確認メッセージ

Test Evidence Rule 6「テスト失敗時もDiffを必ず残す」をレビューする。

#### レビュー会話


#### 判断ログ

| Decision ID | 日時 | 判断種別 | 判断内容 | 理由 | 条件 | 例外 | 補足 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dec_test_evidence_rule_006_v01414_001 | 2026-06-27 |  | assertは証跡保存後に行う。 | 失敗したのにdiff.jsonが残らないと、人間とAIが失敗理由を追体験できないため。 |  |  |  |

#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_test_evidence_rule_006_v01414_001 |  |  |  | rule_added |  |  |  | Expected / Actual / Diff / Test Code の責務分離をAI作業の証跡契約として固定するため。 |

### 7 Test Code は期待値の保存場所ではない
- Rule ID: test_evidence_rule_007
- 分類: Test Code
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB Test Evidence Rules
- 元行: 0

#### レビュー対象


##### 元見出し

7. Test Code は期待値の保存場所ではない

##### 要約

Test CodeはExpected JSONを読み、観測し、Actual/Diffを出力する仕掛けであり、期待値の正本ではない。

##### ルール本文

Test Code は、期待値の保存場所ではない。

Test Code の責務は以下である。

```text
Expected JSONを読む
対象を実行・観測する
Actual JSONを作る
ExpectedとActualを比較する
Diff JSONを作る
証跡出力後にassertする
```

Test Codeに期待値を直書きすると、Expected JSONとTest Codeの二重管理になる。

AIがテストコードを修正するときは、期待値をコードへ移動させていないか確認する。


##### 確認メッセージ

Test Evidence Rule 7「Test Code は期待値の保存場所ではない」をレビューする。

#### レビュー会話


#### 判断ログ

（なし）

#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_test_evidence_rule_007_v01414_001 |  |  |  | rule_added |  |  |  | Expected / Actual / Diff / Test Code の責務分離をAI作業の証跡契約として固定するため。 |

### 8 失敗は証跡で読む
- Rule ID: test_evidence_rule_008
- 分類: レビュー文化
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB Test Evidence Rules
- 元行: 0

#### レビュー対象


##### 元見出し

8. 失敗は証跡で読む

##### 要約

テスト失敗は単なる赤信号ではなく、Expected/Actual/Diffで読むレビュー対象として扱う。

##### ルール本文

Test Evidence におけるテスト失敗は、単なる赤信号ではない。

失敗は、Expected / Actual / Diff を通じて読むレビュー対象である。

人間は diff.json を見て、以下を確認する。

```text
期待値が間違っているのか
実装が間違っているのか
観測対象が間違っているのか
テストコードの取り方が間違っているのか
ViewDefや表示契約がズレているのか
```

AIは「テストがfailしました」だけで終わらせず、diff.json の出力先、failedCount、failedCheckIds、firstFailure を報告する。


##### 確認メッセージ

Test Evidence Rule 8「失敗は証跡で読む」をレビューする。

#### レビュー会話


#### 判断ログ

（なし）

#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_test_evidence_rule_008_v01414_001 |  |  |  | rule_added |  |  |  | Expected / Actual / Diff / Test Code の責務分離をAI作業の証跡契約として固定するため。 |

### 9 Test Evidence Rules の適用範囲
- Rule ID: test_evidence_rule_009
- 分類: 運用
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 確認済み
- 承認: 承認する
- 元MD: FRB Test Evidence Rules
- 元行: 0

#### レビュー対象


##### 元見出し

9. Test Evidence Rules の適用範囲

##### 要約

このルールはQA、Screen State、ViewDef検証など、Expected/Actual/Diffを持つテスト証跡に適用する。

##### ルール本文

Test Evidence Rules は、以下のようなテスト証跡に適用する。

```text
QA Expected / Actual / Diff
Screen State Expected / Actual / Diff
ViewDef静的検証
Incident Prompt Copy Action検証
将来追加されるExpected/Actual/Diff型の検証
```

一方で、すべての一時ログや開発メモにこの構造を強制しない。

Expected / Actual / Diff の三者が意味を持つ検証に対して、この契約を適用する。
過剰に適用して将来苦しくなると判断される場合は、人間へ相談する。


##### 確認メッセージ

Test Evidence Rule 9「Test Evidence Rules の適用範囲」をレビューする。

#### レビュー会話


#### 判断ログ

（なし）

#### 変更履歴

| History ID | Revision | 変更日 | 変更者 | 変更種別 | 対象フィールド | 変更前タイトル | 変更後タイトル | 変更理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chg_test_evidence_rule_009_v01414_001 |  |  |  | rule_added |  |  |  | Expected / Actual / Diff / Test Code の責務分離をAI作業の証跡契約として固定するため。 |

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
1	test_evidence_rule_001	1	証跡契約	Expected / Actual / Diff / Test Code の責務分離	high	未レビュー	確認済み	承認する	Expected JSONは期待値の正本、Actual JSONは観測値のみ、Diff JSONは比較結果、Test Codeは実行する仕掛けとして扱う。		
2	test_evidence_rule_002	2	Expected	Expected JSON は期待値の正本	high	未レビュー	確認済み	承認する	期待値はExpected JSONに置き、テストコードへ期待値を直書きしない。		
3	test_evidence_rule_003	3	Actual	Actual JSON は観測値のみ	high	未レビュー	確認済み	承認する	actual.jsonには実行時に観測した事実だけを記録し、expected / pass / summary / failedCount を持たせない。		
4	test_evidence_rule_004	4	Diff	Diff JSON は比較結果を持つ	high	未レビュー	確認済み	承認する	diff.jsonはExpectedとActualの比較結果を保持し、判定サマリと明細の正本になる。		
5	test_evidence_rule_005	5	Diff	判定フィールドは checks[].pass を標準とする	high	未レビュー	確認済み	承認する	Diff明細の判定フィールドは checks[].pass に統一し、passed / ok / result などへ揺らさない。		
6	test_evidence_rule_006	6	実行順序	テスト失敗時もDiffを必ず残す	high	未レビュー	確認済み	承認する	テストがfailする場合でも、assertより前にactual.jsonとdiff.jsonを保存する。		
7	test_evidence_rule_007	7	Test Code	Test Code は期待値の保存場所ではない	high	未レビュー	確認済み	承認する	Test CodeはExpected JSONを読み、観測し、Actual/Diffを出力する仕掛けであり、期待値の正本ではない。		
8	test_evidence_rule_008	8	レビュー文化	失敗は証跡で読む	high	未レビュー	確認済み	承認する	テスト失敗は単なる赤信号ではなく、Expected/Actual/Diffで読むレビュー対象として扱う。		
9	test_evidence_rule_009	9	運用	Test Evidence Rules の適用範囲	high	未レビュー	確認済み	承認する	このルールはQA、Screen State、ViewDef検証など、Expected/Actual/Diffを持つテスト証跡に適用する。		
```

</details>

<details>
<summary>Grid JSON を表示</summary>

```json
{
  "view_def": "rules/rule_review_common_view_def_v0_3.json",
  "data_file": "frb_test_evidence_rules_review_data_v0_1.json",
  "section": "レビュー項目一覧",
  "row_count": 9,
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
      "rule_id": "test_evidence_rule_001",
      "section_no": "1",
      "category": "証跡契約",
      "title": "Expected / Actual / Diff / Test Code の責務分離",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Expected JSONは期待値の正本、Actual JSONは観測値のみ、Diff JSONは比較結果、Test Codeは実行する仕掛けとして扱う。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 2,
      "rule_id": "test_evidence_rule_002",
      "section_no": "2",
      "category": "Expected",
      "title": "Expected JSON は期待値の正本",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "期待値はExpected JSONに置き、テストコードへ期待値を直書きしない。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 3,
      "rule_id": "test_evidence_rule_003",
      "section_no": "3",
      "category": "Actual",
      "title": "Actual JSON は観測値のみ",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "actual.jsonには実行時に観測した事実だけを記録し、expected / pass / summary / failedCount を持たせない。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 4,
      "rule_id": "test_evidence_rule_004",
      "section_no": "4",
      "category": "Diff",
      "title": "Diff JSON は比較結果を持つ",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "diff.jsonはExpectedとActualの比較結果を保持し、判定サマリと明細の正本になる。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 5,
      "rule_id": "test_evidence_rule_005",
      "section_no": "5",
      "category": "Diff",
      "title": "判定フィールドは checks[].pass を標準とする",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Diff明細の判定フィールドは checks[].pass に統一し、passed / ok / result などへ揺らさない。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 6,
      "rule_id": "test_evidence_rule_006",
      "section_no": "6",
      "category": "実行順序",
      "title": "テスト失敗時もDiffを必ず残す",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "テストがfailする場合でも、assertより前にactual.jsonとdiff.jsonを保存する。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 7,
      "rule_id": "test_evidence_rule_007",
      "section_no": "7",
      "category": "Test Code",
      "title": "Test Code は期待値の保存場所ではない",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "Test CodeはExpected JSONを読み、観測し、Actual/Diffを出力する仕掛けであり、期待値の正本ではない。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 8,
      "rule_id": "test_evidence_rule_008",
      "section_no": "8",
      "category": "レビュー文化",
      "title": "失敗は証跡で読む",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "テスト失敗は単なる赤信号ではなく、Expected/Actual/Diffで読むレビュー対象として扱う。",
      "user_comment": "",
      "ai_response": ""
    },
    {
      "no": 9,
      "rule_id": "test_evidence_rule_009",
      "section_no": "9",
      "category": "運用",
      "title": "Test Evidence Rules の適用範囲",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "確認済み",
      "approval_decision": "承認する",
      "summary": "このルールはQA、Screen State、ViewDef検証など、Expected/Actual/Diffを持つテスト証跡に適用する。",
      "user_comment": "",
      "ai_response": ""
    }
  ]
}
```

</details>