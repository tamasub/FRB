"""Single-column Files A/B mode, including Remote Browser no-bookmark rule.

Qt-free behavioral tests for UI branches so CI need not run PySide6 on Windows.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
VIEW = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
REMOTE = (ROOT / 'src/launch_remote.py').read_text(encoding='utf-8')


def method(source, klass, name):
    tree = ast.parse(source)
    cls = next(c for c in tree.body if isinstance(c, ast.ClassDef) and c.name == klass)
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    standalone = ast.FunctionDef(name=node.name, args=node.args, body=node.body,
                                 decorator_list=[], returns=None, type_comment=None)
    scope = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[standalone], type_ignores=[])),
                 f'<{klass}.{name}>', 'exec'), scope)
    return scope[name]


class Widget:
    def __init__(self, visible=False):
        self.visible = visible
        self.events = []
    def show(self):
        self.visible = True
        self.events.append('show')
    def hide(self):
        self.visible = False
        self.events.append('hide')
    def isVisible(self):
        return self.visible
    def setVisible(self, visible):
        self.show() if visible else self.hide()
    def setEnabled(self, enabled):
        self.events.append(('enabled', enabled))


def test_fixed_files_exp_drops_obsolete_toggle_but_keeps_desktop_option():
    assert "'実験：Files ルート非表示'" not in APP
    assert 'self.files_root_hidden_mode = True' in APP
    assert "'デスクトップダブルクリックでリモコンを表示'" in APP
    assert "'実験：デスクトップダブルクリックでリモコンを表示'" not in APP
    assert "'experiment_files_root_hidden'" in APP


def test_remote_buttons_hidden_but_reversible():
    assert "self.backtab_button.setVisible(not enabled)" in REMOTE
    assert "self.tab_button.setVisible(not enabled)" in REMOTE
    assert "if command in ('TAB', 'BACKTAB') and self.files_root_hidden_mode:" in APP
    # Native Browser HTML Tab still belongs to the Web page.
    assert 'web_keyboard_tab' in APP


def test_browser_remote_choice_never_reopens_bookmarks_in_experiment():
    calls = []
    view = SimpleNamespace(
        isVisible=lambda: True,
        switch_workspace=lambda target: calls.append(('switch', target)) or True,
        set_browser_bookmarks_visible=lambda value, persist=True: calls.append(('visible', value, persist)),
        browser_bookmarks_visible=False,
        show_browser_bookmarks=lambda: calls.append('SHOW_BOOKMARKS'))
    launcher = SimpleNamespace(
        isVisible=lambda: True,
        isMinimized=lambda: False,
        expanded_view=view,
        files_root_hidden_mode=True,
        _current_web_body_area=lambda: 'web_body:0',
        remote_focus_area=lambda area: calls.append(('focus', area)))
    method(APP, 'Launcher', 'remote_command')(launcher, 'WORKSPACE_BROWSER')
    assert calls == [('switch', 'browser'), ('visible', False, False), ('focus', 'web_body:0')]


def test_browser_remote_choice_restores_old_auto_show_when_mode_disabled():
    calls = []
    view = SimpleNamespace(
        isVisible=lambda: True,
        switch_workspace=lambda target: calls.append(('switch', target)) or True,
        browser_bookmarks_visible=False,
        show_browser_bookmarks=lambda: calls.append('SHOW_BOOKMARKS'))
    launcher = SimpleNamespace(
        isVisible=lambda: True,
        isMinimized=lambda: False,
        expanded_view=view,
        files_root_hidden_mode=False,
        remote_focus_area=lambda area: calls.append(('focus', area)))
    method(APP, 'Launcher', 'remote_command')(launcher, 'WORKSPACE_BROWSER')
    assert calls == [('switch', 'browser'), 'SHOW_BOOKMARKS', ('focus', 'bookmarks')]


def test_webview_bookmarks_show_request_cannot_override_experiment():
    calls = []
    class Settings:
        def setValue(self, *args): calls.append(('persist', args))
        def sync(self): calls.append('sync')
    right = Widget(False)
    btn = Widget(True)
    view = SimpleNamespace(
        launcher=SimpleNamespace(files_root_hidden_mode=True, settings=Settings(),
                                 _remote_area=None, remote_window=None),
        _workspace_mode='browser', right=right,
        _browser_bookmarks_visible=False,
        _browser_splitter_sizes=None,
        splitter=SimpleNamespace(sizes=lambda: [250, 800]),
        web_view=SimpleNamespace(set_bookmarks_visible=lambda visible: calls.append(('web', visible))),
        _browser_empty_bookmark_button=btn,
        cancel_bookmark_hover=lambda: None, cancel_bookmark_pointer_follow=lambda: None,
        root_widget=SimpleNamespace(refresh_underline=lambda: None))
    method(VIEW, 'ExpandedLauncherView', 'set_browser_bookmarks_visible')(view, True)
    assert view._browser_bookmarks_visible is False
    assert not right.isVisible()
    assert not btn.isVisible()
    assert ('web', False) in calls
    assert not any(x == 'sync' or isinstance(x, tuple) and x[0] == 'persist' for x in calls)


def test_files_workspace_hides_only_first_column_in_experiment():
    left = Widget(True)
    right = Widget(True)
    calls = []
    stack = SimpleNamespace(setCurrentWidget=lambda widget: calls.append(('widget', widget)))
    launcher = SimpleNamespace(files_root_hidden_mode=True, expanded_view=object())
    view = SimpleNamespace(
        launcher=launcher, _web_selection_timer=SimpleNamespace(stop=lambda: None),
        _workspace_mode='files', right=right, left=left,
        web_view=None, files_content_stack=stack, files_group='file-list',
        _update_workspace_tabs=lambda: None)
    method(VIEW, 'ExpandedLauncherView', 'show_files_view')(view)
    assert not left.isVisible() and not right.isVisible()
    assert ('widget', 'file-list') in calls


def test_left_arrow_stops_at_column_two_when_already_first_row():
    first = object()
    class Tree:
        def topLevelItemCount(self): return 1
        def topLevelItem(self, index): return first
        def currentItem(self): return first
    focus = []
    middle = SimpleNamespace(tree=Tree())
    view = SimpleNamespace(middle=middle, launcher=SimpleNamespace(files_root_hidden_mode=True),
                           row_data=lambda item: {'item_kind': 'directory'},
                           focus_panel=lambda p: focus.append(p))
    assert method(VIEW, 'ExpandedLauncherView', 'navigate_left_from_middle')(view) == 'directory'
    assert focus == [middle]


def test_files_home_focuses_second_column_in_experiment():
    # Hidden-first-column mode (without an active Files Exp model) must keep
    # the original fallback: preview the first authored row in column 2.
    calls = []
    first = object()
    left = SimpleNamespace(tree=SimpleNamespace(
        topLevelItem=lambda index: first,
        setCurrentItem=lambda item: calls.append('select-legacy')))
    view = SimpleNamespace(isVisible=lambda: True,
                           show_files_view=lambda: calls.append('files'),
                           left=left,
                           choose_files=lambda *_: calls.append('choose'))
    launcher = SimpleNamespace(data=[1], pages=[1], expanded_view=view,
                               files_exp_embedded_mode=False,
                               files_root_hidden_mode=True, remote_window=None,
                               remote_focus_area=lambda area: calls.append(('focus', area)))
    method(APP, 'Launcher', 'navigate_home')(launcher)
    assert calls == ['files', 'select-legacy', 'choose', ('focus', 'directory')]


def test_experiment_preserves_original_splitter_sizes_and_bookmark_prefs():
    assert "if getattr(self.launcher, 'files_root_hidden_mode', False):\n            return" in VIEW
    assert 'persist = False  # The experiment must not overwrite user preferences.' in VIEW
    assert "_files_root_saved_bookmarks" in VIEW
    assert "_files_root_saved_sizes" in VIEW
