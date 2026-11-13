"""The visible filter starts in Tab-like menu focus, not editor/caret focus.

Pure unit contracts do not claim to validate native Windows Microsoft IME;
that last part must be confirmed in the running Windows launcher.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

SRC = Path(__file__).resolve().parents[1] / 'src' / 'app.py'
CODE = SRC.read_text(encoding='utf-8')
PARSED = ast.parse(CODE)
MENU = next(node for node in PARSED.body if isinstance(node, ast.ClassDef)
            and node.name == 'CascadeMenu')


def method(name, globals_):
    node = next(n for n in MENU.body if isinstance(n, ast.FunctionDef) and n.name == name)
    unit = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(unit)
    exec(compile(unit, str(SRC), 'exec'), globals_)
    return globals_[name]


class Keys:
    Key_Up=1; Key_Down=2; Key_Left=3; Key_Right=4; Key_Escape=5
    Key_Return=6; Key_Enter=7; Key_Backspace=8; Key_F=9; Key_V=10


Qt = SimpleNamespace(Key=Keys, KeyboardModifier=SimpleNamespace(ControlModifier=1, AltModifier=2))


def event(key, text=''):
    return SimpleNamespace(key=lambda: key, text=lambda: text,
                           modifiers=lambda: 0, type=lambda: 5, accept=Mock())


def test_right_arrow_expands_highlighted_folder_when_menu_owns_focus():
    fn = method('keyPressEvent', {'Qt': Qt})
    action = object()
    popup = SimpleNamespace(scroll_tree=None, hover_timer=SimpleNamespace(stop=Mock()),
        launcher=SimpleNamespace(page_key=lambda e: False), filter_edit=SimpleNamespace(text=lambda: ''),
        activeAction=lambda: action, openers={action: 'expand'}, open_current=Mock())
    right = event(Keys.Key_Right)
    fn(popup, right)
    popup.open_current.assert_called_once_with()
    right.accept.assert_called_once()


def test_typing_english_in_menu_focus_reaches_visible_filter():
    events = []
    sent = SimpleNamespace(sendEvent=lambda target, ev: events.append((target, ev)))
    fn = method('keyPressEvent', {'Qt': Qt, 'AppCascadeMenu': type('AppCascadeMenu', (), {}),
                                  'QApplication': sent, 'QKeyEvent': lambda *args: args})
    edit = object()
    popup = SimpleNamespace(scroll_tree=None, hover_timer=SimpleNamespace(stop=Mock()),
        launcher=SimpleNamespace(page_key=lambda e: False), filter_edit=edit,
        activeAction=lambda: None, openers={}, _ensure_local_filter=Mock())
    letter = event(ord('a'), 'a')
    fn(popup, letter)
    popup._ensure_local_filter.assert_called_once()
    assert events == [(edit, (5, ord('a'), 0, 'a'))]
    letter.accept.assert_called_once()


def test_japanese_ime_event_can_reach_visible_filter_without_editor_focus():
    events = []
    fn = method('inputMethodEvent', {
        'AppCascadeMenu': type('AppCascadeMenu', (), {}),
        'QApplication': SimpleNamespace(sendEvent=lambda dst, evt: events.append((dst, evt)))})
    edit = object()
    popup = SimpleNamespace(filter_edit=edit, _ensure_local_filter=Mock())
    ime = SimpleNamespace(accept=Mock())
    fn(popup, ime)
    assert events == [(edit, ime)]
    ime.accept.assert_called_once()
