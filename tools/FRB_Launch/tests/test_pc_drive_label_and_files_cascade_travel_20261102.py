"""Drive-name visibility and diagonal Files-list travel regressions.

Structural tests run without PySide6; the FakeMenu test exercises the exact
RemoteFolderActionsMenu mouse/hover methods with a fake Qt event loop.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
VIEW = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')


def extract_method(code, owner, name):
    for node in ast.parse(code).body:
        if isinstance(node, ast.ClassDef) and node.name == owner:
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == name:
                    return child
    raise AssertionError((owner, name))


def fake_remote_menu_class():
    methods = [extract_method(APP, 'RemoteFolderActionsMenu', name)
               for name in ('_close_files_preview_on_stable_other_action',
                            'mouseMoveEvent', 'hideEvent')]
    class DummyParent:
        def mouseMoveEvent(self, _event):
            pass
        def hideEvent(self, _event):
            pass
    class Timer:
        def __init__(self, owner):
            self.running = False
            self.callback = None
            self.timeout = SimpleNamespace(connect=lambda cb: setattr(self, 'callback', cb))
        def setSingleShot(self, value):
            assert value
        def isActive(self):
            return self.running
        def start(self, ms):
            assert ms >= 250
            self.running = True
        def stop(self):
            self.running = False
        def fire(self):
            self.running = False
            self.callback()
    class Cursor:
        point = 'files'
        @staticmethod
        def pos():
            return Cursor.point
    module = ast.Module(body=[ast.ClassDef(name='Menu', bases=[ast.Name(id='CascadeMenu', ctx=ast.Load())],
                                             keywords=[], body=methods, decorator_list=[])],
                        type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {'CascadeMenu': DummyParent, 'QTimer': Timer, 'QCursor': Cursor}
    exec(compile(module, '<test>', 'exec'), namespace)
    return namespace['Menu'], Cursor


def test_remote_files_menu_keeps_child_while_crossing_gap_and_other_row():
    Menu, Cursor = fake_remote_menu_class()
    class Action:
        def isEnabled(self):
            return True
        def isSeparator(self):
            return False
    class Child:
        def __init__(self):
            self.closed = False
            self.deleted = False
        def close(self):
            self.closed = True
        def deleteLater(self):
            self.deleted = True
    files = Action(); paste = Action(); child = Child()
    menu = Menu()
    menu.folder_list_action = files
    menu.launcher = SimpleNamespace(_remote_folder_root_menu=child)
    menu.child = child
    menu.actionAt = lambda where: {'files': files, 'other': paste}.get(where)
    menu.isVisible = lambda: True
    menu.rect = lambda: SimpleNamespace(contains=lambda where: where in ('files', 'other', 'blank'))
    menu.mapFromGlobal = lambda pos: pos
    event = lambda point: SimpleNamespace(position=lambda: SimpleNamespace(toPoint=lambda: point))
    # Files-list -> blank edge -> child: neither blank gap nor fleeting hover
    # over another action may destroy already-open columns.
    menu.mouseMoveEvent(event('files'))
    menu.mouseMoveEvent(event('blank'))
    menu.mouseMoveEvent(event('other'))
    assert not child.closed
    Cursor.point = 'child'  # Cursor has left root and entered the right popup.
    menu._non_files_hover_timer.fire()
    assert menu.child is child and not child.closed
    # A deliberate, sustained hover over another action *does* dismiss.
    menu.mouseMoveEvent(event('other'))
    Cursor.point = 'other'
    menu._non_files_hover_timer.fire()
    assert menu.child is None and child.closed and child.deleted
    assert menu.launcher._remote_folder_root_menu is None


def test_hover_timer_cancelled_on_files_row_and_on_hide():
    Menu, Cursor = fake_remote_menu_class()
    action = SimpleNamespace(isEnabled=lambda: True, isSeparator=lambda: False)
    menu = Menu()
    menu.folder_list_action = object()
    menu.child = object()
    menu.actionAt = lambda point: action if point == 'other' else menu.folder_list_action
    event = lambda point: SimpleNamespace(position=lambda: SimpleNamespace(toPoint=lambda: point))
    menu.mouseMoveEvent(event('other'))
    assert menu._non_files_hover_timer.isActive()
    menu.mouseMoveEvent(event('files'))
    assert not menu._non_files_hover_timer.isActive()
    menu.mouseMoveEvent(event('other'))
    menu.hideEvent(object())
    assert not menu._non_files_hover_timer.isActive()


def test_drive_label_is_drawn_after_delegate_with_physical_row_title():
    draw = ast.get_source_segment(VIEW, extract_method(VIEW, '_SeparatedFileTree', 'drawRow'))
    paint = ast.get_source_segment(VIEW, extract_method(VIEW, '_InlineRenameDelegate', 'paint'))
    assert draw.index('super().drawRow(painter, option, index)') < draw.index('painter.drawText(')
    assert "row.get('_system_drive')" in draw
    assert "row.get('title')" in draw
    assert 'self.columnWidth(0)' in draw
    assert 'ElideRight' in draw
    assert 'native.text = \'\'' in paint
    assert 'CE_ItemViewItem' in paint
