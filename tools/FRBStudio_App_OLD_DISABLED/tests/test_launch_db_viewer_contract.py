"""Contract checks for the FRB Launch SQLite viewer (no .NET build needed)."""
from pathlib import Path
import json, sqlite3, tempfile

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT/'data/json/90_samples/frb_launch_file_index_data_v0_1.json').read_text(encoding='utf8'))
VIEW = json.loads((ROOT/'defs/sqlite/frb_launch_file_index_view_def_v0_1.json').read_text(encoding='utf8'))
CONFIG = json.loads((ROOT/'NativeShell/native_shell.config.json').read_text(encoding='utf8'))
assert DATA['data_source']['access_mode']=='read_only'
assert DATA['data_source']['type']=='sqlite'
assert DATA['data_source']['database_path']=='%LOCALAPPDATA%\\FRBLaunch\\file_index.db'
assert CONFIG['sqlite_readonly_external_files']==[DATA['data_source']['database_path']]
assert DATA['view_def']=='sqlite/frb_launch_file_index_view_def_v0_1.json'
expected={'files':['path','name','name_fold','directory','extension','root_key'],
'index_roots':['root_key','root_path','digest','options_digest','checked_at','updated_at','count','excluded'],
'metadata':['key','value']}
sections = VIEW['views'][0]['sections']; groups=VIEW['views'][0]['sectionGroups']
assert len(sections)==len(groups)==3
assert all(all(f['readonly'] and f['edit']['readonly'] for f in s['fields']) for s in sections)
for index, m in enumerate(DATA['data_source']['tables']):
    assert m['table'] in expected and m['load']['limit'] in range(1,1001)
    assert sections[index]['dataPath']==m['data_path']
    assert sections[index]['keyField'] in expected[m['table']]
    assert {f['field'] for f in sections[index]['fields']}==set(expected[m['table']])

# Simulate the exact latest Launch schema from file_index.py and check table mapping.
with tempfile.TemporaryDirectory() as tmp:
    with sqlite3.connect(Path(tmp)/'file_index.db') as db:
        db.execute('CREATE TABLE files(path TEXT PRIMARY KEY COLLATE NOCASE, name TEXT NOT NULL, name_fold TEXT NOT NULL, directory TEXT NOT NULL, extension TEXT NOT NULL, root_key TEXT NOT NULL DEFAULT \'\')')
        db.execute('CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        db.execute('CREATE TABLE index_roots(root_key TEXT PRIMARY KEY, root_path TEXT NOT NULL, digest TEXT NOT NULL, options_digest TEXT NOT NULL, checked_at TEXT NOT NULL, updated_at TEXT NOT NULL, count INTEGER NOT NULL, excluded INTEGER NOT NULL)')
        db.execute('INSERT INTO files VALUES (?,?,?,?,?,?)',('F:\\FRB\\tools\\make.ps1','make.ps1','make.ps1','F:\\FRB\\tools','.ps1','f:\\'))
        db.execute('INSERT INTO metadata VALUES (?,?)',('count','1'))
        db.execute('INSERT INTO index_roots VALUES (?,?,?,?,?,?,?,?)',('f:\\','F:\\','a','b','2026-10-17','2026-10-17',1,0))
        for m in DATA['data_source']['tables']:
            name=m['table']; limit=m['load']['limit'];
            cols={x[1] for x in db.execute('PRAGMA table_info("'+name+'")')}
            assert cols==set(expected[name]), (name,cols)
            records=list(db.execute('SELECT * FROM "'+name+'" LIMIT ?', (limit+1,)))
            assert len(records)==1
# Whitelist and adapter checks (static, C# compiler not available in sandbox).
code = (ROOT/'NativeShell/SqliteDataAdapter.cs').read_text(encoding='utf8')
assert 'SqliteOpenMode.ReadOnly' in code
assert 'WORKSPACE_PATH_DENIED: SQLite external DB is not in native allowlist.' in code
assert 'SQLite data source is read-only.' in code
assert 'Connect(DatabaseFile(ds), false)' in code
cfg = (ROOT/'NativeShell/NativeShellConfig.cs').read_text(encoding='utf8')
assert 'SqliteReadOnlyExternalFiles' in cfg
assert 'sqlite_readonly_external_files' in cfg
print('PASS: 3 table mappings / schema / readonly / allowlist / query limit / generated JSON & ViewDef')
