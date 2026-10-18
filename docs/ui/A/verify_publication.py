"""Full remote blob readback through the configured gh identity (no secrets)."""
from pathlib import Path
import argparse,base64,concurrent.futures,hashlib,json,subprocess,time
REPO='0-FLANDRE-0/Aegis_Project'
def gh(path):return json.loads(subprocess.check_output(['gh','api','repos/'+REPO+'/'+path]))
def git(*args):return subprocess.check_output(['git',*args])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--branch',default='ui-a');ap.add_argument('--base',default='3afd0fc04d0dc707205f5532f9016cd32b10eb56');ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();commit=git('rev-parse','HEAD').decode().strip();assert gh('git/ref/heads/'+a.branch)['object']['sha']==commit
 tree=gh('git/trees/'+commit+'?recursive=1');assert not tree['truncated'];remote={r['path']:r for r in tree['tree']};paths=git('diff','--name-only','--diff-filter=ACMRT','-M',a.base,commit).decode().splitlines()
 def read(path):
  local=git('show',commit+':'+path);expected=hashlib.sha1(b'blob '+str(len(local)).encode()+b'\0'+local).hexdigest();row=remote[path];assert row['sha']==expected and row['size']==len(local),path
  for attempt in range(3):
   try:
    blob=gh('git/blobs/'+expected);raw=base64.b64decode(blob['content']);assert raw==local,path;return {'path':path,'bytes':len(raw),'gitBlob':expected,'sha256':hashlib.sha256(raw).hexdigest(),'fullReadback':True}
   except Exception:
    if attempt==2:raise
    time.sleep(1)
 with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:rows=list(pool.map(read,paths))
 protected={name:gh('git/ref/heads/'+name)['object']['sha']for name in ['main','helicopter-isar-f2','sovremenny-hull-a','viewport-a']}
 out={'schema':'AEGIS_UI_A_REMOTE_PUBLICATION_1','pass':True,'repository':REPO,'branch':a.branch,'verifiedCommit':commit,'baselineCommit':a.base,'recursiveTreeComplete':True,'files':rows,'fileCount':len(rows),'protectedHeads':protected};a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':True,'verifiedCommit':commit,'files':len(rows)}))
if __name__=='__main__':main()
