import json,hashlib,struct
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
G=json.loads((ROOT/'source.gltf.json').read_text());B=(ROOT/'source.bin').read_bytes()
TYPES={5120:np.int8,5121:np.uint8,5122:np.dtype('<i2'),5123:np.dtype('<u2'),5125:np.dtype('<u4'),5126:np.dtype('<f4')};SIZES={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def accessor(i):
 a=G['accessors'][i];v=G['bufferViews'][a['bufferView']];dt=np.dtype(TYPES[a['componentType']]);size=SIZES[a['type']];stride=v.get('byteStride',dt.itemsize*size);off=v.get('byteOffset',0)+a.get('byteOffset',0);return np.ndarray((a['count'],size),dtype=dt,buffer=B,offset=off,strides=(stride,dt.itemsize)).copy()
def local(n):
 if 'matrix'in n:return np.asarray(n['matrix']).reshape((4,4),order='F')
 m=np.eye(4);m[:3,3]=n.get('translation',[0,0,0]);q=n.get('rotation',[0,0,0,1]);x,y,z,w=q
 r=np.asarray([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
 m[:3,:3]=r@np.diag(n.get('scale',[1,1,1]));return m
PARENTS={c:i for i,n in enumerate(G['nodes'])for c in n.get('children',[])};WORLD={}
def world(i):
 if i not in WORLD:WORLD[i]=(world(PARENTS[i])if i in PARENTS else np.eye(4))@local(G['nodes'][i])
 return WORLD[i]
def descendants(i):
 out=[i]
 for c in G['nodes'][i].get('children',[]):out+=descendants(c)
 return out
def mesh_rows(i):
 n=G['nodes'][i];rows=[]
 if 'mesh'not in n:return rows
 for j,p in enumerate(G['meshes'][n['mesh']]['primitives']):
  pos=accessor(p['attributes']['POSITION']);xyz=pos@world(i)[:3,:3].T+world(i)[:3,3];ind=accessor(p['indices']).ravel()if'indices'in p else np.arange(len(pos));rows.append({'node':i,'mesh':n['mesh'],'primitive':j,'vertices':len(pos),'triangles':len(ind)//3,'material':p.get('material'),'min':xyz.min(axis=0).tolist(),'max':xyz.max(axis=0).tolist(),'center':xyz.mean(axis=0).tolist(),'attrs':list(p['attributes'])})
 return rows
if __name__=='__main__':
 rows=[]
 for i in G['nodes'][2]['children']:
  if i<12663:continue
  rr=[r for c in descendants(i)for r in mesh_rows(c)];lo=np.min([r['min']for r in rr],axis=0);hi=np.max([r['max']for r in rr],axis=0);row={'group':i,'name':G['nodes'][i]['name'],'meshes':len(rr),'tris':sum(r['triangles']for r in rr),'materials':sorted(set(r['material']for r in rr)),'min':np.round(lo,3).tolist(),'max':np.round(hi,3).tolist(),'center':np.round((lo+hi)/2,3).tolist()};rows.append(row);print(json.dumps(row))
 (ROOT/'candidate-groups.json').write_text(json.dumps(rows,indent=2)+'\n')
