// v0.1: Cooperative per-document exclusive lock + CAS + same-directory atomic rename.
// Does not promise isolation from external applications that do not honor this lock.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash,randomUUID} from 'node:crypto';
import {ChangeSetError} from './change_core.mjs';
export const sha256=buffer=>createHash('sha256').update(buffer).digest('hex');
export async function readSnapshot(file){const bytes=await fs.readFile(file);return {bytes,sha256:sha256(bytes),document:JSON.parse(bytes.toString('utf8').replace(/^\uFEFF/,''))};}
export async function commitDocument(file,baseSha,serialized,{beforeReplace}={}){
  const lockPath=`${file}.studio-changeset.lock`;
  let lock;
  try{lock=await fs.open(lockPath,'wx',0o600);}
  catch(e){if(e.code==='EEXIST')throw new ChangeSetError('LOCKED','他の保存処理がロックを保持しています');throw e;}
  let temporary='';
  try{
    const current=await fs.readFile(file);
    if(sha256(current)!==baseSha)throw new ChangeSetError('CONFLICT','保存対象が読込後に変更されています');
    const stat=await fs.stat(file);
    temporary=path.join(path.dirname(file),`.${path.basename(file)}.${randomUUID()}.tmp`);
    const fh=await fs.open(temporary,'wx',stat.mode & 0o777);
    try{await fh.writeFile(serialized,'utf8');await fh.sync();}finally{await fh.close();}
    if(beforeReplace)await beforeReplace(); // test fault injection only; not exposed by CLI
    // Cooperating writers cannot race here because the lock is held.
    // Non-cooperating writes/Windows sharing violations remain explicit environmental limits.
    const final=await fs.readFile(file);
    if(sha256(final)!==baseSha)throw new ChangeSetError('CONFLICT','保存直前に競合を検出しました');
    await fs.rename(temporary,file);temporary='';
    try{const dir=await fs.open(path.dirname(file),'r');try{await dir.sync();}finally{await dir.close();}}catch{} // best effort, Windows may reject dir fsync
    return {sha256:sha256(Buffer.from(serialized,'utf8'))};
  }finally{
    if(temporary)await fs.unlink(temporary).catch(()=>{});
    await lock.close();await fs.unlink(lockPath).catch(()=>{});
  }
}
