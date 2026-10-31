"""G7 measured outcomes only; no tuning targets or hypothesis acceptance threshold."""
from pathlib import Path
import json,csv,statistics as st,argparse,itertools,os
H=Path(__file__).resolve().parent;E=Path(os.environ.get('GUN_B1_EFFECT_OUT',str(H/'evidence/effects')));ap=argparse.ArgumentParser();ap.add_argument('--partial',action='store_true');a=ap.parse_args()
rows=[json.loads(l)for p in sorted(E.glob('worker[0-9].jsonl'))for l in p.read_text().splitlines()if l.strip()];assert len({r['caseId']for r in rows})==len(rows)
if not a.partial:assert len(rows)==960 and {r['caseId']for r in rows}==set(range(960))
summary=[]
for ship,bearing,count,on in itertools.product(['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA'],[0,90],range(1,5),[False,True]):
 q=[r['result']for r in rows if (r['ship'],r['bearing'],r['count'],r['on'])==(ship,bearing,count,on)]
 if not q:continue
 if not a.partial:assert len(q)==30 and {r['seed']for r in q}==set(range(419010,419040))
 summary.append({'ship':ship,'bearing':bearing,'count':count,'autoAA':on,'trials':len(q),'gunPreCiwsKills':sum(r['gunPreCiwsKills']for r in q),'allPreCiwsKills':sum(r['preCiwsKills']for r in q),'meanGunRounds':st.mean(r['shots']for r in q),'totalGunRounds':sum(r['shots']for r in q),'meanCloseInInventoryUnits':st.mean(r['ciwsUsed']for r in q),'shipHits':sum(r['shipHits']for r in q),'trialsWithShipHits':sum(r['shipHits']>0 for r in q),'meanHpAfter':st.mean(r['hpAfter']for r in q),'hpPositiveAtEnd':sum(r['shipAlive']for r in q),'meanScenarioSeconds':st.mean(r['seconds']for r in q)})
fatalUnique=all(len(ids:=[v['id']for e in r['result']['auto']['log']if e['kind']=='AIRBURST'for v in e['results']if v['result']in ['KILL','STRUCT_FAIL']])==len(set(ids))for r in rows)
complete=[json.loads(p.read_text())for p in E.glob('worker[0-9]-complete.json')]
out={'schema':'AEGIS_GUN_B1_EFFECTS_1','complete':not a.partial,'trials':len(rows),'conditions':len(summary),'htmlSha256':sorted({r['htmlSha256']for r in rows}),'seedRange':[419010,419039],'summary':summary,'execution':complete,'fatalEffectIdsUniquePerTrial':fatalUnique,'offAutomaticShotsZero':all(r['result']['shots']==0 for r in rows if not r['on']),'errors':[e for q in complete for e in q['errors']],'scope':'Native full fixed tick with real Kh35U flight and observed-track FCS; MANUAL SAM doctrine and native CIWS. Initial 11km + 0.3km per missile, 10m altitude, 3-degree spread. Each run restores pristine operational inventory and seed. Ends after threats retire or 50s; survival is only at that scenario end. preCIWS means threat never entered nominal 3km boundary; native CIWS can engage outside it. DDG close-in inventory units sum 20mm rounds and RAM missiles; CG uses only 20mm. hpPositiveAtEnd means HP>0 only, not a long-term flooding/sinking survival assessment. No hit-rate objective or product tuning from these results.'}
name='partial'if a.partial else 'summary';(E/(name+'.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
if not a.partial:
 assert fatalUnique and not out['errors']and out['offAutomaticShotsZero']and len(complete)==3
 for fn,data in [('summary.csv',summary),('trials.csv',[{k:v for k,v in r.items()if k not in ['result']}|{k:v for k,v in r['result'].items()if k not in ['targets','auto']} for r in sorted(rows,key=lambda r:r['caseId'])])]:
  with(E/fn).open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(2,4,figsize=(15,7));metrics=[('gunPreCiwsKills','5in kills before 3km / trial'),('meanGunRounds','5in rounds / trial'),('meanCloseInInventoryUnits','Close-in units / trial'),('trialsWithShipHits','Trials with ship hits / 30')]
 for si,ship in enumerate(['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']):
  for mi,(key,label)in enumerate(metrics):
   ax=axes[si][mi]
   for bearing,color in [(0,'#1c7f9b'),(90,'#d77a24')]:
    for on,style in [(False,'--'),(True,'-')]:
     q=[r for r in summary if r['ship']==ship and r['bearing']==bearing and r['autoAA']==on];ys=[r[key]/r['trials']if key=='gunPreCiwsKills'else r[key]for r in q];ax.plot([r['count']for r in q],ys,style,marker='o',color=color,label=f'{bearing} deg {"ON"if on else"OFF"}')
   ax.set(title=ship[:2]+' '+label,xlabel='Simultaneous Kh-35U',xticks=[1,2,3,4]);ax.grid(alpha=.25)
 axes[0][0].legend(fontsize=8);fig.suptitle('GUN_B1 native game outcomes (30 paired seeds per condition, no target rate)');fig.tight_layout();fig.savefig(E/'effects.svg');plt.close(fig)
print(json.dumps({'trials':len(rows),'conditions':len(summary),'complete':not a.partial,'offShotsZero':out['offAutomaticShotsZero']}))
