import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from log_retention import cleanup, load_options, DEFAULTS


class RetentionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.now = time.time()
        self.options = self.root/'options.json'
        self.options.write_text(json.dumps(DEFAULTS),encoding='utf-8')

    def artifact(self, name, age_days):
        file = self.root/name
        file.write_text('original', encoding='utf-8')
        timestamp = self.now - age_days * 86400
        os.utime(file, (timestamp,timestamp))
        return file

    def test_prunes_independent_process_log_families_and_preserves_other_files(self):
        for kind in ('wifi','audio'):
            for n in range(15):
                self.artifact(f'{kind}_process_20261010_1010{n:02d}_{n:08x}.log',15-n/100)
        for name in ('launch.log','wifi.log','audio.log','error.log','file_index.db','search_history.json','unexpected.log'):
            self.artifact(name,20)
        counts = cleanup(self.root,self.options, now=self.now)
        self.assertEqual(counts['wifi_process'],10)
        self.assertEqual(counts['audio_process'],10)
        self.assertEqual(len(list(self.root.glob('wifi_process_*'))),5)
        self.assertEqual(len(list(self.root.glob('audio_process_*'))),5)
        for name in ('launch.log','wifi.log','audio.log','error.log','file_index.db','search_history.json','unexpected.log'):
            self.assertTrue((self.root/name).exists())
        self.assertFalse(any(cleanup(self.root,self.options,now=self.now).values()))

    def test_recent_transcripts_never_deleted_even_above_count_limit(self):
        for n in range(12):
            self.artifact(f'wifi_process_20261017_1010{n:02d}_{n:08x}.log',0.001)
        self.assertEqual(cleanup(self.root,self.options,now=self.now)['wifi_process'],0)
        self.assertEqual(len(list(self.root.glob('wifi_process_*'))),12)
        self.assertEqual(cleanup(self.root,self.options,now=self.now+700)['wifi_process'],7)

    def test_audio_config_backups_strictly_keep_newest_five_even_if_all_recent(self):
        # Matches the user's case: 15 backups created during the last week.
        files = [self.artifact(
            f'audio_config_20261017_1010{n:02d}_{n:032x}.json',
            1.0 - n / 100.0) for n in range(15)]
        counts = cleanup(self.root,self.options,now=self.now)
        self.assertEqual(counts['audio_config'],10)
        self.assertEqual(set(self.root.glob('audio_config_*')), set(files[-5:]))
        self.assertEqual(cleanup(self.root,self.options,now=self.now)['audio_config'],0)
        self.artifact('audio_config_20261017_120000_'+'f'*32+'.json',0)
        self.assertEqual(cleanup(self.root,self.options,now=self.now)['audio_config'],1)
        self.assertEqual(len(list(self.root.glob('audio_config_*'))),5)

    def test_audio_config_legacy_age_option_no_longer_prevents_count_limit(self):
        # Older options files can contain the now-obsolete protection window.
        self.options.write_text(json.dumps({
            'audio_config_backups_keep':5,
            'audio_config_backups_min_age_days':7,
        }),encoding='utf-8')
        for n in range(8):
            self.artifact(f'audio_config_20261017_1010{n:02d}_{n:032x}.json',0.1 - n / 1000)
        self.assertEqual(cleanup(self.root,self.options,now=self.now)['audio_config'],3)
        self.assertEqual(len(list(self.root.glob('audio_config_*'))),5)

    def test_only_exact_generated_names_qualify(self):
        for name in ('wifi_process_custom.log','wifi_process_20261010_120000_bad.log',
                     'audio_config_20261010_120000_a.json','audio_process_20261010_120000_aaaaaaaa.log.lock'):
            self.artifact(name,100)
        self.assertFalse(any(cleanup(self.root,self.options,now=self.now).values()))
        self.assertEqual(len(list(self.root.iterdir())),5)  # + options.json

    def test_disabled_policy_does_not_delete(self):
        self.options.write_text(json.dumps({'enabled':False}), encoding='utf-8')
        for n in range(15):
            self.artifact(f'wifi_process_20261010_1010{n:02d}_{n:08x}.log',30)
        self.assertFalse(any(cleanup(self.root,self.options,now=self.now).values()))
        self.assertEqual(len(list(self.root.glob('wifi_process_*'))),15)

    def test_invalid_policy_rejected_and_missing_file_uses_defaults(self):
        self.assertEqual(load_options(self.root/'missing.json'),DEFAULTS)
        self.options.write_text(json.dumps({'audio_config_backups_keep':-1}),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'audio_config_backups_keep'):
            load_options(self.options)


if __name__ == '__main__':
    unittest.main()
