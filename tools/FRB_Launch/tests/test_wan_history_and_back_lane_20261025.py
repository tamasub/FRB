"""Regression checks for the October 25 independent Back lane / history wheel.

These tests run without PySide6: logic, tree structure, and method contracts are
checked from the real source rather than asserting the previous inline-strip.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'src'))
from history_wheel_navigation import history_target_index
from wheel_adaptive import wheel_steps

EXPANDED = (BASE / 'src/expanded_view.py').read_text(encoding='utf-8')
APP = (BASE / 'src/app.py').read_text(encoding='utf-8')


def _method(name, source=EXPANDED, cls='ExpandedLauncherView'):
    module = ast.parse(source)
    parent = next(c for c in module.body if isinstance(c, ast.ClassDef) and c.name == cls)
    method = next(m for m in parent.body if isinstance(m, ast.FunctionDef) and m.name == name)
    ns = {}
    exec(compile(ast.Module(body=[method], type_ignores=[]), 'snippet', 'exec'), ns)
    return ns[name]


def test_history_selected_row_moves_without_wrapping():
    assert history_target_index(0, 7, 1) == 1
    assert history_target_index(3, 7, -2) == 1
    assert history_target_index(6, 7, 3) == 6
    assert history_target_index(0, 7, -1) == 0
    assert history_target_index(-1, 7, -1) == 6
    assert history_target_index(1, 0, 1) == -1
    pending, movement = wheel_steps(0, -240)
    assert pending == 0 and movement == 2


def test_search_field_opens_popup_and_warps_row_without_running_search():
    fn = _method('wheel_search_history', source=APP, cls='Launcher')
    text = ast.get_source_segment(APP, ast.parse(APP).body[0]) if False else APP
    body = APP.split('    def wheel_search_history(', 1)[1].split('    def handle_history_event(', 1)[0]
    assert 'self.show_history_popup()' in body
    assert 'tree.setCurrentItem(target)' in body
    assert 'warp_to_history_row(' in body
    assert 'select_history_keyword(' not in body
    assert 'history_row_clicked(' not in body


def test_favorite_popup_and_address_preview_are_distinct():
    fn = _method('wheel_directory_favorite_history')
    section = EXPANDED.split('    def wheel_directory_favorite_history(', 1)[1].split('    def toggle_directory_favorites(', 1)[0]
    assert 'choices.setCurrentItem(target)' in section
    assert 'warp_to_history_row(' in section
    assert 'bar.editor.setText(paths[index])' in section
    assert 'bar.setCurrentWidget(bar.editor)' in section
    assert 'self.go_to_directory(' not in section
    assert 'self.directory_favorite_clicked(' not in section


def test_middle_back_strip_outside_view_and_not_a_tree_column():
    assert 'self.middle.layout_box.removeWidget(self.middle.tree)' in EXPANDED
    assert 'middle_tree_layout.addWidget(self.middle.tree, 1)' in EXPANDED
    assert 'middle_tree_layout.addWidget(self.middle_back_lane)' in EXPANDED
    assert 'self.middle_back_lane.setFixedWidth(MIDDLE_BACK_LANE_WIDTH)' in EXPANDED
    assert 'self.middle.tree.setColumnWidth(1, 40 + MIDDLE_BACK_LANE_WIDTH)' not in EXPANDED
    assert 'QFrame#expandedBackLane' in EXPANDED
    assert 'return None' in EXPANDED.split('class _NavigationChevronDelegate',1)[1].split('    def paint(',1)[0]


def test_actual_back_handler_accepts_lane_and_blank_but_not_normal_row():
    fn = _method('handle_middle_back_double_click')
    class E:
        def __init__(self, point, kind, mods=0):
            self.point, self.kind, self.mods, self.accepted = point, kind, mods, False
        def type(self): return self.kind
        def button(self): return 1
        def modifiers(self): return self.mods
        def position(self): return SimpleNamespace(toPoint=lambda: self.point)
        def accept(self): self.accepted = True
    class Q:
        class Type:
            MouseButtonPress=1
            MouseButtonRelease=2
            MouseButtonDblClick=3
    class QT:
        class MouseButton: LeftButton=1
        class KeyboardModifier: NoModifier=0
    fn.__globals__.update({'QEvent': Q, 'Qt': QT})
    vp=object();lane=object()
    demo=SimpleNamespace(isVisible=lambda: True,
        middle=SimpleNamespace(tree=SimpleNamespace(viewport=lambda: vp)),
        middle_back_lane=lane,
        middle_blank_back_at=lambda p:p=='blank',
        back_calls=0)
    demo.go_up=lambda: setattr(demo,'back_calls',demo.back_calls+1)
    assert fn(demo,lane,E('row',1))
    assert demo.back_calls==0
    assert fn(demo,lane,E('row',3))
    assert demo.back_calls==1
    assert fn(demo,vp,E('blank',3))
    assert demo.back_calls==2
    assert not fn(demo,vp,E('row',3))
    assert demo.back_calls==2


def test_back_from_single_direct_navigation_goes_to_real_parent():
    fn=_method('go_up')
    class Timer:
        @staticmethod
        def singleShot(delay, callback): callback()
    fn.__globals__.update({'QTimer':Timer, 'directory_row': lambda path:{'title':path}})
    demo=SimpleNamespace(path=[{'title':'F:\\FRB\\project\\data'}],
        current_directory=lambda:'F:\\FRB\\project\\data',
        refresh_count=0, last_focus=None,
        middle='middle', left='left')
    demo.refresh_middle=lambda: setattr(demo,'refresh_count',demo.refresh_count+1)
    demo.focus_panel=lambda target: setattr(demo,'last_focus',target)
    with patch('os.path.isdir', return_value=True):
        fn(demo)
    assert demo.path==[{'title':'F:\\FRB\\project'}]
    assert demo.refresh_count==1
    assert demo.last_focus=='left'


def test_previous_wan_edge_hold_not_changed():
    assert 'if hold is not None and hold.feed(at_first, abs(movement)):' in EXPANDED
    assert 'self.schedule_middle_back_pointer(cursor_global=QCursor.pos())' in EXPANDED
