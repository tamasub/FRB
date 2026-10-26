"""Small, DPI-friendly, locally painted icons for FRB Launch context actions.

No Windows resources, icon themes or external assets are required.
"""
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap


def context_action_icon(action_id):
    size = 24
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    color = '#ce5657' if action_id == 'delete' else '#8662b9' if action_id == 'git_commit_from_zip' else '#487ca6'
    stroke = QPen(QColor(color), 1.8)
    stroke.setCapStyle(Qt.PenCapStyle.RoundCap)
    stroke.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(stroke)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    def line(x1, y1, x2, y2):
        painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    if action_id in ('copy', 'copy_path', 'copy_full_path', 'copy_file_name'):
        painter.drawRoundedRect(QRectF(7, 7, 12, 13), 2, 2)
        line(5, 16, 4, 16)
        painter.drawRoundedRect(QRectF(4, 4, 12, 13), 2, 2)
        line(7, 8, 12, 8)
    elif action_id == 'copy_cloud_link':
        # Cloud link: two chain loops (not a local-path/document copy icon).
        painter.drawRoundedRect(QRectF(3.5, 9.5, 11, 6), 3, 3)
        painter.drawRoundedRect(QRectF(9.5, 9.5, 11, 6), 3, 3)
        line(9, 12.5, 15, 12.5)
    elif action_id == 'paste':
        painter.drawRoundedRect(QRectF(6, 6, 13, 15), 2, 2)
        painter.drawRoundedRect(QRectF(9, 3, 7, 5), 1.2, 1.2)
        line(9, 12, 16, 12)
        line(9, 16, 15, 16)
    elif action_id == 'cut':
        painter.drawEllipse(QRectF(3, 13, 6, 6))
        painter.drawEllipse(QRectF(13, 13, 6, 6))
        line(8, 15, 17, 5)
        line(16, 15, 7, 5)
    elif action_id == 'delete':
        line(5, 7, 19, 7)
        line(9, 5, 15, 5)
        painter.drawRoundedRect(QRectF(7, 9, 10, 11), 1, 1)
        line(11, 12, 11, 17)
        line(14, 12, 14, 17)
    elif action_id in ('open_explorer', 'open_parent_folder', 'new_category'):
        painter.setBrush(QColor('#e9c76f'))
        path = QPainterPath()
        path.moveTo(3, 8); path.lineTo(9, 8); path.lineTo(11, 10)
        path.lineTo(21, 10); path.lineTo(19, 19); path.lineTo(3, 19)
        path.closeSubpath()
        painter.drawPath(path)
        line(3, 8, 3, 18)
        if action_id == 'new_category':
            line(15, 12, 15, 17); line(12.5, 14.5, 17.5, 14.5)
    elif action_id == 'open_with':
        # App-window silhouette with small chooser dots: one-off file action.
        painter.drawRoundedRect(QRectF(3, 4, 18, 16), 2, 2)
        line(3, 9, 21, 9)
        painter.setBrush(QColor(color))
        for x in (8, 12, 16):
            painter.drawEllipse(QRectF(x - 0.8, 13 - 0.8, 1.6, 1.6))
    elif action_id in ('open_terminal', 'open_parent_terminal'):
        painter.drawRoundedRect(QRectF(3, 4, 18, 16), 2, 2)
        line(7, 9, 10, 12); line(10, 12, 7, 15); line(12, 16, 17, 16)
    elif action_id == 'run_with_pause':
        painter.drawRoundedRect(QRectF(3, 4, 18, 16), 2, 2)
        # Play + pause: script runs first, then waits for Enter.
        line(7, 9, 11, 12); line(11, 12, 7, 15); line(7, 15, 7, 9)
        line(15, 9, 15, 15); line(18, 9, 18, 15)
    elif action_id == 'rename':
        path = QPainterPath()
        path.moveTo(5, 17); path.lineTo(7, 12); path.lineTo(17, 4)
        path.lineTo(20, 8); path.lineTo(10, 17); path.closeSubpath()
        painter.drawPath(path)
        line(5, 19, 19, 19)
    elif action_id == 'git_commit_from_zip':
        painter.drawEllipse(QRectF(5, 3, 6, 6))
        painter.drawEllipse(QRectF(5, 15, 6, 6))
        painter.drawEllipse(QRectF(14, 9, 6, 6))
        line(8, 9, 8, 15); line(10.5, 7, 15.5, 11.5)
    elif action_id == 'properties':
        painter.drawRoundedRect(QRectF(5, 3, 14, 18), 2, 2)
        line(9, 8, 15, 8); line(9, 12, 15, 12); line(9, 16, 13, 16)
    else:
        painter.drawEllipse(QRectF(6, 6, 12, 12))
        line(12, 9, 12, 15)
    painter.end()
    return QIcon(pix)
