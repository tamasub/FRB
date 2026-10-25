"""Blank-header focus routing and separator geometry (Oct 25 polish)."""
import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
PAGE = (ROOT / 'src/page_tab_focus.py').read_text(encoding='utf-8')
VIEW = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
APPEARANCE = (ROOT / 'src/launch_appearance.py').read_text(encoding='utf-8')


def _method(class_name, name, source, scope):
    module = ast.parse(source)
    clazz = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    method = next(n for n in clazz.body if isinstance(n, ast.FunctionDef) and n.name == name)
    code = compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), '<isolated>', 'exec')
    exec(code, scope)
    return scope[name]


def test_context_separator_runs_past_icon_without_touching_outer_edge():
    assert 'QMenu::separator { height:1px; background:#e1e5e2; margin:5px 3px; }' in APPEARANCE
    assert 'QMenu::icon { margin-left:4px; margin-right:1px; }' in APPEARANCE


def test_page_header_whitespace_routes_to_first_tab_only():
    fake_qt = SimpleNamespace(
        MouseButton=SimpleNamespace(LeftButton='left', RightButton='right'),
        FocusReason=SimpleNamespace(MouseFocusReason='mouse'),
    )
    fake_qevent = SimpleNamespace(Type=SimpleNamespace(MouseButtonPress='press'))
    call = _method('Launcher', 'focus_first_page_from_header_space', APP,
                   {'Qt': fake_qt, 'QEvent': fake_qevent})
    touched = []
    header = object()
    other = object()
    tabs = SimpleNamespace(
        count=lambda: 3,
        setCurrentIndex=lambda i: touched.append(('page', i)),
        setFocus=lambda reason: touched.append(('focus', reason)))
    self = SimpleNamespace(mode_bar=header, tabs=tabs,
                           close_cascade_for_main_interaction=lambda: touched.append(('close',)))
    class Event:
        def __init__(self, button='left', kind='press'):
            self._button, self._kind, self.accepted = button, kind, False
        def button(self): return self._button
        def type(self): return self._kind
        def accept(self): self.accepted = True
    event = Event()
    assert call(self, header, event) is True
    assert event.accepted is True
    assert touched == [('close',), ('page', 0), ('focus', 'mouse')]
    touched.clear()
    for obj, evt in ((other, Event()), (header, Event('right')),
                     (header, Event(kind='move'))):
        assert call(self, obj, evt) is False
    assert touched == []


def test_tab_blank_click_is_only_for_unused_area():
    assert 'self.tabAt(event.position().toPoint()) == -1' in PAGE
    assert 'self.setCurrentIndex(0)' in PAGE
    assert 'self.setFocus(Qt.FocusReason.MouseFocusReason)' in PAGE
    assert 'super().mousePressEvent(event)' in PAGE
    assert 'self.mode_bar.installEventFilter(self)' in APP


def test_second_row_whitespace_focus_does_not_execute_or_open():
    handler = VIEW.split('    def eventFilter(self, obj, event):')[-1].split('    def wheel_files_first_column(', 1)[0]
    assert 'obj in (self.root_widget, self.toolbar_scroller.viewport(),' in handler
    assert 'event.button() == Qt.MouseButton.LeftButton' in handler
    assert 'self.focus_root(index=0)' in handler
    assert 'button.setChecked(index == 0)' in handler
    assert 'self.launcher.close_cascade_for_main_interaction()' in handler
    assert 'self.open_cascade(' not in handler
    assert 'self.launcher.execute(' not in handler
    assert 'obj in self.root_buttons' in handler  # wheel and real button events kept separate
