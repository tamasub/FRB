# FRB Launch 一の手｜確認UIの入力接続修正（2026-11-10）

## 実機で判明した不具合

- 一の手でフリック後、確認UIは見えるが、マウスホイール（ぐりぐり）でFiles Expのカレントが動いてしまう。
- 見た目の「OK」「キャンセル」をクリックしても反応しない。結果としてZIPも実行できない。

## 原因（ソース上で特定）

1. `launch_remote.LaunchRemote.eventFilter` がRemote内の全ホイールを先取りして `WheelPad.wheelEvent` へ転送していた。`ShurikenButton.wheelEvent` に実ホイールが届かないため、Expへ流れてしまった。前回のButton単体テストはこの共通フィルターを経由せず見落とした。
2. `remote_shuriken.ShurikenPreview` は `WindowTransparentForInput` でクリックを受け付けず、OK／CancelはQPainterで描かれた矩形だけで、実際のクリック対象を持たなかった。

## 今回の対応

- 確認中は `LaunchRemote.eventFilter` と `WheelPad.wheelEvent` がホイールの入力所有権を一の手に移譲する。Exp／List操作に流さない。
- 青いポインティングロッドにぐりぐりが再配置された構成も同様に扱う。
- `app.remote_command` でも確認待ちならUP/DOWN/CLICKを最優先で消費する。ぐりぐり上のホイール→CLICKも可能。
- ポケモンボール本体は従来どおりマウス入力を透過させて残す。
- その**上部にだけ**小さな非アクティブ化ツールウィンドウを重ね、本物の`QPushButton`「OK（実行）」と「キャンセル」を置く。表示文字と選択状態は同じ`FirstHandConfirmation`に従う。
- クリックしたOKでのみ実行。直接キャンセルをクリックすれば終了。ぐりぐりでは下＝OK、上＝キャンセル、続いてぐりぐりのクリックか一の手ボタンのクリックで確定。
- 選択後のホイールだけでは実行されない。確認初期値は必ずキャンセル。
- 候補IDと目玉のIDが一致しなければ実行を許可しない。

## 非変更領域と検証

- 1〜4件の配置、しきい値、StudioのViewDef、設定JSONは変更なし。
- 既存Remoteの通常ホイール操作は一の手確認中**以外**変更なし。
- PythonモックによるテストでRemoteのイベントフィルター、ぐりぐり直受信、ブルーロッド再親化、アプリのコマンドルーティング、OK/Cancel確定、件数別選択を確認。
- Windows/PySide6のネイティブイベント／ツールウィンドウの描画・クリックは本環境では未検証。実機検証が必要。
