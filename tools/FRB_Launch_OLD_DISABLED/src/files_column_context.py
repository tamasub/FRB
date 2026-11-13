"""Shared navigation contract for EVERY Files Exp/List context menu.

This module intentionally has no Qt dependency.  An existing menu only needs
its normal QAction API; the caller supplies the QAction and icon factories.
It owns labels and presence, never folder traversal or filesystem mutations.
"""

NAVIGATION = {
    'exp': ('List列へ進む', 'forward', 'directory'),
    'list': ('Exp列へ戻る', 'back_to_exp', 'files_exp'),
}


def install_column_navigation(menu, column, make_action, make_icon, dispatch):
    """Install exactly one column switch, independent of Remote visibility.

    ``dispatch`` is called only after QAction activation.  The owning launcher
    closes the popup before scheduling the actual operating-target change.
    """
    if column not in NAVIGATION:
        raise ValueError(f'未知のFiles列です: {column}')
    existing = getattr(menu, '_frb_column_navigation', None)
    if existing is not None:
        if existing != column:
            raise ValueError('同じメニューへ異なる列操作を割り当てられません')
        return False
    label, icon_name, target = NAVIGATION[column]
    old_actions = list(menu.actions())
    first = old_actions[0] if old_actions else None
    action = make_action(label, menu)
    action.setIcon(make_icon(icon_name))
    action.setIconVisibleInMenu(True)
    action.setToolTip('表示中のフォルダーを変えず、操作対象を'
                      + ('List列' if column == 'exp' else 'Exp列') + 'に切り替えます')
    action.triggered.connect(lambda checked=False: dispatch(menu, target))
    if first is not None:
        menu.insertAction(first, action)
        menu.insertSeparator(first)
    else:
        menu.addAction(action)
    menu._frb_column_navigation = column
    menu._frb_column_navigation_action = action
    return True
