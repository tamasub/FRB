"""v55 display contract. PySide6 absent from patch environment: source checks only."""
import ast
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXP=(ROOT/'src/expanded_view.py').read_text(encoding='utf-8')
WEB=(ROOT/'src/launch_web_view.py').read_text(encoding='utf-8')


def get_class(name):
    cls=next(x for x in ast.parse(EXP).body if isinstance(x,ast.ClassDef) and x.name==name)
    return {x.name: x for x in cls.body if isinstance(x,ast.FunctionDef)}


def test_selected_tab_and_seam_use_single_continuous_painter_path():
    body=ast.unparse(get_class('_WorkspaceSeamOverlay')['paintEvent'])
    assert 'outline = QPainterPath()' in body
    assert 'outline.cubicTo' in body
    assert body.count('outline.cubicTo') >= 4
    assert 'painter.drawPath(outline)' in body
    assert 'strip._selected_tab' in body
    assert 'strip._end_provider' in body
    assert 'strip._corner_end_provider' in body
    assert 'strip._underline_color' in body
    # Only one actual paint path per frame; old disconnected line strokes gone.
    assert 'painter.drawLine' not in body


def test_painter_is_full_tab_height_and_on_top_of_buttons():
    body=ast.unparse(get_class('_WorkspaceTabStrip')['resizeEvent'])
    assert 'self._seam_overlay.setGeometry(0, 0, self.width(), self.height())' in body
    assert 'self._seam_overlay.raise_()' in ast.unparse(get_class('_WorkspaceTabStrip')['refresh_underline'])
    assert 'WA_TransparentForMouseEvents' in EXP


def test_active_tab_does_not_draw_second_independent_qss_border():
    # Inactive tab still uses its quiet border; active tab is a borderless fill
    # and the overlay draws the stroke in one continuous operation.
    assert 'QPushButton#expandedWorkspaceTab:checked {{background:{hdr};color:{text};\n                border:0;' in EXP
    assert 'QPushButton#expandedWorkspaceTab[workspace="browser"]:checked {{background:{hdr};\n                color:{text};border:0;' in EXP
    assert 'QPushButton#expandedWorkspaceTab[workspace="files"]:!checked' in EXP


def test_top_right_corners_are_drawn_over_header_background():
    cls=get_class('_WorkspaceTopRightOutline')
    paint=ast.unparse(cls['paintEvent'])
    assert 'painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)' in paint
    assert 'curve.cubicTo' in paint
    assert 'painter.drawPath(curve)' in paint
    assert 'self.raise_()' in ast.unparse(cls['update_geometry'])
    # No QPainter calls or geometry changes on the host inside its filter.
    filtr=ast.unparse(cls['eventFilter'])
    assert 'return False' in filtr and 'obj is self._host' in filtr
    assert '_WorkspaceTopRightOutline(self.header)' in EXP
    assert '_WorkspaceTopRightOutline(self.shared_header)' in EXP
    assert 'self._top_right_outline = _WorkspaceTopRightOutline(self)' in WEB
    assert 'self._top_right_outline.set_outline_color(border)' in WEB


def test_light_dark_corner_colors_follow_theme():
    assert 'self._files_top_right_outline.set_outline_color(border)' in EXP
    assert 'self.right._top_right_outline.set_outline_color(border)' in EXP
    assert 'self.root_widget.set_underline_color(border)' in EXP
    assert 'self.root_widget.set_corner_end_provider(' in EXP
    assert 'self._top_right_outline.set_outline_color(border)' in WEB


def test_files_browser_functionality_not_disturbed():
    for mark in (
        'self.files_content_stack.setCurrentWidget(self.files_group)',
        'self.files_content_stack.setCurrentWidget(self.web_view)',
        'self.right.hide()  # Bookmarks belong to Browser, never Files.',
        'self.web_view.add_tab(',
    ):
        assert mark in EXP
