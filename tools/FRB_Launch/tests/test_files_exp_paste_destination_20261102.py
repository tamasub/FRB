"""Selected-folder paste semantics, including explicit multi-folder blocking."""
import ast
from pathlib import Path
from types import SimpleNamespace
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from paste_destination import choose_paste_destination, AmbiguousPasteTarget
from clipboard_paste import clipboard_sources, is_cut_clipboard, make_paste_plan, paste_conflicts, paste_items
from virtual_clipboard_paste import is_virtual_file_clipboard

APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
FILES_EXP = (ROOT / 'src/remote_files_explorer.py').read_text(encoding='utf-8')
VIEW = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')


def extract(method, extra):
    clazz = next(c for c in ast.parse(APP).body
                 if isinstance(c, ast.ClassDef) and c.name == 'Launcher')
    fn = next(f for f in clazz.body if isinstance(f, ast.FunctionDef) and f.name == method)
    scope = dict(extra)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), '<isolated>', 'exec'), scope)
    return scope[method]


def test_selection_resolver_obeys_explorer_and_blocks_ambiguity(tmp_path):
    breadcrumb = tmp_path / 'open'; breadcrumb.mkdir()
    one = breadcrumb / 'one'; one.mkdir()
    two = breadcrumb / 'two'; two.mkdir()
    file = breadcrumb / 'readme.md'; file.write_text('ok')
    assert choose_paste_destination(breadcrumb) == breadcrumb
    assert choose_paste_destination(breadcrumb, [file]) == breadcrumb
    assert choose_paste_destination(breadcrumb, [file, file]) == breadcrumb
    assert choose_paste_destination(breadcrumb, [one]) == one
    for selected in ((one, two), (one, file), (file, one, two)):
        try:
            choose_paste_destination(breadcrumb, selected)
        except AmbiguousPasteTarget as ex:
            assert 'フォルダー' in str(ex)
        else:
            raise AssertionError(f'unsafe destination was accepted: {selected}')


def test_actual_paste_prefers_selected_folder_and_blocks_multi(tmp_path):
    source_dir = tmp_path / 'source'; source_dir.mkdir()
    source = source_dir / 'data.md'; source.write_text('payload', encoding='utf-8')
    current = tmp_path / 'current'; current.mkdir()
    a = current / 'folder_a'; a.mkdir()
    b = current / 'folder_b'; b.mkdir()
    file = current / 'existing.txt'; file.write_text('old')

    class Url:
        def isLocalFile(self): return True
        def toLocalFile(self): return str(source)

    mime = SimpleNamespace(hasUrls=lambda: True, urls=lambda: [Url()], formats=lambda: [])
    clip = SimpleNamespace(mimeData=lambda: mime, clear=lambda: None)
    app = SimpleNamespace(clipboard=lambda: clip)
    scope = {'Path': Path, 'QApplication': app, 'clipboard_sources': clipboard_sources,
             'is_cut_clipboard': is_cut_clipboard,
             'is_virtual_file_clipboard': is_virtual_file_clipboard,
             'make_paste_plan': make_paste_plan, 'paste_conflicts': paste_conflicts,
             'paste_items': paste_items}
    paste = extract('paste_into_expanded_directory', scope)
    selection = [a]
    messages = []
    view = SimpleNamespace(current_directory=lambda: str(current),
                           middle_selected_paths=lambda: selection,
                           refresh_middle=lambda: messages.append('refresh'))
    owner = SimpleNamespace(expanded_view=view,
                            footer=SimpleNamespace(setText=messages.append),
                            _warn_ambiguous_paste_target=lambda m: messages.append(('warning', str(m))),
                            error=lambda m: messages.append(('error', str(m))))
    paste(owner)
    assert (a / source.name).read_text() == 'payload'
    assert not (current / source.name).exists()
    assert not (b / source.name).exists()

    # Multiple selected folders must never begin even one copy or move.
    selection[:] = [a, b]
    (a / source.name).unlink()
    before = len(messages)
    paste(owner)
    assert not (a / source.name).exists()
    assert not (b / source.name).exists()
    assert any(isinstance(x, tuple) and x[0] == 'warning' for x in messages[before:])

    # Multiple selected files: paste into breadcrumb folder as fallback.
    selection[:] = [file]
    paste(owner)
    assert (current / source.name).read_text() == 'payload'


def test_context_menu_and_shortcut_call_same_paste_core():
    assert 'self.paste_into_expanded_directory()' in APP  # Ctrl+V
    assert "self._paste_from_context_menu(parent)" in APP
    assert 'self.expanded_view.middle_selected_paths()' in APP
    assert 'target_folder=clicked' in APP
    assert 'pane.tree.clearSelection()' in VIEW  # blank-area explicit choice


def test_exp_header_uses_remote_spacing():
    assert 'layout.setContentsMargins(5, 5, 5, 5)' in FILES_EXP
    assert 'layout.setSpacing(3)' in FILES_EXP
    assert 'header_row.setContentsMargins(2, 2, 2, 2)' in FILES_EXP
    assert 'self.tree.setIndentation(18)' in FILES_EXP


def test_cascade_context_paste_can_target_right_clicked_subfolder(tmp_path):
    current = tmp_path / 'current'; current.mkdir()
    target = current / 'chosen'; target.mkdir()
    source_dir = tmp_path / 'src'; source_dir.mkdir()
    source = source_dir / 'answer.md'; source.write_text('content')
    events = []
    fn = extract('paste_into_directory', {
        'Path': Path, 'QApplication': SimpleNamespace(clipboard=lambda: SimpleNamespace(
            mimeData=lambda: object(), clear=lambda: None)),
        'clipboard_sources': lambda mime: [source],
        'is_cut_clipboard': lambda mime: False,
        'is_virtual_file_clipboard': lambda mime: False,
        'make_paste_plan': make_paste_plan, 'paste_conflicts': paste_conflicts,
        'paste_items': paste_items,
        'pasted_paths_for': lambda dest, names: [str(dest / name) for name in names],
        'QTimer': SimpleNamespace(singleShot=lambda delay, action: events.append('refresh_scheduled'))
    })
    popup = SimpleNamespace(_folder_container_row=lambda: {
        'launch_browse_target': str(current)})
    owner = SimpleNamespace(
        expander=lambda: SimpleNamespace(expand=lambda path: path),
        footer=SimpleNamespace(setText=events.append),
        refresh_pasted_directory=lambda *a, **kw: events.append('refresh'),
        error=lambda msg: events.append(('error', str(msg))))
    fn(owner, popup, destination_override=target)
    assert (target / source.name).read_text() == 'content'
    assert not (current / source.name).exists()
    assert 'refresh_scheduled' in events
    assert not any(isinstance(e, tuple) and e[0] == 'error' for e in events)


def test_context_dispatch_uses_explicit_selected_folder():
    dispatch = extract('_paste_from_context_menu', {})
    calls=[]
    parent=object()
    host=SimpleNamespace(
        _context_paste_enabled=lambda p: True,
        _paste_context_destination=lambda p: 'expanded',
        paste_into_expanded_directory=lambda **kw: calls.append(('expanded', kw)),
        paste_into_directory=lambda p, **kw: calls.append(('cascade', kw)),
    )
    dispatch(host, parent, target_folder='F:/FRB')
    host._paste_context_destination=lambda p: 'cascade'
    dispatch(host, parent, target_folder='F:/FRB')
    assert calls == [('expanded', {'destination_override':'F:/FRB'}),
                     ('cascade', {'destination_override':'F:/FRB'})]
