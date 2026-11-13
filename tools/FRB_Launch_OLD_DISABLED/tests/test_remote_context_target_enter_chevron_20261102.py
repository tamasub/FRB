"""2026-11-02: Remote context source of truth, Enter safety and native Qt arrow.

Portable source/logic tests; Windows Qt paint/focus behavior needs an on-device test.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

BASE = Path(__file__).resolve().parents[1]
APP = (BASE / 'src/app.py').read_text(encoding='utf-8')
VIEW = (BASE / 'src/expanded_view.py').read_text(encoding='utf-8')


def method(source, cls, name, scope=None):
    cl = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef) and n.name == cls)
    node = next(n for n in cl.body if isinstance(n, ast.FunctionDef) and n.name == name)
    namespace = {} if scope is None else dict(scope)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), '<test>', 'exec'), namespace)
    return namespace[name]


def test_files_exp_menu_pins_all_operations_to_context_folder():
    src = ast.get_source_segment(APP, next(f for c in ast.parse(APP).body
        if isinstance(c, ast.ClassDef) and c.name == 'Launcher'
        for f in c.body if isinstance(f, ast.FunctionDef) and f.name == 'show_expanded_background_paste_menu'))
    assert 'explicit_target = str(files_exp_rename_target)' in src
    assert "menu.remote_target_directory = explicit_target" in src
    assert 'target_folder=p' in src
    assert 'add_lane_new_submenu(menu, target_directory=explicit_target)' in src
    assert 'target_directory = str(files_exp_rename_target or self.expanded_view.current_directory())' in src
    # Never use a selected middle row when Files Exp already gave a target.
    assert 'self.expanded_view.middle_selected_paths()' not in src


def test_explicit_context_paste_ignores_selected_middle_row():
    fn = method(APP, 'Launcher', '_paste_from_context_menu')
    calls = []
    owner = NS(
        _context_paste_enabled=lambda menu: False,  # Explicit path should bypass this context test.
        _paste_context_destination=lambda menu: 'expanded',
        paste_into_expanded_directory=lambda **kwargs: calls.append(kwargs),
    )
    fn(owner, object(), target_folder='X:/target')
    assert calls == [{'destination_override': 'X:/target'}]


def test_new_menu_receives_same_context_target_after_popup_closes():
    menu_method = method(VIEW, 'ExpandedLauncherView', 'add_lane_new_submenu')
    class Action:
        def __init__(self): self.triggered = NS(connect=lambda fn: setattr(self, 'callback', fn))
        def setIcon(self, *_): pass
        def setToolTip(self, *_): pass
        def setEnabled(self, *_): pass
    class Menu:
        def __init__(self): self.actions=[]
        def addMenu(self, *_): self.sub=Menu(); return self.sub
        def addAction(self, *_): a=Action(); self.actions.append(a); return a
        def addSeparator(self): pass
        def setObjectName(self, *_): pass
        def setToolTipsVisible(self, *_): pass
        def setIcon(self, *_): pass
        def setStyleSheet(self, *_): pass
    calls=[]
    class Timer:
        @staticmethod
        def singleShot(ms, fn): fn()
    obj = NS(launcher=NS(file_icons=NS(icon=lambda *_:'icon'), color_theme='light'),
             create_from_lane=lambda kind, **kw: calls.append((kind,kw)))
    fn = menu_method
    fn.__globals__.update({
        'QTimer':Timer, 'QFileIconProvider':NS(IconType=NS(Folder=0)),
        'QFileInfo': lambda name: name,
        'discover_shellnew': lambda: [], 'context_action_icon':lambda _: 'icon',
        'LIGHT_MENU_QSS':'', 'context_menu_spacing_qss':lambda _: ''})
    from unittest.mock import patch
    import sys
    with patch.dict(sys.modules, {'context_menu_icons':NS(context_action_icon=lambda _: 'icon'),
                                  'launch_appearance':NS(context_menu_spacing_qss=lambda _: '', LIGHT_MENU_QSS='')}):
        root=Menu(); fn(obj,root,target_directory='C:/chosen')
    root.sub.actions[0].callback(False)
    root.sub.actions[2].callback(False)
    assert calls == [('folder', {'target_directory':'C:/chosen'}),
                     ('txt', {'target_directory':'C:/chosen'})]


def test_rename_enter_consumed_without_folder_launch():
    fn = method(APP,'RemoteFolderCascade','eventFilter',{'QEvent':NS(Type=NS(KeyPress=1)),
          'Qt': NS(Key=NS(Key_Return=13,Key_Enter=10,Key_Escape=27)),
          'QTimer':NS(singleShot=lambda ms, f: calls.append(f))})
    calls=[]; confirmed=[]
    editor=NS(_launch_finish_rename=lambda: confirmed.append('rename'))
    class Event:
        def type(self): return 1
        def key(self): return 13
        def accept(self): confirmed.append('consumed')
    class Owner:
        _inline_rename_editor=editor
        _remote_rename_activation_guard=False
        def eventFilter(self,obj,event): raise AssertionError('parent key handler activated')
    # Method's final `super()` isn't reached; no Qt is needed for this test.
    owner=Owner(); assert fn(owner,editor,Event()) is True
    assert confirmed == ['rename','consumed']
    assert owner._remote_rename_activation_guard
    calls.pop()(); assert not owner._remote_rename_activation_guard


def test_new_arrow_uses_real_small_bitmap_instead_of_platform_native_size():
    text = APP
    assert 'remote_new_arrow_qss(self.color_theme)' in text
    assert 'width: 4px; height: 8px;' in text
    for theme in ('light','dark'):
        f=BASE/'assets'/f'remote_menu_chevron_{theme}.png'
        assert f.is_file()
        assert f.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
        assert len(f.read_bytes())>80


def test_actual_files_exp_context_actions_capture_right_clicked_folder(tmp_path):
    """A different selected Files row must not retarget Paste/New/Open/Properties."""
    from context_menu_config import load_context_menus, visible_context_entries
    class Signal:
        def connect(self, fn): self.callback=fn
    class Action:
        def __init__(self, name, callback=None):
            self.name=name; self.callback=callback; self.triggered=Signal()
        def setIcon(self,*_): pass
        def setData(self,*_): pass
        def setEnabled(self,*_): pass
        def setIconVisibleInMenu(self,*_): pass
    class Menu:
        def __init__(self, **kw):
            self.items=[]; self.aboutToHide=Signal(); self.openers={}
        def addAction(self, name, callback=None):
            action=Action(name,callback); self.items.append(action); return action
        def addSeparator(self): pass
        def setMinimumWidth(self,*_): pass
        def minimumWidth(self): return 0
        def setStyleSheet(self,*_): pass
        def popup(self,*_): pass
    selected=tmp_path/'selected'; selected.mkdir()
    decoy=tmp_path/'decoy'; decoy.mkdir()
    events=[]; menu_objects=[]
    class RootMenu(Menu):
        def __init__(self, **kwargs):
            super().__init__(**kwargs); menu_objects.append(self)
    owner = NS(
        expanded_view=NS(
            current_directory=lambda: str(decoy),
            add_lane_new_submenu=lambda m, **kw: events.append(('new',kw))),
        file_icons=NS(icon=lambda *_: 'folder-icon'),
        _apply_remote_popup_bounds=lambda m:m,
        _context_paste_enabled=lambda m:True,
        _paste_from_context_menu=lambda parent, **kw:events.append(('paste',kw)),
        perform_filesystem_context_action=lambda a,p,k:events.append((a,p,k)),
        can_rename_remote_folder=lambda p:True,
        rename_remote_folder=lambda p:events.append(('rename',p)),
        _remote_folder_opener_hidden=lambda m:None,
        _forget_launch_context_menu=lambda m:None,
        _open_remote_folder_cascade=lambda *a:events.append(('list',a)),
        color_theme='light', _launch_context_menu=None)
    import os
    fn=method(APP,'Launcher','show_expanded_background_paste_menu',{
        'os':os, 'QMenu':Menu,'RemoteFolderActionsMenu':RootMenu,
        'QFileInfo':lambda p:p,'QTimer':NS(singleShot=lambda ms,fn:fn()),
        'load_context_menus':load_context_menus,
        'CONTEXT_MENU_OPTIONS': BASE/'config/context_menu_options.json',
        'visible_context_entries': visible_context_entries,
        'context_action_icon': lambda a:'icon',
        'LIGHT_MENU_QSS':'', 'context_menu_spacing_qss':lambda _: '',
        'remote_new_arrow_qss':lambda _:''})
    assert fn(owner,'cursor',remote_folder_list=True,files_exp_rename_target=str(selected))
    m=menu_objects[0]
    assert m.remote_target_directory==str(selected)
    assert ('new',{'target_directory':str(selected)}) in events
    [a for a in m.items if a.name=='貼り付け'][0].callback(False)
    assert ('paste',{'target_folder':str(selected)}) in events
    [a for a in m.items if a.name=='パスのコピー'][0].callback(False)
    assert ('copy_path',str(selected),'folder') in events
    # Folder-list callback must inherit root menu's explicit target.
    [a for a in m.items if a.name=='Filesリスト'][0].triggered.callback(False)
    assert any(e[0]=='list' for e in events)


def test_create_from_lane_writes_to_context_folder_not_current_or_selected(tmp_path):
    from windows_shellnew import suggest_name, create_new_item
    decoy=tmp_path/'current'; decoy.mkdir()
    destination=tmp_path/'right-clicked'; destination.mkdir()
    news=[]
    owner=NS(current_directory=lambda:str(decoy),
             launcher=NS(error=lambda x:news.append(('error',x)),
                         footer=NS(setText=lambda x:news.append(('ok',x)))))
    fn=method(VIEW, 'ExpandedLauncherView', 'create_from_lane',
        {'Path':Path,'suggest_name':suggest_name,'create_new_item':create_new_item})
    fn(owner,'folder',target_directory=destination)
    assert (destination/'新しいフォルダー').is_dir()
    assert not (decoy/'新しいフォルダー').exists()
    assert any(k=='ok' for k,_ in news)
