"""Mouse reordering of a single visible group of menu items."""
from PySide6.QtCore import Qt, QMimeData, QEvent, QRect
from PySide6.QtGui import QDrag, QPainter, QColor, QBrush, QPen
from PySide6.QtWidgets import QApplication, QTreeWidget, QStyledItemDelegate, QStyle, QStyleOptionViewItem
from main_grid_visual_state import ROW_PALETTE, row_visual_state, row_fill, row_has_outline

MIME='application/x-frb-launch-order'

class OrderDragMixin:
    def setup_order_drag(self):
        self.order_rows=[];self.order_enabled=False;self.order_boundary=None
        self.setAcceptDrops(True)

    def begin_order_drag(self, row):
        if not self.order_enabled or row is None:return
        self.launcher.hover_timer.stop();self.launcher.pending_menu_item=None
        if hasattr(self,'hover_timer'):self.hover_timer.stop()
        if hasattr(self,'child') and self.child:self.child.close()
        if isinstance(self,QTreeWidget) and self.launcher.menu:self.launcher.menu.close()
        mime=QMimeData();mime.setData(MIME,(str(id(self))+'\n'+row['item_id']).encode())
        drag=QDrag(self);drag.setMimeData(mime)
        self.order_dragging=True
        try:drag.exec(Qt.DropAction.MoveAction)
        finally:
            self.order_dragging=False;self.order_boundary=None;self.order_surface().update()

    def dragEnterEvent(self,event):
        if self.order_source(event):event.acceptProposedAction()
        else:event.ignore()

    def order_source(self,event):
        if not self.order_enabled or not event.mimeData().hasFormat(MIME):return None
        raw=bytes(event.mimeData().data(MIME)).decode().split('\n',1)
        if len(raw)!=2 or raw[0]!=str(id(self)):return None
        return raw[1] if any(r['item_id']==raw[1] for r in self.order_rows) else None

    def dragMoveEvent(self,event):
        if not self.order_source(event):event.ignore();return
        self.order_boundary=self.order_index(event.position().toPoint())
        self.order_surface().update();event.acceptProposedAction()

    def dragLeaveEvent(self,event):
        self.order_boundary=None;self.order_surface().update();event.accept()

    def dropEvent(self,event):
        source=self.order_source(event)
        if source is None:event.ignore();return
        self.apply_order_drop(source,self.order_index(event.position().toPoint()))
        self.order_boundary=None;self.order_surface().update();event.acceptProposedAction()

    def apply_order_drop(self, source, boundary):
        ids=[r['item_id'] for r in self.order_rows]
        old=ids.index(source);ids.pop(old)
        ids.insert(boundary-(1 if old<boundary else 0),source)
        if ids!=[r['item_id'] for r in self.order_rows]:
            return self.launcher.persist_order(ids,self.order_page,self.order_parent,source)
        return True

    def paint_order_line(self):
        if self.order_boundary is None:return
        rects=self.order_rects()
        if not rects:return
        boundary=self.order_boundary
        y=rects[boundary].top() if boundary<len(rects) else rects[-1].bottom()
        painter=QPainter(self.order_surface());painter.setPen(QColor('#72d7c0'))
        painter.drawLine(0,y,self.order_surface().width(),y);painter.end()

    def order_index(self, pos):
        for index,rect in enumerate(self.order_rects()):
            if pos.y()<rect.center().y():return index
        return len(self.order_rows)

class MainGridRowDelegate(QStyledItemDelegate):
    """Render icons, text and checkboxes without Qt's native row highlight.

    The QTreeWidget::item stylesheet can paint *over* option.backgroundBrush,
    so background/outline ownership belongs entirely to ReorderTree.drawRow.
    """
    def __init__(self, tree):
        super().__init__(tree)
        self.tree = tree

    def paint(self, painter, option, index):
        tree = self.tree
        if not tree.main_grid_visuals:
            super().paint(painter, option, index)
            return
        opts = QStyleOptionViewItem(option)
        opts.state &= ~(QStyle.StateFlag.State_Selected |
                        QStyle.StateFlag.State_MouseOver |
                        QStyle.StateFlag.State_HasFocus)
        # Do not supply a background to the delegate: the row-level painting
        # happens before text/icon/checkbox painting, including for columns 0/1.
        opts.backgroundBrush = QBrush(Qt.BrushStyle.NoBrush)
        super().paint(painter, opts, index)


class ReorderTree(OrderDragMixin,QTreeWidget):
    def __init__(self, launcher):
        super().__init__();self.launcher=launcher;self.setup_order_drag()
        self.setDragEnabled(True)
        self.main_grid_visuals = True
        self.row_palette = ROW_PALETTE['dark']
        self._hover_item = None
        self.setItemDelegate(MainGridRowDelegate(self))
        self.viewport().setMouseTracking(True)
        self.currentItemChanged.connect(lambda *_: self.viewport().update())

    def set_row_theme(self, theme):
        self.row_palette = ROW_PALETTE['light' if theme == 'light' else 'dark']
        self.viewport().update()

    def grid_has_focus(self):
        """Qt may give focus to the abstract scroll area's viewport."""
        return (self.hasFocus() or self.viewport().hasFocus()
                or QApplication.focusWidget() is self)

    def row_state_for_index(self, index):
        if not index.isValid():
            return 'normal'
        item = self.itemFromIndex(index)
        return row_visual_state(current=(item is not None and item == self.currentItem()),
                                focused=self.grid_has_focus(),
                                hovered=(item is not None and item == self._hover_item))

    def clear_row_hover(self):
        if self._hover_item is not None:
            self._hover_item = None
            self.viewport().update()

    def viewportEvent(self, event):
        # Mouse hover never requires keyboard focus or changes a checkbox.
        kind = event.type()
        if kind in (QEvent.Type.MouseMove, QEvent.Type.HoverMove):
            item = self.itemAt(event.position().toPoint())
            if item != self._hover_item:
                self._hover_item = item
                self.viewport().update()
        elif kind in (QEvent.Type.Leave, QEvent.Type.HoverLeave):
            self.clear_row_hover()
        elif kind in (QEvent.Type.FocusIn, QEvent.Type.FocusOut):
            self.viewport().update()
        return super().viewportEvent(event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.viewport().update()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.viewport().update()

    def mousePressEvent(self,event):
        self.launcher.hover_timer.stop();self.launcher.pending_menu_item=None
        super().mousePressEvent(event)

    def startDrag(self, actions):
        q=self.currentItem()
        self.begin_order_drag(q.data(0,Qt.ItemDataRole.UserRole) if q else None)

    def order_surface(self):return self.viewport()
    def order_rects(self):return [self.visualItemRect(self.topLevelItem(i)) for i in range(self.topLevelItemCount())]
    def drawRow(self, painter, option, index):
        """Paint a *whole* row using the viewport's actual paint device.

        Previous attempts passed blue through a QStyledItemDelegate's
        option.backgroundBrush. QSS's ::item rules overwrite that color on
        Windows. Painting directly in drawRow before native content, and then
        drawing the current-row border over it, avoids that conflict.
        """
        if not self.main_grid_visuals:
            super().drawRow(painter, option, index)
            return
        state = self.row_state_for_index(index)
        bounds = option.rect
        if not bounds.isValid():
            super().drawRow(painter, option, index)
            return
        full_row = QRect(0, bounds.y(), self.viewport().width(), bounds.height())
        # Keep background independent of selected item flags and columns.
        fill = row_fill(self.row_palette, state)
        if fill:
            painter.fillRect(full_row, QColor(fill))
        # QTreeView may also draw a native *row-level* selection panel before
        # invoking delegates. Strip those flags at this outer layer too.
        opts = QStyleOptionViewItem(option)
        opts.state &= ~(QStyle.StateFlag.State_Selected |
                        QStyle.StateFlag.State_MouseOver |
                        QStyle.StateFlag.State_HasFocus)
        super().drawRow(painter, opts, index)
        if row_has_outline(state):
            painter.save()
            painter.setPen(QPen(QColor(self.row_palette['outline']), 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(full_row.adjusted(0, 0, -1, -1))
            painter.restore()

    def paintEvent(self, event):
        # Main-row visuals are painted in drawRow, not in paintEvent: Qt can
        # compose individual rows after the parent paint handler returns.
        super().paintEvent(event)
        if (getattr(self.launcher, '_column_mode', None) == 'main' and
                getattr(self.launcher, '_main_column_hover', False)):
            x = self.columnViewportPosition(1)
            painter = QPainter(self.viewport())
            painter.setPen(QColor('#7296b9'))
            painter.drawLine(x, 0, x, self.viewport().height())
            painter.end()
        self.paint_order_line()
