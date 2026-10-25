"""Static UI contracts until the Windows/PySide6 integration test runs."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
VIEW = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
DRAG = (ROOT / 'src/reorderable_tree.py').read_text(encoding='utf-8')


def test_registration_controls_aligned_after_addressbar():
    ast.parse(APP)
    ast.parse(VIEW)
    assert VIEW.index('shared_layout.addWidget(self.address_bar, 1)') < VIEW.index('self.address_bar.attach_favorite_save(self.favorite_save)')
    assert 'shared_layout.addWidget(self.favorite_dropdown)' not in VIEW
    assert 'shared_layout.addWidget(self.favorite_save)' not in VIEW
    assert 'self.address_bar.attach_history_dropdown(self.favorite_dropdown)' in VIEW
    assert 'self.address_bar.attach_favorite_save(self.favorite_save)' in VIEW
    assert "self.favorite_save.setText('💛')" in VIEW
    assert 'self.favorite_dropdown.clicked.connect(self.toggle_directory_favorites)' in VIEW


def test_favorite_selection_uses_embedded_explorer_not_windows_explorer():
    begin = VIEW.index('    def directory_favorite_clicked(self, item, column):')
    end = VIEW.index('    def directory_favorites_reordered(', begin)
    code = VIEW[begin:end]
    assert 'self.go_to_directory(path)' in code
    assert 'open_target' not in code
    assert 'startfile' not in code
    assert "self.folder_favorites.remove(path)" in code
    assert 'self.path = [directory_row(target)]' in VIEW  # go_to_directory


def test_both_popups_use_shared_drag_reorder_tree_and_no_up_down_buttons():
    assert 'self.history_choices = ReorderablePopupTree(self.history_popup)' in APP
    assert 'self.favorite_choices = ReorderablePopupTree(self.favorite_popup)' in VIEW
    assert 'self.history_choices.orderChanged.connect(self.history_reordered)' in APP
    assert 'self.favorite_choices.orderChanged.connect(self.directory_favorites_reordered)' in VIEW
    assert "row = QTreeWidgetItem([keyword, '×'])" in APP
    assert "row = QTreeWidgetItem([path, '×'])" in VIEW
    assert 'InternalMove' in DRAG
    assert 'self.takeTopLevelItem(source)' in DRAG
    assert "self.save_history_button.setCursor(Qt.CursorShape.PointingHandCursor)" in APP


def test_popup_dismissed_on_view_switch_and_window_dismiss():
    assert APP.count('self.expanded_view.hide_favorite_popup()') >= 3
    assert 'self.favorite_popup.setGeometry(' in VIEW
    assert 'self.favorite_popup.isVisible()' in VIEW
