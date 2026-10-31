"""Pinned GitHub downloads + ZIP member equality, separate receipt commit."""
from pathlib import Path
import argparse,concurrent.futures,datetime,hashlib,io,json,subprocess,time,urllib.request,zipfile
from source import P,R,MAIN,SOURCE_SHA
p=argparse.ArgumentParser();p.add_argument('commit');a=p.parse_args();assert len(a.commit)==40 and all(c in'0123456789abcdef'for c in a.commit)
repo='0-FLANDRE-0/Aegis_Project';names=['downloads/Aegis_SIM_v48_WIP_GUN_B2_POST_ORIGIN_REPORT.zip','downloads/GUN_B2_POST_ORIGIN_SHA256SUMS.txt','docs/gun/B2/PHASE1_START.md','docs/gun/B2/BUILD_STATUS.json','docs/gun/B2/post-origin/CHECKSUMS.sha256','docs/gun/B2/post-origin/evidence/summary.json','docs/gun/B2/post-origin/rebase.json','Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html'];data={};sha=lambda b:hashlib.sha256(b).hexdigest()
def fetch(name):
 url=f'https://raw.githubusercontent.com/{repo}/{a.commit}/'+name
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AEGIS-GUN-B2-post-origin-readback'}),timeout=45)as r:body=r.read();mime=r.headers.get('Content-Type')
   break
  except Exception:
   if attempt==2:raise
   time.sleep(attempt+1)
 assert body==(R/name).read_bytes(),name;data[name]=body
 return {'path':name,'bytes':len(body),'sha256':sha(body),'matchesLocal':True,'contentType':mime,'downloadUrl':f'https://github.com/{repo}/raw/{a.commit}/'+name+'?download=1'}
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:files=list(pool.map(fetch,names))
assert sha(data[names[-1]])==SOURCE_SHA
with zipfile.ZipFile(io.BytesIO(data[names[0]]))as z:
 assert z.testzip()is None and'REPORT.html'in z.namelist()and not any(n.startswith('/')or'..'in Path(n).parts or n.startswith('Aegis_SIM')for n in z.namelist())
 members=[n for n in z.namelist()if n.startswith('docs/gun/B2/')];assert all(z.read(n)==(R/n).read_bytes()for n in members);archive={'crcPass':True,'entries':len(z.namelist()),'membersChecked':len(members),'membersMatchLocal':True,'gameHtmlIncluded':False}
refs=dict(line.split('\t')[::-1]for line in subprocess.check_output(['git','ls-remote','origin','refs/heads/main','refs/heads/gun-b2'],cwd=R,text=True).strip().splitlines());assert refs['refs/heads/gun-b2']==a.commit
q={'schema':'AEGIS_GUN_B2_POST_ORIGIN_READBACK_1','pass':True,'artifactCommit':a.commit,'checkedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,'archive':archive,'mergedMain':MAIN,'mainObserved':refs['refs/heads/main'],'mainModifiedByThisTask':False,'phase1Implemented':False,'newGameHtmlProduced':False,'adverseHpCases':1,'releaseOrTagCreated':False,'note':'Rebased gun-b2; diagnosis and Phase1 start report only. Receipt committed separately to avoid circular hashes.'};(P/'REMOTE_READBACK.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':True,'artifactCommit':a.commit,'files':len(files),'archive':archive}))
