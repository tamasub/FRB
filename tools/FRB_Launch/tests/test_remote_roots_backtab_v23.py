from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf-8')


def test_root_remote_navigation_uses_logical_selection_not_qt_focus():
    section = SOURCE.split("        if area == 'roots':\n            if not view.root_buttons:", 1)[1].split("        pane = {'files':", 1)[0]
    assert 'self._last_root_id' in section
    assert 'btn.hasFocus()' not in section
    assert "self._last_root_id = view.root_rows[current].get('item_id')" in section


def test_backtab_path_keeps_roots_routing():
    assert "previous_area(area, expanded=expanded) if command == 'BACKTAB'" in SOURCE
    assert "self.remote_focus_area(target)" in SOURCE
