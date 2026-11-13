"""Geometry rules for FRB Launch's cascading popups.

Qt coordinates are logical pixels.  Screen.availableGeometry() excludes the
Windows taskbar; the additional inset prevents the menu touching its edge.
"""

from dataclasses import dataclass

MENU_SCREEN_MARGIN = 12
MENU_MIN_SCROLL_HEIGHT = 160


@dataclass(frozen=True)
class PopupPlacement:
    x: int
    y: int
    height: int
    scroll: bool


def place_popup(anchor_x, anchor_y, width, requested_height, left, top, right, bottom,
                margin=MENU_SCREEN_MARGIN):
    """Place a popup inside [left, right) x [top, bottom), never over taskbar."""
    usable_left, usable_right = left + margin, max(left + margin + 1, right - margin)
    usable_top, usable_bottom = top + margin, max(top + margin + 1, bottom - margin)
    usable_height = usable_bottom - usable_top
    displayed_height = max(1, min(int(requested_height), usable_height))
    x = max(usable_left, min(int(anchor_x), usable_right - min(int(width), usable_right - usable_left)))
    y = max(usable_top, min(int(anchor_y), usable_bottom - displayed_height))
    return PopupPlacement(x, y, displayed_height, requested_height > usable_height)


def main_cascade_anchor_x(viewport_width, second_column_x=None, *, main_columns=False):
    """First cascade's viewport-local x coordinate.

    In the two-column main Page list, start at the *actual* editable column
    boundary, so a folder menu overlays the description column rather than
    opening beyond the outer window. Other list modes keep their old anchor.
    A missing/invalid divider falls back to the viewport's right edge.
    """
    right = max(0, int(viewport_width) - 1)
    if main_columns and second_column_x is not None:
        divider = int(second_column_x)
        if 0 < divider < right:
            return divider - 1
    return right
