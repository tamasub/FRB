"""Regression for local-only history search and main search IME focus.

Tests intentionally run without PySide6 on CI; the real native IME focus and
widget painting still require an actual Windows GUI smoke test.
"""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from history_popup_filter import matches_history_filter


def _method(name):
    source = (ROOT / 'src/app.py').read_text('utf-8')
    tree = ast.parse(source)
    launcher = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    method = next(n for n in launcher.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(source, method)


def test_unicode_width_casefold_and_multiple_fragments():
    assert matches_history_filter('ＶＳＣＯＤＥを起動', 'vscode')
    assert matches_history_filter('Zenn_Blog_All_merged.md', 'zenn md')
    assert matches_history_filter('(田中 一郎) or (佐藤 次郎)', '佐藤 次郎')
    assert not matches_history_filter('Zenn_Blog_All_merged.md', 'zenn python')
    assert matches_history_filter('anything', '  ')
    assert matches_history_filter('日本語', '日本')


class Row:
    def __init__(self, text, identifier=None, children=()):
        self.value = text
        self.identifier = identifier
        self.children = list(children)
        self.hidden = False
        self.expanded = False

    def data(self, col, role):
        return self.identifier

    def text(self, col):
        return self.value

    def setText(self, col, value):
        self.value = value

    def setHidden(self, value):
        self.hidden = value

    def isHidden(self):
        return self.hidden

    def setExpanded(self, value):
        self.expanded = bool(value)

    def isExpanded(self):
        return self.expanded

    def childCount(self):
        return len(self.children)

    def child(self, idx):
        return self.children[idx]


class Tree:
    def __init__(self, items):
        self.items = items
        self.signals = []
        self.drag = True
        self.drop = True
        self.selected = None
        self.scrolled = None

    def blockSignals(self, value):
        self.signals.append(value)

    def topLevelItemCount(self):
        return len(self.items)

    def topLevelItem(self, idx):
        return self.items[idx]

    def setCurrentItem(self, row):
        self.selected = row

    def scrollToItem(self, row, _hint):
        self.scrolled = row

    def setDragEnabled(self, value):
        self.drag = value

    def setAcceptDrops(self, value):
        self.drop = value

    def viewport(self):
        return self


def test_filter_show_collapsed_matches_restore_and_no_persistence():
    source = _method('filter_history_popup')
    method = ast.parse(source).body[0]
    env = {
        'SESSION_HISTORY': 'session_history',
        'UNCATEGORIZED': 'uncategorized',
        'ROLE_ID': 42,
        'matches_history_filter': matches_history_filter,
        'QAbstractItemView': SimpleNamespace(ScrollHint=SimpleNamespace(EnsureVisible=1)),
    }
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), 'app_method.py', 'exec'), env)
    action = env['filter_history_popup']
    temporary = Row('一時履歴', 'session_history', [Row('data json')])
    windows = Row('Windows', 'windows', [Row('コントロールパネル'), Row('環境変数')])
    dev = Row('開発', 'dev', [Row('vscode'), Row('Zenn .md blog')])
    dev.expanded = True
    tree = Tree([temporary, windows, dev])
    filter_input = SimpleNamespace(text=lambda: user_query[0])
    user_query = ['zenn']
    groups = SimpleNamespace(
        get=lambda key: {'name': 'Windows'} if key == 'windows' else {'name': '開発'} if key == 'dev' else None,
        expanded=lambda key: key == 'dev',
    )
    calls = []
    launcher = SimpleNamespace(history_choices=tree, history_filter=filter_input,
                               search_categories=groups, session_history_expanded=True,
                               history_popup=SimpleNamespace(isVisible=lambda: True),
                               position_history_popup=lambda: calls.append('resize'))
    action(launcher)
    assert tree.selected.text(0) == 'Zenn .md blog'
    assert temporary.hidden and windows.hidden and not dev.hidden
    assert dev.expanded and dev.children[0].hidden and not dev.children[1].hidden
    assert not tree.drag and not tree.drop
    assert tree.signals == [True, False]
    user_query[0] = 'windows'
    action(launcher)
    assert not windows.hidden and windows.expanded
    assert all(not row.hidden for row in windows.children)
    assert dev.hidden
    # Clearing is a *view-only* operation: stored open/closed positions survive.
    user_query[0] = ''
    action(launcher)
    assert not any(folder.hidden for folder in tree.items)
    assert temporary.expanded and not windows.expanded and dev.expanded
    assert all(not row.hidden for folder in tree.items for row in folder.children)
    assert tree.drag and tree.drop
    assert len(calls) == 3


def test_focus_filter_ui_wiring_and_no_main_search_mutation():
    app = (ROOT / 'src/app.py').read_text('utf-8')
    assert "self.history_filter = QLineEdit(self.history_popup)" in app
    assert "self.history_filter.textChanged.connect(self.filter_history_popup)" in app
    assert "self.history_filter.installEventFilter(self)" in app
    assert 'self.search.setFocus(Qt.FocusReason.ShortcutFocusReason)' in _method('show_history_popup')
    assert 'self.history_choices.setFocus(' not in _method('show_history_popup')
    assert 'self.history_filter.clear()' in _method('hide_history_popup')
    assert "if local_filter_input and self.history_popup.isVisible():" in _method('handle_history_event')
    assert 'self.search.setText(' not in _method('filter_history_popup')
    assert 'self.render(' not in _method('filter_history_popup')
    assert 'self.search_history.remember' not in _method('filter_history_popup')
    assert 'self.search_categories.set_expanded' not in _method('filter_history_popup')
    assert "if folder.isHidden():" in _method('history_visible_rows')
