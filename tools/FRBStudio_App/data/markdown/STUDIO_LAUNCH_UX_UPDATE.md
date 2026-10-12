# FRB Studio / FRB Launch 操作改善

## 適用
Studio差分をFRBStudio_App直下に上書きしStudioを再起動。StudioのEXE再ビルドは不要。Launch差分はFRB_Launch直下へ上書きしbuild_windows.batでEXEを再ビルド、ランチャーを終了して新EXEを起動してください。Launchの利用中JSONは上書きしません。

## アイコン候補
Studio標準の値語彙マスタを利用。保存先はdata/json/config/launch_enums_v0_1.json。StudioでこのJSONを開くと既存common_enums_view_def_v0_1.jsonで編集できます。コードcdがLaunchのicon_key、nameがコンボ表示名です。Launch用ViewDefのvalueVocabularySourcesから読込み、valueVocabularyRef=launch.icon_keyで参照。既存アイコン値も候補へ登録済みです。候補追加のみでアイコンの絵柄が増えるわけではありません。絵柄の対応はLaunchのicon関数です。

## Pageからツリー
Page→カテゴリー→項目の順に表示。Page行を選択して「子を追加」でPage直下に追加。「Pageを追加」「Pageを編集」、上下ボタンでPage名・有効状態・順序を操作できます。Pageダブルクリックでも編集できます。Page IDは新規のみGUID。既存Page IDとitemsのIDを変更しません。JSON保存形式はpages/itemsのまま、Pageを表示上の最上位として扱います。別のPage一覧を開くボタンは外しました。Page削除はこのツリーには追加していません。

## 処理カード
アクション配列は横長の表から縦カードへ変更。処理の種類を変更すると、その種類に必要な欄を表示します。Openは対象、SendKey/ClipboardCopyは文字列、Runはプログラムと引数。待機・コンソール・タイムアウト・失敗時などは詳細設定を開いて入力。引数は1行に1つ、JSON配列へ変換して保存します。空の引数を含む行や空白入りのパスも保持します。
種類変更で非表示になった設定値は保持します。処理は上から順に実行。追加・削除・上下移動可能。F12で反映しJSONを保存してください。

この機能はStudio共通objectArrayサブグリッドのedit.subGrid.layout=cardsで指定。列のvisibleWhenで同じ行の値による表示、advanced=trueで詳細設定、control=linesで配列を行ごとに入力できます。Launch専用のRuntime分岐は設けていません。

## Launch自動読込と循環移動
起動時に設定の更新日時とサイズを記憶。表示時に比較し、変更があれば読込・再描画。変更がなければ再読込せず表示。設定が不正なら前回の正常設定を維持し、次回表示時も再試行。手動再読込メニューは廃止。
↑: 先頭項目→Pageタブ→末尾項目。↓: 末尾項目→Pageタブ→先頭項目。タブで左右はPage移動。→は従来通りフォルダー展開。空のPageでもキー操作でエラーになりません。

## 検証
StudioのDOM動作・語彙参照・JSON編集回帰43件合格。LaunchのQt/Python58件合格。Windows実画面・EXEビルドは本環境では未確認です。StudioテストのDOMにはjsdomが必要です。
