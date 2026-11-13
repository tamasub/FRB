"""Qt-free regression coverage for the Files Exp HOME reset contract.

Uses the real production methods (via AST) with small QObject-independent
stubs.  Visual placement still needs a Windows interactive check.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'src' / 'remote_files_explorer.py').read_text(encoding='utf-8')
REMOTE = (ROOT / 'src' / 'launch_remote.py').read_text(encoding='utf-8')
MODULE = ast.parse(SOURCE)
CLASS = next(c for c in MODULE.body if isinstance(c, ast.ClassDef)
             and c.name == 'RemoteFilesExplorer')
WHEEL = next(c for c in MODULE.body if isinstance(c, ast.ClassDef)
             and c.name == 'FilesExpWheelTree')


def method(tree, name, env):
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                and n.name == name)
    namespace = dict(env)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 'remote_files_explorer.py', 'exec'), namespace)
    return namespace[name]


def test_home_is_inside_header_with_same_remote_home_icon_and_dimensions():
    assert "self.home_button = QPushButton('', header)" in SOURCE
    assert "self.home_button.setFixedSize(28, 24)" in SOURCE
    assert 'self.home_button.setIconSize(QSize(18, 18))' in SOURCE
    assert 'self.home_button.clicked.connect(self.reset_to_roots)' in SOURCE
    assert "self.home_button.setObjectName('filesExpHomeButton')" in SOURCE
    assert 'header_row.addWidget(self.home_button)' in SOURCE
    assert SOURCE.index('header_row.addWidget(self.home_button)') < SOURCE.index("title = QLabel('Files Exp', header)")
    assert "browser_navigation_icon('home', theme_family(theme))" in SOURCE
    assert "self.home_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)" in SOURCE
    assert 'border-radius:7px;padding:0' in SOURCE
    assert "'HOME', width=28, height=24, role='icon'" in REMOTE
    assert 'self.tree.setIndentation(18)' in SOURCE


def test_home_refresh_uses_same_live_first_column_as_open_and_no_navigation():
    calls = []
    source_rows = [{'title': 'A', 'item_kind': 'directory', 'launch_browse_target': 'A'}]
    launcher = NS(_remote_files_first_column_rows=lambda: list(source_rows),
                  expander=lambda: NS(expand=str.upper))
    remote = NS(parent=lambda: launcher)
    refresh = method(CLASS, 'reset_to_roots', {})
    panel = NS(parentWidget=lambda: remote,
               set_roots=lambda rows, expand: calls.append((rows, expand('a'))))
    refresh(panel)
    assert calls == [([{'title': 'A', 'item_kind': 'directory', 'launch_browse_target': 'A'}], 'A')]
    source_rows[:] = [{'title': 'B', 'item_kind': 'directory', 'launch_browse_target': 'B'}]
    refresh(panel)
    assert calls[-1][0][0]['title'] == 'B'
    assert 'folder_selected.emit' not in ast.get_source_segment(SOURCE, next(n for n in CLASS.body if isinstance(n, ast.FunctionDef) and n.name == 'reset_to_roots'))


def test_home_replaces_tree_and_clears_selection_scroll_pending_wheel():
    calls = []
    rows = [{'label': 'PC', 'path': None, 'pc': True},
            {'label': 'Root', 'path': 'C:/root', 'pc': False}]
    def make_roots(*_args): return rows
    # Avoid filesystem dependency: test path existence via the injected stub.
    class Model:
        def clear(self): calls.append('clear')
        def setHorizontalHeaderLabels(self, v): calls.append(('header', v))
        def invisibleRootItem(self): return 'parent'
        def index(self, row, col): return ('index', row, col)
    class Bar:
        def minimum(self): return 0
        def setValue(self, value): calls.append(('hscroll', value))
    class Tree:
        def clear_wheel_pending(self): calls.append('wheel-clear')
        def clearSelection(self): calls.append('selection-clear')
        def setCurrentIndex(self, idx): calls.append(('current', idx))
        def scrollToTop(self): calls.append('scroll-top')
        def horizontalScrollBar(self): return Bar()
    win = NS(_selection_timer=NS(stop=lambda: calls.append('stop-timer')),
             model=Model(), tree=Tree(),
             _append_folder=lambda *args, **kw: calls.append(('append', kw)))
    fn = method(CLASS, 'set_roots', {'registered_folder_roots': make_roots,
                                    'os': NS(path=NS(isdir=lambda p: True))})
    assert fn(win, [], lambda p: p) == 2
    assert calls.index('stop-timer') < calls.index('clear')
    assert calls.index('wheel-clear') < calls.index('clear')
    assert calls.index('selection-clear') > calls.index('clear')
    assert calls.index('scroll-top') > calls.index('clear')
    assert ('current', ('index', -1, 0)) in calls
    assert ('hscroll', 0) in calls
    assert ('append', {'pc': True, 'missing': False}) in calls
    assert ('append', {'pc': False, 'missing': False}) in calls


def test_pending_wheel_callback_target_is_invalidated_on_home():
    fn = method(WHEEL, 'clear_wheel_pending', {})
    tree = NS(_wheel_remainder=140, _edge_follow_active=True,
              _wheel_follow_pending=('pointer', 'old-index'),
              _flow_pointer='old-pointer')
    fn(tree)
    assert tree._wheel_remainder == 0
    assert tree._edge_follow_active is False
    assert tree._wheel_follow_pending is None
    assert tree._flow_pointer is None


def test_home_keeps_panel_visible_does_not_change_breadcrumb_or_user_size():
    reset_code = ast.get_source_segment(SOURCE, next(n for n in CLASS.body if isinstance(n, ast.FunctionDef) and n.name == 'reset_to_roots'))
    forbidden = ('folder_selected.emit', 'hide(', 'close(', 'resize(', '_save_size(',
                 'go_to_directory(', 'QCursor.setPos(', 'folder_context_requested.emit')
    assert not any(word in reset_code for word in forbidden)
    assert 'panel.set_roots(launcher._remote_files_first_column_rows(),' in REMOTE
