"""Headless contract tests for the Remote breadcrumb-folder entry point."""
import ast
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1] / 'src'


def source(name):
    return (ROOT / name).read_text(encoding='utf-8')


class RemoteCurrentFolderTests(unittest.TestCase):
    def test_directory_enumeration_is_one_level_and_folders_first(self):
        # Compile only the filesystem helper: PySide6 is Windows-only in CI.
        tree = ast.parse(source('remote_folder_menu.py'))
        function = next(n for n in tree.body
                        if isinstance(n, ast.FunctionDef) and n.name == 'directory_entries')
        module = ast.Module(body=[function], type_ignores=[])
        namespace = {'os': __import__('os')}
        exec(compile(ast.fix_missing_locations(module), '<directory_entries>', 'exec'), namespace)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'B').mkdir()
            (root / 'B' / 'nested').mkdir()
            (root / 'a.txt').write_text('a', encoding='utf-8')
            (root / 'Z.txt').write_text('z', encoding='utf-8')
            names = [entry[0] for entry in namespace['directory_entries'](root)]
            self.assertEqual(names, ['B', 'a.txt', 'Z.txt'])

    def test_remote_row_exposes_label_and_command(self):
        remote = source('launch_remote.py')
        self.assertIn('（カレントフォルダー操作）', remote)
        self.assertIn('REMOTE_CURRENT_FOLDER_MENU', remote)
        self.assertIn('def set_files_mode(self, enabled)', remote)

    def test_external_navigation_and_remote_navigation_are_distinguished(self):
        app = source('app.py')
        view = source('expanded_view.py')
        self.assertIn('def on_files_directory_changed(self, directory):', app)
        self.assertIn("getattr(self, '_remote_folder_navigation', False)", app)
        self.assertIn('changed(self.current_directory())', view)
        self.assertIn('self.launcher._remote_folder_navigation = True', source('remote_folder_menu.py'))
        self.assertIn('view.go_to_directory(path, preserve_remote_popup=True)', source('remote_folder_menu.py'))

    def test_file_context_forces_search_result_safety(self):
        app = source('app.py')
        remote = source('remote_folder_menu.py')
        self.assertIn('force_search_context=False', app)
        self.assertIn('bool(force_search_context)', app)
        self.assertIn('force_search_context=True', remote)
        self.assertIn('visible_search_context_entries', app)
        self.assertIn("elif (action_id == 'open_parent_folder' and origin == 'file'", app)

    def test_click_and_hover_do_not_share_commit(self):
        menu = source('remote_folder_menu.py')
        self.assertIn('lambda p=path: self.commit_directory(p)', menu)
        self.assertIn('child = RemoteFolderListMenu(', menu)
        self.assertIn('self.addMenu(child)', menu)
        self.assertIn('self.open_entry_context(p, folder, at)', menu)
        self.assertIn('self.open_file(p)', menu)


if __name__ == '__main__':
    unittest.main()
