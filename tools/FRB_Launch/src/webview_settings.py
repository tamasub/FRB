"""Non-Qt configuration for the opt-in Launch embedded WebView."""
import json
from pathlib import Path
from urllib.parse import urlsplit

DEFAULTS = {
    'mode': 'embedded',  # embedded | external (corporate-policy-friendly)
    'remember_login': True,
    'download_directory': '',  # blank = the OS Downloads folder
    'new_tab_url': 'https://www.google.com/',
    'default_zoom_percent': 90,  # 100 = original size; applied to each new Web tab
    'bookmark_preview_delay_ms': 650,
    'keep_tabs_on_home': True,
}


def valid_http_url(value):
    if not isinstance(value, str) or not value or any(c.isspace() for c in value):
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme.lower() in ('http', 'https') and bool(parsed.hostname)
    except ValueError:
        return False


def read_webview_settings(path):
    settings = dict(DEFAULTS)
    try:
        raw = json.loads(Path(path).read_text(encoding='utf-8-sig'))
        if not isinstance(raw, dict):
            return settings
    except (OSError, ValueError, TypeError):
        return settings
    if raw.get('mode') in ('embedded', 'external'):
        settings['mode'] = raw['mode']
    if isinstance(raw.get('remember_login'), bool):
        settings['remember_login'] = raw['remember_login']
    directory = raw.get('download_directory')
    if isinstance(directory, str) and len(directory) < 1024 and '\x00' not in directory:
        settings['download_directory'] = directory
    if valid_http_url(raw.get('new_tab_url')):
        settings['new_tab_url'] = raw['new_tab_url']
    zoom = raw.get('default_zoom_percent')
    # Keep the configured zoom readable as a percentage; reject bool, NaN,
    # excessively small or excessively large values.
    if (isinstance(zoom, (int, float)) and not isinstance(zoom, bool)
            and 50 <= zoom <= 200):
        settings['default_zoom_percent'] = zoom
    delay = raw.get('bookmark_preview_delay_ms')
    if isinstance(delay, int) and not isinstance(delay, bool) and 100 <= delay <= 5000:
        settings['bookmark_preview_delay_ms'] = delay
    if isinstance(raw.get('keep_tabs_on_home'), bool):
        settings['keep_tabs_on_home'] = raw['keep_tabs_on_home']
    return settings
