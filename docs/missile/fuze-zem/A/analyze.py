"""Read measurements only. Never launches or tunes a missile."""
from pathlib import Path
import csv,gzip,json,collections,math,io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent
load=lambda n:json.loads(gzip.decompress((H/'results'/n).read_bytes()))
delayByWeapon={x['weapon']:x['processingDelayS']for x in json.loads((H/'evidence/fuze-profiles.json').read_text())}
old=load('limited.json.gz')['rows'];det=load('deterministic.json.gz')['rows'];rev=load('revision3.json.gz')['rows']
rows=[x for x in old if x['variant']in['BASE','F','Z']]+[x for x in det if x['variant']=='D']+[x for x in rev if x.get('group')=='TERM_REVISION_3'];base={x['id']:x for x in rows if x['variant']=='BASE'};index={(x['variant'],x['id']):x for x in rows}
P=H/'plots';P.mkdir(exist_ok=True)
def writecsv(name,records):
 records=list(records)
 if not records:return
 fields=list(dict.fromkeys(k for r in records for k in r));s=io.StringIO();w=csv.DictWriter(s,fieldnames=fields);w.writeheader();w.writerows(records);b=s.getvalue().encode('utf-8-sig');p=H/name
 p.write_bytes(gzip.compress(b,9,mtime=0)if str(p).endswith('.gz')else b)
def summary(v,rr=rows,bb=base):
 a=[x for x in rr if x['variant']==v];loss=[x['id']for x in a if bb[x['id']]['result']['success']and not x['result']['success']];gain=[x['id']for x in a if not bb[x['id']]['result']['success']and x['result']['success']];return {'variant':v,'shots':len(a),'effects':sum(x['result']['success']for x in a),'lethal':sum(x['result']['lethal']for x in a),'losses':loss,'gains':gain,'reasons':dict(collections.Counter(x['result']['reason']for x in a))}
S={v:summary(v)for v in['BASE','F','D','Z','T','ZT','DZT']}
def flatten(x):
 r=x['result'];events=r.get('diagnostic',{}).get('fuze',[]);de=[e for e in events if e.get('detection')];hit=next((e for e in events if e['allow']),None);si=next((e for e in events if (e.get('detection')or{}).get('model')=='SAM_SIGNAL_A'and e['allow']),None);c=x['condition']
 return {'variant':x['variant'],'caseId':x.get('id',c.get('caseId')),'weapon':c['weapon'],'rangeKm':c['rangeKm'],'altM':c['altM'],'targetSpeedMps':c.get('targetSpeedMps',0),'crossSpeedMps':c.get('crossSpeedMps',0),'rngSeed':c.get('rngSeed'),'navigationSeed':c.get('navigationSeed'),'effect':r.get('success'),'lethal':r.get('lethal'),'reason':r['reason'],'closestM':r['closestM'],'flightTimeS':r['flightTimeS'],'fuzeMissM':r.get('fuzeMissM'),'nativeTriggerTickS':r['flightTimeS']if r.get('fuzeState',{}).get('_fuzeTriggerReason')else None,'processingDelayS':delayByWeapon[c['weapon']],'nativeBurstOffsetS':r.get('fuzeState',{}).get('_fuzeBurstOffsetS'),'fragmentFlightTimeS':r.get('fuzeState',{}).get('_fuzeFragmentFlightTimeS'),'firstAllowTickS':hit['lifeS']if hit else None,'detectedAtS':si['detection'].get('detectedAtS')if si else None,'firstDraw':de[0]['detection'].get('draw')if de else None,'maxPd':max([e['detection'].get('pd',0)for e in de]+[0]),'minimumCoveredRangeM':min([e['rangeM']for e in events if e.get('beam',{}).get('covered')]+[math.inf]),'allowEvents':sum(e['allow']for e in events)}
flat=[flatten(x)for x in rows];writecsv('AB_RESULTS.csv',flat)
loss=[]
for key in S['F']['losses']:
 x=flatten(index['F',key]);x.update(cause='ENCOUNTER_DRAW_REJECTS_ALL_VALID_LOBE_SAMPLES',classification='SUPERSEDED_STOCHASTIC_CANDIDATE_REJECTED',D_effect=index['D',key]['result']['success'],DZT_effect=index['DZT',key]['result']['success'],D_reason=index['D',key]['result']['reason']);loss.append(x)
writecsv('OLD_REROLL_REGRESSIONS.csv',loss)
writecsv('OLD_REROLL_RECOVERIES.csv',[{**flatten(index['F',key]),'D_effect':index['D',key]['result']['success'],'DZT_effect':index['DZT',key]['result']['success']}for key in S['F']['gains']])
writecsv('SEED2.csv',[x for x in flat if x['navigationSeed']==2654435769])
signals=[]
for x in rows+[x for x in rev if x.get('group')=='FAST680']:
 for e in x['result'].get('diagnostic',{}).get('fuze',[]):
  q=e.get('detection')or{};b=e.get('beam')or{};signals.append({'caseId':x['id'],'group':x.get('group','PRIMARY'),'variant':x['variant'],'timeS':e['lifeS'],'rangeM':e['rangeM'],'allow':e['allow'],'reason':e.get('reason'),'beamCovered':b.get('covered'),'polarDeg':b.get('polarDeg'),**{k:q.get(k)for k in['model','draw','pd','rcsM2','closingMps','radialMps','instantSnr','peakSnr','clutterToNoise','coherence','energyBefore','energy','requiredEnergy','continuousValidS','requiredValidS','validExposureThisStepS','detectedAtS']}})
writecsv('FUZE_SIGNALS.csv.gz',signals)
fast=[x for x in rev if x.get('group')=='FAST680'];fb={x['id']:x for x in fast if x['variant']=='BASE'};S['fast680']={v:summary(v,fast,fb)for v in['BASE','F','D','DZT']}
nat0=load('natural-v1.json.gz')['rows'];nat3=load('natural.json.gz')['rows'];nat=[x for x in nat0 if x['variant']in['BASE','F','D','Z']]+nat3;nb={x['condition']['caseId']:x for x in nat if x['variant']=='BASE'};ns={}
for v in['BASE','F','D','Z','T','ZT','DZT']:
 a=[x for x in nat if x['variant']==v];ns[v]={'shots':len(a),'lethal':sum(x['result']['success']for x in a),'losses':[x['condition']['caseId']for x in a if nb[x['condition']['caseId']]['result']['success']and not x['result']['success']],'gains':[x['condition']['caseId']for x in a if not nb[x['condition']['caseId']]['result']['success']and x['result']['success']]}
S['natural']=ns;writecsv('NATURAL_RF.csv',[{**flatten(x),'lethal':x['result']['success'],'anyEffect':x['result'].get('anyEffect'),'firstTrackS':x['result'].get('firstTrackS'),'reacquired':x['result'].get('reacquired'),'scenario':x['condition']['scenario']}for x in nat])
research=[x for x in rev if x.get('group')=='RESEARCH_LOG'];S['research']=[{'variant':x['variant'],'weapon':x['condition']['weapon'],'reason':x['result']['reason'],'flightTimeS':x['result']['flightTimeS'],'closestM':x['result']['closestM'],'nativeCpa':x['result'].get('nativeCpa'),'maxDemand':x['result']['diagnostic']['maxDemand'],'phases':[{'timeS':p['lifeS'],'phase':p['phase'],'rangeM':p['rangeM']}for p in x['result']['diagnostic']['phases']]}for x in research]
tr=[]
for x in research:
 for r in x['result'].get('samples',[]):tr.append({'weapon':x['condition']['weapon'],'variant':x['variant'],**{k:v for k,v in r.items()if k!='telemetry'},**{k:r.get('telemetry',{}).get(k)for k in['pnG','zemG','zemRawG','zemCapG','commandG','availableG','achievedG','predictedCpaTimeS']}})
writecsv('HIGH_NEAR_TRAJECTORIES.csv.gz',tr)
(H/'SUMMARY.json').write_text(json.dumps(S,indent=2)+'\n')
# Standalone graphs, no game modifications.
fig,axes=plt.subplots(2,2,figsize=(11,7),constrained_layout=True)
for ax,w in zip(axes.flat,['SM2','SM2ER','SM6','ESSM']):
 for v,color in [('BASE','#777777'),('Z','#d89200'),('DZT','#008baa')]:
  x=next(x for x in research if x['variant']==v and x['condition']['weapon']==w);ss=x['result'].get('samples',[]);ax.plot([p['distanceKm']for p in ss],[p['altitudeM']/1000 for p in ss],label=v,color=color)
 ax.plot([5],[20],'rx',label='target');ax.set(title=w+' | 5km horizontal / 20km altitude',xlabel='Horizontal distance (km)',ylabel='Altitude (km)');ax.grid(alpha=.25);ax.legend(fontsize=8)
fig.savefig(P/'high_near_paths.png',dpi=145);fig.savefig(P/'high_near_paths.svg');plt.close(fig)
fig,axes=plt.subplots(3,1,figsize=(10,8),constrained_layout=True,sharex=True);key='SM2_MID_INBOUND_S1'
for v,c in [('BASE','#777'),('F','#b84848')]:
 ev=index[v,key]['result']['diagnostic']['fuze'];de=[e for e in ev if e.get('detection')];axes[0].plot([e['lifeS']for e in de],[e['detection'].get('pd')for e in de],label=v+' Pd',color=c);axes[0].plot([e['lifeS']for e in de],[e['detection'].get('draw')for e in de],'--',label=v+' draw',color=c)
ev=index['D',key]['result']['diagnostic']['fuze'];de=[e for e in ev if e.get('detection')];axes[1].semilogy([e['lifeS']for e in de],[max(1e-5,e['detection'].get('instantSnr',0))for e in de],color='#008baa');axes[1].axhline(1,color='grey',ls='--');ep=[]
for e in de:
 d=e['detection'];ep.append((d.get('intervalStartS',e['lifeS']),d.get('energyBefore',0)));
 if e['allow']:ep.append((d['detectedAtS'],d['requiredEnergy']))
 ep.append((e['lifeS'],d.get('energy',0)))
ep=sorted(ep);axes[2].plot([p[0]for p in ep],[p[1]for p in ep],label='Accumulated evidence (tick ends + acquisition)',color='#008baa');axes[2].axhline(.004,color='grey',ls='--',label='0.004 threshold');when=next(e['detection']['detectedAtS']for e in de if e['allow']);axes[2].axvline(when,color='green',ls=':',label='acquisition');axes[0].set(title='Rejected reroll example: '+key,ylabel='Legacy probability / draw');axes[0].legend(ncol=2);axes[1].set(ylabel='Deterministic SNR');axes[2].set(xlabel='Flight time (s)',ylabel='Excess-SNR seconds');axes[2].legend();[ax.grid(alpha=.2)for ax in axes];fig.savefig(P/'signal_accumulation.png',dpi=145);fig.savefig(P/'signal_accumulation.svg');plt.close(fig)
fig,axes=plt.subplots(2,1,figsize=(10,7),constrained_layout=True)
for v,c in [('BASE','#777'),('Z','#d89200'),('DZT','#008baa')]:
 x=next(x for x in research if x['variant']==v and x['condition']['weapon']=='SM6');ss=x['result'].get('samples',[]);ss=[p for p in ss if p['timeS']<35];axes[0].plot([p['timeS']for p in ss],[p['telemetry'].get('commandG')or 0 for p in ss],label=v+' demand',color=c);axes[1].plot([p['timeS']for p in ss],[p['telemetry'].get('availableG')or 0 for p in ss],label=v+' available G',color=c)
axes[0].set(title='SM-6 high-near miss: requested and physically available control',ylabel='Requested G',yscale='symlog');axes[1].set(xlabel='Flight time (s)',ylabel='Available G');[ax.legend()for ax in axes];[ax.grid(alpha=.25)for ax in axes];fig.savefig(P/'high_near_control.png',dpi=145);plt.close(fig)
print(json.dumps({'primary':{k:{j:v for j,v in x.items()if j not in ['losses','gains','reasons']}for k,x in S.items()if k in ['BASE','F','D','Z','T','ZT','DZT']},'natural':ns,'signals':len(signals)}))
