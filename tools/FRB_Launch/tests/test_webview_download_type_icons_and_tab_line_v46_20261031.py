"""v46: download icons by file type and no redundant Web tab pane rule (no Qt)."""
import ast
from pathlib import Path, PureWindowsPath
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
WEB = (ROOT / 'src/launch_web_view.py').read_text(encoding='utf-8')


def _method(class_name, method_name, extra=None):
    module = ast.parse(WEB)
    cls = next(node for node in module.body
               if isinstance(node, ast.ClassDef) and node.name == class_name)
    method = next(node for node in cls.body
                  if isinstance(node, ast.FunctionDef) and node.name == method_name)
    local = dict(extra or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 '<v46>', 'exec'), local)
    return local[method_name]


class FakeIcon:
    def __init__(self, null=False):
        self.null = null

    def isNull(self):
        return self.null


class FakeIconProvider:
    IconType = SimpleNamespace(File='fallback')

    def __init__(self, *, null_exts=()):
        self.lookups = []
        self.null_exts = null_exts

    def icon(self, value):
        self.lookups.append(value)
        return FakeIcon(value in self.null_exts)


def _owner(provider):
    return SimpleNamespace(_download_file_icon_provider=provider,
                           _download_file_icon_cache={})


def _file_icon_method():
    return _method('LaunchWebView', 'download_file_icon', {
        'PureWindowsPath': PureWindowsPath,
        'QFileInfo': lambda filename: filename,
        'QFileIconProvider': FakeIconProvider,
    })


def test_download_icon_uses_extension_only_not_untrusted_actual_path():
    fn = _file_icon_method()
    provider = FakeIconProvider()
    owner = _owner(provider)
    fn(owner, r'C:\Users\Example\Downloads\document.ZIP')
    fn(owner, r'C:\Users\Example\Downloads\another.zip')
    fn(owner, r'C:\Users\Example\Downloads\guide.PDF')
    fn(owner, r'C:\Users\Example\Downloads\photo.png')
    assert provider.lookups == [
        'FRBLaunchTypeSample.zip',
        'FRBLaunchTypeSample.pdf',
        'FRBLaunchTypeSample.png',
    ]
    assert set(owner._download_file_icon_cache) == {'.zip', '.pdf', '.png'}


def test_download_icon_handles_no_extension_and_windows_unknown_type():
    fn = _file_icon_method()
    provider = FakeIconProvider(null_exts=('FRBLaunchTypeSample.xyz',))
    owner = _owner(provider)
    fn(owner, 'README')
    fn(owner, 'something.xyz')
    fn(owner, 'another.xyz')
    assert provider.lookups == ['fallback', 'FRBLaunchTypeSample.xyz', 'fallback']


def test_download_rows_show_type_icon_instead_of_platform_paper_icon():
    assert 'from PySide6.QtWidgets import' in WEB
    assert 'QFileIconProvider)' in WEB
    assert "self._download_file_icon_provider = QFileIconProvider()" in WEB
    assert "owner.download_file_icon(record['path']).pixmap(QSize(26, 26))" in WEB
    assert 'QStyle.StandardPixmap.SP_FileIcon' not in WEB
    # Download actions remain unchanged.
    assert "owner.open_download_folder(record['path'])" in WEB
    assert "owner.extract_download_zip(record['path'])" in WEB


def test_web_tabs_do_not_draw_an_extra_horizontal_pane_line():
    assert 'QTabWidget#launchWebTabs::pane {{border:0;margin:0;padding:0;}}' in WEB
    assert 'QTabWidget::pane {{border:1px solid {border};}}' not in WEB
    assert 'QTabBar#launchWebTabBar::tab {{background:{hdr};color:{text};' in WEB
    assert 'border-bottom:0;border-top-left-radius:9px;' in WEB
    # Existing Chrome-style tab affordances must remain.
    assert "self.tabs.setTabsClosable(True)" in WEB
    assert "self.tabs.setMovable(True)" in WEB
    assert "new_tab = QToolButton(self.tabs)" in WEB
    assert "self.tabs.setCornerWidget(new_tab, Qt.Corner.TopRightCorner)" not in WEB
