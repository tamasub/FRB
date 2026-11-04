"""Destination tracking for the optional Remote kana keyboard.

Capture explicit text focus before opening the keyboard, and follow explicit
Launch text-focus changes while it is open. Send replaces selected text, or
inserts at the caret if nothing is selected. Never use the clipboard.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
import sys
import weakref


def widget_is_text_target(widget) -> bool:
    """Only standard Qt editable text controls (not a generic selected row)."""
    from PySide6.QtWidgets import QLineEdit, QPlainTextEdit, QTextEdit, QComboBox
    if isinstance(widget, QLineEdit):
        return not widget.isReadOnly()
    if isinstance(widget, (QPlainTextEdit, QTextEdit)):
        return not widget.isReadOnly()
    if isinstance(widget, QComboBox) and widget.isEditable():
        return widget.lineEdit() is not None and not widget.lineEdit().isReadOnly()
    return False


def insert_into_widget(widget, text: str, selection=None) -> bool:
    """Replace an existing selection; otherwise insert at the current caret.

    Some Qt controls drop their visible selection on FocusOut. Restore only
    an explicitly captured selection, and only if the destination text is
    unchanged since capture (never replace unrelated or newly edited text).
    """
    from PySide6.QtWidgets import QLineEdit, QPlainTextEdit, QTextEdit, QComboBox
    if isinstance(widget, QComboBox):
        widget = widget.lineEdit()
    if isinstance(widget, QLineEdit):
        if (selection and selection[0] == 'line' and
                widget.selectionStart() < 0 and widget.text() == selection[1]):
            widget.setSelection(selection[2], selection[3])
        replaced = widget.selectionStart() >= 0
        widget.insert(text)  # Qt replaces the selected range, if any.
        return replaced
    if isinstance(widget, (QPlainTextEdit, QTextEdit)):
        cursor = widget.textCursor()
        if (selection and selection[0] == 'document' and
                not cursor.hasSelection() and
                widget.document().revision() == selection[1]):
            cursor.setPosition(selection[2])
            cursor.setPosition(selection[3], cursor.MoveMode.KeepAnchor)
        replaced = cursor.hasSelection()
        cursor.insertText(text)
        widget.setTextCursor(cursor)
        return replaced
    raise ValueError('入力欄ではありません')


@dataclass
class ExternalTarget:
    foreground: int
    focused_child: int
    title: str


class UnicodeWin32:
    """Small SendInput adapter; only initialized on Windows."""
    def __init__(self):
        if sys.platform != 'win32':
            raise RuntimeError('Windowsでのみ利用できます')
        import ctypes
        from ctypes import wintypes
        self.c = ctypes
        self.w = wintypes
        self.user = ctypes.WinDLL('user32', use_last_error=True)
        U_PTR = ctypes.c_size_t

        class KeyboardInput(ctypes.Structure):
            _fields_ = [('vk', wintypes.WORD), ('scan', wintypes.WORD),
                        ('flags', wintypes.DWORD), ('time', wintypes.DWORD),
                        ('extra', U_PTR)]
        class MouseInput(ctypes.Structure):
            _fields_ = [('dx', wintypes.LONG), ('dy', wintypes.LONG),
                        ('mouseData', wintypes.DWORD), ('flags', wintypes.DWORD),
                        ('time', wintypes.DWORD), ('extra', U_PTR)]
        class HardwareInput(ctypes.Structure):
            _fields_ = [('message', wintypes.DWORD), ('low', wintypes.WORD), ('high', wintypes.WORD)]
        class EventUnion(ctypes.Union):
            _fields_ = [('key', KeyboardInput), ('mouse', MouseInput), ('hardware', HardwareInput)]
        class Input(ctypes.Structure):
            _fields_ = [('type', wintypes.DWORD), ('data', EventUnion)]
        class GUIThreadInfo(ctypes.Structure):
            _fields_ = [('cbSize', wintypes.DWORD), ('flags', wintypes.DWORD),
                        ('hwndActive', wintypes.HWND), ('hwndFocus', wintypes.HWND),
                        ('hwndCapture', wintypes.HWND), ('hwndMenuOwner', wintypes.HWND),
                        ('hwndMoveSize', wintypes.HWND), ('hwndCaret', wintypes.HWND),
                        ('rcCaret', wintypes.RECT)]
        self.Input = Input
        self.GUIThreadInfo = GUIThreadInfo
        self.user.GetForegroundWindow.restype = wintypes.HWND
        self.user.GetWindowThreadProcessId.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.DWORD))
        self.user.GetWindowThreadProcessId.restype = wintypes.DWORD
        self.user.GetGUIThreadInfo.argtypes = (wintypes.DWORD, ctypes.POINTER(GUIThreadInfo))
        self.user.GetGUIThreadInfo.restype = wintypes.BOOL
        self.user.IsWindow.argtypes = (wintypes.HWND,)
        self.user.IsWindow.restype = wintypes.BOOL
        self.user.SetForegroundWindow.argtypes = (wintypes.HWND,)
        self.user.SetForegroundWindow.restype = wintypes.BOOL
        self.user.GetWindowTextW.argtypes = (wintypes.HWND, wintypes.LPWSTR, ctypes.c_int)
        self.user.GetWindowTextW.restype = ctypes.c_int
        self.user.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(Input), ctypes.c_int)
        self.user.SendInput.restype = wintypes.UINT

    def foreground_is_ours(self) -> bool:
        top = int(self.user.GetForegroundWindow() or 0)
        if not top:
            return False
        pid = self.w.DWORD()
        self.user.GetWindowThreadProcessId(top, self.c.byref(pid))
        return pid.value == os.getpid()

    def focused(self):
        top = int(self.user.GetForegroundWindow() or 0)
        if not top:
            return None
        pid = self.w.DWORD()
        thread = self.user.GetWindowThreadProcessId(top, self.c.byref(pid))
        if pid.value == os.getpid():
            return None
        info = self.GUIThreadInfo()
        info.cbSize = self.c.sizeof(info)
        if not self.user.GetGUIThreadInfo(thread, self.c.byref(info)):
            return None
        hwnd = int(info.hwndFocus or 0)
        if not hwnd or not self.user.IsWindow(hwnd):
            return None
        name = self.c.create_unicode_buffer(256)
        self.user.GetWindowTextW(top, name, len(name))
        return ExternalTarget(top, hwnd, name.value or '外部アプリ')

    def restore(self, target: ExternalTarget) -> bool:
        if not self.user.IsWindow(target.foreground) or not self.user.IsWindow(target.focused_child):
            return False
        if int(self.user.GetForegroundWindow() or 0) != target.foreground:
            if not self.user.SetForegroundWindow(target.foreground):
                return False
        return True

    def matches(self, target: ExternalTarget) -> bool:
        top = int(self.user.GetForegroundWindow() or 0)
        if top != target.foreground:
            return False
        thread = self.user.GetWindowThreadProcessId(top, None)
        info = self.GUIThreadInfo()
        info.cbSize = self.c.sizeof(info)
        return bool(self.user.GetGUIThreadInfo(thread, self.c.byref(info)) and
                    int(info.hwndFocus or 0) == target.focused_child)

    def send_unicode(self, text: str) -> None:
        # UTF-16 input units, including surrogate pairs for non-BMP characters.
        encoded = text.encode('utf-16-le')
        units = [int.from_bytes(encoded[i:i+2], 'little')
                 for i in range(0, len(encoded), 2)]
        events = []
        for unit in units:
            for up in (False, True):
                events.append(self.Input(1, self.Input._fields_[1][1](
                    key=self.Input._fields_[1][1]._fields_[0][1](
                        0, unit, 0x0004 | (0x0002 if up else 0), 0, 0))))
        if not events:
            return
        array = (self.Input * len(events))(*events)
        count = self.user.SendInput(len(events), array, self.c.sizeof(self.Input))
        if count != len(events):
            raise OSError(self.c.get_last_error(), f'文字送信が部分失敗しました ({count}/{len(events)})')


class RemoteKanaTarget:
    def __init__(self, widget=None, external=None, api=None):
        self.widget_ref = weakref.ref(widget) if widget is not None else None
        self.external = external
        self.api = api
        self._inline_focus_guard = None
        self._selection = None
        self.last_send_replaced = False
        if widget is not None:
            self.remember_selection()

    def remember_selection(self):
        """Remember only a real selection while a text editor owns focus."""
        widget = self.widget_ref() if self.widget_ref else None
        if widget is None:
            return
        from PySide6.QtWidgets import QLineEdit, QPlainTextEdit, QTextEdit, QComboBox
        if isinstance(widget, QComboBox):
            widget = widget.lineEdit()
        if isinstance(widget, QLineEdit):
            start = widget.selectionStart()
            if start >= 0 and widget.selectedText():
                self._selection = ('line', widget.text(), start, len(widget.selectedText()))
        elif isinstance(widget, (QPlainTextEdit, QTextEdit)):
            cursor = widget.textCursor()
            if cursor.hasSelection():
                self._selection = ('document', widget.document().revision(),
                                   cursor.selectionStart(), cursor.selectionEnd())

    @classmethod
    def from_widget(cls, widget):
        """Track a newly focused Launch editor, even with FRBかな already open."""
        if not widget_is_text_target(widget):
            return cls()
        target = cls(widget=widget)
        target.preserve_inline_editor()
        return target

    def preserve_inline_editor(self):
        """Keep a Qt delegate's temporary rename editor alive while kana has IME focus.

        Normally QStyledItemDelegate commits/closes an inline QLineEdit on
        FocusOut. FRBかな MUST activate its own QLineEdit for Windows IME,
        so retaining a weak reference alone is not enough. Add a temporary
        event filter *after* the delegate's filter, intercepting only FocusOut
        during this keyboard session. Explicit Enter/Escape still belong to
        the original delegate, and ordinary text inputs are unaffected.
        """
        widget = self.widget_ref() if self.widget_ref else None
        if widget is None or widget.objectName() not in (
                'inlineRenameEditor', 'filesExpRenameEditor'):
            return
        from PySide6.QtCore import QEvent, QObject

        class _KeepInlineRenameOpen(QObject):
            def eventFilter(self, watched, event):
                if watched is widget and event.type() == QEvent.Type.FocusOut:
                    return True
                return False

        guard = _KeepInlineRenameOpen(widget)
        widget.installEventFilter(guard)
        self._inline_focus_guard = guard  # Keep the Python QObject alive.

    def release_inline_editor(self):
        """Restore the normal Qt focus-out behavior when FRBかな is hidden."""
        guard = self._inline_focus_guard
        self._inline_focus_guard = None
        if guard is None:
            return
        widget = self.widget_ref() if self.widget_ref else None
        try:
            if widget is not None:
                widget.removeEventFilter(guard)
            guard.deleteLater()
        except RuntimeError:
            # The view/editor may have been destroyed by navigation or close.
            pass

    @classmethod
    def capture(cls, excluded_window=None):
        from PySide6.QtWidgets import QApplication
        # QApplication.focusWidget() is remembered after Launch loses focus.
        # An external foreground editor must win over that stale Qt pointer.
        if sys.platform == 'win32':
            api = UnicodeWin32()
            if not api.foreground_is_ours():
                target = api.focused()
                return cls(external=target, api=api) if target is not None else cls()
        focus = QApplication.focusWidget()
        if focus is not None and focus.window() is excluded_window:
            focus = None
        if widget_is_text_target(focus):
            return cls.from_widget(focus)  # Guard before IME focus moves.
        return cls()

    @property
    def label(self):
        if self.widget_ref is not None and self.widget_ref() is not None:
            widget = self.widget_ref()
            return 'Launch入力欄: ' + (widget.objectName() or type(widget).__name__)
        if self.external is not None:
            return self.external.title
        return '送信先未選択'

    def can_send(self) -> bool:
        return bool(self.widget_ref and self.widget_ref() is not None) or self.external is not None

    def send(self, text: str, *, retry=None):
        if not text:
            raise ValueError('送信文字列が空です')
        if self.widget_ref is not None:
            widget = self.widget_ref()
            if widget is None or not widget_is_text_target(widget):
                raise RuntimeError('送信先の入力欄が閉じられました')
            replaced = insert_into_widget(widget, text, self._selection)
            self.last_send_replaced = replaced
            self._selection = None  # Second Send must insert, not replace again.
            return True
        if self.external is not None:
            if self.api is None or not self.api.restore(self.external):
                raise RuntimeError('送信先ウィンドウを復帰できません')
            if retry is None:
                if not self.api.matches(self.external):
                    raise RuntimeError('送信先のカーソル位置が変わりました。誤送信防止のため中止')
                self.api.send_unicode(text)
                return True
            retry()
            return False
        raise RuntimeError('送信先がありません。送信先の入力欄を選んでからキーボードを開いてください')
