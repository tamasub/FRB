"""Selection descriptions must be painted once while retaining native copy.

The regression originated when a transparent read-only QLineEdit was overlaid
on top of a QTreeWidgetItem which still painted the same emoji string.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'src' / 'app.py'


def test_only_readonly_editor_paints_selection_description():
    module = ast.parse(APP.read_text(encoding='utf-8'))
    launcher = next(node for node in module.body if isinstance(node, ast.ClassDef)
                    and node.name == 'Launcher')
    render = next(node for node in launcher.body if isinstance(node, ast.FunctionDef)
                  and node.name == 'render')
    # Verify the actual constructor expression in render(), not a comment.
    constructors = [node for node in ast.walk(render)
                    if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == 'QTreeWidgetItem']
    choice_constructor = next(node for node in constructors
                              if node.args and isinstance(node.args[0], ast.List)
                              and len(node.args[0].elts) == 2)
    second_text = choice_constructor.args[0].elts[1]
    assert isinstance(second_text, ast.IfExp)
    assert isinstance(second_text.test, ast.Attribute)
    assert second_text.test.attr == 'selection'
    assert isinstance(second_text.body, ast.Constant)
    assert second_text.body.value == ''
    assert isinstance(second_text.orelse, ast.Name)
    assert second_text.orelse.id == 'desc'
    code = ast.get_source_segment(APP.read_text(encoding='utf-8'), render)
    assert 'QLineEdit(desc, self.list)' in code
    assert 'description.setReadOnly(True)' in code
    assert 'self.list.setItemWidget(q, 1, description)' in code
    assert 'q.setToolTip(1,' in code
    assert 'self.selection_send_button' in code


def test_app_source_parses():
    ast.parse(APP.read_text(encoding='utf-8'))


def test_qt_widget_single_paint_when_pyside_available():
    """Optional smoke, requiring Qt; all other tests work without PySide6."""
    import os
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    try:
        from PySide6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QLineEdit
        from PySide6.QtCore import Qt
    except ImportError:
        import pytest
        pytest.skip('PySide6 is unavailable in the test runner')
    app = QApplication.instance() or QApplication([])
    tree = QTreeWidget()
    tree.setColumnCount(2)
    item = QTreeWidgetItem(['😋 顔', ''])
    tree.addTopLevelItem(item)
    description = QLineEdit('😀😃😄😁😆😅😂🤣', tree)
    description.setReadOnly(True)
    tree.setItemWidget(item, 1, description)
    assert item.text(1) == ''  # underlying view paints no text
    assert description.text() == '😀😃😄😁😆😅😂🤣'
    assert description.isReadOnly()
    description.selectAll()
    description.copy()
    assert app.clipboard().text() == description.text()
    tree.deleteLater()
