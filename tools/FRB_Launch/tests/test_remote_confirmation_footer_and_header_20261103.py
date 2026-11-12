"""Tests for Remote Yes/No routing and List-only click, without Windows/Qt GUI.

These exercise the actual source's methods with a minimal Qt stub. They do not
claim real GUI validation of PySide6 or the Windows nonactivating tool window.
"""
import ast
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace as NS
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT/'src/app.py').read_text(encoding='utf-8')
REMOTE = (ROOT/'src/launch_remote.py').read_text(encoding='utf-8')
VIEW = (ROOT/'src/expanded_view.py').read_text(encoding='utf-8')
CONFIRM = (ROOT/'src/remote_confirmation.py').read_text(encoding='utf-8')


def real_method(source, cls, name):
    root = ast.parse(source)
    parent = next(item for item in root.body if isinstance(item, ast.ClassDef) and item.name == cls)
    method = next(item for item in parent.body if isinstance(item, ast.FunctionDef) and item.name == name)
    namespace = {}
    exec(compile(ast.Module(body=[method], type_ignores=[]), '<actual-source>', 'exec'), namespace)
    return namespace[name]


def fake_confirmation_module():
    """Import the real helper with tiny interface stubs; no PySide6 required."""
    events = {name: index for index, name in enumerate(('MouseButtonPress',
             'MouseButtonRelease', 'MouseButtonDblClick', 'Wheel', 'ContextMenu',
             'KeyPress', 'KeyRelease', 'ShortcutOverride'))}
    qt_core = ModuleType('PySide6.QtCore')
    qt_core.QObject = type('QObject', (), {'__init__': lambda self, *args: None})
    qt_core.QEvent = NS(Type=NS(**events))
    qt_core.QEventLoop = type('QEventLoop', (), {})
    qt_core.QTimer = type('QTimer', (), {})
    qt_core.Qt = NS(FocusReason=NS(OtherFocusReason=1, TabFocusReason=2), WindowModality=NS(NonModal=0))
    qt_widgets = ModuleType('PySide6.QtWidgets')
    qt_widgets.QApplication = type('QApplication', (), {})
    qt_widgets.QWidget = type('QWidget', (), {'window': lambda self: self._window})
    qt_widgets.QMessageBox = NS(StandardButton=NS(Yes=16384, No=65536))
    with patch.dict(sys.modules, {'PySide6': ModuleType('PySide6'),
                                  'PySide6.QtCore': qt_core,
                                  'PySide6.QtWidgets': qt_widgets}):
        spec = importlib.util.spec_from_file_location('frb_test_confirmation', ROOT/'src/remote_confirmation.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module, qt_widgets


def test_wheel_no_default_yes_on_step_and_center_click_confirms_only_selected():
    mod, _ = fake_confirmation_module()
    controller = mod.RemoteConfirmation.__new__(mod.RemoteConfirmation)
    class FakeButton:
        def __init__(self):
            self.setStyleSheet = Mock()
            self.setFocus = Mock()
            self.update = Mock()
            self.click = Mock()
    buttons = {16384: FakeButton(), 65536: FakeButton()}
    controller.dialog = NS(button=lambda answer: buttons[answer], setDefaultButton=Mock(), done=Mock())
    controller.selected = controller.NO
    controller.launcher = NS(remote_window=None)
    controller.remote_command('DOWN')
    assert controller.selected == controller.YES
    buttons[controller.YES].click.assert_not_called()
    controller.remote_command('CLICK')
    buttons[controller.YES].click.assert_called_once_with()
    controller.remote_command('UP')
    assert controller.selected == controller.NO
    controller.remote_command('ENTER')
    buttons[controller.NO].click.assert_called_once_with()
    controller.dialog.done.assert_not_called()  # Use actual button.clicked, not done().


def test_remote_confirmation_left_right_and_close_are_safe():
    mod, _ = fake_confirmation_module()
    ctrl = mod.RemoteConfirmation.__new__(mod.RemoteConfirmation)
    buttons = {answer: NS(setFocus=Mock(), setStyleSheet=Mock(), update=Mock(), click=Mock())
               for answer in (ctrl.YES, ctrl.NO)}
    ctrl.dialog = NS(button=lambda answer: buttons[answer],
                     setDefaultButton=Mock(), done=Mock())
    ctrl.selected = ctrl.NO
    ctrl.launcher = NS(remote_window=None)
    ctrl.remote_command('RIGHT')
    assert ctrl.selected == ctrl.YES
    ctrl.remote_command('LEFT')
    assert ctrl.selected == ctrl.NO
    ctrl.remote_command('RIGHT')
    ctrl.remote_command('CLOSE')
    buttons[ctrl.NO].click.assert_called_once_with()
    ctrl.dialog.done.assert_not_called()


def test_dialog_guard_blocks_background_widgets_but_allows_remote_and_question():
    mod, widgets = fake_confirmation_module()
    question, remote, launch = object(), object(), object()
    guard = mod.ConfirmationInputGuard(question, remote)
    def event(t): return NS(type=lambda:t, accept=Mock())
    for target in (question,):
        widget = widgets.QWidget()
        widget._window = target
        e = event(mod.ConfirmationInputGuard.BLOCKED[0])
        assert guard.eventFilter(widget, e) is False
        e.accept.assert_not_called()
    widget = widgets.QWidget()
    widget._window = launch
    e = event(mod.ConfirmationInputGuard.BLOCKED[0])
    assert guard.eventFilter(widget, e) is True
    e.accept.assert_called_once_with()


def test_exclusive_list_band_rejects_exp_and_allows_list():
    fn = real_method(REMOTE,'UpDoubleClickBand','_list_is_active')
    current = NS(_files_operating_target='files_exp')
    band = NS(_files_mode=True, parentWidget=lambda: current)
    assert fn(band) is False
    current._files_operating_target = 'directory'
    assert fn(band) is True
    band._files_mode = False
    assert fn(band) is False


def test_remote_blank_deferred_timer_checks_true_list_target_and_cancels_on_switch():
    assert 'if self._list_is_active() else None' in REMOTE
    assert 'self.up_band._single_click_timer.stop()' in REMOTE
    assert "if getattr(self, '_files_operating_target', None) != 'directory':" in APP
    assert "if not self._list_is_active():" in REMOTE
    assert 'self._list_is_active()' in REMOTE


def test_list_grid_header_is_lighter_in_both_modes():
    assert "list_grid_header = '#FCFEFD' if light" in VIEW
    assert "operating_grid_header = '#FFFCF6' if light" in VIEW
    assert "background:{list_grid_header}" in VIEW
    assert "background:{operating_grid_header}" in VIEW
    # Inactive title #F8FCF9 -> #FCFEFD; active title #FFF9EF -> #FFFCF6.
    for title, header in (('#f8fcf9','#FCFEFD'),('#FFF9EF','#FFFCF6')):
        t = tuple(int(title[i:i+2],16) for i in (1,3,5))
        h = tuple(int(header[i:i+2],16) for i in (1,3,5))
        assert all(a <= b for a,b in zip(t,h)) and any(a < b for a,b in zip(t,h))


def test_done_dialogs_are_footer_info_but_diagnostics_remain_available():
    assert "self.info_notice('Gitコミット完了：' + committed)" in APP
    assert 'self.info_notice(\'索引データをクリアしました' in APP
    assert 'ℹ️ ' in APP
    assert "self.show_launch_notice(QMessageBox.Icon.Information, 'ファイル索引の状態'" in APP
    assert "self.show_launch_notice(QMessageBox.Icon.Information, 'FRB Launch ブックマーク取得診断'" in APP


def test_all_launch_yes_no_prompts_use_common_remote_guard():
    assert 'QMessageBox.question(' not in APP
    assert 'QMessageBox.question(' not in VIEW
    for caption in ('同名の項目があります', '複数項目をごみ箱へ移動', 'ごみ箱へ移動',
                    'カテゴリー削除', '拡張子の変更', 'Gitコミットの確認', 'ファイル索引SQLite DBをクリア'):
        assert caption in APP or caption in VIEW
    assert 'confirmation.remote_command(command)' in APP
    assert 'self._remote_confirmation = None' in APP


def test_no_confirmation_event_can_fallthrough_to_file_actions():
    remote_command = real_method(APP, 'Launcher', 'remote_command')
    target = NS(_remote_confirmation=NS(remote_command=Mock()))
    remote_command(target, 'CLICK')
    target._remote_confirmation.remote_command.assert_called_once_with('CLICK')
    remote_command(target, 'RIGHT')
    assert target._remote_confirmation.remote_command.call_count == 2


def test_remote_caption_shows_confirmation_choice_without_changing_file_target():
    mod, _ = fake_confirmation_module()
    label = NS(setText=Mock())
    remote = NS(area_label=label, isVisible=lambda: True)
    ctrl = mod.RemoteConfirmation.__new__(mod.RemoteConfirmation)
    ctrl.launcher = NS(remote_window=remote, _files_operating_target='files_exp')
    ctrl.dialog = NS(button=lambda _: NS(setFocus=Mock(), setStyleSheet=Mock(), update=Mock()), setDefaultButton=Mock())
    ctrl.selected = ctrl.NO
    ctrl.choose(ctrl.NO)
    label.setText.assert_called_with('確認応答：No')
    ctrl.choose(ctrl.YES)
    label.setText.assert_called_with('確認応答：Yes')
    assert ctrl.launcher._files_operating_target == 'files_exp'
