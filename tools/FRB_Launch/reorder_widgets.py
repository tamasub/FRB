"""Mouse reordering of a single visible group of menu items."""
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag, QPainter, QColor
from PySide6.QtWidgets import QTreeWidget

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

class ReorderTree(OrderDragMixin,QTreeWidget):
    def __init__(self, launcher):
        super().__init__();self.launcher=launcher;self.setup_order_drag()
        self.setDragEnabled(True)

    def mousePressEvent(self,event):
        self.launcher.hover_timer.stop();self.launcher.pending_menu_item=None
        super().mousePressEvent(event)

    def startDrag(self, actions):
        q=self.currentItem()
        self.begin_order_drag(q.data(0,Qt.ItemDataRole.UserRole) if q else None)

    def order_surface(self):return self.viewport()
    def order_rects(self):return [self.visualItemRect(self.topLevelItem(i)) for i in range(self.topLevelItemCount())]
    def paintEvent(self,event):
        super().paintEvent(event)
        if (getattr(self.launcher, '_column_mode', None) == 'main' and
                getattr(self.launcher, '_main_column_hover', False)):
            # Quiet alignment guide visible only when the hidden divider is
            # hovered/dragged; the normal main menu remains header-free.
            x = self.columnViewportPosition(1)
            painter = QPainter(self.viewport())
            painter.setPen(QColor('#7296b9'))
            painter.drawLine(x, 0, x, self.viewport().height())
            painter.end()
        self.paint_order_line()
