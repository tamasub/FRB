"""Regression for virtual Shell clipboard entries copied from inside ZIP files."""

from pathlib import Path
import struct
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from virtual_clipboard_paste import (
    is_virtual_file_clipboard, virtual_clipboard_names, preflight_virtual_destination,
    paste_virtual_shell_items,
)


class Mime:
    def __init__(self, content=None):
        self.content = content or {}
    def formats(self):
        return list(self.content)
    def data(self, fmt):
        return self.content[fmt]


def descriptors(names, wide=True):
    stride = 592 if wide else 332
    content = bytearray(struct.pack('<I', len(names)) + b'\x00' * stride * len(names))
    for i, name in enumerate(names):
        blob = name.encode('utf-16-le') if wide else name.encode('ascii')
        start = 4 + stride * i + 72
        content[start:start + len(blob)] = blob
    return bytes(content)


def test_virtual_zip_clipboard_markers_and_regular_text():
    assert not is_virtual_file_clipboard(None)
    assert not is_virtual_file_clipboard(Mime({'text/plain': b'file.txt'}))
    assert not is_virtual_file_clipboard(Mime({'text/uri-list': b'file:///c:/x'}))
    assert is_virtual_file_clipboard(Mime({
        'application/x-qt-windows-mime;value="FileGroupDescriptorW"': descriptors(['abc.txt'])
    }))
    assert is_virtual_file_clipboard(Mime({
        'application/x-qt-windows-mime;value="Shell IDList Array"': b'...'
    }))


def test_filegroupdescriptor_unicode_names_and_folder_subpaths():
    mime = Mime({'application/x-qt-windows-mime;value="FileGroupDescriptorW"':
                 descriptors(['資料.txt', 'folder\\nested.txt', 'folder\\other.txt'])})
    assert virtual_clipboard_names(mime) == ['folder', '資料.txt']
    assert virtual_clipboard_names(Mime({'application/x-qt-windows-mime;value="Shell IDList Array"': b'.'})) is None


def test_ansi_virtual_clipboard():
    mime = Mime({'application/x-qt-windows-mime;value="FileGroupDescriptor"':
                 descriptors(['file.txt'], wide=False)})
    assert virtual_clipboard_names(mime) == ['file.txt']


def test_reject_malformed_descriptors_and_unsafe_names():
    marker = 'application/x-qt-windows-mime;value="FileGroupDescriptorW"'
    with pytest.raises(ValueError):
        virtual_clipboard_names(Mime({marker: b'\x01\x00'}))
    with pytest.raises(ValueError):
        virtual_clipboard_names(Mime({marker: struct.pack('<I', 1) + b'\0' * 5}))
    with pytest.raises(ValueError):
        virtual_clipboard_names(Mime({marker: descriptors(['..\\evil.txt'])}))


def test_destination_conflict_detected_without_copy(tmp_path):
    (tmp_path / 'exists.txt').write_text('original')
    with pytest.raises(FileExistsError, match='上書きしません'):
        preflight_virtual_destination(tmp_path, ['exists.txt'])
    assert (tmp_path / 'exists.txt').read_text() == 'original'
    preflight_virtual_destination(tmp_path, ['newfile.txt'])
    with pytest.raises(ValueError):
        preflight_virtual_destination(tmp_path / 'missing', ['newfile.txt'])


def test_native_windows_only_on_nonwindows(tmp_path):
    if sys.platform != 'win32':
        with pytest.raises(OSError, match='Windows専用'):
            paste_virtual_shell_items(tmp_path)


def test_app_shows_button_and_preserves_original_local_copy():
    source = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf8')
    assert 'is_virtual_file_clipboard(mime)' in source
    assert 'available = bool(clipboard_sources(mime)) or is_virtual_file_clipboard(mime)' in source
    assert 'paste_virtual_shell_items(destination, overwrite_confirmed=bool(conflicts))' in source
    assert 'make_paste_plan(destination, sources, allow_existing=True)' in source
    assert 'paste_items(plan, move=move, overwrite=bool(conflicts))' in source


def test_launcher_routes_virtual_zip_without_reextracting_to_temporary_file(tmp_path):
    import ast
    from types import SimpleNamespace
    from unittest.mock import Mock
    source = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf8')
    tree = ast.parse(source)
    launcher = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'Launcher')
    method = next(node for node in launcher.body if isinstance(node, ast.FunctionDef) and node.name == 'paste_into_directory')
    code = ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))

    virtual = Mime({'application/x-qt-windows-mime;value="FileGroupDescriptorW"':
                    descriptors(['archive_member.txt'])})
    native = __import__('unittest.mock', fromlist=['Mock']).Mock()
    class QApplication:
        @staticmethod
        def clipboard():
            return SimpleNamespace(mimeData=lambda: virtual, clear=lambda: None)
    class QTimer:
        @staticmethod
        def singleShot(delay, cb):
            assert delay == 0  # defer refresh until native paste returns
    scope = {'Path': Path, 'QApplication': QApplication,
             'clipboard_sources': lambda m: [],
             'is_cut_clipboard': lambda m: False,
             'is_virtual_file_clipboard': is_virtual_file_clipboard,
             'virtual_clipboard_names': virtual_clipboard_names,
             'preflight_virtual_destination': preflight_virtual_destination,
             'paste_virtual_shell_items': native,
             'QTimer': QTimer, 'DIAG': __import__('unittest.mock', fromlist=['Mock']).Mock(),
             'pasted_paths_for': lambda destination, names: [str(destination / name) for name in names]}
    exec(compile(code, 'src/app.py', 'exec'), scope)
    row = {'launch_browse_target': str(tmp_path)}
    holder = SimpleNamespace(expander=lambda: SimpleNamespace(expand=lambda value: value),
                             footer=SimpleNamespace(setText=lambda msg: None),
                             refresh_pasted_directory=lambda _, **kwargs: None,
                             error=__import__('unittest.mock', fromlist=['Mock']).Mock())
    popup = SimpleNamespace(_folder_container_row=lambda: row)
    scope['paste_into_directory'](holder, popup)
    native.assert_called_once_with(tmp_path, overwrite_confirmed=False)
    holder.error.assert_not_called()


def test_native_overwrite_suppression_is_explicit_and_scoped(tmp_path, monkeypatch):
    """Known, Launch-approved conflicts set only the Shell confirmation flag.

    Mimic COM methods without changing the real operating system clipboard.
    """
    import ctypes
    from types import SimpleNamespace
    import virtual_clipboard_paste as module

    class Function:
        def __call__(self, *args):
            return 0

    ole = SimpleNamespace(**{key: Function() for key in (
        'OleInitialize', 'OleGetClipboard', 'CoCreateInstance', 'OleUninitialize')})
    shell = SimpleNamespace(SHCreateItemFromParsingName=Function())
    monkeypatch.setattr(module, 'sys', SimpleNamespace(platform='win32'))
    monkeypatch.setattr(module.ctypes, 'OleDLL',
                        lambda name: ole if name == 'ole32' else shell, raising=False)
    calls = []
    monkeypatch.setattr(module, '_com_call',
                        lambda pointer, index, argtypes=(), args=():
                        calls.append((index, args)) or 0)
    monkeypatch.setattr(module, '_release', lambda pointer: None)

    module.paste_virtual_shell_items(tmp_path)
    assert not any(index == 5 for index, _ in calls)
    calls.clear()
    module.paste_virtual_shell_items(tmp_path, overwrite_confirmed=True)
    assert [args[0] for index, args in calls if index == 5] == [0x0040 | 0x0200 | 0x0010]
    assert [index for index, _ in calls if index == 17] == [17]
    assert [index for index, _ in calls if index == 21] == [21]


def test_virtual_copy_asks_once_then_passes_confirmed_overwrite(tmp_path):
    import ast
    from types import SimpleNamespace
    from unittest.mock import Mock
    source = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf8')
    tree = ast.parse(source)
    launcher = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    method = next(n for n in launcher.body if isinstance(n, ast.FunctionDef)
                  and n.name == 'paste_into_directory')
    code = ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))
    marker = 'application/x-qt-windows-mime;value="FileGroupDescriptorW"'
    mime = Mime({marker: descriptors(['existing.txt'])})
    (tmp_path / 'existing.txt').write_text('do not touch')
    shell = Mock()
    class QApplication:
        @staticmethod
        def clipboard():
            return SimpleNamespace(mimeData=lambda: mime, clear=lambda: None)
    class QTimer:
        @staticmethod
        def singleShot(delay, callback):
            assert delay == 0
    scope = {'Path': Path, 'QApplication': QApplication,
             'clipboard_sources': lambda m: [], 'is_cut_clipboard': lambda m: False,
             'is_virtual_file_clipboard': is_virtual_file_clipboard,
             'virtual_clipboard_names': virtual_clipboard_names,
             'preflight_virtual_destination': preflight_virtual_destination,
             'paste_virtual_shell_items': shell, 'QTimer': QTimer,
             'DIAG': Mock(), 'pasted_paths_for': lambda destination, names: []}
    exec(compile(code, 'src/app.py', 'exec'), scope)
    holder = SimpleNamespace(expander=lambda: SimpleNamespace(expand=lambda v: v),
                             footer=SimpleNamespace(setText=lambda s: None),
                             refresh_pasted_directory=Mock(), error=Mock(),
                             _ask_overwrite=Mock(return_value=False))
    popup = SimpleNamespace(_folder_container_row=lambda: {'launch_browse_target': str(tmp_path)})
    scope['paste_into_directory'](holder, popup)
    holder._ask_overwrite.assert_called_once()
    shell.assert_not_called()
    assert (tmp_path / 'existing.txt').read_text() == 'do not touch'
    holder._ask_overwrite.reset_mock(return_value=True)
    holder._ask_overwrite.return_value = True
    scope['paste_into_directory'](holder, popup)
    shell.assert_called_once_with(tmp_path, overwrite_confirmed=True)
