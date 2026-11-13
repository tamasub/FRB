"""Remote Browser bookmark search has the same right edge as tab choices.

Qt-free focused source checks; real Windows painting still needs manual UI check.
"""
import ast
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf-8')


def _filter_construction():
    mod = ast.parse(SOURCE)
    cls = next(n for n in mod.body if isinstance(n, ast.ClassDef) and n.name == 'CascadeMenu')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_ensure_local_filter')
    return ast.get_source_segment(SOURCE, fn)


def test_bookmark_search_counter_no_longer_reserves_the_search_right_edge():
    fn = _filter_construction()
    assert "bookmark_root = getattr(self, 'remote_browser_bookmark_roots', False)" in fn
    assert 'search_row.addWidget(self.filter_edit, 1)' in fn
    assert "self.filter_count = QLabel('', container)" in fn
    assert 'if bookmark_root:\n            # The match counter used to sit AFTER the search edit.' in fn
    assert 'search_row.insertWidget(1, self.filter_count)' in fn
    assert 'else:\n            search_row.addWidget(self.filter_count)' in fn


def test_bookmark_search_and_tab_choices_share_one_right_margin():
    fn = _filter_construction()
    assert 'layout.setContentsMargins(7, 5, 7, 5)' in fn
    assert 'search_row = QHBoxLayout() if bookmark_root else layout' in fn
    assert 'target_row.setContentsMargins(0, 0, 0, 0)' in fn
    assert 'target_row.addWidget(self.remote_bookmark_current_tab_button, 1)' in fn
    assert 'layout.addLayout(search_row)' in fn
    assert 'layout.addLayout(target_row)' in fn


def test_existing_button_target_and_filter_controls_unchanged():
    fn = _filter_construction()
    assert 'self._select_remote_bookmark_tab(True)' in fn
    assert 'self.filter_edit.textChanged.connect(self._apply_local_filter)' in fn
    assert 'self.remote_bookmark_current_tab_button.clicked.connect(' in fn
    assert 'self.remote_bookmark_new_tab_button.clicked.connect(' in fn
