"""Build a COMPLETE FRB Launch + Studio System ZIP (never a source-backup ZIP).

Requires prebuilt Windows runtime directories. Does not build binaries or use
user data. The generated ZIP has system/<path> and a release.json inventory.
"""
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from frb_update.contracts import safe_relative, sha256_file, version_tuple
from frb_update.updater_core import PACKAGE_SCHEMA

BLOCKED_NAMES={'.git','.venv','.venv_backup','__pycache__','node_modules','build','app_zip','backups','updater','userdata','userconfig','.pytest_cache'}
BLOCKED_SUFFIXES={'.pyc','.pyo','.zip','.log','.bak'}

def selectable(path: Path, rel: str):
    if path.is_symlink() or any(p.casefold() in BLOCKED_NAMES for p in Path(rel).parts):return False
    if rel.lower().endswith(('.downloading','.tmp')) or path.suffix.lower() in BLOCKED_SUFFIXES:return False
    if rel.casefold() in {'launch_home.json','config/frb_launch_data.json','state.ini','installed_release.json'}:return False
    # System-only distribution. Studio's wwwroot/data mirror contains user documents,
    # even though it sits below the public web asset tree.
    lower = rel.casefold()
    if lower.startswith(('studio/wwwroot/data/',
                         'studio/wwwroot/images/chat/',
                         'studio/tools/chatgpt-share-export-minimum/output/')):
        return False
    if lower.startswith('studio/tools/') and '/output/' in lower:
        return False
    return True

def collect_files(launch_dist: Path, studio_runtime: Path, launch_source: Path, *, node_exe=None, node_license=None):
    result={}
    for base,prefix in ((launch_dist,''),(studio_runtime,'Studio')):
        if not base.is_dir():raise ValueError(f'ビルド済みディレクトリがありません: {base}')
        for f in sorted(base.rglob('*')):
            if not f.is_file():continue
            rel=f.relative_to(base).as_posix()
            key=f'{prefix}/{rel}' if prefix else rel
            if prefix == 'Studio':
                # Studio has user-authored documents inside data/json/01_main,
                # data/markdown, etc. The updater must NEVER ship these as
                # system-managed payload, even when given a full source tree.
                approved = (rel.startswith(('NativeShell/_publish/', 'wwwroot/',
                                            'defs/', 'tools/', 'runtime/'))
                            or rel.startswith('data/json/00_rules/'))
                if not approved:
                    continue
            if selectable(f,key):result[key]=f
    for folder in ('defs','defaults','scripts','config'):
        base=launch_source/folder
        if not base.is_dir():continue
        for f in sorted(base.rglob('*')):
            if not f.is_file():continue
            key=f.relative_to(launch_source).as_posix()
            if selectable(f,key):result[key]=f
    # Node.js is a runtime dependency, not a reason to ship the same binary twice.
    # Prefer the copy already present under Studio or the Launch dist directory.
    node_target = ('runtime/node/node.exe' if 'runtime/node/node.exe' in result else
                   'Studio/runtime/node/node.exe' if 'Studio/runtime/node/node.exe' in result else None)
    if node_exe is not None:
        exe = Path(node_exe)
        if not exe.is_file(): raise ValueError('Node.exeが見つかりません: ' + str(exe))
        if node_target is None:
            node_target = 'runtime/node/node.exe'
            result[node_target] = exe
    if node_license is not None:
        license_file = Path(node_license)
        if not license_file.is_file(): raise ValueError('Node.js LICENSEが見つかりません: ' + str(license_file))
        if node_target:
            parent = node_target.rsplit('/', 1)[0]
            result.setdefault(parent + '/LICENSE', license_file)
    bat=launch_source/'backup_frb_launch_config_log.bat'
    if bat.is_file():result[bat.name]=bat
    for name in result:safe_relative(name)
    if 'FRBLaunch.exe' not in result:raise ValueError('ビルド済みFRBLaunch.exeが見つかりません')
    if 'Studio/NativeShell/_publish/FRBStudio.NativeShell.exe' not in result:
        raise ValueError('Studio/NativeShell/_publish/FRBStudio.NativeShell.exeが見つかりません')
    if 'Studio/tools/option_settings/cli.mjs' not in result:
        raise ValueError('Studioの合成CLI (tools/option_settings/cli.mjs) が不足しています')
    if 'runtime/node/node.exe' not in result and 'Studio/runtime/node/node.exe' not in result:
        raise ValueError('配布用Node.js実行環境(runtime/node/node.exe)が不足しています')
    return dict(sorted(result.items()))

def build(args):
    for value in (args.version,args.launch_version,args.studio_version):version_tuple(value)
    files=collect_files(args.launch_dist,args.studio_runtime,args.launch_source,
                        node_exe=getattr(args,'node_exe',None), node_license=getattr(args,'node_license',None))
    if args.archive_url:
        from frb_update.contracts import check_source
        check_source(args.archive_url)
        config=args.launch_source/'defs/update/update_sources.json'
        if not config.is_file():raise ValueError('更新元設定がありません: '+str(config))
        sources=json.loads(config.read_text('utf-8-sig'))
        for name in ('updater_feed_url','product_feed_url'):
            check_source(sources.get(name,''))
    manifest={'schema':PACKAGE_SCHEMA,'product':'FRBLaunchIntegrated',
              'version':args.version,'components':{'launch':args.launch_version,'studio':args.studio_version},
              'notes':args.notes or '',
              'files':{name:sha256_file(path) for name,path in files.items()}}
    output=args.output.resolve();output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        archive.writestr('release.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        for name,path in files.items():archive.write(path,'system/'+name)
    from frb_update.updater_core import validate_zip
    validate_zip(output,expected_version=args.version)
    print('ZIP:',output,'\nFiles:',len(files),'\nSHA256:',sha256_file(output))
    if args.archive_url:
        feed={'schema':'frb-product-feed-v1','product':'FRBLaunchIntegrated','version':args.version,
              'components':manifest['components'],'notes':manifest['notes'],'archive_url':args.archive_url,
              'size':output.stat().st_size,'sha256':sha256_file(output)}
        (output.parent/'product_feed.json').write_text(json.dumps(feed,ensure_ascii=False,indent=2)+'\n','utf-8')
        print('Feed:',output.parent/'product_feed.json')

def main():
    p=argparse.ArgumentParser()
    for x in ('launch-dist','studio-runtime','launch-source','output'):p.add_argument('--'+x,required=True,type=Path)
    for x in ('version','launch-version','studio-version'):p.add_argument('--'+x,required=True)
    p.add_argument('--node-exe',type=Path,default=None)
    p.add_argument('--node-license',type=Path,default=None)
    p.add_argument('--notes',default='')
    p.add_argument('--archive-url',default='')
    build(p.parse_args())
if __name__=='__main__':main()
