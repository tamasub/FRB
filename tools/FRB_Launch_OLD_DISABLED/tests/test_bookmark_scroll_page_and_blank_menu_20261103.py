"""Regression contracts for the 2026-11-03 UI polish changes."""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from bookmark_bar_flatten import flatten_bookmark_rows
from context_menu_config import load_context_menus

APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
BOOKMARKS = (ROOT / 'src/browser_bookmark_bar.py').read_text(encoding='utf-8')


def method_source(source, class_name, name):
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(source, fn)


def test_nested_bookmarks_flatten_without_folder_popups():
    root = {'item_id':'root','title':'親','item_kind':'category'}
    folder = {'item_id':'folder','title':'仕事','item_kind':'category'}
    leaf_a = {'item_id':'a','title':'Zenn','item_kind':'command'}
    leaf_b = {'item_id':'b','title':'Qiita','item_kind':'command'}
    tree = {'root':[folder,leaf_b], 'folder':[leaf_a,root]}
    leaves = flatten_bookmark_rows([root], lambda item: tree.get(item['item_id'], []))
    assert [row['item_id'] for row, _ in leaves] == ['a','b']
    assert leaves[0][1] == ('親','仕事')
    assert all(row['item_kind'] == 'command' for row, _ in leaves)


def test_limiter_and_bad_children_do_not_freeze_ui():
    folder = {'item_id':'r','title':'root','item_kind':'category'}
    leaves = [{'item_id':i,'title':str(i),'item_kind':'command'} for i in range(1500)]
    result = flatten_bookmark_rows([folder], lambda parent: leaves, limit=15)
    assert len(result) == 15
    assert result[-1][0]['item_id'] == 14
    assert flatten_bookmark_rows([folder], lambda parent: (_ for _ in ()).throw(ValueError()), limit=3) == []


def test_scroll_bar_is_horizontal_and_wheel_does_not_trigger_url():
    init = method_source(BOOKMARKS, 'HorizontalBookmarkBar', '__init__')
    wheel = method_source(BOOKMARKS, 'HorizontalBookmarkBar', '_scroll_wheel')
    render = method_source(BOOKMARKS, 'HorizontalBookmarkBar', 'update_bookmark_bar')
    assert 'self.setWidgetResizable(False)' in init
    assert 'ScrollBarAsNeeded' in init
    assert 'bar.setValue(before - delta)' in wheel
    assert 'event.accept()' in wheel
    assert '_open_bookmark_bar_row' not in wheel
    assert 'flatten_bookmark_rows' not in render
    assert 'self._bookmark_bar_roots' in render
    assert '_open_folder' in render
    assert 'setPopupMode(' not in render


def test_page_header_is_hidden_even_before_workspace_first_show():
    text = method_source(APP, 'Launcher', 'update_header_tab_width')
    assert "expanded_workspace = self.view_mode == 'expanded'" in text
    assert 'self.expanded_view.isVisible()' not in text
    assert 'self.tabs.hide()' in text
    assert 'self.page_overflow_button.hide()' in text


def test_home_and_settings_glyphs_same_size():
    assert 'self.theme_button.setIconSize(QSize(22, 22))' in APP
    assert '(self.nav_home_button, ' in APP
    assert 'button.setIconSize(QSize(22, 22))' in APP


def test_background_menu_has_same_rows_with_disabled_row_only_actions():
    text = method_source(APP, 'Launcher', 'show_expanded_background_paste_menu')
    for name in ('copy','cut','delete','rename'):
        assert f"action_id == '{name}'" in text or f"'{name}'" in text
    assert 'continue  # Files background' not in text
    assert 'continue  # No implicit destructive' not in text
    assert 'action.setEnabled(bool(remote_folder_list)' in text
    assert "load_context_menus(CONTEXT_MENU_OPTIONS)['folder']" in text
    entries = load_context_menus(ROOT/'config/context_menu_options.json')['folder']
    assert {x.get('action_id') for x in entries if x.get('action_id')} >= {'copy','cut','paste','delete','rename','properties'}


def test_blank_menu_shows_same_folder_action_rows_safely(tmp_path):
    """Exercise the actual menu builder without Qt; protect unselected paths."""
    from context_menu_config import visible_context_entries
    from types import SimpleNamespace as NS
    src = method_source(APP, 'Launcher', 'show_expanded_background_paste_menu')
    tree = ast.parse(src)
    fn = tree.body[0]
    class Signal:
        def connect(self, callback): self.callback = callback
    class Action:
        def __init__(self, text, separator=False):
            self.title, self.separator, self.enabled = text, separator, True
        def setEnabled(self, flag): self.enabled = bool(flag)
        def setIcon(self, icon): pass
        def setIconVisibleInMenu(self, visible): pass
        def isSeparator(self): return self.separator
        def setVisible(self, visible): pass
    class Menu:
        def __init__(self, parent=None):
            self.items = []
            self.aboutToHide = Signal()
            self.triggered = Signal()
        def setMinimumWidth(self, value): pass
        def setMaximumWidth(self, value): pass
        def addAction(self, text, callback=None):
            action = Action(text)
            self.items.append(action)
            return action
        def addSeparator(self):
            action = Action('|', True)
            self.items.append(action)
            return action
        def actions(self): return self.items
        def setStyleSheet(self, css): pass
        def popup(self, point): self.popup_position = point
    env = {
        'Path':Path, 'QMenu':Menu, 'RemoteFolderActionsMenu':Menu,
        'load_context_menus':load_context_menus,
        'CONTEXT_MENU_OPTIONS':ROOT/'config/context_menu_options.json',
        'visible_context_entries':visible_context_entries,
        'context_action_icon':lambda action: None,
        'LIGHT_MENU_QSS':'', 'context_menu_spacing_qss':lambda theme:'',
        'remote_new_arrow_qss':lambda theme:'',
    }
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 '<menu>', 'exec'), env)
    current = tmp_path/'test_destination'
    current.mkdir()
    created = []
    class NewSubmenu:
        def __init__(self, action): self.action = action
        def menuAction(self): return self.action
    expanded = NS(current_directory=lambda:str(current),
                  add_lane_new_submenu=lambda menu, target_directory=None:
                      NewSubmenu(menu.addAction('新規作成')))
    owner = NS(expanded_view=expanded, color_theme='light',
               _context_paste_enabled=lambda parent: False,
               _forget_launch_context_menu=lambda menu: None,
               _on_file_context_action_triggered=lambda menu, action: None,
               perform_filesystem_context_action=lambda *a: created.append(a),
               error=lambda msg: created.append(('error',msg)))
    result = env['show_expanded_background_paste_menu'](owner, (10,20))
    assert result is True
    actions = owner._launch_context_menu.items
    shown = [a.title for a in actions if not a.separator]
    assert shown == ['コピー','切り取り','貼り付け','新規作成',
                     '最新の情報に更新','エクスプローラで開く',
                     'ターミナルで開く','パスのコピー','クラウドリンクのコピー',
                     '削除（ごみ箱へ）','名前の変更','プロパティー']
    for action in actions:
        if action.title in ('コピー','切り取り','貼り付け','削除（ごみ箱へ）','名前の変更'):
            assert not action.enabled
    assert not created


def test_selected_folder_has_new_submenu_at_same_position():
    src = method_source(APP, 'Launcher', 'show_launch_context_menu')
    assert "origin == 'folder' and not search_result" in src
    assert 'self.expanded_view.add_lane_new_submenu(' in src
    assert 'target_directory=str(path)' in src
