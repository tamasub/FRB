"""Files List metadata projection for physical Files vs. Launch JSON menus.

The source row is preserved, including its original Studio item_kind.
There are no filesystem-stat calls or action changes in the virtual view.
"""

FILES_HEADERS = ('名前', '更新日', 'サイズ', '種類', '')
LAUNCH_HEADERS = ('名前', '説明', '項目の種類', '', '')


def virtual_description(row):
    return str(row.get('description') or '')


def virtual_item_kind(row):
    """Show the original JSON item_kind, not the projected virtual-file kind."""
    node = row.get('_launch_virtual_node') or {}
    original = node.get('row') or {}
    return str(original.get('item_kind') or row.get('item_kind') or '')


def virtual_sort_mode_for_header(column, previous='name'):
    """Only the three visible virtual metadata columns are sortable."""
    pairs = {
        0: ('name', 'name_desc'),
        1: ('description_asc', 'description_desc'),
        2: ('item_kind_asc', 'item_kind_desc'),
    }
    pair = pairs.get(column)
    return None if pair is None else (pair[1] if previous == pair[0] else pair[0])
