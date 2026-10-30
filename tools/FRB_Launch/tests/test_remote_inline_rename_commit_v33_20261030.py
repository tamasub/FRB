"""v33: Remote wheel pad commits an active Files inline rename (file or folder).

Qt-free regression around the real production methods.  The final Windows
GUI event order still needs a local PySide6 click test.
"""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from context_menu_resolver import resolve_context_target
from context_menu_actions import rename_file_or_folder


def isolate(path, cls, name, env):
    mod = ast.parse(path.read_text(encoding='utf-8'))
    parent = next(x for x in mod.body if isinstance(x, ast.ClassDef) and x.name == cls)
    method = next(x for x in parent.body if isinstance(x, ast.FunctionDef) and x.name == name)
    scope = dict(env)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 '<isolated>', 'exec'), scope)
    return scope[name]


EDITING = 'editing'
IDLE = 'idle'
qtwidgets = NS(State=NS(EditingState=EDITING))
qtdelegate = NS(EndEditHint=NS(NoHint='no-hint'))
qt = NS(ItemFlag=NS(ItemIsEditable=1))
VIEW = ROOT / 'src/expanded_view.py'
APP = ROOT / 'src/app.py'


class Editor:
    pass


class Delegate:
    def __init__(self, on_commit, on_close):
        self.commitData = NS(emit=Mock(side_effect=on_commit))
        self.closeEditor = NS(emit=Mock(side_effect=on_close))


class Tree:
    def __init__(self, editor, delegate, state=EDITING):
        self.editor = editor
        self.delegate = delegate
        self._state = state
        self._rename_enter_epoch = 0
        self._rename_enter_guard = False

    def state(self): return self._state
    def findChild(self, cls, name):
        assert cls is Editor and name == 'inlineRenameEditor'
        return self.editor
    def itemDelegateForColumn(self, col):
        assert col == 0
        return self.delegate
    def currentItem(self): return self.item
    def indexOfTopLevelItem(self, item):
        return 0 if item is self.item else -1


def commit_method(timers):
    return isolate(VIEW, 'ExpandedLauncherView', 'commit_remote_inline_rename', {
        'QAbstractItemView': qtwidgets, 'QLineEdit': Editor,
        '_InlineRenameDelegate': Delegate, 'QAbstractItemDelegate': qtdelegate, 'Qt': qt,
        'QTimer': NS(singleShot=lambda delay, callback: timers.append((delay, callback))),
    })


def test_wheel_click_commits_real_file_and_folder_names(tmp_path):
    """Both object types must reuse the existing filesystem rename callback."""
    finisher = isolate(VIEW, 'ExpandedLauncherView', 'finish_inline_rename', {
        'Path': Path, 'resolve_context_target': resolve_context_target,
        'rename_file_or_folder': rename_file_or_folder,
        'QTimer': NS(singleShot=lambda delay, f: f()),
    })
    for folder in (False, True):
        source = tmp_path / ('oldfolder' if folder else 'oldfile.txt')
        if folder:
            source.mkdir()
        else:
            source.write_text('original', encoding='utf-8')
        destination = tmp_path / ('newfolder' if folder else 'newfile.txt')
        row = {'_file': str(source), 'title': source.name,
               'item_kind': 'directory' if folder else 'command'}
        class Item:
            def __init__(self): self._flags = 1
            def text(self, column): return destination.name
            def flags(self): return self._flags
            def setFlags(self, value): self._flags = value
        item = Item()
        updates = []
        launcher = NS(authored_items=(), footer=NS(setText=updates.append))
        view = NS(row_data=lambda _: row, launcher=launcher, refresh_middle=Mock())
        editor = Editor()
        tree = Tree(editor, None)
        tree.item = item
        def on_commit(e):
            assert e is editor
            assert tree._rename_enter_guard
            finisher(view, item, 0)
        def on_close(e, hint):
            assert hint == 'no-hint'
            tree._state = IDLE
        delegate = Delegate(on_commit, on_close)
        tree.delegate = delegate
        view.middle = NS(tree=tree)
        timers = []
        assert commit_method(timers)(view) is True
        assert not source.exists()
        assert destination.exists()
        assert delegate.commitData.emit.call_count == 1
        assert delegate.closeEditor.emit.call_count == 1
        assert tree._state == IDLE
        assert tree._rename_enter_guard
        assert item.flags() == (0 if folder else 1)
        assert len(timers) == 1 and timers[0][0] >= 0
        timers[0][1]()
        assert not tree._rename_enter_guard
        assert commit_method([])(view) is False


def test_editing_without_editor_consumes_click_instead_of_opening_row():
    tree = Tree(None, Delegate(lambda e: None, lambda *args: None))
    view = NS(middle=NS(tree=tree))
    assert commit_method([])(view) is True
    tree._state = IDLE
    assert commit_method([])(view) is False


def test_remote_click_routing_commits_before_click_and_never_activates_row():
    remote_click = isolate(APP, 'Launcher', 'remote_mouse_click', {'starting_area': Mock()})
    done = Mock(return_value=True)
    view = NS(isVisible=lambda: True, commit_remote_inline_rename=done,
              activate_row=Mock())
    win = NS(expanded_view=view, _remote_mouse_last_click=('directory', 'oldfile'),
             _remote_mouse_menu_click='menu-item', _remote_area='directory')
    remote_click(win, double=False)
    done.assert_called_once()
    view.activate_row.assert_not_called()
    assert win._remote_mouse_last_click is None
    assert win._remote_mouse_menu_click is None
    remote_click(win, double=True)
    assert done.call_count == 2
    view.activate_row.assert_not_called()


def test_regular_click_path_keeps_legacy_behavior():
    # The full pre-v33 wheel-pad tests already verify normal file selection,
    # folder single/double click, bookmarks, and classic search results.
    # Here make sure the first edit check only handles an active editor.
    source = APP.read_text(encoding='utf-8')
    assert "if callable(commit_rename) and commit_rename():" in source
    assert "self.remote_mouse_click(double=command == 'DOUBLE_CLICK')" in source
