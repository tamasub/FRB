import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import installed_apps

def test_aliases_only_in_search_keywords():
    data={'items':[{'item_id':'installed_apps','page_id':'x','item_kind':'category','launch_source':'installed_apps'}],
          'app_aliases':[{'kind':'aumid','target':'APP1','alias':'仕事のエディタ'}]}
    source=[{'name':'ToolA','target':'app1','kind':'aumid','icon_path':''},
            {'name':'ToolB','target':'APP2','kind':'aumid','icon_path':''}]
    combined=installed_apps.attach(data,source)
    a=next(i for i in combined['items'] if i.get('title')=='ToolA')
    b=next(i for i in combined['items'] if i.get('title')=='ToolB')
    assert '仕事のエディタ' in a['keywords']
    assert '仕事のエディタ' not in b['keywords']
    assert source[0]['name']=='ToolA'
    assert data['items']==[{'item_id':'installed_apps','page_id':'x','item_kind':'category','launch_source':'installed_apps'}]
    assert all('app_aliases' not in i for i in combined['items'])

def test_orphan_alias_and_identity_separation():
    data={'items':[{'item_id':'installed_apps','page_id':'x','item_kind':'category','launch_source':'installed_apps'}],
          'app_aliases':[{'kind':'shortcut','target':'app1','alias':'Shortcut only'},
                         {'kind':'aumid','target':'removed','alias':'orphan'}]}
    source=[{'name':'X','target':'app1','kind':'aumid','icon_path':''}]
    app=installed_apps.attach(data,source)['items'][-1]
    assert not app['keywords']
