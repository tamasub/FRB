"""Qt-free IMM32 policy tests: open IME + hiragana/fullwidth, not katakana."""
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import ime_input


def test_ime_init_is_noop_on_non_windows_or_null_hwnd(monkeypatch):
    monkeypatch.setattr(ime_input, 'os', SimpleNamespace(name='posix'))
    assert ime_input.initialize_japanese_hiragana(100) is False
    assert ime_input.initialize_japanese_hiragana(None) is False


def test_ime_opens_hiragana_and_preserves_other_flags(monkeypatch):
    monkeypatch.setattr(ime_input, 'os', SimpleNamespace(name='nt'))
    log = []

    def context(hwnd):
        log.append(('get_context', hwnd))
        return 222

    def get_conversion(ctx, conversion, sentence):
        conversion._obj.value = 0x0002 | 0x0040  # KATAKANA and other preserved flag
        sentence._obj.value = 7
        log.append(('get_conversion', ctx))
        return True

    def set_conversion(ctx, conversion, sentence):
        log.append(('set_conversion', ctx, conversion, sentence))
        return True

    def open_ime(ctx, enabled):
        log.append(('open', ctx, bool(enabled)))
        return True

    def release(hwnd, ctx):
        log.append(('release', hwnd, ctx))
        return True

    api = SimpleNamespace(ImmGetContext=Mock(side_effect=context),
                          ImmReleaseContext=Mock(side_effect=release),
                          ImmGetConversionStatus=Mock(side_effect=get_conversion),
                          ImmSetConversionStatus=Mock(side_effect=set_conversion),
                          ImmSetOpenStatus=Mock(side_effect=open_ime))
    monkeypatch.setattr(ime_input.ctypes, 'WinDLL', lambda *a, **kw: api, raising=False)
    assert ime_input.initialize_japanese_hiragana(789) is True
    assert log[0] == ('get_context', 789)
    assert log[1] == ('open', 222, True)
    expected = 0x0001 | 0x0008 | 0x0010 | 0x0040
    assert ('set_conversion', 222, expected, 7) in log
    assert log[-1] == ('release', 789, 222)


def test_ime_failure_releases_context(monkeypatch):
    monkeypatch.setattr(ime_input, 'os', SimpleNamespace(name='nt'))
    api = SimpleNamespace(ImmGetContext=Mock(return_value=123),
                          ImmReleaseContext=Mock(return_value=True),
                          ImmSetOpenStatus=Mock(return_value=False),
                          ImmGetConversionStatus=Mock(return_value=False),
                          ImmSetConversionStatus=Mock(return_value=False))
    monkeypatch.setattr(ime_input.ctypes, 'WinDLL', lambda *a, **kw: api, raising=False)
    assert ime_input.initialize_japanese_hiragana(789) is False
    api.ImmReleaseContext.assert_called_once_with(789, 123)
