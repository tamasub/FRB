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


def make_paste_plan(destination, sources, *, allow_existing=False):
    """Preflight ALL items, preventing unintended overwrite and self-copy.

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
        if source.is_symlink() or not (source.is_file() or source.is_dir()):
            raise ValueError('通常のファイル・フォルダーだけ貼り付けできます: ' + str(source))
        target = destination / source.name
        target_key = os.path.normcase(os.path.abspath(str(target)))
        if target_key in targets:
            raise ValueError('同じ名前の貼り付け対象が重複しています: ' + source.name)
        targets.add(target_key)
        if target.is_symlink():
            raise ValueError('リンク先の上書きはできません: ' + str(target))
        if target.exists():
            if not allow_existing:
                raise FileExistsError('同名のファイル・フォルダーがあります（上書きしません）: ' + str(target))
            if source.is_dir() != target.is_dir():
                raise ValueError('同名のファイルとフォルダーは種類が異なるため上書きできません: ' + str(target))
        if source.resolve() == target.resolve():
            raise ValueError('同じ場所には貼り付けできません: ' + str(source))
        if source.is_dir() and (resolved_destination == source.resolve()
                                or source.resolve() in resolved_destination.parents):
            raise ValueError('フォルダーを自分自身の中には貼り付けできません: ' + str(source))
        result.append(PasteItem(source, target))
    if not result:
        raise ValueError('ファイル・フォルダーをExplorerでコピーしてから実行してください')
    return result


def paste_conflicts(plan):
    """Top-level existing destinations requiring explicit user approval."""
    return [item.target for item in plan
            if item.target.exists() or item.target.is_symlink()]


def _copy_directory_merged(source, target):
    """Merge an existing folder without deleting its unrelated contents."""
    if source.is_symlink() or target.is_symlink():
        raise ValueError('リンクを含むフォルダーの上書きには対応していません')
    if not target.exists():
        shutil.copytree(source, target, symlinks=False)
        return
    if not target.is_dir():
        raise ValueError('同名のファイルとフォルダーの種類が異なります: ' + str(target))
    for child in source.iterdir():
        if child.is_symlink():
            raise ValueError('リンクを含むフォルダーの上書きには対応していません')
        dest_child = target / child.name
        if dest_child.is_symlink():
            raise ValueError('リンク先の上書きには対応していません')
        if child.is_dir():
            _copy_directory_merged(child, dest_child)
        else:
            if dest_child.is_dir():
                raise ValueError('同名のファイルとフォルダーの種類が異なります: ' + str(dest_child))
            shutil.copy2(child, dest_child)


def paste_items(plan, *, move=False, overwrite=False):
    """Copy/move selected items. Overwrite requires separately confirmed opt-in.

    Existing directories are *merged* (unrelated destination children remain).
    A failed batch can be partially applied; never claim transactionality.
    """
    completed = 0
    for item in plan:
        conflict = item.target.exists() or item.target.is_symlink()
        if conflict and not overwrite:
            raise FileExistsError(f'{completed}件処理後に同名の対象を検出しました: {item.target}')
        if item.source.is_symlink() or item.target.is_symlink():
            raise ValueError('リンクのコピー・上書きは対象外です')
        try:
            if conflict and item.source.is_dir() != item.target.is_dir():
                raise ValueError('上書き元と先の種類が異なります')
            if item.source.is_dir():
                if not conflict:
                    if move:
                        shutil.move(str(item.source), str(item.target))
                    else:
                        shutil.copytree(item.source, item.target)
                else:
                    _copy_directory_merged(item.source, item.target)
                    if move:
                        shutil.rmtree(item.source)  # Only after merge copy succeeds.
            elif move:
                if conflict:
                    os.replace(item.source, item.target)
                else:
                    shutil.move(str(item.source), str(item.target))
            elif conflict:
                shutil.copy2(item.source, item.target)
            else:
                with item.source.open('rb') as src, item.target.open('xb') as dst:
                    shutil.copyfileobj(src, dst)
                shutil.copystat(item.source, item.target)
        except Exception as exc:
            raise OSError(f'{completed}件処理後に失敗: {item.source.name}: {exc}') from exc
        completed += 1
    return completed
