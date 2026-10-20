"""Windows filesystem actions for FRB Launch's declarative context menus."""
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import subprocess

INVALID_WIN_CHARS = set('<>:"/\\|?*')
RESERVED_WIN_NAMES = {'CON', 'PRN', 'AUX', 'NUL',
                      *(f'COM{i}' for i in range(1, 10)),
                      *(f'LPT{i}' for i in range(1, 10))}


def _windows_only():
    if os.name != 'nt':
        raise RuntimeError('Windows専用の操作です')


def show_windows_properties(path):
    """Display Explorer's native property sheet, never FRB Studio.

    SHObjectProperties uses SHOP_FILEPATH for both files and directories.
    """
    _windows_only()
    shell32 = ctypes.WinDLL('shell32', use_last_error=True)
    fn = shell32.SHObjectProperties
    fn.argtypes = [wintypes.HWND, wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR]
    fn.restype = wintypes.BOOL
    SHOP_FILEPATH = 0x00000002
    if not fn(None, SHOP_FILEPATH, str(path), None):
        error = ctypes.get_last_error()
        raise OSError(error, 'Windowsのプロパティを表示できませんでした')


def open_file_explorer(path):
    _windows_only()
    subprocess.Popen(['explorer.exe', str(path)])


def open_parent_folder(path):
    """Open the containing directory of a filesystem file in Explorer."""
    open_file_explorer(Path(path).parent)


def open_folder_terminal(path):
    _windows_only()
    folder = str(path)
    try:
        subprocess.Popen(['wt.exe', '-d', folder], cwd=folder)
    except FileNotFoundError:
        subprocess.Popen(['powershell.exe', '-NoExit'], cwd=folder)


def rename_file_or_folder(path, new_name):
    """Rename in the same directory; never overwrite an existing file/folder."""
    path = Path(path)
    if (not isinstance(new_name, str) or not new_name
            or new_name in ('.', '..') or new_name != new_name.strip()
            or new_name.endswith('.') or any(c in INVALID_WIN_CHARS or ord(c) < 32
                                               for c in new_name)
            or new_name.split('.', 1)[0].upper() in RESERVED_WIN_NAMES):
        raise ValueError('Windowsで利用できないファイル名です')
    destination = path.with_name(new_name)
    # normcase is case-insensitive on Windows. A case-only rename remains valid.
    if os.path.normcase(str(path)) == os.path.normcase(str(destination)):
        if str(path) == str(destination):
            return path
    elif os.path.lexists(destination):
        raise FileExistsError('同じ名前のファイルまたはフォルダーが既に存在します: ' + str(destination))
    path.rename(destination)
    return destination
