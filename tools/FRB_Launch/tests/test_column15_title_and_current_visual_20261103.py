"""Column 1.5 visual contract (independent of Qt/Windows execution)."""
import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1] / 'src'
EXP = (ROOT / 'remote_files_explorer.py').read_text(encoding='utf-8')
VIEW = (ROOT / 'expanded_view.py').read_text(encoding='utf-8')
APP = (ROOT / 'app.py').read_text(encoding='utf-8')


def method(text, class_name, name):
    tree = ast.parse(text)
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
    fn = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == name)
    module = ast.Module(body=[fn], type_ignores=[])
    # No Qt classes are required to execute these two state-only functions.
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, '<extracted>', 'exec'), namespace)
    return namespace[name]


class FakeStyle:
    def __init__(self):
        self.changes = []

    def unpolish(self, widget):
        self.changes.append(('unpolish', widget))

    def polish(self, widget):
        self.changes.append(('polish', widget))


class FakeWidget:
    def __init__(self, **properties):
        self.properties = properties
        self._style = FakeStyle()
        self.updates = 0
        self.viewport_updates = 0

    def property(self, name):
        return self.properties.get(name)

    def setProperty(self, name, value):
        self.properties[name] = value

    def style(self):
        return self._style

    def update(self):
        self.updates += 1

    def viewport(self):
        return SimpleNamespace(update=self._viewport_update)

    def _viewport_update(self):
        self.viewport_updates += 1


def test_files_exp_active_passive_state_only_without_navigation():
    f = method(EXP, 'RemoteFilesExplorer', 'set_operating_active')
    header = FakeWidget(operatingActive=False)
    tree = FakeWidget(operatingActive=False)
    panel = SimpleNamespace(_embedded=True, exp_header=header, tree=tree)
    f(panel, True)
    assert header.property('operatingActive') is True
    assert tree.property('operatingActive') is True
    f(panel, False)
    assert header.property('operatingActive') is False
    assert tree.property('operatingActive') is False
    assert tree.viewport_updates == 2
    # No re-polish on redundant mode change.
    before = len(tree._style.changes)
    f(panel, False)
    assert len(tree._style.changes) == before


def test_independent_files_exp_window_does_not_change_with_controller():
    f = method(EXP, 'RemoteFilesExplorer', 'set_operating_active')
    panel = SimpleNamespace(_embedded=False)
    assert f(panel, False) is None


def test_titles_and_list_track_exp_list_mode_without_touching_breadcrumb():
    f = method(VIEW, 'ExpandedLauncherView', 'set_files_operating_area')
    title = FakeWidget(operatingActive=False)
    tree = FakeWidget(remoteInactive=False)
    exp = SimpleNamespace(set_operating_active=lambda active: exp_calls.append(active))
    exp_calls = []
    view = SimpleNamespace(embedded_files_exp=exp, files_list_title_box=title,
                           middle=SimpleNamespace(tree=tree))
    f(view, 'files_exp')
    assert exp_calls == [True]
    assert title.property('operatingActive') is False
    assert tree.property('remoteInactive') is True
    f(view, 'directory')
    assert exp_calls == [True, False]
    assert title.property('operatingActive') is True
    assert tree.property('remoteInactive') is False
    f(view, 'search')
    assert exp_calls == [True, False], 'search must not discard the Files target'
    assert title.property('operatingActive') is True


def test_titles_have_green_border_and_fill_in_active_state():
    assert 'QFrame#filesExpHeader[operatingActive="true"]' in EXP
    assert 'QFrame#filesListTitleBox[operatingActive="true"]' in VIEW
    assert 'background:{colors[\'selection\']};border:1px' in EXP
    assert 'background:{active};border:1px' in VIEW
    assert "self.files_list_title_box.setProperty('operatingActive', False)" in VIEW


def test_exp_selected_fill_requires_active_operating_target():
    assert 'QTreeView#filesExpTree[operatingActive="true"]::item:selected' in EXP
    assert 'QTreeView#filesExpTree::item:selected,' in EXP
    assert 'background:transparent;color:' in EXP
    row = ast.get_source_segment(EXP, next(
        n for n in ast.walk(ast.parse(EXP))
        if isinstance(n, ast.FunctionDef) and n.name == 'drawRow'))
    assert 'index != self.currentIndex()' in row
    assert 'painter.drawRoundedRect' in row


def test_list_active_multiple_selection_never_has_green_fill_without_outline():
    row = ast.get_source_segment(VIEW, next(
        n for n in ast.walk(ast.parse(VIEW))
        if isinstance(n, ast.FunctionDef) and n.name == 'drawRow'
        and 'active_selected' in (ast.get_source_segment(VIEW, n) or '')))
    assert 'active_selected' in row
    assert 'item.isSelected()' in row
    assert "self.property('remoteInactive') is not True" in row
    assert 'if is_current or active_selected' in row
    assert 'painter.drawRoundedRect' in row


def test_remote_target_and_mouse_click_both_update_titles():
    remote_area = ast.get_source_segment(APP, next(
        n for n in ast.walk(ast.parse(APP))
        if isinstance(n, ast.FunctionDef) and n.name == 'remote_focus_area'))
    assert 'self.expanded_view.set_files_operating_area(area)' in remote_area
    click_sync = ast.get_source_segment(VIEW, next(
        n for n in ast.walk(ast.parse(VIEW))
        if isinstance(n, ast.FunctionDef) and n.name == '_sync_remote_area_after_mouse_press'))
    assert 'self.set_files_operating_area(area)' in click_sync


def test_panel_width_sync_and_remote_floating_window_retained():
    assert 'title.setFixedWidth(width)' in VIEW
    assert 'width = max(85, exp.width())' in VIEW
    assert "self.remote_15_lane.setFixedWidth(196)" in VIEW
    assert 'queue_remote_15_alignment' in APP
