"""Remote Page launcher-only root entries.

Files and browser bookmarks already have dedicated Remote buttons.  Keep them
in the main compact launcher; only omit them from a Remote Page's first popup.
"""


def visible_remote_page_roots(rows):
    """Exclude dedicated Files/Bookmarks entry points from Remote Page roots.

    Do not filter nested categories: this applies only to the first column of
    a Page clicked in FRB Remote, never to the main menu or its child columns.
    """
    excluded_ids = {'folders', '__browser_bookmarks_root'}
    excluded_titles = {'files', 'ブックマーク'}
    return [row for row in rows if not (
        row.get('item_id') in excluded_ids
        or row.get('launch_source') == 'browser_bookmarks'
        or str(row.get('title', '')).strip().casefold() in excluded_titles
    )]
