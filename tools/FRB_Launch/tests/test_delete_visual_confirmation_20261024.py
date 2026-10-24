"""Deletion needs both: refreshed list is visible AND later dismisses normally.
These are controller-level regression checks; Windows Qt.Tool focus remains
an explicit manual smoke step.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

SRC = Path(__file__).resolve().parents[1] / 'src' / 'app.py'
TEXT = SRC.read_text(encoding='utf-8')
TREE = ast.parse(TEXT)


def method(name, namespace):
    cls = next(c for c in TREE.body if isinstance(c, ast.ClassDef) and c.name == 'Launcher')
    fn = next(c for c in cls.body if isinstance(c, ast.FunctionDef) and c.name == name)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), str(SRC), 'exec'), namespace)
    return namespace[name]


def run_delete(tmp_path, yes=True):
    file = tmp_path / 'example.txt'
    file.write_text('test')
    events=[]
    class Box:
        class StandardButton:
            Yes=1;No=2
        @staticmethod
        def question(*args):
            events.append('confirm')
            return 1 if yes else 2
    class Timer:
        @staticmethod
        def singleShot(delay, callback):
            events.append('schedule')
            callbacks.append(callback)
    callbacks=[]
    def recycle(p):
        events.append('deleted')
        Path(p).unlink()
    context = SimpleNamespace(close=lambda: events.append('context_closed'))
    old_column=object()
    shown=Mock(side_effect=lambda col: events.append('refreshed'))
    launcher = SimpleNamespace(_directory_menu_for_path=lambda d: old_column,
        _launch_context_menu=context, hover_timer=Mock(), pending_menu_item=None,
        _filesystem_dialog_depth=0, _recent_pasted_paths=[],
        file_index_settings={'enabled':False}, file_index_busy=False,
        footer=Mock(), render=Mock(), error=Mock(),
        refresh_deleted_directory=shown)
    fn=method('perform_filesystem_context_action',
        {'Path':Path,'QMessageBox':Box,'QTimer':Timer,
         'move_to_recycle_bin':recycle,'path_key':lambda p:str(p),'DIAG':Mock()})
    fn(launcher,'delete',str(file),'file')
    for callback in callbacks: callback()
    return events, launcher, shown, old_column, file


def test_delete_yes_shows_updated_column_after_modal_context_closes(tmp_path):
    events, launcher, shown, old_column, file=run_delete(tmp_path)
    assert events.index('deleted') < events.index('context_closed') < events.index('schedule') < events.index('refreshed')
    shown.assert_called_once_with(old_column)
    assert not file.exists()
    launcher.render.assert_not_called()
    launcher.error.assert_not_called()


def test_delete_no_does_not_rebuild_or_delete(tmp_path):
    events, launcher, shown, old_column, file=run_delete(tmp_path, yes=False)
    assert events==['confirm']
    assert file.exists()
    shown.assert_not_called()


def test_same_dismissal_lifecycle_as_paste():
    assert 'self.refresh_pasted_directory(menu, reopen=True, focus_pasted=False,' in TEXT
    assert "'keyboard' if review_deleted else previous.open_mode" in TEXT
    assert 'class CascadeOutsideClickFilter' in TEXT
    assert 'if key in (Qt.Key.Key_Left, Qt.Key.Key_Escape):' in TEXT


def test_delete_review_escape_closes_even_when_main_launcher_has_focus():
    class Obj:
        def __init__(self, parent=None): self._parent=parent
        def parent(self): return self._parent
    class Menu(Obj):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.child=None
            self._delete_review_visible=True
        def isVisible(self): return True
    class Event:
        accepted=False
        def type(self): return 2
        def key(self): return 27
        def accept(self): self.accepted=True
    class App:
        @staticmethod
        def activeModalWidget(): return None
    m=Menu()
    launcher=Obj()
    launcher.menu=m
    launcher._launch_context_menu=None
    launcher._filesystem_dialog_depth=0
    launcher.close_cascade_for_main_interaction=Mock()
    namespace={'QEvent':SimpleNamespace(Type=SimpleNamespace(MouseButtonPress=1,KeyPress=2)),
               'Qt':SimpleNamespace(Key=SimpleNamespace(Key_Escape=27)),
               'QApplication':App, 'QObject':Obj,'CascadeMenu':Menu}
    cl=next(c for c in TREE.body if isinstance(c,ast.ClassDef) and c.name=='CascadeOutsideClickFilter')
    fn=next(f for f in cl.body if isinstance(f,ast.FunctionDef) and f.name=='eventFilter')
    exec(compile(ast.fix_missing_locations(ast.Module([fn],[])),str(SRC),'exec'),namespace)
    handler=SimpleNamespace(launcher=launcher)
    event=Event()
    assert namespace['eventFilter'](handler,Obj(launcher),event) is True
    assert event.accepted
    launcher.close_cascade_for_main_interaction.assert_called_once()


def test_delete_refresh_actually_popups_updated_column_even_if_old_hidden(tmp_path):
    """Mock the Qt column lifecycle (not only the controller's call count)."""
    from types import MethodType
    root = tmp_path / 'files'
    root.mkdir()
    (root / 'keep.txt').write_text('still here')
    original = root / 'gone.txt'
    original.write_text('remove')
    class Column:
        created = []
        def __init__(self, parent=None, launcher=None):
            self.launcher = launcher
            self.parent = parent
            self.open_mode = 'hover'
            self.owner_action = 'owner_action'
            self.owner_item = 'owner_item'
            self._pasted_feedback_paths = ('previous-highlight',)
            self.filter_edit = None
            self.scroll_tree = None
            self.popped = False
            self.closed = False
            self._context = {'launch_browse_target': str(root)}
            Column.created.append(self)
        def isVisible(self): return False  # Modal QMessageBox temporarily hid it.
        def _folder_container_row(self): return self._context
        def pos(self): return (10,20)
        def parentWidget(self): return self.parent
        def close(self): self.closed = True
        def deleteLater(self): pass
        def popup(self, point): self.popped = True
        def setFocus(self): pass
    original_column = Column()
    filenames = []
    def fill(column, context):
        filenames.append((column, sorted(p.name for p in root.iterdir())))
    main_window = {'visible': False}  # Native dialog hid the real launcher.
    def show_main():
        main_window['visible'] = True
    launcher = SimpleNamespace(menu=original_column, fill_cascade=fill,
        isVisible=lambda: main_window['visible'], show=Mock(side_effect=show_main),
        raise_=Mock(), activateWindow=Mock())
    namespace = {'CascadeMenu': Column}
    launcher.restore_launcher_for_transfer_review = method(
        'restore_launcher_for_transfer_review', namespace).__get__(launcher)
    fn = method('refresh_pasted_directory', namespace)
    launcher.refresh_pasted_directory = fn.__get__(launcher)
    launcher.refresh_deleted_directory = method('refresh_deleted_directory', namespace).__get__(launcher)
    original.unlink()
    launcher.refresh_deleted_directory(original_column)
    assert original_column.closed
    assert main_window['visible'] is True
    launcher.show.assert_called_once()
    launcher.raise_.assert_called_once()
    launcher.activateWindow.assert_called_once()
    assert launcher.menu is Column.created[-1]
    assert launcher.menu.popped
    assert launcher.menu._delete_review_visible
    assert launcher.menu.open_mode == 'keyboard'
    assert launcher.menu._pasted_feedback_paths == ()
    assert filenames[-1][1] == ['keep.txt']
