"""Two physical recipients in the acquisition basket: intended hostile and neutral hulk."""
import argparse,hashlib,json,re,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/multiship/G'))
from browser import launch,load_fleet
from verify_native import SETUP
TEST='units=>{'+SETUP+r'''
 const save=d.exportOperationalStateV48Wip11A(),enemy=save.fleet.ships.find(s=>s.role==='ENEMY'),n=enemy.ship.navigation;
 n.positionWorld={x:10*units,y:0};n.previousPositionWorld={...n.positionWorld};n.heading=Math.PI/2;n.previousHeadingWorld=n.heading;n.speedKt=0;n.targetSpeedKt=0;n.vx=0;n.vy=0;
 const validation=d.validateOperationalStateV48Wip11B(save);if(!validation.ok)throw Error(JSON.stringify(validation));d.importOperationalStateV48Wip11A(save);d.setTerrainDiagBypass(true);d.setEmcon(true);d.defenseCommandE(enemy.entityId,{mode:'HOLD'});d.observerCommandC(enemy.entityId,{emcon:true});
 d.createWip13aSurfaceTargetFixture({rangeKm:8,bearingDeg:0,headingDeg:90,speedKt:0});const tr=establish(10000);d.a3SetOperatorIdentity(tr.trackId,'HOSTILE');const gate=har.gate(tr.trackId),request=har.fire(tr.trackId);har.focusedTicks(30);
 for(let i=0;i<120&&har.snapshot().missiles[0].alive;i++)har.focusedTicks(60);
 const final=har.snapshot().missiles[0],log=journal.snapshot(),row=log.records[0],reads=final.seeker.observations;
 checks.basketContainsTwoPhysicalShips=gate.ok&&2000<har.profile().sim.acquisitionBasketM;
 checks.manualOperatorOnly=row.identificationEvidence==='OPERATOR_ONLY'&&row.operatorIdentity==='HOSTILE';checks.hitNeutralDespiteIntendedHostile=final.outcome==='SURFACE_CONTACT'&&row.termination.hitCategory==='NEUTRAL_MERCHANT';checks.truthOnlyAfterAction=row.termination.basis==='AFTER_ACTION_TRUTH';checks.actualSeekerObservations=reads>0;
 return {checks,gate,request,final,log,enemyId:enemy.entityId,geometry:{intendedHostileRangeM:10000,neutralRangeM:8000,separationM:2000,basketM:har.profile().sim.acquisitionBasketM},core:__CORE_SELFTEST_FAILURES__};}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();import base64,gzip
 main=gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">(.*?)</script>',raw,re.S)[1])).decode();units=float(re.search(r'const WORLD_UNITS_PER_KM_FIXED = ([0-9.]+)',main)[1]);errors=[]
 with sync_playwright()as pw:
  b=launch(pw);page=load_fleet(b,raw,own='CG_52_LATE_TICONDEROGA',ally=None,enemy='CG_52_LATE_TICONDEROGA',errors=errors);page.evaluate('window.requestAnimationFrame=()=>0');out=page.evaluate(TEST,units);b.close()
 out.update(errors=errors,htmlSha256=hashlib.sha256(raw).hexdigest());out['checks']['corePass']=not out['core'];out['pass']=all(out['checks'].values())and not errors;(a.out/'mixed-basket.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(out['checks']),'failed':[k for k,v in out['checks'].items()if not v],'outcome':out['final']['outcome'],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
