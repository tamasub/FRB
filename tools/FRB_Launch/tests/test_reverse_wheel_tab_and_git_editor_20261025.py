"""Reverse Wheel Tab and wide ZIP Git dialog regression checks (Qt-free)."""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))
from wheel_zone_navigation import WheelZoneNavigation
from wheel_adaptive import wheel_steps


def method_text(filename, cls, name):
    source = (SRC / filename).read_text(encoding='utf8')
    tree = ast.parse(source)
    obj = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
    func = next(n for n in obj.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(source, func)


def test_backward_routes_include_last_endpoints_and_back_button():
    body = (SRC / 'expanded_view.py').read_text('utf8')
    first_roots = method_text('expanded_view.py', 'ExpandedLauncherView', 'wheel_first_level')
    assert "self.zone_jump('pages', position='last')" in first_roots
    assert 'self._reverse_zone_entry' in first_roots
    for method, edge, target in (
        ('wheel_bookmarks_at_edge', 'bookmarks-first', 'directory'),
        ('wheel_bookmarks_first_level', 'bookmarks-first', 'directory'),
        ('wheel_files_at_edge', 'files-first', 'roots'),
    ):
        code = method_text('expanded_view.py', 'ExpandedLauncherView', method)
        assert edge in code
        assert f"self.zone_jump('{target}', position='last')" in code
    code = method_text('expanded_view.py', 'ExpandedLauncherView', 'wheel_middle_at_edge')
    assert "navigator.feed('directory-first', at_first" in code
    assert "self.zone_jump('back')" in code
    code = method_text('expanded_view.py', 'ExpandedLauncherView', 'wheel_back_button')
    assert "feed('back-up', movement < 0" in code
    assert "self.zone_jump('files', position='last')" in code
    assert 'self.middle.back.installEventFilter(self)' in body
    assert 'self.middle.back.setFocusPolicy(Qt.FocusPolicy.StrongFocus)' in body


def test_zone_jump_focus_and_pointer_for_last_destinations():
    code = method_text('expanded_view.py', 'ExpandedLauncherView', 'zone_jump')
    assert "position='first'" in code
    assert "tree.topLevelItem(tree.topLevelItemCount() - 1)" in code
    assert 'tabs.setCurrentIndex(tabs.count() - 1 if last else 0)' in code
    assert 'self.middle.back.setFocus' in code
    done = method_text('expanded_view.py', 'ExpandedLauncherView', '_finish_zone_jump')
    assert "button = self.middle.back" in done
    assert "tabs.tabRect(tabs.count()-1 if last else 0).center()" in done
    assert 'QCursor.pos() != source' in done
    assert 'QCursor.setPos(destination)' in done
    assert 'self.middle.back.click(' not in done and 'go_up(' not in done


def test_actual_back_wheel_triggers_after_hold_not_immediately():
    method_src = method_text('expanded_view.py', 'ExpandedLauncherView', 'wheel_back_button')
    ns = {
        'Qt': SimpleNamespace(KeyboardModifier=SimpleNamespace(NoModifier=0),
                              MouseButton=SimpleNamespace(NoButton=0)),
        'QApplication': SimpleNamespace(mouseButtons=lambda: 0),
        'wheel_steps': wheel_steps,
    }
    exec('class TestWidget:\n' + '\n'.join('    ' + line for line in method_src.splitlines()), ns)
    now = [0.]
    class Widget(ns['TestWidget']):
        def __init__(self):
            self._wheel_back_delta = 0
            self.wheel_zone_navigation = WheelZoneNavigation(clock=lambda: now[0])
            self.moves = []
        def isVisible(self): return True
        def zone_jump(self, name, position='first'): self.moves.append((name, position))
    class Event:
        def __init__(self, value): self.value = value
        def angleDelta(self): return SimpleNamespace(y=lambda: self.value)
        def pixelDelta(self): return SimpleNamespace(y=lambda: 0)
        def modifiers(self): return 0
    widget = Widget()
    assert widget.wheel_back_button(Event(120))
    assert widget.moves == []  # UP is a negative row movement.
    now[0] = .26
    widget.wheel_back_button(Event(120))
    now[0] = .52
    widget.wheel_back_button(Event(120))
    assert widget.moves == [('files', 'last')]
    widget.wheel_back_button(Event(120))
    assert len(widget.moves) == 1


def test_reverse_hops_require_quiet_between_regions():
    t = [0.]
    nav = WheelZoneNavigation(clock=lambda: t[0])
    for n in range(3):
        t[0] = n * .25
        fired = nav.feed('bookmarks-first', True, 1)
    assert fired
    t[0] = .55
    assert not nav.feed('directory-first', True, 10)
    assert nav.wheel_is_locked()
    t[0] = 1.5
    assert not nav.wheel_is_locked()


def test_git_editor_width_applies_to_real_editor_not_outer_dialog_only():
    code = method_text('app.py', 'Launcher', 'git_commit_using_filename')
    assert 'dialog = QDialog(self)' in code
    assert 'message_editor = QLineEdit(dialog)' in code
    assert 'message_editor.setMinimumWidth(510)' in code
    assert 'dialog.resize(720' in code
    assert 'message = message_editor.text()' in code
    assert 'QInputDialog(' not in code
