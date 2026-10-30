"""Independent GitHub tree and raw-byte readback, without Actions or writes.

Run after normal push. Report is excluded from its own support checksum;
the later evidence-only commit leaves the verified HTML/support blobs intact.
"""
import argparse,base64,concurrent.futures,hashlib,json,subprocess
from pathlib import Path
from urllib.parse import quote
REPO='0-FLANDRE-0/Aegis_Project'
BASE='b74a2c733352230a0799446cfdb6730b2bb87421'
ROOT=Path(__file__).resolve().parents[3]
def command(args):return subprocess.run(args,cwd=ROOT,capture_output=True,check=True).stdout
def gh(endpoint,*args):return command(['gh','api','repos/'+REPO+'/'+endpoint,*args])
def main():
 p=argparse.ArgumentParser();p.add_argument('commit');p.add_argument('out',type=Path);p.add_argument('--branch',default='multiship-defense-h4a');a=p.parse_args()
 head=json.loads(gh('branches/'+quote(a.branch,safe='')))['commit']['sha'];assert head==a.commit,('REMOTE_HEAD_CHANGED',head)
 tree=json.loads(gh('git/trees/'+a.commit+'?recursive=1'));assert not tree.get('truncated');entries={q['path']:q for q in tree['tree']}
 changed=command(['git','diff','--name-only','--diff-filter=ACMR',BASE,a.commit]).decode().splitlines()
 deleted=command(['git','diff','--name-only','--diff-filter=D',BASE,a.commit]).decode().splitlines()
 deleted=sorted(set(deleted)|{'Aegis_SIM_v48_WIP_MULTI_SHIP_H4.html','AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_H4.md','SHA256SUMS_v48_WIP_MULTI_SHIP_H4.txt','.github/workflows/multiship-h4.yml'})
 assert all(q not in entries for q in deleted)
 def read(path):
  data=command(['git','show',a.commit+':'+path]);blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert entries[path]['sha']==blob,(path,'BLOB_MISMATCH')
  raw=subprocess.run(['gh','api','repos/'+REPO+'/contents/'+quote(path,safe='/')+'?ref='+a.commit,'-H','Accept: application/vnd.github.raw+json'],cwd=ROOT,capture_output=True)
  transport='contents raw';failure=None
  if raw.returncode:
   # Some API proxies fail gzip raw transport. The blob API independently
   # returns the exact stored bytes as base64; never infer success from local data.
   q=json.loads(gh('git/blobs/'+blob));assert q['encoding']=='base64' and q['sha']==blob,(path,'BLOB_RESPONSE_MISMATCH')
   remote=base64.b64decode(q['content']);assert len(remote)==q['size'],(path,'BLOB_SIZE_MISMATCH')
   transport='git blob base64';failure=raw.stderr.decode(errors='replace').strip()[:500]
  else:remote=raw.stdout
  assert remote==data,(path,'REMOTE_BYTES_MISMATCH')
  return {'path':path,'bytes':len(data),'gitBlob':blob,'sha256':hashlib.sha256(remote).hexdigest(),'transport':transport,'rawTransportError':failure,'exact':True}
 rows=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
  for row in pool.map(read,changed):
   rows.append(row)
   if len(rows)%10==0:print(json.dumps({'verifiedFiles':len(rows),'total':len(changed)}),flush=True)
 preserved=[]
 for old,new in [('Aegis_SIM_v48_WIP_MULTI_SHIP_H4.html','archive/v48/WIP_MULTI_SHIP_H4/Aegis_SIM_v48_WIP_MULTI_SHIP_H4.html'),('AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_H4.md','archive/v48/WIP_MULTI_SHIP_H4/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_H4.md'),('SHA256SUMS_v48_WIP_MULTI_SHIP_H4.txt','archive/v48/WIP_MULTI_SHIP_H4/SHA256SUMS_v48_WIP_MULTI_SHIP_H4.txt'),('.github/workflows/multiship-h4.yml','archive/v48/WIP_MULTI_SHIP_H4/multiship-h4.yml'),('Aegis_SIM_v48.html','Aegis_SIM_v48.html')]:
  before=command(['git','rev-parse',BASE+':'+old]).decode().strip();assert entries[new]['sha']==before,new;preserved.append({'path':new,'originalBlob':before,'exact':True})
 final_head=json.loads(gh('branches/'+quote(a.branch,safe='')))['commit']['sha'];assert final_head==a.commit,('REMOTE_HEAD_CHANGED_AFTER_READBACK',final_head)
 report={'schema':'AEGIS_MULTISHIP_H4A_REMOTE_READBACK','repository':REPO,'branch':a.branch,'verifiedCommit':a.commit,'baselineCommit':BASE,'mainHead':json.loads(gh('branches/main'))['commit']['sha'],'verifiedFiles':rows,'removedPathsAbsent':deleted,'preserved':preserved,'actions':'not dispatched; user cannot use GitHub Actions; local evidence is the verification gate','pass':True}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':True,'verifiedCommit':a.commit,'files':len(rows),'preserved':len(preserved)}),flush=True)
if __name__=='__main__':main()
