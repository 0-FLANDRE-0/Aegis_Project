"""Separate single-HTML execution ZIP and complete, hashed evidence ZIP."""
from pathlib import Path
import hashlib,json,subprocess,zipfile
H=Path(__file__).resolve().parent;R=H.parents[2];V='v48_WIP_ENV_D'
verified=json.loads((H/'evidence/verification.json').read_text());assert verified['verificationPass']
assert(H/'REPORT.md').exists()
sha=lambda x:hashlib.sha256(x).hexdigest()
htmlName=f'Aegis_SIM_{V}.html';html=(R/htmlName).read_bytes()
entries={}
for p in H.rglob('*'):
 if p in [H/'evidence/post-measurement.json',H/'evidence/package.log']:
  continue  # Runner control receipts continue changing after ZIP creation.
 if p.is_file()and'__pycache__'not in p.parts and p.name not in ['DELIVERY_MANIFEST.json','remote-publication.json','delivery.json']and p.suffix.lower()not in ['.html','.zip']:
  entries[str(p.relative_to(R))]=p.read_bytes()
# Original harnesses are supplied for audit/reproduction. Do not bundle their
# old result directories, binary models, execution HTMLs or nested ZIP kits.
support=['docs/pip/B','docs/map/A','docs/viewport/A','docs/missile/termination/A','docs/missile/range/A','docs/helicopter/F','docs/helicopter/G','docs/helicopter/H','docs/helicopter/J','docs/helicopter/K','docs/helicopter/L','docs/multiship/G','docs/multiship/H4','docs/bunkerhill/K','docs/sovremenny/A']
tracked=subprocess.check_output(['git','ls-files','-z',*support],cwd=R).decode().split('\0')
for name in tracked:
 if not name:continue
 p=R/name
 if not p.exists()or p.suffix not in ['.py','.js','.cjs','.json','.tsv','.md']:continue
 if any(part in ['evidence','results','screenshots','node_modules','plots','kit']for part in p.parts):continue
 if p.stat().st_size>2_000_000:continue
 entries[name]=p.read_bytes()
for name in ['docs/envelope/C/ENVELOPE_TABLE_C.json','docs/performance/F/package.json','docs/performance/F/package-lock.json','docs/performance/F/verify_scope.cjs','README.md','AEGIS_PROJECT_INSTRUCTIONS.md',f'AEGIS_PLAN_STATUS_{V}.md',f'SHA256SUMS_{V}.txt']:
 entries[name]=(R/name).read_bytes()
entries['REPORT_INDEX.md']=b'# REG_K + ENV_D\n\n[Report](docs/envelope/D/REPORT.md) | [Reproduction](docs/envelope/D/README.md) | [Verification](docs/envelope/D/evidence/verification.json)\n\nExecution HTML is delivered separately. Raw gzip JSON/CSV retain their .gz suffix. The invalidated incomplete-hooks pilot/partial sweep is explicitly segregated and is not ENV_D data. Existing ENV_C is historical AIR-point-target, pre-Kappa guidance.\n'
assert not any(n.lower().endswith(('.html','.zip'))for n in entries)
manifest={'schema':'AEGIS_ENV_D_REPORT_MANIFEST_1','htmlDeliveredSeparately':{'file':htmlName,'bytes':len(html),'sha256':sha(html)},'files':[{'path':name,'bytes':len(data),'sha256':sha(data)}for name,data in sorted(entries.items())]}
mb=(json.dumps(manifest,indent=2)+'\n').encode();(H/'DELIVERY_MANIFEST.json').write_bytes(mb);entries['DELIVERY_MANIFEST.json']=mb
def write(name,contents):
 with zipfile.ZipFile(R/name,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for member,data in sorted(contents.items()):
   info=zipfile.ZipInfo(member,date_time=(2026,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data,compresslevel=9)
 with zipfile.ZipFile(R/name)as z:
  assert z.testzip()is None and z.namelist()==sorted(contents)
  for member,data in contents.items():assert z.read(member)==data
 data=(R/name).read_bytes();return {'file':name,'bytes':len(data),'sha256':sha(data),'members':len(contents),'crcValid':True,'allUnpackedBytesVerified':True}
execution=write(f'Aegis_SIM_{V}_HTML.zip',{htmlName:html})
report=write(f'Aegis_SIM_{V}_REPORT.zip',entries)
assert report['bytes']<100*1024*1024,'GitHub regular-blob limit: preserve all evidence and repack raw JSON if needed'
for key,info in [('HTML_ZIP',execution),('REPORT_ZIP',report)]:
 (R/f'SHA256SUMS_{V}_{key}.txt').write_text(info['sha256']+'  '+info['file']+'\n')
out={'pass':True,'html':manifest['htmlDeliveredSeparately'],'executionZip':execution,'reportZip':report,'reportContainsExecutionHtml':False,'measurementComplete':True,'regressionPass':verified['regressionPass'],'successToFailure':verified['successToFailure'],'failureToSuccess':verified['failureToSuccess']}
(H/'evidence/delivery.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
