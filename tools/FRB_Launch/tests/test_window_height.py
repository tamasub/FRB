import test_window_frame
import test_navigation
from PySide6.QtCore import Qt, QPointF, QEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

class WindowHeightTests(test_window_frame.WindowFrameTests):
    def drag_edge(self, edge, delta):
        w=self.w
        local=QPointF(100, 2 if edge=='top' else w.height()-2)
        global_start=QPointF(w.mapToGlobal(local.toPoint()))
        QApplication.sendEvent(w,QMouseEvent(QEvent.Type.MouseButtonPress,local,global_start,Qt.MouseButton.LeftButton,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier))
        end=global_start+QPointF(0,delta)
        QApplication.sendEvent(w,QMouseEvent(QEvent.Type.MouseMove,local+QPointF(0,delta),end,Qt.MouseButton.NoButton,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier))
        QApplication.sendEvent(w,QMouseEvent(QEvent.Type.MouseButtonRelease,local+QPointF(0,delta),end,Qt.MouseButton.LeftButton,Qt.MouseButton.NoButton,Qt.KeyboardModifier.NoModifier))
        self.app.processEvents()

    def test_bottom_changes_only_height_and_restores_new_instance(self):
        w=self.w;w.resize(w.width(),440);original=w.geometry()
        self.drag_edge('bottom',90)
        self.assertEqual(w.height(),530)
        self.assertEqual(w.width(),original.width())
        self.assertEqual(w.pos(),original.topLeft())
        w.dismiss()
        second=test_navigation.module.Launcher()
        try: self.assertEqual(second.height(),530)
        finally: second.dismiss();second.tray.hide();second.deleteLater()

    def test_top_keeps_bottom_fixed_and_minimum_clamps(self):
        w=self.w;w.resize(w.width(),440);bottom=w.y()+w.height()
        self.drag_edge('top',-60)
        self.assertEqual(w.height(),500)
        self.assertEqual(w.y()+w.height(),bottom)
        self.drag_edge('top',2000)
        self.assertGreaterEqual(w.height(),w.minimumHeight())
        self.assertEqual(w.y()+w.height(),bottom)

    def test_invalid_saved_height_uses_default_and_large_value_clamps(self):
        w=self.w
        w.settings.setValue('window_height','invalid');w.restore_window_height()
        self.assertEqual(w.height(),440)
        w.settings.setValue('window_height',99999);w.restore_window_height()
        self.assertLessEqual(w.height(),w.screen().availableGeometry().height())
