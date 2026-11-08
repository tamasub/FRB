"""Public-settings + manual URL routing release contracts (Qt-free)."""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from registered_url_route import registered_embedded_url
from webview_routes import bookmark_web_url

APP = (ROOT / 'src/app.py').read_text('utf-8')


def method(name):
    tree = ast.parse(APP)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    scope = {'registered_embedded_url': registered_embedded_url,
             'bookmark_web_url': bookmark_web_url}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 'app.py', 'exec'), scope)
    return scope[name]


def test_menu_uses_one_warp_rod_submenu_no_plain_rod_choice():
    assert "self.mouse_pointer_rod_menu = self.theme_menu.addMenu(" in APP
    assert "'ワープ差し棒 ～ぐりぐりスピナー～（上下追従）'" in APP
    assert "self.theme_menu.addMenu('マウス差し棒')" not in APP
    assert 'self.mouse_pointer_rod_smart_action = None' in APP
    assert 'self.mouse_pointer_rod_smart_action.triggered.connect(' not in APP
    for mode in ("'off', '使用しない'", "'direct', 'Files List / Exp を直接選択'", "'windows', 'Windowsマウス方式'"):
        assert mode in APP
    assert "if self.mouse_pointer_rod_mode and not self.mouse_pointer_rod_smart_mode:" in APP
    assert 'self.set_mouse_pointer_rod_smart_mode(True)' in APP


def test_compact_hides_only_settings_item_and_keeps_header_button():
    assert "self.theme_menu.addAction('Compact表示へ切り替え')" not in APP
    assert "self.compact_mode_action = QAction('Compact表示へ切り替え', self)" in APP
    assert 'self.mode_button.clicked.connect(self.toggle_expanded_view)' in APP
    assert 'def toggle_expanded_view(self):' in APP


def test_registered_browser_url_qualification():
    plain = {'launch_action_type': 'Open', 'launch_target': 'https://example.org/frb'}
    assert registered_embedded_url(plain) == 'https://example.org/frb'
    assert registered_embedded_url({**plain, 'launch_target': 'http://example.org'}) == 'http://example.org'
    for explicit in ('chrome', 'edge'):
        assert registered_embedded_url({**plain, 'launch_browser': explicit}) is None
    assert registered_embedded_url({**plain, 'launch_browser_profile': 'Profile 1'}) is None
    for invalid in ('C:/FRB/test.md', 'shell:MyComputerFolder', 'file:///C:/test.txt',
                    'javascript:alert(1)', 'https:///missing', 'https://exam ple.org'):
        assert registered_embedded_url({**plain, 'launch_target': invalid}) is None
    assert registered_embedded_url({**plain, 'launch_action_type': 'Run'}) is None


def fake_launcher(*, page='work', view_mode='expanded', search=''):
    class Search:
        def __init__(self, text): self.value = text
        def text(self): return self.value
        def clear(self): self.value = ''
    view = NS(_ensure_web_view=Mock(return_value=True),
              isVisible=Mock(return_value=True),
              show_web_url=Mock(return_value=True))
    obj = NS(webview_settings={'mode': 'embedded'},
             expanded_options={'page_id': 'work'},
             pages=[{'page_id': 'home'}, {'page_id': 'work'}],
             expanded_view=view, view_mode=view_mode, page_id=page,
             search=Search(search), stack=[], selection=None, checked=set(),
             update_expanded_visibility=Mock(), render=Mock())
    def switch_page(index):
        obj.page_id = obj.pages[index]['page_id']
        obj.search.clear()
    obj.switch_page = Mock(side_effect=switch_page)
    obj.set_view_mode = Mock(side_effect=lambda value: setattr(obj, 'view_mode', value))
    return obj


def test_authored_open_uses_new_tab_even_when_other_page_and_compact():
    launcher = fake_launcher(page='home', view_mode='classic', search='folder search')
    url = {'launch_action_type': 'Open', 'launch_target': 'https://example.org/launch'}
    assert method('open_registered_step_in_browser')(launcher, url) is True
    launcher.switch_page.assert_called_once_with(1)
    launcher.set_view_mode.assert_called_once_with('expanded')
    launcher.expanded_view.show_web_url.assert_called_once_with(
        'https://example.org/launch', new_tab=True)
    assert launcher.search.text() == ''


def test_explicit_browser_or_external_mode_preserves_original_opener():
    route = method('open_registered_step_in_browser')
    launcher = fake_launcher()
    base = {'launch_action_type': 'Open', 'launch_target': 'https://example.org'}
    assert route(launcher, {**base, 'launch_browser': 'chrome'}) is False
    assert route(launcher, {**base, 'launch_browser': 'edge'}) is False
    assert route(launcher, {**base, 'launch_target': 'C:/Projects/a.md'}) is False
    launcher.webview_settings['mode'] = 'external'
    assert route(launcher, base) is False
    launcher.expanded_view.show_web_url.assert_not_called()


def test_unavailable_embedded_browser_uses_original_route():
    launcher = fake_launcher()
    launcher.expanded_view._ensure_web_view.return_value = False
    base = {'launch_action_type': 'Open', 'launch_target': 'https://example.org'}
    assert method('open_registered_step_in_browser')(launcher, base) is False
    launcher.expanded_view.show_web_url.assert_not_called()
    launcher.switch_page.assert_not_called()


def test_global_search_respects_explicit_external_browser():
    launcher = fake_launcher(search='FRB')
    launcher.selection = None
    url = {'item_kind': 'command', 'launch_actions': [
        {'launch_action_type': 'Open', 'launch_target': 'https://example.org',
         'launch_browser': 'chrome'}]}
    route = method('open_search_url_in_browser')
    assert route(launcher, url) is False
    launcher.expanded_view.show_web_url.assert_not_called()
    url['launch_actions'][0]['launch_browser'] = ''
    assert route(launcher, url) is True
    launcher.expanded_view.show_web_url.assert_called_once_with(
        'https://example.org', new_tab=True)


def test_execute_embedded_url_does_not_dismiss_before_showing_tab():
    """The ordinary Launch command path must hand off to Browser early."""
    launcher = NS(
        busy=False, open_bookmark_web_view=Mock(return_value=False),
        expander=Mock(return_value=NS(values={}, expand=lambda raw: raw)),
        open_registered_step_in_browser=Mock(return_value=True),
        dismiss=Mock(), next_step=Mock(),
    )
    tree = ast.parse(APP)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'execute')
    env = {'DIAG': NS(info=Mock(), exception=Mock()),
           'file_index': NS(route_registered_open_step=lambda step, root: [step])}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 'app.py', 'exec'), env)
    row = {'item_id': 'url1', 'title': 'Launch URL', 'launch_actions': [{
        'launch_action_type': 'Open', 'launch_target': 'https://example.org'}]}
    env['execute'](launcher, row)
    launcher.open_registered_step_in_browser.assert_called_once_with(row['launch_actions'][0])
    launcher.dismiss.assert_not_called()
    launcher.next_step.assert_not_called()
    assert launcher.busy is False
    assert launcher.queue == []
