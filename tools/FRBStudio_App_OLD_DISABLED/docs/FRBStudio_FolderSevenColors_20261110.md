# FRB Studio フォルダー色選択を7色に整理（2026-11-10）

## 変更点

- Studio の「アイコン（顔で選択）」の選択肢から **フォルダー（水）** `folder.cyan` と **フォルダー（桃）** `folder.pink` を除外。
- 残す7色：黄・青・緑・赤・紫・橙・灰。
- 既存の「カテゴリー（青）」「ファイル」「ZIP」等の選択肢はそのまま。
- Launch 本体の描画コードには変更なし。すでに設定JSONに `folder.cyan` / `folder.pink` がある場合でも Launch は従来どおり解釈できるようにする。
- 選択肢からの削除であり、既存の設定JSONや利用者データは書き換えない。

## 適用手順

Studio を終了したうえで、差分ZIPの構成を保ってStudioルートへ上書き。Studioを再起動し、選択肢が7色になったことを確認する。

## 検証

`python -m pytest -q tests/test_launch_folder_color_choices_20261110.py`

Windows実機GUIでの表示は未確認。
