"""Regressions for shared menu gutter, reversible JSON origins and WAN combo.

Headless contracts run without PySide6; optional Qt test runs on Windows.
These tests do not edit the user's JSON or physical folders.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from directory_entry_origin import within_entry, at_entry_boundary, next_entry_origin

APP = (ROOT / 'src/app.py').read_text('utf-8')
VIEW = (ROOT / 'src/expanded_view.py').read_text('utf-8')
LOOK = (ROOT / 'src/launch_appearance.py').read_text('utf-8')
COMBO = (ROOT / 'src/hybrid_combo_box.py').read_text('utf-8')


def _method(file, owner, method, symbols=None):
    source = (ROOT / 'src' / file).read_text('utf-8')
    mod = ast.parse(source)
    klass = next(x for x in mod.body if isinstance(x, ast.ClassDef) and x.name == owner)
    func = next(x for x in klass.body if isinstance(x, ast.FunctionDef) and x.name == method)
    body = ast.fix_missing_locations(ast.Module(body=[func], type_ignores=[]))
    env = dict(symbols or {})
    exec(compile(body, file, 'exec'), env)
    return env[method]


def test_context_menu_common_left_gutter_only():
    assert 'QMenu { padding:5px 5px 5px 9px; }' in LOOK
    assert 'QMenu::item { padding:7px 9px; }' in LOOK
    assert 'QMenu::separator { height:1px' in LOOK
    assert 'context_menu_spacing_qss(theme)' in (ROOT / 'src/context_menu_presentation.py').read_text('utf-8')
    assert 'def paintEvent(self, event):' not in APP[APP.index('class FRBContextMenu'):APP.index('class RemoteFolderCascade')]


def test_simple_editor_two_fields_share_one_stylesheet():
    begin = APP.index('    def launch_simple_edit_action(')
    end = APP.index('    def launch_unregister_action(', begin)
    section = APP[begin:end]
    assert "title_editor.setObjectName('launchSimpleTitle')" in section
    assert "description_editor.setObjectName('launchSimpleDescription')" in section
    assert 'title_editor.setStyleSheet(SIMPLE_EDIT_FIELD_QSS)' in section
    assert 'description_editor.setStyleSheet(SIMPLE_EDIT_FIELD_QSS)' in section
    assert 'QLineEdit#launchSimpleTitle, QPlainTextEdit#launchSimpleDescription {' in LOOK
    assert 'border:1px solid #b9cbc1; border-radius:7px;' in LOOK
    assert 'QPlainTextEdit' in section and "'description': description_editor.toPlainText()" in section


def test_physical_origin_only_when_started_in_json_folder():
    folder = {'source': 'launch_json', 'kind': 'folder', 'node_id': 'item:work:dev'}
    page = {'source': 'launch_json', 'kind': 'page', 'node_id': 'page:work'}
    anchor = next_entry_origin(None, folder, r'F:\FRB\dev')
    assert anchor == {'node': folder, 'entry_path': r'F:\FRB\dev'}
    assert next_entry_origin(None, page, r'F:\FRB\dev') is None
    assert within_entry(r'f:/frb/dev/inner', anchor['entry_path'])
    assert not within_entry(r'F:\FRB\development', anchor['entry_path'])
    assert not at_entry_boundary(r'F:\FRB\dev\inner', anchor['entry_path'])
    assert at_entry_boundary('f:/frb/dev/', anchor['entry_path'])
    assert next_entry_origin(anchor, None, r'F:\FRB\dev\inner') == anchor
    assert next_entry_origin(anchor, None, r'C:\Unrelated') is None


def test_restore_json_folder_only_at_physical_entry():
    method = _method('expanded_view.py', 'ExpandedLauncherView', 'restore_json_folder_origin',
                     {'virtual_lookup_node': lambda *args: {'node_id': 'item:work:zz'}})
    folder = {'source': 'launch_json', 'kind': 'folder', 'node_id': 'item:work:dev',
              'page_id': 'work', 'parent_item_id': 'zz'}
    origin = {'node': folder, 'entry_path': r'F:\FRB\dev'}
    restored = []
    view = NS(_filesystem_entry_origin=origin, _virtual_directory_node=None,
              launcher=NS(pages=[], authored_items=[], data={}),
              current_directory=lambda: r'F:\FRB\dev',
              show_virtual_launch_directory=lambda item: restored.append(item) or True)
    assert method(view) is True
    assert restored == [{'node_id': 'item:work:zz'}]
    view.current_directory = lambda: r'F:\FRB\dev\inner'
    assert method(view) is False
    assert restored == [{'node_id': 'item:work:zz'}]
    view._filesystem_entry_origin = None
    assert method(view) is False


def test_list_left_checks_json_entry_before_physical_shortcuts():
    method = _method('expanded_view.py', 'ExpandedLauncherView', 'navigate_left_from_middle',
                     {'matching_first_row': lambda *_: 0})
    marker = []
    first = object()
    tree = NS(topLevelItemCount=lambda: 1, topLevelItem=lambda _: first,
              currentItem=lambda: first)
    left_tree = NS(topLevelItemCount=lambda: 1, topLevelItem=lambda _: object())
    middle = NS(tree=tree)
    view = NS(middle=middle, left=NS(tree=left_tree),
              _virtual_directory_node=None,
              _filesystem_entry_origin={'entry_path': r'F:\FRB\dev'},
              row_data=lambda _: {'item_kind': 'directory'},
              launcher=NS(files_root_hidden_mode=False,
                          expander=lambda: NS(expand=lambda x: x),
                          remote_list_left_to_exp=lambda: marker.append('exp') or True),
              path=[{'item_id': 'dev'}],
              focus_panel=lambda panel: marker.append('focus'))
    assert method(view) == 'files_exp'
    assert marker == ['exp']


def test_list_handoff_restores_json_without_changing_general_nav_history():
    method = _method('app.py', 'Launcher', 'remote_list_left_to_exp')
    folder = {'source': 'launch_json', 'kind': 'folder', 'node_id': 'item:work:dev'}
    one = object()
    tree = NS(topLevelItemCount=lambda: 1, topLevelItem=lambda _: one,
              currentItem=lambda: one)
    restored = []
    view = NS(isVisible=lambda: True, _workspace_mode='files',
              middle=NS(tree=tree), row_data=lambda _: {'item_kind': 'directory'},
              _virtual_directory_node=None,
              _filesystem_entry_origin={'node': folder, 'entry_path': r'F:\FRB\dev'},
              current_directory=lambda: r'F:\FRB\dev')
    panel = NS(remote_select_mounted_directory=lambda n, root, path: restored.append(
        ('mount', n, root, path)) or True)
    launcher = NS(expanded_view=view, _current_remote_files_exp=lambda: panel,
                  remote_focus_area=lambda target: restored.append(target))
    assert method(launcher) is True
    assert restored == [('mount', folder, r'F:\FRB\dev', r'F:\FRB\dev'), 'files_exp']


def test_combo_wan_belongs_to_widget_and_preserves_dialog_buttons():
    assert 'class FRBHybridComboBox(QComboBox)' in COMBO
    assert 'def _hybrid_popup_wheel(self, event):' in COMBO
    assert 'can_follow_at_edge(' in COMBO
    assert 'QCursor.setPos(' in COMBO
    assert 'def eventFilter(self, obj, event):' in COMBO
    assert 'model.index(next_row, target.column(), target.parent())' in COMBO
    assert 'view.setCurrentIndex(target)' in COMBO
    assert 'icon_box = FRBHybridComboBox(dialog, launcher=self)' in APP
    assert 'chooser = FRBHybridComboBox(dialog, launcher=self)' in APP
    assert '= QComboBox(dialog)' not in APP
    assert 'self.run_launch_button_dialog(dialog, buttons, title_editor)' in APP
    assert "combo.view().isVisible()" in (ROOT / 'src/remote_confirmation.py').read_text('utf-8')


def test_wan_scroll_edge_helpers_are_shared_with_files_exp():
    from wheel_adaptive import wheel_steps, can_follow_at_edge
    assert wheel_steps(0, -120) == (0, 1)
    assert wheel_steps(0, 120) == (0, -1)
    assert can_follow_at_edge(10, 10, 0, 10, 1)
    assert not can_follow_at_edge(5, 5, 0, 10, 1)


def test_qt_popup_uses_native_commit_on_item_click(monkeypatch):
    import pytest
    pytest.importorskip('PySide6')
    from PySide6.QtWidgets import QApplication
    from hybrid_combo_box import FRBHybridComboBox
    app = QApplication.instance() or QApplication([])
    combo = FRBHybridComboBox()
    combo.addItems(['first', 'second', 'third'])
    combo.show()
    combo.showPopup()
    assert combo.view().isVisible()
    assert combo.count() == 3
    combo.hidePopup()
    combo.close()


def test_hybrid_combo_real_wheel_handler_flow_and_edge_without_qt():
    """Exercise production wheel method, not just its source-code names."""
    from wheel_adaptive import wheel_steps, can_follow_at_edge

    class Index:
        def __init__(self, row): self._row = row
        def isValid(self): return 0 <= self._row <= 5
        def row(self): return self._row
        def column(self): return 0
        def parent(self): return None
        def __eq__(self, other): return isinstance(other, Index) and self._row == other._row

    class Bar:
        current = 1
        def value(self): return self.current
        def minimum(self): return 0
        def maximum(self): return 3
        def singleStep(self): return 1
        def setValue(self, value): self.current = max(0, min(3, value))

    class Event:
        accepted = False
        def modifiers(self): return 0
        def angleDelta(self): return NS(y=lambda: -120)
        def pixelDelta(self): return NS(y=lambda: 0)
        def accept(self): self.accepted = True

    bar = Bar()
    selections, warped, callbacks = [], [], []
    cursor = NS(pos=lambda: (10, 10), setPos=lambda p: warped.append(p))
    viewport = NS(mapFromGlobal=lambda point: point,
                  mapToGlobal=lambda point: point,
                  rect=lambda: NS(contains=lambda _: True))
    model = NS(rowCount=lambda _: 6,
               index=lambda row, col, parent: Index(row))
    current = [Index(1)]
    view = NS(viewport=lambda: viewport,
              verticalScrollBar=lambda: bar,
              indexAt=lambda _: Index(2),
              currentIndex=lambda: current[0],
              model=lambda: model,
              setCurrentIndex=lambda i: (selections.append(i.row()), current.__setitem__(0, i)),
              scrollTo=lambda i: None,
              isVisible=lambda: True,
              visualRect=lambda _: NS(isValid=lambda: True, center=lambda: (12, 12)))
    widget = NS(view=lambda: view, _wan_remainder=0,
                _wan_edge_follow=False, _wan_hover_global=None,
                _wan_hover_queued=False,
                _flow_hover_selection=lambda: selections.append('hover'),
                _pointer_follow_enabled=lambda: True)
    handler = _method('hybrid_combo_box.py', 'FRBHybridComboBox', '_hybrid_popup_wheel', {
        'Qt': NS(KeyboardModifier=NS(NoModifier=0), MouseButton=NS(NoButton=0)),
        'QApplication': NS(mouseButtons=lambda: 0),
        'QCursor': cursor,
        'QTimer': NS(singleShot=lambda _, fn: callbacks.append(fn)),
        'wheel_steps': wheel_steps,
        'can_follow_at_edge': can_follow_at_edge,
    })
    event = Event()
    assert handler(widget, event) is True
    assert event.accepted
    assert bar.current == 2
    assert selections == []  # Native scrollbar first; no forced item click.
    callbacks.pop(0)()
    assert selections == ['hover']
    bar.current = 3  # At true lower scroll edge, next notch follows a row.
    assert handler(widget, Event()) is True
    assert selections[-1] == 3
    callbacks.pop(0)()
    assert warped == [(12, 12)]  # Pointer follows only at the edge.


def test_actual_directory_transition_remembers_json_origin_and_clears_elsewhere(monkeypatch):
    """Exercise the production navigation method, not just helper functions."""
    import os
    monkeypatch.setattr(os.path, 'isdir', lambda _: True)
    method = _method('expanded_view.py', 'ExpandedLauncherView', 'go_to_directory', {
        'normalized_directory': lambda p: p,
        'directory_row': lambda p: {'item_kind': 'directory', 'title': p,
                                    'launch_browse_target': p},
    })
    folder = {'source': 'launch_json', 'kind': 'folder', 'node_id': 'item:work:myfolder'}
    refreshed = []
    view = NS(_virtual_directory_node=folder, _filesystem_entry_origin=None,
              path=[], launcher=NS(remote_window=None),
              refresh_middle=lambda: refreshed.append(True),
              focus_panel=lambda pane: None, middle=object())
    assert method(view, r'F:\FRB\real', source_virtual=folder)
    assert view._virtual_directory_node is None
    assert view._filesystem_entry_origin['node'] is folder
    assert view._filesystem_entry_origin['entry_path'] == r'F:\FRB\real'
    assert method(view, r'F:\FRB\real\child')
    assert view._filesystem_entry_origin['node'] is folder
    assert method(view, r'G:\Unrelated')
    assert view._filesystem_entry_origin is None
    assert len(refreshed) == 3


def test_new_dialog_combo_construction_cannot_bypass_shared_wan_widget():
    module = ast.parse(APP)
    direct = [node.lineno for node in ast.walk(module) if isinstance(node, ast.Call)
              and isinstance(node.func, ast.Name) and node.func.id == 'QComboBox']
    assert direct == [], (
        'New Launch-owned dialog combos must use FRBHybridComboBox, not bare QComboBox: '
        + repr(direct))
