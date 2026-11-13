"""No Qt needed: preserve the user's manual order and existing history JSON."""
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from search_history import SearchHistory
from search_history_categories import SearchHistoryCategories, UNCATEGORIZED


def new_state(tmp_path):
    original = SearchHistory(tmp_path / 'search_history.json')
    for word in ('old', '田中 一郎', '佐藤 次郎', 'vscode'):
        original.remember(word)
    before = original.path.read_bytes()
    categories = SearchHistoryCategories(tmp_path / 'search_history_categories.json', original.keywords)
    return original, before, categories


def test_first_load_preserves_existing_history_and_provides_windows(tmp_path):
    history, original, cats = new_state(tmp_path)
    assert cats.group_items(UNCATEGORIZED) == history.keywords
    assert cats.categories[0]['name'] == 'Windows'
    assert len(cats.categories) == 5
    assert cats.get('windows')['items'] == []  # Never automatically categorize or run actions.
    assert history.path.read_bytes() == original
    assert not cats.path.exists()  # No destructive upgrade on startup.


def test_drag_between_categories_and_reload_preserves_position(tmp_path):
    history, original, cats = new_state(tmp_path)
    assert cats.move_keyword('vscode', 'development', 0)
    assert cats.move_keyword('田中 一郎', 'contacts', 0)
    assert cats.move_keyword('佐藤 次郎', 'contacts', 1)
    assert cats.group_items('contacts') == ['田中 一郎', '佐藤 次郎']
    assert cats.move_keyword('佐藤 次郎', 'contacts', 0)
    assert cats.group_items('contacts') == ['佐藤 次郎', '田中 一郎']
    assert not cats.move_keyword('佐藤 次郎', 'contacts', 0)
    assert history.path.read_bytes() == original
    reloaded = SearchHistoryCategories(cats.path, history.keywords)
    assert reloaded.group_items('contacts') == ['佐藤 次郎', '田中 一郎']
    assert reloaded.group_items('development') == ['vscode']
    assert reloaded.group_items(UNCATEGORIZED) == ['old']


def test_new_history_only_goes_to_unclassified_and_never_moves_old_entries(tmp_path):
    history, _, cats = new_state(tmp_path)
    cats.move_keyword('vscode', 'development', 0)
    cats.move_keyword('田中 一郎', 'contacts', 0)
    cats.move_keyword('佐藤 次郎', 'contacts', 1)
    history.remember('新しい履歴')
    assert cats.sync(history.keywords)
    assert cats.group_items(UNCATEGORIZED) == ['新しい履歴', 'old']
    assert not cats.sync(history.keywords)
    assert not history.remember('田中 一郎')
    cats.sync(history.keywords)
    assert cats.group_items('contacts') == ['田中 一郎', '佐藤 次郎']


def test_unclassified_manual_reorder_and_move_back(tmp_path):
    history, _, cats = new_state(tmp_path)
    original = list(history.keywords)
    assert cats.move_keyword('old', UNCATEGORIZED, 0)
    assert cats.group_items(UNCATEGORIZED) == ['old'] + [x for x in original if x != 'old']
    assert cats.move_keyword('old', 'windows', 0)
    assert cats.move_keyword('old', UNCATEGORIZED, 1)
    assert cats.group_items(UNCATEGORIZED)[1] == 'old'
    assert history.keywords == original


def test_category_delete_returns_all_items_to_unclassified_and_defaults_do_not_reappear(tmp_path):
    history, _, cats = new_state(tmp_path)
    cats.move_keyword('vscode', 'windows', 0)
    cats.delete('windows')
    assert 'vscode' in cats.group_items(UNCATEGORIZED)
    assert cats.get('windows') is None
    reloaded = SearchHistoryCategories(cats.path, history.keywords)
    assert reloaded.get('windows') is None  # No automatic recreation after deletion.
    assert reloaded.group_items(UNCATEGORIZED).count('vscode') == 1


def test_category_create_rename_reorder_and_expand_persist(tmp_path):
    history, _, cats = new_state(tmp_path)
    custom = cats.create('会社')
    assert custom and cats.get(custom)['name'] == '会社'
    assert cats.create('会社') is None
    assert cats.create('未分類') is None
    assert cats.rename(custom, '業務')
    assert cats.move_category(custom, 0)
    assert cats.categories[0]['id'] == custom
    assert cats.expand_all(True)
    assert cats.expanded('windows')
    assert cats.set_expanded(custom, False)
    restored = SearchHistoryCategories(cats.path, history.keywords)
    assert restored.categories[0]['id'] == custom
    assert restored.get(custom)['name'] == '業務'
    assert not restored.expanded(custom)
    assert restored.expanded('windows')
    assert restored.expanded(UNCATEGORIZED)
    assert restored.expand_all(False)
    assert not restored.expand_all(False)


def test_deleted_or_expired_keywords_dont_come_back(tmp_path):
    history, _, cats = new_state(tmp_path)
    cats.move_keyword('田中 一郎', 'contacts', 0)
    history.remove('田中 一郎')
    assert cats.sync(history.keywords)
    assert cats.group_items('contacts') == []
    restored = SearchHistoryCategories(cats.path, history.keywords)
    assert '田中 一郎' not in restored.group_items(UNCATEGORIZED)


def test_rollback_on_failed_persist(tmp_path):
    history, _, cats = new_state(tmp_path)
    cats.create('業務')
    previous = cats.path.read_bytes()
    with patch('search_history_categories.os.replace', side_effect=OSError('locked')):
        try:
            cats.move_keyword('vscode', 'windows', 0)
            assert False, 'expected failure'
        except OSError:
            pass
    assert cats.group_items('windows') == []
    assert cats.path.read_bytes() == previous
    assert list(cats.path.parent.glob('*.tmp')) == []


def test_invalid_partial_category_json_and_duplicate_keywords_are_sanitized(tmp_path):
    history, _, cats = new_state(tmp_path)
    cats.path.write_text(json.dumps({
        'version': 1,
        'categories': [{'id': 'work', 'name': '会社', 'items': ['vscode', 'vscode', 'old']},
                       {'id': 'second', 'name': '次', 'items': ['vscode', 'missing']}],
        'uncategorized_order': ['old', '佐藤 次郎', '佐藤 次郎']
    }, ensure_ascii=False), encoding='utf8')
    restored = SearchHistoryCategories(cats.path, history.keywords)
    assert restored.group_items('work') == ['vscode', 'old']
    assert restored.group_items('second') == []
    assert restored.group_items(UNCATEGORIZED).count('佐藤 次郎') == 1
