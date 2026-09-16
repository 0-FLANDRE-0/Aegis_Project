const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP10.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/aft-geometry-wip10';

test.use({ viewport: { width: 1800, height: 1000 } });

test('v48 WIP10 flat flight deck and aft geometry share one physical/render contract', async ({ page }) => {
  test.setTimeout(240_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  if (process.env.THREE_JS_LOCAL && fs.existsSync(process.env.THREE_JS_LOCAL)) {
    await page.route('https://cdn.jsdelivr.net/**/three.min.js', route => route.fulfill({ path: process.env.THREE_JS_LOCAL, contentType: 'text/javascript' }));
  }
  await page.goto(`http://127.0.0.1:4173/${simulator}?view3d=1`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__WIP148_3D_VIEW__?.ready && window.__NAVAL_SIM_DIAG__?.aftGeometryAuditV48Wip10, null, { timeout: 60_000 });

  const result = await page.evaluate(() => {
    const d=window.__NAVAL_SIM_DIAG__,v=window.__WIP148_3D_VIEW__,T=window.THREE,root=v.shipRoot,profile=d.shipProfileV48Wip10();
    root.updateMatrixWorld(true);
    const inv=new T.Matrix4().copy(root.matrixWorld).invert(),p=new T.Vector3();
    const points=object=>{const a=object?.geometry?.getAttribute?.('position'),m=object?new T.Matrix4().multiplyMatrices(inv,object.matrixWorld):null,out=[];if(!a)return out;for(let i=0;i<a.count;i++)out.push(p.fromBufferAttribute(a,i).applyMatrix4(m).toArray());return out;};
    const bounds=object=>{const a=points(object);return a.length?{min:[Math.min(...a.map(q=>q[0])),Math.min(...a.map(q=>q[1])),Math.min(...a.map(q=>q[2]))],max:[Math.max(...a.map(q=>q[0])),Math.max(...a.map(q=>q[1])),Math.max(...a.map(q=>q[2]))]}:null;};
    const deck=root.getObjectByName('WIP10_FLAT_FLIGHT_DECK'),deckY=[...new Set(points(deck).map(q=>Number(q[1].toFixed(6))))];
    const doors=[-1,1].map(side=>bounds(root.getObjectByName(`HANGAR_DOOR_${side}`)));
    v.toggleInteriorTopology();const interior=d.v48Wip06Interior3DAudit();v.toggleInteriorTopology();
    const impact=d.runV48Wip03StructuralProbe({hits:1,label:'Kh-32',xM:-50,zM:3.5,side:'STARBOARD'});
    document.getElementById('shipDetailBtn').click();
    return {
      selftestFailures:window.__CORE_SELFTEST_FAILURES__.slice(),profile,aft:d.aftGeometryAuditV48Wip10(),render:v.contractAudit(),interior,
      deck:{present:!!deck,ys:deckY,bounds:bounds(deck),userData:{...deck?.userData}},doors,
      meshNames:{hangar:!!root.getObjectByName('FLIGHT_IIA_TWIN_HANGAR'),seaRamSupport:!!root.getObjectByName('SEARAM_RAISED_SUPPORT'),aftHouse:!!root.getObjectByName('AFT_SUPPORT_HOUSE'),spgHigh:!!root.getObjectByName('AFT_HIGH_SPG_PEDESTAL'),spgLow:!!root.getObjectByName('AFT_LOW_SPG_PEDESTAL'),mk45:!!root.getObjectByName('MK45_MOD4_5IN_62'),mk45Housing:!!root.getObjectByName('MK45_MOD4_FACETED_HOUSING'),mk45Barrel:!!root.getObjectByName('MK45_MOD4_62CAL_BARREL')},
      mk45Barrel:bounds(root.getObjectByName('MK45_MOD4_62CAL_BARREL')),
      impact:{entry:impact.visual.scars.find(q=>q.impactRole==='ENTRY'),exit:impact.visual.scars.find(q=>q.impactRole==='EXIT')},
      hitCanvas:{visible:document.getElementById('shipDetailPanel').style.display!=='none'}
    };
  });
  await page.waitForFunction(() => {const q=window.__WIP148_3D_VIEW__?.damageAuditV48Wip03?.();return q?.dualHullOpenings&&!q.pending;}, null, { timeout:60_000 });
  result.damage3d = await page.evaluate(() => window.__WIP148_3D_VIEW__.damageAuditV48Wip03());
  result.hitCanvas = await page.evaluate(() => {const c=document.getElementById('shipDetailCanvas'),q=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let painted=0;for(let i=3;i<q.length;i+=4)if(q[i])painted++;return {width:c.width,height:c.height,paintedPixels:painted};});

  const A=result.profile.geometry.aft,H=A.hangar;
  const checks={
    pageLoad:consoleErrors.length===0&&pageErrors.length===0,
    coreSelftests:result.selftestFailures.length===0,
    auditPass:result.aft.pass&&Object.values(result.aft.checks).every(Boolean)&&result.render.pass,
    flatAuthoredDeck:A.flightDeckStations.length===8&&A.flightDeckStations.every(q=>q[2]===A.flightDeckPlaneZM)&&A.flightDeckPlaneZM===4.88,
    flatRenderedDeck:result.deck.present&&result.deck.ys.length===1&&Math.abs(result.deck.ys[0]-(A.flightDeckPlaneZM+.025))<1e-6,
    doorThreshold:result.doors.every(q=>Math.abs(q.min[1]-(H.doorSillZM+.10))<1e-5)&&Math.abs(H.doorSillZM-A.flightDeckPlaneZM)<=.03,
    hangarClearance:H.interiorCeilingZM-H.interiorFloorZM>=H.minClearHeightM&&result.interior.hangarClearance.clear,
    interiorAligned:result.interior.allSpacesRepresented&&result.interior.allPortalsRepresented&&result.interior.allEquipmentRepresented&&result.interior.superstructureContained,
    aftMeshes:Object.values(result.meshNames).every(Boolean),
    mk45Length:result.mk45Barrel.max[0]-result.mk45Barrel.min[0]>5.6&&result.profile.geometry.mk45.exposedBarrelM===7.05,
    drawingsSynced:result.aft.drawings.revision==='V48_WIP10_AFT_GEOMETRY'&&result.aft.drawings.topPolygons>=1000&&result.aft.drawings.sidePolygons>=1000&&result.hitCanvas.paintedPixels>10000,
    entryExitState:result.impact.entry?.p.x===-50&&result.impact.exit?.p.x===-50&&result.impact.entry?.p.y*result.impact.exit?.p.y<0,
    entryExit3d:result.damage3d.dualHullOpenings&&result.damage3d.entry.some(q=>q.actualHole&&q.attached)&&result.damage3d.exit.some(q=>q.actualHole&&q.attached),
    protectionDeferred:result.profile.protection.status==='SCHEMA_ONLY_DEFERRED_TO_WIP11'&&!result.profile.protection.physicsCoupled,
  };
  fs.mkdirSync(artifactDir,{recursive:true});
  fs.writeFileSync(`${artifactDir}/aft-geometry-results.json`,`${JSON.stringify({schema:'AEGIS_AFT_GEOMETRY_BROWSER_V48_WIP10',simulator,simulatorSha256:crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'),checks,consoleErrors,pageErrors,result},null,2)}\n`);
  await page.screenshot({path:`${artifactDir}/aft-geometry-page.png`,fullPage:true});
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key=>[key,true])));
});
