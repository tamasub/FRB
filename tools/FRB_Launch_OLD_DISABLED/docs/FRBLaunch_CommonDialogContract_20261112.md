# FRB Launch：共通ダイアログ・ぐりぐりボタンセレクター契約

対象: FRB Launch v0.9.0。設定JSON・Studioの変更なし。

## 不変条件（新規ダイアログを作る人にも適用）

1. リモコンの表示・非表示によって、ボタンセレクターやクリックRunnerを切り替えない。
2. Launch所有の `QDialog` と通知 `QMessageBox` は `Launcher.run_launch_button_dialog` 経由で開く。`QDialogButtonBox` のボタンを自動列挙するため、独自のWheel／Remote配線を追加しない。
3. 確認 `Yes/No` は既存の `Launcher.ask_remote_confirmation` で開く。通常ダイアログと同一の `DialogButtonSelection` および `ConfirmationInputGuard` を使用する。
4. Launch上のどの列・背景・見出し・Remoteでホイール操作しても、選択中のボタンを更新する。**実際のボタンを直接クリックした場合は、選択状態にかかわらずその実ボタンが勝つ。** Launchの他の場所を左クリックした場合は、明示的なぐりぐり選択後だけその選択ボタンをクリックする。
5. フォーム内の文字入力／コンボ選択／スクロール可能な文章はネイティブ編集操作を維持。テキスト入力欄上のホイールはボタン選択に使用し、入力欄への左クリックは文字入力操作を優先する。
6. 起動直後のクリックを誤認識しない保護、押下・離しの一致／ドラッグ／右クリック除外、ボタン直接操作による二重実行防止を共通Guardで保証する。
7. `QFileDialog` はOSのファイル選択ダイアログなので、ネイティブ操作を妨げない例外。アプリ起動不能時の緊急 `QMessageBox.critical` は、まだLauncherが存在しないため例外。

## 新規ダイアログの実装方法

`QDialog(self)` でフォームを構成し、`QDialogButtonBox` を配置して通常の `accepted` / `rejected` を接続する。開くときは `self.run_launch_button_dialog(dialog)` を1回呼ぶ。ボタン名・個数は共通Adapterが列挙するので、Remoteの有無を判断するコードは不要。

例：

```python
box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                       QDialogButtonBox.StandardButton.Cancel, parent=dialog)
box.accepted.connect(dialog.accept)
box.rejected.connect(dialog.reject)
layout.addWidget(box)
accepted = self.run_launch_button_dialog(dialog, editor=editor)
```

単純な入力は `self.ask_launch_text(...)`、選択は `self.ask_launch_choice(...)`、通知は `self.show_launch_notice(...)` を使う。WebView内の通知は親Launchの共通通知を使用する。

### 再発防止（ビルド／ZIP作成を止める検査）

`python scripts/check_dialog_contract.py` が以下を見つけると終了コード1で失敗する。

- `QInputDialog`、`QMessageBox.warning/information/question` の直接使用
- 通常の `dialog.exec()` / `dialog.exec_()`
- `QDialog` / `QMessageBox` を作って、同じ関数から `run_launch_button_dialog` で実行しないコード

`_make_launch_zip.bat`（`src/make_launch_zip.py`）と `_build_windows.bat` がこの検査を自動実行する。Qt/PySide6非依存で検査可能。

注意：静的検査はLaunchの `src/` 内の検出可能な記法を対象にする。実際のWindows操作とQtネイティブイベントについては実機受入が別途必要。全ての未来の動作を機械的に保証できるという意味ではない。

## 重点テスト

- `tests/test_shared_dialog_contract_20261112.py`：既存すべてのダイアログ経路、意図的に混入した直接 `.exec()` の検出、リモコン非表示、OK/Cancel直接操作、3ボタンの新しいフォーム
- `tests/test_list_confirmation_click_gate_20261110.py`：Launch全域のクリック、直接Cancel優先、背景操作を誤起動しない
- `tests/test_remote_confirmation_footer_and_header_20261103.py`：既存確認操作と通知の共通入口

Windows実画面で、Gitコミットメッセージ・簡易編集・カテゴリ入力・ZIP解凍先選択・警告・WebView警告で「ホイール選択 → Launch上のクリック」と「実Cancel押下」を確認する。
