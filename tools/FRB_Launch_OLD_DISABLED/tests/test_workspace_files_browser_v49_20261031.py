"""FRB Launch v49: Files / Browser separation, without PySide6 dependency.

These test contracts include execution of Qt-free method branches via AST,
because the actual Windows GUI must be exercised by the user.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')


def method(name):
    tree = ast.parse(SRC)
    cls = next(c for c in tree.body if isinstance(c, ast.ClassDef)
               and c.name == 'ExpandedLauncherView')
    body = next(fn for fn in cls.body if isinstance(fn, ast.FunctionDef)
                and fn.name == name)
    fn = ast.FunctionDef(name=body.name, args=body.args, body=body.body,
                         decorator_list=[], returns=None, type_comment=None)
    code = compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                   '<v49-extracted>', 'exec')
    scope = {}
    exec(code, scope)
    return scope[name]


class FakeView:
    def __init__(self):
        self.visible = False
        self.show_calls = 0
        self.hide_calls = 0
    def show(self):
        self.visible = True
        self.show_calls += 1
    def hide(self):
        self.visible = False
        self.hide_calls += 1
    def isVisible(self):
        return self.visible


class FakeStack:
    def __init__(self, current=None): self.current = current
    def currentWidget(self): return self.current
    def setCurrentWidget(self, widget): self.current = widget


def test_workspace_tabs_are_before_second_layer_right_aligned():
    init_start = SRC.index('            # Workspaces on the LEFT')
    refresh_end = SRC.index('            self.left.label.setText(', init_start)
    chunk = SRC[init_start:refresh_end]
    assert chunk.index("QPushButton('Files'") < chunk.index("QPushButton('Browser'")
    assert chunk.index('self.root_layout.addStretch(1)') < chunk.index('for index, row in enumerate(visible_roots):')
    assert 'self.root_layout.addWidget(button)' in chunk
    assert "QPushButton#expandedWorkspaceTab:checked" in SRC


def test_files_hides_bookmarks_and_does_not_close_web_tabs():
    calls = []
    right = FakeView(); right.show()
    web = SimpleNamespace(set_remote_area=lambda arg: calls.append(('area', arg)),
                          tabs=SimpleNamespace(count=lambda: 3,
                                               currentIndex=lambda: 2))
    files = object()
    stack = FakeStack(web)
    obj = SimpleNamespace(_web_selection_timer=SimpleNamespace(stop=lambda: calls.append('stop')),
                          _workspace_mode='browser', right=right,
                          splitter=SimpleNamespace(sizes=lambda: [670, 340]),
                          _browser_splitter_sizes=None, web_view=web,
                          files_content_stack=stack, files_group=files,
                          _update_workspace_tabs=lambda: calls.append('tabs'))
    method('show_files_view')(obj)
    assert obj._workspace_mode == 'files'
    assert stack.currentWidget() is files
    assert right.hide_calls == 1 and not right.visible
    assert obj._browser_splitter_sizes == [670, 340]
    assert web.tabs.count() == 3 and web.tabs.currentIndex() == 2
    assert ('area', None) in calls


def test_browser_restores_existing_web_without_reloading_or_new_tab():
    calls = []
    right = FakeView()
    files = object(); web = SimpleNamespace(tabs=SimpleNamespace(count=lambda: 2),
                                            add_tab=lambda *args, **kwargs: calls.append('add'))
    stack = FakeStack(files)
    obj = SimpleNamespace(launcher=SimpleNamespace(webview_settings={'mode':'embedded',
                        'new_tab_url':'https://www.google.com/'}),
                          web_view=web, _ensure_web_view=lambda: True,
                          files_content_stack=stack, _update_workspace_tabs=lambda: calls.append('tabs'),
                          _activate_browser_layout=lambda: calls.append('browser'))
    assert method('switch_workspace')(obj, 'browser') is True
    assert stack.currentWidget() is web
    assert 'add' not in calls
    assert 'browser' in calls


def test_first_browser_tab_is_google():
    urls = []
    web = SimpleNamespace(tabs=SimpleNamespace(count=lambda: 0),
                          add_tab=lambda url: urls.append(url))
    obj = SimpleNamespace(launcher=SimpleNamespace(webview_settings={
                    'mode':'embedded', 'new_tab_url':'https://www.google.com/'}),
                    web_view=web, _ensure_web_view=lambda: True,
                    files_content_stack=FakeStack(),
                    _activate_browser_layout=lambda: None)
    assert method('switch_workspace')(obj, 'browser') is True
    assert urls == ['https://www.google.com/']


def test_browser_layout_restores_right_bookmarks_width():
    sizes = []
    right = FakeView()
    obj = SimpleNamespace(_workspace_mode='files', right=right,
                          _browser_splitter_sizes=[640, 320],
                          splitter=SimpleNamespace(setSizes=lambda v: sizes.append(v)),
                          launcher=SimpleNamespace(web_view_activated=lambda: None),
                          _update_workspace_tabs=lambda: None)
    method('_activate_browser_layout')(obj)
    assert obj._workspace_mode == 'browser'
    assert right.visible and sizes == [[640, 320]]


def test_bookmark_wheel_highlight_never_opens_url():
    assert 'currentItemChanged.connect(self.schedule_web_bookmark_preview)' not in SRC
    selection = method('schedule_web_bookmark_preview')
    marker = []
    obj = SimpleNamespace(_web_selection_timer=SimpleNamespace(stop=lambda: marker.append('stop')),
                          show_web_url=lambda url: 1/0)
    assert selection(obj, object(), None) is None
    assert marker == ['stop']
    assert method('preview_selected_bookmark')(obj) is None


def test_bookmark_click_and_keyboard_right_are_explicit():
    assert 'self.right.tree.itemClicked.connect(self.choose_bookmark)' in SRC
    assert "if key == Qt.Key.Key_Right:" in APP
    start = APP.index('    def expanded_tree_key(')
    end = APP.index('\n    def ', start+8)
    assert 'view.launcher.activate(row)' in APP[start:end]
    assert 'if self.open_bookmark_web_view(row):' in APP
    assert "self.choose_bookmark(item, 0, force=True)" in SRC


def test_external_mode_does_not_create_qwebengine():
    obj = SimpleNamespace(launcher=SimpleNamespace(webview_settings={'mode':'external'}))
    assert method('show_web_url')(obj, 'https://example.com') is False
    chunk = SRC[SRC.index('    def switch_workspace('):SRC.index('    def show_web_url(')]
    assert "if self.launcher.webview_settings.get('mode') != 'embedded':" in chunk
    assert '_browser_empty_page' in chunk


def test_home_remains_files_and_browser_tabs_survive():
    assert 'view.show_files_view()' in APP[APP.index('    def navigate_home('):]
    chunk = SRC[SRC.index('    def show_files_view('):SRC.index('    def web_view_active(')]
    assert 'close_tab' not in chunk
    assert 'self.right.hide()' in chunk
