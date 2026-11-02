"""Horizontal Browser bookmarks shared by embedded and external web workspaces.

The authored bookmark model is the single source of truth. A nested QMenu is
populated on demand rather than materializing all Chrome/Edge bookmark nodes.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QFrame, QWidget, QHBoxLayout, QToolButton, QMenu


class HorizontalBookmarkBar(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('launchWebBookmarkStrip')
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setMaximumHeight(45)
        self.setMinimumHeight(32)
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

    def update_bookmark_bar(self, rows, children_of, open_row):
        """Rebuild horizontal, mode-independent Browser bookmarks."""
        self._bookmark_bar_roots = list(rows or [])
        self._bookmark_bar_children = children_of
        self._bookmark_bar_open = open_row
        # Avoid destroying an open dropdown (and re-creating potentially many
        # buttons) merely because the Browser tab becomes active again.
        signature = tuple((str(row.get('item_id')), str(row.get('title')),
                           str(row.get('item_kind')))
                          for row in self._bookmark_bar_roots if isinstance(row, dict))
        if signature == self._bookmark_bar_signature:
            return
        self._bookmark_bar_signature = signature
        bar = self.bookmark_strip_row
        while bar.count():
            item = bar.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        for row in self._bookmark_bar_roots:
            if not isinstance(row, dict) or row.get('_bookmark_group_header'):
                continue
            title = str(row.get('title') or '').strip()
            if not title:
                continue
            button = QToolButton(self.bookmark_strip_inner)
            button.setObjectName('launchWebBookmarkEntry')
            button.setText(title)
            button.setToolTip(row.get('description') or title)
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedHeight(27)
            # A single smaller text step keeps this compact operation bar tidy.
            font = button.font()
            if font.pointSizeF() > 0:
                font.setPointSizeF(max(8.0, font.pointSizeF() - 1.0))
            elif font.pixelSize() > 0:
                font.setPixelSize(max(10, font.pixelSize() - 1))
            button.setFont(font)
            # Qt draws a menu indicator automatically on InstantPopup buttons;
            # the folder icon already communicates the menu, so hide the ▼.
            button.setStyleSheet(
                'QToolButton#launchWebBookmarkEntry { font-size: 12px; } '
                'QToolButton#launchWebBookmarkEntry::menu-indicator { image: none; width: 0px; }')
            if row.get('item_kind') in ('category', 'directory'):
                # Populate only when opened; Chrome profiles can contain
                # thousands of bookmarks and nested folders.
                menu = QMenu(button)
                menu.aboutToShow.connect(
                    lambda r=row, m=menu: self._fill_bookmark_menu(m, r, {r.get('item_id')}, 0))
                button.setMenu(menu)
                button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
                button.setText('📁 ' + title)
            else:
                button.clicked.connect(lambda _checked=False, r=row: self._open_bookmark_bar_row(r))
            bar.addWidget(button)
        bar.addStretch(1)

    def _fill_bookmark_menu(self, menu, parent, seen, depth):
        menu.clear()
        children_of = self._bookmark_bar_children
        if not callable(children_of) or depth >= 16:
            menu.addAction('これ以上展開できません').setEnabled(False)
            return
        try:
            children = children_of(parent)
        except (KeyError, ValueError, TypeError):
            children = []
        count = 0
        for row in children or []:
            if not isinstance(row, dict):
                continue
            identity = row.get('item_id')
            if identity in seen:
                continue
            title = str(row.get('title') or '').strip()
            if not title:
                continue
            count += 1
            if row.get('item_kind') in ('category', 'directory'):
                submenu = menu.addMenu('📁 ' + title)
                submenu.aboutToShow.connect(
                    lambda r=row, m=submenu, ids=frozenset(seen | {identity}), d=depth+1:
                    self._fill_bookmark_menu(m, r, ids, d))
            else:
                action = menu.addAction(title)
                action.triggered.connect(
                    lambda _checked=False, r=row: self._open_bookmark_bar_row(r))
            if count >= 500:
                menu.addAction('残りは検索から開いてください').setEnabled(False)
                break
        if not count:
            menu.addAction('（空のフォルダー）').setEnabled(False)

    def _open_bookmark_bar_row(self, row):
        handler = self._bookmark_bar_open
        if callable(handler):
            handler(row)

