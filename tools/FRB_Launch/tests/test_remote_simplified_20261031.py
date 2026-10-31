from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from remote_navigation import remote_navigation_order, remote_tab_target


def test_files_two_columns_only():
    assert remote_navigation_order(web=False) == ('files', 'directory')
    assert remote_tab_target('files') == 'directory'
    assert remote_tab_target('directory') == 'files'
    assert remote_tab_target('files', backward=True) == 'directory'


def test_browser_bookmarks_only():
    assert remote_navigation_order(web=True) == ('bookmarks',)
    for current in ('bookmarks', 'search', 'pages', 'web_body:0', 'workspace_browser'):
        assert remote_tab_target(current, web=True) == 'bookmarks'
        assert remote_tab_target(current, web=True, backward=True) == 'bookmarks'


def test_remote_layout_order_and_wheel():
    text = (Path(__file__).resolve().parents[1] / 'src/launch_remote.py').read_text(encoding='utf-8')
    assert text.index("row_bottom = QHBoxLayout()") < text.index("row_mid = QHBoxLayout()") < text.index("row_top = QHBoxLayout()")
    assert "role='workspace', wheel_enabled=True)" in text


def test_browser_button_reopens_bookmarks():
    text = (Path(__file__).resolve().parents[1] / 'src/app.py').read_text(encoding='utf-8')
    assert "view.show_browser_bookmarks()" in text
    assert "self.remote_focus_area('bookmarks')" in text
