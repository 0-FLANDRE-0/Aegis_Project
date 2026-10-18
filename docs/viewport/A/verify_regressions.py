"""I: rerun current native suites, with explicit historical-test migrations only.

No production code is altered to satisfy a test. HELI_F2's diagnostic census is
216 after SOV_A's fourth class, and map taps now use the requested public map
transform instead of the obsolete whole-window-center arithmetic.
"""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]
SUITES={
 'helicopter-flight':'docs/helicopter/J/verify_native.py',
 'aps153':'docs/helicopter/G/verify_native.py',
 'isar-native':'docs/helicopter/L/verify_native.py',
 'isar-classes':'docs/helicopter/L/verify_classes.py',
 'isar-clock':'docs/helicopter/L/verify_clock.py',
 'isar-ui':'docs/helicopter/L/verify_ui.py',
 'emcon-native':'docs/helicopter/K/verify_native.py',
 'emcon-ui':'docs/helicopter/K/verify_ui.py',
 'harpoon-f1':'docs/helicopter/H/verify_native.py',
 'harpoon-clock':'docs/helicopter/H/verify_ui_clock.py',
 'sov-native':'docs/sovremenny/A/verify_native.py',
 'sov-casualty':'docs/sovremenny/A/verify_casualty.py',
 'sov-deployment':'docs/sovremenny/A/verify_deployment.py',
 'sov-visual':'docs/sovremenny/A/verify_visual.py',
}
def adapted(name,html,out):
 f=R/SUITES[name];sys.path.insert(0,str(f.parent));s=f.read_text();changes=[]
 if name=='helicopter-flight':
  needle="def flight_sig(r):return [{k:v for k,v in row.items()}for row in r['rows']]";assert s.count(needle)==1
  replacement="def flight_sig(r):\n     def clean(v):\n      if isinstance(v,dict):return {k:clean(x)for k,x in v.items()if not(k=='isar'and x is None)}\n      if isinstance(v,list):return [clean(x)for x in v]\n      return v\n     return clean(r['rows'])"
  s=s.replace(needle,replacement);changes.append('HELI_F2 added nullable isar display metadata; remove only isar:null for historical DDG trajectory equality, preserve every flight/sensor value')
 if name=='isar-native':
  needle="len(diag['rows'])==162";assert s.count(needle)==1;s=s.replace(needle,"len(diag['rows'])==216");changes.append('SOV_A library already has 4 classes: 216 diagnostic rows')
 if name=='isar-ui':
  needle="xy={'x':width/2+tr['positionM']['x']*min(width,height)*.42/40000,'y':height/2+tr['positionM']['y']*min(width,height)*.42/40000}";assert s.count(needle)==1
  s=s.replace(needle,"xy=x.evaluate('t=>__VIEWPORT_A__.worldToScreen(t.x*.0038,t.y*.0038)',tr['positionM'])");changes.append('Map client tap via actual unified worldToScreen, replacing old viewport-center formula')
 scope={'__file__':str(f),'__name__':'__main__'};sys.argv=[str(f)]+([str(R/'archive/v48/WIP_HELI_CG_A/Aegis_SIM_v48_WIP_HELI_CG_A.html')]if name=='helicopter-flight'else[])+[str(html),str(out)]
 out.mkdir(parents=True,exist_ok=True);(out/'test-migration.json').write_text(json.dumps({'source':str(f.relative_to(R)),'sourceSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'changes':changes},indent=2)+'\n')
 exec(compile(s,str(f),'exec'),scope)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--only',choices=SUITES);ap.add_argument('--start-at',choices=SUITES);a=ap.parse_args()
 if a.only:return adapted(a.only,a.html,a.out)
 a.out.mkdir(parents=True,exist_ok=True);rows=[];start=not a.start_at
 for name in SUITES:
  if name==a.start_at:start=True
  if not start:continue
  print('RUN '+name,flush=True);run=subprocess.run([sys.executable,__file__,str(a.html),str(a.out/name),'--only',name],cwd=R);rows.append({'suite':name,'exitCode':run.returncode});(a.out/'suite-progress.json').write_text(json.dumps(rows,indent=2)+'\n')
  if run.returncode:raise SystemExit(run.returncode)
 # Exact same-artifact DDG/CG whole-simulation comparison to SOV_A.
 cmd=[sys.executable,'docs/helicopter/F/verify_regression.py',str((R/'Aegis_SIM_v48_WIP_SOV_A.html')if(R/'Aegis_SIM_v48_WIP_SOV_A.html').exists()else(R/'archive/v48/WIP_SOV_A/Aegis_SIM_v48_WIP_SOV_A.html')),str(a.html),str(a.out/'paired-baseline'),'--baseline-only'];run=subprocess.run(cmd,cwd=R);rows.append({'suite':'paired-baseline','exitCode':run.returncode});(a.out/'suite-progress.json').write_text(json.dumps(rows,indent=2)+'\n');raise SystemExit(run.returncode)
if __name__=='__main__':main()
