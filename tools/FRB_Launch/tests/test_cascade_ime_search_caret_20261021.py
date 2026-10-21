"""Regressions for main search caret and IME input during open cascade.

Pure AST tests intentionally run without PySide6 on build hosts; native Qt
verification (especially Windows Japanese IME) must also be done on the PC.
"""
import ast
from pathlib import Path
import types
from unittest.mock import Mock

SRC = Path(__file__).resolve().parents[1] / 'src' / 'app.py'
CODE = SRC.read_text(encoding='utf-8')
TREE = ast.parse(CODE)


def method(cls_name, name):
    cls = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == cls_name)
    return next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)


def compile_function(body, ns):
    original = method('Launcher', 'eventFilter')
    fn = ast.FunctionDef(name='dispatch', args=original.args, body=body + [ast.Return(value=ast.Constant(False))], decorator_list=[])
    mod = ast.Module(body=[fn], type_ignores=[])
    ast.fix_missing_locations(mod)
    exec(compile(mod, str(SRC), 'exec'), ns)
    return ns['dispatch']


class Event:
    def __init__(self, kind, key=None, preedit=None):
        self.kind, self.k = kind, key
        self.preedit = preedit
        self.accept = Mock()
    def type(self): return self.kind
    def key(self): return self.k
    def preeditString(self): return self.preedit


def test_main_search_is_not_relayed_to_open_cascade():
    # Run REAL first five branches of Launcher.eventFilter with tiny Qt stubs.
    qt = types.SimpleNamespace(MouseButton=types.SimpleNamespace(LeftButton=1, RightButton=2))
    events = types.SimpleNamespace(MouseButtonPress=1, MouseButtonRelease=2, ContextMenu=3,
                                   FocusIn=4, KeyPress=5, InputMethod=6)
    ns = {'Qt': qt, 'QEvent': types.SimpleNamespace(Type=events),
          'QApplication': types.SimpleNamespace(activePopupWidget=lambda: None),
          'QTimer': types.SimpleNamespace(singleShot=lambda *args: None)}
    dispatch = compile_function(method('Launcher', 'eventFilter').body[:5], ns)
    class List:
        def viewport(self): return viewport
    viewport = object()
    col = types.SimpleNamespace(keyPressEvent=Mock(), inputMethodEvent=Mock())
    dummy = types.SimpleNamespace(list=List(), tabs=object(), search=object(),
                                  visible_cascade_for_keyboard=lambda: col)
    # Search editor remains native Qt owner for arrows and IME preedit.
    for event in (Event(5, 16777234), Event(5, ord('a')), Event(6, preedit='かな')):
        assert dispatch(dummy, dummy.search, event) is False
    col.keyPressEvent.assert_not_called()
    col.inputMethodEvent.assert_not_called()
    # List focus with open cascade retains submenu arrow/menu navigation.
    assert dispatch(dummy, dummy.list, Event(5, 16777236)) is True
    col.keyPressEvent.assert_called_once()
    # An IME preedit on a non-grabbing cascade's underlying main list is forwarded.
    assert dispatch(dummy, dummy.list, Event(6, preedit='かな')) is True
    col.inputMethodEvent.assert_called_once()


def test_global_editor_left_right_are_native_even_with_empty_query():
    src = ast.get_source_segment(CODE, method('Launcher', 'eventFilter'))
    assert "if obj is self.search and k in (" in src
    assert 'Qt.Key.Key_Left, Qt.Key.Key_Right' in src
    assert 'Qt.Key.Key_Home, Qt.Key.Key_End' in src
    assert src.index('if obj is self.search and k in (') < src.index('if self.page_key(event):return True')


def test_cascade_filter_editor_preserves_caret_and_ime_candidate_keys():
    node = method('CascadeMenu', 'eventFilter')
    # Execute exact filter-key and filter-IME conditionals, not a copy.
    segments = [n for n in node.body if isinstance(n, ast.If)
                and ast.get_source_segment(CODE, n).startswith('if obj is self.filter_edit')]
    assert len(segments) == 2
    fn = ast.FunctionDef(name='check', args=node.args, body=segments + [ast.Return(value=ast.Constant(False))], decorator_list=[])
    mod=ast.Module(body=[fn], type_ignores=[]); ast.fix_missing_locations(mod)
    class Keys:
        Key_Escape=1; Key_Down=2; Key_Up=3; Key_Return=4; Key_Enter=5
        Key_Left=6; Key_Right=7; Key_F=8
    qt = types.SimpleNamespace(Key=Keys, KeyboardModifier=types.SimpleNamespace(ControlModifier=8))
    events = types.SimpleNamespace(KeyPress=1, InputMethod=2)
    ns = {'Qt':qt, 'QEvent':types.SimpleNamespace(Type=events)}
    exec(compile(mod,str(SRC),'exec'),ns)
    edit = object()
    menu = types.SimpleNamespace(filter_edit=edit, _filter_ime_composing=False,
                                 _move_filtered_selection=Mock(),clear_local_filter=Mock(),keyPressEvent=Mock())
    for k in (Keys.Key_Left, Keys.Key_Right):
        ev = Event(1,k)
        ev.modifiers=lambda:0
        assert ns['check'](menu,edit,ev) is False
        menu.keyPressEvent.assert_not_called()
    down = Event(1,Keys.Key_Down);down.modifiers=lambda:0
    assert ns['check'](menu,edit,down) is True
    menu._move_filtered_selection.assert_called_once_with(1)
    ime=Event(2,preedit='日本')
    assert ns['check'](menu,edit,ime) is False
    assert menu._filter_ime_composing is True
    menu._move_filtered_selection.reset_mock()
    assert ns['check'](menu,edit,down) is False
    menu._move_filtered_selection.assert_not_called()
    assert ns['check'](menu,edit,Event(2,preedit='')) is False
    assert menu._filter_ime_composing is False


def test_first_japanese_preedit_creates_inline_editor():
    fn = method('CascadeMenu','inputMethodEvent')
    mod=ast.Module(body=[fn],type_ignores=[]); ast.fix_missing_locations(mod)
    sent=[]
    ns={'AppCascadeMenu':type('AppCascadeMenu',(),{}),
        'QApplication':types.SimpleNamespace(sendEvent=lambda target,event:sent.append((target,event)))}
    exec(compile(mod,str(SRC),'exec'),ns)
    text_edit = object()
    obj=types.SimpleNamespace(filter_edit=None)
    def ensure(): obj.filter_edit=text_edit
    obj._ensure_local_filter=ensure
    ime=Event(6,preedit='日本')
    ns['inputMethodEvent'](obj,ime)
    assert sent == [(text_edit,ime)]
    ime.accept.assert_called_once()

# Opt-in native test. CI hosts without the Qt bindings still run the pure
# regressions above; Windows/Japanese IME should be checked manually too.
try:
    import os
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from PySide6.QtCore import Qt as NativeQt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication as NativeQApplication
    import app as native_app
except ImportError:
    NativeQApplication = None


def test_native_main_search_caret_remains_editable_with_cascade():
    import pytest
    if NativeQApplication is None:
        pytest.skip('Native PySide6 display required')
    qtapp = NativeQApplication.instance() or NativeQApplication([])
    qtapp.setQuitOnLastWindowClosed(False)
    launcher = native_app.Launcher()
    launcher.show()
    try:
        # Any authored folder/category can open a cascade.  Do not depend on
        # an exact sample item ID that an admin might remove from the JSON.
        folder = next(item for item in launcher.data['items']
                      if item.get('item_kind') == 'category' and item.get('page_id') == launcher.page_id)
        launcher.cascade(folder)
        launcher.search.setText('sample')
        launcher.search.setFocus()
        launcher.search.setCursorPosition(3)
        qtapp.processEvents()
        QTest.keyClick(launcher.search, NativeQt.Key.Key_Left)
        qtapp.processEvents()
        assert launcher.search.cursorPosition() == 2
        QTest.keyClick(launcher.search, NativeQt.Key.Key_Right)
        qtapp.processEvents()
        assert launcher.search.cursorPosition() == 3
    finally:
        launcher.close_cascade_for_main_interaction()
        launcher.tray.hide()
        launcher.close()
