"""Explorer arrow convention: keep real folder sorting but flip only Qt's glyph.

Uses the method from expanded_view.py itself with fake Qt objects, so tests
run on headless Linux without PySide6 or a Windows GUI.
"""
import ast
from pathlib import Path

VIEW = Path(__file__).resolve().parents[1] / 'src' / 'expanded_view.py'


def _live_sort_indicator_method():
    module = ast.parse(VIEW.read_text(encoding='utf-8'))
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef)
               and n.name == 'ExpandedLauncherView')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                  and n.name == '_update_middle_header_sort')
    # Function has no dependency on other view methods or Qt internals.
    scope = {'Qt': type('Qt', (), {'SortOrder': type('SortOrder', (), {
        'AscendingOrder': 'QtAscendingIndicator',
        'DescendingOrder': 'QtDescendingIndicator'})})}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 str(VIEW), 'exec'), scope)
    return scope['_update_middle_header_sort']


class Header:
    def __init__(self):
        self.indicator = None

    def setSortIndicator(self, column, order):
        self.indicator = (column, order)


class View:
    def __init__(self, mode):
        self._middle_sort_mode = mode
        self._header = Header()
        self.middle = type('Middle', (), {'tree': type('Tree', (), {
            'header': lambda unused: self._header})()})()


def test_all_columns_show_explorer_arrows_without_reversing_sort_mode():
    update = _live_sort_indicator_method()
    for mode, column, qt_arrow in (
        ('name', 0, 'QtDescendingIndicator'),
        ('name_desc', 0, 'QtAscendingIndicator'),
        ('date_asc', 1, 'QtDescendingIndicator'),
        ('date_desc', 1, 'QtAscendingIndicator'),
        ('size_asc', 2, 'QtDescendingIndicator'),
        ('size_desc', 2, 'QtAscendingIndicator'),
        ('type_asc', 3, 'QtDescendingIndicator'),
        ('type_desc', 3, 'QtAscendingIndicator'),
    ):
        view = View(mode)
        update(view)
        assert view._header.indicator == (column, qt_arrow), mode
        assert view._middle_sort_mode == mode


def test_sort_order_is_still_managed_by_folder_data_not_qt_header():
    source = VIEW.read_text(encoding='utf-8')
    assert 'self.tree.setSortingEnabled(False)' in source
    assert 'rows = filter_sort_folder_rows(' in source
    assert 'sort_mode_for_header(logical_column, self._middle_sort_mode)' in source
    assert 'self._update_middle_header_sort()' in source
