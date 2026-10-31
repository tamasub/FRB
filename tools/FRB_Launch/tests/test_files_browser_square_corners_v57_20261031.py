"""v57 square-corner visual contract, without a Qt GUI dependency."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')


def qss_rule(selector):
    prefix = selector + ' {{'
    assert prefix in SRC, selector
    return SRC.split(prefix, 1)[1].split('}}', 1)[0]


def test_files_bottom_corners_and_pane_join_are_square():
    frame = qss_rule('QFrame#expandedFilesGroup')
    folder = qss_rule('QFrame#expandedPanel[panelKind="folder"]')
    assert 'border-radius:0;' in frame
    assert 'border:1px solid {border};border-top:0;border-radius:0;' in folder
    assert "self.left = ExpandedPanel('Files', 'folder')" in SRC
    assert "self.middle = ExpandedPanel('フォルダー', 'folder')" in SRC


def test_middle_columns_heading_is_shorter_quieter():
    assert 'header.setFixedHeight(28)' in SRC
    from launch_appearance import theme_palette
    assert theme_palette('light')['column_header'] == '#f3faf5'
    assert theme_palette('dark')['column_header'] == '#394d43'
    meta = qss_rule('QHeaderView#expandedMiddleColumnsHeader::section')
    assert "color:{colors['muted_text']}" in meta
    assert "background:{colors['column_header']}" in meta
    assert 'padding:1px 8px' in meta
    assert 'header.setSectionsMovable(True)' in SRC
    assert 'header.sectionClicked.connect(self._middle_header_clicked)' in SRC


def test_bookmark_frame_and_header_square_mint_corners_no_overlay():
    bookmark = qss_rule('QFrame#expandedPanel[panelKind="bookmark"]')
    assert 'background:{hdr}' in bookmark
    assert 'border:1px solid {border};border-radius:0' in bookmark
    header = qss_rule('QWidget#expandedHeader')
    assert 'background:{hdr}' in header
    assert 'border-radius:0' in header
    assert 'self.right._top_right_outline.hide()' in SRC


def test_unrelated_remote_and_web_view_not_changed():
    assert 'self.show_files_view()' in SRC
    assert 'self.right.tree.itemClicked.connect(self.choose_bookmark)' in SRC
