添付のData JSONから、FRB Studio / No-Code JSON Studio用のViewDef JSONを作成してください。

条件:

* FRB_VIEW_DEF_GENERATION_RULES_ALL_v0_15.md に従う
* schema は frb_view_def_schema_v0_8_action_registry_toolbar.json を前提にする
* Runtime内のData固定名を前提にしない
* field / caption / type を必ず入れる
* ルートのメタ情報は header form
* 主配列は main grid
* 配列履歴は objectArray
* 会話表示が必要な場合は chat + edit.messages
* Markdown AI貼り付け用が必要な場合は section.markdown.aiPrompt
* 主役Actionが必要な場合は toolbar.executeButton
* 出力は JSON ファイルとしてそのまま保存できる完全なJSONのみ
