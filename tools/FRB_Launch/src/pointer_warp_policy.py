"""Public-release pointer movement defaults and startup notice policy.

Keep the existing inverted QSettings key for backward compatibility.  A key
explicitly saved by an older installation keeps its value; an absent key
represents a fresh installation and defaults to pointer movement OFF.
"""

WARP_DISABLED_KEY = 'vdi_no_cursor_warp'
NOTICE_DISMISSED_KEY = 'pointer_warp_notice_dont_show_again'


def _enabled(value):
    return str(value).strip().lower() in ('true', '1', 'yes', 'on')


def read_pointer_warp_enabled(settings):
    # Historical setting is inverted: "VDI without cursor warp".
    return not _enabled(settings.value(WARP_DISABLED_KEY, 'true'))


def should_show_pointer_warp_notice(settings, pointer_warp_enabled):
    return (not pointer_warp_enabled and
            not _enabled(settings.value(NOTICE_DISMISSED_KEY, 'false')))
