"""Fail CI when a new Launch-owned button dialog bypasses the common selector.

Usage: python scripts/check_dialog_contract.py

Native QFileDialog pickers and the pre-main startup crash notification are
intentional exceptions. No runtime GUI/Qt installation is required.
"""
from __future__ import annotations
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _call_path(call: ast.Call) -> str:
    target = call.func
    path = []
    while isinstance(target, ast.Attribute):
        path.insert(0, target.attr)
        target = target.value
    if isinstance(target, ast.Name):
        path.insert(0, target.id)
    return '.'.join(path)


def violations(root: Path = ROOT) -> list[str]:
    issues: list[str] = []
    for source in sorted((root / 'src').rglob('*.py')):
        tree = ast.parse(source.read_text(encoding='utf-8'), filename=str(source))
        filename = source.relative_to(root).as_posix()
        for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
            path = _call_path(call)
            if path.startswith(('QInputDialog.', 'QMessageBox.question',
                                'QMessageBox.information', 'QMessageBox.warning')):
                issues.append(f'{filename}:{call.lineno}: {path} bypasses shared dialog runner')
            if path == 'QMessageBox.critical' and not (filename == 'src/app.py' and
                    call.lineno >= _startup_guard_line(tree)):
                issues.append(f'{filename}:{call.lineno}: {path} bypasses shared dialog runner')
            if path in ('dialog.exec', 'dialog.exec_', 'message_box.exec', 'message_box.exec_'):
                issues.append(f'{filename}:{call.lineno}: direct modal dialog execution')
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            creates_dialog = [call for call in ast.walk(node)
                if isinstance(call, ast.Call) and _call_path(call) in ('QDialog', 'QMessageBox')]
            if not creates_dialog or (filename == 'src/remote_confirmation.py'
                    and node.name == '__init__'):
                continue
            # Each constructor must be in the same function as the common runner.
            # Tests deliberately reject constructors that rely on manual Remote
            # checks or direct .exec(), even if some other feature happens to work.
            shares = any(isinstance(call, ast.Call) and
                         _call_path(call) in ('self.run_launch_button_dialog',
                                              'launcher.run_launch_button_dialog')
                         for call in ast.walk(node))
            if not shares:
                for call in creates_dialog:
                    issues.append(f'{filename}:{call.lineno}: dialog lacks run_launch_button_dialog')
    return issues


def _startup_guard_line(tree: ast.Module) -> int:
    """Only the emergency crash-handler outside main() may use QMessageBox."""
    for stmt in tree.body:
        if isinstance(stmt, ast.If) and isinstance(stmt.test, ast.Compare) and (
            isinstance(stmt.test.left, ast.Name) and stmt.test.left.id == '__name__'):
            return stmt.lineno
    return 10**9


if __name__ == '__main__':
    problems = violations()
    if problems:
        print('\n'.join('FAIL: ' + item for item in problems))
        raise SystemExit(1)
    print('PASS: all Launch button dialogs use the shared selection contract')
