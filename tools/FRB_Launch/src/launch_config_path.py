"""Stable Launch config name and lossless one-time migration of the old filename.

User-edited data, not the shipped default JSON, is the source of truth when
an existing Launch home is upgraded in place. No JSON fields are rewritten.
"""
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from uuid import uuid4

CONFIG_NAME = 'frb_launch_data.json'
LEGACY_CONFIG_NAME = 'frb_launch_sample_data_v0_1.json'
MIGRATION_MARKER = '.frb_launch_data_name_v1'


def _archive_config(root, paths):
    """Backup both possible versions before changing or deleting either one."""
    backup = Path(root) / 'backups' / (
        'config_filename_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid4().hex[:6]
    )
    backup.mkdir(parents=True, exist_ok=False)
    for path in paths:
        if path.is_file():
            shutil.copy2(path, backup / path.name)
    return backup


def _validate_json_bytes(contents, source):
    try:
        data = json.loads(contents.decode('utf-8-sig'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f'Launch設定JSONが不正です: {source}: {exc}') from exc
    if not isinstance(data, dict):
        raise ValueError(f'Launch設定JSONのルートがオブジェクトではありません: {source}')


def ensure_launch_config(home):
    """Return the canonical config; preserve a pre-existing legacy user's file.

    A full ZIP may already contain the new sample JSON next to the user's old
    JSON. On first upgrade the old JSON wins. A durable marker makes subsequent
    launches idempotent; older leftover files cannot replace the live config.
    """
    root = Path(home).resolve()
    config_dir = root / 'config'
    canonical = config_dir / CONFIG_NAME
    legacy = config_dir / LEGACY_CONFIG_NAME
    marker = config_dir / MIGRATION_MARKER
    if marker.is_file():
        if not canonical.is_file():
            raise RuntimeError('Launch設定が見つかりません: ' + str(canonical))
        return canonical
    if legacy.is_file():
        original = legacy.read_bytes()
        _validate_json_bytes(original, legacy)
        backup = _archive_config(root, (legacy, canonical))
        tmp = canonical.with_name(canonical.name + '.' + uuid4().hex + '.tmp')
        try:
            with tmp.open('xb') as fp:
                fp.write(original)
                fp.flush()
                os.fsync(fp.fileno())
            os.replace(tmp, canonical)
            # Remove the obsolete live filename after it is safely archived.
            legacy.unlink()
            marker.write_text('Legacy JSON preserved in ' + str(backup) + '\n', encoding='utf-8')
        finally:
            tmp.unlink(missing_ok=True)
        return canonical
    if not canonical.is_file():
        raise RuntimeError('Launch設定が見つかりません: ' + str(canonical))
    _validate_json_bytes(canonical.read_bytes(), canonical)
    marker.write_text('Canonical FRB Launch config filename enabled.\n', encoding='utf-8')
    return canonical
