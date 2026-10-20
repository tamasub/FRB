"""Portable FRB search query contract (no Qt, reusable by JSON Studio).

- Whitespace joins terms with AND (existing behavior).
- Parenthesized ``(aaa or bbb)`` joins alternatives with OR.
- Multiple OR groups are ANDed with the other terms.
- ``*`` alone is a wildcard; SQLite %, _ and ! remain literal.
- Malformed/unclosed parentheses and ordinary names like ``file(1)`` are literal.

parse_search_query returns AND clauses containing OR branches containing AND
terms: tuple[clause][branch][term]. This small data-only representation is
usable by both in-memory and SQL adapters without evaluating any query text.
"""
import re

_OR_SPLIT = re.compile(r'\s+or\s+', re.IGNORECASE)
_GROUP = re.compile(r'\(([^()]*)\)')


def parse_search_query(query):
    value = str(query or '').casefold()
    clauses = []
    offset = 0

    def ordinary(text):
        for term in text.split():
            clauses.append(((term,),))

    for match in _GROUP.finditer(value):
        inner = match.group(1)
        branches = _OR_SPLIT.split(inner.strip())
        if len(branches) < 2 or not all(part.strip() for part in branches):
            continue  # Literal parenthesis, not a valid OR expression.
        ordinary(value[offset:match.start()])
        clauses.append(tuple(tuple(part.split()) for part in branches))
        offset = match.end()
    ordinary(value[offset:])
    return tuple(clauses)


def _matches_term(content, term):
    offset = 0
    for part in term.split('*'):
        if not part:
            continue
        found = content.find(part, offset)
        if found < 0:
            return False
        offset = found + len(part)
    return True


def matches_search_text(content, query):
    """Casefolded substring/wildcard matching with parenthesized OR groups."""
    folded = str(content).casefold()
    return all(any(all(_matches_term(folded, term) for term in branch)
                   for branch in clause)
               for clause in parse_search_query(query))



def choice_search_content(choice, path=''):
    """Build the searchable text of a recipient, excluding internal metadata.

    Both the Launch global search and the recipient picker use this same
    contract. IDs, grouping keys, sort order and action fields are not text
    the user intends to search; matching them makes unrelated contacts show up.
    The owning menu's display path is searchable only in global search.
    """
    keywords = choice.get('keywords', [])
    if isinstance(keywords, (tuple, list)):
        keywords = ' '.join(map(str, keywords))
    return ' '.join(str(value) for value in (
        choice.get('title', ''), choice.get('description', ''),
        choice.get('value', ''), keywords, path,
    ))


def matches_choice_search(choice, query, path=''):
    """Match a recipient using the shared Boolean/wildcard search grammar."""
    return matches_search_text(choice_search_content(choice, path), query)


def sql_like_term(term):
    """SQLite LIKE fragment: '*' is wildcard; '%'/'_'/'!' are literals."""
    escaped = (str(term).casefold().replace('!', '!!')
               .replace('%', '!%').replace('_', '!_'))
    return '%' + escaped.replace('*', '%') + '%'


def sql_search_condition(query, fields=('name_fold', 'path')):
    """Compile query for trusted SQL column names; user terms are always parameters.

    Returns (SQL WHERE expression, parameters).  The caller supplies fixed,
    trusted column identifiers; do not pass user-provided names here.
    """
    clauses, params = [], []
    for clause in parse_search_query(query):
        branches = []
        for branch in clause:
            terms = []
            for term in branch:
                parts = []
                for field in fields:
                    parts.append(f"{field} LIKE ? ESCAPE '!'")
                    params.append(sql_like_term(term))
                terms.append('(' + ' OR '.join(parts) + ')')
            branches.append('(' + ' AND '.join(terms) + ')')
        clauses.append('(' + ' OR '.join(branches) + ')')
    return (' AND '.join(clauses) if clauses else '1=1'), tuple(params)
