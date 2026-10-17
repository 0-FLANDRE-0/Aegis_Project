"""Mobile/desktop actual buttons: passive designation, retained blocked actions, release-time log."""
import argparse,json,hashlib,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/helicopter/H'))
from browser import load_fleet,launch
SETUP=r'''()=>{const d=__NAVAL_SIM_DIAG__,s=d.exportOperationalStateV48Wip11A(),ship=get3DRenderState().ship;d.setTerrainDiagBypass(true);d.setEmcon(true);d.offboardDiagnosticC(s.shipId,{link:{sourceId:'ANON',connected:true,latencyS:0}});for(let i=1;i<=7;i++){d.offboardDiagnosticC(s.shipId,{report:{schema:'AEGIS_OFFBOARD_PLOT_C_1',sourceId:'ANON',sequence:i,measuredAtS:d.observerSnapshotC().worldTimeS,positionM:{x:ship.worldXM+8000,y:ship.worldYM,z:8},covarianceM2:[400,0,0,0,400,0,0,0,16],domainEvidence:{surface:.98,air:.02,missile:.01,background:.01}}});d.stepTicks(60);}const tr=d.observerFacadeC(s.shipId).tracks.find(t=>t.source==='OFFBOARD_C');if(!tr)throw Error('NO_ANON_TRACK');d.a3SetOperatorIdentity(tr.trackId,'HOSTILE');d.lockTrackViaCursor(tr.trackId);return tr.trackId;}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();checks={};rows=[];errors=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for width,height in [(390,1000),(1100,800)]:
   x=load_fleet(b,raw,width=width,height=height,errors=errors);tid=x.evaluate(SETUP);x.locator('[data-tab=ARM]').click();x.locator('#lockBtn').click();x.evaluate('__NAVAL_SIM_DIAG__.stepTicks(1)');s=x.evaluate('__EMCON_DESIGNATION_F2__.snapshot()');checks[f'{width}.passivePointer']=s['selectedLockId']==tid and not s['pdTracking']and s['physicalSpyEmitters']==0;box=x.locator('#lockBtn').bounding_box();checks[f'{width}.labelFits']=box['x']>=0 and box['x']+box['width']<=width+.1 and '지정 (EMCON · 방사 없음)'in x.locator('#lockBtn').inner_text();x.locator('#autoEngBtn').click();x.locator('#external3DAutoLockBtn').evaluate('e=>e.click()');s=x.evaluate('__EMCON_DESIGNATION_F2__.snapshot()');checks[f'{width}.autoControlsStillBlocked']=s['selectedLockId']==tid and not s['pdTracking'];
   if x.locator('#armSubVlsBtn').is_visible():x.locator('#armSubVlsBtn').click()
   before=x.evaluate('__NAVAL_SIM_DIAG__.snapshot().liveInterceptors');x.locator('#fireBtn').click();x.locator('#external3DFireBtn').evaluate('e=>e.click()');checks[f'{width}.vlsButtonsStillBlocked']=before==x.evaluate('__NAVAL_SIM_DIAG__.snapshot().liveInterceptors')
   x.screenshot(path=str(a.out/f'passive-{width}.png'));x.locator('#harpoonFireA').click();x.evaluate('__NAVAL_SIM_DIAG__.setEmcon(false);__NAVAL_SIM_DIAG__.stepTicks(30)');s=x.evaluate('__EMCON_DESIGNATION_F2__.snapshot()');j=x.evaluate('__HARPOON_JOURNAL_F1__.snapshot()');checks[f'{width}.releaseTimeNotRequestTime']=len(j['records'])==1 and j['records'][0]['launchEmcon']is False;checks[f'{width}.offRestoresNormalPrecision']=s['selectedLockId']==tid and s['pdTracking']and s['physicalSpyEmitters']>0;checks[f'{width}.core']=x.evaluate('__CORE_SELFTEST_FAILURES__.length===0');rows.append({'width':width,'state':s,'journal':j});x.close()
  b.close()
 out={'pass':all(checks.values())and not errors,'checks':checks,'rows':rows,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(a.out/'ui.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
