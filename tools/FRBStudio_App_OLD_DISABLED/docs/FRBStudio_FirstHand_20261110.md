# FRB Studio — Launch手裏剣・一の手設定（2026-11-10）

Launchのメニューアイテム詳細編集画面（`defs/launch/frb_launch_maintenance_view_def_v0_1.json`）で、以下を設定できる。

- **手裏剣・一の手に表示**（チェック）: `shuriken_enabled`
- **一の手：表示優先順**（数値）: `shuriken_order`。昇順で先頭4件が採用される。
- **一の手：フリック方向**（任意、空欄は自動）: `shuriken_direction`
- **一の手専用（通常メニュー非表示）**: `shuriken_only`
- **一の手：専用操作ID**（特殊用途、通常は空欄）: `shuriken_context_action_id`

従来から設定済みの方向・優先順を維持できる。Studioは登録件数を制限しない。5件目以降の非表示・非実行はLaunch側で担当する。

Launch設定JSONはこの配布物では変更しない。既存の4件より後ろの順に追加すると新規登録は表示されないため、優先順や登録チェックを調整する。
