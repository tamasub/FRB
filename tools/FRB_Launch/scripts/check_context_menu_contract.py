"""Guard the single Exp/List context presentation gate in all future builds.

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
                'QMenu::icon { width:24px; height:24px; margin-left:5px; margin-right:5px; }')
    for fragment in required:
        if fragment not in style:
            issues.append('launch_appearance.py: missing geometry: ' + fragment)
    for fragment in ('ICON_BOX_PX = 24', 'GLYPH_PX = 18',
                     'def style_context_menu(', '_normalize_action_icons(menu)'):
        if fragment not in gateway:
            issues.append('context_menu_presentation.py: missing contract: ' + fragment)
    if 'style_context_menu(submenu, self.launcher.color_theme)' not in view:
        issues.append('ExpandedLauncherView: New submenu bypasses common presentation')
    if 'menu.setStyleSheet(LIGHT_MENU_QSS + context_menu_spacing_qss(' in app:
        issues.append('app.py: local stylesheet path was reintroduced')
    return issues


if __name__ == '__main__':
    problems = violations()
    if problems:
        print('\n'.join('FAIL: ' + problem for problem in problems))
        raise SystemExit(1)
    print('PASS: Exp/List menus use one shared icon and spacing contract')
