# Visible Rows MD Button Visibility Guard Report v0.18.6.1

- incident: `studio_work_0110`
- phase: `v0.18.6.1-visible-rows-md-button-visibility-guard`
- date: 2026-07-04
- owner: tamasub
- ai_partner: ChatGPT

---

## 1. 目的

Markdown Export Mode が増えたことで、Grid側の `表示行をMD出力` ボタンの意味が曖昧になった。

このボタンは、現在フィルター表示されている行をレビュー用Markdownとして出力するショートカットであり、`document_rebuild` や `full_dump` の時には用途が一致しない。

そのため、`review_report` 選択時だけ表示し、それ以外のMarkdown Export Modeでは非表示にする。

---

## 2. 対応内容

- `wwwroot/js/actions/action_toolbar.js`
  - `syncViewExecuteButtonVisibilityForMarkdownMode()` を追加。
  - 対象ボタンを `action === "ExportMarkdown"` かつ `caption` に `表示行をMD出力` を含むものだけに限定。
  - `review_report` 以外では対象ボタンに `.hidden` を付与。
  - `Git Diff Run` など他の `toolbar.executeButton` は対象外。

- `wwwroot/js/markdown/data_markdown.js`
  - `updateMarkdownExportModeSelect()` の最後で、Grid側表示行MDボタンの表示状態も同期。

- `wwwroot/myindex.html`
  - 更新JSのキャッシュ回避用クエリを更新。

---

## 3. 表示ルール

| Markdown Export Mode | 表示行をMD出力 |
|---|---|
| 文書Markdown出力 / document_rebuild | 非表示 |
| レビュー用Markdown出力 / review_report | 表示 |
| 全項目Markdown出力 / full_dump | 非表示 |

---

## 4. 事故防止ルール

今回の表示制御は `toolbar.executeButton` 全体へ適用しない。

対象は以下の条件を満たすボタンだけ。

```text
action = ExportMarkdown
caption includes 表示行をMD出力
```

そのため、次のボタンは制御対象外。

```text
Git Diff Run
CSV出力
ViewDef出力
AI Prompt系
その他 executeButton
```

---

## 5. 確認結果

- JS構文確認: OK
- Node VM確認:
  - `document_rebuild` 時に対象ボタンが hidden になること: OK
  - `review_report` 時に対象ボタンが表示されること: OK
  - `Git Diff Run` 相当の別Actionが hidden にならないこと: OK
- ブラウザ実機クリック確認: 未実施
