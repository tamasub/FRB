"""Read-only Launch JSON -> Files Exp virtual tree projection.

Every virtual node carries a stable page/item identity.  The source JSON is
never mutated here; future Studio copy/cut/paste must use an explicit changeset
against that identity, not filesystem operations or an in-memory UI row.
"""

PAGE_NAMES = (('work', 'My Work'), ('windows', 'Windows'), ('frb', 'FRB実験'))


def virtual_launch_pages(pages, authored_items):
    """Return the three ordered enabled page trees from *authored* Launch JSON.

    A row is a folder when it has enabled children, or is an explicit category;
    all executable terminal rows are virtual files. Missing/disabled parents
    and broken cyclic references do not become runnable phantom entries.
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
        by_parent = {}
        for pos, row in enumerate(rows):
            parent = str(row.get('parent_item_id') or '')
            by_parent.setdefault(parent, []).append((pos, row))
        for siblings in by_parent.values():
            siblings.sort(key=lambda pair: (int(pair[1].get('sort_order') or 0), pair[0]))

        def gather(parent_id, ancestry, depth):
            if depth > 30:
                return []
            children = []
            for _, row in by_parent.get(parent_id, ()):
                item_id = str(row.get('item_id'))
                if item_id in ancestry:
                    continue
                descendants = gather(item_id, ancestry | {item_id}, depth + 1)
                children.append({
                    'source': 'launch_json',
                    'kind': 'folder' if descendants else 'file',
                    'page_id': page_id,
                    'item_id': item_id,
                    'parent_item_id': parent_id,
                    'node_id': f'item:{page_id}:{item_id}',
                    'title': str(row.get('title') or item_id),
                    'children': descendants,
                    # Preserve source row data for the existing Launch execute path.
                    'row': row,
                })
            return children
        result.append({
            'source': 'launch_json', 'kind': 'page', 'page_id': page_id,
            'item_id': '', 'parent_item_id': '',
            'node_id': f'page:{page_id}', 'title': label,
            'children': gather('', frozenset(), 0),
        })
    return result


def virtual_item_identity(node):
    """Future Studio changeset reference; never a physical file path."""
    if not isinstance(node, dict) or node.get('source') != 'launch_json':
        return None
    return {key: str(node.get(key, ''))
            for key in ('source', 'page_id', 'item_id', 'parent_item_id', 'node_id')}
