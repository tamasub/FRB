"""Remote pad: Files List context begins with a direct jump back to Files Exp.

Only the Remote pad popup is changed; native right-click and other panes keep
existing menus. These Qt-free tests exercise the actual Launcher method AST.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text('utf-8')


def method(name, globals_):
    module = ast.parse(SOURCE)
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    scope = dict(globals_)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), 'unit', 'exec'), scope)
    return scope[name]


class Action:
    def __init__(self, label, parent=None, *, separator=False):
        self.label = label
        self.separator = separator
        self.callbacks = []
        self.triggered = NS(connect=self.callbacks.append)
        self.hint = None

    def setToolTip(self, value):
        self.hint = value

    def trigger(self):
        for fn in self.callbacks:
            fn(False)


class Menu:
    def __init__(self, original):
        self.entries = [Action(label) for label in original]
        self.closed = 0
        self._visible = True

    def actions(self):
        return self.entries

    def insertAction(self, before, action):
        self.entries.insert(self.entries.index(before), action)

    def insertSeparator(self, before):
        self.insertAction(before, Action('---', separator=True))

    def addAction(self, action):
        self.entries.append(action)

    def close(self):
        self.closed += 1
        self._visible = False


def launcher(*, area='directory', target='directory', mode='files', expanded=True,
             pad_context=True):
    pending = []
    app = NS(
        expanded_view=NS(isVisible=lambda: expanded, _workspace_mode=mode),
        _files_operating_target=target, _remote_area=area,
        _remote_pad_context_active=pad_context,
        _remote_pad_context_menu=None, _remote_context_wheel=None,
        commands=[])
    app.remote_command = app.commands.append
    app._invoke_remote_pad_navigation = method(
        '_invoke_remote_pad_navigation', {'QTimer': NS(singleShot=lambda _ms, cb: pending.append(cb))}
    ).__get__(app)
    prepend = method('_prepend_remote_pad_navigation', {'QAction': Action})
    return app, prepend.__get__(app), pending


def labels(menu):
    return [a.label for a in menu.actions()]


def test_files_list_folder_and_file_share_first_current_exp_switch():
    for item_name in ('フォルダーを開く', 'ファイルを開く'):
        app, prepend, pending = launcher()
        menu = Menu([item_name, 'コピー', '名前の変更'])
        assert prepend(menu)
        assert labels(menu) == [
            'Exp列に戻る', '---', '戻る', '進む', '---',
            '検索履歴', 'フォルダー履歴', '---', item_name, 'コピー', '名前の変更']
        assert menu._remote_pad_initial_action is menu.actions()[0]
        assert menu._remote_pad_initial_action.hint == '操作対象をFiles Exp列に切り替える'
        assert not prepend(menu)  # no duplicates
        menu.actions()[0].trigger()
        assert menu.closed == 1 and app.commands == []
        assert len(pending) == 1  # deferred until after QMenu is closed
        pending.pop()()
        assert app.commands == ['REMOTE_TARGET_EXP']  # not LEFT: any List row works


def test_list_empty_folder_background_can_return_to_exp():
    app, prepend, _ = launcher()
    menu = Menu(['貼り付け'])
    assert prepend(menu)
    assert menu._remote_pad_initial_action.label == 'Exp列に戻る'


def test_exp_other_workspace_and_native_context_unchanged():
    configurations = (
        dict(area='files_exp', target='files_exp'),
        dict(area='directory', target='files_exp'),
        dict(area='files_exp', target='directory'),
        dict(area='directory', target='directory', mode='browser'),
        dict(area='directory', target='directory', expanded=False),
    )
    for config in configurations:
        _, prepend, _ = launcher(**config)
        menu = Menu(['コピー'])
        assert prepend(menu)
        assert labels(menu) == ['戻る', '進む', '---', '検索履歴', 'フォルダー履歴', '---', 'コピー']
        assert not hasattr(menu, '_remote_pad_initial_action')
    _, prepend, _ = launcher(pad_context=False)
    menu = Menu(['コピー'])
    assert not prepend(menu)
    assert labels(menu) == ['コピー']


def test_exp_folder_retains_its_existing_back_default():
    _, prepend, _ = launcher(area='files_exp', target='files_exp')
    menu = Menu(['Filesリスト', 'コピー'])
    menu.remote_context_root = True
    menu.remote_target_directory = r'F:\\FRB\\FRB_Launch'
    assert prepend(menu)
    assert labels(menu) == ['戻る', '進む', '---', '検索履歴', 'フォルダー履歴', '---', 'Filesリスト', 'コピー']
    assert menu._remote_pad_initial_action.label == '戻る'


def test_remote_command_has_dedicated_direct_switch_command():
    # The existing direct target switch is separate from List LEFT's folder navigation.
    assert "if command in ('REMOTE_TARGET_EXP', 'REMOTE_TARGET_LIST'):" in SOURCE
    assert "target = 'files_exp' if command == 'REMOTE_TARGET_EXP' else 'directory'" in SOURCE
