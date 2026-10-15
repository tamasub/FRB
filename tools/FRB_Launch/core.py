"""Launch data contract and expansion, independent of the GUI."""
import json
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

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
        if row['item_kind'] == 'selection' and not any(c.get('group_id') == row.get('launch_selection_group_id') for c in choices.values()):
            raise ValueError('選択候補がありません')
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
            if name not in self.values:
                raise ValueError(f'未定義の変数: %{name}%')
            value = str(self.values[name])
            if value.startswith('REPLACE_'):
                raise ValueError(f'設定値を入力してください: {name}')
            return value
        return re.sub(r'%%|%[^%\r\n]+%', replace, str(text))



def column_filter_match(row, query):
    """Match only one cascade column, never its ancestors' paths.

    Explorer rows carry their full path in `description`. Searching that
    would match every sibling whenever the parent directory name matches.
    """
    text = str(row.get('title', ''))
    if not row.get('_file'):
        text += ' ' + str(row.get('description', ''))
    content = text.casefold()
    return all(word in content for word in query.casefold().split())


def searchable_rows(data, query):
    items = {x['item_id']: x for x in data['items']}
    pages = {p['page_id']: p for p in data['pages']}
    words = query.casefold().split()
    result = []
    for row in data['items']:
        if not row.get('enabled', True) or not pages[row['page_id']].get('enabled', True):
            continue
        chain = []; p = row.get('parent_item_id'); hidden = False
        while p:
            parent = items[p]
            hidden |= not parent.get('enabled', True)
            chain.append(parent['title']); p = parent.get('parent_item_id')
        if hidden:
            continue
        path = ' / '.join([pages[row['page_id']]['title']] + list(reversed(chain)))
        content = json.dumps(row, ensure_ascii=False).casefold() + ' ' + path.casefold()
        if all(word in content for word in words):
            result.append((row, path))
    return sorted(result, key=lambda pair: pair[0].get('sort_order', 0))
