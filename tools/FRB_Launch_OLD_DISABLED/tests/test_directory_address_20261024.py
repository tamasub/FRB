"""Explorer-style FRB Launch address bar contract; no Windows/Qt dependency."""
import ast
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from directory_address import (normalized_directory, breadcrumb_segments,
                               directory_row, row_directory, compact_segments)
from focus_session import normalize_focus_state


@pytest.mark.parametrize(('raw','expected'), [
    (r'F:\FRB\tools\FRBStudio_App\data', r'F:\FRB\tools\FRBStudio_App\data'),
    (r'F:/FRB/tools/../tools/data', r'F:\FRB\tools\data'),
    ('F:', None),
    (r'F:FRB', None),
    (r'\FRB\tools', None),
    ('', None),
    ('\x00F:\\Folder', None),
    ('"C:\\Program Files"', r'C:\Program Files'),
])
def test_absolute_path_contract(raw, expected):
    assert normalized_directory(raw) == expected


def test_ancestors_are_full_paths_even_above_launcher_shortcut():
    parts = breadcrumb_segments(r'F:\FRB\tools\FRBStudio_App\data')
    assert [text for text, _ in parts] == ['F:\\', 'FRB', 'tools', 'FRBStudio_App', 'data']
    assert [target for _, target in parts] == [
        'F:\\', r'F:\FRB', r'F:\FRB\tools', r'F:\FRB\tools\FRBStudio_App',
        r'F:\FRB\tools\FRBStudio_App\data',
    ]
    # This is the requested ability: no restriction to FRBStudio_App root.
    assert parts[1][1] == r'F:\FRB'


def test_windows_drive_root_and_unc_share_boundary():
    assert breadcrumb_segments('F:\\') == [('F:\\','F:\\')]
    result = breadcrumb_segments(r'\\server\share\work\docs')
    assert result[0] == ('\\\\server\\share\\', '\\\\server\\share\\')
    assert result[-1] == ('docs', r'\\server\share\work\docs')
    assert len(result) == 3


def test_category_or_file_has_no_filesystem_breadcrumb():
    assert row_directory({'item_kind': 'category', 'launch_browse_target': r'F:\Work'}) is None
    assert row_directory({'item_kind': 'command', 'launch_browse_target': r'F:\Work'}) is None
    assert row_directory({'item_kind': 'directory', 'launch_browse_target': r'%studio_root%'},
                         lambda s: s.replace('%studio_root%',r'F:\FRB\tools')) == r'F:\FRB\tools'


def test_synthetic_row_can_be_passed_to_existing_directory_browser():
    row = directory_row(r'F:\FRB')
    assert row['_address_synthetic']
    assert row['item_kind'] == 'directory'
    assert row['launch_browse_target'] == r'F:\FRB'
    assert row_directory(row) == r'F:\FRB'


def test_compact_path_prefers_drive_and_nearest_parents():
    segments = breadcrumb_segments(r'F:\FRB\tools\FRBStudio_App\data')
    small = compact_segments(segments, 180, lambda txt: len(txt) * 8 + 10)
    assert small[0] == ('F:\\','F:\\')
    assert small[-1][0] == 'data'
    assert ('…', None) in small
    full = compact_segments(segments, 2000, lambda txt: len(txt) * 8 + 10)
    assert full == segments


def test_restore_same_real_directory_even_if_outside_shortcut_tree():
    state = normalize_focus_state({'area':'directory','middle_path':r'F:\FRB',
                                   'path_ids':['F:\\FRB'], 'mode':'expanded'})
    assert state['middle_path'] == r'F:\FRB'
    assert normalize_focus_state({'middle_path':'relative\u005cdir'}).get('middle_path') is None
    assert normalize_focus_state({'middle_path':'C:relative'}).get('middle_path') is None


def test_address_control_is_in_combined_explorer_header_and_does_not_steal_arrows():
    source = (ROOT/'src/expanded_view.py').read_text(encoding='utf8')
    app = (ROOT/'src/app.py').read_text(encoding='utf8')
    ast.parse(source)
    ast.parse(app)
    for fragment in ('class DirectoryAddressBar(', 'self.editor.selectAll',
                     'Qt.Key.Key_Escape', 'QEvent.Type.FocusOut',
                     'self.go_to_directory', 'self.address_bar.set_directory',
                     'shared_layout.addWidget(self.address_bar, 1)',
                     'self.path = [directory_row(target)]'):
        assert fragment in source
    assert "'middle_path': view.current_directory()" in app
    assert 'os.path.isdir(stored_path)' in app
    assert 'self._show_hidden(btn, entries)' in source
    assert 'menu.exec(button.mapToGlobal(' in source
