import json,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright,TimeoutError
sys.path.insert(0,'/workspace/aegis-performance-e/docs/bunkerhill/K')
from browser_i import launch,load
SETUP=r'''()=>{const v=__WIP148_3D_VIEW__,d=__NAVAL_SIM_DIAG__;__WIP125_DIAG__.forcePreSail();const cfg=d.exportOperationalStateV48Wip11A().deployment;Object.assign(cfg,{enemyProfileId:null,allyProfileId:null,targetShip:'NONE',enemyAircraftEnabled:false});__AEGIS_DEPLOYMENT_A__.setDraft(cfg);document.getElementById('wip125DepartBtn').click();d.ciwsB1Closure.setPaused(true);v.c12ApplyPreset('LOW');v.orbit.distance=125;v.orbit.targetY=5;
 const t=window.__DECK_E__={frames:[],anchors:[],cuts:[],draws:0,first:null},find=v.findDamageSurfaceV2,preview=v.previewDamageCutJobC13,draw=v.renderer.render;
 v.findDamageSurfaceV2=function(s,...args){const q=find.call(this,s,...args);t.anchors.push({id:s.id,point:s.p,normal:s.normal,radius:s.radius,hole:s.hole,role:s.impactRole,matched:!!q,mesh:q?.mesh?.name,anchor:q?.point?.toArray()});return q};
 v.previewDamageCutJobC13=function*(g,b){const row={mesh:b.mesh?.name,vertices:g.attributes.position.count,steps:0,start:performance.now(),done:false};t.cuts.push(row);const job=preview.call(this,g,b);try{for(;;){const n=job.next();row.steps++;if(n.done){row.done=true;row.end=performance.now();row.resultVertices=n.value?.attributes.position.count;return n.value}yield n.value}}finally{if(!row.done)job.return()}};
 v.renderer.render=function(...a){t.draws++;const r=draw.apply(this,a);if(t.start){const row={at:performance.now()-t.start,draw:t.draws,stats:{...v.damageBuildStatsV3},revision:v._damageOpeningRevisionPerfD??null,complete:v._damageGeometryRevisionV11??0,audit:v.damageAuditV48Wip03(),cut:t.cuts.at(-1),job:!!v._damageJobV3,quick:v._damageQuickV11,glError:v.renderer.getContext().getError()};t.frames.push(row);if(!t.first&&row.audit.dualHullOpenings)t.first=row}return r};return true}'''
with sync_playwright()as p:
 b=launch(p,True);errors=[];page=load(b,Path('/workspace/aegis-performance-e/Aegis_SIM_v48_WIP_PERF_D.html').read_bytes(),webgl=True,errors=errors)
 page.evaluate(SETUP);page.wait_for_function('__DECK_E__.draws>=3',timeout=60000)
 probe=page.evaluate("()=>{__DECK_E__.start=performance.now();return __NAVAL_SIM_DIAG__.runV48Wip03StructuralProbe({hits:1,label:'Kh-32',xM:12,zM:4,side:'STARBOARD'})}")
 deadline=time.monotonic()+120
 while True:
  try:page.wait_for_function('__DECK_E__.first||(__DECK_E__.frames.length&& !__DECK_E__.frames.at(-1).job)',polling=500,timeout=10000);break
  except TimeoutError:
   row=page.evaluate('({frames:__DECK_E__.frames.length,last:__DECK_E__.frames.at(-1),anchors:__DECK_E__.anchors})');print(json.dumps(row),flush=True)
   if time.monotonic()>deadline:break
 trace=page.evaluate('__DECK_E__');out=Path('/workspace/aegis-performance-e-work/deck-investigation.json');out.write_text(json.dumps({'trace':trace,'probe':probe,'errors':errors},indent=2)+'\n');print(json.dumps({'first':trace['first'],'anchors':trace['anchors'],'cuts':trace['cuts'],'last':trace['frames'][-1] if trace['frames'] else None,'errors':errors}),flush=True);b.close()
