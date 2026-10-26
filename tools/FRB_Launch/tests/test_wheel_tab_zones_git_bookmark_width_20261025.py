"""Experience navigation contracts independent of Windows/PySide6.

The complete smoke test is on Windows; these assert the production routes,
safety invariants and opt-in popup width without trying to simulate Qt itself.
"""
from pathlib import Path
import ast

SRC = Path(__file__).resolve().parents[1] / 'src'
VIEW = (SRC / 'expanded_view.py').read_text(encoding='utf8')
APP = (SRC / 'app.py').read_text(encoding='utf8')
TABS = (SRC / 'page_tab_focus.py').read_text(encoding='utf8')


def method_source(source, class_name, method_name):
    module = ast.parse(source)
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method_name)
    return ast.get_source_segment(source, method)


def test_horizontal_page_and_root_boundaries():
    tab = method_source(TABS, 'FocusPageTabBar', 'wheelEvent')
    root = method_source(VIEW, 'ExpandedLauncherView', 'wheel_first_level')
    assert "controller.feed('pages-right'" not in tab
    assert "_zone_right_jump" not in tab
    assert "'roots-left', at_left, steps" in root
    assert "'roots-right', at_right, steps" in root
    assert "self.zone_jump('pages', position='current')" in root
    assert "self.zone_jump('files')" in root
    assert "'roots':" in method_source(VIEW, 'ExpandedLauncherView', 'zone_jump')
    # Page tabs remain terminal even at the right edge.
    assert "jump_from_last_page" not in VIEW
    assert "_zone_right_jump" not in APP
    assert '_zone_enabled' in APP and '_zone_enabled' in TABS


def test_all_three_column_lower_boundaries():
    for name, mark, destination in (
        ('wheel_files_at_edge', 'files-last', 'directory'),
        ('wheel_middle_at_edge', 'directory-last', 'bookmarks'),
        ('wheel_bookmarks_at_edge', 'bookmarks-last', 'pages'),
    ):
        code = method_source(VIEW, 'ExpandedLauncherView', name)
        assert f"self.wheel_zone_navigation.feed('{mark}'" in code
        if name == 'wheel_bookmarks_at_edge':
            # The group headings are display-only: the last selectable bookmark
            # is the WAN boundary, not the last QTreeWidgetItem.
            assert 'index == indices[-1] and movement > 0' in code
        else:
            assert 'index == tree.topLevelItemCount() - 1 and movement > 0' in code
        assert f"self.zone_jump('{destination}')" in code
        assert 'scroll_before != scroll_after' in code
    warp = method_source(VIEW, 'ExpandedLauncherView', '_finish_zone_jump')
    assert 'QApplication.mouseButtons()' in warp
    assert 'QCursor.pos() != source' in warp
    assert 'QCursor.setPos(destination)' in warp
    assert 'activate_row' not in warp and 'self.launcher.execute' not in warp


def test_shared_cooldown_and_no_legacy_layout_behavior_change():
    event = method_source(VIEW, 'ExpandedLauncherView', 'eventFilter')
    assert 'self.wheel_zone_navigation.wheel_is_locked()' in event
    assert 'return True  # Ignore momentum' in event
    tabs = method_source(TABS, 'FocusPageTabBar', 'wheelEvent')
    assert 'controller.wheel_is_locked()' in tabs
    assert 'super().wheelEvent(event)' in tabs


def test_git_text_field_doubled_and_bookmark_popup_only():
    commit = method_source(APP, 'Launcher', 'git_commit_using_filename')
    assert 'dialog.setMinimumWidth(680)' in commit
    assert 'message_editor.setText(Path(zip_path).name)' in commit
    assert 'message_editor.setMinimumWidth(510)' in commit
    open_cascade = method_source(APP, 'Launcher', 'open_expanded_cascade')
    assert 'widget is view.right.tree' in open_cascade
    assert 'bookmark_compact_width = True' in open_cascade
    assert 'round(CASCADE_MAX_WIDTH * 0.7)' in open_cascade
    fill = method_source(APP, 'Launcher', 'fill_cascade')
    assert "getattr(m, 'bookmark_compact_width', False)" in fill
    assert 'self.fill_cascade(m.child,r)' in fill
    assert 'Qt.TextElideMode.ElideRight' in fill
