"""Bound FRB Launch diagnostic files without touching unrelated user data.

Per-invocation PowerShell transcripts remain independent, so simultaneous device
commands do not contend for the same transcript. Retention runs at application
startup and after a waited-for process finishes. Process logs have a short
minimum age; audio configuration backups use a strict latest-N limit.
"""
import json
import re
import time
from pathlib import Path

DEFAULTS = {
    'enabled': True,
    'process_logs_keep_each': 5,
    'process_logs_min_age_minutes': 10,
    'audio_config_backups_keep': 5,
}

_PATTERNS = {
    'wifi_process': re.compile(r'wifi_process_\d{8}_\d{6}_[0-9a-fA-F]{8}\.log\Z'),
    'audio_process': re.compile(r'audio_process_\d{8}_\d{6}_[0-9a-fA-F]{8}\.log\Z'),
    'audio_config': re.compile(r'audio_config_\d{8}_\d{6}_[0-9a-fA-F]{32}\.json\Z'),
}


def load_options(path):
    """Read optional local policy, falling back safely if the file is absent."""
    config = DEFAULTS.copy()
    path = Path(path)
    if path.exists():
        obj = json.loads(path.read_text(encoding='utf-8-sig'))
        if not isinstance(obj, dict):
            raise ValueError('Log retention options must be a JSON object')
        for key, default in DEFAULTS.items():
            if key not in obj:
                continue
            value = obj[key]
            if isinstance(default, bool):
                if not isinstance(value, bool):
                    raise ValueError(f'{key} must be true or false')
            elif type(value) is not int or not 0 <= value <= 3650:
                raise ValueError(f'{key} must be a non-negative integer <=3650')
            config[key] = value
    return config


def cleanup(folder, options_path=None, *, now=None):
    """Prune only FRB-generated files that match exact known filenames.

    A minimum age protects process logs that might still be written by detached
    child processes. Audio configuration backups instead retain only the newest
    N files, regardless of age. Failed deletions are retried on the next run.
    Returns a dict of successfully removed file counts by category.
    """
    folder = Path(folder)
    options = load_options(options_path) if options_path is not None else DEFAULTS.copy()
    deleted = {name: 0 for name in _PATTERNS}
    if not options['enabled'] or not folder.is_dir():
        return deleted
    now = time.time() if now is None else now
    policies = {
        'wifi_process': (options['process_logs_keep_each'], options['process_logs_min_age_minutes'] * 60),
        'audio_process': (options['process_logs_keep_each'], options['process_logs_min_age_minutes'] * 60),
        'audio_config': (options['audio_config_backups_keep'], None),
    }
    for name, pattern in _PATTERNS.items():
        candidates = []
        for path in folder.iterdir():
            if not pattern.fullmatch(path.name) or path.is_symlink() or not path.is_file():
                continue
            try:
                candidates.append((path.stat().st_mtime, path))
            except OSError:
                continue
        candidates.sort(key=lambda entry: (entry[0], entry[1].name), reverse=True)
        keep, min_age = policies[name]
        for mtime, path in candidates[keep:]:
            if min_age is not None and now - mtime < min_age:
                continue
            try:
                path.unlink()
                deleted[name] += 1
            except OSError:
                # e.g. Windows antivirus or a transcript that is still open.
                continue
    return deleted
