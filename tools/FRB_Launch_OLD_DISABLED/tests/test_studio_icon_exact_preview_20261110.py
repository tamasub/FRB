"""Protect Studio icon selection from silently becoming a different icon in Launch.

Pure-Python tests: these check dispatch and drawing commands.  Actual colour
emoji glyph rendering still needs a Windows 11 + PySide6 GUI confirmation.
"""
import ast
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from launch_icon_palette import (STUDIO_EMOJI_ICONS, FOLDER_ICON_COLORS,
                                 studio_icon_emoji, folder_icon_color)


# What Studio currently previews in the icon combo.  Test the *actual glyphs*,
# not merely the count of enum choices, so a visual mismatch is caught.
STUDIO_PREVIEW = {
    'file': '📄', 'command': '▶️', 'calendar': '📅', 'mail': '✉️',
    'wifi': '📶', 'volume': '🔊', 'archive': '🗜️', 'globe': '🌐',
    'settings': '⚙️', 'message': '💬', 'app': '🖥️',
}


def test_emoji_catalog_matches_studio_choice_preview_exactly():
    assert STUDIO_EMOJI_ICONS == STUDIO_PREVIEW
    assert {k: studio_icon_emoji(k) for k in STUDIO_PREVIEW} == STUDIO_PREVIEW
    assert folder_icon_color('category.blue') == '#6ba7ff'
    assert folder_icon_color('folder.yellow') == '#e9bb61'
    assert FOLDER_ICON_COLORS['category'] == FOLDER_ICON_COLORS['category.blue']
    assert FOLDER_ICON_COLORS['folder'] == FOLDER_ICON_COLORS['folder.yellow']


def _isolated_renderer():
    """Execute the actual ``app.icon()`` source with a harmless Qt recorder."""
    source = (ROOT / 'src' / 'app.py').read_text('utf-8')
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'icon')
    module = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(module)

    class Pixmap:
        def __init__(self, *size):
            self.size = size
            self.emoji = None
            self.paint_calls = []
        def setDevicePixelRatio(self, ratio):
            self.ratio = ratio
        def fill(self, value):
            pass
        def rect(self):
            return 'pixrect'

    class Painter:
        def __init__(self, pix):
            self.pix = pix
        def setRenderHint(self, *args):
            pass
        def setFont(self, font):
            self.pix.font = font
        def drawText(self, rect, align, value):
            self.pix.emoji = value
        def setPen(self, value):
            pass
        def setBrush(self, value):
            self.pix.brush = value
        def drawRoundedRect(self, *args):
            self.pix.paint_calls.append(('folder_or_tile', args))
        def end(self):
            pass

    ctx = {'studio_icon_emoji': studio_icon_emoji,
           'folder_icon_color': folder_icon_color,
           'QPixmap': Pixmap, 'QPainter': Painter,
           'QFont': lambda *args: args,
           'QRect': lambda *args: args,
           'QColor': lambda value: value,
           'QIcon': lambda pix: pix,
           'Qt': SimpleNamespace(GlobalColor=SimpleNamespace(transparent=None),
                                 PenStyle=SimpleNamespace(NoPen=0),
                                 AlignmentFlag=SimpleNamespace(AlignCenter=0)),
           }
    # The stub Qt painter has the same named attribute used by the code.
    ctx['QPainter'].RenderHint = SimpleNamespace(Antialiasing=True)
    exec(compile(module, '<app.icon>', 'exec'), ctx)
    return ctx['icon']


def test_every_studio_emoji_choice_draws_its_exact_preview():
    render = _isolated_renderer()
    for key, expected in STUDIO_PREVIEW.items():
        icon = render(key)
        assert icon.emoji == expected, (key, icon.emoji, expected)
        assert icon.size == (48, 48)
        assert icon.ratio == 2
        assert icon.font[0] == 'Segoe UI Emoji'


def test_folder_variants_are_still_blue_and_yellow_not_emoji_tiles():
    render = _isolated_renderer()
    assert render('category.blue').brush == '#6ba7ff'
    assert render('folder.yellow').brush == '#e9bb61'


def test_affected_json_root_uses_the_same_archive_key():
    data = json.loads((ROOT / 'config' / 'frb_launch_data.json').read_text('utf-8'))
    row = next(row for row in data['items'] if row['title'] == 'FRB Launch Logフォルダー')
    assert row['item_kind'] == 'directory'
    assert row['icon_key'] == 'archive'
    assert _isolated_renderer()(row['icon_key']).emoji == '🗜️'


def test_files_exp_uses_the_canonical_row_icon_without_replacing_it():
    exp_source = (ROOT / 'src' / 'remote_files_explorer.py').read_text('utf-8')
    assert "source.get('icon_key', 'folder.yellow')" in exp_source
    assert "launcher.row_icon({'icon_key': icon_key})" in exp_source
    assert "self._launcher.row_icon({'icon_key': configured})" in exp_source
    assert 'configured_icon=selected_icon' in exp_source
