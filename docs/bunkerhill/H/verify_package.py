#!/usr/bin/env python3
from pathlib import Path
import base64,gzip,hashlib,json,re,subprocess,sys,tempfile
result,baseline=map(Path,sys.argv[1:]);checks={}
def read(p):
    h=p.read_text();blobs={int(i):base64.b64decode(s)for i,s in re.findall(r'<script type="application/octet-stream" data-c55-index="(\d+)">(.*?)</script>',h,re.S)}
    return h,blobs,json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1])
h,blobs,records=read(result);b,old,_=read(baseline)
checks['baselineHash']=hashlib.sha256(baseline.read_bytes()).hexdigest()=='94f5e9321fe1f04c5b43c4d8dca5b0762014c1cffe358ad92a81b8ffe70e7c92'
checks['allRecords']=set(blobs)==set(range(14))and len(records)==14
checks['embeddedAssetsUnchanged']=all(blobs[i]==old[i]for i in range(13))
main=gzip.decompress(blobs[13]).decode();prev=gzip.decompress(old[13]).decode()
def profile(s):
    start=s.index('const DDG_119_LATE_FLIGHT_IIA_PROFILE=')
    return s[start:s.index('\n}));',start)+len('\n}));')]
checks['immutableDdgProfileUnchanged']=profile(main)==profile(prev)
asset_map={'registration':'registration.json','envelope':'envelope.json','meta':'asset-meta.json','components':'asset-components.json','geo':'asset-geo.gz','projection':'projection.json'}
for ident,filename in asset_map.items():
    node=re.search(r'<script id="cg52-'+ident+r'" type="application/octet-stream">(.*?)</script>',h,re.S)
    raw=gzip.decompress(base64.b64decode(node[1]));expected=(Path(__file__).resolve().parent/filename).read_bytes()
    if ident=='geo':expected=gzip.decompress(expected)
    checks['cgAssetIntegrity_'+ident]=raw==expected
registration=json.loads(gzip.decompress(base64.b64decode(re.search(r'<script id="cg52-registration" type="application/octet-stream">(.*?)</script>',h,re.S)[1])))
checks['photoRadarParts']=len(registration['radars'])==2 and {r['id']:r['component'] for r in registration['radars']}=={'SPQ9':120,'SPS73':122}
checks['fullSourceGeometry']=registration['sourceTriangles']==767571
meta=json.loads(gzip.decompress(base64.b64decode(re.search(r'<script id="cg52-meta" type="application/octet-stream">(.*?)</script>',h,re.S)[1])))
def triangles(rec):return sum(m['idx'][1]//3 for m in rec['meshes'] if m.get('idx'))+sum(triangles(c)for c in rec.get('children',[]))
checks['indexedSourceTriangles']=sum(triangles(s)for s in meta['statics'])+sum(triangles(a['root'])for a in meta['assemblies'])==740819
projection=json.loads(gzip.decompress(base64.b64decode(re.search(r'<script id="cg52-projection" type="application/octet-stream">(.*?)</script>',h,re.S)[1])))
checks['cg2DSourceIdentity']=projection['profileId']=='CG_52_LATE_TICONDEROGA'and projection['sourceHtmlSha256']==registration['sourceHtmlSha256']and projection['indexedSourceTriangles']==740819
checks['cg2DImagesAndClips']=all(hashlib.sha256(base64.b64decode(projection[k]['image'].split(',',1)[1])).hexdigest()==projection[k]['imageSha256']and len(projection[k]['clipRects'])>0 for k in ['top','side'])
for i,row in enumerate(records):
    raw=gzip.decompress(blobs[i]);checks[f'recordIntegrity{i}']=hashlib.sha256(raw).hexdigest()==row['sha256']and len(raw)==row['rawBytes']and len(blobs[i])==row['gzipBytes']
with tempfile.TemporaryDirectory()as tmp:
    tmp=Path(tmp);scripts=[gzip.decompress(blobs[i]).decode()for i,r in enumerate(records)if r['type']in('text/javascript','application/javascript','module')]
    scripts+=[source for attrs,source in re.findall(r'<script\b([^>]*)>(.*?)</script\s*>',h,re.S|re.I)if not any(t in attrs for t in('application/octet-stream','application/json','text/plain'))]
    for i,s in enumerate(scripts):
        p=tmp/f'{i}.js';p.write_text(s);checks[f'syntax{i}']=subprocess.run(['node','--check',str(p)],capture_output=True).returncode==0
    rebuilt=tmp/'rebuilt.html';r=subprocess.run([sys.executable,str(Path(__file__).resolve().parent/'build_bunker.py'),str(baseline.resolve()),str(rebuilt)],capture_output=True)
    checks['exactRebuild']=r.returncode==0 and rebuilt.read_bytes()==result.read_bytes()
out={'schema':'AEGIS_BUNKERHILL_PACKAGE_V1','bytes':result.stat().st_size,'sha256':hashlib.sha256(result.read_bytes()).hexdigest(),'checks':checks,'passed':sum(checks.values()),'total':len(checks),'pass':all(checks.values())}
print(json.dumps(out,indent=2));raise SystemExit(0 if out['pass']else 1)
