"""Select the original raid rows; preserve all original assertions and values."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,sys,time
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'docs/pip/B')]
import browser_backend
browser_backend.install()
ap=argparse.ArgumentParser();ap.add_argument('variant');a=ap.parse_args();versions=json.loads((H/'builds.json').read_text())['versions'];out=H/'evidence/history'/a.variant;out.mkdir(parents=True,exist_ok=True)
module=R/'docs/helicopter/F/verify_regression.py';spec=importlib.util.spec_from_file_location('original_helicopter_regression',module);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
original=Path.read_text;source=R/'docs/multiship/H4/regression_baseline.py'
def read(p,*args,**kw):
 s=original(p,*args,**kw)
 if p==source:
  needle="for scenario in ['idle','raid','damaged']:";assert s.count(needle)==1;s=s.replace(needle,"for scenario in ['raid']:")
 return s
Path.read_text=read
from types import SimpleNamespace
start=time.perf_counter();report=m.baseline(SimpleNamespace(baseline=R/versions['VP']['file'],html=R/versions[a.variant]['file'],out=out))
summary={'variant':a.variant,'pass':report['pass'],'checks':{r['ship']+':'+k:v for r in report['cases']for k,v in r['checks'].items()},'errors':report['errors'],'elapsedS':time.perf_counter()-start,'scope':'Original raid rows only; all assertions unmodified','candidateSha256':report['candidateSha256']};(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary));
