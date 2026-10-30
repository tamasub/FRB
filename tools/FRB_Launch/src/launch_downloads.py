"""Pure download path and safe ZIP-extraction helpers for FRB Launch.

No Qt dependency, no shell invocation. ZIP content is inert and never executed.
"""
from pathlib import Path, PurePosixPath
import os
import re
import shutil
import stat
import tempfile
import zipfile

_WINDOWS_RESERVED = {'CON', 'PRN', 'AUX', 'NUL',
                     *(f'COM{i}' for i in range(1, 10)),
                     *(f'LPT{i}' for i in range(1, 10))}


def safe_download_name(value):
    """Convert untrusted HTTP-suggested names to a single safe Windows filename."""
    name = str(value or '').replace('\\', '/').split('/')[-1].strip()
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name).rstrip(' .')
    if not name or name in ('.', '..'):
        name = 'download'
    if name.split('.')[0].upper() in _WINDOWS_RESERVED:
        name = '_' + name
    # Avoid invalid or overlong Windows filename; preserve the extension.
    stem, suffix = os.path.splitext(name)
    if len(name) > 180:
        name = stem[:max(1, 180-len(suffix))] + suffix[:20]
    return name


def unique_path(folder, name, reserved=(), *, is_dir=False):
    """Suggest a non-existing target with Chrome-like (1), (2) suffixes."""
    directory = Path(folder)
    filename = safe_download_name(name)
    base = directory / filename
    stem, suffix = (filename, '') if is_dir else os.path.splitext(filename)
    reserved_set = {os.path.normcase(os.path.abspath(str(path))) for path in reserved}
    n = 0
    while base.exists() or os.path.normcase(os.path.abspath(str(base))) in reserved_set:
        n += 1
        if n > 9999:
            raise OSError('保存先の重複が多すぎます')
        base = directory / f'{stem} ({n}){suffix}'
    return base


def safe_extract_zip(source, *, max_entries=3000, max_bytes=2 * 1024**3):
    """Extract an explicitly selected ZIP into a new adjacent directory.

    Reject path traversal, symlinks, special files and oversized archives.
    Extract via temporary directory then atomically rename to final target.
    Do not use shutil.unpack_archive because archive paths are untrusted.
    """
    source = Path(source)
    if source.suffix.lower() != '.zip' or not source.is_file():
        raise ValueError('ZIPファイルが見つかりません')
    final = unique_path(source.parent, source.stem, is_dir=True)
    written = 0
    with zipfile.ZipFile(source) as archive:
        entries = archive.infolist()
        if len(entries) > max_entries:
            raise ValueError('ZIP内の項目数が上限を超えています')
        total = 0
        checked = []
        for item in entries:
            raw = item.filename
            # Reject ambiguous Windows path syntax even when running on Unix.
            if not raw or '\\' in raw or '\x00' in raw or ':' in raw or raw.startswith('/'):
                raise ValueError('ZIPに安全でないパスが含まれています')
            rel = PurePosixPath(raw)
            if rel.is_absolute() or '..' in rel.parts or len(raw) > 240:
                raise ValueError('ZIPに安全でないパスが含まれています')
            for segment in rel.parts:
                if segment.rstrip(' .') != segment or segment.split('.')[0].upper() in _WINDOWS_RESERVED:
                    raise ValueError('ZIPにWindowsで扱えないファイル名が含まれています')
            mode = (item.external_attr >> 16) & 0xFFFF
            kind = stat.S_IFMT(mode)
            if kind not in (0, stat.S_IFDIR, stat.S_IFREG):
                raise ValueError('ZIP内のシンボリックリンク等には対応していません')
            total += item.file_size
            if total > max_bytes:
                raise ValueError('ZIP展開サイズが安全上限を超えています')
            checked.append((item, rel))
        # Staging guards against partially visible extraction after failure.
        with tempfile.TemporaryDirectory(prefix='.frb_zip_', dir=str(source.parent)) as temp:
            temp_root = Path(temp)
            for item, rel in checked:
                destination = temp_root.joinpath(*rel.parts)
                if item.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(item, 'r') as reader, destination.open('xb') as writer:
                    while True:
                        data = reader.read(1024 * 1024)
                        if not data:
                            break
                        written += len(data)
                        if written > max_bytes:
                            raise ValueError('ZIP展開サイズが安全上限を超えています')
                        writer.write(data)
            # Prevent races with a folder created while extraction was running.
            final = unique_path(source.parent, source.stem, is_dir=True)
            os.rename(temp_root, final)
    return str(final)
