"""FRB 日本語入力 v0.0 — 単体実験アプリ（PySide6）。

既存 FRB Launch/FRB Remote のファイルは変更しない。
かな漢字変換も Windows IME への入力送信もしない。
"""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from frb_kana_core import (
    DRAG_THRESHOLD_PX,
    DIRECTIONS,
    KANA_ROWS,
    KanaInputModel,
    WheelStepper,
    classify_flick,
)


CSS = """
QWidget#frbWindow { background: #f6f9f8; color: #17382f; }
QFrame#banner { background: #e7f1ed; border: 1px solid #cadfd5; border-radius: 12px; }
QLabel#title { color: #153f32; font-size: 21px; font-weight: 700; }
QLabel#subTitle { color: #587368; font-size: 12px; }
QLabel#sectionTitle { color: #234b3e; font-size: 13px; font-weight: 700; }
QLabel#hint { color: #637e73; font-size: 11px; }
QLabel#rowName { color: #1a664d; font-size: 18px; font-weight: 700; }
QLabel#charHint { background: #fff; color: #245040; border: 1px solid #d1e1da; border-radius: 10px; font-size: 19px; font-weight: 600; }
QLabel#charHint[highlight="true"] { background: #c4e9d9; color: #0f6045; border: 2px solid #25895f; }
QLabel#charHint[missing="true"] { color: #adbbb5; background: #f2f5f3; border-style: dashed; }
QFrame#flickPad { border: 2px solid #348766; border-radius: 15px; background: #e7f7ef; }
QFrame#flickPad[dragging="true"] { background: #c3e8d3; border: 2px solid #16845b; }
QLabel#padLabel { color: #1b6349; font-size: 17px; font-weight: 700; }
QLabel#padCaption { color: #386c57; font-size: 10px; }
QListWidget#rows { background: white; border: 1px solid #d1e1da; border-radius: 10px; padding: 6px; color: #224b3c; font-size: 16px; }
QListWidget#rows::item { padding: 7px 10px; border-radius: 7px; }
QListWidget#rows::item:selected { background: #c5ead9; color: #125f42; font-weight: 700; }
QTextEdit#output { background: white; border: 1px solid #b9d9ca; border-radius: 10px; color: #193a2f; font-size: 20px; padding: 10px; }
QPushButton { background: white; color: #315549; border: 1px solid #c8dcd2; border-radius: 8px; padding: 9px 13px; font-size: 12px; }
QPushButton:hover { background: #e4f5ec; border-color: #62b28a; }
QPushButton:pressed { background: #c6e9d8; }
QPushButton#copyButton { background: #2b8a63; color: white; border: 1px solid #2b8a63; font-weight: 700; }
QPushButton#copyButton:hover { background: #267652; }
QLabel#status { color: #416858; font-size: 12px; }
"""


class KanaRowsList(QListWidget):
    """リスト上のホイールも同じ五十音行選択にする。"""

    wheel_steps = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stepper = WheelStepper()
        self.setObjectName("rows")
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def wheelEvent(self, event):
        steps = self._stepper.feed(angle=event.angleDelta().y(), pixel=event.pixelDelta().y())
        if steps:
            self.wheel_steps.emit(steps)
        event.accept()


class KanaWheelPad(QFrame):
    """固定位置のぐりぐり。押下始点からのドラッグのみを測る。"""

    wheel_steps = Signal(int)
    chosen = Signal(str)
    preview = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("flickPad")
        self.setProperty("dragging", False)
        self.setFixedSize(154, 105)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("ぐりぐりで行選択／クリック＝中央／上下左右へ18px以上ドラッグでフリック")
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setMouseTracking(True)
        self._stepper = WheelStepper()
        self._start = None
        self._drag_direction = "center"
        self._pressed = False
        self._ignore_double_release = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 14, 4, 12)
        layout.setSpacing(4)
        main_label = QLabel("ぐりぐり", self)
        main_label.setObjectName("padLabel")
        main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        caption = QLabel("クリック / 4方向へドラッグ", self)
        caption.setObjectName("padCaption")
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        caption.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(main_label)
        layout.addWidget(caption)

    def _redraw(self):
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _set_drag_state(self, active):
        active = bool(active)
        if self.property("dragging") == active:
            return
        self.setProperty("dragging", active)
        self._redraw()

    def wheelEvent(self, event):
        steps = self._stepper.feed(angle=event.angleDelta().y(), pixel=event.pixelDelta().y())
        if steps:
            self.wheel_steps.emit(steps)
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start = event.position().toPoint()
            self._pressed = True
            self._drag_direction = "center"
            self.preview.emit("center")
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._pressed and self._start is not None:
            dx = event.position().x() - self._start.x()
            dy = event.position().y() - self._start.y()
            direction = classify_flick(dx, dy, DRAG_THRESHOLD_PX)
            if direction != self._drag_direction:
                self._drag_direction = direction
                self.preview.emit(direction or "")
            self._set_drag_state(direction not in ("center", None))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        # 2回目の押下/離上を新しい一文字として扱わない。
        if event.button() == Qt.MouseButton.LeftButton:
            self._ignore_double_release = True
            self._start = None
            self._pressed = False
            self._set_drag_state(False)
            self.preview.emit("")
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._ignore_double_release:
            self._ignore_double_release = False
            self._start = None
            self._pressed = False
            self._set_drag_state(False)
            self.preview.emit("")
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._pressed:
            start = self._start
            self._start = None
            self._pressed = False
            self._set_drag_state(False)
            if start is not None:
                dx = event.position().x() - start.x()
                dy = event.position().y() - start.y()
                direction = classify_flick(dx, dy, DRAG_THRESHOLD_PX)
                # ドラッグならパッド外で離しても入力。通常クリックだけ領域内限定。
                if direction is not None and (direction != "center" or self.rect().contains(event.position().toPoint())):
                    self.chosen.emit(direction)
            self.preview.emit("")
            event.accept()
            return
        super().mouseReleaseEvent(event)


class JapaneseInputWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.model = KanaInputModel()
        self.setObjectName("frbWindow")
        self.setWindowTitle("FRB 日本語入力 v0.0 — ぐりぐり実験室")
        self.setMinimumSize(710, 540)
        self.resize(800, 620)
        self.setStyleSheet(CSS)
        self._gesture_preview = ""
        self._create_ui()
        self._refresh_all()

    def _create_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 15)
        root.setSpacing(12)

        banner = QFrame(self)
        banner.setObjectName("banner")
        bl = QVBoxLayout(banner)
        bl.setContentsMargins(16, 9, 16, 10)
        bl.setSpacing(2)
        title = QLabel("FRB 日本語入力  v0.0", banner)
        title.setObjectName("title")
        sub = QLabel("FRB Remote の子分　｜　かな入力だけを試す独立実験素材", banner)
        sub.setObjectName("subTitle")
        bl.addWidget(title)
        bl.addWidget(sub)
        root.addWidget(banner)

        section = QHBoxLayout()
        section.setSpacing(16)
        rows_col = QVBoxLayout()
        rows_col.setSpacing(6)
        row_title = QLabel("① ぐりぐりで行を選ぶ")
        row_title.setObjectName("sectionTitle")
        rows_col.addWidget(row_title)
        self.rows = KanaRowsList(self)
        for title, _ in KANA_ROWS:
            item = QListWidgetItem(f"{title} 行")
            self.rows.addItem(item)
        self.rows.currentRowChanged.connect(self._on_row_clicked)
        self.rows.wheel_steps.connect(self._on_wheel)
        rows_col.addWidget(self.rows)
        row_hint = QLabel("ホイール下で次の行 / 上で前の行")
        row_hint.setObjectName("hint")
        rows_col.addWidget(row_hint)
        section.addLayout(rows_col, 1)

        pad_col = QVBoxLayout()
        pad_col.setSpacing(8)
        caption = QLabel("② クリック／ドラッグで1文字")
        caption.setObjectName("sectionTitle")
        pad_col.addWidget(caption)
        self.row_name = QLabel()
        self.row_name.setObjectName("rowName")
        self.row_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pad_col.addWidget(self.row_name)

        grid_widget = QWidget(self)
        g = QGridLayout(grid_widget)
        g.setContentsMargins(0, 4, 0, 4)
        g.setSpacing(8)
        self.char_labels = {}
        for direction, r, c in (("up", 0, 1), ("left", 1, 0), ("right", 1, 2), ("down", 2, 1)):
            label = QLabel()
            label.setObjectName("charHint")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setMinimumSize(75, 52)
            label.setProperty("highlight", False)
            self.char_labels[direction] = label
            g.addWidget(label, r, c)
        self.pad = KanaWheelPad(self)
        self.pad.wheel_steps.connect(self._on_wheel)
        self.pad.chosen.connect(self._on_input)
        self.pad.preview.connect(self._on_preview)
        g.addWidget(self.pad, 1, 1)
        g.setColumnStretch(0, 1)
        g.setColumnStretch(2, 1)
        pad_col.addWidget(grid_widget, 1)
        self.center_hint = QLabel()
        self.center_hint.setObjectName("hint")
        self.center_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pad_col.addWidget(self.center_hint)
        section.addLayout(pad_col, 3)
        root.addLayout(section, 1)

        output_title = QLabel("③ 入力結果（このアプリの中だけに表示）")
        output_title.setObjectName("sectionTitle")
        root.addWidget(output_title)
        self.output = QTextEdit(self)
        self.output.setObjectName("output")
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(75)
        self.output.setMaximumHeight(120)
        self.output.setPlaceholderText("ぐりぐりして、1文字入力してみよう！")
        self.output.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        root.addWidget(self.output)

        buttons = QHBoxLayout()
        buttons.setSpacing(9)
        self.back_button = QPushButton("⌫  1文字消す")
        self.back_button.clicked.connect(self._backspace)
        clear_button = QPushButton("全消去")
        clear_button.clicked.connect(self._clear)
        copy_button = QPushButton("文字列をコピー")
        copy_button.setObjectName("copyButton")
        copy_button.clicked.connect(self._copy)
        buttons.addWidget(self.back_button)
        buttons.addWidget(clear_button)
        buttons.addStretch(1)
        buttons.addWidget(copy_button)
        root.addLayout(buttons)

        self.status = QLabel("準備OK：ぐりぐりの上でホイール → 押してドラッグ！")
        self.status.setObjectName("status")
        root.addWidget(self.status)
        last = QLabel("v0.0 は変換・IME連携・他アプリ入力・濁点/小文字変換なし。操作体験だけを検証します。")
        last.setObjectName("hint")
        root.addWidget(last)

    def _on_row_clicked(self, index):
        if index >= 0 and index != self.model.row_index:
            self.model.select(index)
            self._refresh_row()

    def _on_wheel(self, steps):
        self.model.scroll(steps)
        self._refresh_row()
        self.status.setText(f"選択：{KANA_ROWS[self.model.row_index][0]}行")

    def _on_input(self, direction):
        char = self.model.input(direction)
        if char is None:
            self.status.setText("この方向には文字を割り当てていません（入力なし）")
        else:
            self._refresh_text()
            self.status.setText(f"入力：{char}  /  {len(self.model.text)}文字")

    def _on_preview(self, direction):
        self._gesture_preview = direction
        self._refresh_char_labels()

    def _refresh_char_labels(self):
        for direction, label in self.char_labels.items():
            char = KANA_ROWS[self.model.row_index][1][DIRECTIONS.index(direction)]
            arrow = {"up": "↑", "left": "←", "right": "→", "down": "↓"}[direction]
            label.setText(f"{arrow}  {char if char is not None else '—'}")
            label.setProperty("missing", char is None)
            label.setProperty("highlight", direction == self._gesture_preview)
            label.style().unpolish(label)
            label.style().polish(label)
            label.update()
        center = KANA_ROWS[self.model.row_index][1][0]
        self.center_hint.setText(f"中央クリック：{center}　／　フリック判定：{DRAG_THRESHOLD_PX}px以上")

    def _refresh_row(self):
        self.rows.blockSignals(True)
        try:
            self.rows.setCurrentRow(self.model.row_index)
        finally:
            self.rows.blockSignals(False)
        self.row_name.setText(f"{KANA_ROWS[self.model.row_index][0]} 行")
        self._refresh_char_labels()

    def _refresh_text(self):
        self.output.setPlainText(self.model.text)
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output.setTextCursor(cursor)

    def _refresh_all(self):
        self._refresh_row()
        self._refresh_text()

    def _backspace(self):
        self.model.backspace()
        self._refresh_text()
        self.status.setText("末尾の1文字を削除")

    def _clear(self):
        self.model.clear()
        self._refresh_text()
        self.status.setText("入力結果を全消去")

    def _copy(self):
        QApplication.clipboard().setText(self.model.text)
        self.status.setText(f"コピーしました（{len(self.model.text)}文字）")


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("FRB 日本語入力 v0.0")
    app.setFont(QFont("Yu Gothic UI", 10))
    window = JapaneseInputWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
