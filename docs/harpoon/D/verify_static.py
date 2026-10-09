"""D syntax, exact C preservation, automatic selection boundary and reproducible build."""
import argparse,base64,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
from build import patches,markup_patches,BASE,BASE_SHA
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
 normalized=js.replace('V48_WIP_HARPOON_D','V48_WIP_HARPOON_C').replace('WIP HARPOON D','WIP HARPOON C')
 for old,new in reversed(patches()):
  assert normalized.count(new)==1,(new[:120],normalized.count(new));normalized=normalized.replace(new,old)
 check('allUnrelatedSourceByteIdentical',normalized==bjs)
 rebuilt=Path(tmp)/'rebuilt.html';subprocess.run(['python',str(Path(__file__).parent/'build.py'),'--baseline',a.baseline,'--out',str(rebuilt)],check=True,capture_output=True)
 check('exactRebuild',rebuilt.read_bytes()==p.read_bytes())
assets=lambda h:{m[1]:m[2]for m in re.finditer(r'<script id="([^"]+)" type="application/octet-stream">(.*?)</script>',h,re.S)}
check('allOriginalShipAndHarpoonAssetsExact',assets(h)==assets(baseline))
selection=(Path(__file__).parent/'selection.js').read_text();ui=(Path(__file__).parent/'ui.js').read_text()
check('selectionAndUiAuthoringEmbedded',selection in js and ui in js)
check('selectionNoWorldTruthOrRngRead',not any(x in selection for x in ['harpoonWorldA','surfaceContacts','physicalRfReflector','ownerEntityId','truthRef','Math.random','harpoonRandomA']))
check('operatorUiNoFlightOrSeekerRead',not any(x in ui for x in ['harpoonWorldA','m.positionM','m.seeker','m.alive','m.phase']))
check('selectorIsLabelAndNotIndividualDropdown','<span id="harpoonTubeA" role="status"' in h and '<select id="harpoonTubeA"'not in h)
check('manualFireButtonStillBound',"bindPress(document.getElementById('harpoonFireA'),()=>{harpoonRequestFireA();"in ui)
check('unchangedProfilesAndInventorySchema',(Path(__file__).parent.parent/'C/profile.js').read_text().split('function harpoonInstallationA(){')[0]in js and "schema:'MK141_INVENTORY_A1'"in js)
check('actualReleasePinnedAndRechecked',"harpoonGateA(pending.trackId,pending.tubeId,{actualRelease:true})"in js)
check('cicStillMeasuredOnly','function harpoonDrawCicA(ctx,sym){}'in js and "NO DL"in ui)
normalized_markup=h.replace('V48_WIP_HARPOON_D','V48_WIP_HARPOON_C').replace('WIP HARPOON D','WIP HARPOON C')
for old,new in reversed(markup_patches()):
 assert normalized_markup.count(new)==1;normalized_markup=normalized_markup.replace(new,old)
# Packing metadata/main payload are the only outer changes besides the declared label/title.
strip=lambda text:re.sub(r'<script type="application/octet-stream" data-c55-index="13">.*?</script>','MAIN',re.sub(r'const records=\[.*?\];','RECORDS',text,flags=re.S),flags=re.S)
check('allUnrelatedOuterHtmlExact',strip(normalized_markup)==strip(baseline))
r={'schema':'HARPOON_D_STATIC_VERIFICATION','source':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'checks':checks,'pass':all(checks.values())}
(out/'static.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));raise SystemExit(0 if r['pass']else 1)
