# Studio ツリー編集

FRBStudio_App直下に差分を上書きし、Studioを再起動してください。LaunchのJSONデータは変更しません。Launchのメニュー項目Viewにツリー操作バーが表示されます。

- 子を追加: 選択カテゴリー配下。GUID・Page・親・順序は自動設定。
- 同じ階層に追加: 選択項目の直後。
- 最上位に追加: Page名を選択。
- ↑上へ / ↓下へ: 同じ親・Page内で順序を変更。
- 移動: 親を名前で選択。Pageをまたぐ場合は子孫のPageも変更。
- 左右キーで開閉・親子移動、上下キーで表示行を移動。行をクリックしてから操作。
- 全文検索では一致項目と祖先を表示。検索中は該当経路を展開。
- 一覧表示ボタンで従来表示に切替。
- 子がある親の削除は止めます。子を移動してから削除してください。
- 新規作成はF12で反映、最後に通常のJSON保存が必要です。並べ替え・移動も保存してください。

ViewDefのgrid sectionにtreeを設定すると他のJSONにも使用できます。idField / parentField / labelField / orderField は必須、groupFieldは任意。フィールド名は直接プロパティ名を指定します。groupSource、groupIdField、groupLabelFieldでグループ候補配列を指定できます。parentKindField / parentKindsで子を持てる種別を制限できます。実例はdefs/launch/frb_launch_maintenance_view_def_v0_1.jsonです。JSON本体はフラット配列のままです。既存IDは変更しません。

今回の並べ替えは上下ボタン、親変更は移動ダイアログです。ドラッグ移動は未実装です。入力欄の条件表示はStudio既存visibleWhenを利用しています。

## 検証

Nodeテスト: 新規12件 + 既存回帰24件 合格。UI部分はjsdomによるDOM・キーイベント検証です。Windows NativeShell/WebView2の実画面操作は未確認です。Launchの既存43項目の親子関係も読み込み確認しました。

テスト再実行: `node --test tests/tree/tree_model.test.cjs`。UIテストはjsdomを別途用意し `FRB_JSDOM` にそのモジュールパスを設定して `node --test tests/tree/tree_ui.test.cjs`。

ブラウザーに古いJSが残る場合はStudio画面を再読み込みしてください。今回の変更はwwwroot/defs/dataのためEXEの再ビルドは不要です。差分ZIPをFRBStudio_App直下へ配置します。
