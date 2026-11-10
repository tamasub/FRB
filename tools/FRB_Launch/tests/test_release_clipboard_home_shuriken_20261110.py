"""New release contracts: clipboard footer, HOME from choice lists, 手裏剣 four."""
import ast
import copy
import json
from pathlib import Path
from types import SimpleNamespace as NS
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from core import validate
from shuriken_model import configured_entries, choose_entry
APP = (ROOT / 'src/app.py').read_text('utf-8')


def extracted(method):
    tree = ast.parse(APP)
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef)
               and node.name == 'Launcher')
    fn = next(node for node in cls.body if isinstance(node, ast.FunctionDef)
              and node.name == method)
    context = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 f'<{method}>', 'exec'), context)
    return context[method]


def test_copy_status_comes_after_real_clipboard_write():
    method = extracted('next_step')
    writes = []
    callbacks = []
    class Clip:
        def setText(self, value):
            writes.append(value)
    class Application:
        @staticmethod
        def clipboard():
            return Clip()
    class Timer:
        @staticmethod
        def singleShot(delay, callback):
            callbacks.append(callback)
    method.__globals__.update(QApplication=Application, QTimer=Timer,
                              DIAG=NS(info=lambda *a:None),
                              windows=NS(restore=lambda *a:None, paste=lambda *a:None))
    win = NS(queue=[{'launch_action_type':'ClipboardCopy','launch_text':'20261110_103840'}],
             _clipboard_job_title='今日の日時',
             info_notice=lambda message: writes.append(message),
             next_step=lambda:None)
    method(win)
    assert writes == ['20261110_103840','クリップボードにコピーしました：今日の日時']
    assert len(callbacks) == 1


def test_sendkey_choice_notifies_after_clipboard_set():
    method = extracted('next_step')
    writes=[]
    class Application:
        @staticmethod
        def clipboard():
            return NS(setText=lambda v:writes.append(('copied', v)))
    method.__globals__.update(QApplication=Application,
                              QTimer=NS(singleShot=lambda *a:None),
                              DIAG=NS(info=lambda *a:None),
                              windows=NS(restore=lambda *a:writes.append(('restored',None)),
                                         paste=lambda *a:writes.append(('paste',None))))
    win=NS(queue=[{'launch_action_type':'SendKey','launch_text':'😂🤣'}],
           target=None,_clipboard_job_title='絵文字一覧',
           info_notice=lambda s:writes.append(('notice',s)),
           next_step=lambda:None)
    method(win)
    assert [x[0] for x in writes]==['restored','copied','notice','paste']
    assert 'ℹ️' not in writes[2][1]  # added by the shared footer method


def test_home_from_hidden_choice_restores_files_workspace():
    home = extracted('navigate_home')
    events=[]
    panel=NS(reset_to_roots=lambda:events.append('reset'),
             select_first_root_for_home=lambda:('pc',None))
    view=NS(isVisible=lambda:('render' in events),
            show_files_view=lambda:events.append('files'),
            embedded_files_exp=panel,
            _embedded_files_exp_roots_ready=True)
    tab=NS(blockSignals=lambda x:None,setCurrentIndex=lambda x:events.append(('page',x)))
    win=NS(data=True, pages=[{'page_id':'work'}, {'page_id':'system'}],
           view_mode='expanded', expanded_view=view,
           _read_expanded_options=lambda:{'page_id':'system'},
           _nav_before_change=lambda:None,_nav_after_change=lambda:None,
           hide_history_popup=lambda:None,menu=None,
           hover_timer=NS(stop=lambda:None), pending_menu_item=None,
           stack=[{}],selection={'item_id':'email'}, checked={'one'},
           page_id='work',tabs=tab,search=NS(clear=lambda:None),
           render=lambda:events.append('render'),
           files_exp_embedded_mode=True,
           navigate_files_exp_pc=lambda:events.append('pc') or True,
           remote_focus_area=lambda v:events.append('focus:'+v),
           remote_15_mode=False)
    home(win)
    assert win.page_id=='system' and win.selection is None and win.stack==[]
    assert events==[('page',1),'render','files','reset','pc','focus:files_exp']


def test_shuriken_registration_without_advanced_fields_and_fifth_ignored():
    root=json.loads((ROOT/'config/frb_launch_sample_data_v0_1.json').read_text('utf8'))
    draft=copy.deepcopy(root)
    for row in draft['items']:
        row.pop('shuriken_enabled',None)
        row.pop('shuriken_direction',None)
        row.pop('shuriken_button_index',None)
    candidates = [r for r in draft['items'] if r['item_kind']=='command' and r.get('launch_actions')]
    for idx, row in enumerate(candidates[:6]):
        row['shuriken_enabled']=True
        row['shuriken_order']=idx*10
    validate(draft)
    entries=configured_entries(draft,1)
    assert len(entries)==4
    assert [e.direction for e in entries]==['up','right','down','left']
    assert [e.item_id for e in entries]==[r['item_id'] for r in candidates[:4]]
    assert choose_entry(entries,0,-50).item_id==candidates[0]['item_id']
    assert choose_entry(entries,-50,0).item_id==candidates[3]['item_id']


def test_studio_viewdef_exposes_first_hand_in_item_details():
    studio=ROOT/'defs/launch/frb_launch_maintenance_view_def_v0_1.json'
    definition=json.loads(studio.read_text('utf8'))
    fields=definition['views'][0]['sections'][1]['fields']
    names={r['field']:r for r in fields}
    assert names['shuriken_enabled']['edit']['visible'] is True
    assert names['shuriken_order']['type']=='number'
    assert 'shuriken_direction' not in names
    assert names['shuriken_only']['visibleWhen']['equals'] is True
