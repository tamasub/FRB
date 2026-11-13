"""FRB 日本語入力 v0.10 — 4-mode keyboard with bottom IME editor.

Mouse selects a kana key; press, drag and release inputs kana. On Windows,
local IME mode is the default. External app delivery is intentionally deferred.
"""

from __future__ import annotations

import sys
from dataclasses import replace

from PySide6.QtCore import QPoint, QPointF, QRect, QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QPixmap, QIcon
from PySide6.QtWidgets import (
    QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QMenu, QPushButton, QVBoxLayout, QWidget, QSizePolicy,
)

from frb_kana_core import (
    KEY_LAYOUT, KANA_ROWS, SPECIAL_KEYS, MODIFIER_KEY, PUNCTUATION_KEY,
    KanaInputModel, classify_flick, flick_hint,
)
from mini_config import (
    SIZE_PRESETS, DEFAULT_SIZE_INDEX, THRESHOLD_OPTIONS,
    compact_client_height,
)
from ime_bridge import Win32KeyboardSender
from local_ime_bridge import LocalImeSession
from keyboard_modes import (MODES, MODE_LABELS, MODE_COLUMNS, layout_for, request_ime_mode)
from kana_guide_layout import place_guide

ROW_INDEX = {name: i for i, (name, _chars) in enumerate(KANA_ROWS)}




def style_for_size(font_size: int, theme: str = "dark") -> str:
    css = f"""
    QWidget#frbWindow {{ background: transparent; color: #f4f7f5; }}
    QLabel#status {{ color: #91b6aa; font-size: 9px; }}
    QLineEdit#output {{ color: #f9fdfb; background: #273137;
        border: 1px solid #465a59; border-radius: 6px;
        font-size: 14px; padding: 2px 6px; selection-background-color: #348d75; }}
    QPushButton#literalKey {{ color: #f6f9f8; background: #353d46;
        border: 1px solid #4c5861; border-radius: 5px;
        font-size: 13px; font-weight: 600; padding: 0; }}
    QPushButton#literalKey:hover {{ background: #45565e; border-color: #83aaa2; }}
    QPushButton#modeButton {{ color: #dce8e4; background: #303a40;
        border: 1px solid #47585b; border-radius: 4px; font-size: 10px; padding: 0; }}
    QPushButton#modeButton:checked {{ color: #fff; background: #416457;
        border: 1px solid #86bea7; }}
    QPushButton#kanaKey {{ color: #f6f9f8; background: #353d46;
        border: 1px solid #4c5861; border-radius: 6px;
        font-size: {font_size}px; font-weight: 600; padding: 0; }}
    QPushButton#kanaKey:hover {{ background: #45565e; border-color: #83aaa2; }}
    QPushButton#kanaKey[dragActive="true"] {{ background: #3b7460; border: 1px solid #8ad2b5; }}
    QPushButton#specialKey {{ color: #e6ecea; background: #303840;
        border: 1px solid #43525a; border-radius: 6px;
        font-size: {max(10,font_size-9)}px; font-weight: 600; padding: 0; }}
    QPushButton#specialKey:hover {{ background: #45565e; border-color: #83aaa2; }}
    QPushButton#specialKey[dragActive="true"] {{ background: #3b7460; border: 1px solid #8ad2b5; }}
    QPushButton#microButton {{ color: #e3eee8; background: #303a40;
        border: 1px solid #47585b; border-radius: 5px; font-size: 10px; padding: 0 2px; }}
    QPushButton#microButton:hover {{ background: #4c6860; }}
    /* Delete uses a custom-drawn icon, not a platform-dependent glyph. */
    QPushButton#kanaDeleteButton {{ background: #303a40;
        border: 1px solid #47585b; border-radius: 5px;
        padding: 0; }}
    QPushButton#kanaDeleteButton:hover {{ background: #4c6860; }}
    QPushButton#enterButton {{ color: white; background: #2a816b;
        border: 1px solid #62b49a; border-radius: 5px; font-size: 10px; padding: 0; }}
    QPushButton#imeButton {{ color: #d7eddf; background: #303a40;
        border: 1px solid #47585b; border-radius: 4px; font-size: 9px; padding: 0; }}
    QPushButton#imeButton:checked {{ color: #ffffff; background: #416457;
        border: 1px solid #86bea7; }}
    QPushButton#copyButton {{ color: #e3eee8; background: #303a40;
        border: 1px solid #398a75; border-radius: 5px; font-size: 10px; padding: 0 2px; }}
    """
    if theme == 'light':
        palette = {
            '#1b2228': '#edf5f0', '#f4f7f5': '#203e35',
            '#e1f5e9': '#2d6553', '#91b6aa': '#53776a',
            '#f9fdfb': '#213c33', '#273137': '#ffffff',
            '#465a59': '#a9cbb9', '#348d75': '#b9e7d0',
            '#f6f9f8': '#264e40', '#353d46': '#ffffff',
            '#4c5861': '#b8ccc1', '#45565e': '#d8eae0',
            '#83aaa2': '#5c9f82', '#dce8e4': '#305c4c',
            '#303a40': '#f4fbf7', '#47585b': '#b8d0c2',
            '#287c68': '#b9e7d0', '#416457': '#d7ece1',
            '#9bdcc2': '#6bb998', '#86bea7': '#8fc7ab', '#3b7460': '#c8edd8',
            '#8ad2b5': '#519877', '#e6ecea': '#285343',
            '#303840': '#f5fcf8', '#43525a': '#b8ccc1',
            '#e3eee8': '#2d5949', '#4c6860': '#deede4',
            '#2a816b': '#287c68', '#62b49a': '#4e9d82',
            '#d7eddf': '#2d6553', '#327d68': '#b9e7d0',
            '#ffffff': '#ffffff', '#398a75': '#82bda3',
        }
        # Placeholder substitution prevents a color already replaced from
        # accidentally being replaced again by another palette entry.
        tokens = {}
        for i, (old, new) in enumerate(palette.items()):
            token = f'__FRB_COLOR_{i}__'
            css = css.replace(old, token)
            tokens[token] = new
        for token, color in tokens.items():
            css = css.replace(token, color)
        # Avoid white-on-pale active controls in the light theme.
        css = css.replace('QPushButton#modeButton:checked { color: #fff;',
                          'QPushButton#modeButton:checked { color: #164d39;')
        css = css.replace('QPushButton#imeButton:checked { color: #ffffff;',
                          'QPushButton#imeButton:checked { color: #164d39;')
        css = css.replace('QPushButton#enterButton { color: white;',
                          'QPushButton#enterButton { color: #ffffff;')
    # Same title-bar geometry, border and button language as FRB Remote.
    # Keep this self-contained so the standalone keyboard still starts without Launch.
    if theme == 'light':
        header_bg, frame_border, title_ink, control_bg, hover_bg = (
            '#dbe7df', '#bbd8c7', '#233e32', '#eaf6ec', '#ecf7f1')
    else:
        header_bg, frame_border, title_ink, control_bg, hover_bg = (
            '#263532', '#4b6660', '#e6f0eb', '#344a42', '#344d47')
    css += f"""
    QFrame#kanaTitleBar {{ background:{header_bg};
        border:1px solid {frame_border}; border-radius:5px; }}
    QLabel#kanaTitle {{ background:transparent; border:0;
        color:{title_ink}; font-size:10px; font-weight:bold; }}
    QLabel#kanaIdentityIcon {{ background:transparent; border:0; }}
    QPushButton#kanaCloseButton {{ background:{control_bg}; color:{title_ink};
        border:1px solid {frame_border}; border-radius:5px;
        padding:0; font-size:12px; }}
    QPushButton#kanaCloseButton:hover {{ background:{hover_bg}; }}
    """
    return css


def keyboard_title_icon(light: bool) -> QIcon:
    """Draw the same keyboard silhouette used by the Remote launch button."""
    image = QPixmap(64, 64)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    ink = QColor('#24483d' if light else '#e4f6ee')
    painter.setPen(QPen(ink, 3.2))
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


def backspace_button_icon(light: bool) -> QIcon:
    """Draw the requested left-pointing delete tag with an X, independent of fonts.

    The 4x antialiased raster renders clearly even inside the compact 27x18
    toolbar button. The icon does not rely on Windows font glyph coverage.
    """
    scale = 4
    icon_width, icon_height = 22, 16
    image = QPixmap(icon_width * scale, icon_height * scale)
    image.setDevicePixelRatio(scale)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    # Draw in 24x18 reference coordinates; scale to the 22x16 button icon.
    painter.scale(icon_width / 24.0, icon_height / 18.0)

    outline = QPainterPath()
    outline.moveTo(1.5, 8.2)
    outline.lineTo(8.0, 2.5)
    outline.cubicTo(8.8, 1.5, 9.7, 1.1, 10.9, 1.1)
    outline.lineTo(20.6, 1.1)
    outline.cubicTo(22.3, 1.1, 23.2, 2.2, 23.2, 4.0)
    outline.lineTo(23.2, 14.0)
    outline.cubicTo(23.2, 15.8, 22.3, 16.9, 20.6, 16.9)
    outline.lineTo(10.9, 16.9)
    outline.cubicTo(9.7, 16.9, 8.8, 16.5, 8.0, 15.5)
    outline.lineTo(1.5, 9.8)
    outline.cubicTo(1.0, 9.3, 1.0, 8.7, 1.5, 8.2)
    outline.closeSubpath()
    painter.setPen(Qt.PenStyle.NoPen)
    # On the light theme match the supplied charcoal silhouette / white X.
    # On the dark theme use a contrasting fill so the small shape stays legible.
    painter.setBrush(QColor('#454545' if light else '#9bb9aa'))
    painter.drawPath(outline)

    painter.setPen(QPen(QColor('#ffffff' if light else '#263b31'), 3.4,
                        Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
    painter.drawLine(QPointF(12.4, 6.1), QPointF(18.4, 12.1))
    painter.drawLine(QPointF(18.4, 6.1), QPointF(12.4, 12.1))
    painter.end()
    return QIcon(image)


class KanaTitleBar(QFrame):
    """A draggable decorative header; its close button keeps its own clicks."""

    def __init__(self, owner):
        super().__init__(owner)
        self.setObjectName('kanaTitleBar')
        self._owner = owner
        self._drag_origin = None
        self._window_origin = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_origin = event.globalPosition().toPoint()
            self._window_origin = self._owner.pos()
            handle = self._owner.windowHandle()
            if handle is not None and handle.startSystemMove():
                self._drag_origin = None
                self._window_origin = None
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (self._drag_origin is not None and self._window_origin is not None
                and event.buttons() & Qt.MouseButton.LeftButton):
            self._owner.move(self._window_origin + event.globalPosition().toPoint() - self._drag_origin)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._drag_origin is not None:
            self._drag_origin = None
            self._window_origin = None
            event.accept()
            return
        super().mouseReleaseEvent(event)


class FlickGuide(QWidget):
    """Five-way Pokeball guide shown OUTSIDE the keyboard's key hit areas.

    It is a passive Tool window, not a child overlay clipped by the narrow
    FRB kana panel. It neither takes focus from the native IME nor receives
    mouse input. The visible green eye and the pending kana direction agree.
    """

    def __init__(self, parent: QWidget):
        flags = (Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint |
                 Qt.WindowType.WindowDoesNotAcceptFocus |
                 Qt.WindowType.WindowTransparentForInput)
        super().__init__(parent, flags)
        self.setObjectName('kanaPokeballGuide')
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.kana_name = 'あ'
        self.direction = 'center'
        self.light_theme = False
        self.setFixedSize(108, 108)
        self.hide()

    def configure(self, kana_name: str, direction: str | None) -> None:
        self.kana_name = kana_name
        # None denotes a diagonal/cancel gesture. Never show the center eye
        # for a direction that would be cancelled when released.
        self.direction = direction
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
            side = min(self.width(), self.height())
            center = QPointF(self.width() / 2.0, self.height() / 2.0)
            c = center.x()
            radius = side * 0.475
            option_distance = side * 0.325
            marker_radius = side * 0.128

            # Match FRB Remote ShurikenPreview's quieter pastel Pokeball.
            # The same thin strokes and pale fill make the kana guide feel
            # like one member of the Remote UI family instead of a bold badge.
            background = QColor(228, 244, 215, 255)
            border = QColor(154, 196, 119, 210)
            divider = QColor(159, 195, 133, 185)
            text_ink = QColor('#183e33')

            painter.setPen(QPen(border, 1.2))
            painter.setBrush(background)
            painter.drawEllipse(center, radius, radius)

            # Diagonal borders form four cardinal flick sectors, exactly as
            # on the 4-way shuriken; the central click remains a fifth action.
            diagonal = radius / (2.0 ** 0.5)
            painter.setPen(QPen(divider, 1.0))
            painter.drawLine(QPointF(c - diagonal, c - diagonal),
                             QPointF(c + diagonal, c + diagonal))
            painter.drawLine(QPointF(c - diagonal, c + diagonal),
                             QPointF(c + diagonal, c - diagonal))

            painter.setPen(QPen(QColor('#385e56'), 1.2))
            painter.setBrush(QColor('#ffffff'))
            painter.drawEllipse(center, side * 0.178, side * 0.178)

            positions = {
                'center': center,
                'left': QPointF(c - option_distance, c),
                'up': QPointF(c, c - option_distance),
                'right': QPointF(c + option_distance, c),
                'down': QPointF(c, c + option_distance),
            }
            # Draw the marker BEFORE the kana characters. This makes the
            # selected kana legible even when the green eye is beneath it.
            chosen = self.direction
            if chosen in positions and flick_hint(self.kana_name, chosen) is not None:
                painter.setPen(QPen(QColor('#426d59'), 1.0))
                painter.setBrush(QColor('#aed2a0'))
                painter.drawEllipse(positions[chosen], marker_radius, marker_radius)

            font = QFont('Yu Gothic UI')
            font.setPixelSize(max(15, round(side * 0.153)))
            font.setBold(True)
            painter.setFont(font)
            size = 28.0
            for name, position in positions.items():
                char = flick_hint(self.kana_name, name)
                if char is None:
                    continue
                painter.setPen(text_ink)
                rect = QRectF(position.x() - size / 2.0,
                              position.y() - size / 2.0, size, size)
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, char)
        finally:
            # A painter left active makes Qt's backing store fail repeatedly.
            painter.end()


class FlickKanaKey(QPushButton):
    gesture_started = Signal(str, str)
    gesture_updated = Signal(str, object)
    gesture_finished = Signal(str, object)
    gesture_cancelled = Signal()

    def __init__(self, kana_name: str, parent=None):
        super().__init__(kana_name, parent)
        if kana_name not in ROW_INDEX and kana_name not in SPECIAL_KEYS:
            raise ValueError(f"Unknown flick key: {kana_name}")
        self.kana_name = kana_name
        self.threshold_px = 10
        self.setObjectName("specialKey" if kana_name in SPECIAL_KEYS else "kanaKey")
        self.setProperty("dragActive", False)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._press_global = None
        self._pressed = False
        self._direction = "center"

    def _set_drag_active(self, active: bool):
        if self.property("dragActive") == active:
            return
        self.setProperty("dragActive", active)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return
        self._press_global = event.globalPosition()
        self._pressed = True
        self._direction = "center"
        self._set_drag_active(True)
        self.gesture_started.emit(self.kana_name, "center")
        event.accept()

    def _direction_at(self, event):
        if self._press_global is None:
            return None
        delta = event.globalPosition() - self._press_global
        return classify_flick(delta.x(), delta.y(), self.threshold_px)

    def mouseMoveEvent(self, event):
        if self._pressed:
            direction = self._direction_at(event)
            if direction != self._direction:
                self._direction = direction
                self.gesture_updated.emit(self.kana_name, direction)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        # Qt sends mouseDoubleClickEvent instead of mousePressEvent on the
        # second tap. Handle it as another press so あ→い actually works.
        if event.button() == Qt.MouseButton.LeftButton:
            self.mousePressEvent(event)
            return
        super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            super().mouseReleaseEvent(event)
            return
        if self._pressed:
            # Commit the direction already displayed by the green eye.
            # Recomputing from release coordinates could disagree with the
            # guide when the mouse is released slowly or after stopping.
            direction = self._direction
            self._pressed = False
            self._press_global = None
            self._set_drag_active(False)
            if direction == "center" and not self.rect().contains(event.position().toPoint()):
                direction = None
            self.gesture_finished.emit(self.kana_name, direction)
            event.accept()
            return
        super().mouseReleaseEvent(event)


class NativeImeLineEdit(QLineEdit):
    """Keep the real Windows IME composition, without setText during input.

    QLineEdit already supports the Qt platform IME. We only monitor when a
    candidate gets committed so the source gesture history can be reset.
    """
    native_commit_observed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._had_preedit = False
        self._last_preedit = ""

    def inputMethodEvent(self, event):
        text = event.preeditString()
        commit = event.commitString()
        was_composing = self._had_preedit
        super().inputMethodEvent(event)
        self._had_preedit = bool(text)
        self._last_preedit = text
        if was_composing and commit and not text:
            self.native_commit_observed.emit()

    @property
    def is_composing(self):
        return self._had_preedit


class MiniJapaneseInputWindow(QWidget):
    send_requested = Signal(str)
    theme_requested = Signal(str)
    hidden_from_user = Signal()
    layout_size_changed = Signal()

    def __init__(self, parent=None):
        # The keyboard is owned by Remote in Launch mode, so Qt/Windows keep
        # it above its owner without pinning it over unrelated applications.
        # This applies to standalone mode too: a foreground Chrome window must
        # be free to cover the keyboard.
        super().__init__(parent, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.setObjectName("frbWindow")
        self.setWindowTitle("FRB かなフリック")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._panel_fill = QColor('#222e2c')
        self._panel_outline = QColor('#ccd3d7')
        self.model = KanaInputModel()
        self.ime_session = None
        self.ime_sender = None
        self._native_mode = False
        self._updating_from_native = False
        self._commit_in_progress = False
        self.preset_index = DEFAULT_SIZE_INDEX
        self.threshold_px = SIZE_PRESETS[self.preset_index].threshold
        self._last_operation = ""
        self.input_mode = "kana"
        self.shift_armed = False
        self._mode_changing = False
        self.display_theme = 'dark' 
        self._build_ui()
        self._apply_size_preset(first=True)
        self._refresh_output()
        # v0.7 tests the *local* input box, not any outside editor.
        # Enable automatically when Windows is available.
        if sys.platform == "win32":
            QTimer.singleShot(80, self._enable_native_ime_by_default)

    def _micro(self, text: str, handler, width: int | None = None, object_name="microButton") -> QPushButton:
        button = QPushButton(text, self)
        button.setObjectName(object_name)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        if width is not None:
            button.setFixedWidth(width)
        button.clicked.connect(handler)
        return button

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 5, 6, 4)
        root.setSpacing(4)

        # FRB Remote-style identity strip: icon + title + close. No repeated
        # "FRBかな" heading in the keyboard body itself.
        title_frame = KanaTitleBar(self)
        # Do not let the vertical layout stretch the title beyond Remote's 30px.
        title_frame.setFixedHeight(30)
        head = QHBoxLayout(title_frame)
        head.setContentsMargins(2, 2, 2, 2)
        head.setSpacing(2)
        self.header_keyboard_icon = QLabel(title_frame)
        self.header_keyboard_icon.setObjectName('kanaIdentityIcon')
        self.header_keyboard_icon.setFixedSize(25, 24)
        self.header_keyboard_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_keyboard_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.header_keyboard_icon.setToolTip('FRB かなフリック')
        head.addWidget(self.header_keyboard_icon)
        self.header_title = QLabel('FRB かなフリック', title_frame)
        self.header_title.setObjectName('kanaTitle')
        self.header_title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        head.addWidget(self.header_title, 1)
        self.close_button = self._micro('×', self.hide, 22, 'kanaCloseButton')
        self.close_button.setFixedHeight(22)
        self.close_button.setToolTip('閉じる')
        head.addWidget(self.close_button)
        root.addWidget(title_frame)

        # Editing actions move above the keys, so Windows IME candidates
        # opening over the bottom editor cannot hide Delete / Clear.
        # Widths also fit the 174px minimum size preset.
        top = QHBoxLayout()
        top.setSpacing(3)
        self.del_button = self._micro("", self._backspace, 27, 'kanaDeleteButton')
        self.del_button.setIconSize(QSize(22, 16))
        self.del_button.setToolTip("末尾の文字を削除")
        self.clear_button = self._micro("全消", self._clear, 30)
        for button in (self.del_button, self.clear_button):
            button.setFixedHeight(18)
        top.addWidget(self.del_button)
        top.addWidget(self.clear_button)
        # Keep the existing theme, IME and size controls right-aligned.
        top.addStretch(1)
        self.theme_button = self._micro('☀', self._toggle_theme, 20)
        self.theme_button.setFixedHeight(18)
        self.theme_button.setToolTip('ライト／ダークを切り替え')
        top.addWidget(self.theme_button)
        self.ime_button = self._micro('IME', self._toggle_local_ime, 29, 'imeButton')
        self.ime_button.setCheckable(True)
        self.ime_button.setEnabled(False)
        self.ime_button.setFixedHeight(18)
        self.ime_button.setToolTip('ON: この入力欄でWindows IMEの変換候補を表示 / OFF: 従来のかな実験')
        top.addWidget(self.ime_button)
        self.smaller = self._micro("−", lambda: self._change_size(-1), 20)
        self.larger = self._micro("＋", lambda: self._change_size(1), 20)
        self.smaller.setToolTip("キーボードを小さく")
        self.larger.setToolTip("キーボードを大きく")
        self.smaller.setFixedHeight(18)
        self.larger.setFixedHeight(18)
        top.addWidget(self.smaller)
        top.addWidget(self.larger)
        root.addLayout(top)

        mode_strip = QHBoxLayout()
        mode_strip.setSpacing(3)
        self.mode_buttons = {}
        for mode in MODES:
            button = self._micro(MODE_LABELS[mode], lambda checked=False, m=mode: self._select_input_mode(m),
                                 object_name="modeButton")
            button.setCheckable(True)
            button.setChecked(mode == self.input_mode)
            button.setFixedHeight(20)
            mode_strip.addWidget(button, 1)
            self.mode_buttons[mode] = button
        root.addLayout(mode_strip)

        keyboard = QWidget(self)
        self.keyboard = keyboard
        self.grid = QGridLayout(keyboard)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setHorizontalSpacing(3)
        self.grid.setVerticalSpacing(3)
        self.keys = {}
        self.literal_buttons = []
        self._build_keyboard_for_mode()
        root.addWidget(keyboard)
        self.guide = FlickGuide(self)

        actions = QHBoxLayout()
        actions.setSpacing(3)
        self.enter_button = self._micro("確定↵", self._commit, 53, object_name="enterButton")
        self.enter_button.setToolTip("未確定文字列を確定（Enterキーでも可）")
        self.copy_button = self._micro("コピー", self._copy, 32, object_name="copyButton")
        self.send_button = self._micro("送信", self._request_send, 38, object_name="enterButton")
        self.enter_button.setFixedWidth(43)
        actions.addWidget(self.enter_button)
        actions.addWidget(self.copy_button)
        actions.addWidget(self.send_button)
        actions.addStretch(1)
        root.addLayout(actions)
        for button in (self.enter_button, self.copy_button, self.send_button):
            button.setFixedHeight(22)

        footer = QHBoxLayout()
        footer.setSpacing(3)
        self.status = QLabel("クリック / 上下左右フリック", self)
        self.status.setObjectName("status")
        self.status.setMinimumWidth(0)
        footer.addWidget(self.status, 1)
        self.threshold_button = self._micro("10px ▾", self._open_threshold_menu, 53)
        self.threshold_button.setFixedHeight(18)
        self.threshold_button.setToolTip("ドラッグ方向の判定距離を変更")
        footer.addWidget(self.threshold_button)
        root.addLayout(footer)

        # Bottom editor: keep native IME candidates away from the kana keys
        # without inserting a large blank region. The Windows IME decides
        # whether its candidate popup opens below or above the caret.
        self.output = NativeImeLineEdit(self)
        self.output.setObjectName("output")
        self.output.native_commit_observed.connect(self._on_native_ime_committed)
        self.output.textEdited.connect(self._on_native_text_edited)
        self.output.returnPressed.connect(self._on_editor_return_pressed)
        self.output.setReadOnly(True)
        self.output.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.output.setPlaceholderText("入力 → IMEで変換")
        self.output.setFixedHeight(29)
        root.addWidget(self.output)


    def _build_keyboard_for_mode(self):
        """Replace key widgets in the existing grid; preserve the editor and IME."""
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget() is not None:
                child.widget().hide()
                child.widget().deleteLater()
        self.keys = {}
        self.literal_buttons = []
        if self.input_mode == 'kana':
            for row, names in enumerate(KEY_LAYOUT):
                for col, name in enumerate(names):
                    key = FlickKanaKey(name, self.keyboard)
                    key.gesture_started.connect(self._show_guide)
                    key.gesture_updated.connect(self._update_guide)
                    key.gesture_finished.connect(self._finish_gesture)
                    key.gesture_cancelled.connect(self._hide_guide)
                    self.keys[name] = key
                    self.grid.addWidget(key, row, col)
            cols = 3
        else:
            cols = MODE_COLUMNS[self.input_mode]
            for spec in layout_for(self.input_mode):
                if spec.action == 'spacer':
                    continue
                key = QPushButton(spec.label, self.keyboard)
                key.setObjectName('literalKey')
                key.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                key.setMinimumWidth(0)
                key.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                key.clicked.connect(lambda checked=False, k=spec: self._literal_action(k))
                self.literal_buttons.append(key)
                self.grid.addWidget(key, spec.row, spec.col, 1, spec.span)
        for col in range(10):
            self.grid.setColumnStretch(col, 1 if col < cols else 0)

    def _literal_action(self, key):
        """Latin/symbol/number keys insert directly, never via romaji SendInput."""
        if self.input_mode == 'kana':
            return
        if key.action == 'shift':
            self.shift_armed = not self.shift_armed
            self.status.setText('英字: SHIFT ON' if self.shift_armed else '英字: SHIFT OFF')
            return
        if key.action == 'backspace':
            self._backspace()
            return
        if key.action == 'enter':
            self._commit()
            return
        if key.action != 'insert':
            return
        text = key.text
        if self.input_mode == 'latin' and text.isalpha() and self.shift_armed:
            text = text.upper()
            self.shift_armed = False
        if not text:
            return
        if self._native_mode:
            self._ensure_editor_focus()
            # QLineEdit.insert is a direct committed edit, not an IME key event.
            # This also works if Windows IME's global mode is delayed.
            self.output.insert(text)
            self.model = KanaInputModel(text=self.output.text(),
                                        committed_length=len(self.output.text()))
            if self.ime_session is not None:
                self.ime_session.forget()
        else:
            self.model.text += text
            self.model.committed_length = len(self.model.text)
            self._refresh_output()
        self.status.setText(f'{MODE_LABELS[self.input_mode]}: {text}')

    def _set_windows_ime_mode(self, mode: str):
        """Explicit Japanese IME ON / non-kana IME OFF, in our editor only.

        Microsoft IME accepts ImeOn / ImeOff virtual keys. This does not
        install Japanese IME or switch Windows' input language by itself.
        """
        if not self._native_mode or self.ime_sender is None:
            return
        self._ensure_editor_focus()
        request_ime_mode(mode, self.ime_sender, self._editor_is_focused)

    def restore_ime_on_show(self):
        """A fresh kana opening explicitly requests Japanese IME each time.

        The launcher search intentionally uses half-width English. Reopening
        this separate Tool must not inherit that mode. Do not reissue IME
        commands during active composition or when our window lacks focus.
        """
        if (not self.isVisible() or not self._native_mode or
                self.input_mode != 'kana' or self.output.is_composing or
                self.model.has_preedit):
            return
        try:
            if not self.output.hasFocus():
                self._ensure_editor_focus()
            if self._editor_is_focused():
                self._set_windows_ime_mode('kana')
        except Exception as exc:
            self.status.setText(f'日本語IME切替を確認してください ({exc})')

    def _select_input_mode(self, mode: str):
        if mode not in MODES or self._mode_changing:
            return
        if mode == self.input_mode:
            # Clicking the already-selected mode can restore the desired
            # Windows IME state after another app/user changed it.
            try:
                self._set_windows_ime_mode(mode)
            except Exception as exc:
                self.status.setText(f'IME状態の再指定失敗: {exc}')
            return
        # Switching mode is an explicit user action: complete an active kana
        # composition before disabling the Windows IME. Never time-commit.
        if self.input_mode == 'kana' and self.model.has_preedit:
            self._commit()
        self._hide_guide()
        self._mode_changing = True
        try:
            self.input_mode = mode
            self.shift_armed = False
            for name, button in self.mode_buttons.items():
                button.setChecked(name == mode)
            self.ime_button.setChecked(mode == 'kana')
            self.output.setInputMethodHints(Qt.InputMethodHint.ImhNone if mode == 'kana'
                else Qt.InputMethodHint.ImhPreferLatin | Qt.InputMethodHint.ImhNoPredictiveText)
            if self._native_mode:
                self._set_windows_ime_mode(mode)
                self.model = KanaInputModel(text=self.output.text(),
                                            committed_length=len(self.output.text()))
                self.ime_session.forget()
            self._build_keyboard_for_mode()
            self._apply_size_preset()
            self.status.setText(f'{MODE_LABELS[mode]} / Windows IME {"ON" if mode == "kana" else "OFF"} 指示')
        except Exception as exc:
            self.status.setText(f'モード切替: IME操作を確認してください ({exc})')
        finally:
            self._mode_changing = False

    def apply_theme(self, theme: str):
        """Restyle only; never rebuild the IME editor or discard composition."""
        self.display_theme = 'light' if theme == 'light' else 'dark'
        self.theme_button.setText('☾' if self.display_theme == 'light' else '☀')
        self.guide.light_theme = self.display_theme == 'light'
        light = self.display_theme == 'light'
        self._panel_fill = QColor('#fcfffd' if light else '#222e2c')
        self._panel_outline = QColor('#ccd3d7')
        self.header_keyboard_icon.setPixmap(keyboard_title_icon(light).pixmap(20, 20))
        self.del_button.setIcon(backspace_button_icon(light))
        self.setStyleSheet(style_for_size(SIZE_PRESETS[self.preset_index].font_size,
                                          self.display_theme))
        self.guide.update()

    def _toggle_theme(self):
        next_theme = 'dark' if self.display_theme == 'light' else 'light'
        self.apply_theme(next_theme)
        self.theme_requested.emit(next_theme)
        if self._native_mode:
            self._ensure_editor_focus()

    def _request_send(self):
        """Only committed text goes to the explicitly captured destination."""
        if self._native_mode and (self.output.is_composing or self.model.has_preedit):
            self.status.setText('IME変換中です。候補確定↵してから送信')
            return
        value = self.output.text() if self._native_mode else self.model.text
        if not value:
            self.status.setText('送信する文字がありません')
            return
        self.send_requested.emit(value)

    def mark_sent(self, ok: bool, message: str = ''):
        if ok:
            # Do not call _clear() here: it sends an IME ESCAPE keystroke.
            # For an external destination that would cancel/edit the WRONG
            # window immediately after a successful Unicode SendInput.
            self.model.clear()
            if self.ime_session is not None:
                self.ime_session.forget()
            self.output.clear()
            self._refresh_output()
            self.status.setText(message or '送信済み。入力欄をクリア')
        else:
            self.status.setText(message or '送信先が不明です')

    def _change_size(self, offset: int):
        next_index = max(0, min(len(SIZE_PRESETS)-1, self.preset_index + offset))
        if next_index == self.preset_index:
            return
        self.preset_index = next_index
        self.threshold_px = SIZE_PRESETS[next_index].threshold
        self._apply_size_preset()
        self.status.setText(SIZE_PRESETS[next_index].name)

    def _apply_size_preset(self, first=False):
        spec = SIZE_PRESETS[self.preset_index]
        self.apply_theme(self.display_theme)
        for key in (*self.keys.values(), *self.literal_buttons):
            key.setFixedHeight(spec.key_height)
        for key in self.keys.values():
            key.threshold_px = self.threshold_px
        # Large enough to read; this is now a separate passive Tool window,
        # so it is not squeezed into the 200px-wide keyboard panel.
        guide_side = max(108, spec.guide_size + 26)
        self.guide.setFixedSize(guide_side, guide_side)
        self.threshold_button.setText(f"{self.threshold_px}px ▾")
        self.smaller.setEnabled(self.preset_index > 0)
        self.larger.setEnabled(self.preset_index < len(SIZE_PRESETS)-1)
        # A frameless title uses our own 24px header; keep key rows compact.
        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)
        self.resize(self._mode_outer_width(spec), compact_client_height(spec, 0) + 48)
        if not first:
            QTimer.singleShot(0, self._fit_outer_frame)

    def _mode_outer_width(self, spec):
        if self.input_mode in ('latin', 'symbols'):
            return max(330, spec.outer_width + 130)
        if self.input_mode == 'numeric':
            return max(234, spec.outer_width + 34)
        return spec.outer_width

    def _fit_outer_frame(self):
        spec = SIZE_PRESETS[self.preset_index]
        # Frameless Qt Tool has no OS title bar. Reserve an extra compact row
        # for theme / IME / size, while preserving the four flick-key rows.
        self.setFixedSize(max(165, self._mode_outer_width(spec)),
                          compact_client_height(spec, 0) + 48)

    def paintEvent(self, event):
        """Same rounded outer panel/outline geometry as FRB Remote."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setBrush(self._panel_fill)
        painter.setPen(QPen(self._panel_outline, 1))
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), 10, 10)
        painter.end()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._fit_outer_frame)

    def hideEvent(self, event):
        self._hide_guide()
        super().hideEvent(event)
        self.hidden_from_user.emit()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.layout_size_changed.emit()

    def _open_threshold_menu(self):
        menu = QMenu(self)
        for value in THRESHOLD_OPTIONS:
            action = menu.addAction(f"{value} px")
            action.setCheckable(True)
            action.setChecked(value == self.threshold_px)
            action.triggered.connect(lambda checked=False, n=value: self._set_threshold(n))
        menu.exec(self.threshold_button.mapToGlobal(QPoint(0, self.threshold_button.height())))

    def _set_threshold(self, value):
        self.threshold_px = value
        for key in self.keys.values():
            key.threshold_px = value
        self.threshold_button.setText(f"{value}px ▾")
        self.status.setText(f"感度 {value}px")

    def _guide_position(self, key):
        """Anchor the popup to each pressed key at a constant 8px gap.

        mapToGlobal works even if the key is a child of the keyboard grid
        rather than a direct child of the floating tool window. It avoids
        QWidget::mapTo(parent must be in parent hierarchy) warnings.
        """
        key_top = key.mapToGlobal(QPoint(0, 0))
        grid_top = self.keyboard.mapToGlobal(QPoint(0, 0))
        anchor = key.mapToGlobal(key.rect().center())
        screen = QApplication.screenAt(anchor) or QApplication.primaryScreen()
        available = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)
        x, y = place_guide(
            (key_top.x(), key_top.y(), key.width(), key.height()),
            (grid_top.x(), grid_top.y(), self.keyboard.width(), self.keyboard.height()),
            (available.x(), available.y(), available.width(), available.height()),
            (self.guide.width(), self.guide.height()),
        )
        return QPoint(x, y)

    def _show_guide(self, name, direction):
        key = self.keys.get(name)
        if key is None:
            return
        self.guide.configure(name, direction)
        self.guide.move(self._guide_position(key))
        self.guide.show()
        self.guide.raise_()

    def _update_guide(self, name, direction):
        self.guide.configure(name, direction)

    def _hide_guide(self):
        self.guide.hide()

    def _enable_native_ime_by_default(self):
        self.ime_button.setChecked(True)
        self._toggle_local_ime()

    def _toggle_local_ime(self):
        enabled = self.ime_button.isChecked()
        if enabled:
            if self.model.has_preedit:
                self.ime_button.setChecked(False)
                self.status.setText('IME ON前に確定↵または全消してください')
                return
            try:
                sender = Win32KeyboardSender()
                self.ime_sender = sender
                self.output.setReadOnly(False)
                self.output.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                self.output.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
                self.output.setInputMethodHints(Qt.InputMethodHint.ImhNone)
                self.ime_session = LocalImeSession(sender, self._editor_is_focused)
                self._native_mode = True
                self.output.setFocus(Qt.FocusReason.OtherFocusReason)
                self.status.setText('手元IME: この欄で変換 / 外部送信なし')
                self._set_windows_ime_mode(self.input_mode)
            except Exception as exc:
                self.ime_button.setChecked(False)
                self._native_mode = False
                self.ime_session = None
                self.ime_sender = None
                self.output.setReadOnly(True)
                self.output.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                self.status.setText(f'IME利用不可: {exc}')
        else:
            # Don't lose an active native composition by switching to read-only.
            if self._native_mode and self.model.has_preedit:
                self.ime_button.setChecked(True)
                self.status.setText('切替前に「確定↵」または「全消」を押してください')
                return
            if self._native_mode:
                text = self.output.text()
                self.model = KanaInputModel(text=text, committed_length=len(text))
            self._native_mode = False
            self.ime_session = None
            self.ime_sender = None
            self.output.setReadOnly(True)
            self.output.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self._refresh_output()
            self.status.setText('ローカルかな / IME OFF')

    def _editor_is_focused(self) -> bool:
        # Never inject keystrokes if the intended editor has lost focus.
        if not self.output.hasFocus():
            return False
        if not self.isActiveWindow():
            return False
        if self.ime_sender is None:
            return False
        hwnd = self.ime_sender.foreground_window()
        return bool(hwnd and self.ime_sender.is_our_process(hwnd))

    def _ensure_editor_focus(self):
        if self._native_mode and not self.output.hasFocus():
            self.output.setFocus(Qt.FocusReason.OtherFocusReason)

    def _on_editor_return_pressed(self):
        if not self._native_mode:
            return
        # Enter can be pressed on a physical keyboard or sent by the on-screen
        # confirm button. Don't cycle the last kana after a native commit.
        self.model.commit()
        if self.ime_session is not None:
            self.ime_session.forget()
        QTimer.singleShot(0, self._reconcile_native_commit)

    def _on_native_ime_committed(self):
        # Some IMEs commit the preedit when a candidate is clicked. Let the
        # native editor finish processing, then reconcile the gesture history.
        if self._native_mode:
            QTimer.singleShot(0, self._reconcile_native_commit)

    def _on_native_text_edited(self, _text):
        if self._native_mode:
            QTimer.singleShot(0, self._reconcile_native_commit)

    def _reconcile_native_commit(self):
        if not self._native_mode or self._commit_in_progress or self.output.is_composing:
            return
        actual = self.output.text()
        expected = self.model.text
        # During live composition, QLineEdit.text() may omit the preedit.
        # Never treat a shorter prefix as a completed user edit.
        if actual == expected or expected.startswith(actual):
            return
        # A native conversion candidate, or a direct keyboard edit, changed
        # the editor content. The real editor is authoritative at this point.
        self.model = KanaInputModel(text=actual, committed_length=len(actual))
        self.ime_session.forget()
        self.status.setText('IME候補確定 / この欄の文字列を反映')

    def _sync_local_ime(self, old_model) -> bool:
        if self._native_mode:
            try:
                self._ensure_editor_focus()
                self.ime_session.sync(self.model.preedit_text)
                self.enter_button.setEnabled(self.model.has_preedit)
            except Exception as exc:
                self.model = old_model
                self.enter_button.setEnabled(self.model.has_preedit)
                self.status.setText(f'手元IME入力見送り: {exc}')
                return False
            # CRITICAL: NEVER call QLineEdit.setText() while native IME is
            # composing. That would destroy the Windows candidate session.
            return True
        self._refresh_output()
        return True

    def _finish_gesture(self, name, direction):
        self._hide_guide()
        if direction is None:
            self.status.setText('斜めは無効')
            return
        previous = replace(self.model)
        if name in SPECIAL_KEYS:
            char = self.model.special_input(name, direction)
            if char is None:
                self.status.setText('変換対象なし' if name == MODIFIER_KEY else '候補なし')
                return
        else:
            row = ROW_INDEX[name]
            self.model.select(row)
            char = self.model.type_kana(row, direction)
            if char is None:
                self.status.setText('候補なし')
                return
        if self._sync_local_ime(previous):
            label = '手元IME' if self._native_mode else '未確定'
            self.status.setText(f'{label} {char} / 確定↵')

    def _refresh_output(self):
        if self._native_mode:
            # Qt's real IME owns the input line and candidate popup.
            self.enter_button.setEnabled(self.model.has_preedit)
            return
        self.output.setText(self.model.text)
        self.output.setCursorPosition(len(self.model.text))
        if self.model.has_preedit:
            # 未確定の末尾を見える化。前の文字もEnterまで未確定のまま。
            self.output.setSelection(len(self.model.text) - 1, 1)
        else:
            self.output.deselect()
        self.enter_button.setEnabled(self.model.has_preedit)

    def _commit(self):
        if self.input_mode != 'kana':
            self.status.setText('英数字は入力と同時に確定済み')
            return
        if not self.model.has_preedit:
            self.status.setText('未確定文字なし')
            return
        if self._native_mode:
            self._ensure_editor_focus()
            try:
                self._commit_in_progress = True
                self.ime_session.commit()
            except Exception as exc:
                self.status.setText(f'IME確定見送り: {exc}')
                return
            finally:
                self._commit_in_progress = False
        self.model.commit()
        self._refresh_output()
        self.status.setText('確定↵ / IME入力欄' if self._native_mode else f'確定 / {len(self.model.text)}字')

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._commit()
            event.accept()
            return
        if event.key() == Qt.Key.Key_Backspace:
            self._backspace()
            event.accept()
            return
        super().keyPressEvent(event)

    def _backspace(self):
        if self.input_mode != 'kana':
            if self._native_mode:
                self._ensure_editor_focus()
                self.output.backspace()
                text = self.output.text()
                self.model = KanaInputModel(text=text, committed_length=len(text))
                self.ime_session.forget()
            else:
                self.model.backspace()
                self.model.committed_length = len(self.model.text)
                self._refresh_output()
            self.status.setText('1文字削除')
            return
        if self._native_mode and not self.model.has_preedit:
            try:
                self._ensure_editor_focus()
                self.ime_session.backspace_committed()
                # Keep the local gesture history in sync with a committed
                # character deletion; QLineEdit processes SendInput later.
                self.model.backspace()
                self.model.committed_length = len(self.model.text)
                self.status.setText('IME入力欄: 1文字削除')
            except Exception as exc:
                self.status.setText(f'削除見送り: {exc}')
            return
        previous = replace(self.model)
        self.model.backspace()
        if self._sync_local_ime(previous):
            self.status.setText('削除')

    def _clear(self):
        if self._native_mode:
            try:
                self._ensure_editor_focus()
                self.ime_session.cancel()
                QApplication.inputMethod().reset()
                self.ime_session.forget()
                self.output.clear()
            except Exception as exc:
                self.status.setText(f'全消見送り: {exc}')
                return
        self.model.clear()
        self._refresh_output()
        self.status.setText('この欄を全消去' if self._native_mode else '全消去')

    def _copy(self):
        if self._native_mode:
            # QLineEdit.text() may omit the live IME preedit string.
            value = self.output.text() or self.model.text
        else:
            value = self.model.text
        QApplication.clipboard().setText(value)
        self.status.setText('コピー完了 / 変換状態は維持')


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FRB 日本語入力 v0.11 Remote integrated")
    app.setFont(QFont("Yu Gothic UI", 9))
    window = MiniJapaneseInputWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
