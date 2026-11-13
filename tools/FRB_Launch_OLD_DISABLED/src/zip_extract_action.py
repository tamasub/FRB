"""ZIP-only Extract All support, without PowerShell or running archive contents.

Try Explorer's registered Extract All verb first.  Some Windows setups do not
expose that verb to ShellExecute; the caller can then show a native-looking
Qt destination chooser and use safe_extract_zip as a local fallback.
"""
import ctypes
import os
import re
import shutil
import stat
import zipfile
from ctypes import wintypes
from pathlib import Path, PurePosixPath

# Hard bound for the fallback implementation (native Explorer is not limited).
MAX_FALLBACK_UNCOMPRESSED = 8 * 1024**3
_WINDOWS_RESERVED = re.compile(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)', re.I)


def is_extractable_zip(path):
    """Only real .zip files are eligible; never folders or renamed archives."""
    target = Path(path)
    return target.suffix.casefold() == '.zip' and target.is_file()


def default_extract_destination(path):
    source = Path(path)
    return source.with_name(source.stem)


def invoke_windows_extract_all(path):
    """Ask Windows to open its own Extract All wizard; False if unavailable.

    No registry changes, PowerShell, decompression, or automatic overwrite.
    """
    if os.name != 'nt':
        return False
    target = Path(path)
    if not is_extractable_zip(target):
        raise ValueError('すべて展開はZIPファイルのみ対象です')
    executor = ctypes.WinDLL('shell32', use_last_error=True).ShellExecuteW
    executor.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR,
                         wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.c_int]
    executor.restype = ctypes.c_void_p
    status = executor(None, 'extractall', str(target.resolve()), None,
                      str(target.resolve().parent), 1)
    return bool(status and status > 32)


def _safe_relative(name):
    # ZIP convention is forward slashes.  Reject Windows backslashes instead
    # of allowing them to become accidental traversal separators on Windows.
    if not name or '\\' in name or name.startswith('/'):
        raise ValueError(f'ZIP内に安全でないパスがあります: {name!r}')
    parts = PurePosixPath(name).parts
    if not parts or any(part in ('.', '..') for part in parts):
        raise ValueError(f'ZIP内に安全でないパスがあります: {name!r}')
    for part in parts:
        if (not part or part.endswith(('.', ' ')) or
                any(ord(char) < 32 or char in '<>:"|?*' for char in part)
                or _WINDOWS_RESERVED.match(part)):
            raise ValueError(f'ZIP内にWindowsで扱えない名前があります: {name!r}')
    return parts


def safe_extract_zip(zip_path, destination):
    """Extract into a NEW/empty destination, preventing traversal/overwrite.

    No chmod, no symlinks, no file execution; refuse ambiguous/colliding names.
    """
    source, root = Path(zip_path), Path(destination)
    if not is_extractable_zip(source):
        raise ValueError('すべて展開はZIPファイルのみ対象です')
    if root.exists() and (not root.is_dir() or any(root.iterdir())):
        raise FileExistsError(f'展開先に既存ファイルがあります。別のフォルダーを指定してください: {root}')
    try:
        return _extract_validated(source, root)
    except (zipfile.BadZipFile, zipfile.LargeZipFile, NotImplementedError) as exc:
        raise ValueError(f'ZIPを展開できませんでした: {exc}') from exc


def _extract_validated(source, root):
    files = []
    seen = set()
    entry_types = {}
    total_bytes = 0
    with zipfile.ZipFile(source, 'r') as archive:
        for item in archive.infolist():
            parts = _safe_relative(item.filename)
            key = '/'.join(parts).casefold()
            if key in seen:
                raise ValueError(f'ZIP内に重複するパスがあります: {item.filename}')
            seen.add(key)
            # A ZIP must not define both an ordinary file and children under it.
            for index in range(1, len(parts)):
                parent_key = '/'.join(parts[:index]).casefold()
                if entry_types.get(parent_key) == 'file':
                    raise ValueError(f'ZIP内の親パスがファイルです: {item.filename}')
            is_directory = item.is_dir()
            if not is_directory and any(existing.startswith(key + '/') for existing in seen):
                raise ValueError(f'ZIP内のファイルとフォルダーが衝突しています: {item.filename}')
            entry_types[key] = 'directory' if is_directory else 'file'
            file_type = (item.external_attr >> 16) & 0o170000
            if file_type not in (0, stat.S_IFREG, stat.S_IFDIR):
                raise ValueError(f'ZIP内のリンクや特殊ファイルは展開しません: {item.filename}')
            if item.flag_bits & 1:
                raise ValueError('暗号化ZIPにはWindows標準の展開機能をご利用ください')
            total_bytes += item.file_size
            if total_bytes > MAX_FALLBACK_UNCOMPRESSED:
                raise ValueError('容量が大きいため、Windows標準の展開機能をご利用ください')
            files.append((item, parts))
        root.mkdir(parents=True, exist_ok=True)
        resolved_root = root.resolve()
        for item, parts in files:
            output = root.joinpath(*parts)
            if not output.resolve().is_relative_to(resolved_root):
                raise ValueError(f'展開先の外へ書き込めません: {item.filename}')
            if item.is_dir():
                output.mkdir(parents=True, exist_ok=True)
            else:
                output.parent.mkdir(parents=True, exist_ok=True)
                if output.exists():
                    raise FileExistsError(f'ファイルが重複しています: {output}')
                with archive.open(item) as source_stream, output.open('xb') as target_stream:
                    shutil.copyfileobj(source_stream, target_stream)
    return root
