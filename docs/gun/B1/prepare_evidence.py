"""Keep all numeric/log/source evidence and task-required captures; archive duplicate legacy PNGs."""
from pathlib import Path
import json,hashlib,shutil
H=Path(__file__).resolve().parent;E=H/'evidence';out=Path('/tmp/aegis-gun-b1/unpublished-legacy-captures');out.mkdir(parents=True,exist_ok=True);keep={'ui','label','mod4','ui-handoff'};rows=[]
for p in sorted(E.rglob('*.png')):
 rel=p.relative_to(E)
 if rel.parts[0]in keep or rel.parts[:2]==('regression-driver','webgl8'):continue
 data=p.read_bytes();rows.append({'path':p.relative_to(H).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()});dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(p),dest)
q={'schema':'AEGIS_GUN_B1_LEGACY_CAPTURE_ARCHIVE_1','reason':'Task-required new PC/phone muzzle, menu, AIR tag, handoff and ring-label captures are included unchanged. All numerical results, original failures, logs and test sources are included. Repeated inherited legacy UI/domain PNGs are archived outside the deliverable to avoid duplicating previous reports and exceeding GitHub per-file limits. No assertion, result, value or required GUN_B1 capture is omitted. Original PNG hashes retained here.','files':rows,'totalBytes':sum(r['bytes']for r in rows)};(E/'archived-legacy-captures.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({'archivedPngs':len(rows),'bytes':q['totalBytes']}))
p=E/'effects/partial.json'
if p.exists():p.unlink()
for p in H.rglob('__pycache__'):shutil.rmtree(p)
