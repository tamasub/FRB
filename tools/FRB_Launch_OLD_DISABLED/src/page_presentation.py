"""Qt-independent presentation rules for Studio-owned Page titles/icons.

The original Page title is never rewritten; the editor may select an icon
without having to strip old emoji out of a user's existing Launch JSON.
"""

PAGE_ICONS = ('なし', '💼', '🎣', '🪟', '📁', '⭐', '🚀',
              '🧰', '🖥️', '🌐', '📝', '📌', '🎯', '⚙️', '📚', '✨')
DEFAULT_PAGE_TITLES = {'work': 'My Work', 'windows': 'Windows', 'frb': 'FRB実験'}
DEFAULT_PAGE_SORT = {'work': 10, 'windows': 20, 'frb': 30}


def page_display_title(page):
    """An explicitly chosen icon takes priority over any legacy title emoji."""
    title = str(page.get('title') or DEFAULT_PAGE_TITLES.get(str(page.get('page_id')), 'Page')).strip()
    if 'icon_key' not in page:
        return title  # Backward-compatible: original captions already have emojis.
    chosen = str(page.get('icon_key') or 'なし').strip()
    for old in PAGE_ICONS:
        if old != 'なし' and title.startswith(old):
            title = title[len(old):].lstrip()
            break
    return f'{chosen} {title}'.strip() if chosen and chosen != 'なし' else title


def ordered_pages(pages):
    """Use Studio's sort_order, with the legacy three-Page order as fallback."""
    def key(pair):
        pos, page = pair
        ident = str(page.get('page_id') or '')
        fallback = DEFAULT_PAGE_SORT.get(ident, 1000 + pos)
        try:
            order = int(page.get('sort_order') if page.get('sort_order') is not None else fallback)
        except (TypeError, ValueError):
            order = fallback
        return order, pos
    return [page for _, page in sorted(enumerate(pages or ()), key=key)
            if isinstance(page, dict) and page.get('enabled', True)]
