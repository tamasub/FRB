"""Regression for transient paste highlighting, Esc/outer-close and clipboard hotkeys.

Pure AST-executed tests run without PySide6; Windows NativeShell still needs
human confirmation for focus and tool-window interactions.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

SOURCE = Path(__file__).resolve().parents[1] / 'src' / 'app.py'
TEXT = SOURCE.read_text(encoding='utf-8')
ROOT = ast.parse(TEXT)


def method(cls, name, namespace):
    node = next(x for x in ROOT.body if isinstance(x, ast.ClassDef) and x.name == cls)
    fn = next(x for x in node.body if isinstance(x, ast.FunctionDef) and x.name == name)
    unit = ast.fix_missing_locations(ast.Module([fn], []))
    exec(compile(unit, str(SOURCE), 'exec'), namespace)
    return namespace[name]


class Keys:
    Key_C = 67
    Key_V = 86
    Key_X = 88


Qt = SimpleNamespace(Key=Keys, KeyboardModifier=SimpleNamespace(ControlModifier=1),
                     FocusReason=SimpleNamespace(OtherFocusReason=7))


def test_ctrl_c_copies_selected_file_when_column_owns_focus(tmp_path):
    source = tmp_path / 'note.txt'
    source.write_text('x')
    result = Mock()
    row = {'_file': str(source), 'item_kind': 'command'}
    menu = SimpleNamespace(filter_edit=SimpleNamespace(hasFocus=lambda: False),
                           activeAction=lambda: SimpleNamespace(data=lambda: row),
                           launcher=SimpleNamespace(perform_filesystem_context_action=result))
    handler = method('CascadeMenu', 'handle_file_shortcut',
                     {'Qt': Qt, 'AppCascadeMenu': type('AppCascadeMenu', (), {}),
                      'Path': Path})
    menu._filesystem_row_path = lambda r: r.get('_file')
    assert handler(menu, Keys.Key_C, 1) is True
    result.assert_called_once_with('copy', str(source), 'file')


def test_ctrl_x_cuts_folder_and_ctrl_v_pastes_into_open_directory(tmp_path):
    folder = tmp_path / 'target'
    folder.mkdir()
    row = {'_file': str(folder), 'item_kind': 'directory'}
    copy_action = Mock()
    paste_action = Mock()
    menu = SimpleNamespace(filter_edit=SimpleNamespace(hasFocus=lambda: False),
                           activeAction=lambda: SimpleNamespace(data=lambda: row),
                           launcher=SimpleNamespace(perform_filesystem_context_action=copy_action,
                                                    paste_into_directory=paste_action))
    menu._filesystem_row_path = lambda r: r.get('_file')
    menu._folder_container_row = lambda: {'item_kind': 'directory'}
    class Mime: pass
    namespace = {'Qt': Qt, 'AppCascadeMenu': type('AppCascadeMenu', (), {}),
                 'Path': Path, 'QApplication': SimpleNamespace(
                     clipboard=lambda: SimpleNamespace(mimeData=lambda: Mime())),
                 'clipboard_sources': lambda m: [folder],
                 'is_virtual_file_clipboard': lambda m: False}
    handler = method('CascadeMenu', 'handle_file_shortcut', namespace)
    assert handler(menu, Keys.Key_X, 1)
    copy_action.assert_called_once_with('cut', str(folder), 'folder')
    assert handler(menu, Keys.Key_V, 1)
    paste_action.assert_called_once_with(menu)


def test_focused_column_search_owns_native_clipboard():
    menu = SimpleNamespace(filter_edit=SimpleNamespace(hasFocus=lambda: True))
    handler = method('CascadeMenu', 'handle_file_shortcut',
                     {'Qt': Qt, 'AppCascadeMenu': type('AppCascadeMenu', (), {})})
    assert handler(menu, Keys.Key_C, 1) is False
    assert handler(menu, Keys.Key_V, 1) is False
    assert handler(menu, Keys.Key_X, 1) is False


def test_delete_reopens_even_if_modal_temporarily_hid_old_popup():
    """A modal QMenu/QMessageBox may hide the column; it MUST still reopen."""
    popup = SimpleNamespace(child=None, isVisible=lambda: False)
    launcher = SimpleNamespace(isVisible=lambda: True, menu=popup,
                               refresh_pasted_directory=Mock(),
                               _cascade_dismiss_generation=99)
    fn = method('Launcher', 'refresh_deleted_directory', {})
    fn(launcher, popup)
    launcher.refresh_pasted_directory.assert_called_once_with(
        popup, reopen=True, focus_pasted=False, review_deleted=True)


def test_delete_does_not_depend_on_transient_parent_visibility_or_generation():
    popup = SimpleNamespace(child=None, isVisible=lambda: False)
    launcher = SimpleNamespace(isVisible=lambda: False, menu=None,
                               refresh_pasted_directory=Mock(),
                               _cascade_dismiss_generation=12)
    fn = method('Launcher', 'refresh_deleted_directory', {})
    fn(launcher, popup)
    launcher.refresh_pasted_directory.assert_called_once_with(
        popup, reopen=True, focus_pasted=False, review_deleted=True)


def test_paste_highlight_is_popup_scoped_not_launcher_global():
    scope = method('CascadeMenu', '_transfer_state', {})
    assert '_pasted_feedback_paths' in scope.__code__.co_consts or '_pasted_feedback_paths' in TEXT
    launcher = next(x for x in ROOT.body if isinstance(x, ast.ClassDef) and x.name == 'Launcher')
    paste = next(x for x in launcher.body if isinstance(x, ast.FunctionDef) and x.name == 'paste_into_directory')
    refresh = next(x for x in launcher.body if isinstance(x, ast.FunctionDef) and x.name == 'refresh_pasted_directory')
    assert 'menu._pasted_feedback_paths = pasted_paths_for' in ast.get_source_segment(TEXT, paste)
    fragment = ast.get_source_segment(TEXT, refresh)
    assert "if focus_pasted else ()" in fragment
    assert "'keyboard' if review_deleted else previous.open_mode" in fragment
    assert 'replacement._transient_transfer_feedback = True' not in fragment


def test_escape_and_modal_protection_are_explicit():
    assert 'getattr(self, \'_filesystem_dialog_depth\', 0)' in TEXT
    assert 'class CascadeOutsideClickFilter(QObject)' in TEXT
    assert 'active_column.close()' in TEXT
    assert 'self.paste_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)' in TEXT


def test_delete_refreshes_nested_popup_using_same_paste_lifecycle():
    child = SimpleNamespace(child=None)
    parent = SimpleNamespace(child=child)
    launcher = SimpleNamespace(menu=parent, refresh_pasted_directory=Mock())
    fn = method('Launcher', 'refresh_deleted_directory', {})
    fn(launcher, child)
    launcher.refresh_pasted_directory.assert_called_once_with(
        child, reopen=True, focus_pasted=False, review_deleted=True)


def test_main_search_is_not_forced_into_clipboard_shortcut_handler():
    launcher = next(x for x in ROOT.body if isinstance(x, ast.ClassDef) and x.name == 'Launcher')
    fn = next(x for x in launcher.body if isinstance(x, ast.FunctionDef) and x.name == 'eventFilter')
    code = ast.get_source_segment(TEXT, fn)
    assert 'editor_focused = (obj is self.search and self.search.hasFocus())' in code
    assert 'cascade.handle_file_shortcut(k, event.modifiers())' in code
    assert 'active_column.close()' in code


def test_global_outside_click_filter_does_not_consume_mouse_event():
    class EventType:
        MouseButtonPress = 1
        KeyPress = 2
    class QObject:
        def __init__(self, parent=None):
            self._parent = parent
        def parent(self):
            return self._parent
    class CascadeMenu(QObject):
        pass
    class QApplication:
        @staticmethod
        def activeModalWidget():
            return None
    fn = method('CascadeOutsideClickFilter', 'eventFilter',
                {'QObject': QObject, 'CascadeMenu': CascadeMenu,
                 'QEvent': SimpleNamespace(Type=EventType), 'QApplication': QApplication})
    launcher = QObject()
    launcher.menu = SimpleNamespace(isVisible=lambda: True)
    launcher.close_cascade_for_main_interaction = Mock()
    handler = SimpleNamespace(launcher=launcher)
    event = SimpleNamespace(type=lambda: 1)
    nested = QObject(CascadeMenu(launcher))
    assert fn(handler, nested, event) is False
    launcher.close_cascade_for_main_interaction.assert_not_called()
    assert fn(handler, QObject(launcher), event) is False
    launcher.close_cascade_for_main_interaction.assert_called_once()
