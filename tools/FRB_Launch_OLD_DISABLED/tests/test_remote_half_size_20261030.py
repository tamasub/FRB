"""Remote v0.5 trial: minimize travel without changing semantic commands.

GUI is tested on the user's Windows machine; these tests work without Qt.
"""
import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from remote_navigation import popup_at_hotspot

SOURCE = (ROOT / 'src' / 'launch_remote.py').read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)


def remote_init():
    cls = next(node for node in TREE.body
               if isinstance(node, ast.ClassDef) and node.name == 'LaunchRemote')
    return next(node for node in cls.body
                if isinstance(node, ast.FunctionDef) and node.name == '__init__')


def call_literals(method_name):
    init = remote_init()
    calls = []
    for node in ast.walk(init):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == method_name):
            vals = [arg.value if isinstance(arg, ast.Constant) else None for arg in node.args]
            kwargs = {kw.arg: (kw.value.value if isinstance(kw.value, ast.Constant) else None)
                      for kw in node.keywords}
            calls.append((vals, kwargs))
    return calls


def test_half_area_geometry_is_compact_and_balanced():
    width = next(args[0] for args, _ in call_literals('setFixedWidth') if args)
    assert width == 168
    # The former v0.4 was 224 px wide and roughly 210 px high.
    # v0.5 uses fixed 20/24/36 px high rows (approx 138 px in total).
    assert width * 138 < (224 * 210) * .55
    source = SOURCE
    assert 'self.setFixedSize(36, 36)' in source
    assert 'grid.setHorizontalSpacing(2)' in source
    assert 'grid.setVerticalSpacing(2)' in source
    assert 'root.setContentsMargins(5, 5, 5, 5)' in source


def test_control_buttons_remain_and_up_down_are_only_on_wheel():
    button_calls = call_literals('_button')
    commands = {args[2] for args, kw in button_calls if len(args) > 2}
    assert commands == {'HOME', 'CLOSE', 'BACKTAB', 'TAB', 'LEFT', 'RIGHT',
                        'SEARCH_HISTORY', 'FOLDER_HISTORY'}
    assert 'self.command.emit(\'UP\' if steps > 0 else \'DOWN\')' in SOURCE
    assert "self.command.emit('ENTER')" in SOURCE
    for forbidden in ('SendKeys(', 'SendInput(', 'QKeyEvent(', 'keybd_event('):
        assert forbidden not in SOURCE


def test_mouse_hotspot_still_under_pointer():
    # The smaller pad is still placed directly below the pointer.
    mouse_x, mouse_y = (750, 460)
    # 5 px margin + 52 px left column + 2 px gap + 18 px half pad.
    hot_x = 5 + 52 + 2 + 18
    hot_y = 5 + 20 + 3 + 14 + 3 + 24 + 2 + 18
    x, y = popup_at_hotspot(mouse_x, mouse_y, 168, 138,
                            0, 0, 1400, 900, hot_x, hot_y)
    assert (x + hot_x, y + hot_y) == (mouse_x, mouse_y)


def test_shortcut_rows_keep_adjacent_history_buttons():
    # A three-column grid, with histories on either side of the wheel.
    assert 'grid.addWidget(self.pad, 1, 1)' in SOURCE
    assert "'SEARCH_HISTORY', width=52, height=24, role='small'), 2, 0" in SOURCE
    assert "'FOLDER_HISTORY', width=66, height=24, role='small'), 2, 2" in SOURCE
