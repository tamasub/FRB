"""2026-10-31 Remote polish regression: source contracts without Windows Qt."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
REMOTE = (ROOT / 'src' / 'launch_remote.py').read_text(encoding='utf-8')


def method(source, class_name, name, env=None):
    tree = ast.parse(source)
    cls = next(c for c in tree.body if isinstance(c, ast.ClassDef) and c.name == class_name)
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    scope = dict(env or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), '<method>', 'exec'), scope)
    return scope[name]


def test_remote_history_and_tab_are_above_wheel():
    init = ast.get_source_segment(REMOTE, next(n for n in next(c for c in ast.parse(REMOTE).body
        if isinstance(c, ast.ClassDef) and c.name == 'LaunchRemote').body
        if isinstance(n, ast.FunctionDef) and n.name == '__init__'))
    assert init.index('root.addLayout(row_bottom)') < init.index('root.addLayout(row_top)')
    assert init.index('root.addLayout(row_top)') < init.index('root.addLayout(row_mid)')
    assert init.index('root.addLayout(row_mid)') < init.index('root.addWidget(self.up_band)')


def test_remote_folder_list_is_first_action_and_original_operations_follow():
    init = ast.get_source_segment(APP, next(n for n in next(c for c in ast.parse(APP).body
        if isinstance(c, ast.ClassDef) and c.name == 'Launcher').body
        if isinstance(n, ast.FunctionDef) and n.name == 'show_expanded_background_paste_menu'))
    folder = init.index("menu.addAction('Filesリスト')")
    assert folder < init.index("menu.addAction(paste['title']")
    assert folder < init.index('self.expanded_view.add_lane_new_submenu(menu)')
    assert folder < init.index('selected = visible_context_entries(definitions, folder_actions)')
    # Native Files background menu still skips the extra Remote action.
    assert 'if remote_folder_list:' in init[:folder]


def test_dismiss_saves_row_before_remote_is_hidden():
    source = ast.get_source_segment(APP, next(n for n in next(c for c in ast.parse(APP).body
        if isinstance(c, ast.ClassDef) and c.name == 'Launcher').body
        if isinstance(n, ast.FunctionDef) and n.name == 'dismiss'))
    assert source.index('self.save_last_current()') < source.index('self.hide_remote()')
    assert "self._remote_area == 'directory'" in source
    assert 'self._last_focus_area = remote_area' in source
    assert 'self.hide_remote()' in source


def test_middle_current_uses_same_directory_fallback_if_qt_current_is_lost():
    save = method(APP, 'Launcher', 'save_last_current', {'normalize_focus_state': lambda x:x,
                           'json': __import__('json')})
    saved={}
    folder='F:/FRB'
    row_id='F:/FRB/keep.txt'
    tree = NS(currentItem=lambda: None)
    view=NS(middle=NS(tree=tree), left=NS(tree=tree), right=NS(tree=tree),
            _middle_current_memory=(folder,row_id),
            current_directory=lambda:folder, path=[], root_rows=[],
            isVisible=lambda:True)
    launcher = NS(expanded_view=view, _last_focus_area='directory', _saved_focus_state={'area':'files'},
                  menu=None, selection=None, view_mode='expanded', page_id='page', list=tree,
                  settings=NS(setValue=Mock(), sync=Mock()),
                  _selected_item_id=lambda _:None)
    result = save(launcher)
    assert result['area'] == 'directory'
    assert result['middle_id'] == row_id
    view._middle_current_memory=('other-folder',row_id)
    result=save(launcher)
    assert result['middle_id'] is None


def test_remote_reopen_retains_directory_logical_focus_when_saved_row_exists():
    fn = ast.get_source_segment(APP, next(n for n in next(c for c in ast.parse(APP).body
        if isinstance(c, ast.ClassDef) and c.name == 'Launcher').body
        if isinstance(n, ast.FunctionDef) and n.name == 'show_remote_at'))
    assert "saved.get('area') == 'directory'" in fn
    assert "saved.get('middle_path') == self.expanded_view.current_directory()" in fn
    assert 'middle.currentItem() is not None' in fn
    assert "self._last_focus_area == 'directory'" in fn
    assert "self._remote_area = 'directory'" in fn


def test_native_outside_hook_detects_popup_also_in_keep_open_mode():
    main = next(n for n in ast.parse(APP).body if isinstance(n, ast.FunctionDef) and n.name=='main')
    source = ast.get_source_segment(APP, main)
    assert 'def remote_folder_popup_visible():' in source
    assert 'remote_folder_popup_visible()' in source
    assert 'window.close_remote_folder_menu()' in source
    assert 'if launcher_surface_visible() and window.dismiss_on_outside_click:' in source
    assert 'and window.dismiss_on_outside_click))' in source
    assert 'REMOTE_OUTSIDE_CLICK_HIDE' in source
    assert 'REMOTE_POPUP_OUTSIDE_CLICK_CLOSE' in source


def test_application_click_filter_ignores_nested_popup_and_secondary_context():
    source = ast.get_source_segment(APP, next(n for n in next(c for c in ast.parse(APP).body
        if isinstance(c, ast.ClassDef) and c.name == 'CascadeOutsideClickFilter').body
        if isinstance(n, ast.FunctionDef) and n.name == 'eventFilter'))
    assert "getattr(current, 'remote_folder_navigation', False)" in source
    assert 'context is not opener and context.isVisible()' in source
    assert 'remote.isAncestorOf(obj)' in source
    assert 'launcher.close_remote_folder_menu()' in source


def test_external_click_closes_remote_popup_without_hiding_launcher():
    module = ast.parse(APP)
    main = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name=='main')
    functions = [n for n in main.body if isinstance(n, ast.FunctionDef)
                 and n.name in ('remote_visible', 'remote_folder_popup_visible',
                                'remote_page_popup_visible', 'dismiss_from_outside_click')]
    opener = NS(isVisible=lambda: True)
    window = NS(_remote_folder_root_menu=None, _remote_folder_opener=opener,
                dismiss_on_outside_click=True, close_remote_folder_menu=Mock(),
                dismiss=Mock())
    window.close_remote_page_menu = Mock()
    env = dict(window=window, QApplication=NS(activeModalWidget=lambda:None),
               DIAG=NS(info=Mock()), launcher_surface_visible=lambda: True)
    exec(compile(ast.fix_missing_locations(ast.Module(body=functions,
                  type_ignores=[])), '<external>', 'exec'), env)
    env['dismiss_from_outside_click']()
    window.close_remote_folder_menu.assert_called_once()
    window.dismiss.assert_not_called()
    # Without a Remote popup, the legacy dismiss-on-outside setting is retained.
    window._remote_folder_opener = None
    env['dismiss_from_outside_click']()
    window.dismiss.assert_called_once()
    window.close_remote_folder_menu.assert_called_once()


def test_outside_click_in_keep_open_mode_closes_only_remote_popup():
    module = ast.parse(APP)
    main = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    functions = [n for n in main.body if isinstance(n, ast.FunctionDef)
                 and n.name in ('remote_visible', 'remote_folder_popup_visible',
                                'remote_page_popup_visible', 'dismiss_from_outside_click')]
    window = NS(_remote_folder_root_menu=NS(isVisible=lambda:True),
                _remote_folder_opener=None, dismiss_on_outside_click=False,
                close_remote_folder_menu=Mock(), dismiss=Mock())
    window.close_remote_page_menu = Mock()
    env = dict(window=window, QApplication=NS(activeModalWidget=lambda:None),
               DIAG=NS(info=Mock()), launcher_surface_visible=lambda:True)
    exec(compile(ast.fix_missing_locations(ast.Module(body=functions, type_ignores=[])),
                 '<external>', 'exec'), env)
    env['dismiss_from_outside_click']()
    window.close_remote_folder_menu.assert_called_once()
    window.dismiss.assert_not_called()
