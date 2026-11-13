"""Chrome-like navigation icon checks (static + optional headless Qt pixels)."""

from pathlib import Path
import os
import sys

import pytest

BASE = Path(__file__).resolve().parents[1]
APP = (BASE / 'src' / 'app.py').read_text(encoding='utf-8')
ICON = (BASE / 'src' / 'browser_nav_icons.py').read_text(encoding='utf-8')


def test_buttons_use_painted_icons_not_unicode_text():
    for name in ('back_arrow', 'forward', 'home'):
        assert f"'{name}'" in APP
    assert "self.nav_back_button = QPushButton(self.nav_toolbar)" in APP
    assert 'nav_forward_button' in APP
    assert "self.nav_home_button = QPushButton(self.nav_toolbar)" in APP
    assert 'button.setIconSize(QSize(22, 22))' in APP
    assert 'button.setFocusPolicy(Qt.FocusPolicy.NoFocus)' in APP
    assert 'button.setIcon(browser_navigation_icon(name, theme_family(self.color_theme)))' in APP
    assert 'button.setFixedSize(40, 40)' in APP


def test_browser_icons_have_real_paths_and_disabled_color():
    assert 'QPainterPath()' in ICON
    assert 'painter.drawPath(shape)' in ICON
    assert "elif name == 'home':" in ICON
    assert 'QIcon.Mode.Disabled' in ICON
    assert 'pixmap.setDevicePixelRatio(_ICON_SCALE)' in ICON
    assert 'nav_back_button.clicked.connect(self.navigate_back)' in APP
    assert 'def navigate_forward(self):' in APP
    assert 'nav_home_button.clicked.connect(self.navigate_home)' in APP


def test_icon_rasterization_if_pyside6_available():
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    qt = pytest.importorskip('PySide6.QtWidgets')
    from PySide6.QtCore import QSize
    from PySide6.QtGui import QIcon

    sys.path.insert(0, str(BASE / 'src'))
    from browser_nav_icons import browser_navigation_icon

    application = qt.QApplication.instance() or qt.QApplication([])

    def visible_pixels(name, theme, mode):
        pix = browser_navigation_icon(name, theme).pixmap(QSize(24, 24), mode)
        image = pix.toImage()
        pixels = [(image.pixelColor(x, y).red(), image.pixelColor(x, y).green(),
                   image.pixelColor(x, y).blue(), image.pixelColor(x, y).alpha())
                  for y in range(image.height()) for x in range(image.width())]
        return [p for p in pixels if p[3] > 80]

    for theme in ('light', 'dark'):
        for name in ('back', 'home'):
            enabled = visible_pixels(name, theme, QIcon.Mode.Normal)
            disabled = visible_pixels(name, theme, QIcon.Mode.Disabled)
            assert len(enabled) >= 25, f'{theme}/{name} is blank or too tiny'
            assert len(disabled) >= 25, f'{theme}/{name} disabled icon is blank'
            assert enabled != disabled, f'{theme}/{name} ignores disabled state'

    assert visible_pixels('home', 'light', QIcon.Mode.Normal) != visible_pixels('back', 'light', QIcon.Mode.Normal)
    assert visible_pixels('home', 'light', QIcon.Mode.Normal) != visible_pixels('home', 'dark', QIcon.Mode.Normal)
    assert application is not None
