"""FRBかな: keep a transient Files List rename editor alive during IME Send.

Fake Qt objects exercise the focus guard on non-Windows CI. Real Windows Qt
focus/IME behavior must also be checked interactively.
"""
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
from remote_kana_target import RemoteKanaTarget, insert_into_widget


class FakeEvent:
    def __init__(self, kind):
        self.kind = kind

    def type(self):
        return self.kind


class FakeQObject:
    def __init__(self, parent=None):
        self.parent = parent
        self.deleted = False

    def deleteLater(self):
        self.deleted = True


class FakeLineEdit:
    def __init__(self, name='inlineRenameEditor', value='新しいMarkdown文書.md'):
        self.name = name
        self.value = value
        self.cursor = len(value) - 3
        self.selection = (0, self.cursor)
        self.filters = []
        self.focus_out_closed = False

    def objectName(self):
        return self.name

    def isReadOnly(self):
        return False

    def window(self):
        return self

    def installEventFilter(self, guard):
        self.filters.append(guard)

    def removeEventFilter(self, guard):
        self.filters.remove(guard)

    def focus_out(self):
        for guard in reversed(self.filters):
            if guard.eventFilter(self, FakeEvent(8)):
                return
        self.focus_out_closed = True

    def selectionStart(self):
        return self.selection[0] if self.selection else -1

    def selectedText(self):
        if not self.selection:
            return ''
        a, b = self.selection
        return self.value[a:b]

    def text(self):
        return self.value

    def setSelection(self, start, length):
        self.selection = (start, start + length)

    def deselect(self):
        self.selection = None

    def insert(self, text):
        if self.selection:
            start, end = self.selection
            self.value = self.value[:start] + text + self.value[end:]
            self.cursor = start + len(text)
        else:
            self.value = self.value[:self.cursor] + text + self.value[self.cursor:]
            self.cursor += len(text)
        self.selection = None


class FakeQApplication:
    current = None

    @classmethod
    def focusWidget(cls):
        return cls.current


def _qt_modules(monkeypatch):
    core = types.ModuleType('PySide6.QtCore')
    core.QObject = FakeQObject
    core.QEvent = types.SimpleNamespace(Type=types.SimpleNamespace(FocusOut=8))
    widgets = types.ModuleType('PySide6.QtWidgets')
    widgets.QLineEdit = FakeLineEdit
    widgets.QPlainTextEdit = type('FakePlain', (), {})
    widgets.QTextEdit = type('FakeRich', (), {})
    widgets.QComboBox = type('FakeCombo', (), {})
    widgets.QApplication = FakeQApplication
    qt = types.ModuleType('PySide6')
    qt.QtCore = core
    qt.QtWidgets = widgets
    monkeypatch.setitem(sys.modules, 'PySide6', qt)
    monkeypatch.setitem(sys.modules, 'PySide6.QtWidgets', widgets)
    monkeypatch.setitem(sys.modules, 'PySide6.QtCore', core)


def test_files_list_rename_survives_keyboard_ime_focus_and_send(monkeypatch):
    _qt_modules(monkeypatch)
    editor = FakeLineEdit()
    FakeQApplication.current = editor
    target = RemoteKanaTarget.capture()
    assert target.can_send()
    assert len(editor.filters) == 1

    # Opening FRBかな makes the Windows IME focus leave the rename editor.
    editor.focus_out()
    assert not editor.focus_out_closed
    assert target.send('漢字') is True
    # Replace the selected filename stem while preserving the extension.
    assert editor.value == '漢字.md'
    assert target.last_send_replaced is True
    assert target.send('追記') is True
    assert editor.value == '漢字追記.md'
    assert target.last_send_replaced is False
    assert not editor.focus_out_closed

    # After closing the keyboard, the ordinary delegate contract is restored.
    target.release_inline_editor()
    assert editor.filters == []
    editor.focus_out()
    assert editor.focus_out_closed


def test_ordinary_text_field_is_not_focus_guarded(monkeypatch):
    _qt_modules(monkeypatch)
    editor = FakeLineEdit('searchInput', '検索')
    editor.selection = None
    editor.cursor = len(editor.value)
    FakeQApplication.current = editor
    target = RemoteKanaTarget.capture()
    assert target.can_send()
    assert editor.filters == []
    assert target.send('追加入力') is True
    assert editor.value == '検索追加入力'
    target.release_inline_editor()


def test_only_rename_focus_out_is_intercepted(monkeypatch):
    _qt_modules(monkeypatch)
    editor = FakeLineEdit('filesExpRenameEditor')
    FakeQApplication.current = editor
    target = RemoteKanaTarget.capture()
    guard = editor.filters[0]
    assert guard.eventFilter(editor, FakeEvent(8)) is True
    assert guard.eventFilter(editor, FakeEvent(6)) is False  # KeyPress (Enter/Escape)
    assert guard.eventFilter(object(), FakeEvent(8)) is False
    target.release_inline_editor()
    target.release_inline_editor()  # Idempotent


def test_integration_releases_guard_on_keyboard_hide_and_create_failure():
    source = (ROOT / 'src/remote_kana_integration.py').read_text(encoding='utf-8')
    assert 'self.target.release_inline_editor()' in source
    assert 'def _mark_hidden(self):' in source
    assert 'window = self._create_window()' in source


def test_selected_search_text_is_replaced_even_if_qt_loses_visible_selection(monkeypatch):
    _qt_modules(monkeypatch)
    editor = FakeLineEdit('searchInput', '以前の検索')
    editor.selection = (0, len(editor.value))
    FakeQApplication.current = editor
    target = RemoteKanaTarget.capture()
    # Qt focus transition may erase selection, but it was explicitly saved.
    editor.deselect()
    editor.cursor = len(editor.value)
    assert target.send('玉井久進') is True
    assert editor.value == '玉井久進'
    assert target.last_send_replaced is True


def test_changing_a_selected_text_after_capture_never_overwrites_it(monkeypatch):
    _qt_modules(monkeypatch)
    editor = FakeLineEdit('searchInput', '検索')
    editor.selection = (0, 2)
    FakeQApplication.current = editor
    target = RemoteKanaTarget.capture()
    editor.deselect()
    editor.value = '別の値'
    editor.cursor = len(editor.value)
    assert target.send('追記') is True
    assert editor.value == '別の値追記'
    assert target.last_send_replaced is False


def test_newly_focused_launch_input_can_replace_target_while_keyboard_stays_open(monkeypatch):
    _qt_modules(monkeypatch)
    original = FakeLineEdit('inlineRenameEditor', '古い.md')
    newer = FakeLineEdit('searchInput', '検索')
    newer.selection = (0, 2)
    old_target = RemoteKanaTarget.from_widget(original)
    new_target = RemoteKanaTarget.from_widget(newer)
    old_target.release_inline_editor()
    assert original.filters == []
    assert new_target.send('新') is True
    assert newer.value == '新'
    assert original.value == '古い.md'


def test_open_keyboard_can_follow_new_launch_editor_focus(monkeypatch):
    import ast
    from types import SimpleNamespace
    _qt_modules(monkeypatch)
    source = (ROOT / 'src/remote_kana_integration.py').read_text(encoding='utf-8')
    node = ast.parse(source)
    companion_class = next(n for n in node.body if isinstance(n, ast.ClassDef)
                           and n.name == 'RemoteKanaIntegration')
    focus_method = next(n for n in companion_class.body if isinstance(n, ast.FunctionDef)
                        and n.name == '_on_focus_changed')
    namespace = {'RemoteKanaTarget': RemoteKanaTarget,
                 'widget_is_text_target': __import__('remote_kana_target').widget_is_text_target}
    exec(compile(ast.Module(body=[focus_method], type_ignores=[]), 'focus', 'exec'), namespace)
    handler = namespace['_on_focus_changed']

    first = FakeLineEdit('inlineRenameEditor', '旧名.md')
    second = FakeLineEdit('searchInput', '古い検索')
    second.selection = (0, len(second.value))
    target = RemoteKanaTarget.from_widget(first)
    tooltips = []
    keyboard_output = FakeLineEdit('output', '')
    keyboard = SimpleNamespace(isVisible=lambda: True,
                               isAncestorOf=lambda widget: widget is keyboard_output,
                               send_button=SimpleNamespace(setToolTip=tooltips.append))
    session = SimpleNamespace(target=target, window=keyboard)

    handler(session, first, keyboard_output)
    assert session.target is target
    handler(session, keyboard_output, second)
    assert first.filters == []
    assert session.target is not target
    assert 'searchInput' in tooltips[-1]
    assert session.target.send('玉井久進') is True
    assert second.value == '玉井久進'
    assert first.value == '旧名.md'
