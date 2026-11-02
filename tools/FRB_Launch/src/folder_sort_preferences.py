"""Per-directory Files-column sort preferences (independent from Launch DataJSON).

The default name ascending is deliberately not persisted. QSettings receives
only changed folders, not one global sort applied to every folder.
"""
import hashlib
import ntpath

DEFAULT_SORT = 'name'
PREFIX = 'expanded_middle_sort_by_folder_v1/'


def directory_sort_key(directory):
    """Stable key across runs, Windows case differences and slash styles."""
    if not directory:
        return None
    path = ntpath.normcase(ntpath.normpath(str(directory).replace('/', '\\')))
    if not path or path == '.':
        return None
    return PREFIX + hashlib.sha256(path.encode('utf-8')).hexdigest()


def load_directory_sort(settings, directory, valid_modes):
    key = directory_sort_key(directory)
    value = settings.value(key, DEFAULT_SORT) if key else DEFAULT_SORT
    return str(value) if str(value) in valid_modes else DEFAULT_SORT


def save_directory_sort(settings, directory, mode, valid_modes):
    """Store nondefault only; reverting to default removes the override."""
    if mode not in valid_modes:
        raise ValueError('Unsupported folder sort: ' + str(mode))
    key = directory_sort_key(directory)
    if key is None:
        return False
    if mode == DEFAULT_SORT:
        settings.remove(key)
    else:
        settings.setValue(key, mode)
    sync = getattr(settings, 'sync', None)
    if callable(sync):
        sync()
    return True


def transfer_directory_sort(settings, old_directory, new_directory, valid_modes):
    """Keep the renamed folder's own sort choice attached to its new path."""
    old_key = directory_sort_key(old_directory)
    new_key = directory_sort_key(new_directory)
    if not old_key or not new_key or old_key == new_key:
        return False
    mode = load_directory_sort(settings, old_directory, valid_modes)
    if mode != DEFAULT_SORT:
        save_directory_sort(settings, new_directory, mode, valid_modes)
    settings.remove(old_key)
    sync = getattr(settings, 'sync', None)
    if callable(sync):
        sync()
    return True
