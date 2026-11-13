"""Files status bar: selected count and total file size (no GUI dependency)."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from files_selection_status import files_selected_summary


def test_multiple_file_selection_uses_raw_bytes_not_rounded_column():
    rows = [
        {'item_kind': 'command', '_middle_size_bytes': 2048, '_middle_size': '2 KB'},
        {'item_kind': 'command', '_middle_size_bytes': 1515, '_middle_size': '2 KB'},
        {'item_kind': 'command', '_middle_size_bytes': 0, '_middle_size': '0 KB'},
    ]
    assert files_selected_summary(rows) == '3 個の項目を選択  3.48 KB'


def test_folders_count_as_selected_but_not_recursively_scanned():
    rows = [
        {'item_kind': 'directory', '_middle_size_bytes': 9999999},
        {'item_kind': 'category'},
        {'item_kind': 'command', '_middle_size_bytes': 2048},
    ]
    assert files_selected_summary(rows) == '3 個の項目を選択  2 KB'
    assert files_selected_summary(rows[:2]) == '2 個の項目を選択'


def test_zero_file_and_unknown_file_size_are_distinct():
    assert files_selected_summary([{'item_kind': 'command', '_middle_size_bytes': 0}]) == '1 個の項目を選択  0 B'
    assert files_selected_summary([{'item_kind': 'command', '_middle_size_bytes': None}]) == '1 個の項目を選択'
    assert files_selected_summary([{'item_kind': 'command', '_middle_size_bytes': 'bad'}]) == '1 個の項目を選択'


def test_empty_selection_and_large_unit_display():
    assert files_selected_summary([]) == ''
    assert files_selected_summary([None]) == ''
    assert files_selected_summary([{'item_kind': 'command', '_middle_size_bytes': 1024 * 1024 * 5}]) == '1 個の項目を選択  5 MB'


def test_view_reacts_to_qt_selection_changes_and_filter_refresh():
    app = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    view = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
    assert 'self.middle.tree.itemSelectionChanged.connect(self._queue_files_selection_status)' in view
    assert 'self.middle.tree.currentItemChanged.connect(self._queue_files_selection_status)' in view
    assert 'QTimer.singleShot(0, self._flush_files_selection_status)' in view
    assert 'update_count(tree.topLevelItemCount())' in view
    assert 'files_selected_summary(rows)' in app
    assert 'view.middle.tree.selectedItems()' in app
    assert 'self.files_item_count.setVisible(bool(visible))' in app
