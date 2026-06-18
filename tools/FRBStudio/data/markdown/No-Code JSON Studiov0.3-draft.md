# No-Code JSON Studio v0.3-draft

# AI制約設計書 v0.1（ソース逆算・推定版）

## 0. 位置づけ

本書は、既存ソースコードからAIが推定した制約設計書である。
正式仕様ではなく、人間レビューによって修正・追加される前提とする。

目的は、実装から読み取れる「守ろうとしている制約」を可視化し、人間が納得・修正・追加できる状態にすることである。

---

## 1. アプリ構成制約

### APP-001：ローカルWebアプリとして動作する

FRB Studioは `http://localhost:5055` で起動するローカルWebアプリである。

### APP-002：起動時にブラウザを開く

アプリ起動後、自動的にブラウザで画面を開く。

### APP-003：タスクトレイ常駐する

アプリはタスクトレイに常駐し、右クリックメニューから以下を開ける。

* FRB Studio
* data フォルダー
* json フォルダー
* markdown フォルダー
* defs フォルダー

---

## 2. ファイル管理制約

### FILE-001：JSONデータは data/json に保存する

対象JSONは `data/json` 配下で管理される。

### FILE-002：Markdownは data/markdown に保存する

Markdownファイルは `data/markdown` 配下で管理される。

### FILE-003：画面定義JSONは defs に保存する

View定義JSONは `defs` 配下で管理される。

### FILE-004：旧 data/*.json は data/json へ初回移行する

旧構成の `data/*.json` は、新構成の `data/json/*.json` へコピーされる。

### FILE-005：管理対象外ファイルは直接上書き保存しない

DropしたJSONを管理対象へコピーしない場合、上書き保存ではなく別名保存になる。

---

## 3. ファイル名安全制約

### SAFE-001：JSONファイル名は `.json` のみ許可する

JSON APIで扱えるファイル名は `.json` で終わる必要がある。

### SAFE-002：Markdownファイル名は `.md` または `.markdown` のみ許可する

Markdown APIで扱えるファイル名は `.md` または `.markdown` のみ許可される。

### SAFE-003：パストラバーサルは禁止する

ファイル名に以下を含む場合は拒否する。

* `..`
* `/`
* `\`

### SAFE-004：API経由保存は管理対象フォルダー内に限定する

保存先は `data/json`、`data/markdown`、`defs` の配下に限定される。

---

## 4. 画面定義制約

### VIEW-001：現行アプリは 1画面1グリッドを前提とする

複数グリッドではなく、主グリッド1つを扱う。

### VIEW-002：使用するViewは `views[0]`

画面定義に複数Viewがあっても、現行アプリは先頭Viewを使用する。

### VIEW-003：画面構成は固定である

画面は以下の構造を前提とする。

```text
Header Form
Search Form
Grid
Detail Dialog
```

### VIEW-004：Header Formは最初の form section

`type: "form"` かつ `role !== "detailOnly"` の最初のsectionをHeaderとして扱う。

### VIEW-005：Gridは最初の grid section

`type: "grid"` の最初のsectionをメイングリッドとして扱う。

### VIEW-006：Gridの dataPath は Array を指す必要がある

Grid section の `dataPath` が配列でない場合、読み込みエラーになる。

---

## 5. パス制約

### PATH-001：JSONパスは簡易 dot path とする

対応する形式は以下。

```text
$
$.items
experiment.memo
views.0.caption
```

### PATH-002：bracket記法は非対応

以下の形式は非対応。

```text
items[0].name
```

### PATH-003：キー名にドットを含むJSONは非推奨

dot pathで解釈するため、キー名に `.` を含む構造は避ける。

---

## 6. 入力型制約

### FIELD-001：対応Field Typeは固定

現行アプリが扱うField Typeは以下。

* text
* number
* boolean
* select
* datetime
* textarea
* objectArray
* stringArray

### FIELD-002：numberは空文字なら null、入力ありなら Number変換する

number入力は保存時に数値へ変換される。

### FIELD-003：booleanは select で true / false / 空 を扱う

booleanは文字列 `"true"` を true、`"false"` を false として扱う。

### FIELD-004：selectは options 配列から選択する

select型は `options` 配列を選択肢として表示する。

### FIELD-005：textareaは edit.height を最小高さとして扱う

`edit.height` がある場合、textareaの高さに反映する。

---

## 7. 表示制約

### GRID-001：grid.visible が false のFieldは一覧に表示しない

未指定の場合は表示する。

### GRID-002：grid.width は列幅に反映する

`grid.width` がある場合、列幅または最大幅として扱う。

### GRID-003：numberは format 指定で小数桁表示できる

`format`、`grid.format`、`edit.format` により小数桁表示を行う。

---

## 8. 編集制約

### EDIT-001：readonly指定のFieldは編集不可

以下のいずれかが true の場合、入力不可とする。

* `field.readonly`
* `field.edit.readonly`

### EDIT-002：edit.visible が false のFieldは詳細画面に表示しない

Detail Dialogでは `edit.visible !== false` のFieldのみ表示する。

### EDIT-003：Header Formの編集は保存時に反映される

Headerの入力値は保存前に sourceData へ反映される。

### EDIT-004：Detail Dialogの編集は反映ボタンで行データへ反映される

詳細画面の値は「反映」操作で対象行へ反映される。

---

## 9. 検索制約

### SEARCH-001：search.visible が true のFieldのみ検索フォームに表示する

検索対象はView定義で明示されたFieldのみ。

### SEARCH-002：number検索の既定演算子は gte

number型は未指定なら `gte` として扱う。

### SEARCH-003：number以外の既定演算子は contains

文字列系は未指定なら部分一致検索。

### SEARCH-004：対応検索演算子は contains / equals / gte / lte

検索演算子は限定される。

---

## 10. ソート制約

### SORT-001：一覧ヘッダークリックでソートする

列ヘッダークリックで昇順、降順、解除を切り替える。

### SORT-002：number型は数値として比較する

number型はNumber変換できる場合、数値比較する。

### SORT-003：null / 空文字は後ろに並べる

空値は非空値より後ろに配置される。

---

## 11. 新規行制約

### ROW-001：新規行は grid.fields から生成する

新規行追加時、Grid sectionのfields定義をもとに行オブジェクトを生成する。

### ROW-002：create.include false のFieldは新規行に含めない

`create.include: false` のFieldは初期生成対象から除外する。

### ROW-003：defaultValue があれば優先する

`defaultValue` がある場合はその値を初期値にする。

### ROW-004：defaultValue がない場合は型別既定値を使う

既定値は以下。

* number: 0
* boolean: false
* objectArray: []
* stringArray: []
* select: options[0] または空文字
* その他: 空文字

---

## 12. 削除制約

### ROW-DEL-001：選択行のみ削除可能

削除は現在選択中の1行に対して行う。

### ROW-DEL-002：削除前に確認ダイアログを表示する

削除操作には confirm を要求する。

---

## 13. コピー・貼り付け制約

### COPY-001：行単位でコピーできる

右クリックメニューから選択行をコピーできる。

### COPY-002：コピー行から新規行追加できる

コピー済み行を複製して新規行として追加できる。

### COPY-003：コピー行の値を詳細ダイアログへ貼り付けできる

コピー済み行の値を、編集可能Fieldにのみ貼り付ける。

### COPY-004：readonly Fieldには貼り付けない

readonly または disabled のFieldは貼り付け対象外とする。

---

## 14. 子配列制約

### CHILD-001：objectArray / stringArray は詳細画面下部に子テーブル表示する

配列型FieldはDetail Dialogの下部にテーブルとして表示する。

### CHILD-002：stringArray は # / value の2列で表示する

文字列配列は行番号と値を表示する。

### CHILD-003：objectArray はオブジェクトキーを列として表示する

objectArrayは含まれるオブジェクトのキー一覧を列として表示する。

### CHILD-004：現行実装では子配列は編集対象ではなく閲覧寄りである

子配列はテーブル表示されるが、直接編集UIはない。

---

## 15. 保存制約

### SAVE-001：API管理ファイルは上書き保存できる

`/api/data/xxx.json` として読み込まれたデータは上書き保存できる。

### SAVE-002：API管理外ファイルは別名保存する

API管理外のJSONはブラウザダウンロードとして保存する。

### SAVE-003：保存時に view_def 名を data JSON へ埋め込む

保存時、対象データに `view_def` を付与する。

### SAVE-004：保存JSONはインデント付きで整形する

サーバー保存時は整形済みJSONとして保存する。

---

## 16. Drop制約

### DROP-001：画面定義JSONと対象JSONをDropできる

画面定義JSON、対象JSONともにDrop入力を受け付ける。

### DROP-002：Drop後に管理対象へコピーするか確認する

Dropしたファイルは、管理対象へコピーするかユーザー確認する。

### DROP-003：管理対象コピー後はコンボ一覧に反映する

コピー成功後、defs / data の一覧を更新する。

---

## 17. data JSON と view_def の関連制約

### REL-001：data JSON 内の view_def を優先する

対象JSONに `view_def` がある場合、選択中の画面定義より優先する。

### REL-002：view_def がない場合はユーザー指定の画面定義を使う

対象JSONに view_def がない場合、画面定義JSONの選択が必要。

### REL-003：対応する view_def がない場合は読み込みエラーにする

画面定義を決定できない場合は読み込まない。

---

## 18. Markdown制約

### MD-001：Markdownファイル一覧を取得できる

`data/markdown` 内の `.md` / `.markdown` を一覧取得する。

### MD-002：Markdownを読み込みできる

API経由でMarkdown本文を取得する。

### MD-003：Markdownを保存できる

API経由でMarkdown本文を保存する。

### MD-004：MarkdownをDrop登録できる

MarkdownファイルをDrop登録できる。

---

## 19. 現時点で未実装または弱い制約

### GAP-001：validation.required は実質未実装

View定義に `validation.required` は存在するが、入力チェックとしてはほぼ機能していない。

### GAP-002：子配列の直接編集は未実装

objectArray / stringArray は表示できるが、直接編集はできない。

### GAP-003：複数グリッドは未対応

現行は1画面1グリッド前提。

### GAP-004：複数View切替は未対応

`views[0]` のみ使用。

### GAP-005：FieldType継承 / FieldGroup継承は未実装

制約継承の仕組みはまだ存在しない。

### GAP-006：テストパターン生成機能は未実装

制約からテストパターンを生成する仕組みはまだない。

### GAP-007：制約設計書そのものを扱う専用構造は未実装

現行はview_defを管理できるが、AI制約設計書専用の構造はまだない。

---

## 20. 人間レビュー観点

以下を人間がレビューする。

* AIが制約と呼んだものは、本当に制約か
* 実装都合を制約と誤認していないか
* 大事な制約を見落としていないか
* 今後追加したい機能制約は何か
* テストパターン生成に使える粒度になっているか

---

## 21. 次に追加候補となる制約

### ADD-001：子配列を編集可能にする

objectArray / stringArray をDetail Dialog内で編集可能にする。

### ADD-002：validation.required を実装する

required指定されたFieldは保存・反映時に空を許可しない。

### ADD-003：FieldType制約継承を実装する

例:

```text
NumericConstraint
↓
FrequencyConstraint
↓
peakHz
```

### ADD-004：制約からテストパターンJSONを生成する

制約定義をもとに正常系・異常系・境界値テストを生成する。

### ADD-005：テストパターンからテストコードを生成する

test_patterns.json から Playwright 等のテストコードを生成する。


