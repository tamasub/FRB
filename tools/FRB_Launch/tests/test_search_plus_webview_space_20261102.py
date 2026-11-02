"""Search plus relocation and WebView height: no Qt required.

Keep controls wired to the original action so Remote/context menus continue to
use the same category creation command; the Browser no longer reserves a hint row.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
WEB = (ROOT / 'src/launch_web_view.py').read_text(encoding='utf-8')


def _method(source, class_name, name):
    tree = ast.parse(source)
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef)
               and node.name == class_name)
    node = next(node for node in cls.body if isinstance(node, ast.FunctionDef)
                and node.name == name)
    return ast.get_source_segment(source, node)


def test_plus_reuses_history_category_action_beside_magnifier():
    assert "self.history_category_action = QAction(" in APP
    assert 'self.history_category_action.triggered.connect(self.add_history_category)' in APP
    assert 'self.history_category_button = QToolButton(self.search)' in APP
    assert 'self.history_category_button.setDefaultAction(self.history_category_action)' in APP
    assert "QLineEdit.ActionPosition.TrailingPosition)" in APP  # history chevron remains
    assert 'self.search.addAction(\n            QIcon(plus_icon)' not in APP
    method = _method(APP, 'Launcher', 'layout_search_inner_controls')
    assert 'self.search_glyph.move(11,' in method
    assert 'self.history_category_button.move(\n            44,' in method
    assert 'self.search.setTextMargins(60, 0,' in method
    assert 'self.history_category_button.raise_()' in method


def test_plus_inset_survives_theme_and_search_resize():
    assert "QToolButton#searchHistoryCategoryButton:hover" in APP
    assert 'self.search.installEventFilter(self)' in APP
    assert 'self.layout_search_inner_controls()' in _method(APP, 'Launcher', 'eventFilter')
    assert 'launcher.history_category_action.icon()' in (ROOT / 'src/launch_remote.py').read_text(encoding='utf-8')


def test_browser_has_no_bottom_hint_row_or_home_instruction():
    assert "self.hint = QLabel(" not in WEB
    assert 'layout.addWidget(self.hint)' not in WEB
    assert 'self.hint.setText(' not in WEB
    assert 'HOMEでFilesに戻る' not in WEB
    assert 'QLabel#launchWebHint' not in WEB


def test_browser_failure_visible_as_address_tooltip_and_home_stays_available():
    method = _method(WEB, 'LaunchWebView', 'load_finished')
    assert "'ページを表示できません" in method
    assert 'self.address.setToolTip(' in method
    assert 'self.update_navigation()' in method
    assert 'self.nav_home_button.clicked.connect(self.navigate_home)' in APP
