import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const bridge=fs.readFileSync('wwwroot/js/core/native_host_bridge.js','utf8');
test('CLI document bridge reads and saves only the startup capability',async()=>{
  let handler;const calls=[];let document={title:'Launch',items:[{title:'original'}]};
  const window={location:{href:'https://frb-studio.local/index.html',origin:'https://frb-studio.local'},fetch:async()=>{throw Error('unexpected fetch')},setTimeout,clearTimeout,chrome:{webview:{
    addEventListener:(_,h)=>handler=h,
    postMessage:request=>{
      calls.push(request);
      if(request.command==='startupJson.write')document=JSON.parse(request.payload.content);
      handler({data:{request_id:request.request_id,success:true,result:request.command==='startupJson.read'?{content:JSON.stringify(document)}:{saved:true}}});
    }
  }}};
  vm.runInNewContext(bridge,{window,URL,Response,Request,Blob,console,setTimeout,clearTimeout});
  const url='/api/data/__startup_document__.json';
  assert.deepEqual(await (await window.fetch(url)).json(),document);
  await window.fetch(url,{method:'POST',body:JSON.stringify({title:'Launch',items:[{title:'changed'}]})});
  assert.equal((await (await window.fetch(url)).json()).items[0].title,'changed');
  assert.deepEqual(calls.map(c=>c.command),['startupJson.read','startupJson.write','startupJson.read']);
  assert.ok(calls.every(c=>!('path' in c.payload)));
});

test('startup load resolves the declared ViewDef and preserves the external save endpoint',async()=>{
  const source=fs.readFileSync('wwwroot/js/runtime/load_runtime.js','utf8');
  const document={file_name:'launch.json',path:'F:\\FRB\\Launch\\config\\launch.json',content:JSON.stringify({view_def:'launch/test.json',items:[]})};
  let loaded;
  const context={URLSearchParams,location:{search:'?startupJson=1'},window:{FRBStudioNativeHost:{isAvailable:()=>true,invoke:async()=>document}},console,
    $:()=>null,updateCurrentDataViewDefCandidates:()=>{},resolveDefForData:async()=>({defName:'launch/test.json',defObj:{views:[]}}),
    loadFromObjects:async(...args)=>loaded=args,setStatus:message=>{throw Error(message)}};
  vm.createContext(context);vm.runInContext(source,context);context.loadFromObjects=async(...args)=>loaded=args;await vm.runInContext('autoLoadFromQuery()',context);
  assert.equal(loaded[3],'/api/data/__startup_document__.json');
  assert.equal(loaded[4],document.path);
  assert.equal(vm.runInContext('launchRuntime.readonly',context),false);
});
