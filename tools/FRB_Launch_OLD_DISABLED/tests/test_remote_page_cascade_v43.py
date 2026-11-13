"""Remote Page selector contracts without requiring Qt on CI."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
remote = (ROOT / 'src' / 'launch_remote.py').read_text(encoding='utf-8')
app = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')


def test_page_buttons_are_directly_below_title_and_clicked():
    assert 'root.addWidget(title_frame)' in remote
    assert remote.index('root.addWidget(title_frame)') < remote.index('root.addLayout(self.page_column)') < remote.index('root.addLayout(row_workspaces)')
    assert "list(pages)[:3]" in remote
    assert 'button.clicked.connect(lambda checked=False, pid=page_id:' in remote
    assert 'self.page_clicked.emit(pid)' in remote


def test_existing_cascade_is_reused_without_switching_main_page():
    start = app.index('    def open_remote_page(')
    end = app.index('    def show_remote_at(', start)
    block = app[start:end]
    assert 'CascadeMenu(parent=self, launcher=self)' in block
    assert 'self.fill_cascade(menu, root)' in block
    assert 'menu.popup(QPoint(pointer.x() + 8, pointer.y() + 4))' in block
    assert 'self.page_id =' not in block
    assert 'self.tabs.setCurrentIndex' not in block
    assert 'remote_page_navigation = True' in block
    assert 'm.child.remote_page_navigation' in app


def test_files_browser_remote_buttons_remain():
    assert "'WORKSPACE_FILES'" in remote
    assert "'WORKSPACE_BROWSER'" in remote
    assert "'BACKTAB'" in remote
    assert "'TAB'" in remote


def test_compiles():
    ast.parse(remote)
    ast.parse(app)
