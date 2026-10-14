"""Reproduce measured metric hub axes/centres and blade radii from immutable HLA1."""
import argparse,gzip,json,struct
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def measure():
 raw=gzip.decompress((ROOT/'docs/helicopter/A/seahawk-render-a1.bin.gz').read_bytes());n=struct.unpack_from('<I',raw,4)[0];meta=json.loads(raw[8:8+n]);start=8+n+(-n)%4;parts={p['id']:p for p in meta['parts']};rig=json.loads((HERE/'rig.json').read_text());origin=np.array(rig['origin']);scale=np.array([rig['horizontalScale'],rig['verticalScale'],rig['horizontalScale']])
 def vertices(id):
  p=parts[id];out=[];m=np.array(p['matrix']).reshape((4,4),order='F')
  for r in p['primitives']:
   a=meta['accessors'][meta['meshes'][r['mesh']]['primitives'][r['primitive']]['attributes']['POSITION']];q=np.frombuffer(raw,dtype='<u2',count=a['count']*3,offset=start+a['offset']).reshape(-1,3);q=np.asarray(a['min'])+q*np.asarray(a['scale']);out.extend((m@np.column_stack([q,np.ones(len(q))]).T).T[:,:3])
  return np.array(out)
 measured={}
 for name in ['main','tail']:
  ref=rig['rotors'][name];q=vertices(ref['hubSourcePart']);_,_,axes=np.linalg.svd(q-q.mean(0));axis=axes[-1];axis*=1 if axis[1 if name=='main'else 2]>0 else -1;axis/=scale;axis/=np.linalg.norm(axis);center=(q.max(0)+q.min(0))/2;centreM=(center-origin)*scale;blades=(np.concatenate([vertices(id)for id in ref['bladeIds']])-origin)*scale-centreM;radial=blades-(blades@axis)[:,None]*axis;measured[name]={'axis':axis.tolist(),'centerM':centreM.tolist(),'radiusM':float(np.linalg.norm(radial,axis=1).max())}
 return rig,measured

def main():
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);rig,measured=measure();checks={name:all(np.allclose(measured[name][k],rig['rotors'][name][k],rtol=0,atol=1e-10)for k in ['axis','centerM','radiusM'])for name in measured};out={'pass':all(checks.values()),'checks':checks,'measured':measured,'basis':'Extracted immutable HLA1 hub PCA, inverse transpose normal into metric body space, maximum perpendicular blade radius.'};(a.out/'rig-source.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks)}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
