"""Regressions for expanded middle-column multi selection and clipboard paste."""
import ast
from pathlib import Path
from types import SimpleNamespace

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from expanded_selection import physical_paths, context_paths
from clipboard_paste import clipboard_sources, is_cut_clipboard, make_paste_plan, paste_conflicts, paste_items
from virtual_clipboard_paste import is_virtual_file_clipboard

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
VIEW = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')


def isolate(source, cls, method, extra):
    node = ast.parse(source)
    owner = next(n for n in node.body if isinstance(n, ast.ClassDef) and n.name == cls)
    function = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == method)
    module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    exec(compile(module, '<isolated>', 'exec'), extra)
    return extra[method]


def row(path):
    return {'_file': str(path), 'item_kind': 'directory' if path.is_dir() else 'command'}


def test_context_right_click_inside_selection_keeps_all_files_and_folders(tmp_path):
    a = tmp_path / 'a.txt'; a.write_text('a')
    b = tmp_path / 'b.txt'; b.write_text('b')
    d = tmp_path / 'folder'; d.mkdir()
    rows = [row(a), row(b), row(d)]
    assert context_paths(rows[1], rows) == [a.resolve(), b.resolve(), d.resolve()]
    # Outside the existing selection = single clicked target.
    assert context_paths(rows[2], rows[:2]) == [d.resolve()]
    assert len(physical_paths([rows[0], rows[0], rows[1]])) == 2


def test_context_rejects_bookmarks_and_symlinks(tmp_path):
    a = tmp_path / 'a.txt'; a.write_text('data')
    link = tmp_path / 'link.txt'
    link.symlink_to(a)
    assert physical_paths([row(link)]) == []
    assert physical_paths([{'_file': str(a), '_browser_bookmark': True,
                            'item_kind': 'command'}]) == []


def test_middle_right_press_does_not_clear_selected_items():
    fake = SimpleNamespace(SelectionMode=SimpleNamespace(ExtendedSelection=3))
    Qt = SimpleNamespace(MouseButton=SimpleNamespace(RightButton=2))
    event = SimpleNamespace(button=lambda: 2, position=lambda: SimpleNamespace(toPoint=lambda: (0, 0)),
                            accept=lambda: None)
    item = SimpleNamespace(isSelected=lambda: True)
    calls = []
    self = SimpleNamespace(selectionMode=lambda: 3, itemAt=lambda _: item,
                           clearSelection=lambda: calls.append('cleared'),
                           setCurrentItem=lambda _: calls.append('current'))
    mouse_press = isolate(VIEW, '_SeparatedFileTree', 'mousePressEvent',
                          {'QAbstractItemView': fake, 'Qt': Qt})
    mouse_press(self, event)
    assert not calls


def test_batch_context_has_multiple_target_menu_and_no_single_file_fallback():
    assert "if selected_paths is not None and len(selected_paths) > 1:" in APP
    assert "self.perform_filesystem_batch_action(a, ps)" in APP
    assert "targets = context_paths(row, selected_rows, self.launcher.authored_items)" in VIEW
    assert 'pane.tree.setCurrentItem(item)' in VIEW  # only in non-middle branch


def test_copy_batch_populates_all_urls_for_explorer_and_paste(tmp_path):
    a = tmp_path / 'a.txt'; a.write_text('A')
    b = tmp_path / 'b.txt'; b.write_text('B')
    saved = []

    class Mime:
        def setUrls(self, urls): self.urls = urls
        def setData(self, key, data): self.effect = (key, data)

    app = SimpleNamespace(clipboard=lambda: SimpleNamespace(setMimeData=saved.append))
    runtime = {'Path': Path, 'QMimeData': Mime,
               'QUrl': SimpleNamespace(fromLocalFile=lambda p: p),
               'QApplication': app}
    method = isolate(APP, 'Launcher', 'perform_filesystem_batch_action', runtime)
    footer = SimpleNamespace(setText=lambda s: saved.append(('footer', s)))
    owner = SimpleNamespace(footer=footer,
                            _clear_previous_paste_feedback=lambda: None,
                            error=lambda s: saved.append(('error', s)))
    method(owner, 'copy', [a,b])
    assert len(saved[0].urls) == 2
    assert saved[0].urls == [str(a.resolve()), str(b.resolve())]
    assert saved[0].effect[1] == b'\x01\x00\x00\x00'
    assert saved[1][0] == 'footer'
    saved.clear()
    method(owner, 'cut', [a,b])
    assert saved[0].effect[1] == b'\x02\x00\x00\x00'


def test_expanded_paste_copies_all_selected_files_to_destination(tmp_path):
    src = tmp_path / 'src'; src.mkdir()
    dest = tmp_path / 'dest'; dest.mkdir()
    a = src / 'a.txt'; a.write_text('A')
    b = src / 'b.txt'; b.write_text('B')

    class Url:
        def __init__(self, p): self.path = str(p)
        def isLocalFile(self): return True
        def toLocalFile(self): return self.path

    class Mime:
        def hasUrls(self): return True
        def urls(self): return [Url(a), Url(b)]
        def formats(self): return []

    mime = Mime()
    cb = SimpleNamespace(mimeData=lambda: mime, clear=lambda: None)
    fake_app = SimpleNamespace(clipboard=lambda: cb)
    test_state = []
    view = SimpleNamespace(current_directory=lambda: str(dest),
                           refresh_middle=lambda: test_state.append('refreshed'))
    footer = SimpleNamespace(setText=lambda msg: test_state.append(msg))
    method = isolate(APP, 'Launcher', 'paste_into_expanded_directory',
                     {'Path': Path, 'QApplication': fake_app, 'clipboard_sources': clipboard_sources,
                      'is_cut_clipboard': is_cut_clipboard,
                      'is_virtual_file_clipboard': is_virtual_file_clipboard,
                      'make_paste_plan': make_paste_plan, 'paste_conflicts': paste_conflicts,
                      'paste_items': paste_items})
    owner = SimpleNamespace(expanded_view=view, footer=footer,
                            error=lambda message: test_state.append(('error', message)))
    method(owner)
    assert (dest / 'a.txt').read_text() == 'A'
    assert (dest / 'b.txt').read_text() == 'B'
    assert 'refreshed' in test_state
    assert not [x for x in test_state if isinstance(x, tuple) and x[0] == 'error']


def test_left_arrow_first_column_resets_to_first_row_not_files_root():
    fn = isolate(APP, 'Launcher', 'expanded_tree_key', {})
    code = ast.unparse(ast.parse(APP))
    # Assert structural intent, independent of real Qt tests on Windows.
    assert "elif pane is view.left:" in code
    assert "first = pane.tree.topLevelItem(0)" in code
    assert "view.choose_files(first, 0)" in code


def test_expanded_paste_button_and_reduced_density_icon():
    assert "self.paste_button = QPushButton('貼り付け', self.shared_header)" not in VIEW
    assert 'show_expanded_background_paste_menu' in VIEW
    assert "self.density_button.setIconSize(QSize(22, 22))" in VIEW
    # When focus is in another pane, the current row must show an outline,
    # not the old permanently-filled selection background.
    assert "QTreeWidget#expandedTree::item:selected:!active {{background:transparent;" in VIEW
    assert 'QStyle.StateFlag.State_Selected' in VIEW
    assert 'painter.drawRoundedRect(rect, 6.5, 6.5)' in VIEW
