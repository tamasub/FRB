"""FRB kana as a small, independently focusable companion BELOW FRB Remote.

The Remote never takes text focus. The keyboard must take focus for native
Windows IME composition. Sending is an explicit action to a captured target.
"""
from __future__ import annotations

from pathlib import Path
import sys

from PySide6.QtCore import QPoint, QTimer, Qt
from PySide6.QtWidgets import QApplication

from remote_kana_target import RemoteKanaTarget, widget_is_text_target


class RemoteKanaIntegration:
    def __init__(self, launcher):
        self.launcher = launcher
        self.window = None
        self.target = None
        self._focus_tracking_connected = False

    def _on_focus_changed(self, old, new):
        """Follow a deliberately focused Launch input without closing FRBかな.

        Ignore the keyboard's own IME editor: it is never a Send destination.
        A plain click on a non-editor is not interpreted as an input target.
        """
        if self.window is None or not self.window.isVisible():
            return
        if (self.target is not None and self.target.widget_ref is not None and
                self.target.widget_ref() is old):
            self.target.remember_selection()
        if (new is None or self.window is new or self.window.isAncestorOf(new)
                or not widget_is_text_target(new)):
            return
        if (self.target is not None and self.target.widget_ref is not None and
                self.target.widget_ref() is new):
            return
        if self.target is not None:
            self.target.release_inline_editor()
        self.target = RemoteKanaTarget.from_widget(new)
        self.window.send_button.setToolTip('送信先: ' + self.target.label)

    def _create_window(self):
        if self.window is not None:
            return self.window
        # In development use the source tree; in PyInstaller the experiment
        # .py files are included in _MEIPASS as trusted package data.
        root = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent))
        path = root / 'experiments' / 'frb_japanese_input'
        if not (path / 'frb_japanese_input.py').is_file():
            raise FileNotFoundError(f'FRB かなフリック実験ファイルが見つかりません: {path}')
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
        from frb_japanese_input import MiniJapaneseInputWindow
        # Native owner: Remote and kana share an ordered desktop window group.
        self.window = MiniJapaneseInputWindow(parent=self.launcher.remote_window)
        self.window.setWindowTitle('FRB かなフリック')
        self.window.send_requested.connect(self._send)
        self.window.theme_requested.connect(self._theme_requested)
        self.window.hidden_from_user.connect(self._mark_hidden)
        self.window.layout_size_changed.connect(self.reposition)
        self.window.apply_theme(self.launcher.color_theme)
        if not self._focus_tracking_connected:
            QApplication.instance().focusChanged.connect(self._on_focus_changed)
            self._focus_tracking_connected = True
        return self.window

    def toggle(self):
        if self.window is not None and self.window.isVisible():
            self.hide()
            return
        # Capture before the IME keyboard is focused; otherwise a Send click
        # would accidentally target the keyboard's OWN text editor.
        self.target = RemoteKanaTarget.capture(excluded_window=self.window)
        try:
            window = self._create_window()
        except Exception:
            if self.target is not None:
                self.target.release_inline_editor()
                self.target = None
            raise
        window.apply_theme(self.launcher.color_theme)
        window.send_button.setToolTip('送信先: ' + self.target.label)
        # Promote the non-focusing Remote first, then its focusable IME Tool.
        self.launcher.remote_window.set_kana_visible(True)
        window.show()
        window.raise_()
        self.reposition()
        # _fit_outer_frame runs after the show and changes geometry.
        QTimer.singleShot(30, self.reposition)
        window.activateWindow()
        window.output.setFocus(Qt.FocusReason.OtherFocusReason)

    def reposition(self):
        if self.window is None or not self.window.isVisible():
            return
        remote = getattr(self.launcher, 'remote_window', None)
        if remote is None or not remote.isVisible():
            return
        screen = QApplication.screenAt(remote.geometry().center()) or QApplication.primaryScreen()
        if screen is None:
            return
        area = screen.availableGeometry()
        width, height = self.window.width(), self.window.height()
        x = remote.x() + (remote.width() - width) // 2
        below = remote.y() + remote.height() + 4
        # Prefer below; on an edge choose above instead of clipping the IME.
        above = remote.y() - height - 4
        y = below if below + height <= area.bottom() + 1 or above < area.top() else above
        x = max(area.left(), min(x, area.right() - width + 1))
        y = max(area.top(), min(y, area.bottom() - height + 1))
        desired = QPoint(x, y)
        if self.window.pos() != desired:
            self.window.move(desired)

    def follow_launcher_move(self, delta):
        """Translate a visible kana pane with its Launch owner immediately.

        Remote may be aligned on the next event-loop cycle in 1.5-column
        mode. Moving the keyboard by the same delta prevents a stationary
        keyboard during that interval. Remote.reposition() subsequently
        adjusts edge-of-screen positioning without accumulating deltas.
        """
        if (self.window is not None and self.window.isVisible()
                and not delta.isNull()):
            self.window.move(self.window.pos() + delta)

    def _mark_hidden(self):
        # Re-enable native delegate focus-out when the companion closes.
        # Leave the inline rename text/editor untouched: Enter/Escape in the
        # original Files List still control actual filesystem renaming.
        if self.target is not None:
            self.target.release_inline_editor()
            self.target = None
        remote = getattr(self.launcher, 'remote_window', None)
        if remote is not None:
            remote.set_kana_visible(False)

    def hide(self):
        if self.window is not None:
            self.window.hide()
        self._mark_hidden()

    def theme_changed(self):
        if self.window is not None:
            self.window.apply_theme(self.launcher.color_theme)

    def _theme_requested(self, theme):
        self.launcher.set_color_theme(theme)
        if self.window is not None and self.window.isVisible():
            QTimer.singleShot(0, self._refocus_keyboard)

    def _refocus_keyboard(self):
        if self.window is not None and self.window.isVisible():
            self.window.activateWindow()
            self.window.output.setFocus(Qt.FocusReason.OtherFocusReason)

    def _send(self, text):
        if self.window is None:
            return
        if self.target is None or not self.target.can_send():
            self.window.mark_sent(False, '送信先なし。入力欄を選んでRemoteかなを開き直してください')
            return
        try:
            if self.target.external is None:
                self.target.send(text)
                action = '置換' if self.target.last_send_replaced else '追加'
                self.window.mark_sent(True, f'Launch入力欄へ{action}送信しました')
            else:
                # Qt/Windows need a turn for the foreground switch to settle.
                if not self.target.api.restore(self.target.external):
                    raise RuntimeError('送信先ウィンドウを復帰できません')
                QTimer.singleShot(110, lambda value=text: self._finish_external_send(value))
        except Exception as exc:
            self.window.mark_sent(False, f'送信中止: {exc}')

    def _finish_external_send(self, text):
        if self.window is None:
            return
        try:
            if self.target is None or self.target.external is None:
                raise RuntimeError('送信先が変更されました')
            if not self.target.api.matches(self.target.external):
                raise RuntimeError('送信先のフォーカスが一致しません。誤送信防止のため中止')
            self.target.api.send_unicode(text)
            self.window.mark_sent(True, '外部入力欄へ送信しました（選択中は置換）')
            QTimer.singleShot(80, self._refocus_keyboard)
        except Exception as exc:
            self.window.mark_sent(False, f'送信中止: {exc}')
