// Pure native-function harness: launch quality edge cases and writer isolation.
const fs=require('fs'),vm=require('vm'),acorn=require('acorn');
const source=fs.readFileSync(process.argv[2],'utf8'),functions={};
function walk(n){if(!n||typeof n!=='object')return;if(n.type==='FunctionDeclaration')(functions[n.id.name]??=[]).push(source.slice(n.start,n.end));for(const[k,v]of Object.entries(n))if(!['start','end'].includes(k)){if(Array.isArray(v))v.forEach(walk);else if(v&&typeof v==='object')walk(v);}}
walk(acorn.parse(source,{ecmaVersion:2022}));const checks={},data={},check=(n,x)=>{checks[n]=!!x;};
const owner={entityId:'OWN',faction:'FRIENDLY',combatSystem:{}},enemy={entityId:'ENEMY',faction:'HOSTILE',combatSystem:{}},friend={entityId:'ALLY',faction:'FRIENDLY',combatSystem:{}};
const P=()=>{const p=new Array(36).fill(0);p[0]=p[7]=400;p[21]=p[28]=4;return p;};
let tr={trackId:1,x:8,y:0,domain:'SURFACE',classification:'SURFACE',confirmed:true,sensorDetected:true,sensorAge:.4,_operatorIdentity:'HOSTILE',_kfP:P(),sensorSource:'OFFBOARD_C',observationReportsC:{localAtS:null,remote:{H1:{measuredAtS:0}}}};
const cfg={minLaunchRangeKm:4,maxLaunchRangeKm:140,maxTrackAgeS:10,seekerActivationRangeM:12000,cruiseSpeedMps:240,acquisitionBasketM:4000};let runtime={tubes:[{id:'T1',loaded:true}],selectedTubeId:'T1',pending:null,releaseCooldownS:0,routeDraft:{pointsM:[]}};
const ctx={console,window:{},simStepCounter:60,SIM_FIXED_DT:1/60,ENGAGEMENT_RUNTIME:{ships:new Map([['OWN',owner],['ENEMY',enemy],['ALLY',friend]])},ACTIVE_SHIP_RUNTIME:owner,selectedLockId:1,
 HARPOON_PROFILE_A:{sim:cfg},SURFACE_MISSILE_ENGAGEMENT_PROFILE_V48_WIP13C4:{fireControl:{maxMeasurementAgeS:10},authority:{manualIdentities:['HOSTILE','TRAINING_TARGET']}},
 tracks:new Map([[1,tr]]),harpoonRuntimeA:()=>runtime,harpoonTubeSpecA:()=>({moduleName:'MK141',muzzle:{x:0,y:0,z:10},axis:{x:1,y:0,z:.5}}),normalizeTrackOperatorIdentityA3:x=>x??'UNKNOWN',
 surfaceSensorContributorSnapshotWip13B9:t=>t.contributors??{},trackLifecycleState:()=> 'FIRM',wip121TargetSupportBlocked:()=>false,
 aircraft:{x:()=>0,y:()=>0},horizDistKm:(x,y,a,b)=>Math.hypot(a-x,b-y),shipEquipmentOfflineV1:()=>false,getModuleDmg:()=>0,
 shipGameFrameV1:()=>({pointToWorld:p=>({...p}),vectorToWorld:p=>({...p})}),maritimeSeaLevelAtSimulationMetersWip13A3:()=>0,
 harpoonMemoryA:t=>({trackId:t.trackId,updatesAfterRelease:false}),attackAuthorityH3:()=>({ok:false,reason:'ATTACK_CAPABILITY_REQUIRED'}),attackFinalGuardH3:()=>({ok:false}),
 harpoonRouteGateE:()=>({ok:true,routeProgram:true}),claimShipMutableRootA:()=>{},surfaceTargetProfileWip13A:id=>id==='CIVILIAN'?{identity:{basis:'PUBLIC_MERCHANT_PROPORTIONS'}}:null};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(require('path').join(__dirname,'engagement.js'),'utf8'),ctx);
for(const name of ['surfaceMissileIdentityPolicyWip13C4','surfaceMissileTrackReadinessWip13C4','harpoonGateA'])vm.runInContext(functions[name].at(-1),ctx);
function gate(options={}){return ctx.harpoonGateA(1,'T1',options);}
const base=gate();check('offboardNoPenalty',base.ok);const sigma=base.predictionSigmaM;
tr.sensorSource='SPQ9';delete tr.observationReportsC;check('nativeOffboardSameCovarianceSameSigma',gate().predictionSigmaM===sigma);
tr.observationReportsC={localAtS:-20,remote:{H1:{measuredAtS:.6}}};tr.sensorSource='OFFBOARD_C';tr.contributors={SPQ9B:{ageS:30}};check('mixedFreshRemoteNotBlockedByOldLocal',gate().ok);delete tr.contributors;
tr.sensorAge=10;check('ageExactly10Allowed',gate().ok);tr.sensorAge=10+1e-6;check('ageAbove10Expired',gate().reason==='SURFACE_TRACK_COAST_EXPIRED');tr.memActive=true;check('expiredMemoryReasonStable',gate().reason==='SURFACE_TRACK_COAST_EXPIRED');tr.memActive=false;tr.sensorAge=.4;
for(const id of ['UNKNOWN','FRIEND','NEUTRAL']){tr._operatorIdentity=id;check('protect'+id,!gate().ok);}tr._operatorIdentity='HOSTILE';
for(const mode of ['AUTO','SEMIAUTO'])check('blocked'+mode,gate({mode}).reason==='MANUAL_SURFACE_AUTHORITY_REQUIRED');check('blockedAutomaticTubeDoesNotMeanAuthority',gate({automatic:true}).reason==='MANUAL_SURFACE_AUTHORITY_REQUIRED');check('forgedAttackTokenRejected',gate({attackH3:{}}).reason==='ATTACK_CAPABILITY_REQUIRED');
tr.x=3;check('minimumRangePreserved',gate().reason==='SURFACE_TARGET_OUTSIDE_WEAPON_ENVELOPE');tr.x=141;check('maximumRangePreserved',gate().reason==='SURFACE_TARGET_OUTSIDE_WEAPON_ENVELOPE');tr.x=8;
ctx.getModuleDmg=()=>75;check('launcherDamagePreserved',gate().reason==='MK141_LAUNCHER_DAMAGED');ctx.getModuleDmg=()=>0;ctx.shipEquipmentOfflineV1=()=>true;check('equipmentPreserved',gate().reason==='SHIP_EQUIPMENT_OFFLINE');ctx.shipEquipmentOfflineV1=()=>false;
tr._kfP[0]=4000000;tr._kfP[7]=4000000;check('basket2SigmaRejects',gate().reason==='INS_PREDICTION_BASKET_INSUFFICIENT');tr._kfP=P();
check('mixedComposition',ctx.trackCompositionF1(tr)==='MIXED');tr.identificationEvidence='OPERATOR_ONLY';ctx.harpoonJournalReleaseF1(owner,{id:1},{trackId:1,predictionSigmaM:sigma,rangeKm:8},tr);ctx.harpoonJournalFinishF1({ownerEntityId:'OWN',id:1},'NAVAL_CONTACT',{shipRuntimeD:enemy});check('actualEnemyHit',ctx.harpoonJournalSnapshotF1().records[0].termination.hitCategory==='HOSTILE');
ctx.harpoonJournalReleaseF1(owner,{id:2},{trackId:1},tr);ctx.harpoonJournalFinishF1({ownerEntityId:'OWN',id:2},'NAVAL_CONTACT',{shipRuntimeD:friend});check('actualFriendlyHit',ctx.harpoonJournalSnapshotF1().records[1].termination.hitCategory==='FRIENDLY');
for(const [id,reason]of [[3,'SELF_DESTRUCT'],[4,'SEA_IMPACT'],[5,'INTERCEPTED']]){ctx.harpoonJournalReleaseF1(owner,{id},{trackId:1},tr);ctx.harpoonJournalFinishF1({ownerEntityId:'OWN',id},reason);}
let rows=ctx.harpoonJournalSnapshotF1().records;check('selfDestructRecorded',rows[2].termination.result==='SELF_DESTRUCT');check('seaLostNone',rows[3].termination.result==='LOST'&&rows[3].termination.hitCategory==='NONE');check('interceptedLostNone',rows[4].termination.result==='LOST'&&rows[4].termination.hitCategory==='NONE');
ctx.harpoonJournalFinishF1({ownerEntityId:'OWN',id:1},'SEA_IMPACT');check('terminationIdempotent',ctx.harpoonJournalSnapshotF1().records[0].termination.hitCategory==='HOSTILE');
for(let id=6;id<100;id++)ctx.harpoonJournalReleaseF1(owner,{id},{trackId:1},tr);rows=ctx.harpoonJournalSnapshotF1().records;check('bounded64',rows.length===64&&rows[0].missileId===36);rows[0].operatorIdentity='POISON';check('detachedJournal',ctx.harpoonJournalSnapshotF1().records[0].operatorIdentity==='HOSTILE');ctx.harpoonJournalResetF1();check('lifecycleReset',ctx.harpoonJournalSnapshotF1().records.length===0);
// The entire reader surface is fixed and diagnostic-only. AST owner search, not a loose substring count.
const journalReaders=Object.keys(functions).filter(k=>functions[k].some(s=>/harpoonJournalSnapshotF1\(|harpoonJournalTextF1\(/.test(s))&&!k.startsWith('harpoonJournal'));
check('noTacticalJournalReaders',journalReaders.length===0);check('flightFunctionsNeverReadJournal',functions.harpoonFlightStepA.every(s=>!s.includes('Journal')&&!s.includes('identificationEvidence')));check('noDatalinkInFlight',functions.harpoonMemoryA.every(s=>s.includes('updatesAfterRelease:false')));
const result={mainSha256:require('crypto').createHash('sha256').update(source).digest('hex'),pass:Object.values(checks).every(Boolean),checks,data:{nearSigmaM:sigma,journalReaders}};fs.mkdirSync(process.argv[3],{recursive:true});fs.writeFileSync(process.argv[3]+'/policy.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({pass:result.pass,checks:Object.keys(checks).length,failed:Object.keys(checks).filter(k=>!checks[k])}));process.exit(result.pass?0:1);
