"""Qt-free regression for right click on non-row Files surfaces.

On Windows, additionally verify the live QMenu on Exp/List heading, tree
blank area, tonton lane, and page-only List view.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT=Path(__file__).resolve().parents[1]
APP=(ROOT/'src/app.py').read_text(encoding='utf-8')
VIEW=(ROOT/'src/expanded_view.py').read_text(encoding='utf-8')
EXP=(ROOT/'src/remote_files_explorer.py').read_text(encoding='utf-8')


def method(source, cls, name, env=None):
    tree=ast.parse(source)
    owner=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls)
    fn=next(n for n in owner.body if isinstance(n,ast.FunctionDef) and n.name==name)
    ns=dict(env or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),name,'exec'),ns)
    return ns[name]


def test_list_virtual_page_uses_current_json_context_not_physical_paste():
    launcher=NS(show_virtual_launch_context=Mock(),
                show_expanded_background_paste_menu=Mock(),
                show_files_column_navigation_menu=Mock())
    current={'source':'launch_json','page_id':'testwk','item_id':'','node_id':'page:testwk'}
    owner=NS(_workspace_mode='files',_virtual_directory_node=current,
             current_directory=lambda:None,launcher=launcher)
    fn=method(VIEW,'ExpandedLauncherView','show_list_background_context',
              {'virtual_item_identity':None})
    # The implementation imports at runtime; add src to import path.
    import sys
    sys.path.insert(0,str(ROOT/'src'))
    assert fn(owner,'screen-pos') is True
    launcher.show_virtual_launch_context.assert_called_once()
    assert launcher.show_virtual_launch_context.call_args.kwargs['list_context'] is True
    launcher.show_expanded_background_paste_menu.assert_not_called()


def test_list_real_folder_preserves_paste_new_context():
    launcher=NS(show_virtual_launch_context=Mock(),
                show_expanded_background_paste_menu=Mock(return_value=True),
                show_files_column_navigation_menu=Mock())
    owner=NS(_workspace_mode='files',_virtual_directory_node=None,
             current_directory=lambda:'F:/somewhere',launcher=launcher)
    fn=method(VIEW,'ExpandedLauncherView','show_list_background_context')
    assert fn(owner,'screen-pos')
    launcher.show_expanded_background_paste_menu.assert_called_once_with('screen-pos')


def test_list_without_folder_keeps_column_nav_context():
    launcher=NS(show_virtual_launch_context=Mock(),
                show_expanded_background_paste_menu=Mock(),
                show_files_column_navigation_menu=Mock(return_value=True))
    owner=NS(_workspace_mode='files',_virtual_directory_node=None,
             current_directory=lambda:None,launcher=launcher)
    fn=method(VIEW,'ExpandedLauncherView','show_list_background_context')
    assert fn(owner,'pos')
    launcher.show_files_column_navigation_menu.assert_called_once_with('list','pos')


def test_blank_lane_title_and_viewport_use_same_list_entry():
    assert "self.show_lane_new_menu(event.globalPos())" in VIEW
    assert "return self.show_list_background_context(global_pos)" in VIEW
    assert 'self.show_list_background_context(position)' in VIEW
    assert 'lambda point, widget=header: self.show_list_background_context(' in VIEW
    assert 'self.show_list_background_context(global_pos)' in VIEW


def test_embedded_exp_heading_always_has_context_and_shared_nav():
    body=ast.get_source_segment(EXP,next(n for n in next(
        n for n in ast.parse(EXP).body if isinstance(n,ast.ClassDef) and n.name=='RemoteFilesExplorer'
    ).body if isinstance(n,ast.FunctionDef) and n.name=='_show_layout_menu'))
    assert "launcher._wire_hybrid_context_menu(menu, column='exp')" in body
    assert 'if self._embedded or' not in body


def test_navigation_only_launcher_uses_same_popup_contract():
    body=ast.get_source_segment(APP,next(n for n in next(
        n for n in ast.parse(APP).body if isinstance(n,ast.ClassDef) and n.name=='Launcher'
    ).body if isinstance(n,ast.FunctionDef) and n.name=='show_files_column_navigation_menu'))
    assert 'self._show_launch_json_context_popup(menu, point, column=column)' in body
