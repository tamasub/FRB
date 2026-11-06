"""Files Exp polish and desktop invocation contracts (no Qt dependency)."""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
REMOTE = (ROOT / 'src' / 'launch_remote.py').read_text(encoding='utf-8')
TREE = (ROOT / 'src' / 'remote_files_explorer.py').read_text(encoding='utf-8')
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')


def method(source, cls, name):
    module = ast.parse(source)
    node = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == cls)
    return ast.get_source_segment(source, next(node for node in node.body if isinstance(node, ast.FunctionDef) and node.name == name))


def test_one_title_and_footer_only_guidance():
    assert "self.setWindowTitle('Files Exp')" in TREE
    assert "title = QLabel('Files Exp', header)" in TREE
    assert '第1列の登録フォルダー' not in TREE
    assert TREE.index('layout.addWidget(self.tree, 1)') < TREE.index('layout.addWidget(footer)')
    assert 'layout.addWidget(description)' not in TREE


def test_compact_tree_indentation_and_outer_margin():
    assert 'layout.setContentsMargins(5, 5, 5, 5)' in TREE
    assert 'header_row.setContentsMargins(2, 2, 2, 2)' in TREE
    assert 'self.tree.setIndentation(18)' in TREE
    assert 'self.tree.setRootIsDecorated(True)' in TREE


def test_remote_matching_close_button():
    assert "self._button('×', '閉じる'" in REMOTE
    assert "'CLOSE', width=22, height=22, role='icon'" in REMOTE
    assert "close_button.setFixedSize(22, 22)" in TREE
    assert "close_button.setProperty('role', 'icon')" in TREE
    assert 'close_button.clicked.connect(self.hide)' in TREE
    for token in ("background:{colors['panel_header']}", "color:{colors['text']}",
                  "border:1px solid {colors['panel_border']}", 'border-radius:5px',
                  "QPushButton#filesExpClose:hover {{background:{colors['hover']};}}",
                  "QPushButton#filesExpClose:pressed {{background:{colors['selection']};}}"):
        assert token in TREE
    # 2026-11-03: square, lighter Exp titlebar (both embedded and floating).
    assert 'QFrame#filesExpHeader {{background:{exp_header};' in TREE
    assert 'border-radius:0px;' in TREE


def test_remote_anchor_top_and_tracks_remote_movement():
    position = method(REMOTE, 'LaunchRemote', 'position_files_exp')
    move = method(REMOTE, 'LaunchRemote', 'moveEvent')
    assert 'self.mapToGlobal(QPoint(self.width(), 0))' in position
    assert 'panel.move(x, y)' in position
    assert 'self.position_files_exp()' in move
    assert 'panel.isVisible()' in move
    assert 'self.position_files_exp()' in method(REMOTE, 'LaunchRemote', 'toggle_files_exp')


def test_size_persists_via_launch_settings_not_separate_file():
    ctor = method(TREE, 'RemoteFilesExplorer', '__init__')
    save = method(TREE, 'RemoteFilesExplorer', '_save_size')
    assert "getattr(launcher, 'settings', None)" in ctor
    for key in ('remote_files_exp/width', 'remote_files_exp/height'):
        assert key in ctor and key in save
    assert 'self._save_size()' in method(TREE, 'RemoteFilesExplorer', 'hideEvent')
    assert 'self._size_save_timer.start()' in method(TREE, 'RemoteFilesExplorer', 'resizeEvent')
    assert 'self._size_save_timer.timeout.connect(self._save_size)' in ctor
    assert 'self._save_size()' in method(TREE, 'RemoteFilesExplorer', 'closeEvent')
    assert 'self.size_grip = QSizeGrip(footer)' in ctor


def test_desktop_double_click_warps_to_files_exp_only():
    warp = method(REMOTE, 'LaunchRemote', 'focus_cursor_on_files_exp')
    show = method(APP, 'Launcher', 'show_remote_at')
    assert 'self.pad.rect().center()' in warp
    assert "'pointer_warp_enabled', True" in warp
    assert 'QCursor.setPos(' in warp
    assert 'self.remote_window.show_at(pointer)' in show
    assert show.index('self.remote_window.show_at(pointer)') < show.index('self.remote_window.focus_cursor_on_files_exp()')
    assert APP.count('focus_cursor_on_files_exp()') == 1


def test_anchor_geometry_exact_when_screen_has_room():
    from types import SimpleNamespace as NS
    import ast
    fn = next(n for n in next(n for n in ast.parse(REMOTE).body
                       if isinstance(n, ast.ClassDef) and n.name == 'LaunchRemote').body
              if isinstance(n, ast.FunctionDef) and n.name == 'position_files_exp')
    class Point:
        def __init__(self,x,y): self.a,self.b=x,y
        def x(self): return self.a
        def y(self): return self.b
        def __eq__(self,o): return isinstance(o,Point) and (self.a,self.b)==(o.a,o.b)
    class Area:
        def left(self): return 0
        def right(self): return 1919
        def top(self): return 0
        def bottom(self): return 1079
    class Panel:
        def __init__(self): self.p=Point(0,0)
        def width(self): return 330
        def height(self): return 425
        def pos(self): return self.p
        def move(self,x,y): self.p=Point(x,y)
    panel=Panel()
    remote=NS(files_exp_panel=panel, width=lambda:184,
              mapToGlobal=lambda p:Point(100+p.x(),250+p.y()))
    ns={'QPoint':Point,'QApplication':NS(screenAt=lambda p:NS(availableGeometry=lambda:Area()),
                                       primaryScreen=lambda:None)}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),
                 'anchor.py','exec'),ns)
    ns['position_files_exp'](remote)
    assert (panel.pos().x(),panel.pos().y()) == (284,250)


def test_size_saving_is_two_qsettings_keys_and_sync():
    from types import SimpleNamespace as NS
    fn = next(n for n in next(n for n in ast.parse(TREE).body
                       if isinstance(n, ast.ClassDef) and n.name == 'RemoteFilesExplorer').body
              if isinstance(n, ast.FunctionDef) and n.name == '_save_size')
    ns={}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),
                 'size.py','exec'),ns)
    stored=[]
    settings=NS(setValue=lambda k,v:stored.append((k,v)),sync=lambda:stored.append('sync'))
    win=NS(_settings=settings,_restoring_size=False,width=lambda:410,height=lambda:555)
    ns['_save_size'](win)
    assert stored == [('remote_files_exp/width',410),('remote_files_exp/height',555),'sync']
