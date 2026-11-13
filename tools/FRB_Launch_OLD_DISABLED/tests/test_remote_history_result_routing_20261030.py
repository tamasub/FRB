"""Remote search-history selection must retarget mouse clicks to search hits.

Extract the real application handlers with AST so this regression can run
without the Windows GUI / PySide6 dependency.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

APP = ast.parse((Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf-8'))
ROLE_KIND = 91


def method(name, extra=None):
    klass = next(node for node in APP.body
                 if isinstance(node, ast.ClassDef) and node.name == 'Launcher')
    node = next(node for node in klass.body
                if isinstance(node, ast.FunctionDef) and node.name == name)
    env = {'ROLE_KIND': ROLE_KIND,
           'Qt': NS(FocusReason=NS(ShortcutFocusReason=1), ItemDataRole=NS(UserRole=32)),
           'DIAG': NS(info=Mock()), 'starting_area': lambda *args, **kwargs: 'directory'}
    env.update(extra or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 '<app.py>', 'exec'), env)
    return env[name]


REMOTE_HISTORY = method('remote_history_command')
REMOTE_CLICK = method('remote_mouse_click')
HISTORY_CLICK = method('history_row_clicked')
HISTORY_SELECT = method('select_history_keyword')


class Row:
    def __init__(self, kind='keyword'):
        self.kind = kind

    def data(self, col, role):
        return self.kind

    def text(self, col):
        return 'zenn ブックマーク'

    def isExpanded(self):
        return False

    def setExpanded(self, value):
        pass


class Popup:
    visible = True

    def isVisible(self):
        return self.visible

    def hide(self):
        self.visible = False


def launcher_with_history(kind='keyword'):
    history_row = Row(kind)
    result = {'item_id': 'GA_Zenn', 'item_kind': 'command'}
    selected = NS(data=lambda *args: result)
    list_view = NS(topLevelItemCount=lambda: 2, topLevelItem=lambda i: selected,
                   currentItem=lambda: selected, setCurrentItem=Mock(), setFocus=Mock())
    popup = Popup()
    current = NS(currentItem=lambda: history_row, setCurrentItem=Mock())
    view = NS(isVisible=lambda: False)
    win = NS(_remote_area='directory', _last_focus_area='directory',
             _remote_popup_area='search_history', _remote_mouse_last_click=None,
             history_popup=popup, history_choices=current,
             history_visible_rows=lambda: [history_row],
             remote_window=NS(set_area=Mock()),
             expanded_view=view, search=NS(setText=Mock(), setCursorPosition=Mock()),
             search_history=NS(keywords=['zenn ブックマーク']),
             session_history=NS(keywords=[], has=lambda value: False),
             list=list_view, activate=Mock(), remote_cascade_command=Mock(return_value=False))
    win.hide_history_popup = popup.hide
    win.select_history_keyword = lambda: HISTORY_SELECT(win)
    win.history_row_clicked = lambda row, col: HISTORY_CLICK(win, row, col)
    win.remote_history_command = lambda cmd: REMOTE_HISTORY(win, cmd)
    return win


def test_history_keyword_retargets_remote_from_old_files_pane_to_results():
    win = launcher_with_history()
    REMOTE_CLICK(win)  # click first selected search-history keyword
    win.search.setText.assert_called_once_with('zenn ブックマーク')
    assert not win.history_popup.isVisible()
    assert win._remote_popup_area is None
    assert win._remote_area == 'list'
    win.remote_window.set_area.assert_called_with('list')
    win.list.setCurrentItem.assert_called_once()
    win.list.setFocus.assert_called_once()

    # A double-click event that belongs to the *history click* must NOT run
    # the newly exposed first search result by accident.
    REMOTE_CLICK(win, double=True)
    win.activate.assert_not_called()

    # A fresh physical double-click on the pad does activate the current hit.
    REMOTE_CLICK(win)
    REMOTE_CLICK(win, double=True)
    win.activate.assert_called_once_with(win.list.currentItem().data(0, 32))


def test_history_category_expand_does_not_switch_remote_to_results():
    win = launcher_with_history(kind='category')
    REMOTE_CLICK(win)
    assert win.history_popup.isVisible()
    assert win._remote_area == 'directory'
    assert win._remote_popup_area == 'search_history'
    win.remote_window.set_area.assert_not_called()
    win.activate.assert_not_called()
