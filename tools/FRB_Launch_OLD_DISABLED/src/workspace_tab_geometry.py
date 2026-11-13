"""One-pixel underline geometry for joined Files/Browser workspace tabs.

Pure calculation: no Qt imports, so boundary behavior can be tested without GUI.
"""


def workspace_tab_line_segments(width, active_left, active_right):
    """Return portions of the underline outside the active tab, in pixels.

    The active tab visually extends to the content below: there must never be
    a line across its bottom edge, even when the strip is resized or scrolled.
    """
    width = max(0, int(width))
    if width <= 0:
        return []
    left = max(0, min(width, int(active_left)))
    right = max(left, min(width, int(active_right)))
    if left == right:
        return [(0, width - 1)]
    result = []
    if left > 0:
        result.append((0, left - 1))
    if right < width:
        result.append((right, width - 1))
    return result
