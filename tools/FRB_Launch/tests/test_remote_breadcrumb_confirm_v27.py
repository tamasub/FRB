"""Regression: remote breadcrumb preview must be confirmable without local errors."""
import ast
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'src' / 'app.py'

def test_remote_mouse_click_defines_expanded_before_branch():
    method = next(n for n in ast.walk(ast.parse(SOURCE.read_text(encoding='utf-8')))
                  if isinstance(n, ast.FunctionDef) and n.name == 'remote_mouse_click')
    initial = method.body[:3]
    assert any(isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'expanded' for t in n.targets) for n in initial)
    assert 'self.expanded_view.address_bar._submit()' in ast.unparse(method)

def test_remote_right_confirms_breadcrumb():
    method = next(n for n in ast.walk(ast.parse(SOURCE.read_text(encoding='utf-8')))
                  if isinstance(n, ast.FunctionDef) and n.name == 'remote_command')
    code = ast.unparse(method)
    assert "command in ('ENTER', 'RIGHT')" in code
    assert 'view.address_bar._submit()' in code
