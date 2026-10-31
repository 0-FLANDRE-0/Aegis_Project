from pathlib import Path
import sys,json,hashlib,math,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(H));from verify_map_helpers import *
E=H/'evidence/d-native';E.mkdir(parents=True,exist_ok=True);raw=(R/'Aegis_SIM_v48_WIP_MAP_E.html').read_bytes();checks={};records={};errors=[];start=time.perf_counter()
def ck(k,v):checks[k]=bool(v);print(k,bool(v),flush=True)
def resetD(p):p.evaluate('__MD_TEST__.reset()');p.wait_for_timeout(320)
def selectGun(p,mode='SINGLE',ammo='HE_127_SIM'):
 p.locator('[data-weapon-b="MK45"]').click();p.locator('[data-ammo-d="'+ammo+'"]').click();p.locator('[data-gun-mode-d="'+mode+'"]').click();p.wait_for_timeout(100)
fixture=(H/'test-helper.js').read_text()+'\n'+(H/'extension-fixture.js').read_text()
with sync_playwright()as pw:
 b=launch(pw)
 p=load_fleet(b,instrument(raw,fixture),width=1400,height=900,errors=errors);p.set_default_timeout(60000)
 cases=[('READY',{},None),('TRACK_SUPPORT_BLOCKED',{},"__MD_TEST__.observed(id,{_wip11cObservedSeaImpact:{step:0}})"),('PROTECTED_IDENTITY',{},"__MD_TEST__.searchPoint(12000,0);__MD_TEST__.observed(id,{_operatorIdentity:'NEUTRAL',identity:'NEUTRAL',sensorDetected:false})"),('TRACK_SUPPORT_BLOCKED',{},"__MD_TEST__.observed(id,{_wip11cObservedSeaImpact:{step:0},threatStatus:'KILL_ASSESSMENT'})"),('TRACK_SUPPORT_BLOCKED',{},"__MD_TEST__.observed(id,{threatStatus:'HARMLESS'})"),('NO_TRACK',{},'missing'),('PROTECTED_IDENTITY',{},"__MD_TEST__.observed(id,{_operatorIdentity:'NEUTRAL',identity:'NEUTRAL'})"),('SURFACE_IDENTITY_NOT_AUTHORIZED',{},"__MD_TEST__.observed(id,{_operatorIdentity:'UNKNOWN',identity:'UNKNOWN'})"),('NOT_SURFACE_TRACK',{},"__MD_TEST__.observed(id,{domain:'AIR',classification:'AIR'})"),('SURFACE_TRACK_COAST_EXPIRED',{},"__MD_TEST__.observed(id,{sensorAge:11})"),('SURFACE_TRACK_NOT_CONFIRMED',{},"__MD_TEST__.observed(id,{confirmed:false})"),('SURFACE_TARGET_OUTSIDE_WEAPON_ENVELOPE',{'rangeKm':3},None),('INS_PREDICTION_BASKET_INSUFFICIENT',{'rangeKm':100},None),('TUBE_EMPTY',{},'__MD_TEST__.tubeStock(0)'),('MK141_LAUNCHER_DAMAGED',{},'__MD_TEST__.damage()'),('LAUNCHER_COOLDOWN',{},'__MD_TEST__.cooldown(1)'),('MANUAL_SURFACE_AUTHORITY_REQUIRED',{},"__MD_TEST__.mode('AUTO')"),('MANUAL_SURFACE_AUTHORITY_REQUIRED',{},"__MD_TEST__.mode('SEMIAUTO')")]
 for i,(expect,opts,patch)in enumerate(cases):
  resetD(p);tid=p.evaluate('o=>__MD_TEST__.surface(o)',opts)
  if patch=='missing':tid=999999
  elif patch:p.evaluate('id=>{'+patch+'}',tid)
  q=p.evaluate('id=>{const a=__MD_TEST__.preview(id);const b=__MD_TEST__.actualGate(id);return{a,b,same:JSON.stringify(a.q)===JSON.stringify(b)}}',tid);tag=f'gate.{i}.{expect}';ck(tag+'.pure',q['a']['same']);ck(tag+'.exact',q['same']);ck(tag+'.reason',q['a']['q']['ok']if expect=='READY'else q['a']['q']['reason']==expect);records[tag]=q
 for n in [1,2,3,4]:
  resetD(p);select(p,'HARPOON',n);tid=p.evaluate('__MD_TEST__.surface({bearingDeg:90})');q=target(p,tid);old=p.evaluate('__MD_TEST__.state()');p.locator('#mapFireB').click();queueId=p.evaluate('__MAP_D__.snapshot().queue.id');ck(f'hp{n}.queueOnly',p.evaluate('__MD_TEST__.state().harpoon.pending')is None and len(p.evaluate('__MD_TEST__.state().harpoon.launches'))==0);p.evaluate('n=>__MD_TEST__.tick(n)',n*110+20);after=p.evaluate('__MD_TEST__.state()');launch=after['harpoon']['launches'];log=p.evaluate('__MAP_D__.snapshot().log');requests=[r for r in log if r['action']=='HARPOON_REQUEST'and r['id']==queueId];ck(f'hp{n}.nativeN',len(launch)==n and sum(not t['loaded']for t in after['harpoon']['tubes'])==n);ck(f'hp{n}.uniqueAutoTubes',len({r['tubeId']for r in launch})==n);ck(f'hp{n}.delay',all((l['releaseStep']+1-r['step'])/60>=.18 for l,r in zip(launch,requests)));ck(f'hp{n}.cadence',all((bb['releaseStep']-a['releaseStep'])/60>=1.5 for a,bb in zip(launch,launch[1:])));records[f'hp{n}']={'launches':launch,'requests':requests}
 # A later native identity rejection stops remaining requests.
 resetD(p);select(p,'HARPOON',4);tid=p.evaluate('__MD_TEST__.surface({bearingDeg:90})');target(p,tid);p.locator('#mapFireB').click();p.evaluate('__MD_TEST__.tick(20)');p.evaluate("id=>__MD_TEST__.observed(id,{_operatorIdentity:'NEUTRAL',identity:'NEUTRAL'})",tid);p.evaluate('__MD_TEST__.tick(400)');s=p.evaluate('__MAP_D__.snapshot()');ck('hp.midRejectStops',len(p.evaluate('__MD_TEST__.state().harpoon.launches'))==1 and s['queue']is None and any(r['action']=='HARPOON_STOP'and r['reason']=='PROTECTED_IDENTITY'for r in s['log']));records['hp.midReject']=s['log']
 # Native gun solve/clearance across bearings, no selectedGunId changes.
 resetD(p);before=p.evaluate('__MD_TEST__.state().selectedGunId');sweep=p.evaluate('__MD_TEST__.gunSweep()');ck('cg.selectedGunUnchanged',p.evaluate('__MD_TEST__.state().selectedGunId')==before);labels={}
 for row in sweep:
  good=[r for r in row['rows']if r['result']['ok']];name='2문'if len(good)==2 else '사계 없음'if not good else'함수만'if good[0]['id']=='mk45f'else'함미만';labels.setdefault(name,row['bearing'])
 ck('cg.calmThreeCases',set(labels)=={'2문','함수만','함미만'});records['cg.sweep']=sweep;records['cg.bearings']=labels
 for label,bearing in labels.items():
  resetD(p);selectGun(p);tid=p.evaluate('b=>__MD_TEST__.surface({bearingDeg:b,rangeKm:8})',bearing);q=target(p,tid);ck('cg.label.'+label,q['model']['mountLabel']==label);records['cg.'+label]=q
 # At 25 degrees heel the native depression limit creates a genuine joint blind sector.
 resetD(p);selectGun(p);p.evaluate('__MD_TEST__.heel(25)');tid=p.evaluate('__MD_TEST__.surface({bearingDeg:270,rangeKm:8})');q=target(p,tid);ck('cg.heeledNoClearance',q['model']['mountLabel']=='사계 없음'and not q['model']['allowed']);records['cg.heeledNone']={'heelDeg':25,'bearingDeg':270,'model':q,'guns':p.evaluate('__MAP_D__.snapshot().guns')}
 # Existing gun diagnostics, using actual product functions.
 resetD(p);diag=p.evaluate('__MD_TEST__.gunDiag()');fcq=p.evaluate('__MD_TEST__.gunFcqDiag()');ck('gun.nativeDiag',diag['pass']);ck('gun.nativeFcqDiag',fcq['pass']);records['gun.diag']=diag;records['gun.fcqDiag']=fcq
 p.close()
 b.close()
ck('pageErrors0',not errors);out={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest(),'elapsedS':time.perf_counter()-start};(E/'native.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'count':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
