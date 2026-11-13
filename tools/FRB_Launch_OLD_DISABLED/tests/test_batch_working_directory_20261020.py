"""BAT/CMD start from their own directory, regardless of launch entry route.

No Windows or Qt required: exercise the actual Launcher method bodies with stubs.
"""
import ast
import logging
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from process_runner import batch_script_working_directory


def launcher_method(method):
    source = ast.parse((ROOT / 'src' / 'app.py').read_text(encoding='utf8'))
    cls = next(n for n in source.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method)
    return compile(ast.Module(body=[method], type_ignores=[]), 'src/app.py', 'exec')


class BatchWorkingDirectoryTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name) / 'FRB Tools (test) & docs'
        self.folder.mkdir()
        self.bat = self.folder / 'my script.bat'
        self.cmd = self.folder / 'other.cmd'
        self.bat.write_text('@echo off\necho test\n', encoding='utf8')
        self.cmd.write_text('@echo off\necho test\n', encoding='utf8')
        self.expected_cwd = str(self.folder.resolve())

    def test_batch_cwd_recognition(self):
        for script in (self.bat, self.cmd):
            with self.subTest(script=script.name):
                self.assertEqual(batch_script_working_directory(str(script)), self.expected_cwd)
                self.assertEqual(batch_script_working_directory('cmd.exe', ['/d', '/c', str(script)]), self.expected_cwd)
                self.assertEqual(batch_script_working_directory('C:\\Windows\\System32\\cmd.exe', ['/D', '/K', str(script)]), self.expected_cwd)
        self.assertIsNone(batch_script_working_directory('cmd.exe', ['/d', '/c', 'echo hello']))
        self.assertIsNone(batch_script_working_directory('python.exe', [str(self.bat)]))
        self.assertIsNone(batch_script_working_directory('cmd.exe', ['/d', '/c', str(self.folder / 'missing.bat')]))
        self.assertIsNone(batch_script_working_directory('notepad.exe', []))

    def test_files_and_indexed_open_uses_shell_execute_with_cwd(self):
        startfile = Mock()
        env = {'windows': SimpleNamespace(IS_WINDOWS=True),
               'os': SimpleNamespace(startfile=startfile), 'Path': Path}
        exec(launcher_method('open_target'), env)
        for script in (self.bat, self.cmd):
            env['open_target'](object(), str(script))
            startfile.assert_called_with(str(script), cwd=self.expected_cwd)
        startfile.reset_mock()
        text = self.folder / 'note.txt'
        text.touch()
        env['open_target'](object(), str(text))
        startfile.assert_called_once_with(str(text))

    def test_run_cmd_with_batch_overrides_launcher_or_config_cwd(self):
        created = []
        pending = []
        class LauncherStub:
            def __init__(self, step):
                self.queue = [step]
                self.busy = True
                self._foreground_handoff_pending = False
                self.log = []
                self.fail = lambda message: self.log.append(str(message))
                self.open_target = lambda _: None
                self.next_step = lambda: None
        def start_process(program, arguments, cwd, show_console):
            created.append((program, arguments, cwd, show_console))
            return SimpleNamespace(pid=123)
        env = {'DIAG': logging.getLogger('test_batch_working_directory'),
               'QTimer': SimpleNamespace(singleShot=lambda ms, fn: pending.append(fn)),
               'studio_launch_arguments': lambda program, args: list(args),
               'batch_script_working_directory': batch_script_working_directory,
               'start_process': start_process,
               'wifi_transcript_arguments': lambda program, args, _: (args, None),
               'STATE': self.folder, 'ROOT': self.folder / 'launcher_home',
               'windows': SimpleNamespace(allow_child_foreground=lambda pid: True)}
        exec(launcher_method('next_step'), env)
        step = {'launch_action_type':'Run', 'launch_program':'cmd.exe',
                'launch_arguments':['/d', '/c', str(self.bat)],
                'launch_working_directory':str(self.folder / 'wrong-cwd'),
                'launch_show_console':True}
        stub = LauncherStub(step)
        env['next_step'](stub)
        self.assertEqual(created, [('cmd.exe', ['/d', '/c', str(self.bat)], self.expected_cwd, True)])
        self.assertEqual(stub.log, [])
        self.assertEqual(len(pending), 1)
        created.clear()
        stub = LauncherStub({'launch_action_type':'Run', 'launch_program':'git.exe',
                             'launch_arguments':['status'], 'launch_working_directory':str(self.folder)})
        env['next_step'](stub)
        self.assertEqual(created[0][2], str(self.folder))

if __name__ == '__main__':
    unittest.main()
