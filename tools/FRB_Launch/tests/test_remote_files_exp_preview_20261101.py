"""Files Exp prototype contracts (no PySide6 needed in CI).

Checks are intentionally limited to the new experimental Remote surface;
existing Files column navigation / actions must remain untouched.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
REMOTE_SOURCE = (ROOT / 'src' / 'launch_remote.py').read_text('utf-8')
PREVIEW_SOURCE = (ROOT / 'src' / 'remote_files_explorer.py').read_text('utf-8')
REMOTE_TREE = ast.parse(REMOTE_SOURCE)


def remote_method(name):
    cls = next(n for n in REMOTE_TREE.body
               if isinstance(n, ast.ClassDef) and n.name == 'LaunchRemote')
    return next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)


def test_button_is_at_very_bottom_of_remote_after_status():
    status_idx = REMOTE_SOURCE.index('root.addWidget(status_frame)')
    exp_idx = REMOTE_SOURCE.index('root.addWidget(self.files_exp_button)')
    adjust_idx = REMOTE_SOURCE.index('self.adjustSize()', exp_idx)
    assert status_idx < exp_idx < adjust_idx
    assert "'FILES_EXP_PREVIEW', width=172, height=27" in REMOTE_SOURCE
    assert "self.files_exp_button.clicked.connect(self.toggle_files_exp)" in REMOTE_SOURCE


def test_explorer_uses_registered_roots_and_lazy_real_folders():
    # Multiple shortcut roots are presented by a read-only model.
    for clause in ('QStandardItemModel(self)', 'QTreeView(self)',
                   'self.tree.setAnimated(True)',
                   'self.tree.setRootIsDecorated(True)',
                   'self.tree.setExpandsOnDoubleClick(True)',
                   'self.tree.expanded.connect(self._expand_index)',
                   'registered_folder_roots(rows, expand)',
                   "children = subdirectories(data['path'])",
                   'for row in drive_rows()'):
        assert clause in PREVIEW_SOURCE


def test_preview_has_no_mutations_or_navigation_actions():
    for clause in ('self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)',
                   'self.tree.setDragEnabled(False)', 'self.tree.setAcceptDrops(False)',
                   'self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)'):
        assert clause in PREVIEW_SOURCE
    for forbidden in ('go_to_directory(', 'set_current_directory(', 'subprocess.',
                      'rename(', 'os.remove(', 'shutil.'):
        assert forbidden not in PREVIEW_SOURCE


def test_remote_hidden_closes_preview_and_theme_follows_remote():
    hide = ast.get_source_segment(REMOTE_SOURCE, remote_method('hideEvent'))
    theme = ast.get_source_segment(REMOTE_SOURCE, remote_method('apply_theme'))
    assert "getattr(self, 'files_exp_panel', None)" in hide
    assert 'panel.hide()' in hide
    assert 'panel.apply_theme(theme)' in theme


def test_preview_button_toggles_and_is_clamped_to_screen():
    fn = remote_method('toggle_files_exp')
    class FakePoint:
        def __init__(self, x, y): self._x, self._y = x, y
        def x(self): return self._x
        def y(self): return self._y
    class Screen:
        def availableGeometry(self): return self
        def left(self): return 0
        def top(self): return 0
        def right(self): return 1199
        def bottom(self): return 899
    class Panel:
        def __init__(self, *a): self.visible = False; self.pos = None; self.shown = 0; self.roots = None
        def isVisible(self): return self.visible
        def hide(self): self.visible = False
        def width(self): return 330
        def height(self): return 425
        def move(self, x, y): self.pos = (x, y)
        def show(self): self.visible = True; self.shown += 1
        def raise_(self): pass
        def set_roots(self, rows, expand): self.roots = (rows, expand)
    class Button:
        def width(self): return 172
        def height(self): return 27
        def mapToGlobal(self, point): return FakePoint(1080 + point.x(), 850 + point.y())
    scope = {'RemoteFilesExplorer': Panel, 'QPoint': FakePoint,
             'QApplication': NS(screenAt=lambda point: Screen(),
                                primaryScreen=lambda: Screen())}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 'launch_remote.py', 'exec'), scope)
    toggle = scope['toggle_files_exp']
    launcher = NS(_remote_files_first_column_rows=lambda: [{'item_kind': 'directory', 'title': 'Root'}],
                  expander=lambda: NS(expand=lambda text: text))
    remote = NS(files_exp_panel=None, files_exp_theme='light', files_exp_button=Button(),
                parent=lambda: launcher)
    toggle(remote)
    assert remote.files_exp_panel.visible
    assert remote.files_exp_panel.pos == (746, 452)  # flip left, clamp vertical
    assert remote.files_exp_panel.roots[0][0]['title'] == 'Root'
    toggle(remote)
    assert not remote.files_exp_panel.visible
    toggle(remote)
    assert remote.files_exp_panel.visible
    assert remote.files_exp_panel.shown == 2
