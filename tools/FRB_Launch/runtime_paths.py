"""Locate editable files independently of PyInstaller's build output."""
import json
from pathlib import Path


def launch_home(binary_root):
    root=Path(binary_root).resolve()
    marker=root/'launch_home.json'
    if not marker.exists():return root
    relative=json.loads(marker.read_text(encoding='utf-8'))['launch_home']
    home=(root/relative).resolve()
    if not (home/'config/frb_launch_sample_data_v0_1.json').is_file():
        raise RuntimeError('Launch設定が見つかりません: '+str(home/'config/frb_launch_sample_data_v0_1.json'))
    return home
