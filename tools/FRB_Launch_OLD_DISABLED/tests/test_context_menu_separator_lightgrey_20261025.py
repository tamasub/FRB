"""Light gray context separators are defined once in JSON + scoped QSS."""
from pathlib import Path
from context_menu_config import load_context_menus, visible_context_entries
from launch_appearance import CONTEXT_MENU_SPACING_QSS

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config/context_menu_options.json'


def test_file_menu_has_additional_delimiter_between_open_and_terminal():
    rows = load_context_menus(CONFIG)['file']
    ids = [row.get('action_id', '|') for row in rows]
    idx = ids.index('open_parent_folder')
    assert ids[idx:idx + 3] == ['open_parent_folder', '|', 'open_parent_terminal']


def test_other_menu_commands_and_folder_order_unaffected():
    menus = load_context_menus(CONFIG)
    for kind in ('file', 'folder'):
        allowed = [row.get('action_id') for row in menus[kind] if row.get('action_id')]
        assert len(allowed) == len(set(allowed))
        assert allowed[:3] == ['copy', 'cut', 'paste']
        assert allowed[-1] == 'properties'
        visible = visible_context_entries(menus[kind], set(allowed))
        assert visible[0].get('action_id') == 'copy'
        assert visible[-1].get('action_id') == 'properties'


def test_separators_subtle_light_gray_not_blue():
    assert 'QMenu::separator { height:1px; background:#e1e5e2; margin:5px 3px; }' in CONTEXT_MENU_SPACING_QSS
    assert '#6c9bd6' not in CONTEXT_MENU_SPACING_QSS
