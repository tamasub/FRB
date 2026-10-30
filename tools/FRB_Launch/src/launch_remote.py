"""An experimental mouse-side remote for FRB Launch.

Mouse actions emit semantic commands.  No SendKeys, synthetic key presses or
cross-process keyboard injection are involved.
"""

from PySide6.QtCore import Qt, Signal, QPoint, QRect, QRectF, QSize
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QPixmap, QIcon
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                                QLabel, QFrame, QApplication, QMenu)
from remote_navigation import popup_at_hotspot
from passive_header_drag import PassiveHeaderDrag
from launch_appearance import theme_palette, theme_family
from browser_nav_icons import browser_navigation_icon


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
            self.setFixedSize(56, 46)
        else:
            self.setMinimumHeight(70)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1 if self._compact else 4,
                                  1 if self._compact else 8,
                                  1 if self._compact else 4,
                                  1 if self._compact else 8)
        layout.setSpacing(2 if self._compact else 4)
        label = QLabel('◉ ぐりぐり' if not self._compact else 'ぐりぐり', self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setObjectName('remotePadLabel')
        label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(label)
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


class UpDoubleClickBand(QFrame):
    """Blank Remote strip: left double-click = Back, right-click = folder menu."""
    command = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('remoteUpDoubleClickBand')
        self.setFixedHeight(23)
        self.setToolTip('ダブルクリック：第2列の上位フォルダーへ / 右クリック：第2列の空白メニュー')
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.command.emit('FOLDER_UP')
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        # Use Qt's native context-menu event (on Windows it arrives on mouse
        # release). Do not synthesize a click or select a row in Launch.
        self.command.emit('BACKGROUND_CONTEXT_MENU')
        event.accept()


class LaunchRemote(QWidget):
    command = Signal(str)
    header_pressed = Signal()
    more_menu_opening = Signal()

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
        self.more_menu.aboutToShow.connect(self.more_menu_opening.emit)
        root.addWidget(title_frame)
        # The header's empty background and title text move this frameless
        # window; its HOME/MORE/CLOSE buttons keep their native click behavior.
        self._passive_header_drag = PassiveHeaderDrag(self, on_header_press=self.header_pressed.emit)
        title_frame.installEventFilter(self._passive_header_drag)
        title.installEventFilter(self._passive_header_drag)

        # Three dense rows: no empty middle column in the top/bottom rows.
        row_top = QHBoxLayout()
        row_top.setContentsMargins(0, 0, 0, 0)
        row_top.setSpacing(2)
        row_top.addStretch(1)
        row_top.addWidget(self._button('BackTab', '前の操作列へ',
                                       'BACKTAB', width=76, height=37, role='tab', wheel_enabled=True))
        row_top.addWidget(self._button('Tab', '次の操作列へ',
                                       'TAB', width=76, height=37, role='tab', wheel_enabled=True))
        row_top.addStretch(1)
        root.addLayout(row_top)

        row_mid = QHBoxLayout()
        row_mid.setContentsMargins(0, 0, 0, 0)
        row_mid.setSpacing(2)
        row_mid.addStretch(1)
        row_mid.addWidget(self._button('←', '戻る / 左へ',
                                       'LEFT', width=45, height=44))
        self.pad = WheelPad(self, compact=True)
        self.pad.command.connect(self.command.emit)
        row_mid.addWidget(self.pad)
        row_mid.addWidget(self._button('→', 'フォルダーへ / 右へ',
                                       'RIGHT', width=45, height=44))
        row_mid.addStretch(1)
        root.addLayout(row_mid)

        row_bottom = QHBoxLayout()
        row_bottom.setContentsMargins(0, 0, 0, 0)
        row_bottom.setSpacing(2)
        row_bottom.addStretch(1)
        row_bottom.addWidget(self._button('検索履歴', 'メイン検索の履歴を開く / 選択',
                                          'SEARCH_HISTORY', width=84, height=37, role='small', wheel_enabled=True))
        row_bottom.addWidget(self._button('フォルダー履歴', 'パンくずのフォルダー履歴を開く / 選択',
                                          'FOLDER_HISTORY', width=84, height=37, role='small', wheel_enabled=True))
        row_bottom.addStretch(1)
        root.addLayout(row_bottom)
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
        c = theme_palette(theme)
        # The initial theme is applied before the header button exists.
        # On subsequent theme changes refresh the shared vector icon too.
        if hasattr(self, 'home_button'):
            self.home_button.setIcon(browser_navigation_icon('home', theme_family(theme)))
        self._remote_background = QColor(c['panel'])
        self._remote_outline = QColor('#ccd3d7')  # subtle light-grey, 1px
        self.setStyleSheet(f"""
            QWidget#launchRemoteWindow {{ background:transparent; border:0; }}
            QFrame#remoteTitleBar {{background:{c['header']};
                border:1px solid {c['panel_border']};border-radius:5px;}}
            QFrame#remoteStatusBar {{background:{c['subheader']};
                border:1px solid {c['panel_border']};border-radius:4px;}}
            QPushButton {{background:{c['panel_header']};color:{c['text']};
                border:1px solid {c['panel_border']};border-radius:5px;
                font-size:12px;padding:0 4px;}}
            QPushButton[role="small"] {{font-size:12px;padding:0 2px;}}
            QPushButton[role="tab"] {{font-size:12px;}}
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
            QFrame#remoteWheelPad {{background:{c['selection']};
                border:1px dashed {c['focus_outline']};border-radius:5px;}}
        """)
        self.update()

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

    def set_favorite_action_available(self, available):
        """Do not offer the heart action outside a valid Files directory."""
        self.more_favorite_action.setEnabled(bool(available))

    def _button(self, text, tip, command, *, width=50, height=24,
                role='normal', wheel_enabled=False):
        button = (RemoteWheelButton(text, self) if wheel_enabled
                  else QPushButton(text, self))
        button.setToolTip(tip)
        button.setProperty('role', role)
        button.setFixedSize(width, height)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.clicked.connect(lambda checked=False, name=command: self.command.emit(name))
        return button

    def set_area(self, name):
        labels = {'search': '検索', 'pages': 'Page', 'roots': '第1列メニュー',
                  'files': 'Files第1列', 'directory': 'Files第2列',
                  'sort': '第2列 並び替え', 'bookmarks': 'ブックマーク', 'list': '検索結果・メニュー',
                  'search_history': '検索履歴', 'folder_history': 'フォルダー履歴',
                  'cascade': '展開メニュー', 'breadcrumb': 'パンくず'}
        self.area_label.setText('操作先：' + labels.get(name, name))

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
