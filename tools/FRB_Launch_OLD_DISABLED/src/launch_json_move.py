"""Strict, filesystem-free drag-and-drop contract for Studio-authored Launch JSON.

This is intentionally distinct from Qt text/uri-list (which means *copy* a
physical file) and from the older order-only popup drag. No physical path is
present in the payload and no move is ever implemented with os/shutil.
"""
from __future__ import annotations
import json

MOVE_MIME = 'application/x-frb-launch-json-item-move-v1'


def encode_source(page_id, item_id):
    if not page_id or not item_id:
        raise ValueError('An authored item needs a Page and item ID')
    return json.dumps({'version': 1, 'page_id': str(page_id),
                       'item_id': str(item_id)}, ensure_ascii=False).encode('utf-8')


def decode_source(data):
    try:
        value = json.loads(bytes(data).decode('utf-8'))
    except (ValueError, UnicodeError, TypeError):
        return None
    if (not isinstance(value, dict) or value.get('version') != 1 or
            not isinstance(value.get('page_id'), str) or
            not isinstance(value.get('item_id'), str) or
            not value['page_id'] or not value['item_id']):
        return None
    return value['page_id'], value['item_id']


def drop_placement(directory_node, hovered_node=None, *, fraction=0.5, allow_blank=True):
    """Return destination placement for one JSON item, or None to forbid.

    The source/destination must still be verified against authored items by
    Launch before passing the plan to Studio CLI. Runtime bookmark entries,
    installed apps and ordinary filesystem rows fail CLOSED here.

    Hover middle 40% of an authored category -> into folder (append).
    Hover at edges -> insert before/after this sibling. For a leaf only
    before/after is possible. Blank area -> append to the current folder.
    """
    if not isinstance(directory_node, dict) or directory_node.get('source') != 'launch_json':
        return None
    if directory_node.get('runtime_catalog'):
        return None
    page_id = str(directory_node.get('page_id') or '')
    current_item = str(directory_node.get('item_id') or '')
    if not page_id:
        return None
    if hovered_node is None:
        if not allow_blank:
            return None
        if current_item and (directory_node.get('row') or {}).get('item_kind') != 'category':
            return None
        return {'group_id': page_id, 'parent_id': current_item, 'position': 'end'}
    if (not isinstance(hovered_node, dict) or
            hovered_node.get('source') != 'launch_json' or
            hovered_node.get('runtime_catalog') or
            str(hovered_node.get('page_id') or '') != page_id):
        return None
    item_id = str(hovered_node.get('item_id') or '')
    if not item_id:
        return None
    # A folder's middle is an unambiguous 'move INTO folder' gesture.
    if (0.30 <= fraction <= 0.70 and
            (hovered_node.get('row') or {}).get('item_kind') == 'category'):
        return {'group_id': page_id, 'parent_id': item_id, 'position': 'end'}
    return {'group_id': page_id,
            'parent_id': str(hovered_node.get('parent_item_id') or ''),
            'position': 'before' if fraction < 0.5 else 'after',
            'anchor_id': item_id}


def exp_folder_placement(node):
    """Exp has folders and Page headings; never a physical folder target."""
    if (not isinstance(node, dict) or node.get('source') != 'launch_json' or
            node.get('runtime_catalog')):
        return None
    page_id = str(node.get('page_id') or '')
    if not page_id:
        return None
    item_id = str(node.get('item_id') or '')
    if item_id and (node.get('row') or {}).get('item_kind') != 'category':
        return None
    return {'group_id': page_id, 'parent_id': item_id, 'position': 'end'}


def registered_root_reorder_placement(source, target, *, page_id, parent_id,
                                      fraction=0.5):
    """Root-to-root reorder ONLY: no reparent, filesystem move or PC target."""
    if not (isinstance(source, tuple) and len(source) == 2 and
            source[0] == page_id and source[1]):
        return None
    if target is None:  # Files Exp blank background: append to Files roots.
        return {'group_id': page_id, 'parent_id': parent_id, 'position': 'end'}
    if not (isinstance(target, tuple) and len(target) == 2 and
            target[0] == page_id and target[1]):
        return None
    return {'group_id': page_id, 'parent_id': parent_id,
            'position': 'before' if fraction < 0.5 else 'after',
            'anchor_id': target[1]}
