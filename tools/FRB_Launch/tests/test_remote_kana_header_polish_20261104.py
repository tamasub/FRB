"""No-Qt source/AST contracts for the 2026-11-04 FRB Remote/Kana UI polish."""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def source(name):
    return (ROOT / name).read_text(encoding='utf-8')


def test_remote_home_reuses_the_main_window_home_path():
    s = source('src/launch_remote.py')
    assert "self.home_button.setIcon(browser_navigation_icon(" in s
    assert "'home', theme_family(launcher.color_theme)" in s
    assert "self.home_button.setIcon(browser_navigation_icon('home', theme_family(theme)))" in s
    assert "self.home_button.setIcon(remote_compact_icon('home'" not in s
    assert "shape.moveTo(9.6, 20)" in source('src/browser_nav_icons.py')


def test_keyboard_has_the_remote_style_title_close_icon_and_drag():
    s = source('experiments/frb_japanese_input/frb_japanese_input.py')
    assert "Qt.WindowType.FramelessWindowHint" in s
    assert "Qt.WidgetAttribute.WA_TranslucentBackground" in s
    assert "class KanaTitleBar(QFrame):" in s
    assert 'handle.startSystemMove()' in s
    assert "QFrame#kanaTitleBar" in s
    assert 'border-radius:5px' in s
    assert "QPushButton#kanaCloseButton" in s
    assert "'FRB かなフリック', title_frame" in s
    assert "self.close_button = self._micro('×', self.hide, 22" in s
    assert "self.header_keyboard_icon.setPixmap(keyboard_title_icon(light).pixmap(20, 20))" in s
    assert "QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), 10, 10" in s
    assert 'QLabel("FRB かな", self)' not in s
    assert 'setPlaceholderText("FRBかな入力' not in s
    assert "self.output = NativeImeLineEdit(self)" in s
    assert "self.send_requested.emit(value)" in s
    assert "self.header_title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)" in s


def test_title_and_component_use_one_name():
    assert "self.window.setWindowTitle('FRB かなフリック')" in source('src/remote_kana_integration.py')
    assert "'FRB かなフリックをRemoteの下へ表示／非表示'" in source('src/launch_remote.py')
    assert "QMessageBox.warning(self, 'FRB かなフリック', str(exc))" in source('src/app.py')


def test_color_stylesheet_fstring_resolves_for_both_themes():
    s = source('experiments/frb_japanese_input/frb_japanese_input.py')
    tree = ast.parse(s)
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'style_for_size')
    fn = {}
    exec(compile(ast.Module(body=[function], type_ignores=[]), '<style_for_size>', 'exec'), fn)
    for theme in ('light', 'dark'):
        css = fn['style_for_size'](20, theme)
        assert 'QFrame#kanaTitleBar {' in css
        assert 'QPushButton#kanaCloseButton {' in css
        assert 'QLabel#kanaTitle {' in css
        assert 'QWidget#frbWindow { background: transparent;' in css
        assert '{font_size}' not in css
        assert '__FRB_COLOR_' not in css
