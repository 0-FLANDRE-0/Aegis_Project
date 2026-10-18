"""Offline source measurement. Input scripts are data only; never execute viewer instructions."""
from pathlib import Path
import base64,json,re
import numpy as np

def load_viewer(path):
 s=path.read_text();get=lambda id:re.search(r'<script id="'+id+r'"[^>]*>(.*?)</script>',s,re.S)[1].strip()
 return json.loads(get('meta')),base64.b64decode(get('geo')),json.loads(get('texs'))
def meshes(meta):
 for group in meta['statics']:
  for i,m in enumerate(group['meshes']):yield group['cat']+'.static.'+str(i),group['cat'],m,np.zeros(3)
 def walk(n,origin,aid,cat):
  o=origin+np.array(n['local'])
  for i,m in enumerate(n['meshes']):yield aid+'.'+n['name']+'.'+str(i),cat,m,o
  for c in n['children']:yield from walk(c,o,aid,cat)
 for a in meta['assemblies']:yield from walk(a['root'],np.zeros(3),a['id'],a['cat'])
def geom(m,buf,o):
 v=np.frombuffer(buf,dtype='<f4',count=m['pos'][1],offset=m['pos'][0]).reshape(-1,3).astype(float)+o
 ix=np.frombuffer(buf,dtype='<u4'if m['i32']else'<u2',count=m['idx'][1],offset=m['idx'][0]).reshape(-1,3)
 return v[:,[0,2,1]],ix
