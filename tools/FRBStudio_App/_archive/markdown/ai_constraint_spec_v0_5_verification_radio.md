# No-Code JSON Studio v0.3-draft AI制約設計書 v0.5-verification-radio

- 出力日時: 2026/6/18 21:07:10
- 対象: No-Code JSON Studio v0.3-draft
- schema_version: 0.5-draft-verification-radio
- 件数: 40

## 基本情報
- タイトル: No-Code JSON Studio v0.3-draft AI制約設計書 v0.5-verification-radio
- 対象: No-Code JSON Studio v0.3-draft
- Schema Version: 0.5-draft-verification-radio
- 生成者: ChatGPT
- 実施Version: v0.5-verification-radio
- Version状態: 動作確認待ち

---

## APP-001：ローカルWebアプリとして動作する
- 分類: アプリ構成
- 優先度: medium
- 由来: 実装由来
- 承認: ◎正しい

### 制約
FRB StudioはローカルWebアプリとして動作する。

### 根拠
index.html / app.js でクライアント動作。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## APP-002：画面構成は固定である
- 分類: アプリ構成
- 優先度: high
- 由来: 実装由来
- 承認: ◎正しい

### 制約
画面は Header Form + Search Form + Grid + Detail Dialog を前提とする。

### 根拠
FRB_VIEW_DEF_GENERATION_RULESでも現行アプリ前提として同構成を定義。

### 俺コメント
将来的には、タブで増やしたいけどね。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 実施予定
- 対応予定Version: v0.5-action
- 次やること: タブ化・複数View対応の追加制約へ分離候補
- AI回答: 了解。現行制約としては固定画面構成で正しい。ただし将来構想として、複数タブ化を追加GAPに分離するのがよい。追加候補: VIEW-TAB-001 タブにより複数View/複数Gridを切り替え可能にする。
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## VIEW-001：1画面1グリッドを前提とする
- 分類: 画面定義
- 優先度: high
- 由来: 実装由来
- 承認: ◎正しい

### 制約
現行アプリは1つのメイングリッドを扱う。

### 根拠
gridDef() が最初の grid section を取得する。

### 俺コメント
将来的には、タブで増やしたいけどね。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 実施予定
- 対応予定Version: v0.5-action
- 次やること: タブ化・複数View対応の追加制約へ分離候補
- AI回答: 了解。現行は1画面1グリッド制約で正しい。将来のタブ化はこの制約を破るのではなく、上位に『タブ=複数の1画面1グリッドを束ねる』という構造を追加する方が安全。
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## VIEW-002：views[0]を使用する
- 分類: 画面定義
- 優先度: medium
- 由来: 実装由来
- 承認: ◎正しい

### 制約
画面定義に複数Viewがあっても現行アプリは先頭Viewを使用する。

### 根拠
mainView() が viewDef.views?.[0] を使用。

### 俺コメント
将来的には、タブで増やしたいけどね。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 実施予定
- 対応予定Version: v0.5-action
- 次やること: タブ化・複数View対応の追加制約へ分離候補
- AI回答: 了解。現行は views[0] 固定で正しい。将来タブ対応する場合は views[] をタブ候補として扱う制約を追加するのが自然。
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## VIEW-003：Header Formは最初のform section
- 分類: 画面定義
- 優先度: medium
- 由来: 実装由来
- 承認: ◎正しい

### 制約
type=form かつ role!=detailOnly の最初のsectionをHeaderとして扱う。

### 根拠
headerDef() の取得条件。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## VIEW-004：Gridは最初のgrid section
- 分類: 画面定義
- 優先度: high
- 由来: 実装由来
- 承認: ◎正しい

### 制約
type=grid の最初のsectionをメイングリッドとして扱う。

### 根拠
gridDef() の取得条件。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## PATH-001：dot pathを使う
- 分類: パス
- 優先度: high
- 由来: 思想由来
- 承認: ◎正しい

### 制約
dataPathとfieldは簡易dot pathで指定する。

### 根拠
getByPath / setByPath が . split で処理。

### 俺コメント
これ最高。俺の理想形。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 人間確認待ち
- 対応予定Version: v0.5-action
- AI回答: これは思想由来制約として確定寄り。dot path はAI生成・人間レビュー・JSON差分管理の相性が良い。理想形として明記してよい。
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## PATH-002：bracket記法は非対応
- 分類: パス
- 優先度: medium
- 由来: 実装由来
- 承認: ★足りない

### 制約
items[0].name のようなbracket記法は使わない。

### 根拠
パス処理が bracket を解釈しない。

### 俺コメント
補足説明必要

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 人間確認待ち
- 対応予定Version: v0.5-action
- AI回答: 補足が必要。bracket記法非対応は単なる不足ではなく、dot pathへ寄せる設計判断でもある。配列要素を直接指すのではなく、GridのdataPathで配列を指定し、fieldは行内相対pathとして扱う、という説明を追加するとよい。
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## FIELD-001：対応Field Typeは固定
- 分類: Field
- 優先度: high
- 由来: 実装由来
- 承認: ★足りない

### 制約
text/number/boolean/select/datetime/textarea/objectArray/stringArray を扱う。

### 根拠
createInput / defaultForField / schema。

### 俺コメント
select　の全部見えるモードの話は？

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 人間確認待ち
- 対応予定Version: v0.5-action
- AI回答: 指摘どおり不足。Field type は select のままで、表示制御として edit.control を追加するのがよい。追加制約候補: FIELD-004 select型は edit.control により combobox/listbox を選択できる。listbox指定時は候補を常時表示する。
- 確認対象Version: v0.3-draft
- 動作確認: 未確認
- 実装済（旧項目・非表示）: false

## FIELD-002：numberはNumber変換する
- 分類: Field
- 優先度: medium
- 由来: 実装由来
- 承認: ◎正しい

### 制約
number型は空文字ならnull、入力ありならNumberへ変換する。

### 根拠
convertValue(type,value)。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## FIELD-003：booleanはtrue/false/空を扱う
- 分類: Field
- 優先度: medium
- 由来: 実装由来
- 承認: ◎正しい

### 制約
boolean型はselectで true / false / 空 を扱う。

### 根拠
createInput boolean 分岐。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## GRID-001：grid.visible=falseは一覧非表示
- 分類: Grid表示
- 優先度: high
- 由来: 実装由来
- 承認: ◎正しい

### 制約
grid.visible が false のFieldは一覧に表示しない。

### 根拠
visibleFields filter。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## GRID-002：grid.widthを列幅に反映する
- 分類: Grid表示
- 優先度: low
- 由来: 実装由来
- 承認: ★足りない

### 制約
grid.widthはth幅/td最大幅に反映する。

### 根拠
renderGrid 内 style設定。

### 俺コメント
言葉足りてないかも

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 人間確認待ち
- 対応予定Version: v0.5-action
- AI回答: 言葉を補った方がよい。grid.width は『列幅の目安』であり、th/tdの表示幅・最大幅に反映する。ただし内容が長い場合の折返し/省略はCSS側の制御に依存する、と書くと安全。
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## EDIT-001：readonlyは編集不可
- 分類: 編集
- 優先度: high
- 由来: 実装由来
- 承認: ★足りない

### 制約
field.readonly または field.edit.readonly がtrueなら入力不可。

### 根拠
createInput / applyDetail / pasteCopiedRowToForm。

### 俺コメント
field.readonly 、 field.edit.readonly 違いは？

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 人間確認待ち
- 対応予定Version: v0.5-action
- AI回答: 整理すると、field.readonly はその項目の全体readonly。field.edit.readonly はDetail/Headerなど編集画面上のreadonly。現状ではほぼ同じ効き方だが、将来Grid直接編集が入ると差が出る。field.readonly=trueなら全編集経路で不可、edit.readonly=trueなら詳細編集だけ不可、が自然。
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## EDIT-002：edit.visible=falseは詳細非表示
- 分類: 編集
- 優先度: medium
- 由来: 実装由来
- 承認: ◎正しい

### 制約
edit.visible が false のFieldはDetail Dialogに表示しない。

### 根拠
openDetail の filter。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## SEARCH-001：search.visible=trueのみ検索対象
- 分類: 検索
- 優先度: medium
- 由来: 実装由来
- 承認: ★足りない

### 制約
search.visible が true のFieldのみ検索フォームに表示する。

### 根拠
renderSearch filter。

### 俺コメント
補足：たとえば複数行テキストエリア項目の場合は、検索条件の項目としては、高さは他の項目と同じ高さにする。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 人間確認待ち
- 対応予定Version: v0.5-action
- AI回答: 補足として正しい。検索フォームではtextarea項目でも通常入力と同じ高さで表示する制約を追加した方がよい。検索UIは編集UIではなく条件入力UIなので、edit.heightを引き継がないのが自然。
- 確認対象Version: v0.3-draft
- 動作確認: 未確認
- 実装済（旧項目・非表示）: false

## SEARCH-002：number検索の既定はgte
- 分類: 検索
- 優先度: medium
- 由来: 実装由来
- 承認: ★足りない

### 制約
number型の検索演算子未指定時はgteとして扱う。

### 根拠
applySearch の operator既定値。

### 俺コメント
まずはＯＫだが、検索のさせ方は保留。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 人間確認待ち
- 対応予定Version: v0.5-action
- AI回答: 保留でOK。number検索の既定gteは現状仕様として残しつつ、将来は検索演算子を画面で選べるようにする余地がある。追加候補: SEARCH-004 検索条件ごとに operator をUI選択可能にする。
- 確認対象Version: v0.3-draft
- 動作確認: 未確認
- 実装済（旧項目・非表示）: false

## SEARCH-003：文字列検索の既定はcontains
- 分類: 検索
- 優先度: medium
- 由来: 実装由来
- 承認: ★足りない

### 制約
number以外の検索演算子未指定時はcontainsとして扱う。

### 根拠
applySearch の operator既定値。

### 俺コメント
テキストボックスはcontains。
日付はエクセルの日付欄のフィルター機能をつけたい

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 人間確認待ち
- 対応予定Version: v0.5-action
- AI回答: テキストはcontainsでOK。日付は別制約として切り出すべき。追加候補: SEARCH-DATE-001 datetime型はExcel風の日付フィルター（期間、当日、以降、以前）を指定できる。
- 確認対象Version: v0.3-draft
- 動作確認: 未確認
- 実装済（旧項目・非表示）: false

## SORT-001：ヘッダークリックでソートする
- 分類: ソート
- 優先度: medium
- 由来: 実装由来
- 承認: ◎正しい

### 制約
Grid列ヘッダークリックで昇順/降順/解除を切り替える。

### 根拠
cycleSort / renderGrid。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## ROW-001：新規行はgrid.fieldsから生成する
- 分類: 行操作
- 優先度: high
- 由来: 実装由来
- 承認: ◎正しい

### 制約
新規行追加時、grid sectionのfieldsをもとに行オブジェクトを作る。

### 根拠
createDefaultRow。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## ROW-002：create.include=falseは新規行生成対象外
- 分類: 行操作
- 優先度: medium
- 由来: 実装由来
- 承認: ◎正しい

### 制約
create.include=falseのFieldは新規行に含めない。

### 根拠
createDefaultRow。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## ROW-003：defaultValueを初期値にする
- 分類: 行操作
- 優先度: medium
- 由来: 実装由来
- 承認: ◎正しい

### 制約
defaultValueがある場合、新規行の初期値として使う。

### 根拠
defaultForField。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## ROW-DEL-001：選択行のみ削除可能
- 分類: 行操作
- 優先度: medium
- 由来: 実装由来
- 承認: ◎正しい

### 制約
削除は現在選択中の1行に対して行う。

### 根拠
deleteSelectedRow。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## COPY-001：行単位でコピーできる
- 分類: コピー
- 優先度: medium
- 由来: 実装由来
- 承認: ★足りない

### 制約
右クリックメニューから選択行をコピーできる。

### 根拠
copyRow / showRowContextMenu。

### 俺コメント
選択行をコピーして、そのまま新規登録画面に遷移したい。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 人間確認待ち
- 対応予定Version: v0.5-action
- AI回答: その運用なら制約名を広げた方がよい。『行コピー』だけではなく『コピー行を元に新規登録画面を開く』が本命。追加候補: COPY-003 選択行を複製し、Detail Dialogを新規行モードで開ける。
- 確認対象Version: v0.3-draft
- 動作確認: 未確認
- 実装済（旧項目・非表示）: false

## COPY-002：コピー行から新規行追加できる
- 分類: コピー
- 優先度: medium
- 由来: 実装由来
- 承認: ×違う

### 制約
コピー済み行を複製して新規行として追加できる。

### 根拠
addRowFromCopiedRow。

### 俺コメント
COPY-001に記載

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 人間確認待ち
- 対応予定Version: v0.5-action
- AI回答: 了解。COPY-002はCOPY-001へ統合でよい。現状の制約分割が細かすぎた。v0.2ではCOPY-002を廃止候補または統合扱いにする。
- 確認対象Version: v0.3-draft
- 動作確認: 未確認
- 実装済（旧項目・非表示）: false

## CHILD-001：objectArray/stringArrayは子テーブル表示する
- 分類: 子配列
- 優先度: high
- 由来: 実装由来
- 承認: ◎正しい

### 制約
配列型FieldはDetail Dialog下部にテーブル表示する。

### 根拠
renderChildArea。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## CHILD-002：子配列の直接編集は弱い
- 分類: 子配列
- 優先度: high
- 由来: GAP
- 承認: ★足りない

### 制約
現行では子配列は表示中心で、直接編集UIは未整備である。

### 根拠
renderChildArea は表示テーブルのみ生成。

### 俺コメント
編集できるようにしてほしい
制約なにかつけないといけないことあればおしえて

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 人間確認待ち
- 対応予定Version: v0.5-action
- AI回答: 子配列編集には制約が必要。最低限、追加/削除/セル編集/反映/キャンセルの操作単位、objectArrayとstringArrayの扱い、readonly時は編集不可、親行反映時に子配列も保存対象、を定義した方がよい。追加候補: CHILD-EDIT-001 子配列はDetail Dialog内で行追加・削除・セル編集できる。
- 確認対象Version: v0.3-draft
- 動作確認: 未確認
- 実装済（旧項目・非表示）: false

## SAVE-001：API管理ファイルは上書き保存できる
- 分類: 保存
- 優先度: high
- 由来: 実装由来
- 承認: ◎正しい

### 制約
/api/data/xxx.json として読み込まれたデータは上書き保存できる。

### 根拠
currentDataApiUrl / saveOverwriteJson。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## SAVE-002：管理外ファイルは別名保存する
- 分類: 保存
- 優先度: medium
- 由来: 実装由来
- 承認: ◎正しい

### 制約
API管理外ファイルはブラウザダウンロードとして保存する。

### 根拠
saveOverwriteJson fallback saveAsJson。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## SAVE-003：保存時にview_def名を埋め込む
- 分類: 保存
- 優先度: medium
- 由来: 実装由来
- 承認: ★足りない

### 制約
保存時、対象データに view_def を付与する。

### 根拠
ensureViewDefNameInData。

### 俺コメント
管理対象外のファイルの場合は対象外。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 人間確認待ち
- 対応予定Version: v0.5-action
- AI回答: その通り。view_def埋め込みは管理対象JSONに対する保存時のみ対象にする、という条件を明記するべき。管理対象外のブラウザダウンロード保存では強制付与しない。
- 確認対象Version: v0.3-draft
- 動作確認: 未確認
- 実装済（旧項目・非表示）: false

## DROP-001：画面定義JSONと対象JSONをDropできる
- 分類: Drop
- 優先度: medium
- 由来: 実装由来
- 承認: ◎正しい

### 制約
定義JSON、対象JSONをDropで読み込める。

### 根拠
setupDropFileBox / loadFromDroppedFilesOrServer。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## DROP-002：Drop後に管理対象コピー確認する
- 分類: Drop
- 優先度: medium
- 由来: 実装由来
- 承認: ◎正しい

### 制約
Dropしたファイルは管理対象へコピーするか確認する。

### 根拠
confirm in loadFromDroppedFilesOrServer。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## REL-001：data JSON内view_defを優先する
- 分類: 関連
- 優先度: high
- 由来: 実装由来
- 承認: ★足りない

### 制約
対象JSONにview_defがある場合はそれを優先して画面定義を決定する。

### 根拠
getDataViewDefName / loadFromServerNames。

### 俺コメント
あえて言うと？定義ファイルがｄｒｏｐされたらそれを優先する。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 人間確認待ち
- 対応予定Version: v0.5-action
- AI回答: 優先順位の制約が不足。推奨は 1) Dropされたview_def 2) data JSON内view_def 3) 画面で選択中のview_def の順。Dropはユーザーの明示操作なので最優先でよい。
- 確認対象Version: v0.3-draft
- 動作確認: 未確認
- 実装済（旧項目・非表示）: false

## MD-001：表示中データをMarkdown出力できる
- 分類: Markdown出力
- 優先度: high
- 由来: 追加制約
- 承認: ◎正しい

### 制約
現在読み込んでいるJSON全体を、人間が読めるMarkdown形式で出力できる。

### 根拠
今回追加する機能。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 未確認
- 実装済（旧項目・非表示）: false

## NAV-001：詳細画面で前へ/次へ移動できる
- 分類: 詳細ナビ
- 優先度: high
- 由来: 追加制約
- 承認: ◎正しい

### 制約
Detail Dialog上で前後の表示行へ移動できる。

### 根拠
今回追加する機能。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 確認済み
- 実装済（旧項目・非表示）: false

## REVIEW-001：各制約に承認チェックを持つ
- 分類: 承認
- 優先度: high
- 由来: 思想由来
- 承認: ×違う

### 制約
各制約は人間レビュー用の承認チェック項目を持つ。

### 根拠
AI制約設計書JSONの review_check。

### 俺コメント
これは、制約Jsonだけの話で、No-Code JSON Studiov0.3-draftの話ではない。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 人間確認待ち
- 対応予定Version: v0.5-action
- AI回答: 指摘どおり。これはNo-Code JSON Studio本体制約ではなく、AI制約設計書データ形式の制約。カテゴリを『AI制約設計書』へ移すか、targetを分けるべき。
- 確認対象Version: v0.3-draft
- 動作確認: 対象外
- 実装済（旧項目・非表示）: false

## REVIEW-002：各制約に人間コメントを持つ
- 分類: 承認
- 優先度: high
- 由来: 思想由来
- 承認: ×違う

### 制約
各制約は人間が違和感・補足を書くコメント欄を持つ。

### 根拠
AI制約設計書JSONの user_comment。

### 俺コメント
これは、制約Jsonだけの話で、No-Code JSON Studiov0.3-draftの話ではない。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 人間確認待ち
- 対応予定Version: v0.5-action
- AI回答: 指摘どおり。これもNo-Code JSON Studio本体制約ではなく、AI制約設計書JSONのメタ制約。v0.2では本体制約とレビュー用データ制約を分離する。
- 確認対象Version: v0.3-draft
- 動作確認: 対象外
- 実装済（旧項目・非表示）: false

## GAP-001：validation.requiredは弱い
- 分類: 未実装
- 優先度: high
- 由来: GAP
- 承認: △半分正しい

### 制約
validation.requiredはメタ情報として存在するが、入力チェックとしては弱い。

### 根拠
生成ルールにも将来用メタ情報と記載あり。

### 俺コメント
機能追加予定項目。現状対策不要。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- AI状態: ai_answered
- 次の状態（AI記入）: 人間確認待ち
- 対応予定Version: v0.5-action
- AI回答: 了解。現状対策不要なら『未実装GAP』ではなく『将来追加予定』として扱うのがよい。今すぐの不具合ではなく、機能拡張バックログに分類する。
- 確認対象Version: v0.3-draft
- 動作確認: 未確認
- 実装済（旧項目・非表示）: false

## GAP-002：FieldType継承は未実装
- 分類: 未実装
- 優先度: high
- 由来: GAP
- 承認: ◎正しい

### 制約
FieldType / FieldGroup / TableType の制約継承はまだ存在しない。

### 根拠
現行view_defは各fieldへ直接定義する構造。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 未確認
- 実装済（旧項目・非表示）: false

## GAP-003：テストパターン生成は未実装
- 分類: 未実装
- 優先度: high
- 由来: GAP
- 承認: ◎正しい

### 制約
制約からtest_patterns.jsonを生成する仕組みはまだない。

### 根拠
現行ソースに該当機能なし。

### AIメモ
ソース逆算による推定。人間レビューで確定する。

### その他
- 確認対象Version: v0.3-draft
- 動作確認: 未確認
- 実装済（旧項目・非表示）: false
