"""FRB Remote: native single/double click semantics; no Qt required."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP = ast.parse((ROOT / 'src/app.py').read_text(encoding='utf-8'))
REMOTE_SOURCE = (ROOT / 'src/launch_remote.py').read_text(encoding='utf-8')
REMOTE = ast.parse(REMOTE_SOURCE)


def method(tree, cls, name, env=None):
    klass = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
    fn = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == name)
    env = dict(env or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), 'source.py', 'exec'), env)
    return env[name]


def window(*, area='directory', kind='category', mode='single', expanded=True):
    row = {'item_id': 'folder-A', 'item_kind': kind}
    selection = [object()]
    tree = NS(currentItem=lambda: selection[0])
    pane_left, pane_middle, pane_right = (NS(tree=tree), NS(tree=tree), NS(tree=tree))
    view = NS(isVisible=lambda: expanded, left=pane_left, middle=pane_middle, right=pane_right,
              row_data=lambda item: row,
              choose_files=Mock(), choose_middle=Mock(), choose_bookmark=Mock(),
              activate_row=Mock(), root_action=Mock(), root_buttons=[], root_rows=[])
    popup_visible = [False]
    win = NS(expanded_view=view, folder_open_mode=mode, _remote_area=area,
             _last_focus_area=area, _remote_popup_area=None,
             _remote_mouse_last_click=None,
             remote_window=NS(set_area=Mock()),
             history_popup=NS(isVisible=lambda: popup_visible[0]),
             show_history_popup=lambda: popup_visible.__setitem__(0, True),
             remote_history_command=Mock(return_value=True),
             remote_cascade_command=Mock(return_value=False),
             menu=None,
             list=NS(currentItem=lambda: NS(data=lambda *args: row)),
             activate=Mock())
    return win, row, selection


CLICK = method(APP, 'Launcher', 'remote_mouse_click', {'starting_area': Mock(), 'Qt': NS(ItemDataRole=NS(UserRole=32), CheckState=NS(Checked=2, Unchecked=0))})


def test_files_first_column_single_only_previews_even_in_double_mode():
    win, *_ = window(area='files', mode='double')
    CLICK(win)
    CLICK(win, double=True)
    win.expanded_view.choose_files.assert_called_once()
    win.expanded_view.activate_row.assert_not_called()


def test_middle_folder_single_mode_opens_on_single_and_double_does_not_open_twice():
    win, *_ = window(mode='single', area='directory')
    CLICK(win)
    CLICK(win, double=True)
    win.expanded_view.choose_middle.assert_called_once()
    win.expanded_view.activate_row.assert_not_called()


def test_middle_folder_double_mode_selects_on_single_opens_on_double():
    win, *_ = window(mode='double', area='directory')
    CLICK(win)
    win.expanded_view.choose_middle.assert_called_once()
    win.expanded_view.activate_row.assert_not_called()
    CLICK(win, double=True)
    win.expanded_view.activate_row.assert_called_once_with(win.expanded_view.middle, win.expanded_view.middle.tree.currentItem())


def test_middle_file_single_selects_double_activates_in_either_mode():
    for mode in ('single', 'double'):
        win, *_ = window(mode=mode, area='directory', kind='file')
        CLICK(win)
        win.expanded_view.activate_row.assert_not_called()
        CLICK(win, double=True)
        win.expanded_view.activate_row.assert_called_once()


def test_bookmark_folder_remains_single_click_in_both_modes():
    for mode in ('single', 'double'):
        win, *_ = window(mode=mode, area='bookmarks')
        CLICK(win)
        CLICK(win, double=True)
        win.expanded_view.choose_bookmark.assert_called_once()
        win.expanded_view.activate_row.assert_not_called()


def test_search_click_shows_history_even_when_cascade_was_open():
    win, *_ = window(area='search')
    CLICK(win)
    assert win.history_popup.isVisible()
    assert win._remote_popup_area == 'search_history'
    win.remote_window.set_area.assert_called_with('search_history')
    win.remote_cascade_command.assert_not_called()
    CLICK(win, double=True)
    win.remote_history_command.assert_not_called()


def test_history_single_click_uses_existing_activation():
    win, *_ = window(area='directory')
    win._remote_popup_area = 'search_history'
    CLICK(win)
    win.remote_history_command.assert_called_once_with('ENTER')
    CLICK(win, double=True)
    assert win.remote_history_command.call_count == 1


def test_open_cascade_consumes_single_click_but_not_double():
    win, *_ = window(area='directory')
    win.remote_cascade_command.return_value = True
    win.menu = NS(isVisible=lambda: True)
    CLICK(win)
    win.remote_cascade_command.assert_called_once_with('CLICK')
    CLICK(win, double=True)
    assert [c.args[0] for c in win.remote_cascade_command.call_args_list] == ['CLICK', 'DOUBLE_CLICK']
    win.expanded_view.activate_row.assert_not_called()


def test_no_accidental_double_activation_after_model_changes():
    win, row, _ = window(area='directory', kind='file')
    CLICK(win)
    row['item_id'] = 'different-file'
    CLICK(win, double=True)
    win.expanded_view.activate_row.assert_not_called()


def test_classic_search_results_click_selects_double_activates():
    win, *_ = window(area='list', kind='command', expanded=False)
    CLICK(win)
    win.activate.assert_not_called()
    CLICK(win, double=True)
    win.activate.assert_called_once()


def test_recipient_single_click_toggles_checkbox_but_double_does_not_toggle_twice():
    win, row, _ = window(area='list', kind='command', expanded=False)
    row.update({'choice_id': 'recipient-1', '_search_selection_owner': 'group-1'})
    state = [0]
    item = NS(data=lambda *args: row, checkState=lambda col: state[0],
              setCheckState=lambda col, next_state: state.__setitem__(0, next_state))
    win.list.currentItem = lambda: item
    CLICK(win)
    assert state[0] == 2
    CLICK(win, double=True)
    win.activate.assert_not_called()
    assert state[0] == 2


def test_remote_command_dispatches_real_mouse_clicks_not_enter():
    fn = method(APP, 'Launcher', 'remote_command')
    win = NS(isVisible=lambda: True, isMinimized=lambda: False,
             expanded_view=NS(isVisible=lambda: True),
             _remote_area='directory', _last_focus_area='directory',
             remote_mouse_click=Mock(), _remote_mouse_last_click=None)
    fn(win, 'CLICK')
    fn(win, 'DOUBLE_CLICK')
    assert [c.kwargs for c in win.remote_mouse_click.call_args_list] == [
        {'double': False}, {'double': True}]


def test_native_qt_wheel_double_click_does_not_emit_second_click():
    mouse = NS(LeftButton=1)
    qt = NS(MouseButton=mouse)
    fn_release = method(REMOTE, 'WheelPad', 'mouseReleaseEvent', {'Qt': qt})
    fn_dbl = method(REMOTE, 'WheelPad', 'mouseDoubleClickEvent', {'Qt': qt})
    emitted = Mock()
    pad = NS(_pressed=True, _ignore_double_release=False,
             rect=lambda: NS(contains=lambda point: True), command=NS(emit=emitted))
    event = NS(button=lambda: 1, position=lambda: NS(toPoint=lambda: (0, 0)), accept=Mock())
    fn_release(pad, event)
    fn_dbl(pad, event)
    fn_release(pad, event)
    assert [call.args[0] for call in emitted.call_args_list] == ['CLICK', 'DOUBLE_CLICK']


def test_remote_buttons_60px_and_no_key_injection():
    for command, width in [('BACKTAB',76), ('TAB',76), ('SEARCH_HISTORY',84), ('FOLDER_HISTORY',84)]:
        assert f"'{command}', width={width}, height=60" in REMOTE_SOURCE
    assert "self.command.emit('CLICK')" in REMOTE_SOURCE
    assert "self.command.emit('DOUBLE_CLICK')" in REMOTE_SOURCE
    for forbidden in ('SendKeys(', 'SendInput(', 'QKeyEvent(', 'keybd_event('):
        assert forbidden not in REMOTE_SOURCE


class FakeCascade:
    def __init__(self, kind='directory', double_folder=False, opener=True):
        self.row = {'item_kind':kind, 'item_id':'folder-A'}
        self.action = type("Action", (), {})()
        self.action.data = lambda: self.row
        self.action.isEnabled = lambda: True
        self.action.property = lambda key: False
        self.child = None
        self.open_mode = 'hover'
        self.outside_since = 2
        self.hover_timer = NS(stop=Mock())
        self.activeAction = lambda: self.action
        self.setActiveAction = Mock()
        self.open_current = Mock()
        self._queue_folder_single_click = Mock()
        self._folder_click_action = self.action
        self.folder_click_timer = NS(stop=Mock())
        self._double_folder_mode = lambda: double_folder
        self.openers = {self.action: Mock()} if opener else {}
        self._visible = True

    def isVisible(self):
        return self._visible


CASCADE_CLICK = method(APP, 'Launcher', 'remote_cascade_command', {
    'CascadeMenu': FakeCascade, 'AppCascadeMenu': type('OtherCascade', (), {})})


def remote_cascade_window(menu):
    return NS(menu=menu, remote_window=NS(set_area=Mock()),
              _remote_area='directory', _remote_mouse_menu_click=None,
              run_menu_item=Mock())


def test_cascade_single_mode_folder_click_queues_preview_double_launches():
    menu = FakeCascade(double_folder=False)
    win = remote_cascade_window(menu)
    assert CASCADE_CLICK(win, 'CLICK') is True
    menu._queue_folder_single_click.assert_called_once_with(menu.action)
    win.run_menu_item.assert_not_called()
    assert CASCADE_CLICK(win, 'DOUBLE_CLICK') is True
    menu.folder_click_timer.stop.assert_called_once()
    win.run_menu_item.assert_called_once_with(menu.row)


def test_cascade_double_mode_folder_click_selects_then_double_opens():
    menu = FakeCascade(double_folder=True)
    win = remote_cascade_window(menu)
    CASCADE_CLICK(win, 'CLICK')
    menu.setActiveAction.assert_called_once_with(menu.action)
    menu.open_current.assert_not_called()
    CASCADE_CLICK(win, 'DOUBLE_CLICK')
    menu.open_current.assert_called_once_with('keyboard')
    win.run_menu_item.assert_not_called()


def test_cascade_category_opens_on_single_in_both_modes():
    for double_mode in (False, True):
        menu = FakeCascade(kind='category', double_folder=double_mode)
        win = remote_cascade_window(menu)
        CASCADE_CLICK(win, 'CLICK')
        if double_mode:
            menu.setActiveAction.assert_called_once()
            menu.open_current.assert_not_called()
        else:
            menu.open_current.assert_called_once()
        CASCADE_CLICK(win, 'DOUBLE_CLICK')
        assert menu.open_current.call_count == 1


def test_cascade_leaf_executes_once_even_if_double_clicked():
    menu = FakeCascade(kind='command', opener=False)
    win = remote_cascade_window(menu)
    CASCADE_CLICK(win, 'CLICK')
    CASCADE_CLICK(win, 'DOUBLE_CLICK')
    win.run_menu_item.assert_called_once_with(menu.row)


def test_cascade_double_ignores_new_child_after_first_click_opens_menu():
    root = FakeCascade(kind='category')
    win = remote_cascade_window(root)
    CASCADE_CLICK(win, 'CLICK')
    root.child = FakeCascade(kind='command', opener=False)
    CASCADE_CLICK(win, 'DOUBLE_CLICK')
    win.run_menu_item.assert_not_called()


def test_real_middle_folder_handler_honors_saved_single_double_modes():
    source = ast.parse((ROOT / 'src/expanded_view.py').read_text(encoding='utf-8'))
    class FakeQt:
        KeyboardModifier = NS(ControlModifier=1, ShiftModifier=2)
    scheduled = []
    handler = method(source, 'ExpandedLauncherView', 'choose_middle', {
        'QApplication': NS(keyboardModifiers=lambda: 0),
        'Qt': FakeQt, 'QTimer': NS(singleShot=lambda ms, fn: scheduled.append(fn)),
    })
    for mode, expected_path in [('double', 0), ('single', 1)]:
        row = {'item_kind': 'category', 'item_id': 'child'}
        obj = NS(launcher=NS(folder_open_mode=mode), path=[{'item_id':'root'}],
                 row_data=lambda item: row, refresh_middle=Mock())
        handler(obj, object(), 0)
        assert len(obj.path) == 1 + expected_path
    assert len(scheduled) == 1
