"""Build FRB Launch + Studio portable ZIP and the SAME Updater-compatible ZIP.

Input: prebuilt Windows EXEs, Launch source, Studio source. Never copies the
AppData user profile; never builds executables or modifies either source tree.
The Updater's own EXE is bootstrap-owned, not in the product update manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path
from types import SimpleNamespace

from build_release_package import build as build_update_zip

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from frb_update.contracts import sha256_file, version_tuple
from frb_update.updater_core import validate_zip


def get_node_exe(launch_dist: Path, studio: Path, explicit: Path | None):
    candidates = ([explicit] if explicit else []) + [
        launch_dist / 'runtime/node/node.exe',
        studio / 'runtime/node/node.exe',
    ]
    if not explicit:
        path = shutil.which('node.exe') or shutil.which('node')
        if path:
            candidates.append(Path(path))
    return next((p.resolve() for p in candidates if p and p.is_file()), None)


def find_node_license(node: Path, explicit: Path | None, launch_dist: Path, studio: Path):
    candidates = ([explicit] if explicit else []) + [
        node.parent / 'LICENSE', node.parent / 'NODE_LICENSE.txt',
        launch_dist / 'runtime/node/LICENSE', launch_dist / 'runtime/node/NODE_LICENSE.txt',
        studio / 'runtime/node/LICENSE', studio / 'runtime/node/NODE_LICENSE.txt',
    ]
    return next((p.resolve() for p in candidates if p and p.is_file()), None)


def archive_text(name: str, value: str):
    return zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))


def write_portable(update_zip: Path, portable_zip: Path, updater_exe: Path,
                   updater_version: str, approved: bool):
    """Transform validated system inventory into a directly launchable folder.

    `installed_release.json` allows version UI and future updater stale-file
    cleanup to recognize the exact set of System-owned files on first launch.
    """
    manifest = validate_zip(update_zip)
    prefix = 'FRBLaunch/'
    with zipfile.ZipFile(update_zip) as source, zipfile.ZipFile(portable_zip, 'w',
                       zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as dest:
        for name in sorted(manifest['files']):
            with source.open('system/' + name) as reader, dest.open(prefix + name, 'w', force_zip64=True) as writer:
                shutil.copyfileobj(reader, writer, 1024 * 1024)
        text = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
        dest.writestr(prefix + 'installed_release.json', text.encode('utf-8'))
        with updater_exe.open('rb') as reader, dest.open(
                prefix + f'updater/versions/{updater_version}/FRBUpdater.exe', 'w', force_zip64=True) as writer:
            shutil.copyfileobj(reader, writer, 1024 * 1024)
        dest.writestr(prefix + 'Start_FRB_Launch.bat', (
            '@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\n'
            'if not exist "FRBLaunch.exe" (echo [ERROR] FRBLaunch.exe not found & pause & exit /b 1)\r\n'
            'start "" "%~dp0FRBLaunch.exe"\r\n').encode('ascii'))
        if not approved:
            dest.writestr(prefix + 'PRIVATE_REVIEW_NOT_FOR_PUBLIC_RELEASE.txt',
                'PRIVATE REVIEW ONLY. The included initialization template may contain personal menus, paths or URLs.\r\n'
                'Review defaults/frb_launch_data.template.json and config/*.json before a public release.\r\n')
    # Repeat the content check on the portable archive, not just the update ZIP.
    with zipfile.ZipFile(portable_zip) as archive:
        for name, expected in manifest['files'].items():
            digest = hashlib.sha256()
            with archive.open(prefix + name) as fp:
                for chunk in iter(lambda: fp.read(1024 * 1024), b''):
                    digest.update(chunk)
            if digest.hexdigest() != expected:
                raise ValueError('Portable payload SHA-256 mismatch: ' + name)
        if (json.loads(archive.read(prefix + 'installed_release.json')) != manifest):
            raise ValueError('Installed inventory differs from product update archive')


def build(args):
    for version in (args.version, args.launch_version, args.studio_version, args.updater_version):
        version_tuple(version)
    launch = args.launch_source.resolve()
    studio = args.studio_source.resolve()
    dist = launch / 'dist/FRBLaunch'
    updater = launch / 'dist/updater/FRBUpdater.exe'
    if not dist.joinpath('FRBLaunch.exe').is_file():
        raise FileNotFoundError('Launch EXE missing. Run _build_windows.bat: ' + str(dist))
    if not (studio / 'NativeShell/_publish/FRBStudio.NativeShell.exe').is_file():
        raise FileNotFoundError('Studio EXE missing. Run cmd_compile_NativeShell.bat: ' + str(studio))
    if not updater.is_file():
        raise FileNotFoundError('Updater EXE missing. Run _build_updater_windows.bat: ' + str(updater))
    if not (launch / 'scripts/build_release_package.py').is_file():
        raise FileNotFoundError('Current updater release builder missing from Launch/scripts')
    template = launch / 'defaults/frb_launch_data.template.json'
    if not template.is_file():
        raise FileNotFoundError('User initialization template missing: ' + str(template))
    # A deliberate check: the template is the user-approved latest snapshot,
    # not a synthesized empty example and never copied from AppData.
    obj = json.loads(template.read_text('utf-8-sig'))
    if not isinstance(obj, dict) or 'pages' not in obj or 'items' not in obj:
        raise ValueError('Template is not a valid Launch data JSON document')
    node = get_node_exe(dist, studio, args.node_exe)
    if node is None:
        raise FileNotFoundError('Node.js runtime unavailable. Specify --node-exe pointing to node.exe')
    license_file = find_node_license(node, args.node_license, dist, studio)
    if license_file is None:
        raise FileNotFoundError('Node.js LICENSE unavailable. Specify --node-license from official Node.js distribution')
    output = args.output.resolve()
    for candidate in (launch, studio, dist):
        if output == candidate or candidate.is_relative_to(output):
            raise ValueError('Output must not contain a source tree')
    output.mkdir(parents=True, exist_ok=True)
    marker = '' if args.approve_template else '_PRIVATE_REVIEW'
    portable = output / f'FRBLaunch_{args.version}{marker}_portable.zip'
    product = output / f'FRBLaunch_{args.version}{marker}_update.zip'
    for file in (product, portable):
        if file.exists():
            raise FileExistsError(f'Existing release ZIP will not be overwritten: {file}')
    args_release = SimpleNamespace(
        launch_dist=dist, studio_runtime=studio, launch_source=launch,
        output=product, version=args.version, launch_version=args.launch_version,
        studio_version=args.studio_version, notes=args.notes,
        archive_url=args.archive_url, node_exe=node, node_license=license_file,
    )
    build_update_zip(args_release)
    write_portable(product, portable, updater, args.updater_version, args.approve_template)
    # Stage the updater EXE as a separate feed upload artifact.
    updater_upload = output / f'FRBUpdater_{args.updater_version}.exe'
    if updater_upload.exists() and sha256_file(updater_upload) != sha256_file(updater):
        raise FileExistsError('Existing updater binary conflicts with this build: ' + str(updater_upload))
    if not updater_upload.exists():
        shutil.copy2(updater, updater_upload)
    if args.updater_url:
        from frb_update.contracts import check_source
        check_source(args.updater_url)
        feed = {'schema': 'frb-updater-feed-v1', 'version': args.updater_version,
                'url': args.updater_url, 'size': updater_upload.stat().st_size,
                'sha256': sha256_file(updater_upload)}
        feed_path = output / 'updater_feed.json'
        if feed_path.exists():
            raise FileExistsError('Updater feed already exists: ' + str(feed_path))
        feed_path.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    hashes = output / f'SHA256_{args.version}.txt'
    hashes.write_text('\n'.join(f'{sha256_file(x)}  {x.name}' for x in (portable, product, updater_upload)) + '\n', 'utf-8')
    report = output / f'README_配布確認_{args.version}.txt'
    report.write_text((
        f'FRB Launch + Studio integrated release {args.version}\n'
        f'Launch: {args.launch_version} / Studio: {args.studio_version} / Updater: {args.updater_version}\n'
        f'Portable install ZIP: {portable.name} (extract FRBLaunch/ and launch the EXE)\n'
        f'Updater full ZIP:    {product.name} (release.json + system/, do NOT extract directly)\n'
        f'Updater EXE:        {updater_upload.name} (publish for bootstrap)\n'
        f'Node.exe:           {node}\n'
        f'Node license:       {license_file}\n'
        'UserData/UserConfig/state.ini/Studio research data not copied.\n'
        'The System template is preserved EXACTLY as in Launch/defaults.\n'
        'Source launch_home.json is excluded from the portable install.\n'
        'Updater and Product feed files are generated only when corresponding HTTPS URLs are provided.\n'
        'Before external publication review template and system configs for private paths, identities and URLs.\n'
        f'Human approved release template: {args.approve_template}\n'
        'Test on a second Windows PC BEFORE external release.\n'
    ), 'utf-8')
    print('[OK] Portable:', portable)
    print('[OK] Updater full ZIP:', product)
    print('[OK] Updater EXE:', updater_upload)
    print('[OK] SHA256:', hashes)
    if not args.approve_template:
        print('[WARNING] PRIVATE REVIEW ONLY: approve the existing template before public distribution.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--launch-source', type=Path, required=True)
    p.add_argument('--studio-source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    for name in ('version', 'launch-version', 'studio-version', 'updater-version'):
        p.add_argument('--' + name, required=True)
    p.add_argument('--archive-url', default='')
    p.add_argument('--updater-url', default='')
    p.add_argument('--node-exe', type=Path)
    p.add_argument('--node-license', type=Path)
    p.add_argument('--notes', default='')
    p.add_argument('--approve-template', action='store_true',
                   help='Human-reviewed latest Launch template and system options for external distribution')
    args = p.parse_args()
    try:
        build(args)
    except Exception as exc:
        print('[ERROR]', str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
