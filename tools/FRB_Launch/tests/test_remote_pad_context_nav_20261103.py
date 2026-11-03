"""Remote pad special context commands: reuse real ← / → without changing native menus."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

APP = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text('utf-8')
WHEEL = (Path(__file__).resolve().parents[1] / 'src' / 'remote_context_wheel.py').read_text('utf-8')


def method(name, ns):
    root = ast.parse(APP)
    cls = next(node for node in root.body if isinstance(node, ast.ClassDef) and node.name == 'Launcher')
    fn = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == name)
    scope = dict(ns)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), 'isolated', 'exec'), scope)
    return scope[name]


class Signal:
    def __init__(self):
        self.callbacks = []
    def connect(self, callback):
        self.callbacks.append(callback)
    def emit(self, *args):
        for callback in self.callbacks:
            callback(*args)


class Action:
    def __init__(self, name, parent=None, *, separator=False):
        self.name = name
        self.triggered = Signal()
        self.separator = separator
        self.hint = None
    def setToolTip(self, value):
        self.hint = value
    def trigger(self):
        self.triggered.emit(False)


class Menu:
    def __init__(self, *_):
        self._actions = []
        self.visible = False
        self.closed = 0
        self.popup_location = None
    def addAction(self, action):
        self._actions.append(action)
    def insertAction(self, before, action):
        self._actions.insert(self._actions.index(before), action)
    def insertSeparator(self, before):
        self._actions.insert(self._actions.index(before), Action('---', separator=True))
    def actions(self):
        return self._actions
    def popup(self, point):
        self.visible = True
        self.popup_location = point
    def isVisible(self):
        return self.visible
    def close(self):
        self.visible = False
        self.closed += 1


def owner(active=True):
    jobs = []
    instance = NS(_remote_pad_context_active=active, _remote_pad_context_menu=None,
                  _remote_context_wheel=None, commands=[])
    instance.remote_command = lambda command: instance.commands.append(command)
    instance._invoke_remote_pad_navigation = lambda m, c: method(
        '_invoke_remote_pad_navigation', {'QTimer': NS(singleShot=lambda n, cb: jobs.append(cb))})(instance,m,c)
    instance._prepend_remote_pad_navigation = lambda m, **kw: method(
        '_prepend_remote_pad_navigation', {'QAction': Action})(instance,m,**kw)
    return instance, jobs


def test_pad_menu_first_two_entries_are_arrows_and_original_items_follow():
    app, jobs = owner()
    menu = Menu()
    menu.addAction(Action('コピー'))
    menu.addAction(Action('削除'))
    assert app._prepend_remote_pad_navigation(menu)
    assert [a.name for a in menu.actions()] == [
        '戻る', '進む', '---', '検索履歴', 'フォルダー履歴', '---', 'コピー', '削除']
    assert not app._prepend_remote_pad_navigation(menu)  # no duplicates
    assert menu.actions()[0].hint.endswith('←と同じ操作')
    assert menu.actions()[1].hint.endswith('→と同じ操作')
    menu.popup((3, 4))
    menu.actions()[0].trigger()
    assert menu.closed == 1
    assert app.commands == []  # never execute while the popup has the grab
    jobs.pop(0)()
    assert app.commands == ['LEFT']
    menu.popup((3, 4))
    menu.actions()[1].trigger()
    assert menu.closed == 2
    jobs.pop(0)()
    assert app.commands == ['LEFT', 'RIGHT']


def test_native_context_never_receives_remote_only_entries():
    app, _jobs = owner(active=False)
    menu = Menu()
    menu.addAction(Action('コピー'))
    assert not app._prepend_remote_pad_navigation(menu)
    assert [a.name for a in menu.actions()] == ['コピー']


def test_remote_pad_wrapper_uses_existing_menu_and_enables_wheel_navigation():
    app, _jobs = owner()
    pad = NS(width=lambda: 68, mapToGlobal=lambda point: point)
    app.remote_window = NS(pad=pad, isVisible=lambda: True)
    opened = Menu()
    opened.addAction(Action('リネーム'))
    captured = []
    def open_context():
        app._prepend_remote_pad_navigation(opened)
        opened.popup((2, 3))
    app._show_remote_target_context_menu = open_context
    app._enable_remote_context_wheel_for_menu = lambda menu: captured.append(menu)
    call = method('remote_context_menu', {'QMenu': Menu})
    call(app)
    assert [a.name for a in opened.actions()][:6] == [
        '戻る', '進む', '---', '検索履歴', 'フォルダー履歴', '---']
    assert captured == [opened]
    assert not app._remote_pad_context_active


def test_no_selected_item_still_shows_navigation_and_history_context_menu():
    app, jobs = owner()
    app.remote_window = NS(
        pad=NS(width=lambda: 68, mapToGlobal=lambda p: ('pad', p)),
        isVisible=lambda: True)
    app._show_remote_target_context_menu = lambda: None
    visible = []
    app._enable_remote_context_wheel_for_menu = lambda m: visible.append(m)
    call = method('remote_context_menu', {
        'QMenu': Menu, 'QPoint': lambda x,y:(x,y)})
    call(app)
    assert len(visible) == 1
    menu = visible[0]
    assert [a.name for a in menu.actions()] == [
        '戻る', '進む', '---', '検索履歴', 'フォルダー履歴']
    assert menu.popup_location == ('pad',(72, 0))
    menu.actions()[1].trigger()
    jobs.pop(0)()
    assert app.commands == ['RIGHT']


def test_existing_specialized_context_menus_prepend_before_showing():
    # The scope applies to file, folder, virtual Launch JSON and Browser.
    assert APP.count('self._prepend_remote_pad_navigation(menu)') >= 5
    assert "if getattr(self, '_remote_pad_context_active', False):" in APP
    assert 'self._enable_remote_context_wheel_for_menu(menu)' in APP
    assert "if action in getattr(self.current, 'openers', {}):" in WHEEL


def test_remote_folder_list_opener_keeps_popup_instead_of_closing():
    # Reuse the existing tested Qt-free harness to check RemoteFolderActionsMenu.
    # Source-level guard confirms the special handling is before root.close().
    command_body = WHEEL.split("        if name in ('RIGHT', 'ENTER', 'CLICK'):", 1)[1]
    assert command_body.index("if action in getattr(self.current, 'openers', {}):") < command_body.index('self.root.close()')


def test_files_exp_folder_only_marks_back_as_initial_cursor():
    app, _jobs = owner()
    files_exp = Menu()
    files_exp.remote_context_root = True
    files_exp.remote_target_directory = r'F:\\FRB\\tools\\FRB_Launch'
    files_exp.addAction(Action('Filesリスト'))
    assert app._prepend_remote_pad_navigation(files_exp)
    assert files_exp._remote_pad_initial_action is files_exp.actions()[0]
    assert files_exp._remote_pad_initial_action.name == '戻る'

    list_background = Menu()
    list_background.remote_context_root = True
    list_background.remote_target_directory = None
    list_background.addAction(Action('Filesリスト'))
    assert app._prepend_remote_pad_navigation(list_background)
    assert not hasattr(list_background, '_remote_pad_initial_action')

    normal = Menu()
    normal.addAction(Action('コピー'))
    assert app._prepend_remote_pad_navigation(normal)
    assert not hasattr(normal, '_remote_pad_initial_action')
