"""Pinned D -> E prelaunch routes. Repack only record 13, plus declared markup."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=ROOT/'Aegis_SIM_v48_WIP_HARPOON_D.html'
if not BASE.is_file():BASE=ROOT/'archive/v48/WIP_HARPOON_D/Aegis_SIM_v48_WIP_HARPOON_D.html'
BASE_SHA='e92aff9c19a074aa98c3ceca236abaa14b2a674f8417419df7a08dbc248700a1'
def patches():
 old_ui=(HERE.parent/'D/ui.js').read_text()
 return [
  ("id:'RGM84D_BLOCK1C_C1',revision:'HARPOON_C1'","id:'RGM84D_BLOCK1C_E1',revision:'HARPOON_E1'"),
  ("revision:'BUNKERHILL_HARPOON_C_1'","revision:'BUNKERHILL_HARPOON_E_1'"),
  ("[ACTIVE_SHIP_PROFILE.revision,'BUNKERHILL_HARPOON_B_1'","[ACTIVE_SHIP_PROFILE.revision,'BUNKERHILL_HARPOON_C_1','BUNKERHILL_HARPOON_B_1'"),
  ('maxLaunchRangeKm:124','maxLaunchRangeKm:140'),
  ('fuelKg:110,fuelFlowKgS:.245','fuelKg:110,fuelFlowKgS:.225'),
  ('seekerActivationRangeM:14000,seekerPeriodS:.1','seekerMinSurfaceVerticalM:3.5,seekerMaxSurfaceDopplerSpreadMps:2.5,\n    routeMaxPoints:8,routeMinLegM:2000,routeSearchAheadM:8000,routeTurnReserveM:2000,routeCaptureM:200,routePassCorridorM:500,\n    seekerActivationRangeM:14000,seekerPeriodS:.1'),
  ("pending:null,releaseCooldownS:0,lastResult:null,launches:[]","pending:null,releaseCooldownS:0,lastResult:null,launches:[],routeDraft:{editing:false,pointsM:[]}"),
  ('function harpoonGateA(trackId=selectedLockId,tubeId=harpoonRuntimeA().selectedTubeId,options={}){',
   (HERE/'route.js').read_text()+"\nfunction harpoonGateA(trackId=selectedLockId,tubeId=harpoonRuntimeA().selectedTubeId,options={}){\n  if(options.routeProgram||harpoonRuntimeA().routeDraft.pointsM.length)return harpoonRouteGateE(trackId,tubeId,options);"),
  ('const aim=harpoonPredictionA(gate.memory,0,gate.muzzleM),','const aim=gate.routeProgram?.pointsM[0]??harpoonPredictionA(gate.memory,0,gate.muzzleM),'),
  ('r.pending={trackId:gate.trackId,tubeId,remainingS:HARPOON_PROFILE_A.sim.releaseDoorDelayS};','r.pending={trackId:gate.trackId,tubeId,routeProgram:gate.routeProgram??null,remainingS:HARPOON_PROFILE_A.sim.releaseDoorDelayS};'),
  ('harpoonGateA(pending.trackId,pending.tubeId,{actualRelease:true})','harpoonGateA(pending.trackId,pending.tubeId,{actualRelease:true,routeProgram:pending.routeProgram})'),
  ('memory:gate.memory,massKg:','route:gate.routeProgram?{program:gate.routeProgram,index:0,completed:false,passes:[],previousInsM:{x:pos.x,y:pos.y}}:null,\n    memory:gate.memory,massKg:'),
  ("r.lastResult='RELEASED:'+serial;","r.lastResult='RELEASED:'+serial;r.routeDraft={editing:false,pointsM:[]};"),
  ("if(!s.active&&m.ageS>=cfg.boosterBurnS&&rangeToBasket<=cfg.seekerActivationRangeM)","if(!s.active&&m.ageS>=cfg.boosterBurnS&&(m.route?m.route.completed:rangeToBasket<=cfg.seekerActivationRangeM))"),
  ('o.verticalExtentM<1.4||o.dopplerSpreadMps>4','o.verticalExtentM<cfg.seekerMinSurfaceVerticalM||o.dopplerSpreadMps>cfg.seekerMaxSurfaceDopplerSpreadMps'),
  ('cueGate=Math.min(cfg.seekerSearchBasketM,Math.max(250,3*Math.sqrt(lambda+75**2+(t*t*.04)**2))),','cueGate=m.route?cfg.seekerSearchBasketM:Math.min(cfg.seekerSearchBasketM,Math.max(250,3*Math.sqrt(lambda+75**2+(t*t*.04)**2))),'),
  ('  harpoonSeekerA(m,dt);','  harpoonRouteStepE(m);harpoonSeekerA(m,dt);'),
  ('aim=terminal?{x:lock.x+lock.vx*(tgo+m.seeker.missedS),y:lock.y+lock.vy*(tgo+m.seeker.missedS)}:pred,','aim=terminal?{x:lock.x+lock.vx*(tgo+m.seeker.missedS),y:lock.y+lock.vy*(tgo+m.seeker.missedS)}:harpoonRouteAimE(m,pred),'),
  ('r.lastResult=null;r.launches.length=0;','r.lastResult=null;r.launches.length=0;r.routeDraft={editing:false,pointsM:[]};'),
  ('function harpoonRestoreA(value){const r=harpoonRuntimeA();','function harpoonRestoreA(value){const r=harpoonRuntimeA();r.routeDraft={editing:false,pointsM:[]};'),
  (old_ui,(HERE/'ui.js').read_text()),
  ('function harpoonDrawCicA(ctx,sym){} // COMPAT_REQUIRED call site; all Harpoon contacts use measured files.','// Prelaunch route drawing is defined with the ship-owned route program above.'),
  ('return {operatorPicture:harpoonOperatorPictureC,knowledgeAudit:',"return {routeDraft:()=>harpoonCopyA(harpoonRuntimeA().routeDraft),routeToggle:harpoonRouteToggleE,\n    routeAdd:(p)=>harpoonRouteAddE(metersToWorld(p.x),metersToWorld(p.y)),\n    operatorPicture:harpoonOperatorPictureC,knowledgeAudit:"),
  ('carrierVelocityMps:{...m.carrierVelocityMps},memory:gate.memory,','carrierVelocityMps:{...m.carrierVelocityMps},memory:gate.memory,routeProgram:gate.routeProgram??null,'),
  ('initialHeading=Math.atan2(axis.y,axis.x),aim=harpoonPredictionA(record.memory,t,record.positionM),','initialHeading=Math.atan2(axis.y,axis.x),aim=record.routeProgram?.pointsM[0]??harpoonPredictionA(record.memory,t,record.positionM),'),
  ("    if(inputMode === 'NAV'){","    if(harpoonRouteEditingE()){\n      harpoonRouteAddE(worldX,worldY);\n    } else if(inputMode === 'NAV'){"),
  ('  _ptrMoved = false;','  _ptrMoved = harpoonRouteEditingE()&&e.isPrimary===false;'),
  ('  if(e.touches.length === 2){\n    const dx = e.touches[0].clientX - e.touches[1].clientX;\n    const dy = e.touches[0].clientY - e.touches[1].clientY;\n    _pinchDist0',
   '  if(e.touches.length === 2){\n    if(harpoonRouteEditingE())_ptrMoved=true;\n    const dx = e.touches[0].clientX - e.touches[1].clientX;\n    const dy = e.touches[0].clientY - e.touches[1].clientY;\n    _pinchDist0'),
  ("deferred:['damageControlFireTimeline'","deferred:['harpoonPrelaunchRouteAndFlight','damageControlFireTimeline'")]
def markup_patches():
 anchor='<div id="harpoonStatusA"'
 return [(anchor,'<button id="harpoonRouteE" class="wep-btn misc" aria-pressed="false" style="width:100%;margin-top:3px">웨이포인트 지정</button>\n          <div id="harpoonRouteNoteE" class="control-deck-note" style="overflow-wrap:anywhere">마지막 점 = 탐색 시작</div>\n          '+anchor)]
def decode(html):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',html,re.S)[1])).decode()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--baseline',type=Path,default=BASE);a=ap.parse_args()
 raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA;html=raw.decode();js=decode(html)
 for old,new in patches():assert js.count(old)==1,(old[:100],js.count(old));js=js.replace(old,new)
 js=js.replace('V48_WIP_HARPOON_D','V48_WIP_HARPOON_E').replace('WIP HARPOON D','WIP HARPOON E')
 body=js.encode();packed=gzip.compress(body,9,mtime=0);m=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S)
 html=html[:m.start(1)]+base64.b64encode(packed).decode()+html[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',html,re.S);rows=json.loads(m[1]);rows[13].update(rawBytes=len(body),gzipBytes=len(packed),sha256=hashlib.sha256(body).hexdigest());html=html[:m.start(1)]+json.dumps(rows,separators=(',',':'))+html[m.end(1):]
 for old,new in markup_patches():assert html.count(old)==1;html=html.replace(old,new)
 html=html.replace('V48_WIP_HARPOON_D','V48_WIP_HARPOON_E').replace('WIP HARPOON D','WIP HARPOON E')
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(html);(a.out.parent/'harpoon-e-main.js').write_bytes(body)
 print(json.dumps({'bytes':a.out.stat().st_size,'sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),'mainSha256':hashlib.sha256(body).hexdigest()}))
if __name__=='__main__':main()
