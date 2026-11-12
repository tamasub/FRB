"""New Files Exp/List universal context navigation contract (Qt-free).

Tests exercise the real shared installer and the Launcher's real dispatch
methods via AST extraction. Windows native GUI remains an acceptance step.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from files_column_context import install_column_navigation, NAVIGATION

APP=(ROOT/'src/app.py').read_text(encoding='utf-8')


class Signal:
    def __init__(self):self.handlers=[]
    def connect(self,fn):self.handlers.append(fn)
    def emit(self):
        for fn in self.handlers:fn(False)


class Action:
    def __init__(self,text,parent=None):
        self.text=text;self.triggered=Signal();self.icon=None;self.tooltip=''
    def setIcon(self,icon):self.icon=icon
    def setIconVisibleInMenu(self,yes):self.visible=bool(yes)
    def setToolTip(self,hint):self.tooltip=hint


class Menu:
    def __init__(self):self.rows=[];self.closed=0
    def actions(self):return self.rows
    def addAction(self,a):self.rows.append(a)
    def insertAction(self,before,a):self.rows.insert(self.rows.index(before),a)
    def insertSeparator(self,before):self.rows.insert(self.rows.index(before),'|')
    def close(self):self.closed+=1


def fake_install(col):
    calls=[];m=Menu();m.addAction(Action('登録解除...'))
    assert install_column_navigation(m,col,Action,lambda icon:icon,lambda menu,target:calls.append(target))
    return m,calls


def launcher_method(name,env):
    cls=next(n for n in ast.parse(APP).body if isinstance(n,ast.ClassDef) and n.name=='Launcher')
    fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name)
    ns=dict(env)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),name,'exec'),ns)
    return ns[name]


def test_exp_always_has_only_list_move_and_no_legacy_back_forward():
    m,calls=fake_install('exp')
    assert [a.text if isinstance(a,Action) else a for a in m.rows] == [
        'List列へ進む','|','登録解除...']
    assert m.rows[0].icon=='forward'
    m.rows[0].triggered.emit()
    assert calls==['directory']


def test_list_always_has_only_exp_move():
    m,calls=fake_install('list')
    assert [a.text if isinstance(a,Action) else a for a in m.rows] == [
        'Exp列へ戻る','|','登録解除...']
    assert m.rows[0].icon=='back_to_exp'
    m.rows[0].triggered.emit()
    assert calls==['files_exp']


def test_installer_is_idempotent_and_fails_on_column_mixup():
    import pytest
    m,calls=fake_install('exp')
    assert not install_column_navigation(m,'exp',Action,lambda k:k,lambda *_:None)
    assert len(m.rows)==3
    with pytest.raises(ValueError):
        install_column_navigation(m,'list',Action,lambda k:k,lambda *_:None)


def test_popup_closes_before_operating_target_changes_not_folder_navigation():
    jobs=[]; owner=NS(_remote_context_wheel=None, remote_focus_area=lambda target: jobs.append(('focus',target)))
    fn=launcher_method('_dispatch_files_column_context_navigation',{'QTimer':NS(singleShot=lambda ms,cb:jobs.append(('timer',cb)))})
    menu=Menu()
    fn(owner,menu,'directory')
    assert menu.closed==1
    assert jobs[0][0]=='timer'
    jobs[0][1]()
    assert jobs[1]==('focus','directory')
    assert 'remote_command(' not in ast.get_source_segment(APP, next(
        n for n in next(n for n in ast.parse(APP).body if isinstance(n,ast.ClassDef) and n.name=='Launcher').body
        if isinstance(n,ast.FunctionDef) and n.name=='_dispatch_files_column_context_navigation'))


def test_all_launch_files_menu_entrypoints_use_same_wiring():
    assert "self._show_launch_json_context_popup(menu, point, column='exp')" in APP
    assert "menu, point, column='list' if list_context else 'exp'" in APP
    assert "menu, column='exp' if remote_folder_list and explicit_target is not None" in APP
    assert APP.count("column='list' if list_context else 'exp' if exp_context else None") >= 2
    assert "self._wire_hybrid_context_menu(menu, column=column)" in APP
    assert "self._install_files_column_navigation(menu, column)" in APP
    exp=(ROOT/'src/remote_files_explorer.py').read_text(encoding='utf-8')
    assert "launcher._wire_hybrid_context_menu(menu, column='exp')" in exp
    assert "'List列へ進む'" in (ROOT/'src/files_column_context.py').read_text(encoding='utf-8')
    assert "('戻る', 'LEFT')" not in APP
    assert "('進む', 'RIGHT')" not in APP
