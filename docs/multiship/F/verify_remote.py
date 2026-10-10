"""Independent GitHub tree and raw-byte readback, without Actions or writes.

Run after normal push. Report is excluded from its own support checksum;
the later evidence-only commit leaves the verified HTML/support blobs intact.
"""
import argparse,concurrent.futures,hashlib,json,subprocess
from pathlib import Path
from urllib.parse import quote
REPO='0-FLANDRE-0/Aegis_Project'
BASE='bdcf8d1724a72587f9d42e4b1cf70ba4cbe57ef6'
ROOT=Path(__file__).resolve().parents[3]
def command(args):return subprocess.run(args,cwd=ROOT,capture_output=True,check=True).stdout
def gh(endpoint,*args):return command(['gh','api','repos/'+REPO+'/'+endpoint,*args])
def main():
 p=argparse.ArgumentParser();p.add_argument('commit');p.add_argument('out',type=Path);p.add_argument('--branch',default='multiship-ew-f');a=p.parse_args()
 head=json.loads(gh('branches/'+quote(a.branch,safe='')))['commit']['sha'];assert head==a.commit,('REMOTE_HEAD_CHANGED',head)
 tree=json.loads(gh('git/trees/'+a.commit+'?recursive=1'));assert not tree.get('truncated');entries={q['path']:q for q in tree['tree']}
 changed=command(['git','diff','--name-only','--diff-filter=ACMR',BASE,a.commit]).decode().splitlines()
 deleted=command(['git','diff','--name-only','--diff-filter=D',BASE,a.commit]).decode().splitlines()
 deleted=sorted(set(deleted)|{'Aegis_SIM_v48_WIP_MULTI_SHIP_E.html','AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_E.md','SHA256SUMS_v48_WIP_MULTI_SHIP_E.txt','.github/workflows/multiship-e.yml'})
 assert all(q not in entries for q in deleted)
 def read(path):
  data=command(['git','show',a.commit+':'+path]);blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert entries[path]['sha']==blob,(path,'BLOB_MISMATCH')
  remote=gh('contents/'+quote(path,safe='/')+'?ref='+a.commit,'-H','Accept: application/vnd.github.raw+json');assert remote==data,(path,'RAW_BYTES_MISMATCH')
  return {'path':path,'bytes':len(data),'gitBlob':blob,'sha256':hashlib.sha256(remote).hexdigest(),'exact':True}
 rows=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
  for row in pool.map(read,changed):
   rows.append(row)
   if len(rows)%10==0:print(json.dumps({'verifiedFiles':len(rows),'total':len(changed)}),flush=True)
 preserved=[]
 for old,new in [('Aegis_SIM_v48_WIP_MULTI_SHIP_E.html','archive/v48/WIP_MULTI_SHIP_E/Aegis_SIM_v48_WIP_MULTI_SHIP_E.html'),('AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_E.md','archive/v48/WIP_MULTI_SHIP_E/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_E.md'),('SHA256SUMS_v48_WIP_MULTI_SHIP_E.txt','archive/v48/WIP_MULTI_SHIP_E/SHA256SUMS_v48_WIP_MULTI_SHIP_E.txt'),('.github/workflows/multiship-e.yml','archive/v48/WIP_MULTI_SHIP_E/multiship-e.yml'),('Aegis_SIM_v48.html','Aegis_SIM_v48.html')]:
  before=command(['git','rev-parse',BASE+':'+old]).decode().strip();assert entries[new]['sha']==before,new;preserved.append({'path':new,'originalBlob':before,'exact':True})
 final_head=json.loads(gh('branches/'+quote(a.branch,safe='')))['commit']['sha'];assert final_head==a.commit,('REMOTE_HEAD_CHANGED_AFTER_READBACK',final_head)
 report={'schema':'AEGIS_MULTISHIP_F_REMOTE_READBACK','repository':REPO,'branch':a.branch,'verifiedCommit':a.commit,'baselineCommit':BASE,'mainHead':json.loads(gh('branches/main'))['commit']['sha'],'verifiedFiles':rows,'removedPathsAbsent':deleted,'preserved':preserved,'actions':'not dispatched; user cannot use GitHub Actions; local evidence is the verification gate','pass':True}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':True,'verifiedCommit':a.commit,'files':len(rows),'preserved':len(preserved)}),flush=True)
if __name__=='__main__':main()
