"""Explorer clipboard copy/cut: safe non-overwriting filesystem paste."""
from pathlib import Path
import ast
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from clipboard_paste import clipboard_sources, is_cut_clipboard, make_paste_plan, paste_items


class FakeUrl:
    def __init__(self, path, local=True):
        self.path, self.local = path, local

    def isLocalFile(self):
        return self.local

    def toLocalFile(self):
        return str(self.path)


class FakeMime:
    def __init__(self, urls=None, effect=None):
        self._urls = urls or []
        self._effect = effect

    def hasUrls(self):
        return bool(self._urls)

    def urls(self):
        return self._urls

    def formats(self):
        return ['application/x-qt-windows-mime;value="Preferred DropEffect"'] if self._effect is not None else []

    def data(self, fmt):
        return self._effect.to_bytes(4, 'little')


def test_only_existing_file_urls_are_clipboard_candidates(tmp_path):
    file = tmp_path / 'a.txt'
    file.write_text('source', encoding='utf-8')
    mime = FakeMime([FakeUrl(file), FakeUrl(file), FakeUrl('https://x', local=False)])
    assert clipboard_sources(mime) == [file]
    assert clipboard_sources(None) == []
    assert clipboard_sources(FakeMime()) == []


def test_explorer_cut_and_copy_detection():
    assert not is_cut_clipboard(None)
    assert not is_cut_clipboard(FakeMime(effect=1))
    assert is_cut_clipboard(FakeMime(effect=2))
    assert not is_cut_clipboard(FakeMime())


def test_copy_file_and_directory_with_contents(tmp_path):
    src = tmp_path / 'src'
    dst = tmp_path / 'dst'
    src.mkdir()
    dst.mkdir()
    file = src / 'a.txt'
    file.write_text('hello', encoding='utf-8')
    folder = src / 'sub'
    folder.mkdir()
    (folder / 'inner.txt').write_text('nested', encoding='utf-8')
    plan = make_paste_plan(dst, [file, folder])
    assert paste_items(plan) == 2
    assert (dst / 'a.txt').read_text(encoding='utf-8') == 'hello'
    assert (dst / 'sub' / 'inner.txt').read_text(encoding='utf-8') == 'nested'
    assert file.exists() and folder.exists()  # Copy must retain sources.


def test_cut_move_removes_source(tmp_path):
    src, dst = tmp_path / 'src', tmp_path / 'dst'
    src.mkdir(); dst.mkdir()
    file = src / 'cut.txt'
    file.write_text('data', encoding='utf-8')
    assert paste_items(make_paste_plan(dst, [file]), move=True) == 1
    assert not file.exists()
    assert (dst / 'cut.txt').read_text(encoding='utf-8') == 'data'


def test_existing_target_blocks_entire_batch_and_never_overwrites(tmp_path):
    src, dst = tmp_path / 'src', tmp_path / 'dst'
    src.mkdir(); dst.mkdir()
    one = src / 'one.txt'; two = src / 'two.txt'
    one.write_text('one'); two.write_text('two')
    (dst / 'two.txt').write_text('keep')
    with pytest.raises(FileExistsError, match='上書きしません'):
        make_paste_plan(dst, [one, two])
    assert not (dst / 'one.txt').exists()
    assert (dst / 'two.txt').read_text() == 'keep'


def test_reject_copying_directory_into_own_descendant(tmp_path):
    src = tmp_path / 'folder'; nested = src / 'nested'
    nested.mkdir(parents=True)
    with pytest.raises(ValueError, match='自分自身'):
        make_paste_plan(nested, [src])


def test_malformed_source_destination_and_duplicate_names(tmp_path):
    dst = tmp_path / 'dst'; dst.mkdir()
    with pytest.raises(ValueError, match='コピー元'):
        make_paste_plan(dst, [tmp_path / 'missing'])
    with pytest.raises(ValueError, match='Explorer'):
        make_paste_plan(dst, [])
    a = tmp_path / 'a'; b = tmp_path / 'b'; a.mkdir(); b.mkdir()
    f1 = a / 'same.txt'; f2 = b / 'same.txt'
    f1.write_text('1'); f2.write_text('2')
    with pytest.raises(ValueError, match='重複'):
        make_paste_plan(dst, [f1, f2])


def test_button_only_on_directory_and_correct_refresh_contract():
    source = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    menu = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'CascadeMenu')
    setup = next(x for x in menu.body if isinstance(x, ast.FunctionDef) and x.name == '_ensure_local_filter')
    snippet = ast.get_source_segment(source, setup)
    assert 'self._folder_container_row() is not None' in snippet
    assert "QPushButton('貼り付け', container)" in snippet
    assert "self.launcher.paste_into_directory(self)" in snippet
    launcher = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'Launcher')
    paste = next(x for x in launcher.body if isinstance(x, ast.FunctionDef) and x.name == 'paste_into_directory')
    code = ast.get_source_segment(source, paste)
    assert 'make_paste_plan(destination, sources)' in code
    assert 'paste_items(plan, move=move)' in code
    assert 'self.refresh_pasted_directory(m)' in code
