"""Release regression: menu grab, keyboard Exp↔List hand-off, Send placement.

Qt-free behavioral checks; actual Win11 mouse/Qt focus testing remains manual.
"""
import ast
import sys
from unittest.mock import patch
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text('utf-8')
EXP = (ROOT / 'src/remote_files_explorer.py').read_text('utf-8')
WHEEL = (ROOT / 'src/remote_context_wheel.py').read_text('utf-8')


def method(source, klass, name, helpers):
    tree = ast.parse(source)
    owner = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                 and node.name == klass)
    fn = next(node for node in owner.body if isinstance(node, ast.FunctionDef)
              and node.name == name)
    env = dict(helpers)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 'isolated', 'exec'), env)
    return env[name]


def test_send_button_is_immediately_after_back_before_stretch():
    start = APP.index("for title, callback in [('全選択 (Ctrl+A)'")
    ending = APP.index('self.selection_tools.hide()', start)
    group = APP[start:ending]
    assert group.index('buttons.addWidget(button)') < group.index("QPushButton('送信 (F12)'")
    assert group.index('buttons.addWidget(self.selection_send_button)') < group.index('buttons.addStretch()')
    assert 'self.selection_send_button.clicked.connect(self.confirm_selection)' in group


def test_all_hybrid_menus_use_non_grabbing_tool_flags():
    class Menu:
        def __init__(self):
            self.flag = None
            self.callbacks = []
            self.aboutToShow = NS(connect=lambda cb: self.callbacks.append(cb))
        def setWindowFlags(self, flags): self.flag = flags
        def findChildren(self, typ): return [nested]
    qt = NS(WindowType=NS(Tool=1, FramelessWindowHint=2, WindowStaysOnTopHint=4))
    root, nested = Menu(), Menu()
    obj = NS(_enable_remote_context_wheel_for_menu=Mock())
    fn = method(APP, 'Launcher', '_wire_hybrid_context_menu',
                {'Qt': qt, 'QMenu': Menu, 'QTimer': NS(singleShot=lambda ms, cb: cb())})
    fn(obj, root)
    assert root.flag == nested.flag == 7
    assert root._frb_non_grabbing is True
    assert len(root.callbacks) == 1
    root.callbacks[0]()
    obj._enable_remote_context_wheel_for_menu.assert_called_once_with(root)
    fn(obj, root)
    assert len(root.callbacks) == 1


def test_list_left_first_then_exp_focus():
    # Exercise the real app method via the project's existing lightweight Qt doubles.
    from test_expanded_keyboard_dispatch_20261024 import instance, event, Qt
    d = instance()
    d.files_exp_embedded_mode = True
    d.remote_window = None
    d.remote_list_left_to_exp = Mock(side_effect=[False, True])
    exp_tree = NS(setFocus=Mock())
    d._current_remote_files_exp = lambda: NS(tree=exp_tree)
    for _ in range(2):
        e = event('Left')
        assert d.expanded_tree_key(d.expanded_view.middle.tree, e)
        assert e.accepted
    d.remote_list_left_to_exp.assert_called_with()
    assert ('left_hierarchy',) in d.expanded_view.actions
    exp_tree.setFocus.assert_called_once_with(Qt.FocusReason.TabFocusReason)


def test_exp_right_commits_and_focuses_list():
    qt = NS(Key=NS(Key_Right=19, Key_Return=20, Key_Enter=21), KeyboardModifier=NS(NoModifier=0))
    view = NS(middle=object(), focus_panel=Mock())
    launcher = NS(remote_exp_right_to_list=Mock(return_value=True), expanded_view=view)
    panel = NS(_embedded=True, _launcher=launcher, _rename_in_progress=None)
    fn = method(EXP, 'FilesExpWheelTree', 'keyPressEvent',
                {'Qt': qt, 'QAbstractItemView': NS(State=NS(EditingState=5))})
    tree = NS(parentWidget=lambda: panel, state=lambda: 0)
    pressed = NS(key=lambda: 19, modifiers=lambda: 0, accept=Mock())
    fn(tree, pressed)
    launcher.remote_exp_right_to_list.assert_called_once_with()
    view.focus_panel.assert_called_once_with(view.middle)
    pressed.accept.assert_called_once_with()


def test_non_grabbing_menu_closes_on_outside_click():
    kinds = NS(ApplicationDeactivate=1, MouseButtonPress=2, Wheel=3,
               MouseButtonRelease=4, MouseButtonDblClick=5)
    cursor = NS(pos=lambda: 'outside')
    root = NS(isVisible=lambda: True, findChildren=lambda cls: [],
              frameGeometry=lambda: NS(contains=lambda pos: False), close=Mock())
    root._frb_non_grabbing = True
    wheel = NS(active=True, root=root, _hit=lambda pos: None)
    fn = method(WHEEL, 'RemoteContextWheel', 'eventFilter',
                {'QEvent': NS(Type=kinds), 'QCursor': cursor,
                 'QMenu': object, 'Qt': NS(MouseButton=NS(LeftButton=1))})
    e = NS(type=lambda: kinds.MouseButtonPress,
           globalPosition=lambda: NS(toPoint=lambda: 'outside'))
    with patch.dict(sys.modules, {'PySide6': NS(),
                                  'PySide6.QtWidgets': NS(QMenu=object)}):
        assert fn(wheel, object(), e) is False
    root.close.assert_called_once_with()
