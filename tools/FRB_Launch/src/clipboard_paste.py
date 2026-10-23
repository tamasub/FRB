"""Explorer file/folder clipboard -> safe filesystem paste for a folder cascade.

This module has no Qt dependency.  The UI passes the QMimeData object and
refreshes the displayed folder only after the operation succeeds.
"""
from dataclasses import dataclass
from pathlib import Path
import os
import shutil


@dataclass(frozen=True)
class PasteItem:
    source: Path
    target: Path


def clipboard_sources(mime):
    """Only filesystem URLs (Windows Explorer copy/cut), never plain text."""
    if mime is None or not mime.hasUrls():
        return []
    result = []
    seen = set()
    for url in mime.urls():
        if not url.isLocalFile():
            continue
        path_text = url.toLocalFile()
        if not path_text:
            continue
        path = Path(path_text)
        identity = os.path.normcase(os.path.abspath(str(path)))
        if identity not in seen:
            result.append(path)
            seen.add(identity)
    return result


def is_cut_clipboard(mime):
    """Read Explorer's Preferred DropEffect: MOVE=2, COPY=1.

    A format-free URL clipboard is COPY, never an implicit destructive move.
    """
    if mime is None:
        return False
    for fmt in mime.formats():
        if 'preferreddropeffect' not in ''.join(c for c in fmt.casefold() if c.isalnum()):
            continue
        data = bytes(mime.data(fmt))
        if len(data) >= 4:
            effect = int.from_bytes(data[:4], byteorder='little')
            return bool(effect & 2)
    return False


def make_paste_plan(destination, sources):
    """Preflight ALL items, preventing overwrite, duplicates and self-copy.

    A batch with any conflict does no work.  Race-time collisions are still
    possible between preflight and copy; callers report OS errors faithfully.
    """
    destination = Path(destination)
    if not destination.is_dir():
        raise ValueError('貼り付け先のフォルダーが存在しません: ' + str(destination))
    result = []
    targets = set()
    resolved_destination = destination.resolve()
    for original in sources:
        source = Path(original)
        if not source.exists():
            raise ValueError('コピー元が見つかりません: ' + str(source))
        if not (source.is_file() or source.is_dir()):
            raise ValueError('通常のファイル・フォルダーだけ貼り付けできます: ' + str(source))
        target = destination / source.name
        target_key = os.path.normcase(os.path.abspath(str(target)))
        if target_key in targets:
            raise ValueError('同じ名前の貼り付け対象が重複しています: ' + source.name)
        targets.add(target_key)
        if target.exists() or target.is_symlink():
            raise FileExistsError('同名のファイル・フォルダーがあります（上書きしません）: ' + str(target))
        if source.resolve() == target.resolve():
            raise ValueError('同じ場所には貼り付けできません: ' + str(source))
        if source.is_dir() and (resolved_destination == source.resolve()
                                or source.resolve() in resolved_destination.parents):
            raise ValueError('フォルダーを自分自身の中には貼り付けできません: ' + str(source))
        result.append(PasteItem(source, target))
    if not result:
        raise ValueError('ファイル・フォルダーをExplorerでコピーしてから実行してください')
    return result


def paste_items(plan, *, move=False):
    """Copy or move Explorer selections.  No automatic overwrite or merge."""
    completed = 0
    for item in plan:
        # Second conflict check just before execution, to reduce races.
        if item.target.exists() or item.target.is_symlink():
            raise FileExistsError(f'{completed}件処理後に同名の対象を検出しました: {item.target}')
        try:
            if move:
                shutil.move(str(item.source), str(item.target))
            elif item.source.is_dir():
                shutil.copytree(item.source, item.target)
            else:
                # Exclusive creation avoids silent overwrite if another process
                # creates the file after our checks. Keep metadata if possible.
                with item.source.open('rb') as src, item.target.open('xb') as dst:
                    shutil.copyfileobj(src, dst)
                shutil.copystat(item.source, item.target)
        except Exception as exc:
            raise OSError(f'{completed}件処理後に失敗: {item.source.name}: {exc}') from exc
        completed += 1
    return completed
