"""Summarize N/A/U/AU trace chronology without changing game state."""
from pathlib import Path
import csv,gzip,json,math

H=Path(__file__).resolve().parent

def load(v): return json.loads(gzip.decompress((H/f'flight-traces/{v}-primary.json.gz').read_bytes()))
def mag(x): return x.get('magnitude') if isinstance(x,dict) else None
def call(row,name):
    b=row['before'];c=b.get('calls',{}).get(name);q=b.get('last',{}).get(name)
    return q.get('value') if c and c.get('calledThisTick') and q and abs(q.get('atS',-999)-b['lifeS'])<1e-8 else None
def value(row,key):
    b=row['before'];a=b.get('arh') or {};s=b.get('selectedState') or {};bridge=call(row,'bridge') or {};kappa=call(row,'kappa') or {};aero=row.get('physical',{}).get('aero') or {}
    return {
      'rawPosErrorM':mag(a.get('rawWorldPositionErrorM')),'rawVelErrorMps':mag(a.get('rawWorldVelocityErrorMps')),
      'selectedPosErrorM':mag(s.get('relativePositionErrorM')),'selectedVelErrorMps':mag(s.get('relativeVelocityErrorMps')),
      'source':s.get('source'),'mode':a.get('mode'),'confidence':a.get('confidence'),'nis':a.get('lastNisCached'),
      'commandG':bridge.get('rawG',kappa.get('rawG')),'actualG':row.get('physical',{}).get('actualNormalG'),
      'maneuverDragN':aero.get('dragManeuverN'),'speedMps':row.get('speedMps'),'rangeM':b.get('rangeM')}

def first(rows,pred):
    for r in rows:
        v=value(r,'');
        if pred(r,v): return {'timeS':r['timeS'],**v}
    return None
def key_sample(rows,t):
    r=min(rows,key=lambda x:abs(x['timeS']-t));v=value(r,'');assoc=call(r,'association') or {};cov=call(r,'measurementCov') or {};ekf=call(r,'ekfUpdate') or {}
    sel=assoc.get('selected') or {}
    return {'timeS':r['timeS'],**v,'measurement':{k:sel.get(k) for k in ('rangeM','azRad','elRad','dopplerPathRateMps','rangeSigmaM','azSigmaDeg','elSigmaDeg','dopplerSigmaMps','snr','pd')},
      'R':cov.get('R'),'ekfAccepted':ekf.get('accepted'),'ekfBefore':(ekf.get('before') or {}).get('rawWorldVelocityErrorMps'),'ekfAfter':(ekf.get('after') or {}).get('rawWorldVelocityErrorMps')}

def summarize(v,d):
    rows=d['rows'];window=[r for r in rows if 147<=r['timeS']<=163]
    vals=[value(r,'') for r in window];dt=1/60
    sq=lambda key:math.sqrt(sum((x[key] or 0)**2 for x in vals)/max(1,sum(x[key] is not None for x in vals)))
    drag_work=sum((x['maneuverDragN'] or 0)*(x['speedMps'] or 0)*dt for x in vals)
    transitions=[];last=None
    for r in rows:
      a=(r['before'].get('arh') or {}).get('mode');s=(r['before'].get('selectedState') or {}).get('source');k=(a,s)
      if k!=last and r['timeS']>=145: transitions.append({'timeS':r['timeS'],'arhMode':a,'selectedSource':s});last=k
    thresholds={}
    for key,limits in {'rawVelErrorMps':[10,50,100],'selectedVelErrorMps':[10,50,100],'commandG':[2,3,5,10],'maneuverDragN':[50,100,500,1000]}.items():
      thresholds[key]={str(q):first(rows,lambda r,x,k=key,q=q:(r['timeS']>=145 and x[k] is not None and x[k]>=q)) for q in limits}
    result=d['result']
    return {'variant':v,'result':{k:result.get(k) for k in ('success','reason','closestM','fuzeMissM','flightTimeS','firstTrackS')},
      'finalSpeedMps':result.get('final',{}).get('speedMps'),'window147to163':{'ticks':len(window),'rawVelocityErrorRmsMps':sq('rawVelErrorMps'),'selectedVelocityErrorRmsMps':sq('selectedVelErrorMps'),'commandGRms':sq('commandG'),'maneuverDragWorkMJ':drag_work/1e6,'maxManeuverDragN':max(x['maneuverDragN'] or 0 for x in vals)},
      'thresholds':thresholds,'transitions':transitions,'keySamples':[key_sample(rows,t) for t in (147.8166666667,147.85,147.95,148.05,148.5,149.1333333333)]}

def main():
    data={v:load(v) for v in ('N','A','U','AU')};summaries=[summarize(v,data[v]) for v in data]
    # Exact first state/output divergence relative to N at matching fixed ticks.
    n=data['N']['rows'];div={}
    for v in ('A','U','AU'):
      other=data[v]['rows'];limit=min(len(n),len(other));found={}
      for field,getter in {
        'measurement':lambda r:call(r,'association'), 'ekf':lambda r:call(r,'ekfUpdate'),
        'selected':lambda r:r['before'].get('selectedState'),'control':lambda r:call(r,'bridge'),
        'physical':lambda r:r.get('afterPhysical')}.items():
        for i in range(limit):
          if getter(n[i])!=getter(other[i]):found[field]={'timeS':n[i]['timeS'],'n':getter(n[i]),'candidate':getter(other[i])};break
      div[v]=found
    analysis={'schema':'AEGIS_ARH_MEASUREMENT_FIX_A_FLIGHT_ANALYSIS_1','summaries':summaries,'firstDifferencesFromN':div,
      'notes':['PRE_DYNAMICS current-world comparison; physical output first differs after control consumption.','A/U single-shot recovery is contribution evidence, not proof of a sole cause.']}
    (H/'flight-analysis.json').write_text(json.dumps(analysis,indent=2,ensure_ascii=False)+'\n')
    with (H/'flight-timeseries.csv').open('w',newline='') as f:
      cols=['variant','timeS','rangeM','mode','source','confidence','nis','rawPosErrorM','rawVelErrorMps','selectedPosErrorM','selectedVelErrorMps','commandG','actualG','maneuverDragN','speedMps','measurementAzRad','measurementElRad','measurementAzSigmaDeg','measurementElSigmaDeg','rAz','rEl']
      w=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');w.writeheader()
      for v,d in data.items():
       for r in d['rows']:
        if not(145<=r['timeS']<=164):continue
        q=value(r,'');a=call(r,'association') or {};m=a.get('selected') or {};c=call(r,'measurementCov') or {};R=c.get('R') or []
        w.writerow({'variant':v,'timeS':r['timeS'],**q,'measurementAzRad':m.get('azRad'),'measurementElRad':m.get('elRad'),'measurementAzSigmaDeg':m.get('azSigmaDeg'),'measurementElSigmaDeg':m.get('elSigmaDeg'),'rAz':R[5] if len(R)>5 else None,'rEl':R[10] if len(R)>10 else None})
    print(json.dumps({'summaries':[{'variant':x['variant'],**x['result'],'finalSpeedMps':x['finalSpeedMps'],'window':x['window147to163']} for x in summaries],'firstDifferenceTimes':{v:{k:q['timeS'] for k,q in x.items()} for v,x in div.items()}},indent=2))

if __name__=='__main__':main()
