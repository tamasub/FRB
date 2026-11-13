"""Chrome URL title and Files Exp PC divider regressions (studio_work_0276)."""
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from launch_menu_registration import mime_sources, normalize_sources, records_for_sources

URL = 'https://qiita.com/tamasub/items/4e1f729c1a30ada07730'
TITLE = 'AI協働：FRB Launch Python製 独自UI機能14選 の種明かし'


class Url:
    def isLocalFile(self): return False
    def toString(self): return URL


class Mime:
    def __init__(self, formats=None, urls=(), text=None):
        self._formats, self._urls, self._text = formats or {}, urls, text
    def hasUrls(self): return bool(self._urls)
    def urls(self): return self._urls
    def hasFormat(self, name): return name in self._formats
    def formats(self): return list(self._formats)
    def data(self, name): return self._formats[name]
    def hasText(self): return self._text is not None
    def text(self): return self._text


def _result(mime):
    return records_for_sources(normalize_sources(mime_sources(mime)))


def test_chrome_url_list_and_html_merge_to_one_actual_page_title():
    html = f'<a href="{URL}">{TITLE}</a>'.encode('utf-8')
    rows = _result(Mime({'text/html': html}, urls=[Url()]))
    assert len(rows) == 1
    assert rows[0]['title'] == TITLE
    assert rows[0]['launch_actions'][0]['launch_target'] == URL


def test_chrome_address_bar_plain_text_is_not_the_page_title():
    address_without_scheme = URL.split('://', 1)[1]
    html = f'<a href="{URL}">{TITLE}</a>'.encode('utf-8')
    rows = _result(Mime({'text/html': html}, urls=[Url()], text=address_without_scheme))
    assert [r['title'] for r in rows] == [TITLE]


def test_native_windows_html_format_also_supplies_a_title():
    html = f'Version:0.9\r\nStartHTML:00000000\r\n<a href="{URL}">{TITLE}</a>'.encode('utf-8')
    rows = _result(Mime({'application/x-qt-windows-mime;value="HTML Format"': html},
                        urls=[Url()]))
    assert len(rows) == 1 and rows[0]['title'] == TITLE


def test_moz_url_title_survives_existing_qt_urls():
    blob = f'{URL}\r\n{TITLE}\r\n'.encode('utf-16-le')
    rows = _result(Mime({'text/x-moz-url': blob}, urls=[Url()]))
    assert len(rows) == 1 and rows[0]['title'] == TITLE


def test_html_unrelated_link_does_not_create_spurious_bookmark():
    html = b'<a href="https://example.org/other">Unrelated page</a>'
    rows = _result(Mime({'text/html': html}, urls=[Url()]))
    assert len(rows) == 1
    assert rows[0]['launch_actions'][0]['launch_target'] == URL
    assert rows[0]['title'] != 'Unrelated page'


def test_file_drop_title_retains_original_filename(tmp_path):
    from launch_menu_registration import normalize_sources
    file = tmp_path / 'FRB実験ログ.md'
    file.write_text('test', encoding='utf-8')
    assert normalize_sources([{'value': str(file)}])[0]['title'] == file.name


def test_exp_divider_owns_its_air_before_normal_height_pc_row():
    src = (ROOT / 'src/remote_files_explorer.py').read_text(encoding='utf-8')
    assert 'self.tree.setUniformRowHeights(False)' in src
    assert "separator.setData({'separator_before_pc': True}, _DATA_ROLE)" in src
    assert 'separator.setSizeHint(QSize(0, 19))' in src
    assert 'separator.setFlags(Qt.ItemFlag.NoItemFlags)' in src
    assert 'y = option.rect.top() + 8' in src
    assert 'painter.drawLine(' in src
    # Never inflate PC's own row or the spare space ends up below PC.
    assert 'item.setSizeHint(QSize(0, 55))' not in src
    assert 'if pc:\n            item.setSizeHint' not in src
    # The decorative row cannot be selected by wheel or Remote.
    assert 'self._neighbor_operable(new_index, movement)' in src
    assert 'tree._neighbor_operable(index, direction)' in src
    assert "data.get('separator_before_pc')" in src


def test_chrome_virtual_url_descriptor_uses_visible_drag_title():
    # Chrome on Windows advertises a .url filename with the page title.
    # The Qt URI and plain text can both be only an address.
    native = bytearray(struct.pack('<I', 1) + b'\x00' * 592)
    name = (TITLE + '.url').encode('utf-16-le')
    native[4 + 72:4 + 72 + len(name)] = name
    rows = _result(Mime({
        'application/x-qt-windows-mime;value="FileGroupDescriptorW"': bytes(native)
    }, urls=[Url()], text=URL.split('://', 1)[1]))
    assert len(rows) == 1
    assert rows[0]['title'] == TITLE
    assert rows[0]['launch_actions'][0]['launch_target'] == URL


def test_unrelated_virtual_file_descriptor_does_not_set_url_title():
    native = bytearray(struct.pack('<I', 1) + b'\x00' * 592)
    name = 'attachment.pdf'.encode('utf-16-le')
    native[4 + 72:4 + 72 + len(name)] = name
    rows = _result(Mime({
        'application/x-qt-windows-mime;value="FileGroupDescriptorW"': bytes(native)
    }, urls=[Url()]))
    assert len(rows) == 1
    assert rows[0]['title'] != 'attachment'
