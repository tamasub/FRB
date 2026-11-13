"""Single styling gateway for Exp/List Files context menus.

The menu object is FRBContextMenu (including the ぐりぐり Runner) for both
columns. Native QMenu is solely responsible for foreground rendering:
QAction text, icon, selected state, separators and submenu arrows.

IMPORTANT: Do not blank QStyleOptionMenuItem.text or .icon or paint QAction
foreground manually. The 0272 custom painter caused Windows to display a
solid gray menu with only occasional native arrows / the final label.

The stable shared CSS controls background / row padding only. Avoid
per-column icon pixel offsets and transparent-pixmap rescaling. Exact icon
margins still require a successful Windows pixel-render acceptance test.
"""
from launch_appearance import LIGHT_MENU_QSS, context_menu_spacing_qss


def style_context_menu(menu, theme):
    """Apply the same stylesheet to every native-drawn FRBContextMenu."""
    menu._frb_context_style = True
    palette = LIGHT_MENU_QSS if str(theme).casefold() == 'light' else ''
    menu.setStyleSheet(palette + context_menu_spacing_qss(theme))
    return menu
