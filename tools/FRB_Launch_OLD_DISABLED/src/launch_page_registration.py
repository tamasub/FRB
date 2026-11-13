"""Page Add/Update/Delete via the SAME Studio Change Core used for items.

No direct mutation of Launch configuration, no orphaned items, and no
filesystem side effects. Page unregister deliberately rejects non-empty pages.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path

from launch_menu_registration import (RegistrationError, VIEW_DEF, DOCUMENT_REF,
                                      _invoke_delete_cli)

PAGE_VIEW = 'pages_view'
PAGE_SECTION = 'pages'


def page_operation_plan(config_path, action, *, page_id='', title='', icon_key='📁'):
    """Validate against canonical JSON and prepare one CAS-protected operation."""
    filename = Path(config_path).resolve()
    raw = filename.read_bytes()
    document = json.loads(raw.decode('utf-8-sig'))
    pages = document.get('pages')
    items = document.get('items')
    if not isinstance(pages, list) or not isinstance(items, list):
        raise RegistrationError('設定JSONのpages/items配列が見つかりません。')
    identifiers = [str(row.get('page_id') or '') for row in pages if isinstance(row, dict)]
    if len(set(identifiers)) != len(identifiers):
        raise RegistrationError('Page IDが重複しているため変更できません。')
    current = next((row for row in pages if isinstance(row, dict)
                    and row.get('page_id') == page_id), None)
    if action == 'add':
        if not str(title).strip():
            raise RegistrationError('Page名を入力してください。')
        if page_id:
            raise RegistrationError('Page IDはStudioが自動採番します。')
        next_sort = max((int(row.get('sort_order') or 0)
                         for row in pages if isinstance(row, dict)), default=0) + 10
        operation = {'operation': 'add', 'section_id': PAGE_SECTION,
                     'placement': {'position': 'end'},
                     'records': [{'title': str(title).strip(),
                                  'icon_key': str(icon_key or 'なし'),
                                  'enabled': True, 'sort_order': next_sort}]}
        summary = {'added': 1}
    elif action == 'update':
        if current is None:
            raise RegistrationError('簡易編集対象のPageが見つかりません。')
        if not str(title).strip():
            raise RegistrationError('Page名を入力してください。')
        changes = [{'path': k, 'value': v} for k, v in (
            ('title', str(title).strip()), ('icon_key', str(icon_key or 'なし')))
            if current.get(k) != v]
        if not changes:
            return None
        operation = {'operation': 'update', 'section_id': PAGE_SECTION,
                     'targets': [{'id': page_id, 'changes': changes}]}
        summary = {'changed_existing': 1}
    elif action == 'delete':
        if current is None:
            raise RegistrationError('登録解除対象のPageが見つかりません。')
        if page_id == 'system':
            raise RegistrationError('System Pageは内部管理対象のため登録解除できません。')
        attached = [row for row in items if isinstance(row, dict)
                    and str(row.get('page_id') or '') == page_id]
        if attached:
            raise RegistrationError(
                f'配下に設定JSONの登録が{len(attached)}件あります。'
                '孤児データを防ぐため、このPageは登録解除できません。'
                '先に配下の登録を整理してください。')
        if sum(bool(p.get('enabled', True)) for p in pages if isinstance(p, dict)) <= 1:
            raise RegistrationError('最後のPageは登録解除できません。')
        operation = {'operation': 'delete', 'section_id': PAGE_SECTION,
                     'targets': [{'id': page_id}]}
        summary = {'deleted': 1}
    else:
        raise RegistrationError('未対応のPage操作です。')
    return {'filename': filename, 'base_sha256': hashlib.sha256(raw).hexdigest(),
            'operations': [operation], 'summary': summary}


def commit_page_operation(config_path, studio_root, action, *, page_id='',
                          title='', icon_key='📁', timeout=40):
    """PREVIEW → Expected/Actual Diff → COMMIT in Studio; never write JSON here."""
    plan = page_operation_plan(config_path, action, page_id=page_id,
                               title=title, icon_key=icon_key)
    if plan is None:
        return None
    trusted = {'schema_version': 'studio_change_core_config_v0_1',
               'documents': {DOCUMENT_REF: {
                   'path': str(plan['filename']), 'view_def': VIEW_DEF,
                   'view_id': PAGE_VIEW, 'section_ids': [PAGE_SECTION]}}}
    request = {'schema_version': 'studio_changeset_v0_1',
               'request_id': 'launch-page-' + uuid.uuid4().hex,
               'mode': 'dry_run', 'document_ref': DOCUMENT_REF,
               'base_sha256': plan['base_sha256'], 'view_def': VIEW_DEF,
               'view_id': PAGE_VIEW, 'operations': plan['operations']}
    result = None
    for mode in ('dry_run', 'commit'):
        result = _invoke_delete_cli(Path(studio_root).resolve(), trusted,
                                    request, mode, timeout)
        if any(result.get('summary', {}).get(k) != v
               for k, v in plan['summary'].items()):
            raise RegistrationError('Studio CLIのPage操作件数が期待値と一致しません。')
    return result
