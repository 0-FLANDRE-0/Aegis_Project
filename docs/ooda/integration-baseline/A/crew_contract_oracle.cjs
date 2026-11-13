#!/usr/bin/env node
'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const { chromium } = require('playwright');

const [productPath, url, outputPath] = process.argv.slice(2);
if (!productPath || !url || !outputPath) {
  console.error('usage: crew_contract_oracle.cjs PRODUCT URL OUTPUT');
  process.exit(2);
}

const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');
const stableJson = value => JSON.stringify(value, (_key, item) => item && typeof item === 'object' && !Array.isArray(item)
  ? Object.fromEntries(Object.entries(item).sort(([a], [b]) => a.localeCompare(b))) : item);

async function runCase(browser, profileIndex, variant) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => {
    if (message.type() === 'error' && !/favicon\.ico|Failed to load resource.*404/i.test(message.text())) consoleErrors.push(message.text());
  });
  page.on('pageerror', error => pageErrors.push(String(error)));
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__AEGIS_SHIP_STARTUP__?.catalog?.().length >= 2, null, { timeout: 120000 });
  const result = await page.evaluate(async ({ index, fixture }) => {
    const catalog = window.__AEGIS_SHIP_STARTUP__.catalog(), own = catalog[index], ally = catalog[index === 0 ? 1 : 0];
    window.__AEGIS_DEPLOYMENT_A__.setDraft({schema:'AEGIS_DEPLOYMENT_MULTI_SHIP_F_1',targetShip:'NONE',enemyProfileId:null,allyProfileId:ally.id,neutralProfileId:null,enemyAircraftEnabled:false,placementSeed:1831565813,allyEmcon:false,enemyEmcon:false});
    window.__AEGIS_SHIP_STARTUP__.select(own.id);await window.__AEGIS_STARTUP_PROMISE__;
    const d=window.__NAVAL_SIM_DIAG__,api=window.__DEFENSE_DECISION_A1__;
    d.setSeed(1831565813);d.setBattlespaceSeed(1831565813);if(!window.__WIP125_DIAG__.confirmDeparture())throw Error('departure failed');d.setSeed(1831565813);
    const ownId=window.__AEGIS_SHIP_STARTUP__.snapshot().entityId,allyId=d.multiShipSnapshotA().ships.find(q=>q.role==='ALLY')?.entityId??null;
    const pristine=d.exportOperationalStateV48Wip11A(),state=structuredClone(pristine),changed=[];
    if(fixture==='INJURED'){
      const row=state.ship.crew.groups.find(q=>q.role==='COMBAT'&&q.fit>0&&q.teamId==null&&q.pendingTeamId==null&&!q.underCare);
      if(!row)throw Error('COMBAT duty fixture unavailable');
      row.fit-=1;row.injured+=1;changed.push(row.id);
    }else if(fixture==='UNAVAILABLE'){
      for(const row of state.ship.crew.groups.filter(q=>q.role==='OPERATIONS'&&q.fit>0)){row.injured+=row.fit;row.fit=0;changed.push(row.id);}
      state.ship.crew.mode='MISSION_KILLED';state.ship.crew.reason='INTEGRATION_BASELINE_A deterministic fixture';
    }
    const imported=d.importOperationalStateV48Wip11A(state,{resetTransient:true});
    const summarizeSource=()=>{const q=d.v48Wip07CrewState(),department=role=>{const row=q.departments.find(x=>x.role===role);return {duty:row?.duty??null,fit:row?.fit??null,availability:row?.availability??null};};return {mode:q.mode,combatUnavailable:q.combatUnavailable,totals:{total:q.total,fit:q.fit,injured:q.injured,dead:q.dead,evacuated:q.evacuated},departments:{COMBAT:department('COMBAT'),OPERATIONS:department('OPERATIONS')}};};
    const activeInput=api.input(ownId),foreignInput=allyId?api.input(allyId):null,source=summarizeSource(),crew=activeInput.ship.crew;
    const saveBefore=JSON.stringify(d.exportOperationalStateV48Wip11A()),rngBefore=d.snapshot().simRngState,crewBefore=JSON.stringify(crew),sourceBefore=JSON.stringify(source);
    let mutationThrew=false;try{crew.mode='CORRUPT';crew.totals.fit=-999;crew.departments.COMBAT.availability=99;}catch(_error){mutationThrew=true;}
    for(let i=0;i<20;i++){api.input(ownId);if(allyId)api.input(allyId);}
    const crewAfter=api.input(ownId).ship.crew,saveAfter=JSON.stringify(d.exportOperationalStateV48Wip11A()),rngAfter=d.snapshot().simRngState,sourceAfter=JSON.stringify(summarizeSource());
    let command=null,control=null;
    if(fixture!=='UNAVAILABLE'){
      d.setSeed(1831565813);d.setBattlespaceSeed(1831565813);d.tacticalCommandH1(ownId,{enabled:true});
      d.createTerminalAsmFixture({label:'Kh-35U',rangeKm:17,altM:18,speedMps:275});d.wip118ResetControl();control=d.wip118ControlNow();
      const q=api.diagnostics(ownId).lastCommand;
      command={trackOrder:q.trackOrder,priorities:q.priorities,salvoOverrides:q.salvoOverrides,advisoryHold:q.advisoryHold,deferUntilStep:q.deferUntilStep,reason:q.reason};
      control={recommendations:control.recommendations.map(q=>({trackId:q.trackId,weapon:q.weapon,salvo:q.salvo,recommendedRounds:q.recommendedRounds,salvoPolicy:q.salvoPolicy}))};
    }
    return {fixture,profileId:own.id,ownerEntityId:ownId,foreignProfileId:ally.id,foreignOwnerEntityId:allyId,changedCrewIds:changed,imported:!!imported,
      source,activeCrew:crew,foreignCrew:foreignInput?.ship?.crew??null,command,control,
      immutability:{mutationThrew,crewFrozen:Object.isFrozen(crew),totalsFrozen:Object.isFrozen(crew.totals),departmentsFrozen:Object.isFrozen(crew.departments),crewExact:crewBefore===JSON.stringify(crewAfter),sourceExact:sourceBefore===sourceAfter,saveExact:saveBefore===saveAfter,rngExact:rngBefore===rngAfter}};
  }, { index: profileIndex, fixture: variant });
  result.browser={consoleErrors,pageErrors};
  await page.close();return result;
}

function crewShape(crew) {
  const exact=(value,keys)=>value&&JSON.stringify(Object.keys(value).sort())===JSON.stringify([...keys].sort());
  const finiteOrNull=value=>value===null||Number.isFinite(value);
  return !!crew&&exact(crew,['mode','combatUnavailable','totals','departments'])&&exact(crew.totals,['total','fit','injured','dead','evacuated'])&&exact(crew.departments,['COMBAT','OPERATIONS'])&&
    ['COMBAT','OPERATIONS'].every(role=>exact(crew.departments[role],['duty','fit','availability']))&&Object.values(crew.totals).every(finiteOrNull)&&['COMBAT','OPERATIONS'].every(role=>Object.values(crew.departments[role]).every(finiteOrNull));
}

(async()=>{
  const product=fs.readFileSync(productPath),executablePath=process.env.AEGIS_CHROMIUM_EXECUTABLE||(fs.existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined),browser=await chromium.launch({headless:true,...(executablePath?{executablePath}:{}),args:['--no-sandbox','--disable-dev-shm-usage']});
  try{
    const cases=[];for(const index of [0,1])for(const fixture of ['PRISTINE','INJURED','UNAVAILABLE'])cases.push(await runCase(browser,index,fixture));
    const by=(profile,fixture)=>cases.find(q=>q.profileId===profile&&q.fixture===fixture),profiles=[...new Set(cases.map(q=>q.profileId))],checks={};
    for(const profile of profiles){
      const pristine=by(profile,'PRISTINE'),injured=by(profile,'INJURED'),unavailable=by(profile,'UNAVAILABLE');
      checks[profile+'.sourceExact']=stableJson(pristine.activeCrew)===stableJson(pristine.source);
      checks[profile+'.shapeLimited']=cases.filter(q=>q.profileId===profile).every(q=>crewShape(q.activeCrew));
      checks[profile+'.deepFrozen']=cases.filter(q=>q.profileId===profile).every(q=>q.immutability.crewFrozen&&q.immutability.totalsFrozen&&q.immutability.departmentsFrozen);
      checks[profile+'.mutationReadOnly']=cases.filter(q=>q.profileId===profile).every(q=>q.immutability.crewExact&&q.immutability.sourceExact&&q.immutability.saveExact&&q.immutability.rngExact);
      checks[profile+'.injuryTotals']=injured.activeCrew.totals.total===pristine.activeCrew.totals.total&&injured.activeCrew.totals.fit===pristine.activeCrew.totals.fit-1&&injured.activeCrew.totals.injured===pristine.activeCrew.totals.injured+1;
      checks[profile+'.injuryDepartment']=injured.activeCrew.departments.COMBAT.fit===pristine.activeCrew.departments.COMBAT.fit-1&&injured.activeCrew.departments.COMBAT.availability<pristine.activeCrew.departments.COMBAT.availability;
      checks[profile+'.combatUnavailable']=unavailable.activeCrew.combatUnavailable===true&&unavailable.activeCrew.mode==='MISSION_KILLED'&&unavailable.activeCrew.departments.OPERATIONS.fit===0&&unavailable.activeCrew.departments.OPERATIONS.availability===0;
      checks[profile+'.legacyCommandExact']=stableJson(pristine.command)===stableJson(injured.command)&&stableJson(pristine.control)===stableJson(injured.control);
      checks[profile+'.browserClean']=cases.filter(q=>q.profileId===profile).every(q=>q.browser.consoleErrors.length===0&&q.browser.pageErrors.length===0);
      const foreignPristine=by(pristine.foreignProfileId,'PRISTINE');
      checks[profile+'.foreignOwnerExact']=!!foreignPristine&&stableJson(pristine.foreignCrew)===stableJson(foreignPristine.activeCrew);
      checks[profile+'.ownerNotCopied']=pristine.activeCrew.totals.total!==pristine.foreignCrew.totals.total;
    }
    checks.allImportsAccepted=cases.every(q=>q.imported);
    checks.noPersonalOrLocationFields=cases.every(q=>!/(groups|person|roster|location|space|casualtyLog)/i.test(stableJson(q.activeCrew)));
    checks.totalInvariant=cases.every(q=>{const t=q.activeCrew.totals;return t.total!==null&&t.fit+t.injured+t.dead+t.evacuated<=t.total+1e-9;});
    const failed=Object.entries(checks).filter(([,value])=>!value).map(([key])=>key),payload={schema:'AEGIS_INTEGRATION_BASELINE_CREW_CONTRACT_A_1',capturedFrom:{product:productPath.split('/').at(-1),bytes:product.length,sha256:sha256(product),browser:await browser.version(),playwright:require('playwright/package.json').version,fixedSeed:1831565813},checks,cases};
    payload.deterministicDigest=sha256(stableJson({checks,cases}));fs.writeFileSync(outputPath,JSON.stringify(payload,null,2)+'\n');
    console.log(JSON.stringify({checks:Object.keys(checks).length,failed,digest:payload.deterministicDigest}));if(failed.length)process.exitCode=1;
  }finally{await browser.close();}
})().catch(error=>{console.error(error.stack||error);process.exit(1);});
