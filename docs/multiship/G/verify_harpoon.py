"""Paired unchanged F vs G source at measured edge cases, then real routed flight.
Fixtures supply launch acknowledgment and radar observations only; physical truth
in the natural-flight trace is diagnostic evidence and never classifier input.
"""
import argparse,hashlib,json,re,subprocess,sys,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_g import launch,load_fleet
from verify_static import decoded
from build import extract
HERE=Path(__file__).resolve().parent
PURE=r'''
const SIM_FIXED_DT=1/60,clamp=(v,a,b)=>Math.max(a,Math.min(b,v)),angNorm=v=>Math.atan2(Math.sin(v),Math.cos(v)),worldToMeters=v=>v/.0038,worldSpeedToMps=worldToMeters,HARPOON_PROFILE_A={sim:{boosterBurnS:3.2}},harpoonPredictionA=()=>({x:10000,y:0});let simStepCounter=240,ACTIVE_SHIP_RUNTIME={weapons:{harpoon:{launches:[]}}},files=new Map();const observerC=()=>({tracks:files});
__SOURCE__
const checks={},trace={},reset=()=>{simStepCounter=240;files=new Map();ACTIVE_SHIP_RUNTIME.weapons.harpoon.launches=[{id:1,tubeId:'A4',releaseStep:0,positionM:{x:0,y:0},axis:{x:1,y:0},carrierVelocityMps:{x:0,y:0},routeProgram:{pointsM:[{x:10000,y:0}]},excludedTrackIds:[],claimedTrackId:null}];};
const record=()=>ACTIVE_SHIP_RUNTIME.weapons.harpoon.launches[0],track=(id=1)=>{const P=new Float64Array(36);for(let i=0;i<6;i++)P[i*6+i]=i<3?100:25;const tr={trackId:id,z:30,sensorDetected:true,sensorSource:'SPY1DV_TRACK_REVISIT',_kfP:P};files.set(id,tr);return tr;},observe=(tr,step,patch={})=>{simStepCounter=Math.max(simStepCounter,step);const p=harpoonLaunchPredictionC(record(),step/60);Object.assign(tr,{x:p.x*.0038,y:p.y*.0038,vx:225*.0038,vy:0,_lastMeasurementStep:step,_kfX:Float64Array.from([p.x,p.y,30,225,0,0])},patch);return harpoonTrackIdentityC(tr);};
const confirmed=()=>{reset();const tr=track();observe(tr,220);observe(tr,230);observe(tr,240);return tr;};
let tr=confirmed();checks.initialThreeMeasuredFixes=tr._harpoonOwnC?.confirmed===true;
let p=tr._harpoonOwnC;simStepCounter=270;tr._kfP[21]=tr._kfP[28]=200**2;trace.notch=observe(tr,270,{_kfX:Float64Array.from([p.x+100,p.y,30,15,0,0])});checks.notchProtected=!!trace.notch;
tr=confirmed();p=tr._harpoonOwnC;trace.turn=observe(tr,300,{_kfX:Float64Array.from([p.x+180,p.y+80,30,40,220,0])});checks.turnProtected=!!trace.turn;
tr=confirmed();p=tr._harpoonOwnC;trace.reacquire=observe(tr,570,{_kfX:Float64Array.from([p.x+225*5.5,p.y,30,225,0,0])});checks.fiveSecondReacquire=!!trace.reacquire;
tr=confirmed();simStepCounter=540;trace.coast=harpoonTrackIdentityC(tr);checks.fiveSecondPendingProtection=trace.coast?.identity==='UNKNOWN';simStepCounter=780;checks.nineSecondCoastExpires=harpoonTrackIdentityC(tr)===null;
// A late alias follows a recently measured confirmed radar history, not missile truth.
tr=confirmed();for(let step=300;step<=900;step+=60)observe(tr,step);files.delete(tr.trackId);const alias=track(2);trace.alias=observe(alias,960);checks.lateMeasuredAlias=trace.alias?.identity==='FRIEND';
tr=confirmed();p=tr._harpoonOwnC;trace.inbound=observe(tr,300,{_kfX:Float64Array.from([p.x-225,p.y,30,-225,0,0])});checks.clearlyOppositeInboundNotProtected=trace.inbound===null;
reset();record().excludedTrackIds=[1];tr=track();checks.preexistingTrackExcluded=observe(tr,240)===null;
reset();tr=track();checks.unobservedLateLaunchNotManufactured=observe(tr,900)===null;
reset();tr=track();tr.sensorSource='SPS73_NAV';checks.unqualifiedRadarNotLaunchIdentity=observe(tr,240)===null;
tr=confirmed();p=tr._harpoonOwnC;trace.mismatch=observe(tr,300,{_kfX:Float64Array.from([p.x+3000,p.y,30,180,90,0])});checks.pendingMismatchProtection=trace.mismatch?.identity==='UNKNOWN';
console.log(JSON.stringify({checks,trace}));
'''
NATURAL=r'''()=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__,w=window.__AEGIS_ENGAGEMENT_RUNTIME__,oid=w.activePlayerShipId,aid='SHIP_SCENARIO_ALLY_F',checks={},rows=[];d.setTerrainDiagBypass(true);d.setEmcon(false);d.wip119SetMode('MANUAL');d.defenseCommandE(aid,{mode:'AUTO'});h.forgetCombatTracksDiagnostic();h.routeToggle();h.routeAdd({x:3000,y:0});h.routeAdd({x:5000,y:8000});h.routeAdd({x:15000,y:8000});const release=h.fire();d.wip119SetMode('AUTO');
 for(let i=0;i<60;i++){h.fixedTicks(60);const m=h.snapshot().missiles[0],s=d.networkSnapshotG();rows.push({timeS:i+1,diagnosticOnlyMissile:m?{positionM:m.positionM,alive:m.alive,route:m.route,seeker:m.seeker}:null,picture:h.operatorPicture(),network:s,ownFire:d.wip119AutonomySnapshot().fireLog,allyFire:d.defenseSnapshotE().ships.find(q=>q.entityId===aid).autonomy.fireLog});}
 checks.actualRelease=release.ok;checks.observedBeforeAndAfterTurn=rows.some(q=>q.timeS<12&&q.picture.launches[0].source==='RADAR')&&rows.some(q=>q.timeS>25&&q.picture.launches[0].source==='RADAR');checks.noSelfOrAlliedAutoIntercept=rows.every(q=>q.ownFire.length===0&&q.allyFire.length===0);checks.noFlightDl=rows.every(q=>!q.picture.telemetryAvailable&&!q.network.ordnanceDatalink);checks.routeContinues=rows.at(-1).diagnosticOnlyMissile?.alive===true;checks.measuredOwnFriendShared=rows.some(q=>q.network.ships.find(s=>s.entityId===aid).picture.some(f=>f.domain==='AIR'&&f.identity==='FRIEND'&&f.sources.some(s=>s.kind==='TRACK')));
 d.setEmcon(true);d.electronicCommandF(aid,{emcon:true});h.fixedTicks(600);const blind=h.operatorPicture();checks.blindPositionAbsent=blind.launches[0].positionM===null;checks.blindFlightContinues=h.snapshot().missiles[0].alive;checks.coreZero=window.__CORE_SELFTEST_FAILURES__.length===0;checks.faultZero=!window.__WIP125_DIAG__.wip150RuntimeFault()&&!window.__WIP125_DIAG__.wip150PresentationFault();return {checks,release,rows,blind,pass:Object.values(checks).every(Boolean)};}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);b=decoded(a.baseline.read_text());c=decoded(a.html.read_text());pred=re.search(r'function harpoonLaunchPredictionC\(.*?\n}',b,re.S)[0];versions={};errors=[]
 for name,src in [('F',extract(b,'harpoonMatchLaunchC')+'\n'+extract(b,'harpoonTrackIdentityC')),('G',(HERE/'launch-protection.js').read_text())]:
  assert all(part in c for part in [pred])
  with tempfile.TemporaryDirectory() as tmp:
   f=Path(tmp)/'fixture.js';f.write_text(PURE.replace('__SOURCE__',pred+'\n'+src));versions[name]=json.loads(subprocess.check_output(['node',str(f)]))
 with sync_playwright() as pw:
  browser=launch(pw);page=load_fleet(browser,a.html.read_bytes(),enemy=None,errors=errors);page.locator('#modeAimBtn').click();natural=page.evaluate(NATURAL);page.close();browser.close()
 checks={**versions['G']['checks'],'pairedFReproducesNotchLoss':not versions['F']['checks']['notchProtected'],'pairedFReproducesTurnLoss':not versions['F']['checks']['turnProtected'],'pairedFReproducesReacquireLoss':not versions['F']['checks']['fiveSecondReacquire'],**{'natural.'+k:v for k,v in natural['checks'].items()},'pageErrorsZero':not errors};report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'checks':checks,'paired':versions,'natural':natural,'errors':errors,'pass':all(checks.values())};(a.out/'harpoon.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'failed':[k for k,v in checks.items()if not v],'pass':report['pass']}));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
