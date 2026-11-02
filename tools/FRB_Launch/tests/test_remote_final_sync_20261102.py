"""Headless regression checks for the seven 2026-11-02 Remote/Files Exp improvements.

PySide6 is Windows-only for the user's deployment; methods using real Qt
are additionally checked in Windows UI acceptance tests, not claimed here.
"""
import ast
import ntpath
from pathlib import Path
from types import SimpleNamespace as NS

BASE = Path(__file__).resolve().parents[1] / 'src'
APP = (BASE / 'app.py').read_text(encoding='utf-8')
EXP = (BASE / 'remote_files_explorer.py').read_text(encoding='utf-8')
REMOTE = (BASE / 'launch_remote.py').read_text(encoding='utf-8')
VIEW = (BASE / 'expanded_view.py').read_text(encoding='utf-8')


def standalone_method(source, klass, name, namespace):
    tree = ast.parse(source)
    cl = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == klass)
    node = next(n for n in cl.body if isinstance(n, ast.FunctionDef) and n.name == name)
    node.decorator_list = []
    unit = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(unit)
    exec(compile(unit, f'<{klass}.{name}>', 'exec'), namespace)
    return namespace[name]


def test_first_column_tracks_longest_registered_root_without_second_background():
    rows = [ {'launch_browse_target': r'F:\\FRB', 'item_kind':'directory'},
             {'launch_browse_target': r'F:\\FRB\\tools', 'item_kind':'directory'},
             {'launch_browse_target': r'C:\\Downloads', 'item_kind':'directory'}]
    items = [NS(row=row) for row in rows]
    class FakeTree:
        def __init__(self):
            self.current = items[0]
            self.properties = {'remoteInactive': False}
            self.st = NS(unpolish=lambda *_:None, polish=lambda *_:None)
            self.vp = NS(update=lambda:None)
        def topLevelItemCount(self): return len(items)
        def topLevelItem(self, i): return items[i]
        def currentItem(self): return self.current
        def setCurrentItem(self, item): self.current = item
        def property(self, name): return self.properties.get(name)
        def setProperty(self, name, value): self.properties[name] = value
        def style(self): return self.st
        def viewport(self): return self.vp
    tree = FakeTree()
    view = NS(_workspace_mode='files', left=NS(tree=tree), row_data=lambda item:item.row)
    ctx = NS(expanded_view=view, expander=lambda:NS(expand=lambda raw:raw))
    sync = standalone_method(APP, 'Launcher', 'sync_files_first_column_root', {
        'row_directory': lambda r,expand:expand(r['path']) if r.get('item_kind') == 'directory' else None,
        '__import__': __import__,
    })
    # Function imports directory_address; use its actual pure implementation.
    assert sync(ctx, r'F:\\FRB\\tools\\scripts') is True
    assert tree.current is items[1]
    assert tree.properties['remoteInactive'] is True
    assert sync(ctx, r'C:\\Downloads\\2026') is True
    assert tree.current is items[2]
    # A path not beneath any authored shortcut cannot overwrite the root marker.
    assert sync(ctx, r'X:\\unregistered') is False
    assert tree.current is items[2]


def test_mutation_notification_reloads_only_existing_target_parents(tmp_path):
    parent = tmp_path / 'root'
    parent.mkdir()
    calls=[]
    panel = NS(isVisible=lambda:True, refresh_directory_branch=lambda p:calls.append(p))
    ctx = NS(remote_window=NS(files_exp_panel=panel))
    notify = standalone_method(APP, 'Launcher', 'notify_folder_mutation', {'Path':Path, 'path_key':lambda p:str(p).casefold()})
    notify(ctx, parent, parent, parent / 'deleted-child')
    assert calls == [str(parent)]


def test_rename_closes_popup_before_inline_editor_gets_focus():
    events=[]
    queue=[]
    class Timer:
        @staticmethod
        def singleShot(ms, callback):
            assert ms == 0
            queue.append(callback)
    method = standalone_method(APP, 'Launcher', 'begin_remote_rename_after_menu', {'QTimer':Timer})
    ctx = NS(close_finished_file_context_menus=lambda:events.append('close'),
             rename_remote_folder=lambda name:events.append(('edit',name)))
    method(ctx, 'folder')
    assert events == ['close']
    assert len(queue)==1
    queue.pop(0)()
    assert events == ['close', ('edit','folder')]


def test_menu_hover_dismissal_and_shared_width_contract():
    assert "def mouseMoveEvent(self, event):" in APP
    assert "action is not getattr(self, 'folder_list_action', None)" in APP
    assert 'child.close()' in APP
    assert "menu.setMinimumWidth(218)" in APP
    assert "menu.setMaximumWidth(225)" in APP
    assert 'begin_remote_rename_after_menu(p)' in APP


def test_folder_mutation_paths_update_open_exp_branches():
    assert 'self.launcher.notify_folder_mutation(current)' in VIEW  # creation
    assert 'self.launcher.notify_folder_mutation(old_path.parent)' in VIEW  # rename
    assert 'notify(parent)' in APP  # after deletion
    assert 'panel.reflect_external_folder_rename(str(path), str(new_path))' in APP
    assert 'self.notify_folder_mutation(Path(old_path).parent)' in APP or "notify(Path(old_path).parent)" in APP
    assert 'panel.refresh_directory_branch(str(folder))' in APP


def test_cut_visuals_use_same_source_and_pc_icon_is_unchanged():
    assert "'item_kind': 'directory', 'icon_key': 'folder.yellow'" in EXP
    assert 'SP_ComputerIcon' in EXP
    assert "if state == 'cut'" in EXP
    assert 'QApplication.clipboard().dataChanged.connect(self.refresh_main_files_cut_visuals)' in APP
    assert 'CascadeMenu._subdued_icon(base)' in APP


def test_remote_blank_single_click_and_double_click_are_independent():
    assert "self.command.emit('REMOTE_FOLDER_DESELECT')" in REMOTE
    assert 'self._skip_release_after_double = True' in REMOTE
    assert 'self._single_click_timer.stop()' in REMOTE
    assert "if command == 'REMOTE_FOLDER_DESELECT':" in APP
    assert 'tree.deliberate_blank_selection = True' in APP
    assert 'tree.clearSelection()' in APP
