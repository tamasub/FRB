// studio_work_0269: verify actual browser bridge protocol without launching WinForms.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import vm from 'node:vm';
const root = fileURLToPath(new URL('../../', import.meta.url));
const js = readFileSync(new URL('../../wwwroot/js/core/native_host_bridge.js', import.meta.url),'utf8');
const source = readFileSync(new URL('../../NativeShell/NativeShellForm.cs', import.meta.url),'utf8');
const native = readFileSync(new URL('../../NativeShell/NativeCommandDispatcher.cs', import.meta.url),'utf8');
const sha = raw => createHash('sha256').update(raw).digest('hex');
function setup(raw = '{"items":[]}') {
  let listener, disk = raw, commands = [], reject = false;
  const webview = {
    postMessage: command => {
      commands.push(command);
      let result = null, error = null;
      if(command.command === 'file.readText') result = { content:disk, sha256:sha(Buffer.from(disk,'utf8')) };
      else if(command.command === 'file.writeTextCas') {
        if (reject || command.payload.expected_sha256 !== sha(Buffer.from(disk,'utf8')))
          error = { code:'NATIVE_OPERATION_FAILED', message:'CONFLICT: JSON changed before replace.' };
        else {
          disk = command.payload.content;
          result = { saved:command.payload.path, sha256: sha(Buffer.from(disk,'utf8')) };
        }
      } else throw Error(`Unexpected command: ${command.command}`);
      queueMicrotask(() => listener({data:{request_id:command.request_id,success:!error,result,error}}));
    },
    addEventListener: (type,callback) => {assert.equal(type,'message');listener=callback;}
  };
  const window = {
    location:{href:'https://frb-studio.local/index.html', origin:'https://frb-studio.local'},
    chrome:{webview}, setTimeout,clearTimeout,
    fetch:async()=>{throw Error('unexpected network fetch');},
  };
  const context = {window, URL, Request, Response, Blob, console, setTimeout, clearTimeout};
  vm.runInNewContext(js,context,{filename:'native_host_bridge.js'});
  return {get fetch(){return window.fetch;},get commands(){return commands;},setConflict:v=>reject=v,get disk(){return disk;}};
}
test('large incident JSON can be loaded, CAS saved and resaved without losing baseline',async()=>{
  const data = readFileSync(new URL('../../data/json/01_main/_studio_work_incident_data_v2.json',import.meta.url),'utf8');
  assert.ok(Buffer.byteLength(data)>2*1024*1024);
  const ctx=setup(data);
  const url='/api/data/01_main/_studio_work_incident_data_v2.json';
  let res=await ctx.fetch(url);
  assert.equal(res.status,200);
  const doc=await res.json();
  assert.equal(doc.work_items.length,257);
  res=await ctx.fetch(url,{method:'POST',body:JSON.stringify(doc)});
  assert.equal(res.status,200);
  assert.equal(ctx.commands.at(-1).command,'file.writeTextCas');
  assert.equal(ctx.commands.at(-1).payload.expected_sha256,sha(Buffer.from(data)));
  res=await ctx.fetch(url,{method:'POST',body:JSON.stringify(doc)});
  assert.equal(res.status,200);
  assert.equal(ctx.commands.at(-1).payload.expected_sha256,sha(Buffer.from(ctx.disk)));
});
test('concurrent editor rejection keeps browser baseline, and reload refreshes it',async()=>{
  const ctx=setup();const url='/api/data/sample.json';
  await ctx.fetch(url); ctx.setConflict(true);
  const failed=await ctx.fetch(url,{method:'POST',body:'{"items":[1]}'});
  assert.equal(failed.status,409);
  ctx.setConflict(false);
  const saved=await ctx.fetch(url,{method:'POST',body:'{"items":[1]}'});
  assert.equal(saved.status,200);
});
test('POST without initial GET is rejected instead of blind overwrite',async()=>{
  const ctx=setup();const res=await ctx.fetch('/api/data/alone.json',{method:'POST',body:'{}'});
  assert.equal(res.status,409);
  assert.equal(ctx.commands.length,1); // file.readText descriptor check; never reaches write
  assert.equal(ctx.commands[0].command,'file.readText');
});
test('native receiver avoids default 2MiB-deserializer for large messages',()=>{
  assert.match(source,/rawMessage\.Length <= 32768/);
  assert.match(source,/DispatchAsync\(rawMessage, e\.AdditionalObjects\)/);
  assert.match(native,/MaxJsonLength\s*=\s*int\.MaxValue/);
  assert.match(native,/case "file\.writeTextCas"/);
  assert.match(native,/File\.Replace\(tempPath, full, null, true\)/);
  assert.match(native,/\.studio-changeset\.lock/);
});
