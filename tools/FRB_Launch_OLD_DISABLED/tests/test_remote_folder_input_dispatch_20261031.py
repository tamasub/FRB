"""Qt-free behavioural tests for Remote QMenu click interception.

On Windows the visual cross-popup focus must still be tested with PySide6.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'remote_folder_menu.py').read_text(encoding='utf-8')


def make_harness():
    cls = next(n for n in ast.parse(SOURCE).body if isinstance(n, ast.ClassDef)
               and n.name == 'RemoteFolderListMenu')
    names = {'eventFilter', 'open_entry_context', '_restore_after_context'}
    selected = [m for m in cls.body if isinstance(m, ast.FunctionDef) and m.name in names]
    fake_cls = ast.ClassDef(name='RemoteFolderListMenu', bases=[ast.Name(id='BaseMenu', ctx=ast.Load())],
                            keywords=[], body=selected, decorator_list=[])
    events = SimpleNamespace(ContextMenu=0, MouseButtonPress=1, MouseButtonRelease=2,
                             MouseButtonDblClick=3)
    buttons = SimpleNamespace(LeftButton=1, RightButton=2)
    scheduled = []
    class BaseMenu:
        def eventFilter(self, watched, event):
            return False
    scope = dict(BaseMenu=BaseMenu, QEvent=SimpleNamespace(Type=events),
                 Qt=SimpleNamespace(MouseButton=buttons),
                 QTimer=SimpleNamespace(singleShot=lambda _, cb: scheduled.append(cb)),
                 Path=Path)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fake_cls], type_ignores=[])),
                 '<methods>', 'exec'), scope)
    instance = scope['RemoteFolderListMenu']()
    action = object()
    instance._mouse_press_action = None
    instance._row_at = Mock()
    instance.setActiveAction = Mock()
    instance.commit_directory = Mock()
    instance.open_file = Mock()
    instance._keep_preview_visible = Mock()
    context = SimpleNamespace(aboutToHide=SimpleNamespace(connect=Mock()))
    launcher = SimpleNamespace(_remote_folder_root_menu=instance,
                               _remote_folder_commit_pending=False,
                               _launch_context_menu=context,
                               show_launch_context_menu=Mock(return_value=True))
    instance.launcher = launcher
    def event(kind, button=1):
        return SimpleNamespace(type=lambda: kind, button=lambda: button,
                               accept=Mock(), globalPosition=lambda: SimpleNamespace(toPoint=lambda: (5, 6)))
    return instance, launcher, context, action, scheduled, events, event


def run_scheduled(queue):
    while queue:
        queue.pop(0)()


def test_folder_left_press_updates_only_on_click_not_hover(tmp_path):
    menu, launcher, _, action, queue, types, event = make_harness()
    folder = tmp_path / 'next'
    folder.mkdir()
    menu._row_at.return_value = (action, (str(folder), True))
    assert menu.eventFilter(menu, event(types.MouseButtonPress))
    assert launcher._remote_folder_commit_pending is True
    menu.commit_directory.assert_not_called()
    run_scheduled(queue)
    menu.commit_directory.assert_called_once_with(str(folder))


def test_file_click_selects_only_double_click_executes(tmp_path):
    menu, _, _, action, queue, types, event = make_harness()
    file = tmp_path / 'info.txt'
    file.write_text('ok')
    menu._row_at.return_value = (action, (str(file), False))
    assert menu.eventFilter(menu, event(types.MouseButtonPress))
    assert menu.eventFilter(menu, event(types.MouseButtonRelease))
    run_scheduled(queue)
    menu.open_file.assert_not_called()
    assert menu.eventFilter(menu, event(types.MouseButtonDblClick))
    run_scheduled(queue)
    menu.open_file.assert_called_once_with(str(file))


def test_folder_right_click_shares_safe_context_and_restores(tmp_path):
    menu, launcher, context, action, queue, types, event = make_harness()
    folder = tmp_path / 'next'
    folder.mkdir()
    menu._row_at.return_value = (action, (str(folder), True))
    assert menu.eventFilter(menu, event(types.MouseButtonPress, 2))
    run_scheduled(queue)
    args, kwargs = launcher.show_launch_context_menu.call_args
    assert args[1]['item_kind'] == 'directory'
    assert args[1]['_file'] == str(folder)
    assert kwargs['force_search_context'] is True
    assert kwargs['context_parent'] is launcher
    assert context.aboutToHide.connect.call_count == 1
    # Closing the right-click popup retains/restores the underlying preview.
    context.aboutToHide.connect.call_args.args[0]()
    run_scheduled(queue)
    menu._keep_preview_visible.assert_called_once()


def test_file_right_click_shares_safe_search_menu(tmp_path):
    menu, launcher, _, action, queue, types, event = make_harness()
    file = tmp_path / 'info.txt'
    file.write_text('ok')
    menu._row_at.return_value = (action, (str(file), False))
    assert menu.eventFilter(menu, event(types.MouseButtonPress, 2))
    run_scheduled(queue)
    args, kwargs = launcher.show_launch_context_menu.call_args
    assert args[1]['_browse_file'] == str(file)
    assert kwargs['force_search_context'] is True


def test_context_menu_synthesis_is_suppressed(tmp_path):
    menu, _, _, action, queue, types, event = make_harness()
    menu._row_at.return_value = (action, None)
    assert menu.eventFilter(menu, event(types.ContextMenu))
    assert not queue
