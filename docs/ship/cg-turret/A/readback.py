from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,io,json,subprocess,urllib.request,zipfile
P=Path(__file__).resolve().parent;R=P.parents[3];sha=lambda b:hashlib.sha256(b).hexdigest();a=argparse.ArgumentParser();a.add_argument('commit');args=a.parse_args();assert len(args.commit)==40
base='https://raw.githubusercontent.com/0-FLANDRE-0/Aegis_Project/'+args.commit+'/';paths=['Aegis_SIM_v48_WIP_CG_TURRET_A.html','downloads/Aegis_SIM_v48_WIP_CG_TURRET_A_HTML.zip','downloads/Aegis_SIM_v48_WIP_CG_TURRET_A_REPORT.zip','downloads/CG_TURRET_A_SHA256SUMS.txt','docs/ship/cg-turret/A/REPORT.md','docs/ship/cg-turret/A/BUILD_STATUS.json','docs/ship/cg-turret/A/CHECKSUMS.sha256'];rows=[]
for path in paths:
 with urllib.request.urlopen(urllib.request.Request(base+path,headers={'User-Agent':'AEGIS-CG-TURRET-A-readback','Cache-Control':'no-cache'}),timeout=60)as response:data=response.read();status=response.status
 assert data==(R/path).read_bytes();row={'path':path,'status':status,'bytes':len(data),'sha256':sha(data),'equalsLocal':True}
 if path.endswith('.zip'):
  with zipfile.ZipFile(io.BytesIO(data))as z:
   assert z.testzip()is None;row['crcPass']=True
   if path.endswith('_HTML.zip'):assert z.read('Aegis_SIM_v48_WIP_CG_TURRET_A.html')==(R/'Aegis_SIM_v48_WIP_CG_TURRET_A.html').read_bytes();row['embeddedGameExact']=True
   else:
    for l in z.read('BUNDLE_CHECKSUMS.sha256').decode().splitlines():digest,name=l.split('  ',1);assert sha(z.read(name))==digest
    row['memberChecksumsPass']=True
 rows.append(row);print(row,flush=True)
ref=subprocess.check_output(['git','ls-remote','origin','refs/heads/cg-turret-a'],cwd=R,text=True).split()[0];assert ref==args.commit
(P/'REMOTE_READBACK.json').write_text(json.dumps({'pass':True,'utc':datetime.now(timezone.utc).isoformat(),'artifactCommit':args.commit,'remoteBranchAtReadback':ref,'rows':rows},indent=2)+'\n')
