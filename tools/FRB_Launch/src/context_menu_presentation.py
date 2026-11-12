"""One geometry/painting contract for every Files Exp/List context QMenu.

A folder context menu can be a regular Qt.Popup QMenu OR the Qt.Tool
CascadeMenu-based RemoteFolderActionsMenu.  Their source and lifecycle differ;
icon space, row padding, palette and hit-target-independent painting must not.

This adapter intentionally accepts an existing QMenu rather than replacing it.
All submenu and filesystem commands retain their original QAction connections.
"""
from launch_appearance import LIGHT_MENU_QSS, context_menu_spacing_qss


ICON_BOX_PX = 24
GLYPH_PX = 18
ICON_INSET_PX = (ICON_BOX_PX - GLYPH_PX) // 2


def _normalize_action_icons(menu):
    """Center native file icons and FRB pictograms on the same 24px canvas.

    Windows QFileIconProvider can return 16px glyphs while local hand-painted
    icons provide 24px pixmaps.  Margins alone do not unify their visible
    footprints.  Normalize once, retaining the original image/shape/colors.
    """
    try:
        from PySide6.QtCore import QSize, Qt
        from PySide6.QtGui import QIcon, QPainter, QPixmap
    except ImportError:  # Static/unit contract tests also run without Qt.
        return
    for action in menu.actions():
        if action.isSeparator():
            continue
        if not bool(action.property('frbContextIconNormalized')):
            icon = action.icon()
            if not icon.isNull():
                source = icon.pixmap(QSize(GLYPH_PX, GLYPH_PX))
                if not source.isNull():
                    canvas = QPixmap(ICON_BOX_PX, ICON_BOX_PX)
                    canvas.fill(Qt.GlobalColor.transparent)
                    painter = QPainter(canvas)
                    painter.drawPixmap(ICON_INSET_PX, ICON_INSET_PX, source)
                    painter.end()
                    action.setIcon(QIcon(canvas))
                    action.setProperty('frbContextIconNormalized', True)
        # An already populated submenu uses the same geometry, even if its
        # owner opened it with hover rather than a separate right click.
        submenu = action.menu()
        if submenu is not None:
            _normalize_action_icons(submenu)


def style_context_menu(menu, theme, *, extra_qss=''):
    """Install one palette/spacing/icon contract; no Remote/display branching.

    Call only on context popups, not on independent Page cascade columns or
    Settings menus. When an already-built submenu is opened, Qt inherits the
    same style from the owning menu; normalization covers its actions too.
    """
    palette = LIGHT_MENU_QSS if str(theme).casefold() == 'light' else ''
    menu.setStyleSheet(palette + context_menu_spacing_qss(theme) + extra_qss)
    _normalize_action_icons(menu)
    return menu
