"""New Files UX contract without a Windows/PySide6 runtime."""
from pathlib import Path
import ast
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from clipboard_paste import PasteItem, paste_items

APP=(ROOT/'src/app.py').read_text(encoding='utf-8')
VIEW=(ROOT/'src/expanded_view.py').read_text(encoding='utf-8')

def test_selected_color_same_with_or_without_remote():
    assert '::item:selected {{background:{active};color:{text};}}' in VIEW
    assert '::item:selected:!active {{background:{active};color:{text};}}' in VIEW
    assert '::item:selected:!active {{background:transparent' not in VIEW

def test_item_count_lives_outside_timed_notification():
    assert "self.files_item_count = QLabel('')" in APP
    assert 'footer_layout.addWidget(self.files_item_count, 0)' in APP
    assert 'footer_layout.addWidget(self.footer, 1)' in APP
    assert 'self.update_files_item_count()' in APP
    assert 'update_count(tree.topLevelItemCount())' in VIEW
    assert "self.files_item_count.setText(f'{int(count):,} 個の項目')" in APP
    assert 'update_count(0)' in VIEW

def test_popup_wheel_scroll_first_then_edge_selection():
    method=APP[APP.index('    def _wheel_column_browse('):APP.index('    def _schedule_column_wheel_follow(')]
    assert 'bar.setValue(before - distance)' in method
    assert 'if bar.value() != before:' in method
    assert 'can_follow_at_edge(before, bar.value(),' in method
    assert method.index('bar.setValue(') < method.index('self._move_filtered_selection(direction)')

def test_worker_runs_copy_without_gui_thread_blocking():
    assert 'class FilesPasteWorker(QThread)' in APP
    assert 'worker.step.connect(advance)' in APP
    assert 'QTimer.singleShot(0, worker.start)' in APP
    assert 'loop.exec()' in APP
    assert 'progress_factory' not in APP
    assert "with self.filesystem_progress('ごみ箱へ移動', len(targets))" in APP

def test_clipboard_progress_report_success(tmp_path):
    origin=tmp_path/'origin';origin.mkdir()
    target=tmp_path/'target';target.mkdir()
    (origin/'a.txt').write_text('a')
    (origin/'b.md').write_text('b')
    progress=[]
    completed=paste_items([PasteItem(origin/'a.txt',target/'a.txt'),
                          PasteItem(origin/'b.md',target/'b.md')], progress=lambda *a:progress.append(a))
    assert completed==2
    assert progress[0]==(0,2,'a.txt')
    assert progress[-1]==(2,2,'b.md')
    assert (target/'a.txt').read_text()=='a'
    assert (target/'b.md').read_text()=='b'

def test_clipboard_progress_failure_doesnt_report_false_completion(tmp_path):
    origin=tmp_path/'origin';origin.mkdir()
    target=tmp_path/'target';target.mkdir()
    (origin/'a.txt').write_text('a')
    (origin/'b.md').write_text('b')
    (target/'b.md').write_text('existing')
    progress=[]
    try:
        paste_items([PasteItem(origin/'a.txt',target/'a.txt'),
                     PasteItem(origin/'b.md',target/'b.md')], progress=lambda *a:progress.append(a))
    except FileExistsError:
        pass
    else:
        raise AssertionError('must reject conflict')
    assert (target/'b.md').read_text()=='existing'
    assert progress[-1][0] == 1
