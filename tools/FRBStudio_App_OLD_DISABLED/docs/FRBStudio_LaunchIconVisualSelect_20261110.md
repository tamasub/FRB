# Studioくん：Launchのアイコン選択表示 — 2026-11-10

作業元：`FRBStudio_App20261110_085306.zip`。

現在の`icon_key`は既存の `select` + `valueVocabularyRef=launch.icon_key` です。その選択候補の名称にアイコンを連想できる絵文字（📁🟦📄等）を付加しました。値（`cd`）は一切変更しません。旧互換キー `folder` と `category` を追加し、既存JSON値が候補から消えないようにしています。選択欄の表示幅も広げました。

**制約：** 今回ユーザーから渡されたStudio ZIPは `defs`、`data`、`NativeShell` 等の設定・データ中心の内容で、StudioのWeb画面本体（`index.html`、画面レンダラーのJS/CSS）が含まれていません。そのため、フォルダーの実際の描画画像をタイル表示するアイコンピッカーUIは実装できません。今回できたのは「既存セレクトの候補に絵文字プレビューを付ける」範囲までです。次に画像グリッドを実装する際はStudioのHTML/JS本体ソースが必要です。

値語彙マスタ：`data/json/config/launch_enums_v0_1.json`
ViewDef：`defs/launch/frb_launch_maintenance_view_def_v0_1.json`
