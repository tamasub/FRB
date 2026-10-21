"""Qt-free contract checks for the always-visible column search bar.

Windows native focus and Microsoft IME integration still need interactive QA.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

SOURCE = Path(__file__).resolve().parents[1] / 'src' / 'app.py'
CODE = SOURCE.read_text(encoding='utf-8')
TREE = ast.parse(CODE)
MENU = next(n for n in TREE.body if isinstance(n, ast.ClassDef)
            and n.name == 'CascadeMenu')


def source_of(name):
    node = next(n for n in MENU.body
                if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(CODE, node)


def executable(name, helpers=None):
    node = next(n for n in MENU.body
                if isinstance(n, ast.FunctionDef) and n.name == name)
    unit = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(unit)
    scope = dict(helpers or {})
    exec(compile(unit, str(SOURCE), 'exec'), scope)
    return scope[name]


def test_visible_editor_built_before_popup_size_and_display():
    popup = source_of('popup')
    assert popup.index('self._ensure_local_filter()') < popup.index('self.sizeHint()')
    assert popup.index('self._ensure_local_filter()') < popup.index('super().popup(target, at)')
    setup = source_of('_ensure_local_filter')
    assert 'QLineEdit(container)' in setup
    assert "setPlaceholderText('この列から探す…')" in setup
    assert 'setFixedHeight(2)' not in setup
    assert 'self.insertAction(before, action)' in setup
    assert 'self.order_enabled = False' not in setup


def test_initial_ime_halfwidth_and_never_forced_to_japanese():
    focus = source_of('_focus_initial_filter')
    # A visible editor does not have to own keyboard focus.  The popup starts
    # directly in the SAME mode the user previously reached by pressing Tab.
    assert 'self.setFocus(Qt.FocusReason.TabFocusReason)' in focus
    assert 'editor.setFocus' not in focus
    assert 'focus_target = self.scroll_tree if self.scroll_tree is not None else self' in focus
    assert 'initialize_halfwidth_english(int(focus_target.winId()))' in focus
    assert 'focus_target.hasFocus()' in focus
    assert 'editor.text()' in focus
    assert 'initialize_japanese_hiragana' not in CODE
    assert '_start_japanese_local_filter' not in CODE
    assert 'QTimer.singleShot(0, self._focus_initial_filter)' in source_of('showEvent')


def test_empty_query_restores_rows_without_deleting_visible_editor():
    source = source_of('_restore_local_rows')
    assert 'removeAction' not in source
    assert 'self.filter_edit = None' not in source
    assert 'self.order_enabled = self._order_enabled_before_filter' in source
    apply = source_of('_apply_local_filter')
    assert 'self._restore_local_rows()' in apply
    assert 'self.clear_local_filter()' not in apply


def test_scroll_tree_keeps_search_outside_item_list():
    src = source_of('_enable_scroll_tree')
    assert 'if action is not self.filter_action' in src
    assert 'filter_height' in src
    assert 'height - 22 - filter_height' in src


def test_no_hover_or_sort_change_until_actual_text():
    setup = source_of('_ensure_local_filter')
    assert "ancestor.open_mode = 'keyboard'" not in setup
    apply = source_of('_apply_local_filter')
    assert "ancestor.open_mode = 'keyboard'" in apply
    assert 'self.order_enabled = False' in apply


def test_empty_query_clear_keeps_the_bar_and_restores_ordering():
    action = object()
    other = SimpleNamespace(setVisible=Mock())
    counter = SimpleNamespace(setText=Mock())
    state = SimpleNamespace(scroll_tree=None, filter_action=action,
                            filter_count=counter, order_enabled=False,
                            _order_enabled_before_filter=True,
                            actions=lambda: [action, other], select_first=Mock())
    executable('_restore_local_rows')(state)
    other.setVisible.assert_called_once_with(True)
    counter.setText.assert_called_once_with('')
    assert state.order_enabled
    state.select_first.assert_called_once()


def test_initial_ime_callback_only_if_popup_still_owns_editor():
    class Timer:
        callbacks = []
        @classmethod
        def singleShot(cls, delay, callback):
            cls.callbacks.append((delay, callback))
    Timer.callbacks=[]
    qt = SimpleNamespace(FocusReason=SimpleNamespace(TabFocusReason=2))
    editor = SimpleNamespace(hasFocus=Mock(return_value=False),
                             text=Mock(return_value=''), winId=Mock(return_value=123))
    ime = Mock(return_value=True)
    menu = SimpleNamespace(filter_edit=editor, scroll_tree=None,
                           isVisible=Mock(return_value=True),
                           activateWindow=Mock(), setFocus=Mock(),
                           hasFocus=Mock(return_value=True),
                           winId=Mock(return_value=456),
                           _filter_ime_composing=False)
    focus = executable('_focus_initial_filter', dict(
        QTimer=Timer, Qt=qt, initialize_halfwidth_english=ime))
    focus(menu)
    menu.setFocus.assert_called_once_with(2)
    editor.hasFocus.assert_not_called()
    assert len(Timer.callbacks) == 1
    Timer.callbacks.pop()[1]()
    ime.assert_called_once_with(456)  # actual focused QMenu, not QLineEdit

    # User switched to Japanese or typed before delayed callback: do not
    # overwrite their choice with 'A'.
    editor.text.return_value = '日本語'
    focus(menu)
    Timer.callbacks.pop()[1]()
    assert ime.call_count == 1

    # If another control owns focus by then, do not reset its IME either.
    editor.text.return_value = ''
    menu.hasFocus.return_value = False
    focus(menu)
    Timer.callbacks.pop()[1]()
    assert ime.call_count == 1

    # Oversized menus use a scrollable item tree as the Tab destination.
    tree = SimpleNamespace(hasFocus=Mock(return_value=True),
                           winId=Mock(return_value=789))
    menu.scroll_tree = tree
    menu.hasFocus.return_value = False
    focus(menu)
    Timer.callbacks.pop()[1]()
    ime.assert_called_with(789)


def test_escape_and_ordinary_space_contracts():
    keys=source_of('keyPressEvent')
    assert "self.filter_edit.clear();event.accept();return" in keys
    assert "and self.filter_edit.text()" in keys
    assert '_start_japanese_local_filter' not in keys
    assert 'key in (Qt.Key.Key_Left, Qt.Key.Key_Escape)' in keys
    assert 'self.keyPressEvent(event)' in source_of('eventFilter')


def test_order_rebuild_reinstalls_always_visible_search_bar():
    launcher = next(n for n in TREE.body if isinstance(n, ast.ClassDef)
                    and n.name == 'Launcher')
    method = next(n for n in launcher.body if isinstance(n, ast.FunctionDef)
                  and n.name == 'persist_order')
    src = ast.get_source_segment(CODE, method)
    assert src.index('menu.clear_local_filter()') < src.index('self.fill_cascade(menu,context)')
    assert src.index('self.fill_cascade(menu,context)') < src.index('menu._ensure_local_filter()')
