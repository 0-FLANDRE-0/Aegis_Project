"""Verify public pinned GitHub artifacts; write a separate noncircular receipt."""
from pathlib import Path
import argparse,concurrent.futures,datetime,hashlib,io,json,subprocess,time,urllib.parse,urllib.request,zipfile
B=Path(__file__).resolve().parent;R=B.parents[2]
p=argparse.ArgumentParser();p.add_argument('artifact_commit');args=p.parse_args();commit=args.artifact_commit
assert len(commit)==40 and all(c in '0123456789abcdef' for c in commit)
repo='0-FLANDRE-0/Aegis_Project';sha=lambda b:hashlib.sha256(b).hexdigest()
names=['downloads/Aegis_SIM_v48_WIP_GUN_B2_PHASE0_REPORT.zip','downloads/GUN_B2_PHASE0_SHA256SUMS.txt','docs/gun/B2/PHASE0.md','docs/gun/B2/BUILD_STATUS.json','docs/gun/B2/CHECKSUMS.sha256']
temp=Path('/tmp/aegis-gun-b2/readback')/commit;temp.mkdir(parents=True,exist_ok=True)
def fetch(name):
 url=f'https://raw.githubusercontent.com/{repo}/{commit}/'+urllib.parse.quote(name,safe='/')
 for attempt in range(3):
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'AEGIS-GUN-B2-Phase0-readback'})
   with urllib.request.urlopen(req,timeout=45) as response:data=response.read();mime=response.headers.get('Content-Type')
   break
  except Exception:
   if attempt==2:raise
   time.sleep(attempt+1)
 path=temp/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
 q={'path':name,'bytes':len(data),'sha256':sha(data),'matchesLocal':data==(R/name).read_bytes(),'contentType':mime,'downloadUrl':f'https://github.com/{repo}/raw/{commit}/'+urllib.parse.quote(name,safe='/')+'?download=1'}
 assert q['matchesLocal'],name
 return q
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(fetch,names))
with zipfile.ZipFile(io.BytesIO((temp/names[0]).read_bytes())) as z:
 assert z.testzip() is None
 assert all(not n.startswith('/') and '..' not in Path(n).parts for n in z.namelist())
 assert 'REPORT.html' in z.namelist() and not any(n.startswith('Aegis_SIM_') for n in z.namelist())
 members=[n for n in z.namelist() if n.startswith('docs/gun/B2/')]
 assert all(z.read(n)==(R/n).read_bytes() for n in members)
 archive={'file':names[0],'crcPass':True,'entries':len(z.namelist()),'reportMembersChecked':len(members),'membersMatchLocal':True,'gameHtmlIncluded':False}
refs=subprocess.check_output(['git','ls-remote','origin','refs/heads/main','refs/heads/gun-b2'],cwd=R,text=True)
refs=dict(line.split('\t')[::-1] for line in refs.strip().splitlines())
assert refs['refs/heads/gun-b2']==commit
base='9719f1e8b3e574f0969eb57c6b2055f7f8d3ee4c'
out={'schema':'AEGIS_GUN_B2_PHASE0_REMOTE_READBACK_1','pass':True,'checkedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':repo,'artifactCommit':commit,'branch':'gun-b2','phase':'PHASE0_ONLY_AWAIT_USER_APPROVAL','files':rows,'archive':archive,'mainAtStart':base,'mainObserved':refs['refs/heads/main'],'mainUnchangedSinceStart':refs['refs/heads/main']==base,'mainModifiedByThisTask':False,'releaseOrTagCreated':False,'note':'Receipt is a separate follow-up commit. URLs are pinned to the downloaded artifact commit; Phase 1 is not implemented.'}
(B/'REMOTE_READBACK.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'pass':True,'artifactCommit':commit,'files':len(rows),'archive':archive},ensure_ascii=False))
