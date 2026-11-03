import sys
import os
import json
from html import escape as html_escape
import sqlite3
import logging
import time
import threading
from contextlib import contextmanager
import subprocess
from pathlib import Path
from ctypes import wintypes
import ctypes
import math
from PySide6.QtCore import Qt, QTimer, QThread, QSettings, QEvent, QEventLoop, QLockFile, QDir, QRectF, QRect, QPoint, QPointF, QSize, QObject, Signal, QMimeData, QUrl
from PySide6.QtGui import QActionGroup, QIcon, QPixmap, QPainter, QColor, QBrush, QKeyEvent, QShortcut, QKeySequence, QCursor, QAction, QPainterPath, QRegion, QPen, QFont, QLinearGradient
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLineEdit, QTabBar, QTreeWidget, QTreeWidgetItem, QMenu, QSystemTrayIcon, QFileIconProvider, QMessageBox, QFileDialog, QDialog, QLabel, QHBoxLayout, QDialogButtonBox, QCheckBox, QPushButton, QWidgetAction, QAbstractItemView, QHeaderView, QFrame, QInputDialog, QStyle, QSizePolicy, QToolButton, QProgressBar)
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtCore import QFileInfo
from file_drag import ExternalFileDragTree, begin_file_copy_drag
from file_drag_paths import file_path_for_drag
from file_icon_policy import icon_lookup
from core import load, Expander, searchable_rows, column_filter_match, join_selection_values
from search_matching import matches_search_text, matches_choice_search
from ime_input import initialize_halfwidth_english
from search_result_order import display_columns, sort_search_pairs
from selection_scope import (update_visible_checks, leave_global_choice_selection,
                             global_choice_ids_in_results, filtered_selection_choices)
from navigation_wrap import next_wrapped, move_tree_selection, next_page_ring_target
from menu_wheel import wheel_motion, wheel_neighbor
from wheel_adaptive import can_follow_at_edge
from bookmark_cursor_follow import cursor_target
from view_navigation_history import ViewNavigationHistory
from browser_nav_icons import browser_navigation_icon
from webview_routes import bookmark_web_url
from webview_settings import read_webview_settings
from search_history import SearchHistory, normalize_keyword
from session_search_history import SessionSearchHistory, SESSION_HISTORY
from search_history_categories import SearchHistoryCategories, UNCATEGORIZED
from popup_sizing import popup_available_height, popup_tree_height
from history_category_tree import HistoryCategoryTree, ROLE_KIND, ROLE_ID
from history_popup_filter import matches_history_filter
from history_wheel_navigation import history_target_index, warp_to_history_row
from wheel_adaptive import wheel_steps
from reorderable_tree import ReorderablePopupTree
from menu_hotkeys import menu_shortcuts, MENU_HOTKEY_ID_START
import jump_list
import windows
import installed_apps
import browser_bookmarks
import file_index
from frame_geometry import resize_frame
from page_tab_theme import PAGE_TABS_QSS
from launch_appearance import (normalize_theme, theme_palette, theme_family, available_themes,
    context_menu_spacing_qss, history_popup_qss, LIGHT_MAIN_QSS, LIGHT_TABS_QSS,
    LIGHT_HISTORY_QSS, LIGHT_MENU_QSS, LIGHT_CASCADE_TREE_QSS,
    LIGHT_COLUMN_FILTER_QSS, FRAME_COLORS, light_scrollbar_qss, CONTEXT_MENU_SPACING_QSS)
from page_tab_focus import FocusPageTabBar
from combo_chevron_icon import combo_chevron_icon
from menu_display import cascade_label
from cascade_properties import authored_cascade_row
from clipboard_paste import clipboard_sources, is_cut_clipboard, make_paste_plan, paste_items, paste_conflicts
from virtual_clipboard_paste import is_virtual_file_clipboard, virtual_clipboard_names, preflight_virtual_destination, paste_virtual_shell_items
from context_menu_icons import context_action_icon
from zip_extract_action import (is_extractable_zip, default_extract_destination,
                                invoke_windows_extract_all, safe_extract_zip)
from cloud_link_shell import request_native_copy_link, select_in_explorer
from windows_open_with import discover_open_with_apps, open_file_with_app
from file_transfer_visual import transfer_state, pasted_paths_for, path_key, moved_source_parent_directories
from context_menu_resolver import resolve_context_target
from context_menu_config import load_context_menus, visible_context_entries
from context_menu_actions import (show_windows_properties, open_file_explorer, open_parent_folder,
                                  open_with_windows_dialog, open_folder_terminal, open_parent_powershell,
                                  run_script_with_pause, rename_file_or_folder, move_to_recycle_bin, sort_browser_entries,
                                  is_downloads_zip, read_git_commit_options, git_commit_preview,
                                  commit_tracked_changes)
from menu_viewport import place_popup, main_cascade_anchor_x, MENU_SCREEN_MARGIN
from bookmark_menu import visible_bookmark_children
from apps_scan_support import append_apps_log, scan_shortcuts, merge_catalog
from ordering import save_order
from reorder_widgets import OrderDragMixin, ReorderTree
from process_runner import start_process, should_start_before_dismiss, batch_script_working_directory
from studio_theme_launch import studio_launch_arguments
from launch_diagnostics import make_logger, wifi_transcript_arguments
from log_retention import cleanup as cleanup_diagnostics
from logging.handlers import RotatingFileHandler
from runtime_paths import launch_home
from interaction_modes import read_dismiss_on_outside, read_folder_open_mode, is_double_click_folder
from desktop_double_click import DesktopDoubleClick
from launch_remote import LaunchRemote
from passive_header_drag import PassiveHeaderDrag
from remote_navigation import next_area, previous_area, starting_area
from remote_page_items import visible_remote_page_roots
from files_selection_status import files_selected_summary

# Limit cascade-column width; never let a long description/URL stretch across the screen.
CASCADE_MAX_WIDTH = 560
CASCADE_TEXT_RESERVE = 92  # icon, margins, menu indicator and style-dependent padding (px)

# Match the slender, dark scrollbar used by the installed-app cascade menu.
# The search results need both axes because their two columns are resizable.
MAIN_LIST_SCROLLBAR_QSS = """
    QScrollBar:vertical { background:#202b29; width:8px; margin:0; border:0; }
    QScrollBar:horizontal { background:#202b29; height:8px; margin:0; border:0; }
    QScrollBar::handle:vertical { background:#929894; min-height:28px; border-radius:2px; margin:0 2px; }
    QScrollBar::handle:horizontal { background:#929894; min-width:28px; border-radius:2px; margin:2px 0; }
    QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover { background:#c9d0cc; }
    QScrollBar::handle:vertical:pressed, QScrollBar::handle:horizontal:pressed { background:#eef2ef; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; border:0; background:transparent; }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width:0; border:0; background:transparent; }
    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical,
    QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal { width:0; height:0; background:transparent; }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background:transparent; }
"""

def scrollbar_qss(background='#202b29'):
    """One scrollbar appearance for every Launcher list/popup, both axes."""
    return MAIN_LIST_SCROLLBAR_QSS.replace('#202b29', background)


def apply_scrollbar_theme(view, background='#202b29'):
    """Style real scrollbar widgets; styling the tree alone can miss child bars.

    QTreeWidget / QAbstractScrollArea may construct their native-looking child
    QScrollBars separately. Give BOTH bars the same explicit theme, including
    the initially hidden horizontal scrollbar.
    """
    style = scrollbar_qss(background)
    view.verticalScrollBar().setStyleSheet(style)
    view.horizontalScrollBar().setStyleSheet(style)


ROOT = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parents[1]
LAUNCH_HOME = launch_home(ROOT)
CONFIG = LAUNCH_HOME / 'config' / 'frb_launch_sample_data_v0_1.json'
STATE = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'FRBLaunch'
STATE.mkdir(parents=True, exist_ok=True)
logging.basicConfig(handlers=[RotatingFileHandler(STATE / 'error.log', maxBytes=1024*1024,
                                                  backupCount=2, encoding='utf-8')],
                    level=logging.WARNING,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
DIAG = make_logger(STATE)
LOG_RETENTION_OPTIONS = LAUNCH_HOME / 'config' / 'log_retention_options.json'
CONTEXT_MENU_OPTIONS = LAUNCH_HOME / 'config' / 'context_menu_options.json'
GIT_COMMIT_OPTIONS = LAUNCH_HOME / 'config' / 'git_commit_options.json'


def prune_diagnostics():
    try:
        deleted = cleanup_diagnostics(STATE, LOG_RETENTION_OPTIONS)
        if any(deleted.values()):
            DIAG.info('LOG_RETENTION removed wifi_process=%s audio_process=%s audio_config_backups=%s',
                      deleted['wifi_process'], deleted['audio_process'], deleted['audio_config'])
    except Exception:
        DIAG.exception('LOG_RETENTION cleanup failed')


prune_diagnostics()
DIAG.info('START root=%s config=%s', ROOT, CONFIG)


def icon(kind):
    pix = QPixmap(24,24); pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    color = '#6ba7ff' if kind.startswith('category') else '#e9bb61' if kind.startswith('folder') else '#72d7c0'
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(color))
    if 'folder' in kind or 'category' in kind:
        p.drawRoundedRect(2,7,20,14,3,3); p.drawRoundedRect(3,4,9,7,2,2)
    else:
        p.drawRoundedRect(3,3,18,18,5,5)
        p.setPen(QColor('#17212b')); p.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, {'calendar':'D','mail':'@','wifi':'W','volume':'♪','archive':'Z','globe':'↗','settings':'⚙'}.get(kind,'›'))
    p.end(); return QIcon(pix)


def history_clock_icon():
    """Color-emoji history marker without altering the saved keyword text."""
    pix = QPixmap(48, 48)
    pix.setDevicePixelRatio(2)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setFont(QFont('Segoe UI Emoji', 15))
    painter.drawText(QRect(0, 0, 24, 24), Qt.AlignmentFlag.AlignCenter, '🕔')
    painter.end()
    return QIcon(pix)


def application_icon():
    # PyInstaller bundles assets below _MEIPASS; source runs use the project root.
    resources = Path(getattr(sys, '_MEIPASS', ROOT))
    path = resources / 'assets' / 'frb_launch.ico'
    result = QIcon(str(path))
    return result if not result.isNull() else icon('command')


def tray_icon():
    resources = Path(getattr(sys, '_MEIPASS', ROOT))
    result = QIcon(str(resources / 'assets' / 'frb_launch_tray.svg'))
    return result if not result.isNull() else application_icon()


def toolbar_outline_icon(name, theme='light'):
    """Crisp HiDPI glyphs: true short-handled magnifier and a closed gear outline.

    Search/settings use a larger 28dp drawing area; all other titlebar glyphs
    retain the original 24dp geometry.  Do not use QLineEdit.addAction for
    search: Qt reduces those icons to the native 16dp action size on Windows.
    """
    side = 28 if name in ('search', 'settings') else 24
    scale = 3
    pix = QPixmap(side * scale, side * scale)
    pix.setDevicePixelRatio(scale)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    color = '#647c70' if theme == 'light' else '#e3eee7'
    pen = QPen(QColor(color))
    pen.setWidthF(1.9 if name == 'search' else 1.8)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    if name == 'search':
        # Reference sample: 14dp bowl, short 4dp handle, not a tiny 16dp action.
        painter.drawEllipse(QRectF(4.5, 4.4, 13.8, 13.8))
        painter.drawLine(QPointF(16.4, 16.2), QPointF(20.2, 20.0))
    elif name == 'settings':
        # An 8-tooth continuous gear silhouette (not a circle with loose rays).
        cx, cy, pitch = 14.0, 14.0, math.pi / 4.0
        outline = QPainterPath()
        first = True
        for tooth in range(8):
            angle = -math.pi / 2 + tooth * pitch
            for fraction, radius in ((-.49, 7.3), (-.31, 7.3),
                                     (-.20, 10.0), (.20, 10.0),
                                     (.31, 7.3), (.49, 7.3)):
                theta = angle + fraction * pitch
                x = cx + radius * math.cos(theta)
                y = cy + radius * math.sin(theta)
                if first:
                    outline.moveTo(x, y)
                    first = False
                else:
                    outline.lineTo(x, y)
        outline.closeSubpath()
        painter.drawPath(outline)
        painter.drawEllipse(QRectF(cx-3.1, cy-3.1, 6.2, 6.2))
    elif name == 'minimize':
        painter.drawLine(5.9, 17.3, 18.1, 17.3)
    elif name == 'maximize':
        painter.drawRoundedRect(5.8, 5.8, 12.4, 12.4, 1.9, 1.9)
    elif name == 'restore':
        painter.drawRoundedRect(8.2, 5.9, 9.0, 9.0, 1.5, 1.5)
        painter.drawLine(8.2, 8.8, 6.2, 8.8)
        painter.drawLine(6.2, 8.8, 6.2, 16.8)
        painter.drawLine(6.2, 16.8, 14.2, 16.8)
    elif name == 'close':
        painter.drawLine(6.4, 6.4, 17.6, 17.6)
        painter.drawLine(17.6, 6.4, 6.4, 17.6)
    else:
        painter.end()
        raise ValueError(f'Unknown toolbar icon: {name}')
    painter.end()
    return QIcon(pix)


def view_mode_icon(mode, theme='light'):
    """Compact/Three-layer: same 16px stroke footprint as Files density glyph.

    Drawing in the SAME 28dp coordinate system as density_lines_icon() prevents
    Windows button styles from inflating these icons to oversized artwork.
    Four compact lines have identical lengths and regular vertical spacing.
    """
    side, scale = 28, 2
    pix = QPixmap(side * scale, side * scale)
    pix.setDevicePixelRatio(scale)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    pen = QPen(QColor('#557eaa' if theme == 'light' else '#cfe0ff'), 2.0)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    if mode == 'classic':
        # Compact: four equal-length, evenly spaced strokes (16dp across).
        for y in (6.5, 11.5, 16.5, 21.5):
            painter.drawLine(QPointF(7, y), QPointF(23, y))
    elif mode == 'expanded':
        # Three-layer: three paired strokes, same 16dp outer width.
        for y in (9, 14, 19):
            painter.drawLine(QPointF(7, y), QPointF(13, y))
            painter.drawLine(QPointF(17, y), QPointF(23, y))
    else:
        painter.end()
        raise ValueError(f'Unknown view mode icon: {mode}')
    painter.end()
    return QIcon(pix)


def brand_pixmap(size=28):
    resources = Path(getattr(sys, '_MEIPASS', ROOT))
    path = resources / 'assets' / 'frb_launch.png'
    if path.is_file():
        pix = QPixmap(str(path))
        if not pix.isNull():
            return pix.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
    return application_icon().pixmap(size, size)


class CascadeMenu(OrderDragMixin,QMenu):
    """Explicit child popups: selecting a folder never opens it automatically."""
    def __init__(self, title='', parent=None, launcher=None):
        super().__init__(title, parent)
        self.launcher = launcher or parent
        # Qt.Popup grabs mouse input: a right-click on the launcher while a
        # cascade is open merely dismisses the popup and never reaches the
        # launcher.  These are launcher-owned *tool* columns, not modal menus.
        # Keep QMenu's actions/keyboard semantics without its popup mouse grab.
        # Consequently, the launcher can close the cascade first on the same
        # right-button press and handle the context menu on button release.
        self.setWindowFlags(Qt.WindowType.Tool |
                            Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint)
        self.child = None
        self.open_mode = "keyboard"; self.owner_item = None; self.owner_action = None; self.outside_since = None
        self.setup_order_drag();self.order_press=None
        self.openers = {}
        # A search belongs to one open column, including installed-app lists.
        self.filter_action = None
        self.filter_edit = None
        self.filter_count = None
        self.paste_button = None
        self._order_enabled_before_filter = False
        # Preserve the popup's original frame while local filtering hides rows.
        # Otherwise QMenu shrinks to the remaining matches on every keystroke.
        self._filter_original_minimum = None
        self.scroll_tree = None
        self._scroll_actions = []
        self._scroll_action = None
        self._scroll_original_tree_height = None
        self.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        # QAction tooltips are disabled by default on some Qt styles.
        self.setToolTipsVisible(True)
        screen = QApplication.primaryScreen()
        available = screen.availableGeometry().width() if screen else CASCADE_MAX_WIDTH + 80
        self.setMaximumWidth(min(CASCADE_MAX_WIDTH, max(280, available - 80)))
        self.setStyleSheet('QMenu { menu-scrollable: 1; }')
        self.hover_timer = QTimer(self); self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(lambda:self.open_current("hover"))
        # A folder's first click must not let QMenu dismiss itself. Delay
        # expansion until the double-click window has passed, so double-click
        # can instead open the actual folder in Explorer.
        self.folder_click_timer = QTimer(self)
        self.folder_click_timer.setSingleShot(True)
        self.folder_click_timer.timeout.connect(self._finish_folder_single_click)
        self._folder_click_action = None
        self._folder_double_click_row = None
        self._folder_double_click_action = None
        self._bookmark_ignore_double_release = False
        self._right_context_row = None
        # A separate context QMenu must not erase the selected row in the
        # launcher-owned tool column while the popup temporarily owns focus.
        self._context_highlight_action = None
        self._transfer_data_changed_connected = False
        # Per-column wheel navigation. The cursor follows only when the user's
        # "マウスポインター自動" setting is ON; the OFF mode keeps Qt's native wheel.
        self._column_wheel_remainder = 0
        self._column_wheel_follow_pending = None
        self._column_wheel_follow_scheduled = False

    def _wheel_column_viewport(self):
        """Return the row surface of *this* column, not its parent/child."""
        if self.scroll_tree is not None:
            return self.scroll_tree.viewport()
        tree = getattr(self, 'tree', None)  # Installed-app compact column.
        return tree.viewport() if tree is not None else self

    def _wheel_column_browse(self, event):
        """Browse the column physically under the wheel; never run an item.

        The remote's own wheel pad is separate and retains its Page-root-only
        one-level preview rule. Here the user has moved the mouse *into* a
        popup column, so that specific column is the navigation target.
        """
        if (not self.isVisible()
                or not getattr(self.launcher, 'pointer_warp_enabled', True)
                or event.modifiers() != Qt.KeyboardModifier.NoModifier
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return False
        surface = self._wheel_column_viewport()
        pointer = QCursor.pos()
        local = surface.mapFromGlobal(pointer)
        if not surface.rect().contains(local):
            return False
        if surface is self:
            # The per-column search editor and blank margins remain native.
            hovered = self.actionAt(local)
            if hovered is None or hovered is self.filter_action:
                return False

        angle = event.angleDelta().y()
        pixel = event.pixelDelta().y()
        if not angle and not pixel:
            return False
        # Every cascade column uses the same hybrid rule as Files:
        # native scrollbar movement first; only at the actual edge does the
        # current row move and the pointer follow. Never execute a row.
        scroll_tree = self.scroll_tree or getattr(self, 'tree', None)
        if scroll_tree is not None:
            bar = scroll_tree.verticalScrollBar()
            if (isinstance(bar.maximum(), (int, float)) and
                    isinstance(bar.minimum(), (int, float)) and
                    bar.maximum() > bar.minimum()):
                before = bar.value()
                distance = int(round(pixel if pixel else angle / 120 * 105))
                if distance:
                    bar.setValue(before - distance)
                if bar.value() != before:
                    self._column_wheel_remainder = 0
                    self._column_wheel_follow_pending = None
                    event.accept()
                    return True
                # A precise-wheel partial step away from the edge must not
                # change row selection or pointer position.
                row_direction = 1 if (angle or pixel) < 0 else -1
                if not can_follow_at_edge(before, bar.value(),
                                          bar.minimum(), bar.maximum(), row_direction):
                    event.accept()
                    return True
        self._column_wheel_remainder, steps = wheel_steps(
            self._column_wheel_remainder, angle, pixel)
        if steps:
            self.hover_timer.stop()
            self.folder_click_timer.stop()
            self._folder_click_action = None
            for _ in range(min(abs(steps), 5)):
                direction = 1 if steps > 0 else -1
                tree = getattr(self, 'tree', None)
                if tree is not None:
                    move_tree_selection(tree, direction)
                else:
                    self._move_filtered_selection(direction)
            remote_root = getattr(self.launcher, '_remote_page_menu', None)
            if self is remote_root:
                self.launcher._remote_page_wheel_expand(self)
            selected_action = (self._scroll_item_action(self.scroll_tree.currentItem())
                               if self.scroll_tree is not None else self.activeAction())
            self._schedule_column_wheel_follow(pointer, selected_action)
        event.accept()
        return True

    def _schedule_column_wheel_follow(self, original_pos, action):
        """Coalesce bursts and follow after Qt lays out/scrolls the new row."""
        self._column_wheel_follow_pending = (original_pos, action)
        if not self._column_wheel_follow_scheduled:
            self._column_wheel_follow_scheduled = True
            QTimer.singleShot(0, self._follow_column_wheel_pointer)

    def _follow_column_wheel_pointer(self):
        """Warp vertically inside the selected row, never across columns."""
        self._column_wheel_follow_scheduled = False
        pending = self._column_wheel_follow_pending
        self._column_wheel_follow_pending = None
        if (pending is None or not self.isVisible()
                or not getattr(self.launcher, 'pointer_warp_enabled', True)
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return
        original_pos, action = pending
        if (action is None or QCursor.pos() != original_pos):
            return
        if self.scroll_tree is not None:
            current_item = self.scroll_tree.currentItem()
            if current_item is None or self._scroll_item_action(current_item) is not action:
                return
        elif action is not self.activeAction():
            return  # The user moved the mouse, or the selection changed.
        surface = self._wheel_column_viewport()
        local = surface.mapFromGlobal(original_pos)
        if not surface.rect().contains(local):
            return  # Pointer moved to a different column / surface.
        if self.scroll_tree is not None:
            item = self.scroll_tree.currentItem()
            if item is None or self._scroll_item_action(item) is not action:
                return
            bounds = self.scroll_tree.visualItemRect(item)
        elif getattr(self, 'tree', None) is not None:
            item = self.tree.currentItem()
            if item is None:
                return
            bounds = self.tree.visualItemRect(item)
        else:
            bounds = self.actionGeometry(action)
        target = cursor_target((surface.width(), surface.height()),
                               (bounds.left(), bounds.top(), bounds.width(), bounds.height()),
                               local.x())
        if target is None:
            return
        destination = surface.mapToGlobal(QPoint(*target))
        if destination != original_pos:
            QCursor.setPos(destination)

    def wheelEvent(self, event):
        if not self._wheel_column_browse(event):
            super().wheelEvent(event)

    @staticmethod
    def _filesystem_row_path(row):
        if not isinstance(row, dict) or not row.get('_file'):
            return None
        return row['_file']

    def _transfer_state(self, row):
        path = self._filesystem_row_path(row)
        if path is None or self.launcher is None:
            return ''
        mime = QApplication.clipboard().mimeData()
        cut_paths = clipboard_sources(mime) if is_cut_clipboard(mime) else []
        # Paste feedback belongs only to this open folder column. A fresh
        # column never inherits the former column's teal highlight.
        pasted = getattr(self, '_pasted_feedback_paths', ())
        return transfer_state(path, cut_paths=cut_paths, pasted_paths=pasted)

    @staticmethod
    def _subdued_icon(source):
        image = source.pixmap(22, 22)
        if image.isNull():
            return source
        pix = QPixmap(image.size())
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setOpacity(0.38)
        painter.drawPixmap(0, 0, image)
        painter.end()
        return QIcon(pix)

    def _refresh_transfer_visuals(self):
        """Update cut/copy feedback without closing the folder menu."""
        actions = self._scroll_actions if self.scroll_tree is not None else self.actions()
        for action in actions:
            row = action.data()
            if not isinstance(row, dict):
                continue
            state = self._transfer_state(row)
            old = action.property('launch_transfer_state') or ''
            if old != state:
                if old == 'cut' and action.property('launch_original_icon') is not None:
                    action.setIcon(action.property('launch_original_icon'))
                if state == 'cut':
                    action.setProperty('launch_original_icon', action.icon())
                    action.setIcon(self._subdued_icon(action.icon()))
                action.setProperty('launch_transfer_state', state)
        if self.scroll_tree is not None:
            for index in range(self.scroll_tree.topLevelItemCount()):
                item = self.scroll_tree.topLevelItem(index)
                action = self._scroll_item_action(item)
                if action is None:
                    continue
                state = action.property('launch_transfer_state') or ''
                item.setIcon(0, action.icon())
                item.setBackground(0, QBrush(QColor('#d6f1e8') if state == 'pasted'
                                              else QColor(Qt.GlobalColor.transparent)))
                item.setForeground(0, QBrush(QColor('#9ca8af') if state == 'cut'
                                              else QColor('#173c38') if state == 'pasted'
                                              else QColor('#e5ebf3') if getattr(self.launcher, 'color_theme', 'dark') != 'light'
                                              else QColor('#26384a')))
            self.scroll_tree.viewport().update()
        self.update()

    def _on_clipboard_change(self):
        # A new copy/cut (including one in Explorer) supersedes the previous
        # paste result. The clipboard itself is left untouched.
        self._pasted_feedback_paths = ()
        self._update_paste_button()
        self._refresh_transfer_visuals()

    def handle_file_shortcut(self, key, modifiers):
        """File copy/cut/paste while a folder column, not its editor, owns focus."""
        if isinstance(self, AppCascadeMenu) or not (modifiers & Qt.KeyboardModifier.ControlModifier):
            return False
        if self.filter_edit is not None and self.filter_edit.hasFocus():
            # Native QLineEdit Ctrl+C/V/X must never be stolen.
            return False
        if key == Qt.Key.Key_V:
            if self._folder_container_row() is None:
                return False
            mime = QApplication.clipboard().mimeData()
            if clipboard_sources(mime) or is_virtual_file_clipboard(mime):
                self.launcher.paste_into_directory(self)
            return True
        if key not in (Qt.Key.Key_C, Qt.Key.Key_X):
            return False
        action = self.activeAction()
        row = action.data() if action is not None else None
        path = self._filesystem_row_path(row)
        if not path:
            return False
        kind = 'folder' if Path(path).is_dir() else 'file'
        self.launcher.perform_filesystem_context_action(
            'cut' if key == Qt.Key.Key_X else 'copy', path, kind)
        return True

    def _authored_context_row(self, row):
        # One menu can contain Studio-authored rows, physical files, and
        # virtual application/bookmark rows. Return only actionable targets.
        authored = getattr(self.launcher, 'authored_items', [])
        kind, _ = resolve_context_target(row, authored)
        if kind == 'studio':
            return authored_cascade_row(row, authored)
        if kind in ('file', 'folder'):
            return row
        return None

    def _right_click_row(self, event, source=None):
        """Resolve the item from the receiving menu/widget, never from the cursor."""
        if source is None or source is self:
            action = self.actionAt(event.position().toPoint())
            row = action.data() if action is not None else None
            if row is not None:
                # Right-clicking a previously unselected row must visibly
                # select *that* row, not leave the old keyboard row highlighted.
                setter = getattr(self, 'setActiveAction', None)
                if callable(setter):
                    setter(action)
        elif self.scroll_tree is not None and source is self.scroll_tree.viewport():
            item = self.scroll_tree.itemAt(event.position().toPoint())
            action = self._scroll_item_action(item)
            row = action.data() if action is not None else None
            if row is not None and hasattr(self.scroll_tree, 'setCurrentItem'):
                self.scroll_tree.setCurrentItem(item)
        elif (getattr(self, 'tree', None) is not None
              and source is self.tree.viewport()):
            item = self.tree.itemAt(event.position().toPoint())
            row = item.data(0, Qt.ItemDataRole.UserRole) if item is not None else None
            if row is not None and hasattr(self.tree, 'setCurrentItem'):
                self.tree.setCurrentItem(item)
        else:
            return None
        return self._authored_context_row(row)

    def _handle_right_click_properties(self, event, source=None):
        """Right mouse up on a contextual row opens its origin-specific menu.

        Defer popup creation until Qt has dispatched mouse release. Preserve
        the cascade tool column while the context menu is visible.
        """
        kind = event.type()
        if kind not in (QEvent.Type.MouseButtonPress,
                        QEvent.Type.MouseButtonRelease,
                        QEvent.Type.MouseButtonDblClick):
            return False
        if event.button() != Qt.MouseButton.RightButton:
            return False
        if kind == QEvent.Type.MouseButtonPress:
            self.hover_timer.stop()
            self._right_context_row = self._right_click_row(event, source)
            if self._right_context_row is not None:
                # A QMenu QAction does not retain ::item:selected when a
                # second popup takes focus; pin the hit during that popup.
                if source is None or source is self:
                    hit_test = getattr(self, 'actionAt', None)
                    if callable(hit_test) and hasattr(event, 'position'):
                        self._context_highlight_action = hit_test(event.position().toPoint())
                refresh = getattr(self, 'update', None)
                if callable(refresh):
                    refresh()
        elif kind == QEvent.Type.MouseButtonRelease:
            row = self._right_click_row(event, source)
            pressed = self._right_context_row
            self._right_context_row = None
            if (row is not None and pressed is not None
                    and row.get('item_id') == pressed.get('item_id')):
                pos = event.globalPosition().toPoint()
                QTimer.singleShot(0, lambda r=row, p=pos: self._open_context_properties(r, p))
        else:
            self._right_context_row = None
        event.accept()
        return True

    def _open_context_properties(self, row, pos):
        if self.launcher is None or not self.launcher.isVisible():
            return
        # Unlike a right-click on the main launcher, a right-click *inside*
        # the cascade must preserve its column and highlighted row.  Closing
        # the cascade here made only a detached Properties popup visible.
        # Parent the context menu to the source tool-window so it stacks above
        # the column; the origin resolver selects Studio or the OS actions.
        shown = self.launcher.show_launch_context_menu(pos, row, context_parent=self)
        context = getattr(self.launcher, '_launch_context_menu', None)
        clear = getattr(self, '_clear_context_highlight', None)
        if shown and context is not None and callable(clear):
            context.aboutToHide.connect(clear)
        elif callable(clear):
            clear()

    def _clear_context_highlight(self):
        action = self._context_highlight_action
        self._context_highlight_action = None
        if self.isVisible() and action is not None and action in self.actions():
            self.setActiveAction(action)
        self.update()

    @staticmethod
    def _consume_unused_right_click(event):
        """Keep right-clicks on generated/utility rows from dismissing menus.

        Editable authored rows are handled by _handle_right_click_properties
        first. This fallback swallows Qt native menu events and clicks on
        runtime-only items without affecting left-button actions.
        """
        if event.type() == QEvent.Type.ContextMenu:
            event.accept()
            return True
        if event.type() in (QEvent.Type.MouseButtonPress,
                            QEvent.Type.MouseButtonRelease,
                            QEvent.Type.MouseButtonDblClick):
            if event.button() == Qt.MouseButton.RightButton:
                event.accept()
                return True
        return False

    def event(self, event):
        # QMenu may close on a right-button press *or* release, even when no
        # context menu is configured.  Filter before QMenu.event dispatches it.
        if self._handle_right_click_properties(event, self):
            return True
        if self._consume_unused_right_click(event):
            return True
        return super().event(event)

    def select_first(self):
        if self.scroll_tree is not None:
            if self.scroll_tree.topLevelItemCount():
                item = next((self.scroll_tree.topLevelItem(i) for i in range(self.scroll_tree.topLevelItemCount())
                             if not self.scroll_tree.topLevelItem(i).isHidden()), None)
                self.scroll_tree.setCurrentItem(item)
            return
        first = next((a for a in self.actions()
                      if a.isVisible() and a.isEnabled() and isinstance(a.data(), dict)), None)
        self.setActiveAction(first)

    def _scroll_item_action(self, item):
        return item.data(0, Qt.ItemDataRole.UserRole) if item is not None else None

    def activeAction(self):
        if self.scroll_tree is not None:
            return self._scroll_item_action(self.scroll_tree.currentItem())
        return super().activeAction()

    def setActiveAction(self, action):
        if self.scroll_tree is not None:
            for index in range(self.scroll_tree.topLevelItemCount()):
                item = self.scroll_tree.topLevelItem(index)
                if self._scroll_item_action(item) is action:
                    self.scroll_tree.setCurrentItem(item)
                    return
            return
        super().setActiveAction(action)

    def actionAt(self, point):
        if self.scroll_tree is not None:
            viewport = self.scroll_tree.viewport()
            item = self.scroll_tree.itemAt(viewport.mapFrom(self, point))
            return self._scroll_item_action(item)
        return super().actionAt(point)

    def actionGeometry(self, action):
        if self.scroll_tree is not None:
            for index in range(self.scroll_tree.topLevelItemCount()):
                item = self.scroll_tree.topLevelItem(index)
                if self._scroll_item_action(item) is action:
                    rect = self.scroll_tree.visualItemRect(item)
                    return QRect(self.scroll_tree.viewport().mapTo(self, rect.topLeft()), rect.size())
        return super().actionGeometry(action)

    @staticmethod
    def _folder_row(action):
        row = action.data() if action is not None else None
        return row if isinstance(row, dict) and row.get('item_kind') == 'directory' else None

    def _double_folder_mode(self):
        # Remote Page cascades are navigation menus, not a file-manager view.
        # Even when the user chose double-click for Files, a Remote category
        # must expand on hover or one click (also in every nested column).
        return (not getattr(self, 'remote_page_navigation', False)
                and not getattr(self, 'compact_files_cascade', False)
                and not getattr(self, 'remote_folder_navigation', False)
                and not getattr(self, 'remote_context_root', False)
                and getattr(self.launcher, 'folder_open_mode', 'single') == 'double'
                and not getattr(self, 'bookmark_navigation', False))

    def _manual_bookmark_mode(self):
        return (not getattr(self, 'remote_page_navigation', False)
                and getattr(self, 'bookmark_navigation', False)
                and getattr(self.launcher, 'folder_open_mode', 'single') == 'double')

    def _navigable_folder_action(self, action):
        row = action.data() if action is not None else None
        return (action in self.openers and isinstance(row, dict)
                and row.get('item_kind') in ('directory', 'category'))

    def _folder_container_row(self):
        row = getattr(self, 'order_context', None)
        return row if isinstance(row, dict) and row.get('item_kind') == 'directory' else None

    def _queue_folder_single_click(self, action):
        self.hover_timer.stop()
        self._folder_click_action = action
        self.setActiveAction(action)
        # QMenu closes on a normal QAction mouse release; bypassing that
        # release and waiting for the double-click interval keeps the popup
        # alive for the second click.
        interval = QApplication.instance().doubleClickInterval()
        self.folder_click_timer.start(max(1, interval + 15))

    def _finish_folder_single_click(self):
        action = self._folder_click_action
        self._folder_click_action = None
        if action is None or not self.isVisible() or action not in self.openers:
            return
        if self.child and self.child.isVisible() and self.child.owner_action is action:
            # A hover expansion already opened this folder.
            self.child.open_mode = 'keyboard'
            self.child.outside_since = None
            return
        self.openers[action]('keyboard')

    def _open_folder_after_release(self):
        row = self._folder_double_click_row
        self._folder_double_click_row = None
        if row is not None:
            # The second mouse-up must reach Windows before a new Explorer
            # window is created (same foreground handoff rule as the launcher).
            QTimer.singleShot(0, lambda r=row: self.launcher.run_menu_item(r))

    def _scroll_activate(self, item):
        action = self._scroll_item_action(item)
        if action is None or not action.isEnabled():
            return
        if self._double_folder_mode() and self._navigable_folder_action(action):
            self.setActiveAction(action)  # Single click only selects.
        elif self._manual_bookmark_mode() and action in self.openers:
            self.openers[action]('keyboard')  # Bookmark: first click, no hover.
        elif self._folder_row(action) is not None:
            self._queue_folder_single_click(action)
        elif action in self.openers:
            self.openers[action]('keyboard')
        else:
            action.trigger()

    def _scroll_double_clicked(self, item, column):
        if self._manual_bookmark_mode():
            return  # A second click must not run a bookmark folder as a file.
        action = self._scroll_item_action(item)
        if self._double_folder_mode() and self._navigable_folder_action(action):
            self.folder_click_timer.stop()
            self._folder_click_action = None
            self.openers[action]('keyboard')
            return
        row = self._folder_row(action)
        if row is None:
            return
        self.folder_click_timer.stop()
        self._folder_click_action = None
        self._folder_double_click_row = row

    def _scroll_hover(self, item):
        if getattr(self, '_inline_rename_editor', None) is not None:
            # Moving over the input must not select a different row/open a child.
            self.hover_timer.stop()
            return
        if item is None:
            self.hover_timer.stop()
            return
        action = self._scroll_item_action(item)
        if action is self.activeAction():
            # The first row is selected when a popup appears, before the
            # pointer arrives.  Remote Page must still open it on hover.
            if (not (getattr(self, 'remote_page_navigation', False)
                      or getattr(self, 'remote_folder_navigation', False)
                      or getattr(self, 'remote_context_root', False)
                      or getattr(self, 'compact_files_cascade', False))
                    or action not in self.openers
                    or (self.child is not None and self.child.isVisible()
                        and self.child.owner_action is action)
                    or self.hover_timer.isActive()):
                return
        else:
            self.scroll_tree.setCurrentItem(item)
        # Do not immediately close a hover child when the pointer crosses a
        # neighbouring row on its way to the child column.  If the pointer
        # *settles* on another row, open_current replaces the child after the
        # ordinary hover delay; otherwise the existing child stays reachable.
        self.hover_timer.stop()
        if (action in self.openers and not self._manual_bookmark_mode()
                and not (self._double_folder_mode() and self._navigable_folder_action(action))):
            self.hover_timer.start(int(self.launcher.data.get('launch_hover_delay_ms', 250)))

    def _enable_scroll_tree(self, height):
        """Use a genuine Qt item-view scrollbar for oversized popup columns.

        QMenu's native scroll arrows are platform/style-dependent and can leave
        bottom actions below the Windows taskbar.  Only oversized columns use
        this alternative; compact menus remain the original QMenu entirely.
        """
        if self.scroll_tree is not None:
            return
        # The always-visible search bar is a separate QWidgetAction, not a
        # selectable row.  Keep it above the scrolling result list.
        original = [action for action in self.actions()
                    if action is not self.filter_action]
        if len(original) < 2:
            return
        original_width = self.sizeHint().width()
        self._scroll_actions = original
        for action in original:
            self.removeAction(action)  # Keep QAction objects and callbacks alive.
        tree = ExternalFileDragTree(
            self, row_resolver=lambda item: (
                self._scroll_item_action(item).data()
                if self._scroll_item_action(item) is not None else None))
        tree.setObjectName('cascadeScrollView')
        tree.setColumnCount(1)
        tree.setHeaderHidden(True)
        tree.setRootIsDecorated(False)
        tree.setMouseTracking(True)
        tree.setUniformRowHeights(True)
        tree.setIndentation(0)
        tree.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        tree.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        tree.verticalScrollBar().setSingleStep(34)
        tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        tree.setStyleSheet("""
            QTreeWidget#cascadeScrollView { background:#202b39; color:#e5ebf3;
                border:0; outline:0; padding:0; font-family:'Yu Gothic UI'; font-size:13px; }
            QTreeWidget#cascadeScrollView::item { height:32px; padding:0 6px; }
            QTreeWidget#cascadeScrollView::item:selected { background:#304d70; color:white; }
            QTreeWidget#cascadeScrollView::item:selected:!active { background:#304d70; color:white; }
            QTreeWidget#cascadeScrollView::item:hover { background:#34475d; }
        """)
        apply_scrollbar_theme(tree, '#202b39')
        for action in original:
            if action.isSeparator():
                continue
            item = QTreeWidgetItem([action.text()])
            item.setData(0, Qt.ItemDataRole.UserRole, action)
            item.setIcon(0, action.icon())
            item.setToolTip(0, action.toolTip() or action.text())
            if not action.isEnabled():
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            tree.addTopLevelItem(item)
        filter_height = (self.filter_action.defaultWidget().sizeHint().height()
                         if self.filter_action is not None else 0)
        tree.setFixedSize(max(200, min(self.maximumWidth() - 12, original_width)),
                          max(90, height - 22 - filter_height))
        tree.installEventFilter(self)
        tree.viewport().installEventFilter(self)
        tree.itemClicked.connect(self._scroll_activate)
        # itemActivated also fires on a mouse double-click, prematurely
        # expanding the submenu instead of launching the directory.
        tree.itemDoubleClicked.connect(self._scroll_double_clicked)
        tree.itemEntered.connect(self._scroll_hover)
        widget_action = QWidgetAction(self)
        widget_action.setDefaultWidget(tree)
        self.addAction(widget_action)
        self.scroll_tree = tree
        self._refresh_transfer_visuals()
        if self.launcher is not None and hasattr(self.launcher, 'style_cascade_menu'):
            self.launcher.style_cascade_menu(self)
        self._scroll_action = widget_action
        # Scrolling is a display adaptation, not a reordering operation.
        self.order_enabled = False

    def popup(self, pos, at=None):
        if not isinstance(self, AppCascadeMenu) and not self._transfer_data_changed_connected:
            QApplication.clipboard().dataChanged.connect(self._on_clipboard_change)
            self._transfer_data_changed_connected = True
        # All popup columns, including the installed-app catalog, share the
        # same full-height local search bar before their first paint/focus.
        if not getattr(self, 'remote_context_root', False):
            self._ensure_local_filter()
        if self.launcher is not None and hasattr(self.launcher, 'style_cascade_menu'):
            self.launcher.style_cascade_menu(self)
        screen = QApplication.screenAt(pos) or self.screen() or QApplication.primaryScreen()
        if screen is None:
            return super().popup(pos, at)
        rect = screen.availableGeometry()  # Excludes the Windows taskbar.
        popup_bounds = getattr(self, 'remote_popup_bounds', None)
        # Remote requests may extend below the monitor; always keep the real
        # usable screen (including taskbar exclusion) as the hard boundary.
        bound_top = popup_bounds[0] if popup_bounds is not None else rect.top()
        bound_bottom = popup_bounds[1] if popup_bounds is not None else (rect.bottom() + 1)
        bound_top = max(rect.top(), bound_top)
        bound_bottom = max(bound_top + 1, min(rect.bottom() + 1, bound_bottom))
        raw_height = self.sizeHint().height()
        # Some Qt styles pre-clamp QMenu.sizeHint() to a screen height even
        # though actions beyond that height cannot be reached reliably.
        # Count rows as well as checking Qt's own reported size.
        row_count = sum(1 for action in self.actions() if not action.isSeparator())
        estimated_height = row_count * max(32, self.fontMetrics().height() + 18) + 12
        requested_height = max(raw_height, estimated_height) if not isinstance(self, AppCascadeMenu) else raw_height
        placement = place_popup(pos.x(), pos.y(), self.sizeHint().width(), requested_height,
                                rect.left(), bound_top, rect.right()+1, bound_bottom)
        if placement.scroll and self.scroll_tree is None and not isinstance(self, AppCascadeMenu):
            self._enable_scroll_tree(placement.height)
            placement = place_popup(pos.x(), pos.y(), self.sizeHint().width(),
                                    self.sizeHint().height(), rect.left(), bound_top,
                                    rect.right()+1, bound_bottom)
        target = QPoint(placement.x, placement.y)
        self._refresh_transfer_visuals()
        return super().popup(target, at)

    def setFocus(self, reason=Qt.FocusReason.OtherFocusReason):
        if getattr(self, 'scroll_tree', None) is not None:
            self.scroll_tree.setFocus(reason)
        else:
            super().setFocus(reason)

    def _ensure_local_filter(self):
        """Install a permanently visible search bar for a folder/menu column."""
        if self.filter_action is not None:
            return
        # Lock the *minimum* frame size before QWidgetAction is inserted and
        # rows are hidden. Keep the result area visually stable (including 0
        # matches), without interfering with Qt's screen-height/scroll handling.
        self._filter_original_minimum = (self.minimumWidth(), self.minimumHeight())
        if self.isVisible():
            self.setMinimumSize(max(self.minimumWidth(), self.width()),
                                max(self.minimumHeight(), self.height()))
        container = QWidget(self)
        container.setObjectName('columnFilterBar')
        container.setStyleSheet("""
            QWidget#columnFilterBar { background: #26384a; border-radius: 5px; }
            QLineEdit { background: #111e2b; color: #e8f1fc; border: 1px solid #6995cb;
                        border-radius: 5px; padding: 5px 7px; font-size: 13px; }
            QLineEdit:focus { border-color: #85bbff; }
            QLabel { background: transparent; color: #9fb9d5; font-size: 11px; }
        """)
        # The Remote Browser bookmark root has one extra control directly
        # below search.  It is INSIDE the filter QWidgetAction, so long menus
        # keep both controls above their scrollable result tree.
        bookmark_root = getattr(self, 'remote_browser_bookmark_roots', False)
        layout = QVBoxLayout(container) if bookmark_root else QHBoxLayout(container)
        layout.setContentsMargins(7, 5, 7, 5)
        layout.setSpacing(5)
        search_row = QHBoxLayout() if bookmark_root else layout
        if bookmark_root:
            # The empty match counter still occupies two layout gaps before
            # the editor. Tighten only this row: move the editor's left edge
            # ~8px left while retaining the right-edge alignment with the
            # New tab / Current tab buttons and the centered 22px icon.
            search_row.setSpacing(1)
        if bookmark_root:
            # A proper magnifier rather than the tiny platform-font '⌕'.
            # Draw at 3x for crisp Windows / high-DPI rendering, then center
            # its 20px canvas in the 22px-wide whitespace left of the editor.
            icon_canvas = QPixmap(60, 60)
            icon_canvas.setDevicePixelRatio(3)
            icon_canvas.fill(Qt.GlobalColor.transparent)
            painter = QPainter(icon_canvas)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            color = '#648071' if theme_family(getattr(self.launcher, 'color_theme', 'light')) == 'light' else '#9fb9d5'
            outline = QPen(QColor(color), 1.6)
            outline.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(outline)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QRectF(2.8, 2.8, 10.5, 10.5))
            painter.drawLine(QPointF(12.2, 12.2), QPointF(17.3, 17.3))
            painter.end()
            glyph = QLabel(container)
            glyph.setPixmap(icon_canvas)
            glyph.setFixedSize(22, 30)
            glyph.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            glyph = QLabel('⌕', container)
        search_row.addWidget(glyph)
        self.filter_edit = QLineEdit(container)
        self.filter_edit.setPlaceholderText('この列から探す…')
        self.filter_edit.setClearButtonEnabled(True)
        self.filter_edit.setMinimumWidth(180)
        self.filter_edit.installEventFilter(self)
        self._filter_ime_composing = False
        search_row.addWidget(self.filter_edit, 1)
        # This button belongs ONLY to actual filesystem directories, never
        # Studio categories, bookmarks, apps or global search columns.
        if (self._folder_container_row() is not None
                and not getattr(self, 'remote_folder_navigation', False)):
            self.paste_button = QPushButton('貼り付け', container)
            self.paste_button.setObjectName('directoryPasteButton')
            self.paste_button.setToolTip('コピー／切り取りした項目を選択したフォルダーへ貼り付け')
            self.paste_button.setIcon(self._clipboard_paste_icon())
            self.paste_button.setIconSize(QSize(17, 17))
            self.paste_button.setFixedHeight(29)
            # Click must not strand keyboard focus on a tiny toolbar button:
            # Esc and clipboard keys should continue to reach the folder menu.
            self.paste_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.paste_button.setStyleSheet('''
                QPushButton#directoryPasteButton { background:#eaf5ff; color:#244964;
                    border:1px solid #89afcf; border-radius:5px; padding:2px 5px; font-size:11px; }
                QPushButton#directoryPasteButton:hover { background:#cee8ff; }
                QPushButton#directoryPasteButton:disabled { color:#879cab;
                    background:#eaf5ff; border-color:#89afcf; }
            ''')
            self.paste_button.clicked.connect(lambda checked=False: self.launcher.paste_into_directory(self))
            self._update_paste_button()
            search_row.addWidget(self.paste_button)
        self.filter_count = QLabel('', container)
        if bookmark_root:
            # The match counter used to sit AFTER the search edit. Even when
            # empty, Qt reserves two layout spacings on that side, leaving the
            # edit's right edge ~10px short of the tab-choice buttons below.
            # Place it before the edit instead: both right edges now share
            # the container's exact same right margin, with counts retained.
            search_row.insertWidget(1, self.filter_count)
        else:
            search_row.addWidget(self.filter_count)
        if bookmark_root:
            layout.addLayout(search_row)
            # Use full-width segmented choices instead of native radio dots.
            # On Windows the radio indicator was clipped/indistinct in this
            # ~230px popup, making the selected destination impossible to see.
            target_row = QHBoxLayout()
            target_row.setContentsMargins(0, 0, 0, 0)
            target_row.setSpacing(4)
            self.remote_bookmark_new_tab_button = QPushButton('新規タブ', container)
            self.remote_bookmark_current_tab_button = QPushButton('カレントタブ', container)
            for button in (self.remote_bookmark_new_tab_button,
                           self.remote_bookmark_current_tab_button):
                button.setObjectName('remoteBookmarkTabChoice')
                button.setCheckable(True)
                button.setFixedHeight(28)
                button.setMinimumWidth(0)
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                # Mouse selection must not steal the cascade's keyboard focus.
                button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.remote_bookmark_new_tab_button.clicked.connect(
                lambda _checked=False: self._select_remote_bookmark_tab(True))
            self.remote_bookmark_current_tab_button.clicked.connect(
                lambda _checked=False: self._select_remote_bookmark_tab(False))
            target_row.addWidget(self.remote_bookmark_new_tab_button, 1)
            target_row.addWidget(self.remote_bookmark_current_tab_button, 1)
            layout.addLayout(target_row)
            self._select_remote_bookmark_tab(True)  # Each opening defaults to new tab.
        action = QWidgetAction(self)
        action.setDefaultWidget(container)
        self.filter_action = action
        if self.launcher is not None and hasattr(self.launcher, 'style_cascade_menu'):
            self.launcher.style_cascade_menu(self)
        before = self.actions()[0] if self.actions() else None
        if before is not None:
            self.insertAction(before, action)
        else:
            self.addAction(action)
        if self.scroll_tree is not None:
            self._scroll_original_tree_height = self.scroll_tree.height()
            self.scroll_tree.setFixedHeight(max(120, self.scroll_tree.height() - 48))
        self._order_enabled_before_filter = self.order_enabled
        # An empty, visible search field must not disable normal row dragging.
        self.filter_edit.textChanged.connect(self._apply_local_filter)
        # popup/showEvent transfers the actual keyboard focus after display.

    def _select_remote_bookmark_tab(self, new_tab):
        """Make the chosen URL destination unmistakable in the compact menu."""
        self.remote_bookmark_new_tab = bool(new_tab)
        light = theme_family(getattr(self.launcher, 'color_theme', 'light')) == 'light'
        selected_bg = '#d6e7f8' if light else '#345d7a'
        selected_border = '#548fc8' if light else '#83bce4'
        selected_fg = '#173e60' if light else '#f1f8ff'
        idle_bg = '#f8fcfa' if light else '#263a35'
        idle_border = '#b6cfc1' if light else '#537468'
        idle_fg = '#3d6253' if light else '#b7cec3'
        for button, label, chosen in (
                (self.remote_bookmark_new_tab_button, '新規タブ', bool(new_tab)),
                (self.remote_bookmark_current_tab_button, 'カレントタブ', not new_tab)):
            button.setChecked(chosen)
            button.setText(('✓ ' if chosen else '') + label)
            button.setToolTip(('選択中：' if chosen else '切り替える：') + label)
            button.setStyleSheet(
                'QPushButton#remoteBookmarkTabChoice {'
                f'background:{selected_bg if chosen else idle_bg};'
                f'border:1px solid {selected_border if chosen else idle_border};'
                f'color:{selected_fg if chosen else idle_fg};'
                f'font-weight:{"bold" if chosen else "normal"};'
                'border-radius:6px;padding:1px 2px;font-size:12px;}'
                'QPushButton#remoteBookmarkTabChoice:hover {'
                f'border-color:{selected_border};}}')

    @staticmethod
    def _clipboard_paste_icon():
        # Tiny Explorer-like outlined clipboard; drawn locally, no font/icon
        # theme or Windows resource dependency (works in PyInstaller too).
        pix = QPixmap(24, 24)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor('#427ab1'), 1.5))
        painter.setBrush(QColor('#ffffff'))
        painter.drawRoundedRect(5, 5, 15, 17, 2, 2)
        painter.setBrush(QColor('#d4e7fb'))
        painter.drawRoundedRect(9, 2, 7, 5, 1, 1)
        painter.drawLine(8, 11, 17, 11)
        painter.drawLine(8, 15, 17, 15)
        painter.end()
        return QIcon(pix)

    def _update_paste_button(self):
        """An empty clipboard must not reserve space or advertise Paste."""
        button = self.paste_button
        if button is not None:
            mime = QApplication.clipboard().mimeData()
            available = bool(clipboard_sources(mime)) or is_virtual_file_clipboard(mime)
            button.setVisible(available)
            button.setEnabled(available)

    def _focus_initial_filter(self):
        """Start in the same keyboard mode that Tab selects from the search bar.

        The search bar stays visible, but the menu (or its scrollable item tree)
        owns initial keyboard focus.  Thus Right expands the highlighted row,
        while ordinary text and Japanese IME events still reach the column's
        search bar through keyPressEvent/inputMethodEvent.  Clicking the bar
        explicitly returns focus to QLineEdit for normal caret navigation.
        """
        editor = self.filter_edit
        if editor is None or not self.isVisible():
            return
        self.activateWindow()
        # Reproduce the already-working Tab-from-search focus destination.
        # CascadeMenu.setFocus() targets scroll_tree for oversized columns.
        self.setFocus(Qt.FocusReason.TabFocusReason)
        focus_target = (self.scroll_tree if self.scroll_tree is not None
                        else getattr(self, 'tree', None) or self)

        def initialize_once():
            if (self.filter_edit is not editor or not self.isVisible()
                    or not focus_target.hasFocus() or editor.text()
                    or getattr(self, '_filter_ime_composing', False)):
                return
            # Initialize the *actual* focused input window, not the unfocused
            # QLineEdit. Users remain free to switch to Japanese afterwards.
            initialize_halfwidth_english(int(focus_target.winId()))

        # Run once after native focus settles; never reset the IME per keystroke.
        QTimer.singleShot(0, initialize_once)

    def _restore_local_rows(self):
        """An empty query restores rows, but never removes the search bar."""
        if self.scroll_tree is not None:
            for index in range(self.scroll_tree.topLevelItemCount()):
                self.scroll_tree.topLevelItem(index).setHidden(False)
        else:
            for action in self.actions():
                if action is not self.filter_action:
                    action.setVisible(True)
        if self.filter_count is not None:
            self.filter_count.setText('')
        self.order_enabled = self._order_enabled_before_filter
        self.select_first()

    def _apply_local_filter(self, query):
        if not query:
            self._restore_local_rows()
            return
        # Only real search input promotes hover mode to keyboard mode and
        # disables drag-to-reorder for a filtered (possibly incomplete) list.
        ancestor = self
        while isinstance(ancestor, CascadeMenu):
            ancestor.open_mode = 'keyboard'
            ancestor.outside_since = None
            ancestor = ancestor.parentWidget()
        self.order_enabled = False
        shown = 0
        total = 0
        self.hover_timer.stop()
        if self.child:
            self.child.close()
        if self.scroll_tree is not None:
            total = self.scroll_tree.topLevelItemCount()
            for index in range(total):
                item = self.scroll_tree.topLevelItem(index)
                action = self._scroll_item_action(item)
                matches = isinstance(action.data(), dict) and column_filter_match(action.data(), query)
                item.setHidden(not matches)
                shown += bool(matches)
            if self.filter_count is not None:
                self.filter_count.setText(f'{shown}/{total}')
            self.select_first()
            return
        for action in self.actions():
            if action is self.filter_action:
                continue
            row = action.data()
            if isinstance(row, dict):
                total += 1
                visible = column_filter_match(row, query)
                shown += visible
                action.setVisible(visible)
            else:
                # Separators and utilities (e.g. 'open this folder') are not results.
                action.setVisible(False)
        if self.filter_count is not None:
            self.filter_count.setText(f'{shown}/{total}')
        self.select_first()

    def clear_local_filter(self):
        """Fully restore the original menu, including ordering and keyboard focus."""
        action = self.filter_action
        if action is None:
            return
        self.hover_timer.stop()
        # Release the temporary frame lock before returning the full list.
        # Never leave a fixed minimum on a reusable menu after Escape.
        if self._filter_original_minimum is not None:
            self.setMinimumSize(*self._filter_original_minimum)
            self._filter_original_minimum = None
        if self.scroll_tree is not None:
            for index in range(self.scroll_tree.topLevelItemCount()):
                self.scroll_tree.topLevelItem(index).setHidden(False)
            if self._scroll_original_tree_height is not None:
                self.scroll_tree.setFixedHeight(self._scroll_original_tree_height)
                self._scroll_original_tree_height = None
        for candidate in self.actions():
            if candidate is not action:
                candidate.setVisible(True)
        self.removeAction(action)
        action.deleteLater()
        self.filter_action = None
        self.filter_edit = None
        self.filter_count = None
        self.paste_button = None
        self._filter_ime_composing = False
        self.order_enabled = self._order_enabled_before_filter
        self.select_first()
        if self.isVisible():
            self.setFocus(Qt.FocusReason.OtherFocusReason)

    def _move_filtered_selection(self, increment):
        if self.scroll_tree is not None:
            move_tree_selection(self.scroll_tree, increment,
                                usable=lambda item: not item.isHidden()
                                and not item.isDisabled()
                                and self._scroll_item_action(item) is not None
                                and self._scroll_item_action(item).isEnabled())
            return
        matches = [a for a in self.actions()
                   if a is not self.filter_action and a.isVisible()
                   and a.isEnabled() and isinstance(a.data(), dict)]
        if not matches:
            self.setActiveAction(None)
            return
        current = self.activeAction()
        self.setActiveAction(next_wrapped(matches, current, increment))

    def eventFilter(self, obj, event):
        # A long folder/app list is a child widget of this QMenu.  Events
        # targeting its viewport bypass CascadeMenu.event(), so stop them
        # here too.  The small inline filter receives the same protection.
        right_click_child = (obj is getattr(self, 'filter_edit', None)
                             or (self.scroll_tree is not None and obj in (
                                 self.scroll_tree, self.scroll_tree.viewport()))
                             or (getattr(self, 'tree', None) is not None and obj in (
                                 self.tree, self.tree.viewport())))
        # Oversized cascade columns use a child QTreeWidget; its viewport
        # receives wheel events directly instead of CascadeMenu.wheelEvent.
        if (self.scroll_tree is not None
                and obj in (self.scroll_tree, self.scroll_tree.viewport())
                and event.type() == QEvent.Type.Wheel
                and self._wheel_column_browse(event)):
            return True
        if right_click_child and self._handle_right_click_properties(event, obj):
            return True
        if right_click_child and self._consume_unused_right_click(event):
            return True
        # Inline menu filters live inside a Qt popup and may bypass the main
        # window's QShortcut. F3 must still jump to the global search field.
        if (obj is getattr(self, 'filter_edit', None)
                and event.type() == QEvent.Type.KeyPress
                and event.key() == getattr(Qt.Key, 'Key_F3', None)
                and event.modifiers() == Qt.KeyboardModifier.NoModifier):
            self.launcher.focus_search()
            event.accept()
            return True
        if self.scroll_tree is not None and obj is self.scroll_tree:
            if event.type() == QEvent.Type.KeyPress:
                if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                    self._move_filtered_selection(1 if event.key() == Qt.Key.Key_Down else -1)
                    event.accept()
                    return True
                if event.key() in (Qt.Key.Key_Home, Qt.Key.Key_End,
                                   Qt.Key.Key_PageUp, Qt.Key.Key_PageDown):
                    return False  # Native page/home/end behavior is unchanged.
                self.keyPressEvent(event)
                return True
        if self.scroll_tree is not None and obj is self.scroll_tree.viewport():
            if (event.type() == QEvent.Type.MouseButtonDblClick
                    and event.button() == Qt.MouseButton.LeftButton
                    and self.scroll_tree.itemAt(event.position().toPoint()) is None
                    and self._folder_container_row() is not None):
                self.folder_click_timer.stop()
                self._folder_click_action = None
                self._folder_double_click_row = self._folder_container_row()
                event.accept()
                return True
            if (event.type() == QEvent.Type.MouseButtonRelease
                    and event.button() == Qt.MouseButton.LeftButton
                    and self._folder_double_click_row is not None):
                self._open_folder_after_release()
                event.accept()
                return True
            if (event.type() == QEvent.Type.MouseMove
                    and not event.buttons() & Qt.MouseButton.LeftButton):
                self._scroll_hover(self.scroll_tree.itemAt(event.position().toPoint()))
            return False
        if obj is self.filter_edit and event.type() == QEvent.Type.KeyPress:
            # A real QLineEdit must own its editing keys.  In particular,
            # Left/Right belong to caret movement and IME candidate selection,
            # not to cascade close/open.  Do not steal keys during pre-edit.
            key = event.key()
            if getattr(self, '_filter_ime_composing', False):
                return False
            if key == Qt.Key.Key_Escape:
                # First Esc clears the query; second Esc closes the column.
                self.keyPressEvent(event)
                event.accept()
                return True
            if key == Qt.Key.Key_Tab and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                # The menu still supports arrow-based folder navigation after
                # moving focus off the search editor with Tab.
                if self.scroll_tree is not None:
                    self.scroll_tree.setFocus(Qt.FocusReason.TabFocusReason)
                else:
                    super().setFocus(Qt.FocusReason.TabFocusReason)
                event.accept()
                return True
            if key in (Qt.Key.Key_Down, Qt.Key.Key_Up):
                self._move_filtered_selection(1 if key == Qt.Key.Key_Down else -1)
                event.accept()
                return True
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.keyPressEvent(event)
                event.accept()
                return True
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_F:
                self.keyPressEvent(event)
                event.accept()
                return True
        if obj is self.filter_edit and event.type() == QEvent.Type.InputMethod:
            # Leave the actual composition to Qt's QLineEdit, including
            # Japanese pre-edit text and candidate selection.
            self._filter_ime_composing = bool(event.preeditString())
            return False
        return super().eventFilter(obj, event)

    def _visible_route_action(self):
        """The folder row that leads into the currently visible right column.

        QMenu may clear its activeAction when the mouse/focus enters a child
        Tool window. The open-child relationship, not focus, defines the route.
        """
        if not (getattr(self, 'remote_folder_navigation', False)
                or getattr(self, 'remote_context_root', False)):
            return None
        child = getattr(self, 'child', None)
        return (getattr(child, 'owner_action', None)
                if child is not None and child.isVisible() else None)

    def _refresh_route_highlight(self):
        """Pin the route in both ordinary menus and tall scrolling columns."""
        route = self._visible_route_action()
        if self.scroll_tree is not None:
            light = theme_family(getattr(self.launcher, 'color_theme', 'light')) == 'light'
            shade = QBrush(QColor('#d6e7f8' if light else '#304d70'))
            for index in range(self.scroll_tree.topLevelItemCount()):
                item = self.scroll_tree.topLevelItem(index)
                should_pin = self._scroll_item_action(item) is route
                # Preserve unrelated item styling; clear only our own marker.
                was_pinned = bool(item.data(0, Qt.ItemDataRole.UserRole + 2))
                if should_pin != was_pinned:
                    item.setBackground(0, shade if should_pin else QBrush())
                    item.setData(0, Qt.ItemDataRole.UserRole + 2, should_pin)
            self.scroll_tree.viewport().update()
        self.update()

    def _refresh_parent_route_highlight(self):
        parent = self.parentWidget()
        if isinstance(parent, CascadeMenu):
            parent._refresh_route_highlight()

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_parent_route_highlight()
        self.select_first()
        if self.filter_edit is not None:
            # Keep the popup's frame stable as filtered QAction rows disappear.
            # The size is taken AFTER Qt's screen-placement/scroll adaptation.
            self.setMinimumSize(max(self.minimumWidth(), self.width()),
                                max(self.minimumHeight(), self.height()))
            QTimer.singleShot(0, self._focus_initial_filter)

    def hideEvent(self, event):
        self._column_wheel_follow_pending = None
        self._column_wheel_remainder = 0
        self.hover_timer.stop()
        self.folder_click_timer.stop()
        self._folder_click_action = None
        self._folder_double_click_row = None
        self._folder_double_click_action = None
        self._bookmark_ignore_double_release = False
        self._right_context_row = None
        self._context_highlight_action = None
        if self.child:self.child.close()
        super().hideEvent(event)
        self._refresh_parent_route_highlight()

    def order_surface(self):return self
    def order_rects(self):return [self.actionGeometry(a) for a in self.actions() if a.data()]
    def paintEvent(self,event):
        super().paintEvent(event)
        # Result markers deliberately differ from the currently selected row.
        # A pending cut uses Explorer-style subdued icon/text; confirmed paste
        # uses teal and a narrow left rail. Neither modifies file contents.
        if self.scroll_tree is None:
            painter = QPainter(self)
            for action in self.actions():
                state = action.property('launch_transfer_state')
                if state not in ('cut', 'pasted') or not action.isVisible():
                    continue
                rect = self.actionGeometry(action)
                if not rect.isValid():
                    continue
                if state == 'cut':
                    base = '#ffffff' if getattr(self.launcher, 'color_theme', 'dark') == 'light' else '#202b39'
                    shade = QColor(base); shade.setAlpha(156)
                    painter.fillRect(rect.adjusted(1, 1, -1, -1), shade)
                else:
                    painter.fillRect(rect.adjusted(1, 1, -1, -1), QColor(36, 177, 141, 55))
                    painter.fillRect(rect.adjusted(2, 2, -rect.width() + 6, -2), QColor('#16a57d'))
            painter.end()
        # Preserve the entire navigation route while its right-hand child is
        # visible. An ordinary QMenu drops :selected on focus transfer, even
        # though the previous column is deliberately kept on screen.
        route = self._visible_route_action()
        if route is not None and self.scroll_tree is None:
            rect = self.actionGeometry(route)
            if rect.isValid():
                light = theme_family(getattr(self.launcher, 'color_theme', 'light')) == 'light'
                painter = QPainter(self)
                # Translucent blue keeps Qt's existing icon/text/chevron legible.
                painter.fillRect(rect.adjusted(1, 1, -1, -1),
                                 QColor(76, 147, 224, 78 if light else 108))
                painter.end()
        # QAction selection in a QMenu can go inactive as soon as a second
        # context QMenu is shown.  Draw a light, non-opaque pinned highlight
        # so the user can always tell which row was right-clicked.
        action = self._context_highlight_action
        popup = getattr(self.launcher, '_launch_context_menu', None)
        if action is not None and (self._right_context_row is not None or
                                   (popup is not None and popup.isVisible())):
            rect = self.actionGeometry(action)
            if rect.isValid():
                painter = QPainter(self)
                painter.fillRect(rect.adjusted(2, 1, -2, -1), QColor(48, 77, 112, 90))
                painter.setPen(QPen(QColor('#779bc5'), 1))
                painter.drawRect(rect.adjusted(2, 1, -3, -2))
                painter.end()
        self.paint_order_line()
    def mousePressEvent(self,event):
        self.order_press=(event.position().toPoint(),self.actionAt(event.position().toPoint())) if event.button()==Qt.MouseButton.LeftButton else None
        # Clicking a result row transfers clipboard-key ownership away from
        # the inline search QLineEdit, even for short QAction-only columns.
        if (event.button() == Qt.MouseButton.LeftButton
                and self.order_press is not None
                and self.order_press[1] is not None
                and self.order_press[1] is not self.filter_action):
            self.setFocus(Qt.FocusReason.MouseFocusReason)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            action = self.actionAt(event.position().toPoint())
            if (getattr(self, 'remote_page_navigation', False)
                    or getattr(self, 'remote_context_root', False)
                    or getattr(self, 'remote_files_roots', False)) and action in self.openers:
                # Remote Page is a one-click navigation menu. A second click
                # must not launch a directory in Explorer or dismiss the menu.
                self._bookmark_ignore_double_release = True
                event.accept()
                return
            if self._manual_bookmark_mode() and action in self.openers:
                # Bookmark folders opened on the FIRST click in double mode.
                # The second click/release must not execute in Explorer or
                # close the parent QMenu before its submenu is shown.
                self._bookmark_ignore_double_release = True
                event.accept()
                return
            if self._double_folder_mode() and self._navigable_folder_action(action):
                self.folder_click_timer.stop()
                self._folder_click_action = None
                self._folder_double_click_action = action
                event.accept()
                return
            row = self._folder_row(action)
            if action is None:
                # Double-clicking unused space within a real folder popup
                # opens the currently displayed folder itself.
                row = self._folder_container_row()
            if row is not None:
                self.folder_click_timer.stop()
                self._folder_click_action = None
                self._folder_double_click_row = row
                event.accept()
                return
        super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self,event):
        action = self.actionAt(event.position().toPoint()) if event.button()==Qt.MouseButton.LeftButton else None
        press_action = self.order_press[1] if self.order_press is not None else None
        self.order_press = None
        if (event.button() == Qt.MouseButton.LeftButton
                and getattr(self, '_bookmark_ignore_double_release', False)):
            self._bookmark_ignore_double_release = False
            event.accept()
            return
        if (event.button() == Qt.MouseButton.LeftButton
                and self._folder_double_click_action is not None):
            chosen = self._folder_double_click_action
            self._folder_double_click_action = None
            if chosen in self.openers:
                self.openers[chosen]('keyboard')
            event.accept()
            return
        if event.button()==Qt.MouseButton.LeftButton and self._folder_double_click_row is not None:
            self._open_folder_after_release()
            event.accept()
            return
        if (action is press_action
                and (getattr(self, 'remote_page_navigation', False)
                     or getattr(self, 'remote_context_root', False)
                     or getattr(self, 'remote_files_roots', False))
                and action in self.openers):
            # A QAction release can cause QMenu to dismiss itself before the
            # child popup is shown. Open Remote Page folders explicitly and
            # consume that release; leave file execution / other modes alone.
            self.hover_timer.stop()
            self.setActiveAction(action)
            if getattr(self, 'remote_context_root', False):
                # The Remote's folder-list row is also an explicit Refresh.
                # Even if its child column is still on screen, a new click
                # must rebuild that column from the CURRENT Files breadcrumb.
                self.openers[action]('refresh')
            elif not (self.child is not None and self.child.isVisible()
                      and self.child.owner_action is action):
                self.openers[action]('keyboard')
            event.accept()
            return
        if (action is press_action and self._double_folder_mode()
                and self._navigable_folder_action(action)):
            self.setActiveAction(action)
            event.accept()  # Wait for second click; do not open a child.
            return
        if (action is press_action and action in self.openers
                and self._manual_bookmark_mode()):
            # Bookmark in double-click mode: first click opens immediately.
            # Do NOT let QMenu's QAction mouse release close the parent.
            self.hover_timer.stop()
            self.setActiveAction(action)
            self.openers[action]('keyboard')
            event.accept()
            return
        if (action is press_action and action in self.openers
                and self._folder_row(action) is not None):
            self._queue_folder_single_click(action)
            event.accept()
            return
        if action is None and press_action is None and self._folder_container_row() is not None:
            # A click on unused popup space is not an instruction to close.
            event.accept()
            return
        super().mouseReleaseEvent(event)
    def mouseMoveEvent(self, event):
        if getattr(self, '_inline_rename_editor', None) is not None:
            self.hover_timer.stop()
            event.accept()
            return
        if self.order_press and event.buttons() & Qt.MouseButton.LeftButton:
            pos, action = self.order_press
            if (event.position().toPoint() - pos).manhattanLength() >= QApplication.startDragDistance():
                row = action.data() if action else None
                if file_path_for_drag(row):
                    self.order_press = None
                    self.folder_click_timer.stop()
                    self.hover_timer.stop()
                    self.launcher.hover_timer.stop()
                    self.launcher.pending_menu_item = None
                    begin_file_copy_drag(self, row)
                    return
                if self.order_enabled:
                    self.order_press = None
                    self.begin_order_drag(row)
                    return
        before = self.activeAction()
        super().mouseMoveEvent(event)
        action = self.activeAction()
        remote_first_hover = ((getattr(self, 'remote_page_navigation', False)
                               or getattr(self, 'remote_folder_navigation', False)
                               or getattr(self, 'remote_context_root', False)
                               or getattr(self, 'compact_files_cascade', False))
                              and action in self.openers
                              and self.actionAt(event.position().toPoint()) is action
                              and not (self.child is not None and self.child.isVisible()
                                       and self.child.owner_action is action)
                              and not self.hover_timer.isActive())
        if action != before or remote_first_hover:
            if self.folder_click_timer.isActive():
                self.folder_click_timer.stop()
                self._folder_click_action = None
            # Switching rows is delayed; otherwise a diagonal move into an
            # already-open child closes that child before the pointer arrives.
            self.hover_timer.stop()
            action = self.activeAction()
            if (action in self.openers and not self._manual_bookmark_mode()
                    and not (self._double_folder_mode() and self._navigable_folder_action(action))):
                self.hover_timer.start(int(self.launcher.data.get('launch_hover_delay_ms',250)))

    def open_current(self, mode="keyboard"):
        if getattr(self, '_inline_rename_editor', None) is not None:
            return  # A pending hover timer can fire after the editor appears.
        action = self.activeAction()
        if mode=="hover" and self.actionAt(self.mapFromGlobal(QCursor.pos()))!=action:return
        if (mode == 'hover' and (self._manual_bookmark_mode() or
                (self._double_folder_mode() and self._navigable_folder_action(action)))):
            return  # In double mode, bookmark folders use click, not hover.
        if mode=="keyboard":
            m=self
            while isinstance(m,CascadeMenu):
                m.open_mode="keyboard";m.outside_since=None;m=m.parentWidget()
        if action in self.openers:self.openers[action](mode)

    def close_one_level(self):
        """Left/Esc: close only this column, then focus the precise opener.

        A nested cascade returns to the selected parent QAction.  A cascade
        opened from an expanded root button or panel row returns to that very
        widget, not to an unrelated bookmark panel.  Never collapse ancestors.
        """
        parent = self.parentWidget()
        source_widget = getattr(self, 'return_focus_widget', None)
        source_item = getattr(self, 'return_focus_item', None)
        owner_action = self.owner_action
        self.close()  # Closing a child must not close its parent column.
        if isinstance(parent, CascadeMenu):
            if parent.isVisible():
                if owner_action is not None:
                    parent.setActiveAction(owner_action)
                parent.setFocus(Qt.FocusReason.TabFocusReason)
        elif source_widget is not None and source_widget.isVisible():
            if source_item is not None and isinstance(source_widget, QTreeWidget):
                source_widget.setCurrentItem(source_item)
                source_widget.scrollToItem(source_item)
            source_widget.setFocus(Qt.FocusReason.TabFocusReason)
        elif (getattr(self.launcher, 'expanded_view', None) is not None
              and self.launcher.expanded_view.isVisible()):
            self.launcher.expanded_view.focus_root()
        elif self.launcher is not None:
            self.launcher.list.setFocus()

    def keyPressEvent(self, event):
        # A rename editor owns Enter (and every other key) until its edit is
        # fully finished. Never let the QAction behind it open a folder.
        if (getattr(self, '_inline_rename_editor', None) is not None or
                getattr(self, '_remote_rename_activation_guard', False)):
            event.accept()
            return
        if self.scroll_tree is not None and event.key() in (
                Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Home, Qt.Key.Key_End,
                Qt.Key.Key_PageUp, Qt.Key.Key_PageDown):
            QApplication.sendEvent(self.scroll_tree, event)
            return
        self.hover_timer.stop()
        key = event.key(); mods = event.modifiers()
        if key == getattr(Qt.Key, 'Key_F3', None) and mods == Qt.KeyboardModifier.NoModifier:
            self.launcher.focus_search()
            event.accept()
            return
        if getattr(self, 'handle_file_shortcut', lambda *args: False)(key, mods):
            event.accept()
            return
        if (key == getattr(Qt.Key, 'Key_Delete', None) and mods == Qt.KeyboardModifier.NoModifier
                and (self.filter_edit is None or not self.filter_edit.hasFocus())):
            action = self.activeAction()
            row = action.data() if action is not None else None
            path = self._filesystem_row_path(row)
            if path and Path(path).exists():
                kind = 'folder' if Path(path).is_dir() else 'file'
                self.launcher.perform_filesystem_context_action('delete', path, kind)
                event.accept()
                return
        # The editor is always present. Space is ordinary input, not a
        # special Japanese-IME trigger, and never switches the IME mode.
        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            # QMenu normally stops at its edges.  Use the shared wrap rule
            # for folder/bookmark cascades, including the "open folder" action.
            direction = 1 if key == Qt.Key.Key_Down else -1
            if self.filter_action is not None:
                self._move_filtered_selection(direction)
            else:
                actions = [a for a in self.actions()
                           if a.isVisible() and a.isEnabled() and not a.isSeparator()
                           and (isinstance(a.data(), dict)
                                or bool(a.property('launch_right_arrow_executes')))]
                self.setActiveAction(next_wrapped(actions, self.activeAction(), direction))
            event.accept()
            return
        if self.launcher.page_key(event):event.accept();return
        if (key == Qt.Key.Key_Escape and self.filter_edit is not None
                and self.filter_edit.text()):
            self.filter_edit.clear();event.accept();return
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Escape):
            if key == Qt.Key.Key_Escape and self.launcher is not None:
                self.launcher._cascade_dismiss_generation = (getattr(self.launcher, '_cascade_dismiss_generation', 0) + 1)
            self.close_one_level()
            event.accept();return
        action=self.activeAction()
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and action is not None and action.isEnabled():
            # QMenu's native Return handling works for real QAction rows, but
            # scrollable columns replace them with a QWidgetAction/QTreeWidget.
            # Trigger the actual selected row explicitly in *both* modes.
            row = action.data()
            if isinstance(row, dict) and row.get('item_kind') == 'directory':
                self.launcher.run_menu_item(row)
            elif action in self.openers:
                self.open_current()
            elif isinstance(row, dict):
                self.launcher.run_menu_item(row)
            elif action.property('launch_right_arrow_executes'):
                action.trigger()
            else:
                super().keyPressEvent(event)
            event.accept()
            return
        if key == Qt.Key.Key_Right:
            if action in self.openers:
                self.open_current();event.accept();return
            # Command-only actions (e.g. "このフォルダーを開く") have no row data.
            # They must be explicitly marked; never trigger arbitrary QWidgetActions.
            if (action is not None and action.isEnabled() and not action.isSeparator()
                    and action.property('launch_right_arrow_executes')):
                action.trigger();event.accept();return
            row = action.data() if action else None
            if isinstance(row, dict):
                self.launcher.run_menu_item(row);event.accept();return
        if (mods & Qt.KeyboardModifier.ControlModifier and key==Qt.Key.Key_F):
            self.launcher.focus_search();event.accept();return
        if key == Qt.Key.Key_Backspace and self.filter_edit is not None:
            self.filter_edit.backspace();event.accept();return
        # Typing while navigating an installed-app row searches ONLY this
        # column. Ctrl+F/F3 retain their explicit global-search shortcuts.
        # The real QLineEdit also retains native paste/caret/IME handling.
        if (event.text() and (event.text().isprintable() or event.text() == '\u3000')
                and not mods & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier)):
            self._ensure_local_filter()
            QApplication.sendEvent(self.filter_edit, QKeyEvent(event.type(),key,mods,event.text()))
            event.accept();return
        super().keyPressEvent(event)

    def inputMethodQuery(self, query):
        # A QMenu is not normally an IME text editor.  Advertise pre-edit
        # support while the inline QLineEdit is being created lazily so that
        # the very first Japanese conversion needn't start with an ASCII key.
        if query == Qt.InputMethodQuery.ImEnabled:
            return True
        if self.filter_edit is not None:
            return self.filter_edit.inputMethodQuery(query)
        return super().inputMethodQuery(query)

    def inputMethodEvent(self, event):
        # The same visible QLineEdit owns IME composition for both folder and
        # installed-app columns; never hand it to global search implicitly.
        self._ensure_local_filter()
        QApplication.sendEvent(self.filter_edit, event)
        event.accept()



class FilesPasteWorker(QThread):
    """Run filesystem copy/move off the GUI thread; never touch Qt widgets."""
    step = Signal(int, int, str)
    succeeded = Signal(int)
    failed = Signal(object)

    def __init__(self, plan, move, overwrite, parent=None):
        super().__init__(parent)
        self.plan = plan
        self.move = bool(move)
        self.overwrite = bool(overwrite)

    def run(self):
        try:
            count = paste_items(self.plan, move=self.move,
                                overwrite=self.overwrite,
                                progress=lambda *args: self.step.emit(*args))
        except Exception as exc:
            self.failed.emit(exc)
        else:
            self.succeeded.emit(count)


class FilesOperationProgress(QDialog):
    """Reusable, noncancelable progress display for filesystem operations.

    Keep native filesystem APIs on the GUI thread (especially Windows recycle
    bin); repaint safely only between individual operations. A single large
    file/dir may still occupy the UI until its filesystem call returns.
    """
    def __init__(self, parent, verb, total):
        super().__init__(parent)
        self.setWindowTitle('FRB Launch — 処理中')
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setMinimumWidth(360)
        self._total = max(1, int(total))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        self._verb = str(verb)
        self._spinner_frames = ('◐', '◓', '◑', '◒')
        self._spinner_index = 0
        self.heading = QLabel(f'{self._spinner_frames[0]}  {self._verb}しています…', self)
        self.heading.setStyleSheet('font-size:14px;font-weight:600;')
        layout.addWidget(self.heading)
        colors = theme_palette(getattr(parent, 'color_theme', 'light'))
        self.setStyleSheet(
            f'QDialog {{ background:{colors["panel"]};color:{colors["text"]}; }}'
            f'QLabel {{ color:{colors["text"]}; }}'
            f'QProgressBar {{ border:1px solid {colors["panel_border"]};'
            'border-radius:6px;height:16px;text-align:center; }}'
            'QProgressBar::chunk { background:#65b99b;border-radius:5px; }')
        self._spinner = QTimer(self)
        self._spinner.setInterval(120)
        self._spinner.timeout.connect(self._animate)
        self._spinner.start()
        self.detail = QLabel('準備中…', self)
        # A long filename must NEVER widen the dialog or wrap to two lines.
        # The per-file detail is always elided at the right edge.
        self.detail.setWordWrap(False)
        self.detail.setMinimumWidth(0)
        self.detail.setSizePolicy(QSizePolicy.Policy.Ignored,
                                  QSizePolicy.Policy.Fixed)
        self._detail_values = (0, self._total, '')
        layout.addWidget(self.detail)
        self.bar = QProgressBar(self)
        # Indeterminate animation for a single potentially massive directory.
        self.bar.setRange(0, 0 if self._total == 1 else self._total)
        self.bar.setValue(0)
        self.bar.setTextVisible(True)
        layout.addWidget(self.bar)

    def _update_detail_text(self):
        completed, total, name = self._detail_values
        prefix = f'{completed} / {total} 件'
        if name:
            prefix += ' — '
        fm = self.detail.fontMetrics()
        available = max(1, self.detail.width() - 4)
        remaining = max(1, available - fm.horizontalAdvance(prefix))
        shown = fm.elidedText(name, Qt.TextElideMode.ElideRight, remaining) if name else ''
        self.detail.setText(prefix + shown)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'detail') and hasattr(self, '_detail_values'):
            # Layout width settles after the initial show, and can change
            # with Windows DPI or a user resizing the dialog.
            QTimer.singleShot(0, self._update_detail_text)

    def _animate(self):
        self._spinner_index = (self._spinner_index + 1) % len(self._spinner_frames)
        self.heading.setText(f'{self._spinner_frames[self._spinner_index]}  {self._verb}しています…')

    def advance(self, completed, total, name=''):
        if int(total) == 1:
            if int(completed) >= 1:
                self.bar.setRange(0, 1)
                self.bar.setValue(1)
        else:
            self.bar.setMaximum(max(1, int(total)))
            self.bar.setValue(int(completed))
        self._detail_values = (completed, total, str(name or ''))
        self._update_detail_text()
        # Repaint/timers may run, but exclude new mouse/keyboard operations.
        QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)


class TimedStatusFooter(QLabel):
    """Transient Launch footer messages expire; navigation hints stay visible.

    All existing footer.setText call sites share this one policy. A newer
    message resets the timer, so an older expiration cannot erase it.
    """
    def __init__(self, text='', parent=None):
        super().__init__(text, parent)
        self._expiry = QTimer(self)
        self._expiry.setSingleShot(True)
        self._expiry.setInterval(10000)
        self._expiry.timeout.connect(self.clear)

    def setText(self, text):
        self._expiry.stop()
        super().setText(text)
        # The shortcut/help banner is a standing instruction, not a status.
        # Error markup, progress and success notices all time out equally.
        if text and not str(text).startswith(('↑↓', 'Launch外をクリックすると',
                                              '通常ウィンドウとして')):
            self._expiry.start()


def remote_new_arrow_qss(theme):
    """Draw native New submenu chevrons at the same 4x8 size as Files list.

    Qt's Windows QStyle draws the submenu primitive at its own size even if
    QMenu::right-arrow only sets width/height. Give it a real 4x8 bitmap.
    """
    resources = Path(getattr(sys, '_MEIPASS', ROOT)) / 'assets'
    name = ('remote_menu_chevron_light.png' if theme_family(theme) == 'light'
            else 'remote_menu_chevron_dark.png')
    path = (resources / name).as_posix()
    return (f'QMenu::right-arrow {{ image: url("{path}"); '
            'width: 4px; height: 8px; }}')


class RemoteFolderActionsMenu(CascadeMenu):
    """Use one compact arrow painter for both Remote folder submenus.

    On Windows QMenu's native ``新規作成`` submenu triangle ignores the CSS
    right-arrow size, while the virtual Files list uses a custom 4x8 marker.
    Cover ONLY the native indicator lane and paint both arrows with the same
    geometry. Keep the real QMenu submenu to retain its hover behavior.
    """

    def _close_files_preview_on_stable_other_action(self):
        """Close a Files preview only after hovering a *real* other command.

        The pointer may cross blank pixels or briefly pass over other rows
        while travelling diagonally from Filesリスト into its right-hand
        Tool columns. Neither may destroy the already-open preview.
        """
        if not self.isVisible() or getattr(self, 'child', None) is None:
            return
        local = self.mapFromGlobal(QCursor.pos())
        if not self.rect().contains(local):
            return  # Pointer already entered the child popup or passed the gap.
        action = self.actionAt(local)
        if (action is None or action is getattr(self, 'folder_list_action', None)
                or action is not getattr(self, '_non_files_hover_pending_action', None)
                or not action.isEnabled() or action.isSeparator()):
            return
        child = self.child
        self.child = None
        if getattr(self.launcher, '_remote_folder_root_menu', None) is child:
            self.launcher._remote_folder_root_menu = None
        child.close()
        child.deleteLater()

    def mouseMoveEvent(self, event):
        # The Files list is a hover preview. Dismiss it when the pointer
        # *settles* on a different executable action, not while travelling
        # across blank padding or other rows toward a right-hand column.
        action = self.actionAt(event.position().toPoint())
        timer = getattr(self, '_non_files_hover_timer', None)
        if (getattr(self, 'child', None) is not None
                and action is not None
                and action is not getattr(self, 'folder_list_action', None)
                and action.isEnabled() and not action.isSeparator()):
            if timer is None:
                timer = QTimer(self)
                timer.setSingleShot(True)
                timer.timeout.connect(self._close_files_preview_on_stable_other_action)
                self._non_files_hover_timer = timer
            if (not timer.isActive() or
                    action is not getattr(self, '_non_files_hover_pending_action', None)):
                self._non_files_hover_pending_action = action
                timer.start(350)
        else:
            if timer is not None:
                timer.stop()
            self._non_files_hover_pending_action = None
        super().mouseMoveEvent(event)

    def hideEvent(self, event):
        timer = getattr(self, '_non_files_hover_timer', None)
        if timer is not None:
            timer.stop()
        self._non_files_hover_pending_action = None
        super().hideEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        actions = (getattr(self, 'folder_list_action', None),
                   getattr(self, 'new_submenu_action', None))
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for action in actions:
            if action is None or action not in self.actions():
                continue
            rect = self.actionGeometry(action)
            if not rect.isValid():
                continue
            cx, cy = self.contentsRect().right() - 13, rect.center().y()
            selected = self.activeAction() is action
            if action is getattr(self, 'new_submenu_action', None):
                # Hide Qt's larger *native* submenu arrow. The whole patch is
                # inside the submenu indicator lane (not the text/icon area).
                # Match the row's selection/background theme before painting
                # this patch, without modifying QMenu's real submenu behavior.
                from PySide6.QtGui import QPalette
                background = (QColor('#d6e7f8') if selected and
                              theme_family(self.launcher.color_theme) == 'light'
                              else QColor('#ffffff') if
                              theme_family(self.launcher.color_theme) == 'light'
                              else self.palette().color(
                                  QPalette.ColorRole.Highlight if selected
                                  else QPalette.ColorRole.Window))
                painter.fillRect(QRect(cx - 9, rect.top() + 2,
                                       max(0, self.contentsRect().right() - cx + 9),
                                       max(0, rect.height() - 4)), background)
            arrow = QPainterPath()
            arrow.moveTo(cx - 2, cy - 4)
            arrow.lineTo(cx + 2, cy)
            arrow.lineTo(cx - 2, cy + 4)
            arrow.closeSubpath()
            color = (self.palette().highlightedText().color()
                     if selected else self.palette().text().color())
            painter.fillPath(arrow, color)
        painter.end()


class RemoteFolderCascade(CascadeMenu):
    """Remote filesystem columns reuse Compact's proven non-grabbing Tool menus.

    The only difference from an ordinary CascadeMenu is the *commit policy*:
    hover previews a folder, click commits its path to the Files breadcrumb,
    while a file needs a double-click to execute. Right-click delegates to
    the same safe context menu used by search results.
    """
    def __init__(self, parent=None, launcher=None):
        super().__init__(parent=parent, launcher=launcher)
        self.remote_folder_navigation = True
        self.compact_files_cascade = True  # Never apply Files-pane double-click mode.
        self.remote_folder_root = None
        self._remote_pressed_action = None
        self._remote_dbl_file = None

    def begin_inline_rename(self, target, kind):
        """Show a single-line editor ON the existing cascade item itself.

        Both normal QMenu rows and oversized scroll_tree rows use the same
        editor and commit policy. The surrounding cascade stays visible.
        """
        path = Path(target)
        if kind == 'folder' and not self.launcher.can_rename_remote_folder(path):
            return False
        if not (path.is_dir() if kind == 'folder' else path.is_file()):
            return False
        candidates = self._scroll_actions if self.scroll_tree is not None else self.actions()
        action = next((entry for entry in candidates
                       if ((row := self._remote_entry(entry)) is not None and
                           os.path.normcase(str(row.get('launch_browse_target')
                                               if kind == 'folder' else row.get('_browse_file') or
                                               row.get('_file', ''))) == os.path.normcase(str(path)))), None)
        if action is None:
            return False
        # Renaming owns this menu until Enter/Escape/focus loss. Freeze any
        # pending hover / folder-activation callbacks before showing QLineEdit.
        self.hover_timer.stop()
        self.folder_click_timer.stop()
        self._folder_click_action = None
        self._remote_pressed_action = None
        if self.child is not None:
            self.child.close()
            self.child.deleteLater()
            self.child = None
        previous = getattr(self, '_inline_rename_editor', None)
        if previous is not None:
            previous.deleteLater()
        tree_item = None
        if self.scroll_tree is not None:
            tree_item = next((self.scroll_tree.topLevelItem(i)
                              for i in range(self.scroll_tree.topLevelItemCount())
                              if self._scroll_item_action(self.scroll_tree.topLevelItem(i)) is action), None)
            if tree_item is None:
                return False
            self.scroll_tree.scrollToItem(tree_item)
            owner = self.scroll_tree.viewport()
            bounds = self.scroll_tree.visualItemRect(tree_item)
        else:
            owner = self
            bounds = self.actionGeometry(action)
        editor = QLineEdit(owner)
        editor.setObjectName('remoteCascadeRenameEditor')
        # This menu (including the scroll-tree adaptation) renders rows in
        # Yu Gothic UI 13px.  The app-wide QLineEdit rule is 15px, which was
        # the cause of the previous oversized rename-field regression.  Set
        # BOTH QFont and an ID-specific QSS rule to match the displayed row.
        row_font = QFont(self.font() if tree_item is None else self.scroll_tree.font())
        row_font.setFamily('Yu Gothic UI')
        row_font.setPixelSize(13)
        editor.setFont(row_font)
        editor.setStyleSheet('QLineEdit#remoteCascadeRenameEditor {'
                             "font-family:'Yu Gothic UI'; font-size:13px; "
                             'padding:0px 2px;}')
        # Keep the input inside the original row, after its folder/file icon.
        editor.setGeometry(bounds.adjusted(23, 2, -5, -2))
        editor.setText(path.name)
        editor.selectAll()
        editor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._inline_rename_editor = editor
        self._inline_rename_cancelled = False
        self._inline_rename_committing = False
        editor.installEventFilter(self)
        editor.editingFinished.connect(
            lambda e=editor, a=action, t=tree_item, p=str(path), k=kind:
            self._finish_inline_rename(e, a, t, p, k))
        editor._launch_finish_rename = lambda e=editor, a=action, t=tree_item, p=str(path), k=kind: (
            self._finish_inline_rename(e, a, t, p, k))
        editor.show()
        editor.raise_()
        editor.setFocus(Qt.FocusReason.OtherFocusReason)
        return True

    def _finish_inline_rename(self, editor, action, item, old_path, kind):
        if (getattr(self, '_inline_rename_editor', None) is not editor
                or getattr(self, '_inline_rename_committing', False)):
            return
        self._inline_rename_committing = True
        try:
            new_name = editor.text()
            cancelled = getattr(self, '_inline_rename_cancelled', False)
            if not cancelled and new_name != Path(old_path).name:
                try:
                    new_path = self.launcher.commit_remote_inline_rename(
                        old_path, new_name, kind)
                except (OSError, ValueError) as exc:
                    self.launcher.error('名前を変更できませんでした: ' + str(exc))
                else:
                    if new_path:
                        # fill_cascade() captures this dict in its folder opener.
                        # Mutate it IN PLACE: replacing QAction.data alone leaves
                        # the hover/open callbacks pointing at the deleted path.
                        row = action.data()
                        row['title'] = Path(new_path).name
                        row['description'] = new_path
                        row['item_id'] = str(new_path)
                        if kind == 'folder':
                            row['launch_browse_target'] = new_path
                        else:
                            row['_browse_file'] = new_path
                        if row.get('_file'):
                            row['_file'] = new_path
                        for entry in row.get('launch_actions', []):
                            if isinstance(entry, dict) and entry.get('launch_target') == old_path:
                                entry['launch_target'] = new_path
                        action.setData(row)
                        action.setText(Path(new_path).name)
                        action.setToolTip(new_path)
                        if item is not None:
                            item.setText(0, Path(new_path).name)
                            item.setToolTip(0, new_path)
                        if self.child is not None:
                            self.child.close()
                            self.child.deleteLater()
                            self.child = None
        finally:
            self._inline_rename_editor = None
            editor.deleteLater()
            self._inline_rename_committing = False
            # Enter/Escape ends the rename command; do not leave a floating
            # context menu (or its ancestor folder columns) behind.
            closer = getattr(self.launcher, 'close_finished_file_context_menus', None)
            if callable(closer):
                QTimer.singleShot(0, closer)

    def eventFilter(self, obj, event):
        if obj is getattr(self, '_inline_rename_editor', None):
            if (event.type() == QEvent.Type.KeyPress and
                    event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)):
                # Consume Enter here: otherwise the parent QMenu activates its
                # selected folder and opens Explorer after editingFinished.
                # A 0-ms guard also blocks already-queued folder activation.
                self._remote_rename_activation_guard = True
                editor = obj
                editor._launch_finish_rename()  # handled once; no Qt Enter propagation
                event.accept()
                QTimer.singleShot(0, lambda: setattr(
                    self, '_remote_rename_activation_guard', False))
                return True
            if (event.type() == QEvent.Type.KeyPress
                    and event.key() == Qt.Key.Key_Escape):
                self._inline_rename_cancelled = True
                self._finish_inline_rename(obj, None, None, '', 'file')
                event.accept()
                return True
            # QLineEdit handles Enter, IME, selection and clipboard natively.
        return super().eventFilter(obj, event)

    def _remote_entry(self, action):
        row = action.data() if action is not None else None
        if not isinstance(row, dict):
            return None
        if row.get('item_kind') not in ('directory', 'command'):
            return None
        # The user-authored Files first-column shortcuts are directory rows
        # but do not have _file. Keep native browser file rows unchanged.
        if row.get('_file') or (row.get('item_kind') == 'directory'
                                 and row.get('launch_browse_target')):
            return row
        return None

    def _remote_activate_file(self, row):
        """Open a Filesリスト leaf and dismiss the whole context cascade.

        Both QMenu rows and scroll-tree rows execute files through here.
        Closing on the NEXT event-loop tick keeps the double-click release
        intact and avoids destroying its Tool column inside mouse dispatch.
        Folder clicks are navigation only and must retain their menus.
        """
        filename = row.get('_browse_file')
        if not filename or not Path(filename).is_file():
            return
        try:
            self.launcher.activate(row)
        finally:
            closer = getattr(self.launcher, 'close_finished_file_context_menus', None)
            if callable(closer):
                QTimer.singleShot(0, closer)

    def _remote_commit_folder(self, row, action=None):
        if (getattr(self, '_remote_rename_activation_guard', False) or
                getattr(self, '_inline_rename_editor', None) is not None):
            return
        path = row.get('launch_browse_target')
        # Root shortcuts may contain %USERPROFILE%, unlike filesystem rows.
        if path and not Path(path).is_dir():
            path = self.launcher.expander().expand(path)
        view = self.launcher.expanded_view
        if not path or not Path(path).is_dir() or not view.isVisible() or view._workspace_mode != 'files':
            return
        root = self.remote_folder_root or self
        if getattr(self.launcher, '_remote_folder_root_menu', None) is not root:
            return
        self.launcher._remote_folder_navigation = True
        self.launcher._remote_folder_commit_pending = True
        try:
            if not view.go_to_directory(path, preserve_remote_popup=True):
                return
            # The clicked row MUST stay visible in its original column.
            # Previously the context-menu branch rebased/cleared that column,
            # destroying its child and causing the next list to disappear.
            # Instead open (or preserve) the clicked folder's RIGHT column,
            # exactly as the Files-button root already does.
            selected = action if action is not None else (
                self.activeAction() if hasattr(self, 'activeAction') else None)
            opener = getattr(self, 'openers', {}).get(selected)
            if opener is not None and not (self.child is not None
                    and self.child.owner_action is selected
                    and self.child.isVisible()):
                opener('keyboard')
            # Keep the parent context menu's explicit folder target fresh.
            # Otherwise clicking Filesリスト again would silently
            # reopen the originally right-clicked ancestor, not the breadcrumb.
            context = getattr(self.launcher, '_remote_folder_opener', None)
            if context is not None and getattr(context, 'remote_context_root', False):
                context.remote_target_directory = str(view.current_directory())
            self.launcher._remote_folder_source_path = os.path.normcase(
                os.path.normpath(str(view.current_directory())))
        finally:
            self.launcher._remote_folder_navigation = False
            self.launcher._remote_folder_commit_pending = False

    def _remote_rebase(self, directory):
        """Keep parent + first column on screen; rebuild only the contents."""
        self.hover_timer.stop()
        self.folder_click_timer.stop()
        if self.child is not None:
            self.child.close()
            self.child.deleteLater()
            self.child = None
        self.clear_local_filter()
        self.clear()
        self.openers.clear()
        row = self.launcher._remote_folder_context(directory)
        self.launcher.fill_cascade(self, row)
        self._ensure_local_filter()
        self.launcher._remote_folder_source_path = os.path.normcase(os.path.normpath(directory))
        self.select_first()
        self.adjustSize()
        self.update()

    def mousePressEvent(self, event):
        if (getattr(self, '_inline_rename_editor', None) is not None
                or getattr(self, '_remote_rename_activation_guard', False)):
            event.accept()  # The embedded QLineEdit owns clicks during edit.
            return
        if event.button() == Qt.MouseButton.LeftButton:
            action = self.actionAt(event.position().toPoint())
            if self._remote_entry(action) is not None:
                self.hover_timer.stop()
                self._remote_pressed_action = action
                self.setActiveAction(action)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if (getattr(self, '_inline_rename_editor', None) is not None
                or getattr(self, '_remote_rename_activation_guard', False)):
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            action = self.actionAt(event.position().toPoint())
            dbl = self._remote_dbl_file
            if dbl is not None:
                self._remote_dbl_file = None
                self._remote_pressed_action = None
                QTimer.singleShot(0, lambda r=dbl: self._remote_activate_file(r))
                event.accept()
                return
            if self._remote_pressed_action is not None:
                pressed = self._remote_pressed_action
                self._remote_pressed_action = None
                row = self._remote_entry(pressed)
                if pressed is action and row is not None and row['item_kind'] == 'directory':
                    QTimer.singleShot(0, lambda r=row, a=pressed: self._remote_commit_folder(r, a))
                # File single-click is selection only; do not dismiss menu.
                event.accept()
                return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            row = self._remote_entry(self.actionAt(event.position().toPoint()))
            if row is not None:
                self._remote_dbl_file = row if row['item_kind'] != 'directory' else None
                event.accept()
                return
        super().mouseDoubleClickEvent(event)

    def _scroll_activate(self, item):
        # Oversized menus route clicks to their QTreeWidget instead of QMenu.
        if (getattr(self, '_remote_rename_activation_guard', False) or
                getattr(self, '_inline_rename_editor', None) is not None):
            return
        action = self._scroll_item_action(item)
        row = self._remote_entry(action)
        if row is None:
            return super()._scroll_activate(item)
        self.setActiveAction(action)
        if row['item_kind'] == 'directory':
            QTimer.singleShot(0, lambda r=row, a=action: self._remote_commit_folder(r, a))

    def _scroll_double_clicked(self, item, column):
        row = self._remote_entry(self._scroll_item_action(item))
        if row is not None:
            if row['item_kind'] != 'directory':
                QTimer.singleShot(0, lambda r=row: self._remote_activate_file(r))
            return
        super()._scroll_double_clicked(item, column)

    def _open_context_properties(self, row, pos):
        # The safe global-search menu is the authoritative allowlist for both
        # files and folders. Unlike the old nested Qt.Popup, this Tool column
        # survives the second popup being shown and closed.
        if self.launcher is None or not self.launcher.isVisible():
            return
        shown = self.launcher.show_launch_context_menu(
            pos, row, context_parent=self, force_search_context=False)
        context = getattr(self.launcher, '_launch_context_menu', None)
        if shown and context is not None:
            context.aboutToHide.connect(self._clear_context_highlight)
        else:
            self._clear_context_highlight()


class AppCascadeMenu(CascadeMenu):
    """Large app catalogs use a real scrollable view instead of QMenu arrows."""
    def __init__(self, parent=None, launcher=None):
        super().__init__(parent=parent,launcher=launcher)
        self.order_enabled=False
        self.tree=QTreeWidget(self);self.tree.setColumnCount(2);self.tree.setHeaderHidden(True)
        self.tree.setRootIsDecorated(False);self.tree.setColumnWidth(0,220)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tree.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tree.verticalScrollBar().setSingleStep(35)
        apply_scrollbar_theme(self.tree)
        self.tree.setMinimumSize(440,280)
        height=min(490,max(280,QApplication.primaryScreen().availableGeometry().height()-120))
        self.tree.setFixedSize(440,height)
        self.tree.installEventFilter(self);self.tree.viewport().installEventFilter(self)
        self.widget_action=QWidgetAction(self);self.widget_action.setDefaultWidget(self.tree)
        self.addAction(self.widget_action)
        self.tree.itemActivated.connect(lambda item,col:self.launcher.run_menu_item(item.data(0,Qt.ItemDataRole.UserRole)))
        if self.launcher is not None and hasattr(self.launcher, 'style_cascade_menu'):
            self.launcher.style_cascade_menu(self)

    def setFocus(self, reason=Qt.FocusReason.OtherFocusReason):
        # The catalog is a QWidgetAction, so QMenu's own focus does not move
        # its QTreeWidget selection. The editor still owns focus when clicked.
        self.tree.setFocus(reason)

    def _apply_local_filter(self, query):
        # Filter the actual app tree, not QMenu actions (which only contain
        # the tree's QWidgetAction and the search bar).
        self.hover_timer.stop()
        if self.child:
            self.child.close()
        total = self.tree.topLevelItemCount()
        shown = 0
        for index in range(total):
            item = self.tree.topLevelItem(index)
            row = item.data(0, Qt.ItemDataRole.UserRole)
            matches = not query or (isinstance(row, dict)
                                    and column_filter_match(row, query))
            item.setHidden(not matches)
            shown += bool(matches)
        if self.filter_count is not None:
            self.filter_count.setText(f'{shown}/{total}' if query else '')
        self.select_first()

    def _restore_local_rows(self):
        self._apply_local_filter('')

    def _move_filtered_selection(self, increment):
        return move_tree_selection(self.tree, increment)

    def populate(self, rows):
        for row in rows:
            item=QTreeWidgetItem([row['title'],row.get('description','')])
            item.setData(0,Qt.ItemDataRole.UserRole,row)
            item.setIcon(0,self.launcher.row_icon(row));item.setToolTip(0,row['title'])
            item.setToolTip(1,str(row.get('description','')))
            action=QAction(self);action.setData(row);item.setData(0,Qt.ItemDataRole.UserRole+1,action)
            self.tree.addTopLevelItem(item)
        self.select_first()

    def select_first(self):
        # A no-results query must never leave a hidden, executable selection.
        for index in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(index)
            if not item.isHidden() and not item.isDisabled():
                self.tree.setCurrentItem(item)
                self.tree.scrollToItem(item)
                return
        self.tree.setCurrentItem(None)

    def activeAction(self):
        item=self.tree.currentItem() if hasattr(self,'tree') else None
        return item.data(0,Qt.ItemDataRole.UserRole+1) if item else None

    def eventFilter(self, obj, event):
        if obj==self.tree and event.type()==QEvent.Type.KeyPress:
            key=event.key()
            if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                move_tree_selection(self.tree, 1 if key == Qt.Key.Key_Down else -1)
                event.accept()
                return True
            if key in (Qt.Key.Key_PageUp,Qt.Key.Key_PageDown,Qt.Key.Key_Home,Qt.Key.Key_End):return False
            self.keyPressEvent(event);return True
        if obj==self.tree and event.type()==QEvent.Type.InputMethod:
            self.inputMethodEvent(event);return True
        if obj==self.tree.viewport() and event.type()==QEvent.Type.Wheel:
            # Follow the currently selected app row only in pointer-auto mode.
            # With pointer-auto OFF, retain the existing native scrolling.
            if self._wheel_column_browse(event):
                return True
            # Three rows per wheel notch; touchpads keep their pixel delta.
            pixels=event.pixelDelta().y()
            delta=pixels if pixels else event.angleDelta().y()/120*105
            bar=self.tree.verticalScrollBar();bar.setValue(bar.value()-round(delta))
            event.accept();return True
        return super().eventFilter(obj,event)

    def keyPressEvent(self, event):
        key=event.key()
        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            move_tree_selection(self.tree, 1 if key == Qt.Key.Key_Down else -1)
            event.accept()
            return
        if key in (Qt.Key.Key_PageUp,Qt.Key.Key_PageDown,Qt.Key.Key_Home,Qt.Key.Key_End):
            QApplication.sendEvent(self.tree,event);return
        if key in (Qt.Key.Key_Return,Qt.Key.Key_Enter,Qt.Key.Key_Right):
            item=self.tree.currentItem()
            if item:self.launcher.run_menu_item(item.data(0,Qt.ItemDataRole.UserRole))
            event.accept();return
        super().keyPressEvent(event)


class FileIndexSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class FrameEdgeCursorResetFilter(QObject):
    """Release a resize cursor when entering a child widget or leaving frame.

    Qt mouseMoveEvent on the top-level widget does not run while moving over
    embedded controls, so a parent-size cursor otherwise leaks to children.
    """
    def __init__(self, launcher):
        super().__init__(launcher)
        self.launcher = launcher

    def eventFilter(self, obj, event):
        launcher = self.launcher
        if not launcher.isVisible() or getattr(launcher, '_size_drag', None):
            return False
        if event.type() not in (QEvent.Type.MouseMove, QEvent.Type.Leave,
                                QEvent.Type.Enter, QEvent.Type.HoverMove,
                                QEvent.Type.HoverEnter):
            return False
        if launcher.cursor().shape() == Qt.CursorShape.ArrowCursor:
            return False
        # A true edge hover remains the resize zone. Child widget movement
        # must drop the sticky cursor inherited from the main frame.
        pos = launcher.mapFromGlobal(QCursor.pos())
        if not launcher.resize_edge(QPointF(pos)):
            launcher.unsetCursor()
        return False


class HistoryOutsideClickFilter(QObject):
    """Dismiss main search history when clicking anywhere else in the application.

    The history is a child QFrame (not a Qt.Popup), so Qt does not close it
    automatically. A launcher-local filter missed clicks in sibling widgets
    such as Files, bookmarks, the title bar and other toolbar buttons.
    Keep clicks *inside* the history or its search input, including native
    QLineEdit clear/chevron actions, untouched.
    """
    def __init__(self, launcher):
        super().__init__(launcher)
        self.launcher = launcher

    def eventFilter(self, obj, event):
        launcher = self.launcher
        if (event.type() != QEvent.Type.MouseButtonPress
                or not isinstance(obj, QWidget)
                or not getattr(launcher, 'history_popup', None)
                or not launcher.history_popup.isVisible()):
            return False
        # The remote is a separate Qt.Tool child window. Its mouse press
        # precedes WheelPad's release/ENTER command; closing the history here
        # would discard the selected row before the command can use it.
        # Treat the visible remote and its buttons/pad as part of the history
        # interaction, without disabling outside-click dismissal elsewhere.
        remote = getattr(launcher, 'remote_window', None)
        if (remote is not None and remote.isVisible()
                and (obj is remote or remote.isAncestorOf(obj))):
            return False
        # The Files-header magnifier follows Remote's two-click history
        # contract. Do not dismiss its history on the second mouse press.
        files_button = getattr(getattr(launcher, 'expanded_view', None),
                               'files_history_button', None)
        if files_button is not None and (obj is files_button or
                                         files_button.isAncestorOf(obj)):
            return False
        current = obj
        while isinstance(current, QObject):
            if current is launcher.history_popup or current is launcher.search:
                return False
            current = current.parent()
        launcher.hide_history_popup()
        # Preserve the click: page switching, folder navigation and all
        # command buttons must still work on their very first click.
        return False


class CascadeOutsideClickFilter(QObject):
    """Dismiss a visible tool-column when unrelated Launcher UI is clicked.

    The columns deliberately use Qt.Tool instead of Qt.Popup. Qt.Tool does
    not auto-dismiss on every outside click; application-wide mouse presses
    on unrelated *in-process* widgets need a separate, narrow event filter.
    Clicks in other applications are handled by the existing Windows mouse
    hook / application-deactivation path.
    """
    def __init__(self, launcher):
        super().__init__(launcher)
        self.launcher = launcher

    def eventFilter(self, obj, event):
        launcher = self.launcher
        # Ordinary Qt mouse presses (e.g. Files pane) also dismiss the Remote
        # filesystem preview.  A click inside the opener, nested Tool column,
        # or a file's own context menu must continue to work normally.
        if event.type() == QEvent.Type.MouseButtonPress and isinstance(obj, QWidget):
            opener = getattr(launcher, '_remote_folder_opener', None)
            root = getattr(launcher, '_remote_folder_root_menu', None)
            if opener is not None or root is not None:
                inside = False
                current = obj
                while isinstance(current, QObject):
                    if (current is opener or current is root
                            or (isinstance(current, CascadeMenu)
                                and getattr(current, 'remote_folder_navigation', False))):
                        inside = True
                        break
                    current = current.parent()
                context = getattr(launcher, '_launch_context_menu', None)
                if context is not None and context is not opener and context.isVisible():
                    inside = True  # File's secondary context menu.
                remote = getattr(launcher, 'remote_window', None)
                if (remote is not None and remote.isVisible()
                        and (obj is remote or remote.isAncestorOf(obj))):
                    # The Remote remains usable, but a press on ANY of its
                    # surfaces dismisses the old folder preview first.
                    # Never swallow the click: Page/Files/History must run.
                    launcher.close_remote_folder_menu()
                    inside = True
                if not inside:
                    launcher.close_remote_folder_menu()
        menu = getattr(launcher, 'menu', None)
        if menu is None or not menu.isVisible():
            return False
        context = getattr(launcher, '_launch_context_menu', None)
        if (getattr(launcher, '_filesystem_dialog_depth', 0)
                or QApplication.activeModalWidget() is not None
                or (context is not None and context.isVisible())):
            return False
        # After Delete, a modal dialog has stolen focus from the Qt.Tool
        # column. Make the very next Esc close that review, even if focus
        # remains on a main-window widget or the column search editor.
        if (event.type() == QEvent.Type.KeyPress
                and event.key() == Qt.Key.Key_Escape):
            column = menu
            while column is not None and column.child is not None and column.child.isVisible():
                column = column.child
            if getattr(column, '_delete_review_visible', False):
                current = obj
                while isinstance(current, QObject):
                    if current is launcher or isinstance(current, CascadeMenu):
                        launcher.close_cascade_for_main_interaction()
                        event.accept()
                        return True
                    current = current.parent()
            return False
        if event.type() != QEvent.Type.MouseButtonPress:
            return False
        # Clicking ANY Remote surface dismisses an already open Page column
        # (the Remote itself stays visible).  Do this on press so the native
        # button click on release can immediately open a replacement Page.
        remote = getattr(launcher, 'remote_window', None)
        if (remote is not None and remote.isVisible()
                and isinstance(obj, QWidget)
                and (obj is remote or remote.isAncestorOf(obj))):
            if getattr(launcher, '_remote_page_menu', None) is not None:
                launcher.close_remote_page_menu()
            return False
        current = obj
        while isinstance(current, QObject):
            if isinstance(current, CascadeMenu):
                return False  # The pointer is still inside a popup column.
            if current is launcher:
                launcher.close_cascade_for_main_interaction()
                break
            current = current.parent()
        return False  # Always deliver the user's original click.


from expanded_view_model import normalize_options, expanded_targets, should_expand
from expanded_view import ExpandedLauncherView
from focus_session import (normalize_focus_state, focus_area_for_reopen,
                           resolve_path_ids)
from expanded_keyboard_model import (tab_target, FOCUS_ORDER, WEB_FOCUS_ORDER, root_step, middle_back_target,
                                     row_right_action)
from remote_navigation import navigation_order, normalize_area


class NormalWindowClickActivationFilter(QObject):
    """An explicit click on a visible normal Launcher may regain foreground.

    The frameless window is sometimes exposed behind Chrome but stays
    keyboard-inactive. Do not swallow its click or touch the legacy Tool mode.
    Recheck foreground on the next event-loop turn so native Qt activation
    can win first; Win32 attachment is only a guarded fallback.
    """
    def __init__(self, launcher):
        super().__init__(launcher)
        self.launcher = launcher

    def eventFilter(self, obj, event):
        launcher = self.launcher
        if (event.type() != QEvent.Type.MouseButtonPress
                or not isinstance(obj, QWidget)
                or launcher.dismiss_on_outside_click
                or not launcher.isVisible() or launcher.isMinimized()
                or obj.window() is not launcher):
            return False
        hwnd = int(launcher.winId())
        before = windows.foreground()
        if before and before != hwnd:
            def on_explicit_click(fg=before):
                # The mouse press was physically delivered to this Launcher.
                # Repair Z-order even if Qt's frameless activation did not.
                launcher.restore_keyboard_focus(fg, reason='normal_window_click',
                                                restore_current=False)
                raised = windows.raise_normal_window(hwnd)
                DIAG.info('NORMAL_CLICK_ZORDER raised=%s foreground=%s',
                          raised, windows.foreground())
            QTimer.singleShot(0, on_explicit_click)
        return False


class Launcher(QWidget):
    CORNER_RADIUS = 10  # Main window corner radius in logical pixels.
    def __init__(self):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle('FRB Launch'); self.resize(390,440)
        self.setWindowIcon(application_icon())
        self.setMouseTracking(True)
        self.setMinimumHeight(240)
        self.setMinimumWidth(300)
        self.frame_title = QLabel('', self)
        self.frame_title.hide()
        self.app_records=installed_apps.read_cache(STATE/'apps_cache.json');self.apps_proc=None;self.apps_log=STATE/'apps.log'
        self.file_index_options_path = LAUNCH_HOME / 'config' / 'file_index_options.json'
        self.webview_settings = read_webview_settings(LAUNCH_HOME / 'config' / 'webview_settings.json')
        self.file_index_db = STATE / 'file_index.db'
        self.file_index_busy = False
        self._file_index_manual = False
        self._file_index_cancel = threading.Event()
        self.file_index_signals = FileIndexSignals(self)
        self.file_index_signals.finished.connect(self.file_index_finished)
        self.file_index_signals.failed.connect(self.file_index_failed)
        self.file_index_settings = file_index.load_options(self.file_index_options_path)
        self.apps_timer=QTimer(self);self.apps_timer.setInterval(150);self.apps_timer.timeout.connect(self.poll_apps)
        self.data = None; self.authored_items = []; self.mtime = None; self.config_size = None; self.target = 0; self.busy = False
        # A Qt item activation on double-click happens on the second DOWN.
        # Defer launching until its matching UP, otherwise Windows can revoke
        # the new GUI child's foreground permission on that last mouse input.
        self._pending_mouse_activation = None
        self._pending_mouse_foreground = None
        self._cloud_link_handoff = False
        self.stack = []; self.selection = None; self.checked = set(); self.return_page = None
        # None: deliberate picker from a Page. Query: a global-search hit
        # entered recipient selection and can return to global search.
        self._global_selection_query = None
        self._global_selection_choice_ids = None
        self.view_history = ViewNavigationHistory()
        self._nav_restoring = False
        self._nav_transition = False
        self._nav_search_timer = QTimer(self)
        self._nav_search_timer.setSingleShot(True)
        self._nav_search_timer.setInterval(600)
        self._nav_search_timer.timeout.connect(self._nav_flush_search)
        self.menu = None; self.pending_menu_item = None; self.file_icons = QFileIconProvider();self.icon_cache={}
        self.settings = QSettings(str(STATE / 'state.ini'), QSettings.Format.IniFormat)
        # The keyboard's last meaningful current is persisted when hidden.
        # Do not use QApplication.focusWidget() after losing foreground: Qt
        # may already have cleared it by the time app_state() calls dismiss().
        try:
            self._saved_focus_state = normalize_focus_state(
                json.loads(str(self.settings.value('last_current', '{}'))))
        except (ValueError, TypeError):
            self._saved_focus_state = {'area': 'search'}
        self._last_focus_area = None
        self._last_root_id = self._saved_focus_state.get('item_id') if self._saved_focus_state.get('area') == 'roots' else None
        self._restoring_last_focus = False
        self.color_theme = normalize_theme(self.settings.value('appearance_theme', 'dark'))
        # Preserve established behavior for existing installations.
        self.dismiss_on_outside_click = read_dismiss_on_outside(
            self.settings.value('dismiss_on_outside_click', 'true'))
        self.folder_open_mode = read_folder_open_mode(
            self.settings.value('folder_open_mode', 'single'))
        # Opt-in experiment: desktop double-click opens a pointer-side remote.
        self.remote_on_desktop_double_click = str(self.settings.value(
            'desktop_remote_enabled', 'false')).lower() in ('true', '1', 'yes', 'on')
        # UI-only A/B experiment: retain all Files/Bookmarks data and old
        # splitter widths; only disable their redundant visual/navigation lanes.
        self.files_root_hidden_mode = str(self.settings.value(
            'experiment_files_root_hidden', 'false')).strip().lower() in ('true', '1', 'yes', 'on')
        self.files_exp_embedded_mode = str(self.settings.value(
            'experiment_files_exp_embedded', 'false')).strip().lower() in ('true', '1', 'yes', 'on')
        if self.files_exp_embedded_mode:
            self.files_root_hidden_mode = True  # Remote operates column 2 only.
        self.remote_15_mode = str(self.settings.value(
            'experiment_remote_15_column', 'false')).strip().lower() in (
                'true', '1', 'yes', 'on')
        self._remote_15_alignment_pending = False
        self.remote_window = None
        self._remote_area = None
        # Sole operating target for the two Files columns. Search popups and
        # filesystem refreshes must NOT silently change this value.
        self._files_operating_target = 'directory'
        self._remote_popup_area = None
        # A retained launcher is a normal taskbar window, NOT an always-on-top Tool.
        # During construction nothing is visible, so changing flags is safe.
        self._apply_window_mode(initial=True)
        # Bookmarks now follows Launch's sole standard wheel behavior:
        # native Target Flow, then cursor-follow at a real scroll edge.
        # Obsolete bookmark-only A/B settings must not override that rule.
        self.bookmark_pointer_follow = True
        self.bookmark_wan_enabled = True
        for obsolete_key in ('bookmark_pointer_follow', 'bookmark_wan_enabled'):
            if self.settings.contains(obsolete_key):
                self.settings.remove(obsolete_key)
        self.settings.sync()
        # Citrix/VDI can show a server-side cursor distinct from the real
        # client pointer. Leave normal desktops unchanged unless opted in.
        self.vdi_no_cursor_warp = str(self.settings.value(
            'vdi_no_cursor_warp', 'false')).strip().lower() in ('true', '1', 'yes', 'on')
        self.pointer_warp_enabled = not self.vdi_no_cursor_warp
        # Search-only sort state; non-search lists keep their configured order
        # and drag-to-reorder behavior.  A value of -1 means unsorted.
        sort_col = str(self.settings.value('result_sort_column', -1))
        self.result_sort_column = int(sort_col) if sort_col in ('0', '1') else -1
        self.result_sort_desc = str(self.settings.value('result_sort_desc', 'false')).lower() in ('true', '1')
        self.page_id = self.settings.value('page', 'work')
        self.view_mode = str(self.settings.value('view_mode', 'classic')).lower()
        if self.view_mode not in ('classic', 'expanded'):
            self.view_mode = 'classic'
        self.expanded_options = self._read_expanded_options()
        self.bookmark_browser = str(self.settings.value('bookmark_browser', 'chrome')).lower()
        if self.bookmark_browser not in browser_bookmarks.BROWSERS:self.bookmark_browser = 'chrome'
        self.bookmark_signature = None
        self.bookmark_profiles = []
        self.bookmark_errors = []

        self.search_history = SearchHistory(STATE / 'search_history.json')
        self.session_history = SessionSearchHistory()  # RAM only, never persisted
        self.session_history_expanded = True
        self._session_edit_draft = None
        self._last_search_value = ''
        self._search_user_edit_pending = False
        self._live_search_timer = QTimer(self)
        self._live_search_timer.setSingleShot(True)
        self._live_search_timer.timeout.connect(self.render_settled_search)
        self._session_history_timer = QTimer(self)
        self._session_history_timer.setSingleShot(True)
        self._session_history_timer.setInterval(1650)
        self._session_history_timer.timeout.connect(self.record_session_search)
        self.search_categories = SearchHistoryCategories(
            STATE / 'search_history_categories.json', self.search_history.keywords)
        self.search = QLineEdit()
        self.search.setObjectName('mainSearchField')
        self.search.setPlaceholderText('アプリ・ファイル・ブックマークを検索…')
        self.search.setClearButtonEnabled(True)
        self.search.setMinimumHeight(36)
        self.search.setMaximumHeight(36)
        # Give narrow windows some flexibility. The Page strip has its own
        # bounded width and scroll buttons; do not force a 240px search field.
        self.search.setMinimumWidth(100)
        self.search.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # A child QToolButton retains an actual 28dp icon.  A leading
        # QLineEdit action gets silently reduced to 16dp by Windows/Qt.
        self.search_glyph = QToolButton(self.search)
        self.search_glyph.setObjectName('searchGlyph')
        self.search_glyph.setFixedSize(32, 32)
        self.search_glyph.setIconSize(QSize(28, 28))
        self.search_glyph.setIcon(toolbar_outline_icon('search', theme_family(self.color_theme)))
        self.search_glyph.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.search_glyph.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.search_glyph.setToolTip('全Pageから検索')
        # A small trailing chevron makes the '/' history shortcut discoverable.
        chevron = QPixmap(14, 14); chevron.fill(Qt.GlobalColor.transparent)
        painter = QPainter(chevron); painter.setPen(QPen(QColor('#7a9488' if self.color_theme == 'light' else '#a9bed2'), 1.7))
        painter.drawLine(3, 5, 7, 9); painter.drawLine(7, 9, 11, 5); painter.end()
        self.history_action = self.search.addAction(QIcon(chevron), QLineEdit.ActionPosition.TrailingPosition)
        self.history_action.setToolTip('検索履歴を表示 (/)')
        self.history_action.triggered.connect(self.toggle_history_popup)
        # Put category creation next to the magnifier, not at the far-right
        # edge of a wide search field. Keep the QAction for Remote/context
        # menus, which call its trigger() and read its icon().
        plus_icon = QPixmap(16, 16); plus_icon.fill(Qt.GlobalColor.transparent)
        plus_painter = QPainter(plus_icon)
        plus_painter.setPen(QPen(QColor('#608a76'), 2))
        plus_painter.drawLine(8, 3, 8, 13)
        plus_painter.drawLine(3, 8, 13, 8)
        plus_painter.end()
        self.history_category_action = QAction(
            QIcon(plus_icon), '検索履歴カテゴリーを追加', self.search)
        self.history_category_action.setToolTip('検索履歴カテゴリーを追加')
        self.history_category_action.triggered.connect(self.add_history_category)
        self.history_category_button = QToolButton(self.search)
        self.history_category_button.setObjectName('searchHistoryCategoryButton')
        self.history_category_button.setDefaultAction(self.history_category_action)
        self.history_category_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.history_category_button.setFixedSize(24, 28)
        self.history_category_button.setIconSize(QSize(16, 16))
        self.history_category_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.history_category_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # Unified, one-row header: brand / navigation / search / Page tabs /
        # settings / window controls. The old second toolbar row is removed.
        self.search_bar = QWidget(self)
        self.search_bar.setObjectName('searchBar')
        self.search_bar.setMinimumHeight(50)
        search_row = QHBoxLayout(self.search_bar)
        search_row.setContentsMargins(8, 3, 6, 3)
        search_row.setSpacing(6)

        self.brand_widget = QWidget(self.search_bar)
        self.brand_widget.setObjectName('brandWidget')
        brand_row = QHBoxLayout(self.brand_widget)
        brand_row.setContentsMargins(2, 0, 8, 0)
        brand_row.setSpacing(10)
        self.brand_icon_label = QLabel(self.brand_widget)
        self.brand_icon_label.setObjectName('brandIconLabel')
        self.brand_icon_label.setPixmap(brand_pixmap(30))
        self.brand_icon_label.setFixedSize(32, 32)
        self.brand_title_label = QLabel('FRB Launch', self.brand_widget)
        self.brand_title_label.setObjectName('brandTitleLabel')
        brand_row.addWidget(self.brand_icon_label)
        brand_row.addWidget(self.brand_title_label)
        search_row.addWidget(self.brand_widget, 0)
        search_row.addSpacing(4)
        search_row.addWidget(self.search, 1)

        self.theme_button = QPushButton('', self.search_bar)
        self.theme_button.setObjectName('headerSettingsButton')
        self.theme_button.setFixedSize(36, 36)
        self.theme_button.setIconSize(QSize(22, 22))
        self.theme_button.setToolTip('表示テーマを切り替え／Studioくんで設定')
        self.theme_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.theme_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_button.clicked.connect(self.open_theme_menu)
        search_row.addWidget(self.theme_button)

        self.header_divider = QFrame(self.search_bar)
        self.header_divider.setObjectName('headerDivider')
        self.header_divider.setFrameShape(QFrame.Shape.VLine)
        self.header_divider.setFixedHeight(28)
        search_row.addWidget(self.header_divider)

        # The minimize control only belongs to the normal-window (keep-visible) mode.
        self.minimize_button = QPushButton('', self.search_bar)
        self.maximize_button = QPushButton('', self.search_bar)
        self.close_button = QPushButton('', self.search_bar)
        for button, object_name, tip in (
            (self.minimize_button, 'windowFrameButton', '最小化'),
            (self.maximize_button, 'windowFrameButton', '最大化 / 元に戻す'),
            (self.close_button, 'windowCloseButton', '閉じる')):
            button.setObjectName(object_name)
            button.setFixedSize(32, 32)
            button.setIconSize(QSize(18, 18))
            button.setToolTip(tip)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            search_row.addWidget(button)
        self.minimize_button.clicked.connect(self.minimize_launcher)
        self.minimize_button.setVisible(not self.dismiss_on_outside_click)
        self.maximize_button.clicked.connect(self.toggle_maximize_restore)
        self.close_button.clicked.connect(self.dismiss)

        # Reuse the EXISTING header surface as a move handle; do not enlarge
        # the window or intercept the search edit, settings, or frame buttons.
        # The search_bar itself receives presses on its top/bottom whitespace,
        # and the decorative brand widgets receive presses on the title.
        self._passive_header_drag = PassiveHeaderDrag(self)
        for surface in (self.search_bar, self.brand_widget,
                        self.brand_icon_label, self.brand_title_label,
                        self.header_divider):
            surface.installEventFilter(self._passive_header_drag)

        # Browser-style view navigation is separate from ←/→ keyboard
        # shortcuts used by Page tabs, cascades and recipient selection.
        self.nav_toolbar = QWidget(self)
        self.nav_toolbar.setObjectName('navigationToolbar')
        nav_layout = QHBoxLayout(self.nav_toolbar)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(6)
        # Use real vector icons, never tiny platform-dependent Unicode glyphs.
        self.nav_back_button = QPushButton(self.nav_toolbar)
        self.nav_forward_button = QPushButton(self.nav_toolbar)
        self.nav_home_button = QPushButton(self.nav_toolbar)
        for button, name, tip in (
            (self.nav_back_button, 'navBackButton', '前の画面に戻る'),
            (self.nav_forward_button, 'navForwardButton', 'Filesのフォルダー履歴を進む'),
            (self.nav_home_button, 'navHomeButton', 'HOME：Files Expを全折りたたみ→先頭行を選択→第2列に表示')):
            button.setObjectName(name)
            button.setToolTip(tip)
            button.setFixedSize(40, 40)
            button.setIconSize(QSize(22, 22))
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            nav_layout.addWidget(button)
        self.nav_back_button.clicked.connect(self.navigate_back)
        self.nav_forward_button.clicked.connect(self.navigate_forward)
        self.nav_forward_button.hide()  # Visible only while Files Explorer is active.
        self.nav_home_button.clicked.connect(self.navigate_home)
        # Reuse the original navigation widget directly in the header.
        # Moving a widget between layouts preserves its signals and behavior.
        search_row.insertWidget(search_row.indexOf(self.search), self.nav_toolbar, 0)
        # Move settings next to HOME (left-side operation cluster).
        search_row.removeWidget(self.theme_button)
        nav_layout.addWidget(self.theme_button)
        # Inline overlay: left of QLineEdit's native clear (x) and history
        # chevron actions.  Never add it to search_row, which puts it OUTSIDE.
        self.save_history_button = QPushButton('履歴登録', self.search)
        self.save_history_button.setObjectName('saveHistoryButton')
        self.save_history_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_history_button.setToolTip('現在の検索文字列を履歴へ登録')
        self.save_history_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.save_history_button.setFixedSize(82, 26)
        self.save_history_button.hide()
        self.save_history_button.clicked.connect(lambda checked=False: self.remember_search())
        self.layout_search_inner_controls()
        self.theme_menu = QMenu(self)
        heading = self.theme_menu.addAction('外観テーマ')
        heading.setEnabled(False)
        self.theme_action_group = QActionGroup(self)
        self.theme_action_group.setExclusive(True)
        self.theme_actions = {}
        # Adding a new registered theme also creates its menu entry.
        for theme_id in available_themes():
            action = self.theme_menu.addAction(theme_palette(theme_id)['label'])
            action.setCheckable(True)
            self.theme_action_group.addAction(action)
            action.triggered.connect(lambda checked=False, key=theme_id: self.set_color_theme(key))
            self.theme_actions[theme_id] = action
        self.light_theme_action = self.theme_actions['light']
        self.dark_theme_action = self.theme_actions['dark']
        # The legacy Bookmarks-only follow/WAN toggles are retired.
        # A future all-area interaction mode selector can live here, but
        # Bookmarks is not treated as a special case anymore.
        self.theme_menu.addSeparator()
        self.vdi_no_cursor_warp_action = self.theme_menu.addAction(
            'Citrix / VDI互換：マウスポインター自動移動OFF')
        self.vdi_no_cursor_warp_action.setCheckable(True)
        self.vdi_no_cursor_warp_action.setChecked(self.vdi_no_cursor_warp)
        self.vdi_no_cursor_warp_action.setToolTip(
            '仮想デスクトップで二重カーソルが出る場合に使用。'
            'ホイール選択は維持、クリック位置は移動しません。')
        self.vdi_no_cursor_warp_action.triggered.connect(self.set_vdi_no_cursor_warp)
        self.theme_menu.addSeparator()
        outside_menu = self.theme_menu.addMenu('Launch外をクリックしたとき')
        self.outside_mode_group = QActionGroup(self)
        self.outside_mode_group.setExclusive(True)
        self.outside_mode_actions = {}
        for value, title in ((True, 'Launchを隠す（従来）'),
                             (False, 'Launchを表示したまま')):
            action = outside_menu.addAction(title)
            action.setCheckable(True)
            self.outside_mode_group.addAction(action)
            action.setChecked(self.dismiss_on_outside_click == value)
            action.triggered.connect(
                lambda checked=False, enabled=value: self.set_dismiss_on_outside_click(enabled))
            self.outside_mode_actions[value] = action
        folder_menu = self.theme_menu.addMenu('フォルダーを開くクリック操作')
        self.folder_mode_group = QActionGroup(self)
        self.folder_mode_group.setExclusive(True)
        self.folder_mode_actions = {}
        for value, title in (('single', 'シングルクリック（従来）'),
                             ('double', 'ダブルクリック')):
            action = folder_menu.addAction(title)
            action.setCheckable(True)
            action.setToolTip('Files第1列とブックマークはシングルクリックです。Files第2列のみ切替対象です。')
            self.folder_mode_group.addAction(action)
            action.setChecked(self.folder_open_mode == value)
            action.triggered.connect(
                lambda checked=False, mode=value: self.set_folder_open_mode(mode))
            self.folder_mode_actions[value] = action
        self.theme_menu.addSeparator()
        self.remote_mode_action = self.theme_menu.addAction(
            'デスクトップダブルクリックでリモコンを表示')
        self.remote_mode_action.setCheckable(True)
        self.remote_mode_action.setChecked(self.remote_on_desktop_double_click)
        self.remote_mode_action.triggered.connect(self.set_desktop_remote_enabled)
        self.files_root_hidden_action = self.theme_menu.addAction('実験：Files ルート非表示')
        self.files_root_hidden_action.setCheckable(True)
        self.files_root_hidden_action.setChecked(self.files_root_hidden_mode)
        self.files_root_hidden_action.setToolTip(
            'Files第1列・Browserブックマーク列・リモコンTab/BackTabを隠す。'
            'Filesは第2列固定。チェック解除で元に戻せます。')
        self.files_root_hidden_action.triggered.connect(self.set_files_root_hidden_mode)
        self.files_exp_embedded_action = self.theme_menu.addAction(
            '実験：Files Expを第1列に表示')
        self.files_exp_embedded_action.setCheckable(True)
        self.files_exp_embedded_action.setChecked(self.files_exp_embedded_mode)
        self.files_exp_embedded_action.setToolTip(
            '従来の第1列は残したままFiles Expのツリーを組み込む。'
            'Remoteは第2列操作を維持し、単独のFiles Expウィンドウを表示しません。')
        self.files_exp_embedded_action.triggered.connect(self.set_files_exp_embedded_mode)
        self.remote_15_action = self.theme_menu.addAction(
            '実験：リモコンウィンドウ 1.5列表示')
        self.remote_15_action.setCheckable(True)
        self.remote_15_action.setChecked(self.remote_15_mode)
        self.remote_15_action.setToolTip(
            'Filesの第1列と第2列の間に配置場所を確保し、別WindowのRemoteを前面に表示します。'
            'Remoteの検索結果選択・実行は従来のままです。')
        self.remote_15_action.triggered.connect(self.set_remote_15_mode)
        self.files_root_hidden_action.setChecked(
            self.files_root_hidden_mode and not self.files_exp_embedded_mode)
        self.theme_menu.addSeparator()
        self.compact_mode_action = self.theme_menu.addAction('Compact表示へ切り替え')
        self.compact_mode_action.setToolTip('Compact表示とFiles／Browser表示を切り替え')
        self.compact_mode_action.triggered.connect(self.toggle_expanded_view)
        self.theme_menu.addSeparator()
        self.theme_studio_action = self.theme_menu.addAction('メニュー設定 (FRB Studio)')
        self.theme_studio_action.triggered.connect(
            lambda checked=False: self.launch_configuration_studio(page_properties=True))
        self.tabs = FocusPageTabBar(); self.tabs.setExpanding(False); self.tabs.setDrawBase(False)
        # Non-grabbing folder columns sometimes leave native keyboard focus on
        # the Page tabs; it must still be possible to start an IME composition.
        self.tabs.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        # Apply full tab styles (including *unselected* tabs) so Windows does
        # not fall back to the legacy beveled/3D native QTabBar appearance.
        self.tabs.setStyleSheet(PAGE_TABS_QSS)
        self.tabs.setUsesScrollButtons(True)
        # To the RIGHT of search, BEFORE settings. Tabs remain the same
        # FocusPageTabBar (keyboard, wheel, and Page events are preserved).
        search_row.insertWidget(search_row.indexOf(self.header_divider), self.tabs, 0)
        # A narrow Compact window cannot physically contain three Page tabs,
        # the search field and all controls on ONE row. Show a small Page menu
        # in that situation, retaining the three real tabs when space permits.
        self.page_overflow_button = QPushButton('Page ▾', self.search_bar)
        self.page_overflow_button.setObjectName('headerPageOverflow')
        self.page_overflow_button.setFixedHeight(34)
        self.page_overflow_button.setFixedWidth(72)
        self.page_overflow_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.page_overflow_button.clicked.connect(self.open_header_page_menu)
        self.page_overflow_button.hide()
        search_row.insertWidget(search_row.indexOf(self.header_divider), self.page_overflow_button, 0)
        self.list = ReorderTree(self); self.list.setObjectName('mainLaunchList'); self.list.setColumnCount(2); self.list.setHeaderHidden(True); self.list.setRootIsDecorated(False)
        self.list.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        self.list.setHeaderLabels(['タイトル', '説明・場所'])
        header = self.list.header()
        header.setSectionsMovable(False)
        header.setStretchLastSection(False)  # both columns must be user-resizable
        header.setMinimumSectionSize(70)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setToolTip('境界をドラッグ：列幅変更 / 見出しクリック：昇順・降順')
        # QTreeView.setSortingEnabled(False) ALSO disables header clicks.
        # Enable clickable sections AFTER it, then sort our search pairs only.
        # Native Qt sorting must stay disabled to preserve manual menu order.
        self.list.setSortingEnabled(False)
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(False)
        self.list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel);self.list.verticalScrollBar().setSingleStep(35)
        # The same QTreeWidget serves two modes, but widths are independent.
        # No visible header is needed to resize the main menu's first column.
        self._column_mode = None
        self._applying_column_layout = False
        self._main_width_drag = None
        self._main_column_hover = False
        header.sectionClicked.connect(self.sort_search_column)
        header.sectionResized.connect(self.save_result_column_width)
        self.list.setMouseTracking(True); self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.footer = TimedStatusFooter('↑↓ 選択   → 展開   ← 戻る   Enter 実行   Esc 閉じる')
        self.files_item_count = QLabel('')
        self.files_item_count.setObjectName('filesItemCount')
        self.files_item_count.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.files_item_count.setToolTip('表示中の項目数と選択項目のサイズ合計。フォルダー内のサイズは含みません')
        self.files_item_count.hide()
        self.footer_row = QWidget(self)
        self.footer_row.setObjectName('launchFooterRow')
        footer_layout = QHBoxLayout(self.footer_row)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(8)
        footer_layout.addWidget(self.files_item_count, 0)
        footer_layout.addWidget(self.footer, 1)
        # The title header must reach the frame's inner edges.  Keep the
        # original 12px inset for all content below it, but not the header.
        layout = QVBoxLayout(self); layout.setContentsMargins(6,8,6,12); layout.setSpacing(0)
        self.main_body = QWidget(self)
        self.main_body.setObjectName('mainBody')
        body_layout = QVBoxLayout(self.main_body)
        body_layout.setContentsMargins(6, 0, 6, 0)
        body_layout.setSpacing(8)
        self.selection_tools = QWidget()
        buttons = QHBoxLayout(self.selection_tools); buttons.setContentsMargins(0,0,0,0)
        for title, callback in [('全選択 (Ctrl+A)', lambda:self.select_all(True)), ('全解除 (Ctrl+Shift+A)', lambda:self.select_all(False)), ('戻る (←)', self.go_back)]:
            button = QPushButton(title); button.clicked.connect(callback); buttons.addWidget(button)
        buttons.addStretch()
        self.selection_tools.hide()
        # Retain the old mode action widget internally for compatibility with
        # established callers; the user-facing control is now in settings.
        # Neither the old Page bar nor the mode button occupies screen height.
        self.mode_bar = QWidget(self)
        self.mode_bar.setObjectName('pageBar')
        self.mode_button = QPushButton('Three-layer', self.mode_bar)
        self.mode_button.setObjectName('expandedModeButton')
        self.mode_button.setIconSize(QSize(22, 22))
        self.mode_button.setToolTip('CompactとFiles／Browserを切り替え')
        self.mode_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.mode_button.clicked.connect(self.toggle_expanded_view)
        self.mode_bar.hide()
        self.expanded_view = ExpandedLauncherView(self)
        # The view is now fully attached; apply the restored experiment state.
        self.expanded_view.apply_files_root_hidden_mode()
        # A single clipboard drives cut visuals in the main Files columns,
        # the Remote cascade, and the companion Files Exp tree.
        QApplication.clipboard().dataChanged.connect(self.refresh_main_files_cut_visuals)
        # Allow dragging from the workspace-strip whitespace as well.
        # Only background surfaces receive the filter; the actual Files /
        # Browser buttons and authored root buttons keep their clicks.
        for surface in (self.expanded_view.root_widget,
                        self.expanded_view.toolbar_scroller,
                        self.expanded_view.toolbar_scroller.viewport()):
            surface.installEventFilter(self._passive_header_drag)
        # Wheel Tab: share one cooldown across Page, toolbar and Files panels.
        self.tabs._zone_navigation = self.expanded_view.wheel_zone_navigation
        self.tabs._zone_enabled = lambda: self.view_mode == 'expanded'
        self.tabs._pointer_warp_enabled = lambda: self.pointer_warp_enabled
        self.expanded_view.hide()
        layout.addWidget(self.search_bar)
        for w in (self.selection_tools, self.list,
                  self.expanded_view, self.footer_row):
            body_layout.addWidget(w)
        layout.addWidget(self.main_body, 1)
        self._dark_main_qss = '''QWidget{background:#202b29;color:#e5ebf3;font-family:"Yu Gothic UI";font-size:13px;} QLineEdit{background:#101720;border:1px solid #40536d;border-radius:7px;padding:5px 10px;font-size:15px;} QTreeWidget{border:0;outline:0;background:#202b29;} QTreeWidget::item{height:35px;padding:0 6px;} QTreeWidget::item:selected{background:#304d70;color:white;} QTreeWidget::item:selected:!active{background:#304d70;color:white;} QTreeWidget#mainLaunchList::item:selected{background:transparent;color:#e5ebf3;} QTreeWidget#mainLaunchList::item:hover{background:transparent;} QHeaderView::section{background:#2c3d49;color:#e5ebf3;border:0;border-right:1px solid #526377;border-bottom:1px solid #526377;padding:3px 8px;} QHeaderView::section:hover{background:#385268;} QLabel{color:#8d9caf;font-size:11px;} QMenu{background:#202b39;border:1px solid #435369;padding:5px;} QMenu::item{padding:8px 20px;} QMenu::item:selected{background:#304d70;} QAbstractScrollArea::corner{background:#202b29;border:0;}'''
        # Search mode may show both scroll axes.  Keep their look consistent
        # with the slim cascade scrollbar; do not change their policies or sorting.
        self.list.verticalScrollBar().setStyleSheet(MAIN_LIST_SCROLLBAR_QSS)
        self.list.horizontalScrollBar().setStyleSheet(MAIN_LIST_SCROLLBAR_QSS)
        # Child overlay: no separate top-level Popup window and no Windows
        # focus handoff, which is important for this frameless Tool launcher.
        self.history_popup = QFrame(self)
        self.history_popup.setObjectName('historyPopup')
        self._dark_history_qss = history_popup_qss('dark')
        history_layout = QVBoxLayout(self.history_popup)
        history_layout.setContentsMargins(5, 5, 5, 5); history_layout.setSpacing(0)
        self._search_history_wheel_delta = 0
        self._search_history_warp_generation = 0
        # Local in-memory filter: never edits global search or persists keywords.
        self.history_filter = QLineEdit(self.history_popup)
        self.history_filter.setObjectName('historyFilter')
        self.history_filter.setPlaceholderText('履歴内を検索...')
        self.history_filter.setToolTip('検索履歴の中だけを絞り込みます（メイン検索には影響しません）')
        self.history_filter.setClearButtonEnabled(True)
        self.history_filter.setFixedHeight(30)
        history_layout.addWidget(self.history_filter)
        history_layout.addSpacing(3)
        history_toolbar = QHBoxLayout()
        history_toolbar.setContentsMargins(5, 2, 5, 5)
        history_toolbar.setSpacing(4)
        history_title = QLabel('検索履歴', self.history_popup)
        history_toolbar.addWidget(history_title)
        history_toolbar.addStretch(1)
        self.history_expand_button = QPushButton('全展開', self.history_popup)
        self.history_collapse_button = QPushButton('全折畳', self.history_popup)
        self.history_add_button = QPushButton('＋', self.history_popup)
        for button in (self.history_expand_button, self.history_collapse_button,
                       self.history_add_button):
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedHeight(24)
            history_toolbar.addWidget(button)
        self.history_add_button.setFixedWidth(28)
        self.history_expand_button.clicked.connect(lambda: self.set_all_history_categories(True))
        self.history_collapse_button.clicked.connect(lambda: self.set_all_history_categories(False))
        self.history_add_button.clicked.connect(self.add_history_category)
        history_layout.addLayout(history_toolbar)
        self.history_choices = HistoryCategoryTree(self.history_popup)
        # IME preedit belongs to the search box, not the history list. Qt
        # must deliver InputMethod events here so they can be redirected.
        self.history_choices.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        self.history_choices.setObjectName('historyChoices')
        self.history_choices.setColumnCount(2)
        self.history_choices.setHeaderHidden(True)
        self.history_choices.setRootIsDecorated(False)
        self.history_choices.setIndentation(18)
        self.history_choices.setSortingEnabled(False)
        self.history_choices.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.history_choices.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.history_choices.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # History overlay has its own parent stylesheet: style the scrollbar
        # widgets explicitly so Windows does not draw the legacy arrows/track.
        apply_scrollbar_theme(self.history_choices, '#223043')
        self.history_choices.header().setStretchLastSection(False)
        self.history_choices.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.history_choices.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.history_choices.setColumnWidth(1, 34)
        self.history_choices.setIconSize(QSize(19, 19))
        self.history_clock_icon = history_clock_icon()
        self.history_choices.itemClicked.connect(self.history_row_clicked)
        self.history_choices.orderChanged.connect(self.history_reordered)
        self.history_choices.structureChanged.connect(self.history_structure_changed)
        self.history_choices.itemExpanded.connect(self.history_category_expanded)
        self.history_choices.itemCollapsed.connect(self.history_category_collapsed)
        self.history_choices.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_choices.customContextMenuRequested.connect(self.history_category_context_menu)
        self.history_filter.textChanged.connect(self.filter_history_popup)
        self.history_filter.returnPressed.connect(self.select_history_keyword)
        self.history_filter.installEventFilter(self)
        history_layout.addWidget(self.history_choices)
        self.history_popup.hide()
        self.history_choices.installEventFilter(self)
        self.history_choices.viewport().installEventFilter(self)
        self.tray = QSystemTrayIcon(tray_icon(), self); self.tray.setToolTip('FRB Launch — Ctrl+Shift+;')
        traymenu = QMenu(self)
        traymenu.addAction('開く', self.summon)
        traymenu.addAction('設定フォルダーを開く', lambda:self.open_target(str(CONFIG.parent)))
        traymenu.addAction('アプリ一覧を更新', self.refresh_apps)
        traymenu.addAction('アプリ一覧JSONを開く', lambda:self.open_target(str(STATE/'apps_cache.json')))
        traymenu.addSeparator()
        self.file_index_refresh_action = traymenu.addAction('ファイル索引を今すぐ更新', lambda: self.refresh_file_index(manual=True))
        traymenu.addAction('ファイル索引の状態を表示', self.show_file_index_status)
        self.file_index_clear_action = traymenu.addAction('ファイル索引SQLite DBをクリア', self.clear_file_index)
        traymenu.addAction('ファイル索引の設定JSONを開く',
                           lambda: self.open_target(str(self.file_index_options_path)))
        traymenu.addSeparator()
        browser_menu = traymenu.addMenu('ブックマークのブラウザ')
        self.bookmark_browser_actions = {}
        for key, title in (('chrome', 'Chrome'), ('edge', 'Edge')):
            action = browser_menu.addAction(title)
            action.setCheckable(True)
            action.setChecked(self.bookmark_browser == key)
            action.triggered.connect(lambda checked=False, name=key:self.select_bookmark_browser(name))
            self.bookmark_browser_actions[key] = action
        traymenu.addAction('ブックマークを更新', lambda:self.refresh_bookmarks(force=True))
        traymenu.addAction('ブックマーク取得診断', self.show_bookmark_diagnostics)
        traymenu.addAction('ブックマークファイルを指定（手動）', self.pick_bookmark_file)
        self.bookmark_auto_action = traymenu.addAction(
            '手動指定を解除（自動取得へ）', self.use_auto_bookmarks)
        self.update_bookmark_source_action()
        traymenu.addAction('ログフォルダーを開く', lambda:self.open_target(str(STATE)))
        traymenu.addSeparator(); traymenu.addAction('終了', self.quit)
        self.tray_menu = traymenu
        self.apply_color_theme()
        self.tray.setContextMenu(traymenu); self.tray.activated.connect(lambda r:self.summon() if r==QSystemTrayIcon.ActivationReason.Trigger else None)
        self.tray.show()
        self.search.textEdited.connect(self.search_user_edited)
        self.search.textChanged.connect(self.search_text_changed)
        self.tabs.currentChanged.connect(self.page_changed)
        self.tabs.currentChanged.connect(lambda *_: self.update_header_tab_width())
        self.list.itemActivated.connect(lambda item,col:self.activate(item.data(0,Qt.ItemDataRole.UserRole)))
        self.list.itemChanged.connect(self.check_changed)
        self.list.itemEntered.connect(self.hover)
        self.hover_timer = QTimer(self); self.hover_timer.setSingleShot(True); self.hover_timer.timeout.connect(self.open_hover)
        self.search.installEventFilter(self); self.list.installEventFilter(self); self.tabs.installEventFilter(self)
        self.expanded_view.address_bar.editor.installEventFilter(self)
        # The thin margins around the Page QTabBar belong to its containing
        # header, not the tab widget; make those blank clicks focus Page 1 too.
        self.mode_bar.installEventFilter(self)
        for panel in (self.expanded_view.left, self.expanded_view.middle, self.expanded_view.right):
            panel.tree.installEventFilter(self)
            panel.tree.viewport().installEventFilter(self)
        # Root toolbar buttons are recreated when Data/Page definitions reload.
        # Install filters in ExpandedLauncherView.refresh() for each new button.
        # QTreeWidget sends mouse events from its viewport, not from the tree.
        # An empty-area double-click navigates back only while inside a submenu.
        self.list.viewport().installEventFilter(self)
        QApplication.instance().focusChanged.connect(self.capture_last_focus_change)
        self._cascade_outside_click_filter = CascadeOutsideClickFilter(self)
        QApplication.instance().installEventFilter(self._cascade_outside_click_filter)
        self._history_outside_click_filter = HistoryOutsideClickFilter(self)
        QApplication.instance().installEventFilter(self._history_outside_click_filter)
        self._frame_cursor_reset_filter = FrameEdgeCursorResetFilter(self)
        QApplication.instance().installEventFilter(self._frame_cursor_reset_filter)
        self._normal_click_activation_filter = NormalWindowClickActivationFilter(self)
        QApplication.instance().installEventFilter(self._normal_click_activation_filter)
        QApplication.instance().applicationStateChanged.connect(self.app_state)
        # Page: Ctrl+F1..F12. Second layer (visible roots): Ctrl+Shift+F1..F12.
        # Free unmodified F2 for Explorer-style inline rename, and F5 for
        # refreshing the displayed folder. Selection's F12 confirm is retained.
        self.root_action_shortcuts = []
        for index in range(12):
            shortcut = QShortcut(QKeySequence(f'Ctrl+Shift+F{index+1}'), self)
            shortcut.activated.connect(lambda i=index: self.execute_expanded_root_shortcut(i))
            self.root_action_shortcuts.append(shortcut)
        self.page_shortcuts = []
        for index in range(12):
            shortcut = QShortcut(QKeySequence(f'Ctrl+F{index+1}'), self)
            shortcut.activated.connect(lambda i=index:self.switch_page(i))
            self.page_shortcuts.append(shortcut)
        self.file_rename_shortcut = QShortcut(QKeySequence('F2'), self)
        self.file_rename_shortcut.activated.connect(self.rename_current_middle_item)
        # F3 is the keyboard-first entrance to global search in any main view.
        # Window scope avoids installing a system-wide shortcut or changing Ctrl+F3 Page navigation.
        self.search_focus_shortcut = QShortcut(QKeySequence('F3'), self)
        self.search_focus_shortcut.activated.connect(self.focus_search)
        self.folder_refresh_shortcut = QShortcut(QKeySequence('F5'), self)
        self.folder_refresh_shortcut.activated.connect(self.refresh_current_middle_folder)
        self.hover_watch = QTimer(self);self.hover_watch.setInterval(60)
        self.hover_watch.timeout.connect(self.check_hover_menus);self.hover_watch.start()
        # Refresh the taskbar Jump List at every Launch process start even if
        # the prior version left an unchanged fingerprint on disk.
        self._jump_list_startup_synced = False
        self.reload(True)
        self.file_index_check_timer = QTimer(self)
        interval = self.file_index_settings['auto_update']['check_interval_minutes']
        self.file_index_check_timer.setInterval(interval * 60 * 1000)
        self.file_index_check_timer.timeout.connect(self.auto_refresh_file_index)
        self.file_index_check_timer.start()
        delay = self.file_index_settings['auto_update']['startup_delay_seconds']
        QTimer.singleShot(delay * 1000, self.auto_refresh_file_index)
        QTimer.singleShot(0,self.refresh_apps)
        self.registered_key = ''
        self.registered_menu_hotkeys = {}
        self.register_key()
        # Studio may save new shortcuts while Launch is hidden. A new key
        # cannot invoke reload until it is registered; poll the small JSON
        # file while hidden, without disturbing an active editing session.
        self.shortcut_reload_timer = QTimer(self)
        self.shortcut_reload_timer.setInterval(2000)
        self.shortcut_reload_timer.timeout.connect(self.reload_shortcuts_if_hidden)
        self.shortcut_reload_timer.start()
        self.restore_window_size()
        position = self.settings.value('position')
        if position: self.move(position)
        else:
            screen=QApplication.primaryScreen().availableGeometry();self.move(screen.center()-self.rect().center())

    def restore_normal_window_geometry(self):
        """Restore real dimensions after Qt.Tool hide/maximize/restore.

        Clearing WindowMaximized is insufficient for frameless Qt.Tool windows:
        the underlying HWND can retain its full-screen rectangle. Apply the
        last *normal* width, height, and position after showNormal() as well.
        """
        self._maximizing_window = True  # Do not persist intermediary Qt resizes.
        try:
            self.showNormal()
            self.restore_window_size()
            saved_pos = self.settings.value('position')
            if saved_pos is not None:
                self.move(saved_pos)
            self._restore_normal_on_show = False
        finally:
            self._maximizing_window = False
        self.update_header_icons()

    def show_launcher_normal_or_saved(self):
        """Always re-open maximized/hidden launcher using normal dimensions."""
        if self.isMinimized():
            if getattr(self, '_minimize_restore_maximized', False):
                self.showMaximized()
            else:
                self.showNormal()
        elif (getattr(self, '_restore_normal_on_show', False)
                or self.isMaximized()
                or bool(self.windowState() & Qt.WindowState.WindowMaximized)):
            self.restore_normal_window_geometry()
        else:
            self.show()

    def toggle_maximize_restore(self):
        if self.isMaximized() or bool(self.windowState() & Qt.WindowState.WindowMaximized):
            # showNormal() alone may leave an all-screen rectangle behind.
            self.restore_normal_window_geometry()
        else:
            self.save_window_size()
            self.settings.setValue('position', self.pos())
            self.settings.sync()
            self._maximizing_window = True
            try:
                self.showMaximized()
            finally:
                self._maximizing_window = False
        self.update_header_icons()

    def layout_search_inner_controls(self):
        """Keep icon/button inside the pill across DPI, resize and query state.

        The category button sits beside the magnifier; native QLineEdit
        history/clear actions remain on the far right. Reserve text margins
        so even a long query cannot be drawn underneath either control.
        """
        if not hasattr(self, 'search_glyph') or not hasattr(self, 'save_history_button'):
            return
        height, width = self.search.height(), self.search.width()
        self.search_glyph.move(11, max(0, (height - self.search_glyph.height()) // 2 + 2))
        # The plus is always adjacent to the magnifier, independent of width.
        self.history_category_button.move(
            44, max(0, (height - self.history_category_button.height()) // 2))
        is_visible = bool(self.search.text().strip())
        right_space = 75  # native ×, history ▼, breathing room (plus moved left)
        self.save_history_button.move(
            max(48, width - right_space - self.save_history_button.width()),
            max(0, (height - self.save_history_button.height()) // 2))
        # Reserve a clear text start beyond the magnifier AND the plus.
        # QLineEdit's 14px style padding is additional to this margin.
        self.search.setTextMargins(60, 0, 145 if is_visible else 0, 0)
        if is_visible:
            self.save_history_button.raise_()
        self.search_glyph.raise_()
        self.history_category_button.raise_()

    def update_header_icons(self):
        self.search_glyph.setIcon(toolbar_outline_icon('search', theme_family(self.color_theme)))
        self.theme_button.setText('')
        self.theme_button.setIcon(toolbar_outline_icon('settings', theme_family(self.color_theme)))
        icon_name = 'restore' if self.windowState() & Qt.WindowState.WindowMaximized else 'maximize'
        self.minimize_button.setIcon(toolbar_outline_icon('minimize', theme_family(self.color_theme)))
        self.maximize_button.setIcon(toolbar_outline_icon(icon_name, theme_family(self.color_theme)))
        self.close_button.setIcon(toolbar_outline_icon('close', theme_family(self.color_theme)))

    def open_theme_menu(self):
        """Launch's original settings button uses its existing anchor."""
        self.open_theme_menu_at(self.theme_button)

    def open_theme_menu_at(self, anchor):
        """Reuse the settings menu with a different display anchor for Remote."""
        self.close_cascade_for_main_interaction()
        self.hide_history_popup()
        for theme_id, action in self.theme_actions.items():
            action.setChecked(self.color_theme == theme_id)
        width = self.theme_menu.sizeHint().width()
        height = self.theme_menu.sizeHint().height()
        position = anchor.mapToGlobal(
            QPoint(anchor.width() - width, anchor.height() + 3))
        screen = QApplication.screenAt(anchor.mapToGlobal(QPoint(0, 0))) or QApplication.primaryScreen()
        if screen is not None:
            area = screen.availableGeometry()
            position.setX(max(area.left(), min(position.x(), area.right() - width + 1)))
            if position.y() + height > area.bottom() + 1:
                position.setY(anchor.mapToGlobal(QPoint(0, -height - 3)).y())
            position.setY(max(area.top(), min(position.y(), area.bottom() - height + 1)))
        self.theme_menu.popup(position)

    def _apply_window_mode(self, initial=False):
        """Normal window for keep-visible; legacy Tool for auto-dismiss.

        Switching Qt window *types* while shown requires re-showing the widget.
        Preserve the actual screen position, size and maximized state without
        touching the saved normal geometry or the current Launch navigation.
        """
        flags = (Qt.WindowType.FramelessWindowHint |
                 (Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint
                  if self.dismiss_on_outside_click else Qt.WindowType.Window))
        if initial:
            self.setWindowFlags(flags)
            return
        was_visible = self.isVisible()
        was_maximized = self.isMaximized()
        old_position = self.pos()
        old_size = self.size()
        self._maximizing_window = True
        try:
            self.setWindowFlags(flags)
            if was_visible:
                if was_maximized:
                    self.showMaximized()
                else:
                    self.resize(old_size)
                    self.move(old_position)
                    self.showNormal()
        finally:
            self._maximizing_window = False
        if getattr(self, '_cloud_link_handoff', False):
            # An outstanding native dialog must not restore topmost later.
            self._cloud_link_handoff = False
        if hasattr(self, 'minimize_button'):
            self.minimize_button.setVisible(not self.dismiss_on_outside_click)
        if hasattr(self, 'maximize_button'):
            self.update_header_icons()

    def set_dismiss_on_outside_click(self, enabled):
        previous = self.dismiss_on_outside_click
        self.dismiss_on_outside_click = bool(enabled)
        if previous != self.dismiss_on_outside_click:
            self._apply_window_mode()
            remote = getattr(self, 'remote_window', None)
            if remote is not None:
                remote.sync_window_mode()
        self.settings.setValue('dismiss_on_outside_click', self.dismiss_on_outside_click)
        self.settings.sync()
        self.footer.setText(
            'Launch外をクリックすると隠します。' if enabled
            else '通常ウィンドウとして表示します。他のアプリの背面へ移動でき、最小化も使えます。')

    def set_desktop_remote_enabled(self, checked):
        """Opt-in, persisted independently from the existing window modes."""
        self.remote_on_desktop_double_click = bool(checked)
        self.settings.setValue('desktop_remote_enabled', self.remote_on_desktop_double_click)
        self.settings.sync()
        if not self.remote_on_desktop_double_click:
            self.hide_remote()
        self.footer.setText('デスクトップリモコン：' +
                            ('有効（ダブルクリックで表示）' if checked else '無効'))

    def set_files_root_hidden_mode(self, checked):
        """Old single-column mode stays reversible; uncheck restores legacy."""
        self.files_exp_embedded_mode = False
        self.files_root_hidden_mode = bool(checked)
        self._apply_files_first_column_mode()
        if not checked:
            remote = getattr(self, 'remote_window', None)
            if remote is not None:
                remote.leave_files_grid_alignment()

    def set_files_exp_embedded_mode(self, checked):
        """Swap the visible old first-column content for the live Exp tree."""
        self.files_exp_embedded_mode = bool(checked)
        self.files_root_hidden_mode = bool(checked)
        self._apply_files_first_column_mode()

    def _apply_files_first_column_mode(self):
        self.settings.setValue('experiment_files_root_hidden',
                               self.files_root_hidden_mode)
        self.settings.setValue('experiment_files_exp_embedded',
                               self.files_exp_embedded_mode)
        self.settings.sync()
        self.files_root_hidden_action.setChecked(
            self.files_root_hidden_mode and not self.files_exp_embedded_mode)
        self.files_exp_embedded_action.setChecked(self.files_exp_embedded_mode)
        view = getattr(self, 'expanded_view', None)
        if view is not None:
            view.apply_files_root_hidden_mode()
            if self.files_root_hidden_mode and view.isVisible():
                if view._workspace_mode == 'files':
                    self.remote_focus_area('directory')
                elif getattr(self, '_remote_area', None) == 'bookmarks':
                    self.remote_focus_area(self._current_web_body_area())
        remote = getattr(self, 'remote_window', None)
        if remote is not None:
            remote.set_files_root_hidden_mode(self.files_root_hidden_mode)
            if self.files_exp_embedded_mode:
                # One Exp tree is enough: the standalone companion stays
                # available for instant rollback, but not visible in this mode.
                if remote.files_exp_panel is not None:
                    remote.files_exp_panel.hide()
                remote.leave_files_grid_alignment()
            else:
                # Position always belongs to the Remote user preference,
                # not the grid alignment experiment, in either legacy mode.
                remote.leave_files_grid_alignment()
        self.footer.setText(
            'Files Expを第1列に表示します（Remoteは第2列を操作）。'
            if self.files_exp_embedded_mode else
            'Filesルート非表示：第2列のみを操作します。'
            if self.files_root_hidden_mode else '従来のFiles第1列を復元しました。')

    def close_finished_file_context_menus(self):
        """Dismiss filesystem context menus after an operation completes.

        Navigating/hovering Filesリスト is not an operation, so callers run
        this only after an action (Paste, Copy, Cut, Delete, etc.) is chosen.
        Close from the root down to avoid leaving orphaned cascade columns.
        """
        context = getattr(self, '_launch_context_menu', None)
        if context is not None:
            try:
                context.close()
            except RuntimeError:  # Qt already destroyed the popup.
                pass
            if getattr(self, '_launch_context_menu', None) is context:
                self._launch_context_menu = None
        self.close_remote_folder_menu()
        cascade = getattr(self, 'menu', None)
        if (cascade is not None and cascade is not getattr(self, '_remote_page_menu', None)
                and cascade.isVisible()):
            cascade.close()

    def close_remote_folder_menu(self):
        """Close Remote filesystem preview and its right-click opener."""
        menu = getattr(self, '_remote_folder_root_menu', None)
        self._remote_folder_root_menu = None
        opener = getattr(self, '_remote_folder_opener', None)
        self._remote_folder_opener = None
        self._remote_folder_commit_pending = False
        self._remote_folder_popup_pos = None
        self._remote_folder_source_path = None
        if menu is not None:
            menu.close()
        if opener is not None:
            opener.close()
            opener.deleteLater()

    def show_remote_current_folder_menu(self):
        """Show the EXISTING Files background menu plus Remote's file list.

        The add-on must not replace Paste/New/Explorer/Properties: they are
        still the normal right-click operations on this Remote blank strip.
        """
        remote = getattr(self, 'remote_window', None)
        view = self.expanded_view
        if (remote is None or not remote.isVisible() or not view.isVisible()
                or view._workspace_mode != 'files'):
            return
        directory = view.current_directory()
        if not directory or not Path(directory).is_dir():
            return
        self.close_remote_folder_menu()
        self.show_expanded_background_paste_menu(
            QCursor.pos(), remote_folder_list=True)

    def navigate_files_exp_pc(self):
        """Select the virtual PC ROOT in Launch when Files Exp clicks PC.

        A virtual shell root has no filesystem path, so the normal folder
        callback cannot resolve it. Use the authored first-column row and
        the existing browser_rows(PC) drive resolver; never fake C:\\.
        """
        view = self.expanded_view
        if not view.isVisible():
            return False
        if view._workspace_mode != 'files':
            view.show_files_view()
        tree = view.left.tree
        pc_item = next((tree.topLevelItem(i)
                        for i in range(tree.topLevelItemCount())
                        if (view.row_data(tree.topLevelItem(i)) or {}).get(
                            '_system_drives_root')), None)
        if pc_item is None:
            return False
        tree.setCurrentItem(pc_item)
        view.choose_files(pc_item, 0)  # PC breadcrumb + real drive rows.
        # Files Exp owns focus: only change the *logical* active column,
        # without stealing keyboard focus back from the tool window.
        self.set_files_operating_target(
            getattr(self, '_files_operating_target', 'directory'))
        return True

    def navigate_files_exp_folder(self, directory):
        """Commit a Files Exp selection through the existing breadcrumb flow.

        A folder-tree selection never executes/open-files or writes to disk.
        Keep Tool windows and popup focus stable during navigation.
        """
        view = self.expanded_view
        if not view.isVisible() or not Path(directory).is_dir():
            return False
        if view._workspace_mode != 'files':
            view.show_files_view()
        return bool(view.go_to_directory(directory, preserve_remote_popup=True))

    def show_files_exp_folder_menu(self, directory, position):
        """The existing Remote blank-strip menu, bound to the chosen folder.

        Includes the full 'Filesリスト ▶' cascade and all
        shared Paste/New/Explorer/Properties actions; do not duplicate them.
        """
        if not self.navigate_files_exp_folder(directory):
            return False
        self.close_remote_folder_menu()
        return self.show_expanded_background_paste_menu(
            position, remote_folder_list=True,
            files_exp_rename_target=str(directory))

    def on_files_exp_folder_renamed(self, old_path, new_path):
        """An inline Files Exp rename commits before breadcrumb navigation."""
        if not Path(new_path).is_dir():
            return False
        # A renamed directory keeps its own customized sort preference.
        from folder_sort_preferences import transfer_directory_sort
        from middle_folder_filter import SORT_LABELS
        transfer_directory_sort(self.settings, old_path, new_path, SORT_LABELS)
        notify = getattr(self, 'notify_folder_mutation', None)
        if callable(notify):
            notify(Path(old_path).parent)
        changed = self.navigate_files_exp_folder(new_path)
        if changed:
            self.footer.setText(
                f'名前を変更しました: {Path(old_path).name} → {Path(new_path).name}')
            if self.file_index_settings.get('enabled', True) and not self.file_index_busy:
                QTimer.singleShot(0, lambda: self.refresh_file_index(manual=False))
        return changed

    def _remote_popup_vertical_bounds(self):
        """Remote popup band begins at Files and extends 3x downward."""
        remote = getattr(self, 'remote_window', None)
        if remote is None or not remote.isVisible():
            return None
        top = remote.files_button.mapToGlobal(QPoint(0, 0)).y() - 1
        former_bottom = remote.mapToGlobal(QPoint(0, remote.height() - 6)).y()
        if former_bottom <= top:
            return None
        # Previously this band ended at Remote's footer (~200px after Files).
        # User now wants three times that *vertical reach*, for every column.
        # CascadeMenu.popup() independently clips to the available monitor.
        return (top, top + 3 * (former_bottom - top))

    def _apply_remote_popup_bounds(self, menu):
        bounds = self._remote_popup_vertical_bounds()
        if bounds is not None:
            menu.remote_popup_bounds = bounds
        return menu

    def _remote_folder_root_hidden(self, menu):
        if (getattr(self, '_remote_folder_root_menu', None) is menu
                and not getattr(self, '_remote_folder_commit_pending', False)):
            self._remote_folder_root_menu = None
            self._remote_folder_source_path = None
            self._remote_folder_popup_pos = None

    def _remote_browser_bookmark_rows(self):
        """Use Browser's displayed Bookmarks rows, skipping section headings.

        The right panel keeps its rows even when temporarily hidden in Files
        mode.  Never create a parallel bookmark store or mutate the source.
        """
        view = self.expanded_view
        tree = view.right.tree
        return [row for row in (
            view.row_data(tree.topLevelItem(i))
            for i in range(tree.topLevelItemCount()))
            if isinstance(row, dict) and row.get('item_kind') in
            ('category', 'directory', 'command')]

    def show_remote_browser_bookmark_menu(self):
        """Right-click Browser: open its displayed bookmark first column.

        This is a navigation preview, not a workspace switch. A URL uses the
        normal bookmark activation route (embedded WebView / external mode).
        """
        remote = getattr(self, 'remote_window', None)
        view = self.expanded_view
        if (remote is None or not remote.isVisible() or not view.isVisible()
                or view.bookmarks_root is None):
            return
        self.close_remote_folder_menu()
        self.close_remote_page_menu()  # Page and Browser share one menu slot.
        if self.menu is not None:
            self.menu.close()
        menu = self._apply_remote_popup_bounds(CascadeMenu(parent=self, launcher=self))
        menu.remote_page_navigation = True  # First-click/hover opens folders.
        menu.bookmark_navigation = True
        menu.bookmark_compact_width = True
        menu.remote_browser_bookmark_roots = True  # Add target radio buttons below search.
        menu.remote_bookmark_new_tab = True        # Default on EACH opening: new tab.
        menu.setMaximumWidth(min(menu.maximumWidth(), round(CASCADE_MAX_WIDTH * 0.7)))
        menu.open_mode = 'mouse'
        self._remote_page_menu = menu
        self.menu = menu
        root = {'item_kind': 'category', 'item_id': 'remote-browser-bookmarks',
                'title': 'ブックマーク', 'launch_source': 'remote_browser_bookmark_roots'}
        self.fill_cascade(menu, root)
        button = remote.browser_button
        anchor = button.mapToGlobal(QPoint(button.width() - 1, 0))
        menu.popup(anchor)

    def _remote_files_first_column_rows(self):
        """Read the rendered Files column 1, not the breadcrumb/current dir."""
        view = self.expanded_view
        tree = view.left.tree
        return [row for row in (
            view.row_data(tree.topLevelItem(i))
            for i in range(tree.topLevelItemCount()))
            if isinstance(row, dict)]

    def show_remote_files_first_column_menu(self):
        """Right-click Files: switch to Files and open its first-column roots.

        Unlike HOME/left-click, keep the last Files breadcrumb and selection.
        The remote Browser bookmark popup must close before switching modes.
        """
        remote = getattr(self, 'remote_window', None)
        view = self.expanded_view
        if remote is None or not remote.isVisible() or not view.isVisible():
            return
        self.close_remote_page_menu()
        if self.menu is not None:
            self.menu.close()
        if view._workspace_mode != 'files':
            view.show_files_view()  # Switch only; do NOT call navigate_home().
        if view.files_root is None or view.left.tree.topLevelItemCount() == 0:
            return
        self.close_remote_folder_menu()
        menu = self._apply_remote_popup_bounds(RemoteFolderCascade(parent=self, launcher=self))
        menu.remote_files_roots = True   # Keep the root list through breadcrumb commits.
        menu.remote_folder_navigation = True
        menu.remote_folder_root = menu
        self._remote_folder_root_menu = menu
        self._remote_folder_opener = None
        directory = view.current_directory()
        self._remote_folder_source_path = (os.path.normcase(os.path.normpath(str(directory)))
                                           if directory else None)
        anchor = remote.files_button.mapToGlobal(QPoint(remote.files_button.width() - 1, 0))
        self._remote_folder_popup_pos = anchor
        self.fill_cascade(menu, {'item_kind': 'category', 'item_id': 'remote-files-first-column',
                                 'title': 'Files', 'launch_source': 'remote_files_roots'})
        menu.aboutToHide.connect(lambda m=menu: self._remote_folder_root_hidden(m))
        menu.popup(anchor)
        menu.setFocus()

    def _remote_folder_context(self, directory):
        return {'item_kind': 'directory', 'item_id': f'remote-fs:{directory}',
                'title': Path(directory).name or directory,
                'launch_browse_target': str(directory), 'launch_source': 'remote_filesystem'}

    def _open_remote_folder_cascade(self, opener, action, directory, mode='hover'):
        """Open or refresh the Remote list using the *current* Files breadcrumb.

        ``directory`` is only the path from when the context menu was first
        constructed.  A folder click can update the breadcrumb while this
        parent menu remains open, so never use that captured value as truth.
        """
        current = (getattr(opener, 'remote_target_directory', None)
                   or self.expanded_view.current_directory())
        if not current or not Path(current).is_dir():
            self.error('操作対象のフォルダーが見つかりません: ' + str(current))
            return
        directory = str(current)
        if opener.child is not None:
            if (opener.child.isVisible() and opener.child.owner_action is action
                    and mode != 'refresh'):
                return
            # On an explicit click replace the entire child Tool column,
            # including its optional scroll-tree and search QWidgetAction.
            # Rebasing an already rendered column could leave a stale view
            # showing no rows after the Files breadcrumb has changed.
            opener.child.close()
            opener.child.deleteLater()
            opener.child = None
        child = RemoteFolderCascade(parent=opener, launcher=self)
        if hasattr(opener, 'remote_popup_bounds'):
            child.remote_popup_bounds = opener.remote_popup_bounds
        child.remote_folder_root = child
        child.owner_action = action
        child.open_mode = 'keyboard'
        opener.child = child
        self._remote_folder_root_menu = child
        self._remote_folder_source_path = os.path.normcase(os.path.normpath(directory))
        self.fill_cascade(child, self._remote_folder_context(directory))
        rect = opener.actionGeometry(action)
        child.popup(opener.mapToGlobal(QPoint(opener.width() - 1, rect.top())))
        child.setFocus()

    def _remote_folder_opener_hidden(self, opener):
        """Forget only the Remote menu that actually closed."""
        if (getattr(self, '_remote_folder_opener', None) is opener
                and not getattr(self, '_remote_folder_commit_pending', False)):
            self._remote_folder_opener = None
            self._remote_folder_root_menu = None
            self._remote_folder_source_path = None

    def on_files_directory_changed(self, directory):
        """Breadcrumb is authoritative for Remote, Files Exp, and Files."""
        # Store the former breadcrumb, not Exp's candidate row: a List-side
        # parent navigation must collapse the *departed* child folder in Exp.
        # This also covers the Remote's (List カレントフォルダー操作) and Go Up.
        import ntpath
        previous = getattr(self, '_last_files_breadcrumb_directory', None)
        current = str(directory) if directory else None
        self._last_files_breadcrumb_directory = current
        ascending_one_level = bool(
            previous and current
            and ntpath.normcase(ntpath.normpath(ntpath.dirname(previous)))
            == ntpath.normcase(ntpath.normpath(current))
            and ntpath.normcase(ntpath.normpath(previous))
            != ntpath.normcase(ntpath.normpath(current)))
        panel = getattr(getattr(self, 'remote_window', None), 'files_exp_panel', None)
        if panel is not None and panel.isVisible():
            panel.sync_current_directory(directory)
        embedded = getattr(getattr(self, 'expanded_view', None),
                           'embedded_files_exp', None)
        if embedded is not None and embedded.isVisible():
            embedded.sync_current_directory(directory)
        if ascending_one_level:
            for exp_panel in (panel, embedded):
                if exp_panel is not None and exp_panel.isVisible():
                    exp_panel.collapse_departed_child(previous, current)
        self.refresh_main_files_cut_visuals()
        # Exp's current directory also identifies the first-column registered
        # ROOT. Keep that row as an outline (not a second active green row).
        if panel is not None and panel.isVisible():
            self.sync_files_first_column_root(directory)
        if (getattr(self, '_remote_folder_opener', None) is None
                and getattr(self, '_remote_folder_root_menu', None) is None):
            return
        path = (os.path.normcase(os.path.normpath(str(directory)))
                if directory else None)
        if path == getattr(self, '_remote_folder_source_path', None):
            return
        self._remote_folder_source_path = path
        if not getattr(self, '_remote_folder_navigation', False):
            self.close_remote_folder_menu()

    def sync_files_first_column_root(self, directory):
        """Remember the deepest registered root containing the breadcrumb.

        Neither select a filesystem operation target nor change Qt focus.
        The actual active row stays in Files column 2 / Files Exp.
        """
        view = getattr(self, 'expanded_view', None)
        if (view is None or not directory or
                getattr(view, '_workspace_mode', None) != 'files'):
            return False
        from directory_address import row_directory
        import ntpath
        target = ntpath.normcase(ntpath.normpath(str(directory).replace('/', '\\')))
        best = None
        tree = view.left.tree
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            row = view.row_data(item)
            candidate = row_directory(row, self.expander().expand)
            if not candidate:
                continue
            key = ntpath.normcase(ntpath.normpath(candidate))
            if target == key or target.startswith(key.rstrip('\\') + '\\'):
                if best is None or len(key) > best[0]:
                    best = (len(key), item)
        if best is None:
            return False
        if tree.currentItem() is not best[1]:
            tree.setCurrentItem(best[1])
        # The first-column marker is contextual memory, never another active
        # selection after an Exp / second-column navigation.
        if tree.property('remoteInactive') is not True:
            tree.setProperty('remoteInactive', True)
            tree.style().unpolish(tree)
            tree.style().polish(tree)
        tree.viewport().update()
        return True

    def close_remote_page_menu(self):
        """Dismiss the Remote Page cascade, not an unrelated Compact menu."""
        page_menu = getattr(self, '_remote_page_menu', None)
        self._remote_page_menu = None
        if page_menu is not None:
            page_menu.close()  # CascadeMenu closes its child columns as well.
            if getattr(self, 'menu', None) is page_menu:
                self.menu = None

    def hide_remote(self):
        self.close_remote_folder_menu()
        self.close_remote_page_menu()
        popup = getattr(self, '_remote_popup_area', None)
        self._remote_popup_area = None
        if popup == 'search_history':
            self.hide_history_popup()
        elif popup == 'folder_history':
            self.expanded_view.hide_favorite_popup()
        elif popup == 'browser_history':
            web = getattr(self.expanded_view, 'web_view', None)
            if web is not None:
                web.hide_url_favorites()
        if self.remote_window is not None and self.remote_window.isVisible():
            self.remote_window.hide()
        if getattr(self.expanded_view, 'web_view', None) is not None:
            self.expanded_view.web_view.set_remote_area(None)
        # Closing Remote must NOT turn both Files columns green. Preserve the
        # single logical active column even while its companion UI is hidden.
        active_files_area = (self._remote_area if self._remote_area in ('files', 'directory')
                             else self._last_focus_area if self._last_focus_area in ('files', 'directory')
                             else 'files')
        for area_name, pane in (('files', self.expanded_view.left),
                                ('directory', self.expanded_view.middle),
                                ('bookmarks', self.expanded_view.right)):
            pane.tree.remote_logical_active = False
            pane.tree.remote_highlight_mode = False
            if area_name == 'bookmarks':
                pane.tree.setProperty('remoteInactive', False)
            else:
                pane.tree.setProperty('remoteInactive', area_name != active_files_area)
            pane.tree.style().unpolish(pane.tree)
            pane.tree.style().polish(pane.tree)
            pane.tree.viewport().update()

    def bring_launcher_forward_from_remote_header(self):
        """Explicit Remote title click: reveal Launcher without changing its current item.

        Keep this strictly on the title surface, not the wheel or command buttons.
        The remote remains non-activating so a click does not steal keyboard focus.
        """
        if not self.isVisible() or self.isMinimized():
            return
        # Do not invoke restore_keyboard_focus(): that would change the logical
        # current selection and could steal input from the user unexpectedly.
        hwnd = int(self.winId())
        current = windows.foreground()
        if current and current != hwnd:
            windows.activate_keyboard_window(hwnd, expected_foreground=current)
        self.raise_()
        # A non-activating Tool may receive clicks while Chrome keeps native
        # foreground. Temporarily lift the normal Launcher into topmost Z-order,
        # then immediately restore its normal window classification.
        windows.set_window_topmost(hwnd, True)
        windows.set_window_topmost(hwnd, False)
        windows.raise_normal_window(hwnd)
        remote = getattr(self, 'remote_window', None)
        if remote is not None and remote.isVisible():
            remote.raise_()

    def open_remote_page(self, page_id, anchor=None):
        """Open the shared Page cascade beside its Launch/Remote button.

        Page selection is isolated from the main window's selected Page and
        workspace; nested columns and their hover logic are shared unchanged.
        """
        remote = getattr(self, 'remote_window', None)
        if not self.data:
            return
        page = next((p for p in self.pages if str(p.get('page_id')) == str(page_id)), None)
        button = (anchor if anchor is not None else next((b for b in
                       (remote.page_buttons if remote is not None else ())
                       if b.property('remote_page_id') == str(page_id)), None))
        if page is None or button is None:
            return
        existing = getattr(self, '_remote_page_menu', None)
        if existing is not None:
            existing.close()
            existing.deleteLater()
            self._remote_page_menu = None
        if self.menu is not None and self.menu is not existing:
            self.menu.close()
        # A virtual category with the page's root item ID ('') is sufficient
        # for fill_cascade() to use the same filters, icons and hover expansion.
        root = {'item_id': '', 'page_id': page_id,
                'item_kind': 'category', 'launch_source': 'remote_page'}
        menu = CascadeMenu(parent=self, launcher=self)
        menu.open_mode = 'mouse'
        menu.remote_page_navigation = True
        self._remote_page_menu = menu
        self.menu = menu
        self.fill_cascade(menu, root)
        # Position the LEFT EDGE beside the actual click, not at the far
        # right of the entire Remote. Both mouse buttons share this path.
        # The real screen boundary is handled by CascadeMenu.popup().
        pointer = QCursor.pos()
        button_rect = button.rect()
        local_pointer = button.mapFromGlobal(pointer)
        if not button_rect.contains(local_pointer):
            # Programmatic Page activation uses the button center instead.
            pointer = button.mapToGlobal(button_rect.center())
        menu.popup(QPoint(pointer.x() + 8, pointer.y() + 4))

    def ensure_remote_window(self):
        """The sole Remote instance serves desktop, overlay and history modes."""
        if self.remote_window is None:
            self.remote_window = LaunchRemote(self)
            self.remote_window.command.connect(self.remote_command)
            self.remote_window.header_pressed.connect(self.bring_launcher_forward_from_remote_header)
            self.remote_window.more_menu_opening.connect(self.update_remote_more_menu)
            self.remote_window.page_clicked.connect(self.open_remote_page)
            self.remote_window.files_exp_folder_selected.connect(self.navigate_files_exp_folder)
            self.remote_window.files_exp_pc_selected.connect(self.navigate_files_exp_pc)
            self.remote_window.files_exp_folder_context.connect(self.show_files_exp_folder_menu)
            self.remote_window.files_exp_folder_renamed.connect(self.on_files_exp_folder_renamed)
        return self.remote_window

    def set_remote_15_mode(self, checked):
        """Reversible overlay experiment; existing Remote commands stay intact."""
        self.remote_15_mode = bool(checked)
        self.settings.setValue('experiment_remote_15_column', self.remote_15_mode)
        self.settings.sync()
        self.remote_15_action.setChecked(self.remote_15_mode)
        view = getattr(self, 'expanded_view', None)
        if view is not None:
            view.apply_remote_15_lane_mode()
        if self.remote_15_mode:
            if view is not None and view._workspace_mode == 'browser':
                self._remote_15_needs_show = False
                self.hide_remote()
            else:
                self.queue_remote_15_alignment(show=True)
        else:
            remote = getattr(self, 'remote_window', None)
            if remote is not None:
                remote._remote_15_placement = False
                saved = self.settings.value('remote_last_position')
                if isinstance(saved, QPoint):
                    remote.move(saved)
        self.footer.setText(
            'Remoteは第1.5列に別Windowで表示します。' if checked
            else 'リモコン第1.5列表示を解除しました。')

    def queue_remote_15_alignment(self, *, show=False):
        """Schedule AFTER splitter geometry changes without focus stealing."""
        if not getattr(self, 'remote_15_mode', False):
            return
        if show:
            self._remote_15_needs_show = True
        if getattr(self, '_remote_15_alignment_pending', False):
            return
        self._remote_15_alignment_pending = True
        QTimer.singleShot(0, self._align_remote_15_now)

    def _align_remote_15_now(self):
        self._remote_15_alignment_pending = False
        view = getattr(self, 'expanded_view', None)
        if (not self.remote_15_mode or view is None or not self.isVisible()
                or self.isMinimized() or view._workspace_mode != 'files'):
            if view is not None and view._workspace_mode == 'browser':
                self._remote_15_needs_show = False
            return
        lane = getattr(view, 'remote_15_lane', None)
        if lane is None:
            return
        # During global search the Files canvas may be temporarily hidden.
        # Keep the separate Remote above the search result list, at its
        # last anchored offset from Launch, rather than disappearing.
        anchor_visible = view.isVisible() and lane.isVisible()
        if not anchor_visible and not hasattr(self, '_remote_15_offset'):
            return
        show = bool(getattr(self, '_remote_15_needs_show', False))
        self._remote_15_needs_show = False
        remote = getattr(self, 'remote_window', None)
        if not show and (remote is None or not remote.isVisible()):
            # × closes Remote until another explicit Files selection.
            return
        if remote is None:
            remote = self.ensure_remote_window()
        remote.sync_window_mode()
        if show:
            remote.set_pages(self.pages)
            remote.apply_theme(self.color_theme)
            remote.set_workspace('files')
            # Keep previous logical selection, particularly search results.
            if self._remote_area is None:
                self._remote_area = 'directory'
            # The Files target survives transient search/history areas.
            target = getattr(self, '_files_operating_target', 'directory')
            target_button = getattr(remote, 'set_operating_target', None)
            if callable(target_button):
                target_button(target)
            title_sync = getattr(view, 'set_files_operating_area', None)
            if callable(title_sync):
                title_sync(target)
            # When re-entering Files from Browser, don't leave a Web/search
            # caption on a Files controller.
            if self._remote_area not in ('files_exp', 'directory', 'list',
                                         'search_history', 'folder_history'):
                self._remote_area = target
            remote.set_area(self._remote_area)
        remote._remote_15_placement = True
        if anchor_visible:
            pos = lane.mapToGlobal(QPoint(max(0, (lane.width() - remote.width()) // 2), 4))
            self._remote_15_offset = pos - self.pos()
        else:
            pos = self.pos() + self._remote_15_offset
        if remote.pos() != pos:
            remote.move(pos)
        if show and not remote.isVisible():
            remote.show()
        if remote.isVisible():
            remote.raise_()  # Above main search/list overlays, without activation.

    def show_remote_at(self, pointer):
        """Open at a verified desktop mouse point; do not steal IME focus."""
        if not self.remote_on_desktop_double_click or not self.isVisible() or self.isMinimized():
            return
        if (self.remote_15_mode and self.expanded_view._workspace_mode == 'browser'):
            return  # Browser has no Remote overlay in the 1.5-column experiment.
        if (self.remote_15_mode and self.expanded_view.isVisible()
                and self.expanded_view._workspace_mode == 'files'):
            self.queue_remote_15_alignment(show=True)
            return
        self.ensure_remote_window()
        self.remote_window.sync_window_mode()
        self.remote_window.set_pages(self.pages)
        self.remote_window.apply_theme(self.color_theme)
        self.remote_window.set_workspace(self.expanded_view._workspace_mode)
        self._remote_popup_area = None
        self._remote_mouse_last_click = None
        self._remote_mouse_menu_click = None
        web = self.expanded_view._workspace_mode == 'browser'
        self._remote_area = ('bookmarks' if web else
                             getattr(self, '_files_operating_target', 'directory')) if self.expanded_view.isVisible() else 'list'
        # When the previous session deliberately left Files column 2 current,
        # keep that selection visible when the Remote is summoned again.
        # A fresh session still begins at Files column 1 as before.
        saved = normalize_focus_state(self._saved_focus_state)
        if not web and self.expanded_view.isVisible():
            middle = self.expanded_view.middle.tree
            # A still-visible Launch has LIVE focus/selection state.  The
            # persisted snapshot describes a previous dismissal, not the
            # current row: do not reset column 2 to column 1 on Remote summon.
            live_directory_current = (middle.currentItem() is not None and
                                      (self._last_focus_area == 'directory'
                                       or middle.hasFocus()
                                       or getattr(middle, 'remote_logical_active', False)))
            saved_directory_current = (
                self._last_focus_area not in ('files', 'directory')
                and saved.get('area') == 'directory'
                and saved.get('middle_path') == self.expanded_view.current_directory()
                and middle.currentItem() is not None)
            if live_directory_current or saved_directory_current:
                self._remote_area = 'directory'
        if (self.files_root_hidden_mode and not web and self.expanded_view.isVisible()
                and self._remote_area == 'files'):
            self._remote_area = 'files_exp' if self.files_exp_embedded_mode else 'directory'
        self.remote_focus_area(self._remote_area)
        self.remote_window.show_at(pointer)
        # Files Exp is a permanent companion to the Remote. Reopen it on
        # each desktop activation, but never toggle an existing panel OFF.
        panel = getattr(self.remote_window, 'files_exp_panel', None)
        if not self.files_exp_embedded_mode:
            if panel is None or not panel.isVisible():
                self.remote_window.toggle_files_exp()
        # Remote position is the saved user position in every mode. Standalone
        # Exp still follows Remote when that legacy option is selected.
        # Only verified desktop double clicks enter this path. Do not warp
        # the pointer on manual toggles, menu opens, or ordinary navigation.
        self.remote_window.focus_cursor_on_files_exp()

    def _web_tab_count(self):
        web = self.expanded_view.web_view
        return web.tabs.count() if web is not None else 0

    def _current_web_body_area(self):
        web = self.expanded_view.web_view
        return (f'web_body:{max(0, web.tabs.currentIndex())}' if web else
                ('bookmarks' if self.expanded_view.browser_bookmarks_visible
                 else 'workspace_browser'))

    def update_files_item_count(self, count=None):
        """Permanent Files item count; never overwritten by transient notices."""
        view = getattr(self, 'expanded_view', None)
        visible = (view is not None and view.isVisible()
                   and getattr(view, '_workspace_mode', '') == 'files')
        if visible:
            if count is None:
                count = view.middle.tree.topLevelItemCount()
            self.files_item_count.setText(f'{int(count):,} 個の項目')
            # Qt's selectedItems() reflects *actual* multi-selection, not a
            # remembered current-row outline. Metadata was collected while
            # building the displayed rows; never rescan files on selection.
            rows = [view.row_data(item) for item in view.middle.tree.selectedItems()]
            summary = files_selected_summary(rows)
            if summary:
                self.files_item_count.setText(self.files_item_count.text() + '  |  ' + summary)
        self.files_item_count.setVisible(bool(visible))

    def workspace_changed(self, mode):
        """Refresh Remote without resetting the retained Files/Browser state."""
        if getattr(self, 'remote_15_mode', False):
            if mode == 'browser':
                # The floating Remote belongs to Files' middle lane; Browser
                # deliberately has no overlay. It returns on Files selection.
                self._remote_15_needs_show = False
                self.hide_remote()
            elif mode == 'files':
                self.queue_remote_15_alignment(show=True)
        if getattr(self, '_remote_popup_area', None) == 'browser_history' and mode != 'browser':
            web = getattr(self.expanded_view, 'web_view', None)
            if web is not None:
                web.hide_url_favorites()
            self._remote_popup_area = None
        elif getattr(self, '_remote_popup_area', None) == 'folder_history' and mode != 'files':
            self.expanded_view.hide_favorite_popup()
            self._remote_popup_area = None
        if mode != 'files':
            self.close_remote_folder_menu()
        remote = getattr(self, 'remote_window', None)
        if remote is not None:
            remote.set_workspace(mode)
        area = getattr(self, '_remote_area', None)
        if remote is not None and remote.isVisible():
            if mode == 'browser' and area in ('files', 'directory', 'breadcrumb'):
                self.remote_focus_area(self._current_web_body_area() if self.files_root_hidden_mode
                                       else 'bookmarks')
            elif (mode == 'files' and not getattr(self, '_remote_preserve_files_selection', False)
                  and (area == 'bookmarks' or str(area).startswith('web_body:'))):
                self.remote_focus_area(getattr(self, '_files_operating_target', 'directory'))

    def _focus_bookmark_first(self):
        """Entering Bookmarks via Tab begins at the first actionable row."""
        if (self.files_root_hidden_mode or
                not self.expanded_view.browser_bookmarks_visible):
            return
        tree = self.expanded_view.right.tree
        for index in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(index)
            if (item is not None and not item.isHidden() and
                    bool(item.flags() & Qt.ItemFlag.ItemIsSelectable)):
                tree.setCurrentItem(item)
                tree.scrollToItem(item)
                break
        self.expanded_view.focus_panel(self.expanded_view.right)

    def web_view_activated(self):
        """A bookmark can change the View without changing the selected bookmark."""
        view = self.expanded_view
        if not getattr(view, 'web_view_active', lambda: False)():
            return
        remote = getattr(self, 'remote_window', None)
        if remote is not None and remote.isVisible():
            area = self._remote_area
            if area in ('files', 'directory', 'sort', 'breadcrumb'):
                self.remote_focus_area('bookmarks')
            else:
                view.web_view.set_remote_area(
                    'web_body' if str(area).startswith('web_body:') else area)

    def web_surface_selected(self, area):
        """A real click on Web tabs/body moves Remote logical current as well."""
        remote = getattr(self, 'remote_window', None)
        if (getattr(self.expanded_view, 'web_view_active', lambda: False)() and remote is not None
                and remote.isVisible() and area in ('web_tabs', 'web_body')):
            self.remote_focus_area(self._current_web_body_area())

    def web_keyboard_tab(self, backward):
        """Tab on the Web tab STRIP changes Launch areas; HTML forms stay native."""
        if not getattr(self.expanded_view, 'web_view_active', lambda: False)():
            return
        area = self._current_web_body_area()
        order = navigation_order(expanded=True, web=True,
                                 web_tab_count=self._web_tab_count(),
                                 bookmarks_visible=self.expanded_view.browser_bookmarks_visible)
        target = tab_target(area, backward=backward, order=order)
        self.remote_focus_area(target)
        if str(target).startswith('web_body:'):
            self.expanded_view.web_view.focus_page()

    def set_files_operating_target(self, target):
        """One authoritative Files target for direct mouse AND Remote gestures.

        This is intentionally *presentation only*: the breadcrumb, file-row
        selection, tree cursor and native keyboard focus must never change.
        Navigation commands remain separate (Exp ●/→, List ←, etc.).
        """
        if target not in ('files_exp', 'directory', 'files'):
            return False
        if target == 'files' and self.files_exp_embedded_mode:
            target = 'files_exp'
        self._files_operating_target = target
        self._remote_area = target
        self._last_focus_area = target
        view = getattr(self, 'expanded_view', None)
        if view is not None and view._workspace_mode == 'files':
            view.set_files_operating_area(target)
            # A normal Remote may use a SEPARATE Exp tool window, rather
            # than the embedded Exp in Launch. It uses the same canonical
            # active/remembered colors, and follows the same target setter.
            remote = getattr(self, 'remote_window', None)
            standalone_exp = getattr(remote, 'files_exp_panel', None) if remote else None
            if standalone_exp is not None:
                standalone_exp.set_operating_active(target == 'files_exp')
            # Direct Exp wheel/click may leave native Qt focus in List. The
            # current row must therefore follow the logical target, not focus.
            for name, pane in (('files', view.left), ('directory', view.middle)):
                tree = pane.tree
                active = (name == target)
                tree.remote_highlight_mode = True
                tree.remote_logical_active = active
                if tree.property('remoteInactive') != (not active):
                    tree.setProperty('remoteInactive', not active)
                    tree.style().unpolish(tree)
                    tree.style().polish(tree)
                tree.viewport().update()
        remote = getattr(self, 'remote_window', None)
        if remote is not None and view is not None and view._workspace_mode == 'files':
            remote.set_operating_target(target)
            remote.set_area(target)
        return True

    def remote_focus_area(self, area):
        """Keep the highlighted current row in the main UI, not in the remote."""
        if (self.files_root_hidden_mode and self.expanded_view.isVisible()):
            if self.expanded_view._workspace_mode == 'files' and area == 'files':
                area = 'directory'
            elif self.expanded_view._workspace_mode == 'browser' and area == 'bookmarks':
                area = self._current_web_body_area()
        if not self.expanded_view.isVisible():
            if area == 'pages':
                self.tabs.setFocus(Qt.FocusReason.OtherFocusReason)
            elif area == 'search':
                self.search.setFocus(Qt.FocusReason.OtherFocusReason)
            else:
                area = 'list'
                self.list.setFocus(Qt.FocusReason.OtherFocusReason)
        else:
            view = self.expanded_view
            web_active = getattr(view, 'web_view_active', lambda: False)()
            browser_mode = view._workspace_mode == 'browser'
            order = navigation_order(expanded=True, web=browser_mode,
                                     web_tab_count=self._web_tab_count(),
                                     bookmarks_visible=view.browser_bookmarks_visible)
            area = normalize_area(area, order, current_tab=(
                view.web_view.tabs.currentIndex() if web_active else 0))
            if area == 'files_exp' and view._workspace_mode == 'files':
                # Exp is a logical controller even before a standalone Exp
                # panel has been shown; don't normalize it to legacy 'files'.
                # Retain any live tree cursor without stealing native focus.
                panel = self._current_remote_files_exp()
                if panel is not None:
                    panel._selection_timer.stop()
            elif area not in order:
                area = (('bookmarks' if view.browser_bookmarks_visible else
                         self._current_web_body_area()) if browser_mode else
                        ('directory' if self.files_root_hidden_mode else 'files'))
            if area == 'workspace_files':
                view.files_mode_tab.setFocus(Qt.FocusReason.OtherFocusReason)
            elif area == 'workspace_browser':
                view.browser_mode_tab.setFocus(Qt.FocusReason.OtherFocusReason)
            elif web_active and str(area).startswith('web_body:'):
                index = int(area.split(':', 1)[1])
                if 0 <= index < view.web_view.tabs.count():
                    view.web_view.tabs.setCurrentIndex(index)
                # A non-activating Remote must not steal focus from web forms.
            elif area == 'search':
                self.search.setFocus(Qt.FocusReason.OtherFocusReason)
            elif area == 'pages':
                self.tabs.setFocus(Qt.FocusReason.OtherFocusReason)
            elif area == 'breadcrumb':
                view.address_bar.begin_edit()
            elif area == 'roots':
                view.focus_root(item_id=self._last_root_id)
                # Remote is non-activating: don't rely on Qt.hasFocus() to
                # identify its logical selection after BackTab/reopen.
                selected = next((i for i, button in enumerate(view.root_buttons)
                                 if button.hasFocus()), None)
                if selected is None and view.root_rows:
                    selected = next((i for i, row in enumerate(view.root_rows)
                                     if row.get('item_id') == self._last_root_id), 0)
                if selected is not None:
                    self._last_root_id = view.root_rows[selected].get('item_id')
            else:
                pane = {'files': view.left, 'directory': view.middle,
                        'bookmarks': view.right}.get(area)
                if pane is not None:
                    if area == 'bookmarks' and browser_mode:
                        self._focus_bookmark_first()
                    else:
                        view.focus_panel(pane)
        if getattr(self.expanded_view, 'web_view', None) is not None:
            self.expanded_view.web_view.set_remote_area(
                ('web_body' if str(area).startswith('web_body:') else area)
                if getattr(self.expanded_view, 'web_view_active', lambda: False)() else None)
        # In Files, all three displays (Remote button/caption, column titles,
        # actual/remembered rows) read from one operating-target setter.
        # Browser/search focus labels are transient and leave that Files target
        # untouched so returning to Files restores the previous controller.
        files_target = (self.expanded_view._workspace_mode == 'files'
                        and area in ('files_exp', 'directory'))
        if files_target:
            setter = getattr(self, 'set_files_operating_target', None)
            if callable(setter):
                setter(area)
            else:  # Lightweight non-Qt test doubles.
                self._remote_area = area
        else:
            if self.expanded_view.isVisible():
                for name, pane in (('files', self.expanded_view.left),
                                   ('directory', self.expanded_view.middle),
                                   ('bookmarks', self.expanded_view.right)):
                    pane.tree.remote_highlight_mode = True
                    pane.tree.remote_logical_active = (area == name)
                    inactive = area != name
                    if pane.tree.property('remoteInactive') != inactive:
                        pane.tree.setProperty('remoteInactive', inactive)
                        pane.tree.style().unpolish(pane.tree)
                        pane.tree.style().polish(pane.tree)
                    pane.tree.viewport().update()
            self._remote_area = area
            if (self.expanded_view.isVisible() and
                    self.expanded_view._workspace_mode == 'files'):
                self.expanded_view.set_files_operating_area(area)
            if self.remote_window is not None:
                self.remote_window.set_area(area)
        if area == 'directory' and self.expanded_view.isVisible():
            self.expanded_view.ensure_middle_current_selection()

    def remote_history_command(self, command):
        """Navigate existing history trees directly; no synthetic key events.

        Never call the delete (second) column through a remote command.
        """
        area = self._remote_popup_area
        if area == 'search_history':
            if not self.history_popup.isVisible():
                self._remote_popup_area = None
                self.remote_window.set_area(self._remote_area or 'search')
                return True
            tree = self.history_choices
            visible = self.history_visible_rows()
            if command in ('UP', 'DOWN') and visible:
                row = next_wrapped(visible, tree.currentItem(), -1 if command == 'UP' else 1)
                tree.setCurrentItem(row)
                tree.scrollToItem(row, QAbstractItemView.ScrollHint.EnsureVisible)
            elif command in ('ENTER', 'RIGHT'):
                row = tree.currentItem()
                if row is not None:
                    # A keyword selection replaces the visible content with
                    # classic search results. The main list gains focus in
                    # select_history_keyword(), but the remote's independent
                    # routing area must follow it as well. Otherwise the
                    # highlighted first hit still receives Files-pane clicks.
                    self.history_row_clicked(row, 0)
                    # Category clicks leave the popup open. A closed popup
                    # means a keyword was chosen and results are now active.
                    if not self.history_popup.isVisible():
                        self._remote_area = 'list'
                        self._remote_mouse_last_click = None
            elif command == 'LEFT':
                row = tree.currentItem()
                if row is not None and row.data(0, ROLE_KIND) == 'category':
                    row.setExpanded(False)
                else:
                    self.hide_history_popup()
            if not self.history_popup.isVisible():
                self._remote_popup_area = None
                self.remote_window.set_area(self._remote_area or 'search')
            return True
        if area == 'browser_history':
            web = getattr(self.expanded_view, 'web_view', None)
            if web is None or not web.favorite_popup.isVisible():
                self._remote_popup_area = None
                if self.remote_window is not None:
                    self.remote_window.set_area(self._remote_area or 'bookmarks')
                return True
            tree = web.favorite_choices
            if command in ('UP', 'DOWN'):
                row = move_tree_selection(tree, -1 if command == 'UP' else 1)
                if row is not None:
                    tree.scrollToItem(row, QAbstractItemView.ScrollHint.EnsureVisible)
            elif command in ('RIGHT', 'ENTER'):
                row = tree.currentItem()
                if row is not None:
                    web.url_favorite_clicked(row, 0)  # Never invoke delete via Remote.
            elif command == 'LEFT':
                web.hide_url_favorites()
            if not web.favorite_popup.isVisible():
                self._remote_popup_area = None
                if self.remote_window is not None:
                    self.remote_window.set_area(self._remote_area or 'bookmarks')
            return True
        if area == 'folder_history':
            view = self.expanded_view
            if not view.favorite_popup.isVisible():
                self._remote_popup_area = None
                self.remote_window.set_area(self._remote_area or 'directory')
                return True
            tree = view.favorite_choices
            if command in ('UP', 'DOWN'):
                row = move_tree_selection(tree, -1 if command == 'UP' else 1)
                if row is not None:
                    tree.scrollToItem(row, QAbstractItemView.ScrollHint.EnsureVisible)
            elif command in ('RIGHT', 'ENTER'):
                row = tree.currentItem()
                if row is not None:
                    view.directory_favorite_clicked(row, 0)
            elif command == 'LEFT':
                view.hide_favorite_popup()
            if not view.favorite_popup.isVisible():
                self._remote_popup_area = None
                self.remote_window.set_area(self._remote_area or 'directory')
            return True
        return False

    def remote_cascade_command(self, command):
        """Drive the *visible* cascade selection, not the background list.

        The remote does not send virtual keys. It works with QAction and the
        existing scroll-tree model, matching the menu's native Return/Right
        semantics without giving the popup or IME editor keyboard focus.
        """
        menu = getattr(self, 'menu', None)
        if menu is None or not menu.isVisible():
            return False
        # A Remote Page's wheel always browses the FIRST column. Its selected
        # row may preview one child column, but scrolling must never jump into
        # that child (or cascade all the way to the right). Explicit click,
        # hover, LEFT/RIGHT still use the normal deepest-column behavior.
        remote_root = getattr(self, '_remote_page_menu', None)
        page_wheel = (command in ('UP', 'DOWN')
                      and remote_root is not None and remote_root.isVisible())
        if page_wheel:
            menu = remote_root
        else:
            while (isinstance(getattr(menu, 'child', None), CascadeMenu)
                   and menu.child.isVisible()):
                menu.open_mode = 'keyboard'
                menu.outside_since = None
                menu = menu.child
        menu.open_mode = 'keyboard'
        menu.outside_since = None
        menu.hover_timer.stop()

        if command in ('CLICK', 'DOUBLE_CLICK'):
            action = menu.activeAction()
            if action is not None and action.isEnabled():
                row = action.data()
                folder = isinstance(row, dict) and row.get('item_kind') in ('category', 'directory')
                opener = action in menu.openers
                double_folder = (folder and opener and
                                 menu._double_folder_mode())
                token = (id(menu), id(action))
                if command == 'CLICK':
                    self._remote_mouse_menu_click = token
                    if double_folder:
                        menu.setActiveAction(action)  # Select; second click opens.
                    elif opener and folder and row.get('item_kind') == 'directory':
                        # Match the menu's native wait for a possible second
                        # click, which may instead launch this folder.
                        menu._queue_folder_single_click(action)
                    elif opener:
                        menu.open_current('keyboard')
                    elif isinstance(row, dict):
                        self.run_menu_item(row)
                    elif action.property('launch_right_arrow_executes'):
                        action.trigger()
                elif token == getattr(self, '_remote_mouse_menu_click', None):
                    self._remote_mouse_menu_click = None
                    if double_folder:
                        menu.open_current('keyboard')
                    elif folder and row.get('item_kind') == 'directory':
                        menu.folder_click_timer.stop()
                        menu._folder_click_action = None
                        self.run_menu_item(row)
                    # A leaf already executed on the first click. Never run twice.
            else:
                self._remote_mouse_menu_click = None
            if self.remote_window is not None:
                self.remote_window.set_area(
                    'cascade' if self.menu is not None and self.menu.isVisible()
                    else (self._remote_area or 'list'))
            return True

        if command in ('UP', 'DOWN'):
            direction = -1 if command == 'UP' else 1
            if isinstance(menu, AppCascadeMenu):
                item = move_tree_selection(menu.tree, direction)
                if item is not None:
                    menu.tree.scrollToItem(item, QAbstractItemView.ScrollHint.EnsureVisible)
            elif menu.filter_action is not None:
                menu._move_filtered_selection(direction)
            else:
                actions = [a for a in menu.actions()
                           if a.isVisible() and a.isEnabled() and not a.isSeparator()
                           and (isinstance(a.data(), dict)
                                or bool(a.property('launch_right_arrow_executes')))]
                if actions:
                    menu.setActiveAction(next_wrapped(actions, menu.activeAction(), direction))
            # Page wheel = first-column selection plus a ONE-LEVEL preview.
            # All deeper columns remain available through mouse/explicit keys.
            if page_wheel:
                self._remote_page_wheel_expand(menu)
        elif command == 'LEFT':
            menu.close_one_level()
        elif command in ('RIGHT', 'ENTER'):
            action = menu.activeAction()
            if action is not None and action.isEnabled():
                row = action.data()
                if isinstance(menu, AppCascadeMenu):
                    if isinstance(row, dict):
                        self.run_menu_item(row)
                elif command == 'RIGHT':
                    if action in menu.openers:
                        menu.open_current('keyboard')
                    elif action.property('launch_right_arrow_executes'):
                        action.trigger()
                    elif isinstance(row, dict):
                        self.run_menu_item(row)
                elif isinstance(row, dict) and row.get('item_kind') == 'directory':
                    self.run_menu_item(row)
                elif action in menu.openers:
                    menu.open_current('keyboard')
                elif isinstance(row, dict):
                    self.run_menu_item(row)
                elif action.property('launch_right_arrow_executes'):
                    action.trigger()
        else:
            return False
        if self.remote_window is not None:
            self.remote_window.set_area(
                'cascade' if self.menu is not None and self.menu.isVisible()
                else (self._remote_area or 'list'))
        return True

    @staticmethod
    def _remote_page_wheel_expand(menu):
        """Preview only the selected Page-root item's immediate child column.

        A wheel gesture NEVER triggers leaf actions, advances into the preview,
        or leaves previously opened grandchildren floating beside a new row.
        Ordinary compact menus and mouse-hover expansion are unaffected.
        """
        if not getattr(menu, 'remote_page_navigation', False):
            return False
        action = menu.activeAction()
        child = getattr(menu, 'child', None)
        menu.hover_timer.stop()

        # Leaf/empty rows have no preview; discard an obsolete former child.
        if action is None or action not in menu.openers or not action.isEnabled():
            if child is not None:
                child.close()
                child.deleteLater()
                menu.child = None
            return False

        if child is not None and child.isVisible() and child.owner_action is action:
            # An earlier pointer hover may have opened a third/fourth column.
            # Roll back to exactly one preview column on the next wheel tick.
            grandchild = getattr(child, 'child', None)
            if grandchild is not None:
                grandchild.close()
                grandchild.deleteLater()
                child.child = None
            child.hover_timer.stop()
            return False

        # The existing opener replaces any previous preview and shares the
        # compact menu's search, icons and normal hover behavior.
        menu.openers[action]('keyboard')
        return True

    def remote_mouse_click(self, *, double=False):
        """Dispatch the wheel pad like the real mouse, not the Enter key.

        Native clicks select/preview; native double-clicks activate. Folder
        clicks respect the configured mode, except first-column folders and
        bookmark folders which always use their native single-click policy.
        """
        expanded = self.expanded_view.isVisible()
        remote_page = getattr(self, '_remote_page_menu', None)
        remote_page_visible = remote_page is not None and remote_page.isVisible()
        if (expanded and not remote_page_visible
                and getattr(self.expanded_view, 'web_view_active', lambda: False)()):
            area = self._remote_area
            web = self.expanded_view.web_view
            if str(area).startswith('web_body:') or area == 'web_body':
                self._remote_mouse_last_click = None
                if not double:
                    web.focus_page()
                return
        # The Remote pad does not take keyboard focus.  While an inline
        # filename/folder rename is open, its click means COMMIT, not click
        # (or double-click) on the still-selected filesystem row.
        if expanded:
            commit_rename = getattr(self.expanded_view, 'commit_remote_inline_rename', None)
            if callable(commit_rename) and commit_rename():
                self._remote_mouse_last_click = None
                self._remote_mouse_menu_click = None
                return
        area = self._remote_area or starting_area(
            self._last_focus_area, expanded=expanded)
        if not expanded and getattr(self, 'remote_15_mode', False):
            # The Files canvas is temporarily hidden by global search.
            # Continue to operate the search results, even when the retained
            # Files target is Files Exp; do not change that saved target.
            area = 'list'
        if expanded and area == 'directory':
            repair = getattr(self.expanded_view, 'ensure_middle_current_selection', None)
            if callable(repair):
                repair()
        if double:
            # A popup may have been closed by the first click. It must never
            # reactivate the background list on the second mouse press.
            if getattr(self, '_remote_popup_area', None):
                return
            dispatch_cascade = getattr(self, 'remote_cascade_command', None)
            if dispatch_cascade is not None and dispatch_cascade('DOUBLE_CLICK'):
                return
        else:
            if getattr(self, '_remote_popup_area', None):
                self._remote_mouse_last_click = None
                if self.remote_history_command('ENTER'):
                    return
            if area == 'search':
                self._remote_mouse_last_click = None
                if not self.history_popup.isVisible():
                    self.show_history_popup()
                if self.history_popup.isVisible():
                    self._remote_popup_area = 'search_history'
                    self.remote_window.set_area('search_history')
                return
            dispatch_cascade = getattr(self, 'remote_cascade_command', None)
            if dispatch_cascade is not None and dispatch_cascade('CLICK'):
                self._remote_mouse_last_click = None
                return

        if expanded and area == 'breadcrumb':
            self._remote_mouse_last_click = None
            if not double:
                self.expanded_view.address_bar._submit()
            return
        if area in ('workspace_files', 'workspace_browser'):
            self._remote_mouse_last_click = None
            if not double:
                mode = 'files' if area == 'workspace_files' else 'browser'
                self.expanded_view.switch_workspace(mode)
            return
        if area in ('pages',):
            self._remote_mouse_last_click = None
            # The selected Page tab is already current; no Enter-style jump.
            return
        view = self.expanded_view
        expanded = view.isVisible()
        if expanded and area == 'roots':
            self._remote_mouse_last_click = None
            if double or not view.root_buttons:
                return
            current = next((i for i, button in enumerate(view.root_buttons)
                            if button.hasFocus()), None)
            if current is None:
                current = next((i for i, row in enumerate(view.root_rows)
                                if row.get('item_id') == self._last_root_id), 0)
            view.root_action(view.root_rows[current], view.root_buttons[current])
            return
        if not expanded:
            if area != 'list':
                self._remote_mouse_last_click = None
                return
            item = self.list.currentItem()
            row = item.data(0, Qt.ItemDataRole.UserRole) if item is not None else None
            target = ('list', row.get('item_id') or id(row)) if isinstance(row, dict) else None
            if double:
                if (target is not None and target == getattr(self, '_remote_mouse_last_click', None)
                        and not (getattr(self, 'selection', None) or
                                 (isinstance(row, dict) and row.get('_search_selection_owner')))):
                    self.activate(row)
                self._remote_mouse_last_click = None
            else:
                self._remote_mouse_last_click = target
                # A mouse click on a recipient's checkbox toggles it. Qt's
                # itemChanged handler owns the existing selection logic.
                if (isinstance(row, dict) and row.get('choice_id') and
                        (getattr(self, 'selection', None) or row.get('_search_selection_owner'))):
                    checked = item.checkState(0) == Qt.CheckState.Checked
                    item.setCheckState(0, Qt.CheckState.Unchecked if checked
                                       else Qt.CheckState.Checked)
            return

        if expanded and area == 'files_exp':
            self._remote_mouse_last_click = None
            panel = self._current_remote_files_exp()
            if panel is not None and not double:
                panel.remote_activate_current()
                self.remote_focus_area('files_exp')
            return
        pane = {'files': view.left, 'directory': view.middle,
                'bookmarks': view.right}.get(area)
        if pane is None:
            return
        item = pane.tree.currentItem()
        row = view.row_data(item)
        if row is None:
            self._remote_mouse_last_click = None
            return
        target = (area, row.get('item_id') or row.get('path') or id(row))
        if double:
            if target != getattr(self, '_remote_mouse_last_click', None):
                self._remote_mouse_last_click = None
                return
            self._remote_mouse_last_click = None
        else:
            self._remote_mouse_last_click = target
        folder = row.get('item_kind') in ('category', 'directory')
        if pane is view.left:
            if not double:
                view.choose_files(item, 0)
            elif not folder:
                view.activate_row(pane, item)
        elif pane is view.middle:
            if folder:
                if double:
                    if getattr(self, 'folder_open_mode', 'single') == 'double':
                        view.activate_row(pane, item)
                else:
                    view.choose_middle(item, 0)
            elif double:
                view.activate_row(pane, item)
        elif pane is view.right:
            # Browser selection and activation are separate. A wheel turn
            # only selects; an explicit Remote click opens the chosen URL.
            if not double:
                if folder:
                    view.choose_bookmark(item, 0)
                else:
                    view.activate_row(pane, item)

    def remote_web_context_menu(self, area):
        """Remote right click is page/tab-level, never a fabricated DOM click."""
        remote = getattr(self, 'remote_window', None)
        view = self.expanded_view
        if (remote is None or not remote.isVisible() or
                not getattr(view, 'web_view_active', lambda: False)() or area not in ('web_tabs', 'web_body')):
            return
        web = view.web_view
        previous = getattr(self, '_remote_web_popup', None)
        if previous is not None and previous.isVisible():
            previous.close()
            return
        menu = web.tab_context_menu() if area == 'web_tabs' else web.page_context_menu()
        self._remote_web_popup = menu
        menu.aboutToHide.connect(lambda: setattr(self, '_remote_web_popup', None))
        menu.aboutToHide.connect(menu.deleteLater)
        pad = remote.pad
        point = pad.mapToGlobal(QPoint(pad.width() + 4, 0))
        screen = QApplication.screenAt(pad.mapToGlobal(pad.rect().center())) or QApplication.primaryScreen()
        menu.ensurePolished()
        size = menu.sizeHint()
        if screen is not None:
            rect = screen.availableGeometry()
            if point.x() + size.width() > rect.right() + 1:
                point.setX(pad.mapToGlobal(QPoint(-size.width() - 4, 0)).x())
            if point.y() + size.height() > rect.bottom() + 1:
                point.setY(rect.bottom() + 1 - size.height())
            point.setX(max(rect.left(), min(point.x(), rect.right() + 1 - size.width())))
            point.setY(max(rect.top(), min(point.y(), rect.bottom() + 1 - size.height())))
        menu.popup(point)

    def remote_context_menu(self):
        """Open the selected object's existing menu beside the wheel pad."""
        remote = getattr(self, 'remote_window', None)
        if remote is None or not remote.isVisible():
            return
        pad = remote.pad
        pos = pad.mapToGlobal(QPoint(pad.width() + 4, 0))
        web = self.expanded_view
        if (getattr(web, 'web_view_active', lambda: False)() and
                (self._remote_area == 'web_tabs' or
                 str(self._remote_area).startswith('web_body'))):
            self.remote_web_context_menu('web_body' if
                str(self._remote_area).startswith('web_body:') else self._remote_area)
            return
        cascade = getattr(self, 'menu', None)
        if cascade is not None and cascade.isVisible():
            while (isinstance(getattr(cascade, 'child', None), CascadeMenu)
                   and cascade.child.isVisible()):
                cascade = cascade.child
            action = cascade.activeAction()
            row = action.data() if action is not None else None
            if isinstance(row, dict):
                self.show_launch_context_menu(pos, row, context_parent=cascade)
            return
        if getattr(self, '_remote_popup_area', None):
            return
        expanded = self.expanded_view.isVisible()
        area = self._remote_area or starting_area(self._last_focus_area, expanded=expanded)
        if not expanded and getattr(self, 'remote_15_mode', False):
            area = 'list'  # Search results overlay is the live target.
        if not expanded and area == 'list':
            item = self.list.currentItem()
            row = item.data(0, Qt.ItemDataRole.UserRole) if item else None
            if isinstance(row, dict):
                self.show_launch_context_menu(pos, row)
            return
        if not expanded:
            return
        view = self.expanded_view
        if getattr(view, 'web_view_active', lambda: False)() and (
                area == 'web_tabs' or str(area).startswith('web_body')):
            self.remote_web_context_menu('web_body' if str(area).startswith('web_body:') else area)
            return
        if area == 'files_exp':
            panel = self._current_remote_files_exp()
            path = panel.remote_current_folder_path() if panel is not None else None
            if path:
                self.show_files_exp_folder_menu(path, pos)
                self.remote_focus_area('files_exp')
            return
        if area == 'directory':
            view.ensure_middle_current_selection()
        pane = {'files': view.left, 'directory': view.middle,
                'bookmarks': view.right}.get(area)
        if pane is None:
            return
        item = pane.tree.currentItem()
        if item is None:
            if pane is view.middle and view.current_directory():
                self.show_expanded_background_paste_menu(pos)
            return
        rect = pane.tree.visualItemRect(item)
        if rect.isValid():
            view.context_menu(pane, rect.center(), global_pos=pos)

    def update_remote_more_menu(self):
        """Reflect the same enabled state as the breadcrumb heart control."""
        remote = getattr(self, 'remote_window', None)
        if remote is None:
            return
        view = self.expanded_view
        available = bool(view.isVisible() and view.favorite_save.isEnabled()
                         and view.current_directory())
        # Match the three icons on their actual Launch controls, including
        # theme changes and the heart's registered/unregistered state.
        remote.update_more_menu_icons(self.theme_button.icon(),
                                      self.history_category_action.icon(),
                                      view.favorite_save.text())
        remote.set_favorite_action_available(available)
        # Browser: mirror the active Web address-bar heart, not the Files
        # breadcrumb (whose path is retained while switching workspaces).
        mode = getattr(view, '_workspace_mode', 'files')
        url_available = False
        if mode == 'browser':
            web = getattr(view, 'web_view', None)
            url_available = bool(view.isVisible() and web is not None
                                 and view.web_view_active() and web.favorite_save.isEnabled()
                                 and web.current_url_for_favorite())
        if hasattr(remote, 'set_url_favorite_action_available'):
            remote.set_url_favorite_action_available(url_available)
        if hasattr(remote, 'set_more_menu_mode'):
            remote.set_more_menu_mode(
                view._workspace_mode,
                can_add_tab=view.web_view_active())

    def files_history_button_clicked(self):
        """Same two-click history contract as Remote, without requiring Remote.

        First click opens the *existing* main search-history popup; a second
        click confirms its current row (a category toggles rather than runs).
        File/Folder selection and the Files breadcrumb remain untouched until
        a history keyword is deliberately confirmed.
        """
        if self.history_popup.isVisible():
            row = self.history_choices.currentItem()
            if row is not None:
                self.history_row_clicked(row, 0)  # Never the delete column.
            if not self.history_popup.isVisible() and self._remote_popup_area == 'search_history':
                self._remote_popup_area = None
            return
        self.show_history_popup(anchor=self.expanded_view.files_history_button)
        if self.history_popup.isVisible() and self.remote_window is not None and self.remote_window.isVisible():
            self._remote_popup_area = 'search_history'
            self.remote_window.set_area('search_history')

    def remote_search_result_double_click(self):
        """Run the current *visible global-search hit*, never a history row.

        History single-click remains responsible for opening/confirming a
        keyword. A double-click deliberately targets the main results list;
        empty/hidden lists and non-search menus must never be activated.
        """
        results = self.list
        if (not self.search.text().strip() or not results.isVisible()
                or self.history_popup.isVisible()):
            return
        item = results.currentItem()
        row = item.data(0, Qt.ItemDataRole.UserRole) if item is not None else None
        if not isinstance(row, dict) or not row.get('enabled', True):
            return
        # Use the same result activation path as Enter / native double-click.
        self.activate(row)

    def _current_remote_files_exp(self):
        """Select the existing Exp tree independently of Remote placement.

        Embedded Exp is in Launch's first column; standard Remote can also
        own a separate Exp tool window. Never create/rebuild a tree just to
        move the operating target.
        """
        view = self.expanded_view
        if getattr(self, 'files_exp_embedded_mode', False):
            return getattr(view, 'embedded_files_exp', None)
        remote = getattr(self, 'remote_window', None)
        return getattr(remote, 'files_exp_panel', None) if remote is not None else None

    def remote_exp_right_to_list(self):
        """Exp → List: explicitly commit Exp and hand off the controller.

        Works in both the floating 1.5-column experiment and the ordinary
        Remote placement (embedded or separate Files Exp). Wheel only previews
        a candidate; → commits its folder to the breadcrumb.
        """
        view = self.expanded_view
        if not view.isVisible() or view._workspace_mode != 'files':
            return False
        panel = self._current_remote_files_exp()
        if panel is None:
            return False
        directory = panel.remote_current_folder_path()
        if directory:
            changed = self.navigate_files_exp_folder(directory)
        else:
            # PCは実フォルダーパスを持たない仮想ルート。
            changed = (panel._is_pc_index(panel.tree.currentIndex())
                       and self.navigate_files_exp_pc())
        if not changed:
            return False
        self.remote_focus_area('directory')
        return True

    def remote_list_left_to_exp(self):
        """List → Exp: first/empty row hands control back to breadcrumb Exp.

        The identical boundary rule applies to all Remote placements. Keep
        the List cursor/breadcrumb intact and select the matching Exp row.
        """
        view = self.expanded_view
        if not view.isVisible() or view._workspace_mode != 'files':
            return False
        panel = self._current_remote_files_exp()
        if panel is None:
            return False
        tree = view.middle.tree
        first = next((item for i in range(tree.topLevelItemCount())
                      if (item := tree.topLevelItem(i)) is not None
                      and view.row_data(item) is not None), None)
        # No items == already at the List's left boundary. A zero-row
        # folder must not trap the Remote in Files List.
        if first is not None and tree.currentItem() is not first:
            return False
        directory = view.current_directory()
        if directory:
            aligned = panel.sync_current_directory(directory)
        else:
            # パンくずが「PC」の場合は、枝を閉じずにPC行だけを選択する。
            aligned = panel.remote_select_pc_root()
        if not aligned:
            return False
        self.remote_focus_area('files_exp')
        return True

    def remote_command(self, command):
        """Direct Qt widget/model commands, NEVER SendKeys or QKeyEvent injection."""
        if command == 'CLOSE':
            self.hide_remote()
            return
        if not self.isVisible() or self.isMinimized():
            self.hide_remote()
            return
        if command == 'SEARCH_RESULT_DOUBLE_CLICK':
            self.remote_search_result_double_click()
            return
        if command == 'MORE_MENU':
            self.update_remote_more_menu()
            self.remote_window.show_more_menu()
            return
        if command == 'REMOTE_SETTINGS':
            # Wait until the Remote QMenu has closed before opening the
            # Launcher settings menu, avoiding Qt popup-to-popup races.
            QTimer.singleShot(0, lambda: self.open_theme_menu_at(self.remote_window.more_button))
            return
        if command == 'REMOTE_CATEGORY_ADD':
            # Reuse the search + QAction after the popup is dismissed, so
            # the native text-input dialog can take focus normally.
            QTimer.singleShot(0, self.history_category_action.trigger)
            return
        if command == 'REMOTE_NEW_WEB_TAB':
            view = self.expanded_view
            if view.isVisible() and view._workspace_mode == 'browser' and view.web_view_active():
                view.web_view.add_tab(self.webview_settings.get(
                    'new_tab_url', 'https://www.google.com/'))
            return
        if command in ('REMOTE_TARGET_EXP', 'REMOTE_TARGET_LIST'):
            view = self.expanded_view
            if not view.isVisible():
                return
            target = 'files_exp' if command == 'REMOTE_TARGET_EXP' else 'directory'
            if view._workspace_mode != 'files':
                # A Remote Files-target click also returns from Browser.
                # Keep the breadcrumb, tree expansion and List selection;
                # the workspace callback must not reset the Files cursor.
                self._remote_preserve_files_selection = True
                try:
                    view.show_files_view()
                finally:
                    self._remote_preserve_files_selection = False
            # Selecting the controller is not a folder navigation/row commit.
            # All Remote placements use the one authoritative operating target.
            setter = getattr(self, 'set_files_operating_target', None)
            if callable(setter):
                setter(target)
            else:  # Lightweight legacy/test-double compatibility.
                self.remote_focus_area(target)
            return
        if command in ('WORKSPACE_FILES', 'WORKSPACE_BROWSER'):
            view = self.expanded_view
            if not view.isVisible():
                return
            if command == 'WORKSPACE_FILES':
                # Workspace switch != HOME: retain the breadcrumb, Files Exp
                # expanded/selected rows, and the Files column-2 current item.
                # Suppress the generic Browser->Files focus handler, which can
                # otherwise select a root row or implicitly select a file.
                self._remote_preserve_files_selection = True
                try:
                    view.show_files_view()
                finally:
                    self._remote_preserve_files_selection = False
                # Restore the previous Files target without changing the
                # breadcrumb or forcing a List item selection.
                setter = getattr(self, 'set_files_operating_target', None)
                if callable(setter):
                    setter(getattr(self, '_files_operating_target', 'directory'))
                else:  # Legacy launcher/test-double fallback.
                    changed = self._remote_area != 'directory'
                    self._remote_area = 'directory'
                    if changed and self.remote_window is not None:
                        self.remote_window.set_area('directory')
                    for name, pane in (('files', view.left), ('directory', view.middle)):
                        tree = pane.tree
                        tree.remote_highlight_mode = True
                        tree.remote_logical_active = name == 'directory'
                        inactive = name != 'directory'
                        if tree.property('remoteInactive') != inactive:
                            tree.setProperty('remoteInactive', inactive)
                            tree.style().unpolish(tree)
                            tree.style().polish(tree)
                        tree.viewport().update()
            elif view.switch_workspace('browser'):
                if self.files_root_hidden_mode:
                    # Explicitly preserve hidden Bookmarks on Remote Browser.
                    # Unlike legacy mode, do not call show_browser_bookmarks().
                    view.set_browser_bookmarks_visible(False, persist=False)
                    self.remote_focus_area(self._current_web_body_area())
                else:
                    # The original Bookmark focus rule remains the default.
                    if not view.browser_bookmarks_visible:
                        view.show_browser_bookmarks()
                    self.remote_focus_area('bookmarks')
            return
        if command == 'REMOTE_FAVORITE_SAVE':
            # Exactly the same QToolButton as the breadcrumb heart.
            view = self.expanded_view
            if (view.isVisible() and getattr(view, '_workspace_mode', 'files') == 'files'
                    and view.current_directory() and view.favorite_save.isEnabled()):
                view.favorite_save.click()
            return
        if command == 'REMOTE_URL_FAVORITE_SAVE':
            # Reuse Browser's live address-bar heart. It owns URL validation,
            # duplicate handling, JSON persistence, and enabled state.
            view = self.expanded_view
            if view.isVisible() and view._workspace_mode == 'browser' and view.web_view_active():
                web = view.web_view
                if web is not None and web.favorite_save.isEnabled() and web.current_url_for_favorite():
                    web.favorite_save.click()
            return
        if command == 'CONTEXT_MENU':
            self.remote_context_menu()
            return
        if command == 'REMOTE_CURRENT_FOLDER_MENU':
            self.show_remote_current_folder_menu()
            return
        if command == 'REMOTE_FILES_FIRST_COLUMN_MENU':
            self.show_remote_files_first_column_menu()
            return
        if command == 'REMOTE_BROWSER_BOOKMARK_MENU':
            self.show_remote_browser_bookmark_menu()
            return
        if command == 'BACKGROUND_CONTEXT_MENU':
            # Same action builder as a right-click on Files column 2 blank
            # space.  Use the actual pointer position beside Remote; neither
            # the selected file nor the logical current column is changed.
            view = self.expanded_view
            if view.isVisible() and view.current_directory():
                self.show_expanded_background_paste_menu(QCursor.pos())
            return
        if command == 'REMOTE_FOLDER_DESELECT':
            view = self.expanded_view
            if view.isVisible() and view._workspace_mode == 'files':
                tree = view.middle.tree
                tree.deliberate_blank_selection = True
                tree.clearSelection()
                tree.viewport().update()
                self.remote_focus_area('directory')
            return
        if command == 'FOLDER_UP':
            if self.expanded_view.isVisible():
                self.expanded_view.go_up()
                self.remote_focus_area('directory')
            return
        if command not in ('CLICK', 'DOUBLE_CLICK'):
            self._remote_mouse_last_click = None
            self._remote_mouse_menu_click = None
        expanded = self.expanded_view.isVisible()
        web_active = expanded and getattr(self.expanded_view, 'web_view_active', lambda: False)()
        browser_mode = expanded and getattr(self.expanded_view, '_workspace_mode', 'files') == 'browser'
        area = self._remote_area or starting_area(
            self._last_focus_area, expanded=expanded, web=web_active,
            web_tab_count=self._web_tab_count(),
            bookmarks_visible=self.expanded_view.browser_bookmarks_visible)
        if command == 'SEARCH_HISTORY':
            if (getattr(self, '_remote_popup_area', None) == 'search_history'
                    and self.history_popup.isVisible()):
                # First click opens the history. A subsequent click on the SAME
                # Remote button confirms the selected row, just like ENTER.
                # Category rows only expand/collapse; no selection is a no-op.
                self.remote_history_command('ENTER')
                return
            self.show_history_popup()
            if self.history_popup.isVisible():
                self._remote_popup_area = 'search_history'
            self.remote_window.set_area(self._remote_popup_area or area)
            return
        if command == 'FOLDER_HISTORY':
            view = self.expanded_view
            if not view.isVisible():
                self.remote_window.set_area('directory')
                return
            # The same Remote button serves Files breadcrumb favorites and
            # Browser address-bar URL favorites; no second remote button.
            if browser_mode:
                web = getattr(view, 'web_view', None)
                if web is None or not view.web_view_active():
                    return  # External browser mode has no embedded address bar.
                if (self._remote_popup_area == 'browser_history'
                        and web.favorite_popup.isVisible()):
                    self.remote_history_command('ENTER')
                    return
                if self._remote_popup_area == 'folder_history':
                    view.hide_favorite_popup()
                elif self._remote_popup_area == 'search_history':
                    self.hide_history_popup()
                self._remote_popup_area = None
                web.toggle_url_favorites()
                if web.favorite_popup.isVisible():
                    self._remote_popup_area = 'browser_history'
                self.remote_window.set_area(self._remote_popup_area or area)
                return
            if (self._remote_popup_area == 'folder_history'
                    and view.favorite_popup.isVisible()):
                self.remote_history_command('ENTER')
                return
            if self._remote_popup_area == 'browser_history' and view.web_view is not None:
                view.web_view.hide_url_favorites()
            self._remote_popup_area = None
            view.toggle_directory_favorites()
            if view.favorite_popup.isVisible():
                self._remote_popup_area = 'folder_history'
            self.remote_window.set_area(self._remote_popup_area or area)
            return
        if command == 'HOME':
            if getattr(self, '_remote_popup_area', None) == 'search_history':
                self.hide_history_popup()
            elif getattr(self, '_remote_popup_area', None) == 'folder_history':
                self.expanded_view.hide_favorite_popup()
            elif getattr(self, '_remote_popup_area', None) == 'browser_history':
                web = getattr(self.expanded_view, 'web_view', None)
                if web is not None:
                    web.hide_url_favorites()
            self._remote_popup_area = None
            self.navigate_home()
            expanded = self.expanded_view.isVisible()
            self.remote_focus_area(('directory' if self.files_root_hidden_mode else 'files')
                                   if expanded else 'list')
            return
        if command == 'SEARCH':
            self.hide_remote()
            # A non-activating Tool can disappear without giving the launcher
            # native foreground status. This is a direct user click: repair the
            # normal-window Z-order before handing control to the IME editor.
            self.raise_()
            if not self.dismiss_on_outside_click:
                windows.raise_normal_window(int(self.winId()))
            self.activateWindow()
            self.focus_search()
            QTimer.singleShot(0, self.focus_search)
            return
        if command in ('TAB', 'BACKTAB') and self.files_root_hidden_mode:
            return  # No column-switch commands in the experimental mode.
        if command in ('TAB', 'BACKTAB'):
            if getattr(self, '_remote_popup_area', None) == 'search_history':
                self.hide_history_popup()
            elif getattr(self, '_remote_popup_area', None) == 'folder_history':
                self.expanded_view.hide_favorite_popup()
            elif getattr(self, '_remote_popup_area', None) == 'browser_history':
                web = getattr(self.expanded_view, 'web_view', None)
                if web is not None:
                    web.hide_url_favorites()
            self._remote_popup_area = None
            # Only the Remote uses this small ring. Keyboard TAB is untouched.
            from remote_navigation import remote_tab_target
            target = remote_tab_target(
                area, expanded=expanded, web=browser_mode,
                backward=(command == 'BACKTAB'))
            if browser_mode and not self.expanded_view.browser_bookmarks_visible:
                self.expanded_view.show_browser_bookmarks()
            self.remote_focus_area(target)
            return
        if command in ('CLICK', 'DOUBLE_CLICK'):
            self.remote_mouse_click(double=command == 'DOUBLE_CLICK')
            return
        if command not in ('UP', 'DOWN', 'LEFT', 'RIGHT', 'ENTER'):
            return
        if getattr(self, '_remote_popup_area', None) and self.remote_history_command(command):
            return
        # A nested cascade is visually in front of the main results. Route
        # the wheel/click to that column before considering the background.
        dispatch_cascade = getattr(self, 'remote_cascade_command', None)
        remote_page = getattr(self, '_remote_page_menu', None)
        remote_page_visible = remote_page is not None and remote_page.isVisible()
        if (remote_page_visible or not (web_active and str(area).startswith('web_body'))):
            if dispatch_cascade is not None and dispatch_cascade(command):
                return
        if (expanded and not browser_mode and area == 'files_exp'):
            panel = self._current_remote_files_exp()
            if panel is not None:
                if command in ('UP', 'DOWN'):
                    panel.remote_step(-1 if command == 'UP' else 1)
                elif command == 'RIGHT':
                    # Exp → List is a Remote-wide navigation contract.
                    if self.remote_exp_right_to_list():
                        return
                elif command == 'LEFT':
                    panel.remote_branch(-1)
                elif command == 'ENTER':
                    panel.remote_activate_current()
                self.remote_focus_area('files_exp')
            return
        if (self.files_root_hidden_mode and expanded and not browser_mode
                and area != 'directory'):
            area = 'directory'
            self.remote_focus_area(area)
        step = (-1 if command in ('UP', 'LEFT') else 1)
        if web_active and str(area).startswith('web_body'):
            browser = self.expanded_view.web_view
            if command in ('UP', 'DOWN'):
                browser.scroll_page(step)
            elif command == 'LEFT':
                browser.go_back()
            elif command == 'RIGHT':
                browser.go_forward()
            elif command == 'ENTER':
                browser.focus_page()
            return
        if area in ('workspace_files', 'workspace_browser'):
            if command in ('RIGHT', 'ENTER'):
                mode = 'files' if area == 'workspace_files' else 'browser'
                self.expanded_view.switch_workspace(mode)
            return
        if area == 'search':
            if command == 'ENTER':
                self.hide_remote()
                self.focus_search()
            elif command in ('UP', 'DOWN'):
                self.remote_focus_area('directory' if expanded else 'list')
                self.remote_command(command)
            return
        if area == 'breadcrumb':
            view = self.expanded_view
            if command in ('UP', 'DOWN'):
                view.preview_directory_favorite_steps(step)
            elif command in ('ENTER', 'RIGHT'):
                view.address_bar._submit()
            return
        if area == 'pages':
            if command in ('LEFT', 'RIGHT', 'UP', 'DOWN') and self.tabs.count():
                index = max(0, min(self.tabs.count() - 1,
                                   self.tabs.currentIndex() + step))
                self.tabs.setCurrentIndex(index)
            elif command == 'ENTER':
                self.remote_focus_area('roots' if expanded else 'list')
            return
        if not expanded:
            tree = self.list
            if command in ('UP', 'DOWN'):
                move_tree_selection(tree, step)
                tree.setFocus(Qt.FocusReason.OtherFocusReason)
            elif command == 'LEFT':
                self.go_back()
            elif command in ('RIGHT', 'ENTER'):
                item = tree.currentItem()
                if item is not None:
                    row = item.data(0, Qt.ItemDataRole.UserRole)
                    if row is not None:
                        self.activate(row)
            return
        view = self.expanded_view
        if area == 'roots':
            if not view.root_buttons:
                return
            # The Remote has a logical selection even when Windows focus is
            # elsewhere. It must be authoritative for wheel/arrow/activation.
            current = next((i for i, row in enumerate(view.root_rows)
                            if row.get('item_id') == self._last_root_id), 0)
            if command in ('UP', 'DOWN', 'LEFT', 'RIGHT'):
                current = root_step(current, step, len(view.root_buttons))
                view.focus_root(index=current)
                self._last_root_id = view.root_rows[current].get('item_id')
            else:
                view.root_action(view.root_rows[current], view.root_buttons[current])
            return
        pane = {'files': view.left, 'directory': view.middle,
                'bookmarks': view.right}.get(area)
        if pane is None:
            return
        tree = pane.tree
        if area == 'directory':
            view.ensure_middle_current_selection()
        if command in ('UP', 'DOWN'):
            item = move_tree_selection(tree, step)
            if item is not None and pane is view.left:
                view.choose_files(item, 0)
            return
        if command == 'LEFT':
            if pane is view.middle:
                # The first List row (or 0 items) is the shared Exp boundary.
                if self.remote_list_left_to_exp():
                    return
                target = view.navigate_left_from_middle()
                if target == 'files':
                    self.remote_focus_area('directory' if self.files_root_hidden_mode else 'files')
            elif pane is view.right:
                self.remote_focus_area('workspace_browser')
            # Files first column is already the leftmost folder column.
            return
        item = tree.currentItem()
        if item is None:
            return
        row = view.row_data(item)
        if row is None:
            return
        if command == 'ENTER':
            view.enter_row(pane, item)
            return
        if command == 'RIGHT':
            folder = row.get('item_kind') in ('category', 'directory')
            action = row_right_action(area, folder)
            if action == 'enter_directory_panel':
                view.choose_files(item, 0)
                self.remote_focus_area('directory')
            elif action == 'descend':
                view.navigate_middle(row)
            elif action == 'cascade':
                view.open_cascade(row, tree, item)
            else:
                self.activate(row)

    def minimize_launcher(self):
        """Native minimization; tray/global hotkey can restore this window."""
        if self.dismiss_on_outside_click:
            return  # Legacy mode has no minimize command.
        getattr(self, 'hide_remote', lambda: None)()
        self.hide_history_popup()
        self.expanded_view.hide_favorite_popup()
        if self.menu:
            self.menu.close()
        self._minimize_restore_maximized = self.isMaximized()
        self.showMinimized()

    def set_folder_open_mode(self, mode):
        self.folder_open_mode = read_folder_open_mode(mode)
        self.settings.setValue('folder_open_mode', self.folder_open_mode)
        self.settings.sync()
        self.footer.setText(
            'Files第2列のフォルダーはダブルクリックで開きます。第1列・ブックマークはシングルクリックです。'
            if is_double_click_folder(self.folder_open_mode)
            else 'フォルダーのシングルクリック移動を有効にしました。')

    def set_vdi_no_cursor_warp(self, enabled):
        """Opt-in no-warp navigation for Citrix and other remote desktops.

        A remote process cannot guarantee moving the actual client cursor:
        keep wheel selection/focus, but never create a second fake pointer.
        """
        self.vdi_no_cursor_warp = bool(enabled)
        self.pointer_warp_enabled = not self.vdi_no_cursor_warp
        self.settings.setValue('vdi_no_cursor_warp', self.vdi_no_cursor_warp)
        self.settings.sync()
        view = getattr(self, 'expanded_view', None)
        if view is not None:
            view.cancel_bookmark_pointer_follow()
            view._middle_follow_pending = None
            view._files_follow_pending = None
            view._wheel_root_follow_pending = None
            view._middle_vdi_anchor_pos = None
        self._classic_wheel_follow_pending = None
        self.footer.setText(
            'Citrix / VDI互換：カーソル移動OFF。ホイールで選択しEnterで実行できます。'
            if enabled else '通常モード：マウスポインター追従を有効にしました。')

    def set_color_theme(self, theme):
        resolved = normalize_theme(theme)
        if resolved != self.color_theme:
            self.color_theme = resolved
            self.settings.setValue('appearance_theme', resolved)
            self.settings.sync()
            self.apply_color_theme()
        # Do not leave keyboard navigation on a hidden popup/menu button.
        if self.isVisible():
            self.search.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def style_cascade_menu(self, menu):
        """Match both normal and long scrollable child menus to main palette."""
        if theme_family(self.color_theme) != 'light':
            menu.setStyleSheet('')  # Drop any prior light QSS after switching dark.
            return
        menu.setStyleSheet(LIGHT_MENU_QSS)
        tree = getattr(menu, 'scroll_tree', None)
        if tree is not None:
            tree.setStyleSheet(LIGHT_CASCADE_TREE_QSS)
            for bar in (tree.verticalScrollBar(), tree.horizontalScrollBar()):
                bar.setStyleSheet(light_scrollbar_qss('#ffffff'))
        app_tree = getattr(menu, 'tree', None)
        if app_tree is not None:
            app_tree.setObjectName('appCascadeTree')
            app_tree.setStyleSheet(LIGHT_CASCADE_TREE_QSS.replace('cascadeScrollView', 'appCascadeTree'))
            for bar in (app_tree.verticalScrollBar(), app_tree.horizontalScrollBar()):
                bar.setStyleSheet(light_scrollbar_qss('#ffffff'))
        edit = getattr(menu, 'filter_edit', None)
        if edit is not None:
            edit.parentWidget().setStyleSheet(LIGHT_COLUMN_FILTER_QSS)

    def update_history_chevron(self):
        """Search/folder-history glyphs share their shape and alignment."""
        self.history_action.setIcon(combo_chevron_icon(theme_family(self.color_theme), offset_x=-1))

    def apply_color_theme(self):
        """Restyle existing widgets without rebuilding search results or pages."""
        light = theme_family(self.color_theme) == 'light'
        colors = theme_palette(self.color_theme)
        self.setStyleSheet(LIGHT_MAIN_QSS if light else self._dark_main_qss)
        self.expanded_view.apply_theme(self.color_theme)
        palette = (('#aac9b6','#e0f1e7','#275943','#cbe7d8') if light
                   else ('#55766c','#314b41','#def1e7','#416559'))
        self.mode_button.setStyleSheet(
            'QPushButton#expandedModeButton { border:1px solid %s; border-radius:11px; '
            'padding:5px 8px; background:%s; color:%s; text-align:center; } '
            'QPushButton#expandedModeButton:hover {background:%s;}' % palette)
        self.mode_button.setIcon(view_mode_icon(
            'classic' if self.view_mode == 'expanded' else 'expanded',
            theme_family(self.color_theme)))
        self.list.set_row_theme(theme_family(self.color_theme))
        self.tabs.setStyleSheet(LIGHT_TABS_QSS if light else PAGE_TABS_QSS)
        self.tabs.set_light_theme(light)
        self.history_popup.setStyleSheet(LIGHT_HISTORY_QSS if light else self._dark_history_qss)
        if getattr(self, 'remote_window', None) is not None:
            self.remote_window.apply_theme(self.color_theme)
        self.history_filter.setStyleSheet(
            'QLineEdit#historyFilter { border:1px solid %s; border-radius:6px; '
            'padding:2px 8px; background:%s; color:%s; font-size:13px; }'
            % (('#acc9ba', '#ffffff', '#284338') if light else
               ('#587261', '#1a2927', '#e5ebf3')))
        self.update_history_chevron()
        self.update_header_icons()
        self.update_header_tab_width()
        # The global QWidget theme used to paint a pale rectangle behind the
        # brand, despite the titlebar having its own darker green background.
        self.brand_widget.setStyleSheet(
            'QWidget#brandWidget { background:transparent; border:0; } '
            'QLabel#brandIconLabel { background:transparent; border:0; }')
        self.brand_icon_label.setStyleSheet('QLabel#brandIconLabel { background:transparent; border:0; }')
        self.brand_title_label.setStyleSheet('QLabel#brandTitleLabel { background:transparent;color:%s;font-size:18px;font-weight:600;border:0; }'
                                             % ('#20362f' if light else '#eef4ef'))
        header_fill = colors['header']
        subheader_fill = colors['subheader']
        header_line = '#cfddd4' if light else '#455a54'
        self.main_body.setStyleSheet('QWidget#mainBody { background:transparent; border:0; }')
        self.search_bar.setStyleSheet(
            f'QWidget#searchBar {{ background:{header_fill}; border:0; border-bottom:1px solid {header_line}; }}')
        self.search.setStyleSheet(
            'QLineEdit#mainSearchField { '
            f'background:{colors["search_bg"]};color:{colors["search_fg"]};'
            f'border:1px solid {colors["search_border"]};'
            'border-radius:17px;padding:5px 14px;font-size:15px; } '
            'QLineEdit#mainSearchField:focus { '
            f'border-color:{colors["search_focus"]}; }}')
        self.search_glyph.setStyleSheet(
            'QToolButton#searchGlyph { background:transparent; border:0; padding:0; }')
        self.history_category_button.setStyleSheet(
            'QToolButton#searchHistoryCategoryButton { background:transparent; border:0; '
            'border-radius:7px; padding:0; } '
            f'QToolButton#searchHistoryCategoryButton:hover {{ background:{colors["hover"]}; }}')
        header_hover = '#e4eee8' if light else '#334744'
        header_pressed = '#d7e7df' if light else '#415953'
        frame_border = '#d0dfd7' if light else '#47605a'
        divider = '#c9d8d0' if light else '#4d6660'
        self.theme_button.setStyleSheet(
            f'QPushButton#headerSettingsButton {{ background:transparent; border:0; border-radius:17px; padding:0; }} '
            f'QPushButton#headerSettingsButton:hover {{ background:{header_hover}; }} '
            f'QPushButton#headerSettingsButton:pressed {{ background:{header_pressed}; }}')
        self.page_overflow_button.setStyleSheet(
            f'QPushButton#headerPageOverflow {{ background:{subheader_fill}; '
            f'color:{colors["text"]};border:1px solid {frame_border};'
            f'border-radius:9px;padding:3px 5px;font-size:12px; }} '
            f'QPushButton#headerPageOverflow:hover {{background:{header_hover};}}')
        self.header_divider.setStyleSheet(f'QFrame#headerDivider {{ color:{divider}; background:{divider}; }}')
        common_window_style = (
            f'QPushButton#windowFrameButton, QPushButton#windowCloseButton {{ background:transparent; border:0; border-radius:16px; }} '
            f'QPushButton#windowFrameButton:hover {{ background:{header_hover}; }} '
            f'QPushButton#windowFrameButton:pressed {{ background:{header_pressed}; }} '
            f'QPushButton#windowCloseButton:hover {{ background:#e37d7d; }} '
            f'QPushButton#windowCloseButton:pressed {{ background:#d46565; }}')
        self.minimize_button.setStyleSheet(common_window_style)
        self.maximize_button.setStyleSheet(common_window_style)
        self.close_button.setStyleSheet(common_window_style)
        self.save_history_button.setStyleSheet(
            f'QPushButton#saveHistoryButton {{ background:{"#e6f3eb" if light else "#30493e"}; color:{"#285145" if light else "#e5f1eb"}; '
            f'border:1px solid {"#9fbbaa" if light else "#5c7a70"}; border-radius:9px; padding:3px 10px; font-size:12px; }} '
            f'QPushButton#saveHistoryButton:hover {{ background:{header_hover}; }}')
        self.layout_search_inner_controls()
        # Draw bold-enough, consistently sized Chrome-style outline icons.
        # Native font glyphs (← → ⌂) were too tiny and theme-dependent.
        for button, name in (
                (self.nav_back_button, 'back_arrow'),
                (self.nav_forward_button, 'forward'),
                (self.nav_home_button, 'home')):
            button.setIcon(browser_navigation_icon(name, theme_family(self.color_theme)))
        nav_hover = '#e3f1e9' if light else '#354b50'
        nav_pressed = '#d4e7db' if light else '#496168'
        nav_border = '#cbded2' if light else '#405650'
        # Match Page bar's base color. In particular the *toolbar widget*
        # must not inherit LIGHT_MAIN_QSS's global QWidget background, which
        # showed up as a tinted rectangle around the navigation buttons.
        nav_fill = header_fill
        self.nav_toolbar.setStyleSheet(f'''
            QWidget#navigationToolbar {{ background:transparent; border:0; }}
            QPushButton#navBackButton, QPushButton#navForwardButton,
            QPushButton#navHomeButton {{ background:{nav_fill};
                border:1px solid {nav_border}; border-radius:10px;
                padding:0; margin:0; }}
            QPushButton#navBackButton:hover:!disabled,
            QPushButton#navForwardButton:hover:!disabled,
            QPushButton#navHomeButton:hover:!disabled {{ background:{nav_hover}; }}
            QPushButton#navBackButton:pressed:!disabled,
            QPushButton#navForwardButton:pressed:!disabled,
            QPushButton#navHomeButton:pressed:!disabled {{ background:{nav_pressed}; }}
            QPushButton#navBackButton:disabled,
            QPushButton#navForwardButton:disabled,
            QPushButton#navHomeButton:disabled {{ background:{nav_fill}; color:#9eaea7; }}
        ''')
        self.mode_bar.setStyleSheet(
            f'QWidget#pageBar {{ background:{subheader_fill}; border:0; border-bottom:1px solid {header_line}; }}')
        self.theme_menu.setStyleSheet(LIGHT_MENU_QSS if light else '')
        if hasattr(self, 'tray_menu'):
            self.tray_menu.setStyleSheet(LIGHT_MENU_QSS if light else '')
        QApplication.instance().setStyleSheet(light_scrollbar_qss('#edf5f0') if light
                                              else MAIN_LIST_SCROLLBAR_QSS)
        for view, dark_bg in ((self.list, '#202b29'),
                              (self.history_choices, '#223043')):
            if light:
                light_bg = '#ffffff' if view is self.history_choices else '#f8fbf8'
                for bar in (view.verticalScrollBar(), view.horizontalScrollBar()):
                    bar.setStyleSheet(light_scrollbar_qss(light_bg))
            else:
                apply_scrollbar_theme(view, dark_bg)
        # Data and selected index remain untouched; recolor only description.
        for index in range(self.list.topLevelItemCount()):
            self.list.topLevelItem(index).setForeground(
                1, QColor('#647f71' if light else '#a6b4c7'))
        self.update()

    FRAME_WIDTH = 6
    FRAME_TOP = 8

    def frame_inner_rect(self):
        return QRectF(self.FRAME_WIDTH + .5, self.FRAME_TOP + .5,
                      self.width() - 2 * self.FRAME_WIDTH - 1,
                      self.height() - self.FRAME_TOP - self.FRAME_WIDTH - 1)

    def frame_hit(self, pos):
        return self.rect().contains(pos.toPoint()) and not self.frame_inner_rect().contains(pos)

    @staticmethod
    def saved_dimension(value, default, minimum, maximum):
        try:
            dimension = int(value)
        except (TypeError, ValueError):
            dimension = default
        return max(minimum, min(dimension, maximum))

    def view_size_keys(self):
        # Wide view must never overwrite the user's compact layout dimensions.
        if getattr(self, 'view_mode', 'classic') == 'expanded':
            return 'expanded_window_width', 'expanded_window_height', 1060, 670
        return 'window_width', 'window_height', 390, 440

    def restore_window_height(self):
        bounds = self.screen().availableGeometry()
        _, key, _, default = self.view_size_keys()
        height = self.saved_dimension(self.settings.value(key, default),
                                      default, self.minimumHeight(), bounds.height())
        self.resize(self.width(), height)

    def restore_window_size(self):
        bounds = self.screen().availableGeometry()
        key_w, key_h, default_w, default_h = self.view_size_keys()
        width = self.saved_dimension(self.settings.value(key_w, default_w),
                                     default_w, self.minimumWidth(), bounds.width())
        height = self.saved_dimension(self.settings.value(key_h, default_h),
                                      default_h, self.minimumHeight(), bounds.height())
        # Repair legacy state.ini entries poisoned by the previous behavior:
        # maximizing used to save work-area-sized width AND height. If BOTH
        # dimensions fill the work area, restore this view's sensible default.
        if (width >= bounds.width() - 2 and height >= bounds.height() - 2
                and (default_w < bounds.width() or default_h < bounds.height())):
            width = self.saved_dimension(default_w, default_w,
                                         self.minimumWidth(), bounds.width())
            height = self.saved_dimension(default_h, default_h,
                                          self.minimumHeight(), bounds.height())
        self.resize(width, height)

    def resize_edge(self, pos):
        if not self.rect().contains(pos.toPoint()):
            return None
        # Restore top-edge and both top-corner resize hit zones. Only the
        # 6px perimeter resizes; the remaining title/header area still moves.
        if getattr(self, 'isMaximized', lambda: False)():
            return None
        left = pos.x() < self.FRAME_WIDTH
        right = pos.x() >= self.width() - self.FRAME_WIDTH
        top = pos.y() < self.FRAME_WIDTH
        bottom = pos.y() >= self.height() - self.FRAME_WIDTH
        return '-'.join(edge for hit, edge in ((top, 'top'), (bottom, 'bottom'),
                                                (left, 'left'), (right, 'right')) if hit) or None

    @staticmethod
    def edge_cursor(edge):
        if edge in {'top-left', 'bottom-right'}:
            return Qt.CursorShape.SizeFDiagCursor
        if edge in {'top-right', 'bottom-left'}:
            return Qt.CursorShape.SizeBDiagCursor
        if edge in {'left', 'right'}:
            return Qt.CursorShape.SizeHorCursor
        if edge in {'top', 'bottom'}:
            return Qt.CursorShape.SizeVerCursor
        return Qt.CursorShape.ArrowCursor

    def can_save_normal_window_geometry(self):
        """Never persist maximized dimensions/position as the normal frame."""
        return (not getattr(self, '_maximizing_window', False)
                and not self.isMaximized()
                and not bool(self.windowState() & Qt.WindowState.WindowMaximized))

    def save_window_size(self):
        if not self.can_save_normal_window_geometry():
            return
        key_w, key_h, _, _ = self.view_size_keys()
        self.settings.setValue(key_w, self.width())
        self.settings.setValue(key_h, self.height())
        self.settings.sync()

    def save_window_height(self):
        # Compatibility with existing height-setting callers.
        self.save_window_size()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        outer = QRectF(self.rect()).adjusted(.5, .5, -.5, -.5)
        gradient = QLinearGradient(0, 0, 0, self.FRAME_TOP)
        top, bottom, outer_line, inner_line, fill, content_line, fine_line, _ = FRAME_COLORS[theme_family(self.color_theme)]
        gradient.setColorAt(0, QColor(top))
        gradient.setColorAt(1, QColor(bottom))
        painter.setBrush(gradient)
        painter.setPen(QPen(QColor(outer_line), 1))
        painter.drawRoundedRect(outer, self.CORNER_RADIUS, self.CORNER_RADIUS)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(inner_line), 1))
        painter.drawRoundedRect(outer.adjusted(1, 1, -1, -1), self.CORNER_RADIUS - 1, self.CORNER_RADIUS - 1)
        inner = self.frame_inner_rect()
        painter.setBrush(QColor(fill))
        painter.setPen(QPen(QColor(content_line), 1))
        painter.drawRoundedRect(inner, 3, 3)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(fine_line), 1))
        painter.drawRoundedRect(inner.adjusted(1, 1, -1, -1), 2, 2)
        painter.end()

    def mousePressEvent(self, event):
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            self.close_cascade_for_main_interaction()
        edge = self.resize_edge(event.position())
        if event.button() == Qt.MouseButton.LeftButton and edge:
            self.hover_timer.stop(); self.pending_menu_item = None
            if self.menu: self.menu.close()
            self._frame_drag = None
            self._size_drag = (edge, event.globalPosition().toPoint(), self.geometry())
            # Chromium needs several frames to resize its backing surface.
            # While dragging a light-theme Browser, show an in-memory frozen
            # webpage preview instead of exposing black right/bottom strips.
            web = getattr(self.expanded_view, 'web_view', None)
            if (self.view_mode == 'expanded'
                    and self.expanded_view._workspace_mode == 'browser'
                    and web is not None):
                web.begin_live_resize()
            event.accept(); return
        if event.button() == Qt.MouseButton.LeftButton and self.frame_hit(event.position()):
            self.hover_timer.stop(); self.pending_menu_item = None
            if self.menu: self.menu.close()
            self._frame_drag = None
            handle = self.windowHandle()
            if not handle or not handle.startSystemMove():
                self._frame_drag = (event.globalPosition().toPoint(), self.pos())
            event.accept(); return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        resize = getattr(self, '_size_drag', None)
        if resize and event.buttons() & Qt.MouseButton.LeftButton:
            edge, origin_pointer, original = resize
            delta = event.globalPosition().toPoint() - origin_pointer
            bounds = self.screen().availableGeometry()
            rect = resize_frame(edge, original.x(), original.y(),
                                original.width(), original.height(), delta.x(), delta.y(),
                                self.minimumWidth(), self.minimumHeight(),
                                bounds.width(), bounds.height())
            self.setGeometry(*rect)
            event.accept(); return
        self.setCursor(self.edge_cursor(self.resize_edge(event.position())))
        drag = getattr(self, '_frame_drag', None)
        if drag and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(drag[1] + event.globalPosition().toPoint() - drag[0])
            event.accept(); return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._frame_drag = None
            if getattr(self, '_size_drag', None):
                self._size_drag = None
                web = getattr(self.expanded_view, 'web_view', None)
                if web is not None:
                    web.end_live_resize()
                self.save_window_size()
                if self.can_save_normal_window_geometry():
                    self.settings.setValue('position', self.pos())
                    self.settings.sync()
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        if not getattr(self, '_size_drag', None): self.unsetCursor()
        super().leaveEvent(event)

    def open_header_page_menu(self):
        """Space-saving Page selector for narrow Compact windows only."""
        menu = QMenu(self.page_overflow_button)
        for index in range(self.tabs.count()):
            action = menu.addAction(self.tabs.tabText(index))
            action.setCheckable(True)
            action.setChecked(index == self.tabs.currentIndex())
            action.triggered.connect(
                lambda checked=False, i=index: self.tabs.setCurrentIndex(i))
        menu.exec(self.page_overflow_button.mapToGlobal(
            QPoint(0, self.page_overflow_button.height())))

    def update_header_tab_width(self):
        """Keep the main search, Page selection, and controls reachable."""
        width = self.width()
        narrow = width < 780
        self.brand_widget.setVisible(width >= 650)
        # The window still has its close and settings actions at minimum size.
        self.minimize_button.setVisible(
            not self.dismiss_on_outside_click and width >= 720)
        self.maximize_button.setVisible(width >= 720)
        # In expanded Files/Browser view the Page controls are in the
        # workspace strip. Retain the header tabs only for Compact/search.
        # Do not inspect isVisible() here: startup invokes this before
        # the Files/Browser workspace is first shown.  That used to make
        # the legacy header Page controls appear temporarily or persist.
        # Expanded mode owns its Page buttons solely in the workspace strip.
        expanded_workspace = self.view_mode == 'expanded'
        if expanded_workspace:
            self.tabs.hide()
            self.page_overflow_button.hide()
            return
        if narrow:
            self.tabs.hide()
            self.page_overflow_button.show()
            if self.tabs.currentIndex() >= 0:
                self.page_overflow_button.setText(
                    self.tabs.tabText(self.tabs.currentIndex()))
        else:
            self.page_overflow_button.hide()
            self.tabs.show()
            # Qt's native QTabBar scroll arrows handle the remaining width.
            limit = max(130, min(380, width - 750))
            if self.tabs.maximumWidth() != limit:
                self.tabs.setMaximumWidth(limit)

    def update_window_shape(self):
        path=QPainterPath()
        path.addRoundedRect(QRectF(self.rect()),self.CORNER_RADIUS,self.CORNER_RADIUS)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def moveEvent(self, event):
        super().moveEvent(event)
        if getattr(self, 'remote_15_mode', False):
            self.queue_remote_15_alignment()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if getattr(self, 'remote_15_mode', False):
            self.queue_remote_15_alignment()
        if hasattr(self, 'page_overflow_button') and hasattr(self, 'search_bar'):
            self.update_header_tab_width()
        self.update_window_shape()
        if getattr(self, 'history_popup', None) and self.history_popup.isVisible():
            self.position_history_popup()
        if hasattr(self, 'expanded_view') and self.expanded_view.favorite_popup.isVisible():
            self.expanded_view.position_directory_favorites()
        if (self.isVisible() and hasattr(self, 'settings')
                and self.can_save_normal_window_geometry()):
            key_w, key_h, _, _ = self.view_size_keys()
            self.settings.setValue(key_w, self.width())
            self.settings.setValue(key_h, self.height())

    def showEvent(self, event):
        if self.data is not None:self.reload()
        self.update_window_shape()
        super().showEvent(event)
        if getattr(self, 'remote_15_mode', False):
            self.queue_remote_15_alignment(show=True)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange and hasattr(self, 'maximize_button'):
            self.update_header_icons()

    def row_icon(self, row):
        if row.get('_system_drives_root'):
            # Files Exp's virtual PC uses this exact native computer glyph.
            # Never confuse PC with physical drives (which keep their OS icons).
            return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        source, target = icon_lookup(row)
        # SharePoint/Box/OneDrive placeholders may not pass is_file().  Ask the
        # OS for the association of the extension rather than opening the
        # cloud path.  Cache it once per file type, not once per cloud path.
        key = ('file_type', target) if source == 'type' else (source, target)
        if key not in self.icon_cache:
            if source == 'type':
                type_icon = self.file_icons.icon(QFileInfo('FRBLaunchTypeSample' + target))
                self.icon_cache[key] = (type_icon if not type_icon.isNull()
                                        else icon('file'))
            elif source == 'path' and (row.get('_icon_file') or row.get('_system_drive')
                                       or Path(target).is_file()):
                self.icon_cache[key] = self.file_icons.icon(QFileInfo(target))
            else:
                self.icon_cache[key] = icon(row.get('icon_key', 'command'))
        return self.icon_cache[key]

    def bookmark_manual_file(self):
        return str(self.settings.value('bookmark_manual_' + self.bookmark_browser, '') or '')

    def update_bookmark_source_action(self):
        # The menu concerns the *selected* browser, not the other browser.
        if hasattr(self, 'bookmark_auto_action'):
            manual = bool(self.bookmark_manual_file())
            self.bookmark_auto_action.setEnabled(manual)
            self.bookmark_auto_action.setToolTip(
                '手動指定したファイルを解除して標準のブックマーク保存先から取得します' if manual
                else '現在、自動取得になっています')

    def pick_bookmark_file(self):
        # Support browser-native Bookmarks JSON and exported HTML.
        path, _ = QFileDialog.getOpenFileName(
            self, 'Chrome / Edge の Bookmarks ファイルを選択',
            str(browser_bookmarks.user_data_directory(self.bookmark_browser) or Path.home()),
            'Chrome / Edge のブックマーク (*.json *.html *.htm);;すべてのファイル (*)')
        if not path:
            return
        # Validate before changing the saved source; an erroneous selection
        # must not destroy the working auto-import state.
        profiles, errors = browser_bookmarks.read(self.bookmark_browser, manual_file=path)
        if errors or not profiles or not any(p['roots'] for p in profiles):
            QMessageBox.warning(self, 'ブックマーク読込エラー',
                                '指定ファイルを読み込めません。ブラウザの Bookmarks JSON またはエクスポートHTMLを指定してください。\n'
                                + '\n'.join(errors or [path]))
            return
        self.settings.setValue('bookmark_manual_' + self.bookmark_browser, path)
        self.update_bookmark_source_action()
        self.bookmark_signature = None
        self.refresh_bookmarks(force=True)

    def use_auto_bookmarks(self):
        if not self.bookmark_manual_file():
            self.update_bookmark_source_action()
            return
        self.settings.remove('bookmark_manual_' + self.bookmark_browser)
        self.update_bookmark_source_action()
        self.bookmark_signature = None
        self.refresh_bookmarks(force=True)

    def show_bookmark_diagnostics(self):
        browser = self.bookmark_browser
        manual = self.bookmark_manual_file()
        root = browser_bookmarks.user_data_directory(browser)
        try:
            files = browser_bookmarks.bookmark_files(browser, manual_file=manual)
            profiles, errors = browser_bookmarks.read(browser, manual_file=manual)
            total = sum(1 for p in profiles for group in p['roots'] for _ in group['children'])
            lines = [f'ブラウザ: {browser.title()}',
                     f'取得方式: {"指定ファイル" if manual else "自動取得"}',
                     f'標準の保存場所: {root or "不明（LOCALAPPDATA未設定）"}',
                     f'指定ファイル: {manual or "なし"}',
                     f'検出したブックマークファイル（Bookmarks / AccountBookmarks）: {len(files)}件',
                     *[str(path) for path in files],
                     f'読込成功: {len(profiles)}プロフィール / 最上位項目: {total}件']
            if errors:lines += ['読込エラー:', *errors]
            if not files:
                lines += ['保存先が見つかりません。',
                          'ブラウザで chrome://version または edge://version を開き、',
                          '「プロフィール パス」を確認してください。',
                          'そのフォルダーの「Bookmarks」または「AccountBookmarks」、',
                          'もしくはブラウザからエクスポートしたHTMLを指定できます。']
            elif not total:
                lines += ['読み込めましたが表示可能なブックマークが空です。',
                          '別プロフィールや別ブラウザに保存されている可能性があります。']
        except Exception as ex:
            lines = [f'取得診断中にエラー: {ex}']
        QMessageBox.information(self, 'FRB Launch ブックマーク取得診断', '\n'.join(lines))

    def select_bookmark_browser(self, browser):
        if browser not in browser_bookmarks.BROWSERS:return
        self.bookmark_browser=browser
        self.settings.setValue('bookmark_browser',browser)
        self.update_bookmark_source_action()
        for key,action in self.bookmark_browser_actions.items():
            action.setChecked(key==browser)
        self.bookmark_signature=None
        self.bookmark_profiles=[]
        self.refresh_bookmarks(force=True)

    def refresh_bookmarks(self, force=False):
        # Reads only bookmark files belonging to the selected browser.
        try:
            manual=self.bookmark_manual_file()
            stamp=(manual, browser_bookmarks.signature(self.bookmark_browser,manual_file=manual))
            if not force and stamp==self.bookmark_signature:return
            profiles,errors=browser_bookmarks.read(self.bookmark_browser,manual_file=manual)
            # A temporary read/JSON failure must not wipe the last good catalog.
            if errors and not profiles and self.bookmark_profiles:
                DIAG.warning('BOOKMARK read failed; keeping previous catalog: %s',errors)
                return
            self.bookmark_signature=stamp
            self.bookmark_profiles=profiles
            self.bookmark_errors=errors
            if self.data is not None:
                self.data=browser_bookmarks.attach(self.data,self.bookmark_browser,profiles)
                if self.menu:self.menu.close();self.menu=None
                self.render()
            if errors:DIAG.warning('BOOKMARK partial read: %s',errors)
            if force:
                count=sum(1 for r in self.data['items'] if r.get('_browser_bookmark') and r.get('item_kind')=='command') if self.data else 0
                self.footer.setText(f'{self.bookmark_browser.title()} のブックマークを更新: {count}件' if count else
                                    f'{self.bookmark_browser.title()} の取得結果が空です。トレイの「ブックマーク取得診断」を確認')
        except Exception as ex:
            DIAG.exception('BOOKMARK refresh failed')
            if force:self.error('ブックマークを取得できません: '+str(ex))

    def _index_expanse(self, value):
        return self.expander().expand(value)

    def auto_refresh_file_index(self):
        """Lightweight timer; filesystem enumeration runs only in a worker."""
        self.refresh_file_index(manual=False)

    def refresh_file_index(self, manual=True):
        """Refresh independent minimal roots asynchronously; never block the GUI."""
        if self._file_index_cancel.is_set():
            return
        if self.file_index_busy:
            if manual:
                self.tray.showMessage('FRB Launch', 'ファイル索引は更新中です',
                                      QSystemTrayIcon.MessageIcon.Information, 3500)
            return
        try:
            opts = file_index.load_options(self.file_index_options_path)
            self.file_index_settings = opts
            new_interval = opts['auto_update']['check_interval_minutes'] * 60000
            if self.file_index_check_timer.interval() != new_interval:
                self.file_index_check_timer.setInterval(new_interval)
            mode = file_index.index_mode(opts)
            if mode == 'off':
                if manual:
                    raise ValueError('ファイル索引は設定JSONで無効になっています（index_mode: off）')
                return
            if not manual and opts['update_mode'] != 'auto':
                return
            # Unavailable registered roots must remain in the desired set:
            # they cannot be mistaken for removed configuration and deleted.
            # Read the latest authored config even if Studio changed it while
            # the launcher stays hidden in the system tray.
            if mode == 'registered':
                index_data = load(CONFIG)
                roots, warnings = file_index.resolve_roots(
                    opts, index_data, Expander(index_data).expand, include_unavailable=True)
            else:
                roots, warnings = file_index.resolve_roots(
                    opts, include_unavailable=True)
            if not roots:
                if manual:
                    raise ValueError('索引対象フォルダーがありません。index_mode と index_folders を確認してください')
                DIAG.warning('FILE_INDEX auto skipped: no configured index roots (mode=%s)', mode)
                return
            self.file_index_busy = True
            self._file_index_manual = manual
            self.file_index_refresh_action.setEnabled(False)
            self.file_index_clear_action.setEnabled(False)
            DIAG.info('FILE_INDEX start mode=%s roots=%s extensions=%s warnings=%s',
                      'manual' if manual else 'auto', roots, opts['extensions'], warnings)
            if manual:
                self.tray.showMessage('FRB Launch', 'ファイル索引を更新中…（ランチャー操作は継続できます）',
                                      QSystemTrayIcon.MessageIcon.Information, 4500)

            def run_index():
                try:
                    stats = file_index.refresh_index(
                        self.file_index_db, roots, opts, force=False,
                        root_warnings=warnings,
                        cancelled=self._file_index_cancel.is_set,
                        on_root=lambda root, result: DIAG.info(
                            'FILE_INDEX root=%s result=%s', root, result))
                    self.file_index_signals.finished.emit(stats)
                except Exception as exc:
                    DIAG.exception('FILE_INDEX failed')
                    self.file_index_signals.failed.emit(str(exc))
            threading.Thread(target=run_index, name='FRBFileIndex', daemon=True).start()
        except Exception as exc:
            if manual:
                self.error('ファイル索引を開始できません: '+str(exc))
            else:
                DIAG.warning('FILE_INDEX auto start failed: %s', exc)

    def file_index_finished(self, stats):
        self.file_index_busy = False
        self.file_index_refresh_action.setEnabled(True)
        self.file_index_clear_action.setEnabled(True)
        DIAG.info('FILE_INDEX complete count=%s changed=%s unchanged=%s failed=%s applied=%s',
                  stats['count'], len(stats['changed_roots']),
                  len(stats['unchanged_roots']), len(stats['failed_roots']), stats['applied'])
        # Root-by-root evidence is essential when an entire drive silently
        # disappears from search despite a successful overall update.
        if stats.get('applied'):
            for root_info in file_index.index_root_status(self.file_index_db):
                DIAG.info('FILE_INDEX root_stats root=%s count=%s excluded=%s',
                          root_info['root_path'], root_info['count'], root_info['excluded'])
                if root_info['count'] == 0:
                    DIAG.warning('FILE_INDEX empty_root root=%s (check scan warnings and hidden attributes)',
                                 root_info['root_path'])
        if self._file_index_manual:
            summary = (f"ファイル索引: {stats['count']:,}件 / 更新{len(stats['changed_roots'])}ルート"
                       f" / 変更なし{len(stats['unchanged_roots'])}ルート"
                       f" / 失敗{len(stats['failed_roots'])}ルート"
                       f" / 警告{len(stats['scan_warnings'])}件")
            self.tray.showMessage('FRB Launch', summary,
                                  QSystemTrayIcon.MessageIcon.Information, 6000)
        if stats['scan_warnings']:
            DIAG.warning('FILE_INDEX warnings: %s', stats['scan_warnings'])
        if stats['changed_roots'] and self.isVisible() and self.search.text().strip() and not self.selection:
            self.render()

    def file_index_failed(self, message):
        self.file_index_busy = False
        self.file_index_refresh_action.setEnabled(True)
        self.file_index_clear_action.setEnabled(True)
        if self._file_index_manual:
            self.error('ファイル索引の更新に失敗（旧索引は維持）: ' + message)
        else:
            DIAG.warning('FILE_INDEX automatic refresh failed (old index retained): %s', message)

    def show_file_index_status(self):
        try:
            self.file_index_settings = file_index.load_options(self.file_index_options_path)
            mode = file_index.index_mode(self.file_index_settings)
        except (OSError, ValueError) as exc:
            self.error('ファイル索引の設定JSONに問題があります: ' + str(exc))
            return
        status = file_index.index_status(self.file_index_db)
        if status is None:
            message = 'まだ索引がありません。トレイの「ファイル索引を今すぐ更新」を実行してください。'
        else:
            roots = '\n'.join(status.get('roots', []))
            warnings = '\n'.join(status.get('warnings', []))
            message = (f"最終確認/更新: {status['updated_at']}\n"
                       f"登録: {status['count']:,}件  /  除外: {status['excluded']:,}件\n"
                       f"自動更新: {'ON' if self.file_index_settings.get('update_mode') == 'auto' else 'OFF'}\n"
                       f"対象ルート:\n{roots}")
            detail = file_index.index_root_status(self.file_index_db)
            if detail:
                message += '\nルート別状態:'
                for row in detail[:15]:
                    message += (f"\n{row['root_path']}: {row['count']}件"
                                f" / 最終チェック {row['checked_at']}")
                if len(detail)>15:
                    message += f'\nほか {len(detail)-15}ルート'
            if warnings:
                message += '\n警告（前回チェック時）:\n' + warnings
        labels = {'registered':'既存設定のフォルダー', 'configured':'index_folders に指定したフォルダー', 'off':'無効'}
        message = (f"現在のモード: {mode}（{labels[mode]}）\n"
                   f"最大探索深さ: {self.file_index_settings.get('max_depth')}\n" + message)
        if mode == 'off':
            message += '\n※旧DBが残っていても検索には使用されません。'
        QMessageBox.information(self, 'ファイル索引の状態', message)

    def clear_file_index(self):
        """Clear indexed rows safely, preserving the SQLite file and source data."""
        if self.file_index_busy:
            QMessageBox.warning(self, 'ファイル索引', '索引を更新中です。終了後に再実行してください。')
            return
        answer = QMessageBox.question(
            self, 'ファイル索引SQLite DBをクリア',
            'ファイル索引DB内の索引データをすべてクリアしますか？\n\n'
            'DBファイル自体は残します。元のファイルや設定JSONは削除しません。\n'
            '必要な場合は「ファイル索引を今すぐ更新」で再作成できます。',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            removed = file_index.clear_index(self.file_index_db)
            DIAG.info('FILE_INDEX cleared database=%s removed=%s', self.file_index_db, removed)
            if self.isVisible() and self.search.text().strip() and not self.selection:
                self.render()
            QMessageBox.information(self, 'ファイル索引',
                                    '索引データをクリアしました（登録0件）。' if removed else '索引DBは既にありません。')
        except (OSError, sqlite3.Error) as exc:
            DIAG.exception('FILE_INDEX clear failed')
            self.error('ファイル索引DBをクリアできませんでした: ' + str(exc))

    def run_file_path(self, row, path):
        """Index results and expanded folder entries share launch rules."""

        if not os.path.isfile(path):
            self.error('ファイルが見つかりません。パスを確認してください: '+path)
            return
        try:
            studio = self.expander().values.get('studio_root', '')
            steps = file_index.launch_steps(path, studio_root=studio)
            # Literal paths can contain percent signs. Preserve Expander semantics.
            protected = []
            for step in steps:
                protected.append({key: ([v.replace('%', '%%') for v in value] if isinstance(value, list)
                                        else value.replace('%', '%%') if isinstance(value, str) else value)
                                  for key, value in step.items()})
            self.execute({**row, 'launch_actions': protected})
        except Exception as exc:
            self.error('索引ファイルを開けません: '+str(exc))

    def refresh_apps(self):
        if not windows.IS_WINDOWS or self.apps_proc:return
        if not self.data or not any(r.get('launch_source')=='installed_apps' for r in self.data['items']):return
        self.apps_log=STATE/'apps.log'
        append_apps_log(self.apps_log,'SCAN_START','Get-StartApps / Start Menu discovery requested')
        try:
            import uuid
            self.apps_output=STATE/('apps_scan_'+uuid.uuid4().hex+'.json')
            script=LAUNCH_HOME/'scripts'/'Get-LaunchApps.ps1'
            if not script.is_file():raise FileNotFoundError('Get-LaunchApps.ps1が見つかりません: '+str(script))
            self.apps_proc=start_process('powershell.exe',
                ['-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',str(script),'-OutputPath',str(self.apps_output)],
                str(LAUNCH_HOME),False,log_path=self.apps_log)
            self.apps_started=time.monotonic();self.apps_timer.start()
            DIAG.info('APPS scan started pid=%s log=%s',self.apps_proc.pid,self.apps_log)
            self.footer.setText('アプリ一覧を更新中…')
        except Exception as e:
            DIAG.exception('APPS PowerShell launch failed')
            append_apps_log(self.apps_log,'POWERSHELL_LAUNCH_FAILED',str(e))
            self.apps_proc=None
            self._recover_apps(e)

    def _apply_apps_scan(self, records, partial=False):
        # Never destroy a valid catalog when a managed PC gives us zero results.
        records=merge_catalog(self.app_records,records,partial)
        if not records:raise ValueError('取得件数が0件のため、以前のアプリ一覧を保持します')
        installed_apps.write_cache(STATE/'apps_cache.json',records)
        self.app_records=records;self.icon_cache.clear()
        self.data=installed_apps.attach(self.data,records)
        if self.menu:self.menu.close()
        self.render()
        if partial:
            self.footer.setText('アプリ一覧を部分更新: '+str(len(records))+'件（詳細: apps.log）')
        else:
            self.footer.setText('アプリ一覧を更新しました: '+str(len(records))+'件')
        append_apps_log(self.apps_log,'SCAN_COMPLETE',f'count={len(records)} partial={partial}')
        DIAG.info('APPS scan complete count=%s partial=%s',len(records),partial)

    def _recover_apps(self, reason):
        """Read ordinary Start Menu links if company policy blocks PowerShell."""
        try:
            raw,warnings=scan_shortcuts()
            for warning in warnings:
                append_apps_log(self.apps_log,'FALLBACK_WARNING',warning)
            records=installed_apps.normalize(raw)
            append_apps_log(self.apps_log,'FALLBACK_SCAN',f'count={len(records)}')
            if not records:
                self.error('アプリ一覧の更新に失敗。既存一覧は保持しました。詳細: '+str(self.apps_log))
                return
            self._apply_apps_scan(records,partial=True)
            DIAG.warning('APPS fallback used because PowerShell scan failed: %s',reason)
        except Exception as e:
            DIAG.exception('APPS fallback failed')
            append_apps_log(self.apps_log,'FALLBACK_FAILED',str(e))
            self.error('アプリ一覧の更新に失敗。既存一覧は保持しました。詳細: '+str(self.apps_log))

    def poll_apps(self):
        proc=self.apps_proc
        if not proc:return
        code=proc.poll()
        if code is None:
            if time.monotonic()-self.apps_started<90:return
            append_apps_log(self.apps_log,'POWERSHELL_TIMEOUT','90 seconds; terminating scan and trying shortcut fallback')
            proc.kill();proc.wait();code=-1
        self.apps_timer.stop();self.apps_proc=None
        try:
            append_apps_log(self.apps_log,'POWERSHELL_EXIT',f'exit_code={code}')
            if code!=0:raise RuntimeError('PowerShell終了コード '+str(code))
            raw=json.loads(self.apps_output.read_text(encoding='utf-8-sig'))
            if not isinstance(raw,dict) or raw.get('version')!=1 or not isinstance(raw.get('apps'),list):
                raise ValueError('アプリ一覧の形式が不正です')
            records=installed_apps.normalize(raw['apps'])
            self._apply_apps_scan(records,partial=bool(raw.get('partial',False)))
        except Exception as e:
            DIAG.exception('APPS PowerShell scan failed; trying Start Menu fallback')
            append_apps_log(self.apps_log,'POWERSHELL_SCAN_FAILED',str(e))
            self._recover_apps(e)
        finally:
            self.apps_output.unlink(missing_ok=True)

    def error(self, message):
        logging.warning('%s', message)
        DIAG.warning('%s',message)
        self.tray.showMessage('FRB Launch', str(message), QSystemTrayIcon.MessageIcon.Warning,6000)
        # High-contrast error marker without changing the ordinary footer theme.
        # QLabel interprets HTML markup while other status messages stay plain.
        self.footer.setText(
            '<span style="color:#e64040; font-weight:600;">❌ '
            + html_escape(str(message)) + '</span>')

    def register_key(self):
        """Register the normal opener plus all enabled Page-root item keys."""
        hwnd = int(self.winId())
        key = (self.data or {}).get('launch_hotkey', 'Ctrl+Shift+;')
        if key != self.registered_key:
            windows.unhotkey(hwnd)
            try:
                windows.hotkey(hwnd, key)
                self.registered_key = key
            except Exception as exc:
                self.registered_key = ''
                self.error(exc)
        # A reload is atomic for the document, but Windows may reserve an
        # individual shortcut. Keep the working hotkeys and warn for failures.
        for key_id in self.registered_menu_hotkeys:
            windows.unhotkey(hwnd, key_id)
        self.registered_menu_hotkeys = {}
        for index, (item_id, shortcut) in enumerate(menu_shortcuts({
                **self.data, 'items': self.authored_items})):
            hotkey_id = MENU_HOTKEY_ID_START + index
            try:
                windows.hotkey(hwnd, shortcut, hotkey_id)
                self.registered_menu_hotkeys[hotkey_id] = item_id
            except Exception as exc:
                self.error(f'メニューショートカット登録失敗 ({shortcut}): {exc}')

    def reload_shortcuts_if_hidden(self):
        if not self.isVisible() and not self.busy:
            self.reload()

    def reload(self, force=False):
        try:
            stat=CONFIG.stat();stamp=stat.st_mtime_ns
            if not force and stamp==self.mtime and stat.st_size==self.config_size:return
            fresh=load(CONFIG)
            Expander(fresh)  # Validate timezone before swapping the active data.
            self.data=browser_bookmarks.attach(installed_apps.attach(fresh,self.app_records),
                                               self.bookmark_browser,self.bookmark_profiles)
            # Keep the *original* DataJSON rows separate from runtime-merged
            # apps/bookmarks. self.data['items'] is never an authority for
            # deciding what Studio may edit.
            self.authored_items = fresh['items']
            self.mtime=stamp;self.config_size=stat.st_size
            self.tabs.blockSignals(True)
            while self.tabs.count():self.tabs.removeTab(0)
            self.pages=sorted([p for p in fresh['pages'] if p.get('enabled',True)],key=lambda p:p.get('sort_order',0))
            for p in self.pages:self.tabs.addTab(p['title'])
            ids=[p['page_id'] for p in self.pages]
            if self.page_id not in ids:self.page_id=ids[0]
            self.tabs.setCurrentIndex(ids.index(self.page_id));self.tabs.blockSignals(False)
            self.stack=[];self.selection=None;self.checked.clear();self.render()
            self._nav_reset()
            if hasattr(self,'registered_key'):self.register_key()
            jump_list.register_async(
                fresh, sys.executable, STATE, DIAG,
                force=not self._jump_list_startup_synced)
            self._jump_list_startup_synced = True
        except Exception as e:self.error('設定の読込に失敗: '+str(e))

    def nativeEvent(self, kind, message):
        if windows.IS_WINDOWS:
            msg=wintypes.MSG.from_address(int(message))
            if msg.message==0x0312:
                if msg.wParam == 1:
                    QTimer.singleShot(0, self.summon)
                else:
                    item_id = self.registered_menu_hotkeys.get(int(msg.wParam))
                    if item_id is None:
                        return True, 0
                    QTimer.singleShot(0, lambda target=item_id: self.summon_menu(target))
                return True,0
        return super().nativeEvent(kind,message)

    @staticmethod
    def _selected_item_id(tree):
        item = tree.currentItem()
        if item is None:
            return None
        row = item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(row, dict):
            return None
        return row.get('item_id') or row.get('choice_id')

    @staticmethod
    def _focus_tree_row(tree, item_id):
        if not item_id:
            return False
        for index in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(index)
            row = item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(row, dict) and (row.get('item_id') == item_id or
                                          row.get('choice_id') == item_id):
                tree.setCurrentItem(item)
                tree.scrollToItem(item)
                return True
        return False

    def _focus_area_of(self, widget):
        if widget is None:
            return None
        if widget is self.search:
            return 'search'
        if widget is self.tabs:
            return 'pages'
        if widget in (self.list, self.list.viewport()):
            return 'list'
        view = getattr(self, 'expanded_view', None)
        if view is not None:
            return self.expanded_focus_area(widget)
        return None

    def capture_last_focus_change(self, previous, widget):
        # Qt's focusChanged signal catches mouse, Tab and arrow navigation
        # without modifying the legacy eventFilter / menu event routing.
        if self.isVisible() and not self._restoring_last_focus:
            area = self._focus_area_of(widget)
            if area is not None:
                self._last_focus_area = area
                if area == 'roots':
                    view = self.expanded_view
                    if widget in view.root_buttons:
                        index = view.root_buttons.index(widget)
                        self._last_root_id = view.root_rows[index].get('item_id')

    def save_last_current(self):
        """Capture current rows before hiding Remote and its tool popups."""
        view = self.expanded_view
        area = self._last_focus_area or self._saved_focus_state.get('area', 'search')
        # A Qt.Tool cascade lives outside the main widget. Reopen at its
        # exact parent, not at the now-closed popup or the hidden classic list.
        menu = self.menu
        if menu is not None and menu.isVisible():
            opener = getattr(menu, 'return_focus_widget', None)
            anchor = self._focus_area_of(opener)
            if anchor is not None:
                area = anchor
            elif view.isVisible() and self.selection is None:
                # Original classic menu source: main selection was its parent.
                area = 'roots' if self._saved_focus_state.get('area') == 'roots' else 'list'
        root_item_id = None
        if self.selection and self.view_mode == 'expanded':
            # Selection is a temporary classic grid. Resume at the actual
            # first-level opener (e.g. メール宛先) after dismissing it.
            parent = self.selection.get('parent_item_id')
            if any(r.get('item_id') == parent for r in view.root_rows):
                area, root_item_id = 'roots', parent
        if area == 'roots' and root_item_id is None:
            for button, row in zip(view.root_buttons, view.root_rows):
                if button.hasFocus():
                    root_item_id = row.get('item_id')
                    break
            if root_item_id is None and menu is not None:
                opener = getattr(menu, 'return_focus_widget', None)
                if opener in view.root_buttons:
                    root_item_id = view.root_rows[view.root_buttons.index(opener)].get('item_id')
            if root_item_id is None:
                root_item_id = self._last_root_id or self._saved_focus_state.get('item_id')
        # A transient Qt focus loss may clear the middle tree current while the
        # row is still remembered by Files.  Preserve its stable ID only when
        # that memory belongs to the displayed breadcrumb directory.
        middle_id = self._selected_item_id(view.middle.tree)
        remembered = getattr(view, '_middle_current_memory', None)
        if not middle_id and remembered and remembered[0] == view.current_directory():
            middle_id = remembered[1]
        # Only persist stable IDs, never Qt pointers or transient QWidgetItems.
        state = normalize_focus_state({
            'area': area,
            'page_id': self.page_id,
            'mode': self.view_mode,
            'item_id': root_item_id if area == 'roots' else self._selected_item_id(self.list),
            'left_id': self._selected_item_id(view.left.tree),
            'middle_id': middle_id,
            'bookmarks_id': self._selected_item_id(view.right.tree),
            'path_ids': [r.get('item_id') for r in view.path if r.get('item_id')],
            'middle_path': view.current_directory(),
        })
        self._saved_focus_state = state
        self.settings.setValue('last_current', json.dumps(state, ensure_ascii=False))
        self.settings.sync()
        return state

    def restore_last_current(self):
        """Focus previously used Page / root / panel / row after summon()."""
        if not self.isVisible() or not self.data:
            return
        state = normalize_focus_state(self._saved_focus_state)
        view = self.expanded_view
        expanded = view.isVisible()
        area = focus_area_for_reopen(state['area'], expanded=expanded)
        # Explorer-first reopen: non-panel anchors (Page, root button, search)
        # start in the first row of Files column 1, without losing paths.
        first_files_on_reopen = expanded and area not in ('files', 'directory', 'bookmarks')
        if first_files_on_reopen:
            area = 'files'
        if self.files_root_hidden_mode and expanded:
            if view._workspace_mode == 'files' and area in ('files', 'bookmarks'):
                area = 'directory'
            elif view._workspace_mode == 'browser' and area == 'bookmarks':
                area = self._current_web_body_area()
            first_files_on_reopen = False
        self._restoring_last_focus = True
        try:
            if expanded:
                # Restore nested directory path using freshly loaded rows.
                ids = state.get('path_ids', [])
                if ids and view.files_root:
                    path = resolve_path_ids(view.files_root, ids,
                                            self.displayed_children)
                    if path:
                        view.path = path
                        view.refresh_middle()
                # A breadcrumb may have navigated *above* a Files shortcut,
                # where an ordinary item-ID chain cannot resolve. Restore its
                # canonical absolute location when the directory still exists.
                stored_path = state.get('middle_path')
                if stored_path and view.current_directory() != stored_path:
                    from directory_address import directory_row
                    if os.path.isdir(stored_path):
                        view.path = [directory_row(stored_path)]
                        view.refresh_middle()
                if first_files_on_reopen:
                    tree = view.left.tree
                    if tree.topLevelItemCount():
                        tree.setCurrentItem(tree.topLevelItem(0))
                        tree.scrollToItem(tree.topLevelItem(0))
                else:
                    self._focus_tree_row(view.left.tree, state.get('left_id'))
                self._focus_tree_row(view.middle.tree, state.get('middle_id'))
                self._focus_tree_row(view.right.tree, state.get('bookmarks_id'))
                if area == 'roots':
                    view.focus_root(item_id=state.get('item_id'))
                elif area in ('files', 'directory', 'bookmarks'):
                    panel = {'files': view.left, 'directory': view.middle,
                             'bookmarks': view.right}[area]
                    view.focus_panel(panel)
                elif area == 'pages':
                    self.tabs.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
                else:
                    self.search.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
            else:
                self._focus_tree_row(self.list, state.get('item_id'))
                if area == 'pages':
                    self.tabs.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
                elif area == 'list':
                    self.list.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
                else:
                    self.search.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
            self._last_focus_area = area
            if expanded and self.remote_window is not None and self.remote_window.isVisible():
                self.remote_focus_area(area)
            if area == 'roots':
                self._last_root_id = state.get('item_id')
        finally:
            self._restoring_last_focus = False

    def summon(self):
        if self.busy:self.error('処理の完了を待っています');return
        if self.isMinimized():
            self.show_launcher_normal_or_saved()
            self.raise_()
            self.activateWindow()
            return
        if self.isVisible():
            if getattr(self, '_cloud_link_handoff', False):
                self.finish_cloud_link_handoff()
                self.raise_()
                self.activateWindow()
            else:
                self.dismiss()
            return
        self.target=windows.foreground();self.reload();self.refresh_bookmarks()
        self.hide_history_popup()
        self.stack=[];self.selection=None;self.checked.clear();self.search.clear();self.render()
        self._nav_reset()
        if not any(s.availableGeometry().intersects(self.frameGeometry()) for s in QApplication.screens()):
            self.move(QApplication.primaryScreen().availableGeometry().center()-self.rect().center())
        self.show_launcher_normal_or_saved();self.raise_();self.activateWindow();self.restore_last_current()

    def summon_menu(self, item_id):
        """Navigate only: never run a command bound to a Page-root shortcut."""
        if self.busy:
            self.error('処理の完了を待っています')
            return
        if not self.isVisible():
            self.target = windows.foreground()
        self.reload()
        row = next((r for r in self.authored_items
                    if r['item_id'] == item_id and r.get('enabled', True)
                    and not r.get('parent_item_id')
                    and any(p['page_id'] == r['page_id'] for p in self.pages)), None)
        if row is None:
            self.error('ショートカット先の項目が見つかりません')
            return
        self.refresh_bookmarks()
        self.hide_history_popup()
        if self.menu:
            self.menu.close()
        self.hover_timer.stop()
        self.pending_menu_item = None
        self.selection = None
        self.checked.clear()
        self.page_id = row['page_id']
        self.tabs.blockSignals(True)
        self.tabs.setCurrentIndex(next(i for i, p in enumerate(self.pages)
                                      if p['page_id'] == row['page_id']))
        self.tabs.blockSignals(False)
        self.stack = [row] if row.get('item_kind') == 'category' else []
        self.search.clear()
        self.render()
        if not self.stack:
            for index in range(self.list.topLevelItemCount()):
                item = self.list.topLevelItem(index)
                if item.data(0, Qt.ItemDataRole.UserRole).get('item_id') == item_id:
                    self.list.setCurrentItem(item)
                    break
        self._nav_reset()
        if not any(screen.availableGeometry().intersects(self.frameGeometry())
                   for screen in QApplication.screens()):
            self.move(QApplication.primaryScreen().availableGeometry().center()
                      - self.rect().center())
        self.show_launcher_normal_or_saved()
        self.raise_()
        self.activateWindow()
        self.list.setFocus()

    def restore_keyboard_focus(self, expected_foreground=None, reason='open', restore_current=True,
                               desktop_input_hwnd=None):
        """Make a mouse-hook-opened Tool window actually accept keyboard input."""
        if not self.isVisible() or (self.menu and self.menu.isVisible()):
            return
        hwnd = int(self.winId())
        before = windows.foreground()
        # The verified desktop gesture may briefly shift foreground from
        # Chrome to Explorer itself while the final mouse event settles.
        # Allow that desktop host ONLY for explicit desktop summons, not for
        # ordinary mouse clicks or a later switch to an unrelated program.
        allowed = expected_foreground
        if reason.startswith('desktop_') and before != hwnd:
            shell = getattr(windows, 'desktop_shell_foreground', lambda: 0)()
            if not shell and desktop_input_hwnd:
                shell = getattr(windows, 'verified_desktop_view_foreground',
                                lambda view: 0)(desktop_input_hwnd)
            if shell == before:
                candidates = (expected_foreground if isinstance(expected_foreground,
                              (tuple, list, set, frozenset)) else (expected_foreground,))
                allowed = tuple(dict.fromkeys((*candidates, shell)))
        active = (before == hwnd or windows.activate_keyboard_window(
            hwnd, expected_foreground=allowed,
            **({'input_window': desktop_input_hwnd} if desktop_input_hwnd else {})))
        if active:
            self.activateWindow()
            if restore_current:
                self.restore_last_current()
        DIAG.info('KEYBOARD_FOCUS reason=%s success=%s before=%s after=%s restored_area=%s',
                  reason, active, before, windows.foreground(), self._last_focus_area)

    def dismiss(self):
        # Capture the Remote's logical Files column BEFORE hide_remote() removes
        # its selection highlighting.  Mouse-only operation does not always
        # send a native Qt focusChanged signal to the selected Files row.
        remote = getattr(self, 'remote_window', None)
        remote_area = (self._remote_area if remote is not None and remote.isVisible()
                       and self._remote_area == 'directory' else None)
        if self.isVisible():
            if remote_area is not None:
                self._last_focus_area = remote_area
            self.save_last_current()
        self.hide_remote()
        self.finish_cloud_link_handoff()
        # Never carry a half-finished double-click into the next summon.
        # Delayed delete callbacks must not resurrect a previously hidden UI.
        self._cascade_dismiss_generation = getattr(self, '_cascade_dismiss_generation', 0) + 1
        self.hide_history_popup()
        self.expanded_view.hide_favorite_popup()
        self._pending_mouse_activation = None
        self._pending_mouse_foreground = None
        if self.menu:self.menu.close()
        self.save_window_height()
        self.hover_timer.stop()
        if self.can_save_normal_window_geometry():
            self.settings.setValue('position', self.pos())
        self.settings.setValue('page', self.page_id)
        # QWidget.hide()/show() can preserve WindowMaximized. Clear the flag
        # WHILE hidden so reopening uses the normal geometry, with no flash.
        was_maximized = (self.isMaximized()
                         or bool(self.windowState() & Qt.WindowState.WindowMaximized))
        self.hide()
        if was_maximized:
            self._restore_normal_on_show = True
            # Clear Qt's maximized flag, then explicitly restore the underlying
            # hidden frame: clearing the flag alone may preserve its huge size.
            self._maximizing_window = True
            try:
                self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMaximized)
                self.restore_window_size()
                saved_pos = self.settings.value('position')
                if saved_pos is not None:
                    self.move(saved_pos)
            finally:
                self._maximizing_window = False

    def begin_cloud_link_handoff(self):
        """Keep Launch open but let native OneDrive/Box share UI appear above it."""
        self._cloud_link_handoff = True
        # Win32 z-order only; removing the Qt Tool flag would hide/recreate
        # the launcher and lose the user's Files/navigation position.
        windows.set_window_topmost(int(self.winId()), False)

    def finish_cloud_link_handoff(self):
        """Reinstate normal Launch z-order after the user comes back to it."""
        if not getattr(self, '_cloud_link_handoff', False):
            return
        self._cloud_link_handoff = False
        if self.isVisible() and self.dismiss_on_outside_click:
            windows.set_window_topmost(int(self.winId()), True)

    def app_state(self, state):
        if getattr(self, '_cloud_link_handoff', False):
            # Provider dialog is a separate process. It should own the front
            # while this visible Launcher stays alive behind it. Resume the
            # usual always-on-top behavior only when Launch regains focus.
            if (state == Qt.ApplicationState.ApplicationActive
                    and self.isActiveWindow()):
                self.finish_cloud_link_handoff()
            return
        # A native recycle-bin operation or QMessageBox can briefly deactivate
        # the main Tool window. Do not dismiss its folder menu mid-operation.
        context = getattr(self, '_launch_context_menu', None)
        if (getattr(self, '_filesystem_dialog_depth', 0)
                or QApplication.activeModalWidget() is not None
                or (context is not None and context.isVisible())):
            return
        if state == Qt.ApplicationState.ApplicationInactive and self.isVisible():
            if getattr(self, 'dismiss_on_outside_click', True):
                hide_remote = getattr(self, 'hide_remote', None)
                if callable(hide_remote):
                    hide_remote()
                self.dismiss()
            else:
                # Keep the main window, but do not strand independent tool
                # columns or history popups above another application.
                self.hide_history_popup()
                if self.menu:
                    self.menu.close()
                self.expanded_view.hide_favorite_popup()

    def page_key(self, event):
        # Only Ctrl+Fn changes Page; plain F2/F5 belong to file operations.
        if event.modifiers()!=Qt.KeyboardModifier.ControlModifier:return False
        index=event.key()-Qt.Key.Key_F1
        if 0<=index<12:
            self.switch_page(index);return True
        return False

    def rename_current_middle_item(self):
        """F2 edits the selected file/folder in Files' second column only."""
        view = self.expanded_view
        if view.isVisible():
            view.rename_selected_middle_item()

    def refresh_current_middle_folder(self):
        """F5 re-reads the displayed folder without changing Page or focus."""
        view = self.expanded_view
        if view.isVisible():
            view.refresh_current_directory()

    def switch_page(self, index):
        if index>=self.tabs.count():return
        self._nav_before_change()
        self._nav_transition = True
        if self.menu:self.menu.close()
        self.hover_timer.stop();self.pending_menu_item=None
        self.stack=[];self.selection=None;self.checked.clear()
        self.tabs.setCurrentIndex(index)
        self.search.clear();self.render();self.search.setFocus()
        self._nav_transition = False
        self._nav_after_change()

    def page_changed(self,index):
        if self.data and index>=0:
            self._nav_before_change()
            self.page_id=self.pages[index]['page_id'];self.stack=[];self.selection=None;self.checked.clear();self.render()
            self._nav_after_change()

    def children(self,row=None):
        if row and row.get('item_kind')=='directory':
            path=Path(self.expander().expand(row['launch_browse_target']))
            result=[]
            for p in sort_browser_entries(path):
                result.append(dict(item_id=str(p),title=p.name,description=str(p),item_kind='directory' if p.is_dir() else 'command',icon_key='folder.yellow' if p.is_dir() else 'file',launch_browse_target=str(p),launch_actions=[{'launch_action_type':'Open','launch_target':str(p)}],_file=str(p),**({'_browse_file': str(p)} if p.is_file() else {})))
            return result
        parent=row['item_id'] if row else ''
        return sorted([x for x in self.data['items'] if x.get('enabled',True) and x['page_id']==(row['page_id'] if row else self.page_id) and x.get('parent_item_id','')==parent],key=lambda x:x.get('sort_order',0))

    def displayed_children(self, parent):
        """Skip redundant singleton folder levels for browser bookmarks only."""
        return visible_bookmark_children(parent, self.children)

    def set_list_column_mode(self, searching):
        """Use separate persistent widths for the ordinary menu and search.

        The main menu has a hidden header: its first/second-column boundary
        is a draggable grip and the second column fills the available space.
        Search mode retains both independently draggable header sections.
        """
        mode = 'result' if searching else 'main'
        if self._column_mode == mode:
            return
        self._column_mode = mode
        self._main_width_drag = None
        self._main_column_hover = False
        self.list.viewport().unsetCursor()
        self.list.viewport().update()
        self._applying_column_layout = True
        try:
            if searching:
                for column, default in ((0, 180), (1, 180)):
                    saved = self.saved_dimension(
                        self.settings.value(f'result_width_{column}', default),
                        default, 70, 2000)
                    self.list.setColumnWidth(column, saved)
            else:
                first = self.saved_dimension(self.settings.value('main_width_0', 235),
                                             235, 70, 2000)
                self.list.setColumnWidth(0, first)
                self.fill_main_second_column()
        finally:
            self._applying_column_layout = False

    def fill_main_second_column(self):
        """Keep the main menu at two full-width columns without a header."""
        if getattr(self, '_column_mode', None) != 'main':
            return
        viewport_width = self.list.viewport().width()
        if viewport_width < 150:  # Not laid out yet (during construction).
            return
        minimum = 70
        first = self.list.columnWidth(0)
        if first > viewport_width - minimum:
            first = max(minimum, viewport_width - minimum)
            self.list.setColumnWidth(0, first)
        second = max(minimum, viewport_width - first)
        if self.list.columnWidth(1) != second:
            self.list.setColumnWidth(1, second)

    def save_result_column_width(self, column, old_width, new_width):
        # Presentation settings only; never mutate the Launch DataJSON.
        if getattr(self, '_applying_column_layout', False) or new_width < 70:
            return
        if self._column_mode == 'result' and column in (0, 1):
            self.settings.setValue(f'result_width_{column}', new_width)
        elif self._column_mode == 'main' and column == 0:
            self.settings.setValue('main_width_0', new_width)
            self._applying_column_layout = True
            try:
                self.fill_main_second_column()
            finally:
                self._applying_column_layout = False

    def _main_divider_hit(self, x):
        if (self._column_mode != 'main' or getattr(self, 'selection', None) is not None
                or self.list.viewport().width() < 150):
            return False
        divider = self.list.columnViewportPosition(1)
        return abs(x - divider) <= 6

    def handle_main_column_resize(self, event):
        """Resize hidden-header columns by dragging the boundary in the list.

        The event filter is installed on the viewport. All unrelated row
        interactions (selection, launch, order drag) fall through unchanged.
        """
        kind = event.type()
        viewport = self.list.viewport()
        if kind == QEvent.Type.Resize:
            if self._column_mode == 'main' and not self._applying_column_layout:
                self._applying_column_layout = True
                try:
                    self.fill_main_second_column()
                finally:
                    self._applying_column_layout = False
            return False
        if kind == QEvent.Type.Leave and self._main_width_drag is None:
            self._main_column_hover = False
            viewport.unsetCursor()
            viewport.update()
            return False
        if kind not in (QEvent.Type.MouseMove, QEvent.Type.MouseButtonPress,
                        QEvent.Type.MouseButtonRelease, QEvent.Type.MouseButtonDblClick):
            return False
        x = event.position().toPoint().x()
        dragging = self._main_width_drag is not None
        hot = dragging or self._main_divider_hit(x)
        if hot != self._main_column_hover:
            self._main_column_hover = hot
            viewport.update()
        if hot:
            viewport.setCursor(Qt.CursorShape.SplitHCursor)
        else:
            viewport.unsetCursor()
        if kind == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton and hot:
            self._main_width_drag = (x, self.list.columnWidth(0))
            viewport.grabMouse()
            self.hover_timer.stop()
            self.pending_menu_item = None
            event.accept()
            return True
        if kind == QEvent.Type.MouseMove and dragging:
            start_x, start_width = self._main_width_drag
            width = max(70, min(viewport.width() - 70, start_width + x - start_x))
            if width != self.list.columnWidth(0):
                self.list.setColumnWidth(0, width)
            event.accept()
            return True
        if kind == QEvent.Type.MouseButtonRelease and dragging and event.button() == Qt.MouseButton.LeftButton:
            self._main_width_drag = None
            viewport.releaseMouse()
            self.settings.setValue('main_width_0', self.list.columnWidth(0))
            event.accept()
            return True
        if kind == QEvent.Type.MouseButtonDblClick and hot:
            event.accept()
            return True
        return False

    def sort_search_column(self, column):
        if column not in (0, 1) or not self.search.text().strip():
            return
        if self.result_sort_column == column:
            self.result_sort_desc = not self.result_sort_desc
        else:
            self.result_sort_column = column
            self.result_sort_desc = False
        self.settings.setValue('result_sort_column', column)
        self.settings.setValue('result_sort_desc', self.result_sort_desc)
        # Never rely on QTreeWidget.sortItems() while Qt sorting is disabled.
        # Rebuild from explicitly sorted visible column values.
        self.render()

    def apply_search_sort(self):
        if self.result_sort_column < 0 or not self.search.text().strip():
            return
        order = (Qt.SortOrder.DescendingOrder if self.result_sort_desc
                 else Qt.SortOrder.AscendingOrder)
        self.list.header().setSortIndicator(self.result_sort_column, order)
        # Items are already sorted by sort_search_pairs() before insertion.

    def _read_expanded_options(self):
        # Configuration chooses IDs, never displayed captions or ViewDef.
        path = LAUNCH_HOME / 'config' / 'expanded_view_options.json'
        try:
            import json
            if path.is_file():
                return normalize_options(json.loads(path.read_text(encoding='utf-8-sig')))
        except (OSError, ValueError) as exc:
            DIAG.warning('EXPANDED_VIEW invalid config: %s', exc)
        return normalize_options(None)

    def toggle_expanded_view(self):
        self.set_view_mode('classic' if self.view_mode == 'expanded' else 'expanded')

    def set_view_mode(self, mode):
        if mode not in ('classic', 'expanded') or mode == self.view_mode:
            return
        self.save_window_size()
        if self.menu:
            self.menu.close()
        self.hide_history_popup()
        self.view_mode = mode
        self.settings.setValue('view_mode', mode)
        self.settings.sync()
        self.restore_window_size()
        geometry = self.screen().availableGeometry()
        x = max(geometry.left(), min(self.x(), geometry.right() - self.width() + 1))
        y = max(geometry.top(), min(self.y(), geometry.bottom() - self.height() + 1))
        self.move(x, y)
        self.render()
        self.search.setFocus()

    def prepare_browser_before_first_show(self):
        """Initialize the embedded Browser while the launcher is still hidden.

        Creating Qt WebEngine while the main window is visible can cause a
        native-window flash.  Preloading after Files is shown only moves that
        flash from the Browser click to startup, so do it before any show().
        """
        if self.webview_settings.get('mode') != 'embedded':
            return
        if self.isVisible() or self.expanded_view.web_view is not None:
            return
        try:
            self.expanded_view.prewarm_browser()
        except Exception:
            # The launcher must remain usable even without Qt WebEngine.
            DIAG.exception('BROWSER_PREWARM before first show failed')

    def update_expanded_visibility(self):
        if not hasattr(self, 'expanded_view') or self.data is None:
            return
        self.expanded_options = self._read_expanded_options()
        targets = expanded_targets(self.data.get('items', []), self.expanded_options)
        active = should_expand(view_mode=self.view_mode, page_id=self.page_id,
                               query=self.search.text(), stack=self.stack,
                               selection=self.selection, options=self.expanded_options,
                               available=targets is not None)
        if active:
            roots, left, right = targets
            self.expanded_view.refresh(roots, left, right, self.expanded_options)
            self.footer.setText(
                '↑↓ 選択   → 進む   ← 第2列先頭   Enter 実行   Esc 閉じる'
                if self.files_root_hidden_mode and self.expanded_view._workspace_mode == 'files'
                else '↑↓ 選択   → 進む   ← 戻る   Enter 実行   Tab エリア切替   Esc 閉じる')
        self.list.setVisible(not active)
        if not active:
            self.expanded_view.hide_favorite_popup()
        self.expanded_view.setVisible(active)
        self.update_header_tab_width()
        self.update_files_item_count()
        self._nav_update_buttons()
        showing_classic = self.view_mode == 'expanded'
        self.mode_button.setText('Compact' if showing_classic else 'Three-layer')
        self.mode_button.setIcon(view_mode_icon('classic' if showing_classic else 'expanded',
                                                self.color_theme))
        self.mode_button.setToolTip(
            '仕事Pageで展開ビューを使えます' if self.view_mode == 'expanded'
            and self.page_id != self.expanded_options['page_id'] else
            '従来表示とFiles／ブックマーク同時表示を切替')
        self.compact_mode_action.setText(
            'Compact表示へ切り替え' if self.view_mode == 'expanded'
            else 'Files／Browser表示へ切り替え')

    def open_expanded_cascade(self, row, widget, item=None):
        # Transient deep menu reuses Launcher's existing actions/keyboard logic.
        if self.menu:
            self.menu.close()
        self.hover_timer.stop()
        menu_type = AppCascadeMenu if row.get('launch_source') == 'installed_apps' else CascadeMenu
        self.menu = menu_type(parent=self, launcher=self)
        self.menu.open_mode = 'keyboard'
        self.menu.compact_files_cascade = (row.get('item_kind') == 'directory'
                                           and not row.get('launch_source') == 'browser_bookmarks')
        # Only Three-layer bookmark cascades use the slimmer popup. Nested
        # children inherit the limit; all other popup widths remain untouched.
        view = getattr(self, 'expanded_view', None)
        is_bookmark = (view is not None and widget is view.right.tree)
        self.menu.bookmark_navigation = (is_bookmark or bool(
            row.get('_browser_bookmark') or row.get('launch_source') == 'browser_bookmarks'))
        if is_bookmark:
            self.menu.bookmark_compact_width = True
            self.menu.setMaximumWidth(min(self.menu.maximumWidth(), round(CASCADE_MAX_WIDTH * 0.7)))
        # Remember the exact expanded root button / panel row for Left-to-back.
        self.menu.return_focus_widget = widget
        self.menu.return_focus_item = item
        self.fill_cascade(self.menu, row)
        if isinstance(widget, QTreeWidget) and item is not None:
            rect = widget.visualItemRect(item)
            pos = widget.viewport().mapToGlobal(QPoint(widget.viewport().width() - 2, rect.top()))
        else:
            # First-level horizontal root buttons open directly BELOW their
            # own LEFT edge (ZIP -> ZIP), not from the button's right edge.
            # CascadeMenu.popup() already clamps the popup to the screen.
            pos = widget.mapToGlobal(QPoint(0, widget.height()))
        self.menu.popup(pos)
        self.menu.setFocus()

    def render(self,*args):
        if not self.data:return
        # A person chosen in global search opens a recipient picker. Keep it
        # while the new query still finds someone in the same choice group,
        # allowing multi-recipient selection. If the user searches for an
        # unrelated file/app/folder, return to normal *global* search instead
        # of leaving an empty recipient-only result list and selection toolbar.
        # This runs after the existing IME search debounce, never on preedit.
        query = self.search.text().strip()
        if self.selection is not None and self._global_selection_query is not None:
            choices = (choice for choice in self.data.get('launch_choices', ())
                       if choice.get('enabled', True) and
                       choice.get('group_id') == self.selection.get('launch_selection_group_id'))
            if leave_global_choice_selection(query, self._global_selection_query, choices):
                self.selection = None
                self.checked.clear()
                self._global_selection_query = None
                self._global_selection_choice_ids = None
        # Stop this brief reaction when switching pages, views or search terms.
        self.hide_root_left_feedback()
        self.hover_timer.stop();self.pending_menu_item=None
        self.selection_tools.setVisible(self.selection is not None)
        query=self.search.text().strip()
        self.set_list_column_mode(bool(query))
        self.list.setHeaderHidden(not bool(query))
        self.list.header().setSortIndicatorShown(bool(query) and self.result_sort_column >= 0)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded if query else Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list.clear_row_hover()
        self.list.set_wheel_current_visual(False)
        self._classic_wheel_edge_active = False
        self._classic_wheel_remainder = 0
        self.list.blockSignals(True);self.list.clear()
        self.list.order_enabled=not query and not self.selection and not (self.stack and (self.stack[-1]['item_kind']=='directory' or self.stack[-1].get('launch_source') in {'installed_apps','browser_bookmarks'} or self.stack[-1].get('_browser_bookmark'))) 
        self.list.order_rows=[]
        self.list.order_page=self.page_id
        self.list.order_parent=self.stack[-1]['item_id'] if self.stack else ''
        try:
            if self.selection:
                candidates=sorted([c for c in self.data.get('launch_choices',[]) if c.get('enabled',True) and c['group_id']==self.selection['launch_selection_group_id']],key=lambda c:c.get('sort_order',0))
                # Search display fields, not serialized JSON: a choice_id like
                # import_mail_000004 must not make se001 match '(003 or 004)'.
                # A global query may have matched only the owner's folder
                # path (e.g. "SE部"), not a contact's own name/address. After
                # clicking a checkbox, keep the exact original hit rows;
                # subsequent queries still filter the contact fields normally.
                visible_choices = filtered_selection_choices(
                    candidates, query, self._global_selection_query,
                    self._global_selection_choice_ids)
                pairs=[(c,'') for c in visible_choices]
            elif query:
                pairs=searchable_rows(self.data, query, bookmark_browser=self.bookmark_browser)
                try:
                    self.file_index_settings = file_index.load_options(self.file_index_options_path)
                except (OSError, ValueError) as exc:
                    DIAG.warning('FILE_INDEX search options invalid: %s', exc)
                    self.file_index_settings = {'index_mode': 'off', 'enabled': False}
                if file_index.index_mode(self.file_index_settings) != 'off':
                    for hit in file_index.search_index(
                            self.file_index_db, query,
                            self.file_index_settings['search_limit'],
                            entry_type=self.file_index_settings.get('index_target')):
                        # The SQLite table is shared between files and folders.
                        # Classify each hit individually in 'both' mode rather
                        # than treating the entire result as one kind.
                        target = self.file_index_settings.get('index_target', 'files')
                        is_folder = hit['extension'] == ''
                        if (target == 'folders' and not is_folder or
                                target == 'files' and is_folder):
                            continue
                        if is_folder:
                            row = dict(item_id='__folder_index_'+hit['path'],
                                       title=hit['name'], description=hit['directory'],
                                       item_kind='directory', icon_key='folder.yellow',
                                       _file=hit['path'],
                                       launch_browse_target=hit['path'],
                                       launch_actions=[{'launch_action_type':'Open',
                                                        'launch_target':hit['path']}])
                            pairs.append((row, 'フォルダー索引'))
                        else:
                            row = dict(item_id='__file_index_'+hit['path'],
                                       title=hit['name'], description=hit['directory'],
                                       item_kind='command', icon_key='file',
                                       _indexed_file=hit['path'], _file=hit['path'])
                            pairs.append((row, 'ファイル索引'))
            else:pairs=[(x,'') for x in (self.displayed_children(self.stack[-1]) if self.stack else self.children())]
            if query and self.result_sort_column in (0, 1):
                pairs = sort_search_pairs(pairs, self.result_sort_column,
                                          self.result_sort_desc, selection=bool(self.selection))
            if self.list.order_enabled:self.list.order_rows=[row for row,path in pairs]
            for row,path in pairs:
                title, desc = display_columns(row, path, selection=bool(self.selection))
                q=QTreeWidgetItem([title,desc]);q.setData(0,Qt.ItemDataRole.UserRole,row)
                q.setToolTip(0,row['title']);q.setToolTip(1,row.get('description','') if row.get('_browser_bookmark') else desc)
                q.setIcon(0,self.row_icon(row))
                q.setForeground(1,QColor('#647f71' if self.color_theme == 'light' else '#a6b4c7'))
                if self.selection or row.get('_search_selection_owner'):
                    q.setFlags(q.flags()|Qt.ItemFlag.ItemIsUserCheckable)
                    q.setCheckState(0,Qt.CheckState.Checked if self.selection and row['choice_id'] in self.checked else Qt.CheckState.Unchecked)
                self.list.addTopLevelItem(q)
            # Sort only matched search results.  Ordinary groups retain their
            # persisted manual sort_order and mouse drag operations.
            if query:self.apply_search_sort()
            if self.list.topLevelItemCount():self.list.setCurrentItem(self.list.topLevelItem(0))
            self.footer.setText(('↑↓ 移動  →/Space 選択  ← 戻る  F12 入力  '+str(len(self.checked))+'件') if self.selection else (' / '.join(x['title'] for x in self.stack) or '↑↓ 選択   → 展開/実行   Enter 実行   Ctrl+F1〜F12 / Ctrl+PageUp/Down Page切替'))
        except Exception as e:self.error(e)
        finally:self.list.blockSignals(False)
        self.update_expanded_visibility()

    def check_changed(self,item,col):
        if not self.selection:
            row = item.data(0, Qt.ItemDataRole.UserRole)
            if row and row.get('_search_selection_owner'):
                self.activate(row)
            return
        if self.selection:
            key=item.data(0,Qt.ItemDataRole.UserRole)['choice_id']
            if item.checkState(0)==Qt.CheckState.Checked:self.checked.add(key)
            else:self.checked.discard(key)
            self.footer.setText(f'↑↓ 移動  →/Space 選択  ← 戻る  F12 入力  {len(self.checked)}件')

    def select_all(self, selected):
        if not self.selection:return
        # Only affect the currently visible/filter-matched candidates.
        # Preserve checks outside the current filter for deliberate multi-step
        # selections; never silently select or clear hidden recipients.
        visible_ids = {self.list.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)['choice_id']
                       for i in range(self.list.topLevelItemCount())}
        self.checked = update_visible_checks(self.checked, visible_ids, selected)
        self.render()
        self.list.setFocus()

    def _nav_state(self):
        current = self.list.currentItem()
        row = current.data(0, Qt.ItemDataRole.UserRole) if current else None
        return dict(page_id=self.page_id, stack=tuple(self.stack),
                    selection=self.selection, checked=frozenset(self.checked),
                    global_selection_query=(self._global_selection_query if self.selection else None),
                    global_selection_choice_ids=(self._global_selection_choice_ids if self.selection else None),
                    query=self.search.text(), current_item_id=row.get('item_id') if row else None,
                    focus=('tabs' if self.tabs.hasFocus() else
                           'search' if self.search.hasFocus() else 'list'))

    def _nav_update_buttons(self):
        explorer = (hasattr(self, 'expanded_view') and
                    self.expanded_view.isVisibleTo(self))
        if hasattr(self, 'nav_forward_button'):
            self.nav_forward_button.setVisible(explorer)
            self.nav_forward_button.setEnabled(
                explorer and self.expanded_view.directory_history.can_forward)
        self.nav_back_button.setEnabled(
            self.expanded_view.directory_history.can_back
            if explorer else self.view_history.can_back)
        self.nav_back_button.setToolTip(
            'Filesのフォルダー履歴を戻る' if explorer else '前の画面に戻る')
        # Home is always available even if currently at the root.
        self.nav_home_button.setEnabled(bool(getattr(self, 'pages', None)))

    def _nav_reset(self):
        self._nav_search_timer.stop()
        self.view_history.reset(self._nav_state())
        self._nav_update_buttons()

    def _nav_flush_search(self):
        self._nav_search_timer.stop()
        if self._nav_restoring or self._nav_transition or not self.data:
            return
        self.view_history.push(self._nav_state())
        self._nav_update_buttons()

    def _nav_before_change(self):
        if self._nav_restoring or self._nav_transition:
            return
        self._nav_flush_search()
        self.view_history.update_current(self._nav_state())

    def _nav_after_change(self):
        if self._nav_restoring or self._nav_transition:
            return
        self._nav_search_timer.stop()
        self.view_history.push(self._nav_state())
        self._nav_update_buttons()

    def _nav_restore(self, state):
        self._nav_search_timer.stop()
        self._nav_restoring = True
        try:
            self.hide_history_popup()
            self.hover_timer.stop()
            self.pending_menu_item = None
            if self.menu:
                self.menu.close()
            # A configuration reload invalidates the history, so all row
            # objects here belong to the current data snapshot.
            page_ids = [page['page_id'] for page in self.pages]
            if state['page_id'] not in page_ids:
                return
            self.tabs.blockSignals(True)
            self.tabs.setCurrentIndex(page_ids.index(state['page_id']))
            self.tabs.blockSignals(False)
            self.page_id = state['page_id']
            self.stack = list(state['stack'])
            self.selection = state['selection']
            self.checked = set(state['checked'])
            self._global_selection_query = state.get('global_selection_query')
            self._global_selection_choice_ids = state.get('global_selection_choice_ids')
            self.search.setText(state['query'])
            self.render()
            target_id = state.get('current_item_id')
            for index in range(self.list.topLevelItemCount()):
                item = self.list.topLevelItem(index)
                row = item.data(0, Qt.ItemDataRole.UserRole)
                if row and row.get('item_id') == target_id:
                    self.list.setCurrentItem(item)
                    break
            focus = state.get('focus')
            if focus == 'tabs':
                self.tabs.setFocus(Qt.FocusReason.ShortcutFocusReason)
            elif focus == 'search':
                self.search.setFocus(Qt.FocusReason.ShortcutFocusReason)
            else:
                self.list.setFocus(Qt.FocusReason.ShortcutFocusReason)
        finally:
            self._nav_restoring = False
            self._nav_update_buttons()

    def navigate_back(self):
        if self.expanded_view.isVisible():
            self.expanded_view.history_back()
            return
        self._nav_flush_search()
        state = self.view_history.back()
        if state is not None:
            self._nav_restore(state)
        else:
            self._nav_update_buttons()

    def navigate_forward(self):
        """Only the Explorer directory stack has a Forward action."""
        if self.expanded_view.isVisible():
            self.expanded_view.history_forward()

    def open_bookmark_web_view(self, row):
        """Route bookmark URLs to WebView ONLY when embedded mode is enabled."""
        if self.webview_settings.get('mode') != 'embedded':
            return False  # Existing Open action handles the external browser.
        if (not self.expanded_view.isVisible() or
                not self.expanded_view.is_bookmark_row(row)):
            return False
        url = bookmark_web_url(row)
        if not url:
            return False
        # A bookmark picked in a nested cascade must honor the same choice
        # as a direct click in the left Bookmarks pane. Remote Browser's own
        # popup destination is handled separately in run_menu_item().
        if getattr(self.expanded_view, 'bookmark_new_tab', False):
            return self.expanded_view.show_web_url(url, new_tab=True)
        return self.expanded_view.show_web_url(url)

    def navigate_home(self):
        if not self.data or not self.pages:
            return
        if self.expanded_view.isVisible():
            # HOME contract (both Launch and Remote): close ALL Files Exp
            # branches, select its first root (usually PC), then show that
            # root's children in Files column 2. Browser tabs remain intact.
            # Reset the tree BEFORE selecting the first row so stale expanded
            # descendants and a previous current folder cannot survive HOME.
            view = self.expanded_view
            view.show_files_view()
            panel = None
            if self.files_exp_embedded_mode:
                panel = view.embedded_files_exp
                if not view._embedded_files_exp_roots_ready:
                    view.reload_embedded_files_exp_roots()
            else:
                remote = getattr(self, 'remote_window', None)
                candidate = getattr(remote, 'files_exp_panel', None)
                panel = candidate if (candidate is not None and candidate.isVisible()) else None
            if panel is not None:
                panel.reset_to_roots()  # Rebuild collapsed roots; persist reset.
            target = (panel.select_first_root_for_home()
                      if panel is not None else None)
            navigated = False
            if target is not None:
                kind, directory = target
                if kind == 'pc':
                    navigated = self.navigate_files_exp_pc()
                elif kind == 'folder':
                    navigated = self.navigate_files_exp_folder(directory)
            if not navigated:
                # Compatibility fallback for configurations with no Files Exp
                # model (classic/hidden first column, no Remote open).
                first = view.left.tree.topLevelItem(0)
                if first is not None:
                    view.left.tree.setCurrentItem(first)
                    view.choose_files(first, 0)
            self.remote_focus_area('directory' if self.files_root_hidden_mode
                                   else 'files')
            return
        self._nav_before_change()
        self._nav_restoring = True
        try:
            self.hide_history_popup()
            if self.menu:
                self.menu.close()
            self.hover_timer.stop()
            self.pending_menu_item = None
            self.stack = []
            self.selection = None
            self.checked.clear()
            self.page_id = self.pages[0]['page_id']
            self.tabs.blockSignals(True)
            self.tabs.setCurrentIndex(0)
            self.tabs.blockSignals(False)
            self.search.clear()
            self.render()
            self.list.setFocus(Qt.FocusReason.ShortcutFocusReason)
        finally:
            self._nav_restoring = False
        self._nav_after_change()

    def go_back(self):
        # A selection opened from the expanded Page's first-level menu
        # temporarily switches to the classic choice grid.  When Left (or
        # the on-screen Back button) dismisses that grid, return keyboard
        # focus to its *own* opener, e.g. メール宛先, not the hidden classic list.
        # Only direct first-level children qualify: nested menus retain their
        # established one-level-back behaviour and classic mode is unchanged.
        expanded_return_root = None
        if (self.selection and self.view_mode == 'expanded' and not self.stack
                and not self.search.text().strip()):
            parent_id = self.selection.get('parent_item_id')
            view = getattr(self, 'expanded_view', None)
            if (parent_id and view is not None
                    and any(row.get('item_id') == parent_id for row in view.root_rows)):
                expanded_return_root = parent_id
        self._nav_before_change()
        if self.selection:
            self.selection = None; self.checked.clear()
        elif self.stack:
            self.stack.pop()
        self.search.clear(); self.render()
        if expanded_return_root and self.expanded_view.isVisible():
            self.expanded_view.focus_root(item_id=expanded_return_root)
        else:
            self.list.setFocus()
        self._nav_after_change()

    def hide_root_left_feedback(self):
        """Dismiss the harmless left-edge reaction when the view changes."""
        timer = getattr(self, '_root_left_feedback_timer', None)
        if timer is not None:
            timer.stop()
        bubble = getattr(self, '_root_left_feedback', None)
        if bubble is not None:
            bubble.hide()

    def show_root_left_feedback(self):
        """Brief, silent balloon for Left at the root's first row.

        It is a child of the list viewport, not an OS tooltip/popup: it never
        acquires keyboard focus and never interferes with Page-tab arrows.
        """
        bubble = getattr(self, '_root_left_feedback', None)
        if bubble is None:
            bubble = QLabel('🎺 ぱふぅ〜！！', self.list.viewport())
            bubble.setObjectName('rootLeftFeedback')
            bubble.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bubble.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            bubble.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self._root_left_feedback = bubble
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(bubble.hide)
            self._root_left_feedback_timer = timer
        if self.color_theme == 'light':
            bubble.setStyleSheet('QLabel#rootLeftFeedback { '
                'background:#ecf5ff; color:#263f58; border:1px solid #85adcf; '
                'border-radius:12px; padding:7px 13px; font-size:15px; '
                'font-weight:600; }')
        else:
            bubble.setStyleSheet('QLabel#rootLeftFeedback { '
                'background:#2f4961; color:#f3f8ff; border:1px solid #85aed8; '
                'border-radius:12px; padding:7px 13px; font-size:15px; '
                'font-weight:600; }')
        bubble.adjustSize()
        viewport = self.list.viewport()
        current = self.list.currentItem()
        row_rect = self.list.visualItemRect(current) if current is not None else QRect()
        # Sit just below the first row, towards its right side. Keep the
        # balloon completely inside the viewport on narrow windows.
        x = max(4, min(viewport.width() - bubble.width() - 4,
                       (viewport.width() - bubble.width()) // 2))
        y = max(4, min(viewport.height() - bubble.height() - 4,
                       row_rect.bottom() + 6))
        bubble.move(x, y)
        bubble.show()
        bubble.raise_()
        self._root_left_feedback_timer.start(800)

    def at_root_first_row(self):
        """Only the unfiltered root's actual first row has a left edge."""
        return (self.in_root_page_navigation()
                and self.list.topLevelItemCount() > 0
                and self.list.currentItem() is self.list.topLevelItem(0))

    def record_main_hover_motion(self, point, now=None):
        """Keep a short, viewport-local mouse trail; no synthetic events."""
        now = time.monotonic() if now is None else now
        recent = [(t, p) for t, p in getattr(self, '_main_hover_motion', ())
                  if now - t <= .18]
        recent.append((now, point))
        self._main_hover_motion = recent[-20:]

    def main_hover_heading_to_cascade(self):
        """Protect diagonal travel into an open right-hand column only."""
        recent = getattr(self, '_main_hover_motion', ())
        if len(recent) < 2:
            return False
        start, end = recent[0][1], recent[-1][1]
        dx, dy = end.x() - start.x(), end.y() - start.y()
        return dx >= 10 and dx * 2 >= abs(dy)

    def hover(self,q,col):
        if getattr(self, '_classic_wheel_processing', False):
            return  # Scrolling beneath a fixed cursor is not a real hover.
        if self.selection or QApplication.mouseButtons() & Qt.MouseButton.LeftButton or getattr(self.list,'order_dragging',False):return
        current = self.menu if self.menu is not None and self.menu.isVisible() else None
        # Hovering from one root row to another should use the configured
        # latency. A longer protection window is only needed when the cursor
        # is actually travelling diagonally toward the existing child column.
        switching = current is not None and current.owner_item is not q
        if not switching:
            self.list.setCurrentItem(q)
        self.pending_menu_item=q
        delay = int(self.data.get('launch_hover_delay_ms',250))
        if switching and self.main_hover_heading_to_cascade():
            delay = max(delay, 650)
        self.hover_timer.start(delay)

    def open_hover(self):
        q=self.pending_menu_item
        if q and self.isVisible():
            row=q.data(0,Qt.ItemDataRole.UserRole)
            if row.get('item_kind') in {'category','directory'}:
                if self.list.itemAt(self.list.viewport().mapFromGlobal(QCursor.pos()))==q:
                    self.list.setCurrentItem(q)
                    self.cascade(row,q,"hover")

    def check_hover_menus(self, pos=None, now=None):
        # When a context menu owns the pointer, the underlying cascade must
        # remain visible and highlighted, not time out as if mouse left it.
        context = getattr(self, '_launch_context_menu', None)
        if getattr(self, '_filesystem_dialog_depth', 0) or (context is not None and context.isVisible()):
            return
        pos=QCursor.pos() if pos is None else pos
        now=time.monotonic() if now is None else now
        remote = getattr(self, 'remote_window', None)
        if (remote is not None and remote.isVisible()
                and remote.rect().contains(remote.mapFromGlobal(pos))):
            # A hover-opened cascade must survive travel back to the remote;
            # a menu is dismissed by explicit commands, not the wheel hotspot.
            column = self.menu
            while column is not None and column.isVisible():
                column.outside_since = None
                column = column.child
            return
        # Stop delayed opens as soon as their originating row is left.
        if self.pending_menu_item and self.list.itemAt(self.list.viewport().mapFromGlobal(pos))!=self.pending_menu_item:
            self.hover_timer.stop();self.pending_menu_item=None
        menu=self.menu
        while menu and menu.isVisible():
            if menu.hover_timer.isActive() and menu.actionAt(menu.mapFromGlobal(pos))!=menu.activeAction():menu.hover_timer.stop()
            if menu.open_mode == "hover":
                related=False;desc=menu
                while desc and desc.isVisible():
                    if desc.rect().contains(desc.mapFromGlobal(pos)):related=True;break
                    desc=desc.child
                parent=menu.parentWidget()
                if isinstance(parent,CascadeMenu):
                    related=related or (parent.isVisible() and parent.actionAt(parent.mapFromGlobal(pos))==menu.owner_action)
                elif menu.owner_item:
                    viewport_pos = self.list.viewport().mapFromGlobal(pos)
                    related = related or self.list.visualItemRect(menu.owner_item).contains(viewport_pos)
                    # A pending switch is a mouse *hover*, not a click. While
                    # crossing neighbouring rows toward the open menu, do not
                    # retire the old column ahead of the longer hover delay.
                    related = related or (self.hover_timer.isActive() and
                        self.pending_menu_item is not None and
                        self.list.itemAt(viewport_pos) is self.pending_menu_item)
                if related:menu.outside_since=None
                elif menu.outside_since is None:menu.outside_since=now
                elif now-menu.outside_since >= (
                        .8 if (menu.owner_item is not None and
                               self.list.viewport().rect().contains(
                                   self.list.viewport().mapFromGlobal(pos))) else .25):
                    # Crossing the main list on the way to a tool column must
                    # not dismiss it. Normal departure outside the launcher
                    # keeps the original 250ms responsiveness.
                    menu.close();break
            menu=menu.child

    def persist_order(self, ids, page, parent, selected):
        try:
            self.data,self.mtime=save_order(CONFIG,self.mtime,page,parent,ids)
            self.data=browser_bookmarks.attach(installed_apps.attach(self.data,self.app_records),self.bookmark_browser,self.bookmark_profiles)
            self.render()
            for i in range(self.list.topLevelItemCount()):
                q=self.list.topLevelItem(i)
                if q.data(0,Qt.ItemDataRole.UserRole)['item_id']==selected:self.list.setCurrentItem(q);break
            def refresh(menu):
                if not menu:return
                if menu.child and menu.child.isVisible():
                    refresh(menu.child);return
                if menu.isVisible() and menu.order_enabled:
                    if menu.child:menu.child.close()
                    context=menu.order_context;menu.clear_local_filter();menu.clear();menu.openers.clear()
                    self.fill_cascade(menu,context)
                    # Rebuilding a currently visible column must also restore
                    # its permanently displayed search bar.
                    menu._ensure_local_filter()
                    for action in menu.actions():
                        if action.data() and action.data()['item_id']==selected:menu.setActiveAction(action);break
                else:refresh(menu.child)
            QTimer.singleShot(0,lambda:refresh(self.menu))
            self.footer.setText('表示順を保存しました')
            return True
        except Exception as e:
            self.error('表示順を保存できません: '+str(e));return False

    def initialize_search_ime(self):
        """Initialize default IME without interrupting a history-to-search handoff."""
        if getattr(self, '_history_ime_handoff', False):
            # A Japanese preedit is already underway; forcing halfwidth English
            # on the deferred FocusIn callback would break its composition.
            self._history_ime_handoff = False
            return
        if self.search.hasFocus():
            initialize_halfwidth_english(int(self.search.winId()))

    def focus_search(self, select=True):
        self.hide_history_popup()
        self.hover_timer.stop();self.pending_menu_item=None
        if self.menu:self.menu.close()
        self.activateWindow();self.search.setFocus()
        if select:self.search.selectAll()

    def fill_cascade(self, menu, parent):
        if isinstance(menu,AppCascadeMenu):
            menu.populate(self.children(parent));return
        menu.order_enabled=parent['item_kind']=='category' and parent.get('launch_source') not in {'installed_apps','browser_bookmarks','remote_files_roots','remote_browser_bookmark_roots'} and not parent.get('_browser_bookmark')
        menu.order_page=parent.get('page_id',self.page_id)
        menu.order_parent=parent.get('item_id','')
        menu.order_context=parent
        menu.order_rows=[]
        try:
            if parent.get('launch_source') == 'remote_files_roots':
                # The first column belongs to ExpandedLauncherView, not to
                # the current breadcrumb or a separate configuration tree.
                rows = self._remote_files_first_column_rows()
            elif parent.get('launch_source') == 'remote_browser_bookmark_roots':
                # Exactly the visible Browser bookmark entries, retaining
                # their underlying row identities for nested folder / URL use.
                rows = self._remote_browser_bookmark_rows()
            elif getattr(menu, 'remote_folder_navigation', False) and parent.get('_system_drives_root'):
                # "PC" is a virtual root. Expanded Files resolves it to real
                # drive rows, so re-use that same resolver here.
                rows = self.expanded_view.browser_rows(parent)
            else:
                rows = self.displayed_children(parent)
            if parent.get('launch_source') == 'remote_page':
                rows = visible_remote_page_roots(rows)
            for row in rows:
                folder = row['item_kind'] in {'category','directory'}
                metrics = menu.fontMetrics()
                label, tooltip = cascade_label(
                    row, parent['item_kind'], max(120, menu.maximumWidth() - CASCADE_TEXT_RESERVE),
                    lambda text, width: metrics.elidedText(text, Qt.TextElideMode.ElideRight, width),
                    metrics.horizontalAdvance)
                action = menu.addAction(self.row_icon(row), label)
                action.setToolTip(tooltip)
                action.setData(row)
                if menu.order_enabled:menu.order_rows.append(row)
                if folder:
                    def open_child(mode="keyboard", m=menu, r=row, a=action):
                        # A renamed folder changes QAction.data while this
                        # open callback remains installed. Resolve the CURRENT
                        # row when navigating rather than capturing a dead path.
                        if getattr(m, 'remote_folder_navigation', False):
                            latest = a.data()
                            if isinstance(latest, dict):
                                r = latest
                        if m.child:m.child.close();m.child.deleteLater()
                        m.child=(RemoteFolderCascade if getattr(m, 'remote_folder_navigation', False)
                                 else AppCascadeMenu if r.get('launch_source')=='installed_apps'
                                 else CascadeMenu)(parent=m,launcher=self)
                        if hasattr(m, 'remote_popup_bounds'):
                            m.child.remote_popup_bounds = m.remote_popup_bounds
                        m.child.open_mode=mode;m.child.owner_action=a
                        m.child.bookmark_navigation = getattr(m, 'bookmark_navigation', False)
                        m.child.remote_page_navigation = getattr(m, 'remote_page_navigation', False)
                        m.child.compact_files_cascade = getattr(m, 'compact_files_cascade', False)
                        if getattr(m, 'remote_folder_navigation', False):
                            m.child.remote_folder_root = m.remote_folder_root or m
                        if getattr(m, 'bookmark_compact_width', False):
                            m.child.bookmark_compact_width = True
                            m.child.setMaximumWidth(min(m.child.maximumWidth(),
                                                       round(CASCADE_MAX_WIDTH * 0.7)))
                        self.fill_cascade(m.child,r)
                        # Anchor to the *visible parent menu's* right edge,
                        # not actionGeometry's width (which can be stale after
                        # a local filter or an oversized scroll adaptation).
                        action_rect = m.actionGeometry(a)
                        m.child.popup(m.mapToGlobal(QPoint(m.width() - 1, action_rect.top())))
                        m.child.setFocus()
                    menu.openers[action]=open_child
                    action.triggered.connect(lambda checked=False, fn=open_child:fn())
                else:
                    action.triggered.connect(lambda checked=False,r=row:self.run_menu_item(r))
            if (parent['item_kind']=='directory'
                    and not getattr(menu, 'remote_folder_navigation', False)):
                menu.addSeparator()
                open_folder_action = menu.addAction('このフォルダーを開く',
                                                     lambda: self.run_menu_item(parent))
                # Unlike regular rows, this utility action carries no item data.
                # Right-arrow is the same explicit execution as Enter/click.
                open_folder_action.setProperty('launch_right_arrow_executes', True)
            if menu.isEmpty():
                if parent.get('launch_source')=='browser_bookmarks':
                    menu.addAction('取得結果が空です（取得診断を開く）',self.show_bookmark_diagnostics)
                    menu.addAction('Bookmarksファイルを指定する',self.pick_bookmark_file)
                else:
                    menu.addAction('項目なし').setEnabled(False)
        except Exception as e:menu.addAction(str(e)).setEnabled(False)

    def _ask_overwrite(self, destination, conflicts):
        """Explicit approval for replacing matching files / merging folders."""
        shown = '\n'.join('・' + path.name for path in conflicts[:8])
        if len(conflicts) > 8:
            shown += f'\nほか {len(conflicts) - 8} 件'
        self._filesystem_dialog_depth = getattr(self, '_filesystem_dialog_depth', 0) + 1
        try:
            return QMessageBox.question(
                self, '同名の項目があります',
                f'貼り付け先: {destination}\n\n'
                f'次の {len(conflicts)} 件は既に存在します。\n{shown}\n\n'
                '同名ファイルは上書きし、同名フォルダーは中身を統合しますか？\n'
                '（フォルダー内の無関係なファイルは削除しません）',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes
        finally:
            self._filesystem_dialog_depth -= 1

    def _warn_ambiguous_paste_target(self, message):
        """Tell the user why Paste was blocked; do not touch clipboard/files."""
        self.error(str(message))
        QMessageBox.warning(self, '貼り付け先を1つ選択してください', str(message))

    @contextmanager
    def filesystem_progress(self, verb, total):
        """One shared indicator for bulk paste/delete; always closed on error."""
        # Single-item operations can be large too; show processing feedback.
        progress = FilesOperationProgress(self, verb, total)
        self._filesystem_busy = True
        try:
            progress.show()
            progress.advance(0, total)
            yield progress.advance
        finally:
            progress.close()
            progress.deleteLater()
            self._filesystem_busy = False

    def paste_with_progress(self, plan, *, move=False, overwrite=False):
        """Modal UI, nonblocking worker, no second Paste while running.

        The caller keeps control of clipboard cleanup and view refresh AFTER
        completion, exactly as before. Exceptions keep their original type.
        """
        with self.filesystem_progress('移動' if move else 'コピー', len(plan)) as advance:
            worker = FilesPasteWorker(plan, move, overwrite, self)
            loop = QEventLoop(self)
            outcome = {}

            def success(count):
                outcome['count'] = count
                loop.quit()

            def failure(exc):
                outcome['exception'] = exc
                loop.quit()

            worker.step.connect(advance)
            worker.succeeded.connect(success)
            worker.failed.connect(failure)
            # Start after the nested event loop begins; a tiny copy can finish
            # immediately without racing the loop's first exec().
            QTimer.singleShot(0, worker.start)
            loop.exec()
            worker.wait()
            if 'exception' in outcome:
                raise outcome['exception']
            return outcome['count']

    def _record_transfer_result(self, destination, names):
        """Show a short, confirmed paste highlight shared with Files Exp.

        Paste feedback is *not* a selection or clipboard state. It must end
        automatically even if the user does nothing after the paste.
        Restart one timer per successful paste rather than stacking callbacks
        that might prematurely clear a newer operation's feedback.
        """
        self._latest_pasted_paths = tuple(pasted_paths_for(destination, names))
        panel = getattr(getattr(self, 'remote_window', None), 'files_exp_panel', None)
        if panel is not None:
            panel.refresh_transfer_visuals()
        embedded = getattr(getattr(self, 'expanded_view', None), 'embedded_files_exp', None)
        if embedded is not None:
            embedded.refresh_transfer_visuals()
        timer = getattr(self, '_paste_feedback_timer', None)
        if timer is None:
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(self._clear_previous_paste_feedback)
            self._paste_feedback_timer = timer
        timer.start(2500)

    def files_exp_panels(self):
        """Companion and in-window tree share filesystem events, not state.

        The embedded tree may be present even when Remote is never created.
        Avoid treating either panel's transient selection as the write target.
        """
        remote_panel = getattr(getattr(self, 'remote_window', None),
                               'files_exp_panel', None)
        embedded_panel = getattr(getattr(self, 'expanded_view', None),
                                 'embedded_files_exp', None)
        return tuple(panel for panel in (remote_panel, embedded_panel)
                     if panel is not None)

    def notify_folder_mutation(self, *directories):
        """Notify the companion of filesystem changes from EVERY Launch UI.

        Reload only affected, already-visible branches. Unopened branches
        remain lazy and all unrelated expansion state remains intact.
        """
        panels = tuple(panel for panel in getattr(self, 'files_exp_panels', lambda: tuple(
            panel for panel in (
                getattr(getattr(self, 'remote_window', None), 'files_exp_panel', None),
                getattr(getattr(self, 'expanded_view', None), 'embedded_files_exp', None))
            if panel is not None))()
                       if panel.isVisible())
        if not panels:
            return
        seen = set()
        for directory in directories:
            if not directory:
                continue
            folder = Path(directory)
            if not folder.is_dir():
                folder = folder.parent
            key = path_key(folder)
            if key in seen or not folder.is_dir():
                continue
            seen.add(key)
            for panel in panels:
                panel.refresh_directory_branch(str(folder))

    def refresh_main_files_cut_visuals(self):
        """Use the same pending-cut visual in both native Files columns."""
        view = getattr(self, 'expanded_view', None)
        if view is None:
            return
        mime = QApplication.clipboard().mimeData()
        cut = {path_key(p) for p in (clipboard_sources(mime)
                                    if is_cut_clipboard(mime) else ())}
        for pane in (view.left, view.middle):
            tree = pane.tree
            for index in range(tree.topLevelItemCount()):
                item = tree.topLevelItem(index)
                row = view.row_data(item)
                if not row or row.get('item_kind') != 'directory':
                    continue
                raw_path = row.get('launch_browse_target') or row.get('_file')
                if not raw_path:
                    continue
                try:
                    resolved = self.expander().expand(str(raw_path))
                except (OSError, ValueError):
                    continue
                base = self.row_icon(row)
                was_cut = bool(item.data(0, Qt.ItemDataRole.UserRole + 9))
                is_cut = path_key(resolved) in cut
                if is_cut:
                    base = CascadeMenu._subdued_icon(base)
                    if not was_cut:
                        item.setForeground(0, QBrush(QColor('#9ca8af')))
                        item.setData(0, Qt.ItemDataRole.UserRole + 9, True)
                elif was_cut:
                    # Restore an explicit readable text color. Some Windows
                    # Qt styles do not recover drive names after setForeground
                    # with an empty/default QBrush().
                    normal_text = theme_palette(self.color_theme)['text']
                    item.setForeground(0, QBrush(QColor(normal_text)))
                    item.setData(0, Qt.ItemDataRole.UserRole + 9, False)
                item.setIcon(0, base)
        # This is only an icon change; never touch active row/selection.

    def refresh_files_exp_directory(self, directory):
        """Rescan a folder in Files Exp, preserving expanded paths and cursor."""
        for panel in getattr(self, 'files_exp_panels', lambda: tuple(
            panel for panel in (
                getattr(getattr(self, 'remote_window', None), 'files_exp_panel', None),
                getattr(getattr(self, 'expanded_view', None), 'embedded_files_exp', None))
            if panel is not None))():
            panel.refresh_directory_branch(str(directory))

    def refresh_folder_information(self, directory):
        """One explicit Refresh action shared by Files and Remote menus."""
        target = Path(directory)
        if not target.is_dir():
            self.error('更新するフォルダーが見つかりません: ' + str(target))
            return False
        self.refresh_files_exp_directory(target)
        view = getattr(self, 'expanded_view', None)
        if view is not None and view.isVisible():
            current = view.current_directory()
            if current:
                try:
                    belongs = (path_key(current) == path_key(target) or
                               Path(current).resolve().is_relative_to(target.resolve()))
                except (OSError, ValueError):
                    belongs = False
                if belongs:
                    view.refresh_middle()
        # Refresh is itself a completed context action. Show fresh contents
        # in Files/Exp, but never re-open a floating menu after dismissal.
        self.footer.setText('最新の情報に更新しました: ' + str(target))
        return True

    def _clear_previous_paste_feedback(self):
        """End the prior operation's visual result, not its clipboard data.

        Every new filesystem operation starts a fresh feedback cycle. Apply it
        to the whole visible cascade chain: a highlighted row may be in a
        nested directory rather than the menu receiving the new action.
        """
        timer = getattr(self, '_paste_feedback_timer', None)
        if timer is not None:
            timer.stop()
        self._latest_pasted_paths = ()
        panel = getattr(getattr(self, 'remote_window', None), 'files_exp_panel', None)
        if panel is not None:
            panel.refresh_transfer_visuals()
        embedded = getattr(getattr(self, 'expanded_view', None), 'embedded_files_exp', None)
        if embedded is not None:
            embedded.refresh_transfer_visuals()
        menu = getattr(self, 'menu', None)
        while menu is not None:
            if getattr(menu, '_pasted_feedback_paths', ()):
                menu._pasted_feedback_paths = ()
                menu._refresh_transfer_visuals()
            menu = getattr(menu, 'child', None)

    def paste_into_directory(self, menu, *, destination_override=None):
        """Paste into the folder displayed by the cascade or right-clicked."""
        context = menu._folder_container_row()
        if context is None:
            return
        # A new paste replaces the preceding operation's highlighted result,
        # even when overwrite is cancelled or the paste later fails.
        reset = getattr(self, '_clear_previous_paste_feedback', None)
        if callable(reset):
            reset()
        try:
            destination = (Path(destination_override) if destination_override is not None
                           else Path(self.expander().expand(context['launch_browse_target'])))
            if not destination.is_dir():
                raise ValueError('貼り付け先のフォルダーが存在しません: ' + str(destination))
            clipboard = QApplication.clipboard()
            mime = clipboard.mimeData()
            sources = clipboard_sources(mime)
            move = is_cut_clipboard(mime)
            virtual = is_virtual_file_clipboard(mime) and (
                not sources or any(not src.exists() for src in sources))
            if virtual:
                names = virtual_clipboard_names(mime)
                preflight_virtual_destination(destination, names, allow_existing=True)
                existing = {entry.name.casefold(): entry for entry in destination.iterdir()}
                conflicts = [existing[name.casefold()] for name in names or ()
                             if name.casefold() in existing]
                if conflicts and not self._ask_overwrite(destination, conflicts):
                    return
                before = {path.name.casefold() for path in destination.iterdir()}
                # The Shell can show a second overwrite prompt for ZIP members.
                # Suppress it ONLY when known name conflicts were explicitly
                # approved in Launch. Unknown clipboard names keep native UI.
                paste_virtual_shell_items(destination, overwrite_confirmed=bool(conflicts))
                if names:
                    names_done = names
                else:
                    names_done = [p.name for p in destination.iterdir()
                                  if p.name.casefold() not in before]
                self.footer.setText(f'ZIP内の項目をコピーしました → {destination}')
            else:
                plan = (make_paste_plan(destination, sources, allow_existing=True)
                        if move else make_paste_plan(destination, sources,
                                                     allow_existing=True,
                                                     duplicate_in_place=True))
                conflicts = paste_conflicts(plan)
                if conflicts and not self._ask_overwrite(destination, conflicts):
                    return
                run_progress = getattr(self, 'paste_with_progress', None)
                if callable(run_progress):
                    count = run_progress(plan, move=move, overwrite=bool(conflicts))
                else:
                    count = paste_items(plan, move=move, overwrite=bool(conflicts))
                names_done = [item.target.name for item in plan]
                if move:
                    clipboard.clear()
                self.footer.setText(f'{count}件を{"移動" if move else "コピー"}しました → {destination}')
            menu._pasted_feedback_paths = pasted_paths_for(destination, names_done)
            # Move changes *both* folder trees. Capture source parents from the
            # successful plan rather than looking at the clipboard after clear().
            moved_from = (moved_source_parent_directories(plan, move=True)
                          if move and not virtual else ())
            self.refresh_files_exp_directory(destination)
            # The destination gains the moved entries; each source parent loses
            # them. Reconcile both visible tree branches after a confirmed MOVE.
            if move and not virtual:
                for source_parent in moved_from:
                    if path_key(source_parent) != path_key(destination):
                        self.refresh_files_exp_directory(source_parent)
            report = getattr(self, '_record_transfer_result', None)
            if callable(report):
                report(destination, names_done)
            # A finished Paste closes its context menu; the updated Files/Exp
            # views and transient feedback show the result instead of
            # re-opening a floating cascade after the user's command.
            closer = getattr(self, 'close_finished_file_context_menus', None)
            if callable(closer):
                QTimer.singleShot(0, closer)
            else:
                # Historical test adapters have no popup lifecycle owner.
                QTimer.singleShot(0, lambda m=menu: self.refresh_pasted_directory(
                    m, reopen=True, focus_pasted=True))
        except (OSError, ValueError) as exc:
            DIAG.exception('DIRECTORY_PASTE target=%s', context.get('launch_browse_target'))
            self.error('貼り付けできませんでした: ' + str(exc))

    def _directory_menu_for_path(self, directory):
        """Find a currently created folder column that shows this directory."""
        menu = self.menu
        wanted = path_key(directory)
        while isinstance(menu, CascadeMenu):
            context = menu._folder_container_row()
            if context is not None:
                try:
                    actual = self.expander().expand(context['launch_browse_target'])
                    if path_key(actual) == wanted:
                        return menu
                except (ValueError, KeyError):
                    pass
            menu = menu.child
        return None

    def restore_launcher_for_transfer_review(self):
        """Re-arm the ordinary launcher's show/dismiss lifecycle after a modal.

        A modal recycle-bin confirmation (or Windows Shell ZIP paste) may hide
        the main Qt.Tool window. Replacing its separate floating folder column
        while the main window stays hidden creates an orphan: the desktop mouse
        hook only regards a visible launcher as dismissible. Restore the EXISTING
        launcher, without calling summon() (which toggles visibility / resets
        navigation), before reopening the refreshed column.
        """
        if not self.isVisible():
            self.show()
            self.raise_()
            self.activateWindow()

    def refresh_pasted_directory(self, previous, *, reopen=False, focus_pasted=False,
                                 review_deleted=False):
        """Replace a directory column in place, preserving tree/search/scroll."""
        if not previous.isVisible() and not reopen:
            return
        context = previous._folder_container_row()
        if context is None:
            return
        # The main Tool window must own the floating cascade. A modal action
        # can hide the main window even though this asynchronous refresh runs.
        self.restore_launcher_for_transfer_review()
        origin = previous.pos()
        query = previous.filter_edit.text() if previous.filter_edit is not None else ''
        scroll = (previous.scroll_tree.verticalScrollBar().value()
                  if previous.scroll_tree is not None else 0)
        parent = previous.parentWidget()
        is_nested = isinstance(parent, CascadeMenu)
        replacement = CascadeMenu(parent=parent if is_nested else self, launcher=self)
        # A delete confirmation moves the mouse to the modal dialog, outside
        # the old hover column. Keep the result visible until user dismissal;
        # hover mode would otherwise close it in 250ms before it can be read.
        replacement.open_mode = 'keyboard' if review_deleted else previous.open_mode
        replacement._delete_review_visible = review_deleted
        replacement._pasted_feedback_paths = (
            getattr(previous, '_pasted_feedback_paths', ()) if focus_pasted else ())
        replacement.owner_action = previous.owner_action
        replacement.owner_item = previous.owner_item
        replacement.outside_since = None
        if is_nested:
            parent.child = replacement
            if reopen and not parent.isVisible():
                parent.show()
        else:
            self.menu = replacement
        previous.close()
        previous.deleteLater()
        self.fill_cascade(replacement, context)
        replacement.popup(origin)
        if query and replacement.filter_edit is not None:
            replacement.filter_edit.setText(query)
        if replacement.scroll_tree is not None:
            if focus_pasted:
                def reveal_new_rows(tree=replacement.scroll_tree):
                    for index in range(tree.topLevelItemCount()):
                        item = tree.topLevelItem(index)
                        action = item.data(0, Qt.ItemDataRole.UserRole)
                        if (not item.isHidden() and action is not None
                                and action.property('launch_transfer_state') == 'pasted'):
                            tree.scrollToItem(item, QAbstractItemView.ScrollHint.PositionAtCenter)
                            return
                QTimer.singleShot(0, reveal_new_rows)
            else:
                QTimer.singleShot(0, lambda t=replacement.scroll_tree, y=scroll:
                                  t.verticalScrollBar().setValue(y))
        replacement.setFocus()

    def refresh_deleted_directory(self, menu):
        """After confirmed deletion, SHOW the refreshed folder column.

        A QMenu parented to a Qt.Tool column can become temporarily hidden
        while QMessageBox or the row's context QMenu owns focus.  Visibility,
        focus and dismiss-generation checks at this point are NOT evidence of
        user dismissal: they previously skipped refresh altogether.

        Reuse the exact same replacement path as successful Paste.  That path
        restores the folder, query, scroll and normal close behaviour.
        """
        if menu is None:
            return
        self.refresh_pasted_directory(menu, reopen=True, focus_pasted=False,
                                      review_deleted=True)

    def run_menu_item(self, row):
        # Remote > Browser right-click uses its own tab destination, while
        # the normal Bookmarks pane has an independent destination selector.
        # Other cascades retain their established activation semantics.
        root = getattr(self, 'menu', None)
        if (getattr(root, 'remote_browser_bookmark_roots', False)
                and self.webview_settings.get('mode') == 'embedded'):
            url = bookmark_web_url(row)
            if url:
                new_tab = getattr(root, 'remote_bookmark_new_tab', True)
                if root is not None:
                    root.close()
                if self.expanded_view.show_web_url(url, new_tab=new_tab):
                    return
                # WebEngine unavailable: preserve the existing activation
                # fallback (including the configured external-browser mode).
        if self.menu:self.menu.close()
        self.activate(row)

    def cascade(self,row,q=None,mode="keyboard"):
        self.hover_timer.stop();self.pending_menu_item=None
        if self.menu:self.menu.close();self.menu.deleteLater()
        self.menu=(AppCascadeMenu if row.get('launch_source')=='installed_apps' else CascadeMenu)(parent=self,launcher=self)
        self.menu.open_mode=mode;self.menu.owner_item=q or self.list.currentItem()
        self.menu.compact_files_cascade = (row.get('item_kind') == 'directory')
        self.fill_cascade(self.menu,row)
        # Experimental main-Page layout: start the first popup at the
        # title/description divider, overlapping the description column.
        # The saved main-column width controls this divider dynamically.
        # Search/selection modes keep their original viewport-right anchor;
        # nested cascades continue to open at their parent popup's right edge.
        viewport = self.list.viewport()
        rect = self.list.visualItemRect(q or self.list.currentItem())
        main_columns = self._column_mode == 'main' and self.selection is None
        divider = self.list.columnViewportPosition(1) if main_columns else None
        anchor_x = main_cascade_anchor_x(viewport.width(), divider, main_columns=main_columns)
        pos = viewport.mapToGlobal(QPoint(anchor_x, rect.top()))
        self.menu.popup(pos);self.menu.setFocus()

    def activate(self,row):
        if not row:return
        self.record_session_search()
        self._session_edit_draft = None
        # Global URL search hits open inside Launch's Browser, not Chrome.
        # Only a sole URL Open action qualifies; local files and scripts keep
        # their original launch behavior. External Web mode remains external.
        if self.open_search_url_in_browser(row):
            return
        file_path = row.get('_indexed_file') or row.get('_browse_file')
        if file_path:
            self.run_file_path(row, file_path)
            return
        if not self.selection and row.get('_search_selection_owner'):
            self._nav_before_change()
            # Enter/Space on a global-search hit joins its original selection
            # group. Keep the search text, so the selected person stays visible.
            owner_id = row['_search_selection_owner']
            owner = next((item for item in self.data['items']
                          if item['item_id'] == owner_id and item.get('enabled', True)), None)
            if owner is None:return
            # Snapshot global hits *before* rendering the recipient picker;
            # parent-folder terms can match every member of a contact group.
            self._global_selection_choice_ids = global_choice_ids_in_results(
                (self.list.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)
                 for i in range(self.list.topLevelItemCount())), owner_id)
            self.selection = owner
            self.checked = {row['choice_id']}
            self._global_selection_query = self.search.text().strip()
            self.render()
            self.list.setFocus()
            self._nav_after_change()
            return
        if self.selection:
            q=self.list.currentItem();q.setCheckState(0,Qt.CheckState.Unchecked if q.checkState(0)==Qt.CheckState.Checked else Qt.CheckState.Checked);return
        kind=row.get('item_kind')
        if kind=='category':
            self._nav_before_change()
            self.stack.append(row);self.search.clear();self.render();self.list.setFocus()
            self._nav_after_change()
            return
        if kind=='selection':
            self._nav_before_change()
            self.selection=row;self.checked.clear();self._global_selection_query=None;self._global_selection_choice_ids=None;self.search.clear();self.render();self.list.setFocus()
            self._nav_after_change()
            return
        self.execute(row)

    def open_search_url_in_browser(self, row):
        """Route a global-search URL hit to the embedded workspace safely."""
        if (not self.search.text().strip() or self.selection is not None or
                self.webview_settings.get('mode') != 'embedded' or
                row.get('_indexed_file') or row.get('_browse_file')):
            return False
        # Reuse the established URL resolver: it only accepts an Open URL.
        url = bookmark_web_url(row)
        if not url:
            return False
        # Clear the search to recover the Files/Browser workspace before
        # activating WebView. Never discard the search if Browser is absent.
        prior_query = self.search.text()
        if self.view_mode != 'expanded':
            self.set_view_mode('expanded')
        self.search.clear()
        if self.expanded_view.isVisible() and self.expanded_view.show_web_url(
                url, new_tab=getattr(self.expanded_view, 'bookmark_new_tab', True)):
            return True
        self.search.setText(prior_query)
        return False

    def confirm_selection(self):
        if not self.selection or not self.checked:return
        row=self.selection
        choices=sorted([c for c in self.data['launch_choices'] if c['choice_id'] in self.checked],key=lambda c:c.get('sort_order',0))
        value=join_selection_values(row, choices)
        self.execute(row,{row.get('launch_selection_result_name','recipients'):value})

    def activate_after_mouse_release(self, row, expected_foreground):
        """Launch only after the final UP of a mouse double-click is delivered.

        A Qt Tool window can be visible/on top without owning keyboard focus.
        Before spawning a GUI child, request foreground for the launcher only
        if the user has not switched to some other application in the meantime.
        The existing execute() method then grants foreground to the child.
        """
        if not self.isVisible() or self.busy:
            return
        if windows.IS_WINDOWS:
            hwnd = int(self.winId())
            before = windows.foreground()
            if before != hwnd:
                restored = windows.activate_keyboard_window(
                    hwnd, expected_foreground=expected_foreground)
                DIAG.info('MOUSE_LAUNCH_FOCUS before=%s expected=%s restored=%s after=%s',
                          before, expected_foreground, restored, windows.foreground())
        self.activate(row)

    def remember_search(self, value=None):
        """Only an explicit human action promotes a query to persistent history."""
        text = self.search.text() if value is None else value
        try:
            if self.search_history.remember(text):
                DIAG.info('SEARCH_HISTORY saved keyword=%s', normalize_keyword(text))
            self.session_history.remove(text)
            if self._session_edit_draft == normalize_keyword(text):
                self._session_edit_draft = None
            # Do not re-render/rebuild history while a Japanese IME is active.
        except OSError:
            DIAG.exception('SEARCH_HISTORY save failed')

    def search_user_edited(self, value):
        """textEdited precedes textChanged for real edits (including IME commits).

        Programmatic setText/clear stays synchronous to protect navigation and
        existing callers. Only actual typing is coalesced into one heavy search.
        """
        self._search_user_edit_pending = True
        if self._session_edit_draft is not None:
            # A pause during the *same edit* is not a new completed query.
            # Replace its volatile draft instead of accumulating substrings.
            self.session_history.remove(self._session_edit_draft)
            self._session_edit_draft = None

    def render_settled_search(self):
        """Never run SQLite or rebuild the list during Japanese IME preedit."""
        if getattr(self, 'composing', False):
            self._live_search_timer.start(235)
            return
        self.render()

    def flush_live_search(self):
        """Finish deferred results before the user navigates or clicks a hit."""
        if self._live_search_timer.isActive() and not getattr(self, 'composing', False):
            self._live_search_timer.stop()
            self.render()

    def record_session_search(self):
        """Collect settled queries with zero JSON I/O or history UI rebuilding."""
        if getattr(self, 'composing', False):
            return
        text = normalize_keyword(self.search.text())
        if not text or self.session_history.has(text):
            return
        if self.session_history.remember(text, self.search_history.keywords):
            self._session_edit_draft = text

    def search_text_changed(self, value):
        # Any actual edit (including an IME commit or paste) wins over history.
        # Qt's preedit remains untouched; no file I/O is performed on typing.
        if self.history_popup.isVisible():
            self.hide_history_popup()
        if '/' in value:
            cursor = self.search.cursorPosition()
            cleaned = value.replace('/', '')
            self.search.setText(cleaned)
            self.search.setCursorPosition(max(0, cursor - value[:max(0, cursor)].count('/')))
            return
        self._session_history_timer.stop()
        was_user_edit = self._search_user_edit_pending
        self._search_user_edit_pending = False
        # A clear or focus change completes the prior query without needing a
        # manual registration. The RAM-only record cannot pollute saved JSON.
        previous = self._last_search_value
        self._last_search_value = value
        if not value.strip() and previous.strip() and not getattr(self, 'composing', False):
            self.session_history.remember(previous, self.search_history.keywords)
            self._session_edit_draft = None
        visible = bool(value.strip())
        if self.save_history_button.isVisible() != visible:
            self.save_history_button.setVisible(bool(value.strip()))
            self.layout_search_inner_controls()
        self._live_search_timer.stop()
        if visible:
            self._session_history_timer.start()
        if was_user_edit and visible:
            # One search for a burst of keystrokes instead of rebuilding the
            # Qt list and synchronously querying SQLite on every IME commit.
            japanese = any(ord(ch) > 127 for ch in value)
            self._live_search_timer.start(235 if japanese else 135)
        else:
            # Programmatic selection, clear and navigation remain immediate.
            self.render()
        if not self._nav_restoring and not self._nav_transition:
            self._nav_search_timer.start()

    def position_history_popup(self):
        if not hasattr(self, 'history_popup'):
            return
        # The header magnifier can open the SAME history below itself. The
        # main search field and Remote retain their original popup anchor.
        source = getattr(self, '_history_popup_anchor', None)
        if source is not None and source.isVisible():
            anchor = source.mapTo(self, QPoint(0, source.height() + 4))
            x, y = anchor.x(), anchor.y()
            width = min(max(330, self.search.width()), max(1, self.width() - x - 12))
        else:
            anchor = self.search.mapTo(self, QPoint(0, self.search.height() + 4))
            x, y = anchor.x(), anchor.y()
            width = self.search.width()
        # In 1.5-column Files mode, keep the history clear of the floating
        # Remote: anchor its LEFT EDGE to the Files List column, not the
        # magnifier, search edit, breadcrumb, or Remote window.
        files_view = getattr(self, 'expanded_view', None)
        if (getattr(self, 'remote_15_mode', False) and files_view is not None
                and files_view.isVisible()
                and getattr(files_view, '_workspace_mode', '') == 'files'):
            list_title = getattr(files_view, 'files_list_title_box', None)
            if list_title is not None and list_title.isVisible():
                x = list_title.mapTo(self, QPoint(0, 0)).x()
                width = min(width, max(1, self.width() - x - 12))
        footer_top = self.footer.mapTo(self, QPoint(0, 0)).y()
        available = popup_available_height(self.height(), y, footer_top)
        # 31px CSS row + vertical padding; header buttons and frame margins.
        # Open/closed categories have different visible row counts.
        height = popup_tree_height(self.history_choices, self.history_visible_rows(),
                                   minimum_row_height=35, chrome_height=48 + 33,
                                   available_height=available)
        self.history_popup.setGeometry(x, y, width, height)

    def populate_history_popup(self, selected=None):
        """Folders are visual containers; original keyword text stays intact."""
        self.search_categories.sync(self.search_history.keywords)
        tree = self.history_choices
        tree.blockSignals(True)
        tree.clear()
        # Keep the temporary header visible even at 0 entries: inserting it
        # later would shift every saved category and break spatial memory.
        categories = [(SESSION_HISTORY, '一時履歴（終了時に消去）'), (UNCATEGORIZED, '未分類')] + [
            (category['id'], category['name']) for category in self.search_categories.categories]
        first_keyword = None
        selected_row = None
        for category_id, label in categories:
            is_session = category_id == SESSION_HISTORY
            words = (list(self.session_history.keywords) if is_session else
                     self.search_categories.group_items(category_id))
            expanded = self.session_history_expanded if is_session else self.search_categories.expanded(category_id)
            marker = '▾' if expanded else '▸'
            folder = QTreeWidgetItem([f'{marker}  {label}  ({len(words)})', '⋯' if category_id != UNCATEGORIZED else ''])
            folder.setData(0, ROLE_KIND, 'category')
            folder.setData(0, ROLE_ID, category_id)
            folder.setIcon(0, self.history_clock_icon if is_session else icon('category'))
            folder.setToolTip(0, '一時履歴：Launch終了で消去／ドラッグしてカテゴリーへ保存' if is_session else
                              'クリックで開閉／ドラッグでカテゴリー並び替え' if category_id != UNCATEGORIZED
                              else '未分類（削除・移動不可）／クリックで開閉')
            folder.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
            font = folder.font(0); font.setBold(True); folder.setFont(0, font)
            folder.setForeground(0, QBrush(QColor('#547b69' if theme_family(self.color_theme) == 'light' else '#bad5c6')))
            if category_id in (UNCATEGORIZED, SESSION_HISTORY):
                folder.setFlags(folder.flags() & ~Qt.ItemFlag.ItemIsDragEnabled)
            tree.addTopLevelItem(folder)
            for keyword in words:
                row = QTreeWidgetItem([keyword, '×'])
                row.setData(0, ROLE_KIND, 'keyword')
                row.setData(0, ROLE_ID, category_id)
                row.setIcon(0, self.history_clock_icon)
                row.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
                row.setToolTip(0, keyword + '  — クリックで検索／ドラッグで移動・並び替え')
                row.setToolTip(1, '履歴を削除')
                row.setFlags(row.flags() & ~Qt.ItemFlag.ItemIsDropEnabled)
                folder.addChild(row)
                if first_keyword is None and expanded:
                    first_keyword = row
                if keyword == selected:
                    selected_row = row
            folder.setExpanded(expanded)
        if selected_row is not None:
            # Selected rows in collapsed folders would otherwise be invisible.
            if selected_row.parent() is not None and selected_row.parent().isExpanded():
                tree.setCurrentItem(selected_row)
            else:
                tree.setCurrentItem(selected_row.parent())
        elif first_keyword is not None:
            tree.setCurrentItem(first_keyword)
        elif tree.topLevelItemCount():
            tree.setCurrentItem(tree.topLevelItem(0))
        tree.blockSignals(False)
        # A category move/delete recreates items; reapply only visual filters.
        self.filter_history_popup()
        if self.history_popup.isVisible():
            self.position_history_popup()

    def filter_history_popup(self, _value=None):
        """Filter currently displayed history without touching saved positions.

        Closed folders temporarily expand on matches. The original expanded
        flags are restored when the local query is cleared; signals stay
        blocked so searching never writes category JSON.
        """
        tree = self.history_choices
        query = self.history_filter.text().strip()
        filtering = bool(query)
        tree.blockSignals(True)
        try:
            first_match = None
            for index in range(tree.topLevelItemCount()):
                folder = tree.topLevelItem(index)
                category_id = folder.data(0, ROLE_ID)
                if category_id == SESSION_HISTORY:
                    label = '一時履歴（終了時に消去）'
                    was_expanded = self.session_history_expanded
                else:
                    group = self.search_categories.get(category_id)
                    label = group['name'] if group is not None else '未分類'
                    was_expanded = self.search_categories.expanded(category_id)
                category_match = filtering and matches_history_filter(label, query)
                count = 0
                for j in range(folder.childCount()):
                    row = folder.child(j)
                    match = not filtering or category_match or matches_history_filter(row.text(0), query)
                    row.setHidden(not match)
                    if match:
                        count += 1
                        if first_match is None and filtering:
                            first_match = row
                folder.setHidden(filtering and not category_match and count == 0)
                folder.setExpanded((category_match or count > 0) if filtering else was_expanded)
                # Retain real counts and original category ordering while filtering.
                folder.setText(0, f'{"▾" if folder.isExpanded() else "▸"}  {label}  ({folder.childCount()})')
            if filtering and first_match is not None:
                tree.setCurrentItem(first_match)
                tree.scrollToItem(first_match, QAbstractItemView.ScrollHint.EnsureVisible)
            elif filtering:
                tree.setCurrentItem(None)
            # When filtered, visible row indices differ from the stored order.
            # Do not allow drag/drop to silently reorder unseen entries.
            tree.setDragEnabled(not filtering)
            tree.setAcceptDrops(not filtering)
            tree.viewport().setAcceptDrops(not filtering)
        finally:
            tree.blockSignals(False)
        if self.history_popup.isVisible():
            self.position_history_popup()

    def history_visible_rows(self):
        """Flatten only visible folders/entries for wheel and keyboard."""
        tree = self.history_choices
        visible = []
        for index in range(tree.topLevelItemCount()):
            folder = tree.topLevelItem(index)
            if folder.isHidden():
                continue
            visible.append(folder)
            if folder.isExpanded():
                visible.extend(folder.child(j) for j in range(folder.childCount()))
        return [row for row in visible if not row.isHidden()]

    def add_history_category(self, checked=False):
        name, accepted = QInputDialog.getText(self, '検索履歴カテゴリー', 'カテゴリー名を入力:')
        if not accepted:
            return
        try:
            identifier = self.search_categories.create(name)
            if identifier is None:
                QMessageBox.information(self, 'カテゴリー', '名前が空、重複、または長すぎます。')
                return
            self.show_history_popup()
            folder = self.history_category_row(identifier)
            if folder is not None:
                self.history_choices.setCurrentItem(folder)
                self.history_choices.scrollToItem(folder)
        except OSError:
            DIAG.exception('SEARCH_HISTORY create category failed')
            QMessageBox.warning(self, 'カテゴリー', 'カテゴリーを保存できませんでした。')

    def history_category_row(self, category_id):
        for i in range(self.history_choices.topLevelItemCount()):
            row = self.history_choices.topLevelItem(i)
            if row.data(0, ROLE_ID) == category_id:
                return row
        return None

    def set_all_history_categories(self, expanded):
        try:
            self.session_history_expanded = bool(expanded)
            self.search_categories.expand_all(expanded)
            self.populate_history_popup()
            self.history_choices.setFocus(Qt.FocusReason.ShortcutFocusReason)
        except OSError:
            DIAG.exception('SEARCH_HISTORY expand all failed')

    def update_history_folder_marker(self, item):
        category_id = item.data(0, ROLE_ID)
        group = self.search_categories.get(category_id)
        name = ('一時履歴（終了時に消去）' if category_id == SESSION_HISTORY else
                group['name'] if group is not None else '未分類')
        item.setText(0, f'{"▾" if item.isExpanded() else "▸"}  {name}  ({item.childCount()})')

    def history_category_expanded(self, item):
        if item.data(0, ROLE_KIND) == 'category':
            self.update_history_folder_marker(item)
            if self.history_filter.text().strip():
                self.position_history_popup()
                return
            try:
                if item.data(0, ROLE_ID) == SESSION_HISTORY:
                    self.session_history_expanded = True
                else:
                    self.search_categories.set_expanded(item.data(0, ROLE_ID), True)
            except OSError:
                DIAG.exception('SEARCH_HISTORY expand failed')
            if self.history_popup.isVisible():
                self.position_history_popup()

    def history_category_collapsed(self, item):
        if item.data(0, ROLE_KIND) == 'category':
            self.update_history_folder_marker(item)
            if self.history_filter.text().strip():
                self.position_history_popup()
                return
            try:
                if item.data(0, ROLE_ID) == SESSION_HISTORY:
                    self.session_history_expanded = False
                else:
                    self.search_categories.set_expanded(item.data(0, ROLE_ID), False)
            except OSError:
                DIAG.exception('SEARCH_HISTORY collapse failed')
            if self.history_popup.isVisible():
                self.position_history_popup()

    def history_category_context_menu(self, point=None, item=None):
        tree = self.history_choices
        item = item or (tree.itemAt(point) if point is not None else tree.currentItem())
        if item is None or item.data(0, ROLE_KIND) != 'category':
            return
        identifier = item.data(0, ROLE_ID)
        if identifier in (UNCATEGORIZED, SESSION_HISTORY):
            return
        group = self.search_categories.get(identifier)
        if group is None:
            return
        menu = QMenu(tree)
        rename_action = menu.addAction('カテゴリー名を変更...')
        delete_action = menu.addAction('カテゴリーを削除（履歴は未分類へ）...')
        pos = tree.viewport().mapToGlobal(point) if point is not None else tree.viewport().mapToGlobal(tree.visualItemRect(item).center())
        chosen = menu.exec(pos)
        try:
            if chosen == rename_action:
                name, accepted = QInputDialog.getText(self, 'カテゴリー名変更', '新しい名前:', text=group['name'])
                if accepted and name.strip() and not self.search_categories.rename(identifier, name):
                    QMessageBox.information(self, 'カテゴリー', '同じ名前のカテゴリーがあるか、変更できない名前です。')
                elif accepted:
                    self.populate_history_popup()
            elif chosen == delete_action:
                answer = QMessageBox.question(self, 'カテゴリー削除',
                    f'「{group["name"]}」を削除しますか？\n中の検索履歴は未分類へ移動します。',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No)
                if answer == QMessageBox.StandardButton.Yes:
                    self.search_categories.delete(identifier)
                    self.populate_history_popup()
        except OSError:
            DIAG.exception('SEARCH_HISTORY category edit failed')
        if chosen is not None and not self.history_popup.isVisible():
            self.show_history_popup()

    def history_structure_changed(self, kind, value, destination, index):
        try:
            if kind == 'category':
                self.search_categories.move_category(value, index)
            elif kind == 'keyword':
                if self.session_history.has(value):
                    # Dragging a volatile entry is an explicit save decision.
                    if destination == SESSION_HISTORY:
                        return  # Session entries keep their insertion positions.
                    if self.search_history.remember(value):
                        self.search_categories.sync(self.search_history.keywords)
                    if value in self.search_history.keywords:
                        # A no-op move (e.g. saved at 未分類 position 0) is
                        # still a successful promotion, not a duplicate.
                        self.search_categories.move_keyword(value, destination, index)
                        self.session_history.remove(value)
                        self._session_edit_draft = None
                elif destination != SESSION_HISTORY:
                    self.search_categories.move_keyword(value, destination, index)
            self.populate_history_popup(value if kind == 'keyword' else None)
            if kind == 'category':
                row = self.history_category_row(value)
                if row is not None:
                    self.history_choices.setCurrentItem(row)
        except OSError:
            DIAG.exception('SEARCH_HISTORY category drag failed')
            self.populate_history_popup()

    def show_history_popup(self, *, anchor=None):
        if not self.isVisible():
            return
        self._history_popup_anchor = anchor
        if self.menu:
            self.menu.close()
        self.hover_timer.stop(); self.pending_menu_item = None
        self.expanded_view.hide_favorite_popup()
        self.populate_history_popup()
        self.position_history_popup()
        self.history_popup.show()
        self.history_popup.raise_()
        # Showing a non-modal history overlay must NOT steal focus/IME input.
        # The user explicitly clicks the small local filter to edit it.
        self.search.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def hide_history_popup(self, focus_search=False):
        if not hasattr(self, 'history_popup'):
            return
        was_visible = self.history_popup.isVisible()
        self.history_popup.hide()
        self._history_popup_anchor = None
        # Start each invocation with the full history; local filter is not a
        # global search and must not silently hide entries on next open.
        if self.history_filter.text():
            self.history_filter.clear()
        self._search_history_wheel_delta = 0
        self._search_history_warp_generation += 1
        if was_visible and focus_search and self.isVisible():
            self.search.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def toggle_history_popup(self):
        if self.history_popup.isVisible():
            self.hide_history_popup(focus_search=True)
        else:
            self.show_history_popup()

    def select_history_keyword(self):
        row = self.history_choices.currentItem()
        if row is None or not (self.search_history.keywords or self.session_history.keywords):
            return
        if row.data(0, ROLE_KIND) == 'category':
            row.setExpanded(not row.isExpanded())
            return
        keyword = row.text(0)
        if keyword not in self.search_history.keywords and not self.session_history.has(keyword):
            return
        self.hide_history_popup()
        self.search.setText(keyword)  # Existing live textChanged search is the only search path.
        self.search.setCursorPosition(len(keyword))
        if self.list.topLevelItemCount():
            self.list.setCurrentItem(self.list.topLevelItem(0))
        self.list.setFocus(Qt.FocusReason.ShortcutFocusReason)
        DIAG.info('SEARCH_HISTORY selected keyword=%s', keyword)

    def change_history_row(self, value, action):
        try:
            if action == 'delete':
                if self.session_history.has(value):
                    self.session_history.remove(value)
                    if self._session_edit_draft == value:
                        self._session_edit_draft = None
                    selected = None
                else:
                    index = self.search_history.keywords.index(value)
                    if not self.search_history.remove(value):
                        return
                    self.search_categories.sync(self.search_history.keywords)
                    remaining = self.search_history.keywords
                    selected = remaining[min(index, len(remaining)-1)] if remaining else None
            else:
                return
            self.populate_history_popup(selected)
            self.history_choices.setFocus(Qt.FocusReason.ShortcutFocusReason)
        except (OSError, ValueError):
            DIAG.exception('SEARCH_HISTORY update failed')

    def history_reordered(self, order):
        try:
            if not self.search_history.reorder(order):
                self.populate_history_popup()
        except OSError:
            DIAG.exception('SEARCH_HISTORY drag reorder failed')
            self.populate_history_popup()

    def history_row_clicked(self, item, column):
        if item.data(0, ROLE_KIND) == 'category':
            if column == 0:
                item.setExpanded(not item.isExpanded())
            elif column == 1:
                self.history_category_context_menu(item=item)
            return
        if not (self.search_history.keywords or self.session_history.keywords):
            return
        value = item.text(0)
        if column == 0:
            self.history_choices.setCurrentItem(item)
            self.select_history_keyword()
        elif column == 1:
            self.change_history_row(value, 'delete')

    def wheel_search_history(self, obj, event):
        """Wheel on search input opens history, then moves rows and pointer.

        Moving over a history entry never runs the search; only a click/Enter
        commits it. The delete column remains outside the pointer target.
        """
        if (obj not in (self.search, self.history_choices,
                        self.history_choices.viewport()) or
                event.modifiers() != Qt.KeyboardModifier.NoModifier or
                QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return False
        if not self.history_popup.isVisible():
            if obj is not self.search or not (self.search_history.keywords or self.session_history.keywords):
                return False
            self.show_history_popup()
        pending, steps = wheel_steps(self._search_history_wheel_delta,
                                     event.angleDelta().y(), event.pixelDelta().y())
        self._search_history_wheel_delta = pending
        if not steps:
            return True
        tree = self.history_choices
        visible = self.history_visible_rows()
        count = len(visible)
        if count == 0:
            return True
        current = visible.index(tree.currentItem()) if tree.currentItem() in visible else -1
        target = visible[history_target_index(current, count, steps)]
        tree.setCurrentItem(target)
        tree.scrollToItem(target, QAbstractItemView.ScrollHint.EnsureVisible)
        origin = QCursor.pos()
        self._search_history_warp_generation += 1
        generation = self._search_history_warp_generation
        QTimer.singleShot(0, lambda: (
            warp_to_history_row(tree, target, origin, QCursor)
            if (self.pointer_warp_enabled and
                generation == self._search_history_warp_generation) else None))
        return True

    def handle_history_input_method(self, obj, event):
        """Close history on the FIRST Japanese IME preedit, before commit.

        The history tree owns focus for Up/Down/Enter, but it must not swallow
        composition events intended as a new main-search query. Preserve the
        actual Qt input-method event instead of converting it to key presses.
        """
        if (event.type() != QEvent.Type.InputMethod or
                not self.history_popup.isVisible() or
                obj not in (self.search, self.history_choices,
                            self.history_choices.viewport()) or
                not (event.preeditString() or event.commitString())):
            return False
        from_history_list = obj is not self.search
        self.hide_history_popup()
        if from_history_list:
            # FocusIn normally schedules halfwidth-English initialization.
            # During a Japanese composition that delayed reset must be skipped.
            self._history_ime_handoff = True
            self.search.setFocus(Qt.FocusReason.OtherFocusReason)
            QApplication.sendEvent(self.search, event)
            event.accept()
            return True
        # Let QLineEdit process its native InputMethod event normally.
        return False

    def handle_history_event(self, obj, event):
        # Keep popup key handling ahead of the launcher's Enter/Right handlers:
        # the first Enter must search, the NEXT Enter may activate a result.
        popup_input = obj in (self.history_choices, self.history_choices.viewport())
        local_filter_input = obj is getattr(self, 'history_filter', None)
        if event.type() == QEvent.Type.MouseButtonPress and obj in (
                self.list.viewport(), self.tabs) and self.history_popup.isVisible():
            self.hide_history_popup()
            return False
        if event.type() != QEvent.Type.KeyPress:
            return False
        key = event.key()
        modifiers = event.modifiers()
        # The launcher owns F3 even when focus is in its history filter or
        # a Files/Bookmarks panel. Do not change the query or search history.
        if key == getattr(Qt.Key, 'Key_F3', None) and modifiers == Qt.KeyboardModifier.NoModifier:
            self.focus_search()
            event.accept()
            return True
        if getattr(self, 'composing', False):
            return False
        if local_filter_input and self.history_popup.isVisible():
            if key == Qt.Key.Key_Escape:
                if self.history_filter.text():
                    self.history_filter.clear()
                else:
                    self.search.setFocus(Qt.FocusReason.ShortcutFocusReason)
                event.accept()
                return True
            if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                visible = [row for row in self.history_visible_rows()
                           if row.data(0, ROLE_KIND) == 'keyword']
                if visible:
                    current = self.history_choices.currentItem()
                    target = next_wrapped(visible, current,
                                          -1 if key == Qt.Key.Key_Up else 1)
                    self.history_choices.setCurrentItem(target)
                    self.history_choices.scrollToItem(target)
                event.accept()
                return True
            return False  # Native QLineEdit editing and IME preedit.
        if (obj in (self.search, self.list, self.tabs) or popup_input) and (
                event.text() == '/' or (key == Qt.Key.Key_Slash and not event.text())) and modifiers in (
                    Qt.KeyboardModifier.NoModifier, Qt.KeyboardModifier.ShiftModifier):
            self.toggle_history_popup()
            event.accept()
            return True
        if obj is self.search and self.history_popup.isVisible() and modifiers == Qt.KeyboardModifier.NoModifier:
            if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                visible = self.history_visible_rows()
                if visible:
                    row = next_wrapped(visible, self.history_choices.currentItem(),
                                       -1 if key == Qt.Key.Key_Up else 1)
                    self.history_choices.setCurrentItem(row)
                    self.history_choices.scrollToItem(row)
                event.accept()
                return True
            if key == Qt.Key.Key_Escape:
                self.hide_history_popup(focus_search=True)
                event.accept()
                return True
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.select_history_keyword()
                event.accept()
                return True
        if not popup_input or not self.history_popup.isVisible():
            return False
        if key == Qt.Key.Key_Escape:
            self.hide_history_popup(focus_search=True)
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Right, Qt.Key.Key_Tab):
            self.select_history_keyword()
        elif key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            visible = self.history_visible_rows()
            if visible:
                offset = -1 if key == Qt.Key.Key_Up else 1
                row = self.history_choices.currentItem()
                next_row = next_wrapped(visible, row, offset)
                self.history_choices.setCurrentItem(next_row)
                self.history_choices.scrollToItem(next_row)
        elif key == Qt.Key.Key_Left:
            row = self.history_choices.currentItem()
            if row is not None:
                if row.data(0, ROLE_KIND) == 'category':
                    row.setExpanded(False)
                elif row.parent() is not None:
                    self.history_choices.setCurrentItem(row.parent())
        elif key == Qt.Key.Key_Delete:
            row = self.history_choices.currentItem()
            if row is not None and row.data(0, ROLE_KIND) == 'keyword':
                self.change_history_row(row.text(0), 'delete')
        elif key == Qt.Key.Key_Backspace:
            self.hide_history_popup()
            self.search.setFocus()
            self.search.backspace()
        else:
            # No typing into the history list; return to searching on a normal key.
            if event.text() and not (modifiers & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier)):
                self.hide_history_popup()
                self.search.setFocus()
                QApplication.sendEvent(self.search, QKeyEvent(event.type(), key, modifiers, event.text()))
            else:
                return False
        event.accept()
        return True

    def in_root_page_navigation(self):
        """Only the unfiltered Page root includes its tab in Up/Down travel."""
        return (not self.search.text().strip() and not self.stack
                and self.selection is None)

    def move_root_page_selection(self, direction, *, from_tab=False):
        """Page tab -> rows -> Page tab, without changing the selected Page."""
        selectable = [self.list.topLevelItem(i)
                      for i in range(self.list.topLevelItemCount())
                      if not self.list.topLevelItem(i).isHidden()
                      and not self.list.topLevelItem(i).isDisabled()]
        destination, row = next_page_ring_target(
            selectable, self.list.currentItem(), direction, on_tab=from_tab)
        if destination == 'tab':
            self.tabs.setFocus(Qt.FocusReason.TabFocusReason)
        else:
            self.list.setCurrentItem(row)
            self.list.scrollToItem(row)
            self.list.setFocus(Qt.FocusReason.TabFocusReason)

    def visible_cascade_for_keyboard(self):
        """Deepest open column, used when a Qt.Tool menu did not gain focus.

        Tool windows intentionally do not grab the mouse, but on Windows they
        may leave keyboard focus on the main QTreeWidget.  Route those keys to
        the visible cascade rather than executing the main-window selection.
        """
        menu = getattr(self, 'menu', None)
        if menu is None or not menu.isVisible():
            return None
        while menu.child is not None and menu.child.isVisible():
            menu = menu.child
        return menu

    def close_cascade_for_main_interaction(self):
        """ESC-equivalent dismissal, without fabricating key or mouse events.

        With tool-window cascade columns, the launcher receives the original
        press even if a column is open; no global hit-test or event replay is
        needed. Closing here lets the *same* right-click open Properties.
        """
        self.hover_timer.stop()
        self.pending_menu_item = None
        if self.menu is not None and self.menu.isVisible():
            # Prevent a pending delete-dialog refresh from reopening a column
            # that was intentionally dismissed by an outside click.
            self._cascade_dismiss_generation = getattr(self, '_cascade_dismiss_generation', 0) + 1
            self.menu.close()  # CascadeMenu.hideEvent also closes all children.

    def page_empty_area_can_open_context(self, viewport_pos):
        """Only the region strictly BELOW the last visible main Page row.

        Empty cells, reorder rows, tab/search/footer and blank space beside a
        row are NOT the page background.  Context on an actual row is handled
        independently from this guard.
        """
        if self.selection or self.stack or self.search.text().strip():
            return False
        if self.list.itemAt(viewport_pos) is not None:
            return False
        for i in range(self.list.topLevelItemCount() - 1, -1, -1):
            item = self.list.topLevelItem(i)
            if not item.isHidden():
                rect = self.list.visualItemRect(item)
                return rect.isValid() and viewport_pos.y() > rect.bottom()
        return True   # An empty Page has no last row.

    def expanded_focus_area(self, obj):
        """Identify the active keyboard region, never the hidden classic tree."""
        if not self.expanded_view.isVisible():
            return None
        if obj is self.search:
            return 'search'
        if obj is self.tabs:
            return 'pages'
        if obj is self.expanded_view.files_mode_tab:
            return 'workspace_files'
        if obj is self.expanded_view.browser_mode_tab:
            return 'workspace_browser'
        if obj in (self.expanded_view.address_bar.editor, self.expanded_view.address_bar):
            return 'breadcrumb'
        web = getattr(self.expanded_view, 'web_view', None)
        if web is not None and getattr(self.expanded_view, 'web_view_active', lambda: False)():
            if obj is web.tabs.tabBar():
                return self._current_web_body_area()
            for i in range(web.tabs.count()):
                widget = web.tabs.widget(i)
                # The embedded webpage owns Tab inside HTML inputs/forms.
                # Avoid treating WebEngine's child widgets as Launcher controls.
                if obj is widget:
                    return f'web_body:{i}'
        if obj in self.expanded_view.root_buttons:
            return 'roots'
        for name, pane in (('files', self.expanded_view.left),
                           ('directory', self.expanded_view.middle),
                           ('bookmarks', self.expanded_view.right)):
            if obj is pane.tree or obj is pane.tree.viewport():
                return name
        return None

    def expanded_focus_key(self, obj, event):
        """Tab switches areas; arrows are deliberately NOT area traversal."""
        area = self.expanded_focus_area(obj)
        if area is None:
            return False
        if event.key() not in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
            return False
        if area == 'search' and (getattr(self, 'composing', False) or
                                 (getattr(self, 'history_popup', None) is not None
                                  and self.history_popup.isVisible())):
            return False  # IME/history candidate keys belong to the search UI.
        mods = event.modifiers()
        if mods not in (Qt.KeyboardModifier.NoModifier,
                        Qt.KeyboardModifier.ShiftModifier):
            return False
        backward = (event.key() == Qt.Key.Key_Backtab or
                    bool(mods & Qt.KeyboardModifier.ShiftModifier))
        view = self.expanded_view
        web_active = getattr(view, 'web_view_active', lambda: False)()
        order = navigation_order(expanded=True, web=(view._workspace_mode == 'browser'),
                                 web_tab_count=self._web_tab_count(),
                                 bookmarks_visible=view.browser_bookmarks_visible)
        area = normalize_area(area, order, current_tab=(
            view.web_view.tabs.currentIndex() if web_active else 0))
        target = tab_target(area, backward=backward, order=order)
        if self.files_root_hidden_mode:
            hidden_areas = {'files', 'bookmarks'}
            for _ in range(len(order)):
                if target not in hidden_areas:
                    break
                target = tab_target(target, backward=backward, order=order)
        if target == 'search':
            self.search.setFocus(Qt.FocusReason.TabFocusReason)
        elif target == 'pages':
            self.tabs.setFocus(Qt.FocusReason.TabFocusReason)
        elif target == 'workspace_files':
            view.files_mode_tab.setFocus(Qt.FocusReason.TabFocusReason)
        elif target == 'workspace_browser':
            view.browser_mode_tab.setFocus(Qt.FocusReason.TabFocusReason)
        elif target == 'roots':
            view.focus_root()
        elif target == 'breadcrumb':
            view.address_bar.begin_edit()
        elif target == 'files':
            view.focus_panel(view.left)
        elif target == 'directory':
            view.focus_panel(view.middle)
        elif str(target).startswith('web_body:') and web_active:
            view.web_view.tabs.setCurrentIndex(int(target.split(':', 1)[1]))
            view.web_view.focus_page()
        elif target == 'bookmarks':
            self._focus_bookmark_first()
        event.accept()
        return True

    def execute_expanded_root_shortcut(self, index):
        """Dispatch by *current displayed order*, not hardcoded item names."""
        view = self.expanded_view
        if (not view.isVisible() or not 0 <= index < len(view.root_rows)
                or index >= len(view.root_buttons)):
            return
        button = view.root_buttons[index]
        if button.isVisible():
            view.toolbar_scroller.ensureWidgetVisible(button)
        view.root_action(view.root_rows[index], button)

    def expanded_root_key(self, button, event):
        """First-level horizontal button strip: Left/Right select, Down enters."""
        if not self.expanded_view.isVisible() or button not in self.expanded_view.root_buttons:
            return False
        if self.page_key(event):
            event.accept()
            return True
        key = event.key()
        if event.modifiers() != Qt.KeyboardModifier.NoModifier:
            return False
        view = self.expanded_view
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            index = view.root_buttons.index(button)
            target = root_step(index, -1 if key == Qt.Key.Key_Left else 1,
                               len(view.root_buttons))
            view.focus_root(index=target)
        elif key == Qt.Key.Key_Up:
            self.tabs.setFocus(Qt.FocusReason.TabFocusReason)
        elif key == Qt.Key.Key_Down:
            row = view.root_rows[view.root_buttons.index(button)]
            if row.get('item_id') == view.files_root.get('item_id'):
                view.focus_panel(view.middle if self.files_root_hidden_mode else view.left)
            elif row.get('item_id') == view.bookmarks_root.get('item_id'):
                if self.files_root_hidden_mode:
                    self.remote_focus_area(self._current_web_body_area())
                else:
                    view.focus_panel(view.right)
            elif row.get('item_kind') in ('category', 'directory'):
                view.open_cascade(row, button)
            else:
                # Down means "choose" in the first-level strip, including
                # leaf commands such as Settings (same action as Enter).
                view.root_action(row, button)
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            row = view.root_rows[view.root_buttons.index(button)]
            view.root_action(row, button)
        elif key == Qt.Key.Key_Escape:
            if self.menu and self.menu.isVisible():
                self.menu.close()
            else:
                self.dismiss()
        else:
            return False
        event.accept()
        return True

    def expanded_tab_key(self, event):
        """Page Left/Right retains its original meaning; Down enters roots."""
        if not self.expanded_view.isVisible():
            return False
        if self.page_key(event):
            event.accept()
            return True
        if event.modifiers() != Qt.KeyboardModifier.NoModifier:
            return False
        if event.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up):
            self.expanded_view.focus_root(index=(0 if event.key() == Qt.Key.Key_Down else
                                                len(self.expanded_view.root_buttons) - 1))
            event.accept()
            return True
        return False

    def expanded_tree_key(self, tree, event):
        if not self.expanded_view.isVisible():
            return False
        pane = next((p for p in (self.expanded_view.left, self.expanded_view.middle,
                                  self.expanded_view.right)
                     if p.tree is tree or p.tree.viewport() is tree), None)
        if pane is None:
            return False
        # A filename QLineEdit owns Enter while editing. Do not dispatch
        # that same key through the normal expanded Files activation route.
        if (pane is self.expanded_view.middle and
                (getattr(pane.tree, '_rename_enter_guard', False) or
                 (hasattr(pane.tree, 'state') and
                  pane.tree.state() == QAbstractItemView.State.EditingState))):
            return False
        if self.page_key(event):
            event.accept()
            return True
        key = event.key()
        if (event.modifiers() & Qt.KeyboardModifier.ControlModifier
                and key == Qt.Key.Key_F):
            self.focus_search()
            event.accept()
            return True
        if (pane is self.expanded_view.middle
                and event.modifiers() == Qt.KeyboardModifier.ControlModifier):
            if key in (Qt.Key.Key_C, Qt.Key.Key_X):
                self.copy_expanded_selected_paths(cut=(key == Qt.Key.Key_X))
                event.accept()
                return True
            if key == Qt.Key.Key_V:
                self.paste_into_expanded_directory()
                event.accept()
                return True
        # Conventional forward shortcut; Right alone still enters a folder.
        if (pane in (self.expanded_view.left, self.expanded_view.middle) and
                event.modifiers() == Qt.KeyboardModifier.AltModifier and
                key == Qt.Key.Key_Right):
            self.expanded_view.history_forward()
            event.accept()
            return True
        if event.modifiers() != Qt.KeyboardModifier.NoModifier:
            return False
        view = self.expanded_view
        if key == getattr(Qt.Key, 'Key_Delete', None) and pane is view.middle:
            self.delete_expanded_selected_paths()
            event.accept()
            return True
        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            selected = move_tree_selection(pane.tree, -1 if key == Qt.Key.Key_Up else 1)
            if selected is not None and pane is view.left:
                # Preview follows Files selection, but keyboard focus stays left.
                view.choose_files(selected, 0)
        elif key == Qt.Key.Key_Escape:
            if self.menu and self.menu.isVisible():
                self.menu.close()
            else:
                self.dismiss()
        elif key == Qt.Key.Key_Left:
            if pane is view.middle:
                target = view.navigate_left_from_middle()
                # The Remote can remain open while the user uses the real
                # keyboard. Keep its independent routing target in sync.
                remote = getattr(self, 'remote_window', None)
                if remote is not None and remote.isVisible():
                    self._remote_area = target
                    remote.set_area(target)
            elif pane is view.right:
                # Bookmarks' adjacent column is Files' active directory.
                view.focus_panel(view.middle)
            # Files first column is already the leftmost folder column.
            # The top-left Back button alone navigates visit history.
        elif key == Qt.Key.Key_Right:
            item = pane.tree.currentItem()
            if item is not None:
                row = view.row_data(item)
                is_folder = row.get('item_kind') in ('category', 'directory')
                name = ('files' if pane is view.left else
                        'directory' if pane is view.middle else 'bookmarks')
                action = row_right_action(name, is_folder)
                if action == 'enter_directory_panel':
                    view.choose_files(item, 0)
                    view.focus_panel(view.middle)
                elif action == 'descend':
                    view.navigate_middle(row)
                elif action == 'cascade':
                    view.open_cascade(row, pane.tree, item)
                else:
                    view.launcher.activate(row)
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            item = pane.tree.currentItem()
            if item is not None:
                view.enter_row(pane, item)
        else:
            # Keep ordinary Qt shortcuts/text editing out of classic hidden grid.
            return False
        event.accept()
        return True

    def wheel_classic_menu(self, event, scroll_before=None, scroll_after=None):
        """Compact WAN: native Target Flow first, Cursor Follow at the edge.

        ReorderTree.wheelEvent supplies the actual before/after scrollbar
        values. The optional no-scroll arguments preserve the legacy menu
        selection entry point for existing callers/tests.
        """
        if (self.view_mode not in ('classic', 'expanded') or not self.list.isVisible()
                or (self.view_mode == 'expanded' and
                    (getattr(self, 'expanded_view', None) is None or
                     self.expanded_view.isVisible()))
                or event.modifiers() != Qt.KeyboardModifier.NoModifier):
            return False
        angle = event.angleDelta().y()
        pixels = event.pixelDelta().y()
        if not angle and not pixels:
            return False
        tree = self.list
        items = [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())
                 if not tree.topLevelItem(i).isHidden()
                 and not tree.topLevelItem(i).isDisabled()]
        if not items:
            return True
        native_scroll = scroll_before is not None and scroll_after is not None
        if (native_scroll and QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return False  # Never change the selection mid-drag.
        viewport = tree.viewport() if native_scroll else None
        pointer = QCursor.pos() if native_scroll else None
        local = viewport.mapFromGlobal(pointer) if native_scroll else None
        under_pointer = (tree.itemAt(local) if native_scroll
                         and viewport.rect().contains(local) else None)

        if native_scroll and scroll_before != scroll_after:
            # Existing native scroll keeps the pointer stationary while rows
            # move beneath it. Select the actual item now beneath the pointer.
            self._classic_wheel_edge_active = False
            self._classic_wheel_remainder = 0
            if under_pointer in items and under_pointer is not tree.currentItem():
                self.hover_timer.stop()
                self.pending_menu_item = None
                tree.setCurrentItem(under_pointer)
            if under_pointer in items:
                if hasattr(tree, 'set_wheel_current_visual'):
                    tree.set_wheel_current_visual(True)
                row = under_pointer.data(0, Qt.ItemDataRole.UserRole)
                if isinstance(row, dict) and row.get('item_kind') in ('category', 'directory'):
                    # Debounce previews while rows stream under the pointer.
                    self.pending_menu_item = under_pointer
                    self.hover_timer.start(max(230, int(self.data.get('launch_hover_delay_ms', 250))))
                elif self.menu is not None and self.menu.isVisible():
                    self.hover_timer.stop()
                    self.pending_menu_item = None
                    self.menu.close()
            return True

        steps, self._classic_wheel_remainder = wheel_motion(
            angle, pixels, getattr(self, '_classic_wheel_remainder', 0))
        if not steps:
            return True
        direction = -steps  # wheel down -> following row
        if native_scroll:
            bar = tree.verticalScrollBar()
            if not can_follow_at_edge(scroll_before, scroll_after,
                                      bar.minimum(), bar.maximum(), direction):
                self._classic_wheel_remainder = 0
                return False
            # Never teleport a cursor that has left the Compact list.
            if not viewport.rect().contains(local):
                return False
        previous = tree.currentItem()
        anchor = (previous if getattr(self, '_classic_wheel_edge_active', False)
                  or not native_scroll else under_pointer or previous)
        selected = wheel_neighbor(items, anchor, direction)
        if selected is None:
            return True
        self.hover_timer.stop()
        self.pending_menu_item = None
        if selected is anchor:
            return True
        tree.setCurrentItem(selected)
        tree.scrollToItem(selected)
        if hasattr(tree, 'set_wheel_current_visual'):
            tree.set_wheel_current_visual(True)
        self._classic_wheel_edge_active = native_scroll
        row = selected.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(row, dict) and row.get('item_kind') in ('category', 'directory'):
            self.cascade(row, selected, 'keyboard')
        elif self.menu is not None and self.menu.isVisible():
            self.menu.close()
        if native_scroll:
            self.schedule_classic_wheel_pointer_follow(selected, pointer)
        return True

    def schedule_classic_wheel_pointer_follow(self, item, original_pos):
        """Defer cursor motion until Qt has settled the selected row geometry."""
        self._classic_wheel_follow_pending = (item, original_pos)
        if not getattr(self, '_classic_wheel_follow_scheduled', False):
            self._classic_wheel_follow_scheduled = True
            QTimer.singleShot(0, self.follow_classic_wheel_pointer)

    def follow_classic_wheel_pointer(self):
        """Move only vertically when the pointer is still over the old list."""
        self._classic_wheel_follow_scheduled = False
        pending = getattr(self, '_classic_wheel_follow_pending', None)
        self._classic_wheel_follow_pending = None
        if not getattr(self, 'pointer_warp_enabled', True):
            return
        if pending is None:
            return
        item, original_pos = pending
        tree = self.list
        if (self.view_mode not in ('classic', 'expanded') or not tree.isVisible()
                or tree.currentItem() is not item
                or QApplication.mouseButtons() != Qt.MouseButton.NoButton):
            return
        pointer = QCursor.pos()
        if pointer != original_pos:  # Human moved the mouse in the meantime.
            return
        viewport = tree.viewport()
        local = viewport.mapFromGlobal(pointer)
        if not viewport.rect().contains(local):
            return
        bounds = tree.visualItemRect(item)
        target = cursor_target((viewport.width(), viewport.height()),
                               (bounds.left(), bounds.top(), bounds.width(), bounds.height()),
                               local.x())
        if target is None:
            return
        destination = viewport.mapToGlobal(QPoint(*target))
        if destination != pointer:
            QCursor.setPos(destination)

    def focus_first_page_from_header_space(self, obj, event):
        """Focus the leftmost Page button when the Page row background is clicked.

        Real tab hits are handled by FocusPageTabBar and navigation/view-mode
        buttons retain their own click actions. No page change on right click.
        """
        if (obj is not self.mode_bar or event.type() != QEvent.Type.MouseButtonPress
                or event.button() != Qt.MouseButton.LeftButton
                or self.tabs.count() == 0):
            return False
        self.close_cascade_for_main_interaction()
        self.tabs.setCurrentIndex(0)
        self.tabs.setFocus(Qt.FocusReason.MouseFocusReason)
        event.accept()
        return True

    def eventFilter(self,obj,event):
        # Legacy event-filter test doubles do not implement newer handlers.
        if (getattr(self, 'handle_history_input_method', None) and
                self.handle_history_input_method(obj, event)):
            return True
        if (event.type() == QEvent.Type.Wheel and
                self.wheel_search_history(obj, event)):
            event.accept()
            return True
        # The middle viewport is already filtered here for keyboard/navigation.
        # Handle its invisible Back hit areas before Qt sends itemClicked,
        # without installing competing wheel filters on the same viewport.
        view = getattr(self, 'expanded_view', None)
        if (view is not None and view.isVisible() and
                view.handle_middle_back_double_click(obj, event)):
            return True
        if self.focus_first_page_from_header_space(obj, event):
            return True
        # Compact WAN needs the native scroll result first. ReorderTree.wheelEvent
        # calls wheel_classic_menu *after* Qt has moved the scrollbar. Older
        # tree implementations still use the legacy event-filter route.
        if (obj in (self.list, self.list.viewport())
                and event.type() == getattr(QEvent.Type, 'Wheel', None)
                and not getattr(self.list, 'adaptive_compact_wheel', False)
                and self.wheel_classic_menu(event)):
            event.accept()
            return True
        if (obj is self.list.viewport() and
                event.type() == getattr(QEvent.Type, 'MouseButtonPress', None) and
                event.button() in (Qt.MouseButton.LeftButton,
                                   Qt.MouseButton.RightButton)):
            self.close_cascade_for_main_interaction()
        if obj is self.list.viewport():
            if event.type() == getattr(QEvent.Type, 'MouseMove', None):
                self.record_main_hover_motion(event.position().toPoint())
            # Qt/Windows sometimes delivers ContextMenu to the parent, rather
            # than the tree's viewport. Capture the right-button interaction
            # here and hit-test the actual row on the *first* click.
            if (event.type() in (getattr(QEvent.Type, 'MouseButtonPress', None),
                                   QEvent.Type.MouseButtonRelease)
                    and event.button() == getattr(Qt.MouseButton, 'RightButton', None)):
                if event.type() == getattr(QEvent.Type, 'MouseButtonPress', None):
                    self._launcher_context_press = True
                elif getattr(self, '_launcher_context_press', False):
                    self._launcher_context_press = False
                    item = self.list.itemAt(event.position().toPoint())
                    row = item.data(0, Qt.ItemDataRole.UserRole) if item else None
                    if item is not None and row is not None:
                        self.list.setCurrentItem(item)
                    if row is not None or self.page_empty_area_can_open_context(event.position().toPoint()):
                        self.show_launch_context_menu(event.globalPosition().toPoint(), row)
                event.accept()
                return True
            if event.type() == getattr(QEvent.Type, 'ContextMenu', None):
                # No duplicate menu after handling the mouse button release.
                # Virtual search results never invoke Windows's OS menu.
                event.accept()
                return True
        if obj is getattr(self, 'search', None) and event.type() == QEvent.Type.Resize:
            self.layout_search_inner_controls()
        if obj is getattr(self, 'search', None) and event.type() == QEvent.Type.FocusOut:
            self.flush_live_search()
            self.record_session_search()
            self._session_edit_draft = None
        if obj is getattr(self, "search", None) and event.type() == QEvent.Type.FocusIn:
            # Qt may move the native caret HWND after FocusIn dispatch; defer
            # once, and do not touch input state while the user keeps focus.
            QTimer.singleShot(0, self.initialize_search_ime)
        if (obj is getattr(self, 'search', None) and
                event.type() == getattr(QEvent.Type, 'MouseButtonPress', None) and
                event.button() == Qt.MouseButton.LeftButton):
            if not self.history_popup.isVisible():
                QTimer.singleShot(0, self.show_history_popup)
        # Qt.Tool cascade columns do not monopolize keyboard focus.  On some
        # Windows setups the key event still lands in the main list/search/tabs
        # after the user selects a cascade row.  Give visible columns keyboard
        # ownership without changing their non-grabbing mouse behavior.
        if (event.type() == getattr(QEvent.Type, 'KeyPress', None)
                and obj is self.list and not self.expanded_view.isVisible()
                and event.key() == getattr(Qt.Key, 'Key_Delete', None)
                and event.modifiers() == Qt.KeyboardModifier.NoModifier
                and not self.selection):
            item = self.list.currentItem()
            row = item.data(0, Qt.ItemDataRole.UserRole) if item else None
            kind, path = resolve_context_target(row, self.authored_items)
            if kind in ('file', 'folder') and path:
                self.perform_filesystem_context_action('delete', path, kind)
                event.accept()
                return True
        if (event.type() == getattr(QEvent.Type, 'KeyPress', None)
                and obj in (self.list, self.tabs)):
            # Never steal keystrokes from the MAIN search QLineEdit.  When a
            # cascade is open, it must still support Japanese IME composition,
            # Left/Right caret movement, Home/End, and ordinary text editing.
            column = self.visible_cascade_for_keyboard()
            if column is not None and QApplication.activePopupWidget() is None:
                column.keyPressEvent(event)
                event.accept()
                return True
        if (event.type() == getattr(QEvent.Type, 'InputMethod', None)
                and obj in (self.list, self.tabs)):
            # IME pre-edit is not a printable KeyPress.  Relay it explicitly
            # when a non-grabbing Qt.Tool cascade owns the keyboard so the
            # inline QLineEdit can be created BEFORE the first commit.
            column = self.visible_cascade_for_keyboard()
            if column is not None and QApplication.activePopupWidget() is None:
                column.inputMethodEvent(event)
                event.accept()
                return True
        if obj is self.list.viewport():
            # Headerless main-menu columns have an invisible draggable grip.
            # Handle before double-click activation, but leave all other row
            # actions to the existing event path.
            if getattr(self, '_column_mode', None) == 'main' and self.handle_main_column_resize(event):
                return True
            if (event.type()==QEvent.Type.MouseButtonDblClick
                    and event.button()==Qt.MouseButton.LeftButton):
                item = self.list.itemAt(event.position().toPoint())
                if item is not None:
                    # Consume Qt's double-click activation on mouse DOWN.
                    # The same row is activated exactly once on mouse UP.
                    self._pending_mouse_activation = item.data(0,Qt.ItemDataRole.UserRole)
                    self._pending_mouse_foreground = windows.foreground()
                    DIAG.info('MOUSE_ACTIVATION queued item=%s',
                              self._pending_mouse_activation.get('item_id'))
                    event.accept()
                    return True
                # Double-click on empty submenu space remains Back.
                if self.stack or self.selection is not None:
                    self.go_back()
                    event.accept()
                    return True
            if (event.type()==QEvent.Type.MouseButtonRelease
                    and event.button()==Qt.MouseButton.LeftButton
                    and self._pending_mouse_activation is not None):
                row = self._pending_mouse_activation
                expected = self._pending_mouse_foreground
                self._pending_mouse_activation = None
                self._pending_mouse_foreground = None
                # Deliver this release to Windows *before* creating the child.
                QTimer.singleShot(0, lambda r=row, fg=expected:
                                  self.activate_after_mouse_release(r,fg))
                event.accept()
                return True
        if event.type() == QEvent.Type.KeyPress and hasattr(self, 'expanded_view'):
            view = self.expanded_view
            expanded_sources = (view.root_buttons + [view.address_bar.editor] + [pane.tree for pane in
                (view.left, view.middle, view.right)] + [pane.tree.viewport() for pane in
                (view.left, view.middle, view.right)])
            if view.isVisible() and obj in expanded_sources:
                # A Qt.Tool cascade can leave real keyboard focus in the panel.
                # Its deeper rows must own arrows/Enter/Esc until dismissed.
                column = self.visible_cascade_for_keyboard()
                if column is not None and QApplication.activePopupWidget() is None:
                    column.keyPressEvent(event)
                    event.accept()
                    return True
            if self.expanded_focus_key(obj, event):
                return True
            if self.expanded_root_key(obj, event):
                return True
            if obj is self.tabs and self.expanded_tab_key(event):
                return True
            for panel in (self.expanded_view.left, self.expanded_view.middle,
                          self.expanded_view.right):
                if obj in (panel.tree, panel.tree.viewport()) and self.expanded_tree_key(obj, event):
                    return True
        # Legacy mouse-event test stubs reuse this method without a full UI.
        if getattr(self, 'handle_history_event', None) and self.handle_history_event(obj, event):
            return True
        if obj==self.tabs:
            if (event.type()==QEvent.Type.KeyPress
                    and event.modifiers()==Qt.KeyboardModifier.NoModifier):
                key=event.key()
                if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                    direction = 1 if key == Qt.Key.Key_Down else -1
                    if self.in_root_page_navigation():
                        self.move_root_page_selection(direction, from_tab=True)
                    else:
                        # Search / submenus retain list-only wrap navigation.
                        move_tree_selection(self.list, direction)
                        self.list.setFocus(Qt.FocusReason.TabFocusReason)
                    event.accept();return True
                if key in (Qt.Key.Key_Left,Qt.Key.Key_Right):
                    index=max(0,min(self.tabs.count()-1,self.tabs.currentIndex()+(1 if key==Qt.Key.Key_Right else -1)))
                    if self.tabs.count():self.tabs.setCurrentIndex(index)
                    event.accept();return True
            return super().eventFilter(obj,event)
        if event.type()==QEvent.Type.KeyPress:
            k=event.key();ctrl=bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)
            if ctrl and k in (Qt.Key.Key_C, Qt.Key.Key_X, Qt.Key.Key_V):
                # Non-grabbing Qt.Tool cascades can leave focus on the main
                # tree. Only an *actually focused* search field owns text
                # clipboard keys; otherwise route to the folder column.
                editor_focused = (obj is self.search and self.search.hasFocus())
                if not editor_focused:
                    cascade = self.visible_cascade_for_keyboard()
                    if cascade is not None and cascade.handle_file_shortcut(k, event.modifiers()):
                        event.accept()
                        return True
            if ctrl and k==Qt.Key.Key_F:
                self.focus_search();return True
            # When the caret is in the main search editor, cursor navigation
            # must NEVER close/open the still-visible folder cascade.  Qt's
            # QLineEdit handles arrows (including Ctrl+Left/Right) natively.
            if obj is self.search and k in (
                    Qt.Key.Key_Left, Qt.Key.Key_Right,
                    Qt.Key.Key_Home, Qt.Key.Key_End):
                return False
            if self.page_key(event):return True
            # IME owns its pre-edit and candidate keystrokes.
            if getattr(self,'composing',False):return False
            if self.selection and k==Qt.Key.Key_A and (ctrl or
                    bool(event.modifiers() & Qt.KeyboardModifier.AltModifier)):
                self.select_all(not bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier));return True
            # The search box ALWAYS owns Space for text input, including while
            # recipient checkboxes are visible. The list keeps its own Space
            # checkbox shortcut below; Enter also works from the search box.
            # Silent endpoint reaction; Page-tab Left/Right stays unchanged.
            if (k == Qt.Key.Key_Left and obj is self.list
                    and event.modifiers() == Qt.KeyboardModifier.NoModifier
                    and self.at_root_first_row()):
                self.show_root_left_feedback()
                event.accept()
                return True
            if k==Qt.Key.Key_Left and (self.selection or obj==self.list or not self.search.text()):
                self.go_back();return True
            if k==Qt.Key.Key_Right and self.selection and event.modifiers()==Qt.KeyboardModifier.NoModifier:
                # In a recipient-choice list, Right means Enter: toggle the
                # highlighted checkbox. Preserve cursor movement while typing
                # a non-empty search query in QLineEdit.
                if obj==self.list or (obj==self.search and not self.search.text()):
                    q=self.list.currentItem()
                    if q:self.activate(q.data(0,Qt.ItemDataRole.UserRole))
                    event.accept();return True
            if k==Qt.Key.Key_Right and not self.selection and (obj==self.list or not self.search.text()):
                q=self.list.currentItem()
                if q:
                    row=q.data(0,Qt.ItemDataRole.UserRole)
                    if row.get('item_kind') in {'category','directory'}:self.cascade(row,q)
                    else:self.activate(row)
                return True
            if k in (Qt.Key.Key_Down, Qt.Key.Key_Up):
                if obj is self.search:
                    self.flush_live_search()
                direction = 1 if k == Qt.Key.Key_Down else -1
                if self.in_root_page_navigation():
                    # Main Page navigation includes the current Page tab as
                    # one stop between the first and last menu entries.
                    self.move_root_page_selection(direction)
                else:
                    # Search results, selection screens and submenus loop
                    # only within their visible list rows.
                    move_tree_selection(self.list, direction)
                    self.list.setFocus()
                event.accept()
                return True
            if k==Qt.Key.Key_Escape:
                # Qt.Tool columns sometimes leave real keyboard focus on the
                # main grid. First Esc should close the visible column, not
                # clear the global search or dismiss the whole launcher.
                active_column = self.visible_cascade_for_keyboard()
                if active_column is not None and not (obj is self.search and self.search.hasFocus()):
                    active_column.close()
                    event.accept()
                    return True
                if self.search.text():self.search.clear()
                elif self.selection or self.stack:
                    self._nav_before_change()
                    if self.selection:self.selection=None
                    elif self.stack:self.stack.pop()
                    self.render()
                    self._nav_after_change()
                else:self.dismiss()
                return True
            if ctrl and k in (Qt.Key.Key_PageUp,Qt.Key.Key_PageDown):
                self.tabs.setCurrentIndex((self.tabs.currentIndex()+(1 if k==Qt.Key.Key_PageDown else -1))%self.tabs.count());return True
            if k==Qt.Key.Key_F12:self.confirm_selection();return True
            if k in (Qt.Key.Key_Return,Qt.Key.Key_Enter):
                self.flush_live_search()
                self.record_session_search()
                self._session_edit_draft = None
                q=self.list.currentItem()
                if q:self.activate(q.data(0,Qt.ItemDataRole.UserRole))
                return True
            if obj==self.list:
                if k==Qt.Key.Key_Right and self.list.currentItem() and not self.selection:
                    q=self.list.currentItem();r=q.data(0,Qt.ItemDataRole.UserRole)
                    if r['item_kind'] in {'category','directory'}:self.cascade(r,q)
                    return True
                if k==Qt.Key.Key_Left:
                    if self.stack:
                        self._nav_before_change()
                        self.stack.pop();self.render()
                        self._nav_after_change()
                    return True
                if k==Qt.Key.Key_Space:
                    current=self.list.currentItem()
                    if current:
                        hit=current.data(0,Qt.ItemDataRole.UserRole)
                        if self.selection or (hit and hit.get('_search_selection_owner')):
                            self.activate(hit)
                            return True
                if event.text() and not ctrl and not event.modifiers() & Qt.KeyboardModifier.AltModifier:
                    self.search.setFocus();QApplication.sendEvent(self.search,QKeyEvent(event.type(),k,event.modifiers(),event.text()));return True
                if k==Qt.Key.Key_Backspace:self.search.setFocus();self.search.backspace();return True
        if obj==self.list and event.type()==QEvent.Type.InputMethod:
            self.search.setFocus();QApplication.sendEvent(self.search,event);return True
        if obj==self.search and event.type()==QEvent.Type.InputMethod:
            self.composing=bool(event.preeditString())
        return super().eventFilter(obj,event)

    def launch_configuration_studio(self, *, item_id=None, new_category=False,
                                    page_properties=False):
        """Open the authored Launch DataJSON.  UI never edits the JSON itself."""
        if not self.data:
            return
        studio_root = self.expander().values.get('studio_root', '')
        exe = Path(studio_root) / 'NativeShell' / '_publish' / 'FRBStudio.NativeShell.exe'
        if not exe.is_file():
            self.error('Studioくんが見つかりません: ' + str(exe))
            return
        args = ['--open-json=' + str(CONFIG)]
        if new_category:
            args.append('--launch-new-category=' + str(self.page_id))
        elif page_properties:
            # Page is a virtual group header in Studio's ordinary item grid,
            # NOT a menu item and NOT the separate Page editor.
            args.append('--launch-page-id=' + str(self.page_id))
        elif item_id:
            args.append('--launch-item-id=' + str(item_id))
        else:
            return
        self.execute({
            'item_id': '__launch_context_studio',
            'title': 'Studioくんでメニュー設定を編集',
            'launch_actions': [{
                'launch_action_type': 'Run',
                'launch_program': str(exe),
                'launch_arguments': args,
                'launch_working_directory': studio_root,
                'launch_wait_for_exit': False
            }]
        })

    def _paste_context_destination(self, context_parent=None):
        """Use the CURRENT folder, never the right-clicked file's path.

        Search results have no implied destination, so paste remains disabled.
        """
        if isinstance(context_parent, CascadeMenu):
            container = context_parent._folder_container_row()
            if container:
                try:
                    target = Path(self.expander().expand(container['launch_browse_target']))
                    if target.is_dir():
                        return 'cascade'
                except (KeyError, ValueError, OSError):
                    pass
        if (context_parent is self and self.expanded_view.isVisible()):
            path = self.expanded_view.current_directory()
            if path and Path(path).is_dir():
                return 'expanded'
        return None

    def _context_paste_enabled(self, context_parent=None):
        if not self._paste_context_destination(context_parent):
            return False
        mime = QApplication.clipboard().mimeData()
        return bool(clipboard_sources(mime)) or is_virtual_file_clipboard(mime)

    def _paste_from_context_menu(self, context_parent=None, *, target_folder=None):
        # Explicit right-click folders bypass the middle grid's selected rows.
        # Both paste cores validate the final target before writing to disk.
        if target_folder is None and not self._context_paste_enabled(context_parent):
            return
        if self._paste_context_destination(context_parent) == 'cascade':
            if target_folder is None:
                self.paste_into_directory(context_parent)
            else:
                self.paste_into_directory(context_parent, destination_override=target_folder)
        elif target_folder is None:
            self.paste_into_expanded_directory()
        else:
            self.paste_into_expanded_directory(destination_override=target_folder)
        # The destination/clipboard result now lives in the Files views and
        # status bar; never leave a source context menu hovering above them.
        closer = getattr(self, 'close_finished_file_context_menus', None)
        if callable(closer):
            QTimer.singleShot(0, closer)

    def can_rename_remote_folder(self, directory):
        """Never rename a registered shortcut root, drive, or filesystem root."""
        path = Path(directory)
        if not path.is_dir() or path.parent == path:
            return False
        try:
            from remote_files_exp_roots import registered_folder_roots
            roots = registered_folder_roots(self._remote_files_first_column_rows(),
                                            self.expander().expand)
            registered = {path_key(r['path']) for r in roots if r.get('path')}
            if path_key(path) in registered:
                return False
            from system_drives import drive_rows
            drives = {path_key(r['launch_browse_target']) for r in drive_rows()}
            return path_key(path) not in drives
        except (OSError, ValueError, TypeError, KeyError):
            return False

    def can_delete_remote_folder(self, directory):
        """Protect all registered roots, drives and their ancestors.

        A folder *under* a registered root is still a normal folder and can
        be deleted.  Moving (cutting) a protected root is also prohibited.
        """
        if not self.can_rename_remote_folder(directory):
            return False
        candidate = Path(directory)
        try:
            from remote_files_exp_roots import registered_folder_roots
            from system_drives import drive_rows
            roots = registered_folder_roots(self._remote_files_first_column_rows(),
                                             self.expander().expand)
            protected = [r['path'] for r in roots if r.get('path')]
            protected.extend(r['launch_browse_target'] for r in drive_rows())
            candidate_key = path_key(candidate)
            for entry in protected:
                protected_key = path_key(entry)
                # Compare canonical, case-folded paths: Windows filenames are
                # case insensitive and a folder name can be supplied in a
                # different case from the saved JSON shortcut.
                if (protected_key == candidate_key or
                        protected_key.startswith(candidate_key.rstrip('/') + '/')):
                    return False
            return True
        except (OSError, ValueError, TypeError, KeyError):
            return False

    def _after_folder_deleted(self, deleted_path, *, previous_current=None):
        """Navigate from a removed folder to its *parent*, not a sibling row.

        Capture the breadcrumb BEFORE recycle-bin work: after deleting the
        directory, rendering/selection repair can already have cleared it.
        The Files breadcrumb drives Files Exp selection through the existing
        on_files_directory_changed notification, without a second navigation
        source or a spurious history entry for a missing folder.
        """
        deleted = Path(deleted_path)
        current = (previous_current if previous_current is not None else
                   self.expanded_view.current_directory())
        deleted_key = path_key(deleted)
        current_key = path_key(current) if current else ''
        affected = bool(current_key and
                        (current_key == deleted_key or
                         current_key.startswith(deleted_key.rstrip('/') + '/')))
        parent = str(deleted.parent)
        panels = getattr(self, 'files_exp_panels', lambda: tuple(
            panel for panel in (
                getattr(getattr(self, 'remote_window', None), 'files_exp_panel', None),
                getattr(getattr(self, 'expanded_view', None), 'embedded_files_exp', None))
            if panel is not None))()
        # Tree pruning may cause Qt to put the current row on the next sibling.
        # Suppress that incidental selection and restore the exact parent.
        for panel in panels:
            panel.reflect_deleted_folder(str(deleted))
        notify = getattr(self, 'notify_folder_mutation', None)
        if callable(notify):
            notify(parent)
        view = self.expanded_view
        if view.isVisible() and affected and Path(parent).is_dir():
            view.go_to_directory(parent)
            for panel in panels:
                if panel.isVisible():
                    panel.sync_current_directory(parent)
        elif view.isVisible() and current_key == path_key(parent):
            view.refresh_middle()

    def begin_remote_rename_after_menu(self, directory):
        """Dismiss the popup BEFORE focusing Files Exp's inline editor."""
        self.close_finished_file_context_menus()
        QTimer.singleShot(0, lambda: self.rename_remote_folder(directory))

    def rename_remote_folder(self, directory):
        """One Rename command for Files Exp and Remote's current-folder menu.

        Prefer the inline tree editor when the requested folder is selected.
        Otherwise use the same validated filesystem rename as Files.
        """
        if not self.can_rename_remote_folder(directory):
            return False
        for panel in getattr(self, 'files_exp_panels', lambda: tuple(
            panel for panel in (
                getattr(getattr(self, 'remote_window', None), 'files_exp_panel', None),
                getattr(getattr(self, 'expanded_view', None), 'embedded_files_exp', None))
            if panel is not None))():
            if panel.isVisible() and panel.can_rename_folder(directory):
                return panel.begin_folder_rename(directory)
        path = Path(directory)
        name, accepted = QInputDialog.getText(
            self, '名前の変更', '新しい名前:', text=path.name)
        if not accepted or name == path.name:
            return False
        try:
            new_path = str(rename_file_or_folder(path, name))
        except (OSError, ValueError) as exc:
            self.error('名前を変更できませんでした: ' + str(exc))
            return False
        panels = getattr(self, 'files_exp_panels', lambda: tuple(
            panel for panel in (
                getattr(getattr(self, 'remote_window', None), 'files_exp_panel', None),
                getattr(getattr(self, 'expanded_view', None), 'embedded_files_exp', None))
            if panel is not None))()
        for panel in panels:
            panel.reflect_external_folder_rename(directory, new_path)
        self.on_files_exp_folder_renamed(directory, new_path)
        self.notify_folder_mutation(path.parent)
        return True

    def rename_remote_cascade_entry(self, target, kind, source_menu=None):
        """Rename inside its *visible cascade row*, not in a separate dialog."""
        if source_menu is not None:
            if not source_menu.isVisible():
                return False
            return source_menu.begin_inline_rename(target, kind)
        path = Path(target)
        if kind == 'folder' and not self.can_rename_remote_folder(path):
            return False
        if not (path.is_dir() if kind == 'folder' else path.is_file()):
            self.error('名前を変更できませんでした: 対象が見つかりません')
            return False
        name, accepted = QInputDialog.getText(
            self, '名前の変更', '新しい名前:', text=path.name)
        if not accepted or name == path.name:
            return False
        if kind == 'file' and Path(name).suffix.casefold() != path.suffix.casefold():
            answer = QMessageBox.question(
                self, '拡張子の変更', 'ファイルの拡張子が変わります。名前を変更しますか？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if answer != QMessageBox.StandardButton.Yes:
                return False
        try:
            new_path = str(rename_file_or_folder(path, name))
        except (OSError, ValueError) as exc:
            self.error('名前を変更できませんでした: ' + str(exc))
            return False
        # A cached cascade row still refers to the old name. Reopen the folder
        # list on demand using fresh disk entries, without rewriting DataJSON.
        self.close_remote_folder_menu()
        if kind == 'folder':
            for panel in getattr(self, 'files_exp_panels', lambda: tuple(
            panel for panel in (
                getattr(getattr(self, 'remote_window', None), 'files_exp_panel', None),
                getattr(getattr(self, 'expanded_view', None), 'embedded_files_exp', None))
            if panel is not None))():
                panel.reflect_external_folder_rename(path, new_path)
            self.on_files_exp_folder_renamed(str(path), new_path)
        else:
            if self.expanded_view.isVisible() and self.expanded_view.current_directory() == str(path.parent):
                self.expanded_view.refresh_middle()
            self.footer.setText(f'名前を変更しました: {path.name} → {Path(new_path).name}')
        if self.file_index_settings.get('enabled', True) and not self.file_index_busy:
            QTimer.singleShot(0, lambda: self.refresh_file_index(manual=False))
        return True

    def commit_remote_inline_rename(self, old_path, new_name, kind):
        """One validated filesystem mutation shared by Remote cascade editors."""
        path = Path(old_path)
        if kind == 'folder' and not self.can_rename_remote_folder(path):
            raise ValueError('登録フォルダーやドライブの名前は変更できません')
        if not (path.is_dir() if kind == 'folder' else path.is_file()):
            raise ValueError('対象が見つかりません')
        if kind == 'file' and Path(new_name).suffix.casefold() != path.suffix.casefold():
            answer = QMessageBox.question(
                self, '拡張子の変更', 'ファイルの拡張子が変わります。名前を変更しますか？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if answer != QMessageBox.StandardButton.Yes:
                return None
        new_path = str(rename_file_or_folder(path, new_name))
        if kind == 'folder':
            for panel in getattr(self, 'files_exp_panels', lambda: tuple(
            panel for panel in (
                getattr(getattr(self, 'remote_window', None), 'files_exp_panel', None),
                getattr(getattr(self, 'expanded_view', None), 'embedded_files_exp', None))
            if panel is not None))():
                panel.reflect_external_folder_rename(path, new_path)
            # Renaming a child should not jump the breadcrumb away from its
            # parent just because the user edited a submenu row.
            current = self.expanded_view.current_directory()
            if current and os.path.normcase(current) == os.path.normcase(str(path)):
                # The current folder itself moved. Keep the editing cascade
                # alive until its row/editor has finished updating; the normal
                # breadcrumb observer would otherwise close it mid-commit.
                previous_navigation = getattr(self, '_remote_folder_navigation', False)
                self._remote_folder_navigation = True
                try:
                    self.on_files_exp_folder_renamed(str(path), new_path)
                finally:
                    self._remote_folder_navigation = previous_navigation
            else:
                from folder_sort_preferences import transfer_directory_sort
                from middle_folder_filter import SORT_LABELS
                transfer_directory_sort(self.settings, str(path), new_path, SORT_LABELS)
        if (self.expanded_view.isVisible() and
                os.path.normcase(str(self.expanded_view.current_directory() or '')) ==
                os.path.normcase(str(path.parent))):
            self.expanded_view.refresh_middle()
        self.footer.setText(f'名前を変更しました: {path.name} → {Path(new_path).name}')
        if self.file_index_settings.get('enabled', True) and not self.file_index_busy:
            QTimer.singleShot(0, lambda: self.refresh_file_index(manual=False))
        return new_path

    def show_expanded_background_paste_menu(self, global_pos, *, remote_folder_list=False,
                                            files_exp_rename_target=None):
        """One JSON-defined folder menu for the Files background and Remote.

        A Files Exp right-click binds EVERY action to its own folder, never
        to whichever row happens to be highlighted in the main Files grid.
        The Remote adds only Filesリスト and 新規作成 (not filesystem verbs).
        """
        if not self.expanded_view.current_directory():
            return False
        try:
            definitions = load_context_menus(CONTEXT_MENU_OPTIONS)['folder']
        except (OSError, ValueError, KeyError) as exc:
            self.error('コンテキストメニュー定義が不正です: ' + str(exc))
            return False
        explicit_target = str(files_exp_rename_target) if files_exp_rename_target else None
        target_directory = str(explicit_target or self.expanded_view.current_directory())
        if not Path(target_directory).is_dir():
            self.error('操作対象のフォルダーが見つかりません: ' + target_directory)
            return False
        menu = RemoteFolderActionsMenu(parent=self, launcher=self) if remote_folder_list else QMenu(self)
        # The ordinary Launch Files-background menu and Files Exp's Remote
        # menu share the same deliberate compact width.
        menu.setMinimumWidth(218)
        menu.setMaximumWidth(225)
        if remote_folder_list:
            if explicit_target is None:
                menu = self._apply_remote_popup_bounds(menu)
            menu.remote_context_root = True
            menu.open_mode = 'keyboard'
            menu.remote_target_directory = explicit_target
            folder_list_action = menu.addAction('Filesリスト')
            menu.folder_list_action = folder_list_action
            # Compact enough for the short caption without squeezing the
            # longest actual filesystem action ('クラウドリンクのコピー').
            menu.setMinimumWidth(218)
            menu.setMaximumWidth(225)
            folder_list_action.setIcon(self.file_icons.icon(QFileInfo(target_directory)))
            folder_list_action.setData({'item_kind': 'category', 'item_id': 'remote-folder-list'})
            menu.openers[folder_list_action] = (
                lambda mode='hover', m=menu, a=folder_list_action:
                self._open_remote_folder_cascade(m, a, None, mode))
            folder_list_action.triggered.connect(
                lambda checked=False, a=folder_list_action: menu.openers[a]('refresh'))
            self._remote_folder_opener = menu
            self._remote_folder_root_menu = None
            self._remote_folder_source_path = os.path.normcase(os.path.normpath(target_directory))
            self._remote_folder_popup_pos = global_pos
            menu.aboutToHide.connect(lambda m=menu: self._remote_folder_opener_hidden(m))
            menu.addSeparator()

        # Context definitions determine order, labels and grouping.  The
        # special New submenu follows Paste, and Filesリスト stays above them.
        # There must never be an alternate Remote-only copy/delete implementation.
        for definition in visible_context_entries(definitions):
            if definition.get('type') == 'separator':
                menu.addSeparator()
                continue
            action_id = definition['action_id']
            if action_id == 'refresh_directory':
                action = menu.addAction(
                    definition['title'],
                    lambda checked=False, p=target_directory:
                    QTimer.singleShot(0, lambda: self.refresh_folder_information(p)))
            elif action_id == 'paste':
                action = menu.addAction(
                    definition['title'],
                    lambda checked=False, p=(target_directory if remote_folder_list
                                             else explicit_target):
                    self._paste_from_context_menu(self, target_folder=p))
                action.setEnabled(self._context_paste_enabled(self))
            elif action_id == 'rename':
                action = menu.addAction(
                    definition['title'],
                    lambda checked=False, p=target_directory:
                    QTimer.singleShot(0, lambda: self.begin_remote_rename_after_menu(p)))
                # Keep the same menu rows as a selected folder; an empty
                # background never implicitly renames the current directory.
                action.setEnabled(bool(remote_folder_list) and
                                  self.can_rename_remote_folder(target_directory))
            elif action_id == 'delete':
                action = menu.addAction(
                    definition['title'],
                    lambda checked=False, p=target_directory:
                    self.perform_filesystem_context_action('delete', p, 'folder'))
                action.setEnabled(bool(remote_folder_list) and
                                  self.can_delete_remote_folder(target_directory))
            elif action_id in ('copy', 'cut'):
                action = menu.addAction(
                    definition['title'],
                    lambda checked=False, a=action_id, p=target_directory:
                    self.perform_filesystem_context_action(a, p, 'folder'))
                action.setEnabled(bool(remote_folder_list) and
                                  (action_id != 'cut' or
                                   self.can_delete_remote_folder(target_directory)))
            else:
                action = menu.addAction(
                    definition['title'],
                    lambda checked=False, a=action_id, p=target_directory:
                    self.perform_filesystem_context_action(a, p, 'folder'))
            action.setIcon(context_action_icon(action_id))
            action.setIconVisibleInMenu(True)
            if action_id == 'paste':
                menu.addSeparator()
                if explicit_target is None:
                    new_submenu = self.expanded_view.add_lane_new_submenu(menu)
                else:
                    new_submenu = self.expanded_view.add_lane_new_submenu(
                        menu, target_directory=explicit_target)
                if new_submenu is not None:
                    # New-file submenu actions must not dismiss the inline
                    # filename editor, including in the ordinary blank menu.
                    menu.new_submenu_action = new_submenu.menuAction()
        # Ignore repeated or trailing dividers when a subset is disabled.
        actions = menu.actions()
        for current, later in zip(actions, actions[1:]):
            if current.isSeparator() and later.isSeparator():
                current.setVisible(False)
        if actions and actions[-1].isSeparator():
            actions[-1].setVisible(False)
        menu.setStyleSheet((LIGHT_MENU_QSS if self.color_theme == 'light' else '')
                           + context_menu_spacing_qss(self.color_theme)
                           + (remote_new_arrow_qss(self.color_theme)
                              if remote_folder_list else ''))
        self._launch_context_menu = menu
        menu.aboutToHide.connect(lambda m=menu: self._forget_launch_context_menu(m))
        # QMenu keeps hover-preview branches open deliberately. Leaf actions
        # are complete commands and must dismiss all related popup windows.
        menu.triggered.connect(lambda action, m=menu:
            self._on_file_context_action_triggered(m, action))
        menu.popup(global_pos)
        return True

    def _on_file_context_action_triggered(self, menu, action):
        if action is None or action.menu() is not None or action is getattr(menu, 'folder_list_action', None):
            return  # Preview/submenu navigation is not a completed action.
        # New Folder starts an inline grid edit asynchronously; closing the
        # menu immediately can steal editor focus before Enter. Let editing-
        # Finished close the context menu instead.
        new_action = getattr(menu, 'new_submenu_action', None)
        new_menu = new_action.menu() if new_action is not None else None
        if new_menu is not None and action in new_menu.actions():
            return
        if action.text().strip() == '名前の変更':
            # Queue after begin_folder_rename() so the editor survives the
            # popup dismissal. Its Enter/Escape still work independently.
            QTimer.singleShot(0, self.close_finished_file_context_menus)
            return
        QTimer.singleShot(0, self.close_finished_file_context_menus)

    def add_open_with_submenu(self, parent_menu, title, path):
        """Right-opening app list; native chooser remains the final fallback."""
        submenu = parent_menu.addMenu(str(title).rstrip('…').rstrip('.').strip())
        submenu.setObjectName('expandedOpenWithSubmenu')
        submenu.setIcon(context_action_icon('open_with'))
        try:
            applications = discover_open_with_apps(path)
        except (OSError, ValueError) as exc:
            DIAG.warning('OPEN_WITH app discovery failed file=%s error=%s', path, exc)
            applications = []
        for application in applications:
            action = submenu.addAction(application.title)
            action.setIcon(self.file_icons.icon(QFileInfo(application.executable)))
            action.triggered.connect(
                lambda checked=False, filename=str(path), exe=application.executable:
                self.open_file_with_selected_app(filename, exe))
        if applications:
            submenu.addSeparator()
        else:
            unavailable = submenu.addAction('（起動可能な候補が見つかりません）')
            unavailable.setEnabled(False)
        other = submenu.addAction('別のプログラムを選択…')
        other.setIcon(context_action_icon('open_with'))
        other.triggered.connect(
            lambda checked=False, filename=str(path):
            self.perform_filesystem_context_action('open_with', filename, 'file'))
        return submenu

    def open_file_with_selected_app(self, path, executable):
        """A direct Open With choice never changes the default application."""
        try:
            # Registry entries can become stale while a menu is open.
            if not Path(path).is_file():
                raise FileNotFoundError('対象ファイルが見つかりません: ' + str(path))
            if not Path(executable).is_file():
                raise FileNotFoundError('アプリが見つかりません: ' + str(executable))
            # Legacy Tool mode must give the new app the foreground. Normal
            # window mode keeps Launch visible and allows the app above it.
            if getattr(self, 'dismiss_on_outside_click', True):
                self.dismiss()
            open_file_with_app(path, executable)
        except (OSError, ValueError, RuntimeError) as exc:
            self.error('プログラムから開けませんでした: ' + str(exc))

    def show_launch_context_menu(self, global_pos, row=None, *, context_parent=None,
                                 selected_paths=None, force_search_context=False):
        """Choose context actions by authoritative source, not displayed item ID."""
        if not self.data:
            return False
        if (self.selection and not force_search_context
                and not getattr(context_parent, 'remote_folder_navigation', False)):
            return False
        origin, path = resolve_context_target(row, self.authored_items)
        # Main-search results use a safe, shared filesystem context menu.
        # The Files pane/cascade still use their own existing commands.
        search_result = (bool(force_search_context) or
                         (bool(self.search.text().strip())
                          and context_parent is None and selected_paths is None))
        if search_result and origin == 'studio':
            from context_menu_resolver import resolve_search_context_target
            origin, path = resolve_search_context_target(
                row, self.authored_items, lambda target: self.expander().expand(target))
        if row is None:
            if self.stack or self.search.text().strip():
                return False
            menu = QMenu(context_parent if context_parent is not None else self)
            created = menu.addAction('新規作成（カテゴリー）',
                                     lambda: self.launch_configuration_studio(new_category=True))
            props = menu.addAction('プロパティ',
                                   lambda: self.launch_configuration_studio(page_properties=True))
            if created is not None:
                created.setIcon(context_action_icon('new_category'))
            if props is not None:
                props.setIcon(context_action_icon('properties'))
        elif origin == 'studio':
            menu = QMenu(context_parent if context_parent is not None else self)
            props = menu.addAction('プロパティ',
                                   lambda checked=False, item_id=row['item_id']: self.launch_configuration_studio(item_id=item_id))
            if props is not None:
                props.setIcon(context_action_icon('properties'))
        elif origin in ('file', 'folder'):
            # The expanded middle pane passes its actual selection, rather
            # than silently acting on the one row that was right-clicked.
            if selected_paths is not None and len(selected_paths) > 1:
                try:
                    entries = load_context_menus(CONTEXT_MENU_OPTIONS)['file']
                except (OSError, ValueError, KeyError) as exc:
                    self.error('コンテキストメニュー定義が不正です: ' + str(exc))
                    return False
                menu = QMenu(context_parent if context_parent is not None else self)
                batch = tuple(selected_paths)
                batch_allowed = {'copy', 'cut', 'paste', 'copy_full_path', 'copy_file_name', 'delete'}
                for definition in visible_context_entries(entries, batch_allowed):
                    action_id = definition.get('action_id')
                    if definition.get('type') == 'separator':
                        menu.addSeparator()
                        continue
                    if action_id == 'paste':
                        action = menu.addAction(definition['title'],
                            lambda checked=False, parent=context_parent:
                            self._paste_from_context_menu(parent))
                        action.setEnabled(self._context_paste_enabled(context_parent))
                    else:
                        action = menu.addAction(
                            f'{definition["title"]}（{len(batch)}件）',
                            lambda checked=False, a=action_id, ps=batch:
                            self.perform_filesystem_batch_action(a, ps))
                    action.setIcon(context_action_icon(action_id))
                    action.setIconVisibleInMenu(True)
                self.hover_timer.stop()
                self.pending_menu_item = None
                self._launch_context_menu = menu
                menu.aboutToHide.connect(lambda m=menu: self._forget_launch_context_menu(m))
                # A mixed file/folder selection uses the same compact width.
                menu.setMinimumWidth(218)
                menu.setMaximumWidth(225)
                if getattr(self, 'color_theme', 'dark') == 'light':
                    menu.setStyleSheet(LIGHT_MENU_QSS + context_menu_spacing_qss(self.color_theme))
                elif hasattr(menu, 'setStyleSheet'):
                    menu.setStyleSheet(context_menu_spacing_qss(self.color_theme))
                menu.popup(global_pos)
                return True
            try:
                actions = load_context_menus(CONTEXT_MENU_OPTIONS)[origin]
            except (OSError, ValueError, KeyError) as exc:
                self.error('コンテキストメニュー定義が不正です: ' + str(exc))
                return False
            menu = QMenu(context_parent if context_parent is not None else self)
            if origin == 'folder':
                # Match the compact 218-225px Remote / Files Exp menu.
                menu.setMinimumWidth(218)
                menu.setMaximumWidth(225)
            allowed = {d['action_id'] for d in actions if d.get('action_id')
                       and not (d['action_id'] == 'run_with_pause' and Path(path).suffix.casefold() not in ('.ps1', '.py'))
                       and not (d['action_id'] == 'extract_all' and Path(path).suffix.casefold() != '.zip')}
            if search_result:
                # Search is a navigation/lookup surface, not a file editor.
                # Keep menu labels/order configured in JSON while suppressing
                # cut/paste/delete/rename (and script/write operations).
                from context_menu_config import visible_search_context_entries
                definitions = visible_search_context_entries(actions, origin, allowed)
            else:
                definitions = visible_context_entries(actions, allowed)
            if search_result and origin == 'folder':
                action = menu.addAction('Launch内で開く',
                    lambda checked=False, p=path: self.open_search_folder_in_launch(p))
                action.setIcon(context_action_icon('open_explorer'))
                action.setIconVisibleInMenu(True)
                if definitions:
                    menu.addSeparator()
            for definition in definitions:
                if definition.get('type') == 'separator':
                    menu.addSeparator()
                    continue
                action_id = definition['action_id']
                if action_id == 'paste':
                    action = menu.addAction(definition['title'],
                        lambda checked=False, parent=context_parent,
                               clicked=path if origin == 'folder' else None:
                        self._paste_from_context_menu(parent, target_folder=clicked)
                        if clicked is not None else self._paste_from_context_menu(parent))
                    action.setEnabled(self._context_paste_enabled(context_parent))
                    if (origin == 'folder' and not search_result
                            and selected_paths is not None):
                        # The Files list and its blank background present
                        # one consistent folder menu (including New).  Here
                        # the explicit clicked folder owns the creation.
                        menu.addSeparator()
                        new_submenu = self.expanded_view.add_lane_new_submenu(
                            menu, target_directory=str(path))
                        if new_submenu is not None:
                            menu.new_submenu_action = new_submenu.menuAction()
                elif action_id == 'rename' and getattr(context_parent, 'remote_folder_navigation', False):
                    # Remote's actual folder/file list is NOT a search result.
                    # Keep the same JSON-defined rename position as Files.
                    action = menu.addAction(definition['title'],
                        lambda checked=False, p=path, k=origin, source=context_parent:
                        QTimer.singleShot(0, lambda:
                            self.rename_remote_cascade_entry(p, k, source)))
                    if origin == 'folder':
                        action.setEnabled(self.can_rename_remote_folder(path))
                elif action_id == 'open_with' and origin == 'file':
                    # Native Explorer uses a right-hand menu here, not an
                    # immediate modal chooser. Keep the OS chooser as the
                    # last entry for handlers the registry cannot launch.
                    self.add_open_with_submenu(menu, definition['title'], path)
                    continue
                elif (action_id == 'open_parent_folder' and origin == 'file'
                      and search_result):
                    # Main-search file results jump into *Launch's* Files pane.
                    # The normal Files-column action keeps its old OS behavior.
                    action = menu.addAction(definition['title'],
                        lambda checked=False, p=path:
                        self.open_search_file_parent_in_launch(p))
                else:
                    action = menu.addAction(definition['title'],
                        lambda checked=False, a=action_id, p=path, k=origin:
                        self.perform_filesystem_context_action(a, p, k))
                if action is not None:
                    if origin == 'folder' and action_id in ('cut', 'delete'):
                        action.setEnabled(self.can_delete_remote_folder(path))
                    action.setIcon(context_action_icon(action_id))
                    action.setIconVisibleInMenu(True)
            if menu.isEmpty():
                return False
        else:
            # Imported bookmarks/apps have no context menu, even though they
            # happen to be merged into self.data['items'] for display/search.
            return False
        self.hover_timer.stop()
        self.pending_menu_item = None
        self._launch_context_menu = menu
        if origin in ('folder', 'file'):
            # One width contract for files and folders, regardless of whether
            # a menu originates in Files, Remote, or Files Exp.
            menu.setMinimumWidth(218)
            menu.setMaximumWidth(225)
            menu.triggered.connect(lambda action, m=menu:
                self._on_file_context_action_triggered(m, action))
        # Do not keep a stale Python wrapper after a cascade tool-window is
        # closed/deleted. Hover polling must not ask a deleted QMenu if visible.
        if hasattr(menu, 'aboutToHide'):
            menu.aboutToHide.connect(lambda m=menu: self._forget_launch_context_menu(m))
        if getattr(self, 'color_theme', 'dark') == 'light':
            menu.setStyleSheet(LIGHT_MENU_QSS + context_menu_spacing_qss(self.color_theme))
        elif origin in ('file', 'folder') and hasattr(menu, 'setStyleSheet'):
            menu.setStyleSheet(context_menu_spacing_qss(self.color_theme))
        menu.popup(global_pos)
        return True

    def _forget_launch_context_menu(self, menu):
        if getattr(self, '_launch_context_menu', None) is menu:
            self._launch_context_menu = None

    def delete_expanded_selected_paths(self):
        """Delete key uses exactly the same guarded recycle-bin action as right-click.

        Multiple selected files use the shared batch confirmation. Never
        interpret an unselected current/hovered row as permission to delete.
        """
        view = self.expanded_view
        tree = view.middle.tree
        if (not view.isVisible() or
                tree.state() == QAbstractItemView.State.EditingState):
            return False
        paths = view.middle_selected_paths()
        if not paths:
            return False
        if len(paths) > 1:
            self.perform_filesystem_batch_action('delete', paths)
        else:
            path = Path(paths[0])
            self.perform_filesystem_context_action(
                'delete', str(path), 'folder' if path.is_dir() else 'file')
        return True

    def copy_expanded_selected_paths(self, *, cut=False):
        paths = self.expanded_view.middle_selected_paths()
        if not paths:
            return False
        self.perform_filesystem_batch_action('cut' if cut else 'copy', paths)
        return True

    def perform_filesystem_batch_action(self, action_id, paths):
        """Apply common file actions to the entire real-path selection."""
        # Keep frameless Qt.Tool visible across Windows recycle-bin focus loss.
        # Retain the guard until the queued view refresh has settled.
        if action_id == 'delete':
            self._filesystem_dialog_depth = getattr(self, '_filesystem_dialog_depth', 0) + 1
        try:
            # Context source was validated when the menu opened; check again.
            targets = []
            seen = set()
            for value in paths:
                source = Path(value)
                if source.is_symlink():
                    raise ValueError('リンクの一括操作には対応していません')
                path = source.resolve(strict=True)
                if not (path.is_file() or path.is_dir()):
                    raise ValueError('通常のファイル・フォルダーのみ操作できます')
                key = str(path).casefold()
                if key not in seen:
                    seen.add(key)
                    targets.append(path)
            if not targets:
                return
            if action_id in ('cut', 'delete'):
                forbidden = [p for p in targets if p.is_dir() and not self.can_delete_remote_folder(p)]
                if forbidden:
                    raise ValueError('登録フォルダー・保護対象は移動・削除できません: ' + str(forbidden[0]))
            self._clear_previous_paste_feedback()
            if action_id in ('copy_full_path', 'copy_file_name'):
                lines = (str(path) if action_id == 'copy_full_path' else path.name
                         for path in targets)
                QApplication.clipboard().setText('\n'.join(lines))
                self.footer.setText(f'{len(targets)}件の{ "フルパス" if action_id == "copy_full_path" else "ファイル名" }をコピーしました')
            elif action_id in ('copy', 'cut'):
                mime = QMimeData()
                mime.setUrls([QUrl.fromLocalFile(str(path)) for path in targets])
                mime.setData('application/x-qt-windows-mime;value="Preferred DropEffect"',
                             (2 if action_id == 'cut' else 1).to_bytes(4, 'little'))
                QApplication.clipboard().setMimeData(mime)
                self.footer.setText(f'{len(targets)}件を{"切り取り" if action_id == "cut" else "コピー"}しました')
            elif action_id == 'delete':
                current_before_delete = self.expanded_view.current_directory()
                listed = '\n'.join('・' + p.name for p in targets[:8])
                if len(targets) > 8:
                    listed += f'\nほか {len(targets) - 8} 件'
                answer = QMessageBox.question(
                    self, '複数項目をごみ箱へ移動',
                    f'{len(targets)}件をごみ箱へ移動しますか？\n\n{listed}',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No)
                if answer != QMessageBox.StandardButton.Yes:
                    return
                finished = 0
                removed_directories = []
                with self.filesystem_progress('ごみ箱へ移動', len(targets)) as advance:
                    for path in targets:
                        advance(finished, len(targets), path.name)
                        was_directory = path.is_dir()
                        move_to_recycle_bin(path)
                        if was_directory:
                            removed_directories.append(path)
                        finished += 1
                        advance(finished, len(targets), path.name)
                self.footer.setText(f'{finished}件をごみ箱へ移動しました')
            else:
                raise ValueError('複数選択で未対応の操作です: ' + action_id)
        except (OSError, ValueError) as exc:
            self.error('複数項目を操作できませんでした: ' + str(exc))
        finally:
            if action_id == 'delete':
                # Also recover navigation on partial failure. Only successfully
                # recycled folders are removed from the tree.
                for removed in locals().get('removed_directories', ()):
                    self._after_folder_deleted(
                        str(removed),
                        previous_current=locals().get('current_before_delete'))
                    self.notify_folder_mutation(removed.parent)
                # Refresh even after a partially successful recycle batch.
                if locals().get('finished', 0) and self.expanded_view.isVisible():
                    QTimer.singleShot(0, self.expanded_view.refresh_middle)
                # Native shell activation may arrive after the API returns.
                QTimer.singleShot(650, self._finish_batch_delete_guard)

    def _finish_batch_delete_guard(self):
        self._filesystem_dialog_depth = max(
            0, getattr(self, '_filesystem_dialog_depth', 0) - 1)

    def paste_into_expanded_directory(self, *, destination_override=None):
        """Paste to the selected folder (breadcrumb only when none selected)."""
        # Local import keeps this responsibility independently testable without
        # loading Windows/PySide6; it runs before any disk-writing operation.
        from paste_destination import choose_paste_destination, AmbiguousPasteTarget
        destination_text = (destination_override if destination_override is not None
                            else self.expanded_view.current_directory())
        if not destination_text:
            return
        try:
            selected = (() if destination_override is not None else
                        self.expanded_view.middle_selected_paths()
                        if hasattr(self.expanded_view, 'middle_selected_paths') else ())
            destination = choose_paste_destination(destination_text, selected)
            clipboard = QApplication.clipboard()
            mime = clipboard.mimeData()
            sources = clipboard_sources(mime)
            move = is_cut_clipboard(mime)
            virtual = is_virtual_file_clipboard(mime) and (
                not sources or any(not src.exists() for src in sources))
            if virtual:
                names = virtual_clipboard_names(mime)
                preflight_virtual_destination(destination, names, allow_existing=True)
                existing = {entry.name.casefold(): entry for entry in destination.iterdir()}
                conflicts = [existing[name.casefold()] for name in names or ()
                             if name.casefold() in existing]
                if conflicts and not self._ask_overwrite(destination, conflicts):
                    return
                before = {p.name.casefold() for p in destination.iterdir()}
                paste_virtual_shell_items(destination, overwrite_confirmed=bool(conflicts))
                count = len(names) if names else sum(
                    p.name.casefold() not in before for p in destination.iterdir())
                self.footer.setText(f'{count}件をZIPから貼り付けました → {destination}')
            else:
                plan = (make_paste_plan(destination, sources, allow_existing=True)
                        if move else make_paste_plan(destination, sources,
                                                     allow_existing=True,
                                                     duplicate_in_place=True))
                conflicts = paste_conflicts(plan)
                if conflicts and not self._ask_overwrite(destination, conflicts):
                    return
                run_progress = getattr(self, 'paste_with_progress', None)
                if callable(run_progress):
                    count = run_progress(plan, move=move, overwrite=bool(conflicts))
                else:
                    count = paste_items(plan, move=move, overwrite=bool(conflicts))
                if move:
                    clipboard.clear()
                self.footer.setText(f'{count}件を{"移動" if move else "コピー"}しました → {destination}')
            # Only successful transfers count as pasted results. When the
            # clipboard is changed by Windows/Explorer the pending cut state
            # is automatically cleared by the common clipboard signal.
            report = getattr(self, '_record_transfer_result', None)
            if callable(report):
                if not virtual:
                    report(destination, [item.target.name for item in plan])
                else:
                    report(destination, names or ())
            # A move removes entries from the original parents as well as
            # adding them to the target. Keep all other expanded branches.
            moved_from = (moved_source_parent_directories(plan, move=True)
                          if move and not virtual else ())
            self.refresh_files_exp_directory(destination)
            # The destination gains the moved entries; each source parent loses
            # them. Reconcile both visible tree branches after a confirmed MOVE.
            if move and not virtual:
                for source_parent in moved_from:
                    if path_key(source_parent) != path_key(destination):
                        self.refresh_files_exp_directory(source_parent)
            self.expanded_view.refresh_middle()
        except AmbiguousPasteTarget as exc:
            self._warn_ambiguous_paste_target(exc)
        except (OSError, ValueError) as exc:
            DIAG.exception('EXPANDED_DIRECTORY_PASTE target=%s', destination_text)
            self.error('貼り付けできませんでした: ' + str(exc))

    def extract_all_zip(self, path):
        """Prefer Windows Explorer's wizard; supply a Qt fallback if absent."""
        self.begin_cloud_link_handoff()  # Avoid putting Windows dialog behind Qt.Tool.
        try:
            if invoke_windows_extract_all(path):
                self.footer.setText('Windowsの「すべて展開」を起動しました。展開先を確認してください')
                return
        except Exception:
            self.finish_cloud_link_handoff()
            raise
        self.finish_cloud_link_handoff()
        # The Extract All shell verb is not registered on every Windows build.
        # Use a constrained local dialog, never silently unzip on a single click.
        dialog = QDialog(self)
        dialog.setWindowTitle('すべて展開...')
        form = QVBoxLayout(dialog)
        form.addWidget(QLabel('展開先のフォルダーを指定してください。', dialog))
        folder_row = QHBoxLayout()
        destination = QLineEdit(str(default_extract_destination(path)), dialog)
        folder_row.addWidget(destination)
        browse = QPushButton('参照...', dialog)
        folder_row.addWidget(browse)
        form.addLayout(folder_row)
        show_files = QCheckBox('完了時に展開先を表示する', dialog)
        show_files.setChecked(True)
        form.addWidget(show_files)
        actions = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=dialog)
        actions.button(QDialogButtonBox.StandardButton.Ok).setText('展開')
        actions.accepted.connect(dialog.accept)
        actions.rejected.connect(dialog.reject)
        form.addWidget(actions)
        def choose_folder():
            chosen = QFileDialog.getExistingDirectory(
                dialog, '展開先フォルダー', str(Path(path).parent))
            if chosen:
                destination.setText(str(Path(chosen) / Path(path).stem))
        browse.clicked.connect(choose_folder)
        dialog.setMinimumWidth(500)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        dest_text = destination.text().strip()
        if not dest_text:
            raise ValueError('展開先を指定してください')
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            extracted = safe_extract_zip(path, dest_text)
        finally:
            QApplication.restoreOverrideCursor()
        self.footer.setText(f'ZIPを展開しました → {extracted}')
        if show_files.isChecked():
            open_file_explorer(extracted)
        if (self.expanded_view.isVisible() and
                self.expanded_view.current_directory() == str(extracted.parent)):
            self.expanded_view.refresh_middle()

    def open_search_folder_in_launch(self, folder):
        """Open a search result folder itself, using existing Files navigation."""
        return self.open_search_file_parent_in_launch(folder, directory=True)

    def open_search_file_parent_in_launch(self, filename, *, directory=False):
        """Open a search file's parent or the matched folder in Launch Files.

        The Files panel owns breadcrumb updates and the shared 100-stop
        back/forward history, so there is no second history writer.
        """
        from directory_address import directory_row

        parent = Path(filename) if directory else Path(filename).parent
        if not parent.is_dir():
            self.error('保存先フォルダーが見つかりません: ' + str(parent))
            return False

        options = self._read_expanded_options()
        targets = expanded_targets(self.data.get('items', []), options) if self.data else None
        page_index = next((index for index, page in enumerate(self.pages)
                           if page['page_id'] == options['page_id']), None)
        if not options['enabled'] or targets is None or page_index is None:
            self.error('Launch内のFilesビューが利用できません。表示設定を確認してください')
            return False

        # A QMenu action may still own the focus. Close only transient popups;
        # the launcher stays open and its filesystem navigation history lives on.
        context = getattr(self, '_launch_context_menu', None)
        if context is not None:
            context.close()
        self.close_cascade_for_main_interaction()
        self.hide_history_popup()
        self.hover_timer.stop()
        self.pending_menu_item = None
        self.stack = []
        self.selection = None
        self.checked.clear()
        self.page_id = options['page_id']
        self.tabs.blockSignals(True)
        try:
            self.tabs.setCurrentIndex(page_index)
        finally:
            self.tabs.blockSignals(False)

        # When coming from a search, no Files pane is shown yet. Prepare the
        # target BEFORE render() activates it: do not record an unrelated
        # default/previous first-column folder as an intermediate history stop.
        self.expanded_view.path = [directory_row(str(parent))]
        if self.view_mode != 'expanded':
            self.set_view_mode('expanded')
        self.search.clear()
        self.render()
        if not self.expanded_view.isVisible():
            self.error('Launch内のFilesビューを開けませんでした')
            return False
        # Reuse the ordinary internal folder navigation (focus + breadcrumb).
        # Its refresh is deduplicated by DirectoryNavigationHistory.record().
        if not self.expanded_view.go_to_directory(str(parent)):
            self.error('Launch内でフォルダーを開けませんでした: ' + str(parent))
            return False
        # The destination list has been freshly populated. Highlight the
        # original search hit (not its parent or the first item), and scroll
        # it into view without changing directory history again.
        selected = (self.expanded_view.select_middle_file(filename)
                    if not directory else False)
        self.footer.setText(('Launch内でファイルを選択しました: ' + str(filename))
                            if selected else
                            ('Launch内でフォルダーを開きました: ' + str(parent)))
        return True

    def perform_filesystem_context_action(self, action_id, target, kind):
        """Display belongs to JSON; filesystem work belongs to OS action helpers."""
        try:
            path = Path(target)
            # Index/search contents can change after a context menu opens.
            if not path.exists():
                self.error('ファイルまたはフォルダーが見つかりません: ' + str(path))
                return
            if (kind == 'file' and not path.is_file()) or (kind == 'folder' and not path.is_dir()):
                self.error('対象の種類が変更されています: ' + str(path))
                return
            if kind == 'folder' and action_id in ('cut', 'delete'):
                if not self.can_delete_remote_folder(path):
                    self.error('登録フォルダー・ドライブ・保護対象の親フォルダーは移動・削除できません: ' + str(path))
                    return
            # Copy/cut/delete/rename (and other file actions) start a new
            # interaction: do not leave the previous paste's teal rows visible.
            # Clipboard cut state is separately controlled by the OS clipboard.
            reset = getattr(self, '_clear_previous_paste_feedback', None)
            if callable(reset):
                reset()
            if action_id in ('copy', 'cut'):
                # QMimeData local file URLs interoperate with Explorer and with
                # the existing directory paste button. Mark cut as MOVE, not COPY.
                mime = QMimeData()
                mime.setUrls([QUrl.fromLocalFile(str(path.resolve()))])
                mime.setData('application/x-qt-windows-mime;value="Preferred DropEffect"',
                             (2 if action_id == 'cut' else 1).to_bytes(4, 'little'))
                QApplication.clipboard().setMimeData(mime)
                self.footer.setText(f'{path.name} を{"切り取り" if action_id == "cut" else "コピー"}しました')
                # A Remote/Exp clipboard action is finished. Do not leave the
                # Filesリスト cascade or parent context window on screen.
                def close_clipboard_menus():
                    transient = getattr(self, '_launch_context_menu', None)
                    if transient is not None:
                        transient.close()
                    if (getattr(self, '_remote_folder_opener', None) is not None or
                            getattr(self, '_remote_folder_root_menu', None) is not None):
                        self.close_remote_folder_menu()
                if (getattr(self, '_remote_folder_opener', None) is not None or
                        getattr(self, '_remote_folder_root_menu', None) is not None):
                    QTimer.singleShot(0, close_clipboard_menus)
            elif action_id == 'refresh_directory' and kind == 'folder':
                self.refresh_folder_information(path)
            elif action_id == 'delete':
                # A deleted current folder must not be resolved again AFTER
                # the OS has removed it.  Remember its old breadcrumb now.
                current_before_delete = self.expanded_view.current_directory()
                visible_menu = self._directory_menu_for_path(path.parent)
                self.hover_timer.stop()
                self.pending_menu_item = None
                self._filesystem_dialog_depth = getattr(self, '_filesystem_dialog_depth', 0) + 1
                try:
                    answer = QMessageBox.question(
                        self, 'ごみ箱へ移動',
                        f'次の{"フォルダー" if kind == "folder" else "ファイル"}を削除しますか？\n\n{path}\n\n'
                        'Windowsのごみ箱へ移動します。ごみ箱に対応しない場所ではOSの警告を確認してください。',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No)
                    if answer != QMessageBox.StandardButton.Yes:
                        return
                    with self.filesystem_progress('ごみ箱へ移動', 1) as advance:
                        advance(0, 1, path.name)
                        move_to_recycle_bin(path)
                        advance(1, 1, path.name)
                finally:
                    # Windows native recycle-bin and Qt.Tool focus events can
                    # arrive AFTER the modal dialog returns. The previous
                    # immediate decrement dismissed the whole launcher.
                    QTimer.singleShot(900, lambda: setattr(
                        self, '_filesystem_dialog_depth',
                        max(0, getattr(self, '_filesystem_dialog_depth', 0) - 1)))
                # Move the breadcrumb and Files Exp to the real parent BEFORE
                # refreshing/rebuilding any file views or popup columns.
                if kind == 'folder':
                    self._after_folder_deleted(
                        str(path), previous_current=current_before_delete)
                # A delete refresh does not carry over old paste highlights.
                # Do not reopen a popup for a directory that was just removed.
                # Keep the refreshed parent as the Files breadcrumb.
                deleted_current_folder = (kind == 'folder' and
                    current_before_delete is not None and
                    (path_key(current_before_delete) == path_key(path) or
                     path_key(current_before_delete).startswith(path_key(path).rstrip('/') + '/')))
                if deleted_current_folder:
                    context_menu = getattr(self, '_launch_context_menu', None)
                    if context_menu is not None:
                        context_menu.close()
                elif visible_menu is not None:
                    # The row context QMenu may still own Qt focus when the
                    # modal confirmation exits. Close it FIRST so the new
                    # folder column is not hidden by its subsequent cleanup.
                    context_menu = getattr(self, '_launch_context_menu', None)
                    if context_menu is not None:
                        context_menu.close()
                    # Never skip the visual confirmation just because the old
                    # Qt.Tool popup temporarily became invisible in the dialog.
                    QTimer.singleShot(0, lambda m=visible_menu:
                                      self.refresh_deleted_directory(m))
                else:
                    # Files in the expanded middle panel have no classic
                    # CascadeMenu; refresh that live panel rather than losing
                    # it through a main-list render during shell deactivation.
                    if (getattr(self, 'expanded_view', None) is not None and
                            self.expanded_view.isVisible() and
                            self.expanded_view.current_directory() == str(path.parent)):
                        QTimer.singleShot(0, self.expanded_view.refresh_middle)
                    elif not deleted_current_folder:
                        self.render()
                if self.file_index_settings.get('enabled', True) and not self.file_index_busy:
                    QTimer.singleShot(0, lambda: self.refresh_file_index(manual=False))
                self.footer.setText(f'削除を完了しました: {path.name}')
            elif action_id in ('copy_full_path', 'copy_path'):
                QApplication.clipboard().setText(str(path))
            elif action_id == 'copy_file_name':
                QApplication.clipboard().setText(path.name)
            elif action_id == 'copy_cloud_link':
                # The provider's native copy-link dialog is NOT a child of
                # this Qt.Tool window. Allow it above Launch temporarily;
                # keep Launch visible and preserve its Files/navigation state.
                self.begin_cloud_link_handoff()
                try:
                    invoked = request_native_copy_link(path)
                    if invoked:
                        self.footer.setText('Windowsへリンクのコピーを依頼しました。コピー結果・共有範囲をご確認ください')
                    else:
                        # Older shell APIs cannot enumerate all Windows 11
                        # cloud-provider verbs; Explorer remains the fallback.
                        select_in_explorer(path)
                        self.footer.setText('エクスプローラーから「リンクのコピー」を選択してください')
                except Exception:
                    self.finish_cloud_link_handoff()
                    raise
            elif action_id == 'extract_all' and kind == 'file':
                if not is_extractable_zip(path):
                    raise ValueError('すべて展開はZIPファイルのみ対象です')
                self.extract_all_zip(path)
            elif action_id == 'open_with' and kind == 'file':
                # The legacy topmost Tool window must yield to Windows' native
                # chooser. A normal keep-visible window can stay behind it.
                if getattr(self, 'dismiss_on_outside_click', True):
                    self.dismiss()
                open_with_windows_dialog(path)
            elif action_id == 'open_parent_folder' and kind == 'file':
                open_parent_folder(path)
            elif action_id == 'open_parent_terminal' and kind == 'file':
                open_parent_powershell(path)
            elif action_id == 'run_with_pause' and kind == 'file':
                run_script_with_pause(path)
            elif action_id == 'open_explorer':
                open_file_explorer(path)
            elif action_id == 'open_terminal':
                open_folder_terminal(path)
            elif action_id == 'properties':
                # FRB Launch is a permanently topmost Qt.Tool window. Native
                # Native property sheets are not topmost. In keep-visible mode,
                # drop Launch's topmost z-order until the user returns; in the
                # legacy hide mode retain the original dismiss behavior.
                if getattr(self, 'dismiss_on_outside_click', True):
                    self.dismiss()
                    show_windows_properties(path)
                else:
                    self.begin_cloud_link_handoff()
                    try:
                        show_windows_properties(path)
                    except Exception:
                        self.finish_cloud_link_handoff()
                        raise
            elif action_id == 'git_commit_from_zip':
                self.git_commit_using_filename(path)
            elif action_id == 'rename':
                name, accepted = QInputDialog.getText(self, '名前の変更', '新しい名前:', text=path.name)
                if not accepted or name == path.name:
                    return
                if kind == 'file' and Path(name).suffix.casefold() != path.suffix.casefold():
                    answer = QMessageBox.question(
                        self, '拡張子の変更',
                        'ファイルの拡張子が変わります。名前を変更しますか？',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No)
                    if answer != QMessageBox.StandardButton.Yes:
                        return
                new_path = rename_file_or_folder(path, name)
                if kind == 'folder':
                    for panel in getattr(self, 'files_exp_panels', lambda: tuple(
            panel for panel in (
                getattr(getattr(self, 'remote_window', None), 'files_exp_panel', None),
                getattr(getattr(self, 'expanded_view', None), 'embedded_files_exp', None))
            if panel is not None))():
                        panel.reflect_external_folder_rename(str(path), str(new_path))
                    self.notify_folder_mutation(path.parent)
                # Source columns may hold the old path; safely close them and
                # refresh the current page/search result after a successful rename.
                self.close_cascade_for_main_interaction()
                self.render()
                if self.file_index_settings.get('enabled', True) and not self.file_index_busy:
                    QTimer.singleShot(0, lambda: self.refresh_file_index(manual=False))
            else:
                raise ValueError('未対応の操作: ' + str(action_id))
        except (OSError, ValueError, RuntimeError) as exc:
            DIAG.exception('FILESYSTEM_CONTEXT action=%s target=%s', action_id, target)
            self.error('操作を実行できませんでした: ' + str(exc))
        finally:
            # Menus are command launchers, not persistent status displays.
            # Keep inline editors alive: they close on their own commit.
            closer = getattr(self, 'close_finished_file_context_menus', None)
            if action_id != 'rename' and callable(closer):
                QTimer.singleShot(0, closer)

    def git_commit_using_filename(self, selected_path):
        """Use any selected file name as the message; commit repository changes."""
        try:
            if not Path(selected_path).is_file():
                raise ValueError('存在するファイルだけが対象です（フォルダーは対象外）')
            options = read_git_commit_options(GIT_COMMIT_OPTIONS)
            preview = git_commit_preview(options)
            # QInputDialog#setMinimumWidth only widened the outer dialog on
            # some Windows Qt styles: the actual QLineEdit stayed ~150px.
            # Give the editor its OWN minimum width in a normal QDialog.
            dialog = QDialog(self)
            dialog.setWindowTitle('Gitコミットメッセージ')
            form = QVBoxLayout(dialog)
            form.setContentsMargins(14, 12, 14, 12)
            form.setSpacing(8)
            form.addWidget(QLabel('選択ファイルの名前（編集できます）:', dialog))
            message_editor = QLineEdit(dialog)
            message_editor.setText(Path(selected_path).name)
            message_editor.setMinimumWidth(360)  # The real text input, not its frame.
            message_editor.selectAll()
            form.addWidget(message_editor)
            actions = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
                dialog)
            actions.accepted.connect(dialog.accept)
            actions.rejected.connect(dialog.reject)
            form.addWidget(actions)
            dialog.setMinimumWidth(480)
            dialog.resize(500, dialog.sizeHint().height())
            accepted = dialog.exec() == QDialog.DialogCode.Accepted
            message = message_editor.text()
            if not accepted:
                return
            if not message.strip():
                raise ValueError('コミットメッセージは空にできません')
            visible_changes = '\n'.join(preview['changes'][:12])
            if len(preview['changes']) > 12:
                visible_changes += f'\n...ほか {len(preview["changes"])-12} 件'
            question = QMessageBox(self)
            question.setIcon(QMessageBox.Icon.Question)
            question.setWindowTitle('Gitコミットの確認')
            question.setText('現在のGit作業ツリーの変更をコミットしますか？')
            question.setInformativeText(
                f'リポジトリ: {preview["repository"]}\n'
                f'コミットメッセージ: {message}\n'
                f'変更候補: {len(preview["changes"])} 件\n\n'
                f'{visible_changes}\n\n'
                '※ 選択ファイルはメッセージの元になるだけで、コミット対象の限定・追加はしません。\n'
                + ('未追跡ファイルも対象です。' if preview['include_untracked']
                   else '未追跡ファイルは追加しません。'))
            question.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            question.setDefaultButton(QMessageBox.StandardButton.No)
            if question.exec() != QMessageBox.StandardButton.Yes:
                return
            committed = commit_tracked_changes(preview['repository'], message,
                                               include_untracked=preview['include_untracked'])
            QMessageBox.information(self, 'Gitコミット完了',
                                    'コミットしました。\n' + committed)
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
            DIAG.exception('GIT_COMMIT_FROM_FILENAME path=%s', selected_path)
            self.error('Gitコミットできませんでした: ' + str(exc))

    def contextMenuEvent(self, event):
        # The root QWidget cannot distinguish page content from its tab,
        # search box, footer or reordering overlay. The ONLY background menu
        # entry point is the QTreeWidget viewport guard above.
        event.accept()

    def open_target(self,target,browser="",profile=""):
        if browser.lower() == 'chrome' and not profile:windows.open_chrome(target);return
        if browser.lower() in ('chrome','edge'):
            windows.open_browser(target,browser.lower(),profile)
            return
        if not windows.IS_WINDOWS:raise RuntimeError('起動操作はWindowsで利用できます')
        if target.lower().startswith('shell:'):
            import subprocess
            subprocess.Popen(['explorer.exe',target])
        else:
            # ShellExecute's default current directory is not guaranteed to
            # be the script's directory (especially from an indexed search).
            # Pass it explicitly for batch files; keep other Open behavior.
            path = Path(target)
            if path.suffix.casefold() in ('.bat', '.cmd') and path.is_file():
                os.startfile(target, cwd=str(path.resolve().parent))
            else:
                os.startfile(target)

    def expander(self, values=None):
        ex=Expander(self.data,QApplication.clipboard().text(),values or {})
        ex.values.update(launch_data=str(CONFIG),launch_dir=str(ROOT),launch_home=str(LAUNCH_HOME),launch_scripts=str(LAUNCH_HOME/'scripts'))
        return ex

    def execute(self,row,values=None):
        DIAG.info('ITEM id=%s title=%s busy=%s',row.get('item_id'),row.get('title'),self.busy)
        if self.busy:return
        # In Three-layer mode, URLs (including deep bookmark menu actions)
        # open inside Launch. Files, scripts and classic-mode actions are intact.
        if self.open_bookmark_web_view(row):
            return
        try:
            ex=self.expander(values)
            # Resolve all values before any side effects.
            self.queue=[]
            studio_root = getattr(ex, 'values', {}).get('studio_root', '')
            for raw in row.get('launch_actions',[]):
                step={k:([ex.expand(a) for a in val] if k=='launch_arguments' else ex.expand(val) if isinstance(val,str) else val) for k,val in raw.items()}
                # Directly registered local files must behave exactly like
                # file-index hits and expanded-folder files. In particular, a
                # Studio-managed JSON opens via --open-json instead of the OS
                # file association. Authored Run/browser actions remain intact.
                self.queue.extend(file_index.route_registered_open_step(step, studio_root))
            self.busy=True;DIAG.info('QUEUE steps=%s',len(self.queue))
            hide_after_launch = getattr(self, 'dismiss_on_outside_click', True)
            if should_start_before_dismiss(self.queue):
                # GUI children inherit foreground permission when started
                # while Launch is active, regardless of its display mode.
                self._foreground_handoff_pending = True
                DIAG.info('FOREGROUND_HANDOFF starting GUI child before UI transition')
                self.next_step()
                if self.busy and hide_after_launch:
                    self.dismiss()
            else:
                self._foreground_handoff_pending = False
                if hide_after_launch:
                    # Preserve the original Tool-mode hide-then-launch delay.
                    self.dismiss()
                    QTimer.singleShot(180, self.next_step)
                else:
                    # Normal-window mode stays visible. Let Qt close any
                    # context menu first, then run without an extra delay.
                    QTimer.singleShot(0, self.next_step)
        except Exception as e:
            DIAG.exception('PREPARE failed');self.error(e)

    def next_step(self):
        if not self.queue:self.busy=False;DIAG.info('COMPLETE');return
        step=self.queue.pop(0)
        try:
            kind=step['launch_action_type']
            DIAG.info('STEP type=%s remaining=%s',kind,len(self.queue))
            if kind in {'SendKey','ClipboardCopy'}:
                if kind=='SendKey':windows.restore(self.target)
                QApplication.clipboard().setText(step.get('launch_text',''))
                if kind=='SendKey':windows.paste(self.target)
            elif kind=='Open':
                if step.get('launch_browser_profile'):self.open_target(step['launch_target'],step.get('launch_browser',''),step['launch_browser_profile'])
                elif step.get('launch_browser'):self.open_target(step['launch_target'],step['launch_browser'])
                else:self.open_target(step['launch_target'])
            elif kind=='Run':
                program=step['launch_program'];args=studio_launch_arguments(program, step.get('launch_arguments',[]))
                # BAT/CMD always starts in its own folder, including an
                # authored cmd.exe /d /c script. Unrelated Run steps retain
                # their configured working directories.
                cwd=(batch_script_working_directory(program,args)
                     or step.get('launch_working_directory') or str(ROOT))
                args,transcript=wifi_transcript_arguments(program,args,STATE)
                DIAG.info('RUN program=%s cwd=%s console=%s wait=%s transcript=%s',program,cwd,step.get('launch_show_console',False),step.get('launch_wait_for_exit',False),transcript)
                self.proc = start_process(program, args, cwd, step.get('launch_show_console',False))
                DIAG.info('PROCESS started pid=%s',getattr(self.proc,'pid',None))
                if getattr(self, '_foreground_handoff_pending', False):
                    self._foreground_handoff_pending = False
                    try:
                        granted = windows.allow_child_foreground(getattr(self.proc, 'pid', None))
                        DIAG.info('FOREGROUND_HANDOFF pid=%s granted=%s',
                                  getattr(self.proc, 'pid', None), granted)
                    except OSError as focus_error:
                        # The child has already started. Foreground permission
                        # is best effort: never report the launch as failed.
                        DIAG.warning('FOREGROUND_HANDOFF denied: %s', focus_error)
                if step.get('launch_wait_for_exit'):
                    self.timedout=False
                    self.process_started=time.monotonic()
                    self.process_timeout=int(step.get('launch_timeout_ms',30000))/1000
                    if not hasattr(self,'process_timer'):
                        self.process_timer=QTimer(self)
                        self.process_timer.setInterval(100)
                        self.process_timer.timeout.connect(self.poll_process)
                    self.process_timer.start();return
            QTimer.singleShot(100,self.next_step)
        except Exception as e:
            DIAG.exception("STEP failed");self.fail(str(e))

    def poll_process(self):
        code=self.proc.poll()
        if code is None:
            if not self.timedout and time.monotonic()-self.process_started >= self.process_timeout:
                self.queue=[];self.timedout=True
                self.error('タイムアウトしました。後続処理を中止し、実行中の処理が終了するまで待ちます')
            return
        DIAG.info('PROCESS exited code=%s timedout=%s',code,self.timedout)
        prune_diagnostics()
        self.process_timer.stop()
        if self.timedout:self.busy=False;return
        if code!=0:self.fail(f'外部処理の終了コード: {code}（トレイの「ログフォルダーを開く」で詳細を確認）')
        else:self.next_step()

    def fail(self,message):
        self._foreground_handoff_pending = False
        self.queue=[];self.busy=False
        if hasattr(self,'process_timer'):self.process_timer.stop()
        self.error(message)

    def closeEvent(self,event):event.ignore();self.dismiss()
    def quit(self):
        self._file_index_cancel.set()
        if self.apps_proc:
            self.apps_proc.kill();self.apps_proc.wait();self.apps_output.unlink(missing_ok=True)
        for hotkey_id in self.registered_menu_hotkeys:
            windows.unhotkey(int(self.winId()), hotkey_id)
        windows.unhotkey(int(self.winId()));self.dismiss();self.tray.hide();QApplication.quit()


def main():
    requested_jump_item = jump_list.requested_item(sys.argv[1:])
    # Set an explicit identity BEFORE creating any taskbar windows/Jump Lists.
    try:
        jump_list.set_process_app_id()
    except Exception:
        DIAG.exception('JUMP_LIST app identity unavailable')
    # Qt must not interpret our Jump List switch as a Qt command-line option.
    qt_args = [arg for arg in sys.argv if not arg.startswith(jump_list.IPC_SWITCH)]
    app=QApplication(qt_args);app.setQuitOnLastWindowClosed(False)
    # Safety net for scrollbars added in future Qt widgets/menus. Existing
    # themed views override the track color to match their own surface.
    app.setStyleSheet(MAIN_LIST_SCROLLBAR_QSS)
    app.setWindowIcon(application_icon())
    # One user/session-local instance, independent of its installation directory.
    name='FRBLaunch-'+os.environ.get('USERNAME',os.environ.get('USER','default'))
    lock=QLockFile(str(STATE/'instance.lock'));lock.setStaleLockTime(0)
    if not lock.tryLock(0):
        payload = (jump_list.ipc_command(requested_jump_item)
                   if requested_jump_item else b'show\n')
        client=QLocalSocket();client.connectToServer(name)
        if client.waitForConnected(1500):
            client.write(payload)
            client.waitForBytesWritten(1000)
        return 0
    QLocalServer.removeServer(name)
    server=QLocalServer()
    if not server.listen(name):raise RuntimeError(server.errorString())
    window=Launcher()
    # Prime Qt WebEngine before any launcher window is shown.  Unlike a
    # delayed on-screen warm-up, this avoids shifting the first-use flash
    # from the Browser click to the already-visible Files screen.
    window.prepare_browser_before_first_show()
    # CLaunch-style: double-click empty desktop wallpaper to open the launcher.
    # Keep a strong reference for the whole Qt event loop and release on exit.
    # Desktop double-click support is optional: a Windows API/COM error must
    # never prevent the launcher itself from starting (tray/hotkey still work).
    desktop_click = None
    def open_from_desktop(click=None):
        DIAG.info('DESKTOP_OPEN_CALLBACK visible_before=%s minimized=%s',
                  window.isVisible(), window.isMinimized())
        source_foreground = windows.foreground()
        was_hidden = not window.isVisible() or window.isMinimized()
        if was_hidden:
            window.summon()  # Tray-hidden and native-minimized states.
        elif not window.dismiss_on_outside_click or getattr(window, 'remote_on_desktop_double_click', False):
            # Ordinary-window mode: desktop double-click is an explicit summon,
            # even when the launcher is already visible behind another app.
            # Never call summon() here; that toggles a visible window off.
            window.raise_()
            window.activateWindow()
        else:
            # Legacy always-on-top mode already has a visible launcher.
            return
        # Qt can change foreground while showing/raising the window. Record
        # both sides of that operation, but NEVER trust an arbitrary window
        # which becomes foreground later in one of the delayed callbacks.
        after_show = windows.foreground()
        expected_foreground = (source_foreground if after_show == source_foreground
                               else (source_foreground, after_show))
        # Explorer received the final mouse event. Give Windows time to
        # finish it before requesting keyboard focus for the launcher.
        # A visible normal window must retain its current Files navigation;
        # restore_last_current() is only needed after a hidden-window summon.
        def complete_desktop_open(reason, restore):
            # No newer mouse/keyboard input is allowed after the verified
            # desktop gesture.  In particular, don't reactivate Launch over
            # Chrome after the user has actively returned to Chrome.
            if click is not None and not windows.desktop_click_still_last_input(click.tick):
                DIAG.info('DESKTOP_ACTIVATE_CANCELLED reason=%s last_input_changed', reason)
                return
            # The first pass restores saved focus. The retry must not
            # overwrite navigation the user has already begun via the remote.
            restore_on_pass = (restore and reason == 'desktop_first'
                               if getattr(window, 'remote_on_desktop_double_click', False)
                               else restore)
            window.restore_keyboard_focus(
                expected_foreground, reason, restore_current=restore_on_pass,
                **({'desktop_input_hwnd': click.view} if click is not None else {}))
            if not window.dismiss_on_outside_click and window.isVisible():
                # Explicit native Z-order repair.  Qt.raise_() and focus
                # activation are separate operations on Windows; background
                # Chrome/Explorer can otherwise visually cover the Launcher.
                raised = windows.raise_normal_window(int(window.winId()))
                DIAG.info('DESKTOP_ZORDER reason=%s raised=%s active=%s foreground=%s',
                          reason, raised, window.isActiveWindow(), windows.foreground())
            # One popup per desktop gesture, after the first native activation
            # pass. Do not reopen after the user has begun another operation.
            if reason == 'desktop_first' and getattr(window, 'remote_on_desktop_double_click', False):
                point = (QPoint(click.x, click.y) if click is not None else QCursor.pos())
                window.show_remote_at(point)

        for delay, reason in ((0, 'desktop_first'), (120, 'desktop_retry')):
            QTimer.singleShot(delay, lambda r=reason, restore=was_hidden:
                              complete_desktop_open(r, restore))
        DIAG.info('DESKTOP_OPEN_RESULT visible=%s active=%s',
                  window.isVisible(), window.isActiveWindow())
        QTimer.singleShot(400, lambda: DIAG.info(
            'DESKTOP_OPEN_AFTER_400MS visible=%s active=%s foreground=%s',
            window.isVisible(), window.isActiveWindow(), windows.foreground()))
    def launcher_surface_visible():
        # Folder cascades are independent Qt.Tool windows. If the main Tool
        # window is temporarily hidden by a native modal operation, the mouse
        # hook must still consider the surviving cascade dismissible.
        if window.isVisible():
            return True
        menu = getattr(window, 'menu', None)
        try:
            return menu is not None and menu.isVisible()
        except RuntimeError:
            # Qt may have destroyed a column whose Python wrapper still exists.
            return False

    def remote_folder_popup_visible():
        # The new filesystem columns are Qt.Tool windows, not Qt.Popup.
        # They must close on an outside click in either main window mode.
        for name in ('_remote_folder_root_menu', '_remote_folder_opener'):
            candidate = getattr(window, name, None)
            if candidate is not None:
                try:
                    if candidate.isVisible():
                        return True
                except RuntimeError:
                    pass  # A native popup may have just been destroyed.
        return False

    def remote_visible():
        remote = getattr(window, 'remote_window', None)
        try:
            return remote is not None and remote.isVisible()
        except RuntimeError:
            return False

    def remote_page_popup_visible():
        page = getattr(window, '_remote_page_menu', None)
        try:
            return page is not None and page.isVisible()
        except RuntimeError:
            return False

    def dismiss_from_outside_click():
        # The native hook sees desktop/other-app clicks even when a no-focus
        # Remote Tool window generates no Qt activation change.  One rule:
        # Remote and Launcher now share ONE persisted outside-click policy.
        # Keep-visible retains both surfaces when another app is clicked.
        if (getattr(window, '_filesystem_dialog_depth', 0)
                or getattr(window, '_cloud_link_handoff', False)
                or QApplication.activeModalWidget() is not None):
            return
        if remote_visible():
            if window.dismiss_on_outside_click:
                DIAG.info('REMOTE_OUTSIDE_CLICK_HIDE')
                window.hide_remote()
                if launcher_surface_visible():
                    window.dismiss()
            return
        if remote_folder_popup_visible() or remote_page_popup_visible():
            DIAG.info('REMOTE_POPUP_OUTSIDE_CLICK_CLOSE')
            window.close_remote_folder_menu()
            window.close_remote_page_menu()
            return
        if launcher_surface_visible() and window.dismiss_on_outside_click:
            DIAG.info('OUTSIDE_CLICK_DISMISS')
            window.dismiss()

    try:
        desktop_click = DesktopDoubleClick(
            open_from_desktop, DIAG,
            on_outside_click=dismiss_from_outside_click,
            is_launcher_visible=lambda: (remote_visible() or remote_folder_popup_visible()
                                         or remote_page_popup_visible()
                                         or (launcher_surface_visible()
                                             and window.dismiss_on_outside_click)),
        )
        DIAG.info('DESKTOP_DOUBLE_CLICK_HOOK active=%s', desktop_click.start())
    except Exception:
        DIAG.exception('DESKTOP_DOUBLE_CLICK_HOOK unavailable; launcher will keep running')
        if desktop_click is not None:
            try:
                desktop_click.stop()
            except Exception:
                DIAG.exception('DESKTOP_DOUBLE_CLICK_HOOK cleanup failed')
        desktop_click = None
    pending_ipc = {}  # Keep sockets alive until the complete message arrives.

    def finish_ipc(sock):
        if sock not in pending_ipc:
            return
        payload = bytes(pending_ipc[sock]) + bytes(sock.readAll())
        pending_ipc.pop(sock, None)
        sock.disconnectFromServer()
        sock.deleteLater()
        try:
            action, item_id = jump_list.parse_ipc_command(payload)
            if action == 'show-menu':
                window.summon_menu(item_id)  # Validate id/page/enabled; never execute.
            elif not window.isVisible() or window.isMinimized():
                window.summon()
            else:
                window.raise_();window.activateWindow()
        except (ValueError, UnicodeError):
            DIAG.warning('JUMP_LIST invalid IPC command rejected')

    def wake():
        while server.hasPendingConnections():
            sock = server.nextPendingConnection()
            if not sock:
                continue
            pending_ipc[sock] = bytearray()
            def receive(socket=sock):
                if socket not in pending_ipc:
                    return
                pending_ipc[socket].extend(bytes(socket.readAll()))
                if b'\n' in pending_ipc[socket] or len(pending_ipc[socket]) > 2048:
                    finish_ipc(socket)
            sock.readyRead.connect(receive)
            sock.disconnected.connect(lambda socket=sock: finish_ipc(socket))
    server.newConnection.connect(wake)
    if requested_jump_item:
        QTimer.singleShot(0, lambda: window.summon_menu(requested_jump_item))
    # Initial registration was scheduled when Launcher first read its Data JSON.
    # A Jump List selection only relays the item id to this resident process.
    if '--preview' in sys.argv:window.summon()
    try:
        result=app.exec()
    finally:
        if desktop_click is not None:
            desktop_click.stop()
        server.close();lock.unlock()
    return result

if __name__=='__main__':
    try:sys.exit(main())
    except Exception:
        logging.exception('Startup failed')
        DIAG.exception('Startup failed')
        if QApplication.instance():QMessageBox.critical(None,'FRB Launch','起動に失敗しました。LOCALAPPDATA/FRBLaunch/error.logを確認してください。')
        raise
