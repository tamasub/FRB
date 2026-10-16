"""Read Chrome/Edge bookmarks without modifying browser-owned files.

The catalog is ephemeral: it is attached to the in-memory launcher data,
not written back to the FRB Launch configuration JSON.
"""
import copy
import hashlib
import json
import os
from datetime import datetime
from uuid import uuid4
from html.parser import HTMLParser
from pathlib import Path

BROWSERS = {
    'chrome': ('Google', 'Chrome'),
    'edge': ('Microsoft', 'Edge'),
}
BOOKMARK_FILE_NAMES = ('Bookmarks', 'AccountBookmarks')
ROOT_ID = '__browser_bookmarks_root'
BOOTSTRAP_FIELD = 'bookmark_category_initialized'
ROOT_NAMES = {
    'bookmark_bar': 'ブックマーク バー',
    'other': 'その他のブックマーク',
    'synced': 'モバイルのブックマーク',
}


def user_data_directory(browser, localappdata=None):
    """Return the Chromium User Data directory (Windows)."""
    if browser not in BROWSERS:
        raise ValueError('ブラウザはChromeまたはEdgeを選択してください')
    base = localappdata if localappdata is not None else os.getenv('LOCALAPPDATA', '')
    if not base:
        return None
    return Path(base).joinpath(*BROWSERS[browser], 'User Data')


def bookmark_files(browser, localappdata=None, manual_file=None):
    """Return every relevant local/account bookmarks JSON file for each profile.

    Signed-in modern Chrome profiles can save all bookmarks in AccountBookmarks,
    without creating the historical Bookmarks file.  Read both when they exist.
    """
    if manual_file:
        path = Path(manual_file).expanduser()
        return [path] if path.is_file() else []
    root = user_data_directory(browser, localappdata)
    if not root or not root.is_dir():
        return []
    files = []
    for folder in root.iterdir():
        if folder.is_dir():
            for name in BOOKMARK_FILE_NAMES:
                path = folder / name
                if path.is_file():
                    files.append(path)
    return sorted(files, key=lambda p: (
        p.parent.name != 'Default', p.parent.name.casefold(),
        BOOKMARK_FILE_NAMES.index(p.name)))


def signature(browser, localappdata=None, manual_file=None):
    result = []
    for p in bookmark_files(browser, localappdata, manual_file):
        try:
            stat = p.stat()
            result.append((str(p), stat.st_mtime_ns, stat.st_size))
        except OSError:
            continue
    return tuple(result)


def read(browser, localappdata=None, manual_file=None):
    """Return (profiles, errors), combining local and account trees per profile.

    Combining the two sources into one profile is important: URLs must open in
    the actual Chrome profile (e.g. Default), not a synthetic Account profile.
    """
    profiles = []
    errors = []
    combined = {}
    for p in bookmark_files(browser, localappdata, manual_file):
        try:
            if manual_file and p.suffix.casefold() in ('.html', '.htm'):
                roots = _html_bookmark_roots(p.read_text(encoding='utf-8-sig'))
            else:
                doc = json.loads(p.read_text(encoding='utf-8-sig'))
                if not isinstance(doc.get('roots'), dict):
                    raise ValueError('rootsがありません')
                roots = []
                for key, label in ROOT_NAMES.items():
                    node = doc['roots'].get(key)
                    if isinstance(node, dict) and isinstance(node.get('children'), list):
                        roots.append({'name': label, 'children': node['children']})
            directory = p.parent.name if not manual_file else '指定ファイル'
            if directory not in combined:
                profile = {'directory': directory,
                           'browser_profile': p.parent.name if not manual_file else '',
                           'roots': [], '_bookmark_sources': []}
                combined[directory] = profile
                profiles.append(profile)
            profile = combined[directory]
            profile['_bookmark_sources'].append(p.name)
            # If both sources exist, clearly distinguish account and local
            # branches, avoiding duplicated permanent folder headings.
            # The inner bookmark hierarchy is never flattened or modified.
            if not manual_file and p.name == 'AccountBookmarks':
                for group in roots:
                    profile['roots'].append({'name': 'アカウント: ' + group['name'],
                                             'children': group['children']})
            elif not manual_file and p.name == 'Bookmarks':
                for group in roots:
                    profile['roots'].append({'name': 'ローカル: ' + group['name'],
                                             'children': group['children']})
            else:
                profile['roots'].extend(roots)
        except (OSError, ValueError, TypeError, UnicodeError, AttributeError) as ex:
            errors.append(f'{p.parent.name}/{p.name}: {ex}')
    # With only one type of source, retain the familiar 'ブックマーク バー'
    # instead of adding a needless account/local prefix.
    if not manual_file:
        for profile in profiles:
            if len(profile['_bookmark_sources']) == 1:
                for group in profile['roots']:
                    group['name'] = group['name'].split(': ', 1)[-1]
    return profiles, errors


class _ExportedBookmarkHTML(HTMLParser):
    """Read Chrome/Edge Netscape-format HTML exports, preserving DL folders."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.roots = []
        self.parents = [self.roots]
        self.dl_pushes = []
        self.current_tag = None
        self.label = []
        self.url = ''
        self.pending_folder = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == 'h3':
            self.current_tag = 'h3'; self.label = []
        elif tag == 'a':
            self.current_tag = 'a'; self.label = []
            self.url = dict(attrs).get('href', '') or ''
        elif tag == 'dl':
            if self.pending_folder is not None:
                self.parents.append(self.pending_folder['children'])
                self.pending_folder = None
                self.dl_pushes.append(True)
            else:
                self.dl_pushes.append(False)
        elif tag == 'dt' and self.pending_folder is not None:
            self.pending_folder = None

    def handle_data(self, data):
        if self.current_tag:
            self.label.append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == 'h3' and self.current_tag == 'h3':
            folder = {'type': 'folder', 'name': ''.join(self.label).strip(), 'children': []}
            self.parents[-1].append(folder)
            self.pending_folder = folder
            self.current_tag = None
        elif tag == 'a' and self.current_tag == 'a':
            url = self.url.strip()
            if url.lower().startswith(('http://', 'https://')):
                self.parents[-1].append({'type': 'url', 'name': ''.join(self.label).strip(), 'url': url})
            self.current_tag = None
        elif tag == 'dl' and self.dl_pushes:
            if self.dl_pushes.pop():
                self.parents.pop()


def _html_bookmark_roots(text):
    parser = _ExportedBookmarkHTML()
    parser.feed(text)
    parser.close()
    if not parser.roots:
        raise ValueError('HTMLからブックマークを取得できません')
    return [{'name': 'インポートしたブックマーク', 'children': parser.roots}]


def _id(*values):
    return '__bookmark_' + hashlib.sha256('\0'.join(str(v) for v in values).encode('utf-8')).hexdigest()[:24]


def has_category(data):
    """Whether the editable config defines a bookmark category."""
    return any(row.get('launch_source') == 'browser_bookmarks' and
               row.get('item_kind') == 'category'
               for row in data.get('items', []))


def ensure_category_file(config_path):
    """One-time migration for older configs; never recreate a user-deleted category.

    Once BOOTSTRAP_FIELD is true, the user owns the editable root category in
    Studio.  Updates to the browser's bookmark files never rewrite this JSON.
    """
    path = Path(config_path)
    import json
    from core import validate
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    validate(data)
    if data.get(BOOTSTRAP_FIELD) is True:
        return False
    if not has_category(data):
        if any(row.get('item_id') == ROOT_ID for row in data['items']):
            raise ValueError('既存のブックマークIDが別用途で使用されています')
        if not any(page.get('page_id') == 'windows' for page in data['pages']):
            # A nonstandard config without Windows page should not be changed.
            return False
        data['items'].append(dict(
            item_id=ROOT_ID, page_id='windows', parent_item_id='',
            title='ブックマーク', description='Chrome / Edge のブックマークを自動取得',
            item_kind='category', icon_key='category.blue', sort_order=20,
            enabled=True, keywords=['bookmark', 'お気に入り'],
            launch_source='browser_bookmarks', launch_actions=[]))
    data[BOOTSTRAP_FIELD] = True
    validate(data)
    # Preserve every custom field and item exactly as it was, and back up the
    # original user config before writing the migrated copy.
    backup_dir = path.parent.parent / 'backups'
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / ('launch_before_bookmarks_' +
                           datetime.now().strftime('%Y%m%d_%H%M%S') + '_' +
                           uuid4().hex[:6] + '.json')
    original = path.read_bytes()
    backup.write_bytes(original)
    tmp = path.with_name(path.name + '.bookmarks-' + uuid4().hex[:8] + '.tmp')
    try:
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)
    return True


def attach(data, browser, profiles):
    """Replace only ephemeral bookmark descendants of the editable root.

    The bookmark category belongs to the JSON config / Studio, not the runtime.
    Respect its ID, page, parent, enabled flag, title, and sort order.
    """
    if browser not in BROWSERS:
        raise ValueError('未知のブラウザです')
    result = copy.deepcopy(data)
    result['items'] = [r for r in result['items'] if not r.get('_browser_bookmark')]
    # The source-tag identifies the editable bookmark root, even if its ID has
    # been customized in Studio.  Never insert a second category in memory.
    root = next((r for r in result['items'] if
                 r.get('launch_source') == 'browser_bookmarks' and
                 r.get('item_kind') == 'category'), None)
    if not root or not root.get('enabled', True):
        return result
    items = result['items']
    root_id = root['item_id']
    page_id = root['page_id']

    many_profiles = len(profiles) > 1

    def walk(nodes, parent, profile_dir, browser_profile, chain=()):
        if len(chain) >= 40:  # protect against unexpectedly deep or malformed files
            return
        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            title = str(node.get('name') or '(名称なし)')
            identity = (browser, root_id, profile_dir, *chain, str(i), str(node.get('id', '')))
            node_id = _id(*identity)
            children = node.get('children')
            if isinstance(children, list) and node.get('type') == 'folder':
                items.append(dict(item_id=node_id, page_id=page_id, parent_item_id=parent,
                                  title=title, item_kind='category', icon_key='folder.yellow',
                                  enabled=True, sort_order=i, launch_actions=[], _browser_bookmark=True,
                                  _bookmark_browser=browser))
                walk(children, node_id, profile_dir, browser_profile, (*chain, str(i)))
            elif node.get('type') == 'url':
                url = str(node.get('url') or '')
                # Avoid javascript:, data:, file:, internal browser URLs and invalid schemes.
                if not url.casefold().startswith(('https://', 'http://')):
                    continue
                items.append(dict(item_id=node_id, page_id=page_id, parent_item_id=parent,
                                  title=title, description=url, item_kind='command', icon_key='globe',
                                  enabled=True, sort_order=i, _browser_bookmark=True,
                                  _bookmark_browser=browser, launch_actions=[{'launch_action_type': 'Open', 'launch_target': url.replace('%', '%%'),
                                                   'launch_browser': browser, 'launch_browser_profile': browser_profile}]))

    for profile in profiles:
        directory = str(profile['directory'])
        parent_id = root_id
        if many_profiles:
            parent_id = _id('profile', browser, root_id, directory)
            items.append(dict(item_id=parent_id, page_id=page_id, parent_item_id=root_id,
                              title=directory, item_kind='category', icon_key='folder.yellow',
                              enabled=True, sort_order=0 if directory == 'Default' else 1,
                              _browser_bookmark=True, _bookmark_browser=browser, launch_actions=[]))
        for index, group in enumerate(profile['roots']):
            if not group['children']:
                continue
            group_id = _id('root', browser, root_id, directory, index)
            items.append(dict(item_id=group_id, page_id=page_id, parent_item_id=parent_id,
                              title=group['name'], item_kind='category', icon_key='folder.yellow',
                              enabled=True, sort_order=index, _browser_bookmark=True, _bookmark_browser=browser, launch_actions=[]))
            walk(group['children'], group_id, directory, str(profile.get('browser_profile', directory)), ('root', str(index)))
    return result
