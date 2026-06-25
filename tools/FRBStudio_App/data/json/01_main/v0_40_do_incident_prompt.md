今回の作業依頼:
- incident_file: data/json/01_main/studio_work_incident_data_v0_40_md_editor_workplace_safe_added.json
- phase: v0.13.8-md-editor-workplace-safe


以下のGitHub mainを基準ソースとして扱ってください。

- FRBStudio 本体 / .NET Minimal API / タスクトレイ側
  https://github.com/tamasub/FRB/tree/main/tools/FRBStudio

- FRBStudio_App 画面資材 / data / defs / wwwroot / tests 側
  https://github.com/tamasub/FRB/tree/main/tools/FRBStudio_App


作業ルール:
1. incident_file を読み、work_items[] から phase が一致する作業項目を探してください。
2. 修正内容は、その作業項目の objective / scope / user_request / latest_user_comment / decision_log / test_points を正として判断してください。
3. phase が見つからない、または作業内容が特定できない場合は、推測で実装せず確認してください。
4. GitHub main の最新ソースを基準に、必要なファイルだけを修正してください。
5. 返却は原則ZIPとし、ZIP直下の基本階層は data / defs / wwwroot にしてください。
6. 修正したファイルは、ローカル上書きしやすいように、FRBStudio_App配下と同じ相対パスで格納してください。
7. 更新済みインシデント管理JSONは、必ず data/json/01_main/ に格納してください。
8. インシデントJSONの latest_ai_response / discussion_history / change_history に、更新ファイル・変更理由・確認ポイントを記録してください。
9. wwwroot/data と wwwroot/defs は公開用静的領域なので、明示依頼がない限り更新しないでください。
10. Program.cs等、FRBStudio本体側の更新が必要な場合は、返却前に配置方針を明示してください。