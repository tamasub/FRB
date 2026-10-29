"""Regression: clicking a choice matched by its parent SE部 must not blank the list.

No PySide6 required for the pure policy and real activate() branch tests.
The optional GUI check exercises the checkbox-selection signal when PySide6 is available.
"""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from core import load, searchable_rows
from search_matching import matches_choice_search
from selection_scope import (filtered_selection_choices,
                             global_choice_ids_in_results,
                             leave_global_choice_selection)

DATA = load(ROOT / 'config' / 'frb_launch_sample_data_v0_1.json')
SE = [choice for choice in DATA['launch_choices']
      if choice['group_id'] == 'se' and choice.get('enabled', True)]
OWNER = next(item for item in DATA['items'] if item.get('launch_selection_group_id') == 'se')


def _se_global_hits(query):
    return [row for row, path in searchable_rows(DATA, query)
            if row.get('_search_selection_owner') == OWNER['item_id']]


def test_se_folder_search_matches_four_but_recipient_only_matches_none():
    hits = _se_global_hits('se部')
    assert [row['title'] for row in hits] == ['se001', 'se002', 'se003', 'se004']
    # Original failure: once in selection mode, this matcher returned no rows.
    assert not [choice for choice in SE if matches_choice_search(choice, 'se部')]


def test_initial_mouse_choice_selection_preserves_global_visible_hits():
    hits = _se_global_hits('se部')
    ids = global_choice_ids_in_results(hits, OWNER['item_id'])
    assert len(ids) == 4
    assert [choice['title'] for choice in filtered_selection_choices(SE, 'se部', 'se部', ids)] == [
        'se001', 'se002', 'se003', 'se004']
    assert not leave_global_choice_selection('se部', 'se部', SE)
    # Clicking a choice must not uncheck the selected item in the new view.
    selected_id = hits[1]['choice_id']
    assert selected_id in ids


def test_group_path_and_person_and_query_maintain_exact_global_match():
    hits = _se_global_hits('SE部 se003')
    ids = global_choice_ids_in_results(hits, OWNER['item_id'])
    assert len(ids) == 1
    assert [c['title'] for c in filtered_selection_choices(SE, 'SE部 se003', 'SE部 se003', ids)] == ['se003']


def test_followup_person_search_filters_normally_and_unrelated_exits():
    ids = global_choice_ids_in_results(_se_global_hits('se部'), OWNER['item_id'])
    assert [c['title'] for c in filtered_selection_choices(SE, 'se002', 'se部', ids)] == ['se002']
    assert not leave_global_choice_selection('se002', 'se部', SE)
    assert leave_global_choice_selection('.bat launch', 'se部', SE)
    assert filtered_selection_choices(SE, 'se部', None, None) == []  # Page picker unchanged


def test_group_snapshot_ignores_other_owner():
    rows = _se_global_hits('se部') + [
        {'choice_id': 'unrelated', '_search_selection_owner': 'another'}]
    assert 'unrelated' not in global_choice_ids_in_results(rows, OWNER['item_id'])


def _real_activate():
    source = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    module = ast.parse(source)
    launcher = next(x for x in module.body if isinstance(x, ast.ClassDef) and x.name == 'Launcher')
    func = next(x for x in launcher.body if isinstance(x, ast.FunctionDef) and x.name == 'activate')
    # Execute the actual activate() code without importing Qt for its early-return selection branch.
    real = ast.FunctionDef(name='activate_from_global', args=func.args, body=func.body,
                           decorator_list=[], returns=None, type_comment=None)
    class FakeQt:
        class ItemDataRole:
            UserRole = 0
    globals_ = {'Qt': FakeQt, 'global_choice_ids_in_results': global_choice_ids_in_results}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[real], type_ignores=[])),
                 str(ROOT / 'src/app.py'), 'exec'), globals_)
    return globals_['activate_from_global']


def test_real_activate_snapshots_choices_before_rendering_picker():
    hits = _se_global_hits('se部')
    class FakeItem:
        def __init__(self, row): self.row = row
        def data(self, *_): return self.row
    class FakeList:
        def __init__(self, rows): self.items = [FakeItem(row) for row in rows]
        def topLevelItemCount(self): return len(self.items)
        def topLevelItem(self, index): return self.items[index]
        def setFocus(self): pass
    renders = []
    obj = SimpleNamespace(
        selection=None, checked=set(), _global_selection_query=None,
        _global_selection_choice_ids=None,
        search=SimpleNamespace(text=lambda: 'se部'),
        data=DATA, list=FakeList(hits),
        record_session_search=lambda: None,
        _nav_before_change=lambda: None,
        _nav_after_change=lambda: None,
        render=lambda: renders.append('render'),
        _session_edit_draft=None,
    )
    _real_activate()(obj, hits[1])  # Simulate a click on se002
    assert obj.selection is OWNER
    assert obj.checked == {hits[1]['choice_id']}
    assert obj._global_selection_query == 'se部'
    assert obj._global_selection_choice_ids == {r['choice_id'] for r in hits}
    assert renders == ['render']


def test_actual_render_selection_calls_group_aware_filter():
    source = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    klass = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'Launcher')
    funcs = {x.name: ast.get_source_segment(source, x) for x in klass.body
             if isinstance(x, ast.FunctionDef)}
    assert 'filtered_selection_choices(' in funcs['render']
    assert 'self._global_selection_choice_ids' in funcs['render']
    assert "global_selection_choice_ids=(self._global_selection_choice_ids if self.selection else None)" in funcs['_nav_state']
    assert "self._global_selection_choice_ids = state.get('global_selection_choice_ids')" in funcs['_nav_restore']

try:
    import os
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    import app as app_module
except ImportError:
    app_module = None


if app_module is not None:
    def test_qt_click_checkbox_keeps_se_group_visible(tmp_path, monkeypatch):
        """A real itemChanged event (mouse checkbox path) must keep recipients."""
        monkeypatch.setattr(app_module, 'STATE', tmp_path)
        monkeypatch.setattr(app_module.windows, 'hotkey', lambda *args: None)
        monkeypatch.setattr(app_module.windows, 'unhotkey', lambda *args: None)
        qtapp = QApplication.instance() or QApplication([])
        qtapp.setQuitOnLastWindowClosed(False)
        launcher = app_module.Launcher()
        try:
            launcher.show()
            launcher.search.setText('se部')
            qtapp.processEvents()
            visible = [launcher.list.topLevelItem(i) for i in range(launcher.list.topLevelItemCount())]
            candidates = [item for item in visible
                          if item.data(0, Qt.ItemDataRole.UserRole).get('_search_selection_owner') == OWNER['item_id']]
            assert len(candidates) == 4
            clicked = candidates[1]
            choice_id = clicked.data(0, Qt.ItemDataRole.UserRole)['choice_id']
            clicked.setCheckState(0, Qt.CheckState.Checked)  # Emits the mouse click's itemChanged path.
            qtapp.processEvents()
            assert launcher.selection is not None
            assert launcher.checked == {choice_id}
            assert launcher.list.topLevelItemCount() == 4
            assert launcher.selection_tools.isVisible() == launcher.isVisible()
            launcher.search.setText('se003')
            qtapp.processEvents()
            assert launcher.list.topLevelItemCount() == 1
            assert launcher.checked == {choice_id}
            launcher.search.setText('.bat launch')
            qtapp.processEvents()
            assert launcher.selection is None
            assert not launcher.selection_tools.isVisible()
            assert launcher.search.text() == '.bat launch'
        finally:
            launcher.dismiss()
            launcher.tray.hide()
            launcher.deleteLater()
            qtapp.processEvents()
