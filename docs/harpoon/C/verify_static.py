"""C artifact syntax, immutable records/assets, allowed source delta and knowledge boundary."""
import argparse,base64,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
from build import patches,BASE,BASE_SHA
ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('out');ap.add_argument('--baseline',default=str(BASE));a=ap.parse_args()
p=Path(a.html);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);h=p.read_text();baseline=Path(a.baseline).read_text();checks={}
def check(k,v):checks[k]=bool(v)
def records(h):return json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1])
def source(h):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',h,re.S)[1])).decode()
bjs=source(baseline);js=source(h)
check('baselinePinned',hashlib.sha256(baseline.encode()).hexdigest()==BASE_SHA)
check('unchangedRecords0to12',records(h)[:13]==records(baseline)[:13])
for i,row in enumerate(records(h)):
 raw=gzip.decompress(base64.b64decode(re.search(r'data-c55-index="'+str(i)+r'">(.*?)</script>',h,re.S)[1]))
 check('record'+str(i)+'Integrity',len(raw)==row['rawBytes']and hashlib.sha256(raw).hexdigest()==row['sha256'])
with tempfile.TemporaryDirectory()as tmp:
 f=Path(tmp)/'main.mjs';f.write_text(js);r=subprocess.run(['node','--check',str(f)],capture_output=True,text=True);check('decodedMainSyntax',r.returncode==0)
 for i,m in enumerate(re.finditer(r'<script\b([^>]*)>(.*?)</script>',h,re.S)):
  if 'application/octet-stream'in m[1]or not m[2].strip():continue
  f=Path(tmp)/f'{i}.mjs';f.write_text(m[2]);r=subprocess.run(['node','--check',str(f)],capture_output=True,text=True)
  check('script'+str(i)+'Syntax',r.returncode==0)
 normalized=js.replace('V48_WIP_HARPOON_C','V48_WIP_HARPOON_B').replace('WIP HARPOON C','WIP HARPOON B')
 for old,new in reversed(patches()):
  assert normalized.count(new)==1,(new[:120],normalized.count(new));normalized=normalized.replace(new,old)
 check('allUnrelatedSourceByteIdentical',normalized==bjs)
 rebuilt=Path(tmp)/'rebuilt.html';subprocess.run(['python',str(Path(__file__).parent/'build.py'),'--baseline',a.baseline,'--out',str(rebuilt)],check=True,capture_output=True)
 check('exactRebuild',rebuilt.read_bytes()==p.read_bytes())
assets=lambda h:{m[1]:m[2]for m in re.finditer(r'<script id="([^"]+)" type="application/octet-stream">(.*?)</script>',h,re.S)}
check('allOriginalShipAndHarpoonAssetsExact',assets(h)==assets(baseline))
core=(Path(__file__).parent/'core.js').read_text();knowledge=(Path(__file__).parent/'knowledge.js').read_text()
ui=core[core.index('function harpoonUpdateUIA'):core.index('function harpoonBindUIA')]
check('authoringFragmentsMatchEmbeddedCore',all((Path(__file__).parent/f).read_text()in core for f in ['navigation.js','seeker.js','knowledge.js']))
check('operatorUiNoWorldOrSeekerRead',not any(s in ui for s in ['harpoonWorldA','m.positionM','m.seeker','m.alive','m.phase']))
check('cicNoDirectHarpoonTruthIcon','function harpoonDrawCicA(ctx,sym){}'in core)
check('auxNoDirectHarpoonTruthIcon','for(const ms of [...(st?.missiles??[]),...(st?.harpoons??[])])'not in js)
check('knowledgeNoWorldOrOwnerLookup',not any(s in knowledge for s in ['harpoonWorldA','ownerEntityId','_truthObject','truthRef','m.seeker','m.alive','m.positionM']))
check('noRemoteHitNotification',"notify('HARPOON H'+m.id+' 표적함 명중"not in js)
check('insNoTruthVelocityPositionIntegration','m.navPositionM.x+=(m.velocityMps.x'not in core and 'm.navPositionM.z=m.positionM.z'not in core)
check('seekerAllObservationGatesPresent',all(x in core for x in ['cfg.seekerGimbalRad','cfg.seekerElGimbalRad','cfg.seekerBeamHalfRad','cfg.seekerAcquireHits','cfg.seekerCoastS','s.scanDirection*=-1']))
check('originalRfEchoStillPresent',"for(const m of harpoonWorldA()){if(!m.alive||m===exclude)continue;const id='HARPOON:'+m.id"in js)
check('boosterAndVisualBPreserved',(Path(__file__).parent.parent/'B/renderer.js').read_text()in js and 'boosterBurnS:3.2,boosterAverageThrustN:48000'in core+js)
r={'schema':'HARPOON_C_STATIC_VERIFICATION','source':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'checks':checks,'pass':all(checks.values())}
(out/'static.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));raise SystemExit(0 if r['pass']else 1)
