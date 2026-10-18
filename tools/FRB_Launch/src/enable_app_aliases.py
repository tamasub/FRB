"""One-time additive migration of existing FRB Launch JSON. Preserves all existing items."""
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
import os

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'config' / 'frb_launch_sample_data_v0_1.json'
source = path.read_text(encoding='utf-8-sig')
data = json.loads(source)
if not isinstance(data, dict): raise ValueError('Launch data must be a JSON object')
changed = False
if 'app_catalog' not in data:
    data['app_catalog'] = {'cache_path': '%LOCALAPPDATA%\\FRBLaunch\\apps_cache.json'}
    changed = True
if 'app_aliases' not in data:
    data['app_aliases'] = []
    changed = True
if changed:
    backup = path.with_suffix('.json.before_app_aliases.bak')
    if not backup.exists(): backup.write_text(source, encoding='utf-8')
    tmp = path.with_suffix('.json.new')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    os.replace(tmp, path)
    print('Migration complete. Backup:', backup)
else:
    print('Already initialized; no change.')
