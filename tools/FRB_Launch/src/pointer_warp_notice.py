"""Clickable, balloon-style Qt notification for optional OS cursor movement.

QSystemTrayIcon.showMessage() cannot host action buttons or a persistent
"do not show again" control.  This separate non-modal window deliberately
looks like a small toast, without silently enabling pointer movement.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
                               QPushButton, QVBoxLayout, QWidget)


class PointerWarpNotice(QWidget):
    def __init__(self, on_settings, on_dont_show):
        super().__init__(None, (Qt.WindowType.Tool |
                               Qt.WindowType.FramelessWindowHint |
                               Qt.WindowType.WindowStaysOnTopHint))
        self.setObjectName('pointerWarpNotice')
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setWindowTitle('FRB Launch — マウスポインター自動移動')
        self.setFixedWidth(368)
        self.setStyleSheet("""
            QFrame#pointerWarpNoticeCard { background:#f6faf8; border:1px solid #8fb9a6;
                border-radius:12px; }
            QLabel { color:#213b30; background:transparent; border:0; }
            QLabel#pointerWarpNoticeHeading { font-size:13px; font-weight:700; }
            QLabel#pointerWarpNoticeDetails { font-size:12px; }
            QPushButton { border:1px solid #9eb9ab; border-radius:7px;
                background:#ffffff; color:#234b3c; padding:6px 9px; }
            QPushButton#pointerWarpNoticeSettings { background:#27795e;
                color:white; border:1px solid #27795e; font-weight:600; }
            QPushButton:hover { background:#e3f0e9; }
            QPushButton#pointerWarpNoticeSettings:hover { background:#20694f; }
        """)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        card = QFrame(self)
        card.setObjectName('pointerWarpNoticeCard')
        outer.addWidget(card)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(9)
        header = QHBoxLayout()
        heading = QLabel('FRB Launchからのお知らせ', card)
        heading.setObjectName('pointerWarpNoticeHeading')
        header.addWidget(heading)
        header.addStretch(1)
        close = QPushButton('×', card)
        close.setToolTip('今回は閉じる（次回起動時にも案内）')
        close.setFixedSize(25, 25)
        close.clicked.connect(self.close)
        header.addWidget(close)
        layout.addLayout(header)
        message = QLabel('マウスポインター自動移動は現在OFFです。\n'
                         '使いたい場合は、設定 → マウスポインター自動移動 → ON。\n'
                         '仮想環境などではOFFのまま使えます。', card)
        message.setObjectName('pointerWarpNoticeDetails')
        message.setWordWrap(True)
        layout.addWidget(message)
        actions = QHBoxLayout()
        actions.setSpacing(6)
        dont_show = QPushButton('今後表示しない', card)
        dont_show.clicked.connect(lambda checked=False: self._run(on_dont_show))
        actions.addWidget(dont_show)
        later = QPushButton('あとで', card)
        later.clicked.connect(self.close)
        actions.addWidget(later)
        settings = QPushButton('設定を開く', card)
        settings.setObjectName('pointerWarpNoticeSettings')
        settings.clicked.connect(lambda checked=False: self._run(on_settings))
        actions.addWidget(settings)
        layout.addLayout(actions)
        self.adjustSize()

    def _run(self, callback):
        self.close()
        callback()

    def show_near_taskbar(self):
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        if screen is None:
            return
        rect = screen.availableGeometry()
        self.adjustSize()
        margin = 16
        self.move(max(rect.left(), rect.right() - self.width() - margin + 1),
                  max(rect.top(), rect.bottom() - self.height() - margin + 1))
        self.show()
