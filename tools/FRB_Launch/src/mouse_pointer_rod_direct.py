"""Opt-in Mouse Pointer Rod direct operations on Launch's *own* Files views.

The pointer rod reports only a desktop position and a click intent.  This
adapter converts it into a Qt item/index and invokes existing selection or
expansion code without moving the OS cursor or synthesizing Qt/Win32 events.

Scope v0.8: blue clicks select List/Exp; only Exp double-click toggles.
The central ぐりぐり owns activation and context menus. Other apps are untouched.
The rod remains
a target-agnostic control; a different adapter can be tried later.
"""


def _hit(tree, position, point_type):
    """Return a viewport-local point iff the *visible* viewport contains it."""
    if tree is None or not tree.isVisible():
        return None
    viewport = tree.viewport()
    if not viewport.isVisible():
        return None
    global_point = point_type(round(position[0]), round(position[1]))
    local = viewport.mapFromGlobal(global_point)
    return local if viewport.rect().contains(local) else None


def direct_files_action(launcher, screen_position, action='select', *, point_type=None):
    """Dispatch a pointing-rod action to an existing Launch Files row.

    Returns True only when the rod hit an actionable row/index and the request
    was handled. This *never* moves the system pointer or synthesizes mouse
    events. The native click remains confined to the rod pad.

    'select' selects the row; 'double' selects Files List without activation
    or toggles an Exp branch; 'context' opens the already
    existing context menu (possibly containing destructive actions, but does
    NOT trigger one). Legacy 'toggle' is Exp-only for compatibility.
    """
    if action not in ('select', 'double', 'toggle', 'context'):
        return False
    if point_type is None:
        from PySide6.QtCore import QPoint
        point_type = QPoint

    view = getattr(launcher, 'expanded_view', None)
    if (view is None or not view.isVisible()
            or getattr(view, '_workspace_mode', None) != 'files'):
        return False

    # Only the displayed Files List, not the old/hidden first-column tree.
    pane = getattr(view, 'middle', None)
    list_tree = getattr(pane, 'tree', None)
    list_point = _hit(list_tree, screen_position, point_type)
    if list_point is not None:
        item = list_tree.itemAt(list_point)
        if item is None or action == 'toggle':
            return False
        # Use the one authoritative Files target (QSS, Remote, preview state).
        launcher.set_files_operating_target('directory')
        list_tree.deliberate_blank_selection = False
        list_tree.clearSelection()
        list_tree.setCurrentItem(item)
        item.setSelected(True)
        list_tree.viewport().update()
        # Even on double-click, blue List selection must NEVER open a file.
        # Activation and context menus belong to the native ぐりぐり button.
        if action == 'context':
            view.context_menu(view.middle, list_point,
                              global_pos=point_type(round(screen_position[0]),
                                                    round(screen_position[1])))
        # Single click remains selection only; never auto-descend into folders.
        return True

    exp = getattr(view, 'embedded_files_exp', None)
    exp_tree = getattr(exp, 'tree', None)
    exp_point = _hit(exp_tree, screen_position, point_type)
    if exp_point is None:
        return False
    index = exp_tree.indexAt(exp_point)
    if not index.isValid():
        return False
    launcher.set_files_operating_target('files_exp')
    exp_tree.setCurrentIndex(index)
    if action in ('toggle', 'double'):
        # Native expanded/collapsed signals trigger the existing lazy-load,
        # breadcrumb, and persistence handling. No UI event is forged.
        if exp_tree.isExpanded(index):
            exp_tree.collapse(index)
        elif exp_tree.model().hasChildren(index):
            exp_tree.expand(index)
    elif action == 'context':
        # Existing Exp handler resolves physical/virtual folder targets and
        # emits its existing context signals (including rename guards).
        exp._show_folder_context(exp_point)
    # setCurrentIndex() invokes the existing debounced Exp selection preview.
    return True
