"""Independent remote raw-byte readback after report publication."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,urllib.request,hashlib,io,zipfile,subprocess
P=Path(__file__).resolve().parent;R=P.parents[3];commit=sys.argv[1]
assert len(commit)==40 and all(c in'0123456789abcdef'for c in commit)
sha=lambda b:hashlib.sha256(b).hexdigest();prefix=f'https://raw.githubusercontent.com/0-FLANDRE-0/Aegis_Project/{commit}/'
artifact='downloads/Aegis_SIM_v48_WIP_CIWS_DMG_A_REPORT.zip'
paths=[artifact,'downloads/CIWS_DMG_A_SHA256SUMS.txt','docs/ciws/dmg/A/REPORT.md','docs/ciws/dmg/A/CHECKSUMS.sha256','docs/ciws/dmg/A/VALIDATION.json','Aegis_SIM_v48_WIP_CG_TURRET_A.html'];checks=[];remoteZip=None
for rel in paths:
 url=prefix+rel
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Aegis-CIWS-diagnostic-readback/1.0'}),timeout=90)as res:body=res.read();status=res.status
 local=(R/rel).read_bytes();assert body==local,rel;checks.append({'path':rel,'url':url,'status':status,'bytes':len(body),'sha256':sha(body),'localExact':True})
 if rel==artifact:remoteZip=body
head=subprocess.check_output(['git','ls-remote','origin','refs/heads/ciws-dmg-a'],cwd=R).decode().split()[0];assert head==commit
with zipfile.ZipFile(io.BytesIO(remoteZip))as z:
 assert z.testzip()is None
 manifest=z.read('CIWS_DMG_A/CHECKSUMS.sha256').decode();n=0
 for line in manifest.splitlines():
  digest,rel=line.split('  ',1);assert sha(z.read('CIWS_DMG_A/'+rel))==digest,rel;n+=1
 assert not any(Path(name).name.startswith('Aegis_SIM_')and name.endswith('.html')for name in z.namelist())
receipt={'pass':True,'branch':'ciws-dmg-a','payloadCommit':commit,'remoteHeadAtReadback':head,'checks':checks,'zipCrcPass':True,'zipManifestEntriesVerified':n,'newGameHtml':False,'mainMerged':False,'releaseOrTag':False,'verifiedUtc':datetime.now(timezone.utc).isoformat()};(P/'REMOTE_READBACK.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':True,'payloadCommit':commit,'remoteFiles':len(checks),'zipFiles':n}))
