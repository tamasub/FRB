import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const read = p => fs.readFileSync(p, 'utf8');
const config = JSON.parse(read('NativeShell/native_shell.config.json'));
const cfgSource = read('NativeShell/NativeShellConfig.cs');
const adapter = read('NativeShell/SqliteDataAdapter.cs');
const dispatcher = read('NativeShell/NativeCommandDispatcher.cs');

test('external database directories are opt-in and disabled by default', () => {
  assert.deepEqual(config.sqlite_readonly_external_directories, []);
  assert.deepEqual(config.sqlite_readwrite_external_directories, []);
  assert.ok(config.sqlite_readonly_external_files.includes('%LOCALAPPDATA%\\FRBLaunch\\file_index.db'));
});

test('NativeShell loads and passes both directory policies into SQLite adapter', () => {
  for (const key of ['sqlite_readonly_external_directories','sqlite_readwrite_external_directories']) {
    assert.ok(cfgSource.includes(key));
  }
  for (const field of ['SqliteReadOnlyExternalDirectories','SqliteReadWriteExternalDirectories']) {
    assert.ok(cfgSource.includes(field));
    assert.ok(dispatcher.includes('_config.' + field));
  }
});

test('SQLite uses boundary-aware directory prefix and blocks reparse escapes', () => {
  assert.match(adapter, /directory \+ Path\.DirectorySeparatorChar/);
  assert.match(adapter, /filePath\.StartsWith\(prefix, StringComparison\.OrdinalIgnoreCase\)/);
  assert.match(adapter, /FileAttributes\.ReparsePoint/);
  assert.match(adapter, /EnsureNoExternalReparsePoints\(full\)/);
  const d = path.win32;
  const isUnder = (file, root) => file.toLowerCase().startsWith((root.endsWith('\\') ? root : root+'\\').toLowerCase());
  assert.ok(isUnder(d.normalize('F:\\DB\\sub\\a.db'), 'F:\\DB'));
  assert.ok(!isUnder(d.normalize('F:\\DB_Backup\\a.db'), 'F:\\DB'));
  assert.ok(!isUnder(d.normalize('F:\\DB\\..\\escape\\a.db'), 'F:\\DB'));
});

test('read_write is not enabled by read-only file or directory allowlists', () => {
  assert.match(adapter, /if \(wantsWrite && !directoryGrantsWrite\)/);
  assert.match(adapter, /if \(!wantsWrite && !_externalReadOnlyFiles\.Contains\(full\) && !directoryGrantsRead\)/);
  assert.match(adapter, /sqlite_readwrite_external_directories in NativeShell\/native_shell\.config\.json/);
  assert.match(adapter, /SQLite external DB is not in native allowlist/);
  assert.match(adapter, /Path\.IsPathRooted\(expanded\)/);
  assert.match(adapter, /path\.EndsWith\("\.db"/); // .db guard comes before external resolution
});
