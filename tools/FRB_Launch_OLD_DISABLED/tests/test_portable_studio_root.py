# Standalone tests: no PySide6 required.
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from runtime_paths import bundled_studio_root

class PortableStudioRootTests(unittest.TestCase):
    def test_moving_bundle_keeps_studio_discovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'Folder With Space'
            exe = root / 'Studio' / 'NativeShell' / '_publish' / 'FRBStudio.NativeShell.exe'
            exe.parent.mkdir(parents=True)
            exe.write_bytes(b'test')
            other = Path(tmp) / 'other'
            other.mkdir()
            with patch('os.getcwd', return_value=str(other)):
                self.assertEqual(bundled_studio_root(root), str((root / 'Studio').resolve()))
            moved = Path(tmp) / 'moved'
            root.rename(moved)
            self.assertEqual(bundled_studio_root(moved), str((moved / 'Studio').resolve()))

    def test_without_bundled_studio_keeps_developer_setting(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(bundled_studio_root(tmp))

if __name__ == '__main__':
    unittest.main()
