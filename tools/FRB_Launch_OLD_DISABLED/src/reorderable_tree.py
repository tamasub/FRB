"""Top-level-only drag reorder for history and favorite combobox-style lists."""
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import QTreeWidget, QAbstractItemView


class ReorderablePopupTree(QTreeWidget):
    orderChanged = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDropIndicatorShown(True)
        self.setDragDropOverwriteMode(False)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        # Both search history and folder favorites must keep the end of long
        # entries visible. This only affects paint-time elision, never the
        # complete string stored in QTreeWidgetItem.text(0) for actions/reorder.
        self.setTextElideMode(Qt.TextElideMode.ElideLeft)

    def values(self):
        return [self.topLevelItem(i).text(0) for i in range(self.topLevelItemCount())
                if self.topLevelItem(i).flags() & Qt.ItemFlag.ItemIsEnabled]

    def dropEvent(self, event):
        """Defer manual root-only reorder until after Qt finishes dragging.

        QTreeWidget InternalMove will otherwise run its own MoveAction cleanup
        after we have already taken/inserted a row. On Windows that can remove
        the just-moved item until the popup is reopened. The drop is marked as
        ignored *for Qt's model*, while we schedule the move ourselves.
        """
        if event.source() is not self:
            event.ignore()
            return
        dragged = self.currentItem()
        source = self.indexOfTopLevelItem(dragged) if dragged is not None else -1
        if source < 0:
            event.ignore()
            return
        point = event.position().toPoint()
        target_item = self.itemAt(point)
        if target_item is None:
            target = self.topLevelItemCount() if point.y() >= 0 else 0
        else:
            target = self.indexOfTopLevelItem(target_item)
            if target < 0:
                event.ignore()
                return
            if point.y() > self.visualItemRect(target_item).center().y():
                target += 1
        if target > source:
            target -= 1
        # Important: *do not* change the QTreeWidget model inside the drop
        # event: Qt's drag source still has MoveAction post-processing to run.
        event.ignore()
        if target != source:
            before = self.values()
            QTimer.singleShot(0, lambda: self._finish_root_reorder(before, source, target))

    def _finish_root_reorder(self, before, source, target):
        """Move one intact top-level row after native drag cleanup ends."""
        if self.values() != before or not 0 <= source < self.topLevelItemCount():
            return
        moved = self.takeTopLevelItem(source)
        if moved is None:
            return
        self.insertTopLevelItem(target, moved)
        self.setCurrentItem(moved)
        after = self.values()
        if (before != after and len(before) == len(after)
                and sorted(before) == sorted(after)):
            self.orderChanged.emit(after)
        self.viewport().update()
