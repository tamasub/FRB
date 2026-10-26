"""Expanded keyboard contract: no GUI dependency (rules + source wiring)."""
import ast
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from expanded_keyboard_model import (FOCUS_ORDER, tab_target, root_step,
                                     middle_back_target, row_right_action)


def test_focus_ring_forward_and_backward():
    assert FOCUS_ORDER == ('search', 'pages', 'roots', 'files', 'directory', 'bookmarks')
    assert [tab_target(area) for area in FOCUS_ORDER] == list(FOCUS_ORDER[1:]) + ['search']
    assert [tab_target(area, backward=True) for area in FOCUS_ORDER] == ['bookmarks'] + list(FOCUS_ORDER[:-1])


@pytest.mark.parametrize('index,step,count,expected', [
    (0, -1, 7, 0), (6, 1, 7, 6), (2, 1, 7, 3),
    (2, -1, 7, 1), (None, 1, 7, 0), (None, -1, 7, 6),
    (0, -1, 0, None),
])
def test_root_button_edges(index, step, count, expected):
    assert root_step(index, step, count) == expected


@pytest.mark.parametrize('depth,expected', [(0, 'files'), (1, 'files'), (2, 'parent'), (4, 'parent')])
def test_middle_left(depth, expected):
    assert middle_back_target(depth) == expected


@pytest.mark.parametrize('panel,folder,expected', [
    ('files', True, 'enter_directory_panel'), ('files', False, 'execute'),
    ('directory', True, 'descend'), ('directory', False, 'execute'),
    ('bookmarks', True, 'cascade'), ('bookmarks', False, 'execute'),
])
def test_right_arrow_is_hierarchical(panel, folder, expected):
    assert row_right_action(panel, folder) == expected


def test_unknown_panel_rejected():
    with pytest.raises(ValueError):
        row_right_action('elsewhere', True)


def test_qt_event_filter_and_view_handoff_wired():
    app = (ROOT / 'src/app.py').read_text(encoding='utf8')
    view = (ROOT / 'src/expanded_view.py').read_text(encoding='utf8')
    ast.parse(app)
    ast.parse(view)
    for snippet in ('expanded_tree_key(', 'expanded_root_key(', 'expanded_tab_key(',
                    'expanded_focus_key(', 'move_tree_selection(',
                    'view.history_back()', 'row_right_action(',
                    'view.focus_panel('):
        assert snippet in app
    for snippet in ('root_buttons', 'navigate_middle(', 'focus_panel(',
                    'Qt.FocusPolicy.StrongFocus', 'enter_row('):
        assert snippet in view
