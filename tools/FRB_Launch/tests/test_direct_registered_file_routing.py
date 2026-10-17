"""Directly configured Open actions must use the same file route as indexed files.

Qt is intentionally not required for these tests. The Launcher.execute method is
extracted to exercise the actual action dispatch and URL/Run safeguards.
"""
import ast
import json
import logging
import sys
import tempfile
import unittest
from pathlib import Path
from types import MethodType, SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import file_index
from core import Expander
from process_runner import should_start_before_dismiss


class DirectRegisteredFileRoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.studio = self.path / 'studio'
        (self.studio / 'defs' / 'work').mkdir(parents=True)
        (self.studio / 'defs' / 'work' / 'layout.json').write_text('{}', encoding='utf-8')
        binary = self.studio / 'NativeShell' / '_publish' / 'FRBStudio.NativeShell.exe'
        binary.parent.mkdir(parents=True)
        binary.touch()
        self.managed = self.path / 'managed.json'
        self.managed.write_text(json.dumps({'view_def': 'work/layout.json'}), encoding='utf-8')
        self.ordinary = self.path / 'ordinary.json'
        self.ordinary.write_text('{"hello": "world"}', encoding='utf-8')
        self.md = self.path / 'document.md'
        self.md.write_text('# Memo', encoding='utf-8')
        self.ps1 = self.path / 'test.ps1'
        self.ps1.write_text('Write-Host ok', encoding='utf-8')
        self.bat = self.path / 'do.bat'
        self.bat.write_text('echo ok', encoding='utf-8')

    def test_managed_json_goes_to_studio(self):
        routed = file_index.route_registered_open_step(
            {'launch_action_type': 'Open', 'launch_target': str(self.managed)}, str(self.studio))
        self.assertEqual(len(routed), 1)
        self.assertEqual(routed[0]['launch_action_type'], 'Run')
        self.assertEqual(routed[0]['launch_arguments'], ['--open-json=' + str(self.managed)])
        self.assertTrue(routed[0]['launch_program'].endswith('FRBStudio.NativeShell.exe'))

    def test_regular_json_not_rewritten(self):
        original = {'launch_action_type': 'Open', 'launch_target': str(self.ordinary)}
        self.assertEqual(file_index.route_registered_open_step(original, str(self.studio)), [original])
        missing_viewdef = self.path / 'missingdef.json'
        missing_viewdef.write_text('{"view_def":"work/nope.json"}', encoding='utf-8')
        original = {'launch_action_type': 'Open', 'launch_target': str(missing_viewdef)}
        self.assertEqual(file_index.route_registered_open_step(original, str(self.studio)), [original])

    def test_direct_registered_md_and_ps1_reuse_shared_routing(self):
        md = file_index.route_registered_open_step({'launch_action_type': 'Open', 'launch_target': str(self.md)}, str(self.studio))
        self.assertEqual(md[0]['launch_arguments'], ['--open-md=' + str(self.md)])
        ps = file_index.route_registered_open_step({'launch_action_type': 'Open', 'launch_target': str(self.ps1)}, str(self.studio))
        self.assertEqual(ps[0]['launch_program'], 'powershell.exe')
        self.assertEqual(ps[0]['launch_arguments'], ['-NoProfile', '-File', str(self.ps1)])
        bat = {'launch_action_type': 'Open', 'launch_target': str(self.bat)}
        self.assertEqual(file_index.route_registered_open_step(bat, str(self.studio)), [bat])

    def test_non_file_targets_and_explicit_actions_are_untouched(self):
        for target in ('https://example.com/manifest.json', 'shell:Downloads',
                       str(self.path / 'not-found.json'), str(self.path)):
            original = {'launch_action_type': 'Open', 'launch_target': target}
            self.assertEqual(file_index.route_registered_open_step(original, str(self.studio)), [original])
        with_browser = {'launch_action_type': 'Open', 'launch_target': str(self.managed), 'launch_browser': 'edge'}
        self.assertEqual(file_index.route_registered_open_step(with_browser, str(self.studio)), [with_browser])
        run = {'launch_action_type': 'Run', 'launch_program': 'other.exe', 'launch_arguments': [str(self.managed)]}
        self.assertEqual(file_index.route_registered_open_step(run, str(self.studio)), [run])

    def test_existing_launch_execute_uses_shared_routing_after_expansion(self):
        source = (ROOT / 'app.py').read_text(encoding='utf-8')
        tree = ast.parse(source)
        launcher = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
        method = next(n for n in launcher.body if isinstance(n, ast.FunctionDef) and n.name == 'execute')
        env = {
            'DIAG': logging.getLogger('test_direct_registered'), 'file_index': file_index,
            'should_start_before_dismiss': should_start_before_dismiss,
            'QTimer': SimpleNamespace(singleShot=lambda _, action: None),
        }
        exec(compile(ast.Module(body=[method], type_ignores=[]), str(ROOT / 'app.py'), 'exec'), env)

        class Stub:
            busy = False
            def __init__(self, studio, managed):
                self.queue = []
                self.dismissed = 0
                self.error_message = None
                self.executed_next = 0
                self._foreground_handoff_pending = False
                self.expander = lambda values=None: Expander({
                    'launch_variables': [
                        {'variable_id': 'studio_root', 'launch_variable_type': 'literal', 'launch_value': str(studio)},
                        {'variable_id': 'my_json', 'launch_variable_type': 'literal', 'launch_value': str(managed)},
                    ]}, values=values)
            def next_step(self):
                self.executed_next += 1
            def dismiss(self):
                self.dismissed += 1
            def error(self, error):
                self.error_message = str(error)

        stub = Stub(self.studio, self.managed)
        stub.execute = MethodType(env['execute'], stub)
        stub.execute({'item_id': 'direct-config', 'title': 'Direct JSON', 'launch_actions': [
            {'launch_action_type': 'Open', 'launch_target': '%my_json%'},
            {'launch_action_type': 'Open', 'launch_target': 'shell:Downloads'},
            {'launch_action_type': 'Run', 'launch_program': 'custom.exe'},
        ]})
        self.assertIsNone(stub.error_message)
        self.assertEqual(stub.queue[0]['launch_action_type'], 'Run')
        self.assertEqual(stub.queue[0]['launch_arguments'], ['--open-json=' + str(self.managed)])
        self.assertEqual(stub.queue[1], {'launch_action_type': 'Open', 'launch_target': 'shell:Downloads'})
        self.assertEqual(stub.queue[2], {'launch_action_type': 'Run', 'launch_program': 'custom.exe'})
        self.assertEqual(stub.executed_next, 1)  # Studio GUI begins before launcher hides.
        self.assertEqual(stub.dismissed, 1)


if __name__ == '__main__':
    unittest.main()
