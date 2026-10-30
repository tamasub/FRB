"""Source-level integration checks when PySide6 cannot run on Linux CI."""
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'expanded_view.py').read_text(encoding='utf-8')


def test_local_filter_is_live_and_uses_shared_query_engine():
    assert 'from middle_folder_filter import SORT_LABELS, filter_sort_folder_rows' in SOURCE
    assert 'self.middle_search.textChanged.connect(self.apply_middle_filter)' in SOURCE
    assert 'filter_sort_folder_rows(' in SOURCE
    assert "self.middle.layout_box.insertWidget(0, self.middle_search_bar)" in SOURCE


def test_sort_modes_present_as_single_compact_icon_button():
    assert "self.middle_sort_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)" in SOURCE
    assert "self.middle_sort_button.setIcon(middle_sort_icon(theme_family(theme), self._middle_sort_mode))" in SOURCE
    assert "action.setIcon(middle_sort_icon(theme_family(theme), mode))" in SOURCE
    assert "self.launcher.settings.setValue('expanded_middle_sort', mode)" in SOURCE


def test_metadata_does_not_replace_right_chevron_or_rename():
    assert "self.middle.tree.setItemDelegateForColumn(0, _MiddleDetailsDelegate(self.middle.tree))" in SOURCE
    assert "item.setData(0, Qt.ItemDataRole.UserRole + 2" in SOURCE
    assert "self.tree.setItemDelegateForColumn(1, _NavigationChevronDelegate(self.tree))" in SOURCE
    assert 'class _MiddleDetailsDelegate(_InlineRenameDelegate):' in SOURCE


def test_folder_transitions_clear_search_but_not_sort():
    assert 'if folder != self._middle_query_directory:' in SOURCE
    assert 'self.middle_search.clear()' in SOURCE
    assert 'rows = filter_sort_folder_rows(' in SOURCE
    assert "self.middle.tree.state() == QAbstractItemView.State.EditingState" in SOURCE
