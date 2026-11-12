"""FRB Launch: Files Exp root policy and hybrid context wheel when Remote is hidden.

PySide6-free contract tests; real Windows menus require user acceptance.
"""
from pathlib import Path
import ast
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT/'src/app.py').read_text(encoding='utf-8')
VIEW = (ROOT/'src/expanded_view.py').read_text(encoding='utf-8')
STYLE = (ROOT/'src/launch_appearance.py').read_text(encoding='utf-8')


def isolated(name, env):
    cls = next(n for n in ast.parse(APP).body if isinstance(n,ast.ClassDef) and n.name=='Launcher')
    fn = next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name)
    ns = dict(env)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])), '<test>', 'exec'),ns)
    return ns[name]


def test_files_exp_root_only_allows_existing_folder_menu():
    class Action:
        def __init__(self,title): self.title=title;self.triggered=NS(connect=lambda callback:None)
        def setIcon(self,icon):self.icon=icon
        def setIconVisibleInMenu(self,visible):pass
    class Menu:
        def __init__(self):self.titles=[]
        def addAction(self,title):self.titles.append(title);return Action(title)
    add = isolated('_add_registration_menu_actions',{
        'context_action_icon':lambda key:key,
        'QTimer':NS(singleShot=lambda *a:None)})
    menu=Menu()
    add(NS(),menu,'system','folders',allow_file=False,allow_category=False)
    assert menu.titles == ['既存フォルダーを登録...']
    category=Menu()
    add(NS(),category,'work','',allow_file=True)
    assert category.titles == ['カテゴリーフォルダーを作成...',
                               '既存フォルダーを登録...','既存ファイルを登録...']
    method=APP.split('    def show_launch_root_registration_menu(self, point):',1)[1].split('    def handle_launch_drop(',1)[0]
    assert 'allow_category=False' in method


def test_list_context_navigation_is_wired_to_pointer_menus():
    assert VIEW.count('list_context=True') >= 3
    assert "column='list' if list_context else 'exp' if exp_context else None" in APP
    assert "column='exp' if remote_folder_list and explicit_target is not None" in APP
    assert "menu, point, column='list' if list_context else 'exp'" in APP
    assert "self._install_files_column_navigation(menu, column)" in APP
    assert "self.remote_focus_area(target)" in APP


def test_icon_margins_balanced_and_json_icons_present():
    assert 'QMenu::icon {' not in STYLE.split('CONTEXT_MENU_SPACING_QSS = """', 1)[1].split('"""', 1)[0]
    assert 'QMenu::item { padding:7px 9px; }' in STYLE
    virtual = APP.split('    def show_virtual_launch_context(',1)[1].split('    def _show_launch_json_context_popup(',1)[0]
    for icon in ("context_action_icon('rename')","context_action_icon('copy')",
                 "context_action_icon('properties')","context_action_icon('delete')"):
        assert icon in virtual

