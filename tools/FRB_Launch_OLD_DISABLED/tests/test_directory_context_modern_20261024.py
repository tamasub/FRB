"""Regression tests for filesystem clipboard actions and subdued paste UI.

These invoke the real methods from app.py without requiring a display server.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

SRC = Path(__file__).resolve().parents[1] / 'src' / 'app.py'
TEXT = SRC.read_text(encoding='utf-8')
TREE = ast.parse(TEXT)


def method(class_name, name, scope):
    cls = next(x for x in TREE.body if isinstance(x, ast.ClassDef) and x.name == class_name)
    fn = next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == name)
    code = ast.Module(body=[fn], type_ignores=[])
    ast.fix_missing_locations(code)
    exec(compile(code, str(SRC), 'exec'), scope)
    return scope[name]


class Mime:
    def __init__(self):
        self.urls = []
        self.meta = {}
    def setUrls(self, urls):
        self.urls = urls
    def setData(self, key, data):
        self.meta[key] = data


class Url:
    @staticmethod
    def fromLocalFile(value):
        return value


class Clipboard:
    def __init__(self):
        self.mime = None
    def setMimeData(self, mime):
        self.mime = mime


@pytest.mark.parametrize('action,expected', [('copy', 1), ('cut', 2)])
def test_copy_cut_put_file_url_on_clipboard(action, expected, tmp_path):
    from unittest.mock import Mock
    target = tmp_path / 'content.zip'
    target.write_bytes(b'a')
    clipboard = Clipboard()
    class QApplication:
        @staticmethod
        def clipboard():
            return clipboard
    scope = {'Path': Path, 'QMimeData': Mime, 'QUrl': Url,
             'QApplication': QApplication, 'DIAG': Mock()}
    handler = method('Launcher', 'perform_filesystem_context_action', scope)
    holder = SimpleNamespace(error=Mock(), footer=Mock())
    handler(holder, action, str(target), 'file')
    assert clipboard.mime.urls == [str(target.resolve())]
    assert next(iter(clipboard.mime.meta.values())) == expected.to_bytes(4, 'little')
    assert 'Preferred DropEffect' in next(iter(clipboard.mime.meta))
    holder.error.assert_not_called()


def test_delete_requires_confirmation_and_never_permanently_unlinks(tmp_path):
    target = tmp_path / 'folder'
    target.mkdir()
    delete = Mock()
    class StandardButton:
        Yes, No = 1, 2
    class QMessageBox:
        answer = 2
        @staticmethod
        def question(*args, **kwargs):
            return QMessageBox.answer
    QMessageBox.StandardButton = StandardButton
    class QTimer:
        @staticmethod
        def singleShot(delay, call):
            call()
    scope = {'Path': Path, 'QMessageBox': QMessageBox,
             'move_to_recycle_bin': delete, 'QTimer': QTimer, 'DIAG': Mock()}
    handler = method('Launcher', 'perform_filesystem_context_action', scope)
    holder = SimpleNamespace(error=Mock(), footer=Mock(),
                             _directory_menu_for_path=Mock(return_value=None), hover_timer=Mock(),
                             close_cascade_for_main_interaction=Mock(), render=Mock(),
                             file_index_settings={'enabled': False}, file_index_busy=False)
    handler(holder, 'delete', str(target), 'folder')
    delete.assert_not_called()
    assert target.exists()
    QMessageBox.answer = 1
    handler(holder, 'delete', str(target), 'folder')
    delete.assert_called_once_with(target)
    holder.close_cascade_for_main_interaction.assert_not_called()
    holder.render.assert_called_once()
    holder.error.assert_not_called()


@pytest.mark.parametrize('has_files', [False, True])
def test_paste_button_visible_only_for_file_clipboard(has_files):
    mime = object()
    class QApplication:
        @staticmethod
        def clipboard():
            return SimpleNamespace(mimeData=lambda: mime)
    scope = {'QApplication': QApplication,
             'clipboard_sources': lambda m: ['dummy.file'] if has_files else [],
             'is_virtual_file_clipboard': lambda m: False}
    update = method('CascadeMenu', '_update_paste_button', scope)
    button = SimpleNamespace(setVisible=Mock(), setEnabled=Mock())
    update(SimpleNamespace(paste_button=button))
    button.setVisible.assert_called_once_with(has_files)
    button.setEnabled.assert_called_once_with(has_files)


def test_menu_icons_attached_without_changing_json_routing():
    from context_menu_config import load_context_menus
    config = SRC.parent.parent / 'config' / 'context_menu_options.json'
    actions = load_context_menus(config)
    for kind in ('file', 'folder'):
        assert [x['action_id'] for x in actions[kind] if 'action_id' in x][:3] == ['copy', 'cut', 'paste']
    menu_fn = next(x for c in TREE.body if isinstance(c, ast.ClassDef) and c.name == 'Launcher'
                   for x in c.body if isinstance(x, ast.FunctionDef) and x.name == 'show_launch_context_menu')
    snippet = ast.get_source_segment(TEXT, menu_fn)
    assert "action.setIcon(context_action_icon(action_id))" in snippet
    assert "props.setIcon(context_action_icon('properties'))" in snippet


def test_delete_implementation_uses_shell_recycle_not_unlink_or_rmtree():
    text = (SRC.parent / 'context_menu_actions.py').read_text(encoding='utf-8')
    tree = ast.parse(text)
    method = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'move_to_recycle_bin')
    code = ast.get_source_segment(text, method)
    assert 'SHFileOperationW' in code
    assert 'FOF_ALLOWUNDO' in code and 'FOF_WANTNUKEWARNING' in code
    assert '.unlink(' not in code and 'rmtree(' not in code
