"""New search column/order regression tests without Qt GUI runtime."""
import ast
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from search_result_order import display_columns, sort_search_pairs
from file_index import launch_steps


class SearchSortAndRoutesTests(unittest.TestCase):
    def test_sort_title_in_both_directions(self):
        pairs=[({'title':'Zulu'},'A'),({'title':'alpha'},'C'),({'title':'Beta'},'B')]
        self.assertEqual([r['title'] for r,_ in sort_search_pairs(pairs,0)],['alpha','Beta','Zulu'])
        self.assertEqual([r['title'] for r,_ in sort_search_pairs(pairs,0,True)],['Zulu','Beta','alpha'])
        self.assertEqual(pairs[0][0]['title'],'Zulu')

    def test_sort_description_in_both_directions(self):
        pairs=[({'title':'z','description':'C:\\z'},'ファイル索引'),
               ({'title':'a','description':'C:\\a'},'ファイル索引'),
               ({'title':'b','description':'C:\\m'},'ファイル索引')]
        self.assertEqual([r['title'] for r,_ in sort_search_pairs(pairs,1)],['a','b','z'])
        self.assertEqual([r['title'] for r,_ in sort_search_pairs(pairs,1,True)],['z','b','a'])

    def test_sort_uses_only_displayed_columns_not_hidden_metadata(self):
        pairs=[({'title':'bar','description':'z','launch_actions':[{'launch_action_type':'Open'}]},''),
               ({'title':'foo','description':'a','launch_actions':[{'launch_action_type':'Run'}]},'')]
        self.assertEqual([r['title'] for r,_ in sort_search_pairs(pairs,1)],['foo','bar'])
        self.assertEqual(display_columns({'title':'f','item_kind':'directory','description':'d'},'Path'),('f  ›','d  ·  Path'))

    def test_md_studio_command_with_real_executable(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); studio=root/'studio'
            binary=studio/'NativeShell'/'_publish'/'FRBStudio.NativeShell.exe'
            binary.parent.mkdir(parents=True);binary.write_bytes(b'')
            md=root/'memo.md';md.write_text('hello')
            steps=launch_steps(md, str(studio))
            self.assertEqual(steps[0]['launch_action_type'],'Run')
            self.assertEqual(steps[0]['launch_arguments'],['--open-md='+str(md)])
            self.assertEqual(launch_steps(md, str(root/'missing'))[0]['launch_action_type'],'Open')

    def test_folder_routing_is_shared_with_index_routing(self):
        # GUI Qt isn't installed in CI, inspect Python AST for the connection.
        tree=ast.parse((ROOT/'src/app.py').read_text(encoding='utf8'))
        clazz=next(node for node in tree.body if isinstance(node,ast.ClassDef) and node.name=='Launcher')
        funcs={node.name:node for node in clazz.body if isinstance(node,ast.FunctionDef)}
        children=ast.get_source_segment((ROOT/'src/app.py').read_text(encoding='utf8'),funcs['children'])
        activate=ast.get_source_segment((ROOT/'src/app.py').read_text(encoding='utf8'),funcs['activate'])
        runner=ast.get_source_segment((ROOT/'src/app.py').read_text(encoding='utf8'),funcs['run_file_path'])
        self.assertIn('_browse_file',children)
        self.assertIn('_indexed_file',activate)
        self.assertIn('_browse_file',activate)
        self.assertIn('self.run_file_path(row, file_path)',activate)
        self.assertIn('file_index.launch_steps(',runner)


if __name__=='__main__':unittest.main()
