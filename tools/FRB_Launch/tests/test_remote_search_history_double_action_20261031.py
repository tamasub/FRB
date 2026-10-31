"""Search-history Remote: native double click activates *current search hit*.

Run without Windows or Qt installation by extracting the production methods.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP_SOURCE = (ROOT / 'src/app.py').read_text(encoding='utf-8')
REMOTE_SOURCE = (ROOT / 'src/launch_remote.py').read_text(encoding='utf-8')
APP = ast.parse(APP_SOURCE)
REMOTE = ast.parse(REMOTE_SOURCE)


def method(tree, cls, name, scope):
    class_node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
    fn = next(n for n in class_node.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 'source.py', 'exec'), scope)
    return scope[name]


RUN = method(APP, 'Launcher', 'remote_search_result_double_click',
             {'Qt': NS(ItemDataRole=NS(UserRole=32))})


def fixture(*, query='test', visible=True, popup=False, row=None, enabled=True):
    row = {'item_id': 'test', 'item_kind': 'item', 'enabled': enabled} if row is None else row
    item = NS(data=lambda *args: row) if row is not False else None
    lst = NS(isVisible=lambda: visible, currentItem=lambda: item)
    win = NS(search=NS(text=lambda: query), list=lst,
             history_popup=NS(isVisible=lambda: popup), activate=Mock())
    return win, row


def test_selected_search_hit_activates_using_existing_launcher_path():
    win, row = fixture()
    RUN(win)
    win.activate.assert_called_once_with(row)


def test_no_current_search_result_is_noop():
    win, row = fixture(row=False)
    RUN(win)
    win.activate.assert_not_called()


def test_no_search_text_does_not_execute_page_menu_current():
    win, _ = fixture(query='')
    RUN(win)
    win.activate.assert_not_called()


def test_hidden_search_result_does_not_execute():
    win, _ = fixture(visible=False)
    RUN(win)
    win.activate.assert_not_called()


def test_open_history_popup_does_not_execute_background_row():
    win, _ = fixture(popup=True)
    RUN(win)
    win.activate.assert_not_called()


def test_disabled_or_non_dict_row_is_not_executed():
    for row, enabled in [(None, True), ('text', True), ({'item_id': 'x'}, False)]:
        win, _ = fixture(row=row, enabled=enabled)
        if row is None:
            win.list.currentItem = lambda: NS(data=lambda *args: None)
        elif isinstance(row, dict):
            row['enabled'] = False
        RUN(win)
        win.activate.assert_not_called()


def test_double_click_cancelled_first_single_on_same_button():
    button_cls = next(n for n in REMOTE.body if isinstance(n, ast.ClassDef)
                      and n.name == 'RemoteSearchHistoryButton')
    assert {n.name for n in button_cls.body if isinstance(n, ast.FunctionDef)} >= {
        'mouseDoubleClickEvent', 'mouseReleaseEvent'}
    create = next(n for n in REMOTE.body if isinstance(n, ast.ClassDef) and n.name == 'LaunchRemote')
    btn = next(n for n in create.body if isinstance(n, ast.FunctionDef) and n.name == '_button')
    code = ast.unparse(btn)
    assert "command == 'SEARCH_HISTORY'" in code
    assert "timer.stop(), self.command.emit('SEARCH_RESULT_DOUBLE_CLICK')" in code
    assert 'doubleClickInterval()' in code
    assert "timer.timeout.connect(lambda: self.command.emit('SEARCH_HISTORY'))" in code


def test_double_click_routed_before_normal_single_click_logic():
    start = APP_SOURCE.index('    def remote_command(self, command):')
    body = APP_SOURCE[start:APP_SOURCE.index('    def minimize_launcher(self):', start)]
    assert "if command == 'SEARCH_RESULT_DOUBLE_CLICK':" in body
    assert body.index("if command == 'SEARCH_RESULT_DOUBLE_CLICK':") < body.index("if command == 'SEARCH_HISTORY':")
    assert "if command == 'FOLDER_HISTORY':" in body
