import sys
import os
import json
from html import escape as html_escape
import sqlite3
import logging
import time
import threading
import subprocess
from pathlib import Path
from ctypes import wintypes
import ctypes
import math
from PySide6.QtCore import Qt, QTimer, QSettings, QEvent, QLockFile, QDir, QRectF, QRect, QPoint, QPointF, QSize, QObject, Signal, QMimeData, QUrl
from PySide6.QtGui import QActionGroup, QIcon, QPixmap, QPainter, QColor, QBrush, QKeyEvent, QShortcut, QKeySequence, QCursor, QAction, QPainterPath, QRegion, QPen, QFont, QLinearGradient
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLineEdit, QTabBar, QTreeWidget, QTreeWidgetItem, QMenu, QSystemTrayIcon, QFileIconProvider, QMessageBox, QFileDialog, QDialog, QLabel, QHBoxLayout, QDialogButtonBox, QPushButton, QWidgetAction, QAbstractItemView, QHeaderView, QFrame, QInputDialog, QStyle, QSizePolicy, QToolButton)
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtCore import QFileInfo
from file_drag import ExternalFileDragTree, begin_file_copy_drag
from file_drag_paths import file_path_for_drag
from core import load, Expander, searchable_rows, column_filter_match, join_selection_values
from search_matching import matches_search_text, matches_choice_search
from ime_input import initialize_halfwidth_english
from search_result_order import display_columns, sort_search_pairs
from selection_scope import update_visible_checks
from navigation_wrap import next_wrapped, move_tree_selection, next_page_ring_target
from menu_wheel import wheel_motion, wheel_neighbor
from wheel_adaptive import can_follow_at_edge
from bookmark_cursor_follow import cursor_target
from view_navigation_history import ViewNavigationHistory
from browser_nav_icons import browser_navigation_icon
from search_history import SearchHistory, normalize_keyword
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
from file_transfer_visual import transfer_state, pasted_paths_for, path_key
from context_menu_resolver import resolve_context_target
from context_menu_config import load_context_menus, visible_context_entries
from context_menu_actions import (show_windows_properties, open_file_explorer, open_parent_folder,
                                  open_folder_terminal, open_parent_powershell, run_script_with_pause, rename_file_or_folder, move_to_recycle_bin, sort_browser_entries,
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
from desktop_double_click import DesktopDoubleClick

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
                                                  backupCount=2, encoding='utf-8')], level=logging.WARNING)
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
        # A search belongs to one open column, not to the launcher's global search.
        # AppCascadeMenu intentionally keeps its existing global-search behavior.
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
        self._right_context_row = None
        # A separate context QMenu must not erase the selected row in the
        # launcher-owned tool column while the popup temporarily owns focus.
        self._context_highlight_action = None
        self._transfer_data_changed_connected = False

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
        if self._folder_row(action) is not None:
            self._queue_folder_single_click(action)
        elif action in self.openers:
            self.openers[action]('keyboard')
        else:
            action.trigger()

    def _scroll_double_clicked(self, item, column):
        action = self._scroll_item_action(item)
        row = self._folder_row(action)
        if row is None:
            return
        self.folder_click_timer.stop()
        self._folder_click_action = None
        self._folder_double_click_row = row

    def _scroll_hover(self, item):
        if item is None:
            self.hover_timer.stop()
            return
        action = self._scroll_item_action(item)
        if action is self.activeAction():
            return
        self.scroll_tree.setCurrentItem(item)
        # Do not immediately close a hover child when the pointer crosses a
        # neighbouring row on its way to the child column.  If the pointer
        # *settles* on another row, open_current replaces the child after the
        # ordinary hover delay; otherwise the existing child stays reachable.
        self.hover_timer.stop()
        if action in self.openers:
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
        # A real, full-height editor exists before the popup gets native focus.
        # Never insert a 2px hidden editor: that broke QMenu layout on Windows.
        if not isinstance(self, AppCascadeMenu):
            self._ensure_local_filter()
        if self.launcher is not None and hasattr(self.launcher, 'style_cascade_menu'):
            self.launcher.style_cascade_menu(self)
        screen = QApplication.screenAt(pos) or self.screen() or QApplication.primaryScreen()
        if screen is None:
            return super().popup(pos, at)
        rect = screen.availableGeometry()  # Excludes the Windows taskbar.
        raw_height = self.sizeHint().height()
        # Some Qt styles pre-clamp QMenu.sizeHint() to a screen height even
        # though actions beyond that height cannot be reached reliably.
        # Count rows as well as checking Qt's own reported size.
        row_count = sum(1 for action in self.actions() if not action.isSeparator())
        estimated_height = row_count * max(32, self.fontMetrics().height() + 18) + 12
        requested_height = max(raw_height, estimated_height) if not isinstance(self, AppCascadeMenu) else raw_height
        placement = place_popup(pos.x(), pos.y(), self.sizeHint().width(), requested_height,
                                rect.left(), rect.top(), rect.right()+1, rect.bottom()+1)
        if placement.scroll and self.scroll_tree is None and not isinstance(self, AppCascadeMenu):
            self._enable_scroll_tree(placement.height)
            placement = place_popup(pos.x(), pos.y(), self.sizeHint().width(),
                                    self.sizeHint().height(), rect.left(), rect.top(),
                                    rect.right()+1, rect.bottom()+1)
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
        layout = QHBoxLayout(container)
        layout.setContentsMargins(7, 5, 7, 5)
        layout.setSpacing(5)
        glyph = QLabel('⌕', container)
        layout.addWidget(glyph)
        self.filter_edit = QLineEdit(container)
        self.filter_edit.setPlaceholderText('この列から探す…')
        self.filter_edit.setClearButtonEnabled(True)
        self.filter_edit.setMinimumWidth(180)
        self.filter_edit.installEventFilter(self)
        self._filter_ime_composing = False
        layout.addWidget(self.filter_edit, 1)
        # This button belongs ONLY to actual filesystem directories, never
        # Studio categories, bookmarks, apps or global search columns.
        if self._folder_container_row() is not None:
            self.paste_button = QPushButton('貼り付け', container)
            self.paste_button.setObjectName('directoryPasteButton')
            self.paste_button.setToolTip('Explorerでコピー／切り取りしたファイル・フォルダーをこの場所へ貼り付け')
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
            layout.addWidget(self.paste_button)
        self.filter_count = QLabel('', container)
        layout.addWidget(self.filter_count)
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
        focus_target = self.scroll_tree if self.scroll_tree is not None else self

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
        if right_click_child and self._handle_right_click_properties(event, obj):
            return True
        if right_click_child and self._consume_unused_right_click(event):
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

    def showEvent(self, event):
        super().showEvent(event)
        self.select_first()
        if self.filter_edit is not None:
            # Keep the popup's frame stable as filtered QAction rows disappear.
            # The size is taken AFTER Qt's screen-placement/scroll adaptation.
            self.setMinimumSize(max(self.minimumWidth(), self.width()),
                                max(self.minimumHeight(), self.height()))
            QTimer.singleShot(0, self._focus_initial_filter)

    def hideEvent(self, event):
        self.hover_timer.stop()
        self.folder_click_timer.stop()
        self._folder_click_action = None
        self._folder_double_click_row = None
        self._right_context_row = None
        self._context_highlight_action = None
        if self.child:self.child.close()
        super().hideEvent(event)

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
        if event.button()==Qt.MouseButton.LeftButton and self._folder_double_click_row is not None:
            self._open_folder_after_release()
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
        if self.activeAction() != before:
            if self.folder_click_timer.isActive():
                self.folder_click_timer.stop()
                self._folder_click_action = None
            # Switching rows is delayed; otherwise a diagonal move into an
            # already-open child closes that child before the pointer arrives.
            self.hover_timer.stop()
            if self.activeAction() in self.openers:
                self.hover_timer.start(int(self.launcher.data.get('launch_hover_delay_ms',250)))

    def open_current(self, mode="keyboard"):
        action = self.activeAction()
        if mode=="hover" and self.actionAt(self.mapFromGlobal(QCursor.pos()))!=action:return
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
        if self.scroll_tree is not None and event.key() in (
                Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Home, Qt.Key.Key_End,
                Qt.Key.Key_PageUp, Qt.Key.Key_PageDown):
            QApplication.sendEvent(self.scroll_tree, event)
            return
        self.hover_timer.stop()
        key = event.key(); mods = event.modifiers()
        if getattr(self, 'handle_file_shortcut', lambda *args: False)(key, mods):
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
        if not isinstance(self, AppCascadeMenu):
            if key == Qt.Key.Key_Backspace and self.filter_edit is not None:
                self.filter_edit.backspace();event.accept();return
            # Ctrl+V belongs to folder paste unless the real search QLineEdit
            # has keyboard focus (then its own native paste behavior applies).
            if (event.text() and (event.text().isprintable() or event.text() == '\u3000')
                    and not mods & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier)):
                self._ensure_local_filter()
                QApplication.sendEvent(self.filter_edit, QKeyEvent(event.type(),key,mods,event.text()))
                event.accept();return
        elif event.text() and event.text().isprintable() and not mods & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier):
            # The large installed-app catalog intentionally retains global search.
            self.launcher.focus_search(False)
            QApplication.sendEvent(self.launcher.search, QKeyEvent(event.type(),key,mods,event.text()))
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
        if isinstance(self, AppCascadeMenu):
            self.launcher.focus_search(False)
            QApplication.sendEvent(self.launcher.search, event)
        else:
            # The real QLineEdit is already visible: forward IME composition
            # without synthesizing keys or altering the user's chosen mode.
            self._ensure_local_filter()
            QApplication.sendEvent(self.filter_edit, event)
        event.accept()



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
        if hasattr(self,'tree') and self.tree.topLevelItemCount():self.tree.setCurrentItem(self.tree.topLevelItem(0))

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
from expanded_keyboard_model import (tab_target, root_step, middle_back_target,
                                     row_right_action)


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
        self.stack = []; self.selection = None; self.checked = set(); self.return_page = None
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
        self.bookmark_pointer_follow = str(self.settings.value(
            'bookmark_pointer_follow', 'true')).strip().lower() not in ('false', '0', 'no', 'off')
        self.bookmark_wan_enabled = str(self.settings.value(
            'bookmark_wan_enabled', 'true')).strip().lower() not in ('false', '0', 'no', 'off')
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
        self.search = QLineEdit()
        self.search.setObjectName('mainSearchField')
        self.search.setPlaceholderText('アプリ・ファイル・ブックマークを検索…')
        self.search.setClearButtonEnabled(True)
        self.search.setMinimumHeight(36)
        self.search.setMaximumHeight(36)
        self.search.setMinimumWidth(240)
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
        # Modern two-row header: title/search/window actions on the first row,
        # back/home + Page tabs on the second row.
        self.search_bar = QWidget(self)
        self.search_bar.setObjectName('searchBar')
        self.search_bar.setMinimumHeight(50)
        search_row = QHBoxLayout(self.search_bar)
        search_row.setContentsMargins(10, 3, 8, 3)
        search_row.setSpacing(10)

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
        self.theme_button.setIconSize(QSize(26, 26))
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

        # This launcher dismisses to the tray; a separate Minimize control is
        # redundant. Keep only Maximize/Restore and Close in the title bar.
        self.maximize_button = QPushButton('', self.search_bar)
        self.close_button = QPushButton('', self.search_bar)
        for button, object_name, tip in (
            (self.maximize_button, 'windowFrameButton', '最大化 / 元に戻す'),
            (self.close_button, 'windowCloseButton', '閉じる')):
            button.setObjectName(object_name)
            button.setFixedSize(32, 32)
            button.setIconSize(QSize(18, 18))
            button.setToolTip(tip)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            search_row.addWidget(button)
        self.maximize_button.clicked.connect(self.toggle_maximize_restore)
        self.close_button.clicked.connect(self.dismiss)

        # Browser-style view navigation is separate from ←/→ keyboard
        # shortcuts used by Page tabs, cascades and recipient selection.
        self.nav_toolbar = QWidget(self)
        nav_layout = QHBoxLayout(self.nav_toolbar)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(6)
        # Use real vector icons, never tiny platform-dependent Unicode glyphs.
        self.nav_back_button = QPushButton(self.nav_toolbar)
        self.nav_home_button = QPushButton(self.nav_toolbar)
        for button, name, tip in (
            (self.nav_back_button, 'navBackButton', '前の画面に戻る'),
            (self.nav_home_button, 'navHomeButton', 'ホーム（仕事Pageの先頭）')):
            button.setObjectName(name)
            button.setToolTip(tip)
            button.setFixedSize(40, 40)
            button.setIconSize(QSize(22, 22))
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            nav_layout.addWidget(button)
        self.nav_back_button.clicked.connect(self.navigate_back)
        self.nav_home_button.clicked.connect(self.navigate_home)
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
        self.theme_menu.addSeparator()
        # Experimental pointer follow is user-switchable and remembered across
        # launches.  It applies only to the first-level Bookmarks wheel list.
        self.bookmark_pointer_follow_action = self.theme_menu.addAction(
            'ブックマーク：ホイールでポインター追従')
        self.bookmark_pointer_follow_action.setCheckable(True)
        self.bookmark_pointer_follow_action.setChecked(self.bookmark_pointer_follow)
        self.bookmark_pointer_follow_action.triggered.connect(self.set_bookmark_pointer_follow)
        self.bookmark_wan_action = self.theme_menu.addAction(
            'ブックマーク：WANハイブリッド（実験）')
        self.bookmark_wan_action.setCheckable(True)
        self.bookmark_wan_action.setChecked(self.bookmark_wan_enabled)
        self.bookmark_wan_action.triggered.connect(self.set_bookmark_wan_enabled)
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
        self.footer = QLabel('↑↓ 選択   → 展開   ← 戻る   Enter 実行   Esc 閉じる')
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
        self.mode_bar = QWidget(self)
        self.mode_bar.setObjectName('pageBar')
        mode_row = QHBoxLayout(self.mode_bar)
        mode_row.setContentsMargins(10, 8, 10, 8)
        mode_row.setSpacing(10)
        mode_row.addWidget(self.nav_toolbar, 0)
        mode_row.addWidget(self.tabs, 1)
        self.mode_button = QPushButton('Three-layer', self.mode_bar)
        self.mode_button.setObjectName('expandedModeButton')
        self.mode_button.setIconSize(QSize(22, 22))
        self.mode_button.setToolTip('従来表示と、Files／ブックマークを並べた展開ビューを切替')
        self.mode_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.mode_button.clicked.connect(self.toggle_expanded_view)
        mode_row.addWidget(self.mode_button)
        self.expanded_view = ExpandedLauncherView(self)
        # Wheel Tab: share one cooldown across Page, toolbar and Files panels.
        self.tabs._zone_navigation = self.expanded_view.wheel_zone_navigation
        self.tabs._zone_enabled = lambda: self.view_mode == 'expanded'
        self.expanded_view.hide()
        layout.addWidget(self.search_bar)
        for w in (self.mode_bar, self.selection_tools, self.list,
                  self.expanded_view, self.footer):
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
        self.history_choices = ReorderablePopupTree(self.history_popup)
        self.history_choices.setObjectName('historyChoices')
        self.history_choices.setColumnCount(2)
        self.history_choices.setHeaderHidden(True)
        self.history_choices.setRootIsDecorated(False)
        self.history_choices.setIndentation(0)
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
        self.search.textChanged.connect(self.search_text_changed)
        self.tabs.currentChanged.connect(self.page_changed)
        self.list.itemActivated.connect(lambda item,col:self.activate(item.data(0,Qt.ItemDataRole.UserRole)))
        self.list.itemChanged.connect(self.check_changed)
        self.list.itemEntered.connect(self.hover)
        self.hover_timer = QTimer(self); self.hover_timer.setSingleShot(True); self.hover_timer.timeout.connect(self.open_hover)
        self.search.installEventFilter(self); self.list.installEventFilter(self); self.tabs.installEventFilter(self)
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
        if (getattr(self, '_restore_normal_on_show', False)
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

        Native QLineEdit trailing actions are on the far right.  The history
        register button sits 70px to their LEFT, inside the border.  Reserving
        text margins prevents a long search query from appearing behind it.
        """
        if not hasattr(self, 'search_glyph') or not hasattr(self, 'save_history_button'):
            return
        height, width = self.search.height(), self.search.width()
        self.search_glyph.move(11, max(0, (height - self.search_glyph.height()) // 2 + 2))
        is_visible = bool(self.search.text().strip())
        right_space = 71  # native ×, history ▼, and their breathing room
        self.save_history_button.move(
            max(48, width - right_space - self.save_history_button.width()),
            max(0, (height - self.save_history_button.height()) // 2))
        self.search.setTextMargins(49, 0, 137 if is_visible else 0, 0)
        if is_visible:
            self.save_history_button.raise_()
        self.search_glyph.raise_()

    def update_header_icons(self):
        self.search_glyph.setIcon(toolbar_outline_icon('search', theme_family(self.color_theme)))
        self.theme_button.setText('')
        self.theme_button.setIcon(toolbar_outline_icon('settings', theme_family(self.color_theme)))
        icon_name = 'restore' if self.windowState() & Qt.WindowState.WindowMaximized else 'maximize'
        self.maximize_button.setIcon(toolbar_outline_icon(icon_name, theme_family(self.color_theme)))
        self.close_button.setIcon(toolbar_outline_icon('close', theme_family(self.color_theme)))

    def open_theme_menu(self):
        """Only visual appearance changes; never write to Launch DataJSON."""
        self.close_cascade_for_main_interaction()
        self.hide_history_popup()
        for theme_id, action in self.theme_actions.items():
            action.setChecked(self.color_theme == theme_id)
        # The menu opens below the cog, aligned to its right edge.  Clamp it
        # inside the current monitor, even if the launcher is near the edge.
        width = self.theme_menu.sizeHint().width()
        position = self.theme_button.mapToGlobal(
            QPoint(self.theme_button.width() - width, self.theme_button.height() + 3))
        screen = self.theme_button.screen() or QApplication.primaryScreen()
        if screen is not None:
            area = screen.availableGeometry()
            position.setX(max(area.left(), min(position.x(), area.right() - width + 1)))
        self.theme_menu.popup(position)

    def set_bookmark_pointer_follow(self, enabled):
        # Persist optional wheel-assisted cursor movement; do not edit JSON.
        self.bookmark_pointer_follow = bool(enabled)
        self.settings.setValue('bookmark_pointer_follow', self.bookmark_pointer_follow)
        self.settings.sync()
        view = getattr(self, 'expanded_view', None)
        if view is not None:
            view.cancel_bookmark_pointer_follow()

    def set_bookmark_wan_enabled(self, enabled):
        """A/B comparison: hybrid flow/follow vs legacy one-row Follow."""
        self.bookmark_wan_enabled = bool(enabled)
        self.settings.setValue('bookmark_wan_enabled', self.bookmark_wan_enabled)
        self.settings.sync()
        view = getattr(self, 'expanded_view', None)
        if view is not None:
            view.set_bookmark_wan(self.bookmark_wan_enabled)

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
        self.update_history_chevron()
        self.update_header_icons()
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
        header_hover = '#e4eee8' if light else '#334744'
        header_pressed = '#d7e7df' if light else '#415953'
        frame_border = '#d0dfd7' if light else '#47605a'
        divider = '#c9d8d0' if light else '#4d6660'
        self.theme_button.setStyleSheet(
            f'QPushButton#headerSettingsButton {{ background:transparent; border:0; border-radius:17px; padding:0; }} '
            f'QPushButton#headerSettingsButton:hover {{ background:{header_hover}; }} '
            f'QPushButton#headerSettingsButton:pressed {{ background:{header_pressed}; }}')
        self.header_divider.setStyleSheet(f'QFrame#headerDivider {{ color:{divider}; background:{divider}; }}')
        common_window_style = (
            f'QPushButton#windowFrameButton, QPushButton#windowCloseButton {{ background:transparent; border:0; border-radius:16px; }} '
            f'QPushButton#windowFrameButton:hover {{ background:{header_hover}; }} '
            f'QPushButton#windowFrameButton:pressed {{ background:{header_pressed}; }} '
            f'QPushButton#windowCloseButton:hover {{ background:#e37d7d; }} '
            f'QPushButton#windowCloseButton:pressed {{ background:#d46565; }}')
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
                (self.nav_back_button, 'back'),
                (self.nav_home_button, 'home')):
            button.setIcon(browser_navigation_icon(name, theme_family(self.color_theme)))
        nav_hover = '#dbe6e0' if light else '#354b50'
        nav_pressed = '#cbdad4' if light else '#496168'
        nav_border = '#c8ddd1' if light else '#405650'
        nav_fill = '#eef5f1' if light else '#243431'
        self.nav_toolbar.setStyleSheet(f'''
            QPushButton {{ background:{nav_fill}; border:1px solid {nav_border}; border-radius:10px;
                padding:0; margin:0; }}
            QPushButton:hover:!disabled {{ background:{nav_hover}; }}
            QPushButton:pressed:!disabled {{ background:{nav_pressed}; }}
            QPushButton:disabled {{ background:{nav_fill}; color:#9eaea7; }}
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
        if not self.rect().contains(pos.toPoint()): return None
        # The entire very thin top stripe is a MOVE handle, including both
        # corners.  Never display a vertical/diagonal resize cursor there.
        if pos.y() < self.FRAME_TOP:
            return None
        left = pos.x() < self.FRAME_WIDTH
        right = pos.x() >= self.width() - self.FRAME_WIDTH
        bottom = pos.y() >= self.height() - self.FRAME_WIDTH
        return '-'.join(edge for hit, edge in ((bottom, 'bottom'),
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
                self.save_window_size()
                if self.can_save_normal_window_geometry():
                    self.settings.setValue('position', self.pos())
                    self.settings.sync()
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        if not getattr(self, '_size_drag', None): self.unsetCursor()
        super().leaveEvent(event)

    def update_window_shape(self):
        path=QPainterPath()
        path.addRoundedRect(QRectF(self.rect()),self.CORNER_RADIUS,self.CORNER_RADIUS)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def resizeEvent(self, event):
        super().resizeEvent(event)
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

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange and hasattr(self, 'maximize_button'):
            self.update_header_icons()

    def row_icon(self, row):
        path=row.get('_icon_file') or row.get('_file')
        key=path or row.get('icon_key','command')
        if key not in self.icon_cache:
            # Drive roots have real Windows Shell icons but are not files.
            if path and (row.get('_system_drive') or Path(path).is_file()):
                self.icon_cache[key] = self.file_icons.icon(QFileInfo(path))
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
        """Capture the keyboard anchor BEFORE popups and windows are hidden."""
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
        # Only persist stable IDs, never Qt pointers or transient QWidgetItems.
        state = normalize_focus_state({
            'area': area,
            'page_id': self.page_id,
            'mode': self.view_mode,
            'item_id': root_item_id if area == 'roots' else self._selected_item_id(self.list),
            'left_id': self._selected_item_id(view.left.tree),
            'middle_id': self._selected_item_id(view.middle.tree),
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
            if area == 'roots':
                self._last_root_id = state.get('item_id')
        finally:
            self._restoring_last_focus = False

    def summon(self):
        if self.busy:self.error('処理の完了を待っています');return
        if self.isVisible():self.dismiss();return
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

    def restore_keyboard_focus(self, expected_foreground=None, reason='open'):
        """Make a mouse-hook-opened Tool window actually accept keyboard input."""
        if not self.isVisible() or (self.menu and self.menu.isVisible()):
            return
        hwnd = int(self.winId())
        before = windows.foreground()
        # Native activation is needed when Qt is visible but Explorer is still
        # receiving keys. It must never steal focus from a different new app.
        active = (before == hwnd or windows.activate_keyboard_window(
            hwnd, expected_foreground=expected_foreground))
        if active:
            self.activateWindow()
            self.restore_last_current()
        DIAG.info('KEYBOARD_FOCUS reason=%s success=%s before=%s after=%s restored_area=%s',
                  reason, active, before, windows.foreground(), self._last_focus_area)

    def dismiss(self):
        if self.isVisible():
            self.save_last_current()
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

    def app_state(self, state):
        # A native recycle-bin operation or QMessageBox can briefly deactivate
        # the main Tool window. Do not dismiss its folder menu mid-operation.
        context = getattr(self, '_launch_context_menu', None)
        if (getattr(self, '_filesystem_dialog_depth', 0)
                or QApplication.activeModalWidget() is not None
                or (context is not None and context.isVisible())):
            return
        if state == Qt.ApplicationState.ApplicationInactive and self.isVisible():
            self.dismiss()

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
            self.footer.setText('↑↓ 選択   → 進む   ← 戻る   Enter 実行   Tab エリア切替   Esc 閉じる')
        self.list.setVisible(not active)
        if not active:
            self.expanded_view.hide_favorite_popup()
        self.expanded_view.setVisible(active)
        showing_classic = self.view_mode == 'expanded'
        self.mode_button.setText('Compact' if showing_classic else 'Three-layer')
        self.mode_button.setIcon(view_mode_icon('classic' if showing_classic else 'expanded',
                                                self.color_theme))
        self.mode_button.setToolTip(
            '仕事Pageで展開ビューを使えます' if self.view_mode == 'expanded'
            and self.page_id != self.expanded_options['page_id'] else
            '従来表示とFiles／ブックマーク同時表示を切替')

    def open_expanded_cascade(self, row, widget, item=None):
        # Transient deep menu reuses Launcher's existing actions/keyboard logic.
        if self.menu:
            self.menu.close()
        self.hover_timer.stop()
        menu_type = AppCascadeMenu if row.get('launch_source') == 'installed_apps' else CascadeMenu
        self.menu = menu_type(parent=self, launcher=self)
        self.menu.open_mode = 'keyboard'
        # Only Three-layer bookmark cascades use the slimmer popup. Nested
        # children inherit the limit; all other popup widths remain untouched.
        view = getattr(self, 'expanded_view', None)
        is_bookmark = (view is not None and widget is view.right.tree)
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
                pairs=[(c,'') for c in candidates if matches_choice_search(c, query)]
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
                    query=self.search.text(), current_item_id=row.get('item_id') if row else None,
                    focus=('tabs' if self.tabs.hasFocus() else
                           'search' if self.search.hasFocus() else 'list'))

    def _nav_update_buttons(self):
        self.nav_back_button.setEnabled(self.view_history.can_back)
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
        self._nav_flush_search()
        state = self.view_history.back()
        if state is not None:
            self._nav_restore(state)
        else:
            self._nav_update_buttons()

    def navigate_home(self):
        if not self.data or not self.pages:
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
        """Set an initial halfwidth-English IME state after focus settles."""
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
        menu.order_enabled=parent['item_kind']=='category' and parent.get('launch_source') not in {'installed_apps','browser_bookmarks'} and not parent.get('_browser_bookmark')
        menu.order_page=parent.get('page_id',self.page_id)
        menu.order_parent=parent.get('item_id','')
        menu.order_context=parent
        menu.order_rows=[]
        try:
            for row in self.displayed_children(parent):
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
                        if m.child:m.child.close();m.child.deleteLater()
                        m.child=(AppCascadeMenu if r.get('launch_source')=='installed_apps' else CascadeMenu)(parent=m,launcher=self)
                        m.child.open_mode=mode;m.child.owner_action=a
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
            if parent['item_kind']=='directory':
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

    def _clear_previous_paste_feedback(self):
        """End the prior operation's visual result, not its clipboard data.

        Every new filesystem operation starts a fresh feedback cycle. Apply it
        to the whole visible cascade chain: a highlighted row may be in a
        nested directory rather than the menu receiving the new action.
        """
        menu = getattr(self, 'menu', None)
        while menu is not None:
            if getattr(menu, '_pasted_feedback_paths', ()):
                menu._pasted_feedback_paths = ()
                menu._refresh_transfer_visuals()
            menu = getattr(menu, 'child', None)

    def paste_into_directory(self, menu):
        """Paste Explorer files and ZIP virtual items into displayed folder."""
        context = menu._folder_container_row()
        if context is None:
            return
        # A new paste replaces the preceding operation's highlighted result,
        # even when overwrite is cancelled or the paste later fails.
        reset = getattr(self, '_clear_previous_paste_feedback', None)
        if callable(reset):
            reset()
        try:
            destination = Path(self.expander().expand(context['launch_browse_target']))
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
                count = paste_items(plan, move=move, overwrite=bool(conflicts))
                names_done = [item.target.name for item in plan]
                if move:
                    clipboard.clear()
                self.footer.setText(f'{count}件を{"移動" if move else "コピー"}しました → {destination}')
            menu._pasted_feedback_paths = pasted_paths_for(destination, names_done)
            # Refresh only the edited menu. Preserve its parent chain, scroll
            # and search so the newly pasted rows can be visually confirmed.
            QTimer.singleShot(0, lambda m=menu: self.refresh_pasted_directory(m, reopen=True, focus_pasted=True))
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
        if self.menu:self.menu.close()
        self.activate(row)

    def cascade(self,row,q=None,mode="keyboard"):
        self.hover_timer.stop();self.pending_menu_item=None
        if self.menu:self.menu.close();self.menu.deleteLater()
        self.menu=(AppCascadeMenu if row.get('launch_source')=='installed_apps' else CascadeMenu)(parent=self,launcher=self)
        self.menu.open_mode=mode;self.menu.owner_item=q or self.list.currentItem()
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
            self.selection = owner
            self.checked = {row['choice_id']}
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
            self.selection=row;self.checked.clear();self.search.clear();self.render();self.list.setFocus()
            self._nav_after_change()
            return
        self.execute(row)

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
        """Store only completed queries, never intermediate live-search keystrokes."""
        text = self.search.text() if value is None else value
        try:
            if self.search_history.remember(text):
                DIAG.info('SEARCH_HISTORY saved keyword=%s', normalize_keyword(text))
        except OSError:
            DIAG.exception('SEARCH_HISTORY save failed')

    def search_text_changed(self, value):
        # Slash is reserved for the history popup, even for clipboard pastes.
        if '/' in value:
            cursor = self.search.cursorPosition()
            cleaned = value.replace('/', '')
            self.search.setText(cleaned)
            self.search.setCursorPosition(max(0, cursor - value[:max(0, cursor)].count('/')))
            return
        self.save_history_button.setVisible(bool(value.strip()))
        self.layout_search_inner_controls()
        self.render()
        if not self._nav_restoring and not self._nav_transition:
            self._nav_search_timer.start()

    def position_history_popup(self):
        if not hasattr(self, 'history_popup'):
            return
        # QLineEdit is nested in searchBar; map back to Launcher coordinates.
        anchor = self.search.mapTo(self, QPoint(0, self.search.height() + 4))
        x, y = anchor.x(), anchor.y()
        height = min(300, max(88, self.height() - y - 12))
        self.history_popup.setGeometry(x, y, self.search.width(), height)

    def populate_history_popup(self, selected=None):
        self.history_choices.blockSignals(True)
        self.history_choices.clear()
        keywords = self.search_history.keywords
        if not keywords:
            row = QTreeWidgetItem(['（履歴はありません）', ''])
            row.setFlags(Qt.ItemFlag.NoItemFlags)
            self.history_choices.addTopLevelItem(row)
        else:
            for index, keyword in enumerate(keywords):
                row = QTreeWidgetItem([keyword, '×'])
                row.setIcon(0, self.history_clock_icon)
                row.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
                row.setToolTip(0, keyword + '  — クリックで検索／ドラッグで並び替え')
                row.setToolTip(1, '履歴を削除')
                self.history_choices.addTopLevelItem(row)
            target = next((i for i, k in enumerate(keywords) if k == selected), 0)
            self.history_choices.setCurrentItem(self.history_choices.topLevelItem(target))
        self.history_choices.blockSignals(False)

    def show_history_popup(self):
        if not self.isVisible():
            return
        if self.menu:
            self.menu.close()
        self.hover_timer.stop(); self.pending_menu_item = None
        self.expanded_view.hide_favorite_popup()
        self.populate_history_popup()
        self.position_history_popup()
        self.history_popup.show()
        self.history_popup.raise_()
        self.history_choices.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def hide_history_popup(self, focus_search=False):
        if not hasattr(self, 'history_popup'):
            return
        was_visible = self.history_popup.isVisible()
        self.history_popup.hide()
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
        if row is None or not self.search_history.keywords:
            return
        keyword = row.text(0)
        if keyword not in self.search_history.keywords:
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
                index = self.search_history.keywords.index(value)
                if not self.search_history.remove(value):
                    return
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
        if not self.search_history.keywords:
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
            if obj is not self.search or not self.search_history.keywords:
                return False
            self.show_history_popup()
        pending, steps = wheel_steps(self._search_history_wheel_delta,
                                     event.angleDelta().y(), event.pixelDelta().y())
        self._search_history_wheel_delta = pending
        if not steps:
            return True
        tree = self.history_choices
        count = len(self.search_history.keywords)
        if count == 0:
            return True
        current = tree.indexOfTopLevelItem(tree.currentItem())
        target = tree.topLevelItem(history_target_index(current, count, steps))
        tree.setCurrentItem(target)
        tree.scrollToItem(target, QAbstractItemView.ScrollHint.EnsureVisible)
        origin = QCursor.pos()
        self._search_history_warp_generation += 1
        generation = self._search_history_warp_generation
        QTimer.singleShot(0, lambda: (
            warp_to_history_row(tree, target, origin, QCursor)
            if generation == self._search_history_warp_generation else None))
        return True

    def handle_history_event(self, obj, event):
        # Keep popup key handling ahead of the launcher's Enter/Right handlers:
        # the first Enter must search, the NEXT Enter may activate a result.
        popup_input = obj in (self.history_choices, self.history_choices.viewport())
        if event.type() == QEvent.Type.MouseButtonPress and obj in (
                self.list.viewport(), self.tabs) and self.history_popup.isVisible():
            self.hide_history_popup()
            return False
        if event.type() != QEvent.Type.KeyPress:
            return False
        key = event.key()
        modifiers = event.modifiers()
        if getattr(self, 'composing', False):
            return False
        if (obj in (self.search, self.list, self.tabs) or popup_input) and (
                event.text() == '/' or (key == Qt.Key.Key_Slash and not event.text())) and modifiers in (
                    Qt.KeyboardModifier.NoModifier, Qt.KeyboardModifier.ShiftModifier):
            self.toggle_history_popup()
            event.accept()
            return True
        if not popup_input or not self.history_popup.isVisible():
            return False
        if key == Qt.Key.Key_Escape:
            self.hide_history_popup(focus_search=True)
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Right, Qt.Key.Key_Tab):
            self.select_history_keyword()
        elif key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            row = self.history_choices.currentItem()
            count = len(self.search_history.keywords)
            if row is not None and count:
                offset = -1 if key == Qt.Key.Key_Up else 1
                move_tree_selection(self.history_choices, offset)
        elif key == Qt.Key.Key_Delete:
            row = self.history_choices.currentItem()
            if row is not None and self.search_history.keywords:
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
        target = tab_target(area, backward=backward)
        view = self.expanded_view
        if target == 'search':
            self.search.setFocus(Qt.FocusReason.TabFocusReason)
        elif target == 'pages':
            self.tabs.setFocus(Qt.FocusReason.TabFocusReason)
        elif target == 'roots':
            view.focus_root()
        elif target == 'files':
            view.focus_panel(view.left)
        elif target == 'directory':
            view.focus_panel(view.middle)
        elif target == 'bookmarks':
            view.focus_panel(view.right)
        event.accept()
        return True

    def execute_expanded_root_shortcut(self, index):
        """Dispatch by *current displayed order*, not hardcoded item names."""
        view = self.expanded_view
        if (not view.isVisible() or not 0 <= index < len(view.root_rows)
                or index >= len(view.root_buttons)):
            return
        button = view.root_buttons[index]
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
                view.focus_panel(view.left)
            elif row.get('item_id') == view.bookmarks_root.get('item_id'):
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
        if event.modifiers() != Qt.KeyboardModifier.NoModifier:
            return False
        view = self.expanded_view
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
                if middle_back_target(len(view.path)) == 'parent':
                    view.go_up(keep_middle_focus=True)
                else:
                    view.focus_panel(view.left)
            elif pane is view.left:
                # Stay in Files: Left resets current to its first row, never
                # jumps to the top-level Files root button.
                first = pane.tree.topLevelItem(0)
                if first is not None:
                    pane.tree.setCurrentItem(first)
                    view.choose_files(first, 0)
                    pane.tree.setFocus(Qt.FocusReason.TabFocusReason)
            else:
                # Bookmarks is already a permanent panel, not a hidden
                # toolbar button. Left should move to the adjacent column.
                view.focus_panel(view.middle)
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
            expanded_sources = (view.root_buttons + [pane.tree for pane in
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

    def _paste_from_context_menu(self, context_parent=None):
        if not self._context_paste_enabled(context_parent):
            return
        if self._paste_context_destination(context_parent) == 'cascade':
            self.paste_into_directory(context_parent)
        else:
            self.paste_into_expanded_directory()

    def show_expanded_background_paste_menu(self, global_pos):
        """Paste is available even when the current directory has zero rows."""
        if not self.expanded_view.current_directory():
            return False
        try:
            definitions = load_context_menus(CONTEXT_MENU_OPTIONS)['folder']
        except (OSError, ValueError, KeyError) as exc:
            self.error('コンテキストメニュー定義が不正です: ' + str(exc))
            return False
        paste = next((x for x in definitions if x.get('action_id') == 'paste'), None)
        if paste is None:
            return False
        menu = QMenu(self)
        action = menu.addAction(paste['title'],
                                lambda checked=False: self._paste_from_context_menu(self))
        action.setIcon(context_action_icon('paste'))
        action.setIconVisibleInMenu(True)
        action.setEnabled(self._context_paste_enabled(self))
        # Explorer-like New shares the blank-area context menu with Paste.
        # The separate right-side Back lane uses the same submenu builder.
        menu.addSeparator()
        self.expanded_view.add_lane_new_submenu(menu)
        # Both the separate right Back lane and the lower blank area use this
        # SAME menu.  Read existing folder actions from the authoritative JSON
        # so captions, icons and separators match regular folder menus.
        folder_actions = {'open_explorer', 'open_terminal', 'copy_path', 'properties'}
        target_directory = str(self.expanded_view.current_directory())
        selected = visible_context_entries(definitions, folder_actions)
        if selected:
            menu.addSeparator()
            for definition in selected:
                if definition.get('type') == 'separator':
                    menu.addSeparator()
                    continue
                action_id = definition['action_id']
                folder_action = menu.addAction(
                    definition['title'],
                    lambda checked=False, a=action_id, p=target_directory:
                    self.perform_filesystem_context_action(a, p, 'folder'))
                folder_action.setIcon(context_action_icon(action_id))
                folder_action.setIconVisibleInMenu(True)
        menu.setStyleSheet((LIGHT_MENU_QSS if self.color_theme == 'light' else '')
                           + context_menu_spacing_qss(self.color_theme))
        self._launch_context_menu = menu
        menu.aboutToHide.connect(lambda m=menu: self._forget_launch_context_menu(m))
        menu.popup(global_pos)
        return True

    def show_launch_context_menu(self, global_pos, row=None, *, context_parent=None,
                                 selected_paths=None):
        """Choose context actions by authoritative source, not displayed item ID."""
        if not self.data:
            return False
        if self.selection:
            return False
        origin, path = resolve_context_target(row, self.authored_items)
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
            allowed = {d['action_id'] for d in actions if d.get('action_id')
                       and not (d['action_id'] == 'git_commit_from_zip' and not is_downloads_zip(path))
                       and not (d['action_id'] == 'run_with_pause' and Path(path).suffix.casefold() not in ('.ps1', '.py'))}
            for definition in visible_context_entries(actions, allowed):
                if definition.get('type') == 'separator':
                    menu.addSeparator()
                    continue
                action_id = definition['action_id']
                if action_id == 'paste':
                    action = menu.addAction(definition['title'],
                        lambda checked=False, parent=context_parent:
                        self._paste_from_context_menu(parent))
                    action.setEnabled(self._context_paste_enabled(context_parent))
                else:
                    action = menu.addAction(definition['title'],
                        lambda checked=False, a=action_id, p=path, k=origin:
                        self.perform_filesystem_context_action(a, p, k))
                if action is not None:
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
                for path in targets:
                    move_to_recycle_bin(path)
                    finished += 1
                self.footer.setText(f'{finished}件をごみ箱へ移動しました')
            else:
                raise ValueError('複数選択で未対応の操作です: ' + action_id)
        except (OSError, ValueError) as exc:
            self.error('複数項目を操作できませんでした: ' + str(exc))
        finally:
            if action_id == 'delete':
                # Refresh even after a partially successful recycle batch.
                if locals().get('finished', 0) and self.expanded_view.isVisible():
                    QTimer.singleShot(0, self.expanded_view.refresh_middle)
                # Native shell activation may arrive after the API returns.
                QTimer.singleShot(650, self._finish_batch_delete_guard)

    def _finish_batch_delete_guard(self):
        self._filesystem_dialog_depth = max(
            0, getattr(self, '_filesystem_dialog_depth', 0) - 1)

    def paste_into_expanded_directory(self):
        """Explorer/Launch clipboard -> current three-column directory."""
        destination_text = self.expanded_view.current_directory()
        if not destination_text:
            return
        try:
            destination = Path(destination_text)
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
                count = paste_items(plan, move=move, overwrite=bool(conflicts))
                if move:
                    clipboard.clear()
                self.footer.setText(f'{count}件を{"移動" if move else "コピー"}しました → {destination}')
            self.expanded_view.refresh_middle()
        except (OSError, ValueError) as exc:
            DIAG.exception('EXPANDED_DIRECTORY_PASTE target=%s', destination_text)
            self.error('貼り付けできませんでした: ' + str(exc))

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
            elif action_id == 'delete':
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
                    move_to_recycle_bin(path)
                finally:
                    # Windows native recycle-bin and Qt.Tool focus events can
                    # arrive AFTER the modal dialog returns. The previous
                    # immediate decrement dismissed the whole launcher.
                    QTimer.singleShot(900, lambda: setattr(
                        self, '_filesystem_dialog_depth',
                        max(0, getattr(self, '_filesystem_dialog_depth', 0) - 1)))
                # A delete refresh does not carry over old paste highlights.
                if visible_menu is not None:
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
                    else:
                        self.render()
                if self.file_index_settings.get('enabled', True) and not self.file_index_busy:
                    QTimer.singleShot(0, lambda: self.refresh_file_index(manual=False))
                self.footer.setText(f'削除を完了しました: {path.name}')
            elif action_id in ('copy_full_path', 'copy_path'):
                QApplication.clipboard().setText(str(path))
            elif action_id == 'copy_file_name':
                QApplication.clipboard().setText(path.name)
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
                # Shell property sheets do not share that topmost z-order and
                # can be obscured. Dismiss our launcher before opening them;
                # the desktop hotkey/double click will summon it again.
                self.dismiss()
                show_windows_properties(path)
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
                rename_file_or_folder(path, name)
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

    def git_commit_using_filename(self, zip_path):
        """Use a selected Downloads ZIP's name as a message, never as content."""
        try:
            if not is_downloads_zip(zip_path) or not Path(zip_path).is_file():
                raise ValueError('Downloads直下のZIPだけが対象です')
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
            form.addWidget(QLabel('選択ZIPのファイル名（編集できます）:', dialog))
            message_editor = QLineEdit(dialog)
            message_editor.setText(Path(zip_path).name)
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
                '※ ZIPの展開・追加はしません。'
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
            DIAG.exception('GIT_COMMIT_FROM_ZIP path=%s', zip_path)
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
            if should_start_before_dismiss(self.queue):
                # A GUI child can claim foreground only if its launcher was
                # foreground at process creation. Previously we hid first and
                # waited 180 ms, handing foreground to another application.
                self._foreground_handoff_pending = True
                DIAG.info('FOREGROUND_HANDOFF launching before launcher hide')
                self.next_step()
                if self.busy:
                    self.dismiss()
            else:
                self._foreground_handoff_pending = False
                self.dismiss()
                QTimer.singleShot(180,self.next_step)
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
    # CLaunch-style: double-click empty desktop wallpaper to open the launcher.
    # Keep a strong reference for the whole Qt event loop and release on exit.
    # Desktop double-click support is optional: a Windows API/COM error must
    # never prevent the launcher itself from starting (tray/hotkey still work).
    desktop_click = None
    def open_from_desktop():
        DIAG.info('DESKTOP_OPEN_CALLBACK visible_before=%s', window.isVisible())
        if not window.isVisible():
            window.summon()
            source_foreground = window.target
            # Explorer got the double-click, not our Qt Tool window. Qt may
            # raise it without gaining Windows keyboard focus; correct that on
            # the event loop, with one short retry for mouse-up/Qt timing.
            QTimer.singleShot(0, lambda: window.restore_keyboard_focus(
                source_foreground, 'desktop_first'))
            QTimer.singleShot(120, lambda: window.restore_keyboard_focus(
                source_foreground, 'desktop_retry'))
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

    def dismiss_from_outside_click():
        # An outside mouse press closes the ENTIRE UI, including an orphaned
        # folder cascade. Never do this while the OS confirmation is active.
        if (launcher_surface_visible()
                and not getattr(window, '_filesystem_dialog_depth', 0)
                and QApplication.activeModalWidget() is None):
            DIAG.info('OUTSIDE_CLICK_DISMISS')
            window.dismiss()

    try:
        desktop_click = DesktopDoubleClick(
            open_from_desktop, DIAG,
            on_outside_click=dismiss_from_outside_click,
            is_launcher_visible=launcher_surface_visible,
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
            elif not window.isVisible():
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
