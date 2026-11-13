"""Regression for List-origin confirmation and safe Browser blank-space wheel.

Qt-free source-method tests; the actual Windows focus/cursor behavior must be
checked in the desktop build. Nothing in these tests runs Git or opens URLs.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

from bookmark_cursor_follow import nearest_visible_button, cursor_target
from test_bookmark_strip_hybrid_exp_header_20261103 import (
    Demo, Event, Cursor, P, Button,
)
from test_remote_confirmation_footer_and_header_20261103 import (
    fake_confirmation_module, real_method,
)

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf8')
TEXT = (ROOT / 'src/remote_text_dialog.py').read_text(encoding='utf8')


def _wheel(t, *, angle=-120, pixels=0):
    return NS(type=lambda: t, angleDelta=lambda: P(0, angle),
              pixelDelta=lambda: P(0, pixels), accept=Mock())


def test_background_list_wheel_selects_confirmation_and_consumes_event():
    module, widgets = fake_confirmation_module()
    yes, no = module.RemoteConfirmation.YES, module.RemoteConfirmation.NO
    buttons = {id_: NS(setStyleSheet=Mock(), setFocus=Mock(), update=Mock(), click=Mock())
               for id_ in (yes, no)}
    owner = module.RemoteConfirmation.__new__(module.RemoteConfirmation)
    owner.launcher = NS(remote_window=None)
    owner.dialog = NS(button=lambda value:buttons[value], setDefaultButton=Mock())
    owner.selected = no
    owner._background_wheel_angle = 0
    owner._background_wheel_pixel = 0
    question, remote, list_window = object(), object(), object()
    guard = module.ConfirmationInputGuard(question, remote, owner)
    list_widget = widgets.QWidget()
    list_widget._window = list_window
    event = _wheel(module.QEvent.Type.Wheel, angle=-120)
    assert guard.eventFilter(list_widget, event) is True
    event.accept.assert_called_once_with()
    assert owner.selected == yes  # Select only; no side effects before click.
    buttons[yes].click.assert_not_called()
    owner.remote_command('CLICK')
    buttons[yes].click.assert_called_once()
    # Genuine wheel on the Remote still belongs to the Remote pad itself.
    remote_widget = widgets.QWidget()
    remote_widget._window = remote
    assert guard.eventFilter(remote_widget, event) is False
    # Mouse on the original Files List must not click/launch a file behind dialog.
    click = _wheel(module.QEvent.Type.MouseButtonPress)
    assert guard.eventFilter(list_widget, click) is True


def test_background_wheel_accumulates_small_ticks_instead_of_overstepping():
    module, _ = fake_confirmation_module()
    owner = module.RemoteConfirmation.__new__(module.RemoteConfirmation)
    owner.launcher = NS(remote_window=None)
    owner.dialog = NS(button=lambda _:NS(setStyleSheet=Mock(), setFocus=Mock(), update=Mock()),
                      setDefaultButton=Mock())
    owner.selected = owner.NO
    owner._background_wheel_angle = 0
    owner._background_wheel_pixel = 0
    for _ in range(3):
        owner.background_wheel(_wheel(module.QEvent.Type.Wheel, angle=-30))
    assert owner.selected == owner.NO
    owner.background_wheel(_wheel(module.QEvent.Type.Wheel, angle=-30))
    assert owner.selected == owner.YES


def test_git_message_text_dialog_receives_list_wheel_too():
    tree = ast.parse(TEXT)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
               and n.name == 'RemoteTextDialog')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                  and n.name == 'background_wheel')
    namespace = {}
    exec(compile(ast.Module(body=[method], type_ignores=[]), '<text-dialog>', 'exec'), namespace)
    calls=[]
    obj = NS(_background_wheel_angle=0, _background_wheel_pixel=0,
             remote_command=lambda command:calls.append(command))
    for _ in range(3):
        namespace['background_wheel'](obj, _wheel(0, angle=-40))
    assert calls == ['DOWN']
    assert 'ConfirmationInputGuard(self.dialog, remote, self)' in TEXT


def test_confirmation_beats_stale_context_menu_and_exp_list_routing():
    method = real_method(APP, 'Launcher', 'remote_command')
    confirm, context = Mock(), Mock()
    host = NS(remote_window=None, _remote_confirmation=confirm, _remote_context_wheel=context)
    for command in ('UP', 'DOWN', 'CLICK'):
        method(host, command)
    assert confirm.remote_command.call_count == 3
    context.command.assert_not_called()
    assert 'menu_wheel.stop()' in APP
    assert APP.index("confirmation = getattr(self, '_remote_confirmation', None)",
                     APP.index('    def remote_command(self, command):')) < APP.index(
        "menu_wheel = getattr(self, '_remote_context_wheel', None)",
        APP.index('    def remote_command(self, command):'))


def test_nearest_visible_bookmark_rejects_offscreen_edges_and_clamps():
    size=(120, 40)
    rows=[(-900, 5, 60, 27), (5, 5, 35, 27),
          (45, 5, 40, 27), (2400, 5, 90, 27)]
    index, point=nearest_visible_button(size, rows, (115, 38))
    assert index==2 and 45 <= point[0] < 85 and 5 <= point[1] < 32
    index, point=nearest_visible_button(size, rows, (2, 38))
    assert index==1 and 5 <= point[0] < 40
    assert nearest_visible_button(size, [(-100, 5, 20, 20),
                                         (2400, 5, 60, 27)], (55, 38)) is None
    assert cursor_target(size, (118, 4, 20, 26), 118) == (118, 16)


def test_blank_space_edge_wheel_uses_closest_visible_not_last_first():
    Cursor.pos_value=P(300, 36)
    Cursor.moved=[]
    bar=Demo(scroll=0, end=0)
    bar.pointer_follow_enabled=lambda:True
    bar._scroll_wheel(Event(angle=120, x=300, y=36))  # at left edge, move left
    assert bar._wheel_current in bar._buttons
    assert 0 <= Cursor.pos().x() < 400
    assert 0 <= Cursor.pos().y() < 40
    assert Cursor.moved
    # At the right edge, never jump to a 5000px offscreen button.
    Cursor.pos_value=P(300, 36)
    Cursor.moved=[]
    bar=Demo(scroll=50, end=50)
    bar._buttons=[Button(-900), Button(0), Button(45), Button(5000)]
    bar.pointer_follow_enabled=lambda:True
    bar._scroll_wheel(Event(angle=-120, x=300, y=36))
    assert bar._wheel_current in bar._buttons[1:3]
    assert all(0 <= pos.x() < 400 and 0 <= pos.y() < 40 for pos in Cursor.moved)
    assert not bar.opened


def test_blank_area_scroll_routes_in_real_component_and_does_not_execute_url():
    source=(ROOT / 'src/browser_bookmark_bar.py').read_text(encoding='utf8')
    assert 'self.bookmark_strip_inner.installEventFilter(self)' in source
    assert 'self.viewport().installEventFilter(self)' in source
    assert 'obj is getattr(self, \'bookmark_strip_inner\', None)' in source
    assert 'self._nearest_visible_button(pointer)' in source
    wheel=ast.get_source_segment(source, next(
        n for c in ast.parse(source).body if isinstance(c, ast.ClassDef)
        and c.name=='HorizontalBookmarkBar' for n in c.body
        if isinstance(n, ast.FunctionDef) and n.name=='_scroll_wheel'))
    assert '_open_bookmark_bar_row(' not in wheel
