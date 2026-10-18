"""Source layout regression tests (no GUI dependency)."""
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'

from source_layout_migration import EXPECTED_SHA256, migrate


class SourceLayoutTests(unittest.TestCase):
    def test_all_python_modules_live_in_src(self):
        self.assertFalse(list(ROOT.glob('*.py')))
        self.assertTrue((SRC / 'app.py').is_file())
        self.assertTrue((SRC / 'prepare_launch_home.py').is_file())
        self.assertEqual(set(EXPECTED_SHA256), {p.name for p in SRC.glob('*.py')} - {'source_layout_migration.py'})

    def test_entrypoint_scripts_point_into_src(self):
        batches = ['_build_windows.bat', 'run_windows.bat', '_make_launch_zip.bat', 'update_python_env.bat']
        for name in batches:
            script = (ROOT / name).read_text(encoding='utf-8')
            self.assertIn('src\\', script, name)
        spec = (ROOT / 'FRBLaunch.spec').read_text(encoding='utf-8')
        self.assertIn("['src/app.py']", spec)

    def test_legacy_source_relocation_is_verified_and_backed_up(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'src').mkdir()
            original = (SRC / 'core.py').read_bytes()
            # Migration checks old root bytes against the original ZIP, not the changed src/ module.
            # When src/core.py matches old source exactly the migration succeeds.
            (root / 'src/core.py').write_bytes(original)
            # Test only a byte mismatch, without moving user modified code.
            (root / 'core.py').write_text('local customization', encoding='utf-8')
            with self.assertRaisesRegex(RuntimeError, 'differ'):
                migrate(root)
            self.assertTrue((root / 'core.py').exists())
            self.assertFalse((root / 'backups').exists())

    def test_original_root_file_is_backed_up_and_no_longer_active(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'src').mkdir()
            original = (SRC / 'core.py').read_bytes()
            self.assertEqual(hashlib.sha256(original).hexdigest(), EXPECTED_SHA256['core.py'])
            (root / 'core.py').write_bytes(original)
            (root / 'src/core.py').write_bytes(original)
            backup = migrate(root)
            self.assertIsNotNone(backup)
            self.assertFalse((root / 'core.py').exists())
            self.assertEqual((backup / 'core.py').read_bytes(), original)
            self.assertIsNone(migrate(root))

    def test_source_root_is_parent_of_src(self):
        source = (SRC / 'app.py').read_text(encoding='utf-8')
        self.assertIn("else Path(__file__).resolve().parents[1]", source)
        prepare = (SRC / 'prepare_launch_home.py').read_text(encoding='utf-8')
        self.assertIn("root=Path(__file__).resolve().parents[1]", prepare)


if __name__ == '__main__':
    unittest.main()
