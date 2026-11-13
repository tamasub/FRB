"""2026-10-26 regressions for narrow breadcrumbs and main-history IME."""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from directory_address import breadcrumb_segments, compact_segments


def test_compaction_never_reorders_surviving_folder_levels_at_any_width():
    original = breadcrumb_segments(r'F:\alpha\beta\gamma\delta\epsilon\zeta')
    fm = lambda label: len(label) * 7 + 10
    for width in range(30, 900, 3):
        visible = compact_segments(original, width, fm)
        kept = [segment for segment in visible if segment[1] is not None]
        assert kept[0] == original[0]
        assert kept[-1] == original[-1]
        positions = [original.index(segment) for segment in kept]
        assert positions == sorted(positions), (width, visible)
        if ('…', None) in visible:
            assert visible[1] == ('…', None)
            # No ghost levels: after ellipsis, visible ancestors are a suffix.
            assert kept[1:] == original[positions[1]:]


def test_multiple_remaining_ancestors_keep_original_order():
    original = breadcrumb_segments(r'F:\one\two\three\four\five\six')
    fm = lambda label: len(label) * 8 + 10
    candidate = next((compact_segments(original, width, fm)
                      for width in range(50, 700)
                      if len(compact_segments(original, width, fm)) >= 5
                      and ('…', None) in compact_segments(original, width, fm)), None)
    assert candidate is not None
    names = [x[0] for x in candidate]
    assert names == [original[0][0], '…'] + [x[0] for x in original[-(len(candidate)-2):]]


def test_main_history_receives_and_redirects_japanese_ime_preedit():
    source = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    launcher = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                    and node.name == 'Launcher')
    bodies = {node.name: ast.get_source_segment(source, node)
              for node in launcher.body if isinstance(node, ast.FunctionDef)}
    handoff = bodies['handle_history_input_method']
    assert 'QEvent.Type.InputMethod' in handoff
    assert 'event.preeditString() or event.commitString()' in handoff
    assert 'self.hide_history_popup()' in handoff
    assert 'self.search.setFocus(' in handoff
    assert 'QApplication.sendEvent(self.search, event)' in handoff
    assert source.index('self.history_choices.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)') < source.index('self.history_choices.installEventFilter(self)')
    assert 'self.handle_history_input_method(obj, event)' in bodies['eventFilter']
    assert 'self.hide_history_popup()' in bodies['search_text_changed']
    # FocusIn must not forcibly reset an in-progress Japanese composition.
    assert "getattr(self, '_history_ime_handoff', False)" in bodies['initialize_search_ime']


def test_ime_handoff_executes_once_before_commit_and_keeps_preedit():
    """Execute the real method with minimal Qt fakes on non-Windows CI."""
    from types import SimpleNamespace

    source = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    launcher = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    method = next(n for n in launcher.body if isinstance(n, ast.FunctionDef)
                  and n.name == 'handle_history_input_method')
    scope = {'QEvent': SimpleNamespace(Type=SimpleNamespace(InputMethod='ime')),
             'Qt': SimpleNamespace(FocusReason=SimpleNamespace(OtherFocusReason='other'))}
    delivered = []
    scope['QApplication'] = SimpleNamespace(sendEvent=lambda *args: delivered.append(args))
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(ROOT / 'src/app.py'), 'exec'), scope)

    class FakeSearch:
        focused = False
        def setFocus(self, reason):
            self.focused = (reason == 'other')

    class FakePopup:
        visible = True
        def isVisible(self):
            return self.visible

    class FakeEvent:
        accepted = False
        def type(self):
            return 'ime'
        def preeditString(self):
            return 'にほん'
        def commitString(self):
            return ''
        def accept(self):
            self.accepted = True

    search = FakeSearch()
    popup = FakePopup()
    viewport = object()
    history = SimpleNamespace(viewport=lambda: viewport)
    def close():
        popup.visible = False
    state = SimpleNamespace(search=search, history_choices=history,
                            history_popup=popup, hide_history_popup=close)
    evt = FakeEvent()
    assert scope['handle_history_input_method'](state, history, evt) is True
    assert popup.visible is False
    assert search.focused is True
    assert evt.accepted is True
    assert delivered == [(search, evt)]
    assert state._history_ime_handoff is True

    # A native event already addressed to QLineEdit must not be replayed.
    popup.visible = True
    delivered.clear()
    evt2 = FakeEvent()
    assert scope['handle_history_input_method'](state, search, evt2) is False
    assert popup.visible is False
    assert delivered == []
