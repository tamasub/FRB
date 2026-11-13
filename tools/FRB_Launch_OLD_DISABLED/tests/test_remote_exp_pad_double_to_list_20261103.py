"""Files Exp pad double-click is an alias for Remote RIGHT, without a first-click side effect.

Runs the real Launcher methods extracted from source, without needing PySide6.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf-8')


def actual(name, extras=None):
    tree = ast.parse(SOURCE)
    cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'Launcher')
    method = next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == name)
    scope = dict(extras or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 '<real Launcher method>', 'exec'), scope)
    return scope[name]


class Timer:
    def __init__(self, _owner):
        self.callback = None
        self.timeout = NS(connect=lambda fn: setattr(self, 'callback', fn))
        self.active = False
        self.delay = None
        self.setSingleShot = Mock()
    def start(self, ms):
        self.active = True
        self.delay = ms
    def stop(self):
        self.active = False
    def fire(self):
        if self.active:
            self.active = False
            self.callback()


class QtApp:
    def doubleClickInterval(self):
        return 400


def launch(*, area='files_exp', expanded=True, workspace='files'):
    panel = NS(remote_activate_current=Mock())
    view = NS(isVisible=lambda: expanded, _workspace_mode=workspace,
              web_view_active=lambda: False, commit_remote_inline_rename=lambda: False)
    app = NS(expanded_view=view, _remote_page_menu=None, _remote_area=area,
             _last_focus_area=area, _remote_popup_area=None,
             remote_cascade_command=lambda _command: False,
             _current_remote_files_exp=lambda: panel,
             remote_focus_area=Mock(), remote_exp_right_to_list=Mock(return_value=True))
    return app, panel


CLICK = actual('remote_mouse_click', {'QTimer': Timer,
                                     'QApplication': NS(instance=lambda: QtApp())})
COMMIT = actual('_remote_exp_single_click')


def test_double_click_uses_same_right_handoff_without_activating_first_click():
    app, panel = launch()
    app._remote_exp_single_click = lambda: COMMIT(app)
    CLICK(app, double=False)
    assert app._remote_exp_click_timer.active
    assert app._remote_exp_click_timer.delay == 400
    panel.remote_activate_current.assert_not_called()
    CLICK(app, double=True)
    assert not app._remote_exp_click_timer.active
    app._remote_exp_click_timer.fire()  # Double click cancels activation.
    panel.remote_activate_current.assert_not_called()
    app.remote_exp_right_to_list.assert_called_once_with()
    app.remote_focus_area.assert_not_called()  # Handoff owns the focus.


def test_single_click_keeps_original_exp_activation_after_native_interval():
    app, panel = launch()
    app._remote_exp_single_click = lambda: COMMIT(app)
    CLICK(app, double=False)
    app._remote_exp_click_timer.fire()
    panel.remote_activate_current.assert_called_once_with()
    app.remote_focus_area.assert_called_once_with('files_exp')
    app.remote_exp_right_to_list.assert_not_called()


def test_double_click_in_list_does_not_handoff_to_list():
    app, panel = launch(area='directory')
    view = app.expanded_view
    item = object()
    tree = NS(currentItem=lambda: item)
    view.middle = NS(tree=tree)
    view.left = NS(tree=tree)
    view.right = NS(tree=tree)
    view.row_data = lambda _item: {'item_kind': 'file', 'item_id': 'x'}
    view.activate_row = Mock()
    app._remote_mouse_last_click = ('directory','x')
    app.activate = Mock()
    CLICK(app, double=True)
    app.remote_exp_right_to_list.assert_not_called()
    view.activate_row.assert_called_once_with(view.middle, item)


def test_single_click_does_not_activate_after_target_changes():
    app, panel = launch()
    app._remote_exp_single_click = lambda: COMMIT(app)
    CLICK(app, double=False)
    app._remote_area = 'directory'
    app._remote_exp_click_timer.fire()
    panel.remote_activate_current.assert_not_called()
    app.remote_exp_right_to_list.assert_not_called()


def test_double_click_not_repurposed_outside_exp_target():
    app, panel = launch(workspace='browser')
    app._remote_exp_single_click = lambda: COMMIT(app)
    # Stale Exp target while Browser is visible must not invoke handoff.
    empty = NS(tree=NS(currentItem=lambda: None))
    app.expanded_view.left = empty
    app.expanded_view.middle = empty
    app.expanded_view.right = empty
    app.expanded_view.row_data = lambda _item: None
    CLICK(app, double=True)
    app.remote_exp_right_to_list.assert_not_called()


def test_remote_close_cancels_any_pending_exp_single_click():
    command = actual('remote_command')
    timer = Timer(None)
    timer.start(400)
    app = NS(_remote_exp_click_timer=timer, hide_remote=Mock())
    command(app, 'CLOSE')
    assert not timer.active
    app.hide_remote.assert_called_once_with()
