"""v52: both workspace tabs join the mint surface without a stray line."""
from pathlib import Path
import ast
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from workspace_tab_geometry import workspace_tab_line_segments
from launch_appearance import theme_palette

SRC = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')


def test_line_omits_active_tab_exactly():
    assert workspace_tab_line_segments(400, 15, 100) == [(0, 14), (100, 399)]
    assert workspace_tab_line_segments(400, 100, 205) == [(0, 99), (205, 399)]


def test_line_handles_edges_and_compact_width():
    assert workspace_tab_line_segments(0, 10, 90) == []
    assert workspace_tab_line_segments(50, 0, 55) == []
    assert workspace_tab_line_segments(50, 10, 60) == [(0, 9)]
    assert workspace_tab_line_segments(50, 90, 120) == [(0, 49)]
    assert workspace_tab_line_segments(100, 10, 10) == [(0, 99)]


def test_both_active_tabs_reuse_the_same_mint_header():
    assert 'QPushButton#expandedWorkspaceTab:checked {{background:{hdr};color:{text};' in SRC
    assert 'QPushButton#expandedWorkspaceTab[workspace="browser"]:checked {{background:{hdr};' in SRC
    assert 'QPushButton#expandedWorkspaceTab:checked {{background:{bg};' not in SRC
    assert "self.root_widget.set_underline_color(border)" in SRC


def test_inactive_tabs_muted_and_font_is_slightly_larger():
    assert 'background:{stripe};color:#84998d' in SRC
    assert 'border:1px solid {stripe};border-top-left-radius:12px;' in SRC
    assert 'border-top-right-radius:12px;border-bottom-left-radius:0px;' in SRC
    assert 'font-size:13px;font-weight:400;' in SRC
    assert 'border-bottom-right-radius:0px;border-bottom:0;font-weight:400;' in SRC


def test_strip_is_not_broken_by_view_switches():
    assert "self.root_widget = _WorkspaceTabStrip()" in SRC
    assert 'self.root_widget.set_selected_tab(active)' in SRC
    assert "self.files_content_stack.setCurrentWidget(self.files_group)" in SRC
    assert "self.files_content_stack.setCurrentWidget(self.web_view)" in SRC
    assert "self.root_layout.setContentsMargins(6, 3, 4, 0)" in SRC
    assert 'outer.setSpacing(0)' in SRC


def test_qss_template_is_well_formed_both_themes():
    tree = ast.parse(SRC)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ExpandedLauncherView')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'apply_theme')
    sheet = next(n.args[0] for n in ast.walk(method)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and n.func.attr == 'setStyleSheet' and n.args
                 and isinstance(n.args[0], ast.JoinedStr) and 'expandedWorkspaceTab' in ast.unparse(n.args[0]))
    assert isinstance(sheet, ast.JoinedStr)
    for theme in ('light', 'dark'):
        colors = theme_palette(theme)
        values = dict(colors=colors, bg=colors['panel'], border=colors['panel_border'],
                      hdr=colors['panel_header'], text=colors['text'],
                      hover=colors['hover'], active=colors['selection'],
                      root_border=colors['root_button_border'],
                      height=29, pad=3, stripe=colors['stripe'])
        qss = eval(compile(ast.Expression(body=sheet), '<v52-qss>', 'eval'), {}, values)
        assert qss.count('{') == qss.count('}')
        assert f'background:{colors["panel_header"]};color:{colors["text"]};' in qss
