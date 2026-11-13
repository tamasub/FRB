"""2026-11-02: shared '最新の情報に更新', clipboard finish and focused new row.

Portable behavior checks: no PySide6 / Windows shell is required.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

from context_menu_config import load_context_menus

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
VIEW = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
EXP = (ROOT / 'src/remote_files_explorer.py').read_text(encoding='utf-8')


def isolated(source, cls, name, namespace):
    tree = ast.parse(source)
    node = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == cls)
    fn = next(x for x in node.body if isinstance(x, ast.FunctionDef) and x.name == name)
    scope = dict(namespace)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 '<isolated>', 'exec'), scope)
    return scope[name]


def test_shared_folder_menu_declares_exact_requested_label():
    menus = load_context_menus(ROOT / 'config/context_menu_options.json')
    items = [(x['action_id'],x['title']) for x in menus['folder'] if x.get('action_id')]
    assert items[0:4] == [('copy','コピー'),('cut','切り取り'),
                          ('paste','貼り付け'),('refresh_directory','最新の情報に更新')]
    assert sum(key == 'refresh_directory' for key, _ in items) == 1


def test_shared_refresh_reloads_exp_and_main_only_within_target(tmp_path):
    folder = tmp_path/'parent'; child = folder/'child'; child.mkdir(parents=True)
    unrelated = tmp_path/'elsewhere'; unrelated.mkdir()
    events = []
    panel = NS(refresh_directory_branch=lambda path: events.append(('exp',path)))
    view = NS(isVisible=lambda: True, current_directory=lambda: str(child),
              refresh_middle=lambda: events.append(('middle',)))
    owner = NS(remote_window=NS(files_exp_panel=panel), expanded_view=view,
               refresh_files_exp_directory=lambda path:events.append(('exp',str(path))),
               _directory_menu_for_path=lambda p:None,
               footer=NS(setText=lambda txt:events.append(('text',txt))), error=Mock())
    fn = isolated(APP, 'Launcher','refresh_folder_information',{
        'Path':Path, 'path_key':lambda p:str(p).lower(),
        'QTimer':NS(singleShot=lambda ms,callback:callback())})
    assert fn(owner, folder) is True
    assert ('exp',str(folder)) in events and ('middle',) in events
    events.clear()
    assert fn(owner,unrelated) is True
    assert events[0] == ('exp',str(unrelated))
    assert ('middle',) not in events
    assert fn(owner, tmp_path/'missing') is False
    owner.error.assert_called_once()


def test_clipboard_copy_cut_close_remote_context_after_setting_mime(tmp_path):
    f = tmp_path/'one.md'; f.write_text('hello', encoding='utf-8')
    class Mime:
        def __init__(self): self.meta={}
        def setUrls(self,urls): self.urls=urls
        def setData(self,k,v): self.meta[k]=v
    class App:
        _cb = NS(setMimeData=Mock())
        @staticmethod
        def clipboard(): return App._cb
    menu = NS(close=Mock())
    closes=[]
    owner = NS(footer=NS(setText=Mock()), error=Mock(),
               _launch_context_menu=menu,
               _remote_folder_opener=object(),
               close_remote_folder_menu=lambda:closes.append(True),
               can_delete_remote_folder=lambda path:True)
    fn = isolated(APP,'Launcher','perform_filesystem_context_action',{
        'Path':Path,'QMimeData':Mime,
        'QUrl':NS(fromLocalFile=lambda p:p), 'QApplication':App,
        'QTimer':NS(singleShot=lambda ms, cb:cb()), 'DIAG':Mock()})
    for operation, effect in [('copy',1),('cut',2)]:
        fn(owner,operation,str(f),'file')
        assert int.from_bytes(next(iter(App._cb.setMimeData.call_args.args[0].meta.values())),
                              'little') == effect
    assert menu.close.call_count == 2
    assert len(closes)==2
    owner.error.assert_not_called()


def test_files_exp_refresh_is_independent_of_home_reset_and_preserves_open_nodes():
    assert 'def refresh_directory_branch(' in EXP
    branch = EXP.split('    def refresh_directory_branch(',1)[1].split('    def reset_to_roots(',1)[0]
    assert 'self.set_roots(' not in branch  # HOME is the only all-collapsed reset
    assert 'self.tree.isExpanded(' in branch
    assert 'self.tree.setExpanded(' in branch
    assert 'self._syncing_directory = True' in branch
    assert 'restore_current' in branch
    assert 'self._expand_index(' in branch


def test_both_paste_routes_refresh_exp_and_keep_destination():
    assert 'self.refresh_files_exp_directory(destination)' in APP.split(
        '    def paste_into_directory(',1)[1].split('    def _directory_menu_for_path(',1)[0]
    assert 'self.refresh_files_exp_directory(destination)' in APP.split(
        '    def paste_into_expanded_directory(',1)[1].split('    def extract_all_zip(',1)[0]
    assert 'self.select_created_middle_item(created)' in VIEW
    assert 'self._middle_current_memory = (self.current_directory(), key)' in VIEW


def test_real_refresh_branch_algorithm_keeps_expanded_folders_and_new_children(tmp_path):
    """Run the real Files Exp refresh method with a minimal Qt-free tree model."""
    import os
    root = tmp_path/'root'; root.mkdir()
    nested = root/'nested'; nested.mkdir()
    (nested/'original').mkdir()
    other = tmp_path/'other'; other.mkdir()

    DATA, LOADED = 41, 42
    class Item:
        def __init__(self, text=''):
            self.text = text; self.parent = None; self.children=[]; self.roles={}
        def data(self, role): return self.roles.get(role)
        def setData(self, value, role): self.roles[role]=value
        def appendRow(self, child): child.parent=self;self.children.append(child)
        def removeRow(self, row): self.children.pop(row)
        def removeRows(self, start, count): del self.children[start:start+count]
        def rowCount(self): return len(self.children)
        def child(self, row): return self.children[row]
        def index(self): return self
    class Model:
        def __init__(self): self.root=Item()
        def invisibleRootItem(self):return self.root
    class Bar:
        def __init__(self):self.position=11
        def value(self):return self.position
        def maximum(self):return 50
        def setValue(self,val):self.position=val
    class Tree:
        def __init__(self):self.open=set();self.current=None;self.bar=Bar()
        def isExpanded(self,index):return id(index) in self.open
        def setExpanded(self,index,value):
            if value:self.open.add(id(index))
            else:self.open.discard(id(index))
        def verticalScrollBar(self):return self.bar
        def currentIndex(self):return self.current
        def setCurrentIndex(self,index):self.current=index
        def clear_wheel_pending(self):pass
    model=Model(); tree=Tree()
    for path in [root,other]:
        node=Item(path.name); node.setData({'path':str(path),'pc':False},DATA)
        node.setData(False,LOADED);node.appendRow(Item('placeholder'))
        model.root.appendRow(node)
    first,second=model.root.children
    def expand(item):
        if item.data(LOADED):return
        item.setData(True,LOADED)
        children=sorted(x for x in Path(item.data(DATA)['path']).iterdir() if x.is_dir())
        for path in children:
            child=Item(path.name);child.setData({'path':str(path),'pc':False},DATA)
            child.setData(False,LOADED);child.appendRow(Item('placeholder'))
            item.appendRow(child)
        item.removeRow(0)
    expand(first);nested_item=first.child(0);expand(nested_item)
    tree.setExpanded(first,True);tree.setExpanded(nested_item,True)
    original=nested_item.child(0);tree.current=original
    selected=str(original.data(DATA)['path'])
    exp=NS(model=model,tree=tree,_selection_timer=NS(stop=lambda:None),
           _syncing_directory=False, _expand_index=expand,
           _index_path=lambda index: (index.data(DATA) or {}).get('path') if index else None,
           refresh_transfer_visuals=lambda:None)
    (nested/'added_later').mkdir()
    method=isolated(EXP,'RemoteFilesExplorer','refresh_directory_branch',{
        'os':os,'Path':Path,'QStandardItem':Item,
        '_DATA_ROLE':DATA,'_LOADED_ROLE':LOADED})
    assert method(exp,str(root))
    assert first.child(0).data(DATA)['path'] == str(nested)
    restored_nested=first.child(0)
    assert tree.isExpanded(first) and tree.isExpanded(restored_nested)
    assert sorted(restored_nested.child(i).text for i in range(restored_nested.rowCount())) == [
        'added_later', 'original']
    assert tree.current.data(DATA)['path'] == selected
    assert second is model.root.child(1)  # unrelated root not rebuilt
    assert tree.bar.position == 11
    assert not exp._syncing_directory
