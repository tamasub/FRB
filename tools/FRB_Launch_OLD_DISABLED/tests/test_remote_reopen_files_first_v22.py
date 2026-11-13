"""Contract checks: restore to Files top row only from non-panel areas."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
module = ast.parse(source)
launcher = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == 'Launcher')
restore = next(node for node in launcher.body if isinstance(node, ast.FunctionDef) and node.name == 'restore_last_current')
code = ast.get_source_segment(source, restore)


def test_only_non_panel_anchors_fall_back_to_files():
    assert "area not in ('files', 'directory', 'bookmarks')" in code
    assert "area = 'files'" in code


def test_fallback_starts_at_first_files_row():
    assert 'tree.setCurrentItem(tree.topLevelItem(0))' in code
    assert "self._focus_tree_row(view.left.tree, state.get('left_id'))" in code


def test_existing_path_restore_and_remote_sync_are_retained():
    assert 'view.refresh_middle()' in code
    assert 'self.remote_focus_area(area)' in code
