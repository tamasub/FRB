"""Search-history persistence and hotkey contract (no Qt needed)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from search_history import SearchHistory, normalize_keyword


class SearchHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'state' / 'search_history.json'
        self.history = SearchHistory(self.path)

    def test_first_open_has_empty_history(self):
        self.assertEqual(self.history.keywords, [])
        self.assertFalse(self.path.exists())

    def test_completed_keywords_are_added_at_front_and_persist(self):
        self.assertTrue(self.history.remember('  *.ps1  '))
        self.assertTrue(self.history.remember('FRB*.md'))
        self.assertEqual(self.history.keywords, ['FRB*.md', '*.ps1'])
        self.assertEqual(SearchHistory(self.path).keywords, self.history.keywords)
        self.assertEqual(json.loads(self.path.read_text(encoding='utf-8'))['version'], 1)

    def test_reuse_does_not_disturb_manual_order(self):
        for word in ('one', 'two', 'three'):
            self.history.remember(word)
        self.history.move('one', -1)
        original = list(self.history.keywords)
        self.assertFalse(self.history.remember('TWO'))
        self.assertEqual(self.history.keywords, original)
        self.assertEqual(SearchHistory(self.path).keywords, original)

    def test_move_up_down_and_edges(self):
        for word in ('one', 'two', 'three'):
            self.history.remember(word)
        self.assertTrue(self.history.move('one', -1))
        self.assertEqual(self.history.keywords, ['three', 'one', 'two'])
        self.assertFalse(self.history.move('three', -1))
        self.assertTrue(self.history.move('three', 1))
        self.assertEqual(SearchHistory(self.path).keywords, ['one', 'three', 'two'])
        self.assertFalse(self.history.move('three', 3))

    def test_delete_is_persisted(self):
        self.history.remember('make')
        self.history.remember('*.xlsx')
        self.assertTrue(self.history.remove('make'))
        self.assertFalse(self.history.remove('make'))
        self.assertEqual(SearchHistory(self.path).keywords, ['*.xlsx'])

    def test_slash_is_not_stored_and_empty_is_rejected(self):
        self.assertEqual(normalize_keyword(' a/b/c '), 'abc')
        self.assertFalse(self.history.remember(' / '))
        self.assertTrue(self.history.remember('FRB/.md'))
        self.assertEqual(self.history.keywords, ['FRB.md'])

    def test_limit_removes_oldest_by_manual_order(self):
        h = SearchHistory(self.path, limit=3)
        for word in ('A', 'B', 'C'):
            h.remember(word)
        h.move('A', -1)
        h.remember('D')
        self.assertEqual(h.keywords, ['D', 'C', 'A'])
        self.assertEqual(SearchHistory(self.path).keywords, h.keywords)

    def test_corrupt_file_and_duplicates_are_safely_loaded(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text('{oops', encoding='utf-8')
        self.assertEqual(SearchHistory(self.path).keywords, [])
        self.path.write_text(json.dumps({'keywords': ['one', 'ONE', 42, ' / ', 'two']}), encoding='utf8')
        self.assertEqual(SearchHistory(self.path).keywords, ['one', 'two'])

    def test_atomic_replace_failure_preserves_previous_file(self):
        self.history.remember('before')
        original = self.path.read_bytes()
        with patch('search_history.os.replace', side_effect=OSError('busy')):
            with self.assertRaises(OSError):
                self.history.remember('after')
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(self.path.parent.glob('*.tmp')), [])


if __name__ == '__main__':
    unittest.main()
