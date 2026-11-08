"""FRB Launch: narrow Qt WebEngine JavaScript console noise filter.

Only the three Chromium/web-page messages below are hidden from the
_run_windows.bat console. This does NOT fix the underlying failures.
Set to False to see the messages for troubleshooting site typography/GPU.
All other console errors are preserved.
"""

SUPPRESS_KNOWN_WEB_CONSOLE_NOISE = True

_KNOWN_PREFIXES = (
    'Failed to decode downloaded font: https://fonts.gstatic.com/',
    'OTS parsing error: Unable to instantiate font face from font data.',
    'Failed to create WebGPU Context Provider',
)


def should_suppress_console_message(message):
    if not SUPPRESS_KNOWN_WEB_CONSOLE_NOISE:
        return False
    return isinstance(message, str) and message.startswith(_KNOWN_PREFIXES)
