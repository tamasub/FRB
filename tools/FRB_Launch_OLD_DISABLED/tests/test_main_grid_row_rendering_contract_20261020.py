"""Static regression guards for the Qt-stylesheet row-painting regression.

The earlier implementation relied on QStyleOptionViewItem.backgroundBrush,
which was erased by the QTreeWidget::item QSS on Windows.  Keep background
painting owned by the view and performed BEFORE foreground painting.
"""
import ast
import unittest
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'reorder_widgets.py').read_text(encoding='utf-8')


class RowRenderContractTests(unittest.TestCase):
    def test_grid_background_is_drawn_in_draw_row(self):
        row = SOURCE.split('    def drawRow(', 1)[1].split('    def paintEvent(', 1)[0]
        self.assertLess(row.index('painter.fillRect(full_row'), row.index('super().drawRow(painter, opts, index)'))
        self.assertLess(row.index('super().drawRow(painter, opts, index)'), row.index('painter.drawRect(full_row'))
        self.assertIn('row_has_outline(state)', row)
        self.assertIn('self.viewport().width()', row)

    def test_delegate_suppresses_native_selection_and_hover(self):
        delegate = SOURCE.split('class MainGridRowDelegate(', 1)[1].split('class ReorderTree(', 1)[0]
        self.assertIn('State_Selected', delegate)
        self.assertIn('State_MouseOver', delegate)
        self.assertIn('State_HasFocus', delegate)
        self.assertNotIn('opts.backgroundBrush = QBrush(QColor(', delegate)

    def test_hover_and_focus_force_a_repaint(self):
        tree = SOURCE.split('class ReorderTree(', 1)[1]
        self.assertIn('self.viewport().setMouseTracking(True)', tree)
        self.assertIn('QEvent.Type.HoverMove', tree)
        self.assertIn('QEvent.Type.FocusOut', tree)
        self.assertIn('self.viewport().update()', tree)
        self.assertIn('self.viewport().hasFocus()', tree)


if __name__ == '__main__':
    unittest.main()
