"""Launch data contract and expansion, independent of the GUI."""
import json
import os
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from search_matching import matches_search_text, matches_choice_search

TYPES = {'SendKey', 'ClipboardCopy', 'Open', 'Run'}


def validate(data):
    def keyed(name, key):
        rows = data.get(name, [])
        if not isinstance(rows, list):
            raise ValueError(f'{name} must be an array')
        result = {}
        for row in rows:
            value = row.get(key)
            if not value or value in result:
                raise ValueError(f'{name}: missing/duplicate {key}: {value}')
            result[value] = row
        return result
    pages = keyed('pages', 'page_id')
    items = keyed('items', 'item_id')
    keyed('launch_variables', 'variable_id')
    choices = keyed('launch_choices', 'choice_id')
    if not any(p.get('enabled', True) for p in pages.values()):
        raise ValueError('有効なPageがありません')
    for row in items.values():
        if row.get('page_id') not in pages:
            raise ValueError(f"Page不明: {row['item_id']}")
        if row.get('item_kind') not in {'category', 'directory', 'command', 'selection'}:
            raise ValueError('項目種類が不正です')
        seen = {row['item_id']}
        parent = row.get('parent_item_id')
        while parent:
            if parent in seen or parent not in items:
                raise ValueError('親項目が不明、または階層が循環しています')
            seen.add(parent)
            p = items[parent]
            if p['item_kind'] != 'category' or p['page_id'] != row['page_id']:
                raise ValueError('親は同じPageのカテゴリーにしてください')
            parent = p.get('parent_item_id')
        if not isinstance(row.get('launch_actions', []), list):
            raise ValueError('launch_actionsは配列です')
        for step in row.get('launch_actions', []):
            if step.get('launch_action_type') not in TYPES:
                raise ValueError('未対応のLaunchアクションです')
            if not isinstance(step.get('launch_arguments', []), list):
                raise ValueError('引数は配列です')
            if step.get('launch_result_format', 'none') != 'none':
                raise ValueError('v0.1の処理結果変数は未対応です')
        # A selection group may temporarily have no candidates while the user
        # imports a replacement CSV and assigns group_id values later.
        # Keep the item valid; the selection screen already handles 0 rows.
    return data


def load(path):
    with open(path, encoding='utf-8-sig') as f:
        return validate(json.load(f))


def format_date(value, pattern):
    tokens = {'yyyy': f'{value.year:04}', 'MM': f'{value.month:02}', 'M': str(value.month), 'dd': f'{value.day:02}', 'd': str(value.day), 'HH': f'{value.hour:02}', 'H': str(value.hour), 'mm': f'{value.minute:02}', 'm': str(value.minute), 'ss': f'{value.second:02}', 's': str(value.second)}
    # Explicit token set; unsupported alphabetic format tokens fail clearly.
    pieces = re.findall(r'yyyy|MM|dd|HH|mm|ss|M|d|H|m|s|[^A-Za-z]+|[A-Za-z]', pattern)
    if any(p.isalpha() and p not in tokens for p in pieces):
        raise ValueError(f'未対応の日付書式: {pattern}')
    return ''.join(tokens.get(p, p) for p in pieces)


class Expander:
    def __init__(self, data, clipboard='', values=None, now=None):
        self.now = now or datetime.now(ZoneInfo(data.get('launch_timezone', 'Asia/Tokyo')))
        self.values = {'clipboard': clipboard, **(values or {})}
        for var in data.get('launch_variables', []):
            if not var.get('enabled', True):
                continue
            kind = var.get('launch_variable_type', 'literal')
            if kind == 'literal':
                self.values[var['variable_id']] = var.get('launch_value', '')
            elif kind == 'clipboard':
                self.values[var['variable_id']] = clipboard
            elif kind == 'date':
                self.values[var['variable_id']] = format_date(self.now + timedelta(days=var.get('launch_date_offset_days', 0)), var.get('launch_date_format', 'yyyy/MM/dd'))
    def expand(self, text):
        def replace(match):
            token = match.group(0)
            if token == '%%':
                return '%'
            name, _, fmt = token[1:-1].partition(':')
            if name in {'today', 'yesterday', 'now'}:
                value = self.now + timedelta(days=-1 if name == 'yesterday' else 0)
                return format_date(value, fmt or 'yyyy/MM/dd')
            # App-defined variables take precedence over Windows environment
            # variables.  Unlike os.path.expandvars(), unknown names must
            # retain the launcher's explicit error behavior.
            if name in self.values:
                value = self.values[name]
            else:
                # Windows environment names are case-insensitive. Keep that
                # behavior in tests and on other platforms as well.
                value = os.environ.get(name)
                if value is None:
                    value = next((v for k, v in os.environ.items()
                                  if k.casefold() == name.casefold()), None)
                if value is None:
                    raise ValueError(f'未定義の変数: %{name}%')
            value = str(value)
            if value.startswith('REPLACE_'):
                raise ValueError(f'設定値を入力してください: {name}')
            return value
        return re.sub(r'%%|%[^%\r\n]+%', replace, str(text))


# Escape sequences are opt-in for selection separators only.  Do not run this
# converter on contact values, launch action text, or other arbitrary data.
def decode_selection_separator(separator):
    r"""Decode \n, \r, \t, and \\ typed in a selection separator field.

    Unknown backslash escapes are kept verbatim. A doubled backslash is
    treated literally and cannot start another escape within the same pass.
    """
    chars = {'n': '\n', 'r': '\r', 't': '\t', '\\': '\\'}
    return re.sub(r'\\([nrt\\])', lambda m: chars[m.group(1)], str(separator))


def join_selection_values(row, choices):
    """Join selected values using the UI-configured separator semantics."""
    separator = decode_selection_separator(row.get('launch_selection_separator', '; '))
    field = row.get('launch_selection_value_field', 'value')
    return separator.join(str(choice.get(field, '')) for choice in choices)



def column_filter_match(row, query):
    """Match only one cascade column, never its ancestors' paths.

    Explorer rows carry their full path in `description`. Searching that
    would match every sibling whenever the parent directory name matches.
    """
    text = str(row.get('title', ''))
    if not row.get('_file'):
        text += ' ' + str(row.get('description', ''))
    content = text.casefold()
    return matches_search_text(content, query)


def searchable_rows(data, query, bookmark_browser=None):
    """Search all enabled pages, but only the selected browser's bookmarks.

    Browser-owned metadata (including the browser action/profile) is never
    searchable text.  The optional scope preserves existing non-GUI callers.
    """
    def visible_bookmark(row):
        return (not row.get('_browser_bookmark') or bookmark_browser is None or
                row.get('_bookmark_browser') == bookmark_browser)

    items = {x['item_id']: x for x in data['items']}
    pages = {p['page_id']: p for p in data['pages']}
    result = []
    for row in data['items']:
        if (not visible_bookmark(row) or not row.get('enabled', True)
                or not pages[row['page_id']].get('enabled', True)):
            continue
        chain = []; p = row.get('parent_item_id'); hidden = False
        while p:
            parent = items[p]
            # The virtual bookmark root ID is shared by Chrome and Edge;
            # its browser tag cannot determine the scope of mixed stale rows.
            hidden |= (not parent.get('enabled', True) or
                       (parent['item_id'] != '__browser_bookmarks_root' and
                        not visible_bookmark(parent)))
            chain.append(parent['title']); p = parent.get('parent_item_id')
        if hidden:
            continue
        path = ' / '.join([pages[row['page_id']]['title']] + list(reversed(chain)))
        if row.get('_browser_bookmark'):
            # Bookmark UI displays titles and hides URLs in a tooltip. Both
            # remain useful to search; internal action/metadata must not match.
            content = ' '.join((str(row.get('title', '')),
                                str(row.get('description', '')), path)).casefold()
        else:
            # Search the fields users can recognize, not serialized JSON.
            # Most rows contain keys such as `launch_actions` and
            # `launch_target`; searching JSON keys would make a query like
            # "launch" match nearly every installed app regardless of name.
            keywords = row.get('keywords', [])
            if isinstance(keywords, (list, tuple)):
                keywords = ' '.join(map(str, keywords))
            content = ' '.join(map(str, (
                row.get('title', ''), row.get('description', ''),
                keywords, path,
            ))).casefold()
        if matches_search_text(content, query):
            result.append((row, path))
    # Global search also finds individual choices of enabled selection items.
    # Keep the owning selection ID: a choice has no action of its own, and F12
    # must execute the original selection item's SendKey/ClipboardCopy action.
    for owner in data['items']:
        if owner.get('item_kind') != 'selection' or not owner.get('enabled', True):
            continue
        page = pages.get(owner.get('page_id'))
        if not page or not page.get('enabled', True):
            continue
        chain = []
        parent_id = owner.get('parent_item_id')
        hidden = False
        while parent_id:
            parent = items[parent_id]
            if not parent.get('enabled', True):
                hidden = True
                break
            chain.append(parent['title'])
            parent_id = parent.get('parent_item_id')
        if hidden:
            continue
        path = ' / '.join([page['title']] + list(reversed(chain)) + [owner['title']])
        for choice in data.get('launch_choices', []):
            if choice.get('group_id') != owner.get('launch_selection_group_id') or not choice.get('enabled', True):
                continue
            # Match the same searchable fields as the selection screen plus
            # the owning item's path, so names and addresses both work.
            if matches_choice_search(choice, query, path):
                result.append(({**choice,
                                'item_kind': 'choice',
                                'icon_key': owner.get('icon_key', 'mail'),
                                '_search_selection_owner': owner['item_id']}, path))
    return sorted(result, key=lambda pair: pair[0].get('sort_order', 0))
