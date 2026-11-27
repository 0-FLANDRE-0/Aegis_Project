#!/usr/bin/env node
'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const { chromium } = require('playwright');

const [productPath, url, outputPath] = process.argv.slice(2);
if (!productPath || !url || !outputPath) {
  console.error('usage: active_oracle.cjs PRODUCT URL OUTPUT');
  process.exit(2);
}
const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');
const stable = value => JSON.stringify(value, (_key, item) => item && typeof item === 'object' && !Array.isArray(item)
  ? Object.fromEntries(Object.entries(item).sort(([a], [b]) => a.localeCompare(b))) : item);
const command = q => q ? {
  provider:q.provider, ownerEntityId:q.ownerEntityId, inputStep:q.inputStep,
  inputRevision:q.inputRevision, trackOrder:q.trackOrder,
  priorityTrackIds:(q.priorities??[]).map(x=>x.trackId),
  salvoOverrides:q.salvoOverrides, advisoryHold:q.advisoryHold,
  deferUntilStep:q.deferUntilStep, reason:q.reason,
} : null;
const diagnostics = q => q ? {
  provider:q.provider, mode:q.mode, builds:q.builds,
  shadowComparisons:q.shadowComparisons,
  allowedShadowDifferenceCount:q.allowedShadowDifferenceCount,
  shadowMismatchCount:q.shadowMismatchCount,
  validationFailures:q.validationFailures, rngMismatchCount:q.rngMismatchCount,
  truthAuditFailures:q.truthAuditFailures, lastStep:q.lastStep,
  lastCommand:command(q.lastCommand),
} : null;
function deterministicView(scenes) {
  return scenes.map(scene => ({
    profileIndex:scene.result.profileIndex,
    own:scene.result.own, ally:scene.result.ally, provider:scene.result.provider,
    samples:scene.result.samples.map(q=>({
      step:q.step, ownTrackIds:q.ownInput?.trackIds, allyTrackIds:q.allyInput?.trackIds,
      ownOoda:q.ownOoda, allyOoda:q.allyOoda,
      ownDiagnostics:diagnostics(q.ownDiagnostics), allyDiagnostics:diagnostics(q.allyDiagnostics),
      interceptorCount:q.interceptorCount, ownFireCount:q.ownFireCount,
      allyFireCount:q.allyFireCount,
    })),
    manualHold:scene.result.manualHold,
    engineSelfTest:scene.result.engineSelfTest,
    contractSelfTest:scene.result.contractSelfTest,
    localDefense:scene.result.localDefense,
  }));
}
function reportScene(scene) {
  const ooda=q=>q?{schema:q.schema,revision:q.revision,ownerEntityId:q.ownerEntityId,profileId:q.profileId,phase:q.phase,capacity:q.capacity,queueLength:q.queueLength,usedSlots:q.usedSlots,totalSlots:q.totalSlots,nextReadyStep:q.nextReadyStep,rows:q.rows.map(r=>({trackId:r.trackId,sequence:r.sequence,phase:r.phase,remainingSteps:r.remainingSteps,slot:r.slot,readyStep:r.readyStep})),lastCommand:q.lastCommand,diagnostics:q.diagnostics,migration:q.migration}:null;
  const r=scene.result;
  return {consoleErrors:scene.consoleErrors,pageErrors:scene.pageErrors,result:{...r,
    samples:r.samples.map(q=>({...q,ownInput:q.ownInput?{...q.ownInput,tracks:undefined}:null,allyInput:q.allyInput?{...q.allyInput,tracks:undefined}:null,ownOoda:ooda(q.ownOoda),allyOoda:ooda(q.allyOoda),ownDiagnostics:diagnostics(q.ownDiagnostics),allyDiagnostics:diagnostics(q.allyDiagnostics)})),
    engineSelfTest:{schema:r.engineSelfTest.schema,pass:r.engineSelfTest.pass,checks:r.engineSelfTest.checks,repeatDigest:r.engineSelfTest.repeatDigest},
    contractSelfTest:{schema:r.contractSelfTest.schema,pass:r.contractSelfTest.pass,checks:r.contractSelfTest.checks},
    localDefense:{pass:r.localDefense.pass,checks:r.localDefense.checks},
  }};
}

async function runScene(browser, profileIndex, exerciseUi) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => {
    if (message.type() === 'error' && !/favicon\.ico|Failed to load resource.*404/i.test(message.text())) consoleErrors.push(message.text());
  });
  page.on('pageerror', error => pageErrors.push(String(error)));
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__AEGIS_SHIP_STARTUP__?.catalog?.().length >= 2, null, { timeout: 120000 });
  const result = await page.evaluate(async ({index, exerciseUi}) => {
    const catalog=window.__AEGIS_SHIP_STARTUP__.catalog(),own=catalog[index],ally=catalog[index===0?1:0],seed=481803;
    window.__AEGIS_DEPLOYMENT_A__.setDraft({schema:'AEGIS_DEPLOYMENT_MULTI_SHIP_F_1',targetShip:'NONE',enemyProfileId:null,allyProfileId:ally.id,neutralProfileId:null,enemyAircraftEnabled:false,placementSeed:seed,allyEmcon:false,enemyEmcon:false});
    window.__AEGIS_SHIP_STARTUP__.select(own.id);await window.__AEGIS_STARTUP_PROMISE__;
    const d=window.__NAVAL_SIM_DIAG__,api=window.__DEFENSE_DECISION_A1__;
    d.setSeed(seed);d.setBattlespaceSeed(seed);if(!window.__WIP125_DIAG__.confirmDeparture())throw Error('departure failed');
    d.ciwsB1Closure.setPaused(true);
    const ownId=window.__AEGIS_SHIP_STARTUP__.snapshot().entityId,allyId=d.multiShipSnapshotA().ships.find(q=>q.role==='ALLY')?.entityId??null;
    d.tacticalCommandH1(ownId,{enabled:true});d.wip119SetMode('AUTO');if(allyId)d.defenseCommandE(allyId,{mode:'AUTO'});
    const uiStateBefore=JSON.stringify({ships:api.ships(),ooda:api.ooda(ownId),diag:api.diagnostics(ownId)});
    const button=document.getElementById('defenseOodaStatusA'),dialog=document.getElementById('defenseOodaStatusDialogA');
    if(exerciseUi)button?.click();
    const ui={button:!!button,dialog:!!dialog,opened:!!dialog?.open,text:document.getElementById('defenseOodaStatusTextA')?.textContent??'',apiText:api.statusText?.()??''};
    if(dialog?.open)dialog.querySelector('button')?.click();
    const uiStateAfter=JSON.stringify({ships:api.ships(),ooda:api.ooda(ownId),diag:api.diagnostics(ownId)});ui.readOnly=uiStateBefore===uiStateAfter;
    const fixture=d.createTerminalAsmFixture({label:'Kh-35U',rangeKm:24,bearingDeg:0,altM:25,speedMps:260}),sampleSteps=[0,12,36,60,84,120,180,240],samples=[];
    const inputSummary=input=>input?{ownerEntityId:input.ownerEntityId,profileId:input.profileId,step:input.step,revision:input.revision,mode:input.mode,trackIds:input.tracks.map(q=>q.trackId),tracks:input.tracks.map(q=>({trackId:q.trackId,authority:q.identification?.engagementAuthority,ageS:q.measurement?.ageS,fcsSource:q.network?.fcsSource,sourceCount:q.network?.sources?.length??0}))}:null;
    const fireCounts=()=>{const s=d.defenseSnapshotE().ships??[],row=id=>s.find(q=>q.entityId===id);return {own:row(ownId)?.autonomy?.fireLog?.length??0,ally:row(allyId)?.autonomy?.fireLog?.length??0};};
    for(const targetStep of sampleSteps){const previous=samples.at(-1)?.step??0;if(targetStep>previous)d.stepTicks(targetStep-previous);const f=fireCounts();samples.push({step:targetStep,ownInput:inputSummary(api.input(ownId)),allyInput:inputSummary(api.input(allyId)),ownOoda:api.ooda(ownId),allyOoda:api.ooda(allyId),ownDiagnostics:api.diagnostics(ownId),allyDiagnostics:api.diagnostics(allyId),interceptorCount:d.interceptorAudit().length,ownFireCount:f.own,allyFireCount:f.ally});}
    const firstReady=side=>samples.find(q=>q[side]?.phase==='READY')?.step??null,firstRelease=samples.find(q=>q.interceptorCount>0)?.step??null;
    const final=samples.at(-1),allyTrack=final.allyInput?.tracks?.[0]??null;
    const networkProbe=allyId&&allyTrack?d.networkVlsGateProbeG(allyId,allyTrack.trackId,{weapon:'ESSM'}):null;
    d.wip119ResetAutonomy();d.wip119SetMode('MANUAL');d.createTerminalAsmFixture({label:'Kh-35U',rangeKm:15,altM:15,speedMps:260});const beforeManual=d.interceptorAudit().length;d.wip119AutonomyTick(true);d.stepTicks(12);const afterManual=d.interceptorAudit().length;
    const beforeHold=fireCounts().ally,holdResult=allyId?d.defenseCommandE(allyId,{mode:'HOLD'}):null;d.stepTicks(12);const afterHold=fireCounts().ally;
    return {profileIndex:index,own:{id:ownId,profileId:own.id},ally:{id:allyId,profileId:ally.id},provider:{provider:api.provider,mode:api.mode,authority:api.authority,truthUsed:api.truthUsed,rngConsumed:api.rngConsumed},fixture,ui,samples,timing:{firstOwnReady:firstReady('ownOoda'),firstAllyReady:firstReady('allyOoda'),firstRelease},networkProbe,manualHold:{manualMissileDelta:afterManual-beforeManual,holdResult,foreignFireDelta:afterHold-beforeHold},engineSelfTest:api.engineSelfTest(),contractSelfTest:api.selfTest(),localDefense:d.localDefenseSelfTestH4A(),audits:[api.audit(ownId),api.audit(allyId)]};
  }, {index:profileIndex, exerciseUi});
  await page.close();
  return {result,consoleErrors,pageErrors};
}

function sceneChecks(scene) {
  const r=scene.result,final=r.samples.at(-1),owners=[['own',final.ownInput,final.ownOoda,final.ownDiagnostics],['ally',final.allyInput,final.allyOoda,final.allyDiagnostics]],commandKeys=['advisoryHold','deferUntilStep','inputRevision','inputStep','ownerEntityId','priorities','provider','reason','salvoOverrides','schema','trackOrder'];
  const beforeOwnReady=r.samples.filter(q=>r.timing.firstOwnReady==null||q.step<r.timing.firstOwnReady);
  return {
    activeProvider:r.provider.provider==='DEFENSE_OODA_A'&&r.provider.mode==='ACTIVE',
    advisoryOnly:r.provider.authority==='ADVISORY_ONLY'&&!r.provider.truthUsed&&!r.provider.rngConsumed,
    bothOwnersReady:owners.every(([_name,input,ooda,diag])=>input&&ooda?.phase==='READY'&&ooda.diagnostics.evaluated>=1&&diag?.builds>0),
    ownerLocal:owners.every(([_name,input,ooda])=>input.ownerEntityId===ooda.ownerEntityId&&input.profileId===ooda.profileId)&&final.ownOoda.ownerEntityId!==final.allyOoda.ownerEntityId,
    actualUsesOoda:owners.every(([_name,_input,_ooda,diag])=>diag.lastCommand?.provider==='DEFENSE_OODA_A'),
    noUnauthorizedReleaseBeforeReady:beforeOwnReady.every(q=>q.interceptorCount===0)&&r.timing.firstRelease!==null&&r.timing.firstRelease>=r.timing.firstOwnReady,
    noForbiddenMismatch:owners.every(([_name,_input,ooda,diag])=>diag.shadowMismatchCount===0&&diag.validationFailures===0&&diag.rngMismatchCount===0&&diag.truthAuditFailures===0&&ooda.diagnostics.fallback===0&&ooda.diagnostics.rejected===0),
    currentTrackOnly:owners.every(([_name,input,ooda])=>{const ids=new Set(input.trackIds);return ooda.rows.every(q=>ids.has(q.trackId));}),
    commandSchemaOnly:owners.every(([_name,_input,_ooda,diag])=>Object.keys(diag.lastCommand??{}).sort().join('|')===commandKeys.join('|')),
    manualHoldNoLaunch:r.manualHold.manualMissileDelta===0&&r.manualHold.foreignFireDelta===0&&r.manualHold.holdResult?.ok===true,
    networkGatePreserved:r.networkProbe===null||typeof r.networkProbe?.ok==='boolean',
    readOnlyUi:r.ui.button&&r.ui.dialog&&r.ui.readOnly&&r.ui.apiText.includes('DEFENSE_OODA_A')&&(!r.ui.opened||r.ui.text.includes('provider')),
    engineSelfTest:r.engineSelfTest.pass===true, contractSelfTest:r.contractSelfTest.pass===true,
    localCiwsIndependent:r.localDefense.pass===true,
    auditClean:r.audits.every(q=>q&&q.forbiddenPath===null&&q.rngMismatchCount===0&&q.validationFailures===0&&!q.portOwnsSafety&&!q.portOwnsExecution&&!q.portOwnsImmediateCiws),
    noBrowserErrors:scene.consoleErrors.length===0&&scene.pageErrors.length===0,
  };
}

(async()=>{
  const product=fs.readFileSync(productPath),executablePath=process.env.AEGIS_CHROMIUM_EXECUTABLE||(fs.existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined),browser=await chromium.launch({headless:true,...(executablePath?{executablePath}:{}),args:['--no-sandbox','--disable-dev-shm-usage']});
  try {
    const first=[],second=[];for(const index of [0,1])first.push(await runScene(browser,index,true));for(const index of [0,1])second.push(await runScene(browser,index,false));
    const checks={scenes:first.every(scene=>Object.values(sceneChecks(scene)).every(Boolean)),repeatExact:stable(deterministicView(first))===stable(deterministicView(second)),profiles:first.map(q=>q.result.own.profileId).sort().join('|')==='CG_52_LATE_TICONDEROGA|DDG_119_LATE_FLIGHT_IIA'};
    const payload={schema:'AEGIS_DEFENSE_OODA_A_ACTIVE_ORACLE_1',product:{file:productPath.split('/').at(-1),bytes:product.length,sha256:sha256(product)},browser:await browser.version(),playwright:require('playwright/package.json').version,seed:481803,checks,sceneChecks:first.map(sceneChecks),scenes:first.map(reportScene),repeatDigest:sha256(Buffer.from(stable(deterministicView(second))))};
    payload.pass=Object.values(checks).every(Boolean);fs.writeFileSync(outputPath,JSON.stringify(payload,null,2)+'\n');console.log(JSON.stringify({pass:payload.pass,checks,sceneChecks:payload.sceneChecks}));if(!payload.pass)process.exitCode=1;
  } finally { await browser.close(); }
})().catch(error=>{console.error(error.stack||error);process.exit(1);});
