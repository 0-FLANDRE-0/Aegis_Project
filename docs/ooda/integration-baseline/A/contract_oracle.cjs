#!/usr/bin/env node
'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const { chromium } = require('playwright');

const [productPath, url, outputPath] = process.argv.slice(2);
if (!productPath || !url || !outputPath) {
  console.error('usage: contract_oracle.cjs PRODUCT URL OUTPUT');
  process.exit(2);
}
const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');
const stableJson = value => JSON.stringify(value, (_key, item) => item && typeof item === 'object' && !Array.isArray(item)
  ? Object.fromEntries(Object.entries(item).sort(([a], [b]) => a.localeCompare(b))) : item);

async function runOwner(browser, profileIndex) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const consoleErrors = [], pageErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error' && !/favicon\.ico|Failed to load resource.*404/i.test(msg.text())) consoleErrors.push(msg.text());
  });
  page.on('pageerror', error => pageErrors.push(String(error)));
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__AEGIS_SHIP_STARTUP__?.catalog?.().length >= 2, null, { timeout: 120000 });
  const result = await page.evaluate(async index => {
    const catalog = window.__AEGIS_SHIP_STARTUP__.catalog(), own = catalog[index], ally = catalog[index === 0 ? 1 : 0];
    window.__AEGIS_DEPLOYMENT_A__.setDraft({schema:'AEGIS_DEPLOYMENT_MULTI_SHIP_F_1',targetShip:'NONE',enemyProfileId:null,allyProfileId:ally.id,neutralProfileId:null,enemyAircraftEnabled:false,placementSeed:1831565813,allyEmcon:false,enemyEmcon:false});
    window.__AEGIS_SHIP_STARTUP__.select(own.id);await window.__AEGIS_STARTUP_PROMISE__;
    const d=window.__NAVAL_SIM_DIAG__,api=window.__DEFENSE_DECISION_A1__;
    d.setSeed(1831565813);d.setBattlespaceSeed(1831565813);if(!window.__WIP125_DIAG__.confirmDeparture())throw Error('departure failed');d.setSeed(1831565813);
    const ownId=window.__AEGIS_SHIP_STARTUP__.snapshot().entityId,allyId=d.multiShipSnapshotA().ships.find(q=>q.role==='ALLY')?.entityId??null;
    d.tacticalCommandH1(ownId,{enabled:true});if(allyId)d.defenseCommandE(allyId,{mode:'AUTO'});
    const fixture=d.createTerminalAsmFixture({label:'Kh-35U',rangeKm:17,altM:18,speedMps:275});
    d.wip118ResetControl();const beforeControl=d.snapshot(),control=d.wip118ControlNow();d.stepTicks(12);
    const activeInput=api.input(ownId),foreignInput=allyId?api.input(allyId):null,activeDiag=api.diagnostics(ownId),foreignDiag=allyId?api.diagnostics(allyId):null;
    const activeAudit=api.audit(ownId),foreignAudit=allyId?api.audit(allyId):null;
    const saveBefore=JSON.stringify(d.exportOperationalStateV48Wip11A()),rngBefore=d.snapshot().simRngState;
    for(let i=0;i<20;i++){api.input(ownId);if(allyId)api.input(allyId);}
    const saveAfter=JSON.stringify(d.exportOperationalStateV48Wip11A()),rngAfter=d.snapshot().simRngState;
    const freeze=value=>{if(value&&typeof value==='object'&&!Object.isFrozen(value)){for(const child of Object.values(value))freeze(child);Object.freeze(value);}return value;};
    const currentIds=new Set(activeInput.tracks.map(q=>q.trackId)),fresh=structuredClone(activeDiag.lastCommand);
    fresh.inputStep=activeInput.step;fresh.inputRevision=activeInput.revision;fresh.trackOrder=fresh.trackOrder.filter(id=>currentIds.has(id));fresh.priorities=fresh.priorities.filter(q=>currentIds.has(q.trackId));fresh.salvoOverrides=fresh.salvoOverrides.filter(q=>currentIds.has(q.trackId));
    const command=freeze(fresh),clone=()=>structuredClone(command),tests={consumedValidation:activeDiag.lastValidation,valid:api.validate(ownId,command)};
    const ownerMismatch=clone();ownerMismatch.ownerEntityId='FOREIGN_OWNER';tests.ownerMismatch=api.validate(ownId,freeze(ownerMismatch));
    const stale=clone();stale.inputStep--;tests.stale=api.validate(ownId,freeze(stale));
    const staleRevision=clone();staleRevision.inputRevision++;tests.staleRevision=api.validate(ownId,freeze(staleRevision));
    const unknown=clone();unknown.trackOrder=[...unknown.trackOrder,2147483647];tests.unknownTrack=api.validate(ownId,freeze(unknown));
    const duplicate=clone();if(duplicate.trackOrder.length)duplicate.trackOrder.push(duplicate.trackOrder[0]);tests.duplicateTrack=api.validate(ownId,freeze(duplicate));
    const extra=clone();extra.fireNow=true;tests.extraAuthority=api.validate(ownId,freeze(extra));
    tests.mutable=api.validate(ownId,clone());
    if(allyId)tests.crossOwner=api.validate(allyId,command);
    const forbidden=[];const walk=(value,path='$',seen=new WeakSet())=>{if(!value||typeof value!=='object'||seen.has(value))return;seen.add(value);for(const [key,child]of Object.entries(value)){const next=path+'.'+key;if(/(^|_)(truth|truthobject|truthid|renderer|threejs|actualenemy|actualtarget|hostiletruth|faction)(_|$)/i.test(key))forbidden.push(next);walk(child,next,seen);}};walk(activeInput);
    const afterControl=d.snapshot();
    return {own:{id:ownId,profileId:own.id},ally:{id:allyId,profileId:ally.id},fixture,control:{recommendations:control.recommendations.map(q=>({trackId:q.trackId,weapon:q.weapon,salvo:q.salvo,recommendedRounds:q.recommendedRounds,salvoPolicy:q.salvoPolicy}))},
      provider:{schema:api.schema,commandSchema:api.commandSchema,provider:api.provider,mode:api.mode,authority:api.authority,truthUsed:api.truthUsed,rngConsumed:api.rngConsumed,saveFields:api.saveFields},
      active:{input:activeInput,diagnostics:activeDiag,audit:activeAudit},foreign:{input:foreignInput,diagnostics:foreignDiag,audit:foreignAudit},validation:tests,forbidden,
      readOnly:{rngBefore,rngAfter,rngExact:rngBefore===rngAfter,saveBytesBefore:new TextEncoder().encode(saveBefore).length,saveBytesAfter:new TextEncoder().encode(saveAfter).length,saveExact:saveBefore===saveAfter,stepBefore:beforeControl.simStepCounter,stepAfter:afterControl.simStepCounter}};
  }, profileIndex);
  result.browser={consoleErrors,pageErrors};
  await page.close();return result;
}

(async()=>{
  const product=fs.readFileSync(productPath),browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
  try{
    const owners=[];for(const index of [0,1])owners.push(await runOwner(browser,index));
    const payload={schema:'AEGIS_INTEGRATION_BASELINE_CONTRACT_ORACLE_A_1',capturedFrom:{product:productPath.split('/').at(-1),bytes:product.length,sha256:sha256(product),browser:await browser.version(),playwright:require('playwright/package.json').version,fixedSeed:1831565813},owners};
    payload.deterministicDigest=sha256(stableJson(owners));fs.writeFileSync(outputPath,JSON.stringify(payload,null,2)+'\n');
    const summary={owners:owners.length,digest:payload.deterministicDigest,shadowMismatchCount:owners.reduce((n,q)=>n+(q.active.diagnostics.shadowMismatchCount??0)+(q.foreign.diagnostics?.shadowMismatchCount??0),0),forbiddenFields:owners.reduce((n,q)=>n+q.forbidden.length,0),consoleErrors:owners.reduce((n,q)=>n+q.browser.consoleErrors.length+q.browser.pageErrors.length,0)};
    console.log(JSON.stringify(summary));
  }finally{await browser.close();}
})().catch(error=>{console.error(error.stack||error);process.exit(1);});
