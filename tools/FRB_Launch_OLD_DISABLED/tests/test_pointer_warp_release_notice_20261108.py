"""Regression checks for public-release mouse pointer motion opt-in."""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from pointer_warp_policy import (read_pointer_warp_enabled,
                                 should_show_pointer_warp_notice,
                                 NOTICE_DISMISSED_KEY)


class Settings:
    def __init__(self, values=None):
        self.values = values or {}

    def value(self, key, default=None):
        return self.values.get(key, default)

    def setValue(self, key, value):
        self.values[key] = value


def test_new_install_pointer_motion_is_disabled():
    settings = Settings()
    assert not read_pointer_warp_enabled(settings)
    assert should_show_pointer_warp_notice(settings, False)


def test_explicit_legacy_selection_is_preserved():
    assert read_pointer_warp_enabled(Settings({'vdi_no_cursor_warp': False}))
    assert read_pointer_warp_enabled(Settings({'vdi_no_cursor_warp': 'false'}))
    assert not read_pointer_warp_enabled(Settings({'vdi_no_cursor_warp': True}))


def test_notice_only_when_disabled_and_not_suppressed():
    settings = Settings({'vdi_no_cursor_warp': True})
    assert should_show_pointer_warp_notice(settings, False)
    assert not should_show_pointer_warp_notice(settings, True)
    settings.setValue(NOTICE_DISMISSED_KEY, True)
    assert not should_show_pointer_warp_notice(settings, False)
    assert not should_show_pointer_warp_notice(Settings({NOTICE_DISMISSED_KEY: 'on'}), False)


def test_menu_explicit_on_off_and_no_implicit_enable():
    app = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    tree = ast.parse(app)
    launcher = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    methods = {n.name: ast.get_source_segment(app,n) for n in launcher.body if isinstance(n, ast.FunctionDef)}
    init = methods['__init__']
    assert "self.theme_menu.addMenu('マウスポインター自動移動')" in init
    assert "(True, 'ON'" in init
    assert 'OFF（仮想環境等の非対応環境用）' in init
    assert 'self.pointer_warp_mode_group.setExclusive(True)' in init
    assert 'self.set_pointer_warp_enabled(value)' in init
    assert 'self.set_vdi_no_cursor_warp(not bool(enabled))' in methods['set_pointer_warp_enabled']
    assert 'self.pointer_warp_enabled = not self.vdi_no_cursor_warp' in methods['set_vdi_no_cursor_warp']
    assert "self.settings.setValue('vdi_no_cursor_warp', self.vdi_no_cursor_warp)" in methods['set_vdi_no_cursor_warp']
    assert 'self.set_pointer_warp_enabled(True)' not in methods['open_pointer_warp_settings']
    assert 'self.set_vdi_no_cursor_warp(False)' not in methods['open_pointer_warp_settings']


def test_balloon_actions_and_persistent_opt_out():
    app = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    ui = (ROOT / 'src/pointer_warp_notice.py').read_text(encoding='utf-8')
    assert 'QTimer.singleShot(1500, window.maybe_show_pointer_warp_notice)' in app
    assert 'should_show_pointer_warp_notice(self.settings, self.pointer_warp_enabled)' in app
    assert 'self.settings.setValue(NOTICE_DISMISSED_KEY, True)' in app
    for label in ('今後表示しない', '設定を開く', 'あとで'):
        assert label in ui
    assert 'WA_ShowWithoutActivating' in ui
    assert 'self.open_theme_menu()' in app
    assert 'notice.frameGeometry().contains(QCursor.pos())' in app
