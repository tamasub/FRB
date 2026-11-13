"""2026-11-06 regressions: frozen icon, kana follow, Files List query history.

Pure/AST tests run on the Linux packaging runner without PySide6.
A manual Windows build and mouse/IME check remains necessary.
"""
import ast
import json
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from files_list_search_history import FilesListSearchHistory
from shuriken_assets import resource_root


class P:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __add__(self, other):
        return P(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return P(self.x - other.x, self.y - other.y)
    def __eq__(self, other):
        return isinstance(other, P) and (self.x, self.y) == (other.x, other.y)
    def isNull(self):
        return self.x == 0 and self.y == 0


def test_resource_root_works_in_source_and_pyinstaller(tmp_path, monkeypatch):
    monkeypatch.delattr(sys, '_MEIPASS', raising=False)
    root = resource_root(ROOT / 'src/remote_shuriken.py')
    assert root == ROOT
    assert (root / 'assets/remote_shuriken.png').is_file()
    monkeypatch.setattr(sys, '_MEIPASS', str(tmp_path), raising=False)
    assert resource_root(ROOT / 'src/remote_shuriken.py') == tmp_path
    source = (ROOT / 'src/remote_shuriken.py').read_text('utf-8')
    bat = (ROOT / '_build_windows.bat').read_text('utf-8')
    spec = (ROOT / 'FRBLaunch.spec').read_text('utf-8')
    assert "ICON_PATH = resource_root(__file__) / 'assets' / 'remote_shuriken.png'" in source
    assert '--add-data "assets;assets"' in bat
    assert "('assets', 'assets')" in spec


def test_files_list_history_explicit_register_reload_preserves_query(tmp_path):
    file = tmp_path / 'files_list_search_history.json'
    history = FilesListSearchHistory(file, limit=2)
    assert history.remember('画像/2026 OR 日本語')
    assert history.remember('　report AND .md　')
    assert not history.remember(' REPORT and .MD ')
    assert history.keywords == ['report AND .md', '画像/2026 OR 日本語']
    assert FilesListSearchHistory(file, limit=2).keywords == history.keywords
    assert '画像/2026 OR 日本語' in file.read_text('utf-8')
    assert history.remember('新規')
    assert history.keywords == ['新規', 'report AND .md']
    assert history.remove('report AND .md')
    assert FilesListSearchHistory(file, limit=2).keywords == ['新規']


def test_files_list_history_bad_json_and_failed_save(tmp_path, monkeypatch):
    file = tmp_path / 'files_list_search_history.json'
    file.write_text('}{', encoding='utf-8')
    history = FilesListSearchHistory(file)
    assert history.keywords == []
    assert history.remember('初期値')
    import files_list_search_history as mod
    monkeypatch.setattr(mod.os, 'replace', lambda *a, **k: (_ for _ in ()).throw(OSError('locked')))
    with pytest.raises(OSError, match='locked'):
        history.remember('失敗')
    assert history.keywords == ['初期値']
    assert json.loads(file.read_text('utf-8'))['keywords'] == ['初期値']


def _method(source_file, klass, method):
    syntax = ast.parse((ROOT / source_file).read_text('utf-8'))
    cls = next(node for node in syntax.body
               if isinstance(node, ast.ClassDef) and node.name == klass)
    return next(node for node in cls.body
                if isinstance(node, ast.FunctionDef) and node.name == method)


def test_kana_move_uses_exact_main_window_delta():
    method = _method('src/remote_kana_integration.py', 'RemoteKanaIntegration',
                     'follow_launcher_move')
    scope = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 '<follow_launcher_move>', 'exec'), scope)
    class Window:
        def __init__(self): self.location, self.visible = P(300, 400), True
        def isVisible(self): return self.visible
        def pos(self): return self.location
        def move(self, point): self.location = point
    obj = NS(window=Window())
    follow = scope['follow_launcher_move']
    follow(obj, P(32, -14))
    assert obj.window.location == P(332, 386)
    follow(obj, P(0, 0))
    assert obj.window.location == P(332, 386)
    obj.window.visible = False
    follow(obj, P(80, 90))
    assert obj.window.location == P(332, 386)


def test_main_drag_moves_kana_in_both_remote_modes():
    method = _method('src/app.py', 'Launcher', 'moveEvent')
    class Base:
        def moveEvent(self, event): self.base_called = True
    test_cls = ast.ClassDef(name='TestLauncher', bases=[ast.Name(id='Base',ctx=ast.Load())],
                            keywords=[], body=[method], decorator_list=[])
    scope = {'Base': Base}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[test_cls],type_ignores=[])),
                 '<moveEvent>', 'exec'),scope)
    obj = scope['TestLauncher']()
    moves = []
    keyboard = NS(isVisible=lambda: True)
    companion = NS(window=keyboard, follow_launcher_move=lambda delta: moves.append(delta),
                   reposition=lambda: moves.append('reposition'))
    remote = NS(isVisible=lambda: True, pos=lambda: P(200, 200),
                move=lambda p: moves.append(('remote', p)))
    obj._remote_kana_companion = companion
    obj.remote_window = remote
    obj.isVisible = lambda: True
    obj.queue_remote_15_alignment = lambda: moves.append('queue-15')
    event = NS(pos=lambda: P(130, 140), oldPos=lambda: P(110, 115))
    obj.remote_15_mode = False
    obj.moveEvent(event)
    assert moves == [P(20, 25), ('remote', P(220, 225)), 'reposition']
    moves.clear()
    obj.remote_15_mode = True
    obj.moveEvent(event)
    assert moves == [P(20, 25), 'queue-15']
    assert obj.base_called


def test_files_list_history_button_is_left_of_local_search_and_keeps_filter():
    text = (ROOT/'src/expanded_view.py').read_text('utf-8')
    assert "self.files_list_search_history = FilesListSearchHistory(history_path)" in text
    # v0.3: the Files List history must not grab input from the Remote rod.
    assert 'self.middle_search_history_menu = _NonGrabbingHistoryMenu(' in text
    assert 'self.middle_search_history_button.clicked.connect(' in text
    assert text.index('middle_search_layout.addWidget(self.middle_search_history_button, 0)') < text.index('self.middle_search = QLineEdit(self.middle_search_bar)')
    assert 'self.middle_search.textChanged.connect(self.apply_middle_filter)' in text
    assert 'self.middle_search.setText(keyword)' in text
    assert 'self.files_list_search_history.remember(self.middle_search.text())' in text
    assert 'self.files_list_search_history.remove(keyword)' in text
    assert "self.middle_search_history_button.setIcon(_files_list_keyword_history_icon(theme))" in text
