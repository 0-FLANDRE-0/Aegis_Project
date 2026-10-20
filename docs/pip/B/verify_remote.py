"""Full committed-file readback via gh; no credentials or signed URLs in receipts."""
import argparse,base64,concurrent.futures,hashlib,json,subprocess,tempfile,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;REPO='0-FLANDRE-0/Aegis_Project'
p=argparse.ArgumentParser();p.add_argument('commit');p.add_argument('--out',type=Path,default=H/'remote-publication.json');a=p.parse_args()
def gh(endpoint,*args):return subprocess.check_output(['gh','api',endpoint,*args],cwd=R)
def tree(commit):
 raw=subprocess.check_output(['git','ls-tree','-rz','--full-tree',commit],cwd=R);out={}
 for line in raw.split(b'\0'):
  if not line:continue
  meta,name=line.split(b'\t',1);mode,kind,sha=meta.decode().split();out[name.decode()]={'mode':mode,'type':kind,'sha':sha}
 return out
expected=tree(a.commit);remote=json.loads(gh(f'repos/{REPO}/git/trees/{a.commit}?recursive=1'));assert not remote.get('truncated');actual={r['path']:{k:r[k]for k in ['mode','type','sha']}for r in remote['tree']if r['type']!='tree'};assert actual==expected,'REMOTE_TREE_MISMATCH'
base=json.loads((H/'remote-preflight.json').read_text());baseline='662eb14e0344b5202631ab95ec1f8cd354d4a41a';names=subprocess.check_output(['git','diff','--no-renames','--name-only','--diff-filter=ACM',baseline,a.commit],cwd=R,text=True).splitlines();removed=subprocess.check_output(['git','diff','--no-renames','--name-only','--diff-filter=D',baseline,a.commit],cwd=R,text=True).splitlines();assert all(n not in actual for n in removed)
# Read full blobs even when recursive tree IDs already match.
def verify(name):
 payload=json.loads(gh(f'repos/{REPO}/git/blobs/{actual[name]["sha"]}','-H','Accept: application/vnd.github+json'));assert payload['encoding']=='base64'and payload['sha']==actual[name]['sha'];data=base64.b64decode(payload['content']);assert len(data)==payload['size'];local=subprocess.check_output(['git','show',a.commit+':'+name],cwd=R);assert data==local,name
 blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert blob==actual[name]['sha'];q={'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'gitBlob':blob,'fullReadback':True}
 if name.endswith('.zip'):
  import io
  with zipfile.ZipFile(io.BytesIO(data))as z:
   assert z.testzip()is None;q['zipMembers']=len(z.namelist());q['remoteZipCrcValid']=True
   if name.endswith('_HTML.zip'):
    htmlPath=name.removesuffix('_HTML.zip')+'.html';assert z.namelist()==[Path(htmlPath).name];assert z.read(z.namelist()[0])==subprocess.check_output(['git','show',a.commit+':'+htmlPath],cwd=R)
 return q
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:files=list(pool.map(verify,names))
refs=subprocess.check_output(['git','ls-remote','origin',*[f'refs/heads/{n}'for n in base['protectedHeads']],'refs/heads/pip-b-env-a'],cwd=R,text=True);heads={line.split()[1].removeprefix('refs/heads/'):line.split()[0]for line in refs.splitlines()};assert all(heads.get(n)==v for n,v in base['protectedHeads'].items());assert heads['pip-b-env-a']==a.commit
out={'schema':'AEGIS_PIP_B_REMOTE_PUBLICATION_1','pass':True,'repository':REPO,'branch':'pip-b-env-a','verifiedCommit':a.commit,'baselineCommit':baseline,'readbackTransport':'GITHUB_GIT_BLOB_JSON_BASE64','recursiveTreeComplete':True,'remoteTreeEqualsLocalCommittedTree':True,'fullReadbackFiles':len(files),'fullReadbackBytes':sum(r['bytes']for r in files),'files':files,'rootArchivedPathsAbsent':removed,'protectedHeadsUnchanged':base['protectedHeads'],'actionsDispatched':False,'mainMerged':False,'newPrCreated':False};a.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':True,'commit':a.commit,'files':len(files),'bytes':out['fullReadbackBytes']}))
