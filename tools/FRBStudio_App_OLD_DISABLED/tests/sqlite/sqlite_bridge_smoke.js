// Run: node tests/sqlite/sqlite_bridge_smoke.js
// Validates native bridge routing without needing Windows, WebView2, or a live DB.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert/strict');

const root = path.resolve(__dirname, '../..');
const bridgeCode = fs.readFileSync(path.join(root, 'wwwroot/js/core/native_host_bridge.js'), 'utf8');
const descriptor = JSON.stringify({view_def:'sqlite/studio_sample_master_view_def_v0_1.json',data_source:{type:'sqlite'}});
const projected = {view_def:'sqlite/studio_sample_master_view_def_v0_1.json',data_source:{type:'sqlite'},employees:[{employee_id:1}],__sqlite_snapshot:{employees:[{employee_id:1}]}};
const calls = [];
let receive;
const webview = {
  addEventListener(event, fn) { if (event === 'message') receive = fn; },
  postMessage(req) {
    calls.push(req);
    let result;
    if(req.command==='file.readText') result={content:descriptor};
    else if(req.command==='sqlite.documentLoad') result={document:projected};
    else if(req.command==='sqlite.documentSave') result={changed_rows:1, document: projected};
    else throw new Error('Unexpected native command: '+req.command);
    queueMicrotask(()=>receive({data:{request_id:req.request_id,success:true,result}}));
  }
};
const win={chrome:{webview},location:{href:'https://frb-studio.local/index.html',origin:'https://frb-studio.local'},fetch:()=>{throw Error('Should not use originalFetch')},setTimeout,clearTimeout};
const context=vm.createContext({window:win,URL,Response,Request,Blob,console,setTimeout,clearTimeout});
vm.runInContext(bridgeCode,context);
(async()=>{
  const response=await win.fetch('https://frb-studio.local/api/data/90_samples/sqlite_sample_master_data_v0_1.json');
  assert.equal(response.status,200);
  const body=await response.json();
  assert.deepEqual(body.employees,[{employee_id:1}]);
  assert.equal(calls[1].command,'sqlite.documentLoad');
  assert.equal(calls[1].payload.document_path,'data/json/90_samples/sqlite_sample_master_data_v0_1.json');
  const post=await win.fetch('https://frb-studio.local/api/data/90_samples/sqlite_sample_master_data_v0_1.json',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  assert.equal(post.status,200);
  assert.equal((await post.json()).changed_rows,1);
  assert.equal(calls[calls.length-1].command,'sqlite.documentSave');
  assert.equal(calls.filter(c=>c.command==='file.writeText').length,0);
  console.log('PASS sqlite bridge GET/POST routes to adapter, descriptor not overwritten');
})().catch(err=>{console.error(err);process.exitCode=1});
