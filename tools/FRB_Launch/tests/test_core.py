import sys, unittest, copy, os
from unittest.mock import patch
from pathlib import Path
from datetime import datetime
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import load, validate, Expander, searchable_rows, column_filter_match
DATA=load(Path(__file__).resolve().parents[1]/'config/frb_launch_sample_data_v0_1.json')
class CoreTests(unittest.TestCase):
 def test_calendar_and_formats(self):
  e=Expander(DATA,now=datetime(2026,1,1,3,4,5))
  self.assertEqual(e.expand('%yesterday:yyyyMMdd% %now:yyyy/MM/dd HH:mm:ss%'),'20251231 2026/01/01 03:04:05')
 def test_literal_and_non_recursive(self):
  e=Expander(DATA,clipboard='%today%')
  self.assertEqual(e.expand('校正してください。%clipboard% 100%%'),'校正してください。%today% 100%')
 def test_unknown(self):
  with patch.dict(os.environ, {'missing': ''}, clear=False):
   # Defined-but-empty is valid, unknown still raises.
   self.assertEqual(Expander(DATA).expand('%missing%'), '')
  with patch.dict(os.environ, {}, clear=True):
   with self.assertRaises(ValueError):Expander(DATA).expand('%missing%')
 def test_windows_userprofile_fallback(self):
  with patch.dict(os.environ, {'USERPROFILE': r'C:\Users\Sample'}, clear=True):
   target = r'%USERPROFILE%\OneDrive\ドキュメント\Book1.xlsx'
   self.assertEqual(Expander(DATA).expand(target), r'C:\Users\Sample\OneDrive\ドキュメント\Book1.xlsx')
 def test_windows_env_names_case_insensitive(self):
  with patch.dict(os.environ, {'APPDATA': r'C:\Users\Sample\AppData\Roaming'}, clear=True):
   self.assertEqual(Expander(DATA).expand(r'%appdata%\settings.json'),
                    r'C:\Users\Sample\AppData\Roaming\settings.json')
 def test_launch_variables_override_windows_environment(self):
  with patch.dict(os.environ, {'launch_dir': r'C:\wrong'}, clear=True):
   ex = Expander(DATA, values={'launch_dir': r'F:\FRB\tools'})
   self.assertEqual(ex.expand(r'%launch_dir%\script.bat'), r'F:\FRB\tools\script.bat')
 def test_environment_fallback_remains_nonrecursive(self):
  with patch.dict(os.environ, {'USERPROFILE': r'C:\Users\%today%'}, clear=True):
   self.assertEqual(Expander(DATA).expand('%USERPROFILE%'), r'C:\Users\%today%')
 def test_literal_percent_not_changed(self):
  with patch.dict(os.environ, {'USERPROFILE': r'C:\Users\Sample'}, clear=True):
   self.assertEqual(Expander(DATA).expand('100%%'), '100%')
 def test_all_page_search(self):
  self.assertEqual({r['item_id'] for r,p in searchable_rows(DATA,'appdata')},{'roaming','local'})
 def test_cycle(self):
  d=copy.deepcopy(DATA);d['items'][0]['parent_item_id']=d['items'][0]['item_id']
  with self.assertRaises(ValueError):validate(d)
 def test_disabled_parent(self):
  d=copy.deepcopy(DATA)
  next(r for r in d['items'] if r['item_id']=='locations')['enabled']=False
  self.assertEqual(searchable_rows(d,'appdata'),[])
 def test_column_filter_avoids_parent_path_false_matches(self):
  row={'title':'notes','description':r'F:\\FRB\\notes','_file':r'F:\\FRB\\notes'}
  self.assertFalse(column_filter_match(row,'FRB'))
  self.assertTrue(column_filter_match(row,'NOTES'))
 def test_column_filter_descriptions_and_multiple_words(self):
  row={'title':'Launch settings','description':'System tools'}
  self.assertTrue(column_filter_match(row,'settings SYSTEM'))
  self.assertFalse(column_filter_match(row,'settings archive'))
 def test_recipients(self):
  self.assertEqual(Expander(DATA,values={'recipients':'a; b'}).expand('%recipients%'),'a; b')
if __name__=='__main__':unittest.main()
