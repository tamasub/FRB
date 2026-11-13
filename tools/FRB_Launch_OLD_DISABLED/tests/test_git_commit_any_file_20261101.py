"""Git commit message source can be any *file*, regardless of extension/location.

Isolated tests run actual Launcher methods without needing a Windows Qt runtime.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from context_menu_config import load_context_menus, visible_context_entries
from context_menu_resolver import resolve_context_target

SOURCE = (ROOT / 'src/app.py').read_text(encoding='utf-8')
LAUNCHER = next(n for n in ast.parse(SOURCE).body
                if isinstance(n, ast.ClassDef) and n.name == 'Launcher')


def method(name, scope):
    fn = next(n for n in LAUNCHER.body
              if isinstance(n, ast.FunctionDef) and n.name == name)
    module = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    exec(compile(module, '<actual Launcher method>', 'exec'), scope)
    return scope[name]


class Menu:
    def __init__(self, parent):
        self.entries = []
    def addAction(self, title, callback):
        self.entries.append((title, callback))
        return Mock()
    def addSeparator(self):
        self.entries.append(('---', None))
    def isEmpty(self):
        return not self.entries
    def popup(self, point):
        pass


def test_any_file_has_git_menu_in_files_pane():
    show = method('show_launch_context_menu', {
        'QMenu': Menu, 'Path': Path,
        'resolve_context_target': resolve_context_target,
        'load_context_menus': load_context_menus,
        'visible_context_entries': visible_context_entries,
        'CONTEXT_MENU_OPTIONS': ROOT / 'config/context_menu_options.json',
        'context_action_icon': lambda action: None,
    })
    # Different folders and extensions, including a file without an extension.
    for name in ('C:/Users/T/Downloads/latest.zip', 'D:/FRB/docs/記事.md',
                 'D:/FRB/src/test.js', 'D:/FRB/data/a.json',
                 'D:/FRB/README'):
        host = SimpleNamespace(
            data={'items': []}, selection=None, stack=[], authored_items=[],
            search=SimpleNamespace(text=lambda: ''),
            hover_timer=SimpleNamespace(stop=Mock()),
            _context_paste_enabled=Mock(return_value=False), _paste_from_context_menu=Mock(),
            perform_filesystem_context_action=Mock(),
            add_open_with_submenu=lambda menu, title, path: menu.addAction(title, lambda: None))
        assert show(host, (10, 10), {'_browse_file': name, 'item_kind': 'command'})
        items = dict(host._launch_context_menu.entries)
        assert 'ファイル名を使ってGitコミット' in items, name
        items['ファイル名を使ってGitコミット'](True)
        host.perform_filesystem_context_action.assert_called_once_with(
            'git_commit_from_zip', name, 'file')


def test_folder_has_no_git_menu():
    show = method('show_launch_context_menu', {
        'QMenu': Menu, 'Path': Path,
        'resolve_context_target': resolve_context_target,
        'load_context_menus': load_context_menus,
        'visible_context_entries': visible_context_entries,
        'CONTEXT_MENU_OPTIONS': ROOT / 'config/context_menu_options.json',
        'context_action_icon': lambda action: None,
    })
    host = SimpleNamespace(
        data={'items': []}, selection=None, stack=[], authored_items=[],
        search=SimpleNamespace(text=lambda: ''),
        hover_timer=SimpleNamespace(stop=Mock()),
        _context_paste_enabled=Mock(return_value=False), _paste_from_context_menu=Mock())
    assert show(host, (10, 10), {'_file': 'D:/FRB/docs', 'item_kind': 'directory'})
    assert 'ファイル名を使ってGitコミット' not in dict(host._launch_context_menu.entries)


class Dialog:
    DialogCode = SimpleNamespace(Accepted=1)
    def __init__(self, owner):
        self.owner = owner
    def setWindowTitle(self, title):
        pass
    def setMinimumWidth(self, width):
        pass
    def resize(self, width, height):
        pass
    def sizeHint(self):
        return SimpleNamespace(height=lambda: 200)
    def exec(self):
        return 1
    def accept(self):
        pass
    def reject(self):
        pass


class Layout:
    def __init__(self, parent):
        pass
    def setContentsMargins(self, *margins):
        pass
    def setSpacing(self, spacing):
        pass
    def addWidget(self, widget):
        pass


class LineEdit:
    messages = []
    def __init__(self, parent):
        self.value = ''
    def setText(self, value):
        self.value = value
        self.messages.append(value)
    def setMinimumWidth(self, width):
        pass
    def selectAll(self):
        pass
    def text(self):
        return self.value


class ButtonBox:
    StandardButton = SimpleNamespace(Ok=1, Cancel=2)
    def __init__(self, *args):
        self.accepted = SimpleNamespace(connect=lambda handler: None)
        self.rejected = SimpleNamespace(connect=lambda handler: None)


class MessageBox:
    Icon = SimpleNamespace(Question=1)
    StandardButton = SimpleNamespace(Yes=1, No=2)
    notices = []
    def __init__(self, parent):
        self.details = ''
    def setIcon(self, icon):
        pass
    def setWindowTitle(self, title):
        pass
    def setText(self, text):
        pass
    def setInformativeText(self, text):
        self.details = text
        MessageBox.notices.append(text)
    def setStandardButtons(self, buttons):
        pass
    def setDefaultButton(self, button):
        pass
    def exec(self):
        return self.StandardButton.Yes
    @staticmethod
    def information(*args):
        pass


@pytest.mark.parametrize('name', ['説明.md', 'code.js', 'config.json', 'backup.zip', 'README'])
def test_git_commit_uses_any_file_name_and_keeps_repo_scope(tmp_path, name):
    other = tmp_path / 'not Downloads'
    other.mkdir()
    selected = other / name
    selected.write_text('test', encoding='utf-8')
    commit = Mock(return_value='abc123 commit')
    preview = Mock(return_value={
        'repository': tmp_path / 'repo',
        'changes': [' M src/app.py'], 'include_untracked': True,
    })
    LineEdit.messages.clear()
    MessageBox.notices.clear()
    options = {'enabled': True, 'repository_path': str(tmp_path / 'repo')}
    git_method = method('git_commit_using_filename', {
        'Path': Path, 'read_git_commit_options': Mock(return_value=options),
        'git_commit_preview': preview, 'commit_tracked_changes': commit,
        'GIT_COMMIT_OPTIONS': tmp_path / 'config.json', 'QDialog': Dialog,
        'QVBoxLayout': Layout, 'QLabel': lambda label, dialog: label,
        'QLineEdit': LineEdit, 'QDialogButtonBox': ButtonBox,
        'QMessageBox': MessageBox, 'DIAG': SimpleNamespace(exception=Mock()),
        'subprocess': __import__('subprocess'),
    })
    host = SimpleNamespace(error=Mock())
    git_method(host, selected)
    host.error.assert_not_called()
    assert LineEdit.messages == [name]
    preview.assert_called_once_with(options)
    commit.assert_called_once_with(tmp_path / 'repo', name, include_untracked=True)
    assert 'コミット対象の限定・追加はしません' in MessageBox.notices[-1]


def test_non_file_is_rejected_before_commit_preview(tmp_path):
    preview = Mock()
    git_method = method('git_commit_using_filename', {
        'Path': Path, 'git_commit_preview': preview,
        'subprocess': __import__('subprocess'),
        'DIAG': SimpleNamespace(exception=Mock()),
    })
    host = SimpleNamespace(error=Mock())
    git_method(host, tmp_path)
    assert 'フォルダーは対象外' in host.error.call_args.args[0]
    preview.assert_not_called()
