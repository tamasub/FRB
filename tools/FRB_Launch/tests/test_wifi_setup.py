import unittest
from pathlib import Path
from unittest.mock import patch
import test_navigation
from core import load,Expander
from prepare_launch_home import repair_wifi
import app as module

ROOT=Path(__file__).resolve().parents[1]
class WifiSetupTests(unittest.TestCase):
    def test_fft_sequence_and_packaged_script(self):
        d=repair_wifi(load(ROOT/'config/frb_launch_sample_data_v0_1.json'))
        items={r['item_id']:r for r in d['items']}
        for id in ['fft','cam','wifi_home']:
            step=items[id]['launch_actions'][0]
            self.assertTrue(step['launch_wait_for_exit'])
            self.assertTrue(step['launch_show_console'])
            self.assertGreater(step['launch_timeout_ms'],30000)
            self.assertIn('%launch_scripts%\\Connect-Wifi.ps1',step['launch_arguments'])
        ex=Expander(d,values={'launch_scripts':str(ROOT/'scripts')})
        args=[ex.expand(a) for a in items['fft']['launch_actions'][0]['launch_arguments']]
        self.assertEqual(args[args.index('-ProfileName')+1],next(v['launch_value'] for v in d['launch_variables'] if v['variable_id']=='fft_wifi_profile'))
        self.assertEqual(args[args.index('-ProbeUrl')+1],'http://192.168.4.1')
        self.assertTrue((ROOT/'scripts/Connect-Wifi.ps1').is_file())
        self.assertNotIn('xcopy /E /I /Y scripts',(ROOT/'build_windows.bat').read_text())
        if 'wifi_profiles' in items:self.assertFalse(items['wifi_profiles']['launch_actions'][0]['launch_wait_for_exit'])

class WifiFailureTests(test_navigation.NavigationTests):
    test_immediate_right_and_left=None
    test_nested_and_directory_single_column=None
    test_function_page_keys=None
    test_selection_all_clear_and_back=None
    def test_connection_failure_stops_browser(self):
        self.w.busy=True
        self.w.queue=[{'launch_action_type':'Open','launch_target':'http://192.168.4.1','launch_browser':'chrome'}]
        self.w.timedout=False
        class Failed:
            def poll(self):return 1
        self.w.proc=Failed()
        from PySide6.QtCore import QTimer
        self.w.process_timer=QTimer(self.w)
        with patch.object(self.w,'open_target') as opened,patch.object(self.w,'error') as error:
            self.w.poll_process()
            self.assertFalse(self.w.busy)
            self.assertEqual(self.w.queue,[])
            opened.assert_not_called();error.assert_called_once()
