"""F3 -> global-search contract without requiring Qt on the test host.

Actual PySide6 focus delivery from native Windows popups requires a Windows smoke test.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

APP = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf-8')


def method(classname, name, symbols=None):
    root = ast.parse(APP)
    cls = next(node for node in root.body if isinstance(node, ast.ClassDef) and node.name == classname)
    node = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == name)
    scope = dict(symbols or {})
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<method>', 'exec'), scope)
    return scope[name]


def test_f3_window_shortcut_is_bound_without_changing_page_shortcuts():
    assert "self.search_focus_shortcut = QShortcut(QKeySequence('F3'), self)" in APP
    assert 'self.search_focus_shortcut.activated.connect(self.focus_search)' in APP
    assert "QKeySequence(f'Ctrl+F{index+1}')" in APP
    assert "QKeySequence('F2')" in APP
    assert "QKeySequence('F5')" in APP


def test_f3_reuses_existing_focus_search_and_preserves_query():
    operations = []

    class Search:
        text = '(.bat launch)'
        def setFocus(self):
            operations.append('focus')
        def selectAll(self):
            operations.append('select-all')

    class Timer:
        def stop(self):
            operations.append('stop-hover')

    class Menu:
        def close(self):
            operations.append('close-menu')

    fake = SimpleNamespace(
        search=Search(), hover_timer=Timer(), menu=Menu(), pending_menu_item='folder',
        hide_history_popup=lambda: operations.append('hide-history'),
        activateWindow=lambda: operations.append('activate'),
    )
    focus = method('Launcher', 'focus_search')
    focus(fake)
    assert fake.search.text == '(.bat launch)'
    assert fake.pending_menu_item is None
    assert operations == ['hide-history', 'stop-hover', 'close-menu', 'activate', 'focus', 'select-all']
    operations.clear()
    focus(fake, False)
    assert 'select-all' not in operations


def test_launcher_event_filter_routes_only_plain_f3_to_global_search():
    event_type = SimpleNamespace(KeyPress=1, MouseButtonPress=2)
    qt = SimpleNamespace(Key=SimpleNamespace(Key_F3=114),
                         KeyboardModifier=SimpleNamespace(NoModifier=0))
    qevent = SimpleNamespace(Type=event_type)
    receive = method('Launcher', 'handle_history_event', {'Qt': qt, 'QEvent': qevent})
    invoked = []
    fake = SimpleNamespace(
        history_choices=SimpleNamespace(viewport=lambda: object()),
        history_filter=object(),
        search=object(), list=object(), tabs=object(),
        history_popup=SimpleNamespace(isVisible=lambda: False),
        focus_search=lambda: invoked.append('focus-search'),
    )
    class Event:
        accepted = False
        def __init__(self, mod=0): self.mod = mod
        def type(self): return 1
        def key(self): return 114
        def modifiers(self): return self.mod
        def accept(self): self.accepted = True
    evt = Event()
    assert receive(fake, fake.history_filter, evt) is True
    assert evt.accepted
    assert invoked == ['focus-search']
    # Ctrl+F3 is reserved for the existing Page 3 shortcut, never this branch.
    assert receive(fake, fake.history_filter, Event(mod=1)) is False
    assert invoked == ['focus-search']


def test_cascade_popup_keeps_plain_f3_available():
    qt = SimpleNamespace(Key=SimpleNamespace(Key_F3=114),
                         KeyboardModifier=SimpleNamespace(NoModifier=0))
    receive = method('CascadeMenu', 'keyPressEvent', {'Qt': qt})
    invoked = []
    fake = SimpleNamespace(
        scroll_tree=None, hover_timer=SimpleNamespace(stop=lambda: None),
        launcher=SimpleNamespace(focus_search=lambda: invoked.append('focus-search')),
    )
    class Event:
        accepted = False
        def key(self): return 114
        def modifiers(self): return 0
        def accept(self): self.accepted = True
    evt = Event()
    receive(fake, evt)
    assert invoked == ['focus-search']
    assert evt.accepted



def test_cascade_inline_filter_routes_f3_even_while_popup_owns_focus():
    qt = SimpleNamespace(Key=SimpleNamespace(Key_F3=114),
                         KeyboardModifier=SimpleNamespace(NoModifier=0))
    qevent = SimpleNamespace(Type=SimpleNamespace(KeyPress=1))
    receive = method('CascadeMenu', 'eventFilter', {'Qt': qt, 'QEvent': qevent})
    invoked = []
    editor = object()
    fake = SimpleNamespace(
        filter_edit=editor, scroll_tree=None,
        _handle_right_click_properties=lambda event, obj: False,
        _consume_unused_right_click=lambda event: False,
        launcher=SimpleNamespace(focus_search=lambda: invoked.append('focus-search')),
    )
    class Event:
        accepted = False
        def type(self): return 1
        def key(self): return 114
        def modifiers(self): return 0
        def accept(self): self.accepted = True
    evt = Event()
    assert receive(fake, editor, evt) is True
    assert evt.accepted
    assert invoked == ['focus-search']


def test_source_syntax():
    ast.parse(APP)
