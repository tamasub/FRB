"""Files Exp tree state persistence tests without PySide6 / Windows desktop.

Execute the *production methods* from AST with minimal Qt-model doubles. The
live Windows QTreeView paint/scroll specifics still require manual validation.
"""
import ast
import json
import os
from pathlib import Path
from types import MethodType, SimpleNamespace as NS

SOURCE = Path(__file__).resolve().parents[1] / 'src' / 'remote_files_explorer.py'
REMOTE = Path(__file__).resolve().parents[1] / 'src' / 'launch_remote.py'
SOURCE_TEXT = SOURCE.read_text('utf-8')
MOD = ast.parse(SOURCE_TEXT)
CLS = next(node for node in MOD.body if isinstance(node, ast.ClassDef)
           and node.name == 'RemoteFilesExplorer')
DATA_ROLE = 555


def production(name):
    node = next(child for child in CLS.body if isinstance(child, ast.FunctionDef)
                and child.name == name)
    space = dict(json=json, os=os, _DATA_ROLE=DATA_ROLE)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 str(SOURCE), 'exec'), space)
    return space[name]


class Index:
    def __init__(self, item=None):
        self.item = item
    def isValid(self):
        return self.item is not None


class Item:
    def __init__(self, label='', path=None, pc=False):
        self._label, self._path, self._pc = label, path, pc
        self._children = []
        self._parent = None
    def text(self):
        return self._label
    def data(self, role):
        return {'path': self._path, 'pc': self._pc} if role == DATA_ROLE and (self._path or self._pc) else None
    def parent(self):
        return self._parent
    def index(self):
        return Index(self)
    def appendRow(self, child):
        child._parent = self
        self._children.append(child)
    def child(self, idx):
        return self._children[idx]
    def rowCount(self):
        return len(self._children)


class Model:
    def __init__(self):
        self.root = Item()
    def invisibleRootItem(self):
        return self.root
    def itemFromIndex(self, index):
        return index.item


class Bar:
    def __init__(self, value=0, maximum=99):
        self._value, self._maximum = value, maximum
    def value(self):
        return self._value
    def minimum(self):
        return 0
    def maximum(self):
        return self._maximum
    def setValue(self, v):
        self._value = v


class Tree:
    def __init__(self):
        self.opened = set()
        self.current = Index()
        self.y, self.x = Bar(14), Bar(2)
        self.animated = True
    def isExpanded(self, index):
        return index.item in self.opened
    def setExpanded(self, index, opened):
        if opened:
            self.opened.add(index.item)
        else:
            self.opened.discard(index.item)
    def setCurrentIndex(self, index):
        self.current = index
    def currentIndex(self):
        return self.current
    def verticalScrollBar(self):
        return self.y
    def horizontalScrollBar(self):
        return self.x
    def isAnimated(self):
        return self.animated
    def setAnimated(self, value):
        self.animated = value
    def clear_wheel_pending(self):
        pass


class Settings:
    def __init__(self):
        self.values = {}
    def value(self, name, default=''):
        return self.values.get(name, default)
    def setValue(self, name, val):
        self.values[name] = val
    def sync(self):
        pass


class Timer:
    def __init__(self):
        self.events = []
    def stop(self):
        self.events.append('stop')
    def start(self):
        self.events.append('start')


def make_panel(folder, settings):
    panel = NS(model=Model(), tree=Tree(), _settings=settings,
               _restoring_tree=False, _syncing_directory=False,
               _tree_state_timer=Timer(), _selection_timer=Timer(),
               _pending_restored_scroll=None)
    for name in ('_capture_tree_state', '_save_tree_state',
                 'restore_previous_tree_state', 'finish_restoring_tree_scroll',
                 '_schedule_tree_state_save'):
        setattr(panel, name, MethodType(production(name), panel))
    panel._tree_node_key = production('_tree_node_key')  # static function
    root = Item('Documents', str(folder))
    panel.model.root.appendRow(root)
    def load(index):
        item = index.item
        if item.rowCount():
            return
        if item._path and os.path.isdir(item._path):
            for child in sorted(Path(item._path).iterdir()):
                if child.is_dir():
                    item.appendRow(Item(child.name, str(child)))
    panel._expand_index = load
    return panel, root


def test_expanded_subfolders_current_and_scroll_round_trip(tmp_path):
    folder = tmp_path / 'Documents'
    deep = folder / 'A' / 'C'
    deep.mkdir(parents=True)
    (folder / 'B').mkdir()
    settings = Settings()
    first, root = make_panel(folder, settings)
    first._expand_index(root.index())
    first.tree.setExpanded(root.index(), True)
    a = root.child(0)
    first._expand_index(a.index())
    first.tree.setExpanded(a.index(), True)
    first.tree.setCurrentIndex(a.child(0).index())
    first._save_tree_state()
    state = json.loads(settings.value('remote_files_exp/tree_state_v1'))
    assert [entry[-1] for entry in state['expanded']] == [os.path.normpath(str(folder)), os.path.normpath(str(folder / 'A'))]
    assert state['selected'][-1] == os.path.normpath(str(deep))
    assert state['scroll_y'] == 14 and state['scroll_x'] == 2
    # Launch is restarted and a directory is created: path-based reconstruction
    # still selects C, rather than a stale row number.
    (folder / '0-first').mkdir()
    second, new_root = make_panel(folder, settings)
    second.tree.y.setValue(0)
    second.tree.x.setValue(0)
    assert second.restore_previous_tree_state()
    assert new_root in second.tree.opened
    new_a = next(it for it in new_root._children if it.text() == 'A')
    assert new_a in second.tree.opened
    assert second.tree.currentIndex().item._path == str(deep)
    assert second.tree.isAnimated()  # restore must not change UI preference
    second.finish_restoring_tree_scroll()
    assert second.tree.y.value() == 14 and second.tree.x.value() == 2
    assert second._pending_restored_scroll is None


def test_pc_root_and_renamed_folder_not_mis_selected(tmp_path):
    folder = tmp_path / 'root'
    (folder / 'removed').mkdir(parents=True)
    settings = Settings()
    original, root = make_panel(folder, settings)
    original._expand_index(root.index())
    original.tree.setExpanded(root.index(), True)
    original.tree.setCurrentIndex(root.child(0).index())
    original._save_tree_state()
    (folder / 'removed').rename(folder / 'renamed')
    restored, _ = make_panel(folder, settings)
    assert restored.restore_previous_tree_state() is False
    assert restored.tree.currentIndex().item is None
    # PC is a virtual root. No fake file path or navigation is necessary.
    pc = Item('PC', pc=True)
    assert restored._tree_node_key(pc) == ['PC', '<PC>', '<PC>']


def test_empty_state_is_valid_home_reset_and_invalid_state_is_ignored(tmp_path):
    settings = Settings()
    settings.setValue('remote_files_exp/tree_state_v1', json.dumps({
        'version': 1, 'expanded': [], 'selected': None,
        'scroll_y': 0, 'scroll_x': 0,
    }))
    panel, root = make_panel(tmp_path, settings)
    assert panel.restore_previous_tree_state()
    assert not panel.tree.opened and not panel.tree.currentIndex().isValid()
    settings.setValue('remote_files_exp/tree_state_v1', '{broken')
    assert panel.restore_previous_tree_state() is False


def test_open_path_restores_before_show_and_does_not_resync_breadcrumb():
    text = REMOTE.read_text('utf-8')
    code = text.split('    def toggle_files_exp(self):', 1)[1].split('    def position_files_exp(self):', 1)[0]
    assert code.index('panel.set_roots(') < code.index("getattr(panel, 'restore_previous_tree_state'")
    assert code.index("getattr(panel, 'restore_previous_tree_state'") < code.index('panel.show()')
    assert 'if launcher is not None and not restored:' in code
    assert 'QTimer.singleShot(0, restore_scroll)' in code
    assert "self._settings.setValue('remote_files_exp/tree_state_v1'" in SOURCE_TEXT
    assert 'self._save_tree_state()' in SOURCE_TEXT.split('    def hideEvent(self, event):', 1)[1]


def test_virtual_pc_drives_restore_without_faking_pc_directory(tmp_path):
    drive = tmp_path / 'C_Drive'
    (drive / 'workspace').mkdir(parents=True)
    settings = Settings()
    def pc_panel():
        panel, _ = make_panel(tmp_path, settings)
        panel.model.root._children.clear()
        pc = Item('PC', pc=True)
        panel.model.root.appendRow(pc)
        old_load = panel._expand_index
        def load(index):
            if index.item is pc:
                if pc.rowCount() == 0:
                    pc.appendRow(Item('Windows (C:)', str(drive)))
                return
            old_load(index)
        panel._expand_index = load
        return panel, pc
    panel, pc = pc_panel()
    panel._expand_index(pc.index())
    panel.tree.setExpanded(pc.index(), True)
    disk = pc.child(0)
    panel._expand_index(disk.index())
    panel.tree.setExpanded(disk.index(), True)
    panel.tree.setCurrentIndex(disk.child(0).index())
    panel._save_tree_state()
    reopened, second_pc = pc_panel()
    assert reopened.restore_previous_tree_state()
    assert second_pc in reopened.tree.opened
    second_disk = second_pc.child(0)
    assert second_disk in reopened.tree.opened
    assert reopened.tree.currentIndex().item._path == str(drive / 'workspace')
