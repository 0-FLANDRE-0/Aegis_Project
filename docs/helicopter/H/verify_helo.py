"""Native APS/Hawklink reports replayed through CG52 receiver, WITHOUT live cross-mother sharing."""
import argparse,json,hashlib,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/multiship/G'));sys.path.append(str(ROOT/'docs/helicopter/F'))
from browser import launch,load_fleet
import importlib.util
_spec=importlib.util.spec_from_file_location('baseline_helo_native',ROOT/'docs/helicopter/F/verify_native.py');_mod=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_mod);HOVER=_mod.HOVER
COLLECT='options=>{const d=__NAVAL_SIM_DIAG__,api=__HELO__;'+HOVER+r'''
 hover(options.alt,options.mode);d.createWip13aSurfaceTargetFixture({rangeKm:options.rangeKm,bearingDeg:0,headingDeg:90,speedKt:0});const id=api.snapshot().aircraft[0].id,plots=[],seen=new Set();
 for(let i=0;i<options.ticks;i++){d.stepTicks(1);const q=__AEGIS_ACTIVE_SHIP_RUNTIME__.aviation.heloSensorsE.get(id)?.radar;for(const p of q?.stepPlots??[]){if(Math.hypot(p.positionM.x-options.rangeKm*1000,p.positionM.y)<1000&&!seen.has(p.measuredAtS)){seen.add(p.measuredAtS);plots.push(structuredClone(p));}}}
 return {plots,helo:api.snapshot(),observer:d.observerFacadeC(d.exportOperationalStateV48Wip11A().shipId),port:d.offboardSnapshotC(),core:__CORE_SELFTEST_FAILURES__,installation:__HARPOON_DIAG_A__.installation()};}'''
REPLAY=r'''plots=>{const d=__NAVAL_SIM_DIAG__,h=__HARPOON_DIAG_A__,sid=d.exportOperationalStateV48Wip11A().shipId;d.setTerrainDiagBypass(true);d.setEmcon(true);h.forgetCombatTracksDiagnostic();d.offboardDiagnosticC(sid,{link:{sourceId:'APS_REPLAY',connected:true,latencyS:0}});let seq=0;
 for(const p of plots.slice(-6)){d.offboardDiagnosticC(sid,{report:{schema:'AEGIS_OFFBOARD_PLOT_C_1',sourceId:'APS_REPLAY',sequence:++seq,measuredAtS:d.observerSnapshotC().worldTimeS,positionM:p.positionM,covarianceM2:p.covarianceM2,domainEvidence:p.domainEvidence}});d.stepTicks(60);}
 const tr=d.observerFacadeC(sid).tracks.find(t=>t.source==='OFFBOARD_C');if(!tr)return {tr:null};const identity=d.a3SetOperatorIdentity(tr.trackId,'HOSTILE'),gate=h.gate(tr.trackId,h.installation().tubes[0].id);return {tr,identity,gate};}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();errors=[];rows=[];checks={}
 with sync_playwright()as pw:
  b=launch(pw)
  for mode,r,alt,ticks in [('SHORT',20,152,800),('PERI',20,152,1000),('LONG',100,3000,3000)]:
   page=load_fleet(b,raw,own='DDG_119_LATE_FLIGHT_IIA',ally=None,enemy=None,errors=errors);page.evaluate('window.requestAnimationFrame=()=>0');live=page.evaluate(COLLECT,{'mode':mode,'rangeKm':r,'alt':alt,'ticks':ticks});page.close()
   checks[mode+'.realConfirmedReports']=len(live['plots'])>=3;checks[mode+'.realHawklinkDelivered']=live['port']['accepted']>0;checks[mode+'.onlyOffboardMotherTracks']=any(t['source']=='OFFBOARD_C'and t['offboard']['localAgeS']is None for t in live['observer']['tracks']);checks[mode+'.core']=not live['core']
   page=load_fleet(b,raw,own='CG_52_LATE_TICONDEROGA',ally=None,enemy=None,errors=errors);page.evaluate('window.requestAnimationFrame=()=>0');receiver=page.evaluate(REPLAY,live['plots']);page.close();rows.append({'mode':mode,'rangeKm':r,'altitudeM':alt,'live':live,'receiver':receiver})
   checks[mode+'.replayConfirmed']=bool(receiver.get('tr',{}).get('confirmed'));g=receiver.get('gate',{});checks[mode+'.releaseQuality']=g.get('reason')=='INS_PREDICTION_BASKET_INSUFFICIENT'if mode=='LONG'else g.get('ok')is True
  b.close()
 out={'pass':all(checks.values())and not errors,'checks':checks,'rows':rows,'errors':errors,'note':'Diagnostic receiver replay only. DDG helicopter / CG Harpoon live composition deliberately unchanged.','htmlSha256':hashlib.sha256(raw).hexdigest()};(a.out/'helo-replay.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'counts':[len(x['live']['plots'])for x in rows],'gates':[x['receiver'].get('gate',{}).get('reason')for x in rows],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
