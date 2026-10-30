"""v31: three menu icons with equal near-icon spacing and golden heart."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REMOTE = (ROOT / 'src' / 'launch_remote.py').read_text(encoding='utf-8')


def test_menu_labels_no_trailing_heart_character():
    assert "addAction('現在のフォルダーをお気に入り登録')" in REMOTE
    assert 'お気に入り登録（♥）' not in REMOTE


def test_menu_icon_padding_is_symmetric():
    assert 'QMenu#remoteMoreMenu::icon {{padding-left:6px;padding-right:6px;}}' in REMOTE
    assert 'QMenu#remoteMoreMenu::item {{padding:7px 14px;}}' in REMOTE


def test_menu_heart_is_golden_even_when_breadcrumb_registered():
    # Existing menu action availability continues to use the current directory.
    assert "Qt.AlignmentFlag.AlignCenter," in REMOTE
    assert "                     '💛')" in REMOTE
    assert 'self.more_favorite_action.setIcon(remote_favorite_icon(favorite_heart))' in REMOTE
    assert 'self.more_favorite_action.setEnabled(bool(available))' in REMOTE


def test_source_is_valid():
    ast.parse(REMOTE)
