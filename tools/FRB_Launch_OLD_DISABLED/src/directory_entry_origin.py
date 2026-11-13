"""Reversible origin for a JSON folder opening a real Files directory.

No Qt, no generic visit history. It is a strict *source transition* marker:
only the direct originating JSON folder can be restored at its entry path.
"""
import ntpath


def _norm(path):
    return ntpath.normcase(ntpath.normpath(str(path or '')))


def within_entry(path, entry):
    current, root = _norm(path), _norm(entry)
    return bool(root and current and (
        current == root or current.startswith(root.rstrip('\\') + '\\')))


def at_entry_boundary(path, entry):
    return bool(path and entry and _norm(path) == _norm(entry))


def next_entry_origin(prior, virtual, destination):
    if (isinstance(virtual, dict)
            and virtual.get('source') == 'launch_json'
            and virtual.get('kind') in ('folder', 'linked_directory')):
        return {'node': virtual, 'entry_path': destination}
    if prior and within_entry(destination, prior['entry_path']):
        return prior
    return None
