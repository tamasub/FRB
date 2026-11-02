"""HOME contract: both buttons collapse Files Exp, then first row -> column 2.

Qt-free AST tests run on Linux; Windows/PySide6 visual validation remains manual.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
EXP = (ROOT / 'src' / 'remote_files_explorer.py').read_text(encoding='utf-8')
REMOTE = (ROOT / 'src' / 'launch_remote.py').read_text(encoding='utf-8')


def extracted(source, class_name, func_name):
    module = ast.parse(source)
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef)
               and n.name == class_name)
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
              and n.name == func_name)
    ns = {'_DATA_ROLE': 0}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 '<HOME-contract>', 'exec'), ns)
    return ns[func_name]


class Index:
    def __init__(self, valid=True):
        self.valid = valid

    def isValid(self):
        return self.valid


def fake_exp_panel(data, path='C:\\work', valid=True):
    calls = []
    index = Index(valid)
    item = NS(data=lambda role: data)
    panel = NS(
        model=NS(index=lambda r, c: index,
                 itemFromIndex=lambda idx: item),
        tree=NS(clear_wheel_pending=lambda: calls.append('wheel-clear'),
                setCurrentIndex=lambda idx: calls.append(('select', idx)),
                scrollTo=lambda idx: calls.append(('scroll', idx))),
        _syncing_directory=False,
        _selection_timer=NS(stop=lambda: calls.append('stop-timer')),
        _index_path=lambda idx: path if data and not data.get('pc') else None,
        _schedule_tree_state_save=lambda: calls.append('save'))
    return panel, calls


def test_pc_first_row_selection_after_collapse():
    select = extracted(EXP, 'RemoteFilesExplorer', 'select_first_root_for_home')
    panel, calls = fake_exp_panel({'path': None, 'pc': True})
    target = select(panel)
    assert target == ('pc', None)
    assert [c for c in calls if isinstance(c, tuple) and c[0] == 'select']
    assert panel._syncing_directory is False
    assert calls.index('stop-timer') < next(i for i, c in enumerate(calls)
                                             if isinstance(c, tuple) and c[0] == 'select')
    assert not any('reset' in str(c) or 'collapse' in str(c) for c in calls)


def test_directory_home_returns_physical_target_without_launching_file():
    select = extracted(EXP, 'RemoteFilesExplorer', 'select_first_root_for_home')
    panel, calls = fake_exp_panel({'path': 'C:\\work', 'pc': False}, 'C:\\work')
    assert select(panel) == ('folder', 'C:\\work')
    assert len([c for c in calls if isinstance(c, tuple) and c[0] == 'select']) == 1


def test_home_with_invalid_or_missing_first_row_does_not_change_selection():
    select = extracted(EXP, 'RemoteFilesExplorer', 'select_first_root_for_home')
    panel, calls = fake_exp_panel(None, valid=False)
    assert select(panel) is None
    assert calls == []
    panel, calls = fake_exp_panel({'path': 'X:\\gone', 'pc': False}, path=None)
    assert select(panel) is None
    assert calls == []


def fake_launcher_home(*, embedded=True, target=('pc', None), remote_visible=True):
    events = []
    panel = NS(reset_to_roots=lambda: events.append('exp-collapsed'),
               select_first_root_for_home=lambda: (events.append('exp-selected') or target),
               isVisible=lambda: remote_visible)
    legacy_item = NS()
    legacy = NS(topLevelItem=lambda i: legacy_item,
                setCurrentItem=lambda item: events.append('legacy-current'))
    view = NS(isVisible=lambda: True,
              show_files_view=lambda: events.append('files-visible'),
              _embedded_files_exp_roots_ready=True,
              embedded_files_exp=panel,
              reload_embedded_files_exp_roots=lambda: events.append('reload'),
              left=NS(tree=legacy),
              choose_files=lambda item, col: events.append('legacy-preview'))
    win = NS(data=True, pages=[{}],
             expanded_view=view,
             files_exp_embedded_mode=embedded,
             files_root_hidden_mode=embedded,
             remote_window=NS(files_exp_panel=panel),
             navigate_files_exp_pc=lambda: (events.append('preview-pc') or True),
             navigate_files_exp_folder=lambda path: (events.append(('preview-folder', path)) or True),
             remote_focus_area=lambda area: events.append(('focus', area)))
    return win, events


def test_launch_home_selects_exp_pc_then_shows_its_drive_rows_in_column_two():
    navigate = extracted(APP, 'Launcher', 'navigate_home')
    win, calls = fake_launcher_home()
    navigate(win)
    assert calls == ['files-visible', 'exp-collapsed', 'exp-selected', 'preview-pc', ('focus', 'directory')]


def test_home_refreshes_uninitialized_embedded_tree_then_collapses_before_selection():
    navigate = extracted(APP, 'Launcher', 'navigate_home')
    win, calls = fake_launcher_home()
    win.expanded_view._embedded_files_exp_roots_ready = False
    navigate(win)
    assert calls == ['files-visible', 'reload', 'exp-collapsed', 'exp-selected',
                     'preview-pc', ('focus', 'directory')]


def test_repeated_home_never_reopens_previous_files_exp_branches():
    navigate = extracted(APP, 'Launcher', 'navigate_home')
    win, calls = fake_launcher_home()
    navigate(win)
    navigate(win)
    assert calls.count('exp-collapsed') == 2
    assert calls.count('preview-pc') == 2
    assert calls.index('exp-collapsed') < calls.index('exp-selected')
    assert calls.index('exp-collapsed', calls.index('exp-collapsed') + 1) < calls.index(
        'exp-selected', calls.index('exp-selected') + 1)


def test_home_uses_exp_first_folder_in_standalone_mode_too():
    navigate = extracted(APP, 'Launcher', 'navigate_home')
    win, calls = fake_launcher_home(embedded=False, target=('folder', 'C:\\FRB'))
    navigate(win)
    assert calls == ['files-visible', 'exp-collapsed', 'exp-selected', ('preview-folder', 'C:\\FRB'),
                     ('focus', 'files')]


def test_home_falls_back_to_legacy_row_without_visible_files_exp():
    navigate = extracted(APP, 'Launcher', 'navigate_home')
    win, calls = fake_launcher_home(embedded=False, remote_visible=False)
    navigate(win)
    assert calls == ['files-visible', 'legacy-current', 'legacy-preview', ('focus', 'files')]


def test_remote_and_launch_buttons_reuse_same_navigate_home_handler():
    assert 'self.nav_home_button.clicked.connect(self.navigate_home)' in APP
    remote_block = APP[APP.index("        if command == 'HOME':"):]
    assert 'self.navigate_home()' in remote_block.split("        if command == 'SEARCH':", 1)[0]
    assert "'HOME', width=28, height=24, role='icon'" in REMOTE
    assert 'HOME：Files Expを全折りたたみ→先頭行を選択→第2列に表示' in APP
    assert 'HOME：Files Expを全折りたたみ→先頭行を選択→第2列に表示' in REMOTE
    # An embedded Exp is the selected navigation row; the Remote stays bound
    # to column 2 by the existing hidden-root policy.
    assert 'self.files_root_hidden_mode' in APP
