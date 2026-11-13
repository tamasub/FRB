"""The same search/folder-history chevron, independent of the parent widget."""
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor


def combo_chevron_icon(theme='light', offset_x=0):
    """Crisp 14dp glyph, with its stroke visually shifted slightly left."""
    pix = QPixmap(28, 28)
    pix.setDevicePixelRatio(2)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    pen = QPen(QColor('#557667' if theme == 'light' else '#a9bed2'), 1.7)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    # Search history requests a 2px left nudge; breadcrumb keeps its origin.
    painter.drawLine(QPointF(1 + offset_x, 5), QPointF(5 + offset_x, 9))
    painter.drawLine(QPointF(5 + offset_x, 9), QPointF(9 + offset_x, 5))
    painter.end()
    return QIcon(pix)
