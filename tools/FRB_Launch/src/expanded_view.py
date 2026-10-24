"""Optional three-layer launcher view: Page -> root actions -> parallel panels.

This is a QWidget INSIDE the main window (never a second Qt.Tool popup).
All rows/actions are supplied by Launcher and use its existing menu data.
"""
from PySide6.QtCore import Qt, QPoint, QSize, QTimer, QEvent
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPixmap, QLinearGradient, QPen, QPalette
from PySide6.QtWidgets import (QFrame, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QTreeWidget, QTreeWidgetItem, QHeaderView, QAbstractItemView,
    QScrollArea, QSplitter, QSizePolicy, QLineEdit, QStackedWidget, QToolButton, QMenu, QStyledItemDelegate)

from file_drag import ExternalFileDragTree

from directory_address import (breadcrumb_segments, compact_segments,
                               directory_row, row_directory, normalized_directory)


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


class _SeparatedFileTree(ExternalFileDragTree):
    """One thin full-width separator per item, including the chevron column."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.separator_color = QColor('#e1e8e3')

    def drawRow(self, painter, option, index):
        super().drawRow(painter, option, index)
        if not option.rect.isValid():
            return
        painter.save()
        painter.setPen(QPen(self.separator_color, 1.0))
        y = option.rect.bottom()
        painter.drawLine(0, y, self.viewport().width() - 1, y)
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
        self.crumb_layout.setContentsMargins(4, 1, 3, 1)
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
        self.editor.setFocus(Qt.FocusReason.MouseFocusReason)
        # Mouse event completion otherwise can reset QLineEdit's selection.
        QTimer.singleShot(0, self.editor.selectAll)

    def show_breadcrumbs(self):
        self.setCurrentWidget(self.surface)
        self._build_crumbs()

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
        segments = compact_segments(self._segments, self.width() - 18, measure)
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
        header.addWidget(self.icon_label)
        self.label = QLabel(label)
        self.label.setObjectName('expandedTitle')
        header.addWidget(self.label, 1)
        self.back = QPushButton('←')
        self.back.setObjectName('expandedBack')
        self.back.setFixedSize(31, 31)
        self.back.setToolTip('一つ上の階層へ戻る')
        self.back.setFocusPolicy(Qt.FocusPolicy.NoFocus)
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
        self.density_button.setFixedSize(29, 29)
        self.density_button.clicked.connect(self.toggle_row_density)
        shared_layout.addWidget(self.density_button)
        self.address_bar = DirectoryAddressBar(self.go_to_directory, self.shared_header)
        shared_layout.addWidget(self.address_bar, 1)
        self.left = ExpandedPanel('Files', 'folder')
        self.middle = ExpandedPanel('フォルダー', 'folder')
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
        light = theme == 'light'
        bg, border, hdr, text, hover, active, stripe = (
            ('#fcfffd', '#bbd8c7', '#eaf6ec', '#233e32', '#ecf7f1', '#d7ece1', '#e7f3ed')
            if light else
            ('#222e2c', '#4b6660', '#344a42', '#e6f0eb', '#344d47', '#416457', '#32433e'))
        tight = self.row_density == 'compact'
        height, pad = (23, 1) if tight else (29, 3)
        self.density_button.setText('☷' if tight else '≡')
        self.density_button.setToolTip('行間隔：コンパクト（クリックで切替）' if not tight
                                       else '行間隔：標準（クリックで切替）')
        for pane in (self.left, self.middle, self.right):
            pane.tree.separator_color = QColor('#e1e8e3' if light else '#455851')
            pane.tree.viewport().update()
        self.setStyleSheet(f'''
            QWidget#expandedRootBar {{ background:transparent; }}
            QScrollArea#expandedRootScroller {{ background:transparent;border:0; }}
            QPushButton#expandedRootButton {{ background:{hdr};color:{text};border:1px solid {border};
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
            QPushButton#expandedBack {{background:transparent;border:0;color:{text};font-size:18px;}}
            QPushButton#expandedBack:hover {{background:{hover};border-radius:7px;}}
            QTreeWidget#expandedTree {{background:{bg};color:{text};border:0;outline:0;}}
            QTreeWidget#expandedTree::item {{min-height:{height}px;padding:{pad}px 7px;border:0;}}
            QTreeWidget#expandedTree::item:hover {{background:{hover};}}
            QTreeWidget#expandedTree::item:selected {{background:{active};color:{text};}}
            QTreeWidget#expandedTree::item:selected:!active {{background:{stripe};color:{text};}}
        ''')
        self.address_bar.setStyleSheet(f'''
            QFrame#addressBreadcrumbSurface {{border:1px solid {border};border-radius:5px;background:{bg};}}
            QToolButton#addressCrumb {{border:0;background:transparent;color:{text};padding:2px 3px;}}
            QToolButton#addressCrumb:hover {{background:{active};border-radius:4px;}}
            QLabel#addressSeparator {{border:0;color:{text};background:transparent;padding:0 2px;}}
            QLabel#addressPlaceholder {{border:0;color:{text};background:transparent;}}
            QLineEdit#directoryAddressEdit {{background:{bg};color:{text};border:1px solid #55a38c;
                border-bottom:2px solid #167f72;border-radius:5px;padding:3px 5px;selection-background-color:#138c8d;
                selection-color:white;}}
        ''')
        self.shared_icon.setPixmap(header_icon('folder', theme).pixmap(28, 28))
        if self.bookmarks_root is not None:
            for index, root in enumerate(self.root_rows):
                if root.get('item_id') == self.bookmarks_root.get('item_id'):
                    self.root_buttons[index].setIcon(header_icon('bookmark', theme))
        for pane in (self.left, self.middle, self.right):
            pane.tree.verticalScrollBar().setSingleStep(26 if tight else 35)
            pane.row_height = 27 if tight else 37
            for row_index in range(pane.tree.topLevelItemCount()):
                item = pane.tree.topLevelItem(row_index)
                for column in (0, 1):
                    item.setSizeHint(column, QSize(0, pane.row_height))
            pane._theme = theme
            pane.icon_label.setPixmap(header_icon(pane.kind, theme).pixmap(28, 28))

    def refresh(self, roots, left, right, options):
        if self._refreshing:
            return
        self._refreshing = True
        try:
            self.options = options
            self.root_buttons = []
            self.root_rows, self.files_root, self.bookmarks_root = roots, left, right
            while self.root_layout.count():
                item = self.root_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            for index, row in enumerate(roots):
                button = QPushButton(row.get('title', ''), self.root_widget)
                button.setObjectName('expandedRootButton')
                button.setCheckable(True)
                button.setChecked(row.get('item_id') in (left['item_id'], right['item_id']))
                button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                button.installEventFilter(self.launcher)
                button.setIcon(header_icon('bookmark', self.launcher.color_theme)
                               if row.get('item_id') == right['item_id'] else self.launcher.row_icon(row))
                hint = f'Ctrl+F{index+1}' if index < 12 else ''
                button.setToolTip((' / '.join(v for v in (row.get('description', ''), hint) if v)))
                button.clicked.connect(lambda checked=False, r=row, b=button: self.root_action(r, b))
                self.root_layout.addWidget(button)
                self.root_buttons.append(button)
            self.root_layout.addStretch()
            self.left.label.setText(left['title'])
            self.shared_title.setText(left['title'])
            self.right.label.setText(right['title'])
            files_rows = self.launcher.displayed_children(left)
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
                matching = next((r for r in self.launcher.displayed_children(parent)
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
                rows = self.launcher.displayed_children(current)
            except (OSError, ValueError, PermissionError) as exc:
                rows = []
                self.middle.label.setToolTip(str(exc))
            self.middle.fill(rows, self.launcher.row_icon)
        else:
            self.middle.tree.clear()

    def current_directory(self):
        return row_directory(self.path[-1], self.launcher.expander().expand) if self.path else None

    def go_to_directory(self, path):
        """Breadcrumb/edit navigation may go ABOVE the configured Files root."""
        import os
        target = normalized_directory(path)
        if not target or not os.path.isdir(target):
            return False
        self.path = [directory_row(target)]
        self.refresh_middle()
        self.focus_panel(self.middle)
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
            return
        row = self.row_data(item)
        pane.tree.setCurrentItem(item)
        self.launcher.show_launch_context_menu(
            pane.tree.viewport().mapToGlobal(point), row, context_parent=self.launcher)
