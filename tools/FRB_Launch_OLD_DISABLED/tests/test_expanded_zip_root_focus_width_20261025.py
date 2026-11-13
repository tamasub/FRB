"""ZIP toolbar button keeps its complete label when the focus border grows."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')


def test_zip_gets_a_small_extra_width_without_changing_other_roots():
    assert "if row.get('title') == 'ZIP':\n                    button.setMinimumWidth(button.sizeHint().width() + 10)" in SOURCE
    assert SOURCE.count('button.setMinimumWidth(button.sizeHint().width() + 10)') == 1


def test_existing_focus_and_selection_styles_are_preserved():
    assert 'QPushButton#expandedRootButton:focus {{border:2px solid #56a88c;background:{active};}}' in SOURCE
    assert 'QPushButton#expandedRootButton:checked {{background:{active};border:1px solid #81bca4;font-weight:600;}}' in SOURCE
