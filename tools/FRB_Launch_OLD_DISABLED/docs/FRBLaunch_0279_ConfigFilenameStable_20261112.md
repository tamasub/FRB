# FRB Launch 0279 — 設定JSONを固定ファイル名へ変更

## 目的

- 実運用の設定データファイルを `config/frb_launch_data.json` に統一する。
- JSONデータ形式のバージョンはファイル名でなく、既存の `launch_format_version` フィールドで管理する（現行値 `0.2-draft` は変更しない）。
- `view_def` が指す `defs/launch/frb_launch_maintenance_view_def_v0_1.json` は別ファイルであり、今回の変更対象外。
- 既存のメニュー、ユーザーが編集したJSON、Studio連携を保持する。

## 対応範囲

- Launchの読込・保存・Studioへの `--open-json`・`%launch_data%`・ビルド・バックアップ・開発用ツールを新しい名前へ更新。
- 旧 `config/frb_launch_sample_data_v0_1.json` は初回起動またはビルド時に自動移行。
- 旧ファイルとZIPに同梱された新ファイルが同時に存在するときは、**旧ユーザーJSONを優先**。双方を `backups/config_filename_*/` に保存してから、新ファイルを旧ファイルの内容で置き換える。
- `config/.frb_launch_data_name_v1` に移行済み状態を記録。2回目以降の起動で古い残存ファイルへ戻らない。
- 旧ファイルはバックアップしたうえで `config/` の運用場所から除去する。
- `launch_home.json` により旧distを参照する初回ビルド移行は、従来どおり旧distにある編集済み設定を優先する。

## 配布・適用時の注意（重要）

1. LaunchとStudioくんを終了してから適用する。Studioの旧ファイルを開いたまま保存すると、旧名で再作成される可能性がある。
2. **既存環境は差分ZIPを推奨**。修正済みソースを上書きして `_build_windows.bat` を実行する。旧設定JSONは移行処理が読み込むので、手作業で消さない。
3. 完全版ZIPは新規配置向け。すでに `frb_launch_data.json` へ移行済みのユーザー環境へ完全版ZIPを上書き展開すると、同梱されている初期データでユーザーデータが上書きされうる。**完全版を既存環境へ直接上書きしない。**
4. Studioで編集する場合は、起動後の新パス `config/frb_launch_data.json` を使用する。旧パスを開く「最近使ったファイル」は選び直す。

## 安全性・検証

- JSON内の値はファイル名変更により変更しない。
- 初回移行はバイトコピー／原本バックアップで実施し、破損JSONならファイルを書き換えずエラーにする。
- マーカーとバックアップはランタイム管理情報であり、配布用差分ZIPには含めない。
- Windows実機のStudio NativeShell連携およびWindows PowerShellバックアップ実行は別途手動確認が必要。
