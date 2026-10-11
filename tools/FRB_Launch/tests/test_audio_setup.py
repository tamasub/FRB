import base64,json,tempfile,unittest
from pathlib import Path
from core import load,Expander
from launch_diagnostics import wifi_transcript_arguments

ROOT=Path(__file__).resolve().parents[1]
class AudioSetupTests(unittest.TestCase):
    def test_presets_can_start_before_device_ids_are_registered(self):
        data=load(ROOT/'config/frb_launch_sample_data_v0_1.json');items={r['item_id']:r for r in data['items']}
        ex=Expander(data,values={'launch_scripts':str(ROOT/'scripts'),'launch_data':str(ROOT/'config/frb_launch_sample_data_v0_1.json')})
        for id,var in [('speaker','speaker_device_id'),('earphone','earphone_device_id')]:
            step=items[id]['launch_actions'][0]
            args=[ex.expand(a) for a in step['launch_arguments']]
            self.assertEqual(args[args.index('-VariableId')+1],var)
            self.assertNotIn('-DeviceId',args)
            self.assertTrue(step['launch_wait_for_exit'])
            self.assertFalse(step['launch_show_console'])
        self.assertIn('-List',items['audio_list']['launch_actions'][0]['launch_arguments'])
        self.assertIn('-Choose',items['speaker_register']['launch_actions'][0]['launch_arguments'])
        self.assertTrue((ROOT/'scripts/AudioEndpoint.cs').is_file())
    def test_audio_transcript_passes_named_values_and_switches(self):
        with tempfile.TemporaryDirectory() as d:
            args,log=wifi_transcript_arguments('powershell.exe',['-NoProfile','-File',r'F:\scripts\Set-AudioOutput.ps1','-ConfigPath',r"F:\user's files\config.json",'-VariableId','speaker_device_id','-Choose'],d)
            text=base64.b64decode(args[-1]).decode('utf-16le')
            self.assertIn("'ConfigPath'='F:\\user''s files\\config.json'",text)
            self.assertIn("'VariableId'='speaker_device_id'",text)
            self.assertIn("'Choose'=$true",text)
            self.assertIn('audio_process_',log.name)
    def test_audio_missing_parameter_fails_before_start(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError,'Missing device argument value'):
                wifi_transcript_arguments('powershell.exe',['-File','Set-AudioOutput.ps1','-DeviceId'],folder)
