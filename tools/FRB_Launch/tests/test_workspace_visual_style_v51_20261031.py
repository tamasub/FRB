"""v51: Files/Browser large attached tabs, inverse Web chrome and integer KB."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from middle_folder_filter import format_size, filter_sort_folder_rows

EXP = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
WEB = (ROOT / 'src' / 'launch_web_view.py').read_text(encoding='utf-8')


def test_files_size_always_integer_kb_rounded_up():
    for size, expected in [
        (None, ''), (0, '0 KB'), (1, '1 KB'), (1023, '1 KB'),
        (1024, '1 KB'), (1025, '2 KB'), (2048, '2 KB'),
        (2 * 1024**2, '2,048 KB')
    ]:
        assert format_size(size) == expected


def test_columns_keep_raw_byte_sort_precision(tmp_path):
    first = tmp_path / 'one.bin'
    second = tmp_path / 'two.bin'
    first.write_bytes(b'a' * 1025)
    second.write_bytes(b'b' * 1024)
    rows = [dict(title=path.name, item_kind='file', _browse_file=str(path))
            for path in (first, second)]
    sorted_rows = filter_sort_folder_rows(rows, mode='size_desc')
    assert [r['title'] for r in sorted_rows] == ['one.bin', 'two.bin']
    assert [r['_middle_size'] for r in sorted_rows] == ['2 KB', '1 KB']


def test_workspace_tabs_use_connected_full_height_style():
    assert 'self.toolbar_scroller.setFixedHeight(44)' in EXP
    assert 'required = 58 if maximum > minimum else 44' in EXP
    assert 'outer.setSpacing(0)' in EXP
    assert "self.root_layout.setContentsMargins(6, 3, 4, 0)" in EXP
    assert 'button.setFixedHeight(38)' in EXP
    assert 'button.setMaximumHeight(30)' in EXP  # right-side root buttons stay compact
    assert "button.setProperty('workspace', 'files' if button is self.files_mode_tab else 'browser')" in EXP
    assert 'QPushButton#expandedWorkspaceTab:checked' in EXP
    assert 'border-bottom:0;font-weight:400;' in EXP
    assert 'QPushButton#expandedWorkspaceTab[workspace="browser"]:checked' in EXP
    assert 'QFrame#expandedFilesGroup {{background:{bg};border:1px solid {border};border-top:0;' in EXP


def test_browser_chrome_mint_with_rounded_white_address():
    assert 'QFrame#launchWebView {{background:{hdr};border:1px solid {border};border-top:0;' in WEB
    assert "QLineEdit#launchWebAddress {{background:{colors['search_bg']};color:{colors['search_fg']};" in WEB
    assert 'border-radius:12px;padding:4px 10px;' in WEB
    assert 'QToolButton {{background:{bg};color:{text};' in WEB
    assert 'QTabBar#launchWebTabBar::tab:selected {{background:{bg};font-weight:400;}}' in WEB


def test_no_behavioral_changes_to_web_tab_or_folder_navigation():
    assert 'self.files_content_stack.setCurrentWidget(self.web_view)' in EXP
    assert 'self.files_content_stack.setCurrentWidget(self.files_group)' in EXP
    assert 'layout.addWidget(self.tabs, 1)' in WEB
    assert 'self.tabs.setTabsClosable(True)' in WEB


def test_browser_theme_css_renders_with_no_missing_variables():
    """Build the real Web QSS template for both palettes, no GUI required."""
    import ast
    from launch_appearance import theme_palette
    module = ast.parse(WEB)
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef)
               and n.name == 'LaunchWebView')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
              and n.name == 'apply_theme')
    css_calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute)
                 and n.func.attr == 'setStyleSheet' and n.args
                 and isinstance(n.args[0], ast.JoinedStr)]
    assert len(css_calls) == 1
    for theme in ('light', 'dark'):
        colors = theme_palette(theme)
        values = dict(colors=colors, bg=colors['panel'], hdr=colors['panel_header'],
                      text=colors['text'], border=colors['panel_border'],
                      hover=colors['hover'], muted=colors['muted_text'])
        expression = ast.Expression(body=css_calls[0].args[0])
        css = eval(compile(expression, '<v51-web-qss>', 'eval'), {}, values)
        assert css.count('{') == css.count('}')
        assert f'background:{colors["panel_header"]};border:1px' in css
        assert f'background:{colors["search_bg"]};color:{colors["search_fg"]}' in css
