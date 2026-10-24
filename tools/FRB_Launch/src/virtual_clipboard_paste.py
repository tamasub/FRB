"""Paste virtual Shell file objects (including ZIP members) into a real folder.

Windows Explorer can copy items from a ZIP namespace without placing real file
paths on the clipboard.  Unlike ordinary Explorer copies these IDataObjects
may carry FileGroupDescriptor/FileContents or Shell IDList instead of CF_HDROP.

Do not extract ZIP paths manually.  Let Windows Shell perform the extraction via
IFileOperation::CopyItems(IDataObject, IShellItem) on the GUI's STA thread.
"""

import ctypes
import os
from pathlib import Path
import struct
import sys
import uuid


def is_virtual_file_clipboard(mime):
    """Recognize Shell virtual-file clipboard metadata without reading contents."""
    if mime is None:
        return False
    formats = ["".join(c for c in name.lower() if c.isalnum())
               for name in mime.formats()]
    return any("filegroupdescriptor" in fmt or "shellidlistarray" in fmt
               for fmt in formats)


def virtual_clipboard_names(mime):
    """Read names from FILEGROUPDESCRIPTORW/ANSI for collision preflight.

    Returns None when the Shell clipboard exposes only PIDLs or when its
    descriptors are unavailable. Never requests FileContents (potentially huge).
    """
    if mime is None:
        return None
    for fmt in mime.formats():
        marker = "".join(c for c in fmt.lower() if c.isalnum())
        if "filegroupdescriptor" not in marker:
            continue
        wide = "filegroupdescriptorw" in marker
        raw = bytes(mime.data(fmt))
        if len(raw) < 4:
            raise ValueError('ZIP内のコピー情報が不正です（FileGroupDescriptor）')
        count = struct.unpack_from('<I', raw)[0]
        if count < 1 or count > 10000:
            raise ValueError('ZIP内のコピー対象件数が不正です')
        # FILEDESCRIPTORW = 592 bytes, FILEDESCRIPTORA = 332 bytes.
        size = 592 if wide else 332
        width = 520 if wide else 260
        if len(raw) < 4 + size * count:
            raise ValueError('ZIP内のコピー情報が途中で切れています')
        names = []
        for i in range(count):
            blob = raw[4 + i * size + 72:4 + i * size + 72 + width]
            if wide:
                name = blob.decode('utf-16-le', errors='replace').split('\0', 1)[0]
            else:
                name = blob.split(b'\0', 1)[0].decode('mbcs' if sys.platform == 'win32' else 'cp1252', errors='replace')
            # Windows virtual files may give relative subpaths; only top level
            # entries are relevant for collision checks at the destination.
            parts = name.replace('/', '\\').split('\\')
            if not parts or not parts[0] or parts[0] in ('.', '..') or ':' in parts[0]:
                raise ValueError('ZIP内に不正なファイル名があります')
            names.append(parts[0])
        return sorted(set(names), key=str.casefold)
    return None


def preflight_virtual_destination(destination, names, *, allow_existing=False):
    """Reject existing targets rather than overwrite when names are provided."""
    destination = Path(destination)
    if not destination.is_dir():
        raise ValueError('貼り付け先のフォルダーが存在しません: ' + str(destination))
    if names:
        existing = {entry.name.casefold() for entry in destination.iterdir()}
        for name in names:
            if name.casefold() in existing and not allow_existing:
                raise FileExistsError('同名のファイル・フォルダーがあります（上書きしません）: ' + name)


class _GUID(ctypes.Structure):
    _fields_ = [('Data1', ctypes.c_uint32), ('Data2', ctypes.c_uint16),
                ('Data3', ctypes.c_uint16), ('Data4', ctypes.c_ubyte * 8)]

    @classmethod
    def parse(cls, value):
        return cls.from_buffer_copy(uuid.UUID(value).bytes_le)


def _check_hr(hr, action):
    if hr < 0:
        raise OSError(f'{action} 失敗 (HRESULT 0x{hr & 0xffffffff:08X})')


def _com_call(pointer, index, argtypes=(), args=()):
    """Invoke an IUnknown-derived COM vtable method (Windows stdcall)."""
    table = ctypes.cast(pointer, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    call = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, *argtypes)(table[index])
    return call(pointer, *args)


def _release(pointer):
    if pointer and pointer.value:
        _com_call(pointer, 2)


def paste_virtual_shell_items(destination, *, overwrite_confirmed=False):
    """Copy ZIP/virtual clipboard items using Windows IFileOperation.

    The caller may suppress Shell's duplicate overwrite confirmation ONLY after
    discovering the target conflicts and receiving explicit approval in Launch.
    All other Shell UI remains enabled (including errors/UAC where applicable).
    Only COPY is requested; the source ZIP is never edited or moved.
    """
    if sys.platform != 'win32':
        raise OSError('ZIP内の仮想ファイル貼り付けはWindows専用です')
    destination = Path(destination)
    if not destination.is_dir():
        raise ValueError('貼り付け先フォルダーが見つかりません: ' + str(destination))

    ole32 = ctypes.OleDLL('ole32')
    shell32 = ctypes.OleDLL('shell32')
    ole32.OleInitialize.argtypes = [ctypes.c_void_p]
    ole32.OleInitialize.restype = ctypes.c_long
    ole32.OleGetClipboard.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
    ole32.OleGetClipboard.restype = ctypes.c_long
    ole32.CoCreateInstance.argtypes = [ctypes.POINTER(_GUID), ctypes.c_void_p,
                                      ctypes.c_uint32, ctypes.POINTER(_GUID),
                                      ctypes.POINTER(ctypes.c_void_p)]
    ole32.CoCreateInstance.restype = ctypes.c_long
    shell32.SHCreateItemFromParsingName.argtypes = [ctypes.c_wchar_p, ctypes.c_void_p,
                                                   ctypes.POINTER(_GUID), ctypes.POINTER(ctypes.c_void_p)]
    shell32.SHCreateItemFromParsingName.restype = ctypes.c_long

    started = False
    source, target, operation = ctypes.c_void_p(), ctypes.c_void_p(), ctypes.c_void_p()
    try:
        _check_hr(ole32.OleInitialize(None), 'OLE初期化')
        started = True
        _check_hr(ole32.OleGetClipboard(ctypes.byref(source)), 'クリップボード取得')
        _check_hr(shell32.SHCreateItemFromParsingName(str(destination), None,
                  ctypes.byref(_GUID.parse('43826d1e-e718-42ee-bc55-a1e261c37bfe')),
                  ctypes.byref(target)), '貼り付け先取得')
        _check_hr(ole32.CoCreateInstance(
                  ctypes.byref(_GUID.parse('3ad05575-8857-4850-9277-11b85bdb8e09')),
                  None, 1, ctypes.byref(_GUID.parse('947aab5f-0a5c-4c13-b4d6-4bf7836fc9f8')),
                  ctypes.byref(operation)), 'Windowsファイル操作の作成')
        if overwrite_confirmed:
            # IFileOperation::SetOperationFlags (vtable index 5).
            # Preserve the documented defaults and add FOF_NOCONFIRMATION
            # ONLY after Launch has confirmed known same-name conflicts:
            # FOF_ALLOWUNDO | FOF_NOCONFIRMMKDIR | FOF_NOCONFIRMATION.
            flags = 0x0040 | 0x0200 | 0x0010
            _check_hr(_com_call(operation, 5, (ctypes.c_uint32,), (flags,)),
                      '確認済み上書き設定')
        # IFileOperation::CopyItems at vtable index 17, PerformOperations 21.
        _check_hr(_com_call(operation, 17, (ctypes.c_void_p, ctypes.c_void_p),
                            (source, target)), 'ZIP内ファイルのコピー準備')
        _check_hr(_com_call(operation, 21), 'ZIP内ファイルの貼り付け')
        aborted = ctypes.c_int(0)
        _check_hr(_com_call(operation, 22, (ctypes.POINTER(ctypes.c_int),),
                            (ctypes.byref(aborted),)), '貼り付け結果確認')
        if aborted.value:
            raise OSError('貼り付けが中止されたか、一部の項目を処理できませんでした')
    finally:
        _release(operation)
        _release(target)
        _release(source)
        if started:
            ole32.OleUninitialize()
