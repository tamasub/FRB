"""Safely move legacy root *.py modules to a backup after the src/ layout is installed.

Only original, byte-identical sources from the supplied source ZIP are moved;
locally changed files are left alone with a clear message.
"""
from __future__ import annotations
import hashlib
from datetime import datetime
from pathlib import Path
import shutil
import sys
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHA256 = {'app.py': '0e7f7c7dca4374a73de3d5ea2236a872c4e9d0afbede27c3a28908c80c82cde9', 'apps_scan_support.py': 'bdfc996a5f6b6113ed8636dcd5d6dc0a24545a804912aff949194e922fc1f3c4', 'bookmark_menu.py': '9ce0a3cc3b3c0f7e1d1f920a8647eb99016f3de00457a76acdc65db36f4f4a25', 'browser_bookmarks.py': 'ad1b5a470baa8a025cb7ebfba1a94fcde3e89bceb4a5c842511e4a5cb66b396c', 'build_output_preflight.py': '41f9803c6e1ed6b6182aadde8389c8a6e76149b74203ce9cf7a24e1a16b3f803', 'cascade_properties.py': '69b74e4621c0f8a0044f48316f9a89ab1045cb70288ebef73da31d1aaa84b449', 'context_menu_actions.py': '63a86f9193731ec77847d914528d405248f177194d9e51d4504f9ff1d221c44f', 'context_menu_config.py': 'e6c9c058cada6240c1124b3af138d924b0770a3c170e6bd0080eb1890d494eef', 'context_menu_resolver.py': '1f69e12da99fa7e095094038ba84daa1dab80a2c476bee292327a8f1de33c530', 'core.py': 'e6e5aa64748adedc6ede0d87e9c3b57ad8d62010b13bea9f0d250221bad52d18', 'desktop_double_click.py': '1c568063e9e78c1edcfffcc2754c9f5924a0e97ad9cd83ec68906365f187c66e', 'enable_app_aliases.py': '68b8c1c080eb0fafa1cd7f8965079ff970d449d5f554571d8f63820d87f5c9ce', 'file_index.py': '61b70ec991fe6c545e58a3cde20682884f8d2f9c617338b92ca9a96932c011fe', 'frame_geometry.py': 'c8d40392655a76178175b96865a33ad1ccdb96a78ebe152e6d1ffc471c011e5d', 'installed_apps.py': '85df94360c5cb4ffff6801b3214b763cf7c2c9c432e74ca6b9e3bfb210d8aa41', 'launch_diagnostics.py': '3493f7288e32ed53c761389613940ca9f6955cb79998e546754f03a0496602bf', 'log_retention.py': 'ccde5e6ad612357a8e77c63c17c17ff7d591fe49daa19563e7ceb55f04fb17d3', 'make_launch_zip.py': '5758c2c4a9a2a85609b5fb071dc23c4d6ff919853b09c1688103dc220d7124bb', 'menu_display.py': '7919d866fefbf8f0ba3ba3454965a9084012594afedaa60c0fa90170b5355852', 'menu_viewport.py': 'a4f34eceed889c40314cbcecaa7f07c902ffc569d54f8f850f164d58f93644bb', 'navigation_wrap.py': '7ef6408fc03bc6cfe18e240ad0128ff3baac3106cf8ef7f391fc8e298dbeef68', 'ordering.py': 'b820b1d5d57ab2ffae8dbe671a038563032826479805c0a8d3087ca2e259e3eb', 'page_tab_focus.py': 'a5d75cc45d289836083e0ae4b0a0789fc7409fd4886cc1205ca72f9e740b8da4', 'page_tab_theme.py': 'd4138821c7393b377b55f07b9500b7ef8e454a0265fdb5ed3c3b7188fce8c6ef', 'prepare_launch_home.py': '704659f12b9700bc7aebcb61ad3a17ae8e3aaf74c746dad247e4a6f917901133', 'process_runner.py': '5a0045e842c9ab4d77b38403f8327a6e4731ff82a2fcb3def2a29f947002d8e3', 'refresh_python_environment.py': 'de69a268ee4b003b215230da0c930a3931b65c9d66de4a3d58640abbb42fe375', 'reorder_widgets.py': '9cfb9370f77acd7629d0c29d2dbda25f7d384cc6cebcdc72bb3eeaf433f59706', 'runtime_paths.py': 'bd0855aa7ec779c74006632fc65cfb3548cfdc49e6b5ae4675b71ac8fa3d75f7', 'search_history.py': '97b4daa3754115ac6f2eae2d53504a47fbfeb6113617ed4b9c09e14f970d6ecc', 'search_matching.py': 'c9c6a6e0002bd7f8726d31a32c83786dde5740c38f3b9ef334541b451324e41d', 'search_result_order.py': 'a9431db6f0481770c60b4391e66ef86adc6a4097ebb0bb4a786be2828df78904', 'windows.py': '4f487c173039bb4fe85539176ce36525b0c8bed948e87df023327f3df9d619eb'}


def migrate(root: Path = PROJECT_ROOT) -> Path | None:
    root = Path(root).resolve()
    unexpected = sorted(path.name for path in root.glob('*.py') if path.name not in EXPECTED_SHA256)
    if unexpected:
        raise RuntimeError('Unknown Python source at project root: ' + ', '.join(unexpected)
                           + '. Review and move it manually before migrating.')
    legacy = [root / name for name in EXPECTED_SHA256 if (root / name).is_file()]
    if not legacy:
        print('[OK] Root Python files already relocated.')
        return None
    missing_new = [path.name for path in legacy if not (root / 'src' / path.name).is_file()]
    if missing_new:
        raise RuntimeError('Missing new src/ modules: ' + ', '.join(missing_new))
    altered = []
    for path in legacy:
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != EXPECTED_SHA256[path.name]:
            altered.append(path.name)
    if altered:
        raise RuntimeError('Root files differ from supplied original source. Not moving anything: '
                           + ', '.join(altered) + '. Please reconcile edits before retrying.')
    backups = root / 'backups'
    backups.mkdir(exist_ok=True)
    stamp = datetime.now().strftime('python_sources_%Y%m%d_%H%M%S')
    destination = backups / stamp
    suffix = 1
    while destination.exists():
        destination = backups / f'{stamp}_{suffix}'
        suffix += 1
    destination.mkdir()
    for path in legacy:
        shutil.move(str(path), str(destination / path.name))
    print(f'[OK] Moved {len(legacy)} legacy .py files to: {destination}')
    print('[OK] Root now has no Python modules; src/ is the active source.')
    return destination


if __name__ == '__main__':
    try:
        migrate()
    except Exception as exc:
        print('[ERROR]', exc, file=sys.stderr)
        sys.exit(1)
