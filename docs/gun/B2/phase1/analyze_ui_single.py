from pathlib import Path
import csv,json
P=Path(__file__).resolve().parent;E=P/'evidence/ui-single-cause';rows=[];details=[]
for name in ['OFF','ALIGNMENT','WINDOW','ALL','PRECHECK_UNION']:
 q=json.loads((E/name/'gun/B1/evidence/ui/results.json').read_text());s=q['records']['1400.CG.MAIN.shots'];timeline=q['records']['1400.CG.MAIN.timeline'];first=next(t for t in timeline if t['step']==224)
 rows.append({'variant':name,'passedOriginalSingleNative':q['checks']['1400.CG.MAIN.G5.singleNative'],'shots':[g['q']['shotsFired']for g in s],'finalStopReasons':[g['q']['pendingSingleFire']['stopReason']for g in s],'step223AfterTickVerticalMissM':[g['pointing']['verticalMissM']for g in first['guns']],'verticalLimitM':[g['pointing']['verticalLimitM']for g in first['guns']],'normalizedMiss':[g['pointing']['normalizedMiss']for g in first['guns']]})
 for t in timeline:
  for g in t['guns']:
   p=g['pointing'];details.append({'variant':name,'step':t['step'],'mount':g['id'],'pointingOk':p['ok'],'reason':p.get('reason'),'crossMissM':p.get('crossMissM'),'verticalMissM':p.get('verticalMissM'),'verticalLimitM':p.get('verticalLimitM'),'normalizedMiss':p.get('normalizedMiss'),'margin':p.get('releaseAimMargin01'),'pending':g['q']['pendingSingleFire']['active'],'pendingStopReason':g['q']['pendingSingleFire']['stopReason']})
q={'rows':rows,'productChanged':False,'experimentalPrecheckAdopted':False,'finalPointingLimitWeakened':False,'cause':'Independent WINDOW-only reproduces 2->0 CG shots, ALIGNMENT-only preserves 2. At baseline firing tick223, vertical pointing miss 1.67-1.69m fits legacy7.5m vertical budget but not symmetric1.5m floor ×.78=1.17m. Pending intent later ends TRACK_SUPPORT_BLOCKED. Recomputing before strict readiness in private PRECHECK_UNION experiment does not restore fire; rejected. Original 4 UI failures remain unapproved; no coefficient or expectation update.'};(E/'cause.json').write_text(json.dumps(q,indent=2)+'\n')
with(E/'timeline.csv').open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=list(details[0]));w.writeheader();w.writerows(details)
print(json.dumps(rows))
