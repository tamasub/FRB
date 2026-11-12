"""Future dialogs cannot silently lose ぐりぐり; contract tests are mandatory."""
from pathlib import Path
import ast
import importlib.util
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'check_dialog_contract.py'
spec = importlib.util.spec_from_file_location('check_dialog_contract', SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def test_all_existing_launch_dialogs_use_one_shared_entry():
    assert checker.violations(ROOT) == []


def probe(tmp_path, src):
    folder = tmp_path / 'src'
    folder.mkdir()
    (folder / 'feature.py').write_text(src, encoding='utf-8')
    return checker.violations(tmp_path)


def test_new_dialog_using_native_exec_is_rejected(tmp_path):
    assert probe(tmp_path, '''def new_dialog(self):
    dialog = QDialog(self)
    dialog.exec()
''')


def test_new_dialog_missing_shared_runner_is_rejected_even_with_event_filter(tmp_path):
    assert probe(tmp_path, '''def new_dialog(self):
    dialog = QDialog(self)
    dialog.show()
''')


def test_new_static_warning_and_input_dialog_are_rejected(tmp_path):
    assert probe(tmp_path, '''def fail(self):
    QMessageBox.warning(self, 'title', 'message')
    QInputDialog.getText(self, 'title', 'label')
''')


def test_new_dialog_via_common_runner_is_approved(tmp_path):
    assert probe(tmp_path, '''def new_dialog(self):
    dialog = QDialog(self)
    return self.run_launch_button_dialog(dialog)
''') == []


def test_os_native_file_picker_is_outside_launch_button_contract(tmp_path):
    assert probe(tmp_path, '''def choose_path(self):
    return QFileDialog.getExistingDirectory(self, 'select')
''') == []


def load_methods():
    source = (ROOT / 'src' / 'remote_text_dialog.py').read_text(encoding='utf-8')
    source_tree = ast.parse(source)
    cls = next(n for n in source_tree.body if isinstance(n, ast.ClassDef) and n.name == 'RemoteTextDialog')
    code = compile(ast.Module(body=[cls], type_ignores=[]), '<remote-text-actual>', 'exec')
    selection_source = (ROOT / 'src' / 'dialog_button_selection.py').read_text(encoding='utf-8')
    env = {}
    exec(compile(selection_source,'<selection-actual>','exec'),env)
    env['DialogButtonSelection'] = env['DialogButtonSelection']
    env['QDialogButtonBox'] = NS(StandardButton=NS(Ok=1, Cancel=2),
                                 ButtonRole=NS(AcceptRole=10, YesRole=11,
                                               RejectRole=20, NoRole=21))
    env['Qt'] = NS(FocusReason=NS(TabFocusReason=1))
    exec(code,env)
    return env['RemoteTextDialog'], env['QDialogButtonBox']


class FakeButton:
    def __init__(self, text):
        self.text = text
        self.click = Mock()
        self.setStyleSheet = Mock()
        self.setFocus = Mock()
        self.update = Mock()


class FakeBox:
    def __init__(self, specs):
        self.specs = [(FakeButton(name), std, role) for name, std, role in specs]

    def buttons(self):
        return [button for button, _, _ in self.specs]

    def standardButton(self, button):
        return next(std for b,std,role in self.specs if b is button)

    def buttonRole(self, button):
        return next(role for b,std,role in self.specs if b is button)


def make_text_dialog(specs):
    Dialog, QBox = load_methods()
    box = FakeBox(specs)
    launcher = NS(remote_window=None)
    dialog = NS(setDefaultButton=Mock())
    instance = Dialog(launcher, dialog, None, box)
    return instance, box


def test_guriguri_generic_text_dialog_cancel_wins_and_real_button_click_wins():
    inst, box = make_text_dialog([('OK', 1, 10), ('Cancel', 2, 20)])
    ok, cancel = box.buttons()
    assert inst.selected == 'Cancel'
    inst.remote_command('UP')
    assert inst.selected == 'OK'
    inst.remote_command('UP')
    assert inst.selected == 'Cancel'
    inst.remote_command('CLICK')
    cancel.click.assert_called_once_with()
    ok.click.assert_not_called()
    # Real Cancel/OK clicks are never intercepted or rewritten by selector.
    ok.click()
    ok.click.assert_called_once_with()


def test_future_dialog_with_custom_buttons_is_selected_without_special_wiring():
    inst, box = make_text_dialog([('保存', 0, 10), ('破棄', 0, 20), ('ヘルプ', 0, 30)])
    buttons = box.buttons()
    assert len(inst.buttons) == 3
    inst.remote_command('DOWN')
    assert inst.selected in inst.buttons
    inst.remote_command('CLICK')
    assert sum(button.click.call_count for button in buttons) == 1


def test_remote_hidden_does_not_disable_shared_dialog_selection():
    inst, box = make_text_dialog([('OK', 1, 10), ('Cancel', 2, 20)])
    assert inst.launcher.remote_window is None
    inst.remote_command('RIGHT')
    inst.remote_command('CLICK')
    box.buttons()[0].click.assert_called_once()


def test_generic_input_guard_is_used_by_every_remote_text_dialog():
    source = (ROOT/'src/remote_text_dialog.py').read_text(encoding='utf-8')
    assert 'ConfirmationInputGuard(self.dialog, remote, self)' in source
    assert 'application.installEventFilter(guard)' in source
    assert 'application.removeEventFilter(guard)' in source
    assert 'remote is not None and remote.isVisible()' not in (ROOT/'src/app.py').read_text(encoding='utf-8').split('def git_commit_using_filename')[1].split('\n    def ')[0]
