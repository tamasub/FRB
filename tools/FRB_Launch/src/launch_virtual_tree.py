"""Read-only Launch JSON -> Files Exp virtual tree projection.

Every virtual node carries a stable page/item identity.  The source JSON is
never mutated here; future Studio copy/cut/paste must use an explicit changeset
against that identity, not filesystem operations or an in-memory UI row.
"""

PAGE_NAMES = (('work', 'My Work'), ('windows', 'Windows'), ('frb', 'FRB実験'))


def virtual_launch_pages(pages, authored_items, runtime_items=()):
    """Return the three ordered enabled page trees from *authored* Launch JSON.

    A row is a folder when it has enabled children, or is an explicit category;
    all executable terminal rows are virtual files. Missing/disabled parents
    and broken cyclic references do not become runnable phantom entries.

    Installed apps are the sole runtime-generated exception: the normal Launch
    menu synthesizes them from apps_cache.json beneath a user-authored category
    marked launch_source=installed_apps. Project those same rows into the
    virtual Files List, but never treat them as Studio-authored JSON items.
    """
    present = {str(p.get('page_id')) for p in (pages or ())
               if isinstance(p, dict) and p.get('enabled', True)}
    result = []
    for page_id, label in PAGE_NAMES:
        if page_id not in present:
            continue
        rows = [r for r in (authored_items or ())
                if isinstance(r, dict) and r.get('enabled', True)
                and str(r.get('page_id')) == page_id and r.get('item_id')]
        app_categories = {str(r['item_id']) for r in rows
                          if r.get('item_kind') == 'category'
                          and r.get('launch_source') == 'installed_apps'}
        authored_ids = {str(r['item_id']) for r in rows}
        # Only cached installed-app rows directly under an enabled, authored
        # application category. Other runtime rows (e.g. browser bookmarks)
        # stay outside the virtual JSON explorer and cannot be edited as JSON.
        rows.extend(r for r in (runtime_items or ())
                    if isinstance(r, dict) and r.get('_installed_app')
                    and r.get('enabled', True)
                    and str(r.get('page_id')) == page_id and r.get('item_id')
                    and str(r.get('item_id')) not in authored_ids
                    and str(r.get('parent_item_id') or '') in app_categories)
        by_parent = {}
        for pos, row in enumerate(rows):
            parent = str(row.get('parent_item_id') or '')
            by_parent.setdefault(parent, []).append((pos, row))
        for siblings in by_parent.values():
            siblings.sort(key=lambda pair: (int(pair[1].get('sort_order') or 0), pair[0]))

        def gather(parent_id, ancestry, depth, breadcrumbs, lineage):
            if depth > 30:
                return []
            children = []
            for _, row in by_parent.get(parent_id, ()):
                item_id = str(row.get('item_id'))
                if item_id in ancestry:
                    continue
                title = str(row.get('title') or item_id)
                descendants = gather(item_id, ancestry | {item_id}, depth + 1,
                                     breadcrumbs + (title,), lineage + (f'item:{page_id}:{item_id}',))
                is_folder = bool(descendants) or row.get('item_kind') == 'category'
                children.append({
                    'source': 'launch_json',
                    'kind': 'folder' if is_folder else 'file',
                    'page_id': page_id,
                    'item_id': item_id,
                    'parent_item_id': parent_id,
                    'node_id': f'item:{page_id}:{item_id}',
                    'title': title,
                    'breadcrumbs': breadcrumbs + (title,),
                    'lineage': lineage + (f'item:{page_id}:{item_id}',),
                    'children': descendants,
                    # Preserve source row data for the existing Launch execute path.
                    'row': row,
                    'runtime_catalog': ('installed_apps' if row.get('_installed_app')
                                        else ''),
                })
            return children
        result.append({
            'source': 'launch_json', 'kind': 'page', 'page_id': page_id,
            'item_id': '', 'parent_item_id': '',
            'node_id': f'page:{page_id}', 'title': label,
            'breadcrumbs': (label,),
            'lineage': (f'page:{page_id}',),
            'children': gather('', frozenset(), 0, (label,), (f'page:{page_id}',)),
        })
    return result


def virtual_item_identity(node):
    """Future Studio changeset reference; never a physical file path."""
    if not isinstance(node, dict) or node.get('source') != 'launch_json':
        return None
    return {key: str(node.get(key, ''))
            for key in ('source', 'page_id', 'item_id', 'parent_item_id', 'node_id')}


def virtual_exp_folders(node):
    """Only menu groups (never executable leaves) belong in Files Exp."""
    return [child for child in (node or {}).get('children', ())
            if child.get('kind') != 'file']


def virtual_list_rows(node):
    """Immediate children rendered in Files List; no filesystem path/write.

    Folder-like children can also appear in List, just as Windows Explorer
    shows both directories and files. Executable leaves are never Exp rows.
    The original authored Launch row is preserved for activation by stable ID.
    """
    result = []
    for child in (node or {}).get('children', ()):
        row = dict(child.get('row') or {})
        row['title'] = child['title']
        row['_launch_virtual_node'] = child
        row['item_kind'] = ('category' if child['kind'] != 'file'
                            else 'virtual_launch_file')
        row.pop('_browse_file', None)
        row.pop('_file', None)
        row.pop('_indexed_file', None)
        result.append(row)
    return result


def virtual_lookup_node(pages, authored_items, page_id, item_id='', runtime_items=()):
    """Find a folder by stable Launch JSON ID, e.g. for List -> Exp return."""
    for page in virtual_launch_pages(pages, authored_items, runtime_items):
        if page['page_id'] != str(page_id):
            continue
        if not item_id:
            return page
        pending = [page]
        while pending:
            entry = pending.pop()
            if entry.get('item_id') == str(item_id):
                return entry
            pending.extend(reversed(entry['children']))
    return None


def virtual_execution_row(authored_items, runtime_items, page_id, item_id):
    """Resolve a virtual leaf against current data, not a stale UI snapshot.

    Authored entries must still be enabled. Dynamic app rows are allowed only
    under an enabled, user-authored installed_apps category. Thus a virtual
    row can never cause a filesystem operation or execute an arbitrary runtime
    catalog item by forging a page/item ID.
    """
    page_id, item_id = str(page_id or ''), str(item_id or '')
    if not page_id or not item_id:
        return None
    authored = [r for r in (authored_items or ()) if isinstance(r, dict)]
    for row in authored:
        if (str(row.get('page_id') or '') == page_id
                and str(row.get('item_id') or '') == item_id):
            return row if row.get('enabled', True) else None
    app_parents = {str(row.get('item_id')) for row in authored
                   if str(row.get('page_id') or '') == page_id
                   and row.get('enabled', True)
                   and row.get('item_kind') == 'category'
                   and row.get('launch_source') == 'installed_apps'}
    for row in (runtime_items or ()):
        if (isinstance(row, dict) and row.get('_installed_app')
                and row.get('enabled', True)
                and str(row.get('page_id') or '') == page_id
                and str(row.get('item_id') or '') == item_id
                and str(row.get('parent_item_id') or '') in app_parents):
            return row
    return None
