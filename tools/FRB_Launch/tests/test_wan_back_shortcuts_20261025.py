"""Regression checks for the four WAN/Back experiment requirements.

Qt-specific visual/interaction checks need a Windows PySide6 run; these keep
pure input semantics and key source wiring checked on headless CI.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'src'))
from wheel_edge_hold import EdgeWheelHold


def test_sustained_upward_wheel_reaches_back_target():
    now = [0.0]
    hold = EdgeWheelHold(clock=lambda: now[0])
    assert not hold.feed(True, 1)
    now[0] += .23
    assert not hold.feed(True, 1)
    now[0] += .24
    assert hold.feed(True, 1)
    assert not hold.feed(True, 1)  # one action per hold


def test_short_burst_not_enough_to_trigger():
    now = [0.0]
    hold = EdgeWheelHold(clock=lambda: now[0])
    assert not hold.feed(True, 1)
    now[0] += .1
    assert not hold.feed(True, 5)


def test_slow_continuous_input_can_trigger():
    now = [0.0]
    hold = EdgeWheelHold(clock=lambda: now[0])
    assert not hold.feed(True, 1)
    now[0] += .35
    assert not hold.feed(True, 1)
    now[0] += .36
    assert hold.feed(True, 1)


def test_gap_resets_input_episode():
    now = [0.0]
    hold = EdgeWheelHold(clock=lambda: now[0])
    assert not hold.feed(True, 2)
    now[0] += .9
    assert not hold.feed(True, 2)
    now[0] += .49
    assert hold.feed(True, 1)


def test_not_at_edge_resets_input_episode():
    now = [0.0]
    hold = EdgeWheelHold(clock=lambda: now[0])
    assert not hold.feed(True, 2)
    now[0] += .3
    assert not hold.feed(False, 1)
    now[0] += .3
    assert not hold.feed(True, 1)


def test_zero_wheel_input_is_not_a_continuation():
    now = [0.0]
    hold = EdgeWheelHold(clock=lambda: now[0])
    assert not hold.feed(True, 2)
    assert not hold.feed(True, 0)
    now[0] += .46
    assert not hold.feed(True, 1)


def test_three_layer_fallback_pages_use_compact_wan_engine():
    source = (HERE / 'src/app.py').read_text(encoding='utf-8')
    widget = (HERE / 'src/reorder_widgets.py').read_text(encoding='utf-8')
    assert "self.view_mode not in ('classic', 'expanded')" in source
    assert "self.view_mode not in ('classic', 'expanded')" in source
    assert "getattr(self.launcher, 'view_mode', None) not in ('classic', 'expanded')" in widget
    assert 'self.list.setVisible(not active)' in source


def test_doubleclick_back_requires_middle_viewport_and_left_button():
    source = (HERE / 'src/expanded_view.py').read_text(encoding='utf-8')
    assert "getattr(self, 'middle', None) is None" in source
    assert 'in_tree = obj is self.middle.tree.viewport()' in source
    assert "lane = obj is getattr(self, 'middle_back_lane', None)" in source
    assert 'event.button() != Qt.MouseButton.LeftButton' in source
    assert 'event.type() == QEvent.Type.MouseButtonDblClick' in source
    assert 'self.middle_blank_back_at(event.position().toPoint())' in source
    assert 'if lane or (in_tree' in source
    assert 'self.go_up()' in source


def test_right_lane_cannot_activate_a_row_with_single_click():
    source = (HERE / 'src/expanded_view.py').read_text(encoding='utf-8')
    assert 'MIDDLE_BACK_LANE_WIDTH = 24' in source
    assert 'self.middle_back_lane.setFixedWidth(MIDDLE_BACK_LANE_WIDTH)' in source
    assert 'middle_tree_layout.addWidget(self.middle_back_lane)' in source
    assert 'if lane:' in source
    assert 'This is an independent QWidget, not an editable item cell' in source


def test_middle_back_wheel_only_moves_pointer_and_never_clicks():
    source = (HERE / 'src/expanded_view.py').read_text(encoding='utf-8')
    section = source.split('    def follow_middle_back_pointer(self):',1)[1].split('    def sync_first_files_hover_from_cursor',1)[0]
    assert 'QCursor.setPos(destination)' in section
    assert '.click(' not in section
    assert 'go_up(' not in section
    assert 'QCursor.pos() != original' in section


def test_consecutive_wheels_start_only_on_first_row():
    source = (HERE / 'src/expanded_view.py').read_text(encoding='utf-8')
    section = source.split('    def wheel_middle_at_edge(self,',1)[1].split('    def follow_middle_pointer(self):',1)[0]
    assert 'index == 0 and movement < 0' in section
    assert 'tree.currentItem() is tree.topLevelItem(0)' in section
    assert 'hold.feed(at_first' in section


def _hit_test_demo():
    """Run the actual widget handlers with small Qt-free stand-ins."""
    import ast
    from types import SimpleNamespace
    source = ast.parse((HERE / 'src/expanded_view.py').read_text(encoding='utf-8'))
    cls = next(n for n in source.body if isinstance(n, ast.ClassDef)
               and n.name == 'ExpandedLauncherView')
    methods = [n for n in cls.body if isinstance(n, ast.FunctionDef)
               and n.name in ('handle_middle_back_double_click',
                              'middle_back_lane_at', 'middle_blank_back_at')]
    tree_cls = ast.ClassDef(name='HitDemo', bases=[], keywords=[], body=methods,
                            decorator_list=[])
    ns = {'MIDDLE_BACK_LANE_WIDTH': 24,
          'Qt': SimpleNamespace(MouseButton=SimpleNamespace(LeftButton=1),
                                KeyboardModifier=SimpleNamespace(NoModifier=0)),
          'QEvent': SimpleNamespace(Type=SimpleNamespace(
              MouseButtonPress=1, MouseButtonRelease=2,
              MouseButtonDblClick=3))}
    exec(compile(ast.fix_missing_locations(
        ast.Module(body=[tree_cls], type_ignores=[])), 'expanded_view.py', 'exec'), ns)

    class Point:
        def __init__(self, x, y): self._x, self._y = x, y
        def x(self): return self._x
        def y(self): return self._y

    class Viewport:
        def width(self): return 200
        def rect(self): return self
        def contains(self, p): return 0 <= p.x() < 200 and 0 <= p.y() < 200

    class Tree:
        def __init__(self): self.view = Viewport()
        def viewport(self): return self.view
        def itemAt(self, p): return 'folder' if p.y() < 80 else None

    class Demo(ns['HitDemo']):
        def __init__(self):
            self.middle = SimpleNamespace(tree=Tree())
            self.middle_back_lane = object()
            self.back_calls = 0
        def isVisible(self): return True
        def go_up(self): self.back_calls += 1

    class Event:
        def __init__(self, x, y, event_type=3, mods=0):
            self.point = Point(x, y)
            self.kind, self.mods = event_type, mods
            self.accepted = False
        def position(self): return SimpleNamespace(toPoint=lambda: self.point)
        def button(self): return 1
        def modifiers(self): return self.mods
        def type(self): return self.kind
        def accept(self): self.accepted = True

    return Demo(), Event


def test_middle_blank_double_click_uses_existing_back_only():
    demo, Event = _hit_test_demo()
    assert demo.handle_middle_back_double_click(demo.middle.tree.viewport(), Event(40, 120))
    assert demo.back_calls == 1
    # A normal file-row double click must go through the original handler.
    assert not demo.handle_middle_back_double_click(demo.middle.tree.viewport(), Event(40, 20))
    assert demo.back_calls == 1


def test_middle_right_lane_single_click_does_not_activate_file():
    demo, Event = _hit_test_demo()
    assert demo.handle_middle_back_double_click(demo.middle_back_lane, Event(190, 20, 1))
    assert demo.handle_middle_back_double_click(demo.middle_back_lane, Event(190, 20, 2))
    assert demo.back_calls == 0
    assert demo.handle_middle_back_double_click(demo.middle_back_lane, Event(190, 20, 3))
    assert demo.back_calls == 1
    # Same x-coordinate over a *real row* is not a second Back target.
    assert not demo.handle_middle_back_double_click(demo.middle.tree.viewport(), Event(190, 20, 3))


def test_middle_not_initialized_does_not_crash_event_filter():
    demo, Event = _hit_test_demo()
    demo.middle = None
    assert not demo.handle_middle_back_double_click(None, Event(190, 20))


def test_modifier_click_does_not_trigger_back():
    demo, Event = _hit_test_demo()
    assert not demo.handle_middle_back_double_click(demo.middle.tree.viewport(), Event(190, 20, mods=1))
    assert demo.back_calls == 0
