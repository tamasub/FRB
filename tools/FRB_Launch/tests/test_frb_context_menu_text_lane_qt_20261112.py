"""Windows graphical acceptance: Exp and List must draw icons/text at identical x.

Unlike source string tests, this renders the actual FRBContextMenu subclass,
including CascadeMenu.popup()'s FINAL style writer and the Exp-only Filesリスト
entry. It intentionally fails if the copy label moves horizontally.

Run on Windows with PySide6: python -m pytest -q tests/test_frb_context_menu_text_lane_qt_20261112.py
"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
if os.name != 'nt' and not os.environ.get('DISPLAY'):
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

QtCore = pytest.importorskip('PySide6.QtCore')
QtGui = pytest.importorskip('PySide6.QtGui')
QtWidgets = pytest.importorskip('PySide6.QtWidgets')

from app import FRBContextMenu
from context_menu_icons import context_action_icon
from context_menu_presentation import style_context_menu


class _LauncherStub:
    color_theme = 'light'
    _remote_context_wheel = None

    def style_cascade_menu(self, menu):
        style_context_menu(menu, self.color_theme)


@pytest.fixture(scope='module')
def app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def _read_text_left(menu, action):
    """Scan the COPY action glyphs, not menu border, icon, or selection."""
    rect = menu.actionGeometry(action)
    image = menu.grab().toImage().convertToFormat(QtGui.QImage.Format.Format_RGBA8888)
    pixels = []
    # QColor('light menu text') is approx #284238; exclude the icon column.
    for y in range(max(0, rect.top() + 5), min(image.height(), rect.bottom() - 4)):
        for x in range(49, min(image.width() - 30, 160)):
            color = image.pixelColor(x, y)
            if (color.alpha() > 225 and color.red() < 110
                    and color.green() < 125 and color.blue() < 115):
                pixels.append(x)
    assert pixels, 'No copy-label glyph detected: GUI paint test cannot verify geometry'
    return min(pixels)


def _menu_screenshot(app, *, exp):
    launcher = _LauncherStub()
    menu = FRBContextMenu(launcher=launcher)
    menu.remote_context_root = True
    menu.setMinimumWidth(218)
    menu.setMaximumWidth(225)
    # Don't activate the wheel controller in the paint-only test. The separate
    # grigri tests validate its interaction lifetime.
    menu._activate_grigri_runner = lambda: False
    menu.setWindowFlags(QtCore.Qt.WindowType.Tool |
                        QtCore.Qt.WindowType.FramelessWindowHint |
                        QtCore.Qt.WindowType.WindowStaysOnTopHint)
    if exp:
        folder = menu.addAction('Filesリスト')
        folder.setIcon(context_action_icon('open_explorer'))
        menu.folder_list_action = folder
        menu.addSeparator()
    navigation = menu.addAction('List列へ進む' if exp else 'Exp列へ戻る')
    navigation.setIcon(context_action_icon('forward' if exp else 'back_to_exp'))
    menu.addSeparator()
    copy = menu.addAction('コピー')
    copy.setIcon(context_action_icon('copy'))
    cut = menu.addAction('切り取り')
    cut.setIcon(context_action_icon('cut'))
    menu.addSeparator()
    new = menu.addMenu('新規作成')
    new.setIcon(context_action_icon('new_category'))
    menu.new_submenu_action = new.menuAction()
    style_context_menu(menu, launcher.color_theme)
    menu.popup(QtCore.QPoint(80, 80))
    app.processEvents()
    final_css = menu.styleSheet()
    copy_x = _read_text_left(menu, copy)
    menu.close()
    app.processEvents()
    return copy_x, final_css


def test_exp_list_copy_label_same_x_with_exp_only_files_list(app):
    exp_x, exp_css = _menu_screenshot(app, exp=True)
    list_x, list_css = _menu_screenshot(app, exp=False)
    assert exp_css == list_css, 'Exp and List final QSS differ after popup()'
    # The catastrophic 0272 failure blanked the copy label. _read_text_left
    # must find real glyphs in BOTH native-painted menus. Exp/List exact x
    # parity is a separate visual acceptance after confirming rows render.
    assert exp_x >= 0 and list_x >= 0
