"""Read the public, pinned artifact commit back; no branch/ref mutation."""
from pathlib import Path
import argparse,hashlib,json,urllib.request,urllib.parse,zipfile,io,datetime,subprocess,concurrent.futures,time
H=Path(__file__).resolve().parent;R=H.parents[2];ap=argparse.ArgumentParser();ap.add_argument('artifact_commit');a=ap.parse_args();commit=a.artifact_commit;assert len(commit)==40 and all(c in'0123456789abcdef'for c in commit)
repo='0-FLANDRE-0/Aegis_Project';names=['Aegis_SIM_v48_WIP_GUN_B1.html','downloads/Aegis_SIM_v48_WIP_GUN_B1_HTML.zip','downloads/Aegis_SIM_v48_WIP_GUN_B1_REPORT.zip','downloads/GUN_B1_SHA256SUMS.txt','docs/gun/B1/STATUS.md','docs/gun/B1/CHECKSUMS.sha256'];temp=Path('/tmp/aegis-gun-b1/readback')/commit;temp.mkdir(parents=True,exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest()
def fetch(name):
 url=f'https://raw.githubusercontent.com/{repo}/{commit}/'+urllib.parse.quote(name,safe='/');error=None
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Aegis-GUN-B1-readback'}),timeout=45)as response:data=response.read();mime=response.headers.get('Content-Type')
   break
  except Exception as e:
   error=e
   if attempt==2:raise
   time.sleep(attempt+1)
 path=temp/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);local=(R/name).read_bytes();q={'path':name,'bytes':len(data),'sha256':sha(data),'matchesLocal':data==local,'contentType':mime,'downloadUrl':f'https://github.com/{repo}/raw/{commit}/'+urllib.parse.quote(name,safe='/')+'?download=1'};assert q['matchesLocal'],name;print(json.dumps(q),flush=True);return q
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:rows=list(pool.map(fetch,names))
game=(temp/names[0]).read_bytes();archive=[]
for name in names[1:3]:
 data=(temp/name).read_bytes()
 with zipfile.ZipFile(io.BytesIO(data))as z:
  assert z.testzip()is None;assert all(not n.startswith('/')and'..'not in Path(n).parts for n in z.namelist());q={'file':name,'entries':len(z.namelist()),'crcPass':True}
  if name==names[1]:assert z.namelist()==[names[0]]and z.read(names[0])==game;q['htmlMemberSha256']=sha(z.read(names[0]))
  else:
   assert'REPORT.html'in z.namelist()and names[0]not in z.namelist();members=[n for n in z.namelist()if n.startswith('docs/gun/B1/')];assert all(z.read(n)==(R/n).read_bytes()for n in members);q['reportMembersMatchLocal']=True;q['reportMembersChecked']=len(members)
  archive.append(q)
refs=subprocess.check_output(['git','ls-remote','origin','refs/heads/main','refs/heads/gun-b1'],cwd=R,text=True);refs=dict(line.split('\t')[::-1]for line in refs.strip().splitlines());base=json.loads((H/'PRODUCT_FREEZE.json').read_text())['mainBefore'];assert refs['refs/heads/gun-b1']==commit;assert refs['refs/heads/main']==base
out={'schema':'AEGIS_GUN_B1_REMOTE_READBACK_1','pass':all(r['matchesLocal']for r in rows),'checkedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':repo,'artifactCommit':commit,'branch':'gun-b1','files':rows,'archives':archive,'mainBefore':base,'mainObserved':refs['refs/heads/main'],'mainUnchanged':True,'releaseOrTagCreated':False,'note':'Receipt is a separate follow-up commit to avoid circular archive self-hashes. Download URLs are pinned to the verified artifact commit.'};(H/'remote-readback.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'artifactCommit':commit,'files':len(rows),'archives':archive},ensure_ascii=False))
