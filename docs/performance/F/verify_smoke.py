"""Actual native THREE/WebGL smoke attributes and GPU upload-range parity."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
FIXTURE=r'''async()=>{
 const v=__WIP148_3D_VIEW__,T=v.THREE,api=__AEGIS_SMOKE_C13__,diag=__NAVAL_SIM_DIAG__;
 v.active=false;const physical=JSON.stringify(diag.exportOperationalStateV48Wip11A()),rng=__HARPOON_DIAG_A__.snapshot().rng;
 const gl=v.renderer.getContext(),bindings=new Map(),buffers=new Map(),uploads=[],native={bind:gl.bindBuffer.bind(gl),data:gl.bufferData.bind(gl),sub:gl.bufferSubData.bind(gl)};
 gl.bindBuffer=function(target,buffer){bindings.set(target,buffer);return native.bind(target,buffer)};
 gl.bufferData=function(target,data,...rest){if(ArrayBuffer.isView(data))buffers.set(data.buffer,bindings.get(target));return native.data(target,data,...rest)};
 gl.bufferSubData=function(target,offset,data,...rest){const n=rest.length>1?rest[1]:data.length,start=rest[0]??0;uploads.push({offset,bytes:n*data.BYTES_PER_ELEMENT});return native.sub(target,offset,data,...rest)};
 const scene=new T.Scene(),rows=[],hash=async array=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',array))).map(x=>x.toString(16).padStart(2,'0')).join('');
 const capture=async(name,draw=true)=>{
  uploads.length=0;api.flush();const b=v._c13SmokeGPU?.batches;
  if(draw){for(const q of b?.values()??[])scene.add(q.mesh);v.renderer.render(scene,v.camera)}
  const row={name,uploads:[...uploads],bytes:uploads.reduce((n,q)=>n+q.bytes,0),batches:[],glError:gl.getError(),nativeReadbackAvailable:typeof gl.getBufferSubData==='function'};
  for(const [mode,q] of b??[]){const g=q.mesh.geometry,attrs=[];for(const [name,a]of Object.entries(g.attributes))if(a.isInstancedBufferAttribute){
    let gpuExact=null;if(draw&&q.mesh.visible&&buffers.has(a.array.buffer)&&gl.getBufferSubData){const buffer=bindings.get(gl.ARRAY_BUFFER),dst=new Float32Array(a.array.length);gl.bindBuffer(gl.ARRAY_BUFFER,buffers.get(a.array.buffer));gl.getBufferSubData(gl.ARRAY_BUFFER,0,dst);gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gpuExact=await hash(dst.buffer)===await hash(a.array.buffer)}
    attrs.push({name,live:await hash(a.array.slice(0,g.instanceCount*a.itemSize).buffer),all:await hash(a.array.buffer),gpuExact});
  }row.batches.push({mode,count:g.instanceCount,visible:q.mesh.visible,position:q.mesh.position.toArray(),attrs})}rows.push(row);return row;
 };
 api.configure({capacity:12000,hybrid:true});const pool=v.c13Smoke;pool.time=2;v.camera.position.set(0,30,100);v.camera.lookAt(0,20,0);v.camera.updateMatrixWorld(true);
 const emit=(i)=>pool.emit({x:(i%4)*2-4,y:20+i%3,z:-i*5,kind:[1,5,6][i%3],birth:0,life:30,base:2+i*.1,growth:.04,alpha:.55,span:4,ax:1,color:[.31,.27,.19],endColor:[.1,.12,.14],rotation:.23,tile:2});
 for(let i=0;i<24;i++)emit(i);
 await capture('initial');await capture('unchanged');
 pool.fields.x[0]+=.125;await capture('one_particle');await capture('unchanged_after_dirty');pool.fields.x[0]+=1e-12;await capture('sub_float32_ulp');pool.fields.ax[0]=-0;await capture('signed_zero');
 v.camera.position.set(0,35,-140);v.camera.lookAt(0,20,-20);v.camera.updateMatrixWorld(true);await capture('camera_order');
 v.renderOriginWip14A.set(300,0,-200);await capture('floating_origin');
 pool.fields.x[2]+=.25;await capture('pending_first',false);pool.fields.z[5]-=.5;await capture('pending_second');
 for(let i=0;i<10;i++)pool.remove(pool.count-1);await capture('shrink');
 const tail=pool.count-1;pool.fields.x[tail]+=1;await capture('pending_tail',false);const saved=[];for(let i=0;i<pool.count;i++){const q={};for(const key of pool.keys)q[key]=pool.fields[key][i];saved.push(q)}
 pool.count=0;await capture('hidden');pool.count=saved.length;await capture('reappear');
 const old=[...v._c13SmokeGPU.batches.values()].map(q=>q.mesh.geometry),disposed=new Set();for(const g of old)g.addEventListener('dispose',()=>disposed.add(g));api.configure({capacity:12000,hybrid:false});
 v.c13Smoke.time=2;v.c13Smoke.emit({x:1,y:20,z:0,birth:0,life:30,alpha:.8,base:4});await capture('reset_new_batch');
 const gpuChecks=rows.every(r=>r.batches.every(b=>b.attrs.every(a=>a.gpuExact!==false)));
 gl.bindBuffer=native.bind;gl.bufferData=native.data;gl.bufferSubData=native.sub;
 return {rows,checks:{allGpuBuffersMatchCpu:gpuChecks,nativeReadbackAvailable:typeof gl.getBufferSubData==='function',glErrorsZero:rows.every(r=>r.glError===0),resetDisposedAll:old.every(g=>disposed.has(g)),physicalUnchanged:physical===JSON.stringify(diag.exportOperationalStateV48Wip11A()),rngUnchanged:rng===__HARPOON_DIAG_A__.snapshot().rng,coreZero:__CORE_SELFTEST_FAILURES__.length===0,faultsZero:!__WIP125_DIAG__.wip150RuntimeFault()&&!__WIP125_DIAG__.wip150PresentationFault()}};
}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);pair={};errors=[]
 with sync_playwright()as pw:
  b=launch(pw,True)
  for name,src in [('baseline',a.baseline),('candidate',a.html)]:
   page=load(b,src.read_bytes(),webgl=True,errors=errors);pair[name]=page.evaluate(FIXTURE);page.close();print(json.dumps({'version':name,'checks':pair[name]['checks']}),flush=True)
  b.close()
 base,cand=pair['baseline'],pair['candidate'];checks={**cand['checks'],'allLiveAttributesAndInstancesExact':all(x['name']==y['name'] and x['batches']==y['batches'] for x,y in zip(base['rows'],cand['rows'])),'unchangedUploadsZero':next(r for r in cand['rows']if r['name']=='unchanged')['bytes']==0,'unchangedAfterDirtyUploadsZero':next(r for r in cand['rows']if r['name']=='unchanged_after_dirty')['bytes']==0,'subFloat32UlpUploadsZero':next(r for r in cand['rows']if r['name']=='sub_float32_ulp')['bytes']==0,'priorOneParticleUploadRetained':next(r for r in cand['rows']if r['name']=='one_particle')['bytes']==next(r for r in base['rows']if r['name']=='one_particle')['bytes']}
 q={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'baselineSha256':hashlib.sha256(a.baseline.read_bytes()).hexdigest(),'fixture':'Controlled native WebGL2 CPU and actual GPU byte readbacks; not whole-game timing or FPS','checks':checks,'pair':pair,'errors':errors,'pass':not errors and all(checks.values())};(a.out/'smoke.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({'pass':q['pass'],'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if q['pass']else 1)
if __name__=='__main__':main()
