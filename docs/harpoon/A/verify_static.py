"""Validate packing, unchanged baselines, SI assets and the guidance truth boundary."""
import argparse,base64,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('baseline');ap.add_argument('out');a=ap.parse_args()
source,baseline,out=map(Path,[a.html,a.baseline,a.out]);out.mkdir(parents=True,exist_ok=True)
checks={}
def unpack(p):
 h=p.read_text();blobs={int(i):base64.b64decode(s)for i,s in re.findall(r'<script type="application/octet-stream" data-c55-index="(\d+)">(.*?)</script>',h,re.S)}
 return h,blobs,json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1])
h,blobs,records=unpack(source);old,oldblobs,_=unpack(baseline);main=gzip.decompress(blobs[13]).decode();previous=gzip.decompress(oldblobs[13]).decode()
checks['approvedKExact']=hashlib.sha256(baseline.read_bytes()).hexdigest()=='efe1a0994f172da878733023826e9383ed0aed3c8c9601d10177a5d9faf287df'
checks['records0Through12ByteUnchanged']=all(blobs[i]==oldblobs[i]for i in range(13))
for i,row in enumerate(records):
 raw=gzip.decompress(blobs[i]);checks['recordIntegrity'+str(i)]=len(raw)==row['rawBytes']and len(blobs[i])==row['gzipBytes']and hashlib.sha256(raw).hexdigest()==row['sha256']
def profile(text):
 start=text.index('const DDG_119_LATE_FLIGHT_IIA_PROFILE=');end=text.index('\n}));',start)+len('\n}));');return text[start:end]
checks['ddgImmutableProfileUnchanged']=profile(main)==profile(previous)
def legacy_function(text,name):
 start=text.index('  function '+name+'(');end=text.index('\n  function ',start+1);return text[start:end]
for name in ['asmAirDensityKgM3','createAsmFlightState','updateAsmFlightPhysics','updateEnemyMissile']:
 checks['legacyUnchanged_'+name]=legacy_function(main,name)==legacy_function(previous,name)
def asm_profile(text):
 start=text.index('  const ASM_PROFILES');end=text.index('  // ===== WIP112 ASM SYSTEM',start);return text[start:end]
checks['kh35AndKh32ProfilesByteUnchanged']=asm_profile(main)==asm_profile(previous)
for id in ['registration','envelope','meta','components','projection','geo']:
 get=lambda text:re.search(r'<script id="cg52-'+id+r'" type="application/octet-stream">(.*?)</script>',text,re.S)[1]
 checks['cgSourceAssetUnchanged_'+id]=get(h)==get(old)
assets={}
for id,name,binary in [('harpoon-launch-registration','launcher-registration.json',False),('harpoon-model-meta','model-meta.json',False),('harpoon-model-geo','model-geo.gz',True)]:
 packed=base64.b64decode(re.search(r'<script id="'+id+r'" type="application/octet-stream">(.*?)</script>',h,re.S)[1]);raw=gzip.decompress(packed)
 expected=(HERE/name).read_bytes();checks[id+'Exact']=packed==expected if binary else raw==expected
 assets[id]=raw if binary else json.loads(raw)
meta=assets['harpoon-model-meta'];buf=assets['harpoon-model-geo'];triangle_count=0;finite=True;indices=True;tip=0
for m in meta['meshes']:
 p=np.frombuffer(buf,'<f4',count=m['pos'][1],offset=m['pos'][0]).reshape(-1,3)
 n=np.frombuffer(buf,'<f4',count=m['nor'][1],offset=m['nor'][0]).reshape(-1,3)
 ix=np.frombuffer(buf,'<u4',count=m['idx'][1],offset=m['idx'][0]);triangle_count+=ix.size//3
 finite=finite and np.isfinite(p).all()and np.isfinite(n).all();indices=indices and int(ix.max())<len(p)and ix.size%3==0
 if m['role']=='WING':
  q=p+np.array(m['pivot']);tip=max(tip,float(np.linalg.norm(q[:,1:],axis=1).max()))
checks['modelAllBuffersFinite']=bool(finite);checks['modelIndicesValid']=bool(indices)
checks['source24133TrianglesPreserved']=triangle_count==24133
checks['mainWingSpanPublic0914m']=abs(tip*2-.914)<1e-6
checks['modelFourSeparateWingsAndTails']=all(sum(m['role']==role for m in meta['meshes'])==4 for role in ['WING','TAIL'])
checks['attributionAndLicense']=meta['attribution']['author']=='Civorsky'and meta['attribution']['license']=='CC BY 4.0'and 'Civorsky' in h and 'creativecommons.org/licenses/by/4.0/'in h
register=assets['harpoon-launch-registration'];rows=register['tubeRows'];checks['eightDisjointSourceCaps']=len(rows)==8 and len(set(x for t in rows for x in t['capFaces']))==272
checks['eightCanisterFitLength']=all(t['lengthM']>4.63 for t in rows)
def body(name):
 start=main.index('function '+name+'(');end=main.index('\nfunction ',start+1);return main[start:end]
checks['guidanceHasNoLiveTrackOrTargetAccess']=all(not re.search(r'tracks\.(get|values|entries)|surfaceContacts|targetPool|_truthObject|targetRuntime|\.entityId',body(name))for name in ['harpoonPredictionA','harpoonSeekerA','harpoonFlightStepA'])
checks['rendererNoFlightOrDamageIntegration']=not re.search(r'harpoon(FlightStep|Step|Impact|Release|Seeker|RequestFire)A\(',Path(HERE/'renderer.js').read_text())
ids=re.findall(r'\bid="([^"]+)"',h)
checks['newUiIdsUnique']=all(ids.count(id)==1 for id in ['harpoonControlsA','harpoonTubeA','harpoonFireA','harpoonStatusA'])
scripts=[gzip.decompress(blobs[i]).decode()for i,r in enumerate(records)if r['type']in ['text/javascript','application/javascript','module']]
scripts += [s for attrs,s in re.findall(r'<script\b([^>]*)>(.*?)</script\s*>',h,re.S|re.I)if not any(t in attrs for t in ['application/octet-stream','application/json','text/plain'])]
with tempfile.TemporaryDirectory()as tmp:
 for i,script in enumerate(scripts):
  p=Path(tmp)/f'{i}.js';p.write_text(script);run=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
  checks['syntax'+str(i)]=run.returncode==0
  if run.returncode:print(run.stderr[:1000])
 rebuilt=Path(tmp)/'candidate.html';run=subprocess.run(['python',str(HERE/'build.py'),'--out',str(rebuilt)],capture_output=True,text=True)
 checks['exactReproducibleBuild']=run.returncode==0 and rebuilt.read_bytes()==source.read_bytes()
result={'schema':'HARPOON_A_STATIC_VERIFICATION','source':source.name,'bytes':source.stat().st_size,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'checks':checks,'pass':all(checks.values())}
(out/'static.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(0 if result['pass']else 1)
