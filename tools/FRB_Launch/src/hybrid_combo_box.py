"""Reusable FRB WAN Hybrid QComboBox for Launch dialogs.

The popup behaves like other FRB hybrid lists:
  1. wheel scrolls contents under the stationary pointer (Target Flow);
  2. at the actual scroll boundary, the highlighted row follows wheel
     movement and (when pointer-follow is enabled) the pointer follows it.

The native popup's item click/Enter selects the QComboBox value; a wheel alone
never accepts the containing dialog. No per-dialog guard / Remote dependency.
"""
from PySide6.QtCore import QEvent, QTimer, Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication, QComboBox
from wheel_adaptive import wheel_steps, can_follow_at_edge


class FRBHybridComboBox(QComboBox):
    """One standard icon/choice combo with built-in WAN wheel behaviour."""

    def __init__(self, parent=None, *, launcher=None):
        super().__init__(parent)
        self._launcher = launcher
        self._wan_remainder = 0
        self._wan_edge_follow = False
        self._wan_hover_global = None
        self._wan_hover_queued = False
        self.setMaxVisibleItems(12)
        self._install_wan_view_filter()

    def _install_wan_view_filter(self):
        view = self.view()
        view.installEventFilter(self)
        view.viewport().installEventFilter(self)

    def showPopup(self):
        self._wan_remainder = 0
        self._wan_edge_follow = False
        super().showPopup()
        # Qt can replace the view/viewport when native popup styles change.
        self._install_wan_view_filter()

    def hidePopup(self):
        self._wan_remainder = 0
        self._wan_edge_follow = False
        self._wan_hover_global = None
        super().hidePopup()

    def _pointer_follow_enabled(self):
        owner = self._launcher
        return bool(getattr(owner, 'pointer_warp_enabled', True))

    def _flow_hover_selection(self):
        self._wan_hover_queued = False
        pointer = self._wan_hover_global
        self._wan_hover_global = None
        if pointer is None or not self.view().isVisible() or QCursor.pos() != pointer:
            return
        view = self.view()
        local = view.viewport().mapFromGlobal(pointer)
        if view.viewport().rect().contains(local):
            index = view.indexAt(local)
            if index.isValid():
                # Highlight only; actual combo selection happens on mouse
                # click/Enter, exactly as for a native QComboBox popup.
                view.setCurrentIndex(index)

    def _hybrid_popup_wheel(self, event):
        view = self.view()
        if (event.modifiers() != Qt.KeyboardModifier.NoModifier
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return False  # Native Ctrl/Shift gestures keep their own meaning.
        angle, pixel = event.angleDelta().y(), event.pixelDelta().y()
        if not angle and not pixel:
            return False
        pointer = QCursor.pos()
        viewport = view.viewport()
        if not viewport.rect().contains(viewport.mapFromGlobal(pointer)):
            return False
        self._wan_remainder, movement = wheel_steps(
            self._wan_remainder, angle, pixel)
        if not movement:
            event.accept()
            return True
        bar = view.verticalScrollBar()
        before = bar.value()
        count = min(5, abs(movement))
        amount = max(1, bar.singleStep()) * count
        bar.setValue(before + (amount if movement > 0 else -amount))
        after = bar.value()
        if before != after:
            self._wan_edge_follow = False
            self._wan_hover_global = pointer
            if not self._wan_hover_queued:
                self._wan_hover_queued = True
                QTimer.singleShot(0, self._flow_hover_selection)
            event.accept()
            return True
        self._wan_hover_global = None
        if not can_follow_at_edge(before, after, bar.minimum(),
                                  bar.maximum(), movement):
            self._wan_edge_follow = False
            event.accept()
            return True
        hovered = view.indexAt(viewport.mapFromGlobal(pointer))
        current = view.currentIndex()
        start = (current if self._wan_edge_follow and current.isValid()
                 else hovered if hovered.isValid() else current)
        if not start.isValid():
            event.accept()
            return True
        # QComboBox uses a FLAT QListView, not QTreeView (which alone has
        # indexAbove/indexBelow). Use model.index(row) for either Qt style.
        # A wheel never commits the actual QComboBox value; Cancel remains safe.
        model = view.model()
        target = start
        for _ in range(count):
            next_row = target.row() + (1 if movement > 0 else -1)
            if not 0 <= next_row < model.rowCount(target.parent()):
                break
            candidate = model.index(next_row, target.column(), target.parent())
            if not candidate.isValid():
                break
            target = candidate
        if target != start:
            self._wan_edge_follow = True
            view.setCurrentIndex(target)
            view.scrollTo(target)
            if self._pointer_follow_enabled():
                def follow(expected=target):
                    if (view.isVisible() and view.currentIndex() == expected
                            and QApplication.mouseButtons() == Qt.MouseButton.NoButton):
                        target_rect = view.visualRect(expected)
                        if target_rect.isValid():
                            point = viewport.mapToGlobal(target_rect.center())
                            if viewport.rect().contains(viewport.mapFromGlobal(point)):
                                QCursor.setPos(point)
                QTimer.singleShot(0, follow)
        event.accept()
        return True

    def eventFilter(self, obj, event):
        view = self.view()
        if (event.type() == QEvent.Type.Wheel and view.isVisible()
                and obj in (view, view.viewport())):
            if self._hybrid_popup_wheel(event):
                return True
        return super().eventFilter(obj, event)
