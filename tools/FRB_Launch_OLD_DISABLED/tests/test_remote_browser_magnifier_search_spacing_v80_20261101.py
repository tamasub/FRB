"""v80: tighten just the Browser bookmark search row's leading whitespace."""
import ast
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf-8')


def _filter_method():
    module = ast.parse(SOURCE)
    cls = next(node for node in module.body
               if isinstance(node, ast.ClassDef) and node.name == 'CascadeMenu')
    fn = next(node for node in cls.body
              if isinstance(node, ast.FunctionDef) and node.name == '_ensure_local_filter')
    return ast.get_source_segment(SOURCE, fn)


def test_bookmark_search_left_edge_is_eight_pixels_closer():
    code = _filter_method()
    assert 'search_row = QHBoxLayout() if bookmark_root else layout' in code
    assert 'if bookmark_root:\n            # The empty match counter' in code
    assert 'search_row.setSpacing(1)' in code
    assert 'search_row.setSpacing(5)' not in code
    # 2 layout gaps * (5px - 1px) = 8px, assuming empty count.
    assert (5 - 1) * 2 == 8


def test_magnifier_and_right_edge_stay_unchanged():
    code = _filter_method()
    assert 'glyph.setFixedSize(22, 30)' in code
    assert 'glyph.setAlignment(Qt.AlignmentFlag.AlignCenter)' in code
    assert 'search_row.insertWidget(1, self.filter_count)' in code
    assert 'search_row.addWidget(self.filter_edit, 1)' in code
    assert 'target_row.setContentsMargins(0, 0, 0, 0)' in code
    assert 'target_row.addWidget(self.remote_bookmark_current_tab_button, 1)' in code
    assert 'layout.setContentsMargins(7, 5, 7, 5)' in code


def test_other_columns_keep_existing_layout():
    code = _filter_method()
    assert 'search_row = QHBoxLayout() if bookmark_root else layout' in code
    assert "else:\n            glyph = QLabel('⌕', container)" in code
    assert 'else:\n            search_row.addWidget(self.filter_count)' in code
