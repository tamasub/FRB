"""2026-11-12: History remains reachable from dedicated controls, not column menus."""
from pathlib import Path
from files_column_context import NAVIGATION

APP=(Path(__file__).resolve().parents[1]/'src/app.py').read_text(encoding='utf-8')


def test_column_switch_menu_has_one_command_per_origin():
    assert set(NAVIGATION)=={'exp','list'}
    assert NAVIGATION['exp'][0]=='List列へ進む'
    assert NAVIGATION['list'][0]=='Exp列へ戻る'


def test_search_and_folder_history_remain_supported_outside_context_navigation():
    for cmd in ('SEARCH_HISTORY','FOLDER_HISTORY'):
        assert f"if command == '{cmd}':" in APP
    route=APP.split('    def _prepend_remote_pad_navigation(',1)[1].split(
        '    def _show_remote_target_context_menu(',1)[0]
    assert '検索履歴' not in route
    assert 'フォルダー履歴' not in route
