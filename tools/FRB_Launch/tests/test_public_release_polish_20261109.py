"""Public-release fixes: editable Page UI, protected Files and gesture race.

These tests run on non-Windows hosts without PySide6; a real Windows GUI smoke
remains necessary for native focus and wheel event behavior.
"""
import ast
import json
import sys
import types
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from page_presentation import PAGE_ICONS, page_display_title
from launch_virtual_tree import virtual_launch_pages, virtual_lookup_node
from expanded_view_model import expanded_targets, normalize_options
from desktop_double_click import DesktopDoubleClick, Click


def sample():
    return json.loads((ROOT / 'config/frb_launch_sample_data_v0_1.json').read_text(encoding='utf-8'))


def test_page_rename_and_icon_selection_are_source_driven():
    data = sample()
    pages = data['pages']
    assert page_display_title(pages[0]) == '💼 My Work'
    assert page_display_title(pages[1]) == '🎣 FRB実験xxx'
    pages[0]['title'] = '💼 研究本部'  # old user JSON contains an emoji already
    pages[0]['icon_key'] = '🚀'
    nodes = virtual_launch_pages(pages, data['items'])
    assert nodes[0]['title'] == '🚀 研究本部'
    assert nodes[0]['breadcrumbs'] == ('🚀 研究本部',)
    assert virtual_lookup_node(pages, data['items'], 'work')['title'] == '🚀 研究本部'
    pages[0]['icon_key'] = 'なし'
    assert page_display_title(pages[0]) == '研究本部'
    del pages[0]['icon_key']
    assert page_display_title(pages[0]) == '💼 研究本部'  # no migration needed


def test_studio_can_choose_all_supported_page_icons():
    doc = json.loads((ROOT / 'defs/launch/frb_launch_maintenance_view_def_v0_1.json').read_text(encoding='utf8'))
    view = next(v for v in doc['views'] if v.get('id') == 'pages_view')
    section = next(v for v in view['sections'] if v['id'] == 'pages')
    control = next(f for f in section['fields'] if f['field'] == 'icon_key')
    assert control['type'] == 'select'
    assert control['edit']['visible'] is True
    assert control['options'] == list(PAGE_ICONS)
    assert all('icon_key' in p for p in sample()['pages'])


def test_files_is_system_anchor_even_when_disabled_without_json_mutation():
    data = sample()
    options = normalize_options(None)
    files = next(r for r in data['items'] if r['item_id'] == 'folders')
    files['enabled'] = False
    unchanged = json.dumps(data, ensure_ascii=False, sort_keys=True)
    targets = expanded_targets(data['items'], options)
    assert targets is not None
    roots, left, right = targets
    assert left is files and right['item_id'] == '__browser_bookmarks_root'
    assert sum(r['item_id'] == 'folders' for r in roots) == 1
    pages = virtual_launch_pages(data['pages'], data['items'])
    work = next(p for p in pages if p['page_id'] == 'work')
    assert 'folders' not in {n['item_id'] for n in work['children']}
    assert json.dumps(data, ensure_ascii=False, sort_keys=True) == unchanged


def test_enabled_files_also_has_no_duplicate_my_work_node():
    data = sample()
    pages = virtual_launch_pages(data['pages'], data['items'])
    work = next(p for p in pages if p['page_id'] == 'work')
    assert 'folders' not in {n['item_id'] for n in work['children']}
    assert any(n['title'] == 'ZIP' for n in work['children'])
    assert all(n['item_id'] != 'folders' for n in work['children'])


def test_other_disabled_roots_are_still_honored():
    data = sample()
    options = normalize_options(None)
    another = next(r for r in data['items'] if r['item_id'] == 'zip')
    another['enabled'] = False
    roots, left, right = expanded_targets(data['items'], options)
    assert 'zip' not in {r['item_id'] for r in roots}
    assert left['item_id'] == 'folders'
    assert virtual_lookup_node(data['pages'], data['items'], 'work', 'zip') is None


def test_new_and_renamed_pages_are_not_hardcoded_to_three_names():
    pages = [{'page_id': 'work', 'title': '新しい作業', 'enabled': True, 'sort_order': 10},
             {'page_id': 'extra', 'title': '第四のページ', 'sort_order': 40}]
    tree = virtual_launch_pages(pages, [])
    assert [p['title'] for p in tree] == ['新しい作業', '第四のページ']


def test_page_button_option_defaults_hidden_and_scroll_engine_is_retained():
    app = (ROOT / 'src/app.py').read_text(encoding='utf8')
    expanded = (ROOT / 'src/expanded_view.py').read_text(encoding='utf8')
    remote = (ROOT / 'src/launch_remote.py').read_text(encoding='utf8')
    assert "'hide_page_buttons', 'true'" in app
    assert "'Pageボタンを非表示'" in app
    assert 'self.hide_page_buttons_action.triggered.connect(self.set_hide_page_buttons)' in app
    assert "getattr(self.launcher, 'hide_page_buttons', True)" in expanded
    assert 'root.addWidget(self.scroll_pad' not in remote
    assert 'self.scroll_pad.hide()' in remote
    assert 'self.scroll_pad.start_from_wheel' not in app  # still calls via local pad
    assert 'pad.start_from_wheel(direction, source=source)' in app
    assert 'self.scroll_pad.flight_settled.connect' in remote
    for s in ('src/app.py', 'src/expanded_view.py','src/launch_remote.py','src/remote_files_explorer.py'):
        ast.parse((ROOT / s).read_text(encoding='utf8'))


def fake_click_detector(monkeypatch):
    scheduled = []
    module = types.ModuleType('PySide6')
    core = types.ModuleType('PySide6.QtCore')
    core.QTimer = SimpleNamespace(singleShot=lambda delay, callback: scheduled.append((delay,callback)))
    monkeypatch.setitem(sys.modules, 'PySide6', module)
    monkeypatch.setitem(sys.modules, 'PySide6.QtCore', core)
    detector = DesktopDoubleClick.__new__(DesktopDoubleClick)
    detector.logger = None
    detector.defer_wallpaper_outside = lambda: True
    detector._deferred_outside_serial = 0
    detector._deferred_outside_pending = False
    detector.user = SimpleNamespace(WindowFromPoint=lambda pt: 901)
    detector._view_at = lambda hwnd: 902
    detector.pair = SimpleNamespace(interval_ms=500, previous=None)
    detector.raw_pair = SimpleNamespace(previous=None)
    detector.is_launcher_visible = lambda: True
    hidden = []
    opened = []
    detector.on_outside_click = lambda: hidden.append('hide')
    detector._empty_wallpaper = lambda x,y,view: True
    detector.on_double_click = lambda click: opened.append(click)
    return detector, scheduled, hidden, opened


def test_desktop_double_click_open_wins_over_single_click_dismiss(monkeypatch):
    detector, pending, hidden, opened = fake_click_detector(monkeypatch)
    click = Click(10, 20, 30, 902)
    assert detector._defer_desktop_click((10,20)) is True
    assert detector._defer_desktop_click((10,20)) is True
    assert len(pending) == 1  # second DOWN cannot arm an additional close
    detector._verify_and_open(click)
    assert opened == [click]
    pending[0][1]()
    assert hidden == []  # old timer cannot close the newly opened Remote


def test_single_desktop_click_still_dismisses_and_disabled_mode_does_not_defer(monkeypatch):
    detector, pending, hidden, opened = fake_click_detector(monkeypatch)
    assert detector._defer_desktop_click((10,20)) is True
    pending[0][1]()
    assert hidden == ['hide'] and not opened
    detector.defer_wallpaper_outside = lambda: False
    assert detector._defer_desktop_click((10,20)) is False
