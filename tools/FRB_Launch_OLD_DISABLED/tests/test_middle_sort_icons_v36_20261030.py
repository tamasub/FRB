"""Source checks for v36; GUI painting itself needs Windows/PySide6."""
from pathlib import Path
import ast

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'expanded_view.py').read_text(encoding='utf-8')


def test_hidpi_canvas_is_not_clipped():
    # DPR 2 means the old 40x40 backing was only 20x20 logical pixels,
    # while its painter drew arrows at x=32/y=28 (outside the canvas).
    start = SOURCE.index('def middle_sort_icon(')
    end = SOURCE.index('class _SeparatedFileTree(', start)
    icon_code = SOURCE[start:end]
    assert 'QPixmap(48, 48)' in icon_code
    assert 'pix.setDevicePixelRatio(2)' in icon_code
    assert 'QRectF(1.5, 1.0, 12, 11)' in icon_code
    assert 'QPointF(23.2, 15.7)' in icon_code
    assert 'mode in (\'date_asc\', \'size_asc\')' in icon_code
    assert "'A'" in icon_code and "'Z'" in icon_code
    assert 'drawRoundedRect(QRectF(2.5, 5, 13.5, 15)' in icon_code


def test_current_mode_and_all_menu_entries_have_distinct_icons():
    assert 'action.setIcon(middle_sort_icon(theme_family(theme), mode))' in SOURCE
    assert 'middle_sort_icon(theme_family(theme), self._middle_sort_mode)' in SOURCE
    assert 'theme_family(self.launcher.color_theme), mode)' in SOURCE
    assert 'self.middle_sort_button.setAccessibleName(' in SOURCE
    assert 'setFixedSize(33, 28)' in SOURCE
    assert 'QToolButton#expandedMiddleSort::menu-indicator {image:none;width:0px;}' in SOURCE.replace('{{','{').replace('}}','}')


def test_sort_logic_unmodified():
    tree = ast.parse(SOURCE)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ExpandedView') if any(isinstance(n, ast.ClassDef) and n.name=='ExpandedView' for n in tree.body) else None
    assert 'self.launcher.settings.setValue(\'expanded_middle_sort\', mode)' in SOURCE
    assert 'self._fill_middle_from_current()' in SOURCE
