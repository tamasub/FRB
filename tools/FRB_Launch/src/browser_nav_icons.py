"""Compact browser-style toolbar icons for FRB Launch.

Icons are vector paths painted at 2x resolution for sharp Windows/HiDPI
rendering.  Enabled/disabled and light/dark appearances are explicit, rather
than platform-dependent Unicode arrow/house glyphs.
"""

from PySide6.QtCore import Qt
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
    pen.setWidthF(1.0 if name == 'home' else 2.0)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    shape = QPainterPath()
    if name in ('back', 'forward'):
        # Chrome-like simple arrow: shaft + open, gently rounded chevron.
        if name == 'back':
            shape.moveTo(20, 12)
            shape.lineTo(4.5, 12)
            shape.moveTo(11, 5.5)
            shape.lineTo(4.5, 12)
            shape.lineTo(11, 18.5)
        else:
            shape.moveTo(4, 12)
            shape.lineTo(19.5, 12)
            shape.moveTo(13, 5.5)
            shape.lineTo(19.5, 12)
            shape.lineTo(13, 18.5)
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
