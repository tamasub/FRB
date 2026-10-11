"""One-time migration before rebuilding; never resync from dist afterwards."""
import json,shutil
from pathlib import Path
from datetime import datetime
from uuid import uuid4

READY='.launch_home_ready'
CONFIG=Path('config/frb_launch_sample_data_v0_1.json')

def repair_wifi(data):
    # launch_scripts becomes a runtime variable derived from the actual launch home.
    data['launch_variables']=[v for v in data.get('launch_variables',[]) if v['variable_id']!='launch_scripts']
    for row in data['items']:
        for step in row.get('launch_actions',[]):
            args=step.get('launch_arguments',[])
            if step.get('launch_action_type')!='Run' or '-File' not in args:continue
            index=args.index('-File')+1
            if index>=len(args) or not args[index].replace('\\','/').lower().endswith('/connect-wifi.ps1'):continue
            args[index]='%launch_scripts%\\Connect-Wifi.ps1'
            if '-ExecutionPolicy' not in args:args[0:0]=['-ExecutionPolicy','Bypass']
            step['launch_show_console']=True;step['launch_wait_for_exit']=True;step['launch_timeout_ms']=60000
        if row['item_id'] in ('cam','fft'):
            for step in row.get('launch_actions',[]):
                if step.get('launch_action_type')=='Open':step['launch_browser']='chrome'
    return data


def prepare(root):
    root=Path(root).resolve();legacy=root/'dist/FRBLaunch'
    ready=root/READY
    if ready.exists():
        if not (root/CONFIG).exists():raise RuntimeError('Canonical config is missing; restore it from backups.')
        return None
    backup=root/'backups'/('launch_home_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid4().hex[:6])
    backup.mkdir(parents=True)
    for tag,base in [('source',root),('previous_dist',legacy)]:
        for name in ('config','scripts'):
            if (base/name).is_dir():shutil.copytree(base/name,backup/tag/name)
    # The old EXE/Studio edited dist; preserve that active data during initial migration.
    origin=legacy/CONFIG if (legacy/CONFIG).exists() else root/CONFIG
    data=repair_wifi(json.loads(origin.read_text(encoding='utf-8-sig')))
    from core import validate
    validate(data)
    if (legacy/'scripts').is_dir():
        shutil.copytree(legacy/'scripts',root/'scripts',dirs_exist_ok=True)
    dest=root/CONFIG;dest.parent.mkdir(parents=True,exist_ok=True)
    temp=dest.with_suffix('.migration.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(dest)
    ready.write_text('Editable config/scripts are in this project root. Do not restore dist files.\n',encoding='utf-8')
    return backup


def link_build(root):
    root=Path(root).resolve();output=root/'dist/FRBLaunch';output.mkdir(parents=True,exist_ok=True)
    (output/'launch_home.json').write_text(json.dumps({'launch_home':'../..'})+'\n',encoding='utf-8')

if __name__=='__main__':
    import sys
    root=Path(__file__).parent
    if '--link' in sys.argv:link_build(root)
    else:
        backup=prepare(root)
        print('Launch home:',root)
        print('Config:',root/CONFIG)
        if backup:print('Previous files backed up:',backup)
