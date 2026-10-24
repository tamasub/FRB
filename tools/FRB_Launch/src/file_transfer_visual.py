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
