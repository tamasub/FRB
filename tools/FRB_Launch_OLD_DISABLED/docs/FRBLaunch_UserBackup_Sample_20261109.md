# FRB Launch 設定・ログバックアップ（個人設定向けサンプル）

## 目的

`launch_app_20261109_230144.zip` の既存設定を変更せず、`My Work > ZIP` に
**「FRB Launch 設定・ログ バックアップ」**を追加する。
設定 JSON、状態ファイル、ログ、履歴等を日時付き ZIP に保存する。

## 起動

- Launch の `My Work > ZIP > FRB Launch 設定・ログ バックアップ` を選ぶ。
- または `backup_frb_launch_sample.bat` をダブルクリックする。
- `Launch` の登録パスは `%launch_home%\backup_frb_launch_sample.bat` とし、インストール場所を固定しない。
- Windows PowerShell 5.1 以降が必要。実行終了後、結果をコンソールに表示して一時停止する。

## 保存先

`%LOCALAPPDATA%\FRBLaunch\_Backups\FRBLaunch_Backup_YYYYMMDD_HHMMSS.zip`

同じ秒に実行した場合は末尾に `_2`、`_3` のような連番を付ける。
`%USERPROFILE%` 直下には新しいフォルダーを作らない。

## ZIP 収録内容

| 格納先 | 元の場所 | 対象 |
|---|---|---|
| `config/` | `LaunchHome\config\` | 設定 JSON ほか同フォルダーのファイル |
| `defs/launch/` | `LaunchHome\defs\launch\` | Launch / Studio に必要な ViewDef（存在する場合） |
| `user_data/` | `%LOCALAPPDATA%\FRBLaunch\` | `state.ini`、ログ、履歴 JSON 等 |

- **`_Backups` は収録対象外**。バックアップ ZIP の自己取り込みを防止する。
- リンク／ジャンクションを再帰追跡しない。
- 元データを変更・削除せず、ZIP を一時ファイルで作って成功時のみ確定する。
- 個人情報や操作履歴が含まれ得るため、**生成 ZIP をそのまま GitHub 等で公開しない**。

## 手動復元の考え方

1. FRB Launch を終了する。
2. ZIP を別の場所に展開する。
3. `config/` と必要な `defs/launch/` を Launch 本体の同名フォルダーへ戻す。
4. `user_data/` の内容を `%LOCALAPPDATA%\FRBLaunch\` へ戻す。
5. Launch を起動して設定を確認する。

復元は意図的に自動化していない。既存の設定を上書きする際は、別途コピーを残すこと。

## 2026-11-09 修正: GetFullPath の無効パスエラー

初回実行で以下のエラーが報告された。

`GetFullPath` 呼び出し時に「パスに無効な文字が含まれています」。

バッチから PowerShell に `-LaunchHome "%~dp0"` を渡す方法は、
`%~dp0` の末尾が `\` になるため Windows の引数引用符処理で解釈が
崩れる可能性がある。**パスを渡す処理を撤去し、PowerShell 側の
`$PSScriptRoot`（`scripts` フォルダー）から一つ上の Launch 本体を特定する**
方式に修正した。保存先、バックアップ範囲、元ファイル非変更の仕様は維持。

## 確認

- JSON: `src/core.py` の `validate` による検証。
- バッチ、PowerShell: 構文／内容の静的確認のみ。
- **Windows 実機での PowerShell バックアップ実行は未確認。**

## 公開版への注意

この JSON は作者の現行設定のまま。将来の配布用 JSON では登録先のパスやユーザー固有の情報を個別に整理する。

## 2026-11-09 修正: 起動中の error.log が使用中で ZIP 作成に失敗する

実環境で次の例外を確認した。

`CreateEntryFromFile` が `%LOCALAPPDATA%\FRBLaunch\error.log` を読み取ろうとして、
別プロセスで使用中のためバックアップ全体が失敗した。

- `%LOCALAPPDATA%\FRBLaunch\` の **ログファイルだけ**は、共有読み取り
  (`FileShare.ReadWrite | FileShare.Delete`) を試みる。
- ロガーが排他ロックしていて開けない場合は、そのログだけスキップして
  コンソールに `[WARN] Active log skipped` と件数を表示し、ZIP作成は続ける。
- ログが読み取れる場合は、その時点ですでに存在したバイト数だけ収録する。
  追記が続いても読み取り処理が終わらなくなることを防ぐため。
- **設定JSON、ViewDef、state.ini、履歴等は必須のまま**。
  読み取り失敗をログと同じように握りつぶさない。
- `_Backups` 除外・生成途中の `.partial` からの確定・元ファイル非変更・保存先は変更なし。

**Windows 実機での再実行は未確認。**

## 2026-11-09 修正: instance.lock による ZIP 作成失敗

起動中の FRB Launch が保持している `instance.lock` を ZIP に取り込もうとしたため、
`CreateEntryFromFile` が「別のプロセスで使用されている」として失敗した。

- `instance.lock` などの `*.lock` / `*.lck` を **ユーザーデータ内だけ**除外する。
- 書き込み途中の `*.tmp` もユーザーデータ内で除外する。
- `file_index.db` と付属の SQLite 一時ファイルを除外する。ファイル検索用の
  インデックスは再生成可能であり、稼働中の SQLite ファイルを単純コピーしても
  整合性を保証できないため。
- 対象外ファイルは `[INFO] Runtime/cache file excluded:` と表示する。
- JSON・INI・ViewDef・履歴など、復元対象の設定データは引き続き必須扱い。
  ログに限っては、共有読み取りを試し、読めない場合だけ警告してスキップする。

**Windows PowerShell 5.1 実機での動作確認は未実施。**

## 2026-11-09 修正: WebEngine Cookies のロックによる失敗（対象選択方式に変更）

起動中の内蔵ブラウザが `%LOCALAPPDATA%\FRBLaunch\web_profile\data\Cookies`
を開いているため、従来の `user_data/` 丸ごと再帰コピーで失敗した。

**ユーザーデータのバックアップは除外リストから「許可したものだけ収録」へ変更する。**

| 保存するもの | 取り扱い |
|---|---|
| `config/`、`defs/launch/` | 従来どおり必須。再帰コピー（リンクは辿らない） |
| `user_data/` 直下の `*.json` / `*.ini` | 設定・検索履歴・お気に入り等。読み取り失敗時はエラー |
| `user_data/` 直下の `*.log` とローテート済みログ | 共有読み取りを試し、不可なら警告してスキップ |
| `user_data/logs/`、`log/`、`diagnostics/` 等 | 診断ログとして再帰コピー（読めない場合は警告でスキップ） |
| `_Backups/` | 絶対に再取り込みしない |
| `web_profile/` | **ディレクトリごと対象外**。Cookie、ブラウザキャッシュ、ログイン状態は保存しない |
| `instance.lock`、`file_index.db`、`apps_cache.json`、`apps_scan_*.json` 等 | 実行中・再生成可能な管理ファイルとして対象外 |
| その他の未登録ディレクトリ／ファイル | 勝手にコピーしない。対象外として `[INFO]` 表示 |

- 特に `web_profile/` は、内部の個別ファイル名が変わっても辿らない。
- 本体の設定JSONと復元対象の状態INI・履歴は必須扱い。ログだけ例外的にスキップ可。
- ブラウザのログイン状態を復元する機能は提供しない。必要に応じて再ログインする。
- ZIPは個人設定／履歴／ログを含むので、配布・GitHub公開に転用しない。
- **Windows PowerShell 5.1 実機での実行確認は未実施**。既存のユーザー設定は一切変更しない。

## 2026-11-09 修正: バックアップ完了後に保存先をエクスプローラーで開く

- ZIP作成と `.partial` からの確定が成功した**後**、`%LOCALAPPDATA%\FRBLaunch\_Backups` をエクスプローラーで開く。
- アカウント名を埋め込まず、実行中のユーザーの LocalAppData から保存先を決定する。
- ZIP作成に失敗した場合はエクスプローラーを起動しない。
- エクスプローラーの起動だけが失敗しても、完成済みバックアップの成功扱いは変えず、`[WARN]` を表示する。
- 既存の `.bat` は実行結果の表示後に `pause` する仕様を維持する。

※ Linuxでの静的・回帰テストは実施可能だが、Windows ExplorerのGUI起動はWindows実機で確認する。
