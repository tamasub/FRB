"""Mouse double-click release/foreground handoff without requiring Windows/Qt.

The regression is not just execution order: Windows may revoke a new process's
foreground privilege when the second click's UP arrives after spawn. Verify
that the child is not started until after that UP event has been dispatched.
"""
import ast
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
source = ast.parse((ROOT / 'src/app.py').read_text(encoding='utf-8'))
launcher = next(c for c in source.body if isinstance(c, ast.ClassDef) and c.name == 'Launcher')


def extract_method(name):
    fn = next(n for n in launcher.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), str(ROOT / 'src/app.py'), 'exec')


class Base:
    def eventFilter(self, *_):
        return False


class MouseEvent:
    def __init__(self, event_type, position=0, button='left'):
        self.event_type, self.p, self.b, self.accepted = event_type, position, button, False
    def type(self): return self.event_type
    def button(self): return self.b
    def position(self): return self
    def toPoint(self): return self.p
    def accept(self): self.accepted = True


class RowItem:
    def __init__(self, row): self.row = row
    def data(self, *_): return self.row


class MouseDoubleClickTests(unittest.TestCase):
    def setUp(self):
        self.order = []
        self.callbacks = []
        self.row = {'item_id':'studio_app', 'item_kind':'command'}
        self.viewport = object()
        self.item = RowItem(self.row)
        self.visible = True
        self.foreground = 111
        self.active_hwnd = 222
        self.win = SimpleNamespace(IS_WINDOWS=True,
            foreground=lambda:self.foreground,
            activate_keyboard_window=self.focus_launcher)
        qtimer = SimpleNamespace(singleShot=lambda ms,fn:self.callbacks.append((ms,fn)))
        qt = SimpleNamespace(MouseButton=SimpleNamespace(LeftButton='left'),
                             ItemDataRole=SimpleNamespace(UserRole=32))
        events = SimpleNamespace(Type=SimpleNamespace(MouseButtonDblClick='dbl',MouseButtonRelease='up',KeyPress='key',InputMethod='ime'))
        env = dict(Qt=qt, QEvent=events, QTimer=qtimer, windows=self.win,
                   DIAG=logging.getLogger('mouse_test'), super=lambda:Base())
        for name in ('eventFilter','activate_after_mouse_release'):
            exec(extract_method(name),env)
        self.methods=env
        self.stub = SimpleNamespace(
            list=SimpleNamespace(viewport=lambda:self.viewport, itemAt=lambda p:self.item if p==1 else None),
            tabs=object(), search=object(), stack=[], selection=None, busy=False,
            _pending_mouse_activation=None, _pending_mouse_foreground=None,
            winId=lambda:self.active_hwnd, isVisible=lambda:self.visible,
            activate=lambda row:self.order.append(('activate',row['item_id'])),
            go_back=lambda:self.order.append('back'))
        self.stub.activate_after_mouse_release=lambda row,fg:self.methods['activate_after_mouse_release'](self.stub,row,fg)

    def focus_launcher(self, hwnd, expected_foreground=None):
        self.order.append(('focus', hwnd, expected_foreground))
        if self.foreground != expected_foreground:return False
        self.foreground=hwnd
        return True

    def dispatch(self, typ, position=1, button='left'):
        ev=MouseEvent(typ, position, button)
        return self.methods['eventFilter'](self.stub,self.viewport,ev),ev.accepted

    def drain(self):
        queued=self.callbacks[:];self.callbacks.clear()
        for delay,fn in queued: self.assertEqual(delay,0);fn()

    def test_queued_on_second_down_only_launched_after_up(self):
        self.foreground=222  # already keyboard-focused launcher
        self.assertEqual(self.dispatch('dbl'),(True,True))
        self.assertEqual(self.order,[])
        self.assertEqual(self.callbacks,[])
        self.assertEqual(self.dispatch('up'),(True,True))
        self.assertEqual(self.order,[])  # still no launch inside mouse event
        self.drain()
        self.assertEqual(self.order,[('activate','studio_app')])

    def test_visible_but_unfocused_tool_regains_focus_on_release(self):
        self.assertEqual(self.dispatch('dbl'),(True,True))
        self.assertEqual(self.dispatch('up'),(True,True))
        self.drain()
        self.assertEqual(self.order,[('focus',222,111),('activate','studio_app')])

    def test_user_switches_app_between_down_and_up_does_not_steal_focus(self):
        self.dispatch('dbl');self.foreground=333
        self.dispatch('up');self.drain()
        self.assertEqual(self.order,[('focus',222,111),('activate','studio_app')])
        self.assertEqual(self.foreground,333)

    def test_hidden_launcher_cancels_deferred_activation(self):
        self.dispatch('dbl');self.dispatch('up');self.visible=False;self.drain()
        self.assertEqual(self.order,[])

    def test_empty_submenu_doubleclick_remains_back(self):
        self.stub.stack=['folder']
        self.assertEqual(self.dispatch('dbl',position=0),(True,True))
        self.assertEqual(self.order,['back'])
        self.assertEqual(self.callbacks,[])

    def test_right_click_and_single_click_do_not_activate(self):
        self.assertEqual(self.dispatch('dbl',button='right'),(False,False))
        self.assertEqual(self.dispatch('up'),(False,False))
        self.assertEqual(self.callbacks,[])

    def test_new_activations_are_independent(self):
        for _ in range(2):
            self.dispatch('dbl');self.dispatch('up');self.drain()
        self.assertEqual([e for e in self.order if e[0]=='activate'],
                         [('activate','studio_app'),('activate','studio_app')])


if __name__ == '__main__': unittest.main()
