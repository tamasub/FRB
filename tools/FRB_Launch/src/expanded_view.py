"""Optional three-layer launcher view: Page -> root actions -> parallel panels.

This is a QWidget INSIDE the main window (never a second Qt.Tool popup).
All rows/actions are supplied by Launcher and use its existing menu data.
"""
from PySide6.QtCore import Qt, QPoint, QPointF, QSize, QTimer, QEvent, QRectF, QFileInfo, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPainterPath, QPixmap, QLinearGradient, QPen, QPalette, QCursor
from PySide6.QtWidgets import (QApplication, QFrame, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QTreeWidget, QTreeWidgetItem, QHeaderView, QAbstractItemView,
    QScrollArea, QSplitter, QSizePolicy, QLineEdit, QStackedWidget, QToolButton, QMenu, QFileIconProvider, QStyledItemDelegate, QAbstractItemDelegate, QStyleOptionViewItem, QStyle)

from file_drag import ExternalFileDragTree

from directory_address import (breadcrumb_segments, compact_segments,
                               directory_row, row_directory, normalized_directory)
from browser_nav_icons import browser_navigation_icon
from directory_navigation_history import DirectoryNavigationHistory
from expanded_left_navigation import matching_first_row
from popup_sizing import popup_available_height, popup_tree_height
from system_drives import drive_rows, pc_preview_row
from expanded_view_model import toolbar_roots, root_wheel_target
from page_presentation import page_display_title
from expanded_selection import context_paths, physical_paths
from middle_selection_guard import repair_middle_selection, row_key
from clipboard_paste import clipboard_sources
from virtual_clipboard_paste import is_virtual_file_clipboard
from context_menu_resolver import resolve_context_target
from context_menu_actions import rename_file_or_folder
from pathlib import Path
import os
from middle_folder_filter import SORT_LABELS, filter_sort_folder_rows, sort_mode_for_header
from middle_column_presentation import (FILES_HEADERS, LAUNCH_HEADERS,
    virtual_description, virtual_item_kind, virtual_sort_mode_for_header)
from folder_sort_preferences import (DEFAULT_SORT, load_directory_sort,
                                     save_directory_sort)
from windows_shellnew import discover_shellnew, suggest_name, create_new_item
from folder_favorites import FolderFavorites
from files_list_search_history import FilesListSearchHistory
from combo_chevron_icon import combo_chevron_icon
from reorderable_tree import ReorderablePopupTree
from bookmark_cursor_follow import cursor_target, is_warp_generated_mouse_move
from wheel_adaptive import wheel_steps, can_follow_at_edge, monotonic_edge_anchor
from navigation_wrap import move_tree_selection
from shuriken_trace import trace as shuriken_trace, bar_state as shuriken_bar_state
from list_wheel_parity import (
    LIST_WHEEL_MATCH_REMOTE, LIST_WHEEL_HYBRID_ENABLED,
    LIST_WHEEL_SCROLL_PIXELS_PER_NOTCH,
    consume_remote_like_wheel, plan_hybrid_scroll)
from wheel_edge_hold import EdgeWheelHold
from wheel_zone_navigation import WheelZoneNavigation
from workspace_tab_geometry import workspace_tab_line_segments
from history_wheel_navigation import history_target_index, warp_to_history_row
from bookmark_menu import expanded_bookmark_rows
from launch_virtual_tree import (virtual_list_rows, virtual_lookup_node,
                                 virtual_exp_presentation, virtual_item_identity)
from launch_menu_registration import mime_sources
from launch_appearance import (theme_palette, theme_family, scrollbar_for_theme,
                               history_popup_qss, bookmark_section_colors)


MIDDLE_BACK_LANE_WIDTH = 24  # Left-edge operation lane beside the file grid.


class _WorkspaceSeamOverlay(QWidget):
    """Draw the selected tab and the content seam as ONE continuous contour.

    Previously the selected QPushButton drew its own vertical border while a
    separate 2px strip drew a horizontal line. Those strokes cannot produce a
    joined rounded corner and leave visible 1px stubs / missing arcs.
    This transparent overlay owns the ENTIRE contour, over the tab children.
    """

    def __init__(self, strip):
        super().__init__(strip)
        self.strip = strip
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

    def paintEvent(self, event):
        super().paintEvent(event)
        strip = self.strip
        end = float(strip.width()) - 0.5
        if strip._end_provider is not None:
            bound = strip._end_provider()
            if bound is not None:
                end = min(end, float(bound) - 0.5)
        # The horizontal stroke must STOP where the content pane's rounded
        # upper-right arc begins, not extend straight through that arc.
        if strip._corner_end_provider is not None:
            corner_end = strip._corner_end_provider()
            if corner_end is not None:
                end = min(end, float(corner_end) - 11.5)
        if end <= 0.5:
            return
        y = float(self.height()) - 0.5
        active = strip._selected_tab
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QPen(strip._underline_color, 1.0,
                            Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap,
                            Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        outline = QPainterPath()
        outline.moveTo(0.5, y)
        if active is None or not active.isVisible():
            outline.lineTo(end, y)
        else:
            rect = active.geometry()
            left = float(rect.left()) + 0.5
            right = float(rect.right()) + 0.5
            top = float(rect.top()) + 0.5
            # Top corner curves are inside the selected button; lower curves
            # fan OUT into the content rule (like a browser-tab joint).
            top_radius = min(11.0, max(1.0, (right - left) / 4))
            left_radius = min(7.0, max(0.0, left - 1.0))
            right_radius = min(7.0, max(0.0, end - right - 1.0))
            k = 0.55228475   # cubic approximation of a quarter circle
            outline.lineTo(max(0.5, left - left_radius), y)
            if left_radius > 0:
                outline.cubicTo(left - (1-k)*left_radius, y,
                                left, y - (1-k)*left_radius,
                                left, y - left_radius)
            else:
                outline.lineTo(left, y)
            outline.lineTo(left, top + top_radius)
            outline.cubicTo(left, top + (1-k)*top_radius,
                            left + (1-k)*top_radius, top,
                            left + top_radius, top)
            outline.lineTo(right - top_radius, top)
            outline.cubicTo(right - (1-k)*top_radius, top,
                            right, top + (1-k)*top_radius,
                            right, top + top_radius)
            outline.lineTo(right, y - right_radius)
            if right_radius > 0:
                outline.cubicTo(right, y - (1-k)*right_radius,
                                right + (1-k)*right_radius, y,
                                right + right_radius, y)
            else:
                outline.lineTo(right, y)
            outline.lineTo(end, y)
        painter.drawPath(outline)
        painter.end()


class _WorkspaceTabStrip(QWidget):
    """Mouse-transparent top contour spanning tab corners and underline."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_tab = None
        self._underline_color = QColor('#bbd8c7')
        self._end_provider = None
        self._corner_end_provider = None
        self._seam_overlay = _WorkspaceSeamOverlay(self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Full height is essential: selected-tab top corners and lower joined
        # corners must be drawn by the same painter, above the QPushButtons.
        self._seam_overlay.setGeometry(0, 0, self.width(), self.height())
        self.refresh_underline()

    def refresh_underline(self):
        self._seam_overlay.raise_()
        self._seam_overlay.update()

    def set_selected_tab(self, button):
        self._selected_tab = button
        self.refresh_underline()

    def set_underline_color(self, value):
        self._underline_color = QColor(value)
        self.refresh_underline()

    def set_underline_end_provider(self, provider):
        """Browser rule ends at the Web pane boundary, not at Bookmarks."""
        self._end_provider = provider
        self.refresh_underline()

    def set_corner_end_provider(self, provider):
        """Join the content pane's own top-right curve with no straight stub."""
        self._corner_end_provider = provider
        self.refresh_underline()


class _WorkspaceTopRightOutline(QWidget):
    """Visible antialiased outer corner where QSS border-top is intentionally 0.

    This overlay lives ABOVE the header or Web frame's stylesheet; otherwise
    the header's opaque background obscures a border drawn by its parent.
    """

    def __init__(self, host, radius=11):
        super().__init__(host)
        self._host = host
        self._radius = radius
        self._color = QColor('#bbd8c7')
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self._host.installEventFilter(self)
        self.update_geometry()

    def update_geometry(self):
        r = self._radius
        self.setGeometry(max(0, self._host.width() - r - 1), 0, r+1, r+2)
        self.raise_()
        self.update()

    def set_outline_color(self, color):
        self._color = QColor(color)
        self.update_geometry()

    def eventFilter(self, obj, event):
        if obj is self._host and event.type() in (QEvent.Type.Resize, QEvent.Type.Show):
            self.update_geometry()
        return False

    def paintEvent(self, event):
        super().paintEvent(event)
        r = float(self._radius)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QPen(self._color, 1.0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        curve = QPainterPath()
        # Top horizontal becomes the rounded upper-right vertical outline.
        curve.moveTo(0.5, 0.5)
        curve.cubicTo(r*0.55228475, 0.5, r+0.5, r*(1-0.55228475),
                      r+0.5, r+0.5)
        painter.drawPath(curve)
        painter.end()


class _BackLaneWidget(QWidget):
    """Fixed-width operation lane at the LEFT of the Files second-column grid.

    Public-release polish removed the old right-edge separator so the lane and
    the lower blank Files List viewport read as one L-shaped area.  The lane
    still remains outside the QTreeWidget viewport, so it cannot select a file
    or become an accidental paste/rename target.
    """

    def __init__(self, view, parent=None):
        super().__init__(parent)
        self.view = view

    def paintEvent(self, event):
        # Intentionally blank: keep the lane visually merged with Files List.
        super().paintEvent(event)


class _FilesHistoryButton(QToolButton):
    """Native click/double-click separation, matching Remote's history key.

    A click on the first release of a double-click must not select/confirm a
    search history row before the actual double-click executes its result.
    """
    double_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._double_pending = False

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._double_pending = True
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event):
        if self._double_pending and event.button() == Qt.MouseButton.LeftButton:
            self._double_pending = False
            if self.rect().contains(event.position().toPoint()):
                self.double_clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)


def _files_history_icon(theme):
    """A small, theme-aware magnifier consistent with the Launch search icon."""
    pix = QPixmap(48, 48)
    pix.setDevicePixelRatio(2)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    pen = QPen(QColor('#647c70' if theme_family(theme) == 'light' else '#e3eee7'))
    pen.setWidthF(1.8)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.drawEllipse(QRectF(5, 4, 13, 13))
    painter.drawLine(QPointF(16, 16), QPointF(20, 20))
    painter.end()
    return QIcon(pix)


def _files_list_keyword_history_icon(theme):
    """Small clock/history glyph matching the breadcrumb 30px toolbutton."""
    pix = QPixmap(48, 48)
    pix.setDevicePixelRatio(2)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    color = '#647c70' if theme_family(theme) == 'light' else '#e3eee7'
    pen = QPen(QColor(color), 1.7)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(QRectF(3, 3, 17, 17))
    painter.drawLine(QPointF(11.5, 6.0), QPointF(11.5, 11.5))
    painter.drawLine(QPointF(11.5, 11.5), QPointF(15.0, 13.5))
    painter.end()
    return QIcon(pix)


def header_icon(kind, theme):
    """Panel badges. Preserve the original folder; render the ribbon at true HiDPI."""
    if kind != 'bookmark':
        # Exact pre-2026-10-24-19:07 folder silhouette and logical size.
        # Do not scale the painter: the previous green cropped shape was an
        # unintended extra painter transform atop devicePixelRatio(2).
        pix = QPixmap(28, 28)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor('#8cbf68' if theme == 'light' else '#a7d785'))
        p.drawRoundedRect(3, 8, 22, 16, 3, 3)
        p.drawRoundedRect(5, 5, 11, 8, 2, 2)
        p.end()
        return QIcon(pix)

    # 2x backing pixels, 28 logical pixels; Qt handles the DPR automatically.
    # The sample has a soft green rounded top and a clear centred V-notch.
    pix = QPixmap(56, 56)
    pix.setDevicePixelRatio(2)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    ribbon = QPainterPath()
    ribbon.moveTo(6.5, 4.0)
    ribbon.cubicTo(5.0, 4.0, 4.0, 5.2, 4.0, 6.7)
    ribbon.lineTo(4.0, 24.5)
    ribbon.cubicTo(4.0, 25.3, 4.9, 25.7, 5.5, 25.2)
    ribbon.lineTo(14, 19.5)
    ribbon.lineTo(22.5, 25.2)
    ribbon.cubicTo(23.1, 25.7, 24, 25.3, 24, 24.5)
    ribbon.lineTo(24, 6.7)
    ribbon.cubicTo(24, 5.2, 23, 4, 21.5, 4)
    ribbon.closeSubpath()
    # Keep the color quiet and close to the mint screenshot, not glossy.
    gradient = QLinearGradient(4, 4, 24, 26)
    gradient.setColorAt(0, QColor('#59b895' if theme == 'light' else '#83d2b5'))
    gradient.setColorAt(1, QColor('#3ca586' if theme == 'light' else '#56b898'))
    p.setBrush(gradient)
    p.drawPath(ribbon)
    p.end()
    return QIcon(pix)


class _NavigationChevronDelegate(QStyledItemDelegate):
    """Quiet, small chevron with an intentional right-side inset."""

    def __init__(self, parent=None, right_inset=20):
        super().__init__(parent)
        self.right_inset = right_inset

    def createEditor(self, parent, option, index):
        # Column 1 is a navigation glyph, never a filename editor.
        return None

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        if not index.data(Qt.ItemDataRole.UserRole):
            return
        center_x = option.rect.right() - self.right_inset  # leave the middle Back lane clear
        center_y = option.rect.center().y()
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(option.palette.color(QPalette.ColorRole.Text), 1.6,
                            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                            Qt.PenJoinStyle.RoundJoin))
        chevron = QPainterPath()
        chevron.moveTo(center_x - 2.5, center_y - 4)
        chevron.lineTo(center_x + 2, center_y)
        chevron.lineTo(center_x - 2.5, center_y + 4)
        painter.drawPath(chevron)
        painter.restore()


def link_icon(theme):
    """Mint link badge inspired by the mockup; rendered as vectors at any DPI."""
    pix = QPixmap(24, 24)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor('#a4e5d5' if theme == 'light' else '#468e7d'))
    painter.drawRoundedRect(1, 1, 22, 22, 5, 5)
    pen = painter.pen()
    pen.setColor(QColor('#176d61' if theme == 'light' else '#e0fff0'))
    pen.setWidthF(1.9)
    pen.setStyle(Qt.PenStyle.SolidLine)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(5, 11, 9, 7)
    painter.drawEllipse(10, 6, 9, 7)
    painter.drawLine(10, 14, 15, 10)
    painter.end()
    return QIcon(pix)


def density_lines_icon(theme):
    """Three crisp horizontal strokes centered like the Web nav icons."""
    # The Web navigation glyphs share a 24x24 logical vector canvas.
    # The HiDPI pixmap provides the 2x scale implicitly (as in
    # browser_nav_icons.py). Paint in 24px logical coordinates: the old
    # strokes occupied only the upper-left of the oversized physical canvas.
    pix = QPixmap(48, 48)
    pix.setDevicePixelRatio(2)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor('#425750' if theme == 'light' else '#d5e3ed'), 2.0)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    for y in (7, 12, 17):
        painter.drawLine(QPointF(5.5, y), QPointF(18.5, y))
    painter.end()
    return QIcon(pix)


class _ReadOnlyMetadataDelegate(QStyledItemDelegate):
    """Display file properties without allowing Qt to edit their cells.

    QTreeWidgetItem's ItemIsEditable flag applies to the whole row, so the
    SelectedClicked rename trigger would otherwise make the date, size and
    file-type columns editable as well as the filename.
    """

    def createEditor(self, parent, option, index):
        return None


class _InlineRenameDelegate(QStyledItemDelegate):
    """Keep the editor text exactly the same size as its surrounding row."""

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            editor.setObjectName('inlineRenameEditor')
            editor.setFont(option.font)
            pixels = option.font.pixelSize()
            if pixels <= 0:
                pixels = parent.font().pixelSize()
            # The generic application QLineEdit rule is 15px, whereas the
            # expanded list uses 13px. Override the generic stylesheet here.
            editor.setStyleSheet(
                'QLineEdit#inlineRenameEditor { '
                f'font-size:{pixels if pixels > 0 else 13}px; '
                'padding:0px 3px; }')
        return editor

    def eventFilter(self, obj, event):
        """Enter commits the filename ONLY; it must never activate the row.

        QTreeWidget.itemActivated (and the launcher's Enter keyboard router)
        otherwise may treat the same Enter as a request to open the file,
        which dismisses the FRB Launch window. Intercept at the actual Qt
        editor, where both SelectedClicked and context-menu renames arrive.
        """
        if (isinstance(obj, QLineEdit)
                and obj.objectName() == 'inlineRenameEditor'
                and event.type() == QEvent.Type.KeyPress
                and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)):
            tree = self.parent()
            if isinstance(tree, QTreeWidget):
                # Guard synchronous AND shortly deferred itemActivated signals.
                # Epoch protects a newer edit from an older release timer.
                tree._rename_enter_epoch = getattr(tree, '_rename_enter_epoch', 0) + 1
                epoch = tree._rename_enter_epoch
                tree._rename_enter_guard = True
                def release_guard():
                    if getattr(tree, '_rename_enter_epoch', None) == epoch:
                        tree._rename_enter_guard = False
                QTimer.singleShot(120, release_guard)
            self.commitData.emit(obj)
            self.closeEditor.emit(obj, QAbstractItemDelegate.EndEditHint.NoHint)
            event.accept()
            return True
        return super().eventFilter(obj, event)

    def paint(self, painter, option, index):
        """Leave native icon/background painting intact for drive entries.

        The actual drive name is painted *last* in _SeparatedFileTree.drawRow:
        on Windows, the delegate's text sub-element can be clipped to an empty
        rectangle by the platform/QSS combination. Non-drive rows remain
        completely native and still support inline rename.
        """
        row = index.data(Qt.ItemDataRole.UserRole)
        if index.column() != 0 or not isinstance(row, dict) or not row.get('_system_drive'):
            super().paint(painter, option, index)
            return
        native = QStyleOptionViewItem(option)
        self.initStyleOption(native, index)
        native.text = ''  # Do not draw a duplicate beneath the final label.
        style = native.widget.style() if native.widget else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem,
                          native, painter, native.widget)



class _MiddleDetailsDelegate(_InlineRenameDelegate):
    """File name and muted right-aligned date/size in the SAME name column.

    This preserves the separate chevron column and existing inline rename.
    """
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        detail = index.data(Qt.ItemDataRole.UserRole + 2) or ''
        if detail and index.column() == 0:
            mode = index.data(Qt.ItemDataRole.UserRole + 3) or ''
            meta_width = 130 if mode == 'date' else 90
            # The default delegate initializes its option afresh in paint(),
            # so elision belongs HERE, not in a temporary paint() option.
            space = max(12, option.rect.width() - meta_width - 40)
            option.text = option.fontMetrics.elidedText(
                option.text, Qt.TextElideMode.ElideRight, space)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        if index.column() != 0:
            return
        detail = index.data(Qt.ItemDataRole.UserRole + 2) or ''
        if not detail:
            return
        mode = index.data(Qt.ItemDataRole.UserRole + 3) or ''
        width = 130 if mode == 'date' else 90
        painter.save()
        font = QFont(option.font)
        if font.pointSizeF() > 0:
            font.setPointSizeF(max(7.5, font.pointSizeF() - 1.0))
        painter.setFont(font)
        theme = getattr(self.parent(), 'details_theme', 'light')
        painter.setPen(QColor('#71877f' if theme == 'light' else '#9faea8'))
        rect = option.rect.adjusted(0, 0, -9, 0)
        rect.setLeft(max(rect.left(), rect.right() - width))
        painter.drawText(rect, Qt.AlignmentFlag.AlignRight |
                         Qt.AlignmentFlag.AlignVCenter, str(detail))
        painter.restore()


def middle_sort_icon(theme, mode='name'):
    """Compact, HiDPI-safe sort icons: A/Z, calendar, or size bars + direction.

    The 48px backing image has DPR=2, so QPainter coordinates MUST remain
    within the 24x24 logical canvas (the old icon drew beyond a 20x20 canvas).
    """
    mode = mode if mode in SORT_LABELS else 'name'
    pix = QPixmap(48, 48)
    pix.setDevicePixelRatio(2)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    color = QColor('#426b58' if theme == 'light' else '#d5e8dc')
    pen = QPen(color, 1.6)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    if mode == 'name':
        # Recognisable alphabetical sorting, rather than anonymous lines.
        font = QFont('Segoe UI')
        font.setPixelSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(1.5, 1.0, 12, 11),
                         Qt.AlignmentFlag.AlignCenter, 'A')
        painter.drawText(QRectF(1.5, 12, 12, 11),
                         Qt.AlignmentFlag.AlignCenter, 'Z')
    elif mode.startswith('date'):
        # Calendar silhouette and two day markers.
        painter.drawRoundedRect(QRectF(2.5, 5, 13.5, 15), 2, 2)
        painter.drawLine(QPointF(2.8, 10), QPointF(15.5, 10))
        painter.drawLine(QPointF(6, 3.6), QPointF(6, 7))
        painter.drawLine(QPointF(12.2, 3.6), QPointF(12.2, 7))
        painter.drawPoint(QPointF(7, 14))
        painter.drawPoint(QPointF(11.5, 14))
    else:
        # Three horizontal file-size bars, different lengths on purpose.
        painter.drawLine(QPointF(3, 6), QPointF(8, 6))
        painter.drawLine(QPointF(3, 12), QPointF(11, 12))
        painter.drawLine(QPointF(3, 18), QPointF(15, 18))

    # Name order is A -> Z; descending goes down, ascending goes up.
    ascending = mode in ('date_asc', 'size_asc')
    painter.drawLine(QPointF(20, 5), QPointF(20, 19))
    if ascending:
        painter.drawLine(QPointF(16.8, 8.3), QPointF(20, 5))
        painter.drawLine(QPointF(23.2, 8.3), QPointF(20, 5))
    else:
        painter.drawLine(QPointF(16.8, 15.7), QPointF(20, 19))
        painter.drawLine(QPointF(23.2, 15.7), QPointF(20, 19))
    painter.end()
    return QIcon(pix)


class _SeparatedFileTree(ExternalFileDragTree):
    """Inset, hairline row separators and a passive current-row outline."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.separator_color = QColor('#eaf0eb')
        self.separator_inset = 12
        self.separator_width = 0.65
        self.inactive_current_border = QColor('#8fc7ab')
        self.remote_logical_active = False
        self.remote_highlight_mode = False
        self.adaptive_wheel_callback = None  # Only enabled on Files middle pane.
        self.remote_parity_wheel_callback = None  # Experimental List-only A/B switch.
        # The outline remembers the previous row without selecting it. A real
        # blank click intentionally leaves the middle pane with no selection.
        self.deliberate_blank_selection = False
        self.blank_clicked = None

    def _launch_drop_target(self, event):
        callback = getattr(self, 'launch_registration_resolver', None)
        return callback(event.position().toPoint(), event.mimeData()) if callable(callback) else False

    def dragEnterEvent(self, event):
        if self._launch_drop_target(event) is not False:
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if self._launch_drop_target(event) is not False:
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        target = self._launch_drop_target(event)
        if target is False:
            event.ignore()
            return
        callback = getattr(self, 'launch_registration_handler', None)
        if callable(callback) and callback(target, event.mimeData()):
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def wheelEvent(self, event):
        # List-only experiment: the same current-row navigation as the Remote
        # ぐりぐり button. All other trees keep their existing native WAN flow.
        remote_parity = self.remote_parity_wheel_callback
        if remote_parity is not None and remote_parity(event):
            event.accept()
            return
        # Preserve native smooth scrolling first; only the actual change in
        # scrollbar position may trigger WAN's cursor-follow fallback.
        scrollbar = self.verticalScrollBar()
        before = scrollbar.value()
        super().wheelEvent(event)
        callback = self.adaptive_wheel_callback
        if callback is not None and callback(event, before, scrollbar.value()):
            event.accept()

    def mousePressEvent(self, event):
        # Freeze automatic shuriken before a normal List click is handled.
        # Manual Remote shuriken and other tree columns are unaffected.
        stop_auto = getattr(self, 'shuriken_stop_on_action', None)
        if (callable(stop_auto) and event.button() in
                (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton)):
            stop_auto()
        if (self.selectionMode() == QAbstractItemView.SelectionMode.ExtendedSelection
                and event.button() == getattr(Qt.MouseButton, 'LeftButton', None)
                and event.modifiers() == Qt.KeyboardModifier.NoModifier
                and self.itemAt(event.position().toPoint()) is None):
            # Unlike a click on an item, blank-space click must NOT select a
            # fallback row. Keep currentItem() only as a passive outline.
            self.deliberate_blank_selection = True
            self.clearSelection()
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            if callable(self.blank_clicked):
                self.blank_clicked()
            self.viewport().update()
            event.accept()
            return
        if (event.button() == getattr(Qt.MouseButton, 'LeftButton', None)
                and self.itemAt(event.position().toPoint()) is not None):
            self.deliberate_blank_selection = False
        if (self.selectionMode() == QAbstractItemView.SelectionMode.ExtendedSelection
                and event.button() == Qt.MouseButton.RightButton):
            # Qt's default right-press can silently ClearAndSelect. Keep all
            # selected rows if clicked inside the selection, like Explorer.
            item = self.itemAt(event.position().toPoint())
            if item is not None and not item.isSelected():
                self.clearSelection()
                self.setCurrentItem(item)
                item.setSelected(True)
            # ContextMenu event is dispatched separately by Qt; never send
            # this right press through QTreeWidget's selection handler.
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if (self.selectionMode() == QAbstractItemView.SelectionMode.ExtendedSelection
                and event.button() == Qt.MouseButton.RightButton):
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.viewport().update()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.viewport().update()

    def _column_is_focused(self):
        """A rename editor is part of the middle pane's keyboard focus."""
        focused = QApplication.focusWidget()
        return bool(self.hasFocus() or
                    (focused is not None and self.isAncestorOf(focused)))

    def drawRow(self, painter, option, index):
        # Bookmarks section labels must remain visually distinct even under
        # QTreeWidget::item QSS (which can override QTreeWidgetItem backgrounds).
        # Paint *only* these non-action rows after Qt's standard delegate draw,
        # keeping all normal row hover/selection/WAN behavior unchanged.
        if (getattr(self.parentWidget(), 'kind', None) == 'bookmark'
                and index.isValid() and not index.parent().isValid()):
            item = self.topLevelItem(index.row())
            if (item is not None and
                    item.data(0, Qt.ItemDataRole.UserRole + 1)):
                super().drawRow(painter, option, index)
                if option.rect.isValid():
                    palette = bookmark_section_colors(self.parentWidget()._theme)
                    painter.save()
                    full_width = self.viewport().width()
                    rect = option.rect
                    # Fill edge-to-edge: a crisp band reads as a group heading,
                    # not another bookmark or an accidentally selected row.
                    painter.fillRect(0, rect.top(), full_width, rect.height(),
                                     QColor(palette['background']))
                    painter.fillRect(0, rect.top(), 4, rect.height(),
                                     QColor(palette['accent']))
                    painter.fillRect(4, rect.bottom(), max(0, full_width - 4), 1,
                                     QColor(palette['divider']))
                    label_font = QFont(self.font())
                    label_font.setBold(True)
                    painter.setFont(label_font)
                    painter.setPen(QColor(palette['text']))
                    label_rect = rect.adjusted(13, 0, -6, 0)
                    painter.drawText(label_rect,
                                     Qt.AlignmentFlag.AlignVCenter |
                                     Qt.AlignmentFlag.AlignLeft,
                                     painter.fontMetrics().elidedText(
                                         item.text(0), Qt.TextElideMode.ElideRight,
                                         max(0, label_rect.width())))
                    painter.restore()
                return
        # Draw the native selected-row fill only for the active pane; the
        # inactive pane's stylesheet suppresses it. Current rows in either
        # pane retain a thin outline as a passive keyboard-position memory.
        # In multi-select, every green filled row ALSO receives a green outline.
        super().drawRow(painter, option, index)
        if not option.rect.isValid():
            return
        # Always render the actual Windows volume name over the native row.
        # In some Qt/Windows styles the delegate's text rectangle collapses
        # even though its shell icon, date and type are present. Drawing here
        # (AFTER all per-column delegates) prevents the label being masked.
        if index.column() == 0:
            item = self.topLevelItem(index.row())
            row = item.data(0, Qt.ItemDataRole.UserRole) if item else None
            if isinstance(row, dict) and row.get('_system_drive'):
                name = str(row.get('title') or item.text(0) or '')
                if name:
                    painter.save()
                    font = QFont(self.font())
                    painter.setFont(font)
                    theme = getattr(self, '_drive_name_theme', 'light')
                    painter.setPen(QColor('#e5ebf3' if theme == 'dark' else '#284238'))
                    # 19px icon plus padding; keep the label wholly inside
                    # column 0 without spilling into the date column.
                    x = option.rect.left() + max(32, self.iconSize().width() + 12)
                    width = max(0, self.columnWidth(0) - (x - option.rect.left()) - 12)
                    if width:
                        text = painter.fontMetrics().elidedText(
                            name, Qt.TextElideMode.ElideRight, width)
                        painter.drawText(QRectF(x, option.rect.top(), width,
                                                option.rect.height()),
                                         Qt.AlignmentFlag.AlignLeft |
                                         Qt.AlignmentFlag.AlignVCenter, text)
                    painter.restore()
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        current = self.currentItem()
        item = self.topLevelItem(index.row()) if not index.parent().isValid() else None
        is_current = (current is not None and
                      self.indexOfTopLevelItem(current) == index.row())
        active_selected = (item is not None and item.isSelected() and
                           self.property('remoteInactive') is not True)
        if is_current or active_selected:
            rect = QRectF(option.rect.adjusted(5, 3, -5, -3))
            painter.setPen(QPen(self.inactive_current_border, 1.15))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect, 6.5, 6.5)
        painter.setPen(QPen(self.separator_color, self.separator_width))
        y = option.rect.bottom()
        inset = self.separator_inset
        if self.viewport().width() > 2 * inset:
            painter.drawLine(QPointF(inset, y),
                             QPointF(self.viewport().width() - inset - 1, y))
        painter.restore()


class _BreadcrumbSurface(QFrame):
    """Click the blank part of the address bar to reveal the full path."""
    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self.setObjectName('addressBreadcrumbSurface')

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.owner.begin_edit()
            event.accept()
            return
        super().mousePressEvent(event)


class DirectoryAddressBar(QStackedWidget):
    """Explorer-like clickable ancestors ↔ selected editable absolute path."""
    def __init__(self, navigate, parent=None):
        super().__init__(parent)
        self.setObjectName('directoryAddressBar')
        self.navigate = navigate
        self.current_path = ''
        self._segments = []
        self._scheduled = False
        self.surface = _BreadcrumbSurface(self)
        self.crumb_layout = QHBoxLayout(self.surface)
        self.crumb_layout.setContentsMargins(64, 1, 4, 1)
        self.crumb_layout.setSpacing(1)
        self.addWidget(self.surface)
        self.editor = QLineEdit(self)
        self.editor.setObjectName('directoryAddressEdit')
        self.editor.setToolTip('Enterでフォルダーへ移動・Escでキャンセル')
        self.editor.returnPressed.connect(self._submit)
        self.editor.installEventFilter(self)
        self.addWidget(self.editor)
        self.setMinimumWidth(75)
        self.setCurrentWidget(self.surface)
        self._overlay_dropdown = None
        self._overlay_favorite = None
        self._overlay_apply = None
        self.editor.textChanged.connect(self._update_apply_visibility)

    def attach_history_dropdown(self, button):
        """Attach a search-style history chevron to the breadcrumb's own frame.

        It remains in place for both breadcrumb and editable-path views.
        """
        self._overlay_dropdown = button
        button.setParent(self)
        button.setFixedSize(24, 26)
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        button.setIconSize(QSize(14, 14))
        self.editor.setTextMargins(64, 0, 0, 0)
        self._position_dropdown()
        button.show()
        button.raise_()
        self._build_crumbs()

    def attach_favorite_save(self, button):
        """Place register/registered heart inside the same address frame."""
        self._overlay_favorite = button
        button.setParent(self)
        button.setFixedSize(27, 26)
        self._position_dropdown()
        button.show()
        self._build_crumbs()

    def attach_path_apply(self, button):
        """Show a confirmation arrow left of the heart for a pending path."""
        self._overlay_apply = button
        button.setParent(self)
        button.setFixedSize(25, 26)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._position_dropdown()
        self._update_apply_visibility()

    def _update_apply_visibility(self, _text=None):
        """Never show the arrow for the folder that is already on screen."""
        from directory_address import pending_directory_change
        candidate = self.editor.text()
        pending = (self.currentWidget() is self.editor and
                   pending_directory_change(candidate, self.current_path))
        if self._overlay_apply is not None:
            self._overlay_apply.setVisible(pending)
            self._overlay_apply.setToolTip(
                f'このフォルダーを表示: {candidate}' if pending else 'このフォルダーを表示')
        # Left-aligned controls must not cover editable paths or breadcrumbs.
        left_margin = 91 if pending else 64
        self.editor.setTextMargins(left_margin, 0, 0, 0)
        self.crumb_layout.setContentsMargins(left_margin, 1, 4, 1)

    def _position_dropdown(self):
        combo = self._overlay_dropdown
        favorite = self._overlay_favorite
        apply = self._overlay_apply
        # All navigation actions start at the LEFT of the breadcrumb bar.
        x = 7
        for button in (combo, favorite, apply):
            if button is None:
                continue
            button.move(x, max(0, (self.height() - button.height()) // 2))
            button.raise_()
            x += button.width() + 3

    def sizeHint(self):
        # A long path must never expand the whole splitter beyond its width.
        return QSize(185, 31)

    def minimumSizeHint(self):
        return QSize(75, 31)

    def set_directory(self, path, label=''):
        self.current_path = normalized_directory(path) or ''
        self._segments = breadcrumb_segments(self.current_path)
        self._fallback_label = label or 'フォルダーを選択'
        if self.currentWidget() is self.editor:
            self.show_breadcrumbs()
        self._build_crumbs()
        self._update_apply_visibility()
        self.setToolTip(self.current_path or self._fallback_label)

    def begin_edit(self):
        self.editor.setText(self.current_path)
        self.setCurrentWidget(self.editor)
        self._position_dropdown()
        self._update_apply_visibility()
        self.editor.setFocus(Qt.FocusReason.MouseFocusReason)
        # Mouse event completion otherwise can reset QLineEdit's selection.
        QTimer.singleShot(0, self.editor.selectAll)

    def show_breadcrumbs(self):
        self.setCurrentWidget(self.surface)
        self._build_crumbs()
        self._position_dropdown()
        self._update_apply_visibility()

    def _submit(self):
        target = normalized_directory(self.editor.text())
        if target and self.navigate(target):
            self.show_breadcrumbs()
        else:
            self.editor.selectAll()
            self.editor.setToolTip('存在する絶対フォルダーパスを入力してください')

    def eventFilter(self, obj, event):
        if obj is self.editor:
            if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
                self.show_breadcrumbs()
                event.accept()
                return True
            if event.type() == QEvent.Type.FocusOut:
                QTimer.singleShot(0, self.show_breadcrumbs)
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_dropdown()
        if not self._scheduled:
            self._scheduled = True
            QTimer.singleShot(0, self._rebuild_after_resize)

    def _rebuild_after_resize(self):
        self._scheduled = False
        self._build_crumbs()

    def _show_hidden(self, button, entries):
        menu = QMenu(button)
        for label, directory in entries:
            action = menu.addAction(label)
            action.setToolTip(directory)
            action.triggered.connect(lambda checked=False, p=directory: self.navigate(p))
        menu.exec(button.mapToGlobal(QPoint(0, button.height())))

    def _build_crumbs(self):
        while self.crumb_layout.count():
            cell = self.crumb_layout.takeAt(0)
            if cell.widget():
                cell.widget().deleteLater()
        if not self._segments:
            placeholder = QLabel(getattr(self, '_fallback_label', 'フォルダーを選択'), self.surface)
            placeholder.setObjectName('addressPlaceholder')
            placeholder.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.crumb_layout.addWidget(placeholder)
            self.crumb_layout.addStretch()
            return
        fm = self.fontMetrics()
        def measure(label):
            return fm.horizontalAdvance(label) + (12 if label != ' › ' else 6)
        # Reserve the left edge for ▼ / heart / optional path confirmation.
        segments = compact_segments(self._segments, self.width() - 18 - 64, measure)
        for index, (label, path) in enumerate(segments):
            if index:
                sep = QLabel('›', self.surface)
                sep.setObjectName('addressSeparator')
                sep.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                self.crumb_layout.addWidget(sep)
            if path is None:
                # Explorer-style overflow menu: omitted ancestors remain
                # clickable instead of turning into unreachable text.
                segment = QToolButton(self.surface)
                segment.setObjectName('addressCrumb')
                segment.setText('…')
                segment.setToolTip('省略された上位フォルダーを表示')
                segment.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                visible = {p for _, p in segments if p is not None}
                hidden = [(text, p) for text, p in self._segments if p not in visible]
                segment.clicked.connect(
                    lambda checked=False, btn=segment, entries=hidden:
                    self._show_hidden(btn, entries))
            else:
                segment = QToolButton(self.surface)
                segment.setObjectName('addressCrumb')
                segment.setText(label)
                segment.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                segment.setToolTip(path)
                if path == self.current_path:
                    # Current folder is already open: clicking it edits the path.
                    # This guarantees an editable hit target even when no blank
                    # header space survives in a narrow middle panel.
                    segment.clicked.connect(self.begin_edit)
                else:
                    segment.clicked.connect(lambda checked=False, p=path: self.navigate(p))
            self.crumb_layout.addWidget(segment)
        self.crumb_layout.addStretch()



class ExpandedPanel(QFrame):
    def __init__(self, label, kind):
        super().__init__()
        self.setObjectName('expandedPanel')
        self.kind = kind
        self.setProperty('panelKind', kind)
        self._theme = 'light'
        self.details_columns = False
        self._file_type_cache = {}
        self._file_icon_provider = QFileIconProvider()
        self.row_height = 37
        self.setMinimumWidth(190)
        self.layout_box = QVBoxLayout(self)
        self.layout_box.setContentsMargins(0, 0, 0, 0)
        self.layout_box.setSpacing(0)
        self.header = QWidget()
        self.header.setObjectName('expandedHeader')
        self._top_right_outline = (_WorkspaceTopRightOutline(self.header)
                                   if kind == 'bookmark' else None)
        header = QHBoxLayout(self.header)
        header.setContentsMargins(12, 6, 10, 6)
        header.setSpacing(8)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(28, 28)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(self.icon_label)
        self.label = QLabel(label)
        self.label.setObjectName('expandedTitle')
        header.addWidget(self.label, 1)
        self.back = QPushButton('')
        self.back.setObjectName('expandedBack')
        self.back.setFixedSize(30, 29)
        self.back.setIconSize(QSize(19, 19))
        self.back.setToolTip('一つ上の階層へ戻る')
        self.back.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.back.setIcon(browser_navigation_icon('back', self._theme))
        header.addWidget(self.back)
        self.back.hide()
        self.layout_box.addWidget(self.header)
        self.tree = _SeparatedFileTree(self)
        self.tree.setObjectName('expandedTree')
        # A real trailing column anchors every navigation chevron to the right.
        self.tree.setColumnCount(2)
        self.tree.header().setStretchLastSection(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.tree.setColumnWidth(1, 40)
        self.tree.setItemDelegateForColumn(1, _NavigationChevronDelegate(self.tree))
        if kind == 'folder':
            self.tree.setItemDelegateForColumn(0, _InlineRenameDelegate(self.tree))
        self.tree.setHeaderHidden(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setIndentation(0)
        self.tree.setSortingEnabled(False)
        self.tree.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tree.verticalScrollBar().setSingleStep(35)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tree.setMouseTracking(True)
        self.tree.setIconSize(QSize(19, 19))
        self.layout_box.addWidget(self.tree, 1)

    def style_bookmark_heading(self, item):
        """Draw a true section label, not a selectable fake bookmark."""
        theme = self._theme
        item.setFirstColumnSpanned(True)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        font = QFont(self.tree.font())
        font.setBold(True)
        item.setFont(0, font)
        item.setForeground(0, QBrush(QColor(
            '#466e5d' if theme == 'light' else '#beded0')))
        backdrop = QBrush(QColor('#eaf4ee' if theme == 'light' else '#31483e'))
        item.setBackground(0, backdrop)
        item.setBackground(1, backdrop)
        item.setSizeHint(0, QSize(0, max(25, self.row_height - 5)))
        item.setSizeHint(1, QSize(0, max(25, self.row_height - 5)))

    def file_type_label(self, row):
        """Match the Windows Explorer-style type column and type sorting."""
        virtual = row.get('_launch_virtual_node')
        if virtual is not None:
            if virtual.get('runtime_catalog') == 'browser_bookmarks':
                return 'ブックマークフォルダー' if virtual['kind'] != 'file' else 'ブックマーク'
            return '仮想フォルダー' if virtual['kind'] != 'file' else 'Launch メニュー'
        if row.get('item_kind') in ('category', 'directory'):
            return 'ファイル フォルダー'
        fallback = row.get('_middle_type', 'ファイル')
        path = (row.get('_browse_file') or row.get('_file')
                or row.get('_indexed_file') or '')
        extension = Path(str(path or row.get('title', ''))).suffix.lower()
        if extension not in self._file_type_cache:
            try:
                self._file_type_cache[extension] = (self._file_icon_provider.type(
                    QFileInfo(str(path))) if path else fallback) or fallback
            except (OSError, ValueError, RuntimeError):
                self._file_type_cache[extension] = fallback
        return self._file_type_cache[extension]

    def fill(self, rows, icon_resolver):
        prior = self.tree.currentItem()
        prior_row = prior.data(0, Qt.ItemDataRole.UserRole) if prior else None
        current_id = (prior_row or {}).get('item_id')
        self.tree.clear()
        for row in rows:
            if self.kind == 'bookmark' and row.get('_bookmark_group_header'):
                heading = QTreeWidgetItem([row.get('title', ''), ''])
                # No UserRole action data: click, Enter, hover, drag and
                # context menu must never execute a section label.
                heading.setData(0, Qt.ItemDataRole.UserRole + 1, True)
                heading.setToolTip(0, row.get('title', ''))
                self.style_bookmark_heading(heading)
                self.tree.addTopLevelItem(heading)
                continue
            is_folder = row.get('item_kind') in ('category', 'directory')
            if self.details_columns:
                # Windows registered descriptions for the file extension, with
                # cheap caching. Actual file properties stay independently
                # available in all sort modes.
                if getattr(self, 'virtual_details_columns', False):
                    # JSON Menu: source description and *original* item_kind.
                    # No fake filesystem update time/size/type is displayed.
                    item = QTreeWidgetItem([row.get('title', ''),
                                            virtual_description(row),
                                            virtual_item_kind(row), '', ''])
                    item.setToolTip(1, virtual_description(row))
                    item.setToolTip(2, virtual_item_kind(row))
                    item.setTextAlignment(1, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    item.setTextAlignment(2, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                else:
                    type_text = self.file_type_label(row)
                    item = QTreeWidgetItem([row.get('title', ''),
                                            row.get('_middle_date', ''),
                                            row.get('_middle_size', ''), type_text, ''])
                    item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    item.setTextAlignment(2, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                for col in (1, 2, 3):
                    item.setForeground(col, QBrush(QColor(
                        '#81928a' if self._theme == 'light' else '#a1afa8')))
                item.setData(4, Qt.ItemDataRole.UserRole, is_folder)
                for col in range(5):
                    item.setSizeHint(col, QSize(0, self.row_height))
            else:
                item = QTreeWidgetItem([row.get('title', ''), ''])
                item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                item.setData(1, Qt.ItemDataRole.UserRole, is_folder)
                for col in (0, 1):
                    item.setSizeHint(col, QSize(0, self.row_height))
            item.setData(0, Qt.ItemDataRole.UserRole, row)
            if self.kind == 'folder':
                # Middle panel filenames can be edited by clicking the already
                # selected row. Directory single click still means navigation.
                origin, path = resolve_context_target(row, ())
                if origin == 'file' and path:
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            if (self.kind == 'bookmark'
                    and row.get('item_kind') not in ('category', 'directory')):
                item.setIcon(0, link_icon(self._theme))
            else:
                item.setIcon(0, icon_resolver(row))
            item.setToolTip(0, row.get('description') or row.get('title', ''))
            self.tree.addTopLevelItem(item)
            if current_id == row.get('item_id'):
                self.tree.setCurrentItem(item)
        if self.tree.topLevelItemCount() and self.tree.currentItem() is None:
            first = next((self.tree.topLevelItem(i)
                          for i in range(self.tree.topLevelItemCount())
                          if self.tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)), None)
            if first is not None:
                self.tree.setCurrentItem(first)


class _NonGrabbingHistoryMenu(QMenu):
    """A QMenu with actions but WITHOUT the normal Qt.Popup mouse grab.

    The Windows Mouse Pointer Rod clicks through SendInput from the remote pad.
    A regular QToolButton InstantPopup captures the mouse, which redirects the
    synthetic click away from the history row and steals the pad's wheel input.
    A Tool-style QMenu follows the already working Page cascade pattern.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Tool |
                            Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint)
        self.setToolTipsVisible(True)


class _MiddleSortButton(QToolButton):
    """Small local keyboard handler for the Files-column sort control.

    Deliberately do NOT install the main Launcher's eventFilter on this child.
    That large filter covers many unrelated widgets/events and can cause a
    nested PySide QWidget::eventFilter failure in the sort-button lifecycle.
    QWidget processes Tab/BackTab in event() before keyPressEvent(), so we
    intercept just those specific keys here and reuse the existing tab ring.
    """

    def __init__(self, launcher, parent=None):
        super().__init__(parent)
        self._sort_launcher = launcher

    def event(self, event):
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
                if self._sort_launcher.expanded_focus_key(self, event):
                    return True
            if (key in (Qt.Key.Key_Return, Qt.Key.Key_Enter,
                        Qt.Key.Key_Space, Qt.Key.Key_Right)
                    and event.modifiers() == Qt.KeyboardModifier.NoModifier):
                # Same native QToolButton/QMenu as a mouse press, not a copied
                # popup. Remote uses its own popup anchor beside the wheel.
                self.showMenu()
                event.accept()
                return True
        return super().event(event)


class ExpandedLauncherView(QWidget):
    """Work Page: root toolbar + Files + active directory + bookmarks.

    Single-clicking a Files directory browses in the middle column; repeated
    clicks in the middle browse deeper.  Back goes up one directory. Other
    folder/bookmark categories use the existing cascade widget and logic.
    """
    def __init__(self, launcher):
        super().__init__(launcher)
        self.launcher = launcher
        self.options = None
        self.root_rows = []
        self.root_buttons = []
        self._wheel_root_id = None
        self._wheel_root_delta = 0
        self._wheel_back_delta = 0
        self._wheel_files_delta = 0
        self._files_first_wan_enabled = True
        self._files_edge_follow_active = False
        self._files_scroll_hover_scheduled = False
        self._files_follow_pending = None
        self._files_follow_scheduled = False
        self._files_warp_global = None
        self._wheel_root_follow_pending = None
        self._wheel_root_follow_scheduled = False
        self._wheel_bookmark_delta = 0
        self._bookmark_edge_follow_active = False
        self._bookmark_scroll_hover_scheduled = False
        self._bookmark_hover_item = None
        self._wheel_middle_delta = 0
        self._middle_parity_angle_remainder = 0
        self._middle_parity_pixel_remainder = 0
        self._middle_follow_pending = None
        self._middle_follow_scheduled = False
        self._middle_warp_global = None
        self._middle_back_hold = EdgeWheelHold()
        # Public UI: disable ALL wheel-edge jumps between areas, both with
        # pointer auto-move ON and OFF.  Keep in-area wheels, pointer-origin
        # selection, manual/keyboard navigation and shuriken intact.
        # This also disables the post-jump wheel-input lock (empty swings).
        self.wheel_zone_navigation = WheelZoneNavigation(enabled=False)
        self._favorite_popup_wheel_delta = 0
        self._favorite_popup_warp_generation = 0
        self._favorite_path_wheel_delta = 0
        self._middle_back_warp_pending = None
        self._middle_vdi_anchor_pos = None
        self._bookmark_follow_pending = None
        self._bookmark_follow_scheduled = False
        self._bookmark_warp_global = None
        self.files_root = None
        self.bookmarks_root = None
        # Files and Browser are long-lived workspaces, not URL-driven previews.
        self._workspace_mode = 'files'
        self._browser_splitter_sizes = None
        # Persist only the user's explicit Browser hide/show choice; Files mode
        # hiding Bookmarks is independent and must not overwrite this setting.
        stored_bookmarks = launcher.settings.value('browser_bookmarks_visible', True)
        self._browser_bookmarks_visible = str(stored_bookmarks).strip().lower() not in (
            '0', 'false', 'no', 'off')
        self.files_mode_tab = None
        self.browser_mode_tab = None
        self._toolbar_wheel_current = None
        self._toolbar_wheel_remainder = 0
        # Normal Bookmarks has its OWN tab destination; Remote's compact
        # Browser popup keeps its existing independent selector.
        self.bookmark_new_tab = True
        self._browser_empty_page = None
        self._browser_empty_bookmark_button = None
        self.path = []
        self.directory_history = DirectoryNavigationHistory(limit=100)
        self._restoring_directory_history = False
        self._refreshing = False
        # Column-2 fallback selection: remember per directory, not per tree
        # item (QTreeWidgetItem instances are recreated on folder refresh).
        self._middle_current_memory = None
        self._middle_selection_repair_queued = False
        self._middle_selection_repair_running = False
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        # The Files / Browser tabs are attached to the workspace surface,
        # like a browser tab: no gap between the selector and the content.
        outer.setSpacing(0)
        self.toolbar_scroller = QScrollArea(self)
        self.toolbar_scroller.setObjectName('expandedRootScroller')
        self.toolbar_scroller.setWidgetResizable(True)
        # Full-sized workspace tabs (~1.2x the inner Web URL tabs) share a
        # seamless lower edge with the Files / Browser content below.
        self.toolbar_scroller.setFixedHeight(44)
        self.toolbar_scroller.setFrameShape(QFrame.Shape.NoFrame)
        self.toolbar_scroller.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.toolbar_scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.toolbar_scroller.horizontalScrollBar().rangeChanged.connect(
            self.update_root_toolbar_height)
        self.root_widget = _WorkspaceTabStrip()
        self.root_widget.setObjectName('expandedRootBar')
        self.root_layout = QHBoxLayout(self.root_widget)
        # Bottom=0 lets the active tab touch the page without a white band.
        self.root_layout.setContentsMargins(6, 3, 4, 0)
        self.root_layout.setSpacing(5)
        self.toolbar_scroller.setWidget(self.root_widget)
        # Catch wheel gestures on buttons AND on the whitespace in the strip.
        # This has no effect on the Page tab bar or the file-list scrollbars.
        for source in (self.root_widget, self.toolbar_scroller.viewport(),
                       self.toolbar_scroller):
            source.installEventFilter(self)
        outer.addWidget(self.toolbar_scroller)
        # Shared Explorer header sits ACROSS Files and directory; only the
        # content below is divided. The bookmark panel stays independent.
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.setObjectName('expandedSplitter')
        # Keep the original Files widgets alive when the left side becomes WebView.
        # A stacked page preserves folder path, current item and splitter sizes.
        self.files_content_stack = QStackedWidget(self.splitter)
        self.files_group = QFrame(self.files_content_stack)
        self.files_content_stack.addWidget(self.files_group)
        self.web_view = None
        self._web_selection_timer = QTimer(self)
        self._web_selection_timer.setSingleShot(True)
        self._web_selection_timer.setInterval(650)  # v40 default; config may override
        configured_delay = getattr(launcher, 'webview_settings', {}).get('bookmark_preview_delay_ms')
        if configured_delay is not None:
            self._web_selection_timer.setInterval(configured_delay)
        # Selection is never navigation: only click / Right / Enter opens a URL.
        # Timer kept for compatibility with older call sites; not connected.
        self.files_group.setObjectName('expandedFilesGroup')
        group_layout = QVBoxLayout(self.files_group)
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(0)
        self.shared_header = QWidget(self.files_group)
        self.shared_header.setObjectName('expandedCombinedHeader')
        self._files_top_right_outline = _WorkspaceTopRightOutline(self.shared_header)
        shared_layout = QHBoxLayout(self.shared_header)
        shared_layout.setContentsMargins(12, 6, 10, 6)
        shared_layout.setSpacing(8)
        self.shared_icon = QLabel(self.shared_header)
        self.shared_icon.setFixedSize(28, 28)
        shared_layout.addWidget(self.shared_icon)
        self.shared_title = QLabel('Files', self.shared_header)
        self.shared_title.setObjectName('expandedCombinedTitle')
        shared_layout.addWidget(self.shared_title)
        self.density_button = QToolButton(self.shared_header)
        self.density_button.setObjectName('expandedDensityToggle')
        self.density_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.density_button.setFixedSize(30, 29)
        self.density_button.setIconSize(QSize(19, 19))
        self.density_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.density_button.clicked.connect(self.toggle_row_density)
        # History replaces the density button at the original left-hand slot.
        # Single clicks are deferred to avoid confirming a keyword during a
        # double-click; exactly the same protocol as the Remote history key.
        self.files_history_button = _FilesHistoryButton(self.shared_header)
        self.files_history_button.setObjectName('expandedFilesHistoryButton')
        self.files_history_button.setFixedSize(30, 29)
        self.files_history_button.setIconSize(QSize(22, 22))
        self.files_history_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.files_history_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.files_history_button.setToolTip(
            '検索履歴：1回目で開く／2回目で確定／ダブルクリックで検索結果を実行')
        self._files_history_click_timer = QTimer(self.files_history_button)
        self._files_history_click_timer.setSingleShot(True)
        self._files_history_click_timer.timeout.connect(launcher.files_history_button_clicked)
        self.files_history_button.clicked.connect(
            lambda checked=False: self._files_history_click_timer.start(
                QApplication.instance().doubleClickInterval()))
        self.files_history_button.double_clicked.connect(
            lambda: (self._files_history_click_timer.stop(),
                     launcher.remote_search_result_double_click()))
        shared_layout.addWidget(self.files_history_button)
        self.address_bar = DirectoryAddressBar(self.go_to_directory, self.shared_header)
        shared_layout.addWidget(self.address_bar, 1)
        # Move the existing three-lines/density action to the breadcrumb's
        # right end. Its QAction/callback and row-density setting are unchanged.
        shared_layout.addWidget(self.density_button)
        # Ad-hoc work-directory favorites stay outside the authored Launch JSON.
        from os import environ
        self.folder_favorites = FolderFavorites(
            Path(environ.get('LOCALAPPDATA', str(Path.home()))) / 'FRBLaunch' / 'folder_favorites.json')
        self.favorite_save = QToolButton(self.address_bar)
        self.favorite_save.setObjectName('expandedFavoriteSave')
        self.favorite_save.setText('💛')
        self.favorite_save.setToolTip('今表示しているフォルダーをお気に入りに登録')
        self.favorite_save.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.favorite_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.favorite_save.clicked.connect(self.register_directory_favorite)
        self.favorite_dropdown = QToolButton(self.address_bar)
        self.favorite_dropdown.setObjectName('expandedFavoriteDropdown')
        self.favorite_dropdown.setText('')
        self.favorite_dropdown.setIcon(combo_chevron_icon(self.launcher.color_theme))
        self.favorite_dropdown.setToolTip('作業フォルダーのお気に入り一覧')
        self.favorite_dropdown.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.favorite_dropdown.setCursor(Qt.CursorShape.PointingHandCursor)
        self.favorite_dropdown.clicked.connect(self.toggle_directory_favorites)
        self.address_bar.attach_history_dropdown(self.favorite_dropdown)
        self.address_bar.attach_favorite_save(self.favorite_save)
        self.directory_apply = QToolButton(self.address_bar)
        self.directory_apply.setObjectName('expandedDirectoryApply')
        self.directory_apply.setText('➡️')
        self.directory_apply.setToolTip('選択したパスのフォルダーを表示')
        self.directory_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        self.directory_apply.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # Exactly the same navigation/validation contract as pressing Enter.
        self.directory_apply.clicked.connect(self.address_bar._submit)
        self.address_bar.attach_path_apply(self.directory_apply)
        self.favorite_popup = QFrame(self.launcher)
        self.favorite_popup.setObjectName('expandedFavoritesPopup')
        favorite_layout = QVBoxLayout(self.favorite_popup)
        favorite_layout.setContentsMargins(5, 5, 5, 5)
        favorite_layout.setSpacing(0)
        self.favorite_choices = ReorderablePopupTree(self.favorite_popup)
        self.favorite_choices.setObjectName('expandedFavoritesChoices')
        self.favorite_choices.setColumnCount(2)
        self.favorite_choices.setHeaderHidden(True)
        self.favorite_choices.setRootIsDecorated(False)
        self.favorite_choices.setIndentation(0)
        self.favorite_choices.setSortingEnabled(False)
        self.favorite_choices.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.favorite_choices.header().setStretchLastSection(False)
        self.favorite_choices.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.favorite_choices.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.favorite_choices.setColumnWidth(1, 34)
        self.favorite_choices.setIconSize(QSize(19, 19))
        self.favorite_choices.itemClicked.connect(self.directory_favorite_clicked)
        self.favorite_choices.orderChanged.connect(self.directory_favorites_reordered)
        self.favorite_choices.installEventFilter(self)
        self.favorite_choices.viewport().installEventFilter(self)
        favorite_layout.addWidget(self.favorite_choices)
        self.favorite_popup.hide()
        QApplication.instance().installEventFilter(self)
        self.left = ExpandedPanel('Files', 'folder')
        self.middle = ExpandedPanel('フォルダー', 'folder')
        self.middle.tree.setAcceptDrops(True)
        self.middle.tree.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.middle.tree.launch_registration_resolver = self._middle_launch_drop_target
        self.middle.tree.launch_registration_handler = launcher.handle_launch_drop
        # Local, immediate filter; separate from global search and its file index.
        # Preserve the 3-column navigation and right-side chevrons unchanged.
        self._middle_query_directory = None
        # Launch JSON projection is a *virtual* current directory. Its files
        # are shown in the same List widget, never passed to OS path actions.
        self._virtual_directory_node = None
        self._virtual_sort_custom = False
        self.middle.virtual_details_columns = False
        self._middle_header_virtual = False
        self._physical_middle_header_state = None
        # Each visited filesystem directory owns an optional sort override.
        # The old global setting is intentionally ignored: uncustomized
        # directories always start with the Explorer-style standard sort.
        self._middle_sort_mode = DEFAULT_SORT
        self._middle_sort_directory = None
        self.middle_search_bar = QWidget(self.middle)
        self.middle_search_bar.setObjectName('expandedMiddleSearchBar')
        middle_search_layout = QHBoxLayout(self.middle_search_bar)
        middle_search_layout.setContentsMargins(0, 0, 5, 0)
        middle_search_layout.setSpacing(4)
        self.files_list_title_box = QFrame(self.middle_search_bar)
        self.files_list_title_box.setObjectName('filesListTitleBox')
        self.files_list_title_box.setProperty('operatingActive', False)
        files_list_title_layout = QHBoxLayout(self.files_list_title_box)
        files_list_title_layout.setContentsMargins(8, 0, 5, 0)
        self.files_list_title_label = QLabel('Files List', self.files_list_title_box)
        self.files_list_title_label.setObjectName('filesListTitle')
        files_list_title_layout.addWidget(self.files_list_title_label)
        middle_search_layout.addWidget(self.files_list_title_box, 0)
        # This is a *local Files List* keyword history, not Launcher-global
        # search history. Keep the same small, left-side breadcrumb button UI.
        history_path = (Path(launcher.settings.fileName()).parent
                        / 'files_list_search_history.json')
        self.files_list_search_history = FilesListSearchHistory(history_path)
        self.middle_search_history_button = QToolButton(self.middle_search_bar)
        self.middle_search_history_button.setObjectName('expandedMiddleSearchHistoryButton')
        self.middle_search_history_button.setFixedSize(30, 29)
        self.middle_search_history_button.setIconSize(QSize(22, 22))
        self.middle_search_history_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.middle_search_history_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.middle_search_history_button.setToolTip(
            'Files List検索履歴：現在のキーワードを登録／登録済みキーワードを呼び出し')
        # Do NOT use QToolButton.setMenu(...)/InstantPopup here.  That creates
        # a native Qt.Popup grab, preventing Windows-rod click/wheel input from
        # reaching the Remote whenever this one particular history is open.
        # Instead open a non-grabbing QMenu explicitly, just like Page menus.
        self.middle_search_history_menu = _NonGrabbingHistoryMenu(
            self.middle_search_history_button)
        self.middle_search_history_menu.setObjectName('filesListSearchHistoryMenu')
        # Tool QMenus do not rely on a native popup dismissal. Explicitly
        # close after a selection (including a nested delete-history action).
        self.middle_search_history_menu.triggered.connect(
            lambda _action: self.middle_search_history_menu.hide())
        self.middle_search_history_button.clicked.connect(
            self.toggle_middle_search_history_menu)
        middle_search_layout.addWidget(self.middle_search_history_button, 0)
        self.middle_search = QLineEdit(self.middle_search_bar)
        self.middle_search.setObjectName('expandedMiddleSearch')
        self.middle_search.setMinimumHeight(29)
        self.middle_search.setPlaceholderText('このフォルダーを検索 (AND / OR)')
        self.middle_search.setClearButtonEnabled(True)
        self.middle_search.setToolTip('このフォルダー内の名前を絞り込み。メイン検索と同じAND/OR構文。')
        middle_search_layout.addWidget(self.middle_search, 1)
        self.middle.layout_box.insertWidget(0, self.middle_search_bar)
        self.middle_search.textChanged.connect(self.apply_middle_filter)
        # Explorer-style real columns, with a stretchable blank last column.
        # Preserve a fixed separate Back operation lane to the far right.
        tree = self.middle.tree
        self.middle.details_columns = True
        tree.setProperty('detailsColumns', True)
        tree.setColumnCount(5)
        tree.setHeaderLabels(['名前', '更新日', 'サイズ', '種類', ''])
        tree.setHeaderHidden(False)
        tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # Rename is restricted to the filename (column 0). Qt item flags are
        # row-wide: protect *every* metadata column with a non-editing delegate.
        tree.setItemDelegateForColumn(0, _InlineRenameDelegate(tree))
        for metadata_column in (1, 2, 3):
            tree.setItemDelegateForColumn(metadata_column, _ReadOnlyMetadataDelegate(tree))
        tree.setItemDelegateForColumn(4, _NavigationChevronDelegate(tree, right_inset=15))
        header = tree.header()
        header.setObjectName('expandedMiddleColumnsHeader')
        # The metadata heading is secondary to file names. At roughly 80%
        # of the former ~35px height it stays readable without dominating.
        header.setFixedHeight(28)
        header.setSectionsClickable(True)
        header.setSectionsMovable(True)
        header.setHighlightSections(False)
        header.setMinimumSectionSize(34)
        header.setStretchLastSection(False)
        for col, width in enumerate((300, 156, 98, 150, 55)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
            tree.setColumnWidth(col, width)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self._middle_header_restoring = True
        try:
            saved = launcher.settings.value('expanded_middle_header_state_v50')
            if saved is not None:
                header.restoreState(saved)
        finally:
            self._middle_header_restoring = False
        # The blank end column absorbs space, not the data columns.
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.sectionResized.connect(self._save_middle_header_state)
        header.sectionMoved.connect(self._save_middle_header_state)
        header.sectionClicked.connect(self._middle_header_clicked)
        header.setSortIndicatorShown(True)
        self._update_middle_header_sort()
        # Separate a real 24px Back lane OUTSIDE the QTreeWidget viewport.
        # Qt's current-row rectangle therefore cannot extend into the lane,
        # and neither click nor inline rename can land on a hidden row cell.
        self.middle_tree_container = QWidget(self.middle)
        self.middle_tree_container.setObjectName('expandedMiddleTreeContainer')
        middle_tree_layout = QHBoxLayout(self.middle_tree_container)
        middle_tree_layout.setContentsMargins(0, 0, 0, 0)
        middle_tree_layout.setSpacing(0)
        self.middle.layout_box.removeWidget(self.middle.tree)
        self.middle.tree.setParent(self.middle_tree_container)
        middle_tree_layout.addWidget(self.middle.tree, 1)
        self.middle_back_lane = _BackLaneWidget(self, self.middle_tree_container)
        self.middle_back_lane.setObjectName('expandedBackLane')
        self.middle_back_lane.setFixedWidth(MIDDLE_BACK_LANE_WIDTH)
        self.middle_back_lane.setToolTip('ダブルクリック：上のフォルダーへ／右クリック：フォルダー操作')
        self.middle_back_lane.installEventFilter(self)
        middle_tree_layout.insertWidget(0, self.middle_back_lane)
        self.middle.tree.verticalScrollBar().valueChanged.connect(
            lambda *_: self.middle_back_lane.update())
        self.middle.tree.model().rowsInserted.connect(lambda *args: self.middle_back_lane.update())
        self.middle.tree.model().rowsRemoved.connect(lambda *args: self.middle_back_lane.update())
        self.middle.layout_box.addWidget(self.middle_tree_container, 1)
        # Explorer-like empty view: draw in the blank list viewport without
        # intercepting blank-space right-click, Paste, or wheel navigation.
        self.middle_empty_label = QLabel('このフォルダーは空です。', self.middle.tree.viewport())
        self.middle_empty_label.setObjectName('filesListEmptyLabel')
        self.middle_empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.middle_empty_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.middle_empty_label.hide()
        self.middle_parent_return_hint = QLabel('～とんとん親帰り／カレントフォルダー操作 エリア～', self.middle.tree.viewport())
        self.middle_parent_return_hint.setObjectName('filesListParentReturnHint')
        self.middle_parent_return_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.middle_parent_return_hint.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.middle_parent_return_hint.hide()
        self.middle.tree.viewport().installEventFilter(self)
        self.middle.tree.verticalScrollBar().valueChanged.connect(
            lambda *_: self._position_middle_parent_return_hint())
        # Only the directory-content column is multi-select. Qt supplies
        # Ctrl+click, Shift+click, Ctrl+A, and Shift+Up/Down natively.
        self.middle.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        # The current item can temporarily disappear during refresh/rename.
        # Heal after Qt settles, plus a lightweight polling fallback for an
        # occasional focus/selection-loss event that emits no usable signal.
        self.middle.tree.currentItemChanged.connect(self._remember_middle_current)
        self.middle.tree.currentItemChanged.connect(
            lambda *_: self._queue_middle_selection_repair())
        self.middle.tree.itemSelectionChanged.connect(self._queue_middle_selection_repair)
        # Coalesce Ctrl/Shift clicks and the intermediate selections produced
        # by a folder refresh into one status-bar update after Qt settles.
        self._files_selection_status_queued = False
        self.middle.tree.itemSelectionChanged.connect(self._queue_files_selection_status)
        self.middle.tree.currentItemChanged.connect(self._queue_files_selection_status)
        self.middle.tree.blank_clicked = lambda: self._sync_remote_area_after_mouse_press('directory')
        self.middle.tree.model().modelReset.connect(self._queue_middle_selection_repair)
        self._middle_selection_watchdog = QTimer(self)
        self._middle_selection_watchdog.setInterval(400)
        self._middle_selection_watchdog.timeout.connect(self.ensure_middle_current_selection)
        self._middle_selection_watchdog.start()
        # WAN: only this pane measures actual native scroll movement before
        # using wheel steps to move the current row and the mouse cursor.
        self.middle.tree.adaptive_wheel_callback = self.wheel_middle_at_edge
        self.middle.tree.shuriken_stop_on_action = self.launcher.stop_auto_shuriken_on_list_click
        # List-only experiment (settings in list_wheel_parity.py):
        # A) Fast Remote cadence + scrollbar-first/edge-follow hybrid (default)
        # B) Fast Remote current-only (previous successful version)
        # C) Qt native scrollbar-first WAN (original fallback)
        if LIST_WHEEL_MATCH_REMOTE:
            if LIST_WHEEL_HYBRID_ENABLED:
                self.middle.tree.remote_parity_wheel_callback = self.wheel_middle_fast_hybrid
            else:
                self.middle.tree.remote_parity_wheel_callback = self.wheel_middle_like_remote_button
        # The header Back button is an explicit, non-scrolling Wheel Tab zone.
        # Never synthesize its click; a sustained UP gesture goes to Files last.
        self.middle.back.installEventFilter(self)
        # WAN for Files first column: native scrolling first, then select and
        # follow at the relevant edge (also when all rows fit on screen).
        # The older wheel_files_first_column remains as a safe rollback path.
        self.left.tree.adaptive_wheel_callback = self.wheel_files_at_edge
        self.left.tree.installEventFilter(self)
        self.left.tree.viewport().installEventFilter(self)
        self.left.header.hide()
        self.middle.header.hide()
        # Reuse the old Back button/signal, but position it in the shared header.
        self.middle.header.layout().removeWidget(self.middle.back)
        self.middle.back.setParent(self.shared_header)
        # The parent-directory button belongs immediately LEFT of the path.
        shared_layout.insertWidget(shared_layout.indexOf(self.address_bar), self.middle.back)
        self.middle.back.show()
        # Unlike mouse-only Back, Wheel Tab must visibly LAND with keyboard
        # focus on this button. The other pane Back buttons stay unchanged.
        self.middle.back.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        group_layout.addWidget(self.shared_header)
        self.files_splitter = QSplitter(Qt.Orientation.Horizontal, self.files_group)
        self.files_splitter.setObjectName('expandedFilesSplitter')
        # Keep the existing TWO-child splitter contract intact. Column 1.5
        # is a width-reserved child of the first-column host, but the Remote
        # window is never reparented to it (search results can float below).
        self.files_first_host = QWidget(self.files_splitter)
        self.files_first_host.setObjectName('expandedFilesFirstHost')
        first_host_row = QHBoxLayout(self.files_first_host)
        first_host_row.setContentsMargins(0, 0, 0, 0)
        first_host_row.setSpacing(0)
        first_host_row.addWidget(self.left, 1)
        self.remote_15_lane = QFrame(self.files_first_host)
        self.remote_15_lane.setObjectName('remote15PlacementLane')
        self.remote_15_lane.setFixedWidth(196)
        self.remote_15_lane.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.remote_15_lane.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.remote_15_lane.installEventFilter(self)
        first_host_row.addWidget(self.remote_15_lane, 0)
        self.remote_15_lane.hide()
        self.files_splitter.addWidget(self.files_first_host)
        self.files_splitter.addWidget(self.middle)
        # Files Exp replaces only the old first-column CONTENT. The splitter,
        # old authored root tree and all of its data/selection logic survive.
        from remote_files_explorer import RemoteFilesExplorer
        self.embedded_files_exp = RemoteFilesExplorer(
            None, launcher.color_theme, launcher=launcher, embedded=True)
        self.left.layout_box.addWidget(self.embedded_files_exp, 1)
        # The two headers form a matching pair. Their widths follow the
        # *actual* Files Exp column (never the combined Exp+Remote host).
        self.left.installEventFilter(self)
        self.files_splitter.splitterMoved.connect(
            lambda *_: self._align_files_list_title_width())
        QTimer.singleShot(0, self._align_files_list_title_width)
        # Match the Files Exp title's bottom border to the adjacent folder
        # search row's bottom border, regardless of font metrics or DPI.
        self.middle_search_bar.installEventFilter(self)
        self._align_embedded_exp_header()
        self._align_files_list_title_width()
        self.embedded_files_exp.folder_selected.connect(
            launcher.navigate_files_exp_folder)
        self.embedded_files_exp.pc_selected.connect(
            launcher.navigate_files_exp_pc)
        self.embedded_files_exp.folder_context_requested.connect(
            launcher.show_files_exp_folder_menu)
        self.embedded_files_exp.authored_root_context_requested.connect(
            launcher.show_files_exp_authored_root_menu)
        self.embedded_files_exp.folder_renamed.connect(
            launcher.on_files_exp_folder_renamed)
        self.embedded_files_exp.virtual_item_activated.connect(
            launcher.activate_virtual_launch_item)
        self.embedded_files_exp.virtual_folder_selected.connect(
            launcher.navigate_virtual_launch_folder)
        self.embedded_files_exp.virtual_context_requested.connect(
            launcher.show_virtual_launch_context)
        self.embedded_files_exp.root_context_requested.connect(
            launcher.show_launch_root_registration_menu)
        self.embedded_files_exp.registration_drop_requested.connect(
            launcher.handle_launch_drop)
        self.embedded_files_exp.hide()
        self._embedded_files_exp_roots_ready = False
        self.files_splitter.setChildrenCollapsible(False)
        group_layout.addWidget(self.files_splitter, 1)
        self.right = ExpandedPanel('ブックマーク', 'bookmark')
        self.bookmark_close_button = QToolButton(self.right.header)
        self.bookmark_close_button.setObjectName('expandedBookmarkClose')
        self.bookmark_close_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.bookmark_close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bookmark_close_button.setFixedSize(25, 25)
        self.bookmark_close_button.setIconSize(QSize(17, 17))
        self.bookmark_close_button.setToolTip('ブックマークを閉じる')
        self.bookmark_close_button.clicked.connect(self.hide_browser_bookmarks)
        # Header normally has an invisible Back button at its end.
        self.right.header.layout().insertWidget(2, self.bookmark_close_button)
        # Match Remote > Browser's two explicit URL destinations.  Put the
        # choices BELOW the bookmark heading so the narrow pane retains its
        # title and close icon; do not add items to the bookmark tree itself.
        self.bookmark_tab_target_bar = QWidget(self.right)
        self.bookmark_tab_target_bar.setObjectName('expandedBookmarkTabTargetBar')
        target_row = QHBoxLayout(self.bookmark_tab_target_bar)
        target_row.setContentsMargins(9, 5, 9, 5)
        target_row.setSpacing(4)
        self.bookmark_new_tab_button = QPushButton('新規タブ', self.bookmark_tab_target_bar)
        self.bookmark_current_tab_button = QPushButton('カレントタブ', self.bookmark_tab_target_bar)
        for button in (self.bookmark_new_tab_button, self.bookmark_current_tab_button):
            button.setObjectName('expandedBookmarkTabChoice')
            button.setCheckable(True)
            button.setFixedHeight(28)
            button.setMinimumWidth(0)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.bookmark_new_tab_button.clicked.connect(
            lambda _checked=False: self.select_bookmark_tab(True))
        self.bookmark_current_tab_button.clicked.connect(
            lambda _checked=False: self.select_bookmark_tab(False))
        target_row.addWidget(self.bookmark_new_tab_button, 1)
        target_row.addWidget(self.bookmark_current_tab_button, 1)
        self.right.layout_box.insertWidget(1, self.bookmark_tab_target_bar)
        # External browsers own their tab rules: a misleading selector must
        # not appear when Launch is configured to open URLs externally.
        self.bookmark_tab_target_bar.setVisible(
            self.launcher.webview_settings.get('mode') == 'embedded')
        self.select_bookmark_tab(True)  # Same initial target as Remote Browser.
        # Bookmarks first level is also a wheel-driven selector.  Only the
        # tree/viewport are hooked: scrollbar dragging and deeper tool
        # columns continue to use their original native behavior.
        self.right.tree.installEventFilter(self)
        self.right.tree.viewport().installEventFilter(self)
        # WAN is opt-in per Bookmarks: use native scrolling first, then cursor
        # follow only when the wheel cannot move the scrollbar any farther.
        self.right.tree.adaptive_wheel_callback = (
            self.wheel_bookmarks_at_edge
            if getattr(self.launcher, 'bookmark_wan_enabled', True) else None)
        self._bookmark_hover_timer = QTimer(self)
        self._bookmark_hover_timer.setSingleShot(True)
        self._bookmark_hover_timer.timeout.connect(self.open_bookmark_hover)
        self.right.tree.itemEntered.connect(self.hover_bookmark_first_level)
        # Browser: Bookmarks first, then the retained WebView (left to right).
        # Files hides Bookmarks and fills the whole splitter without rebuilding.
        self.splitter.addWidget(self.right)
        self.splitter.addWidget(self.files_content_stack)
        self.root_widget.set_corner_end_provider(
            lambda: (None if self._workspace_mode == 'browser' else
                     self.root_widget.mapFromGlobal(
                         self.files_content_stack.mapToGlobal(
                             QPoint(self.files_content_stack.width(), 0))).x()))
        # A SINGLE rule spans the whole Browser workspace, including
        # Bookmarks. The bookmarks frame has no competing upper border.
        self.root_widget.set_underline_end_provider(lambda: None)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setSizes([350, 660])
        self._browser_splitter_sizes = [350, 660]
        self.files_splitter.setSizes([310, 350])
        # Compatible with the legacy saved 3-column sizes.
        saved = str(launcher.settings.value('expanded_splitter_sizes', '') or '')
        try:
            values = [int(value) for value in saved.split('|')]
            if len(values) == 3 and all(value >= 100 for value in values):
                # Legacy v49-v60 persisted Web width then Bookmarks width.
                self._browser_splitter_sizes = [values[2], values[0] + values[1]]
                self.splitter.setSizes(self._browser_splitter_sizes)
                self.files_splitter.setSizes(values[:2])
        except ValueError:
            pass
        # Files and Browser can now have independent splitter widths.
        saved_files = str(launcher.settings.value('workspace_files_splitter_sizes', '') or '')
        try:
            file_widths = [int(value) for value in saved_files.split('|')]
            if len(file_widths) == 2 and all(value >= 100 for value in file_widths):
                self.files_splitter.setSizes(file_widths)
        except ValueError:
            pass
        self.splitter.splitterMoved.connect(self.save_splitter_sizes)
        self.splitter.splitterMoved.connect(lambda *_: self.root_widget.refresh_underline())
        self.files_splitter.splitterMoved.connect(self.save_splitter_sizes)
        outer.addWidget(self.splitter, 1)
        self.row_density = str(launcher.settings.value('expanded_row_density', 'normal') or 'normal')
        if self.row_density not in ('normal', 'compact'):
            self.row_density = 'normal'
        # Only the middle panel enables Explorer-like edit-on-selected-click.
        # Double-click/Right-arrow navigation remain unchanged.
        self.middle.tree.setEditTriggers(QAbstractItemView.EditTrigger.SelectedClicked)
        self.middle.tree.itemChanged.connect(self.finish_inline_rename)
        self._inline_rename_active = False
        self.middle.back.clicked.connect(self.go_up)
        self.left.tree.itemClicked.connect(self.choose_files)
        self.middle.tree.itemClicked.connect(self.choose_middle)
        # When Remote is visible it owns the logical active-column highlight.
        # Real mouse presses in Launch must update that logical column too;
        # native Qt focus alone is not enough. Defer until the click finishes
        # selecting/navigating, otherwise focus_panel() selects a stale row.
        self.left.tree.itemPressed.connect(
            lambda *_: self._sync_remote_area_after_mouse_press('files'))
        self.middle.tree.itemPressed.connect(
            lambda *_: self._sync_remote_area_after_mouse_press('directory'))
        self.right.tree.itemClicked.connect(self.choose_bookmark)
        # A wheel or keyboard selection must not navigate the current Web tab.
        # Explicit click / Right / Enter is handled independently below.
        for panel in (self.left, self.middle, self.right):
            panel.tree.itemActivated.connect(lambda item, col, pane=panel: self.activate_row(pane, item))
            panel.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            panel.tree.customContextMenuRequested.connect(lambda point, pane=panel:
                self.context_menu(pane, point))
        self.apply_theme('light')
        self.show_files_view()  # No Bookmarks column in the Files workspace.
        # Startup has ONE active Files column. Keep the middle current row as
        # a remembered outline until the user explicitly selects it.
        self.left.tree.setProperty('remoteInactive', False)
        self.middle.tree.setProperty('remoteInactive', True)
        self.middle.tree.style().unpolish(self.middle.tree)
        self.middle.tree.style().polish(self.middle.tree)
        # Embedded Files starts on its actionable List, just like Remote's
        # initial Files List button; the old first-column mode keeps its root.
        self.set_files_operating_area(
            'directory' if launcher.files_exp_embedded_mode else 'files')

    def select_bookmark_tab(self, new_tab):
        """Select the destination for direct and nested bookmark clicks.

        This is a view-only choice, not a change to Launch's JSON data.
        Do not steal keyboard/Remote focus from the bookmark tree.
        """
        self.bookmark_new_tab = bool(new_tab)
        for button, label, selected in (
                (self.bookmark_new_tab_button, '新規タブ', self.bookmark_new_tab),
                (self.bookmark_current_tab_button, 'カレントタブ', not self.bookmark_new_tab)):
            button.setChecked(selected)
            button.setText(('✓ ' if selected else '') + label)
            button.setToolTip(('選択中：' if selected else '切り替える：') + label)

    def update_root_toolbar_height(self, minimum=0, maximum=0):
        """Keep buttons visible when narrow widths require a scrollbar.

        The common case is a 44px strip for the attached workspace tabs;
        when crowded, reserve another 14px for the native scrollbar.
        No navigation, focus or wheel rules are changed by the density tweak.
        """
        required = 58 if maximum > minimum else 44
        if self.toolbar_scroller.height() != required:
            self.toolbar_scroller.setFixedHeight(required)

    def save_splitter_sizes(self, *_):
        # Experimental 1.5-column widths must not poison older 2-column data.
        if getattr(self.launcher, 'remote_15_mode', False):
            widths = self.files_splitter.sizes()
            if (self._workspace_mode == 'files' and len(widths) == 2
                    and widths[0] >= 196 and widths[1] >= 100):
                self.launcher.settings.setValue(
                    'workspace_files_remote_15_splitter_sizes',
                    '|'.join(map(str, widths)))
            return
        # Embedded and original Files layouts have independent user widths.
        if getattr(self.launcher, 'files_exp_embedded_mode', False):
            widths = self.files_splitter.sizes()
            if (self._workspace_mode == 'files' and len(widths) == 2
                    and all(value >= 100 for value in widths)):
                self.launcher.settings.setValue(
                    'workspace_files_exp_embedded_splitter_sizes',
                    '|'.join(map(str, widths)))
            return
        # Never overwrite the original two-column widths with a hidden-pane [0, n].
        if getattr(self.launcher, 'files_root_hidden_mode', False):
            return
        if (self._workspace_mode == 'browser' and self._browser_bookmarks_visible
                and self.right.isVisible()):
            widths = self.splitter.sizes()
            if len(widths) == 2 and all(width > 0 for width in widths):
                self._browser_splitter_sizes = widths
        # When hidden, the Bookmarks splitter segment has width zero. Never
        # persist this temporary Files layout as Browser's preferred widths.
        file_widths = self.files_splitter.sizes()
        self.launcher.settings.setValue('workspace_files_splitter_sizes',
                                        '|'.join(map(str, file_widths)))
        if (self._workspace_mode == 'files' or not self._browser_bookmarks_visible
                or not self.right.isVisible()):
            return
        # Preserve legacy 3-width format for old builds: Files x2, Bookmarks.
        widths = file_widths + self.splitter.sizes()[:1]
        self.launcher.settings.setValue('expanded_splitter_sizes',
                                        '|'.join(map(str, widths)))

    def toggle_row_density(self):
        self.row_density = 'compact' if self.row_density == 'normal' else 'normal'
        self.launcher.settings.setValue('expanded_row_density', self.row_density)
        self.launcher.settings.sync()
        self.apply_theme(self.launcher.color_theme)

    def apply_theme(self, theme):
        self.embedded_files_exp.apply_theme(theme)
        self.remote_15_lane.setStyleSheet(
            'QFrame#remote15PlacementLane { background: transparent; border: 0; }')
        if self.web_view is not None:
            self.web_view.apply_theme(theme)
        colors = theme_palette(theme)
        light = theme_family(theme) == 'light'
        bg, border, hdr, text, hover, active, stripe = (
            colors[key] for key in ('panel', 'panel_border', 'panel_header',
                                   'text', 'hover', 'selection', 'stripe'))
        # Warm operating surface is independent of GREEN current-row status.
        # Sakura Editor-inspired warm white, lightened from #FFFBF0.
        operating_bg = '#FFFEF9' if light else '#463a32'
        operating_title = '#FFF9EF' if light else '#624936'
        # The grid header is one shade lighter than the Files List title,
        # whether its column is active or remembered.
        list_grid_header = '#FCFEFD' if light else '#425a50'
        operating_grid_header = '#FFFCF6' if light else '#6b5141'
        operating_outline = '#d9b991' if light else '#ad8258'
        root_border = colors['root_button_border']
        # The workspace strip is deliberately a shade lighter than the tabs.
        # Keep the active Files/Browser tab's existing {hdr} fill unchanged:
        # only the wide background BEHIND those tabs is softened.
        workspace_strip_bg = colors['workspace_strip']
        # Both active workspaces use exactly the same mint surface color.
        # Inactive tabs recede: a softer border and slightly muted caption.
        # Neutral gray makes the inactive label unobtrusive on either theme;
        # stripe is subtler than the active tab's panel border.
        # The scroll area's viewport is a separate Qt widget; a transparent
        # strip can otherwise expose a white default at its left/right edges.
        root_viewport = self.toolbar_scroller.viewport()
        root_viewport.setAutoFillBackground(True)
        root_palette = root_viewport.palette()
        root_palette.setColor(QPalette.ColorRole.Window, QColor(workspace_strip_bg))
        root_viewport.setPalette(root_palette)
        self.root_widget.set_underline_color(border)
        self._files_top_right_outline.set_outline_color(border)
        self._files_top_right_outline.hide()
        if self.right._top_right_outline is not None:
            self.right._top_right_outline.set_outline_color(border)
            # Bookmark edges are deliberately SQUARE. The old painter drew
            # a curved stroke over the stylesheet, even with radius:0.
            self.right._top_right_outline.hide()
        tight = self.row_density == 'compact'
        height, pad = (23, 1) if tight else (29, 3)
        self.density_button.setText('')
        self.density_button.setIcon(density_lines_icon(theme_family(theme)))
        self.files_history_button.setIcon(_files_history_icon(theme))
        self.middle_search_history_button.setIcon(_files_list_keyword_history_icon(theme))
        self.bookmark_close_button.setIcon(browser_navigation_icon(
            'close', theme_family(theme)))
        if self._browser_empty_bookmark_button is not None:
            self._browser_empty_bookmark_button.setIcon(browser_navigation_icon(
                'bookmark_outline', theme_family(theme)))
        self.density_button.setToolTip('行間隔：コンパクト（クリックで切替）' if not tight
                                       else '行間隔：標準（クリックで切替）')
        for pane in (self.left, self.middle, self.right):
            pane.tree.details_theme = theme_family(theme)
            pane.tree.separator_color = QColor(colors['row_separator'])
            pane.tree.inactive_current_border = QColor(colors['focus_outline'])
            for bar in (pane.tree.verticalScrollBar(), pane.tree.horizontalScrollBar()):
                bar.setStyleSheet(scrollbar_for_theme(theme, bg))
            pane.tree.viewport().update()
        if getattr(self, 'middle_back_lane', None) is not None:
            self.middle_back_lane.line_color = QColor(colors['row_separator'])
            self.middle_back_lane.update()
        for bar in (self.favorite_choices.verticalScrollBar(),
                    self.favorite_choices.horizontalScrollBar()):
            bar.setStyleSheet(scrollbar_for_theme(theme, colors['history_bg']))
        self.setStyleSheet(f'''
            /* Soften ONLY the workspace strip/scroll surface. The two tab
               buttons below still use their original {hdr}/{stripe} colors. */
            QWidget#expandedRootBar {{background:{colors["workspace_strip"]};border:0;}}
            QWidget#expandedWorkspaceDragHandle {{background:transparent;border:0;}}
            QScrollArea#expandedRootScroller {{background:{colors["workspace_strip"]};border:0;}}
            QPushButton#expandedRootButton {{ background:{hdr};color:{text};border:1px solid {root_border};
                border-radius:9px;padding:4px 10px;text-align:left;font-size:12px; }}
            QPushButton#expandedRootButton:hover {{background:{hover};}}
            QPushButton#expandedPageButton {{background:{hdr};color:{text};
                border:1px solid {root_border};border-radius:8px;
                padding:3px 11px;font-size:12px;}}
            QPushButton#expandedPageButton:hover {{background:{hover};}}
            QPushButton#expandedRootButton:checked {{background:{active};border:1px solid #81bca4;font-weight:600;}}
            QPushButton#expandedRootButton:focus {{border:2px solid #56a88c;background:{active};}}
            /* Workspace tabs join the mint header beneath them.  The strip
               paints the lower line only outside the active tab's footprint.
               Keep both corners gently rounded; the two bottom corners are
               square to avoid a visible notch at the joined surface. */
            QPushButton#expandedWorkspaceTab {{background:{stripe};color:#84998d;
                border:1px solid {stripe};border-top-left-radius:12px;
                border-top-right-radius:12px;border-bottom-left-radius:0px;
                border-bottom-right-radius:0px;padding:0 18px;font-size:13px;font-weight:400;}}
            /* The inactive Files tab is a separate, rounded button; the
               selected tab remains square at its joined lower corners. */
            QPushButton#expandedWorkspaceTab[workspace="files"]:!checked {{
                border-bottom-left-radius:10px;}}
            QPushButton#expandedWorkspaceTab:hover:!checked {{background:{hover};color:{text};
                border-color:{border};}}
            /* The active tab's complete outline is drawn above the buttons
               by _WorkspaceSeamOverlay, never by an independent QSS border. */
            QPushButton#expandedWorkspaceTab:checked {{background:{hdr};color:{text};
                border:0;border-top-left-radius:12px;
                border-top-right-radius:12px;border-bottom-left-radius:0px;
                border-bottom-right-radius:0px;border-bottom:0;font-weight:400;}}
            QPushButton#expandedWorkspaceTab[workspace="browser"]:checked {{background:{hdr};
                color:{text};border:0;border-bottom:0;font-weight:400;}}
            /* The Files bottom corners are square, with one continuous
               1px border belonging to each of the two folder panes. */
            QFrame#expandedFilesGroup {{background:{hdr};border:0;
                border-radius:0;}}
            QWidget#expandedCombinedHeader {{background:{hdr};border:0;border-bottom:1px solid {border};
                border-top-left-radius:11px;border-top-right-radius:11px;}}
            QLabel#expandedCombinedTitle {{background:transparent;border:0;color:{text};font-size:15px;font-weight:600;}}
            /* Files header controls share the WebView navigation 30x29 style. */
            QToolButton#expandedDensityToggle {{background:{bg};border:1px solid {border};
                border-radius:7px;color:{text};padding:0;}}
            QToolButton#expandedDensityToggle:hover {{background:{hover};}}
            QToolButton#expandedFilesHistoryButton {{background:{bg};border:1px solid {border};
                border-radius:7px;color:{text};padding:0;}}
            QToolButton#expandedFilesHistoryButton:hover {{background:{hover};}}
            QFrame#expandedPanel {{ background:{bg}; border:1px solid {border};border-radius:12px; }}
            /* Shared Files header already draws the separator below itself.
               Suppress the folder panes' top border to avoid a double rule
               above both the left list and the middle search row. */
            QFrame#expandedPanel[panelKind="folder"] {{background:{bg};
                border:1px solid {border};border-top:0;border-radius:0;}}
            /* A square bookmark frame also fills its top-left corner:
               no white wedge from either the panel or header radius. */
            QFrame#expandedPanel[panelKind="bookmark"] {{background:{hdr};
                border:1px solid {border};border-top:0;border-radius:0;}}
            QWidget#expandedHeader {{background:{hdr};border:0;
                border-bottom:1px solid {border};border-radius:0;}}
            QLabel#expandedTitle {{background:transparent;border:0;color:{text};font-size:15px;font-weight:600;}}
            QToolButton#expandedBookmarkClose {{background:transparent;border:0;
                border-radius:7px;margin:0;padding:0;}}
            QToolButton#expandedBookmarkClose:hover {{background:{hover};}}
            QWidget#expandedBookmarkTabTargetBar {{background:{hdr};border:0;
                border-bottom:1px solid {border};}}
            QPushButton#expandedBookmarkTabChoice {{
                background:{'#f8fcfa' if light else '#263a35'};
                border:1px solid {'#b6cfc1' if light else '#537468'};
                color:{'#3d6253' if light else '#b7cec3'};
                border-radius:6px;padding:1px 2px;font-size:12px;}}
            QPushButton#expandedBookmarkTabChoice:checked {{
                background:{'#d6e7f8' if light else '#345d7a'};
                border:1px solid {'#548fc8' if light else '#83bce4'};
                color:{'#173e60' if light else '#f1f8ff'};font-weight:bold;}}
            QPushButton#expandedBookmarkTabChoice:hover {{
                border-color:{'#548fc8' if light else '#83bce4'};}}
            QToolButton#expandedExternalShowBookmarks {{background:{bg};color:{text};
                border:1px solid {border};border-radius:7px;padding:0;}}
            QToolButton#expandedExternalShowBookmarks:hover {{background:{hover};}}
            QPushButton#expandedBack {{background:{bg};border:1px solid {border};
                color:{text};border-radius:7px;padding:0;}}
            QPushButton#expandedBack:hover {{background:{hover};border-radius:7px;}}
            QPushButton#expandedBack:pressed {{background:{hover};border-radius:7px;}}
            QWidget#expandedMiddleSearchBar {{background:{bg};border:0;border-bottom:1px solid {border};}}
            QWidget#expandedMiddleSearchBar[operatingActive="true"] {{background:{operating_bg};}}
            QFrame#filesListTitleBox {{background:{'#f8fcf9' if light else '#395247'};
                border:1px solid transparent;border-bottom:1px solid {border};border-radius:0px;}}
            QFrame#filesListTitleBox[operatingActive="true"] {{
                background:{operating_title};border:1px solid {operating_outline};
                border-radius:3px;}}
            QLabel#filesListTitle {{color:{text};font-size:12px;font-weight:bold;
                background:transparent;border:0;}}
            QToolButton#expandedMiddleSearchHistoryButton {{background:{bg};color:{text};
                border:1px solid {border};border-radius:7px;padding:0;}}
            QToolButton#expandedMiddleSearchHistoryButton:hover {{background:{hover};}}
            QMenu#filesListSearchHistoryMenu {{background:{colors['history_bg']};
                color:{colors['history_text']};border:1px solid {colors['history_border']};
                padding:4px;}}
            QMenu#filesListSearchHistoryMenu::item {{padding:5px 12px;}}
            QMenu#filesListSearchHistoryMenu::item:selected {{background:{colors['history_selected']};
                color:{colors['history_selected_text']};}}
            QLineEdit#expandedMiddleSearch {{background:{bg};color:{text};border:1px solid {border};
                border-radius:7px;padding:3px 7px;font-size:12px;selection-background-color:#78bba0;}}
            QLineEdit#expandedMiddleSearch:focus {{border:1px solid #55a38c;}}
            QHeaderView#expandedMiddleColumnsHeader::section {{
                color:{colors['muted_text']};background:{list_grid_header};border:0;
                border-right:1px solid {border};border-bottom:1px solid {border};
                padding:1px 8px;font-size:12px;font-weight:400;}}
            QHeaderView#expandedMiddleColumnsHeader[operatingActive="true"]::section {{
                background:{operating_grid_header};}}
            QHeaderView#expandedMiddleColumnsHeader::section:hover {{background:{list_grid_header};}}
            QHeaderView#expandedMiddleColumnsHeader[operatingActive="true"]::section:hover {{
                background:{operating_grid_header};}}
            QTreeWidget#expandedTree[detailsColumns="true"] {{font-size:12px;}}
            QWidget#expandedMiddleTreeContainer {{background:{bg};border:0;}}
            QWidget#expandedMiddleTreeContainer[operatingActive="true"] {{background:{operating_bg};}}
            QWidget#expandedBackLane {{background:{bg};border:0;}}
            QWidget#expandedBackLane[operatingActive="true"] {{background:{operating_bg};}}
            QTreeWidget#expandedTree {{background:{bg};color:{text};border:0;outline:0;}}
            QTreeWidget#expandedTree[detailsColumns="true"][remoteInactive="false"] {{
                background:{operating_bg};}}
            QTreeWidget#expandedTree::item {{min-height:{height}px;padding:{pad}px 7px;border:0;}}
            QTreeWidget#expandedTree::item:hover {{background:{hover};}}
            QTreeWidget#expandedTree::item:selected {{background:{active};color:{text};}}
            QTreeWidget#expandedTree::item:selected:!active {{background:{active};color:{text};}}
            /* Selection is always the same color with or without Remote.
               The logical current column is tracked separately from the fill. */
            QTreeWidget#expandedTree[remoteInactive="true"]::item:selected {{background:transparent;color:{text};}}
            QTreeWidget#expandedTree[remoteInactive="true"]::item:selected:!active {{background:transparent;color:{text};}}
        ''')
        self.address_bar.setStyleSheet(f'''
            /* Align the Files breadcrumb pill with the Browser address bar. */
            QFrame#addressBreadcrumbSurface {{border:1px solid {colors['search_border']};
                border-radius:12px;background:{colors['search_bg']};}}
            QToolButton#addressCrumb {{border:0;background:transparent;color:{text};padding:2px 3px;}}
            QToolButton#addressCrumb:hover {{background:{active};border-radius:4px;}}
            QLabel#addressSeparator {{border:0;color:{text};background:transparent;padding:0 2px;}}
            QLabel#addressPlaceholder {{border:0;color:{colors['muted_text']};background:transparent;}}
            QLineEdit#directoryAddressEdit {{background:{colors['search_bg']};color:{colors['muted_text']};
                border:1px solid {colors['search_border']};border-radius:12px;padding:4px 10px;
                selection-background-color:#138c8d;selection-color:white;font-size:12px;}}
            QLineEdit#directoryAddressEdit:focus {{border:1px solid {colors['search_focus']};}}
        ''')
        self.favorite_popup.setStyleSheet(history_popup_qss(
            theme, frame_name='expandedFavoritesPopup',
            tree_name='expandedFavoritesChoices', height=30, padding=5))
        self.favorite_save.setStyleSheet(f'''
            QToolButton#expandedFavoriteSave {{color:{text};background:transparent;border:0;
                border-radius:6px;padding:0;font-size:14px;}}
            QToolButton#expandedFavoriteSave:hover {{background:{hover};}}
        ''')
        self.favorite_dropdown.setStyleSheet(f'''
            QToolButton#expandedFavoriteDropdown {{color:{text};background:transparent;border:0;
                border-radius:5px;padding:0;}}
            QToolButton#expandedFavoriteDropdown:hover {{background:{hover};}}
        ''')
        self.directory_apply.setStyleSheet(f'''
            QToolButton#expandedDirectoryApply {{color:{text};background:{active};border:1px solid {border};
                border-radius:6px;padding:0;font-size:15px;font-weight:600;}}
            QToolButton#expandedDirectoryApply:hover {{background:{hover};border-color:#55a38c;}}
        ''')
        # Recolor non-primary column text when the theme changes.
        self.middle._theme = theme_family(theme)
        for idx in range(self.middle.tree.topLevelItemCount()):
            row = self.middle.tree.topLevelItem(idx)
            for col in (1, 2, 3):
                row.setForeground(col, QBrush(QColor(
                    '#81928a' if light else '#a1afa8')))
        self.middle_empty_label.setStyleSheet(
            f'QLabel#filesListEmptyLabel {{ background:transparent;'
            f' color:{"#8e918d" if light else "#abb0aa"};font-size:12px; }}')
        self.middle_parent_return_hint.setStyleSheet(
            f'QLabel#filesListParentReturnHint {{ background:transparent;'
            f' color:{"#adb4af" if light else "#87928b"};font-size:12px; }}')
        self.favorite_dropdown.setIcon(combo_chevron_icon(theme_family(theme)))
        self.address_bar._position_dropdown()
        self.shared_icon.setPixmap(header_icon('folder', theme_family(theme)).pixmap(28, 28))
        if self.bookmarks_root is not None:
            for index, root in enumerate(self.root_rows):
                if root.get('item_id') == self.bookmarks_root.get('item_id'):
                    self.root_buttons[index].setIcon(header_icon('bookmark', theme_family(theme)))
        for pane in (self.left, self.middle, self.right):
            pane.back.setIcon(browser_navigation_icon('back', theme_family(theme)))
            pane.tree.verticalScrollBar().setSingleStep(26 if tight else 35)
            pane.row_height = 27 if tight else 37
            pane._theme = theme
            pane.tree._drive_name_theme = theme_family(theme)
            for row_index in range(pane.tree.topLevelItemCount()):
                item = pane.tree.topLevelItem(row_index)
                if pane.kind == 'bookmark' and item.data(0, Qt.ItemDataRole.UserRole + 1):
                    pane.style_bookmark_heading(item)
                else:
                    for column in range(5 if pane is self.middle else 2):
                        item.setSizeHint(column, QSize(0, pane.row_height))
            if pane.kind == 'bookmark':
                for i in range(pane.tree.topLevelItemCount()):
                    item = pane.tree.topLevelItem(i)
                    row = item.data(0, Qt.ItemDataRole.UserRole)
                    if row and row.get('item_kind') not in ('category', 'directory'):
                        item.setIcon(0, link_icon(theme_family(theme)))
            # Ribbon appears visually larger than Files' green folder at 28px.
            pane.icon_label.setPixmap(header_icon(pane.kind, theme_family(theme)).pixmap(
                24 if pane.kind == 'bookmark' else 28,
                24 if pane.kind == 'bookmark' else 28))

    def browser_rows(self, parent):
        """Resolve dynamic 'This PC' drives only in the expanded Files pane."""
        if parent.get('_system_drives_root'):
            return drive_rows()
        rows = self.launcher.displayed_children(parent)
        if self.files_root and parent.get('item_id') == self.files_root.get('item_id'):
            return [pc_preview_row(row) for row in rows]
        return rows

    def refresh(self, roots, left, right, options):
        if self._refreshing:
            return
        self._refreshing = True
        try:
            self.options = options
            for old_button in getattr(self, 'root_buttons', ()):
                old_button.deleteLater()
            self.root_buttons = []
            self.workspace_page_buttons = []
            self._toolbar_wheel_current = None
            self._toolbar_wheel_remainder = 0
            # Cancel a pending warp targeting a button about to be replaced.
            self._wheel_root_follow_pending = None
            # Do not alter Launch DataJSON: the two permanent panel roots are
            # simply not duplicated as buttons in this expanded-view toolbar.
            visible_roots = toolbar_roots(roots, left, right)
            self.root_rows, self.files_root, self.bookmarks_root = visible_roots, left, right
            if self._wheel_root_id not in {row.get('item_id') for row in visible_roots}:
                self._wheel_root_id = None
            self._wheel_root_delta = 0
            self._wheel_bookmark_delta = 0
            self.cancel_bookmark_pointer_follow()
            self.cancel_bookmark_hover()
            while self.root_layout.count():
                item = self.root_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            # Workspaces on the LEFT; user-authored second-layer shortcuts on
            # the RIGHT. These are not Page tabs and do not alter Launch JSON.
            self.files_mode_tab = QPushButton('Files', self.root_widget)
            self.browser_mode_tab = QPushButton('Browser', self.root_widget)
            for button in (self.files_mode_tab, self.browser_mode_tab):
                button.setObjectName('expandedWorkspaceTab')
                button.setProperty('workspace', 'files' if button is self.files_mode_tab else 'browser')
                button.setCheckable(True)
                button.setFixedHeight(38)
                button.setMinimumWidth(84)
                button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Keyboard/Remote target
                button.installEventFilter(self.launcher)
                button.installEventFilter(self)
                self.root_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignBottom)
            self.files_mode_tab.setToolTip('ファイル・フォルダーを表示（状態は保持）')
            self.browser_mode_tab.setToolTip('Webタブとブックマークを表示（状態は保持）')
            self.files_mode_tab.clicked.connect(lambda _checked=False: self.switch_workspace('files'))
            self.browser_mode_tab.clicked.connect(lambda _checked=False: self.switch_workspace('browser'))
            self._update_workspace_tabs()
            # Launch Page buttons live alongside the two workspaces rather
            # than up in the title header or on the remote control. Unlike
            # QTabBar selection, they open the same Page cascade as Remote.
            for page in ([] if getattr(self.launcher, 'hide_page_buttons', True)
                         else list(getattr(self.launcher, 'pages', ()))):
                page_id = str(page.get('page_id') or '')
                if not page_id:
                    continue
                button = QPushButton(page_display_title(page), self.root_widget)
                button.setObjectName('expandedPageButton')
                button.setFixedHeight(30)
                button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                button.setToolTip('このPageのメニューを開く（ホイール：5ボタンを選択）')
                button.installEventFilter(self)
                button.clicked.connect(lambda checked=False, pid=page_id, b=button:
                                       self.launcher.open_remote_page(pid, anchor=b))
                button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                button.customContextMenuRequested.connect(
                    lambda _point, pid=page_id, b=button:
                    self.launcher.open_remote_page(pid, anchor=b))
                self.root_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignVCenter)
                self.workspace_page_buttons.append(button)
            # Use a real mouse-receiving widget for the wide blank band.
            # QLayout.addStretch() has no QWidget hit target: clicks used to
            # fall through to the root's 'select first shortcut' handler.
            # The decorative spacer is the only extra drag target; the
            # workspace tabs and every authored shortcut remain clickable.
            self.workspace_drag_handle = QWidget(self.root_widget)
            self.workspace_drag_handle.setObjectName('expandedWorkspaceDragHandle')
            self.workspace_drag_handle.setCursor(Qt.CursorShape.ArrowCursor)
            self.workspace_drag_handle.setToolTip('ここをドラッグしてFRB Launchを移動')
            self.workspace_drag_handle.setMinimumWidth(1)
            self.workspace_drag_handle.installEventFilter(
                self.launcher._passive_header_drag)
            self.root_layout.addWidget(self.workspace_drag_handle, 1)
            for index, row in enumerate(visible_roots):
                button = QPushButton(row.get('title', ''), self.root_widget)
                button.setObjectName('expandedRootButton')
                # Right-side shortcuts retain their compact height while the
                # Files / Browser workspace tabs grow to 38px.
                button.setMaximumHeight(30)
                button.setCheckable(True)
                button.setChecked(row.get('item_id') == self._wheel_root_id)
                button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                button.installEventFilter(self.launcher)
                button.installEventFilter(self)
                button.setIcon(header_icon('bookmark', self.launcher.color_theme)
                               if row.get('item_id') == right['item_id'] else self.launcher.row_icon(row))
                # The short ZIP label clips when the focus outline grows from
                # 1px to 2px and the checked button switches to a bold font.
                # Reserve a few extra pixels for ZIP only; other roots keep
                # their original natural widths.
                if row.get('title') == 'ZIP':
                    button.setMinimumWidth(button.sizeHint().width() + 10)
                hint = f'Ctrl+Shift+F{index+1}' if index < 12 else ''
                button.setToolTip((' / '.join(v for v in (row.get('description', ''), hint) if v)))
                button.clicked.connect(lambda checked=False, r=row, b=button: self.root_action(r, b))
                # Root shortcuts remain in memory/search/keyboard routes, but
                # their old second-layer button strip is no longer displayed.
                button.hide()
                self.root_buttons.append(button)
            # The green Files header is a UI label, not the editable title of
            # the System/Files JSON category. Studio renames must not leak here.
            self.left.label.setText('Files')
            self.shared_title.setText('Files')
            self.right.label.setText(right['title'])
            files_rows = self.browser_rows(left)
            self.left.fill(files_rows, self.launcher.row_icon)
            self.right.fill(expanded_bookmark_rows(right, self.launcher.children), self.launcher.row_icon)
            self.refresh_horizontal_bookmarks()
            # Start with one real folder in the middle, never invented PC data.
            if not self.path:
                initial = next((row for row in files_rows
                                if row.get('item_kind') in ('category', 'directory')), None)
                if initial:
                    self.path = [initial]
                    for index in range(self.left.tree.topLevelItemCount()):
                        item = self.left.tree.topLevelItem(index)
                        if item.data(0, Qt.ItemDataRole.UserRole).get('item_id') == initial.get('item_id'):
                            self.left.tree.setCurrentItem(item)
                            break
            # Data may have been reloaded; re-resolve every directory in the path.
            updated = []
            for old in self.path:
                if old.get('_address_synthetic'):
                    import os
                    actual = row_directory(old)
                    if not actual or not os.path.isdir(actual):
                        break
                    updated.append(directory_row(actual))
                    continue
                parent = updated[-1] if updated else left
                matching = next((r for r in self.browser_rows(parent)
                                 if r.get('item_id') == old.get('item_id')), None)
                if matching is None:
                    break
                updated.append(matching)
            self.path = updated
            self.refresh_middle()
            if getattr(self.launcher, 'files_exp_embedded_mode', False):
                self.reload_embedded_files_exp_roots(preserve_state=True)
        finally:
            self._refreshing = False

    def _save_middle_header_state(self, *_):
        if self._middle_header_restoring or self._middle_header_virtual:
            return
        self.launcher.settings.setValue('expanded_middle_header_state_v50',
                                        self.middle.tree.header().saveState())

    def _set_middle_columns_for_source(self, virtual):
        """Swap List headers/visible columns without touching saved Files layout.

        The physical header state, including user order/widths, is restored on
        return. A virtual-only resize must never overwrite the Files setting.
        """
        virtual = bool(virtual)
        self.middle.virtual_details_columns = virtual
        if virtual == self._middle_header_virtual:
            return
        tree = self.middle.tree
        header = tree.header()
        self._middle_header_restoring = True
        try:
            if virtual:
                self._physical_middle_header_state = header.saveState()
                tree.setHeaderLabels(list(LAUNCH_HEADERS))
                tree.setColumnHidden(3, True)
                # JSON explanations need space; keep a separate kind column.
                tree.setColumnWidth(1, 350)
                tree.setColumnWidth(2, 145)
            else:
                tree.setColumnHidden(3, False)
                tree.setHeaderLabels(list(FILES_HEADERS))
                saved = self._physical_middle_header_state
                if saved is not None:
                    header.restoreState(saved)
                header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
                self._physical_middle_header_state = None
            self._middle_header_virtual = virtual
        finally:
            self._middle_header_restoring = False

    def _update_middle_header_sort(self):
        mode = self._middle_sort_mode
        column = (1 if mode.startswith(('date', 'description'))
                  else 2 if mode.startswith(('size', 'item_kind'))
                  else 3 if mode.startswith('type') else 0)
        # Qt's native sort indicator artwork points opposite to the Explorer
        # convention on this view/style. The rows themselves are sorted by
        # filter_sort_folder_rows, with QTreeWidget sorting disabled; swap the
        # indicator order ONLY to show ▲ for ascending and ▼ for descending.
        direction = (Qt.SortOrder.AscendingOrder
                     if mode.endswith('desc') else Qt.SortOrder.DescendingOrder)
        self.middle.tree.header().setSortIndicator(column, direction)

    def _middle_header_clicked(self, logical_column):
        if getattr(self, '_virtual_directory_node', None) is not None:
            mode = virtual_sort_mode_for_header(logical_column, self._middle_sort_mode)
        else:
            mode = sort_mode_for_header(logical_column, self._middle_sort_mode)
        if mode is not None:
            if getattr(self, '_virtual_directory_node', None) is not None:
                self._virtual_sort_custom = True
                self.middle.tree.header().setSortIndicatorShown(True)
            self.set_middle_sort(mode)

    def set_middle_sort(self, mode):
        if mode not in SORT_LABELS:
            return
        self._middle_sort_mode = mode
        directory = self.current_directory()
        if directory:
            save_directory_sort(self.launcher.settings, directory, mode, SORT_LABELS)
            self._middle_sort_directory = directory
        self._update_middle_header_sort()
        self._fill_middle_from_current()

    def _dismiss_middle_search_history_on_outside_click(self, obj, event):
        """Restore outside-click dismissal for the non-grabbing Files List menu.

        Unlike a native Qt.Popup, the Tool-style history menu does not dismiss
        itself when another widget receives a mouse press.  This view already
        filters QApplication events, so observe the press without consuming it:
        the clicked file, button, or other control must still work normally.
        """
        menu = getattr(self, 'middle_search_history_menu', None)
        if menu is None or not menu.isVisible():
            return
        kind = event.type()
        if kind == QEvent.Type.ApplicationDeactivate:
            # Includes clicks on the desktop / a different application, which
            # are not delivered as widget mouse presses to this Qt process.
            menu.hide()
            return
        if kind != QEvent.Type.MouseButtonPress:
            return
        point = event.globalPosition().toPoint()
        button = self.middle_search_history_button
        if (button.isVisible() and
                button.rect().contains(button.mapFromGlobal(point))):
            # The clock button owns its existing click-to-toggle behavior.
            return
        if menu.frameGeometry().contains(point):
            return  # Let QMenu deliver this press to its QAction.
        for submenu in menu.findChildren(QMenu):
            if submenu.isVisible() and submenu.frameGeometry().contains(point):
                return  # Do not close while selecting a '履歴から削除' item.
        menu.hide()

    def toggle_middle_search_history_menu(self):
        """Toggle Files List keyword history without Qt's global popup grab.

        A real button press and an OS click from the Windows rod enter through
        the same signal.  The menu is positioned next to its original button;
        the original keyword and removal QAction handlers remain unchanged.
        """
        menu = self.middle_search_history_menu
        if menu.isVisible():
            menu.hide()
            return
        self.populate_middle_search_history_menu()
        button = self.middle_search_history_button
        size = menu.sizeHint()
        point = button.mapToGlobal(QPoint(0, button.height()))
        screen = QApplication.screenAt(point) or QApplication.primaryScreen()
        if screen is not None:
            bounds = screen.availableGeometry()
            point.setX(max(bounds.left(), min(point.x(),
                          bounds.right() - size.width() + 1)))
            if point.y() + size.height() > bounds.bottom() + 1:
                point.setY(button.mapToGlobal(QPoint(0, -size.height())).y())
            point.setY(max(bounds.top(), min(point.y(),
                          bounds.bottom() - size.height() + 1)))
        menu.popup(point)

    def populate_middle_search_history_menu(self):
        """Refresh the left-side button's popup each time it is opened."""
        menu = self.middle_search_history_menu
        menu.clear()
        current = self.middle_search.text().strip()
        register = menu.addAction('＋  現在のキーワードを履歴に登録')
        register.setEnabled(bool(current))
        register.triggered.connect(self.register_middle_search_history)
        menu.addSeparator()
        if not self.files_list_search_history.keywords:
            placeholder = menu.addAction('（登録された検索履歴はありません）')
            placeholder.setEnabled(False)
        else:
            for keyword in self.files_list_search_history.keywords:
                action = menu.addAction(keyword)
                action.setToolTip(keyword)
                action.triggered.connect(
                    lambda checked=False, value=keyword: self.select_middle_search_history(value))
            menu.addSeparator()
            # The submenu must also avoid a native Qt.Popup grab.  Otherwise
            # the rod would stop working again on the 'remove history' branch.
            forget = _NonGrabbingHistoryMenu(menu)
            forget.setTitle('履歴から削除')
            menu.addMenu(forget)
            for keyword in self.files_list_search_history.keywords:
                action = forget.addAction(keyword)
                action.triggered.connect(
                    lambda checked=False, value=keyword: self.remove_middle_search_history(value))

    def register_middle_search_history(self, *_):
        try:
            self.files_list_search_history.remember(self.middle_search.text())
        except OSError as exc:
            self.middle_search_history_button.setToolTip('検索履歴を保存できません: ' + str(exc))

    def select_middle_search_history(self, keyword):
        # Existing textChanged -> apply_middle_filter keeps AND/OR semantics.
        self.middle_search.setText(keyword)
        self.middle_search.setFocus(Qt.FocusReason.MouseFocusReason)

    def remove_middle_search_history(self, keyword):
        try:
            self.files_list_search_history.remove(keyword)
        except OSError as exc:
            self.middle_search_history_button.setToolTip('検索履歴を削除できません: ' + str(exc))

    def apply_middle_filter(self, *_):
        # Keep the local search separate from Launcher-global search.
        self._fill_middle_from_current()

    def _position_middle_empty_label(self):
        label = getattr(self, 'middle_empty_label', None)
        if label is None:
            return
        viewport = self.middle.tree.viewport()
        # Explorer-like guidance in the second visible row, not screen centre.
        height = 28
        label.setGeometry(0, min(28, max(0, viewport.height() - height)),
                          viewport.width(), height)

    def _position_middle_parent_return_hint(self):
        label = getattr(self, 'middle_parent_return_hint', None)
        if label is None:
            return
        viewport = self.middle.tree.viewport()
        count = self.middle.tree.topLevelItemCount()
        if viewport.width() <= 0 or viewport.height() <= 0:
            label.hide()
            return
        if count > 0:
            last = self.middle.tree.topLevelItem(count - 1)
            rect = self.middle.tree.visualItemRect(last)
            content_bottom = max(0, rect.bottom() + 1)
        else:
            content_bottom = 0
        blank_top = min(viewport.height(), content_bottom + 10)
        blank_height = viewport.height() - blank_top
        hint_height = 24
        if blank_height < hint_height + 8:
            label.hide()
            return
        y = blank_top + max(0, (blank_height - hint_height) // 2)
        label.setGeometry(0, y, viewport.width(), hint_height)
        label.show()
        label.raise_()

    def _update_middle_empty_label(self):
        label = getattr(self, 'middle_empty_label', None)
        if label is None:
            return
        directory = self.current_directory()
        empty = ((bool(directory) and os.path.isdir(directory)
                  or getattr(self, '_virtual_directory_node', None) is not None)
                 and self.middle.tree.topLevelItemCount() == 0)
        if empty:
            # A filtered-out folder is not actually empty.
            label.setText('一致する項目はありません。' if self.middle_search.text().strip()
                          else 'このフォルダーは空です。')
            self._position_middle_empty_label()
            label.show()
            label.raise_()
        else:
            label.hide()
        self._position_middle_parent_return_hint()

    def _fill_middle_from_current(self):
        virtual = getattr(self, '_virtual_directory_node', None)
        self._set_middle_columns_for_source(virtual is not None)
        if virtual is not None:
            rows = virtual_list_rows(virtual)
            # The first view keeps the user's Studio/Launch JSON menu order.
            # A click on a List column heading explicitly overrides that order.
            source_order = {row['_launch_virtual_node']['node_id']: i
                            for i, row in enumerate(rows)}
            rows = filter_sort_folder_rows(
                rows, self.middle_search.text(), self._middle_sort_mode)
            if not getattr(self, '_virtual_sort_custom', False):
                rows.sort(key=lambda r: source_order[
                    r['_launch_virtual_node']['node_id']])
            self.middle.fill(rows, self.launcher.row_icon)
            self._queue_middle_selection_repair()
            self._update_middle_empty_label()
            update_count = getattr(self.launcher, 'update_files_item_count', None)
            if callable(update_count):
                update_count(self.middle.tree.topLevelItemCount())
            return
        current = self.path[-1] if self.path else None
        if current is None:
            self.middle.tree.clear()
            self._update_middle_empty_label()
            update_count = getattr(self.launcher, 'update_files_item_count', None)
            if callable(update_count):
                update_count(0)
            return
        # Re-rendering while editing can destroy the QLineEdit and discard an
        # unfinished filesystem rename. Never do that.
        if self.middle.tree.state() == QAbstractItemView.State.EditingState:
            return
        try:
            rows = self.browser_rows(current)
        except (OSError, ValueError, PermissionError) as exc:
            rows = []
            self.middle.label.setToolTip(str(exc))
        rows = filter_sort_folder_rows(
            rows, self.middle_search.text(), self._middle_sort_mode)
        if self._middle_sort_mode.startswith('type'):
            # Sort by the SAME Windows-registered type names that are displayed,
            # not merely the suffix fallback used in the headless core module.
            rows.sort(key=lambda row: self.middle.file_type_label(row).casefold(),
                      reverse=self._middle_sort_mode == 'type_desc')
            rows.sort(key=lambda row: row.get('item_kind') not in ('category', 'directory'))
        tree = self.middle.tree
        # Sorting/filtering re-creates Qt items. Preserve all still-visible
        # selected paths (not just the current item), including Ctrl+click.
        selected_keys = {row_key(self.row_data(item))
                         for item in tree.selectedItems()
                         if row_key(self.row_data(item))}
        self.middle.fill(rows, self.launcher.row_icon)
        if selected_keys:
            restored = []
            for index in range(tree.topLevelItemCount()):
                item = tree.topLevelItem(index)
                if row_key(self.row_data(item)) in selected_keys:
                    restored.append(item)
            if restored:
                tree.clearSelection()
                for item in restored:
                    item.setSelected(True)
        self._queue_middle_selection_repair()
        self._update_middle_empty_label()
        update_count = getattr(self.launcher, 'update_files_item_count', None)
        if callable(update_count):
            update_count(tree.topLevelItemCount())

    def refresh_middle(self):
        self._middle_back_hold.reset()
        self._middle_back_warp_pending = None
        virtual = getattr(self, '_virtual_directory_node', None)
        self._set_middle_columns_for_source(virtual is not None)
        if virtual is not None:
            # This is a *display* breadcrumb, not an editable OS pathname.
            self.middle.tree.header().setSortIndicatorShown(
                getattr(self, '_virtual_sort_custom', False))
            self.middle.label.setText(virtual['title'])
            self.address_bar.set_directory(None, ' › '.join(
                virtual.get('breadcrumbs') or (virtual['title'],)))
            self.middle.back.setEnabled(True)
            location = virtual['node_id']
            if location != self._middle_query_directory:
                self._middle_query_directory = location
                blocked = self.middle_search.blockSignals(True)
                try:
                    self.middle_search.clear()
                finally:
                    self.middle_search.blockSignals(blocked)
                self._middle_sort_mode = DEFAULT_SORT
                self._middle_sort_directory = location
                self._update_middle_header_sort()
            self._fill_middle_from_current()
            self.update_directory_favorite_button()
            self.launcher._nav_update_buttons()
            return
        header_getter = getattr(self.middle.tree, 'header', None)
        if callable(header_getter):
            header_getter().setSortIndicatorShown(True)
        current = self.path[-1] if self.path else None
        self.middle.label.setText(current['title'] if current else 'フォルダーを選択')
        self.address_bar.set_directory(
            row_directory(current, self.launcher.expander().expand),
            current['title'] if current else '')
        self.middle.back.setEnabled(bool(self.path))
        # Search is scoped to ONE displayed directory. A folder transition
        # must not unexpectedly leave the new folder blank due to old filters.
        folder = self.current_directory()
        if folder != self._middle_sort_directory:
            self._middle_sort_directory = folder
            self._middle_sort_mode = load_directory_sort(
                self.launcher.settings, folder, SORT_LABELS)
            self._update_middle_header_sort()
        if folder != self._middle_query_directory:
            self._middle_query_directory = folder
            previous = self.middle_search.blockSignals(True)
            try:
                self.middle_search.clear()
            finally:
                self.middle_search.blockSignals(previous)
        if current:
            self._fill_middle_from_current()
        else:
            self.middle.tree.clear()
            self._update_middle_empty_label()
        self.update_directory_favorite_button()
        # Record only completed folder transitions, regardless of origin:
        # Files first column, folder contents, breadcrumbs, favorites, Up.
        # The history model deduplicates F5/re-render of the same destination.
        if not self._restoring_directory_history:
            root = self.left.tree.currentItem()
            row = self.row_data(root) if root is not None else None
            self.directory_history.record(
                self.current_directory(), self.path,
                row.get('item_id') if row else None)
        self.launcher._nav_update_buttons()
        changed = getattr(self.launcher, 'on_files_directory_changed', None)
        if callable(changed):
            changed(self.current_directory())

    def _restore_directory_history(self, entry):
        if entry is None:
            return False
        self._restoring_directory_history = True
        try:
            self.path = list(entry['rows'])
            if entry['root_id'] is not None:
                for index in range(self.left.tree.topLevelItemCount()):
                    candidate = self.left.tree.topLevelItem(index)
                    row = self.row_data(candidate)
                    if row and row.get('item_id') == entry['root_id']:
                        self.left.tree.setCurrentItem(candidate)
                        break
            self.refresh_middle()
            self.focus_panel(self.middle)
        finally:
            self._restoring_directory_history = False
            self.launcher._nav_update_buttons()
        return True

    def history_back(self):
        return self._restore_directory_history(self.directory_history.back())

    def history_forward(self):
        return self._restore_directory_history(self.directory_history.forward())

    def update_directory_favorite_button(self):
        target = self.current_directory()
        import ntpath
        registered = bool(target and any(ntpath.normcase(p) == ntpath.normcase(target)
                        for p in self.folder_favorites.paths))
        self.favorite_save.setText('🩶' if registered else '💛')
        self.favorite_save.setToolTip('お気に入り登録済み' if registered else '今のフォルダーをお気に入りに登録')
        self.favorite_save.setEnabled(bool(target))
        self.favorite_dropdown.setEnabled(bool(self.folder_favorites.paths))
        self.favorite_dropdown.setToolTip(
            f'お気に入りフォルダーを選択（{len(self.folder_favorites.paths)}件）')

    def register_directory_favorite(self):
        target = self.current_directory()
        if not target:
            return
        try:
            self.folder_favorites.add(target)
        except OSError:
            self.launcher.error('お気に入りの保存に失敗しました')
            return
        self.update_directory_favorite_button()
        if self.favorite_popup.isVisible():
            self.populate_directory_favorites(target)

    def populate_directory_favorites(self, selected=None):
        self.favorite_choices.blockSignals(True)
        self.favorite_choices.clear()
        for path in self.folder_favorites.paths:
            row = QTreeWidgetItem([path, '×'])
            row.setIcon(0, self.launcher.file_icons.icon(QFileIconProvider.IconType.Folder))
            row.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
            row.setToolTip(0, path + '  — クリックでLaunch内のフォルダーへ移動／ドラッグで並び替え')
            row.setToolTip(1, 'お気に入りを削除（実フォルダーは削除されません）')
            self.favorite_choices.addTopLevelItem(row)
            if path == selected:
                self.favorite_choices.setCurrentItem(row)
        if self.favorite_choices.topLevelItemCount() and self.favorite_choices.currentItem() is None:
            self.favorite_choices.setCurrentItem(self.favorite_choices.topLevelItem(0))
        self.favorite_choices.blockSignals(False)
        if self.favorite_popup.isVisible():
            self.position_directory_favorites()

    def position_directory_favorites(self):
        # 1.5-column mode: both history overlays begin at Files List's left
        # edge, keeping the separate Remote fully reachable beneath them.
        anchor = self.address_bar.mapTo(self.launcher, QPoint(0, self.address_bar.height() + 4))
        width = min(self.address_bar.width(), max(1, self.launcher.width() - 12))
        x = anchor.x()
        if (getattr(self.launcher, 'remote_15_mode', False)
                and self._workspace_mode == 'files'):
            title = getattr(self, 'files_list_title_box', None)
            if title is not None and title.isVisible():
                x = title.mapTo(self.launcher, QPoint(0, 0)).x()
        width = min(width, max(1, self.launcher.width() - x - 12))
        x = max(6, min(x, self.launcher.width() - width - 6))
        y = anchor.y()
        footer_top = self.launcher.footer.mapTo(self.launcher, QPoint(0, 0)).y()
        available = popup_available_height(self.launcher.height(), y, footer_top)
        rows = (self.favorite_choices.topLevelItem(i)
                for i in range(self.favorite_choices.topLevelItemCount()))
        # 30px CSS row + padding; frame margins and a little space below the
        # final row. Only scroll when the popup reaches the launcher footer.
        height = popup_tree_height(self.favorite_choices, rows,
                                   minimum_row_height=34, chrome_height=16,
                                   available_height=available)
        self.favorite_popup.setGeometry(x, y, width, height)

    def wheel_directory_favorite_history(self, obj, event):
        """Browse favorite popup rows, or preview a path inside the address edit.

        Browsing must NEVER change folders. Click a popup item or press Enter
        in the address editor to navigate; Escape abandons a preview.
        """
        if (event.modifiers() != Qt.KeyboardModifier.NoModifier or
                QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return False
        choices = self.favorite_choices
        bar = self.address_bar
        in_address = (obj is bar or obj is bar.editor or obj is bar.surface or
                      (isinstance(obj, QWidget) and
                       bar.isAncestorOf(obj) and obj not in (
                           self.favorite_save, self.favorite_dropdown,
                           self.directory_apply)))
        in_popup = (self.favorite_popup.isVisible() and
                    (obj in (choices, choices.viewport()) or in_address))
        if not in_popup and not in_address:
            return False
        if in_popup:
            pending, steps = wheel_steps(self._favorite_popup_wheel_delta,
                                         event.angleDelta().y(), event.pixelDelta().y())
            self._favorite_popup_wheel_delta = pending
            if not steps:
                return True
            count = choices.topLevelItemCount()
            if not count:
                return True
            index = history_target_index(choices.indexOfTopLevelItem(choices.currentItem()),
                                         count, steps)
            target = choices.topLevelItem(index)
            choices.setCurrentItem(target)
            choices.scrollToItem(target, QAbstractItemView.ScrollHint.EnsureVisible)
            origin = QCursor.pos()
            self._favorite_popup_warp_generation += 1
            generation = self._favorite_popup_warp_generation
            QTimer.singleShot(0, lambda: (
                warp_to_history_row(choices, target, origin, QCursor)
                if (getattr(getattr(self, 'launcher', None), 'pointer_warp_enabled', True) and
                    generation == self._favorite_popup_warp_generation) else None))
            return True
        if self.favorite_popup.isVisible():
            # An open list owns its own wheel; clicking its choices navigates.
            return False
        paths = self.folder_favorites.paths
        if not paths:
            return False
        pending, steps = wheel_steps(self._favorite_path_wheel_delta,
                                     event.angleDelta().y(), event.pixelDelta().y())
        self._favorite_path_wheel_delta = pending
        if not steps:
            return True
        # Preview one favorite path per notch without activating it.
        return self.preview_directory_favorite_steps(steps)

    def preview_directory_favorite_steps(self, steps):
        """Preview saved paths without navigation; used by native and Remote wheels."""
        paths = self.folder_favorites.paths
        if not paths or not steps:
            return False
        bar = self.address_bar
        current = bar.editor.text() if bar.currentWidget() is bar.editor else bar.current_path
        import ntpath
        found = next((i for i, path in enumerate(paths)
                      if ntpath.normcase(path) == ntpath.normcase(current)), None)
        index = (found + steps) % len(paths) if found is not None else (
            0 if steps > 0 else len(paths) - 1)
        bar.editor.setText(paths[index])
        bar.setCurrentWidget(bar.editor)
        bar._position_dropdown()
        bar._update_apply_visibility()
        bar.editor.setCursorPosition(len(paths[index]))
        bar.editor.setFocus(Qt.FocusReason.MouseFocusReason)
        return True

    def toggle_directory_favorites(self):
        if self.favorite_popup.isVisible():
            self.hide_favorite_popup()
            return
        if not self.folder_favorites.paths:
            return
        if self.launcher.history_popup.isVisible():
            self.launcher.hide_history_popup()
        self.populate_directory_favorites()
        self.position_directory_favorites()
        self.favorite_popup.show()
        self.favorite_popup.raise_()
        self.favorite_choices.setFocus(Qt.FocusReason.MouseFocusReason)

    def hide_favorite_popup(self):
        self.favorite_popup.hide()
        self._favorite_popup_wheel_delta = 0
        self._favorite_popup_warp_generation += 1

    def directory_favorite_clicked(self, item, column):
        path = item.text(0)
        if column == 1:
            try:
                self.folder_favorites.remove(path)
            except OSError:
                self.launcher.error('お気に入りの削除に失敗しました')
                return
            self.populate_directory_favorites()
            self.update_directory_favorite_button()
            if not self.folder_favorites.paths:
                self.hide_favorite_popup()
            return
        self.hide_favorite_popup()
        if not self.go_to_directory(path):
            self.launcher.error('フォルダーが見つかりません: ' + path)

    def directory_favorites_reordered(self, paths):
        try:
            if not self.folder_favorites.reorder(paths):
                self.populate_directory_favorites()
        except OSError:
            self.launcher.error('お気に入りの並び替えを保存できませんでした')
            self.populate_directory_favorites()

    def current_directory(self):
        if getattr(self, '_virtual_directory_node', None) is not None:
            return None  # A Launch JSON menu has no physical filesystem path.
        return row_directory(self.path[-1], self.launcher.expander().expand) if self.path else None

    def show_virtual_launch_directory(self, node):
        """Read-only virtual folder: Exp is navigation, List is its contents."""
        if (not isinstance(node, dict) or node.get('source') != 'launch_json'
                or node.get('kind') == 'file'):
            return False
        # The System Page is internal to Studio. Files Exp promotes its Browser
        # category to a Page-level 「ブックマーク」 root without changing JSON IDs.
        options = getattr(self.launcher, 'expanded_options', {}) or {}
        node = virtual_exp_presentation(
            node, system_page_id=options.get('page_id', 'system'),
            bookmarks_item_id=options.get('bookmarks_item_id',
                                          '__browser_bookmarks_root'))
        if (getattr(self, '_virtual_directory_node', None) is None or
                self._virtual_directory_node.get('node_id') != node['node_id']):
            self._virtual_sort_custom = False
        self._virtual_directory_node = node
        self.refresh_middle()
        # Keep the Exp row selected even when navigating a virtual subfolder
        # via the List (without stealing the user's logical List focus).
        for panel in (getattr(self, 'embedded_files_exp', None),
                      getattr(getattr(self.launcher, 'remote_window', None),
                              'files_exp_panel', None)):
            if panel is not None and panel.isVisible():
                panel.remote_select_virtual_node(node)
        return True

    def _clear_virtual_directory(self):
        self._virtual_directory_node = None

    def _parent_virtual_directory(self):
        current = getattr(self, '_virtual_directory_node', None)
        if current is None:
            return None
        return virtual_lookup_node(self.launcher.pages, self.launcher.authored_items,
                                   current['page_id'],
                                   current.get('parent_item_id') or '',
                                   (self.launcher.data or {}).get('items', ()))

    def middle_selected_paths(self):
        if getattr(self, '_virtual_directory_node', None) is not None:
            return []  # Launch JSON objects are NEVER filesystem deletion targets.
        rows = [self.row_data(item) for item in self.middle.tree.selectedItems()]
        return physical_paths(rows, self.launcher.authored_items)


    def rename_selected_middle_item(self):
        """F2: invoke the same in-place filename editor as context Rename.

        The shortcut is scoped to the middle file list (not the search box,
        Page tabs or other columns). Never guess a target on multi-selection.
        """
        tree = self.middle.tree
        focused = QApplication.focusWidget()
        if (not self.isVisible() or focused is None or
                not (focused is tree or tree.isAncestorOf(focused)) or
                tree.state() == QAbstractItemView.State.EditingState or
                len(tree.selectedItems()) > 1):
            return False
        item = tree.currentItem()
        return bool(item is not None and self.begin_inline_rename(item))

    def refresh_current_directory(self):
        """F5: re-read filesystem entries while preserving selection/scroll.

        Qt rebuilds the QTreeWidgetItems on refresh. Restore matching paths
        by displayed name so keyboard navigation doesn't jump to another row.
        This is a manual refresh; it does not modify the file index catalog.
        """
        directory = self.current_directory()
        tree = self.middle.tree
        if (not self.isVisible() or not directory or not Path(directory).is_dir() or
                tree.state() == QAbstractItemView.State.EditingState):
            return False
        selected_names = {self.row_data(item).get('title') for item in tree.selectedItems()
                          if self.row_data(item)}
        current = tree.currentItem()
        current_row = self.row_data(current) if current else None
        current_name = current_row.get('title') if current_row else None
        scroll = tree.verticalScrollBar().value()
        self.refresh_middle()
        tree.clearSelection()
        restored_current = None
        for index in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(index)
            row = self.row_data(item)
            name = row.get('title') if row else None
            if name == current_name:
                restored_current = item
        if restored_current is not None:
            tree.setCurrentItem(restored_current)
        # setCurrentItem may reset the selection: put the multi-select set
        # back after restoring the current row, not before it.
        for index in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(index)
            row = self.row_data(item)
            if row and row.get('title') in selected_names:
                item.setSelected(True)
        tree.verticalScrollBar().setValue(scroll)
        return True

    def begin_context_inline_rename(self, item):
        """Keep a Qt.Tool launch window visible while the context menu closes."""
        launcher = self.launcher
        launcher._filesystem_dialog_depth = getattr(launcher, '_filesystem_dialog_depth', 0) + 1
        def open_editor():
            try:
                self.begin_inline_rename(item)
            finally:
                QTimer.singleShot(650, launcher._finish_batch_delete_guard)
        QTimer.singleShot(0, open_editor)

    def begin_inline_rename(self, item):
        """Edit filename in the middle grid; never rename authored commands."""
        tree = self.middle.tree
        if not item or tree.indexOfTopLevelItem(item) < 0:
            return False
        row = self.row_data(item)
        origin, path = resolve_context_target(row, self.launcher.authored_items)
        if origin not in ('file', 'folder') or not path or not Path(path).exists():
            return False
        # Temporarily enable directory editing; normal folder clicks still
        # enter the folder. The context menu invokes this method explicitly.
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        tree.setCurrentItem(item)
        self._inline_rename_active = True
        tree.editItem(item, 0)
        # QLineEdit should select only the stem, leaving the extension intact.
        editor = tree.findChild(QLineEdit)
        if editor is not None:
            # A native popup must not remain open after an inline edit commits.
            # Close *after* editingFinished so the QStyledItemDelegate can
            # commit the final text before the menu loses its focus.
            closer = getattr(self.launcher, 'close_finished_file_context_menus', None)
            if callable(closer):
                editor.editingFinished.connect(lambda: QTimer.singleShot(0, closer))
            if origin == 'file':
                length = len(Path(path).stem)
                editor.setSelection(0, length)
            else:
                # A canceled folder edit must not turn future folder clicks
                # into SelectedClicked editing. They still browse by click.
                def reset_folder_edit_flag():
                    try:
                        if tree.indexOfTopLevelItem(item) >= 0:
                            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    except RuntimeError:
                        pass  # The refreshed row was already released by Qt.
                editor.editingFinished.connect(
                    lambda: QTimer.singleShot(0, reset_folder_edit_flag))
        return True

    def commit_remote_inline_rename(self):
        """Commit an active file OR folder rename from the non-focusing Remote pad.

        Qt normally commits the editor on Enter or focus loss.  The Remote
        deliberately steals neither, so forward the same delegate commit and
        close signals used by the inline editor's Enter handler.  Do not route
        that same click to normal file activation.
        """
        tree = self.middle.tree
        if tree.state() != QAbstractItemView.State.EditingState:
            return False
        editor = tree.findChild(QLineEdit, 'inlineRenameEditor')
        delegate = tree.itemDelegateForColumn(0)
        # EditingState is authoritative: even if the editor is disappearing,
        # swallow the click rather than accidentally opening the file/folder.
        if editor is None or not isinstance(delegate, _InlineRenameDelegate):
            return True
        current_item = tree.currentItem()
        current_row = self.row_data(current_item) if current_item is not None else None
        folder_edit = bool(current_row and current_row.get('item_kind') == 'directory')
        tree._rename_enter_epoch = getattr(tree, '_rename_enter_epoch', 0) + 1
        epoch = tree._rename_enter_epoch
        tree._rename_enter_guard = True

        def release_guard():
            if getattr(tree, '_rename_enter_epoch', None) == epoch:
                tree._rename_enter_guard = False

        try:
            delegate.commitData.emit(editor)
            delegate.closeEditor.emit(editor, QAbstractItemDelegate.EndEditHint.NoHint)
        finally:
            # Folder rows are browse-on-click outside rename mode.  Programmatic
            # closeEditor may bypass QLineEdit.editingFinished, which normally
            # removes this temporary editable flag.
            if folder_edit and current_item is not None:
                try:
                    if tree.indexOfTopLevelItem(current_item) >= 0:
                        current_item.setFlags(current_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                except RuntimeError:
                    pass  # A pending refresh already disposed of this item.
            QTimer.singleShot(120, release_guard)
        return True

    def _dismiss_middle_rename_on_outside_click(self, obj, event):
        """Commit Files List rename on a click outside its editing row.

        The kana companion temporarily suppresses native FocusOut so Windows
        IME can compose text. This must *not* trap the rename editor when the
        user clicks the blank 1.5-column lane, another List row or a different
        Launch control. A click in the editing row itself keeps editing.
        Kana/Remote Tool windows are intentionally excluded.
        """
        if (event.type() != QEvent.Type.MouseButtonPress or
                event.button() not in (Qt.MouseButton.LeftButton,
                                       Qt.MouseButton.RightButton)):
            return
        panel = getattr(self, 'middle', None)
        if panel is None:
            return
        tree = panel.tree
        if tree.state() != QAbstractItemView.State.EditingState:
            return
        editor = tree.findChild(QLineEdit, 'inlineRenameEditor')
        if editor is None or not isinstance(obj, QWidget):
            return
        # Kana and Remote are separate Tool windows. Their controls (including
        # Send) must never terminate the editor just by taking focus.
        if obj.window() is not self.launcher:
            return
        if obj is editor or editor.isAncestorOf(obj):
            return
        if (obj is tree.viewport() and
                tree.itemAt(event.position().toPoint()) is tree.currentItem()):
            return
        # The outside click should only dismiss this edit. Temporarily block
        # SelectedClicked to prevent the SAME click from starting a fresh edit
        # when it lands on an already-selected other file row.
        previous_triggers = tree.editTriggers()
        tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        if not self.commit_remote_inline_rename():
            tree.setEditTriggers(previous_triggers)
            return
        companion = getattr(self.launcher, '_remote_kana_companion', None)
        if companion is not None:
            companion.forget_closed_inline_editor(editor)
        # Re-arm after the mouse release, not between press and release.
        # Qt may invoke SelectedClicked while handling mouseReleaseEvent.
        self._middle_rename_restore_triggers = previous_triggers
        self._middle_rename_wait_release = True

    def _restore_middle_rename_triggers_on_release(self, event):
        if not getattr(self, '_middle_rename_wait_release', False):
            return
        if event.type() != QEvent.Type.MouseButtonRelease:
            return
        self._middle_rename_wait_release = False
        triggers = self._middle_rename_restore_triggers
        self._middle_rename_restore_triggers = None
        # Run after Qt processes release to avoid a second SelectedClicked edit.
        def restore():
            panel = getattr(self, 'middle', None)
            if panel is not None and triggers is not None:
                panel.tree.setEditTriggers(triggers)
        QTimer.singleShot(0, restore)

    def finish_inline_rename(self, item, column):
        """Commit a real filesystem rename, rejecting invalid/colliding names."""
        if column != 0:
            return
        row = self.row_data(item)
        if not row:
            return
        origin, path = resolve_context_target(row, self.launcher.authored_items)
        if origin not in ('file', 'folder') or not path:
            return
        old_path = Path(path)
        new_name = item.text(0)
        # itemChanged also fires when Qt updates row icons, flags, size hints,
        # and other display metadata.  Those notifications are NOT renames.
        # In particular PC drive rows display "Volume (F:)" while their
        # physical path is "F:\\", so comparing only old_path.name would
        # falsely try to rename the drive to a string containing ':'.
        if (row.get('_system_drive') or
                new_name == row.get('title', old_path.name) or
                new_name == old_path.name):
            return
        try:
            # The default extension selection avoids changing .txt by accident.
            if (origin == 'file' and Path(new_name).suffix.casefold() != old_path.suffix.casefold()):
                from PySide6.QtWidgets import QMessageBox
                self.launcher._filesystem_dialog_depth = getattr(
                    self.launcher, '_filesystem_dialog_depth', 0) + 1
                try:
                    answer = self.launcher.ask_remote_confirmation(
                        '拡張子の変更',
                        '拡張子が変わります。名前を変更しますか？')
                finally:
                    self.launcher._filesystem_dialog_depth -= 1
                if answer != QMessageBox.StandardButton.Yes:
                    raise ValueError('拡張子の変更を取り消しました')
            renamed_path = rename_file_or_folder(old_path, new_name)
            if origin == 'folder':
                panel = getattr(getattr(self.launcher, 'remote_window', None), 'files_exp_panel', None)
                if panel is not None:
                    panel.reflect_external_folder_rename(str(old_path), str(renamed_path))
                self.launcher.notify_folder_mutation(old_path.parent)
            self.launcher.footer.setText(f'名前を変更しました: {old_path.name} → {new_name}')
            # Renaming rebuilds the row; keep the newly created folder current.
            def refresh_and_reselect(p=renamed_path):
                self.refresh_middle()
                self.select_created_middle_item(p)
            QTimer.singleShot(0, refresh_and_reselect)
        except (OSError, ValueError) as exc:
            tree = self.middle.tree
            tree.blockSignals(True)
            try:
                item.setText(0, old_path.name)
            finally:
                tree.blockSignals(False)
            if str(exc) != '拡張子の変更を取り消しました':
                self.launcher.error('名前を変更できませんでした: ' + str(exc))

    def go_to_directory(self, path, *, preserve_remote_popup=False):
        """Breadcrumb/edit/favorite navigation stays inside FRB Launch.

        A folder *clicked inside an open Remote context submenu* must update
        Files without transferring Qt focus away from that menu.  All normal
        callers retain the original Files focus behavior.
        """
        import os
        target = normalized_directory(path)
        if not target or not os.path.isdir(target):
            return False
        self._virtual_directory_node = None
        self.path = [directory_row(target)]
        self.refresh_middle()
        if not preserve_remote_popup:
            self.focus_panel(self.middle)
        # A direct breadcrumb/address navigation changes the real keyboard
        # target to Files column 2. Remote navigation only changes the logical
        # target so its popup does not close due to an unrelated setFocus().
        remote = getattr(self.launcher, 'remote_window', None)
        if remote is not None and remote.isVisible():
            if preserve_remote_popup:
                # Explicit Exp row/disclosure navigation is not a RIGHT-arrow
                # handoff. In every Remote placement, retain the human's
                # current logical operating column (Exp or List).
                self.launcher.set_files_operating_target(
                    getattr(self.launcher, '_files_operating_target', 'directory'))
            else:
                self.launcher.remote_focus_area('directory')
        return True

    def select_middle_file(self, filename):
        """Select/scroll the exact file opened from a main-search result.

        Match full Windows paths (case-insensitive), not just filenames:
        similarly named results in other directories must never be selected.
        Selection is UI-only and leaves the folder navigation history alone.
        """
        import ntpath
        def normalized(value):
            return ntpath.normcase(ntpath.normpath(str(value).replace('/', '\\')))

        target = normalized(filename)
        tree = self.middle.tree
        for index in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(index)
            row = self.row_data(item)
            origin, path = resolve_context_target(row, self.launcher.authored_items)
            if origin != 'file' or not path or normalized(path) != target:
                continue
            tree.clearSelection()
            tree.setCurrentItem(item)
            item.setSelected(True)
            tree.scrollToItem(item, QAbstractItemView.ScrollHint.PositionAtCenter)
            self.focus_panel(self.middle)
            return True
        return False

    def middle_back_lane_at(self, point):
        """Legacy viewport helper: the Back lane now lives OUTSIDE the tree."""
        return False

    def middle_blank_back_at(self, point):
        """Only below/between items: real rows remain standard click targets."""
        viewport = self.middle.tree.viewport()
        return (viewport.rect().contains(point) and
                self.middle.tree.itemAt(point) is None)

    def _zone_wheel_source(self, obj):
        """Only freeze wheels in the three-layer navigation zones."""
        if obj in (self.root_widget, self.toolbar_scroller,
                   self.toolbar_scroller.viewport()) or obj in self.root_buttons:
            return True
        if (getattr(self, 'middle', None) is not None and
                obj is self.middle.back):
            return True
        for pane in (getattr(self, 'left', None), getattr(self, 'middle', None),
                     getattr(self, 'right', None)):
            if pane is not None and obj in (pane.tree, pane.tree.viewport()):
                return True
        return False

    def close_transients_for_zone_jump(self):
        """Dismiss temporary overlays before a Wheel Tab leaves its region.

        Keep the displayed directory, rows, breadcrumb, current Page, and
        selection intact.  Only opened cascades and popups are transient.
        This central entry point covers both forward and reverse routes.
        """
        self.cancel_bookmark_hover()
        self.cancel_bookmark_pointer_follow()
        if self.favorite_popup.isVisible():
            self.hide_favorite_popup()
        if self.launcher.history_popup.isVisible():
            self.launcher.hide_history_popup()
        self.launcher.close_cascade_for_main_interaction()
        context_menu = getattr(self.launcher, '_launch_context_menu', None)
        if context_menu is not None and context_menu.isVisible():
            context_menu.close()

    def zone_jump(self, target, position='first'):
        """Move focus and cursor to a zone endpoint; never activate an item.

        Reverse enters at the LAST row/button and forward at the FIRST.
        'current' preserves the selected Page tab on return from layer two.
        Back is a separate focusable header button.
        """
        source = QCursor.pos()
        last = position == 'last'
        # Reject an unavailable destination *before* dismissing the opener.
        if target == 'roots':
            # The authored root button strip was retired. The Page selectors
            # at the left of the workspace bar are the new reachable zone.
            target = 'pages'
        if target == 'back' and (not self.isVisible() or not self.middle.back.isEnabled()):
            return
        if target == 'pages' and not self.launcher.tabs.count():
            return
        self.close_transients_for_zone_jump()
        if target == 'pages':
            buttons = getattr(self, 'workspace_page_buttons', ())
            if buttons and self.isVisible():
                # Hidden header tabs are not a keyboard landing zone anymore.
                (buttons[-1] if last else buttons[0]).setFocus(
                    Qt.FocusReason.TabFocusReason)
            elif self.isVisible():
                # No hidden Page tabs as keyboard destinations in public mode.
                (self.browser_mode_tab if last else self.files_mode_tab).setFocus(
                    Qt.FocusReason.TabFocusReason)
        elif target == 'roots':
            if not self.isVisible() or not self.root_buttons:
                return
            index = len(self.root_buttons) - 1 if last else 0
            self._wheel_root_id = self.root_rows[index].get('item_id')
            for i, button in enumerate(self.root_buttons):
                button.setChecked(i == index)
            self.focus_root(index=index)
        elif target == 'back':
            if not self.isVisible() or not self.middle.back.isEnabled():
                return
            self.middle.back.setFocus(Qt.FocusReason.TabFocusReason)
        else:
            pane = {'files': self.left, 'directory': self.middle,
                    'bookmarks': self.right}.get(target)
            if pane is None or not self.isVisible():
                return
            tree = pane.tree
            if target == 'bookmarks':
                candidates = [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())
                              if self.row_data(tree.topLevelItem(i)) is not None]
                if candidates:
                    tree.setCurrentItem(candidates[-1] if last else candidates[0])
            elif last and tree.topLevelItemCount():
                tree.setCurrentItem(tree.topLevelItem(tree.topLevelItemCount() - 1))
            self.focus_panel(pane)
        QTimer.singleShot(0, lambda dest=target, src=source, end=position:
                          self._finish_zone_jump(dest, src, end))

    def _finish_zone_jump(self, target, source, position='first'):
        if not getattr(getattr(self, 'launcher', None), 'pointer_warp_enabled', True):
            return  # Citrix: focus moved, but the client's cursor must stay put.
        if (QApplication.mouseButtons() != Qt.MouseButton.NoButton or
                QCursor.pos() != source or not self.launcher.isVisible()):
            return
        last = position == 'last'
        if target == 'pages':
            tabs = self.launcher.tabs
            if not tabs.count() or not tabs.isVisible():
                return
            index = tabs.currentIndex() if position == 'current' else (tabs.count() - 1 if last else 0)
            if index < 0:
                return
            destination = tabs.mapToGlobal(tabs.tabRect(index).center())
        elif target == 'roots':
            if not self.isVisible() or not self.root_buttons:
                return
            button = self.root_buttons[-1 if last else 0]
            destination = button.mapToGlobal(button.rect().center())
        elif target == 'back':
            button = self.middle.back
            if not button.isVisible() or not button.isEnabled():
                return
            destination = button.mapToGlobal(button.rect().center())
        else:
            pane = {'files': self.left, 'directory': self.middle,
                    'bookmarks': self.right}.get(target)
            if pane is None or not pane.tree.isVisible():
                return
            tree = pane.tree
            item = tree.currentItem()
            if item is None:
                return
            tree.scrollToItem(item)
            rect = tree.visualItemRect(item)
            if rect.isEmpty():
                return
            viewport = tree.viewport()
            destination = viewport.mapToGlobal(QPoint(
                max(4, min(rect.center().x(), viewport.width() - 12)),
                rect.center().y()))
        if destination != source:
            if target == 'files':
                self._files_warp_global = (destination.x(), destination.y())
            elif target == 'directory':
                self._middle_warp_global = (destination.x(), destination.y())
            elif target == 'bookmarks':
                self._bookmark_warp_global = (destination.x(), destination.y())
            QCursor.setPos(destination)

    def wheel_back_button(self, event):
        """On the Back header, an extra sustained UP wheel enters Files last.

        Back CLICK remains the only way to navigate up a directory.
        """
        if (not self.isVisible() or
                event.modifiers() != Qt.KeyboardModifier.NoModifier or
                QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            self._wheel_back_delta = 0
            self.wheel_zone_navigation.reset('back-up')
            return False
        angle = event.angleDelta().y()
        pixels = event.pixelDelta().y()
        self._wheel_back_delta, movement = wheel_steps(self._wheel_back_delta, angle, pixels)
        if movement:
            if self.wheel_zone_navigation.feed('back-up', movement < 0, abs(movement)):
                self.zone_jump('files', position='last')
        return bool(angle or pixels)

    def add_lane_new_submenu(self, menu, *, target_directory=None):
        """Populate a real Explorer-style New submenu on a supplied menu.

        Used by both the independent right Back lane and the existing blank
        area Paste context menu, so their creation options stay identical.
        """
        from context_menu_icons import context_action_icon
        from launch_appearance import context_menu_spacing_qss, LIGHT_MENU_QSS
        submenu = menu.addMenu('新規作成')
        submenu.setToolTipsVisible(True)
        submenu.setObjectName('expandedNewFileSubmenu')
        submenu.setIcon(context_action_icon('new_category'))
        builtin = (
            ('txt', 'テキスト ドキュメント', '.txt'),
            ('md', 'Markdown 文書', '.md'),
        )
        # Explorer provides Shortcut as a native wizard, not a blank .lnk.
        # Show it for familiarity, but do not create an unusable fake link.
        folder_action = submenu.addAction('フォルダー')
        folder_action.setIcon(self.launcher.file_icons.icon(QFileIconProvider.IconType.Folder))
        folder_action.triggered.connect(lambda checked=False: QTimer.singleShot(
            0, lambda p=target_directory: self.create_from_lane('folder', target_directory=p)))
        shortcut = submenu.addAction('ショートカット')
        shortcut.setIcon(self.launcher.file_icons.icon(QFileInfo('sample.lnk')))
        shortcut.setToolTip('Windowsのショートカット作成ウィザードは未対応です')
        shortcut.setEnabled(False)
        submenu.addSeparator()
        for kind, title, suffix in builtin:
            action = submenu.addAction(title)
            action.setIcon(self.launcher.file_icons.icon(QFileInfo('sample' + suffix)))
            action.triggered.connect(lambda checked=False, k=kind: QTimer.singleShot(
                0, lambda p=target_directory: self.create_from_lane(k, target_directory=p)))
        extras = [entry for entry in discover_shellnew() if entry[0] not in ('.txt', '.md')]
        if extras:
            submenu.addSeparator()
            for extension, label, creation_kind in extras:
                action = submenu.addAction(f'{label} ({extension})')
                action.setIcon(self.launcher.file_icons.icon(QFileInfo('sample' + extension)))
                action.setToolTip(f'Windows登録: ShellNew ({creation_kind})。この形式の作成は未対応です')
                action.setEnabled(False)
        palette = (LIGHT_MENU_QSS if self.launcher.color_theme == 'light' else '') + context_menu_spacing_qss(self.launcher.color_theme)
        submenu.setStyleSheet(palette)
        return submenu

    def show_lane_new_menu(self, global_pos):
        """The right lane and lower blank area MUST offer the same menu.

        Launcher owns the common Paste + New + folder-actions menu, so neither
        location can accidentally omit Paste or diverge in icons/separators.
        """
        return self.launcher.show_expanded_background_paste_menu(global_pos)

    def show_lane_context_menu(self, global_pos):
        """Compatibility alias for the same shared context menu."""
        return self.show_lane_new_menu(global_pos)

    def _clear_lane_new_menu(self):
        self._lane_new_menu = None

    def select_created_middle_item(self, created_path):
        """Select the actual new item instead of a stale first-row fallback."""
        tree = self.middle.tree
        wanted = os.path.normcase(os.path.normpath(str(created_path)))
        for index in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(index)
            row = self.row_data(item)
            if row is None:
                continue
            origin, path = resolve_context_target(row, self.launcher.authored_items)
            if not path or os.path.normcase(os.path.normpath(str(path))) != wanted:
                continue
            key = row_key(row)
            if key:
                self._middle_current_memory = (self.current_directory(), key)
            tree.clearSelection()
            tree.setCurrentItem(item)
            item.setSelected(True)
            tree.scrollToItem(item)
            return item
        return None

    def create_from_lane(self, kind, *, target_directory=None):
        """Explorer behavior: create FIRST, then edit its filename in the grid.

        Escape cancels the rename, NOT the creation.  The freshly created
        folder/file stays on disk (just like Windows Explorer).  Selecting
        another row simply commits/closes the built-in inline editor.
        """
        current = str(target_directory) if target_directory is not None else self.current_directory()
        if not current or not Path(current).is_dir():
            self.launcher.error('作成先フォルダーが見つかりません')
            return
        defaults = {
            'folder': ('新しいフォルダー', ''),
            'txt': ('新しいテキスト ドキュメント', '.txt'),
            'md': ('新しいMarkdown文書', '.md'),
        }
        if kind not in defaults:
            self.launcher.error('未対応の新規作成形式です')
            return
        base, suffix = defaults[kind]
        try:
            # No dialog: create a collision-free real filesystem object.
            name = suggest_name(current, base, suffix)
            created = create_new_item(current, name, kind)
            if kind == 'folder':
                self.launcher.notify_folder_mutation(current)
        except (OSError, ValueError) as exc:
            self.launcher.error('新規作成できませんでした: ' + str(exc))
            return
        # A right-click target may differ from the middle grid's current folder.
        # Do not highlight an unrelated file in that case.
        if self.current_directory() != current:
            self.launcher.footer.setText(f'新規作成しました: {created}（操作対象フォルダー）')
            return
        self.refresh_middle()
        item = self.select_created_middle_item(created)
        if item is not None:
                # Editing is queued until the QMenu is fully dismissed, to
                # avoid Qt.Tool focus loss closing the editor immediately.
                self.begin_context_inline_rename(item)
                self.launcher.footer.setText(f'新規作成しました: {created.name}')
                return
        # Do not leave the user thinking a successful creation was lost.
        self.launcher.error('作成しましたが、一覧で選択できませんでした: ' + created.name)

    def handle_middle_back_double_click(self, obj, event):
        """Double-click blank lower area or invisible right lane = existing Back."""
        if (getattr(self, 'middle', None) is None or not self.isVisible() or
                event.type() not in (QEvent.Type.MouseButtonPress,
                                     QEvent.Type.MouseButtonRelease,
                                     QEvent.Type.MouseButtonDblClick) or
                event.button() != Qt.MouseButton.LeftButton or
                event.modifiers() != Qt.KeyboardModifier.NoModifier):
            return False
        lane = obj is getattr(self, 'middle_back_lane', None)
        in_tree = obj is self.middle.tree.viewport()
        if not (lane or in_tree):
            return False
        if event.type() == QEvent.Type.MouseButtonDblClick:
            if lane or (in_tree and self.middle_blank_back_at(event.position().toPoint())):
                self.go_up()
                event.accept()
                return True
        if lane:
            # This is an independent QWidget, not an editable item cell.
            event.accept()
            return True
        return False

    def set_files_operating_area(self, area):
        """Show the controller's true target on BOTH column titles and rows.

        Updating a logical target is presentation-only: it must never change
        the breadcrumb, folder, currentIndex, or multi-selection.
        """
        if area not in ('files_exp', 'directory', 'files'):
            return
        exp_active = area in ('files_exp', 'files')
        exp = getattr(self, 'embedded_files_exp', None)
        if exp is not None:
            exp.set_operating_active(exp_active)
        title = getattr(self, 'files_list_title_box', None)
        if title is not None and title.property('operatingActive') != (not exp_active):
            title.setProperty('operatingActive', not exp_active)
            title.style().unpolish(title)
            title.style().polish(title)
            title.update()
        # Warm operating surface covers the List's complete title, header,
        # back lane and viewport, not its green current/remembered row state.
        middle_tree = getattr(getattr(self, 'middle', None), 'tree', None)
        for widget in (getattr(self, 'middle_search_bar', None),
                       getattr(self, 'middle_tree_container', None),
                       getattr(self, 'middle_back_lane', None),
                       middle_tree.header() if hasattr(middle_tree, 'header') else None):
            if widget is not None and widget.property('operatingActive') != (not exp_active):
                widget.setProperty('operatingActive', not exp_active)
                widget.style().unpolish(widget)
                widget.style().polish(widget)
                widget.update()
        # The source of truth for the list row is the same logical target.
        # This does not select a new file or move native keyboard focus.
        middle = getattr(self, 'middle', None)
        if middle is not None:
            tree = middle.tree
            inactive = exp_active
            if tree.property('remoteInactive') != inactive:
                tree.setProperty('remoteInactive', inactive)
                tree.style().unpolish(tree)
                tree.style().polish(tree)
            tree.viewport().update()

    def _align_files_list_title_width(self):
        title = getattr(self, 'files_list_title_box', None)
        exp = getattr(self, 'embedded_files_exp', None)
        if title is None or exp is None:
            return
        # Exact peer width: do not tie this to the combined Exp + Remote host,
        # and do not silently shrink it when Launch is temporarily narrow.
        width = max(85, exp.width())
        if title.width() != width:
            title.setFixedWidth(width)

    def _align_embedded_exp_header(self):
        """Keep Exp title strip and Files search bar on one horizontal line."""
        search = getattr(self, 'middle_search_bar', None)
        exp = getattr(self, 'embedded_files_exp', None)
        header = getattr(exp, 'exp_header', None)
        if search is None or header is None:
            return
        height = max(28, search.sizeHint().height())
        if search.isVisible() and search.height() >= height:
            height = search.height()
        if header.height() != height or header.minimumHeight() != height:
            header.setFixedHeight(height)

    def _toolbar_wheel_buttons(self):
        """Left-to-right: Files, Browser, Page1..Page3; no hidden roots."""
        return [button for button in
                (self.files_mode_tab, self.browser_mode_tab,
                 *self.workspace_page_buttons)
                if button is not None and button.isVisible()]

    def wheel_workspace_page_buttons(self, obj, event):
        """Wheel selects one of five; a real click performs the action.

        Selection is separate from activation so wheel cannot unexpectedly
        launch a Page command or change the active Files/Browser workspace.
        """
        buttons = self._toolbar_wheel_buttons()
        if (obj not in buttons or
                event.modifiers() != Qt.KeyboardModifier.NoModifier):
            return False
        angle = event.angleDelta().y()
        pixel = event.pixelDelta().y()
        delta = angle if angle else pixel * 3
        if not delta:
            return False
        self._toolbar_wheel_remainder += delta
        steps = abs(self._toolbar_wheel_remainder) // 120
        if not steps:
            return True
        direction = -1 if self._toolbar_wheel_remainder > 0 else 1
        self._toolbar_wheel_remainder -= (1 if self._toolbar_wheel_remainder > 0
                                          else -1) * steps * 120
        current = self._toolbar_wheel_current
        index = buttons.index(current) if current in buttons else buttons.index(obj)
        target = max(0, min(len(buttons) - 1, index + direction * steps))
        selected = buttons[target]
        self._toolbar_wheel_current = selected
        selected.setFocus(Qt.FocusReason.OtherFocusReason)
        # Queue cursor-follow until the tab geometry settles. Do not simulate
        # a click or move the cursor if pointer warp has been disabled.
        if getattr(self.launcher, 'pointer_warp_enabled', True):
            QTimer.singleShot(0, lambda b=selected: self._follow_toolbar_wheel(b))
        return True

    def _follow_toolbar_wheel(self, button):
        if (button is not self._toolbar_wheel_current or
                not button.isVisible() or not self.isVisible() or
                not getattr(self.launcher, 'pointer_warp_enabled', True) or
                QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return
        buttons = self._toolbar_wheel_buttons()
        if button not in buttons:
            return
        pointer = QCursor.pos()
        # Only warp if the pointer is still in the five-button toolbar.
        rect = self.root_widget.rect()
        if not rect.contains(self.root_widget.mapFromGlobal(pointer)):
            return
        destination = button.mapToGlobal(QPoint(button.width() // 2,
                                                button.height() // 2))
        if destination != pointer:
            QCursor.setPos(destination)

    def eventFilter(self, obj, event):
        # The application-wide filter also receives clicks in the blank 1.5
        # lane, which Qt's inline editor does not see while kana holds focus.
        self._dismiss_middle_rename_on_outside_click(obj, event)
        self._restore_middle_rename_triggers_on_release(event)
        # Stop a wheel-armed shuriken BEFORE a normal Files List click or
        # right-click menu is dispatched. Never swallow the actual click.
        if (getattr(self, 'middle', None) is not None
                and obj is self.middle.tree.viewport()
                and event.type() == QEvent.Type.MouseButtonPress
                and event.button() in (Qt.MouseButton.LeftButton,
                                       Qt.MouseButton.RightButton)):
            self.launcher.stop_auto_shuriken_on_list_click()
        self._dismiss_middle_search_history_on_outside_click(obj, event)
        if (getattr(self, 'middle', None) is not None
                and obj is self.middle.tree.viewport()
                and event.type() == QEvent.Type.Resize):
            self._position_middle_empty_label()
            self._position_middle_parent_return_hint()
        if (obj is getattr(self, 'remote_15_lane', None) and
                event.type() in (QEvent.Type.Resize, QEvent.Type.Move,
                                 QEvent.Type.Show)):
            # Defer to the settled splitter geometry (Qt can issue several
            # intermediate events while restoring widths).
            self.launcher.queue_remote_15_alignment()
        if (obj is getattr(self, 'middle_search_bar', None) and
                event.type() == QEvent.Type.Resize):
            self._align_embedded_exp_header()
            self._align_files_list_title_width()
        if (obj is getattr(self, 'left', None) and
                event.type() == QEvent.Type.Resize):
            self._align_files_list_title_width()
        if (self.isVisible() and self._workspace_mode == 'files'
                and event.type() == QEvent.Type.Wheel
                and obj in (self.middle.tree.viewport(),
                            self.middle.tree.verticalScrollBar())):
            self._sync_remote_area_after_mouse_press('directory')
        if (event.type() == QEvent.Type.Wheel and self.isVisible() and
                self.wheel_workspace_page_buttons(obj, event)):
            event.accept()
            return True
        if (event.type() == QEvent.Type.Wheel and self.isVisible() and
                self._zone_wheel_source(obj) and
                self.wheel_zone_navigation.wheel_is_locked()):
            event.accept()
            return True  # Ignore momentum across an inter-area warp.
        if (event.type() == QEvent.Type.Wheel and self.isVisible() and
                obj is getattr(getattr(self, 'middle', None), 'back', None) and
                self.wheel_back_button(event)):
            event.accept()
            return True
        if (event.type() == QEvent.Type.Wheel and self.isVisible() and
                self.wheel_directory_favorite_history(obj, event)):
            event.accept()
            return True
        if (obj is getattr(self, 'middle_back_lane', None) and
                event.type() == QEvent.Type.ContextMenu):
            self.show_lane_new_menu(event.globalPos())
            event.accept()
            return True
        if self.handle_middle_back_double_click(obj, event):
            return True
        if (getattr(self, 'left', None) is not None and
                obj is self.left.tree.viewport() and
                event.type() == QEvent.Type.MouseMove and
                self._files_warp_global is not None):
            position = event.globalPosition().toPoint()
            warp = self._files_warp_global
            self._files_warp_global = None
            if is_warp_generated_mouse_move((position.x(), position.y()), warp):
                event.accept()
                return True
        if (getattr(self, 'left', None) is not None and
                obj is self.left.tree.viewport() and
                event.type() == QEvent.Type.MouseMove):
            self._files_edge_follow_active = False
        if (getattr(self, 'middle', None) is not None and
                obj is self.middle.tree.viewport() and
                event.type() == QEvent.Type.MouseMove and
                self._middle_warp_global is not None):
            position = event.globalPosition().toPoint()
            warp = self._middle_warp_global
            self._middle_warp_global = None
            if is_warp_generated_mouse_move((position.x(), position.y()), warp):
                event.accept()
                return True
        if (getattr(self, 'right', None) is not None and
                obj is self.right.tree.viewport() and
                event.type() == QEvent.Type.MouseMove and
                self._bookmark_warp_global is not None):
            position = event.globalPosition().toPoint()
            warp = self._bookmark_warp_global
            # QCursor.setPos() can generate a synthetic Qt mouse-move event.
            # Do not mistake that for an intentional user hover operation.
            self._bookmark_warp_global = None
            if is_warp_generated_mouse_move((position.x(), position.y()), warp):
                event.accept()
                return True
        if (getattr(self, 'middle', None) is not None
                and obj is self.middle.tree.viewport()
                and event.type() == QEvent.Type.MouseMove
                and self._middle_vdi_anchor_pos is not None
                and not getattr(self.launcher, 'pointer_warp_enabled', True)):
            # A genuine mouse move chooses a new physical anchor. Ignore
            # synthetic/hover notifications at the unchanged screen position.
            position = event.globalPosition().toPoint()
            if position != self._middle_vdi_anchor_pos:
                self._middle_vdi_anchor_pos = None
        if (getattr(self, 'right', None) is not None
                and obj is self.right.tree.viewport()
                and event.type() == QEvent.Type.MouseMove):
            self._bookmark_edge_follow_active = False
        # Combo-like behavior: dismiss favorites on an unrelated click, but
        # don't consume the click or interfere with file/keyboard actions.
        if (hasattr(self, 'favorite_popup') and self.favorite_popup.isVisible()
                and event.type() == QEvent.Type.MouseButtonPress
                and isinstance(obj, QWidget) and obj.window() is self.launcher
                and obj is not self.favorite_dropdown
                and not self.favorite_dropdown.isAncestorOf(obj)
                and obj is not self.favorite_popup
                and not self.favorite_popup.isAncestorOf(obj)):
            self.hide_favorite_popup()
        if (hasattr(self, 'favorite_choices') and self.favorite_popup.isVisible()
                and obj in (self.favorite_choices, self.favorite_choices.viewport())
                and event.type() == QEvent.Type.KeyPress):
            if event.key() == Qt.Key.Key_Escape:
                self.hide_favorite_popup()
                self.focus_panel(self.middle)
                return True
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Right):
                row = self.favorite_choices.currentItem()
                if row:
                    self.directory_favorite_clicked(row, 0)
                return True
            if event.key() == Qt.Key.Key_Delete:
                row = self.favorite_choices.currentItem()
                if row:
                    self.directory_favorite_clicked(row, 1)
                return True
        if (event.type() == QEvent.Type.Wheel and self.isVisible()
                and obj in (self.left.tree, self.left.tree.viewport())
                and not self._files_first_wan_enabled):
            if self.wheel_files_first_column(event):
                event.accept()
                return True
        if (event.type() == QEvent.Type.Wheel and self.isVisible()
                and obj in (self.right.tree, self.right.tree.viewport())
                and not getattr(self.launcher, 'bookmark_wan_enabled', True)):
            if self.wheel_bookmarks_first_level(event):
                event.accept()
                return True
        if (self.isVisible() and any(b.isVisible() for b in self.root_buttons)
                and obj in (self.root_widget, self.toolbar_scroller.viewport(),
                            self.toolbar_scroller)
                and event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton):
            # The second-level toolbar is mostly empty when it has just a
            # few buttons. A click on that *blank* region focuses the first
            # button, not an arbitrary previous button or its cascade.
            # Actual button clicks are delivered to the QPushButtons above.
            self.launcher.close_cascade_for_main_interaction()
            self._wheel_root_id = self.root_rows[0].get('item_id')
            for index, button in enumerate(self.root_buttons):
                button.setChecked(index == 0)
            self.focus_root(index=0)
            event.accept()
            return True
        if (event.type() == QEvent.Type.Wheel and self.isVisible()
                and any(b.isVisible() for b in self.root_buttons)
                and (obj in self.root_buttons or
                     obj in (self.root_widget, self.toolbar_scroller,
                             self.toolbar_scroller.viewport()))):
            if self.wheel_first_level(event, obj):
                event.accept()
                return True
        return super().eventFilter(obj, event)

    def wheel_middle_fast_hybrid(self, event):
        """Files List: Remoteのノッチ応答 + スクロール優先 + 旧WANの端追従。

        スクロール中は正式な currentItem を変更しない。「相手が
        ポインターの下へ来る」状態を維持する。スクロールできなくなった
        入力だけ既存の wheel_middle_at_edge に渡し、従来どおり
        ホバー行を起点に追従する（フォルダーを勝手に開かない）。
        """
        shuriken_trace = globals().get('shuriken_trace', lambda *a, **kw: None)
        shuriken_bar_state = globals().get('shuriken_bar_state', lambda *a, **kw: {})
        if (not self.isVisible() or self._workspace_mode != 'files'
                or event.modifiers() != Qt.KeyboardModifier.NoModifier
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton
                or self.middle.tree.state() == QAbstractItemView.State.EditingState):
            shuriken_trace('list_wheel_skip', reason='view_modifier_button_or_edit',
                           view_visible=self.isVisible(), workspace=self._workspace_mode)
            return False
        tree = self.middle.tree
        if not tree.topLevelItemCount():
            shuriken_trace('list_wheel_skip', reason='empty_list')
            return False
        angle, pixels = event.angleDelta().y(), event.pixelDelta().y()
        if not angle and not pixels:
            shuriken_trace('list_wheel_skip', reason='zero_delta')
            return False
        (self._middle_parity_angle_remainder,
         self._middle_parity_pixel_remainder,
         steps) = consume_remote_like_wheel(
            self._middle_parity_angle_remainder,
            self._middle_parity_pixel_remainder, angle, pixels)
        shuriken_trace('list_wheel', angle=angle, pixels=pixels, steps=steps,
                       pointer_warp=getattr(getattr(self, 'launcher', None), 'pointer_warp_enabled', None),
                       **shuriken_bar_state(tree.verticalScrollBar(),
                                           row_count=tree.topLevelItemCount()))
        if not steps:
            return True  # 高精度ホイールの端数は保留（Qtへ二重送信しない）。

        # Shuriken owns its activation and flight input; the ordinary
        # scrollbar-first hybrid is untouched until a fast gesture arms it.
        auto_handler = getattr(getattr(self, 'launcher', None), 'shuriken_wheel_list_input', None)
        if callable(auto_handler) and auto_handler(steps, source='list'):
            shuriken_trace('list_wheel_owned_by_flight', steps=steps)
            return True

        bar = tree.verticalScrollBar()
        before = bar.value()
        per_notch = (LIST_WHEEL_SCROLL_PIXELS_PER_NOTCH
                     or max(1, bar.singleStep()))
        after, remaining = plan_hybrid_scroll(
            before, bar.minimum(), bar.maximum(), steps, per_notch)
        shuriken_trace('list_wheel_hybrid', steps=steps, from_pos=before,
                       target_pos=after, remaining=remaining, per_notch=per_notch)
        if after != before:
            bar.setValue(after)  # 1イベント1回のみ。currentItemを変えない。
            # 旧WANの「実際にスクロールした場合」の後処理をそのまま利用。
            self.wheel_middle_at_edge(event, before, bar.value())
        if remaining:
            # 旧WANの「スクロールできない端でだけ追従」を再利用する。
            # 同一イベントで端に到達しても、残ったノッチ分を引き継ぐ。
            # 既存処理の符号は +下 / -上、Remoteノッチは +上 / -下。
            at = bar.value()
            self.wheel_middle_at_edge(event, at, at, movement_override=-remaining)
        return True

    def wheel_middle_like_remote_button(self, event):
        """Experimental Files List wheel: follow Remote ぐりぐり current steps.

        This deliberately bypasses *native* List scrolling while the mode is
        enabled, to compare the two input paths at the same one-row-per-notch
        semantics. The original scroll-then-follow hybrid is the OFF fallback.
        Other panes, popup context menus, and the Remote wheel are untouched.
        """
        if (not self.isVisible() or self._workspace_mode != 'files'
                or event.modifiers() != Qt.KeyboardModifier.NoModifier
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton
                or self.middle.tree.state() == QAbstractItemView.State.EditingState):
            return False  # Preserve Qt's normal modifiers/editors.
        tree = self.middle.tree
        if not tree.topLevelItemCount():
            return False
        angle, pixels = event.angleDelta().y(), event.pixelDelta().y()
        if not angle and not pixels:
            return False
        (self._middle_parity_angle_remainder,
         self._middle_parity_pixel_remainder,
         steps) = consume_remote_like_wheel(
            self._middle_parity_angle_remainder,
            self._middle_parity_pixel_remainder, angle, pixels)
        if not steps:
            return True  # A high-resolution partial notch: do not native-scroll.

        # Same direct row-selection helper as Launcher.remote_command for List.
        # Do not go via remote_command: it may be owned by a popup/menu instead.
        self.ensure_middle_current_selection()
        item = None
        for _ in range(abs(steps)):
            item = move_tree_selection(tree, -1 if steps > 0 else 1)
        if item is None:
            return True
        # Direct mouse-wheel use, unlike Remote pad navigation, can follow the
        # selected row with the pointer. The existing coalesced follower guards
        # against stale targets, mouse buttons and pointer movement elsewhere.
        tree.setFocus(Qt.FocusReason.MouseFocusReason)
        if getattr(self.launcher, 'pointer_warp_enabled', True):
            self._middle_follow_pending = item
            if not self._middle_follow_scheduled:
                self._middle_follow_scheduled = True
                QTimer.singleShot(0, self.follow_middle_pointer)
        return True

    def wheel_middle_at_edge(self, event, scroll_before, scroll_after,
                             movement_override=None):
        """WAN fallback: native scroll first, cursor-follow at a real edge.

        No click, folder preview/expansion, activation, or file operations.
        Keep Ctrl/Shift wheel and active inline editors unchanged.
        """
        hold = getattr(self, '_middle_back_hold', None)
        if (not self.isVisible() or
                event.modifiers() != Qt.KeyboardModifier.NoModifier or
                QApplication.mouseButtons() != Qt.MouseButton.NoButton or
                self.middle.tree.state() == QAbstractItemView.State.EditingState):
            self._wheel_middle_delta = 0
            if hold is not None:
                hold.reset()
            return False
        tree = self.middle.tree
        if not tree.topLevelItemCount():
            self._wheel_middle_delta = 0
            if hold is not None:
                hold.reset()
            return False
        # Any real scroll is Target Flow: keep the OS cursor where it is.
        if scroll_before != scroll_after:
            self._middle_vdi_anchor_pos = None
            getattr(self, 'wheel_zone_navigation', None) and self.wheel_zone_navigation.reset('directory-last')
            getattr(self, 'wheel_zone_navigation', None) and self.wheel_zone_navigation.reset('directory-first')
            self._wheel_middle_delta = 0
            self._middle_follow_pending = None
            if hold is not None:
                hold.reset()
            return False
        angle = event.angleDelta().y()
        pixels = event.pixelDelta().y()
        if movement_override is None:
            pending, movement = wheel_steps(self._wheel_middle_delta, angle, pixels)
            self._wheel_middle_delta = pending
        else:
            # Fast hybrid already converted the physical wheel to Remote
            # notches. Do not count those notches again in the old WAN.
            self._wheel_middle_delta = 0
            movement = movement_override
        if not movement:
            return bool(angle or pixels)  # Incomplete high-res wheel step.
        scrollbar = tree.verticalScrollBar()
        if not can_follow_at_edge(scroll_before, scroll_after,
                                  scrollbar.minimum(), scrollbar.maximum(), movement):
            self._wheel_middle_delta = 0
            if hold is not None:
                hold.reset()
            return False
        viewport = tree.viewport()
        cursor_local = viewport.mapFromGlobal(QCursor.pos())
        if not viewport.rect().contains(cursor_local):
            if hold is not None:
                hold.reset()
            return False
        # Normally the cursor's hovered item anchors the first edge step.
        # With pointer-warp OFF, however, Qt can scroll the viewport again
        # while selecting a row; a later wheel event sees the same physical
        # pointer over an *earlier* item. Restarting from that hover made a
        # down-wheel selection run UP 5-6 rows, over and over. Guard the
        # requested navigation direction even if a scroll/reset invalidates
        # the previous VDI anchor. This doesn't touch the fast scrollbar or
        # the autonomous shuriken animation at all.
        hovered = tree.itemAt(cursor_local)
        cursor_global = QCursor.pos()
        pointer_off = not getattr(getattr(self, 'launcher', None), 'pointer_warp_enabled', True)
        selected = tree.currentItem()
        if pointer_off:
            current_index = (tree.indexOfTopLevelItem(selected)
                             if selected is not None else None)
            hover_index = (tree.indexOfTopLevelItem(hovered)
                           if hovered is not None else None)
            # Keep the 1-row precision once an edge-follow run has started.
            # If Qt resets the anchor while moving the scrollbar, fall back
            # to a directional guard rather than the older hovered row.
            if (getattr(self, '_middle_vdi_anchor_pos', None) == cursor_global
                    and current_index is not None and current_index >= 0):
                index = current_index
            else:
                index = monotonic_edge_anchor(current_index, hover_index, movement)
            if index is None:
                return True
        else:
            current = hovered if hovered is not None else selected
            if current is None:
                return True
            index = tree.indexOfTopLevelItem(current)
            if index < 0:
                return True
        target = root_wheel_target(index, movement, tree.topLevelItemCount())
        # Count only extra upward input AFTER the first row has become current.
        # The last wheel event used to *reach* row 0 is never counted.
        at_first = (index == 0 and movement < 0 and
                    tree.currentItem() is tree.topLevelItem(0) and
                    cursor_local.y() >= 0)
        legacy_hold_fired = False
        if hold is not None and hold.feed(at_first, abs(movement)):
            legacy_hold_fired = True
        navigator = getattr(self, 'wheel_zone_navigation', None)
        if (navigator is not None and
                navigator.feed('directory-first', at_first, abs(movement))):
            self.zone_jump('back')
            return True
        if navigator is None and legacy_hold_fired:
            self.schedule_middle_back_pointer(cursor_global=QCursor.pos())
            return True
        at_last = (index == tree.topLevelItemCount() - 1 and movement > 0
                   and tree.currentItem() is tree.topLevelItem(index))
        if (getattr(self, 'wheel_zone_navigation', None) is not None and
                self.wheel_zone_navigation.feed('directory-last', at_last, abs(movement))):
            self.zone_jump('bookmarks')
            return True
        if target is None or target == index:
            return True  # Stop at first/last file; no wrap and no warp.
        item = tree.topLevelItem(target)
        # A wheel step is navigation, not a filesystem operation.  Do not
        # invoke choose_middle(), activate_row(), or itemClicked handlers.
        # Wheel navigation should visibly mark the current row. Preserve an
        # existing Ctrl/Shift multi-selection rather than silently discarding
        # the user's file selection while browsing.
        preserve_multi = len(tree.selectedItems()) > 1
        if not preserve_multi:
            tree.clearSelection()
        tree.setCurrentItem(item)
        if not preserve_multi:
            item.setSelected(True)
        tree.setFocus(Qt.FocusReason.MouseFocusReason)
        if not getattr(getattr(self, 'launcher', None), 'pointer_warp_enabled', True):
            self._middle_vdi_anchor_pos = cursor_global
            return True
        self._middle_follow_pending = item
        if not self._middle_follow_scheduled:
            self._middle_follow_scheduled = True
            QTimer.singleShot(0, self.follow_middle_pointer)
        return True

    def follow_middle_pointer(self):
        """Move vertically onto the newly current visible file row."""
        self._middle_follow_scheduled = False
        if not getattr(getattr(self, 'launcher', None), 'pointer_warp_enabled', True):
            self._middle_follow_pending = None
            return
        item = self._middle_follow_pending
        self._middle_follow_pending = None
        tree = self.middle.tree
        if (item is None or not self.isVisible() or not tree.isVisible()
                or tree.currentItem() is not item
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return
        viewport = tree.viewport()
        position = QCursor.pos()
        local = viewport.mapFromGlobal(position)
        if not viewport.rect().contains(local):
            return  # User has already moved elsewhere.
        bounds = tree.visualItemRect(item)
        target = cursor_target((viewport.width(), viewport.height()),
                               (bounds.left(), bounds.top(), bounds.width(), bounds.height()),
                               local.x())
        if target is None:
            return
        destination = viewport.mapToGlobal(QPoint(*target))
        if destination == position:
            return
        self._middle_warp_global = (destination.x(), destination.y())
        QCursor.setPos(destination)

    def schedule_middle_back_pointer(self, cursor_global):
        # Warp to Back without clicking, only if the pointer has not moved.
        self._middle_back_warp_pending = cursor_global
        QTimer.singleShot(0, self.follow_middle_back_pointer)

    def follow_middle_back_pointer(self):
        original = self._middle_back_warp_pending
        self._middle_back_warp_pending = None
        if not getattr(getattr(self, 'launcher', None), 'pointer_warp_enabled', True):
            return
        if (original is None or not self.isVisible()
                or not self.middle.back.isVisible() or not self.middle.back.isEnabled()
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton
                or QCursor.pos() != original):
            return
        viewport = self.middle.tree.viewport()
        if not viewport.rect().contains(viewport.mapFromGlobal(original)):
            return
        button = self.middle.back
        destination = button.mapToGlobal(button.rect().center())
        if destination != original:
            QCursor.setPos(destination)  # Never synthesize a click or Back action.

    def sync_first_files_hover_from_cursor(self):
        """In Target Flow, preview the folder that came beneath the cursor."""
        self._files_scroll_hover_scheduled = False
        if not self.isVisible():
            return
        tree = self.left.tree
        viewport = tree.viewport()
        position = viewport.mapFromGlobal(QCursor.pos())
        if not viewport.rect().contains(position):
            return
        item = tree.itemAt(position)
        if item is not None and item is not tree.currentItem():
            tree.setCurrentItem(item)
            self.choose_files(item, 0)  # Preview, never launch or activate.

    def wheel_files_at_edge(self, event, scroll_before, scroll_after):
        """Files first column: Target Flow if scrollbar moves, else Follow.

        Folder preview is kept, but an actual command is never executed by
        the wheel. The middle pane, clicks and drag operations are unchanged.
        """
        if (not self.isVisible()
                or event.modifiers() != Qt.KeyboardModifier.NoModifier
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            self._wheel_files_delta = 0
            return False
        tree = self.left.tree
        if not tree.topLevelItemCount():
            self._wheel_files_delta = 0
            return False
        if scroll_before != scroll_after:
            getattr(self, 'wheel_zone_navigation', None) and self.wheel_zone_navigation.reset('files-last')
            getattr(self, 'wheel_zone_navigation', None) and self.wheel_zone_navigation.reset('files-first')
            self._files_edge_follow_active = False
            self._wheel_files_delta = 0
            self._files_follow_pending = None
            if not self._files_scroll_hover_scheduled:
                self._files_scroll_hover_scheduled = True
                QTimer.singleShot(0, self.sync_first_files_hover_from_cursor)
            return False
        pending, movement = wheel_steps(
            self._wheel_files_delta, event.angleDelta().y(), event.pixelDelta().y())
        self._wheel_files_delta = pending
        if not movement:
            return bool(event.angleDelta().y() or event.pixelDelta().y())
        scrollbar = tree.verticalScrollBar()
        if not can_follow_at_edge(scroll_before, scroll_after,
                                  scrollbar.minimum(), scrollbar.maximum(), movement):
            self._wheel_files_delta = 0
            return False
        viewport = tree.viewport()
        position = viewport.mapFromGlobal(QCursor.pos())
        if not viewport.rect().contains(position):
            return False
        hovered = tree.itemAt(position)
        current = (tree.currentItem() if self._files_edge_follow_active
                   else hovered or tree.currentItem())
        index = tree.indexOfTopLevelItem(current) if current is not None else -1
        if index < 0:
            return True
        target = root_wheel_target(index, movement, tree.topLevelItemCount())
        at_first = (index == 0 and movement < 0 and
                    tree.currentItem() is tree.topLevelItem(0))
        if (getattr(self, 'wheel_zone_navigation', None) is not None and
                self.wheel_zone_navigation.feed('files-first', at_first, abs(movement))):
            self.zone_jump('roots', position='last')
            return True
        at_last = (index == tree.topLevelItemCount() - 1 and movement > 0
                   and tree.currentItem() is tree.topLevelItem(index))
        if (getattr(self, 'wheel_zone_navigation', None) is not None and
                self.wheel_zone_navigation.feed('files-last', at_last, abs(movement))):
            self.zone_jump('directory')
            return True
        if target is None or target == index:
            return True
        item = tree.topLevelItem(target)
        tree.setCurrentItem(item)
        tree.scrollToItem(item)
        tree.setFocus(Qt.FocusReason.MouseFocusReason)
        self._files_edge_follow_active = True
        self.choose_files(item, 0)  # Existing preview only.
        self._files_follow_pending = item
        if not self._files_follow_scheduled:
            self._files_follow_scheduled = True
            QTimer.singleShot(0, self.follow_first_files_pointer)
        return True

    def follow_first_files_pointer(self):
        """Keep the pointer on the previewed Files root at the scroll edge."""
        self._files_follow_scheduled = False
        if not getattr(getattr(self, 'launcher', None), 'pointer_warp_enabled', True):
            self._files_follow_pending = None
            return
        item = self._files_follow_pending
        self._files_follow_pending = None
        tree = self.left.tree
        if (item is None or not self.isVisible() or not tree.isVisible()
                or tree.currentItem() is not item
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return
        viewport = tree.viewport()
        position = QCursor.pos()
        local = viewport.mapFromGlobal(position)
        if not viewport.rect().contains(local):
            return
        bounds = tree.visualItemRect(item)
        target = cursor_target((viewport.width(), viewport.height()),
                               (bounds.left(), bounds.top(), bounds.width(), bounds.height()),
                               local.x())
        if target is None:
            return
        destination = viewport.mapToGlobal(QPoint(*target))
        if destination != position:
            self._files_warp_global = (destination.x(), destination.y())
            QCursor.setPos(destination)

    def wheel_files_first_column(self, event):
        """Browse first-column folders by wheel without scrolling other panes.

        Reuse choose_files(), the same preview as a click/Up/Down key.  This
        never calls execute()/activate(), even for an authored command row.
        """
        tree = self.left.tree
        count = tree.topLevelItemCount()
        if not count or event.modifiers() != Qt.KeyboardModifier.NoModifier:
            return False
        angle = event.angleDelta().y()
        delta = angle if angle else event.pixelDelta().y() * 3
        if not delta:
            return False
        self._wheel_files_delta += delta
        steps = int(abs(self._wheel_files_delta) // 120)
        if not steps:
            return True  # Precision touchpad: wait for one complete step.
        direction = -1 if self._wheel_files_delta > 0 else 1
        self._wheel_files_delta -= (1 if self._wheel_files_delta > 0 else -1) * steps * 120
        current = tree.currentItem()
        index = tree.indexOfTopLevelItem(current) if current is not None else -1
        if index < 0:
            index = 0
        target = root_wheel_target(index, direction * steps, count)
        if target is None or target == index:
            return True  # Stop at the ends; never scroll the folder list.
        item = tree.topLevelItem(target)
        tree.setCurrentItem(item)
        tree.scrollToItem(item)  # Keep the current row visible in long lists.
        tree.setFocus(Qt.FocusReason.MouseFocusReason)
        row = self.row_data(item)
        if row and row.get('item_kind') in ('category', 'directory'):
            self.choose_files(item, 0)
        return True

    def set_bookmark_wan(self, enabled):
        """Swap Bookmarks between native-scroll WAN and the legacy Follow mode."""
        self._wheel_bookmark_delta = 0
        self._bookmark_edge_follow_active = False
        self.cancel_bookmark_pointer_follow()
        self.cancel_bookmark_hover()
        self.right.tree.adaptive_wheel_callback = (
            self.wheel_bookmarks_at_edge if enabled else None)

    def cancel_bookmark_hover(self):
        self._bookmark_hover_item = None
        self._bookmark_hover_timer.stop()

    def hover_bookmark_first_level(self, item, _column):
        """True mouse hover also previews folders, without executing links."""
        if (not getattr(self.launcher, 'bookmark_wan_enabled', True)
                or getattr(self.launcher, 'folder_open_mode', 'single') == 'double'
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return
        # A genuinely new hover target takes priority over an edge-follow
        # sequence (synthesized pointer moves are filtered upstream).
        self._bookmark_edge_follow_active = False
        self.request_bookmark_hover(item)

    def request_bookmark_hover(self, item):
        """Keep the current row at the cursor; debounce cascade expansion.

        Normal scroll moves the *content* beneath the pointer, so itemEntered
        is not always emitted. Both wheel and mouse hover call this function.
        """
        tree = self.right.tree
        if (item is None or tree.indexOfTopLevelItem(item) < 0
                or self.row_data(item) is None):
            self.cancel_bookmark_hover()
            self.launcher.close_cascade_for_main_interaction()
            return
        if tree.currentItem() is not item:
            tree.setCurrentItem(item)
        if self._bookmark_hover_item is item and self._bookmark_hover_timer.isActive():
            return
        self._bookmark_hover_item = item
        # Rapid wheel movement should not open a cascade for every row that
        # briefly passes under the stationary cursor.
        self._bookmark_hover_timer.start(230)

    def open_bookmark_hover(self):
        """Preview the settled hovered folder to the right; links stay inert."""
        item = self._bookmark_hover_item
        self._bookmark_hover_item = None
        if (item is None or not self.isVisible()
                or getattr(self.launcher, 'folder_open_mode', 'single') == 'double'
                or not getattr(self.launcher, 'bookmark_wan_enabled', True)):
            return
        tree = self.right.tree
        viewport = tree.viewport()
        pos = viewport.mapFromGlobal(QCursor.pos())
        if (not viewport.rect().contains(pos) or tree.itemAt(pos) is not item
                or tree.indexOfTopLevelItem(item) < 0):
            return
        row = self.row_data(item)
        if row and row.get('item_kind') in ('category', 'directory'):
            menu = getattr(self.launcher, 'menu', None)
            if (menu is None or not menu.isVisible()
                    or getattr(menu, 'return_focus_item', None) is not item):
                self.choose_bookmark(item, 0)  # Preview only, never execute.
        else:
            self.launcher.close_cascade_for_main_interaction()

    def sync_bookmark_hover_from_cursor(self):
        """Update hover after Qt has applied native scrollbar movement."""
        self._bookmark_scroll_hover_scheduled = False
        if (not self.isVisible()
                or not getattr(self.launcher, 'bookmark_wan_enabled', True)):
            return
        tree = self.right.tree
        viewport = tree.viewport()
        pos = viewport.mapFromGlobal(QCursor.pos())
        if viewport.rect().contains(pos):
            self.request_bookmark_hover(tree.itemAt(pos))

    def wheel_bookmarks_at_edge(self, event, scroll_before, scroll_after):
        """WAN: native Bookmarks scroll first; follow only at a real edge.

        Do not activate URLs or automatically expand directories per notch.
        Folder previews are ordinary (debounced) hover behavior instead.
        """
        if (not self.isVisible()
                or event.modifiers() != Qt.KeyboardModifier.NoModifier
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            self._wheel_bookmark_delta = 0
            return False
        tree = self.right.tree
        if not tree.topLevelItemCount():
            self._wheel_bookmark_delta = 0
            return False
        if scroll_before != scroll_after:
            getattr(self, 'wheel_zone_navigation', None) and self.wheel_zone_navigation.reset('bookmarks-last')
            getattr(self, 'wheel_zone_navigation', None) and self.wheel_zone_navigation.reset('bookmarks-first')
            self._bookmark_edge_follow_active = False
            # Target Flow: content flows beneath a stationary pointer. Hover
            # after the native scroll, not at the pre-scroll item position.
            self._wheel_bookmark_delta = 0
            self.cancel_bookmark_pointer_follow()
            if not self._bookmark_scroll_hover_scheduled:
                self._bookmark_scroll_hover_scheduled = True
                QTimer.singleShot(0, self.sync_bookmark_hover_from_cursor)
            return False
        pending, movement = wheel_steps(
            self._wheel_bookmark_delta, event.angleDelta().y(), event.pixelDelta().y())
        self._wheel_bookmark_delta = pending
        if not movement:
            return bool(event.angleDelta().y() or event.pixelDelta().y())
        scrollbar = tree.verticalScrollBar()
        if not can_follow_at_edge(scroll_before, scroll_after,
                                  scrollbar.minimum(), scrollbar.maximum(), movement):
            self._wheel_bookmark_delta = 0
            return False
        viewport = tree.viewport()
        pos = viewport.mapFromGlobal(QCursor.pos())
        if not viewport.rect().contains(pos):
            return False
        hovered = tree.itemAt(pos)
        if hovered is not None and self.row_data(hovered) is None:
            hovered = None  # Section headings must never drive navigation.
        # After the first edge step, keep navigating the current row even
        # when Follow was switched OFF or a deferred pointer warp is pending.
        # Otherwise consecutive notches would repeatedly target one row.
        current = (tree.currentItem() if self._bookmark_edge_follow_active
                   else hovered or tree.currentItem())
        index = tree.indexOfTopLevelItem(current) if current is not None else -1
        if index < 0:
            return True
        indices = [i for i in range(tree.topLevelItemCount())
                   if self.row_data(tree.topLevelItem(i)) is not None]
        if not indices:
            return True
        position = indices.index(index) if index in indices else 0
        target = indices[root_wheel_target(position, movement, len(indices))]
        at_first = (index == indices[0] and movement < 0 and
                    tree.currentItem() is tree.topLevelItem(indices[0]))
        if (getattr(self, 'wheel_zone_navigation', None) is not None and
                self.wheel_zone_navigation.feed('bookmarks-first', at_first, abs(movement))):
            self.zone_jump('directory', position='last')
            return True
        at_last = (index == indices[-1] and movement > 0
                   and tree.currentItem() is tree.topLevelItem(index))
        if (getattr(self, 'wheel_zone_navigation', None) is not None and
                self.wheel_zone_navigation.feed('bookmarks-last', at_last, abs(movement))):
            self.zone_jump('pages')
            return True
        if target is None or target == index:
            return True
        item = tree.topLevelItem(target)
        tree.setCurrentItem(item)
        tree.setFocus(Qt.FocusReason.MouseFocusReason)
        self._bookmark_edge_follow_active = True
        self.request_bookmark_hover(item)
        if getattr(self.launcher, 'bookmark_pointer_follow', False):
            self.schedule_bookmark_pointer_follow(item)
        return True

    def wheel_bookmarks_first_level(self, event):
        """Wheel through top-level bookmarks; scrollbar drag stays available.

        This right-hand QTreeWidget contains *only* first-level rows.  Child
        categories open in separate existing cascade columns, whose native
        scrolling is unaffected.  One 120-unit notch moves one item; tiny
        precision touchpad deltas accumulate.  No URL or command is run.
        """
        tree = self.right.tree
        count = tree.topLevelItemCount()
        if not count:
            return False
        # Never let modifiers accidentally restore scroll inside this pane.
        # For bulk scrolling the user can drag the native scrollbar thumb.
        if event.modifiers() != Qt.KeyboardModifier.NoModifier:
            return True
        angle = event.angleDelta().y()
        delta = angle if angle else event.pixelDelta().y() * 3
        if not delta:
            return True
        self._wheel_bookmark_delta += delta
        steps = int(abs(self._wheel_bookmark_delta) // 120)
        if not steps:
            return True
        direction = -1 if self._wheel_bookmark_delta > 0 else 1
        self._wheel_bookmark_delta -= (1 if self._wheel_bookmark_delta > 0 else -1) * steps * 120
        current = tree.currentItem()
        index = tree.indexOfTopLevelItem(current) if current is not None else -1
        indices = [i for i in range(count)
                   if self.row_data(tree.topLevelItem(i)) is not None]
        if not indices:
            return True
        if index not in indices:
            index = indices[0]
        target = indices[root_wheel_target(indices.index(index), direction * steps, len(indices))]
        # The older Bookmark Follow mode retains the same lower-edge Wheel Tab
        # destination, even if the user disables the Hybrid A/B experiment.
        at_last = index == indices[-1] and direction > 0 and target == index
        navigation = getattr(self, 'wheel_zone_navigation', None)
        at_first = index == indices[0] and direction < 0 and target == index
        if navigation is not None and navigation.feed('bookmarks-first', at_first, steps):
            self.zone_jump('directory', position='last')
            return True
        if navigation is not None and navigation.feed('bookmarks-last', at_last, steps):
            self.zone_jump('pages')
            return True
        if target is None or target == index:
            return True  # Stop at both ends; no scroll and no repeated popup.
        item = tree.topLevelItem(target)
        tree.setCurrentItem(item)
        tree.scrollToItem(item)  # Auto-follow beyond the visible rows.
        tree.setFocus(Qt.FocusReason.MouseFocusReason)
        row = self.row_data(item)
        if row and row.get('item_kind') in ('category', 'directory'):
            # Preview a folder using the original cascade; never execute it.
            self.choose_bookmark(item, 0)
            # The cascade is a non-grabbing Qt.Tool window. Keep the outline
            # and subsequent wheel navigation anchored to the bookmarks pane.
            tree.setFocus(Qt.FocusReason.MouseFocusReason)
        else:
            # Leaving a folder for a URL should dismiss its stale preview.
            self.launcher.close_cascade_for_main_interaction()
        if getattr(self.launcher, 'bookmark_pointer_follow', False):
            self.schedule_bookmark_pointer_follow(item)
        return True

    def cancel_bookmark_pointer_follow(self):
        """Cancel a pending warp (e.g. when the user switches modes)."""
        self._bookmark_follow_pending = None
        self._bookmark_warp_global = None

    def schedule_bookmark_pointer_follow(self, item):
        """Coalesce rapid wheel events so only the newest selection moves."""
        self._bookmark_follow_pending = item
        if not self._bookmark_follow_scheduled:
            self._bookmark_follow_scheduled = True
            QTimer.singleShot(0, self.follow_bookmark_pointer)

    def follow_bookmark_pointer(self):
        """Move the OS cursor onto selected row, but never click or activate."""
        self._bookmark_follow_scheduled = False
        if not getattr(getattr(self, 'launcher', None), 'pointer_warp_enabled', True):
            self._bookmark_follow_pending = None
            return
        item = self._bookmark_follow_pending
        self._bookmark_follow_pending = None
        tree = self.right.tree
        if (item is None or not getattr(self.launcher, 'bookmark_pointer_follow', False)
                or not self.isVisible() or not tree.isVisible()
                or tree.currentItem() is not item
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return
        viewport = tree.viewport()
        current_global = QCursor.pos()
        current_local = viewport.mapFromGlobal(current_global)
        # If the user moved off Bookmarks since the wheel event, do not jump.
        if not viewport.rect().contains(current_local):
            return
        bounds = tree.visualItemRect(item)
        target = cursor_target(
            (viewport.width(), viewport.height()),
            (bounds.left(), bounds.top(), bounds.width(), bounds.height()),
            current_local.x())
        if target is None:
            return
        destination = viewport.mapToGlobal(QPoint(*target))
        if destination == current_global:
            return
        self._bookmark_warp_global = (destination.x(), destination.y())
        QCursor.setPos(destination)

    def wheel_first_level(self, event, source):
        """Wheel = select/preview; never execute a command or mutate JSON.

        Each 120 angle units is one item. Accumulate smaller high-resolution
        trackpad movements rather than skipping buttons on tiny deltas.
        """
        if not self.root_buttons or event.modifiers() != Qt.KeyboardModifier.NoModifier:
            return False
        angle = event.angleDelta().y()
        # Pixel-only precision touchpads need a separate, modest conversion.
        delta = angle if angle else event.pixelDelta().y() * 3
        if not delta:
            return False
        self._wheel_root_delta += delta
        steps = int(abs(self._wheel_root_delta) // 120)
        if steps == 0:
            return True
        direction = -1 if self._wheel_root_delta > 0 else 1
        self._wheel_root_delta -= (1 if self._wheel_root_delta > 0 else -1) * steps * 120
        index = next((i for i, row in enumerate(self.root_rows)
                      if row.get('item_id') == self._wheel_root_id), None)
        if index is None:
            focus = QApplication.focusWidget()
            if focus in self.root_buttons:
                index = self.root_buttons.index(focus)
            elif source in self.root_buttons:
                index = self.root_buttons.index(source)
            else:
                index = 0
        target = root_wheel_target(index, direction * steps, len(self.root_buttons))
        if target is None:
            return True
        # A sustained extra turn at either END of the root strip acts like a
        # deliberate Wheel Tab gesture; normal one-notch selection is unchanged.
        # The left exit returns to the CURRENT Page, not a hardcoded endpoint.
        at_left = target == index == 0 and direction < 0
        at_right = target == index == len(self.root_buttons) - 1 and direction > 0
        if (getattr(self, 'wheel_zone_navigation', None) is not None and
                self.wheel_zone_navigation.feed('roots-left', at_left, steps)):
            self.zone_jump('pages', position='current')
            return True
        if (getattr(self, 'wheel_zone_navigation', None) is not None and
                self.wheel_zone_navigation.feed('roots-right', at_right, steps)):
            self.zone_jump('files')
            return True
        if target == index:
            return True
        row, button = self.root_rows[target], self.root_buttons[target]
        self._wheel_root_id = row.get('item_id')
        for i, entry in enumerate(self.root_buttons):
            entry.setChecked(i == target)
        self.focus_root(index=target)
        self.schedule_root_pointer_follow(button)
        # Show a navigable folder's menu immediately, just as changing Page
        # switches its content. Pure commands stay SELECTED, never executed.
        if row.get('item_kind') in ('category', 'directory'):
            self.open_cascade(row, button)
        elif self.launcher.menu is not None and self.launcher.menu.isVisible():
            self.launcher.menu.close()
        return True

    def schedule_root_pointer_follow(self, button):
        """Follow a wheel-chosen root button; never synthesize a click."""
        self._wheel_root_follow_pending = button
        if not self._wheel_root_follow_scheduled:
            self._wheel_root_follow_scheduled = True
            QTimer.singleShot(0, self.follow_root_pointer)

    def follow_root_pointer(self):
        """Warp only while the user is still over the second-layer strip."""
        self._wheel_root_follow_scheduled = False
        if not getattr(getattr(self, 'launcher', None), 'pointer_warp_enabled', True):
            self._wheel_root_follow_pending = None
            return
        button = self._wheel_root_follow_pending
        self._wheel_root_follow_pending = None
        if (button not in self.root_buttons or not self.isVisible()
                or not button.isVisible()
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return
        viewport = self.toolbar_scroller.viewport()
        position = QCursor.pos()
        local = viewport.mapFromGlobal(position)
        if not viewport.rect().contains(local):
            return
        # focus_root() called ensureWidgetVisible(); wait for that layout to
        # settle, and land in the visible button rather than a spacer/gap.
        destination = button.mapToGlobal(QPoint(button.width() // 2,
                                                button.height() // 2))
        if not viewport.rect().contains(viewport.mapFromGlobal(destination)):
            return
        if destination != position:
            QCursor.setPos(destination)

    def _sync_remote_area_after_mouse_press(self, area):
        """A genuine Files pane click changes Remote's logical current column.

        Mouse-pressed signals run before QTreeWidget completes its own row
        selection. Update only the logical target immediately, without moving
        native focus, changing the breadcrumb, or selecting a different row.
        """
        # One source of truth. Never set QSS properties independently here:
        # old direct-mouse code could light Exp while the Remote still said List.
        setter = getattr(self.launcher, 'set_files_operating_target', None)
        if callable(setter) and self._workspace_mode == 'files':
            setter(area)
        else:  # Standalone/non-1.5 compatibility: preserve deferred Qt click.
            display = getattr(self, 'set_files_operating_area', None)
            if callable(display):
                display(area)
            remote = getattr(self.launcher, 'remote_window', None)
            if remote is None or not remote.isVisible():
                return

            def finish():
                if (not remote.isVisible() or not self.isVisible()
                        or self._workspace_mode != 'files'):
                    return
                if getattr(self.launcher, '_remote_area', None) != area:
                    self.launcher.remote_focus_area(area)

            QTimer.singleShot(0, finish)

    def _middle_selection_is_active(self):
        """Logical Remote column wins over stale native Qt focus."""
        if not self.isVisible() or not self.middle.tree.isVisible():
            return False
        remote = getattr(self.launcher, 'remote_window', None)
        if remote is not None and remote.isVisible():
            return getattr(self.launcher, '_remote_area', None) == 'directory'
        return self.middle.tree._column_is_focused()

    def _remember_middle_current(self, item, _previous):
        if item is not None and item is not _previous:
            self.middle.tree.deliberate_blank_selection = False
        row = self.row_data(item) if item is not None else None
        key = row_key(row)
        if key:
            self._middle_current_memory = (self.current_directory(), key)

    def _queue_files_selection_status(self, *_):
        if self._files_selection_status_queued:
            return
        self._files_selection_status_queued = True
        QTimer.singleShot(0, self._flush_files_selection_status)

    def _flush_files_selection_status(self):
        self._files_selection_status_queued = False
        if getattr(self.launcher, 'expanded_view', None) is self:
            self.launcher.update_files_item_count()

    def _queue_middle_selection_repair(self, *_):
        if self._middle_selection_repair_queued:
            return
        self._middle_selection_repair_queued = True
        QTimer.singleShot(0, self._run_queued_middle_selection_repair)

    def _run_queued_middle_selection_repair(self):
        self._middle_selection_repair_queued = False
        self.ensure_middle_current_selection()

    def ensure_middle_current_selection(self):
        """Guarantee a visible/operable column-2 row whenever one exists.

        This guard does not touch other panes, navigate folders, open files,
        or interrupt inline renaming. Empty directories remain empty.
        """
        tree = self.middle.tree
        if (self._middle_selection_repair_running or
                getattr(tree, 'deliberate_blank_selection', False) or
                not self._middle_selection_is_active() or
                tree.state() == QAbstractItemView.State.EditingState):
            return None
        self._middle_selection_repair_running = True
        try:
            directory = self.current_directory()
            remembered = (self._middle_current_memory[1]
                          if self._middle_current_memory is not None
                          and self._middle_current_memory[0] == directory else None)
            item, _changed = repair_middle_selection(tree, self.row_data, remembered)
            if item is not None:
                key = row_key(self.row_data(item))
                if key:
                    self._middle_current_memory = (directory, key)
            return item
        finally:
            self._middle_selection_repair_running = False

    def focus_panel(self, panel):
        """Move keyboard focus and visible selection together."""
        tree = panel.tree
        if panel is self.middle:
            # Called on real keyboard/Remote transitions. Recover a missing
            # current item before the old first-row fallback runs.
            self._queue_middle_selection_repair()
        if (not (panel is self.middle and tree.deliberate_blank_selection)
                and tree.currentItem() is None and tree.topLevelItemCount()):
            first = next((tree.topLevelItem(i) for i in range(tree.topLevelItemCount())
                          if self.row_data(tree.topLevelItem(i)) is not None), None)
            if first is not None:
                tree.setCurrentItem(first)
        tree.setFocus(Qt.FocusReason.TabFocusReason)
        if tree.currentItem() is not None:
            tree.scrollToItem(tree.currentItem())

    def focus_root(self, item_id=None, index=None):
        if not self.root_buttons:
            return
        if not any(b.isVisible() for b in self.root_buttons):
            targets = getattr(self, 'workspace_page_buttons', [])
            if targets:
                targets[0].setFocus(Qt.FocusReason.TabFocusReason)
            return
        if item_id is not None:
            index = next((i for i, row in enumerate(self.root_rows)
                          if row.get('item_id') == item_id), None)
        if index is None or not 0 <= index < len(self.root_buttons):
            index = 0
        button = self.root_buttons[index]
        self.toolbar_scroller.ensureWidgetVisible(button)
        button.setFocus(Qt.FocusReason.TabFocusReason)

    def navigate_left_from_middle(self):
        """Move the current highlight left through *hierarchy*, not history.

        First Left selects the top row of the displayed second column. Once
        there, each Left ascends a directory and highlights the directory
        just left in its parent's listing, until the displayed directory
        matches a first-column shortcut. Then focus that shortcut. This is
        independent of how the directory was opened: if there is no matching
        first-column shortcut, continue to the filesystem root, then focus the
        first row of the first column. Never get stuck in the second column.
        """
        if getattr(self, '_virtual_directory_node', None) is not None:
            # The first List row (or an empty List) is the virtual Exp boundary.
            tree = self.middle.tree
            first = next((tree.topLevelItem(i) for i in range(tree.topLevelItemCount())
                          if self.row_data(tree.topLevelItem(i)) is not None), None)
            if first is not None and tree.currentItem() is not first:
                tree.setCurrentItem(first)
                return 'directory'
            self.launcher.remote_list_left_to_exp()
            return 'directory'
        middle_tree = self.middle.tree
        first_middle = next((middle_tree.topLevelItem(i)
                             for i in range(middle_tree.topLevelItemCount())
                             if self.row_data(middle_tree.topLevelItem(i)) is not None), None)
        if first_middle is not None and middle_tree.currentItem() is not first_middle:
            middle_tree.setCurrentItem(first_middle)
            self.focus_panel(self.middle)
            return 'directory'

        if getattr(self.launcher, 'files_root_hidden_mode', False):
            # Single-column Files: the first usable row is the LEFT boundary.
            # Never ascend or return to the hidden Files root panel.
            self.focus_panel(self.middle)
            return 'directory'

        first_tree = self.left.tree
        first_items = [first_tree.topLevelItem(i)
                       for i in range(first_tree.topLevelItemCount())]
        first_rows = [self.row_data(item) for item in first_items]
        current = self.path[-1] if self.path else None
        expand = self.launcher.expander().expand
        found = matching_first_row(current, first_rows, expand)
        if found is not None:
            first_tree.setCurrentItem(first_items[found])
            # Only change focus; changing the Files preview here would replace
            # the displayed folder before the user selects a different row.
            self.focus_panel(self.left)
            return 'files'

        # Preserve the *directory being left*, not an old navigation origin.
        # After showing its parent, highlight that directory in the listing.
        child_to_reselect = self.path[-1] if self.path else None
        if len(self.path) > 1:
            # Walk the existing hierarchy (not the visit-history stack).
            self.path.pop()
        else:
            # The route is derived ONLY from the currently displayed path.
            # Direct address, favorite, search, and first-column navigation
            # must all climb in exactly the same way, regardless of whether
            # a matching Files shortcut is somewhere above the current path.
            import ntpath
            current_path = self.current_directory()
            parent = ntpath.dirname(ntpath.normpath(current_path)) if current_path else None
            if parent and ntpath.normcase(parent) != ntpath.normcase(
                    current_path):
                self.path = [directory_row(parent)]
            else:
                # Drive/UNC root (or a virtual row without a parent): there is
                # nowhere else to ascend. Always provide an escape to column 1.
                first = next((item for item, row in zip(first_items, first_rows)
                              if row is not None), None)
                if first is not None:
                    first_tree.setCurrentItem(first)
                self.focus_panel(self.left)
                return 'files'

        # Delay refreshing while a QTreeWidget key event is in flight. Rebuilt
        # QTreeWidgetItems must not be deleted synchronously by their own event.
        def finish():
            self.refresh_middle()
            tree = self.middle.tree
            items = [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())]
            rows = [self.row_data(item) for item in items]
            index = matching_first_row(child_to_reselect, rows, expand)
            selected = items[index] if index is not None else next(
                (item for item, row in zip(items, rows) if row is not None), None)
            if selected is not None:
                tree.setCurrentItem(selected)
            self.focus_panel(self.middle)
        QTimer.singleShot(0, finish)
        return 'directory'

    def navigate_middle(self, row):
        """Descend without destroying a Qt row during the current key event."""
        virtual = row.get('_launch_virtual_node')
        if virtual is not None:
            if virtual['kind'] != 'file':
                QTimer.singleShot(0, lambda n=virtual: self.show_virtual_launch_directory(n))
            return
        if row.get('item_kind') not in ('category', 'directory'):
            return
        if self.path and self.path[-1].get('item_id') == row.get('item_id'):
            self.focus_panel(self.middle)
            return
        self.path.append(row)
        def finish():
            self.refresh_middle()
            self.focus_panel(self.middle)
        QTimer.singleShot(0, finish)

    def go_up(self, *, keep_middle_focus=False):
        """Navigate to the actual parent folder, even from direct/favorite paths.

        A breadcrumb or favorite can set self.path to a *single* row. History
        popping in that case wrongly did nothing; Back means parent directory.
        """
        if getattr(self, '_virtual_directory_node', None) is not None:
            if self._virtual_directory_node.get('kind') == 'page':
                self.launcher.remote_focus_area('files_exp')
                return
            parent = self._parent_virtual_directory()
            if parent is not None:
                self.show_virtual_launch_directory(parent)
            return
        import ntpath
        import os
        current = self.current_directory()
        if current:
            normalized = ntpath.normpath(current)
            parent = ntpath.dirname(normalized)
            if (parent and ntpath.normcase(parent) != ntpath.normcase(normalized)
                    and os.path.isdir(parent)):
                self.path = [directory_row(parent)]
                def finish():
                    self.refresh_middle()
                    self.focus_panel(self.middle if (
                        keep_middle_focus or getattr(self.launcher, 'files_root_hidden_mode', False)
                    ) else self.left)
                QTimer.singleShot(0, finish)
                return
        # PC / drive roots have no real ancestor in the file list.
        self.focus_panel(self.middle if getattr(self.launcher, 'files_root_hidden_mode', False)
                         else self.left)

    def enter_row(self, pane, item):
        """Enter runs a filesystem directory; Right instead browses it."""
        if (pane is self.middle and
                (getattr(pane.tree, '_rename_enter_guard', False) or
                 (hasattr(pane.tree, 'state') and
                  pane.tree.state() == QAbstractItemView.State.EditingState))):
            return
        row = self.row_data(item)
        if not row:
            return
        virtual = row.get('_launch_virtual_node')
        if virtual is not None:
            if virtual['kind'] == 'file':
                self.launcher.activate_virtual_launch_item(virtual.get('row'))
            else:
                # Keep the Qt item alive until its Enter/double-click event ends.
                QTimer.singleShot(0, lambda n=virtual: self.show_virtual_launch_directory(n))
            return
        if row.get('item_kind') == 'directory':
            if pane is self.middle:
                # Enter on a List folder descends INSIDE the same List column.
                # navigate_middle schedules refresh after the key event and
                # restores List focus; do not open Windows Explorer here.
                self.navigate_middle(row)
            else:
                self.launcher.execute(row)  # Other columns retain old behavior.
        elif row.get('item_kind') == 'category':
            if pane is self.left:
                self.choose_files(item, 0)
                self.focus_panel(self.middle)
            elif pane is self.middle:
                self.navigate_middle(row)
            else:
                self.open_cascade(row, pane.tree, item)
        else:
            self.launcher.activate(row)

    def root_action(self, row, button):
        if row.get('item_id') == self.files_root.get('item_id'):
            self.left.tree.setFocus()
        elif row.get('item_id') == self.bookmarks_root.get('item_id'):
            self.right.tree.setFocus()
        elif row.get('item_kind') in ('category', 'directory'):
            # Shortcuts still work via keyboard after removing their visible
            # second-layer buttons; anchor the menu to the visible workspace.
            anchor = button if button.isVisible() else self.files_mode_tab
            self.open_cascade(row, anchor)
        else:
            self.launcher.execute(row)

    def row_data(self, item):
        return item.data(0, Qt.ItemDataRole.UserRole) if item is not None else None

    def choose_files(self, item, _col):
        row = self.row_data(item)
        if not row:
            return
        self._virtual_directory_node = None
        if row.get('item_kind') in ('category', 'directory'):
            self.path = [row]
            self.refresh_middle()
        else:
            self.path = []
            self.middle.label.setText(row.get('title', ''))
            self.address_bar.set_directory(None, row.get('title', ''))
            self.middle.tree.clear()
            changed = getattr(self.launcher, 'on_files_directory_changed', None)
            if callable(changed):
                changed(None)

    def choose_middle(self, item, _col, *, force=False):
        # Extended-selection clicks must not descend into a folder: doing so
        # clears the selection while Ctrl/Shift is adding files and folders.
        modifiers = QApplication.keyboardModifiers()
        if modifiers & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            return
        row = self.row_data(item)
        virtual = (row or {}).get('_launch_virtual_node')
        if virtual is not None:
            if (virtual['kind'] != 'file' and
                    (force or getattr(self.launcher, 'folder_open_mode', 'single') != 'double')):
                QTimer.singleShot(0, lambda n=virtual: self.show_virtual_launch_directory(n))
            return
        if row and row.get('item_kind') in ('category', 'directory'):
            if not force and getattr(self.launcher, 'folder_open_mode', 'single') == 'double':
                return  # A single click selects; double-click or Enter opens.
            # Keep QTreeWidgetItem alive until Qt finishes clicked/activated
            # delivery (especially a double-click on a directory).
            if self.path and self.path[-1].get('item_id') == row.get('item_id'):
                return
            self.path.append(row)
            QTimer.singleShot(0, self.refresh_middle)

    def is_bookmark_row(self, row):
        """Only Browser bookmark descendants enter the embedded WebView.

        Keep other URL actions (Quick, custom shell shortcuts, etc.) on their
        original external browser route, even in Three-layer mode.
        """
        if not isinstance(row, dict) or not self.bookmarks_root:
            return False
        bookmark_id = self.bookmarks_root.get('item_id')
        parent_id = row.get('parent_item_id')
        if row.get('item_id') == bookmark_id:
            return True
        lookup = {entry.get('item_id'): entry for entry in
                  (self.launcher.data or {}).get('items', [])}
        seen = set()
        while parent_id and parent_id not in seen:
            if parent_id == bookmark_id:
                return True
            seen.add(parent_id)
            parent = lookup.get(parent_id)
            if not parent:
                break
            parent_id = parent.get('parent_item_id')
        return False

    def _update_workspace_tabs(self):
        for mode, button in (('files', self.files_mode_tab),
                             ('browser', self.browser_mode_tab)):
            if button is not None:
                button.setChecked(mode == self._workspace_mode)
        # The underline is a single seam with a gap under the selected tab.
        active = self.files_mode_tab if self._workspace_mode == 'files' else self.browser_mode_tab
        self.root_widget.set_selected_tab(active)

    def prewarm_browser(self):
        """Prepare the embedded Browser after Files is already on screen.

        Never switch workspace during warm-up: the user can keep working in
        Files, and the first Browser click only reveals an existing widget.
        """
        if self.launcher.webview_settings.get('mode') != 'embedded':
            return
        if self.web_view is not None:
            return
        if not self._ensure_web_view():
            return
        if not self.web_view.tabs.count():
            self.web_view.add_tab(self.launcher.webview_settings.get(
                'new_tab_url', 'https://www.google.com/'))

    def _ensure_web_view(self):
        """Build the embedded browser once; preserve every tab on mode switches."""
        if self.web_view is not None:
            return True
        try:
            from launch_web_view import LaunchWebView
            self.web_view = LaunchWebView(
                self.files_content_stack, settings=self.launcher.webview_settings)
            self.web_view.tabs.tabBar().area_tab_requested.connect(
                self.launcher.web_keyboard_tab)
            self.web_view.surface_selected.connect(self.launcher.web_surface_selected)
            self.web_view.bookmarks_show_requested.connect(self.show_browser_bookmarks)
            self.web_view.set_bookmarks_visible(False)
            self.files_content_stack.addWidget(self.web_view)
            self.refresh_horizontal_bookmarks()
            self.web_view.apply_theme(self.launcher.color_theme)
        except (ImportError, RuntimeError) as exc:
            self.launcher.error('WebViewを起動できません。PySide6 WebEngineを確認してください: ' + str(exc))
            return False
        return True

    @property
    def browser_bookmarks_visible(self):
        return self._browser_bookmarks_visible

    def refresh_horizontal_bookmarks(self):
        """Show authored Browser roots as a horizontal bar, in all Files modes."""
        web = getattr(self, 'web_view', None)
        root = getattr(self, 'bookmarks_root', None)
        if root is None:
            return
        from bookmark_menu import visible_bookmark_children
        rows = visible_bookmark_children(root, self.launcher.children)
        if web is not None:
            web.bookmark_strip.pointer_follow_enabled = (
                lambda: getattr(self.launcher, 'pointer_warp_enabled', True))
            web.bookmark_strip.update_bookmark_bar(
                rows, self.launcher.children, self.open_horizontal_bookmark)
        external_bar = getattr(self, '_external_bookmark_strip', None)
        if external_bar is not None:
            external_bar.pointer_follow_enabled = (
                lambda: getattr(self.launcher, 'pointer_warp_enabled', True))
            external_bar.update_bookmark_bar(
                rows, self.launcher.children, self.open_horizontal_bookmark)

    def open_horizontal_bookmark(self, row):
        """Reuse existing Browser URL routing and tab-target policy."""
        from webview_routes import bookmark_web_url
        url = bookmark_web_url(row)
        if not url or not self.is_bookmark_row(row):
            return
        if self.show_web_url(url, new_tab=self.bookmark_new_tab):
            return
        actions = row.get('launch_actions') or []
        step = actions[0] if actions else {}
        self.launcher.open_target(
            url, step.get('launch_browser', ''),
            step.get('launch_browser_profile', ''))

    def show_browser_bookmarks(self):
        self.set_browser_bookmarks_visible(True)

    def hide_browser_bookmarks(self):
        self.set_browser_bookmarks_visible(False)

    def set_browser_bookmarks_visible(self, visible, *, persist=True):
        """Collapse Bookmarks to ZERO width without destroying its selection.

        The complete WebView gets the released width, and the last useful
        Bookmarks/Web splitter sizes survive both the collapse and HOME.
        """
        # Browser's navigation bar has replaced the left Bookmarks pane in
        # EVERY Files first-column mode. Keep the legacy model for menus.
        visible = False
        persist = False
        visible = bool(visible)
        if not visible and self._workspace_mode == 'browser' and self.right.isVisible():
            widths = self.splitter.sizes()
            if len(widths) == 2 and all(width > 0 for width in widths):
                self._browser_splitter_sizes = widths
        self._browser_bookmarks_visible = visible
        self.cancel_bookmark_hover()
        self.cancel_bookmark_pointer_follow()
        if self._workspace_mode == 'browser' and visible:
            self.right.show()
            widths = self._browser_splitter_sizes
            if widths is not None and len(widths) == 2 and all(w > 0 for w in widths):
                self.splitter.setSizes(widths)
        else:
            self.right.hide()
        if self.web_view is not None:
            self.web_view.set_bookmarks_visible(visible)
        if self._browser_empty_bookmark_button is not None:
            self._browser_empty_bookmark_button.setEnabled(False)
            self._browser_empty_bookmark_button.setVisible(False)
        # Never let a hidden row remain the Remote's logical target.
        if (not visible and self._workspace_mode == 'browser' and
                getattr(self.launcher, '_remote_area', None) == 'bookmarks' and
                getattr(self.launcher, 'remote_window', None) is not None):
            self.launcher.remote_focus_area(self.launcher._current_web_body_area())
        if persist:
            self.launcher.settings.setValue('browser_bookmarks_visible', visible)
            self.launcher.settings.sync()
        self.root_widget.refresh_underline()

    def _activate_browser_layout(self):
        """Show Browser + Bookmarks without discarding the Files column state."""
        self._workspace_mode = 'browser'
        self.set_browser_bookmarks_visible(False, persist=False)
        visible = False  # A horizontal bookmark bar now owns navigation.
        if visible:
            self.right.show()
            widths = self._browser_splitter_sizes
            if widths is not None and len(widths) == 2 and all(w > 0 for w in widths):
                self.splitter.setSizes(widths)
            else:
                self.splitter.setSizes([350, 660])
        else:
            self.right.hide()
        if getattr(self, 'web_view', None) is not None:
            self.web_view.set_bookmarks_visible(visible)
        # Repaint after the Browser/Bookmarks splitter has been restored,
        # so the underline ends at the actual bookmark-pane boundary.
        self._update_workspace_tabs()
        self.refresh_horizontal_bookmarks()
        self.launcher.web_view_activated()
        if hasattr(self.launcher, 'workspace_changed'):
            self.launcher.workspace_changed('browser')
        update_count = getattr(self.launcher, 'update_files_item_count', None)
        if callable(update_count):
            update_count()

    def switch_workspace(self, mode):
        """Explicit Files/Browser tabs, initially mouse-driven (Remote later)."""
        if mode == 'files':
            self.show_files_view()
            return True
        if mode != 'browser':
            return False
        if self.launcher.webview_settings.get('mode') != 'embedded':
            # Company/external mode: never instantiate Qt WebEngine.
            if self._browser_empty_page is None:
                # External mode has no QWebEngineView toolbar. Keep a reopen
                # control here too, otherwise a persisted collapsed bookmark
                # panel would become impossible to reopen on company PCs.
                self._browser_empty_page = QWidget(self.files_content_stack)
                empty_layout = QVBoxLayout(self._browser_empty_page)
                from browser_bookmark_bar import HorizontalBookmarkBar
                self._external_bookmark_strip = HorizontalBookmarkBar(self._browser_empty_page)
                empty_layout.addWidget(self._external_bookmark_strip)
                self._browser_empty_bookmark_button = QToolButton(self._browser_empty_page)
                self._browser_empty_bookmark_button.setObjectName('expandedExternalShowBookmarks')
                self._browser_empty_bookmark_button.setFixedSize(30, 29)
                self._browser_empty_bookmark_button.setIconSize(QSize(19, 19))
                self._browser_empty_bookmark_button.setToolTip('ブックマークを表示')
                self._browser_empty_bookmark_button.setIcon(browser_navigation_icon(
                    'bookmark_outline', theme_family(self.launcher.color_theme)))
                self._browser_empty_bookmark_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                self._browser_empty_bookmark_button.clicked.connect(self.show_browser_bookmarks)
                self._browser_empty_bookmark_button.setEnabled(
                    not self._browser_bookmarks_visible)
                # The horizontal bar is permanently visible; the old
                # left-column opener is obsolete in external Browser mode.
                self._browser_empty_bookmark_button.hide()
                placeholder = QLabel(
                    'Browser は外部ブラウザモードです。\n'
                    'ブックマークをクリックすると外部ブラウザで開きます。',
                    self._browser_empty_page)
                placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
                empty_layout.addWidget(placeholder, 1)
                self.files_content_stack.addWidget(self._browser_empty_page)
            self.files_content_stack.setCurrentWidget(self._browser_empty_page)
            self._activate_browser_layout()
            self.refresh_horizontal_bookmarks()
            return True
        if not self._ensure_web_view():
            self._update_workspace_tabs()
            return False
        if not self.web_view.tabs.count():
            self.web_view.add_tab(self.launcher.webview_settings.get(
                'new_tab_url', 'https://www.google.com/'))
        self.files_content_stack.setCurrentWidget(self.web_view)
        self._activate_browser_layout()
        return True

    def show_web_url(self, url, *, new_tab=False):
        """Open a bookmark in Browser using the requested tab destination."""
        if self.launcher.webview_settings.get('mode') != 'embedded':
            return False
        if not self._ensure_web_view():
            return False
        self.files_content_stack.setCurrentWidget(self.web_view)
        self._activate_browser_layout()
        if new_tab:
            self.web_view.show_url(url, new_tab=True)
        else:
            self.web_view.show_url(url)
        return True

    def show_files_view(self):
        """Return to Files without destroying or navigating Browser's tabs."""
        self._web_selection_timer.stop()
        if self._workspace_mode == 'browser' and self.right.isVisible():
            sizes = self.splitter.sizes()
            if len(sizes) == 2 and all(sizes):
                self._browser_splitter_sizes = sizes
        if self.web_view is not None:
            self.web_view.set_remote_area(None)
            hide_url_favorites = getattr(self.web_view, 'hide_url_favorites', None)
            if callable(hide_url_favorites):
                hide_url_favorites()
        self._workspace_mode = 'files'
        self.files_content_stack.setCurrentWidget(self.files_group)
        if getattr(self.launcher, 'files_exp_embedded_mode', False):
            self.left.show()
            self.embedded_files_exp.show()
        elif getattr(self.launcher, 'files_root_hidden_mode', False):
            self.left.hide()
            self.files_first_host.setVisible(
                bool(getattr(self.launcher, 'remote_15_mode', False)))
        self.right.hide()  # Bookmarks belong to Browser, never Files.
        self.apply_remote_15_lane_mode()
        self._update_workspace_tabs()
        # During ExpandedLauncherView.__init__, Launcher.expanded_view has not
        # yet been assigned; a callback here would touch an uninitialized UI.
        if (getattr(getattr(self, 'launcher', None), 'expanded_view', None) is self
                and hasattr(self.launcher, 'workspace_changed')):
            self.launcher.workspace_changed('files')
            update_count = getattr(self.launcher, 'update_files_item_count', None)
            if callable(update_count):
                update_count()

    def reload_embedded_files_exp_roots(self, *, preserve_state=False):
        """Rebase the inline tree on authored roots, not the current folder.

        Exp selection and branch expansion are separate from the breadcrumb;
        rebuilding a changed data model cannot silently navigate Files.
        """
        panel = self.embedded_files_exp
        if preserve_state and self._embedded_files_exp_roots_ready:
            panel._tree_state_timer.stop()
            panel._save_tree_state()
        rows = [self.row_data(self.left.tree.topLevelItem(i))
                for i in range(self.left.tree.topLevelItemCount())]
        rows = [row for row in rows if isinstance(row, dict)]
        if not rows:
            return False
        panel.set_roots(rows, self.launcher.expander().expand)
        self._embedded_files_exp_roots_ready = True
        if not panel.restore_previous_tree_state():
            panel.sync_current_directory(self.current_directory())
        return True

    def apply_remote_15_lane_mode(self):
        """Reserve 196px next to column 1 without embedding the Remote.

        The legacy splitter still has exactly two children, so all former
        saved sizes, hide/show and browser-state behavior remain compatible.
        """
        enabled = bool(getattr(self.launcher, 'remote_15_mode', False))
        old = bool(getattr(self, '_remote_15_lane_applied', False))
        if enabled == old:
            return
        self._remote_15_lane_applied = enabled
        sizes = self.files_splitter.sizes()
        if enabled:
            self._remote_15_previous_sizes = sizes[:]
            self.remote_15_lane.show()
            self.files_first_host.show()
            stored = str(self.launcher.settings.value(
                'workspace_files_remote_15_splitter_sizes', '') or '')
            try:
                widths = [int(v) for v in stored.split('|')]
                if len(widths) != 2 or widths[0] < 196 or widths[1] < 100:
                    raise ValueError('invalid saved 1.5-column widths')
            except (TypeError, ValueError):
                first = sizes[0] if len(sizes) == 2 else 275
                second = sizes[1] if len(sizes) == 2 else 700
                # Classic single-column: the first host was hidden and zero.
                first = max(0, first) + 196
                widths = [max(196, first), max(100, second - 196)]
            self.files_splitter.setSizes(widths)
        else:
            self.remote_15_lane.hide()
            self.files_first_host.setVisible(
                not self.launcher.files_root_hidden_mode
                or self.launcher.files_exp_embedded_mode)
            sizes = getattr(self, '_remote_15_previous_sizes', None)
            if sizes and len(sizes) == 2:
                self.files_splitter.setSizes(sizes)
        self.launcher.queue_remote_15_alignment()

    def apply_files_root_hidden_mode(self):
        """Three reversible modes: legacy tree, hidden, or embedded Files Exp.

        Keep two physical splitter columns: the legacy first-column widget
        stays alive, and only its *contents* are replaced by the Exp tree.
        """
        enabled = bool(getattr(self.launcher, 'files_root_hidden_mode', False))
        embedded = bool(getattr(self.launcher, 'files_exp_embedded_mode', False))
        previous = getattr(self, '_files_root_experiment_applied', False)
        previously_embedded = getattr(self, '_files_root_embedded_applied', False)
        if enabled and not previous:
            self._files_root_saved_sizes = self.files_splitter.sizes()
            self._files_root_saved_bookmarks = self._browser_bookmarks_visible
        self._files_root_experiment_applied = enabled
        self._files_root_embedded_applied = embedded
        self.left.tree.setVisible(not embedded)
        self.left.header.setVisible(not embedded)
        self.embedded_files_exp.setVisible(embedded and self._workspace_mode == 'files')
        self.left.setVisible(not enabled or embedded)
        host = getattr(self, 'files_first_host', None)
        if host is not None:
            host.setVisible(
                not enabled or embedded or getattr(self.launcher, 'remote_15_mode', False))
        if embedded and not self._embedded_files_exp_roots_ready:
            self.reload_embedded_files_exp_roots()
        if embedded and not previously_embedded:
            stored = str(self.launcher.settings.value(
                'workspace_files_exp_embedded_splitter_sizes', '') or '')
            try:
                widths = [int(part) for part in stored.split('|')]
                if len(widths) != 2 or min(widths) < 100:
                    raise ValueError('invalid embedded splitter widths')
            except (ValueError, TypeError):
                # This is an initial *ratio*, not a fixed window pixel size.
                widths = [275, 725]
            self.files_splitter.setSizes(widths)
        if enabled:
            self.set_browser_bookmarks_visible(False, persist=False)
            self.middle.tree.setProperty('remoteInactive', False)
            if self._workspace_mode == 'files':
                self.launcher._remote_area = 'directory'
        elif previous:
            sizes = getattr(self, '_files_root_saved_sizes', None)
            if sizes is not None and len(sizes) == 2 and all(v > 0 for v in sizes):
                self.files_splitter.setSizes(sizes)
            self.set_browser_bookmarks_visible(
                getattr(self, '_files_root_saved_bookmarks', True), persist=False)
        self.middle.tree.style().unpolish(self.middle.tree)
        self.middle.tree.style().polish(self.middle.tree)
        self.middle.tree.viewport().update()

    def web_view_active(self):
        return (self._workspace_mode == 'browser' and self.web_view is not None
                and self.files_content_stack.currentWidget() is self.web_view)

    def schedule_web_bookmark_preview(self, item, _previous):
        """Selection means *only selection*, including wheel and Up/Down."""
        self._web_selection_timer.stop()

    def preview_selected_bookmark(self):
        """Deliberately disabled: opening a URL requires click, Right, Enter."""
        return None

    def choose_bookmark(self, item, _col, *, force=False):
        row = self.row_data(item)
        from webview_routes import bookmark_web_url
        url = bookmark_web_url(row)
        if url and self.is_bookmark_row(row):
            self._web_selection_timer.stop()
            # Keep legacy current-tab call shape for existing integrations;
            # new-tab selection explicitly asks the WebView for another tab.
            opened = (self.show_web_url(url, new_tab=True)
                      if getattr(self, 'bookmark_new_tab', False)
                      else self.show_web_url(url))
            if not opened:
                # Do not route through activate()/execute() again: that would
                # retry the failed WebEngine import and show the same error twice.
                step = row['launch_actions'][0]
                self.launcher.open_target(
                    url, step.get('launch_browser', ''),
                    step.get('launch_browser_profile', ''))
            return
        if row and row.get('item_kind') in ('category', 'directory'):
            # Bookmark folders always open on a click. In double mode, only
            # hover preview is disabled; Files' middle column remains double.
            self.open_cascade(row, self.right.tree, item)

    def activate_row(self, pane, item):
        # Enter committed inside the inline filename editor is NOT an open.
        if (pane is self.middle and
                (getattr(pane.tree, '_rename_enter_guard', False) or
                 (hasattr(pane.tree, 'state') and
                  pane.tree.state() == QAbstractItemView.State.EditingState))):
            return
        row = self.row_data(item)
        if not row:
            return
        virtual = row.get('_launch_virtual_node')
        if virtual is not None:
            if virtual['kind'] == 'file':
                self.launcher.activate_virtual_launch_item(virtual.get('row'))
            else:
                # Keep the Qt item alive until its Enter/double-click event ends.
                QTimer.singleShot(0, lambda n=virtual: self.show_virtual_launch_directory(n))
            return
        if row.get('item_kind') in ('category', 'directory'):
            if pane is self.left:
                self.choose_files(item, 0)
            elif pane is self.middle:
                self.choose_middle(item, 0, force=True)
            else:
                self.choose_bookmark(item, 0, force=True)
        else:
            if pane is self.right:
                self.choose_bookmark(item, 0, force=True)
            else:
                self.launcher.activate(row)

    def open_cascade(self, row, widget, item=None):
        """Use Launcher's existing menu content/actions; no new command logic."""
        self.launcher.open_expanded_cascade(row, widget, item)

    def _middle_launch_drop_target(self, point, mime):
        """Only a visible authored category or blank space of that category."""
        if not mime_sources(mime) or self._workspace_mode != 'files':
            return False
        current = getattr(self, '_virtual_directory_node', None)
        if not isinstance(current, dict):
            return False
        item = self.middle.tree.itemAt(point)
        virtual = (self.row_data(item) or {}).get('_launch_virtual_node') if item else current
        if not isinstance(virtual, dict) or virtual.get('runtime_catalog'):
            return False
        if virtual.get('kind') == 'page' and not virtual.get('item_id'):
            entries = mime_sources(mime)
            if not all(Path(e.get('value', '')).is_dir() for e in entries):
                return False
        elif (virtual.get('row') or {}).get('item_kind') != 'category':
            return False
        return virtual_item_identity(virtual)

    def context_menu(self, pane, point, *, global_pos=None):
        item = pane.tree.itemAt(point)
        if not item:
            if pane is self.middle and self._virtual_directory_node is not None:
                self.launcher.show_virtual_launch_context(
                    virtual_item_identity(self._virtual_directory_node),
                    global_pos if global_pos is not None else pane.tree.viewport().mapToGlobal(point))
                return
            # With no header Paste button, an empty folder must still be
            # pasteable via right-click on its empty middle pane.
            if pane is self.middle and self.current_directory():
                # Explicitly right-clicking blank space means paste HERE,
                # not into a previously selected child folder.
                pane.tree.clearSelection()
                # The lower blank area is both Back (double click) and
                # Paste + New (right click). Keep the existing Paste contract.
                self.launcher.show_expanded_background_paste_menu(
                    (global_pos if global_pos is not None else pane.tree.viewport().mapToGlobal(point)))
            return
        row = self.row_data(item)
        if row is None:  # Non-actionable bookmark section heading.
            return
        if pane is self.middle and row.get('_launch_virtual_node') is not None:
            self.launcher.show_virtual_launch_context(
                row['_launch_virtual_node'],
                global_pos if global_pos is not None else pane.tree.viewport().mapToGlobal(point))
            return
        if pane is self.middle:
            tree = pane.tree
            # A right-click on a selected row keeps the full extended selection.
            # A right-click elsewhere changes the target to that one row.
            if not item.isSelected():
                tree.clearSelection()
                tree.setCurrentItem(item)
                item.setSelected(True)
            selected_rows = [self.row_data(i) for i in tree.selectedItems()]
            targets = context_paths(row, selected_rows, self.launcher.authored_items)
            shown = self.launcher.show_launch_context_menu(
                (global_pos if global_pos is not None else tree.viewport().mapToGlobal(point)), row,
                context_parent=self.launcher, selected_paths=targets)
            if shown and len(targets) == 1:
                menu = getattr(self.launcher, '_launch_context_menu', None)
                if menu is not None:
                    for action in menu.actions():
                        # Built-in context rename uses a modal text dialog.
                        # Replace ONLY this pane's Rename action with inline.
                        if '名前の変更' in action.text():
                            try:
                                action.triggered.disconnect()
                            except (TypeError, RuntimeError):
                                pass
                            action.triggered.connect(
                                lambda checked=False, i=item:
                                self.begin_context_inline_rename(i))
                            break
        else:
            pane.tree.setCurrentItem(item)
            self.launcher.show_launch_context_menu(
                (global_pos if global_pos is not None else pane.tree.viewport().mapToGlobal(point)), row, context_parent=self.launcher)
