"""Run with: python -m unittest discover -s tests -p test_foreground_launch_handoff.py

These tests exercise the real Launcher.execute/next_step method bodies without
requiring PySide6 or a Windows desktop on the build machine.
"""
import ast
import importlib.util
import logging
from pathlib import Path
from types import MethodType, SimpleNamespace
import unittest
from unittest.mock import patch
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from process_runner import should_start_before_dismiss
import file_index


def method_body(name):
    module = ast.parse((ROOT / 'src/app.py').read_text(encoding='utf-8'))
    cls = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == 'Launcher')
    fn = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == name)
    code = compile(ast.Module(body=[fn], type_ignores=[]), str(ROOT / 'src/app.py'), 'exec')
    return code


class LauncherStub:
    def __init__(self, env):
        self.order = []
        self.queue = []
        self.busy = False
        self.data = {}
        self.expander = lambda values=None: SimpleNamespace(expand=lambda value: value)
        self.dismiss = lambda: self.order.append('hide')
        self.error = lambda error: self.order.append('error')
        self.fail = lambda error: self.order.append('error')
        self.execute = MethodType(env['execute'], self)
        self.next_step = MethodType(env['next_step'], self)


class ForegroundLaunchTests(unittest.TestCase):
    def make_stub(self):
        order = []
        callbacks = []
        runner = SimpleNamespace(pid=813, poll=lambda: None)
        def start(program, args, cwd, show_console):
            order.append('spawn')
            return runner
        win = SimpleNamespace(allow_child_foreground=lambda pid: order.append(('grant', pid)) or True)
        env = dict(DIAG=logging.getLogger('foreground_launch_test'),
                   should_start_before_dismiss=should_start_before_dismiss,
                   QTimer=SimpleNamespace(singleShot=lambda delay, fn: callbacks.append((delay, fn))),
                   windows=win, start_process=start,
                   wifi_transcript_arguments=lambda p, a, state:(a, None),
                   STATE=ROOT, ROOT=ROOT,
                   QApplication=SimpleNamespace(clipboard=lambda:None),
                   file_index=file_index)
        for name in ('execute','next_step'):
            exec(method_body(name), env)
        subject = LauncherStub(env)
        subject.order = order
        subject.dismiss = lambda: order.append('hide')
        return subject, order, callbacks, win

    def test_detached_gui_launch_is_spawned_and_granted_before_hide(self):
        stub, events, callbacks, win = self.make_stub()
        stub.execute({'launch_actions':[{'launch_action_type':'Run',
                     'launch_program':'C:/Studio/FRBStudio.NativeShell.exe',
                     'launch_arguments':['--open-json=x']} ]})
        self.assertEqual(events, ['spawn', ('grant', 813), 'hide'])
        self.assertEqual([d for d,_ in callbacks], [100])

    def test_deferred_console_and_waited_commands_remain_hidden_first(self):
        for props in ({'launch_show_console':True}, {'launch_wait_for_exit':True},
                      {'launch_foreground_on_start':False}):
            with self.subTest(props=props):
                stub, events, callbacks, win = self.make_stub()
                stub.execute({'launch_actions':[dict(launch_action_type='Run',launch_program='tool.exe',**props)]})
                self.assertEqual(events, ['hide'])
                self.assertEqual([d for d,_ in callbacks], [180])

    def test_foreground_permission_failure_does_not_fail_launch(self):
        stub, events, callbacks, win = self.make_stub()
        def fail_grant(pid):
            raise OSError('Windows refused permission')
        win.allow_child_foreground = fail_grant
        stub.execute({'launch_actions':[{'launch_action_type':'Run','launch_program':'app.exe'}]})
        self.assertEqual(events,['spawn','hide'])
        self.assertFalse('error' in events)

    def test_non_run_actions_use_existing_delay(self):
        stub, events, callbacks, win = self.make_stub()
        stub.execute({'launch_actions':[{'launch_action_type':'Open','launch_target':'shell:Downloads'}]})
        self.assertEqual(events, ['hide'])
        self.assertEqual(callbacks[0][0], 180)

    def test_handoff_decision_matrix(self):
        gui={'launch_action_type':'Run','launch_program':'C:/path/gui.exe',
             'launch_show_console':False,'launch_wait_for_exit':False}
        self.assertTrue(should_start_before_dismiss([gui]))
        self.assertFalse(should_start_before_dismiss([]))
        self.assertFalse(should_start_before_dismiss([dict(gui,launch_show_console=True)]))
        self.assertFalse(should_start_before_dismiss([dict(gui,launch_wait_for_exit=True)]))
        self.assertFalse(should_start_before_dismiss([dict(gui,launch_foreground_on_start=False)]))
        self.assertFalse(should_start_before_dismiss([dict(gui,launch_action_type='Open')]))


if __name__=='__main__':
    unittest.main()
