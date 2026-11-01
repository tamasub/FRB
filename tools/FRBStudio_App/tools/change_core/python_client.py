"""FRB Studio ChangeSet CLI subprocess adapter (no HTTP server, Python stdlib only).

Call run_changeset with a fully constructed ChangeSet dict; the caller owns
business values and must provide a trustworthy original base_sha256.
The trusted CLI config holds the allowlisted document paths.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping


def file_sha256(path: str | Path) -> str:
    """Raw-byte SHA-256. Call when the source document is initially read."""
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_changeset(
    request: Mapping[str, Any], *, node_executable: str | Path,
    cli_path: str | Path, config_path: str | Path, timeout_seconds: int = 120
) -> dict[str, Any]:
    """Run one ChangeSet and return the machine-readable result (including rejections).

    node_executable may point at a bundled node.exe. No PATH lookup is required.
    A nonzero CLI exit is normal for a rejected ChangeSet, not a Python error.
    """
    result = subprocess.run(
        [str(node_executable), str(cli_path), "--config", str(config_path)],
        input=json.dumps(request, ensure_ascii=False),
        text=True, capture_output=True, encoding="utf-8", timeout=timeout_seconds,
        check=False,
    )
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"ChangeSet CLI invalid response (exit={result.returncode}): "
                           f"{result.stderr[:400]}") from exc
    if response.get("schema_version") != "studio_changeset_result_v0_1":
        raise RuntimeError("ChangeSet CLI returned an unexpected schema_version")
    return response
