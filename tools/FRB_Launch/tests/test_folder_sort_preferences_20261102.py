"""Qt-free functional checks: per-folder overrides, never Downloads-specific."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from folder_sort_preferences import (DEFAULT_SORT, directory_sort_key,
                                     load_directory_sort, save_directory_sort,
                                     transfer_directory_sort)

MODES = {'name', 'name_desc', 'date_asc', 'date_desc', 'size_asc',
         'size_desc', 'type_asc', 'type_desc'}


class Settings:
    def __init__(self):
        self.data = {}

    def value(self, key, default=None):
        return self.data.get(key, default)

    def setValue(self, key, value):
        self.data[key] = value

    def remove(self, key):
        self.data.pop(key, None)


def test_custom_sort_saved_only_to_one_directory_and_restored():
    settings = Settings()
    a = 'F:/FRB/Downloads'
    b = 'F:/FRB/Articles'
    assert load_directory_sort(settings, a, MODES) == DEFAULT_SORT
    assert load_directory_sort(settings, b, MODES) == DEFAULT_SORT
    save_directory_sort(settings, a, 'date_desc', MODES)
    assert load_directory_sort(settings, a, MODES) == 'date_desc'
    assert load_directory_sort(settings, b, MODES) == DEFAULT_SORT
    assert len(settings.data) == 1
    # A new window/instance reads the same QSettings key.
    assert load_directory_sort(settings, a, MODES) == 'date_desc'


def test_any_directory_can_have_distinct_override():
    settings = Settings()
    for folder, mode in [('C:/Temp', 'size_desc'), ('D:/Projects', 'type_asc'),
                         ('F:/FRB/README', 'name_desc')]:
        save_directory_sort(settings, folder, mode, MODES)
        assert load_directory_sort(settings, folder, MODES) == mode


def test_return_to_standard_removes_per_folder_override():
    settings = Settings()
    folder = 'C:/Users/Public/Test'
    assert save_directory_sort(settings, folder, DEFAULT_SORT, MODES)
    assert settings.data == {}
    save_directory_sort(settings, folder, 'date_desc', MODES)
    save_directory_sort(settings, folder, DEFAULT_SORT, MODES)
    assert settings.data == {}
    assert load_directory_sort(settings, folder, MODES) == DEFAULT_SORT


def test_windows_path_key_normalization_and_validation():
    assert directory_sort_key('F:/FRB/TOOLS') == directory_sort_key(r'f:\frb\tools')
    assert directory_sort_key(None) is None
    settings = Settings()
    settings.setValue(directory_sort_key('F:/Test'), 'invalid')
    assert load_directory_sort(settings, 'F:/Test', MODES) == DEFAULT_SORT
    try:
        save_directory_sort(settings, 'F:/Test', 'invalid', MODES)
    except ValueError:
        pass
    else:
        assert False, 'unsupported sort must be rejected'


def test_legacy_global_value_does_not_change_folder_defaults():
    settings = Settings()
    settings.setValue('expanded_middle_sort', 'date_desc')
    assert load_directory_sort(settings, 'F:/random', MODES) == 'name'


def test_rename_preserves_the_folder_own_custom_sort():
    settings = Settings()
    save_directory_sort(settings, 'F:/FRB/old', 'date_desc', MODES)
    assert transfer_directory_sort(settings, 'F:/FRB/old', 'F:/FRB/new', MODES)
    assert load_directory_sort(settings, 'F:/FRB/new', MODES) == 'date_desc'
    assert load_directory_sort(settings, 'F:/FRB/old', MODES) == DEFAULT_SORT
