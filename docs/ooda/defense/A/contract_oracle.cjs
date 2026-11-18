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

async function run(browser, profileIndex) {
  const page = await browser.newPage({ viewport:{ width:1280, height:720 } });
  const consoleErrors=[], pageErrors=[];
  page.on('console', m => { if (m.type()==='error' && !/favicon\.ico|404/i.test(m.text())) consoleErrors.push(m.text()); });
  page.on('pageerror', e => pageErrors.push(String(e)));
  await page.goto(url,{waitUntil:'domcontentloaded',timeout:120000});
  await page.waitForFunction(()=>window.__AEGIS_SHIP_STARTUP__?.catalog?.().length>=2,null,{timeout:120000});
  const result=await page.evaluate(async index=>{
    const catalog=window.__AEGIS_SHIP_STARTUP__.catalog(),own=catalog[index],ally=catalog[index===0?1:0];
    window.__AEGIS_DEPLOYMENT_A__.setDraft({schema:'AEGIS_DEPLOYMENT_MULTI_SHIP_F_1',targetShip:'NONE',enemyProfileId:null,allyProfileId:ally.id,neutralProfileId:null,enemyAircraftEnabled:false,placementSeed:481801,allyEmcon:false,enemyEmcon:false});
    window.__AEGIS_SHIP_STARTUP__.select(own.id);await window.__AEGIS_STARTUP_PROMISE__;const d=window.__NAVAL_SIM_DIAG__,api=window.__DEFENSE_DECISION_A1__;d.setSeed(481801);d.setBattlespaceSeed(481801);if(!window.__WIP125_DIAG__.confirmDeparture())throw Error('departure failed');
    const exported=d.exportOperationalStateV48Wip11A(),validation=d.validateOperationalStateV48Wip11B(exported),ownId=window.__AEGIS_SHIP_STARTUP__.snapshot().entityId,allyRow=exported.fleet.ships.find(q=>q.role==='ALLY'),selfTest=api.selfTest();
    const legacy=structuredClone(exported);delete legacy.ship.defenseOodaA;for(const q of legacy.fleet.ships)delete q.defenseOodaA;const legacyValidation=d.validateOperationalStateV48Wip11B(legacy);
    const invalid=structuredClone(exported),s=invalid.ship.defenseOodaA;s.queueSequence=2;s.rows=[{trackId:7,sequence:1,phase:'OBSERVE',remainingSteps:12,slot:0},{trackId:7,sequence:2,phase:'OBSERVE',remainingSteps:12,slot:1}];const invalidValidation=d.validateOperationalStateV48Wip11B(invalid),before=JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());let rejected=false;try{d.importOperationalStateV48Wip11B(invalid);}catch(_e){rejected=true;}const after=JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());
    const round=d.importOperationalStateV48Wip11B(exported),afterRound=d.exportOperationalStateV48Wip11A();
    return {own:{profileId:own.id,ownerEntityId:ownId,state:exported.ship.defenseOodaA,view:api.ooda(ownId)},ally:{profileId:ally.id,ownerEntityId:allyRow?.entityId??null,state:allyRow?.defenseOodaA??null,view:allyRow?api.ooda(allyRow.entityId):null},provider:{provider:api.provider,mode:api.mode,saveFields:api.saveFields},selfTest,validation,legacy:{validation:legacyValidation,migrations:legacyValidation.migrations??[]},invalid:{validation:invalidValidation,rejected,zeroMutation:before===after},roundTrip:{validation:round.validation,stateExact:JSON.stringify(afterRound.ship.defenseOodaA)===JSON.stringify(exported.ship.defenseOodaA)}};
  },profileIndex);
  await page.close();return {result,consoleErrors,pageErrors};
}

(async()=>{
  const product=fs.readFileSync(productPath),executablePath=process.env.AEGIS_CHROMIUM_EXECUTABLE||(fs.existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined),browser=await chromium.launch({headless:true,...(executablePath?{executablePath}:{}),args:['--no-sandbox','--disable-dev-shm-usage']});
  try{const owners=[];for(const i of [0,1])owners.push(await run(browser,i));const checks={owners:owners.length===2,noBrowserErrors:owners.every(q=>!q.consoleErrors.length&&!q.pageErrors.length),selfTest:owners.every(q=>q.result.selfTest.pass),modeOff:owners.every(q=>q.result.provider.provider==='LEGACY_H1'&&q.result.provider.mode==='OFF'&&q.result.provider.saveFields===1),profiles:owners.every(q=>q.result.own.state?.profileId===q.result.own.profileId&&q.result.ally.state?.profileId===q.result.ally.profileId),ownerIsolation:owners.every(q=>q.result.own.state.ownerEntityId!==q.result.ally.state.ownerEntityId),valid:owners.every(q=>q.result.validation.ok),legacyMigration:owners.every(q=>q.result.legacy.validation.ok&&q.result.legacy.migrations.filter(m=>String(m.id).startsWith('LEGACY_DEFENSE_OODA_A')).length===2),invalidRejected:owners.every(q=>!q.result.invalid.validation.ok&&q.result.invalid.rejected&&q.result.invalid.zeroMutation),roundTrip:owners.every(q=>q.result.roundTrip.validation.ok&&q.result.roundTrip.stateExact)};const payload={schema:'AEGIS_DEFENSE_OODA_A_CONTRACT_ORACLE_1',product:{file:productPath.split('/').at(-1),bytes:product.length,sha256:sha256(product)},checks,owners};payload.pass=Object.values(checks).every(Boolean);fs.writeFileSync(outputPath,JSON.stringify(payload,null,2)+'\n');console.log(JSON.stringify({pass:payload.pass,checks}));if(!payload.pass)process.exitCode=1;}finally{await browser.close();}
})().catch(e=>{console.error(e.stack||e);process.exit(1);});
