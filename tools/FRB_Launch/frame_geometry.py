"""Pure geometry for dragging the frameless launcher's outer borders."""


def resize_frame(edge, x, y, width, height, dx, dy,
                 min_width, min_height, max_width, max_height):
    """Return (x, y, width, height), keeping the opposite edges stationary.

    The requested dimensions are clamped without moving the anchored edge;
    corners simply combine a horizontal and a vertical resize.
    """
    if 'right' in edge:
        width = max(min_width, min(width + dx, max_width))
    elif 'left' in edge:
        requested = max(min_width, min(width - dx, max_width))
        x += width - requested
        width = requested
    if 'bottom' in edge:
        height = max(min_height, min(height + dy, max_height))
    elif 'top' in edge:
        requested = max(min_height, min(height - dy, max_height))
        y += height - requested
        height = requested
    return x, y, width, height
