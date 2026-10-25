"""Regression: bookmarks view cannot register event filters before panel exists."""
import ast
from pathlib import Path


def test_bookmark_event_filters_installed_only_after_panel_construction():
    source = Path(__file__).resolve().parents[1] / 'src' / 'expanded_view.py'
    code = source.read_text(encoding='utf-8')
    module = ast.parse(code)
    klass = next(node for node in module.body
                 if isinstance(node, ast.ClassDef) and node.name == 'ExpandedLauncherView')
    init = next(node for node in klass.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == '__init__')
    # Evaluate the *order*, not mere presence, of these statements.
    creation = []
    hooks = []
    for stmt in init.body:
        if isinstance(stmt, ast.Assign) and any(
            isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name) and target.value.id == 'self'
            and target.attr == 'right' for target in stmt.targets
        ):
            creation.append(stmt.lineno)
        if (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
                and isinstance(stmt.value.func, ast.Attribute)
                and stmt.value.func.attr == 'installEventFilter'):
            ref = ast.unparse(stmt.value.func.value)
            if ref.startswith('self.right.tree'):
                hooks.append(stmt.lineno)
    assert len(creation) == 1, 'Expected one bookmark panel constructor'
    assert len(hooks) == 2, 'Expected tree and viewport wheel event filters'
    assert all(line > creation[0] for line in hooks), (
        f'Bookmark event filters registered before self.right exists: {creation}, {hooks}')
    assert 'self.wheel_bookmarks_first_level(event)' in code
    assert 'tree.scrollToItem(item)' in code


def test_only_bookmark_first_level_uses_right_column_wheel_hook():
    source = Path(__file__).resolve().parents[1] / 'src' / 'expanded_view.py'
    code = source.read_text(encoding='utf-8')
    assert 'self.right.tree.verticalScrollBar().installEventFilter(self)' not in code
    assert 'self.right.tree.viewport().installEventFilter(self)' in code
