"""Final Remote alignment contract, independent of PySide6 availability.

Windows GUI still needs visual confirmation for native glyph shaping.
"""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'src/launch_remote.py').read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)


def cls_method(class_name, method_name):
    cls = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    return next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method_name)


def button_geom():
    init = cls_method('LaunchRemote', '__init__')
    out = {}
    for n in ast.walk(init):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == '_button' and len(n.args) >= 3
                and isinstance(n.args[2], ast.Constant)):
            command = n.args[2].value
            out[command] = {k.arg: k.value.value for k in n.keywords
                            if k.arg in ('width', 'height') and isinstance(k.value, ast.Constant)}
    return out


def test_page_and_workspace_rows_have_same_height():
    geom = button_geom()
    for name in ('WORKSPACE_FILES', 'WORKSPACE_BROWSER'):
        assert geom[name] == {'width': 85, 'height': 27}
    assert "'PAGE_BUTTON_UNUSED', width=172, height=27" in SOURCE


def test_two_column_rows_share_page_edges():
    geom = button_geom()
    for name in ('SEARCH_HISTORY', 'FOLDER_HISTORY', 'BACKTAB', 'TAB'):
        assert geom[name]['width'] == 85
    assert (85 * 2 + 2) == 172
    for section in ('row_workspaces', 'row_bottom', 'row_top'):
        segment = SOURCE.split(f'{section} = QHBoxLayout()', 1)[1].split(f'root.addLayout({section})', 1)[0]
        assert f'{section}.setContentsMargins(0, 0, 0, 0)' in segment
        assert f'{section}.setSpacing(2)' in segment
        assert f'{section}.addStretch' not in segment


def test_three_column_wheel_row_follows_30_40_30_ratio():
    geom = button_geom()
    assert geom['LEFT'] == geom['RIGHT'] == {'width': 50, 'height': 46}
    assert 'self.setFixedSize(68, 46)' in SOURCE
    assert (50 + 2 + 68 + 2 + 50) == 172
    assert abs(50 / 168 - .30) < .01
    assert abs(68 / 168 - .40) < .01
    segment = SOURCE.split('row_mid = QHBoxLayout()', 1)[1].split('root.addLayout(row_mid)', 1)[0]
    assert 'row_mid.addStretch' not in segment


def test_compact_wheel_pad_has_centered_two_line_caption():
    ctor = ast.get_source_segment(SOURCE, cls_method('WheelPad', '__init__'))
    assert "QLabel('ぐりぐり' if self._compact else '◉ ぐりぐり', self)" in ctor
    assert "glyph = QLabel('🔘', self)" in ctor
    assert "glyph.setObjectName('remotePadGlyph')" in ctor
    assert 'glyph.setAlignment(Qt.AlignmentFlag.AlignCenter)' in ctor
    assert 'label.setAlignment(Qt.AlignmentFlag.AlignCenter)' in ctor
    assert 'glyph.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)' in ctor
    assert 'QLabel#remotePadLabel {{font-size:9px;' in SOURCE
    assert 'QLabel#remotePadGlyph {{font-family:\'Segoe UI Emoji\';font-size:11px;' in SOURCE


def test_remote_wheel_and_click_signals_are_not_changed():
    assert "self.command.emit('UP' if steps > 0 else 'DOWN')" in SOURCE
    assert "self.command.emit('CLICK')" in SOURCE
    assert "self.command.emit('DOUBLE_CLICK')" in SOURCE
    assert 'self.pad.wheelEvent(event)' in SOURCE
