"""Contracts for desktop-triggered grid alignment, with no GUI dependency."""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from remote_grid_alignment import files_grid_layout, remote_next_to_exp


def method_source(filename, cls, method):
    source = (ROOT / 'src' / filename).read_text(encoding='utf-8')
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
    func = next(n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == method)
    return ast.get_source_segment(source, func)


def test_matches_reference_screenshot_geometry():
    # Launch starts at x475; Files list header y177; Launch bottom y888.
    remote_x, remote_y, exp_x, exp_y, height = files_grid_layout(
        475, 1720, 177, 888, 181, 260, 0, 1920, 0, 1080)
    assert (remote_x, remote_y, exp_x, exp_y, height) == (28, 177, 212, 177, 711)
    assert exp_x + 260 + 3 == 475
    assert exp_y + height == 888


def test_respects_new_launch_position_on_each_call():
    first = files_grid_layout(750, 1500, 250, 925, 180, 270, 0, 1920, 0, 1080)
    second = files_grid_layout(780, 1530, 300, 985, 180, 270, 0, 1920, 0, 1080)
    assert first[:4] == (294, 250, 477, 250)
    assert second[:4] == (324, 300, 507, 300)
    assert first[4] == 675 and second[4] == 685


def test_right_side_fallback_if_launch_touches_screen_left():
    rx, ry, ex, ey, h = files_grid_layout(
        0, 800, 180, 900, 180, 250, 0, 1920, 0, 1080)
    assert rx == 803 and ex == 986
    assert ry == ey == 180 and h == 720


def test_no_room_keeps_pair_on_screen_and_clamps_height():
    rx, ry, ex, ey, h = files_grid_layout(
        380, 1500, 1020, 1200, 180, 260, 0, 1920, 0, 1080)
    assert 0 <= rx and ex + 260 <= 1920
    assert ry == ey and ey + h <= 1080
    assert h >= 180


def test_manual_exp_position_never_forces_remote_off_screen():
    assert remote_next_to_exp(400, 200, 300, 180, 0, 1920, 0, 1080, 300) == (217, 200)
    assert remote_next_to_exp(10, 200, 300, 180, 0, 1920, 0, 1080, 300) == (313, 200)


def test_alignment_limited_to_summoned_visible_files_workspace():
    entry = method_source('app.py', 'Launcher', 'show_remote_at')
    assert 'self.files_root_hidden_mode and not web' in entry
    assert 'self.remote_window.align_with_files_grid()' in entry
    assert 'QTimer.singleShot(0, self.remote_window.align_with_files_grid)' in entry
    align = method_source('launch_remote.py', 'LaunchRemote', 'align_with_files_grid')
    assert "view._workspace_mode != 'files'" in align
    assert 'view.middle.tree.header()' in align
    assert 'header.mapToGlobal' in align
    assert 'launcher.frameGeometry()' in align


def test_restored_position_and_height_survive_automatic_placement():
    exp = (ROOT / 'src/remote_files_explorer.py').read_text(encoding='utf-8')
    assert "'remote_files_exp/manual_position'" in exp
    assert "'remote_files_exp/manual_height'" in exp
    place = method_source('remote_files_explorer.py', 'RemoteFilesExplorer', 'place_automatically')
    assert 'self._automatic_placement = True' in place
    assert 'self._automatic_placement = False' in place
    save = method_source('remote_files_explorer.py', 'RemoteFilesExplorer', '_save_size')
    assert "getattr(self, '_grid_height_mode', False)" in save
    reset = method_source('remote_files_explorer.py', 'RemoteFilesExplorer', 'reset_grid_layout')
    assert 'self._manual_position = False' in reset
    assert 'self._manual_height = False' in reset


def test_mode_off_restores_legacy_height_and_following():
    toggle = method_source('app.py', 'Launcher', 'set_files_root_hidden_mode')
    assert 'remote.leave_files_grid_alignment()' in toggle
    restore = method_source('launch_remote.py', 'LaunchRemote', 'leave_files_grid_alignment')
    assert "'remote_files_exp/height'" in restore
    assert 'self.position_files_exp()' in restore
