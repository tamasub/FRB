"""Regression: volatile history must never create files or slow typing."""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from session_search_history import SessionSearchHistory, SESSION_HISTORY


def test_session_history_is_memory_only_and_deduplicates_saved_queries(tmp_path):
    history = SessionSearchHistory(limit=3)
    assert history.remember('日本語 入力', ['Windows'])
    assert not history.remember('日本語 入力')
    assert not history.remember('WINDOWS', ['Windows'])
    assert history.remember('file')
    assert history.remember('web')
    assert history.remember('new')
    assert history.keywords == ['file', 'web', 'new']
    assert history.remove('WEB')
    assert history.keywords == ['file', 'new']
    assert not history.remove('missing')
    assert not list(tmp_path.iterdir())
    assert SessionSearchHistory().keywords == []  # fresh process, no persisted state


def test_preserved_order_and_no_autosorting():
    history = SessionSearchHistory()
    for name in ('first', 'second', 'third'):
        history.remember(name)
    assert not history.remember('FIRST')
    assert history.keywords == ['first', 'second', 'third']


def test_lifecycle_and_ime_scheduling_wiring():
    source = (ROOT / 'src/app.py').read_text('utf-8')
    tree = ast.parse(source)
    launcher = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    methods = {n.name: ast.get_source_segment(source, n) for n in launcher.body if isinstance(n, ast.FunctionDef)}
    init = methods['__init__']
    assert 'self.session_history = SessionSearchHistory()' in init
    assert 'self.search.textEdited.connect(self.search_user_edited)' in init
    assert 'self._live_search_timer.setSingleShot(True)' in init
    assert 'self._session_history_timer.setSingleShot(True)' in init
    assert '.timeout.connect(self.record_session_search)' in init
    assert 'self._live_search_timer.start(235 if japanese else 135)' in methods['search_text_changed']
    assert 'self._session_history_timer.stop()' in methods['search_text_changed']
    assert 'self._live_search_timer.stop()' in methods['search_text_changed']
    assert 'self.search_history.remember' not in methods['search_text_changed']
    assert '.remember(text, self.search_history.keywords)' in methods['record_session_search']
    assert "if getattr(self, 'composing', False):" in methods['record_session_search']
    assert 'self.session_history.remove(text)' in methods['remember_search']
    assert 'self.session_history.remember(previous, self.search_history.keywords)' in methods['search_text_changed']
    assert 'self.session_history_expanded = bool(expanded)' in methods['set_all_history_categories']
    assert "if self.session_history.has(value):" in methods['history_structure_changed']
    assert 'self.record_session_search()' in methods['activate']
    assert "STATE / 'search_history.json'" in init
    assert "STATE / 'search_history_categories.json'" in init
    assert 'self.session_history' not in methods['quit'] # process scope, no JSON to save


def test_drag_cannot_move_persistent_entry_to_volatile_group():
    source = (ROOT / 'src/history_category_tree.py').read_text('utf-8')
    assert "if destination == 'session_history':" in source
    assert "('session_history', 'uncategorized')" in source
    assert "value in ('uncategorized', 'session_history')" in source


def _qt_free_app_method(name):
    """Execute only selected methods of app.py without importing PySide6."""
    source = (ROOT / 'src/app.py').read_text('utf-8')
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    program = ast.Module(body=[method], type_ignores=[])
    module = __import__('types').SimpleNamespace(exception=lambda *a, **kw: None,
                                                  info=lambda *a, **kw: None)
    env = {'normalize_keyword': __import__('search_history').normalize_keyword,
           'SESSION_HISTORY': SESSION_HISTORY, 'DIAG': module}
    exec(compile(ast.fix_missing_locations(program), str(ROOT / 'src/app.py'), 'exec'), env)
    return env[name]


def test_actual_session_capture_and_promotion_to_saved_category(tmp_path):
    from types import SimpleNamespace
    from search_history import SearchHistory
    from search_history_categories import SearchHistoryCategories
    saved = SearchHistory(tmp_path / 'search_history.json')
    folders = SearchHistoryCategories(tmp_path / 'search_history_categories.json', [])
    volatile = SessionSearchHistory()
    launcher = SimpleNamespace(
        composing=False,
        search=SimpleNamespace(text=lambda: '田中 一郎'),
        search_history=saved,
        search_categories=folders,
        session_history=volatile,
        _session_edit_draft=None,
        populate_history_popup=lambda *a: None,
    )
    _qt_free_app_method('record_session_search')(launcher)
    assert volatile.keywords == ['田中 一郎']
    assert not saved.path.exists() and not folders.path.exists()
    # Moving the candidate to Windows is the first persistence point.
    _qt_free_app_method('history_structure_changed')(
        launcher, 'keyword', '田中 一郎', 'windows', 0)
    assert volatile.keywords == []
    assert saved.keywords == ['田中 一郎']
    assert folders.group_items('windows') == ['田中 一郎']
    assert '田中 一郎' in saved.path.read_text('utf-8')
    assert folders.path.exists()
    # A new process sees only promoted entries.
    assert SessionSearchHistory().keywords == []
    assert SearchHistory(saved.path).keywords == ['田中 一郎']


def test_ime_preedit_never_enters_volatile_history(tmp_path):
    from types import SimpleNamespace
    from search_history import SearchHistory
    session = SessionSearchHistory()
    launcher = SimpleNamespace(composing=True,
                               search=SimpleNamespace(text=lambda: 'にほん'),
                               session_history=session,
                               search_history=SearchHistory(tmp_path / 'saved.json'),
                               _session_edit_draft=None)
    _qt_free_app_method('record_session_search')(launcher)
    assert session.keywords == []
    assert not list(tmp_path.iterdir())


def test_promotion_to_unclassified_clears_volatile_even_if_move_is_noop(tmp_path):
    from types import SimpleNamespace
    from search_history import SearchHistory
    from search_history_categories import SearchHistoryCategories
    saved = SearchHistory(tmp_path / 'history.json')
    cats = SearchHistoryCategories(tmp_path / 'categories.json', [])
    volatile = SessionSearchHistory()
    volatile.remember('一時候補')
    launcher = SimpleNamespace(search_history=saved, search_categories=cats,
                               session_history=volatile, _session_edit_draft='一時候補',
                               populate_history_popup=lambda *args: None)
    _qt_free_app_method('history_structure_changed')(
        launcher, 'keyword', '一時候補', 'uncategorized', 0)
    assert volatile.keywords == []
    assert saved.keywords == ['一時候補']
    assert cats.group_items('uncategorized') == ['一時候補']
