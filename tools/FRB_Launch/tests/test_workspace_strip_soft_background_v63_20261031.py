"""v63: only the area behind the Files / Browser tabs changes color.

No PySide6 is needed for these source-level regression checks.
"""
import ast
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'expanded_view.py').read_text(encoding='utf-8')


def test_two_workspace_theme_colors_are_soft_but_distinct_from_active_tabs():
    from launch_appearance import theme_palette
    assert theme_palette('light')['workspace_strip'] == '#f3faf6'
    assert theme_palette('dark')['workspace_strip'] == '#2a3b35'
    assert "workspace_strip_bg = colors['workspace_strip']" in SOURCE
    assert 'root_palette.setColor(QPalette.ColorRole.Window, QColor(workspace_strip_bg))' in SOURCE
    assert 'QWidget#expandedRootBar {{background:{colors["workspace_strip"]};border:0;}}' in SOURCE
    assert 'QScrollArea#expandedRootScroller {{background:{colors["workspace_strip"]};border:0;}}' in SOURCE


def test_active_inactive_tab_styles_are_unchanged():
    assert 'QPushButton#expandedWorkspaceTab:checked {{background:{hdr};color:{text};' in SOURCE
    assert 'QPushButton#expandedWorkspaceTab {{background:{stripe};color:#84998d;' in SOURCE
    assert 'QPushButton#expandedWorkspaceTab[workspace="browser"]:checked {{background:{hdr};' in SOURCE


def test_strip_color_is_only_a_local_theme_choice_and_no_tab_logic_changes():
    tree = ast.parse(SOURCE)
    methods = [node for cls in tree.body if isinstance(cls, ast.ClassDef)
               for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
               and node.name == 'apply_theme']
    assert any('workspace_strip_bg' in ast.unparse(method) for method in methods)
    # This change must not affect the Files/Browser selection machinery.
    assert 'self._update_workspace_tabs()' in SOURCE
    assert 'self.files_mode_tab.clicked.connect' in SOURCE
    assert 'self.browser_mode_tab.clicked.connect' in SOURCE


def test_rendered_strip_qss_uses_theme_color_without_changing_selected_fill():
    from launch_appearance import theme_palette
    tree = ast.parse(SOURCE)
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef)
               and node.name == 'ExpandedLauncherView')
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef)
                  and node.name == 'apply_theme')
    sheet = next(call.args[0] for call in ast.walk(method)
                 if isinstance(call, ast.Call)
                 and isinstance(call.func, ast.Attribute)
                 and call.func.attr == 'setStyleSheet'
                 and call.args and isinstance(call.args[0], ast.JoinedStr)
                 and 'expandedWorkspaceTab' in ast.unparse(call.args[0]))
    for theme in ('light', 'dark'):
        colors = theme_palette(theme)
        kwargs = dict(colors=colors, bg=colors['panel'], border=colors['panel_border'],
                      hdr=colors['panel_header'], text=colors['text'],
                      hover=colors['hover'], active=colors['selection'],
                      root_border=colors['root_button_border'],
                      height=29, pad=3, stripe=colors['stripe'])
        qss = eval(compile(ast.Expression(body=sheet), '<v63-workspace-qss>', 'eval'), {}, kwargs)
        assert qss.count('{') == qss.count('}')
        assert f'QWidget#expandedRootBar {{background:{colors["workspace_strip"]};border:0;}}' in qss
        assert f'QScrollArea#expandedRootScroller {{background:{colors["workspace_strip"]};border:0;}}' in qss
        assert f'QPushButton#expandedWorkspaceTab:checked {{background:{colors["panel_header"]};' in qss
        assert colors['workspace_strip'] != colors['panel_header']
