もちろん。次のチャットへそのまま貼れるように、**今回の議論で考え方がどう進化したかも含めて、長めに整理するねぇ〜。**

---

# 引継ぎメモ：項目定義Overlay／バリデーションパターンワード／項目定義Grid

## 0. 前提となる最新資材

前回までの基準ZIPは次。

```text
FRBStudio_App20260725_163402.zip
```

次チャットで実装や現物確認へ進む場合は、このZIPを基準にする。

ただし、今回のチャットではまだ実装には入っていない。

現在は、

```text
項目定義JSONの考え方
項目定義UI
型標準
バリデーションパターン
Overlay保存
```

の設計思想を整理している段階。

---

# 1. 元々の目的

最終的には、Studioくん上で次を一気通貫につなげたい。

```text
責務
↓
検証可能な保証
↓
項目定義
↓
バリデーション用サンプルデータ
↓
TestPattern + Expected
↓
テストコード
↓
Actual / Diff
```

ただし、今回の最優先は責務一覧ではなく、

> バリデーション責務が参照する項目定義の仕組みを明確にする

こと。

---

# 2. 今回の議論で大きく変わった認識

当初は、

```text
field_definitions_data_v0_1.json
```

の中へ、全項目について、

```text
field
value_type_ref
required
nullable
constraints
```

などを列挙する、完全な項目定義台帳を想定していた。

しかし今回の議論で、これは重すぎると分かった。

最新の整理は、

> **項目定義xxx.jsonは、全項目の完全定義ではない。**
> **ViewDefおよび型標準から変更した部分だけを保存するOverlayである。**

という考え方。

つまり、

```text
項目定義なし
＝ バリデーションなし
```

ではない。

```text
項目定義なし
＝ ViewDefのtypeに対応する標準バリデーションをそのまま採用
```

である。

項目定義xxx.jsonは、標準から変更したい項目だけを記録するため、非常に軽いデータになる。

---

# 3. 項目定義JSONはデータごとに作る

項目定義Overlayは、基本的に対象Dataごとに作る。

例：

```text
注文データ
→ order_field_definitions_data_v0_1.json

責務データ
→ responsibility_field_definitions_data_v0_1.json

FFTログ
→ fft_log_field_definitions_data_v0_1.json
```

対象Dataまたは対象ViewDefとの関係を持つ。

```json
{
  "target_view_def_ref": "order_view_def_v0_1",
  "field_overlays": []
}
```

ただし、フィールド名やルート構造はまだ確定していない。

候補としては、

```text
field_defs
field_overlays
overrides
```

などがある。

利用者向け名称は「項目定義」でよいが、内部構造としては、

```text
Field Definition Overlay
```

に近い。

---

# 4. 保存場所はstudio_overlays配下

項目定義Overlayは、普通の業務Dataとは混ぜたくない。

最新の合意は、

```text
studio_overlays/
└─ field_definitions/
   ├─ order_field_definitions_data_v0_1.json
   ├─ responsibility_field_definitions_data_v0_1.json
   └─ fft_log_field_definitions_data_v0_1.json
```

のように、`studio_overlays`配下で管理する方向。

ただし利用者の操作上は、Studioくんトップ画面の、

```text
Data JSONコンボ
```

から選択可能にする。

つまり、

```text
物理配置
＝ studio_overlays配下

Studioくん上の扱い
＝ Data JSONとして選択・表示・編集可能
```

という二層構造。

トップ画面では将来的に、

```text
[Data] 注文データ
[FieldDef] 注文データ 項目定義
[Rule] Foundation Rules
```

のように種別を表示してもよい。

---

# 5. 項目定義UIがこの仕組みの核心

今回の重要な気づきは、

> 項目定義xxx.jsonそのものを人間が直接編集することが主役ではない

という点。

本当に作りたいのは、Studioくん上の項目定義Grid。

項目定義画面では、

```text
対象ViewDefの項目一覧
＋
typeごとの標準値
＋
保存済み項目定義Overlay
```

を合成し、**全項目の解決済み状態**を表示する。

利用者は全項目を一覧しながら、

```text
必須入力
false → true

数値範囲
0以上 → 1以上
```

など、意味のある変更だけを行う。

その操作結果からStudioくんが、

```text
画面上の最終状態
－ 型標準
＝ 項目定義Overlayへ保存する差分
```

を計算する。

---

# 6. 項目定義Gridの表示イメージ

現在共有されている基本イメージは次。

| 項目  | 型       |  必須入力 | 数値範囲 | 標準との差分 |
| --- | ------- | ----: | ---- | ------ |
| 数量  | integer |  true | 1以上  | 2件     |
| 在庫数 | integer | false | 0以上  | なし     |
| 評価点 | integer | false | 0以上  | なし     |

重要なのは、Overlayに記録されていない項目もGridには表示されること。

たとえば在庫数と評価点はOverlayに存在しなくても、

```text
ViewDefに項目が存在する
↓
typeがinteger
↓
integer型標準を解決
↓
必須=false、0以上としてGridへ表示
```

される。

つまり、項目定義Gridは普通のJSON Gridではなく、

> **ViewDefを基礎行として生成する合成Grid**

である。

---

# 7. 型は現時点では変更不可

項目定義Gridには`型`を表示するが、現時点では変更不可とする方向。

```text
型
＝ ViewDef側の責務

必須・範囲・文字列属性など
＝ 項目定義Overlay側の責務
```

型を変えたい場合は、対象ViewDefを変更する。

この方針により、項目定義画面で扱う責務を小さくする。

将来的に型の正本をViewDefから分離する可能性はあるが、現時点では実証なき抽象化を避け、ViewDefの`type`を利用する。

---

# 8. 項目定義Gridへ表示する列候補

現時点の骨格候補。

## 8.1 常時表示する基本列

```text
項目
項目キー
型
必須入力
標準との差分
```

### 項目

ViewDefの`caption`。

### 項目キー

ViewDefの`field`。

非開発者には不要な可能性もあるが、開発者・障害調査では必要。

### 型

ViewDefの`type`。

表示のみで編集不可。

### 必須入力

編集可能。

標準値と異なる場合だけOverlayへ保存する。

### 標準との差分

```text
なし
1件
2件
```

など。

変更項目の視認性を高める。

---

## 8.2 Presence系の列

候補：

```text
必須入力
null許可
空文字許可
```

ただし、

```text
未定義
null
空文字
0
false
```

はすべて別の値として扱う。

以前の整理でも、

```json
{
  "required": true,
  "nullable": false,
  "allow_empty_string": false
}
```

のように分離する方針だった。

型によって関係しない列は、空欄または編集不可にする。

例：

```text
integer
→ 空文字許可は対象外

string
→ 空文字許可が有効
```

---

## 8.3 数値系の列

候補：

```text
数値範囲
最小値
最大値
```

### 数値範囲

人間が意味で選択する主要列。

選択肢の例：

```text
型標準
0以上
1以上
負数を許可
範囲指定
下限指定
上限指定
```

内部的にはパターンワードへ変換されるが、利用者はパターンワードを意識しない。

### 最小値・最大値

通常は型標準または選択した数値範囲から自動解決する。

例：

```text
数値範囲：0以上
最小値：0
最大値：型最大値
```

この場合、最小値・最大値は表示のみ。

```text
数値範囲：範囲指定
```

を選択した場合だけ編集可能にする。

例：

```text
最小値：5
最大値：10
```

---

## 8.4 文字列系の列

今後膨らむ候補。

```text
最小桁数
最大桁数
文字列属性
```

### 文字列属性

選択肢候補：

```text
制限なし
英字のみ
英数字
数字のみ
パターン指定
```

将来的には、

```text
英大文字のみ
英小文字のみ
前後空白を許可
前後空白を除去
メール形式
URL形式
ID形式
```

なども考えられる。

ただしv0.1から増やしすぎない。

正規表現を通常利用者へ直接編集させず、

```text
pattern_ref
```

などの承認済みパターンを選択させる方向。

---

## 8.5 日付系の列

将来的な候補：

```text
日付下限
日付上限
```

日付は、

```text
date
datetime_local
instant
```

を分ける前提。

以前の整理では、

```text
date
＝ YYYY-MM-DD、タイムゾーンなし

datetime_local
＝ ローカル日時

instant
＝ UTCまたはoffset付き絶対日時
```

としていた。

日付境界の標準テストも、

```text
下限の前日
下限当日
下限翌日
上限前日
上限当日
上限翌日
```

から自動生成できる。

---

# 9. 型によって列を条件制御する

すべての列を常時編集可能にすると、横幅も認知負荷も大きくなる。

そのため、

```text
型によって列を表示・編集制御する
```

必要がある。

例：

## integer

```text
必須入力
null許可
数値範囲
最小値
最大値
```

を有効にする。

```text
最小桁数
最大桁数
文字列属性
```

は対象外。

## string

```text
必須入力
null許可
空文字許可
最小桁数
最大桁数
文字列属性
```

を有効にする。

```text
数値範囲
最小値
最大値
```

は対象外。

## date

```text
必須入力
null許可
日付下限
日付上限
```

を有効にする。

---

# 10. 型標準という考え方

各typeには標準バリデーションを持つ。

例として今回の画面では、

```text
integer標準
必須入力：false
数値範囲：0以上
```

という状態を仮置きしていた。

ただし、これはまだ正式決定ではない。

今後、型ごとに次を決める必要がある。

```text
integer
string
decimal
floating_point
date
instant
boolean
```

たとえば整数なら、

```text
型最大値
0を許すか
負数を許すか
小数を拒否するか
文字列数値を拒否するか
```

など。

項目定義Overlayに何も記録されていない場合、この型標準がそのまま使用される。

---

# 11. 標準との差分だけ保存する

たとえばinteger標準が、

```text
必須入力：false
数値範囲：0以上
```

だとする。

利用者が数量を、

```text
必須入力：true
数値範囲：1以上
```

へ変更した場合、Overlayには数量だけを保存する。

```json
{
  "target_view_def_ref": "order_view_def_v0_1",
  "field_overlays": [
    {
      "field": "quantity",
      "overrides": {
        "required": true,
        "numeric_domain": "positive"
      }
    }
  ]
}
```

在庫数と評価点が標準どおりなら記録しない。

```text
全3項目をGrid表示
↓
Overlayに保存するのは1項目だけ
```

になる。

---

# 12. 標準に戻したら差分を削除する

Overlay方式では、標準と同じ値を保存しない。

たとえば、

```text
必須入力：false → true
```

へ変更すると、

```json
{
  "required": true
}
```

が保存される。

後で、

```text
必須入力：true → false
```

へ戻した場合、

```json
{
  "required": false
}
```

とは保存しない。

差分自体を削除する。

すべての変更を標準へ戻した場合、

```json
{
  "target_view_def_ref": "order_view_def_v0_1",
  "field_overlays": []
}
```

へ戻る。

重要ルール：

> **標準と同じ値はOverlayへ保存しない。**

---

# 13. バリデーションは再利用可能なコンポーネントとして扱う

今回の議論では、バリデーションプログラムを、

```javascript
validationComponentRegistry["studio.range.closed"] = {
  validate,
  generateTestPatterns,
  resolveExpected
};
```

のようにRegistryへ登録する構造を想定した。

これは厳密には、

```text
Strategyパターン
＋
Registryパターン
```

の組み合わせ。

```text
パターンワードで戦略を選択
↓
共通インターフェースで実行
```

する。

各バリデーションコンポーネントは、少なくとも概念上、

```text
validate
generateTestPatterns
resolveExpected
```

を持つ。

つまり、

```text
実際のバリデーション
標準TestPattern生成
Expected決定
```

を一体の品質保証単位として扱う。

---

# 14. パターンワードを品質保証の共通言語として育てる

Registryのキーである、

```text
studio.numeric.positive
studio.numeric.non_negative
studio.numeric.signed
studio.range.closed
```

などは、単なるプログラム上の文字列ではない。

将来的には、

```text
意味
対応可能な型
必要パラメータ
Validator実装
標準TestPattern
Expected生成規則
Message ID
バージョン
品質保証状態
```

を束ねる公開契約IDになる。

これを今回「パターンワード」と呼んでいた。

---

# 15. 高水準パターンと低水準パターン

今回、`studio.range.closed`を標準の中心に置くのは違うと整理した。

## 15.1 よく使う高水準パターン

人間が意味で選択できる。

```text
studio.numeric.positive
＝ 1以上
＝ 0を許可しない

studio.numeric.non_negative
＝ 0以上
＝ 0を許可する

studio.numeric.signed
＝ 負数も許可する
```

項目定義者が主に判断するのは、

```text
0を許すか
負数を許すか
```

という業務上の意味。

## 15.2 特殊寄りの汎用範囲パターン

```text
studio.range.closed
```

は、

```text
5～10だけ入力可能
1～12だけ入力可能
評価点は1～5
```

のように、下限と上限の両方が業務上意味を持つ場合に使用する。

例：

```json
{
  "validation_profile_ref": "studio.range.closed",
  "validation_parameters": {
    "minimum": 5,
    "maximum": 10
  }
}
```

このパターンはサポートするが、通常項目の標準ではなく、特殊な業務範囲で使う位置づけ。

---

# 16. 内部実装では共通範囲判定へ解決してよい

項目定義側では意味のあるパターンワードを使う。

```text
studio.numeric.positive
studio.numeric.non_negative
```

しかし内部実装では、最終的に共通Rangeコンポーネントへ解決してよい。

例：

```text
studio.numeric.positive
↓
minimum = 1
maximum = 型最大値
inclusive = true / true
↓
共通Range Validator
```

```text
studio.numeric.non_negative
↓
minimum = 0
maximum = 型最大値
inclusive = true / true
↓
共通Range Validator
```

重要なのは、

```text
項目定義側
＝ 人間が判断できる高水準な意味

内部実装側
＝ 共通化された低水準ロジック
```

と分けること。

---

# 17. 項目定義者はテストパターンを意識しない

今回の最重要原則の一つ。

> **項目定義を行う人は、テストパターンを意識しない。**

開発者は裏側のテスト生成を理解するが、通常利用者には不要。

項目定義者が考えるのは、

```text
必須か
nullを許すか
0を許すか
何桁までか
英数字だけか
5～10だけか
```

だけ。

次のような用語は通常の項目定義Gridに出さない。

```text
generateTestPatterns
resolveExpected
TestPattern ID
Expected
studio.range.closed
studio.numeric.positive
```

UIでは、

```text
1以上
0以上
範囲指定
英数字
```

のように、人間向けの言葉を表示する。

Studioくんがその選択結果を、内部パターンワードへ変換する。

---

# 18. TestPatternは項目定義から生まれる派生物

項目定義者が、

```text
integer
必須
1以上
```

と指定した場合、裏側では自動的に、

```text
未定義
null
文字列
小数
負数
0
1
型最大値
型最大値超過
```

などの標準TestPatternを生成する。

しかし、項目定義者はこれらを1件ずつ書かない。

```text
項目定義
↓
バリデーションコンポーネント解決
↓
標準TestPattern生成
↓
Expected生成
↓
テスト実行
```

という機械処理になる。

以前の項目定義構想ではValueTypeDefを承認し、各FieldDefでは適用関係だけを承認することで、人間の承認範囲を小さくすることを目指していた。今回のOverlay UIは、その考えをさらに人間向けにした形。

---

# 19. 項目定義ファイルにテスト差分を直接書かない

以前の案では、

```json
"test_pattern_customization": {
  "additions": [],
  "overrides": [],
  "exclusions": []
}
```

を項目定義JSONへ持たせる案も出た。

しかし最新の整理では、通常の項目定義Overlayからは外す方向。

理由は、項目定義者をテスト設計へ引っ張らないため。

たとえば、

```text
0を標準ではNGにしているが、この項目ではOKにしたい
```

場合は、Expectedを上書きするのではなく、

```text
数値範囲：1以上
↓
数値範囲：0以上
```

へ項目定義を変更する。

原則：

> **テスト結果を変更したいなら、項目の意味を正しく変更する。**

それでも技術的な追加テストが必要な場合は、項目定義とは別のQA資産として管理する。

---

# 20. ValueTypeDef構想との関係

以前は、

```text
ValueTypeDef
＝ 再利用可能な値契約

FieldDef
＝ 特定項目へValueTypeDefを適用
```

という構造を考えていた。

今回のOverlay構想により、FieldDef側は、

```text
全項目の完全定義
```

ではなく、

```text
型標準からの項目別差分
```

へ変わった。

ただし、ValueTypeDefや型標準カタログの考え方自体は残る。

整理すると、

```text
ViewDef
＝ 項目一覧、caption、type、画面情報

型標準／ValueType
＝ typeごとの標準的な値契約

項目定義Overlay
＝ Data固有・項目固有の変更点

Resolver
＝ ViewDef＋型標準＋Overlayを合成

項目定義Grid
＝ 解決結果を人間向けに表示・編集

Validator
＝ 解決済み定義に従って検証
```

---

# 21. 項目定義用ViewDefが必要

項目定義JSONはStudioくんでGrid表示・編集することが前提なので、対応ViewDefが必要。

ただし普通のViewDefとは少し性質が違う。

通常のViewDef：

```text
JSONに実在する行
↓
Grid表示
```

項目定義ViewDef：

```text
対象ViewDefのfields
↓
型標準を適用
↓
項目定義Overlayを重ねる
↓
解決済み全項目をGrid表示
```

つまり、項目定義用ViewDefは、

> **複数ソースを合成する特殊なGrid定義**

になる。

将来的にはデータごとにViewDefを手書きするのではなく、共通項目定義ViewDefへ対象ViewDefを渡す方式も考えられる。

例：

```json
{
  "view_def_id": "studio.field_definition_editor",
  "source_view_def_ref": "order_view_def_v0_1",
  "field_definition_data_ref": "order_field_definitions_data_v0_1"
}
```

ただし、この構造はまだ未確定。

---

# 22. 保存と表示の双方向処理

## 表示時

```text
1. 対象ViewDefから全項目を取得
2. 各項目のtypeを取得
3. type標準を取得
4. 項目定義Overlayを取得
5. 標準へOverlayを重ねる
6. 解決済み状態をGrid表示
```

## 保存時

```text
1. Grid上の編集結果を取得
2. 各項目の型標準と比較
3. 標準と同じ値を除外
4. 標準と異なる値だけOverlay化
5. 空になった項目Overlayを削除
6. 項目定義xxx.jsonへ保存
```

数式的には、

```text
表示：
標準値 ＋ Overlay ＝ 解決済み値

保存：
編集後の値 － 標準値 ＝ Overlay
```

---

# 23. 標準との差分列

項目定義Gridには、

```text
標準との差分
```

列を置く方向。

例：

```text
なし
1件
2件
```

可能なら、詳細Editorでは、

```text
必須入力
標準 false → 現在 true

数値範囲
標準 0以上 → 現在 1以上
```

のように差分内容を表示する。

また、将来的には、

```text
標準に戻す
```

操作も有効。

項目単位または属性単位で標準へ戻せるようにする。

---

# 24. 現時点のv0.1列候補

次チャットで最初にレビューしたい列候補。

```text
項目
項目キー
型
必須入力
null許可
空文字許可
数値範囲
最小値
最大値
最小桁数
最大桁数
文字列属性
標準との差分
```

ただし最初から全部実装するかは未確定。

v0.1として絞る場合の候補：

```text
項目
型
必須入力
数値範囲
最小値
最大値
最小桁数
最大桁数
文字列属性
標準との差分
```

Presenceの詳細分離は、必要性を確認しながら追加する。

---

# 25. まだ決めていない論点

次チャットで整理が必要。

## 25.1 型標準をどこへ持つか

候補：

```text
既存common_types
新しいValueTypeDef
バリデーションコンポーネントカタログ
ViewDef生成ルール
```

まだ確定していない。

## 25.2 integer標準

今回の画面では仮に、

```text
必須=false
0以上
```

としていた。

しかし正式な標準値は未決定。

```text
0以上を標準にするか
1以上を標準にするか
signedを標準にするか
```

は別途判断が必要。

## 25.3 Overlay JSONの正式スキーマ

候補：

```text
target_view_def_ref
target_data_ref
field_overlays[]
field_defs[]
overrides
numeric_domain
validation_profile_ref
validation_parameters
```

どこまで人間向け意味属性を保存し、どこから内部パターンワードを保存するか未確定。

## 25.4 ViewDef側typeとの優先関係

現時点では、

```text
type
＝ ViewDef正本、変更不可
```

とする。

将来的なFieldDef正本化は未検討。

## 25.5 null・空文字・未定義

Grid列として最初から出すか、詳細Editorへ逃がすか未決定。

## 25.6 文字列属性

```text
英字
英数字
数字のみ
```

の標準パターンワードと表示名をどう定義するか。

## 25.7 列数増加問題

数値・文字列・日付の全属性を同じGridへ出すと横幅が大きくなる。

候補：

```text
型による列表示切替
共通列＋型別詳細Editor
共通列＋サブグリッド
複数View切替
```

## 25.8 Data JSONコンボへの登録方法

`studio_overlays/field_definitions`配下のJSONを、トップ画面のData JSONコンボへどの仕組みで列挙するか。

manifestやワイルドカードとの関係も確認が必要。

---

# 26. 今回確定に近い重たい原則

```text
項目定義xxx.jsonは、
全項目の完全定義ではない。

ViewDefと型標準に対する
項目別の差分Overlayである。
```

```text
項目定義Overlayに記録がない項目も、
項目定義Gridには表示する。

記録がない項目には、
型標準を適用する。
```

```text
項目定義者は、
テストパターンを意識しない。

必須、0の扱い、桁数、文字種など、
項目の意味だけを判断する。
```

```text
標準TestPatternは、
解決済み項目定義から
機械的に生成される派生物である。
```

```text
標準と同じ値は、
項目定義Overlayへ保存しない。

標準へ戻した場合は、
保存済み差分を削除する。
```

```text
型は現時点ではViewDef側の責務とし、
項目定義Gridでは変更不可とする。
```

```text
利用者には、
studio.numeric.positiveなどの
内部パターンワードを見せない。

1以上、0以上、英数字など、
意味のある言葉を表示する。
```

```text
項目定義Overlayは
studio_overlays配下で管理する。

ただしStudioくんトップ画面の
Data JSONコンボから選択可能にする。
```

---

# 27. 今回の中心思想

今回の項目定義の核心は、JSONファイルそのものではない。

```text
全項目を一覧で見る
↓
標準状態を理解する
↓
必要な項目だけ意味を変更する
↓
変更した差分だけ保存する
↓
裏側で品質保証済みバリデーションと
標準TestPatternが自動的についてくる
```

というUI・保存モデルにある。

一言で表すなら、

> **全体を見ながら差分だけを作る、項目定義Overlay UI**

である。

これはStudioくんがこれまで目指してきた、

```text
認知可能な小さな差分
Overlay
人間承認
標準からの変更だけを管理
```

という思想と、そのままつながる。

---

# 28. 次チャットで最初に行うこと

いきなり実装へ入らない。

まず、項目定義Gridの列と操作を確定する。

開始候補：

```text
この引継ぎを前提に、
まず項目定義Grid v0.1の列構成を確定したい。

前提：
・対象ViewDefの全項目をGrid表示する
・型はViewDef由来で変更不可
・型標準を初期値として表示する
・利用者は解決済み値を編集する
・標準との差分だけ項目定義Overlayへ保存する
・標準へ戻した属性はOverlayから削除する
・項目定義者はTestPatternや内部パターンワードを意識しない

候補列：
・項目
・項目キー
・型
・必須入力
・null許可
・空文字許可
・数値範囲
・最小値
・最大値
・最小桁数
・最大桁数
・文字列属性
・標準との差分

まず、
1. v0.1で必須の列
2. 型による表示・編集制御
3. 標準値とOverlay値の見せ方
4. 標準へ戻す操作
を整理してください。

まだ実装は行わないでください。
```

これで、次は**項目定義OverlayのJSON構造より先に、核心となるGrid UIの設計**から再開できるはずやぁ〜。


---

Field
│
├─ type                        基礎型・10種類固定
│  ├─ text
│  ├─ number
│  ├─ boolean
│  ├─ select
│  ├─ datetime
│  ├─ textarea
│  ├─ objectArray
│  ├─ stringArray
│  ├─ chat
│  └─ fieldGroup
│
├─ fieldType / typeRef         意味のある共通型・追加可能
│  ├─ qa.risk
│  ├─ qa.test_pattern_id
│  └─ business.customer_id
│
└─ fieldGroupType              複数Fieldの構造型・追加可能
   ├─ studio.ExpectedDef
   ├─ studio.RuleExpectedDef
   └─ studio.ErrorExpectedDef
   
   
   