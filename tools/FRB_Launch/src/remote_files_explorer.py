"""Read-only folder-tree preview of the registered Files first-column roots.

Roots are taken from Launch's *rendered* Files workspace (not a copy of its
JSON). Child folders are loaded lazily. Selecting/expanding never navigates the
main Files pane, opens anything, or mutates the filesystem.
"""

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QLabel, QStyle,
                               QTreeView, QVBoxLayout, QWidget)
from launch_appearance import theme_palette
from remote_files_exp_roots import registered_folder_roots, subdirectories
from system_drives import drive_rows

_DATA_ROLE = Qt.ItemDataRole.UserRole + 1
_LOADED_ROLE = Qt.ItemDataRole.UserRole + 2


class RemoteFilesExplorer(QWidget):
    """Multiple pinned directory roots, with one-level-at-a-time expansion."""

    def __init__(self, remote, theme):
        # Tool window follows the owning Remote but accepts normal tree input.
        super().__init__(remote, Qt.WindowType.Tool)
        self.setObjectName('remoteFilesExplorer')
        self.setWindowTitle('Files Exp — 登録フォルダーツリー（試作）')
        self.resize(330, 425)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(9, 8, 9, 8)
        layout.setSpacing(5)
        title = QLabel('Files Exp  |  第1列の登録フォルダー', self)
        title.setObjectName('filesExpTitle')
        layout.addWidget(title)
        description = QLabel('▶ で展開／折りたたみ  ·  選択しても移動しません', self)
        description.setObjectName('filesExpHint')
        description.setWordWrap(True)
        layout.addWidget(description)

        # QFileSystemModel accepts only ONE visual root. For several independent
        # shortcut roots retain QTreeView and use a lazy, read-only item model.
        self.model = QStandardItemModel(self)
        self.tree = QTreeView(self)
        self.tree.setObjectName('filesExpTree')
        self.tree.setModel(self.model)
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setUniformRowHeights(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setItemsExpandable(True)
        self.tree.setExpandsOnDoubleClick(True)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree.setDragEnabled(False)
        self.tree.setAcceptDrops(False)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.tree.expanded.connect(self._expand_index)
        layout.addWidget(self.tree, 1)

        style = QApplication.style()
        self._folder_icon = style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        self._pc_icon = style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.apply_theme(theme)

    def _append_folder(self, parent, label, path, *, pc=False, missing=False):
        item = QStandardItem(self._pc_icon if pc else self._folder_icon, label)
        item.setEditable(False)
        item.setDragEnabled(False)
        item.setDropEnabled(False)
        item.setData({'path': path, 'pc': pc}, _DATA_ROLE)
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
        return item

    def set_roots(self, rows, expand):
        """Re-sync from currently rendered Files column one on each opening.

        Does not rely on current breadcrumb or selected folder. Keeps duplicate
        registered paths as separately named roots, in their displayed order.
        """
        roots = registered_folder_roots(rows, expand)
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['フォルダー'])
        parent = self.model.invisibleRootItem()
        for root in roots:
            path = root['path']
            self._append_folder(parent, root['label'], path, pc=root['pc'],
                                missing=not root['pc'] and not os.path.isdir(path))
        return len(roots)

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

    def apply_theme(self, theme):
        colors = theme_palette(theme)
        self.setStyleSheet(f"""
            QWidget#remoteFilesExplorer {{background:{colors['panel']};color:{colors['text']};}}
            QLabel#filesExpTitle {{background:transparent;color:{colors['text']};
                font-size:12px;font-weight:bold;}}
            QLabel#filesExpHint {{background:transparent;color:{colors['muted_text']};
                font-size:10px;}}
            QTreeView#filesExpTree {{background:{colors['panel']};color:{colors['text']};
                border:1px solid {colors['panel_border']};outline:0;}}
            QTreeView#filesExpTree::item {{height:25px;}}
            QTreeView#filesExpTree::item:selected {{background:{colors['selection']};
                color:{colors['text']};}}
            QTreeView#filesExpTree::item:hover:!selected {{background:{colors['hover']};}}
        """)
