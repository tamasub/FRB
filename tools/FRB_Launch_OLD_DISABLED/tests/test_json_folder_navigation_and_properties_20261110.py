"""2026-11-10: internally opened authored folders + Files Exp Studio Properties.

GUI wiring is covered by AST contract checks so this suite also runs in
headless/Linux environments where PySide6 / Windows Explorer are unavailable.
"""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))

from registered_folder_route import embedded_folder_target
from launch_virtual_tree import virtual_launch_pages, virtual_item_identity, virtual_studio_target


def test_authored_open_of_existing_directory_routes_into_launch(tmp_path):
    directory = tmp_path / 'FRB folder with spaces'
    directory.mkdir()
    step = {'launch_action_type': 'Open', 'launch_target': str(directory)}
    assert embedded_folder_target([step]) == str(directory)
    # Folder from a command item (not just an explicit directory row) works.
    assert embedded_folder_target((step,)) == str(directory)
    assert embedded_folder_target([{'launch_action_type': 'Open',
                                    'launch_target': str(tmp_path / 'missing')}]) is None
    file = directory / 'abc.txt'
    file.write_text('OK')
    assert embedded_folder_target([{'launch_action_type': 'Open',
                                    'launch_target': str(file)}]) is None


def test_existing_url_shell_run_browser_and_multistep_keep_their_meaning(tmp_path):
    step = {'launch_action_type': 'Open', 'launch_target': str(tmp_path)}
    assert embedded_folder_target([step, step]) is None
    assert embedded_folder_target([{**step, 'launch_action_type': 'Run'}]) is None
    assert embedded_folder_target([{**step, 'launch_browser': 'chrome'}]) is None
    assert embedded_folder_target([{**step, 'launch_browser_profile': 'Work'}]) is None
    for special in ('https://example.com', 'shell:Downloads', 'file:///C:/a'):
        assert embedded_folder_target([{'launch_action_type': 'Open', 'launch_target': special}],
                                      is_dir=lambda p: True) is None
    assert embedded_folder_target([step], is_dir=lambda p: (_ for _ in ()).throw(OSError())) is None


def test_properties_target_resolves_only_real_authored_page_or_item():
    pages = [{'page_id': 'work', 'title': 'My Work', 'enabled': True}]
    rows = [
        {'page_id': 'work', 'item_id': 'folder', 'item_kind': 'category',
         'title': 'ZIP', 'parent_item_id': '', 'enabled': True},
        {'page_id': 'work', 'item_id': 'disabled', 'item_kind': 'category',
         'title': 'Not editable', 'enabled': False},
    ]
    page = virtual_launch_pages(pages, rows)[0]
    folder = page['children'][0]
    assert virtual_studio_target(virtual_item_identity(page), pages, rows) == {
        'kind': 'page', 'page_id': 'work'}
    assert virtual_studio_target(virtual_item_identity(folder), pages, rows) == {
        'kind': 'item', 'page_id': 'work', 'item_id': 'folder'}
    assert virtual_studio_target({'source':'launch_json', 'page_id':'work',
        'item_id':'disabled', 'node_id':'item:work:disabled'}, pages, rows) is None
    assert virtual_studio_target({'source':'launch_json', 'page_id':'work',
        'item_id':'runtime', 'node_id':'item:work:runtime'}, pages, rows) is None
    assert virtual_studio_target({'source':'launch_json', 'page_id':'work',
        'item_id':'folder', 'node_id':'item:work:other'}, pages, rows) is None
    assert virtual_studio_target(virtual_item_identity(page),
                                  [{**pages[0], 'enabled': False}], rows) is None
    assert virtual_studio_target({'source':'filesystem', 'page_id':'work',
        'node_id':'page:work'}, pages, rows) is None
    assert virtual_studio_target({'source':'launch_json', 'page_id':'work',
        'item_id':'bookmark', 'node_id':'item:work:bookmark'}, pages,
        [*rows, {'page_id': 'work', 'item_id': 'bookmark', '_browser_bookmark': True}]) is None


def method_source(path, cls, name):
    code = ast.parse((SRC / path).read_text(encoding='utf-8'))
    owner = next(n for n in code.body if isinstance(n, ast.ClassDef) and n.name == cls)
    method = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.unparse(method)


def test_execute_checks_directory_before_external_launch_and_dismiss():
    source = method_source('app.py', 'Launcher', 'execute')
    assert 'folder_target = embedded_folder_target(self.queue)' in source
    assert 'self.open_search_folder_in_launch(folder_target)' in source
    assert source.index('folder_target = embedded_folder_target(self.queue)') < source.index('self.busy = True')


def test_virtual_properties_launches_studio_for_selected_exp_page_not_tab():
    context = method_source('app.py', 'Launcher', 'show_virtual_launch_context')
    studio = method_source('app.py', 'Launcher', 'launch_configuration_studio')
    assert 'virtual_studio_target(identity, self.pages, self.authored_items)' in context
    assert '詳細編集...' in context
    assert 'launch_configuration_studio(page_properties=True, page_id=pid)' in context
    assert 'launch_configuration_studio(item_id=iid)' in context
    assert 'target_page_id = str(page_id if page_id is not None else self.page_id)' in studio
    assert "'--launch-page-id=' + target_page_id" in studio
    assert "'--launch-item-id=' + str(item_id)" in studio


def test_virtual_folder_icon_is_distinct_from_real_folder_and_page_stays_iconless():
    source = method_source('remote_files_explorer.py', 'RemoteFilesExplorer', '_append_virtual')
    assert "self._virtual_folder_icon" in source
    assert "self._folder_icon" not in source
    assert "node['kind'] == 'page'" in source
    init = method_source('remote_files_explorer.py', 'RemoteFilesExplorer', '__init__')
    assert "#8675d6" in init
    assert 'self._virtual_folder_icon' in init


def test_real_execute_uses_internal_navigation_without_dismissing(tmp_path):
    """Exercise production execute() with a Qt-free fake launcher, not just AST text."""
    import logging
    from types import MethodType
    import file_index
    tree = ast.parse((SRC / 'app.py').read_text(encoding='utf-8'))
    owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    function = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == 'execute')
    env = {'DIAG': logging.getLogger('test-folder-open'),
           'embedded_folder_target': embedded_folder_target,
           'file_index': file_index}
    exec(compile(ast.Module(body=[function], type_ignores=[]), '<app-execute>', 'exec'), env)

    class LauncherStub:
        busy = False
        def __init__(self):
            self.queue = []
            self.opened = []
            self.dismissed = False
            self.expander = lambda values=None: type('Expanded', (), {
                'values': {}, 'expand': lambda self, text: text})()
        def open_bookmark_web_view(self, row): return False
        def open_registered_step_in_browser(self, step): return False
        def open_search_folder_in_launch(self, folder):
            self.opened.append(folder)
            return True
        def dismiss(self): self.dismissed = True
        def error(self, error): raise AssertionError(str(error))

    stub = LauncherStub()
    stub.execute = MethodType(env['execute'], stub)
    folder = tmp_path / 'Folder to Launch'
    folder.mkdir()
    stub.execute({'item_id': 'open-folder', 'title': 'Folder', 'item_kind': 'directory',
                  'launch_actions': [{'launch_action_type': 'Open', 'launch_target': str(folder)}]})
    assert stub.opened == [str(folder)]
    assert stub.queue == []
    assert not stub.busy and not stub.dismissed
