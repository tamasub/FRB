"""User-visible search terms: space-separated AND with optional '*' wildcards.

Each '*' matches zero or more characters; ordinary terms retain substring
matching, and SQL's '%'/'_' characters are always literal user text.
"""


def matches_search_text(content, query):
    """Case-insensitive search, using ordered literal segments for wildcards.

    Splitting around '*' avoids regex/backtracking even for wide indexes or
    search terms containing many wildcards.
    """
    folded = str(content).casefold()
    for term in str(query).casefold().split():
        offset = 0
        for part in term.split('*'):
            if not part:
                continue
            found = folded.find(part, offset)
            if found < 0:
                return False
            offset = found + len(part)
    return True


def sql_like_term(term):
    """SQLite LIKE fragment: '*' is a wildcard, '%'/'_'/'!' are literals."""
    escaped = (str(term).casefold().replace('!', '!!')
               .replace('%', '!%').replace('_', '!_'))
    return '%' + escaped.replace('*', '%') + '%'
