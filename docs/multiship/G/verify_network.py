"""Native controls, actual delayed link, strict reports, group fallback and saves.

Synthetic reports are explicit DIAGNOSTIC_ONLY measurement fixtures. Natural
radar sharing and real releases are verified separately.
"""
import argparse,hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_g import launch,load_fleet
FIXTURE=r'''()=>{
 const d=window.__NAVAL_SIM_DIAG__,w=window.__AEGIS_ENGAGEMENT_RUNTIME__,aid='SHIP_SCENARIO_ALLY_F',eid='SHIP_SCENARIO_ENEMY_A',checks={},trace={};let own=w.ships.get(w.activePlayerShipId),ally=w.ships.get(aid),enemy=w.ships.get(eid);
 const tick=n=>d.runFramesToTicks(60,1,n),save=()=>d.exportOperationalStateV48Wip11A(),stable=q=>JSON.stringify(q,(k,v)=>k==='performance'?undefined:v),snap=()=>d.networkSnapshotG(),state=id=>snap().ships.find(q=>q.entityId===id),now=()=>d.observerSnapshotC().worldTimeS;
 d.setTerrainDiagBypass(true);d.wip119SetMode('MANUAL');d.defenseCommandE(aid,{mode:'HOLD'});d.defenseCommandE(eid,{mode:'HOLD'});const initial=save();
 checks.friendlyMembersOnly=snap().ships.length===2&&!snap().ships.some(q=>q.entityId===eid);checks.ownerLocalState=own.combatSystem.networkG!==ally.combatSystem.networkG&&own.combatSystem.networkG.files!==ally.combatSystem.networkG.files;
 checks.enemyCannotJoin=d.networkCommandG(eid,{enabled:true}).reason==='AUTHENTICATED_ALLY_REQUIRED';checks.noOrdnanceDl=!snap().ordnanceDatalink&&!snap().remoteFireControl;
 d.importOperationalStateV48Wip11A(initial);own=w.ships.get(w.activePlayerShipId);ally=w.ships.get(aid);enemy=w.ships.get(eid);tick((30-Math.round(now()*60)%30)%30+1);checks.delayedQueue=state(own.entityId).queued===1&&state(own.entityId).peers.every(p=>!p.connected);tick(16);checks.noEarlyDelivery=state(own.entityId).picture.length===0;tick(2);checks.actualHeartbeat=state(own.entityId).peers.some(p=>p.entityId===aid&&p.connected)&&state(aid).peers.some(p=>p.connected);
 checks.authenticatedSelfReport=state(own.entityId).picture.some(q=>q.identity==='FRIEND'&&q.sources.some(s=>s.kind==='SELF'));trace.handshake=snap();
 const P=Array(36).fill(0);for(let i=0;i<6;i++)P[i*6+i]=i<3?1600:9;
 const pos=own.navigation.positionWorld,report={fileId:201,kind:'TRACK',measuredAtS:now(),stateAtS:now(),stateM:[pos.x/.0038+22000,pos.y/.0038+4000,40,-220,0,0],covariance:P,domain:'AIR',classification:'ASM',identity:'HOSTILE',assessment:'THREAT',bid:{eligible:false,cost:1e6,weapon:null,inFlight:0}},
   peer=()=>own.combatSystem.networkG.peers.get(aid),packet=()=>({schema:'AEGIS_LINK_PACKET_G_1',sequence:peer().lastSequence+1,sentAtS:now(),cooperative:false,reports:[structuredClone(report)],group:null,grants:[]});
 const canonicalBefore=stable([...own.combatSystem.observerC.tracks]),good=packet();checks.validReport=d.networkReceiveProbeG(own.entityId,aid,good).ok;checks.sharedReportDoesNotWriteLocalFcs=canonicalBefore===stable([...own.combatSystem.observerC.tracks]);
 const file=()=>state(own.entityId).picture.find(q=>q.sources.some(s=>s.fileId===201));checks.remoteOnlyAndUnknown=file()?.localTrackId===null&&file().identity==='UNKNOWN'&&!file().automaticRelease;
 checks.noSharedOnlyRelease=d.networkVlsGateProbeG(own.entityId,201,{automatic:true}).reason==='LOCAL_FCS_REQUIRED';
 checks.replayRejected=d.networkReceiveProbeG(own.entityId,aid,good).reason==='PACKET_REPLAY';
 const mutations={truth:q=>q.reports[0].truthRef={objectId:1},positionTruth:q=>q.reports[0].objectId='SECRET',future:q=>q.reports[0].stateAtS=now()+1,nonSpd:q=>q.reports[0].covariance[0]=-1,bid:q=>q.reports[0].bid.cost=Infinity,unknown:q=>q.reports[0].classification='HARPOON',control:q=>q.group={mode:'SILENT',revision:1,untilS:now()+2}};
 for(const [name,mutate]of Object.entries(mutations)){const q=packet(),before=stable(state(own.entityId).picture),seq=peer().lastSequence;mutate(q);const result=d.networkReceiveProbeG(own.entityId,aid,q);checks['reportReject.'+name]=!result.ok&&before===stable(state(own.entityId).picture)&&seq===peer().lastSequence;}
 const q=packet(),before=stable(state(own.entityId).picture);checks.enemyReportRejected=d.networkReceiveProbeG(own.entityId,eid,q).reason==='AUTHENTICATED_ALLY_REQUIRED'&&stable(state(own.entityId).picture)===before;
 const repeated=packet(),hits=[...own.combatSystem.networkG.files.values()].find(f=>[...f.sources.values()].some(s=>s.fileId===201)).hits;checks.repeatAcceptedWithoutNewFix=d.networkReceiveProbeG(own.entityId,aid,repeated).ok&&[...own.combatSystem.networkG.files.values()].find(f=>[...f.sources.values()].some(s=>s.fileId===201)).hits===hits;
 const e={x:report.stateM,P},math=d.networkMathProbeG(e,e);checks.correlatedCovarianceNotHalved=math.nis===0&&math.intersection.P.every((v,i)=>Math.abs(v-P[i])<1e-7);
 const shifted={x:e.x.map((v,i)=>i===0?v+100:v),P};checks.correctionUsesMeasuredInputs=Math.abs(d.networkMathProbeG(e,shifted).intersection.x[0]-e.x[0]-50)<1e-6;
 checks.oppositeVelocityNotAssociated=!Number.isFinite(d.networkMathProbeG(e,{x:e.x.map((v,i)=>i===3?-v:v),P}).nis);
 d.networkCommandG(aid,{enabled:false});tick(180);checks.linkLoss=state(own.entityId).peers.every(q=>!q.connected);checks.remoteAgeNotFreshened=file().ageS>=3;tick(600);checks.sharedExpires=file()===undefined;
 d.importOperationalStateV48Wip11A(initial);tick(60);d.setEmcon(false);d.electronicCommandF(aid,{emcon:false});
 const modes={ACTIVE:[false,false],SILENT:[true,true],PLAYER_SEARCH:[false,true],ALLY_SEARCH:[true,false]};
 for(const [mode,values]of Object.entries(modes)){d.networkCommandG(own.entityId,{groupEmcon:mode});tick(90);const ew=d.electronicSnapshotF().ships;checks['group.'+mode]=ew.find(q=>q.entityId===own.entityId).settings.emcon===values[0]&&ew.find(q=>q.entityId===aid).settings.emcon===values[1];}
 const grouped=save();checks.groupSavesIndividualBaseline=grouped.ship.ew.emcon===false&&grouped.fleet.ships.find(q=>q.entityId===aid).ew.emcon===false&&grouped.ship.network.groupEmcon==='ALLY_SEARCH';
 d.networkCommandG(aid,{enabled:false});tick(180);const lost=d.electronicSnapshotF().ships;checks.groupLossRestoresIndividual=lost.find(q=>q.entityId===own.entityId).settings.emcon===false&&lost.find(q=>q.entityId===aid).settings.emcon===false;
 d.importOperationalStateV48Wip11A(grouped);const restored=snap();checks.onlySettingsRestore=restored.ships.every(q=>!q.picture.length&&!q.leases.length&&!q.queued&&!q.peers.length)&&state(own.entityId).settings.groupEmcon==='ALLY_SEARCH';
 const invalid={missingOwn:q=>delete q.ship.network,ownBool:q=>q.ship.network.enabled='ON',extra:q=>q.ship.network.truthRef=1,allyBool:q=>q.fleet.ships.find(r=>r.entityId===aid).network.enabled=1,enemyJoin:q=>q.fleet.ships.find(r=>r.entityId===eid).network.enabled=true,foreignGroup:q=>q.fleet.ships.find(r=>r.entityId===aid).network.groupEmcon='SILENT'};
 for(const [name,mutate]of Object.entries(invalid)){const q=structuredClone(grouped),before=stable(save()),life=w.lifecycle.revision;mutate(q);let rejected=false;try{d.importOperationalStateV48Wip11A(q);}catch(e){rejected=true;}checks['atomicSave.'+name]=rejected&&before===stable(save())&&life===w.lifecycle.revision;}
 const legacy=structuredClone(grouped);legacy.fleet.schema='AEGIS_NAVAL_PHYSICAL_FLEET_F_1';delete legacy.ship.network;for(const q of legacy.fleet.ships)delete q.network;
 const migration=d.validateOperationalStateV48Wip11A(legacy);checks.legacyFExplicitMigration=migration.ok&&migration.migrations.some(q=>q.id==='LEGACY_FRIENDLY_NETWORK_G');d.importOperationalStateV48Wip11A(legacy);checks.legacyRestoresNoLease=state(own.entityId).settings.groupEmcon==='INDIVIDUAL'&&state(own.entityId).leases.length===0;
 checks.networkSettingsDetached=(()=>{const q=snap();q.ships[0].settings.enabled=false;return state(own.entityId).settings.enabled;})();checks.noTruthPicture=!JSON.stringify(snap()).match(/truthRef|objectId|_truthObject|seekerMode|terminalArh/);
 checks.noFault=window.__CORE_SELFTEST_FAILURES__.length===0&&!window.__WIP125_DIAG__.wip150RuntimeFault()&&!window.__WIP125_DIAG__.wip150PresentationFault();trace.final=snap();return {checks,trace,pass:Object.values(checks).every(Boolean)};
}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);rows=[];errors=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for own,ally,width,height in [('CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA',1000,760),('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA',393,852)]:
   page=load_fleet(b,a.html.read_bytes(),own,ally,own,width,height,errors=errors);q=page.evaluate(FIXTURE);page.locator('#modeFleetBtn').click();
   page.locator('#networkRadioG').click();q['checks']['nativeRadioButton']=page.locator('#networkRadioG').inner_text()=='LINK OFF';page.wait_for_timeout(240);page.locator('#networkRadioG').click();page.locator('#networkEmconG').select_option('SILENT');page.evaluate('window.__NAVAL_SIM_DIAG__.runFramesToTicks(60,1,90)');q['checks']['nativeGroupSelector']=page.evaluate('window.__NAVAL_SIM_DIAG__.electronicSnapshotF().ships.find(q=>q.entityId===window.__AEGIS_ENGAGEMENT_RUNTIME__.activePlayerShipId).settings.emcon');page.locator('#fleetEmconG').click();q['checks']['individualToggleExitsGroup']=page.locator('#networkEmconG').input_value()=='INDIVIDUAL'and page.locator('#emconBtn').inner_text()=='EMCON OFF';page.locator('#networkStatusG').scroll_into_view_if_needed();q['checks']['statusVisible']=page.locator('#networkStatusG').is_visible();q['checks']['statusReachable']=page.evaluate("()=>{const q=document.getElementById('networkStatusG').getBoundingClientRect(),bar=document.querySelector('.control-deck-bar').getBoundingClientRect();return q.top>=0&&q.bottom<=bar.top;}");page.screenshot(path=str(a.out/(own+'-network.png')));q.update(own=own,ally=ally,viewport=[width,height]);q['pass']=all(q['checks'].values());rows.append(q);print(json.dumps({'own':own,'failed':[k for k,v in q['checks'].items()if not v]}),flush=True);page.close()
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(q['pass']for q in rows)};(a.out/'network.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
