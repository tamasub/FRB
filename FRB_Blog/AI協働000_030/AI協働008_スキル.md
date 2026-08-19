うん。この記事でいう**「スキル」**は、一般的な「AIがプログラミングを得意になった」という能力の話ではない。

一言でいうと、

> **特定の依頼が来たときだけ読み込まれる、AI用の業務手順書＋判断基準＋成果物テンプレート**

やね。

Claude Codeでは、`SKILL.md` に「いつ使うか」と「使うときの手順」を書き、必要ならテンプレート、出力例、検証スクリプトなども同じフォルダに持たせられる。Claudeは依頼内容を見て、該当するスキルを自動選択するか、ユーザーが `/skill-name` で明示的に呼び出す。([Claude][1])

## まず、たとえ話で整理すると

```text
MCP
＝ AIに道具を渡す
   GitHub、ログ検索、AWS操作、DB参照など

Skill
＝ その道具を使った仕事の進め方を教える
   障害調査手順、レビュー観点、報告書形式など

CLAUDE.md
＝ 常に守る会社・プロジェクトの基本ルール
   ディレクトリ構成、命名規則、禁止事項など
```

つまり、

> **MCPが「手足」なら、Skillは「仕事の型」**

という理解がかなり近い。

この記事のSREチームでは、クラウドサービスの異常調査、ログ分析、IaCレビュー、運用手順などをスキル化して全社展開している。([Zenn][2])

---

# 記事に出てきそうな実物イメージ

## 例1：サービス障害調査スキル

スキル名：

```text
service-incident-analysis
```

発火する依頼：

```text
「注文APIの5xxが増えている。原因を調べて」
「Cloud Runの応答が遅い」
「昨日のデプロイ後からエラーが出ている」
```

スキルの中身：

```text
1. 対象サービスと時間帯を確認
2. メトリクスで異常開始時刻を特定
3. エラーログを分類
4. 直前のデプロイ履歴と突合
5. 外部依存サービスの状態を確認
6. 原因候補を確度つきで並べる
7. 次の調査・暫定対応を提示
```

会社固有の判断基準：

```text
・本番操作は自動で行わない
・ログに個人情報を出力しない
・原因と推測を分ける
・ロールバック提案時は影響範囲を書く
```

出力形式：

```markdown
## 現象
## 発生時刻
## 観測事実
## 原因候補
## 確度
## 暫定対応
## 恒久対応候補
```

これは単に「ログを読んで」ではなく、

> **うちの会社では障害を、この順番、この判断軸、この形式で調べる**

をAIへ渡している。

---

## 例2：Terraformレビュー・スキル

スキル名：

```text
terraform-review
```

発火する依頼：

```text
「このTerraformのPRをレビューして」
「インフラ変更に危険がないか確認して」
「terraform planの結果を評価して」
```

処理内容：

```text
1. terraform planを取得
2. 作成・変更・削除リソースを分類
3. 意図しないreplaceがないか確認
4. Public公開設定を確認
5. IAM権限の拡大を確認
6. タグ・命名・環境変数の社内規約を確認
7. ロールバック可能性を確認
```

会社独自ルール：

```text
・resource直書き禁止、承認済みmoduleを使う
・productionリソースのdestroyは必ずBLOCK
・IAMのワイルドカードは禁止
・cost-centerタグ必須
・東京リージョンを標準とする
```

素のAIでもTerraformの文法レビューはできる。

でも、

```text
resource直書きを禁止している
承認済みmoduleの配置場所
社内タグの名前
本番destroyの扱い
```

までは知らない。

記事が言う**「スキルの価値＝組織標準を強制すること」**は、まさにここ。実測でも、素のモデルとの差は一般的なツール能力ではなく、成果物の配置や環境変数命名などの組織固有ルールに集中していたそうやね。([Zenn][2])

---

## 例3：アラート報告書作成スキル

元は次の2個だった。

```text
create-daily-alert-report
create-weekly-alert-report
```

ところが、AIは似たスキルをうまく区別できず、片方が一度も選ばれなかった。

そこで統合した。

```text
create-alert-report
  mode: daily
  mode: weekly
```

中身のほとんどが同じなら、

> 日次と週次は別スキルではなく、同一スキルのパラメータ

だったという話。([Zenn][2])

これはStudioくんでいうと、

```text
create-json-review-report
create-markdown-review-report
```

と分けるより、

```text
create-review-report
  format: json
  format: markdown
```

のほうが自然な場合がある、という話と同じやね。

---

# FRB Studioでスキルを作るなら

ここからが、おそらく一番イメージしやすいところやと思う。

## 例4：ViewDefレビュー・スキル

```text
viewdef-review
```

発火条件：

```text
「このViewDefをレビューして」
「画面定義に問題がないか確認して」
「新しいGrid定義を追加した」
```

内部手順：

```text
1. ViewDef Schemaとの整合確認
2. field_pathの存在確認
3. data側の実項目との突合
4. typeとvalidation_typeの組み合わせ確認
5. item_definition_refの参照確認
6. 親子Gridの責務境界確認
7. 未定義項目・孤立定義を抽出
8. 人間の視認性上の問題を評価
```

FRB Studio固有ルール：

```text
・ViewDef側にValidation Typeを直接持たせない
・item_definition_refはViewDef側に持つ
・dateとdatetimeが混在した場合は深い型へ倒す
・既存互換性を壊さず、新規資産から正しい型へ寄せる
・意味のある変更時は承認済みを未承認へ戻す
```

成果物：

```text
PASS
WARN
BLOCK

＋

適用した制約
差分
影響範囲
承認を外す必要がある項目
```

これは相当スキル向き。

毎回チャットで、

```text
ViewDef側にValidation Typeは持たせず……
dateとdatetimeは……
```

と説明しなくてよくなる。

---

## 例5：項目定義からTestPatternを導出するスキル

```text
derive-validation-testpatterns
```

発火条件：

```text
「この項目定義からテストパターンを作って」
「Validation Typeに対応する境界値テストを展開して」
「constraint_overridesをテストへ反映して」
```

入力例：

```json
{
  "field_path": "fft.peak_hz",
  "validation_type": "float.measurement",
  "constraints": {
    "minimum": 0,
    "maximum": 20000
  }
}
```

スキル内部の標準導出：

```text
valid value
minimum
minimum_minus_1
maximum
maximum_plus_1
median
null
string
invalid decimal format
```

さらに、

```text
・標準TestPatternはRegistryから導出
・個別項目には差分だけを保存
・overrideがない標準パターンを重複生成しない
・ExpectedはLiteral / Reference / Derivedに分類
```

まで守らせる。

これは単なるコード生成スキルではなく、

> **項目定義の承認から、組織で品質保証済みのテストパターンを展開するスキル**

になる。

かなり「AI承認駆動開発」のど真ん中やね。笑

---

## 例6：インシデント登録スキル

```text
register-studio-incident
```

発火条件：

```text
「今回の判断をインシデントに残して」
「この改修内容を作業記録へ登録して」
「次回へ引き継げる形にして」
```

手順：

```text
1. 今回の依頼内容を抽出
2. 変更理由を抽出
3. 適用した判断軸・制約を抽出
4. 採用案・不採用案を記録
5. 修正ファイルを記録
6. テスト結果を記録
7. 未解決事項を記録
8. 次回フェーズを設定
```

出力先：

```text
data/json/01_main/studio_work_incident_data_v2.json
```

重要なのは、

```text
単なる作業日誌にしない
結果だけでなく判断理由を残す
事実とAI仮説を分ける
既存のincident_idを壊さない
```

というFRB Studio固有の作法。

これも、素のAIへ毎回説明するよりスキル化したほうが強い。

---

## 例7：AI承認差分レビュー・スキル

```text
approval-diff-review
```

発火条件：

```text
「この変更で、どの承認を外すべき？」
「意味のある差分か判定して」
「再承認が必要な範囲を出して」
```

処理：

```text
旧データ
＋
新データ
＋
制約
＋
責務
＋
Expected

↓

差分分類
```

分類結果：

```text
FORMATTING_ONLY
COMMENT_ONLY
MEANINGFUL_CHANGE
CONSTRAINT_CHANGE
RESPONSIBILITY_CHANGE
EXPECTED_CHANGE
TESTPATTERN_CHANGE
BREAKING_CHANGE
```

判断：

```text
承認維持可能
部分再承認
全体再承認
判定不能・人間協議
```

これは今話している、

> **人間が承認すべき最小の意味差分を確定する**

を、一つの再利用可能な仕事の型にしたものやね。

---

# FRB研究側にも作れる

## 例8：FRB実験ログ作成スキル

```text
create-frb-lab-note
```

発火条件：

```text
「今日の実験をLab Notesにして」
「FFT結果と体感を整理して」
「この違和感を次の実験へつなげて」
```

入力：

```text
・実験装置
・ロッド
・入力条件
・FFT結果
・体感メモ
・写真
・前回との差分
```

出力構造：

```text
何をした
観測事実
体感
数値との差分
仮説
まだ言えないこと
次の実験
```

FRB固有ルール：

```text
・体感と測定値を混同しない
・単一個体の結果をモデル全体へ一般化しない
・振動量＝感度と断定しない
・仮説には仮説ラベルを付ける
・再現条件を必ず残す
```

単なる「ブログを書いて」ではなく、

> **FRBの研究姿勢を守りながら実験ログを構造化する**

というスキルになる。

---

# SKILL.mdにすると、こんな感じ

かなり簡略化すると、こういうファイルになる。

```markdown
---
name: viewdef-review
description: >
  FRB StudioのViewDefをSchema・FieldDef・Validation Type・
  プロジェクト固有制約に基づいてレビューする。
  ViewDefの追加・変更・型変更・参照切れ確認を依頼されたときに使用する。
  実装コードのみのレビューには使用しない。
---

# ViewDef Review

## 手順

1. 対象ViewDefとSchemaを特定する
2. data_pathとfield_pathを実データへ突合する
3. typeの許容値を確認する
4. item_definition_refの参照先を確認する
5. Validation Typeとの整合性を確認する
6. 既存ViewDefとの差分を分類する
7. 承認状態への影響を判定する

## 必須制約

- ViewDefにvalidation_typeを直接保持しない
- 意味のある変更では人間承認を未承認へ戻す
- dateとdatetime混在時はdatetimeへ倒す
- 人間の視認性を最優先する

## 出力形式

- 判定: PASS / WARN / BLOCK
- 観測事実
- 違反制約
- 変更差分
- 承認影響
- 推奨修正
```

必要なら同じフォルダに、

```text
viewdef-review/
├── SKILL.md
├── references/
│   ├── viewdef-schema.json
│   └── validation-type-registry.json
├── examples/
│   └── expected-review.md
└── scripts/
    └── validate-viewdef.js
```

を置ける。公式ドキュメントでも、スキルは`SKILL.md`を入口に、テンプレート、出力例、参照資料、実行スクリプトなどを同梱できる構造になっている。([Claude][1])

---

# この記事の核心をStudioくん語に翻訳すると

この記事で問題になったのは、スキルの中身が悪いことだけではない。

```text
viewdef-review
review-view-definition
validate-viewdef
check-json-view
json-definition-review
```

みたいな似たスキルを5個作ると、Claudeが、

> 「今回どれを呼べばええねん」

となる。

エラーにはならない。

ただ、狙ったスキルが**静かに選ばれなくなる**。記事では、意味が重なる隣接スキル同士で「票の取り合い」が実際に観測されたと説明している。([Zenn][2])

なので、たぶんFRB Studioで最初にスキル化すべきなのは、大量の細粒度スキルではなく、

```text
review-studio-asset
  asset_type: viewdef
  asset_type: fielddef
  asset_type: constraint
  asset_type: responsibility
```

のような統合型……とは限らない。

ここが面白いところで、

> **何を別スキルにして、何をパラメータにするか**

自体が、責務分離の話になる。

俺の感覚では、最初の候補はこの4つくらい。

```text
review-studio-definition
derive-testpatterns
register-studio-incident
review-approval-diff
```

これは発火場面が比較的はっきり違う。

逆に、

```text
review-viewdef
review-fielddef
review-constraint
review-responsibility
```

を最初から別々に作ると、記事でいう**票の取り合い世界**へ入りそうやねぇ。笑

つまりこの記事のスキルは、

> **標準TestPatternより、むしろ「標準化されたAI作業責務」に近い**

と思う。

そして、

```text
反復して発生したか
素のAIより良くなるか
他スキルと区別できるか
誰が育てるか
```

を通過したものだけを、AIの正式な仕事として昇格させる。([Zenn][2])

これ、完全に今の俺たちの、

> 一度しか出ていない抽象化はしない
> 同じ差分が複数回出たら標準化候補
> 判断ログから制約へ昇格する

と同じ思想やと思う。**スキルとは、繰り返された判断ログから昇格した「AI作業クラス」**と見ると、めちゃくちゃ綺麗につながるで。

[1]: https://code.claude.com/docs/ja/skills?utm_source=chatgpt.com "スキルで Claude を拡張する - Claude Code Docs"
[2]: https://zenn.dev/canly/articles/43bef1eacdae44 "スキルは増やしすぎると使われなくなるのか？実測したら原因はトークンではなかった"
