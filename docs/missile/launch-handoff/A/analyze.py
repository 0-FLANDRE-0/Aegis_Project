"""Derived reporting only: no simulation execution, verdict weakening or tuning."""
from pathlib import Path
import csv,difflib,gzip,hashlib,json,math
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[3]
J=lambda x:json.loads((H/x).read_text())
G=lambda n:json.load(gzip.open(H/'final-results'/(n+'.json.gz')))
O=H/'analysis';O.mkdir(exist_ok=True)
def write(n,d):
 (O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def csvout(n,rows,columns=None):
 rows=list(rows)
 columns=columns or list(dict.fromkeys(k for r in rows for k in r))
 p=O/n
 with (gzip.open(p,'wt',newline='',encoding='utf-8') if n.endswith('.gz') else p.open('w',newline='',encoding='utf-8'))as f:
  w=csv.DictWriter(f,columns,lineterminator='\n');w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v,separators=(',',':'))if isinstance(v,(dict,list))else v for k,v in r.items()})
def brief(r):
 q=r['result'];c=r['condition'];t=q.get('telemetry',{})
 return {'id':r.get('id',c.get('caseId',f"{c['weapon']}_{c['rangeKm']}_{c['altM']}")),'variant':r.get('variant','REFERENCE_ONLY'),'weapon':c['weapon'],'rangeKm':c['rangeKm'],'altM':c['altM'],'targetSpeedMps':c.get('targetSpeedMps',250),'crossSpeedMps':c.get('crossSpeedMps',0),'rngSeed':c.get('rngSeed'),'navigationSeed':c.get('navigationSeed'),'effect':q.get('anyEffect',q.get('success')),'lethal':q.get('lethal',q.get('success')),'reason':q['reason'],'closestRecordedM':q['closestM'],'fuzeMissM':q.get('fuzeMissM'),'fragmentArrivalMissM':q.get('fragmentArrivalMissM'),'pk':q.get('pk'),'handoffAtS':t.get('handoff',{}).get('timeS')if t.get('handoff')else q.get('handoffAtS'),'flightTimeS':q['flightTimeS'],'outcome':q.get('outcome',q.get('actualOutcome'))}
def pair(rows):
 variants={v:[brief(r)for r in rows if r.get('variant')==v]for v in ['DZT','HANDOFF']}
 a,b=variants.values();assert len(a)==len(b)
 dif=[]
 for x,y in zip(a,b):
  assert (x['weapon'],x['rangeKm'],x['altM'],x['rngSeed'])==(y['weapon'],y['rangeKm'],y['altM'],y['rngSeed'])
  if x['effect']!=y['effect']or x['lethal']!=y['lethal']or x['reason']!=y['reason']:dif.append({'before':x,'after':y})
 return {'DZT':{'count':len(a),'effect':sum(bool(x['effect'])for x in a),'lethal':sum(bool(x['lethal'])for x in a)},'HANDOFF':{'count':len(b),'effect':sum(bool(x['effect'])for x in b),'lethal':sum(bool(x['lethal'])for x in b)},'allOutcomeChanges':dif,'newFailures':[d for d in dif if d['before']['effect']and not d['after']['effect']]}
summary={'build':J('build.json'),'scope':'Actual selected HTML. No full ENV_D remeasurement. All values SIM_TUNED game outputs.'}
for name in ['small','common','natural']:
 d=G(name);rows=d['rows'];summary[name]=pair(rows);csvout(name+'-shots.csv',[brief(r)for r in rows])
 if name=='small':
  for group in ['HIGH','CONTROL']:
   summary['small'][group]=pair([r for r in rows if r['condition']['name']==group])
  csvout('trajectory-10Hz.csv.gz',({'id':r['id'],'variant':r['variant'],**{k:v for k,v in p.items()if k!='telemetry'}}for r in rows for p in r['result']['samples']))
  def traces():
   for r in rows:
    for tick in r['result']['telemetry']['ticks']:
     for point in ['beforeGate','pre','post']:
      s=tick.get(point)
      if s is None:continue
      now=tick['post']['lifeS']
      if point=='beforeGate'and s['lifeS']!=now:continue
      scalars={k:v for k,v in s.items()if not isinstance(v,(dict,list))and k not in ['pnCommand','apnCommand','zemCommand']}
      chain=s.get('chain')or{};bridge=chain.get('bridge')or{};ap=chain.get('autopilot')or{};dyn=chain.get('dynamics')or{}
      g=s.get('newGate')
      yield {'id':r['id'],'variant':r['variant'],'samplePoint':point,'tickTimeS':now,**scalars,'velocityMps':s.get('velMps'),'positionM':s.get('positionM'),'config':s.get('cfg'),'currentGate':g if g and g.get('atS')==now else None,'legacyGate':s.get('gate')if point=='beforeGate'else None,'bridgeInput':bridge.get('input'),'bridgeOutput':bridge.get('output'),'autopilotOutput':ap.get('output'),'dynamicsInput':dyn.get('input'),'normalAccWorld':s.get('normalAccWorld'),'controlVector':s.get('controlVector')}
  csvout('transition-detached-ticks.csv.gz',traces())
  del d,rows

pipe=G('pipeline');rows=[];twelve=[];near=[]
for r in pipe['records']:
 c=r['condition'];tag=f"{r['variant']}_{c['weapon']}_{c['rangeKm']}km"
 for p in r['pipeline']:
  s=p['post'];ch=s.get('chain')or{};br=ch.get('bridge')or{};ap=ch.get('autopilot')or{};g=s.get('newGate')
  rows.append({'case':tag,'timeS':p['timeS'],'owner':s['owner'],'guidance':s['guidance'],'pitchover':s['pitchover'],'launchAuthority':s['launchAuthority'],'overlap':s['overlap'],'blend':s['blend'],'gateIsThisTick':bool(g and g['atS']==p['timeS']),'gate':g if g and g['atS']==p['timeS'] else None,'preGate':p['preGate'],'postDynamics':s,'currentTickCalls':p['calls'],'kappa':p['kappa'],'autopilotCommand':ap.get('command'),'bridge':br,'finalInput':p['finalInput'],'rawDemandG':s['rawDemandG'],'limitedCommandG':s['limitedCommandG'],'availableG':s['availableG'],'actualNormalG':p.get('actualNormalG'),'deliveredG':p.get('deliveredG')})
 p=min(r['pipeline'],key=lambda p:abs(p['timeS']-12));s=p['post'];ch=s['chain'];twelve.append({'case':tag,'timeS':p['timeS'],'pitchover':s['pitchover'],'owner':s['owner'],'bridgePitchRadS':ch['autopilot']['output']['omegaPit'],'finalPitchRadS':p['finalInput']['pitch'],'rawDemandG':s['rawDemandG'],'limitedCommandG':s['limitedCommandG'],'actualNormalG':p['actualNormalG'],'calls':p['calls']})
 if c['rangeKm']==.1:near.append({'variant':r['variant'],'condition':c,'result':brief(r),'handoff':r['result']['telemetry'].get('handoff'),'firstTerminal':next((p for p in r['pipeline']if p['post']['guidance']=='TERMINAL'),None),'firstEndgame':next((p for p in r['pipeline']if p['post']['guidance']=='ENDGAME'),None)})
csvout('pipeline-current-tick.csv.gz',rows);write('at12-control-chain.json',twelve);write('near-vertical-regression.json',near)
summary['boundary']=J('final-evidence/boundary-flights.json')
bd=G('boundary-flights')['records'];csvout('boundary-shots.csv',[brief(r)for r in bd]);summary['boundaryComparison']=pair(bd)

# Keep all original failed assertions, separately classify changed exact-state checks.
dom=J('final-evidence/domain-acceptance.json');failed=[];count=0
for rec in dom['records']:
 d=J('final-evidence/domain/'+rec['path']);sets=[('',d['checks'])]if isinstance(d.get('checks'),dict)else[(f"{c['ship']}/{c['scenario']}",c['checks'])for c in d['cases']]
 for case,checks in sets:
  for key,v in checks.items():
   count+=1
   if not v:failed.append({'suite':rec['path'],'case':case,'assertion':key,'pass':False})
summary['domain']={'checks':count,'passed':count-len(failed),'failed':len(failed),'failedAssertions':failed,'originalAcceptancePass':dom['pass']};write('domain-failures.json',summary['domain'])

raid=G('raid-followup');norm=[]
for ship in sorted({r['ship']for r in raid['records']}):
 a=next(r for r in raid['records']if r['ship']==ship and r['variant']=='DZT');b=next(r for r in raid['records']if r['ship']==ship and r['variant']=='HANDOFF')
 for x,y in zip(a['snapshots'],b['snapshots']):
  f=lambda s:s['state']['damage']['flooding'];water=lambda s:sum(c.get('waterM3',0)for c in f(s)['cells'])
  norm.append({'ship':ship,'timeS':x['run']['simStepCounter']/60,'hpBefore':x['state']['shipHP'],'hpAfter':y['state']['shipHP'],'moduleDamageEqual':x['state']['damage']['moduleDamage']==y['state']['damage']['moduleDamage'],'waterM3Before':water(x),'waterM3After':water(y),'floodSummaryBefore':f(x)['summary'],'floodSummaryAfter':f(y)['summary']})
write('raid-normalized-damage.json',norm)
summary['release']=J('final-evidence/release-comparison.json')

ref=G('reference-pitch-only');csvout('reference-only-shots.csv',[brief(r)for r in ref['rows']]);pk=G('reference-pk');pkrows=[]
for r in pk['rows']:
 p=r['pkEvents'][0];q=r['result'];pkrows.append({'id':r['id'],'reason':q['reason'],'closestRecordedM':q['closestM'],'fuzeMissM':q['fuzeMissM'],'fragmentArrivalMissM':q['fragmentArrivalMissM'],'pk':p['pk'],'draws':p['draws'],'nativeDamageResult':p['result'],'lifeS':p['decisionLifeS'],'observerUnchanged':r['observerLeavesOriginalResultUnchanged']})
summary['referenceOnly']={'notProduct':True,'pk':pkrows};csvout('reference-only-native-pk.csv',pkrows)

# Source diff is decoded live game text, not base64 pack noise.
changes=J('game-changes.json');diff=''
for name,v in changes['functions'].items():diff+=''.join(difflib.unified_diff(v['before'].splitlines(True),v['after'].splitlines(True),fromfile='DZT/live-main/'+name,tofile='HANDOFF/live-main/'+name))
diff+='\n'+''.join(difflib.unified_diff([],('\n'.join(changes['additions'])+'\n').splitlines(True),fromfile='/dev/null',tofile='HANDOFF/live-main/samLaunchHandoffGateA'))
(H/'game-change.diff').write_text(diff)
summary['approval']={'allRegressionPass':False,'releaseApproved':False,'knownNewFailureShots':3,'distinctNewFailureConditions':2,'reason':'SM-6 near-vertical 1 + original release240km termination OFF/ON 2; domain exact-state 6 failed. No main merge/release/tag.'}
write('SUMMARY.json',summary)

# Publication plots are standalone SVG/PNG, based only on saved measured traces.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=H/'plots';P.mkdir(exist_ok=True)
small=G('small')['rows']
for weapon in ['SM2ER','SM6']:
 fig,axs=plt.subplots(1,2,figsize=(11,4))
 for variant,color in [('DZT','#c65151'),('HANDOFF','#22886c')]:
  r=next(r for r in small if r['variant']==variant and r['condition']['weapon']==weapon and r['condition']['name']=='HIGH');ps=r['result']['samples']
  axs[0].plot([math.hypot(p['xM'],p['yM'])/1000 for p in ps],[p['altitudeM']/1000 for p in ps],label=variant,color=color)
  points=next(r['pipeline']for r in pipe['records']if r['variant']==variant and r['condition']['weapon']==weapon and r['condition']['rangeKm']==5)
  axs[1].plot([p['timeS']for p in points],[p['post']['actualNormalG']or 0 for p in points],label=variant+' actual normal G',color=color)
 axs[0].scatter([5],[20],marker='x',color='black',label='target')
 axs[0].set(xlabel='Horizontal distance (km)',ylabel='Altitude MSL (km)',title=weapon+' 5km / 20km, seed 1')
 axs[1].set(xlabel='Life (s)',ylabel='Actual normal acceleration (G)',title='Measured body response (not limited command G)')
 for ax in axs:ax.grid(alpha=.25);ax.legend(fontsize=8)
 fig.tight_layout()
 for ext in ['svg','png']:fig.savefig(P/(weapon+'-high.'+ext),dpi=140)
 plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(11,4))
for r in pipe['records']:
 if r['condition']['rangeKm']!=.1:continue
 ps=r['pipeline'];axs[0].plot([p['post']['positionM']['x']/1000 for p in ps],[p['post']['positionM']['z']/1000 for p in ps],label=r['variant'])
 axs[1].plot([p['timeS']for p in ps],[p['post']['rawDemandG']or 0 for p in ps],label=r['variant']+' demand')
axs[0].scatter([.1],[20],marker='x',color='black');axs[0].set(xlabel='Nav X (km)',ylabel='Nav altitude (km)',title='Known regression: SM-6 0.1km / 20km')
axs[1].set(xlabel='Life (s)',ylabel='Raw demanded G',title='No gain / physical limit change');axs[1].set_ylim(0,140)
for ax in axs:ax.grid(alpha=.25);ax.legend()
fig.tight_layout()
for ext in ['svg','png']:fig.savefig(P/('sm6-near-vertical-regression.'+ext),dpi=140)
plt.close(fig)
print(json.dumps({'small':summary['small']['HIGH']['HANDOFF'],'common':summary['common']['HANDOFF'],'domain':summary['domain']['passed'],'knownNewFailures':3}))
