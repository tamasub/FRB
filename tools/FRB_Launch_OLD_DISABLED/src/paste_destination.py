"""A single, predictable paste destination rule for Files navigation.

The breadcrumb is a fallback, not an override of an explicitly selected
folder.  Multiple selected folders (or a folder combined with other entries)
are ambiguous and must never initiate filesystem modifications.
"""
from pathlib import Path


class AmbiguousPasteTarget(ValueError):
    """The user's selected items do not identify one paste destination."""


def choose_paste_destination(displayed_directory, selected_paths=()):
    """Resolve one destination from the current Files selection.

    - No selection or file(s) only: currently displayed directory.
    - Exactly one selected folder: that folder.
    - Multiple folders / folder mixed with other selections: reject.
    """
    selected = tuple(Path(p) for p in (selected_paths or ()))
    directories = [path for path in selected if path.is_dir()]
    if len(directories) > 1:
        raise AmbiguousPasteTarget(
            '複数のフォルダーが選択されています。貼り付け先のフォルダーを1つだけ選択してください。')
    if directories and len(selected) != 1:
        raise AmbiguousPasteTarget(
            'フォルダーと他の項目が同時に選択されています。貼り付け先のフォルダーを1つだけ選択してください。')
    target = directories[0] if directories else Path(displayed_directory)
    if not target.is_dir():
        raise ValueError('貼り付け先のフォルダーが存在しません: ' + str(target))
    return target
