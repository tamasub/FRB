"""2026-11-10: Data-only emoji palette extension for FRB Launch."""
from pathlib import Path
from core import load, join_selection_values, searchable_rows

ROOT = Path(__file__).resolve().parents[1]
DATA = load(ROOT / 'config/frb_launch_data.json')


def palette():
    return sorted((c for c in DATA['launch_choices']
                   if c.get('group_id') == '絵文字'),
                  key=lambda c: c.get('sort_order', 0))


def test_palette_uses_existing_selection_item():
    owners = [i for i in DATA['items']
              if i.get('launch_selection_group_id') == '絵文字']
    assert len(owners) == 1
    owner = owners[0]
    assert owner['item_kind'] == 'selection'
    assert owner['launch_selection_value_field'] == 'value'
    assert any(s['launch_action_type'] == 'SendKey'
               and s['launch_text'] == '%recipients%'
               for s in owner['launch_actions'])


def test_original_two_rows_preserved_and_30_new_groups_added():
    rows = palette()
    assert len(rows) == 32
    face = next(r for r in rows if r['choice_id'] == '😋_copy_1')
    hearts = next(r for r in rows if r['choice_id'] == '💓_copy_1')
    assert face['value'] == '😀😃😄😆😅🤣🫠😇🥰🤩'
    assert hearts['value'] == '💘💖💓💞💟🩷🧡💛💚💙🤎🖤🩵💜🩶🤍'
    assert [r['choice_id'] for r in rows[2:]] == [
        f'frb_emoji_palette_{n:02d}' for n in range(1, 31)]
    assert [r['sort_order'] for r in rows[2:]] == list(range(30, 330, 10))


def test_group_rows_are_active_searchable_and_send_literal_emoji():
    rows = palette()
    for row in rows:
        assert row['enabled'] is True
        assert row['description'] == row['value']
        assert row['value'].strip()
        assert '\\u' not in row['value']
    assert len({r['choice_id'] for r in DATA['launch_choices']}) == len(DATA['launch_choices'])
    hits = [(r,path) for r,path in searchable_rows(DATA,'釣り・海')
            if r.get('group_id') == '絵文字']
    assert len(hits) == 1
    assert hits[0][0]['title'] == '🎣釣り・海'
    owner = next(i for i in DATA['items']
                 if i.get('launch_selection_group_id') == '絵文字')
    chosen = [next(r for r in rows if 'AI・アイデア' in r['title']),
              next(r for r in rows if '研究・計測' in r['title'])]
    assert join_selection_values(owner, chosen) == '\n'.join(c['value'] for c in chosen)


def test_other_selection_groups_left_untouched():
    assert len([r for r in DATA['launch_choices'] if r['group_id'] == 'sales']) == 5
    assert len([r for r in DATA['launch_choices'] if r['group_id'] == 'se']) == 4
