"""2026-11-03: keep folders intact, square Exp header, five-button wheel.

Qt-free behavior tests. Windows/PySide6 must still be checked on a real desktop.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
BOOKMARK = (ROOT/'src/browser_bookmark_bar.py').read_text(encoding='utf-8')
EXPANDED = (ROOT/'src/expanded_view.py').read_text(encoding='utf-8')
EXP_TREE = (ROOT/'src/remote_files_explorer.py').read_text(encoding='utf-8')


def load_method(source, class_name, method, scope):
    tree = ast.parse(source)
    cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == class_name)
    node = next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == method)
    fn = ast.Module(body=[node], type_ignores=[])
    exec(compile(ast.fix_missing_locations(fn), 'test-snippet', 'exec'), scope)
    return scope[method]


def test_folder_strip_does_not_flatten_urls_even_with_nested_children():
    created = []
    class Font:
        def pointSizeF(self): return 11
        def setPointSizeF(self, x): pass
    class Signal:
        def connect(self, f): self.fn = f
    class Btn:
        def __init__(self, parent):
            self.clicked = Signal()
            created.append(self)
        def setObjectName(self, x): pass
        def setText(self, x): self.text = x
        def setToolTip(self, x): pass
        def setToolButtonStyle(self, x): pass
        def setCursor(self, x): pass
        def setFocusPolicy(self, x): pass
        def setFixedHeight(self, x): pass
        def font(self): return Font()
        def setFont(self, x): pass
        def setStyleSheet(self, x): pass
        def installEventFilter(self, x): pass
    class Scroll:
        def value(self): return 0
        def setValue(self, x): pass
    class Row:
        def __init__(self): self.widgets=[]
        def count(self): return len(self.widgets)
        def takeAt(self, idx):
            w = self.widgets.pop(idx)
            return NS(widget=lambda: w)
        def addWidget(self, b): self.widgets.append(b)
    fake_qt = NS(ToolButtonStyle=NS(ToolButtonTextOnly=1),
                 CursorShape=NS(PointingHandCursor=1),FocusPolicy=NS(NoFocus=1))
    scope = {'QToolButton':Btn, 'Qt': fake_qt}
    method = load_method(BOOKMARK, 'HorizontalBookmarkBar', 'update_bookmark_bar', scope)
    folder = {'item_id':'folder', 'title':'仕事','item_kind':'category'}
    leaf = {'item_id':'link','title':'Zenn','item_kind':'command'}
    inside = {'item_id':'nested','title':'フォルダー内のURL','item_kind':'command'}
    row = Row()
    chosen=[]
    host=NS(_bookmark_bar_signature=None,_folder_menu=None,_buttons=[],
            _wheel_settle_timer=NS(stop=lambda:None),
            _wheel_current=None,bookmark_strip_row=row,
            bookmark_strip_inner=NS(adjustSize=lambda:None),
            horizontalScrollBar=lambda: Scroll(),
            _is_folder=lambda x:x.get('item_kind') in ('category','directory'),
            _open_folder=lambda x,b:chosen.append(('folder',x['title'])),
            _open_bookmark_bar_row=lambda x:chosen.append(('url',x['title'])))
    method(host,[folder,leaf],lambda r:[inside] if r is folder else [],lambda r:None)
    assert len(created)==2
    assert created[0].text=='📁 仕事'
    assert created[1].text=='Zenn'
    assert 'フォルダー内のURL' not in [b.text for b in created]
    created[0].clicked.fn()
    created[1].clicked.fn()
    assert chosen==[('folder','仕事'),('url','Zenn')]


def test_nested_folder_menu_preserves_tree_and_only_runs_clicked_leaf():
    scope={}
    fill=load_method(BOOKMARK,'HorizontalBookmarkBar','_fill_folder_menu',scope)
    called=[]
    class Action:
        def __init__(self,text): self.text=text; self.triggered=NS(connect=lambda cb:setattr(self,'cb',cb))
        def setToolTip(self,value): pass
    class Menu:
        def __init__(self): self.items=[]
        def addAction(self,text):
            a=Action(text);self.items.append(a);return a
        def addMenu(self,text):
            m=Menu();m.text=text;self.items.append(m);return m
    parent={'item_id':'a','title':'研究','item_kind':'category'}
    folder={'item_id':'b','title':'ノート','item_kind':'category'}
    leaf={'item_id':'c','title':'Qiita','item_kind':'command'}
    data={'a':[folder],'b':[leaf],'c':[]}
    host=NS(_folder_rows=lambda row: data.get(row['item_id'],[]),
            _is_folder=lambda row:row['item_kind']=='category',
            _open_bookmark_bar_row=lambda row:called.append(row['item_id']))
    host._fill_folder_menu = lambda menu, row, visited, depth=0: fill(host, menu, row, visited, depth)
    menu=Menu()
    fill(host,menu,parent,set())
    assert len(menu.items)==1 and menu.items[0].text=='📁 ノート'
    assert menu.items[0].items[0].text=='Qiita'
    assert called==[]
    menu.items[0].items[0].cb()
    assert called==['c']


def test_exp_header_is_square_and_soft_green():
    assert "exp_header = '#f8fcf9'" in EXP_TREE
    assert "else '#395247'" in EXP_TREE
    assert "QFrame#filesExpHeader {{background:{exp_header};" in EXP_TREE
    assert 'border-radius:0px;' in EXP_TREE


def test_wheel_moves_across_all_five_without_executing_buttons():
    scope={'Qt':NS(KeyboardModifier=NS(NoModifier=0),
                   FocusReason=NS(OtherFocusReason=1)),
           'QTimer':NS(singleShot=lambda delay,cb:None)}
    wheel=load_method(EXPANDED,'ExpandedLauncherView','wheel_workspace_page_buttons',scope)
    class Button:
        def __init__(self,title): self.title=title;self.focused=False
        def isVisible(self): return True
        def setFocus(self,reason): self.focused=True
    buttons=[Button(x) for x in ('Files','Browser','My Work','Windows','FRB実験')]
    view=NS(files_mode_tab=buttons[0],browser_mode_tab=buttons[1],
            workspace_page_buttons=buttons[2:],_toolbar_wheel_current=None,
            _toolbar_wheel_remainder=0,launcher=NS(pointer_warp_enabled=False))
    view._toolbar_wheel_buttons=lambda: buttons
    def event(angle):
        return NS(modifiers=lambda:0,angleDelta=lambda:NS(y=lambda:angle),
                  pixelDelta=lambda:NS(y=lambda:0))
    assert wheel(view,buttons[0],event(-120)) is True
    assert view._toolbar_wheel_current is buttons[1] and buttons[1].focused
    assert wheel(view,buttons[1],event(-120)) is True
    assert view._toolbar_wheel_current is buttons[2]
    assert wheel(view,buttons[2],event(-240)) is True
    assert view._toolbar_wheel_current is buttons[4]
    assert wheel(view,buttons[4],event(-120)) is True
    assert view._toolbar_wheel_current is buttons[4]  # no wrap
    assert wheel(view,buttons[4],event(480)) is True
    assert view._toolbar_wheel_current is buttons[0]
    # Only focus changed here; click-to-run remains owned by clicked.connect.
    assert 'selected.click()' not in EXPANDED


def test_wheel_filter_installed_for_two_workspaces_and_three_pages():
    assert "button.installEventFilter(self)\n                self.root_layout.addWidget" in EXPANDED
    assert "button.installEventFilter(self)\n                button.clicked.connect" in EXPANDED
    assert 'self.wheel_workspace_page_buttons(obj, event)' in EXPANDED
    assert 'self._toolbar_wheel_current = None' in EXPANDED
