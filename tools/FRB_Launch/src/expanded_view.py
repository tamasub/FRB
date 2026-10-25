"""Optional three-layer launcher view: Page -> root actions -> parallel panels.

This is a QWidget INSIDE the main window (never a second Qt.Tool popup).
All rows/actions are supplied by Launcher and use its existing menu data.
"""
from PySide6.QtCore import Qt, QPoint, QPointF, QSize, QTimer, QEvent, QRectF
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPixmap, QLinearGradient, QPen, QPalette
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
from launch_appearance import theme_palette, theme_family, scrollbar_for_theme, history_popup_qss


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

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        if not index.data(Qt.ItemDataRole.UserRole):
            return
        center_x = option.rect.right() - 20  # sample: visible 18 px right gap
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
        self._wheel_files_delta = 0
        self._wheel_bookmark_delta = 0
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
        # Only the directory-content column is multi-select. Qt supplies
        # Ctrl+click, Shift+click, Ctrl+A, and Shift+Up/Down natively.
        self.middle.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        # Files' first column is a short navigation list: wheel = select and
        # preview in the middle. Other columns keep native wheel scrolling.
        self.left.tree.installEventFilter(self)
        self.left.tree.viewport().installEventFilter(self)
        self.left.header.hide()
        self.middle.header.hide()
        # Reuse the old Back button/signal, but position it in the shared header.
        self.middle.header.layout().removeWidget(self.middle.back)
        self.middle.back.setParent(self.shared_header)
        shared_layout.addWidget(self.middle.back)
        self.middle.back.show()
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
            # Do not alter Launch DataJSON: the two permanent panel roots are
            # simply not duplicated as buttons in this expanded-view toolbar.
            visible_roots = toolbar_roots(roots, left, right)
            self.root_rows, self.files_root, self.bookmarks_root = visible_roots, left, right
            if self._wheel_root_id not in {row.get('item_id') for row in visible_roots}:
                self._wheel_root_id = None
            self._wheel_root_delta = 0
            self._wheel_bookmark_delta = 0
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

    def eventFilter(self, obj, event):
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
                and obj in (self.left.tree, self.left.tree.viewport())):
            if self.wheel_files_first_column(event):
                event.accept()
                return True
        if (event.type() == QEvent.Type.Wheel and self.isVisible()
                and obj in (self.right.tree, self.right.tree.viewport())):
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
        return True

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
        row, button = self.root_rows[target], self.root_buttons[target]
        self._wheel_root_id = row.get('item_id')
        for i, entry in enumerate(self.root_buttons):
            entry.setChecked(i == target)
        self.focus_root(index=target)
        # Show a navigable folder's menu immediately, just as changing Page
        # switches its content. Pure commands stay SELECTED, never executed.
        if row.get('item_kind') in ('category', 'directory'):
            self.open_cascade(row, button)
        elif self.launcher.menu is not None and self.launcher.menu.isVisible():
            self.launcher.menu.close()
        return True

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
        if len(self.path) > 1:
            self.path.pop()
            # Qt must finish the key event before the selected row is removed.
            def finish():
                self.refresh_middle()
                self.focus_panel(self.middle if keep_middle_focus else self.left)
            QTimer.singleShot(0, finish)
        elif self.path:
            # Keep the first directory preview, but return to its parent list.
            self.focus_panel(self.left)
        else:
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
