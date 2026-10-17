// Run: node tests/sqlite/sqlite_error_translation_test.js
// Cross-layer regression: provider category -> native envelope -> UI translation.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '../..');
const get = relative => fs.readFileSync(path.join(root, relative), 'utf8');

(async () => {
  const window = {};
  vm.runInNewContext(get('wwwroot/js/runtime/sqlite_error_messages.js'), { window });
  const translate = window.FRBStudioSqliteErrorMessages.toUserMessage;
  const cases = [
    ['SQLITE_FOREIGN_KEY','DELETE','他のデータから参照されているため削除できません'],
    ['SQLITE_FOREIGN_KEY','INSERT','参照関係に矛盾'],
    ['SQLITE_UNIQUE','INSERT','すでに登録されています'],
    ['SQLITE_NOT_NULL','INSERT','必須項目'],
    ['SQLITE_CHECK','UPDATE','制約条件'],
    ['SQLITE_BUSY','UPDATE','使用中'],
    ['SQLITE_READ_ONLY','UPDATE','書き込み権限'],
    ['SQLITE_SAVE_CONFLICT','UPDATE','読込後に別の処理'],
    ['SQLITE_DATABASE_ERROR','INSERT','エラーが発生']
  ];
  for (const [code,operation,fragment] of cases) {
    const message = translate({error:code,details:{table:'departments',operation}});
    assert.ok(message.includes(fragment),code+' '+message);
    assert.ok(message.includes('テーブル「departments」'),code);
    assert.ok(message.includes('DBには保存されていません'),code);
  }
  console.log('PASS translation: 9 representative database error cases');

  // Emulate a WebView2 native response with structured SQLite error details.
  const calls = [];
  let receive;
  const descriptor = {data_source:{type:'sqlite'}};
  const webview = {
    addEventListener(name,fn){ if(name==='message')receive=fn; },
    postMessage(request) {
      calls.push(request);
      const ok = request.command !== 'sqlite.documentSave';
      const result = {content:JSON.stringify(descriptor)};
      const error = {code:'SQLITE_FOREIGN_KEY', message:'SQLite Error 19: FOREIGN KEY constraint failed.',
        details:{table:'departments',operation:'DELETE',key:'30',sqlite_code:19,sqlite_extended_code:787}};
      queueMicrotask(()=>receive({data:{request_id:request.request_id,success:ok,result,error:ok?null:error}}));
    }
  };
  const host={chrome:{webview},location:{origin:'https://frb-studio.local',href:'https://frb-studio.local/index.html'},fetch(){throw new Error('Original fetch called')},setTimeout,clearTimeout};
  const ctx=vm.createContext({window:host,URL,Response,Request,Blob,console,setTimeout,clearTimeout});
  vm.runInContext(get('wwwroot/js/core/native_host_bridge.js'),ctx);
  const url='https://frb-studio.local/api/data/90_samples/sqlite_sample_master_data_v0_1.json';
  const result=await host.fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(descriptor)});
  assert.equal(result.status,500);
  const payload=await result.json();
  assert.equal(payload.error,'SQLITE_FOREIGN_KEY');
  assert.equal(payload.details.operation,'DELETE');
  assert.equal(payload.details.table,'departments');
  assert.equal(calls.at(-1).command,'sqlite.documentSave');
  assert.equal(calls.filter(x=>x.command==='file.writeText').length,0);
  assert.ok(translate(payload).includes('削除できません'));
  console.log('PASS bridge: native structured error survives HTTP-compatible response');

  // Execute the real save handler with minimal Studio stubs. The user message must
  // never expose the raw sqlite provider text, and original changes remain unsaved.
  const saveSrc=get('wwwroot/js/runtime/detail_save.js');
  const start=saveSrc.indexOf('async function saveOverwriteJson() {');
  const end=saveSrc.indexOf('// v0.5-registry: high-level renderer registrations.',start);
  assert.ok(start>=0 && end>start,'save handler still exists');
  const handlerSrc=saveSrc.slice(start,end);
  const saveCtx=vm.createContext({
    window,
    console:{error:()=>{}},
    fetch:async()=>new Response(JSON.stringify(payload),{status:500}),
    sourceData:{data_source:{type:'sqlite'},departments:[{department_id:31}]},
    currentDataApiUrl:'/api/data/90_samples/sqlite_sample_master_data_v0_1.json',
    currentDataSourceKind:'data',
    detailMode:'',selectedIndex:-1,
    $:()=>null,
    applyHeaderEdits(){},
    writeBackVirtualDataEdits:async()=>[],
    ensureViewDefNameInData(){},
    selectedDefName(){return 'sqlite/mock.json'},
    lastLoadedDefName:'sqlite/mock.json',
    setStatus(){throw Error('Must not announce successful save');}
  });
  vm.runInContext(handlerSrc,saveCtx);
  await assert.rejects(()=>saveCtx.saveOverwriteJson(), err=>{
    assert.match(err.message,/他のデータから参照されているため削除できません/);
    assert.doesNotMatch(err.message,/SQLite Error 19|NATIVE_OPERATION_FAILED|FOREIGN KEY constraint failed/);
    return true;
  });
  assert.deepEqual(JSON.parse(JSON.stringify(saveCtx.sourceData.departments)),[{department_id:31}]);
  console.log('PASS save: user gets friendly failure; unsaved data stays in memory');

  const dispatcher=get('NativeShell/NativeCommandDispatcher.cs');
  const adapter=get('NativeShell/SqliteDataAdapter.cs');
  const errors=get('NativeShell/SqliteDataError.cs');
  assert.match(dispatcher,/catch \(SqliteDataError ex\)/);
  assert.match(dispatcher,/ex\.ErrorCode, ex\.Message, ex\.Details\(\)/);
  assert.match(adapter,/FromSqlite\(ex, map\.Table, now == null \? "DELETE" : "UPDATE", pk\)/);
  assert.match(adapter,/FromSqlite\(ex, map\.Table, "INSERT", pk\)/);
  for (const number of [787,2067,1555,1299,275]) assert.match(errors,new RegExp('case '+number+':'));
  console.log('PASS static native adapter routing and stable SQLite error code mapping');
})().catch(error=>{console.error(error);process.exitCode=1;});
