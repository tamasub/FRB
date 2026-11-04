"""Pure contract tests for the FRB Remote + kana companion integration.

Qt UI is also inspected as source because CI may not have PySide6 or a desktop;
real mouse/IME tests are documented for Windows 11 manual verification.
"""
import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
from remote_kana_target import RemoteKanaTarget, ExternalTarget


class DummyWin32:
    def __init__(self, restore=True, matches=True):
        self.restored = restore
        self.match = matches
        self.sent = []

    def restore(self, target):
        return self.restored

    def matches(self, target):
        return self.match

    def send_unicode(self, text):
        self.sent.append(text)


def _file(path):
    return (ROOT / path).read_text(encoding='utf-8')


def test_external_target_insert_append_with_focus_validation():
    api = DummyWin32()
    target = RemoteKanaTarget(external=ExternalTarget(100, 200, 'Sakura'), api=api)
    assert target.can_send()
    assert target.label == 'Sakura'
    assert target.send('今日はいい天気') is True
    assert api.sent == ['今日はいい天気']


def test_external_target_reject_changed_focus_without_typing():
    api = DummyWin32(matches=False)
    target = RemoteKanaTarget(external=ExternalTarget(100, 200, 'Sakura'), api=api)
    try:
        target.send('危険')
    except RuntimeError as exc:
        assert '送信先' in str(exc)
    else:
        raise AssertionError('must reject stale focus')
    assert api.sent == []


def test_external_target_reject_unrestorable_window():
    api = DummyWin32(restore=False)
    target = RemoteKanaTarget(external=ExternalTarget(100, 200, 'Sakura'), api=api)
    try:
        target.send('禁止')
    except RuntimeError:
        pass
    else:
        raise AssertionError('must reject')
    assert api.sent == []


def test_empty_target_never_sends():
    target = RemoteKanaTarget()
    assert not target.can_send()
    try:
        target.send('hello')
    except RuntimeError:
        pass
    else:
        raise AssertionError('target required')


def test_remote_buttons_and_history_context_menu_preserved():
    s = _file('src/launch_remote.py')
    assert "'HOME', width=68, height=46" in s
    assert "'REMOTE_KANA_TOGGLE', width=50, height=46" in s
    assert 'self.home_button' in s and 'self.kana_button' in s
    assert 'root.addLayout(row_quick)' in s
    assert "検索履歴'," not in s[s.index('row_quick = QHBoxLayout()'):s.index('row_mid = QHBoxLayout()')]
    assert 'self.header_remote_icon' in s
    assert 'self.home_button.setIcon(browser_navigation_icon' in s
    assert 'self.kana_button.setIcon(remote_compact_icon' in s


def test_keyboard_has_explicit_send_and_light_dark_switch():
    s = _file('experiments/frb_japanese_input/frb_japanese_input.py')
    assert "send_requested = Signal(str)" in s
    assert "theme_requested = Signal(str)" in s
    assert 'self.send_button = self._micro("送信"' in s
    assert 'self.output.is_composing or self.model.has_preedit' in s
    assert "def style_for_size(font_size: int, theme: str = \"dark\")" in s
    assert "def apply_theme(self, theme: str)" in s
    assert 'self.theme_button' in s


def test_generated_qss_is_valid_for_both_themes():
    s = _file('experiments/frb_japanese_input/frb_japanese_input.py')
    syntax = ast.parse(s)
    function = next(n for n in syntax.body
                    if isinstance(n, ast.FunctionDef) and n.name == 'style_for_size')
    namespace = {}
    exec(compile(ast.Module(body=[function], type_ignores=[]), 'qss', 'exec'), namespace)
    dark = namespace['style_for_size'](20, 'dark')
    light = namespace['style_for_size'](20, 'light')
    assert 'QWidget#frbWindow { background: transparent;' in dark
    assert 'QWidget#frbWindow { background: transparent;' in light
    assert '#263532' in dark
    assert '#dbe7df' in light
    assert '{font_size}' not in dark
    assert '__FRB_COLOR_' not in light
    assert 'QPushButton#literalKey {' in dark


def test_keyboard_window_attached_and_theme_synced():
    app = _file('src/app.py')
    conn = _file('src/remote_kana_integration.py')
    assert "if command == 'REMOTE_KANA_TOGGLE':" in app
    assert 'companion.theme_changed()' in app
    assert 'companion.hide()' in app
    assert 'self.window.apply_theme(self.launcher.color_theme)' in conn
    assert "self.launcher.set_color_theme(theme)" in conn
    assert 'self.target = RemoteKanaTarget.capture(excluded_window=self.window)' in conn
    assert 'self.target.api.matches(self.target.external)' in conn


def test_packaging_includes_experiment_python_for_frozen_app():
    bat = _file('_build_windows.bat')
    spec = _file('FRBLaunch.spec')
    assert '--add-data "experiments\\frb_japanese_input;experiments/frb_japanese_input"' in bat
    assert "('experiments/frb_japanese_input', 'experiments/frb_japanese_input')" in spec


def test_keyboard_modules_keep_fixed_directory_and_no_legacy_version_folder():
    assert (ROOT/'experiments/frb_japanese_input/frb_japanese_input.py').exists()
    assert not (ROOT/'experiments/frb_japanese_input_v0_11').exists()
