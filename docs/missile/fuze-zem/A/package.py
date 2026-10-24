"""Separate single-HTML execution ZIP and hashed report/reproduction ZIP."""
from pathlib import Path
import hashlib,json,subprocess,zipfile
H=Path(__file__).resolve().parent;R=H.parents[3];V='v48_WIP_FUZE_ZEM_A';sha=lambda b:hashlib.sha256(b).hexdigest()
assert json.loads((H/'evidence/verification.json').read_text())['verificationPass']
htmlName=f'Aegis_SIM_{V}.html';html=(R/htmlName).read_bytes();entries={}
exclude={'DELIVERY_MANIFEST.json','remote-publication.json','delivery.json','publication-receipt.json'}
# Previous revision2 was not used for the final candidate or report figures.
# It remains on the branch; no raw record is deleted/rewritten for packaging.
excludedHistory={'results/revision2.json.gz','results/term-diagnostic-v1.json.gz','results/zt.json.gz'}
for p in H.rglob('*'):
 if p.is_file()and'__pycache__'not in p.parts and p.name not in exclude and p.suffix not in ['.html','.zip']and str(p.relative_to(H))not in excludedHistory:entries[str(p.relative_to(R))]=p.read_bytes()
# Supply the original support harness source, not prior report assets or HTMLs.
support=['docs/pip/B','docs/map/A','docs/viewport/A','docs/missile/termination/A','docs/missile/range/A','docs/helicopter/F','docs/helicopter/G','docs/helicopter/H','docs/helicopter/J','docs/helicopter/K','docs/helicopter/L','docs/multiship/G','docs/multiship/H4','docs/bunkerhill/K','docs/sovremenny/A']
for n in subprocess.check_output(['git','ls-files','-z',*support],cwd=R).decode().split('\0'):
 if not n:continue
 p=R/n
 if not p.exists()or p.suffix not in ['.py','.js','.cjs','.json','.tsv','.md']or p.stat().st_size>2_000_000:continue
 if any(part in ['evidence','results','screenshots','node_modules','plots','kit']for part in p.parts):continue
 entries[n]=p.read_bytes()
for n in ['README.md','AEGIS_PROJECT_INSTRUCTIONS.md',f'AEGIS_PLAN_STATUS_{V}.md',f'SHA256SUMS_{V}.txt','docs/envelope/D/engine.cjs','docs/envelope/D/inputs.json','docs/envelope/D/diagnostic/native-engine.js','docs/envelope/D/diagnostic/private.js','docs/envelope/D/diagnostic/native-asm-prefix.js','docs/envelope/D/diagnostic/boundaries.json','docs/envelope/D/run_observed_webgl.py','docs/envelope/D/verify_world120.py','docs/performance/F/package.json','docs/performance/F/package-lock.json']:entries[n]=(R/n).read_bytes()
entries['REPORT_INDEX.md']='# FUZE_ZEM_A\n\n[보고서](docs/missile/fuze-zem/A/REPORT.md) · [모델](docs/missile/fuze-zem/A/MODEL.md) · [재현](docs/missile/fuze-zem/A/REPRODUCE.md) · [검증](docs/missile/fuze-zem/A/evidence/verification.json)\n\nD=deterministic SAM acquisition; Z=ZEM sign; T=observed TRACK termination. Final game=DZT. F is superseded/rejected. No full ENV_D sweep. Legacy 120-row table is historical/recalculation-required. Execution HTML is supplied separately. Previous non-final duplicate raw runs listed in DELIVERY_MANIFEST stay on the branch and are excluded from this ZIP; final revision3 raw records are complete.\n'.encode()
assert not any(n.lower().endswith(('.html','.zip'))for n in entries)
manifest={'schema':'AEGIS_FUZE_ZEM_A_REPORT_MANIFEST_1','htmlDeliveredSeparately':{'file':htmlName,'bytes':len(html),'sha256':sha(html)},'excludedNonFinalDuplicateRaw':sorted(excludedHistory),'files':[{'path':n,'bytes':len(b),'sha256':sha(b)}for n,b in sorted(entries.items())]};mb=(json.dumps(manifest,indent=2)+'\n').encode();(H/'DELIVERY_MANIFEST.json').write_bytes(mb);entries['DELIVERY_MANIFEST.json']=mb

def write(name,contents):
 with zipfile.ZipFile(R/name,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for n,b in sorted(contents.items()):
   i=zipfile.ZipInfo(n,date_time=(2026,1,1,0,0,0));i.create_system=3;i.external_attr=0o100644<<16;i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,b,compresslevel=9)
 with zipfile.ZipFile(R/name)as z:
  assert z.testzip()is None and z.namelist()==sorted(contents)
  for n,b in contents.items():assert z.read(n)==b
 b=(R/name).read_bytes();return{'file':name,'bytes':len(b),'sha256':sha(b),'members':len(contents),'crcValid':True,'allUnpackedBytesVerified':True}
a=write(f'Aegis_SIM_{V}_HTML.zip',{htmlName:html});b=write(f'Aegis_SIM_{V}_REPORT.zip',entries);assert b['bytes']<100*1024*1024
for kind,q in [('HTML_ZIP',a),('REPORT_ZIP',b)]:(R/f'SHA256SUMS_{V}_{kind}.txt').write_text(q['sha256']+'  '+q['file']+'\n')
out={'pass':True,'html':manifest['htmlDeliveredSeparately'],'executionZip':a,'reportZip':b,'reportContainsExecutionHtml':False};(H/'evidence/delivery.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
