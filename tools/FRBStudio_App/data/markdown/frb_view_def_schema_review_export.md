# ViewDef Schemaレビュー記録

- 出力日時: 2026/6/25 22:54:21
- 対象: FRB Studio / JSON Object Studio / ViewDef Schema
- schema_version: schema_review_data_v0_1
- status: converted_draft
- 件数: 360

## 基本情報

- タイトル: FRB Studio ViewDef Schema Review Data v0.1
- 対象: FRB Studio / JSON Object Studio / ViewDef Schema
- ドメイン: view_def_schema
- 元Schemaファイル: frb_view_def_schema_v0_9_chat_input_mapping.json
- Schema ID: frb_view_def_schema_v0_9_chat_input_mapping.json
- Schema Title: FRB Studio View Definition Schema v0.9 - Chat Input Mapping / Markdown Inline
- JSON Schema Draft: https://json-schema.org/draft/2020-12/schema
- $defs数: 35
- Root properties数: 19
- レビュー項目数: 360

### Schema説明

Schema for FRBStudio_App / No-Code JSON Studio view_def JSON files. Includes inheritance, common field types, Markdown export / AI Prompt, dataSources, virtualData registry builders, single-source writeBack, Relation status filters, and toolbar.executeButton action declarations. v0.9 adds chat edit.input.appendPosition/appendLabel and chat Markdown inline link/image permissions.

### 変換メモ

JSON Schemaはproperties/$defsの辞書構造が多いため、Studio上でレビューしやすいように root_property / definition / definition_property のフラットな schema_items 配列へ変換したData JSON。元Schemaは参照元であり、このJSONはレビュー・確認・Markdown出力用のViewである。

### レビュー方針

Schemaの定義内容はAIが要約・分類できるが、採用可否・修正判断は人間が行う。確認済みにする場合は verification_status を確認済みにし、approval_decision を承認する。

## Schema項目一覧

| No. | 種別 | 名前 | 親 | Schema Path | 型概要 | 必須 | 参照 | 優先度 | レビュー状態 | 確認状態 | 承認 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | root_property | app |  | properties.app | object{2 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 2 | root_property | views |  | properties.views | array<ref: view> | true | view | medium | 未レビュー | 未確認 | 未承認 |  |
| 3 | root_property | extends |  | properties.extends | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 | ViewDef inheritance. String or array of parent view_def JSON file names. |
| 4 | root_property | viewDefReport |  | properties.viewDefReport | ref: viewDefReportOptions | false | viewDefReportOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 5 | root_property | dataSources |  | properties.dataSources | ref: dataSources | false | dataSources | medium | 未レビュー | 未確認 | 未承認 |  |
| 6 | root_property | data_sources |  | properties.data_sources | ref: dataSources | false | dataSources | medium | 未レビュー | 未確認 | 未承認 |  |
| 7 | root_property | virtualData |  | properties.virtualData | ref: virtualData | false | virtualData | medium | 未レビュー | 未確認 | 未承認 |  |
| 8 | root_property | virtual_data |  | properties.virtual_data | ref: virtualData | false | virtualData | medium | 未レビュー | 未確認 | 未承認 |  |
| 9 | root_property | writePolicy |  | properties.writePolicy | ref: writePolicy | false | writePolicy | medium | 未レビュー | 未確認 | 未承認 |  |
| 10 | root_property | write_policy |  | properties.write_policy | ref: writePolicy | false | writePolicy | medium | 未レビュー | 未確認 | 未承認 |  |
| 11 | root_property | fieldTypeSources |  | properties.fieldTypeSources | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 12 | root_property | field_type_sources |  | properties.field_type_sources | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 13 | root_property | typeSources |  | properties.typeSources | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 14 | root_property | type_sources |  | properties.type_sources | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 15 | root_property | commonTypeRegistry |  | properties.commonTypeRegistry | object<additional:any> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 16 | root_property | common_type_registry |  | properties.common_type_registry | object<additional:any> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 17 | root_property | commonTypes |  | properties.commonTypes | object<additional:any> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 18 | root_property | common_types |  | properties.common_types | object<additional:any> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 19 | root_property | toolbar |  | properties.toolbar | ref: toolbarOptions | false | toolbarOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 20 | definition | view | $defs | $defs.view | object{21 properties} | false | layoutOptions, section, markdownOptions, viewDefReportOptions, dataSources, dataSources, virtualData, virtualData, writePolicy, writePolicy, toolbarOptions | high | 未レビュー | 未確認 | 未承認 |  |
| 21 | definition_property | id | view | $defs.view.properties.id | string | true |  | high | 未レビュー | 未確認 | 未承認 |  |
| 22 | definition_property | caption | view | $defs.view.properties.caption | string | true |  | high | 未レビュー | 未確認 | 未承認 |  |
| 23 | definition_property | layout | view | $defs.view.properties.layout | oneOf: string enum[1] / ref: layoutOptions | true | layoutOptions | high | 未レビュー | 未確認 | 未承認 |  |
| 24 | definition_property | sections | view | $defs.view.properties.sections | array<ref: section> | true | section | high | 未レビュー | 未確認 | 未承認 |  |
| 25 | definition_property | markdown | view | $defs.view.properties.markdown | ref: markdownOptions | false | markdownOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 26 | definition_property | viewDefReport | view | $defs.view.properties.viewDefReport | ref: viewDefReportOptions | false | viewDefReportOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 27 | definition_property | dataSources | view | $defs.view.properties.dataSources | ref: dataSources | false | dataSources | medium | 未レビュー | 未確認 | 未承認 |  |
| 28 | definition_property | data_sources | view | $defs.view.properties.data_sources | ref: dataSources | false | dataSources | medium | 未レビュー | 未確認 | 未承認 |  |
| 29 | definition_property | virtualData | view | $defs.view.properties.virtualData | ref: virtualData | false | virtualData | medium | 未レビュー | 未確認 | 未承認 |  |
| 30 | definition_property | virtual_data | view | $defs.view.properties.virtual_data | ref: virtualData | false | virtualData | medium | 未レビュー | 未確認 | 未承認 |  |
| 31 | definition_property | writePolicy | view | $defs.view.properties.writePolicy | ref: writePolicy | false | writePolicy | medium | 未レビュー | 未確認 | 未承認 |  |
| 32 | definition_property | write_policy | view | $defs.view.properties.write_policy | ref: writePolicy | false | writePolicy | medium | 未レビュー | 未確認 | 未承認 |  |
| 33 | definition_property | toolbar | view | $defs.view.properties.toolbar | ref: toolbarOptions | false | toolbarOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 34 | definition_property | fieldTypeSources | view | $defs.view.properties.fieldTypeSources | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 35 | definition_property | field_type_sources | view | $defs.view.properties.field_type_sources | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 36 | definition_property | typeSources | view | $defs.view.properties.typeSources | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 37 | definition_property | type_sources | view | $defs.view.properties.type_sources | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 38 | definition_property | commonTypeRegistry | view | $defs.view.properties.commonTypeRegistry | object<additional:any> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 39 | definition_property | common_type_registry | view | $defs.view.properties.common_type_registry | object<additional:any> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 40 | definition_property | commonTypes | view | $defs.view.properties.commonTypes | object<additional:any> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 41 | definition_property | common_types | view | $defs.view.properties.common_types | object<additional:any> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 42 | definition | section | $defs | $defs.section | object{8 properties} | false | field, markdownSectionOptions | high | 未レビュー | 未確認 | 未承認 |  |
| 43 | definition_property | id | section | $defs.section.properties.id | string | true |  | high | 未レビュー | 未確認 | 未承認 |  |
| 44 | definition_property | caption | section | $defs.section.properties.caption | string | true |  | high | 未レビュー | 未確認 | 未承認 |  |
| 45 | definition_property | type | section | $defs.section.properties.type | string enum[2] | true |  | high | 未レビュー | 未確認 | 未承認 |  |
| 46 | definition_property | role | section | $defs.section.properties.role | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 47 | definition_property | dataPath | section | $defs.section.properties.dataPath | string | true |  | high | 未レビュー | 未確認 | 未承認 |  |
| 48 | definition_property | keyField | section | $defs.section.properties.keyField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 49 | definition_property | fields | section | $defs.section.properties.fields | array<ref: field> | true | field | high | 未レビュー | 未確認 | 未承認 |  |
| 50 | definition_property | markdown | section | $defs.section.properties.markdown | ref: markdownSectionOptions | false | markdownSectionOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 51 | definition | field | $defs | $defs.field | object{26 properties} | false | fieldType, optionItem, gridOptions, editOptions, searchOptions, validationOptions, createOptions | high | 未レビュー | 未確認 | 未承認 |  |
| 52 | definition_property | field | field | $defs.field.properties.field | string | true |  | high | 未レビュー | 未確認 | 未承認 |  |
| 53 | definition_property | caption | field | $defs.field.properties.caption | string | true |  | high | 未レビュー | 未確認 | 未承認 |  |
| 54 | definition_property | type | field | $defs.field.properties.type | ref: fieldType | true | fieldType | high | 未レビュー | 未確認 | 未承認 |  |
| 55 | definition_property | readonly | field | $defs.field.properties.readonly | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 56 | definition_property | options | field | $defs.field.properties.options | array<ref: optionItem> | false | optionItem | medium | 未レビュー | 未確認 | 未承認 |  |
| 57 | definition_property | grid | field | $defs.field.properties.grid | ref: gridOptions | false | gridOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 58 | definition_property | edit | field | $defs.field.properties.edit | ref: editOptions | false | editOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 59 | definition_property | search | field | $defs.field.properties.search | ref: searchOptions | false | searchOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 60 | definition_property | format | field | $defs.field.properties.format | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 61 | definition_property | defaultValue | field | $defs.field.properties.defaultValue | bool | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 62 | definition_property | validation | field | $defs.field.properties.validation | ref: validationOptions | false | validationOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 63 | definition_property | create | field | $defs.field.properties.create | ref: createOptions | false | createOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 64 | definition_property | layout | field | $defs.field.properties.layout | object{3 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 | Detail Dialog内の配置制御。例: {"placement":"detailFooter"} で子配列表示後に描画する。 |
| 65 | definition_property | control | field | $defs.field.properties.control | string enum[3] | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 66 | definition_property | fieldType | field | $defs.field.properties.fieldType | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 67 | definition_property | field_type | field | $defs.field.properties.field_type | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 68 | definition_property | typeRef | field | $defs.field.properties.typeRef | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 69 | definition_property | type_ref | field | $defs.field.properties.type_ref | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 70 | definition_property | valueField | field | $defs.field.properties.valueField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 71 | definition_property | value_field | field | $defs.field.properties.value_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 72 | definition_property | optionValueField | field | $defs.field.properties.optionValueField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 73 | definition_property | option_value_field | field | $defs.field.properties.option_value_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 74 | definition_property | labelField | field | $defs.field.properties.labelField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 75 | definition_property | label_field | field | $defs.field.properties.label_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 76 | definition_property | optionLabelField | field | $defs.field.properties.optionLabelField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 77 | definition_property | option_label_field | field | $defs.field.properties.option_label_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 78 | definition | fieldType | $defs | $defs.fieldType | string enum[9] | false |  | high | 未レビュー | 未確認 | 未承認 |  |
| 79 | definition | gridOptions | $defs | $defs.gridOptions | object{3 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 80 | definition_property | visible | gridOptions | $defs.gridOptions.properties.visible | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 81 | definition_property | width | gridOptions | $defs.gridOptions.properties.width | number | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 82 | definition_property | format | gridOptions | $defs.gridOptions.properties.format | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 83 | definition | editOptions | $defs | $defs.editOptions | object{11 properties} | false | chatEmbeddedField, chatEmbeddedField, markdownInlineOptions, markdownInlineOptions | high | 未レビュー | 未確認 | 未承認 |  |
| 84 | definition_property | visible | editOptions | $defs.editOptions.properties.visible | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 85 | definition_property | readonly | editOptions | $defs.editOptions.properties.readonly | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 86 | definition_property | height | editOptions | $defs.editOptions.properties.height | number | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 87 | definition_property | step | editOptions | $defs.editOptions.properties.step | string \| number | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 88 | definition_property | min | editOptions | $defs.editOptions.properties.min | string \| number | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 89 | definition_property | max | editOptions | $defs.editOptions.properties.max | string \| number | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 90 | definition_property | format | editOptions | $defs.editOptions.properties.format | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 91 | definition_property | control | editOptions | $defs.editOptions.properties.control | string enum[3] | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 92 | definition_property | messages | editOptions | $defs.editOptions.properties.messages | array<object{9 properties}> | false | chatEmbeddedField, chatEmbeddedField, markdownInlineOptions | medium | 未レビュー | 未確認 | 未承認 | Field type chat用。複数フィールドを会話タイムラインとして表示するためのメッセージ定義。 |
| 93 | definition_property | layout | editOptions | $defs.editOptions.properties.layout | object{3 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 | Fieldのedit表示における配置制御。field.layout と同じ意味で利用可能。 |
| 94 | definition_property | input | editOptions | $defs.editOptions.properties.input | object{14 properties} | false | markdownInlineOptions | medium | 未レビュー | 未確認 | 未承認 | Field type chat用のコメント追加入力バー設定。 |
| 95 | definition | searchOptions | $defs | $defs.searchOptions | object{2 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 96 | definition_property | visible | searchOptions | $defs.searchOptions.properties.visible | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 97 | definition_property | operator | searchOptions | $defs.searchOptions.properties.operator | string enum[4] | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 98 | definition | validationOptions | $defs | $defs.validationOptions | object{1 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 99 | definition_property | required | validationOptions | $defs.validationOptions.properties.required | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 100 | definition | createOptions | $defs | $defs.createOptions | object{1 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 101 | definition_property | include | createOptions | $defs.createOptions.properties.include | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 102 | definition | markdownOptions | $defs | $defs.markdownOptions | object{8 properties} | false | markdownSectionOptions | high | 未レビュー | 未確認 | 未承認 | Data JSON export configuration used by Markdown出力→Viewer. Not used for ViewDef Markdown→Viewer. |
| 103 | definition_property | enabled | markdownOptions | $defs.markdownOptions.properties.enabled | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 104 | definition_property | type | markdownOptions | $defs.markdownOptions.properties.type | string enum[5] | false |  | medium | 未レビュー | 未確認 | 未承認 | MarkdownExportRegistry key. Current registered values: auto, generic_sections, screen_state_expected, screen_state_diff, screen_state_test_patterns. |
| 105 | definition_property | exportType | markdownOptions | $defs.markdownOptions.properties.exportType | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 106 | definition_property | title | markdownOptions | $defs.markdownOptions.properties.title | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 107 | definition_property | fileName | markdownOptions | $defs.markdownOptions.properties.fileName | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 108 | definition_property | filename | markdownOptions | $defs.markdownOptions.properties.filename | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 109 | definition_property | defaultFileName | markdownOptions | $defs.markdownOptions.properties.defaultFileName | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 110 | definition_property | sections | markdownOptions | $defs.markdownOptions.properties.sections | array<ref: markdownSectionOptions> | false | markdownSectionOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 111 | definition | markdownSectionOptions | $defs | $defs.markdownSectionOptions | object{12 properties} | false | markdownFieldOptions, aiPromptOptions, aiPromptOptions, markdownSectionOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 112 | definition_property | title | markdownSectionOptions | $defs.markdownSectionOptions.properties.title | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 113 | definition_property | source | markdownSectionOptions | $defs.markdownSectionOptions.properties.source | string enum[8] | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 114 | definition_property | dataPath | markdownSectionOptions | $defs.markdownSectionOptions.properties.dataPath | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 115 | definition_property | arrayField | markdownSectionOptions | $defs.markdownSectionOptions.properties.arrayField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 116 | definition_property | format | markdownSectionOptions | $defs.markdownSectionOptions.properties.format | string enum[16] | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 117 | definition_property | fields | markdownSectionOptions | $defs.markdownSectionOptions.properties.fields | array<ref: markdownFieldOptions> | false | markdownFieldOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 118 | definition_property | visible | markdownSectionOptions | $defs.markdownSectionOptions.properties.visible | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 119 | definition_property | aiPrompt | markdownSectionOptions | $defs.markdownSectionOptions.properties.aiPrompt | ref: aiPromptOptions | false | aiPromptOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 120 | definition_property | ai_prompt | markdownSectionOptions | $defs.markdownSectionOptions.properties.ai_prompt | ref: aiPromptOptions | false | aiPromptOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 121 | definition_property | itemTitle | markdownSectionOptions | $defs.markdownSectionOptions.properties.itemTitle | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 122 | definition_property | showEmpty | markdownSectionOptions | $defs.markdownSectionOptions.properties.showEmpty | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 123 | definition_property | sections | markdownSectionOptions | $defs.markdownSectionOptions.properties.sections | array<ref: markdownSectionOptions> | false | markdownSectionOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 124 | definition | markdownFieldOptions | $defs | $defs.markdownFieldOptions | object{8 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 125 | definition_property | field | markdownFieldOptions | $defs.markdownFieldOptions.properties.field | string | true |  | high | 未レビュー | 未確認 | 未承認 |  |
| 126 | definition_property | caption | markdownFieldOptions | $defs.markdownFieldOptions.properties.caption | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 127 | definition_property | format | markdownFieldOptions | $defs.markdownFieldOptions.properties.format | string enum[16] | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 128 | definition_property | visible | markdownFieldOptions | $defs.markdownFieldOptions.properties.visible | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 129 | definition_property | empty | markdownFieldOptions | $defs.markdownFieldOptions.properties.empty | string \| number \| boolean \| null | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 130 | definition_property | markdownFormat | markdownFieldOptions | $defs.markdownFieldOptions.properties.markdownFormat | string enum[16] | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 131 | definition_property | showEmpty | markdownFieldOptions | $defs.markdownFieldOptions.properties.showEmpty | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 132 | definition_property | label | markdownFieldOptions | $defs.markdownFieldOptions.properties.label | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 133 | definition | viewDefReportOptions | $defs | $defs.viewDefReportOptions | object{4 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 | Future options for ViewDef Markdown→Viewer report. Separate from markdown.type. |
| 134 | definition_property | enabled | viewDefReportOptions | $defs.viewDefReportOptions.properties.enabled | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 135 | definition_property | includeInheritanceDiff | viewDefReportOptions | $defs.viewDefReportOptions.properties.includeInheritanceDiff | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 136 | definition_property | includeResolvedJson | viewDefReportOptions | $defs.viewDefReportOptions.properties.includeResolvedJson | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 137 | definition_property | includeRawJson | viewDefReportOptions | $defs.viewDefReportOptions.properties.includeRawJson | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 138 | definition | chatEmbeddedField | $defs | $defs.chatEmbeddedField | object{8 properties} | false | fieldType, optionItem, editOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 139 | definition_property | field | chatEmbeddedField | $defs.chatEmbeddedField.properties.field | string | true |  | high | 未レビュー | 未確認 | 未承認 |  |
| 140 | definition_property | label | chatEmbeddedField | $defs.chatEmbeddedField.properties.label | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 141 | definition_property | caption | chatEmbeddedField | $defs.chatEmbeddedField.properties.caption | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 142 | definition_property | type | chatEmbeddedField | $defs.chatEmbeddedField.properties.type | ref: fieldType | false | fieldType | medium | 未レビュー | 未確認 | 未承認 |  |
| 143 | definition_property | control | chatEmbeddedField | $defs.chatEmbeddedField.properties.control | string enum[3] | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 144 | definition_property | options | chatEmbeddedField | $defs.chatEmbeddedField.properties.options | array<ref: optionItem> | false | optionItem | medium | 未レビュー | 未確認 | 未承認 |  |
| 145 | definition_property | readonly | chatEmbeddedField | $defs.chatEmbeddedField.properties.readonly | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 146 | definition_property | edit | chatEmbeddedField | $defs.chatEmbeddedField.properties.edit | ref: editOptions | false | editOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 147 | definition | dataSourceSpec | $defs | $defs.dataSourceSpec | object{6 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 148 | definition_property | name | dataSourceSpec | $defs.dataSourceSpec.properties.name | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 149 | definition_property | file | dataSourceSpec | $defs.dataSourceSpec.properties.file | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 150 | definition_property | path | dataSourceSpec | $defs.dataSourceSpec.properties.path | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 151 | definition_property | data | dataSourceSpec | $defs.dataSourceSpec.properties.data | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 152 | definition_property | source | dataSourceSpec | $defs.dataSourceSpec.properties.source | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 153 | definition_property | inline | dataSourceSpec | $defs.dataSourceSpec.properties.inline | bool | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 154 | definition | dataSources | $defs | $defs.dataSources | object<additional:oneOf: string / ref: dataSourceSpec> | false | dataSourceSpec | medium | 未レビュー | 未確認 | 未承認 |  |
| 155 | definition | virtualData | $defs | $defs.virtualData | oneOf: ref: virtualDataConfig / array<ref: virtualDataConfig> | false | virtualDataConfig, virtualDataConfig | medium | 未レビュー | 未確認 | 未承認 |  |
| 156 | definition | virtualDataConfig | $defs | $defs.virtualDataConfig | object{25 properties} | false | relationAxisSource, relationAxisSource, relationAxisSource, relationAxisSource, relationQuery, relationQuery, relationQuery, relationSource, relationSource, relationSource, diffSource, diffViewDefs, diffViewDefs, virtualOutputs, virtualDataWriteBack, virtualDataWriteBack | medium | 未レビュー | 未確認 | 未承認 |  |
| 157 | definition_property | builder | virtualDataConfig | $defs.virtualDataConfig.properties.builder | string | false |  | medium | 未レビュー | 未確認 | 未承認 | VirtualDataBuilderRegistry key. Registered examples: relation_axis_cards, relation_diff_cards, relation_diff_check_cards, constraint_trace_cards, test_pattern_trace_cards, expected_check_cross_counts, expected_check_shortage_findings. |
| 158 | definition_property | type | virtualDataConfig | $defs.virtualDataConfig.properties.type | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 159 | definition_property | kind | virtualDataConfig | $defs.virtualDataConfig.properties.kind | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 160 | definition_property | targetPath | virtualDataConfig | $defs.virtualDataConfig.properties.targetPath | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 161 | definition_property | target_path | virtualDataConfig | $defs.virtualDataConfig.properties.target_path | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 162 | definition_property | dataPath | virtualDataConfig | $defs.virtualDataConfig.properties.dataPath | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 163 | definition_property | data_path | virtualDataConfig | $defs.virtualDataConfig.properties.data_path | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 164 | definition_property | axis | virtualDataConfig | $defs.virtualDataConfig.properties.axis | ref: relationAxisSource | false | relationAxisSource | medium | 未レビュー | 未確認 | 未承認 |  |
| 165 | definition_property | base | virtualDataConfig | $defs.virtualDataConfig.properties.base | ref: relationAxisSource | false | relationAxisSource | medium | 未レビュー | 未確認 | 未承認 |  |
| 166 | definition_property | linked | virtualDataConfig | $defs.virtualDataConfig.properties.linked | ref: relationAxisSource | false | relationAxisSource | medium | 未レビュー | 未確認 | 未承認 |  |
| 167 | definition_property | target | virtualDataConfig | $defs.virtualDataConfig.properties.target | ref: relationAxisSource | false | relationAxisSource | medium | 未レビュー | 未確認 | 未承認 |  |
| 168 | definition_property | relation | virtualDataConfig | $defs.virtualDataConfig.properties.relation | ref: relationQuery | false | relationQuery | medium | 未レビュー | 未確認 | 未承認 |  |
| 169 | definition_property | relationQuery | virtualDataConfig | $defs.virtualDataConfig.properties.relationQuery | ref: relationQuery | false | relationQuery | medium | 未レビュー | 未確認 | 未承認 |  |
| 170 | definition_property | relation_query | virtualDataConfig | $defs.virtualDataConfig.properties.relation_query | ref: relationQuery | false | relationQuery | medium | 未レビュー | 未確認 | 未承認 |  |
| 171 | definition_property | relations | virtualDataConfig | $defs.virtualDataConfig.properties.relations | ref: relationSource | false | relationSource | medium | 未レビュー | 未確認 | 未承認 |  |
| 172 | definition_property | relationSource | virtualDataConfig | $defs.virtualDataConfig.properties.relationSource | ref: relationSource | false | relationSource | medium | 未レビュー | 未確認 | 未承認 |  |
| 173 | definition_property | relation_source | virtualDataConfig | $defs.virtualDataConfig.properties.relation_source | ref: relationSource | false | relationSource | medium | 未レビュー | 未確認 | 未承認 |  |
| 174 | definition_property | diff | virtualDataConfig | $defs.virtualDataConfig.properties.diff | ref: diffSource | false | diffSource | medium | 未レビュー | 未確認 | 未承認 |  |
| 175 | definition_property | diffViewDefs | virtualDataConfig | $defs.virtualDataConfig.properties.diffViewDefs | ref: diffViewDefs | false | diffViewDefs | medium | 未レビュー | 未確認 | 未承認 |  |
| 176 | definition_property | diff_view_defs | virtualDataConfig | $defs.virtualDataConfig.properties.diff_view_defs | ref: diffViewDefs | false | diffViewDefs | medium | 未レビュー | 未確認 | 未承認 |  |
| 177 | definition_property | outputs | virtualDataConfig | $defs.virtualDataConfig.properties.outputs | ref: virtualOutputs | false | virtualOutputs | medium | 未レビュー | 未確認 | 未承認 |  |
| 178 | definition_property | summaryFields | virtualDataConfig | $defs.virtualDataConfig.properties.summaryFields | object<additional:any> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 179 | definition_property | summary_fields | virtualDataConfig | $defs.virtualDataConfig.properties.summary_fields | object<additional:any> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 180 | definition_property | writeBack | virtualDataConfig | $defs.virtualDataConfig.properties.writeBack | ref: virtualDataWriteBack | false | virtualDataWriteBack | medium | 未レビュー | 未確認 | 未承認 |  |
| 181 | definition_property | write_back | virtualDataConfig | $defs.virtualDataConfig.properties.write_back | ref: virtualDataWriteBack | false | virtualDataWriteBack | medium | 未レビュー | 未確認 | 未承認 |  |
| 182 | definition | relationAxisSource | $defs | $defs.relationAxisSource | object{16 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 183 | definition_property | source | relationAxisSource | $defs.relationAxisSource.properties.source | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 184 | definition_property | dataSource | relationAxisSource | $defs.relationAxisSource.properties.dataSource | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 185 | definition_property | data_source | relationAxisSource | $defs.relationAxisSource.properties.data_source | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 186 | definition_property | adapter | relationAxisSource | $defs.relationAxisSource.properties.adapter | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 187 | definition_property | kind | relationAxisSource | $defs.relationAxisSource.properties.kind | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 188 | definition_property | path | relationAxisSource | $defs.relationAxisSource.properties.path | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 189 | definition_property | dataPath | relationAxisSource | $defs.relationAxisSource.properties.dataPath | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 190 | definition_property | data_path | relationAxisSource | $defs.relationAxisSource.properties.data_path | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 191 | definition_property | fallbackPaths | relationAxisSource | $defs.relationAxisSource.properties.fallbackPaths | array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 192 | definition_property | fallback_paths | relationAxisSource | $defs.relationAxisSource.properties.fallback_paths | array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 193 | definition_property | nodeType | relationAxisSource | $defs.relationAxisSource.properties.nodeType | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 194 | definition_property | node_type | relationAxisSource | $defs.relationAxisSource.properties.node_type | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 195 | definition_property | idField | relationAxisSource | $defs.relationAxisSource.properties.idField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 196 | definition_property | id_field | relationAxisSource | $defs.relationAxisSource.properties.id_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 197 | definition_property | titleField | relationAxisSource | $defs.relationAxisSource.properties.titleField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 198 | definition_property | title_field | relationAxisSource | $defs.relationAxisSource.properties.title_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 199 | definition | relationSource | $defs | $defs.relationSource | object{6 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 200 | definition_property | source | relationSource | $defs.relationSource.properties.source | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 201 | definition_property | dataSource | relationSource | $defs.relationSource.properties.dataSource | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 202 | definition_property | data_source | relationSource | $defs.relationSource.properties.data_source | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 203 | definition_property | path | relationSource | $defs.relationSource.properties.path | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 204 | definition_property | relationsPath | relationSource | $defs.relationSource.properties.relationsPath | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 205 | definition_property | relations_path | relationSource | $defs.relationSource.properties.relations_path | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 206 | definition | relationQuery | $defs | $defs.relationQuery | object{31 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 207 | definition_property | source | relationQuery | $defs.relationQuery.properties.source | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 208 | definition_property | dataSource | relationQuery | $defs.relationQuery.properties.dataSource | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 209 | definition_property | data_source | relationQuery | $defs.relationQuery.properties.data_source | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 210 | definition_property | path | relationQuery | $defs.relationQuery.properties.path | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 211 | definition_property | relationsPath | relationQuery | $defs.relationQuery.properties.relationsPath | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 212 | definition_property | relations_path | relationQuery | $defs.relationQuery.properties.relations_path | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 213 | definition_property | name | relationQuery | $defs.relationQuery.properties.name | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 214 | definition_property | relation | relationQuery | $defs.relationQuery.properties.relation | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 215 | definition_property | relationName | relationQuery | $defs.relationQuery.properties.relationName | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 216 | definition_property | relation_name | relationQuery | $defs.relationQuery.properties.relation_name | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 217 | definition_property | direction | relationQuery | $defs.relationQuery.properties.direction | string enum[2] | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 218 | definition_property | includeViaCheck | relationQuery | $defs.relationQuery.properties.includeViaCheck | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 219 | definition_property | include_via_check | relationQuery | $defs.relationQuery.properties.include_via_check | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 220 | definition_property | verifiedByRelation | relationQuery | $defs.relationQuery.properties.verifiedByRelation | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 221 | definition_property | verified_by_relation | relationQuery | $defs.relationQuery.properties.verified_by_relation | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 222 | definition_property | containsCheckRelation | relationQuery | $defs.relationQuery.properties.containsCheckRelation | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 223 | definition_property | contains_check_relation | relationQuery | $defs.relationQuery.properties.contains_check_relation | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 224 | definition_property | testNodeType | relationQuery | $defs.relationQuery.properties.testNodeType | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 225 | definition_property | test_node_type | relationQuery | $defs.relationQuery.properties.test_node_type | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 226 | definition_property | checkType | relationQuery | $defs.relationQuery.properties.checkType | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 227 | definition_property | check_type | relationQuery | $defs.relationQuery.properties.check_type | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 228 | definition_property | constraintType | relationQuery | $defs.relationQuery.properties.constraintType | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 229 | definition_property | constraint_type | relationQuery | $defs.relationQuery.properties.constraint_type | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 230 | definition_property | statusFilter | relationQuery | $defs.relationQuery.properties.statusFilter | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 | Evidence relation statuses to include, e.g. ["approved"]. |
| 231 | definition_property | status_filter | relationQuery | $defs.relationQuery.properties.status_filter | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 | Evidence relation statuses to include, snake_case alias. |
| 232 | definition_property | structureStatusFilter | relationQuery | $defs.relationQuery.properties.structureStatusFilter | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 | Structure relation statuses to include for contains_check etc, e.g. ["derived","approved"]. |
| 233 | definition_property | structure_status_filter | relationQuery | $defs.relationQuery.properties.structure_status_filter | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 | Structure relation statuses to include, snake_case alias. |
| 234 | definition_property | excludeStatus | relationQuery | $defs.relationQuery.properties.excludeStatus | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 | Relation statuses to always exclude, e.g. ["rejected"]. |
| 235 | definition_property | exclude_status | relationQuery | $defs.relationQuery.properties.exclude_status | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 | Relation statuses to always exclude, snake_case alias. |
| 236 | definition_property | includeStatus | relationQuery | $defs.relationQuery.properties.includeStatus | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 | Alias for statusFilter. |
| 237 | definition_property | include_status | relationQuery | $defs.relationQuery.properties.include_status | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 | Alias for statusFilter, snake_case. |
| 238 | definition | diffSource | $defs | $defs.diffSource | object{10 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 239 | definition_property | source | diffSource | $defs.diffSource.properties.source | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 240 | definition_property | dataSource | diffSource | $defs.diffSource.properties.dataSource | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 241 | definition_property | data_source | diffSource | $defs.diffSource.properties.data_source | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 242 | definition_property | enabled | diffSource | $defs.diffSource.properties.enabled | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 243 | definition_property | testNodeType | diffSource | $defs.diffSource.properties.testNodeType | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 244 | definition_property | test_node_type | diffSource | $defs.diffSource.properties.test_node_type | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 245 | definition_property | testIdField | diffSource | $defs.diffSource.properties.testIdField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 246 | definition_property | test_id_field | diffSource | $defs.diffSource.properties.test_id_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 247 | definition_property | checksPath | diffSource | $defs.diffSource.properties.checksPath | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 248 | definition_property | checks_path | diffSource | $defs.diffSource.properties.checks_path | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 249 | definition | diffViewDefRef | $defs | $defs.diffViewDefRef | object{9 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 250 | definition_property | role | diffViewDefRef | $defs.diffViewDefRef.properties.role | string enum[2] | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 251 | definition_property | view_def | diffViewDefRef | $defs.diffViewDefRef.properties.view_def | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 252 | definition_property | name | diffViewDefRef | $defs.diffViewDefRef.properties.name | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 253 | definition_property | file | diffViewDefRef | $defs.diffViewDefRef.properties.file | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 254 | definition_property | caption | diffViewDefRef | $defs.diffViewDefRef.properties.caption | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 255 | definition_property | label | diffViewDefRef | $defs.diffViewDefRef.properties.label | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 256 | definition_property | extends | diffViewDefRef | $defs.diffViewDefRef.properties.extends | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 257 | definition_property | note | diffViewDefRef | $defs.diffViewDefRef.properties.note | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 258 | definition_property | active | diffViewDefRef | $defs.diffViewDefRef.properties.active | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 259 | definition | diffViewDefs | $defs | $defs.diffViewDefs | object{3 properties} | false | diffViewDefRef, diffViewDefRef, diffViewDefRef | medium | 未レビュー | 未確認 | 未承認 |  |
| 260 | definition_property | base | diffViewDefs | $defs.diffViewDefs.properties.base | ref: diffViewDefRef | false | diffViewDefRef | medium | 未レビュー | 未確認 | 未承認 |  |
| 261 | definition_property | children | diffViewDefs | $defs.diffViewDefs.properties.children | array<ref: diffViewDefRef> | false | diffViewDefRef | medium | 未レビュー | 未確認 | 未承認 |  |
| 262 | definition_property | child | diffViewDefs | $defs.diffViewDefs.properties.child | array<ref: diffViewDefRef> | false | diffViewDefRef | medium | 未レビュー | 未確認 | 未承認 |  |
| 263 | definition | virtualOutputs | $defs | $defs.virtualOutputs | object{26 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 264 | definition_property | idField | virtualOutputs | $defs.virtualOutputs.properties.idField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 265 | definition_property | id_field | virtualOutputs | $defs.virtualOutputs.properties.id_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 266 | definition_property | titleField | virtualOutputs | $defs.virtualOutputs.properties.titleField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 267 | definition_property | title_field | virtualOutputs | $defs.virtualOutputs.properties.title_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 268 | definition_property | linkedItemsField | virtualOutputs | $defs.virtualOutputs.properties.linkedItemsField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 269 | definition_property | linked_items_field | virtualOutputs | $defs.virtualOutputs.properties.linked_items_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 270 | definition_property | relatedDiffsField | virtualOutputs | $defs.virtualOutputs.properties.relatedDiffsField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 271 | definition_property | related_diffs_field | virtualOutputs | $defs.virtualOutputs.properties.related_diffs_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 272 | definition_property | failedChecksField | virtualOutputs | $defs.virtualOutputs.properties.failedChecksField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 273 | definition_property | failed_checks_field | virtualOutputs | $defs.virtualOutputs.properties.failed_checks_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 274 | definition_property | evidenceEdgesField | virtualOutputs | $defs.virtualOutputs.properties.evidenceEdgesField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 275 | definition_property | evidence_edges_field | virtualOutputs | $defs.virtualOutputs.properties.evidence_edges_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 276 | definition_property | impactedItemsField | virtualOutputs | $defs.virtualOutputs.properties.impactedItemsField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 277 | definition_property | impacted_items_field | virtualOutputs | $defs.virtualOutputs.properties.impacted_items_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 278 | definition_property | linkedCountField | virtualOutputs | $defs.virtualOutputs.properties.linkedCountField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 279 | definition_property | linked_count_field | virtualOutputs | $defs.virtualOutputs.properties.linked_count_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 280 | definition_property | primaryCountField | virtualOutputs | $defs.virtualOutputs.properties.primaryCountField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 281 | definition_property | primary_count_field | virtualOutputs | $defs.virtualOutputs.properties.primary_count_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 282 | definition_property | secondaryCountField | virtualOutputs | $defs.virtualOutputs.properties.secondaryCountField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 283 | definition_property | secondary_count_field | virtualOutputs | $defs.virtualOutputs.properties.secondary_count_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 284 | definition_property | requiredCountField | virtualOutputs | $defs.virtualOutputs.properties.requiredCountField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 285 | definition_property | required_count_field | virtualOutputs | $defs.virtualOutputs.properties.required_count_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 286 | definition_property | failLinkedCountField | virtualOutputs | $defs.virtualOutputs.properties.failLinkedCountField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 287 | definition_property | fail_linked_count_field | virtualOutputs | $defs.virtualOutputs.properties.fail_linked_count_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 288 | definition_property | coverageField | virtualOutputs | $defs.virtualOutputs.properties.coverageField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 289 | definition_property | coverage_field | virtualOutputs | $defs.virtualOutputs.properties.coverage_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 290 | definition | writePolicy | $defs | $defs.writePolicy | object{13 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 291 | definition_property | mode | writePolicy | $defs.writePolicy.properties.mode | string enum[3] | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 292 | definition_property | primarySource | writePolicy | $defs.writePolicy.properties.primarySource | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 293 | definition_property | primary_source | writePolicy | $defs.writePolicy.properties.primary_source | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 294 | definition_property | virtualDataReadonly | writePolicy | $defs.writePolicy.properties.virtualDataReadonly | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 295 | definition_property | virtual_data_readonly | writePolicy | $defs.writePolicy.properties.virtual_data_readonly | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 296 | definition_property | editableSources | writePolicy | $defs.writePolicy.properties.editableSources | array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 297 | definition_property | editable_sources | writePolicy | $defs.writePolicy.properties.editable_sources | array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 298 | definition_property | readonlySources | writePolicy | $defs.writePolicy.properties.readonlySources | array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 299 | definition_property | readonly_sources | writePolicy | $defs.writePolicy.properties.readonly_sources | array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 300 | definition_property | primaryPath | writePolicy | $defs.writePolicy.properties.primaryPath | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 301 | definition_property | primary_path | writePolicy | $defs.writePolicy.properties.primary_path | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 302 | definition_property | editableFields | writePolicy | $defs.writePolicy.properties.editableFields | array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 303 | definition_property | editable_fields | writePolicy | $defs.writePolicy.properties.editable_fields | array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 304 | definition | writeBackFieldMap | $defs | $defs.writeBackFieldMap | oneOf: string / object{7 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 305 | definition | virtualDataWriteBack | $defs | $defs.virtualDataWriteBack | object{14 properties} | false | writeBackFieldMap | medium | 未レビュー | 未確認 | 未承認 | virtualDataで生成された仮想行から、主たる更新対象JSON 1つへ一部フィールドを書き戻すための定義。 |
| 306 | definition_property | enabled | virtualDataWriteBack | $defs.virtualDataWriteBack.properties.enabled | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 307 | definition_property | source | virtualDataWriteBack | $defs.virtualDataWriteBack.properties.source | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 308 | definition_property | dataSource | virtualDataWriteBack | $defs.virtualDataWriteBack.properties.dataSource | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 309 | definition_property | data_source | virtualDataWriteBack | $defs.virtualDataWriteBack.properties.data_source | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 310 | definition_property | path | virtualDataWriteBack | $defs.virtualDataWriteBack.properties.path | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 311 | definition_property | dataPath | virtualDataWriteBack | $defs.virtualDataWriteBack.properties.dataPath | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 312 | definition_property | data_path | virtualDataWriteBack | $defs.virtualDataWriteBack.properties.data_path | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 313 | definition_property | keyField | virtualDataWriteBack | $defs.virtualDataWriteBack.properties.keyField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 314 | definition_property | key_field | virtualDataWriteBack | $defs.virtualDataWriteBack.properties.key_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 315 | definition_property | rowKeyField | virtualDataWriteBack | $defs.virtualDataWriteBack.properties.rowKeyField | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 316 | definition_property | row_key_field | virtualDataWriteBack | $defs.virtualDataWriteBack.properties.row_key_field | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 317 | definition_property | fields | virtualDataWriteBack | $defs.virtualDataWriteBack.properties.fields | oneOf: array<ref: writeBackFieldMap> / object<additional:string> | false | writeBackFieldMap | medium | 未レビュー | 未確認 | 未承認 | 書き戻し対象フィールド。同名配列、from/to配列、または {仮想field: 元field} のmap。 |
| 318 | definition_property | fieldMap | virtualDataWriteBack | $defs.virtualDataWriteBack.properties.fieldMap | object<additional:string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 319 | definition_property | field_map | virtualDataWriteBack | $defs.virtualDataWriteBack.properties.field_map | object<additional:string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 320 | definition | optionItem | $defs | $defs.optionItem | oneOf: string / number / boolean / object{8 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 321 | definition | layoutOptions | $defs | $defs.layoutOptions | object{2 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 | View/layout options. Runtime currently uses detailDialog: wide for wide detail dialog. String layout header-search-grid-detail is still valid. |
| 322 | definition_property | detailDialog | layoutOptions | $defs.layoutOptions.properties.detailDialog | string enum[2] | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 323 | definition_property | detail_dialog | layoutOptions | $defs.layoutOptions.properties.detail_dialog | string enum[2] | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 324 | definition | executeButtonOptions | $defs | $defs.executeButtonOptions | anyOf: unspecified / unspecified / unspecified | false |  | medium | 未レビュー | 未確認 | 未承認 | View-specific primary execute action. Runtime reads action/actionId/action_id as actionId and passes it to ActionRegistry. Do not hard-code Action names in Runtime. |
| 325 | definition_property | visible | executeButtonOptions | $defs.executeButtonOptions.properties.visible | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 326 | definition_property | caption | executeButtonOptions | $defs.executeButtonOptions.properties.caption | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 327 | definition_property | label | executeButtonOptions | $defs.executeButtonOptions.properties.label | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 328 | definition_property | action | executeButtonOptions | $defs.executeButtonOptions.properties.action | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 329 | definition_property | actionId | executeButtonOptions | $defs.executeButtonOptions.properties.actionId | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 330 | definition_property | action_id | executeButtonOptions | $defs.executeButtonOptions.properties.action_id | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 331 | definition | toolbarButtonOptions | $defs | $defs.toolbarButtonOptions | object{6 properties} | false |  | medium | 未レビュー | 未確認 | 未承認 | Reserved for future secondary toolbar buttons. v0.6 runtime only renders executeButton. |
| 332 | definition_property | visible | toolbarButtonOptions | $defs.toolbarButtonOptions.properties.visible | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 333 | definition_property | caption | toolbarButtonOptions | $defs.toolbarButtonOptions.properties.caption | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 334 | definition_property | label | toolbarButtonOptions | $defs.toolbarButtonOptions.properties.label | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 335 | definition_property | action | toolbarButtonOptions | $defs.toolbarButtonOptions.properties.action | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 336 | definition_property | actionId | toolbarButtonOptions | $defs.toolbarButtonOptions.properties.actionId | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 337 | definition_property | action_id | toolbarButtonOptions | $defs.toolbarButtonOptions.properties.action_id | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 338 | definition | toolbarOptions | $defs | $defs.toolbarOptions | object{3 properties} | false | executeButtonOptions, executeButtonOptions, toolbarButtonOptions | high | 未レビュー | 未確認 | 未承認 | Toolbar declarations. Current runtime supports toolbar.executeButton / toolbar.execute_button as the primary View action. |
| 339 | definition_property | executeButton | toolbarOptions | $defs.toolbarOptions.properties.executeButton | ref: executeButtonOptions | false | executeButtonOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 340 | definition_property | execute_button | toolbarOptions | $defs.toolbarOptions.properties.execute_button | ref: executeButtonOptions | false | executeButtonOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 341 | definition_property | buttons | toolbarOptions | $defs.toolbarOptions.properties.buttons | array<ref: toolbarButtonOptions> | false | toolbarButtonOptions | medium | 未レビュー | 未確認 | 未承認 |  |
| 342 | definition | aiPromptOptions | $defs | $defs.aiPromptOptions | object{11 properties} | false |  | high | 未レビュー | 未確認 | 未承認 | Markdown export AI copy block. Attach to grid section markdown.aiPrompt. |
| 343 | definition_property | enabled | aiPromptOptions | $defs.aiPromptOptions.properties.enabled | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 344 | definition_property | title | aiPromptOptions | $defs.aiPromptOptions.properties.title | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 345 | definition_property | targetFile | aiPromptOptions | $defs.aiPromptOptions.properties.targetFile | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 346 | definition_property | target_file | aiPromptOptions | $defs.aiPromptOptions.properties.target_file | string | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 347 | definition_property | rowSource | aiPromptOptions | $defs.aiPromptOptions.properties.rowSource | string enum[4] | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 348 | definition_property | row_source | aiPromptOptions | $defs.aiPromptOptions.properties.row_source | string enum[4] | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 349 | definition_property | visibleOnly | aiPromptOptions | $defs.aiPromptOptions.properties.visibleOnly | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 350 | definition_property | visible_only | aiPromptOptions | $defs.aiPromptOptions.properties.visible_only | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 351 | definition_property | includeGridJson | aiPromptOptions | $defs.aiPromptOptions.properties.includeGridJson | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 352 | definition_property | include_grid_json | aiPromptOptions | $defs.aiPromptOptions.properties.include_grid_json | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 353 | definition_property | template | aiPromptOptions | $defs.aiPromptOptions.properties.template | oneOf: string / array<string> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 354 | definition | markdownInlineOptions | $defs | $defs.markdownInlineOptions | object{6 properties} | false |  | high | 未レビュー | 未確認 | 未承認 | chat/textarea内のMarkdownリンク・画像記法の表示許可。保存値はMarkdown原文のまま保持する。 |
| 355 | definition_property | enabled | markdownInlineOptions | $defs.markdownInlineOptions.properties.enabled | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 356 | definition_property | inline | markdownInlineOptions | $defs.markdownInlineOptions.properties.inline | oneOf: boolean / object<additional:any> | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 357 | definition_property | allowLinks | markdownInlineOptions | $defs.markdownInlineOptions.properties.allowLinks | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 358 | definition_property | allow_links | markdownInlineOptions | $defs.markdownInlineOptions.properties.allow_links | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 359 | definition_property | allowImages | markdownInlineOptions | $defs.markdownInlineOptions.properties.allowImages | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |
| 360 | definition_property | allow_images | markdownInlineOptions | $defs.markdownInlineOptions.properties.allow_images | boolean | false |  | medium | 未レビュー | 未確認 | 未承認 |  |

## Schema項目詳細


### properties.app
- Item ID: root_property__app
- 種別: root_property
- 名前: app
- 型概要: object{2 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "name": {
      "type": "string"
    },
    "version": {
      "type": "string"
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| name | string | false |  |  |  |
| version | string | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### properties.views
- Item ID: root_property__views
- 種別: root_property
- 名前: views
- 型概要: array<ref: view>
- 必須: true
- 参照: view
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "minItems": 1,
  "items": {
    "$ref": "#/$defs/view"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |
| minItems | 1 |
| $ref(s) | view |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### properties.extends
- Item ID: root_property__extends
- 種別: root_property
- 名前: extends
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

ViewDef inheritance. String or array of parent view_def JSON file names.

##### Raw Schema JSON

{
  "description": "ViewDef inheritance. String or array of parent view_def JSON file names.",
  "oneOf": [
    {
      "type": "string",
      "minLength": 1
    },
    {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1
      }
    }
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### properties.viewDefReport
- Item ID: root_property__viewDefReport
- 種別: root_property
- 名前: viewDefReport
- 型概要: ref: viewDefReportOptions
- 必須: false
- 参照: viewDefReportOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/viewDefReportOptions"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | viewDefReportOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### properties.dataSources
- Item ID: root_property__dataSources
- 種別: root_property
- 名前: dataSources
- 型概要: ref: dataSources
- 必須: false
- 参照: dataSources
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/dataSources"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | dataSources |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### properties.data_sources
- Item ID: root_property__data_sources
- 種別: root_property
- 名前: data_sources
- 型概要: ref: dataSources
- 必須: false
- 参照: dataSources
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/dataSources"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | dataSources |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### properties.virtualData
- Item ID: root_property__virtualData
- 種別: root_property
- 名前: virtualData
- 型概要: ref: virtualData
- 必須: false
- 参照: virtualData
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/virtualData"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | virtualData |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### properties.virtual_data
- Item ID: root_property__virtual_data
- 種別: root_property
- 名前: virtual_data
- 型概要: ref: virtualData
- 必須: false
- 参照: virtualData
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/virtualData"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | virtualData |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### properties.writePolicy
- Item ID: root_property__writePolicy
- 種別: root_property
- 名前: writePolicy
- 型概要: ref: writePolicy
- 必須: false
- 参照: writePolicy
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/writePolicy"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | writePolicy |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### properties.write_policy
- Item ID: root_property__write_policy
- 種別: root_property
- 名前: write_policy
- 型概要: ref: writePolicy
- 必須: false
- 参照: writePolicy
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/writePolicy"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | writePolicy |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### properties.fieldTypeSources
- Item ID: root_property__fieldTypeSources
- 種別: root_property
- 名前: fieldTypeSources
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### properties.field_type_sources
- Item ID: root_property__field_type_sources
- 種別: root_property
- 名前: field_type_sources
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### properties.typeSources
- Item ID: root_property__typeSources
- 種別: root_property
- 名前: typeSources
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### properties.type_sources
- Item ID: root_property__type_sources
- 種別: root_property
- 名前: type_sources
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### properties.commonTypeRegistry
- Item ID: root_property__commonTypeRegistry
- 種別: root_property
- 名前: commonTypeRegistry
- 型概要: object<additional:any>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### properties.common_type_registry
- Item ID: root_property__common_type_registry
- 種別: root_property
- 名前: common_type_registry
- 型概要: object<additional:any>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### properties.commonTypes
- Item ID: root_property__commonTypes
- 種別: root_property
- 名前: commonTypes
- 型概要: object<additional:any>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### properties.common_types
- Item ID: root_property__common_types
- 種別: root_property
- 名前: common_types
- 型概要: object<additional:any>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### properties.toolbar
- Item ID: root_property__toolbar
- 種別: root_property
- 名前: toolbar
- 型概要: ref: toolbarOptions
- 必須: false
- 参照: toolbarOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/toolbarOptions"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | toolbarOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view
- Item ID: def__view
- 種別: definition
- 名前: view
- 親: $defs
- 型概要: object{21 properties}
- 必須: false
- 参照: layoutOptions, section, markdownOptions, viewDefReportOptions, dataSources, dataSources, virtualData, virtualData, writePolicy, writePolicy, toolbarOptions
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "id": {
      "type": "string",
      "minLength": 1
    },
    "caption": {
      "type": "string"
    },
    "layout": {
      "oneOf": [
        {
          "type": "string",
          "enum": [
            "header-search-grid-detail"
          ]
        },
        {
          "$ref": "#/$defs/layoutOptions"
        }
      ]
    },
    "sections": {
      "type": "array",
      "minItems": 1,
      "items": {
        "$ref": "#/$defs/section"
      }
    },
    "markdown": {
      "$ref": "#/$defs/markdownOptions"
    },
    "viewDefReport": {
      "$ref": "#/$defs/viewDefReportOptions"
    },
    "dataSources": {
      "$ref": "#/$defs/dataSources"
    },
    "data_sources": {
      "$ref": "#/$defs/dataSources"
    },
    "virtualData": {
      "$ref": "#/$defs/virtualData"
    },
    "virtual_data": {
      "$ref": "#/$defs/virtualData"
    },
    "writePolicy": {
      "$ref": "#/$defs/writePolicy"
    },
    "write_policy": {
      "$ref": "#/$defs/writePolicy"
    },
    "toolbar": {
      "$ref": "#/$defs/toolbarOptions"
    },
    "fieldTypeSources": {
      "oneOf": [
        {
          "type": "string"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      ]
    },
    "field_type_sources": {
      "oneOf": [
        {
          "type": "string"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      ]
    },
    "typeSources": {
      "oneOf": [
        {
          "type": "string"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      ]
    },
    "type_sources": {
      "oneOf": [
        {
          "type": "string"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      ]
    },
    "commonTypeRegistry": {
      "type": "object",
      "additionalProperties": true
    },
    "common_type_registry": {
      "type": "object",
      "additionalProperties": true
    },
    "commonTypes": {
      "type": "object",
      "additionalProperties": true
    },
    "common_types": {
      "type": "object",
      "additionalProperties": true
    }
  },
  "required": [
    "id",
    "caption",
    "layout",
    "sections"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |
| $ref(s) | layoutOptions, section, markdownOptions, viewDefReportOptions, dataSources, dataSources, virtualData, virtualData, writePolicy, writePolicy, toolbarOptions |
| required | id, caption, layout, sections |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| id | string | true |  |  |  |
| caption | string | true |  |  |  |
| layout | oneOf: string enum[1] / ref: layoutOptions | true | layoutOptions | header-search-grid-detail |  |
| sections | array<ref: section> | true | section |  |  |
| markdown | ref: markdownOptions | false | markdownOptions |  |  |
| viewDefReport | ref: viewDefReportOptions | false | viewDefReportOptions |  |  |
| dataSources | ref: dataSources | false | dataSources |  |  |
| data_sources | ref: dataSources | false | dataSources |  |  |
| virtualData | ref: virtualData | false | virtualData |  |  |
| virtual_data | ref: virtualData | false | virtualData |  |  |
| writePolicy | ref: writePolicy | false | writePolicy |  |  |
| write_policy | ref: writePolicy | false | writePolicy |  |  |
| toolbar | ref: toolbarOptions | false | toolbarOptions |  |  |
| fieldTypeSources | oneOf: string / array<string> | false |  |  |  |
| field_type_sources | oneOf: string / array<string> | false |  |  |  |
| typeSources | oneOf: string / array<string> | false |  |  |  |
| type_sources | oneOf: string / array<string> | false |  |  |  |
| commonTypeRegistry | object<additional:any> | false |  |  |  |
| common_type_registry | object<additional:any> | false |  |  |  |
| commonTypes | object<additional:any> | false |  |  |  |
| common_types | object<additional:any> | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.id
- Item ID: defprop__view__id
- 種別: definition_property
- 名前: id
- 親: view
- 型概要: string
- 必須: true
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "minLength": 1
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| minLength | 1 |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.caption
- Item ID: defprop__view__caption
- 種別: definition_property
- 名前: caption
- 親: view
- 型概要: string
- 必須: true
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.layout
- Item ID: defprop__view__layout
- 種別: definition_property
- 名前: layout
- 親: view
- 型概要: oneOf: string enum[1] / ref: layoutOptions
- 必須: true
- 参照: layoutOptions
- Enum: header-search-grid-detail
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string",
      "enum": [
        "header-search-grid-detail"
      ]
    },
    {
      "$ref": "#/$defs/layoutOptions"
    }
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |
| $ref(s) | layoutOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.sections
- Item ID: defprop__view__sections
- 種別: definition_property
- 名前: sections
- 親: view
- 型概要: array<ref: section>
- 必須: true
- 参照: section
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "minItems": 1,
  "items": {
    "$ref": "#/$defs/section"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |
| minItems | 1 |
| $ref(s) | section |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.markdown
- Item ID: defprop__view__markdown
- 種別: definition_property
- 名前: markdown
- 親: view
- 型概要: ref: markdownOptions
- 必須: false
- 参照: markdownOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/markdownOptions"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | markdownOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.viewDefReport
- Item ID: defprop__view__viewDefReport
- 種別: definition_property
- 名前: viewDefReport
- 親: view
- 型概要: ref: viewDefReportOptions
- 必須: false
- 参照: viewDefReportOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/viewDefReportOptions"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | viewDefReportOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.dataSources
- Item ID: defprop__view__dataSources
- 種別: definition_property
- 名前: dataSources
- 親: view
- 型概要: ref: dataSources
- 必須: false
- 参照: dataSources
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/dataSources"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | dataSources |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.data_sources
- Item ID: defprop__view__data_sources
- 種別: definition_property
- 名前: data_sources
- 親: view
- 型概要: ref: dataSources
- 必須: false
- 参照: dataSources
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/dataSources"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | dataSources |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.virtualData
- Item ID: defprop__view__virtualData
- 種別: definition_property
- 名前: virtualData
- 親: view
- 型概要: ref: virtualData
- 必須: false
- 参照: virtualData
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/virtualData"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | virtualData |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.virtual_data
- Item ID: defprop__view__virtual_data
- 種別: definition_property
- 名前: virtual_data
- 親: view
- 型概要: ref: virtualData
- 必須: false
- 参照: virtualData
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/virtualData"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | virtualData |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.writePolicy
- Item ID: defprop__view__writePolicy
- 種別: definition_property
- 名前: writePolicy
- 親: view
- 型概要: ref: writePolicy
- 必須: false
- 参照: writePolicy
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/writePolicy"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | writePolicy |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.write_policy
- Item ID: defprop__view__write_policy
- 種別: definition_property
- 名前: write_policy
- 親: view
- 型概要: ref: writePolicy
- 必須: false
- 参照: writePolicy
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/writePolicy"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | writePolicy |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.toolbar
- Item ID: defprop__view__toolbar
- 種別: definition_property
- 名前: toolbar
- 親: view
- 型概要: ref: toolbarOptions
- 必須: false
- 参照: toolbarOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/toolbarOptions"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | toolbarOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.fieldTypeSources
- Item ID: defprop__view__fieldTypeSources
- 種別: definition_property
- 名前: fieldTypeSources
- 親: view
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.field_type_sources
- Item ID: defprop__view__field_type_sources
- 種別: definition_property
- 名前: field_type_sources
- 親: view
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.typeSources
- Item ID: defprop__view__typeSources
- 種別: definition_property
- 名前: typeSources
- 親: view
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.type_sources
- Item ID: defprop__view__type_sources
- 種別: definition_property
- 名前: type_sources
- 親: view
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.commonTypeRegistry
- Item ID: defprop__view__commonTypeRegistry
- 種別: definition_property
- 名前: commonTypeRegistry
- 親: view
- 型概要: object<additional:any>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.common_type_registry
- Item ID: defprop__view__common_type_registry
- 種別: definition_property
- 名前: common_type_registry
- 親: view
- 型概要: object<additional:any>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.commonTypes
- Item ID: defprop__view__commonTypes
- 種別: definition_property
- 名前: commonTypes
- 親: view
- 型概要: object<additional:any>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.view.properties.common_types
- Item ID: defprop__view__common_types
- 種別: definition_property
- 名前: common_types
- 親: view
- 型概要: object<additional:any>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.section
- Item ID: def__section
- 種別: definition
- 名前: section
- 親: $defs
- 型概要: object{8 properties}
- 必須: false
- 参照: field, markdownSectionOptions
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "id": {
      "type": "string",
      "minLength": 1
    },
    "caption": {
      "type": "string"
    },
    "type": {
      "type": "string",
      "enum": [
        "form",
        "grid"
      ]
    },
    "role": {
      "type": "string"
    },
    "dataPath": {
      "type": "string",
      "minLength": 1,
      "pattern": "^\\$($|\\.[A-Za-z0-9_]+(\\.[A-Za-z0-9_]+)*)|^[A-Za-z0-9_]+(\\.[A-Za-z0-9_]+)*$"
    },
    "keyField": {
      "type": "string"
    },
    "fields": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/field"
      }
    },
    "markdown": {
      "$ref": "#/$defs/markdownSectionOptions"
    }
  },
  "required": [
    "id",
    "caption",
    "type",
    "dataPath",
    "fields"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |
| $ref(s) | field, markdownSectionOptions |
| required | id, caption, type, dataPath, fields |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| id | string | true |  |  |  |
| caption | string | true |  |  |  |
| type | string enum[2] | true |  | form, grid |  |
| role | string | false |  |  |  |
| dataPath | string | true |  |  |  |
| keyField | string | false |  |  |  |
| fields | array<ref: field> | true | field |  |  |
| markdown | ref: markdownSectionOptions | false | markdownSectionOptions |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.section.properties.id
- Item ID: defprop__section__id
- 種別: definition_property
- 名前: id
- 親: section
- 型概要: string
- 必須: true
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "minLength": 1
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| minLength | 1 |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.section.properties.caption
- Item ID: defprop__section__caption
- 種別: definition_property
- 名前: caption
- 親: section
- 型概要: string
- 必須: true
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.section.properties.type
- Item ID: defprop__section__type
- 種別: definition_property
- 名前: type
- 親: section
- 型概要: string enum[2]
- 必須: true
- Enum: form, grid
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "form",
    "grid"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | form, grid |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.section.properties.role
- Item ID: defprop__section__role
- 種別: definition_property
- 名前: role
- 親: section
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.section.properties.dataPath
- Item ID: defprop__section__dataPath
- 種別: definition_property
- 名前: dataPath
- 親: section
- 型概要: string
- 必須: true
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "minLength": 1,
  "pattern": "^\\$($|\\.[A-Za-z0-9_]+(\\.[A-Za-z0-9_]+)*)|^[A-Za-z0-9_]+(\\.[A-Za-z0-9_]+)*$"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| minLength | 1 |
| pattern | ^\$($\|\.[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)*)\|^[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)*$ |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.section.properties.keyField
- Item ID: defprop__section__keyField
- 種別: definition_property
- 名前: keyField
- 親: section
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.section.properties.fields
- Item ID: defprop__section__fields
- 種別: definition_property
- 名前: fields
- 親: section
- 型概要: array<ref: field>
- 必須: true
- 参照: field
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "items": {
    "$ref": "#/$defs/field"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |
| $ref(s) | field |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.section.properties.markdown
- Item ID: defprop__section__markdown
- 種別: definition_property
- 名前: markdown
- 親: section
- 型概要: ref: markdownSectionOptions
- 必須: false
- 参照: markdownSectionOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/markdownSectionOptions"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | markdownSectionOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field
- Item ID: def__field
- 種別: definition
- 名前: field
- 親: $defs
- 型概要: object{26 properties}
- 必須: false
- 参照: fieldType, optionItem, gridOptions, editOptions, searchOptions, validationOptions, createOptions
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "field": {
      "type": "string",
      "minLength": 1,
      "pattern": "^[A-Za-z0-9_]+(\\.[A-Za-z0-9_]+)*$"
    },
    "caption": {
      "type": "string"
    },
    "type": {
      "$ref": "#/$defs/fieldType"
    },
    "readonly": {
      "type": "boolean"
    },
    "options": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/optionItem"
      }
    },
    "grid": {
      "$ref": "#/$defs/gridOptions"
    },
    "edit": {
      "$ref": "#/$defs/editOptions"
    },
    "search": {
      "$ref": "#/$defs/searchOptions"
    },
    "format": {
      "type": "string"
    },
    "defaultValue": true,
    "validation": {
      "$ref": "#/$defs/validationOptions"
    },
    "create": {
      "$ref": "#/$defs/createOptions"
    },
    "layout": {
      "type": "object",
      "additionalProperties": true,
      "description": "Detail Dialog内の配置制御。例: {\"placement\":\"detailFooter\"} で子配列表示後に描画する。",
      "properties": {
        "placement": {
          "type": "string",
          "enum": [
            "detailBody",
            "detailFooter",
            "afterChildGrids"
          ]
        },
        "after": {
          "type": "string",
          "enum": [
            "childGrids"
          ]
        },
        "order": {
          "type": "number"
        }
      }
    },
    "control": {
      "type": "string",
      "enum": [
        "combobox",
        "listbox",
        "radio"
      ]
    },
    "fieldType": {
      "type": "string"
    },
    "field_type": {
      "type": "string"
    },
    "typeRef": {
      "type": "string"
    },
    "type_ref": {
      "type": "string"
    },
    "valueField": {
      "type": "string"
    },
    "value_field": {
      "type": "string"
    },
    "optionValueField": {
      "type": "string"
    },
    "option_value_field": {
      "type": "string"
    },
    "labelField": {
      "type": "string"
    },
    "label_field": {
      "type": "string"
    },
    "optionLabelField": {
      "type": "string"
    },
    "option_label_field": {
      "type": "string"
    }
  },
  "required": [
    "field",
    "caption",
    "type"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |
| $ref(s) | fieldType, optionItem, gridOptions, editOptions, searchOptions, validationOptions, createOptions |
| required | field, caption, type |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| field | string | true |  |  |  |
| caption | string | true |  |  |  |
| type | ref: fieldType | true | fieldType |  |  |
| readonly | boolean | false |  |  |  |
| options | array<ref: optionItem> | false | optionItem |  |  |
| grid | ref: gridOptions | false | gridOptions |  |  |
| edit | ref: editOptions | false | editOptions |  |  |
| search | ref: searchOptions | false | searchOptions |  |  |
| format | string | false |  |  |  |
| defaultValue | bool | false |  |  |  |
| validation | ref: validationOptions | false | validationOptions |  |  |
| create | ref: createOptions | false | createOptions |  |  |
| layout | object{3 properties} | false |  |  | Detail Dialog内の配置制御。例: {"placement":"detailFooter"} で子配列表示後に描画する。 |
| control | string enum[3] | false |  | combobox, listbox, radio |  |
| fieldType | string | false |  |  |  |
| field_type | string | false |  |  |  |
| typeRef | string | false |  |  |  |
| type_ref | string | false |  |  |  |
| valueField | string | false |  |  |  |
| value_field | string | false |  |  |  |
| optionValueField | string | false |  |  |  |
| option_value_field | string | false |  |  |  |
| labelField | string | false |  |  |  |
| label_field | string | false |  |  |  |
| optionLabelField | string | false |  |  |  |
| option_label_field | string | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.field
- Item ID: defprop__field__field
- 種別: definition_property
- 名前: field
- 親: field
- 型概要: string
- 必須: true
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "minLength": 1,
  "pattern": "^[A-Za-z0-9_]+(\\.[A-Za-z0-9_]+)*$"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| minLength | 1 |
| pattern | ^[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)*$ |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.caption
- Item ID: defprop__field__caption
- 種別: definition_property
- 名前: caption
- 親: field
- 型概要: string
- 必須: true
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.type
- Item ID: defprop__field__type
- 種別: definition_property
- 名前: type
- 親: field
- 型概要: ref: fieldType
- 必須: true
- 参照: fieldType
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/fieldType"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | fieldType |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.readonly
- Item ID: defprop__field__readonly
- 種別: definition_property
- 名前: readonly
- 親: field
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.options
- Item ID: defprop__field__options
- 種別: definition_property
- 名前: options
- 親: field
- 型概要: array<ref: optionItem>
- 必須: false
- 参照: optionItem
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "items": {
    "$ref": "#/$defs/optionItem"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |
| $ref(s) | optionItem |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.grid
- Item ID: defprop__field__grid
- 種別: definition_property
- 名前: grid
- 親: field
- 型概要: ref: gridOptions
- 必須: false
- 参照: gridOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/gridOptions"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | gridOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.edit
- Item ID: defprop__field__edit
- 種別: definition_property
- 名前: edit
- 親: field
- 型概要: ref: editOptions
- 必須: false
- 参照: editOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/editOptions"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | editOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.search
- Item ID: defprop__field__search
- 種別: definition_property
- 名前: search
- 親: field
- 型概要: ref: searchOptions
- 必須: false
- 参照: searchOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/searchOptions"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | searchOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.format
- Item ID: defprop__field__format
- 種別: definition_property
- 名前: format
- 親: field
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.defaultValue
- Item ID: defprop__field__defaultValue
- 種別: definition_property
- 名前: defaultValue
- 親: field
- 型概要: bool
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明

- Raw Schema JSON: true

#### 制約一覧

（なし）

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.validation
- Item ID: defprop__field__validation
- 種別: definition_property
- 名前: validation
- 親: field
- 型概要: ref: validationOptions
- 必須: false
- 参照: validationOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/validationOptions"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | validationOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.create
- Item ID: defprop__field__create
- 種別: definition_property
- 名前: create
- 親: field
- 型概要: ref: createOptions
- 必須: false
- 参照: createOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/createOptions"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | createOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.layout
- Item ID: defprop__field__layout
- 種別: definition_property
- 名前: layout
- 親: field
- 型概要: object{3 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

Detail Dialog内の配置制御。例: {"placement":"detailFooter"} で子配列表示後に描画する。

##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "description": "Detail Dialog内の配置制御。例: {\"placement\":\"detailFooter\"} で子配列表示後に描画する。",
  "properties": {
    "placement": {
      "type": "string",
      "enum": [
        "detailBody",
        "detailFooter",
        "afterChildGrids"
      ]
    },
    "after": {
      "type": "string",
      "enum": [
        "childGrids"
      ]
    },
    "order": {
      "type": "number"
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| placement | string enum[3] | false |  | detailBody, detailFooter, afterChildGrids |  |
| after | string enum[1] | false |  | childGrids |  |
| order | number | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.control
- Item ID: defprop__field__control
- 種別: definition_property
- 名前: control
- 親: field
- 型概要: string enum[3]
- 必須: false
- Enum: combobox, listbox, radio
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "combobox",
    "listbox",
    "radio"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | combobox, listbox, radio |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.fieldType
- Item ID: defprop__field__fieldType
- 種別: definition_property
- 名前: fieldType
- 親: field
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.field_type
- Item ID: defprop__field__field_type
- 種別: definition_property
- 名前: field_type
- 親: field
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.typeRef
- Item ID: defprop__field__typeRef
- 種別: definition_property
- 名前: typeRef
- 親: field
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.type_ref
- Item ID: defprop__field__type_ref
- 種別: definition_property
- 名前: type_ref
- 親: field
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.valueField
- Item ID: defprop__field__valueField
- 種別: definition_property
- 名前: valueField
- 親: field
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.value_field
- Item ID: defprop__field__value_field
- 種別: definition_property
- 名前: value_field
- 親: field
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.optionValueField
- Item ID: defprop__field__optionValueField
- 種別: definition_property
- 名前: optionValueField
- 親: field
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.option_value_field
- Item ID: defprop__field__option_value_field
- 種別: definition_property
- 名前: option_value_field
- 親: field
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.labelField
- Item ID: defprop__field__labelField
- 種別: definition_property
- 名前: labelField
- 親: field
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.label_field
- Item ID: defprop__field__label_field
- 種別: definition_property
- 名前: label_field
- 親: field
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.optionLabelField
- Item ID: defprop__field__optionLabelField
- 種別: definition_property
- 名前: optionLabelField
- 親: field
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.field.properties.option_label_field
- Item ID: defprop__field__option_label_field
- 種別: definition_property
- 名前: option_label_field
- 親: field
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.fieldType
- Item ID: def__fieldType
- 種別: definition
- 名前: fieldType
- 親: $defs
- 型概要: string enum[9]
- 必須: false
- Enum: text, number, boolean, select, datetime, textarea, objectArray, stringArray, chat
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "text",
    "number",
    "boolean",
    "select",
    "datetime",
    "textarea",
    "objectArray",
    "stringArray",
    "chat"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | text, number, boolean, select, datetime, textarea, objectArray, stringArray, chat |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.gridOptions
- Item ID: def__gridOptions
- 種別: definition
- 名前: gridOptions
- 親: $defs
- 型概要: object{3 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "visible": {
      "type": "boolean"
    },
    "width": {
      "type": "number",
      "minimum": 0
    },
    "format": {
      "type": "string"
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| visible | boolean | false |  |  |  |
| width | number | false |  |  |  |
| format | string | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.gridOptions.properties.visible
- Item ID: defprop__gridOptions__visible
- 種別: definition_property
- 名前: visible
- 親: gridOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.gridOptions.properties.width
- Item ID: defprop__gridOptions__width
- 種別: definition_property
- 名前: width
- 親: gridOptions
- 型概要: number
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "number",
  "minimum": 0
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | number |
| minimum | 0 |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.gridOptions.properties.format
- Item ID: defprop__gridOptions__format
- 種別: definition_property
- 名前: format
- 親: gridOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.editOptions
- Item ID: def__editOptions
- 種別: definition
- 名前: editOptions
- 親: $defs
- 型概要: object{11 properties}
- 必須: false
- 参照: chatEmbeddedField, chatEmbeddedField, markdownInlineOptions, markdownInlineOptions
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "visible": {
      "type": "boolean"
    },
    "readonly": {
      "type": "boolean"
    },
    "height": {
      "type": "number",
      "minimum": 0
    },
    "step": {
      "type": [
        "string",
        "number"
      ]
    },
    "min": {
      "type": [
        "string",
        "number"
      ]
    },
    "max": {
      "type": [
        "string",
        "number"
      ]
    },
    "format": {
      "type": "string"
    },
    "control": {
      "type": "string",
      "enum": [
        "combobox",
        "listbox",
        "radio"
      ]
    },
    "messages": {
      "type": "array",
      "description": "Field type chat用。複数フィールドを会話タイムラインとして表示するためのメッセージ定義。",
      "items": {
        "type": "object",
        "additionalProperties": true,
        "properties": {
          "role": {
            "type": "string",
            "enum": [
              "constraint",
              "system",
              "user",
              "human",
              "ai",
              "assistant",
              "other"
            ]
          },
          "field": {
            "type": "string"
          },
          "label": {
            "type": "string"
          },
          "readonly": {
            "type": "boolean"
          },
          "height": {
            "type": "number",
            "minimum": 0
          },
          "placeholder": {
            "type": "string"
          },
          "embeddedFields": {
            "type": "array",
            "description": "chat吹き出し内に埋め込む入力フィールド。承認ラジオ等に利用する。",
            "items": {
              "$ref": "#/$defs/chatEmbeddedField"
            }
          },
          "embedded_fields": {
            "type": "array",
            "description": "chat吹き出し内に埋め込む入力フィールド。承認ラジオ等に利用する。",
            "items": {
              "$ref": "#/$defs/chatEmbeddedField"
            }
          },
          "markdown": {
            "oneOf": [
              {
                "type": "boolean"
              },
              {
                "$ref": "#/$defs/markdownInlineOptions"
              }
            ],
            "description": "このchatメッセージ本文のMarkdownリンク/画像表示許可。"
          }
        },
        "required": [
          "role",
          "field"
        ]
      }
    },
    "layout": {
      "type": "object",
      "additionalProperties": true,
      "description": "Fieldのedit表示における配置制御。field.layout と同じ意味で利用可能。",
      "properties": {
        "placement": {
          "type": "string",
          "enum": [
            "detailBody",
            "detailFooter",
            "afterChildGrids"
          ]
        },
        "after": {
          "type": "string",
          "enum": [
            "childGrids"
          ]
        },
        "order": {
          "type": "number"
        }
      }
    },
    "input": {
      "type": "object",
      "additionalProperties": true,
      "description": "Field type chat用のコメント追加入力バー設定。",
      "properties": {
        "enabled": {
          "type": "boolean"
        },
        "userField": {
          "type": "string"
        },
        "user_field": {
          "type": "string"
        },
        "aiField": {
          "type": "string"
        },
        "ai_field": {
          "type": "string"
        },
        "placeholder": {
          "type": "string"
        },
        "sendLabel": {
          "type": "string"
        },
        "send_label": {
          "type": "string"
        },
        "appendPosition": {
          "type": "string",
          "enum": [
            "afterMessages",
            "messageOrder"
          ],
          "description": "afterMessagesの場合、input.userFieldの本文をmessages定義順ではなく会話末尾に表示する。"
        },
        "append_position": {
          "type": "string",
          "enum": [
            "afterMessages",
            "messageOrder"
          ],
          "description": "afterMessagesの場合、input.userFieldの本文をmessages定義順ではなく会話末尾に表示する。"
        },
        "appendLabel": {
          "type": "string",
          "description": "appendPosition=afterMessagesで末尾表示するuserFieldのラベル。"
        },
        "append_label": {
          "type": "string",
          "description": "appendPosition=afterMessagesで末尾表示するuserFieldのラベル。"
        },
        "label": {
          "type": "string"
        },
        "markdown": {
          "oneOf": [
            {
              "type": "boolean"
            },
            {
              "$ref": "#/$defs/markdownInlineOptions"
            }
          ],
          "description": "送信欄由来のuserField本文に対するMarkdownリンク/画像表示許可。"
        }
      }
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |
| $ref(s) | chatEmbeddedField, chatEmbeddedField, markdownInlineOptions, markdownInlineOptions |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| visible | boolean | false |  |  |  |
| readonly | boolean | false |  |  |  |
| height | number | false |  |  |  |
| step | string \| number | false |  |  |  |
| min | string \| number | false |  |  |  |
| max | string \| number | false |  |  |  |
| format | string | false |  |  |  |
| control | string enum[3] | false |  | combobox, listbox, radio |  |
| messages | array<object{9 properties}> | false | chatEmbeddedField, chatEmbeddedField, markdownInlineOptions |  | Field type chat用。複数フィールドを会話タイムラインとして表示するためのメッセージ定義。 |
| layout | object{3 properties} | false |  |  | Fieldのedit表示における配置制御。field.layout と同じ意味で利用可能。 |
| input | object{14 properties} | false | markdownInlineOptions |  | Field type chat用のコメント追加入力バー設定。 |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.editOptions.properties.visible
- Item ID: defprop__editOptions__visible
- 種別: definition_property
- 名前: visible
- 親: editOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.editOptions.properties.readonly
- Item ID: defprop__editOptions__readonly
- 種別: definition_property
- 名前: readonly
- 親: editOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.editOptions.properties.height
- Item ID: defprop__editOptions__height
- 種別: definition_property
- 名前: height
- 親: editOptions
- 型概要: number
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "number",
  "minimum": 0
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | number |
| minimum | 0 |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.editOptions.properties.step
- Item ID: defprop__editOptions__step
- 種別: definition_property
- 名前: step
- 親: editOptions
- 型概要: string \| number
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": [
    "string",
    "number"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | ["string", "number"] |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.editOptions.properties.min
- Item ID: defprop__editOptions__min
- 種別: definition_property
- 名前: min
- 親: editOptions
- 型概要: string \| number
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": [
    "string",
    "number"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | ["string", "number"] |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.editOptions.properties.max
- Item ID: defprop__editOptions__max
- 種別: definition_property
- 名前: max
- 親: editOptions
- 型概要: string \| number
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": [
    "string",
    "number"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | ["string", "number"] |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.editOptions.properties.format
- Item ID: defprop__editOptions__format
- 種別: definition_property
- 名前: format
- 親: editOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.editOptions.properties.control
- Item ID: defprop__editOptions__control
- 種別: definition_property
- 名前: control
- 親: editOptions
- 型概要: string enum[3]
- 必須: false
- Enum: combobox, listbox, radio
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "combobox",
    "listbox",
    "radio"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | combobox, listbox, radio |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.editOptions.properties.messages
- Item ID: defprop__editOptions__messages
- 種別: definition_property
- 名前: messages
- 親: editOptions
- 型概要: array<object{9 properties}>
- 必須: false
- 参照: chatEmbeddedField, chatEmbeddedField, markdownInlineOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

Field type chat用。複数フィールドを会話タイムラインとして表示するためのメッセージ定義。

##### Raw Schema JSON

{
  "type": "array",
  "description": "Field type chat用。複数フィールドを会話タイムラインとして表示するためのメッセージ定義。",
  "items": {
    "type": "object",
    "additionalProperties": true,
    "properties": {
      "role": {
        "type": "string",
        "enum": [
          "constraint",
          "system",
          "user",
          "human",
          "ai",
          "assistant",
          "other"
        ]
      },
      "field": {
        "type": "string"
      },
      "label": {
        "type": "string"
      },
      "readonly": {
        "type": "boolean"
      },
      "height": {
        "type": "number",
        "minimum": 0
      },
      "placeholder": {
        "type": "string"
      },
      "embeddedFields": {
        "type": "array",
        "description": "chat吹き出し内に埋め込む入力フィールド。承認ラジオ等に利用する。",
        "items": {
          "$ref": "#/$defs/chatEmbeddedField"
        }
      },
      "embedded_fields": {
        "type": "array",
        "description": "chat吹き出し内に埋め込む入力フィールド。承認ラジオ等に利用する。",
        "items": {
          "$ref": "#/$defs/chatEmbeddedField"
        }
      },
      "markdown": {
        "oneOf": [
          {
            "type": "boolean"
          },
          {
            "$ref": "#/$defs/markdownInlineOptions"
          }
        ],
        "description": "このchatメッセージ本文のMarkdownリンク/画像表示許可。"
      }
    },
    "required": [
      "role",
      "field"
    ]
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |
| $ref(s) | chatEmbeddedField, chatEmbeddedField, markdownInlineOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.editOptions.properties.layout
- Item ID: defprop__editOptions__layout
- 種別: definition_property
- 名前: layout
- 親: editOptions
- 型概要: object{3 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

Fieldのedit表示における配置制御。field.layout と同じ意味で利用可能。

##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "description": "Fieldのedit表示における配置制御。field.layout と同じ意味で利用可能。",
  "properties": {
    "placement": {
      "type": "string",
      "enum": [
        "detailBody",
        "detailFooter",
        "afterChildGrids"
      ]
    },
    "after": {
      "type": "string",
      "enum": [
        "childGrids"
      ]
    },
    "order": {
      "type": "number"
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| placement | string enum[3] | false |  | detailBody, detailFooter, afterChildGrids |  |
| after | string enum[1] | false |  | childGrids |  |
| order | number | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.editOptions.properties.input
- Item ID: defprop__editOptions__input
- 種別: definition_property
- 名前: input
- 親: editOptions
- 型概要: object{14 properties}
- 必須: false
- 参照: markdownInlineOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

Field type chat用のコメント追加入力バー設定。

##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "description": "Field type chat用のコメント追加入力バー設定。",
  "properties": {
    "enabled": {
      "type": "boolean"
    },
    "userField": {
      "type": "string"
    },
    "user_field": {
      "type": "string"
    },
    "aiField": {
      "type": "string"
    },
    "ai_field": {
      "type": "string"
    },
    "placeholder": {
      "type": "string"
    },
    "sendLabel": {
      "type": "string"
    },
    "send_label": {
      "type": "string"
    },
    "appendPosition": {
      "type": "string",
      "enum": [
        "afterMessages",
        "messageOrder"
      ],
      "description": "afterMessagesの場合、input.userFieldの本文をmessages定義順ではなく会話末尾に表示する。"
    },
    "append_position": {
      "type": "string",
      "enum": [
        "afterMessages",
        "messageOrder"
      ],
      "description": "afterMessagesの場合、input.userFieldの本文をmessages定義順ではなく会話末尾に表示する。"
    },
    "appendLabel": {
      "type": "string",
      "description": "appendPosition=afterMessagesで末尾表示するuserFieldのラベル。"
    },
    "append_label": {
      "type": "string",
      "description": "appendPosition=afterMessagesで末尾表示するuserFieldのラベル。"
    },
    "label": {
      "type": "string"
    },
    "markdown": {
      "oneOf": [
        {
          "type": "boolean"
        },
        {
          "$ref": "#/$defs/markdownInlineOptions"
        }
      ],
      "description": "送信欄由来のuserField本文に対するMarkdownリンク/画像表示許可。"
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |
| $ref(s) | markdownInlineOptions |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| enabled | boolean | false |  |  |  |
| userField | string | false |  |  |  |
| user_field | string | false |  |  |  |
| aiField | string | false |  |  |  |
| ai_field | string | false |  |  |  |
| placeholder | string | false |  |  |  |
| sendLabel | string | false |  |  |  |
| send_label | string | false |  |  |  |
| appendPosition | string enum[2] | false |  | afterMessages, messageOrder | afterMessagesの場合、input.userFieldの本文をmessages定義順ではなく会話末尾に表示する。 |
| append_position | string enum[2] | false |  | afterMessages, messageOrder | afterMessagesの場合、input.userFieldの本文をmessages定義順ではなく会話末尾に表示する。 |
| appendLabel | string | false |  |  | appendPosition=afterMessagesで末尾表示するuserFieldのラベル。 |
| append_label | string | false |  |  | appendPosition=afterMessagesで末尾表示するuserFieldのラベル。 |
| label | string | false |  |  |  |
| markdown | oneOf: boolean / ref: markdownInlineOptions | false | markdownInlineOptions |  | 送信欄由来のuserField本文に対するMarkdownリンク/画像表示許可。 |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.searchOptions
- Item ID: def__searchOptions
- 種別: definition
- 名前: searchOptions
- 親: $defs
- 型概要: object{2 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "visible": {
      "type": "boolean"
    },
    "operator": {
      "type": "string",
      "enum": [
        "contains",
        "equals",
        "gte",
        "lte"
      ]
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| visible | boolean | false |  |  |  |
| operator | string enum[4] | false |  | contains, equals, gte, lte |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.searchOptions.properties.visible
- Item ID: defprop__searchOptions__visible
- 種別: definition_property
- 名前: visible
- 親: searchOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.searchOptions.properties.operator
- Item ID: defprop__searchOptions__operator
- 種別: definition_property
- 名前: operator
- 親: searchOptions
- 型概要: string enum[4]
- 必須: false
- Enum: contains, equals, gte, lte
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "contains",
    "equals",
    "gte",
    "lte"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | contains, equals, gte, lte |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.validationOptions
- Item ID: def__validationOptions
- 種別: definition
- 名前: validationOptions
- 親: $defs
- 型概要: object{1 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "required": {
      "type": "boolean"
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| required | boolean | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.validationOptions.properties.required
- Item ID: defprop__validationOptions__required
- 種別: definition_property
- 名前: required
- 親: validationOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.createOptions
- Item ID: def__createOptions
- 種別: definition
- 名前: createOptions
- 親: $defs
- 型概要: object{1 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "include": {
      "type": "boolean"
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| include | boolean | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.createOptions.properties.include
- Item ID: defprop__createOptions__include
- 種別: definition_property
- 名前: include
- 親: createOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownOptions
- Item ID: def__markdownOptions
- 種別: definition
- 名前: markdownOptions
- 親: $defs
- 型概要: object{8 properties}
- 必須: false
- 参照: markdownSectionOptions
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

Data JSON export configuration used by Markdown出力→Viewer. Not used for ViewDef Markdown→Viewer.

##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "description": "Data JSON export configuration used by Markdown出力→Viewer. Not used for ViewDef Markdown→Viewer.",
  "properties": {
    "enabled": {
      "type": "boolean"
    },
    "type": {
      "type": "string",
      "enum": [
        "auto",
        "generic_sections",
        "screen_state_expected",
        "screen_state_diff",
        "screen_state_test_patterns"
      ],
      "description": "MarkdownExportRegistry key. Current registered values: auto, generic_sections, screen_state_expected, screen_state_diff, screen_state_test_patterns."
    },
    "exportType": {
      "type": "string"
    },
    "title": {
      "type": "string"
    },
    "fileName": {
      "type": "string"
    },
    "filename": {
      "type": "string"
    },
    "defaultFileName": {
      "type": "string"
    },
    "sections": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/markdownSectionOptions"
      }
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |
| $ref(s) | markdownSectionOptions |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| enabled | boolean | false |  |  |  |
| type | string enum[5] | false |  | auto, generic_sections, screen_state_expected, screen_state_diff, screen_state_test_patterns | MarkdownExportRegistry key. Current registered values: auto, generic_sections, screen_state_expected, screen_state_diff, screen_state_test_patterns. |
| exportType | string | false |  |  |  |
| title | string | false |  |  |  |
| fileName | string | false |  |  |  |
| filename | string | false |  |  |  |
| defaultFileName | string | false |  |  |  |
| sections | array<ref: markdownSectionOptions> | false | markdownSectionOptions |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownOptions.properties.enabled
- Item ID: defprop__markdownOptions__enabled
- 種別: definition_property
- 名前: enabled
- 親: markdownOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownOptions.properties.type
- Item ID: defprop__markdownOptions__type
- 種別: definition_property
- 名前: type
- 親: markdownOptions
- 型概要: string enum[5]
- 必須: false
- Enum: auto, generic_sections, screen_state_expected, screen_state_diff, screen_state_test_patterns
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

MarkdownExportRegistry key. Current registered values: auto, generic_sections, screen_state_expected, screen_state_diff, screen_state_test_patterns.

##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "auto",
    "generic_sections",
    "screen_state_expected",
    "screen_state_diff",
    "screen_state_test_patterns"
  ],
  "description": "MarkdownExportRegistry key. Current registered values: auto, generic_sections, screen_state_expected, screen_state_diff, screen_state_test_patterns."
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | auto, generic_sections, screen_state_expected, screen_state_diff, screen_state_test_patterns |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownOptions.properties.exportType
- Item ID: defprop__markdownOptions__exportType
- 種別: definition_property
- 名前: exportType
- 親: markdownOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownOptions.properties.title
- Item ID: defprop__markdownOptions__title
- 種別: definition_property
- 名前: title
- 親: markdownOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownOptions.properties.fileName
- Item ID: defprop__markdownOptions__fileName
- 種別: definition_property
- 名前: fileName
- 親: markdownOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownOptions.properties.filename
- Item ID: defprop__markdownOptions__filename
- 種別: definition_property
- 名前: filename
- 親: markdownOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownOptions.properties.defaultFileName
- Item ID: defprop__markdownOptions__defaultFileName
- 種別: definition_property
- 名前: defaultFileName
- 親: markdownOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownOptions.properties.sections
- Item ID: defprop__markdownOptions__sections
- 種別: definition_property
- 名前: sections
- 親: markdownOptions
- 型概要: array<ref: markdownSectionOptions>
- 必須: false
- 参照: markdownSectionOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "items": {
    "$ref": "#/$defs/markdownSectionOptions"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |
| $ref(s) | markdownSectionOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownSectionOptions
- Item ID: def__markdownSectionOptions
- 種別: definition
- 名前: markdownSectionOptions
- 親: $defs
- 型概要: object{12 properties}
- 必須: false
- 参照: markdownFieldOptions, aiPromptOptions, aiPromptOptions, markdownSectionOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "title": {
      "type": "string"
    },
    "source": {
      "type": "string",
      "enum": [
        "root",
        "sourceData",
        "currentRow",
        "allRows",
        "header",
        "grid",
        "rows",
        "currentRows"
      ]
    },
    "dataPath": {
      "type": "string"
    },
    "arrayField": {
      "type": "string"
    },
    "format": {
      "type": "string",
      "enum": [
        "auto",
        "text",
        "paragraph",
        "textarea",
        "blockquote",
        "code",
        "json",
        "note",
        "table",
        "list",
        "cards",
        "chat",
        "heading",
        "constraintList",
        "detailList",
        "detail"
      ]
    },
    "fields": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/markdownFieldOptions"
      }
    },
    "visible": {
      "type": "boolean"
    },
    "aiPrompt": {
      "$ref": "#/$defs/aiPromptOptions"
    },
    "ai_prompt": {
      "$ref": "#/$defs/aiPromptOptions"
    },
    "itemTitle": {
      "type": "string"
    },
    "showEmpty": {
      "type": "boolean"
    },
    "sections": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/markdownSectionOptions"
      }
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |
| $ref(s) | markdownFieldOptions, aiPromptOptions, aiPromptOptions, markdownSectionOptions |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| title | string | false |  |  |  |
| source | string enum[8] | false |  | root, sourceData, currentRow, allRows, header, grid, rows, currentRows |  |
| dataPath | string | false |  |  |  |
| arrayField | string | false |  |  |  |
| format | string enum[16] | false |  | auto, text, paragraph, textarea, blockquote, code, json, note, table, list, cards, chat, heading, constraintList, detailList, detail |  |
| fields | array<ref: markdownFieldOptions> | false | markdownFieldOptions |  |  |
| visible | boolean | false |  |  |  |
| aiPrompt | ref: aiPromptOptions | false | aiPromptOptions |  |  |
| ai_prompt | ref: aiPromptOptions | false | aiPromptOptions |  |  |
| itemTitle | string | false |  |  |  |
| showEmpty | boolean | false |  |  |  |
| sections | array<ref: markdownSectionOptions> | false | markdownSectionOptions |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownSectionOptions.properties.title
- Item ID: defprop__markdownSectionOptions__title
- 種別: definition_property
- 名前: title
- 親: markdownSectionOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownSectionOptions.properties.source
- Item ID: defprop__markdownSectionOptions__source
- 種別: definition_property
- 名前: source
- 親: markdownSectionOptions
- 型概要: string enum[8]
- 必須: false
- Enum: root, sourceData, currentRow, allRows, header, grid, rows, currentRows
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "root",
    "sourceData",
    "currentRow",
    "allRows",
    "header",
    "grid",
    "rows",
    "currentRows"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | root, sourceData, currentRow, allRows, header, grid, rows, currentRows |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownSectionOptions.properties.dataPath
- Item ID: defprop__markdownSectionOptions__dataPath
- 種別: definition_property
- 名前: dataPath
- 親: markdownSectionOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownSectionOptions.properties.arrayField
- Item ID: defprop__markdownSectionOptions__arrayField
- 種別: definition_property
- 名前: arrayField
- 親: markdownSectionOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownSectionOptions.properties.format
- Item ID: defprop__markdownSectionOptions__format
- 種別: definition_property
- 名前: format
- 親: markdownSectionOptions
- 型概要: string enum[16]
- 必須: false
- Enum: auto, text, paragraph, textarea, blockquote, code, json, note, table, list, cards, chat, heading, constraintList, detailList, detail
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "auto",
    "text",
    "paragraph",
    "textarea",
    "blockquote",
    "code",
    "json",
    "note",
    "table",
    "list",
    "cards",
    "chat",
    "heading",
    "constraintList",
    "detailList",
    "detail"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | auto, text, paragraph, textarea, blockquote, code, json, note, table, list, cards, chat, heading, constraintList, detailList, detail |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownSectionOptions.properties.fields
- Item ID: defprop__markdownSectionOptions__fields
- 種別: definition_property
- 名前: fields
- 親: markdownSectionOptions
- 型概要: array<ref: markdownFieldOptions>
- 必須: false
- 参照: markdownFieldOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "items": {
    "$ref": "#/$defs/markdownFieldOptions"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |
| $ref(s) | markdownFieldOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownSectionOptions.properties.visible
- Item ID: defprop__markdownSectionOptions__visible
- 種別: definition_property
- 名前: visible
- 親: markdownSectionOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownSectionOptions.properties.aiPrompt
- Item ID: defprop__markdownSectionOptions__aiPrompt
- 種別: definition_property
- 名前: aiPrompt
- 親: markdownSectionOptions
- 型概要: ref: aiPromptOptions
- 必須: false
- 参照: aiPromptOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/aiPromptOptions"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | aiPromptOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownSectionOptions.properties.ai_prompt
- Item ID: defprop__markdownSectionOptions__ai_prompt
- 種別: definition_property
- 名前: ai_prompt
- 親: markdownSectionOptions
- 型概要: ref: aiPromptOptions
- 必須: false
- 参照: aiPromptOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/aiPromptOptions"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | aiPromptOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownSectionOptions.properties.itemTitle
- Item ID: defprop__markdownSectionOptions__itemTitle
- 種別: definition_property
- 名前: itemTitle
- 親: markdownSectionOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownSectionOptions.properties.showEmpty
- Item ID: defprop__markdownSectionOptions__showEmpty
- 種別: definition_property
- 名前: showEmpty
- 親: markdownSectionOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownSectionOptions.properties.sections
- Item ID: defprop__markdownSectionOptions__sections
- 種別: definition_property
- 名前: sections
- 親: markdownSectionOptions
- 型概要: array<ref: markdownSectionOptions>
- 必須: false
- 参照: markdownSectionOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "items": {
    "$ref": "#/$defs/markdownSectionOptions"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |
| $ref(s) | markdownSectionOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownFieldOptions
- Item ID: def__markdownFieldOptions
- 種別: definition
- 名前: markdownFieldOptions
- 親: $defs
- 型概要: object{8 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "field": {
      "type": "string"
    },
    "caption": {
      "type": "string"
    },
    "format": {
      "type": "string",
      "enum": [
        "auto",
        "text",
        "paragraph",
        "textarea",
        "blockquote",
        "code",
        "json",
        "note",
        "table",
        "list",
        "cards",
        "chat",
        "heading",
        "constraintList",
        "detailList",
        "detail"
      ]
    },
    "visible": {
      "type": "boolean"
    },
    "empty": {
      "type": [
        "string",
        "number",
        "boolean",
        "null"
      ]
    },
    "markdownFormat": {
      "type": "string",
      "enum": [
        "auto",
        "text",
        "paragraph",
        "textarea",
        "blockquote",
        "code",
        "json",
        "note",
        "table",
        "list",
        "cards",
        "chat",
        "heading",
        "constraintList",
        "detailList",
        "detail"
      ]
    },
    "showEmpty": {
      "type": "boolean"
    },
    "label": {
      "type": "string"
    }
  },
  "required": [
    "field"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |
| required | field |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| field | string | true |  |  |  |
| caption | string | false |  |  |  |
| format | string enum[16] | false |  | auto, text, paragraph, textarea, blockquote, code, json, note, table, list, cards, chat, heading, constraintList, detailList, detail |  |
| visible | boolean | false |  |  |  |
| empty | string \| number \| boolean \| null | false |  |  |  |
| markdownFormat | string enum[16] | false |  | auto, text, paragraph, textarea, blockquote, code, json, note, table, list, cards, chat, heading, constraintList, detailList, detail |  |
| showEmpty | boolean | false |  |  |  |
| label | string | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownFieldOptions.properties.field
- Item ID: defprop__markdownFieldOptions__field
- 種別: definition_property
- 名前: field
- 親: markdownFieldOptions
- 型概要: string
- 必須: true
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownFieldOptions.properties.caption
- Item ID: defprop__markdownFieldOptions__caption
- 種別: definition_property
- 名前: caption
- 親: markdownFieldOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownFieldOptions.properties.format
- Item ID: defprop__markdownFieldOptions__format
- 種別: definition_property
- 名前: format
- 親: markdownFieldOptions
- 型概要: string enum[16]
- 必須: false
- Enum: auto, text, paragraph, textarea, blockquote, code, json, note, table, list, cards, chat, heading, constraintList, detailList, detail
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "auto",
    "text",
    "paragraph",
    "textarea",
    "blockquote",
    "code",
    "json",
    "note",
    "table",
    "list",
    "cards",
    "chat",
    "heading",
    "constraintList",
    "detailList",
    "detail"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | auto, text, paragraph, textarea, blockquote, code, json, note, table, list, cards, chat, heading, constraintList, detailList, detail |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownFieldOptions.properties.visible
- Item ID: defprop__markdownFieldOptions__visible
- 種別: definition_property
- 名前: visible
- 親: markdownFieldOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownFieldOptions.properties.empty
- Item ID: defprop__markdownFieldOptions__empty
- 種別: definition_property
- 名前: empty
- 親: markdownFieldOptions
- 型概要: string \| number \| boolean \| null
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": [
    "string",
    "number",
    "boolean",
    "null"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | ["string", "number", "boolean", "null"] |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownFieldOptions.properties.markdownFormat
- Item ID: defprop__markdownFieldOptions__markdownFormat
- 種別: definition_property
- 名前: markdownFormat
- 親: markdownFieldOptions
- 型概要: string enum[16]
- 必須: false
- Enum: auto, text, paragraph, textarea, blockquote, code, json, note, table, list, cards, chat, heading, constraintList, detailList, detail
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "auto",
    "text",
    "paragraph",
    "textarea",
    "blockquote",
    "code",
    "json",
    "note",
    "table",
    "list",
    "cards",
    "chat",
    "heading",
    "constraintList",
    "detailList",
    "detail"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | auto, text, paragraph, textarea, blockquote, code, json, note, table, list, cards, chat, heading, constraintList, detailList, detail |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownFieldOptions.properties.showEmpty
- Item ID: defprop__markdownFieldOptions__showEmpty
- 種別: definition_property
- 名前: showEmpty
- 親: markdownFieldOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownFieldOptions.properties.label
- Item ID: defprop__markdownFieldOptions__label
- 種別: definition_property
- 名前: label
- 親: markdownFieldOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.viewDefReportOptions
- Item ID: def__viewDefReportOptions
- 種別: definition
- 名前: viewDefReportOptions
- 親: $defs
- 型概要: object{4 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

Future options for ViewDef Markdown→Viewer report. Separate from markdown.type.

##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "description": "Future options for ViewDef Markdown→Viewer report. Separate from markdown.type.",
  "properties": {
    "enabled": {
      "type": "boolean"
    },
    "includeInheritanceDiff": {
      "type": "boolean"
    },
    "includeResolvedJson": {
      "type": "boolean"
    },
    "includeRawJson": {
      "type": "boolean"
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| enabled | boolean | false |  |  |  |
| includeInheritanceDiff | boolean | false |  |  |  |
| includeResolvedJson | boolean | false |  |  |  |
| includeRawJson | boolean | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.viewDefReportOptions.properties.enabled
- Item ID: defprop__viewDefReportOptions__enabled
- 種別: definition_property
- 名前: enabled
- 親: viewDefReportOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.viewDefReportOptions.properties.includeInheritanceDiff
- Item ID: defprop__viewDefReportOptions__includeInheritanceDiff
- 種別: definition_property
- 名前: includeInheritanceDiff
- 親: viewDefReportOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.viewDefReportOptions.properties.includeResolvedJson
- Item ID: defprop__viewDefReportOptions__includeResolvedJson
- 種別: definition_property
- 名前: includeResolvedJson
- 親: viewDefReportOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.viewDefReportOptions.properties.includeRawJson
- Item ID: defprop__viewDefReportOptions__includeRawJson
- 種別: definition_property
- 名前: includeRawJson
- 親: viewDefReportOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.chatEmbeddedField
- Item ID: def__chatEmbeddedField
- 種別: definition
- 名前: chatEmbeddedField
- 親: $defs
- 型概要: object{8 properties}
- 必須: false
- 参照: fieldType, optionItem, editOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "field": {
      "type": "string"
    },
    "label": {
      "type": "string"
    },
    "caption": {
      "type": "string"
    },
    "type": {
      "$ref": "#/$defs/fieldType"
    },
    "control": {
      "type": "string",
      "enum": [
        "combobox",
        "listbox",
        "radio"
      ]
    },
    "options": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/optionItem"
      }
    },
    "readonly": {
      "type": "boolean"
    },
    "edit": {
      "$ref": "#/$defs/editOptions"
    }
  },
  "required": [
    "field"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |
| $ref(s) | fieldType, optionItem, editOptions |
| required | field |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| field | string | true |  |  |  |
| label | string | false |  |  |  |
| caption | string | false |  |  |  |
| type | ref: fieldType | false | fieldType |  |  |
| control | string enum[3] | false |  | combobox, listbox, radio |  |
| options | array<ref: optionItem> | false | optionItem |  |  |
| readonly | boolean | false |  |  |  |
| edit | ref: editOptions | false | editOptions |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.chatEmbeddedField.properties.field
- Item ID: defprop__chatEmbeddedField__field
- 種別: definition_property
- 名前: field
- 親: chatEmbeddedField
- 型概要: string
- 必須: true
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.chatEmbeddedField.properties.label
- Item ID: defprop__chatEmbeddedField__label
- 種別: definition_property
- 名前: label
- 親: chatEmbeddedField
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.chatEmbeddedField.properties.caption
- Item ID: defprop__chatEmbeddedField__caption
- 種別: definition_property
- 名前: caption
- 親: chatEmbeddedField
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.chatEmbeddedField.properties.type
- Item ID: defprop__chatEmbeddedField__type
- 種別: definition_property
- 名前: type
- 親: chatEmbeddedField
- 型概要: ref: fieldType
- 必須: false
- 参照: fieldType
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/fieldType"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | fieldType |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.chatEmbeddedField.properties.control
- Item ID: defprop__chatEmbeddedField__control
- 種別: definition_property
- 名前: control
- 親: chatEmbeddedField
- 型概要: string enum[3]
- 必須: false
- Enum: combobox, listbox, radio
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "combobox",
    "listbox",
    "radio"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | combobox, listbox, radio |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.chatEmbeddedField.properties.options
- Item ID: defprop__chatEmbeddedField__options
- 種別: definition_property
- 名前: options
- 親: chatEmbeddedField
- 型概要: array<ref: optionItem>
- 必須: false
- 参照: optionItem
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "items": {
    "$ref": "#/$defs/optionItem"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |
| $ref(s) | optionItem |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.chatEmbeddedField.properties.readonly
- Item ID: defprop__chatEmbeddedField__readonly
- 種別: definition_property
- 名前: readonly
- 親: chatEmbeddedField
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.chatEmbeddedField.properties.edit
- Item ID: defprop__chatEmbeddedField__edit
- 種別: definition_property
- 名前: edit
- 親: chatEmbeddedField
- 型概要: ref: editOptions
- 必須: false
- 参照: editOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/editOptions"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | editOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.dataSourceSpec
- Item ID: def__dataSourceSpec
- 種別: definition
- 名前: dataSourceSpec
- 親: $defs
- 型概要: object{6 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "name": {
      "type": "string"
    },
    "file": {
      "type": "string"
    },
    "path": {
      "type": "string"
    },
    "data": {
      "type": "string"
    },
    "source": {
      "type": "string"
    },
    "inline": true
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| name | string | false |  |  |  |
| file | string | false |  |  |  |
| path | string | false |  |  |  |
| data | string | false |  |  |  |
| source | string | false |  |  |  |
| inline | bool | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.dataSourceSpec.properties.name
- Item ID: defprop__dataSourceSpec__name
- 種別: definition_property
- 名前: name
- 親: dataSourceSpec
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.dataSourceSpec.properties.file
- Item ID: defprop__dataSourceSpec__file
- 種別: definition_property
- 名前: file
- 親: dataSourceSpec
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.dataSourceSpec.properties.path
- Item ID: defprop__dataSourceSpec__path
- 種別: definition_property
- 名前: path
- 親: dataSourceSpec
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.dataSourceSpec.properties.data
- Item ID: defprop__dataSourceSpec__data
- 種別: definition_property
- 名前: data
- 親: dataSourceSpec
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.dataSourceSpec.properties.source
- Item ID: defprop__dataSourceSpec__source
- 種別: definition_property
- 名前: source
- 親: dataSourceSpec
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.dataSourceSpec.properties.inline
- Item ID: defprop__dataSourceSpec__inline
- 種別: definition_property
- 名前: inline
- 親: dataSourceSpec
- 型概要: bool
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明

- Raw Schema JSON: true

#### 制約一覧

（なし）

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.dataSources
- Item ID: def__dataSources
- 種別: definition
- 名前: dataSources
- 親: $defs
- 型概要: object<additional:oneOf: string / ref: dataSourceSpec>
- 必須: false
- 参照: dataSourceSpec
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": {
    "oneOf": [
      {
        "type": "string",
        "minLength": 1
      },
      {
        "$ref": "#/$defs/dataSourceSpec"
      }
    ]
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | {"oneOf": [{"type": "string", "minLength": 1}, {"$ref": "#/$defs/dataSourceSpec"}]} |
| $ref(s) | dataSourceSpec |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualData
- Item ID: def__virtualData
- 種別: definition
- 名前: virtualData
- 親: $defs
- 型概要: oneOf: ref: virtualDataConfig / array<ref: virtualDataConfig>
- 必須: false
- 参照: virtualDataConfig, virtualDataConfig
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "oneOf": [
    {
      "$ref": "#/$defs/virtualDataConfig"
    },
    {
      "type": "array",
      "items": {
        "$ref": "#/$defs/virtualDataConfig"
      }
    }
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |
| $ref(s) | virtualDataConfig, virtualDataConfig |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig
- Item ID: def__virtualDataConfig
- 種別: definition
- 名前: virtualDataConfig
- 親: $defs
- 型概要: object{25 properties}
- 必須: false
- 参照: relationAxisSource, relationAxisSource, relationAxisSource, relationAxisSource, relationQuery, relationQuery, relationQuery, relationSource, relationSource, relationSource, diffSource, diffViewDefs, diffViewDefs, virtualOutputs, virtualDataWriteBack, virtualDataWriteBack
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "builder": {
      "type": "string",
      "description": "VirtualDataBuilderRegistry key. Registered examples: relation_axis_cards, relation_diff_cards, relation_diff_check_cards, constraint_trace_cards, test_pattern_trace_cards, expected_check_cross_counts, expected_check_shortage_findings."
    },
    "type": {
      "type": "string"
    },
    "kind": {
      "type": "string"
    },
    "targetPath": {
      "type": "string",
      "minLength": 1
    },
    "target_path": {
      "type": "string",
      "minLength": 1
    },
    "dataPath": {
      "type": "string",
      "minLength": 1
    },
    "data_path": {
      "type": "string",
      "minLength": 1
    },
    "axis": {
      "$ref": "#/$defs/relationAxisSource"
    },
    "base": {
      "$ref": "#/$defs/relationAxisSource"
    },
    "linked": {
      "$ref": "#/$defs/relationAxisSource"
    },
    "target": {
      "$ref": "#/$defs/relationAxisSource"
    },
    "relation": {
      "$ref": "#/$defs/relationQuery"
    },
    "relationQuery": {
      "$ref": "#/$defs/relationQuery"
    },
    "relation_query": {
      "$ref": "#/$defs/relationQuery"
    },
    "relations": {
      "$ref": "#/$defs/relationSource"
    },
    "relationSource": {
      "$ref": "#/$defs/relationSource"
    },
    "relation_source": {
      "$ref": "#/$defs/relationSource"
    },
    "diff": {
      "$ref": "#/$defs/diffSource"
    },
    "diffViewDefs": {
      "$ref": "#/$defs/diffViewDefs"
    },
    "diff_view_defs": {
      "$ref": "#/$defs/diffViewDefs"
    },
    "outputs": {
      "$ref": "#/$defs/virtualOutputs"
    },
    "summaryFields": {
      "type": "object",
      "additionalProperties": true
    },
    "summary_fields": {
      "type": "object",
      "additionalProperties": true
    },
    "writeBack": {
      "$ref": "#/$defs/virtualDataWriteBack"
    },
    "write_back": {
      "$ref": "#/$defs/virtualDataWriteBack"
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |
| $ref(s) | relationAxisSource, relationAxisSource, relationAxisSource, relationAxisSource, relationQuery, relationQuery, relationQuery, relationSource, relationSource, relationSource, diffSource, diffViewDefs, diffViewDefs, virtualOutputs, virtualDataWriteBack, virtualDataWriteBack |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| builder | string | false |  |  | VirtualDataBuilderRegistry key. Registered examples: relation_axis_cards, relation_diff_cards, relation_diff_check_cards, constraint_trace_cards, test_pattern_trace_cards, expected_check_cross_counts, expected_check_shortage_findings. |
| type | string | false |  |  |  |
| kind | string | false |  |  |  |
| targetPath | string | false |  |  |  |
| target_path | string | false |  |  |  |
| dataPath | string | false |  |  |  |
| data_path | string | false |  |  |  |
| axis | ref: relationAxisSource | false | relationAxisSource |  |  |
| base | ref: relationAxisSource | false | relationAxisSource |  |  |
| linked | ref: relationAxisSource | false | relationAxisSource |  |  |
| target | ref: relationAxisSource | false | relationAxisSource |  |  |
| relation | ref: relationQuery | false | relationQuery |  |  |
| relationQuery | ref: relationQuery | false | relationQuery |  |  |
| relation_query | ref: relationQuery | false | relationQuery |  |  |
| relations | ref: relationSource | false | relationSource |  |  |
| relationSource | ref: relationSource | false | relationSource |  |  |
| relation_source | ref: relationSource | false | relationSource |  |  |
| diff | ref: diffSource | false | diffSource |  |  |
| diffViewDefs | ref: diffViewDefs | false | diffViewDefs |  |  |
| diff_view_defs | ref: diffViewDefs | false | diffViewDefs |  |  |
| outputs | ref: virtualOutputs | false | virtualOutputs |  |  |
| summaryFields | object<additional:any> | false |  |  |  |
| summary_fields | object<additional:any> | false |  |  |  |
| writeBack | ref: virtualDataWriteBack | false | virtualDataWriteBack |  |  |
| write_back | ref: virtualDataWriteBack | false | virtualDataWriteBack |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.builder
- Item ID: defprop__virtualDataConfig__builder
- 種別: definition_property
- 名前: builder
- 親: virtualDataConfig
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

VirtualDataBuilderRegistry key. Registered examples: relation_axis_cards, relation_diff_cards, relation_diff_check_cards, constraint_trace_cards, test_pattern_trace_cards, expected_check_cross_counts, expected_check_shortage_findings.

##### Raw Schema JSON

{
  "type": "string",
  "description": "VirtualDataBuilderRegistry key. Registered examples: relation_axis_cards, relation_diff_cards, relation_diff_check_cards, constraint_trace_cards, test_pattern_trace_cards, expected_check_cross_counts, expected_check_shortage_findings."
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.type
- Item ID: defprop__virtualDataConfig__type
- 種別: definition_property
- 名前: type
- 親: virtualDataConfig
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.kind
- Item ID: defprop__virtualDataConfig__kind
- 種別: definition_property
- 名前: kind
- 親: virtualDataConfig
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.targetPath
- Item ID: defprop__virtualDataConfig__targetPath
- 種別: definition_property
- 名前: targetPath
- 親: virtualDataConfig
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "minLength": 1
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| minLength | 1 |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.target_path
- Item ID: defprop__virtualDataConfig__target_path
- 種別: definition_property
- 名前: target_path
- 親: virtualDataConfig
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "minLength": 1
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| minLength | 1 |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.dataPath
- Item ID: defprop__virtualDataConfig__dataPath
- 種別: definition_property
- 名前: dataPath
- 親: virtualDataConfig
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "minLength": 1
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| minLength | 1 |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.data_path
- Item ID: defprop__virtualDataConfig__data_path
- 種別: definition_property
- 名前: data_path
- 親: virtualDataConfig
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "minLength": 1
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| minLength | 1 |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.axis
- Item ID: defprop__virtualDataConfig__axis
- 種別: definition_property
- 名前: axis
- 親: virtualDataConfig
- 型概要: ref: relationAxisSource
- 必須: false
- 参照: relationAxisSource
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/relationAxisSource"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | relationAxisSource |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.base
- Item ID: defprop__virtualDataConfig__base
- 種別: definition_property
- 名前: base
- 親: virtualDataConfig
- 型概要: ref: relationAxisSource
- 必須: false
- 参照: relationAxisSource
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/relationAxisSource"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | relationAxisSource |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.linked
- Item ID: defprop__virtualDataConfig__linked
- 種別: definition_property
- 名前: linked
- 親: virtualDataConfig
- 型概要: ref: relationAxisSource
- 必須: false
- 参照: relationAxisSource
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/relationAxisSource"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | relationAxisSource |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.target
- Item ID: defprop__virtualDataConfig__target
- 種別: definition_property
- 名前: target
- 親: virtualDataConfig
- 型概要: ref: relationAxisSource
- 必須: false
- 参照: relationAxisSource
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/relationAxisSource"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | relationAxisSource |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.relation
- Item ID: defprop__virtualDataConfig__relation
- 種別: definition_property
- 名前: relation
- 親: virtualDataConfig
- 型概要: ref: relationQuery
- 必須: false
- 参照: relationQuery
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/relationQuery"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | relationQuery |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.relationQuery
- Item ID: defprop__virtualDataConfig__relationQuery
- 種別: definition_property
- 名前: relationQuery
- 親: virtualDataConfig
- 型概要: ref: relationQuery
- 必須: false
- 参照: relationQuery
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/relationQuery"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | relationQuery |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.relation_query
- Item ID: defprop__virtualDataConfig__relation_query
- 種別: definition_property
- 名前: relation_query
- 親: virtualDataConfig
- 型概要: ref: relationQuery
- 必須: false
- 参照: relationQuery
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/relationQuery"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | relationQuery |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.relations
- Item ID: defprop__virtualDataConfig__relations
- 種別: definition_property
- 名前: relations
- 親: virtualDataConfig
- 型概要: ref: relationSource
- 必須: false
- 参照: relationSource
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/relationSource"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | relationSource |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.relationSource
- Item ID: defprop__virtualDataConfig__relationSource
- 種別: definition_property
- 名前: relationSource
- 親: virtualDataConfig
- 型概要: ref: relationSource
- 必須: false
- 参照: relationSource
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/relationSource"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | relationSource |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.relation_source
- Item ID: defprop__virtualDataConfig__relation_source
- 種別: definition_property
- 名前: relation_source
- 親: virtualDataConfig
- 型概要: ref: relationSource
- 必須: false
- 参照: relationSource
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/relationSource"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | relationSource |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.diff
- Item ID: defprop__virtualDataConfig__diff
- 種別: definition_property
- 名前: diff
- 親: virtualDataConfig
- 型概要: ref: diffSource
- 必須: false
- 参照: diffSource
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/diffSource"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | diffSource |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.diffViewDefs
- Item ID: defprop__virtualDataConfig__diffViewDefs
- 種別: definition_property
- 名前: diffViewDefs
- 親: virtualDataConfig
- 型概要: ref: diffViewDefs
- 必須: false
- 参照: diffViewDefs
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/diffViewDefs"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | diffViewDefs |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.diff_view_defs
- Item ID: defprop__virtualDataConfig__diff_view_defs
- 種別: definition_property
- 名前: diff_view_defs
- 親: virtualDataConfig
- 型概要: ref: diffViewDefs
- 必須: false
- 参照: diffViewDefs
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/diffViewDefs"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | diffViewDefs |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.outputs
- Item ID: defprop__virtualDataConfig__outputs
- 種別: definition_property
- 名前: outputs
- 親: virtualDataConfig
- 型概要: ref: virtualOutputs
- 必須: false
- 参照: virtualOutputs
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/virtualOutputs"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | virtualOutputs |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.summaryFields
- Item ID: defprop__virtualDataConfig__summaryFields
- 種別: definition_property
- 名前: summaryFields
- 親: virtualDataConfig
- 型概要: object<additional:any>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.summary_fields
- Item ID: defprop__virtualDataConfig__summary_fields
- 種別: definition_property
- 名前: summary_fields
- 親: virtualDataConfig
- 型概要: object<additional:any>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.writeBack
- Item ID: defprop__virtualDataConfig__writeBack
- 種別: definition_property
- 名前: writeBack
- 親: virtualDataConfig
- 型概要: ref: virtualDataWriteBack
- 必須: false
- 参照: virtualDataWriteBack
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/virtualDataWriteBack"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | virtualDataWriteBack |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataConfig.properties.write_back
- Item ID: defprop__virtualDataConfig__write_back
- 種別: definition_property
- 名前: write_back
- 親: virtualDataConfig
- 型概要: ref: virtualDataWriteBack
- 必須: false
- 参照: virtualDataWriteBack
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/virtualDataWriteBack"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | virtualDataWriteBack |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationAxisSource
- Item ID: def__relationAxisSource
- 種別: definition
- 名前: relationAxisSource
- 親: $defs
- 型概要: object{16 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "source": {
      "type": "string"
    },
    "dataSource": {
      "type": "string"
    },
    "data_source": {
      "type": "string"
    },
    "adapter": {
      "type": "string"
    },
    "kind": {
      "type": "string"
    },
    "path": {
      "type": "string"
    },
    "dataPath": {
      "type": "string"
    },
    "data_path": {
      "type": "string"
    },
    "fallbackPaths": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "fallback_paths": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "nodeType": {
      "type": "string"
    },
    "node_type": {
      "type": "string"
    },
    "idField": {
      "type": "string"
    },
    "id_field": {
      "type": "string"
    },
    "titleField": {
      "type": "string"
    },
    "title_field": {
      "type": "string"
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| source | string | false |  |  |  |
| dataSource | string | false |  |  |  |
| data_source | string | false |  |  |  |
| adapter | string | false |  |  |  |
| kind | string | false |  |  |  |
| path | string | false |  |  |  |
| dataPath | string | false |  |  |  |
| data_path | string | false |  |  |  |
| fallbackPaths | array<string> | false |  |  |  |
| fallback_paths | array<string> | false |  |  |  |
| nodeType | string | false |  |  |  |
| node_type | string | false |  |  |  |
| idField | string | false |  |  |  |
| id_field | string | false |  |  |  |
| titleField | string | false |  |  |  |
| title_field | string | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationAxisSource.properties.source
- Item ID: defprop__relationAxisSource__source
- 種別: definition_property
- 名前: source
- 親: relationAxisSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationAxisSource.properties.dataSource
- Item ID: defprop__relationAxisSource__dataSource
- 種別: definition_property
- 名前: dataSource
- 親: relationAxisSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationAxisSource.properties.data_source
- Item ID: defprop__relationAxisSource__data_source
- 種別: definition_property
- 名前: data_source
- 親: relationAxisSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationAxisSource.properties.adapter
- Item ID: defprop__relationAxisSource__adapter
- 種別: definition_property
- 名前: adapter
- 親: relationAxisSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationAxisSource.properties.kind
- Item ID: defprop__relationAxisSource__kind
- 種別: definition_property
- 名前: kind
- 親: relationAxisSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationAxisSource.properties.path
- Item ID: defprop__relationAxisSource__path
- 種別: definition_property
- 名前: path
- 親: relationAxisSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationAxisSource.properties.dataPath
- Item ID: defprop__relationAxisSource__dataPath
- 種別: definition_property
- 名前: dataPath
- 親: relationAxisSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationAxisSource.properties.data_path
- Item ID: defprop__relationAxisSource__data_path
- 種別: definition_property
- 名前: data_path
- 親: relationAxisSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationAxisSource.properties.fallbackPaths
- Item ID: defprop__relationAxisSource__fallbackPaths
- 種別: definition_property
- 名前: fallbackPaths
- 親: relationAxisSource
- 型概要: array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "items": {
    "type": "string"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationAxisSource.properties.fallback_paths
- Item ID: defprop__relationAxisSource__fallback_paths
- 種別: definition_property
- 名前: fallback_paths
- 親: relationAxisSource
- 型概要: array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "items": {
    "type": "string"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationAxisSource.properties.nodeType
- Item ID: defprop__relationAxisSource__nodeType
- 種別: definition_property
- 名前: nodeType
- 親: relationAxisSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationAxisSource.properties.node_type
- Item ID: defprop__relationAxisSource__node_type
- 種別: definition_property
- 名前: node_type
- 親: relationAxisSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationAxisSource.properties.idField
- Item ID: defprop__relationAxisSource__idField
- 種別: definition_property
- 名前: idField
- 親: relationAxisSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationAxisSource.properties.id_field
- Item ID: defprop__relationAxisSource__id_field
- 種別: definition_property
- 名前: id_field
- 親: relationAxisSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationAxisSource.properties.titleField
- Item ID: defprop__relationAxisSource__titleField
- 種別: definition_property
- 名前: titleField
- 親: relationAxisSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationAxisSource.properties.title_field
- Item ID: defprop__relationAxisSource__title_field
- 種別: definition_property
- 名前: title_field
- 親: relationAxisSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationSource
- Item ID: def__relationSource
- 種別: definition
- 名前: relationSource
- 親: $defs
- 型概要: object{6 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "source": {
      "type": "string"
    },
    "dataSource": {
      "type": "string"
    },
    "data_source": {
      "type": "string"
    },
    "path": {
      "type": "string"
    },
    "relationsPath": {
      "type": "string"
    },
    "relations_path": {
      "type": "string"
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| source | string | false |  |  |  |
| dataSource | string | false |  |  |  |
| data_source | string | false |  |  |  |
| path | string | false |  |  |  |
| relationsPath | string | false |  |  |  |
| relations_path | string | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationSource.properties.source
- Item ID: defprop__relationSource__source
- 種別: definition_property
- 名前: source
- 親: relationSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationSource.properties.dataSource
- Item ID: defprop__relationSource__dataSource
- 種別: definition_property
- 名前: dataSource
- 親: relationSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationSource.properties.data_source
- Item ID: defprop__relationSource__data_source
- 種別: definition_property
- 名前: data_source
- 親: relationSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationSource.properties.path
- Item ID: defprop__relationSource__path
- 種別: definition_property
- 名前: path
- 親: relationSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationSource.properties.relationsPath
- Item ID: defprop__relationSource__relationsPath
- 種別: definition_property
- 名前: relationsPath
- 親: relationSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationSource.properties.relations_path
- Item ID: defprop__relationSource__relations_path
- 種別: definition_property
- 名前: relations_path
- 親: relationSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery
- Item ID: def__relationQuery
- 種別: definition
- 名前: relationQuery
- 親: $defs
- 型概要: object{31 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "source": {
      "type": "string"
    },
    "dataSource": {
      "type": "string"
    },
    "data_source": {
      "type": "string"
    },
    "path": {
      "type": "string"
    },
    "relationsPath": {
      "type": "string"
    },
    "relations_path": {
      "type": "string"
    },
    "name": {
      "type": "string"
    },
    "relation": {
      "type": "string"
    },
    "relationName": {
      "type": "string"
    },
    "relation_name": {
      "type": "string"
    },
    "direction": {
      "type": "string",
      "enum": [
        "outgoing",
        "incoming"
      ]
    },
    "includeViaCheck": {
      "type": "boolean"
    },
    "include_via_check": {
      "type": "boolean"
    },
    "verifiedByRelation": {
      "type": "string"
    },
    "verified_by_relation": {
      "type": "string"
    },
    "containsCheckRelation": {
      "type": "string"
    },
    "contains_check_relation": {
      "type": "string"
    },
    "testNodeType": {
      "type": "string"
    },
    "test_node_type": {
      "type": "string"
    },
    "checkType": {
      "type": "string"
    },
    "check_type": {
      "type": "string"
    },
    "constraintType": {
      "type": "string"
    },
    "constraint_type": {
      "type": "string"
    },
    "statusFilter": {
      "oneOf": [
        {
          "type": "string"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      ],
      "description": "Evidence relation statuses to include, e.g. [\"approved\"]."
    },
    "status_filter": {
      "oneOf": [
        {
          "type": "string"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      ],
      "description": "Evidence relation statuses to include, snake_case alias."
    },
    "structureStatusFilter": {
      "oneOf": [
        {
          "type": "string"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      ],
      "description": "Structure relation statuses to include for contains_check etc, e.g. [\"derived\",\"approved\"]."
    },
    "structure_status_filter": {
      "oneOf": [
        {
          "type": "string"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      ],
      "description": "Structure relation statuses to include, snake_case alias."
    },
    "excludeStatus": {
      "oneOf": [
        {
          "type": "string"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      ],
      "description": "Relation statuses to always exclude, e.g. [\"rejected\"]."
    },
    "exclude_status": {
      "oneOf": [
        {
          "type": "string"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      ],
      "description": "Relation statuses to always exclude, snake_case alias."
    },
    "includeStatus": {
      "oneOf": [
        {
          "type": "string"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      ],
      "description": "Alias for statusFilter."
    },
    "include_status": {
      "oneOf": [
        {
          "type": "string"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      ],
      "description": "Alias for statusFilter, snake_case."
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| source | string | false |  |  |  |
| dataSource | string | false |  |  |  |
| data_source | string | false |  |  |  |
| path | string | false |  |  |  |
| relationsPath | string | false |  |  |  |
| relations_path | string | false |  |  |  |
| name | string | false |  |  |  |
| relation | string | false |  |  |  |
| relationName | string | false |  |  |  |
| relation_name | string | false |  |  |  |
| direction | string enum[2] | false |  | outgoing, incoming |  |
| includeViaCheck | boolean | false |  |  |  |
| include_via_check | boolean | false |  |  |  |
| verifiedByRelation | string | false |  |  |  |
| verified_by_relation | string | false |  |  |  |
| containsCheckRelation | string | false |  |  |  |
| contains_check_relation | string | false |  |  |  |
| testNodeType | string | false |  |  |  |
| test_node_type | string | false |  |  |  |
| checkType | string | false |  |  |  |
| check_type | string | false |  |  |  |
| constraintType | string | false |  |  |  |
| constraint_type | string | false |  |  |  |
| statusFilter | oneOf: string / array<string> | false |  |  | Evidence relation statuses to include, e.g. ["approved"]. |
| status_filter | oneOf: string / array<string> | false |  |  | Evidence relation statuses to include, snake_case alias. |
| structureStatusFilter | oneOf: string / array<string> | false |  |  | Structure relation statuses to include for contains_check etc, e.g. ["derived","approved"]. |
| structure_status_filter | oneOf: string / array<string> | false |  |  | Structure relation statuses to include, snake_case alias. |
| excludeStatus | oneOf: string / array<string> | false |  |  | Relation statuses to always exclude, e.g. ["rejected"]. |
| exclude_status | oneOf: string / array<string> | false |  |  | Relation statuses to always exclude, snake_case alias. |
| includeStatus | oneOf: string / array<string> | false |  |  | Alias for statusFilter. |
| include_status | oneOf: string / array<string> | false |  |  | Alias for statusFilter, snake_case. |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.source
- Item ID: defprop__relationQuery__source
- 種別: definition_property
- 名前: source
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.dataSource
- Item ID: defprop__relationQuery__dataSource
- 種別: definition_property
- 名前: dataSource
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.data_source
- Item ID: defprop__relationQuery__data_source
- 種別: definition_property
- 名前: data_source
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.path
- Item ID: defprop__relationQuery__path
- 種別: definition_property
- 名前: path
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.relationsPath
- Item ID: defprop__relationQuery__relationsPath
- 種別: definition_property
- 名前: relationsPath
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.relations_path
- Item ID: defprop__relationQuery__relations_path
- 種別: definition_property
- 名前: relations_path
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.name
- Item ID: defprop__relationQuery__name
- 種別: definition_property
- 名前: name
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.relation
- Item ID: defprop__relationQuery__relation
- 種別: definition_property
- 名前: relation
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.relationName
- Item ID: defprop__relationQuery__relationName
- 種別: definition_property
- 名前: relationName
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.relation_name
- Item ID: defprop__relationQuery__relation_name
- 種別: definition_property
- 名前: relation_name
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.direction
- Item ID: defprop__relationQuery__direction
- 種別: definition_property
- 名前: direction
- 親: relationQuery
- 型概要: string enum[2]
- 必須: false
- Enum: outgoing, incoming
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "outgoing",
    "incoming"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | outgoing, incoming |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.includeViaCheck
- Item ID: defprop__relationQuery__includeViaCheck
- 種別: definition_property
- 名前: includeViaCheck
- 親: relationQuery
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.include_via_check
- Item ID: defprop__relationQuery__include_via_check
- 種別: definition_property
- 名前: include_via_check
- 親: relationQuery
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.verifiedByRelation
- Item ID: defprop__relationQuery__verifiedByRelation
- 種別: definition_property
- 名前: verifiedByRelation
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.verified_by_relation
- Item ID: defprop__relationQuery__verified_by_relation
- 種別: definition_property
- 名前: verified_by_relation
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.containsCheckRelation
- Item ID: defprop__relationQuery__containsCheckRelation
- 種別: definition_property
- 名前: containsCheckRelation
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.contains_check_relation
- Item ID: defprop__relationQuery__contains_check_relation
- 種別: definition_property
- 名前: contains_check_relation
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.testNodeType
- Item ID: defprop__relationQuery__testNodeType
- 種別: definition_property
- 名前: testNodeType
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.test_node_type
- Item ID: defprop__relationQuery__test_node_type
- 種別: definition_property
- 名前: test_node_type
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.checkType
- Item ID: defprop__relationQuery__checkType
- 種別: definition_property
- 名前: checkType
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.check_type
- Item ID: defprop__relationQuery__check_type
- 種別: definition_property
- 名前: check_type
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.constraintType
- Item ID: defprop__relationQuery__constraintType
- 種別: definition_property
- 名前: constraintType
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.constraint_type
- Item ID: defprop__relationQuery__constraint_type
- 種別: definition_property
- 名前: constraint_type
- 親: relationQuery
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.statusFilter
- Item ID: defprop__relationQuery__statusFilter
- 種別: definition_property
- 名前: statusFilter
- 親: relationQuery
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

Evidence relation statuses to include, e.g. ["approved"].

##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  ],
  "description": "Evidence relation statuses to include, e.g. [\"approved\"]."
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.status_filter
- Item ID: defprop__relationQuery__status_filter
- 種別: definition_property
- 名前: status_filter
- 親: relationQuery
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

Evidence relation statuses to include, snake_case alias.

##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  ],
  "description": "Evidence relation statuses to include, snake_case alias."
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.structureStatusFilter
- Item ID: defprop__relationQuery__structureStatusFilter
- 種別: definition_property
- 名前: structureStatusFilter
- 親: relationQuery
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

Structure relation statuses to include for contains_check etc, e.g. ["derived","approved"].

##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  ],
  "description": "Structure relation statuses to include for contains_check etc, e.g. [\"derived\",\"approved\"]."
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.structure_status_filter
- Item ID: defprop__relationQuery__structure_status_filter
- 種別: definition_property
- 名前: structure_status_filter
- 親: relationQuery
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

Structure relation statuses to include, snake_case alias.

##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  ],
  "description": "Structure relation statuses to include, snake_case alias."
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.excludeStatus
- Item ID: defprop__relationQuery__excludeStatus
- 種別: definition_property
- 名前: excludeStatus
- 親: relationQuery
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

Relation statuses to always exclude, e.g. ["rejected"].

##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  ],
  "description": "Relation statuses to always exclude, e.g. [\"rejected\"]."
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.exclude_status
- Item ID: defprop__relationQuery__exclude_status
- 種別: definition_property
- 名前: exclude_status
- 親: relationQuery
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

Relation statuses to always exclude, snake_case alias.

##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  ],
  "description": "Relation statuses to always exclude, snake_case alias."
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.includeStatus
- Item ID: defprop__relationQuery__includeStatus
- 種別: definition_property
- 名前: includeStatus
- 親: relationQuery
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

Alias for statusFilter.

##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  ],
  "description": "Alias for statusFilter."
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.relationQuery.properties.include_status
- Item ID: defprop__relationQuery__include_status
- 種別: definition_property
- 名前: include_status
- 親: relationQuery
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

Alias for statusFilter, snake_case.

##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  ],
  "description": "Alias for statusFilter, snake_case."
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffSource
- Item ID: def__diffSource
- 種別: definition
- 名前: diffSource
- 親: $defs
- 型概要: object{10 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "source": {
      "type": "string"
    },
    "dataSource": {
      "type": "string"
    },
    "data_source": {
      "type": "string"
    },
    "enabled": {
      "type": "boolean"
    },
    "testNodeType": {
      "type": "string"
    },
    "test_node_type": {
      "type": "string"
    },
    "testIdField": {
      "type": "string"
    },
    "test_id_field": {
      "type": "string"
    },
    "checksPath": {
      "type": "string"
    },
    "checks_path": {
      "type": "string"
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| source | string | false |  |  |  |
| dataSource | string | false |  |  |  |
| data_source | string | false |  |  |  |
| enabled | boolean | false |  |  |  |
| testNodeType | string | false |  |  |  |
| test_node_type | string | false |  |  |  |
| testIdField | string | false |  |  |  |
| test_id_field | string | false |  |  |  |
| checksPath | string | false |  |  |  |
| checks_path | string | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffSource.properties.source
- Item ID: defprop__diffSource__source
- 種別: definition_property
- 名前: source
- 親: diffSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffSource.properties.dataSource
- Item ID: defprop__diffSource__dataSource
- 種別: definition_property
- 名前: dataSource
- 親: diffSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffSource.properties.data_source
- Item ID: defprop__diffSource__data_source
- 種別: definition_property
- 名前: data_source
- 親: diffSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffSource.properties.enabled
- Item ID: defprop__diffSource__enabled
- 種別: definition_property
- 名前: enabled
- 親: diffSource
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffSource.properties.testNodeType
- Item ID: defprop__diffSource__testNodeType
- 種別: definition_property
- 名前: testNodeType
- 親: diffSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffSource.properties.test_node_type
- Item ID: defprop__diffSource__test_node_type
- 種別: definition_property
- 名前: test_node_type
- 親: diffSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffSource.properties.testIdField
- Item ID: defprop__diffSource__testIdField
- 種別: definition_property
- 名前: testIdField
- 親: diffSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffSource.properties.test_id_field
- Item ID: defprop__diffSource__test_id_field
- 種別: definition_property
- 名前: test_id_field
- 親: diffSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffSource.properties.checksPath
- Item ID: defprop__diffSource__checksPath
- 種別: definition_property
- 名前: checksPath
- 親: diffSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffSource.properties.checks_path
- Item ID: defprop__diffSource__checks_path
- 種別: definition_property
- 名前: checks_path
- 親: diffSource
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffViewDefRef
- Item ID: def__diffViewDefRef
- 種別: definition
- 名前: diffViewDefRef
- 親: $defs
- 型概要: object{9 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "role": {
      "type": "string",
      "enum": [
        "base",
        "child"
      ]
    },
    "view_def": {
      "type": "string"
    },
    "name": {
      "type": "string"
    },
    "file": {
      "type": "string"
    },
    "caption": {
      "type": "string"
    },
    "label": {
      "type": "string"
    },
    "extends": {
      "type": "string"
    },
    "note": {
      "type": "string"
    },
    "active": {
      "type": "boolean"
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| role | string enum[2] | false |  | base, child |  |
| view_def | string | false |  |  |  |
| name | string | false |  |  |  |
| file | string | false |  |  |  |
| caption | string | false |  |  |  |
| label | string | false |  |  |  |
| extends | string | false |  |  |  |
| note | string | false |  |  |  |
| active | boolean | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffViewDefRef.properties.role
- Item ID: defprop__diffViewDefRef__role
- 種別: definition_property
- 名前: role
- 親: diffViewDefRef
- 型概要: string enum[2]
- 必須: false
- Enum: base, child
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "base",
    "child"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | base, child |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffViewDefRef.properties.view_def
- Item ID: defprop__diffViewDefRef__view_def
- 種別: definition_property
- 名前: view_def
- 親: diffViewDefRef
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffViewDefRef.properties.name
- Item ID: defprop__diffViewDefRef__name
- 種別: definition_property
- 名前: name
- 親: diffViewDefRef
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffViewDefRef.properties.file
- Item ID: defprop__diffViewDefRef__file
- 種別: definition_property
- 名前: file
- 親: diffViewDefRef
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffViewDefRef.properties.caption
- Item ID: defprop__diffViewDefRef__caption
- 種別: definition_property
- 名前: caption
- 親: diffViewDefRef
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffViewDefRef.properties.label
- Item ID: defprop__diffViewDefRef__label
- 種別: definition_property
- 名前: label
- 親: diffViewDefRef
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffViewDefRef.properties.extends
- Item ID: defprop__diffViewDefRef__extends
- 種別: definition_property
- 名前: extends
- 親: diffViewDefRef
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffViewDefRef.properties.note
- Item ID: defprop__diffViewDefRef__note
- 種別: definition_property
- 名前: note
- 親: diffViewDefRef
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffViewDefRef.properties.active
- Item ID: defprop__diffViewDefRef__active
- 種別: definition_property
- 名前: active
- 親: diffViewDefRef
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffViewDefs
- Item ID: def__diffViewDefs
- 種別: definition
- 名前: diffViewDefs
- 親: $defs
- 型概要: object{3 properties}
- 必須: false
- 参照: diffViewDefRef, diffViewDefRef, diffViewDefRef
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "base": {
      "$ref": "#/$defs/diffViewDefRef"
    },
    "children": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/diffViewDefRef"
      }
    },
    "child": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/diffViewDefRef"
      }
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |
| $ref(s) | diffViewDefRef, diffViewDefRef, diffViewDefRef |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| base | ref: diffViewDefRef | false | diffViewDefRef |  |  |
| children | array<ref: diffViewDefRef> | false | diffViewDefRef |  |  |
| child | array<ref: diffViewDefRef> | false | diffViewDefRef |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffViewDefs.properties.base
- Item ID: defprop__diffViewDefs__base
- 種別: definition_property
- 名前: base
- 親: diffViewDefs
- 型概要: ref: diffViewDefRef
- 必須: false
- 参照: diffViewDefRef
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/diffViewDefRef"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | diffViewDefRef |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffViewDefs.properties.children
- Item ID: defprop__diffViewDefs__children
- 種別: definition_property
- 名前: children
- 親: diffViewDefs
- 型概要: array<ref: diffViewDefRef>
- 必須: false
- 参照: diffViewDefRef
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "items": {
    "$ref": "#/$defs/diffViewDefRef"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |
| $ref(s) | diffViewDefRef |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.diffViewDefs.properties.child
- Item ID: defprop__diffViewDefs__child
- 種別: definition_property
- 名前: child
- 親: diffViewDefs
- 型概要: array<ref: diffViewDefRef>
- 必須: false
- 参照: diffViewDefRef
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "items": {
    "$ref": "#/$defs/diffViewDefRef"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |
| $ref(s) | diffViewDefRef |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs
- Item ID: def__virtualOutputs
- 種別: definition
- 名前: virtualOutputs
- 親: $defs
- 型概要: object{26 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": {
    "type": "string"
  },
  "properties": {
    "idField": {
      "type": "string"
    },
    "id_field": {
      "type": "string"
    },
    "titleField": {
      "type": "string"
    },
    "title_field": {
      "type": "string"
    },
    "linkedItemsField": {
      "type": "string"
    },
    "linked_items_field": {
      "type": "string"
    },
    "relatedDiffsField": {
      "type": "string"
    },
    "related_diffs_field": {
      "type": "string"
    },
    "failedChecksField": {
      "type": "string"
    },
    "failed_checks_field": {
      "type": "string"
    },
    "evidenceEdgesField": {
      "type": "string"
    },
    "evidence_edges_field": {
      "type": "string"
    },
    "impactedItemsField": {
      "type": "string"
    },
    "impacted_items_field": {
      "type": "string"
    },
    "linkedCountField": {
      "type": "string"
    },
    "linked_count_field": {
      "type": "string"
    },
    "primaryCountField": {
      "type": "string"
    },
    "primary_count_field": {
      "type": "string"
    },
    "secondaryCountField": {
      "type": "string"
    },
    "secondary_count_field": {
      "type": "string"
    },
    "requiredCountField": {
      "type": "string"
    },
    "required_count_field": {
      "type": "string"
    },
    "failLinkedCountField": {
      "type": "string"
    },
    "fail_linked_count_field": {
      "type": "string"
    },
    "coverageField": {
      "type": "string"
    },
    "coverage_field": {
      "type": "string"
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | {"type": "string"} |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| idField | string | false |  |  |  |
| id_field | string | false |  |  |  |
| titleField | string | false |  |  |  |
| title_field | string | false |  |  |  |
| linkedItemsField | string | false |  |  |  |
| linked_items_field | string | false |  |  |  |
| relatedDiffsField | string | false |  |  |  |
| related_diffs_field | string | false |  |  |  |
| failedChecksField | string | false |  |  |  |
| failed_checks_field | string | false |  |  |  |
| evidenceEdgesField | string | false |  |  |  |
| evidence_edges_field | string | false |  |  |  |
| impactedItemsField | string | false |  |  |  |
| impacted_items_field | string | false |  |  |  |
| linkedCountField | string | false |  |  |  |
| linked_count_field | string | false |  |  |  |
| primaryCountField | string | false |  |  |  |
| primary_count_field | string | false |  |  |  |
| secondaryCountField | string | false |  |  |  |
| secondary_count_field | string | false |  |  |  |
| requiredCountField | string | false |  |  |  |
| required_count_field | string | false |  |  |  |
| failLinkedCountField | string | false |  |  |  |
| fail_linked_count_field | string | false |  |  |  |
| coverageField | string | false |  |  |  |
| coverage_field | string | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.idField
- Item ID: defprop__virtualOutputs__idField
- 種別: definition_property
- 名前: idField
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.id_field
- Item ID: defprop__virtualOutputs__id_field
- 種別: definition_property
- 名前: id_field
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.titleField
- Item ID: defprop__virtualOutputs__titleField
- 種別: definition_property
- 名前: titleField
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.title_field
- Item ID: defprop__virtualOutputs__title_field
- 種別: definition_property
- 名前: title_field
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.linkedItemsField
- Item ID: defprop__virtualOutputs__linkedItemsField
- 種別: definition_property
- 名前: linkedItemsField
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.linked_items_field
- Item ID: defprop__virtualOutputs__linked_items_field
- 種別: definition_property
- 名前: linked_items_field
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.relatedDiffsField
- Item ID: defprop__virtualOutputs__relatedDiffsField
- 種別: definition_property
- 名前: relatedDiffsField
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.related_diffs_field
- Item ID: defprop__virtualOutputs__related_diffs_field
- 種別: definition_property
- 名前: related_diffs_field
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.failedChecksField
- Item ID: defprop__virtualOutputs__failedChecksField
- 種別: definition_property
- 名前: failedChecksField
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.failed_checks_field
- Item ID: defprop__virtualOutputs__failed_checks_field
- 種別: definition_property
- 名前: failed_checks_field
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.evidenceEdgesField
- Item ID: defprop__virtualOutputs__evidenceEdgesField
- 種別: definition_property
- 名前: evidenceEdgesField
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.evidence_edges_field
- Item ID: defprop__virtualOutputs__evidence_edges_field
- 種別: definition_property
- 名前: evidence_edges_field
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.impactedItemsField
- Item ID: defprop__virtualOutputs__impactedItemsField
- 種別: definition_property
- 名前: impactedItemsField
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.impacted_items_field
- Item ID: defprop__virtualOutputs__impacted_items_field
- 種別: definition_property
- 名前: impacted_items_field
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.linkedCountField
- Item ID: defprop__virtualOutputs__linkedCountField
- 種別: definition_property
- 名前: linkedCountField
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.linked_count_field
- Item ID: defprop__virtualOutputs__linked_count_field
- 種別: definition_property
- 名前: linked_count_field
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.primaryCountField
- Item ID: defprop__virtualOutputs__primaryCountField
- 種別: definition_property
- 名前: primaryCountField
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.primary_count_field
- Item ID: defprop__virtualOutputs__primary_count_field
- 種別: definition_property
- 名前: primary_count_field
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.secondaryCountField
- Item ID: defprop__virtualOutputs__secondaryCountField
- 種別: definition_property
- 名前: secondaryCountField
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.secondary_count_field
- Item ID: defprop__virtualOutputs__secondary_count_field
- 種別: definition_property
- 名前: secondary_count_field
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.requiredCountField
- Item ID: defprop__virtualOutputs__requiredCountField
- 種別: definition_property
- 名前: requiredCountField
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.required_count_field
- Item ID: defprop__virtualOutputs__required_count_field
- 種別: definition_property
- 名前: required_count_field
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.failLinkedCountField
- Item ID: defprop__virtualOutputs__failLinkedCountField
- 種別: definition_property
- 名前: failLinkedCountField
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.fail_linked_count_field
- Item ID: defprop__virtualOutputs__fail_linked_count_field
- 種別: definition_property
- 名前: fail_linked_count_field
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.coverageField
- Item ID: defprop__virtualOutputs__coverageField
- 種別: definition_property
- 名前: coverageField
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualOutputs.properties.coverage_field
- Item ID: defprop__virtualOutputs__coverage_field
- 種別: definition_property
- 名前: coverage_field
- 親: virtualOutputs
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.writePolicy
- Item ID: def__writePolicy
- 種別: definition
- 名前: writePolicy
- 親: $defs
- 型概要: object{13 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "mode": {
      "type": "string",
      "enum": [
        "singleSource",
        "readonly",
        "multiSourceDraft"
      ]
    },
    "primarySource": {
      "type": "string"
    },
    "primary_source": {
      "type": "string"
    },
    "virtualDataReadonly": {
      "type": "boolean"
    },
    "virtual_data_readonly": {
      "type": "boolean"
    },
    "editableSources": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "editable_sources": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "readonlySources": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "readonly_sources": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "primaryPath": {
      "type": "string"
    },
    "primary_path": {
      "type": "string"
    },
    "editableFields": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "editable_fields": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| mode | string enum[3] | false |  | singleSource, readonly, multiSourceDraft |  |
| primarySource | string | false |  |  |  |
| primary_source | string | false |  |  |  |
| virtualDataReadonly | boolean | false |  |  |  |
| virtual_data_readonly | boolean | false |  |  |  |
| editableSources | array<string> | false |  |  |  |
| editable_sources | array<string> | false |  |  |  |
| readonlySources | array<string> | false |  |  |  |
| readonly_sources | array<string> | false |  |  |  |
| primaryPath | string | false |  |  |  |
| primary_path | string | false |  |  |  |
| editableFields | array<string> | false |  |  |  |
| editable_fields | array<string> | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.writePolicy.properties.mode
- Item ID: defprop__writePolicy__mode
- 種別: definition_property
- 名前: mode
- 親: writePolicy
- 型概要: string enum[3]
- 必須: false
- Enum: singleSource, readonly, multiSourceDraft
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "singleSource",
    "readonly",
    "multiSourceDraft"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | singleSource, readonly, multiSourceDraft |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.writePolicy.properties.primarySource
- Item ID: defprop__writePolicy__primarySource
- 種別: definition_property
- 名前: primarySource
- 親: writePolicy
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.writePolicy.properties.primary_source
- Item ID: defprop__writePolicy__primary_source
- 種別: definition_property
- 名前: primary_source
- 親: writePolicy
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.writePolicy.properties.virtualDataReadonly
- Item ID: defprop__writePolicy__virtualDataReadonly
- 種別: definition_property
- 名前: virtualDataReadonly
- 親: writePolicy
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.writePolicy.properties.virtual_data_readonly
- Item ID: defprop__writePolicy__virtual_data_readonly
- 種別: definition_property
- 名前: virtual_data_readonly
- 親: writePolicy
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.writePolicy.properties.editableSources
- Item ID: defprop__writePolicy__editableSources
- 種別: definition_property
- 名前: editableSources
- 親: writePolicy
- 型概要: array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "items": {
    "type": "string"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.writePolicy.properties.editable_sources
- Item ID: defprop__writePolicy__editable_sources
- 種別: definition_property
- 名前: editable_sources
- 親: writePolicy
- 型概要: array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "items": {
    "type": "string"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.writePolicy.properties.readonlySources
- Item ID: defprop__writePolicy__readonlySources
- 種別: definition_property
- 名前: readonlySources
- 親: writePolicy
- 型概要: array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "items": {
    "type": "string"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.writePolicy.properties.readonly_sources
- Item ID: defprop__writePolicy__readonly_sources
- 種別: definition_property
- 名前: readonly_sources
- 親: writePolicy
- 型概要: array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "items": {
    "type": "string"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.writePolicy.properties.primaryPath
- Item ID: defprop__writePolicy__primaryPath
- 種別: definition_property
- 名前: primaryPath
- 親: writePolicy
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.writePolicy.properties.primary_path
- Item ID: defprop__writePolicy__primary_path
- 種別: definition_property
- 名前: primary_path
- 親: writePolicy
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.writePolicy.properties.editableFields
- Item ID: defprop__writePolicy__editableFields
- 種別: definition_property
- 名前: editableFields
- 親: writePolicy
- 型概要: array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "items": {
    "type": "string"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.writePolicy.properties.editable_fields
- Item ID: defprop__writePolicy__editable_fields
- 種別: definition_property
- 名前: editable_fields
- 親: writePolicy
- 型概要: array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "items": {
    "type": "string"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.writeBackFieldMap
- Item ID: def__writeBackFieldMap
- 種別: definition
- 名前: writeBackFieldMap
- 親: $defs
- 型概要: oneOf: string / object{7 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "object",
      "additionalProperties": true,
      "properties": {
        "from": {
          "type": "string"
        },
        "to": {
          "type": "string"
        },
        "field": {
          "type": "string"
        },
        "virtualField": {
          "type": "string"
        },
        "virtual_field": {
          "type": "string"
        },
        "sourceField": {
          "type": "string"
        },
        "source_field": {
          "type": "string"
        }
      }
    }
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataWriteBack
- Item ID: def__virtualDataWriteBack
- 種別: definition
- 名前: virtualDataWriteBack
- 親: $defs
- 型概要: object{14 properties}
- 必須: false
- 参照: writeBackFieldMap
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

virtualDataで生成された仮想行から、主たる更新対象JSON 1つへ一部フィールドを書き戻すための定義。

##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "description": "virtualDataで生成された仮想行から、主たる更新対象JSON 1つへ一部フィールドを書き戻すための定義。",
  "properties": {
    "enabled": {
      "type": "boolean"
    },
    "source": {
      "type": "string"
    },
    "dataSource": {
      "type": "string"
    },
    "data_source": {
      "type": "string"
    },
    "path": {
      "type": "string"
    },
    "dataPath": {
      "type": "string"
    },
    "data_path": {
      "type": "string"
    },
    "keyField": {
      "type": "string"
    },
    "key_field": {
      "type": "string"
    },
    "rowKeyField": {
      "type": "string"
    },
    "row_key_field": {
      "type": "string"
    },
    "fields": {
      "description": "書き戻し対象フィールド。同名配列、from/to配列、または {仮想field: 元field} のmap。",
      "oneOf": [
        {
          "type": "array",
          "items": {
            "$ref": "#/$defs/writeBackFieldMap"
          }
        },
        {
          "type": "object",
          "additionalProperties": {
            "type": "string"
          }
        }
      ]
    },
    "fieldMap": {
      "type": "object",
      "additionalProperties": {
        "type": "string"
      }
    },
    "field_map": {
      "type": "object",
      "additionalProperties": {
        "type": "string"
      }
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |
| $ref(s) | writeBackFieldMap |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| enabled | boolean | false |  |  |  |
| source | string | false |  |  |  |
| dataSource | string | false |  |  |  |
| data_source | string | false |  |  |  |
| path | string | false |  |  |  |
| dataPath | string | false |  |  |  |
| data_path | string | false |  |  |  |
| keyField | string | false |  |  |  |
| key_field | string | false |  |  |  |
| rowKeyField | string | false |  |  |  |
| row_key_field | string | false |  |  |  |
| fields | oneOf: array<ref: writeBackFieldMap> / object<additional:string> | false | writeBackFieldMap |  | 書き戻し対象フィールド。同名配列、from/to配列、または {仮想field: 元field} のmap。 |
| fieldMap | object<additional:string> | false |  |  |  |
| field_map | object<additional:string> | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataWriteBack.properties.enabled
- Item ID: defprop__virtualDataWriteBack__enabled
- 種別: definition_property
- 名前: enabled
- 親: virtualDataWriteBack
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataWriteBack.properties.source
- Item ID: defprop__virtualDataWriteBack__source
- 種別: definition_property
- 名前: source
- 親: virtualDataWriteBack
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataWriteBack.properties.dataSource
- Item ID: defprop__virtualDataWriteBack__dataSource
- 種別: definition_property
- 名前: dataSource
- 親: virtualDataWriteBack
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataWriteBack.properties.data_source
- Item ID: defprop__virtualDataWriteBack__data_source
- 種別: definition_property
- 名前: data_source
- 親: virtualDataWriteBack
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataWriteBack.properties.path
- Item ID: defprop__virtualDataWriteBack__path
- 種別: definition_property
- 名前: path
- 親: virtualDataWriteBack
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataWriteBack.properties.dataPath
- Item ID: defprop__virtualDataWriteBack__dataPath
- 種別: definition_property
- 名前: dataPath
- 親: virtualDataWriteBack
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataWriteBack.properties.data_path
- Item ID: defprop__virtualDataWriteBack__data_path
- 種別: definition_property
- 名前: data_path
- 親: virtualDataWriteBack
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataWriteBack.properties.keyField
- Item ID: defprop__virtualDataWriteBack__keyField
- 種別: definition_property
- 名前: keyField
- 親: virtualDataWriteBack
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataWriteBack.properties.key_field
- Item ID: defprop__virtualDataWriteBack__key_field
- 種別: definition_property
- 名前: key_field
- 親: virtualDataWriteBack
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataWriteBack.properties.rowKeyField
- Item ID: defprop__virtualDataWriteBack__rowKeyField
- 種別: definition_property
- 名前: rowKeyField
- 親: virtualDataWriteBack
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataWriteBack.properties.row_key_field
- Item ID: defprop__virtualDataWriteBack__row_key_field
- 種別: definition_property
- 名前: row_key_field
- 親: virtualDataWriteBack
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataWriteBack.properties.fields
- Item ID: defprop__virtualDataWriteBack__fields
- 種別: definition_property
- 名前: fields
- 親: virtualDataWriteBack
- 型概要: oneOf: array<ref: writeBackFieldMap> / object<additional:string>
- 必須: false
- 参照: writeBackFieldMap
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

書き戻し対象フィールド。同名配列、from/to配列、または {仮想field: 元field} のmap。

##### Raw Schema JSON

{
  "description": "書き戻し対象フィールド。同名配列、from/to配列、または {仮想field: 元field} のmap。",
  "oneOf": [
    {
      "type": "array",
      "items": {
        "$ref": "#/$defs/writeBackFieldMap"
      }
    },
    {
      "type": "object",
      "additionalProperties": {
        "type": "string"
      }
    }
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |
| $ref(s) | writeBackFieldMap |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataWriteBack.properties.fieldMap
- Item ID: defprop__virtualDataWriteBack__fieldMap
- 種別: definition_property
- 名前: fieldMap
- 親: virtualDataWriteBack
- 型概要: object<additional:string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": {
    "type": "string"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | {"type": "string"} |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.virtualDataWriteBack.properties.field_map
- Item ID: defprop__virtualDataWriteBack__field_map
- 種別: definition_property
- 名前: field_map
- 親: virtualDataWriteBack
- 型概要: object<additional:string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": {
    "type": "string"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | {"type": "string"} |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.optionItem
- Item ID: def__optionItem
- 種別: definition
- 名前: optionItem
- 親: $defs
- 型概要: oneOf: string / number / boolean / object{8 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "number"
    },
    {
      "type": "boolean"
    },
    {
      "type": "object",
      "additionalProperties": true,
      "description": "Select/radio option object. Default value field is cd; default label field is name. value/id/key and label/caption/text are also supported by runtime.",
      "properties": {
        "cd": {
          "type": [
            "string",
            "number",
            "boolean"
          ]
        },
        "value": {
          "type": [
            "string",
            "number",
            "boolean"
          ]
        },
        "id": {
          "type": [
            "string",
            "number",
            "boolean"
          ]
        },
        "key": {
          "type": [
            "string",
            "number",
            "boolean"
          ]
        },
        "name": {
          "type": "string"
        },
        "label": {
          "type": "string"
        },
        "caption": {
          "type": "string"
        },
        "text": {
          "type": "string"
        }
      }
    }
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 4 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.layoutOptions
- Item ID: def__layoutOptions
- 種別: definition
- 名前: layoutOptions
- 親: $defs
- 型概要: object{2 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

View/layout options. Runtime currently uses detailDialog: wide for wide detail dialog. String layout header-search-grid-detail is still valid.

##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "description": "View/layout options. Runtime currently uses detailDialog: wide for wide detail dialog. String layout header-search-grid-detail is still valid.",
  "properties": {
    "detailDialog": {
      "type": "string",
      "enum": [
        "normal",
        "wide"
      ]
    },
    "detail_dialog": {
      "type": "string",
      "enum": [
        "normal",
        "wide"
      ]
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| detailDialog | string enum[2] | false |  | normal, wide |  |
| detail_dialog | string enum[2] | false |  | normal, wide |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.layoutOptions.properties.detailDialog
- Item ID: defprop__layoutOptions__detailDialog
- 種別: definition_property
- 名前: detailDialog
- 親: layoutOptions
- 型概要: string enum[2]
- 必須: false
- Enum: normal, wide
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "normal",
    "wide"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | normal, wide |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.layoutOptions.properties.detail_dialog
- Item ID: defprop__layoutOptions__detail_dialog
- 種別: definition_property
- 名前: detail_dialog
- 親: layoutOptions
- 型概要: string enum[2]
- 必須: false
- Enum: normal, wide
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "normal",
    "wide"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | normal, wide |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.executeButtonOptions
- Item ID: def__executeButtonOptions
- 種別: definition
- 名前: executeButtonOptions
- 親: $defs
- 型概要: anyOf: unspecified / unspecified / unspecified
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

View-specific primary execute action. Runtime reads action/actionId/action_id as actionId and passes it to ActionRegistry. Do not hard-code Action names in Runtime.

##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "description": "View-specific primary execute action. Runtime reads action/actionId/action_id as actionId and passes it to ActionRegistry. Do not hard-code Action names in Runtime.",
  "properties": {
    "visible": {
      "type": "boolean"
    },
    "caption": {
      "type": "string"
    },
    "label": {
      "type": "string"
    },
    "action": {
      "type": "string"
    },
    "actionId": {
      "type": "string"
    },
    "action_id": {
      "type": "string"
    }
  },
  "anyOf": [
    {
      "required": [
        "action"
      ]
    },
    {
      "required": [
        "actionId"
      ]
    },
    {
      "required": [
        "action_id"
      ]
    }
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |
| anyOf | 3 branches |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| visible | boolean | false |  |  |  |
| caption | string | false |  |  |  |
| label | string | false |  |  |  |
| action | string | false |  |  |  |
| actionId | string | false |  |  |  |
| action_id | string | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.executeButtonOptions.properties.visible
- Item ID: defprop__executeButtonOptions__visible
- 種別: definition_property
- 名前: visible
- 親: executeButtonOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.executeButtonOptions.properties.caption
- Item ID: defprop__executeButtonOptions__caption
- 種別: definition_property
- 名前: caption
- 親: executeButtonOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.executeButtonOptions.properties.label
- Item ID: defprop__executeButtonOptions__label
- 種別: definition_property
- 名前: label
- 親: executeButtonOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.executeButtonOptions.properties.action
- Item ID: defprop__executeButtonOptions__action
- 種別: definition_property
- 名前: action
- 親: executeButtonOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.executeButtonOptions.properties.actionId
- Item ID: defprop__executeButtonOptions__actionId
- 種別: definition_property
- 名前: actionId
- 親: executeButtonOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.executeButtonOptions.properties.action_id
- Item ID: defprop__executeButtonOptions__action_id
- 種別: definition_property
- 名前: action_id
- 親: executeButtonOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.toolbarButtonOptions
- Item ID: def__toolbarButtonOptions
- 種別: definition
- 名前: toolbarButtonOptions
- 親: $defs
- 型概要: object{6 properties}
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

Reserved for future secondary toolbar buttons. v0.6 runtime only renders executeButton.

##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "description": "Reserved for future secondary toolbar buttons. v0.6 runtime only renders executeButton.",
  "properties": {
    "visible": {
      "type": "boolean"
    },
    "caption": {
      "type": "string"
    },
    "label": {
      "type": "string"
    },
    "action": {
      "type": "string"
    },
    "actionId": {
      "type": "string"
    },
    "action_id": {
      "type": "string"
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| visible | boolean | false |  |  |  |
| caption | string | false |  |  |  |
| label | string | false |  |  |  |
| action | string | false |  |  |  |
| actionId | string | false |  |  |  |
| action_id | string | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.toolbarButtonOptions.properties.visible
- Item ID: defprop__toolbarButtonOptions__visible
- 種別: definition_property
- 名前: visible
- 親: toolbarButtonOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.toolbarButtonOptions.properties.caption
- Item ID: defprop__toolbarButtonOptions__caption
- 種別: definition_property
- 名前: caption
- 親: toolbarButtonOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.toolbarButtonOptions.properties.label
- Item ID: defprop__toolbarButtonOptions__label
- 種別: definition_property
- 名前: label
- 親: toolbarButtonOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.toolbarButtonOptions.properties.action
- Item ID: defprop__toolbarButtonOptions__action
- 種別: definition_property
- 名前: action
- 親: toolbarButtonOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.toolbarButtonOptions.properties.actionId
- Item ID: defprop__toolbarButtonOptions__actionId
- 種別: definition_property
- 名前: actionId
- 親: toolbarButtonOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.toolbarButtonOptions.properties.action_id
- Item ID: defprop__toolbarButtonOptions__action_id
- 種別: definition_property
- 名前: action_id
- 親: toolbarButtonOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.toolbarOptions
- Item ID: def__toolbarOptions
- 種別: definition
- 名前: toolbarOptions
- 親: $defs
- 型概要: object{3 properties}
- 必須: false
- 参照: executeButtonOptions, executeButtonOptions, toolbarButtonOptions
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

Toolbar declarations. Current runtime supports toolbar.executeButton / toolbar.execute_button as the primary View action.

##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "description": "Toolbar declarations. Current runtime supports toolbar.executeButton / toolbar.execute_button as the primary View action.",
  "properties": {
    "executeButton": {
      "$ref": "#/$defs/executeButtonOptions"
    },
    "execute_button": {
      "$ref": "#/$defs/executeButtonOptions"
    },
    "buttons": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/toolbarButtonOptions"
      }
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |
| $ref(s) | executeButtonOptions, executeButtonOptions, toolbarButtonOptions |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| executeButton | ref: executeButtonOptions | false | executeButtonOptions |  |  |
| execute_button | ref: executeButtonOptions | false | executeButtonOptions |  |  |
| buttons | array<ref: toolbarButtonOptions> | false | toolbarButtonOptions |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.toolbarOptions.properties.executeButton
- Item ID: defprop__toolbarOptions__executeButton
- 種別: definition_property
- 名前: executeButton
- 親: toolbarOptions
- 型概要: ref: executeButtonOptions
- 必須: false
- 参照: executeButtonOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/executeButtonOptions"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | executeButtonOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.toolbarOptions.properties.execute_button
- Item ID: defprop__toolbarOptions__execute_button
- 種別: definition_property
- 名前: execute_button
- 親: toolbarOptions
- 型概要: ref: executeButtonOptions
- 必須: false
- 参照: executeButtonOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "$ref": "#/$defs/executeButtonOptions"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| $ref(s) | executeButtonOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.toolbarOptions.properties.buttons
- Item ID: defprop__toolbarOptions__buttons
- 種別: definition_property
- 名前: buttons
- 親: toolbarOptions
- 型概要: array<ref: toolbarButtonOptions>
- 必須: false
- 参照: toolbarButtonOptions
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "array",
  "items": {
    "$ref": "#/$defs/toolbarButtonOptions"
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | array |
| $ref(s) | toolbarButtonOptions |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.aiPromptOptions
- Item ID: def__aiPromptOptions
- 種別: definition
- 名前: aiPromptOptions
- 親: $defs
- 型概要: object{11 properties}
- 必須: false
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

Markdown export AI copy block. Attach to grid section markdown.aiPrompt.

##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "description": "Markdown export AI copy block. Attach to grid section markdown.aiPrompt.",
  "properties": {
    "enabled": {
      "type": "boolean"
    },
    "title": {
      "type": "string"
    },
    "targetFile": {
      "type": "string"
    },
    "target_file": {
      "type": "string"
    },
    "rowSource": {
      "type": "string",
      "enum": [
        "filtered",
        "all",
        "current",
        "selected"
      ]
    },
    "row_source": {
      "type": "string",
      "enum": [
        "filtered",
        "all",
        "current",
        "selected"
      ]
    },
    "visibleOnly": {
      "type": "boolean"
    },
    "visible_only": {
      "type": "boolean"
    },
    "includeGridJson": {
      "type": "boolean"
    },
    "include_grid_json": {
      "type": "boolean"
    },
    "template": {
      "oneOf": [
        {
          "type": "string"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      ]
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| enabled | boolean | false |  |  |  |
| title | string | false |  |  |  |
| targetFile | string | false |  |  |  |
| target_file | string | false |  |  |  |
| rowSource | string enum[4] | false |  | filtered, all, current, selected |  |
| row_source | string enum[4] | false |  | filtered, all, current, selected |  |
| visibleOnly | boolean | false |  |  |  |
| visible_only | boolean | false |  |  |  |
| includeGridJson | boolean | false |  |  |  |
| include_grid_json | boolean | false |  |  |  |
| template | oneOf: string / array<string> | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.aiPromptOptions.properties.enabled
- Item ID: defprop__aiPromptOptions__enabled
- 種別: definition_property
- 名前: enabled
- 親: aiPromptOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.aiPromptOptions.properties.title
- Item ID: defprop__aiPromptOptions__title
- 種別: definition_property
- 名前: title
- 親: aiPromptOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.aiPromptOptions.properties.targetFile
- Item ID: defprop__aiPromptOptions__targetFile
- 種別: definition_property
- 名前: targetFile
- 親: aiPromptOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.aiPromptOptions.properties.target_file
- Item ID: defprop__aiPromptOptions__target_file
- 種別: definition_property
- 名前: target_file
- 親: aiPromptOptions
- 型概要: string
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.aiPromptOptions.properties.rowSource
- Item ID: defprop__aiPromptOptions__rowSource
- 種別: definition_property
- 名前: rowSource
- 親: aiPromptOptions
- 型概要: string enum[4]
- 必須: false
- Enum: filtered, all, current, selected
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "filtered",
    "all",
    "current",
    "selected"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | filtered, all, current, selected |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.aiPromptOptions.properties.row_source
- Item ID: defprop__aiPromptOptions__row_source
- 種別: definition_property
- 名前: row_source
- 親: aiPromptOptions
- 型概要: string enum[4]
- 必須: false
- Enum: filtered, all, current, selected
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "string",
  "enum": [
    "filtered",
    "all",
    "current",
    "selected"
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | string |
| enum | filtered, all, current, selected |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.aiPromptOptions.properties.visibleOnly
- Item ID: defprop__aiPromptOptions__visibleOnly
- 種別: definition_property
- 名前: visibleOnly
- 親: aiPromptOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.aiPromptOptions.properties.visible_only
- Item ID: defprop__aiPromptOptions__visible_only
- 種別: definition_property
- 名前: visible_only
- 親: aiPromptOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.aiPromptOptions.properties.includeGridJson
- Item ID: defprop__aiPromptOptions__includeGridJson
- 種別: definition_property
- 名前: includeGridJson
- 親: aiPromptOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.aiPromptOptions.properties.include_grid_json
- Item ID: defprop__aiPromptOptions__include_grid_json
- 種別: definition_property
- 名前: include_grid_json
- 親: aiPromptOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.aiPromptOptions.properties.template
- Item ID: defprop__aiPromptOptions__template
- 種別: definition_property
- 名前: template
- 親: aiPromptOptions
- 型概要: oneOf: string / array<string>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "string"
    },
    {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownInlineOptions
- Item ID: def__markdownInlineOptions
- 種別: definition
- 名前: markdownInlineOptions
- 親: $defs
- 型概要: object{6 properties}
- 必須: false
- 優先度: high
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### 説明

chat/textarea内のMarkdownリンク・画像記法の表示許可。保存値はMarkdown原文のまま保持する。

##### Raw Schema JSON

{
  "type": "object",
  "additionalProperties": true,
  "description": "chat/textarea内のMarkdownリンク・画像記法の表示許可。保存値はMarkdown原文のまま保持する。",
  "properties": {
    "enabled": {
      "type": "boolean"
    },
    "inline": {
      "oneOf": [
        {
          "type": "boolean"
        },
        {
          "type": "object",
          "additionalProperties": true
        }
      ]
    },
    "allowLinks": {
      "type": "boolean"
    },
    "allow_links": {
      "type": "boolean"
    },
    "allowImages": {
      "type": "boolean"
    },
    "allow_images": {
      "type": "boolean"
    }
  }
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | object |
| additionalProperties | True |

#### 子Properties

| Property | 型概要 | 必須 | 参照 | Enum | 説明 |
| --- | --- | --- | --- | --- | --- |
| enabled | boolean | false |  |  |  |
| inline | oneOf: boolean / object<additional:any> | false |  |  |  |
| allowLinks | boolean | false |  |  |  |
| allow_links | boolean | false |  |  |  |
| allowImages | boolean | false |  |  |  |
| allow_images | boolean | false |  |  |  |

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownInlineOptions.properties.enabled
- Item ID: defprop__markdownInlineOptions__enabled
- 種別: definition_property
- 名前: enabled
- 親: markdownInlineOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownInlineOptions.properties.inline
- Item ID: defprop__markdownInlineOptions__inline
- 種別: definition_property
- 名前: inline
- 親: markdownInlineOptions
- 型概要: oneOf: boolean / object<additional:any>
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "oneOf": [
    {
      "type": "boolean"
    },
    {
      "type": "object",
      "additionalProperties": true
    }
  ]
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| oneOf | 2 branches |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownInlineOptions.properties.allowLinks
- Item ID: defprop__markdownInlineOptions__allowLinks
- 種別: definition_property
- 名前: allowLinks
- 親: markdownInlineOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownInlineOptions.properties.allow_links
- Item ID: defprop__markdownInlineOptions__allow_links
- 種別: definition_property
- 名前: allow_links
- 親: markdownInlineOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownInlineOptions.properties.allowImages
- Item ID: defprop__markdownInlineOptions__allowImages
- 種別: definition_property
- 名前: allowImages
- 親: markdownInlineOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

### $defs.markdownInlineOptions.properties.allow_images
- Item ID: defprop__markdownInlineOptions__allow_images
- 種別: definition_property
- 名前: allow_images
- 親: markdownInlineOptions
- 型概要: boolean
- 必須: false
- 優先度: medium
- レビュー状態: 未レビュー
- 確認状態: 未確認
- 承認: 未承認

#### 説明


##### Raw Schema JSON

{
  "type": "boolean"
}

#### 制約一覧

| 制約 | 値 |
| --- | --- |
| type | boolean |

#### 子Properties

（なし）

#### レビュー会話


#### 変更履歴

（なし）

---

# AI貼り付け用

## ViewDef Schemaレビュー コメント生成プロンプト

<details open>
<summary>プロンプト + TSV を表示</summary>

```text
以下はViewDef Schemaレビュー一覧のTSVです。
未確認・未承認・説明不足に見えるSchema項目について、レビューコメント案を作成してください。

条件:
- 元Schemaの意味を壊さない
- required / enum / oneOf / $ref の見落としに注意する
- ViewDef Runtime実装とSchema定義がずれていそうな箇所を指摘する
- approval_decision を勝手に承認へ変更しない

TSV:
No.	種別	名前	親	Schema Path	型概要	必須	参照	優先度	レビュー状態	確認状態	承認	説明
1	root_property	app		properties.app	object{2 properties}	false		medium	未レビュー	未確認	未承認	
2	root_property	views		properties.views	array<ref: view>	true	view	medium	未レビュー	未確認	未承認	
3	root_property	extends		properties.extends	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	ViewDef inheritance. String or array of parent view_def JSON file names.
4	root_property	viewDefReport		properties.viewDefReport	ref: viewDefReportOptions	false	viewDefReportOptions	medium	未レビュー	未確認	未承認	
5	root_property	dataSources		properties.dataSources	ref: dataSources	false	dataSources	medium	未レビュー	未確認	未承認	
6	root_property	data_sources		properties.data_sources	ref: dataSources	false	dataSources	medium	未レビュー	未確認	未承認	
7	root_property	virtualData		properties.virtualData	ref: virtualData	false	virtualData	medium	未レビュー	未確認	未承認	
8	root_property	virtual_data		properties.virtual_data	ref: virtualData	false	virtualData	medium	未レビュー	未確認	未承認	
9	root_property	writePolicy		properties.writePolicy	ref: writePolicy	false	writePolicy	medium	未レビュー	未確認	未承認	
10	root_property	write_policy		properties.write_policy	ref: writePolicy	false	writePolicy	medium	未レビュー	未確認	未承認	
11	root_property	fieldTypeSources		properties.fieldTypeSources	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	
12	root_property	field_type_sources		properties.field_type_sources	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	
13	root_property	typeSources		properties.typeSources	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	
14	root_property	type_sources		properties.type_sources	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	
15	root_property	commonTypeRegistry		properties.commonTypeRegistry	object<additional:any>	false		medium	未レビュー	未確認	未承認	
16	root_property	common_type_registry		properties.common_type_registry	object<additional:any>	false		medium	未レビュー	未確認	未承認	
17	root_property	commonTypes		properties.commonTypes	object<additional:any>	false		medium	未レビュー	未確認	未承認	
18	root_property	common_types		properties.common_types	object<additional:any>	false		medium	未レビュー	未確認	未承認	
19	root_property	toolbar		properties.toolbar	ref: toolbarOptions	false	toolbarOptions	medium	未レビュー	未確認	未承認	
20	definition	view	$defs	$defs.view	object{21 properties}	false	layoutOptions, section, markdownOptions, viewDefReportOptions, dataSources, dataSources, virtualData, virtualData, writePolicy, writePolicy, toolbarOptions	high	未レビュー	未確認	未承認	
21	definition_property	id	view	$defs.view.properties.id	string	true		high	未レビュー	未確認	未承認	
22	definition_property	caption	view	$defs.view.properties.caption	string	true		high	未レビュー	未確認	未承認	
23	definition_property	layout	view	$defs.view.properties.layout	oneOf: string enum[1] / ref: layoutOptions	true	layoutOptions	high	未レビュー	未確認	未承認	
24	definition_property	sections	view	$defs.view.properties.sections	array<ref: section>	true	section	high	未レビュー	未確認	未承認	
25	definition_property	markdown	view	$defs.view.properties.markdown	ref: markdownOptions	false	markdownOptions	medium	未レビュー	未確認	未承認	
26	definition_property	viewDefReport	view	$defs.view.properties.viewDefReport	ref: viewDefReportOptions	false	viewDefReportOptions	medium	未レビュー	未確認	未承認	
27	definition_property	dataSources	view	$defs.view.properties.dataSources	ref: dataSources	false	dataSources	medium	未レビュー	未確認	未承認	
28	definition_property	data_sources	view	$defs.view.properties.data_sources	ref: dataSources	false	dataSources	medium	未レビュー	未確認	未承認	
29	definition_property	virtualData	view	$defs.view.properties.virtualData	ref: virtualData	false	virtualData	medium	未レビュー	未確認	未承認	
30	definition_property	virtual_data	view	$defs.view.properties.virtual_data	ref: virtualData	false	virtualData	medium	未レビュー	未確認	未承認	
31	definition_property	writePolicy	view	$defs.view.properties.writePolicy	ref: writePolicy	false	writePolicy	medium	未レビュー	未確認	未承認	
32	definition_property	write_policy	view	$defs.view.properties.write_policy	ref: writePolicy	false	writePolicy	medium	未レビュー	未確認	未承認	
33	definition_property	toolbar	view	$defs.view.properties.toolbar	ref: toolbarOptions	false	toolbarOptions	medium	未レビュー	未確認	未承認	
34	definition_property	fieldTypeSources	view	$defs.view.properties.fieldTypeSources	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	
35	definition_property	field_type_sources	view	$defs.view.properties.field_type_sources	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	
36	definition_property	typeSources	view	$defs.view.properties.typeSources	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	
37	definition_property	type_sources	view	$defs.view.properties.type_sources	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	
38	definition_property	commonTypeRegistry	view	$defs.view.properties.commonTypeRegistry	object<additional:any>	false		medium	未レビュー	未確認	未承認	
39	definition_property	common_type_registry	view	$defs.view.properties.common_type_registry	object<additional:any>	false		medium	未レビュー	未確認	未承認	
40	definition_property	commonTypes	view	$defs.view.properties.commonTypes	object<additional:any>	false		medium	未レビュー	未確認	未承認	
41	definition_property	common_types	view	$defs.view.properties.common_types	object<additional:any>	false		medium	未レビュー	未確認	未承認	
42	definition	section	$defs	$defs.section	object{8 properties}	false	field, markdownSectionOptions	high	未レビュー	未確認	未承認	
43	definition_property	id	section	$defs.section.properties.id	string	true		high	未レビュー	未確認	未承認	
44	definition_property	caption	section	$defs.section.properties.caption	string	true		high	未レビュー	未確認	未承認	
45	definition_property	type	section	$defs.section.properties.type	string enum[2]	true		high	未レビュー	未確認	未承認	
46	definition_property	role	section	$defs.section.properties.role	string	false		medium	未レビュー	未確認	未承認	
47	definition_property	dataPath	section	$defs.section.properties.dataPath	string	true		high	未レビュー	未確認	未承認	
48	definition_property	keyField	section	$defs.section.properties.keyField	string	false		medium	未レビュー	未確認	未承認	
49	definition_property	fields	section	$defs.section.properties.fields	array<ref: field>	true	field	high	未レビュー	未確認	未承認	
50	definition_property	markdown	section	$defs.section.properties.markdown	ref: markdownSectionOptions	false	markdownSectionOptions	medium	未レビュー	未確認	未承認	
51	definition	field	$defs	$defs.field	object{26 properties}	false	fieldType, optionItem, gridOptions, editOptions, searchOptions, validationOptions, createOptions	high	未レビュー	未確認	未承認	
52	definition_property	field	field	$defs.field.properties.field	string	true		high	未レビュー	未確認	未承認	
53	definition_property	caption	field	$defs.field.properties.caption	string	true		high	未レビュー	未確認	未承認	
54	definition_property	type	field	$defs.field.properties.type	ref: fieldType	true	fieldType	high	未レビュー	未確認	未承認	
55	definition_property	readonly	field	$defs.field.properties.readonly	boolean	false		medium	未レビュー	未確認	未承認	
56	definition_property	options	field	$defs.field.properties.options	array<ref: optionItem>	false	optionItem	medium	未レビュー	未確認	未承認	
57	definition_property	grid	field	$defs.field.properties.grid	ref: gridOptions	false	gridOptions	medium	未レビュー	未確認	未承認	
58	definition_property	edit	field	$defs.field.properties.edit	ref: editOptions	false	editOptions	medium	未レビュー	未確認	未承認	
59	definition_property	search	field	$defs.field.properties.search	ref: searchOptions	false	searchOptions	medium	未レビュー	未確認	未承認	
60	definition_property	format	field	$defs.field.properties.format	string	false		medium	未レビュー	未確認	未承認	
61	definition_property	defaultValue	field	$defs.field.properties.defaultValue	bool	false		medium	未レビュー	未確認	未承認	
62	definition_property	validation	field	$defs.field.properties.validation	ref: validationOptions	false	validationOptions	medium	未レビュー	未確認	未承認	
63	definition_property	create	field	$defs.field.properties.create	ref: createOptions	false	createOptions	medium	未レビュー	未確認	未承認	
64	definition_property	layout	field	$defs.field.properties.layout	object{3 properties}	false		medium	未レビュー	未確認	未承認	Detail Dialog内の配置制御。例: {"placement":"detailFooter"} で子配列表示後に描画する。
65	definition_property	control	field	$defs.field.properties.control	string enum[3]	false		medium	未レビュー	未確認	未承認	
66	definition_property	fieldType	field	$defs.field.properties.fieldType	string	false		medium	未レビュー	未確認	未承認	
67	definition_property	field_type	field	$defs.field.properties.field_type	string	false		medium	未レビュー	未確認	未承認	
68	definition_property	typeRef	field	$defs.field.properties.typeRef	string	false		medium	未レビュー	未確認	未承認	
69	definition_property	type_ref	field	$defs.field.properties.type_ref	string	false		medium	未レビュー	未確認	未承認	
70	definition_property	valueField	field	$defs.field.properties.valueField	string	false		medium	未レビュー	未確認	未承認	
71	definition_property	value_field	field	$defs.field.properties.value_field	string	false		medium	未レビュー	未確認	未承認	
72	definition_property	optionValueField	field	$defs.field.properties.optionValueField	string	false		medium	未レビュー	未確認	未承認	
73	definition_property	option_value_field	field	$defs.field.properties.option_value_field	string	false		medium	未レビュー	未確認	未承認	
74	definition_property	labelField	field	$defs.field.properties.labelField	string	false		medium	未レビュー	未確認	未承認	
75	definition_property	label_field	field	$defs.field.properties.label_field	string	false		medium	未レビュー	未確認	未承認	
76	definition_property	optionLabelField	field	$defs.field.properties.optionLabelField	string	false		medium	未レビュー	未確認	未承認	
77	definition_property	option_label_field	field	$defs.field.properties.option_label_field	string	false		medium	未レビュー	未確認	未承認	
78	definition	fieldType	$defs	$defs.fieldType	string enum[9]	false		high	未レビュー	未確認	未承認	
79	definition	gridOptions	$defs	$defs.gridOptions	object{3 properties}	false		medium	未レビュー	未確認	未承認	
80	definition_property	visible	gridOptions	$defs.gridOptions.properties.visible	boolean	false		medium	未レビュー	未確認	未承認	
81	definition_property	width	gridOptions	$defs.gridOptions.properties.width	number	false		medium	未レビュー	未確認	未承認	
82	definition_property	format	gridOptions	$defs.gridOptions.properties.format	string	false		medium	未レビュー	未確認	未承認	
83	definition	editOptions	$defs	$defs.editOptions	object{11 properties}	false	chatEmbeddedField, chatEmbeddedField, markdownInlineOptions, markdownInlineOptions	high	未レビュー	未確認	未承認	
84	definition_property	visible	editOptions	$defs.editOptions.properties.visible	boolean	false		medium	未レビュー	未確認	未承認	
85	definition_property	readonly	editOptions	$defs.editOptions.properties.readonly	boolean	false		medium	未レビュー	未確認	未承認	
86	definition_property	height	editOptions	$defs.editOptions.properties.height	number	false		medium	未レビュー	未確認	未承認	
87	definition_property	step	editOptions	$defs.editOptions.properties.step	string | number	false		medium	未レビュー	未確認	未承認	
88	definition_property	min	editOptions	$defs.editOptions.properties.min	string | number	false		medium	未レビュー	未確認	未承認	
89	definition_property	max	editOptions	$defs.editOptions.properties.max	string | number	false		medium	未レビュー	未確認	未承認	
90	definition_property	format	editOptions	$defs.editOptions.properties.format	string	false		medium	未レビュー	未確認	未承認	
91	definition_property	control	editOptions	$defs.editOptions.properties.control	string enum[3]	false		medium	未レビュー	未確認	未承認	
92	definition_property	messages	editOptions	$defs.editOptions.properties.messages	array<object{9 properties}>	false	chatEmbeddedField, chatEmbeddedField, markdownInlineOptions	medium	未レビュー	未確認	未承認	Field type chat用。複数フィールドを会話タイムラインとして表示するためのメッセージ定義。
93	definition_property	layout	editOptions	$defs.editOptions.properties.layout	object{3 properties}	false		medium	未レビュー	未確認	未承認	Fieldのedit表示における配置制御。field.layout と同じ意味で利用可能。
94	definition_property	input	editOptions	$defs.editOptions.properties.input	object{14 properties}	false	markdownInlineOptions	medium	未レビュー	未確認	未承認	Field type chat用のコメント追加入力バー設定。
95	definition	searchOptions	$defs	$defs.searchOptions	object{2 properties}	false		medium	未レビュー	未確認	未承認	
96	definition_property	visible	searchOptions	$defs.searchOptions.properties.visible	boolean	false		medium	未レビュー	未確認	未承認	
97	definition_property	operator	searchOptions	$defs.searchOptions.properties.operator	string enum[4]	false		medium	未レビュー	未確認	未承認	
98	definition	validationOptions	$defs	$defs.validationOptions	object{1 properties}	false		medium	未レビュー	未確認	未承認	
99	definition_property	required	validationOptions	$defs.validationOptions.properties.required	boolean	false		medium	未レビュー	未確認	未承認	
100	definition	createOptions	$defs	$defs.createOptions	object{1 properties}	false		medium	未レビュー	未確認	未承認	
101	definition_property	include	createOptions	$defs.createOptions.properties.include	boolean	false		medium	未レビュー	未確認	未承認	
102	definition	markdownOptions	$defs	$defs.markdownOptions	object{8 properties}	false	markdownSectionOptions	high	未レビュー	未確認	未承認	Data JSON export configuration used by Markdown出力→Viewer. Not used for ViewDef Markdown→Viewer.
103	definition_property	enabled	markdownOptions	$defs.markdownOptions.properties.enabled	boolean	false		medium	未レビュー	未確認	未承認	
104	definition_property	type	markdownOptions	$defs.markdownOptions.properties.type	string enum[5]	false		medium	未レビュー	未確認	未承認	MarkdownExportRegistry key. Current registered values: auto, generic_sections, screen_state_expected, screen_state_diff, screen_state_test_patterns.
105	definition_property	exportType	markdownOptions	$defs.markdownOptions.properties.exportType	string	false		medium	未レビュー	未確認	未承認	
106	definition_property	title	markdownOptions	$defs.markdownOptions.properties.title	string	false		medium	未レビュー	未確認	未承認	
107	definition_property	fileName	markdownOptions	$defs.markdownOptions.properties.fileName	string	false		medium	未レビュー	未確認	未承認	
108	definition_property	filename	markdownOptions	$defs.markdownOptions.properties.filename	string	false		medium	未レビュー	未確認	未承認	
109	definition_property	defaultFileName	markdownOptions	$defs.markdownOptions.properties.defaultFileName	string	false		medium	未レビュー	未確認	未承認	
110	definition_property	sections	markdownOptions	$defs.markdownOptions.properties.sections	array<ref: markdownSectionOptions>	false	markdownSectionOptions	medium	未レビュー	未確認	未承認	
111	definition	markdownSectionOptions	$defs	$defs.markdownSectionOptions	object{12 properties}	false	markdownFieldOptions, aiPromptOptions, aiPromptOptions, markdownSectionOptions	medium	未レビュー	未確認	未承認	
112	definition_property	title	markdownSectionOptions	$defs.markdownSectionOptions.properties.title	string	false		medium	未レビュー	未確認	未承認	
113	definition_property	source	markdownSectionOptions	$defs.markdownSectionOptions.properties.source	string enum[8]	false		medium	未レビュー	未確認	未承認	
114	definition_property	dataPath	markdownSectionOptions	$defs.markdownSectionOptions.properties.dataPath	string	false		medium	未レビュー	未確認	未承認	
115	definition_property	arrayField	markdownSectionOptions	$defs.markdownSectionOptions.properties.arrayField	string	false		medium	未レビュー	未確認	未承認	
116	definition_property	format	markdownSectionOptions	$defs.markdownSectionOptions.properties.format	string enum[16]	false		medium	未レビュー	未確認	未承認	
117	definition_property	fields	markdownSectionOptions	$defs.markdownSectionOptions.properties.fields	array<ref: markdownFieldOptions>	false	markdownFieldOptions	medium	未レビュー	未確認	未承認	
118	definition_property	visible	markdownSectionOptions	$defs.markdownSectionOptions.properties.visible	boolean	false		medium	未レビュー	未確認	未承認	
119	definition_property	aiPrompt	markdownSectionOptions	$defs.markdownSectionOptions.properties.aiPrompt	ref: aiPromptOptions	false	aiPromptOptions	medium	未レビュー	未確認	未承認	
120	definition_property	ai_prompt	markdownSectionOptions	$defs.markdownSectionOptions.properties.ai_prompt	ref: aiPromptOptions	false	aiPromptOptions	medium	未レビュー	未確認	未承認	
121	definition_property	itemTitle	markdownSectionOptions	$defs.markdownSectionOptions.properties.itemTitle	string	false		medium	未レビュー	未確認	未承認	
122	definition_property	showEmpty	markdownSectionOptions	$defs.markdownSectionOptions.properties.showEmpty	boolean	false		medium	未レビュー	未確認	未承認	
123	definition_property	sections	markdownSectionOptions	$defs.markdownSectionOptions.properties.sections	array<ref: markdownSectionOptions>	false	markdownSectionOptions	medium	未レビュー	未確認	未承認	
124	definition	markdownFieldOptions	$defs	$defs.markdownFieldOptions	object{8 properties}	false		medium	未レビュー	未確認	未承認	
125	definition_property	field	markdownFieldOptions	$defs.markdownFieldOptions.properties.field	string	true		high	未レビュー	未確認	未承認	
126	definition_property	caption	markdownFieldOptions	$defs.markdownFieldOptions.properties.caption	string	false		medium	未レビュー	未確認	未承認	
127	definition_property	format	markdownFieldOptions	$defs.markdownFieldOptions.properties.format	string enum[16]	false		medium	未レビュー	未確認	未承認	
128	definition_property	visible	markdownFieldOptions	$defs.markdownFieldOptions.properties.visible	boolean	false		medium	未レビュー	未確認	未承認	
129	definition_property	empty	markdownFieldOptions	$defs.markdownFieldOptions.properties.empty	string | number | boolean | null	false		medium	未レビュー	未確認	未承認	
130	definition_property	markdownFormat	markdownFieldOptions	$defs.markdownFieldOptions.properties.markdownFormat	string enum[16]	false		medium	未レビュー	未確認	未承認	
131	definition_property	showEmpty	markdownFieldOptions	$defs.markdownFieldOptions.properties.showEmpty	boolean	false		medium	未レビュー	未確認	未承認	
132	definition_property	label	markdownFieldOptions	$defs.markdownFieldOptions.properties.label	string	false		medium	未レビュー	未確認	未承認	
133	definition	viewDefReportOptions	$defs	$defs.viewDefReportOptions	object{4 properties}	false		medium	未レビュー	未確認	未承認	Future options for ViewDef Markdown→Viewer report. Separate from markdown.type.
134	definition_property	enabled	viewDefReportOptions	$defs.viewDefReportOptions.properties.enabled	boolean	false		medium	未レビュー	未確認	未承認	
135	definition_property	includeInheritanceDiff	viewDefReportOptions	$defs.viewDefReportOptions.properties.includeInheritanceDiff	boolean	false		medium	未レビュー	未確認	未承認	
136	definition_property	includeResolvedJson	viewDefReportOptions	$defs.viewDefReportOptions.properties.includeResolvedJson	boolean	false		medium	未レビュー	未確認	未承認	
137	definition_property	includeRawJson	viewDefReportOptions	$defs.viewDefReportOptions.properties.includeRawJson	boolean	false		medium	未レビュー	未確認	未承認	
138	definition	chatEmbeddedField	$defs	$defs.chatEmbeddedField	object{8 properties}	false	fieldType, optionItem, editOptions	medium	未レビュー	未確認	未承認	
139	definition_property	field	chatEmbeddedField	$defs.chatEmbeddedField.properties.field	string	true		high	未レビュー	未確認	未承認	
140	definition_property	label	chatEmbeddedField	$defs.chatEmbeddedField.properties.label	string	false		medium	未レビュー	未確認	未承認	
141	definition_property	caption	chatEmbeddedField	$defs.chatEmbeddedField.properties.caption	string	false		medium	未レビュー	未確認	未承認	
142	definition_property	type	chatEmbeddedField	$defs.chatEmbeddedField.properties.type	ref: fieldType	false	fieldType	medium	未レビュー	未確認	未承認	
143	definition_property	control	chatEmbeddedField	$defs.chatEmbeddedField.properties.control	string enum[3]	false		medium	未レビュー	未確認	未承認	
144	definition_property	options	chatEmbeddedField	$defs.chatEmbeddedField.properties.options	array<ref: optionItem>	false	optionItem	medium	未レビュー	未確認	未承認	
145	definition_property	readonly	chatEmbeddedField	$defs.chatEmbeddedField.properties.readonly	boolean	false		medium	未レビュー	未確認	未承認	
146	definition_property	edit	chatEmbeddedField	$defs.chatEmbeddedField.properties.edit	ref: editOptions	false	editOptions	medium	未レビュー	未確認	未承認	
147	definition	dataSourceSpec	$defs	$defs.dataSourceSpec	object{6 properties}	false		medium	未レビュー	未確認	未承認	
148	definition_property	name	dataSourceSpec	$defs.dataSourceSpec.properties.name	string	false		medium	未レビュー	未確認	未承認	
149	definition_property	file	dataSourceSpec	$defs.dataSourceSpec.properties.file	string	false		medium	未レビュー	未確認	未承認	
150	definition_property	path	dataSourceSpec	$defs.dataSourceSpec.properties.path	string	false		medium	未レビュー	未確認	未承認	
151	definition_property	data	dataSourceSpec	$defs.dataSourceSpec.properties.data	string	false		medium	未レビュー	未確認	未承認	
152	definition_property	source	dataSourceSpec	$defs.dataSourceSpec.properties.source	string	false		medium	未レビュー	未確認	未承認	
153	definition_property	inline	dataSourceSpec	$defs.dataSourceSpec.properties.inline	bool	false		medium	未レビュー	未確認	未承認	
154	definition	dataSources	$defs	$defs.dataSources	object<additional:oneOf: string / ref: dataSourceSpec>	false	dataSourceSpec	medium	未レビュー	未確認	未承認	
155	definition	virtualData	$defs	$defs.virtualData	oneOf: ref: virtualDataConfig / array<ref: virtualDataConfig>	false	virtualDataConfig, virtualDataConfig	medium	未レビュー	未確認	未承認	
156	definition	virtualDataConfig	$defs	$defs.virtualDataConfig	object{25 properties}	false	relationAxisSource, relationAxisSource, relationAxisSource, relationAxisSource, relationQuery, relationQuery, relationQuery, relationSource, relationSource, relationSource, diffSource, diffViewDefs, diffViewDefs, virtualOutputs, virtualDataWriteBack, virtualDataWriteBack	medium	未レビュー	未確認	未承認	
157	definition_property	builder	virtualDataConfig	$defs.virtualDataConfig.properties.builder	string	false		medium	未レビュー	未確認	未承認	VirtualDataBuilderRegistry key. Registered examples: relation_axis_cards, relation_diff_cards, relation_diff_check_cards, constraint_trace_cards, test_pattern_trace_cards, expected_check_cross_counts, expected_check_shortage_findings.
158	definition_property	type	virtualDataConfig	$defs.virtualDataConfig.properties.type	string	false		medium	未レビュー	未確認	未承認	
159	definition_property	kind	virtualDataConfig	$defs.virtualDataConfig.properties.kind	string	false		medium	未レビュー	未確認	未承認	
160	definition_property	targetPath	virtualDataConfig	$defs.virtualDataConfig.properties.targetPath	string	false		medium	未レビュー	未確認	未承認	
161	definition_property	target_path	virtualDataConfig	$defs.virtualDataConfig.properties.target_path	string	false		medium	未レビュー	未確認	未承認	
162	definition_property	dataPath	virtualDataConfig	$defs.virtualDataConfig.properties.dataPath	string	false		medium	未レビュー	未確認	未承認	
163	definition_property	data_path	virtualDataConfig	$defs.virtualDataConfig.properties.data_path	string	false		medium	未レビュー	未確認	未承認	
164	definition_property	axis	virtualDataConfig	$defs.virtualDataConfig.properties.axis	ref: relationAxisSource	false	relationAxisSource	medium	未レビュー	未確認	未承認	
165	definition_property	base	virtualDataConfig	$defs.virtualDataConfig.properties.base	ref: relationAxisSource	false	relationAxisSource	medium	未レビュー	未確認	未承認	
166	definition_property	linked	virtualDataConfig	$defs.virtualDataConfig.properties.linked	ref: relationAxisSource	false	relationAxisSource	medium	未レビュー	未確認	未承認	
167	definition_property	target	virtualDataConfig	$defs.virtualDataConfig.properties.target	ref: relationAxisSource	false	relationAxisSource	medium	未レビュー	未確認	未承認	
168	definition_property	relation	virtualDataConfig	$defs.virtualDataConfig.properties.relation	ref: relationQuery	false	relationQuery	medium	未レビュー	未確認	未承認	
169	definition_property	relationQuery	virtualDataConfig	$defs.virtualDataConfig.properties.relationQuery	ref: relationQuery	false	relationQuery	medium	未レビュー	未確認	未承認	
170	definition_property	relation_query	virtualDataConfig	$defs.virtualDataConfig.properties.relation_query	ref: relationQuery	false	relationQuery	medium	未レビュー	未確認	未承認	
171	definition_property	relations	virtualDataConfig	$defs.virtualDataConfig.properties.relations	ref: relationSource	false	relationSource	medium	未レビュー	未確認	未承認	
172	definition_property	relationSource	virtualDataConfig	$defs.virtualDataConfig.properties.relationSource	ref: relationSource	false	relationSource	medium	未レビュー	未確認	未承認	
173	definition_property	relation_source	virtualDataConfig	$defs.virtualDataConfig.properties.relation_source	ref: relationSource	false	relationSource	medium	未レビュー	未確認	未承認	
174	definition_property	diff	virtualDataConfig	$defs.virtualDataConfig.properties.diff	ref: diffSource	false	diffSource	medium	未レビュー	未確認	未承認	
175	definition_property	diffViewDefs	virtualDataConfig	$defs.virtualDataConfig.properties.diffViewDefs	ref: diffViewDefs	false	diffViewDefs	medium	未レビュー	未確認	未承認	
176	definition_property	diff_view_defs	virtualDataConfig	$defs.virtualDataConfig.properties.diff_view_defs	ref: diffViewDefs	false	diffViewDefs	medium	未レビュー	未確認	未承認	
177	definition_property	outputs	virtualDataConfig	$defs.virtualDataConfig.properties.outputs	ref: virtualOutputs	false	virtualOutputs	medium	未レビュー	未確認	未承認	
178	definition_property	summaryFields	virtualDataConfig	$defs.virtualDataConfig.properties.summaryFields	object<additional:any>	false		medium	未レビュー	未確認	未承認	
179	definition_property	summary_fields	virtualDataConfig	$defs.virtualDataConfig.properties.summary_fields	object<additional:any>	false		medium	未レビュー	未確認	未承認	
180	definition_property	writeBack	virtualDataConfig	$defs.virtualDataConfig.properties.writeBack	ref: virtualDataWriteBack	false	virtualDataWriteBack	medium	未レビュー	未確認	未承認	
181	definition_property	write_back	virtualDataConfig	$defs.virtualDataConfig.properties.write_back	ref: virtualDataWriteBack	false	virtualDataWriteBack	medium	未レビュー	未確認	未承認	
182	definition	relationAxisSource	$defs	$defs.relationAxisSource	object{16 properties}	false		medium	未レビュー	未確認	未承認	
183	definition_property	source	relationAxisSource	$defs.relationAxisSource.properties.source	string	false		medium	未レビュー	未確認	未承認	
184	definition_property	dataSource	relationAxisSource	$defs.relationAxisSource.properties.dataSource	string	false		medium	未レビュー	未確認	未承認	
185	definition_property	data_source	relationAxisSource	$defs.relationAxisSource.properties.data_source	string	false		medium	未レビュー	未確認	未承認	
186	definition_property	adapter	relationAxisSource	$defs.relationAxisSource.properties.adapter	string	false		medium	未レビュー	未確認	未承認	
187	definition_property	kind	relationAxisSource	$defs.relationAxisSource.properties.kind	string	false		medium	未レビュー	未確認	未承認	
188	definition_property	path	relationAxisSource	$defs.relationAxisSource.properties.path	string	false		medium	未レビュー	未確認	未承認	
189	definition_property	dataPath	relationAxisSource	$defs.relationAxisSource.properties.dataPath	string	false		medium	未レビュー	未確認	未承認	
190	definition_property	data_path	relationAxisSource	$defs.relationAxisSource.properties.data_path	string	false		medium	未レビュー	未確認	未承認	
191	definition_property	fallbackPaths	relationAxisSource	$defs.relationAxisSource.properties.fallbackPaths	array<string>	false		medium	未レビュー	未確認	未承認	
192	definition_property	fallback_paths	relationAxisSource	$defs.relationAxisSource.properties.fallback_paths	array<string>	false		medium	未レビュー	未確認	未承認	
193	definition_property	nodeType	relationAxisSource	$defs.relationAxisSource.properties.nodeType	string	false		medium	未レビュー	未確認	未承認	
194	definition_property	node_type	relationAxisSource	$defs.relationAxisSource.properties.node_type	string	false		medium	未レビュー	未確認	未承認	
195	definition_property	idField	relationAxisSource	$defs.relationAxisSource.properties.idField	string	false		medium	未レビュー	未確認	未承認	
196	definition_property	id_field	relationAxisSource	$defs.relationAxisSource.properties.id_field	string	false		medium	未レビュー	未確認	未承認	
197	definition_property	titleField	relationAxisSource	$defs.relationAxisSource.properties.titleField	string	false		medium	未レビュー	未確認	未承認	
198	definition_property	title_field	relationAxisSource	$defs.relationAxisSource.properties.title_field	string	false		medium	未レビュー	未確認	未承認	
199	definition	relationSource	$defs	$defs.relationSource	object{6 properties}	false		medium	未レビュー	未確認	未承認	
200	definition_property	source	relationSource	$defs.relationSource.properties.source	string	false		medium	未レビュー	未確認	未承認	
201	definition_property	dataSource	relationSource	$defs.relationSource.properties.dataSource	string	false		medium	未レビュー	未確認	未承認	
202	definition_property	data_source	relationSource	$defs.relationSource.properties.data_source	string	false		medium	未レビュー	未確認	未承認	
203	definition_property	path	relationSource	$defs.relationSource.properties.path	string	false		medium	未レビュー	未確認	未承認	
204	definition_property	relationsPath	relationSource	$defs.relationSource.properties.relationsPath	string	false		medium	未レビュー	未確認	未承認	
205	definition_property	relations_path	relationSource	$defs.relationSource.properties.relations_path	string	false		medium	未レビュー	未確認	未承認	
206	definition	relationQuery	$defs	$defs.relationQuery	object{31 properties}	false		medium	未レビュー	未確認	未承認	
207	definition_property	source	relationQuery	$defs.relationQuery.properties.source	string	false		medium	未レビュー	未確認	未承認	
208	definition_property	dataSource	relationQuery	$defs.relationQuery.properties.dataSource	string	false		medium	未レビュー	未確認	未承認	
209	definition_property	data_source	relationQuery	$defs.relationQuery.properties.data_source	string	false		medium	未レビュー	未確認	未承認	
210	definition_property	path	relationQuery	$defs.relationQuery.properties.path	string	false		medium	未レビュー	未確認	未承認	
211	definition_property	relationsPath	relationQuery	$defs.relationQuery.properties.relationsPath	string	false		medium	未レビュー	未確認	未承認	
212	definition_property	relations_path	relationQuery	$defs.relationQuery.properties.relations_path	string	false		medium	未レビュー	未確認	未承認	
213	definition_property	name	relationQuery	$defs.relationQuery.properties.name	string	false		medium	未レビュー	未確認	未承認	
214	definition_property	relation	relationQuery	$defs.relationQuery.properties.relation	string	false		medium	未レビュー	未確認	未承認	
215	definition_property	relationName	relationQuery	$defs.relationQuery.properties.relationName	string	false		medium	未レビュー	未確認	未承認	
216	definition_property	relation_name	relationQuery	$defs.relationQuery.properties.relation_name	string	false		medium	未レビュー	未確認	未承認	
217	definition_property	direction	relationQuery	$defs.relationQuery.properties.direction	string enum[2]	false		medium	未レビュー	未確認	未承認	
218	definition_property	includeViaCheck	relationQuery	$defs.relationQuery.properties.includeViaCheck	boolean	false		medium	未レビュー	未確認	未承認	
219	definition_property	include_via_check	relationQuery	$defs.relationQuery.properties.include_via_check	boolean	false		medium	未レビュー	未確認	未承認	
220	definition_property	verifiedByRelation	relationQuery	$defs.relationQuery.properties.verifiedByRelation	string	false		medium	未レビュー	未確認	未承認	
221	definition_property	verified_by_relation	relationQuery	$defs.relationQuery.properties.verified_by_relation	string	false		medium	未レビュー	未確認	未承認	
222	definition_property	containsCheckRelation	relationQuery	$defs.relationQuery.properties.containsCheckRelation	string	false		medium	未レビュー	未確認	未承認	
223	definition_property	contains_check_relation	relationQuery	$defs.relationQuery.properties.contains_check_relation	string	false		medium	未レビュー	未確認	未承認	
224	definition_property	testNodeType	relationQuery	$defs.relationQuery.properties.testNodeType	string	false		medium	未レビュー	未確認	未承認	
225	definition_property	test_node_type	relationQuery	$defs.relationQuery.properties.test_node_type	string	false		medium	未レビュー	未確認	未承認	
226	definition_property	checkType	relationQuery	$defs.relationQuery.properties.checkType	string	false		medium	未レビュー	未確認	未承認	
227	definition_property	check_type	relationQuery	$defs.relationQuery.properties.check_type	string	false		medium	未レビュー	未確認	未承認	
228	definition_property	constraintType	relationQuery	$defs.relationQuery.properties.constraintType	string	false		medium	未レビュー	未確認	未承認	
229	definition_property	constraint_type	relationQuery	$defs.relationQuery.properties.constraint_type	string	false		medium	未レビュー	未確認	未承認	
230	definition_property	statusFilter	relationQuery	$defs.relationQuery.properties.statusFilter	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	Evidence relation statuses to include, e.g. ["approved"].
231	definition_property	status_filter	relationQuery	$defs.relationQuery.properties.status_filter	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	Evidence relation statuses to include, snake_case alias.
232	definition_property	structureStatusFilter	relationQuery	$defs.relationQuery.properties.structureStatusFilter	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	Structure relation statuses to include for contains_check etc, e.g. ["derived","approved"].
233	definition_property	structure_status_filter	relationQuery	$defs.relationQuery.properties.structure_status_filter	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	Structure relation statuses to include, snake_case alias.
234	definition_property	excludeStatus	relationQuery	$defs.relationQuery.properties.excludeStatus	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	Relation statuses to always exclude, e.g. ["rejected"].
235	definition_property	exclude_status	relationQuery	$defs.relationQuery.properties.exclude_status	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	Relation statuses to always exclude, snake_case alias.
236	definition_property	includeStatus	relationQuery	$defs.relationQuery.properties.includeStatus	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	Alias for statusFilter.
237	definition_property	include_status	relationQuery	$defs.relationQuery.properties.include_status	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	Alias for statusFilter, snake_case.
238	definition	diffSource	$defs	$defs.diffSource	object{10 properties}	false		medium	未レビュー	未確認	未承認	
239	definition_property	source	diffSource	$defs.diffSource.properties.source	string	false		medium	未レビュー	未確認	未承認	
240	definition_property	dataSource	diffSource	$defs.diffSource.properties.dataSource	string	false		medium	未レビュー	未確認	未承認	
241	definition_property	data_source	diffSource	$defs.diffSource.properties.data_source	string	false		medium	未レビュー	未確認	未承認	
242	definition_property	enabled	diffSource	$defs.diffSource.properties.enabled	boolean	false		medium	未レビュー	未確認	未承認	
243	definition_property	testNodeType	diffSource	$defs.diffSource.properties.testNodeType	string	false		medium	未レビュー	未確認	未承認	
244	definition_property	test_node_type	diffSource	$defs.diffSource.properties.test_node_type	string	false		medium	未レビュー	未確認	未承認	
245	definition_property	testIdField	diffSource	$defs.diffSource.properties.testIdField	string	false		medium	未レビュー	未確認	未承認	
246	definition_property	test_id_field	diffSource	$defs.diffSource.properties.test_id_field	string	false		medium	未レビュー	未確認	未承認	
247	definition_property	checksPath	diffSource	$defs.diffSource.properties.checksPath	string	false		medium	未レビュー	未確認	未承認	
248	definition_property	checks_path	diffSource	$defs.diffSource.properties.checks_path	string	false		medium	未レビュー	未確認	未承認	
249	definition	diffViewDefRef	$defs	$defs.diffViewDefRef	object{9 properties}	false		medium	未レビュー	未確認	未承認	
250	definition_property	role	diffViewDefRef	$defs.diffViewDefRef.properties.role	string enum[2]	false		medium	未レビュー	未確認	未承認	
251	definition_property	view_def	diffViewDefRef	$defs.diffViewDefRef.properties.view_def	string	false		medium	未レビュー	未確認	未承認	
252	definition_property	name	diffViewDefRef	$defs.diffViewDefRef.properties.name	string	false		medium	未レビュー	未確認	未承認	
253	definition_property	file	diffViewDefRef	$defs.diffViewDefRef.properties.file	string	false		medium	未レビュー	未確認	未承認	
254	definition_property	caption	diffViewDefRef	$defs.diffViewDefRef.properties.caption	string	false		medium	未レビュー	未確認	未承認	
255	definition_property	label	diffViewDefRef	$defs.diffViewDefRef.properties.label	string	false		medium	未レビュー	未確認	未承認	
256	definition_property	extends	diffViewDefRef	$defs.diffViewDefRef.properties.extends	string	false		medium	未レビュー	未確認	未承認	
257	definition_property	note	diffViewDefRef	$defs.diffViewDefRef.properties.note	string	false		medium	未レビュー	未確認	未承認	
258	definition_property	active	diffViewDefRef	$defs.diffViewDefRef.properties.active	boolean	false		medium	未レビュー	未確認	未承認	
259	definition	diffViewDefs	$defs	$defs.diffViewDefs	object{3 properties}	false	diffViewDefRef, diffViewDefRef, diffViewDefRef	medium	未レビュー	未確認	未承認	
260	definition_property	base	diffViewDefs	$defs.diffViewDefs.properties.base	ref: diffViewDefRef	false	diffViewDefRef	medium	未レビュー	未確認	未承認	
261	definition_property	children	diffViewDefs	$defs.diffViewDefs.properties.children	array<ref: diffViewDefRef>	false	diffViewDefRef	medium	未レビュー	未確認	未承認	
262	definition_property	child	diffViewDefs	$defs.diffViewDefs.properties.child	array<ref: diffViewDefRef>	false	diffViewDefRef	medium	未レビュー	未確認	未承認	
263	definition	virtualOutputs	$defs	$defs.virtualOutputs	object{26 properties}	false		medium	未レビュー	未確認	未承認	
264	definition_property	idField	virtualOutputs	$defs.virtualOutputs.properties.idField	string	false		medium	未レビュー	未確認	未承認	
265	definition_property	id_field	virtualOutputs	$defs.virtualOutputs.properties.id_field	string	false		medium	未レビュー	未確認	未承認	
266	definition_property	titleField	virtualOutputs	$defs.virtualOutputs.properties.titleField	string	false		medium	未レビュー	未確認	未承認	
267	definition_property	title_field	virtualOutputs	$defs.virtualOutputs.properties.title_field	string	false		medium	未レビュー	未確認	未承認	
268	definition_property	linkedItemsField	virtualOutputs	$defs.virtualOutputs.properties.linkedItemsField	string	false		medium	未レビュー	未確認	未承認	
269	definition_property	linked_items_field	virtualOutputs	$defs.virtualOutputs.properties.linked_items_field	string	false		medium	未レビュー	未確認	未承認	
270	definition_property	relatedDiffsField	virtualOutputs	$defs.virtualOutputs.properties.relatedDiffsField	string	false		medium	未レビュー	未確認	未承認	
271	definition_property	related_diffs_field	virtualOutputs	$defs.virtualOutputs.properties.related_diffs_field	string	false		medium	未レビュー	未確認	未承認	
272	definition_property	failedChecksField	virtualOutputs	$defs.virtualOutputs.properties.failedChecksField	string	false		medium	未レビュー	未確認	未承認	
273	definition_property	failed_checks_field	virtualOutputs	$defs.virtualOutputs.properties.failed_checks_field	string	false		medium	未レビュー	未確認	未承認	
274	definition_property	evidenceEdgesField	virtualOutputs	$defs.virtualOutputs.properties.evidenceEdgesField	string	false		medium	未レビュー	未確認	未承認	
275	definition_property	evidence_edges_field	virtualOutputs	$defs.virtualOutputs.properties.evidence_edges_field	string	false		medium	未レビュー	未確認	未承認	
276	definition_property	impactedItemsField	virtualOutputs	$defs.virtualOutputs.properties.impactedItemsField	string	false		medium	未レビュー	未確認	未承認	
277	definition_property	impacted_items_field	virtualOutputs	$defs.virtualOutputs.properties.impacted_items_field	string	false		medium	未レビュー	未確認	未承認	
278	definition_property	linkedCountField	virtualOutputs	$defs.virtualOutputs.properties.linkedCountField	string	false		medium	未レビュー	未確認	未承認	
279	definition_property	linked_count_field	virtualOutputs	$defs.virtualOutputs.properties.linked_count_field	string	false		medium	未レビュー	未確認	未承認	
280	definition_property	primaryCountField	virtualOutputs	$defs.virtualOutputs.properties.primaryCountField	string	false		medium	未レビュー	未確認	未承認	
281	definition_property	primary_count_field	virtualOutputs	$defs.virtualOutputs.properties.primary_count_field	string	false		medium	未レビュー	未確認	未承認	
282	definition_property	secondaryCountField	virtualOutputs	$defs.virtualOutputs.properties.secondaryCountField	string	false		medium	未レビュー	未確認	未承認	
283	definition_property	secondary_count_field	virtualOutputs	$defs.virtualOutputs.properties.secondary_count_field	string	false		medium	未レビュー	未確認	未承認	
284	definition_property	requiredCountField	virtualOutputs	$defs.virtualOutputs.properties.requiredCountField	string	false		medium	未レビュー	未確認	未承認	
285	definition_property	required_count_field	virtualOutputs	$defs.virtualOutputs.properties.required_count_field	string	false		medium	未レビュー	未確認	未承認	
286	definition_property	failLinkedCountField	virtualOutputs	$defs.virtualOutputs.properties.failLinkedCountField	string	false		medium	未レビュー	未確認	未承認	
287	definition_property	fail_linked_count_field	virtualOutputs	$defs.virtualOutputs.properties.fail_linked_count_field	string	false		medium	未レビュー	未確認	未承認	
288	definition_property	coverageField	virtualOutputs	$defs.virtualOutputs.properties.coverageField	string	false		medium	未レビュー	未確認	未承認	
289	definition_property	coverage_field	virtualOutputs	$defs.virtualOutputs.properties.coverage_field	string	false		medium	未レビュー	未確認	未承認	
290	definition	writePolicy	$defs	$defs.writePolicy	object{13 properties}	false		medium	未レビュー	未確認	未承認	
291	definition_property	mode	writePolicy	$defs.writePolicy.properties.mode	string enum[3]	false		medium	未レビュー	未確認	未承認	
292	definition_property	primarySource	writePolicy	$defs.writePolicy.properties.primarySource	string	false		medium	未レビュー	未確認	未承認	
293	definition_property	primary_source	writePolicy	$defs.writePolicy.properties.primary_source	string	false		medium	未レビュー	未確認	未承認	
294	definition_property	virtualDataReadonly	writePolicy	$defs.writePolicy.properties.virtualDataReadonly	boolean	false		medium	未レビュー	未確認	未承認	
295	definition_property	virtual_data_readonly	writePolicy	$defs.writePolicy.properties.virtual_data_readonly	boolean	false		medium	未レビュー	未確認	未承認	
296	definition_property	editableSources	writePolicy	$defs.writePolicy.properties.editableSources	array<string>	false		medium	未レビュー	未確認	未承認	
297	definition_property	editable_sources	writePolicy	$defs.writePolicy.properties.editable_sources	array<string>	false		medium	未レビュー	未確認	未承認	
298	definition_property	readonlySources	writePolicy	$defs.writePolicy.properties.readonlySources	array<string>	false		medium	未レビュー	未確認	未承認	
299	definition_property	readonly_sources	writePolicy	$defs.writePolicy.properties.readonly_sources	array<string>	false		medium	未レビュー	未確認	未承認	
300	definition_property	primaryPath	writePolicy	$defs.writePolicy.properties.primaryPath	string	false		medium	未レビュー	未確認	未承認	
301	definition_property	primary_path	writePolicy	$defs.writePolicy.properties.primary_path	string	false		medium	未レビュー	未確認	未承認	
302	definition_property	editableFields	writePolicy	$defs.writePolicy.properties.editableFields	array<string>	false		medium	未レビュー	未確認	未承認	
303	definition_property	editable_fields	writePolicy	$defs.writePolicy.properties.editable_fields	array<string>	false		medium	未レビュー	未確認	未承認	
304	definition	writeBackFieldMap	$defs	$defs.writeBackFieldMap	oneOf: string / object{7 properties}	false		medium	未レビュー	未確認	未承認	
305	definition	virtualDataWriteBack	$defs	$defs.virtualDataWriteBack	object{14 properties}	false	writeBackFieldMap	medium	未レビュー	未確認	未承認	virtualDataで生成された仮想行から、主たる更新対象JSON 1つへ一部フィールドを書き戻すための定義。
306	definition_property	enabled	virtualDataWriteBack	$defs.virtualDataWriteBack.properties.enabled	boolean	false		medium	未レビュー	未確認	未承認	
307	definition_property	source	virtualDataWriteBack	$defs.virtualDataWriteBack.properties.source	string	false		medium	未レビュー	未確認	未承認	
308	definition_property	dataSource	virtualDataWriteBack	$defs.virtualDataWriteBack.properties.dataSource	string	false		medium	未レビュー	未確認	未承認	
309	definition_property	data_source	virtualDataWriteBack	$defs.virtualDataWriteBack.properties.data_source	string	false		medium	未レビュー	未確認	未承認	
310	definition_property	path	virtualDataWriteBack	$defs.virtualDataWriteBack.properties.path	string	false		medium	未レビュー	未確認	未承認	
311	definition_property	dataPath	virtualDataWriteBack	$defs.virtualDataWriteBack.properties.dataPath	string	false		medium	未レビュー	未確認	未承認	
312	definition_property	data_path	virtualDataWriteBack	$defs.virtualDataWriteBack.properties.data_path	string	false		medium	未レビュー	未確認	未承認	
313	definition_property	keyField	virtualDataWriteBack	$defs.virtualDataWriteBack.properties.keyField	string	false		medium	未レビュー	未確認	未承認	
314	definition_property	key_field	virtualDataWriteBack	$defs.virtualDataWriteBack.properties.key_field	string	false		medium	未レビュー	未確認	未承認	
315	definition_property	rowKeyField	virtualDataWriteBack	$defs.virtualDataWriteBack.properties.rowKeyField	string	false		medium	未レビュー	未確認	未承認	
316	definition_property	row_key_field	virtualDataWriteBack	$defs.virtualDataWriteBack.properties.row_key_field	string	false		medium	未レビュー	未確認	未承認	
317	definition_property	fields	virtualDataWriteBack	$defs.virtualDataWriteBack.properties.fields	oneOf: array<ref: writeBackFieldMap> / object<additional:string>	false	writeBackFieldMap	medium	未レビュー	未確認	未承認	書き戻し対象フィールド。同名配列、from/to配列、または {仮想field: 元field} のmap。
318	definition_property	fieldMap	virtualDataWriteBack	$defs.virtualDataWriteBack.properties.fieldMap	object<additional:string>	false		medium	未レビュー	未確認	未承認	
319	definition_property	field_map	virtualDataWriteBack	$defs.virtualDataWriteBack.properties.field_map	object<additional:string>	false		medium	未レビュー	未確認	未承認	
320	definition	optionItem	$defs	$defs.optionItem	oneOf: string / number / boolean / object{8 properties}	false		medium	未レビュー	未確認	未承認	
321	definition	layoutOptions	$defs	$defs.layoutOptions	object{2 properties}	false		medium	未レビュー	未確認	未承認	View/layout options. Runtime currently uses detailDialog: wide for wide detail dialog. String layout header-search-grid-detail is still valid.
322	definition_property	detailDialog	layoutOptions	$defs.layoutOptions.properties.detailDialog	string enum[2]	false		medium	未レビュー	未確認	未承認	
323	definition_property	detail_dialog	layoutOptions	$defs.layoutOptions.properties.detail_dialog	string enum[2]	false		medium	未レビュー	未確認	未承認	
324	definition	executeButtonOptions	$defs	$defs.executeButtonOptions	anyOf: unspecified / unspecified / unspecified	false		medium	未レビュー	未確認	未承認	View-specific primary execute action. Runtime reads action/actionId/action_id as actionId and passes it to ActionRegistry. Do not hard-code Action names in Runtime.
325	definition_property	visible	executeButtonOptions	$defs.executeButtonOptions.properties.visible	boolean	false		medium	未レビュー	未確認	未承認	
326	definition_property	caption	executeButtonOptions	$defs.executeButtonOptions.properties.caption	string	false		medium	未レビュー	未確認	未承認	
327	definition_property	label	executeButtonOptions	$defs.executeButtonOptions.properties.label	string	false		medium	未レビュー	未確認	未承認	
328	definition_property	action	executeButtonOptions	$defs.executeButtonOptions.properties.action	string	false		medium	未レビュー	未確認	未承認	
329	definition_property	actionId	executeButtonOptions	$defs.executeButtonOptions.properties.actionId	string	false		medium	未レビュー	未確認	未承認	
330	definition_property	action_id	executeButtonOptions	$defs.executeButtonOptions.properties.action_id	string	false		medium	未レビュー	未確認	未承認	
331	definition	toolbarButtonOptions	$defs	$defs.toolbarButtonOptions	object{6 properties}	false		medium	未レビュー	未確認	未承認	Reserved for future secondary toolbar buttons. v0.6 runtime only renders executeButton.
332	definition_property	visible	toolbarButtonOptions	$defs.toolbarButtonOptions.properties.visible	boolean	false		medium	未レビュー	未確認	未承認	
333	definition_property	caption	toolbarButtonOptions	$defs.toolbarButtonOptions.properties.caption	string	false		medium	未レビュー	未確認	未承認	
334	definition_property	label	toolbarButtonOptions	$defs.toolbarButtonOptions.properties.label	string	false		medium	未レビュー	未確認	未承認	
335	definition_property	action	toolbarButtonOptions	$defs.toolbarButtonOptions.properties.action	string	false		medium	未レビュー	未確認	未承認	
336	definition_property	actionId	toolbarButtonOptions	$defs.toolbarButtonOptions.properties.actionId	string	false		medium	未レビュー	未確認	未承認	
337	definition_property	action_id	toolbarButtonOptions	$defs.toolbarButtonOptions.properties.action_id	string	false		medium	未レビュー	未確認	未承認	
338	definition	toolbarOptions	$defs	$defs.toolbarOptions	object{3 properties}	false	executeButtonOptions, executeButtonOptions, toolbarButtonOptions	high	未レビュー	未確認	未承認	Toolbar declarations. Current runtime supports toolbar.executeButton / toolbar.execute_button as the primary View action.
339	definition_property	executeButton	toolbarOptions	$defs.toolbarOptions.properties.executeButton	ref: executeButtonOptions	false	executeButtonOptions	medium	未レビュー	未確認	未承認	
340	definition_property	execute_button	toolbarOptions	$defs.toolbarOptions.properties.execute_button	ref: executeButtonOptions	false	executeButtonOptions	medium	未レビュー	未確認	未承認	
341	definition_property	buttons	toolbarOptions	$defs.toolbarOptions.properties.buttons	array<ref: toolbarButtonOptions>	false	toolbarButtonOptions	medium	未レビュー	未確認	未承認	
342	definition	aiPromptOptions	$defs	$defs.aiPromptOptions	object{11 properties}	false		high	未レビュー	未確認	未承認	Markdown export AI copy block. Attach to grid section markdown.aiPrompt.
343	definition_property	enabled	aiPromptOptions	$defs.aiPromptOptions.properties.enabled	boolean	false		medium	未レビュー	未確認	未承認	
344	definition_property	title	aiPromptOptions	$defs.aiPromptOptions.properties.title	string	false		medium	未レビュー	未確認	未承認	
345	definition_property	targetFile	aiPromptOptions	$defs.aiPromptOptions.properties.targetFile	string	false		medium	未レビュー	未確認	未承認	
346	definition_property	target_file	aiPromptOptions	$defs.aiPromptOptions.properties.target_file	string	false		medium	未レビュー	未確認	未承認	
347	definition_property	rowSource	aiPromptOptions	$defs.aiPromptOptions.properties.rowSource	string enum[4]	false		medium	未レビュー	未確認	未承認	
348	definition_property	row_source	aiPromptOptions	$defs.aiPromptOptions.properties.row_source	string enum[4]	false		medium	未レビュー	未確認	未承認	
349	definition_property	visibleOnly	aiPromptOptions	$defs.aiPromptOptions.properties.visibleOnly	boolean	false		medium	未レビュー	未確認	未承認	
350	definition_property	visible_only	aiPromptOptions	$defs.aiPromptOptions.properties.visible_only	boolean	false		medium	未レビュー	未確認	未承認	
351	definition_property	includeGridJson	aiPromptOptions	$defs.aiPromptOptions.properties.includeGridJson	boolean	false		medium	未レビュー	未確認	未承認	
352	definition_property	include_grid_json	aiPromptOptions	$defs.aiPromptOptions.properties.include_grid_json	boolean	false		medium	未レビュー	未確認	未承認	
353	definition_property	template	aiPromptOptions	$defs.aiPromptOptions.properties.template	oneOf: string / array<string>	false		medium	未レビュー	未確認	未承認	
354	definition	markdownInlineOptions	$defs	$defs.markdownInlineOptions	object{6 properties}	false		high	未レビュー	未確認	未承認	chat/textarea内のMarkdownリンク・画像記法の表示許可。保存値はMarkdown原文のまま保持する。
355	definition_property	enabled	markdownInlineOptions	$defs.markdownInlineOptions.properties.enabled	boolean	false		medium	未レビュー	未確認	未承認	
356	definition_property	inline	markdownInlineOptions	$defs.markdownInlineOptions.properties.inline	oneOf: boolean / object<additional:any>	false		medium	未レビュー	未確認	未承認	
357	definition_property	allowLinks	markdownInlineOptions	$defs.markdownInlineOptions.properties.allowLinks	boolean	false		medium	未レビュー	未確認	未承認	
358	definition_property	allow_links	markdownInlineOptions	$defs.markdownInlineOptions.properties.allow_links	boolean	false		medium	未レビュー	未確認	未承認	
359	definition_property	allowImages	markdownInlineOptions	$defs.markdownInlineOptions.properties.allowImages	boolean	false		medium	未レビュー	未確認	未承認	
360	definition_property	allow_images	markdownInlineOptions	$defs.markdownInlineOptions.properties.allow_images	boolean	false		medium	未レビュー	未確認	未承認	
```

</details>

<details>
<summary>Grid JSON を表示</summary>

```json
{
  "view_def": "rules/frb_view_def_schema_review_view_def_v0_1.json",
  "data_file": "frb_view_def_schema_review_data_v0_1.json",
  "section": "Schema項目一覧",
  "row_count": 360,
  "columns": [
    {
      "field": "no",
      "caption": "No.",
      "type": "number"
    },
    {
      "field": "item_type",
      "caption": "種別",
      "type": "select"
    },
    {
      "field": "name",
      "caption": "名前",
      "type": "text"
    },
    {
      "field": "parent_key",
      "caption": "親",
      "type": "text"
    },
    {
      "field": "schema_path",
      "caption": "Schema Path",
      "type": "text"
    },
    {
      "field": "type_summary",
      "caption": "型概要",
      "type": "text"
    },
    {
      "field": "required",
      "caption": "必須",
      "type": "boolean"
    },
    {
      "field": "ref",
      "caption": "参照",
      "type": "text"
    },
    {
      "field": "priority",
      "caption": "優先度",
      "type": "select"
    },
    {
      "field": "review_status",
      "caption": "レビュー状態",
      "type": "select"
    },
    {
      "field": "verification_status",
      "caption": "確認状態",
      "type": "select"
    },
    {
      "field": "approval_decision",
      "caption": "承認",
      "type": "select"
    },
    {
      "field": "description",
      "caption": "説明",
      "type": "textarea"
    }
  ],
  "rows": [
    {
      "no": 1,
      "item_type": "root_property",
      "name": "app",
      "parent_key": "",
      "schema_path": "properties.app",
      "type_summary": "object{2 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 2,
      "item_type": "root_property",
      "name": "views",
      "parent_key": "",
      "schema_path": "properties.views",
      "type_summary": "array<ref: view>",
      "required": true,
      "ref": "view",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 3,
      "item_type": "root_property",
      "name": "extends",
      "parent_key": "",
      "schema_path": "properties.extends",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "ViewDef inheritance. String or array of parent view_def JSON file names."
    },
    {
      "no": 4,
      "item_type": "root_property",
      "name": "viewDefReport",
      "parent_key": "",
      "schema_path": "properties.viewDefReport",
      "type_summary": "ref: viewDefReportOptions",
      "required": false,
      "ref": "viewDefReportOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 5,
      "item_type": "root_property",
      "name": "dataSources",
      "parent_key": "",
      "schema_path": "properties.dataSources",
      "type_summary": "ref: dataSources",
      "required": false,
      "ref": "dataSources",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 6,
      "item_type": "root_property",
      "name": "data_sources",
      "parent_key": "",
      "schema_path": "properties.data_sources",
      "type_summary": "ref: dataSources",
      "required": false,
      "ref": "dataSources",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 7,
      "item_type": "root_property",
      "name": "virtualData",
      "parent_key": "",
      "schema_path": "properties.virtualData",
      "type_summary": "ref: virtualData",
      "required": false,
      "ref": "virtualData",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 8,
      "item_type": "root_property",
      "name": "virtual_data",
      "parent_key": "",
      "schema_path": "properties.virtual_data",
      "type_summary": "ref: virtualData",
      "required": false,
      "ref": "virtualData",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 9,
      "item_type": "root_property",
      "name": "writePolicy",
      "parent_key": "",
      "schema_path": "properties.writePolicy",
      "type_summary": "ref: writePolicy",
      "required": false,
      "ref": "writePolicy",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 10,
      "item_type": "root_property",
      "name": "write_policy",
      "parent_key": "",
      "schema_path": "properties.write_policy",
      "type_summary": "ref: writePolicy",
      "required": false,
      "ref": "writePolicy",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 11,
      "item_type": "root_property",
      "name": "fieldTypeSources",
      "parent_key": "",
      "schema_path": "properties.fieldTypeSources",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 12,
      "item_type": "root_property",
      "name": "field_type_sources",
      "parent_key": "",
      "schema_path": "properties.field_type_sources",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 13,
      "item_type": "root_property",
      "name": "typeSources",
      "parent_key": "",
      "schema_path": "properties.typeSources",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 14,
      "item_type": "root_property",
      "name": "type_sources",
      "parent_key": "",
      "schema_path": "properties.type_sources",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 15,
      "item_type": "root_property",
      "name": "commonTypeRegistry",
      "parent_key": "",
      "schema_path": "properties.commonTypeRegistry",
      "type_summary": "object<additional:any>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 16,
      "item_type": "root_property",
      "name": "common_type_registry",
      "parent_key": "",
      "schema_path": "properties.common_type_registry",
      "type_summary": "object<additional:any>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 17,
      "item_type": "root_property",
      "name": "commonTypes",
      "parent_key": "",
      "schema_path": "properties.commonTypes",
      "type_summary": "object<additional:any>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 18,
      "item_type": "root_property",
      "name": "common_types",
      "parent_key": "",
      "schema_path": "properties.common_types",
      "type_summary": "object<additional:any>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 19,
      "item_type": "root_property",
      "name": "toolbar",
      "parent_key": "",
      "schema_path": "properties.toolbar",
      "type_summary": "ref: toolbarOptions",
      "required": false,
      "ref": "toolbarOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 20,
      "item_type": "definition",
      "name": "view",
      "parent_key": "$defs",
      "schema_path": "$defs.view",
      "type_summary": "object{21 properties}",
      "required": false,
      "ref": "layoutOptions, section, markdownOptions, viewDefReportOptions, dataSources, dataSources, virtualData, virtualData, writePolicy, writePolicy, toolbarOptions",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 21,
      "item_type": "definition_property",
      "name": "id",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.id",
      "type_summary": "string",
      "required": true,
      "ref": "",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 22,
      "item_type": "definition_property",
      "name": "caption",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.caption",
      "type_summary": "string",
      "required": true,
      "ref": "",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 23,
      "item_type": "definition_property",
      "name": "layout",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.layout",
      "type_summary": "oneOf: string enum[1] / ref: layoutOptions",
      "required": true,
      "ref": "layoutOptions",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 24,
      "item_type": "definition_property",
      "name": "sections",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.sections",
      "type_summary": "array<ref: section>",
      "required": true,
      "ref": "section",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 25,
      "item_type": "definition_property",
      "name": "markdown",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.markdown",
      "type_summary": "ref: markdownOptions",
      "required": false,
      "ref": "markdownOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 26,
      "item_type": "definition_property",
      "name": "viewDefReport",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.viewDefReport",
      "type_summary": "ref: viewDefReportOptions",
      "required": false,
      "ref": "viewDefReportOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 27,
      "item_type": "definition_property",
      "name": "dataSources",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.dataSources",
      "type_summary": "ref: dataSources",
      "required": false,
      "ref": "dataSources",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 28,
      "item_type": "definition_property",
      "name": "data_sources",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.data_sources",
      "type_summary": "ref: dataSources",
      "required": false,
      "ref": "dataSources",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 29,
      "item_type": "definition_property",
      "name": "virtualData",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.virtualData",
      "type_summary": "ref: virtualData",
      "required": false,
      "ref": "virtualData",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 30,
      "item_type": "definition_property",
      "name": "virtual_data",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.virtual_data",
      "type_summary": "ref: virtualData",
      "required": false,
      "ref": "virtualData",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 31,
      "item_type": "definition_property",
      "name": "writePolicy",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.writePolicy",
      "type_summary": "ref: writePolicy",
      "required": false,
      "ref": "writePolicy",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 32,
      "item_type": "definition_property",
      "name": "write_policy",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.write_policy",
      "type_summary": "ref: writePolicy",
      "required": false,
      "ref": "writePolicy",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 33,
      "item_type": "definition_property",
      "name": "toolbar",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.toolbar",
      "type_summary": "ref: toolbarOptions",
      "required": false,
      "ref": "toolbarOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 34,
      "item_type": "definition_property",
      "name": "fieldTypeSources",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.fieldTypeSources",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 35,
      "item_type": "definition_property",
      "name": "field_type_sources",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.field_type_sources",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 36,
      "item_type": "definition_property",
      "name": "typeSources",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.typeSources",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 37,
      "item_type": "definition_property",
      "name": "type_sources",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.type_sources",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 38,
      "item_type": "definition_property",
      "name": "commonTypeRegistry",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.commonTypeRegistry",
      "type_summary": "object<additional:any>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 39,
      "item_type": "definition_property",
      "name": "common_type_registry",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.common_type_registry",
      "type_summary": "object<additional:any>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 40,
      "item_type": "definition_property",
      "name": "commonTypes",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.commonTypes",
      "type_summary": "object<additional:any>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 41,
      "item_type": "definition_property",
      "name": "common_types",
      "parent_key": "view",
      "schema_path": "$defs.view.properties.common_types",
      "type_summary": "object<additional:any>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 42,
      "item_type": "definition",
      "name": "section",
      "parent_key": "$defs",
      "schema_path": "$defs.section",
      "type_summary": "object{8 properties}",
      "required": false,
      "ref": "field, markdownSectionOptions",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 43,
      "item_type": "definition_property",
      "name": "id",
      "parent_key": "section",
      "schema_path": "$defs.section.properties.id",
      "type_summary": "string",
      "required": true,
      "ref": "",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 44,
      "item_type": "definition_property",
      "name": "caption",
      "parent_key": "section",
      "schema_path": "$defs.section.properties.caption",
      "type_summary": "string",
      "required": true,
      "ref": "",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 45,
      "item_type": "definition_property",
      "name": "type",
      "parent_key": "section",
      "schema_path": "$defs.section.properties.type",
      "type_summary": "string enum[2]",
      "required": true,
      "ref": "",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 46,
      "item_type": "definition_property",
      "name": "role",
      "parent_key": "section",
      "schema_path": "$defs.section.properties.role",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 47,
      "item_type": "definition_property",
      "name": "dataPath",
      "parent_key": "section",
      "schema_path": "$defs.section.properties.dataPath",
      "type_summary": "string",
      "required": true,
      "ref": "",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 48,
      "item_type": "definition_property",
      "name": "keyField",
      "parent_key": "section",
      "schema_path": "$defs.section.properties.keyField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 49,
      "item_type": "definition_property",
      "name": "fields",
      "parent_key": "section",
      "schema_path": "$defs.section.properties.fields",
      "type_summary": "array<ref: field>",
      "required": true,
      "ref": "field",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 50,
      "item_type": "definition_property",
      "name": "markdown",
      "parent_key": "section",
      "schema_path": "$defs.section.properties.markdown",
      "type_summary": "ref: markdownSectionOptions",
      "required": false,
      "ref": "markdownSectionOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 51,
      "item_type": "definition",
      "name": "field",
      "parent_key": "$defs",
      "schema_path": "$defs.field",
      "type_summary": "object{26 properties}",
      "required": false,
      "ref": "fieldType, optionItem, gridOptions, editOptions, searchOptions, validationOptions, createOptions",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 52,
      "item_type": "definition_property",
      "name": "field",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.field",
      "type_summary": "string",
      "required": true,
      "ref": "",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 53,
      "item_type": "definition_property",
      "name": "caption",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.caption",
      "type_summary": "string",
      "required": true,
      "ref": "",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 54,
      "item_type": "definition_property",
      "name": "type",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.type",
      "type_summary": "ref: fieldType",
      "required": true,
      "ref": "fieldType",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 55,
      "item_type": "definition_property",
      "name": "readonly",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.readonly",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 56,
      "item_type": "definition_property",
      "name": "options",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.options",
      "type_summary": "array<ref: optionItem>",
      "required": false,
      "ref": "optionItem",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 57,
      "item_type": "definition_property",
      "name": "grid",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.grid",
      "type_summary": "ref: gridOptions",
      "required": false,
      "ref": "gridOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 58,
      "item_type": "definition_property",
      "name": "edit",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.edit",
      "type_summary": "ref: editOptions",
      "required": false,
      "ref": "editOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 59,
      "item_type": "definition_property",
      "name": "search",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.search",
      "type_summary": "ref: searchOptions",
      "required": false,
      "ref": "searchOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 60,
      "item_type": "definition_property",
      "name": "format",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.format",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 61,
      "item_type": "definition_property",
      "name": "defaultValue",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.defaultValue",
      "type_summary": "bool",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 62,
      "item_type": "definition_property",
      "name": "validation",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.validation",
      "type_summary": "ref: validationOptions",
      "required": false,
      "ref": "validationOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 63,
      "item_type": "definition_property",
      "name": "create",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.create",
      "type_summary": "ref: createOptions",
      "required": false,
      "ref": "createOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 64,
      "item_type": "definition_property",
      "name": "layout",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.layout",
      "type_summary": "object{3 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "Detail Dialog内の配置制御。例: {\"placement\":\"detailFooter\"} で子配列表示後に描画する。"
    },
    {
      "no": 65,
      "item_type": "definition_property",
      "name": "control",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.control",
      "type_summary": "string enum[3]",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 66,
      "item_type": "definition_property",
      "name": "fieldType",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.fieldType",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 67,
      "item_type": "definition_property",
      "name": "field_type",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.field_type",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 68,
      "item_type": "definition_property",
      "name": "typeRef",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.typeRef",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 69,
      "item_type": "definition_property",
      "name": "type_ref",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.type_ref",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 70,
      "item_type": "definition_property",
      "name": "valueField",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.valueField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 71,
      "item_type": "definition_property",
      "name": "value_field",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.value_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 72,
      "item_type": "definition_property",
      "name": "optionValueField",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.optionValueField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 73,
      "item_type": "definition_property",
      "name": "option_value_field",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.option_value_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 74,
      "item_type": "definition_property",
      "name": "labelField",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.labelField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 75,
      "item_type": "definition_property",
      "name": "label_field",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.label_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 76,
      "item_type": "definition_property",
      "name": "optionLabelField",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.optionLabelField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 77,
      "item_type": "definition_property",
      "name": "option_label_field",
      "parent_key": "field",
      "schema_path": "$defs.field.properties.option_label_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 78,
      "item_type": "definition",
      "name": "fieldType",
      "parent_key": "$defs",
      "schema_path": "$defs.fieldType",
      "type_summary": "string enum[9]",
      "required": false,
      "ref": "",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 79,
      "item_type": "definition",
      "name": "gridOptions",
      "parent_key": "$defs",
      "schema_path": "$defs.gridOptions",
      "type_summary": "object{3 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 80,
      "item_type": "definition_property",
      "name": "visible",
      "parent_key": "gridOptions",
      "schema_path": "$defs.gridOptions.properties.visible",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 81,
      "item_type": "definition_property",
      "name": "width",
      "parent_key": "gridOptions",
      "schema_path": "$defs.gridOptions.properties.width",
      "type_summary": "number",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 82,
      "item_type": "definition_property",
      "name": "format",
      "parent_key": "gridOptions",
      "schema_path": "$defs.gridOptions.properties.format",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 83,
      "item_type": "definition",
      "name": "editOptions",
      "parent_key": "$defs",
      "schema_path": "$defs.editOptions",
      "type_summary": "object{11 properties}",
      "required": false,
      "ref": "chatEmbeddedField, chatEmbeddedField, markdownInlineOptions, markdownInlineOptions",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 84,
      "item_type": "definition_property",
      "name": "visible",
      "parent_key": "editOptions",
      "schema_path": "$defs.editOptions.properties.visible",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 85,
      "item_type": "definition_property",
      "name": "readonly",
      "parent_key": "editOptions",
      "schema_path": "$defs.editOptions.properties.readonly",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 86,
      "item_type": "definition_property",
      "name": "height",
      "parent_key": "editOptions",
      "schema_path": "$defs.editOptions.properties.height",
      "type_summary": "number",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 87,
      "item_type": "definition_property",
      "name": "step",
      "parent_key": "editOptions",
      "schema_path": "$defs.editOptions.properties.step",
      "type_summary": "string | number",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 88,
      "item_type": "definition_property",
      "name": "min",
      "parent_key": "editOptions",
      "schema_path": "$defs.editOptions.properties.min",
      "type_summary": "string | number",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 89,
      "item_type": "definition_property",
      "name": "max",
      "parent_key": "editOptions",
      "schema_path": "$defs.editOptions.properties.max",
      "type_summary": "string | number",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 90,
      "item_type": "definition_property",
      "name": "format",
      "parent_key": "editOptions",
      "schema_path": "$defs.editOptions.properties.format",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 91,
      "item_type": "definition_property",
      "name": "control",
      "parent_key": "editOptions",
      "schema_path": "$defs.editOptions.properties.control",
      "type_summary": "string enum[3]",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 92,
      "item_type": "definition_property",
      "name": "messages",
      "parent_key": "editOptions",
      "schema_path": "$defs.editOptions.properties.messages",
      "type_summary": "array<object{9 properties}>",
      "required": false,
      "ref": "chatEmbeddedField, chatEmbeddedField, markdownInlineOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "Field type chat用。複数フィールドを会話タイムラインとして表示するためのメッセージ定義。"
    },
    {
      "no": 93,
      "item_type": "definition_property",
      "name": "layout",
      "parent_key": "editOptions",
      "schema_path": "$defs.editOptions.properties.layout",
      "type_summary": "object{3 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "Fieldのedit表示における配置制御。field.layout と同じ意味で利用可能。"
    },
    {
      "no": 94,
      "item_type": "definition_property",
      "name": "input",
      "parent_key": "editOptions",
      "schema_path": "$defs.editOptions.properties.input",
      "type_summary": "object{14 properties}",
      "required": false,
      "ref": "markdownInlineOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "Field type chat用のコメント追加入力バー設定。"
    },
    {
      "no": 95,
      "item_type": "definition",
      "name": "searchOptions",
      "parent_key": "$defs",
      "schema_path": "$defs.searchOptions",
      "type_summary": "object{2 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 96,
      "item_type": "definition_property",
      "name": "visible",
      "parent_key": "searchOptions",
      "schema_path": "$defs.searchOptions.properties.visible",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 97,
      "item_type": "definition_property",
      "name": "operator",
      "parent_key": "searchOptions",
      "schema_path": "$defs.searchOptions.properties.operator",
      "type_summary": "string enum[4]",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 98,
      "item_type": "definition",
      "name": "validationOptions",
      "parent_key": "$defs",
      "schema_path": "$defs.validationOptions",
      "type_summary": "object{1 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 99,
      "item_type": "definition_property",
      "name": "required",
      "parent_key": "validationOptions",
      "schema_path": "$defs.validationOptions.properties.required",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 100,
      "item_type": "definition",
      "name": "createOptions",
      "parent_key": "$defs",
      "schema_path": "$defs.createOptions",
      "type_summary": "object{1 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 101,
      "item_type": "definition_property",
      "name": "include",
      "parent_key": "createOptions",
      "schema_path": "$defs.createOptions.properties.include",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 102,
      "item_type": "definition",
      "name": "markdownOptions",
      "parent_key": "$defs",
      "schema_path": "$defs.markdownOptions",
      "type_summary": "object{8 properties}",
      "required": false,
      "ref": "markdownSectionOptions",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "Data JSON export configuration used by Markdown出力→Viewer. Not used for ViewDef Markdown→Viewer."
    },
    {
      "no": 103,
      "item_type": "definition_property",
      "name": "enabled",
      "parent_key": "markdownOptions",
      "schema_path": "$defs.markdownOptions.properties.enabled",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 104,
      "item_type": "definition_property",
      "name": "type",
      "parent_key": "markdownOptions",
      "schema_path": "$defs.markdownOptions.properties.type",
      "type_summary": "string enum[5]",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "MarkdownExportRegistry key. Current registered values: auto, generic_sections, screen_state_expected, screen_state_diff, screen_state_test_patterns."
    },
    {
      "no": 105,
      "item_type": "definition_property",
      "name": "exportType",
      "parent_key": "markdownOptions",
      "schema_path": "$defs.markdownOptions.properties.exportType",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 106,
      "item_type": "definition_property",
      "name": "title",
      "parent_key": "markdownOptions",
      "schema_path": "$defs.markdownOptions.properties.title",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 107,
      "item_type": "definition_property",
      "name": "fileName",
      "parent_key": "markdownOptions",
      "schema_path": "$defs.markdownOptions.properties.fileName",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 108,
      "item_type": "definition_property",
      "name": "filename",
      "parent_key": "markdownOptions",
      "schema_path": "$defs.markdownOptions.properties.filename",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 109,
      "item_type": "definition_property",
      "name": "defaultFileName",
      "parent_key": "markdownOptions",
      "schema_path": "$defs.markdownOptions.properties.defaultFileName",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 110,
      "item_type": "definition_property",
      "name": "sections",
      "parent_key": "markdownOptions",
      "schema_path": "$defs.markdownOptions.properties.sections",
      "type_summary": "array<ref: markdownSectionOptions>",
      "required": false,
      "ref": "markdownSectionOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 111,
      "item_type": "definition",
      "name": "markdownSectionOptions",
      "parent_key": "$defs",
      "schema_path": "$defs.markdownSectionOptions",
      "type_summary": "object{12 properties}",
      "required": false,
      "ref": "markdownFieldOptions, aiPromptOptions, aiPromptOptions, markdownSectionOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 112,
      "item_type": "definition_property",
      "name": "title",
      "parent_key": "markdownSectionOptions",
      "schema_path": "$defs.markdownSectionOptions.properties.title",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 113,
      "item_type": "definition_property",
      "name": "source",
      "parent_key": "markdownSectionOptions",
      "schema_path": "$defs.markdownSectionOptions.properties.source",
      "type_summary": "string enum[8]",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 114,
      "item_type": "definition_property",
      "name": "dataPath",
      "parent_key": "markdownSectionOptions",
      "schema_path": "$defs.markdownSectionOptions.properties.dataPath",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 115,
      "item_type": "definition_property",
      "name": "arrayField",
      "parent_key": "markdownSectionOptions",
      "schema_path": "$defs.markdownSectionOptions.properties.arrayField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 116,
      "item_type": "definition_property",
      "name": "format",
      "parent_key": "markdownSectionOptions",
      "schema_path": "$defs.markdownSectionOptions.properties.format",
      "type_summary": "string enum[16]",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 117,
      "item_type": "definition_property",
      "name": "fields",
      "parent_key": "markdownSectionOptions",
      "schema_path": "$defs.markdownSectionOptions.properties.fields",
      "type_summary": "array<ref: markdownFieldOptions>",
      "required": false,
      "ref": "markdownFieldOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 118,
      "item_type": "definition_property",
      "name": "visible",
      "parent_key": "markdownSectionOptions",
      "schema_path": "$defs.markdownSectionOptions.properties.visible",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 119,
      "item_type": "definition_property",
      "name": "aiPrompt",
      "parent_key": "markdownSectionOptions",
      "schema_path": "$defs.markdownSectionOptions.properties.aiPrompt",
      "type_summary": "ref: aiPromptOptions",
      "required": false,
      "ref": "aiPromptOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 120,
      "item_type": "definition_property",
      "name": "ai_prompt",
      "parent_key": "markdownSectionOptions",
      "schema_path": "$defs.markdownSectionOptions.properties.ai_prompt",
      "type_summary": "ref: aiPromptOptions",
      "required": false,
      "ref": "aiPromptOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 121,
      "item_type": "definition_property",
      "name": "itemTitle",
      "parent_key": "markdownSectionOptions",
      "schema_path": "$defs.markdownSectionOptions.properties.itemTitle",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 122,
      "item_type": "definition_property",
      "name": "showEmpty",
      "parent_key": "markdownSectionOptions",
      "schema_path": "$defs.markdownSectionOptions.properties.showEmpty",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 123,
      "item_type": "definition_property",
      "name": "sections",
      "parent_key": "markdownSectionOptions",
      "schema_path": "$defs.markdownSectionOptions.properties.sections",
      "type_summary": "array<ref: markdownSectionOptions>",
      "required": false,
      "ref": "markdownSectionOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 124,
      "item_type": "definition",
      "name": "markdownFieldOptions",
      "parent_key": "$defs",
      "schema_path": "$defs.markdownFieldOptions",
      "type_summary": "object{8 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 125,
      "item_type": "definition_property",
      "name": "field",
      "parent_key": "markdownFieldOptions",
      "schema_path": "$defs.markdownFieldOptions.properties.field",
      "type_summary": "string",
      "required": true,
      "ref": "",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 126,
      "item_type": "definition_property",
      "name": "caption",
      "parent_key": "markdownFieldOptions",
      "schema_path": "$defs.markdownFieldOptions.properties.caption",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 127,
      "item_type": "definition_property",
      "name": "format",
      "parent_key": "markdownFieldOptions",
      "schema_path": "$defs.markdownFieldOptions.properties.format",
      "type_summary": "string enum[16]",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 128,
      "item_type": "definition_property",
      "name": "visible",
      "parent_key": "markdownFieldOptions",
      "schema_path": "$defs.markdownFieldOptions.properties.visible",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 129,
      "item_type": "definition_property",
      "name": "empty",
      "parent_key": "markdownFieldOptions",
      "schema_path": "$defs.markdownFieldOptions.properties.empty",
      "type_summary": "string | number | boolean | null",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 130,
      "item_type": "definition_property",
      "name": "markdownFormat",
      "parent_key": "markdownFieldOptions",
      "schema_path": "$defs.markdownFieldOptions.properties.markdownFormat",
      "type_summary": "string enum[16]",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 131,
      "item_type": "definition_property",
      "name": "showEmpty",
      "parent_key": "markdownFieldOptions",
      "schema_path": "$defs.markdownFieldOptions.properties.showEmpty",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 132,
      "item_type": "definition_property",
      "name": "label",
      "parent_key": "markdownFieldOptions",
      "schema_path": "$defs.markdownFieldOptions.properties.label",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 133,
      "item_type": "definition",
      "name": "viewDefReportOptions",
      "parent_key": "$defs",
      "schema_path": "$defs.viewDefReportOptions",
      "type_summary": "object{4 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "Future options for ViewDef Markdown→Viewer report. Separate from markdown.type."
    },
    {
      "no": 134,
      "item_type": "definition_property",
      "name": "enabled",
      "parent_key": "viewDefReportOptions",
      "schema_path": "$defs.viewDefReportOptions.properties.enabled",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 135,
      "item_type": "definition_property",
      "name": "includeInheritanceDiff",
      "parent_key": "viewDefReportOptions",
      "schema_path": "$defs.viewDefReportOptions.properties.includeInheritanceDiff",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 136,
      "item_type": "definition_property",
      "name": "includeResolvedJson",
      "parent_key": "viewDefReportOptions",
      "schema_path": "$defs.viewDefReportOptions.properties.includeResolvedJson",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 137,
      "item_type": "definition_property",
      "name": "includeRawJson",
      "parent_key": "viewDefReportOptions",
      "schema_path": "$defs.viewDefReportOptions.properties.includeRawJson",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 138,
      "item_type": "definition",
      "name": "chatEmbeddedField",
      "parent_key": "$defs",
      "schema_path": "$defs.chatEmbeddedField",
      "type_summary": "object{8 properties}",
      "required": false,
      "ref": "fieldType, optionItem, editOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 139,
      "item_type": "definition_property",
      "name": "field",
      "parent_key": "chatEmbeddedField",
      "schema_path": "$defs.chatEmbeddedField.properties.field",
      "type_summary": "string",
      "required": true,
      "ref": "",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 140,
      "item_type": "definition_property",
      "name": "label",
      "parent_key": "chatEmbeddedField",
      "schema_path": "$defs.chatEmbeddedField.properties.label",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 141,
      "item_type": "definition_property",
      "name": "caption",
      "parent_key": "chatEmbeddedField",
      "schema_path": "$defs.chatEmbeddedField.properties.caption",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 142,
      "item_type": "definition_property",
      "name": "type",
      "parent_key": "chatEmbeddedField",
      "schema_path": "$defs.chatEmbeddedField.properties.type",
      "type_summary": "ref: fieldType",
      "required": false,
      "ref": "fieldType",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 143,
      "item_type": "definition_property",
      "name": "control",
      "parent_key": "chatEmbeddedField",
      "schema_path": "$defs.chatEmbeddedField.properties.control",
      "type_summary": "string enum[3]",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 144,
      "item_type": "definition_property",
      "name": "options",
      "parent_key": "chatEmbeddedField",
      "schema_path": "$defs.chatEmbeddedField.properties.options",
      "type_summary": "array<ref: optionItem>",
      "required": false,
      "ref": "optionItem",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 145,
      "item_type": "definition_property",
      "name": "readonly",
      "parent_key": "chatEmbeddedField",
      "schema_path": "$defs.chatEmbeddedField.properties.readonly",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 146,
      "item_type": "definition_property",
      "name": "edit",
      "parent_key": "chatEmbeddedField",
      "schema_path": "$defs.chatEmbeddedField.properties.edit",
      "type_summary": "ref: editOptions",
      "required": false,
      "ref": "editOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 147,
      "item_type": "definition",
      "name": "dataSourceSpec",
      "parent_key": "$defs",
      "schema_path": "$defs.dataSourceSpec",
      "type_summary": "object{6 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 148,
      "item_type": "definition_property",
      "name": "name",
      "parent_key": "dataSourceSpec",
      "schema_path": "$defs.dataSourceSpec.properties.name",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 149,
      "item_type": "definition_property",
      "name": "file",
      "parent_key": "dataSourceSpec",
      "schema_path": "$defs.dataSourceSpec.properties.file",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 150,
      "item_type": "definition_property",
      "name": "path",
      "parent_key": "dataSourceSpec",
      "schema_path": "$defs.dataSourceSpec.properties.path",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 151,
      "item_type": "definition_property",
      "name": "data",
      "parent_key": "dataSourceSpec",
      "schema_path": "$defs.dataSourceSpec.properties.data",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 152,
      "item_type": "definition_property",
      "name": "source",
      "parent_key": "dataSourceSpec",
      "schema_path": "$defs.dataSourceSpec.properties.source",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 153,
      "item_type": "definition_property",
      "name": "inline",
      "parent_key": "dataSourceSpec",
      "schema_path": "$defs.dataSourceSpec.properties.inline",
      "type_summary": "bool",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 154,
      "item_type": "definition",
      "name": "dataSources",
      "parent_key": "$defs",
      "schema_path": "$defs.dataSources",
      "type_summary": "object<additional:oneOf: string / ref: dataSourceSpec>",
      "required": false,
      "ref": "dataSourceSpec",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 155,
      "item_type": "definition",
      "name": "virtualData",
      "parent_key": "$defs",
      "schema_path": "$defs.virtualData",
      "type_summary": "oneOf: ref: virtualDataConfig / array<ref: virtualDataConfig>",
      "required": false,
      "ref": "virtualDataConfig, virtualDataConfig",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 156,
      "item_type": "definition",
      "name": "virtualDataConfig",
      "parent_key": "$defs",
      "schema_path": "$defs.virtualDataConfig",
      "type_summary": "object{25 properties}",
      "required": false,
      "ref": "relationAxisSource, relationAxisSource, relationAxisSource, relationAxisSource, relationQuery, relationQuery, relationQuery, relationSource, relationSource, relationSource, diffSource, diffViewDefs, diffViewDefs, virtualOutputs, virtualDataWriteBack, virtualDataWriteBack",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 157,
      "item_type": "definition_property",
      "name": "builder",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.builder",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "VirtualDataBuilderRegistry key. Registered examples: relation_axis_cards, relation_diff_cards, relation_diff_check_cards, constraint_trace_cards, test_pattern_trace_cards, expected_check_cross_counts, expected_check_shortage_findings."
    },
    {
      "no": 158,
      "item_type": "definition_property",
      "name": "type",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.type",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 159,
      "item_type": "definition_property",
      "name": "kind",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.kind",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 160,
      "item_type": "definition_property",
      "name": "targetPath",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.targetPath",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 161,
      "item_type": "definition_property",
      "name": "target_path",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.target_path",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 162,
      "item_type": "definition_property",
      "name": "dataPath",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.dataPath",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 163,
      "item_type": "definition_property",
      "name": "data_path",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.data_path",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 164,
      "item_type": "definition_property",
      "name": "axis",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.axis",
      "type_summary": "ref: relationAxisSource",
      "required": false,
      "ref": "relationAxisSource",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 165,
      "item_type": "definition_property",
      "name": "base",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.base",
      "type_summary": "ref: relationAxisSource",
      "required": false,
      "ref": "relationAxisSource",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 166,
      "item_type": "definition_property",
      "name": "linked",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.linked",
      "type_summary": "ref: relationAxisSource",
      "required": false,
      "ref": "relationAxisSource",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 167,
      "item_type": "definition_property",
      "name": "target",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.target",
      "type_summary": "ref: relationAxisSource",
      "required": false,
      "ref": "relationAxisSource",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 168,
      "item_type": "definition_property",
      "name": "relation",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.relation",
      "type_summary": "ref: relationQuery",
      "required": false,
      "ref": "relationQuery",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 169,
      "item_type": "definition_property",
      "name": "relationQuery",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.relationQuery",
      "type_summary": "ref: relationQuery",
      "required": false,
      "ref": "relationQuery",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 170,
      "item_type": "definition_property",
      "name": "relation_query",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.relation_query",
      "type_summary": "ref: relationQuery",
      "required": false,
      "ref": "relationQuery",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 171,
      "item_type": "definition_property",
      "name": "relations",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.relations",
      "type_summary": "ref: relationSource",
      "required": false,
      "ref": "relationSource",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 172,
      "item_type": "definition_property",
      "name": "relationSource",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.relationSource",
      "type_summary": "ref: relationSource",
      "required": false,
      "ref": "relationSource",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 173,
      "item_type": "definition_property",
      "name": "relation_source",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.relation_source",
      "type_summary": "ref: relationSource",
      "required": false,
      "ref": "relationSource",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 174,
      "item_type": "definition_property",
      "name": "diff",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.diff",
      "type_summary": "ref: diffSource",
      "required": false,
      "ref": "diffSource",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 175,
      "item_type": "definition_property",
      "name": "diffViewDefs",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.diffViewDefs",
      "type_summary": "ref: diffViewDefs",
      "required": false,
      "ref": "diffViewDefs",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 176,
      "item_type": "definition_property",
      "name": "diff_view_defs",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.diff_view_defs",
      "type_summary": "ref: diffViewDefs",
      "required": false,
      "ref": "diffViewDefs",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 177,
      "item_type": "definition_property",
      "name": "outputs",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.outputs",
      "type_summary": "ref: virtualOutputs",
      "required": false,
      "ref": "virtualOutputs",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 178,
      "item_type": "definition_property",
      "name": "summaryFields",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.summaryFields",
      "type_summary": "object<additional:any>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 179,
      "item_type": "definition_property",
      "name": "summary_fields",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.summary_fields",
      "type_summary": "object<additional:any>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 180,
      "item_type": "definition_property",
      "name": "writeBack",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.writeBack",
      "type_summary": "ref: virtualDataWriteBack",
      "required": false,
      "ref": "virtualDataWriteBack",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 181,
      "item_type": "definition_property",
      "name": "write_back",
      "parent_key": "virtualDataConfig",
      "schema_path": "$defs.virtualDataConfig.properties.write_back",
      "type_summary": "ref: virtualDataWriteBack",
      "required": false,
      "ref": "virtualDataWriteBack",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 182,
      "item_type": "definition",
      "name": "relationAxisSource",
      "parent_key": "$defs",
      "schema_path": "$defs.relationAxisSource",
      "type_summary": "object{16 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 183,
      "item_type": "definition_property",
      "name": "source",
      "parent_key": "relationAxisSource",
      "schema_path": "$defs.relationAxisSource.properties.source",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 184,
      "item_type": "definition_property",
      "name": "dataSource",
      "parent_key": "relationAxisSource",
      "schema_path": "$defs.relationAxisSource.properties.dataSource",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 185,
      "item_type": "definition_property",
      "name": "data_source",
      "parent_key": "relationAxisSource",
      "schema_path": "$defs.relationAxisSource.properties.data_source",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 186,
      "item_type": "definition_property",
      "name": "adapter",
      "parent_key": "relationAxisSource",
      "schema_path": "$defs.relationAxisSource.properties.adapter",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 187,
      "item_type": "definition_property",
      "name": "kind",
      "parent_key": "relationAxisSource",
      "schema_path": "$defs.relationAxisSource.properties.kind",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 188,
      "item_type": "definition_property",
      "name": "path",
      "parent_key": "relationAxisSource",
      "schema_path": "$defs.relationAxisSource.properties.path",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 189,
      "item_type": "definition_property",
      "name": "dataPath",
      "parent_key": "relationAxisSource",
      "schema_path": "$defs.relationAxisSource.properties.dataPath",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 190,
      "item_type": "definition_property",
      "name": "data_path",
      "parent_key": "relationAxisSource",
      "schema_path": "$defs.relationAxisSource.properties.data_path",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 191,
      "item_type": "definition_property",
      "name": "fallbackPaths",
      "parent_key": "relationAxisSource",
      "schema_path": "$defs.relationAxisSource.properties.fallbackPaths",
      "type_summary": "array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 192,
      "item_type": "definition_property",
      "name": "fallback_paths",
      "parent_key": "relationAxisSource",
      "schema_path": "$defs.relationAxisSource.properties.fallback_paths",
      "type_summary": "array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 193,
      "item_type": "definition_property",
      "name": "nodeType",
      "parent_key": "relationAxisSource",
      "schema_path": "$defs.relationAxisSource.properties.nodeType",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 194,
      "item_type": "definition_property",
      "name": "node_type",
      "parent_key": "relationAxisSource",
      "schema_path": "$defs.relationAxisSource.properties.node_type",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 195,
      "item_type": "definition_property",
      "name": "idField",
      "parent_key": "relationAxisSource",
      "schema_path": "$defs.relationAxisSource.properties.idField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 196,
      "item_type": "definition_property",
      "name": "id_field",
      "parent_key": "relationAxisSource",
      "schema_path": "$defs.relationAxisSource.properties.id_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 197,
      "item_type": "definition_property",
      "name": "titleField",
      "parent_key": "relationAxisSource",
      "schema_path": "$defs.relationAxisSource.properties.titleField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 198,
      "item_type": "definition_property",
      "name": "title_field",
      "parent_key": "relationAxisSource",
      "schema_path": "$defs.relationAxisSource.properties.title_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 199,
      "item_type": "definition",
      "name": "relationSource",
      "parent_key": "$defs",
      "schema_path": "$defs.relationSource",
      "type_summary": "object{6 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 200,
      "item_type": "definition_property",
      "name": "source",
      "parent_key": "relationSource",
      "schema_path": "$defs.relationSource.properties.source",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 201,
      "item_type": "definition_property",
      "name": "dataSource",
      "parent_key": "relationSource",
      "schema_path": "$defs.relationSource.properties.dataSource",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 202,
      "item_type": "definition_property",
      "name": "data_source",
      "parent_key": "relationSource",
      "schema_path": "$defs.relationSource.properties.data_source",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 203,
      "item_type": "definition_property",
      "name": "path",
      "parent_key": "relationSource",
      "schema_path": "$defs.relationSource.properties.path",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 204,
      "item_type": "definition_property",
      "name": "relationsPath",
      "parent_key": "relationSource",
      "schema_path": "$defs.relationSource.properties.relationsPath",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 205,
      "item_type": "definition_property",
      "name": "relations_path",
      "parent_key": "relationSource",
      "schema_path": "$defs.relationSource.properties.relations_path",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 206,
      "item_type": "definition",
      "name": "relationQuery",
      "parent_key": "$defs",
      "schema_path": "$defs.relationQuery",
      "type_summary": "object{31 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 207,
      "item_type": "definition_property",
      "name": "source",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.source",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 208,
      "item_type": "definition_property",
      "name": "dataSource",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.dataSource",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 209,
      "item_type": "definition_property",
      "name": "data_source",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.data_source",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 210,
      "item_type": "definition_property",
      "name": "path",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.path",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 211,
      "item_type": "definition_property",
      "name": "relationsPath",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.relationsPath",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 212,
      "item_type": "definition_property",
      "name": "relations_path",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.relations_path",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 213,
      "item_type": "definition_property",
      "name": "name",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.name",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 214,
      "item_type": "definition_property",
      "name": "relation",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.relation",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 215,
      "item_type": "definition_property",
      "name": "relationName",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.relationName",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 216,
      "item_type": "definition_property",
      "name": "relation_name",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.relation_name",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 217,
      "item_type": "definition_property",
      "name": "direction",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.direction",
      "type_summary": "string enum[2]",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 218,
      "item_type": "definition_property",
      "name": "includeViaCheck",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.includeViaCheck",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 219,
      "item_type": "definition_property",
      "name": "include_via_check",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.include_via_check",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 220,
      "item_type": "definition_property",
      "name": "verifiedByRelation",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.verifiedByRelation",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 221,
      "item_type": "definition_property",
      "name": "verified_by_relation",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.verified_by_relation",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 222,
      "item_type": "definition_property",
      "name": "containsCheckRelation",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.containsCheckRelation",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 223,
      "item_type": "definition_property",
      "name": "contains_check_relation",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.contains_check_relation",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 224,
      "item_type": "definition_property",
      "name": "testNodeType",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.testNodeType",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 225,
      "item_type": "definition_property",
      "name": "test_node_type",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.test_node_type",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 226,
      "item_type": "definition_property",
      "name": "checkType",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.checkType",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 227,
      "item_type": "definition_property",
      "name": "check_type",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.check_type",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 228,
      "item_type": "definition_property",
      "name": "constraintType",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.constraintType",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 229,
      "item_type": "definition_property",
      "name": "constraint_type",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.constraint_type",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 230,
      "item_type": "definition_property",
      "name": "statusFilter",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.statusFilter",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "Evidence relation statuses to include, e.g. [\"approved\"]."
    },
    {
      "no": 231,
      "item_type": "definition_property",
      "name": "status_filter",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.status_filter",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "Evidence relation statuses to include, snake_case alias."
    },
    {
      "no": 232,
      "item_type": "definition_property",
      "name": "structureStatusFilter",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.structureStatusFilter",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "Structure relation statuses to include for contains_check etc, e.g. [\"derived\",\"approved\"]."
    },
    {
      "no": 233,
      "item_type": "definition_property",
      "name": "structure_status_filter",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.structure_status_filter",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "Structure relation statuses to include, snake_case alias."
    },
    {
      "no": 234,
      "item_type": "definition_property",
      "name": "excludeStatus",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.excludeStatus",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "Relation statuses to always exclude, e.g. [\"rejected\"]."
    },
    {
      "no": 235,
      "item_type": "definition_property",
      "name": "exclude_status",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.exclude_status",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "Relation statuses to always exclude, snake_case alias."
    },
    {
      "no": 236,
      "item_type": "definition_property",
      "name": "includeStatus",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.includeStatus",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "Alias for statusFilter."
    },
    {
      "no": 237,
      "item_type": "definition_property",
      "name": "include_status",
      "parent_key": "relationQuery",
      "schema_path": "$defs.relationQuery.properties.include_status",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "Alias for statusFilter, snake_case."
    },
    {
      "no": 238,
      "item_type": "definition",
      "name": "diffSource",
      "parent_key": "$defs",
      "schema_path": "$defs.diffSource",
      "type_summary": "object{10 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 239,
      "item_type": "definition_property",
      "name": "source",
      "parent_key": "diffSource",
      "schema_path": "$defs.diffSource.properties.source",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 240,
      "item_type": "definition_property",
      "name": "dataSource",
      "parent_key": "diffSource",
      "schema_path": "$defs.diffSource.properties.dataSource",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 241,
      "item_type": "definition_property",
      "name": "data_source",
      "parent_key": "diffSource",
      "schema_path": "$defs.diffSource.properties.data_source",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 242,
      "item_type": "definition_property",
      "name": "enabled",
      "parent_key": "diffSource",
      "schema_path": "$defs.diffSource.properties.enabled",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 243,
      "item_type": "definition_property",
      "name": "testNodeType",
      "parent_key": "diffSource",
      "schema_path": "$defs.diffSource.properties.testNodeType",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 244,
      "item_type": "definition_property",
      "name": "test_node_type",
      "parent_key": "diffSource",
      "schema_path": "$defs.diffSource.properties.test_node_type",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 245,
      "item_type": "definition_property",
      "name": "testIdField",
      "parent_key": "diffSource",
      "schema_path": "$defs.diffSource.properties.testIdField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 246,
      "item_type": "definition_property",
      "name": "test_id_field",
      "parent_key": "diffSource",
      "schema_path": "$defs.diffSource.properties.test_id_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 247,
      "item_type": "definition_property",
      "name": "checksPath",
      "parent_key": "diffSource",
      "schema_path": "$defs.diffSource.properties.checksPath",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 248,
      "item_type": "definition_property",
      "name": "checks_path",
      "parent_key": "diffSource",
      "schema_path": "$defs.diffSource.properties.checks_path",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 249,
      "item_type": "definition",
      "name": "diffViewDefRef",
      "parent_key": "$defs",
      "schema_path": "$defs.diffViewDefRef",
      "type_summary": "object{9 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 250,
      "item_type": "definition_property",
      "name": "role",
      "parent_key": "diffViewDefRef",
      "schema_path": "$defs.diffViewDefRef.properties.role",
      "type_summary": "string enum[2]",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 251,
      "item_type": "definition_property",
      "name": "view_def",
      "parent_key": "diffViewDefRef",
      "schema_path": "$defs.diffViewDefRef.properties.view_def",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 252,
      "item_type": "definition_property",
      "name": "name",
      "parent_key": "diffViewDefRef",
      "schema_path": "$defs.diffViewDefRef.properties.name",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 253,
      "item_type": "definition_property",
      "name": "file",
      "parent_key": "diffViewDefRef",
      "schema_path": "$defs.diffViewDefRef.properties.file",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 254,
      "item_type": "definition_property",
      "name": "caption",
      "parent_key": "diffViewDefRef",
      "schema_path": "$defs.diffViewDefRef.properties.caption",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 255,
      "item_type": "definition_property",
      "name": "label",
      "parent_key": "diffViewDefRef",
      "schema_path": "$defs.diffViewDefRef.properties.label",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 256,
      "item_type": "definition_property",
      "name": "extends",
      "parent_key": "diffViewDefRef",
      "schema_path": "$defs.diffViewDefRef.properties.extends",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 257,
      "item_type": "definition_property",
      "name": "note",
      "parent_key": "diffViewDefRef",
      "schema_path": "$defs.diffViewDefRef.properties.note",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 258,
      "item_type": "definition_property",
      "name": "active",
      "parent_key": "diffViewDefRef",
      "schema_path": "$defs.diffViewDefRef.properties.active",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 259,
      "item_type": "definition",
      "name": "diffViewDefs",
      "parent_key": "$defs",
      "schema_path": "$defs.diffViewDefs",
      "type_summary": "object{3 properties}",
      "required": false,
      "ref": "diffViewDefRef, diffViewDefRef, diffViewDefRef",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 260,
      "item_type": "definition_property",
      "name": "base",
      "parent_key": "diffViewDefs",
      "schema_path": "$defs.diffViewDefs.properties.base",
      "type_summary": "ref: diffViewDefRef",
      "required": false,
      "ref": "diffViewDefRef",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 261,
      "item_type": "definition_property",
      "name": "children",
      "parent_key": "diffViewDefs",
      "schema_path": "$defs.diffViewDefs.properties.children",
      "type_summary": "array<ref: diffViewDefRef>",
      "required": false,
      "ref": "diffViewDefRef",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 262,
      "item_type": "definition_property",
      "name": "child",
      "parent_key": "diffViewDefs",
      "schema_path": "$defs.diffViewDefs.properties.child",
      "type_summary": "array<ref: diffViewDefRef>",
      "required": false,
      "ref": "diffViewDefRef",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 263,
      "item_type": "definition",
      "name": "virtualOutputs",
      "parent_key": "$defs",
      "schema_path": "$defs.virtualOutputs",
      "type_summary": "object{26 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 264,
      "item_type": "definition_property",
      "name": "idField",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.idField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 265,
      "item_type": "definition_property",
      "name": "id_field",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.id_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 266,
      "item_type": "definition_property",
      "name": "titleField",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.titleField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 267,
      "item_type": "definition_property",
      "name": "title_field",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.title_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 268,
      "item_type": "definition_property",
      "name": "linkedItemsField",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.linkedItemsField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 269,
      "item_type": "definition_property",
      "name": "linked_items_field",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.linked_items_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 270,
      "item_type": "definition_property",
      "name": "relatedDiffsField",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.relatedDiffsField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 271,
      "item_type": "definition_property",
      "name": "related_diffs_field",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.related_diffs_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 272,
      "item_type": "definition_property",
      "name": "failedChecksField",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.failedChecksField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 273,
      "item_type": "definition_property",
      "name": "failed_checks_field",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.failed_checks_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 274,
      "item_type": "definition_property",
      "name": "evidenceEdgesField",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.evidenceEdgesField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 275,
      "item_type": "definition_property",
      "name": "evidence_edges_field",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.evidence_edges_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 276,
      "item_type": "definition_property",
      "name": "impactedItemsField",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.impactedItemsField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 277,
      "item_type": "definition_property",
      "name": "impacted_items_field",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.impacted_items_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 278,
      "item_type": "definition_property",
      "name": "linkedCountField",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.linkedCountField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 279,
      "item_type": "definition_property",
      "name": "linked_count_field",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.linked_count_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 280,
      "item_type": "definition_property",
      "name": "primaryCountField",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.primaryCountField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 281,
      "item_type": "definition_property",
      "name": "primary_count_field",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.primary_count_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 282,
      "item_type": "definition_property",
      "name": "secondaryCountField",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.secondaryCountField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 283,
      "item_type": "definition_property",
      "name": "secondary_count_field",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.secondary_count_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 284,
      "item_type": "definition_property",
      "name": "requiredCountField",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.requiredCountField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 285,
      "item_type": "definition_property",
      "name": "required_count_field",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.required_count_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 286,
      "item_type": "definition_property",
      "name": "failLinkedCountField",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.failLinkedCountField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 287,
      "item_type": "definition_property",
      "name": "fail_linked_count_field",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.fail_linked_count_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 288,
      "item_type": "definition_property",
      "name": "coverageField",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.coverageField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 289,
      "item_type": "definition_property",
      "name": "coverage_field",
      "parent_key": "virtualOutputs",
      "schema_path": "$defs.virtualOutputs.properties.coverage_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 290,
      "item_type": "definition",
      "name": "writePolicy",
      "parent_key": "$defs",
      "schema_path": "$defs.writePolicy",
      "type_summary": "object{13 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 291,
      "item_type": "definition_property",
      "name": "mode",
      "parent_key": "writePolicy",
      "schema_path": "$defs.writePolicy.properties.mode",
      "type_summary": "string enum[3]",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 292,
      "item_type": "definition_property",
      "name": "primarySource",
      "parent_key": "writePolicy",
      "schema_path": "$defs.writePolicy.properties.primarySource",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 293,
      "item_type": "definition_property",
      "name": "primary_source",
      "parent_key": "writePolicy",
      "schema_path": "$defs.writePolicy.properties.primary_source",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 294,
      "item_type": "definition_property",
      "name": "virtualDataReadonly",
      "parent_key": "writePolicy",
      "schema_path": "$defs.writePolicy.properties.virtualDataReadonly",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 295,
      "item_type": "definition_property",
      "name": "virtual_data_readonly",
      "parent_key": "writePolicy",
      "schema_path": "$defs.writePolicy.properties.virtual_data_readonly",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 296,
      "item_type": "definition_property",
      "name": "editableSources",
      "parent_key": "writePolicy",
      "schema_path": "$defs.writePolicy.properties.editableSources",
      "type_summary": "array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 297,
      "item_type": "definition_property",
      "name": "editable_sources",
      "parent_key": "writePolicy",
      "schema_path": "$defs.writePolicy.properties.editable_sources",
      "type_summary": "array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 298,
      "item_type": "definition_property",
      "name": "readonlySources",
      "parent_key": "writePolicy",
      "schema_path": "$defs.writePolicy.properties.readonlySources",
      "type_summary": "array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 299,
      "item_type": "definition_property",
      "name": "readonly_sources",
      "parent_key": "writePolicy",
      "schema_path": "$defs.writePolicy.properties.readonly_sources",
      "type_summary": "array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 300,
      "item_type": "definition_property",
      "name": "primaryPath",
      "parent_key": "writePolicy",
      "schema_path": "$defs.writePolicy.properties.primaryPath",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 301,
      "item_type": "definition_property",
      "name": "primary_path",
      "parent_key": "writePolicy",
      "schema_path": "$defs.writePolicy.properties.primary_path",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 302,
      "item_type": "definition_property",
      "name": "editableFields",
      "parent_key": "writePolicy",
      "schema_path": "$defs.writePolicy.properties.editableFields",
      "type_summary": "array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 303,
      "item_type": "definition_property",
      "name": "editable_fields",
      "parent_key": "writePolicy",
      "schema_path": "$defs.writePolicy.properties.editable_fields",
      "type_summary": "array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 304,
      "item_type": "definition",
      "name": "writeBackFieldMap",
      "parent_key": "$defs",
      "schema_path": "$defs.writeBackFieldMap",
      "type_summary": "oneOf: string / object{7 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 305,
      "item_type": "definition",
      "name": "virtualDataWriteBack",
      "parent_key": "$defs",
      "schema_path": "$defs.virtualDataWriteBack",
      "type_summary": "object{14 properties}",
      "required": false,
      "ref": "writeBackFieldMap",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "virtualDataで生成された仮想行から、主たる更新対象JSON 1つへ一部フィールドを書き戻すための定義。"
    },
    {
      "no": 306,
      "item_type": "definition_property",
      "name": "enabled",
      "parent_key": "virtualDataWriteBack",
      "schema_path": "$defs.virtualDataWriteBack.properties.enabled",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 307,
      "item_type": "definition_property",
      "name": "source",
      "parent_key": "virtualDataWriteBack",
      "schema_path": "$defs.virtualDataWriteBack.properties.source",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 308,
      "item_type": "definition_property",
      "name": "dataSource",
      "parent_key": "virtualDataWriteBack",
      "schema_path": "$defs.virtualDataWriteBack.properties.dataSource",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 309,
      "item_type": "definition_property",
      "name": "data_source",
      "parent_key": "virtualDataWriteBack",
      "schema_path": "$defs.virtualDataWriteBack.properties.data_source",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 310,
      "item_type": "definition_property",
      "name": "path",
      "parent_key": "virtualDataWriteBack",
      "schema_path": "$defs.virtualDataWriteBack.properties.path",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 311,
      "item_type": "definition_property",
      "name": "dataPath",
      "parent_key": "virtualDataWriteBack",
      "schema_path": "$defs.virtualDataWriteBack.properties.dataPath",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 312,
      "item_type": "definition_property",
      "name": "data_path",
      "parent_key": "virtualDataWriteBack",
      "schema_path": "$defs.virtualDataWriteBack.properties.data_path",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 313,
      "item_type": "definition_property",
      "name": "keyField",
      "parent_key": "virtualDataWriteBack",
      "schema_path": "$defs.virtualDataWriteBack.properties.keyField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 314,
      "item_type": "definition_property",
      "name": "key_field",
      "parent_key": "virtualDataWriteBack",
      "schema_path": "$defs.virtualDataWriteBack.properties.key_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 315,
      "item_type": "definition_property",
      "name": "rowKeyField",
      "parent_key": "virtualDataWriteBack",
      "schema_path": "$defs.virtualDataWriteBack.properties.rowKeyField",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 316,
      "item_type": "definition_property",
      "name": "row_key_field",
      "parent_key": "virtualDataWriteBack",
      "schema_path": "$defs.virtualDataWriteBack.properties.row_key_field",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 317,
      "item_type": "definition_property",
      "name": "fields",
      "parent_key": "virtualDataWriteBack",
      "schema_path": "$defs.virtualDataWriteBack.properties.fields",
      "type_summary": "oneOf: array<ref: writeBackFieldMap> / object<additional:string>",
      "required": false,
      "ref": "writeBackFieldMap",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "書き戻し対象フィールド。同名配列、from/to配列、または {仮想field: 元field} のmap。"
    },
    {
      "no": 318,
      "item_type": "definition_property",
      "name": "fieldMap",
      "parent_key": "virtualDataWriteBack",
      "schema_path": "$defs.virtualDataWriteBack.properties.fieldMap",
      "type_summary": "object<additional:string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 319,
      "item_type": "definition_property",
      "name": "field_map",
      "parent_key": "virtualDataWriteBack",
      "schema_path": "$defs.virtualDataWriteBack.properties.field_map",
      "type_summary": "object<additional:string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 320,
      "item_type": "definition",
      "name": "optionItem",
      "parent_key": "$defs",
      "schema_path": "$defs.optionItem",
      "type_summary": "oneOf: string / number / boolean / object{8 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 321,
      "item_type": "definition",
      "name": "layoutOptions",
      "parent_key": "$defs",
      "schema_path": "$defs.layoutOptions",
      "type_summary": "object{2 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "View/layout options. Runtime currently uses detailDialog: wide for wide detail dialog. String layout header-search-grid-detail is still valid."
    },
    {
      "no": 322,
      "item_type": "definition_property",
      "name": "detailDialog",
      "parent_key": "layoutOptions",
      "schema_path": "$defs.layoutOptions.properties.detailDialog",
      "type_summary": "string enum[2]",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 323,
      "item_type": "definition_property",
      "name": "detail_dialog",
      "parent_key": "layoutOptions",
      "schema_path": "$defs.layoutOptions.properties.detail_dialog",
      "type_summary": "string enum[2]",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 324,
      "item_type": "definition",
      "name": "executeButtonOptions",
      "parent_key": "$defs",
      "schema_path": "$defs.executeButtonOptions",
      "type_summary": "anyOf: unspecified / unspecified / unspecified",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "View-specific primary execute action. Runtime reads action/actionId/action_id as actionId and passes it to ActionRegistry. Do not hard-code Action names in Runtime."
    },
    {
      "no": 325,
      "item_type": "definition_property",
      "name": "visible",
      "parent_key": "executeButtonOptions",
      "schema_path": "$defs.executeButtonOptions.properties.visible",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 326,
      "item_type": "definition_property",
      "name": "caption",
      "parent_key": "executeButtonOptions",
      "schema_path": "$defs.executeButtonOptions.properties.caption",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 327,
      "item_type": "definition_property",
      "name": "label",
      "parent_key": "executeButtonOptions",
      "schema_path": "$defs.executeButtonOptions.properties.label",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 328,
      "item_type": "definition_property",
      "name": "action",
      "parent_key": "executeButtonOptions",
      "schema_path": "$defs.executeButtonOptions.properties.action",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 329,
      "item_type": "definition_property",
      "name": "actionId",
      "parent_key": "executeButtonOptions",
      "schema_path": "$defs.executeButtonOptions.properties.actionId",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 330,
      "item_type": "definition_property",
      "name": "action_id",
      "parent_key": "executeButtonOptions",
      "schema_path": "$defs.executeButtonOptions.properties.action_id",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 331,
      "item_type": "definition",
      "name": "toolbarButtonOptions",
      "parent_key": "$defs",
      "schema_path": "$defs.toolbarButtonOptions",
      "type_summary": "object{6 properties}",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "Reserved for future secondary toolbar buttons. v0.6 runtime only renders executeButton."
    },
    {
      "no": 332,
      "item_type": "definition_property",
      "name": "visible",
      "parent_key": "toolbarButtonOptions",
      "schema_path": "$defs.toolbarButtonOptions.properties.visible",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 333,
      "item_type": "definition_property",
      "name": "caption",
      "parent_key": "toolbarButtonOptions",
      "schema_path": "$defs.toolbarButtonOptions.properties.caption",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 334,
      "item_type": "definition_property",
      "name": "label",
      "parent_key": "toolbarButtonOptions",
      "schema_path": "$defs.toolbarButtonOptions.properties.label",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 335,
      "item_type": "definition_property",
      "name": "action",
      "parent_key": "toolbarButtonOptions",
      "schema_path": "$defs.toolbarButtonOptions.properties.action",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 336,
      "item_type": "definition_property",
      "name": "actionId",
      "parent_key": "toolbarButtonOptions",
      "schema_path": "$defs.toolbarButtonOptions.properties.actionId",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 337,
      "item_type": "definition_property",
      "name": "action_id",
      "parent_key": "toolbarButtonOptions",
      "schema_path": "$defs.toolbarButtonOptions.properties.action_id",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 338,
      "item_type": "definition",
      "name": "toolbarOptions",
      "parent_key": "$defs",
      "schema_path": "$defs.toolbarOptions",
      "type_summary": "object{3 properties}",
      "required": false,
      "ref": "executeButtonOptions, executeButtonOptions, toolbarButtonOptions",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "Toolbar declarations. Current runtime supports toolbar.executeButton / toolbar.execute_button as the primary View action."
    },
    {
      "no": 339,
      "item_type": "definition_property",
      "name": "executeButton",
      "parent_key": "toolbarOptions",
      "schema_path": "$defs.toolbarOptions.properties.executeButton",
      "type_summary": "ref: executeButtonOptions",
      "required": false,
      "ref": "executeButtonOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 340,
      "item_type": "definition_property",
      "name": "execute_button",
      "parent_key": "toolbarOptions",
      "schema_path": "$defs.toolbarOptions.properties.execute_button",
      "type_summary": "ref: executeButtonOptions",
      "required": false,
      "ref": "executeButtonOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 341,
      "item_type": "definition_property",
      "name": "buttons",
      "parent_key": "toolbarOptions",
      "schema_path": "$defs.toolbarOptions.properties.buttons",
      "type_summary": "array<ref: toolbarButtonOptions>",
      "required": false,
      "ref": "toolbarButtonOptions",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 342,
      "item_type": "definition",
      "name": "aiPromptOptions",
      "parent_key": "$defs",
      "schema_path": "$defs.aiPromptOptions",
      "type_summary": "object{11 properties}",
      "required": false,
      "ref": "",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "Markdown export AI copy block. Attach to grid section markdown.aiPrompt."
    },
    {
      "no": 343,
      "item_type": "definition_property",
      "name": "enabled",
      "parent_key": "aiPromptOptions",
      "schema_path": "$defs.aiPromptOptions.properties.enabled",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 344,
      "item_type": "definition_property",
      "name": "title",
      "parent_key": "aiPromptOptions",
      "schema_path": "$defs.aiPromptOptions.properties.title",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 345,
      "item_type": "definition_property",
      "name": "targetFile",
      "parent_key": "aiPromptOptions",
      "schema_path": "$defs.aiPromptOptions.properties.targetFile",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 346,
      "item_type": "definition_property",
      "name": "target_file",
      "parent_key": "aiPromptOptions",
      "schema_path": "$defs.aiPromptOptions.properties.target_file",
      "type_summary": "string",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 347,
      "item_type": "definition_property",
      "name": "rowSource",
      "parent_key": "aiPromptOptions",
      "schema_path": "$defs.aiPromptOptions.properties.rowSource",
      "type_summary": "string enum[4]",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 348,
      "item_type": "definition_property",
      "name": "row_source",
      "parent_key": "aiPromptOptions",
      "schema_path": "$defs.aiPromptOptions.properties.row_source",
      "type_summary": "string enum[4]",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 349,
      "item_type": "definition_property",
      "name": "visibleOnly",
      "parent_key": "aiPromptOptions",
      "schema_path": "$defs.aiPromptOptions.properties.visibleOnly",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 350,
      "item_type": "definition_property",
      "name": "visible_only",
      "parent_key": "aiPromptOptions",
      "schema_path": "$defs.aiPromptOptions.properties.visible_only",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 351,
      "item_type": "definition_property",
      "name": "includeGridJson",
      "parent_key": "aiPromptOptions",
      "schema_path": "$defs.aiPromptOptions.properties.includeGridJson",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 352,
      "item_type": "definition_property",
      "name": "include_grid_json",
      "parent_key": "aiPromptOptions",
      "schema_path": "$defs.aiPromptOptions.properties.include_grid_json",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 353,
      "item_type": "definition_property",
      "name": "template",
      "parent_key": "aiPromptOptions",
      "schema_path": "$defs.aiPromptOptions.properties.template",
      "type_summary": "oneOf: string / array<string>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 354,
      "item_type": "definition",
      "name": "markdownInlineOptions",
      "parent_key": "$defs",
      "schema_path": "$defs.markdownInlineOptions",
      "type_summary": "object{6 properties}",
      "required": false,
      "ref": "",
      "priority": "high",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": "chat/textarea内のMarkdownリンク・画像記法の表示許可。保存値はMarkdown原文のまま保持する。"
    },
    {
      "no": 355,
      "item_type": "definition_property",
      "name": "enabled",
      "parent_key": "markdownInlineOptions",
      "schema_path": "$defs.markdownInlineOptions.properties.enabled",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 356,
      "item_type": "definition_property",
      "name": "inline",
      "parent_key": "markdownInlineOptions",
      "schema_path": "$defs.markdownInlineOptions.properties.inline",
      "type_summary": "oneOf: boolean / object<additional:any>",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 357,
      "item_type": "definition_property",
      "name": "allowLinks",
      "parent_key": "markdownInlineOptions",
      "schema_path": "$defs.markdownInlineOptions.properties.allowLinks",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 358,
      "item_type": "definition_property",
      "name": "allow_links",
      "parent_key": "markdownInlineOptions",
      "schema_path": "$defs.markdownInlineOptions.properties.allow_links",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 359,
      "item_type": "definition_property",
      "name": "allowImages",
      "parent_key": "markdownInlineOptions",
      "schema_path": "$defs.markdownInlineOptions.properties.allowImages",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    },
    {
      "no": 360,
      "item_type": "definition_property",
      "name": "allow_images",
      "parent_key": "markdownInlineOptions",
      "schema_path": "$defs.markdownInlineOptions.properties.allow_images",
      "type_summary": "boolean",
      "required": false,
      "ref": "",
      "priority": "medium",
      "review_status": "未レビュー",
      "verification_status": "未確認",
      "approval_decision": "未承認",
      "description": ""
    }
  ]
}
```

</details>