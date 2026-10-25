"""Windows FILE_ATTRIBUTE_HIDDEN filtering for filesystem browsing/indexing.

A leading dot alone is *not* the Windows Hidden attribute.  Keep .gitignore
and other dot-named items visible unless Windows marks them hidden.
"""
import os
import stat


def is_hidden_attribute(path):
    """Return True for Windows Hidden attribute; safely handle vanishing paths.

    st_file_attributes is available from os.stat on Windows. On POSIX it is
    absent (Windows-specific attribute filtering intentionally does nothing).
    """
    try:
        attributes = getattr(os.stat(path, follow_symlinks=False),
                             'st_file_attributes', 0)
    except (OSError, ValueError):
        # A transiently inaccessible entry must not crash directory browsing.
        return False
    return bool(attributes & getattr(stat, 'FILE_ATTRIBUTE_HIDDEN', 0x2))
