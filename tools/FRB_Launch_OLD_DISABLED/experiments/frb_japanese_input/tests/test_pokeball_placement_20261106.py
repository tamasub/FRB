"""Geometry and contract checks without Qt/Windows; eye, key grid and focus."""
from __future__ import annotations

import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from kana_guide_layout import place_guide


def intersects(a, b):
    x1,y1,w1,h1 = a
    x2,y2,w2,h2 = b
    return x1 < x2+w2 and x1+w1 > x2 and y1 < y2+h2 and y1+h1 > y2


def test_first_row_guide_hovers_eight_pixels_above_pressed_key():
    screen = (0, 0, 1920, 1080)
    board = (500, 320, 200, 172)
    first_key = (510, 325, 62, 32)
    x, y = place_guide(first_key, board, screen, (108, 108))
    assert (x, y) == (487, 209)
    assert first_key[1] - (y + 108) == 8
    assert not intersects((x, y, 108, 108), first_key)


def test_four_kana_rows_keep_same_gap_while_guide_tracks_each_row():
    board = (500, 320, 200, 172)
    screen = (0, 0, 1920, 1080)
    key_y_values = (325, 365, 405, 445)  # あ / た / ま / わ-like rows
    positions = []
    for key_y in key_y_values:
        key = (570, key_y, 62, 32)
        x, y = place_guide(key, board, screen, (108, 108))
        positions.append((x, y))
        assert key_y - (y + 108) == 8
        assert not intersects((x, y, 108, 108), key)
    assert [p[1] for p in positions] == [209, 249, 289, 329]
    assert positions[-1][1] - positions[0][1] == key_y_values[-1] - key_y_values[0]


def test_guide_follows_key_when_whole_window_moves():
    original_board = (500, 320, 200, 172)
    original_key = (570, 445, 62, 32)
    moved_board = (580, 410, 200, 172)
    moved_key = (650, 535, 62, 32)
    screen = (0, 0, 1920, 1080)
    x1, y1 = place_guide(original_key, original_board, screen, (108, 108))
    x2, y2 = place_guide(moved_key, moved_board, screen, (108, 108))
    assert (x2-x1, y2-y1) == (80, 90)


def test_top_screen_edge_moves_hint_outside_keyboard_not_on_key():
    board = (140,28,200,190)
    key = (150,32,60,32)
    screen = (0,0,400,300)
    x,y = place_guide(key, board, screen, (108,108))
    assert 4 <= x and x+108 <= 396
    assert 4 <= y and y+108 <= 296
    assert not intersects((x,y,108,108),board)


def test_no_side_space_below_fallback_is_visible():
    board=(25,30,150,120)
    key=(30,35,45,28)
    x,y=place_guide(key,board,(0,0,200,400),(108,108))
    assert y == key[1] + key[3] + 8
    assert not intersects((x,y,108,108),key)


def test_guide_is_passive_global_window_with_painter_cleanup():
    source = (ROOT/'frb_japanese_input.py').read_text('utf-8')
    assert 'QPoint, QPointF, QRect, QRectF' in source
    assert 'Qt.WindowType.WindowTransparentForInput' in source
    assert 'Qt.WindowType.WindowDoesNotAcceptFocus' in source
    assert 'Qt.WidgetAttribute.WA_ShowWithoutActivating' in source
    assert 'key.mapToGlobal(QPoint(0, 0))' in source
    assert 'self.keyboard.mapToGlobal(QPoint(0, 0))' in source
    assert 'key.mapTo(self' not in source
    assert 'finally:' in source and 'painter.end()' in source
    assert 'self.guide.move(self._guide_position(key))' in source


def test_release_uses_displayed_eye_choice_not_new_release_hit_test():
    source = (ROOT/'frb_japanese_input.py').read_text('utf-8')
    tree = ast.parse(source)
    key = next(c for c in tree.body if isinstance(c,ast.ClassDef) and c.name == 'FlickKanaKey')
    fn = next(f for f in key.body if isinstance(f,ast.FunctionDef) and f.name=='mouseReleaseEvent')
    segment = ast.get_source_segment(source, fn)
    assert 'direction = self._direction' in segment
    assert 'direction = self._direction_at(event)' not in segment
