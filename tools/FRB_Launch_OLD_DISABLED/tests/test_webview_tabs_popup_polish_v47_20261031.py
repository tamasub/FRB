"""v47: web tab + button placement and popup frame contract (no PySide6 needed)."""
import ast
from pathlib import Path
from types import SimpleNamespace

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'launch_web_view.py').read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)


def _method(class_name, method_name):
    klass = next(node for node in TREE.body if isinstance(node, ast.ClassDef)
                 and node.name == class_name)
    node = next(node for node in klass.body if isinstance(node, ast.FunctionDef)
                and node.name == method_name)
    ns = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 '<v47>', 'exec'), ns)
    return ns[method_name]


def test_web_tab_base_line_is_explicitly_disabled_not_just_pane_border():
    assert 'self.setDrawBase(False)' in SOURCE
    assert 'QTabWidget#launchWebTabs::pane {{border:0;margin:0;padding:0;}}' in SOURCE
    assert 'border-top:0;border-bottom:0' in SOURCE
    assert 'QTabBar#launchWebTabBar::scroller {{border:none;background:transparent;}}' in SOURCE


def test_new_tab_button_is_inline_sibling_of_tab_bar_not_top_right_corner():
    assert 'new_tab = QToolButton(self.tabs)' in SOURCE
    assert 'bar.set_new_tab_button(new_tab)' in SOURCE
    assert 'setCornerWidget(new_tab' not in SOURCE
    assert 'self.setExpanding(False)' in SOURCE
    assert 'self.tabs.tabBar()._queue_new_tab_position()' in SOURCE


def test_new_tab_button_is_round_and_stays_aligned_with_tab_close_x():
    assert 'new_tab.setFixedSize(29, 29)' in SOURCE
    assert 'QToolButton#launchWebNewTab:hover {{background:{hover};border-radius:14px;}}' in SOURCE
    assert 'button.move(x, y)' in SOURCE
    assert 'self.tabRect(self.count() - 1).right()' in SOURCE
    assert '(self.height() - button.height()) // 2' in SOURCE
    assert 'button.setFocusPolicy(Qt.FocusPolicy.NoFocus)' not in SOURCE  # existing attribute is on new_tab
    assert 'new_tab.setFocusPolicy(Qt.FocusPolicy.NoFocus)' in SOURCE


def test_plus_placement_uses_tab_widget_coordinates_and_separate_space():
    # Regression: v47 clamped the button *inside the tabbar*, covering X.
    assert 'self.mapTo(host, QPoint(' in SOURCE
    assert 'host.width() - button.width() - 4' in SOURCE
    assert 'visible_right = min(last_right, self.width() - 1)' in SOURCE
    assert 'button.setParent(host)' in SOURCE
    assert 'self.setMaximumWidth(max_width)' in SOURCE


def test_plus_position_updates_after_close_reorder_and_title_change():
    assert 'def tabInserted(self, index):' in SOURCE
    assert 'def tabRemoved(self, index):' in SOURCE
    assert 'bar.tabMoved.connect(lambda *_: bar._queue_new_tab_position())' in SOURCE
    assert 'self.tabs.tabBar()._queue_new_tab_position()' in SOURCE
    assert 'self.tabs.setMovable(True)' in SOURCE
    assert 'self.tabs.tabCloseRequested.connect(self.close_tab)' in SOURCE


def test_download_popup_has_no_native_drop_shadow_or_extra_outer_qss_border():
    assert 'Qt.WindowType.NoDropShadowWindowHint' in SOURCE
    assert 'QFrame#launchDownloadsPanel {{background:{bg};border:none;' in SOURCE
    assert 'self.scroll.setFrameShape(QFrame.Shape.NoFrame)' in SOURCE
    assert 'self.setObjectName(\'launchDownloadsPanel\')' in SOURCE


def test_download_ux_and_remote_controls_unchanged():
    for fragment in ('def _download_requested(self, request):',
                     'def show_downloads_menu(self, *, animated=False):',
                     'def _animate_download_complete(self):',
                     'def extract_download_zip(self, path):',
                     'def select_tab(self, step):',
                     'def scroll_page(self, step):',
                     'def tab_context_menu(self):',
                     'def set_remote_area(self, area):'):
        assert fragment in SOURCE
