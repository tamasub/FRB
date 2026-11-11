"""Launch-owned Add/Delete records and trusted Studio Change Core bridge.

UI adapters resolve a target from authoritative Launch JSON; this module never
mutates a document directly and never treats physical file operations as JSON edits.
"""
from __future__ import annotations

import configparser
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlparse, unquote
import shutil
import subprocess
import tempfile
import uuid


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


def category_record(title):
    text = str(title or '').strip()
    if not text:
        raise RegistrationError('カテゴリー名を入力してください。')
    return {'title': text, 'item_kind': 'category',
            'icon_key': 'category.blue', 'enabled': True,
            'description': '', 'launch_browse_target': '', 'launch_actions': []}


def mime_sources(mime):
    """Extract Windows/Chrome/embedded-browser drag payload without network IO.

    Qt mimeData().urls() may contain local .url shortcuts or actual HTTP URLs.
    Browser links can also arrive in text/uri-list, x-moz-url or text/plain.
    """
    entries = []
    if mime is None:
        return entries
    if mime.hasUrls():
        for url in mime.urls():
            if url.isLocalFile():
                entries.append({'value': url.toLocalFile()})
            elif _valid_http(url.toString()):
                entries.append({'value': url.toString()})
    # Chromium on Windows may use OLE's UniformResourceLocatorW rather than
    # text/uri-list. Accept that standard clipboard representation as well.
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
                entries.append({'value': lines[0], 'title': lines[1] if len(lines) > 1 else ''})
                break
    if mime.hasText() and entries:
        caption = str(mime.text() or '').strip()
        if caption and len(caption) < 160 and not _valid_http(caption) and '\n' not in caption:
            for entry in entries:
                if _valid_http(entry.get('value')) and not entry.get('title'):
                    entry['title'] = caption
    if not entries and mime.hasText():
        lines = str(mime.text() or '').strip().splitlines()
        if lines and _valid_http(lines[0]):
            entries.append({'value': lines[0], 'title': lines[1] if len(lines) > 1 else ''})
    return entries


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


def prepare_delete(config_path, studio_root, page_id, item_id, *, protected=(), timeout=40):
    """Preflight cascade deletion; NO writes. Confirmation consumes its returned plan.

    A stale plan is deliberately rejected at COMMIT by the Studio Core SHA gate.
    """
    filename = Path(config_path).resolve()
    root = Path(studio_root).resolve()
    # Never trust an item identity taken from a UI projection alone.
    page_id, item_id = str(page_id or ''), str(item_id or '')
    if not item_id or (page_id, item_id) in protected:
        raise RegistrationError('Files Expの内部管理ルートは登録解除できません。')
    raw = filename.read_bytes()
    document = json.loads(raw.decode('utf-8-sig'))
    original, children = _delete_subtree(document, page_id, item_id)
    folders = sum(r.get('item_kind') in ('category', 'directory') for r in children)
    leaves = len(children) - folders
    request = {
        'schema_version': 'studio_changeset_v0_1',
        'request_id': 'launch-delete-' + uuid.uuid4().hex,
        'mode': 'dry_run', 'document_ref': DOCUMENT_REF,
        'base_sha256': hashlib.sha256(raw).hexdigest(),
        'view_def': VIEW_DEF, 'view_id': VIEW_ID,
        'operations': [{'operation': 'delete', 'section_id': SECTION_ID,
                        'targets': [{'id': item_id, 'group_id': page_id}],
                        'cascade': True}]
    }
    config = _delete_trusted_config(filename)
    preview = _invoke_delete_cli(root, config, request, 'dry_run', timeout)
    expected = len(children) + 1
    if preview.get('summary', {}).get('deleted') != expected:
        raise RegistrationError('Studio CLIの削除件数とLaunchの子孫件数が一致しません。')
    if preview.get('saved') or preview.get('base_sha256') != request['base_sha256']:
        raise RegistrationError('Studio CLI dry_runで保存またはSHA不一致を検出しました。')
    return {'filename': filename, 'root': root, 'config': config,
            'request': request, 'preview': preview, 'title': str(original.get('title') or item_id),
            'item_kind': str(original.get('item_kind') or ''),
            'page_id': page_id, 'item_id': item_id,
            'folders': folders, 'leaves': leaves, 'descendants': len(children),
            'deleted': expected, 'timeout': timeout}


def commit_delete(plan):
    """Commit EXACTLY the preflighted SHA and target, after user confirmation."""
    reply = _invoke_delete_cli(plan['root'], plan['config'], plan['request'],
                               'commit', plan['timeout'])
    if reply.get('summary', {}).get('deleted') != plan['deleted']:
        raise RegistrationError('登録解除件数が事前確認と異なります。')
    if not reply.get('saved'):
        raise RegistrationError('Studio CLIが保存完了を報告しませんでした。')
    return reply
