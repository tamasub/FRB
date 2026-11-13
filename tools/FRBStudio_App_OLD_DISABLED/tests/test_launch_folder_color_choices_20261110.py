"""FRB Studio: supported folder color picker choices (seven colors)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLOR_KEYS = ('yellow', 'blue', 'green', 'red', 'purple', 'orange', 'gray')
EXCLUDED = {'folder.cyan', 'folder.pink'}


def load_options():
    data = json.loads((ROOT / 'data/json/config/launch_enums_v0_1.json').read_text('utf-8'))
    enum = next(e for ns in data['namespaces'] for e in ns['enums']
                if e.get('enum_ref') == 'launch.icon_key')
    return enum['items']


def test_studio_offers_exactly_seven_folder_colors():
    options = load_options()
    keys = [item['cd'] for item in options]
    assert len(keys) == len(set(keys))
    assert not EXCLUDED.intersection(keys)
    found = [x['cd'] for x in sorted(options, key=lambda x: x['sort_order'])
             if x['cd'].startswith('folder.')]
    assert found == ['folder.' + color for color in COLOR_KEYS]
    for key in found:
        entry = next(x for x in options if x['cd'] == key)
        assert entry['deprecated'] is False
        assert entry['name'].strip()


def test_previous_icon_keys_and_studio_selector_unchanged():
    options = load_options()
    assert {'category.blue', 'folder.yellow', 'archive', 'folder', 'category'}.issubset(
        {x['cd'] for x in options})
    view = json.loads((ROOT / 'defs/launch/frb_launch_maintenance_view_def_v0_1.json').read_text('utf-8'))
    def fields(obj):
        if isinstance(obj, dict):
            if obj.get('field') == 'icon_key':
                yield obj
            for val in obj.values():
                yield from fields(val)
        elif isinstance(obj, list):
            for val in obj:
                yield from fields(val)
    assert any(f.get('valueVocabularyRef') == 'launch.icon_key' and f.get('type') == 'select'
               for f in fields(view))
