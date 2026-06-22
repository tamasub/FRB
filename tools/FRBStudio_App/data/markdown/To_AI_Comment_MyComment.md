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


