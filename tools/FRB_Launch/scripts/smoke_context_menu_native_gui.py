"""Windows pre-build GUI smoke for FRBContextMenu, no pytest required.

This probes real rendered pixels, not the presence of stylesheet strings.  In
v0272 paintEvent erased QAction foreground: the menu displayed a gray sheet
with only submenu arrows / occasional last-row text.  Fail the build when
both the icon and the COPY label are not visibly present in Exp AND List.

Run: .venv\\Scripts\\python.exe scripts\\smoke_context_menu_native_gui.py
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
if os.name != 'nt' and not os.environ.get('QT_QPA_PLATFORM'):
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QIcon, QPixmap, QColor, QImage
from PySide6.QtWidgets import QApplication

from app import FRBContextMenu
from context_menu_presentation import style_context_menu


class StubLauncher:
    color_theme = 'light'
    _remote_context_wheel = None

    def style_cascade_menu(self, menu):
        style_context_menu(menu, self.color_theme)


def count_pixels(image, rect, predicate, left, right):
    count = 0
    for y in range(max(0, rect.top() + 4), min(image.height(), rect.bottom() - 4)):
        for x in range(max(0, left), min(image.width(), right)):
            if predicate(image.pixelColor(x, y)):
                count += 1
    return count


def verify_menu(app, *, column):
    launcher = StubLauncher()
    menu = FRBContextMenu(launcher=launcher)
    # This is a paint test. Runner start/stop is guaranteed by its own
    # lifecycle tests; do not install a global input hook in this probe.
    menu._activate_grigri_runner = lambda: False
    menu.setMinimumWidth(235)
    menu.setMaximumWidth(245)
    if column == 'Exp':
        folder = menu.addMenu('Filesリスト')
        menu.folder_list_action = folder.menuAction()
        menu.addSeparator()
    nav = menu.addAction('List列へ進む' if column == 'Exp' else 'Exp列へ戻る')
    menu.addSeparator()
    image_icon = QPixmap(16, 16)
    image_icon.fill(QColor('#ff00ff'))
    copy_action = menu.addAction('コピー')
    copy_action.setIcon(QIcon(image_icon))
    menu.addAction('切り取り')
    menu.addSeparator()
    submenu = menu.addMenu('新規作成')
    menu.new_submenu_action = submenu.menuAction()
    style_context_menu(menu, launcher.color_theme)
    menu.popup(QPoint(100, 100))
    app.processEvents()
    menu.setActiveAction(None)
    app.processEvents()
    try:
        row = menu.actionGeometry(copy_action)
        image = menu.grab().toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        if not row.isValid():
            raise AssertionError('コピー: empty action geometry')
        icon_pixels = count_pixels(
            image, row,
            lambda c: c.red() > 205 and c.blue() > 205 and c.green() < 95,
            0, min(90, image.width()),
        )
        # Scan the TEXT lane only, far from the magenta fixture icon.
        label_pixels = count_pixels(
            image, row,
            lambda c: c.alpha() >= 220 and c.red() < 145
            and c.green() < 145 and c.blue() < 145,
            67, min(205, image.width() - 20),
        )
        if icon_pixels < 8 or label_pixels < 8:
            target = ROOT / f'context_menu_smoke_failure_{column.lower()}.png'
            image.save(str(target))
            raise AssertionError(
                f'{column}: missing visual foreground: '
                f'icon={icon_pixels}, label={label_pixels}; screenshot={target}'
            )
        print(f'PASS {column}: visible icon ({icon_pixels} px) and label ({label_pixels} px)')
    finally:
        menu.close()
        app.processEvents()


def main():
    app = QApplication.instance() or QApplication([])
    for column in ('Exp', 'List'):
        verify_menu(app, column=column)
    print('PASS FRBContextMenu native GUI foreground smoke')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('FAIL FRBContextMenu GUI smoke:', exc, file=sys.stderr)
        raise SystemExit(1)
