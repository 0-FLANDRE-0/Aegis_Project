"""Recover original Mk141 cover faces directly from pinned embedded CG geometry."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();h=Path(a.html).read_text()
def raw(id):return gzip.decompress(base64.b64decode(re.search(r'<script id="'+id+r'" type="application/octet-stream">(.*?)</script>',h,re.S)[1]))
meta=json.loads(raw('cg52-meta'));buf=raw('cg52-geo');reg=json.loads(raw('harpoon-launch-registration'));manifest=json.loads((HERE.parents[1]/'bunkerhill/K/assets-manifest.json').read_text())
assert hashlib.sha256(base64.b64decode(re.search(r'<script id="cg52-geo" type="application/octet-stream">(.*?)</script>',h,re.S)[1])).hexdigest()==next(r['sha256']for r in manifest['assets']if r['id']=='geo')
m=next(s for s in meta['statics']if s['cat']=='weapons')['meshes'][1]
v=np.frombuffer(buf,'<u2',count=m['pos'][1],offset=m['pos'][0]).reshape(-1,3)*np.array(m['qscale'])+np.array(m['qmin'])
t=np.frombuffer(buf,'<u4'if m['i32']else'<u2',count=m['idx'][1],offset=m['idx'][0]).reshape(-1,3);tri=v[t][:,:,[0,2,1]];rows=[];count={'A':0,'B':0}
cutPolygons={};eye=np.eye(3)
def clip(poly,dist,inside):
 out=[]
 for i,a in enumerate(poly):
  b=poly[(i+1)%len(poly)];da,db=dist(a),dist(b);ina=da<=1e-10 if inside else da>=-1e-10;inb=db<=1e-10 if inside else db>=-1e-10
  if ina:out.append(a)
  if ina!=inb:out.append(a+(b-a)*(da/(da-db)))
 return out
def subtract(poly,planes,points):
 # Return a disjoint decomposition outside the convex bore prism.
 for n,c in planes:
  ds=[float((w@points)@n-c)for w in poly]
  if min(ds)>=-1e-9:return [poly],False
 inside=poly;outside=[]
 for n,c in planes:
  dist=lambda w:float((w@points)@n-c)
  q=clip(inside,dist,False)
  if len(q)>=3:outside.append(q)
  inside=clip(inside,dist,True)
  if len(inside)<3:break
 return outside,True
for s in reg['tubeRows']:
 axis=np.array(list(s['axis'].values()));mouth=np.array(list(s['muzzle'].values()));q=tri-mouth;ax=q@axis;rad=np.linalg.norm(q-ax[:,:,None]*axis,axis=2)
 front=np.where((ax.min(axis=1)>-.112)&(ax.max(axis=1)<.008)&(rad.max(axis=1)<.31))[0].tolist()
 rear=np.where((ax.max(axis=1)<-s['lengthM']+.012)&(ax.min(axis=1)>-s['lengthM']-.008)&(rad.max(axis=1)<.31))[0].tolist()
 count[s['bank']]+=1;assert len(front)==116 and len(rear)==58,(s['component'],len(front),len(rear));assert set(s['capFaces'])<=set(front)
 rows.append({'tubeId':'MK141-'+s['bank']+str(count[s['bank']]),'component':s['component'],'doorFaces':front,'rearFaces':rear})
 # The original rack plates cross the tube at ~1.00/1.08m depth. Cut only
 # their intersection with the hollow liner, keeping all support outside it.
 up=np.array([0.,0.,1.]);u=up-axis*(up@axis);u/=np.linalg.norm(u);w=np.cross(axis,u)
 radius=.245;lo=-s['lengthM']+.018;hi=-.112
 uq=q@u;wq=q@w
 normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(normals,axis=1)
 transverse=(np.abs(normals@axis)/np.maximum(1e-12,area)>.985)&(area>1e-10)
 candidate=np.where(transverse&(ax.max(axis=1)>lo)&(ax.min(axis=1)<hi)&(uq.min(axis=1)<radius)&(uq.max(axis=1)>-radius)&(wq.min(axis=1)<radius)&(wq.max(axis=1)>-radius))[0]
 planes=[(axis,float(mouth@axis+hi)),(-axis,float(-mouth@axis-lo))]
 for k in range(48):
  n=u*np.cos(k*np.pi/24)+w*np.sin(k*np.pi/24);planes.append((n,float(mouth@n+radius)))
 for i in candidate:
  old=cutPolygons.get(int(i),[list(eye)]);new=[];changed=False
  for poly in old:
   kept,did=subtract(poly,planes,tri[i]);new.extend(kept);changed|=did
  if changed:cutPolygons[int(i)]=new
cuts=[]
for i,polygons in sorted(cutPolygons.items()):
 triangles=[]
 for poly in polygons:
  for j in range(1,len(poly)-1):
   weights=np.array([poly[0],poly[j],poly[j+1]]);xyz=weights@tri[i]
   if np.linalg.norm(np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]))>1e-9:triangles.append(np.round(weights,10).tolist())
 cuts.append({'sourceFace':i,'triangles':triangles})
result={'schema':'CG52_MK141_HOLLOW_TUBES_B1','rows':rows,'supportBoreCuts':cuts,'supportBoreCutRadiusM':.245};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,separators=(',',':')))
known=HERE/'mouth-registration.json'
if known.exists()and a.out.resolve()!=known.resolve():assert result==json.loads(known.read_text())
print(json.dumps({'exact':True,'tubes':len(rows),'sourceFaces':sum(len(r['doorFaces'])+len(r['rearFaces'])for r in rows),'supportFacesCut':len(cuts),'supportTrianglesAfterCut':sum(len(c['triangles'])for c in cuts)}))
