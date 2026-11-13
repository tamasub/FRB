import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from apps_scan_support import append_apps_log, scan_shortcuts, merge_catalog, shortcut_roots
from process_runner import start_process


class CompanyAppsScanTests(unittest.TestCase):
    def test_log_created_before_powershell_and_records_failures(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'FRBLaunch'/'apps.log'
            self.assertTrue(append_apps_log(p,'SCAN_START'))
            self.assertTrue(append_apps_log(p,'POWERSHELL_LAUNCH_FAILED','code 1\naccess denied'))
            text=p.read_text(encoding='utf-8')
            self.assertIn('SCAN_START',text)
            self.assertIn('access denied',text)
            self.assertNotIn('code 1\naccess denied',text)  # single-line log record

    def test_find_start_menu_links_with_no_powershell_or_com(self):
        with tempfile.TemporaryDirectory() as d:
            roaming=Path(d)/'roaming'
            common=Path(d)/'common'
            u=roaming/'Microsoft'/'Windows'/'Start Menu'/'Programs'/'Tools'
            c=common/'Microsoft'/'Windows'/'Start Menu'/'Programs'
            u.mkdir(parents=True);c.mkdir(parents=True)
            (u/'Word.lnk').write_text('');(u/'README.txt').write_text('')
            (c/'Excel.LNK').write_text('');(c/'Uninstall Tool.lnk').write_text('')
            records,warnings=scan_shortcuts({'APPDATA':str(roaming),'PROGRAMDATA':str(common)})
            self.assertEqual(len(records),3)
            names={r['name'] for r in records}
            self.assertEqual(names,{'Word','Excel','Uninstall Tool'})
            self.assertEqual(warnings,[])
            self.assertTrue(all(r['kind']=='shortcut' for r in records))

    def test_inaccessible_folder_does_not_discard_other_folder(self):
        with tempfile.TemporaryDirectory() as d:
            common=Path(d)/'common'
            root=common/'Microsoft'/'Windows'/'Start Menu'/'Programs'
            root.mkdir(parents=True);(root/'Brave.lnk').write_text('')
            records,warnings=scan_shortcuts({'APPDATA':str(Path(d)/'missing'),'PROGRAMDATA':str(common)})
            self.assertEqual([r['name'] for r in records],['Brave'])
            self.assertEqual(len(warnings),1)

    def test_partial_keeps_old_aumids_but_filters_uninstall_shortcuts(self):
        old=[{'name':'Calculator','target':'calc.App','kind':'aumid'}]
        new=[{'name':'Word','target':r'C:\Word.lnk','kind':'shortcut'},
             {'name':'Uninstall Tool','target':r'C:\uninstall.lnk','kind':'shortcut'}]
        self.assertEqual(len(merge_catalog(old,new,partial=True)),2)
        self.assertEqual([r['name'] for r in merge_catalog(old,new,partial=False)],['Word'])

    def test_log_capture_for_subprocess_startup_errors(self):
        with tempfile.TemporaryDirectory() as d:
            logfile=Path(d)/'apps.log'
            append_apps_log(logfile,'SCAN_START')
            proc=start_process(sys.executable,['-c',"import sys; sys.stderr.write('process-diagnostic\\n'); sys.exit(2)"],d,False,log_path=logfile)
            self.assertEqual(proc.wait(timeout=5),2)
            data=logfile.read_text(encoding='utf-8')
            self.assertIn('SCAN_START',data)
            self.assertIn('process-diagnostic',data)

    def test_windows_process_failure_can_create_python_log(self):
        with tempfile.TemporaryDirectory() as d:
            logfile=Path(d)/'apps.log'
            try:
                start_process('unlikely-missing-powershell-cmd-9999999',[],d,False,log_path=logfile)
            except OSError as e:
                append_apps_log(logfile,'POWERSHELL_LAUNCH_FAILED',str(e))
            self.assertIn('POWERSHELL_LAUNCH_FAILED',logfile.read_text(encoding='utf-8'))


if __name__=='__main__': unittest.main()
