# v0.14.2 Incident Prompt Copy Action

## 目的

インシデント管理JSONの選択行から、ChatGPTへ貼り付ける作業依頼プロンプトを自動生成し、クリップボードへコピーする。

## 設計方針

- Action名は `CopyPromptFromTemplate` とする。
- プロンプト本文はJSへ固定実装せず、ViewDefの `toolbar.executeButton.promptTemplate` に置く。
- JS側は、テンプレート変数の展開とクリップボードコピーだけを担当する。
- 選択中行がない場合はコピーしない。
- クリップボードAPIが失敗した場合は、手動コピー用ダイアログを表示する。

## 主なテンプレート変数

```text
{{data.filePath}}
{{data.fileName}}
{{row.phase}}
{{row.work_item_id}}
{{row.title}}
{{viewDef.filePath}}
{{viewDef.fileName}}
```

## 保存契約

生成されたプロンプトはData JSONへ保存しない。
Actionは現在のData/ViewDef/選択行から、その場でプロンプトを生成する。

## 注意

`incident_file` には、Studio管理Data JSONの相対パスとして `data/json/...` 形式を優先して埋め込む。
