"""Files Exp final polish: status expiry, cascade edit font, scroll menu arrows,
three-surface synchronization. These source tests run without Windows/PySide6.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
EXP = (ROOT / 'src' / 'remote_files_explorer.py').read_text(encoding='utf-8')
REMOTE = (ROOT / 'src' / 'launch_remote.py').read_text(encoding='utf-8')


def method(code, klass, name):
    class_node = next(n for n in ast.parse(code).body if isinstance(n, ast.ClassDef) and n.name == klass)
    node = next(n for n in class_node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)
    return ast.get_source_segment(code, node)


def test_rename_in_cascade_row_uses_same_13px_font_as_visible_menu():
    editor = method(APP, 'RemoteFolderCascade', 'begin_inline_rename')
    assert "row_font.setFamily('Yu Gothic UI')" in editor
    assert 'row_font.setPixelSize(13)' in editor
    assert "font-size:13px;" in editor
    assert 'editor.setFont(row_font)' in editor
    assert 'font-size:15px' not in editor
    # Both light/dark long-list views use an explicit 13px row.
    assert "font-family:'Yu Gothic UI'; font-size:13px;" in APP
    assert "font-family:'Yu Gothic UI'; font-size:13px;" in (ROOT/'src/launch_appearance.py').read_text(encoding='utf-8')


def test_rename_has_inline_editor_for_normal_and_scroll_columns():
    begin = method(APP, 'RemoteFolderCascade', 'begin_inline_rename')
    assert 'self.actionGeometry(action)' in begin
    assert 'self.scroll_tree.visualItemRect(tree_item)' in begin
    assert "QLineEdit(owner)" in begin
    assert 'editor.editingFinished.connect(' in begin
    assert 'self._finish_inline_rename(' in begin
    route = method(APP, 'Launcher', 'rename_remote_cascade_entry')
    assert 'source_menu.begin_inline_rename(target, kind)' in route


def test_disclosure_and_breadcrumb_changes_keep_exp_in_sync_without_cycle():
    exp = method(EXP, 'FilesExplorerPanel', 'sync_current_directory') if 'class FilesExplorerPanel' in EXP else None
    # Source may use a shorter class name; find by method contract.
    if exp is None:
        exp = next(ast.get_source_segment(EXP, n) for k in ast.parse(EXP).body
                   if isinstance(k, ast.ClassDef) for n in k.body
                   if isinstance(n, ast.FunctionDef) and n.name == 'sync_current_directory')
    assert 'self._syncing_directory = True' in exp
    assert 'self._syncing_directory = False' in exp
    assert 'self.tree.setCurrentIndex(node)' in exp
    assert 'self._activate_disclosure' in EXP
    assert 'self.tree.expanded.connect(self._activate_disclosure)' in EXP
    assert 'self.tree.collapsed.connect(self._activate_disclosure)' in EXP
    launcher_sync = method(APP, 'Launcher', 'on_files_directory_changed')
    assert 'panel.sync_current_directory(directory)' in launcher_sync
    assert 'panel.sync_current_directory(view.current_directory())' in REMOTE


def test_footer_short_lived_messages_and_constant_navigation_hint():
    klass = next(n for n in ast.parse(APP).body if isinstance(n, ast.ClassDef) and n.name == 'TimedStatusFooter')
    source = ast.get_source_segment(APP, klass)
    assert 'setInterval(10000)' in source
    assert '_expiry.setSingleShot(True)' in source
    assert '_expiry.timeout.connect(self.clear)' in source
    assert 'self._expiry.stop()' in source
    assert "str(text).startswith(('↑↓'" in source
    assert "self.footer = TimedStatusFooter(" in APP


def test_chevron_from_menu_outer_right_edge_not_label_length():
    painter = method(APP, 'RemoteFolderActionsMenu', 'paintEvent')
    assert 'self.contentsRect().right() - 13' in painter
    assert 'rect.right() - 15' not in painter
    assert 'painter.fillPath(arrow, color)' in painter
