import shutil
"""Browser integration and actual antenna-only motion regression."""
from pathlib import Path
import json,sys,base64,time,os
from playwright.sync_api import sync_playwright
src=Path(sys.argv[1]);out=Path(os.environ.get('AEGIS_EVIDENCE_DIR',str(src.resolve().parent/'artifacts'/'bunkerhill')));out.mkdir(parents=True,exist_ok=True)
with sync_playwright()as p:
 b=p.chromium.launch(executable_path=os.environ.get('AEGIS_CHROMIUM_EXECUTABLE') or shutil.which('chromium') or None,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':1440,'height':1000});errors=[];console=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('console',lambda m:console.append(m.text[:500])if m.type=='error'else None)
 page.add_init_script('window.__NAVAL_SIM_SEED__=0x6d2b79f5')
 page.route('https://aegis.test/**',lambda r:r.fulfill(body=src.read_bytes(),content_type='text/html'))
 page.goto('https://aegis.test/candidate?view3d=1',wait_until='domcontentloaded',timeout=90000)
 page.wait_for_selector('#aegisShipConfirmBtn',timeout=60000)
 page.locator('#aegisShipSelect').select_option('CG_52_LATE_TICONDEROGA');page.locator('#aegisShipConfirmBtn').click()
 page.wait_for_function('window.C55Packaging?.ready&&window.__NAVAL_SIM_DIAG__',timeout=90000)
 page.wait_for_function('window.__WIP148_3D_VIEW__?.ready',timeout=120000)
 result=page.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,v=window.__WIP148_3D_VIEW__,checks={},details={};
  d.ciwsB1Closure.setPaused(true);
  checks.coreZero=window.__CORE_SELFTEST_FAILURES__.length===0;details.core=window.__CORE_SELFTEST_FAILURES__;
  checks.profile=(details.profile=d.bunkerProfileAudit()).pass;
  checks.masks=(details.masks=d.bunkerMasksAudit()).pass;
  checks.radars=(details.radars=d.bunkerRadarAudit()).pass;
  checks.renderer=(details.renderer=v.contractAudit()).pass;
  const initial=d.exportOperationalStateV48Wip11A(),saved=structuredClone(initial);
  saved.ship.inventory.closeIn[0].ammo=1421;saved.ship.inventory.closeIn[1].ammo=1337;
  saved.ship.inventory.gunMounts[0].magazine.HE_127_SIM=321;saved.ship.inventory.gunMounts[1].magazine.SAP_127_SIM=213;
  saved.ship.inventory.selectedGunId='mk45a';
  checks.importPreflight=d.validateOperationalStateV48Wip11B(saved).ok;
  if(checks.importPreflight){d.importOperationalStateV48Wip11B(saved);const q=d.exportOperationalStateV48Wip11A();
   checks.independentAmmo=q.ship.inventory.closeIn[0].ammo===1421&&q.ship.inventory.closeIn[1].ammo===1337&&
    q.ship.inventory.gunMounts[0].magazine.HE_127_SIM===321&&q.ship.inventory.gunMounts[1].magazine.SAP_127_SIM===213;
   checks.selectedAftGun=d.wip13b1GunRuntime().hardpointId==='mk45Aft';}
  const invalids=[['wrongProfile',q=>q.profileId='DDG_119_LATE_FLIGHT_IIA'],['duplicateGun',q=>q.ship.inventory.gunMounts[1].id=q.ship.inventory.gunMounts[0].id],
    ['excessAmmo',q=>q.ship.inventory.closeIn[1].ammo=9999],['invalidSparseSlot',q=>q.ship.inventory.vls.fwd[50].col=99],
    ['missingMagazine',q=>delete q.ship.inventory.gunMounts[0].magazine],['wrongRevision',q=>q.profileRevision+='BAD'],['invalidNavTelemetry',q=>q.ship.navigation.swayMps='BAD']];
  details.rejections=[];for(const [name,edit]of invalids){const q=structuredClone(saved);edit(q);const before=d.operationalImportMutationFingerprintV48Wip11B();let rejected=false;
   try{d.importOperationalStateV48Wip11B(q);}catch(_){rejected=true;}const after=d.operationalImportMutationFingerprintV48Wip11B();
   checks[name]=rejected&&JSON.stringify(before)===JSON.stringify(after);details.rejections.push({name,rejected,unchanged:JSON.stringify(before)===JSON.stringify(after)});}
  d.importOperationalStateV48Wip11B(initial);v.syncShipFittings(d.bunkerRenderState());
  const fingerprint=JSON.stringify(d.exportOperationalStateV48Wip11A()),source=v._bunkerAsset.parts.get('CG52_structure_2'),fixed=Array.from(source.geometry.index.array),
    wholeBefore=source.matrixWorld.toArray(),spq=v.spq9bRotor,sps=v.bridgeMasterERotor,qa=spq.quaternion.clone(),qb=sps.quaternion.clone(),st=d.bunkerRenderState();
  st.auxNav.forEach(q=>q.angleRad+=Math.PI/2);v.syncShipFittings(st);v.shipRoot.updateMatrixWorld(true);
  checks.onlyAntennaMoves=spq.quaternion.angleTo(qa)>.5&&sps.quaternion.angleTo(qb)>.5&&JSON.stringify(source.matrixWorld.toArray())===JSON.stringify(wholeBefore);
  checks.fixedTrianglesPreserved=source.geometry.index.count===fixed.length&&Array.from(source.geometry.index.array).every((q,i)=>q===fixed[i]);
  checks.noPhysicsFeedback=fingerprint===JSON.stringify(d.exportOperationalStateV48Wip11A());
  const muzzleRows=[];for(const [azOffset,el]of [[0,0],[.45,.25],[-.8,-.1]]){
    const pose=d.bunkerRenderState();pose.mountInventory.closeIn.forEach((q,i)=>{q.azRelRad=(i===0?1:-1)*Math.PI/2+azOffset;q.elRad=el;});
    v.syncShipFittings(pose);v.shipRoot.updateMatrixWorld(true);
    for(const q of pose.mountInventory.closeIn){const node=v._bunkerAsset.parts.get(q.hardpointId==='phalanx'?'ciwss_pitch':'ciwsp_pitch'),
      mesh=node.children.find(m=>m.isMesh&&!m.userData.lines),p=mesh.geometry.attributes.position;const side=q.hardpointId==='phalanx'?1:-1;
      let far=-Infinity;for(let i=0;i<p.count;i++)far=Math.max(far,p.getZ(i)*side);
      const cap=new v.THREE.Vector3();let n=0;for(let i=0;i<p.count;i++)if(p.getZ(i)*side>far-.002){cap.add(new v.THREE.Vector3(p.getX(i),p.getY(i),p.getZ(i)));n++;}
      cap.multiplyScalar(1/n);node.localToWorld(cap);v.shipRoot.worldToLocal(cap);
      const physical=d.bunkerCiwsMuzzleLocal(q.hardpointId,q.azRelRad,q.elRad),error=Math.hypot(cap.x-physical.x,cap.z-physical.y,cap.y-physical.z);
      muzzleRows.push({id:q.id,az:q.azRelRad,el,errorM:error});}}
  details.muzzles=muzzleRows;checks.sourceMuzzleAligned=muzzleRows.every(q=>q.errorM<.004);
  v.syncShipFittings(d.bunkerRenderState());
  const deflect=spq.position.clone();spq.position.x+=.25;checks.displacedRadarRejected=!v.contractAudit().pass;spq.position.copy(deflect);
  const rpos=v.shipRoot.position.clone(),rquat=v.shipRoot.quaternion.clone();v.shipRoot.position.add(new v.THREE.Vector3(33,4,-21));v.shipRoot.rotateY(.7);
  checks.shipLocalMountInvariant=v.contractAudit().pass;v.shipRoot.position.copy(rpos);v.shipRoot.quaternion.copy(rquat);v.shipRoot.updateMatrixWorld(true);
  const first=[...v.vlsLids],key=first[0][0],lid=v.vlsLids.get(key);v.vlsLids.set(key,first[1][1]);checks.wrongVlsNodeRejected=!v.contractAudit().pass;v.vlsLids.set(key,lid);
  const sourceParent=source.parent;sourceParent.remove(source);checks.missingSourceTrianglesRejected=!v.contractAudit().checks.sourcePreserved;sourceParent.add(source);
  v.syncShipFittings(d.bunkerRenderState());return {checks,details};}''')
 (out/'cg52-integration.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps({'stage':'integration','checks':result['checks'],'errors':errors,'console':console}),flush=True)
 # Verify live scanner phases and independent damage before photographing.
 live=page.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__;document.getElementById('wip125DepartBtn').click();d.ciwsB1Closure.setPaused(true);d.setEmcon(false);
   const check={},phase=()=>d.bunkerAuxNavSnapshot().map(q=>q.angleRad),delta=(a,b)=>Math.abs(Math.atan2(Math.sin(b-a),Math.cos(b-a))),before=phase();
   d.wip13b9StepSurfaceSensors(30,{spy:false,spq:true,bme:true});let after=phase();check.bothScan=after.every((a,i)=>delta(before[i],a)>.5);
   d.wip101SetModuleDamage('AN/SPQ-9',100);let start=phase();d.wip13b9StepSurfaceSensors(30,{spy:false,spq:true,bme:true});after=phase();
   check.spqDamageIndependent=delta(start[0],after[0])<1e-12&&delta(start[1],after[1])>.5;
   d.wip101SetModuleDamage('AN/SPQ-9',0);d.wip101SetModuleDamage('AN/SPS-73',100);start=phase();
   d.wip13b9StepSurfaceSensors(30,{spy:false,spq:true,bme:true});after=phase();
   check.spsDamageIndependent=delta(start[1],after[1])<1e-12&&delta(start[0],after[0])>.5;d.wip101SetModuleDamage('AN/SPS-73',0);
   return {checks:check,phases:after};}''')
 result['checks'].update(live['checks']);result['details']['live']=live
 page.evaluate('''()=>{const v=window.__WIP148_3D_VIEW__,T=v.THREE;v.syncCamera=function(){
   const target=this.shipRoot.localToWorld(new T.Vector3(20.5,28.9,1.3));this.camera.position.copy(target).add(new T.Vector3(18,8,14));this.camera.lookAt(target);};v.render(performance.now());}''')
 cdp=page.context.new_cdp_session(page);capture=cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})
 (out/'cg52-front-mast.png').write_bytes(base64.b64decode(capture['data']))
 result.update({'errors':errors,'console':console,'pass':all(result['checks'].values())and not errors and not console})
 print(json.dumps({'stage':'live-radar','checks':live['checks'],'errors':errors,'console':console}),flush=True)
 (out/'cg52-integration.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));b.close()
 if not result['pass']:raise SystemExit(1)
