"""No-PySide6 tests for the independent Shuriken Scroll experiment.

These contracts explicitly protect: Files List only, view-only scroll,
rapid flicks, and legacy WheelPad/confirmation behavior.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
from shuriken_scroll_model import (DEADZONE_PX, TICK_MS,
                                   pixels_per_tick, release_impulse)


def source(name):
    return (ROOT / name).read_text(encoding='utf-8')


def test_click_does_not_scroll():
    for value in (-11, -1, 0, 1, 11):
        assert pixels_per_tick(value) == 0
        assert release_impulse(value, 0) == 0
    assert DEADZONE_PX == 12


def test_up_drag_moves_content_up_and_down_drag_reverses():
    assert pixels_per_tick(-15) > 0
    assert pixels_per_tick(+15) < 0
    assert pixels_per_tick(-60) == -pixels_per_tick(+60)
    assert pixels_per_tick(-80) > pixels_per_tick(-20)
    assert TICK_MS == 40


def test_short_flick_before_first_timer_tick_still_moves():
    assert release_impulse(-20, 0) > 0
    assert release_impulse(20, 0) < 0
    assert release_impulse(-500, 0) == 460
    assert release_impulse(500, 0) == -460
    assert release_impulse(-60, 1) == 0  # no release inertia


def test_quick_scroll_rate_clamped_for_compact_one_and_half_column_goal():
    assert pixels_per_tick(-90) == pixels_per_tick(-2000)
    assert pixels_per_tick(90) == pixels_per_tick(2000)


def test_placement_is_exactly_below_original_68_x_46_pad():
    remote = source('src/launch_remote.py')
    button = source('src/remote_shuriken_scroll.py')
    assert "self.setFixedSize(68, 46)" in button
    assert "self.scroll_pad = ShurikenScrollPad(self)" in remote
    assert remote.index('root.addLayout(row_mid)') < remote.index('root.addWidget(self.scroll_pad') < remote.index('self.up_band = UpDoubleClickBand(self)')
    assert 'Qt.AlignmentFlag.AlignHCenter' in remote
    assert "self.scroll_pad.scroll_requested.connect(launcher.remote_scroll_files_list)" in remote


def test_mouse_press_held_timer_release_and_hide():
    source_text = source('src/remote_shuriken_scroll.py')
    assert 'self._timer.start()' in source_text
    assert 'self._timer.timeout.connect(self._scroll_tick)' in source_text
    assert 'pixels_per_tick(self._dy)' in source_text
    assert 'release_impulse(dy, self._ticks_emitted)' in source_text
    assert 'self._timer.stop()' in source_text
    assert 'def hideEvent' in source_text and 'self._stop()' in source_text
    assert 'Qt.FocusPolicy.NoFocus' in source_text


def test_scroll_applies_only_to_files_list_scrollbar_and_never_selects_row():
    app = source('src/app.py')
    method = app.split('    def remote_scroll_files_list(self, pixels):', 1)[1].split('\n    def shuriken_items', 1)[0]
    assert "view._workspace_mode != 'files'" in method
    assert "getattr(self, '_remote_area', None) != 'directory'" in method
    assert 'tree = view.middle.tree' in method
    assert 'bar = tree.verticalScrollBar()' in method
    assert 'bar.setValue(' in method
    assert 'tree.setCurrentItem' not in method
    assert 'tree.setFocus' not in method
    assert 'QKeyEvent' not in method
    assert "QAbstractItemView.State.EditingState" in method


def test_confirmation_modal_and_active_context_menu_are_safe():
    app = source('src/app.py').split('    def remote_scroll_files_list(self, pixels):', 1)[1].split('\n    def shuriken_items', 1)[0]
    for name in ('_remote_text_dialog', '_remote_confirmation', '_remote_context_wheel'):
        assert name in app
    assert 'menu_wheel.active' in app  # stale, stopped adapter must not block


def test_existing_shuriken_and_kana_not_modified():
    remote = source('src/launch_remote.py')
    assert 'self.pad = WheelPad(self, compact=True)' in remote
    assert 'self.shuriken_button = ShurikenButton(launcher, self, hand_index=1)' in remote
    assert 'self.kana_button = self._button' in remote


def test_app_scroll_handler_changes_only_scrollbar_not_selection_with_fake_tree():
    """Execute the actual handler unbound using a tiny Qt-free fake context."""
    import ast
    from types import SimpleNamespace

    module = ast.parse(source('src/app.py'))
    handler = next(n for cls in module.body if isinstance(cls, ast.ClassDef)
                   for n in cls.body if isinstance(n, ast.FunctionDef)
                   and n.name == 'remote_scroll_files_list')
    wrapper = ast.Module(body=[handler], type_ignores=[])
    ast.fix_missing_locations(wrapper)
    class EditState:
        EditingState = 9
    stub_qabstract = SimpleNamespace(State=EditState)
    namespace = {'QAbstractItemView': stub_qabstract}
    exec(compile(wrapper, '<isolated_remote_scroll_files_list>', 'exec'), namespace)
    invoke = namespace['remote_scroll_files_list']

    class Bar:
        def __init__(self):
            self.position = 100
        def value(self): return self.position
        def minimum(self): return 0
        def maximum(self): return 1000
        def setValue(self, val): self.position = val
    class Tree:
        def __init__(self):
            self.bar = Bar()
            self.selected = ['test-file.md']
        def isVisible(self): return True
        def state(self): return 0
        def verticalScrollBar(self): return self.bar
    tree = Tree()
    view = SimpleNamespace(isVisible=lambda: True, _workspace_mode='files',
                           middle=SimpleNamespace(tree=tree))
    launch = SimpleNamespace(isVisible=lambda: True, isMinimized=lambda: False,
                             _remote_area='directory', expanded_view=view)

    invoke(launch, 40)
    assert tree.bar.value() == 140
    assert tree.selected == ['test-file.md']
    invoke(launch, -9999)
    assert tree.bar.value() == 0  # scrollbar clamped
    invoke(launch, 9999)
    assert tree.bar.value() == 1000
    assert tree.selected == ['test-file.md']

    launch._remote_area = 'files_exp'
    invoke(launch, -100)
    assert tree.bar.value() == 1000  # wrong logical target stays untouched
    launch._remote_area = 'directory'
    view._workspace_mode = 'browser'
    invoke(launch, -100)
    assert tree.bar.value() == 1000
    view._workspace_mode = 'files'
    launch._remote_confirmation = object()
    invoke(launch, -100)
    assert tree.bar.value() == 1000


def test_cancel_or_hide_never_synthesizes_an_event_into_other_app():
    text = source('src/remote_shuriken_scroll.py')
    assert 'QApplication.mouseButtons()' in text
    assert 'def _stop(self):' in text
    assert 'self._stop()' in text
    assert 'QCursor.setPos(' not in text
    assert 'SendInput' not in text
    assert 'QKeyEvent' not in text
