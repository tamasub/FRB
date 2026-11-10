"""Regression: Qt may invoke QScrollArea.eventFilter while setWidget runs.

The test intentionally requires no PySide6.  Its fake QScrollArea delivers an
actual Wheel event to the newly constructed object from inside setWidget,
matching the startup timing that caused repeated AttributeError on Windows.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

SRC = (Path(__file__).resolve().parents[1] / 'src/browser_bookmark_bar.py')


def _load_qt_free_bar():
    tree = ast.parse(SRC.read_text(encoding='utf-8'))
    bar_node = next(node for node in tree.body
                    if isinstance(node, ast.ClassDef) and node.name == 'HorizontalBookmarkBar')
    bar_node.body = [node for node in bar_node.body
                     if isinstance(node, ast.FunctionDef)
                     and node.name in ('__init__', 'eventFilter', '_settle_wheel_current')]
    qt_event = SimpleNamespace(Type=SimpleNamespace(Wheel=17, MouseButtonPress=18))
    evt = SimpleNamespace(type=lambda: qt_event.Type.Wheel)

    class ScrollArea:
        def __init__(self, parent=None):
            self.events_seen = 0
        def setObjectName(self, name):
            pass
        def setWidgetResizable(self, val):
            pass
        def setFrameShape(self, val):
            pass
        def setVerticalScrollBarPolicy(self, val):
            pass
        def setHorizontalScrollBarPolicy(self, val):
            pass
        def setMaximumHeight(self, val):
            pass
        def setMinimumHeight(self, val):
            pass
        def setFocusPolicy(self, value):
            pass
        def setFocus(self, reason):
            self.focus_reason = reason
        def viewport(self):
            return self
        def installEventFilter(self, obj):
            pass
        def setWidget(self, widget):
            self.events_seen += 1
            self.eventFilter(widget, evt)  # event arrives *inside* Qt setup
        def eventFilter(self, obj, event):
            return False

    class Widget:
        def __init__(self, parent=None):
            pass
        def setObjectName(self, name):
            pass
        def installEventFilter(self, obj):
            pass

    class HBoxLayout:
        def __init__(self, parent=None):
            pass
        def setContentsMargins(self, *args):
            pass
        def setSpacing(self, value):
            pass

    class Timer:
        def __init__(self, parent=None):
            self.timeout = SimpleNamespace(connect=lambda fn: None)
        def setSingleShot(self, value): pass
        def setInterval(self, value): pass

    fake_globals = {
        'QScrollArea': ScrollArea,
        'QTimer': Timer,
        'QFrame': SimpleNamespace(Shape=SimpleNamespace(NoFrame=0)),
        'Qt': SimpleNamespace(ScrollBarPolicy=SimpleNamespace(ScrollBarAlwaysOff=0, ScrollBarAsNeeded=1), FocusPolicy=SimpleNamespace(ClickFocus=0), FocusReason=SimpleNamespace(MouseFocusReason=0)),
        'QWidget': Widget,
        'QHBoxLayout': HBoxLayout,
        'QEvent': qt_event,
    }
    ast.fix_missing_locations(bar_node)
    exec(compile(ast.Module(body=[bar_node], type_ignores=[]), str(SRC), 'exec'), fake_globals)
    return fake_globals['HorizontalBookmarkBar'], evt


def test_early_qt_event_during_setwidget_does_not_raise():
    bar_type, _ = _load_qt_free_bar()
    bar = bar_type()
    assert bar.events_seen == 1
    assert bar._buttons == []
    assert bar._wheel_current is None


def test_event_filter_is_safe_before_buttons_created_or_after_teardown():
    bar_type, wheel_event = _load_qt_free_bar()
    bar = bar_type()
    del bar._buttons  # simulate partial initialization or Qt teardown
    assert bar.eventFilter(object(), wheel_event) is False


def test_wheel_over_bookmark_button_routes_to_scroll():
    bar_type, wheel_event = _load_qt_free_bar()
    bar = bar_type()
    button = object()
    called = []
    bar._buttons = [button]
    bar._scroll_wheel = lambda ev, source=None: called.append((ev, source))
    assert bar.eventFilter(button, wheel_event) is True
    assert called == [(wheel_event, button)]
    assert bar.eventFilter(object(), wheel_event) is False


def test_wheel_on_blank_inner_and_viewport_is_handled_and_click_takes_focus():
    bar_type, wheel_event = _load_qt_free_bar()
    bar = bar_type()
    called = []
    bar._scroll_wheel = lambda ev, source=None: called.append((ev, source))
    assert bar.eventFilter(bar.bookmark_strip_inner, wheel_event) is True
    assert bar.eventFilter(bar.viewport(), wheel_event) is True
    assert [target for _, target in called] == [bar.bookmark_strip_inner, bar.viewport()]
    press = SimpleNamespace(type=lambda: 18)
    assert bar.eventFilter(bar.bookmark_strip_inner, press) is False
    assert bar.focus_reason == 0
