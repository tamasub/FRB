"""Regression for Files Exp clipboard keyboard shortcuts and two-sided move sync.

All checks run without Qt/Windows; actual Windows key/focus integration remains
an end-user smoke test.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

from file_transfer_visual import moved_source_parent_directories, path_key
from clipboard_paste import make_paste_plan, paste_items

ROOT = Path(__file__).resolve().parents[1]
EXP = (ROOT/'src/remote_files_explorer.py').read_text(encoding='utf-8')
APP = (ROOT/'src/app.py').read_text(encoding='utf-8')


def method(source, cls, name, scope):
    node = next(x for x in ast.parse(source).body if isinstance(x, ast.ClassDef)
                and x.name == cls)
    func = next(x for x in node.body if isinstance(x, ast.FunctionDef)
                and x.name == name)
    namespace = dict(scope)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[func],type_ignores=[])),
                 '<isolated>', 'exec'), namespace)
    return namespace[name]


class Keys:
    Key_C, Key_X, Key_V, Key_Delete, Key_F2, Key_F5 = 1, 2, 3, 4, 5, 6


QT = NS(KeyboardModifier=NS(ControlModifier=1,NoModifier=0),Key=Keys)
VIEW = NS(State=NS(EditingState=18))


def setup_tree(tmp_path):
    chosen = tmp_path/'folder'; chosen.mkdir()
    events = []
    app = NS(paste_into_expanded_directory=lambda **kw: events.append(('paste',kw)),
             perform_filesystem_context_action=lambda *args: events.append(('action',args)),
             refresh_folder_information=lambda p: events.append(('refresh',p)))
    remote = NS(parent=lambda:app)
    tree = NS(state=lambda:0,currentIndex=lambda:'current')
    panel = NS(tree=tree,_rename_in_progress=None,
               _index_path=lambda index: str(chosen),
               parentWidget=lambda:remote,
               _selection_timer=NS(stop=lambda:events.append(('stop',))),
               begin_folder_rename=lambda p:events.append(('rename',p)) or True)
    return panel, chosen, events


def test_exp_shortcuts_share_context_actions_and_pin_explicit_destination(tmp_path):
    panel, chosen, events = setup_tree(tmp_path)
    handler = method(EXP,'RemoteFilesExplorer','handle_tree_shortcut',
                     {'Qt':QT,'QAbstractItemView':VIEW})
    assert handler(panel,Keys.Key_X,1)
    assert ('action',('cut',str(chosen),'folder')) in events
    assert handler(panel,Keys.Key_C,1)
    assert ('action',('copy',str(chosen),'folder')) in events
    assert handler(panel,Keys.Key_V,1)
    assert ('paste',{'destination_override':str(chosen)}) in events
    for k,expected in [(Keys.Key_Delete,('action',('delete',str(chosen),'folder'))),
                       (Keys.Key_F2,('rename',str(chosen))),
                       (Keys.Key_F5,('refresh',str(chosen)))]:
        assert handler(panel,k,0)
        assert expected in events


def test_shortcut_does_not_mutate_when_no_physical_folder_or_while_renaming(tmp_path):
    panel, folder, events = setup_tree(tmp_path)
    handler = method(EXP,'RemoteFilesExplorer','handle_tree_shortcut',
                     {'Qt':QT,'QAbstractItemView':VIEW})
    panel._index_path=lambda index:None
    assert not handler(panel,Keys.Key_X,1)
    assert not any(row[0]=='action' for row in events)
    panel._index_path=lambda index:str(folder)
    panel._rename_in_progress=object()
    assert not handler(panel,Keys.Key_X,1)
    assert not handler(panel,Keys.Key_V,1)
    panel._rename_in_progress=None
    panel.tree.state=lambda:18
    assert not handler(panel,Keys.Key_X,1)
    panel.tree.state=lambda:0
    assert not handler(panel,Keys.Key_X,3)  # Ctrl+Shift+X isn't Ctrl+X
    assert not any(row[0]=='action' for row in events)


def test_files_exp_tree_intercepts_shortcuts_before_default_qtreeview_behavior():
    tree = next(x for x in ast.parse(EXP).body if isinstance(x,ast.ClassDef)
                and x.name == 'FilesExpWheelTree')
    key_method = next(x for x in tree.body if isinstance(x,ast.FunctionDef)
                      and x.name == 'keyPressEvent')
    code = ast.get_source_segment(EXP,key_method)
    assert 'handle_tree_shortcut' in code
    assert 'event.accept()' in code
    assert 'super().keyPressEvent(event)' in code
    # Existing Files middle and cascade bindings remain in place.
    assert 'self.copy_expanded_selected_paths(cut=(key == Qt.Key.Key_X))' in APP
    assert 'cascade.handle_file_shortcut(k, event.modifiers())' in APP


def test_move_refreshes_exact_source_parents_and_destination(tmp_path):
    origin = tmp_path/'origin'; origin.mkdir()
    dest = tmp_path/'dest'; dest.mkdir()
    child = origin/'child'; child.mkdir()
    (child/'contents.txt').write_text('hello')
    original_plan = make_paste_plan(dest,[child],allow_existing=True)
    assert moved_source_parent_directories(original_plan,move=False)==()
    parents = moved_source_parent_directories(original_plan,move=True)
    assert parents==(str(origin),)
    # Actually move: no stale original, new child at target, no unrelated write.
    assert paste_items(original_plan,move=True) == 1
    assert not child.exists()
    assert (dest/'child'/'contents.txt').read_text()=='hello'
    # The shared move route reloads destination AND each distinct source
    # parent; copies do not touch their origins.
    expanded_route = method(APP,'Launcher','paste_into_expanded_directory',{})
    lines = ast.get_source_segment(APP,next(
        fn for node in ast.parse(APP).body if isinstance(node,ast.ClassDef)
        and node.name=='Launcher' for fn in node.body if isinstance(fn,ast.FunctionDef)
        and fn.name=='paste_into_expanded_directory'))
    assert 'self.refresh_files_exp_directory(destination)' in lines
    assert 'for source_parent in moved_from:' in lines
    assert 'path_key(source_parent) != path_key(destination)' in lines


def test_paste_feedback_expires_and_timer_restarts():
    fired=[]
    class Timer:
        def __init__(self,owner): self.stopped=0;self.started=[]
        def setSingleShot(self,value):self.single=value
        def start(self,ms):self.started.append(ms)
        def stop(self):self.stopped+=1
        timeout=NS(connect=lambda fn:None)
    remote_panel=NS(refresh_transfer_visuals=lambda:fired.append('repaint'))
    host=NS(remote_window=NS(files_exp_panel=remote_panel),menu=None,
            _latest_pasted_paths=())
    recorder=method(APP,'Launcher','_record_transfer_result',
                    {'pasted_paths_for':lambda p,n:[str(Path(p)/v) for v in n],
                     'QTimer':Timer})
    clear=method(APP,'Launcher','_clear_previous_paste_feedback',{})
    host._clear_previous_paste_feedback=lambda:clear(host)
    recorder(host,'/tmp/dest',['a','b'])
    recorder(host,'/tmp/dest',['c'])
    assert len(host._latest_pasted_paths)==1
    assert host._paste_feedback_timer.started==[2500,2500]
    clear(host)
    assert host._latest_pasted_paths==()
    assert host._paste_feedback_timer.stopped>0
    assert len(fired)==3


def test_real_move_through_explicit_paste_reloads_both_visible_tree_parents(tmp_path):
    from clipboard_paste import paste_conflicts
    from paste_destination import choose_paste_destination
    from virtual_clipboard_paste import is_virtual_file_clipboard
    srcparent = tmp_path/'from'; srcparent.mkdir()
    dest = tmp_path/'into'; dest.mkdir()
    leaf = srcparent/'branch'; leaf.mkdir()
    (leaf/'payload.md').write_text('okay',encoding='utf-8')
    calls = []
    clipboard = NS(mimeData=lambda:object(),clear=lambda:calls.append(('clipboard_clear',)))
    view = NS(current_directory=lambda: str(srcparent),
              middle_selected_paths=lambda: [srcparent/'other'],
              refresh_middle=lambda:calls.append(('middle_refresh',)))
    owner = NS(expanded_view=view,
               footer=NS(setText=lambda m:calls.append(('status',m))),
               refresh_files_exp_directory=lambda p:calls.append(('refreshed',str(p))),
               error=lambda m:calls.append(('error',m)))
    fun = method(APP,'Launcher','paste_into_expanded_directory',{
        'Path':Path,
        'QApplication': NS(clipboard=lambda:clipboard),
        'choose_paste_destination':choose_paste_destination,
        'clipboard_sources':lambda mime:[leaf],
        'is_cut_clipboard':lambda mime:True,
        'is_virtual_file_clipboard':lambda mime:False,
        'make_paste_plan':make_paste_plan, 'paste_conflicts':paste_conflicts,
        'paste_items':paste_items,
        'moved_source_parent_directories':moved_source_parent_directories,
        'path_key':path_key,
        'DIAG':Mock(),
        'AmbiguousPasteTarget':type('AmbiguousPasteTarget',(Exception,),{})})
    fun(owner,destination_override=str(dest))
    assert (dest/'branch'/'payload.md').read_text(encoding='utf-8')=='okay'
    assert not leaf.exists()
    assert ('refreshed',str(dest)) in calls
    assert ('refreshed',str(srcparent)) in calls
    assert calls.count(('clipboard_clear',))==1
    assert ('middle_refresh',) in calls
    assert not any(c[0]=='error' for c in calls)


def test_real_copy_does_not_refresh_unmodified_source(tmp_path):
    from clipboard_paste import paste_conflicts
    from paste_destination import choose_paste_destination
    from virtual_clipboard_paste import is_virtual_file_clipboard
    srcparent = tmp_path/'from'; srcparent.mkdir()
    dest = tmp_path/'into'; dest.mkdir()
    leaf = srcparent/'branch';leaf.mkdir()
    (leaf/'a.txt').write_text('okay')
    seen = []
    owner = NS(expanded_view=NS(current_directory=lambda:str(dest),
                                refresh_middle=lambda:None),
               footer=NS(setText=lambda m:None),
               refresh_files_exp_directory=lambda p:seen.append(str(p)),
               error=lambda msg:seen.append(('error',msg)))
    fun = method(APP,'Launcher','paste_into_expanded_directory',{
        'Path':Path,
        'QApplication':NS(clipboard=lambda:NS(mimeData=lambda:object(), clear=lambda:None)),
        'choose_paste_destination':choose_paste_destination,
        'clipboard_sources':lambda mime:[leaf],
        'is_cut_clipboard':lambda mime:False,
        'is_virtual_file_clipboard':lambda mime:False,
        'make_paste_plan':make_paste_plan,'paste_conflicts':paste_conflicts,
        'paste_items':paste_items,
        'DIAG':Mock(),'AmbiguousPasteTarget':type('AmbiguousPasteTarget',(Exception,),{})})
    fun(owner,destination_override=str(dest))
    assert leaf.exists() and (dest/'branch'/'a.txt').exists()
    assert seen==[str(dest)]


def test_real_move_through_remote_folder_paste_reloads_source_and_target(tmp_path):
    from clipboard_paste import paste_conflicts
    from virtual_clipboard_paste import is_virtual_file_clipboard
    from file_transfer_visual import pasted_paths_for
    from clipboard_paste import clipboard_sources
    source_root = tmp_path/'src'; source_root.mkdir()
    target_root = tmp_path/'dst';target_root.mkdir()
    target_folder=target_root/'actual';target_folder.mkdir()
    moved=source_root/'moved';moved.mkdir()
    (moved/'inside.txt').write_text('works')
    seen=[]
    popup=NS(_folder_container_row=lambda:{'launch_browse_target':str(target_root)})
    clipboard=NS(mimeData=lambda:object(),clear=lambda:seen.append('clipboard_cleared'))
    owner=NS(expander=lambda:NS(expand=lambda p:p),
             footer=NS(setText=lambda msg:seen.append(('footer',msg))),
             refresh_files_exp_directory=lambda p:seen.append(('refresh',str(p))),
             refresh_pasted_directory=lambda m,**kw:seen.append(('popup_refresh',kw)),
             error=lambda msg:seen.append(('error',msg)))
    fun=method(APP,'Launcher','paste_into_directory',{
        'Path':Path,'QApplication':NS(clipboard=lambda:clipboard),
        'clipboard_sources':lambda m:[moved],
        'is_cut_clipboard':lambda m:True,
        'is_virtual_file_clipboard':lambda m:False,
        'make_paste_plan':make_paste_plan,'paste_items':paste_items,
        'paste_conflicts':paste_conflicts,'pasted_paths_for':pasted_paths_for,
        'moved_source_parent_directories':moved_source_parent_directories,
        'path_key':path_key,'QTimer':NS(singleShot=lambda ms,fn:fn()),
        'DIAG':Mock()})
    fun(owner,popup,destination_override=target_folder)
    assert not moved.exists()
    assert (target_folder/'moved'/'inside.txt').read_text()=='works'
    assert seen.count(('refresh',str(target_folder)))==1
    assert seen.count(('refresh',str(source_root)))==1
    assert 'clipboard_cleared' in seen
    assert not any(isinstance(row,tuple) and row[0]=='error' for row in seen)
