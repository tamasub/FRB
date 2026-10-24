"""Same-folder copy behaves like Explorer but never touches the original."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pytest
from clipboard_paste import make_paste_plan, paste_items, next_copy_name


def test_same_folder_copy_file_and_numbering(tmp_path):
    original = tmp_path / '004.txt'
    original.write_text('original', encoding='utf-8')
    for expected in ('004 - コピー.txt', '004 - コピー (2).txt'):
        plan = make_paste_plan(tmp_path, [original], allow_existing=True,
                               duplicate_in_place=True)
        assert plan[0].target.name == expected
        assert paste_items(plan) == 1
        assert (tmp_path / expected).read_text(encoding='utf-8') == 'original'
        assert original.read_text(encoding='utf-8') == 'original'


def test_same_folder_directory_copy(tmp_path):
    original = tmp_path / '資料'
    original.mkdir()
    (original / 'hello.txt').write_text('A')
    plan = make_paste_plan(tmp_path, [original], duplicate_in_place=True)
    assert plan[0].target.name == '資料 - コピー'
    assert paste_items(plan) == 1
    assert (tmp_path / '資料 - コピー' / 'hello.txt').read_text() == 'A'
    assert (original / 'hello.txt').read_text() == 'A'


def test_same_folder_multi_file_copy(tmp_path):
    paths = [tmp_path / 'a.txt', tmp_path / 'b.txt']
    for i, path in enumerate(paths):
        path.write_text(str(i))
    plan = make_paste_plan(tmp_path, paths, duplicate_in_place=True)
    assert [p.target.name for p in plan] == ['a - コピー.txt', 'b - コピー.txt']
    assert paste_items(plan) == 2
    assert len(list(tmp_path.iterdir())) == 4


def test_cut_to_same_folder_is_not_a_duplicate(tmp_path):
    src = tmp_path / '004.txt'
    src.write_text('untouched')
    with pytest.raises(ValueError, match='同じ場所'):
        make_paste_plan(tmp_path, [src], allow_existing=True, duplicate_in_place=False)
    assert sorted(p.name for p in tmp_path.iterdir()) == ['004.txt']


def test_no_symlinks_in_duplicate(tmp_path):
    orig = tmp_path / 'a.txt'
    orig.write_text('x')
    link = tmp_path / 'sym.txt'
    try:
        link.symlink_to(orig)
    except OSError:
        pytest.skip('symlink creation is unavailable')
    with pytest.raises(ValueError, match='通常のファイル'):
        next_copy_name(link)


def test_other_folder_paste_existing_conflict_not_auto_renamed(tmp_path):
    source_dir, dest_dir = tmp_path / 'src', tmp_path / 'dest'
    source_dir.mkdir(); dest_dir.mkdir()
    source = source_dir / 'a.txt'
    source.write_text('source')
    (dest_dir / 'a.txt').write_text('destination')
    plan = make_paste_plan(dest_dir, [source], allow_existing=True,
                           duplicate_in_place=True)
    assert plan[0].target.name == 'a.txt'
