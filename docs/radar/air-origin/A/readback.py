"""Pinned public downloads, ZIP CRC/member equality; separate receipt commit."""
from pathlib import Path
import argparse,concurrent.futures,datetime,hashlib,io,json,subprocess,time,urllib.parse,urllib.request,zipfile
B=Path(__file__).resolve().parent;R=B.parents[3];p=argparse.ArgumentParser();p.add_argument('commit');a=p.parse_args();assert len(a.commit)==40 and all(c in'0123456789abcdef'for c in a.commit)
repo='0-FLANDRE-0/Aegis_Project';names=['Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html','downloads/Aegis_SIM_v48_WIP_AIR_ORIGIN_A_HTML.zip','downloads/Aegis_SIM_v48_WIP_AIR_ORIGIN_A_REPORT.zip','downloads/AIR_ORIGIN_A_SHA256SUMS.txt','docs/radar/air-origin/A/REPORT.md','docs/radar/air-origin/A/CHECKSUMS.sha256'];data={};sha=lambda b:hashlib.sha256(b).hexdigest()
if (B/'approved-expectations.json').exists():names+=['docs/radar/air-origin/A/'+n for n in ['approved-expectations.json','APPROVAL_REPORT.md','STATUS.json','evidence/approval/summary.json']]
def fetch(n):
 url=f'https://raw.githubusercontent.com/{repo}/{a.commit}/'+urllib.parse.quote(n,safe='/')
 for i in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AEGIS-AIR-ORIGIN-A-readback'}),timeout=45)as r:q=r.read();mime=r.headers.get('Content-Type')
   break
  except Exception:
   if i==2:raise
   time.sleep(i+1)
 assert q==(R/n).read_bytes();data[n]=q
 return {'path':n,'bytes':len(q),'sha256':sha(q),'matchesLocal':True,'contentType':mime,'downloadUrl':f'https://github.com/{repo}/raw/{a.commit}/'+urllib.parse.quote(n,safe='/')+'?download=1'}
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:files=list(pool.map(fetch,names))
archives=[]
for n in names[1:3]:
 with zipfile.ZipFile(io.BytesIO(data[n]))as z:
  assert z.testzip()is None and all(not x.startswith('/')and'..'not in Path(x).parts for x in z.namelist())
  if n==names[1]:assert z.namelist()==[names[0]]and z.read(names[0])==data[names[0]]
  else:
   assert names[0]not in z.namelist()and'REPORT.html'in z.namelist();members=[x for x in z.namelist()if x.startswith('docs/radar/air-origin/A/')];assert all(z.read(x)==(R/x).read_bytes()for x in members)
  archives.append({'path':n,'crcPass':True,'entries':len(z.namelist()),'membersMatchLocal':True})
refs=dict(line.split('\t')[::-1]for line in subprocess.check_output(['git','ls-remote','origin','refs/heads/main','refs/heads/air-origin-a'],cwd=R,text=True).strip().splitlines());assert refs['refs/heads/air-origin-a']==a.commit
q={'pass':True,'artifactCommit':a.commit,'checkedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,'archives':archives,'mainAtStart':'9719f1e8b3e574f0969eb57c6b2055f7f8d3ee4c','mainObserved':refs['refs/heads/main'],'mainModifiedByThisTask':False,'mainMerged':False,'releaseOrTagCreated':False,'note':'Receipt is a separate follow-up commit to avoid circular ZIP hashes. Post-merge GUN_B2 work is not started.'};(B/'REMOTE_READBACK.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({'pass':True,'artifactCommit':a.commit,'archives':archives}))
