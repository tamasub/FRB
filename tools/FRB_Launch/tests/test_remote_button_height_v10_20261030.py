"""Remote v0.10 visual build marker and equal-height action buttons.
This static contract runs without a Qt runtime. Windows GUI test remains necessary.
"""
from pathlib import Path

REMOTE = (Path(__file__).resolve().parents[1] / 'src' / 'launch_remote.py').read_text(encoding='utf-8')


def test_60px_top_bottom_buttons_and_version_marker():
    for cmd, width in [('BACKTAB', 76), ('TAB', 76), ('SEARCH_HISTORY', 84), ('FOLDER_HISTORY', 84)]:
        assert f"'{cmd}', width={width}, height=60" in REMOTE
    assert "FRB Remote v0.11" in REMOTE
    assert 'self.setMinimumHeight(root.sizeHint().height())' in REMOTE
    assert 'min-height:0' not in REMOTE  # Qt QSS overrides layout minimum height


def test_unchanged_wheel_focus_and_mouse_controls():
    assert 'self.setFixedSize(56, 46)' in REMOTE
    assert "self.command.emit('CLICK')" in REMOTE
    assert "self.command.emit('DOUBLE_CLICK')" in REMOTE
