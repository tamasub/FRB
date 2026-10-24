"""Expanded root strip wheel: view-only hidden panels, safe keyboard/mouse.

The input model and actual method are exercised without Qt on CI machines;
Windows smoke test is still required to confirm native wheel dispatch/focus.
"""
import ast
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from expanded_view_model import (normalize_options, expanded_targets, toolbar_roots,
                                 root_wheel_target)


def sample():
    return json.loads((ROOT/'config/frb_launch_sample_data_v0_1.json').read_text(encoding='utf-8'))


def test_two_panel_buttons_hidden_without_removing_config_or_data():
    config = sample()
    roots, left, right = expanded_targets(config['items'], normalize_options(None))
    original_ids = [row['item_id'] for row in roots]
    visible = toolbar_roots(roots, left, right)
    assert [row['title'] for row in visible] == ['ZIP', 'Quick', '日付・定型文', 'メール宛先']
    assert left['item_id'] in original_ids and right['item_id'] in original_ids
    assert len(config['items']) > len(visible)
    assert [row['item_id'] for row in roots] == original_ids  # no mutation


def test_caption_changes_cannot_reintroduce_system_panel_buttons():
    roots, left, right = expanded_targets(sample()['items'], normalize_options(None))
    fake_rows = [dict(row, title=('自由な名前' if row['item_id'] in
                                 {left['item_id'], right['item_id']} else row['title']))
                 for row in roots]
    assert [row['item_id'] for row in toolbar_roots(fake_rows, left, right)] == [
        row['item_id'] for row in toolbar_roots(roots, left, right)]


def test_wheel_selection_clamps_at_ends_and_does_not_wrap():
    assert [root_wheel_target(0, n, 4) for n in (1, 2, 3, 4, 20)] == [1, 2, 3, 3, 3]
    assert root_wheel_target(0, -1, 4) == 0
    assert root_wheel_target(2, -3, 4) == 0
    assert root_wheel_target(0, 1, 0) is None


def real_wheel_method():
    src = ROOT / 'src' / 'expanded_view.py'
    tree = ast.parse(src.read_text(encoding='utf-8'))
    cl = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ExpandedLauncherView')
    method = next(n for n in cl.body if isinstance(n, ast.FunctionDef)
                  and n.name == 'wheel_first_level')
    klass = ast.ClassDef(name='WheelHandler', bases=[], keywords=[],
                         body=[method], decorator_list=[])
    # The real method uses only these Qt enum values and the current focus getter.
    qt = SimpleNamespace(KeyboardModifier=SimpleNamespace(NoModifier=0))
    app = SimpleNamespace(focusWidget=lambda: None)
    env = dict(Qt=qt, QApplication=app, root_wheel_target=root_wheel_target)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[klass], type_ignores=[])),
                 str(src), 'exec'), env)
    return env['WheelHandler']


class FakeButton:
    def __init__(self):
        self.checked = None

    def setChecked(self, checked):
        self.checked = checked


class FakeEvent:
    def __init__(self, *, angle=0, pixels=0, modifiers=0):
        self.angle = angle
        self.pixels = pixels
        self.mods = modifiers

    def modifiers(self):
        return self.mods

    def angleDelta(self):
        return SimpleNamespace(y=lambda: self.angle)

    def pixelDelta(self):
        return SimpleNamespace(y=lambda: self.pixels)


class WheelDemo(real_wheel_method()):
    __test__ = False

    def __init__(self, kinds=('category', 'category', 'command', 'category')):
        self.root_rows = [{'item_id': str(i), 'item_kind': kind} for i, kind in enumerate(kinds)]
        self.root_buttons = [FakeButton() for _ in kinds]
        self._wheel_root_id = None
        self._wheel_root_delta = 0
        self.opens = []
        self.focuses = []
        self.launches = []
        self.launcher = SimpleNamespace(menu=SimpleNamespace(isVisible=lambda: True,
                                                              close=lambda: self.opens.append('closed')))

    def focus_root(self, index):
        self.focuses.append(index)

    def open_cascade(self, row, button):
        self.opens.append(row['item_id'])


def test_down_wheel_switches_buttons_opens_only_categories():
    demo = WheelDemo()
    assert demo.wheel_first_level(FakeEvent(angle=-120), demo.root_buttons[0])
    assert demo.focuses == [1]
    assert demo.opens == ['1']
    assert [b.checked for b in demo.root_buttons] == [False, True, False, False]
    # Next item is a command. It gets highlighted, but never executed.
    assert demo.wheel_first_level(FakeEvent(angle=-120), demo.root_buttons[0])
    assert demo.focuses == [1, 2]
    assert demo.opens == ['1', 'closed']
    assert demo.launches == []
    assert [b.checked for b in demo.root_buttons] == [False, False, True, False]
    assert demo.wheel_first_level(FakeEvent(angle=-240), demo.root_buttons[0])
    assert demo.focuses[-1] == 3  # no wrap
    assert demo.opens[-1] == '3'
    assert demo.wheel_first_level(FakeEvent(angle=120), demo.root_buttons[0])
    assert demo.focuses[-1] == 2


def test_small_wheel_deltas_accumulate_until_one_step():
    demo = WheelDemo()
    for _ in range(3):
        assert demo.wheel_first_level(FakeEvent(angle=-30), demo.root_buttons[0])
    assert not demo.focuses
    assert demo.wheel_first_level(FakeEvent(angle=-30), demo.root_buttons[0])
    assert demo.focuses == [1]


def test_pixel_only_wheel_supports_touchpad_and_ctrl_ignored():
    demo = WheelDemo()
    assert demo.wheel_first_level(FakeEvent(pixels=-40), demo.root_buttons[0])
    assert demo.focuses == [1]
    assert not demo.wheel_first_level(FakeEvent(angle=-120, modifiers=1), demo.root_buttons[0])
    assert demo.focuses == [1]


def test_qt_wiring_limits_wheel_to_expanded_root_bar():
    view = (ROOT/'src/expanded_view.py').read_text(encoding='utf-8')
    app = (ROOT/'src/app.py').read_text(encoding='utf-8')
    assert 'visible_roots = toolbar_roots(roots, left, right)' in view
    assert 'self.root_rows, self.files_root, self.bookmarks_root = visible_roots, left, right' in view
    assert 'for index, row in enumerate(visible_roots):' in view
    assert 'button.installEventFilter(self)' in view
    assert 'source.installEventFilter(self)' in view
    assert 'def wheel_first_level(self, event, source):' in view
    assert 'self.open_cascade(row, button)' in view
    assert 'view.focus_panel(view.middle)' in app
    # Native Ctrl+Shift+F / Ctrl+Shift+B shortcuts and classic view stay intact.
    assert 'def execute_expanded_root_shortcut(self, index):' in app
    assert 'view.root_action(view.root_rows[index], button)' in app
