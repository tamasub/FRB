"""Create a source/config backup next to this script (no build artifacts)."""
from datetime import datetime
from pathlib import Path
import os
from zipfile import ZipFile, ZIP_DEFLATED

EXCLUDED = {'.venv','.venv_backup', 'venv', '.git', '__pycache__', '.pytest_cache', 'build', 'dist', 'node_modules', 'backups'}

def make_zip(root):
    root = Path(root).resolve()
    target = root / ('launch_app_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.zip')
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
                        if name=='.launch_home_ready':
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
    print(make_zip(Path(__file__).parent))
