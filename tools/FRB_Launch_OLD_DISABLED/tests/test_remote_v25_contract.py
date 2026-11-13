"""Contract tests for FRB Remote v25."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from remote_navigation import next_area, previous_area
from expanded_keyboard_model import tab_target
from focus_session import normalize_focus_state

SRC = Path(__file__).resolve().parents[1] / 'src'

def test_breadcrumb_in_both_tab_rings():
    assert next_area('roots') == 'breadcrumb'
    assert next_area('breadcrumb') == 'files'
    assert previous_area('files') == 'breadcrumb'
    assert tab_target('roots') == 'breadcrumb'
    assert tab_target('files', backward=True) == 'breadcrumb'
    assert normalize_focus_state({'area':'breadcrumb'})['area'] == 'breadcrumb'

def test_home_routes_to_files_first():
    s = (SRC/'app.py').read_text()
    assert 'if self.expanded_view.isVisible():\n            view = self.expanded_view\n            first = view.left.tree.topLevelItem(0)' in s
    assert "self.remote_focus_area('files' if expanded else 'list')" in s

def test_header_repair_and_double_click_band():
    s=(SRC/'app.py').read_text()
    assert 'windows.set_window_topmost(hwnd, True)' in s
    assert 'windows.set_window_topmost(hwnd, False)' in s
    assert "if command == 'FOLDER_UP':" in s
    assert 'self.expanded_view.go_up()' in s
    r=(SRC/'launch_remote.py').read_text()
    assert 'class UpDoubleClickBand' in r
    assert "self.command.emit('FOLDER_UP')" in r
