"""Freeze local report logs, compress generated raw data and hash support files."""
from pathlib import Path
import gzip,hashlib,json,shutil,subprocess
H=Path(__file__).resolve().parent;R=H.parents[3];C=R/'docs/envelope/C';E=H/'evidence'
assert json.loads((E/'acceptance.json').read_text())['pass']
log=Path('/tmp/range-a/after-full.log');assert 'LOCAL_POSTPROCESS_COMPLETE' in log.read_text();shutil.copyfile(log,E/'after-full.log')
for name in ['results.json','trajectories-10hz.csv']:
 src=C/'results'/name
 if src.exists():
  data=src.read_bytes();dst=src.with_suffix(src.suffix+'.gz');dst.write_bytes(gzip.compress(data,9,mtime=0));assert gzip.decompress(dst.read_bytes())==data;src.unlink()
for src in (C/'evidence/path-final').glob('*.json'):
 if src.stat().st_size>500000:
  data=src.read_bytes();dst=src.with_suffix(src.suffix+'.gz');dst.write_bytes(gzip.compress(data,9,mtime=0));assert gzip.decompress(dst.read_bytes())==data;src.unlink()
# These fields/logs are produced after the ZIP and therefore excluded to avoid a hash cycle.
exclude={'REPOSITORY_SUPPORT.sha256','DELIVERY_MANIFEST.json','delivery.json','remote-publication.json'};files=set()
for root in [H,C,R/'docs/envelope/B']:
 for p in root.rglob('*'):
  if p.is_file()and'__pycache__'not in p.parts and p.name not in exclude:files.add(p)
for root in [R/'docs/missile/termination/A']:
 for p in root.rglob('*'):
  if p.is_file()and'__pycache__'not in p.parts and ('evidence'not in p.parts)and p.name not in exclude:files.add(p)
for name in ['README.md','AEGIS_PROJECT_INSTRUCTIONS.md','AEGIS_PLAN_STATUS_v48_WIP_RANGE_A.md','SHA256SUMS_v48_WIP_RANGE_A.txt','.github/workflows/range-a-env-c.yml','docs/pip/B/browser_backend.py','docs/pip/B/run_domain.py','docs/pip/B/verify_ui.py','docs/map/A/verify_regressions.py','docs/viewport/A/verify_regressions.py','docs/helicopter/H/browser.py','docs/helicopter/F/requirements.txt','docs/helicopter/F/verify_regression.py','docs/performance/F/package-lock.json','docs/performance/F/package.json']:files.add(R/name)
lines=[]
for p in sorted(files):lines.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(R)))
(H/'REPOSITORY_SUPPORT.sha256').write_text('\n'.join(lines)+'\n')
subprocess.run(['sha256sum','-c','SHA256SUMS_v48_WIP_RANGE_A.txt'],cwd=R,check=True)
q=subprocess.run(['sha256sum','-c',str((H/'REPOSITORY_SUPPORT.sha256').relative_to(R))],cwd=R,check=True,capture_output=True,text=True);assert q.stdout.count(': OK')==len(files)
print('Support files verified:',len(files))
