"""New embedded Files Exp first-column contract; no Qt installation needed."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1] / 'src'
APP = (ROOT / 'app.py').read_text('utf-8')
VIEW = (ROOT / 'expanded_view.py').read_text('utf-8')
REMOTE = (ROOT / 'launch_remote.py').read_text('utf-8')
TREE = (ROOT / 'remote_files_explorer.py').read_text('utf-8')


def method(src, owner, name):
    cls = next(c for c in ast.parse(src).body if isinstance(c, ast.ClassDef) and c.name == owner)
    func = next(f for f in cls.body if isinstance(f, ast.FunctionDef) and f.name == name)
    scope = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[func], type_ignores=[])), 'isolated', 'exec'),scope)
    return scope[name]


class W:
    def __init__(self, visible=False):
        self.visible = visible
        self.calls = []
    def isVisible(self): return self.visible
    def setVisible(self, v): self.visible = bool(v); self.calls.append(bool(v))
    def show(self): self.setVisible(True)
    def hide(self): self.setVisible(False)
    def style(self): return NS(unpolish=lambda *a:None, polish=lambda *a:None)
    def viewport(self): return NS(update=lambda:None)
    def setProperty(self, *a): pass


class Settings:
    def __init__(self): self.values = {}
    def setValue(self, key, val): self.values[key] = val
    def value(self, key, default=None): return self.values.get(key, default)
    def sync(self): pass


def test_embedded_instantiates_exact_existing_exp_component():
    assert 'RemoteFilesExplorer(' in VIEW
    assert 'None, launcher.color_theme, launcher=launcher, embedded=True' in VIEW
    assert 'self.left.layout_box.addWidget(self.embedded_files_exp, 1)' in VIEW
    assert 'self.left.tree.setVisible(not embedded)' in VIEW
    assert 'self.left.header.setVisible(not embedded)' in VIEW
    assert 'self.files_splitter.addWidget(self.middle)' in VIEW
    assert 'self.embedded_files_exp.folder_selected.connect(' in VIEW
    assert 'launcher.navigate_files_exp_folder' in VIEW
    assert 'launcher.show_files_exp_folder_menu' in VIEW
    assert 'launcher.on_files_exp_folder_renamed' in VIEW


def test_mode_switch_preserves_old_tree_and_replaces_only_content():
    settings=Settings()
    launcher=NS(files_root_hidden_mode=True, files_exp_embedded_mode=True,
                _remote_area=None,settings=settings)
    left=W(True);left.tree=W(True);left.header=W(True)
    middle=W(True); middle.tree=W(True)
    exp=W(False)
    splitter=NS(sizes=lambda:[310,690], setSizes=lambda value:None)
    saved=[]
    view=NS(launcher=launcher, left=left, middle=middle,
            embedded_files_exp=exp, right=W(False),
            files_splitter=splitter, _workspace_mode='files',
            _embedded_files_exp_roots_ready=True,
            _browser_bookmarks_visible=True,
            set_browser_bookmarks_visible=lambda val,persist=False:saved.append((val,persist)))
    apply=method(VIEW,'ExpandedLauncherView','apply_files_root_hidden_mode')
    apply(view)
    assert left.isVisible() and exp.isVisible()
    assert not left.tree.isVisible() and not left.header.isVisible()
    assert launcher._remote_area=='directory'
    assert saved == [(False, False)]
    launcher.files_exp_embedded_mode=False
    launcher.files_root_hidden_mode=False
    apply(view)
    assert left.isVisible() and left.tree.isVisible() and left.header.isVisible()
    assert not exp.isVisible()
    assert saved[-1] == (True,False)


def test_embedded_widths_never_override_old_files_widths():
    settings=Settings()
    launcher=NS(settings=settings, files_root_hidden_mode=True, files_exp_embedded_mode=True)
    splitter=NS(sizes=lambda:[250,750])
    view=NS(launcher=launcher,files_splitter=splitter,_workspace_mode='files')
    save=method(VIEW,'ExpandedLauncherView','save_splitter_sizes')
    save(view)
    assert settings.values == {'workspace_files_exp_embedded_splitter_sizes':'250|750'}
    launcher.files_exp_embedded_mode=False
    save(view)
    assert settings.values == {'workspace_files_exp_embedded_splitter_sizes':'250|750'}


def test_embedded_mode_prevents_remote_companion_window_and_keeps_folder_sync():
    assert 'if not self.files_exp_embedded_mode:' in APP
    assert 'self.remote_window.toggle_files_exp()' in APP
    assert 'if getattr(launcher, \'files_exp_embedded_mode\', False):' in REMOTE
    assert 'view.embedded_files_exp.tree.setFocus(' in REMOTE
    assert 'embedded.sync_current_directory(directory)' in APP
    assert 'for panel in panels:' in APP
    assert 'panel.refresh_directory_branch(str(folder))' in APP


def test_fixed_embedded_exp_keeps_tree_state_without_obsolete_toggle():
    assert 'self.files_exp_embedded_mode = True' in APP
    assert "'実験：Files Expを第1列に表示'" not in APP
    assert 'self.files_exp_embedded_action.setChecked(' not in APP
    assert "'files_exp_embedded/tree_state_v1'" in TREE
    assert "'remote_files_exp/tree_state_v1'" in TREE
    assert 'def reset_to_roots' in TREE
    assert 'def refresh_directory_branch' in TREE
    assert 'self.embedded_files_exp.show()' in VIEW


def test_embedded_tree_cannot_write_remote_window_position_or_size():
    assert 'if not self._embedded:' in TREE
    assert 'and not getattr(self, \'_embedded\', False)' in TREE
    assert 'self._launcher' in TREE
