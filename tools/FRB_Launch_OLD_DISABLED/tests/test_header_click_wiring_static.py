"""Header mouse event wiring regression (runs without PySide6)."""
import ast
from pathlib import Path
import unittest

APP = Path(__file__).resolve().parents[1] / 'src/app.py'


class HeaderClickWiringTests(unittest.TestCase):
    def test_native_sorting_disabled_before_header_clicks_enabled(self):
        tree = ast.parse(APP.read_text(encoding='utf-8'))
        launcher = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
        init = next(n for n in launcher.body if isinstance(n, ast.FunctionDef) and n.name == '__init__')
        calls = [n for n in ast.walk(init)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
        off = next(n for n in calls if n.func.attr == 'setSortingEnabled'
                   and n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value is False)
        on = next(n for n in calls if n.func.attr == 'setSectionsClickable'
                  and n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value is True)
        self.assertLess(off.lineno, on.lineno,
                        'Qt disables clickable header when setSortingEnabled(False) is called')
        self.assertTrue(any(n.func.attr == 'connect' and n.func.value.attr == 'sectionClicked'
                            for n in calls if isinstance(n.func.value, ast.Attribute)))


if __name__ == '__main__':
    unittest.main()
