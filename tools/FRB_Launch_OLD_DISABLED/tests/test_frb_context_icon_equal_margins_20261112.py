"""0273 safety contract: do not lose native menu foreground for cosmetic changes.

The 0272 attempted equal margins by replacing all QAction text/icons in
paintEvent. That blanked actual Windows menus. Shared *structure* and safe
Qt-native rendering are mandatory; margin equality still needs GUI QA.
"""
from pathlib import Path
import ast
import importlib.util

ROOT=Path(__file__).resolve().parents[1]


def test_one_frb_menu_object_and_native_paint_are_mandatory():
    tree=ast.parse((ROOT/'src/app.py').read_text(encoding='utf-8'))
    menu=next(node for node in tree.body if isinstance(node, ast.ClassDef)
              and node.name=='FRBContextMenu')
    method_names={node.name for node in menu.body if isinstance(node,ast.FunctionDef)}
    assert 'paintEvent' not in method_names, 'Do not override native QAction foreground'
    assert {'_schedule_grigri_runner','_activate_grigri_runner',
            '_stop_grigri_runner'} <= method_names
    assert [n.id for n in menu.bases if isinstance(n,ast.Name)] == ['RemoteFolderActionsMenu']


def test_no_foreground_wiping_or_visual_column_overrides():
    app=(ROOT/'src/app.py').read_text(encoding='utf-8')
    first=app.index('class FRBContextMenu(')
    last=app.index('\nclass RemoteFolderCascade(',first)
    section=app[first:last]
    for forbidden in ('option.text =', 'option.icon = QIcon()',
                      'original_icon.paint(', 'context_icon_text_geometry('):
        assert forbidden not in section
    style=(ROOT/'src/context_menu_presentation.py').read_text(encoding='utf-8')
    assert 'menu.setStyleSheet(palette + context_menu_spacing_qss(theme))' in style
    assert 'extra_qss' not in style


def test_contract_checker_enforces_native_rendering():
    spec=importlib.util.spec_from_file_location('context_contract_gate',
               ROOT/'scripts/check_context_menu_contract.py')
    gate=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    assert gate.violations(ROOT) == []


def test_windows_build_requires_real_menu_foreground_smoke():
    build=(ROOT/'_build_windows.bat').read_text(encoding='utf-8')
    assert 'scripts\\smoke_context_menu_native_gui.py' in build
    assert build.index('scripts\\smoke_context_menu_native_gui.py') < build.index(' -m PyInstaller ')
    smoke=(ROOT/'scripts/smoke_context_menu_native_gui.py').read_text(encoding='utf-8')
    assert "for column in ('Exp', 'List'):" in smoke
    assert 'icon_pixels < 8 or label_pixels < 8' in smoke
    assert 'menu.grab().toImage()' in smoke
