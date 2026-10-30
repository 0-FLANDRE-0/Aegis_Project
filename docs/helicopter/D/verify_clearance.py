"""Actual native C5 surfaces versus extracted helo triangles and live ground poses.

No proxy wall-plane test: every visible static ship surface near the hangars and
flight deck is exported after the real build/cut, then tested with triangle SAT.
"""
import argparse,base64,gzip,hashlib,json,re,struct,subprocess,sys
from pathlib import Path
import numpy as np
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'docs/multiship/G'))
from browser_g import launch,load_fleet

def folded_triangles(corrected):
 raw=gzip.decompress((ROOT/'docs/helicopter/A/seahawk-render-a1.bin.gz').read_bytes());n=struct.unpack_from('<I',raw,4)[0];meta=json.loads(raw[8:8+n]);start=8+n+(-n)%4;rig=json.loads((HERE/'rig.json').read_text());origin=np.array(rig['origin']);scale=np.array([rig['horizontalScale'],rig['verticalScale'],rig['horizontalScale']]);parts={p['id']:p for p in meta['parts']};ts=[];ids=[]
 for id in meta['poses']['folded']:
  if corrected and id==12708:continue # Complete extended rear wheel 12704 is retained.
  p=parts[id];m=np.array(p['matrix']).reshape(4,4,order='F')
  for ref in p['primitives']:
   primitive=meta['meshes'][ref['mesh']]['primitives'][ref['primitive']];a=meta['accessors'][primitive['attributes']['POSITION']];q=np.frombuffer(raw,dtype='<u2',count=a['count']*3,offset=start+a['offset']).reshape(-1,3);q=np.array(a['min'])+q*np.array(a['scale']);q=(m@np.column_stack([q,np.ones(len(q))]).T).T[:,:3];q=(q-origin)*scale;i=meta['accessors'][primitive['indices']];ix=np.frombuffer(raw,dtype='<u2',count=i['count'],offset=start+i['offset']);t=q[ix].reshape(-1,3,3);ts.extend(t);ids.extend([id]*len(t))
 return np.array(ts),np.array(ids)

CAPTURE=r'''()=>{const v=__WIP148_3D_VIEW__,T=v.THREE;v.syncShipFittings(get3DRenderState());v.shipRoot.updateWorldMatrix(true,true);const inverse=v.shipRoot.matrixWorld.clone().invert(),out=[];v.shipRoot.traverse(m=>{if(!m.isMesh||m.isInstancedMesh)return;for(let q=m;q;q=q.parent)if(!q.visible)return;const g=m.geometry,p=g.attributes.position,ix=g.index,tr=inverse.clone().multiply(m.matrixWorld),triangles=[],q=new T.Vector3();for(let i=0;i<(ix?.count??p.count);i+=3){const ps=[0,1,2].map(j=>q.fromBufferAttribute(p,ix?ix.getX(i+j):i+j).applyMatrix4(tr).toArray());const lo=[0,1,2].map(k=>Math.min(...ps.map(a=>a[k]))),hi=[0,1,2].map(k=>Math.max(...ps.map(a=>a[k])));if(lo[0]<-28&&hi[0]>-76&&lo[1]<9&&hi[1]>2.5&&lo[2]<10&&hi[2]>-10)triangles.push(ps);}if(triangles.length)out.push({name:m.name,parent:m.parent?.name,triangles});});return {sourceC5:!!v._c5Asset,relocatedStairTriangles:v.heloDoorsA?.relocatedStairTriangles??0,meshes:out,glError:v.renderer.getContext().getError()};}'''
POSE=r'''slot=>{const h=get3DRenderState().helicopters.aircraft.find(h=>h.slot===slot);return {x:h.localM.x,y:h.localM.y,z:h.localM.z,yaw:h.localYawRad,pitch:h.pitchRad,bank:h.bankRad,state:h.state,slot,door:__HELO__.snapshot().doors?.[slot]};}'''

def native_capture(browser,html,live=False):
 errors=[];page=load_fleet(browser,html.read_bytes(),own='DDG_119_LATE_FLIGHT_IIA',ally=None,enemy=None,width=640,height=480,errors=errors)
 page.evaluate("()=>{const a=__HELO__.snapshot().aircraft;__HELO__.command(a[0].id,'LAUNCH');__HELO__.command(a[1].id,'LAUNCH');__NAVAL_SIM_DIAG__.stepTicks(600);}")
 page.evaluate("async()=>{await __WIP148_3D_VIEW__.open();__WIP148_3D_VIEW__.c12ApplyPreset('LOW');}");page.wait_for_function('__WIP148_3D_VIEW__.heloVisualsA.size===1',timeout=90000);data=page.evaluate(CAPTURE)
 # Closing the native view stops costly software rasterization; simulation data
 # below still comes from the unchanged canonical fixed-step runtime.
 page.evaluate('__WIP148_3D_VIEW__.close()');poses=[]
 if live:
  for slot in [0,1]:
   if slot:
    for _ in range(300):
     h=page.evaluate('__HELO__.snapshot().aircraft[1]')
     if h['state']=='HANGAR_OPEN':break
     page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(60)')
    else:raise AssertionError('H2 never receives the cleared deck')
    page.evaluate(f"__NAVAL_SIM_DIAG__.stepTicks({600-h['stateTick']})")
   samples=[]
   for k in range(21):
    if k:page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(60)')
    samples.append(page.evaluate(POSE,slot))
   poses.append(samples)
 page.close();data['errors']=errors;data['livePoses']=poses;return data

def paths(folder,count):
 source=(folder/'motion.js').read_text()+'\n'+(folder/'runtime.js').read_text();corrected=folder==HERE
 row="const p=heloGroundPathB(slot,i/(N-1)),h={localM:p,localYawRad:p.yaw};"+("heloGroundAttitudeC(h);"if corrected else"h.pitchRad=0;h.bankRad=0;")+"return{...p,slot,pitch:h.pitchRad,bank:h.bankRad};"
 script='const window={},N='+str(count)+';'+source+'\nprocess.stdout.write(JSON.stringify([0,1].map(slot=>Array.from({length:N},(_,i)=>{'+row+'}))));'
 return json.loads(subprocess.check_output(['node','-e',script],text=True))

def sat(A,B):
 ea=np.roll(A,-1,axis=1)-A;eb=np.roll(B,-1,axis=1)-B;axes=np.cross(ea[:,:,None,:],eb[:,None,:,:]).reshape(-1,9,3);axes=np.concatenate([axes,np.cross(ea[:,0],ea[:,1])[:,None,:],np.cross(eb[:,0],eb[:,1])[:,None,:]],axis=1);axes/=np.maximum(np.linalg.norm(axes,axis=2,keepdims=True),1e-20);pa=np.einsum('nvc,nac->nva',A,axes);pb=np.einsum('nvc,nac->nva',B,axes);overlap=np.minimum(pa.max(1),pb.max(1))-np.maximum(pa.min(1),pb.min(1));return(overlap>=-1e-7).all(1)

def intersections(data,poses,corrected):
 helo,ids=folded_triangles(corrected);ship=np.array([t for m in data['meshes']for t in m['triangles']]);names=np.array([m['name']for m in data['meshes']for _ in m['triangles']]);minimum=ship.min(1);maximum=ship.max(1);hits=[]
 for slot in [0,1]:
  for k,p in enumerate(poses[slot]):
   yaw=p['yaw'];c=np.cos(yaw);s=np.sin(yaw);pitch=-p['pitch'];bank=-p['bank'];rz=np.array([[np.cos(pitch),-np.sin(pitch),0],[np.sin(pitch),np.cos(pitch),0],[0,0,1]]);rx=np.array([[1,0,0],[0,np.cos(bank),-np.sin(bank)],[0,np.sin(bank),np.cos(bank)]]);ry=np.array([[c,0,-s],[0,1,0],[s,0,c]]);q=helo@(ry@rz@rx).T+np.array([p['x'],p['z'],p['y']]);mn=q.min(1);mx=q.max(1);candidate=np.nonzero((minimum<=mx.max(0)).all(1)&(maximum>=mn.min(0)).all(1))[0];mask=(minimum[candidate,None,:]<=mx[None,:,:]).all(2)&(maximum[candidate,None,:]>=mn[None,:,:]).all(2);si,hi=np.nonzero(mask);si=candidate[si]
   if not len(si):continue
   hit=sat(ship[si],q[hi]);si=si[hit];hi=hi[hit]
   if len(si):hits.append({'slot':slot,'u':k/(len(poses[slot])-1),'parts':sorted(set(ids[hi].tolist())),'shipMeshes':sorted(set(names[si].tolist())),'trianglePairs':len(si)})
 return {'shipTriangles':len(ship),'heloTriangles':len(helo),'posesPerSlot':len(poses[0]),'intersectingPoses':len(hits),'hits':hits,'geometrySha256':hashlib.sha256(ship.tobytes()).hexdigest()}

def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);p.add_argument('--baseline',type=Path,default=ROOT/'archive/v48/WIP_HELI_B/Aegis_SIM_v48_WIP_HELI_B.html');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 main=gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',a.html.read_text(),re.S)[1])).decode()
 assert all(main.count((HERE/f).read_text())==1 for f in ['motion.js','runtime.js'])
 with sync_playwright()as pw:
  browser=launch(pw,True);before=native_capture(browser,a.baseline);after=native_capture(browser,a.html,True);browser.close()
 print('Native C5 geometry and actual fixed-step poses captured.',flush=True)
 cache=Path('/tmp/aegis-helo-clearance-cache');cache.mkdir(exist_ok=True);(cache/'baseline.json').write_text(json.dumps(before));(cache/'final.json').write_text(json.dumps(after));
 old=intersections(before,paths(ROOT/'docs/helicopter/C',101),False);new=intersections(after,paths(HERE,101),True);dense=paths(HERE,101);checks={'nativeActualC5':before['sourceC5']and after['sourceC5'],'baselineInterferenceReproduced':old['intersectingPoses']>0,'portStairComplete48TrianglesMoved':after['relocatedStairTriangles']==48,'bothSlotsNoStaticSurfaceIntersection':new['intersectingPoses']==0,'nativeGlClean':before['glError']==after['glError']==0,'nativeNoErrors':not before['errors']and not after['errors']}
 for slot in [0,1]:
  checks[f'slot{slot}.actualFixedPosesMatchDensePath']=all(np.max(np.abs(np.array([p[k]for k in ['x','y','z','yaw','pitch','bank']])-np.array([dense[slot][i*5][k]for k in ['x','y','z','yaw','pitch','bank']])))<1e-6 for i,p in enumerate(after['livePoses'][slot]))
  checks[f'slot{slot}.deckSurfaceFollowed']=dense[slot][-1]['z']>3.8 and abs(dense[slot][-1]['pitch'])>.04
 out={'pass':all(checks.values()),'checks':checks,'htmlSha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'baselineSha256':hashlib.sha256(a.baseline.read_bytes()).hexdigest(),'baseline':old,'final':new,'livePoses':after['livePoses'],'errors':after['errors'],'limits':'Native Three/SwiftShader static geometry and 101 folded positions per slot; does not model combat collision, structural deformation, or rotor aerodynamics. Original compressed wheel duplication is excluded only in the corrected source pose, matching the native visibility proof.'};(a.out/'clearance.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'baselineIntersectingPoses':old['intersectingPoses'],'finalIntersectingPoses':new['intersectingPoses'],'shipTriangles':new['shipTriangles'],'heloTriangles':new['heloTriangles']}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
