import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, '../../..');
const runtimeCode = fs.readFileSync(path.join(root, 'wwwroot/js/runtime/studio_json_round_trip.js'), 'utf8');

function getByPath(obj, pathName) {
  if (!pathName || pathName === '$') return obj;
  const normalized = String(pathName).replace(/^\$\.?/, '');
  return normalized.split('.').reduce((cur, key) => cur == null ? undefined : cur[key], obj);
}
function setByPath(obj, pathName, value) {
  const normalized = String(pathName).replace(/^\$\.?/, '');
  const parts = normalized.split('.');
  let cur = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    if (!cur[parts[i]] || typeof cur[parts[i]] !== 'object') cur[parts[i]] = {};
    cur = cur[parts[i]];
  }
  cur[parts.at(-1)] = value;
}

function createRuntime({ gridOverride=null, rowOverride=null }={}) {
  const defaultGrid = {
    fields: [
      { field: 'id', type: 'text', readonly: true, edit: { visible: true, readonly: true } },
      { field: 'title', type: 'text', edit: { visible: true } },
      { field: 'memo', type: 'textarea', edit: { visible: true } },
      { field: 'verification_status', type: 'select', options: ['未確認', '確認済み', '対象外'], edit: { visible: true, control: 'radio' } },
      { field: 'tags', type: 'stringArray', edit: { visible: true, readonly: false } },
      {
        field: 'children',
        type: 'objectArray',
        edit: {
          visible: true,
          readonly: false,
          subGrid: {
            columns: [
              { field: 'name', type: 'text' },
              { field: 'status', type: 'select', options: ['OPEN', 'DONE'] }
            ]
          }
        }
      },
      // edit.visible=falseでもDetail下部の共通サブグリッドとして画面編集できる。
      { field: 'decision_log', type: 'objectArray', edit: { visible: false }, defaultValue: [] },
      // 専用の対象文脈Gridとして画面編集できる。
      { field: 'context_refs', type: 'objectArray', contextRole: 'targetContext', edit: { visible: false }, defaultValue: [] },
      { field: 'latest_user_comment', type: 'textarea', edit: { visible: false } },
      { field: 'internal_hidden', type: 'textarea', edit: { visible: false } },
      { field: 'hidden_source', type: 'textarea', edit: { visible: false } },
      {
        field: '__chat', type: 'chat', edit: {
          visible: true,
          messages: [
            { field: 'hidden_source', readonly: false },
            { field: 'ai_note', readonly: true }
          ],
          input: {
            enabled: true,
            userField: 'latest_user_comment',
            aiField: 'ai_note'
          }
        }
      }
    ]
  };
  const grid = gridOverride ?? defaultGrid;
  const defaultRow = {
    id: 'r1', title: 'Before', memo: 'old', verification_status: '未確認', tags: ['a'],
    children: [{ name: 'one', score: 1 }],
    decision_log: [{ decision: 'before decision', reason: 'before reason' }],
    context_refs: [{ context_ref_id: 'ctx_before', title: 'before context' }],
    latest_user_comment: 'before comment',
    internal_hidden: 'must stay hidden',
    hidden_source: 'chat value', ai_note: 'readonly ai'
  };
  const detailDialog = {
    querySelectorAll: () => [],
    querySelector: () => null
  };
  const diffBadge = {
    textContent: '', title: '', classList: { add(){}, remove(){} }, removeAttribute(){}
  };
  const context = {
    console,
    window: {},
    document: { querySelectorAll: () => [] },
    navigator: {},
    detailMode: 'edit',
    draftRow: null,
    selectedIndex: 0,
    currentRows: [rowOverride ?? defaultRow],
    gridDef: () => grid,
    cloneData: value => value == null ? value : JSON.parse(JSON.stringify(value)),
    getByPath,
    setByPath,
    isDetailSubGridEditable: field => !field.readonly && !field.edit?.readonly,
    applyDetailInputsToRow: row => {
      if (!context.latestUiPatch) return;
      Object.entries(context.latestUiPatch).forEach(([pathName, value]) => setByPath(row, pathName, value));
    },
    renderDetailForRow: row => { context.lastRenderedRow = JSON.parse(JSON.stringify(row)); },
    setStatus: message => { context.lastStatus = message; },
    $: id => id === 'detailDialog' ? detailDialog : id === 'studioJsonRoundTripDiff' ? diffBadge : null,
    CSS: { escape: value => String(value) },
    setTimeout,
    structuredClone
  };
  context.window = context;
  vm.createContext(context);
  vm.runInContext(runtimeCode, context, { filename: 'studio_json_round_trip.js' });
  return context;
}

test('Copy JSON emits ViewDef detail fields, chat source fields, and subgrids', () => {
  const runtime = createRuntime();
  const copied = runtime.buildStudioDetailRoundTripJson();
  assert.deepEqual(JSON.parse(JSON.stringify(copied)), {
    id: 'r1',
    title: 'Before',
    memo: 'old',
    verification_status: '未確認',
    tags: ['a'],
    children: [{ name: 'one', score: 1 }],
    decision_log: [{ decision: 'before decision', reason: 'before reason' }],
    context_refs: [{ context_ref_id: 'ctx_before', title: 'before context' }],
    hidden_source: 'chat value',
    ai_note: 'readonly ai',
    latest_user_comment: 'before comment'
  });
});

test('Paste JSON applies partial editable fields and subgrids but skips readonly fields', () => {
  const runtime = createRuntime();
  const result = runtime.applyStudioDetailRoundTripObject({
    id: 'blocked',
    title: 'After',
    tags: ['x', 'y'],
    children: [{ name: 'two', score: 2 }],
    decision_log: [{ decision: 'AI decision', reason: 'AI reason' }],
    context_refs: [{ context_ref_id: 'ctx_after', title: 'after context' }],
    latest_user_comment: 'AI added comment',
    internal_hidden: 'must be ignored',
    ai_note: 'blocked ai'
  });
  assert.deepEqual(JSON.parse(JSON.stringify(result.changes)), [
    'title', 'tags', 'children', 'decision_log', 'context_refs', 'latest_user_comment'
  ]);
  assert.deepEqual(JSON.parse(JSON.stringify(result.readonlyPaths)), ['id', 'ai_note']);
  assert.equal(runtime.lastRenderedRow.id, 'r1');
  assert.equal(runtime.lastRenderedRow.title, 'After');
  assert.deepEqual(runtime.lastRenderedRow.tags, ['x', 'y']);
  assert.deepEqual(runtime.lastRenderedRow.children, [{ name: 'two', score: 2 }]);
  assert.deepEqual(runtime.lastRenderedRow.decision_log, [{ decision: 'AI decision', reason: 'AI reason' }]);
  assert.deepEqual(runtime.lastRenderedRow.context_refs, [{ context_ref_id: 'ctx_after', title: 'after context' }]);
  assert.equal(runtime.lastRenderedRow.latest_user_comment, 'AI added comment');
  assert.equal(runtime.lastRenderedRow.internal_hidden, 'must stay hidden');
  assert.equal(runtime.lastRenderedRow.ai_note, 'readonly ai');
  assert.match(runtime.lastStatus, /F12/);
});

test('Paste JSON includes editable arrays even when edit.visible=false and chat composer userField', () => {
  const runtime = createRuntime();
  runtime.applyStudioDetailRoundTripObject({
    decision_log: [{ decision: 'keyField must be unique', reason: 'identity integrity' }],
    context_refs: [{ context_ref_id: 'ctx_keyfield', title: 'keyField contract' }],
    latest_user_comment: 'AIと往復した追記'
  });

  const draft = runtime.getStudioJsonRoundTripDraftRow();
  assert.deepEqual(draft.decision_log, [{ decision: 'keyField must be unique', reason: 'identity integrity' }]);
  assert.deepEqual(draft.context_refs, [{ context_ref_id: 'ctx_keyfield', title: 'keyField contract' }]);
  assert.equal(draft.latest_user_comment, 'AIと往復した追記');
});

test('Copy/Paste JSON excludes hidden scalar fields that have no screen input UI', () => {
  const runtime = createRuntime();
  const copied = runtime.buildStudioDetailRoundTripJson();
  assert.equal(Object.prototype.hasOwnProperty.call(copied, 'internal_hidden'), false);

  runtime.applyStudioDetailRoundTripObject({ internal_hidden: 'attempted overwrite' });
  assert.equal(runtime.currentRows[0].internal_hidden, 'must stay hidden');
});

test('actual incident ViewDef accepts decision_log through Paste JSON although edit.visible=false', () => {
  const viewDef = JSON.parse(fs.readFileSync(
    path.join(root, 'wwwroot/defs/json/rules/studio_work_incident_view_def_v0_5.json'),
    'utf8'
  ));
  const incidentGrid = viewDef.views[0].sections.find(section => section.id === 'work_items');
  const runtime = createRuntime({
    gridOverride: incidentGrid,
    rowOverride: {
      work_item_id: 'studio_work_0156',
      status: '構想',
      verification_status: '未確認',
      decision_log: [],
      discussion_history: [],
      change_history: [],
      follow_up_actions: []
    }
  });

  runtime.applyStudioDetailRoundTripObject({
    decision_log: [{
      decision_id: 'decision_keyfield_identity_contract_001',
      decision: 'keyFieldは対象Grid内で一意とする',
      applied_axes: [{ axis_id: 'identity_integrity', priority: 'high' }]
    }]
  });

  const draft = runtime.getStudioJsonRoundTripDraftRow();
  assert.equal(draft.decision_log.length, 1);
  assert.equal(draft.decision_log[0].decision_id, 'decision_keyfield_identity_contract_001');
  assert.deepEqual(draft.decision_log[0].applied_axes, [{ axis_id: 'identity_integrity', priority: 'high' }]);
});

test('actual incident ViewDef accepts UI_IMPROVEMENT in follow_up_actions through Paste JSON', () => {
  const viewDef = JSON.parse(fs.readFileSync(
    path.join(root, 'defs/rules/studio_work_incident_view_def_v0_5.json'),
    'utf8'
  ));
  const incidentGrid = viewDef.views[0].sections.find(section => section.id === 'work_items');
  const runtime = createRuntime({
    gridOverride: incidentGrid,
    rowOverride: {
      work_item_id: 'studio_work_0159',
      status: '完了',
      verification_status: '確認済み',
      decision_log: [],
      discussion_history: [],
      change_history: [],
      follow_up_actions: []
    }
  });

  runtime.applyStudioDetailRoundTripObject({
    follow_up_actions: [{
      action_id: 'follow_up_0159_001',
      action_type: 'UI_IMPROVEMENT',
      required: true,
      status: 'COMPLETED',
      related_ids: ['studio_work_0159', 'detailDialog'],
      note: '詳細Editorの表示改善'
    }]
  });

  const draft = runtime.getStudioJsonRoundTripDraftRow();
  assert.equal(draft.follow_up_actions.length, 1);
  assert.equal(draft.follow_up_actions[0].action_type, 'UI_IMPROVEMENT');
});

test('Paste JSON rejects invalid subgrid shapes atomically', () => {
  const runtime = createRuntime();
  assert.throws(
    () => runtime.applyStudioDetailRoundTripObject({ children: ['not-object'] }),
    /children\[0\]: オブジェクト/
  );
  assert.equal(runtime.lastRenderedRow, undefined);
});


test('Paste JSON validates select values inside objectArray subgrids', () => {
  const runtime = createRuntime();
  assert.throws(
    () => runtime.applyStudioDetailRoundTripObject({
      children: [{ name: 'bad child', status: 'DEFERRED' }]
    }),
    /children\[0\]\.status.*DEFERRED.*許可された選択肢.*OPEN.*DONE/
  );
  assert.equal(runtime.lastRenderedRow, undefined);
});

test('Paste JSON keeps chat/card fields in a pending draft until F12 consumption', () => {
  const runtime = createRuntime();
  runtime.applyStudioDetailRoundTripObject({
    title: 'After',
    hidden_source: 'AI generated card text'
  });

  // Paste直後は実データを変更しない。
  assert.equal(runtime.currentRows[0].title, 'Before');
  assert.equal(runtime.currentRows[0].hidden_source, 'chat value');

  const draft = runtime.getStudioJsonRoundTripDraftRow();
  assert.equal(draft.title, 'After');
  assert.equal(draft.hidden_source, 'AI generated card text');

  // F12側がconsumeした行には、contenteditable=falseのMarkdownカード値も残る。
  const committed = runtime.consumeStudioJsonRoundTripDraft();
  assert.equal(committed.title, 'After');
  assert.equal(committed.hidden_source, 'AI generated card text');
  assert.equal(runtime.getStudioJsonRoundTripDraftRow(), null);
});


test('Paste JSON keeps manual edits made after paste when F12 consumes the working row', () => {
  const runtime = createRuntime();
  runtime.applyStudioDetailRoundTripObject({
    title: 'AI pasted title',
    children: [{ name: 'AI child', score: 2 }]
  });

  // Paste後に人間が通常項目とサブグリッドを修正した状態を再現する。
  runtime.latestUiPatch = {
    title: 'Human corrected title',
    children: [{ name: 'Human child', score: 3 }]
  };

  const committed = runtime.consumeStudioJsonRoundTripDraft();
  assert.equal(committed.title, 'Human corrected title');
  assert.deepEqual(committed.children, [{ name: 'Human child', score: 3 }]);
});

test('Paste JSON rejects values outside ViewDef select/radio options', () => {
  const runtime = createRuntime();
  assert.throws(
    () => runtime.applyStudioDetailRoundTripObject({ verification_status: '確認済' }),
    /確認済.*許可された選択肢.*確認済み/
  );
  assert.equal(runtime.lastRenderedRow, undefined);
});

