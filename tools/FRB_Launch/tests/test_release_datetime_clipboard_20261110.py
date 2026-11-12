"""Release regression: authored date/time command uses the existing Expander."""
import sys
import unittest
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from core import Expander, load, validate


class DateTimeClipboardCommandTests(unittest.TestCase):
    def test_current_datetime_entry_and_output(self):
        data = load(ROOT / 'config/frb_launch_data.json')
        row = next(r for r in data['items'] if r['item_id'] == 'today_datetime')
        self.assertEqual(row['parent_item_id'], 'dates')
        self.assertEqual(row['page_id'], 'work')
        self.assertEqual(row['title'], '今日の日時 yyyyMMdd_hhmmss')
        self.assertEqual(row['launch_actions'][0]['launch_action_type'], 'ClipboardCopy')
        self.assertEqual(row['launch_actions'][0]['launch_text'], '%now:yyyyMMdd_HHmmss%')
        now = datetime(2026, 11, 10, 7, 23, 3)
        self.assertEqual(Expander(data, now=now).expand(row['launch_actions'][0]['launch_text']),
                         '20261110_072303')

    def test_no_duplicate_items_and_original_today_unchanged(self):
        data = load(ROOT / 'config/frb_launch_data.json')
        self.assertEqual(len(data['items']), 80)
        self.assertEqual(len({i['item_id'] for i in data['items']}), 80)
        self.assertEqual(next(i for i in data['items'] if i['item_id'] == 'today')['launch_actions'][0]['launch_text'],
                         '%today:yyyy/MM/dd%')
        self.assertIs(validate(data),data)

if __name__ == '__main__':
    unittest.main()
