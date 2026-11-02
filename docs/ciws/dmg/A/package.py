"""Lossless evidence compression and report-only ZIP; never a new game HTML."""
from pathlib import Path
import json,gzip,hashlib,shutil,zipfile
P=Path(__file__).resolve().parent;R=P.parents[3];D=R/'downloads';D.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
v=json.loads((P/'VALIDATION.json').read_text());assert v['totalAcceptedCombatRuns']==133 and v['productByteIdentical']and v['pageErrors']==0
compression=[]
for root in[P/'evidence',P/'evidence-main-before-user-base-change']:
 for f in sorted(root.glob('*.jsonl')):
  before=f.read_bytes();dst=Path(str(f)+'.gz')
  with dst.open('wb')as out:
   with gzip.GzipFile(filename='',fileobj=out,mode='wb',compresslevel=6,mtime=0)as gz:gz.write(before)
  assert gzip.decompress(dst.read_bytes())==before
  compression.append({'original':str(f.relative_to(P)),'gzip':str(dst.relative_to(P)),'originalSha256':sha(before),'originalBytes':len(before),'gzipSha256':sha(dst.read_bytes()),'gzipBytes':dst.stat().st_size,'losslessVerified':True});f.unlink()
if compression:(P/'RAW_COMPRESSION.json').write_text(json.dumps(compression,indent=2)+'\n')
for p in P.rglob('*.pyc'):p.unlink()
manifest=[]
for f in sorted(P.rglob('*')):
 if f.is_file()and f.name not in['CHECKSUMS.sha256','REMOTE_READBACK.json']and'__pycache__'not in f.parts:manifest.append((str(f.relative_to(P)),sha(f.read_bytes())))
(P/'CHECKSUMS.sha256').write_text(''.join(f'{s}  {n}\n'for n,s in manifest))
artifact=D/'Aegis_SIM_v48_WIP_CIWS_DMG_A_REPORT.zip'
with zipfile.ZipFile(artifact,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for f in sorted(P.rglob('*')):
  if f.is_file()and'__pycache__'not in f.parts and f.name!='REMOTE_READBACK.json':
   # Fixed timestamp makes archive construction repeatable for identical files.
   rel=str(f.relative_to(P));info=zipfile.ZipInfo('CIWS_DMG_A/'+rel,date_time=(2026,11,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,f.read_bytes())
with zipfile.ZipFile(artifact)as z:
 assert z.testzip()is None
 for rel,s in manifest:assert sha(z.read('CIWS_DMG_A/'+rel))==s
 assert not any(Path(n).name.startswith('Aegis_SIM_')and n.endswith('.html')for n in z.namelist())
digest=sha(artifact.read_bytes());(D/'CIWS_DMG_A_SHA256SUMS.txt').write_text(f'{digest}  {artifact.name}\n')
print(json.dumps({'artifact':str(artifact.relative_to(R)),'sha256':digest,'bytes':artifact.stat().st_size,'files':len(manifest)+1,'newGameHtml':False}))
