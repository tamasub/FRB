# Responsibility Refactor First Step Report v0.18.7

- incident: `studio_work_0111`
- phase: `v0.18.7-responsibility-refactor-first-step`
- purpose: テスト可能な責務境界への構造改革ファーストステップ
- date: 2026-07-04

---

## 1. 方針

今回の構造改革は、既存APPを作り直すものではない。

既存のGrid/Editor/Search/Toolbar/Markdown/Overlayの動作を維持したまま、裏側にResponsibilityDef単位でテストしやすい薄いInterfaceを追加する。

特に、会社Copilotくんの成果物である `studio_overlays` は互換維持対象とする。

---

## 2. 追加した責務Interface

| 責務CD | 追加Interface | 役割 |
|---|---|---|
| `grid_column_build` | `GridColumnBuilder.build` | ViewDef fieldsからGrid表示列を返す |
| `search_filter` | `SearchFilter.apply` | rowsとcriteriaから一致行を返す |
| `csv_export` | `CsvExporter.export` | rows/fields/value getterからCSV文字列を生成する |

---

## 3. 既存互換方針

既存の公開っぽい関数名は維持した。

- `tableGridVisibleFields(gd)` は残す
- `applySearch()` は残す
- `gridCsvExportFields(gd)` は残す
- `buildVisibleGridCsv()` は残す
- `exportVisibleGridCsv()` は残す

既存関数の内部から新しい責務Interfaceへ委譲するだけにしている。

そのため、既存OverlayやPluginが従来の関数・DOM・状態に乗っていても、呼び出し口を急に失わない。

---

## 4. studio_overlays保護

`applySearch()` の後段にある `applyStudioPluginSearchFilters(filteredRows, { gd, inputs })` は維持した。

これにより、Core検索のあとにOverlay/Plugin検索条件を重ねる既存構造を壊さない。

今回の責務InterfaceはCore側の検索条件評価を薄く置き換えるが、Overlay/Pluginの後段適用は従来通り残す。

---

## 5. 確認

- JS構文確認: OK
- `tests/responsibilities/responsibility_refactor_first_step_smoke.mjs`: OK
- JSON parse: OK
- ブラウザ実機クリック確認: 未実施

---

## 6. 次フェーズ候補

次に切り出しやすい候補は以下。

1. `editor_field_build`
2. `viewdef_parse`
3. `search_state`

`renderer_display` と `visual_evidence` はDOM/CSS/外部テストランナーを巻き込みやすいため、まだ後回しでよい。
