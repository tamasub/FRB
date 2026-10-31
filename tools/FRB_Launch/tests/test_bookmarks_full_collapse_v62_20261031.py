"""v62: Bookmarks can collapse to zero width and restore their state.

Pure Python checks run without Qt; Windows/PySide6 UI must be validated on device.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
import sys

ROOT = Path(__file__).resolve().parents[1] / 'src'
EXP = (ROOT / 'expanded_view.py').read_text(encoding='utf-8')
WEB = (ROOT / 'launch_web_view.py').read_text(encoding='utf-8')
ICON = (ROOT / 'browser_nav_icons.py').read_text(encoding='utf-8')
APP = (ROOT / 'app.py').read_text(encoding='utf-8')
sys.path.insert(0, str(ROOT))
from remote_navigation import navigation_order, next_area, previous_area, starting_area


def method_ast(name):
    module = ast.parse(EXP)
    view = next(cls for cls in module.body if isinstance(cls, ast.ClassDef) and cls.name == 'ExpandedLauncherView')
    return next(node for node in view.body if isinstance(node, ast.FunctionDef) and node.name == name)


def test_nav_button_is_before_back_and_is_outline_not_colored():
    assert WEB.index("self.show_bookmarks_button = self._nav_button(") < WEB.index("self.back = self._nav_button(")
    assert "'bookmark_outline'" in WEB
    assert "elif name == 'bookmark_outline':" in ICON
    assert 'self.show_bookmarks_button.setEnabled(not visible)' in WEB
    assert 'self.show_bookmarks_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)' in WEB


def test_bookmark_close_button_in_right_header_and_no_focus():
    assert 'self.right.header.layout().insertWidget(2, self.bookmark_close_button)' in EXP
    assert 'self.bookmark_close_button.clicked.connect(self.hide_browser_bookmarks)' in EXP
    assert "self.bookmark_close_button.setIcon(browser_navigation_icon(" in EXP


def test_show_hide_uses_existing_splitter_and_preserves_web_view():
    code = ast.unparse(method_ast('set_browser_bookmarks_visible'))
    assert 'self.right.hide()' in code and 'self.right.show()' in code
    assert 'self.splitter.setSizes(widths)' in code
    assert 'self.web_view.set_bookmarks_visible(visible)' in code
    assert "self.launcher.settings.setValue('browser_bookmarks_visible', visible)" in code
    assert not any(name in code for name in ('deleteLater', 'removeWidget', 'add_tab(', 'show_url(', 'reload_page('))


def test_browser_switch_does_not_force_bookmark_back_open():
    code = ast.unparse(method_ast('_activate_browser_layout'))
    assert "visible = getattr(self, '_browser_bookmarks_visible', True)" in code
    assert 'if visible:' in code and 'self.right.show()' in code
    assert 'self.right.hide()' in code
    assert "settings.setValue" not in code
    assert "'browser_bookmarks_visible', True" in EXP


def test_bookmark_hidden_skips_remote_tab_order():
    visible = navigation_order(web=True, web_tab_count=2)
    hidden = navigation_order(web=True, web_tab_count=2, bookmarks_visible=False)
    assert visible[-3:] == ('bookmarks', 'web_body:0', 'web_body:1')
    assert hidden[-2:] == ('web_body:0', 'web_body:1')
    assert 'bookmarks' not in hidden
    assert next_area('workspace_browser', web=True, web_tab_count=2, bookmarks_visible=False) == 'web_body:0'
    assert previous_area('web_body:0', web=True, web_tab_count=2, bookmarks_visible=False) == 'workspace_browser'
    assert starting_area('search', web=True, web_tab_count=2, bookmarks_visible=False) == 'web_body:0'
    assert 'bookmarks_visible=view.browser_bookmarks_visible' in APP


def test_collapsing_model_with_stubs_updates_widgets_settings_and_remote():
    """Run the real method body with Qt-independent tiny widget stubs."""
    class Panel:
        def __init__(self): self.visible = True
        def isVisible(self): return self.visible
        def show(self): self.visible = True
        def hide(self): self.visible = False
    class Splitter:
        def __init__(self): self.values=[230, 670]
        def sizes(self): return list(self.values)
        def setSizes(self, values): self.values = list(values)
    class Web:
        def set_bookmarks_visible(self, value): self.visible = value
    class Settings:
        def __init__(self): self.data={}
        def setValue(self, key, value): self.data[key]=value
        def sync(self): pass
    class Root:
        def refresh_underline(self): pass
    class Launcher:
        def __init__(self):
            self.settings=Settings();self._remote_area='bookmarks';self.remote_window=object()
            self.moves=[]
        def _current_web_body_area(self): return 'web_body:0'
        def remote_focus_area(self, area): self.moves.append(area)
    class View:
        pass
    node=method_ast('set_browser_bookmarks_visible')
    # Compile just the original method, not a reimplementation.
    fn=ast.FunctionDef(name='run', args=node.args, body=node.body, decorator_list=[], returns=None, type_comment=None)
    mod=ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    ns={}
    exec(compile(mod, filename='expanded_view.py', mode='exec'),ns)
    view=View()
    view._workspace_mode='browser';view._browser_bookmarks_visible=True
    view._browser_splitter_sizes=[230,670]
    view.splitter=Splitter();view.right=Panel();view.web_view=Web()
    view._browser_empty_bookmark_button=None
    view.root_widget=Root();view.launcher=Launcher()
    view.cancel_bookmark_hover=lambda:None
    view.cancel_bookmark_pointer_follow=lambda:None
    ns['run'](view, False)
    assert not view.right.isVisible()
    assert view._browser_splitter_sizes==[230,670]
    assert view.web_view.visible is False
    assert view.launcher.settings.data=={'browser_bookmarks_visible':False}
    assert view.launcher.moves==['web_body:0']
    view.splitter.values=[0, 900]
    ns['run'](view, True)
    assert view.right.isVisible() and view.web_view.visible
    assert view.splitter.sizes()==[230,670]
    assert view.launcher.settings.data=={'browser_bookmarks_visible':True}


def test_external_browser_also_has_way_to_reopen_after_restart():
    code = ast.unparse(method_ast('switch_workspace'))
    assert 'self._browser_empty_bookmark_button' in code
    assert 'self._browser_empty_bookmark_button.clicked.connect(self.show_browser_bookmarks)' in code
    assert 'not self._browser_bookmarks_visible' in code
