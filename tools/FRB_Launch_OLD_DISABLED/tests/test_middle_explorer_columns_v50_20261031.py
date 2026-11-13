"""v50: folder metadata columns and persistent/reorderable Explorer header."""
from pathlib import Path
import sys
import os
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from middle_folder_filter import filter_sort_folder_rows, sort_mode_for_header


def row(path):
    return {'title': path.name, '_file': str(path),
            'item_kind': 'directory' if path.is_dir() else 'command'}


def test_metadata_columns_always_populated_and_readable(tmp_path):
    folder = tmp_path / 'abc'; folder.mkdir()
    file = tmp_path / 'test.zip'; file.write_bytes(b'x' * 2048)
    for mode in ('name', 'date_desc', 'size_desc', 'type_asc'):
        rows = filter_sort_folder_rows([row(file), row(folder)], mode=mode)
        assert rows[0]['_middle_type'] == 'ファイル フォルダー'
        assert rows[0]['_middle_date']
        assert rows[0]['_middle_size'] == ''
        assert rows[1]['_middle_size'] == '2 KB'
        assert rows[1]['_middle_type'] == 'ZIP ファイル'
        assert rows[1]['_middle_date'].count('/') == 2


def test_sort_clicks_toggle_and_blank_is_inert():
    assert sort_mode_for_header(0, 'name') == 'name_desc'
    assert sort_mode_for_header(0, 'size_desc') == 'name'
    assert sort_mode_for_header(1, 'name') == 'date_desc'
    assert sort_mode_for_header(1, 'date_desc') == 'date_asc'
    assert sort_mode_for_header(2, 'name') == 'size_desc'
    assert sort_mode_for_header(2, 'size_desc') == 'size_asc'
    assert sort_mode_for_header(3, 'name') == 'type_asc'
    assert sort_mode_for_header(3, 'type_asc') == 'type_desc'
    assert sort_mode_for_header(4, 'name') is None


def test_sorting_by_date_size_name_and_type(tmp_path):
    older = tmp_path / 'beta.txt'; older.write_bytes(b'x')
    newer = tmp_path / 'alpha.zip'; newer.write_bytes(b'x' * 10000)
    os.utime(older, (time.time() - 3600, time.time() - 3600))
    names = lambda mode: [r['title'] for r in filter_sort_folder_rows([row(older), row(newer)], mode=mode)]
    assert names('name') == ['alpha.zip', 'beta.txt']
    assert names('name_desc') == ['beta.txt', 'alpha.zip']
    assert names('date_desc') == ['alpha.zip', 'beta.txt']
    assert names('date_asc') == ['beta.txt', 'alpha.zip']
    assert names('size_desc') == ['alpha.zip', 'beta.txt']
    assert names('size_asc') == ['beta.txt', 'alpha.zip']
    assert names('type_asc') == ['beta.txt', 'alpha.zip']
    assert names('type_desc') == ['alpha.zip', 'beta.txt']


def test_view_wiring_and_appearance():
    view = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
    app = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    assert "tree.setHeaderLabels(['名前', '更新日', 'サイズ', '種類', ''])" in view
    assert 'header.setSectionsMovable(True)' in view
    assert 'header.sectionClicked.connect(self._middle_header_clicked)' in view
    assert 'header.sectionResized.connect(self._save_middle_header_state)' in view
    assert 'header.sectionMoved.connect(self._save_middle_header_state)' in view
    assert 'expanded_middle_header_state_v50' in view
    assert 'header.restoreState(saved)' in view
    assert 'self.middle.tree.header().saveState()' in view
    assert '#81928a' in view and '#a1afa8' in view
    assert 'self.middle_sort_button = ' not in view
    assert 'view.middle_sort_button' not in app
    assert 'self.expanded_view.middle_sort_button' not in app
    assert "'directory', 'sort', 'bookmarks'" not in (ROOT / 'src/remote_navigation.py').read_text(encoding='utf-8')
