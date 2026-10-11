import unittest,base64,tempfile,logging
from pathlib import Path
from launch_diagnostics import wifi_transcript_arguments,make_logger

class DiagnosticsTests(unittest.TestCase):
    def test_wrap_preserves_host_options_and_quotes_script_parameters(self):
        with tempfile.TemporaryDirectory() as folder:
            source=['-NoProfile','-ExecutionPolicy','Bypass','-File',r"F:\FRB's tools\scripts\Connect-Wifi.ps1",'-ProfileName',"CAM's Wifi",'-ProbeUrl','http://192.168.4.1']
            args,log=wifi_transcript_arguments('powershell.exe',source,folder)
            self.assertEqual(args[:3],source[:3])
            self.assertEqual(args[3],'-EncodedCommand')
            command=base64.b64decode(args[4]).decode('utf-16le')
            self.assertIn('Start-Transcript',command)
            self.assertLess(command.index('Start-Transcript'),command.index('& '))
            self.assertIn("'F:\\FRB''s tools\\scripts\\Connect-Wifi.ps1'",command)
            self.assertIn("'CAM''s Wifi'",command)
            self.assertIn('@scriptArgs',command)
            self.assertIn("'ProfileName'='CAM''s Wifi'",command)
            self.assertIn('$scriptArgs = @{',command)
            self.assertIn('exit 1',command)
            self.assertEqual(log.parent,Path(folder))
            self.assertEqual(source[3],'-File')
    def test_does_not_wrap_other_scripts_or_commands(self):
        for program,args in [('cmd.exe',['/c','hello.bat']),('powershell.exe',['-File','Other.ps1'])]:
            result,log=wifi_transcript_arguments(program,args,'.')
            self.assertEqual(result,args);self.assertIsNone(log)
    def test_logging_persists_events(self):
        with tempfile.TemporaryDirectory() as folder:
            logger=make_logger(folder);logger.info('PROCESS exited code=1')
            self.assertIn('PROCESS exited code=1',(Path(folder)/'launch.log').read_text())
            for h in logger.handlers[:]:
                if getattr(h,'baseFilename','')==str(Path(folder)/'launch.log'):h.close();logger.removeHandler(h)
