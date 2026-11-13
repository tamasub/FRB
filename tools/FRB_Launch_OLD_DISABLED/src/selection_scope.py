"""Pure selection-scoping helper, independent of the Qt list implementation."""


def update_visible_checks(checked_ids, visible_ids, selected):
    """Check or uncheck *only* filtered/visible choices; preserve hidden choices."""
    result = set(checked_ids)
    if selected:
        result.update(visible_ids)
    else:
        result.difference_update(visible_ids)
    return result


def leave_global_choice_selection(query, entry_query, choices):
    """Leave a global-search recipient picker when a *different* search has
    no hits in that picker.  A choice group deliberately opened from a Page
    supplies entry_query=None, so filtering that group never exits it.

    Testing only at render time keeps this off the IME preedit/keystroke path.
    """
    if entry_query is None:
        return False
    query = str(query).strip()
    if query == entry_query:
        return False
    if not query:
        return True
    from search_matching import matches_choice_search
    return not any(matches_choice_search(choice, query) for choice in choices)


def global_choice_ids_in_results(rows, owner_id):
    """Snapshot the choices displayed for one owner in global search.

    A global hit can match the *parent path* (e.g. SE部) even when that
    phrase is absent from every individual recipient. Reuse precisely the
    visible hit IDs when entering the picker, without re-running search.
    """
    return frozenset(row['choice_id'] for row in rows
                     if row and row.get('_search_selection_owner') == owner_id
                     and row.get('choice_id'))


def filtered_selection_choices(choices, query, entry_query=None, entry_ids=None):
    """Preserve original global-search hits on entry; filter later edits normally.

    A Page-opened selection has no global entry query and uses the existing
    recipient-only matcher. No additional queries/SQLite work on typing.
    """
    from search_matching import matches_choice_search
    if entry_query is not None and query == entry_query and entry_ids is not None:
        return [choice for choice in choices if choice['choice_id'] in entry_ids]
    return [choice for choice in choices if matches_choice_search(choice, query)]
