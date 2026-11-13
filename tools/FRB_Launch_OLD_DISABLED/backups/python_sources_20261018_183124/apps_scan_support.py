"""App catalog diagnostics and least-privilege fallback for managed Windows PCs.

The fallback only discovers existing Start Menu .lnk files.  It does not
resolve targets, invoke PowerShell/COM, bypass policy, or write to the Start Menu.
"""
from datetime import datetime
import os
from pathlib import Path


def append_apps_log(path, event, detail=''):
    """Log even when powershell.exe could not be launched or parsed the script.

    Returns False if the user profile denies logging, rather than crashing the launcher.
    """
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        line = str(detail).replace('\r', '\\r').replace('\n', '\\n')[:2500]
        with path.open('a', encoding='utf-8') as output:
            output.write(f'{datetime.now():%Y-%m-%d %H:%M:%S} {event} {line}\n')
        return True
    except OSError:
        return False


def shortcut_roots(env=None):
    env = os.environ if env is None else env
    sources = (env.get('APPDATA'), env.get('PROGRAMDATA'))
    roots = []
    seen = set()
    for source in sources:
        if not source:
            continue
        root = Path(source) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs'
        key = os.path.normcase(str(root)).casefold()
        if key not in seen:
            seen.add(key)
            roots.append(root)
    return roots


def scan_shortcuts(env=None):
    """Discover names and .lnk paths without WScript.Shell/COM/PowerShell.

    Each folder is independent: access-denied, redirection or missing folders
    must not discard entries already collected from the other folder.
    Returns (records, warnings); result is ALWAYS partial coverage.
    """
    records = []
    warnings = []
    roots = shortcut_roots(env)
    if not roots:
        warnings.append('APPDATA/PROGRAMDATA environment variables are unavailable')
    for root in roots:
        try:
            if not root.is_dir():
                warnings.append(f'Start Menu directory unavailable: {root}')
                continue
            def onerror(error):
                warnings.append(f'Start Menu subdirectory could not be read: {error}')
            for dirname, _directories, files in os.walk(root, onerror=onerror, followlinks=False):
                for name in files:
                    if not name.lower().endswith('.lnk'):
                        continue
                    target = Path(dirname) / name
                    records.append({'name': name[:-4], 'target': str(target), 'kind': 'shortcut', 'icon_path': str(target)})
        except OSError as error:
            warnings.append(f'Start Menu scan failed ({root}): {error}')
    return records, warnings


def merge_catalog(old_records, fresh_records, partial=False):
    """On partial coverage preserve previously known entries, notably UWP AUMIDs."""
    from installed_apps import normalize
    fresh = normalize(fresh_records)
    return normalize(fresh + normalize(old_records)) if partial else fresh
