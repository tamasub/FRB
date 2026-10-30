"""New folder-only filter/sort contract (does not require Qt)."""
from pathlib import Path
import os
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from middle_folder_filter import filter_sort_folder_rows, format_size, SORT_LABELS


def _row(path):
    return dict(title=path.name, item_id=str(path), _file=str(path),
                item_kind='directory' if path.is_dir() else 'command')


def test_folder_search_reuses_boolean_grammar_and_is_local(tmp_path):
    for name in ('image_01.png', 'image_02.png', 'zenn.md', 'article_01.md'):
        (tmp_path / name).write_text(name, encoding='utf-8')
    rows = [_row(path) for path in tmp_path.iterdir()]
    assert [x['title'] for x in filter_sort_folder_rows(rows, '(image or zenn)')] == [
        'image_01.png', 'image_02.png', 'zenn.md']
    assert [x['title'] for x in filter_sort_folder_rows(rows, 'image png')] == [
        'image_01.png', 'image_02.png']
    assert [x['title'] for x in filter_sort_folder_rows(rows, '*.md')] == [
        'article_01.md', 'zenn.md']
    # Filtering changes only result collection, not originals or disk.
    assert len(rows) == 4 and not any('_middle_detail' in row for row in rows)


def test_modes_and_detail_display(tmp_path):
    small = tmp_path / 'small.md'
    big = tmp_path / 'big.md'
    small.write_bytes(b'a' * 10)
    big.write_bytes(b'b' * 2200)
    older = time.time() - 3600
    newer = older + 1200
    os.utime(big, (older, older))
    os.utime(small, (newer, newer))
    rows = [_row(x) for x in (small, big)]
    def order(mode):
        return filter_sort_folder_rows(rows, mode=mode)
    assert [x['title'] for x in order('name')] == ['big.md', 'small.md']
    assert [x['title'] for x in order('date_desc')] == ['small.md', 'big.md']
    assert [x['title'] for x in order('date_asc')] == ['big.md', 'small.md']
    assert [x['title'] for x in order('size_desc')] == ['big.md', 'small.md']
    assert [x['title'] for x in order('size_asc')] == ['small.md', 'big.md']
    assert all(x['_middle_detail_mode'] == 'date' and '/' in x['_middle_detail']
               for x in order('date_desc'))
    assert all(x['_middle_detail_mode'] == 'size' and 'B' in x['_middle_detail']
               for x in order('size_desc'))
    assert all(x['_middle_detail'] == '' for x in order('name'))


def test_folder_rows_stay_navigable_and_first(tmp_path):
    folder = tmp_path / 'zzz'
    folder.mkdir()
    file = tmp_path / 'aaa.txt'
    file.write_text('test')
    for mode in SORT_LABELS:
        result = filter_sort_folder_rows([_row(file), _row(folder)], mode=mode)
        assert result[0]['title'] == 'zzz'
        assert result[0]['item_kind'] == 'directory'
        assert not result[0]['_middle_detail'] if mode.startswith('size') else True


def test_size_format():
    assert format_size(None) == ''
    assert format_size(0) == '0 B'
    assert format_size(1024) == '1.0 KB'
    assert format_size(2 * 1024 ** 2) == '2.0 MB'
