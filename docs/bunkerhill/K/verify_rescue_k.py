"""Actual abandonment UI, spatial escape, raft manifests and atomic save import."""
from pathlib import Path
import argparse,json,hashlib,math
from playwright.sync_api import sync_playwright
from browser_i import launch,load,served_bytes
p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('baseline_j');p.add_argument('out');a=p.parse_args()
out=Path(a.out);out.mkdir(parents=True,exist_ok=True);checks={};details={};errors=[]
observe="""()=>{const d=window.__NAVAL_SIM_DIAG__,r=window.__AEGIS_ACTIVE_SHIP_RUNTIME__,c=r.crew.snapshot();return {crew:{mode:c.mode,total:c.total,fit:c.fit,injured:c.injured,dead:c.dead,evacuated:c.evacuated,evacuatedIds:c.groups.filter(g=>g.evacuated===1).map(g=>g.id),blocked:c.groups.filter(g=>g.routeBlocked).length},rescue:d.rescueSnapshotK(),summary:d.rescueSummaryK(),valid:d.validateOperationalStateV48Wip11B(d.exportOperationalStateV48Wip11A())};}"""
def conserved(q):
    c=q['crew'];rafts=q['rescue']['rafts'];ids=[n for r in rafts for n in r['personIds']]
    return len(ids)==len(set(ids))==c['evacuated'] and sorted(ids)==sorted(c['evacuatedIds']) and c['fit']+c['injured']+c['dead']+c['evacuated']==c['total'] and all(0<len(r['personIds'])<=25 for r in rafts) and q['valid']['ok']
with sync_playwright()as pw:
 b=launch(pw)
 def fresh(ship='CG_52_LATE_TICONDEROGA'):
    page=load(b,served_bytes(a.html),ship=ship,errors=errors)
    page.evaluate("""()=>{const d=window.__NAVAL_SIM_DIAG__,w=window.__AEGIS_ENGAGEMENT_RUNTIME__;d._resetShipTest();w.world.entities.aircraft.length=0;w.world.entities.surfaceContacts.length=0;d.setEmcon(true);d.wip13a3SetManualWeather({hsM:0,windSpeedMps:6,windDirectionDeg:20});d.stepTicks(1);}""")
    page.locator('#damageControlToggleV1').click();page.locator('#crewAbandonV21').evaluate('(e)=>{for(let p=e.parentElement;p;p=p.parentElement)if(p.tagName==="DETAILS")p.open=true;}')
    return page
 def abandon(page):
    page.once('dialog',lambda d:d.accept());page.locator('#crewAbandonV21').click()
 def finish(page,limit=240):
    hist=[]
    for t in range(10,limit+1,10):
      page.evaluate('window.__NAVAL_SIM_DIAG__.stepTicks(600)');q=page.evaluate(observe);hist.append(q)
      if q['crew']['fit']+q['crew']['injured']==0:break
    return hist
 page=fresh();checks['coreZero']=page.evaluate('window.__CORE_SELFTEST_FAILURES__')==[]
 checks['moduleTransitions']=page.evaluate('window.__NAVAL_SIM_DIAG__.rescueModuleAuditK().pass')
 checks['initialNoRafts']=page.evaluate('window.__NAVAL_SIM_DIAG__.rescueSummaryK().rafts')==0
 page.once('dialog',lambda d:d.dismiss());page.locator('#crewAbandonV21').click();checks['cancelInert']=page.evaluate("window.__AEGIS_ACTIVE_SHIP_RUNTIME__.crew.snapshot().mode==='OPERATIONAL'&&window.__NAVAL_SIM_DIAG__.rescueSummaryK().rafts===0")
 abandon(page);checks['noInstantRosterTeleport']=page.evaluate("window.__AEGIS_ACTIVE_SHIP_RUNTIME__.crew.snapshot().evacuated===0&&window.__NAVAL_SIM_DIAG__.rescueSummaryK().rafts===0")
 history=[];mid=None
 for t in range(10,241,10):
    page.evaluate('window.__NAVAL_SIM_DIAG__.stepTicks(600)');q=page.evaluate(observe);history.append(q)
    if t==50:mid=page.evaluate('window.__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A()')
    if q['crew']['fit']+q['crew']['injured']==0:break
 end=history[-1];details['cg52History']=history
 checks['allSamplesConservePeople']=all(conserved(q)for q in history)
 checks['progressiveActualRoutes']=history[0]['crew']['evacuated']<330 and len({q['summary']['rafts']for q in history})>=8
 checks['cg52FullRoster14Rafts']=end['crew']['evacuated']==330 and end['summary']==dict(rafts=14,afloat=14,boarding=0,persons=330,capacityPersons=25,maxRafts=14)
 rafts=end['rescue']['rafts'];checks['capacityAndLastFive']=all(len(q['personIds'])==25 for q in rafts[:-1]) and len(rafts[-1]['personIds'])==5
 checks['bothSidesAndCadence']=all(q['stationIndex']==i%2 for i,q in enumerate(rafts)) and all(rafts[i]['bornAtS']-rafts[i-1]['bornAtS']>=4-1e-8 for i in range(1,len(rafts)))
 first=history[3]['rescue']['rafts'][0];last=rafts[0];checks['freeSeaDrift']=math.hypot(first['positionM']['x']-last['positionM']['x'],first['positionM']['y']-last['positionM']['y'])>5
 checks['inflatedRaftsDoNotOverlap']=min(math.hypot(a['positionM']['x']-b['positionM']['x'],a['positionM']['y']-b['positionM']['y'])for i,a in enumerate(rafts)for b in rafts[i+1:])>=5.8
 checks['worldOwnership']=page.evaluate("(()=>{const r=window.__AEGIS_ACTIVE_SHIP_RUNTIME__,w=window.__AEGIS_ENGAGEMENT_RUNTIME__;return !!r.rescue&&w.world.entities.lifeRafts.every(q=>q.worldEntityClass==='SURVIVAL_RAFT'&&q.ownerEntityId===r.entityId)&&!('lifeRafts'in r)})()")
 checks['noThreatFiles']=page.evaluate('window.__AEGIS_ACTIVE_SHIP_RUNTIME__.combatSystem.trackManager.tracks.size===0')
 before=page.evaluate('window.__NAVAL_SIM_DIAG__.rescueSnapshotK()');checks['repeatUiDisabled']=page.locator('#crewAbandonV21').is_disabled();checks['repeatCommandNoDuplicate']=page.evaluate('window.__AEGIS_ACTIVE_SHIP_RUNTIME__.crew.abandon()')is False and before==page.evaluate('window.__NAVAL_SIM_DIAG__.rescueSnapshotK()')
 checks['uiCounts']=all(s in page.locator('#crewTotalsV21').inner_text()for s in ['14척','330명','25명'])
 detached=page.evaluate("""()=>{const d=window.__NAVAL_SIM_DIAG__,s=d.exportOperationalStateV48Wip11A(),before=JSON.stringify(d.rescueSnapshotK());s.ship.rescue.rafts[0].personIds.length=0;s.ship.rescue.rafts[0].positionM.x=9e9;return before===JSON.stringify(d.rescueSnapshotK());}""");checks['exportDetached']=detached
 page.screenshot(path=str(out/'cg52-evacuated-ui.png'));page.close()
 Path(out/'mid-abandonment-save.json').write_text(json.dumps(mid,ensure_ascii=False,indent=2)+'\n')
 page=fresh();restored=page.evaluate("""s=>{const d=window.__NAVAL_SIM_DIAG__,r=window.__AEGIS_ACTIVE_SHIP_RUNTIME__,w=window.__AEGIS_ENGAGEMENT_RUNTIME__,refs={r,crew:r.crew,rescue:r.rescue,rafts:w.world.entities.lifeRafts};d.importOperationalStateV48Wip11B(s);return {exact:JSON.stringify(d.rescueSnapshotK())===JSON.stringify(s.ship.rescue),refs:r===refs.r&&r.crew===refs.crew&&r.rescue===refs.rescue&&w.world.entities.lifeRafts===refs.rafts};}""",mid)
 checks['midRestoreExact']=restored['exact']and restored['refs'];resumed=finish(page);details['resumedHistory']=resumed
 checks['abandonmentResumesAfterImport']=resumed[-1]['crew']['evacuated']==330 and resumed[-1]['summary']['rafts']==14 and all(conserved(q)for q in resumed)
 invalid=page.evaluate("""()=>{const d=window.__NAVAL_SIM_DIAG__,valid=d.exportOperationalStateV48Wip11A(),rows=[];const edits=[['duplicatePerson',s=>s.ship.rescue.rafts[1].personIds[0]=s.ship.rescue.rafts[0].personIds[0]],['missingPerson',s=>s.ship.rescue.rafts[0].personIds.pop()],['wrongOwner',s=>s.ship.rescue.rafts[0].ownerEntityId='OTHER'],['badCapacity',s=>s.ship.rescue.capacityPersons=20],['oversize',s=>s.ship.rescue.rafts[0].personIds.push(330)],['badPosition',s=>s.ship.rescue.rafts[0].positionM.x=NaN],['badSerial',s=>s.ship.rescue.serial++],['badLaunchTime',s=>s.ship.rescue.lastLaunchTimeS=1e8],['missingCapabilityPayload',s=>delete s.ship.rescue],['deadOccupant',s=>{const id=s.ship.rescue.rafts[0].personIds[0],g=s.ship.crew.groups.find(q=>q.id===id);g.evacuated=0;g.dead=1;}]];for(const [name,edit]of edits){const s=structuredClone(valid);edit(s);const before=JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());let rejected=false;try{d.importOperationalStateV48Wip11B(s);}catch(_){rejected=true;}rows.push({name,rejected,unchanged:before===JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B())});}return rows;}""")
 details['invalidImports']=invalid;checks['tenInvalidImportsZeroMutation']=all(q['rejected']and q['unchanged']for q in invalid)
 page.evaluate('window.__NAVAL_SIM_DIAG__.importOperationalStateV48Wip11B('+json.dumps(mid)+')')
 sink=page.evaluate("""()=>{const r=window.__AEGIS_ACTIVE_SHIP_RUNTIME__,d=window.__NAVAL_SIM_DIAG__,before=d.rescueSnapshotK();r.crew.step(1,[],[],{lost:true});r.rescue.step(1/60,r.crew.snapshot());const c=r.crew.snapshot();return {before,after:d.rescueSnapshotK(),crew:{mode:c.mode,dead:c.dead,evacuated:c.evacuated,total:c.total},valid:d.validateOperationalStateV48Wip11B(d.exportOperationalStateV48Wip11A())};}""")
 details['sink']=sink;checks['survivorsPersistAfterLoss']=sink['crew']['mode']=='LOST' and sink['crew']['dead']+sink['crew']['evacuated']==330 and sink['crew']['evacuated']==sum(len(q['personIds'])for q in sink['after']['rafts']) and all(q['phase']=='AFLOAT'for q in sink['after']['rafts']) and sink['valid']['ok']
 page.evaluate('window.__NAVAL_SIM_DIAG__.resetEntireSessionV48Wip11A()');checks['wholeResetClearsRafts']=page.evaluate('window.__NAVAL_SIM_DIAG__.rescueSummaryK().rafts===0&&window.__AEGIS_ACTIVE_SHIP_RUNTIME__.crew.snapshot().evacuated===0');page.close()
 page=fresh();casualty=page.evaluate("""()=>{const d=window.__NAVAL_SIM_DIAG__,s=d.exportOperationalStateV48Wip11A();for(let i=0;i<45;i++){const g=s.ship.crew.groups[i];g.fit=0;g.teamId=null;if(i<25)g.dead=1;else{g.injured=1;g.triage='MINOR';g.mobility01=.68;g.underCare=false;}}d.importOperationalStateV48Wip11B(s);return window.__AEGIS_ACTIVE_SHIP_RUNTIME__.crew.snapshot().dead;}""")
 abandon(page);casualtyHistory=finish(page);details['casualtyHistory']=casualtyHistory;q=casualtyHistory[-1];checks['deadExcludedInjuredEvacuate']=casualty==25 and q['crew']['dead']==25 and q['crew']['evacuated']==305 and q['summary']['rafts']==13 and all(conserved(r)for r in casualtyHistory);page.close()
 page=fresh('DDG_119_LATE_FLIGHT_IIA');abandon(page);ddg=finish(page);details['ddgHistory']=ddg;q=ddg[-1];checks['ddgShared310Persons13Rafts']=q['crew']['evacuated']==310 and q['summary']['rafts']==13 and q['summary']['afloat']==13 and len(q['rescue']['rafts'][-1]['personIds'])==10 and all(conserved(r)for r in ddg);page.close()
 old=load(b,served_bytes(a.baseline_j),errors=errors);legacy=old.evaluate('window.__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A()');old.close();page=fresh()
 migration=page.evaluate("""s=>{const d=window.__NAVAL_SIM_DIAG__,before=JSON.stringify(s),validation=d.validateOperationalStateV48Wip11B(s),unchanged=before===JSON.stringify(s);d.importOperationalStateV48Wip11B(s);return {validation,unchanged,rescue:d.rescueSummaryK()};}""",legacy)
 details['jMigration']=migration;checks['legacyJCompatibleDetachedMigration']=migration['validation']['ok'] and migration['unchanged'] and migration['rescue']['rafts']==0 and any(q['schema']=='AEGIS_LEGACY_RESCUE_MIGRATION_K_1'for q in migration['validation'].get('migrations',[]))
 # Historical evacuated people had no world raft positions. Require an explicit migration.
 legacy2=json.loads(json.dumps(legacy));legacy2['ship']['crew']['mode']='ABANDONED'
 for g in legacy2['ship']['crew']['groups'][:31]:g.update(fit=0,injured=0,dead=0,evacuated=1)
 oldSurvivors=page.evaluate("""s=>{const d=window.__NAVAL_SIM_DIAG__,v=d.validateOperationalStateV48Wip11B(s);d.importOperationalStateV48Wip11B(s);return {validation:v,rescue:d.rescueSummaryK(),rafts:d.rescueSnapshotK().rafts};}""",legacy2)
 details['legacySurvivors']=oldSurvivors;checks['legacy31SurvivorsReconstructedOnce']=oldSurvivors['validation']['ok']and oldSurvivors['rescue']['persons']==31 and oldSurvivors['rescue']['rafts']==2 and all(q['phase']=='AFLOAT'for q in oldSurvivors['rafts']);page.close()
 b.close()
checks['pageErrorsZero']=not errors
result={'schema':'AEGIS_RESCUE_BROWSER_K_1','html':Path(a.html).name,'sha256':hashlib.sha256(Path(a.html).read_bytes()).hexdigest(),'capacitySource':'US_NAVY_DVIDS_5627398','fixedTickHz':60,'checks':checks,'details':details,'errors':errors,'pass':all(checks.values())}
(out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'errors':errors,'pass':result['pass']},ensure_ascii=False),flush=True)
if not result['pass']:raise SystemExit(1)
