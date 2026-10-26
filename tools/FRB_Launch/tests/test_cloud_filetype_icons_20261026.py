"""Regression coverage for file-type icons in cloud-backed Windows folders.

No PySide6 or cloud drive is needed for the deterministic lookup tests.
The actual association returned by Windows Shell still needs a Windows smoke test.
"""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from file_icon_policy import icon_lookup


def _file_row(path):
    return {'item_kind': 'command', '_file': path, 'icon_key': 'file'}


def test_cloud_offline_excel_uses_extension_without_file_probe(monkeypatch):
    # If a cloud placeholder was off-line, any stat call here would be a bug.
    import pathlib
    monkeypatch.setattr(pathlib.Path, 'is_file', lambda self: (_ for _ in ()).throw(AssertionError('stat not allowed')))
    assert icon_lookup(_file_row(r'C:\Users\人名\Box\チーム 資料\月次 報告.xlsx')) == ('type', '.xlsx')
    assert icon_lookup(_file_row(r'C:\Users\人名\OneDrive - 会社名\SharePoint\売上.xlsm')) == ('type', '.xlsm')
    assert icon_lookup(_file_row(r'C:\Users\人名\Documents\月次 報告.xlsx')) == ('type', '.xlsx')


def test_casefolded_extension_and_other_office_types():
    assert icon_lookup(_file_row(r'C:\Box\チーム 資料\説明.DOCX')) == ('type', '.docx')
    assert icon_lookup(_file_row(r'C:\Box\チーム 資料\プレゼン.pptx')) == ('type', '.pptx')
    assert icon_lookup(_file_row(r'C:\Box\チーム 資料\手順書.pdf')) == ('type', '.pdf')


def test_path_icons_are_preserved_for_links_exes_and_installed_apps():
    for ext in ('.lnk', '.exe', '.ico', '.url', '.appref-ms'):
        target = r'C:\Box\My Files\App' + ext
        assert icon_lookup(_file_row(target)) == ('path', target)
    app = {'item_kind': 'command', 'icon_key': 'application',
           '_icon_file': r'C:\Program Files\App\app.exe'}
    assert icon_lookup(app) == ('path', app['_icon_file'])


def test_folder_and_drive_behavior_is_unchanged():
    folder = {'item_kind': 'directory', '_file': r'C:\Box\A.Folder', 'icon_key': 'folder.yellow'}
    drive = {'item_kind': 'directory', '_file': 'F:\\', '_system_drive': True,
             'icon_key': 'folder.yellow'}
    assert icon_lookup(folder) == ('path', folder['_file'])
    assert icon_lookup(drive) == ('path', drive['_file'])
    assert icon_lookup({'icon_key': 'mail'}) == ('default', 'mail')


def test_actual_launcher_wires_type_icons_without_accessing_cloud_path():
    source = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    launcher = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    row_icon = next(n for n in launcher.body if isinstance(n, ast.FunctionDef) and n.name == 'row_icon')
    text = ast.get_source_segment(source, row_icon)
    assert 'source, target = icon_lookup(row)' in text
    assert "QFileInfo('FRBLaunchTypeSample' + target)" in text
    assert "('file_type', target)" in text
    assert "source == 'path'" in text


def test_cloud_file_icon_is_resolved_once_per_extension_even_without_stat(monkeypatch):
    """Execute the actual method using light fakes (PySide is not installed)."""
    source = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    launcher = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    method = next(n for n in launcher.body if isinstance(n, ast.FunctionDef) and n.name == 'row_icon')
    fn_module = ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))
    calls = []

    class FakeIcon:
        def isNull(self):
            return False

    expected = FakeIcon()

    class Provider:
        def icon(self, info):
            calls.append(info)
            return expected

    class Launcher:
        icon_cache = {}
        file_icons = Provider()

    namespace = {'icon_lookup': icon_lookup,
                 'QFileInfo': lambda name: name,
                 'Path': Path,
                 'icon': lambda kind: ('generic', kind)}
    exec(compile(fn_module, '<real launcher row_icon>', 'exec'), namespace)
    method = namespace['row_icon']
    a = _file_row(r'C:\Users\法人名\Box\Folder A\月次報告.xlsx')
    b = _file_row(r'D:\SharePoint - 法人名\Folder B\Excel.xlsx')
    monkeypatch.setattr(Path, 'is_file', lambda self: (_ for _ in ()).throw(AssertionError('must not stat cloud path')))
    assert method(Launcher, a) is expected
    assert method(Launcher, b) is expected
    assert calls == ['FRBLaunchTypeSample.xlsx']


def test_path_icon_behavior_still_preserved_for_custom_icon_files():
    source = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    launcher = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    method = next(n for n in launcher.body if isinstance(n, ast.FunctionDef) and n.name == 'row_icon')
    fn_module = ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))
    calls = []
    sentinel = object()

    class Provider:
        def icon(self, info):
            calls.append(info)
            return sentinel

    class Launcher:
        icon_cache = {}
        file_icons = Provider()

    namespace = {'icon_lookup': icon_lookup,
                 'QFileInfo': lambda name: name,
                 'Path': Path,
                 'icon': lambda kind: ('generic', kind)}
    exec(compile(fn_module, '<real launcher row_icon>', 'exec'), namespace)
    method = namespace['row_icon']
    item = {'_icon_file': r'C:\Program Files\Application X\x.exe', 'icon_key': 'application'}
    assert method(Launcher, item) is sentinel
    assert calls == [item['_icon_file']]
