"""Qt-free regression checks for Page, root, F2 and F5 shortcut behavior.

Windows/PySide6 end-to-end keyboard delivery still requires a native smoke test.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
VIEW = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')


def _method(source, classname, methodname, symbols=None):
    module = ast.parse(source)
    cls = next(x for x in module.body if isinstance(x, ast.ClassDef) and x.name == classname)
    method = next(x for x in cls.body if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))
                  and x.name == methodname)
    code = compile(ast.Module(body=[method], type_ignores=[]), '<extracted>', 'exec')
    scope = dict(symbols or {})
    exec(code, scope)
    return scope[methodname]


def test_shortcut_bindings_no_longer_conflict_with_plain_f2_f5():
    assert "QKeySequence(f'Ctrl+F{index+1}')" in APP
    assert "QKeySequence(f'Ctrl+Shift+F{index+1}')" in APP
    assert "QKeySequence(f'F{index+1}')" not in APP
    assert "QKeySequence('F2')" in APP
    assert "QKeySequence('F5')" in APP
    assert "self.file_rename_shortcut.activated.connect(self.rename_current_middle_item)" in APP
    assert "self.folder_refresh_shortcut.activated.connect(self.refresh_current_middle_folder)" in APP
    assert "f'Ctrl+Shift+F{index+1}'" in VIEW
    assert 'Ctrl+F1〜F12 / Ctrl+PageUp/Down Page切替' in APP
    # Ctrl+F12 changes Page 12 even on a selection page; plain F12 still confirms.
    switch_page = APP[APP.index('    def switch_page('):APP.index('    def page_changed(', APP.index('    def switch_page('))]
    assert 'if index==11 and self.selection:' not in switch_page
    assert 'if k==Qt.Key.Key_F12:self.confirm_selection();return True' in APP


def test_page_key_requires_exact_ctrl_modifier():
    qt = SimpleNamespace(KeyboardModifier=SimpleNamespace(ControlModifier=1),
                         Key=SimpleNamespace(Key_F1=100))
    page_key = _method(APP, 'Launcher', 'page_key', {'Qt': qt})
    page_switches = []
    launcher = SimpleNamespace(switch_page=page_switches.append)
    def event(key, modifiers):
        return SimpleNamespace(key=lambda: key, modifiers=lambda: modifiers)
    assert not page_key(launcher, event(101, 0))
    assert not page_key(launcher, event(101, 3))
    assert page_key(launcher, event(101, 1))
    assert page_switches == [1]
    assert not page_key(launcher, event(119, 1))


class FakeItem:
    def __init__(self, title, selected=False):
        self.title = title
        self.selected = selected
    def setSelected(self, selected):
        self.selected = selected


class FakeTree:
    def __init__(self, items):
        self.items = items
        self.current = items[0] if items else None
        self.scroll = SimpleNamespace(value=lambda: self.scroll_position,
                                     setValue=lambda value: setattr(self, 'scroll_position', value))
        self.scroll_position = 9
        self.editing = False
    def currentItem(self): return self.current
    def selectedItems(self): return [item for item in self.items if item.selected]
    def state(self): return int(self.editing)
    def isAncestorOf(self, focus): return focus is self
    def verticalScrollBar(self): return self.scroll
    def clearSelection(self):
        for item in self.items: item.selected = False
    def topLevelItemCount(self): return len(self.items)
    def topLevelItem(self, index): return self.items[index]
    def setCurrentItem(self, item):
        # Matches Qt extended selection: changing current may reset selection.
        self.current = item
        self.clearSelection()
        item.setSelected(True)


def test_f2_scoped_to_middle_focus_and_never_edits_multiselect():
    tree = FakeTree([FakeItem('a.txt', True), FakeItem('b.txt')])
    focus = [tree]
    qt = SimpleNamespace(State=SimpleNamespace(EditingState=1))
    rename = _method(VIEW, 'ExpandedLauncherView', 'rename_selected_middle_item',
                     {'QApplication': SimpleNamespace(focusWidget=lambda: focus[0]),
                      'QAbstractItemView': qt})
    renames = []
    view = SimpleNamespace(middle=SimpleNamespace(tree=tree), isVisible=lambda: True,
                           begin_inline_rename=lambda item: (renames.append(item.title) or True))
    assert rename(view) is True
    assert renames == ['a.txt']
    focus[0] = object()
    assert rename(view) is False
    focus[0] = tree
    tree.items[1].selected = True
    assert rename(view) is False
    tree.items[1].selected = False
    tree.editing = True
    assert rename(view) is False
    assert renames == ['a.txt']


def test_f5_reloads_and_keeps_selection_current_row_scroll(tmp_path):
    tree = FakeTree([FakeItem('first.txt', True), FakeItem('second.txt', True)])
    tree.current = tree.items[1]
    def refresh():
        # File changes between refreshes; widgets are recreated.
        tree.items = [FakeItem('second.txt'), FakeItem('new.txt'), FakeItem('first.txt')]
        tree.current = None
        tree.scroll_position = 0
    qt = SimpleNamespace(State=SimpleNamespace(EditingState=1))
    reload_directory = _method(VIEW, 'ExpandedLauncherView', 'refresh_current_directory',
                               {'QAbstractItemView': qt, 'Path': Path})
    view = SimpleNamespace(middle=SimpleNamespace(tree=tree), isVisible=lambda: True,
                           current_directory=lambda: str(tmp_path),
                           refresh_middle=refresh,
                           row_data=lambda item: {'title': item.title} if item else None)
    assert reload_directory(view) is True
    assert tree.current.title == 'second.txt'
    assert {i.title for i in tree.selectedItems()} == {'first.txt', 'second.txt'}
    assert tree.scroll_position == 9
    tree.editing = True
    assert reload_directory(view) is False


def test_python_source_syntax():
    ast.parse(APP)
    ast.parse(VIEW)
