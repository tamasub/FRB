"""Route authored single-folder Open actions to FRB Launch Files.

Pure decision logic: no Qt calls or browser side effects. Explicit browser
profiles, URLs, shell schemes, missing paths and multi-step jobs stay on their
original execution path.
"""

from pathlib import Path


def embedded_folder_target(steps, *, is_dir=None):
    """Return the existing directory for a single plain Open, or None."""
    if not isinstance(steps, (list, tuple)) or len(steps) != 1:
        return None
    step = steps[0]
    if not isinstance(step, dict) or step.get('launch_action_type') != 'Open':
        return None
    if step.get('launch_browser') or step.get('launch_browser_profile'):
        return None
    target = step.get('launch_target')
    if not isinstance(target, str) or not target or target.strip() != target:
        return None
    # Only physical local directories. Shell namespaces and URLs are external.
    if target.lower().startswith(('shell:', 'http:', 'https:', 'file:')):
        return None
    directory_check = is_dir if is_dir is not None else lambda path: Path(path).is_dir()
    try:
        return target if directory_check(target) else None
    except (OSError, ValueError):
        return None
