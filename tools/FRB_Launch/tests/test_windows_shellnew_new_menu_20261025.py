"""Windows ShellNew discovery/new creation without requiring Qt or Windows."""
import tempfile
import unittest
from pathlib import Path

from windows_shellnew import (create_new_item, discover_shellnew, suggest_name,
                              validate_name)


class NewFileTests(unittest.TestCase):
    def test_create_folder_and_rename(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            folder = create_new_item(p, '新しいフォルダー', 'folder')
            self.assertTrue(folder.is_dir())
            changed = folder.rename(p / '変更後の名前')
            self.assertTrue(changed.is_dir())

    def test_create_txt_md_and_no_double_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            txt = create_new_item(p, 'メモ', 'txt')
            md = create_new_item(p, 'ノート.md', 'md')
            self.assertEqual(txt.name, 'メモ.txt')
            self.assertEqual(md.name, 'ノート.md')
            self.assertEqual(txt.read_bytes(), b'')
            self.assertEqual(md.read_bytes(), b'')
            self.assertEqual(create_new_item(p, 'README.MD', 'md').name, 'README.MD')

    def test_existing_names_are_not_overwritten_even_in_different_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / 'Example.TXT').write_text('original', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                create_new_item(p, 'example.txt', 'txt')
            self.assertEqual((p / 'Example.TXT').read_text(encoding='utf-8'), 'original')
            self.assertEqual(suggest_name(p, 'Example', '.TXT'), 'Example (2).TXT')

    def test_no_directory_traversal_or_reserved_names(self):
        for name in ('', '.', '..', '../oops', '..\\oops', 'CON', 'con.txt', 'LPT1',
                     'a:b', 'a?b', 'a.', 'a ', 'bad\nname'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_name(name)

    def test_nonexistent_destination_and_unsupported_formats(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            with self.assertRaises(FileNotFoundError):
                create_new_item(p / 'missing', 'file', 'txt')
            with self.assertRaises(ValueError):
                create_new_item(p, 'report.docx', 'docx')
            self.assertFalse((p / 'report.docx').exists())

    def test_repeated_default_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            create_new_item(p, '新しいフォルダー', 'folder')
            create_new_item(p, '新しいフォルダー (2)', 'folder')
            self.assertEqual(suggest_name(p, '新しいフォルダー'), '新しいフォルダー (3)')


class RegistryFake:
    HKEY_CLASSES_ROOT = object()

    def __init__(self):
        self.extensions = ['.txt', '.md', '.docx', '.foo', '.ignored', 'random']
        self.values = {
            '.txt\\ShellNew': {'NullFile': ''},
            '.md\\ShellNew': {'NullFile': ''},
            '.docx\\Word.Document.12\\ShellNew': {'FileName': 'template.docx'},
            '.foo\\ShellNew': {'Command': 'unsafe.exe %1'},
            '.ignored\\ShellNew': {},
            '.docx': {'': 'Word.Document.12'},
            'Word.Document.12': {'': 'Microsoft Word 文書'},
        }

    def EnumKey(self, root, index):
        try:
            return self.extensions[index]
        except IndexError:
            raise OSError('done')

    class Key:
        def __init__(self, entries):
            self.entries = entries
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False

    def OpenKey(self, root, key):
        if key not in self.values:
            raise OSError(key)
        return self.Key(self.values[key])

    def QueryValueEx(self, key, value):
        if value not in key.entries:
            raise OSError(value)
        return key.entries[value], None


class RegistryTests(unittest.TestCase):
    def test_registered_types_discovered_without_executing_commands(self):
        types = discover_shellnew(RegistryFake())
        self.assertIn(('.txt', '.txt ファイル', 'NullFile'), types)
        self.assertIn(('.docx', 'Microsoft Word 文書', 'FileName'), types)
        self.assertIn(('.foo', '.foo ファイル', 'Command'), types)
        self.assertNotIn('.ignored', [e[0] for e in types])
        self.assertNotIn('random', [e[0] for e in types])


class UIWiringTests(unittest.TestCase):
    def test_lane_menu_and_double_click_are_independent(self):
        source = (Path(__file__).resolve().parents[1] / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
        self.assertIn('def show_lane_new_menu(', source)
        self.assertIn('menu.addMenu(\'新規作成\')', source)
        self.assertIn('event.type() == QEvent.Type.ContextMenu', source)
        self.assertIn('self.handle_middle_back_double_click(obj, event)', source)
        self.assertIn('self.go_up()', source)
        self.assertIn('create_new_item(current, name, kind)', source)
        self.assertIn('action.setEnabled(False)', source)

    def test_error_status_uses_red_x_and_escaped_html(self):
        source = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf-8')
        method = source[source.index('    def error(self, message):'):]
        self.assertIn('❌', method[:600])
        self.assertIn('html_escape(str(message))', method[:600])


if __name__ == '__main__':
    unittest.main()
