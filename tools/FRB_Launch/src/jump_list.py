"""FRB Launch Windows taskbar Jump List (work Page-root items only).

Only Windows Shell COM is used; no third-party COM dependencies.  This module
never runs a launch action: a Jump List link relays an item id to the existing
single-instance FRB Launch process, which calls ``summon_menu``.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import threading
import uuid
from pathlib import Path

APP_ID = 'FRB.Launch'
IPC_SWITCH = '--jump-item='
MAX_ITEMS = 24  # A conservative upper bound; BeginList can return fewer slots.
JUMP_LIST_PAGE_ID = 'work'  # Other Pages stay in Launch, not the taskbar Jump List.


def page_root_entries(data):
    """Return only the enabled 仕事 Page's authored first-level items.

    The user's taskbar is a short entry point, not a mirror of all Pages.
    Preserve menu order; ignore disabled/nested/runtime-generated entries.
    This module does not depend on PySide6 or Windows to calculate entries.
    """
    pages = sorted((p for p in data.get('pages', []) if p.get('enabled', True)),
                   key=lambda p: (p.get('sort_order', 0), p.get('page_id', '')))
    rows = data.get('items', [])
    result = []
    for page in pages:
        if page.get('page_id') != JUMP_LIST_PAGE_ID:
            continue
        items = sorted((r for r in rows
                        if r.get('page_id') == page.get('page_id')
                        and not r.get('parent_item_id')
                        and r.get('enabled', True)
                        and r.get('item_id')),
                       key=lambda r: (r.get('sort_order', 0), r.get('title', '')))
        if items:
            result.append((str(page.get('title') or page.get('page_id')), [
                (str(r['item_id']), str(r.get('title') or r['item_id']))
                for r in items]))
    return result


def _valid_item_id(item_id):
    return (isinstance(item_id, str) and 0 < len(item_id) <= 250
            and not any(ord(ch) < 32 for ch in item_id))


def ipc_command(item_id):
    """Printable ASCII JSON transports Japanese and any other item_id safely."""
    if not _valid_item_id(item_id):
        raise ValueError('不正なメニュー項目IDです')
    return json.dumps({'action': 'show-menu', 'item_id': item_id}, ensure_ascii=True,
                      separators=(',', ':')).encode('ascii') + b'\n'


def parse_ipc_command(payload):
    """Parse one complete request; fail closed on invalid/unknown messages."""
    if payload == b'show' or payload == b'show\n':
        return 'show', None
    if len(payload) > 2048 or not payload.endswith(b'\n'):
        raise ValueError('IPC命令の形式が不正です')
    command = json.loads(payload.decode('utf-8'))
    if not isinstance(command, dict) or command.get('action') != 'show-menu':
        raise ValueError('未知のIPC命令です')
    item_id = command.get('item_id')
    if not _valid_item_id(item_id):
        raise ValueError('不正な項目IDです')
    return 'show-menu', item_id


def argument_for_item(item_id):
    """One CLI argument (no shell interpolation) from a URL-safe item id."""
    from urllib.parse import quote
    if not _valid_item_id(item_id):
        raise ValueError('不正な項目IDです')
    return IPC_SWITCH + quote(item_id, safe='')


def requested_item(argv):
    from urllib.parse import unquote
    for argument in argv:
        if argument.startswith(IPC_SWITCH):
            encoded = argument[len(IPC_SWITCH):]
            # Reject odd percent-escapes and empty values.
            import re
            if re.search(r'%(?![0-9A-Fa-f]{2})', encoded):
                return None
            item_id = unquote(encoded)
            return item_id if _valid_item_id(item_id) else None
    return None


def limited_page_entries(data, maximum):
    """Show as many 仕事 first-level items as Windows permits, in menu order.

    Windows may return fewer slots than requested.  We cannot override the
    operating system's limit and must not silently add unrelated Pages.
    """
    groups = page_root_entries(data)
    remaining = max(0, int(maximum))
    if not groups or not remaining:
        return []
    page, items = groups[0]
    return [(page, items[:remaining])]


def list_fingerprint(data, exe):
    entries = page_root_entries(data)
    digest = hashlib.sha256(json.dumps(entries, ensure_ascii=False).encode('utf-8')).hexdigest()
    try:
        built = Path(exe).stat().st_mtime_ns
    except OSError:
        built = 0
    return f'v2|{APP_ID}|{str(exe).casefold()}|{built}|{digest}'


# The implementation below mirrors Studio's native JumpListManager COM contract.
# Import-safe on non-Windows systems for unit tests.
if os.name == 'nt':
    import ctypes as C
    from ctypes import wintypes as W

    class GUID(C.Structure):
        _fields_ = [('Data1', C.c_ulong), ('Data2', C.c_ushort),
                    ('Data3', C.c_ushort), ('Data4', C.c_ubyte * 8)]

        @classmethod
        def from_text(cls, text):
            return cls.from_buffer_copy(uuid.UUID(text).bytes_le)

    class PROPERTYKEY(C.Structure):
        _fields_ = [('fmtid', GUID), ('pid', C.c_ulong)]

    class PROPVARIANT(C.Structure):
        _fields_ = [('vt', C.c_ushort), ('w1', C.c_ushort),
                    ('w2', C.c_ushort), ('w3', C.c_ushort),
                    ('value', C.c_void_p)]

    OLE = C.OleDLL('ole32')
    SHELL = C.WinDLL('shell32')
    OLE.CoInitializeEx.argtypes = [C.c_void_p, C.c_ulong]
    OLE.CoInitializeEx.restype = C.c_long
    OLE.CoUninitialize.argtypes = []
    OLE.CoCreateInstance.argtypes = [C.POINTER(GUID), C.c_void_p, C.c_ulong,
                                     C.POINTER(GUID), C.POINTER(C.c_void_p)]
    OLE.CoCreateInstance.restype = C.c_long
    SHELL.SetCurrentProcessExplicitAppUserModelID.argtypes = [W.LPCWSTR]
    SHELL.SetCurrentProcessExplicitAppUserModelID.restype = C.c_long

    I_DEST = GUID.from_text('6332DEBF-87B5-4670-90C0-5E57B408A49E')
    CLS_DEST = GUID.from_text('77F10CF0-3DB5-4966-B520-B7C54FD35ED6')
    I_OBJECT_ARRAY = GUID.from_text('92CA9DCD-5622-4BBA-A805-5E9F541BD8C9')
    I_COLLECTION = GUID.from_text('5632B1A4-E38A-400A-928A-D4CD63230295')
    CLS_COLLECTION = GUID.from_text('2D3468C1-36A7-43B6-AC24-D3F02FD9607A')
    I_SHELLLINK = GUID.from_text('000214F9-0000-0000-C000-000000000046')
    CLS_SHELLLINK = GUID.from_text('00021401-0000-0000-C000-000000000046')
    I_PROPERTY = GUID.from_text('886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99')
    I_PERSIST = GUID.from_text('0000010B-0000-0000-C000-000000000046')
    TITLE_KEY = PROPERTYKEY(GUID.from_text('F29F85E0-4FF9-1068-AB91-08002B27B3D9'), 2)
    APPID_KEY = PROPERTYKEY(GUID.from_text('9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3'), 5)

    def _check(hr, context):
        if hr < 0:
            raise OSError(f'{context}: HRESULT 0x{hr & 0xffffffff:08X}')
        return hr

    def _call(ptr, index, types=(), *args):
        vtable = C.cast(ptr, C.POINTER(C.POINTER(C.c_void_p))).contents
        function = C.WINFUNCTYPE(C.c_long, C.c_void_p, *types)(vtable[index])
        return _check(function(ptr, *args), f'Windows COM call {index}')

    def _create(clsid, iid):
        result = C.c_void_p()
        _check(OLE.CoCreateInstance(C.byref(clsid), None, 1,
                                    C.byref(iid), C.byref(result)), 'CoCreateInstance')
        return result

    def _query(ptr, iid):
        result = C.c_void_p()
        _call(ptr, 0, (C.POINTER(GUID), C.POINTER(C.c_void_p)),
              C.byref(iid), C.byref(result))
        return result

    def _release(ptr):
        if ptr and ptr.value:
            # IUnknown::Release returns ULONG (not HRESULT).
            vtable = C.cast(ptr, C.POINTER(C.POINTER(C.c_void_p))).contents
            C.WINFUNCTYPE(C.c_ulong, C.c_void_p)(vtable[2])(ptr)

    def _set_property(link, key, value):
        store = _query(link, I_PROPERTY)
        try:
            buffer = C.create_unicode_buffer(value)
            variant = PROPVARIANT(31, 0, 0, 0, C.addressof(buffer))
            _call(store, 6, (C.POINTER(PROPERTYKEY), C.POINTER(PROPVARIANT)),
                  C.byref(key), C.byref(variant))
            _call(store, 7)
        finally:
            _release(store)

    def _shell_link(exe, item_id, title):
        link = _create(CLS_SHELLLINK, I_SHELLLINK)
        try:
            _call(link, 20, (W.LPCWSTR,), str(exe))    # SetPath
            _call(link, 11, (W.LPCWSTR,), argument_for_item(item_id))  # SetArguments
            _call(link, 17, (W.LPCWSTR, C.c_int), str(exe), 0)  # SetIconLocation
            _call(link, 7, (W.LPCWSTR,), f'FRB Launch: {title}')
            _set_property(link, TITLE_KEY, title)
            return link
        except Exception:
            _release(link)
            raise

    def set_process_app_id():
        _check(SHELL.SetCurrentProcessExplicitAppUserModelID(APP_ID), 'SetCurrentProcessExplicitAppUserModelID')

    def _write_start_menu_shortcut(exe):
        """Creates a stable pin source carrying the same explicit AppUserModelID.

        Does not pin anything automatically and does not change existing pins.
        """
        appdata = os.environ.get('APPDATA')
        if not appdata:
            return None
        path = (Path(appdata) / 'Microsoft' / 'Windows' / 'Start Menu' /
                'Programs' / 'FRB Launch.lnk')
        path.parent.mkdir(parents=True, exist_ok=True)
        link = _create(CLS_SHELLLINK, I_SHELLLINK)
        persist = None
        try:
            _call(link, 20, (W.LPCWSTR,), str(exe))
            _call(link, 17, (W.LPCWSTR, C.c_int), str(exe), 0)
            _call(link, 9, (W.LPCWSTR,), str(Path(exe).parent))
            _set_property(link, APPID_KEY, APP_ID)
            persist = _query(link, I_PERSIST)
            _call(persist, 6, (W.LPCWSTR, W.BOOL), str(path), True)  # IPersistFile::Save
            return path
        finally:
            _release(persist)
            _release(link)

    def _removed_items(array):
        """Respect destinations manually removed from this Windows Jump List."""
        excluded = set()
        if not array or not array.value:
            return excluded
        count = C.c_uint()
        _call(array, 3, (C.POINTER(C.c_uint),), C.byref(count))
        for index in range(min(count.value, 500)):
            link = C.c_void_p()
            try:
                _call(array, 4, (C.c_uint, C.POINTER(GUID), C.POINTER(C.c_void_p)),
                      index, C.byref(I_SHELLLINK), C.byref(link))
                buf = C.create_unicode_buffer(1024)
                _call(link, 10, (W.LPWSTR, C.c_int), buf, len(buf))
                item_id = requested_item([buf.value])
                if item_id:
                    excluded.add(item_id)
            except OSError:
                pass
            finally:
                _release(link)
        return excluded

    def _publish_windows(data, exe):
        """Called on its own STA worker thread. Never interrupts Qt UI."""
        hr = OLE.CoInitializeEx(None, 2)  # STA
        _check(hr, 'CoInitializeEx')
        dest = None
        removed = C.c_void_p()
        began = False
        try:
            # A missing Start-menu link must not disable the Jump List itself.
            try:
                _write_start_menu_shortcut(exe)
            except Exception:
                pass
            dest = _create(CLS_DEST, I_DEST)
            _call(dest, 3, (W.LPCWSTR,), APP_ID)
            slots = C.c_uint()
            _call(dest, 4, (C.POINTER(C.c_uint), C.POINTER(GUID), C.POINTER(C.c_void_p)),
                  C.byref(slots), C.byref(I_OBJECT_ARRAY), C.byref(removed))
            began = True
            permitted = min(MAX_ITEMS, max(0, int(slots.value)))
            if not permitted:
                raise RuntimeError('Windows Jump List has no available destination slots')
            excluded = _removed_items(removed)
            # Allocate slots after filtering user-removed destinations.
            filtered = dict(data)
            filtered['items'] = [row for row in data.get('items', [])
                                 if row.get('item_id') not in excluded]
            for page, items in limited_page_entries(filtered, permitted):
                collection = _create(CLS_COLLECTION, I_COLLECTION)
                try:
                    for item_id, title in items:
                        link = _shell_link(exe, item_id, title)
                        try:
                            _call(collection, 5, (C.c_void_p,), link)
                        finally:
                            _release(link)
                    # IObjectCollection also implements IObjectArray.
                    _call(dest, 5, (W.LPCWSTR, C.c_void_p), page, collection)
                finally:
                    _release(collection)
            _call(dest, 8)  # CommitList
            began = False
        except Exception:
            if dest and began:
                try:
                    _call(dest, 11)  # AbortList
                except Exception:
                    pass
            raise
        finally:
            _release(removed)
            _release(dest)
            OLE.CoUninitialize()

else:
    def set_process_app_id():
        return None


def needs_refresh(previous, fingerprint, force=False):
    """A startup refresh verifies/republishes the Shell menu even if unchanged."""
    return bool(force) or previous != fingerprint


def register_async(data, exe, state_dir, logger, *, force=False):
    """Publish on every process start; later only when config/EXE changes.

    The stable Start Menu shortcut and AppUserModelID can be refreshed, but
    existing user-managed taskbar pins are NEVER removed or pinned silently.
    """
    if os.name != 'nt' or not getattr(sys, 'frozen', False):
        return False
    fingerprint = list_fingerprint(data, exe)
    marker = Path(state_dir) / 'jump_list_fingerprint.txt'
    try:
        previous = marker.read_text(encoding='utf-8')
    except OSError:
        previous = None
    if not needs_refresh(previous, fingerprint, force):
        return False

    def worker():
        try:
            with _REGISTRATION_LOCK:
                try:
                    previous = marker.read_text(encoding='utf-8')
                except OSError:
                    previous = None
                if not needs_refresh(previous, fingerprint, force):
                    return
                _publish_windows(data, exe)
                marker.write_text(fingerprint, encoding='utf-8')
                logger.info('JUMP_LIST synced page=work items=%d force=%s',
                            sum(len(items) for _, items in page_root_entries(data)), force)
        except Exception:
            logger.exception('JUMP_LIST registration failed (Launch is still usable)')

    threading.Thread(target=worker, name='FRBLaunchJumpList', daemon=True).start()
    return True


_REGISTRATION_LOCK = threading.Lock()
