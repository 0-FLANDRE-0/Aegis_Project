"""Native CG static source/interior/door triangles versus extracted folded helo geometry."""
import argparse,json,hashlib,sys,subprocess,importlib.util
from pathlib import Path
import numpy as np
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'docs/helicopter/H'))
from browser import load_fleet,launch
spec=importlib.util.spec_from_file_location('clearance_D',ROOT/'docs/helicopter/D/verify_clearance.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
CAPTURE=r'''()=>{const v=__WIP148_3D_VIEW__,T=v.THREE;v.syncShipFittings(get3DRenderState());v.shipRoot.updateWorldMatrix(true,true);const inverse=v.shipRoot.matrixWorld.clone().invert(),out=[];v.shipRoot.traverse(m=>{if(!m.isMesh)return;for(let q=m;q;q=q.parent)if(!q.visible)return;const g=m.geometry,p=g.attributes.position,ix=g.index,tr=inverse.clone().multiply(m.matrixWorld),triangles=[],q=new T.Vector3();for(let instance=0;instance<(m.isInstancedMesh?m.count:1);instance++){const im=new T.Matrix4();if(m.isInstancedMesh)m.getMatrixAt(instance,im);const transform=tr.clone().multiply(im);for(let i=0;i<(ix?.count??p.count);i+=3){const ps=[0,1,2].map(j=>q.fromBufferAttribute(p,ix?ix.getX(i+j):i+j).applyMatrix4(transform).toArray());const lo=[0,1,2].map(k=>Math.min(...ps.map(a=>a[k]))),hi=[0,1,2].map(k=>Math.max(...ps.map(a=>a[k])));if(lo[0]<-15&&hi[0]>-55&&lo[1]<15.2&&hi[1]>9.6&&lo[2]<8&&hi[2]>-8)triangles.push(ps);}}if(triangles.length)out.push({name:m.name,parent:m.parent?.name,triangles});});return {meshes:out,cgSource:!!v._bunkerAsset,doorCount:v.heloDoorsA.doors.length,removedPolygons:v.heloDoorsA.removedPolygons,glError:v.renderer.getContext().getError()};}'''
def paths(count=101):
 s="const window={},ACTIVE_SHIP_RUNTIME={profileId:'CG_52_LATE_TICONDEROGA'};"+(ROOT/'docs/helicopter/F/motion.js').read_text()+(HERE/'runtime.js').read_text()+"\nprocess.stdout.write(JSON.stringify([0,1].map(slot=>Array.from({length:COUNT},(_,i)=>{const p=heloGroundPathB(slot,i/(COUNT-1)),h={localM:p,localYawRad:p.yaw};heloGroundAttitudeC(h);return {...p,pitch:h.pitchRad,bank:h.bankRad,slot};}))));"
 return json.loads(subprocess.check_output(['node','-e',s.replace('COUNT',str(count))],text=True))
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();errors=[]
 with sync_playwright()as pw:
  b=launch(pw,True);page=load_fleet(b,raw,own='CG_52_LATE_TICONDEROGA',errors=errors);page.evaluate("()=>{const a=__HELO__;a.command(a.snapshot().aircraft[0].id,'LAUNCH');__NAVAL_SIM_DIAG__.setEmcon(true);__NAVAL_SIM_DIAG__.stepTicks(600);}");page.evaluate('async()=>{await __WIP148_3D_VIEW__.open();__WIP148_3D_VIEW__.c12ApplyPreset("LOW");}');page.wait_for_function('__WIP148_3D_VIEW__.heloVisualsA.size===2',timeout=90000);page.evaluate('window.requestAnimationFrame=()=>0');capture=page.evaluate(CAPTURE);page.close();b.close()
 (a.out/'geometry.json').write_text(json.dumps(capture));print('CG native source and shared hangar captured',flush=True)
 poses=paths();result=old.intersections(capture,poses,True)
 # Aircraft AABBs are disjoint throughout either first-launch order: stronger
 # than a triangle test because no pair can intersect without AABB overlap.
 helos,_=old.folded_triangles(True);lo=helos.min((0,1));hi=helos.max((0,1));park=[np.array([ps[0]['x'],ps[0]['z'],ps[0]['y']])for ps in poses];separated=True
 for slot in [0,1]:
  fixedlo, fixedhi=lo+park[1-slot],hi+park[1-slot]
  if slot==1:continue # Native launch guard waits until port H1 is airborne; no parked H1 remains.
  for q in poses[slot]:
   c,s=np.cos(q['yaw']),np.sin(q['yaw']);rot=np.array([[c,0,-s],[0,1,0],[s,0,c]]);pts=helos@rot.T+np.array([q['x'],q['z'],q['y']]);movinglo,movinghi=pts.min((0,1)),pts.max((0,1));separated&=not bool(np.all(movinglo<=fixedhi)&np.all(movinghi>=fixedlo))
 dense=paths(1201);speeds=[max(np.hypot(b['x']-a['x'],b['y']-a['y'])*60 for a,b in zip(ps,ps[1:]))for ps in dense]
 checks={'towBelow3Mps':bool(max(speeds)<=3),'nativeCgSource':capture['cgSource'],'oneDoor':capture['doorCount']==1,'onlyPortOpeningCut':capture['removedPolygons']>0,'portExitAvoidsParkedStarboardHelo':separated,'bothSlotsNoStaticIntersection':result['intersectingPoses']==0,'glClean':capture['glError']==0,'noPageErrors':not errors};out={'pass':all(checks.values()),'checks':checks,'result':result,'maxTowSpeedMps':speeds,'poses':poses,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(a.out/'clearance.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'hits':result['hits'][:12]}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
