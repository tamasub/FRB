"""2026-11-12: Direct column switches replace misleading Back/Forward verbs."""
from pathlib import Path
import ast
from types import SimpleNamespace as NS

APP=(Path(__file__).resolve().parents[1]/'src/app.py').read_text('utf-8')


def method(name, env):
    cls=next(n for n in ast.parse(APP).body if isinstance(n,ast.ClassDef) and n.name=='Launcher')
    fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name)
    ns=dict(env)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),name,'exec'),ns)
    return ns[name]


def test_column_switch_does_not_change_folder_or_current_selection():
    pending=[]; calls=[]
    launcher=NS(_remote_context_wheel=None,remote_focus_area=lambda dest:calls.append(dest))
    callback=method('_dispatch_files_column_context_navigation',{'QTimer':NS(singleShot=lambda _,fn:pending.append(fn))})
    menu=NS(close=lambda:calls.append('menu-closed'))
    callback(launcher,menu,'files_exp')
    assert calls==['menu-closed']
    pending.pop()()
    assert calls==['menu-closed','files_exp']


def test_list_from_exp_only_changes_operating_target():
    pending=[]; calls=[]
    launcher=NS(_remote_context_wheel=None,remote_focus_area=lambda dest:calls.append(dest))
    callback=method('_dispatch_files_column_context_navigation',{'QTimer':NS(singleShot=lambda _,fn:pending.append(fn))})
    callback(launcher,NS(close=lambda:None),'directory')
    pending.pop()()
    assert calls==['directory']


def test_old_keyboard_left_right_still_have_their_separate_hierarchy_behavior():
    assert 'def remote_list_left_to_exp(self):' in APP
    assert 'def remote_exp_right_to_list(self):' in APP
    assert "if command in ('REMOTE_TARGET_EXP', 'REMOTE_TARGET_LIST'):" in APP
