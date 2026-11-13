"""Locate editable files independently of PyInstaller's build output."""
import json
from pathlib import Path
from launch_config_path import CONFIG_NAME, LEGACY_CONFIG_NAME


def launch_home(binary_root):
    root=Path(binary_root).resolve()
    marker=root/'launch_home.json'
    if not marker.exists():return root
    relative=json.loads(marker.read_text(encoding='utf-8'))['launch_home']
    home=(root/relative).resolve()
    config_dir = home / 'config'
    if not any((config_dir / name).is_file() for name in (CONFIG_NAME, LEGACY_CONFIG_NAME)):
        raise RuntimeError('Launch設定が見つかりません: '+str(config_dir / CONFIG_NAME))
    return home


def bundled_studio_root(launch_home_dir):
    """Resolve a sibling Studio from the *installed* Launch location.

    None means standalone/developer Launch: retain its existing configured
    studio_root value. Never consult the process working directory.
    """
    candidate = Path(launch_home_dir) / 'Studio'
    exe = candidate / 'NativeShell' / '_publish' / 'FRBStudio.NativeShell.exe'
    return str(candidate.resolve()) if exe.is_file() else None
