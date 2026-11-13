"""First-step A/B trial: Files List wheel uses Remote pad row-navigation semantics.

Pure-python tests; Windows and PySide6 are not required to run them.
"""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace as NS

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'src'))
from list_wheel_parity import (consume_remote_like_wheel, LIST_WHEEL_MATCH_REMOTE,
                               LIST_WHEEL_ANGLE_PER_NOTCH, LIST_WHEEL_PIXEL_PER_NOTCH,
                               LIST_WHEEL_MAX_STEPS_PER_EVENT)
from navigation_wrap import move_tree_selection

SOURCE = (BASE / 'src/expanded_view.py').read_text(encoding='utf8')


def extract_method(name):
    module = ast.parse(SOURCE)
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef)
               and n.name == 'ExpandedLauncherView')
    return next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)


class Row:
    def __init__(self, index): self.index = index
    def isHidden(self): return False
    def isDisabled(self): return False


class Tree:
    def __init__(self, count=30):
        self.items = [Row(i) for i in range(count)]
        self.current = self.items[0] if self.items else None
        self.scrolled = []
        self.focused = []
    def topLevelItemCount(self): return len(self.items)
    def topLevelItem(self, index): return self.items[index]
    def currentItem(self): return self.current
    def setCurrentItem(self, item): self.current = item
    def scrollToItem(self, item): self.scrolled.append(item.index)
    def setFocus(self, focus): self.focused.append(focus)
    def state(self): return 'ready'


class Event:
    def __init__(self, angle=-120, pixel=0, modifiers=0):
        self.angle = angle
        self.pixel = pixel
        self.mods = modifiers
    def angleDelta(self): return NS(y=lambda: self.angle)
    def pixelDelta(self): return NS(y=lambda: self.pixel)
    def modifiers(self): return self.mods


class Demo:
    def __init__(self, count=30, warp=True):
        self.middle = NS(tree=Tree(count))
        self.launcher = NS(pointer_warp_enabled=warp)
        self._workspace_mode = 'files'
        self._middle_parity_angle_remainder = 0
        self._middle_parity_pixel_remainder = 0
        self._middle_follow_pending = None
        self._middle_follow_scheduled = False
        self.followed = []
        self.restored = 0
    def isVisible(self): return True
    def ensure_middle_current_selection(self): self.restored += 1
    def follow_middle_pointer(self):
        self.followed.append(self._middle_follow_pending.index)
        self._middle_follow_pending = None
        self._middle_follow_scheduled = False


deferred = []
qt = NS(KeyboardModifier=NS(NoModifier=0),
        MouseButton=NS(NoButton=0), FocusReason=NS(MouseFocusReason='mouse'))
view = NS(State=NS(EditingState='editing'))
world = NS(mouseButtons=lambda: 0)
timer = NS(singleShot=lambda ms, callback: deferred.append(callback))
ns = dict(Qt=qt, QAbstractItemView=view, QApplication=world, QTimer=timer,
          move_tree_selection=move_tree_selection,
          consume_remote_like_wheel=consume_remote_like_wheel)
method = extract_method('wheel_middle_like_remote_button')
exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
             '<extracted>', 'exec'), ns)
Demo.wheel_middle_like_remote_button = ns[method.name]


def setup_function():
    deferred.clear()


def test_configuration_matches_unmodified_remote_pad_step_values():
    assert LIST_WHEEL_MATCH_REMOTE is True
    assert (LIST_WHEEL_ANGLE_PER_NOTCH, LIST_WHEEL_PIXEL_PER_NOTCH,
            LIST_WHEEL_MAX_STEPS_PER_EVENT) == (120, 36, 5)
    pad_source = (BASE / 'src/launch_remote.py').read_text(encoding='utf8')
    pad_method = pad_source.split('    def wheelEvent(self, event):', 1)[1].split(
        '    def mousePressEvent(self, event):', 1)[0]
    assert 'self._angle_remainder / 120' in pad_method
    assert 'self._pixel_remainder / 36' in pad_method
    assert 'min(abs(steps), 5)' in pad_method


def test_direct_wheel_moves_same_single_row_as_remote_button():
    demo = Demo()
    assert demo.wheel_middle_like_remote_button(Event(-120))
    assert demo.middle.tree.current.index == 1
    assert demo.middle.tree.scrolled == [1]
    assert demo.restored == 1
    assert len(deferred) == 1
    deferred.pop()()
    assert demo.followed == [1]
    assert demo.wheel_middle_like_remote_button(Event(120))
    assert demo.middle.tree.current.index == 0


def test_fast_burst_matches_remote_notches_without_acceleration():
    demo = Demo()
    assert demo.wheel_middle_like_remote_button(Event(-480))
    assert demo.middle.tree.current.index == 4
    # Four sequential current selections, never an interpolated jump.
    assert demo.middle.tree.scrolled == [1, 2, 3, 4]
    assert demo.wheel_middle_like_remote_button(Event(-720))
    # Remote clamps to five steps per event even if more notches are reported.
    assert demo.middle.tree.current.index == 9
    assert len(deferred) == 1  # Coalesced pointer-follow only.
    deferred.pop()()
    assert demo.followed == [9]


def test_precision_pixel_accumulator_and_reverse():
    demo = Demo()
    for _ in range(3):
        assert demo.wheel_middle_like_remote_button(Event(angle=0, pixel=-10))
    assert demo.middle.tree.current.index == 0
    assert demo.wheel_middle_like_remote_button(Event(angle=0, pixel=-6))
    assert demo.middle.tree.current.index == 1
    assert demo.wheel_middle_like_remote_button(Event(angle=0, pixel=36))
    assert demo.middle.tree.current.index == 0


def test_modifiers_editing_and_other_workspace_keep_native_fallback():
    demo = Demo()
    assert demo.wheel_middle_like_remote_button(Event(modifiers=1)) is False
    demo.middle.tree.state = lambda: 'editing'
    assert demo.wheel_middle_like_remote_button(Event()) is False
    demo.middle.tree.state = lambda: 'ready'
    demo._workspace_mode = 'browser'
    assert demo.wheel_middle_like_remote_button(Event()) is False
    assert demo.middle.tree.current.index == 0


def test_no_warp_environment_keeps_selection_parity():
    demo = Demo(warp=False)
    assert demo.wheel_middle_like_remote_button(Event(-240))
    assert demo.middle.tree.current.index == 2
    assert deferred == []


def test_trial_is_only_enabled_on_middle_pane_and_wan_remains_fallback():
    assert 'self.middle.tree.remote_parity_wheel_callback = self.wheel_middle_like_remote_button' in SOURCE
    assert 'self.middle.tree.adaptive_wheel_callback = self.wheel_middle_at_edge' in SOURCE
    tree_method = SOURCE.split('class _SeparatedFileTree(', 1)[1].split('class _BreadcrumbSurface',1)[0]
    segment = tree_method.split('    def wheelEvent(self, event):',1)[1].split('    def mousePressEvent(',1)[0]
    assert segment.index('remote_parity(event)') < segment.index('super().wheelEvent(event)')
    assert 'if remote_parity is not None and remote_parity(event):' in segment
    # The Remote event handler and other pane hooks are intentionally untouched.
    assert 'self.left.tree.adaptive_wheel_callback = self.wheel_files_at_edge' in SOURCE
