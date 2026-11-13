# ACTION_EXECUTE_BUTTON_NOTES_v0_6

v0.6-action-execute-button では、ViewDef の `toolbar.executeButton` から主役操作を宣言し、Runtime は Action 名を固定文字列として保持しない。

## 基本形

```json
{
  "toolbar": {
    "executeButton": {
      "visible": true,
      "caption": "Markdown出力",
      "action": "ExportMarkdown"
    }
  }
}
```

## Runtime側の原則

- Runtime は `executeButton.action` を `actionId` として取得する。
- Runtime は `executeStudioAction(actionId, context)` へ変数として渡す。
- `executeStudioAction("PlayMidi", context)` のような固定Action名の直書きは禁止。

## v0.6で登録済みの代表Action

- `LoadData`
- `SaveData`
- `ExportMarkdown`
- `ExportViewDefMarkdown`
- `RefreshServerLists`
- `ShowActionContext`
- `Noop`

## 配置

`toolbar.executeButton` が定義されている場合、Grid右上の操作エリアにView専用の主役ボタンを表示する。
未定義の場合は既存画面に影響しない。
