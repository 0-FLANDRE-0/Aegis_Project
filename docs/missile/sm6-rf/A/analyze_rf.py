"""Read-only analysis of kit outputs; no game or observer code changes."""
from pathlib import Path
import csv,gzip,json,math,hashlib,statistics
from collections import Counter
T=Path(__file__).resolve().parent;O=T/'analysis';O.mkdir(exist_ok=True)
def load(p):return json.load(gzip.open(p))
def norm(v):return math.sqrt(sum((v or{}).get(k,0)**2 for k in ['x','y','z']))
def err(v):return (v or{}).get('magnitude')
def dot(a,b):return sum(a[k]*b[k]for k in ['x','y','z'])
def fresh(b,key):return (b.get('calls',{}).get(key)or{}).get('calledThisTick',False)
def current(b,key):
 q=(b.get('last',{}).get(key)or{})
 return q.get('value')if q.get('atS')==b['lifeS']else None
def flat(r):
 b=r['before'];st=b.get('selectedState')or{};ph=r['physical'];a=ph.get('aero')or{};br=current(b,'bridge')or{};ki=current(b,'kappa')or{};pn=current(b,'pn')or{};t=b['truth'];rv=t['relativePosM'];unit={k:v/b['rangeM']for k,v in rv.items()};e=st.get('relativePositionErrorM');ev=st.get('relativeVelocityErrorMps');assoc=current(b,'association');kf=current(b,'ekfUpdate');cmd=br.get('input')or{}
 f={'timeS':r['timeS'],'rangeKm':b['rangeM']/1000,'phase':b.get('phase'),'owner':b['owner'],'source':st.get('source'),'arhMode':(b.get('arh')or{}).get('mode'),'sarhMode':(b.get('sarh')or{}).get('mode'),'positionErrorM':err(e),'velocityErrorMps':err(ev),'alongPositionErrorM':dot(e,unit)if e else None,'crossPositionErrorM':math.sqrt(max(0,err(e)**2-dot(e,unit)**2))if e else None,'selectedFresh':fresh(b,'selected'),'associationFresh':fresh(b,'association'),'ekfFresh':fresh(b,'ekfUpdate'),'ekfAccepted':kf.get('accepted')if kf else None,'associationHasMeasurement':bool(assoc.get('selected'))if assoc else None,'nisFresh':assoc.get('selectedNis')if assoc else None,'nisCached':(b.get('arh')or{}).get('lastNisCached'),'arhPositionErrorRawM':err((b.get('arh')or{}).get('rawWorldPositionErrorM')),'arhVelocityErrorRawMps':err((b.get('arh')or{}).get('rawWorldVelocityErrorMps')),'rawG':br.get('rawG'),'limitedCommandG':br.get('limitedG'),'actualNormalG':ph.get('actualNormalG'),'deliveredG':ph.get('deliveredG'),'availableG':ph.get('availableG'),'kappaFresh':fresh(b,'kappa'),'pnFresh':fresh(b,'pn'),'apnFresh':fresh(b,'apn'),'zemFresh':fresh(b,'zem'),'kappaTgoS':ki.get('tgo'),'finalYawRadS':r['finalInput']['yaw'],'finalPitchRadS':r['finalInput']['pitch'],'dragManeuverN':a.get('dragManeuverN'),'dragControlN':a.get('dragControlN'),'dragParasiteN':a.get('dragParasiteN'),'dragTotalN':a.get('dragN'),'speedBeforeMps':norm(t['ownVelMps']),'speedAfterMps':r['speedMps'],'altitudeBeforeM':t['ownPosM']['z'],'physicalLateralYM':t['ownPosM']['y'],'finYaw':ph.get('finYaw'),'finPitch':ph.get('finPitch'),'confidence':st.get('confidence'),'arhConfidence':(b.get('arh')or{}).get('confidence'),'arhHitAgeS':(b.get('arh')or{}).get('hitAgeS'),'sourceSwitchCount':(b.get('sourceArbiter')or{}).get('switchCount'),'sourceSwitchReason':(b.get('sourceArbiter')or{}).get('lastSwitchReason')}
 for k in ['x','y','z']:
  f['positionError.'+k]=e.get(k)if e else None;f['velocityError.'+k]=ev.get(k)if ev else None;f['consumedAccel.'+k]=cmd.get('a'+k);f['pnAccel.'+k]=pn.get('a'+k)
 if assoc:
  mm=assoc.get('selected')or{}
  for k in ['rangeM','azRad','elRad','dopplerPathRateMps','rangeSigmaM','azSigmaDeg','elSigmaDeg','dopplerSigmaMps','snr','pd','targetEvidence']:f['measurement.'+k]=mm.get(k)
 if kf:
  before=kf.get('before')or{};after=kf.get('after')or{}
  for prefix,s in [('kfBefore',before),('kfAfter',after)]:
   f[prefix+'.positionErrorRawM']=err(s.get('rawWorldPositionErrorM'));f[prefix+'.velocityErrorRawMps']=err(s.get('rawWorldVelocityErrorMps'));x=s.get('x')or[None]*6
   for i,n in enumerate(['x','y','z','vx','vy','vz']):f[prefix+'.'+n]=x[i]
   f[prefix+'.covarianceDiagonal']=s.get('covarianceDiagonal')
 return f
def csvwrite(name,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with gzip.open(O/name,'wt',newline='')as f:
  w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v,separators=(',',':'))if isinstance(v,(dict,list))else v for k,v in r.items()})
def change_events(rows,key):
 out=[];last=None
 for r in rows:
  if r['timeS']<135:continue
  if r[key]!=last:out.append({'timeS':r['timeS'],'rangeKm':r['rangeKm'],'value':r[key]});last=r[key]
 return out
def first(rows,predicate):return next((r for r in rows if r['timeS']>=145 and predicate(r)),None)
def compact(r):
 if r is None:return None
 keys=['timeS','rangeKm','source','arhMode','phase','owner','positionErrorM','velocityErrorMps','arhVelocityErrorRawMps','rawG','actualNormalG','dragManeuverN','speedBeforeMps','physicalLateralYM','nisFresh','ekfFresh','ekfAccepted','consumedAccel.y']
 return{k:r.get(k)for k in keys}
allRows={};summary=[];onsets={};events={};integrals=[];freshUpdates=[]
for file in sorted((T/'all-modes').glob('*.json.gz')):
 d=load(file);key=d['variant']+'/'+d['mode'];rows=[flat(r)for r in d['rows']];allRows[key]=rows
 for r in rows:r.update(variant=d['variant'],mode=d['mode'])
 summary.append({'variant':d['variant'],'mode':d['mode'],'success':d['result']['success'],'reason':d['result']['reason'],'closestRecordedM':d['result']['closestM'],'fuzeMissM':d['result']['fuzeMissM'],'flightTimeS':d['result']['flightTimeS'],'finalSpeedMps':d['result']['final']['speedMps'],'nativeEntireReturnEqual':d['nativeObserverPreservesEntireOriginalReturn'],'rows':len(rows),'htmlSha256':d['selectedHtmlSha256'],'observerSha256':d['observerSha256']})
 obs={}
 for metric,thresholds in [('arhVelocityErrorRawMps',[10,50,100]),('velocityErrorMps',[10,50,100]),('positionErrorM',[10,50,100]),('rawG',[2,3,5,10]),('actualNormalG',[2,3,5,10]),('dragManeuverN',[50,100,500,1000])]:
  for q in thresholds:obs[f'{metric}>={q}']=compact(first(rows,lambda r:r.get(metric)is not None and r[metric]>=q))
 obs['firstARHSource']=compact(first(rows,lambda r:r['source']=='ARH_RF_EKF'));obs['firstCoast']=compact(first(rows,lambda r:r['arhMode']=='COAST'))
 onsets[key]=obs;events[key]={k:change_events(rows,k)for k in ['source','arhMode','phase']}
 for lo,hi in [(147,163),(145,164)]:
  rr=[(r,x)for r,x in zip(rows,d['rows'])if lo<=r['timeS']<hi];energy=sum(r['dragManeuverN']*r['speedBeforeMps']*x['dtS']for r,x in rr)/1e6
  integrals.append({'case':key,'startS':lo,'endS':hi,'maneuverDragWorkMJ':energy,'allDragWorkMJ':sum(r['dragTotalN']*r['speedBeforeMps']*x['dtS']for r,x in rr)/1e6,'peakManeuverDragN':max(r['dragManeuverN']for r,x in rr),'peakRawG':max(r['rawG']or 0 for r,x in rr),'speedBeforeAtStartMps':rr[0][0]['speedBeforeMps'],'speedAfterAtEndMps':rr[-1][0]['speedAfterMps'],'rule':'Diagnostic integral of logged native force * pre-step speed * fixed dt. Not a new flight model or exact full energy closure.'})
 for r in rows:
  if 145<=r['timeS']<=150 and r['ekfFresh']:freshUpdates.append(r)
 csvwrite(file.name.replace('.json.gz','.csv.gz'),rows)
 del d
samples=[]
for key,rows in allRows.items():
 for t in [146.45,146.5,146.55,147,147.8,147.9,147.95,148,148.1,148.5,149,149.133333,149.5,150,155,160,163]:
  r=min(rows,key=lambda r:abs(r['timeS']-t));samples.append({'case':key,'requestedTimeS':t,**compact(r)})
csvwrite('147-163-window.csv.gz',[r for rows in allRows.values()for r in rows if 147<=r['timeS']<=163]);csvwrite('fresh-ekf-updates-145-150.csv.gz',freshUpdates)
distance=[]
for key,rows in allRows.items():
 for km in [30,25,20,18,15,12,10]:
  valid=[r for r in rows if r['timeS']>=135]
  if not min(r['rangeKm']for r in valid)<=km<=max(r['rangeKm']for r in valid):continue
  r=min(valid,key=lambda r:abs(r['rangeKm']-km));distance.append({'case':key,'requestedRangeKm':km,**compact(r),'speedBeforeMps':r['speedBeforeMps']})
phase=[]
for key,rows in allRows.items():
 for ph in sorted({r['phase']for r in rows if 147<=r['timeS']<=163}):
  rr=[r for r in rows if 147<=r['timeS']<=163 and r['phase']==ph];phase.append({'case':key,'phase':ph,'firstS':rr[0]['timeS'],'lastS':rr[-1]['timeS'],'samples':len(rr),'positionErrorRmsM':math.sqrt(statistics.mean((r['positionErrorM']or 0)**2 for r in rr)),'velocityErrorRmsMps':math.sqrt(statistics.mean((r['velocityErrorMps']or 0)**2 for r in rr)),'meanManeuverDragN':statistics.mean(r['dragManeuverN']for r in rr),'meanRawG':statistics.mean(r['rawG']or 0 for r in rr)})
repeat=[]
for variant in ['DZT','HANDOFF']:
 a=T/'native-first'/(variant+'-NATIVE.json.gz');b=T/'all-modes'/(variant+'-NATIVE.json.gz');repeat.append({'variant':variant,'gzipBytesIdentical':a.read_bytes()==b.read_bytes(),'sha256First':hashlib.sha256(a.read_bytes()).hexdigest(),'sha256Repeated':hashlib.sha256(b.read_bytes()).hexdigest()})
out={'summary':summary,'onsets':onsets,'events':events,'integrals':integrals,'sameDistanceSamples':distance,'samePhase':phase,'fixedTimeSamples':samples,'nativeRepeat':repeat,'thresholdPolicy':'Illustrative multiple thresholds fixed for diagnosis, no production tuning; same-tick sequence additionally checked against source call order.'}
(O/'analysis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,indent=2));print('native repeat',repeat)

import os
os.environ['MPLCONFIGDIR']='/tmp/aegis-sm6-rf-matplotlib'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=O/'plots';P.mkdir(exist_ok=True)
fig,axs=plt.subplots(5,1,figsize=(11,12),sharex=True)
for variant,color in [('DZT','#7b60af'),('HANDOFF','#bd4f39')]:
 rows=[r for r in allRows[variant+'/NATIVE']if 145<=r['timeS']<=164];ts=[r['timeS']for r in rows]
 for ax,key,label in zip(axs,['velocityErrorMps','positionErrorM','rawG','dragManeuverN','speedBeforeMps'],['Selected velocity error (m/s)','Selected relative position error (m)','Raw commanded G','Native maneuver drag (N)','Physical speed (m/s)']):
  ax.plot(ts,[r[key]for r in rows],label=variant,color=color);ax.set_ylabel(label,fontsize=9);ax.grid(alpha=.25)
 for ax in axs:
  ax.axvline(onsets[variant+'/NATIVE']['firstARHSource']['timeS'],color=color,ls='--',alpha=.6);ax.axvline(onsets[variant+'/NATIVE']['firstCoast']['timeS'],color=color,ls=':',alpha=.5)
axs[0].legend();axs[-1].set_xlabel('Missile life (s), PRE_DYNAMICS estimates / native same-step force')
fig.suptitle('NATIVE chronology: dashed = ARH source adoption; dotted = first COAST')
fig.tight_layout()
for ext in ['png','svg']:fig.savefig(P/('native-order.'+ext),dpi=145)
plt.close(fig)
fig,axs=plt.subplots(3,1,figsize=(11,9),sharex=True)
for mode,color in [('NATIVE','#bd4f39'),('IDEAL_ARH_VALUES_REAL_VALIDITY','#328b70'),('WITHHOLD_ARH_AUTHORITY','#4a74ae')]:
 rows=[r for r in allRows['HANDOFF/'+mode]if 145<=r['timeS']<=164];ts=[r['timeS']for r in rows]
 for ax,key,label in zip(axs,['rawG','dragManeuverN','speedBeforeMps'],['Raw commanded G','Native maneuver drag (N)','Physical speed (m/s)']):ax.plot(ts,[r[key]for r in rows],label=mode,color=color);ax.set_ylabel(label);ax.grid(alpha=.25)
axs[0].legend(fontsize=8);axs[-1].set_xlabel('Missile life (s)');fig.suptitle('HANDOFF diagnostic counterfactuals (not product changes)');fig.tight_layout()
for ext in ['png','svg']:fig.savefig(P/('handoff-counterfactuals.'+ext),dpi=145)
plt.close(fig)
