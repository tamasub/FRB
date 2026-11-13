"""Folder favorite persistence and history drag ordering; no Qt dependency."""
import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from folder_favorites import FolderFavorites, normalize_favorite_path
from search_history import SearchHistory


class FolderFavoriteTests(unittest.TestCase):
    def test_windows_path_normalization(self):
        self.assertEqual(normalize_favorite_path('F:/FRB/tools/..'), 'F:\\FRB')
        self.assertEqual(normalize_favorite_path(r'\\server\share\a'), r'\\server\share\a')
        self.assertEqual(normalize_favorite_path('relative\\path'), '')

    def test_add_duplicate_remove_reorder_and_persistence(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / 'folder_favorites.json'
            favorites = FolderFavorites(db)
            self.assertTrue(favorites.add(r'F:\FRB\tools'))
            self.assertTrue(favorites.add(r'C:\Users\Example\Documents'))
            self.assertFalse(favorites.add(r'f:\frb\TOOLS'))
            self.assertEqual(favorites.paths, [r'C:\Users\Example\Documents', r'F:\FRB\tools'])
            self.assertTrue(favorites.reorder([r'F:\FRB\tools', r'C:\Users\Example\Documents']))
            self.assertFalse(favorites.reorder([r'F:\FRB\tools']))
            self.assertEqual(FolderFavorites(db).paths, favorites.paths)
            self.assertTrue(favorites.remove(r'c:\users\example\documents'))
            self.assertFalse(favorites.remove(r'C:\not\there'))
            self.assertEqual(FolderFavorites(db).paths, [r'F:\FRB\tools'])
            self.assertEqual(json.loads(db.read_text('utf-8'))['version'], 1)

    def test_history_drag_reorder_keeps_keywords(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'search_history.json'
            history = SearchHistory(path)
            for value in ('first', 'second', 'third'):
                history.remember(value)
            self.assertTrue(history.reorder(['first','third','second']))
            self.assertEqual(SearchHistory(path).keywords, ['first','third','second'])
            self.assertFalse(history.reorder(['first','third','unknown']))
            self.assertFalse(history.reorder(['first','third','third']))
            self.assertEqual(SearchHistory(path).keywords, ['first','third','second'])

    def test_invalid_json_is_safe(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'folder_favorites.json'
            path.write_text('{bad', encoding='utf8')
            self.assertEqual(FolderFavorites(path).paths, [])


if __name__ == '__main__':
    unittest.main()
