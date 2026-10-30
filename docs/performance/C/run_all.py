"""Local regression runner. Performance timing is a separate serial command."""
import argparse,concurrent.futures,json,os,subprocess,sys
from pathlib import Path
from suite_catalog import SUITES,ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--workers',type=int,default=3);p.add_argument('--exclude',nargs='*',default=[]);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 def run(name):
  dest=a.out/name;dest.mkdir(exist_ok=True);args=[sys.executable,str(ROOT/'docs/performance/C/run_suite.py'),name,str(a.html.resolve()),str(dest.resolve()),'--baseline',str(a.baseline.resolve())]
  r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);(dest/'execution.log').write_text(r.stdout+r.stderr);row={'suite':name,'exit':r.returncode};print(json.dumps(row),flush=True);return row
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers)as pool:rows=list(pool.map(run,[n for n in SUITES if n not in a.exclude]))
 (a.out/'regression-exits.json').write_text(json.dumps(rows,indent=2)+'\n');raise SystemExit(0 if all(q['exit']==0 for q in rows)else 1)
if __name__=='__main__':main()
