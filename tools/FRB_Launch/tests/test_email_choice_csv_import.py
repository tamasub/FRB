"""FRB Launch remains operable while imported mail candidates are ungrouped."""
import copy
import unittest
from pathlib import Path
from core import load, validate, searchable_rows

ROOT = Path(__file__).resolve().parents[1]

class CsvEmailChoiceTests(unittest.TestCase):
    def test_empty_candidate_group_during_csv_assignment_is_valid(self):
        data = copy.deepcopy(load(ROOT / 'config/frb_launch_sample_data_v0_1.json'))
        for i, row in enumerate(data['launch_choices']):
            row['choice_id'] = f'import_mail_{i+1:06d}'
            row['group_id'] = ''
        self.assertIs(validate(data), data)
        self.assertFalse(any(row['group_id'] == 'sales' for row in data['launch_choices']))
        self.assertFalse(any(row.get('_search_selection_owner') == 'sales'
                             for row, _ in searchable_rows(data, '田中')))
        # Group allocation is a separate action; once edited, validation still passes.
        data['launch_choices'][0]['group_id'] = 'sales'
        self.assertIs(validate(data), data)

    def test_duplicate_ids_remain_rejected(self):
        data = copy.deepcopy(load(ROOT / 'config/frb_launch_sample_data_v0_1.json'))
        data['launch_choices'][1]['choice_id'] = data['launch_choices'][0]['choice_id']
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            validate(data)

    def test_viewdef_declares_csv_only_on_candidate_grid(self):
        import json
        path = ROOT / 'defs/launch/frb_launch_maintenance_view_def_v0_1.json'
        definition = json.loads(path.read_text(encoding='utf-8'))
        views = {v['id']: v for v in definition['views']}
        assert views['launch_choices_view']['toolbar']['csvImport']['mode'] == 'replace_all'
        self.assertFalse('csvImport' in views['items_view'].get('toolbar', {}))

if __name__ == '__main__': unittest.main()
