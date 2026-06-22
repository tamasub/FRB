添付のData JSONから、FRB Studio / No-Code JSON Studio用のViewDef JSONを作成してください。

条件:

* frb_viewdef_generation_rules_review_data_v0_1.json に従う
* schema は _frb_view_def_schema_v0_9_chat_input_mapping.json を前提にする
* Runtime内のData固定名を前提にしない
* field / caption / type を必ず入れる
* ルートのメタ情報は header form
* 主配列は main grid
* 配列履歴は objectArray
* 会話表示が必要な場合は chat + edit.messages
* Markdown AI貼り付け用が必要な場合は section.markdown.aiPrompt
* 主役Actionが必要な場合は toolbar.executeButton
* 出力は JSON ファイルとしてそのまま保存できる完全なJSONのみ


