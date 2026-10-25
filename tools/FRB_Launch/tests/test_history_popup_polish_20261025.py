"""Non-GUI checks for global outside click and two popup row icons."""
from pathlib import Path
import ast

PROJECT = Path(__file__).resolve().parents[1]
APP = (PROJECT / 'src/app.py').read_text(encoding='utf-8')
VIEW = (PROJECT / 'src/expanded_view.py').read_text(encoding='utf-8')
CHEVRON = (PROJECT / 'src/combo_chevron_icon.py').read_text(encoding='utf-8')


def test_outside_click_filter_is_installed_application_wide():
    tree = ast.parse(APP)
    matches = [node for node in tree.body
               if isinstance(node, ast.ClassDef) and node.name == 'HistoryOutsideClickFilter']
    assert len(matches) == 1
    source = ast.get_source_segment(APP, matches[0])
    assert 'QEvent.Type.MouseButtonPress' in source
    assert 'current is launcher.history_popup or current is launcher.search' in source
    assert 'launcher.hide_history_popup()' in source
    assert 'return False' in source  # Original click always reaches the destination widget.
    assert 'QApplication.instance().installEventFilter(self._history_outside_click_filter)' in APP


def test_clock_is_icon_only_and_does_not_change_saved_search_terms():
    assert 'def history_clock_icon():' in APP
    assert "'🕔'" in APP
    assert 'row.setIcon(0, self.history_clock_icon)' in APP
    assert "row = QTreeWidgetItem([keyword, '×'])" in APP
    assert 'self.history_choices.setIconSize(QSize(19, 19))' in APP


def test_folder_is_native_folder_icon_without_modifying_full_path():
    assert 'QFileIconProvider.IconType.Folder' in VIEW
    assert 'row.setIcon(0, self.launcher.file_icons.icon(' in VIEW
    assert "row = QTreeWidgetItem([path, '×'])" in VIEW
    assert 'self.favorite_choices.setIconSize(QSize(19, 19))' in VIEW


def test_search_field_is_shorter_and_vertically_centered():
    assert 'self.search.setMinimumHeight(36)' in APP
    assert 'self.search.setMaximumHeight(36)' in APP
    assert 'search_row.setContentsMargins(10, 3, 8, 3)' in APP
    assert "combo_chevron_icon(self.color_theme, offset_x=-1)" in APP
    assert 'def combo_chevron_icon(theme=' in CHEVRON


def test_modified_sources_are_valid_python():
    for source in (APP, VIEW, CHEVRON):
        ast.parse(source)
