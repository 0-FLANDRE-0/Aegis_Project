"""Immutable GitHub byte readback; work branch or post-merge main receipt."""
from pathlib import Path
import argparse,concurrent.futures,hashlib,importlib.util,json,re,subprocess,time
P=Path(__file__).resolve().parent;R=P.parents[3]
s=importlib.util.spec_from_file_location('original_streaming_readback',P.with_name('B_stabilization_r4')/'remote_readback.py');old=importlib.util.module_from_spec(s);s.loader.exec_module(old)
def local(f):return {'path':str(f.relative_to(R)),'bytes':f.stat().st_size,'sha256':old.local_sha(f)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--commit',required=True);ap.add_argument('--merge-commit');ap.add_argument('--pr',type=int);a=ap.parse_args();assert re.fullmatch('[0-9a-f]{40}',a.commit)
 budget=json.loads((P/'evidence/BUDGET.json').read_text());assert time.monotonic()<=budget['deadlineMonotonic'],'TOTAL_WALL_CAP'
 build=json.loads((P/'BUILD.json').read_text());artifact=json.loads((P/'ARTIFACTS.json').read_text());assert json.loads((P/'VALIDATION.json').read_text())['status']=='PASS'
 ref=a.merge_commit or a.commit;assert re.fullmatch('[0-9a-f]{40}',ref)
 rows=([artifact['html']]if a.merge_commit else artifact['archives']+[artifact['html']])+[local(f)for f in [P/'STATUS.json',P/'VALIDATION.json',P/'APPROVED_EXPECTATIONS.json',R/'docs/contact/track/CURRENT.json',R/'deliverables/track-c-lifecycle-a/SHA256SUMS.txt']]
 receipts=[]
 def download(row):
  assert old.local_sha(R/row['path'])==row['sha256'];q=old.download(ref,row);print(json.dumps({'path':row['path'],'sha256Matches':q['sha256Matches'],'bytes':q['bytes']}),flush=True);return q
 with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:receipts=list(pool.map(download,rows))
 raw=subprocess.check_output(['git','ls-remote','origin','refs/heads/main','refs/heads/track-c-lifecycle-a'],cwd=R,text=True);refs={q.split()[1]:q.split()[0]for q in raw.splitlines()};assert refs['refs/heads/track-c-lifecycle-a']==a.commit
 q={'schema':'AEGIS_TRACK_C_REMOTE_READBACK_1','status':'PASS','artifactCommit':a.commit,'readbackCommit':ref,'stage':'POST_MERGE_MAIN'if a.merge_commit else'PRE_MERGE_ARTIFACT_BYTES','files':receipts,'remoteRefsAtReadback':refs,'readbackUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'elapsedWallS':time.monotonic()-budget['startMonotonic'],'mainHtmlSha256':build['htmlSha256']if a.merge_commit else None,'pr':a.pr,'releaseOrTagCreated':False,'directMainCommit':False}
 if a.merge_commit:
  assert a.pr and refs['refs/heads/main']==a.merge_commit
  subprocess.run(['git','fetch','--quiet','origin','main'],cwd=R,check=True);parents=subprocess.check_output(['git','show','-s','--format=%P',a.merge_commit],cwd=R,text=True).strip().split();assert len(parents)==2 and parents[0]=='d328c941d71e39ef616d4136c70bed0eeebe7f06'and parents[1]==a.commit;q.update(mergeCommit=a.merge_commit,mergeParents=parents,mergeMethod='merge',squash=False)
 dest=P/('MERGE_READBACK.json'if a.merge_commit else'REMOTE_READBACK.json');dest.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({'status':'PASS','files':len(receipts),'stage':q['stage'],'elapsedWallS':q['elapsedWallS']}))
if __name__=='__main__':main()
