"""2026-11-08: FRBかな caret insertion and click-outside rename dismissal.

Pure tests with Qt stand-ins: CI doesn't need a GUI. Actual Windows/IME event
ordering still requires a manual smoke check.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from remote_kana_target import RemoteKanaTarget
from test_remote_kana_inline_rename_focus_20261104 import (
    _qt_modules, FakeLineEdit, FakeQApplication,
)


def isolated_view_method(name, extra):
    tree = ast.parse((ROOT / 'src/expanded_view.py').read_text(encoding='utf-8'))
    owner = next(c for c in tree.body if isinstance(c, ast.ClassDef)
                 and c.name == 'ExpandedLauncherView')
    method = next(m for m in owner.body if isinstance(m, ast.FunctionDef)
                  and m.name == name)
    scope = dict(extra)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 'expanded-isolated', 'exec'), scope)
    return scope[name]


class FakeSignal:
    def __init__(self):
        self.handlers = []

    def connect(self, callback):
        self.handlers.append(callback)

    def disconnect(self, callback):
        self.handlers.remove(callback)

    def emit(self):
        for handler in list(self.handlers):
            handler()


class CaretEditor(FakeLineEdit):
    def __init__(self, value):
        super().__init__('inlineRenameEditor', value)
        self.selectionChanged = FakeSignal()
        self.focused = True

    def hasFocus(self):
        return self.focused

    def click_at(self, index):
        self.cursor = index
        self.deselect()
        self.selectionChanged.emit()


def test_kana_does_not_restore_old_stem_selection_after_clicking_caret(monkeypatch):
    _qt_modules(monkeypatch)
    editor = CaretEditor('釣り竿研究.md')
    FakeQApplication.current = editor
    target = RemoteKanaTarget.capture()
    assert target._selection is not None  # Initial stem selection.
    editor.click_at(3)  # User moves caret after opening FRBかな.
    assert target._selection is None
    editor.focused = False
    # Changing focus to the IME must not restore the obsolete selection.
    assert target.send('新') is True
    assert editor.value == '釣り竿新研究.md'
    assert target.last_send_replaced is False
    target.release_inline_editor()
    assert not editor.selectionChanged.handlers


def test_kana_can_still_replace_currently_selected_stem(monkeypatch):
    _qt_modules(monkeypatch)
    editor = CaretEditor('釣り竿研究.md')
    FakeQApplication.current = editor
    target = RemoteKanaTarget.capture()
    assert target.send('完成') is True
    assert editor.value == '完成.md'
    assert target.last_send_replaced is True
    target.release_inline_editor()


def fake_ui():
    class QWidget:
        pass

    class W(QWidget):
        def __init__(self, owner=None):
            self.owner = owner

        def window(self):
            return self.owner

        def isAncestorOf(self, other):
            return False

    launcher = W()
    editor = W(launcher)
    row = object()
    other_row = object()
    viewport = W(launcher)
    tree_calls = []
    tree = NS(state=lambda: 1,
              findChild=lambda cls, object_name: editor,
              viewport=lambda: viewport,
              currentItem=lambda: row,
              itemAt=lambda point: point,
              editTriggers=lambda: 'SelectedClicked',
              setEditTriggers=lambda value: tree_calls.append(value))
    finished = []
    forgotten = []
    launcher._remote_kana_companion = NS(forget_closed_inline_editor=lambda e: forgotten.append(e))
    view = NS(middle=NS(tree=tree), launcher=launcher,
              commit_remote_inline_rename=lambda: finished.append('commit') or True)
    Qt = NS(MouseButton=NS(LeftButton=1, RightButton=2))
    QEvent = NS(Type=NS(MouseButtonPress=10, MouseButtonRelease=11))
    QAbstractItemView = NS(State=NS(EditingState=1), EditTrigger=NS(NoEditTriggers='disabled'))
    timers = []
    QTimer = NS(singleShot=lambda delay, fn: timers.append(fn))
    event = lambda kind, row=other_row: NS(type=lambda: kind, button=lambda: 1,
                                          position=lambda: NS(toPoint=lambda: row))
    scope = dict(QEvent=QEvent, Qt=Qt, QAbstractItemView=QAbstractItemView,
                 QWidget=QWidget, QLineEdit=W, QTimer=QTimer)
    dismiss = isolated_view_method('_dismiss_middle_rename_on_outside_click', scope)
    release = isolated_view_method('_restore_middle_rename_triggers_on_release', scope)
    return NS(view=view, launcher=launcher, editor=editor, viewport=viewport,
              row=row, other_row=other_row, W=W, event=event,
              tree_calls=tree_calls, finished=finished,
              forgotten=forgotten, timers=timers, dismiss=dismiss,
              release=release)


def test_click_in_blank_15_lane_finishes_rename_and_rearms_after_release():
    ui = fake_ui()
    blank_lane = ui.W(ui.launcher)
    ui.dismiss(ui.view, blank_lane, ui.event(10))
    assert ui.finished == ['commit']
    assert ui.forgotten == [ui.editor]
    assert ui.tree_calls == ['disabled']
    ui.release(ui.view, ui.event(11))
    # No new SelectedClicked rename during mouseReleaseEvent.
    assert ui.tree_calls == ['disabled']
    assert len(ui.timers) == 1
    ui.timers.pop()()
    assert ui.tree_calls == ['disabled', 'SelectedClicked']


def test_clicking_editor_or_same_row_keeps_editing():
    ui = fake_ui()
    ui.dismiss(ui.view, ui.editor, ui.event(10))
    ui.dismiss(ui.view, ui.viewport, ui.event(10, ui.row))
    assert ui.finished == []


def test_click_other_row_closes_editor_but_kana_tool_does_not():
    ui = fake_ui()
    kana_window = ui.W()
    ui.dismiss(ui.view, kana_window, ui.event(10))
    assert ui.finished == []
    ui.dismiss(ui.view, ui.viewport, ui.event(10, ui.other_row))
    assert ui.finished == ['commit']


def test_click_when_not_editing_is_inert():
    ui = fake_ui()
    ui.view.middle.tree.state = lambda: 0
    ui.dismiss(ui.view, ui.W(ui.launcher), ui.event(10))
    assert ui.finished == []


def test_global_filter_and_explicit_outside_click_wiring_exist():
    src = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
    assert 'QApplication.instance().installEventFilter(self)' in src
    assert 'self._dismiss_middle_rename_on_outside_click(obj, event)' in src
    assert 'self._restore_middle_rename_triggers_on_release(event)' in src


def test_kana_target_is_invalidated_when_inline_editor_is_closed(monkeypatch):
    _qt_modules(monkeypatch)
    source = (ROOT / 'src/remote_kana_integration.py').read_text(encoding='utf-8')
    node = ast.parse(source)
    owner = next(n for n in node.body if isinstance(n, ast.ClassDef)
                 and n.name == 'RemoteKanaIntegration')
    method = next(n for n in owner.body if isinstance(n, ast.FunctionDef)
                  and n.name == 'forget_closed_inline_editor')
    namespace = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 'kana-integration', 'exec'), namespace)
    editor = FakeLineEdit('inlineRenameEditor', '元の名前.txt')
    target = RemoteKanaTarget.from_widget(editor)
    assert editor.filters
    tooltips = []
    session = NS(target=target, window=NS(send_button=NS(setToolTip=tooltips.append)))
    namespace['forget_closed_inline_editor'](session, editor)
    assert session.target is None
    assert editor.filters == []
    assert '送信先未選択' in tooltips[-1]
