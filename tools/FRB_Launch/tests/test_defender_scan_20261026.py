"""Direct Microsoft Defender context action without Windows/Qt integration."""
import ast
import base64
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import defender_scan
from context_menu_config import load_context_menus

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
MENU_JSON = ROOT / 'config/context_menu_options.json'


def method(name, scope):
    tree = ast.parse(APP)
    clazz = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                 and node.name == 'Launcher')
    fn = next(node for node in clazz.body if isinstance(node, ast.FunctionDef)
              and node.name == name)
    code = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    ns = dict(scope)
    exec(compile(code, '<Launcher>', 'exec'), ns)
    return ns[name]


def test_declarative_config_never_exposes_defender_action():
    raw = json.loads(MENU_JSON.read_text(encoding='utf8'))
    menus = load_context_menus(MENU_JSON)
    for kind in ('file', 'folder'):
        assert not any(e.get('action_id') == 'scan_defender' for e in raw['menus'][kind])
        assert not any(e.get('action_id') == 'scan_defender' for e in menus[kind])
        assert menus[kind][-1]['action_id'] == 'properties'


def test_shell_verb_requires_exact_defender_caption_and_only_selected_path():
    filename = Path("C:/工事 & work/鈴木's summary (2).xlsx")
    script = defender_scan.native_defender_script(filename)
    assert "鈴木''s summary (2).xlsx" in script
    assert 'Scan with Microsoft Defender' in script
    assert 'Microsoft Defenderでスキャンする' in script
    assert 'foreach ($verb in $item.Verbs())' in script
    assert '  $verb.DoIt()' in script
    assert 'Invoke-Expression' not in script
    assert 'Copy link' not in script


def test_native_invocation_uses_utf16le_and_confirmed_result(tmp_path, monkeypatch):
    p = tmp_path / "test ' name.txt"
    p.write_text('content', encoding='utf8')
    monkeypatch.setattr(defender_scan, 'os', SimpleNamespace(name='nt'))
    calls = []

    def runner(args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=0, stdout='INVOCATION_REQUESTED\n')

    assert defender_scan.request_native_defender_scan(p, runner=runner)
    args, opts = calls[0]
    assert args[:3] == ['powershell.exe', '-NoProfile', '-Sta']
    assert p.name.replace("'", "''") in base64.b64decode(args[-1]).decode('utf-16-le')
    assert opts['timeout'] == 10
    assert not defender_scan.request_native_defender_scan(
        p, runner=lambda *args, **kw: SimpleNamespace(returncode=0, stdout='NO_COMMAND\n'))


def test_custom_scan_fallback_targets_only_selected_file_or_folder(tmp_path, monkeypatch):
    monkeypatch.setattr(defender_scan, 'os', SimpleNamespace(name='nt'))
    for p in (tmp_path / '安全なフォルダー', tmp_path / "report';Write-Error 'oops.xlsx"):
        if p.suffix:
            p.write_text('ok', encoding='utf8')
        else:
            p.mkdir()
        args_seen = []
        defender_scan.start_defender_custom_scan(
            p, opener=lambda args, **kwargs: args_seen.append((args, kwargs)))
        assert len(args_seen) == 1
        argv, kwargs = args_seen[0]
        assert argv[:2] == ['powershell.exe', '-NoProfile']
        script = base64.b64decode(argv[-1]).decode('utf-16-le')
        assert 'Start-MpScan -ScanType CustomScan -ScanPath ' in script
        assert defender_scan._ps_literal(str(p)) in script
        assert ' -File ' not in script
        assert 'ScanType FullScan' not in script
        assert 'Invoke-Expression' not in script
        assert 'Read-Host' in script  # user can review an error/result
        assert 'creationflags' in kwargs


def test_missing_target_refused_instead_of_scanning_entire_computer(tmp_path, monkeypatch):
    monkeypatch.setattr(defender_scan, 'os', SimpleNamespace(name='nt'))
    with pytest.raises(FileNotFoundError):
        defender_scan.start_defender_custom_scan(tmp_path / 'missing')


def test_launcher_has_no_defender_dependency_or_dispatch_branch():
    assert 'from defender_scan import ' not in APP
    assert "elif action_id == 'scan_defender':" not in APP
    assert 'request_native_defender_scan(' not in APP
    assert 'start_defender_custom_scan(' not in APP


def test_legacy_defender_entry_is_ignored_without_breaking_other_actions(tmp_path):
    original = json.loads(MENU_JSON.read_text(encoding='utf8'))
    original['menus']['file'].insert(0, {
        'action_id': 'scan_defender', 'title': 'Microsoft Defenderでスキャンする'})
    original['menus']['folder'].insert(0, {
        'action_id': 'scan_defender', 'title': 'Microsoft Defenderでスキャンする'})
    path = tmp_path / 'legacy_menu.json'
    path.write_text(json.dumps(original, ensure_ascii=False), encoding='utf8')
    assert load_context_menus(path) == load_context_menus(MENU_JSON)


def test_direct_retired_action_is_never_dispatched_to_defender(tmp_path):
    file = tmp_path / 'sample.txt'
    file.write_text('hello', encoding='utf8')
    fn = method('perform_filesystem_context_action', {'Path': Path, 'DIAG': Mock()})
    errors = []
    host = SimpleNamespace(error=errors.append)
    fn(host, 'scan_defender', str(file), 'file')
    assert len(errors) == 1
    assert '未対応の操作' in errors[0]


def test_defender_icon_branch_is_inactive():
    code = (ROOT / 'src/context_menu_icons.py').read_text('utf-8')
    assert "elif action_id == 'scan_defender':" not in code
