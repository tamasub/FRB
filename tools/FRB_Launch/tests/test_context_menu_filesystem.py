"""Source routing, JSON allowlist and safe file operations without Qt/Windows."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from context_menu_resolver import resolve_context_target
from context_menu_config import load_context_menus
from context_menu_actions import rename_file_or_folder

CONFIG = Path(__file__).resolve().parents[1] / 'config/context_menu_options.json'


class SourceRoutingTests(unittest.TestCase):
    def setUp(self):
        self.authored = [
            {'item_id': 'bookmark_root', 'item_kind': 'category', 'launch_source': 'browser_bookmarks'},
            {'item_id': 'app_root', 'item_kind': 'category', 'launch_source': 'installed_apps'},
            {'item_id': 'Files', 'item_kind': 'directory', 'launch_browse_target': 'C:/somewhere'},
            {'item_id': 'file_action', 'item_kind': 'command'},
        ]

    def test_real_authored_entries_are_studio_owned(self):
        for row in self.authored:
            self.assertEqual(resolve_context_target(row, self.authored), ('studio', None))

    def test_browser_imports_never_launch_studio(self):
        for row in (
            {'item_id': 'bm', 'item_kind': 'command', '_browser_bookmark': True},
            {'item_id': 'bookmark_root', '_browser_bookmark': True},  # collision
            {'item_id': 'bm_group', 'item_kind': 'category', '_browser_bookmark': True},
        ):
            self.assertEqual(resolve_context_target(row, self.authored), ('none', None))

    def test_app_imports_never_launch_studio(self):
        for row in (
            {'item_id': '__app_42', '_installed_app': True},
            {'item_id': 'app_root', '_installed_app': True},  # collision
        ):
            self.assertEqual(resolve_context_target(row, self.authored), ('none', None))

    def test_generated_fs_rows_and_index(self):
        cases = (
            ({'item_id': 'C:/a/folder', 'item_kind': 'directory', '_file': 'C:/a/folder'},
             ('folder', 'C:/a/folder')),
            ({'item_id': 'C:/a/test.py', 'item_kind': 'command', '_file': 'C:/a/test.py',
              '_browse_file': 'C:/a/test.py'}, ('file', 'C:/a/test.py')),
            ({'item_id': '__file_index_C:/a/test.py', '_indexed_file': 'C:/a/test.py'},
             ('file', 'C:/a/test.py')),
            ({'item_id': 'file_action', 'item_kind': 'command', '_file': 'C:/a/test.py'},
             ('file', 'C:/a/test.py')),
        )
        for row, expected in cases:
            with self.subTest(row=row):
                self.assertEqual(resolve_context_target(row, self.authored), expected)

    def test_no_inferred_file_by_suffix_or_title(self):
        self.assertEqual(resolve_context_target({'item_id': 'x', 'title': 'demo.txt',
                                                 'item_kind': 'command'}, self.authored), ('none', None))
        self.assertEqual(resolve_context_target(None, self.authored), ('none', None))


class ConfigTests(unittest.TestCase):
    def test_exact_v1_actions_no_new_or_delete(self):
        menus = load_context_menus(CONFIG)
        self.assertEqual([x['action_id'] for x in menus['file']],
                         ['copy_full_path', 'copy_file_name', 'rename', 'properties'])
        self.assertEqual([x['action_id'] for x in menus['folder']],
                         ['open_explorer', 'open_terminal', 'copy_path', 'rename', 'properties'])

    def test_actions_are_validated_against_allowlist(self):
        with TemporaryDirectory() as folder:
            options = json.loads(CONFIG.read_text(encoding='utf-8'))
            options['menus']['file'].append({'action_id': 'run_shell', 'title': '危険'})
            path = Path(folder) / 'bad.json'
            path.write_text(json.dumps(options), encoding='utf-8')
            with self.assertRaises(ValueError):
                load_context_menus(path)

    def test_disabled_action(self):
        with TemporaryDirectory() as folder:
            options = json.loads(CONFIG.read_text(encoding='utf-8'))
            options['menus']['file'][0]['enabled'] = False
            path = Path(folder) / 'config.json'
            path.write_text(json.dumps(options), encoding='utf-8')
            self.assertEqual(len(load_context_menus(path)['file']), 3)


class RenameTests(unittest.TestCase):
    def test_file_rename_preserves_bytes(self):
        with TemporaryDirectory() as folder:
            p = Path(folder) / 'old.txt'
            p.write_bytes(b'abc')
            destination = rename_file_or_folder(p, 'new.txt')
            self.assertEqual(destination.read_bytes(), b'abc')
            self.assertFalse(p.exists())

    def test_directory_rename(self):
        with TemporaryDirectory() as folder:
            p = Path(folder) / 'old'
            p.mkdir()
            (p / 'child.txt').write_text('ok')
            destination = rename_file_or_folder(p, 'new')
            self.assertEqual((destination / 'child.txt').read_text(), 'ok')

    def test_collisions_and_invalid_names(self):
        with TemporaryDirectory() as folder:
            p = Path(folder) / 'old.txt'
            q = Path(folder) / 'other.txt'
            p.touch();q.touch()
            with self.assertRaises(FileExistsError):
                rename_file_or_folder(p, q.name)
            for name in ('x\\y', '..', 'CON.txt', 'x.', 'trailing ', 'a:b', 'NUL'):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    rename_file_or_folder(p, name)
            self.assertTrue(p.exists())


if __name__ == '__main__':
    unittest.main()

class ActualLauncherRoutingTests(unittest.TestCase):
    """Execute the real Launcher routing method with a QMenu stub, no Qt import."""
    @staticmethod
    def setup():
        import ast
        import types
        from unittest.mock import Mock
        source = (CONFIG.parent.parent / 'app.py').read_text(encoding='utf-8')
        tree = ast.parse(source)
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
        fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'show_launch_context_menu')
        code = ast.Module(body=[fn], type_ignores=[])
        ast.fix_missing_locations(code)

        class Menu:
            def __init__(self, parent): self.parent = parent; self.actions = []; self.at = None
            def addAction(self, title, callback): self.actions.append((title, callback))
            def isEmpty(self): return not self.actions
            def popup(self, at): self.at = at
        scope = {'QMenu': Menu, 'resolve_context_target': resolve_context_target,
                 'load_context_menus': load_context_menus, 'CONTEXT_MENU_OPTIONS': CONFIG}
        exec(compile(code, '<real Launcher.show_launch_context_menu>', 'exec'), scope)
        holder = types.SimpleNamespace(
            data={'items': [{'item_id':'app', '_installed_app':True}]},
            selection=None, stack=[], search=types.SimpleNamespace(text=lambda: ''),
            authored_items=[{'item_id':'my_setting','item_kind':'command'}],
            hover_timer=types.SimpleNamespace(stop=lambda: None), pending_menu_item=None,
            launch_configuration_studio=Mock(), perform_filesystem_context_action=Mock())
        return scope['show_launch_context_menu'], holder

    def test_physical_folder_menu_calls_correct_action_including_checked(self):
        fn, holder = self.setup()
        self.assertTrue(fn(holder, (3, 4), {'item_kind': 'directory', '_file': 'C:/x'}))
        menu = holder._launch_context_menu
        self.assertEqual(len(menu.actions), 5)
        menu.actions[3][1](True)  # Qt QAction.triggered(bool) must not override action ID
        holder.perform_filesystem_context_action.assert_called_once_with('rename', 'C:/x', 'folder')
        holder.launch_configuration_studio.assert_not_called()

    def test_virtual_app_bookmark_ignored_even_if_merged_into_data(self):
        fn, holder = self.setup()
        for row in ({'item_id':'app', '_installed_app': True},
                    {'item_id':'bookmark', '_browser_bookmark': True}):
            self.assertFalse(fn(holder, (3, 4), row))
            holder.launch_configuration_studio.assert_not_called()

    def test_authored_properties_still_targets_item_id(self):
        fn, holder = self.setup()
        row = {'item_id': 'my_setting', 'item_kind': 'command'}
        self.assertTrue(fn(holder, (3, 4), row))
        holder._launch_context_menu.actions[0][1](True)
        holder.launch_configuration_studio.assert_called_once_with(item_id='my_setting')

    def test_file_index_search_results_get_windows_file_menu(self):
        fn, holder = self.setup()
        holder.search.text = lambda: 'report'
        row = {'item_id':'__file_index_foo', '_indexed_file': 'C:/x/report.txt'}
        self.assertTrue(fn(holder, (3, 4), row))
        self.assertEqual(len(holder._launch_context_menu.actions), 4)

