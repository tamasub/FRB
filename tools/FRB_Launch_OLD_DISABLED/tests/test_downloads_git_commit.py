"""Downloads-only ordering and filename-based Git commit checks."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from context_menu_actions import (
    is_downloads_directory, is_downloads_zip, sort_browser_entries,
    read_git_commit_options, git_commit_preview, commit_tracked_changes,
)
from context_menu_config import load_context_menus


def git(repo, *args):
    return subprocess.run(['git', *args], cwd=repo, check=True, text=True,
                          capture_output=True).stdout.strip()


def test_downloads_only_newest_first(monkeypatch, tmp_path):
    home = tmp_path / 'home'
    downloads = home / 'Downloads'
    elsewhere = home / 'other'
    downloads.mkdir(parents=True)
    elsewhere.mkdir()
    monkeypatch.setenv('USERPROFILE', str(home))
    for parent in (downloads, elsewhere):
        for name, timestamp in [('a.zip', 1000), ('z.zip', 2000), ('middle.txt', 1500)]:
            p = parent / name
            p.write_text(name)
            os.utime(p, (timestamp, timestamp))
    assert is_downloads_directory(downloads)
    assert [p.name for p in sort_browser_entries(downloads)] == ['z.zip', 'middle.txt', 'a.zip']
    assert [p.name for p in sort_browser_entries(elsewhere)] == ['a.zip', 'middle.txt', 'z.zip']
    assert is_downloads_zip(downloads / 'a.zip')
    assert is_downloads_zip(downloads / 'Z.ZIP')
    assert not is_downloads_zip(elsewhere / 'a.zip')
    assert not is_downloads_zip(downloads / 'middle.txt')
    assert not is_downloads_zip(downloads / 'sub' / 'a.zip')


def test_context_is_declared_and_only_single_file_action():
    config = Path(__file__).resolve().parents[1] / 'config/context_menu_options.json'
    menus = load_context_menus(config)
    assert any(x['action_id'] == 'git_commit_from_zip' for x in menus['file'])
    assert not any(x['action_id'] == 'git_commit_from_zip' for x in menus['folder'])


def test_git_commit_filename_and_no_untracked(tmp_path):
    repo = tmp_path / 'repository'
    repo.mkdir()
    git(repo, 'init', '-q')
    git(repo, 'config', 'user.name', 'Test')
    git(repo, 'config', 'user.email', 'test@example.test')
    tracked = repo / 'tracked.txt'
    tracked.write_text('old')
    git(repo, 'add', 'tracked.txt')
    git(repo, 'commit', '-qm', 'initial')
    tracked.write_text('changed')
    (repo / 'untracked.txt').write_text('not staged')
    options_file = tmp_path / 'opts.json'
    options_file.write_text(json.dumps({'version': 1, 'enabled': True, 'repository_path': str(repo)}))
    opts = read_git_commit_options(options_file)
    preview = git_commit_preview(opts)
    assert preview['repository'] == repo
    assert any('tracked.txt' in line for line in preview['changes'])
    assert all('untracked.txt' not in line for line in preview['changes'])
    result = commit_tracked_changes(repo, 'FRBStudio_changes_20261023.zip')
    assert result.endswith('FRBStudio_changes_20261023.zip')
    assert git(repo, 'log', '-1', '--format=%s') == 'FRBStudio_changes_20261023.zip'
    assert git(repo, 'ls-files') == 'tracked.txt'
    assert (repo / 'untracked.txt').exists()
    with pytest.raises(ValueError, match='コミット対象'):
        git_commit_preview(opts)


def test_no_git_when_not_repository(tmp_path):
    with pytest.raises(RuntimeError):
        git_commit_preview({'enabled': True, 'repository_path': str(tmp_path)})


def test_configuration_validation(tmp_path):
    path = tmp_path / 'settings.json'
    path.write_text('{"version": 1, "enabled": "true", "repository_path": "x"}')
    with pytest.raises(ValueError, match='enabled'):
        read_git_commit_options(path)


def test_message_rejects_newlines(tmp_path):
    with pytest.raises(ValueError, match='1行'):
        commit_tracked_changes(tmp_path, 'a\nother')


def test_opt_in_adds_untracked_files(tmp_path):
    repo = tmp_path / 'repo'
    repo.mkdir()
    git(repo, 'init', '-q')
    git(repo, 'config', 'user.name', 'Test')
    git(repo, 'config', 'user.email', 'test@example.test')
    (repo / 'new-file.txt').write_text('new')
    options = {'enabled': True, 'repository_path': str(repo), 'include_untracked': True}
    preview = git_commit_preview(options)
    assert any('new-file.txt' in line for line in preview['changes'])
    assert commit_tracked_changes(repo, 'feature.zip', include_untracked=True).endswith('feature.zip')
    assert git(repo, 'ls-files') == 'new-file.txt'
