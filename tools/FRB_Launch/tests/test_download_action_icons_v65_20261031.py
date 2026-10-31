"""v65: Chrome-like download action glyphs, with click behavior unchanged.

This source-contract test deliberately runs without the GUI/Windows runtime.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = (ROOT / 'src' / 'launch_web_view.py').read_text(encoding='utf-8')
ICONS = (ROOT / 'src' / 'browser_nav_icons.py').read_text(encoding='utf-8')


def test_modified_python_files_parse():
    ast.parse(WEB)
    ast.parse(ICONS)


def test_both_download_buttons_use_larger_icons_with_original_hit_area():
    assert 'self.folder.setIconSize(QSize(22, 22))' in WEB
    assert 'self.extract.setIconSize(QSize(22, 22))' in WEB
    assert 'self.folder.setFixedSize(30, 28)' in WEB
    assert 'self.extract.setFixedSize(30, 28)' in WEB


def test_simple_separate_chrome_style_icons_are_used():
    assert "elif name == 'folder_open':" in ICONS
    assert "elif name == 'unzip':" in ICONS
    assert "if name in ('folder_open', 'unzip'):" in ICONS
    assert 'pen.setWidthF(1.75)' in ICONS
    assert 'shape.quadTo(20.2, 9.1, 20.2, 10.0)' in ICONS
    assert 'shape.lineTo(10.3, 14.0)' in ICONS
    # Former doubled folder contour caused the cramped result.
    assert 'shape.moveTo(4.7, 8.0)' not in ICONS


def test_file_actions_still_do_exactly_the_same_thing():
    assert "self.folder.clicked.connect(lambda: owner.open_download_folder(record['path']))" in WEB
    assert "self.extract.clicked.connect(lambda: owner.extract_download_zip(record['path']))" in WEB
    assert "self.extract.setToolTip('ZIPを展開してフォルダーを開く')" in WEB
    assert "record['path'].lower().endswith('.zip')" in WEB
    assert 'worker.extracted.connect(self.open_download_folder)' in WEB
