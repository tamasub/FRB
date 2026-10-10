import sys
import os
import json
import logging
from pathlib import Path
from ctypes import wintypes
import ctypes
from PySide6.QtCore import Qt, QTimer, QProcess, QSettings, QEvent, QLockFile, QDir
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QKeyEvent
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLineEdit, QTabBar, QTreeWidget, QTreeWidgetItem, QMenu, QSystemTrayIcon, QFileIconProvider, QMessageBox, QLabel, QHBoxLayout, QPushButton)
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtCore import QFileInfo
from core import load, Expander, searchable_rows
import windows

ROOT = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
CONFIG = ROOT / 'config' / 'frb_launch_sample_data_v0_1.json'
STATE = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'FRBLaunch'
STATE.mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=str(STATE / 'error.log'), encoding='utf-8', level=logging.WARNING)


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


class CascadeMenu(QMenu):
    """Explicit child popups: selecting a folder never opens it automatically."""
    def __init__(self, title='', parent=None, launcher=None):
        super().__init__(title, parent)
        self.launcher = launcher or parent
        self.child = None
        self.openers = {}
        self.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        self.setStyleSheet('QMenu { menu-scrollable: 1; }')
        self.hover_timer = QTimer(self); self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self.open_current)

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

    def mouseMoveEvent(self, event):
        before = self.activeAction()
        super().mouseMoveEvent(event)
        if self.activeAction() != before:
            if self.child:self.child.close()
            self.hover_timer.stop()
            if self.activeAction() in self.openers:
                self.hover_timer.start(int(self.launcher.data.get('launch_hover_delay_ms',250)))

    def open_current(self):
        action = self.activeAction()
        if action in self.openers:self.openers[action]()

    def keyPressEvent(self, event):
        self.hover_timer.stop()
        key = event.key(); mods = event.modifiers()
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Escape):
            parent = self.parentWidget()
            self.close()
            if isinstance(parent, CascadeMenu):parent.setFocus()
            else:self.launcher.list.setFocus()
            event.accept();return
        if key == Qt.Key.Key_Right or (key in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and self.activeAction() in self.openers):
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
        self.setWindowTitle('FRB Launch'); self.resize(710,440)
        self.setWindowIcon(icon('command'))
        self.data = None; self.mtime = None; self.target = 0; self.busy = False
        self.stack = []; self.selection = None; self.checked = set(); self.return_page = None
        self.menu = None; self.pending_menu_item = None; self.file_icons = QFileIconProvider()
        self.settings = QSettings(str(STATE / 'state.ini'), QSettings.Format.IniFormat)
        self.page_id = self.settings.value('page', 'work')
        self.search = QLineEdit(); self.search.setPlaceholderText('検索 — 全Pageから探す'); self.search.setClearButtonEnabled(True)
        self.tabs = QTabBar(); self.tabs.setExpanding(False); self.tabs.setDrawBase(False)
        self.list = QTreeWidget(); self.list.setColumnCount(2); self.list.setHeaderHidden(True); self.list.setRootIsDecorated(False)
        self.list.setColumnWidth(0,255); self.list.setMouseTracking(True); self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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
        traymenu.addSeparator(); traymenu.addAction('終了', self.quit)
        self.tray.setContextMenu(traymenu); self.tray.activated.connect(lambda r:self.summon() if r==QSystemTrayIcon.ActivationReason.Trigger else None)
        self.tray.show()
        self.search.textChanged.connect(self.render)
        self.tabs.currentChanged.connect(self.page_changed)
        self.list.itemActivated.connect(lambda item,col:self.activate(item.data(0,Qt.ItemDataRole.UserRole)))
        self.list.itemChanged.connect(self.check_changed)
        self.list.itemEntered.connect(self.hover)
        self.hover_timer = QTimer(self); self.hover_timer.setSingleShot(True); self.hover_timer.timeout.connect(self.open_hover)
        self.search.installEventFilter(self); self.list.installEventFilter(self)
        QApplication.instance().applicationStateChanged.connect(self.app_state)
        self.reload(True)
        self.registered_key = ''
        self.register_key()
        position = self.settings.value('position')
        if position: self.move(position)
        else:
            screen=QApplication.primaryScreen().availableGeometry();self.move(screen.center()-self.rect().center())

    def error(self, message):
        logging.warning('%s', message)
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

    def page_changed(self,index):
        if self.data and index>=0:
            self.page_id=self.pages[index]['page_id'];self.stack=[];self.selection=None;self.checked.clear();self.render()

    def children(self,row=None):
        if row and row.get('item_kind')=='directory':
            path=Path(Expander(self.data,QApplication.clipboard().text()).expand(row['launch_browse_target']))
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
        try:
            if self.selection:
                candidates=sorted([c for c in self.data.get('launch_choices',[]) if c.get('enabled',True) and c['group_id']==self.selection['launch_selection_group_id']],key=lambda c:c.get('sort_order',0))
                pairs=[(c,'') for c in candidates if all(w in json.dumps(c,ensure_ascii=False).casefold() for w in query.casefold().split())]
            elif query:pairs=searchable_rows(self.data,query)
            else:pairs=[(x,'') for x in self.children(self.stack[-1] if self.stack else None)]
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
            self.footer.setText(('Space チェック / F12 入力 / ← 戻る  選択 '+str(len(self.checked))+'件') if self.selection else (' / '.join(x['title'] for x in self.stack) or '↑↓ 選択   → 展開   Enter 実行   Ctrl+PageUp/Down Page切替'))
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
        if self.selection:return
        self.pending_menu_item=q
        self.hover_timer.start(int(self.data.get('launch_hover_delay_ms',250)))

    def open_hover(self):
        q=self.pending_menu_item
        if q and self.isVisible():
            row=q.data(0,Qt.ItemDataRole.UserRole)
            if row.get('item_kind') in {'category','directory'}:
                self.cascade(row,q)

    def focus_search(self, select=True):
        self.hover_timer.stop();self.pending_menu_item=None
        if self.menu:self.menu.close()
        self.activateWindow();self.search.setFocus()
        if select:self.search.selectAll()

    def fill_cascade(self, menu, parent):
        try:
            for row in self.children(parent):
                folder = row['item_kind'] in {'category','directory'}
                label = row['title'] + ('  ›' if folder else '')
                if not folder and parent['item_kind']!='directory':label += '    '+row.get('description','')
                action = menu.addAction(icon(row.get('icon_key','command')),label)
                action.setToolTip(row.get('description',''))
                if folder:
                    def open_child(m=menu, r=row, a=action):
                        if m.child:m.child.close();m.child.deleteLater()
                        m.child=CascadeMenu(parent=m,launcher=self)
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

    def cascade(self,row,q=None):
        self.hover_timer.stop();self.pending_menu_item=None
        if self.menu:self.menu.close();self.menu.deleteLater()
        self.menu=CascadeMenu(parent=self,launcher=self)
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
        if event.type()==QEvent.Type.KeyPress:
            k=event.key();ctrl=bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)
            if ctrl and k==Qt.Key.Key_F:
                self.focus_search();return True
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

    def open_target(self,target):
        if not windows.IS_WINDOWS:raise RuntimeError('起動操作はWindowsで利用できます')
        if target.lower().startswith('shell:'):
            import subprocess
            subprocess.Popen(['explorer.exe',target])
        else:os.startfile(target)

    def execute(self,row,values=None):
        if self.busy:return
        try:
            ex=Expander(self.data,QApplication.clipboard().text(),values)
            # Resolve all values before any side effects.
            self.queue=[]
            for raw in row.get('launch_actions',[]):
                step={k:([ex.expand(a) for a in val] if k=='launch_arguments' else ex.expand(val) if isinstance(val,str) else val) for k,val in raw.items()}
                self.queue.append(step)
            self.busy=True;self.dismiss();QTimer.singleShot(180,self.next_step)
        except Exception as e:self.error(e)

    def next_step(self):
        if not self.queue:self.busy=False;return
        step=self.queue.pop(0)
        try:
            kind=step['launch_action_type']
            if kind in {'SendKey','ClipboardCopy'}:
                if kind=='SendKey':windows.restore(self.target)
                QApplication.clipboard().setText(step.get('launch_text',''))
                if kind=='SendKey':windows.paste(self.target)
            elif kind=='Open':self.open_target(step['launch_target'])
            elif kind=='Run':
                program=step['launch_program'];args=step.get('launch_arguments',[]);cwd=step.get('launch_working_directory') or str(ROOT)
                if not step.get('launch_wait_for_exit'):
                    import subprocess
                    subprocess.Popen([program]+args,cwd=cwd)
                else:
                    self.timedout=False
                    self.proc=QProcess(self);self.proc.setWorkingDirectory(cwd)
                    self.proc.finished.connect(self.process_finished)
                    self.proc.errorOccurred.connect(lambda err:self.fail('外部処理に失敗: '+self.proc.errorString()))
                    self.proc.setProgram(program);self.proc.setArguments(args)
                    self.deadline=QTimer(self);self.deadline.setSingleShot(True);self.deadline.timeout.connect(self.timed_out)
                    self.deadline.start(int(step.get('launch_timeout_ms',30000)));self.proc.start();return
            QTimer.singleShot(100,self.next_step)
        except Exception as e:self.fail(str(e))

    def process_finished(self,code,status):
        self.deadline.stop()
        if not self.busy:return
        if self.timedout:self.busy=False;return
        if code!=0 or status!=QProcess.ExitStatus.NormalExit:
            self.fail(f'外部処理の終了コード: {code}')
        else:self.next_step()

    def timed_out(self):
        self.queue=[];self.timedout=True
        self.error('タイムアウトしました。後続処理を中止し、実行中の処理が終了するまで待ちます')

    def fail(self,message):
        self.queue=[];self.busy=False
        if hasattr(self,'deadline'):self.deadline.stop()
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
        if QApplication.instance():QMessageBox.critical(None,'FRB Launch','起動に失敗しました。LOCALAPPDATA/FRBLaunch/error.logを確認してください。')
        raise
