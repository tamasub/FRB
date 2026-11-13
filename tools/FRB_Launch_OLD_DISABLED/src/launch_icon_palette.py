"""One-to-one visual meaning for Studio's ``launch.icon_key`` vocabulary.

Studio presents these marks beside the enum labels.  Launch must render the
same marks for authored icons, instead of converting them to letters such as
``archive -> Z``.  Folder colours are rendered by the same native vector drawing path for
all nine Studio colour choices. Historical blue category/yellow folder keys
retain their original colours.

This module intentionally has no Qt dependency; it is also used by tests.
"""

STUDIO_EMOJI_ICONS = {
    'file': '📄',
    'command': '▶️',
    'calendar': '📅',
    'mail': '✉️',
    'wifi': '📶',
    'volume': '🔊',
    'archive': '🗜️',
    'globe': '🌐',
    'settings': '⚙️',
    'message': '💬',
    'app': '🖥️',
}

# Explicit palette: the value stored by Studio is the colour Launch draws.
# Keep the two historical values unchanged to preserve existing preferences.
FOLDER_COLORS = {
    'yellow': '#e9bb61',
    'blue': '#599de5',
    'green': '#57ad82',
    'red': '#e47575',
    'purple': '#a388df',
    'orange': '#e99a5f',
    'cyan': '#57baca',
    'pink': '#e78cbe',
    'gray': '#9aa3ad',
}

FOLDER_ICON_COLORS = {
    **{f'folder.{name}': hex_color for name, hex_color in FOLDER_COLORS.items()},
    # Category aliases share the same folder silhouettes, while the existing
    # category.blue remains the original blue used in users' saved JSON.
    **{f'category.{name}': hex_color for name, hex_color in FOLDER_COLORS.items()
       if name != 'blue'},
    'category.blue': '#6ba7ff',
    'category': '#6ba7ff',
    'folder': '#e9bb61',
}


def studio_icon_emoji(icon_key):
    return STUDIO_EMOJI_ICONS.get(str(icon_key or ''))


def folder_icon_color(icon_key):
    key = str(icon_key or '').strip()
    if key in FOLDER_ICON_COLORS:
        return FOLDER_ICON_COLORS[key]
    # Unknown legacy category/folder variants retain their old defaults.
    # Only explicitly supported colours are interpreted as a new colour.
    if key.startswith('category.'):
        return FOLDER_ICON_COLORS['category.blue']
    if key.startswith('folder.'):
        return FOLDER_ICON_COLORS['folder.yellow']
    return None
