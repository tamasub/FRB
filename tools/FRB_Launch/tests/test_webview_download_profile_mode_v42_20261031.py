"""v42: in-app vs external routing, safe download opt-in, and persistent profile.

Qt isn't installed in the CI runner; exercise the exact selected Python methods
with lightweight doubles rather than treating source-search as runtime coverage.
"""
import ast
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from webview_settings import DEFAULTS, read_webview_settings


def source(path):
    return (ROOT / path).read_text(encoding='utf-8')


def method(path, class_name, method_name, extra=None):
    tree = ast.parse(source(path))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    member = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method_name)
    module = ast.fix_missing_locations(ast.Module(body=[member], type_ignores=[]))
    namespace = dict(extra or {})
    exec(compile(module, path, 'exec'), namespace)
    return namespace[method_name]


def test_settings_default_is_embedded_and_persistent_for_existing_launch():
    assert DEFAULTS['mode'] == 'embedded'
    assert DEFAULTS['remember_login'] is True
    assert DEFAULTS['download_directory'] == ''
    assert json.loads(source('config/webview_settings.json'))['mode'] == 'embedded'


def test_external_mode_and_profile_settings_roundtrip(tmp_path):
    file = tmp_path / 'config.json'
    file.write_text(json.dumps({
        'mode': 'external', 'remember_login': False,
        'download_directory': 'D:/Downloads', 'new_tab_url': 'https://www.google.com/'
    }), encoding='utf-8')
    loaded = read_webview_settings(file)
    assert loaded['mode'] == 'external'
    assert loaded['remember_login'] is False
    assert loaded['download_directory'] == 'D:/Downloads'
    file.write_text('{"mode":"bad", "remember_login":"false", "download_directory":5}', encoding='utf-8')
    assert read_webview_settings(file) == DEFAULTS


def test_external_mode_skips_web_engine_at_main_launcher():
    func = method('src/app.py', 'Launcher', 'open_bookmark_web_view',
                  {'bookmark_web_url': lambda row: row['url']})
    obj = SimpleNamespace(webview_settings={'mode':'external'},
                          expanded_view=SimpleNamespace(isVisible=lambda: True,
                                                        is_bookmark_row=lambda row: True,
                                                        show_web_url=lambda url: 1/0))
    assert func(obj, {'url':'https://example.org/'}) is False
    obj.webview_settings['mode'] = 'embedded'
    obj.expanded_view.show_web_url = lambda url: url == 'https://example.org/'
    assert func(obj, {'url':'https://example.org/'}) is True


def test_external_webview_guard_before_lazy_import():
    func = method('src/expanded_view.py', 'ExpandedLauncherView', 'show_web_url')
    obj = SimpleNamespace(launcher=SimpleNamespace(webview_settings={'mode':'external'}))
    assert func(obj, 'https://example.org/') is False


def test_wheel_selection_never_opens_external_browser():
    func = method('src/expanded_view.py', 'ExpandedLauncherView', 'preview_selected_bookmark')
    obj = SimpleNamespace(launcher=SimpleNamespace(webview_settings={'mode':'external'}))
    assert func(obj) is None
    selection = method('src/expanded_view.py', 'ExpandedLauncherView', 'schedule_web_bookmark_preview')
    class Timer:
        stopped = False
        started = False
        def stop(self): self.stopped = True
        def start(self): self.started = True
    timer = Timer()
    obj = SimpleNamespace(_web_selection_timer=timer, _refreshing=False,
                          isVisible=lambda:True,
                          launcher=SimpleNamespace(webview_settings={'mode':'external'}))
    assert selection(obj, object(), None) is None
    assert timer.stopped and not timer.started


def test_external_bookmark_click_delegates_original_browser_profile():
    choose = method('src/expanded_view.py', 'ExpandedLauncherView', 'choose_bookmark')
    opens = []
    row = {'item_kind':'command', 'launch_actions':[{
        'launch_action_type':'Open', 'launch_target':'https://example.org/',
        'launch_browser':'chrome', 'launch_browser_profile':'Profile 3'}]}
    obj = SimpleNamespace(row_data=lambda item:row,
                          is_bookmark_row=lambda row: True,
                          _web_selection_timer=SimpleNamespace(stop=lambda:None),
                          show_web_url=lambda url:False,
                          launcher=SimpleNamespace(open_target=lambda *args: opens.append(args)))
    choose(obj, object(), 0)
    assert opens == [('https://example.org/', 'chrome', 'Profile 3')]


def test_v45_download_is_automatic_without_save_dialog(tmp_path):
    from launch_downloads import safe_download_name, unique_path
    download = method('src/launch_web_view.py', 'LaunchWebView', '_download_requested',
                      {'Path': Path, 'safe_download_name': safe_download_name,
                       'unique_path':unique_path})
    events=[]
    class Signal:
        def connect(self, callback): events.append('connect')
    req=SimpleNamespace(suggestedFileName=lambda:'report.zip', downloadFileName=lambda:'',
                        setDownloadDirectory=lambda d:events.append(('directory',d)),
                        setDownloadFileName=lambda n:events.append(('name',n)),
                        stateChanged=Signal(), receivedBytesChanged=Signal(),
                        totalBytesChanged=Signal(), accept=lambda:events.append('accept'))
    class Owner:
        _downloads=[]
        _downloads_folder=''
        _download_popup=None
        def default_download_folder(self): return str(tmp_path)
        def _update_download_button(self): events.append('update')
        def _on_download_state(self, record): pass
    obj=Owner()
    download(obj,req)
    assert events.index('accept') > events.index(('name','report.zip'))
    assert events.index('accept') > events.index(('directory',str(tmp_path)))
    assert obj._downloads[0]['path'] == str(tmp_path/'report.zip')
    assert obj._downloads_folder == str(tmp_path)


def test_profile_is_named_disk_based_and_shared_by_all_tabs():
    s=source('src/launch_web_view.py')
    assert "QWebEngineProfile('FRBLaunchWeb', QApplication.instance())" in s
    assert 'profile.setPersistentStoragePath(str(data_dir))' in s
    assert 'profile.setCachePath(str(cache_dir))' in s
    assert 'PersistentCookiesPolicy.ForcePersistentCookies' in s
    assert 'QWebEngineProfile(QApplication.instance())  # intentionally off-the-record' in s
    assert 'view.setPage(QWebEnginePage(self.profile, view))' in s
    assert 'self.profile.downloadRequested.connect(self._download_requested)' in s
    assert 'QFileDialog.getSaveFileName(' not in s
    assert 'unique_path(directory, suggested, reserved=in_use)' in s
    assert "self.downloads_button.setObjectName('launchWebDownloads')" in s
    assert "self.show_downloads_menu" in s
    assert 'request.cancel()' in s
    assert 'request.accept()' in s


def test_external_mode_does_not_create_embedded_view_or_show_live_preview():
    expanded=source('src/expanded_view.py')
    assert "if self.launcher.webview_settings.get('mode') != 'embedded':" in expanded
    assert "return  # Wheel selection must never launch an external browser." in expanded
    launcher=source('src/app.py')
    assert "if self.webview_settings.get('mode') != 'embedded':" in launcher
    assert 'if self.open_bookmark_web_view(row):' in launcher
    assert 'self.launcher.open_target(' in expanded  # manual bookmark activation retained
    assert 'from launch_web_view import LaunchWebView' in expanded  # only in lazy path


def test_syntax_all_edited_files():
    for file in ['src/launch_web_view.py', 'src/expanded_view.py', 'src/app.py', 'src/webview_settings.py']:
        ast.parse(source(file), filename=file)
