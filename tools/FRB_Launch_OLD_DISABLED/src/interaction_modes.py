"""Persistent interaction preferences, with legacy-safe defaults."""


def read_dismiss_on_outside(value):
    """Default True; QSettings may return a bool or a string."""
    if isinstance(value, bool):
        return value
    return str(value).strip().casefold() not in ('0', 'false', 'no', 'off')


def read_folder_open_mode(value):
    """Ignore unknown saved values instead of silently changing click behavior."""
    return 'double' if str(value).strip().casefold() == 'double' else 'single'


def is_double_click_folder(value):
    return read_folder_open_mode(value) == 'double'
