"""Launch-owned Add/Delete records and trusted Studio Change Core bridge.

UI adapters resolve a target from authoritative Launch JSON; this module never
mutates a document directly and never treats physical file operations as JSON edits.
"""
from __future__ import annotations

import configparser
import hashlib
import json
import os
import ntpath
from pathlib import Path
from urllib.parse import urlparse, unquote
import shutil
import subprocess
import tempfile
import uuid
from html.parser import HTMLParser
from html import unescape


VIEW_DEF = 'launch/frb_launch_maintenance_view_def_v0_1.json'
VIEW_ID = 'items_view'
SECTION_ID = 'items'
DOCUMENT_REF = 'approved_launch_config'


class RegistrationError(ValueError):
    pass


def eligible_parent(document, page_id, parent_id):
    """Only a page root or an authored category can own new JSON entries."""
    pages = document.get('pages') or []
    if not any(isinstance(p, dict) and p.get('enabled', True)
               and p.get('page_id') == page_id for p in pages):
        raise RegistrationError('登録先のPageが存在しません。')
    if not parent_id:
        return {'page_id': page_id, 'item_id': '', 'item_kind': 'page'}
    rows = document.get('items') or []
    parent = next((row for row in rows if isinstance(row, dict)
                   and row.get('page_id') == page_id
                   and row.get('item_id') == parent_id
                   and row.get('enabled', True)), None)
    if not parent or parent.get('item_kind') != 'category':
        raise RegistrationError('登録先は設定JSONのカテゴリーフォルダーにしてください。')
    return parent


def files_exp_root_target(document, options):
    """Resolve the real Files Exp ROOT (System/Files category), not System Page.

    The visible Files Exp roots are projected from the children of this
    configured JSON category. Never silently fall back to the Page root.
    """
    options = options or {}
    page_id = str(options.get('page_id') or 'system')
    parent_id = str(options.get('files_item_id') or 'folders')
    eligible_parent(document, page_id, parent_id)
    return page_id, parent_id


def _valid_http(url):
    text = str(url or '').strip()
    parsed = urlparse(text)
    return text if (parsed.scheme.lower() in ('http', 'https') and
                    bool(parsed.netloc) and not any(c in text for c in '\r\n\x00')) else ''


def shortcut_url(path):
    """Read Chrome/Windows .url drops; never execute or move the shortcut."""
    p = Path(path)
    if p.suffix.lower() != '.url' or not p.is_file() or p.stat().st_size > 65536:
        return ''
    data = p.read_bytes()
    for encoding in ('utf-8-sig', 'utf-16', 'cp1252'):
        try:
            text = data.decode(encoding)
        except (UnicodeError, LookupError):
            continue
        parser = configparser.ConfigParser(interpolation=None)
        try:
            parser.read_string(text)
            result = _valid_http(parser.get('InternetShortcut', 'URL', fallback=''))
            if result:
                return result
        except (configparser.Error, ValueError):
            pass
    return ''


def normalize_sources(entries):
    """Entries from DnD/mime or dialogs -> ordered, typed, validated sources.

    Each entry is {'value': PATH_OR_URL, 'title': optional external link label}.
    Duplicates within ONE drag are removed; previously registered paths are NOT.
    """
    result = []
    seen = set()
    for entry in entries:
        raw = str(entry.get('value') or '').strip()
        if not raw:
            continue
        url = _valid_http(raw)
        if url:
            kind, value = 'url', url
        else:
            path = Path(raw)
            try:
                if path.is_dir():
                    kind, value = 'directory', str(path.resolve())
                elif path.is_file():
                    link = shortcut_url(path)
                    if link:
                        kind, value = 'url', link
                    else:
                        kind, value = 'file', str(path.resolve())
                else:
                    raise RegistrationError('ドロップ元が存在しません: ' + raw)
            except (OSError, ValueError) as exc:
                raise RegistrationError(str(exc)) from exc
        key = (kind, value.casefold() if kind != 'url' else value)
        if key in seen:
            continue
        seen.add(key)
        if kind == 'url':
            parsed = urlparse(value)
            label = str(entry.get('title') or '').strip()
            if not label and Path(raw).suffix.lower() == '.url':
                label = Path(raw).stem
            if not label or _valid_http(label):
                label = unquote(parsed.path.rstrip('/').split('/')[-1]) or parsed.netloc
            label = label[:160]
        else:
            label = Path(value).name or value
        result.append({'kind': kind, 'value': value, 'title': label})
    if not result:
        raise RegistrationError('登録できるファイル・フォルダー・URLがありません。')
    if len(result) > 100:
        raise RegistrationError('一度に登録できる項目は100件までです。')
    return result


def records_for_sources(sources):
    """Keep exactly the existing Launch item_kind/Action schema."""
    records = []
    for src in sources:
        kind, value, title = src['kind'], src['value'], src['title']
        if kind not in ('file', 'directory', 'url'):
            raise RegistrationError('未対応の登録種類: ' + str(kind))
        is_dir = kind == 'directory'
        records.append({
            'title': title,
            'description': value,
            'item_kind': 'directory' if is_dir else 'command',
            'icon_key': 'folder.yellow' if is_dir else 'file' if kind == 'file' else 'globe',
            'enabled': True,
            'launch_browse_target': value if is_dir else '',
            'launch_actions': [{
                'launch_action_type': 'Open', 'launch_target': value,
                'launch_program': '', 'launch_arguments': [],
                'launch_working_directory': '', 'launch_wait_for_exit': False,
                'launch_timeout_ms': 30000, 'launch_failure_policy': 'stop',
                'launch_result_name': '', 'launch_result_format': 'none'
            }],
        })
    return records



def url_registration_record(title, url):
    """Validate the authored two-field URL form, preserving existing Open schema."""
    label = str(title or '').strip()
    if not label:
        raise RegistrationError('タイトルを入力してください。')
    if len(label) > 160:
        raise RegistrationError('タイトルは160文字以内で入力してください。')
    address = _valid_http(url)
    if not address:
        raise RegistrationError('http:// または https:// から始まる有効なURLを入力してください。')
    return records_for_sources([{'kind': 'url', 'value': address, 'title': label}])[0]


def category_record(title):
    text = str(title or '').strip()
    if not text:
        raise RegistrationError('カテゴリー名を入力してください。')
    return {'title': text, 'item_kind': 'category',
            'icon_key': 'category.blue', 'enabled': True,
            'description': '', 'launch_browse_target': '', 'launch_actions': []}


def _drop_uri_value(text):
    """Convert a file URI or HTTP URL to an untrusted source path/URL.

    Windows Explorer/OneDrive may give text/uri-list without QUrl.isLocalFile.
    Existence and permission checks are deliberately deferred to normalize_sources.
    """
    candidate = str(text or '').strip().strip('\x00')
    if _valid_http(candidate):
        return candidate
    parsed = urlparse(candidate)
    if parsed.scheme.lower() != 'file':
        return ''
    # file:///C:/folder/name%20with%20space.xlsx or file://server/share/x.
    local = unquote(parsed.path)
    if len(local) >= 3 and local[0] == '/' and local[2] == ':':
        local = local[1:]
    if parsed.netloc and parsed.netloc.lower() != 'localhost':
        local = '//'+parsed.netloc + local
    return local if (ntpath.isabs(local) or os.path.isabs(local)) else ''


def _drop_windows_paths(blob, encoding):
    """Read standard OLE FileNameW/FileName null-separated absolute paths."""
    try:
        paths = bytes(blob).decode(encoding).split('\x00')
    except (UnicodeError, LookupError):
        return []
    return [p for p in paths if p and (ntpath.isabs(p) or os.path.isabs(p))]


class _ChromeLinkParser(HTMLParser):
    """Only extract a genuine HTTP(S) href from a Chromium HTML drag."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.href = ''
        self.label = ''
        self._anchor_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'a' and not self.href:
            href = dict(attrs).get('href', '')
            if _valid_http(href):
                self.href = href
                self._anchor_depth = 1

    def handle_data(self, data):
        if self._anchor_depth and len(self.label) < 160:
            self.label += data

    def handle_endtag(self, tag):
        if tag.lower() == 'a':
            self._anchor_depth = 0


def chrome_html_link(blob):
    """Fallback for Chrome drags that expose text/html but no URI list."""
    try:
        raw = bytes(blob).decode('utf-8-sig', errors='replace')
        parser = _ChromeLinkParser()
        parser.feed(raw)
        return {'value': unescape(parser.href),
                'title': parser.label.strip()[:160]} if parser.href else None
    except (TypeError, ValueError):
        return None


def _looks_like_address_caption(caption, address):
    """Detect Chrome text/plain that is just the URL without its scheme.

    Omnibox drags frequently provide "qiita.com/user/items/…" as plain text.
    That is not a page title; prefer any actual HTML or moz-url title.
    """
    address = _valid_http(address)
    if not address:
        return False
    candidate = str(caption or '').strip().rstrip('/').casefold()
    full = address.rstrip('/').casefold()
    no_scheme = full.split('://', 1)[-1]
    return bool(candidate and candidate in (full, no_scheme, 'www.' + no_scheme))


def mime_sources(mime):
    """Decode Explorer/OneDrive/Chromium drops, without changing real files.

    QUrl conversion is not sufficient for every Windows native Explorer drag.
    FileNameW/FileName or a raw uri-list may be present instead. Only absolute
    filenames, file: URIs and validated http(s) URLs are eligible; the Add
    request still checks existence, target category and Studio constraints.
    """
    entries = []
    if mime is None:
        return entries
    if mime.hasUrls():
        for url in mime.urls():
            if url.isLocalFile():
                path = str(url.toLocalFile() or '') or _drop_uri_value(url.toString())
                if path:
                    entries.append({'value': path})
            else:
                candidate = _drop_uri_value(url.toString())
                if candidate:
                    entries.append({'value': candidate})
    # Prefer Qt's canonical CF_HDROP/local-URL paths.  Windows Explorer may
    # expose the SAME files again as OLE FileNameW/FileName, sometimes as an
    # 8.3 alias that does not resolve (notably under OneDrive).  Do not append
    # those aliases when a higher-priority representation is available.
    # Some drag providers expose a raw URI list while QMimeData.urls() is
    # empty; use that before native filename formats for the same reason.
    if not entries and mime.hasFormat('text/uri-list'):
        try:
            lines = bytes(mime.data('text/uri-list')).decode('utf-8-sig').splitlines()
        except UnicodeError:
            lines = []
        for line in lines:
            if not line.startswith('#'):
                candidate = _drop_uri_value(line)
                if candidate:
                    entries.append({'value': candidate})

    if not entries:
        # Unicode FileNameW wins over ANSI FileName.  Never merge both: they
        # are alternative representations of the same dropped files, not
        # separate files.  ;index=N allows multiple native file descriptors.
        native_formats = (mime.formats() if callable(getattr(mime, 'formats', None))
                          else ())
        for base, encoding in (
            ('application/x-qt-windows-mime;value="FileNameW"', 'utf-16-le'),
            ('application/x-qt-windows-mime;value="FileName"', 'mbcs' if os.name == 'nt' else 'cp1252'),
        ):
            formats = [fmt for fmt in native_formats if
                       fmt == base or fmt.startswith(base + ';index=')]
            if not formats and mime.hasFormat(base):
                formats = [base]
            fallback = []
            for fmt in formats:
                fallback.extend({'value': path} for path in
                                _drop_windows_paths(mime.data(fmt), encoding))
            if fallback:
                entries.extend(fallback)
                break
    # Chromium sometimes uses URL-only native clipboard formats.
    for windows_format, encoding in (
        ('application/x-qt-windows-mime;value="UniformResourceLocatorW"', 'utf-16-le'),
        ('application/x-qt-windows-mime;value="UniformResourceLocator"', 'cp1252')):
        if mime.hasFormat(windows_format):
            blob = bytes(mime.data(windows_format))
            try:
                address = blob.decode(encoding).split('\x00')[0].strip()
                if _valid_http(address):
                    entries.append({'value': address})
            except UnicodeError:
                pass
    if mime.hasFormat('text/x-moz-url'):
        blob = bytes(mime.data('text/x-moz-url'))
        for encoding in ('utf-16-le', 'utf-8'):
            try:
                lines = blob.decode(encoding).replace('\x00', '').splitlines()
            except UnicodeError:
                continue
            if lines and _valid_http(lines[0]):
                # A Chromium drag may supply the same URL through Qt urls()
                # *before* the richer URL+title format. Preserve that title
                # during the format merge below, never create a second item.
                if not entries or any(e['value'] == lines[0] for e in entries):
                    entries.append({'value': lines[0],
                                    'title': lines[1].strip() if len(lines) > 1 else ''})
                break
    if mime.hasText() and entries:
        caption = str(mime.text() or '').strip()
        if caption and len(caption) < 160 and not _valid_http(caption) and '\n' not in caption:
            for entry in entries:
                if (_valid_http(entry.get('value')) and not entry.get('title')
                        and not _looks_like_address_caption(caption, entry['value'])):
                    entry['title'] = caption
    if not entries and mime.hasText():
        lines = str(mime.text() or '').strip().splitlines()
        if lines:
            candidate = _drop_uri_value(lines[0])
            if not candidate and (ntpath.isabs(lines[0]) or os.path.isabs(lines[0])):
                candidate = lines[0]
            if candidate:
                entries.append({'value': candidate,
                                'title': lines[1] if len(lines) > 1 and _valid_http(candidate) else ''})
    # Chrome's address-bar drag often has BOTH a URI list (address only) and
    # HTML Format (address + actual page title). The original fallback only
    # examined HTML when entries was empty, throwing away the useful title.
    # Windows can expose CF_HTML under its native Qt MIME name as well.
    for fmt in ('text/html', 'application/x-qt-windows-mime;value="HTML Format"'):
        if not mime.hasFormat(fmt):
            continue
        html_link = chrome_html_link(mime.data(fmt))
        if html_link is None:
            continue
        if not entries or any(e['value'] == html_link['value'] for e in entries):
            entries.append(html_link)
            # A single drag should not import unrelated <a> links in page HTML.
            break

    # Chrome also advertises the dragged bookmark as a virtual Windows .url
    # file. Its FileGroupDescriptorW filename is often the page TITLE even
    # when the visible text/plain contains only the address. Reuse the Shell
    # descriptor reader, but only for one .url and an already validated URL.
    if any(_valid_http(e['value']) for e in entries) and callable(getattr(mime, 'formats', None)):
        formats = mime.formats()
        if any('FileGroupDescriptor' in fmt for fmt in formats):
            from virtual_clipboard_paste import virtual_clipboard_names
            try:
                names = virtual_clipboard_names(mime)
            except (ValueError, UnicodeError):
                names = None
            if names and len(names) == 1 and names[0].lower().endswith('.url'):
                link_title = names[0][:-4].strip()
                if link_title and len(link_title) <= 160:
                    for entry in entries:
                        if _valid_http(entry['value']):
                            entries.append({'value': entry['value'], 'title': link_title})
                            break

    # Merge alternate MIME representations OF THE SAME URL. The first source
    # wins for ordering, but the first *nonempty title* wins for its display
    # name. Previously URL-only Qt urls() shadowed Chrome's HTML/moz title.
    deduped = []
    seen = {}
    for entry in entries:
        key = entry['value'].casefold()
        prior = seen.get(key)
        if prior is None:
            prior = dict(entry)
            deduped.append(prior)
            seen[key] = prior
        elif _valid_http(entry['value']):
            title = str(entry.get('title') or '').strip()
            if (title and not _valid_http(title)
                    and not _looks_like_address_caption(title, entry['value'])
                    and (not prior.get('title') or _looks_like_address_caption(
                        prior['title'], prior['value']))):
                prior['title'] = title
    return deduped


def studio_core_root(launch_home, configured_root=''):
    """Find actual Studio source, never fabricate a CLI nor silently direct-write."""
    home = Path(launch_home).resolve()
    candidates = [configured_root, home / 'Studio', home.parent / 'FRBStudio_App',
                  home.parent / 'Studio', home.parent.parent / 'FRBStudio_App']
    for candidate in candidates:
        if not candidate:
            continue
        root = Path(candidate)
        if ((root / 'tools/change_core/cli.mjs').is_file() and
                (root / 'defs' / VIEW_DEF).is_file()):
            return root.resolve()
    raise RegistrationError('Studio Change Coreが見つかりません。Studioの配置先を確認してください。')


def _node_binary(root):
    override = os.environ.get('FRB_LAUNCH_NODE', '').strip()
    candidates = [override, root / 'portable/node.exe', root / 'node.exe',
                  root / 'tools/change_core/portable/node.exe', shutil.which('node')]
    for candidate in candidates:
        if candidate and (Path(candidate).is_file() or
                          (not Path(candidate).is_absolute() and shutil.which(str(candidate)))):
            return str(candidate)
    raise RegistrationError('Node.jsの実行ファイルが見つかりません。Studio CLIのNode配布またはPATHを確認してください。')


def commit_add(config_path, studio_root, page_id, parent_id, records, *, timeout=40):
    """One SHA-based Add ChangeSet; PREVIEW then COMMIT, no direct JSON writes."""
    filename = Path(config_path).resolve()
    root = Path(studio_root).resolve()
    node = _node_binary(root)
    if not isinstance(records, list) or not records:
        raise RegistrationError('新規登録レコードがありません。')
    raw = filename.read_bytes()
    document = json.loads(raw.decode('utf-8-sig'))
    eligible_parent(document, page_id, parent_id)
    baseline = hashlib.sha256(raw).hexdigest()
    config = {'schema_version': 'studio_change_core_config_v0_1',
              'documents': {DOCUMENT_REF: {
                  'path': str(filename), 'view_def': VIEW_DEF,
                  'view_id': VIEW_ID, 'section_ids': [SECTION_ID]}}}
    request = {
        'schema_version': 'studio_changeset_v0_1',
        'request_id': 'launch-add-' + uuid.uuid4().hex,
        'mode': 'dry_run', 'document_ref': DOCUMENT_REF,
        'base_sha256': baseline, 'view_def': VIEW_DEF, 'view_id': VIEW_ID,
        'operations': [{'operation': 'add', 'section_id': SECTION_ID,
                        'placement': {'group_id': page_id, 'parent_id': parent_id,
                                      'position': 'end'}, 'records': records}]
    }
    with tempfile.TemporaryDirectory(prefix='frb_launch_changeset_') as directory:
        trusted_path = Path(directory) / 'trusted.json'
        trusted_path.write_text(json.dumps(config, ensure_ascii=False), encoding='utf-8')
        def run(mode):
            request['mode'] = mode
            try:
                completed = subprocess.run(
                    [node, str(root / 'tools/change_core/cli.mjs'), '--config', str(trusted_path)],
                    input=json.dumps(request, ensure_ascii=False), text=True, encoding='utf-8',
                    capture_output=True, timeout=timeout, check=False)
                reply = json.loads(completed.stdout)
            except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
                raise RegistrationError('Studio CLIの起動または応答に失敗: ' + str(exc)) from exc
            expected_status = 'PREVIEW' if mode == 'dry_run' else 'COMMITTED'
            if completed.returncode != 0 or reply.get('status') != expected_status:
                errors = reply.get('errors') or []
                detail = '; '.join(f"{e.get('code')}: {e.get('message')}" for e in errors)
                raise RegistrationError(detail or f'Studio CLI: {reply.get("status")}')
            if reply.get('unexpected_diff') or reply.get('summary', {}).get('added') != len(records):
                raise RegistrationError('Studio CLIの差分検証が一致しません。登録を中止しました。')
            return reply
        run('dry_run')
        result = run('commit')
    return result


# studio_work_0269 / cascade Delete: only the CLI mutates the JSON document.
def _delete_subtree(document, page_id, item_id):
    """Return selected item and JSON descendants (not physical directory children)."""
    rows = document.get('items')
    if not isinstance(rows, list):
        raise RegistrationError('設定JSONのitems配列が見つかりません。')
    matches = [row for row in rows if isinstance(row, dict)
               and row.get('page_id') == page_id and row.get('item_id') == item_id]
    if len(matches) != 1 or not item_id:
        raise RegistrationError('登録解除対象が見つからないか、一意に決まりません。')
    # Both the configuration and Studio Tree must identify the same subtree.
    targets = {(page_id, item_id)}
    changed = True
    while changed:
        changed = False
        for row in rows:
            if not isinstance(row, dict):
                continue
            key = (row.get('page_id'), row.get('item_id'))
            parent = (row.get('page_id'), row.get('parent_item_id'))
            if parent in targets and key not in targets:
                targets.add(key)
                changed = True
    selected = [row for row in rows if isinstance(row, dict)
                and (row.get('page_id'), row.get('item_id')) in targets]
    if len(selected) != len(targets):
        raise RegistrationError('設定JSONの登録IDに重複があります。')
    return matches[0], [r for r in selected if r is not matches[0]]


def _delete_trusted_config(filename):
    return {'schema_version': 'studio_change_core_config_v0_1',
            'documents': {DOCUMENT_REF: {
                'path': str(filename), 'view_def': VIEW_DEF,
                'view_id': VIEW_ID, 'section_ids': [SECTION_ID]}}}


def _invoke_delete_cli(root, trusted_config, request, mode, timeout):
    node = _node_binary(root)
    payload = dict(request, mode=mode)
    with tempfile.TemporaryDirectory(prefix='frb_launch_delete_') as directory:
        config_file = Path(directory) / 'trusted.json'
        config_file.write_text(json.dumps(trusted_config, ensure_ascii=False), encoding='utf-8')
        try:
            completed = subprocess.run(
                [node, str(root / 'tools/change_core/cli.mjs'), '--config', str(config_file)],
                input=json.dumps(payload, ensure_ascii=False), text=True, encoding='utf-8',
                capture_output=True, timeout=timeout, check=False)
            reply = json.loads(completed.stdout)
        except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
            raise RegistrationError('Studio CLIの削除処理に失敗: ' + str(exc)) from exc
    expected = 'PREVIEW' if mode == 'dry_run' else 'COMMITTED'
    if completed.returncode != 0 or reply.get('status') != expected:
        errors = reply.get('errors') or []
        message = '; '.join(f"{e.get('code')}: {e.get('message')}" for e in errors)
        raise RegistrationError(message or f"Studio CLI: {reply.get('status')}")
    if reply.get('unexpected_diff') or reply.get('expected_diff') != reply.get('actual_diff'):
        raise RegistrationError('Studio CLIのExpected/Actual Diffが一致しません。')
    return reply


def prepare_delete_many(config_path, studio_root, targets, *, protected=(), timeout=40):
    """One all-or-nothing Studio CLI Delete for several authored JSON targets.

    Overlapping parent/child selections are counted only once. Physical
    filesystem descendants are never inspected, counted, or deleted.
    """
    filename = Path(config_path).resolve()
    root = Path(studio_root).resolve()
    identities = [(str(pg or ''), str(iid or '')) for pg, iid in targets]
    if not identities or len(identities) > 100 or len(set(identities)) != len(identities):
        raise RegistrationError('登録解除対象が不正です。')
    guarded = set(protected)
    if any(not iid or (pg, iid) in guarded for pg, iid in identities):
        raise RegistrationError('Files Expの内部管理ルートは登録解除できません。')
    raw = filename.read_bytes()
    document = json.loads(raw.decode('utf-8-sig'))
    rows = document.get('items')
    if not isinstance(rows, list):
        raise RegistrationError('設定JSONのitems配列が見つかりません。')
    roots = []
    descendants = {}
    to_remove = {}
    for page_id, item_id in identities:
        original, children = _delete_subtree(document, page_id, item_id)
        roots.append(original)
        to_remove[(page_id, item_id)] = original
        for row in children:
            key = (row.get('page_id'), row.get('item_id'))
            descendants[key] = row
            to_remove[key] = row
    if any(key in guarded for key in to_remove):
        raise RegistrationError('削除対象の配下にFiles Exp内部管理ルートがあります。')
    child_only = {key: row for key, row in descendants.items() if key not in set(identities)}
    folders = sum(row.get('item_kind') in ('category', 'directory')
                  for row in child_only.values())
    leaves = len(child_only) - folders
    expected = len(to_remove)
    request = {
        'schema_version': 'studio_changeset_v0_1',
        'request_id': 'launch-delete-' + uuid.uuid4().hex,
        'mode': 'dry_run', 'document_ref': DOCUMENT_REF,
        'base_sha256': hashlib.sha256(raw).hexdigest(),
        'view_def': VIEW_DEF, 'view_id': VIEW_ID,
        'operations': [{'operation': 'delete', 'section_id': SECTION_ID,
                        'targets': [{'id': iid, 'group_id': pg} for pg, iid in identities],
                        'cascade': True}]
    }
    config = _delete_trusted_config(filename)
    preview = _invoke_delete_cli(root, config, request, 'dry_run', timeout)
    if preview.get('summary', {}).get('deleted') != expected:
        raise RegistrationError('Studio CLIの削除件数とLaunchの登録件数が一致しません。')
    if preview.get('saved') or preview.get('base_sha256') != request['base_sha256']:
        raise RegistrationError('Studio CLI dry_runで保存またはSHA不一致を検出しました。')
    first = roots[0]
    return {'filename': filename, 'root': root, 'config': config,
            'request': request, 'preview': preview,
            'title': str(first.get('title') or identities[0][1]),
            'titles': [str(r.get('title') or r.get('item_id')) for r in roots],
            'item_kind': str(first.get('item_kind') or ''),
            'page_id': identities[0][0], 'item_id': identities[0][1],
            'selected_count': len(identities), 'folders': folders, 'leaves': leaves,
            'descendants': len(child_only), 'deleted': expected, 'timeout': timeout}


def prepare_delete(config_path, studio_root, page_id, item_id, *, protected=(), timeout=40):
    """Backward-compatible one-item entrypoint, using the same atomic batch."""
    return prepare_delete_many(config_path, studio_root, [(page_id, item_id)],
                               protected=protected, timeout=timeout)

def commit_delete(plan):
    """Commit EXACTLY the preflighted SHA and target, after user confirmation."""
    reply = _invoke_delete_cli(plan['root'], plan['config'], plan['request'],
                               'commit', plan['timeout'])
    if reply.get('summary', {}).get('deleted') != plan['deleted']:
        raise RegistrationError('登録解除件数が事前確認と異なります。')
    if not reply.get('saved'):
        raise RegistrationError('Studio CLIが保存完了を報告しませんでした。')
    return reply


# studio_work_0269 / generic Update bridge for simple Launch field edits.
def read_item_for_edit(config_path, page_id, item_id):
    """Load the authoritative persisted record and base SHA before UI editing."""
    filename = Path(config_path).resolve()
    raw = filename.read_bytes()
    document = json.loads(raw.decode('utf-8-sig'))
    matches = [row for row in document.get('items', []) if isinstance(row, dict)
               and row.get('page_id') == page_id and row.get('item_id') == item_id]
    if len(matches) != 1:
        raise RegistrationError('編集対象が見つからないか、一意に決まりません。')
    return dict(matches[0]), hashlib.sha256(raw).hexdigest()


def prepare_update(config_path, studio_root, page_id, item_id, changes, *,
                   base_sha256, protected=(), timeout=40):
    """Preview general Update with a frozen pre-dialog SHA. No direct writes."""
    filename = Path(config_path).resolve()
    root = Path(studio_root).resolve()
    if (page_id, item_id) in protected:
        raise RegistrationError('Files Expの内部管理ルートは編集できません。')
    raw = filename.read_bytes()
    if hashlib.sha256(raw).hexdigest() != base_sha256:
        raise RegistrationError('CONFLICT: 編集中に設定JSONが変更されました。')
    document = json.loads(raw.decode('utf-8-sig'))
    originals = [row for row in document.get('items', []) if isinstance(row, dict)
                 and row.get('page_id') == page_id and row.get('item_id') == item_id]
    if len(originals) != 1:
        raise RegistrationError('編集対象が見つからないか、一意に決まりません。')
    if not isinstance(changes, list) or not changes:
        raise RegistrationError('変更項目がありません。')
    request = {
        'schema_version': 'studio_changeset_v0_1',
        'request_id': 'launch-update-' + uuid.uuid4().hex,
        'mode': 'dry_run', 'document_ref': DOCUMENT_REF,
        'base_sha256': base_sha256, 'view_def': VIEW_DEF, 'view_id': VIEW_ID,
        'operations': [{'operation': 'update', 'section_id': SECTION_ID,
                        'targets': [{'id': item_id, 'group_id': page_id,
                                     'changes': changes}]}]
    }
    config = _delete_trusted_config(filename)
    preview = _invoke_delete_cli(root, config, request, 'dry_run', timeout)
    if (preview.get('saved') or preview.get('base_sha256') != base_sha256
            or preview.get('summary', {}).get('changed_existing') != 1):
        raise RegistrationError('Studio CLIのUpdate事前検証に失敗しました。')
    return {'root': root, 'config': config, 'request': request,
            'preview': preview, 'timeout': timeout, 'item_id': item_id}


def commit_update(plan):
    """Commit exactly the previewed Update; races are blocked by Studio SHA."""
    reply = _invoke_delete_cli(plan['root'], plan['config'], plan['request'],
                               'commit', plan['timeout'])
    if reply.get('summary', {}).get('changed_existing') != 1 or not reply.get('saved'):
        raise RegistrationError('Studio CLIのUpdate保存結果が不正です。')
    return reply


# studio_work_0269 / Move: authoritative parent/order, not filesystem paths.
def prepare_move(config_path, studio_root, page_id, item_id, placement, *,
                 protected=(), timeout=40):
    """Preview one reparent/reorder operation through Studio's shared TreeModel.

    placement: {parent_id, group_id, position: end/before/after, anchor_id?}.
    Never does a filesystem move, rename, or traversal.
    """
    filename, root = Path(config_path).resolve(), Path(studio_root).resolve()
    source = (str(page_id or ''), str(item_id or ''))
    guarded = set(protected)
    if not source[1] or source in guarded or not isinstance(placement, dict):
        raise RegistrationError('移動対象が不正、または内部管理ルートです。')
    raw = filename.read_bytes()
    document = json.loads(raw.decode('utf-8-sig'))
    rows = document.get('items') or []
    found = [r for r in rows if isinstance(r, dict)
             and (r.get('page_id'), r.get('item_id')) == source]
    if len(found) != 1 or not found[0].get('enabled', True):
        raise RegistrationError('移動元が設定JSONに見つかりません。')
    parent_id = str(placement.get('parent_id') or '')
    destination_page = str(placement.get('group_id') or '')
    position = str(placement.get('position') or 'end')
    anchor_id = str(placement.get('anchor_id') or '')
    if not destination_page or position not in ('end', 'before', 'after'):
        raise RegistrationError('移動先が不正です。')
    if not any(p.get('page_id') == destination_page and p.get('enabled', True)
               for p in document.get('pages', [])):
        raise RegistrationError('移動先Pageが存在しません。')
    if parent_id:
        eligible_parent(document, destination_page, parent_id)
    siblings = sorted((r for r in rows if isinstance(r, dict) and
                       r.get('page_id') == destination_page and
                       (r.get('parent_item_id') or '') == parent_id),
                      key=lambda r: (float(r.get('sort_order') or 0), rows.index(r)))
    if position != 'end' and not any(r.get('item_id') == anchor_id for r in siblings):
        raise RegistrationError('移動先の基準アイテムが見つかりません。')
    # The caller may drop onto the current position; do not cause needless
    # renumbering or write the same document again.
    current = found[0]
    if ((current.get('page_id'), current.get('parent_item_id') or '') ==
            (destination_page, parent_id)):
        ordered = [str(r.get('item_id')) for r in siblings]
        before = ordered[:]
        before.remove(item_id)
        if position == 'end':
            before.append(item_id)
        else:
            before.insert(before.index(anchor_id) + (position == 'after'), item_id)
        if before == ordered:
            return None
    request = {
        'schema_version': 'studio_changeset_v0_1',
        'request_id': 'launch-move-' + uuid.uuid4().hex,
        'mode': 'dry_run', 'document_ref': DOCUMENT_REF,
        'base_sha256': hashlib.sha256(raw).hexdigest(),
        'view_def': VIEW_DEF, 'view_id': VIEW_ID,
        'operations': [{'operation': 'move', 'section_id': SECTION_ID,
                        'targets': [{'id': item_id, 'group_id': page_id}],
                        'placement': {'group_id': destination_page,
                                      'parent_id': parent_id, 'position': position,
                                      **({'anchor_id': anchor_id} if position != 'end' else {})}}]
    }
    config = _delete_trusted_config(filename)
    preview = _invoke_delete_cli(root, config, request, 'dry_run', timeout)
    if (preview.get('saved') or preview.get('base_sha256') != request['base_sha256']
            or preview.get('summary', {}).get('moved') != 1):
        raise RegistrationError('Studio CLIのMove事前検証に失敗しました。')
    return {'root': root, 'config': config, 'request': request,
            'preview': preview, 'timeout': timeout, 'item_id': item_id}


def commit_move(plan):
    """No confirmation dialog; SHA protects against a concurrent Studio edit."""
    reply = _invoke_delete_cli(plan['root'], plan['config'], plan['request'],
                               'commit', plan['timeout'])
    if reply.get('summary', {}).get('moved') != 1 or not reply.get('saved'):
        raise RegistrationError('Studio CLIのMove保存結果が不正です。')
    return reply
