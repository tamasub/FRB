"""Safely fail early if PyInstaller's previous FRBLaunch output cannot be removed.

PyInstaller's COLLECT deletes ``dist/FRBLaunch`` near the end of a long build.
That operation may fail on Windows when the previous EXE or one of its DLLs is
still loaded.  Perform the same output cleanup *before* starting PyInstaller so
we can report a useful error immediately instead of losing build time.
"""

from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path


RETRIES = 8
WAIT_SECONDS = 1


def prepare_build_output(root: Path, retries: int = RETRIES, wait_seconds: float = WAIT_SECONDS) -> bool:
    root = Path(root).resolve()
    dist = root / "dist"
    output = dist / "FRBLaunch"

    # Avoid following an unexpected reparse point/symlink into user data.
    if (dist.is_symlink() or output.is_symlink()
            or (hasattr(dist, "is_junction") and dist.is_junction())
            or (hasattr(output, "is_junction") and output.is_junction())):
        print("[ERROR] dist or dist\\FRBLaunch is a link; refusing to remove it.", flush=True)
        return False
    if not output.exists():
        print("[BUILD] Previous output does not exist; continuing.", flush=True)
        return True
    if not output.is_dir():
        print("[ERROR] dist\\FRBLaunch is not a directory; refusing to remove it.", flush=True)
        return False

    print("[BUILD] Checking previous dist\\FRBLaunch for file locks...", flush=True)
    for attempt in range(1, retries + 1):
        try:
            shutil.rmtree(output)
            print("[BUILD] Previous output cleaned successfully.", flush=True)
            return True
        except OSError as exc:
            if attempt < retries:
                print(f"[BUILD] Cleanup attempt {attempt}/{retries}: {exc}; retrying...", flush=True)
                time.sleep(wait_seconds)
            else:
                print("[ERROR] Cannot remove previous dist\\FRBLaunch (file in use or access denied).", flush=True)
                print(f"[ERROR] Locked item / details: {exc}", flush=True)
                print("[ACTION] Exit FRB Launch from the tray and close tools using dist\\FRBLaunch.", flush=True)
                print("[ACTION] Check Windows Task Manager for FRBLaunch.exe; retry the build.", flush=True)
                print("[ACTION] If it remains locked, restart Windows and rebuild before launching FRB Launch.", flush=True)
                print("[INFO] Source files, config, scripts, and .venv were not changed by this step.", flush=True)
                return False
    return False


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    sys.exit(0 if prepare_build_output(project_root) else 1)
