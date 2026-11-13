"""v75 regression: Remote Browser bookmark popup chooses new/current Web tab.

Qt-free behavioural checks plus narrow source contracts. Manual Qt UI still required.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
EXP = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')


def extract(src, cls, name, env=None):
    tree = ast.parse(src)
    klass = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                 and node.name == cls)
    func = next(node for node in klass.body if isinstance(node, ast.FunctionDef)
                and node.name == name)
    code = ast.Module(body=[func], type_ignores=[])
    scope = dict(env or {})
    exec(compile(ast.fix_missing_locations(code), '<v75>', 'exec'), scope)
    return scope[name], ast.get_source_segment(src, func)


def url_for(row):
    if row.get('item_kind') != 'command':
        return None
    return row.get('url')


def launcher(new_tab=True, *, remote_root=True, mode='embedded', success=True):
    root = NS(remote_browser_bookmark_roots=remote_root,
              remote_bookmark_new_tab=new_tab, close=Mock())
    view = NS(show_web_url=Mock(return_value=success))
    target = NS(menu=root, webview_settings={'mode': mode}, expanded_view=view,
                activate=Mock())
    return target, root, view


def test_remote_url_new_tab_is_default_and_closes_menu():
    fn, _ = extract(APP, 'Launcher', 'run_menu_item',
                    {'bookmark_web_url': url_for})
    obj, root, view = launcher()
    row = {'item_kind': 'command', 'url': 'https://example.com'}
    fn(obj, row)
    view.show_web_url.assert_called_once_with('https://example.com', new_tab=True)
    root.close.assert_called_once()
    obj.activate.assert_not_called()


def test_remote_url_current_tab_when_selected():
    fn, _ = extract(APP, 'Launcher', 'run_menu_item',
                    {'bookmark_web_url': url_for})
    obj, root, view = launcher(new_tab=False)
    fn(obj, {'item_kind': 'command', 'url': 'https://example.com/current'})
    view.show_web_url.assert_called_once_with('https://example.com/current', new_tab=False)
    root.close.assert_called_once()


def test_normal_bookmark_and_external_mode_keep_existing_activation():
    fn, _ = extract(APP, 'Launcher', 'run_menu_item',
                    {'bookmark_web_url': url_for})
    row = {'item_kind': 'command', 'url': 'https://example.com'}
    for remote_root, mode in ((False, 'embedded'), (True, 'external')):
        obj, root, view = launcher(remote_root=remote_root, mode=mode)
        fn(obj, row)
        root.close.assert_called_once()
        view.show_web_url.assert_not_called()
        obj.activate.assert_called_once_with(row)


def test_bookmark_folder_is_not_opened_as_url():
    fn, _ = extract(APP, 'Launcher', 'run_menu_item',
                    {'bookmark_web_url': url_for})
    obj, root, view = launcher()
    row = {'item_kind': 'category', 'title': 'Folder'}
    fn(obj, row)
    view.show_web_url.assert_not_called()
    obj.activate.assert_called_once_with(row)


def test_failed_embedded_webview_keeps_existing_fallback():
    fn, _ = extract(APP, 'Launcher', 'run_menu_item',
                    {'bookmark_web_url': url_for})
    obj, root, view = launcher(success=False)
    row = {'item_kind': 'command', 'url': 'https://example.com'}
    fn(obj, row)
    view.show_web_url.assert_called_once()
    obj.activate.assert_called_once_with(row)


def test_radio_controls_live_below_search_inside_only_browser_root_filter():
    _, fn = extract(APP, 'CascadeMenu', '_ensure_local_filter')
    assert "bookmark_root = getattr(self, 'remote_browser_bookmark_roots', False)" in fn
    assert 'layout = QVBoxLayout(container) if bookmark_root else QHBoxLayout(container)' in fn
    assert 'layout.addLayout(search_row)' in fn
    assert "QPushButton('新規タブ', container)" in fn
    assert "QPushButton('カレントタブ', container)" in fn
    assert 'target_row.setContentsMargins(0, 0, 0, 0)' in fn
    assert 'self._select_remote_bookmark_tab(True)' in fn
    assert 'self._select_remote_bookmark_tab(False)' in fn
    assert 'layout.addLayout(target_row)' in fn
    assert fn.index('layout.addLayout(search_row)') < fn.index('layout.addLayout(target_row)')
    _, popup = extract(APP, 'CascadeMenu', 'popup')
    assert 'self._ensure_local_filter()' in popup
    _, browser = extract(APP, 'Launcher', 'show_remote_browser_bookmark_menu')
    assert 'menu.remote_browser_bookmark_roots = True' in browser
    assert 'menu.remote_bookmark_new_tab = True' in browser


def test_expanded_browser_supports_current_and_new_tab_without_reloading_existing():
    fn, source = extract(EXP, 'ExpandedLauncherView', 'show_web_url')
    assert "def show_web_url(self, url, *, new_tab=False):" in source
    web = NS(show_url=Mock())
    view = NS(launcher=NS(webview_settings={'mode': 'embedded'}),
              _ensure_web_view=Mock(return_value=True),
              files_content_stack=NS(setCurrentWidget=Mock()), web_view=web,
              _activate_browser_layout=Mock())
    assert fn(view, 'https://example.com', new_tab=True) is True
    web.show_url.assert_called_with('https://example.com', new_tab=True)
    web.show_url.reset_mock()
    assert fn(view, 'https://example.com', new_tab=False) is True
    web.show_url.assert_called_with('https://example.com')
    assert view.files_content_stack.setCurrentWidget.call_count == 2
    assert view._activate_browser_layout.call_count == 2
