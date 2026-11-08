"""Qt-free routing rule for author-registered URL Open actions.

An unqualified HTTP(S) Open should create a NEW tab in FRB Launch Browser.
Explicit Chrome/Edge/profile destinations remain external. Files, custom
schemes and multi-step commands are left to the existing action executor.
"""
from webview_routes import bookmark_web_url


def registered_embedded_url(step):
    if not isinstance(step, dict) or step.get('launch_action_type') != 'Open':
        return None
    if str(step.get('launch_browser') or '').strip():
        return None
    if str(step.get('launch_browser_profile') or '').strip():
        return None
    # Reuse the existing HTTP(S) guard; never pass a file or shell command
    # through the embedded WebView. The step has already been expanded.
    return bookmark_web_url({
        'item_kind': 'command', 'launch_actions': [step],
    })
