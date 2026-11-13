"""Open With right submenu and Delete routing without Windows/Qt in CI."""
import ast
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
import sys

import pytest

from windows_open_with import OpenWithApp, _exe_from_command, discover_open_with_apps, open_file_with_app

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'src' / 'app.py'


def launcher_method(name, namespace):
    tree = ast.parse(APP.read_text(encoding='utf-8'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    unit = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    exec(compile(unit, str(APP), 'exec'), namespace)
    return namespace[name]


def test_windows_command_parser_does_not_execute_or_import_command_arguments():
    assert _exe_from_command('"C:\\Program Files\\Editor\\Code.exe" "%1"') == r'C:\Program Files\Editor\Code.exe'
    assert _exe_from_command('C:\\Editor\\Cursor.exe "%1"') == r'C:\Editor\Cursor.exe'
    assert _exe_from_command('cmd.exe /c run evil') == 'cmd.exe'
    assert _exe_from_command('rundll32.dll %1') is None


class FakeRegistry:
    HKEY_CURRENT_USER = 1
    HKEY_LOCAL_MACHINE = 2
    HKEY_CLASSES_ROOT = 3

    def __init__(self, values=None, subkeys=None):
        self.data = values or {}
        self.keys = subkeys or {}

    class Key:
        def __init__(self, key): self.key = key
        def __enter__(self): return self
        def __exit__(self, *args): pass

    def OpenKey(self, root, subkey):
        key = root, subkey.casefold()
        if key not in self.data and key not in self.keys:
            raise FileNotFoundError(subkey)
        return self.Key(key)

    def EnumValue(self, opened, index):
        records = list(self.data.get(opened.key, {}).items())
        if index >= len(records): raise OSError('end')
        name, value = records[index]
        return name, value, 1

    def EnumKey(self, opened, index):
        records = self.keys.get(opened.key, [])
        if index >= len(records): raise OSError('end')
        return records[index]

    def QueryValueEx(self, opened, name):
        obj = self.data.get(opened.key, {})
        if name not in obj: raise FileNotFoundError(name)
        return obj[name], 1


def test_registry_uses_recent_apps_then_other_registered_and_only_existing_executables(tmp_path):
    import windows_open_with as w
    cursor = tmp_path / 'Cursor.exe'
    code = tmp_path / 'Code.exe'
    cursor.write_bytes(b'fake exe')
    code.write_bytes(b'fake exe')
    base = r'Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.json'
    reg = FakeRegistry(values={
        (1, (base + r'\OpenWithList').casefold()): {'a': 'Code.exe', 'b': 'Cursor.exe', 'c': 'Ghost.exe', 'MRUList': 'bac'},
        (1, r'Software\Microsoft\Windows\CurrentVersion\App Paths\Code.exe'.casefold()): {'': str(code)},
        (2, r'Software\Microsoft\Windows\CurrentVersion\App Paths\Cursor.exe'.casefold()): {'': str(cursor)},
    })
    with patch.object(w, 'os', SimpleNamespace(name='nt', path=os.path)), \
         patch.dict(sys.modules, {'winreg': reg}), patch.object(w, '_associated_strings', return_value=None):
        result = discover_open_with_apps('my document.json')
    assert [(x.title, x.executable) for x in result[:2]] == [
        ('Cursor', str(cursor)), ('Visual Studio Code', str(code))]
    assert all('Ghost' not in x.title for x in result)


def test_direct_open_never_uses_a_shell_or_changes_association(tmp_path):
    import windows_open_with as w
    file = tmp_path / '設定 & (test).json'
    app = tmp_path / 'Code.exe'
    file.write_text('{}')
    app.write_bytes(b'fake exe')
    with patch.object(w, 'os', SimpleNamespace(name='nt', path=os.path)), patch.object(w.subprocess, 'Popen') as popen:
        open_file_with_app(file, app)
    popen.assert_called_once_with([str(app), str(file.resolve())], close_fds=True)


def test_native_submenu_contains_registered_apps_then_system_fallback():
    class Action:
        def __init__(self, title):
            self.title = title
            self.triggered = SimpleNamespace(connect=lambda cb: setattr(self, 'callback', cb))
        def setIcon(self, icon): pass
        def setEnabled(self, value): self.enabled = value

    class Menu:
        def __init__(self): self.rows = [];self.submenu = None
        def addMenu(self, name):
            self.submenu = Menu()
            self.rows.append(('submenu', name, self.submenu))
            return self.submenu
        def addAction(self, name):
            a = Action(name)
            self.rows.append(('action', a))
            return a
        def addSeparator(self): self.rows.append(('separator',))
        def setObjectName(self, name): pass
        def setIcon(self, icon): pass

    opened = []
    chooser = []
    ns = {'context_action_icon': lambda kind: kind,
          'discover_open_with_apps': lambda path: [OpenWithApp('Cursor', 'C:/Cursor.exe'),
                                                   OpenWithApp('Visual Studio Code', 'C:/Code.exe')],
          'QFileInfo': lambda path: path, 'DIAG': Mock()}
    fn = launcher_method('add_open_with_submenu', ns)
    owner = SimpleNamespace(file_icons=SimpleNamespace(icon=lambda path: path),
                            open_file_with_selected_app=lambda *args: opened.append(args),
                            perform_filesystem_context_action=lambda *args: chooser.append(args))
    menu = Menu()
    submenu = fn(owner, menu, 'プログラムから開く…', 'C:/work/setting.json')
    assert menu.rows[0][1] == 'プログラムから開く'
    assert submenu.rows[0][1].title == 'Cursor'
    assert submenu.rows[1][1].title == 'Visual Studio Code'
    assert submenu.rows[-1][1].title == '別のプログラムを選択…'
    submenu.rows[0][1].callback(True)
    submenu.rows[-1][1].callback(True)
    assert opened == [('C:/work/setting.json', 'C:/Cursor.exe')]
    assert chooser == [('open_with', 'C:/work/setting.json', 'file')]


def test_delete_key_uses_existing_single_and_multi_recycle_paths(tmp_path):
    class State: EditingState = 123
    class View:
        def __init__(self, paths):
            self.middle = SimpleNamespace(tree=SimpleNamespace(state=lambda: 1))
            self.paths = paths
        def isVisible(self): return True
        def middle_selected_paths(self): return self.paths
    fn = launcher_method('delete_expanded_selected_paths',
                         {'QAbstractItemView': SimpleNamespace(State=State), 'Path': Path})
    a = tmp_path / 'a.txt'
    b = tmp_path / 'folder'
    a.write_text('a')
    b.mkdir()
    events=[]
    obj = SimpleNamespace(expanded_view=View([str(a)]),
                          perform_filesystem_context_action=lambda *args: events.append(('single', args)),
                          perform_filesystem_batch_action=lambda *args: events.append(('batch', args)))
    assert fn(obj) is True
    assert events == [('single', ('delete', str(a), 'file'))]
    obj.expanded_view.paths = [str(a), str(b)]
    assert fn(obj) is True
    assert events[-1] == ('batch', ('delete', [str(a), str(b)]))
    obj.expanded_view.paths = []
    assert fn(obj) is False
    obj.expanded_view.paths = [str(a)]
    obj.expanded_view.middle.tree.state = lambda: 123
    assert fn(obj) is False
    assert len(events) == 2


def test_source_exposes_key_only_in_real_filesystem_contexts():
    text = APP.read_text(encoding='utf-8')
    assert "key == getattr(Qt.Key, 'Key_Delete', None) and pane is view.middle" in text
    assert "self.delete_expanded_selected_paths()" in text
    assert "self.perform_filesystem_context_action('delete', path, kind)" in text
