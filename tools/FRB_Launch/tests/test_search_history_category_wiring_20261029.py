"""Qt UI wiring contracts: runnable on platforms without PySide6."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
TREE = (ROOT / 'src/history_category_tree.py').read_text(encoding='utf-8')


def method_body(name):
    parsed = ast.parse(APP)
    launcher = next(x for x in parsed.body if isinstance(x, ast.ClassDef) and x.name == 'Launcher')
    method = next(x for x in launcher.body if isinstance(x, ast.FunctionDef) and x.name == name)
    return ast.get_source_segment(APP, method)


def test_popup_is_a_tree_with_folder_headers_and_preserved_original_keyword_text():
    assert "self.history_choices = HistoryCategoryTree(self.history_popup)" in APP
    assert "row = QTreeWidgetItem([keyword, '×'])" in APP
    assert "folder.addChild(row)" in method_body('populate_history_popup')
    assert "self.history_categories" not in APP  # no alternate history service
    assert "self.search_categories.sync(self.search_history.keywords)" in method_body('populate_history_popup')


def test_new_category_and_expand_controls_are_in_history_ui_and_search_field():
    for marker in ("self.history_category_action = self.search.addAction(",
                   "self.history_add_button.clicked.connect(self.add_history_category)",
                   "self.history_expand_button.clicked.connect(",
                   "self.history_collapse_button.clicked.connect(",
                   "self.history_choices.itemCollapsed.connect(",
                   "self.history_choices.itemExpanded.connect("):
        assert marker in APP


def test_category_and_entry_drag_use_deferred_custom_move_instead_of_native_cleanup():
    for marker in ('def dropEvent(', 'event.ignore()', 'QTimer.singleShot(0,',
                   'self.structureChanged.emit(*op)', "'category'", "'keyword'"):
        assert marker in TREE
    assert 'self.history_choices.structureChanged.connect(self.history_structure_changed)' in APP
    assert 'self.search_categories.move_keyword(value, destination, index)' in APP
    assert 'self.search_categories.move_category(value, index)' in APP


def test_keyboard_and_wheel_visit_visible_entries_not_only_top_level_categories():
    assert 'visible.extend(folder.child(j) for j in range(folder.childCount()))' in method_body('history_visible_rows')
    assert 'visible = self.history_visible_rows()' in method_body('handle_history_event')
    assert 'visible = self.history_visible_rows()' in method_body('wheel_search_history')
    assert 'self.select_history_keyword()' in method_body('handle_history_event')
    assert 'self.search.setText(keyword)' in method_body('select_history_keyword')


def test_legacy_history_and_config_are_left_untouched():
    assert "SearchHistory(STATE / 'search_history.json')" in APP
    assert "SearchHistoryCategories(" in APP
    assert "STATE / 'search_history_categories.json'" in APP
    assert 'self.search_history.remove(value)' in method_body('change_history_row')
    assert 'self.search_categories.sync(self.search_history.keywords)' in method_body('change_history_row')
