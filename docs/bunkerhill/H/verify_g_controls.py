"""Native loadout controls, functional upper rooms and detached save migration."""
from pathlib import Path
import argparse,base64,gzip,hashlib,json,os,re,shutil
from playwright.sync_api import sync_playwright

p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('baseline_f');p.add_argument('out');p.add_argument('--main-override');a=p.parse_args()
src,baseline,out=Path(a.html),Path(a.baseline_f),Path(a.out);out.mkdir(parents=True,exist_ok=True)
served=src.read_bytes()
if a.main_override:
    html=served.decode();raw=Path(a.main_override).read_bytes();packed=gzip.compress(raw,9,mtime=0)
    m=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(packed).decode()+html[m.end(1):]
    m=re.search(r'const records=(\[.*?\]);',html,re.S);rows=json.loads(m[1]);rows[13].update(rawBytes=len(raw),gzipBytes=len(packed),sha256=hashlib.sha256(raw).hexdigest());html=html[:m.start(1)]+json.dumps(rows,separators=(',',':'))+html[m.end(1):];served=html.encode()
errors=[];checks={};details={}
with sync_playwright()as pw:
    browser=pw.chromium.launch(executable_path=os.environ.get('AEGIS_CHROMIUM_EXECUTABLE')or shutil.which('chromium')or None,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    def load(body,ship='CG_52_LATE_TICONDEROGA'):
        page=browser.new_page(viewport={'width':960,'height':740});page.on('pageerror',lambda e:errors.append(str(e)));page.add_init_script('window.__NAVAL_SIM_SEED__=0x6d2b79f5')
        page.route('https://aegis.test/**',lambda r:r.fulfill(body=body,content_type='text/html'));page.goto('https://aegis.test/candidate?view3d=0',wait_until='load',timeout=90000)
        page.wait_for_selector('#aegisShipConfirmBtn',timeout=90000);page.locator('#aegisShipSelect').select_option(ship);page.locator('#aegisShipConfirmBtn').click()
        page.wait_for_function('window.C55Packaging?.ready&&window.__WIP125_DIAG__',timeout=120000);page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)');return page
    old=load(baseline.read_bytes());legacy=old.evaluate('window.__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A()');(out/'legacy-F-operational.json').write_text(json.dumps(legacy,indent=2)+'\n')
    normalized_inventory=old.evaluate('''legacy=>{const d=window.__NAVAL_SIM_DIAG__;d.importOperationalStateV48Wip11B(legacy);return d.exportOperationalStateV48Wip11A().ship.inventory;}''',legacy)
    # Native F already normalizes the Mk36 last-fire sentinel on import. Compare
    # G to that existing roundtrip, while still importing the untouched F save.
    old_symptom=old.evaluate('''()=>{const w=window.__WIP125_DIAG__,q=w.snapshot().loadout,section='fwd',occupied=new Set(q[section].map(c=>c.row+':'+c.col));let gap;
      for(let r=0;r<7;r++)for(let c=0;c<8;c++)if(!occupied.has(r+':'+c)&&occupied.has((r+1)+':'+c))gap={row:r,col:c};
      const index=q[section].findIndex(c=>c.row===gap.row+1&&c.col===gap.col),before=q[section][index];w.setCell(section,index,'SM6');const after=w.snapshot().loadout[section][index];
      w.forcePreSail();w.applyPreset('STANDARD');return {gap,index,before,after,cellMoved:before.row!==after.row||before.col!==after.col,presetCapacity:w.snapshot().loadout.aft.length};}''');details['baselineSymptoms']=old_symptom;checks['baselineReproduced']=old_symptom['cellMoved']and old_symptom['presetCapacity']==64;old.close()
    page=load(served)
    checks['coreZero']=page.evaluate('window.__CORE_SELFTEST_FAILURES__')==[]
    slots=page.evaluate('window.__NAVAL_SIM_DIAG__.vlsInstallationSlotAudit()');details['slots']=slots;checks['initialSparseInstallation']=slots['pass']and all(q['capacity']==61 and q['missingSlots']==3 for q in slots['sections'].values())
    # Real pointer click below a three-slot installation gap must leave every
    # button at the same CSS grid/pixel coordinate, including the edited one.
    sec='fwd';index=old_symptom['index'];target=page.locator(f'.wip125-cell[data-section={sec}][data-index="{index}"]')
    before_box=target.bounding_box();page.locator('[data-paint=EMPTY]').click();target.click();empty_box=target.bounding_box();page.locator('[data-paint=SM6]').click();target.click();after_box=target.bounding_box()
    checks['actualClickFixedPosition']=before_box==empty_box==after_box;details['clickedBelowGap']={'section':sec,'index':index,'before':before_box,'empty':empty_box,'filled':after_box}
    checks['uninstalledGapVisible']=page.locator('.wip125-slot-gap').count()==6 and page.locator('.wip125-cell').count()==122
    # Native drag over a gap cannot paint a phantom cell.
    page.locator('[data-paint=ESSM4]').click();target_box=target.bounding_box();gap_box=page.locator('.wip125-slot-gap').first.bounding_box();before_gap=page.evaluate('window.__WIP125_DIAG__.snapshot().loadout')
    page.mouse.move(target_box['x']+13,target_box['y']+13);page.mouse.down();after_down=page.evaluate('window.__WIP125_DIAG__.snapshot().loadout');page.mouse.move(gap_box['x']+13,gap_box['y']+13);after_gap=page.evaluate('window.__WIP125_DIAG__.snapshot().loadout');page.mouse.up()
    checks['dragAcrossUninstalledGapInert']=after_down==after_gap and all(len(q)==61 for q in after_gap.values())
    edited=page.evaluate('''()=>{const w=window.__WIP125_DIAG__,d=window.__NAVAL_SIM_DIAG__,initial=d.vlsInstallationSlotAudit(),rows=[];
      for(const section of ['fwd','aft'])for(let i=0;i<61;i++){const box=w.cellBox(section,i);for(const type of ['EMPTY','SM2','SM2ER','SM6','ESSM4']){
        if(!w.setCell(section,i,type)||JSON.stringify(box)!==JSON.stringify(w.cellBox(section,i)))rows.push({section,i,type});}}
      return {failed:rows,slots:d.vlsInstallationSlotAudit(),preflight:d.validateOperationalStateV48Wip11B(d.exportOperationalStateV48Wip11A())};}''')
    details['allCellsAllTypes']=edited;checks['all122CellsAllFiveTypesFixed']=edited['failed']==[]and edited['slots']['pass']and edited['preflight']['ok']
    presets=page.evaluate('''()=>{const w=window.__WIP125_DIAG__,d=window.__NAVAL_SIM_DIAG__,rows=[];
      for(const name of ['STANDARD','LONG','CLOSE','DISTRIBUTED','ER_TEST','SM6_TEST']){const applied=w.applyPreset(name);rows.push({name,applied,counts:w.snapshot().counts,slots:d.vlsInstallationSlotAudit(),valid:d.validateOperationalStateV48Wip11B(d.exportOperationalStateV48Wip11A()).ok});}
      const before=JSON.stringify(w.snapshot().loadout),unknown=w.applyPreset('UNKNOWN');return {rows,unknownRejected:unknown===false&&before===JSON.stringify(w.snapshot().loadout)};}''')
    details['presets']=presets;checks['sixPresetsRespect61Cells']=all(q['applied']and q['slots']['pass']and q['valid']for q in presets['rows']);checks['unknownPresetNoMutation']=presets['unknownRejected']
    page.screenshot(path=str(out/'fixed-loadout.png'))
    native=page.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,w=window.__WIP125_DIAG__,before=w.snapshot().loadout;w.confirmDeparture();
      const blocked=w.setCell('fwd',10,'EMPTY')===false&&w.applyPreset('STANDARD')===false;d.resetEntireSessionV48Wip11A();d.ciwsB1Closure.setPaused(true);
      return {blocked,restored:JSON.stringify(before)===JSON.stringify(w.snapshot().loadout),slots:d.vlsInstallationSlotAudit(),valid:d.validateOperationalStateV48Wip11B(d.exportOperationalStateV48Wip11A()).ok};}''')
    details['departureRestart']=native;checks['departureLockAndCommittedRestart']=native['blocked']and native['restored']and native['slots']['pass']and native['valid']
    interior=page.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,rt=window.__AEGIS_ACTIVE_SHIP_RUNTIME__,top=rt.interior.topology??rt.interior.runtime??rt.interior,
      snap=d.v48Wip06InteriorState(),crew=d.v48Wip07CrewState(),audit=d.bunkerInteriorDetailAudit();return {audit,summary:snap.summary,spaces:snap.spaces,portals:snap.portals,crewTotal:crew.total,
      crewLocations:crew.groups.map(q=>({id:q.id,spaceId:q.spaceId,position:q.position,homeSpaceId:q.homeSpaceId})),pilot:snap.spaces.find(q=>q.id==='cg52.bridge.pilothouse')};}''')
    details['interior']=interior;checks['functionalRoomsConnectedDisjoint']=interior['audit']['disjointSpaces']and interior['audit']['unreachable']==[]and interior['audit']['centersInside']and interior['audit']['legacyIdsRetained'];checks['upperStructuresFilled']=interior['audit']['deckCount']==12 and sum(q['deck']in ['H0','S1','S2','S3','S4','B1','H1','H2']for q in interior['spaces'])>=70;checks['pilotMatchesUpperWindows']=interior['pilot']['z0']<=20.4 and interior['pilot']['z1']>=21.4
    by_id={q['id']:q for q in interior['spaces']};checks['all330CrewInsideAssignedRoom']=interior['crewTotal']==330 and all(all(by_id[q['spaceId']][k+'0']<=q['position'][k]<=by_id[q['spaceId']][k+'1']for k in 'xyz')for q in interior['crewLocations']);checks['hazardsBoundToDamageCells']=all(q['parentFloodCellId']for q in interior['spaces'])
    migration=page.evaluate('''({legacy,normalizedInventory})=>{const d=window.__NAVAL_SIM_DIAG__,original=JSON.stringify(legacy),before=d.operationalImportMutationFingerprintV48Wip11B();
      const valid=d.validateOperationalStateV48Wip11B(legacy),preflightReadOnly=JSON.stringify(before)===JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());
      const imported=d.importOperationalStateV48Wip11B(legacy),out=d.exportOperationalStateV48Wip11A();
      return {valid,inputDetached:original===JSON.stringify(legacy),preflightReadOnly,revision:out.profileRevision,
        inventoryPreserved:JSON.stringify(out.ship.inventory)===JSON.stringify(normalizedInventory),
        crewTotalsPreserved:['total','fit','injured','dead','evacuated'].every(k=>out.ship.crew[k]===legacy.ship.crew[k]),out};}''',{'legacy':legacy,'normalizedInventory':normalized_inventory})
    details['legacyMigration']=migration;checks['legacyFDetachedMigration']=bool(migration['valid']['ok']and migration['valid'].get('migrations')and migration['inputDetached']and migration['preflightReadOnly']and migration['revision']=='BUNKERHILL_LATE_G_1'and migration['inventoryPreserved']and migration['crewTotalsPreserved'])
    checks['legacyPersonnelLocated']=all(all(by_id[q['spaceId']][k+'0']<=q['position'][k]<=by_id[q['spaceId']][k+'1']for k in 'xyz')for q in migration['out']['ship']['crew']['groups'])
    rejected=page.evaluate('''legacy=>{const d=window.__NAVAL_SIM_DIAG__,rows=[];for(const [name,edit]of [['unknownRevision',q=>q.profileRevision+='UNKNOWN'],['unknownRoom',q=>q.ship.crew.groups[0].spaceId='UNKNOWN'],['invalidSparseCell',q=>q.ship.inventory.vls.fwd[40].row=99]]){
      const q=structuredClone(legacy);edit(q);const before=JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());let rejected=false;try{d.importOperationalStateV48Wip11B(q);}catch(_){rejected=true;}
      rows.push({name,rejected,unchanged:before===JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B())});}return rows;}''',legacy)
    details['rejections']=rejected;checks['badMigrationInputsZeroMutation']=all(q['rejected']and q['unchanged']for q in rejected)
    page.close()
    # Capacity-aware presets leave every DDG placement and count byte-identical.
    old=load(baseline.read_bytes(),'DDG_119_LATE_FLIGHT_IIA');new=load(served,'DDG_119_LATE_FLIGHT_IIA')
    compare='''()=>{const w=window.__WIP125_DIAG__,rows=[];for(const name of ['STANDARD','LONG','CLOSE','DISTRIBUTED','ER_TEST','SM6_TEST']){w.applyPreset(name);rows.push({name,loadout:w.snapshot().loadout,counts:w.snapshot().counts});}return rows;}'''
    checks['ddgSixPresetsExact']=old.evaluate(compare)==new.evaluate(compare);checks['ddgCoreZero']=new.evaluate('window.__CORE_SELFTEST_FAILURES__')==[]
    old.close();new.close();browser.close()
checks['pageErrorsZero']=errors==[];result={'source':src.name,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'baselineF':baseline.name,'baselineFSha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'diagnosticOnlyMemoryOverride':bool(a.main_override),'checks':checks,'details':details,'errors':errors,'pass':all(checks.values())}
(out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'errors':errors,'pass':result['pass']},ensure_ascii=False))
if not result['pass']:raise SystemExit(1)
