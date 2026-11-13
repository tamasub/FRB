"""Contract tests for the Nov 2 PC/menu synchronization fixes; no Qt needed."""
import ast
from pathlib import Path
from types import SimpleNamespace
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from system_drives import drive_rows, pc_preview_row, drive_display_name
from middle_folder_filter import filter_sort_folder_rows

APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
REMOTE = (ROOT / 'src/launch_remote.py').read_text(encoding='utf-8')
EXP = (ROOT / 'src/remote_files_explorer.py').read_text(encoding='utf-8')


def extract_class_method(source, cls_name, name, env=None):
    module = ast.parse(source)
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == cls_name)
    method = next(n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)
    namespace = {} if env is None else dict(env)
    exec(compile(ast.Module(body=[method], type_ignores=[]), '<source>', 'exec'), namespace)
    return namespace[name]


def test_pc_drive_titles_keep_volume_label_and_letter_after_middle_filter():
    original = drive_rows(roots=['C:\\', 'F:\\'], get_label=lambda root: {'C:\\': 'Windows', 'F:\\': 'FRB'}[root])
    entries = filter_sort_folder_rows(original)
    assert [row['title'] for row in entries] == ['FRB (F:)', 'Windows (C:)']
    assert all(row['_system_drive'] and row['title'] for row in entries)
    assert pc_preview_row({'item_kind':'command', 'title':'PC', 'launch_actions':[
        {'launch_action_type':'Open','launch_target':'shell:mycomputerfolder'}]})['_system_drives_root']


def test_pc_icon_uses_exact_files_exp_native_computer_symbol():
    assert 'self._pc_icon = style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)' in EXP
    fn = extract_class_method(APP, 'Launcher', 'row_icon', {'QApplication': SimpleNamespace(
        style=lambda: SimpleNamespace(standardIcon=lambda symbol: ('native-icon', symbol))),
        'QStyle': SimpleNamespace(StandardPixmap=SimpleNamespace(SP_ComputerIcon='pc-icon')),
        'icon_lookup': lambda _: (_ for _ in ()).throw(AssertionError('PC must not use folder icon'))})
    assert fn(SimpleNamespace(), {'_system_drives_root': True}) == ('native-icon', 'pc-icon')


def test_pc_click_emits_distinct_virtual_root_event():
    assert 'pc_selected = Signal()' in EXP
    assert 'files_exp_pc_selected = Signal()' in REMOTE
    assert "pc_signal = getattr(self.files_exp_panel, 'pc_selected', None)" in REMOTE
    assert 'pc_signal.connect(self.files_exp_pc_selected.emit)' in REMOTE
    assert 'self.remote_window.files_exp_pc_selected.connect(self.navigate_files_exp_pc)' in APP
    calls=[]
    fn=extract_class_method(EXP, 'RemoteFilesExplorer', '_activate_index')
    obj=SimpleNamespace(_syncing_directory=False,
        _selection_timer=SimpleNamespace(stop=lambda:None),
        _is_pc_index=lambda index: True,
        pc_selected=SimpleNamespace(emit=lambda:calls.append('PC')),
        folder_selected=SimpleNamespace(emit=lambda path:calls.append(path)))
    assert fn(obj, object()) is None
    assert calls == ['PC']


def test_pc_click_reselects_launch_first_column_without_fake_path():
    fn=extract_class_method(APP, 'Launcher', 'navigate_files_exp_pc')
    class Tree:
        def __init__(self): self.items=[{'item_id':'normal'}, {'_system_drives_root':True, 'title':'PC'}];self.selected=None
        def topLevelItemCount(self): return len(self.items)
        def topLevelItem(self,i): return self.items[i]
        def setCurrentItem(self,item):self.selected=item
    class Pane:
        def __init__(self):
            self.tree=SimpleNamespace(remote_highlight_mode=False,
                remote_logical_active=False, setProperty=lambda *args: None,
                style=lambda:SimpleNamespace(unpolish=lambda x:None, polish=lambda x:None),
                viewport=lambda:SimpleNamespace(update=lambda:None))
    tree=Tree();left=Pane();left.tree=tree
    # Real tree uses the same style/property/viewport methods on QTreeWidget.
    tree.setProperty=lambda *args:None
    tree.style=lambda:SimpleNamespace(unpolish=lambda x:None,polish=lambda x:None)
    tree.viewport=lambda:SimpleNamespace(update=lambda:None)
    middle=Pane();record=[]
    view=SimpleNamespace(isVisible=lambda:True, _workspace_mode='files',
        left=left,middle=middle,row_data=lambda item:item,
        choose_files=lambda item,col:record.append((item,col)))
    remote=SimpleNamespace(set_area=lambda area:record.append(('remote',area)))
    obj=SimpleNamespace(expanded_view=view, remote_window=remote)
    assert fn(obj) is True
    assert tree.selected == tree.items[1]
    assert record[0] == (tree.items[1],0)
    assert ('remote','files') in record
    assert obj._remote_area=='files'


def test_filesystem_context_width_is_consistent_for_file_folder_and_batch():
    fn=extract_class_method(APP, 'Launcher', 'show_launch_context_menu')
    code=ast.get_source_segment(APP, next(n for c in ast.parse(APP).body if isinstance(c,ast.ClassDef) and c.name=='Launcher' for n in c.body if isinstance(n,ast.FunctionDef) and n.name=='show_launch_context_menu'))
    assert code.count('menu.setMinimumWidth(218)') >= 3  # folder + file + batch
    assert code.count('menu.setMaximumWidth(225)') >= 3
    assert 'menu.setMinimumWidth(218)' in APP[APP.index('def show_expanded_background_paste_menu'):]


def test_cut_visuals_do_not_reset_uncut_row_foreground():
    method=next(n for c in ast.parse(APP).body if isinstance(c,ast.ClassDef) and c.name=='Launcher' for n in c.body if isinstance(n,ast.FunctionDef) and n.name=='refresh_main_files_cut_visuals')
    code=ast.get_source_segment(APP, method)
    assert "was_cut = bool(item.data(0, Qt.ItemDataRole.UserRole + 9))" in code
    assert 'elif was_cut:' in code
    assert "theme_palette(self.color_theme)['text']" in code
    assert 'item.setForeground(0, QBrush())' not in code
