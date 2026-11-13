"""0276: Page belongs to Exp header; URL dialog uses the shared Studio schema.

Qt-free checks; the final native dialog/drag should be accepted on Windows.
"""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace as NS

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from launch_menu_registration import RegistrationError, url_registration_record, mime_sources

APP = (ROOT/'src/app.py').read_text(encoding='utf-8')
EXP = (ROOT/'src/remote_files_explorer.py').read_text(encoding='utf-8')
DIALOG = (ROOT/'src/launch_url_dialog.py').read_text(encoding='utf-8')


def method(source, name, next_name=None):
    start = source.index('    def ' + name + '(')
    end = source.find('\n    def ', start + 5)
    return source[start:end if end != -1 else None]


def test_page_menu_is_only_on_exp_title_header():
    assert '_add_page_creation_menu_action(menu)' in method(EXP, '_show_layout_menu')
    assert "header.customContextMenuRequested.connect(" in EXP
    assert "title.customContextMenuRequested.connect(" in EXP
    assert "launcher._show_launch_json_context_popup(menu, position, column='exp')" in EXP
    assert '_add_page_creation_menu_action(menu)' not in method(APP, 'show_launch_root_registration_menu')
    assert '_add_page_creation_menu_action(menu)' not in method(APP, 'show_virtual_launch_context')


def test_url_menu_is_common_for_exp_list_page_category_but_not_physical_blank_root():
    menu_logic = method(APP, '_add_registration_menu_actions')
    assert "commands.append(('file', '既存ファイルを登録...'))" in menu_logic
    assert "commands.append(('url', 'URLを追加...'))" in menu_logic
    assert menu_logic.index("commands.append(('file',") < menu_logic.index("commands.append(('url',")
    assert 'self.launch_url_add_action(pg, par)' in menu_logic
    virtual = method(APP, 'show_virtual_launch_context')
    assert 'self._add_registration_menu_actions(' in virtual
    assert "column='list' if list_context else 'exp'" in virtual
    root = method(APP, 'show_launch_root_registration_menu')
    assert 'allow_file=False, allow_category=False' in root


def test_url_registration_keeps_studio_open_action_schema_and_exact_title():
    row = url_registration_record('FRBの研究 🎣', 'https://example.com/path?a=1&b=2')
    assert row['title'] == 'FRBの研究 🎣'
    assert row['description'] == 'https://example.com/path?a=1&b=2'
    assert row['item_kind'] == 'command'
    assert row['icon_key'] == 'globe'
    assert row['launch_browse_target'] == ''
    assert row['launch_actions'][0]['launch_action_type'] == 'Open'
    assert row['launch_actions'][0]['launch_target'] == 'https://example.com/path?a=1&b=2'
    assert row['launch_actions'][0]['launch_program'] == ''


@pytest.mark.parametrize('title,url', [
    ('', 'https://example.com'),
    ('title', 'javascript:alert(1)'),
    ('title', 'file:///C:/secret.txt'),
    ('title', 'https://example.com\nRUN CMD'),
    ('title', 'foo'),
    ('a' * 161, 'https://example.com'),
])
def test_url_registration_rejects_missing_or_invalid_input(title, url):
    with pytest.raises(RegistrationError):
        url_registration_record(title, url)


def test_url_dialog_has_drop_title_url_get_and_common_runner():
    ast.parse(DIALOG)
    assert 'class URLDropLineEdit(QLineEdit)' in DIALOG
    assert 'def dropEvent(self, event):' in DIALOG
    assert 'self.url_dropped.emit(source[' in DIALOG
    assert "QPushButton('URL取得', self)" in DIALOG
    assert 'Launch本体の登録先へDropしても自動追加できますよ' in DIALOG
    assert 'QApplication.clipboard().mimeData()' in DIALOG
    assert "self.current_browser_url()" in DIALOG
    assert 'url_registration_record(' in DIALOG
    action = method(APP, 'launch_url_add_action')
    assert 'LaunchURLRegistrationDialog(' in action
    assert 'self.run_launch_button_dialog(' in action
    assert 'self._registration_commit(' in action
    assert 'self._registration_commit(' not in DIALOG


class FakeMime:
    def __init__(self, formats=None, text=None):
        self._formats = formats or {}
        self._text = text
    def hasUrls(self): return False
    def hasFormat(self, name): return name in self._formats
    def data(self, name): return self._formats[name]
    def formats(self): return list(self._formats)
    def hasText(self): return self._text is not None
    def text(self): return self._text


def test_extracted_url_drop_adapter_accepts_chrome_url_and_preserves_title():
    # Compile just the adapter function. No PySide6 installed on this Linux CI.
    function = next(n for n in ast.parse(DIALOG).body
                    if isinstance(n, ast.FunctionDef) and n.name == 'url_source_from_mime')
    from launch_menu_registration import normalize_sources
    env = dict(mime_sources=mime_sources, normalize_sources=normalize_sources,
               RegistrationError=RegistrationError)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])),
                 '<url-adapter>', 'exec'), env)
    adapter = env['url_source_from_mime']
    assert adapter(FakeMime(text='https://example.com/'))['value'] == 'https://example.com/'
    assert adapter(FakeMime({'text/html': b'<a href="https://example.com/frb">FRB URL</a>'})) == {
        'kind': 'url', 'value': 'https://example.com/frb', 'title': 'FRB URL'}
    assert adapter(FakeMime(text='cmd.exe /c evil')) is None
