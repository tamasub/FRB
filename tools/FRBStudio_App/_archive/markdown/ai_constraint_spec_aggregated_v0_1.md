# AI制約設計書 集約版

- 出力日時: 2026/6/20 9:58:42
- 対象: No-Code JSON Studio v0.3-draft
- schema_version: 0.6-footer-chat
- 件数: 12

## 基本情報

- タイトル: No-Code JSON Studio v0.3-draft AI制約設計書 集約版 v0.5-split-review-chat
- 対象: No-Code JSON Studio v0.3-draft
- Schema Version: 0.6-footer-chat
- Document Type: ai_constraint_spec_aggregated
- 元ドキュメント: No-Code JSON Studiov0.3-draft.md
- 元制約数: 84
- 集約グループ数: 12

### 集約方針

原子制約をカテゴリ単位に集約し、個別制約はサブグリッドで確認する。詳細画面では、レビュー対象（集約サマリ・対象範囲）と制約グループ会話を分離して表示する。

## 制約グループ一覧

| No | Group ID | 分類 | 制約グループ名 | 優先度 | レビュー状態 | 確認状態 | 制約数 | 集約サマリ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | APP_RUNTIME | アプリ構成 | アプリ実行・起動・常駐 | high | 集約ドラフト | 未確認 | 3 | ローカルWebアプリとしての起動、ブラウザ表示、タスクトレイ常駐をまとめた制約グループ。 |
| 2 | FILE_SECURITY | ファイル管理 | ファイル配置・安全制約 | high | 集約ドラフト | 未確認 | 9 | data/json、data/markdown、defsなどの管理フォルダーと、拡張子・パストラバーサル・保存範囲の安全制約をまとめる。 |
| 3 | VIEW_PATH | 画面定義 | View構造・JSONパス | high | 集約ドラフト | 未確認 | 10 | 1画面1グリッド、views[0]、Header/Grid section、dot pathをまとめた画面定義の核。 Detail Dialogでは、会話欄をレビュー対象と個別明細の後ろへ送るためのfooter配置も扱う。 |
| 4 | FIELD_INPUT | Field | Field Type・入力変換 | high | 集約ドラフト | 未確認 | 5 | 対応Field Type、number/boolean/select/textareaなどの入力UIと保存時変換をまとめる。 |
| 5 | GRID_SEARCH_SORT | 一覧・検索 | Grid表示・検索・ソート | high | 集約ドラフト | 未確認 | 10 | 一覧表示、列幅、number format、検索対象、検索演算子、列ヘッダーソートをまとめる。 |
| 6 | EDIT_ROW_COPY | 編集・行操作 | 編集・新規・削除・コピー | high | 集約ドラフト | 未確認 | 14 | readonly、Detail反映、新規行生成、削除確認、行コピー/貼り付けをまとめる。 |
| 7 | CHILD_ARRAY | 子配列 | 子配列表示・編集候補 | high | 集約ドラフト | 未確認 | 4 | objectArray/stringArrayの子テーブル表示と、直接編集が弱いというGAPをまとめる。 |
| 8 | SAVE_DROP_REL | 保存・関連 | 保存・Drop・view_def関連付け | high | 集約ドラフト | 未確認 | 10 | API管理ファイルの上書き保存、管理外の別名保存、Drop登録、data JSON内view_def優先をまとめる。 |
| 9 | MARKDOWN | Markdown | Markdown入出力 | medium | 集約ドラフト | 未確認 | 4 | Markdown一覧取得、読み込み、保存、Drop登録、表示中データのMarkdown出力をまとめる。 |
| 10 | KNOWN_GAPS | 未実装 | 現時点の未実装・弱い制約 | high | 集約ドラフト | 未確認 | 7 | validation.required、子配列直接編集、複数グリッド、複数View、FieldType継承、テスト生成などの未実装をまとめる。 |
| 11 | FUTURE_ADD | 追加候補 | 次に追加候補となる制約 | medium | 集約ドラフト | 未確認 | 5 | 子配列編集、required実装、FieldType継承、制約からテストパターン生成、テストコード生成をまとめる。 |
| 12 | REVIEW_POLICY | レビュー | 人間レビュー観点 | medium | 集約ドラフト | 未確認 | 3 | AIが制約と呼んだものが本当に制約か、実装都合を誤認していないか、粒度がテスト生成に使えるかを確認する。 |

## 制約グループ詳細


### 1. APP_RUNTIME：アプリ実行・起動・常駐
- 分類: アプリ構成
- 優先度: high
- レビュー状態: 集約ドラフト
- 確認状態: 未確認
- 制約数: 3

#### レビュー対象


##### 集約サマリ

ローカルWebアプリとしての起動、ブラウザ表示、タスクトレイ常駐をまとめた制約グループ。

##### 対象範囲

FRB Studioの実行形態とユーザー起動導線。

#### 含まれる個別制約

| ID | タイトル | 制約本文 |
| --- | --- | --- |
| APP-001 | ローカルWebアプリとして動作する | FRB Studioは `http://localhost:5055` で起動するローカルWebアプリである。 |
| APP-002 | 起動時にブラウザを開く | アプリ起動後、自動的にブラウザで画面を開く。 |
| APP-003 | タスクトレイ常駐する | アプリはタスクトレイに常駐し、右クリックメニューから以下を開ける。 --- |

#### 制約グループ会話


### 2. FILE_SECURITY：ファイル配置・安全制約
- 分類: ファイル管理
- 優先度: high
- レビュー状態: 集約ドラフト
- 確認状態: 未確認
- 制約数: 9

#### レビュー対象


##### 集約サマリ

data/json、data/markdown、defsなどの管理フォルダーと、拡張子・パストラバーサル・保存範囲の安全制約をまとめる。

##### 対象範囲

管理対象ファイル、保存先、安全なファイル名。

#### 含まれる個別制約

| ID | タイトル | 制約本文 |
| --- | --- | --- |
| FILE-001 | JSONデータは data/json に保存する | 対象JSONは `data/json` 配下で管理される。 |
| FILE-002 | Markdownは data/markdown に保存する | Markdownファイルは `data/markdown` 配下で管理される。 |
| FILE-003 | 画面定義JSONは defs に保存する | View定義JSONは `defs` 配下で管理される。 |
| FILE-004 | 旧 data/*.json は data/json へ初回移行する | 旧構成の `data/*.json` は、新構成の `data/json/*.json` へコピーされる。 |
| FILE-005 | 管理対象外ファイルは直接上書き保存しない | DropしたJSONを管理対象へコピーしない場合、上書き保存ではなく別名保存になる。 --- |
| SAFE-001 | JSONファイル名は `.json` のみ許可する | JSON APIで扱えるファイル名は `.json` で終わる必要がある。 |
| SAFE-002 | Markdownファイル名は `.md` または `.markdown` のみ許可する | Markdown APIで扱えるファイル名は `.md` または `.markdown` のみ許可される。 |
| SAFE-003 | パストラバーサルは禁止する | ファイル名に以下を含む場合は拒否する。 |
| SAFE-004 | API経由保存は管理対象フォルダー内に限定する | 保存先は `data/json`、`data/markdown`、`defs` の配下に限定される。 --- |

#### 制約グループ会話


### 3. VIEW_PATH：View構造・JSONパス
- 分類: 画面定義
- 優先度: high
- レビュー状態: 集約ドラフト
- 確認状態: 未確認
- 制約数: 10

#### レビュー対象


##### 集約サマリ

1画面1グリッド、views[0]、Header/Grid section、dot pathをまとめた画面定義の核。 Detail Dialogでは、会話欄をレビュー対象と個別明細の後ろへ送るためのfooter配置も扱う。

##### 対象範囲

view_defの基本構造、dataPath/fieldの参照ルール。 Detail Dialog内の表示順制御を含む。

#### 含まれる個別制約

| ID | タイトル | 制約本文 |
| --- | --- | --- |
| VIEW-001 | 現行アプリは 1画面1グリッドを前提とする | 複数グリッドではなく、主グリッド1つを扱う。 |
| VIEW-002 | 使用するViewは `views[0]` | 画面定義に複数Viewがあっても、現行アプリは先頭Viewを使用する。 |
| VIEW-003 | 画面構成は固定である | 画面は以下の構造を前提とする。 |
| VIEW-004 | Header Formは最初の form section | `type: "form"` かつ `role !== "detailOnly"` の最初のsectionをHeaderとして扱う。 |
| VIEW-005 | Gridは最初の grid section | `type: "grid"` の最初のsectionをメイングリッドとして扱う。 |
| VIEW-006 | Gridの dataPath は Array を指す必要がある | Grid section の `dataPath` が配列でない場合、読み込みエラーになる。 --- |
| PATH-001 | JSONパスは簡易 dot path とする | 対応する形式は以下。 |
| PATH-002 | bracket記法は非対応 | 以下の形式は非対応。 |
| PATH-003 | キー名にドットを含むJSONは非推奨 | dot pathで解釈するため、キー名に `.` を含む構造は避ける。 --- |
| VIEW-007 | detailFooter配置は子配列の後に描画する | Field定義に `layout.placement: "detailFooter"`、または `edit.layout.placement: "detailFooter"` を指定した場合、そのFieldは通常の詳細フォームではなく、objectArray / stringArray の子テーブル表示後に描画する。会話・コメント欄など、レビュー対象と個別明細を読んだ後に扱う入力欄に使用する。 |

#### 制約グループ会話


### 4. FIELD_INPUT：Field Type・入力変換
- 分類: Field
- 優先度: high
- レビュー状態: 集約ドラフト
- 確認状態: 未確認
- 制約数: 5

#### レビュー対象


##### 集約サマリ

対応Field Type、number/boolean/select/textareaなどの入力UIと保存時変換をまとめる。

##### 対象範囲

Field定義、入力UI、保存時の型変換。

#### 含まれる個別制約

| ID | タイトル | 制約本文 |
| --- | --- | --- |
| FIELD-001 | 対応Field Typeは固定 | 現行アプリが扱うField Typeは以下。 |
| FIELD-002 | numberは空文字なら null、入力ありなら Number変換する | number入力は保存時に数値へ変換される。 |
| FIELD-003 | booleanは select で true / false / 空 を扱う | booleanは文字列 `"true"` を true、`"false"` を false として扱う。 |
| FIELD-004 | selectは options 配列から選択する | select型は `options` 配列を選択肢として表示する。 |
| FIELD-005 | textareaは edit.height を最小高さとして扱う | `edit.height` がある場合、textareaの高さに反映する。 --- |

#### 制約グループ会話


### 5. GRID_SEARCH_SORT：Grid表示・検索・ソート
- 分類: 一覧・検索
- 優先度: high
- レビュー状態: 集約ドラフト
- 確認状態: 未確認
- 制約数: 10

#### レビュー対象


##### 集約サマリ

一覧表示、列幅、number format、検索対象、検索演算子、列ヘッダーソートをまとめる。

##### 対象範囲

メイングリッドの見え方、検索条件、並び替え。

#### 含まれる個別制約

| ID | タイトル | 制約本文 |
| --- | --- | --- |
| GRID-001 | grid.visible が false のFieldは一覧に表示しない | 未指定の場合は表示する。 |
| GRID-002 | grid.width は列幅に反映する | `grid.width` がある場合、列幅または最大幅として扱う。 |
| GRID-003 | numberは format 指定で小数桁表示できる | `format`、`grid.format`、`edit.format` により小数桁表示を行う。 --- |
| SEARCH-001 | search.visible が true のFieldのみ検索フォームに表示する | 検索対象はView定義で明示されたFieldのみ。 |
| SEARCH-002 | number検索の既定演算子は gte | number型は未指定なら `gte` として扱う。 |
| SEARCH-003 | number以外の既定演算子は contains | 文字列系は未指定なら部分一致検索。 |
| SEARCH-004 | 対応検索演算子は contains / equals / gte / lte | 検索演算子は限定される。 --- |
| SORT-001 | 一覧ヘッダークリックでソートする | 列ヘッダークリックで昇順、降順、解除を切り替える。 |
| SORT-002 | number型は数値として比較する | number型はNumber変換できる場合、数値比較する。 |
| SORT-003 | null / 空文字は後ろに並べる | 空値は非空値より後ろに配置される。 --- |

#### 制約グループ会話


### 6. EDIT_ROW_COPY：編集・新規・削除・コピー
- 分類: 編集・行操作
- 優先度: high
- レビュー状態: 集約ドラフト
- 確認状態: 未確認
- 制約数: 14

#### レビュー対象


##### 集約サマリ

readonly、Detail反映、新規行生成、削除確認、行コピー/貼り付けをまとめる。

##### 対象範囲

Detail Dialog内の編集、行のライフサイクル操作。

#### 含まれる個別制約

| ID | タイトル | 制約本文 |
| --- | --- | --- |
| EDIT-001 | readonly指定のFieldは編集不可 | 以下のいずれかが true の場合、入力不可とする。 |
| EDIT-002 | edit.visible が false のFieldは詳細画面に表示しない | Detail Dialogでは `edit.visible !== false` のFieldのみ表示する。 |
| EDIT-003 | Header Formの編集は保存時に反映される | Headerの入力値は保存前に sourceData へ反映される。 |
| EDIT-004 | Detail Dialogの編集は反映ボタンで行データへ反映される | 詳細画面の値は「反映」操作で対象行へ反映される。 --- |
| ROW-001 | 新規行は grid.fields から生成する | 新規行追加時、Grid sectionのfields定義をもとに行オブジェクトを生成する。 |
| ROW-002 | create.include false のFieldは新規行に含めない | `create.include: false` のFieldは初期生成対象から除外する。 |
| ROW-003 | defaultValue があれば優先する | `defaultValue` がある場合はその値を初期値にする。 |
| ROW-004 | defaultValue がない場合は型別既定値を使う | 既定値は以下。 --- |
| ROW-DEL-001 | 選択行のみ削除可能 | 削除は現在選択中の1行に対して行う。 |
| ROW-DEL-002 | 削除前に確認ダイアログを表示する | 削除操作には confirm を要求する。 --- |
| COPY-001 | 行単位でコピーできる | 右クリックメニューから選択行をコピーできる。 |
| COPY-002 | コピー行から新規行追加できる | コピー済み行を複製して新規行として追加できる。 |
| COPY-003 | コピー行の値を詳細ダイアログへ貼り付けできる | コピー済み行の値を、編集可能Fieldにのみ貼り付ける。 |
| COPY-004 | readonly Fieldには貼り付けない | readonly または disabled のFieldは貼り付け対象外とする。 --- |

#### 制約グループ会話


### 7. CHILD_ARRAY：子配列表示・編集候補
- 分類: 子配列
- 優先度: high
- レビュー状態: 集約ドラフト
- 確認状態: 未確認
- 制約数: 4

#### レビュー対象


##### 集約サマリ

objectArray/stringArrayの子テーブル表示と、直接編集が弱いというGAPをまとめる。

##### 対象範囲

Detail Dialog下部の子テーブル表示と将来編集。

#### 含まれる個別制約

| ID | タイトル | 制約本文 |
| --- | --- | --- |
| CHILD-001 | objectArray / stringArray は詳細画面下部に子テーブル表示する | 配列型FieldはDetail Dialogの下部にテーブルとして表示する。 |
| CHILD-002 | stringArray は # / value の2列で表示する | 文字列配列は行番号と値を表示する。 |
| CHILD-003 | objectArray はオブジェクトキーを列として表示する | objectArrayは含まれるオブジェクトのキー一覧を列として表示する。 |
| CHILD-004 | 現行実装では子配列は編集対象ではなく閲覧寄りである | 子配列はテーブル表示されるが、直接編集UIはない。 --- |

#### 制約グループ会話


### 8. SAVE_DROP_REL：保存・Drop・view_def関連付け
- 分類: 保存・関連
- 優先度: high
- レビュー状態: 集約ドラフト
- 確認状態: 未確認
- 制約数: 10

#### レビュー対象


##### 集約サマリ

API管理ファイルの上書き保存、管理外の別名保存、Drop登録、data JSON内view_def優先をまとめる。

##### 対象範囲

読み込み、保存、管理対象コピー、画面定義の決定。

#### 含まれる個別制約

| ID | タイトル | 制約本文 |
| --- | --- | --- |
| SAVE-001 | API管理ファイルは上書き保存できる | `/api/data/xxx.json` として読み込まれたデータは上書き保存できる。 |
| SAVE-002 | API管理外ファイルは別名保存する | API管理外のJSONはブラウザダウンロードとして保存する。 |
| SAVE-003 | 保存時に view_def 名を data JSON へ埋め込む | 保存時、対象データに `view_def` を付与する。 |
| SAVE-004 | 保存JSONはインデント付きで整形する | サーバー保存時は整形済みJSONとして保存する。 --- |
| DROP-001 | 画面定義JSONと対象JSONをDropできる | 画面定義JSON、対象JSONともにDrop入力を受け付ける。 |
| DROP-002 | Drop後に管理対象へコピーするか確認する | Dropしたファイルは、管理対象へコピーするかユーザー確認する。 |
| DROP-003 | 管理対象コピー後はコンボ一覧に反映する | コピー成功後、defs / data の一覧を更新する。 --- |
| REL-001 | data JSON 内の view_def を優先する | 対象JSONに `view_def` がある場合、選択中の画面定義より優先する。 |
| REL-002 | view_def がない場合はユーザー指定の画面定義を使う | 対象JSONに view_def がない場合、画面定義JSONの選択が必要。 |
| REL-003 | 対応する view_def がない場合は読み込みエラーにする | 画面定義を決定できない場合は読み込まない。 --- |

#### 制約グループ会話


### 9. MARKDOWN：Markdown入出力
- 分類: Markdown
- 優先度: medium
- レビュー状態: 集約ドラフト
- 確認状態: 未確認
- 制約数: 4

#### レビュー対象


##### 集約サマリ

Markdown一覧取得、読み込み、保存、Drop登録、表示中データのMarkdown出力をまとめる。

##### 対象範囲

Markdown Viewer / Editorとの接続。

#### 含まれる個別制約

| ID | タイトル | 制約本文 |
| --- | --- | --- |
| MD-001 | Markdownファイル一覧を取得できる | `data/markdown` 内の `.md` / `.markdown` を一覧取得する。 |
| MD-002 | Markdownを読み込みできる | API経由でMarkdown本文を取得する。 |
| MD-003 | Markdownを保存できる | API経由でMarkdown本文を保存する。 |
| MD-004 | MarkdownをDrop登録できる | MarkdownファイルをDrop登録できる。 --- |

#### 制約グループ会話


### 10. KNOWN_GAPS：現時点の未実装・弱い制約
- 分類: 未実装
- 優先度: high
- レビュー状態: 集約ドラフト
- 確認状態: 未確認
- 制約数: 7

#### レビュー対象


##### 集約サマリ

validation.required、子配列直接編集、複数グリッド、複数View、FieldType継承、テスト生成などの未実装をまとめる。

##### 対象範囲

現時点では仕様化されているが未実装、または弱い機能。

#### 含まれる個別制約

| ID | タイトル | 制約本文 |
| --- | --- | --- |
| GAP-001 | validation.required は実質未実装 | View定義に `validation.required` は存在するが、入力チェックとしてはほぼ機能していない。 |
| GAP-002 | 子配列の直接編集は未実装 | objectArray / stringArray は表示できるが、直接編集はできない。 |
| GAP-003 | 複数グリッドは未対応 | 現行は1画面1グリッド前提。 |
| GAP-004 | 複数View切替は未対応 | `views[0]` のみ使用。 |
| GAP-005 | FieldType継承 / FieldGroup継承は未実装 | 制約継承の仕組みはまだ存在しない。 |
| GAP-006 | テストパターン生成機能は未実装 | 制約からテストパターンを生成する仕組みはまだない。 |
| GAP-007 | 制約設計書そのものを扱う専用構造は未実装 | 現行はview_defを管理できるが、AI制約設計書専用の構造はまだない。 --- |

#### 制約グループ会話


### 11. FUTURE_ADD：次に追加候補となる制約
- 分類: 追加候補
- 優先度: medium
- レビュー状態: 集約ドラフト
- 確認状態: 未確認
- 制約数: 5

#### レビュー対象


##### 集約サマリ

子配列編集、required実装、FieldType継承、制約からテストパターン生成、テストコード生成をまとめる。

##### 対象範囲

将来の機能拡張バックログ。

#### 含まれる個別制約

| ID | タイトル | 制約本文 |
| --- | --- | --- |
| ADD-001 | 子配列を編集可能にする | objectArray / stringArray をDetail Dialog内で編集可能にする。 |
| ADD-002 | validation.required を実装する | required指定されたFieldは保存・反映時に空を許可しない。 |
| ADD-003 | FieldType制約継承を実装する | 例: |
| ADD-004 | 制約からテストパターンJSONを生成する | 制約定義をもとに正常系・異常系・境界値テストを生成する。 |
| ADD-005 | テストパターンからテストコードを生成する | test_patterns.json から Playwright 等のテストコードを生成する。 |

#### 制約グループ会話


### 12. REVIEW_POLICY：人間レビュー観点
- 分類: レビュー
- 優先度: medium
- レビュー状態: 集約ドラフト
- 確認状態: 未確認
- 制約数: 3

#### レビュー対象


##### 集約サマリ

AIが制約と呼んだものが本当に制約か、実装都合を誤認していないか、粒度がテスト生成に使えるかを確認する。

##### 対象範囲

制約設計書を育てるための人間レビュー方針。

#### 含まれる個別制約

| ID | タイトル | 制約本文 |
| --- | --- | --- |
| REVIEW-POINT-001 | AIが制約と呼んだものは本当に制約か確認する | 実装説明・希望・運用メモを制約と誤認していないか確認する。 |
| REVIEW-POINT-002 | 大事な制約の見落としを補う | コードから逆算できない思想由来・運用由来の制約を人間が追加する。 |
| REVIEW-POINT-003 | テストパターン生成に使える粒度に整える | 制約がExpected JSONやPlaywrightテストへ変換できる粒度か確認する。 |

#### 制約グループ会話
