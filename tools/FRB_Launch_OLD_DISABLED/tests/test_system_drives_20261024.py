"""Pure contracts for drive discovery and stable filesystem browsing rows."""
from pathlib import Path
import ast
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from system_drives import drive_display_name, drive_rows, is_this_pc_shortcut, pc_preview_row

ROOT = Path(__file__).resolve().parents[1]
VIEW = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')


def test_this_pc_detection_by_shell_target_not_title():
    row = {'item_id': 'anything', 'title': '何でも', 'item_kind': 'command',
           'launch_actions': [{'launch_action_type': 'Open', 'launch_target': 'shell:MyComputerFolder'}]}
    assert is_this_pc_shortcut(row)
    updated = pc_preview_row(row)
    assert updated['item_kind'] == 'category'
    assert updated['_system_drives_root'] is True
    assert row['item_kind'] == 'command'  # Never write to authored DataJSON.
    assert pc_preview_row({'title': 'PC', 'item_kind': 'command', 'launch_actions': []}) == {'title': 'PC', 'item_kind': 'command', 'launch_actions': []}


def test_drive_labels_are_explorer_style_and_canonical():
    assert drive_display_name('C:\\', 'Windows') == 'Windows (C:)'
    assert drive_display_name('f:\\', 'Samsung980_Pro') == 'Samsung980_Pro (F:)'
    assert drive_display_name('d:\\', '') == 'ローカル ディスク (D:)'


def test_drive_rows_keep_actual_paths_for_navigation():
    result = drive_rows(roots=['F:\\', 'C:\\'], get_label=lambda root: {'C:\\': 'Windows', 'F:\\': 'SSD'}[root])
    assert [x['title'] for x in result] == ['SSD (F:)', 'Windows (C:)']
    for row in result:
        assert row['item_kind'] == 'directory'
        assert row['_system_drive'] is True
        assert row['item_id'] == row['_file'] == row['launch_browse_target']
        assert row['launch_actions'][0]['launch_target'] == row['_file']
    assert drive_rows(['C:relative', '/not/a/drive'], get_label=lambda _: '') == []


def test_ui_wiring_for_root_refresh_icons_and_navigation():
    ast.parse(VIEW); ast.parse(APP)
    assert 'files_rows = self.browser_rows(left)' in VIEW
    assert 'rows = self.browser_rows(current)' in VIEW
    assert 'matching = next((r for r in self.browser_rows(parent)' in VIEW
    assert 'return drive_rows()' in VIEW
    assert "row.get('_system_drive')" in APP


def test_editor_uses_row_font_and_separator_insets():
    assert 'class _InlineRenameDelegate(QStyledItemDelegate)' in VIEW
    assert 'editor.setFont(option.font)' in VIEW
    assert 'font-size:{pixels if pixels > 0 else 13}px' in VIEW
    assert 'self.separator_inset = 12' in VIEW
    assert 'self.separator_width = 0.65' in VIEW
    assert 'QPointF(inset, y)' in VIEW
