"""Independent extracted folded triangles versus portals and live ground poses."""
import argparse,gzip,json,struct,subprocess
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
p=argparse.ArgumentParser();p.add_argument('runtime',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
b=gzip.decompress((ROOT/'docs/helicopter/A/seahawk-render-a1.bin.gz').read_bytes());n=struct.unpack_from('<I',b,4)[0];j=json.loads(b[8:8+n]);start=8+n+(-n)%4;parts={p['id']:p for p in j['parts']};r=json.loads((HERE/'rig.json').read_text());origin=np.array(r['origin']);scale=np.array([r['horizontalScale'],r['verticalScale'],r['horizontalScale']]);triangles=[]
for id in j['poses']['folded']:
 part=parts[id];m=np.array(part['matrix']).reshape((4,4),order='F')
 for ref in part['primitives']:
  prim=j['meshes'][ref['mesh']]['primitives'][ref['primitive']];v=j['accessors'][prim['attributes']['POSITION']];x=np.frombuffer(b,dtype='<u2',count=v['count']*3,offset=start+v['offset']).reshape(-1,3);x=np.asarray(v['min'])+x*np.asarray(v['scale']);x=(m@np.column_stack([x,np.ones(len(x))]).T).T[:,:3];x=(x-origin)*scale;ind=j['accessors'][prim['indices']];ix=np.frombuffer(b,dtype='<u2',count=ind['count'],offset=start+ind['offset']);triangles.extend(x[ix].reshape(-1,3,3))
triangles=np.array(triangles);source=(HERE/'motion.js').read_text()+'\n'+(HERE/'runtime.js').read_text();script='const window={};'+source+'\nprocess.stdout.write(JSON.stringify([0,1].map(slot=>Array.from({length:401},(_,i)=>({...heloGroundPathB(slot,i/400),slot})))));';poses=json.loads(subprocess.check_output(['node','-e',script],text=True));runtime=json.loads(a.runtime.read_text());live=[runtime['runtime']['samples'],runtime['runtime']['samples2']];checks={};observations=[]
for slot in [0,1]:
 minimum=1e9;minSide=1e9;minTop=1e9;maxGear=0;violations=[]
 for state in poses[slot]:
  yaw=state['yaw'];c=np.cos(yaw);s=np.sin(yaw);q=triangles.copy();q[:,:,0]=triangles[:,:,0]*c-triangles[:,:,2]*s+state['x'];q[:,:,2]=triangles[:,:,0]*s+triangles[:,:,2]*c+state['y'];q[:,:,1]+=state['z'];d=q[:,:,0]-(-48.224+(q[:,:,1]-3.18)*1.047/6.185);cross=(d.min(1)<=0)&(d.max(1)>=0);q=q[cross];d=d[cross]
  for k,l in [(0,1),(1,2),(2,0)]:
   hit=d[:,k]*d[:,l]<=0;den=d[hit,k]-d[hit,l];safe=np.abs(den)>1e-10
   if not safe.any():continue
   t=d[hit,k][safe]/den[safe];v=q[hit,k][safe]+(q[hit,l][safe]-q[hit,k][safe])*t[:,None];margin=np.minimum.reduce([v[:,1]-3.18,8.43-v[:,1],v[:,2]-((slot*2-1)*5.03-2.24),((slot*2-1)*5.03+2.24)-v[:,2]]);minimum=min(minimum,float(margin.min()));minSide=min(minSide,float(np.minimum(v[:,2]-((slot*2-1)*5.03-2.24),((slot*2-1)*5.03+2.24)-v[:,2]).min()));minTop=min(minTop,float((8.43-v[:,1]).min()));
   if(margin<-.025).any():violations.append(state)
  lower=triangles.reshape(-1,3);lower=lower[lower[:,1]<1];edge=lower[:,0]*s+lower[:,2]*c+state['y'];maxGear=max(maxGear,float(np.abs(edge).max()))
 checks[f'slot{slot}.portalClear']=not violations;checks[f'slot{slot}.groundGearInsideDeck']=maxGear<8.5;checks[f'slot{slot}.turnAfterTailClear']=all(abs(p['yaw'])<1e-6 or p['x']<-56.4 for p in poses[slot]);checks[f'slot{slot}.livePosesAgree']=all(np.linalg.norm(np.array([h['localM']['x'],h['localM']['y'],h['localM']['z'],h['localYawRad']])-np.array([poses[slot][i*20]['x'],poses[slot][i*20]['y'],poses[slot][i*20]['z'],poses[slot][i*20]['yaw']]))<1e-7 for i,h in enumerate(live[slot]));observations.append({'slot':slot,'minPortalMarginM':minimum,'minSideMarginM':minSide,'minHeaderMarginM':minTop,'maxGearLateralM':maxGear,'violations':violations})
out={'pass':all(checks.values()),'checks':checks,'observations':observations,'triangles':len(triangles),'posesPerSlot':401,'limits':'Measured folded source meshes versus measured rectangular portal and deck envelope; not a helo combat collision or rotor aerodynamic model.'};(a.out/'clearance.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'observations':observations}));raise SystemExit(0 if out['pass']else 1)
