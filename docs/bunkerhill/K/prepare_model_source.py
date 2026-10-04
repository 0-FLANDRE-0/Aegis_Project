#!/usr/bin/env python3
"""Extract exact source mesh data and deterministic connected components."""
from pathlib import Path
import sys,re,json,gzip,base64,hashlib
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

src,out=map(Path,sys.argv[1:]);out.mkdir(parents=True,exist_ok=True)
raw=src.read_bytes()
if hashlib.sha256(raw).hexdigest()!='402814f3d59fcec1e656cca7c825f5dd4f16c61db42be9913e8af87dfba996cc':
 raise SystemExit('EXACT_SUPPLIED_VIEWER5_REQUIRED')
h=raw.decode();meta=json.loads(re.search(r'<script id="meta"[^>]*>(.*?)</script>',h,re.S)[1])
buf=gzip.decompress(base64.b64decode(re.search(r'<script id="geo"[^>]*>(.*?)</script>',h,re.S)[1]))
(out/'viewer-meta.json').write_text(json.dumps(meta,indent=2));(out/'viewer-geo.bin').write_bytes(buf)
for group in meta['statics']:
 for mi,m in enumerate(group['meshes']):
  if m.get('lines'):continue
  q=np.frombuffer(buf,dtype='<u2',count=m['pos'][1],offset=m['pos'][0]).reshape(-1,3)
  v=q*np.array(m['qscale'])+np.array(m['qmin'])
  ix=np.frombuffer(buf,dtype='<u4'if m['i32']else'<u2',count=m['idx'][1],offset=m['idx'][0]).reshape(-1,3)
  uniq,inv=np.unique(q,axis=0,return_inverse=True);tri=inv[ix]
  pairs=np.concatenate((tri[:,[0,1]],tri[:,[1,2]],tri[:,[0,2]]))
  graph=coo_matrix((np.ones(len(pairs),dtype=np.uint8),(pairs[:,0],pairs[:,1])),shape=(len(uniq),len(uniq)))
  _,labels=connected_components(graph,directed=False);tl=labels[tri[:,0]]
  np.savez_compressed(out/f"components-{group['cat']}-{mi}.npz",vertices=v,triangles=ix,labels=tl)
print(json.dumps({'viewerSha256':hashlib.sha256(raw).hexdigest(),'output':str(out),'geometryBytes':len(buf)}))
