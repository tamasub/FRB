"""Nine authored folder colours must retain exact Studio->Launch fidelity."""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from launch_icon_palette import FOLDER_COLORS, FOLDER_ICON_COLORS, folder_icon_color

EXPECTED = {
    'yellow': '#e9bb61', 'blue': '#599de5', 'green': '#57ad82',
    'red': '#e47575', 'purple': '#a388df', 'orange': '#e99a5f',
    'cyan': '#57baca', 'pink': '#e78cbe', 'gray': '#9aa3ad',
}


def test_exactly_nine_user_selectable_folder_colors():
    assert FOLDER_COLORS == EXPECTED
    assert len(FOLDER_COLORS) == 9
    for color, rgb in EXPECTED.items():
        assert folder_icon_color('folder.' + color) == rgb
        assert FOLDER_ICON_COLORS['folder.' + color] == rgb


def test_category_variants_and_legacy_keys_do_not_change_appearance():
    assert folder_icon_color('category.blue') == '#6ba7ff'
    assert folder_icon_color('category') == '#6ba7ff'
    assert folder_icon_color('folder') == '#e9bb61'
    for color in EXPECTED:
        if color != 'blue':
            assert folder_icon_color('category.' + color) == EXPECTED[color]
    assert folder_icon_color('folder.invalid') == '#e9bb61'
    assert folder_icon_color('category.invalid') == '#6ba7ff'
    assert folder_icon_color('archive') is None


def test_launch_folder_icon_renderer_uses_palette_for_every_color():
    # Real app.icon() is shared by Files Exp, Files List, and launcher rows.
    code = (ROOT / 'src/app.py').read_text('utf-8')
    tree = ast.parse(code)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                and n.name == 'icon')
    body = ast.get_source_segment(code, node)
    assert 'folder_icon_color(kind)' in body
    assert 'painter.setBrush(QColor(color or' in body
    assert 'painter.drawRoundedRect' in body
    exp_code = (ROOT / 'src/remote_files_explorer.py').read_text('utf-8')
    assert "self._launcher.row_icon({'icon_key': configured})" in exp_code
    assert "launcher.row_icon({'icon_key': icon_key})" in exp_code


def test_old_icon_fidelity_still_passes():
    from launch_icon_palette import studio_icon_emoji
    assert studio_icon_emoji('archive') == '🗜️'
    assert studio_icon_emoji('mail') == '✉️'
