"""FRB 日本語入力 v0.10 — 4-mode keyboard with bottom IME editor.

Mouse selects a kana key; press, drag and release inputs kana. On Windows,
local IME mode is the default. External app delivery is intentionally deferred.
"""

from __future__ import annotations

import sys
from dataclasses import replace

from PySide6.QtCore import QPoint, QRect, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
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

ROW_INDEX = {name: i for i, (name, _chars) in enumerate(KANA_ROWS)}




def style_for_size(font_size: int) -> str:
    return f"""
    QWidget#frbWindow {{ background: #1b2228; color: #f4f7f5; }}
    QLabel#header {{ color: #e1f5e9; font-size: 12px; font-weight: bold; }}
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
    QPushButton#modeButton:checked {{ color: #fff; background: #287c68;
        border: 1px solid #9bdcc2; }}
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
    QPushButton#enterButton {{ color: white; background: #2a816b;
        border: 1px solid #62b49a; border-radius: 5px; font-size: 10px; padding: 0; }}
    QPushButton#imeButton {{ color: #d7eddf; background: #303a40;
        border: 1px solid #47585b; border-radius: 4px; font-size: 9px; padding: 0; }}
    QPushButton#imeButton:checked {{ color: #ffffff; background: #327d68;
        border: 1px solid #9bdcc2; }}
    QPushButton#copyButton {{ color: #e3eee8; background: #303a40;
        border: 1px solid #398a75; border-radius: 5px; font-size: 10px; padding: 0 2px; }}
    """


class FlickGuide(QWidget):
    """A tiny, partially transparent, mouse-transparent 5-way hint."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.kana_name = "あ"
        self.direction = "center"
        self.setFixedSize(80, 80)
        self.hide()

    def configure(self, kana_name: str, direction: str | None) -> None:
        self.kana_name = kana_name
        self.direction = direction or ""
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        n = self.width()
        c = n / 2.0
        offset = n * 0.245
        positions = {
            "center": (c, c), "left": (c - offset, c),
            "up": (c, c - offset), "right": (c + offset, c),
            "down": (c, c + offset),
        }
        painter.setBrush(QColor(15, 22, 26, 207))
        painter.setPen(QPen(QColor(148, 179, 168, 95), 1))
        painter.drawRoundedRect(2, 2, n-4, n-4, 15, 15)
        font = QFont("Yu Gothic UI", max(10, int(n * 0.14)))
        font.setBold(True)
        painter.setFont(font)
        radius = n * 0.145
        for name, (x, y) in positions.items():
            char = flick_hint(self.kana_name, name)
            if char is None:
                continue
            if name == self.direction:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(113, 213, 169, 235))
                painter.drawEllipse(QPoint(round(x), round(y)), round(radius), round(radius))
                painter.setPen(QColor(10, 35, 26))
            else:
                painter.setPen(QColor(234, 246, 241, 220 if name == "center" else 172))
            d = round(n * 0.19)
            painter.drawText(QRect(round(x)-d, round(y)-d, 2*d, 2*d),
                             Qt.AlignmentFlag.AlignCenter, char)
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
            direction = self._direction_at(event)
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
    def __init__(self):
        super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setObjectName("frbWindow")
        self.setWindowTitle("FRB 日本語入力 v0.10")
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

        top = QHBoxLayout()
        top.setSpacing(3)
        header = QLabel("FRB かな", self)
        header.setObjectName("header")
        top.addWidget(header)
        top.addStretch(1)
        self.ime_button = self._micro('IME', self._toggle_local_ime, 29, 'imeButton')
        self.ime_button.setCheckable(True)
        # IME state is dictated by the selected keyboard mode, not by a
        # competing manual toggle. Keep the compact indicator in the header.
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
        self.del_button = self._micro("⌫", self._backspace, 25)
        self.del_button.setToolTip("末尾の文字を削除")
        self.clear_button = self._micro("全消", self._clear, 32)
        self.enter_button = self._micro("確定↵", self._commit, 53, object_name="enterButton")
        self.enter_button.setToolTip("未確定文字列を確定（Enterキーでも可）")
        self.copy_button = self._micro("コピー", self._copy, 40, object_name="copyButton")
        actions.addWidget(self.del_button)
        actions.addWidget(self.clear_button)
        actions.addWidget(self.enter_button)
        actions.addWidget(self.copy_button)
        actions.addStretch(1)
        root.addLayout(actions)
        for button in (self.del_button, self.clear_button, self.enter_button, self.copy_button):
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
        self.output.setPlaceholderText("FRBかな入力 → IMEで変換")
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
        self.setStyleSheet(style_for_size(spec.font_size))
        for key in (*self.keys.values(), *self.literal_buttons):
            key.setFixedHeight(spec.key_height)
        for key in self.keys.values():
            key.threshold_px = self.threshold_px
        self.guide.setFixedSize(spec.guide_size, spec.guide_size)
        self.threshold_button.setText(f"{self.threshold_px}px ▾")
        self.smaller.setEnabled(self.preset_index > 0)
        self.larger.setEnabled(self.preset_index < len(SIZE_PRESETS)-1)
        # QWidget geometry excludes the OS title bar; adjust after show so
        # the total visible size matches the screenshot of FRB Remote.
        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)
        self.resize(self._mode_outer_width(spec), compact_client_height(spec, 27) + 24)
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
        frame = self.frameGeometry()
        client = self.geometry()
        extra_width = max(0, frame.width() - client.width())
        extra_height = max(0, frame.height() - client.height())
        self.setFixedSize(max(165, self._mode_outer_width(spec) - extra_width),
                          compact_client_height(spec, extra_height) + 24)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._fit_outer_frame)

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
        c = key.mapTo(self, key.rect().center())
        side = self.guide.width()
        x = c.x() - side // 2
        y = c.y() - side // 2 - 11
        x = max(2, min(self.width() - side - 2, x))
        y = max(2, min(self.height() - side - 2, y))
        return QPoint(x, y)

    def _show_guide(self, name, direction):
        self.guide.configure(name, direction)
        self.guide.move(self._guide_position(self.keys[name]))
        self.guide.raise_()
        self.guide.show()

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
    app.setApplicationName("FRB 日本語入力 v0.10 four modes")
    app.setFont(QFont("Yu Gothic UI", 9))
    window = MiniJapaneseInputWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
