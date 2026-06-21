# README ViewDef Rules v0.15

## Current set

- Rules: `FRB_VIEW_DEF_GENERATION_RULES_v0_15_action_registry_current.md`
- Schema: `frb_view_def_schema_v0_8_action_registry_toolbar.json`

## What changed from older rules

- Rebuilt the Rules MD as a full current-generation document, not a small patch note.
- Added `toolbar.executeButton` rules for v0.6 ActionRegistry runtime.
- Added Registry-era terms: ActionRegistry, VirtualDataBuilderRegistry, MarkdownExportRegistry, FieldControlRegistry.
- Kept v0.7 relation status filter rules.
- Kept v0.14 Markdown AI Prompt rules.
- Clarified chat, objectArray, detailFooter, common field types, and fixed Data field name policy.
- Added schema v0.8 to document current runtime keys that v0.7 did not explicitly define.

## Recommended use

When asking AI to generate a ViewDef, attach:

1. Target Data JSON
2. `FRB_VIEW_DEF_GENERATION_RULES_v0_15_action_registry_current.md`
3. `frb_view_def_schema_v0_8_action_registry_toolbar.json`
4. A similar existing ViewDef only when helpful

Old rules in `archive/` are history, not the primary source of truth.
