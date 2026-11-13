# Copilotくんへ — FRB Smart Search JS 共通部品の引継ぎ（v0.1）

**依頼：既存の業務アプリへ「入力することが楽しい」Smart Searchを組み込みたい。**

このドキュメントは会社Copilot等の実装担当AIにそのまま渡す引継ぎ指示書です。**最初にこの文章と、同じフォルダー内の `FRB_SmartSearch_JS_v0_1/` を確認してください。** 新しい業務アプリの画面・データ構造は自由ですが、ここで定義する最小項目契約と操作・検索の意味を守ってください。利用する資料・コードは所属組織の利用条件と承認を確認し、許可されたものだけ利用してください。

## 1. まず実施してほしいこと

| 順番 | 作業 | 完了条件 |
| --- | --- | --- |
| 1 | 最小項目定義を業務アプリから作る | `field` / `caption` / `type` / 必要なら `options` が揃う |
| 2 | JS部品を画面に読み込む | `FRBSmartSearch.create({ fields })` がエラーなく実行できる |
| 3 | HTML入力欄と補完機能を接続する | `/`・右クリック・候補絞り込み・Tab/Enter/→確定が使える |
| 4 | 検索ボタンを業務アプリ側へ接続する | `smart.filter(rows, query)` で結果を画面に表示できる |
| 5 | 必要なら登録式の履歴を接続する | データセットを分け、登録・呼出・並べ替え・削除ができる |
| 6 | 同梱テストで検証する | 成功・失敗・未対応を表で報告する |

**重要：** Pythonを使った業務アプリでも、HTML/WebView側の検索UIと評価はJSで実現できます。PythonでSQLiteを使っている場合は、SQL変換を別責務として設計してください（この部品はWHERE句を生成しません）。

## 2. 納品した部品一覧

同じフォルダーの `FRB_SmartSearch_JS_v0_1/` が**既存Studioから切り出した試作パッケージ**です。Studioの本体コードはこの作業では変更していません。

| ファイル | 役割 | 使い方 |
| --- | --- | --- |
| `js/smart_search_engine.js` | 検索式Parser・AST・JSON行の評価 | 必須 |
| `js/studio_smart_search_editor.js` | `/`、候補表示、選択肢補完 | 画面補完を使う場合は必須 |
| `js/frb_smart_search_api.js` | **新設した外部アプリ向け公開インターフェース** | 必須 |
| `frb_smart_search.css` | Studio固有の `#searchSection` に依存しない候補UI | 画面補完を使う場合は必須 |
| `js/studio_smart_search_history.js` | 登録式の履歴・並べ替え・削除 | 履歴を使う場合のみ |
| `fields.example.json` | 最小項目定義の例 | 参照用 |
| `demo.html` | Studioなしで動く独立画面サンプル | **最初に動作確認** |
| `test_portable.mjs` | Nodeの公開API契約テスト | `node --test test_portable.mjs` |

スクリプトの読み込み順： **engine → editor → history（使う場合）→ api** 。これらはブラウザーの通常の `<script>` 読み込みを前提とし、npmやPythonのインストールは不要です。

## 3. 最小の「ViewDef相当」インターフェース

フルViewDefやStudioのFieldDefは不要です。業務アプリが**次の最小項目定義の配列**だけ渡せば動くことを目指しています。

| プロパティ | 必須 | 意味 | 例 |
| --- | --- | --- | --- |
| `field` | ○ | JSON行のデータ項目キー。入れ子は `owner.name` のように指定 | `priority` |
| `caption` | ○（省略時はfield） | 候補に表示する名前・検索式の項目名 | `優先度` |
| `type` | ○（省略時はstring） | 検索時の型 | `select` |
| `options` | 選択肢が必要な場合 | 候補と内部値の対応。`[{value,label}]` | `[{"value":"high","label":"高"}]` |
| `value_family` / `validation_type` | 省略可 | 既存Parserとの高度な型互換用 | `number` |

代表型：`string` / `number` / `date` / `datetime` / `instant` / `boolean` / `select`。`text` / `integer` / `float` / `decimal` / `enum` も受付。項目IDは一意にする。同じ表示名が複数ある場合は、検索式で項目IDを使用する。

```javascript
const fields = [
  {field:'title', caption:'タイトル', type:'string'},
  {field:'priority', caption:'優先度', type:'select', options:[
    {value:'high',label:'高'}, {value:'medium',label:'中'}, {value:'low',label:'低'}
  ]},
  {field:'count', caption:'件数', type:'number'},
  {field:'enabled', caption:'有効', type:'boolean'}
];
```

**注意：** `field` はデータJSONのパスと一致させる。このv0.1の部品には、別名のDB列への自動マッピングはありません。データや各アプリのViewDefから最小定義への変換は、**ホストアプリの責務**です。

## 4. 公開API（今回新設）

| API | 入力 | 出力 / 用途 |
| --- | --- | --- |
| `FRBSmartSearch.create({fields})` | 最小項目定義 | 検索部品インスタンス |
| `smart.parse(query)` | 検索文字列 | AST。構文エラーの場合は `code` / `offset` を持つ例外 |
| `smart.match(row, queryOrAst)` | 1件のJSON行・検索式またはAST | `true` / `false` |
| `smart.filter(rows, query)` | JSON行配列・検索式 | 絞り込まれた行配列。元の行を変更しない |
| `smart.getFields()` | なし | 正規化済みの項目配列 |
| `smart.attach({input, host, ...})` | HTML要素・任意の履歴要素 | IntelliSenseの画面接続 |

```javascript
const smart = FRBSmartSearch.create({fields});

// StudioもPythonも知らない。普通のJSの配列を検索する。
const rows = [
  {title:'FRB Launch',priority:'high',count:3,enabled:true},
  {title:'FRB Studio',priority:'low',count:5,enabled:false}
];
const found = smart.filter(rows, '優先度=高 件数=2..5');
// 期待：FRB Launch の1件
```

HTML画面の接続は以下。`host` は `input` と補完ポップアップを収めるコンテナーで、CSSから `.frb-smart-search-host` を付与します。

```javascript
smart.attach({
  input: document.getElementById('query'),
  host: document.getElementById('searchHost'),
  searchButton: document.getElementById('searchBtn'),
  historyRegisterButton: document.getElementById('registerBtn'),
  historyOpenButton: document.getElementById('historyBtn'),
  getDataKey: () => currentDatasetId
});
```

履歴を使わない場合、`searchButton` 以下は省略できます。**検索実行（ボタンを押したとき／候補が開いていないときのEnter）はホストアプリが担当**してください。補完表示中のEnterは先に補完確定が処理されるよう、他のグローバルキーハンドラとの順序を確認してください。

## 5. 検索言語の責務

| 検索式 | 期待する意味 |
| --- | --- |
| `aaa bbb` | 空白区切りAND |
| `aaa or bbb` | OR（大小文字無視） |
| `(aaa or bbb) ccc` | ORグループとcccのAND |
| `((aaa or bbb) (ccc or ddd))` | 括弧の入れ子。**括弧 > AND > OR** |
| `タイトル=Studio` | 文字列の部分一致 |
| `タイトル==Studio` | 文字列の完全一致 |
| `優先度=高` | 選択肢ラベルを内部値 `high` と照合 |
| `件数=2..5` | 2以上5以下（両端含む） |
| `件数>=2` / `件数=>2` | 2以上、同じ意味 |
| `件数<=5` / `件数=<5` | 5以下、同じ意味 |
| `件数!=2` / `件数=!2` | 2以外（**NULL・空値は一致とみなさない**） |
| `"Flux A">=0.1` | 空白を含む表示名を引用符で指定 |
| `"重要 案件"` | 空白を含む全文検索語を1つにする |

型別の `=`：文字列は部分一致、数値・日付・boolean・selectは一致。大小・範囲比較は数値と日付系のみ。**項目指定なしの全文検索はJSON行内の子オブジェクト・子配列も含め、文字列値を横断検索**する（`fields` で指定された列だけに限定されるわけではない）。

## 6. IntelliSense / キー文化（FRB Launchを継承）

| 操作 | 期待する動作 |
| --- | --- |
| 検索欄で `/` | カーソルの位置を問わず項目一覧を開く。`/` は検索文字として残さない |
| 検索欄で右クリック | `/` と同じ項目候補一覧を開く |
| 候補一覧の検索ボックス | 候補を部分一致で絞り込む |
| `↑ / ↓` | 現在選択中の候補を移動 |
| **`Tab / Enter / →`** | **すべて同じ候補確定** |
| Combo/Booleanの項目確定 | 値候補へ連続遷移 |
| 値直後の `/` | `/` を消費し、次の項目確定時に半角空白を挿入 |
| `Esc` | 候補を閉じる |
| 候補が閉じているときのEnter | アプリ側の通常検索実行 |

履歴：登録ボタンによる**明示的な登録**。キーはデータセットごとに分離。登録済み式の呼出・上下移動・削除。通常はブラウザーの `localStorage` を使用し、禁止環境では現在セッション内のメモリ保存へフォールバックする（再起動後の永続化なし）。業務データや機密情報を検索式に含む場合、履歴の保存可否は会社の運用ルールに従ってください。

## 7. 外部アプリで独立して動かす最初の手順

1. パッケージ内 `demo.html` をブラウザーまたは許可されたローカルWebサーバーで開く。
2. `優先度=高 件数=2..5` を入力し、サンプルの結果が2件になることを確認する。
3. 検索欄で `/` を押し、候補検索欄に `優先` と入力し、Tab / Enter / →のいずれかで `優先度=` を確定する。
4. `高` を候補から確定し、検索実行する。
5. 履歴登録 → ▼ → 呼び出し → 並べ替え → 削除を確認する。
6. 実際の業務アプリの項目定義・JSON行へ差し替える。`getDataKey` はデータセット固有値にする。

**Pythonアプリの場合：** UIがHTML/JavaScriptなら上記部品をそのまま読み込めます。Pythonバックエンドには検索文字列や解析済みASTを渡すなど、既存システムの構成に合わせて接続してください。PythonのTkinter等のネイティブUIでは、ブラウザーDOMがないためIntelliSense表示部分をそのまま流用できません。

## 8. テストパターン / Expected

| No | 入力・操作 | Expected |
| --- | --- | --- |
| T01 | `優先度=高 件数=2..5` | 該当JSON行のみ |
| T02 | `(aaa or bbb) ccc` | ORグループとcccのAND |
| T03 | `件数=2..5` | 2および5を含み、範囲外を除外 |
| T04 | `件数>=2` / `件数=>2` | 同一結果 |
| T05 | `件数!=2` | 2以外。ただしNULLは除外 |
| T06 | 項目名が重複 | 表示名だけなら `AMBIGUOUS_FIELD`、ID指定なら成功 |
| T07 | 存在しない項目 | `UNKNOWN_FIELD` を返し、勝手に全件検索しない |
| T08 | 範囲 `件数=9..2` | `REVERSED_RANGE` のエラー |
| T09 | `/` → 項目選択 | スラッシュが残らず `項目名=` を入力 |
| T10 | 値の直後に `/` → 次項目 | 間に半角スペースを1つ追加 |
| T11 | 候補表示中のTab/Enter/→ | 同じ確定結果、通常Enter検索は走らない |
| T12 | 履歴登録→データセット切替 | 履歴が混在しない |

## 9. 現状の境界・残課題（必ず確認）

| 項目 | 現状 | 担当 / 注意 |
| --- | --- | --- |
| WHERE句生成 | **未実装** | SQL Adapterは別責務。ユーザー入力を直接SQL連結しない。列名はホワイトリスト、値はパラメータ化する |
| データソース | JSのオブジェクト配列を評価 | DBを直接問い合わせる場合はPython側などで再実装を検討 |
| Studioの個別検索欄とのAND | 元のStudioでは `SearchFilter.apply` が担当 | 外部アプリではホスト側で組み合わせる |
| Markdownの `？` ヘルプ | Studio専用Markdownレンダラーに接続 | **この汎用パッケージv0.1には未組込**。必要なら別UI部品として追加 |
| UIの複数インスタンス | 元のPopupは固定IDを使用 | **1ページ1検索欄を前提**。複数欄はID採番改修が必要 |
| フルテキスト対象 | ネストした文字列値を横断 | 全項目を検索したくない場合はParser側の責務拡張が必要 |
| 丸め誤差・大規模DB | JS Number / 配列走査 | 大量データ・高精度小数は別途性能・精度設計が必要 |
| WebView / 会社実機 | この環境では未検証 | 業務アプリのキーボードイベント優先順位、レイアウト、保存制限を確認 |
| 契約・許諾 | 社内承認とは別 | 社外ソース・仕様の利用可否は会社規程に従う。「社内Copilot生成」だけで承認済みにはならない |

## 10. 作業報告の書き方（重要・ユーザーの好み）

**長い箇条書きではなく、ChatGPTで説明するような「短い見出し＋Markdown表」を優先してください。** 特に設計・インシデント・実装報告・テスト結果を表にしてください。

| 報告対象 | 書き方 |
| --- | --- |
| 実装内容 | `対象｜変更点｜理由` |
| 最小インターフェース | `項目｜必須｜意味｜例` |
| テスト | `観点｜Expected｜Actual｜判定` |
| 残課題 | `課題｜影響｜次の対応` |

## 11. Copilotくんに期待する最終回答

「**どの項目定義だけを用意すれば使えたか**」「**どのJSとCSSを追加したか**」「**どの検索・補完操作が通ったか**」「**未対応や懸念は何か**」を上記のMarkdown表で説明してください。

**今回の目的はStudio全体の移植ではありません。まずはSmart Searchだけを、既存の業務アプリへ使いやすい共通JS部品として組み込むことです。** Studio全体を自然言語の責務から再構築する研究は、別の長期テーマとして扱います。

## 追加契約（2026-10-23）日付・日時の省略入力

| API | 設定例 | 備考 |
| --- | --- | --- |
| `FRBSmartSearch.create()` | `{fields,dateSearch:{year_mode:'fiscal',fiscal_year_start_month:4}}` | 年度初月を明示。`calendar`も指定可能 |
| `smart.filter()` | `日付=202610..202611` | 2026年10月〜11月末まで |
| `smart.filter()` | `日時=20261023_15` | 15時台全体 |
| `smart.filter()` | `日時=20261023_1530..20261023_1730` | 15:30分台〜17:30分台（両端を含む） |

設定未指定なら年度4月開始。Studio本体は `wwwroot/config/app_settings.json` の `smart_search.date_search` を読み込む。独立JS側ではAPIへ明示的に設定を渡す。保存データは `YYYY-MM-DD` / `YYYY/MM/DD` / `YYYY.MM.DD` 等を検索時に正規化するが、保存形式を変更しない。タイムゾーン付き`instant`は対象外。詳細は `FRB_SmartSearch_JS_v0_1/README_DATE_PRECISION.md`。
