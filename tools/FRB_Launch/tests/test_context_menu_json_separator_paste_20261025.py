"""Regression: JSON-configured separators & paste while removing header Paste button."""
import ast
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
VIEW = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
from context_menu_config import load_context_menus, visible_context_entries

CONFIG = ROOT / 'config/context_menu_options.json'


def actions(items):
    return [x.get('action_id', '|') for x in items]


def isolated(method_name, scope):
    tree = ast.parse(APP)
    clazz = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    method = next(n for n in clazz.body if isinstance(n, ast.FunctionDef) and n.name == method_name)
    module = ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))
    exec(compile(module, 'isolated_launcher_method', 'exec'), scope)
    return scope[method_name]


def test_file_and_folder_separators_and_paste_in_json():
    data = load_context_menus(CONFIG)
    for kind in ('file', 'folder'):
        ids = actions(data[kind])
        assert ids[:4] == ['copy', 'cut', 'paste', '|']
        assert ids.count('|') >= 3
        assert ids[-1] == 'properties'
    # Multiple-selected paths, regardless of which one was right-clicked,
    # must retain full-path and filename copy operations.
    subset = actions(visible_context_entries(
        data['file'], {'copy', 'cut', 'paste', 'copy_full_path', 'copy_file_name', 'delete'}))
    assert subset == ['copy', 'cut', 'paste', '|', 'copy_full_path',
                      'copy_file_name', '|', 'delete']
    assert "load_context_menus(CONTEXT_MENU_OPTIONS)['file']" in APP


def test_separator_is_json_declared_and_does_not_expose_commands(tmp_path):
    data = json.loads(CONFIG.read_text(encoding='utf-8'))
    data['menus']['file'][0] = {'type': 'separator', 'action_id': 'copy'}
    p = tmp_path / 'invalid.json'
    p.write_text(json.dumps(data), encoding='utf-8')
    with pytest.raises(ValueError):
        load_context_menus(p)
    # The collapse helper must also handle removal of conditional items.
    entries = [{'type':'separator'}, {'action_id':'copy','title':'copy'},
               {'type':'separator'}, {'type':'separator'},
               {'action_id':'paste','title':'paste'}, {'type':'separator'}]
    assert actions(visible_context_entries(entries)) == ['copy', '|', 'paste']


def test_clipboard_enables_paste_only_with_valid_current_folder(tmp_path):
    destination = tmp_path / 'to'
    destination.mkdir()
    class Clipboard:
        def __init__(self): self.urls=[]
        def mimeData(self): return self
    clipboard=Clipboard()
    fake_app=SimpleNamespace(clipboard=lambda: clipboard)
    enabled = isolated('_context_paste_enabled', {
        'QApplication': fake_app, 'clipboard_sources': lambda mime: mime.urls,
        'is_virtual_file_clipboard': lambda mime: False,
    })
    host=SimpleNamespace(_paste_context_destination=lambda p: 'expanded')
    assert enabled(host, object()) is False
    clipboard.urls=['copy-file']
    assert enabled(host, object()) is True
    host._paste_context_destination=lambda p: None
    assert enabled(host, object()) is False
    # The current path, not the clicked file, is the destination.
    class StubCascade: pass
    resolver = isolated('_paste_context_destination', {'Path': Path, 'CascadeMenu': StubCascade})
    parent=object()
    view = SimpleNamespace(isVisible=lambda: True, current_directory=lambda: str(destination))
    host=SimpleNamespace(expanded_view=view)
    assert resolver(host,host) == 'expanded'
    assert resolver(host,parent) is None  # search result: no implicit paste target
    view.current_directory=lambda: str(tmp_path/'missing')
    assert resolver(host,host) is None


def test_paste_dispatch_uses_existing_directory_actions_only():
    dispatch = isolated('_paste_from_context_menu', {})
    seen=[]
    root=object()
    owner=SimpleNamespace(
        _context_paste_enabled=lambda p: True,
        _paste_context_destination=lambda p: 'expanded',
        paste_into_expanded_directory=lambda: seen.append('expanded'),
        paste_into_directory=lambda p: seen.append('cascade'),
    )
    dispatch(owner, root)
    assert seen == ['expanded']
    owner._paste_context_destination=lambda p: 'cascade'
    dispatch(owner,root)
    assert seen == ['expanded','cascade']
    owner._context_paste_enabled=lambda p: False
    dispatch(owner,root)
    assert seen == ['expanded','cascade']


def test_no_expanded_header_paste_and_blank_folder_support():
    assert "self.paste_button = QPushButton('貼り付け', self.shared_header)" not in VIEW
    assert 'show_expanded_background_paste_menu(' in VIEW
    assert 'self.paste_into_expanded_directory()' in APP
    assert 'menu.addSeparator()' in APP
    assert 'action.setEnabled(self._context_paste_enabled(context_parent))' in APP
