"""Guard native-size action icons and the Exp/List shared context layout.

Check layout + routing statically so a new menu cannot silently invent its own
padding. The optional Windows GUI acceptance is separately documented.
"""
from __future__ import annotations
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_CONTEXT_ENTRYPOINTS = (
    '_show_launch_json_context_popup',
    'show_expanded_background_paste_menu',
    'show_launch_context_menu',
)


def violations(root: Path = ROOT) -> list[str]:
    issues = []
    src = root / 'src'
    app = (src / 'app.py').read_text(encoding='utf-8')
    view = (src / 'expanded_view.py').read_text(encoding='utf-8')
    style = (src / 'launch_appearance.py').read_text(encoding='utf-8')
    gateway = (src / 'context_menu_presentation.py').read_text(encoding='utf-8')
    tree = ast.parse(app)
    # Basic import-surface check: a previous cleanup removed drawing helpers
    # but left their names imported by app.py, crashing Launch on startup.
    available = {node.name for node in ast.parse(gateway).body
                 if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    for node in ast.parse(app).body:
        if isinstance(node, ast.ImportFrom) and node.module == 'context_menu_presentation':
            for imported in node.names:
                if imported.name not in available:
                    issues.append('app.py: missing shared-menu import: ' + imported.name)
    owner = next((cls for cls in tree.body if isinstance(cls, ast.ClassDef)
                  and cls.name == 'Launcher'), None)
    methods = {method.name: method for method in owner.body if isinstance(method, ast.FunctionDef)} if owner else {}

    for name in ('_wire_hybrid_context_menu', *REQUIRED_CONTEXT_ENTRYPOINTS):
        method = methods.get(name)
        if method is None:
            issues.append(f'Launcher.{name}: missing method')
            continue
        call_names = [node.func.attr if isinstance(node.func, ast.Attribute) else
                      node.func.id if isinstance(node.func, ast.Name) else None
                      for node in ast.walk(method) if isinstance(node, ast.Call)]
        expected = 'style_context_menu' if name == '_wire_hybrid_context_menu' else '_wire_hybrid_context_menu'
        if expected not in call_names:
            issues.append(f'Launcher.{name}: bypasses common presentation gate')

    required = ('QMenu::item { padding:7px 9px; }',
                'QMenu::separator { height:1px; background:#e1e5e2; margin:5px 3px; }')
    for fragment in required:
        if fragment not in style:
            issues.append('launch_appearance.py: missing geometry: ' + fragment)
    # QMenu::icon left/margin/pixmap hacks caused two successive regressions.
    # Qt must position the original QAction icon without an extra offset.
    appearance_rules = style.split('CONTEXT_MENU_SPACING_QSS = ' + chr(34) * 3, 1)[-1].split(chr(34) * 3, 1)[0]
    if 'QMenu::icon' in appearance_rules:
        issues.append('launch_appearance.py: remove local icon offset/size overrides')
    cascade = methods.get('style_cascade_menu')
    if cascade is None:
        issues.append('Launcher.style_cascade_menu: missing final-style method')
    else:
        cascade_calls = [n.func.id if isinstance(n.func, ast.Name) else n.func.attr
                         if isinstance(n.func, ast.Attribute) else None
                         for n in ast.walk(cascade) if isinstance(n, ast.Call)]
        if 'style_context_menu' not in cascade_calls or '_frb_context_style' not in ast.unparse(cascade):
            issues.append('Launcher.style_cascade_menu: final popup paint erases context style')
    if '_frb_context_style' not in gateway:
        issues.append('context_menu_presentation: missing final-style marker')
    if '_frb_context_extra_qss' in gateway or 'extra_qss=' in gateway:
        issues.append('context_menu_presentation: forbidden per-column stylesheet override')
    # Columns may vary actions, but never the widget's drawing configuration.
    if 'extra_qss=remote_new_arrow_qss' in app or 'def _wire_hybrid_context_menu(self, menu, *, column=None, context=True, ' in app:
        issues.append('Launcher: Exp/List override common menu geometry')
    if 'def style_context_menu(' not in gateway:
        issues.append('context_menu_presentation.py: missing shared styling entry point')
    # Never downscale the source action icon into a transparent canvas.  QMenu
    # will itself request the native small-icon size (usually 16px on Windows).
    for forbidden in ('_normalize_action_icons', 'QPixmap(', 'QPainter(',
                      'setIcon(', 'icon.pixmap('):
        if forbidden in gateway:
            issues.append('context_menu_presentation.py: forbidden icon raster mutation: ' + forbidden)
    if 'QMenu::icon { width:24px' in style:
        issues.append('launch_appearance.py: icon size must follow the Qt menu style')
    if 'style_context_menu(submenu, self.launcher.color_theme)' not in view:
        issues.append('ExpandedLauncherView: New submenu bypasses common presentation')
    if 'menu.setStyleSheet(LIGHT_MENU_QSS + context_menu_spacing_qss(' in app:
        issues.append('app.py: local stylesheet path was reintroduced')

    # An Exp/List menu is ONE UI component that intrinsically owns its
    # wheel/click Runner.  Never make callers install an optional Runner after
    # constructing a generic QMenu: that caused Exp/List regressions in v0.9.
    menu_cls = next((cls for cls in tree.body if isinstance(cls, ast.ClassDef)
                     and cls.name == 'FRBContextMenu'), None)
    if menu_cls is None or not any(isinstance(base, ast.Name)
                                   and base.id == 'RemoteFolderActionsMenu'
                                   for base in menu_cls.bases):
        issues.append('FRBContextMenu: missing single menu+Runner component')
    else:
        menu_methods = {n.name: n for n in menu_cls.body if isinstance(n, ast.FunctionDef)}
        for method_name in ('__init__', '_schedule_grigri_runner',
                            '_activate_grigri_runner', '_stop_grigri_runner'):
            if method_name not in menu_methods:
                issues.append(f'FRBContextMenu: missing lifecycle {method_name}')
        source = ast.unparse(menu_cls)
        for required in ('aboutToShow.connect', 'aboutToHide.connect',
                         'RemoteContextWheel(self.launcher, self)'):
            if required not in source:
                issues.append('FRBContextMenu: Runner not owned by menu: ' + required)

    # 0272 catastrophic regression: an overridden paintEvent blanked native
    # QAction icon/text and failed to draw its replacement on Windows.  A
    # menu's own QMenu painter MUST remain the final foreground authority.
    # Keep Runner lifecycle in FRBContextMenu; never couple it to painting.
    if menu_cls is not None:
        methods_in_menu = {node.name for node in menu_cls.body
                           if isinstance(node, ast.FunctionDef)}
        if 'paintEvent' in methods_in_menu:
            issues.append('FRBContextMenu: custom paintEvent forbidden; use native QAction painting')
        source = ast.unparse(menu_cls)
        for forbidden in ('option.text =', 'option.icon = QIcon()',
                          'self.style().drawControl('):
            if forbidden in source:
                issues.append('FRBContextMenu: QAction foreground suppression forbidden: ' + forbidden)

    factory = methods.get('_create_files_context_menu')
    if factory is None or 'FRBContextMenu(' not in ast.unparse(factory):
        issues.append('Launcher: Files factory must create FRBContextMenu')
    required_factories = ('show_files_column_navigation_menu',
                          'show_launch_root_registration_menu',
                          'show_virtual_launch_context',
                          'show_expanded_background_paste_menu',
                          'show_launch_context_menu', 'remote_context_menu')
    for name in required_factories:
        node = methods.get(name)
        if node is None:
            issues.append(f'Launcher.{name}: missing Files context entry')
            continue
        snippet = ast.unparse(node)
        if '_create_files_context_menu(' not in snippet:
            issues.append(f'Launcher.{name}: must use shared menu factory')
        if 'QMenu(' in snippet or 'RemoteFolderActionsMenu(' in snippet:
            issues.append(f'Launcher.{name}: bypasses FRBContextMenu')
    explorer_path = src / 'remote_files_explorer.py'
    # Some regression fixtures copy only the four files under direct test.
    if explorer_path.exists():
        explorer = explorer_path.read_text(encoding='utf-8')
        if 'launcher._create_files_context_menu(self)' not in explorer:
            issues.append('Files Exp detached menu: bypasses shared factory')
    return issues


if __name__ == '__main__':
    problems = violations()
    if problems:
        print('\n'.join('FAIL: ' + problem for problem in problems))
        raise SystemExit(1)
    print('PASS: Exp/List menus use one shared icon and spacing contract')
