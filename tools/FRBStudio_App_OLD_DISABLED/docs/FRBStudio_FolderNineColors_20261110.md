# FRB Studio — FRB Launch用フォルダー色の選択肢追加（2026-11-10）

`data/json/config/launch_enums_v0_1.json` の `launch.icon_key` にフォルダー9色の選択肢を追加した。
既存の選択肢、ビュー定義、JSONデータは保持し、保存値（`cd`）でLaunchと同期する。

- 黄 `folder.yellow` / 青 `folder.blue` / 緑 `folder.green` / 赤 `folder.red`
- 紫 `folder.purple` / 橙 `folder.orange` / 水 `folder.cyan` / 桃 `folder.pink` / 灰 `folder.gray`

色見本絵文字付きでドロップダウンに表示する方式。カラーフォルダー画像タイル式の専用UIは未実装。
「Pageアイコン」の選択肢や旧キーは変更しない。元のアイコンフィールドは `valueVocabularyRef: launch.icon_key` を維持する。

適用後はStudioを**再起動**し、Launchのアイテムを編集→アイコン選択→保存→Launch再読込。
