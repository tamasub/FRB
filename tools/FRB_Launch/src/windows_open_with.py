"""Small, best-effort Windows Open With submenu source.

Explorer's modern Open With UI is not a public QMenu API.  Use registered
file-extension handlers where a directly launchable .exe is available; leave
MSIX/UWP/special COM handlers to the real Windows chooser (always last).

This module never evaluates registry command lines or changes associations.
"""
from dataclasses import dataclass
from pathlib import Path
import os
import re
import shutil
import subprocess


@dataclass(frozen=True)
class OpenWithApp:
    title: str
    executable: str


_COMMON_NAMES = {
    'code.exe': 'Visual Studio Code',
    'cursor.exe': 'Cursor',
    'devenv.exe': 'Microsoft Visual Studio',
    'notepad.exe': 'メモ帳',
    'notepad++.exe': 'Notepad++',
    'sublime_text.exe': 'Sublime Text',
    'wordpad.exe': 'WordPad',
}
_TEXT_SUFFIXES = frozenset({'.json', '.jsonc', '.md', '.txt', '.xml', '.yaml', '.yml',
                           '.ini', '.cfg', '.py', '.js', '.ts', '.html', '.css', '.log',
                           '.csv', '.bat', '.cmd', '.ps1'})
_EDITORS = ('Cursor.exe', 'Code.exe', 'devenv.exe', 'notepad++.exe', 'notepad.exe')
# Shell hosts/interpreters aren't ordinary direct file-open applications.
_NOT_DIRECT_APPS = frozenset({'rundll32.exe', 'dllhost.exe', 'explorer.exe',
    'cmd.exe', 'powershell.exe', 'pwsh.exe', 'wscript.exe', 'cscript.exe',
    'mshta.exe', 'openwith.exe', 'applicationframehost.exe'})


def _values(reg, root, subkey):
    try:
        with reg.OpenKey(root, subkey) as key:
            result = {}
            index = 0
            while True:
                try:
                    name, value, _kind = reg.EnumValue(key, index)
                except OSError:
                    return result
                result[name] = value
                index += 1
    except OSError:
        return {}


def _subkeys(reg, root, subkey):
    try:
        with reg.OpenKey(root, subkey) as key:
            result = []
            index = 0
            while True:
                try:
                    result.append(reg.EnumKey(key, index))
                except OSError:
                    return result
                index += 1
    except OSError:
        return []


def _default(reg, root, key):
    try:
        with reg.OpenKey(root, key) as opened:
            return reg.QueryValueEx(opened, '')[0]
    except OSError:
        return None


def _associated_strings(progid, kind):
    """Optional Shell association query; includes executable and display name."""
    if os.name != 'nt':
        return None
    import ctypes
    from ctypes import wintypes
    try:
        func = ctypes.WinDLL('shlwapi').AssocQueryStringW
        func.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.LPCWSTR,
                         wintypes.LPCWSTR, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
        func.restype = ctypes.c_long
        size = wintypes.DWORD(512)
        buffer = ctypes.create_unicode_buffer(size.value)
        result = func(0, kind, progid, 'open', buffer, ctypes.byref(size))
        return buffer.value if result == 0 and buffer.value else None
    except (AttributeError, OSError, ValueError):
        return None


def _exe_from_command(command):
    """Read ONLY the executable portion; never evaluate command arguments."""
    if not isinstance(command, str):
        return None
    expanded = os.path.expandvars(command).strip()
    if expanded.startswith('"'):
        match = re.match(r'^"([^"]+\.exe)"(?:\s|$)', expanded, re.I)
        return match.group(1) if match else None
    match = re.match(r'^(.+?\.exe)(?:\s|$)', expanded, re.I)
    return match.group(1).strip() if match else None


def _resolve_executable(reg, filename):
    """Use App Paths and registered shell commands; no speculative filesystem scan."""
    filename = str(filename or '').strip()
    if not filename or not filename.casefold().endswith('.exe'):
        return None
    value = os.path.expandvars(filename.strip('"'))
    file_path = Path(value)
    if file_path.is_file():
        return str(file_path)
    exe_name = file_path.name
    if exe_name.casefold() in _NOT_DIRECT_APPS:
        return None
    if '\\' in filename or '/' in filename:
        return None  # An absolute missing path must not fall back to another app.
    for root in (reg.HKEY_CURRENT_USER, reg.HKEY_LOCAL_MACHINE):
        path = _default(reg, root, fr'Software\Microsoft\Windows\CurrentVersion\App Paths\{exe_name}')
        if path:
            actual = Path(os.path.expandvars(str(path).strip('"')))
            if actual.is_file() and actual.suffix.casefold() == '.exe':
                return str(actual)
    cmd = _default(reg, reg.HKEY_CLASSES_ROOT,
                   fr'Applications\{exe_name}\shell\open\command')
    executable = _exe_from_command(cmd)
    if executable and Path(executable).is_file():
        return executable
    found = shutil.which(exe_name)
    if found and Path(found).is_file():
        return found
    return None


def discover_open_with_apps(path, max_results=12):
    """Enumerate real launchable registered apps for one file extension.

    Returns [] on non-Windows, inaccessible registry or an unregistered type;
    the menu must always expose the Windows 'choose another app' fallback.
    """
    if os.name != 'nt':
        return []
    try:
        import winreg as reg
    except ImportError:
        return []
    suffix = Path(path).suffix.casefold()
    if not suffix:
        return []
    user_base = fr'Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\{suffix}'
    system_bases = (suffix, fr'SystemFileAssociations\{suffix}')
    apps = []
    progids = []
    def add_app(exe, friendly=None):
        resolved = _resolve_executable(reg, exe)
        if not resolved:
            return
        if any(Path(a.executable).as_posix().casefold() == Path(resolved).as_posix().casefold()
               for a in apps):
            return
        base_name = Path(resolved).name.casefold()
        title = str(friendly or '').strip()
        if not title:
            title = _values(reg, reg.HKEY_CLASSES_ROOT,
                            fr'Applications\{Path(resolved).name}').get('FriendlyAppName') or ''
        title = title or _COMMON_NAMES.get(base_name, Path(resolved).stem)
        apps.append(OpenWithApp(str(title), str(resolved)))

    # Per-user MRU executable handlers, the most relevant evidence for Open With.
    values = _values(reg, reg.HKEY_CURRENT_USER, user_base + r'\OpenWithList')
    order = str(values.get('MRUList') or '')
    keys = [key for key in order if key in values]
    keys.extend(key for key in values if key not in keys and key not in ('MRUList', 'MRUListEx'))
    for key in keys:
        if isinstance(values.get(key), str):
            add_app(values[key])
    for base in system_bases:
        for entry in _subkeys(reg, reg.HKEY_CLASSES_ROOT, base + r'\OpenWithList'):
            add_app(entry)
        for value in _values(reg, reg.HKEY_CLASSES_ROOT, base + r'\OpenWithList').values():
            if isinstance(value, str) and value.casefold().endswith('.exe'):
                add_app(value)

    # ProgID-based associations (e.g. Visual Studio or VS Code registrations).
    for root, key in ((reg.HKEY_CURRENT_USER, user_base + r'\OpenWithProgids'),
                      *((reg.HKEY_CLASSES_ROOT, b + r'\OpenWithProgids') for b in system_bases)):
        progids.extend(k for k in _values(reg, root, key) if k)
    default_progid = _default(reg, reg.HKEY_CLASSES_ROOT, suffix)
    if default_progid:
        progids.append(str(default_progid))
    for progid in dict.fromkeys(progids):
        exe = _associated_strings(progid, 2)  # ASSOCSTR_EXECUTABLE
        if not exe:
            command = _default(reg, reg.HKEY_CLASSES_ROOT, progid + r'\shell\open\command')
            exe = _exe_from_command(command)
        if exe:
            add_app(exe, _associated_strings(progid, 4))  # ASSOCSTR_FRIENDLYAPPNAME

    # A tiny editor fallback for text-like files. Only show actually installed EXEs.
    if suffix in _TEXT_SUFFIXES:
        for exe in _EDITORS:
            add_app(exe)
    return apps[:max(0, max_results)]


def open_file_with_app(path, executable):
    """Open a file with an explicit executable, without changing default apps."""
    if os.name != 'nt':
        raise RuntimeError('Windows専用の操作です')
    file_path = Path(path)
    exe_path = Path(executable)
    if not file_path.is_file():
        raise FileNotFoundError('対象ファイルがありません: ' + str(file_path))
    if not exe_path.is_file() or exe_path.suffix.casefold() != '.exe':
        raise FileNotFoundError('アプリが見つかりません: ' + str(exe_path))
    subprocess.Popen([str(exe_path), str(file_path.resolve())], close_fds=True)
