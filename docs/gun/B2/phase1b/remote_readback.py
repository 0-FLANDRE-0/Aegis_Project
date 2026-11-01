from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,io,json,subprocess,time,urllib.request,zipfile
P=Path(__file__).resolve().parent;R=P.parents[3];sha=lambda b:hashlib.sha256(b).hexdigest();a=argparse.ArgumentParser();a.add_argument('commit');args=a.parse_args();assert len(args.commit)==40
base='https://raw.githubusercontent.com/0-FLANDRE-0/Aegis_Project/'+args.commit+'/';paths=['Aegis_SIM_v48_WIP_GUN_B2.html','downloads/Aegis_SIM_v48_WIP_GUN_B2B_HTML.zip','downloads/Aegis_SIM_v48_WIP_GUN_B2B_REPORT.zip','downloads/GUN_B2B_SHA256SUMS.txt','docs/gun/B2/phase1b/REPORT.md','docs/gun/B2/phase1b/CHECKSUMS.sha256','docs/gun/B2/phase1b/PACKAGE_RECEIPT.json','docs/gun/B2/phase1b/evidence/scope.json','docs/gun/B2/phase1b/evidence/g7-summary.json','docs/gun/B2/BUILD_STATUS.json'];rows=[]
for path in paths:
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(base+path,headers={'User-Agent':'AEGIS-GUN-B2B-readback','Cache-Control':'no-cache'}),timeout=120) as response:data=response.read();status=response.status
   break
  except Exception:
   if attempt==2:raise
   time.sleep(3)
 local=(R/path).read_bytes();assert data==local,(path,sha(data),sha(local));row={'path':path,'status':status,'bytes':len(data),'sha256':sha(data),'equalsLocal':True}
 if path.endswith('.zip'):
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   assert z.testzip() is None;row['crcPass']=True;row['members']=len(z.namelist())
   if path.endswith('_HTML.zip'):assert z.read('Aegis_SIM_v48_WIP_GUN_B2.html')==(R/'Aegis_SIM_v48_WIP_GUN_B2.html').read_bytes();row['embeddedGameExact']=True
   else:
    for line in z.read('BUNDLE_CHECKSUMS.sha256').decode().splitlines():digest,name=line.split('  ',1);assert sha(z.read(name))==digest,name
    row['allBundledChecksumsPass']=True;row['gameHtmlAbsent']=not any(n.endswith('/Aegis_SIM_v48_WIP_GUN_B2.html') or n=='Aegis_SIM_v48_WIP_GUN_B2.html' for n in z.namelist())
 rows.append(row);print(json.dumps(row),flush=True)
ref=subprocess.check_output(['git','ls-remote','origin','refs/heads/gun-b2'],cwd=R,text=True).split()[0];assert ref==args.commit
q={'pass':True,'utc':datetime.now(timezone.utc).isoformat(),'artifactCommit':args.commit,'remoteBranchAtReadback':ref,'baseUrl':base,'method':'Independent pinned HTTPS bytes, ZIP CRC and member digests','rows':rows,'mainMerged':False,'releaseOrTagCreated':False,'receiptScope':'Committed after immutable artifact ZIPs'};(P/'REMOTE_READBACK.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
