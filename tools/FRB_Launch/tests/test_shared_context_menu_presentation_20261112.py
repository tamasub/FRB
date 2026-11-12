"""Regression: Exp and List share icon positioning but icons remain full-size."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from context_menu_presentation import style_context_menu
from launch_appearance import context_menu_spacing_qss


class FakeAction:
    def __init__(self, icon=None, menu=None):
        self.icon = icon
        self.submenu = menu


class FakeMenu:
    def __init__(self, actions=()):
        self._actions = list(actions)
        self.qss = ''

    def actions(self):
        return self._actions

    def setStyleSheet(self, qss):
        self.qss = qss


def test_both_qmenu_and_cascade_menu_use_one_icon_position_contract():
    a, b = FakeMenu(), FakeMenu()
    assert style_context_menu(a, 'light') is a
    assert style_context_menu(b, 'light') is b
    assert a.qss == b.qss
    # The QStyle owns native icon layout; do not force a second icon offset.
    assert 'QMenu::icon' not in a.qss
    assert 'QMenu::item { padding:7px 9px; }' in a.qss
    assert 'width:24px; height:24px' not in a.qss
    assert 'margin-left:5px' not in a.qss
    dark = FakeMenu()
    style_context_menu(dark, 'dark')
    assert 'QMenu::icon' not in dark.qss
    assert '#4b5b56' in dark.qss


def test_native_and_frb_icons_are_never_resized_or_replaced_even_on_repeated_calls():
    """Preserve OS-specific icons, disabled state, custom FRB art and submenu icons."""
    native = object()
    frb = object()
    submenu = FakeMenu([FakeAction(frb)])
    actions = [FakeAction(native), FakeAction(frb), FakeAction(menu=submenu)]
    menu = FakeMenu(actions)
    expected_actions = tuple(menu.actions())
    for theme in ('light', 'dark', 'light'):
        style_context_menu(menu, theme)
        assert tuple(menu.actions()) == expected_actions
        assert [a.icon for a in actions] == [native, frb, None]
        assert submenu.actions()[0].icon is frb
    # Previous regression put 18px glyphs in 24px transparent pixmaps and
    # QMenu re-scaled that 24px image down to its small-icon size (~16px).
    source = (ROOT / 'src' / 'context_menu_presentation.py').read_text(encoding='utf-8')
    for forbidden in ('_normalize_action_icons', 'setIcon(', 'icon.pixmap(', 'QPixmap(', 'QPainter('):
        assert forbidden not in source


def test_all_folder_context_entry_paths_reuse_shared_styler():
    app = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
    expanded = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
    # Initial menu creation AND CascadeMenu.popup() final styling share one gateway.
    assert app.count('style_context_menu(') == 3
    assert 'def _wire_hybrid_context_menu(self, menu, *, column=None, context=True):' in app
    assert app.count('self._wire_hybrid_context_menu(') >= 6
    assert 'style_context_menu(submenu, self.launcher.color_theme)' in expanded
    assert 'style_context_menu(menu, self.color_theme)' in app
    assert 'setStyleSheet(context_menu_spacing_qss(' not in app
    assert 'menu.setStyleSheet(LIGHT_MENU_QSS + context_menu_spacing_qss(' not in app


def test_new_local_menu_styles_and_icon_mutation_are_caught_by_build_gate(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'context_gate', ROOT / 'scripts/check_context_menu_contract.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    assert checker.violations(ROOT) == []
    (tmp_path / 'src').mkdir()
    for name in ('app.py', 'expanded_view.py', 'launch_appearance.py',
                 'context_menu_presentation.py'):
        (tmp_path / 'src' / name).write_text(
            (ROOT / 'src' / name).read_text(encoding='utf-8'), encoding='utf-8')
    app = tmp_path / 'src' / 'app.py'
    app.write_text(app.read_text(encoding='utf-8').replace(
        '            style_context_menu(menu, self.color_theme)',
        '            menu.setStyleSheet("QMenu::item { padding:6px 13px; }")'),
        encoding='utf-8')
    assert any('_wire_hybrid_context_menu' in message for message in checker.violations(tmp_path))
    app.write_text((ROOT / 'src' / 'app.py').read_text(encoding='utf-8'), encoding='utf-8')
    presentation = tmp_path / 'src' / 'context_menu_presentation.py'
    presentation.write_text(presentation.read_text(encoding='utf-8') +
                            '\n# regression icon.pixmap(18)\n', encoding='utf-8')
    assert any('forbidden icon raster mutation' in message for message in checker.violations(tmp_path))


def test_cascade_popup_final_style_does_not_override_context_geometry():
    """Reproduce the exact regression: initial wiring -> CascadeMenu.popup restyle.

    Prior tests stopped after the initial style_context_menu() call and
    therefore passed even while Exp menus overwrote the shared QSS at popup.
    """
    import ast
    from context_menu_presentation import style_context_menu
    from launch_appearance import LIGHT_MENU_QSS

    tree = ast.parse((ROOT / 'src' / 'app.py').read_text(encoding='utf-8'))
    launcher_class = next(node for node in tree.body
                          if isinstance(node, ast.ClassDef) and node.name == 'Launcher')
    method = next(node for node in launcher_class.body
                  if isinstance(node, ast.FunctionDef) and node.name == 'style_cascade_menu')
    ns = {'style_context_menu': style_context_menu,
          'theme_family': lambda theme: str(theme).casefold(),
          'LIGHT_MENU_QSS': LIGHT_MENU_QSS}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 '<isolated Launcher.style_cascade_menu>', 'exec'), ns)
    style_cascade = ns['style_cascade_menu']

    class MockLauncher:
        color_theme = 'light'

    launcher = MockLauncher()
    exp = FakeMenu()
    list_menu = FakeMenu()
    style_context_menu(exp, launcher.color_theme)
    style_context_menu(list_menu, launcher.color_theme)
    list_before = list_menu.qss
    exp_before = exp.qss
    assert exp_before == list_before  # Strict equality, not CSS-minus-exception.

    # CascadeMenu.popup() calls this after initial context presentation.
    # It must remain byte-identical: no Exp-only right-arrow CSS exception.
    style_cascade(launcher, exp)
    assert exp.qss == list_before
    assert 'QMenu::icon' not in exp.qss

    # Generic non-context cascades keep their own palette (no wider UI change).
    generic = FakeMenu()
    style_cascade(launcher, generic)
    assert generic.qss == LIGHT_MENU_QSS

    # A theme change and another popup must not lose the shared contract.
    launcher.color_theme = 'dark'
    style_context_menu(list_menu, 'dark')
    style_cascade(launcher, exp)
    assert exp.qss == list_menu.qss
    assert '#4b5b56' in exp.qss
    assert 'QMenu::icon' not in exp.qss
