"""Regression: a click on Remote must not close search history before ENTER.

Qt/PySide6 is not installed in this test environment, so exercise the real
Launcher event-filter/command methods with tiny widget doubles.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
REMOTE_SOURCE = (ROOT / 'src' / 'launch_remote.py').read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)


def extract(class_name, method_name, env):
    cls = next(node for node in TREE.body
               if isinstance(node, ast.ClassDef) and node.name == class_name)
    method = next(node for node in cls.body
                  if isinstance(node, ast.FunctionDef) and node.name == method_name)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 'app.py', 'exec'), env)
    return env[method_name]


class QObject:
    def __init__(self, parent=None):
        self._parent = parent

    def parent(self):
        return self._parent


class QWidget(QObject):
    def isAncestorOf(self, widget):
        obj = widget.parent()
        while obj is not None:
            if obj is self:
                return True
            obj = obj.parent()
        return False


class VisibleWidget(QWidget):
    def __init__(self, parent=None, visible=True):
        super().__init__(parent)
        self.visible = visible

    def isVisible(self):
        return self.visible


QEvent = SimpleNamespace(Type=SimpleNamespace(MouseButtonPress=42))
CLICK = SimpleNamespace(type=lambda: QEvent.Type.MouseButtonPress)


def test_remote_wheel_and_button_click_do_not_close_history_popup():
    filtering = extract('HistoryOutsideClickFilter', 'eventFilter',
                        {'QEvent': QEvent, 'QWidget': QWidget, 'QObject': QObject})
    launcher = VisibleWidget()
    launcher.history_popup = VisibleWidget(launcher)
    launcher.search = VisibleWidget(launcher)
    launcher.remote_window = VisibleWidget(launcher)
    launcher.hide_history_popup = Mock()
    filt = SimpleNamespace(launcher=launcher)
    for widget in (launcher.remote_window, VisibleWidget(launcher.remote_window),
                   VisibleWidget(VisibleWidget(launcher.remote_window))):
        assert filtering(filt, widget, CLICK) is False
    launcher.hide_history_popup.assert_not_called()


def test_true_outside_click_still_closes_history():
    filtering = extract('HistoryOutsideClickFilter', 'eventFilter',
                        {'QEvent': QEvent, 'QWidget': QWidget, 'QObject': QObject})
    launcher = VisibleWidget()
    launcher.history_popup = VisibleWidget(launcher)
    launcher.search = VisibleWidget(launcher)
    launcher.remote_window = VisibleWidget(launcher)
    launcher.hide_history_popup = Mock()
    filt = SimpleNamespace(launcher=launcher)
    assert filtering(filt, VisibleWidget(launcher.history_popup), CLICK) is False
    assert filtering(filt, VisibleWidget(launcher.search), CLICK) is False
    launcher.hide_history_popup.assert_not_called()
    assert filtering(filt, VisibleWidget(launcher), CLICK) is False
    launcher.hide_history_popup.assert_called_once_with()


def test_hidden_remote_no_longer_exempts_outside_click():
    filtering = extract('HistoryOutsideClickFilter', 'eventFilter',
                        {'QEvent': QEvent, 'QWidget': QWidget, 'QObject': QObject})
    launcher = VisibleWidget()
    launcher.history_popup = VisibleWidget(launcher)
    launcher.search = VisibleWidget(launcher)
    launcher.remote_window = VisibleWidget(launcher, visible=False)
    launcher.hide_history_popup = Mock()
    filtering(SimpleNamespace(launcher=launcher), VisibleWidget(launcher.remote_window), CLICK)
    launcher.hide_history_popup.assert_called_once_with()


def test_remote_enter_uses_existing_keyword_activation_after_safe_click():
    """Actual command -> row_clicked -> select_history_keyword, not key injection."""
    names = {}
    env = {
        'ROLE_KIND': 10,
        'Qt': SimpleNamespace(FocusReason=SimpleNamespace(ShortcutFocusReason=1)),
        'DIAG': SimpleNamespace(info=Mock()),
    }
    for name in ('remote_history_command', 'history_row_clicked', 'select_history_keyword'):
        names[name] = extract('Launcher', name, env)

    class HistoryRow:
        def data(self, column, role):
            return 'keyword'
        def text(self, column):
            return 'zenn .md merge'

    row = HistoryRow()
    choice_tree = SimpleNamespace(currentItem=lambda: row, setCurrentItem=Mock())
    keyword_store = SimpleNamespace(keywords=['zenn .md merge'])
    record = SimpleNamespace(keywords=[], has=lambda kw: False)
    popup = VisibleWidget()
    search = SimpleNamespace(setText=Mock(), setCursorPosition=Mock())
    result_list = SimpleNamespace(topLevelItemCount=lambda: 0, setCurrentItem=Mock(), setFocus=Mock())
    launcher = SimpleNamespace(
        _remote_popup_area='search_history', _remote_area='directory',
        history_popup=popup, history_choices=choice_tree,
        history_visible_rows=lambda: [row],
        search_history=keyword_store, session_history=record, search=search,
        list=result_list, hide_history_popup=Mock(),
        remote_window=SimpleNamespace(set_area=Mock()),
    )
    launcher.select_history_keyword = lambda: names['select_history_keyword'](launcher)
    launcher.history_row_clicked = lambda item, col: names['history_row_clicked'](launcher, item, col)
    names['remote_history_command'](launcher, 'ENTER')
    search.setText.assert_called_once_with('zenn .md merge')
    launcher.hide_history_popup.assert_called_once_with()
    result_list.setFocus.assert_called_once()


def test_search_button_removed_but_history_controls_remain():
    assert "self._button('検索'," not in REMOTE_SOURCE
    assert "self._button('検索履歴'," in REMOTE_SOURCE
    assert "self._button('フォルダー履歴'," in REMOTE_SOURCE
    assert "self._button('↓'," not in REMOTE_SOURCE
    assert "self._button('↑'," not in REMOTE_SOURCE
    assert all(term not in REMOTE_SOURCE for term in ('SendKeys(', 'SendInput(', 'QKeyEvent('))
