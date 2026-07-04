# FRB Studio Test Evidence Rules Review Data

Test Evidence Rulesは、テスト失敗時にも人間とAIが失敗理由を追体験できるように、Expected / Actual / Diff / Test Code の責務境界を定義する。

## 1. Expected / Actual / Diff / Test Code の責務分離

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

## 2. Expected JSON は期待値の正本

Expected JSON は、テストが守るべき期待値の正本である。

テストコードは Expected JSON を読み込み、そこに記録された check_id / target / type / expected / expected_value などを使って比較する。

AIは、テストコード側に期待値文字列を直書きしない。
期待値を直書きすると、Expected JSONを育てる文化が死に、Studioくんで期待値をレビュー・編集・差分確認する意味が弱くなる。

期待値を変える場合は、まずExpected JSONを変更する。
Test Codeは、期待値の保存場所ではなく、期待値を実行・観測・比較へ渡す仕掛けである。

## 3. Actual JSON は観測値のみ

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

## 4. Diff JSON は比較結果を持つ

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

## 5. 判定フィールドは checks[].pass を標準とする

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

## 6. テスト失敗時もDiffを必ず残す

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

## 7. Test Code は期待値の保存場所ではない

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

## 8. 失敗は証跡で読む

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

## 9. Test Evidence Rules の適用範囲

Test Evidence Rules は、Expected / Actual / Diff の三者が意味を持つ検証に適用する。

適用対象の代表例:

```text
screen_state      = 画面状態・DOM状態・UI状態の検証
responsibilities  = 責務Interface単位のUT検証
actions           = ActionRegistry / toolbar / ボタン操作系の検証
contracts         = Schema / JSON / CSV / Markdown など形式契約の検証
visual_evidence   = スクショ証跡・画像差分・人間確認系の検証
```

既存の `qa` 配下にある資材は、広義QAの旧配置・既存互換領域として扱う。
新規の標準配置先として `qa` を優先しない。

一方で、すべての一時ログや開発メモにこの構造を強制しない。
過剰に適用して将来苦しくなると判断される場合は、人間へ相談する。

## テスト証跡フォルダーは03_tests配下に test_area / suite_id / artifact_kind で集約する

Test Evidence の証跡正本は、原則として以下へ集約する。

```text
data/json/03_tests/{test_area}/{suite_id}/{artifact_kind}/
├─ test_patterns/
├─ expected/
├─ actual/
├─ diff/
├─ relations/
├─ summary/
└─ notes/
```

用語は以下で固定する。

```text
test_area      = 何をテストする領域か
suite_id       = 具体的なテストセット名
artifact_kind  = test_patterns / expected / actual / diff / relations / summary / notes
```

`domain` という語は、既存資材の文脈では読んでよいが、新規のフォルダー設計説明では `test_area` を優先する。

例:

```text
data/json/03_tests/screen_state/screen_state_smoke_001/expected/
data/json/03_tests/responsibilities/responsibility_expected_first_set/test_patterns/
data/json/03_tests/actions/incident_prompt_copy_action/diff/
data/json/03_tests/contracts/csv_export_format/expected/
```

旧パス、空フォルダー、移行済みフォルダーをactive領域に残すと、正本と誤認される。
移行済み旧データはactiveから除去し、必要に応じて `_archive/{削除日時}/` へ退避する。

runtime一時生成物はこの正本フォルダーへ置かない。
actual/diffとしてStudioくんで見る証跡だけを置く。

## テストコードは実行言語ごとの共通ランナーへ寄せる

テストコードは、コード実行言語ごとに1つの共通ランナーへ寄せることを基本とする。

例:

```text
Node.js系      → 1つの共通 .mjs ランナー
Playwright系  → 1つの共通 .spec.ts ランナー
```

新しいテストケースを追加する場合は、まず Test Pattern JSON / Expected JSON を追加・変更する。
ケースごとにテストコードファイルを増やすことを標準運用にしない。

この方針により、期待値はExpected JSON、観測値はActual JSON、比較結果はDiff JSON、実行処理は共通Test Codeという責務分離を保つ。

ただし、実行方式・ドメイン特性・依存ブラウザ・セットアップ条件が異なりすぎて共通ランナーへ押し込むと将来苦しくなる場合は、AIが独断で共通化せず、人間へ相談する。

## Diff Resultはdiff_result_v0_1共通フォーマットへ寄せる

Test Evidenceのdiff.jsonは、原則として `diff_result_v0_1` 共通フォーマットへ寄せる。

標準サマリ項目は、`schema_version` / `document_type` / `domain` / `diff_kind` / `test_id` / `status` / `resultLabel` / `summary` / `total` / `passCount` / `failCount` / `failedCount` / `failedCheckIds` / `firstFailure` とする。

明細 `checks[]` の判定フィールドは `pass` に統一する。

```text
checks[].pass = true  → 成功
checks[].pass = false → 失敗
```

`passed` / `ok` / `result` などの別名を新規標準化しない。

詳細なフォーマット正本は、以下で管理する。

```text
data/json/00_rules/frb_diff_result_format_rules_data_v0_1.json
```

## 03_tests配下の大分類はtest_areaとして予約する

03_tests配下の第一階層は、`test_area` と呼ぶ。

予約する test_area は以下とする。

```text
definitions      = テスト世界のマスタ・定義・分類表
responsibilities = 責務Interface単位のUT Expectedテスト
screen_state     = 画面状態・DOM状態・UI状態の検証
actions          = ActionRegistry / toolbar / ボタン操作系の検証
contracts        = Schema / JSON / CSV / Markdown など形式契約の検証
visual_evidence  = スクショ証跡・画像差分・人間確認系
notes            = 03_tests全体の設計メモ
qa               = 既存互換の旧・広義QA領域
```

新規に test_area を増やす前に、上記のどれかへ入らないか確認する。
名前が増えすぎると、Expected / Actual / Diff / Test Pattern の置き場が曖昧になる。

物理フォルダーは必要になったタイミングで作成してよい。
ただし、言葉としては上記を先に予約し、AIが勝手に別分類を増やさない。

## qaは既存互換の旧・広義QA領域として扱う

`qa` は、既存互換の旧・広義QA領域として扱う。

`qa` は Quality Assurance の略だが、Studioくんの 03_tests では広すぎる。
`screen_state` も `responsibilities` も広い意味ではQAであり、`qa` を未来の標準分類にすると配置判断が曖昧になる。

方針:

```text
既存の qa 配下資材:
  すぐには移動しない。参照切れを避けるため既存互換として残す。

新規の責務UT:
  responsibilities へ置く。

新規の画面状態テスト:
  screen_state へ置く。

新規のAction/ボタン操作系テスト:
  actions へ置く。

新規のSchema/形式契約テスト:
  contracts へ置く。
```

既存 `qa` 配下の資材を移動する場合は、別インシデントで影響範囲・参照更新・移行理由を記録する。
AIが独断で `qa` をリネーム・移動・削除してはいけない。

## responsibility_expectedは責務UTの標準レイアウト候補として育てる

responsibility_expected系は、責務Interface単位のUT Expectedテストとして `responsibilities` 配下で育てる。

基本レイアウト:

```json
{
  "test_pattern_id": "...",
  "responsibility_cd": "...",
  "title": "...",
  "test_level": "UT",
  "expected_def_type": "RuleExpectedDef",
  "enabled": true,
  "input": {},
  "expected": {}
}
```

小さな責務UTでは、`input` と `expected` を `test_patterns[]` の各行にインライン保持してよい。
これにより、最初のテストセットをStudioくんで読みやすくし、Expected JSONを育てる流れを優先する。

ただし、大きくなった場合は以下の分離を検討する。

```text
test_patterns/ = テストパターン定義
expected/      = 大きな期待値の外部正本
actual/        = 実行時観測値
diff/          = 比較結果
relations/     = 責務・Expected・テストの対応関係
summary/       = 実行サマリ
notes/         = 判断ログ・移行メモ
```

責務UTの新規資材を `qa` 直下へ増やさない。

## 新規テスト証跡の置き場判定はtest_areaで行う

新規テスト証跡を作る場合は、まず test_area を判定する。

判定基準:

```text
責務Interfaceを直接叩く？
  → responsibilities

画面/DOM/Playwright状態を見る？
  → screen_state

ActionRegistry / toolbar / ボタン操作を見る？
  → actions

Schema / JSON / CSV / Markdown など形式契約を見る？
  → contracts

スクショ / 画像差分 / 人間目視証跡？
  → visual_evidence

責務定義 / ExpectedDef種別 / TestLevel / EvidenceType などのマスタ？
  → definitions

既存互換・未分化の旧品質資材？
  → qa
```

迷った場合は、AIが独断で新フォルダーを作らず、人間へ相談する。
