# FRB Launch × Studio Change Core｜新規登録（Add-only）受入メモ

対象：`launch_app_20261111_184118(1).zip` を基準にした差分。既存の設定JSONは変更しない。
関連：`studio_work_0269` / `studio-external-changeset-core-v0_1`。

## 1. 実装した入口（今回のスコープ）

- **Expの余白**：カテゴリー作成／既存フォルダー登録を直接表示。Pageは選択可能。ルート直下へのファイル・URL登録は拒否。
- **Expの設定JSON Page／カテゴリーフォルダー**：直接表示。Page直下はカテゴリー・フォルダー登録、カテゴリーフォルダー配下はカテゴリー・フォルダー・ファイル登録。
- **Expの Files登録ルート自身**：既存の長い実フォルダーメニューを維持し `Launch Menu ▶` を追加。新規カテゴリー／既存フォルダー登録は、そのFilesルートと**同じ親カテゴリーの末尾**に追加する（`directory` 自身は子を持たない）。
- **ExpのFiles登録ルートから展開した実フォルダー**：従来のファイルシステム操作のみ。Launch Menuは表示しない。
- **LISTのとんとん親帰り余白**：現在開いている設定JSON Page／カテゴリーフォルダーを操作対象とする。
- **LISTの設定JSONカテゴリーフォルダー**：その配下への新規登録を直接表示。
- **LISTの最下位アイテム**：既存プロパティ／参照IDコピーを維持。追加メニューなし。
- **簡易編集・登録解除**：今回CLIがAdd-onlyのためメニューを無効表示。Update／Deleteの実装は次段階。

## 2. ドラッグ＆ドロップ

- **Windows Explorerの既存フォルダー／ファイル** → 設定JSONのカテゴリーフォルダー（Exp／LIST）。余白の場合、現在のJSONカテゴリーへ登録。
- **Chrome／Launch内ブラウザのHTTP(S) URL** → 設定JSONのカテゴリーフォルダー（Exp／LIST）。`text/uri-list` / `text/x-moz-url` / Windows URL OLE / `.url` ファイルを解析。タイトルが得られない場合はURLから生成。Launch内ブラウザでは、アドレスバー左の小さな `🔗` アイコンをドラッグ元として追加。
- **Expルート余白／Page直下**：既存フォルダーだけをDrop登録可能。URL・ファイルは拒否。
- **実フォルダー、動的インストールアプリ、動的ブックマーク、Leaf** はDrop登録先にしない。
- DnDは常にCopy操作（Launch設定にアイテム追加）。実ファイルのMove/Delete/Copyはしない。
- 同じDrop内の重複ソースのみ省略。別の機会の同じパスは重複登録を許す。
- **ブラウザ／Windows側のDnD MIME差はWindows実機受入が必要。** Launchが外部クリックで自動的に閉じるモードでは、ブラウザからDropするためLaunchを表示維持させる必要がある。

## 3. 保存の保証

`src/launch_menu_registration.py` はUI依存なし。Launchから `node tools/change_core/cli.mjs --config <trusted-temp-config>` をsubprocessで呼ぶ。通信ポートなし。入力は既存文書のSHA、対象Page/親ID、Add複数件。

`dry_run (PREVIEW)` → `commit (COMMITTED)` の順で実行し、基準SHA競合・Tree整合性・Expected/Actual/Unexpected DiffはStudioの既存Coreに委譲。失敗時はLaunch設定JSONを書き換えない。成功したときだけ `reload(force=True)`。

`studio_root` 変数で指定されたStudioの `tools/change_core/cli.mjs` と `defs/launch/frb_launch_maintenance_view_def_v0_1.json` が必要。Node実行ファイルはStudioに同梱されているもの、またはWindowsのPATHにある `node.exe` を使用。**今回node.exeは同梱していない**。

## 4. テスト実施（Windows実画面以外）

- Python の追加テスト6本 PASS（URL・.url・日本語・カテゴリ親制約・CLI結合・元データ不破壊）。
- Studio ZIP `FRBStudio_App20261111_175538.zip` のNode Change Coreを使用し、一時Launch設定JSONへのAddを実行：`COMMITTED`。複数URL Add／カテゴリAdd成功。元ZIP内の設定JSONには書き込んでいない。
- `python -m compileall src` PASS。PySide6がこの検証環境にないためQt実画面は未受入。
- 以前のテストに「Files ExpはDrop完全禁止」という古い期待があったため、**Copy Dropのみ許可／InternalMove禁止**のテストへ改定。
- 既存テストには本差分以前から存在するスタブ不整合等の失敗がある（変更前でも再現）。それらを今回のPASSと誤記しない。

## 5. Windows実機での受入優先順

1. LaunchとStudioのデータ／ソースのバックアップを取る（重要）。
2. 最新Launchに差分を上書き。`_run_windows.bat` でPython版を起動し、Stage1で新規カテゴリーをメニューから登録。新規Page下に表示されること。
3. 次に既存フォルダー／ファイルを選択ダイアログから登録し、開けること。
4. Explorerからフォルダー／ファイルを、カテゴリーにDropして自動登録。物理ファイルが動かされていないこと。
5. Chromeのアドレスバー左側からURLを、Launchを表示維持した状態でカテゴリーにDrop。URLと表示名、起動先ブラウザを確認。Launch内ブラウザも確認。
6. 実フォルダー配下には `Launch Menu` が出ず、Files登録ルート自身にのみ出ること。
7. LISTのとんとん親帰り余白、カテゴリーフォルダー、葉で右クリックメニューを確認。
8. 同時にStudioから設定JSONを編集したときは、CLIの409相当の競合拒否が動くこと。

今回の範囲は**Addのみ**。簡易編集・登録解除・並べ替えは未実装。F12側の文書単位の保証完全共通化も継続課題。
