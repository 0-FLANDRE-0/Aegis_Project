"""Attribute original EW raw-export failures without changing tests or expectations."""
from pathlib import Path
import json,re,copy
H=Path(__file__).resolve().parent;E=H/'evidence';rows=[]
def diff(a,b,p=''):
 if type(a)!=type(b):return [(p,a,b)]
 if isinstance(a,dict):return sum([diff(a.get(k,'<absent>'),b.get(k,'<absent>'),p+'/'+k)for k in sorted(set(a)|set(b))],[])
 if isinstance(a,list):
  if len(a)!=len(b):return[(p+'/length',len(a),len(b))]
  return sum([diff(x,y,p+'/'+str(i))for i,(x,y)in enumerate(zip(a,b))],[])
 return []if a==b else[(p,a,b)]
pattern=re.compile(r'^/(base|roundtrip)/(ship/inventory/gunMounts|fleet/ships/\d+/ship/inventory/guns)/\d+/(magazine/(HE_127_SIM|MFF_127_SIM)|moduleId)$')
for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
 q=json.loads((E/('regression/map/E/evidence/ew-h3/ew-'+ship+'.json')).read_text());d=diff(q['baseline'],q['candidate']);restored=copy.deepcopy(q['candidate']);authorized=True
 for path,a,b in d:
  valid=bool(pattern.fullmatch(path))and ((path.endswith('/HE_127_SIM')and (a,b)==(360,180))or(path.endswith('/MFF_127_SIM')and (a,b)==('<absent>',180))or(path.endswith('/moduleId')and(a,b)==('MK45_MOD2_MK160_SURFACE_V1','MK45_MOD4_CG52_MK160_V1')));authorized=authorized and valid;parts=path.strip('/').split('/');node=restored
  for k in parts[:-1]:node=node[int(k)]if isinstance(node,list)else node[k]
  if a=='<absent>':del node[parts[-1]]
  else:node[parts[-1]]=a
 rows.append({'ship':ship,'originalRawExact':q['same'],'originalNativeChecksPass':q['candidate']['pass']and all(q['candidate']['checks'].values()),'checks':len(q['candidate']['checks']),'differences':d,'onlyAuthorizedInventoryChanges':authorized,'allOtherRawFieldsExactAfterUndoOnCopy':restored==q['baseline'],'expectedValuesUpdated':False})
out={'pass':all(r['originalNativeChecksPass']and r['onlyAuthorizedInventoryChanges']and r['allOtherRawFieldsExactAfterUndoOnCopy']for r in rows),'rows':rows,'note':'Original raw same=false reports and assertions retained. This is a strict attribution of requested module/ammo export deltas, not a changed EW baseline or assertion normalization.'};(E/'ew-inventory-differences.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'differenceCounts':[len(r['differences'])for r in rows]}));raise SystemExit(not out['pass'])
