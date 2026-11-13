"""FRB Launch search: OR between AND groups, with unchanged classic queries."""
from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from core import searchable_rows, column_filter_match
from search_matching import (parse_search_query, matches_search_text,
                             matches_choice_search, sql_search_condition)


QUERIES = (
    '(田中 一郎) or (佐藤 次郎)',
    '((田中 一郎) or (佐藤 次郎))',
    '((田中 一郎) OR (佐藤 次郎))',
)


def test_grouped_names_match_exactly_the_two_and_groups():
    for query in QUERIES:
        assert parse_search_query(query) == ((('田中', '一郎'), ('佐藤', '次郎')),)
        assert matches_search_text('田中 一郎', query)
        assert matches_search_text('佐藤 次郎', query)
        assert not matches_search_text('田中 次郎', query)
        assert not matches_search_text('佐藤 一郎', query)
        assert not matches_search_text('田中 佐藤', query)


def test_single_group_is_and_and_wrapping_is_not_required():
    assert matches_search_text('田中・一郎', '(田中 一郎)')
    assert not matches_search_text('田中 次郎', '(田中 一郎)')
    assert matches_search_text('田中・一郎', '((田中 一郎) or (佐藤 次郎))')
    assert matches_search_text('佐藤・次郎', '((田中 一郎) or (佐藤 次郎))')


def test_grouped_or_combines_with_other_conditions():
    q = '営業部 ((田中 一郎) or (佐藤 次郎))'
    assert matches_search_text('営業部 田中 一郎', q)
    assert matches_search_text('営業部 佐藤 次郎', q)
    assert not matches_search_text('営業部 佐藤 一郎', q)
    assert not matches_search_text('開発部 田中 一郎', q)
    assert matches_search_text('案件_田中 一郎 2026.md', '((田中 一郎) or (佐藤 次郎)) *.md')
    assert not matches_search_text('案件_田中 一郎 2026.xlsx', '((田中 一郎) or (佐藤 次郎)) *.md')


def test_nested_or_and_semantics():
    q = '((田中 一郎) or (佐藤 次郎)) (東京 or 大阪)'
    assert matches_search_text('佐藤 次郎 大阪', q)
    assert matches_search_text('田中 一郎 東京', q)
    assert not matches_search_text('佐藤 次郎 福岡', q)
    assert not matches_search_text('田中 次郎 大阪', q)


def test_existing_literal_parentheses_or_wildcards_and_partial_typing():
    assert parse_search_query('x (a or b) y') == ((('x',),), (('a',), ('b',)), (('y',),))
    assert matches_search_text('report(2026).md', 'report(2026)')
    assert matches_search_text('draft (approved)', '(approved)')
    assert matches_search_text('C:/Project (Team)/report(2026)', 'Project (Team)')
    assert matches_search_text('report(2026) 田中 一郎', 'report(2026) (田中 一郎)')
    assert not matches_search_text('田中 一郎', '(田中 一郎) or (佐藤 次郎')
    assert not matches_search_text('hello', '(x or)')
    assert matches_search_text('MARKDOWN_2026.md', 'mark*own *.md')


def test_choice_and_global_search_use_same_boolean_matching():
    choices = [
        {'choice_id': str(i), 'title': name, 'value': f'{i}@example.invalid',
         'group_id': 'sales', 'enabled': True}
        for i, name in enumerate(('田中 一郎', '佐藤 次郎', '田中 次郎', '佐藤 一郎'), 1)
    ]
    data = {
        'pages': [{'page_id': 'work', 'title': '仕事', 'enabled': True}],
        'items': [{'item_id': 'contacts', 'item_kind': 'selection', 'page_id': 'work',
                   'title': 'メール宛先', 'launch_selection_group_id': 'sales', 'enabled': True}],
        'launch_choices': choices,
    }
    for query in QUERIES:
        picker = [c['title'] for c in choices if matches_choice_search(c, query)]
        global_hits = [r['title'] for r, _ in searchable_rows(data, query)
                       if r.get('_search_selection_owner')]
        assert picker == ['田中 一郎', '佐藤 次郎']
        assert global_hits == ['田中 一郎', '佐藤 次郎']
    assert column_filter_match({'title': '佐藤 次郎', 'description': ''}, QUERIES[0])
    assert not column_filter_match({'title': '佐藤 一郎', 'description': ''}, QUERIES[0])


def test_sql_and_memory_agree_and_are_parameterized():
    names = ('田中 一郎', '佐藤 次郎', '田中 次郎', '佐藤 一郎')
    with sqlite3.connect(':memory:') as db:
        db.execute('CREATE TABLE contacts (name_fold TEXT NOT NULL, path TEXT NOT NULL)')
        db.executemany('INSERT INTO contacts VALUES (?, ?)', [(name.casefold(), '仕事/営業部') for name in names])
        for q in (*QUERIES, '営業部 ((田中 一郎) or (佐藤 次郎))',
                  '((田中 一郎) or (佐藤 次郎)) (営業部 or 企画部)'):
            cond, params = sql_search_condition(q)
            assert '田中' not in cond and '佐藤' not in cond
            results = {row[0] for row in db.execute('SELECT name_fold FROM contacts WHERE ' + cond, params)}
            expected = {name.casefold() for name in names
                        if matches_search_text(name + ' 仕事/営業部', q)}
            assert results == expected, q


def test_file_index_query_uses_same_compiler():
    # SQL search_index invokes sql_search_condition, so check integration with
    # the existing file-index adapter rather than duplicating its SQL logic.
    from file_index import build_index, load_options, search_index
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for name in ('田中_一郎.md', '佐藤_次郎.md', '田中_次郎.md', '佐藤_一郎.md'):
            (root / name).write_text('test', encoding='utf-8')
        db = root / 'index.db'
        build_index(db, [str(root)], load_options(root / 'absent.json'))
        actual = {r['name'] for r in search_index(db, QUERIES[0])}
        assert actual == {'田中_一郎.md', '佐藤_次郎.md'}


def test_large_nested_query_is_bounded_and_does_not_raise():
    query = '(' * 180 + '田中 一郎' + ')' * 180
    assert not matches_search_text('田中 一郎', query)
    assert parse_search_query(query)
