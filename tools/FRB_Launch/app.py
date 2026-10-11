import sys
import os
import json
import logging
import time
from pathlib import Path
from ctypes import wintypes
import ctypes
from PySide6.QtCore import Qt, QTimer, QSettings, QEvent, QLockFile, QDir
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QKeyEvent, QShortcut, QKeySequence, QCursor
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLineEdit, QTabBar, QTreeWidget, QTreeWidgetItem, QMenu, QSystemTrayIcon, QFileIconProvider, QMessageBox, QLabel, QHBoxLayout, QPushButton)
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtCore import QFileInfo
from core import load, Expander, searchable_rows
import windows
from ordering import save_order
from reorder_widgets import OrderDragMixin, ReorderTree
from process_runner import start_process
from launch_diagnostics import make_logger, wifi_transcript_arguments
from runtime_paths import launch_home

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


class CascadeMenu(OrderDragMixin,QMenu):
    """Explicit child popups: selecting a folder never opens it automatically."""
    def __init__(self, title='', parent=None, launcher=None):
        super().__init__(title, parent)
        self.launcher = launcher or parent
        self.child = None
        self.open_mode = "keyboard"; self.owner_item = None; self.owner_action = None; self.outside_since = None
        self.setup_order_drag();self.order_press=None
        self.openers = {}
        self.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        self.setStyleSheet('QMenu { menu-scrollable: 1; }')
        self.hover_timer = QTimer(self); self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(lambda:self.open_current("hover"))

    def select_first(self):
        first = next((a for a in self.actions() if a.isEnabled() and not a.isSeparator()), None)
        if first:self.setActiveAction(first)

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
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Escape):
            parent = self.parentWidget()
            self.close()
            if isinstance(parent, CascadeMenu):parent.setFocus()
            else:self.launcher.list.setFocus()
            event.accept();return
        action=self.activeAction()
        if key in (Qt.Key.Key_Return,Qt.Key.Key_Enter) and action and action.data() and action.data().get('item_kind')=='directory':
            self.launcher.run_menu_item(action.data());event.accept();return
        if key == Qt.Key.Key_Right or (key in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and action in self.openers):
            self.open_current();event.accept();return
        if (mods & Qt.KeyboardModifier.ControlModifier and key==Qt.Key.Key_F):
            self.launcher.focus_search();event.accept();return
        if event.text() and event.text().isprintable() and not mods & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier):
            self.launcher.focus_search(False)
            QApplication.sendEvent(self.launcher.search, QKeyEvent(event.type(),key,mods,event.text()))
            event.accept();return
        super().keyPressEvent(event)

    def inputMethodEvent(self, event):
        self.launcher.focus_search(False)
        QApplication.sendEvent(self.launcher.search,event)



class Launcher(QWidget):
    def __init__(self):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle('FRB Launch'); self.resize(390,440)
        self.setWindowIcon(icon('command'))
        self.data = None; self.mtime = None; self.target = 0; self.busy = False
        self.stack = []; self.selection = None; self.checked = set(); self.return_page = None
        self.menu = None; self.pending_menu_item = None; self.file_icons = QFileIconProvider()
        self.settings = QSettings(str(STATE / 'state.ini'), QSettings.Format.IniFormat)
        self.page_id = self.settings.value('page', 'work')
        self.search = QLineEdit(); self.search.setPlaceholderText('検索 — 全Pageから探す'); self.search.setClearButtonEnabled(True)
        self.tabs = QTabBar(); self.tabs.setExpanding(False); self.tabs.setDrawBase(False)
        self.list = ReorderTree(self); self.list.setColumnCount(2); self.list.setHeaderHidden(True); self.list.setRootIsDecorated(False)
        self.list.setColumnWidth(0,180); self.list.setMouseTracking(True); self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.footer = QLabel('↑↓ 選択   → 展開   ← 戻る   Enter 実行   Esc 閉じる')
        layout = QVBoxLayout(self); layout.setContentsMargins(12,12,12,9); layout.setSpacing(8)
        self.selection_tools = QWidget()
        buttons = QHBoxLayout(self.selection_tools); buttons.setContentsMargins(0,0,0,0)
        for title, callback in [('全選択 (Ctrl+A)', lambda:self.select_all(True)), ('全解除 (Ctrl+Shift+A)', lambda:self.select_all(False)), ('戻る (←)', self.go_back)]:
            button = QPushButton(title); button.clicked.connect(callback); buttons.addWidget(button)
        buttons.addStretch()
        self.selection_tools.hide()
        for w in (self.search,self.tabs,self.selection_tools,self.list,self.footer): layout.addWidget(w)
        self.setStyleSheet('''QWidget{background:#19212c;color:#e5ebf3;font-family:"Yu Gothic UI";font-size:13px;} QLineEdit{background:#101720;border:1px solid #40536d;border-radius:7px;padding:10px;font-size:15px;} QTreeWidget{border:0;outline:0;background:#19212c;} QTreeWidget::item{height:35px;padding:0 6px;} QTreeWidget::item:selected{background:#304d70;color:white;} QTabBar::tab{padding:7px 17px;color:#9eafc3;} QTabBar::tab:selected{background:#2a3b50;color:#8cbcff;border-radius:5px;} QLabel{color:#8d9caf;font-size:11px;} QMenu{background:#202b39;border:1px solid #435369;padding:5px;} QMenu::item{padding:8px 20px;} QMenu::item:selected{background:#304d70;}''')
        self.tray = QSystemTrayIcon(self.windowIcon(), self); self.tray.setToolTip('FRB Launch — Ctrl+Shift+;')
        traymenu = QMenu(self)
        traymenu.addAction('開く', self.summon); traymenu.addAction('設定を再読込', lambda:self.reload(True))
        traymenu.addAction('設定フォルダーを開く', lambda:self.open_target(str(CONFIG.parent)))
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
        QApplication.instance().applicationStateChanged.connect(self.app_state)
        self.page_shortcuts = []
        for index in range(12):
            shortcut = QShortcut(QKeySequence(f'F{index+1}'), self)
            shortcut.activated.connect(lambda i=index:self.switch_page(i))
            self.page_shortcuts.append(shortcut)
        self.hover_watch = QTimer(self);self.hover_watch.setInterval(60)
        self.hover_watch.timeout.connect(self.check_hover_menus);self.hover_watch.start()
        self.reload(True)
        self.registered_key = ''
        self.register_key()
        position = self.settings.value('position')
        if position: self.move(position)
        else:
            screen=QApplication.primaryScreen().availableGeometry();self.move(screen.center()-self.rect().center())

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
            stamp=CONFIG.stat().st_mtime_ns
            if not force and stamp==self.mtime:return
            fresh=load(CONFIG)
            Expander(fresh)  # Validate timezone before swapping the active data.
            self.data=fresh;self.mtime=stamp
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
        self.list.order_enabled=not query and not self.selection and not (self.stack and self.stack[-1]['item_kind']=='directory')
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
                q.setIcon(0,self.file_icons.icon(QFileInfo(row['_file'])) if '_file' in row else icon(row.get('icon_key','mail')))
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
                    context=menu.order_context;menu.clear();menu.openers.clear()
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
        menu.order_enabled=parent['item_kind']=='category'
        menu.order_page=parent.get('page_id',self.page_id)
        menu.order_parent=parent.get('item_id','')
        menu.order_context=parent
        menu.order_rows=[]
        try:
            for row in self.children(parent):
                folder = row['item_kind'] in {'category','directory'}
                label = row['title'] + ('  ›' if folder else '')
                if not folder and parent['item_kind']!='directory':label += '    '+row.get('description','')
                action = menu.addAction(icon(row.get('icon_key','command')),label)
                action.setToolTip(row.get('description',''))
                action.setData(row)
                if menu.order_enabled:menu.order_rows.append(row)
                if folder:
                    def open_child(mode="keyboard", m=menu, r=row, a=action):
                        if m.child:m.child.close();m.child.deleteLater()
                        m.child=CascadeMenu(parent=m,launcher=self)
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
        self.menu=CascadeMenu(parent=self,launcher=self)
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
        if obj==self.tabs:
            if event.type()==QEvent.Type.KeyPress and event.key()==Qt.Key.Key_Down:
                if not self.list.currentItem() and self.list.topLevelItemCount():
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
                i=self.list.indexOfTopLevelItem(self.list.currentItem());i=max(0,min(self.list.topLevelItemCount()-1,i+(1 if k==Qt.Key.Key_Down else -1)))
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
        windows.unhotkey(int(self.winId()));self.dismiss();self.tray.hide();QApplication.quit()


def main():
    app=QApplication(sys.argv);app.setQuitOnLastWindowClosed(False)
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
    def wake():
        sock=server.nextPendingConnection()
        if sock:sock.close();sock.deleteLater()
        if not window.isVisible():window.summon()
        else:window.raise_();window.activateWindow()
    server.newConnection.connect(wake)
    if '--preview' in sys.argv:window.summon()
    result=app.exec();server.close();lock.unlock();return result

if __name__=='__main__':
    try:sys.exit(main())
    except Exception:
        logging.exception('Startup failed')
        DIAG.exception('Startup failed')
        if QApplication.instance():QMessageBox.critical(None,'FRB Launch','起動に失敗しました。LOCALAPPDATA/FRBLaunch/error.logを確認してください。')
        raise
