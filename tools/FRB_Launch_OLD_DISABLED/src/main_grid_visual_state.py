"""FRB Launch's main grid row-appearance contract (Qt independent).

Focus, keyboard current row, and pointer hover are independent state axes.
An inactive current row is outlined, not selected blue; keyboard-focused
current row is both filled and outlined. Pointer hover paints a fill only.
"""

ROW_PALETTE = {
    'light': {
        'focused_current': '#d6e7f8',
        'hover': '#c9e1f8',
        'outline': '#6396c5',
    },
    'dark': {
        'focused_current': '#304d70',
        'hover': '#344e6c',
        'outline': '#88aed2',
    },
}


def row_visual_state(*, current=False, focused=False, hovered=False):
    """Return normal, hover, inactive_current, or focused_current.

    Keyboard current + grid focus outranks hover; otherwise hover takes
    precedence so moving the pointer never paints an inactive outline.
    """
    if current and focused:
        return 'focused_current'
    if hovered:
        return 'hover'
    if current:
        return 'inactive_current'
    return 'normal'


def row_fill(palette, state):
    return palette.get(state)


def row_has_outline(state):
    return state in ('focused_current', 'inactive_current')
