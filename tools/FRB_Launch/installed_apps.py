"""Launchable application catalog; cached separately from user configuration."""
import copy
import hashlib
import json
import os
import re
import unicodedata
from pathlib import Path

EXCLUDE = re.compile(r'アンインストール|uninstall|readme|release notes|リリースノート|^(?:help|ヘルプ)(?:\s|$)|(?:visual c\+\+.*redistributable|\.net.*(?:runtime|framework)|windows.*(?:sdk|driver kit)|webview2.*runtime)', re.I)
ALIASES = {'chrome':['クローム'], 'excel':['エクセル'], 'word':['ワード'], 'powerpoint':['パワーポイント'], 'chatgpt':['チャットgpt'], 'claude':['クロード'], 'arduino':['アルドゥイーノ'], 'notepad':['メモ帳'], 'calculator':['電卓']}

def normalize(records):
    if not isinstance(records,list):raise ValueError('アプリ一覧の形式が不正です')
    result=[];seen=set()
    for r in records:
        if not isinstance(r,dict):raise ValueError('アプリ一覧の項目が不正です')
        name=str(r.get('name','')).strip();target=str(r.get('target','')).strip()
        kind=r.get('kind')
        if not name or not target or kind not in ('aumid','shortcut'):continue
        if EXCLUDE.search(name):continue
        if kind=='shortcut' and not target.lower().endswith('.lnk'):continue
        key=(kind,target.casefold())
        if key in seen:continue
        seen.add(key)
        result.append({'name':name,'target':target,'kind':kind,'icon_path':str(r.get('icon_path',''))})
    return sorted(result,key=lambda r:unicodedata.normalize('NFKC',r['name']).casefold())

def alias_by_identity(data):
    """User-authored sparse search aliases. Only (kind,target) identifies an app."""
    result = {}
    for row in data.get('app_aliases', []):
        if not isinstance(row, dict):
            continue
        kind = str(row.get('kind', '')).strip()
        target = str(row.get('target', '')).strip()
        alias = str(row.get('alias', '')).strip()
        if kind in ('aumid', 'shortcut') and target and alias:
            result[(kind, target.casefold())] = alias
    return result


def attach(data, records):
    result=copy.deepcopy(data)
    result['items']=[r for r in result['items'] if not r.get('_installed_app')]
    used={r['item_id'] for r in result['items']}
    custom_aliases=alias_by_identity(data)
    for parent in list(result['items']):
        if parent.get('launch_source')!='installed_apps' or parent['item_kind']!='category':continue
        for index,r in enumerate(normalize(records),1):
            identity=parent['item_id']+'\0'+r['kind']+'\0'+r['target']
            id='__app_'+hashlib.sha256(identity.encode()).hexdigest()
            if id in used:continue
            used.add(id)
            keywords=[a for term,aliases in ALIASES.items() if term in r['name'].casefold() for a in aliases]
            custom=custom_aliases.get((r['kind'],r['target'].casefold()),'')
            if custom: keywords.append(custom)
            # AUMIDs can contain %; escape them for the launcher's variable expander.
            target=('shell:AppsFolder\\'+r['target'] if r['kind']=='aumid' else r['target']).replace('%','%%')
            result['items'].append(dict(item_id=id,page_id=parent['page_id'],parent_item_id=parent['item_id'],
                title=r['name'],description='インストール済みアプリ',item_kind='command',icon_key='application',
                enabled=True,sort_order=index,keywords=keywords,launch_actions=[{'launch_action_type':'Open','launch_target':target}],
                _installed_app=True,_icon_file=r['icon_path']))
    return result

def read_cache(path):
    try:
        data=json.loads(Path(path).read_text(encoding='utf-8-sig'))
        if data.get('version')!=1:return []
        return normalize(data['apps'])
    except (OSError,ValueError,TypeError,KeyError,AttributeError):return []

def write_cache(path, records):
    path=Path(path);temp=path.with_suffix('.tmp')
    try:
        temp.write_text(json.dumps({'version':1,'apps':normalize(records)},ensure_ascii=False,indent=2),encoding='utf-8')
        os.replace(temp,path)
    finally:temp.unlink(missing_ok=True)
