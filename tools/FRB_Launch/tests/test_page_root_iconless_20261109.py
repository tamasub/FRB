"""Page roots lose the redundant folder glyph, not their Page emoji or tree behavior.

Qt-less isolation of the rendering method: Windows/PySide6 smoke is separate.
"""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from launch_virtual_tree import virtual_launch_pages


class Icon:
    def __init__(self, name=''):
        self.name = name


class Item:
    def __init__(self, icon=None, text=''):
        self.icon, self.text = icon, text
        self.data, self.children, self.tooltip = {}, [], ''

    def setEditable(self, value):
        self.editable = value

    def setDragEnabled(self, value):
        self.drag_enabled = value

    def setDropEnabled(self, value):
        self.drop_enabled = value

    def setData(self, value, role):
        self.data[role] = value

    def setToolTip(self, value):
        self.tooltip = value

    def appendRow(self, child):
        self.children.append(child)


class Parent:
    def __init__(self):
        self.children = []

    def appendRow(self, item):
        self.children.append(item)


def append_virtual():
    source = (ROOT / 'src' / 'remote_files_explorer.py').read_text(encoding='utf-8')
    module = ast.parse(source)
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef)
               and n.name == 'RemoteFilesExplorer')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                  and n.name == '_append_virtual')
    isolated = ast.Module(body=[method], type_ignores=[])
    ast.fix_missing_locations(isolated)
    from launch_virtual_tree import virtual_item_identity, virtual_exp_folders
    ctx = {'QStandardItem': Item, 'QIcon': Icon,
           '_DATA_ROLE': 1, '_NORMAL_ICON_ROLE': 2, '_LOADED_ROLE': 3,
           'virtual_item_identity': virtual_item_identity,
           'virtual_exp_folders': virtual_exp_folders}
    exec(compile(isolated, '<_append_virtual>', 'exec'), ctx)
    return ctx['_append_virtual']


def test_page_root_uses_label_emoji_but_no_extra_folder_icon():
    pages = [{'page_id': 'work', 'title': 'My Work', 'icon_key': '💼', 'enabled': True},
             {'page_id': 'windows', 'title': 'Windows', 'icon_key': '🪟', 'enabled': True}]
    rows = [{'page_id': 'work', 'item_id': 'tools', 'item_kind': 'category',
             'title': '道具', 'enabled': True}]
    root, other = virtual_launch_pages(pages, rows)
    render = append_virtual()
    parent = Parent()
    fake_self = SimpleNamespace(_folder_icon=Icon('folder'))
    rendered = render(fake_self, parent, root)
    assert rendered.icon.name == ''
    assert rendered.text == '💼 My Work'
    assert rendered.data[2].name == ''
    assert rendered.data[1]['virtual'] is root
    assert rendered.children  # Triangle/expansion remains available for child folders
    assert parent.children == [rendered]
    assert render(fake_self, parent, other).icon.name == ''


def test_nested_virtual_folders_still_get_folder_icon():
    nodes = virtual_launch_pages(
        [{'page_id': 'work', 'title': 'My Work', 'icon_key': '💼'}],
        [{'page_id': 'work', 'item_id': 'tools', 'item_kind': 'category',
          'title': '道具', 'enabled': True}])
    child = nodes[0]['children'][0]
    assert child['kind'] == 'folder'
    item = append_virtual()(SimpleNamespace(_folder_icon=Icon('folder')),
                            Parent(), child)
    assert item.icon.name == 'folder'
    assert item.data[2].name == 'folder'


def test_virtual_executable_rows_remain_excluded():
    nodes = virtual_launch_pages(
        [{'page_id': 'work', 'title': 'My Work'}],
        [{'page_id': 'work', 'item_id': 'cmd', 'item_kind': 'command',
          'title': 'Run', 'enabled': True}])
    child = nodes[0]['children'][0]
    assert child['kind'] == 'file'
    parent = Parent()
    assert append_virtual()(SimpleNamespace(_folder_icon=Icon('folder')),
                            parent, child) is None
    assert parent.children == []
