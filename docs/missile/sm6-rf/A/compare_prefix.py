"""Locate first actual difference between NATIVE and diagnostic interventions."""
from pathlib import Path
import gzip,json,hashlib
T=Path(__file__).resolve().parent;out=[]
def read(v,m):return json.load(gzip.open(T/'all-modes'/(v+'-'+m+'.json.gz')))
def at(r,name):
 b=r['before']
 if name=='physicalBefore':return b['truth']
 if name=='physicalAfter':return r['afterPhysical']
 if name=='receiverARH':return b.get('arh')
 if name=='selectedState':return b.get('selectedState')
 if name=='finalInput':return r['finalInput']
 if name=='command':
  v=(b.get('last',{}).get('bridge')or{})
  return v.get('value')if v.get('atS')==r['timeS']else None
for variant in ['DZT','HANDOFF']:
 native=read(variant,'NATIVE')
 for mode in ['IDEAL_ARH_VALUES_REAL_VALIDITY','WITHHOLD_ARH_AUTHORITY']:
  other=read(variant,mode);changes={}
  for field in ['physicalBefore','physicalAfter','receiverARH','selectedState','finalInput','command']:
   pairs=list(zip(native['rows'],other['rows']))
   assert all(abs(a['timeS']-b['timeS'])<1e-9 for a,b in pairs)
   first=next(((a,b)for a,b in pairs if at(a,field)!=at(b,field)),None)
   changes[field]=None if first is None else {'timeS':first[0]['timeS'],'native':at(first[0],field),'counterfactual':at(first[1],field)}
  out.append({'variant':variant,'mode':mode,'firstDifference':changes})
  del other
 del native
(T/'analysis/first-differences.json').write_text(json.dumps(out,indent=2)+'\n')
for r in out:print(r['variant'],r['mode'],{k:v['timeS']if v else None for k,v in r['firstDifference'].items()})
