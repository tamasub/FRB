"""Screen-safe placement for the non-activating kana Pokeball hint.

All coordinates are screen-global pixels, so parent widget hierarchy is not
needed. Anchor above the PRESSED key with a constant gap (rather than the
keyboard grid's first row). If the screen edge prevents this, place the
passive guide beside or below that same key, never on top of the key.
"""


def place_guide(key_rect, keyboard_rect, available_rect, guide_size, gap=8, margin=4):
    kx, ky, kw, kh = key_rect
    bx, by, bw, bh = keyboard_rect
    sx, sy, sw, sh = available_rect
    gw, gh = guide_size
    max_x = sx + sw - gw - margin
    max_y = sy + sh - gh - margin
    left = sx + margin
    top = sy + margin

    def clamp(value, low, high):
        return max(low, min(value, max(low, high)))

    preferred_x = kx + (kw - gw) // 2
    x = clamp(preferred_x, left, max_x)
    # Using the pressed key (ky), NOT the keyboard grid (by), is essential:
    # the 4th-row "わ" must bring the guide down with it, without changing
    # the tactile gap between the button and the circular guide.
    above_y = ky - gh - gap
    if above_y >= top:
        return (x, above_y)

    # Near the screen's top edge, put the guide beside the pressed row.
    # A side placement keeps the same gap from the key when possible.
    side_y = clamp(ky + (kh - gh) // 2, top, max_y)
    right_x = bx + bw + gap
    left_x = bx - gw - gap
    right_ok = right_x + gw <= sx + sw - margin
    left_ok = left_x >= left
    if right_ok and (not left_ok or kx + kw // 2 >= bx + bw // 2):
        return (right_x, side_y)
    if left_ok:
        return (left_x, side_y)
    if right_ok:
        return (right_x, side_y)

    below_y = ky + kh + gap
    if below_y <= max_y:
        return (x, below_y)

    # Extremely small screens have no wholly non-overlapping placement.
    # Prefer an on-screen hint over losing it beyond the display edge.
    return (x, clamp(above_y, top, max_y))
