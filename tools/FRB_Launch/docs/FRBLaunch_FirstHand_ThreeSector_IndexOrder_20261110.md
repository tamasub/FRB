# FRB Launch 一の手：3方向・インデックス順 復元（2026-11-10）

## 目的
Studioで編集するのは「一の手に表示するか」と「表示優先順」のみ。フリック方向はLaunchの責務で、Studioからの方向指定を禁止する。2026-11-10の手描き図に合わせ、中央円＋3本の境界線＋左上／右上／下のラベル配置を維持する。

## 今回の確定仕様

1. `shuriken_enabled=true` かつ `enabled=true` のItemから、`shuriken_order` 昇順に抽出。
2. 同じ優先順は設定JSON内の登録順（配列順）で安定的に整列。
3. 先頭 **3件** を採用、**4件目以降は読み込んでも表示・実行しない**。Studioで件数エラーにしない。
4. インデックス0 → `up_left`（左上）、1 → `up_right`（右上）、2 → `down`（下）。時計回り。
5. 過去JSONに残る `shuriken_direction` は読み込めるが、配置には利用しない。
6. `shuriken_context_action_id` など既存の特殊実行・通常メニュー非表示の契約は維持。
7. 1件・2件しか登録していない場合でも3分割の形は維持し、未割当の領域は実行しない。
8. 緑の目玉で示した選択対象を離した瞬間に実行。放したとき再判定しない。境界、デッドゾーンはキャンセル。

## 非変更事項

- `ShurikenPreview.RADIUS=72`、`CURRENT_RADIUS=24`、`MARKER_DISTANCE=42`、ラベルの外側配置、透過ポップアップ座標。
- マウス押下・ドラッグ・リリースのイベント処理、Gitコミットの既存ダイアログフロー。
- 元の設定JSONのItem内容、`shuriken_order`、`shuriken_direction` の保存値。
- 他機能の2方向Exp/Listおよび汎用4方向の計算プリミティブ。

## 回帰確認

- `tests/test_shuriken_first_hand_clockwise_contract_20261110.py`：新規。順序・旧方向無視・3件上限・境界キャンセル・中央円／目玉・Studio ViewDefを検証。
- `test_remote_shuriken_one_hand_20261105.py` 等、過去の「4件登録」前提のテストを現行の3方向契約へ更新。汎用4方向のテストは合成データで維持。
- PySide6/Windowsがない実行環境では実機描画・マウス操作は未確認。Windowsで（a）押下直後の3分割、（b）左上／右上／下の表示、（c）各方向へフリックと実行先、（d）境界キャンセル、（e）Gitコミット、（f）優先順変更、を確認すること。

## 適用

今回の **Launch** と **Studio** 差分ZIPは**両方**適用する。アプリ終了→設定JSONバックアップ→差分反映→再起動。設定JSON自体は変更しない。
