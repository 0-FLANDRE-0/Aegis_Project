"""Package the measured WIP without disguising failed regression approval."""
from pathlib import Path
import hashlib,json,subprocess,zipfile
H=Path(__file__).resolve().parent;R=H.parents[3];V='v48_WIP_LAUNCH_HANDOFF_A'
sha=lambda b:hashlib.sha256(b).hexdigest()
v=json.loads((H/'final-evidence/verification.json').read_text())
assert v['launchMechanismChecksPass'] and not v['releaseApproved'] and not v['allRegressionPass']
htmlName='Aegis_SIM_'+V+'.html';html=(R/htmlName).read_bytes();assert sha(html)==v['htmlSha256']
exclude={'DELIVERY_MANIFEST.json','remote-publication.json','publication-receipt.json','delivery.json'}
# Redundant CSV expansions stay on the branch. Report contains complete final
# raw JSON.gz plus compact current-tick and 10Hz CSV; no evidence is discarded.
redundant={'analysis/transition-detached-ticks.csv.gz','analysis/pipeline-current-tick.csv.gz'}
entries={}
for p in H.rglob('*'):
 if not p.is_file()or'__pycache__'in p.parts or p.name in exclude or p.suffix in ['.html','.zip']or str(p.relative_to(H))in redundant:continue
 entries[str(p.relative_to(R))]=p.read_bytes()
support=['docs/pip/B','docs/map/A','docs/viewport/A','docs/missile/termination/A','docs/missile/range/A','docs/missile/fuze-zem/A','docs/helicopter','docs/multiship/G','docs/multiship/H4','docs/bunkerhill/K','docs/sovremenny/A']
for n in subprocess.check_output(['git','ls-files','-z',*support],cwd=R).decode().split('\0'):
 if not n:continue
 p=R/n
 if not p.exists()or p.suffix not in ['.py','.js','.cjs','.json','.tsv','.md']or p.stat().st_size>2_000_000:continue
 if any(x in ['evidence','results','screenshots','node_modules','plots','kit']for x in p.parts):continue
 entries[n]=p.read_bytes()
for n in ['README.md','AEGIS_PROJECT_INSTRUCTIONS.md','AEGIS_PLAN_STATUS_'+V+'.md','SHA256SUMS_'+V+'.txt','docs/envelope/D/engine.cjs','docs/envelope/D/inputs.json','docs/envelope/D/diagnostic/native-engine.js','docs/envelope/D/diagnostic/private.js','docs/envelope/D/diagnostic/native-asm-prefix.js','docs/envelope/D/diagnostic/boundaries.json','docs/envelope/D/run_observed_webgl.py','docs/envelope/D/verify_world120.py','docs/performance/F/package.json','docs/performance/F/package-lock.json']:
 entries[n]=(R/n).read_bytes()
entries['REPORT_INDEX.md']=b'''# LAUNCH_HANDOFF_A WIP

[Report](docs/missile/launch-handoff/A/REPORT.md), [contract](docs/missile/launch-handoff/A/MODEL.md), [reproduce](docs/missile/launch-handoff/A/REPRODUCE.md), [verification](docs/missile/launch-handoff/A/final-evidence/verification.json).

Launch mechanism verified for the specified cases; full regression approval WITHHELD. Three new failure shots / two conditions and six original exact-state assertion failures are disclosed. No gain/physics/fuze retuning. No main merge or release/tag. Full final raw JSON.gz included. Two redundant CSV expansions remain on the branch; compact current-tick and 10Hz CSV included. Product HTML is delivered separately. Old ENV_D table remains HISTORICAL/recalculation-required.
'''
assert not any(n.lower().endswith(('.html','.zip'))for n in entries)
manifest={'schema':'AEGIS_LAUNCH_HANDOFF_A_REPORT_MANIFEST_1','releaseApproved':False,'htmlDeliveredSeparately':{'file':htmlName,'bytes':len(html),'sha256':sha(html)},'excludedRedundantCsvRetainedOnBranch':sorted(redundant),'allFinalRawIncluded':True,'files':[{'path':n,'bytes':len(b),'sha256':sha(b)}for n,b in sorted(entries.items())]}
mb=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode();(H/'DELIVERY_MANIFEST.json').write_bytes(mb);entries['DELIVERY_MANIFEST.json']=mb
def write(name,contents):
 with zipfile.ZipFile(R/name,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for n,b in sorted(contents.items()):
   i=zipfile.ZipInfo(n,date_time=(2026,1,1,0,0,0));i.create_system=3;i.external_attr=0o100644<<16;i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,b,compresslevel=9)
 with zipfile.ZipFile(R/name)as z:
  assert z.testzip()is None and z.namelist()==sorted(contents)
  for n,b in contents.items():assert z.read(n)==b
 b=(R/name).read_bytes();assert len(b)<100*1024*1024
 return {'file':name,'bytes':len(b),'sha256':sha(b),'members':len(contents),'crcValid':True,'allUnpackedBytesVerified':True}
a=write('Aegis_SIM_'+V+'_HTML.zip',{htmlName:html});b=write('Aegis_SIM_'+V+'_REPORT.zip',entries)
for kind,q in [('HTML_ZIP',a),('REPORT_ZIP',b)]:(R/('SHA256SUMS_'+V+'_'+kind+'.txt')).write_text(q['sha256']+'  '+q['file']+'\n')
out={'packagingPass':True,'releaseApproved':False,'html':manifest['htmlDeliveredSeparately'],'executionZip':a,'reportZip':b,'reportContainsExecutionHtml':False};(H/'final-evidence/delivery.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
