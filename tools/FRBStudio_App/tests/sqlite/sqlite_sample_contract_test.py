"""Pure fixture/schema tests; not a C# adapter integration test."""
import json
import sqlite3
from pathlib import Path

root=Path(__file__).resolve().parents[2]
config_path=root/'data/json/90_samples/sqlite_sample_master_data_v0_1.json'
data=json.loads(config_path.read_text(encoding='utf-8'))
view=json.loads((root/'defs'/data['view_def']).read_text(encoding='utf-8'))
assert data['data_source']['type']=='sqlite'
assert data['data_source']['access_mode']=='read_write'
assert len(data['data_source']['tables'])==2
assert len(view['views'][0]['sectionGroups'])==2
assert {x['id'] for x in view['views'][0]['sections']}=={'employee_grid','department_grid'}
for mapping in data['data_source']['tables']:
    assert mapping['load']['limit']==100
    assert mapping['load']['on_open'] is True
    assert any(s['dataPath']==mapping['data_path'] for s in view['views'][0]['sections'])
con=sqlite3.connect(root/data['data_source']['database_path'])
assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
for mapping in data['data_source']['tables']:
    table=mapping['table']
    cols=list(con.execute(f'pragma table_info("{table}")'))
    assert len([c for c in cols if c[5] > 0])==1,table
    assert con.execute(f'select count(*) from "{table}"').fetchone()[0]>0
# Make a copy in RAM: exercise SQLite update + rollback without modifying the shipped DB.
ram=sqlite3.connect(':memory:'); con.backup(ram);con.close()
orig=ram.execute('select employee_name from employees where employee_id=1001').fetchone()[0]
ram.execute('begin');ram.execute('update employees set employee_name=? where employee_id=?',('テスト',1001));assert ram.execute('select employee_name from employees where employee_id=1001').fetchone()[0]=='テスト';ram.rollback()
assert ram.execute('select employee_name from employees where employee_id=1001').fetchone()[0]==orig
print('PASS fixture + 2 PK tables + JSON/ViewDef map + SQLite transaction rollback')
