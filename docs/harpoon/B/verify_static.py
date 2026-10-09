"""Pin A; allow only B presentation and the explicit booster tuning changes."""
import argparse,base64,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('baseline');ap.add_argument('out');a=ap.parse_args();source,old,out=map(Path,[a.html,a.baseline,a.out]);out.mkdir(parents=True,exist_ok=True)
def unpack(p):
 h=p.read_text();blobs={int(i):base64.b64decode(s)for i,s in re.findall(r'<script type="application/octet-stream" data-c55-index="(\d+)">(.*?)</script>',h,re.S)}
 return h,blobs,json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1])
h,b,records=unpack(source);oldh,oldb,_=unpack(old);main=gzip.decompress(b[13]).decode();previous=gzip.decompress(oldb[13]).decode();checks={}
checks['approvedAExact']=hashlib.sha256(old.read_bytes()).hexdigest()=='ffd976a211c530bc4d193597751e49febbd755646b865e6ad2685cd9e06aab77'
checks['records0Through12Unchanged']=all(b[i]==oldb[i]for i in range(13))
for i,row in enumerate(records):
 raw=gzip.decompress(b[i]);checks['recordIntegrity'+str(i)]=len(raw)==row['rawBytes']and len(b[i])==row['gzipBytes']and hashlib.sha256(raw).hexdigest()==row['sha256']
normalized=main.replace((HERE/'renderer.js').read_text(),(HERE.parent/'A/renderer.js').read_text()).replace((HERE/'visual-profile.js').read_text()+'\n','')
normalized=normalized.replace("const harpoonVisualAuditB=harpoonVisualCoreAuditB();if(!harpoonVisualAuditB.pass)failures.push('HARPOON_VISUAL_B_CORE:'+JSON.stringify(harpoonVisualAuditB.checks));\n",'')
normalized=normalized.replace('V48_WIP_HARPOON_B','V48_WIP_HARPOON_A').replace('WIP HARPOON B','WIP HARPOON A')
normalized=normalized.replace("min:view.follow.enabled&&String(view.follow.key).startsWith('HARPOON:')?4:(view._c5Focus?8:18)",'min:view._c5Focus?8:18')
for module in ['profile.js','core.js']:
 normalized=normalized.replace((HERE/module).read_text(),(HERE.parent/'A'/module).read_text())
normalized=normalized.replace("revision:'BUNKERHILL_HARPOON_B_1'","revision:'BUNKERHILL_HARPOON_A_1'")
normalized=normalized.replace("[ACTIVE_SHIP_PROFILE.revision,'BUNKERHILL_HARPOON_A_1','BUNKERHILL_LATE_G_1','BUNKERHILL_LATE_D_1']","[ACTIVE_SHIP_PROFILE.revision,'BUNKERHILL_LATE_G_1','BUNKERHILL_LATE_D_1']")
checks['unrelatedSimulationAndRendererSourceByteUnchanged']=normalized==previous
allowedCore=(HERE.parent/'A/core.js').read_text().replace('HARPOON_PROFILE_A.public.boosterBurnS','HARPOON_PROFILE_A.sim.boosterBurnS').replace('pub.boosterBurnS','cfg.boosterBurnS').replace('m.boosterAttached?pub.boosterThrustN:','m.boosterAttached?cfg.boosterAverageThrustN:')
checks['onlyBoosterDurationThrustAndMassScheduleChangedInCore']=(HERE/'core.js').read_text()==allowedCore
ids=['cg52-registration','cg52-envelope','cg52-meta','cg52-components','cg52-projection','cg52-geo','harpoon-launch-registration','harpoon-model-meta','harpoon-model-geo']
for id in ids:
 pattern=r'<script id="'+id+r'" type="application/octet-stream">(.*?)</script>'
 checks['unchangedAsset_'+id]=re.search(pattern,h,re.S)[1]==re.search(pattern,oldh,re.S)[1]
reg=json.loads(gzip.decompress(base64.b64decode(re.search(r'<script id="harpoon-mouth-registration-b" type="application/octet-stream">(.*?)</script>',h,re.S)[1])))
checks['mouthRegistrationExact']=reg==json.loads((HERE/'mouth-registration.json').read_text())
faces=[x for r in reg['rows']for x in r['doorFaces']+r['rearFaces']]
checks['eightCompleteNonoverlappingMouths']=len(reg['rows'])==8 and len(faces)==len(set(faces))==1392
cuts=reg['supportBoreCuts'];cutIds=[r['sourceFace']for r in cuts]
checks['rackCutFacesSeparateFromDoors']=len(cutIds)==len(set(cutIds)) and not set(cutIds).intersection(faces) and reg['supportBoreCutRadiusM']==.245
checks['rackCutWeightsValid']=all(len(t)==3 and all(len(w)==3 and min(w)>=-1e-8 and abs(sum(w)-1)<1e-8 for w in t)for r in cuts for t in r['triangles'])
checks['rendererNoPhysicsWrites']=not re.search(r'harpoon(FlightStep|Step|Impact|Release|Seeker|RequestFire)A\(', (HERE/'renderer.js').read_text())
scripts=[gzip.decompress(b[i]).decode()for i,r in enumerate(records)if r['type']in ['text/javascript','application/javascript','module']]
scripts += [s for attrs,s in re.findall(r'<script\b([^>]*)>(.*?)</script\s*>',h,re.S|re.I)if not any(t in attrs for t in ['application/octet-stream','application/json','text/plain'])]
with tempfile.TemporaryDirectory()as tmp:
 for i,script in enumerate(scripts):
  path=Path(tmp)/f'{i}.js';path.write_text(script);q=subprocess.run(['node','--check',str(path)],capture_output=True,text=True);checks['syntax'+str(i)]=q.returncode==0
  if q.returncode:print(q.stderr)
 rebuilt=Path(tmp)/'candidate.html';q=subprocess.run(['python',str(HERE/'build.py'),'--baseline',str(old),'--out',str(rebuilt)],capture_output=True,text=True)
 checks['exactReproducibleBuild']=q.returncode==0 and rebuilt.read_bytes()==source.read_bytes()
report={'schema':'HARPOON_B_STATIC_VERIFICATION','source':source.name,'bytes':source.stat().st_size,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'checks':checks,'pass':all(checks.values())}
(out/'static.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'pass':report['pass'],'checks':checks}));raise SystemExit(0 if report['pass']else 1)
