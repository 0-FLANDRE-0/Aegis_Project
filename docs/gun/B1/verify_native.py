from pathlib import Path
import sys,json,time,hashlib
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument
raw=(R/'Aegis_SIM_v48_WIP_GUN_B1.html').read_bytes();fixture=(R/'docs/map/E/test-helper.js').read_text()+'\n'+(R/'docs/map/D/extension-fixture.js').read_text()+'\n'+(H/'test-fixture.js').read_text();checks={};records={};errors=[];start=time.perf_counter()
def ck(k,v):checks[k]=bool(v);print(k,bool(v),flush=True)
E=H/'evidence/native';E.mkdir(exist_ok=True,parents=True)
with sync_playwright()as pw:
 b=launch(pw)
 for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
  p=load_fleet(b,instrument(raw,fixture),own=ship,errors=errors);p.set_default_timeout(180000);p.evaluate('__GB_TEST__.reset()');prefix=ship[:2]
  guns=p.evaluate('__GB_TEST__.guns()');ck(prefix+'.G1.module',all(g['spec']['mount']['barrelCalibers']==62 and g['spec']['fireControl']['maxRangeM']==24000 and g['spec']['ammunition']['HE_127_SIM']['muzzleVelocityMps']==823 for g in guns));ck(prefix+'.G1.magazine',all(sum(g['q']['magazine'].values())==600 and g['q']['magazine']['MFF_127_SIM']==180 for g in guns))
  rows=[]
  for alt in [10,30,500]:
   for speed in [0,280]:
    p.evaluate('__GB_TEST__.reset()');id=p.evaluate('o=>__GB_TEST__.air(o)',{'altM':alt,'speedMps':speed});q=p.evaluate('id=>__GB_TEST__.ballistic(id)',id);rows.append({'alt':alt,'speed':speed,'rows':q});ck(prefix+f'.G2.{alt}.{speed}',any(r.get('errorM',999)<.35 for r in q))
  records[prefix+'.ballistics']=rows
  p.evaluate('__GB_TEST__.reset()');id=p.evaluate('__GB_TEST__.air({rangeKm:1,altM:30000})');q=p.evaluate('id=>__GB_TEST__.solve(id)',id);ck(prefix+'.G2.elevationLimit',not any(r['q']['ok']for r in q));records[prefix+'.limit']=q
  for identity in ['FRIEND','NEUTRAL']:
   p.evaluate('__GB_TEST__.reset()');id=p.evaluate('identity=>__GB_TEST__.air({identity})',identity);q=p.evaluate('id=>__GB_TEST__.solve(id)',id);ck(prefix+'.G5.'+identity,all(not r['q']['ok']and r['q']['reason']=='PROTECTED_IDENTITY'for r in q))
  p.evaluate('__GB_TEST__.reset()');id=p.evaluate('__GB_TEST__.air({bearingDeg:90})');p.evaluate('id=>__GB_TEST__.cue(id)',id);p.evaluate('__GB_TEST__.observeTick(360)');q=p.evaluate('id=>__GB_TEST__.fire(id,true)',id);p.evaluate('__GB_TEST__.observeTick(420)');q=p.evaluate('__GB_TEST__.guns()');ck(prefix+'.G5.continuous',sum(g['q']['shotsFired']for g in q)>=2);records[prefix+'.manual']=q
  q=p.evaluate('__GB_TEST__.saveMigration()');ck(prefix+'.saveValid',q['validation']['ok']);ck(prefix+'.loadAutoDefault',q['auto']['enabled']);
  if prefix=='CG':ck(prefix+'.saveSplitNoNewAmmo',all(g['magazine']=={'HE_127_SIM':180,'SAP_127_SIM':212,'MFF_127_SIM':179}and g['shotsFired']==29 for g in q['after']['ship']['inventory']['gunMounts']))
  records[prefix+'.save']=q
  if prefix=='DD':
   q=p.evaluate('__GB_TEST__.shellProbe({distance:0})');ck('G3.safeNoTrigger',q['event']is None)
   q=p.evaluate('__GB_TEST__.shellProbe()');ck('G3.prox',q['event']['reason']=='MFF_PROXIMITY'and abs(q['event']['t']-.5)<1e-12);ck('G3.friendlySAM',p.evaluate('__GB_TEST__.shellProbe({kind:"SAM"}).event.triggerKind')=='SAM');a=p.evaluate('__GB_TEST__.shellProbe()');bb=p.evaluate('__GB_TEST__.shellProbe()');ck('G3.deterministic',a==bb)
   q=p.evaluate('__GB_TEST__.burst()');ck('G4.nativeKill',not q['alive']and q['retirement']is not None);ck('G4.shellAirburst',any(e['type']=='SHELL_AIRBURST'for e in q['events']));records['G4.burst']=q
   q=p.evaluate('__GB_TEST__.scenario({seconds:12})');records['benchmark']=q;print('BENCHMARK',json.dumps(q),flush=True)
  p.close()
 b.close()
ck('pageErrors0',not errors);out={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'sha256':hashlib.sha256(raw).hexdigest(),'elapsedS':time.perf_counter()-start};(E/'results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'pass':out['pass'],'count':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
