"""Regression contracts for the optional FRB Launch local-data backup sample.

PowerShell runs on Windows only. These cross-platform checks validate the
configured launch action and guard the explicitly whitelisted copy scope.
"""
import json
from pathlib import Path

from core import Expander, validate

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config' / 'frb_launch_data.json'
PS = ROOT / 'scripts' / 'Backup-FrbLaunch.ps1'


def script():
    return PS.read_text(encoding='utf-8')


def test_user_backup_row_is_registered_under_zip_category():
    data = json.loads(CONFIG.read_text(encoding='utf-8'))
    validate(data)
    entries = [row for row in data['items'] if row['item_id'] == 'launch_user_backup_zip']
    assert len(entries) == 1
    row = entries[0]
    assert row['page_id'] == 'work'
    assert row['parent_item_id'] == 'zip'
    assert row['item_kind'] == 'command'
    assert row['enabled'] is True
    assert row['launch_actions'] == [{
        'launch_action_type': 'Open',
        'launch_target': '%launch_home%\\backup_frb_launch_sample.bat',
    }]


def test_user_backup_path_resolves_from_launch_home():
    data = json.loads(CONFIG.read_text(encoding='utf-8'))
    action = next(row for row in data['items']
                  if row['item_id'] == 'launch_user_backup_zip')['launch_actions'][0]
    expanded = Expander(data, values={'launch_home': r'F:\FRB\tools\FRB_Launch'}).expand(
        action['launch_target'])
    assert expanded == r'F:\FRB\tools\FRB_Launch\backup_frb_launch_sample.bat'
    assert (ROOT / 'backup_frb_launch_sample.bat').is_file()
    assert PS.is_file()


def test_backup_destination_and_atomic_finalization():
    ps = script()
    assert "Join-Path $userDataDir '_Backups'" in ps
    assert "[System.IO.File]::Move($tempPath, $zipPath)" in ps
    assert 'FileMode]::CreateNew' in ps
    assert 'ReparsePoint' in ps
    assert 'Remove-Item -LiteralPath $tempPath' in ps
    assert 'Remove-Item -LiteralPath $userDataDir' not in ps


def test_launch_home_is_derived_from_script_directory():
    bat = (ROOT / 'backup_frb_launch_sample.bat').read_text(encoding='ascii')
    ps = script()
    assert '-LaunchHome' not in bat
    assert '"%~dp0scripts\\Backup-FrbLaunch.ps1"' in bat
    assert '$root = Split-Path -Parent $PSScriptRoot' in ps
    assert 'GetFullPath($LaunchHome)' not in ps


def test_logs_are_best_effort_but_settings_strict():
    ps = script()
    assert 'function Add-LiveLogFile' in ps
    assert '[System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete' in ps
    assert 'catch [System.IO.IOException]' in ps
    assert '[WARN] Active log skipped:' in ps
    assert 'isDiagnosticLog' in ps
    assert 'Add-LiveLogFile -SourceFile $child.FullName' in ps
    assert '[System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(' in ps
    assert '[WARN] Skipped active diagnostic log(s): ' in ps


def test_live_logs_capture_only_initial_length():
    ps = script()
    assert '$remaining = [long]$inputStream.Length' in ps
    assert '$remaining -= $read' in ps
    assert '$inputStream.Dispose()' in ps


def test_explicit_whitelist_for_user_data_instead_of_recursive_backup():
    ps = script()
    assert 'function Add-UserSettingsAndLogs' in ps
    assert 'Add-UserSettingsAndLogs -Source $userDataDir -Destination $archive' in ps
    assert 'Add-BackupDirectory -Source $userDataDir' not in ps
    # Top-level files only. No general recursion is permitted from user_data.
    user_function = ps.split('function Add-UserSettingsAndLogs {', 1)[1].split('\ntry {\n    Add-Type', 1)[0]
    assert 'Get-ChildItem -LiteralPath $Source' in user_function
    assert "if ($child.Name -match '(?i)^(log|logs|diagnostic|diagnostics)$')" in user_function
    assert 'Add-BackupDirectory -Source $child.FullName' in user_function
    assert '$isSettingsFile = ($name -match' in user_function
    assert "(?i)\\.(json|ini)$" in user_function
    assert 'if ($isDiagnosticLog)' in user_function
    assert 'elseif ($isSettingsFile)' in user_function
    # No general Add-BackupDirectory call on an arbitrary subfolder.
    assert user_function.count('Add-BackupDirectory -Source $child.FullName') == 1


def test_web_profile_and_backup_directory_excluded_before_recursion():
    ps = script()
    user_function = ps.split('function Add-UserSettingsAndLogs {', 1)[1].split('\ntry {\n    Add-Type', 1)[0]
    assert "$child.Name -ieq 'web_profile'" in user_function
    assert "$child.Name -ieq '_Backups'" in user_function
    assert 'Unlisted user-data directory excluded' in user_function
    assert 'Backup/runtime/browser directory excluded' in user_function
    # Explicit folder allowlist rejects cookie DB even when WebEngine is active.
    assert user_function.index("$child.Name -match '(?i)^(log|logs|diagnostic|diagnostics)$'") < user_function.index(
        'Add-BackupDirectory -Source $child.FullName')


def test_runtime_files_skipped_and_personal_json_preserved():
    ps = script()
    assert "$name -match '(?i)\\.(lock|lck|tmp)$'" in ps
    assert "$name -match '(?i)^file_index\\.db(?:-wal|-shm|-journal)?$'" in ps
    assert "$name -match '(?i)^apps_scan_.*\\.json$'" in ps
    assert "$name -match '(?i)^apps_cache\\.json$'" in ps
    assert 'if ($isRuntimeFile)' in ps
    assert "Add-BackupDirectory -Source $configDir -EntryPrefix 'config'" in ps
    assert "Add-BackupDirectory -Source (Join-Path $root 'defs\\launch')" in ps
    assert '$script:entryCount++' in ps


def test_state_restoration_and_cookie_scope_documented():
    ps = script()
    doc = (ROOT / 'docs' / 'FRBLaunch_UserBackup_Sample_20261109.md').read_text(encoding='utf-8')
    assert 'Browser cookies/sessions are not included' in ps
    assert 'web_profile' in doc
    assert '再ログイン' in doc
    assert 'state.ini' in doc


def test_explorer_opens_backup_folder_only_after_successful_commit():
    ps = script()
    commit_pos = ps.index('[System.IO.File]::Move($tempPath, $zipPath)')
    completed_pos = ps.index('$completed = $true', commit_pos)
    explorer_pos = ps.index("Start-Process -FilePath 'explorer.exe'", completed_pos)
    assert commit_pos < completed_pos < explorer_pos
    assert "-ArgumentList ('\"' + $outDir + '\"')" in ps
    # Prevent a GUI-only failure from changing the completed ZIP's exit status.
    explorer_failure = ps[explorer_pos:ps.index('} catch {\n    Write-Host (\'[ERROR] ', explorer_pos)]
    assert '[WARN] Backup ZIP was created, but Explorer could not open:' in explorer_failure
    assert 'exit 1' not in explorer_failure


def test_explorer_path_is_not_hardcoded_to_author_machine():
    ps = script()
    assert "Join-Path $userDataDir '_Backups'" in ps
    assert "[Environment]::GetFolderPath('LocalApplicationData')" in ps
    assert 'C:\\Users\\tsub-' not in ps
