"""Independent source-only rigid-part inventory across quantized vertex seams."""
from pathlib import Path
import array,gzip,hashlib,json,sys
here=Path(__file__).resolve().parent;meta=(here/'asset-meta.json').read_bytes();packed=(here/'asset-geo.gz').read_bytes();buf=gzip.decompress(packed);source=json.loads(meta);out=[]
def u16(offset,length):
    a=array.array('H');a.frombytes(buf[offset:offset+length*2])
    if sys.byteorder!='little':a.byteswap()
    return a
for i in range(4):
    m=next(a for a in source['assemblies']if a['id']=='spg'+str(i))['root']['meshes'][0];p=u16(*m['pos']);ix=u16(*m['idx']);weld={};vertex=[]
    for j in range(0,len(p),3):
        key=tuple(p[j:j+3]);vertex.append(weld.setdefault(key,len(weld)))
    parent=list(range(len(weld)))
    def find(k):
        while parent[k]!=k:parent[k]=parent[parent[k]];k=parent[k]
        return k
    for j in range(0,len(ix),3):
        root=find(vertex[ix[j]])
        for k in ix[j+1:j+3]:parent[find(vertex[k])]=root
    labels=[find(vertex[ix[j]])for j in range(0,len(ix),3)];components={}
    for j,label in enumerate(labels):
        c=components.setdefault(label,{'id':label,'triangles':0,'min':[float('inf')]*3,'max':[-float('inf')]*3});c['triangles']+=1
        for k in ix[j*3:j*3+3]:
            for axis in range(3):
                v=m['qmin'][axis]+p[k*3+axis]*m['qscale'][axis];c['min'][axis]=min(c['min'][axis],v);c['max'][axis]=max(c['max'][axis],v)
    out.append({'id':'spg'+str(i),'components':list(components.values()),'triangleLabels':labels})
result={'schema':'CG52_SOURCE_SPG_RIGID_COMPONENTS_I','assetMetaSha256':hashlib.sha256(meta).hexdigest(),'assetGeoGzipSha256':hashlib.sha256(packed).hexdigest(),'assemblies':out}
(here/'spg-rigid-components.json').write_text(json.dumps(result,separators=(',',':'))+'\n');print(json.dumps({'assemblies':len(out),'components':[len(q['components'])for q in out],'triangles':[len(q['triangleLabels'])for q in out]}))
