"""Updated specification: initial IME is halfwidth English, never forced Japanese.

The former first-Space-to-hiragana contract is superseded by persistent search.
"""
from test_cascade_always_visible_search_20261021 import (
    test_initial_ime_halfwidth_and_never_forced_to_japanese,
    test_initial_ime_callback_only_if_popup_still_owns_editor,
)
