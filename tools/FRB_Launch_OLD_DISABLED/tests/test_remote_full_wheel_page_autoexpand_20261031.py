"""Remote full-surface wheel and Page-only wheel-expansion regressions.

Qt-free tests run the actual methods extracted from source. On Windows the
same source also exercises real PySide6 paint and mouse event dispatch.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
REMOTE = (ROOT / 'src/launch_remote.py').read_text(encoding='utf-8')
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')


def method(text, class_name, name):
    tree = ast.parse(text)
    klass = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    fn = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == name)
    fn.decorator_list = []
    namespace = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 '<source-method>', 'exec'), namespace)
    return namespace[name]


def test_page_separator_is_between_page_column_and_workspaces():
    assert REMOTE.index('root.addLayout(self.page_column)') < REMOTE.index('root.addWidget(self.page_separator)')
    assert REMOTE.index('root.addWidget(self.page_separator)') < REMOTE.index('root.addLayout(row_workspaces)')
    assert 'QFrame#remotePageSeparator' in REMOTE
    assert "border-top:1px solid {c['panel_border']}" in REMOTE


def test_every_remote_child_and_late_page_button_gets_wheel_filter():
    # A global QApplication filter would intercept the underlying Launcher;
    # registration must remain local to this Remote window and its widgets.
    assert 'self.installEventFilter(self)' in REMOTE
    assert 'for widget in self.findChildren(QWidget):' in REMOTE
    assert 'if widget.window() is self:' in REMOTE
    assert 'widget.installEventFilter(self)' in REMOTE
    assert 'button.installEventFilter(self)' in REMOTE
    assert 'QApplication.instance().installEventFilter' not in REMOTE


def test_remote_filter_uses_shared_pad_for_wheel_on_every_remote_surface():
    class Widget:
        def __init__(self, window=None):
            self._window = window
        def window(self):
            return self._window

    class Base(Widget):
        def eventFilter(self, obj, event):
            return 'fallback'

    source = ast.parse(REMOTE)
    klass = next(n for n in source.body if isinstance(n, ast.ClassDef) and n.name == 'LaunchRemote')
    fn = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == 'eventFilter')
    cls = ast.ClassDef(name='RemoteStub', bases=[ast.Name(id='Base', ctx=ast.Load())],
                       keywords=[], body=[fn], decorator_list=[])
    ns = {'Base': Base, 'QWidget': Widget,
          'QEvent': NS(Type=NS(Wheel=42))}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[cls], type_ignores=[])),
                 '<event-filter>', 'exec'), ns)
    remote = ns['RemoteStub']()
    remote.pad = NS(wheelEvent=Mock())
    wheel = NS(type=lambda: 42)
    for target in (remote, Widget(remote), Widget(remote)):
        assert remote.eventFilter(target, wheel) is True
    assert remote.pad.wheelEvent.call_count == 3
    assert remote.eventFilter(Widget(Widget()), wheel) == 'fallback'
    assert remote.eventFilter(remote, NS(type=lambda: 11)) == 'fallback'
    assert remote.pad.wheelEvent.call_count == 3


def test_wheel_expands_only_page_categories_and_never_executes_leaf():
    fn = method(APP, 'Launcher', '_remote_page_wheel_expand')
    class Action:
        def isEnabled(self):
            return True
    chosen = Action()
    leaf = Action()
    opened = Mock()
    timer = NS(stop=Mock())
    menu = NS(remote_page_navigation=True,
              activeAction=lambda: chosen,
              openers={chosen: opened}, hover_timer=timer, child=None)
    assert fn(menu) is True
    opened.assert_called_once_with('keyboard')
    timer.stop.assert_called_once()
    opened.reset_mock()
    menu.child = NS(isVisible=lambda: True, owner_action=chosen, child=None,
                    hover_timer=NS(stop=Mock()))
    assert fn(menu) is False
    opened.assert_not_called()
    menu.child = None
    menu.activeAction = lambda: leaf
    assert fn(menu) is False
    opened.assert_not_called()
    menu.remote_page_navigation = False
    menu.activeAction = lambda: chosen
    assert fn(menu) is False
    opened.assert_not_called()


def test_page_auto_expands_after_wheel_selection_and_not_on_left_right_or_click():
    function = next(n for n in next(c for c in ast.parse(APP).body
                 if isinstance(c, ast.ClassDef) and c.name == 'Launcher').body
                 if isinstance(n, ast.FunctionDef) and n.name == 'remote_cascade_command')
    source = ast.get_source_segment(APP, function)
    assert 'self._remote_page_wheel_expand(menu)' in source
    assert 'if page_wheel:' in source
    assert 'menu = remote_root' in source
    assert source.index("self._remote_page_wheel_expand(menu)") < source.index("elif command == 'LEFT':")
    assert 'self.run_menu_item(row)' not in source[source.index("if command in ('UP', 'DOWN'):"):source.index("elif command == 'LEFT':")]


def test_actual_dispatch_keeps_wheel_on_first_page_column_without_launching():
    dispatch = method(APP, 'Launcher', 'remote_cascade_command')
    expand = method(APP, 'Launcher', '_remote_page_wheel_expand')

    class Action:
        def isEnabled(self):
            return True

    class Menu:
        def __init__(self, actions, *, parent=None):
            self.rows = actions
            self.index = 0
            self.child = None
            self.openers = {}
            self.parent = parent
            self.remote_page_navigation = True
            self.filter_action = object()
            self.hover_timer = NS(stop=Mock())
            self.open_mode = 'mouse'
            self.outside_since = None
            self.closed = False
        def isVisible(self):
            return not self.closed
        def close(self):
            self.closed = True
        def deleteLater(self):
            pass
        def activeAction(self):
            return self.rows[self.index]
        def _move_filtered_selection(self, direction):
            self.index = (self.index + direction) % len(self.rows)

    class AppMenu(Menu):
        pass

    root_actions = [Action(), Action()]
    child_actions = [Action(), Action()]
    root = Menu(root_actions)
    opened = []
    executed = Mock()
    def open_child(mode):
        child = Menu(child_actions, parent=root)
        child.owner_action = root_actions[1]
        root.child = child
        opened.append((mode, child))
    root.openers[root_actions[1]] = open_child
    launch = NS(menu=root, _remote_page_menu=root, remote_window=None,
                _remote_page_wheel_expand=lambda menu: expand(menu),
                run_menu_item=executed)
    dispatch.__globals__['CascadeMenu'] = Menu
    dispatch.__globals__['AppCascadeMenu'] = AppMenu

    # First tick selects second row in page root and opens second column.
    assert dispatch(launch, 'DOWN') is True
    assert root.activeAction() is root_actions[1]
    assert len(opened) == 1
    assert opened[0][0] == 'keyboard'
    assert root.child is opened[0][1]
    # Next tick remains in the Page root, returns to row 1 (leaf), and
    # closes its old preview. It NEVER scrolls the right-hand column.
    assert dispatch(launch, 'DOWN') is True
    assert root.activeAction() is root_actions[0]
    assert root.child is None
    assert len(opened) == 1
    executed.assert_not_called()


def test_python_parses():
    ast.parse(REMOTE)
    ast.parse(APP)

def test_remote_page_wheel_overrides_web_body_scrolling_when_page_open():
    src = ast.get_source_segment(APP, next(n for n in next(c for c in ast.parse(APP).body
        if isinstance(c, ast.ClassDef) and c.name == 'Launcher').body
        if isinstance(n, ast.FunctionDef) and n.name == 'remote_command'))
    assert "remote_page = getattr(self, '_remote_page_menu', None)" in src
    assert "if (remote_page_visible or not (web_active and str(area).startswith('web_body'))):" in src
