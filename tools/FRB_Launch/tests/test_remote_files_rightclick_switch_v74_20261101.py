"""v74: Files remote right click switches from Browser without HOME reset.

Uses the actual Launcher method through AST extraction with lightweight fakes,
so tests do not require Windows, PySide6, or a filesystem at F:/.
"""
import ast
import os
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text('utf-8')


def files_right_click_method():
    module = ast.parse(SOURCE)
    launcher = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    fn = next(n for n in launcher.body if isinstance(n, ast.FunctionDef)
              and n.name == 'show_remote_files_first_column_menu')
    env = {'QPoint': lambda x, y: (x, y), 'os': os,
           'RemoteFolderCascade': FakeCascade}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 '<real-files-rightclick>', 'exec'), env)
    return env[fn.name]


class FakeCascade:
    created = []

    def __init__(self, parent=None, launcher=None):
        self.parent, self.launcher = parent, launcher
        self.aboutToHide = NS(connect=Mock())
        self.popup = Mock()
        self.setFocus = Mock()
        FakeCascade.created.append(self)


class FakeButton:
    def width(self):
        return 85

    def mapToGlobal(self, position):
        return ('files_button_edge', position)


def make_launcher(start_mode='browser', roots=3):
    actions = []
    view = NS(_workspace_mode=start_mode, files_root={'item_id': 'files'},
              left=NS(tree=NS(topLevelItemCount=lambda: roots)),
              current_directory=lambda: 'F:/FRB/KEEP', isVisible=lambda: True)

    def switch_to_files():
        actions.append('switch_to_files')
        view._workspace_mode = 'files'

    view.show_files_view = Mock(side_effect=switch_to_files)
    remote = NS(isVisible=lambda: True, files_button=FakeButton())
    earlier_popup = NS(close=Mock(side_effect=lambda: actions.append('close_earlier_popup')))
    launcher = NS(
        remote_window=remote, expanded_view=view, menu=earlier_popup,
        close_remote_page_menu=Mock(side_effect=lambda: actions.append('close_browser_bookmarks')),
        close_remote_folder_menu=Mock(side_effect=lambda: actions.append('close_files_popups')),
        _apply_remote_popup_bounds=lambda menu: menu,
        fill_cascade=Mock(side_effect=lambda menu, root: actions.append('fill_files_root')),
        _remote_folder_root_hidden=Mock(),
    )
    return launcher, actions


def test_browser_to_files_switches_before_showing_roots_and_preserves_breadcrumb():
    FakeCascade.created.clear()
    launcher, actions = make_launcher('browser')
    directory_before = launcher.expanded_view.current_directory()
    files_right_click_method()(launcher)
    assert launcher.expanded_view._workspace_mode == 'files'
    launcher.expanded_view.show_files_view.assert_called_once_with()
    assert actions == ['close_browser_bookmarks', 'close_earlier_popup',
                       'switch_to_files', 'close_files_popups', 'fill_files_root']
    assert launcher.expanded_view.current_directory() == directory_before
    popup = FakeCascade.created[0]
    assert popup.remote_files_roots is True
    assert popup.remote_folder_root is popup
    assert popup.remote_folder_navigation is True
    assert launcher._remote_folder_root_menu is popup
    assert launcher.fill_cascade.call_args.args[1]['launch_source'] == 'remote_files_roots'
    popup.popup.assert_called_once_with(('files_button_edge', (84, 0)))
    popup.setFocus.assert_called_once()


def test_files_to_files_does_not_reset_current_directory_or_run_home():
    launcher, actions = make_launcher('files')
    files_right_click_method()(launcher)
    launcher.expanded_view.show_files_view.assert_not_called()
    assert 'fill_files_root' in actions
    assert 'switch_to_files' not in actions


def test_missing_file_roots_does_not_show_empty_menu_after_switch():
    FakeCascade.created.clear()
    launcher, actions = make_launcher('browser', roots=0)
    files_right_click_method()(launcher)
    assert launcher.expanded_view._workspace_mode == 'files'
    assert 'fill_files_root' not in actions
    assert not FakeCascade.created


def test_unavailable_remote_does_not_switch_files():
    for remote_visible, expanded_visible in ((False, True), (True, False)):
        launcher, actions = make_launcher('browser')
        launcher.remote_window.isVisible = lambda: remote_visible
        launcher.expanded_view.isVisible = lambda: expanded_visible
        files_right_click_method()(launcher)
        assert actions == []
        launcher.expanded_view.show_files_view.assert_not_called()
