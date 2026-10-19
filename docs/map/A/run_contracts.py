"""Run the unchanged UI_A native contract assertions and record both inputs."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser();ap.add_argument('base',type=Path);ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--part',choices=['events','hash'],required=True);a=ap.parse_args()
script=R/'docs/ui/A/verify_contracts.py';sys.argv=[str(script),str(a.base),str(a.html),str(a.out),'--part',a.part]
try:runpy.run_path(str(script),run_name='__main__')
except SystemExit as e:
 if e.code:raise
p=a.out/(a.part+'.json');d=json.loads(p.read_text());d.update(htmlSha256=hashlib.sha256(a.html.read_bytes()).hexdigest(),baselineSha256=hashlib.sha256(a.base.read_bytes()).hexdigest());p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
