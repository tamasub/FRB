"""Regression for the legibility of Remote Browser's new/current tab choice.

No PySide6 required: inspect UI construction and run the display/state method
against fake buttons to cover both selection states and palette variants.
"""
from pathlib import Path
import ast
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')


def method(name):
    module = ast.parse(SOURCE)
    cls = next(item for item in module.body if isinstance(item, ast.ClassDef)
               and item.name == 'CascadeMenu')
    node = next(item for item in cls.body if isinstance(item, ast.FunctionDef)
                and item.name == name)
    scope = {'theme_family': lambda color: 'light' if color == 'light' else 'dark'}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 '<v76>', 'exec'), scope)
    return scope[name], ast.get_source_segment(SOURCE, node)


class Button:
    def setChecked(self, value):
        self.checked = value

    def setText(self, value):
        self.text = value

    def setToolTip(self, value):
        self.tooltip = value

    def setStyleSheet(self, value):
        self.stylesheet = value


def menu(theme='light'):
    return SimpleNamespace(
        launcher=SimpleNamespace(color_theme=theme),
        remote_bookmark_new_tab_button=Button(),
        remote_bookmark_current_tab_button=Button())


def test_selected_option_visibly_marked_at_start_and_updates_on_click():
    fn, _ = method('_select_remote_bookmark_tab')
    widget = menu()
    fn(widget, True)
    assert widget.remote_bookmark_new_tab is True
    assert widget.remote_bookmark_new_tab_button.checked is True
    assert widget.remote_bookmark_current_tab_button.checked is False
    assert widget.remote_bookmark_new_tab_button.text == '✓ 新規タブ'
    assert widget.remote_bookmark_current_tab_button.text == 'カレントタブ'
    assert 'background:#d6e7f8' in widget.remote_bookmark_new_tab_button.stylesheet
    fn(widget, False)
    assert widget.remote_bookmark_new_tab is False
    assert widget.remote_bookmark_new_tab_button.checked is False
    assert widget.remote_bookmark_current_tab_button.checked is True
    assert widget.remote_bookmark_new_tab_button.text == '新規タブ'
    assert widget.remote_bookmark_current_tab_button.text == '✓ カレントタブ'
    assert 'background:#d6e7f8' in widget.remote_bookmark_current_tab_button.stylesheet
    fn(widget, True)
    assert widget.remote_bookmark_new_tab is True
    assert widget.remote_bookmark_new_tab_button.checked is True


def test_dark_palette_has_a_distinct_selected_surface():
    fn, _ = method('_select_remote_bookmark_tab')
    widget = menu('dark')
    fn(widget, True)
    assert 'background:#345d7a' in widget.remote_bookmark_new_tab_button.stylesheet
    assert 'background:#263a35' in widget.remote_bookmark_current_tab_button.stylesheet


def test_controls_fit_compact_popup_and_do_not_steal_key_focus():
    _, source = method('_ensure_local_filter')
    assert "bookmark_root = getattr(self, 'remote_browser_bookmark_roots', False)" in source
    assert 'target_row.setContentsMargins(0, 0, 0, 0)' in source
    assert 'target_row.setSpacing(4)' in source
    assert 'button.setMinimumWidth(0)' in source
    assert 'button.setFixedHeight(28)' in source
    assert 'button.setFocusPolicy(Qt.FocusPolicy.NoFocus)' in source
    assert 'target_row.addWidget(self.remote_bookmark_new_tab_button, 1)' in source
    assert 'target_row.addWidget(self.remote_bookmark_current_tab_button, 1)' in source
    assert 'self._select_remote_bookmark_tab(True)' in source


def test_remote_url_target_reads_the_same_state():
    module = ast.parse(SOURCE)
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'run_menu_item')
    source = ast.get_source_segment(SOURCE, fn)
    assert "new_tab = getattr(root, 'remote_bookmark_new_tab', True)" in source
    assert 'show_web_url(url, new_tab=new_tab)' in source
