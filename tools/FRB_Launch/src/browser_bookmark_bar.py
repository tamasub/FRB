"""Horizontal Browser bookmarks with preserved folder hierarchy.

Only the top-level rows are rendered in the scrollable strip. Folder buttons
open nested menus on click; scrolling never expands a folder or opens a URL.
The imported bookmark rows remain unchanged.
"""
from PySide6.QtCore import Qt, QEvent, QPoint, QTimer
from PySide6.QtWidgets import (QApplication, QScrollArea, QFrame, QWidget,
                              QHBoxLayout, QToolButton, QMenu)
from PySide6.QtGui import QCursor


class HorizontalBookmarkBar(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        # QScrollArea can dispatch eventFilter() from setWidget() or during
        # child registration, before the constructor reaches its final lines.
        # These fields must exist before installing the scroll-area widget.
        self._buttons = []
        self._wheel_current = None
        self._wheel_edge_active = False
        self._wheel_pointer = None
        self.pointer_follow_enabled = lambda: True
        self._wheel_settle_timer = QTimer(self)
        self._wheel_settle_timer.setSingleShot(True)
        self._wheel_settle_timer.setInterval(120)
        self._wheel_settle_timer.timeout.connect(self._settle_wheel_current)
        self.setObjectName('launchWebBookmarkStrip')
        # Natural content width matters: a resizable child consumes the
        # viewport width and prevents native horizontal scrolling.
        self.setWidgetResizable(False)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setMaximumHeight(52)
        self.setMinimumHeight(47)
        self.bookmark_strip_inner = QWidget(self)
        self.bookmark_strip_inner.setObjectName('launchWebBookmarkStripInner')
        self.bookmark_strip_row = QHBoxLayout(self.bookmark_strip_inner)
        self.bookmark_strip_row.setContentsMargins(4, 2, 4, 2)
        self.bookmark_strip_row.setSpacing(3)
        self.setWidget(self.bookmark_strip_inner)
        self._bookmark_bar_roots = []
        self._bookmark_bar_children = None
        self._bookmark_bar_open = None
        self._bookmark_bar_signature = None
        self._folder_menu = None

    @staticmethod
    def _is_folder(row):
        return row.get('item_kind') in ('category', 'directory')

    def update_bookmark_bar(self, rows, children_of, open_row):
        """Render exactly the supplied level; NEVER flatten folder children.

        The horizontal strip can wheel-scroll without sacrificing the original
        bookmark hierarchy. A folder is one button and opens on a real click.
        """
        self._bookmark_bar_roots = list(rows or [])
        self._bookmark_bar_children = children_of
        self._bookmark_bar_open = open_row
        signature = tuple((str(row.get('item_id')), str(row.get('title')),
                           str(row.get('item_kind')))
                          for row in self._bookmark_bar_roots
                          if isinstance(row, dict))
        if signature == self._bookmark_bar_signature:
            return
        previous_x = self.horizontalScrollBar().value()
        if self._folder_menu is not None:
            self._folder_menu.close()
            self._folder_menu = None
        self._bookmark_bar_signature = signature
        bar = self.bookmark_strip_row
        self._wheel_settle_timer.stop()
        self._wheel_pointer = None
        self._wheel_edge_active = False
        self._wheel_current = None
        self._buttons.clear()
        while bar.count():
            item = bar.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.removeEventFilter(self)
                widget.deleteLater()
        for row in self._bookmark_bar_roots:
            if not isinstance(row, dict) or row.get('_bookmark_group_header'):
                continue
            title = str(row.get('title') or '').strip()
            if not title:
                continue
            folder = self._is_folder(row)
            button = QToolButton(self.bookmark_strip_inner)
            button.setObjectName('launchWebBookmarkEntry')
            button.setText(('📁 ' if folder else '') + title)
            button.setToolTip((title + '\n' + str(row.get('description') or '')).strip())
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedHeight(27)
            font = button.font()
            if font.pointSizeF() > 0:
                font.setPointSizeF(max(8.0, font.pointSizeF() - 1.0))
            elif font.pixelSize() > 0:
                font.setPixelSize(max(10, font.pixelSize() - 1))
            button.setFont(font)
            button.setStyleSheet(
                'QToolButton#launchWebBookmarkEntry { font-size: 12px; }'
                'QToolButton#launchWebBookmarkEntry::menu-indicator { image: none; width: 0px; }'
                'QToolButton#launchWebBookmarkEntry[wheelCurrent="true"] {'
                'border:1px solid #6eae8b; background:rgba(102,175,134,0.16);}')
            if folder:
                button.clicked.connect(
                    lambda _checked=False, r=row, b=button: self._open_folder(r, b))
            else:
                button.clicked.connect(
                    lambda _checked=False, r=row: self._open_bookmark_bar_row(r))
            button.installEventFilter(self)
            bar.addWidget(button)
            self._buttons.append(button)
        self.bookmark_strip_inner.adjustSize()
        self.horizontalScrollBar().setValue(previous_x)

    def _folder_rows(self, row):
        if not callable(self._bookmark_bar_children):
            return []
        try:
            return list(self._bookmark_bar_children(row) or [])
        except (KeyError, ValueError, TypeError, OSError):
            return []

    def _fill_folder_menu(self, menu, folder, visited, depth=0):
        """Build nested QMenus without altering bookmark data or firing URLs.

        Limit total visible nodes per menu and guard cyclic imported folders.
        """
        if depth >= 20:
            return
        identity = str(folder.get('item_id') or id(folder))
        if identity in visited:
            return
        visited = visited | {identity}
        for child in self._folder_rows(folder)[:400]:
            if not isinstance(child, dict) or child.get('_bookmark_group_header'):
                continue
            title = str(child.get('title') or '').strip()
            if not title:
                continue
            if self._is_folder(child):
                submenu = menu.addMenu('📁 ' + title)
                self._fill_folder_menu(submenu, child, visited, depth + 1)
            else:
                action = menu.addAction(title)
                action.setToolTip(str(child.get('description') or ''))
                action.triggered.connect(
                    lambda _checked=False, r=child: self._open_bookmark_bar_row(r))

    def _open_folder(self, folder, anchor):
        """Only a click may expand a folder; never expand during wheel scroll."""
        if self._folder_menu is not None:
            self._folder_menu.close()
        menu = QMenu(self)
        menu.setToolTipsVisible(True)
        self._folder_menu = menu
        self._fill_folder_menu(menu, folder, set())
        if not menu.actions():
            action = menu.addAction('（空のフォルダー）')
            action.setEnabled(False)
        menu.aboutToHide.connect(lambda m=menu: self._clear_folder_menu(m))
        menu.aboutToHide.connect(menu.deleteLater)
        menu.popup(anchor.mapToGlobal(QPoint(0, anchor.height())))

    def _clear_folder_menu(self, menu):
        if self._folder_menu is menu:
            self._folder_menu = None

    def eventFilter(self, obj, event):
        # Guard events delivered during Qt initialization or shutdown.
        if event.type() == QEvent.Type.Wheel and obj in getattr(self, '_buttons', ()):
            self._scroll_wheel(event, source=obj)
            return True
        return super().eventFilter(obj, event)

    def wheelEvent(self, event):
        self._scroll_wheel(event)

    def _scroll_wheel(self, event, source=None):
        """WAN hybrid: scroll normally, then follow the current at an edge.

        During normal scrolling, the pointer stays stationary while bookmark
        buttons flow beneath it. Once scrolling stops, select the button under
        that point. At a *real scrollbar edge*, subsequent wheel notches move
        the current to adjacent buttons (cursor follows if permitted).
        Nothing on the wheel path opens a folder or launches a URL.
        """
        if (event.modifiers() != Qt.KeyboardModifier.NoModifier or
                QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            self._wheel_settle_timer.stop()
            self._wheel_edge_active = False
            event.ignore()
            return
        angles, pixels = event.angleDelta(), event.pixelDelta()
        angle = angles.x() if abs(angles.x()) > abs(angles.y()) else angles.y()
        pixel = pixels.x() if abs(pixels.x()) > abs(pixels.y()) else pixels.y()
        if not angle and not pixel:
            event.ignore()
            return
        bar = self.horizontalScrollBar()
        before = bar.value()
        delta = round((angle / 120.0) * 85) if angle else pixel
        if not delta:
            delta = 1 if (angle or pixel) > 0 else -1
        # The position of the pointer, unlike the contents, is stationary.
        # A button-local wheel event and an area-local event use different
        # coordinate systems, so normalize both to global here.
        source_widget = source if source is not None else self
        pointer = source_widget.mapToGlobal(event.position().toPoint())
        viewport_point = self.viewport().mapFromGlobal(pointer)
        bar.setValue(before - delta)
        after = bar.value()
        if after != before:
            self._wheel_edge_active = False
            self._wheel_pointer = pointer
            self._wheel_settle_timer.start()
        elif (self._buttons and self.viewport().rect().contains(viewport_point)
              and ((delta > 0 and before == bar.minimum()) or
                   (delta < 0 and before == bar.maximum()))):
            # After exhausting the native scroll range, continue moving the
            # current among visible buttons. Never wrap at either end.
            self._wheel_settle_timer.stop()
            self._wheel_pointer = None
            hovered = self._button_under_global(pointer)
            origin = (self._wheel_current if self._wheel_edge_active and
                      self._wheel_current in self._buttons else hovered)
            if origin is None:
                origin = self._buttons[0 if delta < 0 else -1]
            index = self._buttons.index(origin)
            direction = -1 if delta > 0 else 1
            steps = max(1, min(5, round(abs(angle) / 120) if angle
                               else round(abs(pixel) / 85)))
            target = self._buttons[max(0, min(len(self._buttons) - 1,
                                             index + direction * steps))]
            self._wheel_edge_active = True
            self._set_wheel_current(target)
            self._follow_wheel_pointer(target, pointer)
        else:
            self._wheel_edge_active = False
        event.accept()

    def _button_under_global(self, point):
        """Get a real bookmark button at the pointer; never a folder child."""
        local = self.bookmark_strip_inner.mapFromGlobal(point)
        for button in self._buttons:
            if button.isVisible() and button.geometry().contains(local):
                return button
        return None

    def _settle_wheel_current(self):
        """Only commit target flow after the final native scroll event."""
        pointer = self._wheel_pointer
        self._wheel_pointer = None
        if pointer is None or not self.isVisible() or QCursor.pos() != pointer:
            return
        if not self.viewport().rect().contains(self.viewport().mapFromGlobal(pointer)):
            return
        button = self._button_under_global(pointer)
        if button is not None:
            self._set_wheel_current(button)

    def _follow_wheel_pointer(self, button, original):
        """At the scroll edge, move the pointer only when user permits it."""
        if (not self.isVisible() or button is not self._wheel_current or
                not button.isVisible() or
                QApplication.mouseButtons() != Qt.MouseButton.NoButton or
                not self.pointer_follow_enabled() or
                QCursor.pos() != original):
            return
        point = button.mapToGlobal(button.rect().center())
        if point != original:
            QCursor.setPos(point)

    def _set_wheel_current(self, button):
        if self._wheel_current is button:
            return
        if self._wheel_current is not None:
            self._wheel_current.setProperty('wheelCurrent', False)
            self._wheel_current.style().unpolish(self._wheel_current)
            self._wheel_current.style().polish(self._wheel_current)
        self._wheel_current = button
        button.setProperty('wheelCurrent', True)
        button.style().unpolish(button)
        button.style().polish(button)

    def _open_bookmark_bar_row(self, row):
        handler = self._bookmark_bar_open
        if callable(handler):
            handler(row)
