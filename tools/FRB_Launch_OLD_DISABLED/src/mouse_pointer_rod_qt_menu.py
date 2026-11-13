"""Generic Qt QAction bridge for a rod pointing at Launch's Page cascade.

Qt.Tool CascadeMenu columns may not accept injected Windows button events while
another Launch control owns the input sequence.  The Page cascade already
registers every navigable row as a QAction; execute THAT registered action,
not a duplicate, item-specific command.  Other menus and other Windows apps
continue through the ordinary native SendInput route.

The module deliberately imports no Qt types; it only uses QMenu/QAction's
public hit-test and trigger interface.  This makes the semantics testable
without a Windows desktop and keeps it independent of the main app module.
"""


def _page_action_at(menu, target):
    """Resolve an enabled user action at a *global* rod tip, or return None."""
    try:
        if (not menu.isVisible()
                or not getattr(menu, 'remote_page_navigation', False)
                or getattr(menu, 'bookmark_navigation', False)):
            return None
        local = menu.mapFromGlobal(target)
        if not menu.rect().contains(local):
            return None
        action = menu.actionAt(local)
        if (action is None or action is getattr(menu, 'filter_action', None)
                or not action.isVisible() or not action.isEnabled()):
            return None
        # The search bar is a QWidgetAction, not a runnable row.  In that
        # case retain native clicking so the editor can receive focus.
        row = action.data()
        if not isinstance(row, dict) and not action.property('launch_right_arrow_executes'):
            return None
        return action
    except RuntimeError:
        # Qt might delete a cascade between popup closing and the input timer.
        return None


def _column_depth(menu):
    """Nested child columns win when their native frame overlaps the root."""
    depth = 0
    seen = {id(menu)}
    node = menu
    for _ in range(32):
        try:
            node = node.parentWidget()
        except (RuntimeError, AttributeError):
            break
        if node is None or id(node) in seen:
            break
        seen.add(id(node))
        if getattr(node, 'remote_page_navigation', False):
            depth += 1
    return depth


def dispatch_page_cascade_action(target, menus):
    """Activate one Page QAction under the rod tip; return True if dispatched.

    This is an opt-in bridge for the non-grabbing Page cascade only, NOT an
    alternate file operation implementation.  QAction.trigger() invokes the
    existing menu wiring for folder expansion and command execution.
    """
    candidates = sorted(list(menus), key=_column_depth, reverse=True)
    for menu in candidates:
        action = _page_action_at(menu, target)
        if action is None:
            continue
        try:
            menu.setActiveAction(action)
            action.trigger()
        except RuntimeError:
            # Closing/replacing a Page menu can invalidate the C++ object.
            continue
        return True
    return False
