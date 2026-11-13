"""Updated contract (2026-11-12): Remote uses shared Exp/List navigation.

Historical ←/→ and history entries are deliberately absent from Files menus;
their unrelated dedicated hardware/toolbar commands remain available.
"""
from pathlib import Path
import ast
from types import SimpleNamespace as NS

APP=(Path(__file__).resolve().parents[1]/'src/app.py').read_text('utf-8')


def method(name):
    cls=next(n for n in ast.parse(APP).body if isinstance(n,ast.ClassDef) and n.name=='Launcher')
    fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name)
    scope={}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),name,'exec'),scope)
    return scope[name]


def test_remote_menu_uses_the_same_exp_list_installer_as_pointer_menus():
    called=[]
    owner=NS(_remote_area='files_exp',_install_files_column_navigation=lambda menu,column:called.append(column) or True)
    call=method('_prepend_remote_pad_navigation')
    assert call(owner,object())
    assert called==['exp']
    owner._remote_area='directory'
    assert call(owner,object())
    assert called==['exp','list']
    owner._remote_area='web_body'
    assert call(owner,object()) is False
    assert called==['exp','list']


def test_list_context_wins_even_when_remote_controller_targets_exp():
    called=[]
    owner=NS(_remote_area='files_exp', _install_files_column_navigation=lambda _,c:called.append(c) or True)
    assert method('_prepend_remote_pad_navigation')(owner,object(),list_context=True)
    assert called==['list']


def test_canonical_navigation_does_not_dispatch_hierarchy_keys_or_history():
    body=APP.split('    def _dispatch_files_column_context_navigation(',1)[1].split(
        '    def _install_files_column_navigation(',1)[0]
    assert 'remote_focus_area(target)' in body
    assert 'remote_command(' not in body
    assert 'directory_history' not in body
    assert "('戻る', 'LEFT')" not in APP
    assert "('進む', 'RIGHT')" not in APP


def test_existing_remote_history_buttons_are_still_independent():
    assert "if command == 'SEARCH_HISTORY':" in APP
    assert "if command == 'FOLDER_HISTORY':" in APP
    assert "if command == 'CONTEXT_MENU':" in APP
