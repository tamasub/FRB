"""Cloud provider dialog handoff: don't dismiss or cover Share/Copy link."""

import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
WINDOWS = (ROOT / 'src/windows.py').read_text(encoding='utf-8')


def method(name, scope):
    root = ast.parse(APP)
    cls = next(n for n in root.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    code = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    ns = dict(scope)
    exec(compile(code, '<app.py>', 'exec'), ns)
    return ns[name]


def test_native_topmost_helper_does_not_resize_activate_or_move():
    root = ast.parse(WINDOWS)
    fn = next(n for n in root.body if isinstance(n, ast.FunctionDef) and n.name == 'set_window_topmost')
    code = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    calls = []
    user = SimpleNamespace(
        IsWindow=lambda hwnd: hwnd == 123,
        SetWindowPos=lambda *args: calls.append(args) or True,
    )
    ns = {'IS_WINDOWS': True, 'user': user}
    exec(compile(code, '<windows.py>', 'exec'), ns)
    f = ns['set_window_topmost']
    assert f(123, False)
    assert f(123, True)
    assert calls == [(123, -2, 0, 0, 0, 0, 0x13),
                     (123, -1, 0, 0, 0, 0, 0x13)]
    assert not f(0, False)
    assert not f(456, True)


def test_handoff_temporarily_drops_z_order_and_restores_when_user_returns():
    transitions = []
    win = SimpleNamespace(set_window_topmost=lambda hwnd, flag: transitions.append((hwnd, flag)))
    begin = method('begin_cloud_link_handoff', {'windows': win})
    finish = method('finish_cloud_link_handoff', {'windows': win})
    launcher = SimpleNamespace(winId=lambda: 123, isVisible=lambda: True,
                               _cloud_link_handoff=False)
    launcher.finish_cloud_link_handoff = lambda: finish(launcher)
    begin(launcher)
    assert launcher._cloud_link_handoff is True
    assert transitions == [(123, False)]
    finish(launcher)
    assert launcher._cloud_link_handoff is False
    assert transitions == [(123, False), (123, True)]
    finish(launcher)
    assert len(transitions) == 2


def test_app_state_keeps_launcher_visible_while_provider_owns_foreground():
    active = SimpleNamespace(ApplicationActive=1, ApplicationInactive=2)
    qt = SimpleNamespace(ApplicationState=active)
    finish = Mock()
    launcher = SimpleNamespace(_cloud_link_handoff=True,
                               isActiveWindow=lambda: False,
                               finish_cloud_link_handoff=finish)
    app_state = method('app_state', {'Qt': qt})
    app_state(launcher, active.ApplicationInactive)
    app_state(launcher, active.ApplicationActive)
    finish.assert_not_called()
    launcher.isActiveWindow = lambda: True
    app_state(launcher, active.ApplicationActive)
    finish.assert_called_once_with()


def test_copy_link_invocation_does_not_close_launcher(tmp_path):
    path = tmp_path / '資料.xlsx'
    path.write_text('content', encoding='utf8')
    calls = []
    launcher = SimpleNamespace(
        begin_cloud_link_handoff=lambda: calls.append('lower-launch'),
        finish_cloud_link_handoff=lambda: calls.append('restore-launch'),
        dismiss=lambda: calls.append('dismiss'),
        footer=SimpleNamespace(setText=lambda text: calls.append(('footer', text))),
        _clear_previous_paste_feedback=lambda: calls.append('clear-feedback'),
        error=Mock(),
    )
    fn = method('perform_filesystem_context_action', {
        'Path': Path,
        'request_native_copy_link': lambda p: calls.append(('native', p)) or True,
        'select_in_explorer': lambda p: calls.append(('explorer', p)),
        'DIAG': Mock(),
    })
    fn(launcher, 'copy_cloud_link', str(path), 'file')
    assert calls[0:2] == ['clear-feedback', 'lower-launch']
    assert ('native', path) in calls
    assert 'dismiss' not in calls and 'restore-launch' not in calls
    launcher.error.assert_not_called()


def test_copy_link_fallback_does_not_close_launcher(tmp_path):
    path = tmp_path / 'sample.txt'
    path.write_text('content', encoding='utf8')
    calls = []
    launcher = SimpleNamespace(
        begin_cloud_link_handoff=lambda: calls.append('lower-launch'),
        finish_cloud_link_handoff=lambda: calls.append('restore-launch'),
        dismiss=lambda: calls.append('dismiss'),
        footer=SimpleNamespace(setText=lambda text: calls.append(('footer', text))),
        error=Mock(),
    )
    fn = method('perform_filesystem_context_action', {
        'Path': Path,
        'request_native_copy_link': lambda p: False,
        'select_in_explorer': lambda p: calls.append(('explorer', p)),
        'DIAG': Mock(),
    })
    fn(launcher, 'copy_cloud_link', str(path), 'file')
    assert ('explorer', path) in calls
    assert 'dismiss' not in calls
    assert ('footer', 'エクスプローラーから「リンクのコピー」を選択してください') in calls


def test_copy_link_failure_restores_original_topmost(tmp_path):
    path = tmp_path / 'sample.txt'
    path.write_text('content', encoding='utf8')
    calls = []
    launcher = SimpleNamespace(
        begin_cloud_link_handoff=lambda: calls.append('lower'),
        finish_cloud_link_handoff=lambda: calls.append('restore'),
        error=Mock(),
    )
    def fail(_):
        raise OSError('failed')
    fn = method('perform_filesystem_context_action', {
        'Path': Path,
        'request_native_copy_link': fail,
        'DIAG': Mock(),
    })
    fn(launcher, 'copy_cloud_link', str(path), 'file')
    assert calls == ['lower', 'restore']
    launcher.error.assert_called_once()


def test_outside_click_and_deactivation_guarded_during_native_handoff():
    assert "and not getattr(window, '_cloud_link_handoff', False)" in APP
    assert "if getattr(self, '_cloud_link_handoff', False):" in APP
    assert "self.finish_cloud_link_handoff()" in APP
    segment = APP.split("elif action_id == 'copy_cloud_link':", 1)[1].split("elif action_id == 'open_with'",1)[0]
    assert 'self.dismiss()' not in segment
    assert 'self.begin_cloud_link_handoff()' in segment
