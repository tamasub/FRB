"""Manual drag/drop for categorized search history.

Qt's InternalMove post-drop cleanup can remove an item moved by code in the
same event.  As with ReorderablePopupTree, ignore the native move and emit a
semantic request on the following event-loop tick.  The launcher persists the
change then redraws; it never modifies an active Qt drag model.
"""
from PySide6.QtCore import Qt, Signal, QTimer
from reorderable_tree import ReorderablePopupTree

ROLE_KIND = Qt.ItemDataRole.UserRole
ROLE_ID = Qt.ItemDataRole.UserRole + 1


class HistoryCategoryTree(ReorderablePopupTree):
    structureChanged = Signal(str, str, str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_origin = None

    def startDrag(self, supported_actions):
        self._drag_origin = self.currentItem()
        try:
            super().startDrag(supported_actions)
        finally:
            self._drag_origin = None

    def dropEvent(self, event):
        if event.source() is not self:
            event.ignore()
            return
        origin = self._drag_origin or self.currentItem()
        if origin is None:
            event.ignore()
            return
        kind = origin.data(0, ROLE_KIND)
        value = origin.data(0, ROLE_ID) if kind == 'category' else origin.text(0)
        if kind not in ('category', 'keyword') or value in ('uncategorized', 'session_history'):
            event.ignore()
            return
        point = event.position().toPoint()
        target = self.itemAt(point)
        if kind == 'keyword':
            if target is None:
                # Dropping below everything goes to the last category.
                folder = self.topLevelItem(self.topLevelItemCount()-1)
                if folder is None:
                    event.ignore(); return
                index = folder.childCount()
            elif target.data(0, ROLE_KIND) == 'category':
                folder = target
                index = folder.childCount()
            else:
                folder = target.parent()
                index = folder.indexOfChild(target)
                if point.y() > self.visualItemRect(target).center().y():
                    index += 1
            if folder is None:
                event.ignore(); return
            destination = folder.data(0, ROLE_ID)
            # The session folder is an auto-generated source, never a drop
            # target for saved entries. Drop outside it to keep persistence.
            if destination == 'session_history':
                event.ignore(); return
            operation = ('keyword', value, destination, index)
        else:
            if target is None:
                index = self.topLevelItemCount()
            else:
                folder = target if target.data(0, ROLE_KIND) == 'category' else target.parent()
                index = self.indexOfTopLevelItem(folder)
                if point.y() > self.visualItemRect(folder).center().y():
                    index += 1
            # Ignore the auto-generated volatile header and immutable 未分類.
            fixed_prefix = sum(self.topLevelItem(i).data(0, ROLE_ID) in
                               ('session_history', 'uncategorized')
                               for i in range(self.topLevelItemCount()))
            operation = ('category', value, '', max(0, index-fixed_prefix))
        event.ignore()
        QTimer.singleShot(0, lambda op=operation: self.structureChanged.emit(*op))
