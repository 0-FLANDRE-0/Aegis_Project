from pathlib import Path
import sys,json,hashlib,math,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parents[4]/'map/E';R=H.parents[2];sys.path.insert(0,str(H));from verify_map_helpers import *
E=H/'evidence/d-native';E.mkdir(parents=True,exist_ok=True);raw=(R/'Aegis_SIM_v48_WIP_MAP_E.html').read_bytes();checks={};records={};errors=[];start=time.perf_counter()
def ck(k,v):checks[k]=bool(v);print(k,bool(v),flush=True)
def resetD(p):p.evaluate('__MD_TEST__.reset()');p.wait_for_timeout(320)
def selectGun(p,mode='SINGLE',ammo='HE_127_SIM'):
 p.locator('[data-weapon-b="MK45"]').click();p.locator('[data-ammo-d="'+ammo+'"]').click();p.locator('[data-gun-mode-d="'+mode+'"]').click();p.wait_for_timeout(100)
fixture=(H/'test-helper.js').read_text()+'\n'+(H/'extension-fixture.js').read_text()
with sync_playwright()as pw:
 b=launch(pw)
 p=load_fleet(b,instrument(raw,fixture),width=1400,height=900,errors=errors);p.set_default_timeout(60000)
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
