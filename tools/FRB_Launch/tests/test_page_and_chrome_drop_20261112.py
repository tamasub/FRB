"""Contract and Studio CLI tests for new Page UI and Chrome URL registration."""
import ast
import json
import os
from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from launch_page_registration import page_operation_plan, commit_page_operation
from launch_menu_registration import (RegistrationError, mime_sources,
                                      normalize_sources, records_for_sources,
                                      chrome_html_link)


def original_doc(tmp_path):
    p=tmp_path/'launch.json'
    p.write_bytes((ROOT/'config/frb_launch_sample_data_v0_1.json').read_bytes())
    return p


def test_create_page_has_next_sort_no_duplicate_id(tmp_path):
    p=original_doc(tmp_path)
    plan=page_operation_plan(p,'add',title='テスト Page')
    page=plan['operations'][0]['records'][0]
    assert page['title']=='テスト Page'
    assert page['sort_order']==70
    assert 'page_id' not in page
    assert plan['summary']=={'added':1}


def test_update_page_only_name_icon_and_no_op(tmp_path):
    p=original_doc(tmp_path)
    assert page_operation_plan(p,'update',page_id='work',title='💼 My Work',icon_key='💼') is None
    plan=page_operation_plan(p,'update',page_id='work',title='仕事',icon_key='⭐')
    target=plan['operations'][0]['targets'][0]
    assert target['id']=='work'
    assert target['changes']==[{'path':'title','value':'仕事'},
                               {'path':'icon_key','value':'⭐'}]


def test_unregister_fails_closed_with_attached_items_or_system(tmp_path):
    p=original_doc(tmp_path)
    for page_id in ('system','work','frb'):
        with pytest.raises(RegistrationError):
            page_operation_plan(p,'delete',page_id=page_id)
    # No original JSON bytes were changed.
    assert p.read_bytes()==(ROOT/'config/frb_launch_sample_data_v0_1.json').read_bytes()


def test_empty_page_delete_is_single_studio_section(tmp_path):
    p=original_doc(tmp_path)
    doc=json.loads(p.read_text(encoding='utf8'))
    doc['pages'].append({'page_id':'empty_test','title':'空Page','enabled':True})
    p.write_text(json.dumps(doc,ensure_ascii=False),encoding='utf8')
    plan=page_operation_plan(p,'delete',page_id='empty_test')
    assert plan['operations']==[{'operation':'delete','section_id':'pages',
                                 'targets':[{'id':'empty_test'}]}]


def test_chrome_link_from_html_only():
    html=chrome_html_link('<a href="https://example.com/qiita?q=1&amp;x=2">FRB 記事</a>'.encode('utf8'))
    assert html=={'value':'https://example.com/qiita?q=1&x=2','title':'FRB 記事'}
    assert chrome_html_link(b'<a href="javascript:alert(1)">No</a>') is None


class FakeMime:
    def __init__(self,formats=None,text=None):
        self._formats=formats or {}
        self._text=text
    def hasUrls(self):return False
    def hasFormat(self,name):return name in self._formats
    def data(self,name):return self._formats[name]
    def formats(self):return list(self._formats)
    def hasText(self):return self._text is not None
    def text(self):return self._text


@pytest.mark.parametrize('mime',[
    FakeMime(text='https://example.org/'),
    FakeMime({'text/uri-list':b'https://example.org/\r\n'}),
    FakeMime({'text/html':b'<a href="https://example.org/">Example</a>'}),
    FakeMime({'application/x-qt-windows-mime;value="UniformResourceLocatorW"':
              'https://example.org/'.encode('utf-16-le')+b'\x00\x00'}),
])
def test_chrome_address_bar_drop_uses_same_bookmark_record(mime):
    src=normalize_sources(mime_sources(mime))
    assert len(src)==1 and src[0]['kind']=='url'
    row=records_for_sources(src)[0]
    assert row['item_kind']=='command'
    assert row['icon_key']=='globe'
    assert row['launch_actions'][0]['launch_target']=='https://example.org/'


def test_exp_and_list_target_chrome_url_without_loosened_physical_root():
    src=(ROOT/'src/remote_files_explorer.py').read_text(encoding='utf8')
    list_src=(ROOT/'src/expanded_view.py').read_text(encoding='utf8')
    assert 'or Path(e.get(\'value\', \'\')).is_dir()' in src
    assert 'Exp blank root: only physical directories' in src
    assert "not str(e.get('value', '')).lower().startswith(('http://', 'https://'))" in src
    assert 'The List blank area of an authored Page accepts file/URL drops too' in list_src


def test_exp_separator_is_inactive_decoration_not_a_tall_pc():
    src=(ROOT/'src/remote_files_explorer.py').read_text(encoding='utf8')
    assert 'separator.setSizeHint(QSize(0, 19))' in src
    assert 'separator.setFlags(Qt.ItemFlag.NoItemFlags)' in src
    assert 'item.setSizeHint(QSize(0, 55))' not in src
    assert 'self.tree.setUniformRowHeights(False)' in src
    assert 'y = option.rect.top() + 8' in src
    assert 'root_drop_hint' in src


def test_page_actions_use_common_launcher_dialog_and_same_json_core():
    app=(ROOT/'src/app.py').read_text(encoding='utf8')
    ast.parse(app)
    assert "menu.addAction('Pageを追加...')" in app
    assert 'self.launch_page_simple_edit_action(pg)' in app
    assert 'self.launch_page_unregister_action(pg)' in app
    assert 'run_launch_button_dialog(dialog, buttons, title)' in app
    assert 'self.ask_remote_confirmation(' in app


def test_page_add_update_delete_roundtrip_through_real_studio(tmp_path):
    studio=os.environ.get('FRB_STUDIO_TEST_ROOT')
    if not studio or not shutil.which('node'):
        pytest.skip('Studio CLI not provided')
    p=original_doc(tmp_path)
    before=json.loads(p.read_text(encoding='utf8'))
    added=commit_page_operation(p,studio,'add',title='🍀 追加Page')
    assert added['status']=='COMMITTED'
    doc=json.loads(p.read_text(encoding='utf8'))
    new=[x for x in doc['pages'] if x['page_id'] not in {x['page_id'] for x in before['pages']}]
    assert len(new)==1
    pid=new[0]['page_id']
    modified=commit_page_operation(p,studio,'update',page_id=pid,title='変更Page',icon_key='🌐')
    assert modified['status']=='COMMITTED'
    assert next(x for x in json.loads(p.read_text())['pages'] if x['page_id']==pid)['icon_key']=='🌐'
    deleted=commit_page_operation(p,studio,'delete',page_id=pid)
    assert deleted['status']=='COMMITTED'
    after=json.loads(p.read_text(encoding='utf8'))
    assert after==before


def test_chrome_address_bar_url_commits_under_bookmark_category(tmp_path):
    studio=os.environ.get('FRB_STUDIO_TEST_ROOT')
    if not studio or not shutil.which('node'):
        pytest.skip('Studio CLI not provided')
    from launch_menu_registration import commit_add
    p=original_doc(tmp_path)
    doc=json.loads(p.read_text(encoding='utf8'))
    # Add beneath the existing System bookmark category, NOT the physical Files root.
    bookmark_root=next((r for r in doc['items'] if r.get('page_id')=='system'
                        and r.get('launch_source')=='browser_bookmarks'),None)
    if bookmark_root is None:
        pytest.skip('No authored bookmark target in sample')
    target=mime_sources(FakeMime({'text/html':b'<a href="https://example.org/frb">FRB News</a>'}))
    records=records_for_sources(normalize_sources(target))
    result=commit_add(p,studio,'system',bookmark_root['item_id'],records)
    assert result['status']=='COMMITTED'
    rows=json.loads(p.read_text(encoding='utf8'))['items']
    matches=[r for r in rows if r.get('title')=='FRB News'
             and r.get('parent_item_id')==bookmark_root['item_id']]
    assert len(matches)==1
    assert matches[0]['launch_actions'][0]['launch_target']=='https://example.org/frb'
