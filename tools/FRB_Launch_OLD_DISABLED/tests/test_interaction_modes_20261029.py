"""A/B click/visibility settings. Pure and AST-isolated tests, no PySide6 required."""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from interaction_modes import read_dismiss_on_outside, read_folder_open_mode


def method(file, cls, name, scope=None):
    tree = ast.parse((ROOT / 'src' / file).read_text(encoding='utf-8'))
    klass = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
    node = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == name)
    ns = dict(scope or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), file, 'exec'), ns)
    return ns[name]


def test_defaults_and_ini_conversion():
    assert read_dismiss_on_outside('true') is True
    assert read_dismiss_on_outside(True) is True
    assert read_dismiss_on_outside('false') is False
    assert read_dismiss_on_outside(False) is False
    assert read_folder_open_mode(None) == 'single'
    assert read_folder_open_mode('double') == 'double'
    assert read_folder_open_mode('unknown') == 'single'


def test_settings_change_persists_without_changing_other_mode():
    from interaction_modes import is_double_click_folder
    ini = SimpleNamespace(setValue=Mock(), sync=Mock())
    footer = SimpleNamespace(setText=Mock())
    launcher = SimpleNamespace(settings=ini, footer=footer,
                               dismiss_on_outside_click=True, folder_open_mode='single',
                               _apply_window_mode=Mock())
    set_hide = method('app.py', 'Launcher', 'set_dismiss_on_outside_click')
    set_click = method('app.py', 'Launcher', 'set_folder_open_mode', {
        'read_folder_open_mode': read_folder_open_mode,
        'is_double_click_folder': is_double_click_folder,
    })
    set_hide(launcher, False)
    set_click(launcher, 'double')
    assert launcher.dismiss_on_outside_click is False
    assert launcher.folder_open_mode == 'double'
    launcher._apply_window_mode.assert_called_once()
    assert ini.setValue.call_args_list[0].args == ('dismiss_on_outside_click', False)
    assert ini.setValue.call_args_list[1].args == ('folder_open_mode', 'double')
    assert ini.sync.call_count == 2


def test_inactive_window_may_remain_visible_but_legacy_mode_still_hides():
    state = SimpleNamespace(ApplicationActive=1, ApplicationInactive=2)
    qt = SimpleNamespace(ApplicationState=state)
    app = SimpleNamespace(activeModalWidget=lambda: None)
    fn = method('app.py', 'Launcher', 'app_state', {'Qt': qt, 'QApplication': app})
    launcher = SimpleNamespace(_cloud_link_handoff=False, _filesystem_dialog_depth=0,
                               _launch_context_menu=None, isVisible=lambda: True,
                               menu=SimpleNamespace(close=Mock()),
                               expanded_view=SimpleNamespace(hide_favorite_popup=Mock()),
                               hide_history_popup=Mock(),
                               dismiss=Mock(), dismiss_on_outside_click=False)
    fn(launcher, state.ApplicationInactive)
    launcher.dismiss.assert_not_called()
    launcher.hide_history_popup.assert_called_once()
    launcher.menu.close.assert_called_once()
    launcher.dismiss_on_outside_click = True
    fn(launcher, state.ApplicationInactive)
    launcher.dismiss.assert_called_once_with()


def test_properties_keep_visible_temporarily_lowers_launch(tmp_path):
    path = tmp_path / 'あいう.txt'; path.write_text('data', encoding='utf8')
    calls = []
    launcher = SimpleNamespace(
        dismiss_on_outside_click=False,
        begin_cloud_link_handoff=lambda: calls.append('lower'),
        finish_cloud_link_handoff=lambda: calls.append('restore'),
        dismiss=lambda: calls.append('dismiss'),
        error=Mock(),
    )
    fn = method('app.py', 'Launcher', 'perform_filesystem_context_action', {
        'Path': Path,
        'show_windows_properties': lambda p: calls.append(('properties', p)),
        'DIAG': Mock(),
    })
    fn(launcher, 'properties', path, 'file')
    assert calls == ['lower', ('properties', path)]
    launcher.error.assert_not_called()


def test_properties_error_restores_topmost(tmp_path):
    path = tmp_path / 'report'; path.mkdir()
    calls = []
    launcher = SimpleNamespace(
        dismiss_on_outside_click=False,
        begin_cloud_link_handoff=lambda: calls.append('lower'),
        finish_cloud_link_handoff=lambda: calls.append('restore'),
        dismiss=lambda: calls.append('dismiss'), error=Mock())
    def broken(_):
        raise OSError('test failure')
    fn = method('app.py', 'Launcher', 'perform_filesystem_context_action', {
        'Path': Path, 'show_windows_properties': broken, 'DIAG': Mock()})
    fn(launcher, 'properties', path, 'folder')
    assert calls == ['lower', 'restore']
    launcher.error.assert_called_once()


def test_first_column_always_single_even_in_double_mode():
    calls = []
    row = {'item_id': 'root', 'item_kind': 'directory'}
    view = SimpleNamespace(
        launcher=SimpleNamespace(folder_open_mode='double'),
        row_data=lambda item: row,
        path=[],
        refresh_middle=lambda: calls.append('refresh'),
    )
    fn = method('expanded_view.py', 'ExpandedLauncherView', 'choose_files')
    fn(view, object(), 0)
    assert view.path == [row]
    assert calls == ['refresh']


def test_middle_folder_single_click_only_selects_in_double_mode():
    calls = []
    row = {'item_kind': 'directory', 'item_id': 'sub'}
    timer = SimpleNamespace(singleShot=lambda ms, f: (calls.append('queued'), f()))
    qt = SimpleNamespace(KeyboardModifier=SimpleNamespace(ControlModifier=1, ShiftModifier=2))
    app = SimpleNamespace(keyboardModifiers=lambda: 0)
    view = SimpleNamespace(row_data=lambda item: row, launcher=SimpleNamespace(folder_open_mode='double'),
                           path=[], refresh_middle=lambda: calls.append('refresh'))
    fn = method('expanded_view.py', 'ExpandedLauncherView', 'choose_middle', {
        'Qt': qt, 'QApplication': app, 'QTimer': timer})
    fn(view, object(), 0)
    assert view.path == []
    assert calls == []
    fn(view, object(), 0, force=True)
    assert view.path == [row]
    assert calls == ['queued', 'refresh']
    # Restore single-click semantics after switching back.
    view.launcher.folder_open_mode = 'single'
    view.path = []
    calls.clear()
    fn(view, object(), 0)
    assert view.path == [row]


def test_bookmark_folder_stays_single_click_in_double_mode():
    calls = []
    item = object()
    row = {'item_kind': 'category', 'item_id': 'docs'}
    tree = object()
    view = SimpleNamespace(row_data=lambda x: row, launcher=SimpleNamespace(folder_open_mode='double'),
                           right=SimpleNamespace(tree=tree),
                           open_cascade=lambda *args: calls.append(args))
    fn = method('expanded_view.py', 'ExpandedLauncherView', 'choose_bookmark')
    fn(view, item, 0)
    assert calls == [(row, tree, item)]
    fn(view, item, 0, force=True)
    assert calls == [(row, tree, item), (row, tree, item)]


def test_cascade_double_click_navigates_without_explorer_launch():
    calls = []
    launcher = SimpleNamespace(folder_open_mode='double')
    # QAction semantics: a hashable action returns its row through .data().
    class Action:
        def data(self): return {'item_kind': 'directory'}
        def isEnabled(self): return True
    action = Action()
    menu = SimpleNamespace(launcher=launcher, setActiveAction=lambda a: calls.append('selected'),
                           _folder_click_action=None, _folder_double_click_row=None,
                           folder_click_timer=SimpleNamespace(stop=Mock()))
    menu.openers = {action: lambda mode: calls.append(mode)}
    def folder_check(a):
        return a in menu.openers and a.data().get('item_kind') in ('directory', 'category')
    menu._double_folder_mode = lambda: True
    menu._manual_bookmark_mode = lambda: False
    menu._navigable_folder_action = folder_check
    menu._scroll_item_action = lambda item: action
    menu._folder_row = lambda act: {'item_kind': 'directory'}
    menu._queue_folder_single_click = Mock()
    single = method('app.py', 'CascadeMenu', '_scroll_activate')
    double = method('app.py', 'CascadeMenu', '_scroll_double_clicked')
    single(menu, object())
    assert calls == ['selected']
    menu._queue_folder_single_click.assert_not_called()
    double(menu, object(), 0)
    assert calls == ['selected', 'keyboard']


def test_settings_menu_and_hook_wiring_remains_explicit():
    text = (ROOT / 'src' / 'app.py').read_text(encoding='utf8')
    assert 'is_launcher_visible=lambda: (launcher_surface_visible()' in text
    assert 'and window.dismiss_on_outside_click)' in text
    assert "'Launchを表示したまま'" in text
    assert "'ダブルクリック'" in text
    assert 'self.left.tree.itemClicked.connect(self.choose_files)' in (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf8')


def test_cascade_compact_mouse_double_click_waits_for_second_click():
    """A single mouse-up selects only; second mouse-up opens the submenu."""
    calls = []
    class Action:
        def data(self): return {'item_kind': 'directory', 'item_id': 'subdir'}
    action = Action()
    left = object()
    qt = SimpleNamespace(MouseButton=SimpleNamespace(LeftButton=left))
    class Point:
        def toPoint(self): return self
    class Event:
        def button(self): return left
        def position(self): return Point()
        def accept(self): calls.append('accepted')
    timer = SimpleNamespace(stop=lambda: calls.append('stop'))
    menu = SimpleNamespace(
        order_press=(Point(), action),
        launcher=SimpleNamespace(folder_open_mode='double'),
        openers={action: lambda mode: calls.append(('expanded', mode))},
        _folder_double_click_row=None, _folder_double_click_action=None,
        _folder_click_action=None, folder_click_timer=timer,
        _double_folder_mode=lambda: True,
        _manual_bookmark_mode=lambda: False,
        _navigable_folder_action=lambda a: a is action,
        actionAt=lambda point: action,
        setActiveAction=lambda a: calls.append('selected'),
    )
    release = method('app.py', 'CascadeMenu', 'mouseReleaseEvent', {'Qt': qt})
    doubled = method('app.py', 'CascadeMenu', 'mouseDoubleClickEvent', {'Qt': qt})
    release(menu, Event())
    assert 'selected' in calls
    assert not any(isinstance(x, tuple) and x[0] == 'expanded' for x in calls)
    doubled(menu, Event())
    release(menu, Event())
    assert calls.count(('expanded', 'keyboard')) == 1


def test_settings_first_column_and_persistent_z_order_do_not_touch_data_json():
    source = (ROOT / 'src' / 'app.py').read_text(encoding='utf8')
    assert "self.settings.setValue('folder_open_mode', self.folder_open_mode)" in source
    assert "self.settings.setValue('dismiss_on_outside_click', self.dismiss_on_outside_click)" in source
    assert 'if self.dismiss_on_outside_click:' not in (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf8')
