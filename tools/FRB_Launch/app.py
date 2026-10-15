import sys
import os
import json
import logging
import time
from pathlib import Path
from ctypes import wintypes
import ctypes
from PySide6.QtCore import Qt, QTimer, QSettings, QEvent, QLockFile, QDir, QRectF
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QKeyEvent, QShortcut, QKeySequence, QCursor, QAction, QPainterPath, QRegion, QPen, QLinearGradient
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLineEdit, QTabBar, QTreeWidget, QTreeWidgetItem, QMenu, QSystemTrayIcon, QFileIconProvider, QMessageBox, QLabel, QHBoxLayout, QPushButton, QWidgetAction, QAbstractItemView)
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtCore import QFileInfo
from core import load, Expander, searchable_rows, column_filter_match
import windows
import installed_apps
from apps_scan_support import append_apps_log, scan_shortcuts, merge_catalog
from ordering import save_order
from reorder_widgets import OrderDragMixin, ReorderTree
from process_runner import start_process
from launch_diagnostics import make_logger, wifi_transcript_arguments
from runtime_paths import launch_home
from desktop_double_click import DesktopDoubleClick

ROOT = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
LAUNCH_HOME = launch_home(ROOT)
CONFIG = LAUNCH_HOME / 'config' / 'frb_launch_sample_data_v0_1.json'
STATE = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'FRBLaunch'
STATE.mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=str(STATE / 'error.log'), encoding='utf-8', level=logging.WARNING)
DIAG = make_logger(STATE)
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


def application_icon():
    # PyInstaller bundles assets below _MEIPASS; source runs use app.py's folder.
    resources = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
    path = resources / 'assets' / 'frb_launch.ico'
    result = QIcon(str(path))
    return result if not result.isNull() else icon('command')


def tray_icon():
    resources = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
    result = QIcon(str(resources / 'assets' / 'frb_launch_tray.svg'))
    return result if not result.isNull() else application_icon()


class CascadeMenu(OrderDragMixin,QMenu):
    """Explicit child popups: selecting a folder never opens it automatically."""
    def __init__(self, title='', parent=None, launcher=None):
        super().__init__(title, parent)
        self.launcher = launcher or parent
        self.child = None
        self.open_mode = "keyboard"; self.owner_item = None; self.owner_action = None; self.outside_since = None
        self.setup_order_drag();self.order_press=None
        self.openers = {}
        # A search belongs to one open column, not to the launcher's global search.
        # AppCascadeMenu intentionally keeps its existing global-search behavior.
        self.filter_action = None
        self.filter_edit = None
        self.filter_count = None
        self._order_enabled_before_filter = False
        self.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        self.setStyleSheet('QMenu { menu-scrollable: 1; }')
        self.hover_timer = QTimer(self); self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(lambda:self.open_current("hover"))

    def select_first(self):
        first = next((a for a in self.actions()
                      if a.isVisible() and a.isEnabled() and isinstance(a.data(), dict)), None)
        self.setActiveAction(first)

    def _ensure_local_filter(self):
        """Display an inline search only after the user starts typing in this column."""
        if self.filter_action is not None:
            return
        # Keyboard input should keep a hover-opened menu alive even after the
        # pointer leaves the row (same promotion used by Right-arrow).
        ancestor = self
        while isinstance(ancestor, CascadeMenu):
            ancestor.open_mode = 'keyboard'
            ancestor.outside_since = None
            ancestor = ancestor.parentWidget()
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
        layout.addWidget(self.filter_edit, 1)
        self.filter_count = QLabel('', container)
        layout.addWidget(self.filter_count)
        action = QWidgetAction(self)
        action.setDefaultWidget(container)
        self.filter_action = action
        before = self.actions()[0] if self.actions() else None
        if before is not None:
            self.insertAction(before, action)
        else:
            self.addAction(action)
        self._order_enabled_before_filter = self.order_enabled
        self.order_enabled = False  # Never reorder a filtered subset as if it were complete.
        self.filter_edit.textChanged.connect(self._apply_local_filter)
        self.filter_edit.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def _apply_local_filter(self, query):
        if not query:
            self.clear_local_filter()
            return
        shown = 0
        total = 0
        self.hover_timer.stop()
        if self.child:
            self.child.close()
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
        for candidate in self.actions():
            if candidate is not action:
                candidate.setVisible(True)
        self.removeAction(action)
        action.deleteLater()
        self.filter_action = None
        self.filter_edit = None
        self.filter_count = None
        self.order_enabled = self._order_enabled_before_filter
        self.select_first()
        if self.isVisible():
            self.setFocus(Qt.FocusReason.OtherFocusReason)

    def _move_filtered_selection(self, increment):
        matches = [a for a in self.actions()
                   if a is not self.filter_action and a.isVisible()
                   and a.isEnabled() and isinstance(a.data(), dict)]
        if not matches:
            self.setActiveAction(None)
            return
        current = self.activeAction()
        index = matches.index(current) if current in matches else (0 if increment > 0 else len(matches)-1)
        self.setActiveAction(matches[max(0, min(len(matches)-1, index+increment))])

    def eventFilter(self, obj, event):
        if obj is self.filter_edit and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key == Qt.Key.Key_Escape:
                self.clear_local_filter()
                event.accept()
                return True
            if key in (Qt.Key.Key_Down, Qt.Key.Key_Up):
                self._move_filtered_selection(1 if key == Qt.Key.Key_Down else -1)
                event.accept()
                return True
            if key in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.keyPressEvent(event)
                event.accept()
                return True
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_F:
                self.keyPressEvent(event)
                event.accept()
                return True
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        super().showEvent(event)
        self.select_first()

    def hideEvent(self, event):
        self.hover_timer.stop()
        if self.child:self.child.close()
        super().hideEvent(event)

    def order_surface(self):return self
    def order_rects(self):return [self.actionGeometry(a) for a in self.actions() if a.data()]
    def paintEvent(self,event):
        super().paintEvent(event);self.paint_order_line()
    def mousePressEvent(self,event):
        self.order_press=(event.position().toPoint(),self.actionAt(event.position().toPoint())) if event.button()==Qt.MouseButton.LeftButton else None
        super().mousePressEvent(event)
    def mouseReleaseEvent(self,event):
        self.order_press=None;super().mouseReleaseEvent(event)
    def mouseMoveEvent(self, event):
        if self.order_enabled and self.order_press and event.buttons() & Qt.MouseButton.LeftButton:
            pos,action=self.order_press
            if (event.position().toPoint()-pos).manhattanLength()>=QApplication.startDragDistance():
                self.order_press=None
                self.begin_order_drag(action.data() if action else None);return
        before = self.activeAction()
        super().mouseMoveEvent(event)
        if self.activeAction() != before:
            if self.child and self.child.open_mode=="hover":self.child.close()
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

    def keyPressEvent(self, event):
        self.hover_timer.stop()
        key = event.key(); mods = event.modifiers()
        if self.launcher.page_key(event):event.accept();return
        if key == Qt.Key.Key_Escape and self.filter_action is not None:
            self.clear_local_filter();event.accept();return
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Escape):
            parent = self.parentWidget()
            self.close()
            if isinstance(parent, CascadeMenu):parent.setFocus()
            else:self.launcher.list.setFocus()
            event.accept();return
        action=self.activeAction()
        if key in (Qt.Key.Key_Return,Qt.Key.Key_Enter) and action and isinstance(action.data(),dict) and action.data().get('item_kind')=='directory':
            self.launcher.run_menu_item(action.data());event.accept();return
        if key == Qt.Key.Key_Right or (key in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and action in self.openers):
            self.open_current();event.accept();return
        if (mods & Qt.KeyboardModifier.ControlModifier and key==Qt.Key.Key_F):
            self.launcher.focus_search();event.accept();return
        if not isinstance(self, AppCascadeMenu):
            if key == Qt.Key.Key_Backspace and self.filter_edit is not None:
                self.filter_edit.backspace();event.accept();return
            if mods & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_V:
                clip = QApplication.clipboard().text()
                if clip:
                    self._ensure_local_filter()
                    self.filter_edit.insert(clip)
                event.accept();return
            if event.text() and event.text().isprintable() and not mods & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier):
                self._ensure_local_filter()
                QApplication.sendEvent(self.filter_edit, QKeyEvent(event.type(),key,mods,event.text()))
                event.accept();return
        elif event.text() and event.text().isprintable() and not mods & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier):
            # The large installed-app catalog intentionally retains global search.
            self.launcher.focus_search(False)
            QApplication.sendEvent(self.launcher.search, QKeyEvent(event.type(),key,mods,event.text()))
            event.accept();return
        super().keyPressEvent(event)

    def inputMethodEvent(self, event):
        if isinstance(self, AppCascadeMenu):
            self.launcher.focus_search(False)
            QApplication.sendEvent(self.launcher.search,event)
        else:
            self._ensure_local_filter()
            QApplication.sendEvent(self.filter_edit,event)



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
        self.tree.verticalScrollBar().setStyleSheet('''
            QScrollBar:vertical { background:#202b29; width:8px; margin:0; border:0; }
            QScrollBar::handle:vertical { background:#929894; min-height:28px; border-radius:2px; margin:0 2px; }
            QScrollBar::handle:vertical:hover { background:#c9d0cc; }
            QScrollBar::handle:vertical:pressed { background:#eef2ef; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; border:0; background:transparent; }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical { width:0; height:0; background:transparent; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background:transparent; }
        ''')
        self.tree.setMinimumSize(440,280)
        height=min(490,max(280,QApplication.primaryScreen().availableGeometry().height()-120))
        self.tree.setFixedSize(440,height)
        self.tree.installEventFilter(self);self.tree.viewport().installEventFilter(self)
        self.widget_action=QWidgetAction(self);self.widget_action.setDefaultWidget(self.tree)
        self.addAction(self.widget_action)
        self.tree.itemActivated.connect(lambda item,col:self.launcher.run_menu_item(item.data(0,Qt.ItemDataRole.UserRole)))

    def populate(self, rows):
        for row in rows:
            item=QTreeWidgetItem([row['title'],row.get('description','')])
            item.setData(0,Qt.ItemDataRole.UserRole,row)
            item.setIcon(0,self.launcher.row_icon(row));item.setToolTip(0,row['title'])
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
            if key in (Qt.Key.Key_Up,Qt.Key.Key_Down,Qt.Key.Key_PageUp,Qt.Key.Key_PageDown,Qt.Key.Key_Home,Qt.Key.Key_End):return False
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
        if key in (Qt.Key.Key_Up,Qt.Key.Key_Down,Qt.Key.Key_PageUp,Qt.Key.Key_PageDown,Qt.Key.Key_Home,Qt.Key.Key_End):
            QApplication.sendEvent(self.tree,event);return
        if key in (Qt.Key.Key_Return,Qt.Key.Key_Enter):
            item=self.tree.currentItem()
            if item:self.launcher.run_menu_item(item.data(0,Qt.ItemDataRole.UserRole))
            event.accept();return
        if key==Qt.Key.Key_Right:event.accept();return
        super().keyPressEvent(event)


class Launcher(QWidget):
    CORNER_RADIUS = 10  # Main window corner radius in logical pixels.
    def __init__(self):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle('FRB Launch'); self.resize(390,440)
        self.setWindowIcon(application_icon())
        self.setMouseTracking(True)
        self.setMinimumHeight(240)
        self.frame_title = QLabel('FRB Launch', self)
        self.frame_title.setGeometry(14, 3, 220, 18)
        self.frame_title.setStyleSheet('background:transparent;color:#f2f5f2;font-size:12px;border:0;')
        self.frame_title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.app_records=installed_apps.read_cache(STATE/'apps_cache.json');self.apps_proc=None;self.apps_log=STATE/'apps.log'
        self.apps_timer=QTimer(self);self.apps_timer.setInterval(150);self.apps_timer.timeout.connect(self.poll_apps)
        self.data = None; self.mtime = None; self.config_size = None; self.target = 0; self.busy = False
        self.stack = []; self.selection = None; self.checked = set(); self.return_page = None
        self.menu = None; self.pending_menu_item = None; self.file_icons = QFileIconProvider();self.icon_cache={}
        self.settings = QSettings(str(STATE / 'state.ini'), QSettings.Format.IniFormat)
        self.page_id = self.settings.value('page', 'work')
        self.search = QLineEdit(); self.search.setPlaceholderText('検索 — 全Pageから探す'); self.search.setClearButtonEnabled(True)
        self.tabs = QTabBar(); self.tabs.setExpanding(False); self.tabs.setDrawBase(False)
        self.list = ReorderTree(self); self.list.setColumnCount(2); self.list.setHeaderHidden(True); self.list.setRootIsDecorated(False)
        self.list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel);self.list.verticalScrollBar().setSingleStep(35)
        self.list.setColumnWidth(0,180); self.list.setMouseTracking(True); self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.footer = QLabel('↑↓ 選択   → 展開   ← 戻る   Enter 実行   Esc 閉じる')
        layout = QVBoxLayout(self); layout.setContentsMargins(14,32,14,14); layout.setSpacing(8)
        self.selection_tools = QWidget()
        buttons = QHBoxLayout(self.selection_tools); buttons.setContentsMargins(0,0,0,0)
        for title, callback in [('全選択 (Ctrl+A)', lambda:self.select_all(True)), ('全解除 (Ctrl+Shift+A)', lambda:self.select_all(False)), ('戻る (←)', self.go_back)]:
            button = QPushButton(title); button.clicked.connect(callback); buttons.addWidget(button)
        buttons.addStretch()
        self.selection_tools.hide()
        for w in (self.search,self.tabs,self.selection_tools,self.list,self.footer): layout.addWidget(w)
        self.setStyleSheet('''QWidget{background:#202b29;color:#e5ebf3;font-family:"Yu Gothic UI";font-size:13px;} QLineEdit{background:#101720;border:1px solid #40536d;border-radius:7px;padding:5px 10px;font-size:15px;} QTreeWidget{border:0;outline:0;background:#202b29;} QTreeWidget::item{height:35px;padding:0 6px;} QTreeWidget::item:selected{background:#304d70;color:white;} QTabBar::tab{padding:7px 17px;color:#9eafc3;} QTabBar::tab:selected{background:#2a3b50;color:#8cbcff;border-radius:5px;} QLabel{color:#8d9caf;font-size:11px;} QMenu{background:#202b39;border:1px solid #435369;padding:5px;} QMenu::item{padding:8px 20px;} QMenu::item:selected{background:#304d70;}''')
        self.tray = QSystemTrayIcon(tray_icon(), self); self.tray.setToolTip('FRB Launch — Ctrl+Shift+;')
        traymenu = QMenu(self)
        traymenu.addAction('開く', self.summon)
        traymenu.addAction('設定フォルダーを開く', lambda:self.open_target(str(CONFIG.parent)))
        traymenu.addAction('アプリ一覧を更新', self.refresh_apps)
        traymenu.addAction('アプリ一覧JSONを開く', lambda:self.open_target(str(STATE/'apps_cache.json')))
        traymenu.addAction('ログフォルダーを開く', lambda:self.open_target(str(STATE)))
        traymenu.addSeparator(); traymenu.addAction('終了', self.quit)
        self.tray.setContextMenu(traymenu); self.tray.activated.connect(lambda r:self.summon() if r==QSystemTrayIcon.ActivationReason.Trigger else None)
        self.tray.show()
        self.search.textChanged.connect(self.render)
        self.tabs.currentChanged.connect(self.page_changed)
        self.list.itemActivated.connect(lambda item,col:self.activate(item.data(0,Qt.ItemDataRole.UserRole)))
        self.list.itemChanged.connect(self.check_changed)
        self.list.itemEntered.connect(self.hover)
        self.hover_timer = QTimer(self); self.hover_timer.setSingleShot(True); self.hover_timer.timeout.connect(self.open_hover)
        self.search.installEventFilter(self); self.list.installEventFilter(self); self.tabs.installEventFilter(self)
        # QTreeWidget sends mouse events from its viewport, not from the tree.
        # An empty-area double-click navigates back only while inside a submenu.
        self.list.viewport().installEventFilter(self)
        QApplication.instance().applicationStateChanged.connect(self.app_state)
        self.page_shortcuts = []
        for index in range(12):
            shortcut = QShortcut(QKeySequence(f'F{index+1}'), self)
            shortcut.activated.connect(lambda i=index:self.switch_page(i))
            self.page_shortcuts.append(shortcut)
        self.hover_watch = QTimer(self);self.hover_watch.setInterval(60)
        self.hover_watch.timeout.connect(self.check_hover_menus);self.hover_watch.start()
        self.reload(True)
        QTimer.singleShot(0,self.refresh_apps)
        self.registered_key = ''
        self.register_key()
        self.restore_window_height()
        position = self.settings.value('position')
        if position: self.move(position)
        else:
            screen=QApplication.primaryScreen().availableGeometry();self.move(screen.center()-self.rect().center())

    FRAME_WIDTH = 6
    FRAME_TOP = 24

    def frame_inner_rect(self):
        return QRectF(self.FRAME_WIDTH + .5, self.FRAME_TOP + .5,
                      self.width() - 2 * self.FRAME_WIDTH - 1,
                      self.height() - self.FRAME_TOP - self.FRAME_WIDTH - 1)

    def frame_hit(self, pos):
        return self.rect().contains(pos.toPoint()) and not self.frame_inner_rect().contains(pos)

    def restore_window_height(self):
        try:
            height = int(self.settings.value('window_height', 440))
        except (TypeError, ValueError):
            height = 440
        screen = self.screen().availableGeometry()
        self.resize(self.width(), max(self.minimumHeight(), min(height, screen.height())))

    def resize_edge(self, pos):
        if not self.rect().contains(pos.toPoint()): return None
        if pos.y() < self.FRAME_WIDTH: return 'top'
        if pos.y() >= self.height() - self.FRAME_WIDTH: return 'bottom'
        return None

    def save_window_height(self):
        self.settings.setValue('window_height', self.height())
        self.settings.sync()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        outer = QRectF(self.rect()).adjusted(.5, .5, -.5, -.5)
        gradient = QLinearGradient(0, 0, 0, self.FRAME_TOP)
        gradient.setColorAt(0, QColor('#6b756e'))
        gradient.setColorAt(1, QColor('#43524b'))
        painter.setBrush(gradient)
        painter.setPen(QPen(QColor('#d0d7cf'), 1))
        painter.drawRoundedRect(outer, self.CORNER_RADIUS, self.CORNER_RADIUS)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor('#27362e'), 1))
        painter.drawRoundedRect(outer.adjusted(1, 1, -1, -1), self.CORNER_RADIUS - 1, self.CORNER_RADIUS - 1)
        inner = self.frame_inner_rect()
        painter.setBrush(QColor('#202b29'))
        painter.setPen(QPen(QColor('#abb5ab'), 1))
        painter.drawRoundedRect(inner, 3, 3)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor('#101a17'), 1))
        painter.drawRoundedRect(inner.adjusted(1, 1, -1, -1), 2, 2)
        painter.end()

    def mousePressEvent(self, event):
        edge = self.resize_edge(event.position())
        if event.button() == Qt.MouseButton.LeftButton and edge:
            self.hover_timer.stop(); self.pending_menu_item = None
            if self.menu: self.menu.close()
            self._frame_drag = None
            self._height_drag = (edge, event.globalPosition().toPoint().y(), self.geometry())
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
        resize = getattr(self, '_height_drag', None)
        if resize and event.buttons() & Qt.MouseButton.LeftButton:
            edge, start_y, original = resize
            delta = event.globalPosition().toPoint().y() - start_y
            requested = original.height() + (delta if edge == 'bottom' else -delta)
            height = max(self.minimumHeight(), min(requested, self.screen().availableGeometry().height()))
            top = original.y() if edge == 'bottom' else original.y() + original.height() - height
            self.setGeometry(original.x(), top, original.width(), height)
            event.accept(); return
        self.setCursor(Qt.CursorShape.SizeVerCursor if self.resize_edge(event.position()) else Qt.CursorShape.ArrowCursor)
        drag = getattr(self, '_frame_drag', None)
        if drag and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(drag[1] + event.globalPosition().toPoint() - drag[0])
            event.accept(); return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._frame_drag = None
            if getattr(self, '_height_drag', None):
                self._height_drag = None
                self.save_window_height()
                self.settings.setValue('position', self.pos())
                self.settings.sync()
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        if not getattr(self, '_height_drag', None): self.unsetCursor()
        super().leaveEvent(event)

    def update_window_shape(self):
        path=QPainterPath()
        path.addRoundedRect(QRectF(self.rect()),self.CORNER_RADIUS,self.CORNER_RADIUS)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_window_shape()
        if self.isVisible() and hasattr(self, 'settings'): self.save_window_height()

    def showEvent(self, event):
        if self.data is not None:self.reload()
        self.update_window_shape()
        super().showEvent(event)

    def row_icon(self, row):
        path=row.get('_icon_file') or row.get('_file')
        key=path or row.get('icon_key','command')
        if key not in self.icon_cache:
            self.icon_cache[key]=self.file_icons.icon(QFileInfo(path)) if path and Path(path).is_file() else icon(row.get('icon_key','command'))
        return self.icon_cache[key]

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
        self.footer.setText(str(message))

    def register_key(self):
        key=(self.data or {}).get('launch_hotkey','Ctrl+Shift+;')
        if key==self.registered_key: return
        windows.unhotkey(int(self.winId()))
        try:
            windows.hotkey(int(self.winId()),key);self.registered_key=key
        except Exception as e:
            self.registered_key='';self.error(e)

    def reload(self, force=False):
        try:
            stat=CONFIG.stat();stamp=stat.st_mtime_ns
            if not force and stamp==self.mtime and stat.st_size==self.config_size:return
            fresh=load(CONFIG)
            Expander(fresh)  # Validate timezone before swapping the active data.
            self.data=installed_apps.attach(fresh,self.app_records);self.mtime=stamp;self.config_size=stat.st_size
            self.tabs.blockSignals(True)
            while self.tabs.count():self.tabs.removeTab(0)
            self.pages=sorted([p for p in fresh['pages'] if p.get('enabled',True)],key=lambda p:p.get('sort_order',0))
            for p in self.pages:self.tabs.addTab(p['title'])
            ids=[p['page_id'] for p in self.pages]
            if self.page_id not in ids:self.page_id=ids[0]
            self.tabs.setCurrentIndex(ids.index(self.page_id));self.tabs.blockSignals(False)
            self.stack=[];self.selection=None;self.checked.clear();self.render()
            if hasattr(self,'registered_key'):self.register_key()
        except Exception as e:self.error('設定の読込に失敗: '+str(e))

    def nativeEvent(self, kind, message):
        if windows.IS_WINDOWS:
            msg=wintypes.MSG.from_address(int(message))
            if msg.message==0x0312:
                QTimer.singleShot(0,self.summon);return True,0
        return super().nativeEvent(kind,message)

    def summon(self):
        if self.busy:self.error('処理の完了を待っています');return
        if self.isVisible():self.dismiss();return
        self.target=windows.foreground();self.reload()
        self.stack=[];self.selection=None;self.checked.clear();self.search.clear();self.render()
        if not any(s.availableGeometry().intersects(self.frameGeometry()) for s in QApplication.screens()):
            self.move(QApplication.primaryScreen().availableGeometry().center()-self.rect().center())
        self.show();self.raise_();self.activateWindow();self.search.setFocus()

    def dismiss(self):
        if self.menu:self.menu.close()
        self.save_window_height()
        self.hover_timer.stop();self.settings.setValue('position',self.pos());self.settings.setValue('page',self.page_id);self.hide()

    def app_state(self,state):
        if state==Qt.ApplicationState.ApplicationInactive and self.isVisible():self.dismiss()

    def page_key(self, event):
        if event.modifiers()!=Qt.KeyboardModifier.NoModifier:return False
        index=event.key()-Qt.Key.Key_F1
        if 0<=index<12:
            self.switch_page(index);return True
        return False

    def switch_page(self, index):
        # F12 keeps its existing send/confirm meaning in the selection screen.
        if index==11 and self.selection:
            self.confirm_selection();return
        if index>=self.tabs.count():return
        if self.menu:self.menu.close()
        self.hover_timer.stop();self.pending_menu_item=None
        self.stack=[];self.selection=None;self.checked.clear()
        self.tabs.setCurrentIndex(index)
        self.search.clear();self.render();self.search.setFocus()

    def page_changed(self,index):
        if self.data and index>=0:
            self.page_id=self.pages[index]['page_id'];self.stack=[];self.selection=None;self.checked.clear();self.render()

    def children(self,row=None):
        if row and row.get('item_kind')=='directory':
            path=Path(self.expander().expand(row['launch_browse_target']))
            result=[]
            for p in sorted(path.iterdir(),key=lambda p:(not p.is_dir(),p.name.casefold())):
                result.append(dict(item_id=str(p),title=p.name,description=str(p),item_kind='directory' if p.is_dir() else 'command',icon_key='folder.yellow' if p.is_dir() else 'file',launch_browse_target=str(p),launch_actions=[{'launch_action_type':'Open','launch_target':str(p)}],_file=str(p)))
            return result
        parent=row['item_id'] if row else ''
        return sorted([x for x in self.data['items'] if x.get('enabled',True) and x['page_id']==(row['page_id'] if row else self.page_id) and x.get('parent_item_id','')==parent],key=lambda x:x.get('sort_order',0))

    def render(self,*args):
        if not self.data:return
        self.hover_timer.stop();self.pending_menu_item=None
        self.selection_tools.setVisible(self.selection is not None)
        self.list.blockSignals(True);self.list.clear()
        query=self.search.text().strip()
        self.list.order_enabled=not query and not self.selection and not (self.stack and (self.stack[-1]['item_kind']=='directory' or self.stack[-1].get('launch_source')=='installed_apps'))
        self.list.order_rows=[]
        self.list.order_page=self.page_id
        self.list.order_parent=self.stack[-1]['item_id'] if self.stack else ''
        try:
            if self.selection:
                candidates=sorted([c for c in self.data.get('launch_choices',[]) if c.get('enabled',True) and c['group_id']==self.selection['launch_selection_group_id']],key=lambda c:c.get('sort_order',0))
                pairs=[(c,'') for c in candidates if all(w in json.dumps(c,ensure_ascii=False).casefold() for w in query.casefold().split())]
            elif query:pairs=searchable_rows(self.data,query)
            else:pairs=[(x,'') for x in self.children(self.stack[-1] if self.stack else None)]
            if self.list.order_enabled:self.list.order_rows=[row for row,path in pairs]
            for row,path in pairs:
                desc=row.get('description','')+('  ·  '+path if path else '')
                isfolder=row.get('item_kind') in {'category','directory'}
                q=QTreeWidgetItem([row['title']+('  ›' if isfolder else ''),desc]);q.setData(0,Qt.ItemDataRole.UserRole,row)
                q.setToolTip(0,row['title']);q.setToolTip(1,desc)
                q.setIcon(0,self.row_icon(row))
                q.setForeground(1,QColor('#a6b4c7'))
                if self.selection:
                    q.setFlags(q.flags()|Qt.ItemFlag.ItemIsUserCheckable);q.setCheckState(0,Qt.CheckState.Checked if row['choice_id'] in self.checked else Qt.CheckState.Unchecked)
                self.list.addTopLevelItem(q)
            if self.list.topLevelItemCount():self.list.setCurrentItem(self.list.topLevelItem(0))
            self.footer.setText(('Space チェック / F12 入力 / ← 戻る  選択 '+str(len(self.checked))+'件') if self.selection else (' / '.join(x['title'] for x in self.stack) or '↑↓ 選択   → 展開   Enter 実行   F1〜F12 / Ctrl+PageUp/Down Page切替'))
        except Exception as e:self.error(e)
        finally:self.list.blockSignals(False)

    def check_changed(self,item,col):
        if self.selection:
            key=item.data(0,Qt.ItemDataRole.UserRole)['choice_id']
            if item.checkState(0)==Qt.CheckState.Checked:self.checked.add(key)
            else:self.checked.discard(key)
            self.footer.setText(f'Space チェック / F12 入力 / ← 戻る  選択 {len(self.checked)}件')

    def select_all(self, selected):
        if not self.selection:return
        # Apply to the whole group, including choices hidden by the search.
        self.checked = {c['choice_id'] for c in self.data.get('launch_choices', [])
                        if c.get('enabled', True) and c['group_id'] == self.selection['launch_selection_group_id']} if selected else set()
        self.render()
        self.list.setFocus()

    def go_back(self):
        if self.selection:
            self.selection = None; self.checked.clear()
        elif self.stack:
            self.stack.pop()
        self.search.clear(); self.render(); self.list.setFocus()

    def hover(self,q,col):
        if self.selection or QApplication.mouseButtons() & Qt.MouseButton.LeftButton or getattr(self.list,'order_dragging',False):return
        self.list.setCurrentItem(q)
        self.pending_menu_item=q
        self.hover_timer.start(int(self.data.get('launch_hover_delay_ms',250)))

    def open_hover(self):
        q=self.pending_menu_item
        if q and self.isVisible():
            row=q.data(0,Qt.ItemDataRole.UserRole)
            if row.get('item_kind') in {'category','directory'}:
                if self.list.itemAt(self.list.viewport().mapFromGlobal(QCursor.pos()))==q:
                    self.cascade(row,q,"hover")

    def check_hover_menus(self, pos=None, now=None):
        pos=QCursor.pos() if pos is None else pos
        now=time.monotonic() if now is None else now
        # Stop delayed opens as soon as their originating row is left.
        if self.pending_menu_item and self.list.itemAt(self.list.viewport().mapFromGlobal(pos))!=self.pending_menu_item:
            self.hover_timer.stop();self.pending_menu_item=None
        menu=self.menu
        while menu and menu.isVisible():
            if menu.hover_timer.isActive() and menu.actionAt(menu.mapFromGlobal(pos))!=menu.activeAction():menu.hover_timer.stop()
            if menu.open_mode=="hover":
                related=False;desc=menu
                while desc and desc.isVisible():
                    if desc.rect().contains(desc.mapFromGlobal(pos)):related=True;break
                    desc=desc.child
                parent=menu.parentWidget()
                if isinstance(parent,CascadeMenu):
                    related=related or (parent.isVisible() and parent.actionAt(parent.mapFromGlobal(pos))==menu.owner_action)
                elif menu.owner_item:
                    related=related or self.list.visualItemRect(menu.owner_item).contains(self.list.viewport().mapFromGlobal(pos))
                if related:menu.outside_since=None
                elif menu.outside_since is None:menu.outside_since=now
                elif now-menu.outside_since>=.25:
                    menu.close();break
            menu=menu.child

    def persist_order(self, ids, page, parent, selected):
        try:
            self.data,self.mtime=save_order(CONFIG,self.mtime,page,parent,ids)
            self.data=installed_apps.attach(self.data,self.app_records)
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
                    for action in menu.actions():
                        if action.data() and action.data()['item_id']==selected:menu.setActiveAction(action);break
                else:refresh(menu.child)
            QTimer.singleShot(0,lambda:refresh(self.menu))
            self.footer.setText('表示順を保存しました')
            return True
        except Exception as e:
            self.error('表示順を保存できません: '+str(e));return False

    def focus_search(self, select=True):
        self.hover_timer.stop();self.pending_menu_item=None
        if self.menu:self.menu.close()
        self.activateWindow();self.search.setFocus()
        if select:self.search.selectAll()

    def fill_cascade(self, menu, parent):
        if isinstance(menu,AppCascadeMenu):
            menu.populate(self.children(parent));return
        menu.order_enabled=parent['item_kind']=='category' and parent.get('launch_source')!='installed_apps'
        menu.order_page=parent.get('page_id',self.page_id)
        menu.order_parent=parent.get('item_id','')
        menu.order_context=parent
        menu.order_rows=[]
        try:
            for row in self.children(parent):
                folder = row['item_kind'] in {'category','directory'}
                label = row['title'] + ('  ›' if folder else '')
                if not folder and parent['item_kind']!='directory':label += '    '+row.get('description','')
                action = menu.addAction(self.row_icon(row),label)
                action.setToolTip(row.get('description',''))
                action.setData(row)
                if menu.order_enabled:menu.order_rows.append(row)
                if folder:
                    def open_child(mode="keyboard", m=menu, r=row, a=action):
                        if m.child:m.child.close();m.child.deleteLater()
                        m.child=(AppCascadeMenu if r.get('launch_source')=='installed_apps' else CascadeMenu)(parent=m,launcher=self)
                        m.child.open_mode=mode;m.child.owner_action=a
                        self.fill_cascade(m.child,r)
                        m.child.popup(m.mapToGlobal(m.actionGeometry(a).topRight()))
                        m.child.setFocus()
                    menu.openers[action]=open_child
                    action.triggered.connect(lambda checked=False, fn=open_child:fn())
                else:
                    action.triggered.connect(lambda checked=False,r=row:self.run_menu_item(r))
            if parent['item_kind']=='directory':
                menu.addSeparator();menu.addAction('このフォルダーを開く',lambda:self.run_menu_item(parent))
            if menu.isEmpty():menu.addAction('項目なし').setEnabled(False)
        except Exception as e:menu.addAction(str(e)).setEnabled(False)

    def run_menu_item(self, row):
        if self.menu:self.menu.close()
        self.activate(row)

    def cascade(self,row,q=None,mode="keyboard"):
        self.hover_timer.stop();self.pending_menu_item=None
        if self.menu:self.menu.close();self.menu.deleteLater()
        self.menu=(AppCascadeMenu if row.get('launch_source')=='installed_apps' else CascadeMenu)(parent=self,launcher=self)
        self.menu.open_mode=mode;self.menu.owner_item=q or self.list.currentItem()
        self.fill_cascade(self.menu,row)
        pos=self.list.viewport().mapToGlobal(self.list.visualItemRect(q or self.list.currentItem()).topRight())
        self.menu.popup(pos);self.menu.setFocus()

    def activate(self,row):
        if not row:return
        if self.selection:
            q=self.list.currentItem();q.setCheckState(0,Qt.CheckState.Unchecked if q.checkState(0)==Qt.CheckState.Checked else Qt.CheckState.Checked);return
        kind=row.get('item_kind')
        if kind=='category':
            self.stack.append(row);self.search.clear();self.render();self.list.setFocus();return
        if kind=='selection':
            self.selection=row;self.checked.clear();self.search.clear();self.render();self.list.setFocus();return
        self.execute(row)

    def confirm_selection(self):
        if not self.selection or not self.checked:return
        row=self.selection
        choices=sorted([c for c in self.data['launch_choices'] if c['choice_id'] in self.checked],key=lambda c:c.get('sort_order',0))
        value=row.get('launch_selection_separator','; ').join(str(c.get(row.get('launch_selection_value_field','value'),'')) for c in choices)
        self.execute(row,{row.get('launch_selection_result_name','recipients'):value})

    def eventFilter(self,obj,event):
        if obj is self.list.viewport() and event.type()==QEvent.Type.MouseButtonDblClick:
            # Enter opens a category *inside* the launcher window. Double-clicking
            # unused list space has the same meaning as the existing Left/Back key.
            # Never steal double-clicks on items, or at the top/root level.
            if (event.button()==Qt.MouseButton.LeftButton
                    and (self.stack or self.selection is not None)
                    and self.list.itemAt(event.position().toPoint()) is None):
                self.go_back()
                event.accept()
                return True
        if obj==self.tabs:
            if event.type()==QEvent.Type.KeyPress and event.modifiers()==Qt.KeyboardModifier.NoModifier:
                key=event.key()
                if key==Qt.Key.Key_Up:
                    if self.list.topLevelItemCount():
                        self.list.setCurrentItem(self.list.topLevelItem(self.list.topLevelItemCount()-1));self.list.setFocus(Qt.FocusReason.TabFocusReason);self.list.scrollToItem(self.list.currentItem())
                    event.accept();return True
                if key in (Qt.Key.Key_Left,Qt.Key.Key_Right):
                    index=max(0,min(self.tabs.count()-1,self.tabs.currentIndex()+(1 if key==Qt.Key.Key_Right else -1)))
                    if self.tabs.count():self.tabs.setCurrentIndex(index)
                    event.accept();return True
            if event.type()==QEvent.Type.KeyPress and event.key()==Qt.Key.Key_Down:
                if self.list.topLevelItemCount():
                    self.list.setCurrentItem(self.list.topLevelItem(0))
                self.list.setFocus(Qt.FocusReason.TabFocusReason)
                if self.list.currentItem():self.list.scrollToItem(self.list.currentItem())
                event.accept();return True
            return super().eventFilter(obj,event)
        if event.type()==QEvent.Type.KeyPress:
            k=event.key();ctrl=bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)
            if ctrl and k==Qt.Key.Key_F:
                self.focus_search();return True
            if self.page_key(event):return True
            # IME owns its pre-edit and candidate keystrokes.
            if getattr(self,'composing',False):return False
            if self.selection and ctrl and k==Qt.Key.Key_A:
                self.select_all(not bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier));return True
            if k==Qt.Key.Key_Left and (self.selection or obj==self.list or not self.search.text()):
                self.go_back();return True
            if k==Qt.Key.Key_Right and not self.selection and (obj==self.list or not self.search.text()):
                q=self.list.currentItem()
                if q:
                    row=q.data(0,Qt.ItemDataRole.UserRole)
                    if row.get('item_kind') in {'category','directory'}:self.cascade(row,q)
                return True
            if k in (Qt.Key.Key_Down,Qt.Key.Key_Up):
                i=self.list.indexOfTopLevelItem(self.list.currentItem())
                if k==Qt.Key.Key_Up and obj==self.list and i<=0:
                    self.tabs.setFocus(Qt.FocusReason.TabFocusReason)
                    event.accept();return True
                if k==Qt.Key.Key_Down and obj==self.list and i>=self.list.topLevelItemCount()-1:
                    self.tabs.setFocus(Qt.FocusReason.TabFocusReason);event.accept();return True
                i=max(0,min(self.list.topLevelItemCount()-1,i+(1 if k==Qt.Key.Key_Down else -1)))
                if self.list.topLevelItemCount():self.list.setCurrentItem(self.list.topLevelItem(i))
                self.list.setFocus();return True
            if k==Qt.Key.Key_Escape:
                if self.search.text():self.search.clear()
                elif self.selection:self.selection=None;self.render()
                elif self.stack:self.stack.pop();self.render()
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
                    if self.stack:self.stack.pop();self.render()
                    return True
                if k==Qt.Key.Key_Space and self.selection:
                    if self.list.currentItem():self.activate(self.list.currentItem().data(0,Qt.ItemDataRole.UserRole))
                    return True
                if event.text() and not ctrl and not event.modifiers() & Qt.KeyboardModifier.AltModifier:
                    self.search.setFocus();QApplication.sendEvent(self.search,QKeyEvent(event.type(),k,event.modifiers(),event.text()));return True
                if k==Qt.Key.Key_Backspace:self.search.setFocus();self.search.backspace();return True
        if obj==self.list and event.type()==QEvent.Type.InputMethod:
            self.search.setFocus();QApplication.sendEvent(self.search,event);return True
        if obj==self.search and event.type()==QEvent.Type.InputMethod:
            self.composing=bool(event.preeditString())
        return super().eventFilter(obj,event)

    def open_target(self,target,browser=""):
        if browser.lower()=="chrome":windows.open_chrome(target);return
        if not windows.IS_WINDOWS:raise RuntimeError('起動操作はWindowsで利用できます')
        if target.lower().startswith('shell:'):
            import subprocess
            subprocess.Popen(['explorer.exe',target])
        else:os.startfile(target)

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
            for raw in row.get('launch_actions',[]):
                step={k:([ex.expand(a) for a in val] if k=='launch_arguments' else ex.expand(val) if isinstance(val,str) else val) for k,val in raw.items()}
                self.queue.append(step)
            self.busy=True;DIAG.info('QUEUE steps=%s',len(self.queue));self.dismiss();QTimer.singleShot(180,self.next_step)
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
                if step.get('launch_browser'):self.open_target(step['launch_target'],step['launch_browser'])
                else:self.open_target(step['launch_target'])
            elif kind=='Run':
                program=step['launch_program'];args=step.get('launch_arguments',[]);cwd=step.get('launch_working_directory') or str(ROOT)
                args,transcript=wifi_transcript_arguments(program,args,STATE)
                DIAG.info('RUN program=%s cwd=%s console=%s wait=%s transcript=%s',program,cwd,step.get('launch_show_console',False),step.get('launch_wait_for_exit',False),transcript)
                self.proc = start_process(program, args, cwd, step.get('launch_show_console',False))
                DIAG.info('PROCESS started pid=%s',getattr(self.proc,'pid',None))
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
        self.process_timer.stop()
        if self.timedout:self.busy=False;return
        if code!=0:self.fail(f'外部処理の終了コード: {code}（トレイの「ログフォルダーを開く」で詳細を確認）')
        else:self.next_step()

    def fail(self,message):
        self.queue=[];self.busy=False
        if hasattr(self,'process_timer'):self.process_timer.stop()
        self.error(message)

    def closeEvent(self,event):event.ignore();self.dismiss()
    def quit(self):
        if self.apps_proc:
            self.apps_proc.kill();self.apps_proc.wait();self.apps_output.unlink(missing_ok=True)
        windows.unhotkey(int(self.winId()));self.dismiss();self.tray.hide();QApplication.quit()


def main():
    app=QApplication(sys.argv);app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(application_icon())
    # One user/session-local instance, independent of its installation directory.
    name='FRBLaunch-'+os.environ.get('USERNAME',os.environ.get('USER','default'))
    lock=QLockFile(str(STATE/'instance.lock'));lock.setStaleLockTime(0)
    if not lock.tryLock(0):
        client=QLocalSocket();client.connectToServer(name)
        if client.waitForConnected(1500):client.write(b'show');client.waitForBytesWritten(1000)
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
        DIAG.info('DESKTOP_OPEN_RESULT visible=%s active=%s',
                  window.isVisible(), window.isActiveWindow())
        QTimer.singleShot(400, lambda: DIAG.info(
            'DESKTOP_OPEN_AFTER_400MS visible=%s active=%s',
            window.isVisible(), window.isActiveWindow()))
    def dismiss_from_outside_click():
        # A Tool/always-on-top window may not receive ApplicationInactive when
        # summoned from the desktop. Use the existing mouse hook as fallback.
        if window.isVisible() and QApplication.activeModalWidget() is None:
            DIAG.info('OUTSIDE_CLICK_DISMISS')
            window.dismiss()

    try:
        desktop_click = DesktopDoubleClick(
            open_from_desktop, DIAG,
            on_outside_click=dismiss_from_outside_click,
            is_launcher_visible=window.isVisible,
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
    def wake():
        sock=server.nextPendingConnection()
        if sock:sock.close();sock.deleteLater()
        if not window.isVisible():window.summon()
        else:window.raise_();window.activateWindow()
    server.newConnection.connect(wake)
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
