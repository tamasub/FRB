"""For every present/future Files context menu: shared icon canvas/geometry."""
from pathlib import Path
from types import ModuleType, SimpleNamespace as NS
from unittest.mock import Mock
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from context_menu_presentation import (ICON_BOX_PX, GLYPH_PX,
                                      ICON_INSET_PX, style_context_menu)
from launch_appearance import context_menu_spacing_qss


class FakeMenu:
    def __init__(self, actions=()):
        self._actions = list(actions)
        self.qss = ''

    def actions(self):
        return self._actions

    def setStyleSheet(self, qss):
        self.qss = qss


class FakeIcon:
    def __init__(self, null=False):
        self.null = null
        self.requests = []

    def isNull(self):
        return self.null

    def pixmap(self, size):
        self.requests.append(size)
        return NS(isNull=lambda: False)


class FakeAction:
    def __init__(self, icon=None, submenu=None, separator=False):
        self._icon = icon or FakeIcon(null=True)
        self.submenu = submenu
        self.separator = separator
        self.properties = {}

    def isSeparator(self):
        return self.separator

    def property(self, name):
        return self.properties.get(name)

    def setProperty(self, name, value):
        self.properties[name] = value

    def icon(self):
        return self._icon

    def setIcon(self, icon):
        self._icon = icon

    def menu(self):
        return self.submenu


def test_both_qmenu_and_cascade_menu_use_one_presentation_contract(monkeypatch):
    # Both classes implement the same QAction API; Qt.Popup/Qt.Tool must not
    # trigger any separate icon/spacing branch.
    from context_menu_presentation import style_context_menu
    menu_a, menu_b = FakeMenu(), FakeMenu()
    assert style_context_menu(menu_a, 'light') is menu_a
    assert style_context_menu(menu_b, 'light') is menu_b
    assert menu_a.qss == menu_b.qss
    assert 'margin-left:5px; margin-right:5px' in menu_a.qss
    assert 'width:24px; height:24px' in menu_a.qss
    assert 'padding:7px 9px' in menu_a.qss
    dark = FakeMenu()
    style_context_menu(dark, 'dark')
    assert 'margin-left:5px; margin-right:5px' in dark.qss
    assert '#4b5b56' in dark.qss


def test_file_icons_and_frb_icons_get_same_24px_canvas_and_are_not_scaled_twice(monkeypatch):
    # Exercise the painter without depending on PySide6 in the Linux CI image.
    painted = []
    class Pixmap:
        def __init__(self, w, h):
            painted.append(('canvas', w, h))
        def fill(self, color):
            painted.append(('fill', color))
    class Painter:
        def __init__(self, canvas):
            pass
        def drawPixmap(self, x, y, pixmap):
            painted.append(('draw', x, y))
        def end(self):
            pass
    size_requests = []
    class Size:
        def __init__(self, w, h):
            size_requests.append((w, h))
    qtcore = ModuleType('PySide6.QtCore')
    qtcore.QSize = Size
    qtcore.Qt = NS(GlobalColor=NS(transparent='transparent'))
    qtgui = ModuleType('PySide6.QtGui')
    qtgui.QIcon = lambda canvas: FakeIcon()
    qtgui.QPainter = Painter
    qtgui.QPixmap = Pixmap
    monkeypatch.setitem(sys.modules, 'PySide6', ModuleType('PySide6'))
    monkeypatch.setitem(sys.modules, 'PySide6.QtCore', qtcore)
    monkeypatch.setitem(sys.modules, 'PySide6.QtGui', qtgui)
    os_icon = FakeIcon()
    frb_icon = FakeIcon()
    child = FakeMenu([FakeAction(frb_icon)])
    menu = FakeMenu([FakeAction(os_icon), FakeAction(submenu=child)])
    style_context_menu(menu, 'light')
    assert size_requests == [(GLYPH_PX, GLYPH_PX)] * 2
    assert painted.count(('canvas', ICON_BOX_PX, ICON_BOX_PX)) == 2
    assert painted.count(('draw', ICON_INSET_PX, ICON_INSET_PX)) == 2
    style_context_menu(menu, 'dark')
    assert len(size_requests) == 2  # No cumulative pixmap shrink on re-theme.


def test_all_folder_context_entry_paths_reuse_shared_styler():
    app = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
    expanded = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
    presentation = (ROOT / 'src' / 'context_menu_presentation.py').read_text(encoding='utf-8')
    assert app.count('style_context_menu(') == 1, 'all context menus go through the same gateway'
    assert 'def _wire_hybrid_context_menu(self, menu, *, column=None, context=True,' in app
    assert app.count('self._wire_hybrid_context_menu(') >= 6
    assert 'style_context_menu(submenu, self.launcher.color_theme)' in expanded
    assert 'style_context_menu(menu, self.color_theme,' in app
    assert 'setStyleSheet(context_menu_spacing_qss(' not in app
    assert 'menu.setStyleSheet(LIGHT_MENU_QSS + context_menu_spacing_qss(' not in app
    assert 'source = icon.pixmap(QSize(GLYPH_PX, GLYPH_PX))' in presentation


def test_new_local_menu_styles_are_caught_by_build_gate(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'context_gate', ROOT / 'scripts/check_context_menu_contract.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    assert checker.violations(ROOT) == []
    (tmp_path / 'src').mkdir()
    for name in ('app.py', 'expanded_view.py', 'launch_appearance.py',
                 'context_menu_presentation.py'):
        (tmp_path / 'src' / name).write_text(
            (ROOT / 'src' / name).read_text(encoding='utf-8'), encoding='utf-8')
    app = tmp_path / 'src/app.py'
    app.write_text(app.read_text(encoding='utf-8').replace(
        '            style_context_menu(menu, self.color_theme, extra_qss=extra_qss)',
        '            menu.setStyleSheet("QMenu::item { padding:6px 13px; }")'),
        encoding='utf-8')
    assert any('_wire_hybrid_context_menu' in message for message in checker.violations(tmp_path))
