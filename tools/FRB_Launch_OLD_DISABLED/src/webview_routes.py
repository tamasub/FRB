"""Small, Qt-independent guard for the FRB Launch WebView experiment.

Only HTTP(S) Open actions qualify. Do not turn filesystem paths, scripts,
SendKeys, or arbitrary URI schemes into embedded browser navigation.
"""
from urllib.parse import urlsplit


def bookmark_web_url(row):
    if not isinstance(row, dict) or row.get('item_kind') != 'command':
        return None
    steps = row.get('launch_actions')
    if not isinstance(steps, list) or len(steps) != 1:
        return None
    step = steps[0]
    if not isinstance(step, dict) or step.get('launch_action_type') != 'Open':
        return None
    # Browser bookmark URLs escape percent signs for the Launch Expander.
    raw = step.get('launch_target', '')
    if not isinstance(raw, str):
        return None
    url = raw.replace('%%', '%').strip()
    if any(char.isspace() for char in url) or any(ord(char) < 32 for char in url):
        return None
    try:
        parts = urlsplit(url)
        if parts.scheme.lower() not in ('http', 'https') or not parts.hostname:
            return None
    except ValueError:
        return None
    return url
