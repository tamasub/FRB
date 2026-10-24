"""Regression contract for the compact header and expanded middle selection.

Uses AST and lightweight fakes so it runs without Qt/Windows on CI.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
VIEW = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')


def _method(source, class_name, method_name, namespace):
    module = ast.parse(source)
    owner = next(n for n in module.body if isinstance(n, ast.ClassDef)
                 and n.name == class_name)
    method = next(n for n in owner.body if isinstance(n, ast.FunctionDef)
                  and n.name == method_name)
    ast_module = ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))
    exec(compile(ast_module, '<isolated method>', 'exec'), namespace)
    return namespace[method_name]


def test_header_no_longer_shares_body_insets():
    assert 'layout.setContentsMargins(6,8,6,12)' in APP
    assert 'layout.addWidget(self.search_bar)' in APP
    assert 'body_layout.setContentsMargins(6, 0, 6, 0)' in APP
    assert 'body_layout.addWidget(w)' in APP
    assert "self.main_body.setObjectName('mainBody')" in APP


def test_top_thin_strip_has_no_resize_zone_but_side_and_bottom_still_do():
    class Rect:
        def contains(self, pt):
            return 0 <= pt.x() < 600 and 0 <= pt.y() < 500

    class Point:
        def __init__(self, x, y): self._x, self._y = x, y
        def x(self): return self._x
        def y(self): return self._y
        def toPoint(self): return self

    method = _method(APP, 'Launcher', 'resize_edge', {})
    w = SimpleNamespace(FRAME_TOP=8, FRAME_WIDTH=6, rect=lambda: Rect(),
                        width=lambda: 600, height=lambda: 500)
    assert method(w, Point(300, 0)) is None
    assert method(w, Point(0, 0)) is None
    assert method(w, Point(599, 7)) is None
    assert method(w, Point(0, 120)) == 'left'
    assert method(w, Point(599, 120)) == 'right'
    assert method(w, Point(300, 499)) == 'bottom'
    assert method(w, Point(0, 499)) == 'bottom-left'


def test_ribbon_downsizes_without_changing_files_folder_icon():
    assert "24 if pane.kind == 'bookmark' else 28" in VIEW
    assert 'self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)' in VIEW


def test_density_uses_large_vector_strokes_not_font_character():
    assert 'self.density_button.setIcon(density_lines_icon(theme))' in VIEW
    assert 'self.density_button.setIconSize(QSize(22, 22))' in VIEW
    assert "self.density_button.setText('')" in VIEW
    assert "self.density_button.setText('☷'" not in VIEW


def test_only_middle_column_has_extended_selection():
    assert 'self.middle.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)' in VIEW
    assert 'self.left.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)' not in VIEW
    assert 'self.right.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)' not in VIEW


def test_modifier_click_never_descends_into_selected_folder():
    mask = SimpleNamespace(ControlModifier=1, ShiftModifier=2)
    Qt = SimpleNamespace(KeyboardModifier=mask)
    state = SimpleNamespace(modifiers=0)
    application = SimpleNamespace(keyboardModifiers=lambda: state.modifiers)
    tasks = []
    timer = SimpleNamespace(singleShot=lambda _, callback: tasks.append(callback))
    choose_middle = _method(VIEW, 'ExpandedLauncherView', 'choose_middle',
                            {'Qt': Qt, 'QApplication': application, 'QTimer': timer})
    item = {'item_kind': 'directory', 'item_id': 'a'}
    view = SimpleNamespace(row_data=lambda x: x, path=[{'item_id': 'parent'}],
                           refresh_middle=lambda: None)
    for modifiers in (1, 2, 3):
        state.modifiers = modifiers
        choose_middle(view, item, 0)
        assert view.path == [{'item_id': 'parent'}]
        assert tasks == []
    state.modifiers = 0
    choose_middle(view, item, 0)
    assert view.path[-1] is item
    assert len(tasks) == 1
