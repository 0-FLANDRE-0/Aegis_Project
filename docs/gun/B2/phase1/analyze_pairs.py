from pathlib import Path
import json,math,statistics
P=Path(__file__).resolve().parent;file=P/'evidence/final-pairs/results.json';q=json.loads(file.read_text());groups=[];checks={}
for enabled in [False,True]:
 rows=[r for r in q['rows']if r['case']['alignment']==enabled];shots=[s for r in rows for s in r['data']['shots']]
 norm=lambda v:math.sqrt(sum(x*x for x in v.values()))
 residuals=[]
 for s in shots:
  t=s['solveTarget'];v=s['observation']['velocityMps'];d={axis:v[axis]-t['v'+axis+'Mps']for axis in ['x','y','z']};residuals.append(norm(d))
 age=[s['solutionAgeS']for s in shots];origin=[norm(s['originDeltaM'])for s in shots];position=[norm(s['observedDisplacementSinceSolveM'])for s in shots]
 group={'enabled':enabled,'trials':len(rows),'shots':len(shots),'meanAgeS':statistics.mean(age),'maxAgeS':max(age),'maxOriginDeltaM':max(origin),'maxObservedPositionSinceSolveM':max(position),'maxObservedVelocitySinceSolveMps':max(residuals),'meanAbsCrossPointingM':statistics.mean(abs(s['pointing']['crossMissM'])for s in shots)};groups.append(group)
 if enabled:checks.update(currentTick=all(a==0 for a in age),sameTrunnion=all(a==0 for a in origin),currentObservedPosition=all(a==0 for a in position),currentObservedVelocity=all(a==0 for a in residuals))
checks['pairedFixturePass']=q['pass'];out={'pass':all(checks.values()),'checks':checks,'groups':groups,'note':'All-five-feature OFF/ON final pairing. Alignment-only intervention is separately preserved in evidence/alignment.'};(P/'evidence/release-reconciliation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));raise SystemExit(not out['pass'])
