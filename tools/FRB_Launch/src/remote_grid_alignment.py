"""Geometry for the optional Files grid-aligned Remote + Files Exp layout.

All coordinates are global Qt logical pixels; screen/right/bottom bounds here
are exclusive.  Keeping the calculation Qt-free makes edge cases testable on
platforms without a Windows desktop / PySide6.
"""


def clamp(value, low, high):
    return max(low, min(value, max(low, high)))


def files_grid_layout(launch_left, launch_right, grid_top, launch_bottom,
                      remote_width, exp_width, screen_left, screen_right,
                      screen_top, screen_bottom, gap=3, minimum_height=180):
    """Return (remote_x, remote_y, exp_x, exp_y, exp_height).

    Prefer placing both panels immediately LEFT of Launch.  If the entire pair
    cannot fit there, use its right side when possible, or keep the pair fully
    on-screen even when Launch is too close to a screen edge.
    """
    remote_width, exp_width = max(1, remote_width), max(1, exp_width)
    usable_height = max(1, screen_bottom - screen_top)
    min_height = min(minimum_height, usable_height)
    y = clamp(grid_top, screen_top, screen_bottom - min_height)
    h = clamp(launch_bottom - y, min_height, screen_bottom - y)
    pair_width = remote_width + exp_width + gap
    if launch_left - gap - pair_width >= screen_left:
        exp_x = launch_left - gap - exp_width
        remote_x = exp_x - gap - remote_width
    elif launch_right + gap + pair_width <= screen_right:
        remote_x = launch_right + gap
        exp_x = remote_x + remote_width + gap
    else:
        # The launch window leaves too little room on either side; keep both
        # companions visible rather than losing a Remote beyond the desktop.
        remote_x = clamp(launch_left - gap - pair_width,
                         screen_left, screen_right - pair_width)
        exp_x = remote_x + remote_width + gap
    return remote_x, y, exp_x, y, h


def remote_next_to_exp(exp_x, exp_y, exp_width, remote_width,
                       screen_left, screen_right, screen_top, screen_bottom,
                       remote_height, gap=3):
    """Place Remote next to a manually positioned Files Exp window."""
    left = exp_x - gap - remote_width
    right = exp_x + exp_width + gap
    if left >= screen_left:
        x = left
    elif right + remote_width <= screen_right:
        x = right
    else:
        x = clamp(left, screen_left, screen_right - remote_width)
    return x, clamp(exp_y, screen_top, screen_bottom - remote_height)
