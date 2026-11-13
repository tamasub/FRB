"""v30: Remote ... menu gets real leading icons from Launch controls.

Source/AST contract checks do not depend on a Windows Qt runtime. Visual
rendering and QMenu popup still need a manual smoke test on Windows.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
REMOTE = (ROOT / 'src' / 'launch_remote.py').read_text(encoding='utf-8')


def test_menu_actions_have_launch_native_icons():
    assert "self.more_settings_action.setIcon(settings_icon)" in REMOTE
    assert "self.more_category_action.setIcon(category_icon)" in REMOTE
    assert "self.more_favorite_action.setIcon(remote_favorite_icon(favorite_heart))" in REMOTE
    assert "launcher.theme_button.icon()" in REMOTE
    assert "launcher.history_category_action.icon()" in REMOTE
    assert "launcher.expanded_view.favorite_save.text()" in REMOTE


def test_icons_resync_from_actual_widgets_every_menu_open():
    assert "remote.update_more_menu_icons(self.theme_button.icon()," in APP
    assert "self.history_category_action.icon()," in APP
    assert "view.favorite_save.text())" in APP
    assert "remote.set_favorite_action_available(available)" in APP


def test_heart_uses_breadcrumb_yellow_heart_not_folder():
    # v31: Keep Remote's leading heart warm yellow-orange even when registered.
    assert "                     '💛')" in REMOTE
    assert "QFont('Segoe UI Emoji', 13)" in REMOTE
    assert 'SP_DirHomeIcon' not in REMOTE
    assert "self.more_favorite_action.triggered.connect(" in REMOTE
    assert "self.more_settings_action.triggered.connect(" in REMOTE
    assert "self.more_category_action.triggered.connect(" in REMOTE


def test_all_modified_source_is_valid_python():
    ast.parse(APP)
    ast.parse(REMOTE)
