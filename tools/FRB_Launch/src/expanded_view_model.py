"""Data-only rules for the optional, experimental FRB Launch expanded view.

The view does not own menu data and must not hard-code folder/bookmark labels.
"""

DEFAULT_CONFIG = {
    'enabled': True,
    'page_id': 'work',
    'files_item_id': 'folders',
    'bookmarks_item_id': '__browser_bookmarks_root',
}


def normalize_options(value):
    options = dict(DEFAULT_CONFIG)
    if isinstance(value, dict):
        for key in options:
            if key in value:
                options[key] = value[key]
    if not isinstance(options['enabled'], bool):
        raise ValueError('expanded_view.enabled must be boolean')
    for key in ('page_id', 'files_item_id', 'bookmarks_item_id'):
        if not isinstance(options[key], str) or not options[key].strip():
            raise ValueError(f'expanded_view.{key} must be a nonempty string')
    if options['files_item_id'] == options['bookmarks_item_id']:
        raise ValueError('expanded_view panels need distinct item IDs')
    return options


def page_roots(items, page_id):
    return sorted((item for item in items if item.get('enabled', True)
                   and item.get('page_id') == page_id
                   and not item.get('parent_item_id')),
                  key=lambda item: (item.get('sort_order', 0), item.get('title', '')))


def expanded_targets(items, options):
    roots = page_roots(items, options['page_id'])
    by_id = {row.get('item_id'): row for row in roots}
    left = by_id.get(options['files_item_id'])
    right = by_id.get(options['bookmarks_item_id'])
    if not left or not right:
        return None
    if left.get('item_kind') != 'category' or right.get('item_kind') != 'category':
        return None
    return roots, left, right


def should_expand(*, view_mode, page_id, query, stack, selection, options, available):
    return (view_mode == 'expanded' and options['enabled'] and available
            and page_id == options['page_id'] and not query.strip()
            and not stack and selection is None)
