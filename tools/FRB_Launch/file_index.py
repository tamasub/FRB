"""Manual, persistent file-name index for FRB Launch.

The index is derived from *enabled, registered* directory items.  It never
modifies the user launch JSON. Index files live in LOCALAPPDATA and are
atomically replaced only after a complete successful root scan.
"""
from __future__ import annotations

import json
import ntpath
import os
import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from search_matching import sql_like_term

DEFAULT_OPTIONS = {
    'enabled': True,
    'extensions': ['.bat', '.py', '.ps1', '.json', '.xlsx', '.md'],
    'exclude_name_contains': ['view_def'],
    'exclude_directories': ['.venv', '.git', 'node_modules', '__pycache__', 'build', 'dist', 'System Volume Information', '$RECYCLE.BIN'],
    'search_limit': 100,
    'update_mode': 'manual',
}


def load_options(path):
    """Keep all index options in a separate, human-editable settings JSON."""
    path = Path(path)
    raw = json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else {}
    if not isinstance(raw, dict):
        raise ValueError('file_index_options.json はJSONオブジェクトにしてください')
    options = {**DEFAULT_OPTIONS, **raw}
    if options['update_mode'] != 'manual':
        raise ValueError('ファイル索引は手動更新のみ対応します')
    for key in ('extensions', 'exclude_name_contains', 'exclude_directories'):
        if not isinstance(options[key], list) or not all(isinstance(x, str) for x in options[key]):
            raise ValueError(f'{key} は文字列配列にしてください')
    extensions = {x.strip().casefold() for x in options['extensions']}
    if not extensions or any(not x.startswith('.') or len(x) < 2 or '/' in x or '\\' in x for x in extensions):
        raise ValueError('extensions には .py などの拡張子を指定してください')
    options['extensions'] = sorted(extensions)
    if not isinstance(options['enabled'], bool):
        raise ValueError('enabled はtrue/falseで指定してください')
    if type(options['search_limit']) is not int or not 1 <= options['search_limit'] <= 500:
        raise ValueError('search_limit は1～500で指定してください')
    return options


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


def registered_roots(data, expand):
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
            if not os.path.isdir(path):
                errors.append(f'登録フォルダーが存在しません: {path}')
                continue
            # Never follow a linked root beyond the registered path.
            if os.path.islink(path) or (hasattr(os.path, 'isjunction') and os.path.isjunction(path)):
                errors.append(f'リンク先フォルダーは索引対象外: {path}')
                continue
            roots.append(path)
        except (OSError, ValueError) as exc:
            errors.append(f'{row.get("title", "directory")}: {exc}')
    return minimize_roots(roots), errors


def _scan(roots, options, connection):
    extensions = set(options['extensions'])
    hidden = tuple({'view_def', *(x.casefold() for x in options['exclude_name_contains'] if x)})
    excluded_dirs = {x.casefold() for x in options['exclude_directories']}
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
            retained = []
            for dirname in dirs:
                child = os.path.join(parent, dirname)
                if dirname.casefold() in excluded_dirs or os.path.islink(child) or (
                    hasattr(os.path, 'isjunction') and os.path.isjunction(child)):
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
            return {key: json.loads(value) for key, value in db.execute('SELECT key, value FROM metadata')}
    except (sqlite3.Error, OSError, ValueError):
        return None


def search_index(database, query, limit=100):
    """Only basename matches. Never search absolute paths or internal keys."""
    words = query.casefold().split()
    if not words or not Path(database).is_file():
        return []
    clauses = []
    params = []
    for word in words:
        # Only * is a wildcard; SQL-specific wildcard chars are literals.
        clauses.append("name_fold LIKE ? ESCAPE '!'")
        params.append(sql_like_term(word))
    try:
        with closing(sqlite3.connect(database, timeout=1)) as db:
            sql = ('SELECT path, name, directory, extension FROM files WHERE '
                   + ' AND '.join(clauses) + ' ORDER BY name_fold, path LIMIT ?')
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
