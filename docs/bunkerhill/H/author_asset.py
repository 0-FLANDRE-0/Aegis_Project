#!/usr/bin/env python3
"""Offline registration of the supplied CG-52 mesh. No live mesh physics reads."""
from pathlib import Path
import json, gzip, base64, re, hashlib, sys
import numpy as np
OUT=Path(__file__).resolve().parent
ROOT=Path(sys.argv[1])if len(sys.argv)>1 else OUT.parent/'geometry-source'
meta=json.loads((ROOT/'viewer-meta.json').read_text())
buf=(ROOT/'viewer-geo.bin').read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
def canonical(v):return np.asarray(v)[..., [0,2,1]]
def point(v):return dict(zip(('x','y','z'),map(float,v)))
def meshes(cat,mi):
    z=np.load(ROOT/f'components-{cat}-{mi}.npz')
    return z['vertices'],z['triangles'],z['labels']
def component(cat,mi,cid):
    v,t,l=meshes(cat,mi); tri=t[l==cid]
    return v[np.unique(tri)],v[tri]
def bounds(v):
    v=canonical(v);lo=v.min(axis=0);hi=v.max(axis=0)
    return {'center':point((lo+hi)/2),'half':point((hi-lo)/2),'min':point(lo),'max':point(hi)}
def tube(v,axis=None):
    if axis is None:
        _,ev=np.linalg.eigh(np.cov(v.T));axis=ev[:,-1]
        if axis[1]<0:axis=-axis
    axis=np.asarray(axis);axis/=np.linalg.norm(axis)
    dot=v@axis; span=dot.max()-dot.min()
    # Cap centroid is measured in the plane normal to the tube, not the AABB.
    cap=v[dot>dot.max()-.012].mean(axis=0)
    cap+=axis*(dot.max()-cap@axis)
    base=cap-axis*span
    return canonical(base),canonical(cap),canonical(axis)
contract={'schema':'AEGIS_CG52_OFFLINE_REGISTRATION_V1','id':'CG52_VIEWER5_SI_V1',
 'basis':'SUPPLIED_VIEWER_VERTICES__NOT_SHIPYARD_DRAWING','coordinateFrame':'SHIP_LOCAL_METRES_X_BOW_Y_STARBOARD_Z_UP',
 'sourceHtmlSha256':'402814f3d59fcec1e656cca7c825f5dd4f16c61db42be9913e8af87dfba996cc',
 'quantizationToleranceM':.004,'liveMeshReads':False,'sourceTriangles':meta['triangles'],'guns':{},'ciws':{},'spg':[],
 'spy':{},'cells':{},'ewPods':[],'occlusion':{'boxes':[]},'radars':[]}
asm={a['id']:a['root'] for a in meta['assemblies']}
for ident,key,neutral in [('mk45f','mk45',0),('mk45a','mk45Aft',np.pi)]:
    root=asm[ident];pitch=root['children'][0];off=canonical(pitch['local'])
    d=next(d for d in pitch['meshes'] if d['cls']=='std')
    v=np.frombuffer(buf,dtype=np.uint16,count=d['pos'][1],offset=d['pos'][0]).reshape(-1,3)*d['qscale']+d['qmin']
    rest=np.deg2rad(pitch['rest']);axis=np.array([np.cos(neutral)*np.cos(rest),np.sin(rest),0])
    barrel=float((v@axis).max())
    # Trunnion offset is specified in barrel azimuth coordinates for both mounts.
    off[0]=abs(off[0]);off[1]=abs(off[1])
    contract['guns'][key]={'id':ident,'yawNode':root['name'],'pitchNode':pitch['name'],
       'pivot':point(canonical(root['pivot'])),'trunnion':point(canonical(pitch['pivot'])),
       'trunnionOffsetM':point(off),'neutralAzRad':float(neutral),'barrelM':barrel,
       'restElevationRad':float(np.deg2rad(pitch['rest'])),'source':'VIEWER_ARTICULATED_PIVOTS'}
for ident,key,side in [('ciwss','phalanx',1),('ciwsp','phalanxPort',-1)]:
    root=asm[ident];pitch=root['children'][0]
    d=next(d for d in pitch['meshes'] if d['cls']=='std')
    v=np.frombuffer(buf,dtype=np.uint16,count=d['pos'][1],offset=d['pos'][0]).reshape(-1,3)*d['qscale']+d['qmin']
    # Central exit of the six source barrels; never borrow another asset's length.
    cap=v[v[:,2]*side>(v[:,2]*side).max()-.002].mean(axis=0)
    muzzle={'x':float(cap[2]*side),'y':float(-cap[0]*side),'z':float(cap[1])}
    contract['ciws'][key]={'id':ident,'x':root['pivot'][0],'y':root['pivot'][2],'z':pitch['pivot'][1],
       'yawNode':root['name'],'pitchNode':pitch['name'],'neutralAzRad':float(side*np.pi/2),
       'pivot':point(canonical(root['pivot'])),'pitchPivot':point(canonical(pitch['pivot'])),
       'muzzleOffsetLocalM':muzzle,'muzzleBasis':'SOURCE_SIX_BARREL_EXIT_CENTROID','outboardSide':side}
for i in range(4):
    root=asm[f'spg{i}'];v=canonical(root['pivot']);v[2]+=.95
    contract['spg'].append(list(map(float,v)))
for face,cid,az in [('F1',15,0),('F2',10,90),('F3',0,180),('F4',5,-90)]:
    v,tri=component('sensors',1,cid);tr=canonical(tri)
    cross=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);area=np.linalg.norm(cross,axis=1)
    # Swapping viewer Y/Z changes handedness; reverse the winding normal.
    n=-cross/np.maximum(area[:,None],1e-20);expected=np.array([np.cos(np.deg2rad(az)),np.sin(np.deg2rad(az)),0])
    # Octagonal front plane has the largest area facing outside the deckhouse.
    pick=(n@expected>.85)&(area>.05)
    normal=np.average(n[pick],axis=0,weights=area[pick]);normal/=np.linalg.norm(normal)
    center=np.average(tr[pick].mean(axis=1),axis=0,weights=area[pick])
    contract['spy'][face]={'center':list(map(float,center)),'normal':list(map(float,normal)),
       'half':[.20,2.05,2.05],'component':cid,'partId':f'CG52_SPY_{face}','source':'SENSOR_FRONT_FACE_AREA_WEIGHTED_PLANE'}
for vls in meta['vls']:
    sec='fwd' if vls['id']=='vlsf' else 'aft'
    contract['cells'][sec]=[{'x':c['hole'][0],'y':c['hole'][2],'z':c['hole'][1],
       'row':c['row'],'col':c['col'],'lidId':c['node'],'holeSizeM':c['hole'][3:]} for c in vls['cells']]
for i,cid in enumerate([1416,1417]):
    v,_=component('fittings',3,cid);b=bounds(v)
    side=1 if b['center']['y']>0 else -1
    contract['ewPods'].append({'id':'SLQ32_STBD' if side>0 else 'SLQ32_PORT','name':'AN/SLQ-32(우현)' if side>0 else 'AN/SLQ-32(좌현)',
       **b,'side':side,'component':cid,'beamCenterRad':float(side*np.pi/2),'beamHalfRad':float(np.deg2rad(115))})
srboc={'schema':'AEGIS_SRBOC_LAYOUT_WIP15A','revision':'CG52_SRBOC_4X6_VIEWER5_V1',
 'coordinateFrame':contract['coordinateFrame'],'basis':contract['basis'],'sourceBodySHA256':contract['sourceHtmlSha256'],'launchers':[]}
rows=[('PORT_1',[1624,1630,1632,1640,1644,1653]),('STBD_1',[1625,1631,1633,1641,1645,1654]),
      ('PORT_2',[1711,1721,1723,1733,1737,1748]),('STBD_2',[1712,1722,1724,1734,1738,1749])]
for ident,cids in rows:
    tubes=[];allv=[]
    for n,cid in enumerate(cids):
        v,_=component('fittings',3,cid);b,m,a=tube(v);allv.append(canonical(v))
        tubes.append({'id':f'T{n+1}','component':cid,'base':b,'muzzle':m,'axis':a})
    mount=np.concatenate(allv).mean(axis=0)
    srboc['launchers'].append({'id':ident,'label':ident.replace('_',' '),'side':ident.split('_')[0],
      'station':'CG52_OUTBOARD_ECM_SPONSON','mount':point(mount),'damageModule':'AN/SLQ-32(우현)' if ident.startswith('STBD') else 'AN/SLQ-32(좌현)',
      'tubes':[{'id':t['id'],'baseOffsetM':point(t['base']-mount),'muzzleOffsetM':point(t['muzzle']-mount),
        'massOffsetM':point((t['base']+t['muzzle'])/2-mount),'axisBody':point(t['axis']),'component':t['component'],
        'elevationDeg':float(np.rad2deg(np.arcsin(t['axis'][2]))),'azimuthDeg':float(np.rad2deg(np.arctan2(t['axis'][1],t['axis'][0])))} for t in tubes]})
nulka={'schema':'AEGIS_NULKA_LAYOUT_WIP15B','revision':'CG52_NULKA_4X2_VIEWER5_V1',
 'coordinateFrame':contract['coordinateFrame'],'basis':contract['basis'],'launchers':[]}
for ident,cid in [('PORT_1',974),('PORT_2',1686),('STBD_1',1923),('STBD_2',1972)]:
    v,_=component('fittings',3,cid);side=-1 if ident.startswith('PORT') else 1
    axis=np.array([0,np.cos(np.deg2rad(10)),side*np.sin(np.deg2rad(10))]);across=np.array([0,-axis[2],axis[1]])
    proj=v[:,0]; split=(proj.min()+proj.max())/2
    mount=canonical((v.min(axis=0)+v.max(axis=0))/2)
    tubes=[]
    for n,mask in enumerate([proj<split,proj>=split]):
        b,m,a=tube(v[mask],axis)
        tubes.append({'id':f'T{n+1}','baseOffsetM':point(b-mount),'muzzleOffsetM':point(m-mount),
          'massOffsetM':point((m+b)/2-mount),'axisBody':point(a),'elevationDeg':80.0,'azimuthDeg':side*90.0})
    nulka['launchers'].append({'id':ident,'label':ident.replace('_',' N'),'side':'PORT' if side<0 else 'STBD',
      'mount':point(mount),'damageModule':'상부구조(후방)' if cid==974 else '상부구조(전방)',
      'component':cid,'bodyFaces':[],'tubes':tubes,'axisBasis':'VIEWER_SIDE_PLANES_10_DEG_FROM_VERTICAL'})
contract['srboc']=srboc;contract['nulka']=nulka
# User-marked photograph resolves the actual front-mast antennas. Components
# 87/88 and 56/57 are fixed yardarms, and the large dome 744 is not this radar.
for ident,label,cid,module in [('SPQ9','AN/SPQ-9',120,'SPQ9_CG52_V1'),('SPS73','AN/SPS-73',122,'SPS73_CG52_V1')]:
    v,_=component('structure',2,cid);b=bounds(v)
    pivot=dict(b['center'])
    if ident=='SPQ9':pivot['z']=b['min']['z']
    contract['radars'].append({'id':ident,'label':label,**b,'rotorPivot':pivot,
      'category':'structure','mesh':2,'component':cid,'rotatingComponents':[cid],'moduleId':module,
      'fixedComponents':[87,88,94,97,118,123],
      'exactVariant':'SPQ9_FAMILY_USER_SELECTED_NON_B' if ident=='SPQ9' else 'SPS73_SUBVARIANT_PUBLIC_UNKNOWN',
      'locationBasis':'USER_ANNOTATED_FRONT_MAST_PHOTO_AND_SOURCE_COMPONENT',
      'rotationBasis':'ANTENNA_ONLY_FIXED_YARDARM_PLATFORM_RAILINGS_AND_DRIVE_BASE'})
groups=[];occluders=[]
for cat,mi,cids in [('hull',1,[0]),('structure',2,[0,6,21,23,32,41,61,84,87,88,96,97,101,103,105,120,137,140]),
 ('fittings',3,[744,824,861,1874,1973,2041])]:
    for cid in cids:
        v,tr=component(cat,mi,cid);t=canonical(tr)
        if cat=='hull':name='HULL:0'
        elif cid==0 and cat=='structure':name='DECKHOUSE:0'
        elif cid==6 and cat=='structure':name='AFT:0'
        elif cat=='fittings':name='FUNNEL:'+str(cid) if cid!=744 else 'FIXED_RADOME:744'
        elif cid==120:name='ANTENNA:SPQ9'
        else:name='MAST:'+str(cid)
        groups.append({'name':name,'triangles':np.round(t,6).reshape(-1).tolist()})
        occluders.append({'name':name,**bounds(v),'triangles':np.round(t,6).reshape(-1).tolist()})
for face,cid in [('F1',15),('F2',10),('F3',0),('F4',5)]:
    v,tr=component('sensors',1,cid);occluders.append({'name':'CG52_SPY_'+face,**bounds(v),
      'triangles':np.round(canonical(tr),6).reshape(-1).tolist()})
contract['occluders']=occluders
for o in occluders:
    c=o['center'];h=o['half'];contract['occlusion']['boxes'].append({'name':o['name'],'oX':c['x'],'oY':c['y'],
       'hL':h['x'],'hW':h['y'],'zMin':c['z']-h['z'],'zMax':c['z']+h['z']})
stats={'bounds':{'bow':86.396754,'stern':-86.06325},'stations':[], 'waterline':[]}
# Offline hull section intersections at authored stations. Physical hull excludes
# overhanging guard rails; sonar dome stays in collision but not nominal draft data.
tv=np.array(groups[0]['triangles']).reshape(-1,3,3)
for x in sorted(set([-86.06325,-85,-82,-78]+list(range(-74,83,4))+[86,86.396754])):
    p=[];xx=min(86.396744,max(-86.06324,x))
    for j in range(3):
        a=tv[:,j];b=tv[:,(j+1)%3];da=a[:,0]-xx;db=b[:,0]-xx;pick=da*db<0
        u=da[pick]/(da[pick]-db[pick]);p.extend((a[pick]+(b[pick]-a[pick])*u[:,None]).tolist())
    if not p:continue
    p=np.array(p);stats['stations'].append([x,float(np.abs(p[:,1]).max()),float(p[:,2].max()),float(p[:,2].min())])
    sea=[]
    for j in range(3):
        a=tv[:,j];b=tv[:,(j+1)%3];da=a[:,0]-xx;db=b[:,0]-xx;pick=da*db<0
        u=da[pick]/(da[pick]-db[pick]);# Actual waterplane extracted separately below.
    # For wake endpoints, broad model hull reaches the waterline at these X stations.
    if p[:,2].min()<0<p[:,2].max():stats['waterline'].append([x,float(np.abs(p[:,1]).max())])
source={'basis':contract['basis'],'groups':groups}
(OUT/'registration.json').write_text(json.dumps(contract,separators=(',',':')))
(OUT/'envelope.json').write_text(json.dumps({'source':source,'stats':stats},separators=(',',':')))
(OUT/'asset-meta.json').write_text(json.dumps(meta,separators=(',',':')))
(OUT/'asset-geo.gz').write_bytes(gzip.compress(buf,compresslevel=9,mtime=0))
(OUT/'asset-components.json').write_text(json.dumps({'structure':meshes('structure',2)[2].tolist()},separators=(',',':')))
print(json.dumps({'registrationBytes':(OUT/'registration.json').stat().st_size,'envelopeBytes':(OUT/'envelope.json').stat().st_size,
 'assetsGzipBytes':(OUT/'asset-geo.gz').stat().st_size,'guns':len(contract['guns']),'phalanx':len(contract['ciws']),
 'spg':len(contract['spg']),'vls':{k:len(v) for k,v in contract['cells'].items()},
 'nulka':[{'id':l['id'],'mount':l['mount']} for l in nulka['launchers']],
 'srboc':[{'id':l['id'],'mount':l['mount']} for l in srboc['launchers']]}))
