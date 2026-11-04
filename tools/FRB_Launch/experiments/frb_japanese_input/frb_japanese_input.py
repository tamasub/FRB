"""FRB 日本語入力 v0.6 — local kana + optional Windows IME bridge.

Independent PySide6 experiment. Mouse selects a key; press, drag, release
inputs one kana. Repeated center taps cycle the pending kana.
The key never moves. External IME input is an explicitly enabled experiment.
"""

from __future__ import annotations

import sys
from dataclasses import replace

from PySide6.QtCore import QPoint, QRect, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QMenu, QPushButton, QVBoxLayout, QWidget,
)

from frb_kana_core import (
    KEY_LAYOUT, KANA_ROWS, SPECIAL_KEYS, MODIFIER_KEY, PUNCTUATION_KEY,
    KanaInputModel, classify_flick, flick_hint,
)
from mini_config import SIZE_PRESETS, DEFAULT_SIZE_INDEX, THRESHOLD_OPTIONS
from ime_bridge import ExternalImeSession, Win32KeyboardSender

ROW_INDEX = {name: i for i, (name, _chars) in enumerate(KANA_ROWS)}




def style_for_size(font_size: int) -> str:
    return f"""
    QWidget#frbWindow {{ background: #1b2228; color: #f4f7f5; }}
    QLabel#header {{ color: #e1f5e9; font-size: 12px; font-weight: bold; }}
    QLabel#status {{ color: #91b6aa; font-size: 9px; }}
    QLineEdit#output {{ color: #f9fdfb; background: #273137;
        border: 1px solid #465a59; border-radius: 6px;
        font-size: 14px; padding: 2px 6px; selection-background-color: #348d75; }}
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


class MiniJapaneseInputWindow(QWidget):
    def __init__(self):
        super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setObjectName("frbWindow")
        self.setWindowTitle("FRB かな v0.6")
        self.model = KanaInputModel()
        self.ime_session = None
        self.ime_sender = None
        self.preset_index = DEFAULT_SIZE_INDEX
        self.threshold_px = SIZE_PRESETS[self.preset_index].threshold
        self._last_operation = ""
        self._build_ui()
        self._apply_size_preset(first=True)
        self._refresh_output()

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
        self.ime_button = self._micro('IME', self._toggle_external_ime, 29, 'imeButton')
        self.ime_button.setCheckable(True)
        self.ime_button.setFixedHeight(18)
        self.ime_button.setToolTip('外部IME送信 実験モード: ON後、サクラエディタ等の入力欄をクリック')
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

        self.output = QLineEdit(self)
        self.output.setObjectName("output")
        self.output.setReadOnly(True)
        self.output.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.output.setPlaceholderText("未確定入力 → Enterで確定")
        self.output.setFixedHeight(29)
        root.addWidget(self.output)

        keyboard = QWidget(self)
        self.keyboard = keyboard
        self.grid = QGridLayout(keyboard)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setHorizontalSpacing(3)
        self.grid.setVerticalSpacing(3)
        self.keys = {}
        self.literal_buttons = []
        for row, names in enumerate(KEY_LAYOUT):
            for col, name in enumerate(names):
                if name in ROW_INDEX or name in SPECIAL_KEYS:
                    key = FlickKanaKey(name, keyboard)
                    key.gesture_started.connect(self._show_guide)
                    key.gesture_updated.connect(self._update_guide)
                    key.gesture_finished.connect(self._finish_gesture)
                    key.gesture_cancelled.connect(self._hide_guide)
                    self.keys[name] = key
                self.grid.addWidget(key, row, col)
                self.grid.setColumnStretch(col, 1)
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
        self.resize(spec.outer_width, spec.outer_height - 27)
        if not first:
            QTimer.singleShot(0, self._fit_outer_frame)

    def _fit_outer_frame(self):
        spec = SIZE_PRESETS[self.preset_index]
        frame = self.frameGeometry()
        client = self.geometry()
        extra_width = max(0, frame.width() - client.width())
        extra_height = max(0, frame.height() - client.height())
        self.setFixedSize(max(165, spec.outer_width - extra_width),
                          max(195, spec.outer_height - extra_height))

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

    def _toggle_external_ime(self):
        enabled = self.ime_button.isChecked()
        if enabled and self.model.has_preedit:
            self.ime_button.setChecked(False)
            self.status.setText('IME ON前に確定↵または全消してください')
            return
        if enabled:
            try:
                sender = Win32KeyboardSender()
                sender.set_noactivate(int(self.winId()), True)
                self.ime_sender = sender
                self.ime_session = ExternalImeSession(sender)
                self.status.setText('IME ON: 送信先の入力欄をクリック')
            except Exception as exc:
                self.ime_button.setChecked(False)
                self.status.setText(f'IME接続不可: {exc}')
        else:
            try:
                if self.ime_session:
                    self.ime_session.reset(cancel_external=True)
                if self.ime_sender:
                    self.ime_sender.set_noactivate(int(self.winId()), False)
                self.status.setText('IME OFF: アプリ内のみ入力')
            except Exception as exc:
                self.status.setText(f'IME OFF: 外部の未確定状態は要確認 ({exc})')
            finally:
                self.ime_session = None
                self.ime_sender = None

    def _sync_external(self, old_model) -> bool:
        if self.ime_session is not None:
            try:
                self.ime_session.sync(self.model.preedit_text)
            except Exception as exc:
                self.model = old_model
                self._refresh_output()
                self.status.setText(f'送信見送り: {exc}')
                return False
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
        if self._sync_external(previous):
            label = '外部IME' if self.ime_session else '未確定'
            self.status.setText(f'{label} {char} / 確定↵')

    def _refresh_output(self):
        self.output.setText(self.model.text)
        self.output.setCursorPosition(len(self.model.text))
        if self.model.has_preedit:
            # 未確定の末尾を見える化。前の文字もEnterまで未確定のまま。
            self.output.setSelection(len(self.model.text) - 1, 1)
        else:
            self.output.deselect()
        self.enter_button.setEnabled(self.model.has_preedit)

    def _commit(self):
        if not self.model.has_preedit:
            self.status.setText('未確定文字なし')
            return
        if self.ime_session is not None:
            try:
                self.ime_session.commit()
            except Exception as exc:
                self.status.setText(f'確定見送り: {exc}')
                return
        self.model.commit()
        self._refresh_output()
        self.status.setText(f'確定 / {len(self.model.text)}字')

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
        if self.ime_session and not self.model.has_preedit:
            self.status.setText('外部IME中: 確定済み文字の削除は送信しません')
            return
        previous = replace(self.model)
        self.model.backspace()
        if self._sync_external(previous):
            self.status.setText('削除')

    def _clear(self):
        if self.ime_session and self.model.has_preedit:
            try:
                self.ime_session.sync('')
            except Exception as exc:
                self.status.setText(f'全消見送り: {exc}')
                return
        self.model.clear()
        self._refresh_output()
        self.status.setText('全消去（外部の確定済み文字は消しません）' if self.ime_session else '全消去')

    def _copy(self):
        # コピーしても未確定文字を勝手に確定しない。
        QApplication.clipboard().setText(self.model.text)
        self.status.setText("コピー完了（未確定状態は維持）")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FRB 日本語入力 v0.6 mini")
    app.setFont(QFont("Yu Gothic UI", 9))
    window = MiniJapaneseInputWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
