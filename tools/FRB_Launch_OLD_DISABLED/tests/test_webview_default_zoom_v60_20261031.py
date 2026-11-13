"""v60: JSON-configured initial zoom works for ALL new Web tabs.

These tests avoid importing Qt so they also run in the headless development
container, where PySide6 is unavailable. Windows visual checks remain manual.
"""
import ast
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from webview_settings import DEFAULTS, read_webview_settings


def test_initial_zoom_is_90_percent_in_both_default_and_bundled_json(tmp_path):
    assert DEFAULTS['default_zoom_percent'] == 90
    bundled = json.loads((ROOT / 'config/webview_settings.json').read_text(encoding='utf-8'))
    assert bundled['default_zoom_percent'] == 90
    assert '90' in bundled['_webview_zoom_help']
    assert read_webview_settings(ROOT / 'config/webview_settings.json')['default_zoom_percent'] == 90
    assert read_webview_settings(tmp_path / 'missing.json')['default_zoom_percent'] == 90


@pytest.mark.parametrize('percent', [50, 75, 90, 100, 125.5, 200])
def test_valid_zoom_values_are_loaded(percent, tmp_path):
    file = tmp_path / 'webview_settings.json'
    file.write_text(json.dumps({'default_zoom_percent': percent}), encoding='utf-8')
    assert read_webview_settings(file)['default_zoom_percent'] == percent


@pytest.mark.parametrize('percent', [None, '90', True, False, -100, 0, 49, 201, 10000, float('nan')])
def test_invalid_zoom_values_fall_back_to_90(percent, tmp_path):
    file = tmp_path / 'webview_settings.json'
    file.write_text(json.dumps({'default_zoom_percent': percent}), encoding='utf-8')
    assert read_webview_settings(file)['default_zoom_percent'] == 90


def test_every_new_tab_has_zoom_applied_before_url_load():
    code = (ROOT / 'src/launch_web_view.py').read_text(encoding='utf-8')
    module = ast.parse(code)
    owner_type = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == 'LaunchWebView')
    add_tab = next(n for n in owner_type.body if isinstance(n, ast.FunctionDef) and n.name == 'add_tab')
    emitted = {}
    func = ast.fix_missing_locations(ast.Module(body=[add_tab], type_ignores=[]))

    class Signal:
        def connect(self, callback):
            pass

    class View:
        def __init__(self, owner):
            self.log = []
            self.iconChanged = Signal()
            self.titleChanged = Signal()
            self.urlChanged = Signal()
            self.loadFinished = Signal()
            emitted['view'] = self
        def setPage(self, page):
            self.log.append(('page', page))
        def setZoomFactor(self, zoom):
            self.log.append(('zoom', zoom))
        def setObjectName(self, name):
            pass
        def icon(self):
            return None
        def setUrl(self, url):
            self.log.append(('url', url))

    class Tabs:
        def addTab(self, view, name):
            return 0
        def tabBar(self):
            return SimpleNamespace(setTabButton=lambda *args: None, _queue_new_tab_position=lambda: None)
        def setCurrentIndex(self, index):
            pass
    class CloseButton:
        def __init__(self, parent):
            self.clicked = Signal()
        def setIcon(self, value):
            pass

    ns = {'_LaunchWebPage': View,
          'QWebEnginePage': lambda profile, view: 'profile_page',
          '_WebCloseButton': CloseButton,
          'QTabBar': SimpleNamespace(ButtonPosition=SimpleNamespace(RightSide='right')),
          'browser_navigation_icon': lambda *args: None,
          'theme_family': lambda theme: theme,
          'QUrl': lambda url: url}
    exec(compile(func, '<isolated LaunchWebView.add_tab>', 'exec'), ns)
    for zoom in (90, 110):
        owner = SimpleNamespace(tabs=Tabs(), profile=object(),
                                web_settings={'default_zoom_percent': zoom},
                                _current_theme='light',
                                update_tab_icon=lambda *args, **kwargs: None,
                                update_title=lambda *args: None,
                                url_changed=lambda *args: None,
                                load_finished=lambda *args: None,
                                close_tab=lambda *args: None)
        ns['add_tab'](owner, 'https://example.com/', activate=True)
        calls = emitted['view'].log
        assert calls[0][0] == 'page'
        assert calls[1] == ('zoom', zoom / 100.0)
        assert calls[-1] == ('url', 'https://example.com/')


def test_webview_remains_lazy_and_webview_settings_are_shared():
    expanded = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
    assert 'self.files_content_stack, settings=self.launcher.webview_settings' in expanded
    web = (ROOT / 'src/launch_web_view.py').read_text(encoding='utf-8')
    assert 'return self._owner.add_tab(activate=not background)' in web
    assert 'self.web_settings.get(\'new_tab_url\', \'https://www.google.com/\')' in web
    ast.parse(web)
