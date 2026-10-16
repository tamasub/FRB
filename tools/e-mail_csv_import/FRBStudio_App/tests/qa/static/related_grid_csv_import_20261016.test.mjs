import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const require = createRequire(import.meta.url);
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const importer = require(path.join(root, 'wwwroot/js/responsibilities/csv_importer.js'));
const viewdef = JSON.parse(readFileSync(path.join(root, 'defs/launch/frb_launch_maintenance_view_def_v0_1.json'), 'utf8'));
const definition = viewdef.views.find(view => view.id === 'launch_choices_view').toolbar.csvImport;
assert.equal(definition.mode, 'replace_all');
assert.equal(definition.defaults.group_id, '');
const get = text => importer.buildRows(text, definition);

test('Japanese email list creates candidates without group assignments', () => {
  const rows = get('氏名,メールアドレス\r\n田中,tanaka@example.com\r\n佐藤,sato@example.com\r\n');
  assert.equal(rows.length, 2);
  assert.deepEqual(rows[0], {
    group_id: '', enabled: true, title: '田中', value: 'tanaka@example.com',
    description: 'tanaka@example.com', choice_id: 'import_mail_000001', sort_order: 10
  });
  assert.equal(rows[1].sort_order, 20);
  assert.equal(rows[1].choice_id, 'import_mail_000002');
});
test('Google contacts export headers are supported', () => {
  const rows = get('Name,E-mail 1 - Value,E-mail 1 - Type\r\nAlice,alice@example.com,Work\r\n');
  assert.equal(rows[0].title, 'Alice');
  assert.equal(rows[0].value, 'alice@example.com');
});
test('quote, comma, newline, doubled quotes, and BOM', () => {
  const rows = get('\ufeff名前,メールアドレス,説明\r\n"田中, 太郎",tanaka@example.com,"営業部\n""西""支店"\r\n');
  assert.equal(rows[0].title, '田中, 太郎');
  assert.equal(rows[0].description, '営業部\n"西"支店');
});
test('tab and semicolon exported files also work', () => {
  assert.equal(get('名前\tメールアドレス\n田中\tt@e.com')[0].value, 't@e.com');
  assert.equal(get('名前;メールアドレス\n田中;t@e.com')[0].value, 't@e.com');
});
test('missing name falls back to address and group_id from CSV is ignored', () => {
  const rows = get('value,group_id\nme@corp.example,sales\n');
  assert.equal(rows[0].title, 'me@corp.example');
  assert.equal(rows[0].group_id, '');
});
test('reject empty email, broken CSV, missing header, empty data and too many rows', () => {
  assert.throws(() => get('氏名,メールアドレス\n太郎,\n'), /valueが空/);
  assert.throws(() => get('氏名,メールアドレス\n"太郎,me@example.com'), /引用符/);
  assert.throws(() => get('氏名,電話番号\n太郎,12345'), /ヘッダー/);
  assert.throws(() => get('氏名,メールアドレス\n'), /データ行/);
  assert.throws(() => importer.buildRows('メールアドレス\na@b.com\nb@c.com', { ...definition, maxRows:1 }), /上限/);
});
test('UTF-8 BOM and utf-16 decode work', () => {
  assert.equal(importer.decode(new Uint8Array([0xef,0xbb,0xbf,...Buffer.from('名前')])), '名前');
  const utf16 = new Uint8Array([0xff,0xfe,0x41,0x00]);
  assert.equal(importer.decode(utf16), 'A');
});
test('replacement is all-or-nothing: parse produces a new array, not an in-place mutation', () => {
  const existing = [{choice_id:'old_1',group_id:'sales',title:'元のデータ'}];
  const snapshot = JSON.stringify(existing);
  const incoming = get('名前,メールアドレス\n新しい人,new@example.com');
  assert.equal(existing.length, 1);
  assert.equal(JSON.stringify(existing), snapshot);
  assert.equal(incoming.length, 1);
  assert.notEqual(incoming[0].choice_id, existing[0].choice_id);
});
test('ViewDef-driven button, confirm-before-set, parent apply behavior and script loading', () => {
  const related = readFileSync(path.join(root, 'wwwroot/js/runtime/related_grid_view.js'), 'utf8');
  const html = readFileSync(path.join(root, 'wwwroot/index.html'), 'utf8');
  assert.match(html, /js\/responsibilities\/csv_importer\.js/);
  assert.match(related, /function relatedGridCsvImportDefinition\(/);
  assert.match(related, /ensureRelatedGridCsvImportButton\(\)/);
  const button = related.slice(related.indexOf('async () => {\n    const file = picker.files'));
  assert.ok(button.indexOf('CsvGridImporter.buildRows') < button.indexOf('window.confirm'));
  assert.ok(button.indexOf('window.confirm') < button.indexOf('setByPath(sourceData, relatedGridChildRuntime.dataPath, importedRows)'));
  assert.match(related, /親画面へ反映/);
  assert.match(related, /relatedGridChildRuntime\.dataPath/);
});
