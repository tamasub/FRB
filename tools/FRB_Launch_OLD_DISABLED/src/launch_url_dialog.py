"""One URL registration dialog for both Files Exp and Files List.

This is deliberately just a UI adapter: validation and the saved Open record
come from launch_menu_registration; the Launcher commits through Studio Core.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication, QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QVBoxLayout,
)

from launch_menu_registration import (
    RegistrationError, mime_sources, normalize_sources, url_registration_record,
)


def url_source_from_mime(mime):
    """Pick only real HTTP(S) links from clipboard or Chrome URL drops."""
    try:
        entries = mime_sources(mime)
        # normalize_sources can accept file-system entries too; the URL edit
        # must NEVER accept an arbitrary local file as a web address.
        # Process each entry independently: a native Windows fallback may
        # contain an invalid local path alongside a valid Chromium link.
        for entry in entries:
            try:
                sources = normalize_sources([entry])
                source = next((src for src in sources if src['kind'] == 'url'), None)
                if source is not None:
                    return source
            except (RegistrationError, ValueError, OSError, TypeError):
                continue
    except (RegistrationError, ValueError, OSError, TypeError):
        pass
    return None


class URLDropLineEdit(QLineEdit):
    """Preserve Chrome HTML link names and URL MIME data instead of plain text."""
    url_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setPlaceholderText('https://example.com/...')

    def dragEnterEvent(self, event):
        if url_source_from_mime(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if url_source_from_mime(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        source = url_source_from_mime(event.mimeData())
        if source is None:
            event.ignore()
            return
        self.setText(source['value'])
        self.url_dropped.emit(source['title'])
        event.acceptProposedAction()


class LaunchURLRegistrationDialog(QDialog):
    """Title + URL, clipboard button, external Chrome drop, shared validation."""

    def __init__(self, parent=None, *, current_browser_url=None, field_qss=''):
        super().__init__(parent)
        self.setWindowTitle('URLを追加')
        self.setMinimumWidth(470)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.registration_record = None
        self.current_browser_url = current_browser_url

        layout = QVBoxLayout(self)
        layout.setSpacing(9)
        layout.addWidget(QLabel('タイトル', self))
        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText('登録するメニューの表示名')
        layout.addWidget(self.title_input)
        layout.addWidget(QLabel('URL（http:// または https://）', self))
        url_row = QHBoxLayout()
        self.url_input = URLDropLineEdit(self)
        self.url_input.setToolTip('Chromeのアドレスバーやリンクをここへドロップできます')
        self.url_input.url_dropped.connect(self._apply_suggested_title)
        url_row.addWidget(self.url_input, 1)
        self.fetch_button = QPushButton('URL取得', self)
        self.fetch_button.setToolTip('クリップボードのURLを取得（なければFRB Browserの現在URL）')
        self.fetch_button.clicked.connect(self._fetch_url)
        url_row.addWidget(self.fetch_button)
        layout.addLayout(url_row)
        if field_qss:
            self.title_input.setStyleSheet(field_qss)
            self.url_input.setStyleSheet(field_qss)

        hint = QLabel('URL欄へ直接ドロップできます。Launch本体の登録先へDropしても自動追加できますよ。', self)
        hint.setWordWrap(True)
        layout.addWidget(hint)
        detail = QLabel('URL取得：クリップボードのURL（またはFRB Browserで表示中のURL）を読み込みます。', self)
        detail.setWordWrap(True)
        layout.addWidget(detail)
        self.warning = QLabel('', self)
        self.warning.setStyleSheet('color:#bc5757;')
        self.warning.setWordWrap(True)
        self.warning.hide()
        layout.addWidget(self.warning)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText('追加')
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText('キャンセル')
        self.buttons.accepted.connect(self._validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _apply_suggested_title(self, title):
        if not self.title_input.text().strip() and title:
            self.title_input.setText(title)

    def _fetch_url(self):
        source = url_source_from_mime(QApplication.clipboard().mimeData())
        if source is None and callable(self.current_browser_url):
            candidate = str(self.current_browser_url() or '').strip()
            try:
                sources = normalize_sources([{'value': candidate}])
                source = next((src for src in sources if src['kind'] == 'url'), None)
            except (RegistrationError, ValueError, OSError):
                source = None
        if source is None:
            self._warn('URLが見つかりません。ブラウザのURLをコピーするか、URL欄へドロップしてください。')
            return
        self.warning.hide()
        self.url_input.setText(source['value'])
        self._apply_suggested_title(source['title'])

    def _warn(self, message):
        self.warning.setText(message)
        self.warning.show()

    def _validate_and_accept(self):
        try:
            self.registration_record = url_registration_record(
                self.title_input.text(), self.url_input.text())
        except RegistrationError as exc:
            self._warn(str(exc))
            return
        self.accept()
