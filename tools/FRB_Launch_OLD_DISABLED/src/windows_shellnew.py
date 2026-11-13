"""Safe Windows Explorer-style 'New' discovery and basic file creation.

Registry enumeration is informational: third-party ShellNew templates/commands
need their own native handlers.  Never imitate Word/Excel documents with empty
files just because their extension was registered.
"""

from __future__ import annotations

import os
from pathlib import Path
import re


_RESERVED = re.compile(r'^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?$', re.I)
_ILLEGAL = set('<>:"/\\|?*')


def validate_name(name: str) -> str:
    """Reject names Windows cannot create, including ambiguous trailing dots."""
    name = str(name or '')
    if not name or name in ('.', '..') or name != name.strip() or name.endswith('.'):
        raise ValueError('ファイル名またはフォルダー名が不正です')
    if any(ch in _ILLEGAL or ord(ch) < 32 for ch in name) or _RESERVED.match(name):
        raise ValueError('Windowsで使用できない名前が含まれています')
    return name


def suggest_name(directory, base: str, extension: str = '') -> str:
    """Explorer-like unused default; compare case-insensitively on all hosts."""
    directory = Path(directory)
    seen = {entry.name.casefold() for entry in directory.iterdir()}
    for i in range(1, 10001):
        text = base if i == 1 else f'{base} ({i})'
        candidate = text + extension
        if candidate.casefold() not in seen:
            return candidate
    raise FileExistsError('新しい名前を決定できませんでした')


def create_new_item(directory, name, kind):
    """Create a folder/text/markdown item atomically; never overwrite existing."""
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError('作成先フォルダーが存在しません')
    name = validate_name(name)
    if kind not in ('folder', 'txt', 'md'):
        raise ValueError('このファイル種類の作成には対応していません')
    extension = {'folder': '', 'txt': '.txt', 'md': '.md'}[kind]
    if extension and not name.lower().endswith(extension):
        name += extension
        validate_name(name)
    if any(entry.name.casefold() == name.casefold() for entry in directory.iterdir()):
        raise FileExistsError(f'同じ名前がすでに存在します: {name}')
    dest = directory / name
    if kind == 'folder':
        dest.mkdir()  # must fail if created between validation and mkdir
    else:
        with dest.open('xb'):
            pass
    return dest


def discover_shellnew(winreg_module=None):
    """Read ShellNew candidates from HKCR without invoking third-party code.

    Returns (extension, display_name, creation_kind) for UI only.  The list may
    vary between machines and may include registrations Explorer hides.
    """
    if winreg_module is None:
        try:
            import winreg as winreg_module
        except ImportError:
            return []
    registry = winreg_module
    root = registry.HKEY_CLASSES_ROOT
    records = []
    index = 0
    while True:
        try:
            extension = registry.EnumKey(root, index)
        except OSError:
            break
        index += 1
        if not extension.startswith('.') or len(extension) <= 1:
            continue
        try:
            # Explorer accepts both .ext\ShellNew and .ext\ProgID\ShellNew.
            # Office registers .docx\Word.Document.12\ShellNew, for example.
            locations = [extension + r'\ShellNew']
            try:
                with registry.OpenKey(root, extension) as ext_key:
                    progid = registry.QueryValueEx(ext_key, '')[0]
                    if isinstance(progid, str) and progid:
                        locations.append(extension + '\\' + progid + r'\ShellNew')
                    # Some apps register an alternate ProgID under the .ext key.
                    sub_index = 0
                    while sub_index < 64:
                        try:
                            subkey = registry.EnumKey(ext_key, sub_index)
                        except OSError:
                            break
                        sub_index += 1
                        if subkey != 'ShellNew':
                            locations.append(extension + '\\' + subkey + r'\ShellNew')
            except OSError:
                pass
            types = set()
            for location in dict.fromkeys(locations):
                try:
                    with registry.OpenKey(root, location) as shell:
                        for key in ('NullFile', 'FileName', 'Data', 'Command'):
                            try:
                                registry.QueryValueEx(shell, key)
                                types.add(key)
                            except OSError:
                                pass
                except OSError:
                    continue
                if types:
                    break
            if not types:
                continue
            label = extension + ' ファイル'
            try:
                with registry.OpenKey(root, extension) as extkey:
                    progid = registry.QueryValueEx(extkey, '')[0]
                if isinstance(progid, str) and progid:
                    with registry.OpenKey(root, progid) as progkey:
                        human = registry.QueryValueEx(progkey, '')[0]
                        if isinstance(human, str) and human.strip():
                            label = human.strip()
            except OSError:
                pass
            records.append((extension.lower(), label, '/'.join(sorted(types))))
        except OSError:
            continue
    return sorted(set(records), key=lambda item: (item[1].casefold(), item[0]))
