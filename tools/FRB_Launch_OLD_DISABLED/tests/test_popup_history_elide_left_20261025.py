"""Keep the important tail of a long search query or Windows folder path."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAG = (ROOT / 'src/reorderable_tree.py').read_text(encoding='utf-8')
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
EXPANDED = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')


def test_both_history_popups_use_shared_left_eliding_tree():
    """Qt renders an ellipsis on the left while retaining the path ending."""
    tree = ast.parse(DRAG)
    widget = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                  and n.name == 'ReorderablePopupTree')
    init = next(n for n in widget.body if isinstance(n, ast.FunctionDef)
                and n.name == '__init__')
    methods = [n for n in ast.walk(init) if isinstance(n, ast.Call)]
    assert any(isinstance(m.func, ast.Attribute) and m.func.attr == 'setTextElideMode'
               and ast.unparse(m.args[0]) == 'Qt.TextElideMode.ElideLeft'
               for m in methods)
    assert 'self.history_choices = ReorderablePopupTree(self.history_popup)' in APP
    assert 'self.favorite_choices = ReorderablePopupTree(self.favorite_popup)' in EXPANDED


def test_full_values_are_still_used_for_search_folder_jump_and_reorder():
    assert "row = QTreeWidgetItem([keyword, '×'])" in APP
    assert "row = QTreeWidgetItem([path, '×'])" in EXPANDED
    assert 'value = item.text(0)' in APP
    assert 'path = item.text(0)' in EXPANDED
    assert "self.topLevelItem(i).text(0)" in DRAG
    assert 'row.setToolTip(0, keyword +' in APP
    assert 'row.setToolTip(0, path +' in EXPANDED


def test_all_touched_sources_parse():
    for source in (DRAG, APP, EXPANDED):
        ast.parse(source)
