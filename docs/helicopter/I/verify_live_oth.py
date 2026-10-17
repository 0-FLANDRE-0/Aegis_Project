"""Actual CG launch -> APS -> native Hawklink -> manual Harpoon, no report replay."""
import argparse,json,hashlib,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/helicopter/H'))
from browser import load_fleet,launch
TEST=r'''()=>{const a=__HELO__,d=__NAVAL_SIM_DIAG__,har=__HARPOON_DIAG_A__,sid=d.exportOperationalStateV48Wip11A().shipId,checks={},records={};d.setTerrainDiagBypass(true);d.setEmcon(true);d.wip13a3SetManualWeather({hsM:.9,windSpeedMps:0,precipitation01:0});const id=a.snapshot().aircraft[0].id;a.command(id,'SET_ALTITUDE',{altitudeM:300});a.command(id,'LAUNCH');d.stepTicks(14400);checks.realDeparture=a.snapshot().aircraft[0].onboard===false&&a.snapshot().aircraft[0].altitudeM===300;
 records.fixture=d.createWip13aSurfaceTargetFixture({rangeKm:40,bearingDeg:0,headingDeg:90,speedKt:0});a.command(id,'SET_RADAR_MODE',{mode:'PERI'});d.stepTicks(900);const facade=d.observerFacadeC(sid),tr=facade.tracks.find(t=>t.classification==='SURFACE'&&t.confirmed&&t.source==='OFFBOARD_C'&&Math.abs(t.positionM.x-40000)<1000);records.tr=tr??null;checks.realHawklinkSurface=!!tr&&tr.offboard.localAgeS===null&&tr.offboard.remote.some(q=>q.sourceId==='H1');records.link=a.snapshot().aircraft[0].sensorsE.link;checks.realPacketsDelivered=records.link.connected&&records.link.transmittedTotal>0;
 if(tr){records.identity=d.a3SetOperatorIdentity(tr.trackId,'HOSTILE');records.gate=har.gate(tr.trackId);checks.nativeManualGate=records.gate.ok;records.fire=har.fire(tr.trackId);d.stepTicks(30);records.launch=__HARPOON_JOURNAL_F1__.snapshot();const m=har.snapshot().missiles[0];checks.actualMissile=!!m&&records.fire.ok;checks.noDatalink=m.memory.updatesAfterRelease===false;checks.releaseEvidence=records.launch.records[0].trackComposition==='OFFBOARD'&&records.launch.records[0].identificationEvidence==='OPERATOR_ONLY';}
 checks.noQueueOverload=d.offboardSnapshotC().rejected===0;checks.core=!__CORE_SELFTEST_FAILURES__.length;return {checks,records,offboard:d.offboardSnapshotC(),helo:a.snapshot()};}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();errors=[]
 with sync_playwright()as pw:
  b=launch(pw);x=load_fleet(b,raw,own='CG_52_LATE_TICONDEROGA',errors=errors);x.evaluate('window.requestAnimationFrame=()=>0');out=x.evaluate(TEST);b.close()
 out.update(errors=errors,htmlSha256=hashlib.sha256(raw).hexdigest());out['pass']=all(out['checks'].values())and not errors;(a.out/'live-oth.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(out['checks']),'failed':[k for k,v in out['checks'].items()if not v],'gate':out['records'].get('gate',{}).get('reason'),'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
