"""Regression checks for the left-operation-cluster experiment.

These checks intentionally need no PySide6: the real Windows GUI is checked
manually, while dispatch and invariants can run in CI/Linux.
"""
from pathlib import Path
from types import SimpleNamespace
import ast
import textwrap

ROOT = Path(__file__).resolve().parents[1]
VIEW = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')


def method_source(file, cls_name, method_name):
    tree = ast.parse(file)
    klass = next(node for node in tree.body
                 if isinstance(node, ast.ClassDef) and node.name == cls_name)
    node = next(node for node in klass.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == method_name)
    return ast.get_source_segment(file, node)


def run_method(cls, method, fake):
    text = method_source(APP, cls, method)
    namespace = {}
    exec(textwrap.dedent(text), namespace)
    return namespace[method](fake)


def test_density_moves_to_right_of_breadcrumb_and_history_claims_old_slot():
    view_init = method_source(VIEW, 'ExpandedLauncherView', '__init__')
    assert view_init.index('shared_layout.addWidget(self.files_history_button)') < view_init.index(
        'shared_layout.addWidget(self.address_bar, 1)')
    assert view_init.index('shared_layout.addWidget(self.address_bar, 1)') < view_init.index(
        'shared_layout.addWidget(self.density_button)')
    assert view_init.count('shared_layout.addWidget(self.density_button)') == 1
    assert 'self.density_button.clicked.connect(self.toggle_row_density)' in view_init


def test_history_uses_existing_popup_and_selected_keyword_not_second_column():
    events = []
    history = SimpleNamespace(isVisible=lambda: False)
    row = object()
    fake = SimpleNamespace(history_popup=history,
        history_choices=SimpleNamespace(currentItem=lambda: row),
        _remote_popup_area=None, remote_window=None,
        expanded_view=SimpleNamespace(files_history_button='files-magnifier'))
    fake.show_history_popup = lambda **kwargs: events.append(('show', kwargs.get('anchor')))
    fake.history_row_clicked = lambda item, col: events.append(('confirm', item, col))
    run_method('Launcher', 'files_history_button_clicked', fake)
    assert events == [('show', 'files-magnifier')]
    history.isVisible = lambda: True
    run_method('Launcher', 'files_history_button_clicked', fake)
    assert events[-1] == ('confirm', row, 0)


def test_history_category_row_can_toggle_without_running_results():
    events = []
    history = SimpleNamespace(isVisible=lambda: True)
    fake = SimpleNamespace(history_popup=history,
        history_choices=SimpleNamespace(currentItem=lambda: 'category'),
        _remote_popup_area=None)
    fake.history_row_clicked = lambda item, col: events.append((item, col))
    run_method('Launcher', 'files_history_button_clicked', fake)
    assert events == [('category', 0)]


def test_popup_does_not_close_on_second_click_of_new_button():
    method = method_source(APP, 'HistoryOutsideClickFilter', 'eventFilter')
    assert "'files_history_button'" in method
    assert 'files_button.isAncestorOf(obj)' in method
    assert method.index("'files_history_button'") < method.index('launcher.hide_history_popup()')


def test_double_click_defers_single_click_and_reuses_activation_guard():
    view_init = method_source(VIEW, 'ExpandedLauncherView', '__init__')
    assert 'self._files_history_click_timer.setSingleShot(True)' in view_init
    assert 'QApplication.instance().doubleClickInterval()' in view_init
    assert 'self._files_history_click_timer.stop()' in view_init
    assert 'launcher.remote_search_result_double_click()' in view_init
    assert 'self.remote_search_result_double_click()' not in method_source(
        APP, 'Launcher', 'files_history_button_clicked')
    guarded = method_source(APP, 'Launcher', 'remote_search_result_double_click')
    assert 'not self.search.text().strip()' in guarded
    assert 'self.history_popup.isVisible()' in guarded
    assert 'self.activate(row)' in guarded


def test_left_lane_is_not_part_of_file_tree_and_has_full_height_separator():
    view_init = method_source(VIEW, 'ExpandedLauncherView', '__init__')
    assert 'middle_tree_layout.insertWidget(0, self.middle_back_lane)' in view_init
    assert 'middle_tree_layout.addWidget(self.middle.tree, 1)' in view_init
    lane_paint = method_source(VIEW, '_BackLaneWidget', 'paintEvent')
    assert 'x = self.width() - 0.5' in lane_paint
    assert 'QPointF(x, self.height())' in lane_paint
    assert 'visible_line_bottom' not in lane_paint


def test_lane_right_click_and_doubleclick_still_route_to_old_handlers():
    evt = method_source(VIEW, 'ExpandedLauncherView', 'eventFilter')
    double = method_source(VIEW, 'ExpandedLauncherView', 'handle_middle_back_double_click')
    assert 'self.show_lane_new_menu(event.globalPos())' in evt
    assert 'self.handle_middle_back_double_click(obj, event)' in evt
    assert 'self.go_up()' in double


def test_magnifier_icon_receives_current_theme_and_has_clickable_style():
    theme = method_source(VIEW, 'ExpandedLauncherView', 'apply_theme')
    assert 'self.files_history_button.setIcon(_files_history_icon(theme))' in theme
    assert 'QToolButton#expandedFilesHistoryButton' in theme


def test_files_history_popup_is_anchored_near_the_new_left_button():
    position = method_source(APP, 'Launcher', 'position_history_popup')
    show = method_source(APP, 'Launcher', 'show_history_popup')
    assert "getattr(self, '_history_popup_anchor', None)" in position
    assert 'source.mapTo(self' in position
    assert 'self._history_popup_anchor = anchor' in show
