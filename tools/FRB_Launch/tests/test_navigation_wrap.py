"""Shared navigation regression: no Qt required."""
import unittest
from navigation_wrap import next_wrapped, move_tree_selection


class StubItem:
    def __init__(self, name, hidden=False, disabled=False):
        self.name, self.hidden, self.disabled = name, hidden, disabled

    def isHidden(self):
        return self.hidden

    def isDisabled(self):
        return self.disabled


class StubTree:
    def __init__(self, items, current=None):
        self.items, self.current = items, current
        self.scrolled = None

    def topLevelItemCount(self):
        return len(self.items)

    def topLevelItem(self, index):
        return self.items[index]

    def currentItem(self):
        return self.current

    def setCurrentItem(self, item):
        self.current = item

    def scrollToItem(self, item):
        self.scrolled = item


class WrapNavigationTests(unittest.TestCase):
    def test_down_wraps_last_to_first(self):
        items = ['a', 'b', 'c']
        self.assertEqual(next_wrapped(items, 'c', 1), 'a')

    def test_up_wraps_first_to_last(self):
        items = ['a', 'b', 'c']
        self.assertEqual(next_wrapped(items, 'a', -1), 'c')

    def test_no_current_selects_edge(self):
        self.assertEqual(next_wrapped(['a', 'b'], None, 1), 'a')
        self.assertEqual(next_wrapped(['a', 'b'], None, -1), 'b')

    def test_empty_and_singleton(self):
        self.assertIsNone(next_wrapped([], None, 1))
        self.assertEqual(next_wrapped(['only'], 'only', -1), 'only')
        self.assertEqual(next_wrapped(['only'], 'only', 1), 'only')

    def test_hidden_and_disabled_items_are_skipped(self):
        a = StubItem('a')
        b = StubItem('b', hidden=True)
        c = StubItem('c')
        d = StubItem('d', disabled=True)
        tree = StubTree([a, b, c, d], current=c)
        self.assertIs(move_tree_selection(tree, 1), a)
        self.assertIs(tree.scrolled, a)
        self.assertIs(move_tree_selection(tree, -1), c)

    def test_empty_visible_list_keeps_selection_unchanged(self):
        item = StubItem('hidden', hidden=True)
        tree = StubTree([item], current=None)
        self.assertIsNone(move_tree_selection(tree, 1))
        self.assertIsNone(tree.currentItem())

    def test_custom_filter_for_backing_disabled_menu_actions(self):
        a, b, c = StubItem('a'), StubItem('b'), StubItem('c')
        tree = StubTree([a, b, c], current=a)
        self.assertIs(move_tree_selection(tree, -1,
            usable=lambda row: row.name != 'c'), b)


if __name__ == '__main__':
    unittest.main()
