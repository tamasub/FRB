import copy,json,tempfile,unittest
from pathlib import Path
from core import validate,searchable_rows,Expander
from installed_apps import normalize,attach,read_cache,write_cache

class InstalledAppsTests(unittest.TestCase):
    def setUp(self):
        self.data={'pages':[{'page_id':'windows','title':'Windows'}], 'items':[{'item_id':'apps','page_id':'windows','parent_item_id':'','title':'アプリ','item_kind':'category','launch_source':'installed_apps'}]}
    def test_filters_launch_helpers_but_keeps_programs(self):
        names=['Arduino IDE','Microsoft Visual C++ 2022 Redistributable','Microsoft .NET Runtime','Windows SDK','Uninstall Audacity','Audacity','Framework Designer','Brave','README']
        records=[dict(name=n,target=n,kind='aumid') for n in names]
        self.assertEqual([r['name'] for r in normalize(records)],['Arduino IDE','Audacity','Brave','Framework Designer'])
    def test_dynamic_rows_search_launch_and_do_not_mutate_config(self):
        original=copy.deepcopy(self.data)
        records=[dict(name='Google Chrome',target='Chrome.App',kind='aumid'),dict(name='Tool',target=r'C:\50%stuff\Tool.lnk',kind='shortcut')]
        data=validate(attach(self.data,records));self.assertEqual(self.data,original)
        result=searchable_rows(data,'クローム');self.assertEqual(len(result),1)
        self.assertEqual(result[0][0]['launch_actions'][0]['launch_target'],r'shell:AppsFolder\Chrome.App')
        tool=next(r for r in data['items'] if r['title']=='Tool')
        self.assertEqual(Expander(data).expand(tool['launch_actions'][0]['launch_target']),r'C:\50%stuff\Tool.lnk')
        self.assertEqual(attach(data,records),data)
    def test_dedup_keeps_distinct_ids_with_same_name(self):
        rows=[dict(name='Tool',target=id,kind='aumid') for id in ['A','a','B']]
        self.assertEqual(len(normalize(rows)),2)
    def test_disabled_parent_is_not_searchable(self):
        self.data['items'][0]['enabled']=False
        data=attach(self.data,[dict(name='Excel',target='excel',kind='aumid')])
        self.assertEqual(searchable_rows(data,'Excel'),[])
    def test_cache_and_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'cache.json';self.assertEqual(read_cache(p),[])
            rows=[dict(name='Word',target='Word.App',kind='aumid')]
            write_cache(p,rows);self.assertEqual(read_cache(p),normalize(rows))
            p.write_text('{broken');self.assertEqual(read_cache(p),[])
    def test_runtime_items_are_not_saved_by_reorder(self):
        from ordering import reordered
        data=copy.deepcopy(self.data)
        data['items'].append(dict(item_id='sound',page_id='windows',title='Sound',item_kind='command'))
        saved=reordered(data,'windows','',['sound','apps'])
        self.assertFalse(any(r.get('_installed_app') for r in saved['items']))
        shown=attach(saved,[dict(name='Word',target='word',kind='aumid')])
        self.assertEqual(len(shown['items']),3)

if __name__=='__main__':unittest.main()
