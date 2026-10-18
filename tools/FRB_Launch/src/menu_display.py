"""Pure display rules for keyboard-navigable cascade menus.

This module never rewrites source rows: names, descriptions and full URLs remain
available to search, tooltips and launch actions even when rendered text is short.
"""


def cascade_label(row, parent_kind, available_text_width, elide, measure):
    """Return (visible_label, complete_tooltip) using Qt-compatible callbacks.

    elide(text, width): measure and add a trailing ellipsis if necessary.
    measure(text): width in screen pixels.
    """
    title = str(row.get('title', ''))
    description = str(row.get('description', '') or '')
    tooltip = title + ('\n' + description if description else '')
    folder = row.get('item_kind') in {'category', 'directory'}

    if folder:
        # Keep the right-facing chevron, including on very long folder names.
        chevron = '  ›'
        name_width = max(50, available_text_width - measure(chevron))
        return elide(title, name_width) + chevron, tooltip

    label = title
    if parent_kind != 'directory' and not row.get('_browser_bookmark') and description:
        label += '    ' + ' '.join(description.split())
    return elide(label, available_text_width), tooltip
