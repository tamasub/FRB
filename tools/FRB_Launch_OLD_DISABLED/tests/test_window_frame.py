"""Window frame colors, drag boundary and fallback movement."""
import test_navigation
from unittest.mock import patch
from PySide6.QtCore import Qt, QPoint, QPointF, QEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

class WindowFrameTests(test_navigation.NavigationTests):
    test_immediate_right_and_left = None
    test_nested_and_directory_single_column = None
    test_function_page_keys = None
    test_selection_all_clear_and_back = None

    def test_frame_bounds_and_content_are_separate(self):
        w=self.w
        for p in [QPointF(30,10),QPointF(3,100),QPointF(w.width()-3,100),QPointF(30,w.height()-3)]:
            self.assertTrue(w.frame_hit(p))
        self.assertFalse(w.frame_hit(QPointF(30,60)))
        self.assertFalse(w.frame_hit(QPointF(-1,10)))
        self.assertGreaterEqual(w.search.y(),32)

    def test_drag_moves_window_and_keeps_saved_position(self):
        w=self.w;start=w.pos();local=QPointF(30,10);global_start=QPointF(w.mapToGlobal(QPoint(30,10)))
        with patch.object(w,'windowHandle',return_value=None):
            QApplication.sendEvent(w,QMouseEvent(QEvent.Type.MouseButtonPress,local,global_start,Qt.MouseButton.LeftButton,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier))
        delta=QPointF(45,25)
        QApplication.sendEvent(w,QMouseEvent(QEvent.Type.MouseMove,local+delta,global_start+delta,Qt.MouseButton.NoButton,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier))
        self.assertEqual(w.pos(),start+QPoint(45,25))
        QApplication.sendEvent(w,QMouseEvent(QEvent.Type.MouseButtonRelease,local+delta,global_start+delta,Qt.MouseButton.LeftButton,Qt.MouseButton.NoButton,Qt.KeyboardModifier.NoModifier))
        self.assertIsNone(w._frame_drag)
        w.dismiss();self.assertEqual(w.settings.value('position'),w.pos())

    def test_frame_has_light_outer_and_inner_lines(self):
        image=self.w.grab().toImage()
        outer=image.pixelColor(30,0);inner=image.pixelColor(30,24);body=image.pixelColor(8,60)
        self.assertGreater(outer.lightness(),body.lightness()+60)
        self.assertGreater(inner.lightness(),body.lightness()+40)

    def test_title_is_visible_and_does_not_intercept_frame_drag(self):
        self.assertEqual(self.w.frame_title.text(),'FRB Launch')
        self.assertTrue(self.w.frame_title.isVisible())
        self.assertTrue(self.w.frame_title.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents))
        self.assertTrue(self.w.frame_hit(QPointF(self.w.frame_title.geometry().center())))
