"""Explorer-only back/forward stack and UI wiring regression tests."""
import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from directory_navigation_history import DirectoryNavigationHistory


def row(name):
    return {'item_kind': 'directory', 'item_id': name}


def test_first_column_and_subfolder_navigation_are_history_entries():
    history = DirectoryNavigationHistory()
    assert history.record(r'C:\Work A', [row('files_A')], 'files_A')
    assert history.record(r'D:\Shared Space', [row('files_B')], 'files_B')
    assert history.record(r'D:\Shared Space\Reports', [row('files_B'), row('reports')], 'files_B')
    assert history.can_back and not history.can_forward
    assert history.back()['path'] == r'D:\Shared Space'
    assert history.back()['path'] == r'C:\Work A'
    assert not history.can_back
    assert history.forward()['path'] == r'D:\Shared Space'
    assert history.forward()['path'] == r'D:\Shared Space\Reports'
    assert not history.can_forward


def test_refresh_does_not_record_and_case_insensitive_windows_paths():
    history = DirectoryNavigationHistory()
    history.record(r'C:\Work\Folder', [row('a')], 'a')
    assert not history.record(r'c:\WORK\FOLDER\\', [row('b')], 'b')
    assert len(history.entries) == 1
    assert history.current['root_id'] == 'b'  # latest selection is preserved


def test_branch_clears_forward_and_maximum_100_entries():
    history = DirectoryNavigationHistory(100)
    for idx in range(105):
        history.record(r'C:\Folder' + str(idx), [row(str(idx))])
    assert len(history.entries) == 100
    assert history.entries[0]['path'] == r'C:\Folder5'
    assert history.back()['path'] == r'C:\Folder103'
    history.record(r'C:\Elsewhere', [row('elsewhere')])
    assert not history.can_forward
    assert history.current['path'] == r'C:\Elsewhere'
    assert history.entries[-1]['root_id'] is None


def test_virtual_category_can_be_revisited_and_no_empty_location():
    history = DirectoryNavigationHistory()
    assert not history.record(None, [])
    assert history.record(None, [row('virtual-root')])
    assert history.record(r'\\server\share\Box folder', [row('network')])
    assert history.back()['key'] == ('virtual', ('virtual-root',))


def test_ui_wiring_and_up_vs_back_are_separate():
    app = (ROOT / 'src/app.py').read_text('utf-8')
    view = (ROOT / 'src/expanded_view.py').read_text('utf-8')
    for file in (app, view):
        ast.parse(file)
    assert "(self.nav_back_button, 'back_arrow')" in app
    assert "(self.nav_forward_button, 'forward')" in app
    assert "(self.nav_home_button, 'home')" in app
    assert 'self.nav_forward_button.clicked.connect(self.navigate_forward)' in app
    assert 'self.expanded_view.history_back()' in app
    assert 'self.expanded_view.history_forward()' in app
    assert 'self.nav_forward_button.setVisible(explorer)' in app
    assert 'self.directory_history.record(' in view
    assert 'def history_back(self):' in view
    assert 'def history_forward(self):' in view
    assert 'self.middle.back.clicked.connect(self.go_up)' in view
    assert "pane.back.setIcon(browser_navigation_icon('back', theme_family(theme)))" in view


def test_actual_files_first_column_handler_records_and_restores_directory():
    """Execute the real View methods without needing PySide6 on CI."""
    from types import SimpleNamespace
    from directory_address import row_directory, directory_row
    source = ast.parse((ROOT / 'src/expanded_view.py').read_text('utf-8'))
    widget = next(n for n in source.body if isinstance(n, ast.ClassDef)
                  and n.name == 'ExpandedLauncherView')
    wanted = {'choose_files', 'refresh_middle', 'current_directory',
              '_restore_directory_history', 'history_back', 'history_forward'}
    mock_class = ast.ClassDef(name='MockView', bases=[], keywords=[],
                             body=[n for n in widget.body
                                   if isinstance(n, ast.FunctionDef) and n.name in wanted],
                             decorator_list=[])
    module = ast.fix_missing_locations(ast.Module(body=[mock_class], type_ignores=[]))
    ns = {'row_directory': row_directory}
    exec(compile(module, '<view-explorer-history>', 'exec'), ns)
    view = ns['MockView']()

    class Tree:
        def __init__(self, rows):
            self.items = [SimpleNamespace(row=r) for r in rows]
            self.current = self.items[0]
        def currentItem(self): return self.current
        def setCurrentItem(self, item): self.current = item
        def topLevelItemCount(self): return len(self.items)
        def topLevelItem(self, index): return self.items[index]
        def clear(self): pass

    roots = [directory_row(r'C:\Box Folder'), directory_row(r'D:\Shared Folder')]
    view.left = SimpleNamespace(tree=Tree(roots))
    view.middle = SimpleNamespace(label=SimpleNamespace(setText=lambda *a: None),
        back=SimpleNamespace(setEnabled=lambda *a: None),
        fill=lambda *a: None, tree=SimpleNamespace(clear=lambda: None))
    view.address_bar = SimpleNamespace(set_directory=lambda *a: None)
    view.path = []
    view.directory_history = DirectoryNavigationHistory()
    view._restoring_directory_history = False
    view._middle_back_hold = SimpleNamespace(reset=lambda: None)
    view.update_directory_favorite_button = lambda: None
    view.browser_rows = lambda row: []
    view.row_data = lambda item: item.row
    view.focus_panel = lambda panel: None
    view.launcher = SimpleNamespace(expander=lambda: SimpleNamespace(expand=lambda s: s),
        row_icon=lambda r: None, _nav_update_buttons=lambda: None)
    assert view.current_directory() is None
    view.choose_files(view.left.tree.current, 0)
    assert view.current_directory() == r'C:\Box Folder'
    view.left.tree.setCurrentItem(view.left.tree.items[1])
    view.choose_files(view.left.tree.current, 0)
    assert view.current_directory() == r'D:\Shared Folder'
    assert len(view.directory_history.entries) == 2
    view.refresh_middle()  # F5 is not a new destination.
    assert len(view.directory_history.entries) == 2
    assert view.history_back()
    assert view.current_directory() == r'C:\Box Folder'
    assert view.left.tree.currentItem() is view.left.tree.items[0]
    assert view.history_forward()
    assert view.current_directory() == r'D:\Shared Folder'
