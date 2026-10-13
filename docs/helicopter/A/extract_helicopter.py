"""Extract exact helicopter buffers; source document metadata is attribution only."""
import copy,base64,gzip,hashlib,json,struct
from pathlib import Path
import numpy as np
from inspect_asset import G,B,ROOT,accessor,world,descendants
GROUPS=[i for i in G['nodes'][2]['children']if i>=12669]
SELECTED=[c for i in GROUPS for c in descendants(i)]
def glb(doc,binary):
 j=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode();j+=b' '*((-len(j))%4);binary+=b'\0'*((-len(binary))%4);return struct.pack('<4sII',b'glTF',2,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary

def main():
 usedmats=sorted({p['material']for i in SELECTED if'mesh'in G['nodes'][i]for p in G['meshes'][G['nodes'][i]['mesh']]['primitives']});materialMap={i:j for j,i in enumerate(usedmats)}
 assert not any('baseColorTexture'in G['materials'][i]['pbrMetallicRoughness']for i in usedmats)
 binary=bytearray();views=[];accessors=[];accessorMap={};accessorHashes={};metrics={'rawSelectedAccessorBytes':0,'deduplicatedAccessorBytes':0};narrow=0
 def encodeAccessor(i):
  nonlocal narrow
  if i in accessorMap:return accessorMap[i]
  a=copy.deepcopy(G['accessors'][i]);arr=accessor(i);metrics['rawSelectedAccessorBytes']+=arr.nbytes
  if a['type']=='SCALAR'and a['componentType']==5125 and arr.max()<65536:arr=arr.astype('<u2');a['componentType']=5123;narrow+=1
  raw=arr.tobytes();meta={k:v for k,v in a.items()if k not in ['bufferView','byteOffset','name']};key=(json.dumps(meta,sort_keys=True),hashlib.sha256(raw).hexdigest())
  if key in accessorHashes:accessorMap[i]=accessorHashes[key];return accessorMap[i]
  binary.extend(b'\0'*((-len(binary))%4));off=len(binary);binary.extend(raw);v={'buffer':0,'byteOffset':off,'byteLength':len(raw),'target':34963 if a['type']=='SCALAR'else 34962};a['bufferView']=len(views);a.pop('byteOffset',None);views.append(v);idx=len(accessors);accessors.append(a);accessorHashes[key]=idx;accessorMap[i]=idx;metrics['deduplicatedAccessorBytes']+=len(raw);return idx
 meshMap={};meshes=[];meshHashes={}
 for ni in SELECTED:
  node=G['nodes'][ni]
  if'mesh'not in node:continue
  old=node['mesh'];m=copy.deepcopy(G['meshes'][old]);m.pop('name',None)
  for p in m['primitives']:
   assert not p.get('targets');p['attributes']={k:encodeAccessor(v)for k,v in p['attributes'].items()};p['indices']=encodeAccessor(p['indices']);p['material']=materialMap[p['material']]
  key=json.dumps(m,sort_keys=True)
  if key not in meshHashes:meshHashes[key]=len(meshes);meshes.append(m)
  meshMap[old]=meshHashes[key]
 nodeMap={old:i+1 for i,old in enumerate(SELECTED)};nodes=[{'name':'SH60_SOURCE_OPTIONS','children':[nodeMap[i]for i in GROUPS]}]
 for old in SELECTED:
  n=copy.deepcopy(G['nodes'][old]);n['extras']={'sourceNode':old,'sourceName':n.get('name','')}
  if old in GROUPS:n['matrix']=world(old).reshape(16,order='F').tolist();n.pop('translation',None);n.pop('rotation',None);n.pop('scale',None)
  if'children'in n:n['children']=[nodeMap[c]for c in n['children']]
  if'mesh'in n:n['mesh']=meshMap[n['mesh']]
  nodes.append(n)
 doc={'asset':copy.deepcopy(G['asset']),'scene':0,'scenes':[{'name':'All authored helicopter alternatives (overlap)','nodes':[0]}],'nodes':nodes,'meshes':meshes,'materials':[copy.deepcopy(G['materials'][i])for i in usedmats],'accessors':accessors,'bufferViews':views,'buffers':[{'byteLength':len(binary)}]}
 doc['asset']['extras']['extraction']='Helicopter groups12669 onward only; alternatives overlap in source; source transforms, vertices, normals, indices and material factors retained. Index width narrowed losslessly; exact buffers/meshes shared.'
 raw=glb(doc,bytes(binary));(ROOT/'helicopter-options.glb').write_bytes(raw);(ROOT/'helicopter-options.glb.gz').write_bytes(gzip.compress(raw,9,mtime=0));(ROOT/'helicopter-options.gltf.json').write_text(json.dumps(doc,indent=2)+'\n');(ROOT/'helicopter-options.bin').write_bytes(binary)
 metrics.update({'sourceBytes':(ROOT/'source.glb').stat().st_size,'groups':len(GROUPS),'sourceMeshInstances':sum('mesh'in G['nodes'][i]for i in SELECTED),'uniqueMeshes':len(meshes),'uniqueAccessors':len(accessors),'materials':usedmats,'textures':0,'narrowedIndexBuffers':narrow,'glbBytes':len(raw),'gzipBytes':(ROOT/'helicopter-options.glb.gz').stat().st_size,'htmlDataBase64Bytes':len(base64.b64encode(gzip.compress(raw,9,mtime=0))),'sha256':hashlib.sha256(raw).hexdigest()});(ROOT/'extraction.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps(metrics))
if __name__=='__main__':main()
