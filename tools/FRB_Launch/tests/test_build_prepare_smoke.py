"""Exercise the exact CLI pre-build step without modifying user files."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]

class BuildPrepareSmokeTests(unittest.TestCase):
    def test_prepare_cli_and_repeated_build(self):
        # The CLI is run as it is in build_windows.bat, but in an isolated home.
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'config').mkdir()
            shutil.copy2(SOURCE / 'config/frb_launch_sample_data_v0_1.json',
                         root / 'config/frb_launch_sample_data_v0_1.json')
            (root / 'src').mkdir()
            for name in ('prepare_launch_home.py', 'core.py', 'browser_bookmarks.py', 'search_matching.py'):
                shutil.copy2(SOURCE / 'src' / name, root / 'src' / name)
            cmd = [sys.executable, str(root / 'src' / 'prepare_launch_home.py')]
            first = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertTrue((root / '.launch_home_ready').is_file())
            canonical = root / 'config/frb_launch_sample_data_v0_1.json'
            before = canonical.read_bytes()
            second = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(canonical.read_bytes(), before)
            linked = subprocess.run(cmd + ['--link'], cwd=root,
                                    capture_output=True, text=True)
            self.assertEqual(linked.returncode, 0, linked.stdout + linked.stderr)
            link = json.loads((root / 'dist/FRBLaunch/launch_home.json').read_text())
            self.assertEqual(link['launch_home'], '../..')

if __name__ == '__main__':
    unittest.main()
