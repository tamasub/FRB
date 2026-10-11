import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
import app as module

class FolderEnterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def test_enter_opens_current_folder_and_right_expands(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/'child').mkdir()
            w=module.Launcher();w.show()
            row={'item_kind':'directory','launch_browse_target':tmp}
            w.cascade(row);menu=w.menu
            QTest.keyClick(menu,Qt.Key.Key_Right)
            self.assertTrue(menu.child.isVisible())
            QTest.keyClick(menu.child,Qt.Key.Key_Left)
            with patch.object(w,'execute') as execute:
                QTest.keyClick(menu,Qt.Key.Key_Return)
                self.assertEqual(execute.call_args.args[0]['launch_actions'][0]['launch_target'],str(Path(tmp)/'child'))
                self.assertFalse(menu.isVisible())
            w.dismiss();w.tray.hide();w.deleteLater();self.app.processEvents()
    def test_work_file_uses_os_association(self):
        w=module.Launcher()
        row=next(r for r in w.data['items'] if r['item_id']=='experiment_overview_excel')
        target=row['launch_actions'][0]['launch_target']
        self.assertEqual(target,'F:\\FRB_docsExcel\\実験全体図.xlsx')
        with patch.object(module.windows,'IS_WINDOWS',True),patch.object(module.os,'startfile',create=True) as start:
            w.open_target(target);start.assert_called_once_with(target)
        w.tray.hide();w.deleteLater();self.app.processEvents()

if __name__=='__main__':unittest.main()
