"""An experimental mouse-side remote for FRB Launch.

Mouse actions emit semantic commands.  No SendKeys, synthetic key presses or
cross-process keyboard injection are involved.
"""

from PySide6.QtCore import Qt, QEvent, Signal, QPoint, QRect, QRectF, QSize, QTimer
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QPixmap, QIcon
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                                QLabel, QFrame, QApplication, QMenu)
from remote_navigation import popup_at_hotspot
from passive_header_drag import PassiveHeaderDrag
from launch_appearance import theme_palette, theme_family
from browser_nav_icons import browser_navigation_icon
from remote_files_explorer import RemoteFilesExplorer


def remote_favorite_icon(heart):
    """Render the breadcrumb's existing color heart as a proper QAction icon.

    The main breadcrumb's unregistered icon is 💛 (a warm yellow-orange heart).
    The Remote menu intentionally keeps this golden heart even when the current
    folder is already registered; the action's enabled state is unchanged.
    Render the same glyph into a transparent HiDPI QIcon rather than inserting
    an emoji into the action label.
    """
    pixmap = QPixmap(40, 40)
    pixmap.setDevicePixelRatio(2)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setFont(QFont('Segoe UI Emoji', 13))
    painter.drawText(QRect(0, 0, 20, 20), Qt.AlignmentFlag.AlignCenter,
                     '💛')
    painter.end()
    return QIcon(pixmap)


class WheelPad(QFrame):
    command = Signal(str)

    def __init__(self, parent=None, *, compact=False):
        super().__init__(parent)
        self.setObjectName('remoteWheelPad')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip('ホイールで選択／左クリック・ダブルクリック／右クリックで現在項目のメニュー')
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._angle_remainder = 0
        self._pixel_remainder = 0
        self._pressed = False
        self._ignore_double_release = False
        self._compact = bool(compact)
        if self._compact:
            # Compact, but not too tiny: keep neighbor travel short while
            # preserving enough hit area and visual balance.
            self.setFixedSize(68, 46)
        else:
            self.setMinimumHeight(70)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1 if self._compact else 4,
                                  1 if self._compact else 8,
                                  1 if self._compact else 4,
                                  1 if self._compact else 8)
        layout.setSpacing(2 if self._compact else 4)
        label = QLabel('ぐりぐり' if self._compact else '◉ ぐりぐり', self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setObjectName('remotePadLabel')
        label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(label)
        if self._compact:
            # Second line: use the requested circle glyph one font step
            # larger than the text, without altering wheel/click handling.
            glyph = QLabel('🔘', self)
            glyph.setObjectName('remotePadGlyph')
            glyph.setAlignment(Qt.AlignmentFlag.AlignCenter)
            glyph.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            layout.setSpacing(0)
            layout.addWidget(glyph)
        if not self._compact:
            caption = QLabel('ホイールで選択  /  押して決定', self)
            caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
            caption.setObjectName('remotePadCaption')
            caption.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            layout.addWidget(caption)

    def wheelEvent(self, event):
        angle = event.angleDelta().y()
        pixel = event.pixelDelta().y()
        if angle:
            self._angle_remainder += angle
            steps = int(self._angle_remainder / 120)
            self._angle_remainder -= steps * 120
        else:
            self._pixel_remainder += pixel
            steps = int(self._pixel_remainder / 36)
            self._pixel_remainder -= steps * 36
        # Limit trackpad bursts to protect expensive directory refreshes.
        for _ in range(min(abs(steps), 5)):
            self.command.emit('UP' if steps > 0 else 'DOWN')
        event.accept()

    def mousePressEvent(self, event):
        self._pressed = event.button() == Qt.MouseButton.LeftButton
        if event.button() == Qt.MouseButton.RightButton:
            event.accept()
            return
        if self._pressed:
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        # Qt recognizes the native platform double-click interval/distance.
        # The first click already performed the normal single-click action,
        # exactly as a real mouse does. Suppress only the second release.
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            self._ignore_double_release = True
            if self.rect().contains(event.position().toPoint()):
                self.command.emit('DOUBLE_CLICK')
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            if self.rect().contains(event.position().toPoint()):
                self.command.emit('CONTEXT_MENU')
            event.accept()
            return
        if self._ignore_double_release and event.button() == Qt.MouseButton.LeftButton:
            self._ignore_double_release = False
            self._pressed = False
            event.accept()
            return
        if self._pressed and event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            if self.rect().contains(event.position().toPoint()):
                self.command.emit('CLICK')
            event.accept()
        else:
            self._pressed = False
            super().mouseReleaseEvent(event)


class RemoteWheelButton(QPushButton):
    """A normal command button that also shares the central pad's wheel.

    No eventFilter, synthetic keys or button-click side effects: only wheel
    rotation is forwarded to WheelPad, with its existing fractional-step
    accumulator.  Native mouse clicks still activate the button's own action.
    """

    def wheelEvent(self, event):
        pad = getattr(self.parentWidget(), 'pad', None)
        if pad is not None:
            pad.wheelEvent(event)
        else:
            super().wheelEvent(event)


class RemoteSearchHistoryButton(RemoteWheelButton):
    """Distinguish a real double-click from a single history confirmation.

    QPushButton.clicked fires on the first release of a double-click. The
    owning Remote therefore defers only this button's single-click command
    until the platform double-click interval has elapsed.
    """
    double_clicked = Signal()

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._double_pending = False

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._double_pending = True
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event):
        if self._double_pending and event.button() == Qt.MouseButton.LeftButton:
            self._double_pending = False
            if self.rect().contains(event.position().toPoint()):
                # Dispatch after the second mouse release, not on press.
                self.double_clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)


class UpDoubleClickBand(QFrame):
    """Blank Remote strip: left double-click = Back, right-click = folder menu."""
    command = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('remoteUpDoubleClickBand')
        self.setFixedHeight(23)
        self.setToolTip('ダブルクリック：上位フォルダーへ / 右クリック：カレントフォルダー操作')
        self._files_mode = True
        self._caption = QLabel('（カレントフォルダー操作）', self)
        self._caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._caption.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._caption)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def set_files_mode(self, enabled):
        self._files_mode = bool(enabled)
        self._caption.setVisible(self._files_mode)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._files_mode:
            self.command.emit('FOLDER_UP')
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        # Use Qt's native context-menu event (on Windows it arrives on mouse
        # release). Do not synthesize a click or select a row in Launch.
        if self._files_mode:
            self.command.emit('REMOTE_CURRENT_FOLDER_MENU')
        event.accept()


class LaunchRemote(QWidget):
    command = Signal(str)
    header_pressed = Signal()
    more_menu_opening = Signal()
    page_clicked = Signal(str)
    files_exp_folder_selected = Signal(str)
    files_exp_folder_context = Signal(str, QPoint)
    files_exp_folder_renamed = Signal(str, str)

    def __init__(self, launcher):
        flags = (Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint |
                 Qt.WindowType.WindowDoesNotAcceptFocus)
        super().__init__(launcher, flags)
        self.setObjectName('launchRemoteWindow')
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        # Transparent window corners; the antialiased panel is drawn in paintEvent.
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Compact layout tuned from hands-on feedback: keep the pointer
        # travel short, but preserve enough button height and readable text.
        self.setFixedWidth(184)
        self.apply_theme(launcher.color_theme)
        root = QVBoxLayout(self)
        root.setContentsMargins(5, 5, 5, 5)
        root.setSpacing(3)

        # Distinct title strip; no extra mouse travel or focus change.
        title_frame = QFrame(self)
        title_frame.setObjectName('remoteTitleBar')
        head = QHBoxLayout(title_frame)
        head.setContentsMargins(2, 2, 2, 2)
        head.setSpacing(2)
        self.home_button = self._button('', 'HOME：Files第1列の先頭行へ',
                                        'HOME', width=28, height=24, role='icon')
        self.home_button.setObjectName('remoteHomeButton')
        # The very same house outline used by Launch's navigation HOME.
        # Only its rendered size differs for the compact remote title bar.
        self.home_button.setIconSize(QSize(18, 18))
        self.home_button.setIcon(browser_navigation_icon('home', theme_family(launcher.color_theme)))
        head.addWidget(self.home_button)
        title = QLabel('FRB Remote v0.12', title_frame)
        title.setObjectName('remoteTitle')
        head.addWidget(title, 1)
        # The more-menu sits beside ×; the close control remains at the far
        # right.  Keep it non-focusing like the other Remote controls.
        self.more_button = self._button('…', 'Launchの機能を開く',
                                        'MORE_MENU', width=22, height=22, role='icon')
        self.more_button.setObjectName('remoteMoreButton')
        head.addWidget(self.more_button)
        head.addWidget(self._button('×', '閉じる',
                                    'CLOSE', width=22, height=22, role='icon'))
        self.more_menu = QMenu(self)
        self.more_menu.setObjectName('remoteMoreMenu')
        self.more_settings_action = self.more_menu.addAction('設定')
        self.more_category_action = self.more_menu.addAction('検索履歴カテゴリーを追加')
        self.more_favorite_action = self.more_menu.addAction('現在のフォルダーをお気に入り登録')
        self.more_url_favorite_action = self.more_menu.addAction('現在のアドレスをお気に入り登録')
        self.more_new_tab_action = self.more_menu.addAction('新規タブ追加')
        # Use the *actual* main-window glyphs (not a platform folder icon).
        # The menu text stays unchanged; Qt reserves an icon column itself.
        self.update_more_menu_icons(launcher.theme_button.icon(),
                                    launcher.history_category_action.icon(),
                                    launcher.expanded_view.favorite_save.text())
        self.more_settings_action.triggered.connect(
            lambda checked=False: self.command.emit('REMOTE_SETTINGS'))
        self.more_category_action.triggered.connect(
            lambda checked=False: self.command.emit('REMOTE_CATEGORY_ADD'))
        self.more_favorite_action.triggered.connect(
            lambda checked=False: self.command.emit('REMOTE_FAVORITE_SAVE'))
        self.more_url_favorite_action.triggered.connect(
            lambda checked=False: self.command.emit('REMOTE_URL_FAVORITE_SAVE'))
        self.more_new_tab_action.setIcon(browser_navigation_icon(
            'plus', theme_family(launcher.color_theme)))
        self.more_new_tab_action.triggered.connect(
            lambda checked=False: self.command.emit('REMOTE_NEW_WEB_TAB'))
        self.more_menu.aboutToShow.connect(self.more_menu_opening.emit)
        root.addWidget(title_frame)
        # The header's empty background and title text move this frameless
        # window; its HOME/MORE/CLOSE buttons keep their native click behavior.
        self._passive_header_drag = PassiveHeaderDrag(self, on_header_press=self.header_pressed.emit)
        title_frame.installEventFilter(self._passive_header_drag)
        title.installEventFilter(self._passive_header_drag)

        # Remote Page selector: click opens that Page's compact first column.
        # Its child categories use the existing CascadeMenu hover/search logic.
        self.page_buttons = []
        self.page_column = QVBoxLayout()
        self.page_column.setContentsMargins(0, 0, 0, 0)
        self.page_column.setSpacing(3)
        root.addLayout(self.page_column)
        self.set_pages(getattr(launcher, 'pages', ()))

        # Separate the three Page launchers from the Files/Browser controls.
        self.page_separator = QFrame(self)
        self.page_separator.setObjectName('remotePageSeparator')
        self.page_separator.setFixedHeight(7)
        root.addWidget(self.page_separator)

        # Promoted Files Exp: a full-width Remote control above Files/Browser.
        # Both mouse buttons toggle the same registered-folder tree.
        self.files_exp_panel = None
        self.files_exp_theme = launcher.color_theme
        self.files_exp_button = self._button(
            'Files Exp', '登録フォルダーのツリーを開く（左右クリック対応）',
            'FILES_EXP_PREVIEW', width=172, height=27, role='workspace',
            wheel_enabled=True)
        self.files_exp_button.clicked.disconnect()
        self.files_exp_button.clicked.connect(self.toggle_files_exp)
        self.files_exp_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.files_exp_button.customContextMenuRequested.connect(
            lambda _point: self.toggle_files_exp())
        root.addWidget(self.files_exp_button)

        # One-click mode switch, directly above BackTab/Tab.  Wheel gestures
        # on these buttons still go through the shared WheelPad accumulator.
        # Geometry shared by the Page and all control rows:
        # Page = 172px. Two columns = 85 + 2 gap + 85 = 172px.
        # Wheel row = 50 + 2 gap + 68 + 2 gap + 50 = 172px.
        # Every row starts at the same 5px root left margin.
        row_workspaces = QHBoxLayout()
        row_workspaces.setContentsMargins(0, 0, 0, 0)
        row_workspaces.setSpacing(2)
        self.files_button = self._button('Files', 'Files画面へ切り替え / 右クリック：第1列から開く',
                                         'WORKSPACE_FILES', width=85, height=27,
                                         role='workspace', wheel_enabled=True)
        self.files_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.files_button.customContextMenuRequested.connect(
            lambda _point: self.command.emit('REMOTE_FILES_FIRST_COLUMN_MENU'))
        self.browser_button = self._button('Browser', 'Browser画面へ切り替え / 右クリック：ブックマークを展開',
                                           'WORKSPACE_BROWSER', width=85, height=27,
                                           role='workspace', wheel_enabled=True)
        # Mirror Files: right-click opens a non-modal, searchable cascade.
        # Native left-click remains WORKSPACE_BROWSER, never a context action.
        self.browser_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.browser_button.customContextMenuRequested.connect(
            lambda _point: self.command.emit('REMOTE_BROWSER_BOOKMARK_MENU'))
        row_workspaces.addWidget(self.files_button)
        row_workspaces.addWidget(self.browser_button)
        root.addLayout(row_workspaces)
        # History -> TAB controls -> wheel pad: keep Tab/BackTab next to the
        # history operations and immediately above the three-way wheel row.
        row_bottom = QHBoxLayout()
        row_bottom.setContentsMargins(0, 0, 0, 0)
        row_bottom.setSpacing(2)
        row_bottom.addWidget(self._button('検索履歴', '1回目：検索履歴を開く／2回目：選択中の履歴を決定。ダブルクリック：検索結果のカレント行を実行',
                                          'SEARCH_HISTORY', width=85, height=37, role='small', wheel_enabled=True))
        self.folder_history_button = self._button(
            'フォルダー履歴', '1回目：フォルダー履歴を開く／2回目：選択中のフォルダーへ移動',
            'FOLDER_HISTORY', width=85, height=37, role='small', wheel_enabled=True)
        row_bottom.addWidget(self.folder_history_button)
        root.addLayout(row_bottom)
        row_mid = QHBoxLayout()
        row_mid.setContentsMargins(0, 0, 0, 0)
        row_mid.setSpacing(2)
        row_mid.addWidget(self._button('←', '戻る / 左へ',
                                       'LEFT', width=50, height=46))
        self.pad = WheelPad(self, compact=True)
        self.pad.command.connect(self.command.emit)
        row_mid.addWidget(self.pad)
        row_mid.addWidget(self._button('→', 'フォルダーへ / 右へ',
                                       'RIGHT', width=50, height=46))
        # The wheel row is added after the Tab/BackTab row below.

        row_top = QHBoxLayout()
        row_top.setContentsMargins(0, 0, 0, 0)
        row_top.setSpacing(2)
        row_top.addWidget(self._button('BackTab', '前の操作列へ',
                                       'BACKTAB', width=85, height=37, role='tab', wheel_enabled=True))
        row_top.addWidget(self._button('Tab', '次の操作列へ',
                                       'TAB', width=85, height=37, role='tab', wheel_enabled=True))
        root.addLayout(row_top)
        root.addLayout(row_mid)

        self.up_band = UpDoubleClickBand(self)
        self.up_band.command.connect(self.command.emit)
        root.addWidget(self.up_band)

        # The current target is status information, not a control.
        status_frame = QFrame(self)
        status_frame.setObjectName('remoteStatusBar')
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(5, 2, 5, 2)
        self.area_label = QLabel('操作先：', status_frame)
        self.area_label.setObjectName('remoteAreaLabel')
        self.area_label.setFixedHeight(16)
        status_layout.addWidget(self.area_label)
        root.addWidget(status_frame)

        # The old caption and up/down buttons are intentionally omitted.
        # The wheel pad emits UP/DOWN, CLICK and DOUBLE_CLICK without synthetic keys.
        self.adjustSize()
        # Keep the window large enough for the intentionally tall tab/history
        # buttons. Their height is fixed on each button, not by the stylesheet.
        self.setMinimumHeight(root.sizeHint().height())

        # Accept the same wheel gesture over *every* Remote surface: empty
        # strips, title/status text, arrows, Page buttons and the central pad.
        # Never install this on a cascade QMenu (it has its own window/scroll).
        self.installEventFilter(self)
        for widget in self.findChildren(QWidget):
            if widget.window() is self:
                widget.installEventFilter(self)

    def hideEvent(self, event):
        # The experimental tool window must not outlive a dismissed Remote.
        panel = getattr(self, 'files_exp_panel', None)
        if panel is not None:
            panel.hide()
        # A pending single-click must not reopen history after Remote closes.
        timer = getattr(self, 'search_history_click_timer', None)
        if timer is not None:
            timer.stop()
        super().hideEvent(event)

    def toggle_files_exp(self):
        """Show/hide the registered-folder tree while retaining the Files view."""
        if self.files_exp_panel is None:
            self.files_exp_panel = RemoteFilesExplorer(self, self.files_exp_theme)
            self.files_exp_panel.folder_selected.connect(self.files_exp_folder_selected.emit)
            self.files_exp_panel.folder_context_requested.connect(self.files_exp_folder_context.emit)
            self.files_exp_panel.folder_renamed.connect(self.files_exp_folder_renamed.emit)
        panel = self.files_exp_panel
        if panel.isVisible():
            panel.hide()
            return
        # Use precisely the same rendered first-column rows as Files' Remote
        # context menu. Never rebuild roots from the config JSON or breadcrumb.
        launcher = self.parent()
        if launcher is not None and hasattr(launcher, '_remote_files_first_column_rows'):
            panel.set_roots(launcher._remote_files_first_column_rows(),
                            launcher.expander().expand)
        self.position_files_exp()
        panel.show()
        panel.raise_()
        # On reopening, the tree should reflect the already-active Files
        # breadcrumb, not retain an unrelated root selection.
        if launcher is not None:
            view = getattr(launcher, 'expanded_view', None)
            if view is not None and view.current_directory():
                panel.sync_current_directory(view.current_directory())
        # Frameless Tool windows may be placed by Windows on first show.
        # Reassert the Remote-relative anchor after native show processing.
        QTimer.singleShot(0, self.position_files_exp)

    def position_files_exp(self):
        """Attach Files Exp top-left to Remote top-right, even during drag."""
        panel = getattr(self, 'files_exp_panel', None)
        if panel is None:
            return
        anchor = self.mapToGlobal(QPoint(self.width(), 0))
        screen = QApplication.screenAt(anchor) or QApplication.primaryScreen()
        x, y = anchor.x(), anchor.y()
        if screen is not None:
            area = screen.availableGeometry()
            # Flip beside the Remote only if there's no room to the right.
            if x + panel.width() > area.right() + 1:
                left = self.mapToGlobal(QPoint(-panel.width(), 0)).x()
                if left >= area.left():
                    x = left
            x = max(area.left(), min(x, area.right() - panel.width() + 1))
            y = max(area.top(), min(y, area.bottom() - panel.height() + 1))
        if panel.pos() != QPoint(x, y):
            panel.move(x, y)

    def moveEvent(self, event):
        super().moveEvent(event)
        panel = getattr(self, 'files_exp_panel', None)
        if panel is not None and panel.isVisible():
            self.position_files_exp()

    def focus_cursor_on_files_exp(self):
        """Desktop-double-click only: move pointer to the Files Exp button."""
        launcher = self.parent()
        if not getattr(launcher, 'pointer_warp_enabled', True):
            return
        if not self.isVisible():
            return
        from PySide6.QtGui import QCursor
        QCursor.setPos(self.files_exp_button.mapToGlobal(
            self.files_exp_button.rect().center()))

    def eventFilter(self, obj, event):
        if (event.type() == QEvent.Type.Wheel
                and (obj is self or (isinstance(obj, QWidget) and obj.window() is self))
                and hasattr(self, 'pad')):
            # Directly reuse WheelPad's angle/pixel remainder so a half-step
            # over one button plus a half-step over another is one movement.
            # This does not synthesize keys or trigger any button's click.
            self.pad.wheelEvent(event)
            return True
        return super().eventFilter(obj, event)

    def paintEvent(self, event):
        """Render a truly rounded window with a thin pale-grey outline."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self._remote_background)
        painter.setPen(QPen(self._remote_outline, 1))
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), 10, 10)
        painter.end()

    def apply_theme(self, theme):
        """Follow the Launch appearance palette, including live theme changes."""
        self.files_exp_theme = theme
        panel = getattr(self, 'files_exp_panel', None)
        if panel is not None:
            panel.apply_theme(theme)
        c = theme_palette(theme)
        # The initial theme is applied before the header button exists.
        # On subsequent theme changes refresh the shared vector icon too.
        if hasattr(self, 'home_button'):
            self.home_button.setIcon(browser_navigation_icon('home', theme_family(theme)))
        if hasattr(self, 'more_new_tab_action'):
            self.more_new_tab_action.setIcon(browser_navigation_icon(
                'plus', theme_family(theme)))
        self._remote_background = QColor(c['panel'])
        self._remote_outline = QColor('#ccd3d7')  # subtle light-grey, 1px
        self.setStyleSheet(f"""
            QWidget#launchRemoteWindow {{ background:transparent; border:0; }}
            QFrame#remoteTitleBar {{background:{c['header']};
                border:1px solid {c['panel_border']};border-radius:5px;}}
            QFrame#remoteStatusBar {{background:{c['subheader']};
                border:1px solid {c['panel_border']};border-radius:4px;}}
            QFrame#remotePageSeparator {{background:transparent;border:0;
                border-top:1px solid {c['panel_border']};margin:3px 2px 0 2px;}}
            QPushButton {{background:{c['panel_header']};color:{c['text']};
                border:1px solid {c['panel_border']};border-radius:5px;
                font-size:12px;padding:0 4px;}}
            QPushButton[role="small"] {{font-size:12px;padding:0 2px;}}
            QPushButton[role="tab"] {{font-size:12px;}}
            QPushButton[role="workspace"] {{font-size:12px;}}
            QPushButton[role="page"] {{text-align:left;padding-left:10px;font-size:12px;}}
            QPushButton[role="workspace"][active="true"] {{background:{c['selection']};
                border:1px solid {c['focus_outline']};}}
            QPushButton[role="icon"] {{font-size:12px;padding:0;}}
            QPushButton#remoteHomeButton {{border-radius:7px;padding:0;}}
            QPushButton:hover {{background:{c['hover']};}}
            QPushButton:pressed {{background:{c['selection']};}}
            QLabel {{background:transparent;color:{c['text']};border:0;}}
            QLabel#remoteTitle {{font-size:10px;font-weight:bold;}}
            QMenu#remoteMoreMenu {{background:{c['panel']};color:{c['text']};
                border:1px solid {c['panel_border']};padding:3px;}}
            QMenu#remoteMoreMenu::item {{padding:7px 14px;}}
            /* Equal left/right whitespace around each leading icon.
               The menu's native icon slot remains keyboard-accessible. */
            QMenu#remoteMoreMenu::icon {{padding-left:6px;padding-right:6px;}}
            QMenu#remoteMoreMenu::item:selected {{background:{c['hover']};}}
            QMenu#remoteMoreMenu::item:disabled {{color:{c['muted_text']};}}
            QLabel#remoteAreaLabel {{color:{c['muted_text']};font-size:10px;font-weight:bold;}}
            QLabel#remotePadCaption {{color:{c['muted_text']};font-size:10px;}}
            QLabel#remotePadLabel {{font-size:9px;font-weight:bold;}}
            QLabel#remotePadGlyph {{font-family:'Segoe UI Emoji';font-size:11px;}}
            QFrame#remoteUpDoubleClickBand {{border:0;background:transparent;}}
            QFrame#remoteUpDoubleClickBand QLabel {{color:{c['muted_text']};font-size:10px;}}
            QFrame#remoteWheelPad {{background:{c['selection']};
                border:1px dashed {c['focus_outline']};border-radius:5px;}}
        """)
        self.update()

    def set_pages(self, pages):
        """Mirror the current configured Page order; no separate menu data."""
        for button in self.page_buttons:
            self.page_column.removeWidget(button)
            button.deleteLater()
        self.page_buttons = []
        for page in list(pages)[:3]:
            page_id = str(page.get('page_id', ''))
            if not page_id:
                continue
            button = self._button(str(page.get('title', 'Page')),
                                  '左クリック／右クリック：このPageのメニューを右に表示',
                                  'PAGE_BUTTON_UNUSED', width=172, height=27,
                                  role='page')
            # Do not emit the generic command; Page selection has its own signal.
            button.clicked.disconnect()
            button.clicked.connect(lambda checked=False, pid=page_id:
                                   self.page_clicked.emit(pid))
            button.setProperty('remote_page_id', page_id)
            button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            button.customContextMenuRequested.connect(
                lambda _point, pid=page_id: self.page_clicked.emit(pid))
            self.page_column.addWidget(button)
            self.page_buttons.append(button)
        self.adjustSize()

    def set_workspace(self, mode):
        self.up_band.set_files_mode(mode == 'files')
        self.folder_history_button.setToolTip(
            '1回目：URLのお気に入りを開く／2回目：選択中のURLを開く'
            if mode == 'browser' else
            '1回目：フォルダー履歴を開く／2回目：選択中のフォルダーへ移動')
        """Active mode is visible even though Remote never takes focus."""
        for button, value in ((self.files_button, 'files'),
                              (self.browser_button, 'browser')):
            active = mode == value
            if button.property('active') != active:
                button.setProperty('active', active)
                button.style().unpolish(button)
                button.style().polish(button)

    def set_more_menu_mode(self, mode, *, can_add_tab=True):
        browser = mode == 'browser'
        self.more_new_tab_action.setVisible(browser)
        self.more_new_tab_action.setEnabled(browser and can_add_tab)
        self.more_category_action.setVisible(not browser)
        self.more_favorite_action.setVisible(not browser)
        self.more_url_favorite_action.setVisible(browser)

    def show_more_menu(self):
        """Show a three-action menu next to …, not over the main Launcher."""
        width = self.more_menu.sizeHint().width()
        height = self.more_menu.sizeHint().height()
        point = self.more_button.mapToGlobal(
            QPoint(self.more_button.width() - width, self.more_button.height() + 2))
        screen = QApplication.screenAt(self.more_button.mapToGlobal(QPoint(0, 0)))
        if screen is None:
            screen = QApplication.primaryScreen()
        if screen is not None:
            area = screen.availableGeometry()
            point.setX(max(area.left(), min(point.x(), area.right() - width + 1)))
            if point.y() + height > area.bottom() + 1:
                point.setY(self.more_button.mapToGlobal(QPoint(0, -height - 2)).y())
            point.setY(max(area.top(), min(point.y(), area.bottom() - height + 1)))
        self.more_menu.popup(point)

    def update_more_menu_icons(self, settings_icon, category_icon, favorite_heart):
        """Reuse Launch settings/search icons and the breadcrumb heart glyph."""
        self.more_settings_action.setIcon(settings_icon)
        self.more_category_action.setIcon(category_icon)
        self.more_favorite_action.setIcon(remote_favorite_icon(favorite_heart))
        # The Browser address bar's heart and the Files breadcrumb heart
        # share one icon language; each action has its own enabled state.
        self.more_url_favorite_action.setIcon(remote_favorite_icon(favorite_heart))

    def set_url_favorite_action_available(self, available):
        self.more_url_favorite_action.setEnabled(bool(available))

    def set_favorite_action_available(self, available):
        """Do not offer the heart action outside a valid Files directory."""
        self.more_favorite_action.setEnabled(bool(available))

    def _button(self, text, tip, command, *, width=50, height=24,
                role='normal', wheel_enabled=False):
        button = (RemoteSearchHistoryButton(text, self) if command == 'SEARCH_HISTORY'
                  else RemoteWheelButton(text, self) if wheel_enabled
                  else QPushButton(text, self))
        button.setToolTip(tip)
        button.setProperty('role', role)
        button.setFixedSize(width, height)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # Dynamic Page buttons are rebuilt by set_pages() on every Remote
        # opening, so install the shared wheel listener at construction time.
        if hasattr(button, 'installEventFilter'):
            button.installEventFilter(self)
        if command == 'SEARCH_HISTORY':
            # Delay ONLY this button's single click; a native double-click
            # must not first confirm a history keyword and change results.
            timer = QTimer(button)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self.command.emit('SEARCH_HISTORY'))
            button.clicked.connect(lambda checked=False: timer.start(
                QApplication.instance().doubleClickInterval()))
            button.double_clicked.connect(lambda: (
                timer.stop(), self.command.emit('SEARCH_RESULT_DOUBLE_CLICK')))
            self.search_history_click_timer = timer
        else:
            button.clicked.connect(lambda checked=False, name=command: self.command.emit(name))
        return button

    def set_area(self, name):
        labels = {'search': '検索', 'pages': 'Page', 'roots': '第1列メニュー',
                  'files': 'Files第1列', 'directory': 'Files第2列',
                  'sort': '第2列 並び替え', 'bookmarks': 'ブックマーク', 'list': '検索結果・メニュー',
                  'search_history': '検索履歴', 'folder_history': 'フォルダー履歴',
                  'browser_history': 'URLお気に入り',
                  'cascade': '展開メニュー', 'breadcrumb': 'パンくず',
                  'web_tabs': 'Webタブ', 'web_body': 'Web本文',
                  'workspace_files': 'Filesタブ', 'workspace_browser': 'Browserタブ'}
        label = ('Web本文 ' + str(int(name.split(':', 1)[1]) + 1) if
                 name.startswith('web_body:') and name.split(':', 1)[1].isdigit()
                 else labels.get(name, name))
        self.area_label.setText('操作先：' + label)

    def show_at(self, global_point):
        screen = QApplication.screenAt(global_point)
        if screen is None:
            screen = QApplication.primaryScreen()
        if screen is None:
            return
        rect = screen.availableGeometry()
        # The wheel pad (not the remote's title!) should appear right under
        # the desktop click. Start scrolling without chasing another widget.
        self.layout().activate()
        center = self.pad.geometry().center()
        x, y = popup_at_hotspot(global_point.x(), global_point.y(),
                                self.width(), self.height(),
                                rect.left(), rect.top(), rect.right() + 1, rect.bottom() + 1,
                                center.x(), center.y())
        self.move(QPoint(x, y))
        self.show()
        self.raise_()
