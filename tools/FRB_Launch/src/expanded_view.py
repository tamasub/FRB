"""Optional three-layer launcher view: Page -> root actions -> parallel panels.

This is a QWidget INSIDE the main window (never a second Qt.Tool popup).
All rows/actions are supplied by Launcher and use its existing menu data.
"""
from PySide6.QtCore import Qt, QPoint, QPointF, QSize, QTimer, QEvent, QRectF
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPixmap, QLinearGradient, QPen, QPalette, QCursor
from PySide6.QtWidgets import (QApplication, QFrame, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QTreeWidget, QTreeWidgetItem, QHeaderView, QAbstractItemView,
    QScrollArea, QSplitter, QSizePolicy, QLineEdit, QStackedWidget, QToolButton, QMenu, QFileIconProvider, QStyledItemDelegate, QStyleOptionViewItem, QStyle)

from file_drag import ExternalFileDragTree

from directory_address import (breadcrumb_segments, compact_segments,
                               directory_row, row_directory, normalized_directory)
from browser_nav_icons import browser_navigation_icon
from system_drives import drive_rows, pc_preview_row
from expanded_view_model import toolbar_roots, root_wheel_target
from expanded_selection import context_paths, physical_paths
from clipboard_paste import clipboard_sources
from virtual_clipboard_paste import is_virtual_file_clipboard
from context_menu_resolver import resolve_context_target
from context_menu_actions import rename_file_or_folder
from pathlib import Path
from folder_favorites import FolderFavorites
from combo_chevron_icon import combo_chevron_icon
from reorderable_tree import ReorderablePopupTree
from bookmark_cursor_follow import cursor_target, is_warp_generated_mouse_move
from wheel_adaptive import wheel_steps, can_follow_at_edge
from wheel_edge_hold import EdgeWheelHold
from wheel_zone_navigation import WheelZoneNavigation
from history_wheel_navigation import history_target_index, warp_to_history_row
from launch_appearance import theme_palette, theme_family, scrollbar_for_theme, history_popup_qss


MIDDLE_BACK_LANE_WIDTH = 24  # Invisible double-click-to-back strip after the chevron.


def header_icon(kind, theme):
    """Panel badges. Preserve the original folder; render the ribbon at true HiDPI."""
    if kind != 'bookmark':
        # Exact pre-2026-10-24-19:07 folder silhouette and logical size.
        # Do not scale the painter: the previous green cropped shape was an
        # unintended extra painter transform atop devicePixelRatio(2).
        pix = QPixmap(28, 28)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor('#8cbf68' if theme == 'light' else '#a7d785'))
        p.drawRoundedRect(3, 8, 22, 16, 3, 3)
        p.drawRoundedRect(5, 5, 11, 8, 2, 2)
        p.end()
        return QIcon(pix)

    # 2x backing pixels, 28 logical pixels; Qt handles the DPR automatically.
    # The sample has a soft green rounded top and a clear centred V-notch.
    pix = QPixmap(56, 56)
    pix.setDevicePixelRatio(2)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    ribbon = QPainterPath()
    ribbon.moveTo(6.5, 4.0)
    ribbon.cubicTo(5.0, 4.0, 4.0, 5.2, 4.0, 6.7)
    ribbon.lineTo(4.0, 24.5)
    ribbon.cubicTo(4.0, 25.3, 4.9, 25.7, 5.5, 25.2)
    ribbon.lineTo(14, 19.5)
    ribbon.lineTo(22.5, 25.2)
    ribbon.cubicTo(23.1, 25.7, 24, 25.3, 24, 24.5)
    ribbon.lineTo(24, 6.7)
    ribbon.cubicTo(24, 5.2, 23, 4, 21.5, 4)
    ribbon.closeSubpath()
    # Keep the color quiet and close to the mint screenshot, not glossy.
    gradient = QLinearGradient(4, 4, 24, 26)
    gradient.setColorAt(0, QColor('#59b895' if theme == 'light' else '#83d2b5'))
    gradient.setColorAt(1, QColor('#3ca586' if theme == 'light' else '#56b898'))
    p.setBrush(gradient)
    p.drawPath(ribbon)
    p.end()
    return QIcon(pix)


class _NavigationChevronDelegate(QStyledItemDelegate):
    """Quiet, small chevron with an intentional right-side inset."""

    def __init__(self, parent=None, right_inset=20):
        super().__init__(parent)
        self.right_inset = right_inset

    def createEditor(self, parent, option, index):
        # Column 1 is a navigation glyph, never a filename editor.
        return None

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        if not index.data(Qt.ItemDataRole.UserRole):
            return
        center_x = option.rect.right() - self.right_inset  # leave the middle Back lane clear
        center_y = option.rect.center().y()
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(option.palette.color(QPalette.ColorRole.Text), 1.6,
                            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                            Qt.PenJoinStyle.RoundJoin))
        chevron = QPainterPath()
        chevron.moveTo(center_x - 2.5, center_y - 4)
        chevron.lineTo(center_x + 2, center_y)
        chevron.lineTo(center_x - 2.5, center_y + 4)
        painter.drawPath(chevron)
        painter.restore()


def link_icon(theme):
    """Mint link badge inspired by the mockup; rendered as vectors at any DPI."""
    pix = QPixmap(24, 24)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor('#a4e5d5' if theme == 'light' else '#468e7d'))
    painter.drawRoundedRect(1, 1, 22, 22, 5, 5)
    pen = painter.pen()
    pen.setColor(QColor('#176d61' if theme == 'light' else '#e0fff0'))
    pen.setWidthF(1.9)
    pen.setStyle(Qt.PenStyle.SolidLine)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(5, 11, 9, 7)
    painter.drawEllipse(10, 6, 9, 7)
    painter.drawLine(10, 14, 15, 10)
    painter.end()
    return QIcon(pix)


def density_lines_icon(theme):
    """Three crisp horizontal strokes, visually centered in the square button."""
    pix = QPixmap(56, 56)
    pix.setDevicePixelRatio(2)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor('#3a6254' if theme == 'light' else '#e4f0e8'), 2.0)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    # Slightly right/down vs. the previous icon so it reads optically centered.
    for y in (10, 16, 22):
        painter.drawLine(7, y, 23, y)
    painter.end()
    return QIcon(pix)


class _InlineRenameDelegate(QStyledItemDelegate):
    """Keep the editor text exactly the same size as its surrounding row."""

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            editor.setObjectName('inlineRenameEditor')
            editor.setFont(option.font)
            pixels = option.font.pixelSize()
            if pixels <= 0:
                pixels = parent.font().pixelSize()
            # The generic application QLineEdit rule is 15px, whereas the
            # expanded list uses 13px. Override the generic stylesheet here.
            editor.setStyleSheet(
                'QLineEdit#inlineRenameEditor { '
                f'font-size:{pixels if pixels > 0 else 13}px; '
                'padding:0px 3px; }')
        return editor


class _SeparatedFileTree(ExternalFileDragTree):
    """Inset, hairline row separators and a passive current-row outline."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.separator_color = QColor('#eaf0eb')
        self.separator_inset = 12
        self.separator_width = 0.65
        self.inactive_current_border = QColor('#8fc7ab')
        self.adaptive_wheel_callback = None  # Only enabled on Files middle pane.

    def wheelEvent(self, event):
        # Preserve native smooth scrolling first; only the actual change in
        # scrollbar position may trigger WAN's cursor-follow fallback.
        scrollbar = self.verticalScrollBar()
        before = scrollbar.value()
        super().wheelEvent(event)
        callback = self.adaptive_wheel_callback
        if callback is not None and callback(event, before, scrollbar.value()):
            event.accept()

    def mousePressEvent(self, event):
        if (self.selectionMode() == QAbstractItemView.SelectionMode.ExtendedSelection
                and event.button() == Qt.MouseButton.RightButton):
            # Qt's default right-press can silently ClearAndSelect. Keep all
            # selected rows if clicked inside the selection, like Explorer.
            item = self.itemAt(event.position().toPoint())
            if item is not None and not item.isSelected():
                self.clearSelection()
                self.setCurrentItem(item)
                item.setSelected(True)
            # ContextMenu event is dispatched separately by Qt; never send
            # this right press through QTreeWidget's selection handler.
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if (self.selectionMode() == QAbstractItemView.SelectionMode.ExtendedSelection
                and event.button() == Qt.MouseButton.RightButton):
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.viewport().update()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.viewport().update()

    def _column_is_focused(self):
        """A rename editor is part of the middle pane's keyboard focus."""
        focused = QApplication.focusWidget()
        return bool(self.hasFocus() or
                    (focused is not None and self.isAncestorOf(focused)))

    def drawRow(self, painter, option, index):
        # Keep a single pale-green active column. A different pane's current
        # item remains visible as an outline, with no filled selection behind it.
        focused = self._column_is_focused()
        row_option = option
        if not focused:
            row_option = QStyleOptionViewItem(option)
            row_option.state &= ~QStyle.StateFlag.State_Selected
        super().drawRow(painter, row_option, index)
        if not option.rect.isValid():
            return
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        current = self.currentItem()
        if (not focused and current is not None and
                self.indexOfTopLevelItem(current) == index.row()):
            rect = QRectF(option.rect.adjusted(5, 3, -5, -3))
            painter.setPen(QPen(self.inactive_current_border, 1.15))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect, 6.5, 6.5)
        painter.setPen(QPen(self.separator_color, self.separator_width))
        y = option.rect.bottom()
        inset = self.separator_inset
        if self.viewport().width() > 2 * inset:
            painter.drawLine(QPointF(inset, y),
                             QPointF(self.viewport().width() - inset - 1, y))
        painter.restore()


class _BreadcrumbSurface(QFrame):
    """Click the blank part of the address bar to reveal the full path."""
    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self.setObjectName('addressBreadcrumbSurface')

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.owner.begin_edit()
            event.accept()
            return
        super().mousePressEvent(event)


class DirectoryAddressBar(QStackedWidget):
    """Explorer-like clickable ancestors ↔ selected editable absolute path."""
    def __init__(self, navigate, parent=None):
        super().__init__(parent)
        self.setObjectName('directoryAddressBar')
        self.navigate = navigate
        self.current_path = ''
        self._segments = []
        self._scheduled = False
        self.surface = _BreadcrumbSurface(self)
        self.crumb_layout = QHBoxLayout(self.surface)
        self.crumb_layout.setContentsMargins(4, 1, 64, 1)
        self.crumb_layout.setSpacing(1)
        self.addWidget(self.surface)
        self.editor = QLineEdit(self)
        self.editor.setObjectName('directoryAddressEdit')
        self.editor.setToolTip('Enterでフォルダーへ移動・Escでキャンセル')
        self.editor.returnPressed.connect(self._submit)
        self.editor.installEventFilter(self)
        self.addWidget(self.editor)
        self.setMinimumWidth(75)
        self.setCurrentWidget(self.surface)
        self._overlay_dropdown = None
        self._overlay_favorite = None

    def attach_history_dropdown(self, button):
        """Attach a search-style history chevron to the breadcrumb's own frame.

        It remains in place for both breadcrumb and editable-path views.
        """
        self._overlay_dropdown = button
        button.setParent(self)
        button.setFixedSize(24, 26)
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        button.setIconSize(QSize(14, 14))
        self.editor.setTextMargins(0, 0, 60, 0)
        self._position_dropdown()
        button.show()
        button.raise_()
        self._build_crumbs()

    def attach_favorite_save(self, button):
        """Place register/registered heart inside the same address frame."""
        self._overlay_favorite = button
        button.setParent(self)
        button.setFixedSize(27, 26)
        self._position_dropdown()
        button.show()
        self._build_crumbs()

    def _position_dropdown(self):
        combo = self._overlay_dropdown
        favorite = self._overlay_favorite
        if combo is not None:
            combo.move(max(0, self.width() - combo.width() - 4),
                       max(0, (self.height() - combo.height()) // 2))
        if favorite is not None:
            combo_start = combo.x() if combo is not None else self.width() - 28
            favorite.move(max(0, combo_start - favorite.width() - 3),
                          max(0, (self.height() - favorite.height()) // 2))
            favorite.raise_()
        if combo is not None:
            combo.raise_()

    def sizeHint(self):
        # A long path must never expand the whole splitter beyond its width.
        return QSize(185, 31)

    def minimumSizeHint(self):
        return QSize(75, 31)

    def set_directory(self, path, label=''):
        self.current_path = normalized_directory(path) or ''
        self._segments = breadcrumb_segments(self.current_path)
        self._fallback_label = label or 'フォルダーを選択'
        if self.currentWidget() is self.editor:
            self.show_breadcrumbs()
        self._build_crumbs()
        self.setToolTip(self.current_path or self._fallback_label)

    def begin_edit(self):
        if not self.current_path:
            return
        self.editor.setText(self.current_path)
        self.setCurrentWidget(self.editor)
        self._position_dropdown()
        self.editor.setFocus(Qt.FocusReason.MouseFocusReason)
        # Mouse event completion otherwise can reset QLineEdit's selection.
        QTimer.singleShot(0, self.editor.selectAll)

    def show_breadcrumbs(self):
        self.setCurrentWidget(self.surface)
        self._build_crumbs()
        self._position_dropdown()

    def _submit(self):
        target = normalized_directory(self.editor.text())
        if target and self.navigate(target):
            self.show_breadcrumbs()
        else:
            self.editor.selectAll()
            self.editor.setToolTip('存在する絶対フォルダーパスを入力してください')

    def eventFilter(self, obj, event):
        if obj is self.editor:
            if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
                self.show_breadcrumbs()
                event.accept()
                return True
            if event.type() == QEvent.Type.FocusOut:
                QTimer.singleShot(0, self.show_breadcrumbs)
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_dropdown()
        if not self._scheduled:
            self._scheduled = True
            QTimer.singleShot(0, self._rebuild_after_resize)

    def _rebuild_after_resize(self):
        self._scheduled = False
        self._build_crumbs()

    def _show_hidden(self, button, entries):
        menu = QMenu(button)
        for label, directory in entries:
            action = menu.addAction(label)
            action.setToolTip(directory)
            action.triggered.connect(lambda checked=False, p=directory: self.navigate(p))
        menu.exec(button.mapToGlobal(QPoint(0, button.height())))

    def _build_crumbs(self):
        while self.crumb_layout.count():
            cell = self.crumb_layout.takeAt(0)
            if cell.widget():
                cell.widget().deleteLater()
        if not self._segments:
            placeholder = QLabel(getattr(self, '_fallback_label', 'フォルダーを選択'), self.surface)
            placeholder.setObjectName('addressPlaceholder')
            placeholder.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.crumb_layout.addWidget(placeholder)
            self.crumb_layout.addStretch()
            return
        fm = self.fontMetrics()
        def measure(label):
            return fm.horizontalAdvance(label) + (12 if label != ' › ' else 6)
        # Reserve space for the inside heart + dropdown (also in edit mode).
        segments = compact_segments(self._segments, self.width() - 18 - 64, measure)
        for index, (label, path) in enumerate(segments):
            if index:
                sep = QLabel('›', self.surface)
                sep.setObjectName('addressSeparator')
                sep.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                self.crumb_layout.addWidget(sep)
            if path is None:
                # Explorer-style overflow menu: omitted ancestors remain
                # clickable instead of turning into unreachable text.
                segment = QToolButton(self.surface)
                segment.setObjectName('addressCrumb')
                segment.setText('…')
                segment.setToolTip('省略された上位フォルダーを表示')
                segment.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                visible = {p for _, p in segments if p is not None}
                hidden = [(text, p) for text, p in self._segments if p not in visible]
                segment.clicked.connect(
                    lambda checked=False, btn=segment, entries=hidden:
                    self._show_hidden(btn, entries))
            else:
                segment = QToolButton(self.surface)
                segment.setObjectName('addressCrumb')
                segment.setText(label)
                segment.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                segment.setToolTip(path)
                if path == self.current_path:
                    # Current folder is already open: clicking it edits the path.
                    # This guarantees an editable hit target even when no blank
                    # header space survives in a narrow middle panel.
                    segment.clicked.connect(self.begin_edit)
                else:
                    segment.clicked.connect(lambda checked=False, p=path: self.navigate(p))
            self.crumb_layout.addWidget(segment)
        self.crumb_layout.addStretch()



class ExpandedPanel(QFrame):
    def __init__(self, label, kind):
        super().__init__()
        self.setObjectName('expandedPanel')
        self.kind = kind
        self._theme = 'light'
        self.row_height = 37
        self.setMinimumWidth(190)
        self.layout_box = QVBoxLayout(self)
        self.layout_box.setContentsMargins(0, 0, 0, 0)
        self.layout_box.setSpacing(0)
        self.header = QWidget()
        self.header.setObjectName('expandedHeader')
        header = QHBoxLayout(self.header)
        header.setContentsMargins(12, 6, 10, 6)
        header.setSpacing(8)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(28, 28)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(self.icon_label)
        self.label = QLabel(label)
        self.label.setObjectName('expandedTitle')
        header.addWidget(self.label, 1)
        self.back = QPushButton('')
        self.back.setObjectName('expandedBack')
        self.back.setFixedSize(34, 34)
        self.back.setIconSize(QSize(22, 22))
        self.back.setToolTip('一つ上の階層へ戻る')
        self.back.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.back.setIcon(browser_navigation_icon('back', self._theme))
        header.addWidget(self.back)
        self.back.hide()
        self.layout_box.addWidget(self.header)
        self.tree = _SeparatedFileTree(self)
        self.tree.setObjectName('expandedTree')
        # A real trailing column anchors every navigation chevron to the right.
        self.tree.setColumnCount(2)
        self.tree.header().setStretchLastSection(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.tree.setColumnWidth(1, 40)
        self.tree.setItemDelegateForColumn(1, _NavigationChevronDelegate(self.tree))
        if kind == 'folder':
            self.tree.setItemDelegateForColumn(0, _InlineRenameDelegate(self.tree))
        self.tree.setHeaderHidden(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setIndentation(0)
        self.tree.setSortingEnabled(False)
        self.tree.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tree.verticalScrollBar().setSingleStep(35)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tree.setMouseTracking(True)
        self.tree.setIconSize(QSize(19, 19))
        self.layout_box.addWidget(self.tree, 1)

    def fill(self, rows, icon_resolver):
        prior = self.tree.currentItem()
        current_id = prior.data(0, Qt.ItemDataRole.UserRole).get('item_id') if prior else None
        self.tree.clear()
        for row in rows:
            is_folder = row.get('item_kind') in ('category', 'directory')
            item = QTreeWidgetItem([row.get('title', ''), ''])
            item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item.setData(1, Qt.ItemDataRole.UserRole, is_folder)
            for col in (0, 1):
                item.setSizeHint(col, QSize(0, self.row_height))
            item.setData(0, Qt.ItemDataRole.UserRole, row)
            if self.kind == 'folder':
                # Middle panel filenames can be edited by clicking the already
                # selected row. Directory single click still means navigation.
                origin, path = resolve_context_target(row, ())
                if origin == 'file' and path:
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            if (self.kind == 'bookmark'
                    and row.get('item_kind') not in ('category', 'directory')):
                item.setIcon(0, link_icon(self._theme))
            else:
                item.setIcon(0, icon_resolver(row))
            item.setToolTip(0, row.get('description') or row.get('title', ''))
            self.tree.addTopLevelItem(item)
            if current_id == row.get('item_id'):
                self.tree.setCurrentItem(item)
        if self.tree.topLevelItemCount() and self.tree.currentItem() is None:
            self.tree.setCurrentItem(self.tree.topLevelItem(0))


class ExpandedLauncherView(QWidget):
    """Work Page: root toolbar + Files + active directory + bookmarks.

    Single-clicking a Files directory browses in the middle column; repeated
    clicks in the middle browse deeper.  Back goes up one directory. Other
    folder/bookmark categories use the existing cascade widget and logic.
    """
    def __init__(self, launcher):
        super().__init__(launcher)
        self.launcher = launcher
        self.options = None
        self.root_rows = []
        self.root_buttons = []
        self._wheel_root_id = None
        self._wheel_root_delta = 0
        self._wheel_back_delta = 0
        self._reverse_zone_entry = False
        self._wheel_files_delta = 0
        self._files_first_wan_enabled = True
        self._files_edge_follow_active = False
        self._files_scroll_hover_scheduled = False
        self._files_follow_pending = None
        self._files_follow_scheduled = False
        self._files_warp_global = None
        self._wheel_root_follow_pending = None
        self._wheel_root_follow_scheduled = False
        self._wheel_bookmark_delta = 0
        self._bookmark_edge_follow_active = False
        self._bookmark_scroll_hover_scheduled = False
        self._bookmark_hover_item = None
        self._wheel_middle_delta = 0
        self._middle_follow_pending = None
        self._middle_follow_scheduled = False
        self._middle_warp_global = None
        self._middle_back_hold = EdgeWheelHold()
        self.wheel_zone_navigation = WheelZoneNavigation()
        self._favorite_popup_wheel_delta = 0
        self._favorite_popup_warp_generation = 0
        self._favorite_path_wheel_delta = 0
        self._middle_back_warp_pending = None
        self._bookmark_follow_pending = None
        self._bookmark_follow_scheduled = False
        self._bookmark_warp_global = None
        self.files_root = None
        self.bookmarks_root = None
        self.path = []
        self._refreshing = False
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)
        self.toolbar_scroller = QScrollArea(self)
        self.toolbar_scroller.setObjectName('expandedRootScroller')
        self.toolbar_scroller.setWidgetResizable(True)
        self.toolbar_scroller.setFixedHeight(47)
        self.toolbar_scroller.setFrameShape(QFrame.Shape.NoFrame)
        self.toolbar_scroller.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.toolbar_scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.root_widget = QWidget()
        self.root_widget.setObjectName('expandedRootBar')
        self.root_layout = QHBoxLayout(self.root_widget)
        self.root_layout.setContentsMargins(4, 2, 4, 2)
        self.root_layout.setSpacing(5)
        self.toolbar_scroller.setWidget(self.root_widget)
        # Catch wheel gestures on buttons AND on the whitespace in the strip.
        # This has no effect on the Page tab bar or the file-list scrollbars.
        for source in (self.root_widget, self.toolbar_scroller.viewport(),
                       self.toolbar_scroller):
            source.installEventFilter(self)
        outer.addWidget(self.toolbar_scroller)
        # Shared Explorer header sits ACROSS Files and directory; only the
        # content below is divided. The bookmark panel stays independent.
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.setObjectName('expandedSplitter')
        self.files_group = QFrame(self.splitter)
        self.files_group.setObjectName('expandedFilesGroup')
        group_layout = QVBoxLayout(self.files_group)
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(0)
        self.shared_header = QWidget(self.files_group)
        self.shared_header.setObjectName('expandedCombinedHeader')
        shared_layout = QHBoxLayout(self.shared_header)
        shared_layout.setContentsMargins(12, 6, 10, 6)
        shared_layout.setSpacing(8)
        self.shared_icon = QLabel(self.shared_header)
        self.shared_icon.setFixedSize(28, 28)
        shared_layout.addWidget(self.shared_icon)
        self.shared_title = QLabel('Files', self.shared_header)
        self.shared_title.setObjectName('expandedCombinedTitle')
        shared_layout.addWidget(self.shared_title)
        self.density_button = QToolButton(self.shared_header)
        self.density_button.setObjectName('expandedDensityToggle')
        self.density_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.density_button.setFixedSize(31, 31)
        self.density_button.setIconSize(QSize(22, 22))
        self.density_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.density_button.clicked.connect(self.toggle_row_density)
        shared_layout.addWidget(self.density_button)
        self.address_bar = DirectoryAddressBar(self.go_to_directory, self.shared_header)
        shared_layout.addWidget(self.address_bar, 1)
        # Ad-hoc work-directory favorites stay outside the authored Launch JSON.
        from os import environ
        self.folder_favorites = FolderFavorites(
            Path(environ.get('LOCALAPPDATA', str(Path.home()))) / 'FRBLaunch' / 'folder_favorites.json')
        self.favorite_save = QToolButton(self.address_bar)
        self.favorite_save.setObjectName('expandedFavoriteSave')
        self.favorite_save.setText('💛')
        self.favorite_save.setToolTip('今表示しているフォルダーをお気に入りに登録')
        self.favorite_save.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.favorite_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.favorite_save.clicked.connect(self.register_directory_favorite)
        self.favorite_dropdown = QToolButton(self.address_bar)
        self.favorite_dropdown.setObjectName('expandedFavoriteDropdown')
        self.favorite_dropdown.setText('')
        self.favorite_dropdown.setIcon(combo_chevron_icon(self.launcher.color_theme))
        self.favorite_dropdown.setToolTip('作業フォルダーのお気に入り一覧')
        self.favorite_dropdown.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.favorite_dropdown.setCursor(Qt.CursorShape.PointingHandCursor)
        self.favorite_dropdown.clicked.connect(self.toggle_directory_favorites)
        self.address_bar.attach_history_dropdown(self.favorite_dropdown)
        self.address_bar.attach_favorite_save(self.favorite_save)
        self.favorite_popup = QFrame(self.launcher)
        self.favorite_popup.setObjectName('expandedFavoritesPopup')
        favorite_layout = QVBoxLayout(self.favorite_popup)
        favorite_layout.setContentsMargins(5, 5, 5, 5)
        favorite_layout.setSpacing(0)
        self.favorite_choices = ReorderablePopupTree(self.favorite_popup)
        self.favorite_choices.setObjectName('expandedFavoritesChoices')
        self.favorite_choices.setColumnCount(2)
        self.favorite_choices.setHeaderHidden(True)
        self.favorite_choices.setRootIsDecorated(False)
        self.favorite_choices.setIndentation(0)
        self.favorite_choices.setSortingEnabled(False)
        self.favorite_choices.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.favorite_choices.header().setStretchLastSection(False)
        self.favorite_choices.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.favorite_choices.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.favorite_choices.setColumnWidth(1, 34)
        self.favorite_choices.setIconSize(QSize(19, 19))
        self.favorite_choices.itemClicked.connect(self.directory_favorite_clicked)
        self.favorite_choices.orderChanged.connect(self.directory_favorites_reordered)
        self.favorite_choices.installEventFilter(self)
        self.favorite_choices.viewport().installEventFilter(self)
        favorite_layout.addWidget(self.favorite_choices)
        self.favorite_popup.hide()
        QApplication.instance().installEventFilter(self)
        self.left = ExpandedPanel('Files', 'folder')
        self.middle = ExpandedPanel('フォルダー', 'folder')
        # Separate a real 24px Back lane OUTSIDE the QTreeWidget viewport.
        # Qt's current-row rectangle therefore cannot extend into the lane,
        # and neither click nor inline rename can land on a hidden row cell.
        self.middle_tree_container = QWidget(self.middle)
        self.middle_tree_container.setObjectName('expandedMiddleTreeContainer')
        middle_tree_layout = QHBoxLayout(self.middle_tree_container)
        middle_tree_layout.setContentsMargins(0, 0, 0, 0)
        middle_tree_layout.setSpacing(0)
        self.middle.layout_box.removeWidget(self.middle.tree)
        self.middle.tree.setParent(self.middle_tree_container)
        middle_tree_layout.addWidget(self.middle.tree, 1)
        self.middle_back_lane = QFrame(self.middle_tree_container)
        self.middle_back_lane.setObjectName('expandedBackLane')
        self.middle_back_lane.setFixedWidth(MIDDLE_BACK_LANE_WIDTH)
        self.middle_back_lane.setToolTip('ダブルクリックで一つ上のフォルダーへ')
        self.middle_back_lane.installEventFilter(self)
        middle_tree_layout.addWidget(self.middle_back_lane)
        self.middle.layout_box.addWidget(self.middle_tree_container, 1)
        # Only the directory-content column is multi-select. Qt supplies
        # Ctrl+click, Shift+click, Ctrl+A, and Shift+Up/Down natively.
        self.middle.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        # WAN: only this pane measures actual native scroll movement before
        # using wheel steps to move the current row and the mouse cursor.
        self.middle.tree.adaptive_wheel_callback = self.wheel_middle_at_edge
        # The header Back button is an explicit, non-scrolling Wheel Tab zone.
        # Never synthesize its click; a sustained UP gesture goes to Files last.
        self.middle.back.installEventFilter(self)
        # WAN for Files first column: native scrolling first, then select and
        # follow at the relevant edge (also when all rows fit on screen).
        # The older wheel_files_first_column remains as a safe rollback path.
        self.left.tree.adaptive_wheel_callback = self.wheel_files_at_edge
        self.left.tree.installEventFilter(self)
        self.left.tree.viewport().installEventFilter(self)
        self.left.header.hide()
        self.middle.header.hide()
        # Reuse the old Back button/signal, but position it in the shared header.
        self.middle.header.layout().removeWidget(self.middle.back)
        self.middle.back.setParent(self.shared_header)
        shared_layout.addWidget(self.middle.back)
        self.middle.back.show()
        # Unlike mouse-only Back, Wheel Tab must visibly LAND with keyboard
        # focus on this button. The other pane Back buttons stay unchanged.
        self.middle.back.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        group_layout.addWidget(self.shared_header)
        self.files_splitter = QSplitter(Qt.Orientation.Horizontal, self.files_group)
        self.files_splitter.setObjectName('expandedFilesSplitter')
        self.files_splitter.addWidget(self.left)
        self.files_splitter.addWidget(self.middle)
        self.files_splitter.setChildrenCollapsible(False)
        group_layout.addWidget(self.files_splitter, 1)
        self.right = ExpandedPanel('ブックマーク', 'bookmark')
        # Bookmarks first level is also a wheel-driven selector.  Only the
        # tree/viewport are hooked: scrollbar dragging and deeper tool
        # columns continue to use their original native behavior.
        self.right.tree.installEventFilter(self)
        self.right.tree.viewport().installEventFilter(self)
        # WAN is opt-in per Bookmarks: use native scrolling first, then cursor
        # follow only when the wheel cannot move the scrollbar any farther.
        self.right.tree.adaptive_wheel_callback = (
            self.wheel_bookmarks_at_edge
            if getattr(self.launcher, 'bookmark_wan_enabled', True) else None)
        self._bookmark_hover_timer = QTimer(self)
        self._bookmark_hover_timer.setSingleShot(True)
        self._bookmark_hover_timer.timeout.connect(self.open_bookmark_hover)
        self.right.tree.itemEntered.connect(self.hover_bookmark_first_level)
        self.splitter.addWidget(self.files_group)
        self.splitter.addWidget(self.right)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setSizes([660, 350])
        self.files_splitter.setSizes([310, 350])
        # Compatible with the legacy saved 3-column sizes.
        saved = str(launcher.settings.value('expanded_splitter_sizes', '') or '')
        try:
            values = [int(value) for value in saved.split('|')]
            if len(values) == 3 and all(value >= 100 for value in values):
                self.splitter.setSizes([values[0] + values[1], values[2]])
                self.files_splitter.setSizes(values[:2])
        except ValueError:
            pass
        self.splitter.splitterMoved.connect(self.save_splitter_sizes)
        self.files_splitter.splitterMoved.connect(self.save_splitter_sizes)
        outer.addWidget(self.splitter, 1)
        self.row_density = str(launcher.settings.value('expanded_row_density', 'normal') or 'normal')
        if self.row_density not in ('normal', 'compact'):
            self.row_density = 'normal'
        # Only the middle panel enables Explorer-like edit-on-selected-click.
        # Double-click/Right-arrow navigation remain unchanged.
        self.middle.tree.setEditTriggers(QAbstractItemView.EditTrigger.SelectedClicked)
        self.middle.tree.itemChanged.connect(self.finish_inline_rename)
        self._inline_rename_active = False
        self.middle.back.clicked.connect(self.go_up)
        self.left.tree.itemClicked.connect(self.choose_files)
        self.middle.tree.itemClicked.connect(self.choose_middle)
        self.right.tree.itemClicked.connect(self.choose_bookmark)
        for panel in (self.left, self.middle, self.right):
            panel.tree.itemActivated.connect(lambda item, col, pane=panel: self.activate_row(pane, item))
            panel.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            panel.tree.customContextMenuRequested.connect(lambda point, pane=panel:
                self.context_menu(pane, point))
        self.apply_theme('light')

    def save_splitter_sizes(self, *_):
        widths = self.files_splitter.sizes() + self.splitter.sizes()[1:]
        self.launcher.settings.setValue('expanded_splitter_sizes',
                                        '|'.join(map(str, widths)))

    def toggle_row_density(self):
        self.row_density = 'compact' if self.row_density == 'normal' else 'normal'
        self.launcher.settings.setValue('expanded_row_density', self.row_density)
        self.launcher.settings.sync()
        self.apply_theme(self.launcher.color_theme)

    def apply_theme(self, theme):
        colors = theme_palette(theme)
        light = theme_family(theme) == 'light'
        bg, border, hdr, text, hover, active, stripe = (
            colors[key] for key in ('panel', 'panel_border', 'panel_header',
                                   'text', 'hover', 'selection', 'stripe'))
        root_border = colors['root_button_border']
        tight = self.row_density == 'compact'
        height, pad = (23, 1) if tight else (29, 3)
        self.density_button.setText('')
        self.density_button.setIcon(density_lines_icon(theme_family(theme)))
        self.density_button.setToolTip('行間隔：コンパクト（クリックで切替）' if not tight
                                       else '行間隔：標準（クリックで切替）')
        for pane in (self.left, self.middle, self.right):
            pane.tree.separator_color = QColor(colors['row_separator'])
            pane.tree.inactive_current_border = QColor(colors['focus_outline'])
            for bar in (pane.tree.verticalScrollBar(), pane.tree.horizontalScrollBar()):
                bar.setStyleSheet(scrollbar_for_theme(theme, bg))
            pane.tree.viewport().update()
        for bar in (self.favorite_choices.verticalScrollBar(),
                    self.favorite_choices.horizontalScrollBar()):
            bar.setStyleSheet(scrollbar_for_theme(theme, colors['history_bg']))
        self.setStyleSheet(f'''
            QWidget#expandedRootBar {{ background:transparent; }}
            QScrollArea#expandedRootScroller {{ background:transparent;border:0; }}
            QPushButton#expandedRootButton {{ background:{hdr};color:{text};border:1px solid {root_border};
                border-radius:9px;padding:6px 10px;text-align:left;font-size:12px; }}
            QPushButton#expandedRootButton:hover {{background:{hover};}}
            QPushButton#expandedRootButton:checked {{background:{active};border:1px solid #81bca4;font-weight:600;}}
            QPushButton#expandedRootButton:focus {{border:2px solid #56a88c;background:{active};}}
            QFrame#expandedFilesGroup {{background:{bg};border:1px solid {border};border-radius:12px;}}
            QWidget#expandedCombinedHeader {{background:{hdr};border:0;border-bottom:1px solid {border};
                border-top-left-radius:11px;border-top-right-radius:11px;}}
            QLabel#expandedCombinedTitle {{background:transparent;border:0;color:{text};font-size:15px;font-weight:600;}}
            QToolButton#expandedDensityToggle {{background:transparent;border:1px solid {border};
                border-radius:7px;color:{text};font-size:17px;}}
            QToolButton#expandedDensityToggle:hover {{background:{hover};}}
            QFrame#expandedPanel {{ background:{bg}; border:1px solid {border};border-radius:12px; }}
            QWidget#expandedHeader {{background:{hdr};border:0;border-bottom:1px solid {border};
                border-top-left-radius:11px;border-top-right-radius:11px;}}
            QLabel#expandedTitle {{background:transparent;border:0;color:{text};font-size:15px;font-weight:600;}}
            QPushButton#expandedBack {{background:{hdr};border:1px solid {border};color:{text};border-radius:9px;padding:0;}}
            QPushButton#expandedBack:hover {{background:{hover};border-radius:9px;}}
            QPushButton#expandedBack:pressed {{background:{active};border-radius:9px;}}
            QWidget#expandedMiddleTreeContainer {{background:{bg};border:0;}}
            QFrame#expandedBackLane {{background:{bg};border:0;border-left:1px solid {border};}}
            QTreeWidget#expandedTree {{background:{bg};color:{text};border:0;outline:0;}}
            QTreeWidget#expandedTree::item {{min-height:{height}px;padding:{pad}px 7px;border:0;}}
            QTreeWidget#expandedTree::item:hover {{background:{hover};}}
            QTreeWidget#expandedTree::item:selected {{background:{active};color:{text};}}
            QTreeWidget#expandedTree::item:selected:!active {{background:transparent;color:{text};}}
        ''')
        self.address_bar.setStyleSheet(f'''
            QFrame#addressBreadcrumbSurface {{border:1px solid {border};border-radius:17px;background:{bg};}}
            QToolButton#addressCrumb {{border:0;background:transparent;color:{text};padding:2px 3px;}}
            QToolButton#addressCrumb:hover {{background:{active};border-radius:4px;}}
            QLabel#addressSeparator {{border:0;color:{text};background:transparent;padding:0 2px;}}
            QLabel#addressPlaceholder {{border:0;color:{text};background:transparent;}}
            QLineEdit#directoryAddressEdit {{background:{bg};color:{text};border:1px solid #55a38c;
                border-bottom:2px solid #167f72;border-radius:17px;padding:3px 5px;selection-background-color:#138c8d;
                selection-color:white;}}
        ''')
        self.favorite_popup.setStyleSheet(history_popup_qss(
            theme, frame_name='expandedFavoritesPopup',
            tree_name='expandedFavoritesChoices', height=30, padding=5))
        self.favorite_save.setStyleSheet(f'''
            QToolButton#expandedFavoriteSave {{color:{text};background:transparent;border:0;
                border-radius:6px;padding:0;font-size:14px;}}
            QToolButton#expandedFavoriteSave:hover {{background:{hover};}}
        ''')
        self.favorite_dropdown.setStyleSheet(f'''
            QToolButton#expandedFavoriteDropdown {{color:{text};background:transparent;border:0;
                border-radius:5px;padding:0;}}
            QToolButton#expandedFavoriteDropdown:hover {{background:{hover};}}
        ''')
        self.favorite_dropdown.setIcon(combo_chevron_icon(theme_family(theme)))
        self.address_bar._position_dropdown()
        self.shared_icon.setPixmap(header_icon('folder', theme_family(theme)).pixmap(28, 28))
        if self.bookmarks_root is not None:
            for index, root in enumerate(self.root_rows):
                if root.get('item_id') == self.bookmarks_root.get('item_id'):
                    self.root_buttons[index].setIcon(header_icon('bookmark', theme_family(theme)))
        for pane in (self.left, self.middle, self.right):
            pane.back.setIcon(browser_navigation_icon('back', theme_family(theme)))
            pane.tree.verticalScrollBar().setSingleStep(26 if tight else 35)
            pane.row_height = 27 if tight else 37
            for row_index in range(pane.tree.topLevelItemCount()):
                item = pane.tree.topLevelItem(row_index)
                for column in (0, 1):
                    item.setSizeHint(column, QSize(0, pane.row_height))
            pane._theme = theme
            if pane.kind == 'bookmark':
                for i in range(pane.tree.topLevelItemCount()):
                    item = pane.tree.topLevelItem(i)
                    row = item.data(0, Qt.ItemDataRole.UserRole)
                    if row and row.get('item_kind') not in ('category', 'directory'):
                        item.setIcon(0, link_icon(theme_family(theme)))
            # Ribbon appears visually larger than Files' green folder at 28px.
            pane.icon_label.setPixmap(header_icon(pane.kind, theme_family(theme)).pixmap(
                24 if pane.kind == 'bookmark' else 28,
                24 if pane.kind == 'bookmark' else 28))

    def browser_rows(self, parent):
        """Resolve dynamic 'This PC' drives only in the expanded Files pane."""
        if parent.get('_system_drives_root'):
            return drive_rows()
        rows = self.launcher.displayed_children(parent)
        if self.files_root and parent.get('item_id') == self.files_root.get('item_id'):
            return [pc_preview_row(row) for row in rows]
        return rows

    def refresh(self, roots, left, right, options):
        if self._refreshing:
            return
        self._refreshing = True
        try:
            self.options = options
            self.root_buttons = []
            # Cancel a pending warp targeting a button about to be replaced.
            self._wheel_root_follow_pending = None
            # Do not alter Launch DataJSON: the two permanent panel roots are
            # simply not duplicated as buttons in this expanded-view toolbar.
            visible_roots = toolbar_roots(roots, left, right)
            self.root_rows, self.files_root, self.bookmarks_root = visible_roots, left, right
            if self._wheel_root_id not in {row.get('item_id') for row in visible_roots}:
                self._wheel_root_id = None
            self._wheel_root_delta = 0
            self._wheel_bookmark_delta = 0
            self.cancel_bookmark_pointer_follow()
            self.cancel_bookmark_hover()
            while self.root_layout.count():
                item = self.root_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            for index, row in enumerate(visible_roots):
                button = QPushButton(row.get('title', ''), self.root_widget)
                button.setObjectName('expandedRootButton')
                button.setCheckable(True)
                button.setChecked(row.get('item_id') == self._wheel_root_id)
                button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                button.installEventFilter(self.launcher)
                button.installEventFilter(self)
                button.setIcon(header_icon('bookmark', self.launcher.color_theme)
                               if row.get('item_id') == right['item_id'] else self.launcher.row_icon(row))
                # The short ZIP label clips when the focus outline grows from
                # 1px to 2px and the checked button switches to a bold font.
                # Reserve a few extra pixels for ZIP only; other roots keep
                # their original natural widths.
                if row.get('title') == 'ZIP':
                    button.setMinimumWidth(button.sizeHint().width() + 10)
                hint = f'Ctrl+F{index+1}' if index < 12 else ''
                button.setToolTip((' / '.join(v for v in (row.get('description', ''), hint) if v)))
                button.clicked.connect(lambda checked=False, r=row, b=button: self.root_action(r, b))
                self.root_layout.addWidget(button)
                self.root_buttons.append(button)
            self.root_layout.addStretch()
            self.left.label.setText(left['title'])
            self.shared_title.setText(left['title'])
            self.right.label.setText(right['title'])
            files_rows = self.browser_rows(left)
            self.left.fill(files_rows, self.launcher.row_icon)
            self.right.fill(self.launcher.displayed_children(right), self.launcher.row_icon)
            # Start with one real folder in the middle, never invented PC data.
            if not self.path:
                initial = next((row for row in files_rows
                                if row.get('item_kind') in ('category', 'directory')), None)
                if initial:
                    self.path = [initial]
                    for index in range(self.left.tree.topLevelItemCount()):
                        item = self.left.tree.topLevelItem(index)
                        if item.data(0, Qt.ItemDataRole.UserRole).get('item_id') == initial.get('item_id'):
                            self.left.tree.setCurrentItem(item)
                            break
            # Data may have been reloaded; re-resolve every directory in the path.
            updated = []
            for old in self.path:
                if old.get('_address_synthetic'):
                    import os
                    actual = row_directory(old)
                    if not actual or not os.path.isdir(actual):
                        break
                    updated.append(directory_row(actual))
                    continue
                parent = updated[-1] if updated else left
                matching = next((r for r in self.browser_rows(parent)
                                 if r.get('item_id') == old.get('item_id')), None)
                if matching is None:
                    break
                updated.append(matching)
            self.path = updated
            self.refresh_middle()
        finally:
            self._refreshing = False

    def refresh_middle(self):
        self._middle_back_hold.reset()
        self._middle_back_warp_pending = None
        current = self.path[-1] if self.path else None
        self.middle.label.setText(current['title'] if current else 'フォルダーを選択')
        self.address_bar.set_directory(
            row_directory(current, self.launcher.expander().expand),
            current['title'] if current else '')
        self.middle.back.setEnabled(bool(self.path))
        if current:
            try:
                rows = self.browser_rows(current)
            except (OSError, ValueError, PermissionError) as exc:
                rows = []
                self.middle.label.setToolTip(str(exc))
            self.middle.fill(rows, self.launcher.row_icon)
        else:
            self.middle.tree.clear()
        self.update_directory_favorite_button()

    def update_directory_favorite_button(self):
        target = self.current_directory()
        import ntpath
        registered = bool(target and any(ntpath.normcase(p) == ntpath.normcase(target)
                        for p in self.folder_favorites.paths))
        self.favorite_save.setText('🩶' if registered else '💛')
        self.favorite_save.setToolTip('お気に入り登録済み' if registered else '今のフォルダーをお気に入りに登録')
        self.favorite_save.setEnabled(bool(target))
        self.favorite_dropdown.setEnabled(bool(self.folder_favorites.paths))
        self.favorite_dropdown.setToolTip(
            f'お気に入りフォルダーを選択（{len(self.folder_favorites.paths)}件）')

    def register_directory_favorite(self):
        target = self.current_directory()
        if not target:
            return
        try:
            self.folder_favorites.add(target)
        except OSError:
            self.launcher.error('お気に入りの保存に失敗しました')
            return
        self.update_directory_favorite_button()
        if self.favorite_popup.isVisible():
            self.populate_directory_favorites(target)

    def populate_directory_favorites(self, selected=None):
        self.favorite_choices.blockSignals(True)
        self.favorite_choices.clear()
        for path in self.folder_favorites.paths:
            row = QTreeWidgetItem([path, '×'])
            row.setIcon(0, self.launcher.file_icons.icon(QFileIconProvider.IconType.Folder))
            row.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
            row.setToolTip(0, path + '  — クリックでLaunch内のフォルダーへ移動／ドラッグで並び替え')
            row.setToolTip(1, 'お気に入りを削除（実フォルダーは削除されません）')
            self.favorite_choices.addTopLevelItem(row)
            if path == selected:
                self.favorite_choices.setCurrentItem(row)
        if self.favorite_choices.topLevelItemCount() and self.favorite_choices.currentItem() is None:
            self.favorite_choices.setCurrentItem(self.favorite_choices.topLevelItem(0))
        self.favorite_choices.blockSignals(False)

    def position_directory_favorites(self):
        # Same left edge and width as the breadcrumb input, not the ▼ button.
        anchor = self.address_bar.mapTo(self.launcher, QPoint(0, self.address_bar.height() + 4))
        width = min(self.address_bar.width(), max(1, self.launcher.width() - 12))
        x = max(6, min(anchor.x(), self.launcher.width() - width - 6))
        y = anchor.y()
        # Allow ~2x the old popup height, with a generous minimum when saved
        # favorites exist; keep the popup completely inside the launcher.
        desired_height = max(180, min(600, (len(self.folder_favorites.paths) * 31 + 12) * 2))
        height = max(1, min(desired_height, self.launcher.height() - y - 12))
        self.favorite_popup.setGeometry(x, y, width, height)

    def wheel_directory_favorite_history(self, obj, event):
        """Browse favorite popup rows, or preview a path inside the address edit.

        Browsing must NEVER change folders. Click a popup item or press Enter
        in the address editor to navigate; Escape abandons a preview.
        """
        if (event.modifiers() != Qt.KeyboardModifier.NoModifier or
                QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return False
        choices = self.favorite_choices
        bar = self.address_bar
        in_address = (obj is bar or obj is bar.editor or obj is bar.surface or
                      (isinstance(obj, QWidget) and
                       bar.isAncestorOf(obj) and obj not in (
                           self.favorite_save, self.favorite_dropdown)))
        in_popup = (self.favorite_popup.isVisible() and
                    (obj in (choices, choices.viewport()) or in_address))
        if not in_popup and not in_address:
            return False
        if in_popup:
            pending, steps = wheel_steps(self._favorite_popup_wheel_delta,
                                         event.angleDelta().y(), event.pixelDelta().y())
            self._favorite_popup_wheel_delta = pending
            if not steps:
                return True
            count = choices.topLevelItemCount()
            if not count:
                return True
            index = history_target_index(choices.indexOfTopLevelItem(choices.currentItem()),
                                         count, steps)
            target = choices.topLevelItem(index)
            choices.setCurrentItem(target)
            choices.scrollToItem(target, QAbstractItemView.ScrollHint.EnsureVisible)
            origin = QCursor.pos()
            self._favorite_popup_warp_generation += 1
            generation = self._favorite_popup_warp_generation
            QTimer.singleShot(0, lambda: (
                warp_to_history_row(choices, target, origin, QCursor)
                if generation == self._favorite_popup_warp_generation else None))
            return True
        if self.favorite_popup.isVisible():
            # An open list owns its own wheel; clicking its choices navigates.
            return False
        paths = self.folder_favorites.paths
        if not paths:
            return False
        pending, steps = wheel_steps(self._favorite_path_wheel_delta,
                                     event.angleDelta().y(), event.pixelDelta().y())
        self._favorite_path_wheel_delta = pending
        if not steps:
            return True
        # Preview one favorite path per notch without activating it.
        current = bar.editor.text() if bar.currentWidget() is bar.editor else bar.current_path
        import ntpath
        found = next((i for i, path in enumerate(paths)
                      if ntpath.normcase(path) == ntpath.normcase(current)), None)
        index = (found + steps) % len(paths) if found is not None else (
            0 if steps > 0 else len(paths) - 1)
        bar.editor.setText(paths[index])
        bar.setCurrentWidget(bar.editor)
        bar._position_dropdown()
        bar.editor.setCursorPosition(len(paths[index]))
        bar.editor.setFocus(Qt.FocusReason.MouseFocusReason)
        return True

    def toggle_directory_favorites(self):
        if self.favorite_popup.isVisible():
            self.hide_favorite_popup()
            return
        if not self.folder_favorites.paths:
            return
        if self.launcher.history_popup.isVisible():
            self.launcher.hide_history_popup()
        self.populate_directory_favorites()
        self.position_directory_favorites()
        self.favorite_popup.show()
        self.favorite_popup.raise_()
        self.favorite_choices.setFocus(Qt.FocusReason.MouseFocusReason)

    def hide_favorite_popup(self):
        self.favorite_popup.hide()
        self._favorite_popup_wheel_delta = 0
        self._favorite_popup_warp_generation += 1

    def directory_favorite_clicked(self, item, column):
        path = item.text(0)
        if column == 1:
            try:
                self.folder_favorites.remove(path)
            except OSError:
                self.launcher.error('お気に入りの削除に失敗しました')
                return
            self.populate_directory_favorites()
            self.update_directory_favorite_button()
            if not self.folder_favorites.paths:
                self.hide_favorite_popup()
            return
        self.hide_favorite_popup()
        if not self.go_to_directory(path):
            self.launcher.error('フォルダーが見つかりません: ' + path)

    def directory_favorites_reordered(self, paths):
        try:
            if not self.folder_favorites.reorder(paths):
                self.populate_directory_favorites()
        except OSError:
            self.launcher.error('お気に入りの並び替えを保存できませんでした')
            self.populate_directory_favorites()

    def current_directory(self):
        return row_directory(self.path[-1], self.launcher.expander().expand) if self.path else None

    def middle_selected_paths(self):
        rows = [self.row_data(item) for item in self.middle.tree.selectedItems()]
        return physical_paths(rows, self.launcher.authored_items)


    def begin_context_inline_rename(self, item):
        """Keep a Qt.Tool launch window visible while the context menu closes."""
        launcher = self.launcher
        launcher._filesystem_dialog_depth = getattr(launcher, '_filesystem_dialog_depth', 0) + 1
        def open_editor():
            try:
                self.begin_inline_rename(item)
            finally:
                QTimer.singleShot(650, launcher._finish_batch_delete_guard)
        QTimer.singleShot(0, open_editor)

    def begin_inline_rename(self, item):
        """Edit filename in the middle grid; never rename authored commands."""
        tree = self.middle.tree
        if not item or tree.indexOfTopLevelItem(item) < 0:
            return False
        row = self.row_data(item)
        origin, path = resolve_context_target(row, self.launcher.authored_items)
        if origin not in ('file', 'folder') or not path or not Path(path).exists():
            return False
        # Temporarily enable directory editing; normal folder clicks still
        # enter the folder. The context menu invokes this method explicitly.
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        tree.setCurrentItem(item)
        self._inline_rename_active = True
        tree.editItem(item, 0)
        # QLineEdit should select only the stem, leaving the extension intact.
        editor = tree.findChild(QLineEdit)
        if editor is not None:
            if origin == 'file':
                length = len(Path(path).stem)
                editor.setSelection(0, length)
            else:
                # A canceled folder edit must not turn future folder clicks
                # into SelectedClicked editing. They still browse by click.
                def reset_folder_edit_flag():
                    try:
                        if tree.indexOfTopLevelItem(item) >= 0:
                            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    except RuntimeError:
                        pass  # The refreshed row was already released by Qt.
                editor.editingFinished.connect(
                    lambda: QTimer.singleShot(0, reset_folder_edit_flag))
        return True

    def finish_inline_rename(self, item, column):
        """Commit a real filesystem rename, rejecting invalid/colliding names."""
        if column != 0:
            return
        row = self.row_data(item)
        if not row:
            return
        origin, path = resolve_context_target(row, self.launcher.authored_items)
        if origin not in ('file', 'folder') or not path:
            return
        old_path = Path(path)
        new_name = item.text(0)
        if new_name == old_path.name:
            return
        try:
            # The default extension selection avoids changing .txt by accident.
            if (origin == 'file' and Path(new_name).suffix.casefold() != old_path.suffix.casefold()):
                from PySide6.QtWidgets import QMessageBox
                self.launcher._filesystem_dialog_depth = getattr(
                    self.launcher, '_filesystem_dialog_depth', 0) + 1
                try:
                    answer = QMessageBox.question(
                        self.launcher, '拡張子の変更',
                        '拡張子が変わります。名前を変更しますか？',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No)
                finally:
                    self.launcher._filesystem_dialog_depth -= 1
                if answer != QMessageBox.StandardButton.Yes:
                    raise ValueError('拡張子の変更を取り消しました')
            rename_file_or_folder(old_path, new_name)
            self.launcher.footer.setText(f'名前を変更しました: {old_path.name} → {new_name}')
            QTimer.singleShot(0, self.refresh_middle)
        except (OSError, ValueError) as exc:
            tree = self.middle.tree
            tree.blockSignals(True)
            try:
                item.setText(0, old_path.name)
            finally:
                tree.blockSignals(False)
            if str(exc) != '拡張子の変更を取り消しました':
                self.launcher.error('名前を変更できませんでした: ' + str(exc))

    def go_to_directory(self, path):
        """Breadcrumb/edit/favorite navigation stays inside FRB Launch."""
        import os
        target = normalized_directory(path)
        if not target or not os.path.isdir(target):
            return False
        self.path = [directory_row(target)]
        self.refresh_middle()
        self.focus_panel(self.middle)
        return True

    def middle_back_lane_at(self, point):
        """Legacy viewport helper: the Back lane now lives OUTSIDE the tree."""
        return False

    def middle_blank_back_at(self, point):
        """Only below/between items: real rows remain standard click targets."""
        viewport = self.middle.tree.viewport()
        return (viewport.rect().contains(point) and
                self.middle.tree.itemAt(point) is None)

    def _zone_wheel_source(self, obj):
        """Only freeze wheels in the three-layer navigation zones."""
        if obj in (self.root_widget, self.toolbar_scroller,
                   self.toolbar_scroller.viewport()) or obj in self.root_buttons:
            return True
        if (getattr(self, 'middle', None) is not None and
                obj is self.middle.back):
            return True
        for pane in (getattr(self, 'left', None), getattr(self, 'middle', None),
                     getattr(self, 'right', None)):
            if pane is not None and obj in (pane.tree, pane.tree.viewport()):
                return True
        return False

    def zone_jump(self, target, position='first'):
        """Move focus and cursor to a zone endpoint; never activate an item.

        The reverse route enters at the LAST row/button. Forward navigation
        still enters at the FIRST. Back is a separate focusable header button.
        """
        source = QCursor.pos()
        last = position == 'last'
        if target == 'pages':
            tabs = self.launcher.tabs
            if tabs.count():
                tabs.setCurrentIndex(tabs.count() - 1 if last else 0)
                tabs.setFocus(Qt.FocusReason.TabFocusReason)
        elif target == 'roots':
            if not self.isVisible() or not self.root_buttons:
                return
            index = len(self.root_buttons) - 1 if last else 0
            self._wheel_root_id = self.root_rows[index].get('item_id')
            for i, button in enumerate(self.root_buttons):
                button.setChecked(i == index)
            self.focus_root(index=index)
            self._reverse_zone_entry = last
        elif target == 'back':
            if not self.isVisible() or not self.middle.back.isEnabled():
                return
            self.middle.back.setFocus(Qt.FocusReason.TabFocusReason)
        else:
            pane = {'files': self.left, 'directory': self.middle,
                    'bookmarks': self.right}.get(target)
            if pane is None or not self.isVisible():
                return
            tree = pane.tree
            if last and tree.topLevelItemCount():
                tree.setCurrentItem(tree.topLevelItem(tree.topLevelItemCount() - 1))
            self.focus_panel(pane)
        QTimer.singleShot(0, lambda dest=target, src=source, end=position:
                          self._finish_zone_jump(dest, src, end))

    def _finish_zone_jump(self, target, source, position='first'):
        if (QApplication.mouseButtons() != Qt.MouseButton.NoButton or
                QCursor.pos() != source or not self.launcher.isVisible()):
            return
        last = position == 'last'
        if target == 'pages':
            tabs = self.launcher.tabs
            if not tabs.count() or not tabs.isVisible():
                return
            destination = tabs.mapToGlobal(tabs.tabRect(tabs.count()-1 if last else 0).center())
        elif target == 'roots':
            if not self.isVisible() or not self.root_buttons:
                return
            button = self.root_buttons[-1 if last else 0]
            destination = button.mapToGlobal(button.rect().center())
        elif target == 'back':
            button = self.middle.back
            if not button.isVisible() or not button.isEnabled():
                return
            destination = button.mapToGlobal(button.rect().center())
        else:
            pane = {'files': self.left, 'directory': self.middle,
                    'bookmarks': self.right}.get(target)
            if pane is None or not pane.tree.isVisible():
                return
            tree = pane.tree
            item = tree.currentItem()
            if item is None:
                return
            tree.scrollToItem(item)
            rect = tree.visualItemRect(item)
            if rect.isEmpty():
                return
            viewport = tree.viewport()
            destination = viewport.mapToGlobal(QPoint(
                max(4, min(rect.center().x(), viewport.width() - 12)),
                rect.center().y()))
        if destination != source:
            if target == 'files':
                self._files_warp_global = (destination.x(), destination.y())
            elif target == 'directory':
                self._middle_warp_global = (destination.x(), destination.y())
            elif target == 'bookmarks':
                self._bookmark_warp_global = (destination.x(), destination.y())
            QCursor.setPos(destination)

    def wheel_back_button(self, event):
        """On the Back header, an extra sustained UP wheel enters Files last.

        Back CLICK remains the only way to navigate up a directory.
        """
        if (not self.isVisible() or
                event.modifiers() != Qt.KeyboardModifier.NoModifier or
                QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            self._wheel_back_delta = 0
            self.wheel_zone_navigation.reset('back-up')
            return False
        angle = event.angleDelta().y()
        pixels = event.pixelDelta().y()
        self._wheel_back_delta, movement = wheel_steps(self._wheel_back_delta, angle, pixels)
        if movement:
            if self.wheel_zone_navigation.feed('back-up', movement < 0, abs(movement)):
                self.zone_jump('files', position='last')
        return bool(angle or pixels)

    def jump_from_last_page(self):
        """The rightmost Page can enter the Work Page's second layer."""
        if self.launcher.view_mode != 'expanded':
            return
        work = self.launcher.expanded_options.get('page_id')
        index = next((i for i, p in enumerate(self.launcher.pages)
                      if p.get('page_id') == work), None)
        if index is None:
            return
        if self.launcher.tabs.currentIndex() != index:
            self.launcher.tabs.setCurrentIndex(index)
        QTimer.singleShot(0, lambda: self.zone_jump('roots'))

    def handle_middle_back_double_click(self, obj, event):
        """Double-click blank lower area or invisible right lane = existing Back."""
        if (getattr(self, 'middle', None) is None or not self.isVisible() or
                event.type() not in (QEvent.Type.MouseButtonPress,
                                     QEvent.Type.MouseButtonRelease,
                                     QEvent.Type.MouseButtonDblClick) or
                event.button() != Qt.MouseButton.LeftButton or
                event.modifiers() != Qt.KeyboardModifier.NoModifier):
            return False
        lane = obj is getattr(self, 'middle_back_lane', None)
        in_tree = obj is self.middle.tree.viewport()
        if not (lane or in_tree):
            return False
        if event.type() == QEvent.Type.MouseButtonDblClick:
            if lane or (in_tree and self.middle_blank_back_at(event.position().toPoint())):
                self.go_up()
                event.accept()
                return True
        if lane:
            # This is an independent QWidget, not an editable item cell.
            event.accept()
            return True
        return False

    def eventFilter(self, obj, event):
        if (event.type() == QEvent.Type.Wheel and self.isVisible() and
                self._zone_wheel_source(obj) and
                self.wheel_zone_navigation.wheel_is_locked()):
            event.accept()
            return True  # Ignore momentum across an inter-area warp.
        if (event.type() == QEvent.Type.Wheel and self.isVisible() and
                obj is getattr(getattr(self, 'middle', None), 'back', None) and
                self.wheel_back_button(event)):
            event.accept()
            return True
        if (event.type() == QEvent.Type.Wheel and self.isVisible() and
                self.wheel_directory_favorite_history(obj, event)):
            event.accept()
            return True
        if self.handle_middle_back_double_click(obj, event):
            return True
        if (getattr(self, 'left', None) is not None and
                obj is self.left.tree.viewport() and
                event.type() == QEvent.Type.MouseMove and
                self._files_warp_global is not None):
            position = event.globalPosition().toPoint()
            warp = self._files_warp_global
            self._files_warp_global = None
            if is_warp_generated_mouse_move((position.x(), position.y()), warp):
                event.accept()
                return True
        if (getattr(self, 'left', None) is not None and
                obj is self.left.tree.viewport() and
                event.type() == QEvent.Type.MouseMove):
            self._files_edge_follow_active = False
        if (getattr(self, 'middle', None) is not None and
                obj is self.middle.tree.viewport() and
                event.type() == QEvent.Type.MouseMove and
                self._middle_warp_global is not None):
            position = event.globalPosition().toPoint()
            warp = self._middle_warp_global
            self._middle_warp_global = None
            if is_warp_generated_mouse_move((position.x(), position.y()), warp):
                event.accept()
                return True
        if (getattr(self, 'right', None) is not None and
                obj is self.right.tree.viewport() and
                event.type() == QEvent.Type.MouseMove and
                self._bookmark_warp_global is not None):
            position = event.globalPosition().toPoint()
            warp = self._bookmark_warp_global
            # QCursor.setPos() can generate a synthetic Qt mouse-move event.
            # Do not mistake that for an intentional user hover operation.
            self._bookmark_warp_global = None
            if is_warp_generated_mouse_move((position.x(), position.y()), warp):
                event.accept()
                return True
        if (getattr(self, 'right', None) is not None
                and obj is self.right.tree.viewport()
                and event.type() == QEvent.Type.MouseMove):
            self._bookmark_edge_follow_active = False
        # Combo-like behavior: dismiss favorites on an unrelated click, but
        # don't consume the click or interfere with file/keyboard actions.
        if (hasattr(self, 'favorite_popup') and self.favorite_popup.isVisible()
                and event.type() == QEvent.Type.MouseButtonPress
                and isinstance(obj, QWidget) and obj.window() is self.launcher
                and obj is not self.favorite_dropdown
                and not self.favorite_dropdown.isAncestorOf(obj)
                and obj is not self.favorite_popup
                and not self.favorite_popup.isAncestorOf(obj)):
            self.hide_favorite_popup()
        if (hasattr(self, 'favorite_choices') and self.favorite_popup.isVisible()
                and obj in (self.favorite_choices, self.favorite_choices.viewport())
                and event.type() == QEvent.Type.KeyPress):
            if event.key() == Qt.Key.Key_Escape:
                self.hide_favorite_popup()
                self.focus_panel(self.middle)
                return True
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Right):
                row = self.favorite_choices.currentItem()
                if row:
                    self.directory_favorite_clicked(row, 0)
                return True
            if event.key() == Qt.Key.Key_Delete:
                row = self.favorite_choices.currentItem()
                if row:
                    self.directory_favorite_clicked(row, 1)
                return True
        if (event.type() == QEvent.Type.Wheel and self.isVisible()
                and obj in (self.left.tree, self.left.tree.viewport())
                and not self._files_first_wan_enabled):
            if self.wheel_files_first_column(event):
                event.accept()
                return True
        if (event.type() == QEvent.Type.Wheel and self.isVisible()
                and obj in (self.right.tree, self.right.tree.viewport())
                and not getattr(self.launcher, 'bookmark_wan_enabled', True)):
            if self.wheel_bookmarks_first_level(event):
                event.accept()
                return True
        if (self.isVisible() and self.root_buttons
                and obj in (self.root_widget, self.toolbar_scroller.viewport(),
                            self.toolbar_scroller)
                and event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton):
            # The second-level toolbar is mostly empty when it has just a
            # few buttons. A click on that *blank* region focuses the first
            # button, not an arbitrary previous button or its cascade.
            # Actual button clicks are delivered to the QPushButtons above.
            self.launcher.close_cascade_for_main_interaction()
            self._wheel_root_id = self.root_rows[0].get('item_id')
            for index, button in enumerate(self.root_buttons):
                button.setChecked(index == 0)
            self.focus_root(index=0)
            event.accept()
            return True
        if (event.type() == QEvent.Type.Wheel and self.isVisible()
                and (obj in self.root_buttons or
                     obj in (self.root_widget, self.toolbar_scroller,
                             self.toolbar_scroller.viewport()))):
            if self.wheel_first_level(event, obj):
                event.accept()
                return True
        return super().eventFilter(obj, event)

    def wheel_middle_at_edge(self, event, scroll_before, scroll_after):
        """WAN fallback: native scroll first, cursor-follow at a real edge.

        No click, folder preview/expansion, activation, or file operations.
        Keep Ctrl/Shift wheel and active inline editors unchanged.
        """
        hold = getattr(self, '_middle_back_hold', None)
        if (not self.isVisible() or
                event.modifiers() != Qt.KeyboardModifier.NoModifier or
                QApplication.mouseButtons() != Qt.MouseButton.NoButton or
                self.middle.tree.state() == QAbstractItemView.State.EditingState):
            self._wheel_middle_delta = 0
            if hold is not None:
                hold.reset()
            return False
        tree = self.middle.tree
        if not tree.topLevelItemCount():
            self._wheel_middle_delta = 0
            if hold is not None:
                hold.reset()
            return False
        # Any real scroll is Target Flow: keep the OS cursor where it is.
        if scroll_before != scroll_after:
            getattr(self, 'wheel_zone_navigation', None) and self.wheel_zone_navigation.reset('directory-last')
            getattr(self, 'wheel_zone_navigation', None) and self.wheel_zone_navigation.reset('directory-first')
            self._wheel_middle_delta = 0
            self._middle_follow_pending = None
            if hold is not None:
                hold.reset()
            return False
        angle = event.angleDelta().y()
        pixels = event.pixelDelta().y()
        pending, movement = wheel_steps(self._wheel_middle_delta, angle, pixels)
        self._wheel_middle_delta = pending
        if not movement:
            return bool(angle or pixels)  # Incomplete high-res wheel step.
        scrollbar = tree.verticalScrollBar()
        if not can_follow_at_edge(scroll_before, scroll_after,
                                  scrollbar.minimum(), scrollbar.maximum(), movement):
            self._wheel_middle_delta = 0
            if hold is not None:
                hold.reset()
            return False
        viewport = tree.viewport()
        cursor_local = viewport.mapFromGlobal(QCursor.pos())
        if not viewport.rect().contains(cursor_local):
            if hold is not None:
                hold.reset()
            return False
        # Anchor to the *item under the mouse*, not a stale keyboard current
        # item. It can differ after many normal wheel scroll events.
        hovered = tree.itemAt(cursor_local)
        current = hovered if hovered is not None else tree.currentItem()
        if current is None:
            return True
        index = tree.indexOfTopLevelItem(current)
        if index < 0:
            return True
        target = root_wheel_target(index, movement, tree.topLevelItemCount())
        # Count only extra upward input AFTER the first row has become current.
        # The last wheel event used to *reach* row 0 is never counted.
        at_first = (index == 0 and movement < 0 and
                    tree.currentItem() is tree.topLevelItem(0) and
                    cursor_local.y() >= 0)
        legacy_hold_fired = False
        if hold is not None and hold.feed(at_first, abs(movement)):
            legacy_hold_fired = True
        navigator = getattr(self, 'wheel_zone_navigation', None)
        if (navigator is not None and
                navigator.feed('directory-first', at_first, abs(movement))):
            self.zone_jump('back')
            return True
        if navigator is None and legacy_hold_fired:
            self.schedule_middle_back_pointer(cursor_global=QCursor.pos())
            return True
        at_last = (index == tree.topLevelItemCount() - 1 and movement > 0
                   and tree.currentItem() is tree.topLevelItem(index))
        if (getattr(self, 'wheel_zone_navigation', None) is not None and
                self.wheel_zone_navigation.feed('directory-last', at_last, abs(movement))):
            self.zone_jump('bookmarks')
            return True
        if target is None or target == index:
            return True  # Stop at first/last file; no wrap and no warp.
        item = tree.topLevelItem(target)
        # A wheel step is navigation, not a filesystem operation.  Do not
        # invoke choose_middle(), activate_row(), or itemClicked handlers.
        # Wheel navigation should visibly mark the current row. Preserve an
        # existing Ctrl/Shift multi-selection rather than silently discarding
        # the user's file selection while browsing.
        preserve_multi = len(tree.selectedItems()) > 1
        if not preserve_multi:
            tree.clearSelection()
        tree.setCurrentItem(item)
        if not preserve_multi:
            item.setSelected(True)
        tree.setFocus(Qt.FocusReason.MouseFocusReason)
        self._middle_follow_pending = item
        if not self._middle_follow_scheduled:
            self._middle_follow_scheduled = True
            QTimer.singleShot(0, self.follow_middle_pointer)
        return True

    def follow_middle_pointer(self):
        """Move vertically onto the newly current visible file row."""
        self._middle_follow_scheduled = False
        item = self._middle_follow_pending
        self._middle_follow_pending = None
        tree = self.middle.tree
        if (item is None or not self.isVisible() or not tree.isVisible()
                or tree.currentItem() is not item
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return
        viewport = tree.viewport()
        position = QCursor.pos()
        local = viewport.mapFromGlobal(position)
        if not viewport.rect().contains(local):
            return  # User has already moved elsewhere.
        bounds = tree.visualItemRect(item)
        target = cursor_target((viewport.width(), viewport.height()),
                               (bounds.left(), bounds.top(), bounds.width(), bounds.height()),
                               local.x())
        if target is None:
            return
        destination = viewport.mapToGlobal(QPoint(*target))
        if destination == position:
            return
        self._middle_warp_global = (destination.x(), destination.y())
        QCursor.setPos(destination)

    def schedule_middle_back_pointer(self, cursor_global):
        # Warp to Back without clicking, only if the pointer has not moved.
        self._middle_back_warp_pending = cursor_global
        QTimer.singleShot(0, self.follow_middle_back_pointer)

    def follow_middle_back_pointer(self):
        original = self._middle_back_warp_pending
        self._middle_back_warp_pending = None
        if (original is None or not self.isVisible()
                or not self.middle.back.isVisible() or not self.middle.back.isEnabled()
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton
                or QCursor.pos() != original):
            return
        viewport = self.middle.tree.viewport()
        if not viewport.rect().contains(viewport.mapFromGlobal(original)):
            return
        button = self.middle.back
        destination = button.mapToGlobal(button.rect().center())
        if destination != original:
            QCursor.setPos(destination)  # Never synthesize a click or Back action.

    def sync_first_files_hover_from_cursor(self):
        """In Target Flow, preview the folder that came beneath the cursor."""
        self._files_scroll_hover_scheduled = False
        if not self.isVisible():
            return
        tree = self.left.tree
        viewport = tree.viewport()
        position = viewport.mapFromGlobal(QCursor.pos())
        if not viewport.rect().contains(position):
            return
        item = tree.itemAt(position)
        if item is not None and item is not tree.currentItem():
            tree.setCurrentItem(item)
            self.choose_files(item, 0)  # Preview, never launch or activate.

    def wheel_files_at_edge(self, event, scroll_before, scroll_after):
        """Files first column: Target Flow if scrollbar moves, else Follow.

        Folder preview is kept, but an actual command is never executed by
        the wheel. The middle pane, clicks and drag operations are unchanged.
        """
        if (not self.isVisible()
                or event.modifiers() != Qt.KeyboardModifier.NoModifier
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            self._wheel_files_delta = 0
            return False
        tree = self.left.tree
        if not tree.topLevelItemCount():
            self._wheel_files_delta = 0
            return False
        if scroll_before != scroll_after:
            getattr(self, 'wheel_zone_navigation', None) and self.wheel_zone_navigation.reset('files-last')
            getattr(self, 'wheel_zone_navigation', None) and self.wheel_zone_navigation.reset('files-first')
            self._files_edge_follow_active = False
            self._wheel_files_delta = 0
            self._files_follow_pending = None
            if not self._files_scroll_hover_scheduled:
                self._files_scroll_hover_scheduled = True
                QTimer.singleShot(0, self.sync_first_files_hover_from_cursor)
            return False
        pending, movement = wheel_steps(
            self._wheel_files_delta, event.angleDelta().y(), event.pixelDelta().y())
        self._wheel_files_delta = pending
        if not movement:
            return bool(event.angleDelta().y() or event.pixelDelta().y())
        scrollbar = tree.verticalScrollBar()
        if not can_follow_at_edge(scroll_before, scroll_after,
                                  scrollbar.minimum(), scrollbar.maximum(), movement):
            self._wheel_files_delta = 0
            return False
        viewport = tree.viewport()
        position = viewport.mapFromGlobal(QCursor.pos())
        if not viewport.rect().contains(position):
            return False
        hovered = tree.itemAt(position)
        current = (tree.currentItem() if self._files_edge_follow_active
                   else hovered or tree.currentItem())
        index = tree.indexOfTopLevelItem(current) if current is not None else -1
        if index < 0:
            return True
        target = root_wheel_target(index, movement, tree.topLevelItemCount())
        at_first = (index == 0 and movement < 0 and
                    tree.currentItem() is tree.topLevelItem(0))
        if (getattr(self, 'wheel_zone_navigation', None) is not None and
                self.wheel_zone_navigation.feed('files-first', at_first, abs(movement))):
            self.zone_jump('roots', position='last')
            return True
        at_last = (index == tree.topLevelItemCount() - 1 and movement > 0
                   and tree.currentItem() is tree.topLevelItem(index))
        if (getattr(self, 'wheel_zone_navigation', None) is not None and
                self.wheel_zone_navigation.feed('files-last', at_last, abs(movement))):
            self.zone_jump('directory')
            return True
        if target is None or target == index:
            return True
        item = tree.topLevelItem(target)
        tree.setCurrentItem(item)
        tree.scrollToItem(item)
        tree.setFocus(Qt.FocusReason.MouseFocusReason)
        self._files_edge_follow_active = True
        self.choose_files(item, 0)  # Existing preview only.
        self._files_follow_pending = item
        if not self._files_follow_scheduled:
            self._files_follow_scheduled = True
            QTimer.singleShot(0, self.follow_first_files_pointer)
        return True

    def follow_first_files_pointer(self):
        """Keep the pointer on the previewed Files root at the scroll edge."""
        self._files_follow_scheduled = False
        item = self._files_follow_pending
        self._files_follow_pending = None
        tree = self.left.tree
        if (item is None or not self.isVisible() or not tree.isVisible()
                or tree.currentItem() is not item
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return
        viewport = tree.viewport()
        position = QCursor.pos()
        local = viewport.mapFromGlobal(position)
        if not viewport.rect().contains(local):
            return
        bounds = tree.visualItemRect(item)
        target = cursor_target((viewport.width(), viewport.height()),
                               (bounds.left(), bounds.top(), bounds.width(), bounds.height()),
                               local.x())
        if target is None:
            return
        destination = viewport.mapToGlobal(QPoint(*target))
        if destination != position:
            self._files_warp_global = (destination.x(), destination.y())
            QCursor.setPos(destination)

    def wheel_files_first_column(self, event):
        """Browse first-column folders by wheel without scrolling other panes.

        Reuse choose_files(), the same preview as a click/Up/Down key.  This
        never calls execute()/activate(), even for an authored command row.
        """
        tree = self.left.tree
        count = tree.topLevelItemCount()
        if not count or event.modifiers() != Qt.KeyboardModifier.NoModifier:
            return False
        angle = event.angleDelta().y()
        delta = angle if angle else event.pixelDelta().y() * 3
        if not delta:
            return False
        self._wheel_files_delta += delta
        steps = int(abs(self._wheel_files_delta) // 120)
        if not steps:
            return True  # Precision touchpad: wait for one complete step.
        direction = -1 if self._wheel_files_delta > 0 else 1
        self._wheel_files_delta -= (1 if self._wheel_files_delta > 0 else -1) * steps * 120
        current = tree.currentItem()
        index = tree.indexOfTopLevelItem(current) if current is not None else -1
        if index < 0:
            index = 0
        target = root_wheel_target(index, direction * steps, count)
        if target is None or target == index:
            return True  # Stop at the ends; never scroll the folder list.
        item = tree.topLevelItem(target)
        tree.setCurrentItem(item)
        tree.scrollToItem(item)  # Keep the current row visible in long lists.
        tree.setFocus(Qt.FocusReason.MouseFocusReason)
        row = self.row_data(item)
        if row and row.get('item_kind') in ('category', 'directory'):
            self.choose_files(item, 0)
        return True

    def set_bookmark_wan(self, enabled):
        """Swap Bookmarks between native-scroll WAN and the legacy Follow mode."""
        self._wheel_bookmark_delta = 0
        self._bookmark_edge_follow_active = False
        self.cancel_bookmark_pointer_follow()
        self.cancel_bookmark_hover()
        self.right.tree.adaptive_wheel_callback = (
            self.wheel_bookmarks_at_edge if enabled else None)

    def cancel_bookmark_hover(self):
        self._bookmark_hover_item = None
        self._bookmark_hover_timer.stop()

    def hover_bookmark_first_level(self, item, _column):
        """True mouse hover also previews folders, without executing links."""
        if (not getattr(self.launcher, 'bookmark_wan_enabled', True)
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return
        # A genuinely new hover target takes priority over an edge-follow
        # sequence (synthesized pointer moves are filtered upstream).
        self._bookmark_edge_follow_active = False
        self.request_bookmark_hover(item)

    def request_bookmark_hover(self, item):
        """Keep the current row at the cursor; debounce cascade expansion.

        Normal scroll moves the *content* beneath the pointer, so itemEntered
        is not always emitted. Both wheel and mouse hover call this function.
        """
        tree = self.right.tree
        if item is None or tree.indexOfTopLevelItem(item) < 0:
            self.cancel_bookmark_hover()
            return
        if tree.currentItem() is not item:
            tree.setCurrentItem(item)
        if self._bookmark_hover_item is item and self._bookmark_hover_timer.isActive():
            return
        self._bookmark_hover_item = item
        # Rapid wheel movement should not open a cascade for every row that
        # briefly passes under the stationary cursor.
        self._bookmark_hover_timer.start(230)

    def open_bookmark_hover(self):
        """Preview the settled hovered folder to the right; links stay inert."""
        item = self._bookmark_hover_item
        self._bookmark_hover_item = None
        if (item is None or not self.isVisible()
                or not getattr(self.launcher, 'bookmark_wan_enabled', True)):
            return
        tree = self.right.tree
        viewport = tree.viewport()
        pos = viewport.mapFromGlobal(QCursor.pos())
        if (not viewport.rect().contains(pos) or tree.itemAt(pos) is not item
                or tree.indexOfTopLevelItem(item) < 0):
            return
        row = self.row_data(item)
        if row and row.get('item_kind') in ('category', 'directory'):
            menu = getattr(self.launcher, 'menu', None)
            if (menu is None or not menu.isVisible()
                    or getattr(menu, 'return_focus_item', None) is not item):
                self.choose_bookmark(item, 0)  # Preview only, never execute.
        else:
            self.launcher.close_cascade_for_main_interaction()

    def sync_bookmark_hover_from_cursor(self):
        """Update hover after Qt has applied native scrollbar movement."""
        self._bookmark_scroll_hover_scheduled = False
        if (not self.isVisible()
                or not getattr(self.launcher, 'bookmark_wan_enabled', True)):
            return
        tree = self.right.tree
        viewport = tree.viewport()
        pos = viewport.mapFromGlobal(QCursor.pos())
        if viewport.rect().contains(pos):
            self.request_bookmark_hover(tree.itemAt(pos))

    def wheel_bookmarks_at_edge(self, event, scroll_before, scroll_after):
        """WAN: native Bookmarks scroll first; follow only at a real edge.

        Do not activate URLs or automatically expand directories per notch.
        Folder previews are ordinary (debounced) hover behavior instead.
        """
        if (not self.isVisible()
                or event.modifiers() != Qt.KeyboardModifier.NoModifier
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            self._wheel_bookmark_delta = 0
            return False
        tree = self.right.tree
        if not tree.topLevelItemCount():
            self._wheel_bookmark_delta = 0
            return False
        if scroll_before != scroll_after:
            getattr(self, 'wheel_zone_navigation', None) and self.wheel_zone_navigation.reset('bookmarks-last')
            getattr(self, 'wheel_zone_navigation', None) and self.wheel_zone_navigation.reset('bookmarks-first')
            self._bookmark_edge_follow_active = False
            # Target Flow: content flows beneath a stationary pointer. Hover
            # after the native scroll, not at the pre-scroll item position.
            self._wheel_bookmark_delta = 0
            self.cancel_bookmark_pointer_follow()
            if not self._bookmark_scroll_hover_scheduled:
                self._bookmark_scroll_hover_scheduled = True
                QTimer.singleShot(0, self.sync_bookmark_hover_from_cursor)
            return False
        pending, movement = wheel_steps(
            self._wheel_bookmark_delta, event.angleDelta().y(), event.pixelDelta().y())
        self._wheel_bookmark_delta = pending
        if not movement:
            return bool(event.angleDelta().y() or event.pixelDelta().y())
        scrollbar = tree.verticalScrollBar()
        if not can_follow_at_edge(scroll_before, scroll_after,
                                  scrollbar.minimum(), scrollbar.maximum(), movement):
            self._wheel_bookmark_delta = 0
            return False
        viewport = tree.viewport()
        pos = viewport.mapFromGlobal(QCursor.pos())
        if not viewport.rect().contains(pos):
            return False
        hovered = tree.itemAt(pos)
        # After the first edge step, keep navigating the current row even
        # when Follow was switched OFF or a deferred pointer warp is pending.
        # Otherwise consecutive notches would repeatedly target one row.
        current = (tree.currentItem() if self._bookmark_edge_follow_active
                   else hovered or tree.currentItem())
        index = tree.indexOfTopLevelItem(current) if current is not None else -1
        if index < 0:
            return True
        target = root_wheel_target(index, movement, tree.topLevelItemCount())
        at_first = (index == 0 and movement < 0 and
                    tree.currentItem() is tree.topLevelItem(0))
        if (getattr(self, 'wheel_zone_navigation', None) is not None and
                self.wheel_zone_navigation.feed('bookmarks-first', at_first, abs(movement))):
            self.zone_jump('directory', position='last')
            return True
        at_last = (index == tree.topLevelItemCount() - 1 and movement > 0
                   and tree.currentItem() is tree.topLevelItem(index))
        if (getattr(self, 'wheel_zone_navigation', None) is not None and
                self.wheel_zone_navigation.feed('bookmarks-last', at_last, abs(movement))):
            self.zone_jump('pages')
            return True
        if target is None or target == index:
            return True
        item = tree.topLevelItem(target)
        tree.setCurrentItem(item)
        tree.setFocus(Qt.FocusReason.MouseFocusReason)
        self._bookmark_edge_follow_active = True
        self.request_bookmark_hover(item)
        if getattr(self.launcher, 'bookmark_pointer_follow', False):
            self.schedule_bookmark_pointer_follow(item)
        return True

    def wheel_bookmarks_first_level(self, event):
        """Wheel through top-level bookmarks; scrollbar drag stays available.

        This right-hand QTreeWidget contains *only* first-level rows.  Child
        categories open in separate existing cascade columns, whose native
        scrolling is unaffected.  One 120-unit notch moves one item; tiny
        precision touchpad deltas accumulate.  No URL or command is run.
        """
        tree = self.right.tree
        count = tree.topLevelItemCount()
        if not count:
            return False
        # Never let modifiers accidentally restore scroll inside this pane.
        # For bulk scrolling the user can drag the native scrollbar thumb.
        if event.modifiers() != Qt.KeyboardModifier.NoModifier:
            return True
        angle = event.angleDelta().y()
        delta = angle if angle else event.pixelDelta().y() * 3
        if not delta:
            return True
        self._wheel_bookmark_delta += delta
        steps = int(abs(self._wheel_bookmark_delta) // 120)
        if not steps:
            return True
        direction = -1 if self._wheel_bookmark_delta > 0 else 1
        self._wheel_bookmark_delta -= (1 if self._wheel_bookmark_delta > 0 else -1) * steps * 120
        current = tree.currentItem()
        index = tree.indexOfTopLevelItem(current) if current is not None else -1
        if index < 0:
            index = 0
        target = root_wheel_target(index, direction * steps, count)
        # The older Bookmark Follow mode retains the same lower-edge Wheel Tab
        # destination, even if the user disables the Hybrid A/B experiment.
        at_last = index == count - 1 and direction > 0 and target == index
        navigation = getattr(self, 'wheel_zone_navigation', None)
        at_first = index == 0 and direction < 0 and target == index
        if navigation is not None and navigation.feed('bookmarks-first', at_first, steps):
            self.zone_jump('directory', position='last')
            return True
        if navigation is not None and navigation.feed('bookmarks-last', at_last, steps):
            self.zone_jump('pages')
            return True
        if target is None or target == index:
            return True  # Stop at both ends; no scroll and no repeated popup.
        item = tree.topLevelItem(target)
        tree.setCurrentItem(item)
        tree.scrollToItem(item)  # Auto-follow beyond the visible rows.
        tree.setFocus(Qt.FocusReason.MouseFocusReason)
        row = self.row_data(item)
        if row and row.get('item_kind') in ('category', 'directory'):
            # Preview a folder using the original cascade; never execute it.
            self.choose_bookmark(item, 0)
            # The cascade is a non-grabbing Qt.Tool window. Keep the outline
            # and subsequent wheel navigation anchored to the bookmarks pane.
            tree.setFocus(Qt.FocusReason.MouseFocusReason)
        else:
            # Leaving a folder for a URL should dismiss its stale preview.
            self.launcher.close_cascade_for_main_interaction()
        if getattr(self.launcher, 'bookmark_pointer_follow', False):
            self.schedule_bookmark_pointer_follow(item)
        return True

    def cancel_bookmark_pointer_follow(self):
        """Cancel a pending warp (e.g. when the user switches modes)."""
        self._bookmark_follow_pending = None
        self._bookmark_warp_global = None

    def schedule_bookmark_pointer_follow(self, item):
        """Coalesce rapid wheel events so only the newest selection moves."""
        self._bookmark_follow_pending = item
        if not self._bookmark_follow_scheduled:
            self._bookmark_follow_scheduled = True
            QTimer.singleShot(0, self.follow_bookmark_pointer)

    def follow_bookmark_pointer(self):
        """Move the OS cursor onto selected row, but never click or activate."""
        self._bookmark_follow_scheduled = False
        item = self._bookmark_follow_pending
        self._bookmark_follow_pending = None
        tree = self.right.tree
        if (item is None or not getattr(self.launcher, 'bookmark_pointer_follow', False)
                or not self.isVisible() or not tree.isVisible()
                or tree.currentItem() is not item
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return
        viewport = tree.viewport()
        current_global = QCursor.pos()
        current_local = viewport.mapFromGlobal(current_global)
        # If the user moved off Bookmarks since the wheel event, do not jump.
        if not viewport.rect().contains(current_local):
            return
        bounds = tree.visualItemRect(item)
        target = cursor_target(
            (viewport.width(), viewport.height()),
            (bounds.left(), bounds.top(), bounds.width(), bounds.height()),
            current_local.x())
        if target is None:
            return
        destination = viewport.mapToGlobal(QPoint(*target))
        if destination == current_global:
            return
        self._bookmark_warp_global = (destination.x(), destination.y())
        QCursor.setPos(destination)

    def wheel_first_level(self, event, source):
        """Wheel = select/preview; never execute a command or mutate JSON.

        Each 120 angle units is one item. Accumulate smaller high-resolution
        trackpad movements rather than skipping buttons on tiny deltas.
        """
        if not self.root_buttons or event.modifiers() != Qt.KeyboardModifier.NoModifier:
            return False
        angle = event.angleDelta().y()
        # Pixel-only precision touchpads need a separate, modest conversion.
        delta = angle if angle else event.pixelDelta().y() * 3
        if not delta:
            return False
        self._wheel_root_delta += delta
        steps = int(abs(self._wheel_root_delta) // 120)
        if steps == 0:
            return True
        direction = -1 if self._wheel_root_delta > 0 else 1
        self._wheel_root_delta -= (1 if self._wheel_root_delta > 0 else -1) * steps * 120
        index = next((i for i, row in enumerate(self.root_rows)
                      if row.get('item_id') == self._wheel_root_id), None)
        if index is None:
            focus = QApplication.focusWidget()
            if focus in self.root_buttons:
                index = self.root_buttons.index(focus)
            elif source in self.root_buttons:
                index = self.root_buttons.index(source)
            else:
                index = 0
        target = root_wheel_target(index, direction * steps, len(self.root_buttons))
        if target is None:
            return True
        # A sustained extra turn at either END of the root strip acts like a
        # deliberate Wheel Tab gesture; normal one-notch selection is unchanged.
        at_left = target == index == 0 and direction < 0
        at_right = target == index == len(self.root_buttons) - 1 and direction > 0
        if (getattr(self, 'wheel_zone_navigation', None) is not None and
                self.wheel_zone_navigation.feed('roots-left', at_left, steps)):
            if self._reverse_zone_entry:
                self.zone_jump('pages', position='last')
                self._reverse_zone_entry = False
            else:
                self.zone_jump('pages')
            return True
        if (getattr(self, 'wheel_zone_navigation', None) is not None and
                self.wheel_zone_navigation.feed('roots-right', at_right, steps)):
            self.zone_jump('files')
            return True
        if target == index:
            return True
        row, button = self.root_rows[target], self.root_buttons[target]
        self._wheel_root_id = row.get('item_id')
        for i, entry in enumerate(self.root_buttons):
            entry.setChecked(i == target)
        self.focus_root(index=target)
        self.schedule_root_pointer_follow(button)
        # Show a navigable folder's menu immediately, just as changing Page
        # switches its content. Pure commands stay SELECTED, never executed.
        if row.get('item_kind') in ('category', 'directory'):
            self.open_cascade(row, button)
        elif self.launcher.menu is not None and self.launcher.menu.isVisible():
            self.launcher.menu.close()
        return True

    def schedule_root_pointer_follow(self, button):
        """Follow a wheel-chosen root button; never synthesize a click."""
        self._wheel_root_follow_pending = button
        if not self._wheel_root_follow_scheduled:
            self._wheel_root_follow_scheduled = True
            QTimer.singleShot(0, self.follow_root_pointer)

    def follow_root_pointer(self):
        """Warp only while the user is still over the second-layer strip."""
        self._wheel_root_follow_scheduled = False
        button = self._wheel_root_follow_pending
        self._wheel_root_follow_pending = None
        if (button not in self.root_buttons or not self.isVisible()
                or not button.isVisible()
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return
        viewport = self.toolbar_scroller.viewport()
        position = QCursor.pos()
        local = viewport.mapFromGlobal(position)
        if not viewport.rect().contains(local):
            return
        # focus_root() called ensureWidgetVisible(); wait for that layout to
        # settle, and land in the visible button rather than a spacer/gap.
        destination = button.mapToGlobal(QPoint(button.width() // 2,
                                                button.height() // 2))
        if not viewport.rect().contains(viewport.mapFromGlobal(destination)):
            return
        if destination != position:
            QCursor.setPos(destination)

    def focus_panel(self, panel):
        """Move keyboard focus and visible selection together."""
        tree = panel.tree
        if tree.currentItem() is None and tree.topLevelItemCount():
            tree.setCurrentItem(tree.topLevelItem(0))
        tree.setFocus(Qt.FocusReason.TabFocusReason)
        if tree.currentItem() is not None:
            tree.scrollToItem(tree.currentItem())

    def focus_root(self, item_id=None, index=None):
        if not self.root_buttons:
            return
        if item_id is not None:
            index = next((i for i, row in enumerate(self.root_rows)
                          if row.get('item_id') == item_id), None)
        if index is None or not 0 <= index < len(self.root_buttons):
            index = 0
        button = self.root_buttons[index]
        self.toolbar_scroller.ensureWidgetVisible(button)
        button.setFocus(Qt.FocusReason.TabFocusReason)

    def navigate_middle(self, row):
        """Descend without destroying a Qt row during the current key event."""
        if row.get('item_kind') not in ('category', 'directory'):
            return
        if self.path and self.path[-1].get('item_id') == row.get('item_id'):
            self.focus_panel(self.middle)
            return
        self.path.append(row)
        def finish():
            self.refresh_middle()
            self.focus_panel(self.middle)
        QTimer.singleShot(0, finish)

    def go_up(self, *, keep_middle_focus=False):
        """Navigate to the actual parent folder, even from direct/favorite paths.

        A breadcrumb or favorite can set self.path to a *single* row. History
        popping in that case wrongly did nothing; Back means parent directory.
        """
        import ntpath
        import os
        current = self.current_directory()
        if current:
            normalized = ntpath.normpath(current)
            parent = ntpath.dirname(normalized)
            if (parent and ntpath.normcase(parent) != ntpath.normcase(normalized)
                    and os.path.isdir(parent)):
                self.path = [directory_row(parent)]
                def finish():
                    self.refresh_middle()
                    self.focus_panel(self.middle if keep_middle_focus else self.left)
                QTimer.singleShot(0, finish)
                return
        # PC / drive roots have no real ancestor in the file list.
        self.focus_panel(self.left)

    def enter_row(self, pane, item):
        """Enter runs a filesystem directory; Right instead browses it."""
        row = self.row_data(item)
        if not row:
            return
        if row.get('item_kind') == 'directory':
            self.launcher.execute(row)
        elif row.get('item_kind') == 'category':
            if pane is self.left:
                self.choose_files(item, 0)
                self.focus_panel(self.middle)
            elif pane is self.middle:
                self.navigate_middle(row)
            else:
                self.open_cascade(row, pane.tree, item)
        else:
            self.launcher.activate(row)

    def root_action(self, row, button):
        if row.get('item_id') == self.files_root.get('item_id'):
            self.left.tree.setFocus()
        elif row.get('item_id') == self.bookmarks_root.get('item_id'):
            self.right.tree.setFocus()
        elif row.get('item_kind') in ('category', 'directory'):
            self.open_cascade(row, button)
        else:
            self.launcher.execute(row)

    def row_data(self, item):
        return item.data(0, Qt.ItemDataRole.UserRole) if item is not None else None

    def choose_files(self, item, _col):
        row = self.row_data(item)
        if not row:
            return
        if row.get('item_kind') in ('category', 'directory'):
            self.path = [row]
            self.refresh_middle()
        else:
            self.path = []
            self.middle.label.setText(row.get('title', ''))
            self.address_bar.set_directory(None, row.get('title', ''))
            self.middle.tree.clear()

    def choose_middle(self, item, _col):
        # Extended-selection clicks must not descend into a folder: doing so
        # clears the selection while Ctrl/Shift is adding files and folders.
        modifiers = QApplication.keyboardModifiers()
        if modifiers & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            return
        row = self.row_data(item)
        if row and row.get('item_kind') in ('category', 'directory'):
            # Keep QTreeWidgetItem alive until Qt finishes clicked/activated
            # delivery (especially a double-click on a directory).
            if self.path and self.path[-1].get('item_id') == row.get('item_id'):
                return
            self.path.append(row)
            QTimer.singleShot(0, self.refresh_middle)

    def choose_bookmark(self, item, _col):
        row = self.row_data(item)
        if row and row.get('item_kind') in ('category', 'directory'):
            self.open_cascade(row, self.right.tree, item)

    def activate_row(self, pane, item):
        row = self.row_data(item)
        if not row:
            return
        if row.get('item_kind') in ('category', 'directory'):
            if pane is self.left:
                self.choose_files(item, 0)
            elif pane is self.middle:
                self.choose_middle(item, 0)
            else:
                self.open_cascade(row, pane.tree, item)
        else:
            self.launcher.activate(row)

    def open_cascade(self, row, widget, item=None):
        """Use Launcher's existing menu content/actions; no new command logic."""
        self.launcher.open_expanded_cascade(row, widget, item)

    def context_menu(self, pane, point):
        item = pane.tree.itemAt(point)
        if not item:
            # With no header Paste button, an empty folder must still be
            # pasteable via right-click on its empty middle pane.
            if pane is self.middle and self.current_directory():
                self.launcher.show_expanded_background_paste_menu(
                    pane.tree.viewport().mapToGlobal(point))
            return
        row = self.row_data(item)
        if pane is self.middle:
            tree = pane.tree
            # A right-click on a selected row keeps the full extended selection.
            # A right-click elsewhere changes the target to that one row.
            if not item.isSelected():
                tree.clearSelection()
                tree.setCurrentItem(item)
                item.setSelected(True)
            selected_rows = [self.row_data(i) for i in tree.selectedItems()]
            targets = context_paths(row, selected_rows, self.launcher.authored_items)
            shown = self.launcher.show_launch_context_menu(
                tree.viewport().mapToGlobal(point), row,
                context_parent=self.launcher, selected_paths=targets)
            if shown and len(targets) == 1:
                menu = getattr(self.launcher, '_launch_context_menu', None)
                if menu is not None:
                    for action in menu.actions():
                        # Built-in context rename uses a modal text dialog.
                        # Replace ONLY this pane's Rename action with inline.
                        if '名前の変更' in action.text():
                            try:
                                action.triggered.disconnect()
                            except (TypeError, RuntimeError):
                                pass
                            action.triggered.connect(
                                lambda checked=False, i=item:
                                self.begin_context_inline_rename(i))
                            break
        else:
            pane.tree.setCurrentItem(item)
            self.launcher.show_launch_context_menu(
                pane.tree.viewport().mapToGlobal(point), row, context_parent=self.launcher)
