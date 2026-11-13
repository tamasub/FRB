"""Presentation contracts for the October 24 icon/chevron correction.

These source-backed tests run without PySide6. Actual Windows/Qt rendering
is still a manual smoke test and must not be reported as automated PASS.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEW = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')


def _function_source(name):
    module = ast.parse(VIEW)
    node = next(child for child in module.body
                if isinstance(child, (ast.FunctionDef, ast.ClassDef)) and child.name == name)
    return ast.get_source_segment(VIEW, node)


def test_icons_and_delegate_parse():
    ast.parse(VIEW)
    assert 'QStyledItemDelegate' in VIEW


def test_exact_pre_polish_folder_icon_is_restored():
    src = _function_source('header_icon')
    assert "if kind != 'bookmark':" in src
    assert 'QPixmap(28, 28)' in src
    assert "p.drawRoundedRect(3, 8, 22, 16, 3, 3)" in src
    assert "p.drawRoundedRect(5, 5, 11, 8, 2, 2)" in src
    assert "QColor('#8cbf68' if theme == 'light' else '#a7d785')" in src


def test_bookmark_ribbon_is_real_hidpi_no_double_scaling():
    src = _function_source('header_icon')
    assert 'QPixmap(56, 56)' in src
    assert 'pix.setDevicePixelRatio(2)' in src
    assert 'p.scale(2, 2)' not in src
    assert 'ribbon.lineTo(14, 19.5)' in src
    assert 'p.drawPath(ribbon)' in src
    assert 'QLinearGradient' in src


def test_chevrons_are_small_vector_strokes_with_right_inset():
    src = _function_source('_NavigationChevronDelegate')
    assert 'QStyledItemDelegate' in src
    assert 'QPen(' in src
    assert '1.6' in src
    assert 'center_y - 4' in src
    assert 'center_y + 4' in src
    assert 'Qt.PenCapStyle.RoundCap' in src
    assert 'Qt.PenJoinStyle.RoundJoin' in src
    assert 'painter.drawPath(chevron)' in src


def test_delegate_drawn_in_right_column_only_for_expandable_rows():
    assert 'self.tree.setColumnCount(2)' in VIEW
    assert 'self.tree.setColumnWidth(1, 40)' in VIEW
    assert 'center_x = option.rect.right() - 20' in VIEW
    assert 'self.tree.setItemDelegateForColumn(1, _NavigationChevronDelegate(self.tree))' in VIEW
    assert "item.setData(1, Qt.ItemDataRole.UserRole, is_folder)" in VIEW
    assert "item = QTreeWidgetItem([row.get('title', ''), ''])" in VIEW


def test_other_icons_and_commands_not_changed():
    assert 'def link_icon(theme):' in VIEW
    assert 'self.launcher.row_icon(row)' in VIEW
    assert 'self.root_layout.addWidget(button)' in VIEW
    assert 'self.middle.back.clicked.connect(self.go_up)' in VIEW
