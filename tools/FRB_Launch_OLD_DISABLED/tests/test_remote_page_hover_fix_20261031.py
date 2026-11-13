"""Remote Page menu hover/one-click regression; Qt-free structural/runtime tests.

The normal Compact Files mode may require a double click, but the Remote Page
cascade is a navigation surface: categories must open on hover or one click.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

SOURCE = (Path(__file__).resolve().parents[1] / 'src/app.py').read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)


def cascade_method(name):
    cls = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'CascadeMenu')
    fn = next(n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)
    module = ast.Module(body=[fn], type_ignores=[])
    ns = {}
    exec(compile(ast.fix_missing_locations(module), '<cascade-method>', 'exec'), ns)
    return ns[name]


def test_remote_ignores_normal_double_click_folder_setting():
    fn = cascade_method('_double_folder_mode')
    launcher = NS(folder_open_mode='double')
    assert fn(NS(launcher=launcher, remote_page_navigation=True)) is False
    assert fn(NS(launcher=launcher, remote_page_navigation=True, bookmark_navigation=False)) is False
    assert fn(NS(launcher=launcher, remote_page_navigation=False, bookmark_navigation=False)) is True
    assert fn(NS(launcher=launcher, remote_page_navigation=False, bookmark_navigation=True)) is False


def test_one_click_expands_remote_folder_without_dismissing_parent():
    fn = cascade_method('mouseReleaseEvent')
    action = object()
    events = []
    menu = NS(
        order_press=(object(), action),
        actionAt=lambda pos: action,
        _bookmark_ignore_double_release=False,
        _folder_double_click_action=None,
        _folder_double_click_row=None,
        remote_page_navigation=True,
        openers={action: lambda mode: events.append(('open', mode))},
        hover_timer=NS(stop=lambda: events.append('stop')),
        setActiveAction=lambda a: events.append('active'),
        child=None,
    )
    event = NS(button=lambda: 'left', position=lambda: NS(toPoint=lambda: object()),
               accept=lambda: events.append('accepted'))
    fn.__globals__['Qt'] = NS(MouseButton=NS(LeftButton='left'))
    fn(menu, event)
    assert events == ['stop', 'active', ('open', 'keyboard'), 'accepted']


def test_one_click_existing_hover_child_does_not_recreate_it():
    fn = cascade_method('mouseReleaseEvent')
    action = object()
    opener = Mock()
    menu = NS(order_press=(object(), action), actionAt=lambda _: action,
              _bookmark_ignore_double_release=False,
              _folder_double_click_action=None, _folder_double_click_row=None,
              remote_page_navigation=True, openers={action: opener},
              hover_timer=NS(stop=Mock()), setActiveAction=Mock(),
              child=NS(isVisible=lambda: True, owner_action=action))
    event = NS(button=lambda: 'left', position=lambda: NS(toPoint=lambda: object()),
               accept=Mock())
    fn.__globals__['Qt'] = NS(MouseButton=NS(LeftButton='left'))
    fn(menu, event)
    opener.assert_not_called()
    event.accept.assert_called_once()


def test_same_initially_selected_scroll_row_arms_remote_hover_once():
    fn = cascade_method('_scroll_hover')
    action = object()
    item = object()
    timer = NS(stop=Mock(), start=Mock(), isActive=lambda: False)
    menu = NS(remote_page_navigation=True, hover_timer=timer, child=None,
              openers={action: Mock()}, activeAction=lambda: action,
              _scroll_item_action=lambda _: action,
              scroll_tree=NS(setCurrentItem=Mock()),
              _manual_bookmark_mode=lambda: False,
              _double_folder_mode=lambda: False,
              launcher=NS(data={'launch_hover_delay_ms': 250}))
    fn(menu, item)
    timer.start.assert_called_once_with(250)
    menu.scroll_tree.setCurrentItem.assert_not_called()
    timer.start.reset_mock()
    menu.child = NS(isVisible=lambda: True, owner_action=action)
    fn(menu, item)
    timer.start.assert_not_called()


def test_short_first_selected_row_arms_remote_hover():
    fn = cascade_method('mouseMoveEvent')
    source = ast.get_source_segment(SOURCE, next(
        n for n in next(c for c in TREE.body if isinstance(c, ast.ClassDef) and c.name == 'CascadeMenu').body
        if isinstance(n, ast.FunctionDef) and n.name == 'mouseMoveEvent'))
    assert "getattr(self, 'remote_page_navigation', False)" in source
    assert 'remote_first_hover' in source
    assert 'not self.hover_timer.isActive()' in source
