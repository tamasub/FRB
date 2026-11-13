"""Regression checks that do not require PySide6 on the test machine."""
from __future__ import annotations

import ast
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'frb_japanese_input.py'


class StartupUiRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = MODULE.read_text(encoding='utf-8')
        cls.tree = ast.parse(cls.source, filename=str(MODULE))

    def test_stylesheet_renders_without_python_name_errors(self):
        """All CSS braces in an f-string must escape as {{ and }}."""
        style_func = next(
            item for item in self.tree.body
            if isinstance(item, ast.FunctionDef) and item.name == 'style_for_size'
        )
        # Isolate the pure-Python style function; avoid Qt imports for CI.
        namespace = {}
        exec(compile(ast.Module(body=[style_func], type_ignores=[]), str(MODULE), 'exec'), namespace)
        for size in (17, 20, 22):
            sheet = namespace['style_for_size'](size)
            for selector in ('QPushButton#literalKey', 'QPushButton#modeButton',
                             'QPushButton#kanaKey', 'QPushButton#specialKey'):
                self.assertIn(selector + ' {', sheet)
            self.assertIn(f'font-size: {size}px', sheet)
            self.assertNotIn('{{', sheet)
            self.assertNotIn('}}', sheet)

    def test_qt_mode_button_clicked_bool_does_not_override_mode(self):
        """QPushButton.clicked passes checked; do not consume it as mode."""
        fn = next(item for item in self.tree.body
                  if isinstance(item, ast.ClassDef) and item.name == 'MiniJapaneseInputWindow')
        build = next(item for item in fn.body
                     if isinstance(item, ast.FunctionDef) and item.name == '_build_ui')
        mode_callbacks = [n for n in ast.walk(build)
                          if isinstance(n, ast.Lambda)
                          and any(isinstance(call, ast.Call)
                                  and isinstance(call.func, ast.Attribute)
                                  and call.func.attr == '_select_input_mode'
                                  for call in ast.walk(n.body))]
        self.assertEqual(len(mode_callbacks), 1)
        cb = mode_callbacks[0]
        self.assertEqual([a.arg for a in cb.args.args], ['checked', 'm'])
        self.assertEqual(len(cb.args.defaults), 2)


if __name__ == '__main__':
    unittest.main()
