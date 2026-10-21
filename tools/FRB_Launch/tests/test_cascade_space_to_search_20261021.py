"""Updated specification: popup search is visible before any Space is pressed.

The former first-Space-to-reveal contract is superseded by persistent search.
"""
from test_cascade_always_visible_search_20261021 import (
    test_visible_editor_built_before_popup_size_and_display,
    test_empty_query_restores_rows_without_deleting_visible_editor,
    test_escape_and_ordinary_space_contracts,
)
