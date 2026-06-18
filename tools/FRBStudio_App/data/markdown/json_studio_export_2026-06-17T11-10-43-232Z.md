# No-Code JSON Studio v0.3-draft AI制約設計書

- 出力日時: 2026/6/17 20:10:43
- 対象: No-Code JSON Studio v0.3-draft
- schema_version: 0.1-draft
- status: human_review_draft
- 件数: 40

## 基本情報
- タイトル: No-Code JSON Studio v0.3-draft AI制約設計書
- 対象: No-Code JSON Studio v0.3-draft
- Schema Version: 0.1-draft
- 状態: human_review_draft
- 生成者: ChatGPT

---

## APP-001：ローカルWebアプリとして動作する
- 分類: アプリ構成
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
FRB StudioはローカルWebアプリとして動作する。

### 根拠
index.html / app.js でクライアント動作。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## APP-002：画面構成は固定である
- 分類: アプリ構成
- 優先度: high
- 由来: 実装由来
- 承認: 未確認

### 制約
画面は Header Form + Search Form + Grid + Detail Dialog を前提とする。

### 根拠
FRB_VIEW_DEF_GENERATION_RULESでも現行アプリ前提として同構成を定義。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## VIEW-001：1画面1グリッドを前提とする
- 分類: 画面定義
- 優先度: high
- 由来: 実装由来
- 承認: 未確認

### 制約
現行アプリは1つのメイングリッドを扱う。

### 根拠
gridDef() が最初の grid section を取得する。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## VIEW-002：views[0]を使用する
- 分類: 画面定義
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
画面定義に複数Viewがあっても現行アプリは先頭Viewを使用する。

### 根拠
mainView() が viewDef.views?.[0] を使用。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## VIEW-003：Header Formは最初のform section
- 分類: 画面定義
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
type=form かつ role!=detailOnly の最初のsectionをHeaderとして扱う。

### 根拠
headerDef() の取得条件。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## VIEW-004：Gridは最初のgrid section
- 分類: 画面定義
- 優先度: high
- 由来: 実装由来
- 承認: 未確認

### 制約
type=grid の最初のsectionをメイングリッドとして扱う。

### 根拠
gridDef() の取得条件。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## PATH-001：dot pathを使う
- 分類: パス
- 優先度: high
- 由来: 実装由来
- 承認: 未確認

### 制約
dataPathとfieldは簡易dot pathで指定する。

### 根拠
getByPath / setByPath が . split で処理。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## PATH-002：bracket記法は非対応
- 分類: パス
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
items[0].name のようなbracket記法は使わない。

### 根拠
パス処理が bracket を解釈しない。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## FIELD-001：対応Field Typeは固定
- 分類: Field
- 優先度: high
- 由来: 実装由来
- 承認: 未確認

### 制約
text/number/boolean/select/datetime/textarea/objectArray/stringArray を扱う。

### 根拠
createInput / defaultForField / schema。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## FIELD-002：numberはNumber変換する
- 分類: Field
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
number型は空文字ならnull、入力ありならNumberへ変換する。

### 根拠
convertValue(type,value)。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## FIELD-003：booleanはtrue/false/空を扱う
- 分類: Field
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
boolean型はselectで true / false / 空 を扱う。

### 根拠
createInput boolean 分岐。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## GRID-001：grid.visible=falseは一覧非表示
- 分類: Grid表示
- 優先度: high
- 由来: 実装由来
- 承認: 未確認

### 制約
grid.visible が false のFieldは一覧に表示しない。

### 根拠
visibleFields filter。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## GRID-002：grid.widthを列幅に反映する
- 分類: Grid表示
- 優先度: low
- 由来: 実装由来
- 承認: 未確認

### 制約
grid.widthはth幅/td最大幅に反映する。

### 根拠
renderGrid 内 style設定。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## EDIT-001：readonlyは編集不可
- 分類: 編集
- 優先度: high
- 由来: 実装由来
- 承認: 未確認

### 制約
field.readonly または field.edit.readonly がtrueなら入力不可。

### 根拠
createInput / applyDetail / pasteCopiedRowToForm。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## EDIT-002：edit.visible=falseは詳細非表示
- 分類: 編集
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
edit.visible が false のFieldはDetail Dialogに表示しない。

### 根拠
openDetail の filter。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## SEARCH-001：search.visible=trueのみ検索対象
- 分類: 検索
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
search.visible が true のFieldのみ検索フォームに表示する。

### 根拠
renderSearch filter。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## SEARCH-002：number検索の既定はgte
- 分類: 検索
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
number型の検索演算子未指定時はgteとして扱う。

### 根拠
applySearch の operator既定値。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## SEARCH-003：文字列検索の既定はcontains
- 分類: 検索
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
number以外の検索演算子未指定時はcontainsとして扱う。

### 根拠
applySearch の operator既定値。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## SORT-001：ヘッダークリックでソートする
- 分類: ソート
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
Grid列ヘッダークリックで昇順/降順/解除を切り替える。

### 根拠
cycleSort / renderGrid。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## ROW-001：新規行はgrid.fieldsから生成する
- 分類: 行操作
- 優先度: high
- 由来: 実装由来
- 承認: 未確認

### 制約
新規行追加時、grid sectionのfieldsをもとに行オブジェクトを作る。

### 根拠
createDefaultRow。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## ROW-002：create.include=falseは新規行生成対象外
- 分類: 行操作
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
create.include=falseのFieldは新規行に含めない。

### 根拠
createDefaultRow。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## ROW-003：defaultValueを初期値にする
- 分類: 行操作
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
defaultValueがある場合、新規行の初期値として使う。

### 根拠
defaultForField。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## ROW-DEL-001：選択行のみ削除可能
- 分類: 行操作
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
削除は現在選択中の1行に対して行う。

### 根拠
deleteSelectedRow。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## COPY-001：行単位でコピーできる
- 分類: コピー
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
右クリックメニューから選択行をコピーできる。

### 根拠
copyRow / showRowContextMenu。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## COPY-002：コピー行から新規行追加できる
- 分類: コピー
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
コピー済み行を複製して新規行として追加できる。

### 根拠
addRowFromCopiedRow。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## CHILD-001：objectArray/stringArrayは子テーブル表示する
- 分類: 子配列
- 優先度: high
- 由来: 実装由来
- 承認: 未確認

### 制約
配列型FieldはDetail Dialog下部にテーブル表示する。

### 根拠
renderChildArea。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## CHILD-002：子配列の直接編集は弱い
- 分類: 子配列
- 優先度: high
- 由来: GAP
- 承認: 未確認

### 制約
現行では子配列は表示中心で、直接編集UIは未整備である。

### 根拠
renderChildArea は表示テーブルのみ生成。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## SAVE-001：API管理ファイルは上書き保存できる
- 分類: 保存
- 優先度: high
- 由来: 実装由来
- 承認: 未確認

### 制約
/api/data/xxx.json として読み込まれたデータは上書き保存できる。

### 根拠
currentDataApiUrl / saveOverwriteJson。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## SAVE-002：管理外ファイルは別名保存する
- 分類: 保存
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
API管理外ファイルはブラウザダウンロードとして保存する。

### 根拠
saveOverwriteJson fallback saveAsJson。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## SAVE-003：保存時にview_def名を埋め込む
- 分類: 保存
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
保存時、対象データに view_def を付与する。

### 根拠
ensureViewDefNameInData。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## DROP-001：画面定義JSONと対象JSONをDropできる
- 分類: Drop
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
定義JSON、対象JSONをDropで読み込める。

### 根拠
setupDropFileBox / loadFromDroppedFilesOrServer。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## DROP-002：Drop後に管理対象コピー確認する
- 分類: Drop
- 優先度: medium
- 由来: 実装由来
- 承認: 未確認

### 制約
Dropしたファイルは管理対象へコピーするか確認する。

### 根拠
confirm in loadFromDroppedFilesOrServer。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## REL-001：data JSON内view_defを優先する
- 分類: 関連
- 優先度: high
- 由来: 実装由来
- 承認: 未確認

### 制約
対象JSONにview_defがある場合はそれを優先して画面定義を決定する。

### 根拠
getDataViewDefName / loadFromServerNames。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## MD-001：表示中データをMarkdown出力できる
- 分類: Markdown出力
- 優先度: high
- 由来: 追加制約
- 承認: 未確認

### 制約
現在読み込んでいるJSON全体を、人間が読めるMarkdown形式で出力できる。

### 根拠
今回追加する機能。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## NAV-001：詳細画面で前へ/次へ移動できる
- 分類: 詳細ナビ
- 優先度: high
- 由来: 追加制約
- 承認: 未確認

### 制約
Detail Dialog上で前後の表示行へ移動できる。

### 根拠
今回追加する機能。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## REVIEW-001：各制約に承認チェックを持つ
- 分類: 承認
- 優先度: high
- 由来: 思想由来
- 承認: 未確認

### 制約
各制約は人間レビュー用の承認チェック項目を持つ。

### 根拠
AI制約設計書JSONの review_check。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## REVIEW-002：各制約に人間コメントを持つ
- 分類: 承認
- 優先度: high
- 由来: 思想由来
- 承認: 未確認

### 制約
各制約は人間が違和感・補足を書くコメント欄を持つ。

### 根拠
AI制約設計書JSONの user_comment。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## GAP-001：validation.requiredは弱い
- 分類: 未実装
- 優先度: high
- 由来: GAP
- 承認: 未確認

### 制約
validation.requiredはメタ情報として存在するが、入力チェックとしては弱い。

### 根拠
生成ルールにも将来用メタ情報と記載あり。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## GAP-002：FieldType継承は未実装
- 分類: 未実装
- 優先度: high
- 由来: GAP
- 承認: 未確認

### 制約
FieldType / FieldGroup / TableType の制約継承はまだ存在しない。

### 根拠
現行view_defは各fieldへ直接定義する構造。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

## GAP-003：テストパターン生成は未実装
- 分類: 未実装
- 優先度: high
- 由来: GAP
- 承認: 未確認

### 制約
制約からtest_patterns.jsonを生成する仕組みはまだない。

### 根拠
現行ソースに該当機能なし。

### AIメモ
ソース逆算による推定。人間レビューで確定する。
