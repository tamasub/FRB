"""Remote Page root-wheel and root-entry exclusion contracts (Qt-free)."""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from remote_page_items import visible_remote_page_roots

APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')


def extracted(name):
    cls = next(c for c in ast.parse(APP).body if isinstance(c, ast.ClassDef)
               and c.name == 'Launcher')
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                and n.name == name)
    node.decorator_list = []
    context = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 '<source>', 'exec'), context)
    return context[name]


def test_files_and_bookmarks_are_excluded_only_from_remote_page_root():
    rows = [
        dict(item_id='zip', title='ZIP', launch_source=''),
        dict(item_id='folders', title='Files'),
        dict(item_id='custom_files', title=' Files '),
        dict(item_id='__browser_bookmarks_root', title='Chromeのお気に入り'),
        dict(item_id='another', title='ブックマーク'),
        dict(item_id='some_source', title='読込済', launch_source='browser_bookmarks'),
        dict(item_id='quick', title='Quick'),
    ]
    assert [r['item_id'] for r in visible_remote_page_roots(rows)] == ['zip', 'quick']
    # The caller applies the filter only when parent.launch_source == remote_page.
    source = APP[APP.index('    def fill_cascade('):APP.index('    def _ask_overwrite(', APP.index('    def fill_cascade('))]
    assert "if parent.get('launch_source') == 'remote_page':" in source
    assert 'rows = visible_remote_page_roots(rows)' in source


def test_same_preview_closes_its_grandchild_but_keeps_first_child():
    fn = extracted('_remote_page_wheel_expand')
    chosen = Mock()
    chosen.isEnabled.return_value = True
    grandchild = NS(close=Mock(), deleteLater=Mock())
    child = NS(isVisible=lambda: True, owner_action=chosen, child=grandchild,
               hover_timer=NS(stop=Mock()))
    root = NS(remote_page_navigation=True, activeAction=lambda: chosen,
              openers={chosen: Mock()}, child=child,
              hover_timer=NS(stop=Mock()))
    assert fn(root) is False
    grandchild.close.assert_called_once()
    grandchild.deleteLater.assert_called_once()
    assert child.child is None
    assert root.child is child
    root.openers[chosen].assert_not_called()


def test_leaf_wheel_closes_previous_preview_without_executing():
    fn = extracted('_remote_page_wheel_expand')
    action = Mock()
    action.isEnabled.return_value = True
    child = NS(close=Mock(), deleteLater=Mock())
    root = NS(remote_page_navigation=True, activeAction=lambda: action,
              openers={}, child=child, hover_timer=NS(stop=Mock()))
    assert fn(root) is False
    assert root.child is None
    child.close.assert_called_once()
    child.deleteLater.assert_called_once()


def test_normal_compact_and_nested_page_menus_remain_unchanged():
    fn = extracted('_remote_page_wheel_expand')
    action = Mock()
    action.isEnabled.return_value = True
    opened = Mock()
    non_page = NS(remote_page_navigation=False, activeAction=lambda: action,
                  openers={action: opened}, child=None,
                  hover_timer=NS(stop=Mock()))
    assert fn(non_page) is False
    opened.assert_not_called()


def test_page_wheel_uses_root_even_when_child_menu_is_visible():
    source = ast.get_source_segment(APP, next(n for n in next(c for c in ast.parse(APP).body
        if isinstance(c, ast.ClassDef) and c.name == 'Launcher').body
        if isinstance(n, ast.FunctionDef) and n.name == 'remote_cascade_command'))
    assert "page_wheel = (command in ('UP', 'DOWN')" in source
    assert 'menu = remote_root' in source
    assert "if page_wheel:\n                self._remote_page_wheel_expand(menu)" in source
