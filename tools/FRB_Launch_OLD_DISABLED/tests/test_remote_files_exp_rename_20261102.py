"""Exercise filesystem rename without requiring PySide6 on non-Windows CI."""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace
import textwrap

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))
from context_menu_actions import rename_file_or_folder

CODE = (SRC / 'remote_files_explorer.py').read_text('utf-8')
LAUNCHER = (SRC / 'app.py').read_text('utf-8')
REMOTE = (SRC / 'launch_remote.py').read_text('utf-8')
VIEW = (SRC / 'expanded_view.py').read_text('utf-8')


def _method(name):
    cls = next(n for n in ast.parse(CODE).body
               if isinstance(n, ast.ClassDef) and n.name == 'RemoteFilesExplorer')
    method = next(n for n in cls.body
                  if isinstance(n, ast.FunctionDef) and n.name == name)
    text = ast.get_source_segment(CODE, method)
    ns = {'Path': Path, 'rename_file_or_folder': rename_file_or_folder,
          'os': __import__('os'), '_DATA_ROLE': 257}
    exec(textwrap.dedent(text), ns)
    return ns[name]


class Item:
    def __init__(self, label, path):
        self.name = label
        self.data_value = {'path': path, 'pc': False}
        self.children = []
        self.editable = True

    def text(self):
        return self.name

    def setText(self, text):
        self.name = text

    def setEditable(self, value):
        self.editable = value

    def data(self, role):
        return self.data_value

    def setData(self, value, role):
        self.data_value = value

    def setToolTip(self, value):
        self.tip = value

    def rowCount(self):
        return len(self.children)

    def child(self, index):
        return self.children[index]


class Panel:
    _rewrite_child_paths = _method('_rewrite_child_paths')
    _finish_folder_rename = _method('_finish_folder_rename')

    def __init__(self):
        self._rename_in_progress = None
        self._selection_timer = SimpleNamespace(stop=lambda: None)
        self.emitted = []
        self.folder_renamed = SimpleNamespace(emit=lambda *args: self.emitted.append(args))
        self.errors = []

    def parentWidget(self):
        return SimpleNamespace(parent=lambda: SimpleNamespace(
            error=lambda value: self.errors.append(value)))


def test_child_folder_rename_updates_tree_descendants(tmp_path):
    root = tmp_path / 'parent'
    root.mkdir()
    old = root / 'old'
    child = old / 'child'
    child.mkdir(parents=True)
    item = Item('new', str(old))
    item.children.append(Item('child', str(child)))
    panel = Panel()
    panel._rename_in_progress = (item, str(old))
    panel._finish_folder_rename(item)
    assert not old.exists()
    assert (root / 'new' / 'child').is_dir()
    assert item.data_value['path'] == str(root / 'new')
    assert item.children[0].data_value['path'] == str(root / 'new' / 'child')
    assert panel.emitted == [(str(old), str(root / 'new'))]
    assert panel.errors == []
    assert not item.editable


def test_rename_collision_restores_ui_and_never_emits_navigation(tmp_path):
    root = tmp_path / 'parent'
    root.mkdir()
    old = root / 'old'
    old.mkdir()
    (root / 'taken').mkdir()
    item = Item('taken', str(old))
    panel = Panel()
    panel._rename_in_progress = (item, str(old))
    panel._finish_folder_rename(item)
    assert old.is_dir() and (root / 'taken').is_dir()
    assert item.text() == 'old'
    assert panel.emitted == []
    assert '名前を変更できませんでした:' in panel.errors[0]


def test_menu_uses_shared_context_with_inline_rename_for_files_exp():
    assert 'files_exp_rename_target=None' in LAUNCHER
    assert 'files_exp_rename_target=str(directory)' in LAUNCHER
    assert "folder_actions.add('rename')" in LAUNCHER
    assert 'panel.begin_folder_rename(directory)' in LAUNCHER
    assert 'self.navigate_files_exp_folder(new_path)' in LAUNCHER
    assert 'files_exp_folder_renamed.connect(self.on_files_exp_folder_renamed)' in LAUNCHER
    assert 'folder_renamed.connect(self.files_exp_folder_renamed.emit)' in REMOTE
    assert 'self.tree.setIndentation(18)' in CODE
    assert 'if self._index_path(root) == path:' in CODE  # protect shortcut roots


def test_sort_integration_reads_on_folder_change_and_writes_only_override():
    assert 'load_directory_sort(' in VIEW
    assert 'save_directory_sort(' in VIEW
    assert 'folder != self._middle_sort_directory' in VIEW
    assert "self._middle_sort_mode = DEFAULT_SORT" in VIEW


def test_app_rename_commit_updates_breadcrumb_and_carries_folder_sort(tmp_path):
    import folder_sort_preferences
    import middle_folder_filter
    ns = {'Path': Path, 'QTimer': SimpleNamespace(singleShot=lambda ms, f: f())}
    cls = next(n for n in ast.parse(LAUNCHER).body
               if isinstance(n, ast.ClassDef) and
               any(isinstance(n, ast.FunctionDef) and n.name == 'on_files_exp_folder_renamed'
                   for n in n.body))
    function = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'on_files_exp_folder_renamed')
    exec(textwrap.dedent(ast.get_source_segment(LAUNCHER, function)), ns)
    class Settings:
        def __init__(self):
            self.values = {}
        def value(self, key, default=None):
            return self.values.get(key, default)
        def setValue(self, key, value):
            self.values[key] = value
        def remove(self, key):
            self.values.pop(key, None)
    settings = Settings()
    old = tmp_path / 'old'
    new = tmp_path / 'new'
    new.mkdir()
    folder_sort_preferences.save_directory_sort(
        settings, str(old), 'date_desc', middle_folder_filter.SORT_LABELS)
    navigated = []
    footer = SimpleNamespace(setText=lambda text: navigated.append(('footer', text)))
    obj = SimpleNamespace(settings=settings, file_index_settings={'enabled': False},
                          file_index_busy=False, footer=footer,
                          navigate_files_exp_folder=lambda path: navigated.append(path) or True)
    assert ns['on_files_exp_folder_renamed'](obj, str(old), str(new)) is True
    assert str(new) in navigated
    assert folder_sort_preferences.load_directory_sort(
        settings, str(new), middle_folder_filter.SORT_LABELS) == 'date_desc'
