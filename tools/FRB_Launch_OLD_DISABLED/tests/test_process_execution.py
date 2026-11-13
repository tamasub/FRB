import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
import app as module
from process_runner import start_process

class ProcessExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])
        cls.temp=tempfile.TemporaryDirectory();module.STATE=Path(cls.temp.name)
        module.windows.hotkey=lambda *a:None;module.windows.unhotkey=lambda *a:None

    def setUp(self):self.w=module.Launcher()
    def tearDown(self):self.w.dismiss();self.w.tray.hide();self.w.deleteLater();self.app.processEvents()

    def wait_done(self):
        for _ in range(100):
            QTest.qWait(20)
            if not self.w.busy:return
        self.fail('launcher remained busy')

    def test_detached_run_releases_launcher(self):
        self.w.execute({'launch_actions':[{'launch_action_type':'Run','launch_program':sys.executable,'launch_arguments':['-c','import time; time.sleep(.6)'],'launch_wait_for_exit':False}]})
        self.wait_done()
        self.assertIsNone(self.w.proc.poll())
        self.w.proc.wait(timeout=3)

    def test_wait_success_and_failure(self):
        for code in (0,3):
            QApplication.clipboard().setText('before')
            self.w.execute({'launch_actions':[{'launch_action_type':'Run','launch_program':sys.executable,'launch_arguments':['-c',f'import sys; sys.exit({code})'],'launch_wait_for_exit':True}, {'launch_action_type':'ClipboardCopy','launch_text':'after'}]})
            self.wait_done()
            self.assertEqual(QApplication.clipboard().text(),'after' if code==0 else 'before')

    def test_console_flags_and_exact_config_argument(self):
        import subprocess
        with patch('process_runner.os.name','nt'), patch('process_runner.subprocess.CREATE_NEW_CONSOLE',16,create=True), patch('process_runner.subprocess.CREATE_NO_WINDOW',134217728,create=True), patch('process_runner.subprocess.Popen') as spawn:
            start_process('cmd.exe',['/d','/c','F:\\FRB\\build.bat'],'F:\\FRB',True)
            self.assertEqual(spawn.call_args.kwargs['creationflags'],16)
            self.assertNotIn('stdin',spawn.call_args.kwargs)
        row=next(x for x in self.w.data['items'] if x['item_id']=='studio_app')
        with patch('app.start_process') as spawn:
            self.w.execute(row);self.wait_done()
            self.assertIn('--open-json='+str(module.CONFIG),spawn.call_args.args[1])

if __name__=='__main__':unittest.main()
