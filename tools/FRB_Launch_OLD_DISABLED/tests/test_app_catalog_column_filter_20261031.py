"""Local search for installed-app cascades (compact menu + remote Page).

The small data tests run without Qt; the actual popup test runs when PySide6
is installed (Windows development environment).
"""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from core import column_filter_match
from navigation_wrap import move_tree_selection

SOURCE = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
APP = next(node for node in ast.parse(SOURCE).body
           if isinstance(node, ast.ClassDef) and node.name == 'AppCascadeMenu')
CASCADE = next(node for node in ast.parse(SOURCE).body
               if isinstance(node, ast.ClassDef) and node.name == 'CascadeMenu')


def method(cls, name):
    return next(node for node in cls.body
                if isinstance(node, ast.FunctionDef) and node.name == name)


def load_method(cls, name):
    node = method(cls, name)
    module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    ns = {'Qt': SimpleNamespace(ItemDataRole=SimpleNamespace(UserRole=32)),
          'column_filter_match': column_filter_match,
          'move_tree_selection': move_tree_selection}
    exec(compile(module, '<installed-app-column>', 'exec'), ns)
    return ns[name]


class FakeItem:
    def __init__(self, row):
        self.row = row
        self.hidden = False
        self.disabled = False

    def data(self, col, role):
        assert col == 0 and role == 32
        return self.row

    def setHidden(self, value):
        self.hidden = value

    def isHidden(self):
        return self.hidden

    def isDisabled(self):
        return self.disabled


class FakeTree:
    def __init__(self, rows):
        self.items = [FakeItem(row) for row in rows]
        self.current = None

    def topLevelItemCount(self):
        return len(self.items)

    def topLevelItem(self, index):
        return self.items[index]

    def setCurrentItem(self, item):
        self.current = item

    def currentItem(self):
        return self.current

    def scrollToItem(self, item):
        pass


class FakeMenu:
    select_first = load_method(APP, 'select_first')
    _apply_local_filter = load_method(APP, '_apply_local_filter')
    _restore_local_rows = load_method(APP, '_restore_local_rows')
    _move_filtered_selection = load_method(APP, '_move_filtered_selection')

    def __init__(self):
        self.tree = FakeTree([
            dict(title='Excel', description='Microsoft 365'),
            dict(title='Chrome', description='Web browser'),
            dict(title='電卓', description='Windows Calculator'),
        ])
        self.hover_timer = SimpleNamespace(stop=lambda: None)
        self.child = None
        self.filter_count = SimpleNamespace(setText=self.set_count)
        self.count = ''
        self.select_first()

    def set_count(self, text):
        self.count = text


def visible_titles(menu):
    return [item.row['title'] for item in menu.tree.items if not item.hidden]


def test_app_search_matches_visible_name_and_description_only():
    menu = FakeMenu()
    menu._apply_local_filter('EXCEL')
    assert visible_titles(menu) == ['Excel']
    assert menu.tree.currentItem().row['title'] == 'Excel'
    assert menu.count == '1/3'
    menu._apply_local_filter('web browser')
    assert visible_titles(menu) == ['Chrome']
    menu._apply_local_filter('電卓')
    assert visible_titles(menu) == ['電卓']


def test_zero_matches_cannot_leave_hidden_app_selected():
    menu = FakeMenu()
    menu._apply_local_filter('存在しない名前')
    assert visible_titles(menu) == []
    assert menu.count == '0/3'
    assert menu.tree.currentItem() is None
    assert menu._move_filtered_selection(1) is None
    assert menu.tree.currentItem() is None
    menu._restore_local_rows()
    assert visible_titles(menu) == ['Excel', 'Chrome', '電卓']
    assert menu.tree.currentItem().row['title'] == 'Excel'
    assert menu.count == ''


def test_filtered_wheel_and_arrow_navigation_stay_in_matching_rows():
    menu = FakeMenu()
    menu._apply_local_filter('(Excel or Chrome)')
    assert visible_titles(menu) == ['Excel', 'Chrome']
    menu._move_filtered_selection(1)
    assert menu.tree.currentItem().row['title'] == 'Chrome'
    menu._move_filtered_selection(1)
    assert menu.tree.currentItem().row['title'] == 'Excel'


def test_app_popup_installs_shared_local_search_on_all_open_paths():
    popup = ast.get_source_segment(SOURCE, method(CASCADE, 'popup'))
    key = ast.get_source_segment(SOURCE, method(CASCADE, 'keyPressEvent'))
    ime = ast.get_source_segment(SOURCE, method(CASCADE, 'inputMethodEvent'))
    filter_method = ast.get_source_segment(SOURCE, method(APP, '_apply_local_filter'))
    assert 'self._ensure_local_filter()' in popup
    assert 'if not isinstance(self, AppCascadeMenu):' not in popup
    assert 'QApplication.sendEvent(self.filter_edit,' in key
    assert 'QApplication.sendEvent(self.launcher.search,' not in key
    assert 'QApplication.sendEvent(self.filter_edit, event)' in ime
    assert 'self.launcher.focus_search(False)' not in ime
    assert 'item.setHidden(not matches)' in filter_method
    assert 'self.select_first()' in filter_method


def test_native_compact_and_remote_share_app_search_widget():
    PySide6 = pytest.importorskip('PySide6')
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication, QWidget
    import app

    qt = QApplication.instance() or QApplication([])
    launcher = QWidget()
    launcher.pointer_warp_enabled = False
    launcher.row_icon = lambda row: QIcon()
    executed = []
    launcher.run_menu_item = lambda row: executed.append(row)
    launcher.style_cascade_menu = lambda menu: None
    for origin in ('compact', 'remote_page'):
        menu = app.AppCascadeMenu(parent=launcher, launcher=launcher)
        rows = [{'title': 'Excel', 'description': 'Office'},
                {'title': 'Google Chrome', 'description': 'Browser'}]
        menu.populate(rows)
        menu.popup(QPoint(100, 100))
        qt.processEvents()
        try:
            assert menu.filter_edit is not None, origin
            assert menu.filter_edit.isVisible(), origin
            menu.filter_edit.setText('chrome')
            qt.processEvents()
            assert menu.tree.topLevelItem(0).isHidden()
            assert not menu.tree.topLevelItem(1).isHidden()
            assert menu.tree.currentItem().text(0) == 'Google Chrome'
            menu.filter_edit.clear()
            qt.processEvents()
            assert not menu.tree.topLevelItem(0).isHidden()
        finally:
            menu.close()
            menu.deleteLater()
    launcher.deleteLater()
