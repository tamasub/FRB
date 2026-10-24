"""Checks for outbound file drag, based on the supplied Oct 24 launcher.

These tests work without Windows/PySide6. Native OS drag must be smoke-tested.
"""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from file_drag_paths import file_path_for_drag


def test_real_file_markers_are_supported(tmp_path):
    demo = tmp_path / 'sample #1 日本語.md'
    demo.write_text('# sample', encoding='utf-8')
    for key in ('_browse_file', '_indexed_file', '_file'):
        row = {'item_kind': 'command', key: str(demo)}
        assert file_path_for_drag(row) == str(demo.resolve())


def test_directory_and_virtual_rows_not_draggable(tmp_path):
    folder = tmp_path / 'folder'
    folder.mkdir()
    path = folder / 'example.txt'
    path.write_text('hello', encoding='utf-8')
    cases = [
        {'item_kind': 'directory', '_file': str(folder)},
        {'item_kind': 'directory', '_file': str(path)},
        {'item_kind': 'command', '_browser_bookmark': True, '_file': str(path)},
        {'item_kind': 'command', '_installed_app': True, '_file': str(path)},
        {'item_kind': 'command', 'title': 'example.txt'},
        {'item_kind': 'command', '_browse_file': str(folder)},
        {'item_kind': 'command', '_browse_file': str(folder / 'gone.txt')},
        {'item_kind': 'command', '_browse_file': '\0hack'},
    ]
    for row in cases:
        assert file_path_for_drag(row) is None


def test_source_contract_and_copy_only():
    file_drag = (ROOT / 'src' / 'file_drag.py').read_text(encoding='utf-8')
    view = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
    reorder = (ROOT / 'src' / 'reorder_widgets.py').read_text(encoding='utf-8')
    app = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
    for source in (file_drag, view, reorder, app):
        ast.parse(source)
    assert 'QUrl.fromLocalFile(path)' in file_drag
    assert '(1).to_bytes(4, \'little\')' in file_drag
    assert 'drag.exec(Qt.DropAction.CopyAction, Qt.DropAction.CopyAction)' in file_drag
    assert 'self.tree = _SeparatedFileTree(self)' in view
    assert 'self.tree.setColumnWidth(1, 40)' in view
    assert 'begin_file_copy_drag(self, row)' in reorder
    assert 'self.begin_order_drag(row)' in reorder
    assert 'tree = ExternalFileDragTree(' in app
    assert 'begin_file_copy_drag(self, row)' in app


def test_divider_covers_both_columns_and_theme():
    view = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
    assert 'class _SeparatedFileTree(ExternalFileDragTree):' in view
    assert 'painter.drawLine(0, y, self.viewport().width() - 1, y)' in view
    assert "'#e1e8e3' if light else '#455851'" in view
    assert 'center_x = option.rect.right() - 20' in view
    assert 'center_x + 2, center_y' in view  # 18 px right gap
