"""Modern dark page tabs for the FRB Launch QTabBar.

Keep tab visuals here rather than relying on the Windows / Qt native tab
painting.  In particular, define the *unselected* state explicitly: if only
:selected is styled, Qt can draw the other tabs as old-style raised buttons.
The tab's geometry, navigation, and page IDs remain owned by the QTabBar.
"""

PAGE_TABS_QSS = """
QTabBar {
    background: transparent;
    border: none;
    outline: none;
}
QTabBar::tab {
    /* Idle sits one subtle step below hover, not lost in the dark header. */
    background: #304340;
    color: #afbdc9;
    border: 1px solid #42595b;
    border-bottom: 2px solid #42595b;
    border-radius: 7px;
    margin-right: 5px;
    padding: 4px 15px;
    min-height: 23px;
}
QTabBar::tab:hover:!selected {
    /* Only a very small color lift on pointer hover. */
    background: #344746;
    color: #eef5f7;
    border-color: #465e61;
    border-bottom-color: #465e61;
}
QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #355171, stop:1 #293f5c);
    color: #f5faff;
    border: 1px solid #496787;
    border-bottom: 2px solid #8ab9ff;
}
QTabBar::tab:disabled {
    background: #26302f;
    color: #6e8287;
    border-color: #26302f;
}
QTabBar::scroller {
    background: #202b29;
    border: none;
}
"""
