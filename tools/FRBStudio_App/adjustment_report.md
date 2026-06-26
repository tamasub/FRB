# rule_review_common_view_def_v0_3 対応データ調整レポート

## 実施内容

- 3つのレビュー系Data JSONの `view_def` を `rules/rule_review_common_view_def_v0_3.json` に更新。
- `frb_coding_constraints_review_data_v0_3.json` は `constitution_sections` を `rules` に正規化。
- Coding Constraints 各行に `rule_id` を追加し、値は既存 `section_id` と同じ `constitution_xx` を使用。
- 各ルール行に `decision_log: []` を追加。
- `change_history` がない行には `change_history: []` を補完。
- `rule_count` / `approved_count` を現在の配列内容から再計算。
- `viewing_policy.recommended_view_def` を `defs/rules/rule_review_common_view_def_v0_3.json` に更新。

## 方針

- JS/Runtimeの修正は行っていない。
- Data JSONを共通Rule Review形式へ寄せることで、v0.3 ViewDefの `dataPath: $.rules` / `keyField: rule_id` に合わせた。
- Coding Constraints の `section_id` は互換・履歴確認用に残した。

## 確認

- JSON parse: OK
- 3ファイルすべて `rules` 配列あり
- 3ファイルすべて `view_def = rules/rule_review_common_view_def_v0_3.json`
- 全ルール行に `rule_id` / `decision_log` / `change_history` あり
