"""Inline rename contract; pure filesystem and isolated callback tests."""
import ast
from pathlib import Path
from types import SimpleNamespace
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from context_menu_actions import rename_file_or_folder
from context_menu_resolver import resolve_context_target

VIEW = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')


def isolated(name):
    root = ast.parse(VIEW)
    owner = next(n for n in root.body if isinstance(n, ast.ClassDef)
                 and n.name == 'ExpandedLauncherView')
    method = next(n for n in owner.body if isinstance(n, ast.FunctionDef)
                  and n.name == name)
    module = ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))
    scope = dict(Path=Path, resolve_context_target=resolve_context_target,
                 rename_file_or_folder=rename_file_or_folder,
                 QTimer=SimpleNamespace(singleShot=lambda delay, fn: fn()))
    exec(compile(module, '<isolated>', 'exec'), scope)
    return scope[name]


def test_inline_rename_file_commits_on_grid_change(tmp_path):
    source = tmp_path / '004.txt'
    source.write_text('contents')
    row = {'_file': str(source), 'title': '004.txt', 'item_kind': 'command'}
    class Item:
        def text(self, index): return '005.txt'
    refreshed = []
    launcher = SimpleNamespace(authored_items=(), footer=SimpleNamespace(setText=lambda x:None))
    view = SimpleNamespace(row_data=lambda _: row, launcher=launcher,
                           refresh_middle=lambda:refreshed.append(True))
    isolated('finish_inline_rename')(view, Item(), 0)
    assert not source.exists()
    assert (tmp_path / '005.txt').read_text() == 'contents'
    assert refreshed == [True]


def test_inline_rename_folder_commits_without_copy(tmp_path):
    source = tmp_path / 'folder'
    source.mkdir(); (source / 'sample.txt').write_text('contents')
    row = {'_file': str(source), 'title': 'folder', 'item_kind': 'directory'}
    launcher = SimpleNamespace(authored_items=(), footer=SimpleNamespace(setText=lambda x:None))
    view = SimpleNamespace(row_data=lambda _: row, launcher=launcher,
                           refresh_middle=lambda:None)
    isolated('finish_inline_rename')(view, SimpleNamespace(text=lambda _: 'renamed'), 0)
    assert (tmp_path / 'renamed' / 'sample.txt').read_text() == 'contents'


def test_inline_wiring_and_folder_navigation_contract():
    assert 'self.middle.tree.setEditTriggers(QAbstractItemView.EditTrigger.SelectedClicked)' in VIEW
    assert 'self.middle.tree.itemChanged.connect(self.finish_inline_rename)' in VIEW
    assert 'self.middle.tree.itemClicked.connect(self.choose_middle)' in VIEW
    assert 'self.begin_context_inline_rename(i)' in VIEW
    assert "self.paste_button.setText('📋貼り付け')" in VIEW
    assert "QTimer.singleShot(650, self._finish_batch_delete_guard)" in APP
