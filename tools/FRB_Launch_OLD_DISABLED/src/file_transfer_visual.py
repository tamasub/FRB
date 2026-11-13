"""Pure transfer-feedback rules shared by normal and scrolling folder cascades.

Cut is pending transfer (subdued); pasted items are confirmed results (teal).
Path identity is Windows-style case insensitive without depending on Qt.
"""
from pathlib import Path
import os


def path_key(path):
    return os.path.normpath(os.path.abspath(str(path))).replace('\\', '/').casefold()


def transfer_state(path, *, cut_paths=(), pasted_paths=()):
    if path is None:
        return ''
    key = path_key(path)
    if key in {path_key(value) for value in cut_paths}:
        return 'cut'
    if key in {path_key(value) for value in pasted_paths}:
        return 'pasted'
    return ''


def pasted_paths_for(destination, names):
    return [str(Path(destination) / name) for name in names]


def moved_source_parent_directories(plan, *, move=False):
    """Parent folders that need a tree reload after a successful MOVE.

    A copy never changes the source tree. Dedupe paths case-insensitively so
    moving several files from the same folder updates it just once.
    """
    if not move:
        return ()
    seen = set()
    parents = []
    for item in plan:
        parent = str(Path(item.source).parent)
        identity = path_key(parent)
        if identity not in seen:
            seen.add(identity)
            parents.append(parent)
    return tuple(parents)
