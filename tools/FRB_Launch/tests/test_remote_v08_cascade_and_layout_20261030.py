"""Remote v0.8: dispatch to visible menu (no SendKeys) and compact visual priorities."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP = ast.parse((ROOT / 'src/app.py').read_text(encoding='utf-8'))
REMOTE = (ROOT / 'src/launch_remote.py').read_text(encoding='utf-8')


def extract(cls, method, environment):
    klass = next(n for n in APP.body if isinstance(n, ast.ClassDef) and n.name == cls)
    fn = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == method)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), 'app.py', 'exec'), environment)
    return environment[method]


class Action:
    def __init__(self, row=None, *, execute=False):
        self.row = row
        self.execute = execute
        self.trigger = Mock()

    def data(self):
        return self.row

    def isVisible(self):
        return True

    def isEnabled(self):
        return True

    def isSeparator(self):
        return False

    def property(self, key):
        return self.execute if key == 'launch_right_arrow_executes' else False


class CascadeMenu:
    def __init__(self, actions=()):
        self._visible = True
        self._actions = list(actions)
        self._active = self._actions[0] if self._actions else None
        self.child = None
        self.hover_timer = SimpleNamespace(stop=Mock())
        self.open_mode = 'hover'
        self.outside_since = 1
        self.filter_action = None
        self.openers = {}
        self.scroll_tree = None
        self.open_current = Mock()
        self.close_one_level = Mock()
        self._move_filtered_selection = Mock()

    def isVisible(self):
        return self._visible

    def actions(self):
        return self._actions

    def activeAction(self):
        return self._active

    def setActiveAction(self, action):
        self._active = action


class AppCascadeMenu(CascadeMenu):
    pass


def make_dispatch():
    env = dict(CascadeMenu=CascadeMenu, AppCascadeMenu=AppCascadeMenu,
               move_tree_selection=Mock(),
               QAbstractItemView=SimpleNamespace(ScrollHint=SimpleNamespace(EnsureVisible=1)),
               next_wrapped=lambda items, current, step: items[(items.index(current)+step) % len(items)]
               if current in items else items[0 if step > 0 else -1])
    return extract('Launcher', 'remote_cascade_command', env), env


def launcher(menu):
    return SimpleNamespace(menu=menu, run_menu_item=Mock(),
                           remote_window=SimpleNamespace(set_area=Mock()),
                           _remote_area='roots')


def test_wheel_moves_visible_menu_selection_and_enter_runs_its_action():
    dispatch, _ = make_dispatch()
    rows = [Action({'item_kind': 'command', 'title': name}) for name in ('A', 'B', 'C')]
    menu = CascadeMenu(rows)
    win = launcher(menu)
    assert dispatch(win, 'DOWN') is True
    assert menu.activeAction() is rows[1]
    assert dispatch(win, 'ENTER') is True
    win.run_menu_item.assert_called_once_with(rows[1].row)
    assert menu.open_mode == 'keyboard'
    assert menu.outside_since is None
    win.remote_window.set_area.assert_called_with('cascade')


def test_popup_child_is_always_targeted_before_parent():
    dispatch, _ = make_dispatch()
    root = CascadeMenu([Action({'title':'root'})])
    target = Action({'title':'deep', 'item_kind':'command'})
    child = CascadeMenu([target])
    root.child = child
    win = launcher(root)
    assert dispatch(win, 'ENTER') is True
    win.run_menu_item.assert_called_once_with(target.row)
    assert root.open_mode == 'keyboard'


def test_folder_right_opens_child_and_left_goes_one_level_back():
    dispatch, _ = make_dispatch()
    folder = Action({'item_kind':'category','title':'folder'})
    menu = CascadeMenu([folder])
    menu.openers[folder] = Mock()
    win = launcher(menu)
    dispatch(win, 'RIGHT')
    menu.open_current.assert_called_once_with('keyboard')
    win.run_menu_item.assert_not_called()
    dispatch(win, 'LEFT')
    menu.close_one_level.assert_called_once_with()


def test_directory_enter_matches_native_open_folder_action():
    dispatch, _ = make_dispatch()
    folder = Action({'item_kind':'directory','title':'physical folder'})
    menu = CascadeMenu([folder])
    menu.openers[folder] = Mock()
    win = launcher(menu)
    dispatch(win, 'ENTER')
    win.run_menu_item.assert_called_once_with(folder.row)
    menu.open_current.assert_not_called()


def test_filtered_and_long_scroll_menu_moves_its_own_selection():
    dispatch, _ = make_dispatch()
    menu = CascadeMenu([Action({'item_kind':'command'})])
    menu.filter_action = object()
    win = launcher(menu)
    dispatch(win, 'DOWN')
    menu._move_filtered_selection.assert_called_once_with(1)


def test_large_app_menu_uses_its_own_tree_and_activates_selected_row():
    dispatch, env = make_dispatch()
    selected = Action({'item_kind':'command','title':'app'})
    menu = AppCascadeMenu([selected])
    menu.tree = SimpleNamespace(scrollToItem=Mock())
    env['move_tree_selection'].return_value = object()
    win = launcher(menu)
    dispatch(win, 'UP')
    env['move_tree_selection'].assert_called_once_with(menu.tree, -1)
    dispatch(win, 'ENTER')
    win.run_menu_item.assert_called_once_with(selected.row)


def test_hidden_menu_returns_control_to_standard_remote():
    dispatch, _ = make_dispatch()
    menu = CascadeMenu([Action({'item_kind':'command'})])
    menu._visible = False
    win = launcher(menu)
    assert dispatch(win, 'ENTER') is False
    win.run_menu_item.assert_not_called()


def test_remote_command_routes_to_popup_before_background_search_list():
    fn = extract('Launcher', 'remote_command', {
        'starting_area': Mock(return_value='list'),
        'QTimer': SimpleNamespace(singleShot=Mock()),
    })
    win = SimpleNamespace(
        isVisible=lambda: True, isMinimized=lambda: False,
        expanded_view=SimpleNamespace(isVisible=lambda: False),
        _remote_area='list', _remote_popup_area=None,
        remote_cascade_command=Mock(return_value=True),
        list=SimpleNamespace(currentItem=Mock(side_effect=AssertionError('background must stay idle'))),
    )
    fn(win, 'ENTER')
    win.remote_cascade_command.assert_called_once_with('ENTER')


class QObject:
    def __init__(self, parent=None):
        self._parent = parent

    def parent(self):
        return self._parent


class QWidget(QObject):
    def __init__(self, parent=None, *, visible=True):
        super().__init__(parent)
        self.visible = visible

    def isVisible(self):
        return self.visible

    def isAncestorOf(self, obj):
        while obj is not None:
            if obj is self:
                return True
            obj = obj.parent()
        return False


class Event:
    def type(self):
        return 1


def test_remote_buttons_no_longer_dismiss_visible_cascade():
    env = dict(QEvent=SimpleNamespace(Type=SimpleNamespace(MouseButtonPress=1, KeyPress=2)),
               QWidget=QWidget, QObject=QObject, QApplication=SimpleNamespace(activeModalWidget=lambda: None),
               CascadeMenu=CascadeMenu)
    fn = extract('CascadeOutsideClickFilter', 'eventFilter', env)
    root = QWidget()
    root._size_drag = False
    root.menu = CascadeMenu([Action({'title':'foo'})])
    root.remote_window = QWidget(root)
    root._launch_context_menu = None
    root._filesystem_dialog_depth = 0
    root.close_cascade_for_main_interaction = Mock()
    f = SimpleNamespace(launcher=root)
    fn(f, QWidget(root.remote_window), Event())
    root.close_cascade_for_main_interaction.assert_not_called()
    fn(f, QWidget(root), Event())
    root.close_cascade_for_main_interaction.assert_called_once_with()


def test_layout_makes_wheel_primary_and_footer_status():
    assert 'self.setFixedSize(56, 46)' in REMOTE
    assert "'LEFT', width=45, height=44" in REMOTE
    assert "'RIGHT', width=45, height=44" in REMOTE
    assert "'BACKTAB', width=76, height=60" in REMOTE
    assert "'TAB', width=76, height=60" in REMOTE
    assert "'SEARCH_HISTORY', width=84, height=60" in REMOTE
    assert "'FOLDER_HISTORY', width=84, height=60" in REMOTE
    assert "QFrame#remoteTitleBar" in REMOTE and "QFrame#remoteStatusBar" in REMOTE
    assert REMOTE.index('root.addLayout(row_bottom)') < REMOTE.index('root.addWidget(status_frame)')
    for forbidden in ('SendKeys(', 'SendInput(', 'QKeyEvent('):
        assert forbidden not in REMOTE


def test_hover_opened_menu_is_not_retired_while_pointer_is_over_remote():
    import time
    fn = extract('Launcher', 'check_hover_menus', {
        'time': time,
        'QCursor': SimpleNamespace(pos=Mock()),
    })
    class Remote:
        def isVisible(self): return True
        def rect(self): return SimpleNamespace(contains=lambda point: True)
        def mapFromGlobal(self, pos): return pos
    child = SimpleNamespace(isVisible=lambda: True, outside_since=12, child=None)
    menu = SimpleNamespace(isVisible=lambda: True, outside_since=13, child=child)
    win = SimpleNamespace(menu=menu, remote_window=Remote(),
                          _launch_context_menu=None, _filesystem_dialog_depth=0)
    fn(win, pos=(5, 5), now=50)
    assert menu.outside_since is None
    assert child.outside_since is None
