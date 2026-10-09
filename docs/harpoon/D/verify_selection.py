"""Real ARM input and observed tracks: selection, fallback, pinned release, saves and DDG."""
import argparse,base64,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parents[1]/'bunkerhill/K'))
from browser_i import launch,load
ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('out');a=ap.parse_args()
source=Path(a.html);body=source.read_bytes();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
checks={};details={};errors=[];console=[]
def check(k,v):checks[k]=bool(v)
def setup(p,bearing=0):
 return p.evaluate('''bearing=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;
  d.setEmcon(false);d.createWip13aSurfaceTargetFixture({rangeKm:8,bearingDeg:bearing,headingDeg:90,speedKt:0});
  const t=d.wip13b9StepSurfaceSensors(1200).audit.surfaceTracks.find(t=>t.confirmed);
  if(!t)throw Error('NO_OBSERVED_TRACK');d.a3SetOperatorIdentity(t.trackId,'TRAINING_TARGET');h.select(t.trackId);
  return {trackId:t.trackId,gate:h.autoTube(),audit:h.selectionAudit()};}''',bearing)
with sync_playwright()as pw:
 b=launch(pw);p=load(b,body,errors=errors);p.on('console',lambda m:console.append(m.text)if m.type=='error'else None)
 s=setup(p);details['initial']=s
 check('startupAndSelectionSelfTestsPass',p.evaluate('window.__CORE_SELFTEST_FAILURES__')==[]and s['audit']['pass'])
 p.locator('#modeAimBtn').click()
 if p.locator('#armSubVlsBtn').is_visible():p.locator('#armSubVlsBtn').click()
 check('autoLabelReplacesIndividualDropdown',p.locator('#harpoonTubeA').evaluate('(e)=>e.tagName')=='SPAN'and p.locator('#harpoonTubeA').inner_text().startswith('AUTO · '))
 idle=p.evaluate('''()=>{const h=window.__HARPOON_DIAG_A__,before=h.snapshot();for(let i=0;i<10;i++)h.refreshUi();h.focusedTicks(100);return {before,after:h.snapshot()};}''')
 check('selectionAndTimeNeverFireByThemselves',not idle['after']['missiles']and idle['after']['pending']is None and idle['before']['inventory']['tubes']==idle['after']['inventory']['tubes'])
 check('selectionDoesNotConsumeCombatRng',idle['before']['rng']==idle['after']['rng'])
 blocked=p.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__,id=h.autoTube().trackId,rows={};
  for(const identity of ['UNKNOWN','FRIEND','NEUTRAL']){d.a3SetOperatorIdentity(id,identity);rows[identity]=h.fire(id);}
  d.a3SetOperatorIdentity(id,'TRAINING_TARGET');rows.AUTO=h.autoTube(id,{automatic:true});rows.SEMIAUTO=h.autoTube(id,{mode:'SEMIAUTO'});h.refreshUi();return {rows,state:h.snapshot()};}''')
 details['authority']=blocked
 check('protectedIdentitiesStillCannotRelease',all(not blocked['rows'][k]['ok']for k in ['UNKNOWN','FRIEND','NEUTRAL'])and not blocked['state']['missiles'])
 check('automaticFireAuthorityStillDenied',all(blocked['rows'][k]['reason']=='MANUAL_SURFACE_AUTHORITY_REQUIRED'for k in ['AUTO','SEMIAUTO']))
 before=p.evaluate('window.__NAVAL_SIM_DIAG__.shipMassLedger().massKg');requests=[];releases=[];cooldowns=[]
 ids=p.evaluate('window.__HARPOON_DIAG_A__.snapshot().inventory.tubes.map(t=>t.id)')
 for i in range(8):
  p.evaluate('window.__HARPOON_DIAG_A__.refreshUi()');gate=p.evaluate('window.__HARPOON_DIAG_A__.autoTube()');label=p.locator('#harpoonTubeA').inner_text()
  assert gate['ok'],gate
  p.locator('#harpoonFireA').click();pending=p.evaluate('window.__HARPOON_DIAG_A__.snapshot().pending');requests.append({'gate':gate,'label':label,'pending':pending})
  p.evaluate('window.__HARPOON_DIAG_A__.fixedTicks(12)');state=p.evaluate('window.__HARPOON_DIAG_A__.snapshot()');releases.append(state['missiles'][-1]['tubeId'])
  p.evaluate('window.__HARPOON_DIAG_A__.refreshUi()');cooldowns.append(p.locator('#harpoonFireA').is_disabled())
  p.evaluate('window.__HARPOON_DIAG_A__.fixedTicks(91)')
  print(json.dumps({'stage':'button-release','number':i+1,'tube':releases[-1]}),flush=True)
 p.evaluate('window.__HARPOON_DIAG_A__.refreshUi()');ended=p.evaluate('window.__HARPOON_DIAG_A__.snapshot()');removed=before-p.evaluate('window.__NAVAL_SIM_DIAG__.shipMassLedger().massKg')
 details['eightAutomaticSelections']={'requests':requests,'releaseTubes':releases,'inventory':ended['inventory'],'massRemovedKg':removed}
 check('eightRealButtonPressesReleaseEightDifferentTubes',len(ended['missiles'])==8 and len(set(releases))==8 and set(releases)==set(ids))
 check('displayedAndPinnedTubeMatchesActualRelease',all(q['gate']['tubeId']==q['pending']['tubeId']==tube and tube.replace('MK141-','')in q['label']for q,tube in zip(requests,releases)))
 check('preferredBankAutomaticallyFallsBackWhenEmpty',len({q.rsplit('-',1)[1][0]for q in releases[:4]})==1 and releases[3].rsplit('-',1)[1][0]!=releases[4].rsplit('-',1)[1][0])
 check('tubeInventoryNeverCompactsOrDuplicates',[t['id']for t in ended['inventory']['tubes']]==ids and all(not t['loaded']for t in ended['inventory']['tubes']))
 check('eachRoundRemovesExactly690kg',abs(removed-8*690)<1e-6)
 check('cooldownIsStillEnforced',all(cooldowns))
 check('emptyLauncherClearlyDisablesFire',p.locator('#harpoonFireA').is_disabled()and p.locator('#harpoonTubeA').inner_text()=='AUTO · 소진'and p.evaluate('window.__HARPOON_DIAG_A__.fire().reason')=='TUBE_EMPTY')
 saved=p.evaluate('window.__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A()')
 p.evaluate('window.__NAVAL_SIM_DIAG__.resetEntireSessionV48Wip11A();window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)')
 check('fullResetRestoresEightFixedLoadedSlots',p.evaluate('window.__HARPOON_DIAG_A__.snapshot().inventory.tubes.every(t=>t.loaded)'))
 restored=p.evaluate('''saved=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;d.importOperationalStateV48Wip11B(saved);h.refreshUi();return h.snapshot();}''',saved)
 check('oldInventorySchemaRoundTripsEmptyState',restored['inventory']['schema']=='MK141_INVENTORY_A1'and all(not t['loaded']for t in restored['inventory']['tubes'])and not restored['missiles']and restored['pending']is None)
 # New physical contacts, not direct edits to their truth position or track estimate.
 p.close();p=load(b,body,errors=errors);s=setup(p,180);details['oppositeBearing']=s
 check('oppositeObservedBearingSelectsOppositeBank',s['gate']['tubeId'].rsplit('-',1)[1][0]!=releases[0].rsplit('-',1)[1][0])
 damage=p.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__,initial=h.autoTube(),bank=initial.tubeId.split('-')[1][0];
  d.wip101SetModuleDamage('Mk 141('+bank+')',100);const fallback=h.autoTube();
  const request=h.fire();d.wip101SetModuleDamage('Mk 141('+fallback.tubeId.split('-')[1][0]+')',100);h.focusedTicks(12);
  const cancelled=h.snapshot();h.refreshUi();const blocked=h.autoTube();
  d.wip101SetModuleDamage('Mk 141(A)',0);d.wip101SetModuleDamage('Mk 141(B)',0);h.refreshUi();
  return {initial,fallback,request,cancelled,blocked,recovered:h.autoTube()};}''')
 details['damage']=damage
 check('damagedPreferredBankFallsBackToOtherLoadedBank',damage['fallback']['ok']and damage['initial']['tubeId'].split('-')[1][0]!=damage['fallback']['tubeId'].split('-')[1][0])
 check('damageAfterDoorOpeningCancelsPinnedTubeWithoutAmmoLoss',damage['request']['ok']and not damage['cancelled']['missiles']and all(t['loaded']for t in damage['cancelled']['inventory']['tubes']))
 check('allBanksDamagedBlocksAndRepairRestoresSelection',damage['blocked']['reason']=='MK141_LAUNCHER_DAMAGED'and damage['recovered']['ok'])
 pin=p.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__,id=h.autoTube().trackId,request=h.fire();
  h.select(999999);h.refreshUi();const during={gate:h.autoTube(),pending:h.snapshot().pending,label:document.getElementById('harpoonTubeA').textContent};
  h.focusedTicks(12);const released=h.snapshot();h.select(id);return {request,during,released};}''')
 details['pinnedRequest']=pin
 check('selectionChangesDoNotRetargetPendingDoorOrRelease',pin['during']['pending']['tubeId']==pin['request']['tubeId']==pin['during']['gate']['tubeId']==pin['released']['missiles'][0]['tubeId']and pin['released']['missiles'][0]['memory']['trackId']==pin['request'].get('trackId',s['trackId']))
 # Saved historical selection is accepted but does not override the new live auto policy.
 restore=p.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__,saved=d.exportOperationalStateV48Wip11A();
  const empty=saved.ship.inventory.harpoon.tubes.find(t=>!t.loaded);saved.ship.inventory.harpoon.selectedTubeId=empty.id;
  d.importOperationalStateV48Wip11B(saved);return {inventory:h.snapshot().inventory,empty:empty.id};}''')
 t=setup(p,180);req=p.evaluate('window.__HARPOON_DIAG_A__.fire()')
 check('staleSavedEmptySelectionCannotForceEmptyTube',req['ok']and req['tubeId']!=restore['empty'])
 dpage=load(b,body,ship='DDG_119_LATE_FLIGHT_IIA',errors=errors)
 ddg=dpage.evaluate('''()=>({inventory:window.__HARPOON_DIAG_A__.snapshot().inventory,gate:window.__HARPOON_DIAG_A__.autoTube(),hidden:document.getElementById('harpoonControlsA').hidden,core:window.__CORE_SELFTEST_FAILURES__})''');details['ddg']=ddg
 check('ddg119RetainsNoHarpoonInstallation',not ddg['inventory']['tubes']and ddg['hidden']and ddg['gate']['reason']=='MK141_NOT_INSTALLED'and ddg['core']==[])
 b.close()
check('pageErrorsZero',not errors);check('consoleErrorsZero',not console)
report={'schema':'HARPOON_D_SELECTION_VERIFICATION','source':source.name,'sha256':hashlib.sha256(body).hexdigest(),'seed':'0x6d2b79f5','clock':'FULL_FIXED_TICK_EIGHT_BUTTON_RELEASES_PLUS_FOCUSED_GATE_FIXTURES','checks':checks,'details':details,'errors':errors,'console':console,'pass':all(checks.values())}
(out/'selection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'pass':report['pass'],'errors':errors,'console':console},ensure_ascii=False));raise SystemExit(0 if report['pass']else 1)
