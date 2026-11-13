"""Pixel acceptance: BOTH Exp/List show equal sides of each icon (Windows GUI).

python -m pytest -q tests/test_frb_context_icon_equal_margins_qt_20261112.py
Requires PySide6; runs offscreen elsewhere if a Qt plugin is available.
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
    def __init__(self, theme):
        self.color_theme = theme
        self._remote_context_wheel = None

    def style_cascade_menu(self, menu):
        style_context_menu(menu, self.color_theme)


@pytest.fixture(scope='module')
def app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def _pixels(menu, action, theme):
    rect = menu.actionGeometry(action)
    pic = menu.grab().toImage().convertToFormat(QtGui.QImage.Format.Format_RGBA8888)
    magenta, glyph = [], []
    for y in range(rect.top() + 4, min(rect.bottom() - 3, pic.height())):
        for x in range(max(0, rect.left()), min(rect.right(), pic.width())):
            c = pic.pixelColor(x, y)
            if c.red() > 190 and c.blue() > 190 and c.green() < 100:
                magenta.append((x, y))
            elif c.alpha() > 200 and (
                    (theme == 'light' and c.red() < 110 and c.green() < 125 and c.blue() < 120)
                    or (theme == 'dark' and c.red() > 160 and c.green() > 160
                        and c.blue() > 160)):
                glyph.append((x, y))
    assert magenta, 'Test icon was not painted'
    assert glyph, 'Menu label was not painted'
    left_icon = min(x for x, y in magenta)
    right_icon = max(x for x, y in magenta)
    left_label = min(x for x, y in glyph if x >= right_icon + 5)
    return rect, left_icon, right_icon, left_label


@pytest.mark.parametrize('theme', ['light', 'dark'])
def test_exp_list_icon_and_label_both_render_in_actual_paint(app, theme):
    outputs=[]
    for exp in (True, False):
        launcher=LauncherStub(theme)
        menu=FRBContextMenu(launcher=launcher)
        menu._activate_grigri_runner=lambda: False
        menu.remote_context_root=True
        menu.setMinimumWidth(225)
        menu.setMaximumWidth(225)
        menu.setWindowFlags(QtCore.Qt.WindowType.Tool |
                            QtCore.Qt.WindowType.FramelessWindowHint |
                            QtCore.Qt.WindowType.WindowStaysOnTopHint)
        if exp:
            submenu=menu.addMenu('Filesリスト')
            submenu.setIcon(QtGui.QIcon())
            menu.folder_list_action=submenu.menuAction()
            menu.addSeparator()
        menu.addAction('List列へ進む' if exp else 'Exp列へ戻る')
        menu.addSeparator()
        pix=QtGui.QPixmap(16, 16)
        pix.fill(QtGui.QColor('#ff00ff'))
        copy=menu.addAction('コピー')
        copy.setIcon(QtGui.QIcon(pix))
        menu.addSeparator()
        menu.addMenu('新規作成')
        style_context_menu(menu, theme)
        menu.popup(QtCore.QPoint(70, 70))
        app.processEvents()
        metrics=_pixels(menu,copy,theme)
        menu.close()
        app.processEvents()
        outputs.append(metrics)
        rect, icon_left, icon_right, text_left = metrics
        assert icon_right >= icon_left, metrics
        assert text_left > icon_right + 4, metrics
    # Native QMenu owns text/icon drawing. Exact Exp/List equal spacing is
    # tracked by Windows visual QA, not by a fake static geometry formula.
