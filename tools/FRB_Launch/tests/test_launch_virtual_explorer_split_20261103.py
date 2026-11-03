"""Contract: Launch JSON navigation is split between Exp folders and List items."""
import ast
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC))
from launch_virtual_tree import (virtual_launch_pages, virtual_exp_folders,
                                 virtual_list_rows, virtual_item_identity,
                                 virtual_lookup_node)


def sample():
    pages = [{'page_id': 'work'}, {'page_id': 'frb'}, {'page_id': 'windows'}]
    rows = [
        {'page_id':'work', 'item_id':'nest', 'parent_item_id':'',
         'title':'作業道具', 'item_kind':'category', 'sort_order':10},
        {'page_id':'work', 'item_id':'child', 'parent_item_id':'nest',
         'title':'ZIP', 'item_kind':'category', 'sort_order':5},
        {'page_id':'work', 'item_id':'leaf', 'parent_item_id':'nest',
         'title':'昨日の日付', 'item_kind':'command', 'sort_order':10,
         'launch_actions':[{'launch_action_type':'Send', 'launch_text':'%yesterday%'}]},
        {'page_id':'work', 'item_id':'under', 'parent_item_id':'child',
         'title':'ZIPを作成', 'item_kind':'command', 'sort_order':10},
        {'page_id':'work', 'item_id':'root_leaf', 'parent_item_id':'',
         'title':'今日の日付', 'item_kind':'command', 'sort_order':20},
        {'page_id':'work', 'item_id':'empty', 'parent_item_id':'',
         'title':'空フォルダー', 'item_kind':'category', 'sort_order':30},
    ]
    return pages, rows


def test_exp_has_only_folders_and_list_has_direct_members():
    pages, items = sample()
    root = virtual_launch_pages(pages, items)[0]
    assert [n['title'] for n in virtual_exp_folders(root)] == ['作業道具', '空フォルダー']
    assert [(row['title'],row['item_kind']) for row in virtual_list_rows(root)] == [
        ('作業道具','category'), ('今日の日付','virtual_launch_file'),
        ('空フォルダー','category')]
    nest = root['children'][0]
    assert [n['title'] for n in virtual_exp_folders(nest)] == ['ZIP']
    assert [row['title'] for row in virtual_list_rows(nest)] == ['ZIP','昨日の日付']


def test_terminal_node_retains_authored_action_and_stable_identity():
    pages, items = sample()
    folder = virtual_lookup_node(pages,items,'work','nest')
    row = virtual_list_rows(folder)[1]
    assert row['_launch_virtual_node']['row'] is items[2]
    assert row['item_kind'] == 'virtual_launch_file'
    assert not any(key in row for key in ('_browse_file','_file','_indexed_file'))
    assert virtual_item_identity(row['_launch_virtual_node'])['item_id']=='leaf'


def test_breadcrumb_and_lineage_identify_only_selected_ancestors():
    pages, items = sample()
    nested = virtual_lookup_node(pages,items,'work','child')
    assert nested['breadcrumbs'] == ('My Work','作業道具','ZIP')
    assert nested['lineage'] == ('page:work','item:work:nest','item:work:child')
    assert virtual_lookup_node(pages,items,'windows')['title']=='Windows'
    assert virtual_lookup_node(pages,items,'work','missing') is None


def test_empty_category_still_projects_as_explorer_folder():
    pages, items = sample()
    folder = virtual_lookup_node(pages,items,'work','empty')
    assert folder['kind']=='folder'
    assert virtual_list_rows(folder)==[]


def between(file, left, right):
    src = (SRC / file).read_text(encoding='utf-8')
    return src.split('    def '+left+'(',1)[1].split('    def '+right+'(',1)[0]


def test_files_exp_lazy_tree_never_adds_launch_file_rows():
    impl = between('remote_files_explorer.py','_expand_index','_tree_node_key')
    assert 'virtual_exp_folders(virtual)' in impl
    assert 'for child in virtual.get' not in impl
    assert 'remote_select_virtual_node' in (SRC / 'remote_files_explorer.py').read_text(encoding='utf-8')


def test_preview_does_not_steal_exp_operating_target():
    preview = between('remote_files_explorer.py','_commit_current_selection','_activate_index')
    assert 'self.virtual_folder_selected.emit(virtual)' in preview
    assert "remote_focus_area('directory')" not in preview
    switch = between('app.py','remote_exp_right_to_list','remote_list_left_to_exp')
    assert 'navigate_virtual_launch_folder' in switch


def test_physical_deletes_are_fenced_out_of_virtual_list():
    selected = between('expanded_view.py','middle_selected_paths','rename_selected_middle_item')
    assert "if getattr(self, '_virtual_directory_node', None) is not None:" in selected
    assert 'return []' in selected
    menu = between('expanded_view.py','context_menu','apply_theme')  # may be large
    assert "row.get('_launch_virtual_node') is not None" in menu


def test_virtual_row_activation_delegates_to_existing_launch_executor():
    virtual = between('expanded_view.py','enter_row','root_action')
    assert 'self.launcher.activate_virtual_launch_item' in virtual
    app = between('app.py','activate_virtual_launch_item','show_virtual_launch_context')
    assert 'self.activate(authoritative)' in app


def test_virtual_list_search_and_physical_return_have_separate_branches():
    source = (SRC / 'expanded_view.py').read_text(encoding='utf-8')
    assert 'virtual_list_rows(virtual)' in source
    assert 'self._virtual_directory_node = None' in between('expanded_view.py','go_to_directory','select_middle_file')
    assert 'self._virtual_directory_node = None' in between('expanded_view.py','choose_files','choose_middle')


def test_python_syntax_check():
    for filename in ('app.py','launch_remote.py','expanded_view.py',
                     'remote_files_explorer.py','launch_virtual_tree.py'):
        ast.parse((SRC / filename).read_text(encoding='utf-8'))
