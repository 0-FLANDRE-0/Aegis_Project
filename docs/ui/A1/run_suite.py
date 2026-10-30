"""Focused UI_A1 checks. Gameplay is additionally proven byte-exact outside UI shell."""
from pathlib import Path
import argparse,json,subprocess,sys
HERE=Path(__file__).resolve().parent;R=HERE.parents[2]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('base',type=Path);ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 jobs=[('static',HERE/'verify_static.py',[a.base,a.html,a.out/'static']),('compact',HERE/'verify_compact.py',[a.html,a.out/'compact']),('events',R/'docs/ui/A/verify_contracts.py',[a.base,a.html,a.out/'events','--part','events']),('hash',R/'docs/ui/A/verify_contracts.py',[a.base,a.html,a.out/'hash','--part','hash'])]
 suites=[]
 for name,script,args in jobs:
  subprocess.run([sys.executable,str(script),*map(str,args)],cwd=R,check=True);p=a.out/name/(name+'.json');d=json.loads(p.read_text());suites.append({'suite':name,'pass':d['pass'],'checks':len(d['checks'])})
 result={'pass':all(s['pass']for s in suites),'assertions':sum(s['checks']for s in suites),'suites':suites};(a.out/'verification-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
