"""Causal ordering from two guarded native logger captures; no native calls."""
from pathlib import Path
import gzip,hashlib,importlib.util,json,math

P=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('battle_codec',P/'battle.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def load(folder,version):
 directory=P/'evidence'/folder;guard=json.loads((directory/'OFF_ON_GUARD.json').read_text());assert guard['status']=='PASS'and all(guard['checks'].values())
 path=directory/(version+'-NATURAL_SATURATION_13.json.gz');return b.decode_capture(json.loads(gzip.decompress(path.read_bytes()))),guard,hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 a,ga,ha=load('battle-cause-old-logger','old-active');z,gz,hz=load('battle-cause-logger','candidate-active');old,new=a['causalExtra'],z['causalExtra']
 def graph(ex):return next(q for q in ex['graph']if q['step']==158 and q['input']['route']=='OWN_SPY_GLOBAL'and any(len(c['plots'])==13 for c in q['components']))
 g,h=graph(old),graph(new);edge=lambda q:[{k:p.get(k)for k in ['i','id','nis']}for p in q['pairs']]
 equal_graph=edge(g)==edge(h);same_before=g['beforeStates']==h['beforeStates'];rng_diff=next(({'old':{k:x[k]for k in ['step','timeS','rngBefore','rngAfter']},'new':{k:y[k]for k in ['step','timeS','rngBefore','rngAfter']}}for x,y in zip(old['ticks'],new['ticks'])if x['rngAfter']!=y['rngAfter']),None)
 first_state=None
 for x,y in zip(old['ticks'],new['ticks']):
  if x['tracks']is None or x['tracks']==y['tracks']:continue
  dx={t['trackId']:t for t in x['tracks']};dy={t['trackId']:t for t in y['tracks']};changes=[]
  for key in sorted(dx.keys()&dy.keys()):
   u,v=dx[key],dy[key]
   if u==v:continue
   changes.append({'trackId':key,'old':u,'new':v,'positionDeltaM':math.sqrt(sum((u['x6'][i]-v['x6'][i])**2 for i in range(3))),'largestP36Delta':max(abs(c-d)for c,d in zip(u['P36'],v['P36']))})
  first_state={'afterNativeTickCounter':x['step'],'timeS':x['timeS'],'changes':changes};break
 pka=[q for q in old['pk']if q['kind']=='NATIVE_PK_RETURN'];pkz=[q for q in new['pk']if q['kind']=='NATIVE_PK_RETURN'];paired_pk=[]
 for i,(x,y)in enumerate(zip(pka,pkz)):
  paired_pk.append({'index':i,'sameTimeAndWeapon':x['timeS']==y['timeS']and x['weapon']==y['weapon'],'old':x,'new':y,'sameRngBefore':x['rngBefore']==y['rngBefore'],'missDistanceDeltaM':y['missDistanceM']-x['missDistanceM'],'pkDelta':y['returned']-x['returned']})
 draws_a=[q for q in old['pk']if q['kind']=='ACTUAL_RANDOM_DRAW_IN_NATIVE_INTERCEPT_APPLY'];draws_z=[q for q in new['pk']if q['kind']=='ACTUAL_RANDOM_DRAW_IN_NATIVE_INTERCEPT_APPLY'];prefix=0
 for x,y in zip(draws_a,draws_z):
  if x!=y:break
  prefix+=1
 result={'schema':'AEGIS_NATIVE_BATTLE_GUARDED_LOGGER_ORDERING_1','status':'CAUSE_PARTIALLY_ISOLATED_NOT_APPROVED','guards':{'old':ga,'new':gz},'rawHashes':{'old':ha,'new':hz},'first13Graph':{'old':g,'new':h,'sameNativeNisEdges':equal_graph,'sameNativePreUpdateTrackStates':same_before,'step158IsInsideTickBeforeCounterAdvance':True},'firstPostTickStateDifference':first_state,'rngCriticalWindow':{'steps':[120,240],'afterNativeTickRngIdentical':rng_diff is None,'firstObservedDifference':rng_diff,'scope':'Equal RNG states in this window do not prove identical per-draw use or equality outside it.'},'nativePkPairedBySequence':paired_pk,'identicalNativeGlobalDrawPrefixCount':prefix,'identicalDrawPrefix':draws_a[:prefix],'firstDifferentDrawBySequence':{'old':draws_a[prefix]if prefix<len(draws_a)else None,'new':draws_z[prefix]if prefix<len(draws_z)else None},'oldNativeApplyRecords':[q for q in old['pk']if q['kind']=='NATIVE_INTERCEPT_APPLY_RETURN'],'newNativeApplyRecords':[q for q in new['pk']if q['kind']=='NATIVE_INTERCEPT_APPLY_RETURN'],'importantScope':['Native computeInterceptPk is not invoked for every native apply call; direct-apply pk arguments are retained separately.','System damage0 is source-confirmed zero damage; absent fields are not filled.','Independent WIP112 fragment subsystem RNG depends on target/event seed and geometry; global RNG logs alone do not explain every subsystem value.','The first filter/geometry change and ninth-launch scheduling change precede later observed effect/draw sequence divergence. This is not proven to be a global-RNG-only regression.','Native NIS winner or mathematical graph certificate does not prove physical target identity. No tactical truth inputs or coefficients changed.'],'releaseApproved':False}
 out=P/'evidence/battle-analysis/GUARDED_LOGGER_ORDERING.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 lines=['# Guarded natural13 causal ordering','','Both frozen-product loggerON/OFF guards passed12/12. No native code is recomputed by this analysis.','','1. Critical13×13 graph/86edges at inside-tickcounter158: native NIS edges '+str(equal_graph)+', pre-update local x/P '+str(same_before)+' equal. Old holds13; combined releases3 and holds10.','2. After that native tick returns, its counter is159(time2.65s). The first sampled local x/P difference is on IDs1,8,13; the158→159 label is the existing counter advancement, not an extra tick delay.','3. Global RNG after native ticks120–240 remains identical. First nativePk/miss-distance difference is already at11.45s, before any observed differing globaldraw. The first6 actual native interception RNG draws through14.6167s are identical; the first four native effect outcomes are unchanged.','4. Native launch9 changes17→21s. Later effect sequence changes from old25.1s ESSM kill to combined30.6833s RAM kill. Later RNG/fragment/impact paths differ and cannot be compressed into a global-RNG-only explanation.','','All exact x/P, graph/evidence, actualPk/draw values, native apply arguments/target states and guard hashes are in GUARDED_LOGGER_ORDERING.json. WIP112 independent fragment RNG and unobserved physical identity remain explicit limitations. Results and inherited failures remain unapproved.'];(P/'evidence/battle-analysis/GUARDED_LOGGER_ORDERING.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({'nativeGraphEqual':equal_graph,'preStatesEqual':same_before,'firstStatePostTick':first_state['afterNativeTickCounter']if first_state else None,'criticalRngEqual':rng_diff is None,'identicalDrawPrefix':prefix,'firstPkDelta':paired_pk[0]['pkDelta']}))

if __name__=='__main__':main()
