"""JSON menu fields replace Files metadata without changing source JSON or Files layout."""
import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from middle_column_presentation import (
    FILES_HEADERS, LAUNCH_HEADERS, virtual_description,
    virtual_item_kind, virtual_sort_mode_for_header)
from middle_folder_filter import filter_sort_folder_rows, sort_mode_for_header
from launch_virtual_tree import virtual_launch_pages, virtual_list_rows


def _test_node():
    source = [
        {'page_id': 'p', 'item_id': 'group', 'title': '実験装置',
         'item_kind': 'category', 'description': 'Wi-Fi接続と画面表示',
         'enabled': True, 'sort_order': 10},
        {'page_id': 'p', 'item_id': 'action', 'title': 'Wi-Fi切り替え',
         'item_kind': 'command', 'parent_item_id': 'group',
         'description': 'ESP32と接続する', 'enabled': True, 'sort_order': 20},
        {'page_id': 'p', 'item_id': 'submenu', 'title': '子を持つコマンド',
         'item_kind': 'command', 'description': '', 'enabled': True, 'sort_order': 30},
        {'page_id': 'p', 'item_id': 'child', 'title': '葉',
         'item_kind': 'selection', 'description': '選択リスト',
         'parent_item_id': 'submenu', 'enabled': True, 'sort_order': 40},
    ]
    pages = virtual_launch_pages([{'page_id': 'p', 'title': 'My Work',
                                   'enabled': True}], source)
    return pages[0], source


def test_json_description_and_original_item_kind_not_projected_kind():
    page, source = _test_node()
    rows = virtual_list_rows(page)
    assert [virtual_item_kind(r) for r in rows] == ['category', 'command']
    assert [virtual_description(r) for r in rows] == ['Wi-Fi接続と画面表示', '']
    # The command is projected as a navigable category because it has children,
    # but the List displays its JSON's original kind, not that projection.
    assert rows[1]['item_kind'] == 'category'
    assert virtual_item_kind(rows[1]) == 'command'
    assert source[2]['item_kind'] == 'command'
    child = virtual_list_rows(page['children'][0])[0]
    assert (virtual_description(child), virtual_item_kind(child)) == ('ESP32と接続する', 'command')


def test_virtual_sort_and_physical_sort_are_separate():
    assert FILES_HEADERS == ('名前', '更新日', 'サイズ', '種類', '')
    assert LAUNCH_HEADERS == ('名前', '説明', '項目の種類', '', '')
    assert sort_mode_for_header(1, 'name') == 'date_desc'
    assert sort_mode_for_header(2, 'name') == 'size_desc'
    assert virtual_sort_mode_for_header(1, 'name') == 'description_asc'
    assert virtual_sort_mode_for_header(1, 'description_asc') == 'description_desc'
    assert virtual_sort_mode_for_header(2, 'name') == 'item_kind_asc'
    assert virtual_sort_mode_for_header(2, 'item_kind_asc') == 'item_kind_desc'
    assert virtual_sort_mode_for_header(3, 'name') is None
    assert virtual_sort_mode_for_header(4, 'name') is None


def test_json_sort_uses_json_source_fields():
    a = {'title': 'Z', 'item_kind': 'category', 'description': 'zzz',
         '_launch_virtual_node': {'row': {'item_kind': 'selection'}}}
    b = {'title': 'A', 'item_kind': 'virtual_launch_file', 'description': 'aaa',
         '_launch_virtual_node': {'row': {'item_kind': 'command'}}}
    c = {'title': 'B', 'item_kind': 'virtual_launch_file', 'description': 'bbb',
         '_launch_virtual_node': {'row': {'item_kind': 'selection'}}}
    rows = [a, b, c]
    names = lambda mode: [r['title'] for r in filter_sort_folder_rows(rows, mode=mode)]
    assert names('description_asc') == ['Z', 'A', 'B']  # folders stay ahead
    assert names('description_desc') == ['Z', 'B', 'A']
    assert names('item_kind_asc') == ['Z', 'A', 'B']
    assert names('item_kind_desc') == ['Z', 'B', 'A']


def _method(name):
    path = ROOT / 'src' / 'expanded_view.py'
    module = ast.parse(path.read_text(encoding='utf-8'))
    cls = next(node for node in module.body if isinstance(node, ast.ClassDef)
               and node.name == 'ExpandedLauncherView')
    return next(node for node in cls.body if isinstance(node, ast.FunctionDef)
                and node.name == name)


def test_view_switch_keeps_physical_headers_and_saved_sizes():
    # Exercise the production switch body with a minimal Qt stand-in.
    class Header:
        def __init__(self):
            self.saved = ['physical-column-order-and-width']
            self.restore_count = 0

        def saveState(self):
            return self.saved.copy()

        def restoreState(self, state):
            self.saved = list(state)
            self.restore_count += 1
            return True

        def setSectionResizeMode(self, *args):
            pass

    class Tree:
        def __init__(self):
            self._header = Header()
            self.hidden = {}
            self.labels = None
            self.widths = {}

        def header(self):
            return self._header

        def setHeaderLabels(self, labels):
            self.labels = labels

        def setColumnHidden(self, index, hidden):
            self.hidden[index] = hidden

        def setColumnWidth(self, index, width):
            self.widths[index] = width

    class Self:
        def __init__(self):
            self.middle = type('P', (), {'tree': Tree(), 'virtual_details_columns': False})()
            self._middle_header_virtual = False
            self._middle_header_restoring = False
            self._physical_middle_header_state = None

    scope = {'QHeaderView': type('H', (), {'ResizeMode': type('R', (), {'Stretch': 'stretch'})}),
             'FILES_HEADERS': FILES_HEADERS, 'LAUNCH_HEADERS': LAUNCH_HEADERS}
    node = _method('_set_middle_columns_for_source')
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 'expanded_view.py', 'exec'), scope)
    switch = scope['_set_middle_columns_for_source']
    obj = Self()
    switch(obj, True)
    assert obj.middle.tree.labels == list(LAUNCH_HEADERS)
    assert obj.middle.tree.hidden[3] is True
    assert obj.middle.virtual_details_columns is True
    assert obj._physical_middle_header_state == ['physical-column-order-and-width']
    switch(obj, False)
    assert obj.middle.tree.labels == list(FILES_HEADERS)
    assert obj.middle.tree.hidden[3] is False
    assert obj.middle.virtual_details_columns is False
    assert obj.middle.tree._header.restore_count == 1
    assert obj._physical_middle_header_state is None
    assert obj._middle_header_restoring is False


def test_virtual_header_resizes_do_not_persist_files_layout():
    node = _method('_save_middle_header_state')
    scope = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 'expanded_view.py', 'exec'), scope)
    class Self:
        _middle_header_restoring = False
        _middle_header_virtual = True
    obj = Self()
    obj.launcher = type('L', (), {'settings': type('S', (), {
        'setValue': lambda *args: (_ for _ in ()).throw(AssertionError('saved virtual state'))})()})()
    scope['_save_middle_header_state'](obj)


def test_view_wiring_uses_virtual_headers_and_unmodified_files_headers():
    source = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
    assert 'self._set_middle_columns_for_source(virtual is not None)' in source
    assert 'virtual_description(row)' in source
    assert 'virtual_item_kind(row)' in source
    # Move owns the JSON order: virtual header sorting is intentionally disabled.
    assert 'virtual_sort_mode_for_header(logical_column, self._middle_sort_mode)' not in source
    assert 'self.middle.tree.header().setSortIndicatorShown(False)' in source
    assert "tree.setHeaderLabels(['名前', '更新日', 'サイズ', '種類', ''])" in source
