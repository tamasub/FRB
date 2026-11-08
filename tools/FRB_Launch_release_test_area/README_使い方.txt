FRB Launch + FRB Studio 配布構成集約（検証版）
=============================================

■ 何をする？
現在のビルド済み Launch dist と Studio _publish などをコピーして、
FRB_Launch / Studio の一体フォルダーを作成します。
開発元のファイルは変更しません。新しいEXEのビルドも行いません。

■ 使い方
1. このフォルダーの4ファイル（make_*.bat, assemble_*.ps1,
   _prepare_*.ps1, Start_*.bat）を同じ場所に置く。
2. make_FRB_Launch_Studio_bundle.bat をダブルクリック。
3. Launch開発ルート（dist/FRBLaunch がある場所）を入力。
   または dist/FRBLaunch フォルダーそのものを入力。
4. Studio開発ルート（wwwroot, defs, data/json,
   NativeShell/_publish がある場所）を入力。
   または NativeShell/_publish を入力。
5. 出力先フォルダーを指定。EnterならBATと同じ場所の
   FRB_Bundle_Output/FRB_Launch に生成。

コマンドライン指定の例：
make_FRB_Launch_Studio_bundle.bat "F:\FRB\tools\FRB_Launch" "F:\FRB\tools\FRBStudio_App" "F:\FRB\tools\release_test"

■ 動作確認
出力した FRB_Launch フォルダーを別の場所へコピーし、
必ず「Start_FRB_Launch.bat」から起動してください。
このBATが移動先のStudioの絶対パスをLaunch設定JSONに反映します。
その後、Launchの設定画面からStudioを開いてください。

■ 重要な制約
・これは「配布構成が成立するか確認するため」のテスト版です。
・Launchの設定JSONとStudioのdata/jsonをそのままコピーします。
  個人用パス・研究データ等が入るため、この生成物をVectorへ公開しないでください。
・移動後にFRBLaunch.exeを直接起動するとstudio_rootが古いパスのままに
  なる可能性があります。公開版ではLaunch側の相対パス解決改修が必要です。
・StudioのREADME/設定などに追加の依存がある場合、機能単位での
  実機動作確認が必要です（ここではRoot判定条件を満たすことを検査します）。
・再実行時、既に FRB_Launch が存在すればエラー停止します。
  古いテスト出力を自分で移動するか、新しい出力先を指定してください。
・生成されたビルドにはStudioのdata/markdown内の既存個人文書はコピーしません。
  空フォルダーのみ作成します。
