const { chromium } = require('@playwright/test');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const repo = path.resolve(__dirname, '..');
const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP12C.html';
const outDir = path.resolve(process.env.ARTIFACT_DIR || path.join(repo, 'artifacts/wip11-visual'));
const threeLocal = process.env.THREE_JS_LOCAL || '/tmp/three.min.js';

const waitForServer = async url => {
  for (let i = 0; i < 80; i++) {
    try { if ((await fetch(url)).ok) return; } catch {}
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error(`local server did not start: ${url}`);
};

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const server = spawn('python3', ['-m', 'http.server', '4173'], { cwd: repo, stdio: ['ignore', 'pipe', 'pipe'] });
  let serverLog = '';
  server.stdout.on('data', chunk => { serverLog += chunk; });
  server.stderr.on('data', chunk => { serverLog += chunk; });
  let browser;
  try {
    await waitForServer('http://127.0.0.1:4173/');
    browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
    const page = await browser.newPage({ viewport: { width: 1800, height: 1000 }, deviceScaleFactor: 1 });
    const consoleErrors = [], pageErrors = [];
    page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
    page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
    if (fs.existsSync(threeLocal)) {
      await page.route('https://cdn.jsdelivr.net/**/three.min.js', route => route.fulfill({ path: threeLocal, contentType: 'text/javascript' }));
    }
    await page.goto(`http://127.0.0.1:4173/${simulator}?view3d=1`, { waitUntil: 'load', timeout: 45_000 });
    await page.waitForFunction(() => window.__WIP148_3D_VIEW__?.ready === true, null, { timeout: 60_000 });
    await page.addStyleTag({ content: 'body>*:not(#external3DView):not(script):not(style){visibility:hidden!important}#external3DView,#external3DView *{visibility:visible!important}.external3d-toolbar,.external3d-help,.external3d-mini-cic,.external3d-msl-status,.external3d-loading{display:none!important}' });
    await page.evaluate(() => {
      const v=window.__WIP148_3D_VIEW__,T=window.THREE;
      v.scene.fog=null;v.scene.background=new T.Color(0x7392a0);if(v.water)v.water.visible=false;if(v.terrainLayer)v.terrainLayer.visible=false;
      const hemi=new T.HemisphereLight(0xffffff,0x52636b,2.7),sun=new T.DirectionalLight(0xffffff,3.2);sun.position.set(80,130,95);v.scene.add(hemi,sun);
      if(v.renderer){v.renderer.toneMappingExposure=1.65;v.renderer.setClearColor(0x7392a0,1);}
    });

    const inspection = await page.evaluate(() => {
      const v = window.__WIP148_3D_VIEW__, T = window.THREE, root = v.shipRoot;
      root.updateMatrixWorld(true);
      const rootInverse = new T.Matrix4().copy(root.matrixWorld).invert();
      const localPoints = object => {
        const attr = object.geometry?.getAttribute?.('position');
        if (!attr) return [];
        const matrix = new T.Matrix4().multiplyMatrices(rootInverse, object.matrixWorld), p = new T.Vector3(), out = [];
        for (let i = 0; i < attr.count; i++) out.push(p.fromBufferAttribute(attr, i).applyMatrix4(matrix).toArray());
        return out;
      };
      const bounds = object => {
        const pts = localPoints(object);
        return pts.length ? { min: [Math.min(...pts.map(p => p[0])), Math.min(...pts.map(p => p[1])), Math.min(...pts.map(p => p[2]))], max: [Math.max(...pts.map(p => p[0])), Math.max(...pts.map(p => p[1])), Math.max(...pts.map(p => p[2]))] } : null;
      };
      const deepBounds = object => {
        const all=[];object?.traverse(q=>{if(q.isMesh)all.push(...localPoints(q));});
        return all.length ? { min:[Math.min(...all.map(p=>p[0])),Math.min(...all.map(p=>p[1])),Math.min(...all.map(p=>p[2]))],max:[Math.max(...all.map(p=>p[0])),Math.max(...all.map(p=>p[1])),Math.max(...all.map(p=>p[2]))] } : null;
      };
      const flightDeck = root.getObjectByName('WIP10_FLAT_FLIGHT_DECK');
      const deckPoints = localPoints(flightDeck), deckY = [...new Set(deckPoints.map(p => Number(p[1].toFixed(6))))];
      const doors = [-1, 1].map(side => bounds(root.getObjectByName(`HANGAR_DOOR_${side}`)));
      const mk45 = root.getObjectByName('MK45_MOD4_5IN_62');
      const contract=v.contractAudit();
      return {
        contract: {pass:contract.pass,shipProfileBound:contract.shipProfileBound,aftGeometryPass:contract.aftGeometry?.pass,mk45Mod4:contract.mk45Mod4,threeVersion:contract.threeVersion}, aftAudit: window.__NAVAL_SIM_DIAG__.aftGeometryAuditV48Wip11(),
        liferafts: window.__NAVAL_SIM_DIAG__.aftLiferaft3DAuditV48Wip11(),
        materialProtection: window.__NAVAL_SIM_DIAG__.materialProtectionAuditV48Wip11(),
        selftestFailures: window.__CORE_SELFTEST_FAILURES__.slice(),
        flatDeck: { present: !!flightDeck, uniqueRenderedYM: deckY, bounds: bounds(flightDeck), userData: { ...flightDeck?.userData } },
        hangar: { bounds: deepBounds(root.getObjectByName('FLIGHT_IIA_TWIN_HANGAR')), doors },
        supports: { seaRam: bounds(root.getObjectByName('SEARAM_RAISED_SUPPORT')), base: bounds(root.getObjectByName('AFT_SUPPORT_HOUSE')), high: bounds(root.getObjectByName('AFT_HIGH_SPG_PEDESTAL')), low: bounds(root.getObjectByName('AFT_LOW_SPG_PEDESTAL')) },
        mk45: { present: !!mk45, bounds: deepBounds(mk45), barrel: bounds(root.getObjectByName('MK45_MOD4_62CAL_BARREL')), namedParts: ['MK45_MOD4_FIXED_BASE','MK45_MOD4_ROTATION_RING','MK45_MOD4_FACETED_HOUSING','MK45_MOD4_GUN_SLEEVE','MK45_MOD4_62CAL_BARREL','MK45_MOD4_MUZZLE_COLLAR','MK45_MOD4_BORE'].map(name => !!root.getObjectByName(name)) },
      };
    });

    const drawings = await page.evaluate(() => {
      const v = window.__WIP148_3D_VIEW__, T = window.THREE, root = v.shipRoot;
      root.updateMatrixWorld(true);
      const rootInverse = new T.Matrix4().copy(root.matrixWorld).invert(), p = new T.Vector3();
      const hull = points => {
        const unique = new Map();
        for (const q of points) unique.set(`${q[0].toFixed(4)},${q[1].toFixed(4)}`, q);
        const a = [...unique.values()].sort((u, w) => u[0] - w[0] || u[1] - w[1]);
        if (a.length < 3) return [];
        const cross = (o, u, w) => (u[0]-o[0])*(w[1]-o[1])-(u[1]-o[1])*(w[0]-o[0]);
        const lo = []; for (const q of a) { while (lo.length >= 2 && cross(lo.at(-2), lo.at(-1), q) <= 0) lo.pop(); lo.push(q); }
        const hi = []; for (let i = a.length - 1; i >= 0; i--) { const q = a[i]; while (hi.length >= 2 && cross(hi.at(-2), hi.at(-1), q) <= 0) hi.pop(); hi.push(q); }
        lo.pop(); hi.pop(); return lo.concat(hi);
      };
      const area = q => Math.abs(q.reduce((sum, a, i) => { const b = q[(i+1)%q.length]; return sum + a[0]*b[1]-b[0]*a[1]; }, 0))*.5;
      const rows = { top: [], side: [] };
      let meshCount = 0;
      root.traverse(object => {
        if (!object.isMesh || object.isInstancedMesh || !object.geometry?.getAttribute?.('position')) return;
        for (let q = object; q; q = q.parent) if (!q.visible) return;
        if (/INTERIOR|CREW|DAMAGE|FLOOD|FIRE|SMOKE|TRACER|MISSILE/i.test(object.name || '')) return;
        const attr = object.geometry.getAttribute('position'), matrix = new T.Matrix4().multiplyMatrices(rootInverse, object.matrixWorld), pts = [];
        for (let i = 0; i < attr.count; i++) pts.push(p.fromBufferAttribute(attr, i).applyMatrix4(matrix).toArray());
        if (pts.length < 3) return;
        const material = Array.isArray(object.material) ? object.material.find(m => m?.color) : object.material;
        if (!material?.color || material.visible === false || Number(material.opacity) < .16) return;
        const color = `#${material.color.getHexString()}`, avgY = pts.reduce((n,q)=>n+q[1],0)/pts.length, avgZ = pts.reduce((n,q)=>n+q[2],0)/pts.length;
        for (const [view, projected, depth] of [['top', pts.map(q=>[q[0],q[2]]), avgY], ['side', pts.map(q=>[q[0],q[1]]), avgZ]]) {
          const polygon = hull(projected), polygonArea = polygon.length >= 3 ? area(polygon) : 0;
          if (polygonArea < .002) continue;
          const flat = polygon.flatMap(q => q.map(n => Number(n.toFixed(3))));
          rows[view].push({ depth, name: object.name || '', row: [color, flat, polygonArea > 5] });
        }
        meshCount++;
      });
      rows.top.sort((a,b) => a.depth-b.depth || a.name.localeCompare(b.name));
      rows.side.sort((a,b) => a.depth-b.depth || a.name.localeCompare(b.name));
      return { schema:'AEGIS_SHIP_DRAWINGS_V48_WIP11', revision:'V48_WIP11_MATERIAL_PROTECTION', source:'LIVE_THREE_SHIP_ROOT_CONVEX_PROJECTION', meshCount, top:rows.top.map(q=>q.row), side:rows.side.map(q=>q.row) };
    });

    const presets = [
      ['aft-quarter', 125, 22, 165, 10], ['starboard', 90, 8, 175, 11], ['top', 90, 78, 175, 7], ['stern', 180, 10, 150, 9], ['bow-gun', 18, 18, 125, 10],
    ];
    for (const [name, yaw, pitch, distance, targetY] of presets) {
      await page.evaluate(([yaw, pitch, distance, targetY]) => { const v=window.__WIP148_3D_VIEW__;v.follow.enabled=false;v.orbit.yaw=yaw*Math.PI/180;v.orbit.pitch=pitch*Math.PI/180;v.orbit.distance=distance;v.orbit.targetY=targetY; }, [yaw, pitch, distance, targetY]);
      await page.waitForTimeout(350);
      await page.locator('#external3DView').screenshot({ path: path.join(outDir, `${name}.png`) });
    }
    await page.evaluate(() => {
      window.__WIP148_3D_VIEW__.close();
      const panel=document.getElementById('shipDetailPanel');
      panel.style.setProperty('display','none','important');document.getElementById('shipDetailBtn').click();
      panel.style.setProperty('display','block','important');panel.style.setProperty('visibility','visible','important');
      panel.style.setProperty('position','fixed','important');panel.style.setProperty('inset','0 auto auto 0','important');
      for(const q of panel.querySelectorAll('*'))q.style.setProperty('visibility','visible','important');
    });
    await page.waitForTimeout(250);
    await page.locator('#shipDetailPanel').screenshot({ path:path.join(outDir,'hit-indicator.png') });
    fs.writeFileSync(path.join(outDir, 'visual-audit.json'), `${JSON.stringify({ simulator, inspection, consoleErrors, pageErrors }, null, 2)}\n`);
    fs.writeFileSync(path.join(outDir, 'ship-drawings.json'), `${JSON.stringify(drawings)}\n`);
    const ok = inspection.contract.pass && inspection.aftAudit.pass && inspection.liferafts.pass && inspection.materialProtection.pass && inspection.selftestFailures.length === 0 && inspection.flatDeck.uniqueRenderedYM.length === 1 && inspection.mk45.namedParts.every(Boolean) && pageErrors.length === 0;
    console.log(JSON.stringify({ result: ok ? 'PASS' : 'FAIL', screenshots: [...presets.map(q=>`${q[0]}.png`),'hit-indicator.png'], inspection, drawings: { meshCount:drawings.meshCount, top:drawings.top.length, side:drawings.side.length }, consoleErrors, pageErrors }, null, 2));
    if (!ok) process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    server.kill('SIGTERM');
    fs.writeFileSync(path.join(outDir, 'http-server.log'), serverLog);
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
