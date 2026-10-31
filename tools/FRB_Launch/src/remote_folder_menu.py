"""Remote-only, breadcrumb-rooted filesystem preview.

Hover previews child directories.  Only a *click* on a folder commits the
Files breadcrumb; the menu remains visible and rebases to the new location.
The menu does not own any independent 'current directory' state in Launcher.
"""
from pathlib import Path
import os

from PySide6.QtCore import Qt, QTimer, QFileInfo, QEvent
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QMenu, QWidgetAction, QWidget, QHBoxLayout, QLineEdit, QLabel


def directory_entries(directory):
    """Enumerate one directory only; never recurse when hovering.

    Preserve file paths as objects (rather than interpreting labels as paths).
    """
    entries = []
    with os.scandir(directory) as iterator:
        for entry in iterator:
            try:
                is_folder = entry.is_dir(follow_symlinks=False)
                is_file = entry.is_file(follow_symlinks=False)
            except OSError:
                continue
            if is_folder or is_file:
                entries.append((entry.name, entry.path, is_folder))
    entries.sort(key=lambda v: (not v[2], v[0].casefold()))
    return entries


class RemoteFolderListMenu(QMenu):
    """One searchable column in a right-opening Remote folder tree."""

    def __init__(self, launcher, directory, root=None, parent=None):
        super().__init__(parent)
        self.launcher = launcher
        self.root = root or self
        self.directory = str(directory)
        self._entries = []
        self._mouse_press_action = None
        self._populated = False
        self.setObjectName('remoteFolderListColumn')
        self.setToolTipsVisible(True)
        # IMPORTANT: this menu is a real child of an ordinary QMenu (the
        # Remote's Files background context menu). Keep Qt.Popup semantics.
        # Turning it into an independent Qt.Tool breaks Qt's submenu mouse
        # tracking: the opener loses its active child as the pointer crosses
        # into this list, and the list immediately disappears.
        self.setMinimumWidth(250)
        self.setMaximumWidth(450)
        self.setStyleSheet('QMenu { menu-scrollable: 1; }')
        self.aboutToShow.connect(self.ensure_populated)
        # Intercept the menu's native action dispatch *before* QMenu can
        # trigger/hide a popup. In particular, an addMenu() folder QAction
        # is NOT a normal triggered action, and native QMenu eats its clicks.
        # Installing on each column also covers recursively opened submenus.
        self.installEventFilter(self.root)

    def ensure_populated(self):
        if not self._populated:
            self.populate()

    def populate(self):
        self.clear()
        self._entries = []
        self._populated = True
        search = QWidget(self)
        layout = QHBoxLayout(search)
        layout.setContentsMargins(5, 4, 5, 4)
        layout.setSpacing(3)
        icon = QLabel('⌕', search)
        edit = QLineEdit(search)
        edit.setPlaceholderText('この列から探す…')
        edit.setClearButtonEnabled(True)
        layout.addWidget(icon)
        layout.addWidget(edit)
        widget_action = QWidgetAction(self)
        widget_action.setDefaultWidget(search)
        self.addAction(widget_action)
        self.filter_edit = edit
        self.filter_action = widget_action
        edit.textChanged.connect(self.apply_filter)
        self.addSeparator()
        try:
            entries = directory_entries(self.directory)
        except (OSError, ValueError) as exc:
            disabled = self.addAction('（一覧を読み込めません）')
            disabled.setToolTip(str(exc))
            disabled.setEnabled(False)
            return
        for name, path, is_folder in entries:
            if is_folder:
                # create lazy submenus, populated only on hover.  A folder
                # never changes the current location until left-clicked.
                child = RemoteFolderListMenu(self.launcher, path, self.root, self)
                action = self.addMenu(child)
                action.setText(name)
            else:
                action = self.addAction(name)
            action.setIcon(self.launcher.file_icons.icon(QFileInfo(path)))
            action.setIconVisibleInMenu(True)
            action.setData((path, is_folder))
            action.setToolTip(path)
            self._entries.append((name, action))
        if not entries:
            disabled = self.addAction('（空のフォルダー）')
            disabled.setEnabled(False)

    def apply_filter(self, query):
        term = query.strip().casefold()
        for name, action in self._entries:
            action.setVisible(term in name.casefold())
        current = self.activeAction()
        if current is not None and not current.isVisible():
            self.setActiveAction(None)

    def _row_at(self, event):
        action = self.actionAt(event.position().toPoint())
        data = action.data() if action is not None else None
        return action, data if isinstance(data, tuple) and len(data) == 2 else None

    def eventFilter(self, watched, event):
        """Retain the popup while handling file/folder input explicitly.

        Native QMenu may dismiss a submenu before mouseReleaseEvent or
        mouseDoubleClickEvent reaches a subclass override. An event filter on
        every column sees the press first, and prevents its QAction from being
        auto-triggered/closed by Qt. Hover remains native (submenus still open).
        """
        if not isinstance(watched, RemoteFolderListMenu):
            return super().eventFilter(watched, event)
        kind = event.type()
        if kind == QEvent.Type.ContextMenu:
            # Qt can send this *after* a right-button release. We handled
            # the actual row with the press; do not let QMenu dismiss itself.
            event.accept()
            return True
        if kind not in (QEvent.Type.MouseButtonPress,
                        QEvent.Type.MouseButtonRelease,
                        QEvent.Type.MouseButtonDblClick):
            return super().eventFilter(watched, event)
        action, data = watched._row_at(event)
        button = event.button()
        if kind == QEvent.Type.MouseButtonPress:
            if data and button in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
                path, is_folder = data
                watched._mouse_press_action = action
                watched.setActiveAction(action)
                if button == Qt.MouseButton.RightButton:
                    point = event.globalPosition().toPoint()
                    QTimer.singleShot(0, lambda p=path, folder=is_folder, at=point:
                                      self.open_entry_context(p, folder, at))
                elif is_folder:
                    # Retain the popup even if Qt emits a hide event before
                    # the queued navigation callback can run.
                    self.launcher._remote_folder_commit_pending = True
                    # A *press*, not a hover, is the commit boundary. Do not
                    # rely on QMenu delivering the corresponding release when
                    # another submenu is currently active.
                    QTimer.singleShot(0, lambda p=path: self.commit_directory(p))
                # First left click on a file is selection only. The second
                # click is recognized by MouseButtonDblClick below.
                event.accept()
                return True
        elif kind == QEvent.Type.MouseButtonDblClick:
            if data and button == Qt.MouseButton.LeftButton:
                path, is_folder = data
                if not is_folder:
                    QTimer.singleShot(0, lambda p=path: self.open_file(p))
                # Double-click on a folder is still only one navigation.
                event.accept()
                return True
        elif kind == QEvent.Type.MouseButtonRelease:
            if button in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
                pressed = watched._mouse_press_action is not None
                watched._mouse_press_action = None
                if data or pressed:
                    event.accept()
                    return True
        return super().eventFilter(watched, event)

    def open_entry_context(self, path, is_folder, pos):
        """Use exactly the safe search-results menu for files AND folders.

        Opening a second Qt popup can temporarily dismiss the original QMenu
        chain. Retain its references while the context menu is active and
        restore the original chain when the context menu closes.
        """
        target = Path(path)
        if not (target.is_dir() if is_folder else target.is_file()):
            return
        launcher = self.launcher
        row = {'item_kind': 'directory' if is_folder else 'command',
               'title': target.name}
        if is_folder:
            row['_file'] = str(target)  # resolve_context_target -> folder
        else:
            row['_browse_file'] = str(target)  # -> file
        launcher._remote_folder_commit_pending = True
        try:
            shown = launcher.show_launch_context_menu(
                pos, row, context_parent=launcher, force_search_context=True)
        except Exception:
            launcher._remote_folder_commit_pending = False
            raise
        context = getattr(launcher, '_launch_context_menu', None)
        if not shown or context is None:
            launcher._remote_folder_commit_pending = False
            return
        context.aboutToHide.connect(
            lambda: QTimer.singleShot(0, self._restore_after_context))

    def _restore_after_context(self):
        """Reopen the retained menu only after the safe context popup closes."""
        if getattr(self.launcher, '_remote_folder_root_menu', None) is self:
            self._keep_preview_visible()
        else:
            self.launcher._remote_folder_commit_pending = False

    def commit_directory(self, path):
        """Route through Files' real navigator, then keep preview open."""
        view = self.launcher.expanded_view
        if (not view.isVisible() or view._workspace_mode != 'files'
                or not Path(path).is_dir()):
            return
        self.launcher._remote_folder_navigation = True
        # Qt may queue the parent menu's focus-loss event after the click.
        # Keep its references until our next-event-loop retention check.
        self.launcher._remote_folder_commit_pending = True
        try:
            changed = view.go_to_directory(path, preserve_remote_popup=True)
        except Exception:
            self.launcher._remote_folder_commit_pending = False
            raise
        finally:
            self.launcher._remote_folder_navigation = False
        if changed:
            # Root menu is the retained interaction surface, independently
            # of the submenu the user clicked. Discard old child previews.
            self.directory = str(view.current_directory())
            self.populate()
            # Keep the opener and its folder-list child together: opening the
            # child alone leaves an orphan menu after the parent loses focus.
            QTimer.singleShot(0, self._keep_preview_visible)
        else:
            self.launcher._remote_folder_commit_pending = False

    def _keep_preview_visible(self):
        try:
            launcher = self.launcher
            remote = getattr(launcher, 'remote_window', None)
            opener = getattr(launcher, '_remote_folder_opener', None)
            if (getattr(launcher, '_remote_folder_root_menu', None) is not self
                    or remote is None or not remote.isVisible() or opener is None):
                return
            if not opener.isVisible():
                # Reopen only if Qt dismissed the popup during Files refresh.
                # The normal (still-visible) menu is never repositioned.
                pos = getattr(launcher, '_remote_folder_popup_pos', None)
                opener.popup(pos if pos is not None else QCursor.pos())
                launcher._launch_context_menu = opener
            if not self.isVisible():
                # Preserve the native QMenu parent/child chain on recovery.
                action = next((a for a in opener.actions() if a.menu() is self), None)
                if action is not None:
                    opener.setActiveAction(action)
                    point = opener.mapToGlobal(
                        opener.actionGeometry(action).topRight())
                    self.popup(point)
        finally:
            self.launcher._remote_folder_commit_pending = False

    def open_file(self, path):
        if not Path(path).is_file():
            return
        row = {'item_kind': 'command', 'title': Path(path).name,
               '_browse_file': str(path)}
        # Use existing file launch rules (incl. Studio JSON and file types).
        QTimer.singleShot(0, lambda r=row: self.launcher.activate(r))

    def open_file_context(self, path, pos):
        # Backward-compatible entry point for the Remote preview.
        self.open_entry_context(path, False, pos)
