"""Experimental embedded HTTP(S) viewer for the two Files columns.

Qt WebEngine is intentionally imported only when the user first opens a URL.
Existing Files widgets are kept alive in a separate QStackedWidget page.
"""
import os
from pathlib import Path, PureWindowsPath

from PySide6.QtCore import (QUrl, Qt, Signal, QStandardPaths, QSize, QPoint, QTimer, QFileInfo,
                            QPropertyAnimation, QEasingCurve, QThread, QEvent)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QVBoxLayout, QLineEdit,
                               QToolButton, QTabWidget, QTabBar, QMenu, QWidget, QLabel,
                               QScrollArea, QGraphicsOpacityEffect, QMessageBox, QFileIconProvider,
                               QTreeWidgetItem, QHeaderView, QAbstractItemView)
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineDownloadRequest
from PySide6.QtWebEngineWidgets import QWebEngineView

from browser_nav_icons import browser_navigation_icon
from launch_downloads import safe_download_name, unique_path, safe_extract_zip
from launch_appearance import theme_family, theme_palette, history_popup_qss
from browser_url_favorites import BrowserUrlFavorites, normalize_favorite_url
from combo_chevron_icon import combo_chevron_icon
from reorderable_tree import ReorderablePopupTree
from wheel_adaptive import wheel_steps
from history_wheel_navigation import history_target_index, warp_to_history_row
from PySide6.QtGui import QCursor, QColor, QPainter


class _ResizePreview(QWidget):
    """Opaque, in-memory last-frame preview during a live Windows resize.

    Chromium paints asynchronously. Enlarging QWebEngineView while dragging
    the frame can expose black right/bottom strips before its new texture is
    ready. Hide that surface and draw the previous frame at 1:1 scale, with
    the surrounding light panel color, until the resize finishes. No URL
    reload, disk screenshot or modification of the page is involved.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._snapshot = None
        self._fill = QColor('#fcfffd')
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.hide()

    def set_preview(self, snapshot, color):
        self._snapshot = snapshot if snapshot is not None and not snapshot.isNull() else None
        self._fill = QColor(color)
        self.update()

    def clear_preview(self):
        self._snapshot = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self._fill)
        if self._snapshot is not None:
            # Never stretch webpage text. Newly exposed space gets the light
            # panel color instead of a black Chromium backing surface.
            painter.drawPixmap(0, 0, self._snapshot)
        painter.end()


class _WebTabs(QTabWidget):
    """Keep a separate slot for '+' even when tabs start overflowing."""

    def resizeEvent(self, event):
        super().resizeEvent(event)
        bar = self.tabBar()
        if isinstance(bar, _WebTabBar):
            bar.reserve_new_tab_space()
            bar._queue_new_tab_position()
        owner = self.parentWidget()
        if owner is not None and hasattr(owner, '_position_resize_preview'):
            owner._position_resize_preview()


class _WebTabBar(QTabBar):
    """Chrome-like tabs with a SEPARATE '+' button beside the last tab.

    Important: the '+' must be a sibling of the tab bar, *not its child*.
    QTabWidget can give QTabBar exactly the width needed for the tabs.
    Clamping a child button inside that width overlays the last tab's X.
    """
    area_tab_requested = Signal(bool)
    area_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._new_tab_button = None
        self.setDrawBase(False)
        self.setExpanding(False)

    def set_new_tab_button(self, button):
        host = self.parentWidget()  # QTabWidget, which spans the entire strip.
        self._new_tab_button = button
        if host is not None and button.parentWidget() is not host:
            button.setParent(host)
        self.reserve_new_tab_space()
        button.show()
        self._queue_new_tab_position()

    def reserve_new_tab_space(self):
        """Leave room for '+' on narrow windows instead of covering a tab."""
        button = self._new_tab_button
        host = self.parentWidget()
        if button is None or host is None or host.width() <= 60:
            return
        max_width = max(40, host.width() - button.width() - 16)
        if self.maximumWidth() != max_width:
            self.setMaximumWidth(max_width)

    def position_new_tab_button(self):
        button = self._new_tab_button
        host = self.parentWidget()
        if button is None or host is None:
            return
        # tabRect includes title, favicon and the close X.  Using the host
        # coordinate system means '+' is *outside* the tab bar and cannot
        # steal the last tab's close-button area.
        last_right = self.tabRect(self.count() - 1).right() if self.count() else -1
        visible_right = min(last_right, self.width() - 1)
        pos = self.mapTo(host, QPoint(visible_right + 8 if self.count() else 6, 0))
        x = max(3, min(pos.x(), host.width() - button.width() - 4))
        y = self.mapTo(host, QPoint(0, max(0, (self.height() - button.height()) // 2))).y()
        button.move(x, y)
        button.raise_()

    def _queue_new_tab_position(self):
        QTimer.singleShot(0, self.position_new_tab_button)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._queue_new_tab_position()

    def tabLayoutChange(self):
        super().tabLayoutChange()
        self._queue_new_tab_position()

    def tabInserted(self, index):
        super().tabInserted(index)
        self._queue_new_tab_position()

    def tabRemoved(self, index):
        super().tabRemoved(index)
        self._queue_new_tab_position()

    def mousePressEvent(self, event):
        self.area_clicked.emit()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if (event.key() in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab) and
                event.modifiers() in (Qt.KeyboardModifier.NoModifier,
                                      Qt.KeyboardModifier.ShiftModifier)):
            backward = (event.key() == Qt.Key.Key_Backtab or
                        bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier))
            self.area_tab_requested.emit(backward)
            event.accept()
            return
        super().keyPressEvent(event)


class _WebCloseButton(QToolButton):
    """Chrome-like quiet X; intentionally does not add a new tab stop."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('launchWebCloseButton')
        self.setFixedSize(21, 21)
        self.setIconSize(QSize(18, 18))
        self.setAutoRaise(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setToolTip('タブを閉じる')


class _LaunchWebPage(QWebEngineView):
    """Keep new-window and 'Open link in new tab' inside FRB Launch."""

    def __init__(self, owner):
        super().__init__(owner.tabs)
        self._owner = owner
        self._last_viewport_size = None
        self._repairing_surface = False
        self._resize_surface_timer = QTimer(self)
        self._resize_surface_timer.setSingleShot(True)
        self._resize_surface_timer.timeout.connect(self._repair_resize_surface)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # On some Windows/QtWebEngine combinations the Chromium surface
        # retains the OLD dimensions after QTabWidget is enlarged. The newly
        # exposed right/bottom area is black. QSS/background does not fix it.
        previous = self._last_viewport_size
        self._last_viewport_size = event.size()
        if (previous is not None and previous != event.size()
                and not self._repairing_surface
                and theme_family(getattr(self._owner, '_current_theme', 'dark')) == 'light'):
            self._resize_surface_timer.start(160)

    def _repair_resize_surface(self):
        """Recreate the visible surface after resizing, without a URL reload."""
        if (self._repairing_surface or not self.isVisible()
                or self._owner.current_view() is not self
                or theme_family(getattr(self._owner, '_current_theme', 'dark')) != 'light'):
            return
        self._repairing_surface = True
        try:
            self.hide()
            self.show()
            self.update()
            # Give responsive websites the final viewport measurements.
            self.page().runJavaScript('window.dispatchEvent(new Event("resize"))')
        finally:
            self._repairing_surface = False

    def mousePressEvent(self, event):
        self._owner.surface_selected.emit('web_body')
        super().mousePressEvent(event)

    def createWindow(self, window_type):
        # WebBrowserBackgroundTab must NOT replace the currently active page.
        background = window_type == QWebEnginePage.WebWindowType.WebBrowserBackgroundTab
        return self._owner.add_tab(activate=not background)


class _DownloadRow(QFrame):
    """A Chrome-like entry; actions appear on hover, not as permanent clutter."""
    def __init__(self, owner, record, parent=None):
        super().__init__(parent)
        self.record = record
        self.setObjectName('launchDownloadRow')
        self.setFixedHeight(67)
        row = QHBoxLayout(self)
        row.setContentsMargins(10, 6, 8, 6)
        row.setSpacing(9)
        # Reuse Windows' registered file-type icon (ZIP/PDF/PNG/etc.), not a
        # generic paper icon.  The shell is asked only about the extension,
        # never to open or inspect the downloaded file itself.
        file_icon = QLabel(self)
        file_icon.setFixedSize(30, 30)
        file_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_icon.setPixmap(owner.download_file_icon(record['path']).pixmap(QSize(26, 26)))
        row.addWidget(file_icon)
        texts = QVBoxLayout()
        texts.setSpacing(2)
        self.name = QLabel(Path(record['path']).name, self)
        self.name.setObjectName('launchDownloadName')
        self.name.setToolTip(record['path'])
        self.name.setMaximumWidth(218)
        self.name.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.status = QLabel(self)
        self.status.setObjectName('launchDownloadStatus')
        texts.addWidget(self.name)
        texts.addWidget(self.status)
        row.addLayout(texts, 1)
        self.folder = QToolButton(self)
        self.folder.setObjectName('launchDownloadAction')
        self.folder.setIcon(browser_navigation_icon('folder_open', theme_family(
            getattr(owner, '_current_theme', 'light'))))
        self.folder.setIconSize(QSize(22, 22))
        self.folder.setToolTip('エクスプローラーで保存フォルダーを開く')
        self.folder.setFixedSize(30, 28)
        policy = self.folder.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        self.folder.setSizePolicy(policy)
        self.folder.clicked.connect(lambda: owner.open_download_folder(record['path']))
        row.addWidget(self.folder)
        self.extract = QToolButton(self)
        self.extract.setObjectName('launchDownloadAction')
        self.extract.setIcon(browser_navigation_icon('unzip', theme_family(
            getattr(owner, '_current_theme', 'light'))))
        self.extract.setIconSize(QSize(22, 22))
        self.extract.setToolTip('ZIPを展開してフォルダーを開く')
        self.extract.setFixedSize(30, 28)
        policy = self.extract.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        self.extract.setSizePolicy(policy)
        self.extract.clicked.connect(lambda: owner.extract_download_zip(record['path']))
        row.addWidget(self.extract)
        self._show_actions(False)
        self.update_status()

    def _show_actions(self, hovered):
        complete = (self.record['request'].state() ==
                    QWebEngineDownloadRequest.DownloadState.DownloadCompleted)
        self.folder.setVisible(hovered and complete)
        self.extract.setVisible(hovered and complete and
                                self.record['path'].lower().endswith('.zip'))

    def enterEvent(self, event):
        self._show_actions(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._show_actions(False)
        super().leaveEvent(event)

    def update_status(self):
        request = self.record['request']
        state = request.state()
        if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            size = request.receivedBytes()
            self.status.setText(f'{size / 1024:.0f} KB ・ 完了' if size >= 0 else '完了')
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
            self.status.setText('キャンセルしました')
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
            self.status.setText('ダウンロード失敗')
        else:
            total = request.totalBytes()
            got = request.receivedBytes()
            self.status.setText(f'{min(100, int(got * 100 / total))}% ・ ダウンロード中'
                                if total > 0 else 'ダウンロード中…')


class _DownloadPanel(QFrame):
    """Persistent transient panel anchored to the download toolbar button."""
    def __init__(self, owner):
        super().__init__(owner, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.NoDropShadowWindowHint)
        self.setObjectName('launchDownloadsPanel')
        self.setFixedWidth(376)
        self.setMaximumHeight(480)
        self._rows = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(9, 9, 9, 9)
        layout.setSpacing(4)
        header = QHBoxLayout()
        title = QLabel('最近のダウンロード', self)
        title.setObjectName('launchDownloadsTitle')
        header.addWidget(title)
        header.addStretch()
        close = QToolButton(self)
        close.setObjectName('launchDownloadsClose')
        close.setText('×')
        close.setToolTip('閉じる')
        close.clicked.connect(self.hide)
        header.addWidget(close)
        layout.addLayout(header)
        self.scroll = QScrollArea(self)
        self.scroll.setObjectName('launchDownloadsScroll')
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.contents = QWidget(self.scroll)
        self.list_layout = QVBoxLayout(self.contents)
        self.list_layout.setContentsMargins(0, 2, 0, 2)
        self.list_layout.setSpacing(3)
        self.scroll.setWidget(self.contents)
        layout.addWidget(self.scroll)
        bottom = QToolButton(self)
        bottom.setObjectName('launchDownloadsFolder')
        bottom.setText('ダウンロードフォルダーを開く')
        bottom.clicked.connect(lambda: owner.open_download_folder(
            owner._downloads_folder or owner.default_download_folder()))
        layout.addWidget(bottom)
        self.owner = owner
        self.reload_rows()

    def reload_rows(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._rows = []
        if not self.owner._downloads:
            label = QLabel('ダウンロード履歴はありません', self.contents)
            label.setObjectName('launchDownloadStatus')
            self.list_layout.addWidget(label)
        else:
            for record in self.owner._downloads[:8]:
                row = _DownloadRow(self.owner, record, self.contents)
                self._rows.append(row)
                self.list_layout.addWidget(row)
        self.list_layout.addStretch()
        self.scroll.setFixedHeight(min(390, max(54, min(8, len(self.owner._downloads)) * 70 + 8)))
        self.adjustSize()

    def update_progress(self):
        for row in self._rows:
            row.update_status()

    def apply_colors(self, colors):
        bg = colors['panel']
        hdr = colors['panel_header']
        text = colors['text']
        border = colors['panel_border']
        muted = colors['muted_text']
        hover = colors['hover']
        self.setStyleSheet(f"""
            QFrame#launchDownloadsPanel {{background:{bg};border:none;
                border-radius:12px;}}
            QLabel {{color:{text};border:0;background:transparent;}}
            QLabel#launchDownloadsTitle {{font-weight:500;font-size:13px;}}
            QLabel#launchDownloadName {{font-size:11px;}}
            QLabel#launchDownloadStatus {{font-size:10px;color:{muted};}}
            QScrollArea#launchDownloadsScroll {{background:transparent;border:0;}}
            QScrollArea#launchDownloadsScroll QWidget {{background:transparent;}}
            QFrame#launchDownloadRow {{border:0;border-radius:7px;background:transparent;}}
            QFrame#launchDownloadRow:hover {{background:{hover};}}
            QToolButton#launchDownloadAction {{border:0;background:transparent;
                border-radius:7px;min-width:29px;min-height:28px;}}
            QToolButton#launchDownloadAction:hover {{background:{hdr};}}
            QToolButton#launchDownloadsClose {{background:transparent;border:0;
                font-size:17px;min-width:25px;min-height:23px;}}
            QToolButton#launchDownloadsClose:hover {{background:{hover};border-radius:8px;}}
            QToolButton#launchDownloadsFolder {{color:{text};background:{hdr};
                border:1px solid {border};border-radius:7px;padding:6px;}}
            QToolButton#launchDownloadsFolder:hover {{background:{hover};}}
        """)


class _ZipExtractionWorker(QThread):
    extracted = Signal(str)
    failed = Signal(str)

    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path

    def run(self):
        try:
            self.extracted.emit(safe_extract_zip(self.path))
        except Exception as error:
            # Failed extraction is presented as a UI error, not a worker crash.
            self.failed.emit(str(error))


class LaunchWebView(QFrame):
    """A disposable View over a persistent Files model, not a second app."""
    surface_selected = Signal(str)
    bookmarks_show_requested = Signal()

    def __init__(self, parent=None, *, settings=None):
        super().__init__(parent)
        self.web_settings = settings or {}
        self._remote_area = None
        self._url_favorite_wheel_delta = 0
        self._url_favorite_warp_generation = 0
        self._downloads = []
        self._downloads_folder = ''
        self._download_file_icon_provider = QFileIconProvider()
        self._download_file_icon_cache = {}
        self._download_popup = None
        self._download_animation = None
        self._download_icon_animation = None
        self._extract_workers = set()
        # A named profile is essential: QWebEngineProfile(self) is off-the-record.
        # Keep it alive for all tabs; no Chrome profile/cookies are imported.
        self.profile = self._create_profile()
        self.profile.downloadRequested.connect(self._download_requested)
        self.setObjectName('launchWebView')
        # Parent CSS has border-top:0; the upper-right curve needs its own
        # foreground stroke rather than a radius with no visible border.
        from expanded_view import _WorkspaceTopRightOutline
        self._top_right_outline = _WorkspaceTopRightOutline(self)
        self._top_right_outline.hide()  # 実験：右上の角丸線を非表示
        self._tabs = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        nav = QHBoxLayout()
        nav.setContentsMargins(4, 0, 4, 0)
        nav.setSpacing(4)
        # Visible in both bookmark states; disabled while the left panel is open.
        # No hidden spacer is left behind when Bookmarks is fully collapsed.
        self.show_bookmarks_button = self._nav_button(
            'bookmark_outline', 'ブックマークを表示',
            self.bookmarks_show_requested.emit, nav)
        self.show_bookmarks_button.setObjectName('launchWebShowBookmarks')
        self.show_bookmarks_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.back = self._nav_button('back_arrow', 'Webページを戻る', self.go_back, nav)
        self.forward = self._nav_button('forward', 'Webページを進む', self.go_forward, nav)
        self.reload = self._nav_button('reload', '再読み込み', self.reload_page, nav)
        # Match the Files breadcrumb: URL editor, heart and favorite-list ▼
        # are one address-bar control. These are separate from authored bookmarks.
        self.url_favorites = BrowserUrlFavorites(
            Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) /
            'FRBLaunch' / 'browser_url_favorites.json')
        self.address_shell = QFrame(self)
        self.address_shell.setObjectName('launchWebAddressShell')
        address_row = QHBoxLayout(self.address_shell)
        address_row.setContentsMargins(5, 0, 4, 0)
        address_row.setSpacing(1)
        self.address = QLineEdit(self.address_shell)
        self.address.setObjectName('launchWebAddress')
        self.address.setPlaceholderText('https://...')
        self.address.returnPressed.connect(self.open_address)
        address_row.addWidget(self.address, 1)
        self.favorite_save = QToolButton(self.address_shell)
        self.favorite_save.setObjectName('launchWebFavoriteSave')
        self.favorite_save.setFixedSize(25, 25)
        self.favorite_save.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.favorite_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.favorite_save.clicked.connect(self.register_url_favorite)
        address_row.addWidget(self.favorite_save)
        self.favorite_dropdown = QToolButton(self.address_shell)
        self.favorite_dropdown.setObjectName('launchWebFavoriteDropdown')
        self.favorite_dropdown.setFixedSize(24, 25)
        self.favorite_dropdown.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.favorite_dropdown.setCursor(Qt.CursorShape.PointingHandCursor)
        self.favorite_dropdown.clicked.connect(self.toggle_url_favorites)
        address_row.addWidget(self.favorite_dropdown)
        nav.addWidget(self.address_shell, 1)
        # Same two-column delete / scroll / reorder popup as Files favorites.
        self.favorite_popup = QFrame(self.window())
        self.favorite_popup.setObjectName('launchWebFavoritesPopup')
        favorite_layout = QVBoxLayout(self.favorite_popup)
        favorite_layout.setContentsMargins(5, 5, 5, 5)
        favorite_layout.setSpacing(0)
        self.favorite_choices = ReorderablePopupTree(self.favorite_popup)
        self.favorite_choices.setObjectName('launchWebFavoritesChoices')
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
        self.favorite_choices.itemClicked.connect(self.url_favorite_clicked)
        self.favorite_choices.orderChanged.connect(self.url_favorites_reordered)
        favorite_layout.addWidget(self.favorite_choices)
        self.favorite_popup.hide()
        self.favorite_popup.installEventFilter(self)
        self.favorite_choices.installEventFilter(self)
        self.favorite_choices.viewport().installEventFilter(self)
        QApplication.instance().installEventFilter(self)
        self.external = self._nav_button('external', 'このページを既定ブラウザで開く',
                                         self.open_external, nav)
        self.downloads_button = self._nav_button('download', 'ダウンロード一覧',
                                                lambda: self.show_downloads_menu(), nav)
        self.downloads_button.setObjectName('launchWebDownloads')
        layout.addLayout(nav)
        self.tabs = _WebTabs(self)
        self.tabs.setTabBar(_WebTabBar(self.tabs))
        self.tabs.tabBar().setDrawBase(False)  # Also after QTabWidget takes ownership.
        self.tabs.tabBar().setObjectName('launchWebTabBar')
        self.tabs.tabBar().area_clicked.connect(lambda: self.surface_selected.emit('web_tabs'))
        self.tabs.setObjectName('launchWebTabs')
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.current_changed)
        new_tab = QToolButton(self.tabs)
        new_tab.setObjectName('launchWebNewTab')
        new_tab.setFixedSize(29, 29)
        new_tab.setAutoRaise(True)
        new_tab.setIconSize(QSize(17, 17))
        new_tab.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        new_tab.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        new_tab.setToolTip('新しいWebタブ')
        new_tab.clicked.connect(lambda: self.add_tab(
            self.web_settings.get('new_tab_url', 'https://www.google.com/'), activate=True))
        self.new_tab_button = new_tab
        bar = self.tabs.tabBar()
        bar.set_new_tab_button(new_tab)
        bar.tabMoved.connect(lambda *_: bar._queue_new_tab_position())
        layout.addWidget(self.tabs, 1)
        # The overlay is a sibling of the WebEngine viewport, not its child.
        # It remains visible while the actual Chromium widget is hidden.
        self._resize_preview = _ResizePreview(self.tabs)
        self._resize_preview_view = None
        self._resize_preview_active = False
        self._resize_preview_finish_timer = QTimer(self)
        self._resize_preview_finish_timer.setSingleShot(True)
        self._resize_preview_finish_timer.timeout.connect(self._finish_live_resize)
        self.hint = QLabel('HOMEでFilesに戻る', self)
        self.hint.setObjectName('launchWebHint')
        layout.addWidget(self.hint)
        self.apply_theme('dark')
        self.update_url_favorite_button()

    def set_bookmarks_visible(self, visible):
        """Keep show control visible but unclickable while Bookmarks is open."""
        self.show_bookmarks_button.setEnabled(not visible)
        self.show_bookmarks_button.setToolTip(
            'ブックマークは表示中' if visible else 'ブックマークを表示')

    def _create_profile(self):
        """Separate local WebEngine profile; never use or modify Chrome data."""
        if not self.web_settings.get('remember_login', True):
            return QWebEngineProfile(QApplication.instance())  # intentionally off-the-record
        root = (Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) /
                'FRBLaunch' / 'web_profile')
        data_dir = root / 'data'
        cache_dir = root / 'cache'
        data_dir.mkdir(parents=True, exist_ok=True)
        cache_dir.mkdir(parents=True, exist_ok=True)
        # Profile must outlive individual QWebEnginePage instances.
        profile = QWebEngineProfile('FRBLaunchWeb', QApplication.instance())
        profile.setPersistentStoragePath(str(data_dir))
        profile.setCachePath(str(cache_dir))
        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        return profile

    def download_file_icon(self, path):
        """Use Windows' registered icon for the filename extension.

        Match the Files column's QFileIconProvider approach while querying a
        synthetic filename, so an untrusted download is never inspected just
        to choose its icon.  Cache by extension for stable, cheap repaints.
        """
        suffix = PureWindowsPath(str(path)).suffix.casefold()
        if not suffix:
            return self._download_file_icon_provider.icon(QFileIconProvider.IconType.File)
        icon = self._download_file_icon_cache.get(suffix)
        if icon is None:
            icon = self._download_file_icon_provider.icon(
                QFileInfo('FRBLaunchTypeSample' + suffix))
            if icon.isNull():
                icon = self._download_file_icon_provider.icon(
                    QFileIconProvider.IconType.File)
            self._download_file_icon_cache[suffix] = icon
        return icon

    def default_download_folder(self):
        configured = self.web_settings.get('download_directory', '').strip()
        if configured:
            return str(Path(configured).expanduser())
        system_folder = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DownloadLocation)
        return system_folder or str(Path.home() / 'Downloads')

    def _download_requested(self, request):
        """Chrome-like automatic download into the configured folder (no dialog)."""
        suggested = safe_download_name(request.suggestedFileName() or
                                       request.downloadFileName() or 'download')
        directory = Path(self.default_download_folder()).expanduser()
        try:
            directory.mkdir(parents=True, exist_ok=True)
            in_use = (record['path'] for record in self._downloads)
            target = unique_path(directory, suggested, reserved=in_use)
            request.setDownloadDirectory(str(target.parent))
            request.setDownloadFileName(target.name)
        except (OSError, ValueError) as error:
            request.cancel()
            QMessageBox.warning(self, 'ダウンロードできません',
                                f'保存先を確認してください。\n{error}')
            return
        self._downloads_folder = str(target.parent)
        record = {'request': request, 'path': str(target), 'notified': False}
        self._downloads.insert(0, record)
        self._downloads = self._downloads[:20]
        request.stateChanged.connect(lambda _state, r=record: self._on_download_state(r))
        request.receivedBytesChanged.connect(self._update_download_button)
        request.totalBytesChanged.connect(self._update_download_button)
        request.accept()
        self._update_download_button()
        if self._download_popup is not None and self._download_popup.isVisible():
            self._download_popup.reload_rows()

    def _on_download_state(self, record):
        self._update_download_button()
        state = record['request'].state()
        if (state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted
                and not record['notified']):
            record['notified'] = True
            if self.isVisible():
                self._animate_download_complete()
                # A slight pause lets the animation precede the panel, like Chrome.
                QTimer.singleShot(230, self._show_completed_downloads)

    def _show_completed_downloads(self):
        if self.isVisible():
            self.show_downloads_menu(animated=True)

    def _update_download_button(self, *_args):
        in_progress = sum(
            r['request'].state() == QWebEngineDownloadRequest.DownloadState.DownloadInProgress
            for r in self._downloads)
        self.downloads_button.setToolTip(
            f'ダウンロード一覧（実行中 {in_progress}件）')
        active = bool(in_progress)
        if self.downloads_button.property('activeDownloads') != active:
            self.downloads_button.setProperty('activeDownloads', active)
            self.downloads_button.style().unpolish(self.downloads_button)
            self.downloads_button.style().polish(self.downloads_button)
        if self._download_popup is not None and self._download_popup.isVisible():
            self._download_popup.update_progress()

    def _animate_download_complete(self):
        # Animate the icon's opacity without moving it or stealing keyboard focus.
        effect = self.downloads_button.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(self.downloads_button)
            self.downloads_button.setGraphicsEffect(effect)
        if self._download_animation is not None:
            self._download_animation.stop()
        animation = QPropertyAnimation(effect, b'opacity', self.downloads_button)
        animation.setDuration(640)
        animation.setStartValue(0.25)
        animation.setKeyValueAt(0.4, 1.0)
        animation.setKeyValueAt(0.68, 0.55)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._download_animation = animation
        animation.start()
        if self._download_icon_animation is not None:
            self._download_icon_animation.stop()
        icon_animation = QPropertyAnimation(self.downloads_button, b'iconSize',
                                            self.downloads_button)
        icon_animation.setDuration(560)
        icon_animation.setStartValue(QSize(16, 16))
        icon_animation.setKeyValueAt(0.45, QSize(23, 23))
        icon_animation.setEndValue(QSize(19, 19))
        icon_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._download_icon_animation = icon_animation
        icon_animation.start()

    def show_downloads_menu(self, *, animated=False):
        """Show a hover-action download panel just below the download button."""
        if not self.isVisible():
            return
        if self._download_popup is None:
            self._download_popup = _DownloadPanel(self)
        panel = self._download_popup
        panel.reload_rows()
        from launch_appearance import theme_palette
        panel.apply_colors(theme_palette(getattr(self, '_current_theme', 'light')))
        # Clamp to the actual monitor, including multi-monitor and high-DPI.
        anchor = self.downloads_button.mapToGlobal(
            self.downloads_button.rect().bottomRight())
        screen = QApplication.screenAt(anchor) or QApplication.primaryScreen()
        available = screen.availableGeometry() if screen else self.screen().availableGeometry()
        x = max(available.left() + 4,
                min(anchor.x() - panel.width(), available.right() - panel.width() - 4))
        y = anchor.y() + 5
        if y + panel.sizeHint().height() > available.bottom() - 4:
            y = max(available.top() + 4, available.bottom() - panel.sizeHint().height() - 4)
        panel.move(x, y)
        panel.show()
        panel.raise_()
        if animated:
            effect = QGraphicsOpacityEffect(panel)
            panel.setGraphicsEffect(effect)
            if getattr(self, '_popup_animation', None) is not None:
                self._popup_animation.stop()
            animation = QPropertyAnimation(effect, b'opacity', panel)
            animation.setDuration(220)
            animation.setStartValue(0.25)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._popup_animation = animation
            animation.start()
        elif isinstance(panel.graphicsEffect(), QGraphicsOpacityEffect):
            panel.graphicsEffect().setOpacity(1.0)

    def open_download_folder(self, path):
        """Open a folder in the system file explorer (never execute downloads)."""
        from PySide6.QtGui import QDesktopServices
        folder = Path(path)
        if folder.is_file():
            folder = folder.parent
        if folder.is_dir():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))
        else:
            QMessageBox.warning(self, 'フォルダーがありません', str(folder))

    def extract_download_zip(self, path):
        """Unzip only on explicit click, in a worker so WebView stays responsive."""
        path = Path(path)
        if path.suffix.lower() != '.zip' or not path.is_file():
            QMessageBox.warning(self, 'ZIPがありません', str(path))
            return
        worker = _ZipExtractionWorker(str(path), self)
        self._extract_workers.add(worker)
        worker.extracted.connect(self.open_download_folder)
        worker.failed.connect(self._on_zip_failed)
        worker.finished.connect(self._finish_extract_worker)
        worker.start()

    def _on_zip_failed(self, text):
        QMessageBox.warning(self, 'ZIPを展開できません', text)

    def _finish_extract_worker(self):
        worker = self.sender()
        if worker in self._extract_workers:
            self._extract_workers.discard(worker)
            worker.deleteLater()

    def _nav_button(self, icon_name, tip, callback, row):
        button = QToolButton(self)
        button.setProperty('webIconName', icon_name)
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        button.setIconSize(QSize(19, 19))
        button.setToolTip(tip)
        button.setFixedSize(30, 29)
        button.clicked.connect(callback)
        row.addWidget(button)
        return button

    def _refresh_icons(self, theme):
        """Share the Launch toolbar's vector language and theme colors."""
        family = theme_family(theme)
        for button in (self.show_bookmarks_button, self.back, self.forward, self.reload, self.external,
                       self.downloads_button):
            button.setIcon(browser_navigation_icon(button.property('webIconName'), family))
        self.new_tab_button.setIcon(browser_navigation_icon('plus', family))
        bar = self.tabs.tabBar()
        for index in range(bar.count()):
            close_button = bar.tabButton(index, QTabBar.ButtonPosition.RightSide)
            if isinstance(close_button, _WebCloseButton):
                close_button.setIcon(browser_navigation_icon('close', family))
            view = self.tabs.widget(index)
            if isinstance(view, QWebEngineView):
                self.update_tab_icon(view, view.icon(), theme=theme)

    def _apply_view_backgrounds(self, theme):
        """Avoid black resize gaps in light mode; keep dark mode unchanged."""
        colors = theme_palette(theme)
        light = theme_family(theme) == 'light'
        panel = colors['panel'] if light else 'transparent'
        self.setAutoFillBackground(light)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(colors['panel']))
        self.setPalette(palette)
        self.tabs.setAutoFillBackground(light)
        tab_palette = self.tabs.palette()
        tab_palette.setColor(self.tabs.backgroundRole(), QColor(colors['panel']))
        self.tabs.setPalette(tab_palette)
        self.tabs.setStyleSheet((self.tabs.styleSheet() or '') + '')
        for index in range(self.tabs.count()):
            view = self.tabs.widget(index)
            if isinstance(view, QWebEngineView):
                try:
                    if light:
                        view.page().setBackgroundColor(QColor(colors['panel']))
                    else:
                        view.page().setBackgroundColor(QColor(0, 0, 0, 0))
                except Exception:
                    pass
                view.setStyleSheet(f'background:{panel}; border:0;')

    def update_tab_icon(self, view, icon, *, theme=None):
        """Show the site's favicon; use a quiet globe until one arrives."""
        index = self.tabs.indexOf(view)
        if index < 0:
            return
        if icon is not None and not icon.isNull():
            self.tabs.setTabIcon(index, icon)
        else:
            family = theme_family(theme or getattr(self, '_current_theme', 'light'))
            self.tabs.setTabIcon(index, browser_navigation_icon('globe', family))

    def current_view(self):
        widget = self.tabs.currentWidget()
        return widget if isinstance(widget, QWebEngineView) else None

    def _position_resize_preview(self):
        """Follow the current Web viewport even during rapid width changes."""
        if not getattr(self, '_resize_preview_active', False):
            return
        view = self._resize_preview_view
        if view is None:
            return
        top_left = view.mapTo(self.tabs, QPoint(0, 0))
        # QStackedWidget may delay resizing a temporarily hidden WebEngine
        # child. Extend the opaque preview through the entire new tab pane.
        width = max(view.width(), self.tabs.width() - top_left.x() - 4)
        height = max(view.height(), self.tabs.height() - top_left.y() - 4)
        self._resize_preview.setGeometry(top_left.x(), top_left.y(), width, height)
        self._resize_preview.raise_()

    def begin_live_resize(self):
        """Before border dragging starts, freeze only the light-mode Web body."""
        if theme_family(getattr(self, '_current_theme', 'dark')) != 'light':
            return
        if self._resize_preview_active:
            self._resize_preview_finish_timer.stop()
            return
        view = self.current_view()
        if view is None or not view.isVisible():
            return
        # Capture BEFORE the first resize; taking a screenshot afterwards
        # captures the very black strip this workaround is meant to prevent.
        snapshot = view.grab()
        self._resize_preview.set_preview(snapshot, theme_palette(self._current_theme)['panel'])
        self._resize_preview_view = view
        self._resize_preview_active = True
        self._position_resize_preview()
        view.hide()
        self._resize_preview.show()
        self._resize_preview.raise_()

    def end_live_resize(self):
        """Let Chromium finish allocating its new surface, then restore."""
        if self._resize_preview_active:
            self._resize_preview_finish_timer.start(170)

    def _finish_live_resize(self):
        if not self._resize_preview_active:
            return
        view = self._resize_preview_view
        self._resize_preview_active = False
        self._resize_preview_view = None
        if view is not None and view is self.current_view():
            view.show()
            view.update()
            # Retain the existing post-resize recovery as a fallback.
            view._resize_surface_timer.start(160)
        self._resize_preview.hide()
        self._resize_preview.clear_preview()

    def add_tab(self, url=None, *, activate=True):
        view = _LaunchWebPage(self)
        view.setPage(QWebEnginePage(self.profile, view))
        # Apply the user-configured initial zoom to every new tab, including
        # links opened via 'new tab' and window.open. Do this before loading.
        view.setZoomFactor(self.web_settings.get('default_zoom_percent', 90) / 100.0)
        view.setObjectName('launchWebPage')
        current_theme = getattr(self, '_current_theme', 'light')
        try:
            if theme_family(current_theme) == 'light':
                view.page().setBackgroundColor(QColor(theme_palette(current_theme)['panel']))
            else:
                view.page().setBackgroundColor(QColor(0, 0, 0, 0))
        except Exception:
            pass
        view.setStyleSheet(f"background:{theme_palette(current_theme)['panel'] if theme_family(current_theme) == 'light' else 'transparent'}; border:0;")
        index = self.tabs.addTab(view, '新規タブ')
        # Replace Qt's platform-dependent square close glyph with a small X.
        close_button = _WebCloseButton(self.tabs.tabBar())
        close_button.clicked.connect(lambda _checked=False, v=view:
                                     self.close_tab(self.tabs.indexOf(v)))
        self.tabs.tabBar().setTabButton(index, QTabBar.ButtonPosition.RightSide,
                                        close_button)
        close_button.setIcon(browser_navigation_icon(
            'close', theme_family(getattr(self, '_current_theme', 'light'))))
        self.update_tab_icon(view, view.icon())
        view.iconChanged.connect(lambda icon, v=view: self.update_tab_icon(v, icon))
        view.titleChanged.connect(lambda name, v=view: self.update_title(v, name))
        view.urlChanged.connect(lambda value, v=view: self.url_changed(v, value))
        view.loadFinished.connect(lambda ok, v=view: self.load_finished(v, ok))
        if activate:
            self.tabs.setCurrentIndex(index)
        self.tabs.tabBar()._queue_new_tab_position()
        if url:
            view.setUrl(QUrl(url))
        return view

    def select_tab(self, step):
        """Remote wheel changes tabs, not focus or DOM scroll."""
        if self.tabs.count():
            index = self.tabs.currentIndex()
            self.tabs.setCurrentIndex(max(0, min(self.tabs.count() - 1,
                                                 index + step)))

    def scroll_page(self, step):
        """Scroll the actual document while the pointer stays on Remote."""
        view = self.current_view()
        if view is not None:
            view.page().runJavaScript(f'window.scrollBy(0, {int(step) * 180})')

    def focus_page(self):
        view = self.current_view()
        if view is not None:
            view.setFocus(Qt.FocusReason.OtherFocusReason)

    def set_remote_area(self, area):
        """Highlight whichever Web surface the non-activating Remote targets."""
        if self._remote_area == area:
            return
        self._remote_area = area
        self.setProperty('remoteWebArea', area or '')
        self.style().unpolish(self)
        self.style().polish(self)
        bar = self.tabs.tabBar()
        bar.setProperty('remoteWebActive', area == 'web_tabs')
        bar.style().unpolish(bar)
        bar.style().polish(bar)
        self.update()
        bar.update()

    def tab_context_menu(self):
        """A menu for the *current Web tab* (no hidden DOM position assumed)."""
        menu = QMenu(self)
        menu.addAction('新しいWebタブ', lambda: self.add_tab(
            self.web_settings.get('new_tab_url', 'https://www.google.com/')))
        has_tab = self.current_view() is not None
        close_action = menu.addAction('現在のタブを閉じる',
                                      lambda: self.close_tab(self.tabs.currentIndex()))
        close_action.setEnabled(has_tab)
        close_others = menu.addAction('他のタブを閉じる', self.close_other_tabs)
        close_others.setEnabled(self.tabs.count() > 1)
        menu.addSeparator()
        refresh = menu.addAction('現在のタブを再読み込み', self.reload_page)
        refresh.setEnabled(has_tab)
        return menu

    def close_other_tabs(self):
        keep = self.tabs.currentWidget()
        for index in range(self.tabs.count() - 1, -1, -1):
            if self.tabs.widget(index) is not keep:
                self.close_tab(index)

    def page_context_menu(self):
        """Page-level actions for Remote; link-specific native right-click stays native."""
        menu = QMenu(self)
        view = self.current_view()
        if view is None:
            menu.addAction('新しいWebタブ', lambda: self.add_tab(
                self.web_settings.get('new_tab_url', 'https://www.google.com/')))
            return menu
        back = menu.addAction('戻る', self.go_back)
        back.setEnabled(view.history().canGoBack())
        forward = menu.addAction('進む', self.go_forward)
        forward.setEnabled(view.history().canGoForward())
        menu.addAction('再読み込み', self.reload_page)
        menu.addSeparator()
        menu.addAction('現在のページを新しいタブで開く',
                       lambda: self.add_tab(view.url().toString()))
        menu.addAction('ページのURLをコピー',
                       lambda: QApplication.clipboard().setText(view.url().toString()))
        if view.selectedText():
            menu.addAction('選択テキストをコピー',
                           lambda: QApplication.clipboard().setText(view.selectedText()))
        menu.addAction('既定ブラウザで開く', self.open_external)
        return menu

    def show_url(self, url, *, new_tab=False):
        # Bookmarks navigate the current tab; Ctrl/right-click links open tabs.
        view = self.current_view()
        if view is None or new_tab:
            view = self.add_tab(activate=True)
        view.setUrl(QUrl(url))
        if self.tabs.currentWidget() is view:
            self.address.setText(url)
            self.update_url_favorite_button()

    def update_title(self, view, text):
        index = self.tabs.indexOf(view)
        if index >= 0:
            title = (text or view.url().host() or '読み込み中')
            self.tabs.setTabText(index, title[:22] + ('…' if len(title) > 22 else ''))
            self.tabs.setTabToolTip(index, title)
            self.tabs.tabBar()._queue_new_tab_position()

    def url_changed(self, view, url):
        if view is self.current_view():
            self.address.setText(url.toString())
            self.update_url_favorite_button()
            self.update_navigation()

    def load_finished(self, view, ok):
        if view is self.current_view():
            self.update_navigation()
            self.hint.setText('HOMEでFilesに戻る' if ok else
                              'ページを表示できません（サイト側の制限や通信状態を確認）')

    def current_changed(self, _index):
        view = self.current_view()
        self.address.setText(view.url().toString() if view else '')
        self.update_url_favorite_button()
        self.update_navigation()

    def update_navigation(self):
        view = self.current_view()
        self.back.setEnabled(bool(view and view.history().canGoBack()))
        self.forward.setEnabled(bool(view and view.history().canGoForward()))
        self.reload.setEnabled(view is not None)
        self.external.setEnabled(bool(view and view.url().isValid()))

    def current_url_for_favorite(self):
        """Use the current Web page, not an unsubmitted edit in the address bar."""
        view = self.current_view() if hasattr(self, 'tabs') else None
        return normalize_favorite_url(view.url().toString()) if view else ''

    def update_url_favorite_button(self):
        url = self.current_url_for_favorite()
        saved = bool(url and url in self.url_favorites.urls)
        self.favorite_save.setText('🩶' if saved else '💛')
        self.favorite_save.setToolTip('お気に入り登録済み' if saved else '今のURLをお気に入りに登録')
        self.favorite_save.setEnabled(bool(url))
        self.favorite_dropdown.setEnabled(bool(self.url_favorites.urls))
        self.favorite_dropdown.setToolTip(
            f'URLのお気に入り一覧（{len(self.url_favorites.urls)}件）')

    def register_url_favorite(self):
        url = self.current_url_for_favorite()
        if not url:
            return
        try:
            self.url_favorites.add(url)
        except OSError:
            QMessageBox.warning(self, 'お気に入り', 'URLのお気に入りを保存できませんでした')
            return
        self.update_url_favorite_button()
        if self.favorite_popup.isVisible():
            self.populate_url_favorites(selected=url)

    def populate_url_favorites(self, selected=None):
        tree = self.favorite_choices
        tree.blockSignals(True)
        try:
            tree.clear()
            for url in self.url_favorites.urls:
                row = QTreeWidgetItem([url, '×'])
                row.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
                row.setToolTip(0, 'クリックでBrowser内のURLを開く／ドラッグで並び替え')
                row.setToolTip(1, 'お気に入りを削除（Webページは削除されません）')
                tree.addTopLevelItem(row)
                if url == selected:
                    tree.setCurrentItem(row)
            if tree.topLevelItemCount() and tree.currentItem() is None:
                tree.setCurrentItem(tree.topLevelItem(0))
        finally:
            tree.blockSignals(False)
        if self.favorite_popup.isVisible():
            self.position_url_favorites()

    def position_url_favorites(self):
        from popup_sizing import popup_tree_height
        host = self.favorite_popup.parentWidget()
        point = self.address_shell.mapTo(host, QPoint(0, self.address_shell.height() + 4))
        width = min(self.address_shell.width(), max(1, host.width() - 12))
        x = max(6, min(point.x(), host.width() - width - 6))
        available = max(60, host.height() - point.y() - 12)
        rows = (self.favorite_choices.topLevelItem(i)
                for i in range(self.favorite_choices.topLevelItemCount()))
        height = popup_tree_height(self.favorite_choices, rows,
                                   minimum_row_height=34, chrome_height=16,
                                   available_height=available)
        self.favorite_popup.setGeometry(x, point.y(), width, height)

    def toggle_url_favorites(self):
        if self.favorite_popup.isVisible():
            self.hide_url_favorites()
            return
        if not self.url_favorites.urls:
            return
        self.populate_url_favorites(selected=self.current_url_for_favorite())
        self.position_url_favorites()
        self.favorite_popup.show()
        self.favorite_popup.raise_()
        self.favorite_choices.setFocus(Qt.FocusReason.MouseFocusReason)

    def hide_url_favorites(self):
        self.favorite_popup.hide()
        self._url_favorite_wheel_delta = 0
        self._url_favorite_warp_generation += 1

    def url_favorite_clicked(self, item, column):
        url = item.text(0)
        if column == 1:
            try:
                self.url_favorites.remove(url)
            except OSError:
                QMessageBox.warning(self, 'お気に入り', 'URLのお気に入りを削除できませんでした')
                return
            self.populate_url_favorites()
            self.update_url_favorite_button()
            if not self.url_favorites.urls:
                self.hide_url_favorites()
            return
        self.hide_url_favorites()
        self.show_url(url)

    def url_favorites_reordered(self, urls):
        try:
            if not self.url_favorites.reorder(urls):
                self.populate_url_favorites()
        except OSError:
            QMessageBox.warning(self, 'お気に入り', 'URLお気に入りの並び替えを保存できませんでした')
            self.populate_url_favorites()

    def eventFilter(self, obj, event):
        if not hasattr(self, 'favorite_popup'):
            return super().eventFilter(obj, event)
        if (self.favorite_popup.isVisible() and
                event.type() == QEvent.Type.MouseButtonPress and
                isinstance(obj, QWidget) and obj.window() is self.window() and
                obj is not self.favorite_dropdown and
                not self.favorite_dropdown.isAncestorOf(obj) and
                obj is not self.favorite_popup and
                not self.favorite_popup.isAncestorOf(obj)):
            self.hide_url_favorites()
        if (self.favorite_popup.isVisible() and
                obj in (self.favorite_choices, self.favorite_choices.viewport()) and
                event.type() == QEvent.Type.Wheel and
                event.modifiers() == Qt.KeyboardModifier.NoModifier):
            tree = self.favorite_choices
            pending, steps = wheel_steps(self._url_favorite_wheel_delta,
                                         event.angleDelta().y(), event.pixelDelta().y())
            self._url_favorite_wheel_delta = pending
            count = tree.topLevelItemCount()
            if steps and count:
                index = history_target_index(tree.indexOfTopLevelItem(tree.currentItem()),
                                             count, steps)
                item = tree.topLevelItem(index)
                tree.setCurrentItem(item)
                tree.scrollToItem(item, QAbstractItemView.ScrollHint.EnsureVisible)
                if getattr(self.window(), 'pointer_warp_enabled', False):
                    origin = QCursor.pos()
                    self._url_favorite_warp_generation += 1
                    generation = self._url_favorite_warp_generation
                    QTimer.singleShot(0, lambda: (
                        warp_to_history_row(tree, item, origin, QCursor)
                        if generation == self._url_favorite_warp_generation else None))
            event.accept()
            return True
        if (self.favorite_popup.isVisible() and
                obj in (self.favorite_choices, self.favorite_choices.viewport()) and
                event.type() == QEvent.Type.KeyPress):
            if event.key() == Qt.Key.Key_Escape:
                self.hide_url_favorites()
                return True
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                row = self.favorite_choices.currentItem()
                if row is not None:
                    self.url_favorite_clicked(row, 0)
                return True
        return super().eventFilter(obj, event)

    def open_address(self):
        from webview_routes import bookmark_web_url
        value = self.address.text().strip()
        # Do not navigate arbitrary WebEngine schemes from the address bar.
        if bookmark_web_url({'item_kind': 'command', 'launch_actions':
                             [{'launch_action_type': 'Open', 'launch_target': value}]}):
            self.show_url(value)

    def go_back(self):
        if self.current_view():
            self.current_view().back()

    def go_forward(self):
        if self.current_view():
            self.current_view().forward()

    def reload_page(self):
        if self.current_view():
            self.current_view().reload()

    def open_external(self):
        from PySide6.QtGui import QDesktopServices
        view = self.current_view()
        if view and view.url().scheme() in ('http', 'https'):
            QDesktopServices.openUrl(view.url())

    def close_tab(self, index):
        view = self.tabs.widget(index)
        if view is None:
            return
        self.tabs.removeTab(index)
        view.deleteLater()
        if self.tabs.count() == 0:
            self.hint.setText('ブックマークのURLを選ぶと表示されます。HOMEでFilesに戻る')
        self.address.setText(self.current_view().url().toString() if self.current_view() else '')
        self.update_url_favorite_button()
        self.update_navigation()
        self.tabs.tabBar()._queue_new_tab_position()

    def apply_theme(self, theme):
        from launch_appearance import theme_palette
        if (getattr(self, '_resize_preview_active', False)
                and theme_family(theme) != 'light'):
            self._resize_preview_finish_timer.stop()
            self._finish_live_resize()
        colors = theme_palette(theme)
        self._current_theme = theme
        bg = colors['panel']
        text = colors['text']
        border = colors['panel_border']
        hdr = colors['panel_header']
        self._top_right_outline.set_outline_color(border)
        self._refresh_icons(theme)
        self.favorite_dropdown.setIcon(combo_chevron_icon(theme))
        self.favorite_popup.setStyleSheet(history_popup_qss(theme, frame_name='launchWebFavoritesPopup',
                                                    tree_name='launchWebFavoritesChoices'))
        if self._download_popup is not None:
            self._download_popup.apply_colors(colors)
        hover = colors['hover']
        muted = colors['muted_text']
        self.setStyleSheet(f'''
            /* Files-like Web chrome: the large surrounding area is mint-green.
               The rendered website is still owned by QWebEngineView itself. */
            QFrame#launchWebView {{background:{hdr};border:1px solid {border};border-top:0;
                 border-top-left-radius:0;border-top-right-radius:11px;}}
            QTabWidget#launchWebTabs {{border:0;background:{bg};}}
            QTabWidget#launchWebTabs::pane {{border:0;margin:0;padding:0;background:{bg};}}
            QTabBar#launchWebTabBar {{background:transparent;border:none;}}
            QTabBar#launchWebTabBar::scroller {{border:none;background:transparent;}}
            QTabWidget#launchWebTabs::tab-bar {{border:none;}}
            QTabBar#launchWebTabBar::tab {{background:{hdr};color:{text};
                 font-weight:400;min-height:20px;padding:5px 10px;
                 margin-right:3px;border:1px solid {border};
                 border-top:0;border-bottom:0;border-top-left-radius:9px;
                 border-top-right-radius:9px;}}
            QTabBar#launchWebTabBar::tab:selected {{background:{bg};font-weight:400;}}
            QTabBar#launchWebTabBar::tab:hover:!selected {{background:{hover};}}
            QFrame#launchWebAddressShell {{background:{colors['search_bg']};
                 border:1px solid {colors['search_border']};border-radius:12px;}}
            QLineEdit#launchWebAddress {{background:transparent;color:{muted};
                 border:0;padding:2px 5px;font-size:12px;}}
            QLineEdit#launchWebAddress:focus {{border:0;}}
            QToolButton#launchWebFavoriteSave,
            QToolButton#launchWebFavoriteDropdown {{background:transparent;border:0;
                 padding:0;margin:0;}}
            QToolButton#launchWebFavoriteSave:hover,
            QToolButton#launchWebFavoriteDropdown:hover {{background:{hover};border-radius:7px;}}
            QLabel#launchWebHint {{color:{colors['text']};font-size:10px;}}
            QToolButton {{background:{bg};color:{text};border:1px solid {border};border-radius:7px;}}
            QToolButton:hover {{background:{hover};}}
            QToolButton#launchWebDownloads[activeDownloads="true"]
                {{border:1px solid #58ad82;background:{hover};}}
            QToolButton#launchWebNewTab {{border:0;background:transparent;
                 border-radius:14px;margin:0;padding:0;}}
            QToolButton#launchWebNewTab:hover {{background:{hover};border-radius:14px;}}
            QToolButton#launchWebNewTab:pressed {{background:{border};border-radius:14px;}}
            QToolButton#launchWebCloseButton {{background:transparent;border:0;
                 border-radius:10px;padding:0;margin:0;}}
            QToolButton#launchWebCloseButton:hover {{background:{hover};}}
        ''')
        self._apply_view_backgrounds(theme)
