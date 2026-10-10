# 操作改善

- 起動・表示直後、検索欄が空なら右キーでカレント項目を展開。
- 展開メニューは先頭の有効項目を自動選択。右で次階層、左でその階層を閉じる。
- 実フォルダーの一覧は名前だけの1列。画面に収まらない分は上下にスクロール。
- 選択画面に全選択・全解除・戻るボタンを追加。
  Ctrl+A：グループの全選択（検索で隠れた対象も含む）。Ctrl+Shift+A：全解除。
  左キー：選択画面から戻る。Space：個別チェック。F12：送信。
- make_launch_zip.bat：同じフォルダーに launch_app_yyyyMMdd_HHmmss.zip を作成。
  ソース・設定・定義・テスト等を含み、.venv、build、dist、.git、キャッシュ、ZIP、ログを除外。
  同一秒のファイルがある場合は上書きせずエラーにする。1秒以上あけて再実行。

更新時はトレイから終了し、ファイルを上書きして build_windows.bat を実行してください。
設定・定義は今回の添付内容を保持しています。別途編集した設定があれば上書き前に退避してください。

## 2026-10-10 展開・検索の再修正

- 子フォルダーは先頭選択だけでは開かず、右キーで1階層ずつ展開。
- 左キーは現在の展開だけ閉じて親へ戻る。マウスの実移動によるホバー展開は維持。
- 展開中も Ctrl+F で検索欄へ移動。直接文字入力でもメニューを閉じて検索。
- 作業フォルダーに「FRBルート」（F:\FRB）を追加。
- ZIP作成に「FRB LaunchをZIP保存」を追加。
  Openアクションで F:\FRB\tools\FRB_Launch\make_launch_zip.bat を起動。

### Studioでフォルダーを追加する設定

itemsに行を追加し、page_id=work、parent_item_id=folders、item_id=一意なID、
title=表示名、item_kind=directory、icon_key=folder.yellow、enabled=true、
launch_browse_target=展開するフォルダーを指定する。
launch_actionsにはlaunch_action_type=Open、launch_target=同じフォルダーを指定する。
FRBルートの登録行を複製してパスとIDを変えてもよい。

ランチャーが読む設定はEXEと同じ場所のconfig内。
ビルド時はソース側configがdistへコピーされるため、ソース側も同じ内容に保つこと。
