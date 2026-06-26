# Defs/Data Link Inventory v0.1

Source ZIP: `defs (2).zip`

## Summary

- defs JSON: 43
- data JSON: 40
- data->viewdef references: 36
- data linked defs: 15
- defs only: 28
- missing viewdef references: 0
- parse errors: 0

## Generated files

- `data/json/05_inventory/defs_data_link_inventory_v0_1.json`
- `defs/inventory/defs_data_link_inventory_view_def_v0_1.json`

## Notes

`defs_only` は data JSON の `view_def` / `view_def_candidates` / `viewing_policy.recommended_view_def` から参照されていない defs JSON を示します。削除判断では、`def_kind` と `referenced_by_viewdefs` も確認してください。
