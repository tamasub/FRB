"""Qt pixel acceptance for the actual Exp/List component, not plain QMenu.

The previous test compared unrelated native QMenu classes and therefore
could pass despite FRBContextMenu rendering a different text/icon lane.
Run on Windows: python -m pytest -q tests/test_context_menu_icon_qt_geometry_20261112.py
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
from context_menu_presentation import style_context_menu


class LauncherStub:
    color_theme = 'light'
    _remote_context_wheel = None

    def style_cascade_menu(self, menu):
        from context_menu_presentation import style_context_menu
        style_context_menu(menu, self.color_theme)


@pytest.fixture(scope='module')
def app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def _render(app, with_folder_entry):
    launcher = LauncherStub()
    menu = FRBContextMenu(launcher=launcher)
    menu.remote_context_root = True
    menu._activate_grigri_runner = lambda: False
    menu.setWindowFlags(QtCore.Qt.WindowType.Tool |
                        QtCore.Qt.WindowType.FramelessWindowHint |
                        QtCore.Qt.WindowType.WindowStaysOnTopHint)
    menu.setMinimumWidth(225)
    menu.setMaximumWidth(225)
    if with_folder_entry:
        folder = menu.addMenu('Filesリスト')
        folder.setIcon(QtGui.QIcon())
        menu.folder_list_action = folder.menuAction()
        menu.addSeparator()
    menu.addAction('List列へ進む' if with_folder_entry else 'Exp列へ戻る')
    menu.addSeparator()
    pix = QtGui.QPixmap(16, 16)
    pix.fill(QtGui.QColor('#ff00ff'))
    copy = menu.addAction('コピー')
    copy.setIcon(QtGui.QIcon(pix))
    menu.addAction('切り取り')
    menu.popup(QtCore.QPoint(70, 70))
    app.processEvents()
    rect = menu.actionGeometry(copy)
    img = menu.grab().toImage().convertToFormat(QtGui.QImage.Format.Format_RGBA8888)
    found = []
    for y in range(rect.top(), min(rect.bottom(), img.height())):
        for x in range(rect.left(), min(rect.right(), img.width())):
            c = img.pixelColor(x, y)
            if c.red() > 210 and c.green() < 80 and c.blue() > 210:
                found.append(x)
    assert found, 'FRBContextMenu failed to render the icon'
    # Require actual native label glyphs to be present (0272 rendered blank rows).
    text_pixels = []
    for y in range(rect.top() + 4, min(rect.bottom() - 3, img.height())):
        for x in range(62, min(img.width() - 22, 190)):
            c = img.pixelColor(x, y)
            if c.alpha() > 220 and max(c.red(), c.green(), c.blue()) < 135:
                text_pixels.append(x)
    assert len(text_pixels) >= 5, 'Windows menu has icon but QAction label is blank'
    result = min(found), max(found), min(text_pixels)
    menu.close()
    app.processEvents()
    return result


def test_exp_and_list_render_both_icon_and_label(app):
    exp = _render(app, True)
    listed = _render(app, False)
    for icon_left, icon_right, text_left in (exp, listed):
        assert icon_right >= icon_left
        assert text_left > icon_right + 5
    # Pixel parity is an independent Windows visual acceptance task.  Do not
    # turn the app gray again trying to force it through an untested painter.
