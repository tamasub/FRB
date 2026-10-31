"""v58: unified toolbar, Settings mode switch, upper-edge resize, one bookmark seam.

PySide6-independent wiring and geometry contracts. Windows GUI remains manual.
"""
from pathlib import Path
from types import SimpleNamespace
import ast

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT/'src/app.py').read_text(encoding='utf-8')
EXP = (ROOT/'src/expanded_view.py').read_text(encoding='utf-8')


def method(name):
    cls = next(node for node in ast.parse(APP).body if isinstance(node, ast.ClassDef)
               and node.name == 'Launcher')
    item = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    mod = ast.fix_missing_locations(ast.Module(body=[item], type_ignores=[]))
    scope = {}
    exec(compile(mod, '<extracted method>', 'exec'), scope)
    return scope[name]


def test_one_row_header_moves_original_navigation_and_page_widgets():
    # No replacement widgets: same signals/keyboard focus and page selection.
    assert 'search_row.insertWidget(search_row.indexOf(self.search), self.nav_toolbar, 0)' in APP
    assert 'search_row.insertWidget(search_row.indexOf(self.theme_button), self.tabs, 0)' in APP
    assert 'self.nav_back_button.clicked.connect(self.navigate_back)' in APP
    assert 'self.nav_forward_button.clicked.connect(self.navigate_forward)' in APP
    assert 'self.nav_home_button.clicked.connect(self.navigate_home)' in APP
    assert 'self.tabs.currentChanged.connect(self.page_changed)' in APP
    assert 'self.mode_bar.hide()' in APP
    assert 'body_layout.addWidget(self.mode_bar)' not in APP
    assert 'mode_row.addWidget(self.nav_toolbar' not in APP
    assert 'mode_row.addWidget(self.tabs' not in APP


def test_settings_mode_menu_reuses_existing_toggle():
    assert "self.compact_mode_action = self.theme_menu.addAction('Compact表示へ切り替え')" in APP
    assert 'self.compact_mode_action.triggered.connect(self.toggle_expanded_view)' in APP
    assert "'Compact表示へ切り替え' if self.view_mode == 'expanded'" in APP
    assert "else 'Files／Browser表示へ切り替え'" in APP
    assert 'self.settings.setValue(\'view_mode\', mode)' in APP
    assert 'self.mode_button.clicked.connect(self.toggle_expanded_view)' in APP


def test_narrow_compact_page_selector_is_still_available():
    assert 'self.tabs.hide()' in APP
    assert 'self.page_overflow_button.show()' in APP
    assert 'self.tabs.show()' in APP
    assert 'self.page_overflow_button.hide()' in APP
    assert 'self.tabs.tabText(index)' in APP
    assert 'self.tabs.setCurrentIndex(i)' in APP
    assert 'self.brand_widget.setVisible(width >= 650)' in APP


class Point:
    def __init__(self, x, y):
        self._x, self._y = x, y
    def x(self): return self._x
    def y(self): return self._y
    def toPoint(self): return self


class Rect:
    def contains(self, point):
        return 0 <= point.x() < 1000 and 0 <= point.y() < 700


def test_top_left_top_right_and_top_edge_resize_while_header_still_moves():
    m = method('resize_edge')
    win = SimpleNamespace(FRAME_WIDTH=6, rect=lambda: Rect(),
                          width=lambda: 1000, height=lambda: 700,
                          isMaximized=lambda: False)
    assert m(win, Point(400, 0)) == 'top'
    assert m(win, Point(4, 5)) == 'top-left'
    assert m(win, Point(996, 5)) == 'top-right'
    assert m(win, Point(3, 300)) == 'left'
    assert m(win, Point(997, 300)) == 'right'
    assert m(win, Point(3, 697)) == 'bottom-left'
    assert m(win, Point(997, 697)) == 'bottom-right'
    assert m(win, Point(400, 7)) is None
    assert m(win, Point(400, 35)) is None
    win.isMaximized = lambda: True
    assert m(win, Point(400, 0)) is None


def test_browser_bookmark_single_top_seam():
    assert 'self.root_widget.set_underline_end_provider(lambda: None)' in EXP
    assert "None if self._workspace_mode == 'browser'" in EXP
    rule = EXP.split('QFrame#expandedPanel[panelKind="bookmark"]', 1)[1].split('}}', 1)[0]
    assert 'border-top:0' in rule
    assert 'border-radius:0' in rule
    assert 'self.root_widget.refresh_underline()' in EXP
