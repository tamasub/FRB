import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt, QMimeData, QPointF
from PySide6.QtGui import QDragEnterEvent,QDropEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
import app as module
from ordering import save_order, reordered
from reorder_widgets import MIME

class OrderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])
        cls.sample=module.CONFIG.read_bytes()
        cls.original_config=module.CONFIG

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'launch.json';self.path.write_bytes(self.sample)
        self.patch=patch.object(module,'CONFIG',self.path);self.patch.start()
        self.w=module.Launcher();self.w.page_id='work';self.w.render();self.w.show();self.app.processEvents()

    def tearDown(self):
        self.w.dismiss();self.w.tray.hide();self.w.deleteLater();self.app.processEvents();self.patch.stop();self.temp.cleanup()

    def drop(self,widget,source,pos):
        mime=QMimeData();mime.setData(MIME,(str(id(widget))+'\n'+source).encode())
        surface=widget.viewport() if widget==self.w.list else widget
        enter=QDragEnterEvent(pos,Qt.DropAction.MoveAction,mime,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier)
        QApplication.sendEvent(surface,enter);self.assertTrue(enter.isAccepted())
        event=QDropEvent(QPointF(pos),Qt.DropAction.MoveAction,mime,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier)
        QApplication.sendEvent(surface,event);self.assertTrue(event.isAccepted());self.app.processEvents()

    def test_drop_top_and_reload(self):
        before=json.loads(self.path.read_text())
        rows=self.w.list.order_rows;first=rows[0]['item_id'];last=rows[-1]['item_id']
        point=self.w.list.visualItemRect(self.w.list.topLevelItem(0)).topLeft()
        self.drop(self.w.list,last,point)
        self.assertEqual(self.w.children()[0]['item_id'],last)
        self.w.reload(True);self.assertEqual(self.w.children()[0]['item_id'],last)
        after=json.loads(self.path.read_text())
        for old,new in zip(before['items'],after['items']):
            self.assertEqual({k:v for k,v in old.items() if k!='sort_order'},{k:v for k,v in new.items() if k!='sort_order'})
        self.assertEqual(before['launch_variables'],after['launch_variables'])
        self.assertEqual(self.w.children()[1]['item_id'],first)

    def test_cascade_drop_and_filter_gate(self):
        parent=next(r for r in self.w.data['items'] if r['item_id']=='dates')
        self.w.cascade(parent);menu=self.w.menu
        rows=menu.order_rows;last=rows[-1]['item_id']
        self.drop(menu,last,menu.actionGeometry(menu.actions()[0]).topLeft())
        self.assertEqual(menu.order_rows[0]['item_id'],last)
        self.w.search.setText('date');self.assertFalse(self.w.list.order_enabled)
        self.w.search.clear()
        row=next(r for r in self.w.data['items'] if r['item_kind']=='selection');self.w.activate(row)
        self.assertFalse(self.w.list.order_enabled)

    def test_concurrent_edit_is_not_overwritten(self):
        original=self.path.read_text();self.path.write_text(original+'\n')
        ids=[r['item_id'] for r in self.w.children()]
        with self.assertRaises(ValueError):save_order(self.path,self.w.mtime,'work','',list(reversed(ids)))
        self.assertEqual(self.path.read_text(),original+'\n')

if __name__=='__main__':unittest.main()
