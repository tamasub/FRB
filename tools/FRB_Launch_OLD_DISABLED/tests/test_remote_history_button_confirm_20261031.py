"""FRB Remote history buttons: open once, press again to commit current row.

Exercise real Launcher handlers without requiring Windows or PySide6.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

APP = ast.parse((Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf-8'))


def method(name, env=None):
    cls = next(n for n in APP.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    scope = {'starting_area': lambda *args, **kw: 'directory',
             'ROLE_KIND': 91,
             'Qt': NS(FocusReason=NS(ShortcutFocusReason=1)),
             'DIAG': NS(info=Mock())}
    scope.update(env or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 'src/app.py', 'exec'), scope)
    return scope[name]


COMMAND = method('remote_command')
HISTORY_COMMAND = method('remote_history_command')
HISTORY_CLICK = method('history_row_clicked')
HISTORY_SELECT = method('select_history_keyword')


class Popup:
    def __init__(self, visible=False):
        self.visible = visible

    def isVisible(self):
        return self.visible


class Row:
    def __init__(self, text='FRB', kind='keyword'):
        self.value = text
        self.kind = kind
        self.expanded = False

    def data(self, col, role):
        return self.kind

    def text(self, col):
        return self.value

    def setExpanded(self, value):
        self.expanded = value

    def isExpanded(self):
        return self.expanded


def launcher(kind='keyword', selected=True):
    sr = Row(kind=kind) if selected else None
    choice = NS(currentItem=lambda: sr, setCurrentItem=Mock())
    history = Popup()
    folders = Popup()
    first_result = NS()
    results = NS(topLevelItemCount=lambda: 1, topLevelItem=lambda index: first_result,
                 setCurrentItem=Mock(), setFocus=Mock())
    view = NS(isVisible=lambda: True, _workspace_mode='files',
              favorite_popup=folders, favorite_choices=choice, toggle_directory_favorites=Mock(),
              hide_favorite_popup=Mock(), directory_favorite_clicked=Mock())
    remote = NS(set_area=Mock())
    win = NS(isVisible=lambda: True, isMinimized=lambda: False, expanded_view=view,
             history_popup=history, history_choices=choice, history_visible_rows=lambda: [sr],
             _remote_area='directory', _remote_popup_area=None,
             _last_focus_area='directory', remote_window=remote,
             search=NS(setText=Mock(), setCursorPosition=Mock()),
             search_history=NS(keywords=['FRB']), session_history=NS(has=lambda value: False),
             list=results, _remote_mouse_last_click=None,
             hide_history_popup=Mock(), hide_remote=Mock())
    win.show_history_popup = Mock(side_effect=lambda: setattr(history, 'visible', True))

    def hide_search():
        history.visible = False
    win.hide_history_popup.side_effect = hide_search
    win.select_history_keyword = lambda: HISTORY_SELECT(win)
    win.history_row_clicked = lambda row, col: HISTORY_CLICK(win, row, col)
    win.remote_history_command = Mock(side_effect=lambda cmd: HISTORY_COMMAND(win, cmd))
    view.toggle_directory_favorites.side_effect = lambda: setattr(folders, 'visible', True)
    def choose_folder(row, col):
        folders.visible = False
    view.directory_favorite_clicked.side_effect = choose_folder
    return win


def test_search_button_opens_then_confirm_search_row():
    win = launcher()
    COMMAND(win, 'SEARCH_HISTORY')
    assert win.history_popup.isVisible()
    assert win._remote_popup_area == 'search_history'
    win.remote_history_command.assert_not_called()
    COMMAND(win, 'SEARCH_HISTORY')
    win.remote_history_command.assert_called_once_with('ENTER')
    win.search.setText.assert_called_once_with('FRB')
    assert not win.history_popup.isVisible()
    assert win._remote_popup_area is None
    assert win._remote_area == 'list'
    win.remote_window.set_area.assert_called_with('list')


def test_search_category_second_click_only_expands_category():
    win = launcher(kind='category')
    row = win.history_choices.currentItem()
    COMMAND(win, 'SEARCH_HISTORY')
    COMMAND(win, 'SEARCH_HISTORY')
    assert row.isExpanded()
    assert win.history_popup.isVisible()
    win.search.setText.assert_not_called()


def test_no_selection_second_click_is_noop_and_keeps_popup():
    win = launcher(selected=False)
    COMMAND(win, 'SEARCH_HISTORY')
    COMMAND(win, 'SEARCH_HISTORY')
    assert win.history_popup.isVisible()
    win.search.setText.assert_not_called()


def test_folder_button_opens_then_confirms_selected_folder_once():
    win = launcher()
    COMMAND(win, 'FOLDER_HISTORY')
    assert win.expanded_view.favorite_popup.isVisible()
    assert win._remote_popup_area == 'folder_history'
    COMMAND(win, 'FOLDER_HISTORY')
    win.remote_history_command.assert_called_once_with('ENTER')
    win.expanded_view.directory_favorite_clicked.assert_called_once_with(
        win.expanded_view.favorite_choices.currentItem(), 0)
    assert win._remote_popup_area is None
    win.expanded_view.hide_favorite_popup.assert_not_called()


def test_folder_button_second_click_without_selected_row_does_not_close_or_navigate():
    win = launcher(selected=False)
    COMMAND(win, 'FOLDER_HISTORY')
    COMMAND(win, 'FOLDER_HISTORY')
    assert win.expanded_view.favorite_popup.isVisible()
    win.expanded_view.directory_favorite_clicked.assert_not_called()


def test_folder_history_does_not_open_in_non_expanded_mode():
    win = launcher()
    win.expanded_view.isVisible = lambda: False
    COMMAND(win, 'FOLDER_HISTORY')
    win.expanded_view.toggle_directory_favorites.assert_not_called()
    win.remote_window.set_area.assert_called_with('directory')


def test_history_tooltips_document_first_and_second_click():
    source = (Path(__file__).resolve().parents[1] / 'src' / 'launch_remote.py').read_text(encoding='utf-8')
    assert '1回目：検索履歴を開く／2回目：選択中の履歴を決定' in source
    assert '1回目：フォルダー履歴を開く／2回目：選択中のフォルダーへ移動' in source
