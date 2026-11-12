"""The renamed canonical filename must never erase previously edited Launch data."""
import json
from pathlib import Path
import shutil
import tempfile

import pytest

from launch_config_path import (CONFIG_NAME, LEGACY_CONFIG_NAME, MIGRATION_MARKER,
                                ensure_launch_config)
from prepare_launch_home import READY, prepare

ROOT = Path(__file__).resolve().parents[1]


def _home(tmp_path):
    (tmp_path / 'config').mkdir(parents=True, exist_ok=True)
    return tmp_path / 'config'


def _json(label):
    return (json.dumps({'title': label, 'launch_format_version': '0.2-draft',
                        'items': [{'title': '🍣日本語の設定'}]}, ensure_ascii=False)
            + '\n').encode('utf-8')


def test_only_canonical_filename_shipped_and_version_is_in_data():
    assert (ROOT/'config'/CONFIG_NAME).exists()
    assert not (ROOT/'config'/LEGACY_CONFIG_NAME).exists()
    data = json.loads((ROOT/'config'/CONFIG_NAME).read_text('utf-8'))
    assert data['launch_format_version'] == '0.2-draft'


def test_fresh_canonical_keeps_original_bytes(tmp_path):
    config = _home(tmp_path)
    original = _json('new only')
    (config / CONFIG_NAME).write_bytes(original)
    assert ensure_launch_config(tmp_path) == config / CONFIG_NAME
    assert (config / CONFIG_NAME).read_bytes() == original
    assert (config / MIGRATION_MARKER).exists()


def test_legacy_only_migrates_losslessly_and_archives_original(tmp_path):
    config = _home(tmp_path)
    original = _json('ユーザー編集済み')
    (config / LEGACY_CONFIG_NAME).write_bytes(original)
    assert ensure_launch_config(tmp_path) == config / CONFIG_NAME
    assert (config / CONFIG_NAME).read_bytes() == original
    assert not (config / LEGACY_CONFIG_NAME).exists()
    assert (config / MIGRATION_MARKER).exists()
    backups = list((tmp_path/'backups').glob('config_filename_*/'+LEGACY_CONFIG_NAME))
    assert len(backups) == 1 and backups[0].read_bytes() == original


def test_in_place_zip_upgrade_prefers_edited_legacy_not_new_sample(tmp_path):
    config = _home(tmp_path)
    old = _json('MY PERSONAL MODIFICATIONS')
    sample = _json('BUNDLED FRESH SAMPLE')
    (config / LEGACY_CONFIG_NAME).write_bytes(old)
    (config / CONFIG_NAME).write_bytes(sample)
    assert ensure_launch_config(tmp_path) == config / CONFIG_NAME
    assert (config / CONFIG_NAME).read_bytes() == old
    backups = list((tmp_path/'backups').glob('config_filename_*/'+CONFIG_NAME))
    assert len(backups) == 1 and backups[0].read_bytes() == sample
    # An abandoned legacy file after an earlier successful upgrade must not win.
    (config / LEGACY_CONFIG_NAME).write_bytes(_json('stale legacy'))
    assert ensure_launch_config(tmp_path) == config / CONFIG_NAME
    assert (config / CONFIG_NAME).read_bytes() == old


def test_invalid_legacy_fails_before_touching_new_config(tmp_path):
    config = _home(tmp_path)
    sample = _json('safe')
    (config / CONFIG_NAME).write_bytes(sample)
    (config / LEGACY_CONFIG_NAME).write_bytes(b'{ broken json')
    with pytest.raises(ValueError, match='JSON'):
        ensure_launch_config(tmp_path)
    assert (config / CONFIG_NAME).read_bytes() == sample
    assert (config / LEGACY_CONFIG_NAME).exists()


def test_existing_ready_home_migrates_old_filename_and_preserves_user_fields(tmp_path):
    config = _home(tmp_path)
    user_data = json.loads((ROOT/'config'/CONFIG_NAME).read_text('utf-8'))
    user_data['title'] = 'ユーザー編集済みの設定！'
    old = (json.dumps(user_data, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    (config / LEGACY_CONFIG_NAME).write_bytes(old)
    (config / CONFIG_NAME).write_bytes(_json('bundled sample'))
    (tmp_path / READY).write_text('ready', encoding='utf-8')
    assert prepare(tmp_path) is None
    # Browser-bookmark migration should not rewrite the already-bootstrapped doc.
    assert (config / CONFIG_NAME).read_bytes() == old
    assert (config / MIGRATION_MARKER).exists()


def test_first_build_preserves_editable_old_dist_even_if_new_sample_present(tmp_path):
    config = _home(tmp_path)
    shipped = (ROOT/'config'/CONFIG_NAME).read_bytes()
    (config / CONFIG_NAME).write_bytes(shipped)
    dist_config = tmp_path/'dist'/'FRBLaunch'/'config'
    dist_config.mkdir(parents=True)
    customized = json.loads(shipped.decode('utf-8'))
    customized['title'] = '旧distで編集した設定'
    (dist_config / LEGACY_CONFIG_NAME).write_text(
        json.dumps(customized, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    backup = prepare(tmp_path)
    assert backup is not None
    live = json.loads((config / CONFIG_NAME).read_text('utf-8'))
    assert live['title'] == '旧distで編集した設定'
    assert (backup/'previous_dist'/'config'/LEGACY_CONFIG_NAME).exists()
    assert (config / MIGRATION_MARKER).exists()
    assert not (config / LEGACY_CONFIG_NAME).exists()


def test_source_references_and_studio_open_follow_canonical_file():
    app = (ROOT/'src/app.py').read_text('utf-8')
    assert 'CONFIG = ensure_launch_config(LAUNCH_HOME)' in app
    assert "'--open-json=' + str(CONFIG)" in app
    assert "launch_data=str(CONFIG)" in app
    assert CONFIG_NAME in (ROOT/'scripts/Backup-FrbLaunch.ps1').read_text('utf-8')
    assert LEGACY_CONFIG_NAME not in app
