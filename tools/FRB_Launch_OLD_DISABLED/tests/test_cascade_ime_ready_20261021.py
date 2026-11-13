"""First-key Japanese IME safeguards for folder-column search.

The AST tests work without PySide6. Native Qt preedit tests are opt-in and
still require a real Windows IME check for OS-specific input-context behavior.
"""
import ast
from pathlib import Path

import pytest

CODE_PATH = Path(__file__).resolve().parents[1] / 'src' / 'app.py'
CODE = CODE_PATH.read_text(encoding='utf-8')
TREE = ast.parse(CODE)
CASCADE = next(node for node in TREE.body if isinstance(node, ast.ClassDef)
               and node.name == 'CascadeMenu')


def method(name):
    return next(node for node in CASCADE.body
                if isinstance(node, ast.FunctionDef) and node.name == name)


def test_first_ime_input_has_a_preexisting_editor():
    setup = ast.get_source_segment(CODE, method('_prepare_ime_input'))
    popup = ast.get_source_segment(CODE, method('popup'))
    assert 'QLineEdit(container)' in setup
    assert 'WA_InputMethodEnabled' in setup
    assert 'setFixedHeight(2)' in setup
    assert 'insertAction(before, action)' in setup
    assert popup.index('self._prepare_ime_input()') < popup.index('super().popup(target, at)')
    assert 'QTimer.singleShot(0, self._focus_ime_input)' in popup


def test_preedit_expands_same_editor_before_qt_delivers_text():
    setup = ast.get_source_segment(CODE, method('_prepare_ime_input'))
    reveal = ast.get_source_segment(CODE, method('_ensure_local_filter'))
    events = ast.get_source_segment(CODE, method('eventFilter'))
    assert 'self._ime_input_edit = edit' in setup
    assert 'self.filter_edit = self._ime_input_edit' in reveal
    assert 'event.preeditString() or event.commitString()' in events
    assert 'self._ensure_local_filter()' in events
    assert 'return False  # Let QLineEdit / Windows IME handle the real input.' in events
    assert 'self.keyPressEvent(event)' in events


def test_reset_leaves_ime_ready_editor_for_next_search():
    reset = ast.get_source_segment(CODE, method('clear_local_filter'))
    assert 'self.filter_edit = None' in reset
    assert 'container.setFixedHeight(2)' in reset
    assert 'self._focus_ime_input()' in reset
    assert 'self.removeAction(action)' not in reset
    assert 'action.deleteLater()' not in reset


def test_installed_apps_menu_uses_existing_global_search_route():
    prepare = ast.get_source_segment(CODE, method('_prepare_ime_input'))
    assert 'isinstance(self, AppCascadeMenu)' in prepare


try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QInputMethodEvent
    from PySide6.QtWidgets import QApplication
    import sys
    sys.path.insert(0, str(CODE_PATH.parent))
    import app
except ImportError:
    QApplication = None


@pytest.mark.skipif(QApplication is None, reason='Native Qt/PySide6 required')
def test_native_editor_keeps_first_japanese_preedit_while_revealing():
    qt = QApplication.instance() or QApplication([])
    menu = app.CascadeMenu()
    menu.addAction('対象ファイル')
    menu.popup(app.QPoint(100, 100))
    try:
        qt.processEvents()
        initial_editor = menu._ime_input_edit
        assert initial_editor.isVisible()
        assert menu.filter_edit is None
        initial_editor.setFocus()
        qt.processEvents()
        ime = QInputMethodEvent('日本', [])
        QApplication.sendEvent(initial_editor, ime)
        qt.processEvents()
        assert menu.filter_edit is initial_editor
        assert menu.filter_action is menu._ime_filter_action
        assert menu._filter_ime_composing is True
        assert menu._ime_filter_container.height() > 2
        QApplication.sendEvent(initial_editor, QInputMethodEvent('', []))
        # The same editor remains available; no reparent/recreation on commit.
        assert menu.filter_edit is initial_editor
    finally:
        menu.close()
