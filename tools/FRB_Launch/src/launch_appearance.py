"""FRB Launch visual palettes.

Only appearance belongs here.  Search, page navigation, and Launch DataJSON
stay unchanged.  Keep the original dark theme as the default.
"""


def normalize_theme(value):
    key = str(value).strip().lower()
    return key if key in THEME_REGISTRY else 'dark'



# Central theme catalog.  Display names, base family, and semantic colors live
# together so a new scheme can be registered without changing the gear menu or
# three-layer widget.  The original compact dark palette is intentionally kept.
THEME_REGISTRY = {
    'light': {
        'label': 'Light（ライト）', 'family': 'light',
        'window': '#edf5f0', 'header': '#dbe7df', 'subheader': '#f8fcfa',
        'panel': '#fcfffd', 'panel_border': '#bbd8c7', 'panel_header': '#eaf6ec',
        'column_header': '#f3faf5', 'workspace_strip': '#f3faf6',
        'text': '#233e32', 'muted_text': '#607a6d', 'hover': '#ecf7f1',
        'selection': '#d7ece1', 'stripe': '#e7f3ed',
        'focus_outline': '#8fc7ab', 'row_separator': '#eaf0eb',
        'root_button_border': '#bbd8c7',
        'history_bg': '#ffffff', 'history_border': '#acc9ba',
        'history_text': '#284338', 'history_selected': '#d6e7f8',
        'history_selected_text': '#1d3b4b', 'history_hover': '#e4eee8',
        'search_bg': '#ffffff', 'search_fg': '#2b433a',
        'search_border': '#8fb29f', 'search_focus': '#6e9f8b',
    },
    'dark': {
        'label': 'Dark（ダーク）', 'family': 'dark',
        'window': '#202b29', 'header': '#263532', 'subheader': '#263a35',
        'panel': '#222e2c', 'panel_border': '#4b6660', 'panel_header': '#344a42',
        'column_header': '#394d43', 'workspace_strip': '#2a3b35',
        'text': '#e6f0eb', 'muted_text': '#a2b9ae', 'hover': '#344d47',
        'selection': '#416457', 'stripe': '#32433e',
        'focus_outline': '#86bea7', 'row_separator': '#455851',
        'root_button_border': '#698779',
        'history_bg': '#223043', 'history_border': '#58718c',
        'history_text': '#e8f1fa', 'history_selected': '#365778',
        'history_selected_text': '#ffffff', 'history_hover': '#344b63',
        'search_bg': '#1a2422', 'search_fg': '#e8f2eb',
        'search_border': '#5d7b71', 'search_focus': '#88b4a1',
    },
}


def theme_palette(theme):
    """Shared semantic palette for header, compact view and three-layer UI."""
    return THEME_REGISTRY[normalize_theme(theme)]


def theme_family(theme):
    """Legacy QSS/icon family (light/dark), even for future named schemes."""
    return theme_palette(theme)['family']


def available_themes():
    """Ordered IDs for automatically populated theme menus."""
    return tuple(THEME_REGISTRY)




def bookmark_section_colors(theme):
    """Subtle bookmark section heading colors."""
    if theme_family(theme) == 'light':
        return {
            'background': '#f7faf8',
            'accent': '#c7ded0',
            'divider': '#edf2ee',
            'text': '#527062'
        }
    return {
        'background': '#30443a',
        'accent': '#729e87',
        'divider': '#405a4b',
        'text': '#d7e8dd'
    }



def history_popup_qss(theme, *, frame_name='historyPopup',
                      tree_name='historyChoices', height=31, padding=6):
    """Shared search-history / folder-favorites popup colors.

    The widget names and row geometry may differ, but the background and
    selection colors always come from the *same theme tokens*.
    """
    colors = theme_palette(theme)
    return (
        f'QFrame#{frame_name} {{background:{colors["history_bg"]};'
        f'border:1px solid {colors["history_border"]};border-radius:7px;}} '
        f'QTreeWidget#{tree_name} {{background:{colors["history_bg"]};'
        f'color:{colors["history_text"]};border:0;outline:0;}} '
        f'QTreeWidget#{tree_name}::item {{height:{height}px;padding:2px {padding}px;}} '
        f'QTreeWidget#{tree_name}::item:selected {{background:{colors["history_selected"]};'
        f'color:{colors["history_selected_text"]};}} '
        f'QTreeWidget#{tree_name}::item:hover {{background:{colors["history_hover"]};}}'
    )


def context_menu_spacing_qss(theme):
    """Keep quiet separators readable in both color schemes."""
    color = '#e1e5e2' if theme_family(theme) == 'light' else '#4b5b56'
    return CONTEXT_MENU_SPACING_QSS.replace('#e1e5e2', color)

# Based on the pastel green/white FRB Studio compact-light appearance.
LIGHT_MAIN_QSS = '''
QWidget { background:#edf5f0; color:#273d36; font-family:"Yu Gothic UI"; font-size:13px; }
QWidget#searchBar { background:transparent; border:0; }
QLineEdit { background:#ffffff; color:#263e35; border:1px solid #bdcfc5;
            border-radius:7px; padding:5px 10px; font-size:15px;
            selection-background-color:#c4ddf6; selection-color:#203d50; }
QLineEdit:focus { border-color:#72a99b; }
QPushButton#themeButton { background:#f8fcf9; color:#2b6257; border:1px solid #a7c8bb;
                          border-radius:6px; font-size:19px; font-weight:bold; padding:0; }
QPushButton#themeButton:hover { background:#deeee5; border-color:#53917e; }
QPushButton#themeButton:pressed { background:#cce4d8; }
QTreeWidget { border:0; outline:0; background:#f8fbf8; color:#253e35;
              alternate-background-color:#f1f7f3; }
QTreeWidget::item { height:35px; padding:0 6px; }
QTreeWidget::item:selected, QTreeWidget::item:selected:!active {
    background:#d6e7f8; color:#1d3b4b; }
QTreeWidget::item:hover:!selected { background:#e4eee8; }
/* The main grid's blue fills and full-row outline are drawn separately.
   History and cascade lists retain their existing styling. */
QTreeWidget#mainLaunchList::item:selected { background:transparent; color:#253e35; }
QTreeWidget#mainLaunchList::item:hover { background:transparent; }
QHeaderView::section { background:#e3eee7; color:#28463b; border:0;
    border-right:1px solid #cbdcd1; border-bottom:1px solid #cbdcd1; padding:3px 8px; }
QHeaderView::section:hover { background:#d2e7db; }
QLabel { color:#607a6d; font-size:11px; }
QPushButton { background:#f8fbf8; color:#235d4c; border:1px solid #bbd1c3;
              border-radius:5px; padding:4px 8px; }
QPushButton:hover { background:#e2f0e8; }
QMenu { background:#ffffff; color:#254138; border:1px solid #c2d4c7; padding:5px; }
QMenu::item { padding:8px 20px; }
QMenu::item:selected { background:#d6e7f8; color:#1d3b4b; }
QAbstractScrollArea::corner { background:#f8fbf8; border:0; }
'''

LIGHT_TABS_QSS = '''
QTabBar { background:transparent; border:none; outline:none; }
QTabBar::tab { background:#e0ebe4; color:#3f6255; border:1px solid #cadbd0;
    border-bottom:2px solid #cadbd0; border-radius:7px; margin-right:5px;
    padding:4px 15px; min-height:23px; }
QTabBar::tab:hover:!selected { background:#d3e8dc; color:#254f40;
    border-color:#a2c5b2; border-bottom-color:#a2c5b2; }
QTabBar::tab:selected { background:#d6e7f8; color:#1c4963;
    border:1px solid #a8c9e7; border-bottom:2px solid #6196c5; }
QTabBar::tab:disabled { background:#edf2ee; color:#9caea4; border-color:#e0e8e2; }
QTabBar::scroller { background:#edf5f0; border:none; }
'''

LIGHT_HISTORY_QSS = '''
QFrame#historyPopup { background:#ffffff; border:1px solid #acc9ba; border-radius:7px; }
QTreeWidget#historyChoices { background:#ffffff; color:#284338; border:0; outline:0; }
QTreeWidget#historyChoices::item { height:31px; padding:2px 6px; }
QTreeWidget#historyChoices::item:selected { background:#d6e7f8; color:#1d3b4b; }
QTreeWidget#historyChoices::item:hover { background:#e4eee8; }
'''

LIGHT_MENU_QSS = '''
QMenu { menu-scrollable:1; background:#ffffff; color:#284238;
        border:1px solid #b6cebe; padding:5px; }
QMenu::item { padding:8px 20px; }
QMenu::item:selected { background:#d6e7f8; color:#1d3b4b; }
QMenu::item:disabled { color:#8da69a; }
QMenu::separator { background:#dce8df; height:1px; margin:4px 6px; }
'''

LIGHT_CASCADE_TREE_QSS = '''
QTreeWidget#cascadeScrollView { background:#ffffff; color:#284238;
    border:0; outline:0; padding:0; font-family:'Yu Gothic UI'; font-size:13px; }
QTreeWidget#cascadeScrollView::item { height:32px; padding:0 6px; }
QTreeWidget#cascadeScrollView::item:selected,
QTreeWidget#cascadeScrollView::item:selected:!active { background:#d6e7f8; color:#1d3b4b; }
QTreeWidget#cascadeScrollView::item:hover { background:#e4eee8; }
'''

LIGHT_COLUMN_FILTER_QSS = '''
QWidget#columnFilterBar { background:#e8f2eb; border-radius:5px; }
QLineEdit { background:#ffffff; color:#284238; border:1px solid #accdbb;
            border-radius:5px; padding:5px 7px; font-size:13px; }
QLineEdit:focus { border-color:#74ae99; }
QLabel { background:transparent; color:#648071; font-size:11px; }
'''

FRAME_COLORS = {
    'dark': ('#6b756e', '#43524b', '#d0d7cf', '#27362e',
             '#202b29', '#abb5ab', '#101a17', '#f2f5f2'),
    'light': ('#dcebe2', '#c8ddd1', '#a4beaf', '#b3d0bf',
              '#edf5f0', '#9fbaa9', '#d0e0d6', '#244337'),
}


def light_scrollbar_qss(background='#ffffff'):
    """Keep the slim 8px compact scrollbar geometry across both themes."""
    return '''
    QScrollBar:vertical { background:%s; width:8px; margin:0; border:0; }
    QScrollBar:horizontal { background:%s; height:8px; margin:0; border:0; }
    QScrollBar::handle:vertical { background:#a5bfb0; min-height:28px; border-radius:2px; margin:0 2px; }
    QScrollBar::handle:horizontal { background:#a5bfb0; min-width:28px; border-radius:2px; margin:2px 0; }
    QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover { background:#76a593; }
    QScrollBar::handle:vertical:pressed, QScrollBar::handle:horizontal:pressed { background:#548a72; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; border:0; background:transparent; }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width:0; border:0; background:transparent; }
    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical,
    QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal { width:0; height:0; background:transparent; }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background:transparent; }
    ''' % (background, background)

def scrollbar_for_theme(theme, background):
    """Unified slim scrollbar for three-layer files, bookmarks and popups."""
    style = light_scrollbar_qss(background)
    if theme_family(theme) == 'light':
        return style
    return (style.replace('#a5bfb0', '#607c71')
                 .replace('#76a593', '#8db3a4')
                 .replace('#548a72', '#abcbbd'))


# Context menu row icons should sit near their labels, with just a small left inset.
CONTEXT_MENU_SPACING_QSS = """
QMenu::item { padding:7px 9px 7px 5px; }
QMenu::icon { margin-left:4px; margin-right:1px; }
QMenu::separator { height:1px; background:#e1e5e2; margin:5px 3px; }
"""
