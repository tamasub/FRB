"""Search results have a consistent, non-destructive file/folder right-click menu.

Test the real Launcher method in isolation without PySide6/Windows.
"""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from context_menu_config import load_context_menus, visible_context_entries, visible_search_context_entries
from context_menu_resolver import resolve_search_context_target, resolve_context_target
from context_menu_actions import is_downloads_zip

SRC = (ROOT / 'src/app.py').read_text(encoding='utf-8')
TREE = ast.parse(SRC)
LAUNCHER = next(c for c in TREE.body if isinstance(c, ast.ClassDef) and c.name == 'Launcher')
CONFIG = ROOT / 'config/context_menu_options.json'


def isolated(name, scope):
    fn = next(m for m in LAUNCHER.body if isinstance(m, ast.FunctionDef) and m.name == name)
    code = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    exec(compile(code, '<FRB Launcher method>', 'exec'), scope)
    return scope[name]


class FakeMenu:
    def __init__(self, parent):
        self.actions = []
        self.aboutToHide = SimpleNamespace(connect=lambda fn: None)
    def addAction(self, title, callback):
        self.actions.append((title, callback))
        return SimpleNamespace(setEnabled=lambda x: None, setIcon=lambda x: None,
                               setIconVisibleInMenu=lambda x: None)
    def addSeparator(self):
        self.actions.append(('---', None))
    def isEmpty(self):
        return not self.actions
    def setStyleSheet(self, style):
        pass
    def popup(self, point):
        pass


def make_launcher(search_query, authored=None, expander=None):
    scope = dict(QMenu=FakeMenu, resolve_context_target=resolve_context_target,
                 load_context_menus=load_context_menus,
                 visible_context_entries=visible_context_entries,
                 CONTEXT_MENU_OPTIONS=CONFIG, context_action_icon=Mock(),
                 is_downloads_zip=is_downloads_zip, Path=Path,
                 context_menu_spacing_qss=lambda theme: '')
    show = isolated('show_launch_context_menu', scope)
    holder = SimpleNamespace(
        data={'items':[{}]}, selection=None, authored_items=authored or [],
        color_theme='dark',
        search=SimpleNamespace(text=lambda: search_query),
        hover_timer=SimpleNamespace(stop=Mock()),
        _context_paste_enabled=Mock(return_value=True),
        _paste_from_context_menu=Mock(),
        perform_filesystem_context_action=Mock(),
        launch_configuration_studio=Mock(),
        open_search_file_parent_in_launch=Mock(),
        open_search_folder_in_launch=Mock(),
        expander=lambda: SimpleNamespace(expand=expander or (lambda x: x)),
        add_open_with_submenu=lambda menu, title, path: menu.addAction(title, lambda: None),
    )
    return show, holder


def menu_labels(holder):
    return [label for label, _ in holder._launch_context_menu.actions]


def callback(holder, title):
    return next(cb for label, cb in holder._launch_context_menu.actions if label == title)


def test_main_search_file_is_safe_and_parent_stays_in_launch():
    show, host = make_launcher('report')
    row={'_indexed_file':r'C:\Docs\report.txt', 'item_id':'__file_index_report'}
    assert show(host, (4,5), row)
    labels=menu_labels(host)
    for name in ('コピー', 'フルパスのコピー', 'クラウドリンクのコピー',
                 'ファイル名のコピー', 'プログラムから開く…',
                 'フォルダーを開く', 'フォルダーをターミナルで開く', 'プロパティー'):
        assert name in labels
    for risky in ('切り取り', '貼り付け', '削除（ごみ箱へ）', '名前の変更',
                  'すべて展開...', 'Pause付きで実行', 'ファイル名を使ってGitコミット'):
        assert risky not in labels
    assert labels[0] != '---' and labels[-1] != '---'
    assert all(a != b or a != '---' for a,b in zip(labels, labels[1:]))
    callback(host,'フォルダーを開く')(True)
    host.open_search_file_parent_in_launch.assert_called_once_with(r'C:\Docs\report.txt')
    callback(host,'フルパスのコピー')(True)
    host.perform_filesystem_context_action.assert_called_once_with(
        'copy_full_path', r'C:\Docs\report.txt', 'file')


def test_main_search_indexed_folder_has_safe_menu_and_launch_navigation():
    show, host = make_launcher('json')
    path = r'C:\Docs\data\json'
    row = {'item_kind':'directory', '_file':path, 'item_id':'__folder_index_json'}
    assert show(host, (4,5), row)
    labels=menu_labels(host)
    for name in ('Launch内で開く', 'エクスプローラで開く', 'ターミナルで開く',
                 'パスのコピー', 'クラウドリンクのコピー', 'コピー', 'プロパティー'):
        assert name in labels
    for risky in ('切り取り', '貼り付け', '削除（ごみ箱へ）', '名前の変更'):
        assert risky not in labels
    callback(host,'Launch内で開く')(True)
    host.open_search_folder_in_launch.assert_called_once_with(path)
    callback(host,'エクスプローラで開く')(True)
    host.perform_filesystem_context_action.assert_called_once_with('open_explorer',path,'folder')


def test_authored_real_folder_search_gets_safe_folder_menu(tmp_path):
    folder=tmp_path/'FRBStudio_App data json'
    folder.mkdir()
    authored={'item_id':'studio_folder', 'item_kind':'directory',
              'launch_browse_target':'%frb_root%/data/json'}
    show, host=make_launcher('data json',[authored],
                             expander=lambda value: str(folder))
    assert show(host, (4,5), authored)
    assert 'Launch内で開く' in menu_labels(host)
    assert '削除（ごみ箱へ）' not in menu_labels(host)
    callback(host,'Launch内で開く')(True)
    host.open_search_folder_in_launch.assert_called_once_with(str(folder))
    host.launch_configuration_studio.assert_not_called()


def test_authored_folder_retains_studio_properties_without_search(tmp_path):
    folder=tmp_path/'real folder'
    folder.mkdir()
    authored={'item_id':'studio_folder', 'item_kind':'directory',
              'launch_browse_target':str(folder)}
    show, host=make_launcher('',[authored])
    assert show(host, (4,5), authored)
    assert menu_labels(host)==['プロパティ']
    callback(host,'プロパティ')(True)
    host.launch_configuration_studio.assert_called_once_with(item_id='studio_folder')


def test_authored_command_or_missing_folder_cannot_become_filesystem_menu(tmp_path):
    command={'item_id':'not_a_folder', 'item_kind':'command',
             'launch_browse_target':str(tmp_path)}
    missing={'item_id':'missing', 'item_kind':'directory',
             'launch_browse_target':str(tmp_path/'gone')}
    show, host=make_launcher('results',[command,missing])
    for row in (command,missing):
        assert show(host, (4,5), row)
        assert menu_labels(host)==['プロパティ']
        assert resolve_search_context_target(row,[command,missing]) == ('studio',None)


def test_normal_files_menu_keeps_existing_file_rename_and_folder_delete():
    show, host=make_launcher('')
    assert show(host, (4,5), {'item_kind':'command', '_file':r'C:\Doc\report.txt'})
    assert '名前の変更' in menu_labels(host)
    assert '切り取り' in menu_labels(host)
    assert '削除（ごみ箱へ）' in menu_labels(host)
    assert show(host, (4,5), {'item_kind':'directory', '_file':r'C:\Doc\folder'})
    assert '名前の変更' in menu_labels(host)
    assert '貼り付け' in menu_labels(host)


def test_safe_filter_preserves_json_order_and_collapses_separators():
    config=load_context_menus(CONFIG)
    for kind in ('file','folder'):
        source=config[kind]
        safe=visible_search_context_entries(source,kind)
        labels=[r.get('action_id') for r in safe if r.get('action_id')]
        assert 'delete' not in labels and 'rename' not in labels
        assert 'cut' not in labels and 'paste' not in labels
        assert safe[0].get('action_id')=='copy'
        assert safe[-1].get('action_id')=='properties'
        assert safe[0].get('type')!='separator'
        assert safe[-1].get('type')!='separator'
        assert all(a.get('type')!='separator' or b.get('type')!='separator'
                   for a,b in zip(safe,safe[1:]))


def test_folder_navigation_reuses_existing_history_and_does_not_select_file():
    # The new folder entry point delegates to the same Files history path.
    navigate=isolated('open_search_folder_in_launch', {})
    calls=[]
    holder=SimpleNamespace(open_search_file_parent_in_launch=lambda *args, **kwargs: calls.append((args,kwargs)))
    navigate(holder,r'C:\Data\json')
    assert calls==[((r'C:\Data\json',), {'directory':True})]


def test_folder_search_navigation_registers_one_files_history_stop(tmp_path):
    from directory_navigation_history import DirectoryNavigationHistory
    from directory_address import directory_row
    # DirectoryNavigationHistory intentionally accepts Windows paths only.
    folder=r'C:\FRB\data\json'
    home=r'C:\FRB\tools'

    class WindowsDir:
        def __init__(self, value): self.value=value
        def is_dir(self): return True
        def __str__(self): return self.value

    class View:
        def __init__(self):
            self.path=[directory_row(str(home))]
            self.history=DirectoryNavigationHistory(100)
            self.history.record(str(home),self.path)
            self.visible=False
            self.select_middle_file=Mock(return_value=True)
        def isVisible(self):
            return self.visible
        def go_to_directory(self,target):
            self.path=[directory_row(target)]
            self.history.record(target,self.path)
            return True

    view=View()
    state={'query':'json','mode':'compact','page':'search'}
    holder=SimpleNamespace(
        data={'items':[]}, pages=[{'page_id':'work'}], expanded_view=view,
        view_mode='compact', page_id='search', stack=[{'title':'search'}],
        selection=None, checked={'previous'},
        search=SimpleNamespace(clear=lambda:state.update(query='')),
        tabs=SimpleNamespace(blockSignals=Mock(),setCurrentIndex=Mock()),
        footer=SimpleNamespace(setText=Mock()),
        _launch_context_menu=SimpleNamespace(close=Mock()),
        close_cascade_for_main_interaction=Mock(),
        hide_history_popup=Mock(),
        hover_timer=SimpleNamespace(stop=Mock()),
        _read_expanded_options=lambda:{'enabled':True,'page_id':'work'},
        error=Mock(),
    )
    def render():
        view.visible=(holder.view_mode=='expanded' and holder.page_id=='work'
                      and not state['query'])
    holder.render=render
    holder.set_view_mode=lambda mode:setattr(holder,'view_mode',mode)
    scope={'Path':WindowsDir, 'expanded_targets':lambda items,opts:(True,)}
    open_path=isolated('open_search_file_parent_in_launch',scope)
    holder.open_search_file_parent_in_launch=lambda target,**kwargs:open_path(holder,target,**kwargs)
    open_folder=isolated('open_search_folder_in_launch',{})

    assert open_folder(holder,str(folder)) is True
    assert holder.page_id=='work' and holder.view_mode=='expanded'
    assert str(view.path[-1]['launch_browse_target'])==str(folder)
    assert len(view.history.entries)==2
    view.select_middle_file.assert_not_called()
    assert state['query']==''
    holder.error.assert_not_called()
