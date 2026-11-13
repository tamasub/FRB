"""Global-search recipient selection returns to global search for unrelated terms.

These tests can run without PySide6 on the build/test host. They exercise the
real render-mode transition and safeguard the original recipient multi-select.
"""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from selection_scope import leave_global_choice_selection


CHOICES = [
    {'group_id': 'sales', 'title': '田中 一郎', 'description': 'tanaka@example.invalid', 'enabled': True},
    {'group_id': 'sales', 'title': '佐藤 次郎', 'description': 'sato@example.invalid', 'enabled': True},
    {'group_id': 'other', 'title': '山田 三郎', 'description': 'yamada@example.invalid', 'enabled': True},
]


def test_choice_picker_keeps_multiperson_search():
    assert not leave_global_choice_selection('田中', '田中', CHOICES[:2])
    assert not leave_global_choice_selection('佐藤', '田中', CHOICES[:2])
    assert not leave_global_choice_selection('sato@example.invalid', '田中', CHOICES[:2])


def test_unrelated_search_returns_global_and_blank_query_clears_mode():
    assert leave_global_choice_selection('.bat launch', '田中', CHOICES[:2])
    assert leave_global_choice_selection('data\\json', '田中', CHOICES[:2])
    assert leave_global_choice_selection('vscode', '田中', CHOICES[:2])
    assert leave_global_choice_selection('', '田中', CHOICES[:2])


def test_page_opened_picker_is_sticky_even_when_filter_has_no_hits():
    assert not leave_global_choice_selection('not-a-recipient', None, CHOICES[:2])
    assert not leave_global_choice_selection('', None, CHOICES[:2])


def _render_transition_from_actual_source():
    source = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    module = ast.parse(source)
    klass = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    render = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == 'render')
    # Render's initial statements handle selection-mode transition, followed by
    # Qt painting. Execute just those real statements to test without PySide6.
    assert isinstance(render.body[0], ast.If)
    assert isinstance(render.body[1], ast.Assign)
    assert isinstance(render.body[2], ast.If)
    render_copy = ast.FunctionDef(name='transition', args=render.args,
                                  body=render.body[:3], decorator_list=[],
                                  returns=None, type_comment=None)
    globals_ = {'leave_global_choice_selection': leave_global_choice_selection}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[render_copy], type_ignores=[])),
                 str(ROOT / 'src/app.py'), 'exec'), globals_)
    return globals_['transition']


def test_real_render_transition_clears_buttons_and_search_scope_without_losing_query():
    transition = _render_transition_from_actual_source()
    widget = SimpleNamespace(
        data={'launch_choices': CHOICES},
        selection={'launch_selection_group_id': 'sales'},
        checked={'tanaka'},
        _global_selection_query='田中',
        search=SimpleNamespace(text=lambda: '.bat launch'),
    )
    transition(widget)
    assert widget.selection is None
    assert widget.checked == set()
    assert widget._global_selection_query is None
    assert widget.search.text() == '.bat launch'  # Do not erase the new search!


def test_real_render_transition_keeps_other_recipient_search_and_direct_picker():
    transition = _render_transition_from_actual_source()
    for initial, term in [('田中', '佐藤'), (None, '.bat launch')]:
        widget = SimpleNamespace(
            data={'launch_choices': CHOICES},
            selection={'launch_selection_group_id': 'sales'},
            checked={'tanaka'},
            _global_selection_query=initial,
            search=SimpleNamespace(text=lambda term=term: term),
        )
        transition(widget)
        assert widget.selection is not None
        assert widget.checked == {'tanaka'}


def test_enter_global_choice_and_nav_restore_track_origin():
    source = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    launcher = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    methods = {n.name: ast.get_source_segment(source, n) for n in launcher.body if isinstance(n, ast.FunctionDef)}
    assert 'self._global_selection_query = self.search.text().strip()' in methods['activate']
    assert 'self._global_selection_query=None' in methods['activate']
    assert 'global_selection_query=(self._global_selection_query if self.selection else None)' in methods['_nav_state']
    assert "self._global_selection_query = state.get('global_selection_query')" in methods['_nav_restore']
    assert 'self.selection_tools.setVisible(self.selection is not None)' in methods['render']
    # Debounced rendering remains in place; no extra SQLite work per keypress.
    assert 'self._live_search_timer.start(235 if japanese else 135)' in methods['search_text_changed']
