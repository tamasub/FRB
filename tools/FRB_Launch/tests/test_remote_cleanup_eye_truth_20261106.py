"""November 6: retire four Remote buttons and make the shuriken eye authoritative.

All tests run without an installed Qt GUI. Real OS behavior requires a Windows check.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

import pytest

from test_shuriken_confirm_click_and_paint_20261105 import (
    load_button_module, make_button, DummyEvent,
)
from shuriken_model import ShurikenEntry

ROOT = Path(__file__).resolve().parents[1]
REMOTE = (ROOT / 'src' / 'launch_remote.py').read_text('utf-8')
APP = (ROOT / 'src' / 'app.py').read_text('utf-8')
SHURIKEN = (ROOT / 'src' / 'remote_shuriken.py').read_text('utf-8')


def test_four_dead_buttons_really_removed_from_remote_layout():
    """Remove the actual widget constructors, not just hide their labels."""
    remote_cls = next(n for n in ast.parse(REMOTE).body
                      if isinstance(n, ast.ClassDef) and n.name == 'LaunchRemote')
    ctor = next(n for n in remote_cls.body
                if isinstance(n, ast.FunctionDef) and n.name == '__init__')
    src = ast.get_source_segment(REMOTE, ctor)
    for attribute in ('files_exp_button', 'files_list_button',
                      'left_button', 'right_button'):
        assert 'self.' + attribute not in src
    for command in ("'REMOTE_TARGET_EXP', width=85", "'REMOTE_TARGET_LIST', width=85",
                    "'LEFT', width=50", "'RIGHT', width=50"):
        assert command not in src
    assert 'root.addWidget(self.pad, 0, Qt.AlignmentFlag.AlignHCenter)' in src
    assert 'self.browser_button = self._button(' in src
    assert 'row_quick.addWidget(self.shuriken_button)' in src
    assert 'row_quick.addWidget(self.home_button)' in src
    assert 'row_quick.addWidget(self.kana_button)' in src
    assert 'root.addWidget(self.scroll_pad, 0, Qt.AlignmentFlag.AlignHCenter)' in src


def test_both_files_targets_are_still_reachable_from_grigri_even_in_browser():
    assert "ShurikenEntry('REMOTE_TARGET_EXP', 'Exp列', 0, 'left', 0)" in REMOTE
    assert "ShurikenEntry('REMOTE_TARGET_LIST', 'List列', 0, 'right', 1)" in REMOTE
    assert "launcher.expanded_view._workspace_mode in ('files', 'browser')" in REMOTE
    assert "if command in ('REMOTE_TARGET_EXP', 'REMOTE_TARGET_LIST'):" in APP
    assert "view.show_files_view()" in APP


def test_removed_button_dependencies_retarget_to_pad():
    assert 'QCursor.setPos(self.pad.mapToGlobal(self.pad.rect().center()))' in REMOTE
    assert "getattr(remote, 'pad', None)" in APP
    assert 'for name, widget in ((\'CLICK\', getattr(remote, \'pad\', None)),):' in (
        ROOT / 'src' / 'remote_context_wheel.py').read_text('utf-8')
    # Source references to removed buttons must not appear in active methods.
    assert 'self.files_exp_button.mapToGlobal' not in REMOTE
    assert 'self.files_list_button' not in REMOTE


def test_shuriken_eye_selected_with_15_pixels_commits_on_slow_release():
    mod = load_button_module()
    mod.ShurikenPreview = type('Preview', (), {
        '__init__': lambda self, *a: setattr(self, 'present', Mock()),
        'hide': lambda self: None,
    })
    button, launcher = make_button(mod)
    button.mousePressEvent(DummyEvent())
    assert button._selected_entry is None
    button.mouseMoveEvent(DummyEvent(global_y=85))  # 15px UP, < old release 27px.
    assert button._selected_entry.item_id == 'zip'
    painted = button._preview.present.call_args.args[2]
    assert painted is button._selected_entry
    button.mouseReleaseEvent(DummyEvent(global_y=85))
    button.triggered.emit.assert_called_once_with('zip')
    assert button._selected_entry is None


def test_shuriken_eye_back_at_origin_cancels_and_stale_release_does_nothing():
    mod = load_button_module()
    mod.ShurikenPreview = type('Preview', (), {
        '__init__': lambda self, *a: setattr(self, 'present', Mock()),
        'hide': lambda self: None,
    })
    button, _ = make_button(mod)
    button.mousePressEvent(DummyEvent())
    button.mouseMoveEvent(DummyEvent(global_y=50))  # up eye
    assert button._selected_entry.item_id == 'zip'
    button.mouseMoveEvent(DummyEvent())  # eye returns to the center
    assert button._selected_entry is None
    assert button._preview.present.call_args.args[2] is None
    button.mouseReleaseEvent(DummyEvent(global_y=50))  # stale release location
    button.triggered.emit.assert_not_called()


def test_release_without_painted_selection_never_guesses_action():
    mod = load_button_module()
    mod.ShurikenPreview = type('Preview', (), {
        '__init__': lambda self, *a: setattr(self, 'present', Mock()),
        'hide': lambda self: None,
    })
    button, _ = make_button(mod)
    button.mousePressEvent(DummyEvent())
    button.mouseReleaseEvent(DummyEvent(global_y=20))  # no move event, no eye
    button.triggered.emit.assert_not_called()


def test_four_way_eye_action_direction_matches_release_without_rehittest():
    mod = load_button_module()
    mod.ShurikenPreview = type('Preview', (), {
        '__init__': lambda self, *a: setattr(self, 'present', Mock()),
        'hide': lambda self: None,
    })
    button, launcher = make_button(mod)
    entries = [ShurikenEntry(f'item-{d}', d, 1, d, i)
               for i, d in enumerate(('up', 'right', 'down', 'left'))]
    launcher.shuriken_items = Mock(return_value=entries)
    button.mousePressEvent(DummyEvent())
    button.mouseMoveEvent(DummyEvent(global_x=116, global_y=100))
    assert button._selected_entry.item_id == 'item-right'
    assert button._preview.present.call_args.args[2] == button._selected_entry
    button.mouseReleaseEvent(DummyEvent(global_x=160, global_y=100))
    button.triggered.emit.assert_called_once_with('item-right')
