"""v45 automatic download, hover actions, auto-popup and safe ZIP tests (no Qt)."""
import ast
import io
from pathlib import Path
from types import SimpleNamespace
import sys
import zipfile
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from launch_downloads import safe_download_name, unique_path, safe_extract_zip


def web_source():
    return (ROOT / 'src/launch_web_view.py').read_text(encoding='utf-8')


def method(class_name, name, extra=None):
    tree = ast.parse(web_source())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    member = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    mod = ast.fix_missing_locations(ast.Module(body=[member], type_ignores=[]))
    scope = dict(extra or {})
    exec(compile(mod, 'src/launch_web_view.py', 'exec'), scope)
    return scope[name]


def test_safe_name_and_collision_rules(tmp_path):
    assert safe_download_name('../../oops.zip') == 'oops.zip'
    assert safe_download_name(r'C:\Users\x\nice.zip') == 'nice.zip'
    assert safe_download_name('CON.txt') == '_CON.txt'
    assert safe_download_name('bad<>?*.zip') == 'bad____.zip'
    assert unique_path(tmp_path, 'report.zip').name == 'report.zip'
    (tmp_path / 'report.zip').write_bytes(b'old')
    assert unique_path(tmp_path, 'report.zip').name == 'report (1).zip'
    assert unique_path(tmp_path, 'report.zip', [tmp_path / 'report (1).zip']).name == 'report (2).zip'


def test_automatic_download_without_save_dialog(tmp_path):
    events = []
    class Signal:
        def connect(self, callback): events.append('connect')
    class Request:
        def suggestedFileName(self): return 'sample.zip'
        def downloadFileName(self): return ''
        def setDownloadDirectory(self, value): events.append(('directory', value))
        def setDownloadFileName(self, value): events.append(('name', value))
        stateChanged = Signal()
        receivedBytesChanged = Signal()
        totalBytesChanged = Signal()
        def accept(self): events.append('accept')
        def cancel(self): events.append('cancel')
    fn = method('LaunchWebView', '_download_requested', {
        'Path': Path, 'safe_download_name':safe_download_name, 'unique_path':unique_path,
    })
    class Owner:
        _downloads = []
        _download_popup = None
        _downloads_folder = ''
        def default_download_folder(self): return str(tmp_path / 'files')
        def _update_download_button(self): events.append('update')
        def _on_download_state(self, r): pass
    owner = Owner()
    fn(owner, Request())
    assert ('name', 'sample.zip') in events
    assert ('directory', str(tmp_path / 'files')) in events
    assert events.index('accept') > events.index(('name', 'sample.zip'))
    assert len(owner._downloads) == 1
    assert owner._downloads[0]['path'] == str(tmp_path/'files'/'sample.zip')
    assert 'cancel' not in events


def test_completed_download_animates_and_auto_shows_panel_once():
    class State:
        DownloadCompleted='done'
    class DownloadRequest:
        DownloadState=State
    fn = method('LaunchWebView', '_on_download_state', {
        'QWebEngineDownloadRequest': DownloadRequest,
        'QTimer': SimpleNamespace(singleShot=lambda ms, cb: events.append(('schedule', ms, cb))),
    })
    events=[]
    record={'request':SimpleNamespace(state=lambda:'done'), 'notified':False}
    owner=SimpleNamespace(_update_download_button=lambda: events.append('update'),
                          isVisible=lambda: True,
                          _animate_download_complete=lambda: events.append('animate'),
                          _show_completed_downloads=lambda:events.append('popup'))
    fn(owner, record)
    fn(owner, record)
    assert record['notified'] is True
    assert events.count('animate')==1
    assert sum(e[0]=='schedule' for e in events if isinstance(e,tuple))==1


def test_zip_extraction_creates_subfolder_and_does_not_overwrite(tmp_path):
    original=tmp_path/'sample.zip'
    with zipfile.ZipFile(original, 'w') as z:
        z.writestr('folder/readme.md', 'hello')
        z.writestr('root.txt', 'world')
    first=Path(safe_extract_zip(original))
    assert first == tmp_path/'sample'
    assert (first/'folder'/'readme.md').read_text()=='hello'
    second=Path(safe_extract_zip(original))
    assert second == tmp_path/'sample (1)'
    assert (second/'root.txt').read_text()=='world'


@pytest.mark.parametrize('dangerous', [
    '../evil.txt', '/root/evil.txt', r'dir\evil.txt', 'C:/Windows/evil.txt',
    'CON.txt', 'dir/../evil.txt', 'sneaky:/foo',
])
def test_zip_extraction_rejects_unsafe_names(tmp_path, dangerous):
    zip_path=tmp_path/'evil.zip'
    with zipfile.ZipFile(zip_path,'w') as archive:
        archive.writestr(dangerous,'evil')
    with pytest.raises(ValueError):
        safe_extract_zip(zip_path)
    assert not (tmp_path/'evil').exists()


def test_zip_extraction_rejects_symlink(tmp_path):
    file=tmp_path/'link.zip'
    link=zipfile.ZipInfo('link')
    link.create_system=3
    link.external_attr=(0o120777<<16)
    with zipfile.ZipFile(file,'w') as archive:
        archive.writestr(link,'../../etc/passwd')
    with pytest.raises(ValueError):
        safe_extract_zip(file)


def test_zip_extraction_rejects_limit(tmp_path):
    file=tmp_path/'big.zip'
    with zipfile.ZipFile(file,'w') as archive:
        archive.writestr('large', '123456789')
    with pytest.raises(ValueError):
        safe_extract_zip(file, max_bytes=8)


def test_download_panel_has_hover_actions_and_animations():
    src=web_source()
    icons=(ROOT/'src/browser_nav_icons.py').read_text(encoding='utf-8')
    assert 'class _DownloadPanel(QFrame)' in src
    assert 'class _DownloadRow(QFrame)' in src
    assert 'def enterEvent(self, event):' in src
    assert "self.extract.setToolTip('ZIPを展開してフォルダーを開く')" in src
    assert "self.folder.setToolTip('エクスプローラーで保存フォルダーを開く')" in src
    assert 'QPropertyAnimation(effect, b\'opacity\'' in src
    assert 'QTimer.singleShot(230, self._show_completed_downloads)' in src
    assert "name == 'folder_open'" in icons
    assert "name == 'unzip'" in icons
    assert 'QFileDialog.getSaveFileName(' not in src
    assert 'request.setDownloadDirectory(str(target.parent))' in src
    assert 'request.setDownloadFileName(target.name)' in src
    assert 'request.accept()' in src
    assert 'worker.extracted.connect(self.open_download_folder)' in src
    assert 'Qt.WindowType.Popup' in src
