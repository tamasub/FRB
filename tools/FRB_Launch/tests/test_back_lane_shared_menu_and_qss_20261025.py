"""No-GUI regressions: start-up QSS and two matching Back-area context menus."""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'src'))
from context_menu_config import load_context_menus, visible_context_entries

VIEW = (HERE / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
APP = (HERE / 'src' / 'app.py').read_text(encoding='utf-8')


def method(name, source, cls):
    tree = ast.parse(source)
    parent = next(item for item in tree.body if isinstance(item, ast.ClassDef) and item.name == cls)
    definition = next(item for item in parent.body if isinstance(item, ast.FunctionDef) and item.name == name)
    ns = {}
    exec(compile(ast.Module(body=[definition], type_ignores=[]), '<isolated-method>', 'exec'), ns)
    return ns[name]


def test_expand_theme_qss_is_an_actual_valid_fstring_not_variable_reference():
    """Prevent the previous `NameError: background` from escaping py_compile."""
    tree = ast.parse(VIEW)
    klass = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'ExpandedLauncherView')
    apply_theme = next(x for x in klass.body if isinstance(x, ast.FunctionDef) and x.name == 'apply_theme')
    call = next(n for n in ast.walk(apply_theme) if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute) and n.func.attr == 'setStyleSheet'
                and isinstance(n.func.value, ast.Name) and n.func.value.id == 'self'
                and n.args and isinstance(n.args[0], ast.JoinedStr)
                and 'expandedBackLane' in ast.get_source_segment(VIEW, n))
    fstring = call.args[0]
    local_vars = {node.id: '#fcfffd' for node in ast.walk(fstring)
                  if isinstance(node, ast.Name)}
    local_vars.update({'height': 29, 'pad': 3})
    rendered = eval(compile(ast.Expression(fstring), '<startup-qss>', 'eval'), {}, local_vars)
    assert 'QWidget#expandedBackLane {background:#fcfffd;border:0;}' in rendered
    assert 'QTreeWidget#expandedTree {background:#fcfffd;' in rendered


def test_both_back_areas_call_exact_same_menu_builder():
    lane_menu = method('show_lane_new_menu', VIEW, 'ExpandedLauncherView')
    calls = []
    obj = SimpleNamespace(launcher=SimpleNamespace(
        show_expanded_background_paste_menu=lambda pos: calls.append(('menu', pos))))
    lane_menu(obj, 'right_lane_pos')
    assert calls == [('menu', 'right_lane_pos')]
    blank = VIEW.split('    def context_menu(self, pane, point):', 1)[1]
    assert 'self.launcher.show_expanded_background_paste_menu(' in blank
    filt = VIEW.split('    def eventFilter(self, obj, event):', 1)[1]
    assert 'self.show_lane_new_menu(event.globalPos())' in filt


class FakeAction:
    def __init__(self, title, callback=None):
        self.title = title
        self.callback = callback
        self.enabled = True
        self.icon = None
        self.visible_icon = False

    def setIcon(self, icon): self.icon = icon
    def setIconVisibleInMenu(self, visible): self.visible_icon = visible
    def setEnabled(self, value): self.enabled = value

    def trigger(self):
        assert self.callback is not None
        self.callback(False)


class FakeSignal:
    def connect(self, callback):
        self.callback = callback


class FakeMenu:
    created = []

    def __init__(self, parent):
        self.actions = []
        self.popup_pos = None
        self.aboutToHide = FakeSignal()
        FakeMenu.created.append(self)

    def addAction(self, title, callback=None):
        action = FakeAction(title, callback)
        self.actions.append(action)
        return action

    def addSeparator(self):
        self.actions.append(FakeAction('---'))

    def setStyleSheet(self, text): self.style = text
    def popup(self, pos): self.popup_pos = pos


def test_shared_folder_menu_keeps_paste_and_folder_actions_with_original_icons():
    build = method('show_expanded_background_paste_menu', APP, 'Launcher')
    events = []
    directory = str(HERE / 'config')
    folder = SimpleNamespace(current_directory=lambda: directory,
        add_lane_new_submenu=lambda menu: menu.addAction('新規作成 ▶'))
    dummy = SimpleNamespace(expanded_view=folder,
        color_theme='light', _launch_context_menu=None,
        _context_paste_enabled=lambda parent: True,
        _paste_from_context_menu=lambda parent: events.append('paste'),
        perform_filesystem_context_action=lambda *args: events.append(args),
        _forget_launch_context_menu=lambda menu: None)
    build.__globals__.update({
        'QMenu': FakeMenu,
        'load_context_menus': load_context_menus,
        'visible_context_entries': visible_context_entries,
        'CONTEXT_MENU_OPTIONS': HERE / 'config' / 'context_menu_options.json',
        'context_action_icon': lambda action: 'icon:' + action,
        'LIGHT_MENU_QSS': '',
        'context_menu_spacing_qss': lambda theme: '',
    })
    assert build(dummy, 'clicked_right_lane') is True
    menu = FakeMenu.created[-1]
    assert menu.popup_pos == 'clicked_right_lane'
    assert [a.title for a in menu.actions] == [
        '貼り付け', '---', '新規作成 ▶', '---',
        'エクスプローラで開く', 'ターミナルで開く', 'パスのコピー',
        '---', 'プロパティー',
    ]
    for action, action_id in zip(menu.actions[4:7] + menu.actions[8:],
                                 ('open_explorer', 'open_terminal', 'copy_path', 'properties')):
        assert action.icon == 'icon:' + action_id
        assert action.visible_icon
        action.trigger()
    assert events == [(a, directory, 'folder') for a in
                      ('open_explorer', 'open_terminal', 'copy_path', 'properties')]
    menu.actions[0].trigger()
    assert events[-1] == 'paste'
    assert dummy._launch_context_menu is menu
