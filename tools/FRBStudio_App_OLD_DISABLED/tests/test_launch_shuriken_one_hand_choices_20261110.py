"""FRB Studio Launch data editor exposes authorable 手裏剣・一の手 properties."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_launch_studio_item_editor_has_first_hand_controls():
    view = json.loads((ROOT/'defs/launch/frb_launch_maintenance_view_def_v0_1.json').read_text('utf8'))
    item_section = next(s for s in view['views'][0]['sections'] if s['id'] == 'items')
    fields = {r['field']: r for r in item_section['fields']}
    enabled = fields['shuriken_enabled']
    assert enabled['type'] == 'boolean'
    assert enabled['edit']['visible'] is True
    assert fields['shuriken_order']['type'] == 'number'
    assert fields['shuriken_direction']['options'][0] == ''
    assert fields['shuriken_only']['type'] == 'boolean'
    assert all(fields[key]['visibleWhen'] == {'field':'shuriken_enabled','equals':True}
               for key in ('shuriken_order','shuriken_direction','shuriken_only',
                           'shuriken_context_action_id'))
    assert 'shuriken_button_index' not in fields  # Always 1の手 in this editor.
