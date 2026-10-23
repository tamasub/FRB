"""Jump List contracts, independently testable without Windows Shell/PySide6."""
import copy
import json
from pathlib import Path
import pytest
from jump_list import (page_root_entries, limited_page_entries,
                       ipc_command, parse_ipc_command, argument_for_item,
                       requested_item, list_fingerprint, needs_refresh, APP_ID)

ROOT = Path(__file__).resolve().parents[1]


def data():
    return json.loads((ROOT/'config'/'frb_launch_sample_data_v0_1.json').read_text(encoding='utf-8'))


def test_only_work_page_all_six_root_items_in_data_order():
    groups = page_root_entries(data())
    assert [name for name, _ in groups] == ['仕事']
    assert [title for _, title in groups[0][1]] == [
        '設定', 'ZIP', 'Files', 'ブックマーク', '日付・定型文', 'メール宛先'
    ]
    assert len(groups[0][1]) == 6


def test_page_root_ignores_other_pages_disabled_nested():
    sample = {'pages': [{'page_id':'work','title':'仕事'},
                        {'page_id':'windows','title':'Windows'},
                        {'page_id':'disabled','enabled':False}],
              'items': [
                  {'item_id':'root','page_id':'work','title':'Root','sort_order':5},
                  {'item_id':'child','page_id':'work','parent_item_id':'root'},
                  {'item_id':'off','page_id':'work','enabled':False},
                  {'item_id':'other','page_id':'windows'},
                  {'item_id':'closed','page_id':'disabled'},
              ]}
    assert page_root_entries(sample) == [('仕事', [('root','Root')])]
    sample['pages'][0]['enabled'] = False
    assert page_root_entries(sample) == []


def test_windows_slot_limit_prioritizes_work_only():
    assert limited_page_entries(data(), 7) == page_root_entries(data())
    assert [title for _, title in limited_page_entries(data(), 4)[0][1]] == [
        '設定','ZIP','Files','ブックマーク']
    assert limited_page_entries(data(), 0) == []
    assert limited_page_entries(data(), -10) == []


def test_ipc_command_and_cli_unicode_round_trip():
    for item in ['folders','ZIP 設定','a/b&()']:
        action, decoded = parse_ipc_command(ipc_command(item))
        assert (action, decoded) == ('show-menu', item)
        assert requested_item([argument_for_item(item)]) == item


def test_legacy_show_still_works():
    assert parse_ipc_command(b'show') == ('show', None)
    assert parse_ipc_command(b'show\n') == ('show', None)


@pytest.mark.parametrize('message', [b'', b'execute', b'{}\n', b'{"action":"run","item_id":"folders"}\n',
                                    b'{"action":"show-menu","item_id":""}\n', b'garbage\n',
                                    b'{"action":"show-menu","item_id":"a"}' + b' '*2200 + b'\n'])
def test_invalid_ipc_never_executes(message):
    with pytest.raises((ValueError, UnicodeError, json.JSONDecodeError)):
        parse_ipc_command(message)


def test_invalid_item_ids_and_args():
    for item in ('', 'a\nb', 'x'*251):
        with pytest.raises(ValueError):
            ipc_command(item)
    assert requested_item(['--jump-item=%XX']) is None


def test_fingerprint_only_tracks_work_menu():
    original = data()
    before = list_fingerprint(original, r'C:\FRB\FRBLaunch.exe')
    edited = copy.deepcopy(original)
    edited['items'][0]['title'] += '修正'
    assert list_fingerprint(edited, r'C:\FRB\FRBLaunch.exe') != before
    edited = copy.deepcopy(original)
    next(item for item in edited['items'] if item['page_id'] == 'windows')['title'] += '修正'
    assert list_fingerprint(edited, r'C:\FRB\FRBLaunch.exe') == before
    assert APP_ID == 'FRB.Launch'


def test_force_refresh_after_restart_with_unchanged_fingerprint():
    assert needs_refresh('abc', 'abc') is False
    assert needs_refresh('abc', 'abc', force=True) is True
    assert needs_refresh('abc', 'xyz') is True
    assert needs_refresh(None, 'abc') is True
