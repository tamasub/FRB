"""Compact browser-style toolbar icons for FRB Launch.

Icons are vector paths painted at 2x resolution for sharp Windows/HiDPI
rendering.  Enabled/disabled and light/dark appearances are explicit, rather
than platform-dependent Unicode arrow/house glyphs.
"""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QIcon, QColor, QPainter, QPainterPath, QPen, QPixmap


_ICON_SIDE = 24
_ICON_SCALE = 2


def _draw_icon(name: str, color: str) -> QPixmap:
    pixmap = QPixmap(_ICON_SIDE * _ICON_SCALE, _ICON_SIDE * _ICON_SCALE)
    pixmap.setDevicePixelRatio(_ICON_SCALE)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    pen = QPen(QColor(color))
    pen.setWidthF(1.0 if name == 'home' else 1.6 if name == 'close' else 2.0)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    shape = QPainterPath()
    if name in ('back', 'back_arrow', 'forward'):
        if name == 'back':
            # Breadcrumb toolbar: the requested upward corner arrow.
            # One upright shaft turning RIGHT at the bottom (not a house).
            # The prior left-pointing arrow remains available as back_arrow.
            shape.moveTo(4.5, 10.0)
            shape.lineTo(11.5, 4.5)
            shape.lineTo(18.5, 10.0)
            shape.moveTo(11.5, 4.5)
            shape.lineTo(11.5, 19.0)
            shape.lineTo(20.0, 19.0)
        elif name == 'back_arrow':
            # Original left arrow preserved for future use, unchanged.
            shape.moveTo(20, 12)
            shape.lineTo(4.5, 12)
            shape.moveTo(11, 5.5)
            shape.lineTo(4.5, 12)
            shape.lineTo(11, 18.5)
        else:
            # Forward remains a simple open arrow.
            shape.moveTo(4, 12)
            shape.lineTo(19.5, 12)
            shape.moveTo(13, 5.5)
            shape.lineTo(19.5, 12)
            shape.lineTo(13, 18.5)
    elif name == 'reload':
        # Same round-cap, 2px stroke as the Launch navigation arrows.
        painter.drawArc(QRectF(5.1, 5.1, 13.8, 13.8), 35 * 16, 295 * 16)
        shape.moveTo(19.4, 5.7)
        shape.lineTo(19.0, 11.5)
        shape.lineTo(13.7, 8.9)
    elif name == 'plus':
        shape.moveTo(12, 5)
        shape.lineTo(12, 19)
        shape.moveTo(5, 12)
        shape.lineTo(19, 12)
    elif name == 'external':
        shape.moveTo(13, 5)
        shape.lineTo(19, 5)
        shape.lineTo(19, 11)
        shape.moveTo(19, 5)
        shape.lineTo(9, 15)
        shape.moveTo(16.5, 15)
        shape.lineTo(16.5, 19)
        shape.lineTo(5, 19)
        shape.lineTo(5, 7.5)
        shape.lineTo(9, 7.5)
    elif name == 'download':
        shape.moveTo(12, 4)
        shape.lineTo(12, 16)
        shape.moveTo(7.5, 11.5)
        shape.lineTo(12, 16)
        shape.lineTo(16.5, 11.5)
        shape.moveTo(5, 19.5)
        shape.lineTo(19, 19.5)
    elif name == 'folder_open':
        # Open folder: simple rounded file-folder silhouette.
        shape.moveTo(3.5, 18.5)
        shape.lineTo(5.0, 8.2)
        shape.lineTo(9, 8.2)
        shape.lineTo(11, 10.3)
        shape.lineTo(20.5, 10.3)
        shape.lineTo(19, 18.5)
        shape.closeSubpath()
        shape.moveTo(4.7, 8.0)
        shape.lineTo(4.7, 5.6)
        shape.lineTo(10.5, 5.6)
        shape.lineTo(12.2, 7.5)
        shape.lineTo(19, 7.5)
    elif name == 'unzip':
        # Archive square and an up-arrow: extract without executing contents.
        shape.moveTo(5, 6)
        shape.lineTo(19, 6)
        shape.lineTo(19, 19.5)
        shape.lineTo(5, 19.5)
        shape.closeSubpath()
        shape.moveTo(10, 9)
        shape.lineTo(12, 7)
        shape.lineTo(14, 9)
        shape.moveTo(12, 7)
        shape.lineTo(12, 15.5)
        shape.moveTo(9, 16.5)
        shape.lineTo(15, 16.5)
    elif name == 'close':
        shape.moveTo(8, 8)
        shape.lineTo(16, 16)
        shape.moveTo(16, 8)
        shape.lineTo(8, 16)
    elif name == 'globe':
        painter.drawEllipse(QRectF(4, 4, 16, 16))
        painter.drawEllipse(QRectF(8, 4, 8, 16))
        shape.moveTo(4, 12)
        shape.lineTo(20, 12)
    elif name == 'home':
        # 屋根
        shape.moveTo(3.5, 10.7)
        shape.lineTo(12, 3.8)
        shape.lineTo(20.5, 10.7)

        # 左壁 + 左下の線
        shape.moveTo(5.8, 9.5)
        shape.lineTo(5.8, 20)
        shape.lineTo(9.6, 20)

        # 右下の線 + 右壁
        shape.moveTo(14.4, 20)
        shape.lineTo(18.2, 20)
        shape.lineTo(18.2, 9.5)

        # ドア
        shape.moveTo(9.6, 20)
        shape.lineTo(9.6, 13.7)
        shape.lineTo(14.4, 13.7)
        shape.lineTo(14.4, 20)
    else:
        painter.end()
        raise ValueError(f'Unknown browser navigation icon: {name}')

    painter.drawPath(shape)
    painter.end()
    return pixmap


def browser_navigation_icon(name: str, theme: str) -> QIcon:
    """Return theme-aware Chrome-style icons with disabled pixmaps."""
    is_light = theme == 'light'
    enabled = '#425750' if is_light else '#d5e3ed'
    disabled = '#acbdb7' if is_light else '#60736f'
    result = QIcon()
    result.addPixmap(_draw_icon(name, enabled), QIcon.Mode.Normal)
    result.addPixmap(_draw_icon(name, enabled), QIcon.Mode.Active)
    result.addPixmap(_draw_icon(name, disabled), QIcon.Mode.Disabled)
    return result
