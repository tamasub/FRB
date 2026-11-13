"""Regression for the three synchronized Remote / Files Exp upgrades.

Portable tests: verify target-specific callbacks and filesystem safety without Qt.
The Windows popup layout and animation still require a local visual check.
"""
import ast
import os
import sys
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'src'))
from context_menu_config import load_context_menus, visible_context_entries
from file_transfer_visual import path_key

APP = (BASE / 'src/app.py').read_text(encoding='utf-8')
REMOTE = (BASE / 'src/launch_remote.py').read_text(encoding='utf-8')
EXPLORER = (BASE / 'src/remote_files_explorer.py').read_text(encoding='utf-8')


def extract(src, class_name, method, namespace=None):
    cls = next(x for x in ast.parse(src).body if isinstance(x, ast.ClassDef) and x.name == class_name)
    func = next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == method)
    ns = {} if namespace is None else dict(namespace)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[func], type_ignores=[])), 'isolated', 'exec'), ns)
    return ns[method]


class Signal:
    def connect(self, fn): self.callback = fn


class Action:
    def __init__(self, title, callback=None, separator=False):
        self.title, self.callback, self.sep = title, callback, separator
        self.enabled, self.visible = True, True
        self.triggered = Signal()
    def setIcon(self, *_): pass
    def setData(self, *_): pass
    def setEnabled(self, value): self.enabled = value
    def setIconVisibleInMenu(self, *_): pass
    def isSeparator(self): return self.sep
    def setVisible(self, value): self.visible = value
    def trigger(self):
        if self.callback is not None and self.enabled:
            return self.callback(False)


class Menu:
    instances = []
    def __init__(self, *_, **__):
        self.items = []
        self.aboutToHide = Signal()
        self.openers = {}
        self.__class__.instances.append(self)
    def addAction(self, title, callback=None):
        item = Action(title, callback)
        self.items.append(item)
        return item
    def addSeparator(self): self.items.append(Action('---', separator=True))
    def actions(self): return self.items
    def setMinimumWidth(self, value): self.min_width = value
    def setMaximumWidth(self, value): self.max_width = value
    def setStyleSheet(self, *_): pass
    def popup(self, *_): pass


def build_menu(tmp_path, target=None, *, protect=False):
    Menu.instances.clear()
    events=[]
    current=tmp_path/'current'; current.mkdir(exist_ok=True)
    target = target or current
    owner=NS(
        expanded_view=NS(
            current_directory=lambda: str(current),
            add_lane_new_submenu=lambda m, **kw:
                events.append(('new', kw)) or NS(menuAction=lambda: Action('new'))),
        color_theme='light', file_icons=NS(icon=lambda *_:'folder'),
        _apply_remote_popup_bounds=lambda m:m,
        _context_paste_enabled=lambda *_:True,
        _paste_from_context_menu=lambda *_a, **kw:events.append(('paste',kw)),
        perform_filesystem_context_action=lambda a,p,k:events.append((a,p,k)),
        refresh_folder_information=lambda p: events.append(('refresh', p)),
        can_rename_remote_folder=lambda _:not protect,
        can_delete_remote_folder=lambda _:not protect,
        rename_remote_folder=lambda p:events.append(('rename',p)),
        _remote_folder_opener_hidden=lambda *_:None,
        _forget_launch_context_menu=lambda *_:None,
        _open_remote_folder_cascade=lambda *args:events.append(('list',args)),
    )
    method=extract(APP,'Launcher','show_expanded_background_paste_menu',{
        'Path':Path, 'os':os, 'QMenu':Menu, 'RemoteFolderActionsMenu':Menu,
        'QFileInfo':str, 'QTimer': NS(singleShot=lambda _ms,cb:cb()),
        'load_context_menus':load_context_menus,
        'visible_context_entries':visible_context_entries,
        'CONTEXT_MENU_OPTIONS':BASE/'config/context_menu_options.json',
        'context_action_icon':lambda _:'icon','LIGHT_MENU_QSS':'',
        'context_menu_spacing_qss':lambda _:'',
        'remote_new_arrow_qss':lambda _:'',
    })
    assert method(owner,'cursor',remote_folder_list=True,files_exp_rename_target=str(target))
    return Menu.instances[0],events


def test_full_folder_menu_uses_same_json_order_and_compact_width(tmp_path):
    menu, _events = build_menu(tmp_path)
    titles=[a.title for a in menu.actions() if not a.isSeparator()]
    assert titles == [
        'Filesリスト', 'コピー', '切り取り', '貼り付け',
        '最新の情報に更新', 'エクスプローラで開く', 'ターミナルで開く',
        'パスのコピー','クラウドリンクのコピー',
        '削除（ごみ箱へ）', '名前の変更', 'プロパティー'
    ]
    assert menu.min_width == 218
    assert menu.max_width == 225
    assert 'new' in menu.__dict__.get('new_submenu_action', Action('')).title


def test_files_exp_actions_always_capture_right_clicked_target(tmp_path):
    target=tmp_path/'selected'; target.mkdir()
    menu, events = build_menu(tmp_path, target)
    assert menu.remote_target_directory == str(target)
    for name in ['コピー','切り取り','貼り付け','最新の情報に更新','削除（ごみ箱へ）',
                 'エクスプローラで開く','名前の変更','プロパティー']:
        action=next(a for a in menu.actions() if a.title==name)
        action.trigger()
    for expected in ['copy','cut','delete','open_explorer','properties']:
        assert (expected,str(target),'folder') in events
    assert ('rename',str(target)) in events
    assert ('paste',{'target_folder':str(target)}) in events
    assert ('refresh',str(target)) in events
    assert ('new',{'target_directory':str(target)}) in events


def test_protected_root_disables_cut_delete_rename_but_allows_copy(tmp_path):
    target=tmp_path/'registered'; target.mkdir()
    menu,events=build_menu(tmp_path,target,protect=True)
    by_title={a.title:a for a in menu.actions()}
    for title in ['切り取り','削除（ごみ箱へ）','名前の変更']:
        assert by_title[title].enabled is False
        by_title[title].trigger()
    assert not events or all(e[0]=='new' for e in events)
    assert by_title['コピー'].enabled is True
    by_title['コピー'].trigger()
    assert ('copy',str(target),'folder') in events


def test_protected_root_and_ancestor_guard_but_children_can_be_deleted(tmp_path):
    root = tmp_path/'registered'; root.mkdir()
    sub = root/'child'; sub.mkdir()
    unrelated = tmp_path/'other'; unrelated.mkdir()
    rows=[{'title':'registered','launch_browse_target':str(root)}]
    method=extract(APP,'Launcher','can_delete_remote_folder', {'Path':Path,'path_key':path_key})
    owner=NS(can_rename_remote_folder=lambda p:Path(p).is_dir(),
             _remote_files_first_column_rows=lambda:rows,
             expander=lambda:NS(expand=lambda x:x))
    with patch.dict(sys.modules, {
        'remote_files_exp_roots':NS(registered_folder_roots=lambda rows,expand:[{'path':str(root)}]),
        'system_drives':NS(drive_rows=lambda:[])
    }):
        assert not method(owner,root)
        assert not method(owner,tmp_path)  # would remove the registered root
        assert method(owner,sub)
        assert method(owner,unrelated)


def test_deleted_current_folder_navigates_to_its_parent_and_syncs_tree(tmp_path):
    parent=tmp_path/'parent'; parent.mkdir()
    deleted=parent/'child'; deleted.mkdir()
    nested=deleted/'nested'; nested.mkdir()
    events=[]
    current=[str(nested)]
    panel=NS(reflect_deleted_folder=lambda p:events.append(('remove',p)),
             isVisible=lambda:True,
             sync_current_directory=lambda p:events.append(('tree',p)))
    view=NS(isVisible=lambda:True,current_directory=lambda:current[0],
            go_to_directory=lambda p:current.__setitem__(0,p) or events.append(('navigate',p)),
            refresh_middle=lambda:events.append(('refresh',)))
    owner=NS(remote_window=NS(files_exp_panel=panel),expanded_view=view)
    after=extract(APP,'Launcher','_after_folder_deleted',{'Path':Path,'path_key':path_key})
    after(owner,str(deleted))
    assert current[0]==str(parent)
    assert events == [('remove',str(deleted)),('navigate',str(parent)),('tree',str(parent))]


def test_remote_initialization_opens_files_exp_once_and_hides_with_remote():
    show = ast.get_source_segment(APP, next(n for c in ast.parse(APP).body
        if isinstance(c, ast.ClassDef) and c.name=='Launcher'
        for n in c.body if isinstance(n, ast.FunctionDef) and n.name=='show_remote_at'))
    assert 'self.remote_window.show_at(pointer)' in show
    assert 'if panel is None or not panel.isVisible():' in show
    assert 'self.remote_window.toggle_files_exp()' in show
    assert show.index('self.remote_window.show_at(pointer)') < show.index('self.remote_window.toggle_files_exp()')
    hide = ast.get_source_segment(REMOTE,next(n for c in ast.parse(REMOTE).body
        if isinstance(c,ast.ClassDef) and c.name=='LaunchRemote'
        for n in c.body if isinstance(n,ast.FunctionDef) and n.name=='hideEvent'))
    assert 'panel.hide()' in hide
    assert 'self.tree.setIndentation(18)' in EXPLORER


def test_delete_guard_rejects_registered_root_before_recycle_bin(tmp_path):
    root=tmp_path/'registered'; root.mkdir()
    notices=[]
    deletion=[]
    fn=extract(APP,'Launcher','perform_filesystem_context_action', {'Path':Path})
    owner=NS(
        can_delete_remote_folder=lambda p:False,
        error=lambda message:notices.append(message),
        _clear_previous_paste_feedback=lambda:None,
    )
    fn(owner,'delete',str(root),'folder')
    assert root.is_dir() and deletion == []
    assert notices and '移動・削除できません' in notices[0]


def test_protected_bulk_delete_fails_before_any_folder_is_recycled(tmp_path):
    root=tmp_path/'root'; root.mkdir()
    other=tmp_path/'other'; other.mkdir()
    fn=extract(APP,'Launcher','perform_filesystem_batch_action',
               {'Path':Path,'QTimer':NS(singleShot=lambda *_:None)})
    errors=[]
    owner=NS(can_delete_remote_folder=lambda p:Path(p)!=root,
             error=lambda message:errors.append(message),
             _filesystem_dialog_depth=0,
             _finish_batch_delete_guard=lambda:None)
    # The action must never reach QInputDialog / filesystem_progress.
    fn(owner,'delete',[str(other),str(root)])
    assert root.is_dir() and other.is_dir()
    assert errors and '登録フォルダー' in errors[0]


def test_files_exp_removes_only_deleted_branch_from_both_duplicate_roots(tmp_path):
    # Structural contract: recursive tree pruning should not re-create the
    # whole tree (which would lose unrelated expanded branches).
    prune=ast.get_source_segment(EXPLORER,next(n for c in ast.parse(EXPLORER).body
        if isinstance(c,ast.ClassDef) and c.name=='RemoteFilesExplorer'
        for n in c.body if isinstance(n,ast.FunctionDef) and n.name=='reflect_deleted_folder'))
    assert 'parent.removeRow(row)' in prune
    assert 'prune(item)' in prune
    assert 'self.reset_to_roots()' not in prune


def test_remote_blank_strip_paste_is_fixed_to_current_directory():
    source=ast.get_source_segment(APP,next(n for c in ast.parse(APP).body
        if isinstance(c,ast.ClassDef) and c.name=='Launcher'
        for n in c.body if isinstance(n,ast.FunctionDef) and n.name=='show_expanded_background_paste_menu'))
    assert 'p=(target_directory if remote_folder_list' in source
    assert 'self._paste_from_context_menu(self, target_folder=p)' in source
