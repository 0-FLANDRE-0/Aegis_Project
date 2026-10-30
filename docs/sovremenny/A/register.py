"""MODEL_REGISTRATION: offline v9.1 measurements; never consumes a live render mesh.
Hull skin is sliced at 1 m. A SIM_TUNED weather-deck cut excludes railings and
connected deckhouses from the buoyant envelope. Upper connected components are
retained as static convex damage envelopes, not functional installations.
"""
from pathlib import Path
import sys,json,hashlib,gzip
import numpy as np
from scipy.spatial import ConvexHull
from extract import load_viewer,meshes,geom
HERE=Path(__file__).resolve().parent
P=lambda x:np.round(x,5).tolist()
def components(v,ix):
 _,rm=np.unique(np.round(v,3),axis=0,return_inverse=True);par=np.arange(rm.max()+1)
 def find(a):
  while par[a]!=a:par[a]=par[par[a]];a=par[a]
  return a
 for t in rm[ix]:
  a=find(t[0]);par[find(t[1])]=a;par[find(t[2])]=a
 groups={}
 for i,t in enumerate(ix):groups.setdefault(int(find(rm[t[0]])),[]).append(i)
 return sorted([v[ix[ids]]for ids in groups.values()],key=lambda t:-len(t))
def section(tri,x,cap=100):
 pts=[]
 for t in tri[(tri[:,:,0].min(1)<=x)&(tri[:,:,0].max(1)>=x)]:
  hits=[]
  for a,b in zip(t,np.roll(t,-1,axis=0)):
   if (a[0]-x)*(b[0]-x)<0:hits.append((a+(b-a)*(x-a[0])/(b[0]-a[0]))[1:])
  for q in hits:
   if q[1]<=cap:pts.append(q)
  if len(hits)==2:
   a,b=hits
   if (a[1]-cap)*(b[1]-cap)<0:pts.append(a+(b-a)*(cap-a[1])/(b[1]-a[1]))
 if len(pts)<3:return None
 p=np.unique(np.round(pts,6),axis=0)
 try:return p[ConvexHull(p).vertices]
 except:return None
def ints(poly,y):
 hits=[]
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  if (a[0]-y)*(b[0]-y)<0:hits.append(a[1]+(b[1]-a[1])*(y-a[0])/(b[0]-a[0]))
 return [min(hits),max(hits)]if len(hits)>1 else None

def main(path):
 meta,buf,tex=load_viewer(path);source=[];rows=[];hull=None;upper=[];parked=[]
 for name,cat,m,o in meshes(meta):
  v,ix=geom(m,buf,o);t=v[ix];lo=t.reshape(-1,3).min(0);hi=t.reshape(-1,3).max(0)
  rows.append(dict(id=name,category=cat,min=P(lo),max=P(hi),triangles=len(ix)))
  if name=='hull.static.0':hull=components(v,ix)[0]
  if cat=='structure':upper.extend(components(v,ix))
  if '.static.'not in name:parked.append((name,cat,t))
 xs=np.linspace(-78.2499,78.2499,158);secs=[];columns=[]
 for x in xs:
  cap=float(np.interp(x,[30,60,78.25],[4.9,8.3,10.1]));poly=section(hull,x,cap)
  if poly is not None:secs.append({'x':round(x,5),'poly':P(poly)})
 # Hydro grid: exact vertical intersections of static sectional skin; no live geometry.
 nx=157;dx=156.5/nx
 for x in (-78.25+(np.arange(nx)+.5)*dx):
  p=section(hull,x,float(np.interp(x,[30,60,78.25],[4.9,8.3,10.1])))
  if p is None:continue
  width=max(abs(p[:,0]));ny=max(2,2*int(np.ceil(width/.5)));dy=2*width/ny
  for y in (-width+(np.arange(ny)+.5)*dy):
   a=ints(p,y)
   if a:columns.append(dict(x=float(x),y=float(y),bottom=a[0],top=a[1],area=dx*dy))
 vol=sum(max(0,min(0,c['top'])-c['bottom'])*c['area']for c in columns)
 factor=7940000/(1025*vol)
 wet=[(max(0,min(0,c['top'])-c['bottom'])*c['area'],c)for c in columns]
 cgx=sum(v*c['x']for v,c in wet)/vol
 # Connected portions above weather deck in the main hull mesh contain the bridge.
 hi_tri=hull[(hull[:,:,2].min(1)>4.9)&(hull[:,:,0].max(1)<40)]
 upper.extend(components(hi_tri.reshape(-1,3),np.arange(len(hi_tri)*3).reshape(-1,3)))
 groups=[];boxes=[]
 # MODEL_REGISTRATION: resample each measured closed section perimeter, then loft.
 rings=[]
 for q in secs:
  p=np.array(q['poly']);delta=np.roll(p,-1,axis=0)-p;length=np.linalg.norm(delta,axis=1);cum=np.r_[0,np.cumsum(length)];ring=[]
  for d in np.arange(64)*cum[-1]/64:
   k=min(len(p)-1,np.searchsorted(cum,d,side='right')-1);v=p[k]+delta[k]*(d-cum[k])/max(1e-12,length[k]);ring.append([q['x'],*v])
  rings.append(np.array(ring))
 skin=[]
 for a,b in zip(rings,rings[1:]):
  for i in range(64):
   j=(i+1)%64;skin.extend([a[i],a[j],b[j],a[i],b[j],b[i]])
 groups.append({'name':'HULL_SOURCE_LOFT','triangles':P(np.array(skin).reshape(-1))})
 for i,t in enumerate(upper):
  if len(t)<16:continue
  v=np.unique(np.round(t.reshape(-1,3),5),axis=0)
  try:ch=ConvexHull(v)
  except:continue
  lo=v.min(0);hi=v.max(0)
  if ch.volume<2 or min(hi-lo)<.7:continue
  groups.append({'name':'DECKHOUSE_'+str(i),'triangles':P(v[ch.simplices].reshape(-1))})
  boxes.append(dict(name='상부구조 '+str(i),oX=float((lo[0]+hi[0])/2),oY=float((lo[1]+hi[1])/2),hL=float((hi[0]-lo[0])/2),hW=float((hi[1]-lo[1])/2),zMin=float(lo[2]),zMax=float(hi[2]),system='STRUCTURE',targetId='SOV_STRUCT_'+str(i)))
 # MODEL_REGISTRATION: parked hardware has physical collision volume but no
 # sensor/weapon function. Propeller/shaft envelopes do not inflate buoyancy.
 for name,cat,t in parked:
  v=np.unique(np.round(t.reshape(-1,3),5),axis=0)
  try:ch=ConvexHull(v)
  except:continue
  if ch.volume<.001:continue
  groups.append({'name':'HARDWARE_'+name,'triangles':P(v[ch.simplices].reshape(-1))})
  if cat=='hull':
   lo=v.min(0);hi=v.max(0);boxes.append(dict(name='추진축 '+name,oX=float((lo[0]+hi[0])/2),oY=float((lo[1]+hi[1])/2),hL=float((hi[0]-lo[0])/2),hW=float((hi[1]-lo[1])/2),zMin=float(lo[2]),zMax=float(hi[2]),system='SHAFT_P'if lo[1]+hi[1]<0 else'SHAFT_S',targetId='SOV_SHAFT_'+name))
 # Upper mast/radar masses remain inactive physical reflectors, even when not solid deckhouses.
 for r in rows:
  if r['category'] not in ['sensors','weapons']:continue
  lo=np.array(r['min']);hi=np.array(r['max'])
  if min(hi-lo)<.15:continue
  boxes.append(dict(name='비활성 '+r['id'],oX=float((lo[0]+hi[0])/2),oY=float((lo[1]+hi[1])/2),hL=float((hi[0]-lo[0])/2),hW=float((hi[1]-lo[1])/2),zMin=float(lo[2]),zMax=float(hi[2]),system='STRUCTURE',targetId='SOV_INACTIVE_'+str(len(boxes))))
 # Finite stations for common longitudinal strength and ISAR hull length.
 stations=[]
 for q in secs[::4]+[secs[-1]]:
  p=np.array(q['poly']);stations.append([q['x'],float(max(abs(p[:,0]))),float(max(p[:,1])),float(min(p[:,1]))])
 stations[0][0]=-78.25;stations[-1][0]=78.25
 # 8 x 3 common flood parent grid. Functional topology below is explicitly SIM_TUNED.
 divisions=[-78.25,-58,-38,-18,2,22,42,62,78.25]
 for i,(a,b)in enumerate(zip(divisions,divisions[1:])):
  mid=(a+b)/2;p=section(hull,mid,4.8);w=max(abs(p[:,0]));z0=min(p[:,1]);
  boxes.append(dict(name='선체 '+str(i+1),oX=mid,oY=0,hL=(b-a)/2,hW=float(w),zMin=float(z0),zMax=4.5,system='HULL_SKIN',targetId='SOV_HULL_'+str(i)))
 inactive=[]
 for a in meta['assemblies']:
  o=np.array(a['root']['local'])[[0,2,1]]
  inactive.append({'id':a['id'],'label':a['label'],'positionM':P(o),'installed':False,'active':False,'emitter':False,'source':'MODEL_REGISTRATION','registration':a})
 waterline=[]
 for q in secs:
  poly=np.array(q['poly']);hits=[]
  for a,b in zip(poly,np.roll(poly,-1,axis=0)):
   if a[1]*b[1]<0:hits.append(a[0]+(b[0]-a[0])*(-a[1])/(b[1]-a[1]))
  if len(hits)>1:waterline.append([q['x'],max(abs(np.array(hits)))])
 # MODEL_REGISTRATION projected silhouette union, 1 m offline raster. All
 # above-water static envelope groups + parked hardware; overlapping areas once.
 cloud=[]
 for g in groups:
  tri=np.array(g['triangles']).reshape(-1,3,3);v=tri.reshape(-1,3);pts=[v[v[:,2]>=0]]
  for k in range(3):
   a,b=tri[:,k],tri[:,(k+1)%3];cross=a[:,2]*b[:,2]<0;a,b=a[cross],b[cross]
   if len(a):pts.append(a+(b-a)*(-a[:,2]/(b[:,2]-a[:,2]))[:,None])
  pts=np.concatenate(pts)
  if len(pts)>3:cloud.append(pts)
 for r in rows:
  if r['category'] in ['sensors','weapons']:
   lo,hi=np.array(r['min']),np.array(r['max']);cloud.append(np.array([[x,y,z]for x in [lo[0],hi[0]]for y in [lo[1],hi[1]]for z in [max(0,lo[2]),hi[2]]]))
 areas=[]
 for deg in range(0,360,15):
  az=np.deg2rad(deg);polys=[]
  for v in cloud:
   p=np.unique(np.round(np.c_[-v[:,0]*np.sin(az)+v[:,1]*np.cos(az),v[:,2]],4),axis=0)
   try:polys.append(ConvexHull(p))
   except:pass
  xmin=min(p.points[:,0].min()for p in polys);xmax=max(p.points[:,0].max()for p in polys);xx,zz=np.meshgrid(np.arange(np.floor(xmin)+.5,np.ceil(xmax),1),np.arange(.5,31,1));points=np.c_[xx.ravel(),zz.ravel()];inside=np.zeros(len(points),bool)
  for h in polys:inside|=np.all(points@h.equations[:,:2].T+h.equations[:,2]<=1e-8,axis=1)
  areas.append([deg,int(inside.sum())])
 data=dict(projectedAreaLut=areas,projectedAreaBasis='MODEL_REGISTRATION_ABOVE_WATER_STATIC_ENVELOPE_UNION_1M_RASTER__NO_LIVE_MESH',waterline=P(waterline),schema='SOVREMENNY_OFFLINE_REGISTRATION_A_1',source='MODEL_REGISTRATION',sourceFile=path.name,sourceSha256=hashlib.sha256(path.read_bytes()).hexdigest(),axes='sim=(viewer.x,viewer.z,viewer.y)',verticalDatum='AUTHORED_WATERLINE_Z0__NO_VERTICAL_OFFSET',lengthM=156.5,beamM=17.2,modelHullBeamM=17.48654,mastHeightM=meta['bounds'][1][1],sourceTriangles=sum(r['triangles']for r in rows),declaredTriangles=meta['triangles'],meshBatches=len(rows),stations=P(stations),sections=secs,groups=groups,hitboxes=boxes,hydroColumns=[{k:round(float(v),7)for k,v in c.items()}for c in columns],hydroCalibration=dict(source='SIM_TUNED',rhoKgM3=1025,rawVolumeM3=vol,adoptedMassKg=7940000,effectiveBuoyancyScale=factor,referenceCGXM=cgx,explanation='effective column area = source area * mass/(rho*raw submerged volume); same skin/datum, effective displacement calibration, NOT a CG-induced buoyancy change'),inactiveHardpoints=inactive,sensorRegistration={**meta['simRegistration'],'sensors':[{**q,'active':False,'emitter':False,'installed':False}for q in meta['simRegistration']['sensors']],'active':False,'emitter':False},meshBounds=rows,attribution={'title':'Sovremenny-class destroyer','author':'SB-129','platform':'Sketchfab','sourceUrl':'https://sketchfab.com/3d-models/sovremenny-class-destroyer-d3c3426bc8c74918b18ce84999e94fb0','license':'CC BY 4.0','licenseUrl':'https://creativecommons.org/licenses/by/4.0/','changes':'Axis registration; static collision/hydro/ISAR extraction; game damage/paint/lighting integration. All articulated parts parked.'})
 (HERE/'registration.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
 for name,b in [('meta.json',json.dumps(meta,separators=(',',':')).encode()),('textures.json',json.dumps(tex,separators=(',',':')).encode()),('geometry.bin',buf)]:
  (HERE/(name+'.gz')).write_bytes(gzip.compress(b,9,mtime=0))
 print(json.dumps({k:data[k]for k in ['sourceTriangles','declaredTriangles','meshBatches','mastHeightM','hydroCalibration']}));print('groups',len(groups),'boxes',len(boxes),'cols',len(columns))
if __name__=='__main__':main(Path(sys.argv[1]))
