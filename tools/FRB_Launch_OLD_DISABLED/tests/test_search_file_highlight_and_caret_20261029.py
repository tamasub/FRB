"""Main-search -> Files: highlight the exact file without another navigation.

Pure tests extract the two small methods by AST: PySide6 is Windows-only in
this project, so CI can validate the behavior without loading the GUI.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from context_menu_resolver import resolve_context_target

APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
VIEW = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')


def extract(source, class_name, function_name, extra):
    module = ast.parse(source)
    owner = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    fn = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == function_name)
    namespace = dict(extra)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), '<isolated>', 'exec'), namespace)
    return namespace[function_name]


class Item:
    def __init__(self, path, kind='file'):
        self.row = ({'_browse_file': path, 'item_kind': 'command', 'title': Path(path).name}
                    if kind == 'file' else
                    {'item_kind': 'directory', '_file': path, 'title': Path(path).name})
        self.selected = False

    def setSelected(self, selected):
        self.selected = selected


class Tree:
    def __init__(self, items):
        self.items = items
        self.current = None
        self.scrollToItem = Mock()
        self.setCurrentItem = Mock(side_effect=self.set_current)
        self.clearSelection = Mock(side_effect=self.clear)

    def topLevelItemCount(self):
        return len(self.items)

    def topLevelItem(self, index):
        return self.items[index]

    def set_current(self, item):
        self.current = item

    def clear(self):
        for item in self.items:
            item.selected = False


def view_with_rows(items):
    tree = Tree(items)
    pane = SimpleNamespace(tree=tree)
    view = SimpleNamespace(
        middle=pane, launcher=SimpleNamespace(authored_items=[]),
        row_data=lambda item: item.row,
        focus_panel=Mock(),
    )
    return view, tree


def test_exact_windows_path_highlights_only_hit_and_scrolls_into_view():
    wrong_folder = Item(r'C:\Another\Report.md')
    folder = Item(r'C:\Work\Report.md', kind='directory')
    hit = Item(r'C:\Work\Report.md')
    tree_items = [wrong_folder, folder, hit, Item(r'C:\Work\Notes.md')]
    view, tree = view_with_rows(tree_items)
    fn = extract(VIEW, 'ExpandedLauncherView', 'select_middle_file', {
        'resolve_context_target': resolve_context_target,
        'QAbstractItemView': SimpleNamespace(ScrollHint=SimpleNamespace(PositionAtCenter=object())),
    })

    assert fn(view, r'c:/work/REPORT.MD')
    assert hit.selected
    assert not wrong_folder.selected and not folder.selected
    assert tree.current is hit
    tree.scrollToItem.assert_called_once()
    assert tree.scrollToItem.call_args.args[0] is hit
    view.focus_panel.assert_called_once_with(view.middle)


def test_missing_file_is_not_silently_replaced_with_first_row():
    first = Item(r'C:\Work\first.md')
    view, tree = view_with_rows([first])
    fn = extract(VIEW, 'ExpandedLauncherView', 'select_middle_file', {
        'resolve_context_target': resolve_context_target,
        'QAbstractItemView': SimpleNamespace(ScrollHint=SimpleNamespace(PositionAtCenter=object())),
    })
    assert not fn(view, r'C:\Work\missing.md')
    assert tree.current is None
    tree.clearSelection.assert_not_called()
    view.focus_panel.assert_not_called()


def test_search_caret_is_moved_left_four_pixels_with_glyph_unchanged():
    source = extract(APP, 'Launcher', 'layout_search_inner_controls', {})
    assert source  # compile and parse the changed method
    assert 'self.search.setTextMargins(32, 0, 165 if is_visible else 0, 0)' in APP
    assert 'self.search_glyph.move(11,' in APP
    assert 'self.search_glyph.setFixedSize(32, 32)' in APP


def test_selection_occurs_after_parent_navigation_and_does_not_record_history():
    source = extract(APP, 'Launcher', 'open_search_file_parent_in_launch', {})
    assert source
    portion = APP[APP.index('    def open_search_file_parent_in_launch('):
                  APP.index('    def perform_filesystem_context_action(')]
    assert portion.index('self.expanded_view.go_to_directory(str(parent))') < portion.index('self.expanded_view.select_middle_file(filename)')
    assert 'directory_history.record(' not in portion
    assert 'self.search.clear()' in portion
