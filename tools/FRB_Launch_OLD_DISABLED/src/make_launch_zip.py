"""Create a source/config backup in the app_zip directory (no build artifacts)."""
from datetime import datetime
from pathlib import Path
import os
import subprocess
import sys
from zipfile import ZipFile, ZIP_DEFLATED

EXCLUDED = {'.venv','.venv_backup', 'venv', '.git', '__pycache__', '.pytest_cache', 'build', 'dist', 'node_modules', 'backups', 'app_zip'}

def make_zip(root):
    root = Path(root).resolve()
    # A new button dialog must never silently bypass the ぐりぐり selector.
    # Fail source-ZIP creation BEFORE writing the artifact if this contract breaks.
    if (root / 'src/app.py').is_file():  # Actual Launch source, not a config-only backup fixture.
        for contract_script in ('check_dialog_contract.py', 'check_context_menu_contract.py'):
            subprocess.run([sys.executable, str(root / 'scripts' / contract_script)],
                           cwd=root, check=True)
    output_dir = root / 'app_zip'
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / ('launch_app_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.zip')
    # Exclusive creation avoids overwriting a backup made in the same second.
    with target.open('xb') as output:
        try:
            with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
                for directory, dirs, files in os.walk(root, followlinks=False):
                    def allowed(name):
                        path = Path(directory) / name
                        junction = getattr(os.path, 'isjunction', lambda p: False)
                        return name.casefold() not in EXCLUDED and not path.is_symlink() and not junction(path)
                    dirs[:] = sorted(d for d in dirs if allowed(d))
                    for name in sorted(files):
                        path = Path(directory) / name
                        if name in {'.launch_home_ready', '.frb_launch_data_name_v1'}:
                            continue
                        if path.is_symlink() or path.suffix.lower() in {'.zip', '.pyc', '.pyo', '.log'}:
                            continue
                        archive.write(path, path.relative_to(root))
        except BaseException:
            output.close()
            target.unlink(missing_ok=True)
            raise
    return target

if __name__ == '__main__':
    print(make_zip(Path(__file__).resolve().parents[1]))
