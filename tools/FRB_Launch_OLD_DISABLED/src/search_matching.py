"""Portable FRB search query contract (no Qt, reusable by JSON Studio).

- Whitespace joins terms with AND (existing behavior).
- Parenthesized ``(aaa or bbb)`` joins alternatives with OR.
- Parenthesized AND groups may be ORed: ``(田中 一郎) or (佐藤 次郎)``.
- Extra enclosing parentheses work: ``((田中 一郎) or (佐藤 次郎))``.
- ``*`` alone is a wildcard; SQLite %, _ and ! remain literal.
- Invalid/unclosed parentheses and ordinary names like ``file(1)`` stay literal.

parse_search_query returns AND clauses containing OR branches containing AND
terms: tuple[clause][branch][term]. This data-only representation is shared by
in-memory and SQL adapters; user input is never evaluated as code.
"""
import re
from functools import lru_cache

_OR_SPLIT = re.compile(r'\s+or\s+', re.IGNORECASE)
_GROUP = re.compile(r'\(([^()]*)\)')
# Only interpret parentheses as an expression if they hold multiple separated
# words. This preserves legacy literal searches for file(1), (2026), and paths.
_EXPRESSION_GROUP = re.compile(r'\([^()]*\s+[^()]*\)')
_MAX_CLAUSES = 128
_MAX_BRANCHES = 512


def _legacy_parse(query):
    """Retain the previous parser for plain search and literal punctuation."""
    clauses = []
    offset = 0

    def ordinary(text):
        for term in text.split():
            clauses.append(((term,),))

    for match in _GROUP.finditer(query):
        branches = _OR_SPLIT.split(match.group(1).strip())
        if len(branches) < 2 or not all(part.strip() for part in branches):
            continue
        ordinary(query[offset:match.start()])
        clauses.append(tuple(tuple(part.split()) for part in branches))
        offset = match.end()
    ordinary(query[offset:])
    return tuple(clauses)


def _expression_tokens(text):
    """Split only leading/trailing group marks; file(1) remains one term."""
    result = []
    for raw in text.split():
        word = raw
        while word.startswith('('):
            result.append('(')
            word = word[1:]
        # Embedded literal parentheses (e.g. report(2026)) are not syntax.
        ending = len(word) - len(word.rstrip(')'))
        middle = word[:-ending] if ending else word
        if '(' in middle or ')' in middle:
            if word:
                result.append(word)
            continue
        if ending:
            middle = word[:-ending]
            if middle:
                result.append(middle)
            result.extend(')' for _ in range(ending))
        elif word:
            result.append(word)
    return result


class _InvalidExpression(Exception):
    pass


class _ExpressionParser:
    """Boolean grammar: implicit AND binds tighter than OR."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def read_atom(self):
        token = self.peek()
        if token == '(':
            self.pos += 1
            node = self.read_or()
            if self.peek() != ')':
                raise _InvalidExpression()
            self.pos += 1
            return node
        if token is None or token == ')' or token == 'or':
            raise _InvalidExpression()
        self.pos += 1
        return ('term', token)

    def read_and(self):
        nodes = []
        while self.peek() not in (None, ')', 'or'):
            nodes.append(self.read_atom())
        if not nodes:
            raise _InvalidExpression()
        return nodes[0] if len(nodes) == 1 else ('and', tuple(nodes))

    def read_or(self):
        nodes = [self.read_and()]
        while self.peek() == 'or':
            self.pos += 1
            nodes.append(self.read_and())
        return nodes[0] if len(nodes) == 1 else ('or', tuple(nodes))

    def parse(self):
        node = self.read_or()
        if self.peek() is not None:
            raise _InvalidExpression()
        return node


def _simple_and_terms(node):
    """Represent (a b) OR (c d) compactly as one OR clause."""
    if node[0] == 'term':
        return (node[1],)
    if node[0] == 'and':
        terms = tuple(_simple_and_terms(part) for part in node[1])
        if all(term is not None for term in terms):
            return tuple(word for group in terms for word in group)
    return None


def _expression_clauses(node):
    kind, value = node
    if kind == 'term':
        return (((value,),),)
    if kind == 'and':
        clauses = ()
        for item in value:
            clauses += _expression_clauses(item)
            if len(clauses) > _MAX_CLAUSES:
                raise _InvalidExpression()
        return clauses
    # An OR between AND-groups needs no expensive distribution.
    branches = tuple(_simple_and_terms(item) for item in value)
    if all(branch is not None for branch in branches):
        if len(branches) > _MAX_BRANCHES:
            raise _InvalidExpression()
        return (branches,)
    # General nested expressions: distribute OR over the AND clauses.
    clauses = _expression_clauses(value[0])
    for item in value[1:]:
        other = _expression_clauses(item)
        if len(clauses) * len(other) > _MAX_CLAUSES:
            raise _InvalidExpression()
        clauses = tuple(a + b for a in clauses for b in other)
        if any(len(clause) > _MAX_BRANCHES for clause in clauses):
            raise _InvalidExpression()
    return clauses


@lru_cache(maxsize=256)
def _parse_folded_query(value):
    if _EXPRESSION_GROUP.search(value):
        try:
            tokens = _expression_tokens(value)
            # Bound parse work for pasted/unfinished deeply nested queries.
            if len(tokens) <= 128:
                return _expression_clauses(_ExpressionParser(tokens).parse())
        except (_InvalidExpression, RecursionError):
            # Typing half an expression (especially with a Japanese IME)
            # should never break the search UI; fall back to literal terms.
            pass
    return _legacy_parse(value)


def parse_search_query(query):
    return _parse_folded_query(str(query or '').casefold())


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
    """Casefolded substring/wildcard matching with grouped AND / OR."""
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
    """Compile query for trusted SQL column names; user terms are parameters.

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
