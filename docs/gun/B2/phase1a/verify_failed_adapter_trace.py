"""Read-only RNG observation of the remaining same-seed adapter failure.
No new seed, geometry, coefficient, damage draw or expected value.
"""
from pathlib import Path
import ast,hashlib,json,sys
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent;R=P.parents[3];H=R/'docs/gun/B1';sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument
source=(P/'adapted/verify_physical_adapter.py').read_text();tree=ast.parse(source);scope={'R':R,'H':H};nodes=[n for n in tree.body if isinstance(n,(ast.Assign,ast.AugAssign))and any(isinstance(x,ast.Name)and x.id=='fixture'for x in ast.walk(n.target if isinstance(n,ast.AugAssign)else n.targets[0]))]
for node in nodes:exec(compile(ast.Module(body=[node],type_ignores=[]),'B2A_SAME_FIXTURE_EXTRACT','exec'),scope)
extra='''
const b2aNativeRandom=simRandom,b2aNativeDamage=gunB1Detonate;let b2aRngEnabled=false,b2aInDamage=false,b2aDamageDraws=[];
simRandom=function(){const u=b2aNativeRandom(...arguments);if(b2aRngEnabled&&b2aInDamage)b2aDamageDraws.push(u);return u;};
gunB1Detonate=function(){const old=b2aInDamage;b2aInDamage=true;try{return b2aNativeDamage(...arguments);}finally{b2aInDamage=old;}};
window.__B2A_ADAPTER_TRACE__=enabled=>{b2aRngEnabled=enabled;b2aDamageDraws=[];const result=__GB_TEST__.harpoonProbe();return{result,rng:SIM_RNG_STATE,draws:b2aDamageDraws};};
'''
raw=(R/'Aegis_SIM_v48_WIP_GUN_B2.html').read_bytes();errors=[]
with sync_playwright()as pw:
 b=launch(pw);p=load_fleet(b,instrument(raw,scope['fixture']+extra),own='CG_52_LATE_TICONDEROGA',errors=errors);p.set_default_timeout(120000);native=p.evaluate('__B2A_ADAPTER_TRACE__(false)');traced=p.evaluate('__B2A_ADAPTER_TRACE__(true)');p.close();b.close()
prior=json.loads((P/'evidence/regression/ON/gun/B1/evidence/physical-adapter/results.json').read_text())['record'];effect=traced['result']['log'][-1]['results'][0];checks={'sameAsExistingFailure':native['result']==prior,'traceDoesNotChangeResult':native['result']==traced['result'],'traceDoesNotChangeRng':native['rng']==traced['rng'],'oneNativeDamageDraw':len(traced['draws'])==1,'actualMissDraw':len(traced['draws'])==1 and traced['draws'][0]>=effect['pk']and effect['result']=='MISS','detectorSucceeded':traced['result']['event']['reason']=='MFF_PROXIMITY','bodyBandPassed':effect['gunB2FragmentField']['ok'],'errors0':not errors};q={'pass':all(checks.values()),'checks':checks,'native':native,'traced':traced,'productHtmlSha256':hashlib.sha256(raw).hexdigest(),'inputsChanged':False,'expectedValuesChanged':False,'newSeedsTested':0,'classification':'UNCONDITIONAL_KILL_ASSERTION_NOT_MET_NATIVE_DAMAGE_MISS; retained as2nonpass assertions, not auto-approved'};(P/'evidence/failed-adapter-rng-trace.json').write_text(json.dumps(q,indent=2)+'\n');print({'checks':checks,'draws':traced['draws'],'pk':effect['pk']});raise SystemExit(not q['pass'])
