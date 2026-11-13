"""File multi-selection outbound drag; fake Qt allows running on Linux CI."""
from pathlib import Path
import importlib.util
import sys
from types import ModuleType, SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from file_drag_paths import file_paths_for_drag


def _row(path):
    return {'item_kind': 'command', '_browse_file': str(path)}


def test_file_only_order_dedup_and_non_file_rows(tmp_path):
    first, second = tmp_path / 'first.md', tmp_path / 'second_日本語.txt'
    first.write_text('first', encoding='utf-8')
    second.write_text('second', encoding='utf-8')
    actual = file_paths_for_drag([
        _row(second), {'item_kind':'directory', '_browse_file':str(tmp_path)},
        _row(first), _row(second), {'item_kind':'command', 'title':'not real'},
    ])
    assert actual == [str(second.resolve()), str(first.resolve())]


def _load_fake_qt_file_drag(monkeypatch):
    drops = []

    class Mime:
        def __init__(self):
            self.urls = None
            self.data = {}
        def setUrls(self, urls):
            self.urls = urls
        def setData(self, name, data):
            self.data[name] = data

    class Drag:
        def __init__(self, widget):
            self.widget = widget
            self.mime = None
            drops.append(self)
        def setMimeData(self, mime):
            self.mime = mime
        def exec(self, *actions):
            self.actions = actions

    class Tree:
        pass

    qt = SimpleNamespace(
        ItemDataRole=SimpleNamespace(UserRole=32),
        DropAction=SimpleNamespace(CopyAction=1),
    )
    for name in ('PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets'):
        module = ModuleType(name)
        monkeypatch.setitem(sys.modules, name, module)
    sys.modules['PySide6.QtCore'].Qt = qt
    sys.modules['PySide6.QtCore'].QMimeData = Mime
    sys.modules['PySide6.QtCore'].QUrl = SimpleNamespace(fromLocalFile=lambda path: ('file', path))
    sys.modules['PySide6.QtGui'].QDrag = Drag
    sys.modules['PySide6.QtWidgets'].QTreeWidget = Tree
    sys.modules['PySide6.QtWidgets'].QAbstractItemView = SimpleNamespace(
        SelectionMode=SimpleNamespace(ExtendedSelection=2))

    spec = importlib.util.spec_from_file_location('_multi_drag_testing', ROOT / 'src' / 'file_drag.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, drops, qt


def test_multiple_selected_files_become_multiple_urls(monkeypatch, tmp_path):
    module, drops, _qt = _load_fake_qt_file_drag(monkeypatch)
    paths = [tmp_path / name for name in ('a.txt', 'b.txt', 'c.txt')]
    for p in paths:
        p.write_text('file', encoding='utf-8')
    rows = [_row(path) for path in paths]

    class FakeItem:
        def __init__(self, row, selected):
            self.row, self.selected = row, selected
        def data(self, column, role):
            return self.row
        def isSelected(self):
            return self.selected

    class FakeTree(module.ExternalFileDragTree):
        def __init__(self):
            self._file_drag_row_resolver = None
            self.items = [FakeItem(row, True) for row in rows]
        def currentItem(self):
            return self.items[1]
        def selectedItems(self):
            return [self.items[2], self.items[0], self.items[1]]
        def selectionMode(self):
            return 2
        def indexOfTopLevelItem(self, item):
            return self.items.index(item)

    tree = FakeTree()
    tree.startDrag(1)
    assert len(drops) == 1
    assert drops[0].mime.urls == [('file', str(path.resolve())) for path in paths]
    assert drops[0].mime.data['application/x-qt-windows-mime;value="Preferred DropEffect"'] == b'\x01\x00\x00\x00'
    assert drops[0].actions == (1, 1)


def test_single_file_and_virtual_row(monkeypatch, tmp_path):
    module, drops, _ = _load_fake_qt_file_drag(monkeypatch)
    path = tmp_path / 'only.txt'
    path.write_text('one', encoding='utf-8')
    assert module.begin_file_copy_drag(object(), _row(path))
    assert drops[-1].mime.urls == [('file', str(path.resolve()))]
    assert not module.begin_file_copy_drag(object(), {'item_kind':'directory','_browse_file':str(tmp_path)})
    assert len(drops) == 1


def test_unselected_drag_does_not_pick_other_selected_files(monkeypatch, tmp_path):
    module, drops, _ = _load_fake_qt_file_drag(monkeypatch)
    files = [tmp_path / 'one.txt', tmp_path / 'two.txt']
    for f in files: f.write_text('x')
    class FakeItem:
        def __init__(self, path, selected):
            self.row, self.selected = _row(path), selected
        def data(self, *args): return self.row
        def isSelected(self): return self.selected
    class FakeTree(module.ExternalFileDragTree):
        def __init__(self):
            self._file_drag_row_resolver = None
            self.items = [FakeItem(files[0], True), FakeItem(files[1], False)]
        def currentItem(self): return self.items[1]
        def selectedItems(self): return [self.items[0]]
        def selectionMode(self): return 2
        def indexOfTopLevelItem(self, item): return self.items.index(item)
    FakeTree().startDrag(1)
    assert drops[-1].mime.urls == [('file', str(files[1].resolve()))]
