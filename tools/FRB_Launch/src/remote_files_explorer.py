"""Explorer-style tree rooted at the rendered Files first-column shortcuts.

Only navigation and the existing Files context-menu interface are emitted;
filesystem operations remain owned by Launch.  Children load lazily.
"""

import json
import os

from PySide6.QtCore import Qt, QPoint, QRectF, QSize, QTimer, Signal
from PySide6.QtGui import (QBrush, QColor, QCursor, QIcon, QPainter, QPen,
                           QPixmap, QStandardItem, QStandardItemModel)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QHBoxLayout,
                               QLabel, QLineEdit, QMenu, QPushButton, QSizeGrip, QStyle,
                               QStyledItemDelegate, QTreeView, QVBoxLayout, QWidget)
from launch_appearance import theme_palette, theme_family
from browser_nav_icons import browser_navigation_icon
from passive_header_drag import PassiveHeaderDrag
from bookmark_cursor_follow import cursor_target
from wheel_adaptive import wheel_steps, can_follow_at_edge
from remote_files_exp_roots import registered_folder_roots, subdirectories
from context_menu_actions import rename_file_or_folder
from clipboard_paste import clipboard_sources, is_cut_clipboard
from file_transfer_visual import transfer_state
from pathlib import Path
from system_drives import drive_rows

_DATA_ROLE = Qt.ItemDataRole.UserRole + 1
_LOADED_ROLE = Qt.ItemDataRole.UserRole + 2
_NORMAL_ICON_ROLE = Qt.ItemDataRole.UserRole + 3


class FilesExpWheelTree(QTreeView):
    """Launch WAN hybrid: native Target Flow, then Cursor Follow at an edge.

    As long as the native scrollbar can travel, keep the pointer still and
    select the folder flowing underneath it. Only at a *real* scroll edge
    select a neighboring visible tree row and optionally warp the pointer.
    Wheel alone never expands folders or invokes a context action.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pointer_follow_enabled = lambda: True
        self._wheel_remainder = 0
        self._edge_follow_active = False
        self._wheel_follow_pending = None
        self._wheel_follow_scheduled = False
        self._flow_selection_scheduled = False
        self._flow_pointer = None
        # An operating row always owns BOTH its green fill and green outline.
        # The same QModelIndex is an outline-only memory when List is active.
        self.current_outline_color = QColor('#8fc7ab')

    def drawRow(self, painter, option, index):
        super().drawRow(painter, option, index)
        if not option.rect.isValid() or index != self.currentIndex():
            return
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QPen(self.current_outline_color, 1.15))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRectF(option.rect.adjusted(5, 3, -5, -3)), 6.5, 6.5)
        painter.restore()

    def _claim_operating_target(self):
        """Only a *real user gesture* in Exp claims the operating column."""
        panel = self.parentWidget()
        launcher = getattr(panel, '_launcher', None)
        view = getattr(launcher, 'expanded_view', None)
        if (launcher is not None and view is not None
                and getattr(view, '_workspace_mode', None) == 'files'):
            # Exp claims the controller first; a wheel-selected folder may
            # later update the breadcrumb without transferring control.
            launcher.set_files_operating_target('files_exp')

    def mousePressEvent(self, event):
        self._claim_operating_target()
        super().mousePressEvent(event)

    def wheelEvent(self, event):
        self._claim_operating_target()
        bar = self.verticalScrollBar()
        before = bar.value()
        # Always give Qt the first opportunity to scroll its *actual* view.
        super().wheelEvent(event)
        after = bar.value()
        if (event.modifiers() != Qt.KeyboardModifier.NoModifier
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            self._wheel_remainder = 0
            self._edge_follow_active = False
            self._wheel_follow_pending = None
            return
        viewport = self.viewport()
        original = QCursor.pos()
        local = viewport.mapFromGlobal(original)
        if not viewport.rect().contains(local):
            self._wheel_remainder = 0
            self._edge_follow_active = False
            self._wheel_follow_pending = None
            return
        angle, pixel = event.angleDelta().y(), event.pixelDelta().y()
        if not angle and not pixel:
            return
        if before != after:
            # Target Flow: scroll content, NEVER move the physical pointer.
            # Re-sync current row after Qt completes scroll geometry updates.
            self._wheel_remainder = 0
            self._edge_follow_active = False
            self._wheel_follow_pending = None
            self._flow_pointer = original
            if not self._flow_selection_scheduled:
                self._flow_selection_scheduled = True
                QTimer.singleShot(0, self._select_flow_row)
            return
        self._wheel_remainder, movement = wheel_steps(self._wheel_remainder, angle, pixel)
        if not movement:
            return
        if not can_follow_at_edge(before, after, bar.minimum(), bar.maximum(), movement):
            # A small trackpad delta in mid-scroll is not a scroll edge.
            self._wheel_remainder = 0
            self._edge_follow_active = False
            return
        # Cursor Follow: choose the row actually under the pointer on the
        # first edge notch. For subsequent notches, advance from currentIndex
        # even if pointer warping is disabled (remote-desktop friendliness).
        hovered = self.indexAt(local)
        current = self.currentIndex()
        target = (current if self._edge_follow_active and current.isValid()
                  else hovered if hovered.isValid() else current)
        if not target.isValid():
            target = self.model().index(0, 0) if self.model() is not None else target
        if not target.isValid():
            return
        new_index = target
        for _ in range(min(abs(movement), 5)):
            neighbor = (self.indexBelow(new_index) if movement > 0
                        else self.indexAbove(new_index))
            if not neighbor.isValid():
                break
            new_index = neighbor
        if new_index == target:
            return  # Last/first visible row: stop here, never wrap or click.
        self._edge_follow_active = True
        self.setCurrentIndex(new_index)
        self.scrollTo(new_index, QAbstractItemView.ScrollHint.EnsureVisible)
        if self.pointer_follow_enabled():
            self._wheel_follow_pending = (original, new_index)
            if not self._wheel_follow_scheduled:
                self._wheel_follow_scheduled = True
                QTimer.singleShot(0, self._follow_wheel_pointer)

    def keyPressEvent(self, event):
        """Use Launch's shared filesystem actions for focused Files Exp keys.

        QTreeView has its own focus as an independent Qt.Tool; the main
        Launch window's Ctrl+C/X/V and F2/F5 shortcuts do not reach it.
        Inline QLineEdit rename editors continue to own their text keys.
        """
        panel = self.parentWidget()
        handler = getattr(panel, 'handle_tree_shortcut', None)
        if callable(handler) and handler(event.key(), event.modifiers()):
            event.accept()
            return
        super().keyPressEvent(event)

    def clear_wheel_pending(self):
        """Discard scheduled cursor movement when the tree is rebuilt.

        Already queued singleShot callbacks may still fire, but their pending
        targets are cleared so a HOME reset cannot select an old index or
        move the user's pointer unexpectedly.
        """
        self._wheel_remainder = 0
        self._edge_follow_active = False
        self._wheel_follow_pending = None
        self._flow_pointer = None

    def _select_flow_row(self):
        """Native scroll moved: highlight the folder now below the cursor."""
        self._flow_selection_scheduled = False
        pointer = self._flow_pointer
        self._flow_pointer = None
        if pointer is None or not self.isVisible() or QCursor.pos() != pointer:
            return
        viewport = self.viewport()
        local = viewport.mapFromGlobal(pointer)
        if viewport.rect().contains(local):
            item = self.indexAt(local)
            if item.isValid() and item != self.currentIndex():
                self.setCurrentIndex(item)

    def _follow_wheel_pointer(self):
        self._wheel_follow_scheduled = False
        pending = self._wheel_follow_pending
        self._wheel_follow_pending = None
        if (pending is None or not self.isVisible() or not self.pointer_follow_enabled()
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return
        original, index = pending
        if QCursor.pos() != original or not index.isValid() or index != self.currentIndex():
            return
        viewport = self.viewport()
        local = viewport.mapFromGlobal(original)
        if not viewport.rect().contains(local):
            return
        rect = self.visualRect(index)
        point = cursor_target((viewport.width(), viewport.height()),
                              (rect.left(), rect.top(), rect.width(), rect.height()),
                              local.x())
        if point is not None:
            dest = viewport.mapToGlobal(QPoint(*point))
            if dest != original:
                QCursor.setPos(dest)


class FilesExpRenameDelegate(QStyledItemDelegate):
    """Use the tree row font, not Launch's larger default QLineEdit font."""

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            editor.setObjectName('filesExpRenameEditor')
            editor.setFont(option.font)
            pixels = option.font.pixelSize()
            if pixels <= 0:
                from PySide6.QtGui import QFontInfo
                pixels = QFontInfo(option.font).pixelSize()
            editor.setStyleSheet(
                'QLineEdit#filesExpRenameEditor {'
                f'font-size:{max(9, pixels)}px; padding:0px 2px;}}')
        return editor


class RemoteFilesExplorer(QWidget):
    """Independent registered directory roots, with live Files navigation."""

    folder_selected = Signal(str)
    pc_selected = Signal()
    folder_context_requested = Signal(str, QPoint)
    folder_renamed = Signal(str, str)

    def __init__(self, remote, theme, *, launcher=None, embedded=False):
        # The remote owns this independent, resizable frameless tool. Its
        # geometry is Remote-relative, but its *size* belongs to the user.
        embedded = bool(embedded)
        owner = launcher if launcher is not None else remote.parent()
        parent = owner if embedded else remote
        if embedded:
            super().__init__(parent)
        else:
            super().__init__(parent, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self._embedded = embedded
        self._remote = remote
        self._launcher = owner
        # Match the Remote's painted 1px / 10px outline, including its
        # genuinely transparent corners on Windows.
        if not self._embedded:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setObjectName('embeddedFilesExplorer' if self._embedded else 'remoteFilesExplorer')
        self.setWindowTitle('Files Exp')
        self.setMinimumSize(220, 180)
        launcher = self._launcher
        self._tree_state_key = ('files_exp_embedded/tree_state_v1' if self._embedded
                                else 'remote_files_exp/tree_state_v1')
        self._settings = getattr(launcher, 'settings', None)
        # User overrides are independent of the existing Exp size settings.
        # Until explicitly dragged/resized, Files single-column mode may
        # derive position/height afresh from the Launch grid on every summon.
        self._automatic_placement = False
        self._header_move_armed = False
        self._header_move_origin = None
        self._grid_height_mode = False
        self._manual_position = str(self._settings.value(
            'remote_files_exp/manual_position', 'false')).lower() in ('true', '1', 'yes') if self._settings is not None else False
        self._manual_height = str(self._settings.value(
            'remote_files_exp/manual_height', 'false')).lower() in ('true', '1', 'yes') if self._settings is not None else False
        self._position_save_timer = QTimer(self)
        self._position_save_timer.setSingleShot(True)
        self._position_save_timer.setInterval(250)
        self._position_save_timer.timeout.connect(self._save_manual_position)
        self._restoring_size = True
        width, height = 330, 425
        if self._settings is not None:
            try:
                width = int(self._settings.value('remote_files_exp/width', width))
                height = int(self._settings.value('remote_files_exp/height', height))
            except (TypeError, ValueError):
                width, height = 330, 425
        if not self._embedded:
            self.resize(max(220, min(width, 1600)), max(180, min(height, 1400)))
        self._restoring_size = False
        # Tree session is independent of the Launch breadcrumb. Restoring a
        # window must not navigate Launch or collapse another user's branches.
        self._restoring_tree = False
        self._syncing_directory = False
        self._tree_state_timer = QTimer(self)
        self._tree_state_timer.setSingleShot(True)
        self._tree_state_timer.setInterval(350)
        self._tree_state_timer.timeout.connect(self._save_tree_state)
        self._pending_restored_scroll = None
        # Avoid syncing state.ini for every pixel while the resize grip moves.
        self._size_save_timer = QTimer(self)
        self._size_save_timer.setSingleShot(True)
        self._size_save_timer.setInterval(250)
        self._size_save_timer.timeout.connect(self._save_size)

        layout = QVBoxLayout(self)
        # Match LaunchRemote's title-strip breathing room (5px, 3px).
        if self._embedded:
            layout.setContentsMargins(0, 0, 0, 0)
        else:
            layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)

        # Only one header remains: no duplicated 'first column' caption.
        header = QFrame(self)
        header.setObjectName('filesExpHeader')
        self.exp_header = header
        # Match the *actual* Remote title strip, including user font scaling.
        remote_header = remote.findChild(QFrame, 'remoteTitleBar') if remote is not None else None
        remote_header_height = (remote_header.height() if remote_header is not None
                                and remote_header.height() >= 24 else
                                remote_header.sizeHint().height() if remote_header is not None
                                else 28)
        header.setFixedHeight(max(28, remote_header_height))
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(8 if self._embedded else 2, 2, 2, 2)
        header_row.setSpacing(2)
        # Exactly the Remote title bar's 28x24 HOME control and 18px glyph.
        self.home_button = QPushButton('', header)
        self.home_button.setObjectName('filesExpHomeButton')
        self.home_button.setProperty('role', 'icon')
        self.home_button.setToolTip('HOME：登録フォルダーを最新化して全て折りたたむ')
        self.home_button.setFixedSize(28, 24)
        self.home_button.setIconSize(QSize(18, 18))
        self.home_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.home_button.clicked.connect(self.reset_to_roots)
        if not self._embedded:
            header_row.addWidget(self.home_button)
        else:
            # Inline first column has no close/remove button; its own HOME
            # control is also redundant beside Launch's permanent HOME.
            self.home_button.hide()
        title = QLabel('Files Exp', header)
        title.setObjectName('filesExpTitle')
        header_row.addWidget(title, 1)
        # Match the Remote header's × control (22px square, framed, rounded).
        if not self._embedded:
            # The inline first column cannot be closed: Files Exp is the
            # navigation area, not a dismissible floating tool window.
            close_button = QPushButton('×', header)
            close_button.setObjectName('filesExpClose')
            close_button.setProperty('role', 'icon')
            close_button.setToolTip('閉じる')
            close_button.setFixedSize(22, 22)
            close_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            close_button.clicked.connect(self.hide)
            header_row.addWidget(close_button)
        layout.addWidget(header)
        self._header_drag = (None if self._embedded else
                             PassiveHeaderDrag(self, on_header_press=self._arm_manual_move))
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        title.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(
            lambda point: self._show_layout_menu(header.mapToGlobal(point)))
        title.customContextMenuRequested.connect(
            lambda point: self._show_layout_menu(title.mapToGlobal(point)))
        if self._header_drag is not None:
            header.installEventFilter(self._header_drag)
            title.installEventFilter(self._header_drag)

        # QFileSystemModel accepts only ONE visual root. For several independent
        # shortcut roots retain QTreeView and use a lazy, read-only item model.
        self.model = QStandardItemModel(self)
        # Same clipboard as Launch's folder cascade: cut stays subdued until
        # paste or a new clipboard value. No separate Exp-only transfer state.
        QApplication.clipboard().dataChanged.connect(self._clipboard_changed)
        self._rename_in_progress = None
        self.tree = FilesExpWheelTree(self)
        self.tree.pointer_follow_enabled = lambda: bool(getattr(
            launcher, 'pointer_warp_enabled', True))
        self.tree.setObjectName('filesExpTree')
        # Both embedded and standalone Exp follow the shared Remote target.
        # Until the Launcher assigns one, remember the row as outline-only.
        self.tree.setProperty('operatingActive', False)
        self.exp_header.setProperty('operatingActive', False)
        self.tree.setModel(self.model)
        self.tree.setItemDelegate(FilesExpRenameDelegate(self.tree))
        self.tree.setHeaderHidden(True)
        # Narrower than the Qt default, but leave room for arrows and icons.
        self.tree.setIndentation(18)
        self.tree.setAnimated(True)
        self.tree.setUniformRowHeights(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setItemsExpandable(True)
        self.tree.setExpandsOnDoubleClick(True)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree.setDragEnabled(False)
        self.tree.setAcceptDrops(False)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_folder_context)
        self.tree.clicked.connect(self._activate_index)
        self._selection_timer = QTimer(self)
        self._selection_timer.setSingleShot(True)
        self._selection_timer.setInterval(130)
        self._selection_timer.timeout.connect(self._commit_current_selection)
        self.tree.selectionModel().currentChanged.connect(self._selection_changed)
        self.tree.expanded.connect(self._schedule_tree_state_save)
        self.tree.collapsed.connect(self._schedule_tree_state_save)
        self.tree.verticalScrollBar().valueChanged.connect(self._schedule_tree_state_save)
        self.tree.horizontalScrollBar().valueChanged.connect(self._schedule_tree_state_save)
        self.tree.expanded.connect(self._expand_index)
        # Clicking the triangle is navigation too: Qt does not guarantee a
        # 'clicked' signal when the disclosure control consumes the click.
        self.tree.expanded.connect(self._activate_disclosure)
        self.tree.collapsed.connect(self._activate_disclosure)
        # Only an explicit Files Exp context Rename can start editing.
        # Normal clicks and double-clicks remain navigation/expansion.
        self.model.itemChanged.connect(self._finish_folder_rename)
        self.tree.itemDelegate().closeEditor.connect(self._close_folder_rename_editor)
        layout.addWidget(self.tree, 1)

        # Guidance belongs below the tree; keep the resize handle reachable.
        footer = QFrame(self)
        footer.setObjectName('filesExpFooter')
        footer_row = QHBoxLayout(footer)
        footer_row.setContentsMargins(4, 0, 0, 0)
        footer_row.setSpacing(2)
        description = QLabel('▶ 展開・折りたたみ  ·  選択で移動  ·  右クリックで操作', footer)
        description.setObjectName('filesExpHint')
        description.setWordWrap(True)
        footer_row.addWidget(description, 1)
        self.size_grip = QSizeGrip(footer)
        self.size_grip.setObjectName('filesExpSizeGrip')
        footer_row.addWidget(self.size_grip, 0, Qt.AlignmentFlag.AlignBottom)
        if not self._embedded:
            layout.addWidget(footer)
        else:
            footer.hide()

        style = QApplication.style()
        # Use the SAME glyph as Launch's ordinary directory rows; virtual PC
        # intentionally keeps the Qt computer icon unique to Files Exp.
        self._folder_icon = (launcher.row_icon({
            'item_kind': 'directory', 'icon_key': 'folder.yellow'})
            if launcher is not None else style.standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        self._pc_icon = style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.apply_theme(theme)

    def _append_folder(self, parent, label, path, *, pc=False, missing=False):
        item = QStandardItem(self._pc_icon if pc else self._folder_icon, label)
        item.setEditable(False)
        item.setDragEnabled(False)
        item.setDropEnabled(False)
        item.setData({'path': path, 'pc': pc}, _DATA_ROLE)
        item.setData(self._pc_icon if pc else self._folder_icon, _NORMAL_ICON_ROLE)
        item.setData(False, _LOADED_ROLE)
        item.setToolTip('ドライブ一覧' if pc else str(path))
        if missing:
            item.setEnabled(False)
            item.setToolTip(f'存在しないかアクセスできないフォルダー: {path}')
        else:
            # A placeholder permits ▶ display without enumerating directories
            # until the user actually expands this particular folder.
            item.appendRow(QStandardItem(''))
        parent.appendRow(item)
        self._apply_transfer_visual(item)
        return item

    def _transfer_paths(self):
        launcher = self._launcher
        mime = QApplication.clipboard().mimeData()
        cut_paths = clipboard_sources(mime) if is_cut_clipboard(mime) else ()
        pasted_paths = getattr(launcher, '_latest_pasted_paths', ())
        return cut_paths, pasted_paths

    @staticmethod
    def _subdued_icon(source):
        """The same 38% icon opacity used in Launch's CascadeMenu."""
        image = source.pixmap(22, 22)
        if image.isNull():
            return source
        pix = QPixmap(image.size())
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setOpacity(0.38)
        painter.drawPixmap(0, 0, image)
        painter.end()
        return QIcon(pix)

    def _apply_transfer_visual(self, item, cut_paths=None, pasted_paths=None):
        data = item.data(_DATA_ROLE)
        if not isinstance(data, dict) or data.get('pc') or not data.get('path'):
            return
        if cut_paths is None or pasted_paths is None:
            cut_paths, pasted_paths = self._transfer_paths()
        state = transfer_state(data['path'], cut_paths=cut_paths,
                               pasted_paths=pasted_paths)
        base = item.data(_NORMAL_ICON_ROLE) or self._folder_icon
        item.setIcon(self._subdued_icon(base) if state == 'cut' else base)
        item.setBackground(QBrush(QColor('#d6f1e8')) if state == 'pasted'
                           else QBrush())
        item.setForeground(QBrush(QColor('#9ca8af')) if state == 'cut'
                           else QBrush())

    def refresh_transfer_visuals(self):
        """Update visible folder icons from Launch's authoritative clipboard."""
        cut_paths, pasted_paths = self._transfer_paths()
        def visit(parent):
            for row in range(parent.rowCount()):
                item = parent.child(row)
                if item is None:
                    continue
                self._apply_transfer_visual(item, cut_paths, pasted_paths)
                visit(item)
        visit(self.model.invisibleRootItem())

    def _clipboard_changed(self):
        # Explorer can replace the clipboard too. End the former paste marker,
        # exactly as CascadeMenu._on_clipboard_change does.
        launcher = self._launcher
        if launcher is not None:
            launcher._latest_pasted_paths = ()
        self.refresh_transfer_visuals()

    def set_roots(self, rows, expand):
        """Rebuild live registered roots; opening subsequently restores state.

        HOME intentionally calls this without restoring the previous tree.
        Changes to the first column and removed folders are handled on reload.
        """
        roots = registered_folder_roots(rows, expand)
        previous_restoring = getattr(self, '_restoring_tree', False)
        self._restoring_tree = True
        try:
            self._selection_timer.stop()
            self.tree.clear_wheel_pending()
            self.model.clear()
            self.model.setHorizontalHeaderLabels(['フォルダー'])
            parent = self.model.invisibleRootItem()
            for root in roots:
                path = root['path']
                self._append_folder(parent, root['label'], path, pc=root['pc'],
                                    missing=not root['pc'] and not os.path.isdir(path))
            self.tree.clearSelection()
            self.tree.setCurrentIndex(self.model.index(-1, 0))
            self.tree.scrollToTop()
            self.tree.horizontalScrollBar().setValue(
                self.tree.horizontalScrollBar().minimum())
        finally:
            self._restoring_tree = previous_restoring
        return len(roots)

    def refresh_directory_branch(self, directory):
        """Reload a physical folder WITHOUT losing expanded descendants.

        Refresh each matching alias under the independent registered roots.
        An expanded child's children are rebuilt only when that child was
        previously expanded; closed branches remain lazy.  Qt's incidental
        currentChanged while rebuilding must never navigate Launch.
        """
        if not directory or not os.path.isdir(directory):
            return False
        target = os.path.normcase(os.path.normpath(str(directory)))
        self._selection_timer.stop()
        self.tree.clear_wheel_pending()
        current_path = self._index_path(self.tree.currentIndex())
        bar = self.tree.verticalScrollBar()
        scroll = bar.value()
        old_sync = self._syncing_directory
        self._syncing_directory = True
        changed = False
        try:
            def reload_node(item):
                """Keep expansion state by path, never by old row index."""
                nonlocal changed
                data = item.data(_DATA_ROLE) or {}
                path = data.get('path')
                if not path or data.get('pc'):
                    return
                idx = item.index()
                opened = self.tree.isExpanded(idx)
                # A closed target is invalidated, and read on next disclosure.
                opened_paths = set()
                def remember(parent):
                    for n in range(parent.rowCount()):
                        child = parent.child(n)
                        if child is None:
                            continue
                        info = child.data(_DATA_ROLE) or {}
                        if info.get('path') and self.tree.isExpanded(child.index()):
                            opened_paths.add(os.path.normcase(os.path.normpath(str(info['path']))))
                        remember(child)
                if opened:
                    remember(item)
                item.removeRows(0, item.rowCount())
                item.setData(False, _LOADED_ROLE)
                if os.path.isdir(path):
                    item.appendRow(QStandardItem(''))
                    if opened:
                        self._expand_index(item.index())
                        self.tree.setExpanded(item.index(), True)
                        def restore(parent):
                            for n in range(parent.rowCount()):
                                child = parent.child(n)
                                if child is None:
                                    continue
                                info = child.data(_DATA_ROLE) or {}
                                key = (os.path.normcase(os.path.normpath(str(info['path'])))
                                       if info.get('path') else None)
                                if key in opened_paths and os.path.isdir(info['path']):
                                    self._expand_index(child.index())
                                    self.tree.setExpanded(child.index(), True)
                                    restore(child)
                        restore(item)
                changed = True
            def scan(parent):
                for n in range(parent.rowCount()):
                    item = parent.child(n)
                    if item is None:
                        continue
                    info = item.data(_DATA_ROLE) or {}
                    path = info.get('path')
                    if path and os.path.normcase(os.path.normpath(str(path))) == target:
                        reload_node(item)
                    else:
                        scan(item)
            scan(self.model.invisibleRootItem())
            # Restoring selection by path avoids choosing the adjacent sibling
            # when the model invalidates an old QModelIndex.
            if changed and current_path and not os.path.isdir(current_path):
                # A cut/move may have removed the selected folder itself.
                # Qt otherwise moves the currentIndex to an arbitrary sibling,
                # leaving the user looking at a misleading green selection.
                self.tree.clearSelection()
                self.tree.setCurrentIndex(self.model.index(-1, 0))
            if changed and current_path and os.path.isdir(current_path):
                wanted = os.path.normcase(os.path.normpath(current_path))
                def restore_current(parent):
                    for n in range(parent.rowCount()):
                        item = parent.child(n)
                        if item is None:
                            continue
                        info = item.data(_DATA_ROLE) or {}
                        path = info.get('path')
                        if path and os.path.normcase(os.path.normpath(str(path))) == wanted:
                            self.tree.setCurrentIndex(item.index())
                            return True
                        if restore_current(item):
                            return True
                    return False
                restore_current(self.model.invisibleRootItem())
            bar.setValue(min(scroll, bar.maximum()))
            self.refresh_transfer_visuals()
        finally:
            self._syncing_directory = old_sync
            self._selection_timer.stop()
        return changed

    def reset_to_roots(self):
        """HOME: reload first-column roots and start with every branch closed.

        This intentionally does *not* emit folder_selected or touch Launch's
        breadcrumb.  The registered root list comes from the same rendered
        Files first-column that is used when the Exp panel is opened.
        """
        launcher = getattr(self, '_launcher', None)
        if launcher is None:
            remote = self.parentWidget()
            launcher = remote.parent() if remote is not None else None
        if launcher is None or not hasattr(launcher, '_remote_files_first_column_rows'):
            return
        self.set_roots(launcher._remote_files_first_column_rows(),
                       launcher.expander().expand)
        # HOME is a deliberate reset. Persist the empty expansion/selection so
        # the next Remote opening does not resurrect discarded branches.
        state_timer = getattr(self, '_tree_state_timer', None)
        save_state = getattr(self, '_save_tree_state', None)
        if state_timer is not None and callable(save_state):
            state_timer.stop()
            save_state()

    def select_first_root_for_home(self):
        """Select the first Files Exp root for Launch/Remote HOME.

        Selection and the column-2 preview are separate responsibilities:
        return an explicit PC/folder target and let Launcher perform the
        navigation.  Launcher calls reset_to_roots() first, which folds all
        branches; this method then selects the fresh first root.
        Suppress delayed selection callbacks so HOME cannot navigate twice.
        """
        index = self.model.index(0, 0)
        if not index.isValid():
            return None
        item = self.model.itemFromIndex(index)
        data = item.data(_DATA_ROLE) if item is not None else None
        if not isinstance(data, dict):
            return None
        if data.get('pc'):
            target = ('pc', None)
        else:
            path = self._index_path(index)
            if not path:
                return None
            target = ('folder', path)
        self._selection_timer.stop()
        self.tree.clear_wheel_pending()
        previous_sync = self._syncing_directory
        self._syncing_directory = True
        try:
            self.tree.setCurrentIndex(index)
            self.tree.scrollTo(index)
        finally:
            self._syncing_directory = previous_sync
        self._schedule_tree_state_save()
        return target

    def _index_path(self, index):
        if not index.isValid():
            return None
        item = self.model.itemFromIndex(index)
        data = item.data(_DATA_ROLE) if item is not None else None
        if not isinstance(data, dict) or data.get('pc'):
            return None  # PC is a virtual root, not a real path.
        path = data.get('path')
        return str(path) if path and os.path.isdir(path) else None

    def handle_tree_shortcut(self, key, modifiers):
        """Dispatch from the Files Exp CURRENT folder, never a stale Files row.

        Keep rename text editing native, prohibit registered-root mutations,
        and reuse the same OS action/paste/refresh responsibility as right-click.
        """
        if self._rename_in_progress is not None or self.tree.state() == QAbstractItemView.State.EditingState:
            return False
        ctrl = modifiers == Qt.KeyboardModifier.ControlModifier
        plain = modifiers == Qt.KeyboardModifier.NoModifier
        if not ((ctrl and key in (Qt.Key.Key_C, Qt.Key.Key_X, Qt.Key.Key_V)) or
                (plain and key in (Qt.Key.Key_Delete, Qt.Key.Key_F2, Qt.Key.Key_F5))):
            return False
        path = self._index_path(self.tree.currentIndex())
        if not path:
            return False  # PC / no selection is not a physical target.
        launcher = getattr(self, '_launcher', None)
        if launcher is None:
            remote = self.parentWidget()
            launcher = remote.parent() if remote is not None else None
        if launcher is None:
            return False
        self._selection_timer.stop()
        if ctrl:
            if key == Qt.Key.Key_V:
                # Explicit target bypasses the main grid's unrelated selected
                # row, which caused accidental pastes to a different folder.
                launcher.paste_into_expanded_directory(destination_override=path)
            else:
                launcher.perform_filesystem_context_action(
                    'cut' if key == Qt.Key.Key_X else 'copy', path, 'folder')
            return True
        if key == Qt.Key.Key_Delete:
            launcher.perform_filesystem_context_action('delete', path, 'folder')
        elif key == Qt.Key.Key_F2:
            if not self.begin_folder_rename(path):
                return False
        else:  # F5
            launcher.refresh_folder_information(path)
        return True

    def _is_pc_index(self, index):
        if not index.isValid():
            return False
        item = self.model.itemFromIndex(index)
        return bool(item is not None and
                    (item.data(_DATA_ROLE) or {}).get('pc'))

    def remote_step(self, direction):
        """Select a visible folder; debounce its breadcrumb/List preview.

        The same currentChanged timer is used by direct Exp wheel scrolling.
        Never hand the logical operating target to List just to refresh it.
        """
        tree = self.tree
        index = tree.currentIndex()
        if not index.isValid():
            index = self.model.index(0, 0)
        else:
            index = (tree.indexBelow(index) if direction > 0
                     else tree.indexAbove(index))
        if not index.isValid():
            return False
        tree.setCurrentIndex(index)  # currentChanged arms the delayed preview.
        tree.scrollTo(index, QAbstractItemView.ScrollHint.EnsureVisible)
        self._schedule_tree_state_save()
        return True

    def remote_activate_current(self):
        """Central Remote click: expand the selected folder AND navigate it."""
        index = self.tree.currentIndex()
        if not index.isValid():
            return False
        self._selection_timer.stop()
        if not self.tree.isExpanded(index):
            # expanded -> _activate_disclosure -> existing breadcrumb callback.
            self.tree.expand(index)
            # Folders with no children cannot expand: still navigate them.
            if self.tree.isExpanded(index):
                return True
        self._activate_index(index)
        return True

    def remote_branch(self, direction):
        """Right expands, left collapses or selects the visible parent."""
        tree = self.tree
        index = tree.currentIndex()
        if not index.isValid():
            return False
        self._selection_timer.stop()
        if direction > 0:
            if not tree.isExpanded(index):
                tree.expand(index)
            else:
                child = self.model.index(0, 0, index)
                if child.isValid() and self._index_path(child):
                    tree.setCurrentIndex(child)
                    self._selection_timer.stop()
                    tree.scrollTo(child)
        elif tree.isExpanded(index):
            tree.collapse(index)
        else:
            parent = index.parent()
            if parent.isValid():
                tree.setCurrentIndex(parent)
                self._selection_timer.stop()
                tree.scrollTo(parent)
        self._schedule_tree_state_save()
        return True

    def remote_current_folder_path(self):
        """Context actions must use the actual selected Exp row, not a guess."""
        return self._index_path(self.tree.currentIndex())

    def remote_select_pc_root(self):
        """パンくずPCからExpへ戻る。ツリーの展開・現在地は変更しない。"""
        for row in range(self.model.rowCount()):
            index = self.model.index(row, 0)
            if not self._is_pc_index(index):
                continue
            self._selection_timer.stop()
            old_sync = self._syncing_directory
            self._syncing_directory = True
            try:
                self.tree.setCurrentIndex(index)
                self.tree.scrollTo(index, QAbstractItemView.ScrollHint.EnsureVisible)
            finally:
                self._syncing_directory = old_sync
            self._schedule_tree_state_save()
            return True
        return False

    def _selection_changed(self, index, _previous):
        """Debounce Exp's selection into a breadcrumb/List *content* update.

        A real wheel (direct or Remote) selects first, then previews the folder
        after 130 ms without any further movement. It does NOT select List as
        the operating column. Programmatic sync/restore is not navigation.
        """
        self._schedule_tree_state_save()
        if self._syncing_directory or getattr(self, '_restoring_tree', False):
            return
        self._selection_timer.stop()
        launcher = getattr(self, '_launcher', None)
        if launcher is not None:
            view = getattr(launcher, 'expanded_view', None)
            if (view is None or not view.isVisible()
                    or view._workspace_mode != 'files'
                    or getattr(launcher, '_files_operating_target', None) != 'files_exp'):
                return
        if self._index_path(index) or self._is_pc_index(index):
            self._selection_timer.start()

    def _commit_current_selection(self):
        """Refresh Files List and breadcrumb, preserving Exp as controller."""
        if self._syncing_directory or getattr(self, '_restoring_tree', False):
            return
        launcher = getattr(self, '_launcher', None)
        if launcher is not None:
            view = getattr(launcher, 'expanded_view', None)
            # A queued timer must not navigate after Browser/List takes over.
            if (view is None or not view.isVisible()
                    or view._workspace_mode != 'files'
                    or getattr(launcher, '_files_operating_target', None) != 'files_exp'):
                return
        index = self.tree.currentIndex()
        if self._is_pc_index(index):
            self.pc_selected.emit()
            return
        path = self._index_path(index)
        if path:
            if launcher is not None:
                directory = view.current_directory()
                if (directory and os.path.normcase(os.path.normpath(str(directory)))
                        == os.path.normcase(os.path.normpath(str(path)))):
                    return  # No costly reload for an already-shown folder.
            self.folder_selected.emit(path)

    def _activate_index(self, index):
        if self._syncing_directory:
            return
        self._selection_timer.stop()
        if self._is_pc_index(index):
            self.pc_selected.emit()
            return
        path = self._index_path(index)
        if path:
            self.folder_selected.emit(path)

    def _activate_disclosure(self, index):
        """The explicit ▶/▼ control updates the same breadcrumb as a row click."""
        if self._syncing_directory:
            return
        self._selection_timer.stop()
        self.tree.setCurrentIndex(index)
        self._activate_index(index)

    def sync_current_directory(self, directory):
        """Reflect every Files breadcrumb transition in the visible tree.

        A programmatic selection must never emit folder_selected again; that
        would cause Files -> Exp -> Files recursion, duplicate history, and
        unexpected focus/cursor movement. Expand ONLY the path to the target.
        Registered roots retain their display order and duplicate aliases.
        """
        if (not directory or not os.path.isdir(directory) or
                self._rename_in_progress is not None):
            return False
        target = os.path.normcase(os.path.normpath(str(directory)))
        if self._index_path(self.tree.currentIndex()) is not None:
            existing = os.path.normcase(os.path.normpath(
                self._index_path(self.tree.currentIndex())))
            if existing == target:
                return True
        self._selection_timer.stop()
        self.tree.clear_wheel_pending()
        # Prefer the longest registered root that contains the destination;
        # PC/drives are a fallback when it is outside the registered roots.
        candidates = []
        pc_root = None
        for row in range(self.model.rowCount()):
            index = self.model.index(row, 0)
            data = (self.model.itemFromIndex(index).data(_DATA_ROLE) or {})
            if data.get('pc'):
                pc_root = index
                continue
            base = data.get('path')
            if not base:
                continue
            base_normal = os.path.normcase(os.path.normpath(str(base)))
            try:
                common = os.path.commonpath((base_normal, target))
            except ValueError:
                continue
            if common == base_normal:
                candidates.append((len(base_normal), index, base_normal))
        candidate = max(candidates, key=lambda record: record[0]) if candidates else None
        self._syncing_directory = True
        try:
            if candidate:
                _, node, base = candidate
            elif pc_root is not None:
                node = pc_root
                self._expand_index(node)
                self.tree.expand(node)
                base = None
                for i in range(self.model.itemFromIndex(node).rowCount()):
                    child = self.model.itemFromIndex(node).child(i)
                    child_path = self._index_path(child.index())
                    if child_path:
                        normalized = os.path.normcase(os.path.normpath(child_path))
                        try:
                            if os.path.commonpath((normalized, target)) == normalized:
                                node, base = child.index(), normalized
                                break
                        except ValueError:
                            continue
                if base is None:
                    return False
            else:
                return False
            relative = os.path.relpath(target, base)
            if relative not in ('.', ''):
                for part in relative.split(os.sep):
                    self._expand_index(node)
                    self.tree.expand(node)
                    parent_item = self.model.itemFromIndex(node)
                    next_node = None
                    for i in range(parent_item.rowCount()):
                        child = parent_item.child(i)
                        if child is not None and child.text().casefold() == part.casefold():
                            next_node = child.index()
                            break
                    if next_node is None:
                        return False
                    node = next_node
            self.tree.setCurrentIndex(node)
            self.tree.scrollTo(node, QAbstractItemView.ScrollHint.EnsureVisible)
            return True
        finally:
            self._syncing_directory = False
            self._schedule_tree_state_save()

    def collapse_departed_child(self, previous_directory, parent_directory):
        """Close the child just exited by a List-side parent navigation.

        The new breadcrumb was already synchronized by the caller. Suppress
        QFileSystemModel disclosure callbacks so collapsing a branch NEVER
        navigates back into that child or steals Remote's logical focus.
        """
        if not previous_directory or not parent_directory:
            return False
        import ntpath
        old = ntpath.normcase(ntpath.normpath(str(previous_directory)))
        parent_path = ntpath.normcase(ntpath.normpath(str(parent_directory)))
        if ntpath.normcase(ntpath.normpath(ntpath.dirname(old))) != parent_path:
            return False
        parent_index = self.tree.currentIndex()
        if (not parent_index.isValid() or
                ntpath.normcase(ntpath.normpath(
                    str(self._index_path(parent_index) or ''))) != parent_path):
            return False
        item = self.model.itemFromIndex(parent_index)
        if item is None:
            return False
        for row in range(item.rowCount()):
            child = item.child(row)
            if child is None:
                continue
            index = child.index()
            child_path = self._index_path(index)
            if (child_path and
                    ntpath.normcase(ntpath.normpath(str(child_path))) == old):
                if self.tree.isExpanded(index):
                    old_sync = self._syncing_directory
                    self._syncing_directory = True
                    try:
                        self.tree.collapse(index)
                    finally:
                        self._syncing_directory = old_sync
                    self._schedule_tree_state_save()
                return True
        return False

    def can_rename_folder(self, path):
        """Never invalidate an authored first-column shortcut or drive root."""
        for row in range(self.model.rowCount()):
            root = self.model.index(row, 0)
            if self._index_path(root) == path:
                return False
            # Drives directly beneath virtual PC are navigation anchors.
            root_item = self.model.itemFromIndex(root)
            if root_item is not None and (root_item.data(_DATA_ROLE) or {}).get('pc'):
                for index in range(root_item.rowCount()):
                    if self._index_path(root_item.child(index).index()) == path:
                        return False
        index = self.tree.currentIndex()
        return bool(index.isValid() and self._index_path(index) == path
                    and index.parent().isValid())

    def begin_folder_rename(self, path):
        """Edit a real folder name in Files Exp, not in the main Files grid."""
        if not self.can_rename_folder(path) or not os.path.isdir(path):
            return False
        index = self.tree.currentIndex()
        item = self.model.itemFromIndex(index)
        if item is None:
            return False
        self._selection_timer.stop()
        self.tree.clear_wheel_pending()
        item.setEditable(True)
        self._rename_in_progress = (item, path)
        self.tree.setFocus(Qt.FocusReason.OtherFocusReason)
        self.tree.edit(index)
        return True

    def _close_folder_rename_editor(self, *_):
        # Escape/cancel must not leave a pending rename armed for a later edit.
        pending = self._rename_in_progress
        self._rename_in_progress = None
        if pending is not None:
            item, _ = pending
            item.setEditable(False)

    def _rewrite_child_paths(self, item, old_root, new_root):
        """Keep already-expanded child branches navigable after a rename."""
        for position in range(item.rowCount()):
            child = item.child(position)
            if child is None:
                continue
            data = child.data(_DATA_ROLE)
            if not isinstance(data, dict) or not data.get('path'):
                continue  # Lazy placeholder, not a physical folder.
            try:
                relative = Path(data['path']).relative_to(Path(old_root))
            except ValueError:
                continue
            new_path = str(Path(new_root) / relative)
            child.setData({**data, 'path': new_path}, _DATA_ROLE)
            child.setToolTip(new_path)
            self._rewrite_child_paths(child, old_root, new_root)

    def _finish_folder_rename(self, changed):
        pending = self._rename_in_progress
        if pending is None or changed is not pending[0]:
            return
        self._rename_in_progress = None
        item, old_path = pending
        new_name = item.text()
        item.setEditable(False)
        if new_name == Path(old_path).name:
            return
        try:
            # Share the exact Windows name validation and collision protection
            # already used by Files and the ordinary context menu.
            new_path = str(rename_file_or_folder(old_path, new_name))
        except (OSError, ValueError) as exc:
            item.setText(Path(old_path).name)
            launcher = getattr(self, '_launcher', None)
            if launcher is None:
                remote = self.parentWidget()
                launcher = remote.parent() if remote is not None else None
            launcher.error('名前を変更できませんでした: ' + str(exc))
            return
        item.setData({'path': new_path, 'pc': False}, _DATA_ROLE)
        item.setToolTip(new_path)
        self._rewrite_child_paths(item, old_path, new_path)
        self._selection_timer.stop()
        self.folder_renamed.emit(old_path, new_path)

    def reflect_deleted_folder(self, deleted_path):
        """Remove deleted branches without collapsing unrelated open paths."""
        target = os.path.normcase(os.path.normpath(str(deleted_path)))
        self._selection_timer.stop()
        def prune(parent):
            for row in range(parent.rowCount() - 1, -1, -1):
                item = parent.child(row)
                if item is None:
                    continue
                data = item.data(_DATA_ROLE)
                path = data.get('path') if isinstance(data, dict) else None
                if path and os.path.normcase(os.path.normpath(str(path))) == target:
                    parent.removeRow(row)
                else:
                    prune(item)
        # QTreeView may emit currentChanged while removing a selected row;
        # do not interpret that incidental replacement as a folder click.
        previous_sync = self._syncing_directory
        self._syncing_directory = True
        try:
            prune(self.model.invisibleRootItem())
        finally:
            self._syncing_directory = previous_sync
            self._selection_timer.stop()

    def reflect_external_folder_rename(self, old_path, new_path):
        """Keep loaded tree nodes (and expanded descendants) coherent with a
        rename committed by Remote's OTHER filesystem context menu.
        """
        wanted = os.path.normcase(os.path.normpath(str(old_path)))
        def walk(parent):
            for i in range(parent.rowCount()):
                item = parent.child(i)
                if item is None:
                    continue
                data = item.data(_DATA_ROLE)
                if isinstance(data, dict) and data.get('path'):
                    current = os.path.normcase(os.path.normpath(str(data['path'])))
                    if current == wanted:
                        item.setText(Path(new_path).name)
                        item.setData({**data, 'path': str(new_path)}, _DATA_ROLE)
                        item.setToolTip(str(new_path))
                        self._rewrite_child_paths(item, old_path, new_path)
                        return True
                if walk(item):
                    return True
            return False
        return walk(self.model.invisibleRootItem())

    def _show_folder_context(self, local_pos):
        # QAbstractScrollArea forwards positions in viewport coordinates.
        index = self.tree.indexAt(local_pos)
        path = self._index_path(index)
        if path is None:
            return
        self._selection_timer.stop()
        self.tree.setCurrentIndex(index)
        self._selection_timer.stop()
        self.folder_context_requested.emit(path, self.tree.viewport().mapToGlobal(local_pos))

    def _expand_index(self, index):
        """Populate only the opened branch. No filesystem write or navigation."""
        item = self.model.itemFromIndex(index)
        if item is None or item.data(_LOADED_ROLE):
            return
        item.setData(True, _LOADED_ROLE)
        data = item.data(_DATA_ROLE)
        if not isinstance(data, dict):
            return
        if data['pc']:
            children = [(row['title'], row['launch_browse_target'])
                        for row in drive_rows()]
        else:
            children = subdirectories(data['path'])
        for label, path in children:
            self._append_folder(item, label, path)
        # Add children before removing the placeholder, otherwise Qt can
        # collapse an expanded branch when its last child temporarily vanishes.
        item.removeRow(0)
        self.refresh_transfer_visuals()

    @staticmethod
    def _tree_node_key(item):
        """Stable (shortcut identity, physical path) across sorted children.

        The same physical directory can occur under several registered roots.
        Keep each alias separate; virtual PC has no filesystem path.
        """
        if item is None:
            return None
        info = item.data(_DATA_ROLE)
        if not isinstance(info, dict):
            return None  # Placeholder row, not a real folder.
        root = item
        while root.parent() is not None:
            parent = root.parent()
            # QStandardItemModel can expose invisibleRootItem() as the
            # top-level item's parent. It is not a registered folder.
            if not isinstance(parent.data(_DATA_ROLE), dict):
                break
            root = parent
        root_info = root.data(_DATA_ROLE) or {}
        root_path = ('<PC>' if root_info.get('pc') else
                     os.path.normcase(os.path.normpath(str(root_info.get('path') or ''))))
        node_path = ('<PC>' if info.get('pc') else
                     os.path.normcase(os.path.normpath(str(info.get('path') or ''))))
        return [root.text(), root_path, node_path]

    def _capture_tree_state(self):
        opened = []
        def visit(parent):
            for row in range(parent.rowCount()):
                item = parent.child(row)
                if item is None:
                    continue
                key = self._tree_node_key(item)
                if key is not None and self.tree.isExpanded(item.index()):
                    opened.append(key)
                    visit(item)
        visit(self.model.invisibleRootItem())
        selected_item = self.model.itemFromIndex(self.tree.currentIndex())
        selected = self._tree_node_key(selected_item)
        return {
            'version': 1, 'expanded': opened,
            'selected': selected,
            'scroll_y': self.tree.verticalScrollBar().value(),
            'scroll_x': self.tree.horizontalScrollBar().value(),
        }

    def _schedule_tree_state_save(self, *_):
        if (self._settings is not None and not self._restoring_tree
                and not self._syncing_directory):
            self._tree_state_timer.start()

    def _save_tree_state(self):
        if self._settings is None or self._restoring_tree or self._syncing_directory:
            return
        state = self._capture_tree_state()
        if getattr(self, '_embedded', False):
            self._settings.setValue('files_exp_embedded/tree_state_v1',
                                    json.dumps(state, ensure_ascii=False))
        else:
            self._settings.setValue('remote_files_exp/tree_state_v1',
                                    json.dumps(state, ensure_ascii=False))
        self._settings.sync()

    def restore_previous_tree_state(self):
        """Restore opened paths, current item and scroll without navigation.

        No previous snapshot: the caller may sync to Launch's breadcrumb.
        A stale/missing folder is simply skipped. HOME remains a hard reset.
        """
        if self._settings is None:
            return False
        key = ('files_exp_embedded/tree_state_v1' if getattr(self, '_embedded', False)
               else 'remote_files_exp/tree_state_v1')
        raw = self._settings.value(key, '')
        try:
            state = json.loads(raw) if isinstance(raw, str) else None
        except (ValueError, TypeError):
            return False
        if not isinstance(state, dict) or state.get('version') != 1:
            return False
        expanded = state.get('expanded', [])
        if not isinstance(expanded, list):
            return False
        # Do not allow a corrupted/hostile state.ini to traverse unlimited rows.
        keys = {tuple(value) for value in expanded[:800]
                if isinstance(value, list) and len(value) == 3
                and all(isinstance(piece, str) for piece in value)}
        selection = state.get('selected')
        selected_key = (tuple(selection) if isinstance(selection, list)
                        and len(selection) == 3
                        and all(isinstance(piece, str) for piece in selection)
                        else None)
        previous_restoring = self._restoring_tree
        previous_sync = self._syncing_directory
        self._restoring_tree = True
        self._syncing_directory = True
        previous_animated = self.tree.isAnimated()
        self.tree.setAnimated(False)
        found_selected = selected_key is None
        try:
            self._selection_timer.stop()
            self.tree.clear_wheel_pending()
            def visit(parent):
                nonlocal found_selected
                for row in range(parent.rowCount()):
                    item = parent.child(row)
                    if item is None:
                        continue
                    key = self._tree_node_key(item)
                    if key is None:
                        continue
                    # Expand lazy parents before locating saved descendants.
                    if tuple(key) in keys:
                        self._expand_index(item.index())
                        self.tree.setExpanded(item.index(), True)
                    if tuple(key) == selected_key:
                        self.tree.setCurrentIndex(item.index())
                        found_selected = True
                    if self.tree.isExpanded(item.index()):
                        visit(item)
            visit(self.model.invisibleRootItem())
        finally:
            self.tree.setAnimated(previous_animated)
            self._syncing_directory = previous_sync
            self._restoring_tree = previous_restoring
            self._selection_timer.stop()
        if not found_selected:
            # Removed/renamed folder: let the caller choose the valid current
            # Launch breadcrumb instead of selecting an unrelated sibling.
            return False
        try:
            y = max(0, int(state.get('scroll_y', 0)))
            x = max(0, int(state.get('scroll_x', 0)))
        except (ValueError, TypeError):
            y = x = 0
        self._pending_restored_scroll = (y, x)
        return True

    def finish_restoring_tree_scroll(self):
        """Scrollbars have their real extents only after the tool is shown."""
        pending = self._pending_restored_scroll
        self._pending_restored_scroll = None
        if pending is None:
            return
        self._restoring_tree = True
        try:
            y, x = pending
            ybar = self.tree.verticalScrollBar()
            xbar = self.tree.horizontalScrollBar()
            ybar.setValue(max(ybar.minimum(), min(y, ybar.maximum())))
            xbar.setValue(max(xbar.minimum(), min(x, xbar.maximum())))
        finally:
            self._restoring_tree = False

    def _arm_manual_move(self):
        # Native startSystemMove may consume the mouse-release event, so the
        # actual moveEvent (not a press alone) is the evidence of a drag.
        self._header_move_origin = self.pos()
        self._header_move_armed = True

    def _save_manual_position(self):
        if self._settings is not None and self._manual_position:
            self._settings.setValue('remote_files_exp/manual_position', True)
            self._settings.setValue('remote_files_exp/manual_x', self.x())
            self._settings.setValue('remote_files_exp/manual_y', self.y())
            self._settings.sync()

    def saved_manual_position(self):
        if not self._manual_position or self._settings is None:
            return None
        try:
            return QPoint(int(self._settings.value('remote_files_exp/manual_x')),
                          int(self._settings.value('remote_files_exp/manual_y')))
        except (ValueError, TypeError):
            return None

    def place_automatically(self, x, y, height=None):
        """Programmatic placement must never become a user position override."""
        self._automatic_placement = True
        try:
            if height is not None and not self._manual_height:
                self.resize(self.width(), height)
            self.move(x, y)
        finally:
            self._automatic_placement = False

    def reset_grid_layout(self):
        """User-requested reset via the Exp header context menu."""
        self._manual_position = False
        self._manual_height = False
        self._header_move_armed = False
        self._grid_height_mode = True
        if self._settings is not None:
            for key in ('remote_files_exp/manual_position',
                        'remote_files_exp/manual_x', 'remote_files_exp/manual_y',
                        'remote_files_exp/manual_height'):
                self._settings.remove(key)
            self._settings.sync()
        remote = self.parentWidget()
        if remote is not None and hasattr(remote, 'align_with_files_grid'):
            remote.align_with_files_grid()

    def _show_layout_menu(self, position):
        launcher = self._launcher
        if self._embedded or not getattr(launcher, 'files_root_hidden_mode', False):
            return
        menu = QMenu(self)
        reset = menu.addAction('Launchのグリッド位置・高さに再整列')
        reset.setEnabled(self._manual_position or self._manual_height)
        chosen = menu.exec(position)
        if chosen is reset:
            self.reset_grid_layout()

    def _save_size(self):
        if (self._settings is not None and not self._restoring_size
                and not getattr(self, '_embedded', False)):
            self._settings.setValue('remote_files_exp/width', self.width())
            # Auto-fit height is a display result, not a new user preference:
            # preserve the old saved height for non-experimental mode.
            if not getattr(self, '_grid_height_mode', False) or getattr(self, '_manual_height', False):
                self._settings.setValue('remote_files_exp/height', self.height())
            self._settings.sync()

    def moveEvent(self, event):
        super().moveEvent(event)
        if (self._header_move_armed and not self._automatic_placement
                and self.isVisible() and self._header_move_origin != self.pos()):
            self._manual_position = True
            self._header_move_origin = self.pos()
            self._position_save_timer.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.isVisible() and not getattr(self, '_embedded', False):
            if (self._grid_height_mode and not self._automatic_placement
                    and event.oldSize().height() != event.size().height()):
                self._manual_height = True
                if self._settings is not None:
                    self._settings.setValue('remote_files_exp/manual_height', True)
            self._size_save_timer.start()
            remote = self.parentWidget()
            if remote is not None and hasattr(remote, 'position_files_exp'):
                QTimer.singleShot(0, remote.position_files_exp)

    def hideEvent(self, event):
        self._size_save_timer.stop()
        self._position_save_timer.stop()
        self._tree_state_timer.stop()
        self._save_tree_state()
        if not self._embedded:
            self._save_size()
            self._save_manual_position()
        self._selection_timer.stop()
        super().hideEvent(event)

    def closeEvent(self, event):
        self._size_save_timer.stop()
        self._position_save_timer.stop()
        self._tree_state_timer.stop()
        self._save_tree_state()
        if not self._embedded:
            self._save_size()
            self._save_manual_position()
        super().closeEvent(event)

    def paintEvent(self, event):
        """Draw exactly the same rounded, hairline window rim as LaunchRemote."""
        if self._embedded:
            return super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self._exp_background)
        painter.setPen(QPen(self._exp_outline, 1))
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5),
                                10, 10)
        painter.end()

    def set_operating_active(self, active):
        """Embedded AND standalone Exp share the same actual/memory colors."""
        active = bool(active)
        for widget in (self.exp_header, self.tree):
            if widget.property('operatingActive') != active:
                widget.setProperty('operatingActive', active)
                widget.style().unpolish(widget)
                widget.style().polish(widget)
                widget.update()
        self.tree.viewport().update()

    def apply_theme(self, theme):
        colors = theme_palette(theme)
        self.tree.current_outline_color = QColor(colors['focus_outline'])
        # Share the same vector house icon as the Remote HOME, on theme change.
        self.home_button.setIcon(browser_navigation_icon('home', theme_family(theme)))
        self._exp_background = QColor(colors['panel'])
        self._exp_outline = QColor('#ccd3d7')  # identical to LaunchRemote
        # Slightly lighter than the toolbar immediately above the embedded Exp.
        exp_header = '#f8fcf9' if theme_family(theme) == 'light' else '#395247'
        # Sakura Editor-inspired warm white, lightened to #FFFEF9.
        operating_bg = '#FFFEF9' if theme_family(theme) == 'light' else '#463a32'
        operating_title = '#FFF9EF' if theme_family(theme) == 'light' else '#624936'
        operating_outline = '#d9b991' if theme_family(theme) == 'light' else '#ad8258'
        self.setStyleSheet(f"""
            QWidget#remoteFilesExplorer, QWidget#embeddedFilesExplorer {{background:transparent;color:{colors['text']};
                border:0;}}
            QFrame#filesExpHeader {{background:{exp_header};
                border:1px solid transparent;border-bottom:1px solid {colors['panel_border']};
                border-radius:0px;}}
            QFrame#filesExpHeader[operatingActive="true"] {{
                background:{operating_title};border:1px solid {operating_outline};
                border-radius:3px;}}
            QLabel#filesExpTitle {{background:transparent;color:{colors['text']};
                font-size:12px;font-weight:bold;border:0;}}
            /* Identical 28x24 HOME button styling to LaunchRemote. */
            QPushButton#filesExpHomeButton {{background:{colors['panel_header']};
                color:{colors['text']};border:1px solid {colors['panel_border']};
                border-radius:7px;padding:0;}}
            QPushButton#filesExpHomeButton:hover {{background:{colors['hover']};}}
            QPushButton#filesExpHomeButton:pressed {{background:{colors['selection']};}}
            /* Identical visual rules to LaunchRemote's 22x22 icon button. */
            QPushButton#filesExpClose {{background:{colors['panel_header']};color:{colors['text']};
                border:1px solid {colors['panel_border']};border-radius:5px;
                font-size:12px;padding:0;}}
            QPushButton#filesExpClose:hover {{background:{colors['hover']};}}
            QPushButton#filesExpClose:pressed {{background:{colors['selection']};}}
            QFrame#filesExpFooter {{background:{colors['panel']};border:0;}}
            QLabel#filesExpHint {{background:transparent;color:{colors['muted_text']};
                font-size:10px;border:0;}}
            QTreeView#filesExpTree {{background:{colors['panel']};color:{colors['text']};
                border:0;outline:0;}}
            QTreeView#filesExpTree[operatingActive="true"] {{background:{operating_bg};}}
            QTreeView#filesExpTree::item {{height:24px;padding:0;}}
            /* Passive memory = outlined current row, NO green fill. */
            QTreeView#filesExpTree::item:selected,
            QTreeView#filesExpTree::item:selected:!active {{
                background:transparent;color:{colors['text']};}}
            /* True current = green fill AND the outline painted in drawRow.
               Both standalone and embedded Exp use the shared operating target. */
            QTreeView#filesExpTree[operatingActive="true"]::item:selected,
            QTreeView#filesExpTree[operatingActive="true"]::item:selected:!active {{
                background:{colors['selection']};color:{colors['text']};}}
            QTreeView#filesExpTree::item:hover:!selected {{background:{colors['hover']};}}
        """)
        self.update()
