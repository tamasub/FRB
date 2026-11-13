"""Cloud Copy Link: do not invent URLs or misreport native invocation as copy."""
import json
from pathlib import Path
import subprocess
import sys
import types

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'src'))
import cloud_link_shell
from context_menu_config import load_context_menus


def test_copy_link_verb_script_quotes_spaces_japanese_and_apostrophe():
    script = cloud_link_shell.copy_link_powershell_script(Path("/folder with spaces/鈴木's plan.xlsx"))
    assert "鈴木''s plan.xlsx" in script
    assert "リンクのコピー" in script
    assert "Copy shared link" in script
    assert "Copy link" in script
    assert 'INVOCATION_REQUESTED' in script
    assert 'NO_COMMAND' in script
    assert 'Get-Item' not in script
    assert 'Set-Acl' not in script


def test_invocation_request_must_be_returned_exactly_and_no_claim_of_clipboard(monkeypatch, tmp_path):
    target = tmp_path / 'テスト.xlsx'
    target.write_text('sample', encoding='utf-8')
    monkeypatch.setattr(cloud_link_shell, 'os', types.SimpleNamespace(name='nt'))
    commands = []

    def runner(args, **kwargs):
        commands.append((args, kwargs))
        return subprocess.CompletedProcess(args, 0, 'INVOCATION_REQUESTED\n', '')

    assert cloud_link_shell.request_native_copy_link(target, runner=runner)
    assert commands[0][0][0] == 'powershell.exe'
    assert commands[0][0][1:3] == ['-NoProfile', '-Sta']
    assert '-EncodedCommand' in commands[0][0]
    assert commands[0][1]['timeout'] <= 10
    assert commands[0][1]['check'] is False

    def no_command(args, **kwargs):
        return subprocess.CompletedProcess(args, 0, 'NO_COMMAND\n', '')

    assert not cloud_link_shell.request_native_copy_link(target, runner=no_command)

    def wrong_output(args, **kwargs):
        return subprocess.CompletedProcess(args, 0, 'ANOTHER_INVOCATION_REQUESTED\n', '')

    assert not cloud_link_shell.request_native_copy_link(target, runner=wrong_output)


def test_fallback_opens_selected_file_without_using_shell_string(monkeypatch, tmp_path):
    target = tmp_path / "猫's Excel file.xlsx"
    target.write_text('sample', encoding='utf-8')
    monkeypatch.setattr(cloud_link_shell, 'os', types.SimpleNamespace(name='nt'))
    args = []
    cloud_link_shell.select_in_explorer(target, opener=lambda command: args.append(command))
    assert args == [['explorer.exe', '/select,', str(target)]]


def test_json_def_and_context_whitelist_support_file_and_folder_copy_link():
    data = json.loads((HERE / 'config/context_menu_options.json').read_text(encoding='utf-8'))
    menus = load_context_menus(HERE / 'config/context_menu_options.json')
    for kind in ('file','folder'):
        assert any(d.get('action_id')=='copy_cloud_link' for d in data['menus'][kind])
        assert any(d.get('action_id')=='copy_cloud_link' for d in menus[kind])


def test_app_ui_calls_provider_then_fallback_and_preserves_path_copy():
    text = (HERE / 'src/app.py').read_text(encoding='utf-8')
    assert "elif action_id == 'copy_cloud_link':" in text
    assert 'request_native_copy_link(path)' in text
    assert 'select_in_explorer(path)' in text
    assert "elif action_id in ('copy_full_path', 'copy_path')" in text
    assert 'self.dismiss()' in text
    assert 'コピーしました' not in text[text.index("elif action_id == 'copy_cloud_link':"):text.index("elif action_id == 'open_with'")]
