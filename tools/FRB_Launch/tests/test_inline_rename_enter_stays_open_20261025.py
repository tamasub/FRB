"""Regression: Enter in the Files inline rename must not launch the file.

Qt-free tests exercise the real source methods (AST isolation) so they run on
non-Windows CI as well as the ordinary Windows PySide6 application.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
VIEW = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')


def method(source, owner, name, scope):
    module = ast.parse(source)
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == owner)
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    isolated = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    exec(compile(isolated, '<source>', 'exec'), scope)
    return scope[name]


class FakeQt:
    class Key:
        Key_Return = 13
        Key_Enter = 10
        Key_Escape = 27
    class Mouse:
        pass


class FakeTree:
    def __init__(self):
        self._rename_enter_guard = False
        self._rename_enter_epoch = 0
    def state(self):
        return 'idle'


class FakeLineEdit:
    def objectName(self):
        return 'inlineRenameEditor'


class FakeEvent:
    def __init__(self, key):
        self._key = key
        self.accepted = False
    def type(self):
        return 'keypress'
    def key(self):
        return self._key
    def accept(self):
        self.accepted = True


def test_delegate_intercepts_enter_commits_exactly_once_and_guards_activation():
    timers = []
    tree = FakeTree()
    emitted = []
    class FakeBase:
        def eventFilter(self, obj, event):
            emitted.append('base')
            return False
    class FakeSignal:
        def __init__(self, name): self.name = name
        def emit(self, *args):
            emitted.append(self.name)
            if self.name == 'commit':
                assert tree._rename_enter_guard
    # Compile the actual delegate method into a simple fake class, without Qt.
    src = ast.parse(VIEW)
    node = next(n for n in src.body if isinstance(n, ast.ClassDef)
                and n.name == '_InlineRenameDelegate')
    fn = next(n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == 'eventFilter')
    dummy = ast.ClassDef(name='Delegate', bases=[ast.Name(id='FakeBase', ctx=ast.Load())],
                         keywords=[], body=[fn], decorator_list=[])
    scope = {
        'FakeBase': FakeBase,
        'QLineEdit': FakeLineEdit,
        'QTreeWidget': FakeTree,
        'QEvent': SimpleNamespace(Type=SimpleNamespace(KeyPress='keypress')),
        'Qt': FakeQt,
        'QAbstractItemDelegate': SimpleNamespace(EndEditHint=SimpleNamespace(NoHint='none')),
        'QTimer': SimpleNamespace(singleShot=lambda msecs, callback: timers.append((msecs, callback))),
    }
    module = ast.fix_missing_locations(ast.Module(body=[dummy], type_ignores=[]))
    exec(compile(module, '<delegate>', 'exec'), scope)
    delegate = scope['Delegate']()
    delegate.parent = lambda: tree
    delegate.commitData = FakeSignal('commit')
    delegate.closeEditor = FakeSignal('close')
    event = FakeEvent(FakeQt.Key.Key_Return)
    assert delegate.eventFilter(FakeLineEdit(), event)
    assert event.accepted
    assert emitted == ['commit', 'close']
    assert tree._rename_enter_guard
    assert len(timers) == 1 and timers[0][0] >= 0
    timers.pop()[1]()
    assert not tree._rename_enter_guard


def test_only_enter_is_special_editor_keeps_other_keys():
    # Esc and IME composition remain owned by the original Qt delegate.
    assert 'return super().eventFilter(obj, event)' in VIEW.split('class _InlineRenameDelegate(', 1)[1].split('class _SeparatedFileTree(', 1)[0]
    assert 'event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)' in VIEW


def test_editor_enter_must_not_execute_directory_or_file():
    qt = SimpleNamespace(State=SimpleNamespace(EditingState='editing'))
    for function in ('activate_row', 'enter_row'):
        executed = []
        tree = FakeTree()
        middle = SimpleNamespace(tree=tree)
        view = SimpleNamespace(middle=middle, left=object(),
                               choose_middle=lambda item, col: executed.append('choose_middle'),
                               row_data=lambda i: {'item_kind': 'directory'},
                               launcher=SimpleNamespace(execute=lambda r: executed.append('execute'),
                                                        activate=lambda r: executed.append('activate')))
        action = method(VIEW, 'ExpandedLauncherView', function,
                        {'QAbstractItemView': qt})
        tree._rename_enter_guard = True
        action(view, middle, object())
        assert executed == []
        tree._rename_enter_guard = False
        action(view, middle, object())
        assert executed == (['execute'] if function == 'enter_row' else ['choose_middle'])


def test_normal_expanded_enter_dispatch_remains_in_place():
    assert 'view.enter_row(pane, item)' in APP
    assert 'if (pane is self.expanded_view.middle and' in APP
    assert "getattr(pane.tree, '_rename_enter_guard', False)" in APP
