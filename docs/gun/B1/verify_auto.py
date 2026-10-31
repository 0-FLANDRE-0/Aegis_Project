from pathlib import Path
import sys,json,time,hashlib
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument
raw=(R/'Aegis_SIM_v48_WIP_GUN_B1.html').read_bytes();fixture='\n'.join((p.read_text()for p in [R/'docs/map/E/test-helper.js',R/'docs/map/D/extension-fixture.js',H/'test-fixture.js']))
fixture+='''
__GB_TEST__.modeProbe=mode=>{__GB_TEST__.reset();engagementControlMode=mode;__GB_TEST__.air({bearingDeg:90,classification:'ASM'});gunB1SetAuto(true);gunB1AutoTick();return __GB_TEST__.guns();};
__GB_TEST__.autoprobes=()=>{const out={};__GB_TEST__.reset();const a=__GB_TEST__.air({rangeKm:3,bearingDeg:90,speedMps:100,classification:'ASM'}),b=__GB_TEST__.air({rangeKm:5,bearingDeg:90,speedMps:280,classification:'ASM'});gunB1SetAuto(true);gunB1AutoTick();out.initial=gunB1AutoSnapshot();out.a=a;out.b=b;out.guns=__GB_TEST__.guns();const first=gunB1OwnGuns()[0][1],surface=__MD_TEST__.surface({rangeKm:5,bearingDeg:90});gunB1ManualIntent(first);first.selectAmmo('HE_127_SIM');const cue=first.command(surface,'HE_127_SIM'),manual=first.startContinuousFire(surface,{mode:'MANUAL',ammoId:'HE_127_SIM'});simStepCounter+=60;gunB1AutoTick();out.manual={cue,manual,first:first.snapshot(),auto:gunB1AutoSnapshot(),other:__GB_TEST__.guns().slice(1)};first.stopContinuousFire('OPERATOR_STOP');simStepCounter+=60;for(const tr of tracks.values())tr._lastMeasurementStep=simStepCounter;gunB1AutoTick();out.resumed={first:first.snapshot(),auto:gunB1AutoSnapshot()};gunB1SetAuto(false);out.off={guns:__GB_TEST__.guns(),auto:gunB1AutoSnapshot()};if(first.restoreInventory){const q=first.snapshot();first.restoreInventory({...q,magazine:{...q.magazine,MFF_127_SIM:0}});gunB1SetAuto(true);gunB1AutoTick();out.empty={gun:first.snapshot(),auto:gunB1AutoSnapshot()};}return out;};
__GB_TEST__.fuzeMore=()=>{__GB_TEST__.reset();const out={},seed=SIM_SEED_BASE;for(const alt of [5,30,100]){let count=0;for(let i=0;i<10000;i++){SIM_SEED_BASE=41901+i;const p={id:'MK45-1',ammoId:'MFF_127_SIM',positionM:{x:0,y:0,z:alt},velocityMps:{x:600,y:0,z:0},ageS:1,flightDistanceM:1000,solutionTimeOfFlightS:100};gunB1ArmShell(p);const e=gunB1ShellEvent(p,{x:0,y:0,z:alt},{x:2400,y:0,z:alt},4);if(e?.reason==='MFF_SEA_CLUTTER')count++;}out[alt]=count;}SIM_SEED_BASE=seed;
 const p={id:'MK45-1',ammoId:'MFF_127_SIM',positionM:{x:0,y:0,z:100},velocityMps:{x:600,y:0,z:0},ageS:1,flightDistanceM:1000,solutionTimeOfFlightS:1};gunB1ArmShell(p);out.et=gunB1ShellEvent(p,{x:0,y:0,z:100},{x:600,y:0,z:100},1);return out;};
'''
errors=[];checks={};records={};start=time.perf_counter()
def ck(k,v):checks[k]=bool(v);print(k,bool(v),flush=True)
with sync_playwright()as pw:
 b=launch(pw)
 for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
  p=load_fleet(b,instrument(raw,fixture),own=ship,errors=errors);p.set_default_timeout(180000);q=p.evaluate('__GB_TEST__.autoprobes()');key=ship[:2];records[key]=q
  ck(key+'.G6.ttc',all(r['targetId']==q['b']for r in q['initial']['mounts']));ck(key+'.G6.mffNativeFeed',all(g['q']['loadedAmmoId']=='MFF_127_SIM'and g['q']['continuousFire']['active']for g in q['guns']));ck(key+'.G6.manualPriority',q['manual']['manual']['ok']and q['manual']['first']['continuousFire']['trackId']==q['manual']['cue']['trackId']);ck(key+'.G6.resume',q['resumed']['first']['continuousFire']['active']and q['resumed']['first']['loadedAmmoId']=='MFF_127_SIM');ck(key+'.G6.off',not any(g['q']['continuousFire']['active']for g in q['off']['guns']));
  if key=='CG':ck(key+'.G6.independentMounts',any(r['owned']for r in q['manual']['auto']['mounts'])and any(r['reason']=='MANUAL_PRIORITY'for r in q['manual']['auto']['mounts']));ck(key+'.G6.emptyStops',not q['empty']['gun']['continuousFire']['active']and q['empty']['auto']['mounts'][0]['reason']=='MFF_EMPTY')
  for mode in ['MANUAL','SEMIAUTO','AUTO']:
   q=p.evaluate('mode=>__GB_TEST__.modeProbe(mode)',mode);ck(key+'.G6.mode.'+mode,any(g['q']['continuousFire']['active']for g in q))
  if key=='DD':q=p.evaluate('__GB_TEST__.fuzeMore()');records['fuzeMore']=q;ck('G3.clutterAltitudeTrend',q['5']>q['30']>=q['100']);ck('G3.ET',q['et']['reason']=='MFF_ET_BACKUP'and abs(q['et']['t']-.2)<1e-12)
  p.close()
 b.close()
ck('pageErrors0',not errors);out={'checks':checks,'records':records,'errors':errors,'pass':all(checks.values()),'elapsedS':time.perf_counter()-start,'htmlSha256':hashlib.sha256(raw).hexdigest()};E=H/'evidence/auto';E.mkdir(parents=True,exist_ok=True);(E/'results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'pass':out['pass'],'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(not out['pass'])
