"""Explorer-style New: create on disk *before* Qt's inline filename editing.

PySide6 isn't required on build hosts for these behavioral and wiring checks.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
import tempfile

from windows_shellnew import create_new_item, suggest_name

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'expanded_view.py').read_text('utf-8')


def method(name):
    module = ast.parse(SOURCE)
    view = next(node for node in module.body if isinstance(node, ast.ClassDef)
                and node.name == 'ExpandedLauncherView')
    node = next(node for node in view.body if isinstance(node, ast.FunctionDef)
                and node.name == name)
    # Keyword defaults aren't relevant for create_from_lane; compile standalone
    # to test actual method logic rather than a second approximation.
    return compile(ast.Module(body=[node], type_ignores=[]), '<expanded_view>', 'exec')


class Row:
    def __init__(self, name):
        self.name = name
        self.selected = False
    def setSelected(self, value):
        self.selected = value


class Tree:
    def __init__(self):
        self.rows = []
        self.current = None
        self.scrolled = None
    def topLevelItemCount(self):
        return len(self.rows)
    def topLevelItem(self, index):
        return self.rows[index]
    def clearSelection(self):
        for row in self.rows:
            row.selected = False
    def setCurrentItem(self, item):
        self.current = item
    def scrollToItem(self, item):
        self.scrolled = item


def demo_for(tmp):
    directory = Path(tmp)
    tree = Tree()
    changes = []
    errors = []
    statuses = []
    demo = SimpleNamespace(
        current_directory=lambda: str(directory),
        middle=SimpleNamespace(tree=tree),
        launcher=SimpleNamespace(error=errors.append,
                                 footer=SimpleNamespace(setText=statuses.append)),
    )
    def refresh_middle():
        tree.rows = [Row(p.name) for p in sorted(directory.iterdir())]
    def rename(item):
        # Inline rename is requested ONLY AFTER physical creation and selection.
        assert (directory / item.name).exists()
        assert tree.current is item
        assert tree.scrolled is item
        assert item.selected
        changes.append(item.name)
    demo.refresh_middle = refresh_middle
    demo.begin_context_inline_rename = rename
    demo.row_data = lambda item: {'title': item.name}
    return demo, changes, errors, statuses


def test_new_folder_file_markdown_exist_before_inline_rename():
    namespace = {'Path': Path, 'suggest_name': suggest_name,
                 'create_new_item': create_new_item}
    exec(method('create_from_lane'), namespace)
    fn = namespace['create_from_lane']
    with tempfile.TemporaryDirectory() as tmp:
        demo, renamed, errors, statuses = demo_for(tmp)
        for kind, filename in (
            ('folder', '新しいフォルダー'),
            ('txt', '新しいテキスト ドキュメント.txt'),
            ('md', '新しいMarkdown文書.md'),
            ('txt', '新しいテキスト ドキュメント (2).txt'),
        ):
            fn(demo, kind)
            assert renamed[-1] == filename
            assert (Path(tmp) / filename).exists()
        assert (Path(tmp) / '新しいフォルダー').is_dir()
        assert (Path(tmp) / '新しいMarkdown文書.md').read_bytes() == b''
        assert not errors
        assert len(statuses) == 4


def test_new_explorer_flow_has_no_precreation_input_dialog_and_uses_existing_rename_editor():
    fragment = SOURCE.split('    def create_from_lane(', 1)[1].split(
        '    def handle_middle_back_double_click(', 1)[0]
    assert 'QInputDialog.getText' not in fragment
    assert fragment.index('created = create_new_item(') < fragment.index('self.refresh_middle()')
    assert fragment.index('self.refresh_middle()') < fragment.index('self.begin_context_inline_rename(item)')
    assert 'self.begin_context_inline_rename(item)' in fragment
    rename_section = SOURCE.split('    def begin_inline_rename(', 1)[1].split(
        '    def finish_inline_rename(', 1)[0]
    assert 'editor.setSelection(0, length)' in rename_section  # extension stays unselected
    assert 'item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)' in rename_section


def test_both_back_areas_offer_new_and_blank_area_preserves_paste():
    assert "obj is getattr(self, 'middle_back_lane', None)" in SOURCE
    assert 'self.show_lane_new_menu(event.globalPos())' in SOURCE
    fragment = SOURCE.split('    def context_menu(', 1)[1]
    assert 'if pane is self.middle and self.current_directory():' in fragment
    assert 'self.launcher.show_expanded_background_paste_menu(' in fragment
    new_menu = SOURCE.split('    def add_lane_new_submenu(', 1)[1].split(
        '    def show_lane_new_menu(', 1)[0]
    assert "menu.addMenu('新規作成')" in new_menu
    app = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text('utf-8')
    paste_menu = app.split('    def show_expanded_background_paste_menu(', 1)[1].split(
        '    def show_launch_context_menu(', 1)[0]
    assert 'menu.addSeparator()' in paste_menu
    assert 'self.expanded_view.add_lane_new_submenu(menu)' in paste_menu
    back = SOURCE.split('    def handle_middle_back_double_click(', 1)[1].split(
        '    def eventFilter(', 1)[0]
    assert 'self.middle_blank_back_at(' in back
    assert 'self.go_up()' in back
