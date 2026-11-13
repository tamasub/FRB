"""Files Left-arrow behavior using actual production handlers without PySide6."""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from directory_address import directory_row, row_directory
from expanded_left_navigation import matching_first_row, has_first_row_ancestor
from remote_navigation import starting_area, next_area, previous_area
from expanded_keyboard_model import row_right_action, root_step


def extract_method(file, cls, name, env):
    nodes = ast.parse((ROOT / 'src' / file).read_text('utf-8'))
    owner = next(n for n in nodes.body if isinstance(n, ast.ClassDef) and n.name == cls)
    target = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == name)
    block = ast.fix_missing_locations(ast.Module(body=[target], type_ignores=[]))
    ns = dict(env)
    exec(compile(block, file, 'exec'), ns)
    return ns[name]


class Item:
    def __init__(self, row):
        self.row = row


class Tree:
    def __init__(self, rows):
        self.rows = [Item(r) for r in rows]
        self.current = self.rows[0] if self.rows else None
        self.focused = False
    def currentItem(self): return self.current
    def setCurrentItem(self, item): self.current = item
    def topLevelItemCount(self): return len(self.rows)
    def topLevelItem(self, index): return self.rows[index]
    def scrollToItem(self, item): pass
    def setFocus(self, *args): self.focused = True


class Timer:
    def __init__(self): self.pending = []
    def singleShot(self, delay, fn):
        assert delay == 0
        self.pending.append(fn)
    def flush(self):
        while self.pending:
            self.pending.pop(0)()


def make_view(first_rows, path, child_rows):
    timer = Timer()
    left = NS(tree=Tree(first_rows))
    middle = NS(tree=Tree(child_rows[path[-1]['item_id']]))
    view = NS(left=left, middle=middle, path=list(path),
              row_data=lambda item: item.row if item is not None else None,
              launcher=NS(expander=lambda: NS(expand=lambda x: x)),
              history_back=Mock(), history_forward=Mock())
    view.current_directory = lambda: row_directory(view.path[-1]) if view.path else None
    view.focus_panel = lambda pane: pane.tree.setFocus()
    def refresh_middle():
        middle.tree = Tree(child_rows[view.path[-1]['item_id']])
    view.refresh_middle = Mock(side_effect=refresh_middle)
    nav = extract_method('expanded_view.py', 'ExpandedLauncherView', 'navigate_left_from_middle', {
        'matching_first_row': matching_first_row,
        'has_first_row_ancestor': has_first_row_ancestor,
        'directory_row': directory_row,
        'QTimer': timer,
    })
    view.navigate_left_from_middle = lambda: nav(view)
    return view, timer


def test_windows_case_and_virtual_row_matching_without_history():
    first = [directory_row(r'C:\Different'), directory_row(r'F:\FRB\tools\FRBStudio_App')]
    assert matching_first_row(directory_row('f:/frb/TOOLS/frbstudio_app/'), first) == 1
    assert matching_first_row(directory_row(r'F:\Unrelated'), first) is None
    assert matching_first_row({'item_kind': 'category', 'item_id': 'virtual-A'},
                              [{'item_kind': 'category', 'item_id': 'virtual-A'}]) == 0
    assert has_first_row_ancestor(r'F:\FRB\tools\FRBStudio_App\data\json', first)
    assert not has_first_row_ancestor(r'G:\Other\data\json', first)
    assert not has_first_row_ancestor(r'F:\FRB\tools\FRBStudio_AppBackup', first)


def test_middle_bottom_row_then_parent_then_matching_first_column():
    root = directory_row(r'F:\FRB\tools\FRBStudio_App')
    subfolder = directory_row(r'F:\FRB\tools\FRBStudio_App\data')
    listing = {
        root['item_id']: [directory_row(r'F:\FRB\tools\FRBStudio_App\.obsidian'), subfolder],
        subfolder['item_id']: [directory_row(r'F:\FRB\tools\FRBStudio_App\data\json'),
                               directory_row(r'F:\FRB\tools\FRBStudio_App\data\more')],
    }
    first = [directory_row(r'F:\Another'), root, directory_row(r'C:\Other')]
    view, timer = make_view(first, [root, subfolder], listing)
    view.middle.tree.setCurrentItem(view.middle.tree.topLevelItem(1))

    # Step 1: only select top row, no history and no directory refresh.
    assert view.navigate_left_from_middle() == 'directory'
    assert view.middle.tree.currentItem() is view.middle.tree.topLevelItem(0)
    assert view.path == [root, subfolder]
    view.refresh_middle.assert_not_called()

    # Step 2: climb one parent and highlight the folder we just exited.
    assert view.navigate_left_from_middle() == 'directory'
    assert view.path == [root]
    assert len(timer.pending) == 1
    timer.flush()
    assert view.refresh_middle.call_count == 1
    assert view.middle.tree.currentItem() is view.middle.tree.topLevelItem(1)
    assert view.middle.tree.currentItem().row == subfolder
    assert view.middle.tree.focused

    # Step 3: the previous folder is now highlighted at row 2; as specified,
    # Left first moves back to row 1 before leaving the second column.
    assert view.navigate_left_from_middle() == 'directory'
    assert view.middle.tree.currentItem() is view.middle.tree.topLevelItem(0)

    # Step 4: current directory is an authored Files shortcut; focus it.
    assert view.navigate_left_from_middle() == 'files'
    assert view.left.tree.currentItem() is view.left.tree.topLevelItem(1)
    assert view.left.tree.focused
    assert view.path == [root]
    view.history_back.assert_not_called()


def test_direct_directory_beneath_first_column_unwinds_real_ancestors():
    root = directory_row(r'F:\FRB\tools\FRBStudio_App')
    direct = directory_row(r'F:\FRB\tools\FRBStudio_App\data\json')
    parent = directory_row(r'F:\FRB\tools\FRBStudio_App\data')
    listing = {
        direct['item_id']: [directory_row(direct['item_id'] + r'\a')],
        parent['item_id']: [directory_row(parent['item_id'] + r'\json')],
        root['item_id']: [directory_row(root['item_id'] + r'\data')],
    }
    view, timer = make_view([root], [direct], listing)
    assert view.navigate_left_from_middle() == 'directory'
    assert view.path[-1]['item_id'] == parent['item_id']
    timer.flush()
    assert view.navigate_left_from_middle() == 'directory'
    assert view.path[-1]['item_id'] == root['item_id']
    timer.flush()
    assert view.navigate_left_from_middle() == 'files'
    assert view.left.tree.currentItem() is view.left.tree.topLevelItem(0)


def test_return_from_config_selects_config_in_parent_not_first_file():
    """User case: config's contents -> parent, config current."""
    root = directory_row(r'F:\FRB\tools\FRB_Launch')
    config = directory_row(r'F:\FRB\tools\FRB_Launch\config')
    first_file = {'item_id': 'context_menu_options.json', 'item_kind': 'file',
                  'title': 'context_menu_options.json'}
    listing = {
        config['item_id']: [first_file, {'item_id': 'expanded_view_options.json',
                                         'item_kind': 'file'}],
        root['item_id']: [directory_row(r'F:\FRB\tools\FRB_Launch\app_zip'),
                          directory_row(r'F:\FRB\tools\FRB_Launch\config'),
                          directory_row(r'F:\FRB\tools\FRB_Launch\src')],
    }
    view, timer = make_view([root], [root, config], listing)
    # Current is the first file in config, so Left ascends immediately.
    assert view.navigate_left_from_middle() == 'directory'
    assert view.path == [root]
    timer.flush()
    assert view.middle.tree.currentItem().row['title'] == 'config'
    assert view.middle.tree.currentItem() is view.middle.tree.topLevelItem(1)
    assert view.middle.tree.focused
    view.history_back.assert_not_called()


def test_direct_config_address_selects_config_on_ascending():
    root = directory_row(r'F:\FRB\tools\FRB_Launch')
    config = directory_row(r'F:\FRB\tools\FRB_Launch\config')
    listing = {
        config['item_id']: [directory_row(config['item_id'] + r'\sub')],
        root['item_id']: [directory_row(root['item_id'] + r'\app_zip'),
                          directory_row(root['item_id'] + r'\CONFIG')],
    }
    view, timer = make_view([root], [config], listing)
    assert view.navigate_left_from_middle() == 'directory'
    timer.flush()
    assert view.path[-1]['item_id'] == root['item_id']
    # Matching uses Windows paths (case-insensitive), not old click history.
    assert view.middle.tree.currentItem().row['title'] == 'CONFIG'
    assert view.middle.tree.currentItem() is view.middle.tree.topLevelItem(1)


def test_ascending_missing_child_in_parent_listing_falls_back_to_first_row():
    root = directory_row(r'F:\FRB\tools\FRB_Launch')
    config = directory_row(r'F:\FRB\tools\FRB_Launch\config')
    listing = {
        config['item_id']: [directory_row(config['item_id'] + r'\sub')],
        root['item_id']: [directory_row(root['item_id'] + r'\src'),
                          directory_row(root['item_id'] + r'\tests')],
    }
    view, timer = make_view([root], [root, config], listing)
    assert view.navigate_left_from_middle() == 'directory'
    timer.flush()
    assert view.middle.tree.currentItem() is view.middle.tree.topLevelItem(0)


def test_unrelated_direct_directory_climbs_to_drive_root_then_first_row():
    """No origin tracking: even unregistered direct paths must never dead-end."""
    current = directory_row(r'G:\Something\NotFromFiles')
    parent = directory_row(r'G:\Something')
    drive = directory_row('G:\\')
    first = [directory_row(r'F:\FRB'), directory_row(r'C:\Elsewhere')]
    listing = {
        current['item_id']: [directory_row(current['item_id'] + r'\child')],
        parent['item_id']: [directory_row(current['item_id'])],
        drive['item_id']: [directory_row(parent['item_id'])],
    }
    view, timer = make_view(first, [current], listing)
    view.left.tree.setCurrentItem(view.left.tree.topLevelItem(1))

    # Left must NOT jump straight to first column just because no Files root
    # matches the direct address. It climbs through the actual hierarchy.
    assert view.navigate_left_from_middle() == 'directory'
    assert view.path[-1]['item_id'] == parent['item_id']
    timer.flush()
    assert view.middle.tree.currentItem().row['item_id'] == current['item_id']
    # Selected child is not the first row? Here only one, so we can ascend.
    assert view.navigate_left_from_middle() == 'directory'
    assert view.path[-1]['item_id'] == drive['item_id']
    timer.flush()
    assert view.middle.tree.currentItem().row['item_id'] == parent['item_id']

    # The filesystem root is not a registered first-column folder. Now fall
    # back to row one, irrespective of whichever first-column row was selected.
    assert view.navigate_left_from_middle() == 'files'
    assert view.left.tree.currentItem() is view.left.tree.topLevelItem(0)
    assert view.path[-1]['item_id'] == drive['item_id']
    view.history_back.assert_not_called()


def test_direct_address_outside_first_column_is_identical_to_folder_navigation():
    """A regular folder path chain and a direct address use the same policy."""
    current = directory_row(r'G:\Something\NotFromFiles')
    parent = directory_row(r'G:\Something')
    drive = directory_row('G:\\')
    first = [directory_row(r'F:\FRB')]
    listing = {
        current['item_id']: [],
        parent['item_id']: [current],
        drive['item_id']: [parent],
    }
    direct_view, direct_timer = make_view(first, [current], listing)
    entered_view, entered_timer = make_view(first, [drive, parent, current], listing)
    for view, timer in ((direct_view, direct_timer), (entered_view, entered_timer)):
        assert view.navigate_left_from_middle() == 'directory'
        timer.flush()
        assert view.middle.tree.currentItem().row == current
        assert view.navigate_left_from_middle() == 'directory'
        timer.flush()
        assert view.middle.tree.currentItem().row == parent
        assert view.navigate_left_from_middle() == 'files'
        assert view.left.tree.currentItem() is view.left.tree.topLevelItem(0)


def test_drive_root_direct_address_falls_back_to_first_row():
    drive = directory_row('G:\\')
    first = [directory_row(r'F:\FRB'), directory_row(r'C:\Elsewhere')]
    view, timer = make_view(first, [drive], {drive['item_id']: []})
    view.left.tree.setCurrentItem(view.left.tree.topLevelItem(1))
    assert view.navigate_left_from_middle() == 'files'
    assert view.left.tree.currentItem() is view.left.tree.topLevelItem(0)
    assert not timer.pending


def test_empty_middle_can_return_directly_to_first_column():
    root = directory_row(r'F:\FRB')
    view, _ = make_view([directory_row(r'D:\Other'), root], [root], {root['item_id']: []})
    assert view.navigate_left_from_middle() == 'files'
    assert view.left.tree.currentItem() is view.left.tree.topLevelItem(1)


def test_keyboard_and_remote_left_call_identical_hierarchy_method():
    from test_expanded_keyboard_dispatch_20261024 import dispatch_class, instance, event
    d = instance()
    d.expanded_tree_key(d.expanded_view.middle.tree, event('Left'))
    assert d.expanded_view.actions == [('left_hierarchy',)]
    d.remote_window = NS(isVisible=lambda: True, set_area=Mock())
    d._remote_area = 'directory'
    d.expanded_tree_key(d.expanded_view.middle.tree, event('Left'))
    d.remote_window.set_area.assert_called_once_with('directory')
    d.remote_window.set_area.reset_mock()
    d.expanded_view.navigate_left_from_middle = lambda: 'files'
    d.expanded_tree_key(d.expanded_view.middle.tree, event('Left'))
    assert d._remote_area == 'files'
    d.remote_window.set_area.assert_called_once_with('files')

    remote_command = extract_method('app.py', 'Launcher', 'remote_command', {
        'starting_area': starting_area, 'previous_area': previous_area,
        'next_area': next_area, 'row_right_action': row_right_action,
        'root_step': root_step})
    view = NS(isVisible=lambda: True,
              left=NS(tree=Tree([])), middle=NS(tree=Tree([])), right=NS(tree=Tree([])),
              navigate_left_from_middle=Mock(return_value='files'))
    app = NS(expanded_view=view, _remote_area='directory', _last_focus_area='directory',
             _remote_mouse_last_click=None, _remote_mouse_menu_click=None,
             _remote_popup_area=None, menu=None,
             isVisible=lambda: True, isMinimized=lambda: False,
             remote_cascade_command=Mock(return_value=False), remote_focus_area=Mock())
    remote_command(app, 'LEFT')
    view.navigate_left_from_middle.assert_called_once()
    app.remote_focus_area.assert_called_once_with('files')
    view.navigate_left_from_middle.reset_mock(return_value=True)
    view.navigate_left_from_middle.return_value = 'directory'
    app.remote_focus_area.reset_mock()
    remote_command(app, 'LEFT')
    view.navigate_left_from_middle.assert_called_once()
    app.remote_focus_area.assert_not_called()


def test_toolbar_visit_history_remains_separate_from_left_arrow():
    app = (ROOT / 'src/app.py').read_text('utf-8')
    assert 'self.expanded_view.history_back()' in app
    assert 'self.expanded_view.history_forward()' in app
    assert 'view.navigate_left_from_middle()' in app
    # Never repurpose the breadcrumb up button as visit-history navigation.
    view = (ROOT / 'src/expanded_view.py').read_text('utf-8')
    assert 'self.middle.back.clicked.connect(self.go_up)' in view


def test_direct_virtual_category_returns_to_matching_first_row():
    category = {'item_kind': 'category', 'item_id': 'tools-group', 'title': 'Tools'}
    view, timer = make_view([{'item_kind': 'category', 'item_id': 'other'}, category],
                             [category], {'tools-group': [{'item_kind': 'command', 'item_id': 'build'}]})
    assert view.navigate_left_from_middle() == 'files'
    assert view.left.tree.currentItem() is view.left.tree.topLevelItem(1)
    assert not timer.pending


def test_remote_left_from_first_column_never_uses_history():
    remote_command = extract_method('app.py', 'Launcher', 'remote_command', {
        'starting_area': starting_area, 'previous_area': previous_area,
        'next_area': next_area, 'row_right_action': row_right_action, 'root_step': root_step})
    view = NS(isVisible=lambda: True, left=NS(tree=Tree([])),
              middle=NS(tree=Tree([])), right=NS(tree=Tree([])),
              history_back=Mock(), navigate_left_from_middle=Mock())
    app = NS(expanded_view=view, _remote_area='files', _last_focus_area='files',
             _remote_mouse_last_click=None, _remote_mouse_menu_click=None,
             _remote_popup_area=None, menu=None,
             isVisible=lambda: True, isMinimized=lambda: False,
             remote_cascade_command=Mock(return_value=False), remote_focus_area=Mock())
    remote_command(app, 'LEFT')
    view.history_back.assert_not_called()
    view.navigate_left_from_middle.assert_not_called()
    app.remote_focus_area.assert_not_called()
