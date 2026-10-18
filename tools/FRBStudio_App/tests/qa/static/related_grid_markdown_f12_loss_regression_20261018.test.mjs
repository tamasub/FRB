import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const source = file => fs.readFileSync(path.join(root, file), 'utf8');
const controls = source('wwwroot/js/renderers/field_controls.js');
const grid = source('wwwroot/js/renderers/grid_detail.js');
const detail = source('wwwroot/js/runtime/detail_save.js');

// Execute the actual production functions in isolation. A fake element mimics
// the real blur: contentEditable changes to false while data.rawValue contains
// the just-edited text.
function functionSource(js, name) {
  const start = js.indexOf(`function ${name}(`);
  assert.ok(start >= 0, `${name} must exist`);
  const end = js.indexOf('\n}', start);
  assert.ok(end >= 0, `${name} must terminate`);
  return js.slice(start, end + 2);
}

function testEditor({ readonly=false, success=true, raw=false }={}) {
  const canonical = { reason: '旧テキスト', id: 'axis-1' };
  const el = {
    dataset: { field:'reason', prefix:'detail', type:'textarea', markdownDisplay:'true',
      editMode:raw?'raw':'preview', rawValue:'新しいテキスト\n追記' },
    disabled: false,
    type: 'div',
    innerText:'新しいテキスト\n追記',
    classList:{ contains: name => name === 'readonly' && readonly },
    getAttribute: key => key === 'contenteditable' ? (raw?'true':'false') : null,
    hasAttribute: key => key === 'contenteditable'
  };
  const ctx = vm.createContext({
    el, canonical,
    currentRows:[canonical], selectedIndex:0, detailMode:'edit',
    detailVisibilityDraft:{ reason:'旧テキスト', id:'axis-1' },
    gridDef:() => ({fields:[{ field:'reason',type:'textarea',readonly }]}),
    detailEditableControls:() => [el],
    getByPath:(row,p)=>row[p],
    setByPath:(row,p,v)=>{row[p]=v;},
    convertValue:(_type,value)=>value,
    cloneData: value=>JSON.parse(JSON.stringify(value)),
    studioTreeProtect(){}, studioTreeValidateKind:()=>true,
    validatePendingDetailApplyRow:()=>({status:success?'ACCEPT':'REJECT'}),
    reportRuntimeFieldDefinitionValidationFailure(){},
    finalizeValidatedDetailCommit:(row,index)=>{Object.assign(ctx.currentRows[index],row);},
    queueRelatedGridAutoApply(){ctx.applies++;},
    applies:0,
    console
  });
  const functions = [
    functionSource(controls,'markdownPreviewRawValue'),
    functionSource(controls,'syncMarkdownRawToRow'),
    functionSource(grid,'getControlValue'),
    functionSource(grid,'isControlReadonly'),
    functionSource(grid,'applyDetailInputsToRow'),
    functionSource(detail,'buildPendingDetailApplyRow'),
    functionSource(detail,'tryCommitCurrentDetailEdits')
  ];
  vm.runInContext(functions.join('\n'),ctx);
  return ctx;
}

test('Mouse click F12: blurred Markdown Reading View remains writable, commits the latest text', () => {
  const ctx = testEditor();
  assert.equal(vm.runInContext('isControlReadonly(el)',ctx),false);
  vm.runInContext('syncMarkdownRawToRow(el,el.dataset.rawValue)',ctx);
  assert.equal(ctx.canonical.reason,'旧テキスト','blur must NOT mutate canonical sourceData');
  assert.equal(ctx.detailVisibilityDraft.reason,'新しいテキスト\n追記');
  assert.equal(vm.runInContext('tryCommitCurrentDetailEdits()',ctx),true);
  assert.equal(ctx.canonical.reason,'新しいテキスト\n追記');
  assert.equal(ctx.applies,1);
});

test('F12 key while raw editing commits the same value as mouse F12 after blur', () => {
  const ctx = testEditor({raw:true});
  assert.equal(vm.runInContext('tryCommitCurrentDetailEdits()',ctx),true);
  assert.equal(ctx.canonical.reason,'新しいテキスト\n追記');
});

test('Validation rejection keeps canonical unchanged even after Markdown blur', () => {
  const ctx=testEditor({success:false});
  vm.runInContext('syncMarkdownRawToRow(el,el.dataset.rawValue)',ctx);
  assert.equal(vm.runInContext('tryCommitCurrentDetailEdits()',ctx),false);
  assert.equal(ctx.canonical.reason,'旧テキスト');
  assert.equal(ctx.applies,0);
});

test('True readonly Markdown fields stay readonly, as do ordinary contenteditable=false elements', () => {
  const ctx=testEditor({readonly:true});
  assert.equal(vm.runInContext('isControlReadonly(el)',ctx),true);
  assert.equal(vm.runInContext('tryCommitCurrentDetailEdits()',ctx),true);
  assert.equal(ctx.canonical.reason,'旧テキスト');
  ctx.el.dataset.markdownDisplay='false';
  assert.equal(vm.runInContext('isControlReadonly(el)',ctx),true);
});

test('Repeated F12 edit cycles do not resurrect prior text after blur', () => {
  const ctx=testEditor();
  for(let i=0;i<25;i++) {
    const next=`本文-第${i}回\n行${i}`;
    ctx.el.dataset.rawValue=next;
    ctx.el.innerText=next;
    vm.runInContext('syncMarkdownRawToRow(el, el.dataset.rawValue)',ctx);
    assert.equal(vm.runInContext('tryCommitCurrentDetailEdits()',ctx),true);
    assert.equal(ctx.canonical.reason,next);
    // Reopened editor clones the most recently committed data.
    ctx.detailVisibilityDraft=JSON.parse(JSON.stringify(ctx.canonical));
  }
  assert.equal(ctx.applies,25);
});
