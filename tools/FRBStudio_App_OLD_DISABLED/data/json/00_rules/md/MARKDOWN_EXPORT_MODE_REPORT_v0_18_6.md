# Markdown Export Mode / ExportDef 対応レポート v0.18.6

- incident: `studio_work_0110`
- phase: `v0.18.6-markdown-export-mode-exportdef-rules`
- created_at: 2026-07-04
- owner: tamasub
- ai_partner: ChatGPT

---

## 1. 目的

Markdown出力を単一処理ではなく、用途別のExport Modeとして扱えるようにした。

今回の標準モードは以下の3つ。

| mode | 目的 | field/section `markdown.export=false` の扱い |
|---|---|---|
| `full_dump` | JSON全体確認・AI共有・デバッグ | 無視する |
| `review_report` | 既存のレビュー報告書型Markdown | 尊重する |
| `document_rebuild` / `document_sections` | 読み物型Markdown再構成 | 主制御にしない。指定フィールドだけ使う |

---

## 2. 実装方針

`field.markdown.export=false` はMarkdown出力全体の主制御にはしない。

主制御は `view.markdown.modes[]` に置く。

```json
{
  "markdown": {
    "enabled": true,
    "defaultMode": "document_rebuild",
    "modes": [
      {
        "id": "document_rebuild",
        "caption": "文書Markdown出力",
        "type": "document_sections",
        "fieldPolicy": "explicit_fields",
        "source": "$.rules",
        "headingField": "source_heading",
        "headingLevelField": "source_heading_level",
        "bodyField": "body"
      },
      {
        "id": "review_report",
        "caption": "レビュー用Markdown出力",
        "type": "review_report",
        "fieldPolicy": "respect_markdown_export"
      },
      {
        "id": "full_dump",
        "caption": "全項目Markdown出力",
        "type": "full_dump",
        "fieldPolicy": "all"
      }
    ]
  }
}
```

---

## 3. rawField不採用

`rawField` / `markdown_export_body` に原文Markdown全文を保持して再出力する方式は、今回の推奨から外した。

理由は、Data JSON内に原文全文を持つと、`rules[].body` と `markdown_export_body` のどちらが正本か分からなくなり、同期不整合が発生しやすいため。

今回の推奨は、構造化JSONからMarkdownを再構成する方式。

```text
Data JSON = 構造化された意味の正本
Markdown = Export View
```

---

## 4. 更新ファイル

- `wwwroot/myindex.html`
- `wwwroot/styles.css`
- `wwwroot/app.js`
- `wwwroot/js/runtime/load_runtime.js`
- `wwwroot/js/actions/action_registry.js`
- `wwwroot/js/markdown/data_markdown.js`
- `defs/rules/rule_review_common_view_def_v0_3.json`
- `data/json/00_rules/frb_view_def_schema_v0_9.json`
- `data/json/00_rules/frb_viewdef_generation_rules_data_v0_1.json`
- `data/json/00_rules/md/MARKDOWN_EXPORT_MODE_REPORT_v0_18_6.md`
- `data/json/01_main/studio_work_incident_data_v0_120_markdown_export_mode_rules_added.json`

---

## 5. 確認結果

- JSON parse: OK
- JSON Schema self check: OK
- `rule_review_common_view_def_v0_3.json` schema validation: OK
- JS syntax check: OK
- Node VMによるMarkdown生成確認: OK
  - `document_rebuild`: review metaを出さず、title/preamble/章見出し/bodyから再構成
  - `full_dump`: `markdown.export=false` を無視し、JSON全体を出力
  - `review_report`: `markdown.export=false` を尊重し、raw系項目を除外

---
