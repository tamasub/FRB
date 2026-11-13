"""Regression: explicitly indexed Windows drive roots must not go missing."""
import ast
from pathlib import Path
from unittest.mock import patch

import file_index as fi

ROOT = Path(__file__).resolve().parents[1]


def test_windows_drive_root_detection_handles_long_paths():
    for drive in ('F:\\', 'F:/', 'C:\\', '\\\\?\\F:\\'):
        assert fi._windows_drive_root(drive), drive
    for subdirectory in ('F:', 'F:\\FRB', 'F:\\FRB\\tools',
                         'C:\\Users', '\\\\server\\share', '/tmp'):
        assert not fi._windows_drive_root(subdirectory), subdirectory


def test_hidden_root_directory_is_still_excluded(tmp_path):
    root = tmp_path / 'hidden_folder'
    root.mkdir()
    (root / 'private.md').write_text('test')
    opts = fi.load_options(tmp_path / 'missing.json')
    opts['index_target'] = 'both'
    with patch.object(fi, 'is_hidden_attribute', side_effect=lambda path: str(path) == str(root)):
        result = fi._root_scan(str(root), opts)
    assert result['count'] == 0
    assert '隠し属性' in result['warnings'][0]


def test_drive_root_ignores_root_hidden_flag_but_still_hides_child_files(tmp_path):
    """Simulate an F drive on Linux; its Windows path has no local filesystem."""
    physical_root = tmp_path / 'fake_F_drive'
    physical_root.mkdir()
    (physical_root / 'visible.md').write_text('safe')
    (physical_root / 'hidden.md').write_text('secret')
    opts = fi.load_options(tmp_path / 'missing.json')
    opts['index_target'] = 'both'
    def hidden_flag(path):
        return str(path) in (str(physical_root), str(physical_root / 'hidden.md'))
    with patch.object(fi, '_windows_scan_path', return_value=str(physical_root)), \
         patch.object(fi, 'is_hidden_attribute', side_effect=hidden_flag):
        result = fi._root_scan('F:\\', opts)
    assert result['count'] == 2  # eligible file plus its folder
    assert 'visible.md' in {row[1] for row in result['rows']}
    assert 'hidden.md' not in {row[1] for row in result['rows']}


def test_index_revision_rechecks_existing_drive_snapshots(tmp_path):
    root = tmp_path / 'drive'
    root.mkdir()
    (root / 'ok.md').write_text('test')
    opts = fi.load_options(tmp_path / 'missing.json')
    opts['index_target'] = 'both'
    db = tmp_path / 'index.db'
    assert fi.refresh_index(db, [str(root)], opts)['count'] == 2
    import sqlite3
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE index_roots SET options_digest='old_implementation'")
    result = fi.refresh_index(db, [str(root)], opts)
    assert result['changed_roots'] == [str(root)]
    assert result['count'] == 2


def test_diagnostic_root_counts_are_logged():
    src = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    ast.parse(src)
    assert 'FILE_INDEX root_stats root=%s count=%s excluded=%s' in src
    assert 'FILE_INDEX empty_root root=%s' in src
