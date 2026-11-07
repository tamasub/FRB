"""v0.3 deterministic regression checks for Qt menus and Windows rod clicks.

Runs without PySide6 or Windows; real mouse-grab behavior still needs a local
Windows smoke check because native GUI delivery cannot be emulated here.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import mouse_pointer_rod_windows as native


def extract_method(module, cls, name, env=None):
    source = (ROOT / 'src' / module).read_text('utf-8')
    tree = ast.parse(source)
    owner = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                 and node.name == cls)
    fn = next(node for node in owner.body if isinstance(node, ast.FunctionDef)
              and node.name == name)
    scope = dict(env or {})
    exec(compile(ast.Module(body=[fn], type_ignores=[]), 'rod_v03_test', 'exec'), scope)
    return scope[name]


class P:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __sub__(self, other):
        return NS(manhattanLength=lambda: abs(self.x-other.x)+abs(self.y-other.y))

    def __eq__(self, other):
        return isinstance(other, P) and (self.x, self.y) == (other.x, other.y)

    def setX(self, value):
        self.x = value

    def setY(self, value):
        self.y = value


class Cursor:
    current = P(11, 13)
    movements = []

    @classmethod
    def pos(cls):
        return cls.current

    @classmethod
    def setPos(cls, point):
        cls.current = point
        cls.movements.append((point.x, point.y))


def dispatch_setup(monkeypatch, menu_visible=True):
    class Menu:
        def isVisible(self):
            return menu_visible
        def frameGeometry(self):
            return NS(contains=lambda point: point == P(100, 120))
    menu = Menu()
    timers = []
    from types import ModuleType
    fake_mod = ModuleType('mouse_pointer_rod_windows')
    fake_mod.click_at = native.click_at
    fake_mod.restore_cursor_if_unchanged = native.restore_cursor_if_unchanged
    monkeypatch.setitem(sys.modules, 'mouse_pointer_rod_windows', fake_mod)
    monkeypatch.setattr(native, 'send_left_click', Mock(return_value=True))
    Cursor.current = P(11, 13)
    Cursor.movements = []
    callback = extract_method('mouse_pointer_rod.py', 'MousePointerRodPad',
                 '_dispatch_windows_click', env={
        'QApplication': NS(screenAt=lambda _: True,
                           topLevelWidgets=lambda: [menu]),
        'QMenu': Menu, 'QPoint': P, 'QCursor': Cursor,
        'QTimer': NS(singleShot=lambda ms, fn: timers.append((ms, fn))),
    })
    rod = NS(_cursor_on_blue=lambda: True,
             tip_global=lambda: (100, 120),
             _finish_native_warp=Mock())
    remote = NS(frameGeometry=lambda: NS(contains=lambda target: False))
    launcher = NS(footer=NS(setText=Mock()))
    return callback, rod, remote, launcher, timers


def test_own_qmenu_defers_cursor_return_until_qt_can_handle_click(monkeypatch):
    method, rod, remote, launcher, timers = dispatch_setup(monkeypatch)
    assert method(rod, 'select', remote, launcher)
    assert (Cursor.current.x, Cursor.current.y) == (100, 120)
    assert len(timers) == 1 and timers[0][0] == 70
    timers[0][1]()
    assert Cursor.movements == [(100, 120), (11, 13)]
    rod._finish_native_warp.assert_called_once()


def test_other_windows_keep_immediate_restore(monkeypatch):
    method, rod, remote, launcher, timers = dispatch_setup(monkeypatch, menu_visible=False)
    assert method(rod, 'select', remote, launcher)
    assert Cursor.movements == [(100, 120), (11, 13)]
    assert len(timers) == 1 and timers[0][0] == 85


def test_deferred_restore_does_not_override_user_movement(monkeypatch):
    method, rod, remote, launcher, timers = dispatch_setup(monkeypatch)
    assert method(rod, 'select', remote, launcher)
    Cursor.setPos(P(160, 180))  # The real user moved before the restore.
    timers[0][1]()
    assert Cursor.movements == [(100, 120), (160, 180)]
    rod._finish_native_warp.assert_called_once()


def test_native_adapter_defer_and_legacy_immediate(monkeypatch):
    monkeypatch.setattr(native, 'send_left_click', Mock(return_value=True))
    Cursor.current = P(11, 13)
    Cursor.movements = []
    deferred = []
    native.click_at(P(100, 120), cursor=Cursor,
                    defer_restore=lambda original, target: deferred.append((original, target)))
    assert (Cursor.current.x, Cursor.current.y) == (100, 120)
    assert len(deferred) == 1
    Cursor.setPos(deferred[0][0])
    assert (Cursor.current.x, Cursor.current.y) == (11, 13)
    native.click_at(P(100, 120), cursor=Cursor)
    assert (Cursor.current.x, Cursor.current.y) == (11, 13)


def test_keyword_history_uses_non_grabbing_qmenu_instead_of_instant_popup():
    source = (ROOT / 'src/expanded_view.py').read_text('utf-8')
    init_segment = source.split('self.middle_search_history_button = QToolButton(', 1)[1].split('middle_search_layout.addWidget(', 1)[0]
    assert '_NonGrabbingHistoryMenu(' in init_segment
    assert '.clicked.connect(' in init_segment
    assert 'InstantPopup' not in init_segment.split('self.middle_search_history_button.clicked.connect(', 1)[1]
    assert 'self.middle_search_history_button.setMenu(' not in init_segment
    cls = source.split('class _NonGrabbingHistoryMenu(QMenu):', 1)[1].split('class _MiddleSortButton(', 1)[0]
    assert 'Qt.WindowType.Tool' in cls
    assert 'Qt.WindowType.FramelessWindowHint' in cls
    assert 'Qt.WindowType.WindowStaysOnTopHint' in cls
    # The nested delete-history menu must not reintroduce popup grab.
    populator = source.split('def populate_middle_search_history_menu(',1)[1].split('def register_middle_search_history(',1)[0]
    assert 'forget = _NonGrabbingHistoryMenu(menu)' in populator


def test_keyword_menu_toggle_preserves_button_anchor():
    toggle = extract_method('expanded_view.py', 'ExpandedLauncherView',
                            'toggle_middle_search_history_menu',
                            {'QPoint': P, 'QApplication': NS(screenAt=lambda _:None,
                                                          primaryScreen=lambda:None)})
    button = NS(height=lambda:29, mapToGlobal=lambda pos:P(40+pos.x, 50+pos.y))
    menu = NS(isVisible=lambda:False, hide=Mock(), sizeHint=lambda:NS(width=lambda:200,height=lambda:100),popup=Mock())
    view = NS(middle_search_history_menu=menu,
              middle_search_history_button=button,
              populate_middle_search_history_menu=Mock())
    toggle(view)
    view.populate_middle_search_history_menu.assert_called_once()
    menu.popup.assert_called_once()
    pos = menu.popup.call_args.args[0]
    assert (pos.x, pos.y)==(40,79)
    menu.isVisible=lambda:True
    toggle(view)
    menu.hide.assert_called_once()
    assert menu.popup.call_count==1
