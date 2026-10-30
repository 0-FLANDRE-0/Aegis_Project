"""Structural comparison against original upload and independent packed decoding."""
import gzip,hashlib,json,struct
from pathlib import Path
import numpy as np
from inspect_asset import ROOT,G,B,accessor,world,descendants,local
from extract_helicopter import GROUPS,SELECTED
from prepare_source import baseline_path
raw=(ROOT/'helicopter-options.glb').read_bytes();jn=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+jn]);data=raw[28+jn:];nodesBySource={n['extras']['sourceNode']:i for i,n in enumerate(g['nodes'])if'extras'in n};newParents={c:i for i,n in enumerate(g['nodes'])for c in n.get('children',[])};worlds={}
def nw(i):
 if i not in worlds:worlds[i]=(nw(newParents[i])if i in newParents else np.eye(4))@local(g['nodes'][i])
 return worlds[i]
def read(aid):
 a=g['accessors'][aid];v=g['bufferViews'][a['bufferView']];dt={5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];size={'SCALAR':1,'VEC3':3,'VEC2':2}[a['type']];return np.frombuffer(data,dtype=dt,count=a['count']*size,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape((-1,size))
checks={'sourcePinned':hashlib.sha256((ROOT/'source.glb').read_bytes()).hexdigest()=='69b83b51a9d3d9a50d5a5accba84c113ecd827e7e7e66af72fe1eaa55ade7013','noTexturePayload':not any(k in g for k in ['images','textures']),'sourceAnimationsAndSkinsAbsent':not G.get('animations')and not G.get('skins'),'selectedNodesOnly':set(nodesBySource)==set(SELECTED),'attributionRetained':all(g['asset']['extras'][k]==G['asset']['extras'][k]for k in ['author','license','source','title'])};materialIds=json.loads((ROOT/'extraction.json').read_text())['materials'];fail=[];triangleInstances=0;maxMatrixError=0
for old in SELECTED:
 new=nodesBySource[old];maxMatrixError=max(maxMatrixError,float(np.abs(nw(new)-world(old)).max()));node=G['nodes'][old]
 if'mesh'not in node:continue
 src=G['meshes'][node['mesh']]['primitives'];dst=g['meshes'][g['nodes'][new]['mesh']]['primitives'];assert len(src)==len(dst)
 for x,y in zip(src,dst):
  for k,i in x['attributes'].items():
   if not np.array_equal(accessor(i),read(y['attributes'][k])):fail.append((old,k))
  if not np.array_equal(accessor(x['indices']),read(y['indices'])):fail.append((old,'indices'))
  if G['materials'][x['material']]!=g['materials'][y['material']]:fail.append((old,'material'))
  triangleInstances+=G['accessors'][x['indices']]['count']//3
checks['allOriginalAttributesIndicesMaterialsExact']=not fail;checks['allWorldMatricesExactTolerance']=maxMatrixError<1e-12
packed=gzip.decompress((ROOT/'seahawk-render-a1.bin.gz').read_bytes());assert packed[:4]==b'HLA1';n=struct.unpack_from('<I',packed,4)[0];a=json.loads(packed[8:8+n]);start=8+n+(4-n%4)%4;decoded=[];maxPosition=0;maxNormal=0
for i,r in enumerate(a['accessors']):
 arr=np.frombuffer(packed,dtype='<i2'if r['codec']=='SNORM16'else'<u2',count=r['count']*r['itemSize'],offset=start+r['offset']).reshape((-1,r['itemSize']))
 if r['codec']=='Q16':arr=(np.array(r['min'])+arr*np.array(r['scale'])).astype('<f4');maxPosition=max(maxPosition,float(np.linalg.norm(arr-read(i),axis=1).max()))
 elif r['codec']=='SNORM16':arr=arr.astype(np.float64)/32767;orig=read(i).astype(np.float64);den=np.linalg.norm(orig,axis=1)*np.linalg.norm(arr,axis=1);c=np.divide(np.einsum('ij,ij->i',orig,arr),den,out=np.ones_like(den),where=den>0);maxNormal=max(maxNormal,float(np.degrees(np.arccos(np.clip(c,-1,1))).max()))
 else:assert np.array_equal(arr,read(i))
 decoded.append(arr)
checks['packedTopologyAndMaterialsExact']=a['meshes']==g['meshes']and a['materials']==g['materials'];checks['positionBoundedLocalError']=maxPosition<.00025;checks['normalBoundedAngle']=maxNormal<.002;checks['allPoseIdsUniqueValid']=all(len(v)==len(set(v))and set(v)<=set(GROUPS)for v in a['poses'].values());checks['commonPartsInAllPoses']=all(set(a['sharedParts'])<=set(v)for v in a['poses'].values());checks['noSceneCopyPerPose']='meshes'not in a['poses'];checks['simulatorUnchanged']=hashlib.sha256(baseline_path().read_bytes()).hexdigest()=='4571ed015469a48a0cc3ab96b4ee4e3d72c05257d2943a88fdd39272292583d5'
q={'checks':checks,'pass':all(checks.values()),'failed':fail,'sourceMeshInstances':137,'triangleInstances':triangleInstances,'maxWorldMatrixError':maxMatrixError,'maxLocalPositionError':maxPosition,'maxNormalAngleDegrees':maxNormal,'packedSha256':hashlib.sha256((ROOT/'seahawk-render-a1.bin.gz').read_bytes()).hexdigest()};(ROOT/'verification-structure.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q));raise SystemExit(0 if q['pass']else 1)
