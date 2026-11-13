"""New Wheel Tab contract: Page terminal; return to current Page; close overlays.

These are Qt-free tests because automated Windows/PySide6 widgets are not
available in this runner. Windows mouse/UI verification is still required.
"""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace

SRC = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC))


def method(filename, classname, method_name):
    source = (SRC / filename).read_text('utf8')
    parsed = ast.parse(source)
    cls = next(n for n in parsed.body if isinstance(n, ast.ClassDef) and n.name == classname)
    item = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method_name)
    return ast.get_source_segment(source, item)


def extract_method(filename, classname, method_name, namespace):
    source = method(filename, classname, method_name)
    exec('class Subject:\n' + '\n'.join('    '+line for line in source.splitlines()), namespace)
    return namespace['Subject']


def test_page_right_is_terminal_no_jump_or_lock():
    text = method('page_tab_focus.py', 'FocusPageTabBar', 'wheelEvent')
    assert 'super().wheelEvent(event)' in text
    assert "feed('pages-right'" not in text
    assert '_zone_right_jump' not in text
    assert 'follow_wheel_tab_pointer' in text
    app = (SRC / 'app.py').read_text('utf8')
    assert '._zone_right_jump' not in app


def test_reverse_second_level_returns_current_page_instead_of_endpoint():
    roots = method('expanded_view.py', 'ExpandedLauncherView', 'wheel_first_level')
    assert "feed('roots-left', at_left, steps)" in roots
    assert "self.zone_jump('pages', position='current')" in roots
    assert "self.zone_jump('pages', position='last')" not in roots
    jump = method('expanded_view.py', 'ExpandedLauncherView', 'zone_jump')
    assert "if position != 'current':" in jump
    follow = method('expanded_view.py', 'ExpandedLauncherView', '_finish_zone_jump')
    assert "tabs.currentIndex() if position == 'current'" in follow


def test_popup_cleanup_actually_dismisses_existing_overlays():
    class Popup:
        def __init__(self, exists): self.exists = exists; self.closed = False
        def isVisible(self): return self.exists
        def close(self): self.closed = True; self.exists = False
    class Launcher:
        def __init__(self):
            self.history_popup = Popup(True)
            self._launch_context_menu = Popup(True)
            self.calls = []
        def hide_history_popup(self): self.calls.append('history'); self.history_popup.exists = False
        def close_cascade_for_main_interaction(self): self.calls.append('cascade')
    ns = {}
    Subject = extract_method('expanded_view.py', 'ExpandedLauncherView', 'close_transients_for_zone_jump', ns)
    class View(Subject):
        def __init__(self):
            self.launcher = Launcher()
            self.favorite_popup = Popup(True)
            self.calls = []
        def cancel_bookmark_hover(self): self.calls.append('hover')
        def cancel_bookmark_pointer_follow(self): self.calls.append('follow')
        def hide_favorite_popup(self): self.calls.append('favorite'); self.favorite_popup.exists = False
    view = View()
    view.close_transients_for_zone_jump()
    assert view.calls == ['hover', 'follow', 'favorite']
    assert view.launcher.calls == ['history', 'cascade']
    assert view.launcher._launch_context_menu.closed
    assert not view.favorite_popup.isVisible()
    assert not view.launcher.history_popup.isVisible()


def test_zone_jump_closes_first_but_preserves_current_tab_and_follows_it():
    actions=[]
    class FakeTab:
        def __init__(self): self.index=2
        def count(self): return 3
        def currentIndex(self): return self.index
        def setCurrentIndex(self,v): actions.append(('set_page',v)); self.index=v
        def setFocus(self,_): actions.append('focus_page')
    tab=FakeTab()
    ns={
        'QCursor': SimpleNamespace(pos=lambda:'cursor'),
        'Qt': SimpleNamespace(FocusReason=SimpleNamespace(TabFocusReason=42)),
        'QTimer': SimpleNamespace(singleShot=lambda n, fn: actions.append('deferred_warp')),
    }
    Subject = extract_method('expanded_view.py', 'ExpandedLauncherView', 'zone_jump', ns)
    class View(Subject):
        launcher=SimpleNamespace(tabs=tab)
        def close_transients_for_zone_jump(self): actions.append('close_overlays')
    View().zone_jump('pages', 'current')
    assert tab.index == 2
    assert actions == ['close_overlays','focus_page','deferred_warp']


def test_zone_jump_rejects_missing_destination_before_closing_overlay():
    actions=[]
    ns={
        'QCursor': SimpleNamespace(pos=lambda:'cursor'),
    }
    Subject=extract_method('expanded_view.py', 'ExpandedLauncherView','zone_jump',ns)
    class View(Subject):
        launcher=SimpleNamespace(tabs=SimpleNamespace(count=lambda:0))
        def close_transients_for_zone_jump(self): actions.append('close_overlays')
    View().zone_jump('pages','current')
    assert actions==[]
