"""Separate deterministic HTML-only and report-only ZIPs; verify every member."""
from pathlib import Path
import json,gzip,hashlib,zipfile
P=Path(__file__).resolve().parent;R=P.parents[3];D=R/'downloads';D.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
v=json.loads((P/'VALIDATION.json').read_text());b=json.loads((P/'BUILD.json').read_text());html=R/b['output']
assert sha(html.read_bytes())==v['productSha256']==b['htmlSha256']
assert v['scopePass']and v['ciws']['caseCount']==30 and not v['releaseApproved']
assert v['ciws']['worseNewHit']==[419025]and v['protection']['pass']
compressed=[]
for f in sorted((P/'evidence').glob('*.jsonl')):
 data=f.read_bytes();dst=Path(str(f)+'.gz');z=gzip.compress(data,compresslevel=6,mtime=0);dst.write_bytes(z);assert gzip.decompress(z)==data;compressed.append({'original':str(f.relative_to(P)),'gzip':str(dst.relative_to(P)),'originalSha256':sha(data),'gzipSha256':sha(z),'originalBytes':len(data),'gzipBytes':len(z),'losslessVerified':True});f.unlink()
if compressed:(P/'RAW_COMPRESSION.json').write_text(json.dumps(compressed,indent=2)+'\n')
for f in P.rglob('*.pyc'):f.unlink()
manifest=[(str(f.relative_to(P)),sha(f.read_bytes()))for f in sorted(P.rglob('*'))if f.is_file()and f.name not in ['CHECKSUMS.sha256','REMOTE_READBACK.json']and'__pycache__'not in f.parts]
(P/'CHECKSUMS.sha256').write_text(''.join(s+'  '+name+'\n'for name,s in manifest))
def write_zip(target,entries):
 with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for name,data in entries:
   info=zipfile.ZipInfo(name,date_time=(2026,11,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,data)
 with zipfile.ZipFile(target)as z:
  assert z.testzip()is None
  for name,data in entries:assert z.read(name)==data
artifacts=[]
for suffix,entries in [('HTML',[(html.name,html.read_bytes())]),('REPORT',[('FRIENDLY_CONTACT_A/'+str(f.relative_to(P)),f.read_bytes())for f in sorted(P.rglob('*'))if f.is_file()and'__pycache__'not in f.parts and f.name!='REMOTE_READBACK.json'])]:
 target=D/('Aegis_SIM_v48_WIP_FRIENDLY_CONTACT_A_'+suffix+'.zip');write_zip(target,entries);artifacts.append({'path':str(target.relative_to(R)),'sha256':sha(target.read_bytes()),'bytes':target.stat().st_size,'members':len(entries)})
(D/'FRIENDLY_CONTACT_A_SHA256SUMS.txt').write_text(sha(html.read_bytes())+'  '+html.name+'\n'+''.join(x['sha256']+'  '+Path(x['path']).name+'\n'for x in artifacts))
print(json.dumps({'artifacts':artifacts,'htmlSha256':sha(html.read_bytes()),'releaseApproved':False},indent=2))
