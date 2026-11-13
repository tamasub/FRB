"""FRB Launch: refresh the project venv after an installed Python update.

Intentionally run using the selected *system* Python, not .venv/Python.
The old environment is moved aside, not deleted, until the new environment
has installed requirements, passed pip check and (by default) rebuilt the app.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PROBE_CODE = (
    "import json, struct, sys; "
    "print(json.dumps({'version': list(sys.version_info[:3]), "
    "'bits': struct.calcsize('P') * 8, 'executable': sys.executable}))"
)


class RefreshError(RuntimeError):
    pass


def find_venv_python(venv: Path) -> Path:
    return venv / "Scripts" / "python.exe"


def python_identity(executable: Path) -> dict | None:
    try:
        result = subprocess.run(
            [str(executable), "-c", PROBE_CODE],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        return json.loads(result.stdout.strip().splitlines()[-1])
    except (OSError, ValueError, IndexError, subprocess.SubprocessError):
        return None


def must_run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    print("[RUN]", " ".join('"'+s+'"' if ' ' in s else s for s in command), flush=True)
    try:
        code = subprocess.run(command, cwd=ROOT, env=env, check=False).returncode
    except OSError as exc:
        raise RefreshError(f"Could not start command: {exc}") from exc
    if code:
        raise RefreshError(f"Command failed with exit code {code}: {command[0]}")


def unique_side_path(label: str) -> Path:
    name = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    for n in range(1000):
        suffix = f"_{n}" if n else ""
        candidate = ROOT / f".{label}_{name}{suffix}"
        if not candidate.exists():
            return candidate
    raise RefreshError("Could not find a unique backup path")


def ensure_requirements() -> Path:
    path = ROOT / "requirements.txt"
    if not path.is_file():
        raise RefreshError("requirements.txt not found; refusing to recreate venv")
    return path


def install_and_check(venv_python: Path, requirements: Path) -> None:
    must_run([str(venv_python), "-m", "pip", "install", "--upgrade", "-r", str(requirements)])
    must_run([str(venv_python), "-m", "pip", "check"])


def run_build() -> None:
    build = ROOT / "_build_windows.bat"
    if not build.is_file():
        raise RefreshError("_build_windows.bat not found")
    env = os.environ.copy()
    env["FRB_ENV_REFRESH"] = "1"
    must_run(["cmd.exe", "/d", "/c", str(build)], env=env)


def rollback(venv: Path, backup: Path | None) -> None:
    if backup is None:
        print("[ROLLBACK] No prior environment existed; removing the incomplete one.", flush=True)
    else:
        print("[ROLLBACK] Restoring the previous .venv ...", flush=True)
    if venv.exists():
        try:
            shutil.rmtree(venv)
        except OSError as exc:
            failed = unique_side_path("venv_failed")
            print(f"[WARN] Cannot delete incomplete .venv ({exc}). Moving aside: {failed}")
            try:
                venv.rename(failed)
            except OSError as inner:
                raise RefreshError(
                    f"Rollback blocked: please move '{venv}' away, then rename '{backup}' to '.venv': {inner}"
                ) from inner
    if backup is not None:
        try:
            backup.rename(venv)
        except OSError as exc:
            raise RefreshError(f"Rollback blocked: rename '{backup}' to '{venv}': {exc}") from exc
    print("[ROLLBACK] Complete.", flush=True)


def refresh(*, force: bool = False, no_build: bool = False) -> int:
    if os.name != "nt":
        print("[ERROR] Run this script on Windows.")
        return 1
    if sys.version_info[:2] != (3, 14) or sys.version_info[:3] < (3, 14, 8) or struct.calcsize("P") != 8:
        print("[ERROR] This updater requires 64-bit Python 3.14.8 or newer (3.14.x).")
        return 1

    print("=== FRB Launch Python environment updater ===", flush=True)
    print(f"[TARGET] Python {sys.version.split()[0]} / {struct.calcsize('P') * 8}bit", flush=True)
    print(f"[TARGET] {sys.executable}", flush=True)
    requirements = ensure_requirements()
    if not no_build and not (ROOT / "_build_windows.bat").is_file():
        raise RefreshError("_build_windows.bat is missing; update is aborted")

    venv = ROOT / ".venv"
    if venv.is_symlink():
        raise RefreshError(".venv is a symbolic link; refusing to modify it automatically")
    current = python_identity(find_venv_python(venv)) if venv.exists() else None
    if current:
        print(f"[CURRENT] Python {'.'.join(map(str, current['version']))} / {current['bits']}bit", flush=True)
    else:
        print("[CURRENT] No usable .venv interpreter was found.", flush=True)

    target_version = list(sys.version_info[:3])
    needs_recreate = force or not current or current.get("version") != target_version or current.get("bits") != 64
    backup: Path | None = None

    if needs_recreate:
        if venv.exists():
            backup = unique_side_path("venv_backup")
            print(f"[BACKUP] {venv} -> {backup}", flush=True)
            try:
                venv.rename(backup)
            except OSError as exc:
                raise RefreshError(f"Could not move .venv. Close processes using the venv: {exc}") from exc
        try:
            # Create directly at .venv. Windows venv entry points are not safely relocatable.
            must_run([sys.executable, "-m", "venv", str(venv)])
            new_python = find_venv_python(venv)
            actual = python_identity(new_python)
            if not actual or actual["version"] != target_version or actual["bits"] != 64:
                raise RefreshError(f"Created .venv did not use the expected Python: {actual}")
            install_and_check(new_python, requirements)
            if not no_build:
                run_build()
        except Exception as exc:
            try:
                rollback(venv, backup)
            except RefreshError as rollback_exc:
                print(f"[ERROR] {rollback_exc}", flush=True)
            raise RefreshError(str(exc)) from exc
    else:
        print("[SKIP] .venv already uses the selected Python patch version.", flush=True)
        install_and_check(find_venv_python(venv), requirements)
        if not no_build:
            run_build()

    if backup is not None:
        print(f"[BACKUP] Previous environment retained: {backup}", flush=True)
        print("         Delete it manually after confirming the new build works.", flush=True)
    print("[SUCCESS] .venv and dependencies are ready.", flush=True)
    if no_build:
        print("[INFO] EXE was not rebuilt because --no-build was specified.", flush=True)
    else:
        print("[SUCCESS] FRBLaunch.exe has been rebuilt in dist\\FRBLaunch.", flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Recreate .venv even when versions match")
    parser.add_argument("--no-build", action="store_true", help="Refresh only the environment, not the EXE")
    args = parser.parse_args()
    try:
        return refresh(force=args.force, no_build=args.no_build)
    except RefreshError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
