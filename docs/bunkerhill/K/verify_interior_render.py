"""Native CG upper-deck geometry, functional isolation and clean visual evidence."""
from pathlib import Path
import argparse,base64,gzip,hashlib,json,os,re,shutil
from playwright.sync_api import sync_playwright

p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('out');p.add_argument('--main-override');a=p.parse_args()
src,out=Path(a.html),Path(a.out);out.mkdir(parents=True,exist_ok=True);served=src.read_bytes()
if a.main_override:
    h=served.decode();raw=Path(a.main_override).read_bytes();packed=gzip.compress(raw,9,mtime=0)
    m=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',h,re.S);h=h[:m.start(1)]+base64.b64encode(packed).decode()+h[m.end(1):]
    m=re.search(r'const records=(\[.*?\]);',h,re.S);r=json.loads(m[1]);r[13].update(rawBytes=len(raw),gzipBytes=len(packed),sha256=hashlib.sha256(raw).hexdigest());h=h[:m.start(1)]+json.dumps(r,separators=(',',':'))+h[m.end(1):];served=h.encode()
errors=[];checks={};details={}
with sync_playwright()as pw:
    b=pw.chromium.launch(executable_path=os.environ.get('AEGIS_CHROMIUM_EXECUTABLE')or shutil.which('chromium')or None,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
    page=b.new_page(viewport={'width':960,'height':640});page.on('pageerror',lambda e:errors.append(str(e)));page.add_init_script('window.__NAVAL_SIM_SEED__=0x6d2b79f5')
    page.route('https://aegis.test/**',lambda r:r.fulfill(body=served,content_type='text/html'));page.goto('https://aegis.test/candidate?view3d=1',wait_until='load',timeout=90000)
    page.wait_for_selector('#aegisShipConfirmBtn',timeout=90000);page.locator('#aegisShipSelect').select_option('CG_52_LATE_TICONDEROGA');page.locator('#aegisShipConfirmBtn').click()
    page.wait_for_function('window.C55Packaging?.ready&&window.__WIP148_3D_VIEW__?.ready',timeout=120000)
    print(json.dumps({'stage':'ready','source':src.name}),flush=True)
    page.locator('#wip125DepartBtn').click()
    page.evaluate("()=>{const d=window.__NAVAL_SIM_DIAG__,v=window.__WIP148_3D_VIEW__;d.ciwsB1Closure.setPaused(true);v.c12ApplyPreset('LOW');}")
    # Detached crew fixture traverses the upper pilothouse and its stretcher
    # stairs; it also checks damage, medical routing and single event delivery.
    crew=page.evaluate('window.__NAVAL_SIM_DIAG__.runV48Wip07CrewDamageProbe({readCount:1000})');details['crewProbe']=crew
    checks['upperCrewRoutesAndMedical']=all(crew['checks'].values())
    # Read canonical methods, then exercise derived per-space hazards. The
    # damage/flood/crew authorities and combat RNG must remain untouched.
    isolation=page.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,rt=window.__AEGIS_ACTIVE_SHIP_RUNTIME__,top=rt.interior,
      before=JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B()),snap=top.snapshot(),ids=['cg52.bridge.pilothouse',snap.spaces.find(s=>s.deck==='H1'&&s.kind!=='PASSAGE').id],rows=[];
      for(const id of ids){top.step({spaceHazards:{[id]:{fire01:.8,smoke01:.9,temperatureC:250}}});const state=top.snapshot(),closed=state.portalStates.filter(p=>!p.open&&state.portals.some(q=>q.id===p.id&&(q.a===id||q.b===id)));
        rows.push({spaceId:id,hazard:state.hazards.find(h=>h.spaceId===id),closed,automaticActions:state.automaticActions});}
      top.step({});const recovered=top.snapshot();return {rows,recovered:recovered.portalStates.every(p=>p.open),authorityUnchanged:before===JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B())};}''');details['upperIsolation']=isolation
    checks['upperFireSmokeDerived']=all(q['hazard']['fire01']==.8 and q['hazard']['smoke01']==.9 for q in isolation['rows'])
    checks['upperAutomaticDoorsClose']=all(q['closed'] for q in isolation['rows'])
    checks['hazardRecoveryAuthorityUnchanged']=isolation['recovered']and isolation['authorityUnchanged']
    page.locator('#c14ControlsToggle').click()
    panel=page.evaluate("()=>{const target=document.getElementById('external3DInteriorBtn');for(const b of document.querySelectorAll('.c15-category')){if(document.getElementById(b.getAttribute('aria-controls'))?.contains(target))return b.getAttribute('aria-controls');}}")
    page.locator('.c15-category[aria-controls="'+panel+'"]').click();page.locator('#external3DInteriorBtn').click();page.locator('#c14ControlsToggle').click()
    page.wait_for_timeout(2000)
    audit=page.evaluate('window.__WIP148_3D_VIEW__.interiorAuditV48Wip06()');details['renderAudit']=audit
    checks['everySpacePortalEquipmentRendered']=all(audit[k]for k in ['allSpacesRepresented','allPortalsRepresented','allEquipmentRepresented'])
    checks['allHullAndUpperVerticesContained']=audit['allInteriorContained']and audit['outsideInteriorVertices']==0
    checks['allUpperDecksRendered']=audit['verticalShellFilled']and audit['representedBridgeDecks']==5 and audit['representedHangarDecks']==3
    checks['hangarsRemainClear']=audit['hangarClearance']['bays']==2 and audit['hangarClearance']['clear']and audit['hangarClearance']['clearHeightM']==5.2
    print(json.dumps({'stage':'interior-audit','checks':checks,'outsideVertices':audit['outsideInteriorVertices']}),flush=True)
    cdp=page.context.new_cdp_session(page)
    for name,x,z,distance in [('fore-bridge-interior',24,16,49),('aft-deckhouse-interior',-23,12,46)]:
        page.evaluate('''({x,z,distance})=>{const v=window.__WIP148_3D_VIEW__;v._c5Focus={local:new v.THREE.Vector3(x,z,0)};v.follow.enabled=false;v.orbit.distance=distance;v.orbit.yaw=1.2;v.orbit.pitch=.32;}''',{'x':x,'z':z,'distance':distance});page.wait_for_timeout(3000)
        (out/(name+'.png')).write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']))
    checks['coreZero']=page.evaluate('window.__CORE_SELFTEST_FAILURES__')==[];b.close()
checks['pageErrorsZero']=not errors
result={'source':src.name,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'servedSha256':hashlib.sha256(served).hexdigest(),'diagnosticOnlyMemoryOverride':bool(a.main_override),'queueMode':'NATIVE_RAF_ONLY','checks':checks,'details':details,'errors':errors,'pass':all(checks.values())}
(out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'errors':errors,'pass':result['pass']},ensure_ascii=False))
if not result['pass']:raise SystemExit(1)
