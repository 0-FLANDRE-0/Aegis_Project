"""Exact packed F1: anonymous-port manual releases, real Harpoon flight/collision.
Replay inputs are diagnostic anonymous measurements, not a new live cross-mother link.
"""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/multiship/G'))
from browser import launch,load_fleet
SETUP=r'''
 const d=__NAVAL_SIM_DIAG__,har=__HARPOON_DIAG_A__,journal=__HARPOON_JOURNAL_F1__,checks={},records={},sid=d.exportOperationalStateV48Wip11A().shipId,ship=get3DRenderState().ship,
 now=()=>d.observerSnapshotC().worldTimeS,tick=n=>d.stepTicks(n),facade=()=>d.observerFacadeC(sid);
 d.setTerrainDiagBypass(true);d.setEmcon(true);har.forgetCombatTracksDiagnostic();
 let sequence=0;const feed=(rangeM=8000,sigmaM=20,sourceId='HELI_REPLAY')=>{d.offboardDiagnosticC(sid,{link:{sourceId,connected:true,latencyS:0}});return d.offboardDiagnosticC(sid,{report:{schema:'AEGIS_OFFBOARD_PLOT_C_1',sourceId,sequence:++sequence,measuredAtS:now(),positionM:{x:ship.worldXM+rangeM,y:ship.worldYM,z:8},covarianceM2:[sigmaM*sigmaM,0,0,0,sigmaM*sigmaM,0,0,0,16],domainEvidence:{surface:.98,air:.02,missile:.01,background:.01}}});};
 const establish=(rangeM=8000,sigmaM=20)=>{for(let i=0;i<7;i++){feed(rangeM,sigmaM);tick(60);}const tr=facade().tracks.find(t=>t.source==='OFFBOARD_C');if(!tr)throw Error('NO_REPLAY_TRACK');return tr;};
'''
GATES='()=>{'+SETUP+r'''
 const tr=establish(),id=tr.trackId;checks.onlyOffboard=tr.confirmed&&tr.offboard.localAgeS===null;
 records.unknown=har.gate(id);checks.unknownProtected=!records.unknown.ok;
 records.operator=d.a3SetOperatorIdentity(id,'HOSTILE');records.near=har.gate(id);checks.operatorOffboard=records.operator.ok&&records.operator.identificationEvidence==='OPERATOR_ONLY';checks.nearManualPermitted=records.near.ok&&records.near.predictionSigmaM<=har.profile().sim.acquisitionBasketM;
 records.direct=har.gate(id,records.near.tubeId);checks.fixedTubeSameReadiness=records.direct.ok&&records.direct.predictionSigmaM===records.near.predictionSigmaM;
 records.auto=har.autoTube(id,{automatic:true,mode:'AUTO'});records.semi=har.autoTube(id,{mode:'SEMIAUTO'});records.forged=har.autoTube(id,{attackH3:{ownerId:sid}});checks.autoBlocked=records.auto.reason==='MANUAL_SURFACE_AUTHORITY_REQUIRED';checks.semiBlocked=records.semi.reason==='MANUAL_SURFACE_AUTHORITY_REQUIRED';checks.forgedAiTokenBlocked=records.forged.reason==='ATTACK_CAPABILITY_REQUIRED';
 for(const identity of ['FRIEND','NEUTRAL']){d.a3SetOperatorIdentity(id,identity);checks['protect'+identity]=!har.gate(id).ok;}d.a3SetOperatorIdentity(id,'HOSTILE');
 d.offboardDiagnosticC(sid,{link:{sourceId:'HELI_REPLAY',connected:false,latencyS:0}});tick(611);records.stale=har.gate(id);checks.expiry10s=records.stale.reason==='SURFACE_TRACK_COAST_EXPIRED';checks.noFailedLaunchLog=journal.snapshot().records.length===0;
 har.forgetCombatTracksDiagnostic();const far=establish(100000,100);d.a3SetOperatorIdentity(far.trackId,'HOSTILE');records.far=har.gate(far.trackId,har.installation().tubes[0].id);checks.longFarBasket=records.far.reason==='INS_PREDICTION_BASKET_INSUFFICIENT'&&records.far.predictionSigmaM>har.profile().sim.acquisitionBasketM;
 har.forgetCombatTracksDiagnostic();d.wip13cSetControlDeckTab('ARM');har.routeToggle();har.routeAdd({x:ship.worldXM+10000,y:ship.worldYM+1000});records.coordinate=har.gate(null);checks.coordinatePreserved=records.coordinate.ok&&records.coordinate.authority.mode==='MANUAL_COORDINATE_SEARCH';har.routeToggle();
 checks.corePass=__CORE_SELFTEST_FAILURES__.length===0;return {checks,records};}'''
FLIGHT='disconnect=>{'+SETUP+r'''
 d.createWip13aSurfaceTargetFixture({rangeKm:8,bearingDeg:0,headingDeg:90,speedKt:0});
 const tr=establish(),id=tr.trackId;d.a3SetOperatorIdentity(id,'HOSTILE');records.release=har.fire(id);har.focusedTicks(30);const released=har.snapshot().missiles[0];checks.actualRelease=records.release.ok&&!!released;
 checks.frozenNoUpdates=released.memory.updatesAfterRelease===false&&!har.profile().public.dataLink;
 records.launch=journal.snapshot();checks.launchObservedFields=records.launch.records[0]?.trackComposition==='OFFBOARD'&&records.launch.records[0]?.identificationEvidence==='OPERATOR_ONLY'&&records.launch.records[0]?.operatorIdentity==='HOSTILE';
 if(disconnect){d.offboardDiagnosticC(sid,{link:{sourceId:'HELI_REPLAY',connected:false,latencyS:0}});har.forgetCombatTracksDiagnostic();}
 for(let i=0;i<160&&har.snapshot().missiles[0].alive;i++)har.focusedTicks(60);
 records.final=har.snapshot().missiles[0];records.log=journal.snapshot();const entry=records.log.records[0];
 checks.terminated=!records.final.alive&&!!entry.termination;checks.neutralMerchantHit=entry.termination?.result==='HIT'&&entry.termination.hitCategory==='NEUTRAL_MERCHANT';checks.afterActionOnly=entry.termination?.basis==='AFTER_ACTION_TRUTH';checks.noFlightTelemetry=har.operatorPicture().contacts?.length===0||!JSON.stringify(har.operatorPicture()).includes('SURFACE_CONTACT');
 const detached=journal.snapshot();detached.records[0].operatorIdentity='POISON';checks.snapshotDetached=journal.snapshot().records[0].operatorIdentity==='HOSTILE';
 checks.corePass=__CORE_SELFTEST_FAILURES__.length===0;return {checks,records};}'''
FOREIGN=r'''()=>{
 const d=__NAVAL_SIM_DIAG__,checks={},records={},sid=d.exportOperationalStateV48Wip11A().shipId,ally=d.observerSnapshotC().ships.find(s=>s.ownerEntityId!==sid).ownerEntityId,ship=get3DRenderState().ship;
 d.setTerrainDiagBypass(true);d.setEmcon(true);d.observerCommandC(ally,{emcon:true});d.defenseCommandE(ally,{mode:'HOLD'});d.physicalShipCommandB(ally,{targetSpeedKt:0,targetRudder:0});d.offboardDiagnosticC(ally,{link:{sourceId:'REPLAY',connected:true,latencyS:0}});
 for(let i=1;i<7;i++){d.offboardDiagnosticC(ally,{report:{schema:'AEGIS_OFFBOARD_PLOT_C_1',sourceId:'REPLAY',sequence:i,measuredAtS:d.observerSnapshotC().worldTimeS,positionM:{x:ship.worldXM+8000,y:ship.worldYM,z:8},covarianceM2:[400,0,0,0,400,0,0,0,16],domainEvidence:{surface:.98,air:.02,missile:.01,background:.01}}});d.stepTicks(60);}
 const tr=d.observerFacadeC(ally).tracks.find(t=>t.source==='OFFBOARD_C');records.track=tr;checks.ownerHasAnonymousTrack=!!tr?.confirmed&&tr.offboard.localAgeS===null;
 records.identity=d.fleetCommandG(ally,{action:'IDENTITY',trackId:tr.trackId,identity:'HOSTILE'});checks.fleetOperatorAllowed=records.identity.ok;
 records.request=d.fleetCommandG(ally,{action:'FIRE',trackId:tr.trackId,weapon:'HARPOON'});checks.foreignFleetManualAccepted=records.request.ok;d.stepTicks(30);
 records.log=__HARPOON_JOURNAL_F1__.snapshot(ally);checks.foreignOwnerLog=records.log.records.length===1&&records.log.records[0].identificationEvidence==='OPERATOR_ONLY';checks.ownLogSeparate=__HARPOON_JOURNAL_F1__.snapshot(sid).records.length===0;
 const save=d.exportOperationalStateV48Wip11A();checks.notSaved=!JSON.stringify(save).includes('harpoonJournalF1')&&!JSON.stringify(save).includes('AFTER_ACTION_TRUTH');d.importOperationalStateV48Wip11A(save);checks.lifecycleClears=__HARPOON_JOURNAL_F1__.snapshot(ally).records.length===0;
 checks.corePass=__CORE_SELFTEST_FAILURES__.length===0;return {checks,records};}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();errors=[];results={}
 with sync_playwright()as pw:
  b=launch(pw)
  def load(own='CG_52_LATE_TICONDEROGA',ally=None):
   page=load_fleet(b,raw,own=own,ally=ally,enemy=None,errors=errors);page.evaluate('window.requestAnimationFrame=()=>0');return page
  page=load();results['gates']=page.evaluate(GATES);page.close()
  for drop in [False,True]:
   page=load();r=page.evaluate(FLIGHT,drop);results['flightDrop'if drop else'flightConnected']=r
   page.evaluate("document.getElementById('modeDebugBtn').click();document.getElementById('harpoonJournalF1').click()")
   r['checks']['debugModal']=page.locator('#harpoonJournalDialogF1').is_visible();r['checks']['copyableText']=page.locator('#harpoonJournalTextF1').input_value().find('중립 상선')>=0 and page.locator('#harpoonJournalTextF1').get_attribute('readonly')is not None
   page.screenshot(path=str(a.out/('journal-disconnected.png'if drop else'journal-connected.png')));page.close()
  page=load('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA');results['foreign']=page.evaluate(FOREIGN);page.close();b.close()
 checks={k+'.'+name:bool(v)for k,r in results.items()for name,v in r['checks'].items()};f=[results[k]['records']['final']for k in ['flightConnected','flightDrop']];checks['linkLossFlightIdentical']=f[0]==f[1]
 out={'pass':all(checks.values())and not errors,'checks':checks,'results':results,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(a.out/'native.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'outcomes':[x.get('outcome')for x in f],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
