"""v53: attached workspace seam, file corner, web corner and bookmark top.

Tests are deliberately source/geometry based because PySide6 is not installed
in the patch build environment; do not claim a Windows rendering test.
"""
import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from workspace_tab_geometry import workspace_tab_line_segments
from launch_appearance import theme_palette

EXP = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
WEB = (ROOT / 'src' / 'launch_web_view.py').read_text(encoding='utf-8')


def test_active_browser_underline_does_not_hide_inactive_files_line():
    # Browser is selected at x 101..195; Files occupies x 6..90.
    assert workspace_tab_line_segments(700, 101, 195) == [(0, 100), (195, 699)]
    # The overlay is on top of the tab QSS painted by Qt, unlike the old
    # parent paintEvent which could be hidden behind the button.
    assert 'class _WorkspaceSeamOverlay(QWidget)' in EXP
    assert 'self._seam_overlay.raise_()' in EXP
    assert 'WA_TransparentForMouseEvents' in EXP
    assert 'self._seam_overlay.setGeometry(' in EXP


def test_browser_line_ends_before_bookmarks_not_across_it():
    # Limit to the left Web pane's width; the bookmark header is separate.
    assert workspace_tab_line_segments(700, 101, 195) == [(0, 100), (195, 699)]
    assert 'self.root_widget.set_underline_end_provider(' in EXP
    assert "self.right.mapTo(self.root_widget, QPoint(0, 0)).x()" in EXP
    assert "self._workspace_mode == 'browser' and self.right.isVisible()" in EXP
    assert 'self.splitter.splitterMoved.connect(lambda *_: self.root_widget.refresh_underline())' in EXP
    assert "self._update_workspace_tabs()\n        self.launcher.web_view_activated()" in EXP


def test_unselected_files_tab_has_lower_left_radius():
    assert 'QPushButton#expandedWorkspaceTab[workspace="files"]:!checked' in EXP
    assert 'border-bottom-left-radius:10px;' in EXP
    # Active tab still touches the content, without a bottom border.
    assert 'border-bottom-right-radius:0px;border-bottom:0;font-weight:400;' in EXP


def test_web_top_right_corner_rounds_download_toolbar_end():
    assert 'border-top-left-radius:0;border-top-right-radius:11px;' in WEB
    assert 'QFrame#launchWebView {{background:{hdr};border:1px solid {border};border-top:0;' in WEB
    assert 'self.downloads_button = self._nav_button(' in WEB


def test_bookmark_header_has_no_duplicate_top_border():
    assert "self.setProperty('panelKind', kind)" in EXP
    assert 'QFrame#expandedPanel[panelKind="bookmark"] {{border-top:0;' in EXP
    assert 'border-top-left-radius:0;border-top-right-radius:11px;' in EXP
    assert "self.right = ExpandedPanel('ブックマーク', 'bookmark')" in EXP


def test_existing_files_browser_state_retention_remains():
    for mark in ('self.files_content_stack.setCurrentWidget(self.files_group)',
                 'self.files_content_stack.setCurrentWidget(self.web_view)',
                 "self.right.hide()  # Bookmarks belong to Browser, never Files.",
                 'self._update_workspace_tabs()'):
        assert mark in EXP


def _sheet(tree, class_name):
    module = ast.parse(tree)
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef)
               and n.name == class_name)
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
              and n.name == 'apply_theme')
    return next(n.args[0] for n in ast.walk(fn) if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute)
                and n.func.attr == 'setStyleSheet' and n.args
                and isinstance(n.args[0], ast.JoinedStr)
                and (class_name == 'LaunchWebView' or
                     'expandedWorkspaceTab' in ast.unparse(n.args[0])))


def test_qss_valid_for_light_and_dark_themes():
    for theme in ('light', 'dark'):
        c = theme_palette(theme)
        e = _sheet(EXP, 'ExpandedLauncherView')
        args = {'colors':c, 'bg':c['panel'], 'border':c['panel_border'],
                'hdr':c['panel_header'], 'text':c['text'],
                'hover':c['hover'], 'active':c['selection'],
                'root_border':c['root_button_border'],
                'height':29, 'pad':3, 'stripe':c['stripe']}
        exp_css = eval(compile(ast.Expression(e), '<v53-expanded-qss>', 'eval'), {}, args)
        w = _sheet(WEB, 'LaunchWebView')
        web_css = eval(compile(ast.Expression(w), '<v53-web-qss>', 'eval'), {},
                       {'colors':c, 'bg':c['panel'], 'hdr':c['panel_header'],
                        'text':c['text'], 'border':c['panel_border'],
                        'hover':c['hover'], 'muted':c['muted_text']})
        assert exp_css.count('{') == exp_css.count('}')
        assert web_css.count('{') == web_css.count('}')
        assert 'border-bottom-left-radius:10px' in exp_css
        assert 'panelKind="bookmark"' in exp_css
        assert 'border-top-right-radius:11px' in web_css
