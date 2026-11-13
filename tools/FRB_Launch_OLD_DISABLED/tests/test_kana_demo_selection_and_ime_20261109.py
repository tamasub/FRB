"""FRB Launch demo regression: kana reopens Japanese IME and sends to rename.

Use Qt stand-ins on CI; verify actual Microsoft IME activation manually on Windows.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from remote_kana_target import RemoteKanaTarget
from test_remote_kana_inline_rename_focus_20261104 import _qt_modules, FakeQApplication
from test_kana_rename_caret_and_outside_click_20261108 import CaretEditor


def method_from_source(path, cls, name, namespace):
    module = ast.parse((ROOT / path).read_text(encoding='utf-8'))
    owner = next(c for c in module.body if isinstance(c, ast.ClassDef) and c.name == cls)
    method = next(m for m in owner.body if isinstance(m, ast.FunctionDef) and m.name == name)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 str(path), 'exec'), namespace)
    return namespace[name]


class RenameEdit(CaretEditor):
    def cursorPosition(self):
        return self.cursor

    def setCursorPosition(self, pos):
        self.cursor = pos
        self.selection = None


def test_selection_survives_focus_changed_and_replaces_only_selected_name(monkeypatch):
    _qt_modules(monkeypatch)
    editor = RenameEdit('2026開発記録.md')
    editor.selection = (2, 6)  # The user selected one piece of the filename.
    FakeQApplication.current = editor
    target = RemoteKanaTarget.capture()
    assert target._selection == ('line', '2026開発記録.md', 2, 4)
    # Qt's actual FocusOut can erase the selected text before focusChanged.
    editor.focused = False
    editor.deselect()
    editor.cursor = 0
    keyboard_output = RenameEdit('')
    keyboard = NS(isVisible=lambda: True, isAncestorOf=lambda w: w is keyboard_output)
    session = NS(window=keyboard, target=target)
    cb = method_from_source('src/remote_kana_integration.py',
                            'RemoteKanaIntegration', '_on_focus_changed',
                            {'RemoteKanaTarget': RemoteKanaTarget,
                             'widget_is_text_target': lambda w: False})
    cb(session, editor, keyboard_output)
    assert target._selection == ('line', '2026開発記録.md', 2, 4)
    target.send('新')
    assert editor.value == '20新記録.md'
    assert target.last_send_replaced is True
    target.release_inline_editor()


def test_unselected_caret_is_restored_when_focus_out_resets_it(monkeypatch):
    _qt_modules(monkeypatch)
    editor = RenameEdit('研究実験.md')
    editor.selection = None
    editor.cursor = 2
    FakeQApplication.current = editor
    target = RemoteKanaTarget.capture()
    assert target._selection is None
    assert target._caret == ('line', '研究実験.md', 2)
    editor.focused = False
    editor.cursor = 0  # Simulate a temporary Windows/Qt caret reset.
    target.send('新')
    assert editor.value == '研究新実験.md'
    assert target.last_send_replaced is False
    target.send('続')
    assert editor.value == '研究新続実験.md'
    target.release_inline_editor()


def test_user_can_move_caret_while_kana_is_open(monkeypatch):
    _qt_modules(monkeypatch)
    editor = RenameEdit('研究実験.md')
    FakeQApplication.current = editor
    target = RemoteKanaTarget.capture()
    editor.click_at(1)
    assert target._selection is None
    assert target._caret == ('line', '研究実験.md', 1)
    editor.focused = False
    editor.cursor = 0
    target.send('前')
    assert editor.value == '研前究実験.md'
    target.release_inline_editor()


def test_reopen_calls_ime_restore_each_time_and_only_in_kana_mode():
    source = (ROOT / 'src/remote_kana_integration.py').read_text(encoding='utf-8')
    assert 'QTimer.singleShot(110, window.restore_ime_on_show)' in source
    method = method_from_source('experiments/frb_japanese_input/frb_japanese_input.py',
                                'MiniJapaneseInputWindow', 'restore_ime_on_show', {})
    calls = []
    output = NS(is_composing=False, hasFocus=lambda: True)
    session = NS(isVisible=lambda: True, _native_mode=True, input_mode='kana',
                 output=output, model=NS(has_preedit=False),
                 _editor_is_focused=lambda: True,
                 _set_windows_ime_mode=calls.append,
                 _ensure_editor_focus=lambda: calls.append('focus'),
                 status=NS(setText=lambda t: calls.append(t)))
    method(session)
    assert calls == ['kana']
    calls.clear()
    session.input_mode = 'latin'
    method(session)
    assert calls == []
    session.input_mode = 'kana'
    session.model.has_preedit = True
    method(session)
    assert calls == []
    session.model.has_preedit = False
    session.isVisible = lambda: False
    method(session)
    assert calls == []


def test_active_inline_rename_takes_precedence_over_stale_menu_focus(monkeypatch):
    _qt_modules(monkeypatch)
    import PySide6.QtWidgets as w

    class View:
        class State:
            EditingState = 1

    w.QAbstractItemView = View

    class VisibleEditor(RenameEdit):
        def isVisible(self):
            return True

    editor = VisibleEditor('あとから.md')
    editor.selection = (0, 4)

    class FakeTree:
        def __init__(self, state):
            self._state = state

        def state(self):
            return self._state

        def findChild(self, cls, name):
            return editor if name == 'inlineRenameEditor' else None

    session = NS(launcher=NS(expanded_view=NS(middle=NS(tree=FakeTree(1))),
                             remote_window=None))
    finder = method_from_source('src/remote_kana_integration.py',
                                'RemoteKanaIntegration', '_capture_active_rename',
                                {'RemoteKanaTarget': RemoteKanaTarget,
                                 'widget_is_text_target': lambda w: True})
    target = finder(session)
    assert target is not None
    assert target.label.endswith('inlineRenameEditor')
    target.send('改名')
    assert editor.value == '改名.md'
    target.release_inline_editor()
    session.launcher.expanded_view.middle.tree._state = 0
    assert finder(session) is None  # Never guess from selected file rows.
