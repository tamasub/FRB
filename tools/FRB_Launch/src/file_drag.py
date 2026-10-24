"""Outbound file-copy drag for launcher tree rows and cascade actions.

QDrag + text/uri-list provides real Windows file URLs to Chromium/Explorer.
No file bytes are loaded, no copy/move/delete is performed by FRB Launch.
"""
from PySide6.QtCore import Qt, QMimeData, QUrl
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QAbstractItemView, QTreeWidget
from file_drag_paths import file_path_for_drag


def begin_file_copy_drag(widget, row):
    """Start a copy-only OS drag. Returns False when row is not an actual file."""
    path = file_path_for_drag(row)
    if path is None:
        return False
    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(path)])
    # Clipboard/OLE Windows consumers should see COPY, never MOVE.
    mime.setData('application/x-qt-windows-mime;value="Preferred DropEffect"',
                 (1).to_bytes(4, 'little'))
    drag = QDrag(widget)
    drag.setMimeData(mime)
    drag.exec(Qt.DropAction.CopyAction, Qt.DropAction.CopyAction)
    return True


class ExternalFileDragTree(QTreeWidget):
    """Drag selected physical file outside; keep click and keyboard handling."""

    def __init__(self, parent=None, row_resolver=None):
        super().__init__(parent)
        self._file_drag_row_resolver = row_resolver
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.setAcceptDrops(False)
        self.setDropIndicatorShown(False)

    def startDrag(self, supported_actions):
        item = self.currentItem()
        if item is None:
            return
        row = (self._file_drag_row_resolver(item) if self._file_drag_row_resolver
               else item.data(0, Qt.ItemDataRole.UserRole))
        begin_file_copy_drag(self, row)
