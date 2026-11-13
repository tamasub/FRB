import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const read = file => fs.readFileSync(file,'utf8');

test('full-text Enter invokes the canonical search button, not a duplicate search implementation', () => {
  const app=read('wwwroot/app.js');
  const block=app.match(/\$\('studioFullTextSearchInput'\)\?\.addEventListener\('keydown', event => \{[\s\S]*?\n\}\);/);
  assert.ok(block,'canonical full-text keydown listener missing');
  const actions={};
  const submit={ disabled:false, click:()=>{actions.clicked=(actions.clicked || 0)+1;} };
  const mockInput={addEventListener:(name,fn)=>{actions[name]=fn;}};
  const $=id=>id==='studioFullTextSearchInput'?mockInput: id==='searchBtn'?submit:null;
  vm.runInNewContext(block[0],{$});
  function key(event) {
    let prevented=false;
    actions.keydown({key:'Enter',isComposing:false,keyCode:13,...event,preventDefault:()=>{prevented=true;}});
    return prevented;
  }
  assert.equal(key({}),true);
  assert.equal(actions.clicked,1);
  assert.equal(key({isComposing:true}),false);
  assert.equal(actions.clicked,1);
  assert.equal(key({keyCode:229}),false);
  assert.equal(actions.clicked,1);
  assert.equal(key({key:'x'}),false);
  submit.disabled=true;
  assert.equal(key({}),false);
  assert.equal(actions.clicked,1);
});

test('NativeShell receives a presentation notification from the loaded ViewDef', () => {
  const presentation=read('wwwroot/js/ui/studio_presentation_profile.js');
  const native=read('NativeShell/NativeShellForm.cs');
  assert.match(presentation,/global\.chrome\.webview\.postMessage\(\{ studio_presentation:/);
  assert.match(native,/message\.TryGetValue\("studio_presentation"/);
  assert.match(native,/if \(!IsAllowedSource\(e\.Source\)\) return/);
  assert.match(native,/ApplyNativePresentation\(get\("preset"\), get\("theme"\), get\("shell"\)\)/);
  assert.match(native,/return;\s*}\s*var responseJson = await _dispatcher\.DispatchAsync/);
  assert.match(native,/DwmSetWindowAttribute\(Handle, 20/);
});

test('launcher dimensions persist independently of standard studio window',()=>{
  const native=read('NativeShell/NativeShellForm.cs');
  const bounds=read('NativeShell/NativeShellWindowBounds.cs');
  assert.match(native,/if \(!launcher \|\| !firstPresentation\) return/);
  assert.match(native,/NativeShellWindowBounds\.TryLoad/);
  assert.match(native,/NativeShellWindowBounds\.TrySave/);
  assert.match(native,/ResizeEnd \+=/);
  assert.match(bounds,/launcher_window_bounds\.json/);
  assert.match(bounds,/Screen\.AllScreens/);
  assert.match(bounds,/width < 520 \|\| height < 360/);
  assert.doesNotMatch(read('wwwroot/index.html'),/通常表示に戻す/);
});

test('dark detail editor overrides white gradients and card backgrounds only when opted in',()=>{
  const css=read('wwwroot/css/studio-presentation.css');
  assert.match(css,/\[data-studio-theme="launch-dark"\]/);
  assert.match(css,/#detailDialog \.dialog-body/);
  assert.match(css,/#detailDialog \.dialog-title-row/);
  assert.match(css,/#detailDialog \.detail-footer/);
  assert.match(css,/\.detail-subgrid-preview-body/);
  assert.match(css,/\.detail-subgrid-cell-input/);
  assert.match(css,/body\.frb-page-json-object:is\(\[data-studio-theme="dark"\]/);
});
