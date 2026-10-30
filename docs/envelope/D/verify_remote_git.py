"""Full file readback from an independent GitHub Git clone, without alternates.

Use this when the API credential cannot read private blob endpoints. This uses
normal Git authentication, never copies local objects, and changes no artifacts.
The publication receipt and this helper are the only post-artifact additions.
"""
import argparse,concurrent.futures,hashlib,io,json,os,subprocess,tempfile,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
REPO='0-FLANDRE-0/Aegis_Project';URL='https://github.com/'+REPO+'.git';BRANCH='reg-k-env-d';BASE='80b65143d10f0fc42072d068dacbbc69a2b78fc3'
p=argparse.ArgumentParser();p.add_argument('commit');p.add_argument('--bare',type=Path);p.add_argument('--out',type=Path,default=H/'remote-publication.json');a=p.parse_args()
bare=a.bare or Path(tempfile.mkdtemp(prefix='aegis-env-d-git-readback-'))/'remote.git'
env=os.environ.copy()
for key in ['GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES','GIT_DIR','GIT_WORK_TREE']:env.pop(key,None)
def git(where,*args):return subprocess.check_output(['git','-C',str(where),*args],env=env)
if not bare.exists():subprocess.run(['git','clone','--bare','--depth=1','--single-branch','--branch',BRANCH,URL,str(bare)],env=env,check=True)
assert bare.resolve()!=(R/'.git').resolve()
assert git(bare,'rev-parse','--is-bare-repository').strip()==b'true'
assert git(bare,'remote','get-url','origin').decode().strip()==URL
assert not(bare/'objects/info/alternates').exists()
assert git(bare,'rev-parse','refs/heads/'+BRANCH).decode().strip()==a.commit
# A full branch refetch is necessary if a previous filtered clone omitted blobs.
# No local clone, alternates, object copies or shared object stores are accepted.
def tree(where,commit):
 out={}
 for row in git(where,'ls-tree','-rz','--full-tree',commit).split(b'\0'):
  if not row:continue
  meta,name=row.split(b'\t',1);mode,kind,sha=meta.decode().split();out[name.decode()]={'mode':mode,'type':kind,'sha':sha}
 return out
expected=tree(R,a.commit);actual=tree(bare,a.commit);assert expected==actual
names=git(R,'diff','--no-renames','--name-only','--diff-filter=ACM',BASE,a.commit).decode().splitlines()
removed=git(R,'diff','--no-renames','--name-only','--diff-filter=D',BASE,a.commit).decode().splitlines();assert all(n not in actual for n in removed)
# Enumerating the local clone object store does not trigger lazy downloads.
present={r.split()[0]for r in git(bare,'cat-file','--batch-all-objects','--batch-check=%(objectname)').decode().splitlines()}
assert all(actual[n]['sha']in present for n in names),'FULL_REMOTE_BLOBS_NOT_FETCHED'
def verify(name):
 data=git(bare,'cat-file','blob',actual[name]['sha']);local=git(R,'show',a.commit+':'+name);assert data==local,name
 blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert blob==actual[name]['sha']
 q={'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'gitBlob':blob,'fullReadback':True}
 if name.endswith('.zip'):
  with zipfile.ZipFile(io.BytesIO(data))as z:
   assert z.testzip()is None;q.update(zipMembers=len(z.namelist()),remoteZipCrcValid=True)
   if name.endswith('_HTML.zip'):
    html=name.removesuffix('_HTML.zip')+'.html';assert z.namelist()==[Path(html).name];assert z.read(z.namelist()[0])==git(R,'show',a.commit+':'+html)
 return q
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:files=list(pool.map(verify,names))
protected=json.loads((H/'remote-heads-before.json').read_text());raw=git(R,'ls-remote','origin',*[f'refs/heads/{n}'for n in protected],'refs/heads/'+BRANCH).decode();heads={r.split()[1].removeprefix('refs/heads/'):r.split()[0]for r in raw.splitlines()}
assert all(heads.get(n)==v for n,v in protected.items());assert heads[BRANCH]==a.commit
out={'schema':'AEGIS_ENV_D_REMOTE_PUBLICATION_1','pass':True,'repository':REPO,'branch':BRANCH,'verifiedCommit':a.commit,'baselineCommit':BASE,'readbackTransport':'INDEPENDENT_FULL_GITHUB_GIT_CLONE','apiAttempt':'Private blob API returned HTTP401; no credential values were read or changed. Used the working normal Git transport.','independentObjectStore':True,'alternatesUsed':False,'allVerifiedBlobsPresentBeforeReading':True,'remoteTreeEqualsLocalCommittedTree':True,'fullReadbackFiles':len(files),'fullReadbackBytes':sum(q['bytes']for q in files),'files':files,'rootArchivedPathsAbsent':removed,'protectedHeadsUnchanged':protected,'actionsDispatched':False,'mainMerged':False,'newPrCreated':False,'artifactFilesChangedAfterVerification':False}
a.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':True,'commit':a.commit,'files':len(files),'bytes':out['fullReadbackBytes'],'transport':out['readbackTransport']}))
