import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'src/build_output_preflight.py'
spec = importlib.util.spec_from_file_location('build_output_preflight', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class BuildOutputGuardTests(unittest.TestCase):
    def test_empty_dist_is_safe(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertTrue(mod.prepare_build_output(Path(folder), retries=2, wait_seconds=0))

    def test_old_output_is_removed_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            old = root / 'dist' / 'FRBLaunch'
            (old / '_internal').mkdir(parents=True)
            (old / '_internal' / 'VCRUNTIME140.dll').write_bytes(b'dummy dll')
            (root / 'config').mkdir()
            (root / 'config' / 'user.json').write_text('personal settings')
            (root / '.venv').mkdir()
            (root / '.venv' / 'pyvenv.cfg').write_text('venv metadata')
            self.assertTrue(mod.prepare_build_output(root, retries=2, wait_seconds=0))
            self.assertFalse(old.exists())
            self.assertEqual((root / 'config' / 'user.json').read_text(), 'personal settings')
            self.assertEqual((root / '.venv' / 'pyvenv.cfg').read_text(), 'venv metadata')

    def test_retries_lock_then_succeeds(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            old = root / 'dist' / 'FRBLaunch'
            old.mkdir(parents=True)
            orig = mod.shutil.rmtree
            called = []

            def one_lock(path):
                called.append(path)
                if len(called) == 1:
                    raise PermissionError('file locked')
                orig(path)

            with patch.object(mod.shutil, 'rmtree', side_effect=one_lock):
                self.assertTrue(mod.prepare_build_output(root, retries=3, wait_seconds=0))
            self.assertEqual(len(called), 2)

    def test_persistent_lock_fails_early(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            old = root / 'dist' / 'FRBLaunch'
            old.mkdir(parents=True)
            with patch.object(mod.shutil, 'rmtree', side_effect=PermissionError('VCRUNTIME140.dll in use')) as mocked:
                self.assertFalse(mod.prepare_build_output(root, retries=3, wait_seconds=0))
            self.assertEqual(mocked.call_count, 3)
            self.assertTrue(old.exists())

    def test_link_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            external = root / 'external'
            external.mkdir()
            (external / 'keep.txt').write_text('keep')
            (root / 'dist').mkdir()
            try:
                (root / 'dist' / 'FRBLaunch').symlink_to(external, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('directory symlink not supported')
            self.assertFalse(mod.prepare_build_output(root, retries=1, wait_seconds=0))
            self.assertTrue((external / 'keep.txt').is_file())

    def test_build_order_retains_migration(self):
        bat = (SCRIPT.parents[1] / '_build_windows.bat').read_text(encoding='utf-8-sig')
        self.assertLess(bat.index('prepare_launch_home.py\nif errorlevel 1 goto fail'), bat.index('src\\build_output_preflight.py'))
        self.assertLess(bat.index('src\\build_output_preflight.py'), bat.index('PyInstaller --noconfirm'))
        self.assertIn('if %_frb_wait% GEQ 15 goto frb_process_stuck', bat)

if __name__ == '__main__':
    unittest.main()
