# FRB Launch 公開準備｜フォルダーをLaunchで開く／JSON仮想フォルダーのプロパティ

2026-11-10

## ① 設定JSONのフォルダーOpenをLaunch内で開く

- 対象：展開後の `launch_actions` が **1件だけ**で、`launch_action_type: Open`・`launch_target` が現在存在する実フォルダーの場合。
- 動作：Windows Explorerを新規起動せず、Launchの既存 Files ワークスペースへ移動。既存のパンくず・Files List・移動履歴を使用。
- アイテム種類が `directory` / `command` のどちらでも、アクションが実フォルダーOpenなら同じ。
- 複数アクション、Run、ファイルOpen、URL、`shell:`、明示的な外部ブラウザー指定は従来どおり。単独のBATやStudio JSONルーティングは変更しない。
- フォルダーが削除済みの場合は従来のOpen経路へ進む（Launch内に空の仮想フォルダーを作らない）。
- 設定JSON／ViewDefに新しい属性・固定値は追加していない。

## ② Files Exp：Launch JSON仮想フォルダー

- **実フォルダー：従来の黄色アイコン、従来のOS向けコンテキストメニュー**。
- **設定JSONの仮想フォルダー：青紫色アイコン**。Pageルートは従来どおりタイトルに含まれる絵文字のみ（アイコン重複なし）。
- 右クリックに **「プロパティ」** を追加。実際のDataJSONに存在し、有効なPageなら`--launch-page-id`、有効な管理Itemなら`--launch-item-id`を付け、Studioくんで該当設定を表示する。
- 現在選択中のLaunchタブと異なるPageを右クリックしても、**右クリック対象のPage**をStudioへ渡す。
- 自動生成したインストール済みアプリ・ブラウザーブックマークにはStudioプロパティを表示しない。JSON参照IDコピーは従来どおり。
- 実ファイル・フォルダーの右クリックメニュー、コピー／移動／削除機能には変更なし。

## テスト

- `python -m pytest -q tests/test_json_folder_navigation_and_properties_20261110.py` で専用テストを実行。
- Windows11での推奨手動確認：①Launchの既存設定フォルダーOpen（例: Downloads）を実行し、Explorer新規起動でなくFiles List・パンくずが切り替わること、②Files Expの青紫フォルダーを右クリックし「プロパティ」→Studioで該当Itemを開けること、③Pageルートのプロパティが右クリックしたPageへ遷移すること、④実フォルダーは黄色・従来メニューのままであること。
- この環境にはPySide6/WindowsのGUIがないため、実機マウス操作は未確認。

## 留意

- 個人設定JSONを含むFULL ZIPを公開版としてそのまま配布しないこと。公開用設定の秘匿項目の削除は別作業。
- Studioの既存CLI引数と焦点合わせ機能を利用するため、Studio本体のソース変更は不要。
