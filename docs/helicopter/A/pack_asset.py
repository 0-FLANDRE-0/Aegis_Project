"""Aegis-friendly Q16 positions/SNORM16 normals, unchanged topology/materials.
Keep lossless GLB separately. Error is measured against original float data.
"""
import base64,gzip,hashlib,json,struct
from pathlib import Path
import numpy as np
from inspect_asset import ROOT,G,B,world,accessor,descendants
from extract_helicopter import GROUPS,SELECTED

def main():
 doc=json.loads((ROOT/'helicopter-options.gltf.json').read_text());binary=(ROOT/'helicopter-options.bin').read_bytes();packed=bytearray();rows=[];worstLocal=0;worstNormal=0
 normalIds={p['attributes']['NORMAL']for m in doc['meshes']for p in m['primitives']};positionIds={p['attributes']['POSITION']for m in doc['meshes']for p in m['primitives']}
 for ai,a in enumerate(doc['accessors']):
  dt={5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];size={'SCALAR':1,'VEC3':3,'VEC2':2}[a['type']];v=doc['bufferViews'][a['bufferView']];arr=np.frombuffer(binary,dtype=dt,count=a['count']*size,offset=v['byteOffset']).reshape((-1,size));row={'count':a['count'],'itemSize':size}
  if a['type']=='SCALAR':raw=arr.astype('<u2').tobytes();row['codec']='U16'
  elif ai in positionIds:
   lo=arr.min(axis=0).astype(np.float64);hi=arr.max(axis=0).astype(np.float64);span=hi-lo;q=np.rint(np.divide(arr-lo,span,out=np.zeros_like(arr,dtype=np.float64),where=span!=0)*65535).astype('<u2');decoded=(lo+q.astype(np.float64)*span/65535).astype('<f4');worstLocal=max(worstLocal,float(np.max(np.linalg.norm(decoded-arr,axis=1))));raw=q.tobytes();row.update(codec='Q16',min=lo.tolist(),scale=(span/65535).tolist())
  else:
   assert size==3;raw=np.rint(np.clip(arr,-1,1)*32767).astype('<i2').tobytes();decoded=np.frombuffer(raw,dtype='<i2').reshape((-1,3)).astype(np.float64)/32767;orig=arr.astype(np.float64);dot=np.einsum('ij,ij->i',orig,decoded);length=np.linalg.norm(orig,axis=1)*np.linalg.norm(decoded,axis=1);angle=np.degrees(np.arccos(np.clip(np.divide(dot,length,out=np.ones_like(dot),where=length>0),-1,1)));worstNormal=max(worstNormal,float(angle.max()));row['codec']='SNORM16'
  packed.extend(b'\0'*((-len(packed))%4));row['offset']=len(packed);row['bytes']=len(raw);packed.extend(raw);rows.append(row)
 usedmats=sorted({p['material']for i in SELECTED if'mesh'in G['nodes'][i]for p in G['meshes'][G['nodes'][i]['mesh']]['primitives']});matMap={i:j for j,i in enumerate(usedmats)};sourceMeshMap={};keyMap={}
 for mi,m in enumerate(doc['meshes']):keyMap[json.dumps(m,sort_keys=True)]=mi
 # Recover source mesh map by source node extras, kept in lossless extract.
 for n in doc['nodes']:
  if'mesh'in n:sourceMeshMap[G['nodes'][n['extras']['sourceNode']]['mesh']]=n['mesh']
 parts=[];worstWorld=0
 for i in GROUPS:
  primitives=[]
  for child in descendants(i):
   n=G['nodes'][child]
   if'mesh'in n:
    assert np.allclose(world(child),world(i),atol=1e-12)
    mi=sourceMeshMap[n['mesh']];primitives.extend({'mesh':mi,'primitive':j}for j in range(len(doc['meshes'][mi]['primitives'])))
    for p in doc['meshes'][mi]['primitives']:
     ai=p['attributes']['POSITION'];a=doc['accessors'][ai];v=doc['bufferViews'][a['bufferView']];original=np.frombuffer(binary,dtype='<f4',offset=v['byteOffset'],count=a['count']*3).reshape((-1,3));r=rows[ai];q=np.frombuffer(packed,dtype='<u2',count=r['count']*3,offset=r['offset']).reshape((-1,3));decoded=(np.array(r['min'])+q*np.array(r['scale'])).astype('<f4');delta=(decoded-original)@world(i)[:3,:3].T;worstWorld=max(worstWorld,float(np.linalg.norm(delta,axis=1).max()))
  parts.append({'id':i,'name':G['nodes'][i]['name'],'matrix':world(i).reshape(16,order='F').tolist(),'primitives':primitives})
 def pick(a,b):return [i for i in GROUPS if a<=i<=b]
 variable=set(pick(12684,12727)+pick(12746,12754)+pick(12759,12767)+pick(12779,12834)+pick(12847,12882));common=[i for i in GROUPS if i not in variable]
 kits={'folded':common+pick(12684,12689)+[12704,12708,12712]+pick(12759,12767)+pick(12779,12805),'deployed':common+pick(12684,12689)+[12704,12708,12712]+pick(12746,12754)+pick(12808,12834),'flight':common+[12722,12727,12704,12715,12719]+pick(12847,12882)}
 asset={'schema':'AEGIS_SH60_RENDER_ASSET_A1','source':G['asset']['extras'],'sourceSha256':hashlib.sha256((ROOT/'source.glb').read_bytes()).hexdigest(),'attribution':'SB-129; CC BY4.0; extracted/repacked/Q16 coordinates/SNORM16 normals; source alternative visibility reconstructed.','coordinateSpace':'SOURCE_GLTF_WORLD_Y_UP_NEGATIVE_X_FORWARD','sourceUnitsToMeters':None,'originHint':[29.267,4.116,-.0746],'accessors':rows,'meshes':doc['meshes'],'materials':doc['materials'],'parts':parts,'poses':kits,'sharedParts':common,'physicalModel':'NOT_IMPLEMENTED','animations':'No source animation/skin; authored static alternatives and blur meshes only.'}
 meta=json.dumps(asset,separators=(',',':'),ensure_ascii=False).encode();raw=b'HLA1'+struct.pack('<I',len(meta))+meta+b'\0'*((-len(meta))%4)+packed;gz=gzip.compress(raw,9,mtime=0);(ROOT/'seahawk-render-a1.bin.gz').write_bytes(gz);(ROOT/'seahawk-render-a1.json').write_text(json.dumps(asset,ensure_ascii=False,indent=2)+'\n');(ROOT/'seahawk-render-a1.raw.bin').write_bytes(raw)
 metrics={'rawBytes':len(raw),'gzipBytes':len(gz),'base64Bytes':len(base64.b64encode(gz)),'positionMaxLocalError':worstLocal,'positionMaxSourceWorldError':worstWorld,'normalMaxAngleDegrees':worstNormal,'sourceUnitsToMeters':'Not certified; source GLB scale is retained.','sha256':hashlib.sha256(gz).hexdigest(),'parts':len(parts),'sharedParts':len(common),'poseParts':{k:len(v)for k,v in kits.items()},'triangles':sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes']for p in m['primitives'])};(ROOT/'packed-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps(metrics))
if __name__=='__main__':main()
