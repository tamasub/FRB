# FILE_TREE_PICKER_NAME_FIX_NOTES_v0_10_1

## Purpose

Fix a UI issue where the folder/file icons were visible in the JSON/ViewDef tree picker but the folder/file names were not visible.

## Changes

- Changed tree rows from flex layout to grid layout.
- Added explicit `.file-tree-label` styling with visible color/opacity/visibility.
- Added separate label classes for folder and file names.
- Added a small display label fallback in `file_tree_picker.js`.

## Expected result

The picker should show both icons and names:

```text
📁 test_patterns
  📄 screen_state_smoke_001.expected.json
📁 tests_screen_state
  📁 test_results
    📁 diff
      📄 screen_state_smoke_001.diff.json
```
