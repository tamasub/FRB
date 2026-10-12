import unittest
from PySide6.QtCore import Qt,QPoint,QPointF
from PySide6.QtGui import QWheelEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
import test_apps_ui as apps_ui
import installed_apps
import app as module

class AppScrollingTests(unittest.TestCase):
    setUpClass=classmethod(apps_ui.AppsUITests.setUpClass.__func__)
    setUp=apps_ui.AppsUITests.setUp
    tearDown=apps_ui.AppsUITests.tearDown
    def open_large(self):
        self.w.app_records=[dict(name=f'Application {i:03}',target=f'Tool{i}',kind='aumid') for i in range(200)]
        self.w.data=installed_apps.attach(self.w.data,self.w.app_records)
        parent=next(r for r in self.w.data['items'] if r['item_id']=='installed_apps')
        self.w.cascade(parent);self.qt.processEvents()
        return self.w.menu
    def test_repeated_arrows_and_long_scroll(self):
        menu=self.open_large();self.assertIsInstance(menu,module.AppCascadeMenu)
        for i in range(80):QTest.keyClick(menu.tree,Qt.Key.Key_Down)
        self.assertEqual(menu.tree.indexOfTopLevelItem(menu.tree.currentItem()),80)
        self.assertGreater(menu.tree.verticalScrollBar().value(),0)
        QTest.keyClick(menu.tree,Qt.Key.Key_End)
        self.assertEqual(menu.tree.indexOfTopLevelItem(menu.tree.currentItem()),199)
        QTest.keyClick(menu.tree,Qt.Key.Key_Home)
        self.assertEqual(menu.tree.indexOfTopLevelItem(menu.tree.currentItem()),0)
        QTest.keyClick(menu.tree,Qt.Key.Key_PageDown)
        self.assertGreater(menu.tree.indexOfTopLevelItem(menu.tree.currentItem()),1)
    def test_wheel_search_and_left(self):
        menu=self.open_large();bar=menu.tree.verticalScrollBar();bar.setValue(0)
        event=QWheelEvent(QPointF(10,10),QPointF(10,10),QPoint(),QPoint(0,-120),Qt.MouseButton.NoButton,Qt.KeyboardModifier.NoModifier,Qt.ScrollPhase.NoScrollPhase,False)
        QApplication.sendEvent(menu.tree.viewport(),event)
        self.assertEqual(bar.value(),105)
        QTest.keyClick(menu.tree,Qt.Key.Key_F,Qt.KeyboardModifier.ControlModifier)
        self.assertFalse(menu.isVisible())
        self.w.cascade(next(r for r in self.w.data['items'] if r['item_id']=='installed_apps'))
        menu=self.w.menu;QTest.keyClicks(menu.tree,'Application 199')
        self.assertEqual(self.w.search.text(),'Application 199')
        self.assertIn('Application 199',[self.w.list.topLevelItem(i).data(0,Qt.ItemDataRole.UserRole)['title'] for i in range(self.w.list.topLevelItemCount())])
        self.w.search.clear();self.w.cascade(next(r for r in self.w.data['items'] if r['item_id']=='installed_apps'))
        menu=self.w.menu;QTest.keyClick(menu.tree,Qt.Key.Key_Left);self.assertFalse(menu.isVisible())

    def test_thin_scrollbar_can_still_reach_last_item(self):
        menu=self.open_large();bar=menu.tree.verticalScrollBar()
        self.assertTrue(bar.isVisible())
        self.assertEqual(bar.width(),8)
        bar.setValue(bar.maximum());self.qt.processEvents()
        last=menu.tree.visualItemRect(menu.tree.topLevelItem(199))
        self.assertTrue(menu.tree.viewport().rect().intersects(last))
