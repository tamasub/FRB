"""Executable, Qt-free contracts for the breadcrumb's pending-path apply arrow."""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace

SRC = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC))
from directory_address import pending_directory_change

TEXT = (SRC / 'expanded_view.py').read_text(encoding='utf-8')
MODULE = ast.parse(TEXT)


def method(klass, name):
    owner = next(n for n in MODULE.body if isinstance(n, ast.ClassDef) and n.name == klass)
    node = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == name)
    ns = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'extracted', 'exec'), ns)
    return ns[name]


class Editor:
    def __init__(self, value):
        self.value = value
        self.margins = None
    def text(self):
        return self.value
    def setTextMargins(self, *args):
        self.margins = args


class Apply:
    def __init__(self):
        self.visible = None
        self.tooltip = ''
    def setVisible(self, value):
        self.visible = value
    def setToolTip(self, text):
        self.tooltip = text


class Address:
    _update_apply_visibility = method('DirectoryAddressBar', '_update_apply_visibility')
    def __init__(self, current, candidate, editing):
        self.current_path = current
        self.editor = Editor(candidate)
        self.surface = object()
        self.active = self.editor if editing else self.surface
        self._overlay_apply = Apply()
    def currentWidget(self):
        return self.active


def test_pending_path_is_case_insensitive_and_normalized_on_windows():
    assert not pending_directory_change('F:/FRB/tools/', 'f:\\frb\\tools')
    assert not pending_directory_change('F:\\FRB', 'F:\\FRB')
    assert pending_directory_change('F:\\FRB\\docs', 'F:\\FRB')
    assert pending_directory_change('F:\\FRB', '')
    assert not pending_directory_change('not-absolute', 'F:\\FRB')
    assert not pending_directory_change('', 'F:\\FRB')


def test_favorite_wheel_preview_shows_arrow_only_if_path_differs():
    demo = Address('F:\\FRB\\live', 'F:\\FRB\\docs', editing=True)
    demo._update_apply_visibility()
    assert demo._overlay_apply.visible is True
    assert demo.editor.margins == (0, 0, 91, 0)
    assert 'F:\\FRB\\docs' in demo._overlay_apply.tooltip

    demo.editor.value = 'f:/frb/live/'
    demo._update_apply_visibility()
    assert demo._overlay_apply.visible is False
    assert demo.editor.margins == (0, 0, 60, 0)


def test_hidden_in_breadcrumb_mode_even_when_editor_has_pending_text():
    demo = Address('F:\\FRB\\live', 'F:\\FRB\\docs', editing=False)
    demo._update_apply_visibility()
    assert demo._overlay_apply.visible is False


def test_invalid_candidate_not_executable_and_clear_restores_state():
    demo = Address('F:\\FRB\\live', 'relative-folder', editing=True)
    demo._update_apply_visibility()
    assert demo._overlay_apply.visible is False
    demo.editor.value = 'F:\\FRB\\docs'
    demo._update_apply_visibility()
    assert demo._overlay_apply.visible is True
    demo.current_path = 'F:\\FRB\\docs'  # navigation has been committed
    demo.active = demo.surface
    demo._update_apply_visibility()
    assert demo._overlay_apply.visible is False


def test_apply_is_left_of_heart_and_connected_to_enter_submission():
    init = ast.get_source_segment(TEXT, next(n for n in next(
        k for k in MODULE.body if isinstance(k, ast.ClassDef) and k.name == 'ExpandedLauncherView'
    ).body if isinstance(n, ast.FunctionDef) and n.name == '__init__'))
    position = ast.get_source_segment(TEXT, next(n for n in next(
        k for k in MODULE.body if isinstance(k, ast.ClassDef) and k.name == 'DirectoryAddressBar'
    ).body if isinstance(n, ast.FunctionDef) and n.name == '_position_dropdown'))
    assert 'self.directory_apply.clicked.connect(self.address_bar._submit)' in init
    assert 'self.address_bar.attach_path_apply(self.directory_apply)' in init
    assert 'favorite.x()' in position
    assert 'left_edge - apply.width() - 3' in position


def test_wheel_browse_remains_preview_only_and_refresh_clears_arrow():
    wheel = ast.get_source_segment(TEXT, next(n for n in next(
        k for k in MODULE.body if isinstance(k, ast.ClassDef) and k.name == 'ExpandedLauncherView'
    ).body if isinstance(n, ast.FunctionDef) and n.name == 'wheel_directory_favorite_history'))
    show_crumbs = method('DirectoryAddressBar', 'show_breadcrumbs')
    assert 'bar.editor.setText(paths[index])' in wheel
    assert 'bar._update_apply_visibility()' in wheel
    assert 'self.go_to_directory(' not in wheel
    assert 'self._update_apply_visibility()' in TEXT.split('    def show_breadcrumbs(',1)[1].split('    def _submit(',1)[0]
    assert callable(show_crumbs)
