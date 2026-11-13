"""v56: Files tab strip has a mint backing; folder panes do not double header lines.

Source-level tests are intentionally GUI-free, so they can run on hosts without
PySide6. The actual Windows result remains an application-level visual check.
"""
import ast
from pathlib import Path

CODE = (Path(__file__).resolve().parents[1] / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
MODULE = ast.parse(CODE)


def _apply_theme():
    cls = next(n for n in MODULE.body if isinstance(n, ast.ClassDef)
               and n.name == 'ExpandedLauncherView')
    return next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'apply_theme')


def _css_values():
    from launch_appearance import theme_palette
    fn = _apply_theme()
    calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and n.func.attr == 'setStyleSheet'
             and n.args and isinstance(n.args[0], ast.JoinedStr)]
    main = next(call for call in calls if 'expandedRootBar' in ast.unparse(call.args[0]))
    for theme in ('light', 'dark'):
        colors = theme_palette(theme)
        args = {**colors, 'bg':colors['panel'], 'hdr':colors['panel_header'],
                'border':colors['panel_border'], 'root_border':colors['root_button_border'],
                'text':colors['text'], 'hover':colors['hover'], 'active':colors['selection'],
                'stripe':colors['stripe'], 'height':29, 'pad':3}
        yield colors, eval(compile(ast.Expression(main.args[0]), '<files-qss-v56>', 'eval'), {}, args)


def test_qss_uses_mint_surface_behind_both_workspace_corners():
    for c, css in _css_values():
        assert f'QWidget#expandedRootBar {{background:{c["panel_header"]};border:0;}}' in css
        assert f'QScrollArea#expandedRootScroller {{background:{c["panel_header"]};border:0;}}' in css
        assert f'QFrame#expandedFilesGroup {{background:{c["panel_header"]};border:0;' in css
        assert css.count('{') == css.count('}')


def test_scroll_viewport_uses_matching_theme_palette():
    method = ast.unparse(_apply_theme())
    assert 'self.toolbar_scroller.viewport()' in method
    assert 'root_viewport.setAutoFillBackground(True)' in method
    assert 'root_palette.setColor(QPalette.ColorRole.Window, QColor(hdr))' in method
    assert 'root_viewport.setPalette(root_palette)' in method


def test_folder_panes_have_no_duplicate_top_border_but_keep_sides():
    for _, css in _css_values():
        start = css.index('QFrame#expandedPanel[panelKind="folder"] {')
        end = css.index('}', start)
        rule = css[start:end]
        assert 'border-top:0;' in rule
        assert 'border:1px solid' in rule
        assert 'border-top-left-radius:0;' in rule
        assert 'border-top-right-radius:0;' in rule
        # The shared header keeps the one separator line.
        assert 'QWidget#expandedCombinedHeader {' in css
        assert 'border-bottom:1px solid' in css
        # Bookmark panel retains its separate specification.
        assert 'QFrame#expandedPanel[panelKind="bookmark"] {' in css
