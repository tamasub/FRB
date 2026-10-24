"""The five requested 3-panel affordances: static wiring + pure UI contracts.

Qt/Windows actual keyboard focus and layout require the Windows smoke checklist.
"""
import ast
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
VIEW = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')


def test_python_syntax():
    ast.parse(VIEW)
    ast.parse(APP)


def test_combined_header_spans_files_and_directory():
    assert "self.files_group = QFrame(self.splitter)" in VIEW
    assert "group_layout.addWidget(self.shared_header)" in VIEW
    assert "group_layout.addWidget(self.files_splitter, 1)" in VIEW
    assert "self.files_splitter.addWidget(self.left)" in VIEW
    assert "self.files_splitter.addWidget(self.middle)" in VIEW
    assert "self.splitter.addWidget(self.right)" in VIEW
    assert "self.left.header.hide()" in VIEW
    assert "self.middle.header.hide()" in VIEW
    assert "shared_layout.addWidget(self.address_bar, 1)" in VIEW


def test_splitter_restores_legacy_3_width_settings():
    assert "expanded_splitter_sizes" in VIEW
    assert "[values[0] + values[1], values[2]]" in VIEW
    assert "self.files_splitter.setSizes(values[:2])" in VIEW
    assert "self.files_splitter.sizes() + self.splitter.sizes()[1:]" in VIEW


def test_chevrons_are_a_right_aligned_separate_column():
    assert "self.tree.setColumnCount(2)" in VIEW
    assert "item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)" in VIEW
    assert "self.tree.setColumnWidth(1, 40)" in VIEW
    assert "row.get('title', '') + '   ›'" not in VIEW


def test_density_toggle_persists_and_updates_style():
    assert "expanded_row_density" in VIEW
    assert "self.density_button.clicked.connect(self.toggle_row_density)" in VIEW
    assert "(23, 1) if tight else (29, 3)" in VIEW
    assert "QTreeWidget#expandedTree::item {{min-height:{height}px;padding:{pad}px 7px" in VIEW
    assert "self.launcher.settings.sync()" in VIEW


def test_ribbon_uses_multistop_gradient_with_bookmark_notch():
    assert "gradient = QLinearGradient" in VIEW
    assert "ribbon.lineTo(14, 19.5)" in VIEW
    assert "p.drawPath(ribbon)" in VIEW


def test_first_level_ctrl_fn_shortcuts_follow_visible_order():
    assert "QKeySequence(f'Ctrl+F{index+1}')" in APP
    assert "self.execute_expanded_root_shortcut(i)" in APP
    assert "view.root_action(view.root_rows[index], button)" in APP
    assert "view.toolbar_scroller.ensureWidgetVisible(button)" in APP
    assert "enumerate(roots)" in VIEW
    assert "f'Ctrl+F{index+1}'" in VIEW


def test_original_page_function_keys_are_kept():
    assert "QKeySequence(f'F{index+1}')" in APP
    assert "shortcut.activated.connect(lambda i=index:self.switch_page(i))" in APP


def test_old_expanded_keyboard_path_kept():
    for method in ('expanded_root_key', 'expanded_tree_key', 'expanded_tab_key'):
        assert f'def {method}(' in APP
