"""Persistent, root-scoped file index for FRB Launch.

Indexing may use registered launch folders, separately configured folders, or be disabled. v0.2
compares filename/path snapshots and transactionally updates only changed
roots; the legacy full-build function remains for compatibility.
"""
from __future__ import annotations

import json
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import ntpath
import re
import os
import sqlite3
import tempfile
import fnmatch
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from search_matching import sql_search_condition, parse_search_query

DEFAULT_OPTIONS = {
    'enabled': True,  # Backward-compatible switch; false overrides index_mode.
    'index_mode': 'registered',  # registered / configured / off
    'index_folders': [],  # Used only in configured mode; absolute paths, spaces OK.
    'max_depth': None,  # None=recursive, 0=files in root only, 1=one child level.
    'extensions': ['.bat', '.py', '.ps1', '.json', '.xlsx', '.md'],
    'exclude_name_contains': ['view_def'],
    'exclude_directories': ['.venv', '.git', 'node_modules', '__pycache__', 'build', 'dist', 'System Volume Information', '$RECYCLE.BIN'],
    'exclude_directory_globs': [],  # Relative paths or folder names; e.g. '**/Broken (*)'.
    'scan_error_policy': 'preserve_cached',  # or 'fail_root'; see README.

    'search_limit': 100,
    'update_mode': 'manual',
    'auto_update': {'startup_delay_seconds': 90, 'check_interval_minutes': 30, 'max_scan_workers': 2},
}


def load_options(path):
    """Keep all index options in a separate, human-editable settings JSON."""
    path = Path(path)
    raw = json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else {}
    if not isinstance(raw, dict):
        raise ValueError('file_index_options.json はJSONオブジェクトにしてください')
    options = {**DEFAULT_OPTIONS, **raw}
    if options['index_mode'] not in ('registered', 'configured', 'off'):
        raise ValueError('index_mode は registered / configured / off を指定してください')
    if not isinstance(options['index_folders'], list) or not all(
            isinstance(x, str) and x.strip() for x in options['index_folders']):
        raise ValueError('index_folders は空でないパス文字列の配列にしてください')
    if options['max_depth'] is not None and (
            type(options['max_depth']) is not int or not 0 <= options['max_depth'] <= 100):
        raise ValueError('max_depth は null または 0～100 の整数にしてください')
    if options['update_mode'] not in ('manual', 'auto'):
        raise ValueError('update_mode は manual / auto を指定してください')
    auto = options.get('auto_update', {})
    if not isinstance(auto, dict):
        raise ValueError('auto_update はJSONオブジェクトにしてください')
    auto = {**DEFAULT_OPTIONS['auto_update'], **auto}
    limits = {'startup_delay_seconds': (0, 3600),
              'check_interval_minutes': (1, 1440),
              'max_scan_workers': (1, 99)}
    for key, (minimum, maximum) in limits.items():
        if type(auto[key]) is not int or not minimum <= auto[key] <= maximum:
            raise ValueError(f'auto_update.{key} は {minimum}～{maximum} の整数にしてください')
    options['auto_update'] = auto
    for key in ('extensions', 'exclude_name_contains', 'exclude_directories', 'exclude_directory_globs'):
        if not isinstance(options[key], list) or not all(isinstance(x, str) for x in options[key]):
            raise ValueError(f'{key} は文字列配列にしてください')
    if options['scan_error_policy'] not in ('preserve_cached', 'fail_root'):
        raise ValueError('scan_error_policy は preserve_cached / fail_root を指定してください')
    extensions = {x.strip().casefold() for x in options['extensions']}
    if not extensions or any(not x.startswith('.') or len(x) < 2 or '/' in x or '\\' in x for x in extensions):
        raise ValueError('extensions には .py などの拡張子を指定してください')
    options['extensions'] = sorted(extensions)
    if not isinstance(options['enabled'], bool):
        raise ValueError('enabled はtrue/falseで指定してください')
    if type(options['search_limit']) is not int or not 1 <= options['search_limit'] <= 500:
        raise ValueError('search_limit は1～500で指定してください')
    return options


def index_mode(options):
    """Legacy enabled:false always means off (including old installations)."""
    return 'off' if not options.get('enabled', True) else options.get('index_mode', 'registered')


def configured_roots(options, *, include_unavailable=True):
    """Separate index scope from the launch JSON; do not tokenize paths at spaces.

    Never interpret paths as shell commands. Environment vars and ~ are allowed,
    but relative paths and drive/share roots are rejected to avoid surprise scans.
    Unavailable roots are retained in the desired set so a disconnected sync
    drive cannot silently wipe an older index snapshot.
    """
    roots, warnings = [], []
    for raw in options.get('index_folders', []):
        expanded = os.path.expanduser(os.path.expandvars(raw.strip()))
        # ntpath handles Windows %VAR% even when unit tests run on POSIX.
        expanded = ntpath.expandvars(expanded)
        if re.search(r'%[A-Za-z_][A-Za-z0-9_]*%', expanded):
            raise ValueError(f'環境変数を展開できないパスです: {raw}')
        if not os.path.isabs(expanded):
            raise ValueError(f'index_folders には絶対パスを指定してください: {raw}')
        path = os.path.abspath(expanded)
        drive, tail = ntpath.splitdrive(path)
        # C:\, //server/share, or the POSIX filesystem root.
        if os.path.normpath(path) == os.path.normpath(os.path.abspath(os.sep)) or (
                drive and not tail.strip('\\/')):
            raise ValueError(f'ドライブルート/共有ルートは索引できません。下位フォルダーを指定してください: {path}')
        if not os.path.isdir(_windows_scan_path(path)):
            warnings.append(f'指定フォルダーを利用できません: {path}')
            if not include_unavailable:
                continue
        # An explicitly configured cloud folder may itself be a junction;
        # traversal still avoids following links encountered *under* the root.
        roots.append(path)
    return minimize_roots(roots), warnings


def resolve_roots(options, launch_data=None, expand=None, *, include_unavailable=True):
    """Resolve one of three independent indexing scopes."""
    mode = index_mode(options)
    if mode == 'off':
        return [], []
    if mode == 'configured':
        return configured_roots(options, include_unavailable=include_unavailable)
    if launch_data is None or expand is None:
        raise ValueError('registered モードにはランチャー設定が必要です')
    return registered_roots(launch_data, expand, include_unavailable=include_unavailable)


def clear_index(database):
    """Atomically empty the generated index, without unlinking its SQLite file.

    Windows prevents deleting a database while another connection holds it open
    (WinError 32).  Clearing rows in a single transaction is safe with other
    readers in WAL mode, and deleting index_roots as well as files guarantees
    the next refresh really rebuilds the index rather than reusing old digests.

    The launcher disables this action while its index writer is working.  If an
    unrelated writer keeps SQLite locked, raise an error and preserve the old
    data rather than reporting a partial/silent success.
    """
    database = Path(database)
    if not database.is_file():
        return False
    with closing(sqlite3.connect(database, timeout=5)) as db:
        db.execute('PRAGMA busy_timeout=5000')
        tables = {name for (name,) in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name IN ('files', 'index_roots', 'metadata')")}
        # The old index schema lacks index_roots. Handle both versions without
        # dropping tables, modifying the journal mode, or touching WAL sidecars.
        with db:
            for name in ('files', 'index_roots', 'metadata'):
                if name in tables:
                    db.execute(f'DELETE FROM {name}')
    return True


def _normalized_path(path):
    """Cross-platform boundary-aware comparison for registered roots."""
    text = str(path)
    if ntpath.splitdrive(text)[0] or '\\' in text:
        return ntpath.normcase(ntpath.normpath(text))
    return os.path.normcase(os.path.normpath(text))


def _contains(ancestor, child):
    a, b = _normalized_path(ancestor), _normalized_path(child)
    pathmod = ntpath if ntpath.splitdrive(a)[0] or '\\' in a else os.path
    try:
        return pathmod.commonpath((a, b)) == a
    except ValueError:
        return False


def minimize_roots(paths):
    """Only remove descendants of an explicitly registered ancestor."""
    result = []
    for path in paths:
        path = str(path)
        if any(_contains(existing, path) for existing in result):
            continue
        result = [existing for existing in result if not _contains(path, existing)]
        result.append(path)
    return result


def registered_roots(data, expand, *, include_unavailable=False):
    pages = {x.get('page_id'): x for x in data.get('pages', [])}
    items = {x.get('item_id'): x for x in data.get('items', [])}
    roots, errors = [], []
    for row in data.get('items', []):
        if row.get('item_kind') != 'directory' or not row.get('enabled', True):
            continue
        page = pages.get(row.get('page_id'))
        if not page or not page.get('enabled', True):
            continue
        ancestor, seen, hidden = row.get('parent_item_id'), set(), False
        while ancestor:
            if ancestor in seen or ancestor not in items or not items[ancestor].get('enabled', True):
                hidden = True; break
            seen.add(ancestor)
            ancestor = items[ancestor].get('parent_item_id')
        if hidden:
            continue
        target = row.get('launch_browse_target', '')
        if not target:
            continue
        try:
            path = os.path.abspath(os.path.expanduser(expand(target)))
            if not os.path.isdir(_windows_scan_path(path)):
                errors.append(f'登録フォルダーが存在しません: {path}')
                if include_unavailable:
                    roots.append(path)
                continue
            # Never follow a linked root beyond the registered path.
            if os.path.islink(_windows_scan_path(path)) or (hasattr(os.path, 'isjunction') and os.path.isjunction(_windows_scan_path(path))):
                errors.append(f'リンク先フォルダーは索引対象外: {path}')
                continue
            roots.append(path)
        except (OSError, ValueError) as exc:
            errors.append(f'{row.get("title", "directory")}: {exc}')
    return minimize_roots(roots), errors


def _windows_scan_path(path):
    """Use Win32 extended-length paths for deep Box/SharePoint sync trees.

    Parentheses, spaces, Unicode, % and ! are *literal* path characters;
    no cmd.exe/PowerShell parsing or string escaping is involved.
    """
    path = os.fspath(path)
    if os.name != 'nt' or path.startswith('\\\\?\\'):
        return path
    absolute = os.path.abspath(path)
    if absolute.startswith('\\\\'):
        return '\\\\?\\UNC\\' + absolute.lstrip('\\')
    return '\\\\?\\' + absolute


def _original_scan_path(path):
    path = os.fspath(path)
    if path.startswith('\\\\?\\UNC\\'):
        return '\\\\' + path[len('\\\\?\\UNC\\'):]
    if path.startswith('\\\\?\\'):
        return path[len('\\\\?\\'):]
    return path


def _excluded_folder(options, root, child):
    """Match user-configured globs against both leaf name and root-relative path."""
    patterns = options.get('exclude_directory_globs', [])
    name = os.path.basename(child).casefold()
    relative = os.path.relpath(child, root).replace('\\', '/').casefold()
    return any(fnmatch.fnmatchcase(name, pattern.casefold()) or
               fnmatch.fnmatchcase(relative, pattern.replace('\\', '/').casefold())
               for pattern in patterns if pattern)


def _digest_rows(rows):
    digest = hashlib.sha256()
    for row in rows:
        digest.update(os.path.normpath(row[0]).encode('utf-8', errors='surrogatepass'))
        digest.update(b'\0')
    return digest.hexdigest()


def _preserve_failed_subtrees(db, scanned):
    """Keep cached entries below inaccessible subfolders; never erase them.

    The newly scanned branches still update normally.  A previously unseen
    inaccessible branch remains missing, but is recorded as a warning.
    """
    failed = scanned.get('failed_dirs', ())
    if not failed:
        return scanned
    rows = { _normalized_path(r[0]): r for r in scanned['rows'] }
    for p, name, folded, folder, extension, key in db.execute(
            'SELECT path,name,name_fold,directory,extension,root_key FROM files WHERE root_key=?',
            (scanned['key'],)):
        if any(_contains(directory, p) for directory in failed):
            rows.setdefault(_normalized_path(p), (p, name, folded, folder, extension, key))
    scanned['rows'] = sorted(rows.values(), key=lambda row: _normalized_path(row[0]))
    scanned['count'] = len(scanned['rows'])
    scanned['digest'] = _digest_rows(scanned['rows'])
    return scanned


def _scan(roots, options, connection):
    extensions = set(options['extensions'])
    hidden = tuple({'view_def', *(x.casefold() for x in options['exclude_name_contains'] if x)})
    excluded_dirs = {x.casefold() for x in options['exclude_directories']}
    max_depth = options.get('max_depth')
    inserted, skipped, errors = 0, 0, []
    cur = connection.cursor()
    def onerror(error):
        errors.append(str(error))
    for root in roots:
        if not os.path.isdir(root):
            raise FileNotFoundError(f'索引更新中に対象フォルダーが見つからなくなりました: {root}')
        # Detect root permission failures before accepting a partial scan.
        with os.scandir(root) as check:
            next(check, None)
        for parent, dirs, files in os.walk(root, topdown=True, followlinks=False, onerror=onerror):
            if max_depth is not None and os.path.relpath(parent, scan_root).count(os.sep) + (parent != scan_root) >= max_depth:
                skipped += len(dirs)
                dirs[:] = []
            retained = []
            for dirname in dirs:
                child = os.path.join(parent, dirname)
                if (dirname.casefold() in excluded_dirs or _excluded_folder(options, root, child)
                    or os.path.islink(child) or (
                    hasattr(os.path, 'isjunction') and os.path.isjunction(child))):
                    skipped += 1
                else:
                    retained.append(dirname)
            dirs[:] = retained
            for name in files:
                extension = os.path.splitext(name)[1].casefold()
                if extension not in extensions or any(token in name.casefold() for token in hidden):
                    skipped += 1; continue
                path = os.path.join(parent, name)
                if os.path.islink(path):
                    skipped += 1; continue
                cur.execute('INSERT OR IGNORE INTO files(path, name, name_fold, directory, extension) VALUES(?,?,?,?,?)',
                            (path, name, name.casefold(), parent, extension))
                inserted += cur.rowcount
        connection.commit()
    return inserted, skipped, errors


def build_index(database, roots, options, *, root_warnings=()):
    """Build in a temporary database; keep the previous cache on any failure."""
    database = Path(database)
    if not roots:
        raise ValueError('索引対象の実フォルダー展開先がありません（設定を確認してください）')
    database.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.file_index_', suffix='.db', dir=database.parent)
    os.close(fd)
    temporary = Path(name)
    try:
        with closing(sqlite3.connect(temporary)) as db:
            db.execute('CREATE TABLE files(path TEXT PRIMARY KEY COLLATE NOCASE, name TEXT NOT NULL, name_fold TEXT NOT NULL, directory TEXT NOT NULL, extension TEXT NOT NULL)')
            db.execute('CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL)')
            count, excluded, errors = _scan(roots, options, db)
            # Inaccessible subfolders are skipped and reported, rather than
            # failing an entire drive scan (e.g. a Windows system folder).
            metadata = {
                'updated_at': datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds'),
                'count': count, 'excluded': excluded,
                'roots': list(roots), 'extensions': options['extensions'],
                'warnings': [*root_warnings, *errors[:15]],
                'scan_errors': len(errors),
            }
            db.executemany('INSERT INTO metadata(key,value) VALUES(?,?)',
                           [(key, json.dumps(value, ensure_ascii=False)) for key, value in metadata.items()])
            db.commit()
        os.replace(temporary, database)
        return metadata
    finally:
        temporary.unlink(missing_ok=True)


def index_status(database):
    if not Path(database).is_file():
        return None
    try:
        with closing(sqlite3.connect(database, timeout=1)) as db:
            metadata = {key: json.loads(value) for key, value in db.execute('SELECT key, value FROM metadata')}
            # Empty metadata means the cache was cleared; it is not a valid
            # index status (the tray expects updated_at/count/etc.).
            return metadata or None
    except (sqlite3.Error, OSError, ValueError):
        return None


def search_index(database, query, limit=100):
    """Match each space-separated term against the indexed file's full path.

    Full path includes the filename, so terms may independently match folder
    names or filenames. Retain name_fold for Unicode-insensitive basename
    matching and compatibility with indexes built by older versions.
    """
    if not parse_search_query(query) or not Path(database).is_file():
        return []
    condition, params = sql_search_condition(query)
    try:
        with closing(sqlite3.connect(database, timeout=1)) as db:
            sql = ('SELECT path, name, directory, extension FROM files WHERE '
                   + condition + ' ORDER BY name_fold, path LIMIT ?')
            return [dict(path=p, name=n, directory=d, extension=e)
                    for p,n,d,e in db.execute(sql, (*params, limit))]
    except (sqlite3.Error, OSError):
        # A freshly installed launcher may not have an index yet.
        return []


def studio_managed_json(path, studio_root):
    """Consider JSON Studio-managed only if its ViewDef is resolvable."""
    if not studio_root or not Path(path).is_file():
        return False
    try:
        with open(path, encoding='utf-8-sig') as stream:
            document = json.load(stream)
        if not isinstance(document, dict):
            return False
        ref = document.get('view_def')
        if not isinstance(ref, str) or not ref.strip() or not ref.lower().endswith('.json'):
            return False
        root = Path(studio_root)
        return any(candidate.is_file() for candidate in (
            root / 'defs' / ref, root / ref, Path(path).parent / ref,
        ))
    except (OSError, ValueError, UnicodeError):
        return False


def launch_steps(file, studio_root=''):
    """Convert a search hit to existing launch actions; no shell string eval."""
    path = str(file)
    extension = Path(path).suffix.casefold()
    working_directory = str(Path(path).parent)
    if extension == '.md' and studio_root:
        # CLI deep-link is handled by NativeShell --open-md (Studio add-on).
        executable = Path(studio_root) / 'NativeShell' / '_publish' / 'FRBStudio.NativeShell.exe'
        if executable.is_file():
            return [{'launch_action_type': 'Run', 'launch_program': str(executable),
                     'launch_arguments': ['--open-md='+path],
                     'launch_working_directory': str(studio_root)}]
    if extension == '.json' and studio_managed_json(path, studio_root):
        executable = Path(studio_root) / 'NativeShell' / '_publish' / 'FRBStudio.NativeShell.exe'
        if executable.is_file():
            return [{'launch_action_type': 'Run', 'launch_program': str(executable),
                     'launch_arguments': ['--open-json='+path],
                     'launch_working_directory': str(studio_root)}]
    if extension == '.py':
        return [{'launch_action_type': 'Run', 'launch_program': 'py.exe',
                 'launch_arguments': ['-3', path], 'launch_working_directory': working_directory,
                 'launch_show_console': True}]
    if extension == '.ps1':
        return [{'launch_action_type': 'Run', 'launch_program': 'powershell.exe',
                 'launch_arguments': ['-NoProfile', '-File', path], 'launch_working_directory': working_directory,
                 'launch_show_console': True}]
    return [{'launch_action_type': 'Open', 'launch_target': path}]


# Registered plain Open actions use the same file-type launch rules as index
# results and browsed directory files. Explicit Run and browser actions are
# deliberately left alone to respect the user's authored commands.
ROUTABLE_OPEN_EXTENSIONS = frozenset(('.bat', '.py', '.ps1', '.json', '.xlsx', '.md'))


def route_registered_open_step(step, studio_root=''):
    """Route an expanded local file Open step through the shared file launcher.

    URL/shell targets, directories, missing files and browser-specific Open
    actions keep their original behavior. No data or index files are changed.
    """
    if (step.get('launch_action_type') != 'Open'
            or step.get('launch_browser') or step.get('launch_browser_profile')):
        return [step]
    target = step.get('launch_target', '')
    if not isinstance(target, str) or not target:
        return [step]
    if Path(target).suffix.casefold() not in ROUTABLE_OPEN_EXTENSIONS:
        return [step]
    try:
        if not Path(target).is_file():
            return [step]
    except (OSError, ValueError):
        return [step]
    return launch_steps(target, studio_root=studio_root)


# V0.2: per-root file-list comparison, background-safe transactional updates.
# The legacy build_index function remains available for tests/older callers;
# the live launcher uses refresh_index, which never replaces an open SQLite file.

def _index_options_digest(options):
    relevant = {key: options[key] for key in
                ('extensions', 'exclude_name_contains', 'exclude_directories',
                 'exclude_directory_globs', 'scan_error_policy', 'max_depth')}
    return hashlib.sha256(json.dumps(relevant, ensure_ascii=False,
                                    sort_keys=True).encode('utf-8')).hexdigest()


def _root_key(root):
    return _normalized_path(root)


def _root_scan(root, options, cancelled=None):
    """List matching paths once. Never open file contents or follow directory links.

    Directory enumeration errors invalidate that root's snapshot; otherwise a
    transient access failure could accidentally delete correct old entries.
    """
    if cancelled and cancelled():
        raise InterruptedError('索引更新は中断されました')
    scan_root = _windows_scan_path(root)
    # Cloud filesystem providers sometimes reject extended-length notation.
    # Keep the original path as a fallback instead of breaking a root that
    # previously worked with the ordinary Windows pathname.
    if scan_root != root and not os.path.isdir(scan_root) and os.path.isdir(root):
        scan_root = root
    if not os.path.isdir(scan_root):
        raise FileNotFoundError(f'対象フォルダーが利用できません: {root}')
    try:
        with os.scandir(scan_root) as entries:
            next(entries, None)  # fail fast on an inaccessible root
    except OSError:
        if scan_root == root:
            raise
        scan_root = root
        with os.scandir(scan_root) as entries:
            next(entries, None)
    extensions = set(options['extensions'])
    hidden = ('view_def', *(v.casefold() for v in options['exclude_name_contains'] if v))
    excluded_dirs = {v.casefold() for v in options['exclude_directories']}
    max_depth = options.get('max_depth')
    rows, excluded = [], 0
    failures, failed_dirs = [], []
    def on_error(exc):
        path = _original_scan_path(getattr(exc, 'filename', '') or root)
        failures.append(f'{path}: {exc}')
        failed_dirs.append(path)
    for parent, dirs, files in os.walk(scan_root, topdown=True, followlinks=False,
                                       onerror=on_error):
        if cancelled and cancelled():
            raise InterruptedError('索引更新は中断されました')
        if max_depth is not None and os.path.relpath(parent, scan_root).count(os.sep) + (parent != scan_root) >= max_depth:
            excluded += len(dirs)
            dirs[:] = []
        retained = []
        for dirname in dirs:
            child = os.path.join(parent, dirname)
            if (dirname.casefold() in excluded_dirs or
                    _excluded_folder(options, root, _original_scan_path(child)) or os.path.islink(child)
                    or (hasattr(os.path, 'isjunction') and os.path.isjunction(child))):
                excluded += 1
            else:
                retained.append(dirname)
        dirs[:] = retained
        for name in files:
            extension = os.path.splitext(name)[1].casefold()
            if extension not in extensions or any(token in name.casefold() for token in hidden):
                excluded += 1
                continue
            path = os.path.join(parent, name)
            if os.path.islink(path):
                excluded += 1
                continue
            rows.append((_original_scan_path(path), name, name.casefold(),
                         _original_scan_path(parent), extension, _root_key(root)))
    if failures and options.get('scan_error_policy', 'preserve_cached') == 'fail_root':
        raise OSError(f'{root}: サブフォルダーの走査に失敗: {failures[0]}（{len(failures)}件）')
    rows.sort(key=lambda row: _normalized_path(row[0]))
    return {'root': root, 'key': _root_key(root), 'rows': rows,
            'digest': _digest_rows(rows), 'count': len(rows), 'excluded': excluded,
            'failed_dirs': failed_dirs, 'warnings': failures}


def _ensure_incremental_schema(db):
    db.execute("""CREATE TABLE IF NOT EXISTS files (
        path TEXT PRIMARY KEY COLLATE NOCASE, name TEXT NOT NULL,
        name_fold TEXT NOT NULL, directory TEXT NOT NULL, extension TEXT NOT NULL)""")
    db.execute('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
    if 'root_key' not in {item[1] for item in db.execute('PRAGMA table_info(files)')}:
        db.execute("ALTER TABLE files ADD COLUMN root_key TEXT NOT NULL DEFAULT ''")
    db.execute('CREATE INDEX IF NOT EXISTS idx_file_index_root_key ON files(root_key)')
    db.execute("""CREATE TABLE IF NOT EXISTS index_roots (
        root_key TEXT PRIMARY KEY, root_path TEXT NOT NULL,
        digest TEXT NOT NULL, options_digest TEXT NOT NULL,
        checked_at TEXT NOT NULL, updated_at TEXT NOT NULL,
        count INTEGER NOT NULL, excluded INTEGER NOT NULL)""")
    db.commit()


def _write_root(db, scanned, options_digest, now):
    key = scanned['key']
    db.execute('DELETE FROM files WHERE root_key = ?', (key,))
    db.executemany("""INSERT OR REPLACE INTO files
        (path, name, name_fold, directory, extension, root_key)
        VALUES (?, ?, ?, ?, ?, ?)""", scanned['rows'])
    db.execute("""INSERT OR REPLACE INTO index_roots
        (root_key, root_path, digest, options_digest, checked_at,
         updated_at, count, excluded) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (key, scanned['root'], scanned['digest'], options_digest, now, now,
         scanned['count'], scanned['excluded']))


def _save_index_metadata(db, roots, options, warnings):
    root_info = list(db.execute('SELECT root_path, excluded FROM index_roots ORDER BY root_path'))
    count = db.execute('SELECT COUNT(*) FROM files').fetchone()[0]
    excluded = sum(item[1] for item in root_info)
    metadata = {
        'updated_at': datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds'),
        'count': count, 'excluded': excluded,
        'roots': [item[0] for item in root_info],
        'extensions': options['extensions'],
        'warnings': list(warnings)[:15], 'scan_errors': len(warnings),
        'index_version': 2,
    }
    db.executemany('INSERT OR REPLACE INTO metadata(key,value) VALUES(?,?)',
                   [(key, json.dumps(value, ensure_ascii=False)) for key, value in metadata.items()])
    return metadata


def refresh_index(database, roots, options, *, force=False, root_warnings=(),
                  cancelled=None, on_root=None):
    """Enumerate each minimal root once, compare path snapshots, update atomically.

    Unchanged root => only checked_at is updated. Changed root => one SQLite
    transaction; concurrent readers see previous complete rows until commit.
    A changed root *set* => one full transaction after every root scans OK, so
    moving a parent boundary never exposes duplicates or missing descendants.
    Existing pre-v0.2 indexes remain searchable until first full success.
    """
    roots = minimize_roots(roots)
    if not roots:
        raise ValueError('索引対象の実フォルダー展開先がありません')
    if len({_root_key(root) for root in roots}) != len(roots):
        raise ValueError('索引対象のフォルダーが重複しています')
    database = Path(database)
    database.parent.mkdir(parents=True, exist_ok=True)
    digest = _index_options_digest(options)
    with closing(sqlite3.connect(database, timeout=15)) as db:
        db.execute('PRAGMA busy_timeout=15000')
        db.execute('PRAGMA journal_mode=WAL')
        _ensure_incremental_schema(db)
        stored = {r[0]: {'digest':r[1], 'opts':r[2]}
                  for r in db.execute('SELECT root_key,digest,options_digest FROM index_roots')}
        desired = {_root_key(root) for root in roots}
        topology_changed = set(stored) != desired
        changed, unchanged, failed, warnings = [], [], [], list(root_warnings)
        completed = {}
        # Independent directory enumeration can run simultaneously, but all
        # database writes are serial on this worker connection.
        with ThreadPoolExecutor(max_workers=options['auto_update']['max_scan_workers'],
                                thread_name_prefix='FRBIndexScan') as executor:
            jobs = {executor.submit(_root_scan, root, options, cancelled): root for root in roots}
            for job in as_completed(jobs):
                root = jobs[job]
                try:
                    scanned = job.result()
                except Exception as exc:
                    failed.append(root)
                    warnings.append(f'{root}: {exc}')
                    if on_root:
                        on_root(root, 'failed')
                    continue
                if scanned.get('failed_dirs'):
                    scanned = _preserve_failed_subtrees(db, scanned)
                    warnings.extend(scanned['warnings'][:15])
                completed[scanned['key']] = scanned
                old = stored.get(scanned['key'])
                needs_update = (force or topology_changed or old is None or
                                old['digest'] != scanned['digest'] or old['opts'] != digest)
                if needs_update:
                    changed.append(root)
                else:
                    unchanged.append(root)
                if not topology_changed and not (cancelled and cancelled()):
                    now = datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')
                    with db:
                        if needs_update:
                            _write_root(db, scanned, digest, now)
                        else:
                            db.execute('UPDATE index_roots SET checked_at=? WHERE root_key=?',
                                       (now, scanned['key']))
                if on_root:
                    on_root(root, 'changed' if needs_update else 'unchanged')
                # Release the per-root listing before scanning the next root.
                if not topology_changed:
                    completed.pop(scanned['key'], None)
        if cancelled and cancelled():
            raise InterruptedError('索引更新は中断されました')
        if topology_changed and not failed:
            # Migration and root-set changes are indivisible (all roots or none).
            with db:
                db.execute('DELETE FROM files')
                db.execute('DELETE FROM index_roots')
                now = datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')
                for root in roots:
                    _write_root(db, completed[_root_key(root)], digest, now)
        if not topology_changed or not failed:
            with db:
                metadata = _save_index_metadata(db, roots, options, warnings)
        else:
            # If migration/root topology failed, preserve the old complete index.
            metadata = index_status(database) or {'count': 0, 'excluded': 0}
        return {**metadata, 'changed_roots': changed if not (topology_changed and failed) else [],
                'unchanged_roots': unchanged, 'failed_roots': failed,
                'root_set_changed': topology_changed,
                'scan_warnings': warnings,
                'applied': not (topology_changed and failed)}


def index_root_status(database):
    """Per-root update evidence for tray status; supports legacy DBs."""
    if not Path(database).is_file():
        return []
    try:
        with closing(sqlite3.connect(database, timeout=1)) as db:
            return [dict(root_path=root, checked_at=checked,
                         updated_at=updated, count=count, excluded=excluded)
                    for root, checked, updated, count, excluded in db.execute(
                        'SELECT root_path, checked_at, updated_at, count, excluded '
                        'FROM index_roots ORDER BY root_path')]
    except (sqlite3.Error, OSError):
        return []
