"""An experimental mouse-side remote for FRB Launch.

Mouse actions emit semantic commands.  No SendKeys, synthetic key presses or
cross-process keyboard injection are involved.
"""

from PySide6.QtCore import Qt, QEvent, Signal, QPoint, QRect, QRectF, QSize, QTimer
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QPixmap, QIcon
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                                QLabel, QFrame, QApplication, QMenu)
from remote_navigation import popup_at_hotspot
from remote_grid_alignment import files_grid_layout, remote_next_to_exp
from passive_header_drag import PassiveHeaderDrag
from launch_appearance import theme_palette, theme_family
from browser_nav_icons import browser_navigation_icon
from remote_files_explorer import RemoteFilesExplorer
from remote_shuriken import ShurikenButton, ShurikenPreview
from shuriken_model import ShurikenEntry, choose_entry
from remote_shuriken_scroll import ShurikenScrollPad
from mouse_pointer_rod import MousePointerRodPad, MousePointerRodOrigin


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


def remote_compact_icon(kind: str, light: bool) -> QIcon:
    """Scalable Remote symbols; HOME shares the main-window geometry."""
    if kind == 'home':
        return browser_navigation_icon('home', 'light' if light else 'dark')
    image = QPixmap(64, 64)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    ink = QColor('#24483d' if light else '#e4f6ee')
    painter.setPen(QPen(ink, 3.2))
    if kind == 'remote':
        painter.setBrush(ink)
        painter.drawRoundedRect(15, 4, 34, 56, 9, 9)
        painter.setBrush(QColor('#f4fbf8' if light else '#132b25'))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(21, 9, 22, 22)
        painter.setBrush(QColor('#f4fbf8' if light else '#132b25'))
        for x in (24, 32, 40):
            painter.drawEllipse(x - 3, 44, 6, 6)
    elif kind == 'keyboard':
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(5, 12, 54, 40, 6, 6)
        painter.setBrush(ink)
        painter.setPen(Qt.PenStyle.NoPen)
        for y in (20, 29, 38):
            for x in (13, 23, 33, 43):
                if y == 38 and x in (23, 33):
                    continue
                painter.drawRoundedRect(x, y, 7, 6, 1, 1)
        painter.drawRoundedRect(23, 39, 17, 5, 1, 1)
    painter.end()
    return QIcon(image)


class WheelPad(QFrame):
    command = Signal(str)
    # The legacy horizontal drag-to-LEFT/RIGHT navigation is RETIRED.
    # A deliberate hold opens the two-way Exp/List shuriken target selector.
    DRAG_THRESHOLD_PX = 18  # Cancel long-press when dragging too early.
    TARGET_SELECT_DEADZONE_PX = 12  # Only used while eye is at its origin.
    TARGET_MENU_HOLD_MS = 450

    def __init__(self, parent=None, *, compact=False):
        super().__init__(parent)
        self.setObjectName('remoteWheelPad')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip('ホイールで選択／クリック・ダブルクリック／長押し→左右へシュッでExp列・List列を選択／右クリックでメニュー')
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._angle_remainder = 0
        self._pixel_remainder = 0
        self._rod_wheel_angle_remainder = 0
        self._rod_wheel_pixel_remainder = 0
        self._pressed = False
        self._ignore_double_release = False
        self._drag_start_pos = None
        self._dragged = False
        self._target_menu_open = False
        self._target_preview = None
        self._target_choice = None  # Exactly the choice the eye last displayed.
        self.target_switch_allowed = None  # Remote supplies Files-only eligibility.
        self._target_entries = (
            ShurikenEntry('REMOTE_TARGET_EXP', 'Exp列', 0, 'left', 0),
            ShurikenEntry('REMOTE_TARGET_LIST', 'List列', 0, 'right', 1),
        )
        self._target_hold_timer = QTimer(self)
        self._target_hold_timer.setSingleShot(True)
        self._target_hold_timer.timeout.connect(self._show_target_menu)
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

    def _target_allowed(self):
        allowed = getattr(self, 'target_switch_allowed', None)
        return bool(callable(allowed) and allowed())

    def _show_target_menu(self):
        """Long press only: show the existing Pokeball current-dot guide."""
        if (not self._pressed or self._dragged
                or self._drag_start_pos is None or not self._target_allowed()):
            return
        if self._target_preview is None:
            self._target_preview = ShurikenPreview(self)
        self._target_choice = None
        self._target_menu_open = True
        self._target_preview.present(self, self._target_entries, self._target_choice)

    def _hide_target_menu(self):
        timer = getattr(self, '_target_hold_timer', None)
        if timer is not None:
            timer.stop()
        preview = getattr(self, '_target_preview', None)
        if preview is not None:
            preview.hide()
        self._target_menu_open = False
        self._target_choice = None

    def hideEvent(self, event):
        self._hide_target_menu()
        self._pressed = False
        self._drag_start_pos = None
        self._dragged = False
        super().hideEvent(event)

    def wheelEvent(self, event):
        # Works both for native pad events and button wheel forwarding.
        # Ctrl+wheel changes ONLY the Remote background transparency.
        parent_method = getattr(self, 'parentWidget', None)
        owner = parent_method() if callable(parent_method) else None
        remote = getattr(owner, '_remote', None) or owner
        adjust_opacity = getattr(remote, 'adjust_background_opacity_from_wheel', None)
        if callable(adjust_opacity) and adjust_opacity(event):
            return
        # This button ALWAYS keeps the original Files/Browser navigation,
        # including when physically embedded in the blue pointing-rod pad.
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
        # A single physical wheel event has ONE owner. Capture that owner
        # BEFORE processing its notches: if the flight becomes invalid during
        # this event, the remaining notches must not leak to the old current.
        # This applies equally over ぐりぐり and the shuriken scroll button.
        scroll_pad = getattr(remote, 'scroll_pad', None)
        flight_owned_wheel = (scroll_pad is not None
                              and getattr(scroll_pad, '_flight', None) is not None)
        # Fast wheel over Remote ぐりぐり while targeting Files List may arm
        # the SAME shuriken engine as a physical wheel over the List itself.
        # During a flight, keep the original wheel_while_flying owner below.
        launcher = getattr(remote, 'launcher', None)
        auto_input = getattr(launcher, 'shuriken_wheel_list_input', None)
        if (not flight_owned_wheel and steps and callable(auto_input)
                and getattr(launcher, '_remote_area', None) == 'directory'
                and auto_input(max(-5, min(5, steps)), source='remote')):
            event.accept()
            return
        for _ in range(min(abs(steps), 5)):
            direction = 'UP' if steps > 0 else 'DOWN'
            if flight_owned_wheel:
                if getattr(scroll_pad, '_flight', None) is not None:
                    scroll_pad.wheel_while_flying(direction)
                # Invalid/finished flight never falls through to a current
                # step within this same physical wheel event.
                continue
            self.command.emit(direction)
        event.accept()

    def mousePressEvent(self, event):
        self._pressed = event.button() == Qt.MouseButton.LeftButton
        if event.button() == Qt.MouseButton.RightButton:
            event.accept()
            return
        if self._pressed:
            self._hide_target_menu()
            self._drag_start_pos = event.position().toPoint()
            self._dragged = False
            timer = getattr(self, '_target_hold_timer', None)
            if timer is not None and self._target_allowed():
                timer.start(self.TARGET_MENU_HOLD_MS)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Qt implicitly grabs the mouse while the left button is held. This
        # continues to work if the pointer leaves the small pad's rectangle.
        # Do NOT move this widget or its parent window.
        start = getattr(self, '_drag_start_pos', None)
        if self._pressed and start is not None:
            pos = event.position().toPoint()
            dx, dy = pos.x() - start.x(), pos.y() - start.y()
            if self._target_menu_open:
                # The green eye and the pending command are ONE state.
                # Once the eye chooses a side, no later velocity, distance,
                # or release-coordinate test can silently cancel it.
                self._target_choice = choose_entry(
                    self._target_entries, dx, dy,
                    min_release_distance=self.TARGET_SELECT_DEADZONE_PX)
                if self._target_preview is not None:
                    self._target_preview.present(
                        self, self._target_entries, self._target_choice)
            elif (abs(dx) >= self.DRAG_THRESHOLD_PX or
                  abs(dy) >= self.DRAG_THRESHOLD_PX):
                # Before the hold, movement CANCELS the timer. The old drag
                # must not silently navigate List to its first row.
                self._dragged = True
                timer = getattr(self, '_target_hold_timer', None)
                if timer is not None:
                    timer.stop()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        # Preserve the existing native double-click command. A drag never
        # synthesizes DOUBLE_CLICK or a second CLICK.
        if event.button() == Qt.MouseButton.LeftButton:
            self._hide_target_menu()
            self._pressed = False
            self._drag_start_pos = None
            self._dragged = False
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
            self._hide_target_menu()
            self._ignore_double_release = False
            self._pressed = False
            self._drag_start_pos = None
            self._dragged = False
            event.accept()
            return
        if self._pressed and event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            pos = event.position().toPoint()
            start = getattr(self, '_drag_start_pos', None)
            self._drag_start_pos = None
            moved = getattr(self, '_dragged', False)
            self._dragged = False
            if start is not None:
                dx, dy = pos.x() - start.x(), pos.y() - start.y()
                moved = moved or abs(dx) >= self.DRAG_THRESHOLD_PX or abs(dy) >= self.DRAG_THRESHOLD_PX
            else:
                dx, dy = 0, 0
            # A long-press gesture selects the *operating target* only.
            # NEVER reuse old LEFT/RIGHT (List LEFT can jump to row one).
            menu_open = getattr(self, '_target_menu_open', False)
            # Commit EXACTLY the current eye's displayed selection, not a
            # second release-time hit test with another distance threshold.
            # Releasing slowly is intentionally identical to releasing fast.
            chosen = (getattr(self, '_target_choice', None)
                      if menu_open and self._target_allowed() else None)
            self._hide_target_menu()
            if chosen is not None:
                self.command.emit(chosen.item_id)
            elif not menu_open and not moved and self.rect().contains(pos):
                self.command.emit('CLICK')
            event.accept()
        else:
            self._pressed = False
            self._drag_start_pos = None
            self._dragged = False
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
        self.setFixedHeight(46)
        self.setToolTip('ダブルクリック：上位フォルダーへ / 右クリック：List カレントフォルダー操作')
        self._files_mode = True
        self._skip_release_after_double = False
        self._single_click_timer = QTimer(self)
        self._single_click_timer.setSingleShot(True)
        self._single_click_timer.timeout.connect(
            lambda: self.command.emit('REMOTE_FOLDER_DESELECT') if self._list_is_active() else None)
        self._caption = QLabel('（List カレントフォルダー操作）', self)
        self._caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._caption.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._caption)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def _list_is_active(self):
        """The lower blank band belongs exclusively to Files List."""
        remote = self.parentWidget()
        return (self._files_mode and remote is not None and
                getattr(remote, '_files_operating_target', None) == 'directory')

    def set_files_mode(self, enabled):
        self._files_mode = bool(enabled)
        if not enabled:
            self._single_click_timer.stop()
        self._caption.setVisible(self._files_mode)

    def mouseReleaseEvent(self, event):
        if not self._list_is_active():
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._files_mode:
            if self._skip_release_after_double:
                self._skip_release_after_double = False
                event.accept()
                return
            self._single_click_timer.start(QApplication.instance().doubleClickInterval())
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if not self._list_is_active():
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._files_mode:
            self._single_click_timer.stop()
            self._skip_release_after_double = True
            self.command.emit('FOLDER_UP')
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        # Use Qt's native context-menu event (on Windows it arrives on mouse
        # release). Do not synthesize a click or select a row in Launch.
        if self._list_is_active():
            self.command.emit('REMOTE_CURRENT_FOLDER_MENU')
        event.accept()


class LaunchRemote(QWidget):
    command = Signal(str)
    header_pressed = Signal()
    more_menu_opening = Signal()
    page_clicked = Signal(str)
    files_exp_folder_selected = Signal(str)
    files_exp_pc_selected = Signal()
    files_exp_folder_context = Signal(str, QPoint)
    files_exp_folder_renamed = Signal(str, str)
    virtual_item_activated = Signal(object)
    virtual_folder_selected = Signal(object)
    virtual_context_requested = Signal(object, QPoint)
    geometry_changed = Signal()
    remote_hidden = Signal()

    def __init__(self, launcher):
        flags = (Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint |
                 Qt.WindowType.WindowDoesNotAcceptFocus)
        super().__init__(launcher, flags)
        self.launcher = launcher  # WheelPad's auto-shuriken route.
        self.setObjectName('launchRemoteWindow')
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        # Transparent window corners; the antialiased panel is drawn in paintEvent.
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # QSettings owns this experiment, not the user's Launch data JSON.
        settings = getattr(launcher, 'settings', None)
        try:
            saved_opacity = float(settings.value('remote_background_opacity', 0.65)) if settings is not None else 0.65
        except (TypeError, ValueError):
            saved_opacity = 0.65
        self._background_opacity = max(0.25, min(1.0, saved_opacity))
        self._opacity_wheel_angle_remainder = 0
        self._opacity_wheel_pixel_remainder = 0
        self._remote_15_placement = False
        self._window_mode_transition = False

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
        # Shared fixed title-strip height with FRB かなフリック.
        title_frame.setFixedHeight(30)
        head = QHBoxLayout(title_frame)
        head.setContentsMargins(2, 2, 2, 2)
        head.setSpacing(2)
        # The title bar carries the Remote's identity, not another HOME.
        # The actual large HOME lives directly above the WheelPad below.
        self.header_remote_icon = QLabel(title_frame)
        self.header_remote_icon.setObjectName('remoteIdentityIcon')
        self.header_remote_icon.setFixedSize(25, 24)
        self.header_remote_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_remote_icon.setPixmap(remote_compact_icon(
            'remote', theme_family(launcher.color_theme) == 'light').pixmap(22, 22))
        self.header_remote_icon.setToolTip('FRB Remote')
        head.addWidget(self.header_remote_icon)
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
        launcher._wire_hybrid_context_menu(self.more_menu)
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
        self.header_remote_icon.installEventFilter(self._passive_header_drag)

        # Remote Page selector: click opens that Page's compact first column.
        # Its child categories use the existing CascadeMenu hover/search logic.
        self.page_buttons = []
        self.page_column = QVBoxLayout()
        self.page_column.setContentsMargins(0, 0, 0, 0)
        self.page_column.setSpacing(3)
        # Page controls now live beside Launch's Files/Browser tabs.
        # Keep the empty layout as an API-compatible placeholder only.
        self.set_pages(getattr(launcher, 'pages', ()))

        # Separate the three Page launchers from the Files/Browser controls.
        self.page_separator = QFrame(self)
        self.page_separator.setObjectName('remotePageSeparator')
        self.page_separator.setFixedHeight(7)
        self.page_separator.hide()

        # The former Files Exp / Files List buttons are retired.  The hold
        # menu on the ぐりぐり pad is the sole visible Files target selector.
        # Keep only the logical target; changing it must not navigate rows.
        self._files_operating_target = 'directory'
        self.files_exp_panel = None
        self._grid_aligned = False
        self._applying_grid_alignment = False
        self.files_exp_theme = launcher.color_theme
        # Browser remains a distinct workspace action.
        self.browser_button = self._button('Browser', 'Browser画面へ切り替え / 右クリック：ブックマークを展開',
                                           'WORKSPACE_BROWSER', width=172, height=27,
                                           role='workspace', wheel_enabled=True)
        # Browser right-click opens its non-modal searchable bookmarks;
        # native left-click remains WORKSPACE_BROWSER.
        self.browser_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.browser_button.customContextMenuRequested.connect(
            lambda _point: self.command.emit('REMOTE_BROWSER_BOOKMARK_MENU'))
        # Browser gets its own full-width row. It is not a Files target.
        root.addWidget(self.browser_button)
        # Former dedicated history buttons were redundant: both remain in
        # WheelPad's context menu. Use the saved row for a prominent HOME
        # directly above the pad and a keyboard launcher on its right.
        row_quick = QHBoxLayout()
        row_quick.setContentsMargins(0, 0, 0, 0)
        row_quick.setSpacing(2)
        # 1の手 identifies this shuriken BUTTON, not a direction or menu ID.
        # Its 4-action eye marker is authoritative; the release commits what
        # the user saw, rather than re-evaluating the mouse trajectory.
        self.shuriken_button = ShurikenButton(launcher, self, hand_index=1)
        self.shuriken_button.triggered.connect(
            lambda item_id: self.command.emit('SHURIKEN_ITEM:' + item_id))
        row_quick.addWidget(self.shuriken_button)
        self.home_button = self._button('', 'HOME：Files Expの先頭へ',
                                        'HOME', width=68, height=46, role='quick',
                                        wheel_enabled=True)
        self.home_button.setObjectName('remoteLargeHomeButton')
        self.home_button.setIconSize(QSize(34, 34))
        self.home_button.setIcon(browser_navigation_icon(
            'home', theme_family(launcher.color_theme)))
        row_quick.addWidget(self.home_button)
        self.kana_button = self._button('', 'FRB かなフリックをRemoteの下へ表示／非表示',
                                        'REMOTE_KANA_TOGGLE', width=50, height=46,
                                        role='quick', wheel_enabled=True)
        self.kana_button.setObjectName('remoteKanaButton')
        self.kana_button.setIconSize(QSize(31, 31))
        self.kana_button.setIcon(remote_compact_icon(
            'keyboard', theme_family(launcher.color_theme) == 'light'))
        row_quick.addWidget(self.kana_button)
        root.addLayout(row_quick)
        self.pad = WheelPad(self, compact=True)
        # The pad can be reparented into the pointing-rod wrapper; retain the
        # real Launch as the one source of truth for the flick guide theme.
        self.pad.launcher = launcher
        # With the two Files target buttons removed, the ぐりぐり hold menu
        # also offers the path BACK from Browser to Files Exp/List.  The
        # actual REMOTE_TARGET_* dispatcher preserves Files' current row.
        # Native modal confirmations retain sole ownership of input.
        self.pad.target_switch_allowed = lambda: (
            launcher.isVisible() and not launcher.isMinimized()
            and launcher.expanded_view.isVisible()
            and launcher.expanded_view._workspace_mode in ('files', 'browser')
            and getattr(launcher, '_remote_text_dialog', None) is None
            and getattr(launcher, '_remote_confirmation', None) is None)
        self.pad.command.connect(self.command.emit)
        # No old ←/→ buttons: the ぐりぐり alone occupies this center row.
        # The hold selector chooses a COLUMN, never a first/next row.
        # The regular wheel / click / double click on ぐりぐり remain intact.

        row_top = QHBoxLayout()
        row_top.setContentsMargins(0, 0, 0, 0)
        row_top.setSpacing(2)
        self.backtab_button = self._button('BackTab', '前の操作列へ',
                                           'BACKTAB', width=85, height=37, role='tab', wheel_enabled=True)
        self.tab_button = self._button('Tab', '次の操作列へ',
                                       'TAB', width=85, height=37, role='tab', wheel_enabled=True)
        row_top.addWidget(self.backtab_button)
        row_top.addWidget(self.tab_button)
        root.addLayout(row_top)
        root.addWidget(self.pad, 0, Qt.AlignmentFlag.AlignHCenter)
        self._pad_layout_index = root.indexOf(self.pad)
        self._pad_inside_rod = False

        # An independent scroll-only pad immediately below the ぐりぐり pad.
        # Same footprint and centerline. During flight, only the viewport
        # moves. On a real stop, the logical current is handed off without
        # changing the selected filesystem entries.
        self.scroll_pad = ShurikenScrollPad(self)
        # A flight is bound to this exact Files List tree. Switching tabs,
        # opening a dialog or changing the Remote target stops it safely.
        self.scroll_pad.target_provider = launcher.remote_scroll_files_list_target
        self.scroll_pad.auto_target_provider = launcher.auto_shuriken_scroll_files_list_target
        self.scroll_pad.auto_end_callback = lambda: launcher._shuriken_wheel_gate.reset(cooldown=True)
        self.scroll_pad.scroll_requested.connect(launcher.remote_scroll_files_list)
        self.scroll_pad.flight_settled.connect(launcher.remote_scroll_files_list_settle)
        root.addWidget(self.scroll_pad, 0, Qt.AlignmentFlag.AlignHCenter)

        # Visual order while the experiment is ON:
        # BLUE (aim, green pivot directly ABOVE native ぐりぐり) ->
        # current-folder band -> operating-target status.
        # The band stays separate: it is never a blue aiming surface.
        self.pointer_rod = MousePointerRodPad(self)
        root.addWidget(self.pointer_rod)

        self.up_band = UpDoubleClickBand(self)
        self.up_band.command.connect(self.command.emit)
        root.addWidget(self.up_band)

        # Overlay the actual green pivot INSIDE blue without consuming an
        # extra row. Its global center remains the single rod origin.
        self.pointer_rod_origin = MousePointerRodOrigin(self.pointer_rod)
        self.pointer_rod.set_origin_marker(self.pointer_rod_origin)

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

        # The wheel pad emits UP/DOWN, CLICK and DOUBLE_CLICK without synthetic
        # keys. Its hold selector owns Files Exp/List switching; the former
        # target pair and dedicated arrow buttons no longer occupy space.
        self.adjustSize()
        # Keep the window large enough for the intentionally tall tab/history
        # buttons. Their height is fixed on each button, not by the stylesheet.
        self.setMinimumHeight(root.sizeHint().height())

        # Accept the same wheel gesture over *every* Remote surface: empty
        # strips, title/status text, remaining buttons and the central pad.
        # Never install this on a cascade QMenu (it has its own window/scroll).
        self.installEventFilter(self)
        for widget in self.findChildren(QWidget):
            if widget.window() is self:
                widget.installEventFilter(self)
        self.set_files_root_hidden_mode(
            bool(getattr(launcher, 'files_root_hidden_mode', False)))
        self.set_mouse_pointer_rod_windows_mode(
            bool(getattr(launcher, 'mouse_pointer_rod_windows_mode', False)))
        self.set_mouse_pointer_rod_enabled(
            bool(getattr(launcher, 'mouse_pointer_rod_mode', False)))
        self.set_mouse_pointer_rod_smart_mode(
            bool(getattr(launcher, 'mouse_pointer_rod_smart_mode', False)))

    def moveEvent(self, event):
        super().moveEvent(event)
        rod = getattr(self, 'pointer_rod', None)
        if rod is not None:
            rod.refresh_position()
        self.geometry_changed.emit()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rod = getattr(self, 'pointer_rod', None)
        if rod is not None:
            # Let the layout settle before recomputing the pad anchor.
            QTimer.singleShot(0, rod.refresh_position)
        # When the rod mode changes Remote height, keep its bottom anchored
        # in column 1.5 instead of leaving the green origin floating up.
        launcher = self.parent()
        if getattr(launcher, 'remote_15_mode', False):
            QTimer.singleShot(0, launcher.queue_remote_15_alignment)
        self.geometry_changed.emit()

    def hideEvent(self, event):
        super().hideEvent(event)
        # setWindowFlags() temporarily hides the native Remote window.
        # This is not a user close and must not dismiss its kana companion.
        if not self._window_mode_transition:
            self.remote_hidden.emit()

    def set_mouse_pointer_rod_windows_mode(self, enabled):
        """Select the OS click adapter without altering rod aim or other buttons."""
        self.pointer_rod.set_windows_click_mode(enabled)

    def set_mouse_pointer_rod_smart_mode(self, enabled):
        """Keep click adapters untouched; opt in to vertical tip tracking."""
        self.pointer_rod.set_smart_mode(enabled)

    def set_mouse_pointer_rod_enabled(self, enabled):
        """Embed/restore the one native ぐりぐり button without changing its duties."""
        enabled = bool(enabled)
        self.pad._hide_target_menu()
        self.pad._pressed = False
        self.pad._drag_start_pos = None
        self.pad._dragged = False
        self.pad._ignore_double_release = False
        root = self.layout()
        if enabled and not self._pad_inside_rod:
            root.removeWidget(self.pad)
            self.pad.setParent(self.pointer_rod)
            self.pointer_rod.set_wheel_pad(self.pad)
            self.pad.show()
            self._pad_inside_rod = True
        elif not enabled and self._pad_inside_rod:
            self.pointer_rod.set_wheel_pad(None)
            self.pad.hide()
            self.pad.setParent(self)
            root.insertWidget(self._pad_layout_index, self.pad, 0,
                              Qt.AlignmentFlag.AlignHCenter)
            self.pad.show()
            self._pad_inside_rod = False
        origin = getattr(self, 'pointer_rod_origin', None)
        if origin is not None:
            origin.setVisible(enabled)
        self.pointer_rod.set_mode_enabled(enabled)
        self.pad.setToolTip(
            'ホイールで選択／クリック・ダブルクリック／長押し→左右へシュッでExp列・List列を選択／右クリックでメニュー')
        self.setMinimumHeight(0)
        root.activate()
        self.adjustSize()
        self.setMinimumHeight(root.sizeHint().height())
        if enabled:
            QTimer.singleShot(0, self._clamp_pointer_rod_to_screen)
            QTimer.singleShot(0, self.pointer_rod.refresh_position)

    def _clamp_pointer_rod_to_screen(self):
        if not self.isVisible() or getattr(self, '_grid_aligned', False):
            return  # Files grid alignment manages its own remote position.
        screen = QApplication.screenAt(self.frameGeometry().center()) or QApplication.primaryScreen()
        if screen is None:
            return
        rect = screen.availableGeometry()
        x = max(rect.left(), min(self.x(), rect.right() - self.width() + 1))
        y = max(rect.top(), min(self.y(), rect.bottom() - self.height() + 1))
        if x != self.x() or y != self.y():
            self.move(x, y)

    def set_kana_visible(self, visible: bool):
        self.kana_button.setProperty('active', bool(visible))
        self.kana_button.style().unpolish(self.kana_button)
        self.kana_button.style().polish(self.kana_button)
        # Kana and Remote are native owner-linked tools. Never promote either
        # to topmost merely because the keyboard is open: Chrome or another
        # foreground app must be able to cover the entire Launch group.

    def sync_window_mode(self):
        """Use the same outside-click policy as the main Launch window."""
        launcher = self.parent()
        auto_dismiss = bool(getattr(launcher, 'dismiss_on_outside_click', True))
        flags = (Qt.WindowType.FramelessWindowHint |
                 Qt.WindowType.WindowDoesNotAcceptFocus |
                 (Qt.WindowType.Tool if auto_dismiss else Qt.WindowType.Window) |
                 (Qt.WindowType.WindowStaysOnTopHint
                  if auto_dismiss else Qt.WindowType(0)))
        if self.windowFlags() == flags:
            return
        visible, pos = self.isVisible(), self.pos()
        self._window_mode_transition = True
        try:
            self.setWindowFlags(flags)
            self.move(pos)
            if visible:
                self.show()
                self.raise_()  # Never activate: preserve the keyboard's IME focus.
        finally:
            self._window_mode_transition = False

    def set_files_root_hidden_mode(self, enabled):
        """Remove both obsolete column switch controls in single-column mode."""
        self.backtab_button.setVisible(not enabled)
        self.tab_button.setVisible(not enabled)
        # Adjust frameless Remote size to avoid a blank former TAB row.
        self.setMinimumHeight(0)
        self.layout().activate()
        self.adjustSize()
        self.setMinimumHeight(self.layout().sizeHint().height())

    def hideEvent(self, event):
        # Preserve the last actual position even when CLOSE is pressed.
        settings = getattr(self.parent(), 'settings', None)
        if (settings is not None and not self._remote_15_placement
                and self.pos().x() >= -32000):
            settings.setValue('remote_last_position', self.pos())
            settings.sync()
        # The experimental tool window must not outlive a dismissed Remote.
        panel = getattr(self, 'files_exp_panel', None)
        if panel is not None:
            panel.hide()
        self.up_band._single_click_timer.stop()
        # A pending single-click must not reopen history after Remote closes.
        timer = getattr(self, 'search_history_click_timer', None)
        if timer is not None:
            timer.stop()
        rod = getattr(self, 'pointer_rod', None)
        if rod is not None:
            # A dismissed Remote cancels pending hover and accent timers as
            # well as hiding the painted overlay. No spontaneous reappearance.
            rod._stop_aiming()
            rod.hide_overlay()
        super().hideEvent(event)

    def toggle_files_exp(self):
        launcher = self.parent()
        if getattr(launcher, 'files_exp_embedded_mode', False):
            # The same tree lives in Launch column 1; no duplicate Tool window.
            view = launcher.expanded_view
            if view.isVisible():
                view.show_files_view()
                view.embedded_files_exp.tree.setFocus(Qt.FocusReason.OtherFocusReason)
            return

        """Show/hide the registered-folder tree while retaining the Files view."""
        if self.files_exp_panel is None:
            self.files_exp_panel = RemoteFilesExplorer(self, self.files_exp_theme)
            self.files_exp_panel.folder_selected.connect(self.files_exp_folder_selected.emit)
            pc_signal = getattr(self.files_exp_panel, 'pc_selected', None)
            if pc_signal is not None:
                pc_signal.connect(self.files_exp_pc_selected.emit)
            self.files_exp_panel.folder_context_requested.connect(self.files_exp_folder_context.emit)
            self.files_exp_panel.folder_renamed.connect(self.files_exp_folder_renamed.emit)
            if hasattr(self.files_exp_panel, 'virtual_item_activated'):
                self.files_exp_panel.virtual_item_activated.connect(self.virtual_item_activated.emit)
            self.files_exp_panel.virtual_folder_selected.connect(self.virtual_folder_selected.emit)
            if hasattr(self.files_exp_panel, 'virtual_context_requested'):
                self.files_exp_panel.virtual_context_requested.connect(self.virtual_context_requested.emit)
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
        # Reopen the *previous* Exp tree, not a brand-new tree based solely on
        # the Launch breadcrumb. Never emit navigation while restoring state.
        restore_state = getattr(panel, 'restore_previous_tree_state', None)
        restored = bool(restore_state()) if callable(restore_state) else False
        self.position_files_exp()
        panel.show()
        panel.raise_()
        if launcher is not None and not restored:
            # First launch, or a selected folder was removed since last use:
            # use the already valid Launch breadcrumb as a safe fallback.
            view = getattr(launcher, 'expanded_view', None)
            if view is not None and view.current_directory():
                panel.sync_current_directory(view.current_directory())
                sync_root = getattr(launcher, 'sync_files_first_column_root', None)
                if callable(sync_root):
                    sync_root(view.current_directory())
        # Scrollbar ranges are established after show(), not while hidden.
        restore_scroll = getattr(panel, 'finish_restoring_tree_scroll', None)
        if callable(restore_scroll):
            QTimer.singleShot(0, restore_scroll)
        # Frameless Tool windows may be placed by Windows on first show.
        # Reassert the Remote-relative anchor after native show processing.
        QTimer.singleShot(0, self.position_files_exp)

    def position_files_exp(self):
        """Preserve grid alignment, or the legacy Remote-relative placement."""
        panel = getattr(self, 'files_exp_panel', None)
        if panel is None:
            return
        if getattr(self, '_grid_aligned', False):
            return  # Resizes/Qt show events must not undo the deliberate layout.
        if getattr(panel, '_manual_position', False) and getattr(
                self.parent(), 'files_root_hidden_mode', False):
            return  # An explicitly moved Exp is independent from Remote drag.
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
            if hasattr(panel, 'place_automatically'):
                panel.place_automatically(x, y)
            else:
                panel.move(x, y)  # Compatible with old Exp test doubles.

    def align_with_files_grid(self):
        """Desktop summons only: align companion windows to the real Files grid.

        Uses the rendered header's *global* Y and Launch's actual exterior
        edges.  Manual Exp location and height overrides win over defaults.
        """
        launcher = self.parent()
        panel = getattr(self, 'files_exp_panel', None)
        view = getattr(launcher, 'expanded_view', None)
        if (panel is None or view is None or not self.isVisible()
                or not panel.isVisible()
                or not getattr(launcher, 'files_root_hidden_mode', False)
                or not view.isVisible() or view._workspace_mode != 'files'):
            return False
        header = view.middle.tree.header()
        top = header.mapToGlobal(QPoint(0, 0)).y()
        launch = launcher.frameGeometry()
        screen = (QApplication.screenAt(header.mapToGlobal(QPoint(0, 0)))
                  or QApplication.screenAt(launch.center())
                  or QApplication.primaryScreen())
        if screen is None:
            return False
        area = screen.availableGeometry()
        rx, ry, ex, ey, h = files_grid_layout(
            launch.left(), launch.right() + 1, top, launch.bottom() + 1,
            self.width(), panel.width(), area.left(), area.right() + 1,
            area.top(), area.bottom() + 1)
        panel._grid_height_mode = True
        manual = panel.saved_manual_position()
        if manual is not None:
            # Monitor configuration may have changed since last save.  The
            # eventual auto-fitted height (not the old saved height) determines
            # the vertical clamp.
            planned_height = panel.height() if panel._manual_height else h
            ex = max(area.left(), min(manual.x(), area.right() - panel.width() + 1))
            ey = max(area.top(), min(manual.y(), area.bottom() - planned_height + 1))
            if not panel._manual_height:
                h = max(180, min(launch.bottom() + 1 - ey,
                                 area.bottom() + 1 - ey))
            rx, ry = remote_next_to_exp(
                ex, ey, panel.width(), self.width(), area.left(),
                area.right() + 1, area.top(), area.bottom() + 1,
                self.height())
        self._applying_grid_alignment = True
        try:
            panel.place_automatically(ex, ey, h)
            self.move(rx, ry)
            self._grid_aligned = True
        finally:
            self._applying_grid_alignment = False
        return True

    def leave_files_grid_alignment(self):
        """Restore pre-experiment Remote/Exp coupling and user saved height."""
        self._grid_aligned = False
        panel = getattr(self, 'files_exp_panel', None)
        if panel is None:
            return
        panel._grid_height_mode = False
        if panel.isVisible():
            settings = getattr(self.parent(), 'settings', None)
            if settings is not None:
                try:
                    height = int(settings.value('remote_files_exp/height', panel.height()))
                    panel.place_automatically(panel.x(), panel.y(),
                                              max(180, min(height, 1400)))
                except (TypeError, ValueError):
                    pass
            self.position_files_exp()

    def moveEvent(self, event):
        super().moveEvent(event)
        # This is the effective moveEvent (overrides the earlier definition).
        rod = getattr(self, 'pointer_rod', None)
        if rod is not None:
            rod.refresh_position()
        if self._applying_grid_alignment:
            return
        # Deliberate Remote drag ends the grid layout for this open session;
        # next desktop summons re-applies it unless Exp was user-positioned.
        self._grid_aligned = False
        panel = getattr(self, 'files_exp_panel', None)
        if panel is not None and panel.isVisible():
            self.position_files_exp()

    def focus_cursor_on_files_exp(self):
        """Desktop summons the Remote with the pointer on the central ぐりぐり.

        Keep this public method name for callers of the older Remote; the
        deleted Files Exp button is no longer a valid pointer destination.
        """
        launcher = self.parent()
        if not getattr(launcher, 'pointer_warp_enabled', True):
            return
        if not self.isVisible():
            return
        from PySide6.QtGui import QCursor
        QCursor.setPos(self.pad.mapToGlobal(self.pad.rect().center()))

    def eventFilter(self, obj, event):
        if (event.type() == QEvent.Type.Wheel
                and (obj is self or (isinstance(obj, QWidget) and obj.window() is self))):
            if (getattr(self, '_files_operating_target', None) == 'files_exp'
                    and (obj is self.up_band or obj is self.up_band._caption)):
                event.accept()  # List-only blank band's wheel is also inert in Exp.
                return True
            if self.adjust_background_opacity_from_wheel(event):
                return True
            # Wheel events have ONE spatial owner. Blue background controls
            # rod length; embedded central button and every other Remote
            # surface retain the existing ぐりぐり navigation behavior.
            if obj is getattr(self, 'pointer_rod', None):
                return False  # Let MousePointerRodPad.wheelEvent handle it.
            if hasattr(self, 'pad'):
                self.pad.wheelEvent(event)
                return True
        return super().eventFilter(obj, event)

    def adjust_background_opacity_from_wheel(self, event):
        """Ctrl+wheel anywhere on Remote adjusts painted backgrounds only.

        Text, icons, and the main Launch window remain fully opaque.  Fractional
        wheel deltas accumulate; Ctrl+wheel must never navigate Files rows.
        """
        if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            return False
        angle = event.angleDelta().y()
        if angle:
            self._opacity_wheel_angle_remainder += angle
            steps = int(self._opacity_wheel_angle_remainder / 120)
            self._opacity_wheel_angle_remainder -= steps * 120
        else:
            self._opacity_wheel_pixel_remainder += event.pixelDelta().y()
            steps = int(self._opacity_wheel_pixel_remainder / 36)
            self._opacity_wheel_pixel_remainder -= steps * 36
        if steps:
            value = self._background_opacity + max(-5, min(5, steps)) * 0.05
            self.set_background_opacity(value)
        event.accept()
        return True

    def set_background_opacity(self, value):
        """Persist the uniform Remote panel/button fill opacity (25..100%)."""
        try:
            value = float(value)
        except (ValueError, TypeError):
            return
        if not 0.25 <= value <= 1.0:
            value = max(0.25, min(1.0, value))
        value = round(value, 2)
        if value == self._background_opacity:
            return
        self._background_opacity = value
        settings = getattr(self.parent(), 'settings', None)
        if settings is not None:
            settings.setValue('remote_background_opacity', value)
            settings.sync()
        self.apply_theme(self.files_exp_theme)
        # Only Ctrl+wheel displays this hint; no permanent extra UI row.
        from PySide6.QtGui import QCursor
        from PySide6.QtWidgets import QToolTip
        QToolTip.showText(QCursor.pos(), f'リモコン背景の不透明度：{int(value * 100)}%', self)

    def _background_css(self, value):
        """Qt stylesheet RGBA: alpha is applied to fills, not to glyphs."""
        color = QColor(value)
        return f'rgba({color.red()},{color.green()},{color.blue()},{round(self._background_opacity * 255)})'

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
        # An already-open flick guide must follow theme changes immediately.
        for control, attribute in ((getattr(self, 'shuriken_button', None), '_preview'),
                                   (getattr(self, 'pad', None), '_target_preview')):
            preview = getattr(control, attribute, None)
            if preview is not None:
                preview.set_theme(theme)
        rod = getattr(self, 'pointer_rod', None)
        if rod is not None:
            rod.set_theme(theme_family(theme))
        panel = getattr(self, 'files_exp_panel', None)
        if panel is not None:
            panel.apply_theme(theme)
        c = theme_palette(theme)
        # The initial theme is applied before the header button exists.
        # On subsequent theme changes refresh the shared vector icon too.
        if hasattr(self, 'home_button'):
            light_mode = theme_family(theme) == 'light'
            self.home_button.setIcon(browser_navigation_icon('home', theme_family(theme)))
            self.kana_button.setIcon(remote_compact_icon('keyboard', light_mode))
            self.header_remote_icon.setPixmap(remote_compact_icon('remote', light_mode).pixmap(22, 22))
        if hasattr(self, 'more_new_tab_action'):
            self.more_new_tab_action.setIcon(browser_navigation_icon(
                'plus', theme_family(theme)))
        self._remote_background = QColor(c['panel'])
        self._remote_background.setAlphaF(self._background_opacity)
        self._remote_outline = QColor('#ccd3d7')  # subtle light-grey, 1px
        self._remote_outline.setAlphaF(self._background_opacity)
        header_bg = self._background_css(c['header'])
        subheader_bg = self._background_css(c['subheader'])
        button_bg = self._background_css(c['panel_header'])
        active_bg = self._background_css(c['selection'])
        hover_bg = self._background_css(c['hover'])
        self.setStyleSheet(f"""
            QWidget#launchRemoteWindow {{ background:transparent; border:0; }}
            QFrame#remoteTitleBar {{background:{header_bg};
                border:1px solid {c['panel_border']};border-radius:5px;}}
            QFrame#remoteStatusBar {{background:{subheader_bg};
                border:1px solid {c['panel_border']};border-radius:4px;}}
            QFrame#remotePageSeparator {{background:transparent;border:0;
                border-top:1px solid {c['panel_border']};margin:3px 2px 0 2px;}}
            QPushButton {{background:{button_bg};color:{c['text']};
                border:1px solid {c['panel_border']};border-radius:5px;
                font-size:12px;padding:0 4px;}}
            QPushButton[role="small"] {{font-size:12px;padding:0 2px;}}
            QPushButton[role="tab"] {{font-size:12px;}}
            QPushButton[role="workspace"] {{font-size:12px;}}
            QPushButton[role="page"] {{text-align:left;padding-left:10px;font-size:12px;}}
            QPushButton[role="workspace"][active="true"] {{background:{active_bg};
                border:1px solid {c['focus_outline']};}}
            QPushButton[role="icon"] {{font-size:12px;padding:0;}}
            QPushButton#remoteLargeHomeButton {{border-radius:7px;padding:0;}}
            QPushButton#remoteShurikenButton {{border-radius:7px;padding:0;}}
            QPushButton#remoteKanaButton {{border-radius:7px;padding:0;}}
            QPushButton#remoteKanaButton[active="true"] {{background:{active_bg};
                border:2px solid {c['focus_outline']};}}
            QPushButton:hover {{background:{hover_bg};}}
            QPushButton:pressed {{background:{active_bg};}}
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
            QLabel#remoteShurikenScrollLabel {{font-size:9px;font-weight:bold;}}
            QLabel#remoteShurikenScrollGlyph {{font-size:12px;font-weight:bold;}}
            QFrame#remoteShurikenScrollPad {{background:{active_bg};
                border:1px dashed {c['focus_outline']};border-radius:5px;}}
            QFrame#remoteUpDoubleClickBand {{background:transparent;
                border:1px solid #a5adb0;border-radius:4px;}}
            QFrame#remoteUpDoubleClickBand QLabel {{color:{c['muted_text']};font-size:10px;}}
            QFrame#remoteWheelPad {{background:{active_bg};
                border:1px dashed {c['focus_outline']};border-radius:5px;}}
            QFrame#mousePointerRodPad {{background:transparent;border:0;}}
        """)
        self.update()

    def set_pages(self, pages):
        """Page buttons moved to Launch's workspace strip; keep no copies."""
        for button in self.page_buttons:
            self.page_column.removeWidget(button)
            button.deleteLater()
        self.page_buttons = []
        self.adjustSize()

    def set_operating_target(self, target):
        """Only move the Remote's logical target; never navigate a folder."""
        self._files_operating_target = 'files_exp' if target == 'files_exp' else 'directory'
        if self._files_operating_target != 'directory':
            self.up_band._single_click_timer.stop()
        self.set_workspace('files')

    def set_workspace(self, mode):
        self.up_band.set_files_mode(mode == 'files')
        # History remains available through WheelPad context menu.
        # The Files target is shown in the status footer and the ぐりぐり
        # Pokeball selector, not by the removed pair of workspace buttons.
        button = self.browser_button
        active = mode == 'browser'
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
                  'files_exp': 'Files Exp',
                   'files': 'Files第1列', 'directory': 'Files List',
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
        self._remote_15_placement = False
        # An already-visible Remote may have been dragged since its last
        # close; never snap it back to the previous session's saved point.
        if self.isVisible():
            self.raise_()
            return
        # A genuine first run uses the desktop click; all later activations
        # recover the user's last Remote position, independent of Files mode.
        settings = getattr(self.parent(), 'settings', None)
        saved = settings.value('remote_last_position') if settings is not None else None
        point = saved if isinstance(saved, QPoint) else None
        screen = QApplication.screenAt(point) if point is not None else None
        if screen is None:
            screen = QApplication.screenAt(global_point)
        if screen is None:
            screen = QApplication.primaryScreen()
        if screen is None:
            return
        rect = screen.availableGeometry()
        self.layout().activate()
        if point is not None:
            x = max(rect.left(), min(point.x(), rect.right() - self.width() + 1))
            y = max(rect.top(), min(point.y(), rect.bottom() - self.height() + 1))
        else:
            center = self.pad.geometry().center()
            x, y = popup_at_hotspot(global_point.x(), global_point.y(),
                                    self.width(), self.height(),
                                    rect.left(), rect.top(), rect.right() + 1, rect.bottom() + 1,
                                    center.x(), center.y())
        self._grid_aligned = False
        self.move(QPoint(x, y))
        self.show()
        self.raise_()
