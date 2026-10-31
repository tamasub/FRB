"""v70: real blank-band drag surface and Chromium resize redraw.

The remote Windows WebEngine compositor cannot be exercised headlessly. These
checks verify the actual callbacks, no reload/URL loss and layout wiring.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
WEB = (ROOT / 'src' / 'launch_web_view.py').read_text(encoding='utf-8')
EXP = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
MAIN = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')


def method(source, klass, name, env=None):
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == klass)
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    scope = dict(env or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 '<production-method>', 'exec'), scope)
    return scope[name]


def test_workspace_blank_band_is_real_mouse_widget_and_not_layout_spacer():
    assert 'self.workspace_drag_handle = QWidget(self.root_widget)' in EXP
    assert "self.workspace_drag_handle.setObjectName('expandedWorkspaceDragHandle')" in EXP
    assert 'self.workspace_drag_handle.installEventFilter(' in EXP
    assert 'self.launcher._passive_header_drag)' in EXP
    assert 'self.root_layout.addWidget(self.workspace_drag_handle, 1)' in EXP
    assert 'self.root_layout.addStretch(1)' not in EXP
    assert 'QWidget#expandedWorkspaceDragHandle {{background:transparent;border:0;}}' in EXP
    assert 'self.root_layout.addWidget(button)' in EXP  # Buttons remain independent.
    assert 'self._passive_header_drag = PassiveHeaderDrag(self)' in MAIN


def test_web_resizes_trigger_debounced_visible_surface_repair():
    source = ast.get_source_segment(WEB, next(m for c in ast.parse(WEB).body
        if isinstance(c, ast.ClassDef) and c.name == '_LaunchWebPage'
        for m in c.body if isinstance(m, ast.FunctionDef) and m.name == 'resizeEvent'))
    assert 'super().resizeEvent(event)' in source
    assert 'previous != event.size()' in source
    assert 'self._resize_surface_timer.start(160)' in source
    assert "theme_family(getattr(self._owner, '_current_theme', 'dark')) == 'light'" in source


def test_resize_repair_hides_and_shows_the_active_page_without_reloading():
    repair = method(WEB, '_LaunchWebPage', '_repair_resize_surface',
                    {'theme_family': lambda theme: theme})
    calls = []
    page = NS(runJavaScript=lambda script: calls.append(('js', script)))
    obj = NS(_repairing_surface=False,
             isVisible=lambda: True,
             hide=lambda: calls.append('hide'),
             show=lambda: calls.append('show'),
             update=lambda: calls.append('update'),
             page=lambda: page)
    obj._owner = NS(_current_theme='light', current_view=lambda: obj)
    repair(obj)
    assert calls[:3] == ['hide', 'show', 'update']
    assert calls[3][0] == 'js'
    assert 'resize' in calls[3][1]
    assert not obj._repairing_surface
    assert 'reload(' not in ast.get_source_segment(WEB, next(m for c in ast.parse(WEB).body
        if isinstance(c, ast.ClassDef) and c.name == '_LaunchWebPage'
        for m in c.body if isinstance(m, ast.FunctionDef) and m.name == '_repair_resize_surface'))


def test_repair_skips_dark_or_background_tabs():
    repair = method(WEB, '_LaunchWebPage', '_repair_resize_surface',
                    {'theme_family': lambda theme: theme})
    obj = NS(_repairing_surface=False,
             isVisible=lambda: True,
             hide=Mock(), show=Mock(), update=Mock())
    obj._owner = NS(_current_theme='dark', current_view=lambda: obj)
    repair(obj)
    obj._owner._current_theme = 'light'
    obj._owner.current_view = lambda: None
    repair(obj)
    obj.hide.assert_not_called()
    obj.show.assert_not_called()
    obj.update.assert_not_called()
