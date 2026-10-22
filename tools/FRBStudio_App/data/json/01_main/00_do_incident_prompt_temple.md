今回の作業依頼:
- incident_file: data/json/01_main/studio_work_incident_data_v0_51_data_viewdef_candidates_added.json
- phase: v0.14.1-data-viewdef-candidates

作業ルール:

AIやスクリプトが直接取得するためのraw/archive URL:
- Foundation Rules raw: https://raw.githubusercontent.com/tamasub/FRB/main/tools/FRBStudio_App/data/json/00_rules/frb_foundation_rules_data_v0_1.json

- リポジトリ main ZIP: https://github.com/tamasub/FRB/archive/refs/heads/main.zip
- FRBStudio_App raw base: https://raw.githubusercontent.com/tamasub/FRB/main/tools/FRBStudio_App/
- FRBStudio 本体 raw base: https://raw.githubusercontent.com/tamasub/FRB/main/tools/FRBStudio/

FRB Studio Foundation Rules の foundation_rule_019「GitHub基準ソースとZIP返却契約」を参照してください。

記載形式（ユーザー希望・今後のインシデントにも適用）:
- Studioくん憲法 constitution_32「構造化記述の原則」に従う。
- **ChatGPTのチャットで説明するように、短い見出し＋Markdown表を優先する。**
- 計画・変更点・理由・対象・判断・テスト結果・残課題・リスク・次の作業は、内容を比較できる場合は `| 項目 | 内容 |` 形式のMarkdown表で簡潔に整理する。
- 表より読みやすい短い事項のみ箇条書き／番号付きリストを使う。文章の長い羅列や一つの文章への連結を避ける。
- テストの確認結果は「観点｜期待値｜実測｜判定」、計画は「作業｜目的｜完了条件」を基本列として検討する。必要ない列は省く。
- この書き方はSmart Searchだけでなく、新しいインシデントや計画を作る場合にも継続適用する。

