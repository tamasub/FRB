import json,shutil,tempfile,unittest
from pathlib import Path
from runtime_paths import launch_home
from prepare_launch_home import prepare,link_build,CONFIG,READY
from make_launch_zip import make_zip

SOURCE=Path(__file__).resolve().parents[1]
class LaunchHomeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        (self.root/'config').mkdir();shutil.copy2(SOURCE/CONFIG,self.root/CONFIG)
    def tearDown(self):self.temp.cleanup()
    def test_migrate_active_dist_then_rebuild_never_restores_old_dist(self):
        legacy=self.root/'dist/FRBLaunch';(legacy/'config').mkdir(parents=True)
        data=json.loads((self.root/CONFIG).read_text());data['launch_variables'][0]['launch_value']='CURRENT_USER_SETTING'
        (legacy/CONFIG).write_text(json.dumps(data))
        (legacy/'scripts').mkdir();(legacy/'scripts/custom.ps1').write_text('user script')
        backup=prepare(self.root)
        self.assertTrue((backup/'source'/CONFIG).exists());self.assertTrue((backup/'previous_dist'/CONFIG).exists())
        migrated=json.loads((self.root/CONFIG).read_text())
        self.assertEqual(migrated['launch_variables'][0]['launch_value'],'CURRENT_USER_SETTING')
        self.assertEqual((self.root/'scripts/custom.ps1').read_text(),'user script')
        self.assertNotIn('launch_scripts',[v['variable_id'] for v in migrated['launch_variables']])
        cam=next(r for r in migrated['items'] if r['item_id']=='cam')['launch_actions'][0]
        self.assertTrue(cam['launch_show_console']);self.assertIn('%launch_scripts%\\Connect-Wifi.ps1',cam['launch_arguments'])
        # Simulate editing canonical data and a stale build folder being restored.
        migrated['launch_variables'][0]['launch_value']='NEW_CANONICAL_VALUE'
        (self.root/CONFIG).write_text(json.dumps(migrated));expected=(self.root/CONFIG).read_bytes()
        self.assertIsNone(prepare(self.root));self.assertEqual((self.root/CONFIG).read_bytes(),expected)
        shutil.rmtree(legacy);link_build(self.root)
        self.assertEqual(launch_home(legacy),self.root)
        self.assertEqual((self.root/CONFIG).read_bytes(),expected)
    def test_migration_does_not_replace_updated_system_scanner(self):
        legacy=self.root/'dist/FRBLaunch/scripts'
        legacy.mkdir(parents=True)
        (legacy/'Get-LaunchApps.ps1').write_text('OLD_SCANNER',encoding='utf-8')
        (legacy/'company_custom.ps1').write_text('CUSTOM_SCRIPT',encoding='utf-8')
        current=self.root/'scripts'
        current.mkdir()
        (current/'Get-LaunchApps.ps1').write_text('UPDATED_SCANNER',encoding='utf-8')
        prepare(self.root)
        self.assertEqual((current/'Get-LaunchApps.ps1').read_text(encoding='utf-8'),'UPDATED_SCANNER')
        self.assertEqual((current/'company_custom.ps1').read_text(encoding='utf-8'),'CUSTOM_SCRIPT')

    def test_missing_link_target_does_not_fall_back_to_stale_config(self):
        out=self.root/'dist/FRBLaunch';link_build(self.root)
        (self.root/CONFIG).unlink()
        with self.assertRaises(RuntimeError):launch_home(out)
    def test_standalone_no_marker_uses_local_folder(self):
        self.assertEqual(launch_home(self.root),self.root)
    def test_backup_contains_canonical_config_scripts_without_migration_flag(self):
        prepare(self.root);(self.root/'scripts').mkdir(exist_ok=True);(self.root/'scripts/test.ps1').write_text('test')
        import zipfile
        with zipfile.ZipFile(make_zip(self.root)) as z:
            self.assertIn(CONFIG.as_posix(),z.namelist());self.assertIn('scripts/test.ps1',z.namelist())
            self.assertNotIn(READY,z.namelist());self.assertFalse(any(p.startswith('backups/') for p in z.namelist()))
