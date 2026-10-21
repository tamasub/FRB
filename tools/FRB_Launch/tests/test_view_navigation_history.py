import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from view_navigation_history import ViewNavigationHistory


def state(page='work', stack=(), query='', selection=None, current=None, checks=()):
    return dict(page_id=page, stack=tuple({'item_id': item} for item in stack),
                selection={'item_id': selection} if selection else None,
                query=query, current_item_id=current, checked=frozenset(checks), focus='list')


def test_page_folder_search_back_forward_home():
    h = ViewNavigationHistory()
    h.reset(state())
    h.push(state(stack=('files',)))
    h.push(state(stack=('files', 'dev')))
    h.push(state(query='config'))
    h.push(state(page='frb', query=''))
    assert h.back()['query'] == 'config'
    assert h.back()['stack'][-1]['item_id'] == 'dev'
    assert h.forward()['query'] == 'config'
    assert h.forward()['page_id'] == 'frb'
    h.push(state(page='work'))  # Home
    assert h.back()['page_id'] == 'frb'
    assert h.forward()['page_id'] == 'work'


def test_editing_current_selection_does_not_create_history():
    h = ViewNavigationHistory()
    h.reset(state(current='one'))
    h.update_current(state(current='two'))
    assert not h.can_back
    assert h.current['current_item_id'] == 'two'
    h.push(state(current='three'))
    assert len(h.entries) == 1
    h.push(state(selection='email'))
    h.update_current(state(selection='email', current='bob', checks=('bob',)))
    assert h.back()['current_item_id'] == 'three'
    assert h.forward()['checked'] == frozenset(('bob',))


def test_new_navigation_from_middle_discards_forward_and_bounds_history():
    h = ViewNavigationHistory(limit=4)
    h.reset(state())
    for key in ['a', 'b', 'c', 'd']:
        h.push(state(query=key))
    assert len(h.entries) == 4
    assert [entry['query'] for entry in h.entries] == ['a', 'b', 'c', 'd']
    assert h.back()['query'] == 'c'
    assert h.back()['query'] == 'b'
    h.push(state(query='other'))
    assert not h.can_forward
    assert h.back()['query'] == 'b'
    assert h.forward()['query'] == 'other'


def test_no_duplicate_history_for_same_location_and_reset():
    h = ViewNavigationHistory()
    h.push(state())
    assert not h.can_back
    assert not h.push(state(current='new'))
    assert len(h.entries) == 1
    h.push(state(query='x'))
    h.reset(state(page='frb'))
    assert not h.can_back and not h.can_forward
    assert h.current['page_id'] == 'frb'


def test_no_mutation_of_browsing_stack_and_nested_selection_location():
    h = ViewNavigationHistory()
    page = state()
    groups = state(stack=('mail',))
    recipient = state(stack=('mail',), selection='sales', checks=('a',))
    h.reset(page)
    h.push(groups)
    h.push(recipient)
    assert h.back() == groups
    assert h.back() == page
    assert h.forward() == groups
    assert h.forward() == recipient
