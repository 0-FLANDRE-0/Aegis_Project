// TEST ONLY: explicit anonymous component inputs, never natural RF or weapon evidence.
// The fixture exercises native paths. Private prepared ships are NOT world-registered.
window.__TRACK_NATIVE_INGRESS_A__=Object.freeze({async run(){
 const checks={},records={},errors=[],copy=x=>JSON.parse(JSON.stringify(x)),now=()=>simStepCounter*SIM_FIXED_DT;
 const ck=(k,v)=>{checks[k]=!!v;},section=(name,fn)=>{try{records[name]=fn();}catch(e){checks[name+'.completed']=false;errors.push({section:name,error:String(e.stack??e)});}};
 __GB_TEST__.reset(419025);BATTLESPACE_DIAG_BYPASS=true;emconActive=true;
 if(window.__TRACK_A__)__TRACK_A__.clear();
 const initialWorldIds=[...ENGAGEMENT_RUNTIME.ships.keys()];
 const privateShip=label=>{const r=createPreparedShipRuntimeA(resolveShipProfile(ACTIVE_SHIP_RUNTIME.profileId),{entityId:'TRACK_A_FIXTURE_'+label,role:'ALLY',faction:'FRIENDLY'});preparePhysicalShipB(r);prepareObserverC(r);return r;};
 const state=tr=>tr?{id:tr.trackId,source:tr.sensorSource,domain:tr.domain,classification:tr.classification,identity:tr.identity,authority:tr.engagementAuthority,hits:tr.sensorHits,confirmed:!!tr.confirmed,age:tr.sensorAge,x:Array.from(tr._kfX??[]),P:Array.from(tr._kfP??[])}:null;
 const stored=store=>JSON.stringify([...store.values()].map(state));
 const air=(x,y=0,z=50)=>{const dz=z-22,r=Math.hypot(x,y,dz);return {x:metersToWorld(x),y:metersToWorld(y),z,rangeM:r,azRad:Math.atan2(y,x),elRad:Math.atan2(dz,Math.hypot(x,y)),radialMps:0,radialVelSigmaMps:3,rangeSigmaM:15,azSigmaDeg:.1,elSigmaDeg:.1,losUx:x/r,losUy:y/r,losUz:dz/r,sensorXWorld:0,sensorYWorld:0,sensorZM:22,sensorVxMps:0,sensorVyMps:0,sensorVzMps:0,quality:.8,source:'SPY1DV_SEARCH_VOLUME',domainEvidence:{surface:.05,air:.9,missile:.05,background:0}};};
 const surface=(x,y=0)=>{const p={...air(x,y,8),z:8,rangeM:Math.hypot(x,y),source:'SPQ9B_SURFACE_PRECISION',surfaceReferenceZM:8,domainEvidence:{surface:.9,air:.05,missile:.05,background:0}};delete p.elRad;return p;};
 section('offboardOriginalFixture',()=>{const q=offboardFixtureC();for(const[k,v]of Object.entries(q.checks))ck('offboardFixture.'+k,v);return q;});
 section('ownMeasurement',()=>{
  tracks.clear();const p1=air(4000,0,50),p2=air(4000,400,80),a=updateSensorTrackMeasurement(null,p1,{source:p1.source,taskType:'SEARCH_VOLUME'}),b=updateSensorTrackMeasurement(null,p2,{source:p2.source,taskType:'SEARCH_VOLUME'}),ids=[a.trackId,b.trackId];
  const accepted=spq9bAcceptSurfacePlotsWip13B1([surface(4000,0),surface(4000,400)].map(plot=>({plot,pd:.8,panel:0})));
  ck('own.resolvedOneToOne',accepted===2&&tracks.size===2&&ids.every(id=>tracks.has(id)));ck('own.noHeightPriorCollapse',Math.abs(a.z-50)<1&&Math.abs(b.z-80)<1);ck('own.noIdentityOrAuthorityEscalation',[a,b].every(t=>t.identity==='UNKNOWN'&&t.engagementAuthority!=='AUTO_AUTHORIZED'));
  return {accepted,files:[...tracks.values()].map(state)};
 });
 section('npcMeasurement',()=>{
  const r=privateShip('NPC'),o=observerC(r),ownBefore=stored(tracks);observerAcceptPlotsC(r,[air(4000,0,50),air(4000,400,80)]);const ids=[...o.tracks.keys()];observerAcceptPlotsC(r,[surface(4000,0),surface(4000,400)]);
  ck('npc.resolvedOneToOne',o.tracks.size===2&&ids.every(id=>o.tracks.has(id)));ck('npc.privateStore',o.tracks!==tracks&&ownBefore===stored(tracks));ck('npc.noForcedFriend',[...o.tracks.values()].every(t=>t.identity==='UNKNOWN'&&t.engagementAuthority==='WITHHELD'));
  const hits=[...o.tracks.values()].map(t=>t.sensorHits);observerAcceptPlotsC(r,[air(15000,-5000,1200)],{initiate:false});ck('npc.nativeGateReject',o.tracks.size===2&&JSON.stringify(hits)===JSON.stringify([...o.tracks.values()].map(t=>t.sensorHits)));
  const r2=privateShip('NPC_2D'),o2=observerC(r2);observerAcceptPlotsC(r2,[surface(4000)]);const first=[...o2.tracks.keys()][0];observerAcceptPlotsC(r2,[air(4000)]);ck('npc.initial2DThen3DKeepsFile',o2.tracks.size===1&&o2.tracks.has(first));
  return {files:[...o.tracks.values()].map(state),initial2DThen3D:[...o2.tracks.values()].map(state)};
 });
 section('apsContactInput',()=>{
  const h={ownerEntityId:'TRACK_A_FIXTURE_APS',positionM:{x:0,y:0,z:150}},q={mode:'SHORT',originM:{x:0,y:0,z:150},prunedTurn:0,cells:new Map(),contacts:new Map(),cellIndex:new Map(),nextContact:1,stats:{expired:0,candidateDrops:0}},before=stored(tracks);
  const p={positionM:{x:10000,y:0,z:8},covarianceM2:[100,0,0,0,400,0,0,0,16],domainEvidence:{surface:.98,air:.02,missile:0,background:0},measuredAtS:now(),measuredRangeM:Math.hypot(10000,142),measuredAzRad:0,scanOrdinalF:0,rangeExtentM:10,crossExtentM:10,weight:1};
  const out=apsContactStepF(h,q,[p],0),cell=[...q.cells.values()][0];
  ck('aps.nativeContactInputAccepted',q.cells.size===1&&!!cell);ck('aps.surfaceHeightRemainsPrior',cell?.measurement?.positionM.z===8);ck('aps.noPublishedConfirmationClaim',q.contacts.size===0&&out.length===0);ck('aps.canonicalStoreUnchanged',stored(tracks)===before);
  return {fixtureOnly:true,actualFunction:'apsContactStepF',naturalRfPdOrMofNConfirmationNotExercised:true,input:copy(p),cells:q.cells.size,confirmedContacts:q.contacts.size,cell:cell?copy({id:cell.id,mask:cell.mask,confirmed:cell.confirmed,point:cell.point,measurement:cell.measurement}):null};
 });
 section('esm',()=>{
  const r=privateShip('ESM'),o=observerC(r),before=stored(o.tracks);
  // Native ESM context consumes native defense control. Initialize it normally, then
  // detach this private fixture's empty ordnance registry entry before any ingress.
  try{prepareWeaponsD(r);}finally{ENGAGEMENT_RUNTIME.world.entities.navalOrdnanceD?.delete(r.entityId);}
  const p={bearing:.7,bearingSigmaDeg:2,strength:.7,quality:.7,band:'IJ',type:'FIXTURE_SEARCH_RADAR',emitterClass:'SEARCH_RADAR',measuredAtS:now()},q=electronicAcceptPlotsF(r,[p]),contacts=[...r.ew.contacts.values()];
  ck('esm.nativeAccepted',q.ok&&contacts.length===1);ck('esm.noCanonicalPosition',before===stored(o.tracks)&&contacts.every(c=>c.rangeKm===null&&!('x'in c)&&!('y'in c)));return {result:q,contacts:copy(contacts)};
 });
 section('hawklink',()=>{
  const r=privateShip('HAWK'),o=observerC(r),at=now(),p={schema:'AEGIS_OFFBOARD_PLOT_C_1',sourceId:'H1',sequence:1,measuredAtS:at,positionM:{x:120000,y:50000,z:8},covarianceM2:[40000,0,0,0,40000,0,0,0,400],domainEvidence:{surface:.9,air:.1,missile:.1,background:.1}};
  const link=configureOffboardSourceC(r,{sourceId:'H1',connected:true,latencyS:.5}),accepted=ingestOffboardReportC(r,p);drainOffboardC(r);ck('hawk.nativeDelayed',link.ok&&accepted.ok&&o.tracks.size===0);const replay=ingestOffboardReportC(r,p);ck('hawk.replayBlocked',!replay.ok);
  // Actual full fixed ticks advance delivery time; the private receiver is drained explicitly.
  for(let i=0;i<30;i++)simulateFixedTick(SIM_FIXED_DT);drainOffboardC(r);const tr=[...o.tracks.values()][0];ck('hawk.delivered',!!tr&&o.tracks.size===1);if(!tr)throw Error('NO_NATIVE_HAWK_TRACK');
  const age=now()-at;ck('hawk.originalMeasurementTime',tr.observationReportsC.remote.H1.measuredAtS===at&&Math.abs(tr.sensorAge-age)<1e-8);ck('hawk.ageInflatesCovariance',tr._kfP[0]>=p.covarianceM2[0]);
  const hits=tr.sensorHits,count=o.offboard.accepted;configureOffboardSourceC(r,{sourceId:'H1',connected:true,latencyS:0});const again=ingestOffboardReportC(r,{...p,sequence:2});drainOffboardC(r);ck('hawk.repeatedFixNotHit',again.ok&&tr.sensorHits===hits&&o.offboard.accepted===count);
  const own=ACTIVE_SHIP_RUNTIME,oldAt=Math.max(0,now()-.25);configureOffboardSourceC(own,{sourceId:'H2',connected:true,latencyS:0});const ownReport={...p,sourceId:'H2',sequence:1,measuredAtS:oldAt,positionM:{x:150000,y:90000,z:8}},ownResult=ingestOffboardReportC(own,ownReport);drainOffboardC(own);ck('hawk.ownCartesianIngress',ownResult.ok&&[...tracks.values()].some(t=>t.sensorSource==='OFFBOARD_C'&&t.observationReportsC?.remote?.H2?.measuredAtS===oldAt));
  return {privateOwner:r.entityId,report:p,link,accepted,replay,deliveryAt:now(),file:state(tr),remote:copy(tr.observationReportsC.remote),ownReport,ownResult};
 });
 section('network',()=>{
  const r=privateShip('NET'),o=observerC(r),nativeBefore=stored(o.tracks),n=prepareNetworkG(r),P=new Array(36).fill(0);for(let i=0;i<6;i++)P[i*6+i]=i<3?10000:100;
  const p={fileId:31,kind:'TRACK',measuredAtS:Math.max(0,now()-.25),stateAtS:now(),stateM:[20000,9000,1000,0,0,0],covariance:P,domain:'AIR',classification:'AIR',identity:'UNKNOWN',assessment:'MONITOR',bid:{eligible:false,cost:1e6,weapon:null,inFlight:0}};
  ck('network.reportSchemaValid',networkValidateReportG(p,now()));networkAcceptReportG(r,'FIXTURE_SENDER',p);const file=[...n.files.values()][0];if(!file)throw Error('NO_NETWORK_FILE');const before={hits:file.hits,state:copy([...file.sources.values()][0].stateM),covariance:copy([...file.sources.values()][0].covariance)};
  networkAcceptReportG(r,'FIXTURE_SENDER',{...p,identity:'NEUTRAL',assessment:'MONITOR'});const updated=[...file.sources.values()][0];ck('network.repeatStatusOnly',file.hits===before.hits&&JSON.stringify(updated.stateM)===JSON.stringify(before.state)&&JSON.stringify(updated.covariance)===JSON.stringify(before.covariance)&&updated.identity==='NEUTRAL');
  const self={...p,fileId:0,kind:'SELF',stateM:[5000,3000,8,10,5,0],domain:'SURFACE',classification:'SURFACE',identity:'FRIEND'};ck('network.selfSchemaValid',networkValidateReportG(self,now()));networkAcceptReportG(r,'FIXTURE_SENDER',self);networkReconcileG(r);
  ck('network.independentReceivedStore',n.files.size===2&&stored(o.tracks)===nativeBefore);ck('network.noCanonicalFcsAuthority',o.tracks.size===0&&[...n.files.values()].every(f=>f.localTrackId==null));
  // Exercise actual native reconcile candidates and selection with a separately
  // confirmed LOCAL file. These anonymous fixtures are not natural RF evidence.
  for(let hit=0;hit<3;hit++){if(hit)for(let tick=0;tick<15;tick++)simulateFixedTick(SIM_FIXED_DT);observerAcceptPlotsC(r,[air(20000,9000,1000)]);}
  const local=[...o.tracks.values()][0],localBefore=state(local);ck('network.nativeLocalConfirmed',o.tracks.size===1&&!!local?.confirmed&&local.sensorHits>=3);
  networkReconcileG(r);const localAfter=state(local);
  ck('network.nativeReconcileAssigned',!!local&&file.localTrackId===local.trackId);ck('network.reconcileNoCanonicalHitOrAuthorityChange',JSON.stringify(localBefore)===JSON.stringify(localAfter));
  return {directValidatedComponentIngress:true,transportAuthenticationNotExercised:true,initialEmptyCanonicalAssertionsBeforeLocalInsertion:true,nativeReconcile:{localBefore,localAfter,selectedNetworkFile:file.id,localTrackId:file.localTrackId},files:[...n.files.values()].map(f=>({id:f.id,domain:f.domain,hits:f.hits,localTrackId:f.localTrackId,sources:[...f.sources.values()].map(s=>({kind:s.kind,fileId:s.fileId,identity:s.identity,measuredAtS:s.measuredAtS,stateM:s.stateM,covariance:s.covariance}))}))};
 });
 section('isar',()=>{
  const r=privateShip('ISAR'),o=observerC(r),p=surface(4000);observerAcceptPlotsC(r,[p]);const tr=[...o.tracks.values()][0];if(!tr)throw Error('NO_ISAR_POSITION_FILE');configureOffboardSourceC(r,{sourceId:'H1',connected:true,latencyS:0});
  const result={candidates:ISAR_LIBRARY_F2.map(l=>({classId:l.classId,label:l.label,confidence:1/ISAR_LIBRARY_F2.length})),quality:.6,lengthM:155,lengthSigmaM:12,heightsM:new Array(ISAR_F2.featureBins).fill(10),heightSigmaM:3,mastPosition01:.5,mastSigma01:.1,crossResolutionM:3,rangeResolutionM:3,deltaThetaRad:.1};
  const report={schema:'AEGIS_OFFBOARD_ISAR_C_1',sourceId:'H1',sequence:1,measuredAtS:now(),positionM:{x:worldToMeters(tr.x),y:worldToMeters(tr.y),z:8},covarianceM2:[400,0,0,0,400,0,0,0,16],result},before=state(tr),valid=isarReportValidF2(report,now()),accepted=ingestOffboardIsarF2(r,report);drainIsarOffboardF2(r);const after=state(tr);
  ck('isar.nativeValidEvidence',valid&&accepted.ok&&!!tr.isarEvidence);ck('isar.notAnotherPositionHit',JSON.stringify(before)===JSON.stringify(after));ck('isar.noIdentityOrAuthorityPromotion',tr.identity==='UNKNOWN'&&tr.engagementAuthority==='WITHHELD');const replay=ingestOffboardIsarF2(r,report);ck('isar.replayBlocked',!replay.ok);return {valid,accepted,replay,before,after,evidence:copy(tr.isarEvidence)};
 });
 ck('owners.noWorldInsertion',JSON.stringify(initialWorldIds)===JSON.stringify([...ENGAGEMENT_RUNTIME.ships.keys()]));
 ck('core.noSelfTestFailures',(window.__CORE_SELFTEST_FAILURES__??[]).length===0);
 const traceSnapshot=window.__TRACK_A__?__TRACK_A__.snapshot():null;
 return {schema:'AEGIS_TRACK_A_NATIVE_COMPONENT_INGRESS_1',classification:'FIXTURE_ONLY_NOT_NATURAL_RF',naturalRfOrWeaponEvidence:false,sourceOnlyTraceCoverage:['IFF_REPLY','HELO_CONTACT_INPUT','ISAR_INGEST'],coverageNote:'APS contact input is executed with anonymous fixture data; its RF/Pd/M-of-N confirmation are not tested. IFF producer trace remains partial and is not separately stimulated by this helper.',transportAuthenticationNotExercised:true,checks,records,errors,traceSnapshot,pass:Object.values(checks).every(Boolean)&&!errors.length,core:copy(window.__CORE_SELFTEST_FAILURES__??[])};
}});
