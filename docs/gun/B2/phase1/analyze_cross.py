from pathlib import Path
import csv,json,statistics
P=Path(__file__).resolve().parent;rows=[]
for stage,file in [('INITIAL_ALIGNMENT_ONLY','evidence/alignment/results.json'),('FINAL_ALL_FEATURES','evidence/final-pairs/results.json')]:
 q=json.loads((P/file).read_text());assert q['pass']
 for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
  for bearing in [0,90]:
   for enabled in [False,True]:
    rr=[r for r in q['rows']if(r['case']['ship'],r['case']['bearing'],r['case']['alignment'])==(ship,bearing,enabled)];shots=[s for r in rr for s in r['data']['shots']];v=[s['cpa']['resolvedM']['cross']for s in shots if s.get('cpa')and s.get('assignedTargetAliveBeforeBurst')is True];ages=[s['solutionAgeS']for s in shots];rows.append({'stage':stage,'ship':ship,'bearing':bearing,'enabled':enabled,'cases':len(rr),'shots':len(shots),'aliveAssignedPreBurstCpaN':len(v),'preBurstCrossMeanM':statistics.mean(v)if v else None,'preBurstCrossStdM':statistics.pstdev(v)if v else None,'meanReleaseAgeS':statistics.mean(ages)if ages else None,'sourceHtmlSha256s':sorted({r['productSha256']for r in rr})})
(P/'evidence/cross-comparison.json').write_text(json.dumps({'rows':rows,'scope':'2 common seeds per cell, actual observed/truth decomposition after action only; not30seed population. INITIAL is chronological implementation-stage evidence; FINAL mixes all new features. Native fuze now ends flight before geometricCPA, so full-feature pre-burst closest distances have a different endpoint.','coefficientsChosenFromTheseValues':False},indent=2)+'\n')
with(P/'evidence/cross-comparison.csv').open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print([r for r in rows if r['bearing']==90])
