# FRB Launch 0269 — Explorer複数ファイルDropのパス表現優先順位修正

## 症状

- Windows Explorerで複数ファイル（例：`_make_launch_zip.bat` と `AGENTS.md`）を選択してLaunchの設定JSONフォルダーへDropした際、`ドロップ元が存在しません` となる。
- エラーにはWindowsの8.3形式に似た短縮パスが現れる。画面の `¥` は日本語フォント環境でのバックスラッシュ表示の場合があり、それ自体は文字化けの確証ではない。

## 原因候補と今回の変更

- 変更前 `mime_sources()` は、Qtの `mime.urls()` で取得した通常パスに加え、Windows OLEの `FileNameW` と `FileName` を無条件に追加していた。
- 同じファイルの別表現（存在しない短縮パスを含む）を別ファイルと誤認すると、`normalize_sources()` の存在確認でDrop全体が失敗し得る。
- 変更後は**入力表現の優先順位**を `Qt URLs → text/uri-list → Unicode FileNameW → ANSI FileName` に変更し、先の方式で有効候補が得られた場合、後のファイル名方式を重複追加しない。
- Windows ANSIの補助読み取りはWindowsの標準ANSIコードページ(`mbcs`)を使用する。ただし優先順位はUnicodeが上。
- Windows上のファイルの移動・削除処理、Studio Change Core、設定JSONへの登録契約は変更しない。

## テスト

`python -m pytest -q tests/test_launch_menu_registration_20261111.py tests/test_launch_0269_explorer_files_root_order_20261111.py tests/test_launch_0269_files_root_cli_20261111.py tests/test_launch_json_move_0269.py`

- この環境：23 PASS / 4 SKIP（Windowsまたは関連環境が必要なテスト）。
- 追加：Qtの2ファイルに存在しないDOS短縮パスのOLE表現が混在しても、元の2ファイルだけを登録候補にする。
- 追加：Qt URLsが空の場合はUTF-8 URIリストを短縮パスより優先する。
- 追加：Unicode `FileNameW` をANSI `FileName` より優先する。

## 受入・残課題

- Windows実機のExplorer→Launch Dropは本環境では未受入。OneDrive配下の2ファイル（`.bat`, `.md`）を選択して、設定JSONカテゴリー配下へDropし、2件だけ登録されることを確認する。
- 一部の特殊な仮想ファイルプロバイダーではQt URLs / URIリストが空で、Windows OLEのファイル名だけを渡す場合がある。その形式で存在しないパスが渡されるケースには、追加の診断と対応が必要。
- ファイル・フォルダーの物理操作やJSON Moveは変更対象外。
