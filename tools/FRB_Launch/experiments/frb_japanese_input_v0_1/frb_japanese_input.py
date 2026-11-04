"""FRB 日本語入力 v0.1 — compact mouse-flick experiment.

Standalone PySide6 application. No Windows IME integration, system-wide input,
or FRB Launch changes. Hover a key, press, drag, release to input one kana.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from frb_kana_core import DRAG_THRESHOLD_PX, KEY_LAYOUT, KANA_ROWS, KanaInputModel, classify_flick, get_kana

# The keyboard layout is defined in frb_kana_core.py for easy testing.
ROW_INDEX = {name: index for index, (name, _chars) in enumerate(KANA_ROWS)}

CSS = """
QWidget#frbWindow { background: #1b2026; color: #eef4f2; }
QLabel#header { color: #f2f6f4; font-size: 17px; font-weight: 700; }
QLabel#subTitle { color: #9baeb1; font-size: 11px; }
QLabel#hint { color: #a9b9b8; font-size: 11px; }
QLabel#status { color: #b2d8ca; font-size: 12px; }
QFrame#outputFrame { background: #252e33; border: 1px solid #3e4b4d; border-radius: 12px; }
QLabel#outputTitle { color: #94bcb2; font-size: 11px; }
QPlainTextEdit#output { color: #fbfdfc; border: 0; background: transparent; font-size: 21px; selection-background-color: #398970; }
QPushButton#kanaKey { color: #f6faf9; background: #353c45; border: 1px solid #465058; border-radius: 10px; font-size: 28px; font-weight: 550; padding: 0; }
QPushButton#kanaKey:hover { background: #46535c; border-color: #6b918b; }
QPushButton#kanaKey[dragActive="true"] { background: #356951; border: 2px solid #70cba9; }
QPushButton#utilityKey { color: #e0e8e5; background: #2c333b; border: 1px solid #45515a; border-radius: 9px; font-size: 12px; padding: 8px; }
QPushButton#utilityKey:hover { background: #40515b; }
QPushButton#utilityKey:pressed { background: #355c51; }
QPushButton#copyKey { color: white; background: #257b67; border: 1px solid #338d76; border-radius: 9px; font-size: 12px; font-weight: 650; padding: 8px; }
QPushButton#copyKey:hover { background: #33947b; }
"""


class FlickGuide(QWidget):
    """Compact, mouse-transparent guide. Painted over the selected key."""

    GUIDE_SIZE = 106
    POSITIONS = {
        "center": QPoint(53, 53),
        "left": QPoint(27, 53),
        "up": QPoint(53, 27),
        "right": QPoint(79, 53),
        "down": QPoint(53, 79),
    }

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setFixedSize(self.GUIDE_SIZE, self.GUIDE_SIZE)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.kana_name = "あ"
        self.direction = "center"
        self.hide()

    def configure(self, kana_name: str, direction: str | None) -> None:
        self.kana_name = kana_name
        self.direction = direction or ""
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setBrush(QColor(14, 23, 28, 226))
        painter.setPen(QPen(QColor(160, 188, 187, 116), 1))
        painter.drawEllipse(2, 2, self.width() - 4, self.height() - 4)

        base_font = QFont("Yu Gothic UI", 14)
        base_font.setBold(True)
        painter.setFont(base_font)

        for name, center in self.POSITIONS.items():
            kana = get_kana(ROW_INDEX[self.kana_name], name)
            if kana is None:
                continue
            if name == self.direction:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(104, 205, 162, 225))
                painter.drawEllipse(center, 17, 17)
                painter.setPen(QColor(12, 40, 31))
            else:
                painter.setPen(QColor(232, 244, 240, 212 if name == "center" else 170))
            rect = QRect(center.x() - 16, center.y() - 17, 32, 34)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, kana)
        painter.end()


class FlickKanaKey(QPushButton):
    """A key stays fixed while the pointer displacement chooses a kana."""

    gesture_started = Signal(str, str)
    gesture_updated = Signal(str, object)
    gesture_finished = Signal(str, object)
    gesture_cancelled = Signal()

    def __init__(self, kana_name: str, parent=None):
        super().__init__(kana_name, parent)
        if kana_name not in ROW_INDEX:
            raise ValueError(f"Not a kana row: {kana_name}")
        self.kana_name = kana_name
        self.setObjectName("kanaKey")
        self.setProperty("dragActive", False)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setMinimumHeight(62)
        self.setToolTip("押す→上下左右へドラッグ→離して1文字（動かさなければ中央文字）")
        self._press_global = None
        self._pressed = False
        self._direction = "center"
        self._ignore_double_release = False

    def _set_drag_active(self, active: bool) -> None:
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
        self._ignore_double_release = False
        self._direction = "center"
        self._set_drag_active(True)
        self.gesture_started.emit(self.kana_name, "center")
        event.accept()

    def _direction_at(self, event) -> str | None:
        if self._press_global is None:
            return None
        delta = event.globalPosition() - self._press_global
        return classify_flick(delta.x(), delta.y(), DRAG_THRESHOLD_PX)

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
        if event.button() == Qt.MouseButton.LeftButton:
            self._ignore_double_release = True
            self._pressed = False
            self._press_global = None
            self._set_drag_active(False)
            self.gesture_cancelled.emit()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            super().mouseReleaseEvent(event)
            return
        if self._ignore_double_release:
            self._ignore_double_release = False
            self._set_drag_active(False)
            event.accept()
            return
        if self._pressed:
            direction = self._direction_at(event)
            self._pressed = False
            self._press_global = None
            self._set_drag_active(False)
            # Deliberately allow release outside the original key for a flick,
            # but not for a plain click dragged beyond the key into nowhere.
            if direction == "center" and not self.rect().contains(event.position().toPoint()):
                direction = None
            self.gesture_finished.emit(self.kana_name, direction)
            event.accept()
            return
        super().mouseReleaseEvent(event)


class JapaneseInputWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.model = KanaInputModel()
        self.setObjectName("frbWindow")
        self.setWindowTitle("FRB 日本語入力 v0.1 — フリック実験")
        self.setMinimumSize(366, 505)
        self.resize(395, 535)
        self.setStyleSheet(CSS)
        self._build_ui()
        self._refresh_text()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(15, 13, 15, 12)
        root.setSpacing(10)

        title = QLabel("FRB 日本語入力  v0.1", self)
        title.setObjectName("header")
        root.addWidget(title)
        subtitle = QLabel("キーに移動 → 押す → フリック → 離す", self)
        subtitle.setObjectName("subTitle")
        root.addWidget(subtitle)

        output_frame = QFrame(self)
        output_frame.setObjectName("outputFrame")
        output_layout = QVBoxLayout(output_frame)
        output_layout.setContentsMargins(11, 8, 11, 7)
        output_layout.setSpacing(2)
        output_title = QLabel("入力結果（このアプリ内のみ）", output_frame)
        output_title.setObjectName("outputTitle")
        output_layout.addWidget(output_title)
        self.output = QPlainTextEdit(output_frame)
        self.output.setObjectName("output")
        self.output.setReadOnly(True)
        self.output.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.output.setPlaceholderText("ここにひらがなが入る")
        self.output.setFixedHeight(65)
        output_layout.addWidget(self.output)
        root.addWidget(output_frame)

        keyboard = QWidget(self)
        grid = QGridLayout(keyboard)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(5)
        grid.setVerticalSpacing(6)
        self.keys = {}
        for row, kana_names in enumerate(KEY_LAYOUT):
            for col, name in enumerate(kana_names):
                if name in ROW_INDEX:
                    key = FlickKanaKey(name, keyboard)
                    key.gesture_started.connect(self._show_guide)
                    key.gesture_updated.connect(self._update_guide)
                    key.gesture_finished.connect(self._finish_gesture)
                    key.gesture_cancelled.connect(self._hide_guide)
                    self.keys[name] = key
                else:
                    key = QPushButton(name, keyboard)
                    key.setObjectName("utilityKey")
                    key.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                    key.setMinimumHeight(62)
                    key.clicked.connect(lambda checked=False, character=name: self._append_literal(character))
                grid.addWidget(key, row, col)
                grid.setColumnStretch(col, 1)
        root.addWidget(keyboard)
        self.guide = FlickGuide(self)

        actions = QHBoxLayout()
        actions.setSpacing(6)
        self._action_button(actions, "⌫  1文字削除", self._backspace)
        self._action_button(actions, "全消去", self._clear)
        self._action_button(actions, "コピー", self._copy, name="copyKey")
        root.addLayout(actions)

        self.status = QLabel("どのキーからでも、中央クリック・4方向フリックで入力", self)
        self.status.setObjectName("status")
        self.status.setWordWrap(True)
        root.addWidget(self.status)
        hint = QLabel("18px以上で方向判定・斜めはキャンセル / IME変換なし", self)
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        root.addWidget(hint)
        root.addStretch(1)

    def _action_button(self, layout, text, callback, name="utilityKey"):
        btn = QPushButton(text, self)
        btn.setObjectName(name)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        return btn

    def _guide_position(self, key: FlickKanaKey) -> QPoint:
        # The guide is painted in this window (NOT moved with the key).
        # Float it a little above the pressed key, clamped inside the window.
        key_center = key.mapTo(self, key.rect().center())
        x = key_center.x() - FlickGuide.GUIDE_SIZE // 2
        y = key_center.y() - FlickGuide.GUIDE_SIZE // 2 - 18
        x = max(6, min(self.width() - FlickGuide.GUIDE_SIZE - 6, x))
        y = max(6, min(self.height() - FlickGuide.GUIDE_SIZE - 6, y))
        return QPoint(x, y)

    def _show_guide(self, name: str, direction: str):
        self.guide.configure(name, direction)
        self.guide.move(self._guide_position(self.keys[name]))
        self.guide.raise_()
        self.guide.show()

    def _update_guide(self, name: str, direction: str | None):
        self.guide.configure(name, direction)

    def _hide_guide(self):
        self.guide.hide()

    def _finish_gesture(self, name: str, direction: str | None):
        self._hide_guide()
        if direction is None:
            self.status.setText("斜めのドラッグは入力せずキャンセル")
            return
        self.model.select(ROW_INDEX[name])
        char = self.model.input(direction)
        if char is None:
            self.status.setText("この方向には文字がありません（入力なし）")
            return
        self._refresh_text()
        self.status.setText(f"入力：{char}　／　{len(self.model.text)}文字")

    def _append_literal(self, character: str):
        self.model.text += character
        self._refresh_text()
        self.status.setText(f"入力：{character}　／　{len(self.model.text)}文字")

    def _refresh_text(self):
        self.output.setPlainText(self.model.text)
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output.setTextCursor(cursor)

    def _backspace(self):
        self.model.backspace()
        self._refresh_text()
        self.status.setText("1文字削除")

    def _clear(self):
        self.model.clear()
        self._refresh_text()
        self.status.setText("入力結果を全消去")

    def _copy(self):
        QApplication.clipboard().setText(self.model.text)
        self.status.setText(f"コピー完了（{len(self.model.text)}文字）")


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("FRB 日本語入力 v0.1")
    app.setFont(QFont("Yu Gothic UI", 10))
    window = JapaneseInputWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
