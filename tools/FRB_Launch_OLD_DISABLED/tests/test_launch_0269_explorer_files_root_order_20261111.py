"""Explorer native file drops + Files Exp registered-root-only Move contract."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from launch_menu_registration import mime_sources, normalize_sources, records_for_sources
from registered_root_studio import authored_files_root_identity
from launch_json_move import registered_root_reorder_placement


class Url:
    def __init__(self, value, local=False):
        self.value, self.local = value, local
    def isLocalFile(self): return self.local
    def toLocalFile(self): return self.value
    def toString(self): return self.value


class Mime:
    def __init__(self, urls=(), payload=None, text=None):
        self._urls = urls
        self.payload = payload or {}
        self._text = text
    def hasUrls(self): return bool(self._urls)
    def formats(self): return list(self.payload)
    def urls(self): return self._urls
    def hasFormat(self, name): return name in self.payload
    def data(self, name): return self.payload[name]
    def hasText(self): return self._text is not None
    def text(self): return self._text or ''


def test_qt_explorer_file_drop_registers_single_and_multiple_files(tmp_path):
    a, b = tmp_path / 'Book1.xlsx', tmp_path / 'note.txt'
    a.write_bytes(b'xlsx')
    b.write_bytes(b'txt')
    mime = Mime(urls=[Url(str(a), local=True), Url(str(b), local=True)])
    records = records_for_sources(normalize_sources(mime_sources(mime)))
    assert len(records) == 2
    assert [r['item_kind'] for r in records] == ['command', 'command']
    assert [r['launch_actions'][0]['launch_target'] for r in records] == [str(a), str(b)]


def test_uri_list_fallback_registers_file_when_qt_urls_empty(tmp_path):
    file = tmp_path / 'file with space.xlsx'
    file.write_bytes(b'ok')
    mime = Mime(payload={'text/uri-list': (file.as_uri() + '\r\n').encode('utf-8')})
    sources = normalize_sources(mime_sources(mime))
    assert len(sources) == 1 and sources[0]['kind'] == 'file'
    assert Path(sources[0]['value']) == file


def test_local_path_text_fallback_when_urls_empty(tmp_path):
    file = tmp_path / 'a.txt'
    file.write_text('ok', encoding='utf-8')
    assert mime_sources(Mime(text=str(file))) == [{'value': str(file), 'title': ''}]


def test_windows_filename_w_fallback_and_dedupe():
    raw = r'C:\Users\someone\Documents\Book1.xlsx'
    fmt = 'application/x-qt-windows-mime;value="FileNameW"'
    assert mime_sources(Mime(payload={fmt: (raw + '\0').encode('utf-16-le')})) == [
        {'value': raw}]
    assert mime_sources(Mime(urls=[Url(raw, True)],
                             payload={fmt: (raw + '\0').encode('utf-16-le')})) == [
        {'value': raw}]


def test_multi_file_qt_urls_win_over_stale_native_short_paths(tmp_path):
    """Explorer exposes CF_HDROP plus an 8.3 alias; the alias is NOT a third file."""
    first = tmp_path / '_make_launch_zip.bat'
    second = tmp_path / 'AGENTS.md'
    first.write_text('echo ok', encoding='utf-8')
    second.write_text('# readme', encoding='utf-8')
    stale_native = r'C:\Users\USER~1\OneDrive\_tmp\_MAKE_~1.BAT'
    mime = Mime(
        urls=[Url(str(first), local=True), Url(str(second), local=True)],
        payload={
            'application/x-qt-windows-mime;value="FileNameW"':
                (stale_native + '\0').encode('utf-16-le'),
            'application/x-qt-windows-mime;value="FileName"':
                stale_native.encode('cp1252') + b'\0',
        })
    sources = normalize_sources(mime_sources(mime))
    assert [Path(src['value']).name for src in sources] == [first.name, second.name]


def test_raw_uri_list_wins_over_short_filename_when_qt_urls_absent(tmp_path):
    target = tmp_path / '新しいファイル.txt'
    target.write_text('ok', encoding='utf-8')
    mime = Mime(payload={
        'text/uri-list': (target.as_uri() + '\r\n').encode('utf-8'),
        'application/x-qt-windows-mime;value="FileNameW"':
            (r'C:\USER~1\BAD~1.TXT' + '\0').encode('utf-16-le')})
    sources = normalize_sources(mime_sources(mime))
    assert len(sources) == 1 and Path(sources[0]['value']) == target


def test_unicode_filename_w_takes_precedence_over_ansi_variant():
    unicode_path = r'C:\Users\user\Documents\作業メモ.txt'
    ansi_path = r'C:\Users\USER~1\DOCUME~1\bad.txt'
    mime = Mime(payload={
        'application/x-qt-windows-mime;value="FileNameW"':
            (unicode_path + '\0').encode('utf-16-le'),
        'application/x-qt-windows-mime;value="FileName"':
            (ansi_path + '\0').encode('cp1252')})
    assert mime_sources(mime) == [{'value': unicode_path}]


def test_untrusted_non_filename_payload_not_accepted():
    assert mime_sources(Mime(text='powershell -ExecutionPolicy Bypass')) == []
    assert mime_sources(Mime(payload={'application/x-qt-windows-mime;value="FileNameW"':
                                    'filename.xlsx\0'.encode('utf-16-le')})) == []


def _registered_data(item='root1', parent='folders', kind='directory', pc=False):
    return {'pc': pc, 'path': r'F:\FRB', 'studio_identity': {
        'source': 'launch_json', 'page_id': 'system', 'parent_item_id': parent,
        'item_id': item, 'item_kind': kind, 'node_id': f'item:system:{item}'}}


def test_registered_exp_root_is_only_physical_path_reorder_candidate():
    assert authored_files_root_identity(_registered_data(), 'system', 'folders') == (
        'system', 'root1')
    assert authored_files_root_identity(_registered_data(pc=True), 'system', 'folders') is None
    assert authored_files_root_identity(_registered_data(parent='root1'), 'system', 'folders') is None
    assert authored_files_root_identity(_registered_data(kind='category'), 'system', 'folders') is None
    assert authored_files_root_identity(_registered_data(), 'other_page', 'folders') is None
    assert authored_files_root_identity({'path': r'F:\FRB\sub'}, 'system', 'folders') is None


def test_files_exp_root_move_only_reorders_siblings():
    kwargs = {'page_id': 'system', 'parent_id': 'folders'}
    assert registered_root_reorder_placement(('system', 'one'), ('system', 'two'),
                                              fraction=0.1, **kwargs) == {
        'group_id': 'system', 'parent_id': 'folders', 'position': 'before',
        'anchor_id': 'two'}
    assert registered_root_reorder_placement(('system', 'one'), ('system', 'two'),
                                              fraction=0.9, **kwargs)['position'] == 'after'
    assert registered_root_reorder_placement(('system', 'one'), None, **kwargs) == {
        'group_id': 'system', 'parent_id': 'folders', 'position': 'end'}
    assert registered_root_reorder_placement(('system', 'one'), ('other', 'two'),
                                              **kwargs) is None
    assert registered_root_reorder_placement(('other', 'one'), None, **kwargs) is None


def test_physical_descendant_cannot_start_move_and_pc_has_separator():
    src = (ROOT / 'src/remote_files_explorer.py').read_text(encoding='utf-8')
    assert 'item.parent() is not None' in src
    assert "_active_registered_root_drag = registered_root if registered_root == source else None" in src
    assert 'source != active_root' in src
    assert 'if index.isValid() and target is None:' in src
    assert "data.get('pc')" in src and "QColor('#b8c7bd')" in src


def test_registration_and_move_mime_are_distinct():
    src = (ROOT / 'src/remote_files_explorer.py').read_text(encoding='utf-8')
    assert 'if event.mimeData().hasFormat(MOVE_MIME):' in src
    assert 'self.perform_registration_drop(target, event.mimeData())' not in src
    assert 'panel.perform_registration_drop(target, event.mimeData())' in src


def test_native_indexed_windows_filenames_are_accepted():
    one = r'C:\\Users\\user\\Documents\\001.txt'
    two = r'C:\\Users\\user\\Documents\\002.txt'
    base = 'application/x-qt-windows-mime;value="FileNameW"'
    mime = Mime(payload={base+';index=0': (one+'\0').encode('utf-16-le'),
                         base+';index=1': (two+'\0').encode('utf-16-le')})
    assert [e['value'] for e in mime_sources(mime)] == [one, two]
