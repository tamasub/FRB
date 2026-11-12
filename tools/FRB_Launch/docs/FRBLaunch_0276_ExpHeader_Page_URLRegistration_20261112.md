# FRB Launch 0276 — ExpヘッダーにPage追加／Exp・List共通URL登録

更新日: 2026-11-12

## 変更内容

### ① Pageを追加の場所修正

- **Files Expのタイトルヘッダー（「Files Exp」の文字とその背景）を右クリック** → `Pageを追加...`。
- Page行、設定JSONのカテゴリーフォルダー行、Expの空白ルートから `Pageを追加...` を撤去。
- Page登録の実処理は変更しない。従来どおりStudio Change CoreのPage Addを使用。
- Expヘッダーは埋め込み・分離型のどちらも同じ共通コンテキストメニューを使用し、既存ぐりぐり操作を維持。

### ② URLを追加の新設

- 設定JSONの**Pageまたはカテゴリーフォルダー**を右クリック → `既存ファイルを登録...` の直下に `URLを追加...`。
- Files ExpとFiles Listの両方で同一メニュー・同一画面を利用する。
- ダイアログには **タイトル／URL**、**URL取得**、**追加／キャンセル** を用意。
- URL取得は**クリップボード**内のChrome等のURLを読み取り、取得できなければFRB Browserで表示中のURLを使用。
  - 外部ブラウザのアドレスバーを勝手に操作する機能ではない。Chrome利用時は URLをコピーするか、URLをドラッグする。
- URL欄にはChromeのURL／リンクを**ドラッグ＆ドロップ**可能。リンク名からタイトルを補完（タイトル手入力済みなら上書きしない）。
- 説明に `Launch本体の登録先へDropしても自動追加できますよ。` を明記。
- URLは `http://` / `https://` のみ許可し、タイトル必須。Openアクション／globeアイコン／Studio Change Core登録を再利用。
- **Files Expの空白ルート**は従来どおり実フォルダー登録専用。URL登録は設定JSONのPage／カテゴリーフォルダーを対象にする。

## テスト

- `python scripts/check_dialog_contract.py`
- `python scripts/check_context_menu_contract.py`
- `pytest -q tests/test_launch_0276_page_header_and_url_dialog_20261112.py`
- Windowsで要確認: Expタイトル右クリック、Page行にPage追加が無い、Exp/ListのURLメニュー位置、Chromeアドレスバードロップ、クリップボードURL取得、URLの保存→再起動後実行。
- Linux側にPySide6がないため、GUIウィジェットの実機イベントテストは未実施。

## 配布

- **差分ZIP** は変更・追加ファイルだけを、ルートからの相対パス（`src/`、`tests/`、`docs/`）で収録する。既存プロジェクトへ上書き展開する。
- 実際のLauncher設定データ `config/frb_launch_sample_data_v0_1.json` には触れていない。
