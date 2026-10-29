"""Main-search 'フォルダーを開く' should navigate in Files, with its own history."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from directory_address import directory_row
from directory_navigation_history import DirectoryNavigationHistory
from expanded_view_model import expanded_targets
from context_menu_config import load_context_menus, visible_context_entries
from context_menu_resolver import resolve_context_target
from context_menu_actions import is_downloads_zip

SOURCE = (ROOT / 'src/app.py').read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)
LAUNCHER = next(node for node in TREE.body if isinstance(node, ast.ClassDef)
                and node.name == 'Launcher')


def method(name, scope):
    fn = next(node for node in LAUNCHER.body if isinstance(node, ast.FunctionDef)
              and node.name == name)
    program = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    exec(compile(program, '<launcher isolated>', 'exec'), scope)
    return scope[name]


class FakeMenu:
    def __init__(self, parent):
        self.actions = []
    def addAction(self, title, callback):
        self.actions.append((title, callback))
        return Mock()
    def addSeparator(self):
        self.actions.append(('---', None))
    def isEmpty(self):
        return not self.actions
    def popup(self, pos):
        pass


def menu_fixture(query):
    opts = ROOT / 'config/context_menu_options.json'
    scope = {'QMenu': FakeMenu, 'resolve_context_target': resolve_context_target,
             'load_context_menus': load_context_menus,
             'visible_context_entries': visible_context_entries,
             'CONTEXT_MENU_OPTIONS': opts, 'context_action_icon': Mock(),
             'is_downloads_zip': is_downloads_zip, 'Path': Path}
    call_menu = method('show_launch_context_menu', scope)
    view = SimpleNamespace(
        data={'items': [{}]}, selection=None, authored_items=[],
        search=SimpleNamespace(text=lambda: query),
        hover_timer=SimpleNamespace(stop=Mock()),
        _context_paste_enabled=Mock(return_value=False),
        _paste_from_context_menu=Mock(),
        perform_filesystem_context_action=Mock(),
        open_search_file_parent_in_launch=Mock(),
        add_open_with_submenu=lambda m, title, p: m.addAction(title, lambda: None),
    )
    return call_menu, view


def test_only_main_search_routes_file_parent_inside_launch():
    row = {'item_id': '__file_index_report', '_indexed_file': r'C:\Work Files\report.txt'}
    call_menu, launcher = menu_fixture('report')
    assert call_menu(launcher, (20, 30), row)
    callback = next(cb for title, cb in launcher._launch_context_menu.actions
                    if title == 'フォルダーを開く')
    callback(True)
    launcher.open_search_file_parent_in_launch.assert_called_once_with(row['_indexed_file'])
    launcher.perform_filesystem_context_action.assert_not_called()

    call_menu, launcher = menu_fixture('')
    assert call_menu(launcher, (20, 30), row, context_parent=launcher)
    callback = next(cb for title, cb in launcher._launch_context_menu.actions
                    if title == 'フォルダーを開く')
    callback(True)
    launcher.perform_filesystem_context_action.assert_called_once_with(
        'open_parent_folder', row['_indexed_file'], 'file')
    launcher.open_search_file_parent_in_launch.assert_not_called()


def test_search_folder_transition_is_one_history_entry_and_back_forward_work():
    directory = r'D:\SharePoint\Team Docs\Monthly Reports'
    filename = directory + r'\売上 2026.xlsx'

    class RealisticWindowsPath:
        def __init__(self, name):
            self.parent = type('Parent', (), {'__str__': lambda self: directory,
                                              'is_dir': lambda self: True})()

    class View:
        def __init__(self):
            self.path = [directory_row(r'C:\Work')]
            self.history = DirectoryNavigationHistory(100)
            self.history.record(r'C:\Work', self.path)
            self.visible = False
            self.render_count = 0
            self.select_middle_file = Mock(return_value=True)
        def isVisible(self):
            return self.visible
        def refresh_middle(self):
            self.history.record(self.path[-1]['launch_browse_target'], self.path)
        def go_to_directory(self, path):
            self.path = [directory_row(path)]
            self.refresh_middle()
            return True

    view = View()
    launcher = SimpleNamespace()
    launcher.data = {'items': []}
    launcher.pages = [{'page_id': 'work'}]
    launcher.view_mode = 'classic'
    launcher.page_id = 'other'
    launcher.expanded_view = view
    launcher.stack = ['search navigation']
    launcher.selection = None
    launcher.checked = {'old selection'}
    launcher.search = SimpleNamespace(text=lambda: '売上', clear=lambda: setattr(launcher.search, 'text', lambda: ''))
    launcher.tabs = SimpleNamespace(blockSignals=Mock(), setCurrentIndex=Mock())
    launcher.footer = SimpleNamespace(setText=Mock())
    launcher._launch_context_menu = SimpleNamespace(close=Mock())
    launcher.close_cascade_for_main_interaction = Mock()
    launcher.hide_history_popup = Mock()
    launcher.hover_timer = SimpleNamespace(stop=Mock())
    launcher.error = Mock()
    launcher._read_expanded_options = lambda: {'enabled': True, 'page_id': 'work'}
    launcher.render = lambda: (setattr(view, 'visible', launcher.view_mode == 'expanded'
                                and launcher.page_id == 'work' and not launcher.search.text()),
                                view.refresh_middle() if launcher.view_mode == 'expanded'
                                and launcher.page_id == 'work' and not launcher.search.text() else None)
    def switch_to_expanded(value):
        launcher.view_mode = value
        launcher.render()
    launcher.set_view_mode = Mock(side_effect=switch_to_expanded)

    scope = {'Path': RealisticWindowsPath, 'expanded_targets': lambda rows, opts: (1, 2, 3)}
    enter = method('open_search_file_parent_in_launch', scope)
    assert enter(launcher, filename)
    assert view.path[-1]['launch_browse_target'] == directory
    assert view.isVisible()
    assert launcher.page_id == 'work'
    assert launcher.search.text() == ''
    assert launcher.stack == []
    assert not launcher.checked
    assert launcher.tabs.setCurrentIndex.call_args.args == (0,)
    assert len(view.history.entries) == 2  # no intermediate default folder
    assert view.history.current['path'] == directory
    view.select_middle_file.assert_called_once_with(filename)
    assert view.history.back()['path'] == r'C:\Work'
    assert view.history.forward()['path'] == directory
    assert not view.history.can_forward
    launcher.error.assert_not_called()


def test_missing_path_does_not_navigate_or_misrepresent_success():
    scope = {'Path': lambda text: SimpleNamespace(parent=SimpleNamespace(is_dir=lambda: False))}
    enter = method('open_search_file_parent_in_launch', scope)
    launcher = SimpleNamespace(error=Mock(), render=Mock())
    assert not enter(launcher, r'C:\missing\file.txt')
    launcher.error.assert_called_once()
    launcher.render.assert_not_called()


def test_existing_files_history_refresh_still_registers_all_folder_sources():
    view_source = (ROOT / 'src/expanded_view.py').read_text('utf-8')
    assert 'self.directory_history.record(' in view_source
    assert 'self.current_directory(), self.path,' in view_source
    assert "self.expanded_view.go_to_directory(str(parent))" in SOURCE
    assert "self.expanded_view.path = [directory_row(str(parent))]" in SOURCE
